# Glossary â€” LCA & Brightway Terms

## LCA concepts (ISO 14040/44)

- **Life Cycle Assessment (LCA)** â€” quantifying the environmental impacts of a
  product/service across its life cycle (raw materials â†’ manufacturing â†’ use â†’
  end-of-life).
- **Functional unit (FU)** â€” the quantified service the study is about
  ("1000 servings of coffee", "1 MJ of fuel"). All results are per FU. The FU is
  the single most important scoping choice; comparisons are only valid at equal FU.
- **System boundary** â€” what is included/excluded (cradle-to-gate,
  cradle-to-grave, gate-to-gate).
- **Foreground** â€” the system you model yourself (your product/plant).
- **Background** â€” generic upstream data taken from a database (ecoinvent, USEEIO).
- **LCI (Life Cycle Inventory)** â€” the list of all elementary flows (emissions,
  resources) crossing the boundary, per FU. In matrix terms: `g = BÂ·Aâ»Â¹Â·f`.
- **LCIA (Life Cycle Impact Assessment)** â€” translating inventory into impact
  category indicators via characterization. `h = CÂ·g`.
- **Midpoint vs endpoint** â€” midpoint = an impact category near the emission
  (e.g. kg COâ‚‚-eq climate change); endpoint = modeled damage (e.g. DALYs, species-years).
- **Characterization factor (CF)** â€” how much one unit of a flow contributes to
  an impact category (e.g. CHâ‚„ = 29.8 kg COâ‚‚-eq under GWP100).
- **GWP100** â€” Global Warming Potential, 100-year horizon; the standard climate metric.
- **Allocation** â€” splitting burdens between co-products (by mass, energy,
  economic value). **Substitution / system expansion** â€” instead crediting the
  avoided burden of what a co-product displaces.
- **Attributional vs consequential** â€” accounting the impacts *of* a system vs
  the impacts *caused by a decision* about it.
