# Wiring Brightway into the LCA Copilot

How this hub plugs into the SDAI **LCA copilot** (`../../LCA copilot`). This is a
reference/plan — it does **not** modify the copilot repo. Apply the steps there
when ready.

## What already exists in the copilot

- `LCA copilot/skills/brightway2/` — a skill (`skill.json` + `SKILL.md`) already
  registered. Its `skill.json` schema (loaded by
  `lca_multiagent/skills.py::SkillRegistry.from_directory`) is:
  ```json
  {
    "name": "brightway2",
    "summary": "...",
    "packages": ["brightway2", "bw2data", "bw2calc", "bw2io"],
    "preferred_phases": ["life_cycle_inventory", "life_cycle_impact_assessment", "interpretation"],
    "toolchain": ["Brightway2 project setup", "biosphere/database imports", "bw2calc LCA"],
    "when_to_use": "...",
    "instructions_file": "SKILL.md"
  }
  ```
- The orchestrator runs four ISO-phase subagents sequentially; each phase selects
  skills via `SkillRegistry.select_for_phase` (by phase preference + the study's
  `package_preferences`).

## Two integration paths

### Path A — knowledge (update `SKILL.md`)

Point the copilot's brightway2 `SKILL.md` at this hub's validated patterns so the
phase agents generate correct 2.5 code. The highest-value things to fold in
(all learned/verified while building this hub):

- Biosphere setup via `bw2io.remote.install_project("ecoinvent-3.10-biosphere", …)`
  (the classic `bw2setup()` is broken on bw2data 4.7 / bw2io 0.9.17).
- Resolve the biosphere DB name dynamically (`ecoinvent-3.10-biosphere`, not `biosphere3`).
- The Excel-import `type: process` requirement and hash-code lookup-by-name.
- `lcia(demand={act.id: 1})` (not the object) and `switch_method` for multi-calc.
- float32 tolerance (~1e-5) for hand-vs-Brightway checks.

Link the tutorials/case studies as canonical examples the agent can cite.

### Path B — tools (register `brightway_mcp`)

Give the copilot *executable* Brightway tools via the MCP server in this repo.
The `brightway_mcp` tools are already organized by the copilot's four ISO phases,
which maps cleanly onto the phase subagents:

| Copilot phase | brightway_mcp tools |
|---------------|---------------------|
| Goal & Scope | `list_projects`, `list_databases`, `search_activities`, `list_methods` |
| Life Cycle Inventory | `create_database`, `write_activities`, `database_stats` |
| Life Cycle Impact Assessment | `run_lca`, `run_multi_method`, `run_monte_carlo` |
| Interpretation | `contribution_analysis`, `top_emissions`, `dispose_result` |

Register it wherever the copilot configures MCP servers (mirror how
`openlca_mcp` is wired), e.g. an `.mcp.json` entry:

```json
{
  "mcpServers": {
    "brightway": {
      "command": "python",
      "args": ["-m", "brightway_mcp.server"],
      "env": { "BRIGHTWAY_READ_ONLY": "false" }
    }
  }
}
```

The tools share `openlca_mcp`'s envelope conventions (`success`, `error_code`,
`recoverable`, `suggested_next_actions`, `result_id`), so any agent logic that
already branches on openLCA tool results works unchanged against Brightway.

## Recommended rollout

1. **Path A first** — update `SKILL.md` with the verified 2.5 patterns; zero new
   infrastructure, immediately improves generated code.
2. **Path B next** — register `brightway_mcp` for the phases that benefit most
   from real execution (LCI build + LCIA + interpretation), keeping
   `BRIGHTWAY_READ_ONLY=true` in any phase that should not mutate data.
3. Set the study's `package_preferences` to include `brightway2` so the
   registry selects it for the inventory/impact/interpretation phases.

## Safety note for autonomous use

Run the inventory phase with writes enabled but goal-scope/interpretation with
`BRIGHTWAY_READ_ONLY=true`, so an agent can freely explore and interpret without
risk of mutating databases. The `dispose_result` tool should be called at the end
of each interpretation phase to keep the result registry clean across a long run.
