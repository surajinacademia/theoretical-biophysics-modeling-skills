"""Recreate the gallery's original, synthetic teaching tables; no simulation runs.

Run only to regenerate these fixtures. Values are invented for demonstrating
visual encodings and are not experimental observations or validated predictions.
"""

from pathlib import Path

import numpy as np
import pandas as pd


def main():
    output = Path(__file__).resolve().parent.parent / "assets" / "examples"
    if any(p.is_symlink() for p in (output, *output.parents)):
        raise ValueError("The teaching-data directory must not contain symlinks")
    output.mkdir(exist_ok=True)
    tables = {}
    records = []
    offsets = np.array([-2.5, -1.5, -0.5, 0.5, 1.5, 2.5])
    for condition in ["Control", "Perturbed"]:
        for run, offset in enumerate(offsets, start=1):
            for time in np.arange(0, 13, 2):
                mean = 10 + (2.2 * time if condition == "Control" else
                             32 * (1 - np.exp(-time / 5)))
                value = mean + offset * (0.6 + 0.04 * time)
                records.append((condition, f"{run:02d}", time, value))
    tables["timecourse"] = pd.DataFrame(records, columns=["condition", "run", "time", "value"])
    tables["replicate-comparison"] = pd.DataFrame([
        (condition, f"{run:02d}", value)
        for condition, values in [
            ("Control", [1.5, 1.8, 1.9, 2.0, 2.2, 2.6]),
            ("Perturbed", [1.9, 2.2, 2.4, 2.6, 2.7, 3.2])]
        for run, value in enumerate(values, start=1)
    ], columns=["condition", "run", "value"])
    before = np.array([1.5, 1.8, 1.9, 2.0, 2.2, 2.6])
    after = before + np.array([0.5, 0.3, -0.1, 0.8, 0.2, 0.6])
    tables["paired-change"] = pd.DataFrame([
        (f"{run:02d}", state, value)
        for run, (a, b) in enumerate(zip(before, after), start=1)
        for state, value in [("Before", a), ("After", b)]
    ], columns=["run", "state", "value"])
    rng = np.random.default_rng(20260921)
    tables["distribution"] = pd.DataFrame([
        (condition, f"{run:02d}", value)
        for condition, values in [
            ("Control", rng.lognormal(np.log(14), 0.28, 36)),
            ("Perturbed", rng.lognormal(np.log(20), 0.35, 36))]
        for run, value in enumerate(values, start=1)
    ], columns=["condition", "run", "value"])
    records = []
    for condition, gain in [("Control", 0.065), ("Perturbed", 0.09)]:
        for run, area in enumerate(np.linspace(12, 42, 18), start=1):
            records.append((condition, f"{run:02d}", area,
                            0.35 + gain * area + rng.normal(0, 0.13)))
    tables["scatter"] = pd.DataFrame(records, columns=["condition", "run", "area", "speed"])
    records = []
    for y in [0.5, 1.0, 2.0, 4.0]:
        for x in [0.1, 0.25, 0.5, 0.9, 1.4]:
            value = 0.85 * (1 - np.exp(-2 * x)) * np.exp(-y / 7)
            if (x, y) == (0.5, 2.0):
                value = np.nan
            records.append((x, y, value))
    tables["parameter-map"] = pd.DataFrame(records, columns=["x", "y", "value"])
    # Dense evaluation of an original continuous function, not interpolated
    # parameter measurements. The renderer can display this field smoothly.
    tables["continuous-field"] = pd.DataFrame([
        (x, y, np.tanh(2 * x) * (0.5 + 0.5 * np.cos(np.pi * y)))
        for y in np.linspace(0, 1, 101) for x in np.linspace(-1, 1, 201)
    ], columns=["x", "y", "value"])
    tables["metric-comparison"] = pd.DataFrame([
        (condition, f"{run:02d}", speed, order)
        for condition, speeds, orders in [
            ("Control", [1.5, 1.8, 1.9, 2.0, 2.2, 2.6], [.35, .40, .43, .48, .49, .55]),
            ("Perturbed", [1.9, 2.2, 2.4, 2.6, 2.7, 3.2], [.56, .60, .63, .66, .68, .73])]
        for run, (speed, order) in enumerate(zip(speeds, orders), start=1)
    ], columns=["condition", "run", "speed", "order"])
    for case, table in tables.items():
        target = output / case / "data.csv"
        if any(p.is_symlink() for p in (target, *target.parents)):
            raise ValueError(f"Refusing symlink: {target}")
        target.parent.mkdir(parents=True, exist_ok=True)
        table.to_csv(target, index=False, float_format="%.8g")


if __name__ == "__main__":
    main()
