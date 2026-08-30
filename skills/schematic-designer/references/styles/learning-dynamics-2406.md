# Aesthetic Profile: learning-dynamics-2406

This is a visual-only adaptation of the grammar in Mandal et al.,
[Learning dynamical behaviors in physical systems](https://arxiv.org/abs/2406.07856).
It does not copy the paper's data, photographs, panel composition, scientific
claims, or semantic color assignments. Assign every color role for the new
figure explicitly.

## Visual grammar

- Use a white canvas with generous whitespace and a left-to-right or
  top-to-bottom scientific narrative.
- Use broad pale ribbons or a vertical rail only for genuine phases or repeated
  categories; do not card every panel.
- Use bold sans-serif text for structural labels and serif mathematical type for
  equations, variables, units, and data labels.
- Put scalar fields below crisp particles, trajectories, arrows, axes, and text.
- Use direct labels and sparse annotations instead of decorative legends.

## Semantic tokens

The executable token source is
assets/styles/matplotlib/learning_dynamics_2406.py and
assets/styles/tikz/learning-dynamics-2406.sty.

| Role | Token |
|---|---|
| Ink and secondary ink | #1A1A1A, #4D4D4D |
| Training and retrieval | green #2CA05A, brown #A9745C |
| Entity pair | purple #8B5EB9, orange #E8901A |
| Interaction pair | blue #3B8BC3, red #F24432 |
| Selected state | yellow #FFD42A |
| Section ribbons | #C0E3CE, #EACFC3, #E1E1E1 |

Use a direct label, sign, line style, marker, or arrow direction alongside any
critical color distinction. Use blue/red only for an explicitly assigned pair,
not unrelated categories.

## Type and geometry

Use CMU Sans Serif for prose when available; fall back to Latin Modern Sans or
DejaVu Sans and report a constrained-font substitution. Use Computer Modern or
Latin Modern math. At final size, use approximately 13 pt for a major heading,
11–12 pt for a panel tag, 8.5–10 pt for axes/equations, and at least 7 pt for
small text. Keep ordinary plot strokes thin, narrative arrows heavier, and
structural rails heaviest.

Use lower-case bold panel tags. Align repeated panels and snapshots; allocate
width by information density rather than forcing equal cells. Render actual
quantitative fields from data or computation; translucent halos are only
illustrative.

Apply this profile through references/renderer-workflows.md; validate its final
files through references/vector-export.md.
