# Brightway MCP Quick Start

Use the Brightway MCP server to inspect or build a Brightway 2.5 project, run LCIA, interpret stored results, and dispose result state through typed MCP tools.

## Requirements

- Python 3.11+
- Brightway 2.5-compatible packages (`bw2data>=4`, `bw2calc>=2`, `bw2io>=0.9`)
- the `brightway-mcp` package/repository
- an existing Brightway project, or permission to bootstrap one

The reviewed package version is 0.3.0.

## 1. Install

```bash
cd Brightway2/brightway_mcp
pip install -e .
```

For development and tests:

```bash
pip install -e ".[dev]"
```

## 2. Start the server

Local stdio:

```bash
python -m brightway_mcp.server
```

Streamable HTTP on the local host:

```bash
python -m brightway_mcp.server --http
```

The installed console script is also available as:

```bash
brightway-mcp
```

## 3. Verify the environment

Start with:

```text
health_check
list_projects
```

Then choose the exact Brightway project for subsequent calls. A Brightway project is the per-call target boundary used by the MCP server.

## 4. Read-only first workflow

A safe first study path is:

```text
list_databases
→ database_stats
→ search_activities
→ get_activity
→ list_methods
→ run_lca
→ contribution_analysis / top_emissions
→ dispose_result
```

`run_lca` returns a `result_id`. Reuse that stored solved LCA for interpretation rather than recomputing it silently.

## 5. New project / foreground workflow

When writes are authorized:

```text
setup_project
→ create_database
→ search_biosphere
→ write_activities
→ get_activity
→ run_lca
```

`setup_project`, foreground writes, uncertainty assignment, method import, and file export are blocked when `BRIGHTWAY_READ_ONLY=true`.

## 6. Comparative and uncertainty work

Use `run_multi_method` when one activity must be evaluated with several methods, `compare_activities` for a comparative grid, and `run_monte_carlo` only after meaningful uncertainty distributions have been attached to the relevant exchanges.

A Monte Carlo distribution reflects the uncertainty encoded in the model. It does not independently establish source-data quality.

## 7. Preserve study context

For reproducible work record:

- Brightway project;
- database(s) and versions/source;
- activity keys;
- functional/reference amount;
- LCIA method tuple(s);
- uncertainty definitions and random seed when used;
- MCP/source revision;
- result or exported artifact identity;
- methodological limitations.

## Next

- [Tool Reference](tool-reference.md)
- [Validation Scope](validation.md)
- [Brightway MCP README](../README.md)
- [Brightway learning hub](../../README.md)
