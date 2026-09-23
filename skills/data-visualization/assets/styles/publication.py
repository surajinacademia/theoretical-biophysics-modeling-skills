"""Scoped optional minimalist style, with a disclosed native Matplotlib fallback.

Read the package's style resource and palette API, and scope its hollow-marker
errorbar gaps to this context. No source, fonts, or palette are copied here.
Render and save inside the context so the draw-time gap API remains active.
"""

from contextlib import ExitStack, contextmanager
from importlib.resources import as_file, files
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.font_manager import FontProperties, findfont
import warnings

try:
    import minimalist
except ModuleNotFoundError as exc:
    if exc.name != "minimalist":
        raise
    minimalist = None


# Shared roles used by the templates and gallery. Sizes are physical points;
# layout pads are multiples of the base font size, as required by tight_layout.
FONT_PT = {"body": 8, "note": 8, "panel": 9}
LINE_PT = {"context": 0.65, "outline": 0.8}
MARK_PT = {"point": 5, "mean": 11, "cap": 3}
OPACITY = {"context": 0.5}
LAYOUT = {"pad": 0.8, "panel_gap": 2.0, "note_y": 0.02, "note_top": 0.12}
MARKERS = ("o", "s", "^", "D", "v", "P")
LINESTYLES = ("-", "--", "-.", ":")
DASH_PT = {"dashed": (3, 2), "dashdot": (3, 2, 0.7, 2), "dotted": (0.7, 1.5)}


def get_cmap(role):
    """Use the optional owner palette, or a named Matplotlib palette."""
    if minimalist is not None:
        return minimalist.get_cmap(role)
    names = {"sequential": "inferno", "diverging": "coolwarm"}
    return plt.get_cmap(names[role])


@contextmanager
def paper_style():
    """Apply package defaults plus PDF geometry, then restore the caller's style."""
    overlay = Path(__file__).with_name("paper.mplstyle")
    with ExitStack() as stack:
        styles = ["default"]
        if minimalist is not None:
            resource = files("minimalist").joinpath("styles", "white.mplstyle")
            styles.append(stack.enter_context(as_file(resource)))
        else:
            warnings.warn("minimalist unavailable: using Matplotlib DejaVu Sans, tab10, "
                          "and through-going error bars (marker_gap is ignored).", stacklevel=2)
        styles.append(overlay)
        with plt.style.context(styles):
            if minimalist is not None:
                plt.rcParams["axes.prop_cycle"] = plt.cycler(color=minimalist.get_cmap("qualitative"))
            plt.rcParams.update({
                "font.size": FONT_PT["body"], "axes.labelsize": FONT_PT["body"],
                "xtick.labelsize": FONT_PT["body"], "ytick.labelsize": FONT_PT["body"],
                "legend.fontsize": FONT_PT["body"], "axes.titlesize": FONT_PT["panel"],
                "axes.titleweight": "bold", "lines.markersize": MARK_PT["point"],
                "lines.markeredgewidth": LINE_PT["outline"],
                "lines.scale_dashes": False, "lines.dashed_pattern": DASH_PT["dashed"],
                "lines.dashdot_pattern": DASH_PT["dashdot"], "lines.dotted_pattern": DASH_PT["dotted"],
                "legend.handlelength": 2.0,
            })
            findfont(FontProperties(family=plt.rcParams["font.family"]), fallback_to_default=False)
            original_errorbar, original_draw = Axes.errorbar, Axes.draw
            try:
                if minimalist is not None:
                    minimalist.enable_errorbar_marker_gap(default=True)
                else:
                    # Native Matplotlib has no marker_gap keyword. Preserve the
                    # open marker and uncertainty extent rather than mask data.
                    def errorbar(ax, *args, marker_gap=True, **kwargs):
                        return original_errorbar(ax, *args, **kwargs)
                    Axes.errorbar = errorbar
                yield
            finally:
                Axes.errorbar, Axes.draw = original_errorbar, original_draw
