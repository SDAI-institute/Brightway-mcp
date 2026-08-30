"""FastMCP server exposing Brightway 2.5 as agent tools, organized by ISO phase.

Tool groups (mirroring the sibling ``openlca_mcp``):
  * Goal & scope   â€” projects, databases, search activities, list methods (read)
  * Inventory      â€” create database, write activities (write)
  * Impact         â€” run LCA, multi-method, Monte Carlo (read; hands back result_id)
  * Interpretation â€” contribution analysis, top emissions, export, dispose (read)

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
# Phase 1 â€” Goal & Scope (read-only)
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
# Phase 2 â€” Inventory (write; honors read-only)
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
