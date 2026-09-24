"""Build one maintained example from source using the current Minimalist profile.

Run with the owner's compatible Python environment. Temporary TeX support and
hybrid panels are rebuilt on every invocation, never read from archived renders.
"""
from pathlib import Path
import argparse
import subprocess
import sys
import tempfile

from vector_output import prepare_output_directory

SKILL = Path(__file__).resolve().parents[1]
EXAMPLES = SKILL / "assets" / "examples"
IMPORTED_TIKZ_CASES = (
    "behavioral-timescale-buckets", "dome", "epc-flow-charts", "global-nodes",
    "lab-curriculum-flow", "mesif", "model-physics",
    "optimization-decision-flowchart", "orbital-elements-3d-trajectory",
    "polarizing-microscope", "secant-regression-geometry",
    "seismic-focal-mechanism-in-3d-view", "spherical-and-cartesian-grids",
    "swan-wave-model", "tkz-linknodes-examples", "tkz-orm-example",
    "transmission-electron-microscope",
)
TIKZ_CASES = (*IMPORTED_TIKZ_CASES, "learning-dynamics", "chemoattraction")
CASES = ("activator-inhibitor", "collective-cell-model-classes",
         "learning-dynamics", "learning-tikz", "chemoattraction",
         *(f"tikz-{slug}" for slug in IMPORTED_TIKZ_CASES))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=CASES)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    output = prepare_output_directory(args.output_dir)

    def run(script, *options, **kwargs):
        return subprocess.run([sys.executable, str(script), *map(str, options)],
                              check=True, **kwargs)

    gallery_slug = args.case.removeprefix("tikz-") if args.case.startswith("tikz-") else None
    if not gallery_slug and args.case not in {"learning-tikz", "chemoattraction"}:
        run(EXAMPLES / "matplotlib" / args.case / "matplotlib-figure.py", "--output-dir", output)
        return

    with tempfile.TemporaryDirectory(prefix="schematic-example-") as temporary:
        work = Path(temporary).resolve()
        profile = work / "minimalist-profile.sty"
        with profile.open("w") as stream:
            run(SKILL / "assets/styles/minimalist_profile.py", "--tikz", stdout=stream)
        includes = [profile]
        if gallery_slug:
            source = EXAMPLES / "tikz" / gallery_slug / "source.tex"
            basename = "figure"
        elif args.case == "learning-tikz":
            source = EXAMPLES / "tikz/learning-dynamics/source.tex"
            includes.append(SKILL / "assets/styles/tikz/learning-dynamics-2406.sty")
            basename = "learning-dynamics-tikz"
        else:
            source = EXAMPLES / "tikz/chemoattraction/tikz-compositor.tex"
            includes.append(SKILL / "assets/styles/tikz/scientific-neutral.sty")
            panels = work / "panels"
            run(EXAMPLES / "matplotlib/chemoattraction/matplotlib-panels.py", "--panel-dir", panels)
            includes.extend(panels / f"{name}.pdf" for name in
                            ("field-profile", "concentration-map", "simulation-summary", "phase-diagram"))
            basename = "chemoattraction-hybrid"
        options = [source, "--engine", "lualatex", "--basename", basename,
                   "--output-dir", output]
        for path in includes:
            options.extend(["--include", path])
        run(SKILL / "scripts/render_tikz.py", *options)


if __name__ == "__main__":
    main()
