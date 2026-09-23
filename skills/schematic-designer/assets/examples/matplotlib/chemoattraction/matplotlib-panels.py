"""Generate the PDF panel inputs for the chemoattraction TikZ compositor.

The panels are intermediate vector work products, not final deliverables.  Run
``tikz-compositor.tex`` afterward to produce the final PDF/outlined-SVG pair.
All simulations are illustrative and deterministic, not experimental data.
The inherited toy model assigns angle zero when the sensed gradient vanishes;
this numerical convention can bias isolated cells and is not a validated model.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from matplotlib.patches import Circle
from scipy.special import k0, k1


SKILL_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(SKILL_ROOT / "scripts"))
sys.path.insert(0, str(SKILL_ROOT / "assets" / "styles" / "matplotlib"))

from scientific_neutral import COLORS, apply_style  # noqa: E402
apply_style()  # Select PGF and CMU/LaTeX before importing pyplot.
import matplotlib.pyplot as plt  # noqa: E402
import minimalist  # noqa: E402
from native_tikz import arrow  # noqa: E402
sys.path.insert(0, str(SKILL_ROOT / "assets" / "styles"))
from minimalist_profile import LINE_PT, MARKER_PT, OPACITY  # noqa: E402
from vector_output import (  # noqa: E402
    prepare_output_directory,
    save_figure_atomic,
)


SOURCE_POSITIONS = np.array([[5.0, 5.0], [7.0, 3.0], [6.0, 7.0]])
SENSOR_POSITION = np.array([2.5, 5.0])


def field_profile(ax) -> None:
    radius = np.linspace(0.05, 8.0, 320)
    for decay_length, linestyle in zip((1.0, 2.0, 4.0), ("-", "--", ":")):
        concentration = k0(radius / decay_length)
        concentration /= concentration[0]
        ax.plot(radius, concentration, linestyle=linestyle, color=COLORS["orange"], linewidth=LINE_PT["emphasis"], label=rf"$\lambda={decay_length:g}$")
    ax.set(xlabel=r"distance $r$ (cell diameters)", ylabel=r"$C(r)/C(0.05)$", xlim=(0, 8), ylim=(0, 1.05))
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(False)
    ax.legend(frameon=False)


def concentration_map(ax) -> None:
    grid = np.linspace(0.0, 10.0, 100)
    x_grid, y_grid = np.meshgrid(grid, grid)
    concentration = np.zeros_like(x_grid)
    decay_length = 2.5
    for source_x, source_y in SOURCE_POSITIONS:
        distance = np.hypot(x_grid - source_x, y_grid - source_y) + 0.05
        concentration += k0(distance / decay_length)
    contours = ax.contourf(x_grid, y_grid, concentration, levels=18, cmap=minimalist.get_cmap("sequential"))
    ax.contour(x_grid, y_grid, concentration, levels=7, colors="white", linewidths=LINE_PT["context"])
    colorbar = plt.colorbar(contours, ax=ax, label=r"$C(\mathbf{r})$")
    colorbar.solids.set_rasterized(False)
    colorbar.solids.set_edgecolor("face")  # Avoid seams between adjacent vector cells.
    ax.scatter(*SOURCE_POSITIONS.T, s=MARKER_PT["emphasis"] ** 2, color=COLORS["orange"], edgecolor=COLORS["ink"], zorder=4)
    ax.scatter(*SENSOR_POSITION, s=MARKER_PT["emphasis"] ** 2, color=COLORS["blue_light"], edgecolor=COLORS["blue"], zorder=5)
    displacement = SOURCE_POSITIONS - SENSOR_POSITION
    distance = np.linalg.norm(displacement, axis=1)
    weights = k1(distance / decay_length) / (decay_length * distance)
    gradient = np.sum(weights[:, None] * displacement, axis=0)
    gradient /= np.linalg.norm(gradient)
    arrow(ax, SENSOR_POSITION, SENSOR_POSITION + 1.25 * gradient,
          color=COLORS["green_text"], linewidth=LINE_PT["emphasis"], zorder=6)
    ax.add_patch(Circle(SENSOR_POSITION, 3.0, fill=False, linestyle="--", linewidth=LINE_PT["structure"], edgecolor=COLORS["blue"]))
    label_box = dict(facecolor=COLORS["canvas"], edgecolor="none", pad=0.6)
    ax.text(*(SENSOR_POSITION + 0.18), r"$i$", bbox=label_box)
    for index, position in enumerate(SOURCE_POSITIONS, start=1):
        ax.text(*(position + 0.18), rf"$j_{index}$", bbox=label_box)
    ax.set(xlabel=r"$x$ (cell diameters)", ylabel=r"$y$ (cell diameters)", xlim=(0, 10), ylim=(0, 10))
    ax.set_xticks([0, 5, 10])
    ax.set_yticks([0, 5, 10])
    ax.set_aspect("equal")


def pairwise_gradient_angles(positions, decay_length=3.0, sensing_radius=3.5):
    displacement = positions[None, :, :] - positions[:, None, :]
    distance = np.linalg.norm(displacement, axis=2)
    active = (distance > 0.15) & (distance <= sensing_radius)
    weights = np.zeros_like(distance)
    weights[active] = k1(distance[active] / decay_length) / (decay_length * distance[active])
    gradient = np.sum(weights[:, :, None] * displacement, axis=1)
    return np.arctan2(gradient[:, 1], gradient[:, 0])


def simulate_cells(*, seed=42, n_cells=24, steps=110, kappa=0.18, sigma=0.35):
    rng = np.random.default_rng(seed)
    positions = rng.uniform(1.0, 9.0, (n_cells, 2))
    headings = rng.uniform(0.0, 2.0 * np.pi, n_cells)
    sampled = [positions.copy()]
    for step in range(steps):
        target = pairwise_gradient_angles(positions)
        headings = (headings + rng.normal(0.0, sigma, n_cells) + kappa * np.sin(target - headings)) % (2.0 * np.pi)
        positions = np.clip(positions + 0.15 * np.column_stack((np.cos(headings), np.sin(headings))), 0.5, 9.5)
        if (step + 1) % 10 == 0:
            sampled.append(positions.copy())
    return np.stack(sampled), positions, headings


def simulation_summary(ax) -> None:
    trajectories, final_positions, headings = simulate_cells()
    for cell_index in range(final_positions.shape[0]):
        ax.plot(trajectories[:, cell_index, 0], trajectories[:, cell_index, 1], color=COLORS["faint"], linewidth=LINE_PT["context"], alpha=OPACITY["context"])
    ax.scatter(*final_positions.T, color=COLORS["blue_light"], edgecolor=COLORS["blue"], s=MARKER_PT["point"] ** 2, zorder=3)
    # Preserve the previous 1/5 data-unit direction vectors; only heads change.
    for position, heading in zip(final_positions, headings):
        arrow(ax, position, position + np.array([np.cos(heading), np.sin(heading)]) / 5.0,
              color=COLORS["green_text"], linewidth=LINE_PT["structure"])
    ax.set(xlabel=r"$x$ (cell diameters)", ylabel=r"$y$ (cell diameters)", xlim=(0.3, 9.7), ylim=(0.3, 9.7))
    ax.set_aspect("equal")


def phase_diagram(ax) -> None:
    kappas = np.linspace(0.03, 0.72, 7)
    sigmas = np.linspace(0.08, 1.0, 7)
    order = np.zeros((len(sigmas), len(kappas)))
    for row, sigma in enumerate(sigmas):
        for column, kappa in enumerate(kappas):
            _, _, headings = simulate_cells(seed=700 + 31 * row + column, n_cells=16, steps=60, kappa=float(kappa), sigma=float(sigma))
            order[row, column] = np.abs(np.mean(np.exp(1j * headings)))
    # Each cell shows one of the 49 simulated values. Midpoint display edges
    # preserve sampled coordinates without inventing interpolated boundaries.
    def edges(values):
        midpoints = (values[:-1] + values[1:]) / 2
        return np.r_[values[0] - (midpoints[0] - values[0]), midpoints,
                     values[-1] + (values[-1] - midpoints[-1])]
    cells = ax.pcolormesh(edges(kappas), edges(sigmas), order, shading="flat",
                         cmap=minimalist.get_cmap("sequential"), vmin=0, vmax=1)
    colorbar = plt.colorbar(cells, ax=ax, label=r"$|\langle e^{i\theta}\rangle|$", ticks=[0, 0.5, 1])
    colorbar.solids.set_rasterized(False)
    colorbar.solids.set_edgecolor("face")  # Avoid seams between adjacent vector cells.
    ax.set(xlabel=r"coupling $\kappa$", ylabel=r"noise $\sigma$")


PANEL_DRAWERS = (
    ("field-profile", field_profile),
    ("concentration-map", concentration_map),
    ("simulation-summary", simulation_summary),
    ("phase-diagram", phase_diagram),
)


def build_panels(panel_directory: Path) -> tuple[Path, ...]:
    apply_style()
    approved_panels = prepare_output_directory(panel_directory)
    paths = []
    for name, drawer in PANEL_DRAWERS:
        panel_figure, panel_axis = plt.subplots(figsize=(7.8 / 2.54, 5.15 / 2.54), constrained_layout=True)
        drawer(panel_axis)
        save_figure_atomic(panel_figure, approved_panels, f"{name}.pdf")
        plt.close(panel_figure)
        paths.append(approved_panels / f"{name}.pdf")
    return tuple(paths)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--panel-dir", type=Path, required=True)
    arguments = parser.parse_args()
    for panel_path in build_panels(arguments.panel_dir):
        print(panel_path)


if __name__ == "__main__":
    main()
