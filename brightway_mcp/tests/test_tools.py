"""End-to-end tests of the Brightway MCP tools against a fixture project.

Calls the tool functions directly (they return plain envelope dicts), exercising
the full goal-scope -> inventory -> impact -> interpretation chain, plus the
read-only guard.
"""
import os

import pytest

from brightway_mcp import server, bw_core
from brightway_mcp.result_store import store


@pytest.mark.asyncio
async def test_native_task_metadata_switch():
    expected = "optional" if server.NATIVE_TASKS_ENABLED else "forbidden"
    for name in (
        "setup_project", "import_lcia_methods", "run_multi_method",
        "run_monte_carlo", "compare_activities", "supply_chain",
    ):
        tool = await server.mcp.get_tool(name)
        assert tool.task_config.mode == expected


def test_list_projects_includes_fixture(bw_project):
    out = server.list_projects()
    assert out["success"] is True
    names = [p["name"] for p in out["projects"]]
    assert bw_project["project"] in names


def test_list_databases(bw_project):
    out = server.list_databases(bw_project["project"])
    assert out["success"]
    names = [d["name"] for d in out["databases"]]
    assert "fg_test" in names and "biosphere_test" in names
    assert out["biosphere"] == "biosphere_test"


def test_database_stats(bw_project):
    out = server.database_stats(bw_project["project"], "fg_test")
    assert out["success"]
    assert out["activities"] == 4  # elec, steel, widget, widget_lite
    assert out["production_exchanges"] == 4


def test_search_activities(bw_project):
    out = server.search_activities(bw_project["project"], "fg_test", "steel")
    assert out["success"] and out["count"] == 1
    assert out["activities"][0]["name"] == "steel"


def test_list_methods(bw_project):
    out = server.list_methods(bw_project["project"], filter=["GWP100"])
    assert out["success"] and out["count"] >= 1


def test_run_lca_matches_hand_calc(bw_project):
    out = server.run_lca(bw_project["project"], "fg_test",
                         method=bw_project["method"], code="widget")
    assert out["success"], out
    # hand calc: 0.9*(2.5*0.5 + 1.0) + 1.8*0.5 = 2.925
    assert abs(out["score"] - 2.925) < 1e-4
    assert out["unit"] == "kg CO2-eq"
    assert out["result_id"] in store


def test_contribution_and_emissions(bw_project):
    lca = server.run_lca(bw_project["project"], "fg_test",
                         method=bw_project["method"], code="widget")
    rid = lca["result_id"]
    ca = server.contribution_analysis(rid, limit=5)
    assert ca["success"] and ca["top_processes"]
    te = server.top_emissions(rid, limit=5)
    assert te["success"] and te["top_emissions"]
    # CO2 should dominate
    assert "Carbon dioxide" in te["top_emissions"][0]["name"]


def test_multi_method(bw_project):
    out = server.run_multi_method(bw_project["project"], "fg_test",
                                  methods=[bw_project["method"]], code="widget")
    assert out["success"] and len(out["results"]) == 1


def test_dispose_result(bw_project):
    lca = server.run_lca(bw_project["project"], "fg_test",
                         method=bw_project["method"], code="widget")
    rid = lca["result_id"]
    out = server.dispose_result(rid)
    assert out["success"] and out["disposed"] is True
    assert rid not in store


def test_unknown_project_error(bw_project):
    out = server.list_databases("no-such-project")
    assert out["success"] is False
    assert out["error_code"] == "UNKNOWN_PROJECT"
    assert out["suggested_next_actions"]


def test_unknown_method_error(bw_project):
    out = server.run_lca(bw_project["project"], "fg_test",
                         method=["nope", "nope"], code="widget")
    assert out["success"] is False
