# Vector Export Contract

Read this before producing a final figure.

## Artifact contract

Keep the editable source as provenance. The final rendered deliverables are
exactly:

- figure.pdf
- figure.svg

The PDF must open at the intended page size with embedded fonts. The SVG must
contain outlined glyph paths: no live <text>, <tspan>, <textPath>,
font-family, or @font-face. Reused path definitions through <use> are allowed.
Do not deliver a raster preview, TeX build debris, or a full-page bitmap wrapped
in SVG.

## Matplotlib

Call configure_matplotlib_vector_output() before creating the figure and
save_vector_pair(...) from assets/python/vector_output.py for the final pair.
The helper sets svg.fonttype = "path", embeds intentional raster layers, and
publishes safely. Keep rasterization limited to a declared dense scientific
layer at sufficient final-size resolution.

## TikZ and hybrid

Compile the trusted/generated final TeX with scripts/render_tikz.py. It produces
the PDF and converts it to a path-only SVG with dvisvgm --no-fonts or its checked
local fallback. For a hybrid, validate only the composed final pair; intermediate
vector PDFs are inputs, not final deliverables.

## Verify

- The PDF has a valid header, opens, and has the intended physical page size.
- The SVG is XML/SVG with visible vector geometry and no live text or font
  declarations.
- The SVG has no script, DTD, entity declaration, stylesheet import, or external
  file reference.
- Any <image> is an intentional scientific raster layer, never rasterized labels
  or a disguised full-page figure.
- Reopen both files at final dimensions and check clipping, legibility, and
  color-independent distinctions.
