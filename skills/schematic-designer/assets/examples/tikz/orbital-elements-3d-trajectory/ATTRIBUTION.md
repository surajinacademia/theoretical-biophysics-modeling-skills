# Attribution: Inclined orbital trajectory

- Author of the archived source: schematic-designer maintainers.
- Archived source: `archives/imported-tikz-gallery/orbital-elements-3d-trajectory/source.tex` within this skill.
- Archived source SHA-256: `ab35869b83c03028b952f69e15f245a738f2ebada166079b238836420a015eb9`.
- Original page/pattern reference: https://github.com/f0nzie/tikz_favorites/blob/9506fd5643abb406197bed176ab9183484006dd1/src/physics-trajectory.tex
- License: MIT.
- Adaptation: schematic-designer maintainers, 2026.

The linked upstream file was only a high-level pattern reference for the independent archived implementation; no code from that unlicensed upstream file was copied. This adaptation starts from the repository’s MIT source.

MIT License

Copyright (c) 2026 Biophysics Simulation Workflow Skills contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Changes

Replaced historical styling with the generated shared Minimalist profile, CMU text, real Computer Modern LaTeX math, named palette colors, shared physical stroke/marker roles, and current Latex arrowheads. No archive was altered.

The archived illustrative geometry and inclination constants are retained. The incorrect “focus” label at the ellipse center is corrected to “Ellipse center”; no point was moved. This construction is illustrative, not an exact Keplerian orbit.

Central scientific labels use the shared body role (8 pt); only supporting notes use the smaller type role.

## Visual design revision

The orbital plane, full path, highlighted segment, body marker, and body label consistently use palette color 1, with context opacity distinguishing supporting geometry. The position vector and its label use palette color 6; the line of nodes and its label retain palette color 5. The inclination is a neutral angular measure rather than sharing the body color. Plane borders and the projection guide now use context strokes and opacity. Scientific coordinates, vectors, angles, and 8 pt central labels are unchanged.
