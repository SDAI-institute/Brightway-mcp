# Tutorial 01 — The Brightway Data Model & the Math of LCA

**Companion notebook:** [01_ecosystem_and_lca_math.ipynb](01_ecosystem_and_lca_math.ipynb)

This is the most important tutorial in the set. Once you see how Brightway's
objects map onto the matrix algebra of LCA, everything else — imports, LCIA,
contribution analysis, Monte Carlo — becomes obvious.

## 1. The data model: four nested layers

```
Project  ("bw25-tutorials")            ← isolated workspace
└── Database  ("biosphere3", "my_db")  ← a named collection of nodes
    └── Activity / Node                ← a process or an elementary flow
        └── Exchange / Edge            ← a quantified link between two nodes
```

- **Activity (node)** — either a *process* (something that produces a product:
  "steel production", 1 kg) or an *elementary flow* (an exchange with nature:
  "Carbon dioxide, fossil, to air"). Identified by `(database, code)`.
- **Exchange (edge)** — "this activity consumes/emits *amount* of *that node*".
  Every exchange has a `type`:

| Exchange type | Meaning | Lands in matrix |
|---------------|---------|-----------------|
| `production` | reference product output of the process | **A** (diagonal, positive) |
| `technosphere` | input from another process | **A** (off-diagonal, negative) |
| `biosphere` | emission to / extraction from nature | **B** |

> **2.5 naming:** bw2data 4 also calls these *nodes* and *edges*
> (`db.new_node()`, `node.new_edge()`); the classic `new_activity()` /
> `new_exchange()` names still work and are used throughout these tutorials.

## 2. From data model to matrices

Collect all processes as columns. Then:

- **A — technosphere matrix** (products × processes, square): `A[i, j]` = net
  amount of product *i* produced (+) or consumed (−) by one unit of process *j*.
- **B — biosphere matrix** (elementary flows × processes): `B[k, j]` = amount of
  elementary flow *k* exchanged with nature per unit of process *j*.
- **f — demand vector**: the functional unit, e.g. "1 unit of product P".

**Life Cycle Inventory (LCI):** find the process scaling vector **s** such that
the system delivers exactly the demand:

```
A · s = f      →      s = A⁻¹ · f
g = B · s      (total inventory of elementary flows)
```

**Impact assessment (LCIA):** with **C** the characterization matrix
(impact categories × elementary flows, holding the characterization factors):

```
h = C · g = C · B · A⁻¹ · f      (impact scores)
```

That one line *is* LCA. Everything else is data management and interpretation.

## 3. What Brightway does with it

When you call

```python
import bw2calc as bc
lca = bc.LCA({activity: 1}, method=("IPCC 2013", "climate change", "GWP 100a"))
lca.lci()      # builds A and B, solves A·s = f, computes g
lca.lcia()     # applies C
lca.score      # the single number: total impact
```

Brightway:

1. Collects the relevant **datapackages** (processed matrix data written when a
   database is saved — bw2data 4 handles this automatically),
2. Builds sparse matrices `lca.technosphere_matrix` (A), `lca.biosphere_matrix`
   (B), `lca.characterization_matrix` (C),
3. Solves the linear system (sparse LU factorization — no explicit inverse),
4. Exposes intermediate results: `lca.supply_array` (s), `lca.inventory` (the
   matrix `B · diag(s)`, flows *by process*), and
   `lca.characterized_inventory` (`C · B · diag(s)`, impacts by flow × process).

Those two matrices being kept *disaggregated by process* is what makes
contribution analysis (tutorial 06) essentially free.

## 4. A worked 3-process example (the notebook computes this both ways)

System: producing **1 kg of widget** requires steel; steel requires electricity;
electricity also feeds widget assembly. CO₂ is emitted by electricity and steel.

| Process (1 unit =) | Inputs | Emissions |
|---|---|---|
| electricity (1 kWh) | – | 0.9 kg CO₂ |
| steel (1 kg) | 2.5 kWh electricity | 1.8 kg CO₂ (process) |
| widget (1 kg) | 0.5 kg steel, 1.0 kWh electricity | – |

```
        elec  steel widget                    elec  steel widget
A =  [  1    -2.5  -1.0 ]  (kWh)      B = [  0.9   1.8    0  ]  (kg CO₂)
     [  0     1    -0.5 ]  (kg steel)
     [  0     0     1   ]  (kg widget)
```

For f = (0, 0, 1): s = (2.25, 0.5, 1) → g = B·s = 0.9·2.25 + 1.8·0.5 = **2.925 kg CO₂**.

The notebook solves this with plain NumPy, then builds the same system as a
Brightway database and shows `lca.score` matches to machine precision. This
cross-check pattern — *hand math vs framework* — is the single best way to trust
(and debug) your models.

## 5. Sign conventions & gotchas

- You enter all exchange amounts as **positive numbers**; Brightway applies the
  negative sign for technosphere *inputs* when building A. (An explicit
  `production` exchange of 1 is created implicitly if you don't add one.)
- A is only invertible if every product has exactly one producing process
  (square, non-singular). Import errors about "unlinked exchanges" (tutorial 04)
  are usually a violation of this.
- Loops (steel needs electricity, electricity plant needs steel) are fine —
  that's exactly what the linear solve handles; no iteration needed.

## Next

→ [02 — Projects & data management](02_projects_and_data.md): the bw2data API
for creating, inspecting, copying, and backing up all of the above.
