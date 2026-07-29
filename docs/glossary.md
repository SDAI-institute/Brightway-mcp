# Glossary — LCA & Brightway Terms

## LCA concepts (ISO 14040/44)

- **Life Cycle Assessment (LCA)** — quantifying the environmental impacts of a
  product/service across its life cycle (raw materials → manufacturing → use →
  end-of-life).
- **Functional unit (FU)** — the quantified service the study is about
  ("1000 servings of coffee", "1 MJ of fuel"). All results are per FU. The FU is
  the single most important scoping choice; comparisons are only valid at equal FU.
- **System boundary** — what is included/excluded (cradle-to-gate,
  cradle-to-grave, gate-to-gate).
- **Foreground** — the system you model yourself (your product/plant).
- **Background** — generic upstream data taken from a database (ecoinvent, USEEIO).
- **LCI (Life Cycle Inventory)** — the list of all elementary flows (emissions,
  resources) crossing the boundary, per FU. In matrix terms: `g = B·A⁻¹·f`.
- **LCIA (Life Cycle Impact Assessment)** — translating inventory into impact
  category indicators via characterization. `h = C·g`.
- **Midpoint vs endpoint** — midpoint = an impact category near the emission
  (e.g. kg CO₂-eq climate change); endpoint = modeled damage (e.g. DALYs, species-years).
- **Characterization factor (CF)** — how much one unit of a flow contributes to
  an impact category (e.g. CH₄ = 29.8 kg CO₂-eq under GWP100).
- **GWP100** — Global Warming Potential, 100-year horizon; the standard climate metric.
- **Allocation** — splitting burdens between co-products (by mass, energy,
  economic value). **Substitution / system expansion** — instead crediting the
  avoided burden of what a co-product displaces.
- **Attributional vs consequential** — accounting the impacts *of* a system vs
  the impacts *caused by a decision* about it.
- **Contribution / hotspot analysis** — attributing the total to processes or flows.
- **Sensitivity analysis** — how outputs respond to input changes (tornado, OAT).
- **Uncertainty analysis** — propagating input distributions to output
  distributions (Monte Carlo).
- **Pedigree matrix** — ecoinvent's scheme for turning data-quality scores into
  lognormal uncertainty.

## Brightway objects

- **Project** — an isolated workspace; holds databases, methods, parameters.
- **Database** — a named collection of nodes (activities/flows).
- **Activity / Node** — a process (produces a product) or an elementary flow.
- **Exchange / Edge** — a quantified link between nodes; `type` ∈
  {production, technosphere, biosphere}.
- **biosphere3 / biosphere db** — the database of elementary flows (~4,700).
  In the 2.5 prepared project it's named `ecoinvent-3.10-biosphere`.
- **Method** — an LCIA method: a list of (flow, CF) pairs + metadata, keyed by a
  hierarchical tuple.
- **Technosphere matrix (A)** — products × processes; the economy's structure.
- **Biosphere matrix (B)** — elementary flows × processes; exchanges with nature.
- **Characterization matrix (C)** — impact categories × flows; the CFs.
- **Supply vector (s)** — how much each process runs to satisfy the demand.
- **Datapackage** — the 2.5 portable bundle of matrix data (`bw_processing`);
  replaces legacy pickled arrays and enables scenarios.

## Brightway packages

| Package | Role |
|---------|------|
| `bw2data` | storage: projects, databases, activities, exchanges, methods, parameters |
| `bw2calc` | the calculator: matrices, LCA solve, Monte Carlo |
| `bw2io` | import/export: Excel, ecospold, SimaPro, ecoinvent, remote projects |
| `bw2analyzer` | interpretation: contribution & supply-chain analysis |
| `bw_processing` | writes datapackages (matrix storage) |
| `matrix_utils` | assembles matrices from datapackages |
| `stats_arrays` | uncertainty distribution definitions |
| `bw_graph_tools` | supply-chain graph traversal (Sankey data) |

## Free data sources used here

- **USEEIO** — US environmentally-extended input-output database (sectors, free).
- **Forwast** — EU IO database (free).
- **ecoinvent** — the standard process database (license required; optional here).
