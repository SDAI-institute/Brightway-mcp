# Tutorial 08 â€” Parameterized Inventories & Scenario Analysis

**Companion notebook:** [08_parameters_scenarios.ipynb](08_parameters_scenarios.ipynb)

System analysis lives on questions like *"what if the grid decarbonizes 40%?"*,
*"what if yield improves to 0.48?"*. Hard-coding numbers into exchanges makes
those questions painful. This tutorial covers two complementary techniques:

1. **bw2data parameters** â€” named variables + formulas stored *in* the model
2. **Scenario sweeps** â€” programmatically re-evaluating the model over
   parameter sets (the workhorse pattern used in all three case studies)

## 1. The bw2data parameter system

Three scopes, evaluated in order (each may reference the previous):

```
ProjectParameter   â†’   DatabaseParameter   â†’   ActivityParameter (in "groups")
```

```python
from bw2data.parameters import parameters, ProjectParameter

parameters.new_project_parameters([
    {"name": "grid_ci",   "amount": 0.95},   # kg CO2 / kWh
    {"name": "steel_kg",  "amount": 1.2},
])

parameters.new_activity_parameters([
    {"name": "elec_use", "formula": "steel_kg * 2.9 + 0.8", "amount": 0},
], group="kettle_group")
```

Exchanges opt in by carrying a `formula` and being registered to a group:

```python
exc["formula"] = "steel_kg"
exc.save()
parameters.add_exchanges_to_group("kettle_group", kettle_act)
ActivityParameter.recalculate_exchanges("kettle_group")
```

After `recalculate_exchanges`, every formula-bearing exchange's `amount` is
recomputed. Change a `ProjectParameter`, call `parameters.recalculate()`, and
