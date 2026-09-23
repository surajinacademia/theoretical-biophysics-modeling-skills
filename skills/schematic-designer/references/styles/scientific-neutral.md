# Scientific-neutral construction vocabulary

This historical profile name now provides compatibility names for the shared
[Minimalist design](minimalist.md). It does not select a second palette or font.
Use it only when adapting examples that already refer to `COLORS`, `sa/cell`,
`sa/process box`, and related components; start new figures from Minimalist.

The Python asset reads the owner's palette API and maps the old color names to
that palette. Pale fills are derived from the shared fill-opacity role; no
separate hue table is maintained. Color names are compatibility identifiers,
not scientific meanings. Declare the actual entity-to-color mapping in the figure.

The TikZ asset loads a generated `minimalist-profile.sty`. Declare both style
files to the renderer. It supplies the same CMU/LaTeX typography, role sizes,
white canvas, and native `Latex` heads while retaining useful cell, receptor,
fiber, process, scale-bar, and layout primitives. Geometric dimensions remain
construction defaults and must not replace a physical size or quantitative scale.

Small labels use dark ink when a light palette entry is not readable. Keep
labels opaque even when their associated fill or contextual geometry is pale.
A panel border or equation box should express a real grouping; ordinary panel
separation uses whitespace. Follow the [renderer workflow](../renderer-workflows.md)
and [vector export contract](../vector-export.md).
