# Pandas Data Handling for Biophysical Plots

Read this reference when Pandas or another dataframe library is material to the
analysis-to-plot path. Apply its structural rules, not a fixed syntax style.

## Contents

- [Start with Table Grain](#start-with-table-grain)
- [Combine Runs Once](#combine-runs-once)
- [Choose an Operation by Its Effect on Grain](#choose-an-operation-by-its-effect-on-grain)
- [Join without Changing the Population Accidentally](#join-without-changing-the-population-accidentally)
- [Keep Missingness and Zero Distinct](#keep-missingness-and-zero-distinct)
- [Treat Duplicate Keys as a Scientific Question](#treat-duplicate-keys-as-a-scientific-question)
- [Reshape Once and Deliberately](#reshape-once-and-deliberately)
- [Keep the Pandas Path Small](#keep-the-pandas-path-small)
- [Evidence](#evidence)

## Start with Table Grain

Table grain means what one row represents. Common grains include:

- one cell or particle at one frame;
- one trajectory at one lag time;
- one run at one output time;
- one replicate for one condition;
- one component of one field sample.

Name the complete key for that grain, such as `(run_id, cell_id, frame)`. Keep
the key as named columns unless an index directly represents the same stable
scientific identity. Sort by entity and scientific time before a lag,
difference, rolling, or cumulative calculation. Do not assume file order or the
current row order is time order. Apply each ordered calculation within the full
entity key. Enforce the frame or time separation required by the observable. Do
not bridge an undefined temporal gap merely because two rows become adjacent
after sorting.

Define the result grain before an operation that can change row count. A direct
analysis can state this through the grouping columns and output names. Do not
build a schema class, grain registry, or separate table contract for one plot.

## Combine Runs Once

For multiple completed runs, use this structure:

```text
read each run -> attach stable run and replicate keys -> concatenate once
-> scientific selection -> observable -> required aggregation -> plot
```

Attach run, replicate, condition, and source identity before concatenation when
those keys are not already stored. Do not try to recover identity later from the
combined row index. Collect compatible tables before concatenation instead of
growing one dataframe inside a loop. Normalize only columns used by the
observable, keys, grouping, or plot.

## Choose an Operation by Its Effect on Grain

- A row selection keeps the grain and changes the population.
- A column calculation keeps the grain and adds or changes an observable.
- A grouped transform keeps one result aligned with each input row.
- A grouped aggregation changes the grain to one row per grouping key.
- A join combines attributes or observations through scientific keys.
- A reshape changes representation and should not change scientific meaning by
  itself.

Use direct built-in column, aggregation, and transform operations when they
express the calculation. Use a row callback, group callback, or manual loop only
for a real ordered or cross-row scientific calculation that the direct
operations cannot express clearly.

For nested observations, aggregate in the scientific hierarchy. If the target
weights runs equally, first create one value per run and comparison coordinate,
then summarize those run values. Do not pool unequal numbers of cells, frames,
or particles and label the pooled row count as the replicate count.

## Join without Changing the Population Accidentally

Use the full key shared by both tables. Select the join population from the
scientific question. Enforce the expected cardinality at the join when the
library supports it; in Pandas, the merge cardinality option is preferable to a
new preflight framework.

Stop if a supposed one-to-one or many-to-one join multiplies rows. A many-to-
many join is valid only when every resulting pairing is intended. If unmatched
keys can remove requested units or introduce missing attributes, inspect one
unmatched-key count at the affected scientific unit. Do not retain a permanent
join-audit table when the count resolves the question.

Use automatic dataframe index alignment only when the index is the intended
scientific key. Equal row counts do not prove alignment. For paired values from
one table, prefer one shared validity mask. For values from separate tables,
join or align by the full key before calculation.

## Keep Missingness and Zero Distinct

Classify missing data by role:

- A missing required identity or group key is an input-boundary failure.
- A missing measurement affects only observables that require that measurement.
- A measured zero is data, not missingness.
- An absent run or group is not a row of zeros.

Do not apply a blanket missing-value removal across unrelated columns. Do not
fill missing measurements, time points, or runs with zero, a group mean, or the
previous value unless that operation is part of the scientific definition.

For a joint calculation, use the same complete cases for all paired values. For
separate summaries, keep each observable's valid values and retain its valid
scientific-unit count per group. Make clear whether a reported count is rows,
cells, trajectories, runs, or replicates.

## Treat Duplicate Keys as a Scientific Question

Repeated values in one identifier column can be correct. A cell identifier, for
example, repeats across frames. Test uniqueness only for the full key that is
expected to identify one row.

If the full key repeats, determine whether the rows are technical duplicates,
separate measurements, or an omitted dimension. Stop or add the missing key.
Aggregate repeated rows only when the reducer defines the requested observable.
Never use blanket duplicate removal to make a join or reshape succeed.

## Reshape Once and Deliberately

Keep long form when group, condition, observable, or component names naturally
vary by row and the plot accepts that form. Use wide form when a paired or
matrix-like calculation needs aligned columns. Reshape near that calculation or
plot, preserve identity columns, and avoid repeated long-to-wide-to-long cycles.

A plain pivot requires one value for each index-and-column key combination. If
repeated combinations exist, do not use an aggregating pivot as an implicit
cleanup step. Define the scientific aggregation first or correct the grain.

## Keep the Pandas Path Small

- At an unverified input boundary, check required keys and observable columns
  once. Do not repeat the check when an inspected upstream contract guarantees
  them.
- Make one explicit working table only when mutation or isolation is needed. Do
  not copy after every selection.
- Do not rely on chained assignment or on changes to a filtered view affecting
  its source.
- Do not add a generic cleaner, dtype mapper, join manager, aggregation
  registry, dataframe subclass, or validation report for one analysis.
- Do not add chunking, distributed dataframes, categorical optimization, or a
  new storage layer until measured data size or runtime requires it.
- Keep plot ordering and labels as presentation choices. Do not encode display
  order as an analytical filter.

The final plot-ready table should contain the keys needed to trace each plotted
value, the named observable, the requested grouping columns, and any requested
uncertainty or valid-unit count. Pass those columns directly to the plot. Do not
convert a table to nested dictionaries or lists and then rebuild it.

## Evidence

Biophysics repository evidence is recorded in
[repository-patterns.md](repository-patterns.md). In particular, Trackpy shows
keyed particle/frame operations, one-time reshape, and joined paired values;
saenopy shows per-file and group-level aggregation; PhysiCell shows category
attachment before concatenation and direct long-form plotting. Do not open that
evidence reference unless the current code leaves two competing structures
unresolved.

The official Pandas documentation establishes the relevant operation semantics:

- [grouped aggregation and transform](https://pandas.pydata.org/docs/user_guide/groupby.html)
  distinguish reduced-grain output from same-grain output and recommend direct
  built-in operations before custom group callbacks;
- [merge, join, and concatenation](https://pandas.pydata.org/docs/user_guide/merging.html)
  document join populations, many-to-many row multiplication, cardinality
  validation, and one-time concatenation;
- [missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)
  documents that removal and filling change which values enter calculations;
- [reshaping](https://pandas.pydata.org/docs/user_guide/reshaping.html) documents
  that a plain pivot requires unique key combinations while a pivot table
  aggregates them;
- [index alignment](https://pandas.pydata.org/docs/user_guide/indexing.html#series-assignment-and-index-alignment)
  documents label-based assignment; and
- [copy-on-write](https://pandas.pydata.org/docs/user_guide/copy_on_write.html)
  documents why chained assignment and filtered-view side effects are not a
  reliable data path.

These sources support operation semantics. The observable, scientific unit,
keys, valid population, and aggregation order still come from the model and the
analysis question.
