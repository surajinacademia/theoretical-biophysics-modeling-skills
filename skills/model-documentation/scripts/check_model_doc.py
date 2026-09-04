#!/usr/bin/env python3
"""Read-only format checks for the default model-document Markdown skeleton.

The checker deliberately validates document format only. It does not inspect or
execute linked sources, evaluate equations, or make scientific claims.
"""

from __future__ import annotations

import argparse
import os
import re
import stat
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path


EXPECTED_HEADINGS: tuple[tuple[int, str], ...] = (
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
LEAF_HEADINGS = frozenset(
    EXPECTED_HEADINGS[:7] + EXPECTED_HEADINGS[8:12] + EXPECTED_HEADINGS[13:]
)

ATX_HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.*?)[ \t]*$")
SETEXT_UNDERLINE = re.compile(r"^ {0,3}(?P<marker>=+|-+)[ \t]*$")
THEMATIC_BREAK = re.compile(
    r"^ {0,3}(?:(?:\*[ \t]*){3,}|(?:_[ \t]*){3,}|(?:-[ \t]*){3,})$"
)
MARKDOWN_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
LINK = re.compile(r"^\[(?P<label>[^\]\r\n]+)\]\((?P<target>[^)\r\n]+)\)$")
IMPLEMENTATION_PREFIX = r"(?:Implementation:|\*\*Implementation:\*\*)"
IMPLEMENTED_HEADER = re.compile(
    rf"^{IMPLEMENTATION_PREFIX}\s+(?P<link>\[[^\r\n]*\]\([^\r\n]*\))\.?$"
)
PLANNED_HEADER = re.compile(
    rf"^{IMPLEMENTATION_PREFIX}\s+Not implemented;\s+plan:\s+"
    r"(?P<link>\[[^\r\n]*\]\([^\r\n]*\))\.?$"
)
CONVERSATION_PLAN_HEADER = re.compile(
    rf"^{IMPLEMENTATION_PREFIX}\s+Not implemented; source: "
    r"user-approved plan in this conversation\.$"
)
ADMINISTRATIVE_TITLE = re.compile(
    r"^(?:canonical\s+model(?:\s+(?:documentation|docs))?|"
    r"model\s+(?:documentation|docs))\b",
    re.IGNORECASE,
)
ANGLE_BRACKETS = re.compile(r"<([^<>\r\n]{1,120})>")
WORD_LIKE = re.compile(r"[A-Za-z][A-Za-z0-9_.:/-]*\Z")
TEMPLATE_WORDS = frozenset(
    {
        "artifact",
        "citation",
        "definition",
        "domain",
        "explicit",
        "field",
        "file",
        "identifier",
        "model",
        "name",
        "output",
        "path",
        "range",
        "rationale",
        "source",
        "status",
        "symbol",
        "type",
        "unit",
        "value",
    }
)


@dataclass(frozen=True)
class Heading:
    """One ATX heading outside fenced code and display math."""

    line: int
    level: int
    text: str


@dataclass
class ParsedMarkdown:
    """Structural facts collected without interpreting scientific content."""

    lines: list[str]
    visible_lines: list[str]
    headings: list[Heading]
    content_lines: list[bool]
    errors: list[str]


class StdoutArgumentParser(argparse.ArgumentParser):
    """Keep CLI help and parse diagnostics on stdout with checker diagnostics."""

    def _print_message(self, message: str | None, file: object | None = None) -> None:
        if message:
            sys.stdout.write(message)


def _lexical_absolute(path: Path, base: Path) -> Path:
    """Make an absolute path without resolving any symlink."""

    expanded = path.expanduser()
    if not expanded.is_absolute():
        expanded = base / expanded
    return Path(os.path.abspath(os.fspath(expanded)))


def _safe_root(root: Path, errors: list[str]) -> bool:
    """Require an existing directory and reject every symlinked root component."""

    current = Path(root.anchor)
    try:
        mode = current.lstat().st_mode
    except OSError:
        errors.append("repository root is missing or unreadable")
        return False
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        errors.append("repository root must be a non-symlinked directory")
        return False

    for part in root.parts[1:]:
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            errors.append("repository root is missing or unreadable")
            return False
        except OSError:
            errors.append("repository root is unreadable")
            return False
        if stat.S_ISLNK(mode):
            errors.append("repository root contains a symlink path component")
            return False
        if not stat.S_ISDIR(mode):
            errors.append("repository root must be a directory")
            return False
    return True


def _raw_path_has_no_symlink(
    raw_path: Path,
    base: Path,
    label: str,
    errors: list[str],
) -> bool:
    """Reject symlinks and require every raw path component to resolve."""

    try:
        expanded = raw_path.expanduser()
    except RuntimeError:
        errors.append(f"{label} cannot be expanded safely")
        return False

    if expanded.is_absolute():
        current = Path(expanded.anchor)
        parts = expanded.parts[1:]
    else:
        current = base
        parts = expanded.parts

    for index, part in enumerate(parts):
        if part in ("", "."):
            continue
        if part == "..":
            current = current.parent
            continue
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            errors.append(f"{label} does not resolve")
            return False
        except (NotADirectoryError, OSError):
            errors.append(f"{label} is unreadable")
            return False
        if stat.S_ISLNK(mode):
            errors.append(f"{label} contains a symlink path component")
            return False
        if any(next_part not in ("", ".") for next_part in parts[index + 1 :]) and not stat.S_ISDIR(mode):
            errors.append(f"{label} has a non-directory ancestor")
            return False
    return True


def _contained_regular_file(
    root: Path,
    relative: Path,
    label: str,
    errors: list[str],
) -> Path | None:
    """Return a contained regular file without following any symlink component."""

    if relative.is_absolute() or not relative.parts or ".." in relative.parts:
        errors.append(f"{label} escapes the repository root")
        return None

    current = root
    for index, part in enumerate(relative.parts):
        current /= part
        try:
            mode = current.lstat().st_mode
        except FileNotFoundError:
            errors.append(f"{label} does not exist")
            return None
        except OSError:
            errors.append(f"{label} is unreadable")
            return None
        if stat.S_ISLNK(mode):
            errors.append(f"{label} contains a symlink path component")
            return None
        if index < len(relative.parts) - 1 and not stat.S_ISDIR(mode):
            errors.append(f"{label} has a non-directory ancestor")
            return None

    if not stat.S_ISREG(mode):
        errors.append(f"{label} must be a regular file")
        return None
    return current


def _heading_text(raw: str) -> str:
    """Normalize optional closing ATX hashes while preserving heading words."""

    return re.sub(r"[ \t]+#+[ \t]*$", "", raw).strip()


def _looks_like_template_placeholder(line: str) -> bool:
    """Find clear template markers while leaving ordinary math inequalities alone."""

    for match in ANGLE_BRACKETS.finditer(line):
        # Angle-bracketed link destinations are checked as paths, not prose.
        if line[: match.start()].endswith("](") and line[match.end() :].startswith(")"):
            continue
        candidate = match.group(1).strip()
        lowered = candidate.lower()
        if candidate == "..." or lowered == "model name":
            return True
        words = candidate.split()
        if len(words) >= 2 and all(WORD_LIKE.fullmatch(word) for word in words):
            return True
        if WORD_LIKE.fullmatch(candidate) and any(
            word in lowered for word in TEMPLATE_WORDS
        ):
            return True
    return False


def _matching_backtick_closer(line: str, delimiter: str, start: int) -> int | None:
    """Find a same-length backtick run that closes one lightweight code span."""

    position = line.find(delimiter, start)
    while position >= 0:
        end = position + len(delimiter)
        if (position == 0 or line[position - 1] != "`") and (
            end == len(line) or line[end] != "`"
        ):
            return position
        position = line.find(delimiter, end)
    return None


def _without_html_comments(
    line: str,
    in_comment: bool,
) -> tuple[str, bool]:
    """Remove comments outside lightweight code and paired same-line math spans."""

    visible: list[str] = []
    position = 0
    while position < len(line):
        if in_comment:
            closing = line.find("-->", position)
            if closing < 0:
                return "".join(visible), True
            position = closing + len("-->")
            in_comment = False
            continue

        comment_opening = line.find("<!--", position)
        code_opening = line.find("`", position)
        math_opening = line.find("$$", position)
        openings = [
            (opening, kind)
            for opening, kind in (
                (comment_opening, "comment"),
                (code_opening, "code"),
                (math_opening, "math"),
            )
            if opening >= 0
        ]
        if not openings:
            visible.append(line[position:])
            break

        opening, kind = min(openings)
        if kind == "comment":
            visible.append(line[position:opening])
            position = opening + len("<!--")
            in_comment = True
            continue
        if kind == "code":
            visible.append(line[position:opening])
            delimiter_end = opening
            while delimiter_end < len(line) and line[delimiter_end] == "`":
                delimiter_end += 1
            delimiter = line[opening:delimiter_end]
            closing = _matching_backtick_closer(line, delimiter, delimiter_end)
            if closing is None:
                visible.append(delimiter)
                position = delimiter_end
                continue
            closing_end = closing + len(delimiter)
            visible.append(line[opening:closing_end])
            position = closing_end
            continue

        closing = line.find("$$", opening + len("$$"))
        if closing < 0:
            visible.append(line[position : opening + len("$$")])
            position = opening + len("$$")
            continue
        closing_end = closing + len("$$")
        visible.append(line[position:closing_end])
        position = closing_end

    return "".join(visible), in_comment


def parse_markdown(text: str) -> ParsedMarkdown:
    """Parse headings and lightweight block delimiters needed for format checks."""

    lines = text.splitlines()
    visible_lines = list(lines)
    headings: list[Heading] = []
    content_lines = [False] * len(lines)
    errors: list[str] = []
    fence: tuple[str, int, int] | None = None
    display_math: tuple[str, int] | None = None
    in_html_comment = False
    setext_candidate: tuple[int, str] | None = None

    for index, line in enumerate(lines):
        line_number = index + 1
        stripped = line.strip()

        if fence is not None:
            setext_candidate = None
            marker, minimum_length, opened_at = fence
            match = MARKDOWN_FENCE.match(line)
            if (
                match is not None
                and match.group(1)[0] == marker
                and len(match.group(1)) >= minimum_length
                and not match.group(2).strip()
            ):
                fence = None
            elif stripped:
                content_lines[index] = True
            continue

        if display_math is not None:
            setext_candidate = None
            delimiter, opened_at = display_math
            closing = "$$" if delimiter == "$$" else r"\]"
            if stripped == closing:
                display_math = None
            elif stripped:
                content_lines[index] = True
            continue

        if not in_html_comment:
            match = MARKDOWN_FENCE.match(line)
            if match is not None:
                fence = (match.group(1)[0], len(match.group(1)), line_number)
                setext_candidate = None
                continue

            if stripped == "$$":
                display_math = ("$$", line_number)
                setext_candidate = None
                continue
            if stripped == r"\[":
                display_math = (r"\[", line_number)
                setext_candidate = None
                continue
            if stripped == r"\]":
                errors.append(f"unmatched display-math delimiter at line {line_number}")
                setext_candidate = None
                continue

        visible, in_html_comment = _without_html_comments(line, in_html_comment)
        visible_lines[index] = visible
        stripped = visible.strip()

        heading = ATX_HEADING.match(visible)
        if heading is not None:
            headings.append(
                Heading(line=index, level=len(heading.group(1)), text=_heading_text(heading.group(2)))
            )
            setext_candidate = None
        elif (underline := SETEXT_UNDERLINE.match(visible)) is not None and setext_candidate:
            candidate_line, candidate_text = setext_candidate
            headings.append(
                Heading(
                    line=candidate_line,
                    level=1 if underline.group("marker")[0] == "=" else 2,
                    text=candidate_text,
                )
            )
            content_lines[candidate_line] = False
            setext_candidate = None
        elif THEMATIC_BREAK.match(visible) is not None:
            setext_candidate = None
        elif stripped:
            content_lines[index] = True
            setext_candidate = (index, stripped)
        else:
            setext_candidate = None

        if _looks_like_template_placeholder(visible):
            errors.append(f"unresolved template placeholder at line {line_number}")

    if fence is not None:
        errors.append(f"unclosed fenced code block opened at line {fence[2]}")
    if display_math is not None:
        errors.append(f"unclosed display-math block opened at line {display_math[1]}")

    return ParsedMarkdown(lines, visible_lines, headings, content_lines, errors)


def _parse_link(raw: str) -> tuple[str, str] | None:
    """Return a nonempty Markdown link label and an unadorned local target."""

    match = LINK.fullmatch(raw)
    if match is None:
        return None
    label = match.group("label").strip()
    target = match.group("target").strip()
    if target.startswith("<") or target.endswith(">"):
        if not (target.startswith("<") and target.endswith(">")):
            return None
        target = target[1:-1]
        if not target or "<" in target or ">" in target:
            return None
    elif any(char.isspace() for char in target):
        return None
    if not label.strip("` \t") or not target:
        return None
    return label, target


def _parse_implementation_header(line: str) -> tuple[str, str | None] | None:
    """Classify one allowed first-content implementation declaration."""

    if CONVERSATION_PLAN_HEADER.fullmatch(line):
        return "conversation-plan", None
    planned = PLANNED_HEADER.fullmatch(line)
    if planned is not None:
        link = _parse_link(planned.group("link"))
        return ("planned", link[1]) if link is not None else None
    implemented = IMPLEMENTED_HEADER.fullmatch(line)
    if implemented is not None:
        link = _parse_link(implemented.group("link"))
        return ("implemented", link[1]) if link is not None else None
    return None


def _validate_link_target(
    target: str,
    document: Path,
    root: Path,
    label: str,
    errors: list[str],
) -> Path | None:
    """Validate one declared local source or plan path without reading it."""

    if (
        target.startswith(("/", "\\", "#"))
        or "://" in target
        or target.startswith(("mailto:", "http:", "https:"))
        or "#" in target
        or "?" in target
        or re.match(r"^[A-Za-z]:[\\/]", target)
    ):
        errors.append(f"{label} must be a contained relative path")
        return None

    target_path = Path(target)
    if target_path.is_absolute():
        errors.append(f"{label} must be a contained relative path")
        return None
    candidate = _lexical_absolute(target_path, document.parent)
    try:
        relative = candidate.relative_to(root)
    except ValueError:
        errors.append(f"{label} escapes the repository root")
        return None
    if not _raw_path_has_no_symlink(target_path, document.parent, label, errors):
        return None
    return _contained_regular_file(root, relative, label, errors)


def _validate_title_and_header(
    parsed: ParsedMarkdown,
    document: Path,
    root: Path,
    errors: list[str],
) -> None:
    """Check the H1 and its immediately following implementation declaration."""

    titles = [heading for heading in parsed.headings if heading.level == 1]
    if len(titles) != 1:
        errors.append("document must contain exactly one model-name H1")
        return

    title = titles[0]
    if any(line.strip() for line in parsed.visible_lines[: title.line]):
        errors.append("model-name H1 must be the first content in the document")
    if not title.text:
        errors.append("model-name H1 must not be empty")
    elif ADMINISTRATIVE_TITLE.match(title.text):
        errors.append("model-name H1 must not use an administrative documentation prefix")

    first_after_title = next(
        (
            (index, line)
            for index, line in enumerate(
                parsed.visible_lines[title.line + 1 :], start=title.line + 1
            )
            if line.strip()
        ),
        None,
    )
    if first_after_title is None:
        errors.append("first content below the model-name H1 must be an Implementation declaration")
        return

    line_number, header_line = first_after_title
    header = _parse_implementation_header(header_line)
    if header is None:
        errors.append(
            f"first content below the model-name H1 at line {line_number + 1} "
            "must be an allowed Implementation declaration"
        )
        return

    mode, target = header
    if mode == "conversation-plan":
        return
    assert target is not None
    if mode == "planned" and Path(target).suffix.lower() != ".md":
        errors.append("source plan link target must be a .md file")
        return
    target_label = "implementation source link" if mode == "implemented" else "source plan link"
    _validate_link_target(target, document, root, target_label, errors)


def _render_heading(heading: tuple[int, str]) -> str:
    return f"{'#' * heading[0]} {heading[1]}"


def _validate_heading_sequence(parsed: ParsedMarkdown, errors: list[str]) -> None:
    """Require the complete fixed H2/H3 sequence exactly once and in order."""

    actual = [(heading.level, heading.text) for heading in parsed.headings if heading.level in (2, 3)]
    expected_counts = Counter(EXPECTED_HEADINGS)
    actual_counts = Counter(actual)

    for heading, expected_count in expected_counts.items():
        actual_count = actual_counts[heading]
        if actual_count < expected_count:
            errors.append(f"missing required heading: {_render_heading(heading)}")
        elif actual_count > expected_count:
            errors.append(f"repeated heading: {_render_heading(heading)}")
    for heading in actual_counts:
        if heading not in expected_counts:
            errors.append(f"unexpected heading: {_render_heading(heading)}")
    if actual == list(EXPECTED_HEADINGS):
        return
    if Counter(actual) == expected_counts:
        errors.append("H2/H3 headings are not in the required order")


def _validate_heading_levels(parsed: ParsedMarkdown, errors: list[str]) -> None:
    for heading in parsed.headings:
        if heading.level >= 4:
            errors.append(f"heading at line {heading.line + 1} is deeper than H3")


def _validate_leaf_sections(parsed: ParsedMarkdown, errors: list[str]) -> None:
    """Reject blank leaves while allowing parent H2 sections to contain only H3s."""

    headings = [heading for heading in parsed.headings if heading.level in (2, 3)]
    if [(heading.level, heading.text) for heading in headings] != list(EXPECTED_HEADINGS):
        return

    all_headings = sorted(parsed.headings, key=lambda heading: heading.line)
    for heading in headings:
        key = (heading.level, heading.text)
        if key not in LEAF_HEADINGS:
            continue
        next_heading_line = len(parsed.lines)
        for candidate in all_headings:
            if candidate.line > heading.line:
                next_heading_line = candidate.line
                break
        if not any(parsed.content_lines[heading.line + 1 : next_heading_line]):
            errors.append(f"empty leaf section: {heading.text}")


def validate_document(document: Path, root: Path) -> list[str]:
    """Return format diagnostics for one document; this function never writes."""

    errors: list[str] = []
    try:
        root_input = Path(root)
        document_input = Path(document)
        root_path = _lexical_absolute(root_input, Path.cwd())
        document_path = _lexical_absolute(document_input, Path.cwd())
    except (OSError, RuntimeError, TypeError, ValueError):
        return ["document or repository root path cannot be interpreted safely"]

    if not _raw_path_has_no_symlink(root_input, Path.cwd(), "repository root", errors):
        return errors
    if not _safe_root(root_path, errors):
        return errors

    try:
        relative_document = document_path.relative_to(root_path)
    except ValueError:
        errors.append("document path escapes the repository root")
        return errors
    if document_path.suffix.lower() != ".md":
        errors.append("document must be a .md file")
        return errors
    if not _raw_path_has_no_symlink(document_input, Path.cwd(), "document path", errors):
        return errors
    safe_document = _contained_regular_file(
        root_path, relative_document, "document path", errors
    )
    if safe_document is None:
        return errors

    try:
        text = safe_document.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return [*errors, "document must be UTF-8 text"]
    except OSError:
        return [*errors, "document is unreadable"]

    parsed = parse_markdown(text)
    errors.extend(parsed.errors)
    _validate_title_and_header(parsed, safe_document, root_path, errors)
    _validate_heading_levels(parsed, errors)
    _validate_heading_sequence(parsed, errors)
    _validate_leaf_sections(parsed, errors)
    return errors


def build_parser() -> argparse.ArgumentParser:
    """Build the public read-only checker CLI."""

    parser = StdoutArgumentParser(
        description="Check the fixed default model-document Markdown format."
    )
    parser.add_argument("document", metavar="DOC", type=Path, help="Markdown document to check.")
    parser.add_argument(
        "--root",
        required=True,
        type=Path,
        help="Repository boundary that must contain DOC and any declared local target.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the checker and print every diagnostic to stdout."""

    args = build_parser().parse_args(argv)
    errors = validate_document(args.document, args.root)
    if errors:
        print("Model-document format check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Model-document format check passed: format only; not scientific validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
