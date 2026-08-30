# Examples and Licenses

Inspect an example only after choosing the renderer and profile. Treat source as
a construction pattern, not as scientific authority; retain or replace its
science with the user-specified model, data, and claims.

## Approved project examples

| Need | Location | Primary pattern |
|---|---|---|
| Profile-defining computed/narrative figure | examples/learning-dynamics/ | matplotlib-figure.py and tikz.tex |
| Computed reaction–diffusion field with mechanism inset | examples/activator-inhibitor/ | matplotlib-figure.py |

Both directories include the approved PDF and outlined-SVG render pair under
`renders/`. Use `assets/templates/tikz-standalone.tex` for a neutral TikZ start.

## TikZ gallery patterns

All gallery examples live under examples/tikz-gallery/. Choose by construction
pattern:

| Pattern family | Examples |
|---|---|
| Process and dependency flows | lab-curriculum-flow, optimization-decision-flowchart, epc-flow-charts, swan-wave-model |
| State and system maps | mesif, model-physics, behavioral-timescale-buckets |
| Geometry and trajectories | secant-regression-geometry, orbital-elements-3d-trajectory, spherical-and-cartesian-grids, dome, seismic-focal-mechanism-in-3d-view |
| Scientific instruments | polarizing-microscope, transmission-electron-microscope |
| Structural notation | global-nodes, tkz-linknodes-examples, tkz-orm-example |

Each gallery directory supplies source.tex, figure.pdf, and figure.svg. Use the
source as the editable starting point and re-render it after changes.

## Licensing

The activator-inhibitor example and the example scientific content are original
and use the repository MIT license.

The learning-dynamics profile records visual grammar informed by arXiv:2406.07856.
Read the repository `THIRD_PARTY_NOTICES.md` before copying or redistributing
that profile or its examples.

Before copying or redistributing a gallery pattern, read
examples/tikz-gallery/manifest.json and examples/tikz-gallery/LICENSE.md. Honor
the entry-specific source and package terms, preserve required notices, and
redraw from first principles if the downstream license is incompatible.

Before adding an external pattern, record its source, license, attribution,
change notice, and redistribution conditions. If those terms are incompatible,
identify the construction technique and redraw from first principles. Do not
infer reuse rights from a public URL or visual similarity.
