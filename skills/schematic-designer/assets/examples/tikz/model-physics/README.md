# Standard model of physics

[Editable source](source.tex), [PDF](figures/figure.pdf), [SVG](figures/figure.svg), [attribution and license](ATTRIBUTION.md).

## Design lesson

- **Use when:** many entities share a compact property schema and also belong to overlapping families. Repeated particle cards make this a structured reference figure.
- **Why this choice helps:** a large symbol identifies each particle; mass and name occupy stable positions, while colored corner tabs locate color charge, electric charge, and spin. A single external legend explains these positions. Generation columns, braces, and enclosing interaction boundaries add relationships across cards without repeating their explanations. The outside-Standard-Model graviton remains visually separated.
- **Borrow:** give the entity symbol priority, keep equivalent properties in fixed slots, and explain compact visual encodings with an external legend. Preserve the card geometry and depth cues when they are part of the requested design.
- **Adaptation check:** blank slots do not establish zero values. The inherited values are explicitly historical; reuse the construction, not its values as a current reference. Original miniature text scales are retained at the owner's request, including very small corner labels. Inspect at the intended reading size before adapting this compact layout.

From the skill root:

```sh
python3 scripts/build_example.py tikz-model-physics --output-dir /tmp/tikz-model-physics
```

Requires the shared Minimalist profile, LuaLaTeX, CMU fonts and the supported PDF-to-outlined-SVG converter. This is a design example. The previously documented correction of the Higgs heading to scalar boson and the note identifying all inherited numerical values as historical remain.

## Current visual design

The owner requested restoration of the original appearance with a palette change only. The rounded particle cards, shadows, large symbols, colored corner tabs, miniature legend, original coordinates and text scales, generation headings, braces, and interaction boundaries are restored. Minimalist colors and their white tints replace the earlier palette. CMU text, true Computer Modern math, and native LaTeX annotation heads use the current rendering support.

This example deliberately retains its original compact typography and shadows; it does not demonstrate the shared 8 pt body-size default. This is a case-specific preservation decision, not a new default for other figures. All historical numerical values remain unchanged, and the graviton retains its dashed boundary outside the Standard Model.

## Verified export

The restored native PDF is **107.48 × 82.59 mm**. Its compact local font scales
are intentionally retained from the original design. PDF fonts are embedded;
SVG labels, cards, property tabs and group marks remain vectors. The converter
represents the 18 original blur shadows with embedded opacity masks, recorded
individually in the TikZ manifest. These masks contain no diagram labels or
particle content. Both final formats were visually inspected after rebuilding.
