
from ortools.linear_solver import pywraplp
import pandas as pd


with open('test_data.csv', 'r') as f:
    data = f.readlines()
data = [x.strip() for x in data]
rows = []
for row in data:
    row_items = row.split(',')
    row_items = list(map(float, row_items))
    rows.append(row_items)
data = rows


nutrients = [
    ['Calories', 2],
    ['Protein', 50],
    ['Fat', 70],
    ['Carbohydrates', 310],
    ['Sugar', 90],
    ['Sodium', 2300]]

solver = pywraplp.Solver('SolveStigler', pywraplp.Solver.GLOP_LINEAR_PROGRAMMING)

food = [[]] * len(data)

# Objective: minimize the sum of (price-normalized) foods.
objective = solver.Objective()
for i in range(0, len(data)):

    food[i] = solver.NumVar(0.0, solver.infinity(), str(data[i][0]))
    objective.SetCoefficient(food[i], 1)
objective.SetMinimization()

# Create the constraints, one per nutrient.
constraints = [0] * len(nutrients)
for i in range(0, len(nutrients)):
    constraints[i] = solver.Constraint(nutrients[i][1], solver.infinity())
    for j in range(0, len(data)):
        constraints[i].SetCoefficient(food[j], data[j][i+3])



status = solver.Solve()
print(dir(solver))

if status == solver.OPTIMAL:
    # Display the amounts (in dollars) to purchase of each food.
    price = 0
    num_nutrients = len(data[i]) - 2
    nutrients = [0] * (len(data[i]) - 2)
    for i in range(0, len(data)):
        price += food[i].solution_value()


        for nutrient in range(0, num_nutrients):
            nutrients[nutrient] += data[i][nutrient+2] * food[i].solution_value()

        if food[i].solution_value() > 0:
            print("%s = %f" % (data[i][0], food[i].solution_value()))

    print('Optimal annual price: $%.2f' % (365 * price))
else:  # No optimal solution was found.
    if status == solver.FEASIBLE:
        print('A potentially suboptimal solution was found.')
    else:
        print('The solver could not solve the problem.')
