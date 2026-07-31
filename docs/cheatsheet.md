# Brightway 2.5 Cheatsheet

One-page API reference. `import bw2data as bd, bw2calc as bc, bw2io as bi, bw2analyzer as ba`.

## Projects
```python
bd.projects.set_current("name")     # activate (CREATES if missing!)
bd.projects.current                  # active project name
bd.projects.dir                      # on-disk folder
[p.name for p in bd.projects]        # list
bd.projects.copy_project("new")      # duplicate + switch
bd.projects.delete_project("x", delete_dir=True)
```

## Biosphere & setup (this hub)
```python
bi.remote.install_project("ecoinvent-3.10-biosphere", "proj")  # free flows+methods
BIOSPHERE = next(d for d in bd.databases if "biosphere" in d.lower())  # NOT 'biosphere3'!
```

## Databases
```python
bd.databases                         # registry (dict-like)
db = bd.Database("name")             # handle (creates nothing)
db.register()                        # create empty
db.write({(db, code): {...}})        # bulk write (replaces db)
db.process()                         # refresh calc arrays after edits
len(db); db.random(); db.search("x")
del bd.databases["name"]             # delete
```

## Activities & exchanges
```python
act = bd.get_node(database="db", code="c")   # or name="..."
act = bd.get_activity(("db", "c"))           # by key
act["name"], act["unit"], act.key, act.id
act.exchanges(); act.technosphere(); act.biosphere(); act.production()
act.upstream()                                # reverse edges (consumers)
act.copy(code="c2"); act.delete()
# incremental
a = db.new_activity(code="c", name="n", unit="u"); a.save()
a.new_exchange(input=other, amount=2.0, type="technosphere").save()
```

Exchange `type`: `production` (self output), `technosphere` (input from process),
`biosphere` (elementary flow). Amounts are POSITIVE; Brightway signs A.

## Methods (LCIA)
```python
bd.methods                                    # registry (tuple keys)
