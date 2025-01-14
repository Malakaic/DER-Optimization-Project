import gurobipy as gp
from gurobipy import GRB

# Create a model
model = gp.Model("DER_Optimization")

# Parameters
load_demand = 700  # Total load demand in MWh/day
solar_cost = 50    # Cost of solar PV energy ($/MWh)
wind_cost = 30     # Cost of wind energy ($/MWh)
grid_cost = 70     # Cost of grid energy ($/MWh)

solar_max = 500    # Maximum solar PV output (MWh/day)
wind_max = 400     # Maximum wind turbine output (MWh/day)

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

# Results
if model.status == GRB.OPTIMAL:
    print(f"Optimal Solution Found:")
    print(f"Solar Energy: {solar_energy.x} MWh")
    print(f"Wind Energy: {wind_energy.x} MWh")
    print(f"Grid Energy: {grid_energy.x} MWh")
    print(f"Total Cost: ${model.objVal}")
else:
    print("No optimal solution found.")