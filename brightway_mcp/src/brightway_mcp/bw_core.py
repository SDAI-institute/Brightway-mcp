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
    a read tool — silent creation is the classic Brightway footgun)."""
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


def _find_biosphere(bio_name: Optional[str], name: str, categories=("air",)) -> Any:
    if bio_name is None:
        raise BrightwayToolError(
            "No biosphere database in this project.", error_code="NO_BIOSPHERE",
            suggested_next_actions=[
                "Install one: bw2io.remote.install_project('ecoinvent-3.10-biosphere', <project>)."],
        )
    bio = bd.Database(bio_name)
    try:
        return next(f for f in bio
                    if f["name"] == name and tuple(f["categories"]) == tuple(categories))
    except StopIteration:
        raise BrightwayToolError(
            f"No biosphere flow name={name!r} categories={categories!r}.",
            error_code="FLOW_NOT_FOUND",
            suggested_next_actions=["Check the exact flow name and compartment."],
        )


# --------------------------------------------------------------------------
# Calculation
# --------------------------------------------------------------------------

def run_lca(activity: Any, method: Tuple, amount: float = 1.0) -> Tuple[Any, float, str]:
    lca = bc.LCA({activity: amount}, method=method)
    lca.lci()
    lca.lcia()
    unit = bd.Method(method).metadata.get("unit", "")
    return lca, float(lca.score), unit


def multi_method(activity: Any, methods: List[Tuple], amount: float = 1.0) -> List[Dict[str, Any]]:
    methods = [resolve_method(m) for m in methods]
    lca = bc.LCA({activity: amount}, method=methods[0])
    lca.lci(factorize=True)
    lca.lcia()
    out = []
    for m in methods:
        lca.switch_method(m)
        lca.lcia()
        out.append({"method": list(m), "score": float(lca.score),
                    "unit": bd.Method(m).metadata.get("unit", "")})
    return out


def monte_carlo(activity: Any, method: Tuple, iterations: int = 500,
                amount: float = 1.0, seed: Optional[int] = None) -> Dict[str, Any]:
    import numpy as np
    lca = bc.LCA(
        {activity: amount},
        method=method,
        use_distributions=True,
        seed_override=seed,
    )
    lca.lci()
    lca.lcia()
    scores = np.array([lca.score for _ in zip(range(iterations), lca)])
    return {
        "iterations": int(len(scores)),
        "seed": seed,
        "mean": float(scores.mean()),
        "std": float(scores.std()),
        "median": float(np.median(scores)),
        "percentile_5": float(np.percentile(scores, 5)),
        "percentile_95": float(np.percentile(scores, 95)),
    }


# --------------------------------------------------------------------------
# Interpretation
# --------------------------------------------------------------------------

def top_processes(lca: Any, limit: int = 10) -> List[Dict[str, Any]]:
    import bw2analyzer as ba
    ca = ba.ContributionAnalysis()
    total = lca.score
    out = []
    for s, supply, act in ca.annotated_top_processes(lca, limit=limit):
        out.append({"score": float(s),
                    "share": float(s / total) if total else None,
                    "supply": float(supply), "name": str(act)})
    return out


def top_emissions(lca: Any, limit: int = 10) -> List[Dict[str, Any]]:
    import bw2analyzer as ba
    ca = ba.ContributionAnalysis()
    total = lca.score
    out = []
    for s, amount, flow in ca.annotated_top_emissions(lca, limit=limit):
        out.append({"score": float(s),
                    "share": float(s / total) if total else None,
                    "amount": float(amount), "name": str(flow)})
    return out


def supply_chain(activity: Any, method: Tuple, amount: float = 1.0,
                 max_level: int = 3, cutoff: float = 0.02) -> Dict[str, Any]:
    """Recursive supply-chain contribution as a bounded tree. Each node reports
    its cumulative share of the total score. Meant for foreground/small systems
    (each node solves an LCA); ``max_level`` + ``cutoff`` bound the recursion."""
    method = resolve_method(method)
    root = bc.LCA({activity: amount}, method=method)
    root.lci()
    root.lcia()
    total = float(root.score)

    def node(act: Any, amt: float, level: int) -> Dict[str, Any]:
        lca = bc.LCA({act: amt}, method=method)
        lca.lci()
        lca.lcia()
        share = (lca.score / total) if total else 0.0
        entry = {"name": act.get("name"), "amount": float(amt),
                 "score": float(lca.score), "share": float(share), "children": []}
        if level < max_level and abs(share) >= cutoff:
            for exc in act.technosphere():
                entry["children"].append(node(exc.input, amt * exc["amount"], level + 1))
        return entry

    return {"total": total, "unit": bd.Method(method).metadata.get("unit", ""),
            "tree": node(activity, amount, 0)}


def compare_activities(alternatives: List[Dict[str, Any]],
                       methods: List[Tuple]) -> List[Dict[str, Any]]:
    """Comparative LCA: several activities x several methods (multi-FU grid).

    alternatives: list of {database, code|name, [label]}.
    Uses one factorized LCA object and switch_method for efficiency.
    """
    resolved = []
    for a in alternatives:
        act = get_activity(a["database"], code=a.get("code"), name=a.get("name"))
        resolved.append((a.get("label") or act.get("name"), act))
    methods = [resolve_method(m) for m in methods]

    lca = bc.LCA({resolved[0][1]: 1}, method=methods[0])
    lca.lci(factorize=True)
    lca.lcia()
    rows = []
    for m in methods:
        lca.switch_method(m)
        unit = bd.Method(m).metadata.get("unit", "")
        for label, act in resolved:
            lca.lcia(demand={act.id: 1})
            rows.append({"alternative": label, "method": list(m),
                         "unit": unit, "score": float(lca.score)})
    return rows


# --------------------------------------------------------------------------
# Uncertainty setup
# --------------------------------------------------------------------------

_DIST = {"lognormal": 2, "normal": 3, "uniform": 4, "triangular": 5}


def set_uncertainty(activity: Any, scale: float = 0.15,
                    distribution: str = "lognormal",
                    input_filter: Optional[str] = None) -> Dict[str, Any]:
    """Attach an uncertainty distribution to an activity's non-production
    exchanges, so Monte Carlo has something to sample.

    scale: for lognormal/normal, sigma of the underlying/normal (GSD-ish);
    for uniform/triangular, the +/- fractional half-width around the amount.
    input_filter: only touch exchanges whose input name contains this substring.
    """
    import math
    ut = _DIST.get(distribution)
    if ut is None:
        raise BrightwayToolError(
            f"Unknown distribution {distribution!r}.", error_code="BAD_REQUEST",
            suggested_next_actions=[f"Use one of: {list(_DIST)}"],
        )
    n = 0
    for exc in activity.exchanges():
        if exc["type"] == "production":
            continue
        if input_filter and input_filter.lower() not in (exc.input.get("name") or "").lower():
            continue
        amt = exc["amount"]
        exc["uncertainty type"] = ut
        if ut == 2:  # lognormal
            exc["loc"] = math.log(abs(amt)) if amt != 0 else 0.0
            exc["scale"] = scale
            if amt < 0:
                exc["negative"] = True
        elif ut == 3:  # normal
            exc["loc"] = amt
            exc["scale"] = abs(amt) * scale
        elif ut == 4:  # uniform
            exc["minimum"] = amt * (1 - scale)
            exc["maximum"] = amt * (1 + scale)
        elif ut == 5:  # triangular
            exc["minimum"] = amt * (1 - scale)
            exc["loc"] = amt
            exc["maximum"] = amt * (1 + scale)
        exc.save()
        n += 1
    bd.Database(activity.key[0]).process()
    return {"activity": activity.get("name"), "exchanges_updated": n,
            "distribution": distribution, "scale": scale}


# --------------------------------------------------------------------------
# Inspection, setup, import, export, health
# --------------------------------------------------------------------------

def activity_detail(activity: Any) -> Dict[str, Any]:
    """Full exchange list of one activity."""
    exchanges = []
    for e in activity.exchanges():
        exchanges.append({
            "type": e["type"], "amount": e["amount"],
            "input_name": e.input.get("name"), "input_key": list(e.input.key),
            "unit": e.input.get("unit"),
            "uncertainty_type": e.get("uncertainty type", 0),
        })
    return {"name": activity.get("name"), "unit": activity.get("unit"),
            "key": list(activity.key), "id": activity.id,
            "location": activity.get("location"), "exchanges": exchanges}


def search_biosphere(query: str, limit: int = 10,
                     categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """Search elementary flows in the biosphere database by name substring."""
    bio_name = biosphere_name()
    if bio_name is None:
        raise BrightwayToolError(
            "No biosphere database in this project.", error_code="NO_BIOSPHERE",
            suggested_next_actions=["Call setup_project to install one."],
        )
    bio = bd.Database(bio_name)
    q = query.lower()
    cat = tuple(categories) if categories else None
    out = []
    for f in bio:
        if q not in (f["name"] or "").lower():
            continue
        fcat = tuple(f.get("categories") or ())
        if cat is not None and fcat != cat:
            continue
        out.append({"name": f["name"], "categories": list(fcat),
                    "unit": f.get("unit"), "code": f.key[1], "database": f.key[0]})
        if len(out) >= limit:
            break
    return out


def setup_project(project: str, source: str = "ecoinvent-3.10-biosphere",
                  overwrite: bool = False) -> Dict[str, Any]:
    """Bootstrap a project with a free biosphere + LCIA methods via a remote
    prepared project. No-ops (returns created=False) if already set up and not
    overwriting. Network required only when it actually installs."""
    import bw2io as bi
    existed = project in {p.name for p in bd.projects}
    if existed and not overwrite:
        bd.projects.set_current(project)
        if any("biosphere" in d.lower() for d in bd.databases):
            return {"project": project, "created": False,
                    "biosphere": biosphere_name(), "methods": len(bd.methods),
                    "note": "already set up"}
    bi.remote.install_project(source, project, overwrite_existing=overwrite)
    bd.projects.set_current(project)
    return {"project": project, "created": not existed,
            "biosphere": biosphere_name(), "methods": len(bd.methods)}


def import_lcia_methods(project: str, zip_path: str,
                        drop_unlinked: bool = True) -> Dict[str, Any]:
    """Import an openLCA JSON-LD LCIA method pack (e.g. a local ecoinvent LCIA
    zip) into a project, patching the bw2io strategy quirks these packs trip."""
    import tempfile
    import zipfile
    from pathlib import Path
    from bw2io.importers.json_ld_lcia import JSONLDLCIAImporter

    p = Path(zip_path)
    if not p.exists():
        raise BrightwayToolError(
            f"Zip not found: {zip_path}", error_code="NOT_FOUND",
            suggested_next_actions=["Check the path to the LCIA .zip pack."],
        )
    bd.projects.set_current(project)
    bio = biosphere_name()
    if bio is None:
        raise BrightwayToolError(
            "Target project has no biosphere.", error_code="NO_BIOSPHERE",
            suggested_next_actions=["Call setup_project first."],
        )
    before = len(bd.methods)
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(p) as z:
            z.extractall(tmp)
        imp = JSONLDLCIAImporter(tmp)
        for section in ("lcia_methods", "lcia_categories", "flows"):
            for obj in imp.data.get(section, {}).values():
                obj.setdefault("lastChange", "")
                obj.setdefault("version", "00.00.000")
                obj.setdefault("description", "")
                if isinstance(obj.get("parameters"), list):
                    obj["parameters"] = {}
        for cat in imp.data.get("lcia_categories", {}).values():
            cat.setdefault("impactFactors", [])
        imp.apply_strategies()
        imp.match_biosphere_by_id(bio)
        if not imp.all_linked and drop_unlinked:
            imp.drop_unlinked()
        imp.write_methods(overwrite=True)
    after = len(bd.methods)
    return {"project": project, "methods_added": after - before,
            "methods_total": after, "biosphere": bio}


def export_result_csv(lca: Any, path: str, limit: int = 25) -> Dict[str, Any]:
    """Write a stored result's process-contribution table to a CSV file."""
    import csv
    procs = top_processes(lca, limit)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rank", "score", "share", "supply", "name"])
        for i, r in enumerate(procs, 1):
            w.writerow([i, r["score"], r["share"], r["supply"], r["name"]])
    return {"path": path, "rows": len(procs)}


def health_check() -> Dict[str, Any]:
    """Versions + a quick environment sanity summary."""
    import bw2data
    import bw2calc
    import bw2io
    return {
        "bw2data": bw2data.__version__,
        "bw2calc": bw2calc.__version__,
        "bw2io": bw2io.__version__,
        "current_project": bd.projects.current,
        "n_projects": len(list(bd.projects)),
        "read_only_supported": True,
    }
