"""In-process demo of the Brightway MCP tools (no MCP transport needed).

Drives the full ISO-phase chain against a temp project + fixture database, the
same way the test suite does, and prints each envelope. Run:

    python examples/demo.py
"""
import os
import tempfile
import json


def main():
    tmp = tempfile.mkdtemp(prefix="bw-mcp-demo-")
    os.environ["BRIGHTWAY_DIR"] = tmp
    os.environ.setdefault("BRIGHTWAY_READ_ONLY", "false")

    import bw2data as bd
    project = "bw-mcp-demo"
    bd.projects.set_current(project)

    # tiny biosphere + method + foreground
    bd.Database("biosphere_demo").write({
        ("biosphere_demo", "co2"): {"name": "Carbon dioxide, fossil",
            "categories": ("air",), "type": "emission", "unit": "kilogram"},
    })
    m = bd.Method(("demo", "GWP100")); m.register(unit="kg CO2-eq")
    m.write([(("biosphere_demo", "co2"), 1.0)])
    bd.Database("fg_demo").write({
        ("fg_demo", "elec"): {"name": "electricity", "unit": "kilowatt hour",
            "exchanges": [
                {"input": ("fg_demo", "elec"), "amount": 1.0, "type": "production"},
                {"input": ("biosphere_demo", "co2"), "amount": 0.9, "type": "biosphere"}]},
        ("fg_demo", "widget"): {"name": "widget", "unit": "kilogram", "exchanges": [
            {"input": ("fg_demo", "widget"), "amount": 1.0, "type": "production"},
            {"input": ("fg_demo", "elec"), "amount": 2.0, "type": "technosphere"}]},
    })

    from brightway_mcp import server

    def show(label, env):
        print(f"\n### {label}")
        print(json.dumps(env, indent=2)[:800])

    show("health_check", server.health_check())
    show("list_projects", server.list_projects())
    show("list_databases", server.list_databases(project))
    show("search_biosphere", server.search_biosphere(project, "Carbon dioxide"))
    show("search_activities", server.search_activities(project, "fg_demo", "widget"))
    show("get_activity", server.get_activity(project, "fg_demo", code="widget"))
    show("list_methods", server.list_methods(project, filter=["GWP100"]))
    lca = server.run_lca(project, "fg_demo", method=["demo", "GWP100"], code="widget")
    show("run_lca", lca)
    show("compare_activities", server.compare_activities(
        project,
        alternatives=[{"database": "fg_demo", "code": "widget"},
                      {"database": "fg_demo", "code": "elec", "label": "elec"}],
        methods=[["demo", "GWP100"]]))
    show("supply_chain", server.supply_chain(project, "fg_demo",
                                             method=["demo", "GWP100"], code="widget"))
    show("contribution_analysis", server.contribution_analysis(lca["result_id"]))
    show("top_emissions", server.top_emissions(lca["result_id"]))
    show("dispose_result", server.dispose_result(lca["result_id"]))

    import shutil
    shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()
