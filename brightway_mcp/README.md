# Brightway MCP Server

A [FastMCP](https://gofastmcp.com) server that exposes **Brightway 2.5** LCA as
tools for AI agents, organized by the four ISO 14040/44 phases. It mirrors the
conventions of the sibling [`openlca_mcp`](../../openlca_mcp) server so the two
feel identical to an agent (structured envelopes, read-only mode, result-id
registry, per-call target selection).

## Tool surface

| Phase | Tools |
|-------|-------|
| **Setup / Goal & Scope** (read) | `health_check`, `list_projects`, `list_databases`, `database_stats`, `search_activities`, `search_biosphere`, `get_activity`, `list_methods` |
| **Inventory** (write) | `setup_project`, `create_database`, `write_activities`, `set_uncertainty`, `import_lcia_methods` |
| **Impact** (read) | `run_lca`, `run_multi_method`, `compare_activities`, `run_monte_carlo` |
| **Interpretation** (read/write) | `contribution_analysis`, `top_emissions`, `supply_chain`, `export_result`, `dispose_result` |

The 22 core tools are joined by six explicit background-job variants for long-running operations (`setup_project_async`, `import_lcia_methods_async`, `run_multi_method_async`, `run_monte_carlo_async`, `compare_activities_async`, `supply_chain_async`) and five job-lifecycle tools (`get_job_status`, `get_job_result`, `list_jobs`, `cancel_job`, `dispose_job`). The current server therefore exposes **33 tools** in total.

Highlights beyond the basics:
- **`setup_project`** — bootstrap a fresh project with a free biosphere + LCIA
  methods (remote prepared project); the usual first write on a new machine.
- **`search_biosphere`** — discover the exact elementary-flow name to link an
  emission in `write_activities`.
- **`set_uncertainty`** + **`run_monte_carlo`** — attach lognormal/normal/
  uniform/triangular distributions, then propagate them; pass `seed` to reproduce the same Monte Carlo draw sequence.
- **`compare_activities`** — the comparative-study grid (several activities ×
  several methods) in one call.
- **`supply_chain`** — bounded recursive contribution tree.
- **`import_lcia_methods`** — import a local openLCA JSON-LD LCIA pack
  (e.g. an ecoinvent LCIA zip), patching the bw2io quirks these packs trip.
- **`export_result`** — dump a result's contribution table to CSV.

Plus resources `brightway://projects`, `brightway://methods/{project}` and a
guided `lca_walkthrough` prompt.

## Design conventions (shared with openlca_mcp)

- **Structured envelopes** — every tool returns `{"success": bool, ...}`; errors
  add `error_code`, `recoverable`, and `suggested_next_actions` so an agent can
  branch programmatically. See [responses.py](src/brightway_mcp/responses.py).
- **Result registry** — `run_lca` returns a `result_id`; interpretation tools
  operate on the stored solved `LCA` without recomputing. See
  [result_store.py](src/brightway_mcp/result_store.py).
- **Read-only mode** — set `BRIGHTWAY_READ_ONLY=true` to block every write tool
  (`setup_project`, `create_database`, `write_activities`, `set_uncertainty`,
  `import_lcia_methods`, `export_result`).
- **MCP safety annotations** — read tools advertise `readOnlyHint=true`; mutation tools
  advertise `readOnlyHint=false`; `dispose_result` additionally advertises
  `destructiveHint=true`. Clients should still enforce their own permission policy.
- **Project = target** — a Brightway *project* is the analogue of an openLCA
  connection profile; every tool takes a `project` argument.

## Install & run

```bash
cd brightway_mcp
pip install -e .
# stdio (for Claude Desktop / Claude Code)
python -m brightway_mcp.server
# streamable-HTTP on :8000
python -m brightway_mcp.server --http
```

The server operates on whatever Brightway projects exist on the machine. To get
a free biosphere + methods into a project (no ecoinvent license needed):

```python
import bw2io as bi
bi.remote.install_project("ecoinvent-3.10-biosphere", "my-project")
```

## Documentation

- [Quick start](docs/quickstart.md)
- [Client configuration](docs/client-configuration.md)
- [Tool reference](docs/tool-reference.md)
- [Validation scope](docs/validation.md)
- [Reliability record](RELIABILITY.md)

## Full tool reference

Every tool takes `project` (except `health_check` / `list_projects`) and returns
`{"success": bool, ...}`. `W` = write (blocked by `BRIGHTWAY_READ_ONLY`).

| Tool | Args (besides `project`) | Returns |
|------|--------------------------|---------|
| `health_check` | — | package versions, current project |
| `list_projects` | — | all projects |
| `list_databases` | — | databases + counts, biosphere name |
| `database_stats` | `database` | activity + exchange counts |
| `search_activities` | `database`, `query`, `limit=10` | matching activities |
| `search_biosphere` | `query`, `limit=10`, `categories=None` | matching elementary flows |
| `get_activity` | `database`, `code`\|`name` | one activity's full exchange list |
| `list_methods` | `filter=None`, `limit=50` | LCIA methods (+ units) |
| `setup_project` `W` | `source="ecoinvent-3.10-biosphere"`, `overwrite=False` | installs biosphere+methods |
| `create_database` `W` | `name`, `overwrite=False` | creates empty db |
| `write_activities` `W` | `database`, `activities[]` | writes foreground |
| `set_uncertainty` `W` | `database`, `code`\|`name`, `scale=0.15`, `distribution="lognormal"`, `input_filter=None` | exchanges updated |
| `import_lcia_methods` `W` | `zip_path`, `drop_unlinked=True` | methods added (openLCA JSON-LD LCIA pack) |
| `run_lca` | `database`, `method`, `code`\|`name`, `amount=1.0` | score + `result_id` |
| `run_multi_method` | `database`, `methods[]`, `code`\|`name`, `amount=1.0` | score per method |
| `compare_activities` | `alternatives[]`, `methods[]` | comparative grid rows |
| `run_monte_carlo` | `database`, `method`, `code`\|`name`, `iterations=500`, `seed=None` | mean/std/median + 5/95 percentiles; optional reproducible RNG seed |
| `contribution_analysis` | `result_id`, `limit=10` | top processes |
| `top_emissions` | `result_id`, `limit=10` | top elementary flows |
| `supply_chain` | `database`, `method`, `code`\|`name`, `max_level=3`, `cutoff=0.02` | recursive contribution tree |
| `export_result` `W` | `result_id`, `path`, `limit=25` | writes CSV |
| `dispose_result` | `result_id` | drops stored result |

For `write_activities`, each activity is
`{code, name, unit, exchanges:[{input, amount, type, [categories]}]}` where
`input` is `[database, code]` (technosphere), a bare code (internal), or a flow
name when `type="biosphere"`. For `compare_activities`, each alternative is
`{database, code|name, [label]}`.

## Register with a client

See [examples/mcp.json](examples/mcp.json) (Claude Code / `.mcp.json`) and
[examples/claude_desktop_config.json](examples/claude_desktop_config.json).
A no-server demo driving the tools in-process is in
[examples/demo.py](examples/demo.py).

## Tests

```bash
pip install -e ".[dev]"
pytest
```

Tests run against a throwaway project with a tiny fixture database (3 biosphere
flows, a 3-process foreground, a hand GWP method) in a temp `BRIGHTWAY_DIR` — no
downloads, no touching your real projects. They cover the full
search→build→calculate→contribution chain, the read-only guard, and error
envelopes.

## Integration with LCA copilot

See [../docs/copilot_integration.md](../docs/copilot_integration.md) for wiring
this server into the SDAI LCA copilot's `skills/` and ISO-phase agent specs.
