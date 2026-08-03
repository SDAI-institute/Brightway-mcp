# Brightway2 Learning Hub — Master Checklist

Legend: `[ ]` not started · `[~]` partial / in progress · `[x]` done & verified

## Phase 0 — Environment

- [x] Dedicated venv at `Brightway2/.venv` (Python 3.13.5)
- [x] Brightway 2.5 stack installed (bw2data 4.7, bw2calc 2.5.0, bw2io 0.9.17, bw2analyzer, bw_processing, stats_arrays)
- [x] Support stack installed (pandas, matplotlib, seaborn, jupyter, fastmcp, pytest, pypardiso)
- [x] `brightway25` Jupyter kernel registered
- [x] `import bw2data` + biosphere setup verified (via `bw2io.remote.install_project`; `bw2setup()` broken on this stack — documented)
- [x] `requirements.txt` with pinned working versions
- [x] `SETUP.md` (install, kernel, optional ecoinvent path, biosphere naming quirk)
- [x] Full API smoke test (21/22 checks; the 1 fail was a test-script bug, corrected pattern verified)

## Phase 1 — Core tutorials (md + ipynb pairs)

- [x] 00 Setup & environment
- [x] 01 Brightway ecosystem & LCA math (A/B matrices, demand → LCI → LCIA)
- [x] 02 Projects & data management (bw2data)
- [x] 03 Building foreground inventories in code (hand-calc vs Brightway cross-check)
- [x] 04 Importing data with bw2io (Excel importer; optional ecoinvent section)
- [x] 05 LCIA with bw2calc (LCA object, methods, multi-method/multi-FU)

## Phase 2 — Advanced tutorials (md + ipynb pairs)

- [x] 06 Contribution analysis & interpretation (bw2analyzer)
- [x] 07 Uncertainty & Monte Carlo (stats_arrays, use_distributions)
- [x] 08 Parameterized inventories & scenarios
- [x] 09 Comparative LCA & visualization
- [x] 10 Advanced: matrices, custom LCIA methods, graph traversal, legacy-vs-2.5 diff table

## Phase 3 — Case studies (study.md + study.ipynb + data/)

- [x] CS1 Reusable vs single-use bottle (break-even ≈ 35 uses; MC + grid scenarios)
- [x] CS2 Biofuel pathway (parameterized; ~52% GHG savings; analytical MC vs fossil)
- [x] CS3 Cement / industrial system (baseline/alt-fuel/CCS; calcination floor; sensitivity)

## Phase 4 — brightway_mcp server (v0.2 — 22 tools)

- [x] Package scaffold (pyproject.toml, src layout, README)
- [x] Goal & scope tools (health_check, list_projects, list_databases, database_stats, search_activities, search_biosphere, get_activity, list_methods)
- [x] Inventory tools (setup_project, create_database, write_activities, set_uncertainty, import_lcia_methods)
- [x] Impact tools (run_lca, run_multi_method, compare_activities, run_monte_carlo → result_id)
- [x] Interpretation tools (contribution_analysis, top_emissions, supply_chain, export_result, dispose_result)
- [x] Result store (result_id registry)
- [x] Structured error envelopes (error_code, recoverable, suggested_next_actions)
- [x] BRIGHTWAY_READ_ONLY safety mode (verified blocks all writes incl. new ones)
- [x] Resources (brightway://projects, brightway://methods/{project}) + lca_walkthrough prompt
- [x] pytest suite (23 tests, temp project + fixture database) — all green
- [x] Example client configs (mcp.json, claude_desktop_config.json) + demo.py (exercises new tools)
- [x] stdio + streamable-HTTP (--http) entry points
- [x] Local ecoinvent LCIA packs importable via the `import_lcia_methods` tool (mirrors scripts/import_openlca_lcia.py)

## Phase 5 — Reference docs

- [x] docs/cheatsheet.md (one-page API reference)
- [x] docs/glossary.md (LCA + Brightway terms)
- [x] docs/bw_vs_openlca.md (framework comparison)
- [x] docs/legacy_vs_25.md (API migration table)
- [x] docs/copilot_integration.md (wiring into LCA copilot skills/, both paths)
- [x] README.md final (learning path map)

## Local databases integration (`SDAI- Ecosystem\databases\`)

- [x] Audited folder — all files are openLCA-native (`.zolca` = Derby DB; method zips); none directly Brightway-importable
- [x] `ecoinvent_interface` installed; `bw2io.import_ecoinvent_release` path verified available
- [x] `scripts/import_ecoinvent.py` — credentialed ecoinvent 3.10 import helper (guards missing creds)
- [x] `docs/using_your_databases.md` — format reality + 3 real paths (ecoinvent creds / stay in openLCA / free data)
- [x] SETUP.md + README linked to the databases doc
- [x] Local openLCA JSON-LD **LCIA packs** ARE importable — `scripts/import_openlca_lcia.py` (patches 3 bw2io strategy bugs); verified: ecoinvent 3.10 pack → 614 methods / 170k CFs, imported EF v3.0 GWP100 computes correctly (2.925 kg CO₂-eq on tutorial widget)
- [x] Confirmed `.zolca` files are Derby DB (unreadable by Brightway); older LCIA packs (3.9.1/3.6) have extra quirks — 3.10 pack is the validated one
- [ ] Run `scripts/import_ecoinvent.py` with your ecoinvent login to load the ecoinvent *inventory* (LCI) — user action, needs credentials (LCIA methods already available locally via the pack above)

## Verification

- [x] All 11 tutorial notebooks execute headlessly, outputs embedded, 0 errors
- [x] All 3 case-study notebooks execute headlessly, outputs embedded, 0 errors
- [x] Tutorial 01 & 03 numbers match hand matrix calculation (to float32 precision)
- [x] MCP pytest suite green (13/13 passed)
- [x] MCP end-to-end smoke test (demo.py: search → build → run_lca → contribution → dispose)
- [x] Read-only mode verified to block writes (test_read_only_blocks_writes)
- [x] 14 result figures (.png) generated across tutorials + case studies
