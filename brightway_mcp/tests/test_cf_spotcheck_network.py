"""
Characterization-factor spot-check against a REAL background database
(ecoinvent-3.10-biosphere via bw2io's free remote install).

Unlike the rest of the test suite (which uses the fully offline, no-download
`bw_project` fixture), this test calls `setup_project`, which downloads the
free ecoinvent-3.10-biosphere + methods pack (~17 MB) on first use. It is kept
separate and OPT-IN (not part of the default `pytest` run) so CI and offline
development aren't affected -- run explicitly with:

    pytest tests/test_cf_spotcheck_network.py -m network

Purpose: rule out method-level defects (mirrors the openlca_mcp audit's
fossil-CO2=1.0 characterization spot-check) -- confirms Brightway's own real
characterization data agrees with the same convention the synthetic golden
system assumes (CO2 fossil = 1.0 kg CO2-eq under a GWP100 method).

Uses a dedicated project name and deletes it (data + registry entry) in a
fixture teardown, so it never pollutes the user's real Brightway projects.
"""
from __future__ import annotations

import bw2data as bd
import pytest

from brightway_mcp import bw_core as core

PROJECT = "sdai_cf_spotcheck"
METHOD = ("IPCC 2021 no LT", "climate change: fossil no LT",
          "global warming potential (GWP100) no LT")

pytestmark = pytest.mark.network


@pytest.fixture(scope="module")
def real_biosphere_project():
    try:
        core.setup_project(PROJECT, source="ecoinvent-3.10-biosphere")
    except Exception as exc:  # pragma: no cover - network/environment dependent
        pytest.skip(f"Could not set up real biosphere project (offline?): {exc}")
    try:
        yield
    finally:
        if PROJECT in {p.name for p in bd.projects}:
            bd.projects.delete_project(PROJECT, delete_dir=True)


def test_fossil_co2_characterizes_to_one(real_biosphere_project):
    """1 kg of the real ecoinvent 'Carbon dioxide, fossil' flow, under a real
    IPCC 2021 GWP100 (fossil) method, must characterize to exactly 1.0 --
    the universal GWP convention the synthetic golden system assumes."""
    bd.projects.set_current(PROJECT)
    method = core.resolve_method(list(METHOD))

    core.create_database("cf_check", overwrite=True)
    core.write_activities("cf_check", [
        {"code": "probe", "name": "CF probe", "unit": "kg", "exchanges": [
            {"type": "biosphere", "input": "Carbon dioxide, fossil",
             "categories": ["air"], "amount": 1.0},
        ]},
    ])
    try:
        act = core.get_activity("cf_check", code="probe")
        _, score, unit = core.run_lca(act, method, amount=1.0)
        assert score == pytest.approx(1.0, rel=1e-9)
        assert "CO2" in unit
    finally:
        if "cf_check" in bd.databases:
            del bd.databases["cf_check"]
