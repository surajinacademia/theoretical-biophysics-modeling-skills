#!/usr/bin/env python3
"""Render one declared TikZ document to PDF and a path-only SVG artifact.

TeX is executable input. This script is for newly generated or explicitly
trusted source only; its lexical checks are defense in depth, not a TeX parser
or OS sandbox. It snapshots declared inputs before creating an isolated build
directory and publishes validated artifacts through no-symlink atomic replaces.
"""

from __future__ import annotations

import argparse
import os
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple

try:  # ``resource`` is intentionally optional for non-POSIX Python builds.
    import resource
except ImportError:  # pragma: no cover - exercised on platforms without it.
    resource = None  # type: ignore[assignment]


MAX_INPUT_BYTES = 64 * 1024 * 1024
MAX_TOTAL_INPUT_BYTES = 128 * 1024 * 1024
MAX_ARTIFACT_BYTES = 256 * 1024 * 1024
COMPILE_TIMEOUT_SECONDS = 60
CONVERT_TIMEOUT_SECONDS = 60
COPY_CHUNK_BYTES = 1024 * 1024

_TEX_CODE_SUFFIXES = {".tex", ".sty", ".cls", ".def", ".cfg"}
_CONTROL_SEQUENCE = re.compile(r"\\([A-Za-z@]+|.)", re.DOTALL)
_WINDOWS_DRIVE = re.compile(r"^[A-Za-z]:")
_DANGEROUS_EXPL3 = re.compile(
    r"\\(?:"
    r"sys_(?:shell|get_shell)[A-Za-z_:]*"
    r"|shell_escape[A-Za-z_:]*"
    r"|lua_(?:now|exec|shipout)[A-Za-z_:]*"
    r"|(?:file|ior|iow)_(?:input|open|read|write)[A-Za-z_:]*"
    r")",
    re.IGNORECASE,
)
_CSS_URL = re.compile(
    r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE | re.DOTALL
)
_SVG_CSS_PROPERTIES = frozenset(
    "color opacity display visibility fill fill-opacity fill-rule stroke "
    "stroke-width stroke-opacity stroke-dasharray stroke-dashoffset stroke-linecap "
    "stroke-linejoin stroke-miterlimit clip-path clip-rule mask filter marker "
    "marker-start marker-mid marker-end stop-color stop-opacity flood-color "
    "flood-opacity lighting-color color-interpolation color-interpolation-filters "
    "shape-rendering image-rendering vector-effect paint-order".split()
)
_SVG_CSS_FUNCTIONS = frozenset({"url", "rgb", "rgba", "hsl", "hsla"})
_SAFE_OUTPUT_BASENAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
_SAFE_DOCUMENT_CLASSES = frozenset({"article", "minimal", "standalone"})
_SAFE_SYSTEM_PACKAGES = frozenset(
    {
        "amsmath",
        "amssymb",
        "etex",
        "etoolbox",
        "fontenc",
        "fontspec",
        "fourier",
        "graphicx",
        "iftex",
        "ifthen",
        "inputenc",
        "lmodern",
        "mathastext",
        "pgf",
        "pgfplots",
        "preview",
        "tikz",
        "tikz-3dplot",
        "tkz-orm",
        "xcolor",
        "xkeyval",
    }
)
_SAFE_TIKZ_LIBRARIES = frozenset(
    {
        "angles",
        "arrows",
        "arrows.meta",
        "automata",
        "backgrounds",
        "calc",
        "decorations.pathmorphing",
        "decorations.pathreplacing",
        "fadings",
        "fit",
        "intersections",
        "patterns",
        "positioning",
        "quotes",
        "shadings",
        "shadows.blur",
        "shapes.geometric",
    }
)
_SAFE_PGFPLOTS_LIBRARIES = frozenset({"groupplots"})


class RenderError(RuntimeError):
    """Raised for a rejected input or an unsuccessful rendering stage."""


@dataclass(frozen=True)
class DeclaredInput:
    """An immutable snapshot of a declared source or support file."""

    original_path: Path
    name: str
    data: bytes


def _absolute_lexical(path: Path) -> Path:
    """Make a path absolute without resolving a filesystem link."""

    try:
        expanded = path.expanduser()
    except RuntimeError as error:
        raise RenderError("Unable to expand the requested path") from error
    return Path(os.path.abspath(os.fspath(expanded)))


def _directory_flags() -> int:
    """Return flags needed to walk an output/input directory without links."""

    if not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW"):
        raise RenderError("This platform lacks no-symlink directory support")
    return os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


def _open_directory(path: Path, *, create: bool) -> int:
    """Open a directory by component, refusing every symlink in the path."""

    absolute = _absolute_lexical(path)
    flags = _directory_flags()
    try:
        descriptor = os.open(absolute.anchor, flags)
    except OSError as error:
        raise RenderError(f"Cannot safely open directory: {absolute.anchor}") from error

    try:
        for component in absolute.parts[1:]:
            if component in {"", ".", ".."}:
                raise RenderError("Unsafe directory path component")
            try:
                child = os.open(component, flags, dir_fd=descriptor)
            except FileNotFoundError:
                if not create:
                    raise RenderError(f"Directory does not exist: {absolute}") from None
                try:
                    os.mkdir(component, mode=0o755, dir_fd=descriptor)
                except FileExistsError:
                    pass
                try:
                    child = os.open(component, flags, dir_fd=descriptor)
                except OSError as error:
                    raise RenderError(
                        f"Refusing unsafe output path component: {component}"
                    ) from error
            except OSError as error:
                raise RenderError(
                    f"Refusing symlink or non-directory path component: {component}"
                ) from error
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def _read_fd_limited(descriptor: int, limit: int, label: str) -> bytes:
    """Read a regular file descriptor while enforcing a byte limit."""

    chunks: List[bytes] = []
    total = 0
    while True:
        chunk = os.read(descriptor, COPY_CHUNK_BYTES)
        if not chunk:
            break
        total += len(chunk)
        if total > limit:
            raise RenderError(f"{label} exceeds the {limit} byte safety limit")
        chunks.append(chunk)
    return b"".join(chunks)


def _read_declared_regular_file(path: Path, label: str) -> Tuple[Path, bytes]:
    """Snapshot one input only if its path and final object are non-symlinked."""

    absolute = _absolute_lexical(path)
    if not absolute.name or absolute.name in {".", ".."}:
        raise RenderError(f"{label} must name a regular file")

    parent_descriptor = _open_directory(absolute.parent, create=False)
    descriptor: Optional[int] = None
    try:
        if not hasattr(os, "O_NONBLOCK"):
            raise RenderError("This platform lacks nonblocking input support")
        try:
            descriptor = os.open(
                absolute.name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK,
                dir_fd=parent_descriptor,
            )
        except FileNotFoundError:
            raise RenderError(f"{label} does not exist: {absolute}") from None
        except OSError as error:
            raise RenderError(f"{label} must be a non-symlink regular file: {absolute}") from error

        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise RenderError(f"{label} must be a regular file: {absolute}")
        if metadata.st_size > MAX_INPUT_BYTES:
            raise RenderError(
                f"{label} exceeds the {MAX_INPUT_BYTES} byte safety limit: {absolute}"
            )
        return absolute, _read_fd_limited(descriptor, MAX_INPUT_BYTES, label)
    finally:
        if descriptor is not None:
            os.close(descriptor)
        os.close(parent_descriptor)


def _is_tex_code_name(name: str) -> bool:
    return Path(name).suffix.lower() in _TEX_CODE_SUFFIXES


def _load_declared_inputs(source: Path, includes: Sequence[Path]) -> List[DeclaredInput]:
    """Validate and snapshot the source plus each explicitly declared include."""

    source_path, source_data = _read_declared_regular_file(source, "TeX source")
    if source_path.suffix.lower() != ".tex":
        raise RenderError("TeX source must have a .tex suffix")

    declared = [DeclaredInput(source_path, source_path.name, source_data)]
    for include in includes:
        include_path, include_data = _read_declared_regular_file(include, "Declared include")
        declared.append(DeclaredInput(include_path, include_path.name, include_data))

    seen: Dict[str, Path] = {}
    total_bytes = 0
    for item in declared:
        # A flat build directory must be safe on both case-sensitive and
        # case-insensitive filesystems.
        key = item.name.casefold()
        if key in seen:
            raise RenderError(
                "Declared inputs must have unique basenames: "
                f"{seen[key]} and {item.original_path}"
            )
        seen[key] = item.original_path
        total_bytes += len(item.data)
        if total_bytes > MAX_TOTAL_INPUT_BYTES:
            raise RenderError(
                f"Declared inputs exceed the {MAX_TOTAL_INPUT_BYTES} byte safety limit"
            )
        if not item.name or item.name in {".", ".."} or "/" in item.name or "\\" in item.name:
            raise RenderError(f"Unsafe declared input basename: {item.name!r}")
    return declared


def _strip_tex_comments(text: str) -> str:
    """Remove TeX comments while preserving line boundaries for diagnostics."""

    output: List[str] = []
    index = 0
    while index < len(text):
        character = text[index]
        if character == "%":
            preceding_backslashes = 0
            cursor = index - 1
            while cursor >= 0 and text[cursor] == "\\":
                preceding_backslashes += 1
                cursor -= 1
            if preceding_backslashes % 2 == 0:
                while index < len(text) and text[index] not in "\r\n":
                    index += 1
                continue
        output.append(character)
        index += 1
    return "".join(output)


def _skip_space(text: str, index: int) -> int:
    while index < len(text) and text[index].isspace():
        index += 1
    return index


def _read_balanced(text: str, index: int, opening: str, closing: str, label: str) -> Tuple[str, int]:
    """Read one balanced TeX argument, preserving its literal contents."""

    if index >= len(text) or text[index] != opening:
        raise RenderError(f"{label} requires a literal {opening}...{closing} argument")
    depth = 1
    start = index + 1
    index += 1
    while index < len(text):
        character = text[index]
        if character == "\\":
            # A control symbol can quote a brace.  Skipping its next character
            # is enough for argument delimiters; ordinary control words have no
            # delimiters in their names.
            index += 2
            continue
        if character == opening:
            depth += 1
        elif character == closing:
            depth -= 1
            if depth == 0:
                return text[start:index], index + 1
        index += 1
    raise RenderError(f"Unterminated argument for {label}")


def _read_command_argument(
    text: str,
    index: int,
    command: str,
    *,
    allow_bare: bool,
    allow_optional: bool,
    allow_star: bool = False,
) -> Tuple[str, int]:
    """Read the simple literal argument forms allowed for file references."""

    index = _skip_space(text, index)
    if allow_star and index < len(text) and text[index] == "*":
        index = _skip_space(text, index + 1)
    if allow_optional:
        while index < len(text) and text[index] == "[":
            _, index = _read_balanced(text, index, "[", "]", "\\" + command)
            index = _skip_space(text, index)
    if index < len(text) and text[index] == "{":
        return _read_balanced(text, index, "{", "}", "\\" + command)
    if not allow_bare:
        raise RenderError(f"\\{command} requires a literal braced argument")
    if index >= len(text):
        raise RenderError(f"\\{command} requires a literal filename")
    end = index
    while end < len(text) and not text[end].isspace():
        end += 1
    return text[index:end], end


def _reject_path_syntax(value: str, context: str) -> None:
    """Require a literal flat filename rather than a path or a macro value."""

    if not value:
        raise RenderError(f"{context} must not be empty")
    if (
        value.startswith(("/", "\\", "~"))
        or "/" in value
        or "\\" in value
        or _WINDOWS_DRIVE.match(value)
        or value in {".", ".."}
        or any(character in value for character in "\x00{}[]")
    ):
        raise RenderError(f"{context} must not use an absolute, parent, or nested path")
    if any(character.isspace() for character in value.strip(" ")):
        # Spaces are harmless in a declared basename, but TeX's unbraced file
        # argument grammar is not.  A braced argument retains its interior
        # spaces; this check only rejects embedded control whitespace.
        if any(character in "\r\n\t" for character in value):
            raise RenderError(f"{context} must be a literal filename")
    if any(character in value for character in "|`$;&<>'\""):
        raise RenderError(f"{context} contains unsafe filename syntax")


def _resolve_declared_reference(
    value: str,
    allowed_names: Set[str],
    *,
    context: str,
) -> str:
    """Resolve a literal TeX file argument to exactly one declared basename."""

    candidate = value.strip()
    _reject_path_syntax(candidate, context)
    if ".." in candidate.split("/"):
        raise RenderError(f"{context} must not use parent traversal")
    if candidate in allowed_names:
        return candidate

    # TeX commonly permits ``\\input{fragment}`` for a declared
    # ``fragment.tex`` and graphic packages permit extensionless filenames.
    if Path(candidate).suffix:
        matches: List[str] = []
    else:
        matches = [name for name in allowed_names if Path(name).stem == candidate]
    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        raise RenderError(f"{context} is ambiguous among declared input basenames")
    raise RenderError(f"{context} must name one declared support file")


def _validate_package_argument(value: str, command: str, declared_names: Set[str]) -> None:
    """Allow only declared local code or a narrow trusted distribution set."""

    packages = [part.strip() for part in value.split(",")]
    if not packages or any(not package for package in packages):
        raise RenderError(f"\\{command} has an invalid package list")
    for package in packages:
        _reject_path_syntax(package, f"\\{command} package name")
        if any(character.isspace() for character in package):
            raise RenderError(f"\\{command} package names must be literal tokens")
        is_class_command = "class" in command.lower()
        expected_suffix = ".cls" if is_class_command else ".sty"
        local_candidates = {
            name
            for name in declared_names
            if Path(name).suffix.lower() == expected_suffix
            and (name == package or Path(name).stem == package)
        }
        if len(local_candidates) == 1:
            continue
        if len(local_candidates) > 1:
            raise RenderError(f"\\{command} local dependency is ambiguous: {package}")
        allowed = _SAFE_DOCUMENT_CLASSES if is_class_command else _SAFE_SYSTEM_PACKAGES
        if package not in allowed:
            dependency_kind = "document class" if is_class_command else "package"
            raise RenderError(
                f"\\{command} {dependency_kind} is not allowlisted or declared: {package}"
            )


def _validate_library_argument(value: str, command: str) -> None:
    """Restrict TikZ/PGFPlots code-loading helpers to reviewed libraries."""

    libraries = [part.strip() for part in value.split(",")]
    if not libraries or any(not library for library in libraries):
        raise RenderError(f"\\{command} has an invalid library list")
    allowed = (
        _SAFE_TIKZ_LIBRARIES
        if command.lower() == "usetikzlibrary"
        else _SAFE_PGFPLOTS_LIBRARIES
    )
    for library in libraries:
        _reject_path_syntax(library, f"\\{command} library name")
        if any(character.isspace() for character in library) or library not in allowed:
            raise RenderError(f"\\{command} library is not allowlisted: {library}")


def _scan_tex_input(item: DeclaredInput, declared_names: Set[str], code_names: Set[str]) -> None:
    """Reject obvious risky controls in already trusted/generated TeX."""

    try:
        source = item.data.decode("utf-8")
    except UnicodeDecodeError:
        # ASCII TeX control sequences have the same representation in latin-1,
        # which avoids accidentally skipping a dangerous byte sequence.
        source = item.data.decode("latin-1")
    source = _strip_tex_comments(source)

    if _DANGEROUS_EXPL3.search(source):
        raise RenderError(f"{item.name} contains a forbidden shell or Lua primitive")

    dangerous_exact = {
        "catcode",
        "csname",
        "directlua",
        "latelua",
        "luaexec",
        "luadirect",
        "luafunction",
        "luabytecode",
        "newluafunction",
        "openin",
        "openout",
        "read",
        "readline",
        "newread",
        "newwrite",
        "shellescape",
        "pdfshellescape",
    }
    blocked_imports = {
        "catchfile",
        "catchfiledef",
        "externaldocument",
        "graphicspath",
        "import",
        "includeanimated",
        "includeanimation",
        "includemedia",
        "inputfrom",
        "inputminted",
        "includefrom",
        "bibliographystyle",
        "pgfdeclareimage",
        "pgfimage",
        "subimport",
        "usepgflibrary",
        "usepgfmodule",
        "verbatiminput",
    }
    input_commands = {"input", "@input", "@@input", "include"}
    simple_file_commands = {
        "addbibresource",
        "bibliography",
        "includegraphics",
        "includepdf",
        "lstinputlisting",
    }
    package_commands = {
        "documentclass",
        "loadclass",
        "loadclasswithoptions",
        "requirepackage",
        "requirepackagewithoptions",
        "usepackage",
    }
    library_commands = {"usetikzlibrary", "usepgfplotslibrary"}

    for match in _CONTROL_SEQUENCE.finditer(source):
        command = match.group(1)
        lower_command = command.lower()
        location = f"{item.name}: \\{command}"

        if (
            lower_command in dangerous_exact
            or lower_command.startswith(("catcode", "read", "write"))
            or "csname" in lower_command
            or "write" in lower_command
            or lower_command in {"lua", "luanow"}
            or "shell" in lower_command
        ):
            raise RenderError(f"{location} is a forbidden TeX primitive")
        if lower_command in blocked_imports:
            raise RenderError(f"{location} is not allowed in isolated rendering")

        if lower_command in input_commands:
            argument, _ = _read_command_argument(
                source,
                match.end(),
                command,
                allow_bare=True,
                allow_optional=False,
            )
            _resolve_declared_reference(argument, code_names, context=location)
        elif lower_command in simple_file_commands:
            argument, _ = _read_command_argument(
                source,
                match.end(),
                command,
                allow_bare=False,
                allow_optional=lower_command
                in {"includegraphics", "includepdf", "lstinputlisting"},
                allow_star=lower_command == "includegraphics",
            )
            if lower_command == "bibliography":
                for bibliography in argument.split(","):
                    _resolve_declared_reference(
                        bibliography, declared_names, context=location
                    )
            else:
                _resolve_declared_reference(argument, declared_names, context=location)
        elif lower_command in package_commands:
            argument, _ = _read_command_argument(
                source,
                match.end(),
                command,
                allow_bare=False,
                allow_optional=True,
            )
            _validate_package_argument(argument, command, declared_names)
        elif lower_command in library_commands:
            argument, _ = _read_command_argument(
                source,
                match.end(),
                command,
                allow_bare=False,
                allow_optional=False,
            )
            _validate_library_argument(argument, command)
        elif "fileexists" in lower_command or (
            ("input" in lower_command or "include" in lower_command)
            and lower_command
            not in {
                "endinput",
                "includegraphics",
                "includepdf",
            }
        ):
            raise RenderError(f"{location} is not allowed in isolated rendering")


def _scan_declared_inputs(declared: Sequence[DeclaredInput]) -> None:
    """Scan source and every copied TeX-like support file before compilation."""

    declared_names = {item.name for item in declared}
    code_names = {item.name for item in declared if _is_tex_code_name(item.name)}
    for item in declared:
        if _is_tex_code_name(item.name):
            _scan_tex_input(item, declared_names, code_names)


def _resolve_executable(command: str) -> str:
    """Resolve an executable before the temporary build directory is entered."""

    located = shutil.which(command)
    if not located:
        raise RenderError(f"Required executable is not available on PATH: {command}")
    try:
        resolved = Path(located).resolve(strict=True)
    except OSError as error:
        raise RenderError(f"Cannot resolve required executable: {command}") from error
    if not resolved.is_file() or not os.access(os.fspath(resolved), os.X_OK):
        raise RenderError(f"Required executable is not runnable: {resolved}")
    return os.fspath(resolved)


def _resolve_optional_executable(command: str) -> Optional[str]:
    """Resolve an optional fallback executable without making it a prerequisite."""

    if not shutil.which(command):
        return None
    return _resolve_executable(command)


def _prepare_output_directory(path: Path) -> Path:
    """Create/validate a no-symlink output directory and return its lexical path."""

    output = _absolute_lexical(path)
    descriptor = _open_directory(output, create=True)
    os.close(descriptor)
    return output


def _validate_output_basename(value: str) -> str:
    """Require one extensionless, shell-safe TeX jobname/output basename."""

    if not _SAFE_OUTPUT_BASENAME.fullmatch(value):
        raise RenderError(
            "Output basename must be an extensionless ASCII jobname containing "
            "only letters, digits, underscores, or hyphens"
        )
    return value


def _validate_artifact_name(value: str) -> str:
    """Require the derived PDF/SVG filename for one previously safe basename."""

    path = Path(value)
    if path.name != value or path.suffix not in {".pdf", ".svg"}:
        raise RenderError("Output artifact must be one derived .pdf or .svg filename")
    basename = value[: -len(path.suffix)]
    _validate_output_basename(basename)
    return value


def _write_all(descriptor: int, data: bytes) -> None:
    view = memoryview(data)
    offset = 0
    while offset < len(view):
        written = os.write(descriptor, view[offset:])
        if written <= 0:
            raise RenderError("Unable to write output data")
        offset += written


def _copy_declared_inputs(declared: Sequence[DeclaredInput], build_directory: Path) -> None:
    """Populate a fresh build directory with only the snapshotted declarations."""

    for item in declared:
        destination = build_directory / item.name
        descriptor: Optional[int] = None
        try:
            descriptor = os.open(
                os.fspath(destination),
                os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                0o600,
            )
            _write_all(descriptor, item.data)
            os.fsync(descriptor)
        except OSError as error:
            raise RenderError(f"Cannot copy declared input into isolated build: {item.name}") from error
        finally:
            if descriptor is not None:
                os.close(descriptor)


def _lower_resource_limit(limit: int, desired: int) -> None:
    """Lower one inherited POSIX limit when the host exposes it."""

    if resource is None:
        return
    try:
        current_soft, current_hard = resource.getrlimit(limit)
        target = desired
        if current_hard != resource.RLIM_INFINITY:
            target = min(target, current_hard)
        if current_soft == resource.RLIM_INFINITY or current_soft > target:
            resource.setrlimit(limit, (target, current_hard))
    except (OSError, ValueError):
        # A host may expose a constant but not permit this particular limit.
        # ``subprocess.run(timeout=...)`` remains an unconditional bound.
        return


def _resource_preexec(timeout: int) -> Optional[Callable[[], None]]:
    """Build a POSIX child hook for CPU, file-size, memory, and FD limits."""

    if resource is None or os.name != "posix":
        return None

    # Current macOS LuaTeX fails while initializing an isolated font cache if
    # any inherited rlimit is tightened in a Python ``preexec_fn``.  The
    # unconditional subprocess timeout remains in force there.  Linux supports
    # the fuller CPU/memory/file/descriptor limits without that regression.
    if not sys.platform.startswith("linux"):
        return None
    limits: List[Tuple[str, int]] = [
        ("RLIMIT_CPU", timeout + 5),
        ("RLIMIT_FSIZE", MAX_ARTIFACT_BYTES),
        ("RLIMIT_AS", 4 * 1024 * 1024 * 1024),
        ("RLIMIT_NOFILE", 128),
    ]

    def apply_limits() -> None:
        for name, desired in limits:
            limit = getattr(resource, name, None)
            if limit is not None:
                _lower_resource_limit(limit, desired)

    return apply_limits


def _isolated_tex_environment(
    build_directory: Path,
    executables: Sequence[str],
) -> Dict[str, str]:
    """Build a fresh non-secret environment with isolated TeX/cache paths."""

    texmf_var = build_directory / "texmf-var"
    texmf_var.mkdir(mode=0o700, exist_ok=True)
    temporary_root = build_directory / "tmp"
    temporary_root.mkdir(mode=0o700, exist_ok=True)
    xdg_cache = build_directory / "xdg-cache"
    xdg_config = build_directory / "xdg-config"
    xdg_data = build_directory / "xdg-data"
    for directory in (xdg_cache, xdg_config, xdg_data):
        directory.mkdir(mode=0o700, exist_ok=True)

    tool_directories = [os.fspath(Path(executable).parent) for executable in executables]
    tool_directories.extend(("/usr/bin", "/bin", "/usr/sbin", "/sbin"))
    trusted_path = os.pathsep.join(dict.fromkeys(tool_directories))
    environment = {
        "PATH": trusted_path,
        "LANG": "C",
        "LC_ALL": "C",
        "TMPDIR": os.fspath(temporary_root),
        "XDG_CACHE_HOME": os.fspath(xdg_cache),
        "XDG_CONFIG_HOME": os.fspath(xdg_config),
        "XDG_DATA_HOME": os.fspath(xdg_data),
    }

    # The trailing path separator appends the TeX distribution's trusted
    # defaults.  An exclamation mark disables user TEXMF home/config/output
    # trees. LuaTeX may build a font cache only inside this fresh directory.
    # The restricted open-in policy is the strongest setting compatible with
    # current LuaTeX cache initialization on macOS. The preflight scanner also
    # rejects obvious literal input primitives, but is not a TeX sandbox.
    environment["TEXINPUTS"] = "." + os.pathsep
    environment["TEXMFHOME"] = "!"
    environment["TEXMFVAR"] = os.fspath(texmf_var)
    environment["TEXMFCONFIG"] = "!"
    environment["TEXMFOUTPUT"] = "!"
    environment["openin_any"] = "r"
    environment["openout_any"] = "p"
    return environment


def _run_checked(
    command: Sequence[str],
    *,
    build_directory: Path,
    environment: Dict[str, str],
    timeout: int,
    stage: str,
) -> None:
    """Run a resolved renderer with noninteractive, bounded process execution."""

    try:
        completed = subprocess.run(
            list(command),
            cwd=os.fspath(build_directory),
            env=environment,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=timeout,
            check=False,
            close_fds=True,
            preexec_fn=_resource_preexec(timeout),
        )
    except subprocess.TimeoutExpired as error:
        raise RenderError(f"{stage} exceeded the {timeout} second timeout") from error
    except OSError as error:
        raise RenderError(f"Unable to start {stage}") from error
    if completed.returncode != 0:
        raise RenderError(f"{stage} failed with exit status {completed.returncode}")


def _read_build_artifact(path: Path, label: str) -> bytes:
    """Read a compiler artifact only if it is a bounded regular non-symlink file."""

    try:
        metadata = os.lstat(os.fspath(path))
    except FileNotFoundError:
        raise RenderError(f"{label} was not produced") from None
    if not stat.S_ISREG(metadata.st_mode):
        raise RenderError(f"{label} must be a regular non-symlink file")
    if metadata.st_size <= 0:
        raise RenderError(f"{label} is empty")
    if metadata.st_size > MAX_ARTIFACT_BYTES:
        raise RenderError(f"{label} exceeds the {MAX_ARTIFACT_BYTES} byte safety limit")

    descriptor: Optional[int] = None
    try:
        descriptor = os.open(os.fspath(path), os.O_RDONLY | os.O_NOFOLLOW)
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode):
            raise RenderError(f"{label} must be a regular non-symlink file")
        return _read_fd_limited(descriptor, MAX_ARTIFACT_BYTES, label)
    except OSError as error:
        raise RenderError(f"Cannot safely read {label}") from error
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _remove_build_entry(path: Path, label: str) -> None:
    """Remove one failed converter output inside the private build directory."""

    try:
        metadata = os.lstat(os.fspath(path))
    except FileNotFoundError:
        return
    if stat.S_ISDIR(metadata.st_mode):
        raise RenderError(f"{label} unexpectedly created a directory")
    try:
        os.unlink(os.fspath(path))
    except OSError as error:
        raise RenderError(f"Cannot remove failed {label}") from error


def _xml_local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1].lower()


def _validate_svg_uri(value: str, *, is_image: bool, context: str) -> None:
    """Permit local fragments and safe embedded raster image data only."""

    reference = value.strip()
    lower_reference = reference.lower()
    if reference.startswith("#"):
        return
    if is_image and lower_reference.startswith("data:image/"):
        media_type = lower_reference[5:].split(";", 1)[0].split(",", 1)[0]
        if media_type in {"image/png", "image/jpeg", "image/gif", "image/webp", "image/avif"}:
            return
    raise RenderError(f"SVG contains an external or unsafe file reference in {context}")


def _validate_svg_url_functions(value: str, context: str) -> None:
    """Reject CSS url(...) references except local SVG fragments."""

    if "url(" not in value.lower():
        return
    matches = list(_CSS_URL.finditer(value))
    if not matches or "url(" in _CSS_URL.sub("", value).lower():
        raise RenderError(f"SVG contains an unparsable URL reference in {context}")
    for match in matches:
        _validate_svg_uri(match.group(2), is_image=False, context=context)


def _validate_svg_css_syntax(value: str, context: str) -> None:
    """Accept plain generated CSS, rejecting escape/comment obfuscation."""

    if "\\" in value or "/*" in value or "*/" in value or "@" in value:
        raise RenderError(f"SVG contains unsupported CSS syntax in {context}")


def _validate_svg_css_value(value: str, context: str) -> None:
    _validate_svg_css_syntax(value, context)
    _validate_svg_url_functions(value, context)
    functions = re.findall(r"([A-Za-z_-][A-Za-z0-9_-]*)\s*\(", value)
    if any(name.lower() not in _SVG_CSS_FUNCTIONS for name in functions):
        raise RenderError(f"SVG contains an unsupported CSS function in {context}")


def _validate_svg_css_declarations(value: str, context: str) -> None:
    """Allow only static SVG paint properties, never resource-bearing CSS extensions."""

    _validate_svg_css_syntax(value, context)
    for declaration in value.split(";"):
        if not declaration.strip():
            continue
        name, separator, contents = declaration.partition(":")
        if not separator or name.strip().lower() not in _SVG_CSS_PROPERTIES:
            raise RenderError(f"SVG contains an unsupported CSS property in {context}")
        _validate_svg_css_value(contents, context)


def _validate_svg_stylesheet(value: str) -> None:
    """Validate flat static style rules emitted by figure renderers."""

    _validate_svg_css_syntax(value, "<style>")
    cursor = 0
    for rule in re.finditer(r"([^{}]+)\{([^{}]*)\}", value):
        if value[cursor:rule.start()].strip() or not rule.group(1).strip():
            raise RenderError("SVG contains an unsupported stylesheet rule")
        _validate_svg_css_declarations(rule.group(2), "<style>")
        cursor = rule.end()
    if value[cursor:].strip():
        raise RenderError("SVG contains an unsupported stylesheet rule")


def _validate_svg(svg_data: bytes) -> None:
    """Require SVG glyph geometry rather than text, fonts, scripts, or links."""

    try:
        raw_svg = svg_data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RenderError("SVG is not valid UTF-8 XML") from error
    # Expat can autodetect BOM-less UTF-16/32 in the original bytes. Reject
    # controls that are invalid in decoded UTF-8 XML so lexical checks and the
    # XML parser cannot see different markup (notably stylesheet PIs).
    if any(ord(character) < 0x20 and character not in "\t\r\n" for character in raw_svg):
        raise RenderError("SVG contains invalid UTF-8 XML control characters")
    declaration = re.match(r"\ufeff?<\?xml\s+([^?]*)\?>", raw_svg, re.IGNORECASE)
    if declaration:
        encoding = re.search(r"\bencoding\s*=\s*(['\"])(.*?)\1", declaration.group(1), re.IGNORECASE)
        if encoding and encoding.group(2).lower() not in {"utf-8", "utf8"}:
            raise RenderError("SVG must declare UTF-8 XML encoding")
    lowered = raw_svg.lower()
    if "<!doctype" in lowered or "<!entity" in lowered:
        raise RenderError("SVG must not contain a DTD or entity declaration")
    if "<?xml-stylesheet" in lowered:
        raise RenderError("SVG must not load an external stylesheet")
    if "<script" in lowered or "@font-face" in lowered or "font-family" in lowered:
        raise RenderError("SVG contains forbidden script or font content")
    if "@import" in lowered or "javascript:" in lowered:
        raise RenderError("SVG contains a forbidden external reference")

    try:
        root = ElementTree.fromstring(svg_data)
    except ElementTree.ParseError as error:
        raise RenderError("SVG converter did not produce well-formed SVG") from error
    if _xml_local_name(root.tag) != "svg":
        raise RenderError("Converted artifact is not an SVG document")

    forbidden_elements = {
        "animate",
        "animatecolor",
        "animatemotion",
        "animatetransform",
        "audio",
        "discard",
        "embed",
        "font",
        "font-face",
        "foreignobject",
        "iframe",
        "object",
        "script",
        "set",
        "text",
        "tspan",
        "textpath",
        "video",
    }
    for element in root.iter():
        element_name = _xml_local_name(element.tag)
        if element_name in forbidden_elements:
            raise RenderError(f"SVG contains forbidden <{element_name}> content")
        if element_name == "style":
            style_text = "".join(element.itertext())
            _validate_svg_stylesheet(style_text)

        for attribute, value in element.attrib.items():
            attribute_name = _xml_local_name(attribute)
            context = f"<{element_name}> @{attribute_name}"
            if attribute_name in {"font", "font-family", "base"}:
                raise RenderError("SVG contains forbidden font or base attributes")
            if attribute_name.startswith("on"):
                raise RenderError("SVG contains an event-handler attribute")
            if attribute_name in {"data", "href", "src"}:
                _validate_svg_uri(value, is_image=element_name == "image", context=context)
            if attribute_name == "style":
                _validate_svg_css_declarations(value, context)
            elif attribute_name in _SVG_CSS_PROPERTIES or attribute_name in {"cursor", "color-profile"}:
                _validate_svg_css_value(value, context)
            _validate_svg_url_functions(value, context)
            if "javascript:" in value.lower():
                raise RenderError("SVG contains a JavaScript reference")


def _convert_pdf_to_svg(
    *,
    dvisvgm: Optional[str],
    pdf2svg: Optional[str],
    build_pdf: Path,
    build_svg: Path,
    build_directory: Path,
    environment: Dict[str, str],
) -> bytes:
    """Prefer dvisvgm outlines, with validated pdf2svg fallback when necessary."""

    dvisvgm_error: Optional[RenderError] = None
    if dvisvgm is not None:
        try:
            _remove_build_entry(build_svg, "previous SVG output")
            _run_checked(
                [
                    dvisvgm,
                    "--pdf",
                    "--no-fonts",
                    "--output=" + os.fspath(build_svg),
                    os.fspath(build_pdf),
                ],
                build_directory=build_directory,
                environment=environment,
                timeout=CONVERT_TIMEOUT_SECONDS,
                stage="dvisvgm conversion",
            )
            svg_data = _read_build_artifact(build_svg, "Converted SVG")
            _validate_svg(svg_data)
            return svg_data
        except RenderError as error:
            dvisvgm_error = error

    if pdf2svg is None:
        raise RenderError(
            "No usable PDF-to-SVG converter is available; install dvisvgm or pdf2svg"
        ) from dvisvgm_error

    try:
        _remove_build_entry(build_svg, "failed dvisvgm SVG output")
        _run_checked(
            [pdf2svg, os.fspath(build_pdf), os.fspath(build_svg)],
            build_directory=build_directory,
            environment=environment,
            timeout=CONVERT_TIMEOUT_SECONDS,
            stage="pdf2svg fallback conversion",
        )
        svg_data = _read_build_artifact(build_svg, "Fallback SVG")
        _validate_svg(svg_data)
    except RenderError as error:
        raise RenderError(
            "dvisvgm conversion failed and pdf2svg fallback conversion failed"
        ) from error

    if dvisvgm is None:
        print("render_tikz.py: used validated pdf2svg converter", file=sys.stderr)
    else:
        print("render_tikz.py: dvisvgm failed; used validated pdf2svg fallback", file=sys.stderr)
    return svg_data


def _assert_replaceable_output(parent_descriptor: int, name: str) -> None:
    try:
        existing = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return
    if not stat.S_ISREG(existing.st_mode):
        raise RenderError(f"Refusing unsafe existing output file: {name}")


def _copy_artifact_atomic(source: Path, output_directory: Path, name: str) -> Path:
    """Copy one validated temporary artifact through a no-symlink atomic replace."""

    _validate_artifact_name(name)
    parent_descriptor = _open_directory(output_directory, create=False)
    source_descriptor: Optional[int] = None
    temporary_descriptor: Optional[int] = None
    temporary_name = "." + name + "." + secrets.token_hex(12) + ".tmp"
    try:
        _assert_replaceable_output(parent_descriptor, name)
        try:
            source_descriptor = os.open(os.fspath(source), os.O_RDONLY | os.O_NOFOLLOW)
            source_metadata = os.fstat(source_descriptor)
        except OSError as error:
            raise RenderError(f"Cannot safely read generated artifact: {source.name}") from error
        if not stat.S_ISREG(source_metadata.st_mode):
            raise RenderError(f"Generated artifact is not a regular file: {source.name}")

        temporary_descriptor = os.open(
            temporary_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=parent_descriptor,
        )
        while True:
            chunk = os.read(source_descriptor, COPY_CHUNK_BYTES)
            if not chunk:
                break
            _write_all(temporary_descriptor, chunk)
        os.fchmod(temporary_descriptor, 0o644)
        os.fsync(temporary_descriptor)
        os.close(temporary_descriptor)
        temporary_descriptor = None
        os.replace(
            temporary_name,
            name,
            src_dir_fd=parent_descriptor,
            dst_dir_fd=parent_descriptor,
        )
        try:
            os.fsync(parent_descriptor)
        except OSError:
            # Some filesystems do not permit fsync on a directory.  The rename
            # remains atomic even when durability cannot be requested here.
            pass
    except OSError as error:
        raise RenderError(f"Cannot atomically publish output artifact: {name}") from error
    finally:
        if temporary_descriptor is not None:
            os.close(temporary_descriptor)
        if source_descriptor is not None:
            os.close(source_descriptor)
        try:
            os.unlink(temporary_name, dir_fd=parent_descriptor)
        except FileNotFoundError:
            pass
        finally:
            os.close(parent_descriptor)
    return output_directory / name


def _render(
    source: Path,
    output_directory: Path,
    basename: Optional[str],
    engine: str,
    includes: Sequence[Path],
) -> Tuple[Path, Path]:
    """Execute the complete isolated render pipeline and return final artifacts."""

    declared = _load_declared_inputs(source, includes)
    _scan_declared_inputs(declared)

    output_base = _validate_output_basename(basename or declared[0].original_path.stem)

    # Resolve the compiler, primary converter, and optional fallback before a
    # temporary directory is created or used as the working directory for TeX.
    compiler = _resolve_executable(engine)
    dvisvgm = _resolve_optional_executable("dvisvgm")
    pdf2svg = _resolve_optional_executable("pdf2svg")
    if dvisvgm is None and pdf2svg is None:
        raise RenderError("Required converter is unavailable: install dvisvgm or pdf2svg")
    ghostscript = _resolve_optional_executable("gs")
    approved_output = _prepare_output_directory(output_directory)

    with tempfile.TemporaryDirectory(prefix="render-tikz-") as temporary:
        build_directory = Path(temporary)
        _copy_declared_inputs(declared, build_directory)
        environment = _isolated_tex_environment(
            build_directory,
            [
                executable
                for executable in (compiler, dvisvgm, pdf2svg, ghostscript)
                if executable is not None
            ],
        )

        compile_command = [
            compiler,
            "-fmt=" + engine,
            "-no-shell-escape",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-file-line-error",
            "-output-directory=" + os.fspath(build_directory),
            "-jobname=" + output_base,
            declared[0].name,
        ]
        for pass_number in (1, 2):
            _run_checked(
                compile_command,
                build_directory=build_directory,
                environment=environment,
                timeout=COMPILE_TIMEOUT_SECONDS,
                stage=f"{engine} compile pass {pass_number}",
            )

        build_pdf = build_directory / (output_base + ".pdf")
        _read_build_artifact(build_pdf, "Compiled PDF")
        build_svg = build_directory / (output_base + ".svg")
        _convert_pdf_to_svg(
            dvisvgm=dvisvgm,
            pdf2svg=pdf2svg,
            build_pdf=build_pdf,
            build_svg=build_svg,
            build_directory=build_directory,
            environment=environment,
        )

        final_pdf = _copy_artifact_atomic(
            build_pdf, approved_output, output_base + ".pdf"
        )
        final_svg = _copy_artifact_atomic(
            build_svg, approved_output, output_base + ".svg"
        )
    return final_pdf, final_svg


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compile one trusted/generated TikZ source twice and export "
            "PDF plus a path-only SVG artifact."
        )
    )
    parser.add_argument(
        "source", type=Path, help="trusted/generated regular non-symlink .tex source"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="directory in which basename.pdf and basename.svg are atomically published",
    )
    parser.add_argument(
        "--basename",
        help="output basename (defaults to the source filename without .tex)",
    )
    parser.add_argument(
        "--engine",
        choices=("lualatex", "pdflatex"),
        default="lualatex",
        help="trusted TeX engine to invoke (default: lualatex)",
    )
    parser.add_argument(
        "--include",
        type=Path,
        action="append",
        default=[],
        help="declared regular non-symlink support file; may be repeated",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = _build_parser()
    arguments = parser.parse_args(argv)
    try:
        pdf_path, svg_path = _render(
            arguments.source,
            arguments.output_dir,
            arguments.basename,
            arguments.engine,
            arguments.include,
        )
    except RenderError as error:
        parser.exit(1, f"{parser.prog}: error: {error}\n")
    print(pdf_path)
    print(svg_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
