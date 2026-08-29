"""Test fixtures: an isolated Brightway project with a tiny fixture database.

Uses a temporary BRIGHTWAY_DIR so tests never touch the user's real projects,
and a minimal biosphere (3 flows) + a 3-process foreground so calculations run
without ecoinvent or any download.
"""
import os
import tempfile
import shutil

import pytest


@pytest.fixture(scope="session")
def bw_project():
    tmp = tempfile.mkdtemp(prefix="bw-mcp-test-")
    os.environ["BRIGHTWAY_DIR"] = tmp
    # import AFTER setting BRIGHTWAY_DIR so bw2data picks up the temp dir
    import bw2data as bd

    project = "bw-mcp-test"
    bd.projects.set_current(project)

    # --- minimal biosphere with 3 elementary flows
    bio = bd.Database("biosphere_test")
    bio.write({
        ("biosphere_test", "co2"): {
            "name": "Carbon dioxide, fossil", "categories": ("air",),
            "type": "emission", "unit": "kilogram"},
        ("biosphere_test", "ch4"): {
            "name": "Methane, fossil", "categories": ("air",),
            "type": "emission", "unit": "kilogram"},
        ("biosphere_test", "so2"): {
            "name": "Sulfur dioxide", "categories": ("air",),
            "type": "emission", "unit": "kilogram"},
    })

    # --- a GWP method: CO2=1, CH4=29.8
    method_key = ("test", "GWP100")
    m = bd.Method(method_key)
    m.register(unit="kg CO2-eq")
    m.write([(("biosphere_test", "co2"), 1.0), (("biosphere_test", "ch4"), 29.8)])

    # --- a 3-process foreground
    fg = bd.Database("fg_test")
    fg.write({
        ("fg_test", "elec"): {"name": "electricity", "unit": "kilowatt hour",
            "exchanges": [
                {"input": ("fg_test", "elec"), "amount": 1.0, "type": "production"},
                {"input": ("biosphere_test", "co2"), "amount": 0.9, "type": "biosphere"}]},
        ("fg_test", "steel"): {"name": "steel", "unit": "kilogram", "exchanges": [
            {"input": ("fg_test", "steel"), "amount": 1.0, "type": "production"},
            {"input": ("fg_test", "elec"), "amount": 2.5, "type": "technosphere"},
            {"input": ("biosphere_test", "co2"), "amount": 1.8, "type": "biosphere"}]},
        ("fg_test", "widget"): {"name": "widget", "unit": "kilogram", "exchanges": [
            {"input": ("fg_test", "widget"), "amount": 1.0, "type": "production"},
            {"input": ("fg_test", "steel"), "amount": 0.5, "type": "technosphere"},
            {"input": ("fg_test", "elec"), "amount": 1.0, "type": "technosphere"}]},
        # a second alternative for compare_activities: same product, less steel
        ("fg_test", "widget_lite"): {"name": "widget lite", "unit": "kilogram",
            "exchanges": [
                {"input": ("fg_test", "widget_lite"), "amount": 1.0, "type": "production"},
                {"input": ("fg_test", "steel"), "amount": 0.3, "type": "technosphere"},
                {"input": ("fg_test", "elec"), "amount": 1.0, "type": "technosphere"}]},
    })

    yield {"project": project, "method": list(method_key)}

    shutil.rmtree(tmp, ignore_errors=True)
