"""In-memory registry of Brightway LCA results.

An agent runs an LCA once (search → build → calculate) and then wants to ask
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
    context: Dict[str, Any] = field(default_factory=dict)


class ResultStore:
    """Registry of stored results keyed by a generated ``res_<hex>`` id."""

    def __init__(self) -> None:
        self._results: Dict[str, StoredResult] = {}

    def add(self, lca: Any, *, project: str, demand: Dict[str, float],
            method: tuple, score: float, unit: str = "",
            context: Optional[Dict[str, Any]] = None) -> StoredResult:
        result_id = f"res_{uuid.uuid4().hex[:12]}"
        stored = StoredResult(
            result_id=result_id, lca=lca, project=project, demand=demand,
            method=tuple(method), score=score, unit=unit, context=context or {},
        )
        self._results[result_id] = stored
        return stored

    def get(self, result_id: str) -> Optional[StoredResult]:
        return self._results.get(result_id)

    def __contains__(self, result_id: str) -> bool:
        return result_id in self._results

    def dispose(self, result_id: str) -> bool:
        return self._results.pop(result_id, None) is not None

    def dispose_all(self) -> int:
        n = len(self._results)
        self._results.clear()
        return n


# Process-wide store shared by all tools.
store = ResultStore()
