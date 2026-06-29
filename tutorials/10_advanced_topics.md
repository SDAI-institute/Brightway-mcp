# Tutorial 10 — Advanced Topics: Matrices, Custom Methods, Graph Traversal

**Companion notebook:** [10_advanced_topics.ipynb](10_advanced_topics.ipynb)

Grab-bag of the techniques that separate "runs tutorials" from "builds
systems": direct matrix surgery, writing your own LCIA method, structured
supply-chain traversal, performance, and the legacy↔2.5 translation table.

## 1. Working with the matrices directly

After `lca.lci()`:

```python
A = lca.technosphere_matrix      # scipy.sparse
B = lca.biosphere_matrix
lca.dicts.activity[node.id]      # node → column index (and .reversed for back)
lca.dicts.biosphere[flow.id]     # flow → row index
```

Things this unlocks (all in the notebook):

- **Audit**: densify a small foreground block and eyeball it against your
  process table (the tutorial-03 trust pattern, industrialized).
- **What-if without DB writes**: modify a matrix cell in place, then
  `lca.redo_lci()` / re-solve — the fastest possible sensitivity loop:

```python
row = lca.dicts.activity[elec.id]; col = lca.dicts.activity[steel.id]
lca.technosphere_matrix[row, col] *= 0.8       # 20% less electricity in steel
lca.lci(); lca.lcia()
```

- **Cumulative intensity vectors**: solve `Aᵀx = (C·B)ᵀ` once to get impact
  intensity *per unit of every process* simultaneously — how backgrounds like
  ecoinvent get their per-process footprints.

## 2. Writing a custom LCIA method

A method is just `[(flow_key_or_id, CF), ...]` plus metadata:

```python
my = bd.Method(("SDAI", "simple GWP", "v1"))
my.register(unit="kg CO2-eq", description="teaching method")
my.write([
    (co2.key, 1.0),
    (ch4.key, 29.8),
    (n2o.key, 273.0),
])
```

Use cases: impact categories that don't ship with Brightway (e.g. a
company-internal water-stress weighting), reproducing a paper's CFs exactly, or
**regionalized variants** (same flows, site-specific factors). The notebook
writes one, runs it next to the shipped IPCC method, and reconciles the
difference flow by flow — a drill that also teaches you what's *in* a method.

## 3. Structured graph traversal

`print_recursive_calculation` (tutorial 06) is for eyeballs. For *programmatic*
traversal — building Sankey data, custom cutoff logic — use
[`bw_graph_tools`](https://github.com/brightway-lca/bw_graph_tools):

```python
import bw_graph_tools as bgt
gt = bgt.NewNodeEachVisitGraphTraversal.calculate(lca, cutoff=0.01)
gt["nodes"], gt["edges"]     # ready for networkx / plotly Sankey
```

"New node each visit" means the same background process appearing via two paths
becomes two graph nodes — path-true accounting, exactly what a Sankey wants.
(Optional dependency; the notebook guards the import and falls back to a
homemade recursive traversal that produces the same edge list on the toy model,
which is also a great exercise.)

## 4. Performance notes

| Situation | Lever |
|---|---|
| Many demands / methods | `lci(factorize=True)` + `switch_method` (tut. 05) |
| Slow solves on big DBs | install `pypardiso` (this repo's venv has it) — MKL-backed solver, ~10× on ecoinvent-sized A |
| Monte Carlo at scale | keep one LCA object; iteration cost ≈ one solve; avoid recreating LCA objects in loops |
| Massive scenario sets | datapackage arrays (tut. 08 §4), not database rewrites |
| Memory | matrices are sparse — never `.todense()` anything ecoinvent-sized |

## 5. Legacy Brightway2 ↔ 2.5 translation table

| Task | Legacy (bw2data 3 / bw2calc 1) | 2.5 (this hub) |
|---|---|---|
| Imports | `from brightway2 import *` | explicit: `import bw2data as bd, bw2calc as bc` |
| LCA construction | `LCA({act: 1}, method)` | same, or `demand + data_objs` (datapackages) |
| Demand for extra runs | `redo_lcia({act: 1})` | `lca.lcia(demand={act.id: 1})` — **note: `.id`, not object** |
| Monte Carlo | `MonteCarloLCA(...)` class | `LCA(..., use_distributions=True)` + `next(lca)` |
| Multi-LCA | `calculation_setups` + `MultiLCA(name)` | loop + `switch_method`, or new `MultiLCA(demands=..., method_config=...)` |
| Matrix row/col lookup | `lca.activity_dict` | `lca.dicts.activity` |
| Processed data | `.pickle` arrays | `bw_processing` datapackages (zip) |
| Nodes/edges | `new_activity` / `new_exchange` | same names work; `new_node` / `new_edge` preferred |
| Biosphere setup | `bw2setup()` | `bw2io.remote.install_project("ecoinvent-<v>-biosphere", ...)` |

A prose version with migration advice: [docs/legacy_vs_25.md](../docs/legacy_vs_25.md).

## Where to go next

- **Case studies** in this repo — apply everything on realistic systems
- [`premise`](https://premise.readthedocs.io) — prospective/IAM-modified backgrounds
- [`multifunctional`](https://github.com/brightway-lca/multifunctional) — proper co-product handling
- Activity Browser — GUI over your Brightway projects
- The [Brightway documentation](https://docs.brightway.dev) & the
  [from-the-ground-up](https://github.com/brightway-lca/from-the-ground-up) course
