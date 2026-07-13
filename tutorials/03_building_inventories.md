# Tutorial 03 â€” Building Foreground Inventories in Code

**Companion notebook:** [03_building_inventories.ipynb](03_building_inventories.ipynb)

"Foreground" = the part of the system you model yourself (your product, your
plant, your supply chain decisions). "Background" = generic upstream data you
take from a database (ecoinvent, USEEIO, â€¦). This tutorial builds a complete
foreground database from scratch, links it to real `biosphere3` flows, and
**verifies the LCA result against a hand matrix calculation** â€” the
trust-but-verify pattern you should use on every model you build.

## The system we build

A simplified **electric kettle** (functional unit: 1 kettle, cradle-to-gate):

```
1 kettle  â†  1.2 kg steel  â†  2.9 kwh electricity each kg
          â†  0.4 kg plastic (PP)
          â†  0.8 kWh electricity (assembly)
```

with process emissions (linked to genuine `biosphere3` flows):

| Process | Elementary flows |
|---|---|
| electricity, coal (1 kWh) | 0.95 kg COâ‚‚-fossil, 0.0001 kg CHâ‚„-fossil, 0.002 kg SOâ‚‚ |
| steel (1 kg) | 1.9 kg COâ‚‚-fossil, 0.0008 kg PMâ‚‚.â‚… |
| polypropylene (1 kg) | 1.6 kg COâ‚‚-fossil, 0.004 kg NMVOC |
| kettle assembly | â€“ (only inputs) |

(Numbers are literature-plausible teaching values, not certified factors.)

## Finding the right biosphere flows

`biosphere3` has many variants of "Carbon dioxide" (fossil / non-fossil /
land-transformation Ã— emission compartments). Picking the wrong one means LCIA
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
