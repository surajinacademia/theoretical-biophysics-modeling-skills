"""Render eight original quantitative examples and assemble their PDF gallery.

Each assets/examples/<case>/ contains source.py, data.csv, and figure.pdf.
The default overview is assets/gallery.pdf.
Use --output-dir to render elsewhere; all outputs remain PDFs.
Plotting uses Matplotlib (optionally the owner minimalist theme), NumPy and
Pandas; assembling the gallery additionally needs ReportLab and pypdf. No
package installation, TeX engine, or network is used by this script.
"""

import argparse
from io import BytesIO
from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap

import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties, findfont


ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "assets" / "examples"
sys.path.insert(0, str(ROOT / "assets" / "styles"))
from publication import paper_style
from pdf_output import pdf_output

CASES = [
    ("timecourse", "Time courses", "Follow a quantity through time.",
     "Each hollow marker is the equal-run mean of six saved run values. Capped error bars show sample SD, not a confidence interval.",
     "All point markers use the same size and light outline. Error bars and legend text match their condition's color; there is no shaded band.",
     "Do not bridge an unmeasured time point or count individual cells as independent runs."),
    ("replicate-comparison", "Replicate comparisons", "Show variation before summarizing it.",
     "Each hollow point is one run. Beside the points, a horizontal mark is the equal-run mean and whiskers show sample SD. n counts measured runs.",
     "Modest horizontal offsets separate observations without altering their values. Shape reinforces condition identity.",
     "Use a point comparison for a focused scale; do not imply differences through truncated bar lengths."),
    ("paired-change", "Paired changes", "Keep the same run connected.",
     "Each line connects two values belonging to one run. All six pairs are shown, including the run whose value falls.",
     "Neutral connectors carry pairing. Two restrained endpoint colors show measurement state; no fitted trend is added.",
     "Pair by the run key. Never connect independently sorted arrays or silently drop unmatched runs."),
    ("distribution", "Distributions", "Count observations in clear, shared bins.",
     "Bar heights count runs in common five-minute bins; n=36 per condition. Control is the left bar and Perturbed the right bar in each pair.",
     "Separate bars use solid group-color fills with clear boundaries and small gaps. Legend text matches each bar's color.",
     "Use the same bin edges and zero baseline for both groups. Keep every value, including tails; do not confuse counts with probability density."),
    ("scatter", "Relationships", "Show paired observables directly.",
     "Each point contains area and speed from the same run; there are 18 runs per condition. No fitted line or inferential statistic is implied.",
     "Hollow markers share the same size and light outline as the other plots. Shape and matching legend text identify condition; units name both coordinates.",
     "Align both measurements by scientific identity. Equal array lengths do not establish pairing."),
    ("parameter-map", "Parameter maps", "Keep coordinates and missingness visible.",
     "Each measured parameter pair supplies one descriptive order value. Unequal coordinate spacing is retained. Gray and a cross mark one missing value.",
     "The package's sequential colormap encodes magnitude. Display-cell boundaries are midpoints between sampled coordinates.",
     "Cells summarize sampled values, not a continuous interpolated phase diagram. Missing is not zero."),
    ("continuous-field", "Continuous functions", "Render a continuous field smoothly.",
     "An original analytic function is evaluated on a dense 201 by 101 grid. Its signed color scale is centered on zero and fixed to [-1, 1].",
     "Bilinear image rendering follows the minimalist example. The field stays continuous without cell outlines or a grid of numeric labels.",
     "Smooth display is appropriate for this known continuous function. Do not smooth sparse parameter samples or interpolate across missing observations."),
    ("metric-comparison", "Related metrics", "Keep units separate and conditions consistent.",
     "Two metrics use the same six runs per condition. Hollow points are run values; matching-color marks and whiskers beside them show mean and sample SD.",
     "Aligned panels repeat the same condition colors and markers. Each metric retains its own labeled scale and units.",
     "Do not use a dual axis to imply a relationship or merge quantities with different units into one scale."),
]


def assemble_gallery(figure_pdfs):
    from pypdf import PdfReader, PdfWriter, Transformation
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen.canvas import Canvas

    with paper_style():
        family = plt.rcParams["font.family"]
        ink, muted = plt.rcParams["text.color"], plt.rcParams["axes.edgecolor"]
        accent = plt.rcParams["axes.prop_cycle"].by_key()["color"][0]
        pdfmetrics.registerFont(TTFont("House", findfont(FontProperties(family=family))))
        # CMU's actual bold face is catalogued with expanded stretch; the default
        # stretch can resolve to Medium even when weight="bold" is requested.
        pdfmetrics.registerFont(TTFont("HouseBold", findfont(
            FontProperties(family=family, weight="bold", stretch="expanded"))))
    width, height = landscape(A4)
    writer = PdfWriter()
    figures = [PdfReader(BytesIO(pdf)).pages[0] for pdf in figure_pdfs]

    def text(canvas, x, y, value, size=10, color=ink, bold=False):
        canvas.setFillColor(color)
        canvas.setFont("HouseBold" if bold else "House", size)
        canvas.drawString(x, y, value)

    def paragraph(canvas, x, y, value):
        for line in textwrap.wrap(value, 38):
            text(canvas, x, y, line)
            y -= 15
        return y

    # A square overview accommodates three rows at native size. The double-width
    # eighth example spans two columns instead of shrinking into a single tile.
    overview_height = width
    compact_width = float(figures[0].mediabox.width)
    gutter = 20
    left = (width - 3 * compact_width - 2 * gutter) / 2
    overview_positions = []
    for i, figure in enumerate(figures):
        col, row = i % 3, i // 3
        span = 2 if i == 7 else 1
        source_width = float(figure.mediabox.width)
        slot_width = span * compact_width + (span - 1) * gutter
        x = left + col * (compact_width + gutter) + (slot_width - source_width) / 2
        overview_positions.append((x, overview_height - 331 - row * 233))
    memory = BytesIO()
    c = Canvas(memory, pagesize=(width, overview_height))
    text(c, 34, overview_height - 29, "DATA VISUALIZATION  /  MINIMAL SCIENTIFIC STYLE", 8, muted)
    text(c, 34, overview_height - 61, "Quantitative plots, with restraint.", 23, bold=True)
    text(c, 34, overview_height - 81, "Eight original examples · consistent font sizes · PDF review gallery", 10, muted)
    for i, (case, (x, y)) in enumerate(zip(CASES, overview_positions)):
        text(c, x + 3, y + 215, f"{i + 1:02d}  {case[1]}", 9, "black", True)
    text(c, 34, 23, "Synthetic teaching data · all plots placed at native size, including the wider two-panel figure.", 8, muted)
    c.save()
    overview = PdfReader(memory).pages[0]
    for figure, (x, y) in zip(figures, overview_positions):
        overview.merge_transformed_page(figure, Transformation().translate(x, y))
    writer.add_page(overview)

    for i, (case, figure) in enumerate(zip(CASES, figures)):
        stem, title, question, meaning, design, pitfall = case
        source = f"assets/examples/{stem}/source.py"
        data = f"assets/examples/{stem}/data.csv"
        memory = BytesIO()
        c = Canvas(memory, pagesize=(width, height))
        text(c, 34, height - 29, f"DATA VISUALIZATION  /  {i + 1:02d} OF 08", 8, muted)
        text(c, 34, height - 66, title, 23, bold=True)
        text(c, 34, height - 90, question, 12, muted)
        y = height - 148
        for label, body in [("READ THE DATA", meaning), ("DESIGN DECISION", design), ("KEEP THE SCIENCE", pitfall)]:
            text(c, 564, y, label, 8, accent, True)
            y = paragraph(c, 564, y - 20, body) - 24
        text(c, 34, 83, "SOURCE", 7, muted, True)
        text(c, 34, 66, source, 8)
        text(c, 34, 48, f"Teaching table: {data}", 8)
        text(c, 34, 23, "SYNTHETIC DATA · Design specimen, not a scientific result", 8, muted)
        text(c, width - 64, 23, f"{i + 2:02d}", 8, muted)
        c.save()
        page = PdfReader(memory).pages[0]
        # The figure is placed at its saved physical size, centered in the left column.
        w = float(figure.mediabox.width)
        page.merge_transformed_page(figure, Transformation().translate(34 + (496 - w) / 2, 186))
        writer.add_page(page)
    writer.add_metadata({"/Title": "Quantitative plots, with restraint", "/Author": "Local data-visualization skill",
                         "/Subject": "Original synthetic teaching examples for visual review"})
    memory = BytesIO()
    writer.write(memory)
    return memory.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "assets")
    args = parser.parse_args()
    output = args.output_dir
    for path in [output, output / "gallery.pdf",
                 *(output / "examples" / case[0] / "figure.pdf" for case in CASES)]:
        if any(p.is_symlink() for p in (path, *path.parents)):
            parser.error("output paths must not contain symlinks")
    # The output tree may be shared and replaceable. Never reopen its published
    # PDFs as gallery inputs, even if they look like regular files. Build and
    # assemble everything in a fresh mode-0700 temporary directory first.
    with tempfile.TemporaryDirectory(prefix="data-gallery-") as temporary:
        staging = Path(temporary).resolve()
        figure_pdfs = []
        for case in CASES:
            figure = staging / f"{case[0]}.pdf"
            subprocess.run([sys.executable, str(EXAMPLES / case[0] / "source.py"),
                            "--output", str(figure)], check=True)
            figure_pdfs.append(figure.read_bytes())
        gallery_pdf = assemble_gallery(figure_pdfs)
        for case, contents in zip(CASES, figure_pdfs):
            with pdf_output(output / "examples" / case[0] / "figure.pdf",
                            create_parents=True) as stream:
                stream.write(contents)
        with pdf_output(output / "gallery.pdf", create_parents=True) as stream:
            stream.write(gallery_pdf)
    print(f"Rendered 8 example PDFs and {output / 'gallery.pdf'}")


if __name__ == "__main__":
    main()
