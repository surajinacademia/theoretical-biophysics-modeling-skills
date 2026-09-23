"""Original synthetic teaching example; render its sibling data.csv to PDF."""

import argparse
from pathlib import Path
import sys
import subprocess

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "figure.pdf")
    args = parser.parse_args()
    if args.output.suffix.lower() != ".pdf":
        parser.error("output must end in .pdf")
    if any(p.is_symlink() for p in (args.output, *args.output.parents)):
        parser.error("output paths must not contain symlinks")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    template = ROOT.parents[1] / "templates" / "parameter_map.py"
    subprocess.run([sys.executable, str(template), str(ROOT / "data.csv"),
                    str(args.output), *['--xlabel', 'Adhesion (dimensionless)', '--ylabel', 'Noise (dimensionless)', '--colorbar-label', 'Order (dimensionless)']], check=True)


if __name__ == "__main__":
    main()
