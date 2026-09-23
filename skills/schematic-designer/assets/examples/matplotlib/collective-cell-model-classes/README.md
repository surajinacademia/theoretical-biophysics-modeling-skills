# Collective cell model classes

[Editable Python source](matplotlib-figure.py) ·
[Finished PDF](figures/collective-cell-model-classes.pdf) ·
[Finished SVG](figures/collective-cell-model-classes.svg) ·
[Library](../../../../references/library.md)

## Design lesson

- **Use when:** several scientific representations must be compared despite
  having different internal geometry: particles, cells, lattices, fields, and
  coupled representations.
- **Why it helps:** repeated heading positions, compact color keys, and common
  panel proportions make comparison possible without forcing every model into
  the same symbol. Whitespace groups the families; internal boundaries remain
  available to describe actual cells, compartments, or lattice structure.
- **Borrow:** standardize the comparison frame while preserving the geometry
  that distinguishes each representation. Put an independent attribute, such
  as spatial/internal resolution, on its own explanatory axis instead of using
  panel order to encode an unstated ranking.
- **Check after adapting:** a reader should identify each family without color
  and understand that the families can overlap. Equal panel treatment does not
  establish equal resolution, equal validity, or mutual exclusivity.

## Build and scientific context

Run from the skill root, replacing the output path with an approved directory:

```bash
python3 scripts/build_example.py collective-cell-model-classes --output-dir /tmp/schematic-cell-model-classes
```

The Matplotlib PGF build writes `collective-cell-model-classes.pdf` and
`collective-cell-model-classes.svg`, with CMU/LaTeX and native TikZ heads. Follow
the [shared build and trust requirements](../../../../references/tutorials.md).

The conceptual figure compares particle, agent, lattice, continuum, and hybrid
representations. These families are non-exclusive: agent implementations may be
particle- or lattice-based, and hybrids couple representations. Spatial/internal
resolution is a separate dimension rather than a ranking of the five families.
All geometry is illustrative, not to scale, and not simulation output.

Shared typography, strokes, small color keys, and whitespace support comparison
without enclosing every family in a decorative card. Within each panel, preserve
physical and logical boundaries such as cells, compartments, and lattice edges.
Dense internal motifs can require local geometry; those coordinates do not
replace the figure-wide type or stroke hierarchy. Keep labels opaque and use
shape or text as well as color to identify model representations.

Inspect panel headings, directional links, internal labels, model-family
qualifications, and the separate resolution axis. Apply the
[export checks](../../../../references/vector-export.md) at final size. Earlier
reconstruction notes and outputs are preserved in
private local history (excluded from the public package); they
are historical references, not active build inputs or current style templates.
