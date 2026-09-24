# Implemented Interfaces and Resource Layout

## Contents

- [Resource layout](#find-the-right-file)
- [Runtime and style context](#runtime-and-scoped-style)
- [CSV templates](#three-csv-to-pdf-templates)
- [Runnable examples](#eight-runnable-examples)
- [Gallery and data commands](#gallery-and-teaching-data-commands)

Use these implemented interfaces with the [scientific workflow](analysis-workflow.md)
and [design rules](design-style.md).

## Find the Right File

```text
data-visualization/
├── SKILL.md                         # scope, resource router, completion gate
├── agents/openai.yaml               # discovery prompt
├── references/                      # analysis, design, tutorials, API, gallery index
├── assets/
│   ├── styles/                      # publication.py, pdf_output.py, paper.mplstyle
│   ├── templates/                   # three reusable CSV-to-PDF programs
│   ├── gallery.pdf                  # overview and eight teaching pages
│   └── examples/
│       ├── timecourse/              # source.py, data.csv, figure.pdf in each case
│       ├── replicate-comparison/
│       ├── paired-change/
│       ├── distribution/
│       ├── scatter/
│       ├── parameter-map/
│       ├── continuous-field/
│       └── metric-comparison/
└── scripts/
    ├── build_gallery.py             # run specimens and assemble the review PDF
    └── create_demo_data.py          # regenerate deterministic synthetic tables
```

## Runtime and Scoped Style

Individual figures require NumPy, Pandas, and Matplotlib. Install dependencies
from the skill's `requirements.txt` in a prepared environment; ReportLab and pypdf
are used only for gallery assembly. No LaTeX engine is needed. Commands perform
no installation or network request.

`paper_style()` uses a separately installed owner `minimalist` package when
available, retaining its palette, style resource, strict CMU Sans Serif lookup,
and draw-time marker-gap API. A broken installed theme or missing theme font
fails visibly. The theme and its fonts are not bundled; do not install a PyPI
namesake. Without the package, a warning discloses the native Matplotlib fallback:
DejaVu Sans, tab10 categorical colors, inferno sequential colors, and coolwarm
diverging colors. `get_cmap(role)` exposes the selected sequential/diverging map.
The fallback retains the physical size roles and hollow markers, but uses
through-going error bars and ignores `marker_gap`; it does not reproduce the
saved owner-themed gallery exactly.

Both routes apply neighboring `paper.mplstyle` and restore caller rcParams and
`Axes.errorbar`/`Axes.draw` even after an exception. These methods are temporarily
patched process-wide; avoid concurrent plotting threads. **Create, render, and
save inside the context.** The adapter does not call `minimalist.use_style()`.
When moving a template, preserve the neighboring `../styles/` directory with
`publication.py`, `pdf_output.py`, and `paper.mplstyle`. No external owner package
is required for the fallback.

## Three CSV-to-PDF Templates

From `skills/data-visualization/`, use:

```sh
python assets/templates/timecourse.py INPUT.csv OUTPUT.pdf --xlabel 'Time (h)' --ylabel 'Value (units)' --group-order Control Perturbed
python assets/templates/replicate_comparison.py INPUT.csv OUTPUT.pdf --xlabel 'Condition' --ylabel 'Value (units)' --group-order Control Perturbed
python assets/templates/parameter_map.py INPUT.csv OUTPUT.pdf --xlabel 'Parameter x (units)' --ylabel 'Parameter y (units)' --colorbar-label 'Value (units)'
```

| Template | Required columns and grain | Summary or display |
| --- | --- | --- |
| `timecourse.py` | `condition, run, time, value`; one completed value per condition/run/time | Equal-run mean and sample SD at each time; missing means break the line. |
| `replicate_comparison.py` | `condition, run, value`; one completed scalar per condition/run | All measured run points, equal-run mean and sample SD; deterministic horizontal offsets carry no measurement meaning. |
| `parameter_map.py` | `x, y, value`; one completed scalar per coordinate pair | Discrete cells respect numeric coordinates and retain missingness; no pooling or interpolation. |

All three accept `--xlabel` and `--ylabel`; only the map accepts
`--colorbar-label`. The first two accept `--group-order GROUP [GROUP ...]`.
Use the same full ordered group universe for related plots, including groups
absent from a particular CSV. This preserves palette, marker, and line-pattern
indices without adding data. Without the option, observed names are sorted.
Duplicate or incomplete group universes are errors, not requests to discard data.

The explicit output must end in `.pdf`, differ from the input, and have an
existing parent directory. Symlink paths are rejected. Relevant duplicate
scientific keys fail visibly. Blank measurements remain missing rather than
becoming zero. The [tutorials](tutorials.md) supply runnable inputs, expected
values, and the limits of each template's scientific contract.

## Eight Runnable Examples

Every directory under `assets/examples/` contains `source.py`, `data.csv`, and
`figure.pdf`. Run a case from the skill directory:

```sh
python assets/examples/distribution/source.py
python assets/examples/distribution/source.py --output /private/tmp/distribution-review.pdf
```

The default replaces that case's `figure.pdf`; `--output` selects another PDF.
The timecourse, replicate-comparison, and parameter-map sources invoke their
canonical templates. The other five contain their direct worked plot functions:
`paired_change()`, `distribution()`, `scatter()`, `signed_map()`, and
`metric_comparison()`. The continuous-field case retains `signed_map()` as its
function name. These functions read their case's teaching data and return a
Matplotlib figure; their entrypoints handle scoped styling and PDF output.
Adapt the relevant case directly rather than treating it as a general library.

## Gallery and Teaching-Data Commands

With all gallery dependencies available, from the skill directory:

```sh
python scripts/build_gallery.py
python scripts/build_gallery.py --output-dir /private/tmp/data-vis-gallery-review
```

The default rebuilds `assets/gallery.pdf` and each case's `figure.pdf`.
An alternative output root receives `gallery.pdf` and
`examples/<case>/figure.pdf`, leaving the bundled figures available for
comparison. All retained figure outputs are PDF.

To regenerate the eight co-located teaching tables deliberately:

```sh
python scripts/create_demo_data.py
```

This overwrites `assets/examples/<case>/data.csv` with deterministic synthetic
values. It runs no simulation. Existing tables are sufficient to rebuild the
figures; regenerating them is not a prerequisite. Inspect changed figures and
the assembled gallery before declaring a visual revision complete.
