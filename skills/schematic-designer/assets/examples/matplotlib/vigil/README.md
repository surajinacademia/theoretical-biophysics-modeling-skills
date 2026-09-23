# VIGIL: source-backed conceptual reconstruction

[Builder](build_figure.py) · [Preserved geometry](vigil_geometry.py) ·
[Attribution](ATTRIBUTION.md) · [License](LICENSE) ·
[Finished PDF](figures/vigil-minimalist.pdf) ·
[Finished SVG](figures/vigil-minimalist.svg) ·
[Library](../../../../references/library.md)

Read the attribution and CC BY-NC 4.0 license before adapting this example. Its
source is Chen Liu's figures4papers construction at the pinned revision recorded
in `ATTRIBUTION.md`. Keep those notices with the source and rendered adaptation. The approved
public export retains the noncommercial restriction; MIT does not replace it.

## Design lesson

- **Use when:** a figure combines sparse curves and a dense cloud of points,
  contours, trajectories, and annotations, or an existing construction needs
  restyling without moving its scientific geometry.
- **Why it helps:** smaller named point roles and quieter contours keep the
  cloud subordinate to the paths and checkpoints. A single aligned legend row
  and matching curve patterns make the conditions identifiable beyond color;
  clear label backgrounds protect text in crowded regions.
- **Borrow:** separate geometry generation from presentation. Map annotations
  through the actual axes transforms so a layout revision does not detach them
  from their targets. Adjust dense-detail roles together rather than assigning
  a different size or opacity to each mark.
- **Check after adapting:** preserve points, contour levels, endpoints, and
  pattern-to-condition mappings. Keep gaps around labels without displacing
  meaningful coordinates. The retained “Probability” label does not establish
  calibrated probabilities; these profiles and manifolds remain illustrative.

## Build and scientific context

Run from the skill root with an approved output path:

```bash
python3 scripts/build_example.py vigil --output-dir /tmp/schematic-vigil
```

This example lives under Matplotlib because its maintained authoring sources
are Python. Its builder generates the TikZ compositor, labels, and native heads
during the build; there is no separately maintained TeX example or hybrid folder.

The builder computes the base panels and writes declared compositor/style inputs
and `geometry-check.json` beneath the output's `source/` directory. It compiles
that generated compositor to `vigil-minimalist.pdf` and
`vigil-minimalist.svg` at the output root. `source/panels.pdf` is an intermediate
input. Follow the [shared build and trust requirements](../../../../references/tutorials.md).

`vigil_geometry.py` preserves the seeded cloud points, Gaussian constructions,
KDE levels, trajectories, and checkpoints. `build_figure.py` owns presentation:
Minimalist colors, CMU/LaTeX, native TikZ arrowheads, a shared hierarchy, and
non-color line-pattern distinctions. The VIG endpoints are mapped through the
actual axes transforms. Keep geometry changes separate from restyling.

Dense clouds use named derived roles: a point diameter of one third of the shared
point role, shared fill opacity, contextual contour opacity, and a star outline
half the context stroke. The blind-condition dash pattern is assembled once
from shared dash tokens and reused in the curve and legend. These local choices
support this density and distinction; they are not new universal defaults.

The answer profiles and manifolds are illustrative, not empirical embeddings
or normalized probability densities. The original Probability axis and display
coordinate tick labels are retained, so do not infer calibrated probabilities or
validated VIGIL results. Inspect VIG endpoints, label placement, curve-pattern
matching, checkpoints, and the illustrative-content note, then apply all
[export checks](../../../../references/vector-export.md).
