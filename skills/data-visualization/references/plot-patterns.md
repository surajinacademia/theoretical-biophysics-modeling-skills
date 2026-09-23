# Choose the Plot from the Scientific Question

## Contents

- [Time Courses](#time-courses)
- [Replicate Comparisons and Distributions](#replicate-comparisons-and-distributions)
- [Scatter Plots](#scatter-plots)
- [Parameter Maps](#parameter-maps)
- [Continuous Functions](#continuous-functions)
- [Vector Fields](#vector-fields)

Use the smallest plot that makes the requested comparison visible. These
patterns assume completed observables. They do not define new simulation
outputs, filters, or inferential analyses. Use
[pandas-data-handling.md](pandas-data-handling.md) for grain and aggregation, and
[design-style.md](design-style.md) for visual treatment.
The [PDF gallery](gallery.md) provides visible examples of these decisions,
including paired change, distributions, scatter, discrete parameter maps, and
smooth continuous-function heatmaps.

| Question | Useful starting form | What the reader must be able to see |
| --- | --- | --- |
| How does a quantity change over time? | Per-run trajectories and a condition summary | Time coordinates, run variation, summary definition, and contributing run counts |
| How do conditions compare across runs? | Individual run points with a descriptive summary | Each run, group size, and the meaning of any interval |
| How broad or structured is a distribution? | Histogram with separate group-colored filled bars; individual points for small samples | Common bin boundaries, counts or stated normalization, and the scientific unit |
| How do two observables relate? | Scatter plot | Which two values belong to the same scientific unit |
| How does a scalar vary across two parameters? | Parameter map | Actual parameter coordinates, scalar units, and unsampled or missing combinations |
| How does a known continuous function vary over a domain? | Smooth heatmap from dense function evaluation | Function definition, domain, normalization, and evaluation resolution |
| What direction does a vector field take? | Quiver plot over a scalar background when useful | Direction, magnitude convention, coordinates, and any display thinning |

## Time Courses

The [time-course template](../assets/templates/timecourse.py) starts from one
completed value per `(condition, run, time)`. Its condition summary gives each
contributing run one value at a time coordinate. Error bars labeled SD show
between-run spread; they do not establish confidence intervals or a treatment
effect. Apply the shared [visual defaults](design-style.md).

Show individual trajectories when their variability or differing behavior is
part of the question. If only a summary is legible, preserve counts and describe
what it summarizes. A connected line suggests continuity: do not bridge an
undefined measurement gap without making the gap visible. Unequal time grids
need an explicit scientific alignment decision before aggregation; drawing a
smooth line is not that decision.

## Replicate Comparisons and Distributions

The [replicate template](../assets/templates/replicate_comparison.py) displays
one completed scalar per `(condition, run)` as individual points with a mean
and SD. This is a useful default for small descriptive comparisons because
the observations remain visible. Horizontal offsets only separate coincident
points; they have no scientific value.

Connect observations across conditions only when a genuine shared identifier
defines the pairing. Matching row positions or reusing the label `run 1` in two
independent ensembles does not establish a pair. The bundled template does not
assume pairing.

If shape matters, show a distribution rather than only a mean and interval.
Default to a bar histogram with separate group-colored filled bars, clear
boundaries, visible gaps, and a zero count baseline.
Use common bin boundaries when comparing groups, and label counts or the stated
normalization. Grouped bars within each shared bin prevent one group from
covering another; explain that the side-by-side offsets distinguish groups and
do not change bin membership. Bin width changes the apparent shape, so state
the boundaries or make them recoverable from the source. Preserve all selected
observations and identify whether they represent runs, cells, or another
scientific unit. Use an ECDF or density only when explicitly requested or when
the defined scientific question requires it; neither is the style default.

## Scatter Plots

Construct each point from two values for the same scientific unit, using their
shared key. A diagonal identity line is meaningful only when both axes represent
commensurate quantities. Use common limits and equal aspect if visual distance
from identity is the intended comparison. Otherwise choose scales for the
actual question and label both axes independently. A scatter plot alone does
not justify a fitted relationship or causal interpretation.

## Parameter Maps

The [parameter-map template](../assets/templates/parameter_map.py) expects one
precomputed scalar per `(x, y)` pair. It does not pool repeated runs or invent a
reducer for duplicate parameter pairs. Complete that scientific aggregation
before plotting.

Preserve nonuniform parameter coordinates rather than displaying equally
spaced matrix cells under numeric labels. Cell boundaries inferred between
sampled centers are a display convention, not additional measurements. Use a
coordinate-based scatter plot instead if rectangular cells imply a sampled
domain that the data do not support. Leave absent combinations visibly missing;
do not interpolate a continuous parameter landscape by default.

## Continuous Functions

Keep this representation separate from a discrete parameter map. The gallery
evaluates the analytic function `f(x, y) = tanh(2x) · [0.5 + 0.5 cos(πy)]`
on a 201 × 101 coordinate grid over `x ∈ [−1, 1]`, `y ∈ [0, 1]`, with a
diverging scale fixed to `[−1, 1]` and centered on zero. Bilinear image
interpolation provides a smooth display between these dense evaluations; it
does not change the stored function values. Report the formula, domain,
evaluation resolution, and display interpolation. Do not use this treatment to conceal missing cells
or imply an unmeasured continuum in a parameter sweep.

## Vector Fields

Specify whether arrow length represents magnitude or whether arrows are
normalized to emphasize direction. Include a key with units when lengths carry
magnitude. Use physical coordinate aspect when geometry matters. Regular
display thinning may reduce overlap, but compute any reported field summary
before thinning and disclose the display rule. The core skill owns the
analysis/display boundary; this reference supplies no new selection rule.
