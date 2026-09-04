"""Unit tests for the bounded model-document checker evaluation runner."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_PATH = REPOSITORY_ROOT / "evals" / "model-documentation" / "checker_eval.py"
SPEC = importlib.util.spec_from_file_location("model_document_checker_eval", EVALUATOR_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load checker_eval.py")
EVALUATOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = EVALUATOR
SPEC.loader.exec_module(EVALUATOR)
TEMPORARY_ROOT = Path(tempfile.gettempdir()).resolve()


EXPECTED_CASE_IDS = (
    "valid-implemented-local-source",
    "valid-planned-markdown-source",
    "valid-conversation-plan",
    "valid-angle-bracket-source-path",
    "extra-atx-heading-rejected",
    "setext-extra-heading-rejected",
    "h7-pseudo-heading-is-body",
    "html-commented-extra-heading-ignored",
    "html-block-commented-extra-heading-ignored",
    "html-commented-required-sections-rejected",
    "html-comment-only-leaf-rejected",
    "markup-only-leaf-rejected",
    "fenced-headings-ignored",
    "display-math-headings-ignored",
    "balanced-multiline-display-math-is-content",
    "unbalanced-multiline-display-math-rejected",
    "remote-source-link-rejected",
    "source-link-escape-rejected",
    "source-link-fragment-rejected",
    "missing-source-link-rejected",
    "source-link-directory-rejected",
    "planned-source-non-markdown-rejected",
    "wrong-physical-claim-is-manual-review-control",
    "alternate-local-source-is-provenance-control",
)


class ModelDocumentCheckerEvaluationTests(unittest.TestCase):
    def test_case_identity_and_explicit_scope_are_stable(self):
        cases = EVALUATOR.CASES

        self.assertEqual(tuple(case.id for case in cases), EXPECTED_CASE_IDS)
        self.assertGreaterEqual(len(cases), 15)
        self.assertLessEqual(len(cases), 25)
        self.assertEqual(len({case.id for case in cases}), len(cases))
        self.assertTrue(all(isinstance(case.expected_format_pass, bool) for case in cases))
        self.assertTrue(all(case.rationale for case in cases))
        self.assertEqual(
            next(
                case.scope
                for case in cases
                if case.id == "wrong-physical-claim-is-manual-review-control"
            ),
            "semantic-manual-review",
        )
        self.assertEqual(
            next(
                case.scope
                for case in cases
                if case.id == "alternate-local-source-is-provenance-control"
            ),
            "source-provenance-manual-review",
        )

    def test_evaluate_cases_reports_matches_and_mismatches_from_explicit_expectations(self):
        cases = (EVALUATOR.CASES[0], EVALUATOR.CASES[4])
        invocations: list[tuple[Path, Path, Path]] = []

        def passing_invoker(
            checker_path: Path, document: Path, root: Path
        ) -> subprocess.CompletedProcess[str]:
            invocations.append((checker_path, document, root))
            self.assertTrue(document.is_file())
            self.assertTrue(root.is_dir())
            return subprocess.CompletedProcess(
                args=["synthetic-checker"],
                returncode=0,
                stdout="Model-document format check passed: format only.\n",
                stderr="",
            )

        with tempfile.TemporaryDirectory(dir=TEMPORARY_ROOT) as temporary:
            report = EVALUATOR.evaluate_cases(
                cases=cases,
                checker_path=EVALUATOR_PATH,
                temporary_root=Path(temporary).resolve(),
                invoker=passing_invoker,
            )

        self.assertEqual(report["case_count"], 2)
        self.assertEqual(report["mismatch_count"], 1)
        self.assertEqual([entry["outcome"] for entry in report["cases"]], ["match", "mismatch"])
        self.assertEqual([entry["actual_pass"] for entry in report["cases"]], [True, True])
        self.assertEqual(len(invocations), 2)

    def test_invoke_checker_disables_bytecode_and_captures_output(self):
        with tempfile.TemporaryDirectory(dir=TEMPORARY_ROOT) as temporary:
            root = Path(temporary).resolve() / "repository"
            root.mkdir()
            document = root / "model.md"
            document.write_text("# Synthetic\n", encoding="utf-8")
            completed = subprocess.CompletedProcess(
                args=["synthetic-checker"], returncode=0, stdout="ok\n", stderr=""
            )

            with patch.object(EVALUATOR.subprocess, "run", return_value=completed) as run:
                result = EVALUATOR.invoke_checker(EVALUATOR_PATH, document, root)

        self.assertIs(result, completed)
        command = run.call_args.args[0]
        self.assertEqual(command[0:2], [sys.executable, "-B"])
        self.assertEqual(command[2], str(EVALUATOR_PATH))
        self.assertEqual(command[3:], [str(document), "--root", str(root)])
        self.assertEqual(run.call_args.kwargs["cwd"], root)
        self.assertFalse(run.call_args.kwargs["check"])
        self.assertTrue(run.call_args.kwargs["capture_output"])
        self.assertTrue(run.call_args.kwargs["text"])
        self.assertEqual(run.call_args.kwargs["timeout"], 15)

    def test_checker_crash_is_not_counted_as_expected_rejection(self):
        case = next(case for case in EVALUATOR.CASES if not case.expected_format_pass)
        crash = subprocess.CompletedProcess(args=[], returncode=1, stdout="", stderr="Traceback")
        report = EVALUATOR._case_report(case, crash)
        self.assertEqual(report["outcome"], "error")
        self.assertIsNone(report["actual_pass"])

    def test_timeout_is_recorded_as_an_error(self):
        def timeout(*args):
            raise subprocess.TimeoutExpired(cmd="checker", timeout=15)

        report = EVALUATOR.evaluate_cases(
            cases=(EVALUATOR.CASES[0],), invoker=timeout,
        )
        self.assertEqual(report["error_count"], 1)
        self.assertEqual(report["mismatch_count"], 0)
        self.assertEqual(report["cases"][0]["outcome"], "error")

    def test_main_prints_json_and_returns_nonzero_for_mismatches(self):
        expected_report = {
            "suite": "model-document-checker-adversarial-eval",
            "checker": "synthetic-checker",
            "temporary_parent": "/private/tmp",
            "case_count": 1,
            "mismatch_count": 1,
            "cases": [],
        }
        output = io.StringIO()

        with (
            patch.object(EVALUATOR, "evaluate_cases", return_value=expected_report),
            contextlib.redirect_stdout(output),
        ):
            status = EVALUATOR.main()

        self.assertEqual(status, 1)
        self.assertEqual(json.loads(output.getvalue()), expected_report)

    def test_selected_temporary_parent_is_within_an_allowed_temp_root(self):
        selected = EVALUATOR.temporary_parent()
        allowed = [TEMPORARY_ROOT]
        private_tmp = Path("/private/tmp")
        if private_tmp.exists():
            allowed.append(private_tmp.resolve())

        self.assertTrue(selected.is_dir())
        self.assertTrue(
            any(
                selected == root or root in selected.parents
                for root in allowed
            )
        )

    def test_main_fails_on_execution_error_without_decision_mismatches(self):
        with (
            patch.object(EVALUATOR, "evaluate_cases", return_value={"mismatch_count": 0, "error_count": 1}),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(EVALUATOR.main(), 1)


if __name__ == "__main__":
    unittest.main()
