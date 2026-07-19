# Tutorial 00 — Setup & Environment

**Companion notebook:** [00_setup_environment.ipynb](00_setup_environment.ipynb)

## What Brightway is (and is not)

[Brightway](https://docs.brightway.dev) is an **open-source Python framework for
Life Cycle Assessment**. Unlike GUI tools (openLCA, SimaPro, GaBi), Brightway is a
library: you build, calculate, and analyze LCA models *in code*. That makes it
ideal for:

- **System analysis** — parameterized models, scenario sweeps, sensitivity studies
- **Reproducible science** — every number traceable to a script
- **Automation & agents** — exactly why we wrap it in an MCP server later
- **Scale** — thousands of Monte Carlo iterations or functional units in minutes

If you want a GUI on top of Brightway, use the
[Activity Browser](https://github.com/LCA-ActivityBrowser/activity-browser).

## Brightway2 vs Brightway 2.5 — naming, quickly

| Name | Packages | Status |
|------|----------|--------|
| **Brightway2 (legacy)** | `bw2data 3.x`, `bw2calc 1.x` | maintenance mode |
| **Brightway 2.5** (this hub) | `bw2data ≥ 4`, `bw2calc ≥ 2`, `bw_processing`, `matrix_utils` | active development |

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

This repo ships a dedicated virtual environment — see [SETUP.md](../SETUP.md).
The short version:

```powershell
cd "D:\01code\Projects\SDAI- Ecosystem\Brightway2"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m ipykernel install --user --name brightway25 --display-name "Python (brightway25)"
```

Open the notebooks with the **Python (brightway25)** kernel.

## Where Brightway keeps data

Brightway stores everything (SQLite databases, processed arrays) in a per-user
data directory, organized into **projects**. On Windows it's typically
`%LOCALAPPDATA%\pylca\Brightway3\`. You never edit these files directly; the
notebook shows how to inspect the location with `bd.projects`.

Key mental model: **a project is a completely isolated workspace.** Databases,
methods, and parameters in one project are invisible to others. We use:

- `bw25-tutorials` — shared by tutorial notebooks
- one project per case study (`cs1-bottle`, `cs2-biofuel`, `cs3-cement`)

## Biosphere & LCIA methods: `bw2setup()`

`bw2io.bw2setup()` installs, into the *current project*:

1. **`biosphere3`** — the standard database of elementary flows (~4,700 flows:
   emissions to air/water/soil, resource extractions), using ecoinvent's
   nomenclature (but free — it's just names/categories, no inventory data)
2. **LCIA methods** — hundreds of ready characterization methods (IPCC GWP,
   ReCiPe, EF 3.1, USEtox, …) as lists of (flow, characterization factor) pairs

This is bundled with `bw2io` — no license needed. Run it once per project;
it detects and skips if already installed.

> **Important (this repo):** on the installed stack (bw2data 4.7 + bw2io 0.9.17)
> the classic `bw2io.bw2setup()` currently errors while writing methods. We use
> the officially-recommended remote prepared project instead:
> `bw2io.remote.install_project("ecoinvent-3.10-biosphere", "bw25-tutorials")`.
> It ships the elementary flows **and** LCIA methods, free of any ecoinvent
> license. One consequence: the biosphere database is named
> **`ecoinvent-3.10-biosphere`**, not `biosphere3`. Resolve it dynamically —
> the notebook defines `BIOSPHERE = next(d for d in bd.databases if "biosphere"
> in d.lower())` and uses that everywhere. See [SETUP.md](../SETUP.md).

## What the notebook does

1. Imports the stack and prints versions
2. Shows the data directory and lists existing projects
3. Creates/activates the `bw25-tutorials` project
4. Runs `bw2setup()` (biosphere + methods)
5. Sanity-checks: counts biosphere flows, lists a few methods, runs a trivial query

## Common pitfalls

- **Wrong kernel** → `ModuleNotFoundError: bw2data`. Select *Python (brightway25)*.
- **Forgetting `set_current`** → you silently write into the `default` project.
  Always start notebooks with `bd.projects.set_current(...)`.
- **Mixing legacy and 2.5 environments** — bw2data 3.x and 4.x use different
  project formats. Keep them in separate virtualenvs (bw2data 4 can migrate legacy
  projects, but don't point both at the same data directory casually).

## Next

→ [01 — Ecosystem & LCA math](01_ecosystem_and_lca_math.md): how those
projects/databases/activities map onto the matrix algebra of LCA.
