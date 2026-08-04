# Case Study 3 â€” Cement Clinker: Decarbonization Scenarios

**Notebook:** [study.ipynb](study.ipynb) Â· **Data:** [data/cement_scenarios.csv](data/cement_scenarios.csv)

An industrial-system LCA of Portland cement with three decarbonization
scenarios, exercising scenario analysis (tutorial 08), contribution analysis
(06), and sensitivity. Cement is ~8% of global COâ‚‚ and a textbook "hard-to-abate"
system because a large share of its emissions is **process chemistry**, not
energy â€” which makes it a perfect teaching case for *where* interventions can and
cannot help.

## 1. Goal & Scope

- **Goal:** compare the cradle-to-gate GWP of 1 kg cement under a **baseline**
  (coal-fired kiln), an **alternative-fuel** scenario (40% waste-derived fuel),
  and a **CCS** scenario (85% capture + cleaner grid), and identify the
  irreducible floor set by calcination chemistry.
- **Functional unit:** **1 kg of cement** (cradle-to-gate).
- **System boundary:** clinker production (calcination + kiln fuel) + grinding
  electricity. Two COâ‚‚ sources are distinguished: **process/calcination COâ‚‚**
  (from limestone â†’ lime, chemically unavoidable) and **combustion COâ‚‚** (kiln
  fuel). This split is the whole point.
- **Method:** IPCC 2013 GWP100.
