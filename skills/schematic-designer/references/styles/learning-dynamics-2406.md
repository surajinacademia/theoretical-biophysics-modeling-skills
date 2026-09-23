# Learning-dynamics construction vocabulary

The historical asset name is retained for existing example source. Its palette,
typography, stroke sizes and arrowheads now come from the shared
[Minimalist profile](minimalist.md); it is not a competing default style.

The original construction study was inspired by Mandal et al.,
[Learning dynamical behaviors in physical systems](https://arxiv.org/abs/2406.07856).
The local examples use an original illustrative learning-and-drift model, not
the paper's data, photographs or scientific claims.

Useful construction choices remain: organize imposed motion, learned response
and retrieval in reading order; separate phases with headings and whitespace;
place computed scalar fields beneath crisp entities, paths and annotations.
A phase ribbon is optional when it communicates a real grouping. A decorative
card around every panel is unnecessary.

The Python compatibility asset maps existing names such as `training`,
`retrieval`, `blue`, and `red` to the owner's live palette. The TikZ asset loads
`minimalist-profile.sty` and exposes matching aliases. Generate that support
file with the shared helper and declare both styles to `render_tikz.py`.
Assign scientific meanings explicitly; the compatibility names do not establish
universal positive/negative or training/retrieval color semantics.

Use the shared type, stroke, marker, opacity and spacing roles at final size.
CMU text and real LaTeX equations are mandatory, with no font fallback. All
arrows use native TikZ terminals; preserve inhibition bars and meaningful
vector lengths. Keep time-encoding opacity or magnitude-encoding color when
those are part of the science. The [worked examples](../tutorials.md) explain
how to run the updated native-TikZ and computed-panel versions.
