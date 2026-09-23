# Chemoattraction: computed panels with TikZ composition

[Panel source](../../matplotlib/chemoattraction/matplotlib-panels.py) · [Compositor](tikz-compositor.tex) ·
[Retained model context](model-plan.md) ·
[Finished PDF](figures/chemoattraction-hybrid.pdf) ·
[Finished SVG](figures/chemoattraction-hybrid.svg) ·
[Library](../../../../references/library.md)

The Python panel source is maintained in the sibling
[Matplotlib helper folder](../../matplotlib/chemoattraction/README.md). This
folder owns the TeX compositor, model context, and the only final PDF/SVG pair.
The full build command below regenerates the panel inputs; neither source nor
final output is duplicated between renderer folders.

## Design lesson

- **Use when:** a mechanism, computed maps and trajectories, and a parameter
  sweep need to read as one figure despite being authored in different renderers.
- **Why it helps:** the compositor allocates consistent panel spaces and imports
  computed panels at their native physical size. Text, markers, and line weights
  therefore retain their hierarchy beside native TikZ labels and mechanisms.
  One compositor title per panel avoids duplicate headings. An elliptical halo
  and opaque entity tints distinguish field extent from cell identity; dark teal
  process arrows remain visible. The sweep retains its discrete sampled cells.
- **Borrow:** allocate final panel sizes before rendering, then regenerate any
  panel whose allotted size changes. Use common heading positions and whitespace
  to connect the panels; let each panel retain the encoding its quantity needs.
- **Check after adapting:** inspect the joins between renderers for size drift.
  Do not smooth sparse sweep cells into a claimed phase boundary. The final
  “hybrid contract” panel explains this tutorial's construction and should be
  replaced with relevant scientific content in a research figure.

## Build and scientific context

Run from the skill root with an approved output path:

```bash
python3 scripts/build_example.py chemoattraction --output-dir /tmp/schematic-chemoattraction
```

The build regenerates `field-profile.pdf`, `concentration-map.pdf`,
`simulation-summary.pdf`, and `phase-diagram.pdf` in a fresh temporary directory.
It generates the shared style, declares both style inputs and all four panels,
and compiles the compositor through LuaLaTeX. Final outputs are
`chemoattraction-hybrid.pdf` and `chemoattraction-hybrid.svg`; intermediate panels
are not deliverables. The archived panels are never inputs. Follow the
[common build and trust requirements](../../../../references/tutorials.md).

The compositor imports panels at their native physical size, preserving CMU
text, actual LaTeX equations, line weights, and marker sizes. Panel grouping uses
whitespace. The mechanism and annotations use native TikZ heads, as do directions
inside computed panels. Regenerate panels if their allotted width changes.

The computed examples illustrate a `K0` concentration profile, a `K1` gradient
construction, and noisy heading updates biased toward the aggregate gradient.
The default trajectory illustration uses 24 cells, 110 steps, `κ = 0.18`, and
`σ = 0.35`. The parameter sweep evaluates seven coupling values and seven noise
values, with 16 cells and 60 steps per sample. Its **49 discrete colored cells**
show the sampled final heading-order values directly, with midpoint display
edges and a fixed `[0, 1]` color scale. Do not interpolate boundaries or describe
this small illustrative sweep as an established phase diagram.

Scientific limitations retained from the source:

- When the sensed gradient is zero, `atan2(0, 0)` assigns angle zero. The ensuing
  torque can bias isolated cells toward that direction. These illustrative
  trajectories and order values therefore do not validate a chemotaxis model.
- The profile samples from `r = 0.05` and normalizes by that first value,
  labeled `C(r)/C(0.05)`. This is a finite-radius reference, not a finite value
  of `K0` at zero, where the function is singular.
- The concentration map sums all three displayed sources, including its gradient
  direction, while showing a sensing-radius circle. That circle does not impose
  a cutoff on the map calculation. The trajectory code applies its own cutoff.
- The retained model plan supplies context and proposed physical interpretations;
  the illustrative builder does not establish every claim in that document or
  implement the full biochemical pathway shown in the mechanism.

Preserve these distinctions when adapting presentation. Resolving scientific
limitations requires a separately authorized model change, not a silent drawing
edit. Check the update equation, sensed direction, labels, sample-cell values,
and declared limitations, then inspect both formats and apply the full
[export contract](../../../../references/vector-export.md).

## Current visual design

The compositor owns each panel title; the Python panels no longer repeat those headings, and the simulation parameter subtitle is retained. The illustrative mechanism halo keeps its elliptical boundary instead of a rectangular clip, with opaque pale entity fills above it. Process arrows use higher-contrast teal and the noise link uses the shared dash role. Equation and build-pipeline annotations are unboxed. Concentration and heading-order maps still use Minimalist’s sequential colormap API, not categorical colors; the sampled values, normalization, and scientific limitations are unchanged.
