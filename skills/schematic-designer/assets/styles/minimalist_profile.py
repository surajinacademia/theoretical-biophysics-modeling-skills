"""Shared schematic defaults with optional ``minimalist`` palette integration.

Call ``apply_style()`` before importing pyplot. Customize the role dictionaries
once, before applying the profile or generating TikZ, for figure-wide changes.
Geometry uses physical points (1/72 inch), written as ``bp`` in TikZ. Font
sizes use TeX ``pt`` in TikZ to match Matplotlib PGF font-size emission.
These are visual defaults, not scientific encodings or a layout prescription.
``python minimalist_profile.py --tikz`` prints a complete LuaLaTeX .sty file.
No package installation, font fallback, or artifact export is performed here.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
import warnings


FONT_PT = {"panel": 10, "title": 9, "body": 8, "equation": 8, "small": 7}
LINE_PT = {"context": 0.5, "structure": 0.75, "emphasis": 1.1}
MARKER_PT = {"point": 3, "emphasis": 4.5}  # Marker diameter, not scatter area.
ARROW_PT = {"length": 4, "width": 2.8}
OPACITY = {"context": 0.25, "fill": 0.12, "foreground": 1}
SPACE_PT = {"unit": 4, "label": 4, "group": 8, "panel": 12}
DASH_PT = {"dashed": (3, 2), "dotted": (0.7, 1.5)}  # On/off lengths.
INK = "#202020"
MUTED = "#666666"
PAPER = "#FFFFFF"


def tint(color, fraction):
    """Mix a role color with the common paper color, identically in both renderers."""
    if not isinstance(color, str) or re.fullmatch(r"#[0-9A-Fa-f]{6}", color) is None:
        raise ValueError("Tint colors must be six-digit #RRGGBB values")
    if not math.isfinite(fraction) or not 0 <= fraction <= 1:
        raise ValueError("Tint fractions must be between zero and one")
    return '#' + ''.join(f'{round(fraction*int(color[i:i+2],16)+(1-fraction)*int(PAPER[i:i+2],16)):02X}'
                         for i in (1,3,5))


def neutral_colors():
    """Compatibility neutral roles; do not maintain separate Python/TeX shades."""
    return {'faint': tint(MUTED, .6), 'grid': tint(MUTED, OPACITY['context']),
            'panel': tint(MUTED, OPACITY['fill'])}

_PREAMBLE = "\n".join([
    r"\usepackage{amsmath,amssymb}",
    r"\usepackage{tikz}",
    r"\usetikzlibrary{arrows.meta}",
    r"\usepackage[no-math]{fontspec}",
    r"\setmainfont{CMU Serif}",
    r"\setsansfont{CMU Sans Serif}",
])


def _prepare_backend():
    import matplotlib as mpl

    if "matplotlib.pyplot" in sys.modules and mpl.get_backend().lower() != "pgf":
        raise RuntimeError(
            "Apply minimalist_profile before importing pyplot or minimalist; "
            "an existing non-PGF backend will not be switched. Start a fresh "
            "process with the profile first."
        )
    mpl.use("pgf")
    mpl.rcParams["pgf.texsystem"] = "lualatex"
    return mpl


def palette():
    """Return a fresh, validated qualitative palette without reordering colors.

    Select PGF first because importing minimalist also imports pyplot. When the
    optional personal theme is absent, use Matplotlib's installed default cycle.
    This portable palette is explicitly different from the bundled specimens.
    """
    mpl = _prepare_backend()
    try:
        import minimalist
    except ModuleNotFoundError as error:
        if error.name == "minimalist":
            warnings.warn(
                "Optional minimalist theme is unavailable; using Matplotlib's "
                "default color cycle. Colors differ from bundled specimens.",
                RuntimeWarning,
                stacklevel=2,
            )
            colors = mpl.rcParamsDefault["axes.prop_cycle"].by_key()["color"]
        else:
            raise
    else:
        colors = minimalist.get_cmap("qualitative")
    if not isinstance(colors, (list, tuple)) or not colors:
        raise ValueError("minimalist qualitative palette must be a nonempty color list")
    if any(not isinstance(color, str) or re.fullmatch(r"#[0-9A-Fa-f]{6}", color) is None
           for color in colors):
        raise ValueError("minimalist palette colors must be six-digit #RRGGBB values")
    return list(colors)


def _validate_roles():
    for roles in (FONT_PT, LINE_PT, MARKER_PT, ARROW_PT, SPACE_PT, OPACITY):
        for value in roles.values():
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("Visual role values must be finite numbers")
            if not math.isfinite(value) or value < 0 or (roles is not OPACITY and value == 0):
                raise ValueError("Sizes must be positive and opacity must be nonnegative")
            if roles is OPACITY and value > 1:
                raise ValueError("Opacity must be between zero and one")
    for pattern in DASH_PT.values():
        if len(pattern) != 2 or any(
            isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value <= 0 for value in pattern
        ):
            raise ValueError("Dash patterns need two positive finite on/off lengths")


def apply_style():
    """Apply PGF/LuaLaTeX CMU typography and shared defaults before plotting.

    Does not call minimalist.use_style(), mutate Axes methods, set figure size,
    or export files. Apply role-specific opacity/spacing explicitly to artists;
    Matplotlib has no global rcParam for those roles. Scatter ``s`` is area in
    points squared, so square MARKER_PT values when using ``Axes.scatter``.
    """
    _validate_roles()
    mpl = _prepare_backend()
    colors = palette()
    mpl.rcParams.update({
        "text.usetex": True,
        "pgf.texsystem": "lualatex",
        "pgf.rcfonts": False,
        "pgf.preamble": _PREAMBLE,
        "font.family": "sans-serif",
        "font.sans-serif": ["CMU Sans Serif"],
        "font.serif": ["CMU Serif"],
        "font.size": FONT_PT["body"],
        "axes.titlesize": FONT_PT["title"],
        "axes.titleweight": "bold",
        "figure.titleweight": "bold",
        "font.weight": "normal",
        "axes.labelsize": FONT_PT["body"],
        "axes.labelweight": "normal",
        "xtick.labelsize": FONT_PT["small"],
        "ytick.labelsize": FONT_PT["small"],
        "legend.fontsize": FONT_PT["small"],
        "figure.titlesize": FONT_PT["panel"],
        "axes.prop_cycle": mpl.cycler(color=colors),
        "lines.linewidth": LINE_PT["structure"],
        "patch.linewidth": LINE_PT["structure"],
        "axes.linewidth": LINE_PT["structure"],
        "lines.markersize": MARKER_PT["point"],
        "lines.linestyle": "-",
        "lines.solid_capstyle": "butt",
        "lines.dash_capstyle": "butt",
        "lines.solid_joinstyle": "round",
        "lines.dash_joinstyle": "round",
        "lines.scale_dashes": False,
        "lines.dashed_pattern": DASH_PT["dashed"],
        "lines.dotted_pattern": DASH_PT["dotted"],
        "lines.markeredgewidth": LINE_PT["structure"],
        "xtick.major.width": LINE_PT["structure"],
        "ytick.major.width": LINE_PT["structure"],
        "xtick.minor.width": LINE_PT["context"],
        "ytick.minor.width": LINE_PT["context"],
        "text.color": INK,
        "axes.labelcolor": INK,
        "axes.titlecolor": INK,
        "axes.edgecolor": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "axes.grid": False,
        "savefig.facecolor": PAPER,
        "savefig.transparent": False,
    })


def tikz_style():
    """Return a complete .sty source with shared palette and role tokens.

    Colors: msColor1… plus msInk, msMuted, msPaper. Dimension macros:
    \\msFontPanel, \\msLineStructure, \\msMarkerPoint, \\msSpaceGroup, etc.
    Opacity macros (e.g. \\msOpacityFill) are unitless. Named styles include
    ``ms base``, ``ms body``, ``ms structure``, ``ms fill``, ``ms point`` and
    ``ms arrow``. Context affects strokes; fill affects fills; text stays opaque.
    The caller saves this as a declared support file for the TikZ renderer.
    """
    _validate_roles()
    colors = palette()
    lines = [
        r"\NeedsTeXFormat{LaTeX2e}",
        r"\ProvidesPackage{minimalist-profile}[Shared schematic visual defaults]",
        r"\RequirePackage{iftex}",
        r"\RequireLuaTeX",
        r"\RequirePackage{amsmath,amssymb}",
        r"\RequirePackage[no-math]{fontspec}",
        r"\setmainfont{CMU Serif}",
        r"\setsansfont{CMU Sans Serif}",
        r"\renewcommand{\familydefault}{\sfdefault}",
        r"\RequirePackage{tikz}",
        r"\usetikzlibrary{arrows.meta,positioning,patterns,backgrounds}",
    ]
    for name, color in [("msInk", INK), ("msMuted", MUTED), ("msPaper", PAPER),
                        *[("ms" + name.title(), color) for name, color in neutral_colors().items()]] + [
        (f"msColor{index}", color) for index, color in enumerate(colors, 1)
    ]:
        lines.append(r"\definecolor{" + name + "}{HTML}{" + color[1:] + "}")
    for prefix, roles, unit in [
        ("Font", FONT_PT, "pt"), ("Line", LINE_PT, "bp"),
        ("Marker", MARKER_PT, "bp"), ("Arrow", ARROW_PT, "bp"), ("Opacity", OPACITY, ""),
        ("Space", SPACE_PT, "bp"),
    ]:
        for role, value in roles.items():
            lines.append(r"\newcommand{\ms" + prefix + role.title() + "}{" + f"{value:g}{unit}" + "}")
    for role, pattern in DASH_PT.items():
        for suffix, value in zip(("On", "Off"), pattern):
            lines.append(r"\newcommand{\msDash" + role.title() + suffix + "}{" + f"{value:g}bp" + "}")
    lines.append(r"\pgfmathsetmacro{\msFillPercent}{100*\msOpacityFill}")
    lines.append(r"\tikzset{")
    for role, value in FONT_PT.items():
        lines.append(
            "  ms " + role + r"/.style={font=\sffamily\fontsize{\msFont" + role.title()
            + "}{" + f"{value * 1.2:g}pt" + r"}\selectfont"
            + (r"\bfseries}," if role in {"panel", "title"} else r"\mdseries},")
        )
    lines.extend([
        r"  >={Latex[length=\msArrowLength,width=\msArrowWidth]},",
        r"  ms base/.style={ms body,text=msInk,color=msInk,line width=\msLineStructure,",
        r"    line cap=butt,line join=round,",
        r"    show background rectangle,inner frame sep=0bp,",
        r"    background rectangle/.style={fill=msPaper,fill opacity=1,draw=none},",
        r"    execute at begin picture={\everymath=\expandafter{\the\everymath\displaystyle}},",
        r"    draw opacity=\msOpacityForeground,fill opacity=\msOpacityForeground,",
        r"    text opacity=1,inner sep=\msSpaceLabel,node distance=\msSpaceGroup},",
        r"  ms context/.style={line width=\msLineContext,draw opacity=\msOpacityContext},",
        r"  ms structure/.style={line width=\msLineStructure,draw opacity=\msOpacityForeground},",
        r"  ms emphasis/.style={line width=\msLineEmphasis,draw opacity=\msOpacityForeground},",
        r"  ms fill/.style={fill opacity=\msOpacityFill,text opacity=1},",
        r"  ms point/.style={circle,inner sep=0bp,outer sep=0bp,minimum size=\msMarkerPoint,",
        r"    draw=none,fill=msInk,fill opacity=\msOpacityForeground},",
        r"  ms emphasis point/.style={ms point,minimum size=\msMarkerEmphasis},",
        r"  ms arrow/.style={ms structure,->},",
        r"  ms solid/.style={solid},",
        r"  ms dashed/.style={dash pattern=on \msDashDashedOn off \msDashDashedOff},",
        r"  ms dotted/.style={dash pattern=on \msDashDottedOn off \msDashDottedOff},",
        r"  ms pattern/.style={pattern=north east lines,pattern color=msMuted}",
        "}",
        r"\endinput",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tikz", action="store_true", required=True,
                        help="print the complete TikZ .sty source to stdout")
    parser.parse_args()
    print(tikz_style(), end="")


if __name__ == "__main__":
    main()
