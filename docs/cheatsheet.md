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
[m for m in bd.methods if "IPCC" in str(m) and "GWP100" in str(m).replace(" ","")]
bd.Method(m).load()                           # [(flow_id, CF), ...]
bd.Method(m).metadata["unit"]
# custom method
my = bd.Method(("me","cat")); my.register(unit="kg CO2-eq")
my.write([(flow.key, 1.0), ...])
```

## Calculation
```python
lca = bc.LCA({act: 1}, method=m)
lca.lci()                    # build A,B; solve A·s=f
lca.lcia()                   # apply C
lca.score                    # single number
# efficient many-calc
lca.lci(factorize=True)
lca.switch_method(m2); lca.lcia()
lca.lcia(demand={act2.id: 1})   # note .id, not the object
# internals
lca.supply_array; lca.inventory; lca.characterized_inventory
lca.technosphere_matrix; lca.biosphere_matrix; lca.characterization_matrix
lca.dicts.activity[act.id]; lca.dicts.biosphere[flow.id]
```

## Uncertainty & Monte Carlo
```python
exc["uncertainty type"] = 2          # 2=lognormal,3=normal,4=uniform,5=triangular
exc["loc"] = math.log(exc["amount"]) # lognormal: loc = ln(median)!
exc["scale"] = 0.15; exc.save(); db.process()
mc = bc.LCA({act:1}, method=m, use_distributions=True); mc.lci(); mc.lcia()
scores = [mc.score for _ in zip(range(500), mc)]
```

## Parameters
```python
from bw2data.parameters import parameters, ProjectParameter, ActivityParameter
parameters.new_project_parameters([{"name":"x","amount":1.2}], overwrite=True)
exc["formula"] = "x"; exc.save()
parameters.add_exchanges_to_group("grp", act)
ActivityParameter.recalculate_exchanges("grp")
# update + cascade
for p in ProjectParameter.select().where(ProjectParameter.name=="x"): p.amount=2; p.save()
parameters.recalculate()
```

## Contribution analysis
```python
ca = ba.ContributionAnalysis()
ca.annotated_top_processes(lca, limit=10)     # [(score, supply, act), ...]
ca.annotated_top_emissions(lca, limit=10)
ba.print_recursive_calculation(act, m, amount=1, max_level=4, cutoff=0.02)
# manual cuts
lca.characterized_inventory.sum(axis=0)        # by process (columns)
lca.characterized_inventory.sum(axis=1)        # by flow (rows)
```

## Import (bw2io)
```python
imp = bi.ExcelImporter("file.xlsx")
imp.apply_strategies()                         # normalize FIRST
imp.match_database(fields=["name"])            # internal links
imp.match_database(BIOSPHERE, fields=["name","categories"])
imp.statistics()                               # (datasets, exchanges, unlinked)
list(imp.unlinked)                             # debug
if imp.statistics()[2] == 0: imp.write_database()
```
Excel gotcha: each Activity block needs a `type   process` row, or production
edges won't link. Importer reassigns codes to hashes → look up by `name`.

## Gotchas
- float32 storage → results agree to ~1e-7 relative, not machine precision.
- `set_current` creates unknown projects silently.
- lognormal `loc` = ln(median), not median.
- method tuples are exact dict keys — copy, don't type.
- biosphere db is `ecoinvent-3.10-biosphere`, not `biosphere3`.
