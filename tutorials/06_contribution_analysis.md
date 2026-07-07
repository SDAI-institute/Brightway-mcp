# Tutorial 06 — Contribution Analysis & Interpretation

**Companion notebook:** [06_contribution_analysis.ipynb](06_contribution_analysis.ipynb)

A single score answers "how much?". Interpretation (ISO 14044 phase 4) answers
"**why**, and **where do I intervene**?". Because bw2calc keeps results
disaggregated (`lca.characterized_inventory` is impacts by flow × process),
contribution analysis is mostly clever slicing of a matrix you already have.

## 1. The two fundamental cuts

For a solved, characterized LCA:

```python
ci = lca.characterized_inventory        # sparse: flows × processes

by_process = ci.sum(axis=0)   # column sums → impact attributable to each process
by_flow    = ci.sum(axis=1)   # row sums    → impact attributable to each emission
```

- **By process** ("process contribution"): where in the *supply chain* impacts
  occur — coal power plant, steel mill, …
- **By flow** ("elementary flow contribution"): which *substances* carry the
  impact — CO₂ vs CH₄ vs N₂O.

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

Column sums give **direct** (gate-to-gate) impacts. A different question —
"what's the *cumulative* footprint of the steel input, including everything
upstream of it?" — needs supply-chain traversal:

```python
ba.print_recursive_calculation(
    kettle, gwp,
    amount=1,
    max_level=4,     # depth
    cutoff=0.02,     # hide branches below 2% of total
)
```

This prints an indented tree: each node shows the *fraction of total score*
flowing through that branch. Crucial reading rule: **branches overlap** —
electricity appears both directly (assembly) and inside steel; cumulative
numbers don't sum to 100%.

There is also `ba.print_recursive_supply_chain(...)` — same tree but amounts
only (no LCIA), useful for checking model structure.

## 4. Grouping (the analysis clients actually want)

Real interpretation groups processes into life-cycle stages ("materials",
"energy", "transport", "EoL"). The notebook implements the standard pattern:
tag foreground activities with a custom attribute...

```python
act["stage"] = "materials"; act.save()
```

...then aggregate the by-process contributions over tags. This produces the
classic stacked-bar-by-stage chart (fully realized in case study 1). For deeply
nested foregrounds, `bw2analyzer.traverse_tagged_databases()` automates
tag-aware traversal.

## 5. Visuals that work

The notebook builds three matplotlib figures you'll reuse constantly:

1. **Horizontal bar** — top-10 process contributions (one method)
2. **Stacked bar by stage** — alternatives side by side
3. **Heatmap** — alternatives × impact categories, normalized per category
   (each column scaled to its max → comparable colors despite different units)

## Pitfalls

- Negative contributions are legitimate (avoided burdens, e.g. recycling
  credits) — never clip them; show them below the axis.
- Top-process lists on IO databases (USEEIO) are dominated by aggregated
  sectors; grouping/tagging matters even more there.
- `recursive_calculation` with low cutoff + high depth explodes
  combinatorially — start at `cutoff=0.05, max_level=3` and loosen as needed.
- Contribution ≠ sensitivity: a process contributing 40% is not automatically
  where a 10% improvement helps most (that's tutorial 07/08 territory).

## Next

→ [07 — Uncertainty & Monte Carlo](07_uncertainty_monte_carlo.md): scores are
not points; give them distributions.
