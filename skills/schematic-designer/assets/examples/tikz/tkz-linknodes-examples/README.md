# Linked equation nodes

This maintained adaptation uses the owner's Minimalist palette through the
shared profile, CMU Sans Serif text, real Computer Modern math, and native
TikZ `arrows.meta` terminals. Body text, structural strokes, pale fills and
spacing use shared roles; colors carry the same meaning in marks and labels.

Two single-picture equation chains preserve the seven-step quadratic solution
and the completing-square construction, including adding and subtracting 9/16
inside the outer factor of two. Operation labels and arrows share each chain's
color. The completed-square expression retains red across successive steps;
remaining constants stay in neutral ink. The real-valued domain is explicit.

The source's incorrect annotation `sqrt(x) = |x|` is corrected to
`sqrt(x²) = |x|`; the actual equations are unchanged. The second construction
is credited in the archived source to Herbert Voß's *MathMode.pdf*. That
secondary attribution is retained here. Native TikZ named nodes replace the
old `tkz-linknodes` package and remembered-page overlays, so that package's
code is not copied or required. Its original license notices remain archived.

## Design lesson

- **Use when:** Readers need to understand the operation connecting successive equations, rather than merely see an initial expression and final result.
- **Why this arrangement helps:** Each derivation occupies its own vertical column, and operation labels sit beside the arrows between equations. The completing-square example exposes the added and subtracted term inside the outer factor; underbraces identify the regrouping, and the square retains its red identity through the final step while constants stay neutral. This makes the reason for each transition inspectable.
- **Transfer to a new figure:** Reserve vertical space for the operation as well as the equation. Name the transformation at its transition, and highlight the subexpression being reorganized before highlighting the final result.
- **Check before adapting:** An arrow must connect mathematically valid steps under the stated domain. In particular, the real-valued identity is `sqrt(x²) = |x|`; dropping the absolute value or moving the compensating term outside its factor changes the mathematics.

## Build and inspect

From the schematic-designer skill directory, using the documented compatible
Python environment:

```sh
python3 scripts/build_example.py tikz-tkz-linknodes-examples --output-dir /tmp/tkz-linknodes-examples
```

The builder generates current style support and compiles trusted source with
LuaLaTeX in a fresh work directory. It exports a PDF and an outlined SVG.
Inspect labels, mathematical notation, terminal types and clearances at final
size. No archived render or local legacy package is a build dependency.

[Editable source](source.tex) · [PDF](figures/figure.pdf) ·
[Outlined SVG](figures/figure.svg) · [Attribution](ATTRIBUTION.md)

## Current visual design

The binomial square remains red while it is regrouped and in the final expression; constants remain neutral ink. Removing separate shift/constant accents avoids suggesting new categories midway through the derivation. Equations, domains, operations, and the documented square-root annotation correction are retained.
