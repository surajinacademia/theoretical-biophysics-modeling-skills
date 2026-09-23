# Laboratory curriculum dependencies

Active Minimalist adaptation. See [attribution](ATTRIBUTION.md) for provenance and reuse terms. Source: [source.tex](source.tex); outputs: [PDF](figures/figure.pdf), [SVG](figures/figure.svg).

## Design lesson

- **Use when:** a dependency chain splits into parallel activities and later rejoins. The layout makes the common foundation, two laboratory streams, and shared outcome visible before the labels are read.
- **Why this choice helps:** aligned rows give corresponding stages equal visual weight. The converging arrows identify integration; the small orange capstone key marks the endpoint. Solid prerequisites and dashed cross-stream links distinguish two relation types without adding more node categories.
- **Borrow:** arrange the main path first, reserve a central gap for cross-links, and name stages beside the activity groups. Reuse this structure for parallel experiments, analysis pipelines, or coupled modules when their dependencies have the same topology.
- **Adaptation check:** trace each cross-link separately at final size. Crossing curves must not suggest a junction, and matching row heights must not imply simultaneous timing unless that meaning is intended.

From the skill root, the supported entry point is:

```sh
python3 scripts/build_example.py tikz-lab-curriculum-flow --output-dir /tmp/tikz-lab-curriculum-flow
```

The explicit recipe below runs from the repository root with a Python environment containing Minimalist and with LuaLaTeX/CMU fonts and the supported SVG converters available:

```sh
mkdir -p /tmp/schematic-minimalist
python3 skills/schematic-designer/assets/styles/minimalist_profile.py --tikz > /tmp/schematic-minimalist/minimalist-profile.sty
python3 skills/schematic-designer/scripts/render_tikz.py skills/schematic-designer/assets/examples/tikz/lab-curriculum-flow/source.tex --include /tmp/schematic-minimalist/minimalist-profile.sty --engine lualatex --output-dir /tmp/tikz-lab-curriculum-flow --basename figure
```

This is a construction example, not new scientific evidence. Preserve its directed relations and formulas when changing visual layout.

## Current visual design

Visual re-audit: removed repeated filled boxes from laboratory labels; retained every prerequisite and cross-stream edge. Stage names now use the title role. The capstone uses dark ink plus an orange key, and the text uses shared roles at native output size.

The checked PDF is **108.38 × 99.49 mm** at native size. Place it unscaled to retain the shared 8 pt body role; headings use 9 pt and panel tags, where present, use 10 pt. Only supporting notes use 7 pt. These are TeX points (PDF reports about 7.97 pt for an 8 pt TeX font); mathematical subscripts retain normal LaTeX sizing. Both PDF and outlined SVG were visually inspected after regeneration.
