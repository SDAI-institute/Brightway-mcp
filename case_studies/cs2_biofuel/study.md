# Case Study 2 — Corn-Ethanol Biofuel Pathway

**Notebook:** [study.ipynb](study.ipynb) · **Data:** [data/ethanol_parameters.csv](data/ethanol_parameters.csv)

A parameterized bioprocess LCA comparing corn-ethanol against a fossil-gasoline
reference on an **energy-equivalent** basis, with co-product handling
(DDGS substitution) and Monte Carlo. Connects to the SDAI **Biosteam++** work:
the foreground parameters (yields, energy demands) are exactly the outputs a
process simulator produces, so this notebook doubles as a template for feeding
Biosteam mass/energy balances into Brightway.

## 1. Goal & Scope

- **Goal:** estimate the cradle-to-gate GWP of 1 MJ of corn-ethanol fuel and
  compare it to fossil gasoline, quantifying the effect of co-product
  allocation and parameter uncertainty.
- **Functional unit:** **1 MJ of fuel energy** (LHV basis). Comparing per-kg
  would be misleading — ethanol's energy density (26.8 MJ/kg) is far below
  gasoline's (43.4 MJ/kg). Energy-equivalence is the honest basis.
- **System boundary:** corn cultivation → milling → fermentation → distillation
  (process heat + electricity). End-of-life combustion CO₂ is **biogenic**
  (excluded from fossil GWP, the standard convention). Fossil reference is a
  well-to-tank gasoline value.
- **Co-product:** DDGS (distillers' grains, animal feed) handled by
  **substitution** (system expansion): credit the avoided burden of the
  soybean-meal feed it displaces. Allocation alternatives discussed.
- **Method:** IPCC 2013 GWP100.

## 2. Life Cycle Inventory

All foreground numbers live in `ethanol_parameters.csv` with distributions —
this is the parameter table a bioprocess engineer hands over. Per kg ethanol:

- corn feedstock = 1 / `corn_yield` kg, at `corn_ci` (cultivation: N₂O + diesel)
- process heat `process_heat` MJ at `heat_ci` (natural-gas boiler)
- electricity `elec_use` kWh at `grid_ci`
- **minus** DDGS credit: `ddgs_credit` kg × `ddgs_ci_avoided` (avoided feed)

The notebook builds this as a Brightway foreground where the DDGS credit is a
**negative technosphere/biosphere contribution** (substitution), then converts
per-kg to per-MJ via the LHV.

## 3. Life Cycle Impact Assessment

Reported per MJ:

- ethanol **without** co-product credit (attributional, no allocation)
- ethanol **with** DDGS substitution credit
- fossil gasoline reference

The gap between the first two shows how much the result depends on co-product
methodology — often the single biggest lever in biofuel LCAs, and a frequent
source of dispute in the literature.

## 4. Interpretation

- **Contribution analysis:** splits ethanol's GWP among cultivation, process
  heat, and electricity — usually cultivation (N₂O) and distillation heat
  dominate.
- **Monte Carlo:** propagates the CSV distributions (shared grid/heat
  uncertainty) to a distribution of per-MJ GWP and of the **ethanol-vs-gasoline
  savings**, yielding P(ethanol < gasoline).
- **Sensitivity:** a tornado over yield, corn CI, heat demand, and the DDGS
  credit shows which parameter most needs better data.
- **Caveats:** excludes land-use change (potentially decisive for biofuels —
  flagged, not modeled here); results are illustrative teaching values.

## Biosteam++ hook

The `load_parameters()` function reads the CSV into a dict. To drive the study
from a Biosteam simulation instead, replace that dict with the simulator's
computed yields and utility demands — the rest of the notebook is unchanged.

## Reproduce

Open `study.ipynb` with **Python (brightway25)** and run all. Offline, seconds.
