# Behavioral timescale buckets

This maintained adaptation uses the owner's Minimalist palette through the
shared profile, CMU Sans Serif text, real Computer Modern math, and native
TikZ `arrows.meta` terminals. Body text, structural strokes, outline regions and
spacing use shared roles; colors carry the same meaning in marks and labels.

The five overlapping disciplinary buckets, ten branches and three braces
preserve the original qualitative cross-timescale story. Axis position is
conceptual, not a numerical time coordinate. The progression to behavior has
one native Latex head. The shared emphasis stroke replaces the heavy arrow;
larger physical spacing makes body labels readable without shrinking text.
Unfilled region outlines keep overlapping scopes visible while labels remain opaque. Branch labels associated with a discipline reuse its categorical color when
legible. Orange and amber categories use dark text beside the colored branch,
brace or explicit key, retaining contrast on the white canvas.

## Design lesson

- **Use when:** several explanatory perspectives overlap along a conceptual progression. The enclosing buckets communicate shared scope more directly than separate panels would, while the central arrow supplies a common reading direction.
- **Why this choice helps:** unfilled outlines preserve intersections without composite colors; text and branch marks stay opaque. Labels alternate above and below the progression to distribute crowding; braces name spans without adding another arrow. Dark text beside orange and amber keys preserves the category link where colored text would lose contrast.
- **Borrow:** use overlapping regions for genuinely overlapping scope, place their names near exposed boundaries, and coordinate label placement with the densest intersections. Keep explanatory spans visually distinct from directional relations.
- **Adaptation check:** positions and widths are qualitative, not measured times or effect sizes. Region overlaps do not add color categories. Do not let a neat sequence imply exclusive stages or a causal claim the model does not support.

## Build and inspect

From the schematic-designer skill directory, using the documented compatible
Python environment:

```sh
python3 scripts/build_example.py tikz-behavioral-timescale-buckets --output-dir /tmp/behavioral-timescale-buckets
```

The builder generates current style support and compiles trusted source with
LuaLaTeX in a fresh work directory. It exports a PDF and an outlined SVG.
Inspect labels, mathematical notation, terminal types and clearances at final
size. No archived render or local legacy package is a build dependency.

[Editable source](source.tex) · [PDF](figures/figure.pdf) ·
[Outlined SVG](figures/figure.svg) · [Attribution](ATTRIBUTION.md)

## Current visual design

Visual re-audit: retained all five scientific region extents but removed overlapping translucent fills, which previously produced muddy composite colors. Shared context-width outline boundaries now preserve overlap without inventing colors. The neutral behavior axis no longer borrows the evolution color; releasing-stimuli marks and text use their neurobiology region color.

The checked PDF is **154.6 × 65.18 mm** at native size. Place it unscaled to retain the shared 8 pt body role; headings use 9 pt and panel tags, where present, use 10 pt. Only supporting notes use 7 pt. These are TeX points (PDF reports about 7.97 pt for an 8 pt TeX font); mathematical subscripts retain normal LaTeX sizing. Both PDF and outlined SVG were visually inspected after regeneration.
