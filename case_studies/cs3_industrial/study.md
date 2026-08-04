# Case Study 3 — Cement Clinker: Decarbonization Scenarios

**Notebook:** [study.ipynb](study.ipynb) · **Data:** [data/cement_scenarios.csv](data/cement_scenarios.csv)

An industrial-system LCA of Portland cement with three decarbonization
scenarios, exercising scenario analysis (tutorial 08), contribution analysis
(06), and sensitivity. Cement is ~8% of global CO₂ and a textbook "hard-to-abate"
system because a large share of its emissions is **process chemistry**, not
energy — which makes it a perfect teaching case for *where* interventions can and
cannot help.

## 1. Goal & Scope

- **Goal:** compare the cradle-to-gate GWP of 1 kg cement under a **baseline**
  (coal-fired kiln), an **alternative-fuel** scenario (40% waste-derived fuel),
  and a **CCS** scenario (85% capture + cleaner grid), and identify the
  irreducible floor set by calcination chemistry.
- **Functional unit:** **1 kg of cement** (cradle-to-gate).
- **System boundary:** clinker production (calcination + kiln fuel) + grinding
  electricity. Two CO₂ sources are distinguished: **process/calcination CO₂**
  (from limestone → lime, chemically unavoidable) and **combustion CO₂** (kiln
  fuel). This split is the whole point.
- **Method:** IPCC 2013 GWP100.

## 2. Life Cycle Inventory

Scenario parameters in `cement_scenarios.csv`. Per kg cement:

- calcination CO₂ = `clinker_ratio` × `calcination_co2` (process, unavoidable)
- kiln combustion CO₂ = `clinker_ratio` × `fuel_energy` ×
  (`coal_share`×`coal_ci` + (1−`coal_share`)×`altfuel_ci`)
- grinding CO₂ = `elec_use` × `grid_ci`
- CCS captures `ccs_capture` of the (calcination + combustion) CO₂

## 3. Life Cycle Impact Assessment

The notebook computes total GWP per scenario, **decomposed** into calcination /
combustion / electricity, and plots a stacked bar. The key visual result: alt-fuel
cuts only the combustion slice; CCS cuts across calcination + combustion but adds
an electricity penalty; and even aggressive action leaves the calcination floor
unless the captured stream includes process CO₂.

## 4. Interpretation

- **Contribution analysis:** shows calcination as the dominant, hardest slice —
  in the baseline it's ~50% of the total and cannot be touched by fuel switching.
- **Scenario comparison:** ranks the three options and quantifies the residual
  floor.
- **Sensitivity:** tornado over clinker ratio (SCM substitution), capture rate,
  and grid intensity — clinker substitution and capture rate dominate; grid
  intensity matters more in the CCS scenario because of its parasitic load.
- **Caveats:** excludes SCM (fly ash/slag) upstream burdens and CO₂ transport/
  storage for CCS; a full study would add these. Values are illustrative.

## Reproduce

Open `study.ipynb` with **Python (brightway25)** and run all. Offline, seconds.
