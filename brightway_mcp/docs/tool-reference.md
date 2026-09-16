# Brightway MCP Tool Reference

Reviewed package: `brightway-mcp` 0.1.0. The current FastMCP server exposes **22 tools** organized around setup/goal-and-scope, inventory, impact assessment, and interpretation.

## Setup / goal and scope — 8 tools

| Tool | Purpose |
|---|---|
| `health_check` | Report Brightway package versions and environment state. |
| `list_projects` | List Brightway projects available on the machine. |
| `list_databases` | List databases and activity counts for a selected project. |
| `database_stats` | Inspect activity and exchange counts for one database. |
| `search_activities` | Search activity names inside a database. |
| `search_biosphere` | Search elementary flows, optionally by compartment/category. |
| `get_activity` | Inspect one activity and its complete exchange list. |
| `list_methods` | List/filter LCIA methods and units. |

## Inventory / project writes — 5 tools

| Tool | Purpose |
|---|---|
| `setup_project` | Install a prepared free biosphere + LCIA method project when needed. |
| `create_database` | Create or replace a foreground database. |
| `write_activities` | Bulk-write foreground activities and exchanges. |
| `set_uncertainty` | Attach supported uncertainty distributions to non-production exchanges. |
| `import_lcia_methods` | Import an openLCA JSON-LD LCIA method pack into the project. |

These operations mutate Brightway data and are blocked by `BRIGHTWAY_READ_ONLY=true`.

## Impact assessment — 4 tools

| Tool | Purpose |
|---|---|
| `run_lca` | Run one activity/method calculation and store the solved LCA under a `result_id`. |
| `run_multi_method` | Score one activity against multiple LCIA methods efficiently. |
| `compare_activities` | Produce a comparative alternatives × methods result grid. |
| `run_monte_carlo` | Propagate stored exchange uncertainties with optional reproducible seed. |

## Interpretation — 5 tools

| Tool | Purpose |
|---|---|
| `contribution_analysis` | Return top contributing processes for a stored result. |
| `top_emissions` | Return top elementary-flow contributions for a stored result. |
| `supply_chain` | Build a bounded recursive supply-chain contribution tree. |
| `export_result` | Write a process-contribution table to CSV. |
| `dispose_result` | Drop a stored solved LCA from the result registry. |

## Result workflow

`run_lca` stores a solved `LCA` object and returns a `result_id`. Use the same result for `contribution_analysis` and `top_emissions`, then call `dispose_result` when finished.

## Project targeting

Most tools require a `project` argument. Treat the selected Brightway project as part of the study identity and record it with every result. Switching projects can change database content, methods, and activity keys even when names appear similar.

## Read-only operation

Set:

```text
BRIGHTWAY_READ_ONLY=true
```

to block `setup_project`, `create_database`, `write_activities`, `set_uncertainty`, `import_lcia_methods`, and `export_result`. Calculation and inspection calls remain available.

## Review boundary

Typed tool inputs reduce malformed calls but do not establish that an activity, database, method, uncertainty distribution, functional unit, or interpretation is scientifically appropriate. Those decisions remain part of the LCA review process.