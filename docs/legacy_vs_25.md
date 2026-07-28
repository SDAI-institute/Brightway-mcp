# Legacy Brightway2 ↔ Brightway 2.5 Migration Guide

"Brightway2" now names two things. Same concepts, different calculation layer.

| | Legacy Brightway2 | Brightway 2.5 (this hub) |
|-|-------------------|--------------------------|
| Storage | `bw2data 3.x` | `bw2data ≥ 4` |
| Calculator | `bw2calc 1.x` | `bw2calc ≥ 2` |
| Matrix data | pickled numpy arrays | `bw_processing` **datapackages** |
| Matrix assembly | built-in | `matrix_utils` |
| Status | maintenance | active development |
| GUI | Activity Browser 1 | Activity Browser 2 |

The big architectural change: 2.5 stores matrix data as portable **datapackages**
and assembles matrices with `matrix_utils`. This enables scenario arrays, remote
calculation, and cleaner uncertainty — at the cost of some API changes.

## API translation table

| Task | Legacy | 2.5 |
|------|--------|-----|
| Import style | `from brightway2 import *` | explicit: `import bw2data as bd, bw2calc as bc` |
| Biosphere setup | `bw2setup()` | `bw2io.remote.install_project("ecoinvent-<v>-biosphere", proj)` |
| Biosphere name | `biosphere3` | `ecoinvent-3.10-biosphere` (resolve dynamically) |
| LCA construction | `LCA({act: 1}, method)` | same, or `LCA(demand, data_objs=[...])` for datapackages |
| Extra demand | `redo_lcia({act: 1})` | `lca.lcia(demand={act.id: 1})` — **`.id`, not the object** |
| Monte Carlo | `MonteCarloLCA(demand, method)` class | `LCA(..., use_distributions=True)` + `next(lca)` |
| Multi-LCA | `calculation_setups` + `MultiLCA(name)` | loop + `switch_method`, or new `MultiLCA(demands=, method_config=)` |
| Matrix row/col map | `lca.activity_dict`, `lca.biosphere_dict` | `lca.dicts.activity`, `lca.dicts.biosphere` |
| Nodes/edges | `new_activity` / `new_exchange` | same names work; `new_node` / `new_edge` preferred |
| Parameters recalc | `parameters.recalculate()` | same, but query rows via `ProjectParameter.select()` (peewee) |

## Gotchas when porting legacy code

1. **`redo_lcia({activity: 1})` → `lcia(demand={activity.id: 1})`.** The demand
   dict is keyed by integer `id`, not the activity object. This is the single
   most common port error.
2. **No `MonteCarloLCA`.** Delete the import; pass `use_distributions=True` to
   `LCA` and iterate it.
3. **`bw2setup()` may fail** on the current bw2data/bw2io combo (method-writing
   `ValueError`). Use the remote prepared project — it's the recommended path.
4. **Don't share a data directory** between a bw2data 3.x env and a 4.x env.
   4.x can *migrate* legacy projects, but keep the environments separate
   (different virtualenvs) to avoid format confusion.
5. **float32 storage** in datapackages means results agree to ~1e-7 relative,
   not float64 machine precision. Loosen equality tolerances accordingly.

## Should you migrate?

Yes for new work — 2.5 is where development happens, it works with modern Python,
and Activity Browser 2, `premise`, and the current docs all target it. Legacy is
fine for reproducing an existing legacy study but pins old dependencies.
