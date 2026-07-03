# Tutorial 08 — Parameterized Inventories & Scenario Analysis

**Companion notebook:** [08_parameters_scenarios.ipynb](08_parameters_scenarios.ipynb)

System analysis lives on questions like *"what if the grid decarbonizes 40%?"*,
*"what if yield improves to 0.48?"*. Hard-coding numbers into exchanges makes
those questions painful. This tutorial covers two complementary techniques:

1. **bw2data parameters** — named variables + formulas stored *in* the model
2. **Scenario sweeps** — programmatically re-evaluating the model over
   parameter sets (the workhorse pattern used in all three case studies)

## 1. The bw2data parameter system

Three scopes, evaluated in order (each may reference the previous):

```
ProjectParameter   →   DatabaseParameter   →   ActivityParameter (in "groups")
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
the whole cascade updates. Formulas support arithmetic, `exp/log/sqrt`, and
references to any visible parameter name.

**When to use it:** models you'll hand to others / open in Activity Browser —
the parameterization travels with the database.

## 2. The sweep pattern (plain Python, maximum control)

For analysis scripts, a build-function is often clearer than stored formulas:

```python
def build_kettle(grid_ci=0.95, steel_kg=1.2, pp_kg=0.4):
    bd.Database("kettle_p").write(make_data(grid_ci, steel_kg, pp_kg))
    return bd.get_node(database="kettle_p", code="kettle")

results = []
for ci in np.linspace(0.1, 1.0, 10):          # grid decarbonization sweep
    act = build_kettle(grid_ci=ci)
    lca = bc.LCA({act: 1}, gwp); lca.lci(); lca.lcia()
    results.append((ci, lca.score))
```

Rebuilding a small foreground database is milliseconds; don't over-engineer.
The notebook wraps this into a tidy `sweep(param_grid) → DataFrame` helper and
plots score-vs-parameter curves, including a two-parameter contour.

## 3. Scenarios as data: one-at-a-time & named scenarios

The notebook then formalizes scenarios as dicts —

```python
SCENARIOS = {
    "baseline":        dict(grid_ci=0.95),
    "2030 grid":       dict(grid_ci=0.45),
    "green steel":     dict(grid_ci=0.45, steel_kg=1.2, steel_ci=0.4),
}
```

— and produces the standard **scenario × impact-category** results table plus a
tornado chart (one-at-a-time ±20% on each parameter, sorted by output swing).
Tornado charts are the fastest honest answer to "which assumption matters?".

## 4. Datapackage scenarios (the pure-2.5 mechanism, preview)

Brightway 2.5's native scenario machinery operates *below* bw2data: a
`bw_processing` datapackage can carry **arrays of alternative values** for
specific matrix cells, and `bc.LCA(..., data_objs=[...])` consumes them without
touching the database. This enables huge scenario sets (IAM-coupled background
scenarios à la `premise`) with zero database rewrites. The notebook shows a
minimal example — overriding one technosphere cell from a handmade datapackage —
so the concept is concrete; production use belongs to advanced workflows.

## Pitfalls

- Formula-based exchanges are only updated on `recalculate…` calls — a stored
  `amount` can silently be stale w.r.t. its formula.
- Parameter names share one namespace per scope: a DatabaseParameter shadows a
  ProjectParameter of the same name for that database's formulas.
- In sweep-by-rebuild, re-fetch the activity object after each `write()` (the
  old handle points at deleted rows).
- Scenario tables must state the functional unit and method in the caption —
  a scenario table without units is numerology.

## Next

→ [09 — Comparative LCA & visualization](09_comparative_lca_visualization.md):
turn grids of scores into decision-grade figures.
