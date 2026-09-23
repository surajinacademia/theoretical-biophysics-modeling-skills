# VIGIL concept figure — Minimalist adaptation

Original creator: Chen Liu / figures4papers.

Source: [https://github.com/ChenLiu-1996/figures4papers/blob/3c181f85e82c6f24948fcaaf3be6696102b41d8d/figure_VIGIL/plot_concept.py](https://github.com/ChenLiu-1996/figures4papers/blob/3c181f85e82c6f24948fcaaf3be6696102b41d8d/figure_VIGIL/plot_concept.py)

Reference: [original figure](https://github.com/ChenLiu-1996/figures4papers/blob/3c181f85e82c6f24948fcaaf3be6696102b41d8d/figure_VIGIL/figures/concept.png).

Original material and this adaptation: [Creative Commons Attribution–NonCommercial 4.0 International](https://creativecommons.org/licenses/by-nc/4.0/). Full license retained in `LICENSE`. No endorsement by the original creator is implied.

Changes: owner's Minimalist palette, CMU typography and real LaTeX math, native TikZ arrowheads, shared physical style roles, a compact two-panel layout, line-pattern redundancy, and vector PDF/outlined-SVG exports. All 5,200 seeded cloud points, Gaussian constructions, KDE levels, trajectory samples, and checkpoint positions are retained from the original numerical construction. These are illustrative distributions/manifolds, not empirical embeddings or normalized probability densities. The original Probability axis and display-coordinate tick labels are preserved.

The source functions were inspected and adapted into `vigil_geometry.py`; the original plotting script was not executed. `build_figure.py` renders the computed base and writes the TikZ compositor. `panels.pdf` is an intermediate input; the final rendered pair is `vigil-minimalist.pdf` and `vigil-minimalist.svg`.

Run `build_figure.py --output-dir /approved/figure/directory` with the configured Python runtime. It creates declared intermediates beneath `source/` in that output directory and the final PDF/SVG pair at its root. The bundled shared Minimalist profile supplies colors and typography; no package or font is installed by the example.
