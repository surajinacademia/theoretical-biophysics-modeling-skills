# Transmission Electron Microscope System

This maintained adaptation uses the owner's Minimalist palette through the
shared profile, CMU Sans Serif text, real Computer Modern math, and native
TikZ `arrows.meta` terminals. Body text, structural strokes, pale fills and
spacing use shared roles; colors carry the same meaning in marks and labels.

The cutaway geometry, paired coils, aperture openings, sample holder and
beam crossover paths retain the archived coordinates. Flat neutral housing,
pale coil fills and repeated coil marks replace metallic gradients. The random
cut edge is replaced by its deterministic polygon; the shading workaround was
removed. Red denotes lens coils and their labels, teal the beam, and navy the
specimen. The dotted optical axis remains distinct from the solid beam paths.
“Sample” and “imaging” labels are expanded to “specimen” and “imaging plane.”
This is an instrument construction example, not a calibrated electron-optics
calculation. The native Latex arrow by the beam key indicates propagation.

## Design lesson

- **Use when:** An instrument's internal arrangement explains its function, but a full exterior drawing would hide the important path.
- **Why this arrangement helps:** The central cutaway exposes the source, coils, apertures, specimen and beam while retaining enough housing to locate them. Repeated paired coil marks identify related lens assemblies; quieter housing outlines and coil stippling keep the internal beam path prominent. A dotted axis remains distinguishable from the solid teal beam, and labels outside the housing preserve the narrow interior for geometry.
- **Transfer to a new figure:** Choose the cutaway around the path readers need to trace. Keep housing subordinate, repeat component symbols consistently, and place labels beside the corresponding heights or stages. Preserve openings as visible negative space.
- **Check before adapting:** Confirm that clipping does not erase a relevant component or close an aperture. Repeated coil marks and beam crossovers explain this schematic construction; they do not establish winding counts, physical dimensions or calibrated electron trajectories.

## Build and inspect

From the schematic-designer skill directory, using the documented compatible
Python environment:

```sh
python3 scripts/build_example.py tikz-transmission-electron-microscope --output-dir /tmp/transmission-electron-microscope
```

The builder generates current style support and compiles trusted source with
LuaLaTeX in a fresh work directory. It exports a PDF and an outlined SVG.
Inspect labels, mathematical notation, terminal types and clearances at final
size. No archived render or local legacy package is a build dependency.

[Editable source](source.tex) · [PDF](figures/figure.pdf) ·
[Outlined SVG](figures/figure.svg) · [Attribution](ATTRIBUTION.md)

## Current visual design

Housing outlines and repeated coil stippling use context strokes and reduced visual prominence, leaving the beam, apertures, specimen, and colored lens labels easier to locate. The cutaway coordinates, coil pattern positions, and beam paths are unchanged. Stippling remains a component texture, not a calibrated winding count.
