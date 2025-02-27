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
load_demand = 15000  # Total hourly load demand (kW)
PowerTurbine = [5000, 10000, 15000]  # Wind turbine capacities (kW)
PowerPV = [300, 600, 900]  # Solar PV capacities (kW)

# Turbine cost $120/kWh, PV cost $150/kWh
costTurbine = [120, 230, 390]  # Cost per kWh for wind turbines
costPV = [150, 190, 230]  # Cost per kWh for solar PV
costgrid = 0.1  # Cost per kWh from the grid

# Define maximum quantities
max_turbines = 8  # Maximum number of turbines
max_pv = 8  # Maximum number of PV systems

# Define weights for objectives
weight_cost = 0.1  # Weight for cost minimization
weight_renewable = 0.9  # Weight for renewable energy maximization

# Initialize results list
results = []

# Create the model
model = gp.Model("DER_Optimization")

# Decision Variables
turbine = model.addVars(3, vtype=GRB.INTEGER, lb=0, ub=max_turbines, name="Turbine")
PV = model.addVars(3, vtype=GRB.INTEGER, lb=0, ub=max_pv, name="PV")
grid_energy = model.addVars(len(power_data), vtype=GRB.CONTINUOUS, lb=0, name="GridEnergy")
total_installation_cost = model.addVar(vtype=GRB.CONTINUOUS, name="TotalInstallationCost")

# Iterate over each hour and compute contributions
total_wind_power = sum(PowerTurbine[i] * turbine[i] for i in range(3))
total_solar_power = sum(PowerPV[i] * PV[i] for i in range(3))

# Total annual costs and energy contributions
model.addConstr(total_installation_cost == sum(costTurbine[i] * turbine[i] * 8760 for i in range(3)) +
                                   sum(costPV[i] * PV[i] * 8760 for i in range(3)), "InstallationCost")

# Objective Function: Minimize total installation cost and maximize renewable energy
model.setObjective(weight_cost * total_installation_cost - weight_renewable * (total_wind_power + total_solar_power), GRB.MINIMIZE)

# Constraints
for hour in range(len(power_data)):
    load = load_demand
    model.addConstr(grid_energy[hour] >= load - (total_wind_power + total_solar_power), "DemandConstraint_{}".format(hour))

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

    # Calculate total energy generated
    total_wind_power_generated = sum(PowerTurbine[i] * turbine[i].X for i in range(3))
    total_solar_power_generated = sum(PowerPV[i] * PV[i].X for i in range(3))

    # Print summary
    print("Optimization complete. Results saved to 'optimized_results.csv'.")
    print(f"Total installation cost: ${total_installation_cost.X:.2f}")
    print(f"Total wind power generated: {total_wind_power_generated:.2f} kWh")
    print(f"Total solar power generated: {total_solar_power_generated:.2f} kWh")
    print(f"Total grid energy used: {sum(row[5] for row in results):.2f} kWh")
    for i in range(3):
        print(f"Number of wind turbines of capacity {PowerTurbine[i]} kW: {turbine[i].X}")
        print(f"Number of solar PV systems of capacity {PowerPV[i]} kW: {PV[i].X}")
else:
    print("No optimal solution found.")
