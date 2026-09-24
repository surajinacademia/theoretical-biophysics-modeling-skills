# MESIF protocol

Active Minimalist adaptation. See [attribution](ATTRIBUTION.md) for provenance and reuse terms. Source: [source.tex](source.tex); outputs: [PDF](figures/figure.pdf), [SVG](figures/figure.svg).

## Design lesson

- **Use when:** a small set of states has many directed transitions, including self-loops. The example shows how edge routing can carry complexity while state symbols remain simple and consistent.
- **Why this choice helps:** states share one vertical spine. Most downward connections fan out to the right and upward connections to the left; differing bend angles separate routes with similar endpoints. Self-loops sit near their states, and white label backgrounds keep transition text readable over passing curves.
- **Borrow:** choose a routing convention before drawing individual edges, then reserve progressively wider arcs for longer connections. Keep state appearance stable so the reader concentrates on the transition labels.
- **Adaptation check:** curve position is a layout convention, not an extra protocol category. Label backgrounds can conceal a crossing, so trace arrowheads and endpoints in the final render. More states or longer labels may require a different layout rather than still wider arcs.

From the skill root, the supported entry point is:

```sh
python3 scripts/build_example.py tikz-mesif --output-dir ./output/tikz-mesif
```

The builder generates its style and compiler inputs in a fresh private temporary
directory. Use a Python environment with the plotting dependencies and available
LuaLaTeX/CMU fonts and supported SVG converters.

This is a construction example, not new scientific evidence. Preserve its directed relations and formulas when changing visual layout.

## Current visual design

Visual re-audit: the formal state circles, native transitions, 8 pt edge labels and semantic white space already passed visual inspection. Retained their design; aligned label-mask padding with the shared spacing role. All 18 transitions remain unchanged.

The checked PDF is **124.37 × 161.62 mm** at native size. Place it unscaled to retain the shared 8 pt body role; headings use 9 pt and panel tags, where present, use 10 pt. Only supporting notes use 7 pt. These are TeX points (PDF reports about 7.97 pt for an 8 pt TeX font); mathematical subscripts retain normal LaTeX sizing. Both PDF and outlined SVG were visually inspected after regeneration.
