# Scripts

Helpers for loading **local, licensed** data into Brightway. Neither is needed
for the tutorials or case studies (those run on free data) â€” they exist to bring
in your own ecoinvent assets. Full context:
[../docs/using_your_databases.md](../docs/using_your_databases.md).

Run them with the repo's venv Python:
`..\.venv\Scripts\python.exe scripts\<name>.py ...`

## `import_openlca_lcia.py`

Import a local openLCA **JSON-LD LCIA method pack** (the `*_LCIA_Methods*.zip`
files in `SDAI- Ecosystem\databases\`) into a Brightway project. Patches the
three bw2io strategy quirks these ecoinvent packs trip, links CFs to the
project's biosphere by id, and drops the ~10â€“12% of CFs whose flows aren't in
that biosphere.

```powershell
.\.venv\Scripts\python.exe scripts\import_openlca_lcia.py `
