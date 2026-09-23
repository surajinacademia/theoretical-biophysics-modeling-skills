# Learning dynamics: computed Matplotlib variant

[Editable Python source](matplotlib-figure.py) ·
[Native TikZ alternative](../../tikz/learning-dynamics/README.md) ·
[Library](../../../../references/library.md)

These original illustrative examples organize imposed motion, learning, and
retrieval. They do not reproduce the data or scientific content of
arXiv:2406.07856. The historical style name retains construction aliases backed
by the shared Minimalist profile.

Run the command from the skill root with an approved output path. This example
uses real CMU/LaTeX typography and native TikZ heads; read the
[common build and trust requirements](../../../../references/tutorials.md).

## Design lesson

- **Use when:** a figure must distinguish an imposed protocol, the response it
  produces, and a subsequent outcome. Training spans the imposed-motion and
  response panels; retrieval occupies its own area.
- **Why it helps:** phase headings group the first two panels as training and
  identify the last as retrieval, adding structure above the individual panel
  labels. The trajectory, sampled positions, and
  changing opacity show progression within retrieval without adding a separate
  box for every time point.
- **Borrow:** align related panels under a shared phase heading and reserve
  stronger separation for a change of experimental or modeling role. Keep the
  field quiet enough that positions and paths remain readable above it.
- **Check after adapting:** preserve time-encoding opacity and computed
  coordinates. Panel order should not imply that an imposed-motion sketch is a
  measured trajectory or that the retrieval path is merely a decorative arrow.

## Build and scientific context

[PDF](figures/learning-dynamics-2406.pdf) ·
[SVG](figures/learning-dynamics-2406.svg)

```bash
python3 scripts/build_example.py learning-dynamics --output-dir /tmp/schematic-learning-computed
```

Outputs are `learning-dynamics-2406.pdf` and `learning-dynamics-2406.svg`.
The Python source integrates `τ_g dg/dt = g_target − g` by forward Euler,
with `τ_g = 1.35`, targets `0.82` and `0.28`, and timestep `0.025`.
Retrieval integrates `dr/dt = χ g ∇C` in the source's anisotropic Gaussian
field. Preserve the field parameters, initial state, durations, mobility, and
response combination when adapting presentation alone.

Headings, short color keys, and whitespace separate phases. A computed scalar
field sits beneath entities and trajectories; its raster layer is intentional,
while scientific labels and heads remain vector. Time-encoding opacity and
trajectory coordinates carry meaning and must not be replaced by a generic
context-opacity role. Inspect the distinction between the imposed-motion
schematic and the computed retrieval coordinates.

Inspect phase order, response signs and labels, line-pattern redundancy, native
arrow endpoints, and final-size legibility. Keep the illustrative distinctions
and apply the [export contract](../../../../references/vector-export.md).
