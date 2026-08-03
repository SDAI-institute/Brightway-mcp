# Brightway2 Learning Hub â€” Master Checklist

Legend: `[ ]` not started Â· `[~]` partial / in progress Â· `[x]` done & verified

## Phase 0 â€” Environment

- [x] Dedicated venv at `Brightway2/.venv` (Python 3.13.5)
- [x] Brightway 2.5 stack installed (bw2data 4.7, bw2calc 2.5.0, bw2io 0.9.17, bw2analyzer, bw_processing, stats_arrays)
- [x] Support stack installed (pandas, matplotlib, seaborn, jupyter, fastmcp, pytest, pypardiso)
- [x] `brightway25` Jupyter kernel registered
- [x] `import bw2data` + biosphere setup verified (via `bw2io.remote.install_project`; `bw2setup()` broken on this stack â€” documented)
- [x] `requirements.txt` with pinned working versions
- [x] `SETUP.md` (install, kernel, optional ecoinvent path, biosphere naming quirk)
- [x] Full API smoke test (21/22 checks; the 1 fail was a test-script bug, corrected pattern verified)

## Phase 1 â€” Core tutorials (md + ipynb pairs)

- [x] 00 Setup & environment
- [x] 01 Brightway ecosystem & LCA math (A/B matrices, demand â†’ LCI â†’ LCIA)
- [x] 02 Projects & data management (bw2data)
- [x] 03 Building foreground inventories in code (hand-calc vs Brightway cross-check)
- [x] 04 Importing data with bw2io (Excel importer; optional ecoinvent section)
- [x] 05 LCIA with bw2calc (LCA object, methods, multi-method/multi-FU)

## Phase 2 â€” Advanced tutorials (md + ipynb pairs)

- [x] 06 Contribution analysis & interpretation (bw2analyzer)
- [x] 07 Uncertainty & Monte Carlo (stats_arrays, use_distributions)
- [x] 08 Parameterized inventories & scenarios
- [x] 09 Comparative LCA & visualization
- [x] 10 Advanced: matrices, custom LCIA methods, graph traversal, legacy-vs-2.5 diff table

## Phase 3 â€” Case studies (study.md + study.ipynb + data/)
