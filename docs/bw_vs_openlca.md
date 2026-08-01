# Brightway vs openLCA â€” When to Use Which

The SDAI ecosystem has both a Brightway stack (this repo) and an
[`openlca_mcp`](../../openlca_mcp) server. They solve the same LCA math; they
differ in interface and workflow.

| | **Brightway 2.5** | **openLCA** |
|-|-------------------|-------------|
| Nature | Python library | Desktop application (+ IPC/gRPC server) |
| Interface | code (notebooks, scripts) | GUI, or `olca-ipc` over a running instance |
| Automation | native â€” it *is* Python | via the IPC server (openlca-ipc) |
| Data model | projects â†’ databases â†’ activities â†’ exchanges | databases â†’ processes â†’ flows â†’ exchanges |
| Matrices | directly accessible (`lca.technosphere_matrix`) | computed internally, less exposed |
| Uncertainty | `stats_arrays` + `use_distributions` | built-in Monte Carlo |
| Parameters | code formulas + `bw2data.parameters` | GUI global/process parameters |
| Databases | ecoinvent, USEEIO, Forwast, ecospold/SimaPro import | ecoinvent, ELCD, GaBi import, Nexus |
| Scenarios | datapackages, `premise` | product-system variants |
| Best for | system analysis, batch studies, ML pipelines, reproducible science | interactive modeling, review, teaching non-coders, regulated EPDs |
