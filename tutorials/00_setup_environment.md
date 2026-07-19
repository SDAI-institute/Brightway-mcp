# Tutorial 00 â€” Setup & Environment

**Companion notebook:** [00_setup_environment.ipynb](00_setup_environment.ipynb)

## What Brightway is (and is not)

[Brightway](https://docs.brightway.dev) is an **open-source Python framework for
Life Cycle Assessment**. Unlike GUI tools (openLCA, SimaPro, GaBi), Brightway is a
library: you build, calculate, and analyze LCA models *in code*. That makes it
ideal for:

- **System analysis** â€” parameterized models, scenario sweeps, sensitivity studies
- **Reproducible science** â€” every number traceable to a script
- **Automation & agents** â€” exactly why we wrap it in an MCP server later
- **Scale** â€” thousands of Monte Carlo iterations or functional units in minutes

If you want a GUI on top of Brightway, use the
[Activity Browser](https://github.com/LCA-ActivityBrowser/activity-browser).

## Brightway2 vs Brightway 2.5 â€” naming, quickly

| Name | Packages | Status |
|------|----------|--------|
| **Brightway2 (legacy)** | `bw2data 3.x`, `bw2calc 1.x` | maintenance mode |
| **Brightway 2.5** (this hub) | `bw2data â‰¥ 4`, `bw2calc â‰¥ 2`, `bw_processing`, `matrix_utils` | active development |

The *concepts* are identical. 2.5 rebuilt the calculation layer around
**datapackages** (portable bundles of matrix data), which enables scenarios,
remote calculation, and cleaner uncertainty handling. Where the APIs diverge,
these tutorials flag it with a **"Legacy note"**; a full migration table is in
[docs/legacy_vs_25.md](../docs/legacy_vs_25.md).

## The package family

| Package | Role |
|---------|------|
| `bw2data` | storage & metadata: projects, databases, activities, exchanges, methods, parameters |
| `bw2calc` | the calculator: builds matrices, solves the LCA system, Monte Carlo |
| `bw2io` | import/export: Excel, ecospold, SimaPro CSV, ecoinvent, remote data |
| `bw2analyzer` | interpretation: contribution analysis, comparisons, supply-chain exploration |
| `bw_processing` | writes datapackages (the 2.5 matrix storage format) |
| `matrix_utils` | assembles matrices from datapackages |
| `stats_arrays` | uncertainty distribution definitions |

You mostly touch the first four; the rest work behind the scenes.

## Installation (already done for this repo)
