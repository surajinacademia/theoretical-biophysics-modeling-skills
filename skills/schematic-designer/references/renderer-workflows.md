# Renderer Workflows

Use this reference after the scientific inventory and before authoring source.
Choose the renderer from content and required editability, never from the input
file extension.

## Contents

- [Choose a renderer](#choose)
- [Arrowheads](#arrowheads)
- [Matplotlib](#matplotlib)
- [TikZ](#tikz)
- [Hybrid](#hybrid)
- [Reconstruction and layout](#reconstruction-and-layout)

## Choose

| Renderer | Best fit | Avoid when |
|---|---|---|
| Matplotlib | Computed plots, trajectories, fields, data-heavy panels, rapid iteration | Final composition needs dense native-TeX annotation |
| TikZ | Equations, node-and-arrow schematics, braces, relative layout, document-matched type | The figure is dominated by computed fields or plot panels |
| Hybrid | Current computed panels with TikZ labels, callouts, and composition | Either renderer alone can express the figure clearly |

An input PNG or JPEG is not a reason to deliver raster output. Recreate its
meaning with editable primitives and retain an intentional photo or computed
raster layer only when it is itself scientific content.

## Arrowheads

Use actual TikZ `arrows.meta` heads for schematic arrows in every profile.
Set `>={Latex}` and use `->`, `<-`, or `<->` as the relation requires. The
minimalist helper sets this default; `ms arrow` adds the shared structural
stroke. Other `arrows.meta` terminals, including bars, circles, or diamonds,
remain available when their shape carries an explicit scientific meaning.

Keep head shape, length, width, stroke, color, and opacity consistent for each
relation role at the final physical size. Heads inherit the connector color;
choose any size override once for the role. Leave clear space around tips and
labels, and preserve direction, attachment points, and magnitude-bearing
vector lengths.

Matplotlib's PGF backend typesets text with LaTeX but does not turn Matplotlib
arrow patches into TikZ heads. For a computed panel with schematic arrows, use
the hybrid workflow: omit those arrows from the panel and draw them in the TikZ
composition. Map data-attached endpoints through the panel's actual transform
and fixed placement; do not position quantitative vectors by eye. Do not
substitute `FancyArrowPatch` tips, text arrow glyphs, or hand-drawn triangles.
For computed figures that do not need a separate compositor,
[native_tikz.py](../scripts/native_tikz.py) draws genuine TikZ paths and
heads through PGF at each artist's drawing position. This preserves clipping
and layer order without putting every arrow on top of the final scene.

## Matplotlib

- For the default minimalist profile, call `apply_style()` from
  [minimalist_profile.py](../assets/styles/minimalist_profile.py) before importing
  pyplot or `minimalist`; it selects PGF and applies LuaLaTeX/CMU typography.
  Use `palette()` for shared colors. Follow [minimalist.md](styles/minimalist.md)
  for the runtime and token mapping.
- The historical assets in `assets/styles/matplotlib/` are compatibility names
  for Minimalist. Select PGF before pyplot when using them too.
- Separate data/computation from drawing functions; drawing functions accept an
  ax.
- Use the selected profile's shared type, stroke, marker, opacity, pattern, and
  spacing roles. Follow [vector-export.md](vector-export.md) for the
  LaTeX-rendered PDF and outlined SVG.
- Keep text, curves, markers, axes, and overlays vector. Compose schematic
  arrows through TikZ as described above. Rasterize only an intentional dense
  scientific image layer.
- Use Matplotlib for the computation-backed panels in
  assets/examples/matplotlib/learning-dynamics/ and
  assets/examples/matplotlib/collective-cell-model-classes/.

## TikZ

- Use named nodes, relative positioning, semantic styles, and native math.
- For minimalist, generate the helper's `--tikz` output into a support `.sty`
  file inside the approved project work directory. Declare that file to
  `scripts/render_tikz.py` along with the figure source and any other inputs.
  Generate from the same runtime and palette as the Matplotlib panels; do not
  keep a second handwritten palette or put generated support files in this skill.
- Construction packages in `assets/styles/tikz/` also require the generated
  `minimalist-profile.sty`; declare both to the renderer. Do not copy tokens
  into every figure.
- Build trusted or generated source through scripts/render_tikz.py.
- Use LuaLaTeX, native LaTeX math, and explicit CMU font selection as specified
  in references/typography.md. Do not take an older profile's font fallback.
- Choose construction patterns from the [TikZ library](library.md#tikz-examples).

## Hybrid

1. Choose one profile and figure-wide role mapping. Regenerate each Matplotlib
   panel from the current data at its intended final physical size.
2. Save declared intermediate panels as vector PDFs, not PNGs.
3. Import them into named TikZ nodes and attach equations, arrows, and labels.
4. Declare every imported PDF and local style package to render_tikz.py.
5. Build the final pair through the TikZ workflow.

Use the same helper for minimalist panel settings and the TikZ support style;
its unit mapping is documented in [minimalist.md](styles/minimalist.md).
Avoid resizing imported panels after rendering; if composition requires a
different size, regenerate them so labels, strokes, and markers retain their
shared physical sizes. Preserve any scientifically meaningful aspect ratio.

Use assets/examples/tikz/chemoattraction/ for the complete pattern. Record input
hashes or otherwise check freshness so composition cannot silently use stale
panels.

## Reconstruction and layout

- Inspect image references at native resolution and make a content ledger for
  panels, entities, labels, equations, units, relations, scales, and
  ambiguities.
- Rebuild the semantic skeleton first, then derive repeated sizes and gaps from
  anchors or constants rather than tracing antialiased pixels.
- Preserve quantitative traces only from supplied data or computation; otherwise
  label them illustrative.
- Use whitespace, a ribbon, rail, or frame only when it expresses hierarchy.
- Route connectors through clear lanes, clip fields to their semantic zone, and
  keep repeated objects and panel tags consistently sized and aligned.
- Apply visual size and opacity tokens only to styling. Preserve radii, vector
  lengths, colors, and opacity that encode scientific quantities. Define pattern
  meanings for the figure and retain them in marks, labels, and legends.
