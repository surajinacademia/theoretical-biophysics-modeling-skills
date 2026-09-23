"""Publication figure for a toy activator--inhibitor model.

The one-dimensional steady profiles are

    u(x) = exp[-x^2 / (2 sigma_u^2)]
    v(x) = A_v exp[-x^2 / (2 sigma_v^2)],

with sigma_u = 0.7, sigma_v = 1.5, and A_v = 0.65.  The two-dimensional
panel uses the explicit isotropic extension r^2 = x^2 + y^2 and plots u-v.

The script follows the schematic-designer Minimalist profile
and writes deterministic PDF and outlined-text SVG outputs.
"""

import argparse
from pathlib import Path
import sys

import matplotlib

matplotlib.use("pgf")

import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Circle, Ellipse
from matplotlib.text import Text
import numpy as np

SKILL_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
sys.path.insert(0, str(SKILL_ROOT / "assets" / "styles" / "matplotlib"))
sys.path.insert(0, str(SKILL_ROOT / "assets" / "styles"))

from learning_dynamics_2406 import COLORS, FONT_SIZES, apply_style  # noqa: E402
from native_tikz import arrow as tikz_arrow
from minimalist_profile import FONT_PT, LINE_PT, DASH_PT
from vector_output import save_vector_pair  # noqa: E402


# Scientific parameters -------------------------------------------------------
SIGMA_U = 0.7
SIGMA_V = 1.5
AMPLITUDE_V = 0.65
PROFILE_X_MIN = -3.5
PROFILE_X_MAX = 3.5
FIELD_LIMIT = 3.25
PROFILE_SAMPLES = 1001
FIELD_SAMPLES = 501


# Aesthetic profile aliases ---------------------------------------------------
STYLE_CANVAS = COLORS["canvas"]
STYLE_INK = COLORS["ink"]
STYLE_MUTED = COLORS["muted"]
STYLE_BLUE = COLORS["blue"]
STYLE_BLUE_DARK = COLORS["blue_dark"]
STYLE_RED = COLORS["red"]
STYLE_RED_DARK = COLORS["red_dark"]
STYLE_PALE_BLUE = COLORS["fixed_section"]
STYLE_PALE_RED = COLORS["cycle_section"]

PANEL_LABEL_SIZE = FONT_SIZES["panel_label"]
PANEL_TITLE_SIZE = FONT_SIZES["panel_title"]
AXIS_LABEL_SIZE = FONT_PT["body"]
TICK_LABEL_SIZE = FONT_SIZES["tick_label"]
ANNOTATION_SIZE = FONT_SIZES["annotation"]

apply_style()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs"))
    return parser.parse_args()


def profiles_1d(x):
    """Return the prescribed one-dimensional steady profiles."""
    x = np.asarray(x, dtype=float)
    u = np.exp(-(x**2) / (2.0 * SIGMA_U**2))
    v = AMPLITUDE_V * np.exp(-(x**2) / (2.0 * SIGMA_V**2))
    return u, v


def field_2d(x, y):
    """Return u, v, and u-v for the isotropic radial 2D extension."""
    radius_squared = np.asarray(x, dtype=float) ** 2 + np.asarray(y, dtype=float) ** 2
    u = np.exp(-radius_squared / (2.0 * SIGMA_U**2))
    v = AMPLITUDE_V * np.exp(-radius_squared / (2.0 * SIGMA_V**2))
    return u, v, u - v


def zero_crossing_radius():
    """Analytic radius at which the two Gaussian fields are equal."""
    denominator = 1.0 / SIGMA_U**2 - 1.0 / SIGMA_V**2
    return np.sqrt(2.0 * np.log(1.0 / AMPLITUDE_V) / denominator)


def panel_heading(ax, letter, title):
    """Add the profile's bold uppercase panel tag and short heading."""
    position = ax.get_position(original=True)
    ax.figure.text(
        position.x0 - 0.02,
        position.y1 + 0.02,
        letter.upper(),
        ha="left",
        va="bottom",
        clip_on=False,
        fontsize=PANEL_LABEL_SIZE,
        fontfamily="sans-serif",
        fontweight="bold",
        color=STYLE_INK,
    )
    ax.figure.text(
        position.x0 + 0.02,
        position.y1 + 0.02,
        title,
        ha="left",
        va="bottom",
        clip_on=False,
        fontsize=PANEL_TITLE_SIZE,
        fontfamily="sans-serif",
        fontweight="bold",
        color=STYLE_INK,
    )


def minimal_axes(ax, *, snapshot=False):
    """Apply the profile's sparse quantitative-axis treatment."""
    ax.grid(False)
    ax.tick_params(
        direction="out",
        width=LINE_PT["structure"],
        length=3.0,
        labelsize=TICK_LABEL_SIZE,
        colors=STYLE_INK,
        pad=2.5,
    )
    for name, spine in ax.spines.items():
        spine.set_visible(snapshot or name in {"left", "bottom"})
        spine.set_linewidth(LINE_PT["structure"])
        spine.set_color(STYLE_INK)


def soft_halo(ax, radius, color, *, zorder):
    """Draw a low-opacity schematic halo beneath vector interaction marks."""
    radii = np.linspace(radius, 0.42 * radius, 9)
    alphas = np.linspace(0.020, 0.075, len(radii))
    for current_radius, alpha in zip(radii, alphas):
        ax.add_patch(
            Ellipse(
                (0.0, 0.08),
                2.0 * current_radius,
                1.05 * current_radius,
                facecolor=color,
                edgecolor="none",
                alpha=alpha,
                zorder=zorder,
            )
        )


def range_bar(ax, half_width, y, color, label, *, dashed=False):
    """Draw a centered scale cue with terminal ticks."""
    linestyle = (0, DASH_PT["dashed"]) if dashed else "-"
    ax.plot(
        [-half_width, half_width],
        [y, y],
        color=color,
        lw=LINE_PT["structure"],
        ls=linestyle,
        solid_capstyle="butt",
        zorder=8,
    )
    ax.plot(
        [-half_width, -half_width],
        [y - 0.07, y + 0.07],
        color=color,
        lw=LINE_PT["structure"],
        zorder=8,
    )
    ax.plot(
        [half_width, half_width],
        [y - 0.07, y + 0.07],
        color=color,
        lw=LINE_PT["structure"],
        zorder=8,
    )
    ax.text(
        0.0,
        y - 0.13,
        label,
        ha="center",
        va="top",
        fontsize=ANNOTATION_SIZE,
        color=color,
    )


def draw_schematic(ax):
    """Panel (a): local self-activation and long-range inhibition."""
    ax.set_xlim(-2.75, 2.75)
    ax.set_ylim(-2.1, 1.72)
    ax.set_aspect("equal")
    ax.axis("off")

    # Long-range inhibitor field below the local activator field.
    soft_halo(ax, 2.20, STYLE_RED, zorder=0)
    soft_halo(ax, 0.95, STYLE_BLUE, zorder=1)

    # Activator core.
    core = Circle(
        (0.0, 0.08),
        0.30,
        facecolor=STYLE_PALE_BLUE,
        edgecolor=STYLE_BLUE_DARK,
        linewidth=LINE_PT["structure"],
        zorder=7,
    )
    ax.add_patch(core)
    ax.text(0.0, 0.08, r"$u$", ha="center", va="center", fontsize=FONT_PT["panel"], zorder=8)

    # Solid curved feedback arrow: u promotes itself locally.
    tikz_arrow(ax, (-0.24, 0.36), (0.24, 0.36),
               color=STYLE_BLUE_DARK, linewidth=LINE_PT["emphasis"],
               rad=-1.10, zorder=9)
    ax.text(
        0.0,
        1.26,
        "local self-activation  +",
        ha="center",
        va="center",
        fontsize=FONT_PT["body"],
        fontfamily="sans-serif",
        fontweight="bold",
        color=STYLE_BLUE_DARK,
        zorder=10,
    )

    # Two spatially separated v cues terminate in standard inhibitory bars at u.
    for side in (-1.0, 1.0):
        x_v = 2.08 * side
        v_node = Circle(
            (x_v, 0.08),
            0.22,
            facecolor=STYLE_CANVAS,
            edgecolor=STYLE_RED_DARK,
            linewidth=LINE_PT["structure"],
            linestyle=(0, DASH_PT["dashed"]),
            zorder=7,
        )
        ax.add_patch(v_node)
        ax.text(x_v, 0.08, r"$v$", ha="center", va="center", fontsize=FONT_PT["title"], zorder=8)
        x_bar = 0.43 * side
        ax.plot(
            [x_v - 0.25 * side, x_bar],
            [0.08, 0.08],
            color=STYLE_RED_DARK,
            lw=LINE_PT["structure"],
            ls=(0, DASH_PT["dashed"]),
            zorder=6,
        )
        ax.plot(
            [x_bar, x_bar],
            [-0.06, 0.22],
            color=STYLE_RED_DARK,
            lw=LINE_PT["emphasis"],
            zorder=7,
        )

    ax.text(
        0.0,
        0.70,
        "long-range inhibition  -",
        ha="center",
        va="center",
        fontsize=FONT_PT["body"],
        fontfamily="sans-serif",
        fontweight="bold",
        color=STYLE_RED_DARK,
        zorder=10,
    )

    range_bar(ax, SIGMA_U, -0.93, STYLE_BLUE_DARK, r"local range  $\sigma_u=0.7$")
    range_bar(
        ax,
        SIGMA_V,
        -1.65,
        STYLE_RED_DARK,
        r"longer range  $\sigma_v=1.5$",
        dashed=True,
    )
    panel_heading(ax, "a", "interaction logic")


def draw_profiles(ax, x, u, v):
    """Panel (b): directly computed 1D Gaussian profiles."""
    ax.plot(x, u, color=STYLE_BLUE_DARK, lw=LINE_PT["emphasis"], solid_capstyle="butt", zorder=4)
    ax.plot(
        x,
        v,
        color=STYLE_RED_DARK,
        lw=LINE_PT["emphasis"],
        ls=(0, DASH_PT["dashed"]),
        solid_capstyle="butt",
        zorder=3,
    )
    ax.axhline(0.0, color=STYLE_INK, lw=LINE_PT["structure"], zorder=1)

    ax.set_xlim(PROFILE_X_MIN, PROFILE_X_MAX)
    ax.set_ylim(-0.02, 1.10)
    ax.set_xticks([-3, 0, 3])
    ax.set_yticks([0.0, 0.5, 1.0])
    ax.set_xlabel(r"position $x$", fontsize=AXIS_LABEL_SIZE)
    ax.set_ylabel("steady amplitude", fontsize=AXIS_LABEL_SIZE)
    minimal_axes(ax)

    # Direct formula labels eliminate a legend while preserving the model exactly.
    ax.text(
        0.12,
        1.015,
        r"$u=e^{-x^2/(2\,0.7^2)}$",
        ha="left",
        va="bottom",
        fontsize=FONT_PT["body"],
        color=STYLE_BLUE_DARK,
    )
    ax.text(
        0.75,
        0.75,
        r"$v=0.65e^{-x^2/(2\,1.5^2)}$",
        ha="left",
        va="bottom",
        fontsize=FONT_PT["body"],
        color=STYLE_RED_DARK,
    )
    panel_heading(ax, "b", "steady 1D profiles")


def draw_net_field(ax, cax, x, y, net):
    """Panel (c): computed signed 2D field for the radial extension."""
    signed_cmap = LinearSegmentedColormap.from_list(
        "activation_inhibition",
        [STYLE_RED, STYLE_PALE_RED, STYLE_CANVAS, STYLE_PALE_BLUE, STYLE_BLUE],
        N=256,
    )
    bound = float(np.max(np.abs(net)))
    norm = TwoSlopeNorm(vmin=-bound, vcenter=0.0, vmax=bound)
    image = ax.imshow(
        net,
        origin="lower",
        extent=(x.min(), x.max(), y.min(), y.max()),
        cmap=signed_cmap,
        norm=norm,
        interpolation="bilinear",
        rasterized=True,
        zorder=0,
    )

    # A dashed zero contour redundantly encodes the sign transition.
    contour = ax.contour(
        x,
        y,
        net,
        levels=[0.0],
        colors=[STYLE_INK],
        linewidths=[LINE_PT["structure"]],
        linestyles=[(0, DASH_PT["dashed"])],
        zorder=3,
    )
    ax.clabel(
        contour,
        fmt={0.0: r"$u=v$"},
        fontsize=FONT_PT["small"],
        inline=True,
        inline_spacing=3,
        manual=[(zero_crossing_radius() / np.sqrt(2), zero_crossing_radius() / np.sqrt(2))],
    )

    ax.text(
        0.0,
        0.0,
        r"$u>v$",
        ha="center",
        va="center",
        fontsize=FONT_PT["body"],
        color=STYLE_INK,
        zorder=4,
    )
    ax.text(
        1.55,
        0.0,
        r"$v>u$",
        ha="center",
        va="center",
        fontsize=FONT_PT["body"],
        color=STYLE_INK,
        zorder=4,
    )

    ax.set_xlim(-FIELD_LIMIT, FIELD_LIMIT)
    ax.set_ylim(-FIELD_LIMIT, FIELD_LIMIT)
    ax.set_aspect("equal")
    ax.set_xticks([-3, 0, 3])
    ax.set_yticks([-3, 0, 3])
    ax.set_xlabel(r"$x$", fontsize=AXIS_LABEL_SIZE, labelpad=1.5)
    ax.set_ylabel(r"$y$", fontsize=AXIS_LABEL_SIZE, labelpad=1.5)
    minimal_axes(ax, snapshot=True)
    panel_heading(ax, "c", r"net 2D field  $u-v$")
    ax.text(
        0.02,
        0.98,
        r"radial extension:  $r^2=x^2+y^2$",
        transform=ax.transAxes,
        ha="left",
        va="top",
        fontsize=FONT_PT["small"],
        color=STYLE_MUTED,
        zorder=4,
    )

    colorbar = ax.figure.colorbar(image, cax=cax, orientation="horizontal")
    colorbar.set_ticks([-bound, 0.0, bound])
    colorbar.set_ticklabels([f"{-bound:.2f}", "0", f"{bound:.2f}"])
    colorbar.ax.tick_params(
        direction="out",
        width=LINE_PT["context"],
        length=2.3,
        labelsize=FONT_PT["small"],
        colors=STYLE_INK,
        pad=1.5,
    )
    colorbar.outline.set_linewidth(LINE_PT["structure"])
    colorbar.outline.set_edgecolor(STYLE_INK)
    colorbar.set_label(r"net field $u-v$", fontsize=FONT_PT["body"], labelpad=1.0)


def validate_science(x, u, v, field_x, field_y, net):
    """Fail early if the rendered arrays do not match the stated model."""
    center_1d = int(np.argmin(np.abs(x)))
    center_x = int(np.argmin(np.abs(field_x)))
    center_y = int(np.argmin(np.abs(field_y)))
    radius0 = zero_crossing_radius()

    if not np.isclose(u[center_1d], 1.0, atol=1e-12):
        raise RuntimeError("u(0) is not 1")
    if not np.isclose(v[center_1d], AMPLITUDE_V, atol=1e-12):
        raise RuntimeError("v(0) does not equal the prescribed amplitude")
    if not np.isclose(net[center_y, center_x], 1.0 - AMPLITUDE_V, atol=1e-12):
        raise RuntimeError("the central 2D net field is inconsistent")
    if not (np.min(net) < 0.0 < np.max(net)):
        raise RuntimeError("the signed field does not cross zero")
    if not (SIGMA_V > SIGMA_U and 0.0 < radius0 < FIELD_LIMIT):
        raise RuntimeError("the local/long-range ordering is inconsistent")


def validate_layout(fig):
    """Check that visible text lies within the fixed-size canvas."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    canvas_width, canvas_height = fig.canvas.get_width_height()
    violations = []
    for text_artist in fig.findobj(match=Text):
        if not text_artist.get_visible() or not text_artist.get_text().strip():
            continue
        bounds = text_artist.get_window_extent(renderer=renderer)
        if (
            bounds.x0 < -1.0
            or bounds.y0 < -1.0
            or bounds.x1 > canvas_width + 1.0
            or bounds.y1 > canvas_height + 1.0
        ):
            violations.append(text_artist.get_text())
    if violations:
        raise RuntimeError(f"text outside figure canvas: {violations}")


def main():
    args = parse_args()
    profile_x = np.linspace(PROFILE_X_MIN, PROFILE_X_MAX, PROFILE_SAMPLES)
    u_profile, v_profile = profiles_1d(profile_x)

    field_x = np.linspace(-FIELD_LIMIT, FIELD_LIMIT, FIELD_SAMPLES)
    field_y = np.linspace(-FIELD_LIMIT, FIELD_LIMIT, FIELD_SAMPLES)
    X, Y = np.meshgrid(field_x, field_y)
    _, _, net = field_2d(X, Y)
    validate_science(profile_x, u_profile, v_profile, field_x, field_y, net)

    fig = plt.figure(figsize=(7.05, 3.15), facecolor=STYLE_CANVAS)
    grid = GridSpec(
        1,
        3,
        figure=fig,
        width_ratios=[1.12, 1.00, 1.08],
        left=0.055,
        right=0.985,
        bottom=0.16,
        top=0.83,
        wspace=0.43,
    )
    ax_a = fig.add_subplot(grid[0, 0])
    ax_b = fig.add_subplot(grid[0, 1])
    field_grid = grid[0, 2].subgridspec(2, 1, height_ratios=[1.0, 0.075], hspace=0.30)
    ax_c = fig.add_subplot(field_grid[0, 0])
    cax = fig.add_subplot(field_grid[1, 0])

    draw_schematic(ax_a)
    draw_profiles(ax_b, profile_x, u_profile, v_profile)
    draw_net_field(ax_c, cax, field_x, field_y, net)
    validate_layout(fig)

    metadata = {
        "Title": "Local activation and long-range inhibition",
        "Subject": "Computed toy activator-inhibitor model",
        "Creator": "Matplotlib",
    }
    # The PDF's intentionally rasterized scalar field is embedded at 600 dpi;
    # all text, contours, axes, and schematic geometry remain vector objects.
    pdf_path, svg_path = save_vector_pair(
        fig,
        args.output_dir,
        "activator-inhibitor",
        common_options={"dpi": 600},
        pdf_options={"metadata": metadata},
    )
    plt.close(fig)

    print(f"science_validation=PASS zero_radius={zero_crossing_radius():.6f}")
    print("layout_validation=PASS all_visible_text_inside_canvas")
    print(f"pdf={pdf_path}")
    print(f"svg={svg_path}")


if __name__ == "__main__":
    main()
