# Reference-Image Reconstruction

Use this workflow when a PNG, JPEG, screenshot, scan, or rendered figure is an
input. Reconstruct scientific meaning and visual structure with editable
primitives; do not optimize for literal pixel imitation.

## Contents

- [Define the reconstruction contract](#define-the-reconstruction-contract)
- [Inspect and inventory the reference](#inspect-and-inventory-the-reference)
- [Choose TikZ or Matplotlib](#choose-tikz-or-matplotlib)
- [Rebuild in three passes](#rebuild-in-three-passes)
- [Handle text, equations, and quantitative marks](#handle-text-equations-and-quantitative-marks)
- [Validate against the reference](#validate-against-the-reference)
- [Deliver the reconstruction](#deliver-the-reconstruction)

## Define the reconstruction contract

Classify the reference before drawing:

| Mode | Preserve | May change |
|---|---|---|
| Faithful reconstruction | Scientific content, topology, text, equations, intentional layout, visual encodings | Raster artifacts, accidental misalignment, unavailable font |
| Scientific redesign | Scientific content, topology, labels, equations, data provenance | Composition, spacing, hierarchy, palette, framing, annotation placement |
| Aesthetic-only reference | Reusable visual grammar only | Scientific content must come from the user's separate specification |

Interpret “make this schematic better” as **scientific redesign** unless the user
requests exact reproduction. Define better as clearer hierarchy, cleaner
alignment, accessible encodings, legibility at final size, editable source, and
vector output—not added scientific content.

Preserve the reference file unchanged. If the desired output size, document
font, or fidelity mode is discoverable from the active project, use it. Ask one
focused question only when the answer changes scientific meaning, editability,
or delivery format.

## Inspect and inventory the reference

Inspect the image at original resolution before using a resized preview. Use
crops for small labels or dense regions, but never overwrite the original.
Record its pixel dimensions, aspect ratio, color mode, and transparency.

Build a task-local content ledger:

| Field | Record |
|---|---|
| Panels/groups | Count, reading order, titles, grouping devices |
| Entities | Count, labels, shapes, roles, repeated classes |
| Relations | Source, target, arrow direction, line style, label |
| Equations | Exact symbols, subscripts, superscripts, operators, delimiters |
| Quantitative marks | Axes, ticks, units, scales, curves, markers, color maps |
| Layout anchors | Alignment lines, margins, repeated gaps, relative sizes |
| Style roles | Ink, background, semantic colors, line weights, typography |
| Ambiguities | Unreadable text, occlusion, unclear direction, uncertain meaning |

Treat OCR as a draft transcription only. Verify every scientific label and
equation visually. Do not infer a subscript, sign, arrowhead, unit, or variable
from context when a different reading would change the science.

Distinguish structural problems worth fixing from intentional encodings worth
preserving. Common structural problems include uneven spacing, weak hierarchy,
label collisions, inconsistent arrowheads, accidental low contrast, and
decorative boxes that do not express grouping.

## Choose TikZ or Matplotlib

Choose from the content, target workflow, and required editability—not from the
reference's file extension.

| Signal | Prefer |
|---|---|
| Discrete nodes, boxes, arrows, braces, flowcharts, equations | TikZ |
| Native LaTeX typography or document macros | TikZ |
| Repeated relative positioning and all-vector geometry | TikZ |
| Plots, trajectories, sampled curves, scalar/vector fields, image panels | Matplotlib |
| Geometry computed from a model or source data | Matplotlib |
| Rapid Python iteration or later coupling to analysis code | Matplotlib |
| Computed raster field plus vector annotations | Matplotlib, or hybrid when TikZ supplies the overlays |

When both are suitable, use Matplotlib for the fastest review loop and TikZ for
native LaTeX integration. Do not use a generative image renderer for equations,
scientific text, data marks, or topology.

Verify the chosen toolchain before authoring. For TikZ, verify the intended TeX
engine and vector converter. For Matplotlib, use the non-interactive Agg backend.
Do not create a raster image and wrap it in SVG merely to satisfy a vector
deliverable.

## Rebuild in three passes

### 1. Semantic skeleton

Recreate every panel, entity, relation, label, equation, and encoding with
minimal styling. Establish the reading order and arrow topology first. Compare
the skeleton with the content ledger before polishing.

Use named primitives:

- TikZ: semantic `tikzset` styles, named nodes, relative positioning, and
  reusable macros for repeated glyphs.
- Matplotlib: functions that accept an `ax`, return their artists, and use
  patches, paths, annotations, and transforms rather than baked pixels.

### 2. Geometric system

Define a logical canvas and derive placement from anchors, grids, or normalized
coordinates. Express repeated gaps and sizes as constants. Avoid independent
pixel-by-pixel coordinates and avoid tracing antialiased boundaries.

Preserve meaningful spatial relationships, but normalize accidental offsets.
Route connectors so that arrowheads, labels, and crossings remain unambiguous.
Use explicit z-order or TikZ layers: background fields, containers, connectors,
entities, labels, and annotations.

### 3. Design refinement

Apply the selected aesthetic profile after content parity is established.
Improve hierarchy with restrained differences in size, weight, color, spacing,
and grouping. Keep prose and equations typographically distinct. Encode every
critical color distinction with a second cue such as shape, line style,
direction, symbol, or direct label.

Remove decoration only when it carries no scientific or grouping function.
Report any intentional merge, omission, relabeling, or rearrangement.

## Handle text, equations, and quantitative marks

- Transcribe prose as renderer-safe text and equations as verified TeX math.
- Preserve capitalization, symbols, units, signs, indices, and operator
  precedence. Do not “correct” scientific notation silently.
- If text is unreadable, leave a conspicuous source-code placeholder and ask the
  user before final delivery; do not guess.
- If a raster curve represents measured or simulated data, request the source
  data for a quantitative redraw. Without data, reproduce it only as an
  explicitly illustrative trace.
- If the reference contains a photograph or computed raster field, retain that
  declared raster layer at sufficient effective resolution and reconstruct all
  labels and overlays as vectors.

## Validate against the reference

Validate at the intended physical size, not only at a zoomed editing size.

Check semantic parity:

- same panel and entity counts;
- exact text, equations, units, and time labels;
- same connectivity, arrow direction, line/marker meaning, and legend mapping;
- same quantitative provenance and scale claims;
- every omission or design change intentional and reported.

Check design quality:

- clear reading order and hierarchy;
- consistent alignment, padding, line weights, and arrowheads;
- no collisions, clipping, ambiguous crossings, or tiny labels;
- critical distinctions survive a common color-vision-deficiency simulation;
- vector text and paths remain sharp at final size.

Use a same-size side-by-side comparison for every reconstruction. An optional
low-opacity overlay or edge comparison can diagnose geometry in faithful mode,
but do not chase pixel similarity after an intentional redesign. Re-open and
inspect both final vector files rather than trusting the source canvas.

## Deliver the reconstruction

Deliver the editable `.tex` or `.py` source, one vector PDF, and one SVG whose
text has been converted to paths. Do not emit a PNG preview. In the completion
response, list the renderer choice, intentional improvements, font or tool
fallbacks, illustrative elements, and unresolved ambiguities.

Keep the source deterministic and parameterized. Preserve the reference beside
the outputs or link to its existing location; never replace it with the redraw.
