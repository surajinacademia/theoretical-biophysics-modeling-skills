"""Publication-style schematic of model classes for collective cell dynamics.

The figure is conceptual and deliberately separates two ideas:

1. model class: how biological state is represented and evolved; and
2. resolution: how much spatial/internal detail is resolved.

All geometry is illustrative and not simulation output.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import Iterable

import matplotlib

matplotlib.use("pgf")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import (
    Circle,
    Polygon,
    Rectangle,
)

SKILL_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
sys.path.insert(0, str(SKILL_ROOT / "assets" / "styles" / "matplotlib"))
sys.path.insert(0, str(SKILL_ROOT / "assets" / "styles"))

from scientific_neutral import COLORS, apply_style  # noqa: E402
from native_tikz import arrow as tikz_arrow
from minimalist_profile import FONT_PT, LINE_PT, MARKER_PT, OPACITY, DASH_PT
from vector_output import save_vector_pair  # noqa: E402


# ---------------------------------------------------------------------------
# Output and reproducibility
# ---------------------------------------------------------------------------

OUTPUT_BASENAME = "collective-cell-model-classes"
PAPER_SIZE_IN = (11.2, 6.4)

# ---------------------------------------------------------------------------
# Minimalist visual grammar
# ---------------------------------------------------------------------------

INK = COLORS["ink"]
MUTED = COLORS["muted"]
FAINT = COLORS["faint"]
GRID = COLORS["grid"]
WHITE = COLORS["canvas"]

PURPLE = COLORS["purple"]
PURPLE_LIGHT = COLORS["purple_light"]
PURPLE_TEXT = COLORS["purple_text"]
BLUE = COLORS["blue"]
BLUE_LIGHT = COLORS["blue_light"]
GREEN = COLORS["green"]
GREEN_LIGHT = COLORS["green_light"]
GREEN_TEXT = COLORS["green_text"]
ORANGE = COLORS["orange"]
ORANGE_LIGHT = COLORS["orange_light"]
ORANGE_TEXT = COLORS["orange_text"]
RED = COLORS["red"]
RED_LIGHT = COLORS["red_light"]
RED_TEXT = COLORS["red_text"]
TEAL = COLORS["teal"]
TEAL_TEXT = COLORS["teal_text"]
ECM = COLORS["ecm"]

PANEL_ACCENTS = (PURPLE, BLUE, GREEN, ORANGE, RED)
FIELD_CMAP = LinearSegmentedColormap.from_list(
    "scientific_field",
    (WHITE, BLUE_LIGHT, BLUE),
)

apply_style()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    return parser.parse_args()


def blend_with_white(color: str, amount: float = 1 - OPACITY["fill"]) -> tuple[float, ...]:
    """Return a pale tint while keeping one semantic accent per panel."""
    rgb = np.asarray(matplotlib.colors.to_rgb(color))
    return tuple((1.0 - amount) * rgb + amount * np.ones(3))


def configure_panel(ax: plt.Axes, letter: str, title: str, accent: str) -> None:
    """Group one model family with whitespace and a compact color key."""
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.76)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    # Whitespace separates model families; a short key preserves their colors.
    ax.plot(
        [0.04, 0.04],
        [1.515, 1.665],
        color=accent,
        lw=LINE_PT["emphasis"],
        solid_capstyle="butt",
        zorder=2,
    )
    ax.text(
        0.075,
        1.595,
        letter.upper(),
        ha="left",
        va="center",
        fontsize=FONT_PT["panel"],
        fontweight="bold",
        color=INK,
    )
    ax.text(
        0.195,
        1.595,
        title,
        ha="left",
        va="center",
        fontsize=FONT_PT["title"],
        fontweight="bold",
        linespacing=1.08,
        color=INK,
    )


def draw_arrow(
    ax: plt.Axes,
    start: tuple[float, float],
    end: tuple[float, float],
    *,
    color: str = INK,
    lw: float = LINE_PT["structure"],
    linestyle: str = "-",
    zorder: float = 6,
):
    """Draw one vector arrow with consistent publication-scale geometry."""
    return tikz_arrow(ax, start, end, color=color, linewidth=lw,
                      linestyle=linestyle, zorder=zorder)


def draw_cell(
    ax: plt.Axes,
    xy: tuple[float, float],
    *,
    radius: float = 0.075,
    face: str = BLUE_LIGHT,
    edge: str = BLUE,
    nucleus: bool = True,
    state_color: str | None = None,
    zorder: float = 8,
) -> Circle:
    """Draw a finite-size cell agent with an optional internal state marker."""
    cell = Circle(
        xy,
        radius,
        facecolor=face,
        edgecolor=edge,
        linewidth=LINE_PT["emphasis"],
        zorder=zorder,
    )
    ax.add_patch(cell)
    if nucleus:
        ax.add_patch(
            Circle(
                xy,
                0.34 * radius,
                facecolor=state_color or edge,
                edgecolor="none",
                alpha=OPACITY["foreground"],
                zorder=zorder + 1,
            )
        )
    return cell


def label_box(
    ax: plt.Axes,
    xy: tuple[float, float],
    text: str,
    *,
    color: str = INK,
    fontsize: float = FONT_PT["body"],
    ha: str = "center",
    va: str = "center",
    alpha: float = OPACITY["foreground"],
    zorder: float = 20,
) -> None:
    """Place a compact direct label over visually dense content."""
    ax.text(
        *xy,
        text,
        ha=ha,
        va=va,
        fontsize=fontsize,
        color=color,
        zorder=zorder,
        bbox={
            "boxstyle": "round,pad=0.18",
            "facecolor": WHITE,
            "edgecolor": "none",
            "alpha": alpha,
        },
    )


# ---------------------------------------------------------------------------
# Panel (a): Brownian / active particles
# ---------------------------------------------------------------------------


def draw_noise_wiggle(
    ax: plt.Axes,
    center: tuple[float, float],
    *,
    angle: float,
    color: str = PURPLE,
) -> None:
    """Draw a deterministic angular-noise cue."""
    t = np.linspace(-0.07, 0.07, 60)
    normal = 0.012 * np.sin(8.0 * np.pi * (t + 0.07) / 0.14)
    ca, sa = np.cos(angle), np.sin(angle)
    x = center[0] + ca * t - sa * normal
    y = center[1] + sa * t + ca * normal
    ax.plot(x, y, color=color, lw=LINE_PT["structure"], zorder=5)


def draw_pair_force(
    ax: plt.Axes,
    a: np.ndarray,
    b: np.ndarray,
    *,
    attractive: bool,
    label: str,
) -> None:
    """Show pair attraction (inward) or repulsion (outward) redundantly."""
    delta = b - a
    unit = delta / np.linalg.norm(delta)
    midpoint = 0.5 * (a + b)
    color = GREEN if attractive else RED
    text_color = GREEN_TEXT if attractive else RED_TEXT

    # Attraction points toward the midpoint; repulsion reverses the same segments.
    segments = (
        (a + 0.09 * unit, midpoint - 0.025 * unit),
        (b - 0.09 * unit, midpoint + 0.025 * unit),
    )
    for start, end in segments:
        if not attractive:
            start, end = end, start
        draw_arrow(
            ax, tuple(start), tuple(end), color=color, lw=LINE_PT["emphasis"],
        )
    normal = np.array([-unit[1], unit[0]])
    offset = 0.075 * normal
    ax.text(
        *(midpoint + offset),
        label,
        ha="center",
        va="center",
        fontsize=FONT_PT["body"],
        fontweight="bold",
        color=text_color,
        zorder=15,
    )


def plot_particle_models(ax: plt.Axes) -> None:
    configure_panel(
        ax,
        "a",
        "Brownian / active\nparticle models",
        PANEL_ACCENTS[0],
    )
    positions = [
        (0.23, 1.19),
        (0.70, 1.18),
        (0.23, 0.72),
        (0.70, 0.72),
        (0.47, 0.27),
    ]
    for position in positions:
        draw_cell(
            ax,
            position,
            radius=0.070,
            face=PURPLE_LIGHT,
            edge=PURPLE,
            nucleus=False,
        )

    motion_vectors = [
        ((0.25, 1.24), (0.39, 1.39)),
        ((0.75, 1.15), (0.90, 1.06)),
        ((0.19, 0.67), (0.09, 0.51)),
        ((0.50, 0.31), (0.65, 0.42)),
    ]
    for start, end in motion_vectors:
        draw_arrow(ax, start, end, color=INK, lw=LINE_PT["emphasis"])

    draw_noise_wiggle(ax, (0.10, 1.17), angle=0.2)
    draw_noise_wiggle(ax, (0.87, 1.27), angle=-1.0)
    draw_noise_wiggle(ax, (0.31, 0.30), angle=-0.5)
    ax.text(0.08, 1.30, "noise", fontsize=FONT_PT["small"], color=PURPLE_TEXT, ha="left")
    ax.text(
        0.45,
        1.33,
        "self-\npropulsion",
        fontsize=FONT_PT["small"],
        color=MUTED,
        ha="center",
        va="center",
        linespacing=0.95,
    )

    draw_pair_force(
        ax,
        np.asarray(positions[2]),
        np.asarray(positions[3]),
        attractive=True,
        label="attract",
    )
    draw_pair_force(
        ax,
        np.asarray(positions[1]),
        np.asarray(positions[3]),
        attractive=False,
        label="repel",
    )
    ax.text(
        0.50,
        0.11,
        "off-lattice positions · stochastic motion · pair forces",
        ha="center",
        va="center",
        fontsize=FONT_PT["small"],
        color=MUTED,
    )


# ---------------------------------------------------------------------------
# Panel (b): Agent-based rules and internal state
# ---------------------------------------------------------------------------


def draw_signal_dots(ax: plt.Axes, points: Iterable[tuple[float, float]]) -> None:
    for index, point in enumerate(points):
        ax.add_patch(
            Circle(
                point,
                0.012 + 0.002 * index,
                facecolor=TEAL,
                edgecolor="none",
                alpha=OPACITY["foreground"],
                zorder=7,
            )
        )


def plot_agent_models(ax: plt.Axes) -> None:
    configure_panel(ax, "b", "Agent-based\nmodels", PANEL_ACCENTS[1])

    source = (0.18, 0.90)
    draw_cell(
        ax,
        source,
        radius=0.092,
        face=BLUE_LIGHT,
        edge=BLUE,
        state_color=PURPLE,
    )
    draw_signal_dots(ax, [(0.055, 0.84), (0.073, 0.91), (0.060, 0.99)])
    draw_arrow(ax, (0.09, 0.91), (0.115, 0.91), color=TEAL, lw=LINE_PT["structure"])
    ax.text(0.13, 0.77, r"state $s_i$", ha="center", fontsize=FONT_PT["body"], color=MUTED)
    ax.text(
        0.055,
        1.08,
        "sense",
        ha="left",
        fontsize=FONT_PT["body"],
        color=TEAL_TEXT,
        fontweight="bold",
    )

    diamond_center = np.asarray((0.45, 0.90))
    half_w, half_h = 0.095, 0.075
    diamond = Polygon(
        [
            diamond_center + (0.0, half_h),
            diamond_center + (half_w, 0.0),
            diamond_center + (0.0, -half_h),
            diamond_center + (-half_w, 0.0),
        ],
        closed=True,
        facecolor=blend_with_white(BLUE),
        edgecolor=BLUE,
        linewidth=LINE_PT["structure"],
        zorder=9,
    )
    ax.add_patch(diamond)
    ax.text(
        *diamond_center,
        "rules",
        ha="center",
        va="center",
        fontsize=FONT_PT["small"],
        fontweight="bold",
        color=INK,
        zorder=11,
    )
    draw_arrow(ax, (0.275, 0.90), (0.35, 0.90), color=INK, lw=LINE_PT["structure"])

    output_rows = (1.28, 1.02, 0.72, 0.39)
    for y in output_rows:
        draw_arrow(
            ax,
            (0.53, 0.90),
            (0.64, y),
            color=FAINT,
            lw=LINE_PT["structure"],
        )

    # Move
    draw_cell(ax, (0.76, output_rows[0]), radius=0.047, nucleus=False)
    draw_arrow(
        ax,
        (0.81, output_rows[0]),
        (0.91, output_rows[0]),
        color=INK,
        lw=LINE_PT["structure"],
    )
    label_box(
        ax,
        (0.65, output_rows[0]),
        "move",
        ha="right",
        fontsize=FONT_PT["body"],
        color=INK,
        alpha=OPACITY["foreground"],
    )

    # Divide
    draw_cell(ax, (0.75, output_rows[1] + 0.025), radius=0.043, nucleus=False)
    draw_cell(ax, (0.82, output_rows[1] - 0.025), radius=0.043, nucleus=False)
    label_box(
        ax,
        (0.65, output_rows[1]),
        "divide",
        ha="right",
        fontsize=FONT_PT["body"],
        color=INK,
        alpha=OPACITY["foreground"],
    )

    # Secrete
    draw_cell(ax, (0.76, output_rows[2]), radius=0.048, nucleus=False)
    draw_signal_dots(
        ax,
        [(0.83, output_rows[2] + 0.035), (0.875, output_rows[2]), (0.83, output_rows[2] - 0.045)],
    )
    label_box(
        ax,
        (0.65, output_rows[2]),
        "secrete",
        ha="right",
        fontsize=FONT_PT["body"],
        color=INK,
        alpha=OPACITY["foreground"],
    )

    # Change state
    draw_cell(
        ax,
        (0.73, output_rows[3]),
        radius=0.045,
        face=BLUE_LIGHT,
        edge=BLUE,
        state_color=BLUE,
    )
    draw_arrow(
        ax,
        (0.78, output_rows[3]),
        (0.83, output_rows[3]),
        color=MUTED,
        lw=LINE_PT["structure"],
    )
    draw_cell(
        ax,
        (0.89, output_rows[3]),
        radius=0.045,
        face=ORANGE_LIGHT,
        edge=ORANGE,
        state_color=ORANGE,
    )
    label_box(
        ax,
        (0.65, output_rows[3]),
        "change\nstate",
        ha="right",
        fontsize=FONT_PT["small"],
        color=INK,
        alpha=OPACITY["foreground"],
    )
    ax.text(
        0.50,
        0.11,
        "cell-level state + explicit decision rules",
        ha="center",
        va="center",
        fontsize=FONT_PT["small"],
        color=MUTED,
    )


# ---------------------------------------------------------------------------
# Panel (c): Lattice and Cellular Potts representations
# ---------------------------------------------------------------------------


def plot_lattice_models(ax: plt.Axes) -> None:
    configure_panel(
        ax,
        "c",
        "Lattice-based\ncell models",
        PANEL_ACCENTS[2],
    )

    x0, y0, step = 0.09, 0.27, 0.117
    n_columns, n_rows = 7, 9
    multi_site_cell = {
        (2, 3),
        (3, 3),
        (4, 3),
        (2, 4),
        (3, 4),
        (4, 4),
        (3, 5),
        (4, 5),
        (4, 6),
    }
    neighbor_cell = {(5, 3), (5, 4), (5, 5), (6, 4)}
    site_agents = {(0, 7), (5, 7), (1, 5), (0, 1), (5, 1), (6, 2)}

    for sites, color in ((multi_site_cell, PURPLE_LIGHT), (neighbor_cell, ORANGE_LIGHT)):
        for col, row in sites:
            ax.add_patch(
                Rectangle(
                    (x0 + col * step, y0 + row * step),
                    step,
                    step,
                    facecolor=color,
                    edgecolor="none",
                    zorder=1,
                )
            )

    for col in range(n_columns + 1):
        x = x0 + col * step
        ax.plot(
            [x, x],
            [y0, y0 + n_rows * step],
            color=GRID,
            lw=LINE_PT["structure"],
            zorder=4,
        )
    for row in range(n_rows + 1):
        y = y0 + row * step
        ax.plot(
            [x0, x0 + n_columns * step],
            [y, y],
            color=GRID,
            lw=LINE_PT["structure"],
            zorder=4,
        )
    ax.add_patch(
        Rectangle(
            (x0, y0),
            n_columns * step,
            n_rows * step,
            fill=False,
            edgecolor=MUTED,
            linewidth=LINE_PT["structure"],
            zorder=5,
        )
    )

    for col, row in site_agents:
        center = (x0 + (col + 0.5) * step, y0 + (row + 0.5) * step)
        ax.add_patch(
            Circle(
                center,
                0.033,
                facecolor=GREEN_LIGHT,
                edgecolor=GREEN,
                linewidth=LINE_PT["structure"],
                zorder=7,
            )
        )

    cluster_center = (
        x0 + 3.6 * step,
        y0 + 4.55 * step,
    )
    ax.text(
        *cluster_center,
        "cell 1",
        ha="center",
        va="center",
        fontsize=FONT_PT["small"],
        fontweight="bold",
        color=PURPLE_TEXT,
        zorder=8,
    )
    ax.text(
        x0 + 5.55 * step,
        y0 + 4.45 * step,
        "cell 2",
        ha="center",
        va="center",
        fontsize=FONT_PT["small"],
        color=ORANGE_TEXT,
        rotation=90,
        zorder=8,
    )
    draw_arrow(
        ax,
        (0.49, 0.20),
        (cluster_center[0], y0 + 3.0 * step),
        color=PURPLE,
        lw=LINE_PT["structure"],
    )
    ax.text(
        0.49,
        0.13,
        "one cell occupies\nmany sites (CPM)",
        ha="center",
        va="center",
        fontsize=FONT_PT["small"],
        color=PURPLE,
        fontweight="bold",
    )
    ax.text(0.87, 1.38, "site agents", ha="right", fontsize=FONT_PT["small"], color=GREEN_TEXT)


# ---------------------------------------------------------------------------
# Panel (d): Continuum, chemical, density, stress, and phase fields
# ---------------------------------------------------------------------------


def normalized(values: np.ndarray) -> np.ndarray:
    low, high = float(np.min(values)), float(np.max(values))
    return (values - low) / (high - low + 1e-12)


def plot_continuum_models(ax: plt.Axes) -> None:
    configure_panel(
        ax,
        "d",
        "Continuum /\nfield-based models",
        PANEL_ACCENTS[3],
    )

    x = np.linspace(0.07, 0.93, 180)
    y = np.linspace(0.24, 1.38, 220)
    xx, yy = np.meshgrid(x, y)

    chemical = (
        0.65 * xx
        + 0.18 * yy
        + 0.35 * np.exp(-((xx - 0.76) ** 2 + (yy - 1.10) ** 2) / 0.06)
        - 0.22 * np.exp(-((xx - 0.25) ** 2 + (yy - 0.45) ** 2) / 0.04)
    )
    chemical = normalized(chemical)
    density = (
        np.exp(-((xx - 0.42) ** 2 / 0.095 + (yy - 0.82) ** 2 / 0.20))
        + 0.55 * np.exp(-((xx - 0.76) ** 2 / 0.10 + (yy - 0.48) ** 2 / 0.16))
    )

    angle = np.arctan2((yy - 0.74) / 0.31, (xx - 0.45) / 0.25)
    radial = np.sqrt(((xx - 0.45) / 0.25) ** 2 + ((yy - 0.74) / 0.31) ** 2)
    distorted_radius = 1.0 + 0.10 * np.cos(3.0 * angle) - 0.05 * np.sin(2.0 * angle)
    phase = 0.5 * (1.0 - np.tanh((radial - distorted_radius) / 0.12))

    ax.contourf(
        xx,
        yy,
        chemical,
        levels=np.linspace(0.0, 1.0, 28),
        cmap=FIELD_CMAP,
        antialiased=True,
        zorder=-5,
    )
    ax.contour(
        xx,
        yy,
        density,
        levels=(0.18, 0.36, 0.58, 0.80),
        colors=INK,
        linewidths=LINE_PT["structure"],
        linestyles=[(0, DASH_PT["dashed"])],
        alpha=OPACITY["context"],
        zorder=3,
    )
    ax.contourf(
        xx,
        yy,
        phase,
        levels=(0.50, 1.01),
        colors=(GREEN_LIGHT,),
        alpha=OPACITY["fill"],
        zorder=2,
    )
    ax.contour(
        xx,
        yy,
        phase,
        levels=(0.2, 0.5, 0.8),
        colors=(WHITE, INK, WHITE),
        linewidths=(LINE_PT["structure"], LINE_PT["emphasis"], LINE_PT["structure"]),
        linestyles=("--", "-", "--"),
        alpha=OPACITY["foreground"],
        zorder=5,
    )
    ax.add_patch(
        Rectangle(
            (0.07, 0.24),
            0.86,
            1.14,
            fill=False,
            edgecolor=ORANGE,
            linewidth=LINE_PT["structure"],
            zorder=12,
        )
    )

    label_box(ax, (0.12, 1.31), r"chemical $c(\mathbf{x},t)$", ha="left")
    label_box(
        ax,
        (0.86, 1.18),
        r"density $\rho(\mathbf{x},t)$" "\ncontours",
        ha="right",
    )
    draw_arrow(
        ax,
        (0.70, 0.49),
        (0.62, 0.59),
        color=INK,
        lw=LINE_PT["structure"],
    )
    label_box(ax, (0.82, 0.40), r"diffuse boundary $\phi$", ha="right")
    ax.text(
        0.50,
        0.12,
        "smooth state variables defined over space",
        ha="center",
        va="center",
        fontsize=FONT_PT["small"],
        color=MUTED,
    )


# ---------------------------------------------------------------------------
# Panel (e): Hybrid coupling of cells, fields, ECM, and force
# ---------------------------------------------------------------------------


def plot_hybrid_models(ax: plt.Axes) -> None:
    configure_panel(
        ax,
        "e",
        "Hybrid / multiscale\nmodels",
        PANEL_ACCENTS[4],
    )

    x = np.linspace(0.07, 0.93, 160)
    y = np.linspace(0.24, 1.38, 190)
    xx, yy = np.meshgrid(x, y)
    chemical = normalized(
        0.35 * xx
        + 0.24 * yy
        + 0.70 * np.exp(-((xx - 0.82) ** 2 + (yy - 1.18) ** 2) / 0.10)
    )
    ax.contourf(
        xx,
        yy,
        chemical,
        levels=np.linspace(0.0, 1.0, 24),
        cmap=FIELD_CMAP,
        antialiased=True,
        alpha=OPACITY["foreground"],
        zorder=-6,
    )

    network_nodes = np.asarray(
        [
            (0.08, 0.31),
            (0.20, 0.53),
            (0.17, 0.79),
            (0.35, 0.36),
            (0.39, 0.62),
            (0.34, 0.88),
            (0.55, 0.30),
            (0.60, 0.52),
            (0.57, 0.79),
            (0.76, 0.38),
            (0.80, 0.66),
            (0.92, 0.45),
            (0.91, 0.83),
        ]
    )
    network_edges = (
        (0, 1),
        (0, 3),
        (1, 2),
        (1, 3),
        (1, 4),
        (2, 4),
        (2, 5),
        (3, 4),
        (3, 6),
        (4, 5),
        (4, 6),
        (4, 7),
        (4, 8),
        (5, 8),
        (6, 7),
        (6, 9),
        (7, 8),
        (7, 9),
        (7, 10),
        (8, 10),
        (8, 12),
        (9, 10),
        (9, 11),
        (10, 11),
        (10, 12),
        (11, 12),
    )
    for first, second in network_edges:
        ax.plot(
            network_nodes[[first, second], 0],
            network_nodes[[first, second], 1],
            color=ECM,
            lw=LINE_PT["structure"],
            alpha=OPACITY["foreground"],
            zorder=2,
        )
    ax.scatter(
        network_nodes[:, 0],
        network_nodes[:, 1],
        s=MARKER_PT["point"] ** 2,
        facecolor=blend_with_white(ECM, 0.45),
        edgecolor=ECM,
        linewidth=LINE_PT["context"],
        zorder=3,
    )

    cell_positions = ((0.24, 1.05), (0.58, 1.18), (0.71, 0.83), (0.45, 0.55))
    for index, position in enumerate(cell_positions):
        draw_cell(
            ax,
            position,
            radius=0.072,
            face=RED_LIGHT,
            edge=RED,
            state_color=RED if index != 2 else ORANGE,
            zorder=10,
        )

    # Chemical guidance: direction is explicitly the increasing illustrative field.
    draw_arrow(
        ax,
        (0.63, 1.22),
        (0.78, 1.33),
        color=GREEN,
        lw=LINE_PT["emphasis"],
    )
    ax.text(
        0.76,
        1.28,
        r"$\nabla c$",
        color=GREEN_TEXT,
        fontsize=FONT_PT["body"],
        fontweight="bold",
    )

    # Mechanical coupling: traction terminates at resolved fiber-network nodes,
    # while the dashed reaction cue points from the matrix back toward a cell.
    draw_arrow(
        ax,
        (0.41, 0.57),
        (0.39, 0.62),
        color=INK,
        lw=LINE_PT["emphasis"],
    )
    draw_arrow(
        ax,
        (0.50, 0.55),
        (0.60, 0.52),
        color=INK,
        lw=LINE_PT["emphasis"],
    )
    draw_arrow(
        ax,
        (0.34, 0.88),
        (0.23, 0.98),
        color=RED,
        lw=LINE_PT["structure"],
        linestyle="--",
    )
    ax.text(0.10, 1.33, r"chemical field $c$", fontsize=FONT_PT["body"], color=INK)
    label_box(ax, (0.12, 0.33), "ECM fibers", ha="left", fontsize=FONT_PT["small"])
    label_box(ax, (0.66, 0.43), r"cell traction $\mathbf{F}$", ha="center", fontsize=FONT_PT["small"])
    label_box(ax, (0.16, 0.86), "ECM feedback", ha="left", fontsize=FONT_PT["small"])
    ax.add_patch(
        Rectangle(
            (0.07, 0.24),
            0.86,
            1.14,
            fill=False,
            edgecolor=RED,
            linewidth=LINE_PT["structure"],
            zorder=14,
        )
    )
    ax.text(
        0.50,
        0.12,
        r"discrete cells $\leftrightarrow$ fields $\leftrightarrow$ matrix mechanics",
        ha="center",
        va="center",
        fontsize=FONT_PT["small"],
        color=MUTED,
    )


# ---------------------------------------------------------------------------
# Cross-cutting resolution axis
# ---------------------------------------------------------------------------


def plot_resolution_axis(ax: plt.Axes) -> None:
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.axis("off")

    ax.text(
        0.50,
        0.93,
        "REPRESENTATION SCALE / RESOLUTION — CROSS-CUTTING, NOT MONOTONIC",
        ha="center",
        va="center",
        fontsize=FONT_PT["title"],
        fontweight="bold",
        color=INK,
    )
    ax.plot(
        [0.055, 0.955],
        [0.66, 0.66],
        color=INK,
        lw=LINE_PT["emphasis"],
        solid_capstyle="butt",
    )
    ax.plot([0.055, 0.055], [0.625, 0.695], color=INK, lw=LINE_PT["emphasis"])
    ax.plot([0.955, 0.955], [0.625, 0.695], color=INK, lw=LINE_PT["emphasis"])

    tick_positions = (0.09, 0.37, 0.65, 0.91)
    tick_labels = (
        "point cell",
        "finite-size cell",
        "shape-resolved cell",
        "tissue-level field",
    )
    for position, label in zip(tick_positions, tick_labels):
        ax.plot(
            [position, position],
            [0.60, 0.72],
            color=INK,
            lw=LINE_PT["structure"],
            solid_capstyle="butt",
        )
        ax.text(
            position,
            0.51,
            label,
            ha="center",
            va="top",
            fontsize=FONT_PT["title"],
            color=INK,
        )

    ax.text(
        0.50,
        0.17,
        "Subcellular states and deformability can be embedded across particle, agent-based, "
        "lattice, field, and hybrid families; neither defines a separate family.",
        ha="center",
        va="center",
        fontsize=FONT_PT["body"],
        color=MUTED,
    )


def build_figure(
    figure_size: tuple[float, float] = PAPER_SIZE_IN,
) -> plt.Figure:
    """Compose the five class panels and the orthogonal resolution axis."""
    fig = plt.figure(figsize=figure_size, facecolor=WHITE)
    grid = fig.add_gridspec(
        2,
        5,
        height_ratios=(5.95, 1.32),
        left=0.025,
        right=0.985,
        top=0.885,
        bottom=0.055,
        wspace=0.065,
        hspace=0.07,
    )

    panels = [fig.add_subplot(grid[0, column]) for column in range(5)]
    plot_particle_models(panels[0])
    plot_agent_models(panels[1])
    plot_lattice_models(panels[2])
    plot_continuum_models(panels[3])
    plot_hybrid_models(panels[4])

    resolution_ax = fig.add_subplot(grid[1, :])
    plot_resolution_axis(resolution_ax)

    fig.text(
        0.03,
        0.958,
        "Computational modeling families for collective cell dynamics",
        ha="left",
        va="top",
        fontsize=FONT_PT["panel"],
        fontweight="bold",
        color=INK,
    )
    fig.text(
        0.03,
        0.914,
        "Non-exclusive families: agent-based implementations may be particle- or lattice-based; hybrids couple representations.",
        ha="left",
        va="top",
        fontsize=FONT_PT["title"],
        color=MUTED,
    )
    fig.text(
        0.975,
        0.914,
        "conceptual schematic · not to scale",
        ha="right",
        va="top",
        fontsize=FONT_PT["body"],
        color=MUTED,
    )
    return fig


def export_figure(
    figure: plt.Figure,
    output_directory: Path,
    basename: str,
) -> tuple[Path, Path]:
    """Export one PDF/SVG pair with outlined SVG text."""
    artifacts = save_vector_pair(
        figure,
        output_directory,
        basename,
        common_options={"bbox_inches": "tight", "pad_inches": 0.08},
    )
    plt.close(figure)
    return artifacts


def main() -> None:
    args = parse_args()
    export_figure(
        build_figure(PAPER_SIZE_IN),
        args.output_dir,
        OUTPUT_BASENAME,
    )


if __name__ == "__main__":
    main()
