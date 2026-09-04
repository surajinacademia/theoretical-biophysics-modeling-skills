#!/usr/bin/env python3
"""Run bounded adversarial format checks against the model-document checker.

This is an audit suite. It exercises only the checker's declared Markdown and
local-link contract; scientific correctness and primary-source identity remain
manual-review concerns.
"""

from __future__ import annotations

import json
import os
import stat
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Callable, Mapping, Sequence


REPOSITORY_ROOT = Path(__file__).parent.parent.parent
CHECKER_PATH = (
    REPOSITORY_ROOT
    / "skills"
    / "model-documentation"
    / "scripts"
    / "check_model_doc.py"
)
DOCUMENT_PATH = PurePosixPath("docs/model.md")
MAX_DOCUMENT_BYTES = 32 * 1024
MAX_FIXTURE_FILES = 4
MAX_FIXTURE_FILE_BYTES = 4 * 1024

HEADINGS: tuple[tuple[int, str], ...] = (
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
LEAF_HEADINGS = HEADINGS[:7] + HEADINGS[8:12] + HEADINGS[13:]
LEAF_TITLES = frozenset(title for _, title in LEAF_HEADINGS)


@dataclass(frozen=True)
class FixtureFile:
    """One bounded synthetic file relative to an isolated temporary root."""

    path: PurePosixPath
    content: str


@dataclass(frozen=True)
class EvaluationCase:
    """One explicit expected format decision and its isolated fixture."""

    id: str
    expected_format_pass: bool
    scope: str
    rationale: str
    document: str
    files: tuple[FixtureFile, ...] = ()


def _document(
    header: str,
    bodies: Mapping[str, str | None] | None = None,
    trailing: str = "",
) -> str:
    """Build the fixed skeleton without importing checker implementation data."""

    lines = ["# Synthetic Relaxation Model", "", header, ""]
    body_overrides = bodies or {}
    for level, title in HEADINGS:
        lines.extend([f"{'#' * level} {title}", ""])
        if title not in LEAF_TITLES:
            continue
        body = body_overrides.get(title, f"Synthetic body for {title}.")
        if body is not None:
            lines.extend([body, ""])
    if trailing:
        lines.extend([trailing, ""])
    return "\n".join(lines).rstrip() + "\n"


def _file(path: str, content: str = "# synthetic source; never execute\n") -> FixtureFile:
    return FixtureFile(PurePosixPath(path), content)


IMPLEMENTED_HEADER = "Implementation: [synthetic solver](../src/solver.R)"
PLANNED_HEADER = (
    "Implementation: Not implemented; plan: [approved plan](../plans/approved.md)."
)
CONVERSATION_PLAN_HEADER = (
    "Implementation: Not implemented; source: user-approved plan in this conversation."
)
SOLVER = _file("src/solver.R")


CASES: tuple[EvaluationCase, ...] = (
    EvaluationCase(
        id="valid-implemented-local-source",
        expected_format_pass=True,
        scope="format",
        rationale="A contained regular local implementation source is an allowed header target.",
        document=_document(IMPLEMENTED_HEADER),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="valid-planned-markdown-source",
        expected_format_pass=True,
        scope="format",
        rationale="A planned document may declare a contained Markdown plan source.",
        document=_document(PLANNED_HEADER),
        files=(_file("plans/approved.md", "# Synthetic approved plan\n"),),
    ),
    EvaluationCase(
        id="valid-conversation-plan",
        expected_format_pass=True,
        scope="format",
        rationale="The exact user-approved conversation plan declaration needs no local file.",
        document=_document(CONVERSATION_PLAN_HEADER),
    ),
    EvaluationCase(
        id="valid-angle-bracket-source-path",
        expected_format_pass=True,
        scope="format",
        rationale="An angle-bracketed relative target preserves a local path containing spaces.",
        document=_document("Implementation: [source](<../model files/source.py>)"),
        files=(_file("model files/source.py"),),
    ),
    EvaluationCase(
        id="extra-atx-heading-rejected",
        expected_format_pass=False,
        scope="format",
        rationale="A real extra H2 violates the fixed heading sequence.",
        document=_document(
            IMPLEMENTED_HEADER,
            {
                "1. Model Purpose And Questions": (
                    "Synthetic body for 1. Model Purpose And Questions.\n\n"
                    "## Extra Evaluation Section\n\nUnexpected material."
                )
            },
        ),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="setext-extra-heading-rejected",
        expected_format_pass=False,
        scope="known-unsupported-markdown",
        rationale="A setext H2 is still an extra Markdown heading and should be rejected.",
        document=_document(
            IMPLEMENTED_HEADER,
            {
                "1. Model Purpose And Questions": (
                    "Synthetic body for 1. Model Purpose And Questions.\n\n"
                    "Extra Evaluation Section\n------------------------\n\nUnexpected material."
                )
            },
        ),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="h7-pseudo-heading-is-body",
        expected_format_pass=True,
        scope="format",
        rationale="Seven hashes are plain text, not a Markdown heading level beyond H6.",
        document=_document(
            IMPLEMENTED_HEADER,
            {
                "1. Model Purpose And Questions": (
                    "Synthetic body for 1. Model Purpose And Questions.\n\n"
                    "####### Not A Markdown Heading"
                )
            },
        ),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="html-commented-extra-heading-ignored",
        expected_format_pass=True,
        scope="format",
        rationale="A heading inside an HTML comment must not alter the document structure.",
        document=_document(
            IMPLEMENTED_HEADER,
            {
                "1. Model Purpose And Questions": (
                    "Synthetic body for 1. Model Purpose And Questions.\n\n"
                    "<!-- ## Commented Extra Section -->"
                )
            },
        ),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="html-block-commented-extra-heading-ignored",
        expected_format_pass=True,
        scope="known-unsupported-markdown",
        rationale="A multiline HTML comment must not introduce a visible extra heading.",
        document=_document(
            IMPLEMENTED_HEADER,
            {"1. Model Purpose And Questions": "Visible content.\n\n<!--\n## Hidden Extra Section\n-->"},
        ),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="html-commented-required-sections-rejected",
        expected_format_pass=False,
        scope="known-unsupported-markdown",
        rationale="Required sections inside an HTML comment are absent from the rendered document.",
        document=_document(IMPLEMENTED_HEADER).replace(
            "## 1. Model Purpose And Questions", "<!--\n## 1. Model Purpose And Questions", 1
        ) + "-->\n",
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="html-comment-only-leaf-rejected",
        expected_format_pass=False,
        scope="known-unsupported-markdown",
        rationale="A comment-only leaf has no rendered body and should be treated as empty.",
        document=_document(
            IMPLEMENTED_HEADER,
            {"5. Governing Equations": "<!-- No visible section content -->"},
        ),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="markup-only-leaf-rejected",
        expected_format_pass=False,
        scope="known-unsupported-markdown",
        rationale="A thematic break alone is markup, not a nonempty leaf-section body.",
        document=_document(IMPLEMENTED_HEADER, {"5. Governing Equations": "---"}),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="fenced-headings-ignored",
        expected_format_pass=True,
        scope="format",
        rationale="Heading-like lines inside a balanced fence are code, not document headings.",
        document=_document(
            IMPLEMENTED_HEADER,
            {
                "1. Model Purpose And Questions": (
                    "Synthetic body for 1. Model Purpose And Questions.\n\n"
                    "```text\n## Fenced Fake H2\n### Fenced Fake H3\n```"
                )
            },
        ),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="display-math-headings-ignored",
        expected_format_pass=True,
        scope="format",
        rationale="Heading-like lines inside balanced display math are not document headings.",
        document=_document(
            IMPLEMENTED_HEADER,
            {"1. Model Purpose And Questions": "$$\n## Math Fake H2\nx = y\n$$"},
        ),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="balanced-multiline-display-math-is-content",
        expected_format_pass=True,
        scope="format",
        rationale="Balanced multiline display math supplies nonempty leaf-section content.",
        document=_document(
            IMPLEMENTED_HEADER,
            {"5. Governing Equations": "\\[\nF = 0\n\\]"},
        ),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="unbalanced-multiline-display-math-rejected",
        expected_format_pass=False,
        scope="format",
        rationale="An unclosed multiline display-math delimiter must fail structural validation.",
        document=_document(IMPLEMENTED_HEADER, trailing="$$\nx = y\nz = x + y"),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="remote-source-link-rejected",
        expected_format_pass=False,
        scope="format",
        rationale="Implementation targets must be contained relative paths, not remote URLs.",
        document=_document("Implementation: [source](https://example.invalid/model.R)"),
    ),
    EvaluationCase(
        id="source-link-escape-rejected",
        expected_format_pass=False,
        scope="format",
        rationale="A source target may not escape the synthetic repository root.",
        document=_document("Implementation: [source](../../outside.R)"),
    ),
    EvaluationCase(
        id="source-link-fragment-rejected",
        expected_format_pass=False,
        scope="format",
        rationale="Fragments make a source target non-file-like and must be rejected.",
        document=_document("Implementation: [source](../src/solver.R#entry)"),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="missing-source-link-rejected",
        expected_format_pass=False,
        scope="format",
        rationale="A declared implementation source must resolve to a regular local file.",
        document=_document("Implementation: [source](../src/missing.R)"),
    ),
    EvaluationCase(
        id="source-link-directory-rejected",
        expected_format_pass=False,
        scope="format",
        rationale="A directory is not a valid implementation source file.",
        document=_document("Implementation: [source](../src)"),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="planned-source-non-markdown-rejected",
        expected_format_pass=False,
        scope="format",
        rationale="A planned implementation declaration requires a Markdown plan target.",
        document=_document(
            "Implementation: Not implemented; plan: [plan](../plans/approved.txt)."
        ),
        files=(_file("plans/approved.txt", "Synthetic plan\n"),),
    ),
    EvaluationCase(
        id="wrong-physical-claim-is-manual-review-control",
        expected_format_pass=True,
        scope="semantic-manual-review",
        rationale=(
            "A structural pass is expected; the deliberately wrong physical claim requires "
            "manual scientific review."
        ),
        document=_document(
            IMPLEMENTED_HEADER,
            {
                "2. Physical Picture And Assumptions": (
                    "This deliberately wrong claim says an overdamped model conserves "
                    "inertial kinetic energy without evidence."
                )
            },
        ),
        files=(SOLVER,),
    ),
    EvaluationCase(
        id="alternate-local-source-is-provenance-control",
        expected_format_pass=True,
        scope="source-provenance-manual-review",
        rationale=(
            "A structural pass is expected; identifying an actual primary source is outside "
            "the checker's format contract."
        ),
        document=_document("Implementation: [alternate source](../src/alternate.R)"),
        files=(SOLVER, _file("src/alternate.R")),
    ),
)


def _is_within(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def _lexical_absolute(path: Path) -> Path:
    expanded = path.expanduser()
    if not expanded.is_absolute():
        expanded = Path.cwd() / expanded
    return Path(os.path.abspath(os.fspath(expanded)))


def _require_regular_file_without_symlinks(path: Path, label: str) -> Path:
    """Return a lexical absolute regular file after rejecting symlink components."""

    candidate = _lexical_absolute(path)
    current = Path(candidate.anchor)
    try:
        mode = current.lstat().st_mode
    except OSError as error:
        raise RuntimeError(f"{label} root is unavailable") from error
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        raise RuntimeError(f"{label} root must be a non-symlinked directory")

    parts = candidate.parts[1:]
    if not parts:
        raise RuntimeError(f"{label} must be a regular file")
    for index, part in enumerate(parts):
        current /= part
        try:
            mode = current.lstat().st_mode
        except OSError as error:
            raise RuntimeError(f"{label} is missing or unreadable") from error
        if stat.S_ISLNK(mode):
            raise RuntimeError(f"{label} contains a symlink path component")
        if index < len(parts) - 1 and not stat.S_ISDIR(mode):
            raise RuntimeError(f"{label} has a non-directory ancestor")
    if not stat.S_ISREG(mode):
        raise RuntimeError(f"{label} must be a regular file")
    return current


def _allowed_temporary_roots() -> tuple[Path, ...]:
    roots: list[Path] = []
    for candidate in (Path("/private/tmp"), Path(tempfile.gettempdir())):
        try:
            resolved = candidate.resolve(strict=True)
        except OSError:
            continue
        if resolved.is_dir() and resolved not in roots:
            roots.append(resolved)
    return tuple(roots)


def temporary_parent(preferred: Path | None = None) -> Path:
    """Return an allowed resolved temporary parent, never a repository path."""

    allowed_roots = _allowed_temporary_roots()
    if not allowed_roots:
        raise RuntimeError("no resolved /private/tmp or operating-system temporary directory")
    if preferred is None:
        return allowed_roots[0]

    try:
        candidate = preferred.resolve(strict=True)
    except OSError as error:
        raise RuntimeError("requested temporary parent is unavailable") from error
    if not candidate.is_dir() or not any(
        _is_within(candidate, root) for root in allowed_roots
    ):
        raise RuntimeError("requested temporary parent is outside allowed temporary roots")
    return candidate


def _validate_case(case: EvaluationCase) -> None:
    if not case.id or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-" for character in case.id):
        raise ValueError(f"invalid case id: {case.id!r}")
    if not case.scope or not case.rationale:
        raise ValueError(f"case {case.id} needs a scope and rationale")
    if len(case.document.encode("utf-8")) > MAX_DOCUMENT_BYTES:
        raise ValueError(f"case {case.id} document exceeds {MAX_DOCUMENT_BYTES} bytes")
    if len(case.files) > MAX_FIXTURE_FILES:
        raise ValueError(f"case {case.id} has too many fixture files")

    seen_paths = {DOCUMENT_PATH}
    for fixture in case.files:
        path = fixture.path
        if (
            path.is_absolute()
            or not path.parts
            or any(part in ("", ".", "..") for part in path.parts)
            or path in seen_paths
        ):
            raise ValueError(f"case {case.id} has an unsafe fixture path: {path}")
        if len(fixture.content.encode("utf-8")) > MAX_FIXTURE_FILE_BYTES:
            raise ValueError(f"case {case.id} fixture file exceeds byte limit: {path}")
        seen_paths.add(path)


def _write_fixture(case: EvaluationCase, root: Path) -> Path:
    """Create one bounded document tree beneath a fresh temporary directory."""

    _validate_case(case)
    root.mkdir(parents=True, exist_ok=False)
    document = root.joinpath(*DOCUMENT_PATH.parts)
    document.parent.mkdir(parents=True, exist_ok=True)
    document.write_text(case.document, encoding="utf-8")

    for fixture in case.files:
        destination = root.joinpath(*fixture.path.parts)
        if not _is_within(destination, root):
            raise RuntimeError(f"case {case.id} fixture escapes its temporary root")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(fixture.content, encoding="utf-8")
    return document


def invoke_checker(
    checker_path: Path, document: Path, root: Path
) -> subprocess.CompletedProcess[str]:
    """Invoke the checker as a separate read-only process with bytecode disabled."""

    checker = _require_regular_file_without_symlinks(checker_path, "checker path")
    return subprocess.run(
        [
            sys.executable,
            "-B",
            os.fspath(checker),
            os.fspath(document),
            "--root",
            os.fspath(root),
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=15,
    )


CheckerInvoker = Callable[[Path, Path, Path], subprocess.CompletedProcess[str]]


def _diagnostics(completed: subprocess.CompletedProcess[str]) -> list[str]:
    lines: list[str] = []
    passed = False
    for raw_line in completed.stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("Model-document format check passed:"):
            passed = True
            continue
        if line == "Model-document format check failed:":
            continue
        lines.append(line.removeprefix("- "))
    if passed:
        lines.insert(0, "format checker passed")
    if completed.stderr.strip():
        lines.append(f"stderr: {completed.stderr.strip().splitlines()[0]}")
    if not lines:
        lines.append(f"checker returned {completed.returncode} without diagnostics")
    if len(lines) > 3:
        remaining = len(lines) - 3
        lines = [*lines[:3], f"{remaining} additional diagnostics"]
    return lines


def _case_report(
    case: EvaluationCase, completed: subprocess.CompletedProcess[str]
) -> dict[str, object]:
    valid_response = (
        completed.returncode in (0, 1)
        and not completed.stderr.strip()
        and completed.stdout.startswith(
            "Model-document format check passed:" if completed.returncode == 0
            else "Model-document format check failed:"
        )
    )
    actual_pass = completed.returncode == 0 if valid_response else None
    return {
        "id": case.id,
        "expectation": {
            "format_pass": case.expected_format_pass,
            "scope": case.scope,
        },
        "actual_pass": actual_pass,
        "outcome": (
            "error" if not valid_response else
            "match" if actual_pass == case.expected_format_pass else "mismatch"
        ),
        "rationale": case.rationale,
        "diagnostics": _diagnostics(completed),
        "returncode": completed.returncode,
    }


def evaluate_cases(
    cases: Sequence[EvaluationCase] = CASES,
    checker_path: Path = CHECKER_PATH,
    temporary_root: Path | None = None,
    invoker: CheckerInvoker = invoke_checker,
) -> dict[str, object]:
    """Evaluate explicit decisions in one bounded temporary directory tree."""

    selected_cases = tuple(cases)
    if not selected_cases:
        raise ValueError("at least one evaluation case is required")
    ids = [case.id for case in selected_cases]
    if len(ids) != len(set(ids)):
        raise ValueError("evaluation case ids must be unique")
    for case in selected_cases:
        _validate_case(case)

    checker = _require_regular_file_without_symlinks(checker_path, "checker path")
    parent = temporary_parent(temporary_root)
    reports: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(
        prefix="model-document-checker-eval-", dir=parent
    ) as temporary:
        temporary_directory = Path(temporary).resolve(strict=True)
        if not _is_within(temporary_directory, parent):
            raise RuntimeError("evaluation temporary directory escaped its allowed parent")
        for index, case in enumerate(selected_cases, start=1):
            fixture_root = temporary_directory / f"case-{index:02d}-{case.id}" / "repository"
            if not _is_within(fixture_root, temporary_directory):
                raise RuntimeError(f"case {case.id} root escaped the temporary directory")
            document = _write_fixture(case, fixture_root)
            try:
                completed = invoker(checker, document, fixture_root)
            except (OSError, subprocess.TimeoutExpired) as error:
                completed = subprocess.CompletedProcess(
                    args=[os.fspath(checker)], returncode=124, stdout="",
                    stderr=f"Checker invocation failed: {type(error).__name__}",
                )
            reports.append(_case_report(case, completed))

    mismatch_count = sum(report["outcome"] == "mismatch" for report in reports)
    error_count = sum(report["outcome"] == "error" for report in reports)
    return {
        "suite": "model-document-checker-adversarial-eval",
        "checker": os.fspath(checker),
        "temporary_parent": os.fspath(parent),
        "case_count": len(reports),
        "mismatch_count": mismatch_count,
        "error_count": error_count,
        "cases": reports,
    }


def main() -> int:
    """Print the JSON report and fail on mismatches or execution errors."""

    try:
        report = evaluate_cases()
    except Exception as error:
        print(
            json.dumps(
                {
                    "suite": "model-document-checker-adversarial-eval",
                    "runner_error": f"{type(error).__name__}: {error}",
                },
                indent=2,
            )
        )
        return 2

    print(json.dumps(report, indent=2))
    return 1 if report["mismatch_count"] or report.get("error_count", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
