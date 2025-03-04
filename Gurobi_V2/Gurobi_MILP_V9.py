import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Parameters
load_demand = 10000  # Total hourly load demand (kW)
PowerTurbine = [3000, 6000, 9000]  # Wind turbine capacities (kW)
PowerPV = [200, 400, 600]  # Solar PV capacities (kW)

# Cost per kWh for DER components
costTurbine = [100, 120, 140]  # Wind turbines
costPV = [150, 180, 210]  # Solar PV
costgrid = 0.01  # Grid energy cost per kWh

# Lifespan in hours (24 hours * 365 days * 10 years)
lifespan_hours = 24 * 365 * 10

# Objective Weights
weight_cost = 0.5
weight_renewable = 0.5

# DER Maximums
turbine_max = 4
PV_max = 20

# Load Solar Power Data
solar_df = pd.read_csv(r"C:\Users\crane30\DER-Code\DER-Optimization-Project\Environmental Data V4\solar_data_saved.csv", skiprows=28, usecols=[0, 1, 2, 3], names=["Month", "Day", "Hour", "Solar_Power"], header=0)
solar_df["Original_Solar_Power"] = solar_df["Solar_Power"] / 1000  # Convert to kW
solar_df["Solar_Power"] = (solar_df["Solar_Power"] / 1000) * (PowerPV[0] / 10)  # Adjust for 10 kW panel size

# Load Wind Power Data
wind_df = pd.read_csv(r"C:\Users\crane30\DER-Code\DER-Optimization-Project\Environmental Data V4\wind_power_output_main_GUI.csv", usecols=[0, 1, 2, 3, 6], names=["Year", "Month", "Day", "Hour", "Wind_Power"], header=0)
wind_df["Original_Wind_Power"] = wind_df["Wind_Power"] / 1500  # Convert to kW
wind_df["Wind_Power"] = (wind_df["Wind_Power"] / 1500) * PowerTurbine[0]  # Adjust for 1500 kW turbine size


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

# Merge data
power_data = pd.merge(solar_df, wind_df, on=["Month", "Day", "Hour"], how="inner")

# Initialize model
model = gp.Model("DER_Optimization")

# Decision variables
selected_turbine = model.addVars(len(PowerTurbine), vtype=GRB.BINARY, name="SelectedTurbine")
selected_pv = model.addVars(len(PowerPV), vtype=GRB.BINARY, name="SelectedPV")
grid_energy = model.addVars(len(power_data), vtype=GRB.CONTINUOUS, name="GridEnergy")

# Constraints
for i, row in power_data.iterrows():
    model.addConstr(
        gp.quicksum(selected_turbine[j] * PowerTurbine[j] for j in range(len(PowerTurbine))) +
        gp.quicksum(selected_pv[j] * PowerPV[j] for j in range(len(PowerPV))) +
        grid_energy[i] == load_demand,
        name=f"LoadBalance_{i}"
    )

# Max installations constraints
model.addConstr(gp.quicksum(selected_turbine[j] for j in range(len(PowerTurbine))) <= turbine_max, "MaxTurbines")
model.addConstr(gp.quicksum(selected_pv[j] for j in range(len(PowerPV))) <= PV_max, "MaxPV")

# Objective function
installation_cost = gp.quicksum(selected_turbine[j] * costTurbine[j] * PowerTurbine[j] for j in range(len(PowerTurbine))) + \
                    gp.quicksum(selected_pv[j] * costPV[j] * PowerPV[j] for j in range(len(PowerPV)))

grid_cost = gp.quicksum(grid_energy[i] * costgrid for i in range(len(power_data)))

total_renewable_power = gp.quicksum(
    selected_turbine[j] * PowerTurbine[j] + selected_pv[j] * PowerPV[j] for j in range(len(PowerTurbine))
)

renewable_fraction = total_renewable_power / (load_demand * len(power_data)) if load_demand > 0 else 0

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
        row["Original_Solar_Power"], row["Original_Wind_Power"],
        sum(selected_turbine[j].x * PowerTurbine[j] for j in range(len(PowerTurbine))),
        sum(selected_pv[j].x * PowerPV[j] for j in range(len(PowerPV))),
        grid_usage
    ])

# Convert results to DataFrame
output_df = pd.DataFrame(results, columns=["Month", "Day", "Hour", "Original_Solar_Power", "Original_Wind_Power", "Optimized_Wind_Power", "Optimized_Solar_Power", "Grid_Consumption"])

# Save to Excel
output_df.to_excel("DER_Optimization_Results_Final_Version.xlsx", index=False)
