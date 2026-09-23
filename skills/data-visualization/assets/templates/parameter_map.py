"""Plot one precomputed descriptive scalar per numeric (x, y) parameter pair.

CSV columns: x,y,value. Missing pairs and blank values remain missing cells.
Coordinates are cell centers: edges lie halfway between neighboring centers,
with outer edges extended by half the nearest spacing. At least two distinct
coordinates per axis are required; no cell width is invented for a singleton.
Keep templates/ and ../styles/ together when copying this example.
"""

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "styles"))
from publication import get_cmap, paper_style, LAYOUT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--xlabel", default="x (supply units)")
    parser.add_argument("--ylabel", default="y (supply units)")
    parser.add_argument("--colorbar-label", default="Value (supply units)")
    args = parser.parse_args()
    if args.output.suffix.lower() != ".pdf":
        parser.error("output must end in .pdf")
    if any(path.is_symlink() for path in (args.output, *args.output.parents)):
        parser.error("output must not be a symlink or pass through a symlink")
    if args.output.resolve() == args.input.resolve():
        parser.error("input and output must be different files")

    data = pd.read_csv(args.input, keep_default_na=False,
                       na_values={"value": ["", "NaN", "nan"]})
    if not {"x", "y", "value"}.issubset(data.columns) or data.empty:
        parser.error("input needs nonempty x,y,value columns")
    for column in ["x", "y", "value"]:
        data[column] = pd.to_numeric(data[column], errors="raise")
    if not np.isfinite(data[["x", "y"]]).all().all():
        parser.error("x and y keys must be finite and present")
    if np.isinf(data["value"]).any():
        parser.error("values may be missing but not infinite")
    if data.duplicated(["x", "y"]).any():
        parser.error("expected exactly one precomputed value per x,y pair")
    if not data["value"].notna().any():
        parser.error("at least one measured value is needed to define the color scale")

    # Plain pivot deliberately rejects aggregation of repeated parameter pairs.
    grid = data.pivot(index="y", columns="x", values="value").sort_index().sort_index(axis=1)
    x = grid.columns.to_numpy(dtype=float)
    y = grid.index.to_numpy(dtype=float)
    if len(x) < 2 or len(y) < 2:
        parser.error("need at least two distinct coordinates per axis to infer cell edges")
    x_edges = np.r_[x[0] - (x[1] - x[0]) / 2, (x[:-1] + x[1:]) / 2,
                    x[-1] + (x[-1] - x[-2]) / 2]
    y_edges = np.r_[y[0] - (y[1] - y[0]) / 2, (y[:-1] + y[1:]) / 2,
                    y[-1] + (y[-1] - y[-2]) / 2]
    with paper_style():
        fig, ax = plt.subplots()
        cmap = get_cmap("sequential").with_extremes(bad="#dddddd")
        mesh = ax.pcolormesh(x_edges, y_edges, np.ma.masked_invalid(grid.to_numpy()),
                             cmap=cmap, shading="flat")
        ax.set(xlabel=args.xlabel, ylabel=args.ylabel)
        fig.colorbar(mesh, ax=ax, label=args.colorbar_label)
        if grid.isna().any().any():
            missing_y, missing_x = np.where(grid.isna().to_numpy())
            ax.scatter(x[missing_x], y[missing_y], marker="x",
                       s=plt.rcParams["lines.markersize"] ** 2, color="0.35",
                       linewidth=plt.rcParams["lines.markeredgewidth"])
            ax.legend(handles=[Line2D([], [], color="0.35", marker="x", linestyle="none", label="Missing")],
                      loc="upper center", bbox_to_anchor=(0.5, 1.16), labelcolor="0.35")
        fig.tight_layout(pad=LAYOUT["pad"])
        fig.savefig(args.output)
        plt.close(fig)


if __name__ == "__main__":
    main()
