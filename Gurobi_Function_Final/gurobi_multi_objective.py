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
costgrid = 0.01  # Grid energy cost per kWh

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



# Initialize model
model = gp.Model("DER_Optimization")

# Decision variables
selected_turbine = model.addVars(len(PowerTurbine), vtype=GRB.BINARY, name="SelectedTurbine")
selected_pv = model.addVars(len(PowerPV), vtype=GRB.BINARY, name="SelectedPV")
grid_energy = model.addVars(len(power_data), vtype=GRB.CONTINUOUS, name="GridEnergy")

# New variable for actual solar power used
actual_solar_power_used = model.addVars(len(power_data), vtype=GRB.CONTINUOUS, name="ActualSolarPowerUsed")

# Ensure only one PV and one wind turbine is selected
model.addConstr(gp.quicksum(selected_turbine[j] for j in range(len(PowerTurbine))) == 1, "SelectOneTurbine")
model.addConstr(gp.quicksum(selected_pv[j] for j in range(len(PowerPV))) == 1, "SelectOnePV")

# Constraints
for i, row in power_data.iterrows():
    # Calculate available wind power
    available_wind_power = sum(
        selected_turbine[j] * row[f"Turbine-{j+1} Power"] for j in range(len(PowerTurbine))
    )

    # Constraint to limit actual solar power to available solar power
    model.addConstr(
        actual_solar_power_used[i] <= sum(
            selected_pv[j] * row[f"PV-{j+1} Solar Power"] for j in range(len(PowerPV))
        ),
        name=f"LimitSolarPower_{i}"
    )

    # Load balance constraint considering available wind and actual solar power
    model.addConstr(
        available_wind_power + actual_solar_power_used[i] + grid_energy[i] == load_demand,
        name=f"LoadBalance_{i}"
    )

# Objective function
turbine_installation_cost = gp.quicksum(selected_turbine[j] * costTurbine[j] * PowerTurbine[j] for j in range(len(PowerTurbine)))
pv_installation_cost = gp.quicksum(selected_pv[j] * costPV[j] * PowerPV[j] for j in range(len(PowerPV)))
installation_cost = turbine_installation_cost + pv_installation_cost

turbine_hourly_cost = turbine_installation_cost / lifespan_hours
pv_hourly_cost = pv_installation_cost / lifespan_hours

grid_cost = gp.quicksum(grid_energy[i] * costgrid for i in range(len(power_data)))

total_renewable_power = gp.quicksum(
    selected_turbine[j] * PowerTurbine[j] + selected_pv[j] * PowerPV[j] for j in range(len(PowerTurbine))
)

renewable_fraction = total_renewable_power / (load_demand * len(power_data))

model.setObjective(weight_cost * (installation_cost + grid_cost) - weight_renewable * renewable_fraction, GRB.MINIMIZE)

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
    # Add optimized power data and costs
    result_row.extend([
        sum(selected_pv[j].x * PowerPV[j] for j in range(len(PowerPV))),
        sum(selected_turbine[j].x * PowerTurbine[j] for j in range(len(PowerTurbine))),
        grid_usage,
        sum(selected_pv[j].x * costPV[j] * PowerPV[j] for j in range(len(PowerPV))) / lifespan_hours,
        sum(selected_turbine[j].x * costTurbine[j] * PowerTurbine[j] for j in range(len(PowerTurbine))) / lifespan_hours,
        grid_usage * costgrid
    ])
    results.append(result_row)

# Define column names
columns = ["Month", "Day", "Hour"]
columns.extend([f"Original-PV-{idx+1} Solar Power" for idx in range(len(solar_files))])
columns.extend([f"Original-Turbine-{idx+1} Power" for idx in range(len(wind_files))])
columns.extend(["Optimized-PV-Power", "Optimized-Wind-Turbine-Power", "Grid-Consumption", "Optimized-PV-Hourly-Cost", "Optimized-Turbine-Hourly-Cost", "Hourly-Grid-Cost"])

# Convert results to DataFrame
output_df = pd.DataFrame(results, columns=columns)

# Save to Excel
output_df.to_excel("DER_Optimization_Results_Final_Version.xlsx", index=False)
