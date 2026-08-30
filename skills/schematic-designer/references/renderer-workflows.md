# Renderer Workflows

Use this reference after the scientific inventory and before authoring source.
Choose the renderer from content and required editability, never from the input
file extension.

## Choose

| Renderer | Best fit | Avoid when |
|---|---|---|
| Matplotlib | Computed plots, trajectories, fields, data-heavy panels, rapid iteration | Final composition needs dense native-TeX annotation |
| TikZ | Equations, node-and-arrow schematics, braces, relative layout, document-matched type | The figure is dominated by computed fields or plot panels |
| Hybrid | Current computed panels with TikZ labels, callouts, and composition | Either renderer alone can express the figure clearly |

An input PNG or JPEG is not a reason to deliver raster output. Recreate its
meaning with editable primitives and retain an intentional photo or computed
raster layer only when it is itself scientific content.

## Matplotlib

- Select the non-interactive Agg backend before importing pyplot.
- Separate data/computation from drawing functions; drawing functions accept an
  ax.
- Import the active profile from assets/styles/matplotlib/, and use
  assets/python/vector_output.py for final output.
- Keep text, arrows, curves, markers, axes, and overlays vector. Rasterize only
  an intentional dense scientific image layer.
- Use Matplotlib for the computation-backed panels in
  examples/learning-dynamics/ and examples/activator-inhibitor/.

## TikZ

- Use named nodes, relative positioning, semantic styles, and native math.
- Import the active package from assets/styles/tikz/; do not copy profile
  colors or type settings into every figure.
- Build trusted or generated source through scripts/render_tikz.py.
- Use the profile-required TeX engine; for learning-dynamics-2406, use an engine
  that can resolve CMU Sans Serif.
- Use examples/learning-dynamics/ and the approved gallery entries in
  references/examples-and-licenses.md as construction patterns.

## Hybrid

1. Regenerate each Matplotlib panel from the current data.
2. Save declared intermediate panels as vector PDFs, not PNGs.
3. Import them into named TikZ nodes and attach equations, arrows, and labels.
4. Declare every imported PDF and local style package to render_tikz.py.
5. Build the final pair through the TikZ workflow.

No project-specific hybrid example is bundled. Record input hashes or otherwise
check freshness so composition cannot silently use stale panels.

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
