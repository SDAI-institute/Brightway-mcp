# Tutorial 01 â€” The Brightway Data Model & the Math of LCA

**Companion notebook:** [01_ecosystem_and_lca_math.ipynb](01_ecosystem_and_lca_math.ipynb)

This is the most important tutorial in the set. Once you see how Brightway's
objects map onto the matrix algebra of LCA, everything else â€” imports, LCIA,
contribution analysis, Monte Carlo â€” becomes obvious.

## 1. The data model: four nested layers

```
Project  ("bw25-tutorials")            â† isolated workspace
â””â”€â”€ Database  ("biosphere3", "my_db")  â† a named collection of nodes
    â””â”€â”€ Activity / Node                â† a process or an elementary flow
        â””â”€â”€ Exchange / Edge            â† a quantified link between two nodes
```

- **Activity (node)** â€” either a *process* (something that produces a product:
  "steel production", 1 kg) or an *elementary flow* (an exchange with nature:
  "Carbon dioxide, fossil, to air"). Identified by `(database, code)`.
- **Exchange (edge)** â€” "this activity consumes/emits *amount* of *that node*".
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

- **A â€” technosphere matrix** (products Ã— processes, square): `A[i, j]` = net
  amount of product *i* produced (+) or consumed (âˆ’) by one unit of process *j*.
- **B â€” biosphere matrix** (elementary flows Ã— processes): `B[k, j]` = amount of
  elementary flow *k* exchanged with nature per unit of process *j*.
- **f â€” demand vector**: the functional unit, e.g. "1 unit of product P".

**Life Cycle Inventory (LCI):** find the process scaling vector **s** such that
the system delivers exactly the demand:

```
A Â· s = f      â†’      s = Aâ»Â¹ Â· f
g = B Â· s      (total inventory of elementary flows)
```
