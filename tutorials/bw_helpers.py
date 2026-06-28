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
    prepared 2.5 project â€” it is 'ecoinvent-3.10-biosphere')."""
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
