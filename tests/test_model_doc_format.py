"""Focused behavior tests for the read-only model-document format checker."""

from __future__ import annotations

import importlib.util
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
CHECKER_PATH = (
    REPOSITORY_ROOT / "skills" / "model-documentation" / "scripts" / "check_model_doc.py"
)
TEMPLATE_PATH = (
    REPOSITORY_ROOT
    / "skills"
    / "model-documentation"
    / "references"
    / "model-document-template.md"
)
SPEC = importlib.util.spec_from_file_location("model_document_format_checker", CHECKER_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load check_model_doc.py")
CHECKER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = CHECKER
SPEC.loader.exec_module(CHECKER)


def make_document(header: str, empty_heading: str | None = None) -> str:
    """Build the fixed skeleton with short nonempty bodies for all leaves."""

    headings = (
        (2, "1. Model Purpose And Questions"),
        (2, "2. Physical Picture And Assumptions"),
        (2, "3. Entities, Domain, And Notation"),
        (2, "4. Parameters And Scales"),
        (2, "5. Governing Equations"),
        (2, "6. Initial And Boundary Conditions"),
        (2, "7. Observables And Model Tests"),
        (2, "8. Solution Method"),
        (3, "8.1. Methodology And Rationale"),
        (3, "8.2. Numerical Formulation"),
        (3, "8.3. Algorithm And Flowchart"),
        (3, "8.4. Accuracy And Verification"),
        (2, "9. Model Record And Implementation"),
        (3, "9.1. Implementation Mapping"),
        (3, "9.2. Method Decisions And Changes"),
        (3, "9.3. References"),
    )
    leaves = {
        *headings[:7],
        *headings[8:12],
        *headings[13:],
    }
    lines = ["# Example Relaxation Model", "", header, ""]
    for level, title in headings:
        lines.extend([f"{'#' * level} {title}", ""])
        if (level, title) in leaves and title != empty_heading:
            lines.extend([f"Body for {title}.", ""])
    return "\n".join(lines)


class ModelDocumentFormatTests(unittest.TestCase):
    def make_root(self, directory: Path) -> tuple[Path, Path]:
        root = (directory / "repository").resolve()
        (root / "docs").mkdir(parents=True)
        document = root / "docs" / "model.md"
        return root, document

    def run_checker(self, root: Path, document: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(CHECKER_PATH),
                str(document),
                "--root",
                str(root),
            ],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
        )

    def write_implemented(self, root: Path, document: Path, text: str | None = None) -> None:
        source = root / "src" / "solver.R"
        source.parent.mkdir(exist_ok=True)
        source.write_text("# source is never executed by this checker\n", encoding="utf-8")
        document.write_text(
            text
            or make_document("**Implementation:** [`solver.R`](../src/solver.R)"),
            encoding="utf-8",
        )

    def test_valid_implemented_document_accepts_non_python_source_and_stdout_only(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            self.write_implemented(root, document)

            result = self.run_checker(root, document)

            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("format only; not scientific validation", result.stdout)
            self.assertEqual(result.stderr, "")

    def test_valid_proposed_document_accepts_contained_markdown_plan(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            plan = root / "plans" / "approved.md"
            plan.parent.mkdir()
            plan.write_text("# Approved plan\n", encoding="utf-8")
            document.write_text(
                make_document(
                    "Implementation: Not implemented; plan: [source plan](../plans/approved.md)."
                ),
                encoding="utf-8",
            )

            result = self.run_checker(root, document)

            self.assertEqual(result.returncode, 0, result.stdout)

    def test_valid_proposed_document_accepts_conversation_only_plan_header(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            document.write_text(
                make_document(
                    "Implementation: Not implemented; source: user-approved plan in this conversation."
                ),
                encoding="utf-8",
            )

            result = self.run_checker(root, document)

            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertFalse((root / "plans").exists())

    def test_angle_bracketed_local_target_with_spaces_is_accepted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            for parent, target in (
                (root, "../model files/source.py"),
                (document.parent, "model files/source.py"),
            ):
                with self.subTest(target=target):
                    source = parent / "model files" / "source.py"
                    source.parent.mkdir()
                    source.write_text("source\n", encoding="utf-8")
                    document.write_text(
                        make_document(f"Implementation: [source](<{target}>)"),
                        encoding="utf-8",
                    )
                    result = self.run_checker(root, document)
                    self.assertEqual(result.returncode, 0, result.stdout)

    def test_worked_example_passes_without_modification(self):
        document = (
            REPOSITORY_ROOT
            / "skills"
            / "model-documentation"
            / "examples"
            / "overdamped-harmonic-oscillator"
            / "model.md"
        )

        result = self.run_checker(REPOSITORY_ROOT, document)

        self.assertEqual(result.returncode, 0, result.stdout)

    def test_template_fixed_skeleton_matches_checker_headings(self):
        template = TEMPLATE_PATH.read_text(encoding="utf-8")
        skeleton = re.search(
            r"^```markdown[ \t]*\n(?P<body>.*?)^```[ \t]*$",
            template,
            re.MULTILINE | re.DOTALL,
        )
        self.assertIsNotNone(skeleton)
        assert skeleton is not None
        parsed = CHECKER.parse_markdown(skeleton.group("body"))
        headings = [
            (heading.level, heading.text)
            for heading in parsed.headings
            if heading.level in (2, 3)
        ]

        self.assertEqual(headings, list(CHECKER.EXPECTED_HEADINGS))

    def test_extra_reordered_duplicate_and_missing_headings_fail(self):
        cases = {
            "extra": lambda text: text.replace(
                "## 2. Physical Picture And Assumptions",
                "## Extra Section\n\nBody.\n\n## 2. Physical Picture And Assumptions",
                1,
            ),
            "reordered": lambda text: text.replace(
                "## 1. Model Purpose And Questions", "## TEMPORARY HEADING", 1
            )
            .replace(
                "## 2. Physical Picture And Assumptions",
                "## 1. Model Purpose And Questions",
                1,
            )
            .replace("## TEMPORARY HEADING", "## 2. Physical Picture And Assumptions", 1),
            "duplicate": lambda text: text.replace(
                "## 3. Entities, Domain, And Notation",
                "## 3. Entities, Domain, And Notation\n\nBody.\n\n## 3. Entities, Domain, And Notation",
                1,
            ),
            "missing": lambda text: text.replace(
                "### 8.4. Accuracy And Verification\n\nBody for 8.4. Accuracy And Verification.\n\n",
                "",
                1,
            ),
        }
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            for name, transform in cases.items():
                with self.subTest(case=name):
                    self.write_implemented(root, document, transform(make_document("Implementation: [source](../src/solver.R)")))
                    result = self.run_checker(root, document)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("heading", result.stdout.lower())

    def test_setext_extra_heading_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            text = make_document("Implementation: [source](../src/solver.R)").replace(
                "Body for 1. Model Purpose And Questions.",
                "Body for 1. Model Purpose And Questions.\n\n"
                "Extra Evaluation Section\n------------------------\n\nUnexpected material.",
                1,
            )
            self.write_implemented(root, document, text)

            result = self.run_checker(root, document)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("unexpected heading: ## Extra Evaluation Section", result.stdout)

    def test_html_comments_do_not_create_headings_or_leaf_content(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            valid = make_document("Implementation: [source](../src/solver.R)").replace(
                "Body for 1. Model Purpose And Questions.",
                "Visible body <!-- ## Inline Fake Heading --> after the comment.\n\n"
                "<!--\n## Multiline Fake Heading\n-->",
                1,
            )
            self.write_implemented(root, document, valid)
            self.assertEqual(self.run_checker(root, document).returncode, 0)

            hidden_required = valid.replace(
                "## 1. Model Purpose And Questions",
                "<!--\n## 1. Model Purpose And Questions",
                1,
            ) + "-->\n"
            self.write_implemented(root, document, hidden_required)
            required_result = self.run_checker(root, document)
            self.assertNotEqual(required_result.returncode, 0)
            self.assertIn("missing required heading", required_result.stdout)

            comment_only = make_document("Implementation: [source](../src/solver.R)").replace(
                "Body for 5. Governing Equations.",
                "<!-- No visible section content -->",
                1,
            )
            self.write_implemented(root, document, comment_only)
            leaf_result = self.run_checker(root, document)
            self.assertNotEqual(leaf_result.returncode, 0)
            self.assertIn("empty leaf section: 5. Governing Equations", leaf_result.stdout)

    def test_comment_and_setext_syntax_inside_code_and_math_is_not_structure(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            text = make_document("Implementation: [source](../src/solver.R)").replace(
                "Body for 1. Model Purpose And Questions.",
                "```markdown <!-- fenced text\nFenced Fake Heading\n-------------------\n```\n\n"
                "$$\n<!--\nMath Fake Heading\n-----------------\n$$",
                1,
            )
            self.write_implemented(root, document, text)

            result = self.run_checker(root, document)

            self.assertEqual(result.returncode, 0, result.stdout)

    def test_inline_code_and_same_line_math_do_not_open_html_comments(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            contexts = {
                "inline-code": "The literal `<!--` remains inline code.",
                "same-line-display-math": "$$x + <!-- literal display-math text$$",
            }
            for name, body in contexts.items():
                with self.subTest(context=name):
                    text = make_document("Implementation: [source](../src/solver.R)").replace(
                        "Body for 1. Model Purpose And Questions.", body, 1
                    )
                    self.write_implemented(root, document, text)

                    result = self.run_checker(root, document)

                    self.assertEqual(result.returncode, 0, result.stdout)

    def test_unmatched_backtick_is_literal_and_does_not_hide_headings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            text = make_document("Implementation: [source](../src/solver.R)").replace(
                "Body for 1. Model Purpose And Questions.",
                "An unmatched ` remains ordinary body text.",
                1,
            )
            self.write_implemented(root, document, text)

            result = self.run_checker(root, document)

            self.assertEqual(result.returncode, 0, result.stdout)

    def test_thematic_break_only_leaf_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            for thematic_break in ("---", "***", "___"):
                with self.subTest(thematic_break=thematic_break):
                    text = make_document("Implementation: [source](../src/solver.R)").replace(
                        "Body for 5. Governing Equations.", thematic_break, 1
                    )
                    self.write_implemented(root, document, text)

                    result = self.run_checker(root, document)

                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("empty leaf section: 5. Governing Equations", result.stdout)

    def test_empty_leaf_section_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            self.write_implemented(
                root,
                document,
                make_document(
                    "Implementation: [source](../src/solver.R)",
                    empty_heading="5. Governing Equations",
                ),
            )

            result = self.run_checker(root, document)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("empty leaf section: 5. Governing Equations", result.stdout)

    def test_fenced_fake_headings_are_ignored(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            text = make_document("Implementation: [source](../src/solver.R)")
            text = text.replace(
                "Body for 1. Model Purpose And Questions.",
                "Body for 1. Model Purpose And Questions.\n\n"
                "```mermaid\n## Fake H2\n### Fake H3\n#### Fake H4\n```",
                1,
            )
            self.write_implemented(root, document, text)

            result = self.run_checker(root, document)

            self.assertEqual(result.returncode, 0, result.stdout)

    def test_invalid_source_links_fail(self):
        cases = {
            "remote": "Implementation: [source](https://example.invalid/model.R)",
            "missing": "Implementation: [source](../src/missing.R)",
            "directory": "Implementation: [source](../src)",
            "malformed": "Implementation: source",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            self.write_implemented(root, document)
            for name, header in cases.items():
                with self.subTest(case=name):
                    document.write_text(make_document(header), encoding="utf-8")
                    result = self.run_checker(root, document)
                    self.assertNotEqual(result.returncode, 0)

    def test_document_and_source_path_escapes_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            root, document = self.make_root(base)
            outside = base / "outside.md"
            outside.write_text(make_document("Implementation: [source](model.R)"), encoding="utf-8")

            document_result = self.run_checker(root, outside)
            self.assertNotEqual(document_result.returncode, 0)
            self.assertIn("document path escapes the repository root", document_result.stdout)

            self.write_implemented(
                root,
                document,
                make_document("Implementation: [source](../../outside.R)"),
            )
            source_result = self.run_checker(root, document)
            self.assertNotEqual(source_result.returncode, 0)
            self.assertIn("implementation source link escapes the repository root", source_result.stdout)

    def test_nonresolving_raw_path_before_parent_segment_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            self.write_implemented(
                root,
                document,
                make_document("Implementation: [source](../missing/../src/solver.R)"),
            )

            result = self.run_checker(root, document)

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("implementation source link does not resolve", result.stdout)

    def test_source_document_and_ancestor_symlinks_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            root, document = self.make_root(base)
            external_source = base / "external-source.R"
            external_source.write_text("external\n", encoding="utf-8")
            external_docs = base / "external-docs"
            external_docs.mkdir()
            external_document = external_docs / "model.md"
            external_document.write_text(make_document("Implementation: [source](../src/solver.R)"), encoding="utf-8")
            external_source_dir = base / "external-source-dir"
            external_source_dir.mkdir()
            (external_source_dir / "solver.R").write_text("external\n", encoding="utf-8")
            try:
                os.symlink(external_source, root / "src-link.R")
                os.symlink(external_document, document)
            except (NotImplementedError, OSError) as error:
                self.skipTest(f"symlinks unavailable: {error}")

            document_link_result = self.run_checker(root, document)
            self.assertNotEqual(document_link_result.returncode, 0)
            self.assertIn("symlink", document_link_result.stdout)

            document.unlink()
            (root / "docs").rmdir()
            os.symlink(external_docs, root / "docs")
            document_ancestor_result = self.run_checker(root, root / "docs" / "model.md")
            self.assertNotEqual(document_ancestor_result.returncode, 0)
            self.assertIn("symlink", document_ancestor_result.stdout)

            (root / "docs").unlink()
            (root / "docs").mkdir()
            source_document = root / "docs" / "model.md"
            source_document.write_text(
                make_document("Implementation: [source](../src-link.R)"), encoding="utf-8"
            )
            source_link_result = self.run_checker(root, source_document)
            self.assertNotEqual(source_link_result.returncode, 0)
            self.assertIn("symlink", source_link_result.stdout)

            (root / "src-link.R").unlink()
            os.symlink(external_source_dir, root / "src")
            source_document.write_text(
                make_document("Implementation: [source](../src/solver.R)"), encoding="utf-8"
            )
            source_ancestor_result = self.run_checker(root, source_document)
            self.assertNotEqual(source_ancestor_result.returncode, 0)
            self.assertIn("symlink", source_ancestor_result.stdout)

            root_alias = base / "repository-alias"
            os.symlink(root, root_alias)
            root_alias_result = self.run_checker(
                root_alias, root_alias / "docs" / "model.md"
            )
            self.assertNotEqual(root_alias_result.returncode, 0)
            self.assertIn("symlink", root_alias_result.stdout)

    def test_template_placeholders_fail_without_rejecting_math_inequalities(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            valid_math = make_document("Implementation: [source](../src/solver.R)").replace(
                "Body for 5. Governing Equations.",
                "The relation $a < b > c$ is stated here.",
                1,
            )
            self.write_implemented(root, document, valid_math)
            self.assertEqual(self.run_checker(root, document).returncode, 0)

            document.write_text(
                valid_math.replace("# Example Relaxation Model", "# <Model Name>", 1),
                encoding="utf-8",
            )
            self.assertNotEqual(self.run_checker(root, document).returncode, 0)

            document.write_text(
                valid_math.replace("Body for 1. Model Purpose And Questions.", "<...>", 1),
                encoding="utf-8",
            )
            self.assertNotEqual(self.run_checker(root, document).returncode, 0)

    def test_administrative_title_prefixes_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            for title in (
                "Canonical Model",
                "Canonical Model Docs: Example",
                "Canonical Model Documentation: Example",
                "Model Docs: Example",
                "Model Documentation: Example",
            ):
                with self.subTest(title=title):
                    self.write_implemented(
                        root,
                        document,
                        make_document("Implementation: [source](../src/solver.R)").replace(
                            "# Example Relaxation Model", f"# {title}", 1
                        ),
                    )
                    result = self.run_checker(root, document)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("administrative", result.stdout)

    def test_unbalanced_fence_and_display_math_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            for name, addition in {
                "fence": "\n```text\nunclosed\n",
                "math": "\n$$\nx = y\n",
            }.items():
                with self.subTest(case=name):
                    self.write_implemented(
                        root,
                        document,
                        make_document("Implementation: [source](../src/solver.R)") + addition,
                    )
                    result = self.run_checker(root, document)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn("unclosed", result.stdout)

    def test_checker_has_no_side_effects_and_never_executes_linked_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root, document = self.make_root(Path(temporary).resolve())
            source = root / "src" / "solver.py"
            source.parent.mkdir()
            source.write_text(
                "from pathlib import Path\nPath('executed.txt').write_text('ran')\n",
                encoding="utf-8",
            )
            document.write_text(
                make_document("Implementation: [source](../src/solver.py)"), encoding="utf-8"
            )
            before = {
                path.relative_to(root): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }

            result = self.run_checker(root, document)
            after = {
                path.relative_to(root): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }

            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertEqual(after, before)
            self.assertFalse((root / "executed.txt").exists())


if __name__ == "__main__":
    unittest.main()
