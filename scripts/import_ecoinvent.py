r"""Import an ecoinvent release into a Brightway 2.5 project (license required).

You have an ecoinvent 3.10 academic license (see
`databases/ecoinvent/Caleb/`). Brightway CANNOT read the openLCA `.zolca`
exports in that folder â€” it needs the **ecospold2** release, which this script
downloads directly from ecoinvent using your ecoinvent (Nexus/website) login.
Those credentials are the SAME account as your license, but are NOT stored in
the .zolca files; you enter them here.

Usage (PowerShell):
    $env:ECOINVENT_USERNAME = "you@psu.edu"
    $env:ECOINVENT_PASSWORD = "..."
    .\.venv\Scripts\python.exe scripts\import_ecoinvent.py --version 3.10 --system-model cutoff --project ecoinvent-3.10

Credentials are read from the environment (never hard-code them). The first run
downloads a few hundred MB and takes a while; subsequent imports into other
projects reuse the local ecoinvent_interface cache.
"""
from __future__ import annotations

import argparse
import os
import sys


def main() -> int:
    ap = argparse.ArgumentParser(description="Import an ecoinvent release into a Brightway project.")
    ap.add_argument("--version", default="3.10", help="ecoinvent version, e.g. 3.10")
    ap.add_argument("--system-model", default="cutoff",
                    choices=["cutoff", "consequential", "apos", "EN15804"],
