# Scripts

Helpers for loading **local, licensed** data into Brightway. Neither is needed
for the tutorials or case studies (those run on free data) — they exist to bring
in your own ecoinvent assets. Full context:
[../docs/using_your_databases.md](../docs/using_your_databases.md).

Run them with the repo's venv Python:
`..\.venv\Scripts\python.exe scripts\<name>.py ...`

## `import_openlca_lcia.py`

Import a local openLCA **JSON-LD LCIA method pack** (the `*_LCIA_Methods*.zip`
files in `SDAI- Ecosystem\databases\`) into a Brightway project. Patches the
three bw2io strategy quirks these ecoinvent packs trip, links CFs to the
project's biosphere by id, and drops the ~10–12% of CFs whose flows aren't in
that biosphere.

```powershell
.\.venv\Scripts\python.exe scripts\import_openlca_lcia.py `
    --zip "..\databases\ecoinvent\ecoinvent_v3_10_LCIA_Methods_2024_01_14.zip" `
    --project bw25-tutorials
```

- **Prereq:** the target project must already have a biosphere database (the
  tutorial project does).
- **Verified** on the ecoinvent 3.10 pack → 614 methods / ~170k CFs; an imported
  `EF v3.0 GWP100` method computes correctly. Older packs (3.9.1, 3.6) have
  further structural quirks and may not import cleanly.
- Same logic is exposed as the MCP tool `import_lcia_methods`.

## `import_ecoinvent.py`

Download the ecoinvent **inventory** (the process database, ecospold2) directly
from ecoinvent using your ecoinvent website / Nexus login. This is the clean path
for the LCI data — the `.zolca` files in `databases\` are openLCA's Derby format
and are NOT readable by Brightway.

```powershell
$env:ECOINVENT_USERNAME = "you@psu.edu"
$env:ECOINVENT_PASSWORD = "..."
.\.venv\Scripts\python.exe scripts\import_ecoinvent.py `
    --version 3.10 --system-model cutoff --project ecoinvent-3.10
```

- Credentials are read from environment variables only — never hard-code or
  commit them. The script exits cleanly if they're absent.
- Requires the `ecoinvent_interface` package (already in `requirements.txt`).
- Downloads a few hundred MB the first time; cached afterward.
