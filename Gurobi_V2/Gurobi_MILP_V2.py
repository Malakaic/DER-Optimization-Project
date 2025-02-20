from gurobipy import Model, GRB

# Create a new model
model = Model("DER_Optimization")

# Decision variables
# Turbine and PV are integer variables with bounds [0, 3]
turbine = model.addVars(3, vtype=GRB.INTEGER, lb=0, ub=3, name="turbine")
PV = model.addVars(3, vtype=GRB.INTEGER, lb=0, ub=3, name="PV")
grid = model.addVar(vtype=GRB.CONTINUOUS, lb=0, name="grid")

# Power capacity of each component
PowerTurbine = [5, 10, 15]
PowerPV = [3, 6, 9]

# Costs per unit power
costTurbine = [100, 180, 360]
costPV = [50, 90, 130]
costgrid = 200

# Print parameter values
print("PowerTurbine:", PowerTurbine)
print("PowerPV:", PowerPV)
print("costTurbine:", costTurbine)
print("costPV:", costPV)
print("costgrid:", costgrid)

# Objective function: Minimize total cost
cost_expr = sum(costTurbine[i] * PowerTurbine[i] * turbine[i] for i in range(3)) + \
            sum(costPV[i] * PowerPV[i] * PV[i] for i in range(3)) + \
            costgrid * grid
model.setObjective(cost_expr, GRB.MINIMIZE)

# Constraint: Total power must equal 25 kW
total_power_expr = sum(PowerTurbine[i] * turbine[i] for i in range(3)) + \
                   sum(PowerPV[i] * PV[i] for i in range(3)) + \
                   grid
model.addConstr(total_power_expr == 25, "PowerBalance")

# Print constraint expression
print("Total Power Constraint Expression:", total_power_expr)

# Solve the optimization problem
model.optimize()

# Print the results
if model.status == GRB.OPTIMAL:
    print("Optimal Solution Found")
    for i in range(3):
        print(f"Turbine {i+1}: {turbine[i].x}")
        print(f"PV {i+1}: {PV[i].x}")
    print(f"Grid: {grid.x}")
    print(f"Total Cost: {model.objVal}")
else:
    print("No optimal solution found")
