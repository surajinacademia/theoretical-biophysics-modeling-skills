"""Original synthetic teaching example; render its sibling data.csv to PDF."""

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / "styles"))
from matplotlib.ticker import MaxNLocator
from pdf_output import save_pdf
from publication import LINE_PT, LAYOUT, paper_style

GROUP_INDEX = {"Control": 0, "Perturbed": 1}

def distribution():
    data = pd.read_csv(ROOT / "data.csv", dtype={"run": "string"})
    fig, ax = plt.subplots()
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    # Shared five-minute bins cover all observations in both conditions.
    bin_width = 5.0
    edges = np.arange(np.floor(data.value.min() / bin_width) * bin_width,
                      np.ceil(data.value.max() / bin_width) * bin_width + bin_width,
                      bin_width)
    centers = (edges[:-1] + edges[1:]) / 2
    bar_width = bin_width * 0.4
    for i, (condition, group) in enumerate(data.groupby("condition", sort=True)):
        style_index = GROUP_INDEX[condition]
        counts, _ = np.histogram(group.value, bins=edges)
        ax.bar(centers + (i - 0.5) * bar_width, counts, width=bar_width * 0.9,
               facecolor=colors[style_index], edgecolor=colors[style_index], linewidth=LINE_PT["outline"],
               label=f"{condition} (n={len(group)})")
    ax.set(xlabel="Persistence time (min)", ylabel="Run count per 5 min bin",
           ylim=(0, None), xlim=(edges[0], edges[-1]))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.legend(loc="upper right", labelcolor=[colors[GROUP_INDEX[c]] for c in sorted(data.condition.unique())])
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
    # Keep rendering inside the shared context for draw-time marker gaps.
    with paper_style():
        fig = distribution()
        save_pdf(fig, args.output, create_parents=True)
        plt.close(fig)


if __name__ == "__main__":
    main()
