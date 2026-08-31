"""In-memory registry of Brightway LCA results.

An agent runs an LCA once (search â†’ build â†’ calculate) and then wants to ask
follow-up questions (contributions, top emissions, Monte Carlo) about *that same*
result without recomputing. We hand back a stable ``result_id`` and keep the
solved ``bw2calc.LCA`` object (plus context) here.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass
class StoredResult:
    result_id: str
    lca: Any                       # solved bw2calc.LCA
    project: str
    demand: Dict[str, float]       # {activity_key_str: amount}
    method: tuple
    score: float
    unit: str = ""
