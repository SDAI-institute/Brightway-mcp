# Brightway MCP Server

A [FastMCP](https://gofastmcp.com) server that exposes **Brightway 2.5** LCA as
tools for AI agents, organized by the four ISO 14040/44 phases. It mirrors the
conventions of the sibling [`openlca_mcp`](../../openlca_mcp) server so the two
feel identical to an agent (structured envelopes, read-only mode, result-id
registry, per-call target selection).

## Tools by ISO phase (22 tools)

| Phase | Tools |
|-------|-------|
| **Setup / Goal & Scope** (read) | `health_check`, `list_projects`, `list_databases`, `database_stats`, `search_activities`, `search_biosphere`, `get_activity`, `list_methods` |
| **Inventory** (write) | `setup_project`, `create_database`, `write_activities`, `set_uncertainty`, `import_lcia_methods` |
| **Impact** (read) | `run_lca`, `run_multi_method`, `compare_activities`, `run_monte_carlo` |
| **Interpretation** (read/write) | `contribution_analysis`, `top_emissions`, `supply_chain`, `export_result`, `dispose_result` |

Highlights beyond the basics:
- **`setup_project`** â€” bootstrap a fresh project with a free biosphere + LCIA
  methods (remote prepared project); the usual first write on a new machine.
- **`search_biosphere`** â€” discover the exact elementary-flow name to link an
  emission in `write_activities`.
- **`set_uncertainty`** + **`run_monte_carlo`** â€” attach lognormal/normal/
  uniform/triangular distributions, then propagate them; pass `seed` to reproduce the same Monte Carlo draw sequence.
- **`compare_activities`** â€” the comparative-study grid (several activities Ã—
  several methods) in one call.
- **`supply_chain`** â€” bounded recursive contribution tree.
- **`import_lcia_methods`** â€” import a local openLCA JSON-LD LCIA pack
  (e.g. an ecoinvent LCIA zip), patching the bw2io quirks these packs trip.
- **`export_result`** â€” dump a result's contribution table to CSV.

Plus resources `brightway://projects`, `brightway://methods/{project}` and a
guided `lca_walkthrough` prompt.

## Design conventions (shared with openlca_mcp)

- **Structured envelopes** â€” every tool returns `{"success": bool, ...}`; errors
  add `error_code`, `recoverable`, and `suggested_next_actions` so an agent can
  branch programmatically. See [responses.py](src/brightway_mcp/responses.py).
- **Result registry** â€” `run_lca` returns a `result_id`; interpretation tools
  operate on the stored solved `LCA` without recomputing. See
  [result_store.py](src/brightway_mcp/result_store.py).
- **Read-only mode** â€” set `BRIGHTWAY_READ_ONLY=true` to block every write tool
  (`setup_project`, `create_database`, `write_activities`, `set_uncertainty`,
  `import_lcia_methods`, `export_result`).
- **MCP safety annotations** â€” read tools advertise `readOnlyHint=true`; mutation tools
  advertise `readOnlyHint=false`; `dispose_result` additionally advertises
  `destructiveHint=true`. Clients should still enforce their own permission policy.
- **Project = target** â€” a Brightway *project* is the analogue of an openLCA
  connection profile; every tool takes a `project` argument.

## Install & run

```bash
cd brightway_mcp
