# Tutorial 02 â€” Projects & Data Management with bw2data

**Companion notebook:** [02_projects_and_data.ipynb](02_projects_and_data.ipynb)

This tutorial is the bw2data "driver's manual": everything you routinely do with
projects, databases, activities, and methods â€” create, search, inspect, copy,
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
names, a typo gives you a mysteriously empty workspace â€” if everything
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

1. **Incremental** (`new_activity` / `new_exchange` + `.save()`) â€” tutorial 03.
2. **Bulk write** â€” a dict keyed by `(db_name, code)`:

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
