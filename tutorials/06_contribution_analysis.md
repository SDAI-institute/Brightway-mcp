# Tutorial 06 â€” Contribution Analysis & Interpretation

**Companion notebook:** [06_contribution_analysis.ipynb](06_contribution_analysis.ipynb)

A single score answers "how much?". Interpretation (ISO 14044 phase 4) answers
"**why**, and **where do I intervene**?". Because bw2calc keeps results
disaggregated (`lca.characterized_inventory` is impacts by flow Ã— process),
contribution analysis is mostly clever slicing of a matrix you already have.

## 1. The two fundamental cuts

For a solved, characterized LCA:

```python
ci = lca.characterized_inventory        # sparse: flows Ã— processes

by_process = ci.sum(axis=0)   # column sums â†’ impact attributable to each process
by_flow    = ci.sum(axis=1)   # row sums    â†’ impact attributable to each emission
```

- **By process** ("process contribution"): where in the *supply chain* impacts
  occur â€” coal power plant, steel mill, â€¦
- **By flow** ("elementary flow contribution"): which *substances* carry the
  impact â€” COâ‚‚ vs CHâ‚„ vs Nâ‚‚O.

The notebook maps indices back to names via `lca.dicts` and wraps both cuts
into DataFrames sorted by contribution, with a `share` column.

## 2. bw2analyzer conveniences

```python
import bw2analyzer as ba

ca = ba.ContributionAnalysis()
ca.annotated_top_processes(lca, limit=10)   # [(score, supply amount, name), ...]
ca.annotated_top_emissions(lca, limit=10)
```

Same information as the manual cuts, pre-annotated with activity metadata.

## 3. Direct vs cumulative: `recursive_calculation`
