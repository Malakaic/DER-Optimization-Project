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
load_demand = 150  # Total hourly load demand (kW)
PowerTurbine = [5, 10, 15]  # Wind turbine capacities (kW)
PowerPV = [3, 6, 9]  # Solar PV capacities (kW)

# Turbine cost $100/kWh, PV cost $50/kWh
costTurbine = [120, 230, 390]  # Cost per kWh for wind turbines
costPV = [150, 190, 230]  # Cost per kWh for solar PV
costgrid = 30  # Cost per kWh from the grid

# Define maximum quantities
max_turbines = 8  # Maximum number of turbines
max_pv = 8  # Maximum number of PV systems

# Define weights for objectives
weight_cost = 0.5  # Weight for cost minimization
weight_renewable = 0.5  # Weight for renewable energy maximization

total_cost = 0
total_solar = 0
total_wind = 0
total_grid = 0
results = []

# Iterate over each hour
for _, row in power_data.iterrows():
    model = gp.Model("DER_Optimization")
    
    # Decision Variables
    turbine = model.addVars(3, vtype=GRB.INTEGER, lb=0, ub=max_turbines, name="Turbine")
    PV = model.addVars(3, vtype=GRB.INTEGER, lb=0, ub=max_pv, name="PV")
    grid_energy = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="GridEnergy")
    
    # Compute power contributions
    total_wind_power = sum(PowerTurbine[i] * turbine[i] for i in range(3))
    total_solar_power = sum(PowerPV[i] * PV[i] for i in range(3))
    
    # Objective Function: Minimize total cost and maximize renewable energy
    cost_objective = sum(costTurbine[i] * turbine[i] for i in range(3)) + sum(costPV[i] * PV[i] for i in range(3)) + costgrid * grid_energy
    renewable_objective = total_wind_power + total_solar_power
    
    # Set combined objective
    model.setObjective(weight_cost * cost_objective - weight_renewable * renewable_objective, GRB.MINIMIZE)
    
    # Constraints
    model.addConstr(total_wind_power + total_solar_power + grid_energy >= load_demand, "DemandConstraint")
    model.addConstr(sum(turbine[i] for i in range(3)) <= max_turbines, "SingleTurbineConstraint")
    model.addConstr(sum(PV[i] for i in range(3)) <= max_pv, "SinglePVConstraint")
    
    # Optimize the model
    model.optimize()
    
    # Store results
    if model.status == GRB.OPTIMAL:
        turbine_quantities = [turbine[i].x for i in range(3)]
        PV_quantities = [PV[i].x for i in range(3)]
        results.append([row["Month"], row["Day"], row["Hour"],
            sum(PowerPV[i] * PV[i].x for i in range(3)),
            sum(PowerTurbine[i] * turbine[i].x for i in range(3)),
            grid_energy.x, model.objVal,
            *turbine_quantities, *PV_quantities
        ])
        total_solar += sum(PowerPV[i] * PV[i].x for i in range(3))
        total_wind += sum(PowerTurbine[i] * turbine[i].x for i in range(3))
        total_grid += grid_energy.x
        total_cost += model.objVal

# Convert results to DataFrame and save
columns = ["Month", "Day", "Hour", "Solar Energy (kWh)", "Wind Energy (kWh)", "Grid Energy (kWh)", "Total Cost ($)",
           "Turbine_1", "Turbine_2", "Turbine_3", "PV_1", "PV_2", "PV_3"]
results_df = pd.DataFrame(results, columns=columns)
results_df.to_csv("optimized_results.csv", index=False)

# Print yearly summary
print("Optimization complete. Results saved to 'optimized_results.csv'.")
print("\nYearly Summary:")
print(f"Total Solar Energy Used: {total_solar:.2f} MWh")
print(f"Total Wind Energy Used: {total_wind:.2f} MWh")
print(f"Total Grid Energy Used: {total_grid:.2f} MWh")
print(f"Total Cost: ${total_cost:.2f}")
print("\nTurbine Quantities Used:")
print(f"Turbine 1: {sum(row[7] for row in results):.0f}")
print(f"Turbine 2: {sum(row[8] for row in results):.0f}")
print(f"Turbine 3: {sum(row[9] for row in results):.0f}")
print("\nPV Quantities Used:")
print(f"PV 1: {sum(row[10] for row in results):.0f}")
print(f"PV 2: {sum(row[11] for row in results):.0f}")
print(f"PV 3: {sum(row[12] for row in results):.0f}")
