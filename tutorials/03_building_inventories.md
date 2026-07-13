# Tutorial 03 — Building Foreground Inventories in Code

**Companion notebook:** [03_building_inventories.ipynb](03_building_inventories.ipynb)

"Foreground" = the part of the system you model yourself (your product, your
plant, your supply chain decisions). "Background" = generic upstream data you
take from a database (ecoinvent, USEEIO, …). This tutorial builds a complete
foreground database from scratch, links it to real `biosphere3` flows, and
**verifies the LCA result against a hand matrix calculation** — the
trust-but-verify pattern you should use on every model you build.

## The system we build

A simplified **electric kettle** (functional unit: 1 kettle, cradle-to-gate):

```
1 kettle  ←  1.2 kg steel  ←  2.9 kwh electricity each kg
          ←  0.4 kg plastic (PP)
          ←  0.8 kWh electricity (assembly)
```

with process emissions (linked to genuine `biosphere3` flows):

| Process | Elementary flows |
|---|---|
| electricity, coal (1 kWh) | 0.95 kg CO₂-fossil, 0.0001 kg CH₄-fossil, 0.002 kg SO₂ |
| steel (1 kg) | 1.9 kg CO₂-fossil, 0.0008 kg PM₂.₅ |
| polypropylene (1 kg) | 1.6 kg CO₂-fossil, 0.004 kg NMVOC |
| kettle assembly | – (only inputs) |

(Numbers are literature-plausible teaching values, not certified factors.)

## Finding the right biosphere flows

`biosphere3` has many variants of "Carbon dioxide" (fossil / non-fossil /
land-transformation × emission compartments). Picking the wrong one means LCIA
methods silently don't match it. Robust pattern:

```python
co2 = next(f for f in bd.Database("biosphere3")
           if f["name"] == "Carbon dioxide, fossil"
           and f["categories"] == ("air",))
```

Filter on **name AND categories**, and prefer the plain compartment `("air",)`
(the unspecified one) for generic emissions. The notebook wraps this in a
`find_flow()` helper you'll reuse in later tutorials.

## Two authoring styles

**Bulk-write style** (declarative — best for whole systems, used here):

```python
data = {
    ("kettle", "electricity"): {
        "name": "electricity production, coal",
        "unit": "kilowatt hour",
        "exchanges": [
            {"input": ("kettle", "electricity"), "amount": 1.0, "type": "production"},
            {"input": co2.key, "amount": 0.95, "type": "biosphere"},
            ...
        ],
    },
    ...
}
bd.Database("kettle").write(data)
```

**Incremental style** (imperative — best for scripted/parametric generation):

```python
db = bd.Database("kettle"); db.register()
elec = db.new_activity(code="electricity", name="electricity production, coal",
                       unit="kilowatt hour")
elec.save()
elec.new_exchange(input=elec, amount=1.0, type="production").save()
elec.new_exchange(input=co2, amount=0.95, type="biosphere").save()
```

> **2.5 note:** `new_node` / `new_edge` are the modern aliases. Also: `.save()`
> on both the activity *and each exchange* is mandatory in incremental style —
> forgetting it is the #1 "why is my database empty" bug.

## The hand-check

The notebook then:

1. Assembles **A** (4×4) and **B** (5×4) with NumPy from the same numbers
2. Solves `s = A⁻¹f`, `g = B·s`, `h = c·g` with hand-typed IPCC GWP factors
   (CO₂ = 1, CH₄ = 29.8 kg CO₂e/kg)
3. Runs the same calculation through `bw2calc` with the real
   `("IPCC 2013", "climate change", "global warming potential (GWP100)")` method
4. Asserts agreement (CO₂/CH₄ terms to machine precision; tiny differences can
   only come from CF values, which the notebook prints side by side)

If a model ever surprises you, reduce it to this pattern: extract
`lca.technosphere_matrix.todense()` and compare against what you *think* A
should be. The notebook shows how to map matrix rows/columns back to activities
using `lca.dicts.activity` / `lca.dicts.biosphere`.

## Multifunctionality (heads-up)

Everything here assumes one product per process (square A). Real systems have
co-products (a biorefinery makes ethanol *and* DDGS). The standard treatments —
substitution or allocation — appear in case study 2. Brightway also has
first-class multifunctional support via `multifunctional`, out of scope here.

## Pitfalls

- **Missing production exchange**: if you add none, Brightway assumes 1 unit —
  fine, but be explicit; if you add one with amount ≠ 1, all inputs are "per
  that amount".
- **Linking by tuple key**: a typo in `("kettle", "stee1")` won't fail on write —
  it fails at calculation with a "missing datapackage/unlinked" error. Use object
  references (`input=elec`) in incremental style to make typos impossible.
- **Units are metadata, not physics.** Brightway never converts units; if you
  say a process consumes 2.9 of electricity, it's 2.9 *of whatever unit the
  producing process defines*. Unit discipline is on you.

## Next

→ [04 — Importing data](04_importing_data.md): the same system from an Excel
file, plus real background databases (USEEIO, ecoinvent).
