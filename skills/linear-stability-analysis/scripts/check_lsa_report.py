#!/usr/bin/env python3
"""Read-only checks for a canonical single-file LSA LaTeX report.

This deliberately checks direct LaTeX structure and local figure references only.
It rejects conditional and dynamic wrappers instead of interpreting them. It never
runs TeX, a shell, or calculations, and cannot verify mathematics, figure contents,
macro expansion, or compiled layout.
"""

from __future__ import annotations

import argparse
import os
import re
import stat
import sys
from pathlib import Path


SECTIONS = (
    "Model Purpose And Questions",
    "Physical Picture And Assumptions",
    "Entities, Domain, And Notation",
    "Parameters And Scales",
    "Governing Equations",
    "Initial And Boundary Conditions",
    "Observables And Model Tests",
    "Solution Method",
    "Model Record And Implementation",
)
SUBSECTIONS = (
    ("Solution Method", "Methodology And Rationale"),
    ("Solution Method", "Numerical Formulation"),
    ("Solution Method", "Algorithm And Flowchart"),
    ("Solution Method", "Accuracy And Verification"),
    ("Model Record And Implementation", "Implementation Mapping"),
    ("Model Record And Implementation", "Method Decisions And Changes"),
    ("Model Record And Implementation", "References"),
)
EXPECTED = tuple(("section", title) for title in SECTIONS[:8]) + tuple(
    ("subsection", title) for parent, title in SUBSECTIONS[:4]
) + (("section", SECTIONS[8]),) + tuple(("subsection", title) for parent, title in SUBSECTIONS[4:])
ALLOWED_FIGURE_EXTENSIONS = (".pdf", ".png", ".jpg", ".jpeg")
LITERAL_ENVIRONMENTS = "verbatim|verbatim\\*|Verbatim|BVerbatim|LVerbatim|lstlisting|lstlisting\\*|minted"
LITERAL_BEGIN = re.compile(r"\\begin\s*\{\s*(" + LITERAL_ENVIRONMENTS + r")\s*\}")
COMMAND = re.compile(r"\\([A-Za-z@]+)")
STRUCTURAL = {"part", "chapter", "section", "subsection", "subsubsection", "paragraph", "subparagraph"}
UNSUPPORTED_INPUT = {"input", "include", "subfile", "import", "subimport", "includestandalone"}
MACRO_COMMANDS = {
    "newcommand", "renewcommand", "providecommand", "DeclareRobustCommand",
    "newenvironment", "renewenvironment", "provideenvironment", "def", "gdef", "edef", "xdef",
}
SENSITIVE_COMMANDS = {"section", "subsection", "includegraphics", "title", "maketitle", "documentclass", "begin", "end"}
DYNAMIC_COMMANDS = {
    "let", "futurelet", "csname", "expandafter", "noexpand", "newif", "chardef", "mathchardef", "countdef", "toksdef",
    "catcode", "makeatletter", "makeatother", "explsyntaxon", "explsyntaxoff", "newdocumentcommand", "renewdocumentcommand", "providedocumentcommand",
}


def _mask(text: str) -> str:
    return "".join("\n" if char == "\n" else " " for char in text)


def _without_comments(text: str) -> str:
    """Mask TeX comments; an odd run of preceding slashes escapes a percent."""
    lines: list[str] = []
    for line in text.splitlines(keepends=True):
        for index, char in enumerate(line):
            if char != "%":
                continue
            slashes = 0
            while index > slashes and line[index - slashes - 1] == "\\":
                slashes += 1
            if slashes % 2 == 0:
                lines.append(line[:index] + _mask(line[index:]))
                break
        else:
            lines.append(line)
    return "".join(lines)


def _active_source(text: str, errors: list[str]) -> str:
    """Mask comments and literal listing environments, preserving positions."""
    source = _without_comments(text)
    cursor = 0
    chunks: list[str] = []
    while (begin := next((item for item in LITERAL_BEGIN.finditer(source, cursor) if _direct_command(source, item.start())), None)) is not None:
        chunks.append(source[cursor : begin.start()])
        name = begin.group(1)
        end = next(
            (item for item in re.compile(r"\\end\s*\{\s*" + re.escape(name) + r"\s*\}").finditer(source, begin.end()) if _direct_command(source, item.start())),
            None,
        )
        if end is None:
            errors.append(f"unclosed literal environment {name} at line {source.count(chr(10), 0, begin.start()) + 1}")
            chunks.append(_mask(source[begin.start() :]))
            return "".join(chunks)
        chunks.append(_mask(source[begin.start() : end.end()]))
        cursor = end.end()
    chunks.append(source[cursor:])
    return "".join(chunks)


def _skip_space(source: str, position: int) -> int:
    while position < len(source) and source[position].isspace():
        position += 1
    return position


def _argument(source: str, position: int, opener: str = "{", closer: str = "}") -> tuple[str, int] | None:
    position = _skip_space(source, position)
    if position >= len(source) or source[position] != opener:
        return None
    depth, start, index = 1, position + 1, position + 1
    while index < len(source):
        if source[index] == "\\":
            index += 2
            continue
        if source[index] == opener:
            depth += 1
        elif source[index] == closer:
            depth -= 1
            if not depth:
                return source[start:index], index + 1
        index += 1
    return None


def _normal(text: str) -> str:
    return " ".join(text.split())


def _line(source: str, position: int) -> int:
    return source.count("\n", 0, position) + 1


def _direct_command(source: str, position: int) -> bool:
    slashes = 0
    while position > slashes and source[position - slashes - 1] == "\\":
        slashes += 1
    return slashes % 2 == 0


def _walk(path: Path, base: Path) -> tuple[Path, int] | tuple[None, str]:
    """lstat every component without resolving symlinks or reading file content."""
    try:
        raw = path.expanduser()
    except RuntimeError:
        return None, "cannot be expanded safely"
    candidate = raw if raw.is_absolute() else base / raw
    current = Path(candidate.anchor)
    try:
        mode = current.lstat().st_mode
    except OSError:
        return None, "is missing or unreadable"
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        return None, "has an unsafe filesystem root"
    parts = candidate.parts[1:]
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
            return None, "does not exist"
        except OSError:
            return None, "is unreadable"
        if stat.S_ISLNK(mode):
            return None, "contains a symlink path component"
        if index < len(parts) - 1 and not stat.S_ISDIR(mode):
            return None, "has a non-directory ancestor"
    return current, mode


def _absolute(path: Path, base: Path) -> Path:
    expanded = path.expanduser()
    return Path(os.path.abspath(os.fspath(expanded if expanded.is_absolute() else base / expanded)))


def _safe_file(path: Path, base: Path, root: Path) -> tuple[Path | None, str | None]:
    candidate = _absolute(path, base)
    try:
        candidate.relative_to(root)
    except ValueError:
        return None, "escapes the analysis root"
    checked, detail = _walk(path, base)
    if checked is None:
        return None, detail
    if not stat.S_ISREG(detail):
        return None, "must be a regular file"
    return candidate, None


def _commands(source: str, errors: list[str]):
    """Yield direct control words and their enclosing brace depth."""
    depth, position = 0, 0
    while position < len(source):
        if source[position] == "\\":
            match = COMMAND.match(source, position)
            if match is not None and _direct_command(source, position):
                yield match.group(1), position, match.end(), depth
                position = match.end()
                continue
            position += 2
            continue
        if source[position] == "{":
            depth += 1
        elif source[position] == "}":
            if depth:
                depth -= 1
            else:
                errors.append(f"unmatched closing brace at line {_line(source, position)}")
        position += 1
    if depth:
        errors.append("unclosed braced group")


def _graphic_path(source: str, position: int) -> tuple[str | None, int]:
    position = _skip_space(source, position)
    if position < len(source) and source[position] == "*":
        position = _skip_space(source, position + 1)
    if position < len(source) and source[position] == "[":
        option = _argument(source, position, "[", "]")
        if option is None:
            return None, position
        position = option[1]
    argument = _argument(source, position)
    return (argument[0].strip(), argument[1]) if argument else (None, position)


def _macro_body_has_structure(source: str, name: str, position: int) -> bool:
    """Recognize common direct macro definitions without expanding any macro."""
    if name in {"def", "gdef", "edef", "xdef"}:
        opening = source.find("{", position, min(len(source), position + 400))
        body = _argument(source, opening) if opening >= 0 else None
    else:
        declared = _argument(source, position)
        if declared is None:
            return False
        position = declared[1]
        while _skip_space(source, position) < len(source) and source[_skip_space(source, position)] == "[":
            optional = _argument(source, _skip_space(source, position), "[", "]")
            if optional is None:
                return False
            position = optional[1]
        body = _argument(source, position)
    return bool(body and re.search(r"\\(?:section|subsection|includegraphics)\b", body[0]))


def _macro_target(source: str, name: str, position: int) -> str | None:
    if name in {"def", "gdef", "edef", "xdef"}:
        match = COMMAND.match(source, _skip_space(source, position))
        return match.group(1) if match is not None else None
    declared = _argument(source, position)
    if declared is None:
        return None
    match = re.fullmatch(r"\\([A-Za-z@]+)", declared[0].strip())
    return match.group(1) if match is not None else None


def _dynamic(name: str) -> bool:
    lowered = name.lower()
    return (
        (lowered.startswith("if") and lowered != "iff")
        or lowered.startswith("@if")
        or lowered in {"fi", "else", "or", "unless"}
        or lowered in DYNAMIC_COMMANDS
    )


def _validate_figure(raw: str, report: Path, root: Path) -> tuple[Path | None, str | None]:
    if not raw or raw != raw.strip() or any(char in raw for char in "\\{}#?$\r\n\x00") or raw.startswith("~"):
        return None, "must use a literal relative path"
    path = Path(raw)
    if path.is_absolute() or "://" in raw or re.match(r"^[A-Za-z]:", raw) or not path.name:
        return None, "must use a literal relative path"
    if path.suffix:
        if path.suffix.lower() not in ALLOWED_FIGURE_EXTENSIONS:
            return None, "uses an unsupported figure extension"
        return _safe_file(path, report.parent, root)
    candidates: list[Path] = []
    invalid: list[str] = []
    for extension in ALLOWED_FIGURE_EXTENSIONS:
        candidate, detail = _safe_file(path.with_suffix(extension), report.parent, root)
        if candidate is not None:
            candidates.append(candidate)
        elif detail not in ("does not exist",):
            invalid.append(detail or "is invalid")
    if invalid:
        return None, invalid[0]
    if not candidates:
        return None, "has no permitted figure file for TeX extension inference"
    if len(candidates) != 1:
        return None, "has ambiguous TeX extension inference"
    return candidates[0], None


def validate_report(report: Path, root: Path) -> list[str]:
    """Return bounded structural diagnostics; never writes or executes input."""
    errors: list[str] = []
    cwd = Path.cwd()
    root_checked, root_mode = _walk(root, cwd)
    if root_checked is None or not stat.S_ISDIR(root_mode):
        return [f"analysis root {root_mode if root_checked is None else 'must be a directory'}"]
    root_path = _absolute(root, cwd)
    report_path, detail = _safe_file(report, cwd, root_path)
    if report_path is None:
        return [f"report path {detail}"]
    if report_path.suffix.lower() != ".tex":
        return ["report path must name a .tex file"]
    try:
        text = report_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return ["report must be UTF-8 text"]
    except OSError:
        return ["report is unreadable"]

    source = _active_source(text, errors)
    events: list[tuple[str, str, int]] = []
    graphics: list[tuple[str, int, int]] = []
    titles: list[tuple[str, int]] = []
    maketitles: list[int] = []
    begins: list[int] = []
    ends: list[int] = []
    documentclasses = 0
    for name, start, end, depth in _commands(source, errors):
        if _dynamic(name):
            errors.append(f"unsupported conditional, alias, or catcode command \\{name} at line {_line(source, start)}")
        if name in UNSUPPORTED_INPUT:
            errors.append(f"unsupported file inclusion command \\{name} at line {_line(source, start)}")
        if name in MACRO_COMMANDS:
            target = _macro_target(source, name, end)
            if target in SENSITIVE_COMMANDS or _macro_body_has_structure(source, name, end):
                errors.append(f"unsupported macro-generated structure near line {_line(source, start)}")
        hidden_document_environment = False
        if name in {"begin", "end"}:
            argument = _argument(source, end)
            hidden_document_environment = bool(argument and _normal(argument[0]) == "document")
        if depth and (name in SENSITIVE_COMMANDS - {"begin", "end"} or hidden_document_environment):
            errors.append(f"canonical command \\{name} at line {_line(source, start)} is hidden in a braced group")
            continue
        if name == "documentclass":
            documentclasses += 1
        elif name in ("begin", "end"):
            argument = _argument(source, end)
            if argument and _normal(argument[0]) == "document":
                (begins if name == "begin" else ends).append(start)
        elif name == "title":
            argument = _argument(source, end)
            if argument is None or not _normal(argument[0]):
                errors.append(f"title must have nonempty direct text at line {_line(source, start)}")
            else:
                titles.append((argument[0], start))
        elif name == "maketitle":
            maketitles.append(start)
        elif name in STRUCTURAL:
            position = _skip_space(source, end)
            if position < len(source) and source[position] == "*":
                errors.append(f"starred structural command \\{name} at line {_line(source, start)} is not permitted")
                continue
            if name not in {"section", "subsection"}:
                errors.append(f"structural command \\{name} at line {_line(source, start)} is not permitted")
                continue
            argument = _argument(source, position)
            if argument is None:
                errors.append(f"direct \\{name} command at line {_line(source, start)} needs a title argument")
            else:
                events.append((name, _normal(argument[0]), start))
        elif name == "includegraphics":
            raw, _ = _graphic_path(source, end)
            if raw is None:
                errors.append(f"includegraphics at line {_line(source, start)} needs a literal braced path")
            else:
                figure, figure_error = _validate_figure(raw, report_path, root_path)
                if figure_error:
                    errors.append(f"figure {raw!r} at line {_line(source, start)} {figure_error}")
                else:
                    graphics.append((raw, start, _line(source, start)))

    if documentclasses != 1:
        errors.append("report must contain exactly one direct documentclass command")
    if len(begins) != 1 or len(ends) != 1 or (begins and ends and begins[0] >= ends[0]):
        errors.append("report must contain one ordered begin{document}/end{document} pair")
    if len(titles) != 1:
        errors.append("report must contain exactly one nonempty direct title")
    elif begins and titles[0][1] >= begins[0]:
        errors.append("title must occur before begin{document}")
    if len(maketitles) != 1:
        errors.append("report must contain exactly one direct maketitle command")
    elif not begins or not ends or not begins[0] < maketitles[0] < ends[0]:
        errors.append("maketitle must occur inside the document environment")
    if begins and ends:
        for _, _, position in events:
            if not begins[0] < position < ends[0]:
                errors.append("structural commands must be inside the document environment")
                break

    actual = [(kind, title) for kind, title, position in events]
    if actual != list(EXPECTED):
        errors.append("section and subsection commands do not match the canonical order")
    section7 = next((position for kind, title, position in events if kind == "section" and title == SECTIONS[6]), None)
    section8 = next((position for kind, title, position in events if kind == "section" and title == SECTIONS[7]), None)
    section7_graphics = [raw for raw, position, line in graphics if section7 is not None and section7 < position and (section8 is None or position < section8)]
    if not section7_graphics:
        errors.append("section 7 needs a direct included figure; its spectral content needs manual review")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check canonical LSA LaTeX report structure.")
    parser.add_argument("report", type=Path, metavar="REPORT")
    parser.add_argument("--root", required=True, type=Path, metavar="ANALYSIS_OUTPUT_DIR")
    args = parser.parse_args(argv)
    errors = validate_report(args.report, args.root)
    if errors:
        print("LSA report check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("LSA report check passed: structural paths only; not TeX compilation or scientific validation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
