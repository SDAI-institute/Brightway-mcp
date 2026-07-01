# Tutorial 09 — Comparative LCA & Visualization

**Companion notebook:** [09_comparative_lca_visualization.ipynb](09_comparative_lca_visualization.ipynb)

Most LCA studies that influence a decision are **comparative**: product A vs B,
scenario X vs Y. This tutorial consolidates the calculation patterns from 05–08
into a small comparative-study toolkit and covers the visual grammar for
reporting results honestly.

## 1. The comparative results cube

Every comparative study reduces to a 3-dimensional array:

```
scores[alternative, impact_category, (scenario | MC draw)]
```

The notebook builds `compare(alternatives, methods)` → tidy ("long") DataFrame
with columns `alternative, method, unit, score` — tidy format because every
plotting and stats tool downstream (pandas groupby, seaborn) natively consumes
it. Wide tables are for the final report, produced at the very end with
`.pivot()`.

Key implementation points (from tutorial 05): one `LCA` object,
`lci(factorize=True)`, `switch_method()` across categories,
`lcia(demand=...)` across alternatives.

## 2. Fair comparison checklist

Before plotting anything, verify:

- **Same functional unit**, quantitatively identical service ("1000 uses of a
  cup", not "1 cup"). Most bad comparative LCAs die here.
- **Same system boundaries** (both cradle-to-gate, or both cradle-to-grave).
- **Same background** database and version.
- Differences smaller than background uncertainty are **not findings** —
  pair the comparison with tutorial 07's dependent MC (`P(A>B)`).

## 3. The visual grammar

The notebook implements five report-grade figures (matplotlib/seaborn,
consistent styling helper included):

| Figure | Question it answers | Trap it avoids |
|---|---|---|
| Grouped bar (per category) | who wins, per impact? | never a single mixed-unit bar chart |
| Normalized heatmap (alt × category, column-max = 1) | pattern across many categories | unit-mixing; shows trade-offs |
| Stacked stage bars | *where* the impact sits per alternative | hides nothing under "other" |
| Break-even line plot (score vs use-count/parameter) | when does the durable option win? | point estimates for inherently parametric answers |
| Paired MC violin + P(A>B) annotation | is the difference real? | overlapping histograms read as "no difference" |

Styling rules baked into the helper: impact units in axis labels; functional
unit in the title; horizontal bars for long names; a **relative** axis
(% of max alternative) whenever categories share a panel.

## 4. Exporting

```python
df.to_excel("results.xlsx", sheet_name="scores")     # data
fig.savefig("comparison.png", dpi=200, bbox_inches="tight")
```

The notebook writes both into `tutorials/outputs/` — the same pattern the case
studies use for their deliverables. For interactive exploration, the tidy
DataFrame drops straight into plotly/altair if you prefer; we stay with
matplotlib to keep the environment lean.

## Pitfalls

- Normalizing each category to its max makes *patterns* visible but destroys
  magnitude — always accompany a heatmap with the absolute table.
- Sorting alternatives by one category (usually GWP) biases reading of the
  others; sort by name or by aggregate rank.
- Beware "winner across 15 of 18 categories" claims when the 3 losses are the
  categories that matter for the decision context (e.g., water use for a
  product deployed in arid regions).

## Next

→ [10 — Advanced topics](10_advanced_topics.md): under the hood — matrices,
custom methods, graph traversal, and the legacy↔2.5 API map.
