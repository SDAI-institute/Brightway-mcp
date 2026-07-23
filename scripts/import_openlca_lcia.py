r"""Import an openLCA JSON-LD LCIA method package into a Brightway 2.5 project.

Your local `databases\` folder has several openLCA LCIA method packs as
**JSON-LD zips** (these DO have a Brightway importer, unlike the `.zolca`
database files, which are openLCA's internal Derby format and are unreadable):

  - ecoinvent/ecoinvent_v3_10_LCIA_Methods_2024_01_14.zip
  - ecoinvent/ecoinvent_3_9_1_LCIA_Methods.zip
  - ecoinvent_36_lcia_methods.zip
  - "openLCA LCIA Methods 2.4.3 2024-07-22.zip"

`bw2io`'s `JSONLDLCIAImporter` chokes on these packs out of the box (two
strategy bugs: a missing ``lastChange`` key, and ``parameters`` arriving as a
list instead of a dict). This script applies a small, contained pre-processing
patch for both, links characterization factors to the project's biosphere by id,
DROPS the fraction of CFs whose flows aren't in that biosphere (typically ~10%,
flows introduced by newer method versions), and writes the rest.

Prereq: the target project must already contain a biosphere database â€” e.g. the
tutorial project (`bw2io.remote.install_project("ecoinvent-3.10-biosphere", ...)`)
or a full ecoinvent import.

Usage (PowerShell):
    .\.venv\Scripts\python.exe scripts\import_openlca_lcia.py `
        --zip "..\databases\ecoinvent\ecoinvent_v3_10_LCIA_Methods_2024_01_14.zip" `
        --project bw25-tutorials
"""
from __future__ import annotations

import argparse
import sys
import tempfile
import zipfile
from pathlib import Path


def _patch_sections(data: dict) -> None:
    """In-place workarounds for bw2io JSON-LD LCIA strategy assumptions that
    some openLCA exports violate:
      * `lastChange` / `version` / `description` missing on methods/categories
      * `parameters` present as a list instead of a dict
