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

Prereq: the target project must already contain a biosphere database — e.g. the
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
      * `impactFactors` missing on a category (older packs) — give it an empty
        list so the reformat-as-exchanges strategy doesn't KeyError.
    Validated on the ecoinvent 3.10 LCIA pack; older packs (3.9.1, 3.6) have
    further structural differences and may still not import cleanly.
    """
    for section in ("lcia_methods", "lcia_categories", "flows"):
        for obj in data.get(section, {}).values():
            obj.setdefault("lastChange", "")
            obj.setdefault("version", "00.00.000")
            obj.setdefault("description", "")
            if isinstance(obj.get("parameters"), list):
                obj["parameters"] = {}
    for cat in data.get("lcia_categories", {}).values():
        cat.setdefault("impactFactors", [])


def main() -> int:
    ap = argparse.ArgumentParser(description="Import an openLCA JSON-LD LCIA pack into Brightway.")
    ap.add_argument("--zip", required=True, help="Path to the openLCA JSON-LD LCIA .zip")
    ap.add_argument("--project", required=True, help="Target Brightway project (must have a biosphere db)")
    ap.add_argument("--keep-unlinked", action="store_true",
                    help="Do not drop CFs whose flows aren't in the biosphere (write will fail if any remain)")
    args = ap.parse_args()

    zip_path = Path(args.zip)
    if not zip_path.exists():
        print(f"ERROR: {zip_path} not found.", file=sys.stderr)
        return 2

    import bw2data as bd
    from bw2io.importers.json_ld_lcia import JSONLDLCIAImporter

    if args.project not in {p.name for p in bd.projects}:
        print(f"ERROR: project {args.project!r} does not exist. Create it and install a "
              f"biosphere first.", file=sys.stderr)
        return 2
    bd.projects.set_current(args.project)
    bio = next((d for d in bd.databases if "biosphere" in d.lower()), None)
    if bio is None:
        print(f"ERROR: project {args.project!r} has no biosphere database.", file=sys.stderr)
        return 2

    before = len(bd.methods)
    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(tmp)
        imp = JSONLDLCIAImporter(tmp)
        _patch_sections(imp.data)
        imp.apply_strategies()
        imp.match_biosphere_by_id(bio)
        if not imp.all_linked and not args.keep_unlinked:
            imp.drop_unlinked()
        imp.write_methods(overwrite=True)

    after = len(bd.methods)
    print(f"Imported into {args.project!r}: {after - before} new methods "
          f"(biosphere: {bio}). Total methods now: {after}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
