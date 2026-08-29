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
