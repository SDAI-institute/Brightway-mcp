# Tutorial 02 — Projects & Data Management with bw2data

**Companion notebook:** [02_projects_and_data.ipynb](02_projects_and_data.ipynb)

This tutorial is the bw2data "driver's manual": everything you routinely do with
projects, databases, activities, and methods — create, search, inspect, copy,
back up, delete.

## Projects

```python
import bw2data as bd

bd.projects                     # the project manager (iterable)
bd.projects.current             # name of the active project
bd.projects.set_current("x")    # switch (creates if missing!)
bd.projects.copy_project("y")   # duplicate current project as "y" and switch to it
bd.projects.delete_project("y", delete_dir=True)
bd.projects.dir                 # folder on disk of current project
```

**Habit to build:** the first executable line of every script/notebook is
`bd.projects.set_current("...")`. Since `set_current` silently *creates* unknown
names, a typo gives you a mysteriously empty workspace — if everything
"disappeared", check `bd.projects.current` first.

## Databases

```python
bd.databases                    # dict-like registry of databases in this project
db = bd.Database("my_db")       # handle (does not create anything yet)
db.register()                   # create empty database
len(db)                        # number of nodes
db.random()                     # a random activity (great for exploring)
del bd.databases["my_db"]       # delete database
```

Two ways to put data in:

1. **Incremental** (`new_activity` / `new_exchange` + `.save()`) — tutorial 03.
2. **Bulk write** — a dict keyed by `(db_name, code)`:

```python
db.write({
    ("my_db", "widget"): {
        "name": "widget production", "unit": "kilogram",
        "exchanges": [
            {"input": ("my_db", "widget"), "amount": 1, "type": "production"},
            {"input": ("my_db", "steel"),  "amount": 0.5, "type": "technosphere"},
        ],
    },
    ...
})
```

`db.write()` replaces the whole database and (re)processes it into the
datapackage used by bw2calc. After incremental edits, call `db.process()`
if you need the calculation arrays refreshed (bw2data 4 usually handles this
via signals, but an explicit `process()` after a batch of edits is cheap
insurance).

## Activities (nodes)

```python
act = bd.get_node(database="my_db", name="widget production")   # precise lookup
act = bd.get_activity(("my_db", "widget"))                       # by key
act["name"], act["unit"], act["location"]     # dict-like metadata access
act.key                                        # ("my_db", "widget")
act["code"]                                    # "widget"

for exc in act.exchanges(): ...    # all edges
act.technosphere()                 # input edges from other processes
act.biosphere()                    # elementary-flow edges
act.production()                   # reference-product edge(s)
act.upstream()                     # who consumes me? (reverse edges)

act2 = act.copy(code="widget-v2")  # duplicate incl. exchanges
act.delete()
```

Searching:

```python
db.search("steel")                          # full-text search
[a for a in db if "electric" in a["name"]]  # brute force is fine for small DBs
```

## Methods (LCIA)

```python
bd.methods                          # registry: keys are tuples
m = ("IPCC 2013", "climate change", "GWP 100a")
bd.Method(m).load()                 # [(flow_id, factor), ...]
bd.Method(m).metadata               # unit, description, ...
```

Method identifiers are **tuples** (hierarchical names). Finding one:

```python
[m for m in bd.methods if "IPCC" in str(m) and "GWP100" in str(m)]
```

## Backup & restore

```python
import bw2io
bw2io.backup_project_directory("bw25-tutorials")   # → tarball in home dir
bw2io.restore_project_directory("path/to/tarball.tar.gz", "restored-name")
```

Single databases can also be round-tripped to Excel/CSV
(`bw2io.export.write_lci_excel(db_name)`) — human-reviewable and diff-able.

## What the notebook does

1. Tours `bd.projects` (list, current, directory on disk)
2. Creates a scratch database two ways (bulk `write` vs incremental) and compares
3. Demonstrates every query pattern above on the toy widget system
4. Explores `biosphere3`: counts flows by category, finds CO₂ variants
5. Filters `bd.methods` (there are hundreds) down to IPCC / ReCiPe / EF
6. Copies an activity, edits an exchange amount, deletes, cleans up

## Pitfalls

- `bd.Database("name")` **does not create** a database — writing/registering does.
- Deleting an activity that others link to leaves **dangling edges**; delete
  consumers first, or rebuild the database with `write()`.
- `db.search()` uses a whoosh index that can lag freshly-written data; the
  list-comprehension filter is the reliable fallback.
- Everything is per-project. "My database vanished" almost always means
  "I'm in a different project".

## Next

→ [03 — Building foreground inventories](03_building_inventories.md): build the
widget system properly, linked to `biosphere3`, and verify the math.
