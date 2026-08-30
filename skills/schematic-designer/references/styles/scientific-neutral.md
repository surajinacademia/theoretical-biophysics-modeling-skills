# Aesthetic Profile: scientific-neutral

Use this quiet, portable profile when a journal, project, or user-supplied
visual grammar does not take precedence. It changes only presentation, never
data, equations, units, scale, topology, or physical relationships.

## Visual grammar

- Use a white canvas, near-black text and outlines, and no decorative page tint.
- Use the colorblind-aware qualitative cycle only for unrelated categories; use
  sequential color for magnitude and diverging color only around a meaningful
  center.
- Give every critical color distinction a label, marker, line style, direction,
  or shape cue.
- Favor direct labels, restrained line weights, and whitespace. Add a frame or
  ribbon only when it communicates grouping or phase.
- Use lower-case panel tags (a), (b), and so on at consistent upper-left
  positions.

## Tokens and use

The authoritative executable tokens are
assets/styles/matplotlib/scientific_neutral.py and
assets/styles/tikz/scientific-neutral.sty.

Use CMU Sans Serif when available, with DejaVu Sans, Arial, or Latin Modern
Sans as the local fallback. Use native mathematical typography for variables
and equations. The assets provide near-black ink, muted and faint neutrals, a
blue/orange/green/red/purple/teal cycle, and standard panel, title, body, and
small-text sizes.

Apply the profile before figure-specific layout, then follow
references/renderer-workflows.md and references/vector-export.md.
