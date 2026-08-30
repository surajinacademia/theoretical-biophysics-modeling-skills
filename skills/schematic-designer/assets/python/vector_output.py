"""Safe PDF/SVG output helpers for schematic-designer Matplotlib specimens.

The public contract is deliberately narrow: final figures are a PDF plus an
SVG whose glyphs are paths.  No raster preview is written by this module.
"""

from __future__ import annotations

import os
import re
import secrets
import stat
import xml.etree.ElementTree as ElementTree
from pathlib import Path
from typing import Any, Mapping


VECTOR_SUFFIXES = (".pdf", ".svg")
_SVG_DOCTYPE = re.compile(br"<!DOCTYPE\s+svg\b[^>]*>\s*", re.IGNORECASE | re.DOTALL)
_CSS_URL = re.compile(r"url\(\s*(['\"]?)(.*?)\1\s*\)", re.IGNORECASE | re.DOTALL)


def _xml_local_name(name: str) -> str:
    return name.rsplit("}", 1)[-1].lower()


def _validate_svg_uri(value: str, *, is_image: bool, context: str) -> None:
    reference = value.strip()
    lowered = reference.lower()
    if reference.startswith("#"):
        return
    if is_image and lowered.startswith("data:image/"):
        media_type = lowered[5:].split(";", 1)[0].split(",", 1)[0]
        if media_type in {"image/png", "image/jpeg", "image/gif", "image/webp", "image/avif"}:
            return
    raise RuntimeError(f"SVG contains an external or unsafe reference in {context}")


def _validate_svg_url_functions(value: str, context: str) -> None:
    if "url(" not in value.lower():
        return
    matches = list(_CSS_URL.finditer(value))
    if not matches:
        raise RuntimeError(f"SVG contains an unparsable URL reference in {context}")
    for match in matches:
        _validate_svg_uri(match.group(2), is_image=False, context=context)


def _validate_svg_bytes(payload: bytes) -> None:
    """Reject live text, executable content, fonts, and external references."""
    try:
        raw_svg = payload.decode("utf-8")
    except UnicodeDecodeError as error:
        raise RuntimeError("SVG is not valid UTF-8 XML") from error
    lowered = raw_svg.lower()
    forbidden_tokens = {
        "<!doctype": "DTD declaration",
        "<!entity": "entity declaration",
        "<?xml-stylesheet": "external stylesheet instruction",
        "<script": "script element",
        "javascript:": "JavaScript reference",
        "@import": "stylesheet import",
        "@font-face": "embedded font rule",
        "font-family": "font-family declaration",
    }
    present = [description for token, description in forbidden_tokens.items() if token in lowered]
    if present:
        raise RuntimeError(f"SVG contains forbidden content: {', '.join(present)}")

    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError as error:
        raise RuntimeError("SVG is not well-formed XML") from error
    if _xml_local_name(root.tag) != "svg":
        raise RuntimeError("Rendered artifact is not an SVG document")

    forbidden_elements = {
        "audio",
        "embed",
        "font",
        "font-face",
        "foreignobject",
        "iframe",
        "object",
        "script",
        "text",
        "textpath",
        "tspan",
        "video",
    }
    for element in root.iter():
        element_name = _xml_local_name(element.tag)
        if element_name in forbidden_elements:
            raise RuntimeError(f"SVG contains forbidden <{element_name}> content")
        if element_name == "style":
            style_text = "".join(element.itertext())
            _validate_svg_url_functions(style_text, "<style>")
        for attribute, value in element.attrib.items():
            attribute_name = _xml_local_name(attribute)
            context = f"<{element_name}> @{attribute_name}"
            if attribute_name in {"base", "font", "font-family"}:
                raise RuntimeError("SVG contains a forbidden base or font attribute")
            if attribute_name.startswith("on"):
                raise RuntimeError("SVG contains an event-handler attribute")
            if attribute_name in {"data", "href", "src"}:
                _validate_svg_uri(value, is_image=element_name == "image", context=context)
            _validate_svg_url_functions(value, context)


def _normalize_svg_bytes(payload: bytes) -> bytes:
    """Remove Matplotlib's legacy external SVG DTD declaration."""
    normalized = _SVG_DOCTYPE.sub(b"", payload, count=1)
    if b"<!DOCTYPE" in normalized.upper() or b"<!ENTITY" in normalized.upper():
        raise RuntimeError("Generated SVG contains a DTD or entity declaration")
    _validate_svg_bytes(normalized)
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
    temporary_name = (
        f".{destination.stem}.{secrets.token_hex(12)}{destination.suffix}"
    )
    temporary_descriptor: int | None = None
    try:
        try:
            target = os.stat(
                destination.name,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
        except FileNotFoundError:
            target = None
        if target is not None and not stat.S_ISREG(target.st_mode):
            raise RuntimeError(f"Refusing unsafe output file: {destination.name}")

        temporary_descriptor = os.open(
            temporary_name,
            os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600,
            dir_fd=parent_descriptor,
        )
        save_options = dict(kwargs)
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
            os.fsync(temporary_file.fileno())

        os.replace(
            temporary_name,
            destination.name,
            src_dir_fd=parent_descriptor,
            dst_dir_fd=parent_descriptor,
        )
    finally:
        if temporary_descriptor is not None:
            os.close(temporary_descriptor)
        try:
            os.unlink(temporary_name, dir_fd=parent_descriptor)
        except FileNotFoundError:
            pass
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
    _validate_svg_bytes(path.read_bytes())


def validate_pdf(path: Path) -> None:
    """Check that a rendered file has a non-empty PDF header."""
    with path.open("rb") as handle:
        header = handle.read(5)
    if header != b"%PDF-" or path.stat().st_size < 100:
        raise RuntimeError(f"Invalid PDF output: {path}")


def save_vector_pair(
    figure: Any,
    approved_directory: Path,
    basename: str,
    *,
    common_options: Mapping[str, Any] | None = None,
    pdf_options: Mapping[str, Any] | None = None,
    svg_options: Mapping[str, Any] | None = None,
) -> tuple[Path, Path]:
    """Atomically write and validate exactly ``basename.pdf`` and ``basename.svg``."""
    if not basename or Path(basename).name != basename or Path(basename).suffix:
        raise RuntimeError("Output basename must be one extension-free filename")

    output_directory = prepare_output_directory(approved_directory)
    shared = dict(common_options or {})
    pdf_path = output_directory / f"{basename}.pdf"
    svg_path = output_directory / f"{basename}.svg"

    configure_matplotlib_vector_output()
    save_figure_atomic(
        figure,
        output_directory,
        pdf_path.name,
        **(shared | dict(pdf_options or {})),
    )
    save_figure_atomic(
        figure,
        output_directory,
        svg_path.name,
        **(shared | dict(svg_options or {})),
    )
    validate_pdf(pdf_path)
    validate_outlined_svg(svg_path)
    return pdf_path, svg_path
