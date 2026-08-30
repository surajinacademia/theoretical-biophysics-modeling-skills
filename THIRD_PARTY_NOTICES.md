# Third-Party Notices

## Learning Dynamics visual profile

The `schematic-designer` skill includes an independently documented visual-
grammar profile informed by:

Rituparno Mandal, Rosalind Huang, Michel Fruchart, Pepijn G. Moerman,
Suriyanarayanan Vaikuntanathan, Arvind Murugan, and Vincenzo Vitelli,
*Learning dynamical behaviors in physical systems*, arXiv:2406.07856v1,
<https://arxiv.org/abs/2406.07856>.

The arXiv record identifies the paper license as Creative Commons Attribution
4.0 International: <https://creativecommons.org/licenses/by/4.0/>.

The profile records independently measured or inferred visual grammar. It does
not include the paper, its data, photographs, bespoke illustrations, or panel
compositions. The bundled example science is original and illustrative. This
notice does not imply endorsement by the paper authors.

## TikZ example gallery

The bundled TikZ gallery has mixed licensing. Its `manifest.json` records the
title, author, source, and license for each example.

- Twelve TeXample adaptations and one tikz.net adaptation use CC BY-SA 4.0.
- One Stack Exchange adaptation uses CC BY-SA 3.0.
- Three independent examples use this repository's MIT license.
- `tkz-linknodes.sty` retains its separate LPPL/GPL notice.

Read `skills/schematic-designer/examples/tikz-gallery/LICENSE.md` and the
entry-specific manifest record before copying or adapting a gallery example.

## Software and fonts

Python, NumPy, Matplotlib, TeX engines, and PDF-to-SVG converters are not
redistributed. Their own licenses apply when a user installs them.

The bundled PDF specimens embed font subsets. The SVG specimens convert text
to paths and do not depend on installed fonts.

- CMU Sans Serif is part of Computer Modern Unicode and uses the SIL Open Font
  License 1.1. See <https://ctan.org/pkg/cm-unicode> and
  `THIRD_PARTY_LICENSES/CMU-SIL-OFL-1.1.txt`.
- The embedded Computer Modern Type 1 math fonts are distributed by AMSFonts
  under the SIL Open Font License 1.1. See
  <https://ctan.org/pkg/amsfonts> and
  `THIRD_PARTY_LICENSES/AMSFonts-SIL-OFL-1.1.txt`.
- Latin Modern uses the GUST Font License. See
  <https://ctan.org/pkg/lm> and
  `THIRD_PARTY_LICENSES/Latin-Modern-GUST-FONT-LICENSE.txt`.
