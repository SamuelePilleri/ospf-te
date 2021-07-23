from pandas.core.algorithms import mode
import pyomo.environ as pyo

model = pyo.AbstractModel()

model.m = pyo.Param(within=pyo.NonNegativeIntegers)
model.n = pyo.Param(within=pyo.NonNegativeIntegers)

model.I = pyo.RangeSet(1, model.m)
model.J = pyo.RangeSet(1, model.m)
model.K = pyo.RangeSet(1, model.n)

model.c = pyo.Param(model.I, model.J, within=pyo.NonNegativeIntegers)
model.d = pyo.Param(model.K, within=pyo.NonNegativeReals)
model.s = pyo.Param(model.K, within=pyo.NonNegativeReals)
model.t = pyo.Param(model.K, within=pyo.NonNegativeReals)

model.X = pyo.Var(model.I, model.J, model.K, within=pyo.Binary) # prendo il flusso o non lo prendo
model.alpha = pyo.Var(within=pyo.PercentFraction) # alpha è compreso tra 0 e 1

def obj_expression(m):
    return m.alpha

model.OBJ = pyo.Objective(rule=obj_expression)

def traffic_constraint(m, i, k):
    if i != m.s[k] and i != m.t[k]:
        return sum(m.X[i, j, k] for j in m.J) - sum(m.X[j, i, k] for j in m.J) == 0
    elif i == m.s[k]:
        return sum(m.X[i, j, k] for j in m.J) - sum(m.X[j, i, k] for j in m.J) == m.d[k]
    elif i == m.t[k]:
        return sum(m.X[i, j, k] for j in m.J) - sum(m.X[j, i, k] for j in m.J) == -m.d[k]

model.traffic_contraint = pyo.Constraint(model.I, model.K, rule=traffic_constraint)

def capacity_constraint(m, i, j):
    return sum(m.X[i, j, k] for k in m.K) <= m.c[i, j] * m.alpha

model.capacity_constraint(model.I, model.J, rule=capacity_constraint)