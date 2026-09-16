# Brightway MCP Tool Reference

Reviewed package: `brightway-mcp` 0.1.0. The current FastMCP server exposes **22 tools** organized around setup/goal-and-scope, inventory, impact assessment, and interpretation.

## Setup / goal and scope â€” 8 tools

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

## Inventory / project writes â€” 5 tools

| Tool | Purpose |
|---|---|
| `setup_project` | Install a prepared free biosphere + LCIA method project when needed. |
| `create_database` | Create or replace a foreground database. |
| `write_activities` | Bulk-write foreground activities and exchanges. |
| `set_uncertainty` | Attach supported uncertainty distributions to non-production exchanges. |
| `import_lcia_methods` | Import an openLCA JSON-LD LCIA method pack into the project. |

These operations mutate Brightway data and are blocked by `BRIGHTWAY_READ_ONLY=true`.
