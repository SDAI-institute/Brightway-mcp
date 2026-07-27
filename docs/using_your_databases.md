# Using the databases in `SDAI- Ecosystem\databases\` with Brightway

**Short version:** the files in `D:\01code\Projects\SDAI- Ecosystem\databases\`
are all **openLCA-native format** — Brightway cannot read any of them directly.
But you hold a genuine **ecoinvent 3.10 academic license**, which unlocks the
clean Brightway path via a direct download. Details below.

## What's actually in that folder

| File / folder | Format | Brightway-importable? |
|---------------|--------|-----------------------|
| `*.zolca` (elcd_bottles, needs_18, bioenergiedat_18, USDA_1901009, LCIA_2_0_2, …) | openLCA internal **Apache Derby database** (zipped) | ❌ No reader exists |
| `ecoinvent/*_LCIA_Methods*.zip`, `ecoinvent_*_lcia_methods.zip`, `openLCA LCIA Methods 2.4.3 …zip` | openLCA **JSON-LD** LCIA method packs | ✅ **Yes** — via `scripts/import_openlca_lcia.py` (see below) |
| `*.zolca` LCIA methods (ecoinvent3_1, 2_2, 3_5, 3_3 …) | openLCA **Derby** method exports | ❌ Derby, not JSON-LD |
| `ecoinvent/Caleb/*.pdf` | license confirmations + notes (ecoinvent 3.10 academic, Nexus order) | n/a — proof of license |
| `PSILICA/` | PSILCA docs (xlsx, pdf, txt) — social LCA, openLCA | ❌ openLCA-only |

Two things share the "openLCA method" label but are **different formats**:
- **`.zolca` method files** (ecoinvent3_1_lcia_methods, etc.) = zipped Derby DB → ❌ unreadable.
- **`.zip` method packs** (`*_LCIA_Methods*.zip`) = openLCA **JSON-LD** →
  ✅ importable (see path 4). Peek inside: JSON-LD packs have
  `lcia_methods/`, `flows/`, `openlca.json`; Derby zips have `seg0/`, `_olca_`.

The `.zolca` *database* files (elcd_bottles, needs, USDA, …) are Derby directories
zipped up — not JSON-LD, not ecospold. No Brightway importer exists for them.

## The three real paths

### 1. ecoinvent → Brightway (recommended — you have the license)

Brightway needs the **ecospold2** version of ecoinvent, which it downloads
straight from ecoinvent's servers using your **ecoinvent website / Nexus login**
(the account your academic license is attached to — *not* anything inside the
`.zolca`). Use the helper script:

```powershell
$env:ECOINVENT_USERNAME = "you@psu.edu"
$env:ECOINVENT_PASSWORD = "..."
.\.venv\Scripts\python.exe scripts\import_ecoinvent.py --version 3.10 --system-model cutoff --project ecoinvent-3.10
```

This creates a Brightway project with the full ecoinvent 3.10 cutoff database +
its biosphere + LCIA methods. After it's in, the tutorials and case studies work
against real background data — e.g. in CS1 replace the hand-built `elec`/steel
surrogates with ecoinvent market processes. `ecoinvent_interface` (installed) and
`bw2io.import_ecoinvent_release` do the work; the download is a few hundred MB
the first time and is cached for reuse.

### 2. openLCA `.zolca` databases → stay in openLCA

For the non-ecoinvent databases (ELCD bottles, NEEDS, USDA, bioenergiedat,
PSILCA), the practical answer is: **use them where they already work** — in
openLCA, through your existing `openlca_mcp` server. They were exported from
openLCA and belong there. This is why the ecosystem has both backends
(see [bw_vs_openlca.md](bw_vs_openlca.md)).

If you specifically need one of them *inside* Brightway, the only supported
bridge is: open the `.zolca` in openLCA Desktop → **export to Excel**
(or ecospold2) → import that with `bw2io.ExcelImporter` /
`SingleOutputEcospold2Importer` (tutorial 04). That's a manual, per-database
conversion; do it only when a study truly needs that dataset in Brightway.

### 4. openLCA JSON-LD **LCIA method** packs → Brightway (works, with a caveat)

The `*_LCIA_Methods*.zip` files (ecoinvent 3.9/3.10, openLCA 2.4.3) are openLCA
**JSON-LD** — Brightway's `JSONLDLCIAImporter` reads them. But that importer has
two bugs against these specific ecoinvent exports (a missing `lastChange` key and
`parameters` arriving as a list). The shipped helper patches both and imports:

```powershell
.\.venv\Scripts\python.exe scripts\import_openlca_lcia.py `
    --zip "..\databases\ecoinvent\ecoinvent_v3_10_LCIA_Methods_2024_01_14.zip" `
    --project bw25-tutorials
```

**Verified:** this imports **614 LCIA methods (~170k characterization factors)**
— EF v3.0, EF v3.1, IPCC, ReCiPe, etc. — into a project, and an imported
`EF v3.0 climate change GWP100` method computes correctly on the tutorial widget
(2.925 kg CO₂-eq, matching the hand calc).

**Caveat:** ~10–12% of CFs reference elementary flows not present in the base
`ecoinvent-3.10-biosphere` (flows added in newer method revisions). The helper
`drop_unlinked()`s those and writes the rest — standard practice, but note that a
handful of exotic flows won't be characterized. The target project must already
have a biosphere database.

This gives you the **LCIA methods** locally without any download. It does **not**
give you the ecoinvent *inventory* (the process database) — that still comes from
path 1.

### 3. Free background (no license, already wired)

Everything in this hub already runs on free data
(`bw2io.remote.install_project`, USEEIO). Nothing above is required to use the
tutorials or case studies — the ecoinvent path just makes the case-study numbers
realistic.

## Which to use when

- **Screening / teaching / reproducible demos** → free data (path 3) — already set up.
- **Realistic Brightway studies** → ecoinvent via credentials (path 1).
- **ELCD/NEEDS/USDA/PSILCA-specific work** → openLCA + `openlca_mcp` (path 2).

## Note on credentials & privacy

Enter ecoinvent credentials only via environment variables, never commit them,
and never paste them into a notebook cell that gets saved with output. The import
script reads them from the environment and exits cleanly if they're absent.
