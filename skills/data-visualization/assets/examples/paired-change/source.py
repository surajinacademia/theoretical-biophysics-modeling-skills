"""Original synthetic teaching example; render its sibling data.csv to PDF."""

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / "styles"))
from publication import LINE_PT, OPACITY, LAYOUT, paper_style

STATE_INDEX = {"Before": 0, "After": 1}

def paired_change():
    data = pd.read_csv(ROOT / "data.csv", dtype={"run": "string"})
    paired = data.pivot(index="run", columns="state", values="value")
    if paired[["Before", "After"]].isna().any().any():
        raise ValueError("Every run needs both measurements")
    fig, ax = plt.subplots()
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for _, row in paired.iterrows():
        ax.plot([0, 1], row[["Before", "After"]], color="black", linewidth=LINE_PT["context"], alpha=OPACITY["context"], zorder=1)
    marker_area = plt.rcParams["lines.markersize"] ** 2
    edge_width = plt.rcParams["lines.markeredgewidth"]
    ax.scatter(np.zeros(len(paired)), paired.Before, facecolors="none", edgecolors=colors[STATE_INDEX["Before"]],
               s=marker_area, linewidths=edge_width, zorder=2)
    ax.scatter(np.ones(len(paired)), paired.After, facecolors="none", edgecolors=colors[STATE_INDEX["After"]],
               marker="s", s=marker_area, linewidths=edge_width, zorder=2)
    ax.set(xticks=[0, 1], xticklabels=["Before", "After"], xlim=(-0.25, 1.25),
           ylabel="Speed (µm/min)")
    ax.text(0.04, 0.96, f"{len(paired)} matched runs", transform=ax.transAxes, va="top")
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
        fig = paired_change()
        fig.savefig(args.output)
        plt.close(fig)


if __name__ == "__main__":
    main()
