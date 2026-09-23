# Chemoattraction: computed panel helper

[Editable Python source](matplotlib-panels.py) ·
[TikZ compositor and final figure](../../tikz/chemoattraction/README.md) ·
[Model context](../../tikz/chemoattraction/model-plan.md) ·
[Library](../../../../references/library.md)

This folder owns the Python source for four intermediate panels. The maintained
TeX compositor and the only final PDF/SVG pair live in
`assets/examples/tikz/chemoattraction/`. The
[composition's Design lesson](../../tikz/chemoattraction/README.md#design-lesson)
explains how native panel sizes preserve hierarchy across the two renderers.

## Build and inspect

From the skill root, build the complete figure with an approved output path:

```bash
python3 scripts/build_example.py chemoattraction --output-dir /tmp/schematic-chemoattraction
```

The builder runs this source in fresh temporary storage to produce
`field-profile.pdf`, `concentration-map.pdf`, `simulation-summary.pdf`, and
`phase-diagram.pdf`. It declares those inputs to the TikZ compositor and exports
`chemoattraction-hybrid.pdf` and `chemoattraction-hybrid.svg`. Do not copy panels
from the archive or maintain duplicate final renders in this helper directory.
Regenerate panels when their intended physical size changes.

## Scientific boundary

These are deterministic illustrative computations, not experimental data or a
validated chemotaxis model. The 49 sweep cells show actual sampled heading-order
values, not an interpolated phase boundary. The `K0` profile is normalized at
`r = 0.05`, not at its singular origin. The map includes all three sources;
its sensing circle does not impose the trajectory calculation's cutoff. The
inherited zero-gradient angle convention can bias isolated cells.

Read the [complete scientific context and limitations](../../tikz/chemoattraction/README.md#build-and-scientific-context)
before changing or interpreting these panels. Preserve computations and
scientific encodings when adapting presentation; the retained model plan does
not establish the illustrative builder's validity. Follow the
[common build requirements](../../../../references/tutorials.md).
