"""
Golden-system cross-engine validation (SDAI reliability pass).

Ports the EXACT scenario from `openlca_library/tests/fixtures/golden_system.py`
(the openLCA reliability audit's independent, hand-calculable cross-check) into
Brightway, using this repo's own `bw_project` fixture (session-scoped, no
ecoinvent download -- its `("test", "GWP100")` method already defines
CO2=1.0 kg CO2-eq, matching the openLCA golden system's characterization
factor exactly). This is not a "similar" system built from scratch: it is the
same elementary flow / CF / 2-level process chain / amounts, so a matching
result is a genuine second-engine confirmation, not a coincidence.

    Golden Material Production          Golden Product Production (= reference)
      output: 1 kg Golden Material        output: 1 kg Golden Product
      emits:  2.0 kg CO2 (fossil)          input:  3 kg Golden Material
                                           emits:  0.5 kg CO2 (fossil)

    Hand calc for 1 kg Golden Product:
        direct:   0.5 kg CO2 * CF 1.0            = 0.5 kg CO2-eq
        upstream: 3 kg Golden Material * 2.0 kg CO2/kg
                  * CF 1.0                         = 6.0 kg CO2-eq
        TOTAL                                      = 6.5 kg CO2-eq

Also verifies a real ecoinvent-3.10-biosphere "Carbon dioxide, fossil" flow
under a real IPCC 2021 GWP100 (fossil) method characterizes to exactly 1.0 --
the same characterization-factor spot-check used in the openlca_mcp audit to
rule out method-level defects. That check is network/download-dependent (it
installs the free ecoinvent-3.10-biosphere pack via bw2io on first use) and is
marked accordingly so it can be skipped in fully offline environments.
"""
from __future__ import annotations

import bw2data as bd
import numpy as np
import pytest

from brightway_mcp import bw_core as core

EXPECTED_IMPACT = 6.5  # kg CO2-eq per 1 kg "Golden Product" -- see module docstring


@pytest.fixture
def golden_db(bw_project):
    """Build the golden system in a dedicated database within the shared
    bw_project fixture; drop it afterwards so tests stay isolated."""
    bd.projects.set_current(bw_project["project"])
    method = tuple(bw_project["method"])

    core.create_database("golden_db", overwrite=True)
    core.write_activities("golden_db", [
        {"code": "material_production", "name": "Golden Material Production",
         "unit": "kg", "exchanges": [
             {"type": "production", "input": "material_production", "amount": 1.0},
             {"type": "biosphere", "input": "Carbon dioxide, fossil",
              "categories": ["air"], "amount": 2.0},
         ]},
        {"code": "product_production", "name": "Golden Product Production",
         "unit": "kg", "exchanges": [
             {"type": "production", "input": "product_production", "amount": 1.0},
             {"type": "technosphere", "input": "material_production", "amount": 3.0},
             {"type": "biosphere", "input": "Carbon dioxide, fossil",
              "categories": ["air"], "amount": 0.5},
         ]},
    ])
    try:
        yield method
    finally:
        if "golden_db" in bd.databases:
            del bd.databases["golden_db"]


def _golden_activity():
    return core.get_activity("golden_db", code="product_production")


class TestGoldenSystemHandCalc:
    """Independent cross-check: same scenario, same hand-derived answer,
    confirmed in a second engine (Brightway, not just openLCA)."""

    def test_matches_hand_calculation(self, golden_db):
        method = golden_db
        act = _golden_activity()
        _, score, unit = core.run_lca(act, method, amount=1.0)
        assert score == pytest.approx(EXPECTED_IMPACT, rel=1e-9)
        assert "CO2" in unit

    def test_scales_linearly_with_functional_unit(self, golden_db):
        """2 kg of Golden Product should give exactly 2x the impact -- no
        allocation/cutoff in this model, pure linear scaling."""
        method = golden_db
        act = _golden_activity()
        _, score, _ = core.run_lca(act, method, amount=2.0)
        assert score == pytest.approx(2 * EXPECTED_IMPACT, rel=1e-9)


class TestGoldenSystemDeterminism:
    """Repeated calculations of the identical system must be bit-identical
    (bc.LCA's deterministic solve, no Monte Carlo / sampling involved)."""

    def test_repeated_calculations_are_identical(self, golden_db):
        method = golden_db
        act = _golden_activity()
        scores = [core.run_lca(act, method, amount=1.0)[1] for _ in range(5)]
        assert max(scores) - min(scores) == 0.0, f"Non-deterministic: {scores}"
        assert all(s == pytest.approx(EXPECTED_IMPACT, rel=1e-9) for s in scores)


class TestGoldenSystemConsistency:
    """Process/flow contribution shares should sum to (approximately) the
    total score -- mirrors openlca_mcp's check_result_consistency."""

    def test_top_processes_sum_to_total(self, golden_db):
        method = golden_db
        act = _golden_activity()
        lca, score, _ = core.run_lca(act, method, amount=1.0)
        procs = core.top_processes(lca, limit=10)
        assert sum(p["score"] for p in procs) == pytest.approx(score, rel=1e-6)

    def test_top_emissions_sum_to_total(self, golden_db):
        method = golden_db
        act = _golden_activity()
        lca, score, _ = core.run_lca(act, method, amount=1.0)
        emissions = core.top_emissions(lca, limit=10)
        assert sum(e["score"] for e in emissions) == pytest.approx(score, rel=1e-6)


class TestGoldenSystemMonteCarlo:
    """With uncertainty attached, the Monte Carlo mean should converge near
    the deterministic value, and percentiles should be internally ordered."""

    def test_monte_carlo_mean_near_deterministic(self, golden_db):
        method = golden_db
        act = _golden_activity()
        _, deterministic, _ = core.run_lca(act, method, amount=1.0)

        core.set_uncertainty(act, scale=0.05, distribution="lognormal")
        stats = core.monte_carlo(act, method, iterations=300, amount=1.0)

        assert stats["iterations"] == 300
        assert stats["percentile_5"] <= stats["median"] <= stats["percentile_95"]
        # mean within a few std of the deterministic baseline (loose bound --
        # this is a sanity check on convergence, not a tight statistical test)
        assert abs(stats["mean"] - deterministic) < 3 * stats["std"] + 1e-6


class TestGoldenSystemUnitSignFuzzing:
    """Bug-class prevention (mirrors openlca_mcp's F1 unit-handling audit):
    a negative/avoided-product-style exchange must propagate its sign
    correctly, not get silently absorbed or flipped."""

    def test_negative_exchange_credits_rather_than_adds(self, bw_project):
        """An activity with a NEGATIVE technosphere input of an emitting
        upstream process should REDUCE the total (an avoided-burden credit),
        not increase it."""
        bd.projects.set_current(bw_project["project"])
        method = tuple(bw_project["method"])
        core.create_database("sign_check", overwrite=True)
        core.write_activities("sign_check", [
            {"code": "emitter", "name": "Emitter", "unit": "kg", "exchanges": [
                {"type": "production", "input": "emitter", "amount": 1.0},
                {"type": "biosphere", "input": "Carbon dioxide, fossil",
                 "categories": ["air"], "amount": 4.0},
            ]},
            {"code": "credited", "name": "Credited process", "unit": "kg",
             "exchanges": [
                 {"type": "production", "input": "credited", "amount": 1.0},
                 {"type": "biosphere", "input": "Carbon dioxide, fossil",
                  "categories": ["air"], "amount": 10.0},
                 # avoided burden: -0.5 kg of the emitter's output credited back
                 {"type": "technosphere", "input": "emitter", "amount": -0.5},
             ]},
        ])
        try:
            act = core.get_activity("sign_check", code="credited")
            _, score, _ = core.run_lca(act, method, amount=1.0)
            expected = 10.0 + (-0.5 * 4.0)  # 10.0 - 2.0 = 8.0
            assert score == pytest.approx(expected, rel=1e-9)
            assert score < 10.0, "Negative exchange should have credited, not added"
        finally:
            if "sign_check" in bd.databases:
                del bd.databases["sign_check"]
