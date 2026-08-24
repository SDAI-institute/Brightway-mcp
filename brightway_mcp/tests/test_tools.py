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
    assert out["error_code"] == "UNKNOWN_METHOD"


def test_read_only_blocks_writes(bw_project, monkeypatch):
    monkeypatch.setenv("BRIGHTWAY_READ_ONLY", "true")
    out = server.create_database(bw_project["project"], "should_not_exist")
    assert out["success"] is False
    assert out["error_code"] == "READ_ONLY"
    out2 = server.write_activities(bw_project["project"], "fg_test", [])
    assert out2["error_code"] == "READ_ONLY"


def test_write_activities_roundtrip(bw_project, monkeypatch):
    monkeypatch.delenv("BRIGHTWAY_READ_ONLY", raising=False)
    server.create_database(bw_project["project"], "written_db", overwrite=True)
    out = server.write_activities(bw_project["project"], "written_db", [
        {"code": "box", "name": "box", "unit": "kilogram", "exchanges": [
            {"input": "Carbon dioxide, fossil", "amount": 0.5, "type": "biosphere",
             "categories": ["air"]},
        ]},
    ])
    assert out["success"] and out["written"] == 1 and out["total"] == 1
    lca = server.run_lca(bw_project["project"], "written_db",
                         method=bw_project["method"], code="box")
    assert lca["success"] and abs(lca["score"] - 0.5) < 1e-4

    # A second write must preserve the first activity instead of replacing the DB.
    out2 = server.write_activities(bw_project["project"], "written_db", [
        {"code": "box2", "name": "box2", "unit": "kilogram", "exchanges": [
            {"input": "Carbon dioxide, fossil", "amount": 1.0, "type": "biosphere",
             "categories": ["air"]},
        ]},
    ])
    assert out2["success"] and out2["written"] == 1
    assert out2["preserved_existing"] == 1 and out2["total"] == 2

    lca_old = server.run_lca(bw_project["project"], "written_db",
                             method=bw_project["method"], code="box")
    lca_new = server.run_lca(bw_project["project"], "written_db",
                             method=bw_project["method"], code="box2")
    assert lca_old["success"] and abs(lca_old["score"] - 0.5) < 1e-4
    assert lca_new["success"] and abs(lca_new["score"] - 1.0) < 1e-4


# --- v0.2 tools -----------------------------------------------------------

def test_health_check(bw_project):
    out = server.health_check()
    assert out["success"] and out["bw2data"].startswith("4")


def test_search_biosphere(bw_project):
    out = server.search_biosphere(bw_project["project"], "Carbon dioxide")
    assert out["success"] and out["count"] >= 1
    assert any("Carbon dioxide" in f["name"] for f in out["flows"])
    # category filter
    out2 = server.search_biosphere(bw_project["project"], "Carbon dioxide",
                                   categories=["air"])
    assert out2["success"] and out2["count"] >= 1


def test_get_activity_detail(bw_project):
    out = server.get_activity(bw_project["project"], "fg_test", code="widget")
    assert out["success"]
    assert out["name"] == "widget"
    types = {e["type"] for e in out["exchanges"]}
    assert "production" in types and "technosphere" in types


def test_setup_project_already_set_up(bw_project):
    # fixture project has a biosphere; setup should no-op without network
    out = server.setup_project(bw_project["project"])
    assert out["success"] and out["created"] is False
    assert "already set up" in out.get("note", "")


def test_compare_activities(bw_project):
    out = server.compare_activities(
        bw_project["project"],
        alternatives=[
            {"database": "fg_test", "code": "widget", "label": "widget"},
            {"database": "fg_test", "code": "widget_lite", "label": "lite"},
        ],
        methods=[bw_project["method"]],
    )
    assert out["success"] and out["count"] == 2
    scores = {r["alternative"]: r["score"] for r in out["results"]}
    # lite uses less steel -> lower score
    assert scores["lite"] < scores["widget"]


def test_supply_chain(bw_project):
    out = server.supply_chain(bw_project["project"], "fg_test",
                              method=bw_project["method"], code="widget",
                              max_level=3, cutoff=0.01)
    assert out["success"]
    assert out["tree"]["name"] == "widget"
    assert abs(out["tree"]["share"] - 1.0) < 1e-6
    assert out["tree"]["children"]  # steel + electricity


def test_set_uncertainty_enables_monte_carlo(bw_project, monkeypatch):
    monkeypatch.delenv("BRIGHTWAY_READ_ONLY", raising=False)
    su = server.set_uncertainty(bw_project["project"], "fg_test", code="elec",
                                scale=0.2)
    assert su["success"] and su["exchanges_updated"] >= 1
    mc = server.run_monte_carlo(bw_project["project"], "fg_test",
                                method=bw_project["method"], code="widget",
                                iterations=30)
    assert mc["success"] and mc["std"] > 0


def test_monte_carlo_seed_is_reproducible(bw_project, monkeypatch):
    monkeypatch.delenv("BRIGHTWAY_READ_ONLY", raising=False)
    server.set_uncertainty(bw_project["project"], "fg_test", code="elec", scale=0.2)
    kwargs = {
        "project": bw_project["project"],
        "database": "fg_test",
        "method": bw_project["method"],
        "code": "widget",
        "iterations": 30,
        "seed": 20260814,
    }
    first = server.run_monte_carlo(**kwargs)
    second = server.run_monte_carlo(**kwargs)
    assert first["success"] and second["success"]
    assert first["seed"] == second["seed"] == 20260814
    for key in ("mean", "std", "median", "percentile_5", "percentile_95"):
        assert first[key] == second[key]


def test_export_result_csv(bw_project, tmp_path, monkeypatch):
    monkeypatch.delenv("BRIGHTWAY_READ_ONLY", raising=False)
    lca = server.run_lca(bw_project["project"], "fg_test",
                         method=bw_project["method"], code="widget")
    csv_path = str(tmp_path / "contrib.csv")
    out = server.export_result(lca["result_id"], csv_path)
    assert out["success"] and out["rows"] >= 1
    assert os.path.exists(csv_path)
    with open(csv_path) as f:
        assert "rank,score,share" in f.read()


def test_read_only_blocks_new_writes(bw_project, monkeypatch):
    monkeypatch.setenv("BRIGHTWAY_READ_ONLY", "true")
    for out in [
        server.setup_project(bw_project["project"]),
        server.set_uncertainty(bw_project["project"], "fg_test", code="elec"),
        server.import_lcia_methods(bw_project["project"], "nope.zip"),
        server.export_result("res_x", "x.csv"),
    ]:
        assert out["success"] is False and out["error_code"] == "READ_ONLY"


def test_import_lcia_missing_file(bw_project, monkeypatch):
    monkeypatch.delenv("BRIGHTWAY_READ_ONLY", raising=False)
    out = server.import_lcia_methods(bw_project["project"], "does_not_exist.zip")
    assert out["success"] is False and out["error_code"] == "NOT_FOUND"
