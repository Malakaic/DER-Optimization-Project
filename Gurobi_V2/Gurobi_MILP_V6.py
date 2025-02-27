import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Load Solar Power Data (Skipping first 28 rows)
solar_df = pd.read_csv(r"C:\Users\crane30\DER-Code\DER-Optimization-Project\Environmental Data V4\solar_data_saved.csv", skiprows=28, usecols=[0, 1, 2, 3], names=["Month", "Day", "Hour", "Solar_Power"], header=0)

# Load Wind Power Data
wind_df = pd.read_csv(r"C:\Users\crane30\DER-Code\DER-Optimization-Project\Environmental Data V4\wind_power_output_main_GUI.csv", usecols=[0, 1, 2, 3, 6], names=["Year", "Month", "Day", "Hour", "Wind_Power"], header=0)

# Define month mapping
month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
             "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}

# Convert month names to numbers if necessary
if solar_df["Month"].dtype == object:
    solar_df["Month"] = solar_df["Month"].map(month_map)
if wind_df["Month"].dtype == object:
    wind_df["Month"] = wind_df["Month"].map(month_map)

# Ensure consistent data types
solar_df[["Month", "Day", "Hour"]] = solar_df[["Month", "Day", "Hour"]].astype(int)
wind_df[["Month", "Day", "Hour"]] = wind_df[["Month", "Day", "Hour"]].astype(int)

# Merge data on Month, Day, and Hour
power_data = pd.merge(solar_df, wind_df, on=["Month", "Day", "Hour"], how="inner")

# Parameters
load_demand = 1500  # Total hourly load demand (kW)
PowerTurbine = [3000, 6000, 9000]  # Wind turbine capacities (kW)
PowerPV = [200, 400, 600]  # Solar PV capacities (kW)

# Turbine cost $100/kWh, PV cost $150/kWh
costTurbine = [100, 120, 140]  # Cost per kWh for wind turbines
costPV = [150, 180, 210]  # Cost per kWh for solar PV
costgrid = 0.1  # Cost per kWh from the grid

# Define maximum quantities
max_turbines = 8  # Maximum number of turbines
max_pv = 8  # Maximum number of PV systems

# Lifespan in hours (24 hours * 365 days)
lifespan_hours = 24 * 365  # Total lifespan in hours

# Initialize results list
results = []

# Create the model
model = gp.Model("DER_Optimization")

# Decision Variables
turbine = model.addVars(3, vtype=GRB.INTEGER, lb=0, ub=max_turbines, name="Turbine")
PV = model.addVars(3, vtype=GRB.INTEGER, lb=0, ub=max_pv, name="PV")
grid_energy = model.addVars(len(power_data), vtype=GRB.CONTINUOUS, lb=0, name="GridEnergy")
total_installation_cost = model.addVar(vtype=GRB.CONTINUOUS, name="TotalInstallationCost")

# Total annual costs and energy contributions
model.addConstr(total_installation_cost == 
    sum((costTurbine[i] * PowerTurbine[i] * turbine[i] * lifespan_hours) for i in range(3)) +
    sum((costPV[i] * PowerPV[i] * PV[i] * lifespan_hours) for i in range(3)), "InstallationCost")

# Objective Function: Minimize total installation cost and maximize renewable energy
model.setObjective(sum(costTurbine[i] * turbine[i] for i in range(3)) + sum(costPV[i] * PV[i] for i in range(3)), GRB.MINIMIZE)

# Constraints
for hour in range(len(power_data)):
    load = load_demand
    
    # Define renewable power available from data
    available_solar_power = solar_df["Solar_Power"].iloc[hour]
    available_wind_power = wind_df["Wind_Power"].iloc[hour]

    # Total renewable power generated from turbines and PV
    total_renewable_power = sum(PowerTurbine[i] * turbine[i] for i in range(3)) + sum(PowerPV[i] * PV[i] for i in range(3))
    
    # Demand constraint ensuring load is met
    model.addConstr(grid_energy[hour] >= load - total_renewable_power, "DemandConstraint_{}".format(hour))
    
    # Adjust renewable generation based on availability
    model.addConstr(sum(PowerPV[i] * PV[i] for i in range(3)) <= available_solar_power, "SolarPowerAvailabilityConstraint_{}".format(hour))
    model.addConstr(sum(PowerTurbine[i] * turbine[i] for i in range(3)) <= available_wind_power, "WindPowerAvailabilityConstraint_{}".format(hour))

    # Constraint to ensure at least 75% of demand comes from renewables if possible
    model.addConstr(total_renewable_power >= 0.75 * load, "RenewableFractionConstraint_{}".format(hour))

# Optimize the model
model.optimize()

# Collect results
if model.status == GRB.OPTIMAL:
    for hour, row in power_data.iterrows():
        grid_value = grid_energy[hour].X
        results.append([row["Month"], row["Day"], row["Hour"],
                        sum(PowerPV[i] * PV[i].X for i in range(3)),
                        sum(PowerTurbine[i] * turbine[i].X for i in range(3)),
                        grid_value, model.objVal])

    # Print summary
    print("Optimization complete. Results saved to 'optimized_results.csv'.")
    print(f"Total installation cost: ${total_installation_cost.X:.2f}")
    for i in range(3):
        print(f"Number of wind turbines of capacity {PowerTurbine[i]} kW: {turbine[i].X}")
        print(f"Number of solar PV systems of capacity {PowerPV[i]} kW: {PV[i].X}")
else:
    print("No optimal solution found.")

# Save results to CSV
results_df = pd.DataFrame(results, columns=["Month", "Day", "Hour", "Total PV Power", "Total Wind Power", "Grid Energy Used", "Total Cost"])
results_df.to_csv("optimized_results.csv", index=False)
