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
