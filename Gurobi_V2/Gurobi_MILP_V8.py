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

# Lifespan in years
lifespan = 10
# Lifespan in hours (24 hours * 365 days)
lifespan_hours = 24 * 365 * lifespan

# Objective Weights
weight_cost = 0.5
weight_renewable = 0.5

#DER Maximums
turbine_max = 4
PV_max = 20

# Load Solar Power Data (Skipping first 28 rows)
solar_df = pd.read_csv(r"C:\Users\crane30\DER-Code\DER-Optimization-Project\Environmental Data V4\solar_data_saved.csv", skiprows=28, usecols=[0, 1, 2, 3], names=["Month", "Day", "Hour", "Solar_Power"], header=0)
solar_df["Solar_Power"] = (solar_df["Solar_Power"] / 1000) * (PowerPV[0] / 10)  # Convert to kW and adjust for 10 kW panel size

# Load Wind Power Data
wind_df = pd.read_csv(r"C:\Users\crane30\DER-Code\DER-Optimization-Project\Environmental Data V4\wind_power_output_main_GUI.csv", usecols=[0, 1, 2, 3, 6], names=["Year", "Month", "Day", "Hour", "Wind_Power"], header=0)
wind_df["Wind_Power"] = (wind_df["Wind_Power"] / 1500) * PowerTurbine[0]  # Convert to kW and adjust for 1500 kW turbine size

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

# Initialize model
model = gp.Model("DER_Optimization")

# Decision variables (binary for selection)
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

# Max installations constraints (one of each type)
model.addConstr(gp.quicksum(selected_turbine[j] for j in range(len(PowerTurbine))) <= turbine_max, "MaxTurbines")
model.addConstr(gp.quicksum(selected_pv[j] for j in range(len(PowerPV))) <= PV_max, "MaxPV")

# Calculate installation costs and renewable fraction
installation_cost = gp.quicksum(selected_turbine[j] * costTurbine[j] * PowerTurbine[j] for j in range(len(PowerTurbine))) + \
                    gp.quicksum(selected_pv[j] * costPV[j] * PowerPV[j] for j in range(len(PowerPV)))

grid_cost = gp.quicksum(grid_energy[i] * costgrid for i in range(len(power_data)))

# Calculate renewable fraction
total_renewable_power = gp.quicksum(
    selected_turbine[j] * PowerTurbine[j] + selected_pv[j] * PowerPV[j] for j in range(len(PowerTurbine))
)

renewable_fraction = total_renewable_power / (load_demand * len(power_data)) if load_demand > 0 else 0

# Set the objective to minimize costs and maximize renewable output
model.setObjective(weight_cost * (installation_cost + grid_cost) - weight_renewable * renewable_fraction, GRB.MINIMIZE)

# Solve model
model.optimize()

# Store results
results = []
total_grid_energy = 0
installation_cost_total = 0
for i, row in power_data.iterrows():
    grid_usage = grid_energy[i].x
    total_grid_energy += grid_usage
    results.append([row["Month"], row["Day"], row["Hour"],
                    sum(selected_turbine[j].x * PowerTurbine[j] for j in range(len(PowerTurbine))),
                    sum(selected_pv[j].x * PowerPV[j] for j in range(len(PowerPV))),
                    grid_usage
                    ])
    
    # Calculate total installation cost
    installation_cost_total += sum(selected_turbine[j].x * costTurbine[j] * PowerTurbine[j] for j in range(len(PowerTurbine)))
    installation_cost_total += sum(selected_pv[j].x * costPV[j] * PowerPV[j] for j in range(len(PowerPV)))

# Convert results to DataFrame
output_df = pd.DataFrame(results, columns=["Month", "Day", "Hour", "Wind_Power", "Solar_Power", "Grid_Consumption"])

# Save to Excel
output_df.to_excel("DER_Optimization_Results_Final_Version.xlsx", index=False)

# Print summary
print("Optimized DER System:")
turbine_used = [j for j in range(len(PowerTurbine)) if selected_turbine[j].x > 0]
pv_used = [j for j in range(len(PowerPV)) if selected_pv[j].x > 0]

if turbine_used:
    print(f"Selected Wind Turbine Capacity: {PowerTurbine[turbine_used[0]]} kW")
    print(f"Installation Cost for Wind Turbine: ${costTurbine[turbine_used[0]] * PowerTurbine[turbine_used[0]]}")
else:
    print("No Wind Turbine Selected")

if pv_used:
    print(f"Selected Solar PV Capacity: {PowerPV[pv_used[0]]} kW")
    print(f"Installation Cost for Solar PV: ${costPV[pv_used[0]] * PowerPV[pv_used[0]]}")
else:
    print("No Solar PV Selected")

print(f"Total Installation Costs for DERs: ${installation_cost_total:.2f}")
print(f"Total Wind Turbines Installed: {len(turbine_used)}")
print(f"Total Solar Panels Installed: {len(pv_used)}")
print(f"Total Grid Energy Used Throughout Year: {total_grid_energy:.2f} kWh")
print(f"Hourly Energy Costs from Grid: ${grid_cost.getValue():.2f} (Total: ${total_grid_energy * costgrid:.2f})")
