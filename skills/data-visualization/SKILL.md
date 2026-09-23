---
name: data-visualization
description: Create, style, review, or simplify quantitative plots from completed biophysical simulation data, including ordinary paper-ready PDF figures. Use the visual gallery, a portable style adapter, and direct plotting templates while preserving scientific identity, weighting, and observable definitions. Do not use for simulation execution, generic data cleaning, inferential modeling, vasculogenesis media, or composite schematic design.
---

# Data Visualization Skill

Create clear quantitative figures from completed data with a direct, traceable
analysis path. Use the bundled style adapter for the visual
identity and the bundled examples to connect a question with its finished plot.

## Scope

Use this skill to create, style, review, or simplify a small number of
exploratory, diagnostic, comparative, or ordinary paper-ready quantitative
plots. A small grid of related quantitative axes remains in scope.

Do not use it for simulation execution or monitoring, generic dataframe cleanup
without a defined plot, inferential statistics, model fitting, or complex
cohort construction. `graph` owns vasculogenesis frames and MP4 files;
`schematic-designer` owns bespoke schematics, illustrations, composite
publication composition, and its exact vector-delivery contract.

An ancillary plot does not make an excluded analysis eligible. Apply this skill
only when the request separately defines an ordinary descriptive plot from
completed values.

If `code-simplifier` also applies, this skill owns scientific selections and
data meaning; that skill owns the wider preservation boundary and code shape.

## Route to the Needed Resource

Read the required workflow when the data path changes, then load only the
references needed for the task. Do not read every reference for a simple plot.

| Task | Resource and action |
| --- | --- |
| Create or change an analysis-to-plot path | **Read [analysis-workflow.md](references/analysis-workflow.md) before editing.** Preserve its scientific selection, identity, weighting, and analysis/display boundaries. |
| Change Pandas or another tabular data path | Also read [pandas-data-handling.md](references/pandas-data-handling.md) for grain, keys, joins, missingness, and aggregation. |
| Choose the quantitative encoding | Read [plot-patterns.md](references/plot-patterns.md). |
| Establish or review appearance | Read [design-style.md](references/design-style.md). |
| Use the style adapter, template CLI, or build commands | Consult [api.md](references/api.md), which documents implemented interfaces and the resource tree. |
| Start a time course, replicate comparison, or parameter map | Follow [tutorials.md](references/tutorials.md) and adapt the corresponding complete template. |
| Learn from a finished figure | Open the relevant PDF in [gallery.md](references/gallery.md), then its linked plotting source and teaching CSV. |
| Resolve competing analysis structures | Consult [repository-patterns.md](references/repository-patterns.md) only when the current code leaves a choice unresolved. |
| Understand architectural inspiration and reuse terms | Consult [design-provenance.md](references/design-provenance.md); it is not required for plotting. |

The gallery contains synthetic teaching values, not scientific evidence. Reuse
its design decisions and direct code structure with the actual completed data.
The templates are examples, not a reason to rewrite established analysis in
Python or introduce a general plotting framework.

## Shared Visual Defaults

Use `paper_style()` from [publication.py](assets/styles/publication.py).
It preserves the owner's separately installed `minimalist` package when available,
or warns and uses Matplotlib's native DejaVu Sans, tab10, inferno, and coolwarm
styles when absent. No owner theme, fonts, or palette source is distributed.
The portable fallback preserves physical sizes and hollow markers but draws
through-going error bars; `marker_gap` is ignored with the warning. **Create,
render, and save inside the context**. Runtime and context behavior are in
[api.md](references/api.md). Do not install a PyPI namesake of the optional theme.

- Match final physical font sizes across related plots: 8 pt text and 9 pt bold
  panel tags by default. Give wider figures more room instead of shrinking them.
- Use 5 pt hollow markers with 0.8 pt outlines, `markerfacecolor="none"`, and
  `marker_gap=True` when the optional theme is available. Explicit `marker_gap=False` permits through-going error bars.
- Match error bars and legend text to their group's plot color. Keep the same
  named group-to-style mapping across figures; overview headings are bold black.
- Use labeled uncertainty bars, no filled curve areas or ribbons. Histograms
  use group-colored **filled bars**, shared bins, clear gaps, and a zero baseline.
- Keep discrete parameter maps and missing cells distinct from smooth heatmaps
  of a stated function evaluated densely; never smooth sparse data for appearance.

[design-style.md](references/design-style.md) defines the remaining visual roles.
PDF is the default and the only bundled export. Honor another explicitly
requested ordinary plot format without inheriting schematic vector requirements.

## Completion Gate

Apply the proportional numerical checks in
[analysis-workflow.md](references/analysis-workflow.md#verify-proportionally)
when data handling changes. Do not claim preserved results without checking
representative values and the relevant scientific keys, counts, or weighting.

Save and visually inspect every changed figure at its intended physical size.
Check labels and units, group encodings, interval definitions, sample counts,
missingness, clipping, and overlap against the plot-ready data. For related
figures, inspect matching text and mark sizes in the assembled PDF; matching
source settings alone do not establish consistency after placement. A temporary
raster preview is an inspection aid, not an additional deliverable. State any
unavailable inspection capability rather than claiming visual verification.

For an explicitly requested non-PDF artifact, inspect that saved artifact.
Code-only simplification needs relevant numerical checks, not a redesign or
unrelated gallery rebuild. Confirm that a reader can trace load to plot in one
pass, every selection has a scientific reason, and display-only transformations
remain outside the analysis path.
