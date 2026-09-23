"""Minimalist worked example of adaptive field response.

The scientific content is an original illustrative model, not data or content from
arXiv:2406.07856. A response coefficient is learned during imposed motion,

    tau_g * dg/dt = g_target - g,

and then drives motion up a computed anisotropic scalar field,

    dr_i/dt = chi * g * grad C(r_i).

The script writes PDF and outlined-text SVG outputs non-interactively.
"""

import argparse
from pathlib import Path
import sys

import matplotlib

matplotlib.use("pgf")

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle, Ellipse
import numpy as np

SKILL_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
sys.path.insert(0, str(SKILL_ROOT / "assets" / "styles" / "matplotlib"))
sys.path.insert(0, str(SKILL_ROOT / "assets" / "styles"))

from learning_dynamics_2406 import (  # noqa: E402
    COLORS,
    FONT_SIZES,
    apply_style,
)
from native_tikz import arrow as tikz_arrow
from minimalist_profile import FONT_PT, LINE_PT, MARKER_PT, OPACITY
from vector_output import save_vector_pair  # noqa: E402


# Scientific parameters -------------------------------------------------------
SOURCE_POSITION = np.array([1.75, 0.25])
FIELD_LENGTH_X = 2.20
FIELD_LENGTH_Y = 1.05
LEARNING_TIME = 1.35
EVEN_TARGET = 0.82
ODD_TARGET = 0.28
MOBILITY = 4.8
TRAIN_DURATION = 6.0
RETRIEVAL_DURATION = 3.5
TIME_STEP = 0.025
INITIAL_POSITION = np.array([-2.25, -1.15])


# Profile aliases keep the drawing code semantic and compact. -----------------
STYLE_CANVAS = COLORS["canvas"]
STYLE_INK = COLORS["ink"]
STYLE_MUTED = COLORS["muted"]
STYLE_TRAIN = COLORS["training"]
STYLE_RETRIEVE = COLORS["retrieval"]
STYLE_PURPLE = COLORS["purple"]
STYLE_PURPLE_EDGE = COLORS["purple_edge"]
STYLE_ORANGE = COLORS["orange"]
STYLE_ORANGE_EDGE = COLORS["orange_edge"]
STYLE_BLUE = COLORS["blue"]
STYLE_RED = COLORS["red"]
STYLE_FIELD_CORE = COLORS["field_core"]
STYLE_FIELD_PALE = COLORS["field_pale"]

PANEL_LABEL_SIZE = FONT_SIZES["panel_label"]
SECTION_LABEL_SIZE = FONT_SIZES["section_label"]
AXIS_LABEL_SIZE = FONT_SIZES["axis_label"]
TICK_LABEL_SIZE = FONT_SIZES["tick_label"]

apply_style()


def parse_args():
    """Parse renderer options without making the installed skill directory writable."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("outputs"),
        help="Approved output directory; relative paths resolve from the working directory.",
    )
    return parser.parse_args()


def scalar_field(x, y):
    """An anisotropic Gaussian field centered on ``SOURCE_POSITION``."""
    dx = x - SOURCE_POSITION[0]
    dy = y - SOURCE_POSITION[1]
    exponent = -0.5 * ((dx / FIELD_LENGTH_X) ** 2 + (dy / FIELD_LENGTH_Y) ** 2)
    return np.exp(exponent)


def scalar_gradient(position):
    """Exact gradient of :func:`scalar_field` at one 2D position."""
    dx = position[0] - SOURCE_POSITION[0]
    dy = position[1] - SOURCE_POSITION[1]
    concentration = scalar_field(position[0], position[1])
    return concentration * np.array(
        [-dx / FIELD_LENGTH_X**2, -dy / FIELD_LENGTH_Y**2]
    )


def learn_response(target, times):
    """Integrate ``tau_g * dg/dt = target - g`` by forward Euler."""
    values = np.zeros_like(times)
    for index in range(1, len(times)):
        dt = times[index] - times[index - 1]
        values[index] = values[index - 1] + dt * (
            target - values[index - 1]
        ) / LEARNING_TIME
    return values


def retrieve_trajectory(total_response):
    """Integrate ``dr/dt = mobility * response * grad C``."""
    times = np.arange(0.0, RETRIEVAL_DURATION + TIME_STEP, TIME_STEP)
    positions = np.empty((len(times), 2), dtype=float)
    positions[0] = INITIAL_POSITION
    for index in range(1, len(times)):
        velocity = MOBILITY * total_response * scalar_gradient(positions[index - 1])
        positions[index] = positions[index - 1] + TIME_STEP * velocity
    return times, positions


def add_section_heading(fig, bounds, label, color, *, fontsize):
    x, y, width, height = bounds
    # A restrained color key groups the panels without a decorative ribbon.
    fig.add_artist(matplotlib.lines.Line2D(
        [x, x + min(width, 0.035)], [y + height / 2, y + height / 2],
        transform=fig.transFigure, color=color,
        linewidth=LINE_PT["emphasis"], clip_on=False,
    ))
    fig.text(
        x + 0.045,
        y + height / 2,
        label,
        ha="left",
        va="center",
        zorder=11,
        fontsize=fontsize,
        fontfamily="sans-serif",
        fontweight="bold",
        color=STYLE_INK,
    )


def panel_tag(ax, letter):
    position = ax.get_position(original=True)
    return ax.figure.text(
        position.x0 - 0.02,
        position.y1 + 0.015,
        letter.upper(),
        ha="left",
        va="bottom",
        clip_on=False,
        fontsize=PANEL_LABEL_SIZE,
        fontfamily="sans-serif",
        fontweight="bold",
        color=STYLE_INK,
    )


def minimal_axes(ax, *, snapshot=False):
    ax.grid(False)
    ax.tick_params(
        direction="out",
        width=LINE_PT["structure"],
        length=3.0,
        labelsize=TICK_LABEL_SIZE,
        colors=STYLE_INK,
    )
    for name, spine in ax.spines.items():
        spine.set_visible(snapshot or name in {"left", "bottom"})
        spine.set_linewidth(LINE_PT["structure"])
        spine.set_color(STYLE_INK)


def particle(ax, position, face, edge, label, *, radius=0.23,
             alpha=OPACITY["foreground"], zorder=6):
    glyph = Circle(
        position,
        radius,
        facecolor=matplotlib.colors.to_rgba(face, OPACITY["fill"] * alpha),
        edgecolor=matplotlib.colors.to_rgba(edge, alpha),
        linewidth=LINE_PT["structure"],
        zorder=zorder,
    )
    ax.add_patch(glyph)
    ax.text(
        position[0],
        position[1],
        label,
        ha="center",
        va="center",
        fontsize=FONT_PT["body"],
        color=STYLE_INK,
        alpha=OPACITY["foreground"],
        zorder=zorder + 1,
    )
    return glyph


def process_arrow(ax, start, end, color, *, lw=LINE_PT["emphasis"], rad=0.0, zorder=7):
    return tikz_arrow(ax, start, end, color=color, linewidth=lw, rad=rad,
                      zorder=zorder)



def illustrative_halo(ax, center, color):
    """A schematic field cue; graded opacity communicates illustrative extent.

    Quantitative fields use ``scalar_field`` below.
    """
    for width, height, alpha in zip(
        np.linspace(3.6, 0.7, 8),
        np.linspace(1.8, 0.35, 8),
        np.linspace(0.025, 0.18, 8),
    ):
        ax.add_patch(
            Ellipse(
                center,
                width,
                height,
                facecolor=color,
                edgecolor="none",
                alpha=alpha,
                zorder=1,
            )
        )


def draw_training_schematic(ax):
    ax.set_xlim(-3.0, 3.0)
    ax.set_ylim(-1.65, 1.65)
    ax.set_aspect("equal")
    ax.axis("off")

    position_i = np.array([-1.25, 0.0])
    position_j = np.array([1.25, 0.0])
    illustrative_halo(ax, position_j, STYLE_FIELD_CORE)
    particle(ax, position_i, STYLE_PURPLE, STYLE_PURPLE_EDGE, r"$i$")
    particle(ax, position_j, STYLE_ORANGE, STYLE_ORANGE_EDGE, r"$j$")

    process_arrow(ax, position_i + [0.0, 0.48], position_i + [1.0, 0.48], STYLE_TRAIN)
    process_arrow(ax, position_j + [0.0, 0.48], position_j + [1.0, 0.48], STYLE_TRAIN)
    ax.text(
        0.0,
        1.05,
        "imposed motion",
        ha="center",
        va="center",
        fontsize=FONT_PT["title"],
        fontfamily="sans-serif",
        fontweight="bold",
        color=STYLE_INK,
    )

    ax.plot(
        [position_i[0], position_j[0]],
        [-0.55, -0.55],
        color=STYLE_INK,
        lw=LINE_PT["structure"],
    )
    ax.plot([position_i[0], position_i[0]], [-0.62, -0.48], color=STYLE_INK, lw=LINE_PT["structure"])
    ax.plot([position_j[0], position_j[0]], [-0.62, -0.48], color=STYLE_INK, lw=LINE_PT["structure"])
    ax.text(0.0, -0.78, r"$a$", ha="center", va="center", fontsize=FONT_PT["equation"])
    ax.text(
        0.0,
        -1.28,
        r"$\tau_g\dot g=g_{\rm target}-g$",
        ha="center",
        va="center",
        fontsize=FONT_PT["equation"],
        color=STYLE_INK,
    )

    panel_tag(ax, "a")


def draw_learning_plot(ax, times, even_response, odd_response):
    ax.plot(times, even_response, color=STYLE_BLUE, lw=LINE_PT["emphasis"])
    ax.plot(times, odd_response, color=STYLE_RED, lw=LINE_PT["emphasis"], ls="--")
    ax.axhline(0.0, color=STYLE_INK, lw=LINE_PT["structure"])
    ax.set_xlim(0.0, TRAIN_DURATION)
    ax.set_ylim(-0.03, 0.92)
    ax.set_xticks([0, 3, 6])
    ax.set_yticks([0.0, 0.4, 0.8])
    ax.set_xlabel(r"$t$", fontsize=AXIS_LABEL_SIZE)
    ax.set_ylabel(r"learned response $g$", fontsize=AXIS_LABEL_SIZE)
    minimal_axes(ax)

    ax.text(
        TRAIN_DURATION * 0.96,
        even_response[-1] + 0.045,
        r"$g^{+}$",
        ha="right",
        va="bottom",
        fontsize=FONT_PT["equation"],
        color=STYLE_BLUE,
    )
    ax.text(
        TRAIN_DURATION * 0.96,
        odd_response[-1] - 0.045,
        r"$g^{-}$",
        ha="right",
        va="top",
        fontsize=FONT_PT["equation"],
        color=STYLE_RED,
    )
    ax.text(
        0.04,
        0.95,
        "learn interaction",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=FONT_PT["title"],
        fontfamily="sans-serif",
        fontweight="bold",
        color=STYLE_INK,
    )
    panel_tag(ax, "b")


def draw_retrieval(ax, positions, retrieval_times):
    x = np.linspace(-3.0, 3.0, 260)
    y = np.linspace(-2.0, 2.0, 190)
    X, Y = np.meshgrid(x, y)
    C = scalar_field(X, Y)
    field_cmap = LinearSegmentedColormap.from_list(
        "profile_field", [STYLE_CANVAS, STYLE_FIELD_PALE, STYLE_FIELD_CORE]
    )
    image = ax.pcolormesh(
        X,
        Y,
        C,
        cmap=field_cmap,
        shading="gouraud",
        rasterized=True,
        zorder=0,
    )
    image.set_clim(0.0, 1.0)

    ax.plot(
        positions[:, 0],
        positions[:, 1],
        color=STYLE_RETRIEVE,
        lw=LINE_PT["emphasis"],
        alpha=OPACITY["foreground"],
        zorder=4,
    )
    sample_indices = np.linspace(0, len(positions) - 1, 7, dtype=int)
    ax.scatter(
        positions[sample_indices, 0],
        positions[sample_indices, 1],
        s=MARKER_PT["point"] ** 2,
        facecolor=STYLE_RETRIEVE,
        edgecolor="none",
        alpha=np.linspace(OPACITY["context"], OPACITY["foreground"], len(sample_indices)),
        zorder=5,
    )
    particle(
        ax,
        positions[0],
        STYLE_PURPLE,
        STYLE_PURPLE_EDGE,
        r"$i$",
        alpha=OPACITY["context"],
        radius=0.20,
    )
    particle(
        ax,
        positions[-1],
        STYLE_PURPLE,
        STYLE_PURPLE_EDGE,
        r"$i$",
        radius=0.20,
    )
    particle(
        ax,
        SOURCE_POSITION,
        STYLE_ORANGE,
        STYLE_ORANGE_EDGE,
        r"$j$",
        radius=0.23,
    )

    arrow_start = positions[-42]
    arrow_end = positions[-1]
    process_arrow(ax, arrow_start, arrow_end, STYLE_RETRIEVE, lw=LINE_PT["emphasis"])

    ax.text(
        positions[0, 0] + 0.12,
        positions[0, 1] - 0.22,
        r"$t=0$",
        ha="left",
        va="top",
        fontsize=FONT_PT["body"],
        color=STYLE_MUTED,
    )
    ax.text(
        0.96,
        0.95,
        rf"$t={retrieval_times[-1]:.1f}$",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=FONT_PT["body"],
        color=STYLE_INK,
    )
    ax.text(
        0.05,
        0.95,
        "adaptive drift",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=FONT_PT["title"],
        fontfamily="sans-serif",
        fontweight="bold",
        color=STYLE_INK,
    )
    ax.text(
        0.96,
        0.05,
        "illustrative computation",
        transform=ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=FONT_PT["small"],
        color=STYLE_MUTED,
    )

    ax.set_xlim(-3.0, 3.0)
    ax.set_ylim(-2.0, 2.0)
    ax.set_aspect("equal")
    ax.set_xticks([-2, 0, 2])
    ax.set_yticks([-1, 0, 1])
    ax.set_xlabel(r"$x$", fontsize=AXIS_LABEL_SIZE)
    ax.set_ylabel(r"$y$", fontsize=AXIS_LABEL_SIZE)
    minimal_axes(ax, snapshot=True)
    panel_tag(ax, "c")


def main():
    args = parse_args()
    training_times = np.arange(0.0, TRAIN_DURATION + TIME_STEP, TIME_STEP)
    even_response = learn_response(EVEN_TARGET, training_times)
    odd_response = learn_response(ODD_TARGET, training_times)
    total_response = even_response[-1] + odd_response[-1]
    retrieval_times, positions = retrieve_trajectory(total_response)

    fig = plt.figure(figsize=(7.0, 3.35), facecolor=STYLE_CANVAS)
    grid = GridSpec(
        1,
        3,
        figure=fig,
        width_ratios=[1.05, 0.95, 1.18],
        left=0.055,
        right=0.985,
        bottom=0.15,
        top=0.72,
        wspace=0.42,
    )
    ax_a = fig.add_subplot(grid[0, 0])
    ax_b = fig.add_subplot(grid[0, 1])
    ax_c = fig.add_subplot(grid[0, 2])

    add_section_heading(
        fig,
        (0.02, 0.90, 0.96, 0.075),
        "Adaptive field response",
        STYLE_INK,
        fontsize=FONT_PT["title"],
    )
    add_section_heading(
        fig,
        (0.02, 0.79, 0.615, 0.065),
        "Training",
        STYLE_TRAIN,
        fontsize=SECTION_LABEL_SIZE,
    )
    add_section_heading(
        fig,
        (0.655, 0.79, 0.325, 0.065),
        "Retrieval",
        STYLE_RETRIEVE,
        fontsize=SECTION_LABEL_SIZE,
    )

    draw_training_schematic(ax_a)
    draw_learning_plot(ax_b, training_times, even_response, odd_response)
    draw_retrieval(ax_c, positions, retrieval_times)

    pdf_path, svg_path = save_vector_pair(
        fig,
        args.output_dir,
        "learning-dynamics-2406",
        common_options={"dpi": 300, "bbox_inches": "tight"},
    )
    plt.close(fig)

    print(pdf_path)
    print(svg_path)


if __name__ == "__main__":
    main()
