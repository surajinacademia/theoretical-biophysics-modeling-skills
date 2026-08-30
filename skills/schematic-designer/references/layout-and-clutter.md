# Layout and Clutter Control

Use this before finalizing a schematic or hybrid composition.

## Core rule

Detailed objects are allowed; free-sized and unassigned objects are not.

- Assign each object to a semantic zone before drawing.
- Reuse renderer tokens from `assets/styles/` for typography, colors, and common
  object sizes.
- Clip fields, halos, and contextual backgrounds to their zones.
- Route arrows through whitespace lanes and avoid crossing object bodies.
- Put labels outside an object when text would force the object to resize.
- Use a single primary hierarchy device per level: whitespace, ribbon, rail, or
  frame.
- Reserve a fixed header lane inside every panel. Give the panel tag and title
  separate anchors with enough horizontal clearance for the rendered tag width;
  never place both at one nominal coordinate.

## Useful panel templates

| Template | Zones | Use |
|---|---|---|
| Left-to-right | input / mechanism / output | signaling, migration, causal flow |
| Three-zone | cell / signal / source | chemotaxis and sensed fields |
| Stacked process | top / middle / bottom | algorithms and derivations |
| Matrix network | grid objects / edge lanes | ECM and interaction maps |
| Plot plus margin | plot / callout region | quantitative panels with annotations |

## Review

- Similar objects and labels use equal visual sizes.
- Each zone contains one primary object group.
- No label forces a semantic shape to grow unexpectedly.
- No arrow hides another object or changes the apparent mechanism.
- Colors encode one stable role and have a non-color cue where important.
- Panel tags, titles, axes, and section boundaries align at final physical size,
  and no tag overlaps or visually merges with its title.
- Layout-specific values remain in the example; reusable visual tokens remain in
  `assets/styles/`.
