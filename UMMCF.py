import pandas as pd
import pyomo.environ as pyo

topology = pd.read_csv("dummy_topology.csv")
topology.set_index(["Start", "End"], inplace=True)
topology.sort_index(inplace=True)
flows = pd.read_csv("dummy_flows.csv")
# flows.set_index(["Source", "Destination"], inplace=True)
# flows.sort_index(inplace=True)

model = pyo.ConcreteModel()

starts = set(topology.index.get_level_values("Start"))
ends = set(topology.index.get_level_values("End"))
nodes = sorted(starts | ends)

model.Nodes = pyo.Set(initialize=nodes)
model.Arcs = pyo.Set(initialize=list(topology.index))
model.K = pyo.RangeSet(0, len(flows.index) - 1)

model.X = pyo.Var(model.Arcs, model.K, within=pyo.Binary) # prendo il flusso o non lo prendo
model.alpha = pyo.Var(within=pyo.PercentFraction) # alpha è compreso tra 0 e 1

def obj_expression(m):
    return m.alpha

model.OBJ = pyo.Objective(rule=obj_expression)

def traffic_constraint(m, i, k):
    arcs = topology.reset_index()
    precs = arcs[ arcs.End == i ]["Start"]
    succs = arcs[ arcs.Start == i ]["End"]
    s, t, d = flows.loc[k]
    if i != s and i != t:
        return sum(m.X[i, j, k]*d for j in succs) - sum(m.X[j, i, k]*d for j in precs) == 0
    elif i == s:
        return sum(m.X[i, j, k]*d for j in succs) - sum(m.X[j, i, k]*d for j in precs) == d
    elif i == t:
        return sum(m.X[i, j, k]*d for j in succs) - sum(m.X[j, i, k]*d for j in precs) == -d

model.traffic_constraint = pyo.Constraint(model.Nodes, model.K, rule=traffic_constraint)

def capacity_constraint(m, i, j):
    c = int(topology.loc[i, j]["Capacity"])
    return sum(m.X[i, j, k] * flows.loc[k]["Demand"] for k in m.K) <= c * m.alpha

model.capacity_constraint = pyo.Constraint(model.Arcs, rule=capacity_constraint)

solver = pyo.SolverFactory("cbc")
results = solver.solve(model, tee=True, keepfiles=False)

if results.solver.status != pyo.SolverStatus.ok:
    print("Check solver not ok?")
if results.solver.termination_condition != pyo.TerminationCondition.optimal:  
    print("Check solver optimality?")

print("Solution: ", model.OBJ())
print(model.X.pprint())
