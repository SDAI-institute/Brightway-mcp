"""FastMCP server exposing Brightway 2.5 as agent tools, organized by ISO phase.

Tool groups (mirroring the sibling ``openlca_mcp``):
  * Goal & scope   — projects, databases, search activities, list methods (read)
  * Inventory      — create database, write activities (write)
  * Impact         — run LCA, multi-method, Monte Carlo (read; hands back result_id)
  * Interpretation — contribution analysis, top emissions, export, dispose (read)

Safety:
  * ``BRIGHTWAY_READ_ONLY=true`` blocks every write tool.
  * Every tool returns a structured envelope (see ``responses.py``); errors carry
    ``error_code`` / ``recoverable`` / ``suggested_next_actions``.
  * A ``project`` argument selects the Brightway project per call (projects are
    the Brightway analogue of openLCA connection profiles).

Run:
  python -m brightway_mcp.server               # stdio (default)
  python -m brightway_mcp.server --http         # streamable-HTTP on :8000
"""

from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

import anyio
from fastmcp import FastMCP
from mcp.types import ToolAnnotations

from . import __version__, bw_core
from .job_runtime import ENGINE_LOCK, jobs
from .responses import success, error_body, read_only_error, BrightwayToolError
from .result_store import store

SERVER_NAME = "brightway-mcp"
INSTRUCTIONS = (
    "Tools for Brightway 2.5 life-cycle assessment, organized by ISO 14040/44 phase. "
    "Typical flow: list_projects -> list_databases -> search_activities -> "
    "run_lca (returns a result_id) -> contribution_analysis(result_id). "
    "Pass `project` to target a specific Brightway project. "
    "create_database / write_activities mutate data and honor read-only mode. "
    "Modern MCP 2026-07-28 clients may run project setup/import, multi-method, "
    "Monte Carlo, comparative, and supply-chain tools as native Tasks when enabled. "
    "Older clients can use the *_async compatibility tools and poll get_job_status / "
    "get_job_result. Call dispose_result when finished with a result_id."
)

NATIVE_TASKS_ENABLED = os.getenv("BRIGHTWAY_NATIVE_TASKS_ENABLED", "false").lower() in (
    "1", "true", "yes", "on"
)
NATIVE_TASKS_CONCURRENCY = max(1, int(os.getenv("BRIGHTWAY_NATIVE_TASKS_CONCURRENCY", "1")))

mcp = FastMCP(name=SERVER_NAME, version=__version__, instructions=INSTRUCTIONS)
if NATIVE_TASKS_ENABLED:
    from fastmcp_tasks import TasksExtension

    mcp.add_extension(TasksExtension(concurrency=NATIVE_TASKS_CONCURRENCY))


def _tool_title(name: str) -> str:
    return name.replace("_", " ").title()


def _read_registration(name: str, *, task: bool = False):
    return mcp.tool(
        name=name,
        task=task,
        annotations=ToolAnnotations(
            title=_tool_title(name),
            readOnlyHint=True,
            destructiveHint=False,
            openWorldHint=False,
        ),
    )


def _write_registration(name: str, *, task: bool = False):
    return mcp.tool(
        name=name,
        task=task,
        annotations=ToolAnnotations(
            title=_tool_title(name),
            readOnlyHint=False,
            openWorldHint=False,
        ),
    )


def read_tool(fn):
    """Advertise a tool that does not mutate the Brightway project or filesystem."""
    return _read_registration(fn.__name__)(fn)


def write_tool(fn):
    """Advertise a tool that can mutate Brightway data or the filesystem."""
    return _write_registration(fn.__name__)(fn)


def destructive_tool(fn):
    """Advertise a tool that intentionally invalidates or removes state."""
    return mcp.tool(
        annotations=ToolAnnotations(
            title=_tool_title(fn.__name__),
            readOnlyHint=False,
            destructiveHint=True,
            openWorldHint=False,
        )
    )(fn)


def read_only() -> bool:
    return os.getenv("BRIGHTWAY_READ_ONLY", "").lower() in ("1", "true", "yes")


def _guard(fn, *args, **kwargs) -> Dict[str, Any]:
    """Run a bw_core call under the process-wide project lock and envelope errors."""
    try:
        with ENGINE_LOCK:
            return success(fn(*args, **kwargs))
    except Exception as exc:  # noqa: BLE001 - envelope every failure
        return error_body(exc)


async def _offload_sync(fn, *args, **kwargs) -> Dict[str, Any]:
    """Run a synchronous public tool in a worker thread for native MCP Tasks."""
    return await anyio.to_thread.run_sync(lambda: fn(*args, **kwargs))


# ===========================================================================
# Phase 1 — Goal & Scope (read-only)
# ===========================================================================

@read_tool
def health_check() -> Dict[str, Any]:
    """Package versions + a quick environment sanity summary. Call this first to
    confirm the server and Brightway stack are working."""
    return _guard(bw_core.health_check)


@read_tool
def list_projects() -> Dict[str, Any]:
    """List all Brightway projects available on this machine."""
    return _guard(lambda: {"projects": bw_core.list_projects()})


@read_tool
def list_databases(project: str) -> Dict[str, Any]:
    """List databases in a project (with activity counts)."""
    def run():
        bw_core.use_project(project)
        return {"project": project, "databases": bw_core.list_databases(),
                "biosphere": bw_core.biosphere_name()}
    return _guard(run)


@read_tool
def database_stats(project: str, database: str) -> Dict[str, Any]:
    """Exchange/activity counts for one database."""
    def run():
        bw_core.use_project(project)
        return bw_core.database_stats(database)
    return _guard(run)


@read_tool
def search_activities(project: str, database: str, query: str,
                      limit: int = 10) -> Dict[str, Any]:
    """Case-insensitive substring search over activity names in a database."""
    def run():
        bw_core.use_project(project)
        hits = bw_core.search_activities(database, query, limit)
        return {"count": len(hits), "activities": hits}
    return _guard(run)


@read_tool
def list_methods(project: str, filter: Optional[List[str]] = None,
                 limit: int = 50) -> Dict[str, Any]:
    """List LCIA methods, optionally filtered by substrings (all must match).
    Example: filter=['IPCC','GWP100']."""
    def run():
        bw_core.use_project(project)
        methods = bw_core.list_methods(filter, limit)
        return {"count": len(methods), "methods": methods}
    return _guard(run)


@read_tool
def search_biosphere(project: str, query: str, limit: int = 10,
                     categories: Optional[List[str]] = None) -> Dict[str, Any]:
    """Search elementary flows in the biosphere database by name substring. Use
    this to find the exact flow name to link an emission in write_activities.
    Pass categories like ['air'] to disambiguate compartment."""
    def run():
        bw_core.use_project(project)
        hits = bw_core.search_biosphere(query, limit, categories)
        return {"count": len(hits), "flows": hits}
    return _guard(run)


@read_tool
def get_activity(project: str, database: str, code: Optional[str] = None,
                 name: Optional[str] = None) -> Dict[str, Any]:
    """Inspect one activity's full exchange list (by code or name). Use this to
    understand a process before editing or calculating on it."""
    def run():
        bw_core.use_project(project)
        act = bw_core.get_activity(database, code=code, name=name)
        return bw_core.activity_detail(act)
    return _guard(run)


# ===========================================================================
# Phase 2 — Inventory (write; honors read-only)
# ===========================================================================

@write_tool
def create_database(project: str, name: str, overwrite: bool = False) -> Dict[str, Any]:
    """Create (or overwrite) an empty foreground database. WRITE."""
    if read_only():
        return read_only_error("create_database")

    def run():
        bw_core.ensure_project(project)
        return bw_core.create_database(name, overwrite)
    return _guard(run)


@write_tool
def write_activities(project: str, database: str,
                     activities: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Upsert activities by code while preserving unrelated database entries. WRITE.

    Each activity: {code, name, unit, exchanges:[{input, amount, type, [categories]}]}.
    `input` is [database, code] for a technosphere link, a bare code for an internal
    link, or a flow name when type='biosphere' (resolved against the biosphere db;
    pass `categories` like ['air'] to disambiguate). A production exchange is added
    automatically if you omit one. Existing activities with matching codes are
    replaced; other activities remain. Use create_database(overwrite=true) to clear
    a foreground database deliberately.
    """
    if read_only():
        return read_only_error("write_activities")

    def run():
        bw_core.ensure_project(project)
        return bw_core.write_activities(database, activities)
    return _guard(run)


def setup_project(project: str, source: str = "ecoinvent-3.10-biosphere",
                  overwrite: bool = False) -> Dict[str, Any]:
    """Bootstrap a project with a free biosphere + LCIA methods (via a remote
    prepared project). WRITE. No-ops if already set up. Network required only
    when it actually installs. This is the usual first step on a fresh machine."""
    if read_only():
        return read_only_error("setup_project")
    return _guard(bw_core.setup_project, project, source=source, overwrite=overwrite)


@_write_registration("setup_project", task=NATIVE_TASKS_ENABLED)
async def _setup_project_mcp(project: str, source: str = "ecoinvent-3.10-biosphere",
                             overwrite: bool = False) -> Dict[str, Any]:
    return await _offload_sync(setup_project, project, source, overwrite)


@write_tool
def setup_project_async(project: str, source: str = "ecoinvent-3.10-biosphere",
                        overwrite: bool = False) -> Dict[str, Any]:
    """Start project bootstrap as a bounded background job and return a job_id."""
    if read_only():
        return read_only_error("setup_project_async")
    return jobs.submit(
        "setup_project",
        lambda: setup_project(project=project, source=source, overwrite=overwrite),
    )


@write_tool
def set_uncertainty(project: str, database: str, code: Optional[str] = None,
                    name: Optional[str] = None, scale: float = 0.15,
                    distribution: str = "lognormal",
                    input_filter: Optional[str] = None) -> Dict[str, Any]:
    """Attach an uncertainty distribution to an activity's non-production
    exchanges so run_monte_carlo has something to sample. WRITE.
    distribution: lognormal | normal | uniform | triangular."""
    if read_only():
        return read_only_error("set_uncertainty")

    def run():
        bw_core.use_project(project)
        act = bw_core.get_activity(database, code=code, name=name)
        return bw_core.set_uncertainty(act, scale=scale, distribution=distribution,
                                       input_filter=input_filter)
    return _guard(run)


def import_lcia_methods(project: str, zip_path: str,
                        drop_unlinked: bool = True) -> Dict[str, Any]:
    """Import an openLCA JSON-LD LCIA method pack (e.g. a local ecoinvent LCIA
    zip) into a project. WRITE. Patches the bw2io strategy quirks these packs
    trip; drops CFs whose flows aren't in the biosphere when drop_unlinked."""
    if read_only():
        return read_only_error("import_lcia_methods")
    return _guard(bw_core.import_lcia_methods, project, zip_path,
                  drop_unlinked=drop_unlinked)


@_write_registration("import_lcia_methods", task=NATIVE_TASKS_ENABLED)
async def _import_lcia_methods_mcp(project: str, zip_path: str,
                                   drop_unlinked: bool = True) -> Dict[str, Any]:
    return await _offload_sync(import_lcia_methods, project, zip_path, drop_unlinked)


@write_tool
def import_lcia_methods_async(project: str, zip_path: str,
                              drop_unlinked: bool = True) -> Dict[str, Any]:
    """Start LCIA-method import as a background job and return a job_id."""
    if read_only():
        return read_only_error("import_lcia_methods_async")
    return jobs.submit(
        "import_lcia_methods",
        lambda: import_lcia_methods(
            project=project, zip_path=zip_path, drop_unlinked=drop_unlinked
        ),
    )


# ===========================================================================
# Phase 3 — Impact assessment (read; stores a result)
# ===========================================================================

@read_tool
def run_lca(project: str, database: str, method: List[str],
            code: Optional[str] = None, name: Optional[str] = None,
            amount: float = 1.0) -> Dict[str, Any]:
    """Run an LCA for one activity + one method. Returns a compact summary and a
    `result_id` for follow-up interpretation tools."""
    def run():
        bw_core.use_project(project)
        act = bw_core.get_activity(database, code=code, name=name)
        m = bw_core.resolve_method(method)
        lca, score, unit = bw_core.run_lca(act, m, amount)
        stored = store.add(lca, project=project,
                           demand={str(act.key): amount}, method=m,
                           score=score, unit=unit,
                           context={"activity": act.get("name")})
        return {"result_id": stored.result_id, "score": score, "unit": unit,
                "activity": act.get("name"), "method": list(m), "amount": amount}
    return _guard(run)


def run_multi_method(project: str, database: str, methods: List[List[str]],
                     code: Optional[str] = None, name: Optional[str] = None,
                     amount: float = 1.0) -> Dict[str, Any]:
    """Score one activity across several methods efficiently (factorize once)."""
    def run():
        bw_core.use_project(project)
        act = bw_core.get_activity(database, code=code, name=name)
        rows = bw_core.multi_method(act, [tuple(m) for m in methods], amount)
        return {"activity": act.get("name"), "results": rows}
    return _guard(run)


@_read_registration("run_multi_method", task=NATIVE_TASKS_ENABLED)
async def _run_multi_method_mcp(project: str, database: str, methods: List[List[str]],
                                code: Optional[str] = None, name: Optional[str] = None,
                                amount: float = 1.0) -> Dict[str, Any]:
    return await _offload_sync(
        run_multi_method, project, database, methods, code, name, amount
    )


@read_tool
def run_multi_method_async(project: str, database: str, methods: List[List[str]],
                           code: Optional[str] = None, name: Optional[str] = None,
                           amount: float = 1.0) -> Dict[str, Any]:
    """Run a potentially large multi-method study in the background."""
    return jobs.submit(
        "run_multi_method",
        lambda: run_multi_method(
            project=project, database=database, methods=methods,
            code=code, name=name, amount=amount,
        ),
    )


def run_monte_carlo(project: str, database: str, method: List[str],
                    code: Optional[str] = None, name: Optional[str] = None,
                    iterations: int = 500, amount: float = 1.0,
                    seed: Optional[int] = None) -> Dict[str, Any]:
    """Monte Carlo LCA using each exchange's stored uncertainty. Returns summary
    statistics (median + 5/95 percentiles). Set uncertainty first with
    set_uncertainty, or scores will not vary. Pass a seed for reproducible runs."""
    def run():
        bw_core.use_project(project)
        act = bw_core.get_activity(database, code=code, name=name)
        m = bw_core.resolve_method(method)
        stats = bw_core.monte_carlo(act, m, iterations, amount, seed=seed)
        stats.update({"activity": act.get("name"), "method": list(m)})
        return stats
    return _guard(run)


@_read_registration("run_monte_carlo", task=NATIVE_TASKS_ENABLED)
async def _run_monte_carlo_mcp(project: str, database: str, method: List[str],
                               code: Optional[str] = None, name: Optional[str] = None,
                               iterations: int = 500, amount: float = 1.0,
                               seed: Optional[int] = None) -> Dict[str, Any]:
    return await _offload_sync(
        run_monte_carlo, project, database, method, code, name,
        iterations, amount, seed,
    )


@read_tool
def run_monte_carlo_async(project: str, database: str, method: List[str],
                          code: Optional[str] = None, name: Optional[str] = None,
                          iterations: int = 500, amount: float = 1.0,
                          seed: Optional[int] = None) -> Dict[str, Any]:
    """Start Monte Carlo LCA as a background job and return immediately."""
    return jobs.submit(
        "run_monte_carlo",
        lambda: run_monte_carlo(
            project=project, database=database, method=method,
            code=code, name=name, iterations=iterations, amount=amount, seed=seed,
        ),
    )


def compare_activities(project: str, alternatives: List[Dict[str, Any]],
                       methods: List[List[str]]) -> Dict[str, Any]:
    """Comparative LCA: score several activities across several methods (the
    classic comparative-study grid). alternatives: list of
    {database, code|name, [label]}. Returns a tidy list of rows."""
    def run():
        bw_core.use_project(project)
        rows = bw_core.compare_activities(alternatives, [tuple(m) for m in methods])
        return {"count": len(rows), "results": rows}
    return _guard(run)


@_read_registration("compare_activities", task=NATIVE_TASKS_ENABLED)
async def _compare_activities_mcp(project: str, alternatives: List[Dict[str, Any]],
                                  methods: List[List[str]]) -> Dict[str, Any]:
    return await _offload_sync(compare_activities, project, alternatives, methods)


@read_tool
def compare_activities_async(project: str, alternatives: List[Dict[str, Any]],
                             methods: List[List[str]]) -> Dict[str, Any]:
    """Run a comparative LCA grid as a background job."""
    return jobs.submit(
        "compare_activities",
        lambda: compare_activities(
            project=project, alternatives=alternatives, methods=methods
        ),
    )


# ===========================================================================
# Phase 4 — Interpretation (read; operates on a stored result)
# ===========================================================================

def _get_stored(result_id: str):
    stored = store.get(result_id)
    if stored is None:
        raise BrightwayToolError(
            f"Unknown result_id {result_id!r}.", error_code="UNKNOWN_RESULT",
            suggested_next_actions=["Run run_lca first; result_ids are per session."],
        )
    return stored


@read_tool
def contribution_analysis(result_id: str, limit: int = 10) -> Dict[str, Any]:
    """Top contributing processes for a stored result."""
    def run():
        stored = _get_stored(result_id)
        return {"result_id": result_id, "total": stored.score, "unit": stored.unit,
                "top_processes": bw_core.top_processes(stored.lca, limit)}
    return _guard(run)


@read_tool
def top_emissions(result_id: str, limit: int = 10) -> Dict[str, Any]:
    """Top contributing elementary flows (emissions/resources) for a stored result."""
    def run():
        stored = _get_stored(result_id)
        return {"result_id": result_id, "total": stored.score, "unit": stored.unit,
                "top_emissions": bw_core.top_emissions(stored.lca, limit)}
    return _guard(run)


def supply_chain(project: str, database: str, method: List[str],
                 code: Optional[str] = None, name: Optional[str] = None,
                 amount: float = 1.0, max_level: int = 3,
                 cutoff: float = 0.02) -> Dict[str, Any]:
    """Recursive supply-chain contribution as a bounded tree; each node reports
    its cumulative share of the total score. Best for foreground/small systems
    (max_level + cutoff bound the recursion)."""
    def run():
        bw_core.use_project(project)
        act = bw_core.get_activity(database, code=code, name=name)
        m = bw_core.resolve_method(method)
        return bw_core.supply_chain(act, m, amount, max_level, cutoff)
    return _guard(run)


@_read_registration("supply_chain", task=NATIVE_TASKS_ENABLED)
async def _supply_chain_mcp(project: str, database: str, method: List[str],
                            code: Optional[str] = None, name: Optional[str] = None,
                            amount: float = 1.0, max_level: int = 3,
                            cutoff: float = 0.02) -> Dict[str, Any]:
    return await _offload_sync(
        supply_chain, project, database, method, code, name,
        amount, max_level, cutoff,
    )


@read_tool
def supply_chain_async(project: str, database: str, method: List[str],
                       code: Optional[str] = None, name: Optional[str] = None,
                       amount: float = 1.0, max_level: int = 3,
                       cutoff: float = 0.02) -> Dict[str, Any]:
    """Run bounded recursive supply-chain analysis as a background job."""
    return jobs.submit(
        "supply_chain",
        lambda: supply_chain(
            project=project, database=database, method=method,
            code=code, name=name, amount=amount, max_level=max_level, cutoff=cutoff,
        ),
    )


@write_tool
def export_result(result_id: str, path: str, limit: int = 25) -> Dict[str, Any]:
    """Write a stored result's process-contribution table to a CSV file. WRITE
    (to the filesystem); honors read-only mode."""
    if read_only():
        return read_only_error("export_result")

    def run():
        stored = _get_stored(result_id)
        return bw_core.export_result_csv(stored.lca, path, limit)
    return _guard(run)


@destructive_tool
def dispose_result(result_id: str) -> Dict[str, Any]:
    """Drop a stored result from the registry."""
    return _guard(lambda: {"result_id": result_id, "disposed": store.dispose(result_id)})


@read_tool
def get_job_status(job_id: str) -> Dict[str, Any]:
    """Return the state of a background Brightway job."""
    return jobs.status(job_id)


@read_tool
def get_job_result(job_id: str, field: Optional[str] = None,
                   offset: int = 0, limit: int = 50) -> Dict[str, Any]:
    """Retrieve a completed job result; page a top-level list field when needed."""
    return jobs.result(job_id, field=field, offset=offset, limit=limit)


@read_tool
def list_jobs(limit: int = 20) -> Dict[str, Any]:
    """List recent Brightway background jobs, newest first."""
    return jobs.list_jobs(limit)


@destructive_tool
def cancel_job(job_id: str) -> Dict[str, Any]:
    """Cancel a queued job; running Brightway work is not force-killed."""
    return jobs.cancel(job_id)


@destructive_tool
def dispose_job(job_id: str) -> Dict[str, Any]:
    """Remove a terminal job and its stored compatibility result."""
    return jobs.dispose(job_id)


# ===========================================================================
# Resources & prompt
# ===========================================================================

@mcp.resource("brightway://projects")
def projects_resource() -> str:
    import json
    return json.dumps(bw_core.list_projects(), indent=2)


@mcp.resource("brightway://methods/{project}")
def methods_resource(project: str) -> str:
    import json
    bw_core.use_project(project)
    return json.dumps(bw_core.list_methods(limit=200), indent=2)


@mcp.prompt
def lca_walkthrough(product: str = "a product") -> str:
    """Guided ISO 14040/44 LCA walkthrough prompt."""
    return (
        f"Guide me through a Brightway LCA of {product} following ISO 14040/44:\n"
        "0. Setup: health_check, then setup_project if no biosphere exists yet.\n"
        "1. Goal & scope: confirm functional unit, boundary, and method "
        "(list_methods); find emission flows with search_biosphere.\n"
        "2. Inventory: create_database + write_activities for the foreground; "
        "inspect with get_activity; set_uncertainty for a stochastic study.\n"
        "3. Impact: run_lca (note the result_id), run_multi_method for several "
        "categories, compare_activities for a comparative study, run_monte_carlo "
        "if uncertainty is set.\n"
        "4. Interpretation: contribution_analysis, top_emissions, and supply_chain "
        "on the result; export_result to CSV.\n"
        "Report the functional unit alongside every number."
    )


# ===========================================================================
# Entry point
# ===========================================================================

def main(argv: Optional[List[str]] = None) -> None:
    argv = list(sys.argv[1:] if argv is None else argv)
    if "--http" in argv:
        port = int(os.getenv("PORT", "8000"))
        mcp.run(transport="http", host="127.0.0.1", port=port)
    else:
        mcp.run()  # stdio


if __name__ == "__main__":
    main()
