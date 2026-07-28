# Legacy Brightway2 â†” Brightway 2.5 Migration Guide

"Brightway2" now names two things. Same concepts, different calculation layer.

| | Legacy Brightway2 | Brightway 2.5 (this hub) |
|-|-------------------|--------------------------|
| Storage | `bw2data 3.x` | `bw2data â‰¥ 4` |
| Calculator | `bw2calc 1.x` | `bw2calc â‰¥ 2` |
| Matrix data | pickled numpy arrays | `bw_processing` **datapackages** |
| Matrix assembly | built-in | `matrix_utils` |
| Status | maintenance | active development |
| GUI | Activity Browser 1 | Activity Browser 2 |

The big architectural change: 2.5 stores matrix data as portable **datapackages**
and assembles matrices with `matrix_utils`. This enables scenario arrays, remote
calculation, and cleaner uncertainty â€” at the cost of some API changes.

## API translation table

| Task | Legacy | 2.5 |
|------|--------|-----|
