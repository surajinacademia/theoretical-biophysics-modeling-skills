"""Original synthetic teaching example; render its sibling data.csv to PDF."""

import argparse
from pathlib import Path
import sys
import subprocess

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parents[1] / "styles"))
from pdf_output import output_directory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "figure.pdf")
    args = parser.parse_args()
    if args.output.suffix.lower() != ".pdf":
        parser.error("output must end in .pdf")
    if any(p.is_symlink() for p in (args.output, *args.output.parents)):
        parser.error("output paths must not contain symlinks")
    with output_directory(args.output.parent, create=True):
        pass
    template = ROOT.parents[1] / "templates" / "timecourse.py"
    subprocess.run([sys.executable, str(template), str(ROOT / "data.csv"),
                    str(args.output), *['--group-order', 'Control', 'Perturbed', '--xlabel', 'Time (h)', '--ylabel', 'Front position (µm)']], check=True)


if __name__ == "__main__":
    main()
