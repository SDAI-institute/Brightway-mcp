# Case Study 1 — Reusable vs Single-Use Drinking Bottle

**Notebook:** [study.ipynb](study.ipynb) · **Data:** [data/bottle_inventory.csv](data/bottle_inventory.csv)

A classic comparative product LCA, ISO 14040/44-structured, fully reproducible
on free data. It exercises tutorials 03 (build), 05 (LCIA), 06 (contribution),
07 (Monte Carlo), and 09 (break-even & visualization).

## 1. Goal & Scope

- **Goal:** compare the cradle-to-grave climate impact of a **single-use PET
  bottle** against a **reusable stainless-steel bottle**, and find the number of
  uses at which the reusable option becomes preferable.
- **Functional unit:** *delivering 1 litre of drinking water to a consumer, once.*
  All results are normalized per single "serving/use". The reusable bottle's
  manufacturing burden is amortized over its lifetime N; each use also incurs a
  washing burden.
- **System boundary:** raw material + manufacturing (per bottle) + use-phase
  washing (reusable only) + a simplified end-of-life. Transport and water
  treatment are excluded (identical across alternatives → cancel in comparison).
- **Impact method:** IPCC 2013 GWP100 (primary). Acidification shown as a
  secondary check where the free method set allows.
- **Background data:** hand-built foreground surrogates (free, reproducible).
  An optional cell documents swapping in ecoinvent PET/steel/grid processes.

## 2. Life Cycle Inventory

Foreground processes (see the CSV):

| Process | Key flows |
|---|---|
| `single_use_pet` | 0.20 kWh forming + 0.082 kg CO₂ (resin+forming) per bottle |
| `reusable_steel` | 4.5 kWh forming + 3.6 kg CO₂ (stainless) per bottle |
| `wash` | 0.015 kWh grid electricity per wash |
| `elec` | grid at 0.42 kg CO₂/kWh (+ SO₂) |

The reusable bottle carries a large **fixed** manufacturing burden (steel is
energy-intensive) but a small **per-use** burden (one wash). The single-use
bottle has a small per-bottle burden but pays it *every* use. This is the
canonical break-even structure.

## 3. Life Cycle Impact Assessment

The notebook computes, per use:

- single-use: `pet_per_bottle` (constant, one new bottle each time)
- reusable over N uses: `steel_manufacturing / N + wash_per_use`

and sweeps N to find the **break-even point** — the N where the two curves
cross. Below it, single-use wins (rarely-reused durable goods are not free
lunches); above it, reusable wins and keeps improving.

## 4. Interpretation

- **Contribution analysis** (tutorial 06) attributes the reusable bottle's
  impact between manufacturing and the cumulative washing energy, and shows how
  the split shifts with N and with grid carbon intensity.
- **Sensitivity/scenarios:** grid decarbonization (0.42 → 0.10 kg CO₂/kWh)
  moves the break-even point — a cleaner grid makes washing cheaper and lowers
  the reusable break-even.
- **Monte Carlo** (tutorial 07) puts a distribution on the break-even N by
  sampling manufacturing and wash-energy uncertainty under shared grid
  uncertainty, yielding P(reusable better than single-use | N uses).
- **Honest caveats:** results hinge on the assumed steel manufacturing factor
  and realistic reuse counts; the study reports the break-even as a *range*, not
  a single number, and states all assumptions.

## Reproduce

Open `study.ipynb` with the **Python (brightway25)** kernel and run all. It runs
offline in seconds and writes figures + a results CSV into this folder.
