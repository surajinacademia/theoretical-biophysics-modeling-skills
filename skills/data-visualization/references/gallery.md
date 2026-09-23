# Quantitative Figure Gallery

Open the [nine-page PDF gallery](../assets/gallery.pdf): an overview and eight
case pages. Each case below co-locates runnable source, synthetic teaching data,
and a PDF at its intended physical size. The values are deterministic examples,
not simulation findings or scientific evidence. The overview preserves native
placement scale and gives the wider related-metrics case two columns.

| Example PDF | Use and principal pitfall | Plotting source | Teaching CSV |
| --- | --- | --- | --- |
| [01 · Time courses](../assets/examples/timecourse/figure.pdf) | Show time dependence with equal-run mean and SD; do not confuse spread with a confidence interval. | [source.py](../assets/examples/timecourse/source.py) → [timecourse.py](../assets/templates/timecourse.py) | [timecourse/data.csv](../assets/examples/timecourse/data.csv) |
| [02 · Replicate comparisons](../assets/examples/replicate-comparison/figure.pdf) | Keep run values visible around a descriptive summary; horizontal offsets carry no measurement meaning. | [source.py](../assets/examples/replicate-comparison/source.py) → [replicate_comparison.py](../assets/templates/replicate_comparison.py) | [replicate-comparison/data.csv](../assets/examples/replicate-comparison/data.csv) |
| [03 · Paired changes](../assets/examples/paired-change/figure.pdf) | Connect the same run before and after; pairing requires its key, not matching row positions. | [source.py — paired_change](../assets/examples/paired-change/source.py) | [paired-change/data.csv](../assets/examples/paired-change/data.csv) |
| [04 · Distributions](../assets/examples/distribution/figure.pdf) | Use clearly separated group-colored filled histogram bars with shared bin boundaries and a zero count baseline; preserve every selected observation. | [source.py — distribution](../assets/examples/distribution/source.py) | [distribution/data.csv](../assets/examples/distribution/data.csv) |
| [05 · Relationships](../assets/examples/scatter/figure.pdf) | Show two observables from each run with separate units; the scatter implies no fitted or causal relation. | [source.py — scatter](../assets/examples/scatter/source.py) | [scatter/data.csv](../assets/examples/scatter/data.csv) |
| [06 · Parameter maps](../assets/examples/parameter-map/figure.pdf) | Preserve nonuniform coordinates and visible missingness; cells do not establish a continuous phase diagram. | [source.py](../assets/examples/parameter-map/source.py) → [parameter_map.py](../assets/templates/parameter_map.py) | [parameter-map/data.csv](../assets/examples/parameter-map/data.csv) |
| [07 · Continuous functions](../assets/examples/continuous-field/figure.pdf) | Evaluate a stated analytic function densely for a smooth heatmap; do not smooth sparse parameter measurements or fill missing cells. | [source.py — signed_map](../assets/examples/continuous-field/source.py) | [continuous-field/data.csv](../assets/examples/continuous-field/data.csv) |
| [08 · Related metrics](../assets/examples/metric-comparison/figure.pdf) | Repeat group encodings across two ordinary quantitative axes; retain each metric's units and scale. | [source.py — metric_comparison](../assets/examples/metric-comparison/source.py) | [metric-comparison/data.csv](../assets/examples/metric-comparison/data.csv) |


The first, second, and sixth cases invoke the canonical CSV templates; use the
[tutorials](tutorials.md) to adapt them. The other cases use direct functions in
their `source.py`. They are teaching examples, not a general plotting API.

From `skills/data-visualization/`, run one case or rebuild the gallery:

```sh
python assets/examples/distribution/source.py --output /private/tmp/distribution-review.pdf
python scripts/build_gallery.py --output-dir /private/tmp/data-vis-gallery-review
```

Omitting `--output` replaces that case's `figure.pdf`; omitting `--output-dir`
replaces the bundled gallery and figures. See [api.md](api.md) for runtime
requirements and deliberate data regeneration. After visual changes, inspect
the standalone PDF and assembled overview using the
[completion gate](../SKILL.md#completion-gate).
