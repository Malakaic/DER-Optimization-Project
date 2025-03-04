import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Load Solar Power Data (Skipping first 28 rows)
solar_df = pd.read_csv(r"C:\Users\crane30\DER-Code\DER-Optimization-Project\Environmental Data V4\solar_data_saved.csv", skiprows=28, usecols=[0, 1, 2, 3], names=["Month", "Day", "Hour", "Solar_Power"], header=0)

# Load Wind Power Data
wind_df = pd.read_csv(r"C:\Users\crane30\DER-Code\DER-Optimization-Project\Environmental Data V4\wind_power_output_main_GUI.csv", usecols=[0, 1, 2, 3, 6], names=["Year", "Month", "Day", "Hour", "Wind_Power"], header=0)

# Convert month names to numbers if necessary
month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
             "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
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
PowerTurbine = [1000, 1500, 2000]  # Wind turbine capacities (kW)
PowerPV = [200, 400, 600]  # Solar PV capacities (kW)

# Cost per kWh for DER components
costTurbine = [100, 120, 140]  # Wind turbines
costPV = [150, 180, 210]  # Solar PV
costgrid = 0.01  # Grid energy cost per kWh

# Maximum allowed installations
max_turbines = 4
max_pv = 8

# Lifespan in hours (24 hours * 365 days)
lifespan_hours = 24 * 365

# Objective Weights
weight_cost = 0.5
weight_renewable = 0.5

# Initialize model
model = gp.Model("DER_Optimization")

# Decision variables
num_turbines = model.addVars(len(PowerTurbine), vtype=GRB.INTEGER, name="Turbines")
num_pv = model.addVars(len(PowerPV), vtype=GRB.INTEGER, name="PV")
grid_energy = model.addVars(len(power_data), vtype=GRB.CONTINUOUS, name="GridEnergy")

# Constraints
for i, row in power_data.iterrows():
    model.addConstr(
        gp.quicksum(num_turbines[j] * PowerTurbine[j] for j in range(len(PowerTurbine))) +
        gp.quicksum(num_pv[j] * min(PowerPV[j], row["Solar_Power"]) for j in range(len(PowerPV))) +
        grid_energy[i] == load_demand,
        name=f"LoadBalance_{i}"
    )

model.addConstr(gp.quicksum(num_turbines[j] for j in range(len(PowerTurbine))) <= max_turbines, "MaxTurbines")
model.addConstr(gp.quicksum(num_pv[j] for j in range(len(PowerPV))) <= max_pv, "MaxPV")

# Objective function
installation_cost = (
    gp.quicksum(num_turbines[j] * costTurbine[j] * PowerTurbine[j] for j in range(len(PowerTurbine))) +
    gp.quicksum(num_pv[j] * costPV[j] * PowerPV[j] for j in range(len(PowerPV)))
) / lifespan_hours

grid_cost = gp.quicksum(grid_energy[i] * costgrid for i in range(len(power_data)))
renewable_fraction = gp.quicksum(
    num_turbines[j] * PowerTurbine[j] + num_pv[j] * PowerPV[j] for j in range(len(PowerTurbine))
) / (load_demand * len(power_data))

model.setObjective(weight_cost * (installation_cost + grid_cost) - weight_renewable * renewable_fraction, GRB.MINIMIZE)

# Solve model
model.optimize()

# Store results
results = []
total_grid_energy = 0
for i, row in power_data.iterrows():
    grid_usage = grid_energy[i].x
    total_grid_energy += grid_usage
    results.append([
        row["Month"], row["Day"], row["Hour"],
        sum(num_turbines[j].x * PowerTurbine[j] for j in range(len(PowerTurbine))),
        sum(num_pv[j].x * min(PowerPV[j], row["Solar_Power"]) for j in range(len(PowerPV))),
        grid_usage
    ])

# Convert results to DataFrame
output_df = pd.DataFrame(results, columns=["Month", "Day", "Hour", "Wind_Power", "Solar_Power", "Grid_Consumption"])

# Save to Excel
output_df.to_excel("DER_Optimization_Results.xlsx", index=False)

# Print summary
print("Optimized DER System:")
print(f"Total Wind Turbines Installed: {sum(num_turbines[j].x for j in range(len(PowerTurbine)))}")
print(f"Total Solar Panels Installed: {sum(num_pv[j].x for j in range(len(PowerPV)))}")
print(f"Total Grid Energy Used Throughout Year: {total_grid_energy:.2f} kWh")
print(f"Installation Costs for DERs: ${installation_cost.getValue():.2f}")
print(f"Total Grid Cost Throughout Year: ${grid_cost.getValue():.2f}")
