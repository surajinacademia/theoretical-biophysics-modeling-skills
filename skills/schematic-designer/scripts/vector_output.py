"""Safe PDF/SVG output helpers for schematic-designer Matplotlib specimens.

The public contract is deliberately narrow: final figures are a PDF plus an
SVG whose glyphs are paths.  No raster preview is written by this module.
"""

from __future__ import annotations

import importlib.util
import os
import re
import secrets
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any, BinaryIO, Mapping


_SVG_DOCTYPE = re.compile(br"<!DOCTYPE\s+svg\b[^>]*>\s*", re.IGNORECASE | re.DOTALL)


def _tikz_renderer():
    """Load the shared SVG validator and contained PDF converter once."""
    module_name = "_schematic_tikz_renderer"
    if module_name not in sys.modules:
        path = Path(__file__).resolve().with_name("render_tikz.py")
        spec = importlib.util.spec_from_file_location(module_name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return sys.modules[module_name]


def _normalize_svg_bytes(payload: bytes) -> bytes:
    """Remove Matplotlib's legacy external SVG DTD declaration."""
    normalized = _SVG_DOCTYPE.sub(b"", payload, count=1)
    if b"<!DOCTYPE" in normalized.upper() or b"<!ENTITY" in normalized.upper():
        raise RuntimeError("Generated SVG contains a DTD or entity declaration")
    _tikz_renderer()._validate_svg(normalized)
    return normalized


def _absolute_lexical(path: Path) -> Path:
    """Return an absolute path without following any filesystem links."""
    return Path(os.path.abspath(path.expanduser()))


def _open_directory(path: Path, *, create: bool) -> int:
    """Open a directory by walking each component without following links."""
    if not hasattr(os, "O_DIRECTORY") or not hasattr(os, "O_NOFOLLOW"):
        raise RuntimeError("Safe output requires directory no-follow support")

    absolute = _absolute_lexical(path)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    descriptor = os.open(absolute.anchor, flags)
    try:
        for part in absolute.parts[1:]:
            try:
                child = os.open(part, flags, dir_fd=descriptor)
            except FileNotFoundError:
                if not create:
                    raise RuntimeError(f"Output directory does not exist: {part}") from None
                os.mkdir(part, mode=0o755, dir_fd=descriptor)
                child = os.open(part, flags, dir_fd=descriptor)
            except OSError as error:
                raise RuntimeError(
                    f"Refusing unsafe output path component: {part}"
                ) from error
            os.close(descriptor)
            descriptor = child
        return descriptor
    except BaseException:
        os.close(descriptor)
        raise


def prepare_output_directory(requested: Path) -> Path:
    """Create an output directory without following any symlink component."""
    output = _absolute_lexical(requested)
    descriptor = _open_directory(output, create=True)
    os.close(descriptor)
    return output


def _check_output_target(parent_descriptor: int, name: str) -> None:
    """Reject an existing destination that is not a regular file."""
    try:
        target = os.stat(name, dir_fd=parent_descriptor, follow_symlinks=False)
    except FileNotFoundError:
        return
    if not stat.S_ISREG(target.st_mode):
        raise RuntimeError(f"Refusing unsafe output file: {name}")


def _validate_pdf_stream(stream: BinaryIO, name: str | Path) -> None:
    """Apply the PDF header and size checks to an already-open file."""
    stream.seek(0)
    if stream.read(5) != b"%PDF-" or os.fstat(stream.fileno()).st_size < 100:
        raise RuntimeError(f"Invalid PDF output: {name}")


def publish_bytes_atomic(
    payload: bytes, approved_directory: Path, destination_name: str
) -> None:
    """Publish bytes from private staging, anchored to the opened output directory.

    The staging directory is owner-only, and all file operations use its retained
    descriptor, so replacing its public name cannot substitute the staged bytes.
    """
    destination = Path(destination_name)
    if (destination.is_absolute() or len(destination.parts) != 1
            or destination.name in {"", ".", ".."}):
        raise RuntimeError("Output destination must be one contained basename")
    parent = _open_directory(approved_directory, create=False)
    stage_name = f".publish-{secrets.token_hex(16)}"
    stage = None
    created = False
    try:
        _check_output_target(parent, destination.name)
        os.mkdir(stage_name, mode=0o700, dir_fd=parent)
        created = True
        stage = os.open(stage_name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                        dir_fd=parent)
        info = os.fstat(stage)
        if info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) & 0o077:
            raise RuntimeError("Unsafe publication staging directory")
        descriptor = os.open("payload", os.O_WRONLY | os.O_CREAT | os.O_EXCL
                             | os.O_NOFOLLOW, 0o600, dir_fd=stage)
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        _check_output_target(parent, destination.name)
        os.replace("payload", destination.name, src_dir_fd=stage, dst_dir_fd=parent)
    finally:
        try:
            if stage is not None:
                try:
                    os.unlink("payload", dir_fd=stage)
                except FileNotFoundError:
                    pass
                finally:
                    os.close(stage)
            if created:
                try:
                    os.rmdir(stage_name, dir_fd=parent)
                except (FileNotFoundError, NotADirectoryError):
                    pass
        finally:
            os.close(parent)


def _stage_figure(
    figure: Any,
    parent_descriptor: int,
    destination: Path,
    options: Mapping[str, Any],
) -> str:
    """Render and check one temporary file without replacing its destination."""
    temporary_name = (
        f".{destination.stem}.{secrets.token_hex(12)}{destination.suffix}"
    )
    temporary_descriptor: int | None = None
    created = False
    try:
        temporary_descriptor = os.open(
            temporary_name,
            os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=parent_descriptor,
        )
        created = True
        save_options = dict(options)
        if destination.suffix and "format" not in save_options:
            save_options["format"] = destination.suffix.removeprefix(".")
        with os.fdopen(temporary_descriptor, "w+b") as temporary_file:
            temporary_descriptor = None
            if destination.suffix.lower() == ".svg":
                import matplotlib

                with matplotlib.rc_context(
                    {"svg.fonttype": "path", "svg.image_inline": True}
                ):
                    figure.savefig(temporary_file, **save_options)
            else:
                figure.savefig(temporary_file, **save_options)
            if destination.suffix.lower() == ".svg":
                temporary_file.flush()
                temporary_file.seek(0)
                normalized = _normalize_svg_bytes(temporary_file.read())
                temporary_file.seek(0)
                temporary_file.truncate()
                temporary_file.write(normalized)
            temporary_file.flush()
            if destination.suffix.lower() == ".pdf":
                _validate_pdf_stream(temporary_file, destination.name)
            os.fsync(temporary_file.fileno())
        return temporary_name
    except BaseException:
        if temporary_descriptor is not None:
            os.close(temporary_descriptor)
        if created:
            try:
                os.unlink(temporary_name, dir_fd=parent_descriptor)
            except FileNotFoundError:
                pass
        raise


def save_figure_atomic(
    figure: Any,
    approved_directory: Path,
    destination_name: str | Path,
    **kwargs: Any,
) -> None:
    """Render one basename inside an approved directory and replace it atomically."""
    destination = Path(destination_name)
    if destination.is_absolute() or len(destination.parts) != 1:
        raise RuntimeError("Output destination must be one contained basename")
    if destination.name in {"", ".", ".."}:
        raise RuntimeError("Output destination basename is invalid")

    parent_descriptor = _open_directory(approved_directory, create=False)
    temporary_name: str | None = None
    try:
        _check_output_target(parent_descriptor, destination.name)
        temporary_name = _stage_figure(figure, parent_descriptor, destination, kwargs)
        _check_output_target(parent_descriptor, destination.name)
        os.replace(
            temporary_name,
            destination.name,
            src_dir_fd=parent_descriptor,
            dst_dir_fd=parent_descriptor,
        )
    finally:
        try:
            if temporary_name is not None:
                try:
                    os.unlink(temporary_name, dir_fd=parent_descriptor)
                except FileNotFoundError:
                    pass
        finally:
            os.close(parent_descriptor)


def configure_matplotlib_vector_output() -> None:
    """Configure Matplotlib so SVG glyphs are emitted as vector paths."""
    import matplotlib

    matplotlib.rcParams.update(
        {
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "svg.fonttype": "path",
            "svg.image_inline": True,
            "savefig.transparent": False,
        }
    )


def validate_outlined_svg(path: Path) -> None:
    """Reject SVG content that can trigger font substitution in an editor."""
    _tikz_renderer()._validate_svg(path.read_bytes())


def validate_pdf(path: Path) -> None:
    """Check that a rendered file has a non-empty PDF header."""
    with path.open("rb") as handle:
        _validate_pdf_stream(handle, path)


def save_vector_pair(
    figure: Any,
    approved_directory: Path,
    basename: str,
    *,
    common_options: Mapping[str, Any] | None = None,
    pdf_options: Mapping[str, Any] | None = None,
    svg_options: Mapping[str, Any] | None = None,
) -> tuple[Path, Path]:
    """Stage and check both formats before replacing either final file.

    Each replacement is atomic; the two replacements are not one transaction.
    """
    if not basename or Path(basename).name != basename or Path(basename).suffix:
        raise RuntimeError("Output basename must be one extension-free filename")

    output_directory = prepare_output_directory(approved_directory)
    shared = dict(common_options or {})
    pdf_path = output_directory / f"{basename}.pdf"
    svg_path = output_directory / f"{basename}.svg"

    configure_matplotlib_vector_output()
    parent_descriptor = _open_directory(output_directory, create=False)
    staged: list[tuple[str, str]] = []
    try:
        for destination in (pdf_path, svg_path):
            _check_output_target(parent_descriptor, destination.name)
        pgf = "backend_pgf" in type(getattr(figure, "canvas", None)).__module__
        if pgf and svg_options:
            raise ValueError("PGF SVG is converted from the PDF; use common/PDF options")
        destinations = [(pdf_path, shared | dict(pdf_options or {}))]
        if not pgf:
            destinations.append((svg_path, shared | dict(svg_options or {})))
        for destination, options in destinations:
            temporary_name = _stage_figure(
                figure, parent_descriptor, destination, options
            )
            staged.append((temporary_name, destination.name))
        if pgf:
            temporary_name = _stage_svg_from_pdf(parent_descriptor, staged[0][0])
            staged.append((temporary_name, svg_path.name))
        for _, name in staged:
            _check_output_target(parent_descriptor, name)
        for temporary_name, name in staged:
            os.replace(
                temporary_name,
                name,
                src_dir_fd=parent_descriptor,
                dst_dir_fd=parent_descriptor,
            )
    finally:
        try:
            for temporary_name, _ in staged:
                try:
                    os.unlink(temporary_name, dir_fd=parent_descriptor)
                except FileNotFoundError:
                    pass
        finally:
            os.close(parent_descriptor)
    return pdf_path, svg_path


def _stage_svg_from_pdf(parent_descriptor: int, pdf_name: str) -> str:
    """Reuse the contained TikZ runner's bounded, validated PDF conversion."""
    runner = _tikz_renderer()
    dvisvgm = runner._resolve_optional_executable("dvisvgm")
    pdf2svg = runner._resolve_optional_executable("pdf2svg")
    ghostscript = runner._resolve_optional_executable("gs")
    if dvisvgm is None and pdf2svg is None:
        raise RuntimeError("Outlined SVG requires dvisvgm or pdf2svg")
    with tempfile.TemporaryDirectory(prefix="schematic-pgf-") as directory:
        build = Path(directory)
        descriptor = os.open(pdf_name, os.O_RDONLY | os.O_NOFOLLOW, dir_fd=parent_descriptor)
        with os.fdopen(descriptor, "rb") as stream:
            payload = stream.read(runner.MAX_ARTIFACT_BYTES + 1)
        if len(payload) > runner.MAX_ARTIFACT_BYTES:
            raise RuntimeError("PDF exceeds conversion size limit")
        pdf = build / "figure.pdf"
        svg = build / "figure.svg"
        pdf.write_bytes(payload)
        environment = runner._isolated_tex_environment(build, [p for p in (dvisvgm, pdf2svg, ghostscript) if p])
        runner._convert_pdf_to_svg(dvisvgm=dvisvgm, pdf2svg=pdf2svg,
                                  build_pdf=pdf, build_svg=svg,
                                  build_directory=build, environment=environment)
        svg_bytes = _normalize_svg_bytes(svg.read_bytes())
    name = f".converted.{secrets.token_hex(12)}.svg"
    descriptor = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=parent_descriptor)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(svg_bytes)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        os.unlink(name, dir_fd=parent_descriptor)
        raise
    return name
