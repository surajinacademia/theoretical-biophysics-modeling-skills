# Quantitative Design Style

Use this reference for appearance changes; use [plot-patterns.md](plot-patterns.md)
for the scientific encoding. The [gallery](gallery.md) demonstrates the shared
style across all eight cases.

## Optional Minimalist Identity

When available, the owner's installed `minimalist` package supplies CMU Sans Serif, Computer
Modern mathtext, thin boxed axes, inward ticks, frameless legends, and its native
warm-to-cool qualitative palette. Do not copy or reorder that palette or
silently substitute a font or theme. Colors identify groups without implying
that one condition is scientifically preferable.

[publication.py](../assets/styles/publication.py) applies the package through
`paper_style()` and the adjacent [overlay](../assets/styles/paper.mplstyle).
The [API reference](api.md#runtime-and-scoped-style) owns dependency and context
mechanics, including draw-time marker gaps. No LaTeX engine is required.

The portable fallback is documented in [api.md](api.md#runtime-and-scoped-style):
DejaVu Sans and native Matplotlib colors, with through-going error bars. Saved
gallery examples retain the owner theme; a portable rebuild will look different.

## Shared Roles in the Executable Examples

Choose physical output size first. The 85 × 70 mm default is a starting point,
not a journal requirement. Apply each text role at the same final point size
across related figures, even when canvas widths differ. Reflow, widen, or split
a crowded plot rather than shrinking one legend or scaling a wide figure down.

| Role | Default at final placement |
| --- | --- |
| Body, axes, ticks, legends, notes | 8 pt CMU Sans Serif (DejaVu Sans in fallback) |
| Panel tag | 9 pt actual bold face |
| Point / outline | 5 pt diameter / 0.8 pt; scatter area is 25 pt² |
| Mean mark / error cap | 11 pt / 3 pt |
| Pairing connector | 0.65 pt black at 0.5 opacity; measured points stay opaque |
| Dashed / dotted line | 3–2 pt / 0.7–1.5 pt, independent of stroke width |
| Layout padding / panel gap | 0.8 / 2 base-font units in `tight_layout` |

These roles come from `FONT_PT`, `LINE_PT`, `MARK_PT`, `OPACITY`, `LAYOUT`,
`MARKERS`, `LINESTYLES`, and `DASH_PT`. Notes reserve the lower 12% of the canvas.
Change a role consistently if the destination requires it. The installed CMU
bold face needs `FontProperties(..., weight="bold", stretch="expanded")`;
ordinary bold lookup can resolve to the regular face.

Use equally sized hollow markers: `markerfacecolor="none"`, `marker_gap=True`.
The gap removes the error-bar segment inside its own marker without painting
the face; `marker_gap=False` explicitly allows through-going segments. Place
summary whiskers beside raw points so they do not cross unrelated hollow
markers. Light reference lines or grids are useful only when they aid reading.

## Color and Quantitative Encodings

Reuse a named group-to-style mapping. The categorical templates accept the same
full `--group-order` list across figures, including absent groups, to preserve
color, marker, and dash indices. Without it, they sort observed group names.
Mean marks, error bars, and legend text match the group's exact plot color;
neutral explanatory text remains dark and gallery headings remain bold black.
Keep marker or dash cues alongside pale legend colors and check readability.
Do not silently recolor one panel or depend on color alone for identity.

Use labeled error bars rather than filled uncertainty ribbons or areas beneath
curves. Histogram bars are **filled** with their group color, with visible gaps,
shared bin boundaries, and a zero count baseline. Heatmap colors also remain
part of their quantitative encoding.

- Sequential values: `minimalist.get_cmap('sequential')` supplies `inferno`.
- Signed departures from a meaningful reference: explicitly center the
  normalization there. `minimalist.get_cmap('diverging')` supplies `pride` through
  `scicomap`; the package can silently construct a fallback if that dependency
  fails. The adapter does not guard this, so gallery reproduction needs a healthy
  `scicomap` dependency.
- Distinct states: use categorical colors, not a gradient implying numeric distance.

Fix color normalization across directly compared plots, or disclose independent
ranges. Label the colorbar with observable and units. Show missing cells distinctly;
missingness is not a low value. Preserve discrete parameter coordinates and
missing cells. Smooth continuous-function heatmaps require a stated function
and dense evaluation; they must not invent observations from a sparse sweep.

## Axes and Statistical Meaning

Name observable and units on each axis, including dimensionless quantities when
unclear. Keep scientific-notation scale factors visible. Bars require a zero
baseline; points and lines may use a restricted range when clearly shown, with
a disclosed zoom if it could exaggerate change. Log scales must suit the quantity
and cannot silently discard nonpositive values.

Define the scientific unit behind `n` and show changing counts when relevant.
Mean ± SD describes spread among included units, not uncertainty in the mean or
a confidence interval. [Pandas guidance](pandas-data-handling.md) defines grain,
weighting, and valid counts.

Follow the [completion gate](../SKILL.md#completion-gate): inspect the saved PDF
and assembled figures at intended size, compare visible values with the table,
and check a grayscale view when group identity uses color. Dense artists may
be rasterized inside the PDF while labels and axes remain vector. Temporary
inspection rasters are not additional deliverables.
