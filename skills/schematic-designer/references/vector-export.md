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

Follow references/typography.md and render the figure to a staged PDF with
Matplotlib's PGF/LuaLaTeX backend. Convert that same PDF to outlined SVG using
`dvisvgm --pdf --no-fonts` or a verified local vector converter. Validate both
staged files before atomically replacing each final file in the approved output
directory. Keep rasterization limited to declared scientific image layers.

The bundled `save_vector_pair` detects the PGF canvas and converts its rendered
PDF to SVG using the same bounded converter and validation as the TikZ runner.
Both formats are staged and checked before either final file is replaced.
Use common/PDF save options; a PGF SVG has no independent renderer options.
The older non-PGF branch remains for existing callers, but it does not meet
this skill's mandatory LaTeX typography rule. Do not switch backends for SVG.

## TikZ and hybrid

Compile the trusted/generated final TeX with scripts/render_tikz.py. It produces
the PDF and converts it to an outlined-text SVG with dvisvgm --no-fonts or its checked
local fallback. For a hybrid, validate only the composed final pair; intermediate
vector PDFs are inputs, not final deliverables.

## Verify

- The PDF has a valid header, opens, and has the intended physical page size.
- The SVG is XML/SVG with visible vector geometry and no live text or font
  declarations.
- The SVG has no script, DTD, entity declaration, stylesheet import, or external
  file reference.
- Any <image> is an intentional scientific raster layer, never rasterized labels
  or a disguised full-page figure. The owner-requested original Standard Model
  design has one documented exception: 18 embedded blur-shadow opacity masks.
  Its manifest identifies and hashes each mask; tests require every image
  reference to occur inside a mask, with all diagram content kept as vectors.
- Reopen both files at final dimensions and check clipping, legibility, and
  color-independent distinctions.
