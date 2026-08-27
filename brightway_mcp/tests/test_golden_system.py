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
