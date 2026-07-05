# Tutorial 07 — Uncertainty & Monte Carlo

**Companion notebook:** [07_uncertainty_monte_carlo.ipynb](07_uncertainty_monte_carlo.ipynb)

Every exchange amount in an LCA is uncertain — measurement error, temporal and
geographic variability, technology proxies. Deterministic scores hide this.
Brightway makes stochastic LCA nearly free: attach distributions to exchanges,
tell the LCA object to sample them, iterate.

## 1. Describing uncertainty: stats_arrays

Each exchange can carry uncertainty fields following the
[`stats_arrays`](https://stats-arrays.readthedocs.io) convention (same scheme
ecoinvent uses):

| `uncertainty type` | id | key fields |
|---|---|---|
| No uncertainty | 0/1 | `amount` |
| **Lognormal** | 2 | `loc` = ln(median), `scale` = σ of underlying normal |
| Normal | 3 | `loc` = mean, `scale` = σ |
| Uniform | 4 | `minimum`, `maximum` |
| Triangular | 5 | `minimum`, `loc` (mode), `maximum` |

```python
exc["uncertainty type"] = 2          # lognormal
exc["loc"] = np.log(exc["amount"])   # median = deterministic value
exc["scale"] = 0.15                  # GSD ≈ e^0.15 ≈ 1.16
exc.save()
```

**Lognormal is the LCA default** (amounts are positive, right-skewed;
ecoinvent's pedigree approach produces lognormals). Rule of thumb for `scale`:
0.1 ≈ tight (±10–20%), 0.3 ≈ loose (±35–80%).

## 2. Running Monte Carlo (the 2.5 way)

```python
lca = bc.LCA({kettle: 1}, method=gwp, use_distributions=True)
lca.lci(); lca.lcia()

scores = np.array([lca.score for _ in zip(range(500), lca)])
```

Iterating the LCA object (`next(lca)`) resamples every uncertain parameter,
rebuilds the matrices, re-solves, and re-characterizes. 500–1000 iterations is
plenty for a foreground model; report **median and a 90% interval**
(2.5/97.5 for 95%), not mean ± σ — LCA output distributions are skewed.

> **Legacy note:** old Brightway had a separate `MonteCarloLCA` class. In
> bw2calc 2.x it's gone — `LCA(..., use_distributions=True)` + iteration *is*
> the Monte Carlo interface.

## 3. Comparing alternatives: dependent sampling

The critical subtlety. Wrong way: run independent MC for products A and B,
compare the two histograms. If A and B share background processes (same
electricity), independent sampling ignores that their errors are **correlated**
— and *overstates* the overlap.

Right way — sample once, evaluate both demands on the same matrix draw:

```python
lca = bc.LCA({a: 1}, method=gwp, use_distributions=True)
lca.lci(); lca.lcia()
diffs = []
for _ in range(500):
    next(lca)
    lca.lcia(demand={a.id: 1}); sa = lca.score
    lca.lcia(demand={b.id: 1}); sb = lca.score
    diffs.append(sa - sb)
np.mean(np.array(diffs) > 0)    # P(A worse than B)
```

The deliverable statistic for comparative LCA is exactly that:
**P(A > B)** under shared uncertainty — the notebook demonstrates both
approaches and shows how much they disagree.

## 4. Which inputs matter? (toward GSA)

The notebook closes with a pragmatic sensitivity screen: correlate each sampled
input parameter with the output scores (Spearman ρ across MC draws). Parameters
with |ρ| > ~0.3 dominate output variance → prioritize them for better data.
This is "poor man's GSA"; the real thing (Sobol indices, delta-moment methods)
lives in the `SALib` ecosystem and pairs naturally with tutorial 08's
parameterized models.

## Pitfalls

- **`loc` for lognormal is ln(median)**, not the median. Setting
  `loc = exc["amount"]` inflates results by orders of magnitude. (bw2io's
  strategies handle this on import; hand-set fields are on you.)
- `negative=True` field is required for lognormal exchanges with negative
  amounts (e.g. substitution credits).
- MC without `use_distributions=True` silently returns identical scores every
  iteration — assert `scores.std() > 0` in your code.
- Don't compare a deterministic score of A with an MC distribution of B; run
  both stochastic, dependently.

## Next

→ [08 — Parameters & scenarios](08_parameters_scenarios.md): make the *model*
a function of named parameters, then sweep them.
