import gurobipy as gp
from gurobipy import GRB
import pandas as pd

# Load Solar Power Data (Skipping first 28 rows)
solar_df = pd.read_csv(
    r"C:\Users\crane30\DER-Code\DER-Optimization-Project\Environmental Data V4\solar_data_saved.csv",
    skiprows=28, usecols=[0, 1, 2, 3], names=["Month", "Day", "Hour", "Solar_Power"], header=0
)

# Load Wind Power Data
wind_df = pd.read_csv(
    r"C:\Users\crane30\DER-Code\DER-Optimization-Project\Environmental Data V4\wind_power_output_main_GUI.csv",
    usecols=[0, 1, 2, 3, 6], names=["Year", "Month", "Day", "Hour", "Wind_Power"], header=0
)

# Define month mapping
month_map = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
}

# Convert month names to numbers if necessary
solar_df["Month"] = solar_df["Month"].map(month_map)
wind_df["Month"] = wind_df["Month"].map(month_map)

# Fill NaN values with 0 in Solar and Wind DataFrames (or drop if necessary)
solar_df.fillna(0, inplace=True)
wind_df.fillna(0, inplace=True)

# Ensure consistent data types
solar_df[["Month", "Day"]] = solar_df[["Month", "Day"]].astype(int)
wind_df[["Month", "Day"]] = wind_df[["Month", "Day"]].astype(int)

# Merge data on Month and Day, aggregating hourly data
power_data = pd.merge(
    solar_df.groupby(['Month', 'Day']).agg({'Solar_Power': 'sum'}).reset_index(),
    wind_df.groupby(['Month', 'Day']).agg({'Wind_Power': 'sum'}).reset_index(),
    on=["Month", "Day"], how="inner"
)

# Fill NaN values again after merging
power_data.fillna(0, inplace=True)

# Parameters
load_demand = 7000  # Total load demand in MWh/day
solar_cost = 500000  # Fixed installation cost of solar PVs ($)
wind_cost = 1000000  # Fixed installation cost of wind turbines ($)
grid_cost = 70       # Cost of grid energy ($/MWh)
solar_capacity = 5   # Capacity of each solar PV panel (MWh)
wind_capacity = 10   # Capacity of each wind turbine (MWh)


# Create a new optimization model
model = gp.Model("DER_Optimization")

# Decision Variables
num_solar_panels = model.addVar(vtype=GRB.INTEGER, lb=0, name="NumSolarPanels")
num_wind_turbines = model.addVar(vtype=GRB.INTEGER, lb=0, name="NumWindTurbines")
grid_energy = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="TotalGridEnergy")
renewable_output = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="RenewableOutput")

# Add maximum limits for practical scenarios
max_solar_panels = 1000  # Adjust according to your scenario
max_wind_turbines = 500   # Adjust according to your scenario
model.addConstr(num_solar_panels <= max_solar_panels, "MaxSolarPanels")
model.addConstr(num_wind_turbines <= max_wind_turbines, "MaxWindTurbines")

# Add minimum installation constraints
model.addConstr(num_solar_panels >= 1, "MinSolarPanels")
model.addConstr(num_wind_turbines >= 1, "MinWindTurbines")

# Constraints for daily energy production limits
for _, row in power_data.iterrows():
    model.addConstr(
        renewable_output == num_solar_panels * solar_capacity + num_wind_turbines * wind_capacity,
        "RenewableOutputConstraint"
    )
    model.addConstr(
        renewable_output + grid_energy >= load_demand,
        f"DemandConstraint_{row['Month']}_{row['Day']}"
    )

# Objective Function: Minimize total system cost while maximizing renewable output
model.setObjective(
    solar_cost * num_solar_panels + wind_cost * num_wind_turbines - grid_cost * grid_energy,
    GRB.MINIMIZE
)

# Optimize the model
model.optimize()

# Store results
if model.status == GRB.OPTIMAL:
    total_solar_energy = num_solar_panels.x * solar_capacity
    total_wind_energy = num_wind_turbines.x * wind_capacity
    total_system_cost = model.objVal
    results = [
        num_solar_panels.x, num_wind_turbines.x, total_solar_energy, total_wind_energy, grid_energy.x, total_system_cost
    ]
    
    # Convert results to DataFrame and save
    results_df = pd.DataFrame([results], columns=["Num Solar Panels", "Num Wind Turbines", "Total Solar Energy (MWh)", "Total Wind Energy (MWh)", "Total Grid Energy (MWh)", "Total Cost ($)"])
    results_df.to_csv("optimized_results.csv", index=False)

    # Print yearly summary
    print("Optimization complete. Results saved to 'optimized_results.csv'.")
    print("\nYearly Summary:")
    print(f"Number of Solar Panels Installed: {num_solar_panels.x:.0f}")
    print(f"Number of Wind Turbines Installed: {num_wind_turbines.x:.0f}")
    print(f"Total Solar Energy Produced: {total_solar_energy:.2f} MWh")
    print(f"Total Wind Energy Produced: {total_wind_energy:.2f} MWh")
    print(f"Total Grid Energy Used: {grid_energy.x:.2f} MWh")
    print(f"Total System Cost: ${total_system_cost:.2f}")
else:
    print("No optimal solution found.")
