r"""Import an ecoinvent release into a Brightway 2.5 project (license required).

You have an ecoinvent 3.10 academic license (see
`databases/ecoinvent/Caleb/`). Brightway CANNOT read the openLCA `.zolca`
exports in that folder — it needs the **ecospold2** release, which this script
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
                    help="ecoinvent system model")
    ap.add_argument("--project", default=None,
                    help="Brightway project name (default: ecoinvent-<version>-<model>)")
    args = ap.parse_args()

    username = os.environ.get("ECOINVENT_USERNAME")
    password = os.environ.get("ECOINVENT_PASSWORD")
    if not username or not password:
        print("ERROR: set ECOINVENT_USERNAME and ECOINVENT_PASSWORD in the environment.\n"
              "These are your ecoinvent website / Nexus login (the account your\n"
              "academic license is tied to) — NOT anything stored in the .zolca files.",
              file=sys.stderr)
        return 2

    project = args.project or f"ecoinvent-{args.version}-{args.system_model}"

    import bw2data as bd
    import bw2io as bi

    bd.projects.set_current(project)
    print(f"Importing ecoinvent {args.version} ({args.system_model}) into project "
          f"'{project}' — this downloads ~hundreds of MB and takes several minutes...")

    bi.import_ecoinvent_release(
        version=args.version,
        system_model=args.system_model,
        username=username,
        password=password,
        lci=True,
        lcia=True,
    )

    print("\nDone. Databases now in this project:")
    for name in bd.databases:
        try:
            print(f"  {name}: {len(bd.Database(name))} nodes")
        except Exception:
            print(f"  {name}")
    print(f"\nLCIA methods available: {len(bd.methods)}")
    print("Use it: bd.projects.set_current(%r); ei = bd.Database('<ecoinvent db name>')" % project)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
