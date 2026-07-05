# Tutorial 07 â€” Uncertainty & Monte Carlo

**Companion notebook:** [07_uncertainty_monte_carlo.ipynb](07_uncertainty_monte_carlo.ipynb)

Every exchange amount in an LCA is uncertain â€” measurement error, temporal and
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
| **Lognormal** | 2 | `loc` = ln(median), `scale` = Ïƒ of underlying normal |
| Normal | 3 | `loc` = mean, `scale` = Ïƒ |
| Uniform | 4 | `minimum`, `maximum` |
| Triangular | 5 | `minimum`, `loc` (mode), `maximum` |

```python
exc["uncertainty type"] = 2          # lognormal
exc["loc"] = np.log(exc["amount"])   # median = deterministic value
exc["scale"] = 0.15                  # GSD â‰ˆ e^0.15 â‰ˆ 1.16
exc.save()
```

**Lognormal is the LCA default** (amounts are positive, right-skewed;
ecoinvent's pedigree approach produces lognormals). Rule of thumb for `scale`:
0.1 â‰ˆ tight (Â±10â€“20%), 0.3 â‰ˆ loose (Â±35â€“80%).

## 2. Running Monte Carlo (the 2.5 way)

```python
lca = bc.LCA({kettle: 1}, method=gwp, use_distributions=True)
lca.lci(); lca.lcia()

scores = np.array([lca.score for _ in zip(range(500), lca)])
