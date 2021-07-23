import pandas as pd
from pyomo.core.base.util import Initializer
import pyomo.environ as pyo

topology = pd.read_csv("NCS/rmfgen.lam-060.d-6-2-15/topology.csv")
topology.set_index(["Start", "End"], inplace=True)
topology.sort_index(inplace=True)
flows = pd.read_csv("NCS/rmfgen.lam-060.d-6-2-15/flows.csv")
# flows.set_index(["Source", "Destination"], inplace=True)
# flows.sort_index(inplace=True)

model = pyo.ConcreteModel()

starts = set(topology.index.get_level_values("Start"))
ends = set(topology.index.get_level_values("End"))
nodes = list(starts | ends).sort()
model.Nodes = pyo.Set(initialize=nodes)
model.Arcs = pyo.Set(initialize=list(topology.index))
model.Arcs2 = pyo.RangeSet(0, len(topology.reset_index().index) - 1)
model.K = pyo.RangeSet(0, len(flows.index) - 1)

model.c = pyo.Param(model.Arcs2, within=pyo.NonNegativeIntegers)

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
        return sum(m.X[i, j, k] for j in succs) - sum(m.X[j, i, k] for j in precs) == 0
    elif i == s:
        return sum(m.X[i, j, k] for j in succs) - sum(m.X[j, i, k] for j in precs) == d
    elif i == t:
        return sum(m.X[i, j, k] for j in succs) - sum(m.X[j, i, k] for j in precs) == -d

model.traffic_contraint = pyo.Constraint(model.Nodes, model.K, rule=traffic_constraint)

# def capacity_constraint(m, i, j):
def capacity_constraint(m, a):
    i, j, c = topology.reset_index().loc[a]
    # return sum(m.X[i, j, k] for k in m.K) <= m.c[a] * m.alpha
    return sum(m.X[i, j, k] for k in m.K) <= c * m.alpha

model.capacity_constraint = pyo.Constraint(model.Arcs2, rule=capacity_constraint)

opt = pyo.SolverFactory("cbc")
opt.solve(model)
