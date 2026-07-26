# Brightway2 Learning Hub

A self-contained tutorial set, case-study collection, and MCP server for the
[Brightway](https://docs.brightway.dev) LCA framework (targeting **Brightway 2.5**:
`bw2data â‰¥ 4`, `bw2calc â‰¥ 2`), built for system-analysis LCA studies and for
integration into the SDAI **LCA copilot**.

Progress is tracked in [CHECKLIST.md](CHECKLIST.md). Environment setup lives in
[SETUP.md](SETUP.md).

## Learning path

Every tutorial is a **pair**: an `NN_topic.md` explainer (theory, API notes,
pitfalls) and an `NN_topic.ipynb` executable demo. Read the `.md`, then run the
notebook. All notebooks run on **free data** â€” no ecoinvent license required
(ecoinvent import is covered as an optional path in tutorial 04 and SETUP.md).

### Core (tutorials/)

| # | Topic | You learn toâ€¦ |
|---|-------|----------------|
| 00 | Setup & environment | install the stack, create a project, set up the biosphere |
| 01 | Ecosystem & LCA math | how projects/databases/activities/exchanges map to the A & B matrices |
| 02 | Projects & data management | manage projects and databases with bw2data |
| 03 | Foreground inventories in code | build a linked inventory and verify it against a hand calculation |
| 04 | Importing data (bw2io) | Excel importer workflow, strategies; optional ecoinvent import |
| 05 | LCIA with bw2calc | run LCA calculations, single & multi-method / multi-FU |

### Advanced

| # | Topic | You learn toâ€¦ |
|---|-------|----------------|
