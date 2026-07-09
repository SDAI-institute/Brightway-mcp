# Tutorial 05 â€” Impact Assessment with bw2calc

**Companion notebook:** [05_lcia_with_bw2calc.ipynb](05_lcia_with_bw2calc.ipynb)

You have inventories (tutorials 03â€“04) and characterization methods (installed
by `bw2setup`). This tutorial covers the calculation layer end to end: the `LCA`
object lifecycle, choosing methods wisely, and the efficient patterns for
*many* calculations (multiple methods Ã— multiple alternatives).

## 1. The basic lifecycle

```python
import bw2data as bd, bw2calc as bc

kettle = bd.get_node(database="kettle", code="kettle")
gwp = ("IPCC 2013", "climate change", "global warming potential (GWP100)")

lca = bc.LCA({kettle: 1}, method=gwp)   # 1 = functional unit amount
lca.lci()          # build A, B; solve AÂ·s = f
lca.lcia()         # apply characterization
lca.score          # kg COâ‚‚-eq per functional unit
```

> **What `{kettle: 1}` means:** demand of 1 unit *of kettle's reference
> product*. Any linear combination works: `{kettle: 1000}` or even
> `{kettle: 1, other_thing: 3}`.

> **2.5 internals:** `bc.LCA(demand, method=...)` is the convenience form â€” it
> calls `bd.prepare_lca_inputs()` behind the scenes to gather datapackages. The
> pure-2.5 form (`bc.LCA(demand=fu, data_objs=objs)`) matters when you do
> scenario datapackages (tutorial 08) or calculate without a bw2data project.

## 2. Choosing LCIA methods

`bd.methods` contains hundreds of entries. Practical guidance:

- **Climate**: `IPCC 2013 / GWP 100a` (or IPCC 2021 where available)
- **Multi-category midpoint**: ReCiPe 2016 Midpoint (H) â€” climate, acidification,
  eutrophication, human tox, land, waterâ€¦
- **EU regulatory context**: EF v3.1 methods
- **Single-score teaching demos**: ReCiPe Endpoint (but understand the weighting!)

The notebook builds a `find_methods(*substrings)` helper and assembles a
"portfolio" of 4â€“5 midpoint categories used for the rest of the tutorials.
Always check `bd.Method(m).metadata["unit"]` â€” comparing scores across methods
with different units is meaningless.

## 3. Many calculations, done right
