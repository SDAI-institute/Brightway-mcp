# Tutorial 05 — Impact Assessment with bw2calc

**Companion notebook:** [05_lcia_with_bw2calc.ipynb](05_lcia_with_bw2calc.ipynb)

You have inventories (tutorials 03–04) and characterization methods (installed
by `bw2setup`). This tutorial covers the calculation layer end to end: the `LCA`
object lifecycle, choosing methods wisely, and the efficient patterns for
*many* calculations (multiple methods × multiple alternatives).

## 1. The basic lifecycle

```python
import bw2data as bd, bw2calc as bc

kettle = bd.get_node(database="kettle", code="kettle")
gwp = ("IPCC 2013", "climate change", "global warming potential (GWP100)")

lca = bc.LCA({kettle: 1}, method=gwp)   # 1 = functional unit amount
lca.lci()          # build A, B; solve A·s = f
lca.lcia()         # apply characterization
lca.score          # kg CO₂-eq per functional unit
```

> **What `{kettle: 1}` means:** demand of 1 unit *of kettle's reference
> product*. Any linear combination works: `{kettle: 1000}` or even
> `{kettle: 1, other_thing: 3}`.

> **2.5 internals:** `bc.LCA(demand, method=...)` is the convenience form — it
> calls `bd.prepare_lca_inputs()` behind the scenes to gather datapackages. The
> pure-2.5 form (`bc.LCA(demand=fu, data_objs=objs)`) matters when you do
> scenario datapackages (tutorial 08) or calculate without a bw2data project.

## 2. Choosing LCIA methods

`bd.methods` contains hundreds of entries. Practical guidance:

- **Climate**: `IPCC 2013 / GWP 100a` (or IPCC 2021 where available)
- **Multi-category midpoint**: ReCiPe 2016 Midpoint (H) — climate, acidification,
  eutrophication, human tox, land, water…
- **EU regulatory context**: EF v3.1 methods
- **Single-score teaching demos**: ReCiPe Endpoint (but understand the weighting!)

The notebook builds a `find_methods(*substrings)` helper and assembles a
"portfolio" of 4–5 midpoint categories used for the rest of the tutorials.
Always check `bd.Method(m).metadata["unit"]` — comparing scores across methods
with different units is meaningless.

## 3. Many calculations, done right

**Naive** (rebuilds matrices every time — slow):

```python
for m in methods:
    lca = bc.LCA({kettle: 1}, method=m); lca.lci(); lca.lcia()
```

**Right** — factorize once, then switch:

```python
lca = bc.LCA({kettle: 1}, method=methods[0])
lca.lci(factorize=True)        # LU factorization cached
lca.lcia()
for m in methods[1:]:
    lca.switch_method(m)       # only swaps C
    lca.lcia()

for act in alternatives:        # new demand: reuse factorization
    lca.lcia(demand={act.id: 1})   # redo_lci happens internally
```

`factorize=True` makes each extra demand a cheap back-substitution instead of a
fresh solve — the difference between minutes and seconds on big databases.
The notebook wraps this into a `results_grid(alternatives, methods)` function
returning a tidy pandas DataFrame — a pattern reused in every case study.

> **Legacy note:** old Brightway had `bd.calculation_setups` +
> `bc.MultiLCA(name)`. bw2calc 2.x redesigned `MultiLCA` around explicit
> `demands` / `method_config` dicts; the loop-with-`switch_method` pattern above
> is simpler, works everywhere, and is what we standardize on.

## 4. Inspecting what happened

```python
lca.supply_array          # s — total activity of every process
lca.inventory             # B·diag(s): flows × processes (sparse)
lca.characterized_inventory   # C·B·diag(s): the money matrix for hotspots

lca.dicts.activity[act.id]    # activity → matrix column index
lca.dicts.biosphere[flow.id]  # flow → row index
```

Row/column sums of `characterized_inventory` give impact *by elementary flow*
and *by process* respectively — that's already contribution analysis, formalized
in tutorial 06.

## 5. Interpreting scores

- Scores are **per functional unit** — always report the FU with the number.
- A midpoint score (kg CO₂-eq) is not "damage"; it's a normalized inventory.
- Cross-method comparisons need identical units *and* identical system
  boundaries; cross-*database* comparisons (foreground on USEEIO vs ecoinvent)
  additionally differ in background completeness — expect systematic offsets.

## Pitfalls

- `lca.score` before `lca.lcia()` → AttributeError. Lifecycle is
  `lci() → lcia() → score`.
- Method tuples must match **exactly** (they're dict keys). Copy them from a
  `bd.methods` search, never type from memory.
- If a foreground exchange references a biosphere flow that the method has no CF
  for, it contributes zero *silently* — the notebook shows how to audit CF
  coverage with `bd.Method(m).load()`.
- After editing a database, if scores look stale, re-instantiate the `LCA`
  object (matrix data is read at construction).

## Next

→ [06 — Contribution analysis](06_contribution_analysis.md): from a single
score to *why*: which processes and which emissions drive it.
