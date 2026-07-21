# Environment Setup

This repo uses a dedicated virtual environment with the **Brightway 2.5** stack
on Python 3.13.

## Installed & verified versions

| Package | Version |
|---|---|
| Python | 3.13.5 |
| bw2data | 4.7 |
| bw2calc | 2.5.0 |
| bw2io | 0.9.17 |
| bw2analyzer | (see requirements.txt) |
| pypardiso | fast sparse solver (MKL) |

Full pinned list: [requirements.txt](requirements.txt).

## Fresh install

```powershell
cd "D:\01code\Projects\SDAI- Ecosystem\Brightway2"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m ipykernel install --user --name brightway25 --display-name "Python (brightway25)"
```

Open notebooks with the **Python (brightway25)** kernel (already registered on
this machine).

## Biosphere & LCIA methods

> **Heads-up:** the classic `bw2io.bw2setup()` currently fails with
> bw2data 4.7 + bw2io 0.9.17 (`ValueError: Can't understand elementary flow
> identifier [...]` while writing methods). Use the **remote prepared project**
> instead — it is also the officially recommended 2.5 path:

```python
import bw2data as bd, bw2io as bi

if "bw25-tutorials" not in bd.projects:
    bi.remote.install_project("ecoinvent-3.10-biosphere", "bw25-tutorials")
bd.projects.set_current("bw25-tutorials")
```

This downloads (~once) a prepared project containing the ecoinvent 3.10
elementary-flow list and the standard LCIA method collection — free, no
ecoinvent license involved. Tutorial notebook 00 does this automatically.

> **Naming quirk that trips everyone up:** in this prepared project the
> biosphere database is named **`ecoinvent-3.10-biosphere`**, *not* the classic
> `biosphere3`. Never hard-code the name — resolve it dynamically:
> ```python
> BIOSPHERE = next(d for d in bd.databases if "biosphere" in d.lower())
> ```
> Every tutorial notebook defines this `BIOSPHERE` variable in its first cell
> and uses it everywhere. The `.md` explainers say "biosphere3" generically for
> the *concept*; the code uses the resolved name.

`bw2io.remote.get_projects()` lists other available prepared projects
(USEEIO-1.1, forwast, other biosphere versions).

## Optional: ecoinvent (license required — you have one)

You hold an ecoinvent 3.10 academic license (see
`SDAI- Ecosystem\databases\ecoinvent\Caleb\`). **Important:** the `.zolca` files
in that `databases\` folder are openLCA-format and Brightway cannot read them —
Brightway downloads the **ecospold2** release directly from ecoinvent using your
ecoinvent login. `ecoinvent_interface` is installed for this. Use the helper:

```powershell
$env:ECOINVENT_USERNAME = "you@psu.edu"
$env:ECOINVENT_PASSWORD = "..."
.\.venv\Scripts\python.exe scripts\import_ecoinvent.py --version 3.10 --system-model cutoff --project ecoinvent-3.10
```

or the underlying call:

```python
import bw2io
bw2io.import_ecoinvent_release(
    version="3.10", system_model="cutoff",
    username=os.environ["ECOINVENT_USERNAME"],
    password=os.environ["ECOINVENT_PASSWORD"],
)
```

Set credentials as environment variables — tutorial notebooks skip ecoinvent
cells cleanly when they're absent, and nothing in this repo requires them. For
the full picture of which files in `databases\` are usable and how, see
[docs/using_your_databases.md](docs/using_your_databases.md).

## Where Brightway stores data

Per-user, per-project: `%LOCALAPPDATA%\pylca\Brightway3\`. Inspect with
`bd.projects.dir`. Projects used by this repo:

- `bw25-tutorials` — all tutorial notebooks
- `cs1-bottle`, `cs2-biofuel`, `cs3-cement` — one per case study
- `bw-mcp-*` — created by MCP server tests (temporary)

## Known environment quirks

- **"No fast sparse solver found"** warning → `pypardiso` missing; it's in
  requirements.txt, so a fresh `pip install -r requirements.txt` fixes it.
- **`SimaProBlockCSVImporter` import warning** from bw2io is harmless unless you
  need SimaPro block-CSV imports (`pip install bw2io[multifunctional]`).
- Keep legacy Brightway2 (bw2data 3.x) environments separate from this one.
