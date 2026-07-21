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
> instead â€” it is also the officially recommended 2.5 path:

```python
import bw2data as bd, bw2io as bi

if "bw25-tutorials" not in bd.projects:
    bi.remote.install_project("ecoinvent-3.10-biosphere", "bw25-tutorials")
bd.projects.set_current("bw25-tutorials")
