# Brightway vs openLCA — When to Use Which

The SDAI ecosystem has both a Brightway stack (this repo) and an
[`openlca_mcp`](../../openlca_mcp) server. They solve the same LCA math; they
differ in interface and workflow.

| | **Brightway 2.5** | **openLCA** |
|-|-------------------|-------------|
| Nature | Python library | Desktop application (+ IPC/gRPC server) |
| Interface | code (notebooks, scripts) | GUI, or `olca-ipc` over a running instance |
| Automation | native — it *is* Python | via the IPC server (openlca-ipc) |
| Data model | projects → databases → activities → exchanges | databases → processes → flows → exchanges |
| Matrices | directly accessible (`lca.technosphere_matrix`) | computed internally, less exposed |
| Uncertainty | `stats_arrays` + `use_distributions` | built-in Monte Carlo |
| Parameters | code formulas + `bw2data.parameters` | GUI global/process parameters |
| Databases | ecoinvent, USEEIO, Forwast, ecospold/SimaPro import | ecoinvent, ELCD, GaBi import, Nexus |
| Scenarios | datapackages, `premise` | product-system variants |
| Best for | system analysis, batch studies, ML pipelines, reproducible science | interactive modeling, review, teaching non-coders, regulated EPDs |
| MCP server | `brightway_mcp` (this repo) | `openlca_mcp` |

## Rules of thumb

- **Choose Brightway** when the study is *computational*: thousands of scenarios
  or Monte Carlo runs, parameter sweeps, coupling to a process simulator
  (Biosteam), custom LCIA methods, or anything that must be scripted and version-
  controlled. Also when you want matrix-level access.
- **Choose openLCA** when the work is *interactive*: building/curating a model by
  hand, visual review with stakeholders, using databases distributed in openLCA
  format, or producing EPDs with a validated GUI trail.

## They interoperate

- Both read/write **Excel** and can exchange inventories via it.
- Both consume **ecoinvent** (same underlying data, different importers).
- SimaPro CSV and ecospold flow between them via `bw2io` importers.
- In the SDAI copilot, the two MCP servers expose deliberately parallel tools
  (ISO-phase organization, structured envelopes, read-only mode, result-id
  registry) so an agent can target either backend with the same mental model.

## In this ecosystem

- `Brightway2/` (this repo) — Brightway tutorials, case studies, MCP.
- `openlca_mcp/` — openLCA MCP server + case studies.
- `LCA copilot/` — the multi-agent system that orchestrates both, with
  package-specific skills under `skills/` (`brightway2`, `openlca-ipc`, `greet`).
