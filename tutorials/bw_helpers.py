"""Shared helpers used across the Brightway 2.5 tutorial notebooks.

Importing this keeps each notebook focused on the concept it teaches rather than
repeating boilerplate (project setup, biosphere-name resolution, flow lookup,
results grids, plotting).

All functions target Brightway 2.5 (bw2data >= 4, bw2calc >= 2).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import bw2data as bd
import bw2calc as bc

TUTORIAL_PROJECT = "bw25-tutorials"


def use_project(name: str = TUTORIAL_PROJECT) -> str:
    """Activate a project; return its name. Fails loudly if biosphere absent."""
    bd.projects.set_current(name)
    if not any("biosphere" in d.lower() for d in bd.databases):
        raise RuntimeError(
            f"Project '{name}' has no biosphere database. Run:\n"
            "  import bw2io as bi\n"
            "  bi.remote.install_project('ecoinvent-3.10-biosphere', "
            f"'{name}')"
        )
    return name


def biosphere_name() -> str:
    """Resolve the biosphere database name (it is NOT 'biosphere3' in the
    prepared 2.5 project — it is 'ecoinvent-3.10-biosphere')."""
    return next(d for d in bd.databases if "biosphere" in d.lower())


def biosphere():
    return bd.Database(biosphere_name())


def find_flow(name: str, categories=("air",)):
    """Robust elementary-flow lookup: match on name AND categories."""
    bio = biosphere()
    try:
        return next(f for f in bio
                    if f["name"] == name and f["categories"] == categories)
    except StopIteration as e:  # pragma: no cover - helps notebook debugging
        raise LookupError(
            f"No biosphere flow name={name!r} categories={categories!r}. "
            f"Try: [f['name'] for f in bio if {name.split(',')[0]!r} in f['name']]"
        ) from e


def gwp_method():
    """The canonical IPCC GWP100 method key (excludes the 'no LT'/SLCF variants)."""
    return next(
        m for m in bd.methods
        if "IPCC 2013" in str(m)
        and "GWP100" in str(m).replace(" ", "")
        and "no LT" not in str(m)
        and "SLCF" not in str(m)
    )


def find_methods(*substrings, exclude=("no LT",)):
    """All method keys whose string contains every substring (case-insensitive)
    and none of the excludes."""
    out = []
    for m in bd.methods:
        s = str(m).lower()
        if all(sub.lower() in s for sub in substrings) and not any(
            ex.lower() in s for ex in exclude
        ):
            out.append(m)
    return out


def score(demand_act, method, amount: float = 1.0) -> float:
    """One-shot LCA score for a single activity."""
    lca = bc.LCA({demand_act: amount}, method=method)
    lca.lci()
    lca.lcia()
    return lca.score


def results_grid(alternatives: dict, methods: list) -> pd.DataFrame:
    """Efficient alternatives x methods score table (tidy long format).

    alternatives: {label: activity}
    methods:      list of method keys
    Uses one factorized LCA object, switch_method across methods, and
    lcia(demand=...) across alternatives.
    """
    labels = list(alternatives)
    acts = [alternatives[k] for k in labels]

    lca = bc.LCA({acts[0]: 1}, method=methods[0])
    lca.lci(factorize=True)
    lca.lcia()

    rows = []
    for m in methods:
        lca.switch_method(m)
        unit = bd.Method(m).metadata.get("unit", "")
        for label, act in zip(labels, acts):
            lca.lcia(demand={act.id: 1})
            rows.append({
                "alternative": label,
                "method": " | ".join(m[-2:]) if len(m) >= 2 else str(m),
                "method_key": m,
                "unit": unit,
                "score": lca.score,
            })
    return pd.DataFrame(rows)


def top_processes(lca, limit: int = 10) -> pd.DataFrame:
    """Process contribution table from a solved+characterized LCA."""
    import bw2analyzer as ba
    ca = ba.ContributionAnalysis()
    rows = ca.annotated_top_processes(lca, limit=limit)
    total = lca.score
    return pd.DataFrame(
        [{"score": s, "share": s / total if total else np.nan,
          "supply": sup, "name": str(act)} for s, sup, act in rows]
    )


def top_emissions(lca, limit: int = 10) -> pd.DataFrame:
    """Elementary-flow contribution table from a solved+characterized LCA."""
    import bw2analyzer as ba
    ca = ba.ContributionAnalysis()
    rows = ca.annotated_top_emissions(lca, limit=limit)
    total = lca.score
    return pd.DataFrame(
        [{"score": s, "share": s / total if total else np.nan,
          "amount": amt, "name": str(flow)} for s, amt, flow in rows]
    )
