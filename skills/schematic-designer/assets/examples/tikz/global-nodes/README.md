# Global nodes across equations and lists

This maintained adaptation uses the owner's Minimalist palette through the
shared profile, CMU Sans Serif text, real Computer Modern math, and native
TikZ `arrows.meta` terminals. Body text, structural strokes, pale fills and
spacing use shared roles; colors carry the same meaning in marks and labels.

The complete acceleration decomposition is preserved, including the body-frame
superscript on both time derivatives, all plus signs and vector cross products.
Named equation nodes replace document-global remembered overlays, so each
colored term and its matching callout are positioned in one bounded picture.
The arrows identify terms; they do not assert causal dependence. Labels and
terms share teal (Coriolis), red (transversal), and navy (centripetal) colors.

## Design lesson

- **Use when:** A compact equation contains several physically meaningful contributions that need names without breaking the expression into separate panels.
- **Why this arrangement helps:** The unboxed terms share a mathematical baseline, with neutral plus signs between the colored contributions. Body-size callouts leave the equation visually primary. Callouts alternate above and below the equation and connect directly to their named terms. Readers can inspect the complete decomposition and then identify a contribution without consulting a distant legend.
- **Transfer to a new figure:** Anchor annotations to the actual equation nodes, leave a clear annotation lane above or below, and retain operators and parentheses as part of the mathematical reading order. Color only the contributions that need identification.
- **Check before adapting:** These arrows identify terms; they do not show causation or an algebraic transition. Recheck attachment points and label clearances whenever an expression changes, especially superscripts, fractions and nested cross products.

## Build and inspect

From the schematic-designer skill directory, using the documented compatible
Python environment:

```sh
python3 scripts/build_example.py tikz-global-nodes --output-dir /tmp/global-nodes
```

The builder generates current style support and compiles trusted source with
LuaLaTeX in a fresh work directory. It exports a PDF and an outlined SVG.
Inspect labels, mathematical notation, terminal types and clearances at final
size. No archived render or local legacy package is a build dependency.

[Editable source](source.tex) · [PDF](figures/figure.pdf) ·
[Outlined SVG](figures/figure.svg) · [Attribution](ATTRIBUTION.md)

## Current visual design

Removed the tinted equation-term rectangles and changed the three callouts from the title role to the 8 pt body role. Colored terms, matching callouts, and clear annotation lanes supply identification without enclosing the algebra. Every derivative, operator, and term remains unchanged.
