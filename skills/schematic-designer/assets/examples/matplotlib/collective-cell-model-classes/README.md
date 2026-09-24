# Modeling choices for collective cell dynamics

[Editable Python source](matplotlib-figure.py) ·
[Finished PDF](figures/collective-cell-model-classes.pdf) ·
[Finished SVG](figures/collective-cell-model-classes.svg) ·
[Library](../../../../references/library.md)

## Scientific caption

**Complementary choices in modeling collective cell dynamics.** The panels show
what a model can retain explicitly: particle positions and interactions (A),
cell states and behavioral rules (B), lattice occupancy or cell identity (C),
individual cell shape or spatially averaged density (D), and possible couplings
between cells, chemical fields, and extracellular matrix (E). These choices can
be combined.
An agent model can use particles, a lattice, or deformable cells; a continuous
field can describe one cell rather than an averaged tissue. Retained state,
spatial detail, and coarse-graining therefore require separate decisions. Panel
order does not rank accuracy, biological validity, or computational cost. All
geometry and fields are illustrative constructions, not simulation results or
calibrated biological measurements.

## What each panel represents

- **A — Particle dynamics.** Cell centers interact through a specified central
  force, $\mathbf{F}_i=k(r-r_0)\hat{\mathbf{e}}_{ij}$ and
  $\mathbf{F}_j=-\mathbf{F}_i$, with $k>0$. Here $r$ is the center separation,
  $r_0$ the equilibrium separation, and $\hat{\mathbf{e}}_{ij}$ is the unit vector
  from $i$ to $j$.
  Repulsion ($r<r_0$) and attraction ($r>r_0$) use the same illustrative law.
  The optional active term $v_0\mathbf{p}_i$ is a propulsion velocity, with
  speed $v_0$ and unit polarity $\mathbf{p}_i$; it is not an additional force.
  Cell-center mechanics and self-propulsion are distinct modeling choices
  ([Osborne et al., 2017](https://doi.org/10.1371/journal.pcbi.1005387);
  [ten Hagen et al., 2011](https://arxiv.org/abs/1005.1343)).
- **B — Cell states and rules.** Individual cells retain state and respond to
  their surroundings through specified rules: sensing, movement, division,
  secretion, and changes of state. These possible behaviors can occur
  simultaneously; they are not a mandatory sequence or a separate spatial
  representation
  ([Ghaffarizadeh et al., 2018](https://doi.org/10.1371/journal.pcbi.1005991)).
- **C — Lattice representations.** The cellular automaton example assigns at
  most one cell to each site. In the cellular Potts example, several sites carry
  the same cell identity and together represent that cell. Connected shapes are
  drawn here; connectivity must be enforced if a chosen Potts update rule can
  fragment cells. The two conventions are shown separately
  ([Osborne et al., 2017](https://doi.org/10.1371/journal.pcbi.1005387)).
- **D — Fields at different levels of description.** A separate phase field
  $\phi_i$ can retain the shape and identity of each cell, with values near one
  inside and zero outside; the displayed boundary is $\phi_i=1/2$
  ([Nonomura, 2012](https://doi.org/10.1371/journal.pone.0033501)). The density
  example instead uses $\rho(\mathbf{x})=\sum_i K_h(\mathbf{x}-\mathbf{x}_i)$,
  where $K_h$ is a normalized two-dimensional Gaussian kernel and the black dots
  mark the source positions. Its width $h$ sets the averaging scale; it does
  not resolve cell boundaries. This illustrative density construction is not a
  phase-field simulation or a derived tissue evolution equation.
- **E — Cell–environment coupling.** Discrete cells can respond to a chemical
  field and contribute sources or sinks to it; agent–continuum coupling is
  exemplified by
  [Ghaffarizadeh et al. (2018)](https://doi.org/10.1371/journal.pcbi.1005991).
  The fixed-length arrow shows the gradient direction of the prescribed
  illustrative field $c=\exp(0.9x+0.6y)$ in dimensionless plotting coordinates;
  its length does not encode gradient magnitude. The dashed link to the
  extracellular matrix (ECM), labeled “Possible coupling,” indicates a possible
  mechanical dependence, not a computed force or traction. The panel presents
  ingredients for coupling, not a complete closed model or PhysiCell output.

## Design lesson

Use this example to compare representations that differ in the variables they
retain. Align headings and use a consistent visual grammar, while preserving
scientifically meaningful distinctions inside each panel. Separate alternative
conventions, define every arrow, and make each field or interaction agree with
its stated construction. Use labels and geometry as well as color.

After adapting it, check that cells, lattice sites, fields, and coupling links
have unambiguous meanings. Do not turn panel order into an implied progression
from simple to accurate, or treat more geometric detail as evidence of greater
biological validity.

## Build

Run from the skill root, replacing the output path with an approved directory:

```bash
python3 scripts/build_example.py collective-cell-model-classes --output-dir /private/tmp/schematic-cell-model-classes
```

The Matplotlib PGF build writes `collective-cell-model-classes.pdf` and
`collective-cell-model-classes.svg`, with CMU/LaTeX and native TikZ heads. Follow
the [shared build and trust requirements](../../../../references/tutorials.md)
and [vector export checks](../../../../references/vector-export.md). Inspect
both exports at the size at which readers will see them.

## Provenance

Original illustration and editable source prepared for Computational Modeling
Skills, distributed under the collection's MIT license. The papers above support
the scientific distinctions; no artwork or source code from those papers is
copied into this example. The remake follows the recovered brief for an earlier
AI-generated reference, which was not available for direct visual comparison.
It replaces the earlier captions, geometry, and resolution-axis framing with
explicit modeling choices. Earlier reconstructions remain in private local
history and are not active build inputs or public package contents.
