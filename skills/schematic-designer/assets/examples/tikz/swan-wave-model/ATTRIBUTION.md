# Attribution

SWAN wave model by Marco Miani.

Source: https://texample.net/files/swan-wave-model.tex

License: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); original terms continue to apply to this adaptation.

Archived curated input: `archives/imported-tikz-gallery/swan-wave-model/source.tex`.
SHA-256 of that archived source (not an upstream Git commit): `fd36d386c24a9baa9d5d4f948436cda1aec2535eeb6c035c738484ab7186bfd6`.

Changes: rebuilt preamble with the shared Minimalist palette, CMU text and Computer Modern math, native TikZ Latex heads, role-based strokes and text; adjusted spacing. All original entities, directed relations and equations retained. Corrected the label typo “Batymetry” to “Bathymetry”. SWAN geometric grid resolutions, contours and labels remain archival and illustrative; no physical interpretation has been changed.

Original notices:

```text
%Author: Marco Miani
%SWAN (developed by SWAN group, TU Delft, The Netherlands) is a wave spectral numerical model.
%For Simlating WAves Nearshore, it is necessary to define spatial grids of
%physical dominant factors (wind friction, dissipation) as well as define a COMPUTATIONAL
%grid on which the model performs its (spectral) calculations: budgeting energy spectra over
%each cell of the (computational) grid. Grids might have different spatial resolution and extension.
```

## Visual re-audit — 2026-09-22

Visual re-audit: moved the Shoreline annotation outside the grid transform so its CMU glyphs are no longer sheared. The annotation target is preserved. Corner labels now use dark ink beside their existing orange markers. Grid transforms, domains, mesh steps and contour coordinates are unchanged.
