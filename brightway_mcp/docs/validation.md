# Brightway MCP Validation Scope

This page summarizes the repository's current reliability evidence without turning it into a general accuracy, security, or LCA-validity claim. The detailed test record remains in [`RELIABILITY.md`](../RELIABILITY.md).

## Reviewed environment

The recorded reliability pass used the repository's Brightway environment and test fixtures. The note reports Python 3.13.5 with `bw2data 4.7` and associated Brightway packages, followed by **30 passing tests and 1 network-gated test deselected** in the default post-hardening suite.

These numbers describe that recorded test environment. They are not a service-level guarantee.

## Cross-engine synthetic golden system

The reliability suite ports the same hand-derived synthetic system used in the openLCA IPC validation into Brightway.

The reference calculation is intentionally simple:

- material-production process emits 2.0 kg CO2-equivalent per kg material;
- product process consumes 3 kg material and emits 0.5 kg CO2-equivalent directly;
- therefore the hand-derived total for 1 kg product is `3 × 2.0 + 0.5 = 6.5 kg CO2e`.

The recorded test result is 6.5 kg CO2e in Brightway and 6.5 kg CO2e in the corresponding openLCA synthetic case. The 2 kg scaling check records 13.0 kg CO2e in both engines.

This validates the tested synthetic calculation path and linear scaling. It does not prove equivalence for arbitrary databases, allocation methods, non-linear workflows, or all LCA features.

## Additional bug-class checks

The repository reliability note records checks for:

- deterministic repeated calculations on the identical fixture;
- contribution totals reconciling with the total score;
- Monte Carlo percentile ordering and basic sanity;
- negative technosphere exchange/sign behavior;
- one network-gated characterization-factor spot check using a real biosphere flow and LCIA method.

## Known finding

The reliability pass records one minor test-isolation hygiene issue: the test fixture can leave a project registration entry in the user's default Brightway project registry even though test data are intended to live in a temporary directory. The note classifies this as a developer-environment hygiene issue, not a calculation-correctness defect.

## What this evidence supports

Within the documented fixtures and environment, the tests support statements that:

- the tested Brightway MCP/core paths reproduced the hand-derived synthetic result;
- the tested scaling, contribution, sign, and uncertainty sanity checks passed;
- no equivalent silent unit/sign defect was found in the tested Brightway path.

## What it does not support

The validation does **not** establish:

- correctness of every Brightway database or LCIA method;
- validity of an arbitrary foreground model;
- methodological compliance of a specific LCA study;
- hosted reliability, uptime, enterprise security, or multi-user isolation;
- correctness of AI-generated study definitions or interpretations.

## Reproduction

The repository records these commands for the current test suite:

```bash
cd Brightway2/brightway_mcp
../.venv/Scripts/python -m pytest -q
../.venv/Scripts/python -m pytest -m network -v
```

The network-gated test may download external free background data and should be run deliberately. Preserve the package versions and source revision with any reproduced validation report.