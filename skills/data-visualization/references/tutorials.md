# Three Direct Plotting Tutorials

## Contents

- [Change over time](#1-compare-change-over-time)
- [Completed run values](#2-compare-completed-run-values)
- [Two-parameter map](#3-show-a-scalar-across-two-parameters)

These templates turn completed per-run or per-coordinate values into ordinary
PDF plots. Their bundled inputs are **synthetic teaching data**. Use the
[gallery](gallery.md) to select a pattern and [api.md](api.md) for runtime,
imports, style context, and CLI contracts. Run commands from the skill directory
in a compatible environment; the explicit output directory must exist.

## 1. Compare Change over Time

**Question:** how does the observable evolve across conditions, and how much
do the supplied runs differ at each time?

[timecourse.py](../assets/templates/timecourse.py) takes one completed value per
`(condition, run, time)`; it does not aggregate raw cells or particles.

```sh
python assets/templates/timecourse.py assets/examples/timecourse/data.csv /private/tmp/data-vis-timecourse.pdf --group-order Control Perturbed --xlabel 'Time (h)' --ylabel 'Front position (µm)'
```

The summary is an equal-run mean and sample SD (`ddof=1`) at each time. The
legend reports measured runs per time, or their range when counts vary. Blank
measurements contribute neither to mean nor count; one valid run has a mean but
no sample SD. Missing means break the line.

**Check the teaching CSV:** both conditions have six measured runs at each of
seven times. At `time=0`, both means are 10 µm and sample SDs approximately
1.12250 µm. At `time=12`, Control has mean 36.4 µm and Perturbed 39.097025 µm;
both sample SDs are approximately 2.02049 µm. These check aggregation of invented
inputs, not a prediction.

The template uses the union of supplied times as each condition's expected grid.
It cannot infer a time absent from every run: include a row with blank `value`
for such an expected time. Use another scientifically justified alignment when
this common-grid convention does not fit.

**Adapt and inspect:** replace completed values and units, retain a stable full
`--group-order` across related plots, and add individual trajectories when run
behavior matters. Check mean ± SD endpoints, a line break at missing means, and
counts including zero where appropriate. A repeated `(condition, run, time)` key
fails: establish a scientific reducer or correct the input rather than dropping
duplicates to obtain a plot.

## 2. Compare Completed Run Values

**Question:** how do conditions compare while retaining each measured run?

[replicate_comparison.py](../assets/templates/replicate_comparison.py) takes one
completed scalar per `(condition, run)`.

```sh
python assets/templates/replicate_comparison.py assets/examples/replicate-comparison/data.csv /private/tmp/data-vis-replicates.pdf --group-order Control Perturbed --xlabel 'Condition' --ylabel 'Speed (µm/min)'
```

Run points surround a group-colored equal-run mean and sample SD; the summary
sits beside observations to avoid crossing hollow markers. Deterministic
horizontal offsets have no measurement meaning. Labels show measured `n`, or
`n=measured/supplied` when measurements are missing. They cannot count runs never
supplied. Blank values stay missing; measured zero remains data.

**Check the teaching CSV:** both groups have `n=6`. Control has mean 2.0 µm/min
and sample SD approximately 0.374166 µm/min; Perturbed has mean 2.5 µm/min and
sample SD approximately 0.447214 µm/min. All twelve run values remain visible.

**Adapt and inspect:** compute the scientifically defined scalar within each run
first; do not count pooled cell observations as runs. Verify every point, count,
and interval. One measured value has a point and mean but no fabricated SD.
Repeated `(condition, run)` keys fail: define a per-run scalar or choose the
time-course template. Genuine pairing requires the keyed paired-change example
in the [gallery](gallery.md), not independently numbered runs or row order.

## 3. Show a Scalar across Two Parameters

**Question:** how does a completed scalar vary over two numeric parameters,
including combinations without measurements?

[parameter_map.py](../assets/templates/parameter_map.py) takes one completed
`value` per `(x, y)` pair, without pooling repeated pairs.

```sh
python assets/templates/parameter_map.py assets/examples/parameter-map/data.csv /private/tmp/data-vis-parameter-map.pdf --xlabel 'Adhesion (dimensionless)' --ylabel 'Noise (dimensionless)' --colorbar-label 'Order (dimensionless)'
```

Numeric coordinates are cell centers. Interior boundaries lie halfway between
neighbors; outer boundaries extend by half the nearest spacing. This preserves
nonuniform spacing without interpolating measurements. Missing pairs and blank
values appear gray with a missing-data key. At least two distinct coordinates
on each axis and one measured value are required.

**Check the teaching CSV:** five x and four y coordinates define twenty pairs;
nineteen are measured and `(0.5, 2)` is missing. Values at `(0.1, 0.5)` and
`(1.4, 0.5)` are 0.14345709 and 0.74327807. Missingness must not acquire a
zero-valued color or enter the color limits as zero.

**Adapt and inspect:** complete scientific run aggregation before creating the
input and label parameters, scalar, and units. Use common color limits for
direct comparisons. Signed departures need explicit centered normalization
while preserving discrete cells; dense continuous-function rendering belongs
to the separate [gallery case](gallery.md). Check low/high colors, missingness,
unequal spacing, and colorbar readability. Repeated `(x, y)` pairs fail instead
of silently averaging; a singleton axis fails because no neighbor defines cell
width. Use points or a line for that case.

All tutorials retain the [Pandas identity and weighting rules](pandas-data-handling.md),
[visual defaults](design-style.md), and saved-artifact
[completion gate](../SKILL.md#completion-gate). Successful execution alone does
not establish a readable figure.
