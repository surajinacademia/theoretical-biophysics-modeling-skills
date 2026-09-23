# Required Typography

Use LaTeX for every equation in Matplotlib, TikZ, and hybrid figures. Use
Computer Modern Unicode (CMU) for text: CMU Sans Serif for labels and prose,
and CMU Serif for serif text. Keep LaTeX's Computer Modern mathematical fonts
for mathematical symbols; CMU text fonts are not a replacement for a complete
math font. Do not substitute DejaVu, Arial, or Latin Modern text fonts.

This requirement applies to every profile and to adaptations of bundled
examples. The default minimalist helper and its compatibility assets apply it
directly. Replace font fallbacks and Mathtext settings when adapting an imported
construction reference.
If LaTeX or the required CMU faces are missing, report the missing dependency
and stop final rendering rather than silently substitute typography.

## Matplotlib

For the default profile, import `apply_style` from
[minimalist_profile.py](../assets/styles/minimalist_profile.py) and call it before
importing `matplotlib.pyplot` or `minimalist`. It selects PGF before loading the
palette package, then applies CMU text and LuaLaTeX math settings. Do not call
`minimalist.use_style()` afterward; it is not this skill's typography setup.

Use the PGF backend with LuaLaTeX so real LaTeX renders equations and fontspec
selects the CMU text faces. When a project explicitly supplies its own profile,
select PGF first, apply it, then apply this configuration before creating a figure:

```python
import matplotlib as mpl
mpl.use("pgf")  # Before importing pyplot.

# Apply the chosen profile's colors, sizes, and line styles here.
mpl.rcParams.update({
    "text.usetex": True,
    "pgf.texsystem": "lualatex",
    "pgf.rcfonts": False,
    "font.family": "sans-serif",
    "font.sans-serif": ["CMU Sans Serif"],
    "font.serif": ["CMU Serif"],
    "pgf.preamble": "\n".join([
        r"\usepackage{amsmath,amssymb}",
        r"\usepackage[no-math]{fontspec}",
        r"\setmainfont{CMU Serif}",
        r"\setsansfont{CMU Sans Serif}",
    ]),
})
import matplotlib.pyplot as plt
```

Write equations as raw LaTeX strings, for example
`ax.set_ylabel(r"$\frac{\mathrm{d}x}{\mathrm{d}t}=-k x$")`.
Mathtext alone, including `mathtext.fontset="cm"`, does not satisfy the LaTeX
requirement. Escape ordinary text before passing it to TeX; preserve the skill's
allowlisted-equation and trusted-source boundaries.

Render a staged PDF using PGF, then convert that PDF to an outlined SVG; do not
switch back to the native SVG backend for the final figure. PGF does not export
SVG directly. Follow references/vector-export.md for validation and publication.

Implementation reference: [Matplotlib PGF documentation](https://matplotlib.org/stable/users/explain/text/pgf.html).

## TikZ and hybrid

Compile with LuaLaTeX and load `fontspec` with the `no-math` option. Select
`\setmainfont{CMU Serif}` and `\setsansfont{CMU Sans Serif}` explicitly, with
`\renewcommand{\familydefault}{\sfdefault}` for prose and labels. Use LaTeX
math mode (`$...$`, `\(...\)`, or a suitable math environment) for all equations.
Do not select a pdfLaTeX or fallback-font branch from an older style asset.
The default helper's generated TikZ support style supplies this CMU/LaTeX setup;
use it through [renderer-workflows.md](renderer-workflows.md).
Use the same CMU faces and LaTeX math setup in Matplotlib panels and the TikZ
compositor. Existing examples are construction references, not typography
exceptions.

## Hierarchy and label color

Use the selected profile's panel, title, body, equation, and small-text roles
consistently at the intended publication size. Use weight and spacing to separate
structural labels from scientific labels; equations retain their exact notation.
Place labels near the entity or relation they identify. Match an entity's color
in its label when it remains readable against the background; otherwise use dark
text with a colored key. Keep text opaque and use fill opacity for pale context.
When a label does not fit, adjust the layout before reducing its type size.

## Final check

Inspect a representative equation containing a fraction, Greek symbol,
subscript, and superscript. Check the PDF font inventory for the selected CMU
text faces and Computer Modern math, and check the outlined SVG visually.
A successful render with substituted fonts is not a completed figure.
In a hybrid composition, also compare imported panel labels with native TikZ
labels at the final size; scaling a panel scales its typography and strokes.
