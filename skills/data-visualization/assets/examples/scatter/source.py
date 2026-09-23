"""Original synthetic teaching example; render its sibling data.csv to PDF."""

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / "styles"))
from publication import MARKERS, LAYOUT, paper_style

GROUP_INDEX = {"Control": 0, "Perturbed": 1}

def scatter():
    data = pd.read_csv(ROOT / "data.csv", dtype={"run": "string"})
    if data.duplicated(["condition", "run"]).any():
        raise ValueError("One pair of observables per run is required")
    fig, ax = plt.subplots()
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for condition, group in data.groupby("condition", sort=True):
        style_index = GROUP_INDEX[condition]
        ax.scatter(group.area, group.speed, s=plt.rcParams["lines.markersize"] ** 2,
                   marker=MARKERS[style_index], facecolor="none", edgecolor=colors[style_index],
                   linewidth=plt.rcParams["lines.markeredgewidth"],
                   label=f"{condition} (n={len(group)})")
    ax.set(xlabel="Area (µm²)", ylabel="Speed (µm/min)")
    ax.legend(loc="upper left", labelcolor=[colors[GROUP_INDEX[c]] for c in sorted(data.condition.unique())])
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
        fig = scatter()
        fig.savefig(args.output)
        plt.close(fig)


if __name__ == "__main__":
    main()
