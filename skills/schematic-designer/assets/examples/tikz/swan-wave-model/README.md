# SWAN wave model

Active Minimalist adaptation. See [attribution](ATTRIBUTION.md) for provenance and reuse terms. Source: [source.tex](source.tex); outputs: [PDF](figures/figure.pdf), [SVG](figures/figure.svg).

## Design lesson

- **Use when:** several spatial fields cover related domains but use different extents or resolutions. An exploded stack exposes those differences without forcing every grid onto one congested plane.
- **Why this choice helps:** every layer uses the same oblique transform, giving the reader a common spatial frame. Stronger perimeter lines separate domain boundaries from fine mesh lines; accented subgrids reveal local refinement. Opaque white layer fills prevent grids behind them from producing distracting interference.
- **Borrow:** keep the projection consistent, separate layers enough to identify their edges, and place callouts outside the stack. Use a restrained accent for the specific cell or refinement region being discussed.
- **Adaptation check:** vertical separation is diagrammatic, not a measured physical height. This source also repeats the label “Bathymetry”; clarify layer identities for a new model. Verify every callout endpoint after changing the projection, extent, or stacking order.

From the skill root, the supported entry point is:

```sh
python3 scripts/build_example.py tikz-swan-wave-model --output-dir /tmp/tikz-swan-wave-model
```

The explicit recipe below runs from the repository root with a Python environment containing Minimalist and with LuaLaTeX/CMU fonts and the supported SVG converters available:

```sh
mkdir -p /tmp/schematic-minimalist
python3 skills/schematic-designer/assets/styles/minimalist_profile.py --tikz > /tmp/schematic-minimalist/minimalist-profile.sty
python3 skills/schematic-designer/scripts/render_tikz.py skills/schematic-designer/assets/examples/tikz/swan-wave-model/source.tex --include /tmp/schematic-minimalist/minimalist-profile.sty --engine lualatex --output-dir /tmp/tikz-swan-wave-model --basename figure
```

This is a construction example, not new scientific evidence. Preserve its directed relations and formulas when changing visual layout.

## Current visual design

Visual re-audit: moved the Shoreline annotation outside the grid transform so its CMU glyphs are no longer sheared. The annotation target is preserved. Corner labels now use dark ink beside their existing orange markers. Grid transforms, domains, mesh steps and contour coordinates are unchanged.

The checked PDF is **138.84 × 181.2 mm** at native size. Place it unscaled to retain the shared 8 pt body role; headings use 9 pt and panel tags, where present, use 10 pt. Only supporting notes use 7 pt. These are TeX points (PDF reports about 7.97 pt for an 8 pt TeX font); mathematical subscripts retain normal LaTeX sizing. Both PDF and outlined SVG were visually inspected after regeneration.
