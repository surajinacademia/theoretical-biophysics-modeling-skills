# Optimization decision flowchart

Active Minimalist adaptation. See [attribution](ATTRIBUTION.md) for provenance and reuse terms. Source: [source.tex](source.tex); outputs: [PDF](figures/figure.pdf), [SVG](figures/figure.svg).

## Design lesson

- **Use when:** several candidate evaluations repeat the same operation-and-test structure. A vertical sequence lets the reader recognize the repeated pattern and locate the changing candidate expression.
- **Why this choice helps:** equal-width process boxes and repeated decision diamonds distinguish actions from questions. Branches leave the central column through a separate routing corridor, while step labels occupy the opposite margin. This reserves the main column for the sequence itself.
- **Borrow:** define one reusable process style, one decision style, and explicit branch waypoints before adding labels. Keep long conditions beside their own edges rather than compressing the main boxes.
- **Adaptation check:** this preserves a historical diagram with repeated “Yes, pass” labels and some unlabeled exits; it is not a validated optimization algorithm. Supply unambiguous conditions for every outgoing branch in a new application, and verify whether shared branch lines mean collection, continuation, or both.

From the skill root, the supported entry point is:

```sh
python3 scripts/build_example.py tikz-optimization-decision-flowchart --output-dir ./output/tikz-optimization-decision-flowchart
```

The builder generates its style and compiler inputs in a fresh private temporary
directory. Use a Python environment with the plotting dependencies and available
LuaLaTeX/CMU fonts and supported SVG converters.

This is a construction example, not new scientific evidence. Preserve its directed relations and formulas when changing visual layout.

## Current visual design

Visual re-audit: retained formal process rectangles and decision diamonds but removed their colored background fills. Reduced excessive vertical gaps without changing any edge or branch. All branch/step labels now use the body role and shared label padding.

The checked PDF is **200.88 × 197.51 mm** at native size. Place it unscaled to retain the shared 8 pt body role; headings use 9 pt and panel tags, where present, use 10 pt. Only supporting notes use 7 pt. These are TeX points (PDF reports about 7.97 pt for an 8 pt TeX font); mathematical subscripts retain normal LaTeX sizing. Both PDF and outlined SVG were visually inspected after regeneration.
