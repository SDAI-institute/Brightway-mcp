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
