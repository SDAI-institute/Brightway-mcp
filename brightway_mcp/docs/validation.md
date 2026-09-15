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
- therefore the hand-derived total for 1 kg product is `3 Ã— 2.0 + 0.5 = 6.5 kg CO2e`.

The recorded test result is 6.5 kg CO2e in Brightway and 6.5 kg CO2e in the corresponding openLCA synthetic case. The 2 kg scaling check records 13.0 kg CO2e in both engines.

This validates the tested synthetic calculation path and linear scaling. It does not prove equivalence for arbitrary databases, allocation methods, non-linear workflows, or all LCA features.

## Additional bug-class checks

The repository reliability note records checks for:
