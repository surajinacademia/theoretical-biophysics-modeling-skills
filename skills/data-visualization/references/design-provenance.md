# Design Provenance

Reviewed 2026-09-21 against Chen Liu's `figures4papers` commit
`3c181f85e82c6f24948fcaaf3be6696102b41d8d`. This is provenance for the adaptation,
not a required plotting reference.

## Architecture Adapted

The upstream package connects visual outcomes to design rationale, tutorials,
and projects through a short task router. Our earlier skill concentrated on
scientific grain, identity, weighting, missingness, and analysis/display
separation. The updated structure combines those strengths:

- A short entrypoint routes design, tutorials, implemented API, and gallery;
  the scientific workflow remains required when a data path changes.
- Each of eight local cases pairs its source, teaching CSV, and PDF. Three
  complete templates and a scoped style adapter provide executable starting points.
- Completion includes inspection of the actual saved artifact at intended size.

The reviewed upstream installable skill contains six Markdown files; its gallery
assets and plotting scripts sit elsewhere in the repository. Its tutorials say
the documented helper API has no shared implementation. We keep our executable
resources inside the skill and document only implemented interfaces.

The optional owner configuration retains the Minimalist style; the public
portable fallback uses native Matplotlib styles without copying owner source. Upstream large
canvases, heavy spines, preferred-method colors, and legend-only panels are not
inherited defaults. Nor is a truncated bar baseline a general comparison rule.
The upstream trend API exposes a shadow switch without interval arrays or a
calculation; our examples explicitly label sample SD across runs and valid counts.

Schematic-designer already had routing, renderer guidance, styles, examples, and
an inspection gate. The useful shared lesson is connecting a goal and design
decision to executable source and visible output. Its composite diagrams and
exact vector-delivery contract remain separate from ordinary quantitative plots.

## Reuse Boundary

The upstream license is **CC BY-NC 4.0**, not this plugin's MIT license.
Only organizational ideas were adapted: local prose, templates, style adapter,
overlay, synthetic inputs, and PDFs are original work. No upstream code, images,
datasets, manuals, or history are bundled or executed. Future copying requires
review of the exact material, attribution, and reuse terms; the local license
does not relicense upstream content. Gallery PDFs are neither paper excerpts nor
scientific findings.

## Owner Dependency

The inspected optional package is Suraj Sahu's `minimalist` **3.0.0**; its
`STYLE.md` documents appearance and `src/minimalist/__init__.py` implements
the API. The owner uses Python 3.13. Machine-specific installation paths remain
in private maintenance records; the package is not copied into the skill.
The public workflow also supports the documented native Matplotlib fallback.

The integration consumes local style resources and public Python APIs, performs
no installation or network request, and does not edit the owner package. See
[api.md](api.md#runtime-and-scoped-style) for dependencies and context behavior,
and [design-style.md](design-style.md) for the palette fallback limitation.
The continuous-function example follows the owner's dense analytic evaluation
and bilinear-display pattern with its own formula and data, without copying the
demonstration code. Only the explicitly approved skill export is intended for public distribution;
the external owner package is not bundled.

## Reviewed Upstream Sources

- [entrypoint](https://github.com/ChenLiu-1996/figures4papers/blob/3c181f85e82c6f24948fcaaf3be6696102b41d8d/scientific-figure-making/SKILL.md)
- [design theory](https://github.com/ChenLiu-1996/figures4papers/blob/3c181f85e82c6f24948fcaaf3be6696102b41d8d/scientific-figure-making/references/design-theory.md)
- [tutorials](https://github.com/ChenLiu-1996/figures4papers/blob/3c181f85e82c6f24948fcaaf3be6696102b41d8d/scientific-figure-making/references/tutorials.md)
- [demo index](https://github.com/ChenLiu-1996/figures4papers/blob/3c181f85e82c6f24948fcaaf3be6696102b41d8d/scientific-figure-making/references/demos.md)
- [repository gallery and packaging](https://github.com/ChenLiu-1996/figures4papers/blob/3c181f85e82c6f24948fcaaf3be6696102b41d8d/README.md)
- [API specification](https://github.com/ChenLiu-1996/figures4papers/blob/3c181f85e82c6f24948fcaaf3be6696102b41d8d/scientific-figure-making/references/api.md)
- [common patterns](https://github.com/ChenLiu-1996/figures4papers/blob/3c181f85e82c6f24948fcaaf3be6696102b41d8d/scientific-figure-making/references/common-patterns.md)
- [license](https://github.com/ChenLiu-1996/figures4papers/blob/3c181f85e82c6f24948fcaaf3be6696102b41d8d/LICENSE)
