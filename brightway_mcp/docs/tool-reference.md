# Brightway MCP Tool Reference

Reviewed package: `brightway-mcp` 0.3.0. The current FastMCP server exposes **33 tools**: 22 core LCA tools, 6 explicit background-job variants for long-running operations, and 5 job-lifecycle tools.

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

## Background-job variants — 6 tools

| Tool | Purpose |
|---|---|
| `setup_project_async` | Start project bootstrap as a background job. |
| `import_lcia_methods_async` | Import an LCIA pack without holding one MCP request open. |
| `run_multi_method_async` | Run a multi-method calculation as a background job. |
| `run_monte_carlo_async` | Run Monte Carlo analysis as a background job. |
| `compare_activities_async` | Run an alternatives × methods comparison as a background job. |
| `supply_chain_async` | Build a supply-chain contribution tree as a background job. |

When `BRIGHTWAY_NATIVE_TASKS_ENABLED=true` and the client supports MCP Tasks, the corresponding long-running core tools can also use native task behavior. The explicit `*_async` tools remain available for clients that do not support MCP Tasks.

## Job lifecycle — 5 tools

| Tool | Purpose |
|---|---|
| `get_job_status` | Poll a background job until `terminal=true`. |
| `get_job_result` | Retrieve the result of a completed job, with optional paging for large lists. |
| `list_jobs` | List recent background jobs. |
| `cancel_job` | Cancel a queued job when cancellation is still safe. |
| `dispose_job` | Remove a terminal job and its stored result from the job registry. |

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