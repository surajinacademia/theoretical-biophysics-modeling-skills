# Polarizing microscope

This maintained adaptation uses the owner's Minimalist palette through the
shared profile, CMU Sans Serif text, real Computer Modern math, and native
TikZ `arrows.meta` terminals. Body text, structural strokes, pale fills and
spacing use shared roles; colors carry the same meaning in marks and labels.

The projection basis, polarizer/crystal positions, sampled wave formulas,
phase offsets and component coefficients are preserved from Langlois's
illustrative construction. They are not a newly validated quantitative optics
model. Propagation and polarization directions use native Latex heads; material
plane fill opacity is separate from the opacity of labels and field vectors.
The red and teal component colors persist across the crystal and output planes;
the input field is deep navy. The source swapped the component colors after
the analyzer; that color inconsistency is corrected without changing formulas. No independent field amplitude or phase was fitted.
The caption retains the monochromatic and omitted-magnetic-field qualifications.

## Design lesson

- **Use when:** A mechanism changes a vector field as it passes through successive material elements, and the reader must follow both propagation and component identity.
- **Why this arrangement helps:** A common propagation axis orders the two polarizers and crystal. The red and teal components retain their identities through the crystal and output planes; matching optical-index labels make that correspondence explicit. Quiet material planes and axes leave the field vectors prominent; horizontal material labels remain readable independently of the projection. Smaller derived heads distinguish sampled vectors from the main directional annotations.
- **Transfer to a new figure:** Establish the spatial sequence first, then assign each component a persistent visual identity. Show local orientation at the relevant material plane, and reserve descriptive labels for the spaces between elements.
- **Check before adapting:** Perspective and overlapping vectors can conceal signs, directions, or relative amplitudes. Inspect those separately from appearance. The sampled waves here are illustrative; preserve the monochromatic and omitted-magnetic-field qualifications rather than implying a validated optics calculation.

## Build and inspect

From the schematic-designer skill directory, using the documented compatible
Python environment:

```sh
python3 scripts/build_example.py tikz-polarizing-microscope --output-dir /tmp/polarizing-microscope
```

The builder generates current style support and compiles trusted source with
LuaLaTeX in a fresh work directory. It exports a PDF and an outlined SVG.
Inspect labels, mathematical notation, terminal types and clearances at final
size. No archived render or local legacy package is a build dependency.

[Editable source](source.tex) · [PDF](figures/figure.pdf) ·
[Outlined SVG](figures/figure.svg) · [Attribution](ATTRIBUTION.md)

## Current visual design

Material labels are horizontal; muted context strokes keep axes and planes behind the colored wave components. Sampled field-vector shafts use the context stroke and native Latex heads at 0.6 times the shared head dimensions; main direction and polarization annotations retain the standard heads. The zero-amplitude samples at x = 0 omit their degenerate arrow glyphs while the plotted wave still includes zero. Wave formulas, phase offsets, component coefficients, and nonzero vector endpoints are unchanged. The smaller sampled heads are a figure-specific density choice, not a replacement for the shared directional default.
