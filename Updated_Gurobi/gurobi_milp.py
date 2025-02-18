import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Load Solar Power Data (Skipping first 28 rows)
solar_df = pd.read_csv(r"C:\Users\crane30\DER-Code\DER-Optimization-Project\Environmental Data V4\solar_data_saved.csv", skiprows=28, usecols=[0, 1, 2, 3], names=["Month", "Day", "Hour", "Solar_Power"], header = 0)

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
load_demand = 7000  # Total load demand in MWh/day
solar_cost = 50    # Cost of solar PV energy ($/MWh)
wind_cost = 30     # Cost of wind energy ($/MWh)
grid_cost = 70     # Cost of grid energy ($/MWh)

total_cost = 0
total_solar = 0
total_wind = 0
total_grid = 0
results = []

# Iterate over each hour
for _, row in power_data.iterrows():
    solar_max = row["Solar_Power"]
    wind_max = row["Wind_Power"]
    
    # Create a new optimization model for each hour
    model = gp.Model("DER_Optimization")
    
    # Decision Variables
    solar_energy = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=solar_max, name="SolarEnergy")
    wind_energy = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=wind_max, name="WindEnergy")
    grid_energy = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="GridEnergy")
    
    # Objective Function: Minimize total cost
    model.setObjective(
        solar_cost * solar_energy + wind_cost * wind_energy + grid_cost * grid_energy,
        GRB.MINIMIZE
    )
    
    # Constraints
    model.addConstr(solar_energy + wind_energy + grid_energy >= load_demand, "DemandConstraint")
    
    # Optimize the model
    model.optimize()
    
    # Store results
    if model.status == GRB.OPTIMAL:
        results.append([
            row["Month"], row["Day"], row["Hour"],
            solar_energy.x, wind_energy.x, grid_energy.x, model.objVal
        ])
        total_solar += solar_energy.x
        total_wind += wind_energy.x
        total_grid += grid_energy.x
        total_cost += model.objVal
    
# Convert results to DataFrame and save
results_df = pd.DataFrame(results, columns=["Month", "Day", "Hour", "Solar Energy (MWh)", "Wind Energy (MWh)", "Grid Energy (MWh)", "Total Cost ($)"])
results_df.to_csv("optimized_results.csv", index=False)

# Print yearly summary
print("Optimization complete. Results saved to 'optimized_results.csv'.")
print("\nYearly Summary:")
print(f"Total Solar Energy Used: {total_solar:.2f} MWh")
print(f"Total Wind Energy Used: {total_wind:.2f} MWh")
print(f"Total Grid Energy Used: {total_grid:.2f} MWh")
print(f"Total Cost: ${total_cost:.2f}")
