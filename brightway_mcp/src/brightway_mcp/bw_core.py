"""Thin, agent-friendly wrapper over bw2data / bw2calc / bw2analyzer.

Keeps all direct Brightway calls in one place so the tool modules stay declarative
and so tests can exercise the logic without going through MCP. Every function
raises :class:`BrightwayToolError` with an agent-legible message on failure.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import bw2data as bd
import bw2calc as bc

from .responses import BrightwayToolError


# --------------------------------------------------------------------------
# Projects & databases
# --------------------------------------------------------------------------

def list_projects() -> List[Dict[str, Any]]:
    return [{"name": p.name} for p in bd.projects]


def use_project(project: str) -> None:
    """Activate a project. Raises if it does not exist (we never auto-create in
    a read tool â€” silent creation is the classic Brightway footgun)."""
    if project not in {p.name for p in bd.projects}:
        raise BrightwayToolError(
            f"Project {project!r} does not exist.",
            error_code="UNKNOWN_PROJECT",
            suggested_next_actions=["Call list_projects to see available projects."],
        )
    bd.projects.set_current(project)


def ensure_project(project: str) -> bool:
    """Activate a project, creating it if absent. Returns True if created.
    Only call from write tools."""
    existed = project in {p.name for p in bd.projects}
    bd.projects.set_current(project)  # creates if missing
    return not existed


def biosphere_name() -> Optional[str]:
    """Resolve the biosphere database name (NOT always 'biosphere3')."""
    for d in bd.databases:
        if "biosphere" in d.lower():
            return d
    return None


def list_databases() -> List[Dict[str, Any]]:
    out = []
    for name in bd.databases:
        try:
            out.append({"name": name, "count": len(bd.Database(name))})
        except Exception:
            out.append({"name": name, "count": None})
    return out


def database_stats(name: str) -> Dict[str, Any]:
    if name not in bd.databases:
        raise BrightwayToolError(
            f"Database {name!r} not found in project {bd.projects.current!r}.",
            error_code="UNKNOWN_DATABASE",
            suggested_next_actions=["Call list_databases."],
        )
    db = bd.Database(name)
    n_tech = n_bio = n_prod = 0
    for act in db:
        for exc in act.exchanges():
            t = exc.get("type")
            n_tech += t == "technosphere"
            n_bio += t == "biosphere"
            n_prod += t == "production"
    return {"name": name, "activities": len(db),
            "technosphere_exchanges": n_tech, "biosphere_exchanges": n_bio,
            "production_exchanges": n_prod}


# --------------------------------------------------------------------------
# Search & lookup
# --------------------------------------------------------------------------

def _act_summary(act: Any) -> Dict[str, Any]:
    return {
        "database": act.key[0], "code": act.key[1], "id": act.id,
        "name": act.get("name"), "unit": act.get("unit"),
        "location": act.get("location"),
    }


def search_activities(database: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
    if database not in bd.databases:
        raise BrightwayToolError(
            f"Database {database!r} not found.", error_code="UNKNOWN_DATABASE",
            suggested_next_actions=["Call list_databases."],
        )
    db = bd.Database(database)
    q = query.lower()
    hits = [a for a in db if q in (a.get("name") or "").lower()]
    return [_act_summary(a) for a in hits[:limit]]


def get_activity(database: str, code: Optional[str] = None,
                 name: Optional[str] = None) -> Any:
    if code is not None:
        try:
            return bd.get_node(database=database, code=code)
        except Exception as e:
            raise BrightwayToolError(
                f"No activity with code={code!r} in {database!r}: {e}",
                error_code="NOT_FOUND",
                suggested_next_actions=["Use search_activities to find the code."],
            )
    if name is not None:
        try:
            return bd.get_node(database=database, name=name)
        except Exception as e:
            raise BrightwayToolError(
                f"No unique activity named {name!r} in {database!r}: {e}",
                error_code="NOT_FOUND",
                suggested_next_actions=["Use search_activities; names may be non-unique."],
            )
    raise BrightwayToolError("Provide either code or name.", error_code="BAD_REQUEST")


def list_methods(filter_substrings: Optional[List[str]] = None,
                 limit: int = 50) -> List[Dict[str, Any]]:
    subs = [s.lower() for s in (filter_substrings or [])]
    out = []
    for m in bd.methods:
        s = str(m).lower()
        if all(sub in s for sub in subs):
            out.append({"method": list(m),
                        "unit": bd.Method(m).metadata.get("unit", "")})
        if len(out) >= limit:
            break
    return out


def resolve_method(method: Any) -> Tuple:
    """Coerce a list/tuple method identifier to a tuple and validate it exists."""
    key = tuple(method)
    if key not in bd.methods:
        raise BrightwayToolError(
            f"Method {key!r} not registered.", error_code="UNKNOWN_METHOD",
            suggested_next_actions=["Call list_methods to find exact method tuples."],
        )
    return key


# --------------------------------------------------------------------------
# Inventory writes
# --------------------------------------------------------------------------

def create_database(name: str, overwrite: bool = False) -> Dict[str, Any]:
    if name in bd.databases:
        if not overwrite:
            raise BrightwayToolError(
                f"Database {name!r} already exists.", error_code="EXISTS",
                suggested_next_actions=["Pass overwrite=true, or pick another name."],
            )
        del bd.databases[name]
    db = bd.Database(name)
    db.register()
    return {"database": name, "created": True}


def write_activities(database: str, activities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Upsert activity specs into a database without deleting unrelated entries.

    Each activity spec: {code, name, unit, exchanges: [{input, amount, type,
    [biosphere_database]}]}. ``input`` is either a [database, code] pair or a
    biosphere flow name (resolved against the biosphere db when type=biosphere).
    Existing activities with matching codes are replaced; all other activities
    are preserved. Use ``create_database(..., overwrite=True)`` for an explicit
    destructive reset.
    """
    bio = biosphere_name()
    data: Dict[Tuple[str, str], Dict[str, Any]] = {}
    for spec in activities:
        code = spec["code"]
        exchanges = []
        for exc in spec.get("exchanges", []):
            etype = exc.get("type", "technosphere")
            inp = exc["input"]
            if etype == "biosphere" and isinstance(inp, str):
                # resolve a biosphere flow by name (+ optional categories)
                cats = tuple(exc.get("categories", ("air",)))
                flow = _find_biosphere(bio, inp, cats)
                key = flow.key
            elif isinstance(inp, (list, tuple)):
                key = tuple(inp)
            else:
                # internal reference by code within this database
                key = (database, inp)
            exchanges.append({"input": key, "amount": exc["amount"], "type": etype})
        # ensure a production exchange exists
        if not any(e["type"] == "production" for e in exchanges):
            exchanges.insert(0, {"input": (database, code), "amount": 1.0,
                                 "type": "production"})
        data[(database, code)] = {
            "name": spec.get("name", code),
            "unit": spec.get("unit", "unit"),
            "exchanges": exchanges,
        }
    db = bd.Database(database)
    existing = db.load() if database in bd.databases else {}
    replaced = sum(1 for key in data if key in existing)
    preserved = sum(1 for key in existing if key not in data)
    merged = dict(existing)
    merged.update(data)
    db.write(merged)
    return {
        "database": database,
        "written": len(data),
        "updated_existing": replaced,
        "preserved_existing": preserved,
        "total": len(merged),
    }


