import gurobipy as gp
from gurobipy import GRB

# Create a model
model = gp.Model("DER_Optimization")

# Parameters
load_demand = 7000  # Total load demand in MWh/day
solar_cost = 51     # Cost of solar PV energy ($/MWh)
wind_cost = 89      # Cost of wind energy ($/MWh)
grid_cost = 50      # Cost of grid energy ($/MWh)

solar_max = 500     # Maximum solar PV output (MWh/day)
wind_max = 500      # Maximum wind turbine output (MWh/day)

# Weights: Prioritizing Cost Only
w_cost = 1.0
w_efficiency = 100
w_sustainability = 0.0

# Decision Variables
solar_energy = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=solar_max, name="SolarEnergy")
wind_energy = model.addVar(vtype=GRB.CONTINUOUS, lb=0, ub=wind_max, name="WindEnergy")
grid_energy = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="GridEnergy")

# Define objectives
financial_objective = solar_cost * solar_energy + wind_cost * wind_energy + grid_cost * grid_energy  # Minimize cost
efficiency_objective = grid_energy  # Minimize grid energy usage (not considered)
sustainability_objective = solar_energy + wind_energy  # Maximize renewable energy (not considered)

# Set the objective (only cost matters)
model.setObjective(
    w_cost * financial_objective + w_efficiency * efficiency_objective - w_sustainability * sustainability_objective,
    GRB.MINIMIZE
)

# Constraints
model.addConstr(solar_energy + wind_energy + grid_energy >= load_demand, "DemandConstraint")

# Optimize the model
model.optimize()

# Results
if model.status == GRB.OPTIMAL:
    total_cost = (solar_energy.x * solar_cost) + (wind_energy.x * wind_cost) + (grid_energy.x * grid_cost)
    
    print(f"Optimal Solution Found:")
    print(f"Solar Energy: {solar_energy.x:.2f} MWh")
    print(f"Wind Energy: {wind_energy.x:.2f} MWh")
    print(f"Grid Energy: {grid_energy.x:.2f} MWh")
    print(f"Total Cost: ${total_cost:.2f}")  # Explicitly calculated
else:
    print("No optimal solution found.")
