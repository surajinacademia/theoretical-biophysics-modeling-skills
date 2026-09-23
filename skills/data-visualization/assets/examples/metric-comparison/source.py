"""Original synthetic teaching example; render its sibling data.csv to PDF."""

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / "styles"))
from matplotlib.font_manager import FontProperties
from publication import FONT_PT, LINE_PT, MARK_PT, LAYOUT, MARKERS, paper_style

GROUP_INDEX = {"Control": 0, "Perturbed": 1}

def metric_comparison():
    data = pd.read_csv(ROOT / "data.csv", dtype={"run": "string"})
    if data.duplicated(["condition", "run"]).any():
        raise ValueError("One row per condition/run is required")
    fig, axes = plt.subplots(1, 2, figsize=(170 / 25.4, 70 / 25.4))
    colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    for ax, metric, label, tag in zip(axes, ["speed", "order"],
                                     ["Speed (µm/min)", "Order (dimensionless)"], ["a", "b"]):
        for i, (condition, group) in enumerate(data.groupby("condition", sort=True)):
            style_index = GROUP_INDEX[condition]
            values = group.sort_values("run")[metric]
            ax.scatter(i + np.linspace(-0.13, 0.13, len(values)), values,
                       s=plt.rcParams["lines.markersize"] ** 2, marker=MARKERS[style_index],
                       facecolors="none", edgecolors=colors[style_index],
                       linewidths=plt.rcParams["lines.markeredgewidth"])
            # Keep summaries clear of the hollow observations; a dash has no interior.
            ax.errorbar(i + 0.26, values.mean(), yerr=values.std(ddof=1), color=colors[style_index],
                        ecolor=colors[style_index],
                        fmt="_", markersize=MARK_PT["mean"], capsize=MARK_PT["cap"],
                        linewidth=LINE_PT["outline"], marker_gap=False)
        ax.set(xticks=[0, 1], xticklabels=["Control", "Perturbed"],
               ylabel=label, xlim=(-0.5, 1.5))
        ax.set_title(f"({tag})", loc="left", fontproperties=FontProperties(
            family=plt.rcParams["font.family"], weight="bold", stretch="expanded",
            size=FONT_PT["panel"]))
    fig.text(0.5, LAYOUT["note_y"], "6 runs per condition · marks: equal-run mean ± sample SD", ha="center", fontsize=FONT_PT["note"])
    fig.tight_layout(rect=(0, LAYOUT["note_top"], 1, 1), pad=LAYOUT["pad"], w_pad=LAYOUT["panel_gap"])
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
        fig = metric_comparison()
        fig.savefig(args.output)
        plt.close(fig)


if __name__ == "__main__":
    main()
