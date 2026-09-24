"""Show all precomputed run values and the equal-run mean ± sample SD.

CSV columns: condition,run,value; one value per condition/run. Blank values
are missing measurements, counted separately from measured zero.
Keep templates/ and ../styles/ together when copying this example.
"""

import argparse
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "styles"))
from pdf_output import save_pdf
from publication import paper_style, FONT_PT, MARK_PT, LAYOUT, MARKERS


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--xlabel", default="Condition")
    parser.add_argument("--ylabel", default="Value (supply units)")
    parser.add_argument("--group-order", nargs="+", metavar="GROUP",
                        help="Full ordered group universe, including groups absent from this file; keeps colors and shapes stable across subsets")
    args = parser.parse_args()
    if args.output.suffix.lower() != ".pdf":
        parser.error("output must end in .pdf")
    if any(path.is_symlink() for path in (args.output, *args.output.parents)):
        parser.error("output must not be a symlink or pass through a symlink")
    if args.output.resolve() == args.input.resolve():
        parser.error("input and output must be different files")

    data = pd.read_csv(args.input, dtype={"condition": "string", "run": "string"},
                       keep_default_na=False, na_values={"value": ["", "NaN", "nan"]})
    keys = ["condition", "run"]
    if not set(keys + ["value"]).issubset(data.columns) or data.empty:
        parser.error("input needs nonempty condition,run,value columns")
    if data[keys].isna().any().any() or data[keys].eq("").any().any():
        parser.error("condition and run keys must not be missing")
    if data.duplicated(keys).any():
        parser.error("expected exactly one precomputed value per condition,run")
    data["value"] = pd.to_numeric(data["value"], errors="raise")
    if np.isinf(data["value"]).any():
        parser.error("values may be missing but not infinite")

    conditions = sorted(data["condition"].unique())
    group_order = args.group_order or conditions
    if len(group_order) != len(set(group_order)) or not set(conditions).issubset(group_order):
        parser.error("group-order must contain each observed condition exactly once, with no duplicates")
    group_index = {condition: i for i, condition in enumerate(group_order)}
    summary = data.groupby("condition")["value"].agg(["mean", "std", "count", "size"])
    with paper_style():
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        fig, ax = plt.subplots()
        for i, condition in enumerate(conditions):
            runs = data.loc[data["condition"] == condition].sort_values("run")
            # Deterministic horizontal offsets aid visibility only; no values removed.
            offsets = np.linspace(-0.16, 0.16, len(runs)) if len(runs) > 1 else [0]
            style_index = group_index[condition]
            color = colors[style_index % len(colors)]
            ax.scatter(i + np.asarray(offsets), runs["value"],
                       s=plt.rcParams["lines.markersize"] ** 2,
                       marker=MARKERS[style_index % len(MARKERS)], facecolors="none",
                       edgecolors=color, linewidths=plt.rcParams["lines.markeredgewidth"])
            row = summary.loc[condition]
            if row["count"] > 0:
                # Put the summary beside observations so bars do not cross hollow points.
                ax.plot(i + 0.26, row["mean"], marker="_", markersize=MARK_PT["mean"], color=color)
            if row["count"] > 1:
                ax.errorbar(i + 0.26, row["mean"], yerr=row["std"], color=color, ecolor=color,
                            capsize=MARK_PT["cap"], fmt="none",
                            elinewidth=plt.rcParams["lines.markeredgewidth"],
                            capthick=plt.rcParams["lines.markeredgewidth"], marker_gap=False)
        has_missing = bool((summary["count"] < summary["size"]).any())
        labels = [f"{c}\nn={int(summary.loc[c, 'count'])}" +
                  (f"/{int(summary.loc[c, 'size'])}" if has_missing else "") for c in conditions]
        ax.set(xticks=range(len(conditions)), xticklabels=labels,
               xlabel=args.xlabel, ylabel=args.ylabel, xlim=(-0.5, len(conditions) - 0.5))
        note = "Markers: runs; dash: mean ± sample SD"
        if has_missing:
            note += "\nn = measured/supplied"
        if (summary["count"] < 2).any():
            note += "; SD undefined if n < 2" if has_missing else "\nSD undefined if n < 2"
        fig.text(0.5, LAYOUT["note_y"], note, ha="center", fontsize=FONT_PT["note"])
        fig.tight_layout(rect=(0, LAYOUT["note_top"], 1, 1), pad=LAYOUT["pad"])
        save_pdf(fig, args.output)
        plt.close(fig)


if __name__ == "__main__":
    main()
