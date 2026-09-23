# Learning dynamics: native TikZ variant

[Editable TikZ source](source.tex) ·
[Computed Matplotlib alternative](../../matplotlib/learning-dynamics/README.md) ·
[Library](../../../../references/library.md)

These original illustrative examples organize imposed motion, learning, and
retrieval. They do not reproduce the data or scientific content of
arXiv:2406.07856. The historical style name retains construction aliases backed
by the shared Minimalist profile.

Run the command from the skill root with an approved output path. This example
uses real CMU/LaTeX typography and native TikZ heads; read the
[common build and trust requirements](../../../../references/tutorials.md).

## Design lesson

- **Use when:** a conceptual story needs discrete entities, an analytic response
  plot, and an illustrative path in one native TeX composition.
- **Why it helps:** aligned panel tags and titles let the reader scan phases,
  while direct labels and distinct line patterns separate the response channels.
  An open x/y frame and one response-axis pair reduce redundant framing.
  Opaque pale entity fills preserve categorical identity over the field halo;
  clipping keeps that halo inside the retrieval region.
- **Borrow:** establish panel anchors and label clearances before adding paths
  or field layers. Keep analytic curve parameters separate from manually placed
  entities, and place annotations on the same coordinate construction they
  describe.
- **Check after adapting:** the halo and retrieval path are illustrative. Reusing
  the computed variant's visual organization does not make this trajectory
  numerically equivalent to it. If quantitative motion matters, use computed
  coordinates rather than adjusting this path by eye.

## Build and scientific context

[PDF](figures/learning-dynamics-tikz.pdf) ·
[SVG](figures/learning-dynamics-tikz.svg)

```bash
python3 scripts/build_example.py learning-tikz --output-dir /tmp/schematic-learning-tikz
```

Outputs are `learning-dynamics-tikz.pdf` and `learning-dynamics-tikz.svg`.
The builder generates the shared style in fresh temporary storage and declares
it together with `learning-dynamics-2406.sty` before LuaLaTeX compilation.

The native source plots the analytic response
`g_target (1 − exp[−t/τ_g])` with `τ_g = 1.35` and target values
`0.82` and `0.28`. The retrieval path,
particle positions, and halo layers are illustrative TikZ geometry, explicitly
not to scale; they are not the numerically integrated Python trajectory. This
variant teaches native layout and annotation, not numerical equivalence between
the two renderers.

Inspect phase order, response signs and labels, line-pattern redundancy, native
arrow endpoints, and final-size legibility. Keep the illustrative distinctions
and apply the [export contract](../../../../references/vector-export.md).

## Current visual design

The retrieval frame is open along x and y, and the response plot has one axis pair rather than overlapping duplicate strokes. Ordinary entity fills use opaque preblended palette tints, preventing the halo from changing their apparent category. The intentionally faded starting entity and trajectory samples retain their progression encoding. The analytic response constants and illustrative retrieval geometry are unchanged.
