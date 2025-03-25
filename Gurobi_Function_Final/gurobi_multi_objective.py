import gurobipy as gp
from gurobipy import GRB
import pandas as pd
import config
import os

# Parameters
load_demand = 10000  # Total hourly load demand (kW)
PowerTurbine = [config.wind_data_dict[i][1] for i in config.wind_data_dict]  # Wind turbine capacities (kW)
PowerPV = [config.pv_data_dict[i][1] for i in config.pv_data_dict]  # Solar PV capacities (kW)

# Cost per kWh for DER components
costTurbine = [config.wind_data_dict[i][6] for i in config.wind_data_dict]  # Wind turbine costs
costPV = [config.pv_data_dict[i][5] for i in config.pv_data_dict]  # Solar PV costs
costgrid = 1  # Grid energy cost per kWh

# Lifespan in hours (24 hours * 365 days * 10 years)
lifespan_hours = 24 * 365 * 10

# Objective Weights
weight_cost = 0.5
weight_renewable = 0.5

# DER Maximums
turbine_max = 4
PV_max = 20

# Construct the file paths using the project name
project_folder = os.path.join(os.getcwd(), config.project_name)

# Load Solar Power Data

solar_files = [f for f in os.listdir(project_folder) if f.endswith("_solar_data_saved.csv")]
solar_dfs = []
for idx, file in enumerate(solar_files):
    file_path = os.path.join(project_folder, file)
    df = pd.read_csv(file_path, skiprows=28, usecols=[0, 1, 2, 3], names=["Month", "Day", "Hour", f"PV-{idx+1} Solar Power"], header=0)
    df[f"PV-{idx+1} Solar Power"] /= 1000
    solar_dfs.append(df)

# Merge solar data on Month, Day, Hour
solar_df = solar_dfs[0] if solar_dfs else pd.DataFrame(columns=["Month", "Day", "Hour"])
for df in solar_dfs[1:]:
    solar_df = pd.merge(solar_df, df, on=["Month", "Day", "Hour"], how="outer")

# Load Wind Power Data
wind_files = [f for f in os.listdir(project_folder) if f.endswith("_wind_data_saved.csv")]
wind_dfs = []
for idx, file in enumerate(wind_files):
    file_path = os.path.join(project_folder, file)
    df = pd.read_csv(file_path, usecols=[1, 2, 3, 7], names=["Month", "Day", "Hour", f"Turbine-{idx+1} Power"], header=0)
    wind_dfs.append(df)

# Merge wind data on Month, Day, Hour
wind_df = wind_dfs[0] if wind_dfs else pd.DataFrame(columns=["Month", "Day", "Hour"])
for df in wind_dfs[1:]:
    wind_df = pd.merge(wind_df, df, on=["Month", "Day", "Hour"], how="outer")


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
# Merge solar and wind data on Month, Day, Hour
power_data = pd.merge(solar_df, wind_df, on=["Month", "Day", "Hour"], how="outer")

# Save combined CSV
combined_csv_path = os.path.join(project_folder, "Combined_Power_Data.csv")
power_data.to_csv(combined_csv_path, index=False)

# Calculate the highest possible installation cost
max_turbine_installation_cost = sum(costTurbine[j] * PowerTurbine[j] for j in range(len(PowerTurbine))) * turbine_max
max_pv_installation_cost = sum(costPV[j] * PowerPV[j] for j in range(len(PowerPV))) * PV_max
max_installation_cost = max_turbine_installation_cost + max_pv_installation_cost

# Calculate the highest possible grid cost
max_grid_cost = load_demand * costgrid * lifespan_hours

# Calculate the highest possible total system cost
max_total_system_cost = max_installation_cost + max_grid_cost


# Initialize model
model = gp.Model("DER_Optimization")

# Decision variables
selected_turbine_type = model.addVars(len(PowerTurbine), vtype=GRB.BINARY, name="SelectedTurbineType")
selected_pv_type = model.addVars(len(PowerPV), vtype=GRB.BINARY, name="SelectedPVType")
num_turbines = model.addVar(vtype=GRB.INTEGER, name="NumTurbines")
num_pvs = model.addVar(vtype=GRB.INTEGER, name="NumPVs")
grid_energy = model.addVars(len(power_data), vtype=GRB.CONTINUOUS, name="GridEnergy")

# New variable for actual solar power used
actual_solar_power_used = model.addVars(len(power_data), vtype=GRB.CONTINUOUS, name="ActualSolarPowerUsed")

# Ensure only one type of PV and one type of wind turbine is selected
model.addConstr(gp.quicksum(selected_turbine_type[j] for j in range(len(PowerTurbine))) == 1, "OneTurbineType")
model.addConstr(gp.quicksum(selected_pv_type[j] for j in range(len(PowerPV))) == 1, "OnePVType")

# Ensure the number of selected PVs and turbines does not exceed the maximum values
model.addConstr(num_turbines <= turbine_max, "MaxTurbines")
model.addConstr(num_pvs <= PV_max, "MaxPVs")

# Constraints
for i, row in power_data.iterrows():
    # Calculate available wind power
    available_wind_power = gp.quicksum(
        selected_turbine_type[j] * num_turbines * row[f"Turbine-{j+1} Power"] for j in range(len(PowerTurbine))
    )

    # Constraint to limit actual solar power to available solar power
    model.addConstr(
        actual_solar_power_used[i] <= gp.quicksum(
            selected_pv_type[j] * num_pvs * row[f"PV-{j+1} Solar Power"] for j in range(len(PowerPV))
        ),
        name=f"LimitSolarPower_{i}"
    )

    # Load balance constraint considering available wind and actual solar power
    model.addConstr(
        available_wind_power + actual_solar_power_used[i] + grid_energy[i] == load_demand,
        name=f"LoadBalance_{i}"
    )

# Objective function
turbine_installation_cost = gp.quicksum(selected_turbine_type[j] * num_turbines * costTurbine[j] * PowerTurbine[j] for j in range(len(PowerTurbine)))
pv_installation_cost = gp.quicksum(selected_pv_type[j] * num_pvs * costPV[j] * PowerPV[j] for j in range(len(PowerPV)))
installation_cost = turbine_installation_cost + pv_installation_cost

turbine_hourly_cost = turbine_installation_cost / lifespan_hours
pv_hourly_cost = pv_installation_cost / lifespan_hours

grid_cost = gp.quicksum(grid_energy[i] * costgrid for i in range(len(power_data)))

total_renewable_power = gp.quicksum(
    selected_turbine_type[j] * num_turbines * PowerTurbine[j] + selected_pv_type[j] * num_pvs * PowerPV[j] for j in range(len(PowerTurbine))
)

renewable_fraction = total_renewable_power / (load_demand * len(power_data))

normalized_installation_cost = (installation_cost+grid_cost) / max_total_system_cost

model.setObjective(weight_cost * normalized_installation_cost - weight_renewable * renewable_fraction, GRB.MINIMIZE)

# Solve model
model.optimize()

# Store results
results = []
total_grid_energy = 0
for i, row in power_data.iterrows():
    grid_usage = grid_energy[i].x
    total_grid_energy += grid_usage
    result_row = [
        row["Month"],
        row["Day"],
        row["Hour"]
    ]
    # Add original solar power data
    for idx in range(len(solar_files)):
        result_row.append(row.get(f"PV-{idx+1} Solar Power", 0))
    # Add original wind power data
    for idx in range(len(wind_files)):
        result_row.append(row.get(f"Turbine-{idx+1} Power", 0))
    # Calculate actual power used from selected components
    actual_pv_power = sum(selected_pv_type[j].x * num_pvs.x * row.get(f"PV-{j+1} Solar Power", 0) for j in range(len(PowerPV)))
    actual_wind_power = sum(selected_turbine_type[j].x * num_turbines.x * row.get(f"Turbine-{j+1} Power", 0) for j in range(len(PowerTurbine)))
    # Add actual power used and costs
    result_row.extend([
        actual_pv_power,
        actual_wind_power,
        grid_usage,
        sum(selected_pv_type[j].x * num_pvs.x * costPV[j] * row.get(f"PV-{j+1} Solar Power", 0) for j in range(len(PowerPV))) / lifespan_hours,
        sum(selected_turbine_type[j].x * num_turbines.x * costTurbine[j] * row.get(f"Turbine-{j+1} Power", 0) for j in range(len(PowerTurbine))) / lifespan_hours,
        grid_usage * costgrid
    ])
    results.append(result_row)

# Define column names
columns = ["Month", "Day", "Hour"]
columns.extend([f"Original-PV-{idx+1} Solar Power" for idx in range(len(solar_files))])
columns.extend([f"Original-Turbine-{idx+1} Power" for idx in range(len(wind_files))])
columns.extend(["Actual-PV-Power", "Actual-Wind-Turbine-Power", "Grid-Consumption", "Optimized-PV-Hourly-Cost", "Optimized-Turbine-Hourly-Cost", "Hourly-Grid-Cost"])

# Convert results to DataFrame
output_df = pd.DataFrame(results, columns=columns)

# Save to Excel
output_df.to_excel("DER_Optimization_Results_Final_Version.xlsx", index=False)

# Print selected turbine and PV
selected_turbine_idx = [j for j in range(len(PowerTurbine)) if selected_turbine_type[j].x > 0.5]
selected_pv_idx = [j for j in range(len(PowerPV)) if selected_pv_type[j].x > 0.5]

selected_turbine_values = [config.wind_data_dict[j][0] for j in selected_turbine_idx]
selected_pv_values = [config.pv_data_dict[j][0] for j in selected_pv_idx]

print (f"Normalized Installation Cost: {normalized_installation_cost.getValue()}")
print (f"Renewable Fraction: {renewable_fraction.getValue()}")

print(f"Selected Turbine(s): {selected_turbine_values}")
print(f"Selected PV(s): {selected_pv_values}")

# Print the number of each PV and turbine used
print(f"Number of selected turbines: {num_turbines.x}")
print(f"Number of selected PVs: {num_pvs.x}")

# Print installation costs
print(f"Turbine installation cost: {turbine_installation_cost.getValue()}")
print(f"PV installation cost: {pv_installation_cost.getValue()}")

# Print yearly costs
print(f"Turbine yearly cost: {turbine_hourly_cost.getValue() * 24 * 365}")
print(f"PV yearly cost: {pv_hourly_cost.getValue() * 24 * 365}")
print(f"Grid yearly cost: {grid_cost.getValue()}")

# Calculate and print total yearly energy generated from each component
total_yearly_pv_energy = sum(selected_pv_type[j].x * num_pvs.x * PowerPV[j] * 24 * 365 for j in range(len(PowerPV)))
total_yearly_wind_energy = sum(selected_turbine_type[j].x * num_turbines.x * PowerTurbine[j] * 24 * 365 for j in range(len(PowerTurbine)))

print(f"Total yearly PV energy generated: {total_yearly_pv_energy}")
print(f"Total yearly wind energy generated: {total_yearly_wind_energy}")