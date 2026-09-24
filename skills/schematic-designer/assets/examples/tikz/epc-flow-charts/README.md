# EPC flow charts

Active Minimalist adaptation. See [attribution](ATTRIBUTION.md) for provenance and reuse terms. Source: [source.tex](source.tex); outputs: [PDF](figures/figure.pdf), [SVG](figures/figure.svg).

## Design lesson

- **Use when:** a protocol needs both state transitions and substantial information about what each state does. The two stacked flows demonstrate how to retain instructions, equations, and a small table within a state diagram.
- **Why this choice helps:** bold state names provide a first reading level; the longer descriptions remain inside their state boxes. Transition conditions sit on the connecting edges, and curved return paths separate repetition from the forward route. The same box treatment carries across both flows.
- **Borrow:** divide information by responsibility: node title for identity, node body for local operations, edge label for the condition or message that changes state. Allocate space for return paths before placing explanatory text.
- **Adaptation check:** these two flows are not aligned as a row-by-row comparison. If comparison is the goal, align equivalent states explicitly. Preserve protocol conditions when shortening text, and inspect long edge annotations for collisions rather than reducing their font size.

From the skill root, the supported entry point is:

```sh
python3 scripts/build_example.py tikz-epc-flow-charts --output-dir ./output/tikz-epc-flow-charts
```

The builder generates its style and compiler inputs in a fresh private temporary
directory. Use a Python environment with the plotting dependencies and available
LuaLaTeX/CMU fonts and supported SVG converters.

This is a construction example, not new scientific evidence. Preserve its directed relations and formulas when changing visual layout.

## Current visual design

Visual re-audit: removed large teal prose-block fills, retained semantic state outlines, separated palette-colored state headings from dark body text, and added A/B panel tags. Item spacing uses the shared spacing role. All state transitions, formulas and tabulated values remain unchanged.

The checked PDF is **215.06 × 165.71 mm** at native size. Place it unscaled to retain the shared 8 pt body role; headings use 9 pt and panel tags, where present, use 10 pt. Only supporting notes use 7 pt. These are TeX points (PDF reports about 7.97 pt for an 8 pt TeX font); mathematical subscripts retain normal LaTeX sizing. Both PDF and outlined SVG were visually inspected after regeneration.
