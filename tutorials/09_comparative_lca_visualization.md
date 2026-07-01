# Tutorial 09 â€” Comparative LCA & Visualization

**Companion notebook:** [09_comparative_lca_visualization.ipynb](09_comparative_lca_visualization.ipynb)

Most LCA studies that influence a decision are **comparative**: product A vs B,
scenario X vs Y. This tutorial consolidates the calculation patterns from 05â€“08
into a small comparative-study toolkit and covers the visual grammar for
reporting results honestly.

## 1. The comparative results cube

Every comparative study reduces to a 3-dimensional array:

```
scores[alternative, impact_category, (scenario | MC draw)]
```

The notebook builds `compare(alternatives, methods)` â†’ tidy ("long") DataFrame
with columns `alternative, method, unit, score` â€” tidy format because every
plotting and stats tool downstream (pandas groupby, seaborn) natively consumes
it. Wide tables are for the final report, produced at the very end with
`.pivot()`.

Key implementation points (from tutorial 05): one `LCA` object,
`lci(factorize=True)`, `switch_method()` across categories,
`lcia(demand=...)` across alternatives.

## 2. Fair comparison checklist

Before plotting anything, verify:

- **Same functional unit**, quantitatively identical service ("1000 uses of a
