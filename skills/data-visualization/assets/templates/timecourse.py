"""Plot one precomputed value per (condition, run, time).

CSV columns: condition,run,time,value. Blank values mean missing measurements.
The union of supplied times is the expected grid for every condition. Include
an explicit blank-value row for an expected time absent from every run.
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
from pdf_output import save_pdf
from publication import paper_style, FONT_PT, MARK_PT, LAYOUT, MARKERS, LINESTYLES


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--xlabel", default="Time (supply units)")
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
    keys = ["condition", "run", "time"]
    if not set(keys + ["value"]).issubset(data.columns) or data.empty:
        parser.error("input needs nonempty condition,run,time,value columns")
    if data[keys].isna().any().any() or data[keys].eq("").any().any():
        parser.error("condition, run, and time keys must not be missing")
    data["time"] = pd.to_numeric(data["time"], errors="raise")
    data["value"] = pd.to_numeric(data["value"], errors="raise")
    if not np.isfinite(data["time"]).all() or np.isinf(data["value"]).any():
        parser.error("times must be finite; values may be missing but not infinite")
    if data.duplicated(keys).any():
        parser.error("expected exactly one precomputed value per condition,run,time")

    # Each supplied run value has equal weight; SD uses ddof=1, never SEM.
    conditions = sorted(data["condition"].unique())
    group_order = args.group_order or conditions
    if len(group_order) != len(set(group_order)) or not set(conditions).issubset(group_order):
        parser.error("group-order must contain each observed condition exactly once, with no duplicates")
    group_index = {condition: i for i, condition in enumerate(group_order)}
    summary = data.groupby(["condition", "time"])["value"].agg(["mean", "std", "count"])
    times = np.sort(data["time"].unique())
    with paper_style():
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        fig, ax = plt.subplots()
        legend_handles = []
        undefined_sd = False
        for condition in conditions:
            values = summary.loc[condition].reindex(times)
            count = values["count"].fillna(0).astype(int)
            mean = values["mean"].to_numpy()
            sd = values["std"].to_numpy()
            style_index = group_index[condition]
            color = colors[style_index % len(colors)]
            n_label = str(count.min()) if count.min() == count.max() else f"{count.min()}–{count.max()}"
            label = f"{condition} (n={n_label})"
            undefined_sd |= bool((count < 2).any())
            # Keep the full grid for connecting lines, including explicit missing gaps.
            ax.plot(times, mean, color=color, label=label,
                    marker="", linestyle=LINESTYLES[style_index % len(LINESTYLES)])
            marker = MARKERS[style_index % len(MARKERS)]
            legend_handles.append(Line2D(
                [], [], color=color, marker=marker,
                linestyle=LINESTYLES[style_index % len(LINESTYLES)],
                markerfacecolor="none", label=label))
            # The package gap API requires finite marker positions and finite SD.
            # Singletons remain visible as separate hollow markers, without whiskers.
            measured_sd = np.isfinite(mean) & np.isfinite(sd)
            if measured_sd.any():
                ax.errorbar(times[measured_sd], mean[measured_sd], yerr=sd[measured_sd],
                            fmt=marker, linestyle="none", color=color, ecolor=color,
                            capsize=MARK_PT["cap"],
                            elinewidth=plt.rcParams["lines.markeredgewidth"],
                            capthick=plt.rcParams["lines.markeredgewidth"])
            singleton = np.isfinite(mean) & ~np.isfinite(sd)
            if singleton.any():
                ax.plot(times[singleton], mean[singleton], color=color,
                        marker=marker, linestyle="none")
        ax.set(xlabel=args.xlabel, ylabel=args.ylabel)
        ax.legend(handles=legend_handles, loc="best", labelcolor="linecolor")
        note = "Equal-run mean ± sample SD; n = runs/time"
        if undefined_sd:
            note += "\nSD undefined for n < 2"
        fig.text(0.5, LAYOUT["note_y"], note, ha="center", fontsize=FONT_PT["note"])
        fig.tight_layout(rect=(0, LAYOUT["note_top"], 1, 1), pad=LAYOUT["pad"])
        save_pdf(fig, args.output)  # Keep the physical canvas size; no tight crop.
        plt.close(fig)


if __name__ == "__main__":
    main()
