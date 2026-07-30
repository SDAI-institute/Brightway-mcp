# Wiring Brightway into the LCA Copilot

How this hub plugs into the SDAI **LCA copilot** (`../../LCA copilot`). This is a
reference/plan â€” it does **not** modify the copilot repo. Apply the steps there
when ready.

## What already exists in the copilot

- `LCA copilot/skills/brightway2/` â€” a skill (`skill.json` + `SKILL.md`) already
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

### Path A â€” knowledge (update `SKILL.md`)

Point the copilot's brightway2 `SKILL.md` at this hub's validated patterns so the
phase agents generate correct 2.5 code. The highest-value things to fold in
(all learned/verified while building this hub):

- Biosphere setup via `bw2io.remote.install_project("ecoinvent-3.10-biosphere", â€¦)`
  (the classic `bw2setup()` is broken on bw2data 4.7 / bw2io 0.9.17).
