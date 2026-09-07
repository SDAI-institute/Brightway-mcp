# Brightway MCP — Reliability Verification (SDAI reliability pass)

**Method:** independently tested `brightway_mcp` for correctness, following the
same rigor applied to `openlca_mcp` (which found and fixed a critical ~30×
unit-conversion bug in that project's underlying library). Since Brightway is
a real background-LCA engine — directly comparable to openLCA, unlike
BioSTEAM (a TEA/process-simulation tool with no LCA benchmark to be judged
against) — this audit **reused the exact golden-system scenario** from
`openlca_library/tests/fixtures/golden_system.py` rather than inventing a
look-alike, so a matching result is a genuine cross-engine confirmation.

**Bottom line: no defects found.** Every test passed, including bug-class
checks modeled directly on the categories of bug that broke `openlca_mcp`
(unit/sign handling, characterization-factor correctness, result consistency).
One minor test-isolation hygiene issue was found in the pre-existing test
suite (not a correctness bug — see "Findings" below).

## Environment

- Installed into `Brightway2/.venv` (Python 3.13.5); `bw2data 4.7`,
  `bw2calc`, `bw2io`, `bw2analyzer` all import cleanly.
- Original test suite: **23/23 passed** (the earlier exploratory estimate of
  "~20 tests" was informal; the actual count is 23).
- Post-hardening: **30 passed, 1 deselected** (the 1 deselected is the new
  network-gated CF spot-check, opt-in via `pytest -m network`).

## Cross-engine validation (golden system)

Ported the exact scenario from `openlca_library`'s golden system — one
elementary flow with a known characterization factor, a 2-level process
chain, hand-derived total — into Brightway via `bw_core` (the same functions
the MCP tools call):

```
Golden Material Production          Golden Product Production (= reference)
  output: 1 kg Golden Material        output: 1 kg Golden Product
  emits:  2.0 kg CO2 (fossil)          input:  3 kg Golden Material
                                       emits:  0.5 kg CO2 (fossil)
```

| Check | Expected | Brightway result | openLCA result (same system) | Match |
|---|---|---|---|---|
| 1 kg Golden Product | 6.5 kg CO2e | **6.5** | 6.5 | ✅ exact, both engines |
| 2 kg (linear scaling) | 13.0 kg CO2e | **13.0** | 13.0 | ✅ exact |

This is not a coincidence of two similarly-designed systems — it is the
identical scenario, computed independently by two different LCA engines,
agreeing to floating-point precision. See the shared cross-engine write-up
for the full comparison.

## Characterization-factor spot-check (real background data)

To rule out method-level defects (the same class of check that ruled out
EF 3.1's characterization factors in the `openlca_mcp` audit), verified a
**real** ecoinvent-3.10-biosphere flow under a **real** LCIA method:

| Flow | Method | Expected | Result |
|---|---|---|---|
| `Carbon dioxide, fossil` (biosphere3) | `IPCC 2021 no LT / climate change: fossil no LT / GWP100 no LT` | 1.0 kg CO2-Eq | **1.0** exact |

(`tests/test_cf_spotcheck_network.py`, network-gated since it downloads the
free ecoinvent-3.10-biosphere pack via `bw2io` on first use — not part of the
default `pytest` run.)

## Bug-class checks (modeled on the openlca_mcp defect categories)

| Check | Result |
|---|---|
| **Determinism** — 5 repeated `run_lca` calls on the identical database | Identical every time (spread = 0.0) |
| **Contribution consistency** — `top_processes`/`top_emissions` shares sum to the total | Both sum to the total within 1e-6 |
| **Monte Carlo sanity** — mean converges near the deterministic value; percentiles ordered | P5 ≤ median ≤ P95; mean within 3σ of deterministic |
| **Unit/sign fuzzing** — a negative technosphere exchange (avoided-burden credit) must *reduce*, not increase, the total | `10.0 + (-0.5 × 4.0) = 8.0` computed exactly; confirmed `< 10.0` |

All four pass (`tests/test_golden_system.py`). Together with the golden-system
match, this directly tests for the openlca_mcp bug class (silent unit/sign
mishandling) and finds no equivalent defect in Brightway.

## Findings

**F1 (minor, hygiene, not a correctness bug) — `bw_project` fixture leaves a
stray project registration.** The existing `tests/conftest.py` fixture sets
`BRIGHTWAY_DIR` to a temp directory before creating its `bw-mcp-test` project,
intending full test isolation. In practice, running the test suite leaves a
`bw-mcp-test` entry in the **real/default** Brightway project registry (visible
via `bw2data.projects` after running from a plain shell) even though the
underlying data appears to live in the temp directory. This is pre-existing
test infrastructure, not something introduced by this reliability pass, and
it's a minor developer-experience nuisance (an extra empty-looking project
name accumulates in the user's real Brightway install), not a data-correctness
issue. **Recommendation:** add an explicit
`bd.projects.delete_project("bw-mcp-test", delete_dir=True)` in the fixture's
teardown (in addition to `shutil.rmtree`), or investigate why
`BRIGHTWAY_DIR` doesn't fully redirect the project *registry* (as opposed to
project *data*).

**No other findings.** All 22 MCP tools are backed by real, substantive logic
(confirmed in the earlier codebase audit); the reliability tests added here
found no unit-handling, sign-convention, consistency, or characterization
defects.

## What changed

- `pyproject.toml`: registered a `network` pytest marker, excluded from the
  default run (`addopts = "-m 'not network'"`).
- `tests/test_golden_system.py` (new): golden-system cross-engine match,
  determinism, consistency, Monte Carlo sanity, sign fuzzing — 7 tests.
- `tests/test_cf_spotcheck_network.py` (new): real biosphere3 CF spot-check —
  1 test, network-gated.

## Reproduce

```bash
cd Brightway2/brightway_mcp
../.venv/Scripts/python -m pytest -q                    # 30 passed, 1 deselected
../.venv/Scripts/python -m pytest -m network -v         # the CF spot-check (downloads ~17MB)
```
