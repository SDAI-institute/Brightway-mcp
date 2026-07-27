# Using the databases in `SDAI- Ecosystem\databases\` with Brightway

**Short version:** the files in `D:\01code\Projects\SDAI- Ecosystem\databases\`
are all **openLCA-native format** â€” Brightway cannot read any of them directly.
But you hold a genuine **ecoinvent 3.10 academic license**, which unlocks the
clean Brightway path via a direct download. Details below.

## What's actually in that folder

| File / folder | Format | Brightway-importable? |
|---------------|--------|-----------------------|
| `*.zolca` (elcd_bottles, needs_18, bioenergiedat_18, USDA_1901009, LCIA_2_0_2, â€¦) | openLCA internal **Apache Derby database** (zipped) | âŒ No reader exists |
| `ecoinvent/*_LCIA_Methods*.zip`, `ecoinvent_*_lcia_methods.zip`, `openLCA LCIA Methods 2.4.3 â€¦zip` | openLCA **JSON-LD** LCIA method packs | âœ… **Yes** â€” via `scripts/import_openlca_lcia.py` (see below) |
| `*.zolca` LCIA methods (ecoinvent3_1, 2_2, 3_5, 3_3 â€¦) | openLCA **Derby** method exports | âŒ Derby, not JSON-LD |
| `ecoinvent/Caleb/*.pdf` | license confirmations + notes (ecoinvent 3.10 academic, Nexus order) | n/a â€” proof of license |
| `PSILICA/` | PSILCA docs (xlsx, pdf, txt) â€” social LCA, openLCA | âŒ openLCA-only |

Two things share the "openLCA method" label but are **different formats**:
- **`.zolca` method files** (ecoinvent3_1_lcia_methods, etc.) = zipped Derby DB â†’ âŒ unreadable.
- **`.zip` method packs** (`*_LCIA_Methods*.zip`) = openLCA **JSON-LD** â†’
  âœ… importable (see path 4). Peek inside: JSON-LD packs have
  `lcia_methods/`, `flows/`, `openlca.json`; Derby zips have `seg0/`, `_olca_`.

The `.zolca` *database* files (elcd_bottles, needs, USDA, â€¦) are Derby directories
zipped up â€” not JSON-LD, not ecospold. No Brightway importer exists for them.

## The three real paths

### 1. ecoinvent â†’ Brightway (recommended â€” you have the license)

Brightway needs the **ecospold2** version of ecoinvent, which it downloads
straight from ecoinvent's servers using your **ecoinvent website / Nexus login**
(the account your academic license is attached to â€” *not* anything inside the
`.zolca`). Use the helper script:

```powershell
$env:ECOINVENT_USERNAME = "you@psu.edu"
$env:ECOINVENT_PASSWORD = "..."
.\.venv\Scripts\python.exe scripts\import_ecoinvent.py --version 3.10 --system-model cutoff --project ecoinvent-3.10
```

This creates a Brightway project with the full ecoinvent 3.10 cutoff database +
its biosphere + LCIA methods. After it's in, the tutorials and case studies work
