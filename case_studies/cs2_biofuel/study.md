# Case Study 2 â€” Corn-Ethanol Biofuel Pathway

**Notebook:** [study.ipynb](study.ipynb) Â· **Data:** [data/ethanol_parameters.csv](data/ethanol_parameters.csv)

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
  would be misleading â€” ethanol's energy density (26.8 MJ/kg) is far below
  gasoline's (43.4 MJ/kg). Energy-equivalence is the honest basis.
- **System boundary:** corn cultivation â†’ milling â†’ fermentation â†’ distillation
  (process heat + electricity). End-of-life combustion COâ‚‚ is **biogenic**
  (excluded from fossil GWP, the standard convention). Fossil reference is a
  well-to-tank gasoline value.
- **Co-product:** DDGS (distillers' grains, animal feed) handled by
  **substitution** (system expansion): credit the avoided burden of the
  soybean-meal feed it displaces. Allocation alternatives discussed.
- **Method:** IPCC 2013 GWP100.

## 2. Life Cycle Inventory

