# Scientific Analysis-to-Plot Workflow

Read this reference before creating or changing an analysis-to-plot path.
It preserves scientific meaning from completed data through the saved figure.
For appearance-only changes, use [design-style.md](design-style.md) and preserve
the established plotted values and definitions.

## Contents

- [Establish the Scientific Target](#establish-the-scientific-target)
- [Use a Direct Analysis Path](#use-a-direct-analysis-path)
- [Handle Pandas Tables by Scientific Grain](#handle-pandas-tables-by-scientific-grain)
- [Keep Only Scientific Selections](#keep-only-scientific-selections)
- [Preserve Scientific Identity](#preserve-scientific-identity)
- [Separate Analysis from Display](#separate-analysis-from-display)
- [Limit Abstraction](#limit-abstraction)
- [Verify Proportionally](#verify-proportionally)

## Establish the Scientific Target

Recover these facts from the request, current code, and stored data before
editing:

- the observable;
- the scientific unit, such as a cell, particle, trajectory, replicate, or run;
- the requested comparison or grouping;
- the time and spatial domain.

Do not create a separate specification, filter ledger, or validation framework
for these facts. Ask only when different answers would change the scientific
result and the repository does not resolve them.

## Use a Direct Analysis Path

This skill governs analysis structure, not programming-language syntax.
The bundled Python templates are examples, not a requirement to rewrite an
established analysis in Python.

Prefer this structure:

```text
load completed data
select the scientifically defined population
calculate the named observable
aggregate only when the comparison requires it
plot the result
save or return the figure
```

Keep this path visible in one script, function, or short notebook sequence when
practical. Combine simple stages when that makes the path easier to trace.

Use the natural data representation. Use table operations for tabular records.
Keep trajectories, fields, images, and vector data in arrays or domain objects
unless a table has a clear scientific purpose.

Reuse an established domain-library operation when it already defines the
observable or selection. Do not reproduce library internals in the plot code.

## Handle Pandas Tables by Scientific Grain

For Pandas or another tabular representation, first identify what one input row
represents. This is the table grain. Identify the named columns that form its
scientific key. Define the required result grain before each aggregation. Do not
create a schema document or validation object when one sentence or the direct
grouping columns make the grain clear.

Before editing a Pandas or other dataframe data path, read
[pandas-data-handling.md](pandas-data-handling.md). It owns the
operational rules for identity before concatenation, aggregation weighting,
keyed joins, alignment, missingness, duplicate keys, reshaping, and direct
plot-ready columns. Apply those rules alongside the scientific selections and
display boundaries below.

## Keep Only Scientific Selections

Default to no ad hoc exclusions. Keep a selection only when one of these reasons
applies:

- it is part of the observable definition;
- it defines the requested comparison;
- it applies the requested or protocol-defined time or spatial domain;
- it enforces a documented run-quality or protocol-validity criterion;
- it removes a documented invalid sentinel;
- it satisfies a mathematical precondition.

Preserve the requested scientific definition, not undocumented legacy
filtering. If removing an undocumented filter changes reported values, show the
change and do not claim behavior preservation.

Place each selection next to the calculation it affects. Use a concise name or
comment when its scientific reason is not evident.

Never remove data because the plot looks noisy or crowded. Do not add automatic
quantile, interquartile-range, z-score, smoothing, or missing-value filters as a
generic precaution.

If an exclusion removes records from the requested population, report one
before-and-after count at the affected scientific unit. Stratify that count only
when differential removal could bias the requested comparison. Do not count an
ordinary requested group or domain as an exclusion. Do not build a filter report
object or audit table.

## Preserve Scientific Identity

- For tabular records, select and group by named identifiers, not current row
  positions.
- For ordered arrays or domain objects, use direct frame, time, spatial, or
  topology indices when those positions have scientific meaning. Do not create
  an identifier only to avoid a clear index.
- Decide whether selection membership is fixed by the observable or changes
  with state. Evaluate a fixed selection once. Recompute state-dependent
  membership for each relevant frame or time point.
- Preserve run and replicate identity until per-run or per-replicate values are
  complete.
- Make aggregation weighting agree with the named scientific unit and the
  quantity being estimated. Preserve existing weighting only after this match
  is established. Do not
  exchange equal-run weighting and pooled-observation weighting silently.
- For a paired or joint calculation, use one shared mask or a keyed join. For
  separate summaries of each observable, use observable-specific validity masks
  while retaining identifiers and sample counts.
- At each data boundary, check only relevant units, denominators, keys, shapes,
  or coordinates whose mismatch can change the result.
- Fail visibly on a real mismatch. Do not catch broad exceptions or substitute a
  plausible value.

## Separate Analysis from Display

Use all scientifically selected data to calculate observables and descriptive
summary statistics.

Classify sampling, smoothing, interpolation, and clipping by purpose. If a
transformation defines the observable or aligns measurements, keep it in the
analysis and state its scientific reason.

Apply display-only arrow thinning, point decimation, rasterization, or clipping
after the reported values are complete. Prefer regular spatial thinning that
preserves the defined groups. Do not select displayed observations by their
result value by default.

If vector legibility requires a documented magnitude threshold or local-maximum
rule, show the full field and disclose the rule near the plot. Never feed
display-only data back into a reported value.

When display sampling is necessary, make it reproducible only to the degree
needed to reproduce the figure. Do not create a general sampling subsystem.

## Limit Abstraction

- Prefer direct library calls for one plot or a small related set.
- Keep a helper only when it is reused, names a non-trivial scientific
  calculation, or creates a useful test boundary.
- Accept a few explicit plot calls when they are clearer than a loop or wrapper.
- Do not add a class, registry, configuration schema, callback system, strategy,
  plugin layer, or generic filter pipeline for a small plot task.
- Do not wrap one dataframe or plotting call without adding scientific meaning.
- Do not add checks for states that an inspected upstream contract already
  excludes.

Stop simplifying when another removal would hide the observable definition,
scientific unit, comparison, domain, or data identity.

## Verify Proportionally

Choose only the checks that match the change:

Keep comparison and diagnostic checks outside the final analysis-to-plot path
unless one guards an input boundary required for correctness.

- For a population-changing exclusion, compare the affected scientific-unit
  count.
- For a simplification, compare representative values and keyed plot inputs.
  Use an existing or justified floating-point tolerance.
- For changed aggregation, compare run or replicate counts and the named
  weighting.
- For a new plot without a baseline, inspect representative values and final
  plot inputs. Do not invent an equivalence test.
- Run the smallest relevant existing test or render when execution is in scope.

For figure changes, follow the [saved-artifact completion gate](../SKILL.md#completion-gate).
Inspect each changed figure; do not create a separate review report or render
unrelated gallery examples. A code-only simplification needs relevant numerical
checks, not a redesign or gallery rebuild.

Do not claim preserved results when these checks did not run. Do not expand this
verification into a general validation system.

Before completion, confirm that a reader can trace data from load to plot in one
pass. Every remaining selection must have a scientific reason. Every
presentation-only transformation must stay outside the analysis path.

For the repository evidence behind this structure, read
[repository-patterns.md](repository-patterns.md) only when the
current code leaves two competing structures unresolved.
