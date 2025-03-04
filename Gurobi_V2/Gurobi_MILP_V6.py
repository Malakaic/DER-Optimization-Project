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

# Weights for objectives
weight_cost = 0.25  # Weight for cost minimization
weight_renewable = 0.75  # Weight for renewable energy maximization

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

# Iterate over each hour and compute contributions
for hour in range(len(power_data)):
    available_solar_power = solar_df.iloc[hour]['Solar_Power']
    available_wind_power = wind_df.iloc[hour]['Wind_Power']
    
    # Ensure power does not exceed available generation
    total_wind_power = sum(min(PowerTurbine[i], available_wind_power) * turbine[i] for i in range(3))
    total_solar_power = sum(min(PowerPV[i], available_solar_power) * PV[i] for i in range(3))

    # Total available renewable power for this hour
    renewable_power = total_wind_power + total_solar_power

    # Debugging output
    print(f"Hour {hour}: Load Demand = {load_demand}, Available Solar Power = {available_solar_power}, Available Wind Power = {available_wind_power}, Renewable Power = {renewable_power}")

    load = load_demand
    model.addConstr(grid_energy[hour] >= load - renewable_power, "DemandConstraint_{}".format(hour))
    
    # Relax renewable constraint temporarily for debugging
    #model.addConstr(renewable_power >= 0.5 * load, "RenewableFractionConstraint_{}".format(hour))

# Objective Function: Minimize total installation cost and maximize renewable energy
model.setObjective(weight_cost * total_installation_cost - weight_renewable * (total_wind_power + total_solar_power), GRB.MINIMIZE)

# Set NumericFocus for better numerical stability
model.setParam('NumericFocus', 2)

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
