"""Original synthetic teaching example; render its sibling data.csv to PDF."""

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / "styles"))
from matplotlib.colors import TwoSlopeNorm
from publication import get_cmap, LAYOUT, paper_style

def signed_map():
    data = pd.read_csv(ROOT / "data.csv", dtype={"run": "string"})
    grid = data.pivot(index="y", columns="x", values="value").sort_index().sort_index(axis=1)
    x, y = grid.columns.to_numpy(), grid.index.to_numpy()
    cmap = get_cmap("diverging")
    fig, ax = plt.subplots()
    # Image pixels are centered on the saved grid coordinates. Bilinear rendering
    # smooths only their display; no values are filtered or missing cells filled.
    dx, dy = x[1] - x[0], y[1] - y[0]
    mesh = ax.imshow(grid.to_numpy(), origin="lower", aspect="auto",
                     extent=(x[0] - dx / 2, x[-1] + dx / 2,
                             y[0] - dy / 2, y[-1] + dy / 2),
                     interpolation="bilinear", cmap=cmap,
                     norm=TwoSlopeNorm(vmin=-1, vcenter=0, vmax=1))
    ax.set(xlabel="Bias (dimensionless)", ylabel="Coupling (dimensionless)",
           xlim=(x[0], x[-1]), ylim=(y[0], y[-1]))
    fig.colorbar(mesh, ax=ax, label="Signed response", ticks=[-1, 0, 1])
    fig.tight_layout(pad=LAYOUT["pad"])
    return fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "figure.pdf")
    args = parser.parse_args()
    if args.output.suffix.lower() != ".pdf":
        parser.error("output must end in .pdf")
    if any(p.is_symlink() for p in (args.output, *args.output.parents)):
        parser.error("output paths must not contain symlinks")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    # Keep rendering inside the shared context for draw-time marker gaps.
    with paper_style():
        fig = signed_map()
        fig.savefig(args.output)
        plt.close(fig)


if __name__ == "__main__":
    main()
