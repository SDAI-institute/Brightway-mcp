# Brightway MCP â€” Reliability Verification (SDAI reliability pass)

**Method:** independently tested `brightway_mcp` for correctness, following the
same rigor applied to `openlca_mcp` (which found and fixed a critical ~30Ã—
unit-conversion bug in that project's underlying library). Since Brightway is
a real background-LCA engine â€” directly comparable to openLCA, unlike
BioSTEAM (a TEA/process-simulation tool with no LCA benchmark to be judged
against) â€” this audit **reused the exact golden-system scenario** from
`openlca_library/tests/fixtures/golden_system.py` rather than inventing a
look-alike, so a matching result is a genuine cross-engine confirmation.

**Bottom line: no defects found.** Every test passed, including bug-class
checks modeled directly on the categories of bug that broke `openlca_mcp`
(unit/sign handling, characterization-factor correctness, result consistency).
One minor test-isolation hygiene issue was found in the pre-existing test
suite (not a correctness bug â€” see "Findings" below).

## Environment

- Installed into `Brightway2/.venv` (Python 3.13.5); `bw2data 4.7`,
  `bw2calc`, `bw2io`, `bw2analyzer` all import cleanly.
- Original test suite: **23/23 passed** (the earlier exploratory estimate of
  "~20 tests" was informal; the actual count is 23).
- Post-hardening: **30 passed, 1 deselected** (the 1 deselected is the new
  network-gated CF spot-check, opt-in via `pytest -m network`).

## Cross-engine validation (golden system)

Ported the exact scenario from `openlca_library`'s golden system â€” one
elementary flow with a known characterization factor, a 2-level process
chain, hand-derived total â€” into Brightway via `bw_core` (the same functions
the MCP tools call):

```
Golden Material Production          Golden Product Production (= reference)
  output: 1 kg Golden Material        output: 1 kg Golden Product
  emits:  2.0 kg CO2 (fossil)          input:  3 kg Golden Material
                                       emits:  0.5 kg CO2 (fossil)
```

| Check | Expected | Brightway result | openLCA result (same system) | Match |
|---|---|---|---|---|
| 1 kg Golden Product | 6.5 kg CO2e | **6.5** | 6.5 | âœ… exact, both engines |
| 2 kg (linear scaling) | 13.0 kg CO2e | **13.0** | 13.0 | âœ… exact |

This is not a coincidence of two similarly-designed systems â€” it is the
