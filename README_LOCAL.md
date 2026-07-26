# Brightway2 Learning Hub

A self-contained tutorial set, case-study collection, and MCP server for the
[Brightway](https://docs.brightway.dev) LCA framework (targeting **Brightway 2.5**:
`bw2data ≥ 4`, `bw2calc ≥ 2`), built for system-analysis LCA studies and for
integration into the SDAI **LCA copilot**.

Progress is tracked in [CHECKLIST.md](CHECKLIST.md). Environment setup lives in
[SETUP.md](SETUP.md).

## Learning path

Every tutorial is a **pair**: an `NN_topic.md` explainer (theory, API notes,
pitfalls) and an `NN_topic.ipynb` executable demo. Read the `.md`, then run the
notebook. All notebooks run on **free data** — no ecoinvent license required
(ecoinvent import is covered as an optional path in tutorial 04 and SETUP.md).

### Core (tutorials/)

| # | Topic | You learn to… |
|---|-------|----------------|
| 00 | Setup & environment | install the stack, create a project, set up the biosphere |
| 01 | Ecosystem & LCA math | how projects/databases/activities/exchanges map to the A & B matrices |
| 02 | Projects & data management | manage projects and databases with bw2data |
| 03 | Foreground inventories in code | build a linked inventory and verify it against a hand calculation |
| 04 | Importing data (bw2io) | Excel importer workflow, strategies; optional ecoinvent import |
| 05 | LCIA with bw2calc | run LCA calculations, single & multi-method / multi-FU |

### Advanced

| # | Topic | You learn to… |
|---|-------|----------------|
| 06 | Contribution analysis | find hotspot processes and emissions, traverse the supply chain |
| 07 | Uncertainty & Monte Carlo | attach distributions, run MC, compare alternatives statistically |
| 08 | Parameters & scenarios | parameterize inventories and run scenario sets |
| 09 | Comparative LCA & visualization | build comparison dashboards and report-ready plots |
| 10 | Advanced internals | matrix access, custom LCIA methods, graph traversal, legacy-vs-2.5 |

### Case studies (case_studies/)

ISO 14040/44-structured worked studies (goal & scope → LCI → LCIA → interpretation):

1. **cs1_product_lca** — reusable vs single-use bottle; EoL scenarios, break-even analysis
2. **cs2_biofuel** — corn-ethanol-style pathway; parameterized foreground, Monte Carlo vs fossil reference
3. **cs3_industrial** — cement clinker; alternative fuels & electricity-mix scenarios, sensitivity

### MCP server (brightway_mcp/)

A [FastMCP](https://gofastmcp.com) server exposing Brightway as agent tools,
organized by ISO LCA phase (mirroring the sibling `openlca_mcp` conventions):
goal & scope · inventory · impact assessment · interpretation. See
[brightway_mcp/README.md](brightway_mcp/README.md).

### Reference docs (docs/)

| Doc | What it covers |
|-----|----------------|
| [cheatsheet.md](docs/cheatsheet.md) | one-page Brightway 2.5 API reference |
| [glossary.md](docs/glossary.md) | LCA + Brightway terms |
| [bw_vs_openlca.md](docs/bw_vs_openlca.md) | Brightway vs openLCA — when to use which |
| [legacy_vs_25.md](docs/legacy_vs_25.md) | legacy Brightway2 → 2.5 migration table |
| [using_your_databases.md](docs/using_your_databases.md) | how (and whether) the files in `SDAI- Ecosystem\databases\` work with Brightway |
| [copilot_integration.md](docs/copilot_integration.md) | wiring this hub into the LCA copilot |

### Scripts (scripts/)

Helper scripts for loading your **local** licensed data — see
[scripts/README.md](scripts/README.md):
- `import_openlca_lcia.py` — import a local openLCA JSON-LD **LCIA pack**
  (verified: 614 ecoinvent 3.10 methods), no download needed.
- `import_ecoinvent.py` — download the ecoinvent **inventory** via your
  ecoinvent login (credentialed).

## Quick start

```powershell
cd "D:\01code\Projects\SDAI- Ecosystem\Brightway2"
.\.venv\Scripts\Activate.ps1
jupyter lab tutorials/
```
