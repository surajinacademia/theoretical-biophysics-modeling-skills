"""Focused behavior checks for the bounded LSA LaTeX report checker."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = REPOSITORY_ROOT / "skills" / "linear-stability-analysis" / "scripts" / "check_lsa_report.py"
TEMPLATE_PATH = REPOSITORY_ROOT / "skills" / "linear-stability-analysis" / "assets" / "report-template.tex"
SPEC = importlib.util.spec_from_file_location("check_lsa_report", CHECKER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load LSA report checker")
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


def report_text(
    figure: str = "figures/dispersion_relation.pdf",
    *,
    include_in_section7: bool = True,
    title: str = "Example Linear Stability Analysis",
) -> str:
    lines = [r"\documentclass{article}", r"\usepackage{graphicx}", rf"\title{{{title}}}", r"\begin{document}", r"\maketitle"]
    for section in CHECKER.SECTIONS:
        lines.extend((rf"\section{{{section}}}", "Report content."))
        if section == CHECKER.SECTIONS[5] and not include_in_section7:
            lines.append(rf"\includegraphics{{{figure}}}")
        if section == CHECKER.SECTIONS[6] and include_in_section7:
            lines.append(rf"\includegraphics{{{figure}}}")
        for parent, subsection in CHECKER.SUBSECTIONS:
            if parent == section:
                lines.extend((rf"\subsection{{{subsection}}}", "Method content."))
    return "\n".join([*lines, r"\end{document}", ""])


class LsaReportCheckerTests(unittest.TestCase):
    def make_report(self, directory: Path, text: str | None = None, figure: str = "figures/dispersion_relation.pdf") -> tuple[Path, Path]:
        root = directory / "analysis"
        root.mkdir()
        figure_path = root / figure
        figure_path.parent.mkdir(parents=True, exist_ok=True)
        figure_path.write_bytes(b"fixture figure")
        report = root / "report.tex"
        report.write_text(text or report_text(figure), encoding="utf-8")
        return root, report

    def run_cli(self, root: Path, report: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(CHECKER_PATH), str(report), "--root", str(root)],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )

    def completed_template(self) -> str:
        text = TEMPLATE_PATH.read_text(encoding="utf-8")
        command = text.index(r"\IfFileExists{")
        first = CHECKER._argument(text, command + len(r"\IfFileExists"))
        self.assertIsNotNone(first)
        assert first is not None
        second = CHECKER._argument(text, first[1])
        self.assertIsNotNone(second)
        assert second is not None
        third = CHECKER._argument(text, second[1])
        self.assertIsNotNone(third)
        assert third is not None
        figure = r"\includegraphics[width=0.86\linewidth]{figures/dispersion_relation.pdf}"
        return text[:command] + figure + text[third[1] :]

    def test_valid_explicit_figure_and_cli(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, report = self.make_report(Path(temporary).resolve())
            self.assertEqual(CHECKER.validate_report(report, root), [])
            result = self.run_cli(root, report)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stderr, "")

    def test_bundled_template_scaffold_is_rejected_and_completed_form_passes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve() / "analysis"
            root.mkdir()
            report = root / "report.tex"
            report.write_text(TEMPLATE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
            figure = root / "figures" / "dispersion_relation.pdf"
            figure.parent.mkdir()
            figure.write_bytes(b"fixture figure")
            self.assertTrue(CHECKER.validate_report(report, root))
            report.write_text(self.completed_template(), encoding="utf-8")
            self.assertEqual(CHECKER.validate_report(report, root), [])

    def test_extension_inference_accepts_one_file_and_rejects_ambiguity_or_missing(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary).resolve()
            root, report = self.make_report(directory, report_text("figures/dispersion_relation"), "figures/dispersion_relation.png")
            self.assertEqual(CHECKER.validate_report(report, root), [])
            (root / "figures" / "dispersion_relation.pdf").write_bytes(b"another figure")
            self.assertTrue(CHECKER.validate_report(report, root))
            (root / "figures" / "dispersion_relation.pdf").unlink()
            (root / "figures" / "dispersion_relation.png").unlink()
            self.assertTrue(CHECKER.validate_report(report, root))
            (root / "figures" / "dispersion_relation.svg").write_bytes(b"unsupported")
            report.write_text(report_text("figures/dispersion_relation.svg"), encoding="utf-8")
            self.assertTrue(CHECKER.validate_report(report, root))

    def test_canonical_structure_rejects_starred_extra_reordered_and_numbered_titles(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, report = self.make_report(Path(temporary).resolve())
            valid = report.read_text(encoding="utf-8")
            first = r"\section{Model Purpose And Questions}"
            first_subsection = r"\subsection{Methodology And Rationale}" + "\nMethod content."
            section7 = r"\section{Observables And Model Tests}" + "\nReport content."
            wrong_parent = valid.replace(first_subsection, "", 1).replace(
                section7, section7 + "\n" + first_subsection, 1
            )
            cases = (
                valid.replace(first, r"\section*{Model Purpose And Questions}", 1),
                valid.replace(first, r"\\section{Model Purpose And Questions}", 1),
                valid.replace(first, first + "\n\\section{Unexpected}", 1),
                valid.replace(first, r"\section{1. Model Purpose And Questions}", 1),
                valid.replace(
                    r"\section{Physical Picture And Assumptions}", r"\section{TEMPORARY}", 1
                ).replace(
                    r"\section{Entities, Domain, And Notation}",
                    r"\section{Physical Picture And Assumptions}",
                    1,
                ).replace(r"\section{TEMPORARY}", r"\section{Entities, Domain, And Notation}", 1),
                wrong_parent,
            )
            for malformed in cases:
                with self.subTest(malformed=malformed[:40]):
                    report.write_text(malformed, encoding="utf-8")
                    self.assertTrue(CHECKER.validate_report(report, root))

    def test_comments_and_literal_listing_environments_do_not_supply_structure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, report = self.make_report(Path(temporary).resolve())
            text = report.read_text(encoding="utf-8").replace(
                r"\begin{document}",
                "\n".join(
                    (
                        r"\begin{document}",
                        r"% \section{Commented Extra}",
                        r"\begin{verbatim}",
                        r"\section{Quoted Extra}",
                        r"\includegraphics{../outside.pdf}",
                        r"\end{verbatim}",
                        r"\begin{lstlisting}",
                        r"\subsection{Quoted Extra}",
                        r"\end{lstlisting}",
                    )
                ),
                1,
            )
            report.write_text(text, encoding="utf-8")
            self.assertEqual(CHECKER.validate_report(report, root), [])
            report.write_text(text.replace(r"% \section{Commented Extra}", r"\% \section{Live Extra}"), encoding="utf-8")
            self.assertTrue(CHECKER.validate_report(report, root))

    def test_nested_math_environments_are_allowed(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, report = self.make_report(Path(temporary).resolve())
            text = report.read_text(encoding="utf-8").replace(
                "Report content.",
                r"\[\boxed{\begin{aligned}\lambda &= \sigma + i\omega\end{aligned}}\]",
                1,
            )
            report.write_text(text, encoding="utf-8")
            self.assertEqual(CHECKER.validate_report(report, root), [])

    def test_section7_requires_an_actual_figure_but_does_not_classify_plot_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, report = self.make_report(Path(temporary).resolve(), report_text(include_in_section7=False))
            self.assertTrue(CHECKER.validate_report(report, root))
            generic = "figures/figure.pdf"
            (root / generic).write_bytes(b"fixture figure")
            report.write_text(report_text(generic), encoding="utf-8")
            self.assertEqual(CHECKER.validate_report(report, root), [])

    def test_document_framing_and_unsupported_indirection_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, report = self.make_report(Path(temporary).resolve())
            valid = report.read_text(encoding="utf-8")
            section = r"\section{Model Purpose And Questions}"
            cases = (
                valid.replace(r"\end{document}", "", 1),
                valid.replace(r"\title{Example Linear Stability Analysis}", r"\title{}", 1),
                valid.replace(r"\maketitle", "", 1),
                valid.replace(r"\begin{document}", r"\input{other.tex}\n\begin{document}", 1),
                valid.replace(section, r"\newcommand{\FirstSection}{" + section + r"}\FirstSection", 1),
            )
            for malformed in cases:
                with self.subTest(malformed=malformed[:40]):
                    report.write_text(malformed, encoding="utf-8")
                    self.assertTrue(CHECKER.validate_report(report, root))

    def test_hidden_structure_conditionals_aliases_and_catcodes_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, report = self.make_report(Path(temporary).resolve())
            valid = report.read_text(encoding="utf-8")
            discarded = valid.replace(
                r"\begin{document}", r"\newcommand{\discard}[1]{}" + "\n" + r"\begin{document}", 1
            )
            for kind, title in CHECKER.EXPECTED:
                command = rf"\{kind}{{{title}}}"
                discarded = discarded.replace(command, rf"\discard{{{command}}}", 1)
            graphic = r"\includegraphics{figures/dispersion_relation.pdf}"
            discarded = discarded.replace(graphic, rf"\discard{{{graphic}}}", 1)
            conditional = valid.replace(r"\maketitle", r"\iffalse" + "\n" + r"\maketitle", 1).replace(
                r"\end{document}", r"\fi" + "\n" + r"\end{document}", 1
            )
            cases = (
                discarded,
                conditional,
                valid.replace(r"\begin{document}", r"\let\section\discard" + "\n" + r"\begin{document}", 1),
                valid.replace(r"\begin{document}", r"\catcode`\@=11" + "\n" + r"\begin{document}", 1),
            )
            for malformed in cases:
                with self.subTest(malformed=malformed[:60]):
                    report.write_text(malformed, encoding="utf-8")
                    self.assertTrue(CHECKER.validate_report(report, root))

    def test_report_escape_and_symlinked_figure_component_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary).resolve()
            root, report = self.make_report(directory)
            outside = directory / "outside.tex"
            outside.write_text(report.read_text(encoding="utf-8"), encoding="utf-8")
            self.assertTrue(CHECKER.validate_report(outside, root))
            external_figures = directory / "external-figures"
            external_figures.mkdir()
            (external_figures / "dispersion_relation.pdf").write_bytes(b"external")
            linked = root / "linked"
            try:
                os.symlink(external_figures, linked)
            except (NotImplementedError, OSError) as error:
                self.skipTest(f"symlinks unavailable: {error}")
            report.write_text(report_text("linked/dispersion_relation.pdf"), encoding="utf-8")
            self.assertTrue(CHECKER.validate_report(report, root))
            report_link = root / "report-link.tex"
            os.symlink(report, report_link)
            self.assertTrue(CHECKER.validate_report(report_link, root))
            root_link = directory / "analysis-link"
            os.symlink(root, root_link)
            self.assertTrue(CHECKER.validate_report(report, root_link))


if __name__ == "__main__":
    unittest.main()
