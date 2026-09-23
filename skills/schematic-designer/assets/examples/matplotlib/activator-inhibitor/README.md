# Activator–inhibitor: mechanism, profiles, and signed field

[Editable Python source](matplotlib-figure.py) ·
[Finished PDF](figures/activator-inhibitor.pdf) ·
[Finished SVG](figures/activator-inhibitor.svg) ·
[Library](../../../../references/library.md)

## Design lesson

- **Use when:** a reader must connect a mechanism to a spatial profile and its
  combined effect. The three panels answer different questions about the same
  two entities, giving the reader a reason to move through the figure.
- **Why it helps:** repeated entity colors connect the mechanism to its curves;
  activation heads and inhibition bars distinguish relations independently of
  color. The signed field changes to a zero-centered magnitude scale because
  the reader now needs the sign and strength of the difference.
- **Borrow:** carry identity across representations, then explicitly change the
  encoding when the quantity changes. Keep direct curve labels and the zero
  contour so the correspondence is visible without a long caption.
- **Check after adapting:** distinguish qualitative interaction ranges from
  plotted distances. Confirm that the profile crossing agrees with the field's
  zero contour; a coordinated palette cannot establish that scientific link.

## Build and scientific context

From the skill root, use an approved output path in place of the example path:

```bash
python3 scripts/build_example.py activator-inhibitor --output-dir /tmp/schematic-activator-inhibitor
```

The build writes `activator-inhibitor.pdf` and `activator-inhibitor.svg` using
Matplotlib PGF, real LaTeX/CMU, and native TikZ arrowheads. Follow the
[shared build and trust requirements](../../../../references/tutorials.md).

The toy figure prescribes Gaussian profiles
`u(x) = exp[-x²/(2σ_u²)]` and `v(x) = A_v exp[-x²/(2σ_v²)]`, with
`σ_u = 0.7`, `σ_v = 1.5`, and `A_v = 0.65`. Its two-dimensional field uses the
isotropic extension `r² = x² + y²` and displays `u − v`. These are prescribed
analytic profiles, not a simulated reaction–diffusion solution or experimental
data. Keep the mechanism geometry illustrative and distinguish its length cues
from the plotted coordinates.

The design connects entity labels, interaction marks, and curves. Activation
heads and inhibitory terminals retain different scientific meanings. The signed
field uses zero-centered normalization; its magnitude encoding takes precedence
over categorical palette roles. The dense scalar field is a declared scientific
raster layer embedded at 600 dpi; labels, annotations, and other vector geometry
remain separate. Do not treat this exception as permission to rasterize text or
the whole figure.

The source checks the sampled profiles, central values, and analytic zero
crossing before export. Inspect the zero contour, signed color scale, curve
labels, endpoint attachment, and inhibition bars in both formats at final size.
Apply all [export checks](../../../../references/vector-export.md) after adaptation.
