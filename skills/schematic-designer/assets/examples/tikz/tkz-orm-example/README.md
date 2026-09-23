# Object-role modeling notation

[Editable source](source.tex), [PDF](figures/figure.pdf), [SVG](figures/figure.svg), [attribution and license](ATTRIBUTION.md).

From the skill root:

```sh
python3 scripts/build_example.py tikz-tkz-orm-example --output-dir /tmp/tikz-tkz-orm-example
```

Requires the shared Minimalist profile, LuaLaTeX, CMU fonts and the supported PDF-to-outlined-SVG converter. This is a design example. The package-specific ORM source is redrawn with native TikZ; binary role boxes, uniqueness spans, mandatory participation dots, reading direction markers and all three textual rules are preserved. This source has no tkz-orm package dependency.

## Design lesson

- **Use when:** A relationship diagram has a formal notation whose small marks carry constraints as important as the entities themselves.
- **Why this arrangement helps:** Employee sits between the rank/car and date relationships, with paired role boxes making each binary predicate explicit. White entity ovals and role boxes retain the formal boundaries without broad color fills. Mandatory dots, uniqueness bars and reading-direction markers retain distinct meanings; constraint and date labels use the body role. Numbered textual rules sit below the network, keeping the longer conditions readable without crowding the connectors.
- **Transfer to a new figure:** Separate entity identity, relation structure and additional rules. Allocate clearance for notation marks before arranging labels, and link longer qualifications by identifiers instead of fitting them onto edges.
- **Check before adapting:** A bar's span and a dot's attachment determine which constraint is expressed. Verify each against the intended model after moving nodes. Plain participation connectors must retain their ORM meaning; adding directional arrowheads would introduce a different reading.

## Current visual design

Entity ovals and binary role boxes retain their formal outlines with white interiors instead of tinted backgrounds. Constraint and date labels use the 8 pt body role so they remain part of the main reading. Mandatory dots, uniqueness spans, reading markers, and all three textual rules are retained; these shapes carry notation and are not ornamental boxes.
