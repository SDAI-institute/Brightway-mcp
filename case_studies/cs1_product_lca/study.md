# Case Study 1 â€” Reusable vs Single-Use Drinking Bottle

**Notebook:** [study.ipynb](study.ipynb) Â· **Data:** [data/bottle_inventory.csv](data/bottle_inventory.csv)

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
  treatment are excluded (identical across alternatives â†’ cancel in comparison).
- **Impact method:** IPCC 2013 GWP100 (primary). Acidification shown as a
  secondary check where the free method set allows.
- **Background data:** hand-built foreground surrogates (free, reproducible).
  An optional cell documents swapping in ecoinvent PET/steel/grid processes.

## 2. Life Cycle Inventory

Foreground processes (see the CSV):
