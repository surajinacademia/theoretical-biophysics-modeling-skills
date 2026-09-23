---
name: scientific-notebook
description: Create, maintain, execute, or review Jupyter notebooks for scientific research, theoretical modeling, simulations, and scientific data analysis. Use for new research notebooks and targeted edits to existing .ipynb files; standalone model documents and business dashboards are outside this skill's scope.
---

# Scientific Notebook

Deliver one ordinary, editable `.ipynb` containing the scientific explanation,
calculation, and figures. Add interpretation only when explicitly requested.
Maintain the notebook directly; do not create a paired Python implementation or
Jupytext synchronization unless requested. Reuse established project modules.

## Scientific authority and scope

For work on a scientific model's formulation, hypotheses, implementation,
verification, validation, or supporting evidence, read and apply
[computational-modeling](../computational-modeling/SKILL.md), with or without code
changes. It governs the scientific contract, evidence, provenance, and model
version identity; this skill owns notebook organization and maintenance.
Standalone non-model data analysis, plotting, and isolated scientific explanations
do not trigger the modeling skill. For data analysis, check provenance, units,
exclusions, missing values, normalization, uncertainty, and the path from data to
reported quantities directly.

Data guidance is optional. [data-guidance.md](references/data-guidance.md) records
the narrow adaptations from OpenAI's public MIT source. Consult an installed
`data-analytics:jupyter-notebooks` skill when useful, retaining this structure and
the user's scientific question. Do not copy proprietary cached files or activate
a formal model-document workflow merely because the notebook explains equations.

Establish the question, assumptions, equations or transformations, units, and
initial/boundary conditions. Resolve ambiguities that change results. Scale
verification to the claim through relevant limiting cases, invariants, numerical
convergence, or statistical checks. A successful kernel run alone is insufficient.

## Notebook structure

For new notebooks, use these section roles with as many focused cells as the work
needs. There is no fixed cell count. The single starting layout is
[notebook-template.ipynb](assets/notebook-template.ipynb); the helper loads it.

1. **Opening Markdown:** a descriptive title and a short explanation of the
   question and approach. Use bullets only when helpful, with no mandatory count.
   Preserve the user's shortened opening; do not expand it to fill a template.
2. **Setup and computational functions:** imports, relevant paths, shared
   plotting style, and scientific/analysis functions. Use short preceding
   Markdown for substantive methods; simple imports need no explanatory cell.
   Explain the physical or analytical reasoning and how the calculation proceeds;
   include equations or short pseudocode when useful. Avoid formal “Inputs” and
   “Outputs” sections.
   Group simple setup sensibly; split substantive methods when clarity needs it.
3. **Technical comments in code:** explain numerical methods, algorithms,
   approximations, scientific implementation choices, and non-obvious programming
   decisions beside the code. Do not narrate obvious syntax.
4. **Plotting function definitions:** provide editable plotting code, without
   additional prose explaining how that plotting code works. Use the plotting-style selection described below. Explain plotted quantities in methods or,
   when requested, interpretation.
5. **Parameters:** use one plain `PARAMETERS` dictionary by default for adjustable
   model, calculation, and plotting settings, immediately before the final
   execution and plotting calls. Use plain physical names such as `length`,
   `gravity`, and `mass`, with units in comments. Functions accept parameters
   explicitly; avoid duplicate definitions, captured later settings in default
   arguments, or simulations during definitions. Split numerical settings only
   when the task or established notebook warrants it.
6. **Results:** execute calculations, meaningful scientific checks, and plotting
   calls. Show plots primarily; add a table only when needed to answer the
   question. Keep checks quiet on success. Do not print verbose diagnostics,
   software-version lists, hashes, or raw arrays.

Interpretation is optional and must be explicitly requested. The template has
none. When requested, write it after inspecting executed results and distinguish
supported findings, uncertainty, and limitations. Do not restore a section the
user removed or treat interpretation metadata as permission to add prose.

## Plotting style

Use the project's configured plotting style. When the owner's separately
installed `minimalist` package is available, preserve its `use_style('white')`
setup and `figsize()` API; do not copy its defaults into cells. The portable
scaffold uses Matplotlib's built-in default when that optional package is absent.
The fallback uses DejaVu Sans and Matplotlib's default color cycle and does not
reproduce the owner's theme. Do not install a PyPI package merely because it has
the same name. Preserve an explicit user style choice.

Use `plt.subplots()` for one panel and an explicit `(width, height)` in inches for
portable multi-panel layouts. With `minimalist`, `aspect_ratio` in `figsize()`
means height divided by width. No installation occurs in notebook cells.
Install the helper dependencies from `requirements.txt` in a prepared project
environment; `examples/requirements.txt` adds the scientific example dependencies.
The saved nonlinear-pendulum example retains figures rendered with the owner's
black `minimalist` theme. Rebuilding without the optional package uses native
Matplotlib dark-background styling and explicit figure dimensions; scientific
calculations are unchanged. Exact reproduction of the saved appearance requires
the optional theme.

Keep the notebook runnable top-to-bottom from a fresh kernel without hidden
state. Use paths relative to the project or notebook with their base explicit;
create output directories during execution when needed. Keep relevant sources,
parameter values, seeds, and numerical tolerances traceable. Record additional
environment or model identity only when needed, without verbose printed output.
Save figures or numerical outputs needed for the requested handoff, retaining
inline figure outputs and editable plotting code. Label axes, units, colorbars,
and uncertainty; use comparable scales when the comparison requires them.

## Create or maintain

Inspect the target project and existing notebook before choosing either route.
Use [the shared helper](references/helper.md) for repeated notebook mechanics;
it uses `nbformat` and `nbclient`, not a model-specific assembly script.

- **New notebook:** scaffold with the helper and replace authoring prompts with
  task-specific explanations, functions, settings, and calls. The scaffold cannot
  execute successfully until the computation is implemented.
- **Existing notebook:** inspect cell IDs, sources, metadata, attachments, and
  saved outputs. Edit, insert, or remove only cells needed for the request. Keep
  the user's unrelated prose, code, order, IDs, and customizations. Do not rebuild
  the notebook from a template or impose this structure wholesale during a narrow
  edit. Inspect again if the file changed while work was in progress.
- **One cell or a few cells:** answer or edit just the requested cells. Do not
  scaffold a new notebook, reorganize sections, or automatically execute the full
  notebook. Check the affected behavior and dependencies proportionately. A prose
  change does not require rerunning a simulation.

Preserve unaffected cells, IDs, metadata, attachments, and valid outputs. The
helper preserves outputs for Markdown-only edits. For code changes, explicitly
list affected code cells when their dependencies are understood; otherwise it
clears all code outputs conservatively. It does not infer dependencies. A
computational change preserves `not_requested` (also the default for absent
interpretation metadata); tracked requested interpretation is flagged for review.
Metadata flags are not visible warnings. Review affected existing
claims without adding an unrequested section. External data, imported code,
assumptions, or environment changes can also invalidate results.

For operations outside the helper's bounded patch vocabulary, use `nbformat`
directly with the same preservation and stale-output rules. Temporary cell-source
or patch files are authoring intermediates, not a second maintained notebook
implementation. Avoid hand-editing notebook JSON.

## Execute, inspect, and finish

Review code and dependencies before execution; the helper is not a sandbox. Use
the project environment and an appropriate timeout. Do not install packages from
cells or create scheduled/remote runs merely to complete the layout. Use the
project's run workflow for long calculations; do not substitute a cheaper problem.

For a new notebook or a requested whole-workflow revision, complete these checks:

1. Validate notebook format and execute top-to-bottom in a fresh kernel using
   `nbclient` (the helper's `execute` command). Select the project kernel and a
   suitable per-cell timeout; execution uses the notebook's directory. Retain
   successful outputs in the same notebook. Errors and timeouts mean incomplete
   execution.
2. Check the task-specific scientific acceptance evidence. Inspect the saved
   notebook in a notebook viewer, or render it locally and inspect the saved
   figures and text at reading size. Look for clipped labels, missing outputs,
   misleading scales, and claims that disagree with the results.
3. If interpretation was explicitly requested, write or revise it after reviewing
   results, preserving execution outputs. Recheck affected calculations or plots
   after subsequent changes; prose-only edits do not require another run.
4. Confirm there are no scaffold prompts, unsupported conclusions, or stale
   results presented as current. Link the notebook and briefly state what was
   established and any consequential limits.

For targeted edits, validate notebook format and test the changed behavior with
its required prerequisites. Inspect changed plots if any. Reuse the project
kernel or an isolated check when appropriate; the helper's `execute` command is
always a full fresh-kernel run, not a targeted execution command. Broaden execution
when dependencies or findings cannot otherwise be verified, rather than treating
every edit as a whole-notebook assignment. Preserve unrelated valid results.

Completion means the requested scope is implemented and its relevant scientific
checks and affected outputs are inspected. State any remaining execution,
dependency, or visual-inspection gap and the exact action needed to resolve it;
never call a partial check full-notebook verification. Keep any existing
interpretation consistent with that status. Stop when the requested work is complete.

See [nonlinear-pendulum.ipynb](examples/nonlinear-pendulum.ipynb) for the editable,
executed example of the complete workflow. Its equations, parameters, and checks
illustrate this problem; they are not defaults for other scientific tasks.
