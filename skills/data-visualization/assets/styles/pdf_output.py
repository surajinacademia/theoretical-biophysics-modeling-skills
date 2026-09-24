"""Publish PDFs through pinned directories and a private staging directory.

POSIX directory descriptors and O_NOFOLLOW are required. No output component
is resolved through a symlink. Renaming a directory after it is opened cannot
redirect writes; a replaced destination leaf is replaced, never opened.
"""

from contextlib import contextmanager
import os
from pathlib import Path
import secrets
import stat


@contextmanager
def output_directory(path, *, create=False):
    """Open each directory component without following links; retain the last FD."""
    path = Path(path)
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    fd = os.open(path.anchor or ".", flags)
    try:
        for part in path.parts[1:] if path.is_absolute() else path.parts:
            if part == ".":
                continue
            if create:
                try:
                    os.mkdir(part, dir_fd=fd)
                except FileExistsError:
                    pass
            child = os.open(part, flags, dir_fd=fd)
            os.close(fd)
            fd = child
        yield fd
    finally:
        os.close(fd)


def _reject_link(parent, name):
    try:
        info = os.stat(name, dir_fd=parent, follow_symlinks=False)
    except FileNotFoundError:
        return
    if stat.S_ISLNK(info.st_mode):
        raise ValueError("output paths must not contain symlinks")


@contextmanager
def pdf_output(path, *, create_parents=False):
    """Yield a writable stream; publish atomically only after successful rendering.

    Staging is on the destination filesystem, mode 0700, and accessed through
    its retained FD. Cleanup also uses that FD, so swapping the staging name
    cannot redirect either publication or cleanup into another directory.
    """
    path = Path(path)
    if path.suffix.lower() != ".pdf":
        raise ValueError("output must end in .pdf")
    with output_directory(path.parent, create=create_parents) as parent:
        _reject_link(parent, path.name)
        stage = ".pdf-" + secrets.token_hex(16)
        os.mkdir(stage, mode=0o700, dir_fd=parent)
        stage_fd = os.open(stage, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                           dir_fd=parent)
        identity = os.fstat(stage_fd)
        created = False
        try:
            if identity.st_uid != os.geteuid() or stat.S_IMODE(identity.st_mode) != 0o700:
                raise RuntimeError("PDF staging directory is not private")
            fd = os.open("render.pdf", os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=stage_fd)
            created = True
            with os.fdopen(fd, "w+b") as stream:
                yield stream
                stream.flush()
                os.fsync(stream.fileno())
                # The directory is private; also fail closed on detected
                # interference from another process running as this user.
                saved = os.stat("render.pdf", dir_fd=stage_fd, follow_symlinks=False)
                opened = os.fstat(stream.fileno())
                if (saved.st_dev, saved.st_ino) != (opened.st_dev, opened.st_ino):
                    raise RuntimeError("PDF staging file was replaced")
                _reject_link(parent, path.name)
                os.replace("render.pdf", path.name, src_dir_fd=stage_fd, dst_dir_fd=parent)
        finally:
            if created:
                try:
                    os.unlink("render.pdf", dir_fd=stage_fd)
                except FileNotFoundError:
                    pass
            os.close(stage_fd)
            try:
                current = os.stat(stage, dir_fd=parent, follow_symlinks=False)
                if (current.st_dev, current.st_ino) == (identity.st_dev, identity.st_ino):
                    os.rmdir(stage, dir_fd=parent)
            except FileNotFoundError:
                pass


def save_pdf(figure, path, *, create_parents=False):
    """Render to an open stream, preserving Matplotlib's physical canvas size."""
    with pdf_output(path, create_parents=create_parents) as stream:
        figure.savefig(stream, format="pdf")
