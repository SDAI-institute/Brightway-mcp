# Tutorial 10 â€” Advanced Topics: Matrices, Custom Methods, Graph Traversal

**Companion notebook:** [10_advanced_topics.ipynb](10_advanced_topics.ipynb)

Grab-bag of the techniques that separate "runs tutorials" from "builds
systems": direct matrix surgery, writing your own LCIA method, structured
supply-chain traversal, performance, and the legacyâ†”2.5 translation table.

## 1. Working with the matrices directly

After `lca.lci()`:

```python
A = lca.technosphere_matrix      # scipy.sparse
B = lca.biosphere_matrix
lca.dicts.activity[node.id]      # node â†’ column index (and .reversed for back)
lca.dicts.biosphere[flow.id]     # flow â†’ row index
```

Things this unlocks (all in the notebook):

- **Audit**: densify a small foreground block and eyeball it against your
  process table (the tutorial-03 trust pattern, industrialized).
- **What-if without DB writes**: modify a matrix cell in place, then
  `lca.redo_lci()` / re-solve â€” the fastest possible sensitivity loop:

```python
row = lca.dicts.activity[elec.id]; col = lca.dicts.activity[steel.id]
lca.technosphere_matrix[row, col] *= 0.8       # 20% less electricity in steel
lca.lci(); lca.lcia()
```

- **Cumulative intensity vectors**: solve `Aáµ€x = (CÂ·B)áµ€` once to get impact
  intensity *per unit of every process* simultaneously â€” how backgrounds like
  ecoinvent get their per-process footprints.

## 2. Writing a custom LCIA method

A method is just `[(flow_key_or_id, CF), ...]` plus metadata:

```python
my = bd.Method(("SDAI", "simple GWP", "v1"))
my.register(unit="kg CO2-eq", description="teaching method")
