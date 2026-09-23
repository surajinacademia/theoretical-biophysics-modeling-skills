# Aesthetic Profile: minimalist

Use this default for scientific schematics and eligible composite figures unless
the user, journal, or project specifies another profile. Use the optional
`minimalist` package for colors when installed, and the skill's shared helper for
typography and visual roles. Without that personal theme, the helper explicitly
warns and uses Matplotlib's default color cycle. This changes presentation, not
scientific content; it does not reproduce the stored specimens' exact colors.

## Contents

- [Shared source and runtime](#one-source-for-all-renderers)
- [Physical style tokens](#roles-at-the-intended-publication-size)
- [Color and pattern meaning](#color-text-and-pattern-meaning)
- [Typography and spacing](#typography-and-negative-space)
- [Matplotlib setup](#apply-in-matplotlib)
- [TikZ and hybrid setup](#apply-in-tikz-and-hybrid-figures)

## One source for all renderers

[minimalist_profile.py](../../assets/styles/minimalist_profile.py) is the shared
source for Matplotlib and TikZ. Its `palette()` function reads
`minimalist.get_cmap("qualitative")` when available, without copying that package
or its palette. Otherwise it reads Matplotlib's installed default cycle.
`apply_style()` selects PGF and applies LuaLaTeX/CMU typography;
`tikz_style()` returns a support style with the same colors and numerical tokens.

Use a project Python with NumPy and Matplotlib, plus LuaLaTeX, TikZ, CMU fonts,
and a supported PDF-to-SVG converter as described in the renderer references.
`minimalist` is optional and is not bundled or automatically installed. Do not
change global discovery or install dependencies merely to apply this profile.
Report missing required tools. There is no font substitution: the portable
palette still uses the same CMU/LaTeX typography and geometric role constants.

## Roles at the intended publication size

Choose the final width before drawing. These defaults are starting values for
the whole figure at its final size, not universal rules for every publication.
The bridge preserves the renderer's font and graphic units as described below.

| Shared constant | Roles and defaults | Use |
|---|---|---|
| `FONT_PT` | panel 10; title 9; body 8; equation 8; small 7 | Repeated typographic hierarchy |
| `LINE_PT` | context 0.5; structure 0.75; emphasis 1.1 | Supporting geometry, ordinary relations, selected emphasis |
| `MARKER_PT` | point 3; emphasis 4.5 | Nominal marker diameters; Matplotlib scatter uses squared values for `s` |
| `ARROW_PT` | length 4; width 2.8 | Native `Latex` tip dimensions shared by PGF artists and TikZ |
| `OPACITY` | context 0.25; fill 0.12; foreground 1 | Supporting strokes, pale fills, opaque foreground |
| `DASH_PT` | dashed (3, 2); dotted (0.7, 1.5) | On/off lengths for consistent line patterns; solid remains the default |
| `SPACE_PT` | unit 4; label 4; group 8; panel 12 | Starting distances for repeated gaps and padding |

Adjust a role once in the figure source before applying the profile and
generating its TikZ style. Keep the same settings in every panel; if Matplotlib
and TikZ generation run separately, pass them the same figure configuration.
Apply role-specific opacity and spacing explicitly to Matplotlib artists;
`apply_style()` cannot infer which objects are context or emphasis.
Foreground opacity applies to geometry; label text stays opaque even when that
role is changed. Both renderers use matching flat line ends and rounded joins.
The default canvas is white in both exports. TikZ places an opaque white
background behind the picture so pale fills do not depend on the SVG viewer's
background; this background is not a visible panel frame.

Visual size defaults do not override a physical radius, a vector length mapped
to magnitude, or any other scientific geometry. Likewise, preserve color or
opacity that already encodes a quantitative value. The qualitative palette is
for distinct entities or categories, not a replacement for a field's magnitude
mapping. Inspect the final-size composition before changing a shared token.

## Color, text, and pattern meaning

Assign palette entries to named entities or conditions before drawing. Retain
that mapping across marks, arrows, nearby labels, equations where appropriate,
and panel legends. A color cycle supplies candidates; it does not decide the
scientific mapping. Use the few colors needed to express the actual distinctions.

Match label color to the entity when it remains readable on the background.
Otherwise use dark text with a small colored key beside it. Keep text opaque;
use pale fills or quieter supporting lines to reduce visual prominence. Direct
labels placed near the relevant entity reduce unnecessary legend lookup.

For categorical objects over a field or overlapping backgrounds, prefer an
opaque tint preblended with white to a transparent fill that changes their
identity color. Keep genuine time, density, and field-opacity encodings explicit.
For overlapping qualitative regions, unfilled outlines can preserve their
extents without inventing new colors through blending.

Give every critical distinction a non-color cue such as a label, shape, terminal,
dash pattern, or hatch. Define pattern meanings for this figure and preserve them
throughout; dashed does not inherently mean uncertainty and an arrow does not
inherently mean causation. Reuse the same dash lengths across renderers. Hatches
should remain distinguishable at the final size without covering key geometry.

For a palette-only edit, preserve the original layout, glyph sizes, shadows,
shading, and opacity. Keep lighting gradients and translucent layers that convey
3D depth; change their colors without flattening their appearance.

## Typography and negative space

Follow [typography.md](../typography.md): CMU text and real Computer Modern LaTeX
math remain mandatory. Use panel/title roles for structure and body/equation
roles for scientific labels. Use consistent weight within a role. Align panel
tags, repeated motifs, and text baselines so comparisons require little scanning.

Reserve whitespace for connector lanes and nearby labels. Keep related elements
close and leave a larger gap between independent groups. Increase a panel's room
or rearrange labels before shrinking its text. A frame, rail, or ribbon needs an
actual grouping function; avoid decorative cards around every panel. Retain
boundaries that represent real compartments and label illustrative geometry when
it could otherwise imply scale.

## Apply in Matplotlib

Make the helper importable from the resolved skill's `assets/styles/` directory.
Call it before importing `pyplot` or `minimalist`, since importing `minimalist`
also imports pyplot:

```python
from minimalist_profile import apply_style, palette, FONT_PT, LINE_PT

apply_style()
import matplotlib.pyplot as plt

colors = palette()  # Assign entries to named entities in the figure source.
```

Do not call `minimalist.use_style()` afterward. Use the role constants for custom
artists as well as ordinary plotting defaults. Render through
[renderer-workflows.md](../renderer-workflows.md) and
[vector-export.md](../vector-export.md); the helper does not export figures.

## Apply in TikZ and hybrid figures

The helper's CLI `--tikz` prints a complete support style to stdout. Write it as
`minimalist-profile.sty` only inside the approved project work directory, then
declare it to `scripts/render_tikz.py` and load it with
`\usepackage{minimalist-profile}`. For customized role values, call
`tikz_style()` after setting those values in the figure's Python source. Keep
generated support files out of the skill repository.

The bridge exposes `msColor1`, `msColor2`, and subsequent palette entries in
their original order, plus `msInk`, `msMuted`, and `msPaper`. Dimensions use
macros such as `\msFontBody`, `\msLineStructure`, `\msMarkerPoint`, and
`\msSpaceGroup`; opacity macros such as `\msOpacityFill` are unitless.
Font macros use TeX `pt` and 1.2-times leading to match Matplotlib's PGF text;
strokes, markers, gaps, and dash lengths use `bp` (1/72 inch) to match its graphics.
Within the picture, math uses display style to match PGF, including fractions
and their subscripts. This does not change the surrounding document's math.
Start a picture with `[ms base]`, then select named roles such as `ms body`,
`ms equation`, `ms structure`, `ms emphasis`, `ms fill`, `ms point`,
`ms dashed`, and `ms dotted`. `ms arrow` draws a structural connector with the
actual TikZ `Latex` head; plain `->`, `<-`, and `<->` use the same tip default.
For example, `\draw[ms arrow,color=msColor6] (u.east) -- (v.west);` keeps the
shaft and head in the entity color. Follow the shared
[arrowhead rule](../renderer-workflows.md#arrowheads) for computed panels and
special terminals. Assign scientific meanings to connectors and `ms pattern`
hatches explicitly.

In hybrid figures, generate the support style and computed panels from the same
configuration. Render panels at their final physical size so importing a PDF
does not silently rescale labels, strokes, or markers relative to TikZ content.
Verify semantic color mapping, readable typography, pattern meaning, and clear
spacing in the final PDF and outlined SVG.
