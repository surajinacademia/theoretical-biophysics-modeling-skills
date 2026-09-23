#!/usr/bin/env python3
"""Edit one notebook with explicit cell IDs and execute it in a fresh kernel.

Requires nbformat and nbclient (plus the selected kernel). Execution runs arbitrary
notebook code with the caller's privileges; this helper is not a sandbox.
Version 4 notebooks without cell IDs receive deterministic IDs on mutation.
"""

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import stat
import sys
import tempfile

import nbformat
from nbclient import NotebookClient


def _path(value):
    """Reject links throughout the selected path, except macOS system aliases."""
    path = Path(os.path.abspath(os.path.expanduser(value)))
    # macOS exposes /tmp and /var through system-owned aliases. Resolve just
    # these explicit prefixes, never arbitrary user-selected parents.
    if sys.platform == "darwin" and path.parts[1:2] in [("tmp",), ("var",)]:
        prefix = Path("/") / path.parts[1]
        path = prefix.resolve().joinpath(*path.parts[2:])
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        if current.is_symlink():
            raise ValueError(f"Symlink paths are not supported: {current}")
    if not path.parent.is_dir():
        raise ValueError(f"Parent directory must exist: {path.parent}")
    if path.exists() and not path.is_file():
        raise ValueError(f"Expected a regular file: {path}")
    return path


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _validate(nb):
    if nb.get("nbformat") != 4 or nb.get("nbformat_minor", 0) < 5:
        raise ValueError("Requires notebook format 4.5+ with explicit cell IDs")
    ids = [cell.get("id") for cell in nb.get("cells", [])]
    if any(not isinstance(cid, str) or not cid for cid in ids) or len(set(ids)) != len(ids):
        raise ValueError("Requires unique, explicit cell IDs; repair IDs before editing")
    nbformat.validate(nb)


def _read(value):
    path = _path(value)
    data = path.read_bytes()
    # Parse first so nbformat cannot silently generate IDs or normalize input.
    nb = nbformat.from_dict(json.loads(data))
    if nb.get("nbformat") != 4:
        raise ValueError("Requires notebook format 4")
    nb.nbformat_minor = max(nb.get("nbformat_minor", 0), 5)
    for index, cell in enumerate(nb.get("cells", [])):
        if "id" not in cell:
            seed = json.dumps([index, cell.get("cell_type"), cell.get("source")], sort_keys=True)
            cell.id = "cell-" + _hash(seed.encode())[:20]
    _validate(nb)
    nb = nbformat.reads(json.dumps(nb), as_version=4)
    return path, nb, _hash(data)


def _save(path, nb, expected=None):
    _validate(nb)
    data = nbformat.writes(nb).encode()
    path = _path(path)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), mode)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        _path(path)
        if expected is None:
            # Linking a same-directory staging file is atomic and cannot clobber.
            os.link(name, path)
        else:
            if _hash(path.read_bytes()) != expected:
                raise ValueError("Notebook changed concurrently; inspect again before saving")
            os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def _clear(nb, execution="stale", ids=None):
    for cell in nb.cells:
        if cell.cell_type == "code" and (ids is None or cell.id in ids):
            cell.outputs = []
            cell.execution_count = None
    if ids is None:
        nb.metadata.pop("widgets", None)
    state = nb.metadata.setdefault("scientific_notebook", {})
    interpretation = state.get("interpretation", "not_requested")
    state.update(execution=execution, interpretation=(
        "not_requested" if interpretation == "not_requested" else "review_required"))


def create(path, title, points):
    if not points or not title.strip() or any(not p.strip() for p in points):
        raise ValueError("Provide a title and one or more nonempty points")
    path = _path(path)
    if path.exists():
        raise FileExistsError(f"Refusing to overwrite {path}")
    # Skill discovery may link to this source; notebook and patch paths still
    # pass through _path's symlink checks.
    template = Path(__file__).resolve().parent.parent / "assets" / "notebook-template.ipynb"
    _, nb, _ = _read(template)
    openings = [cell for cell in nb.cells
                if cell.metadata.get("scientific_notebook", {}).get("role") == "opening"]
    if len(openings) != 1 or openings[0].cell_type != "markdown":
        raise ValueError("Template requires exactly one opening markdown cell")
    openings[0].source = "# " + title + "\n\n" + "\n".join("- " + p for p in points)
    _clear(nb)
    _save(path, nb)
    return inspect(path)


def inspect(path):
    _, nb, digest = _read(path)
    return {"sha256": digest, "metadata": nb.metadata, "cells": [
        {"id": cell.id, "cell_type": cell.cell_type, "source": cell.source,
         "metadata": cell.metadata, "execution_count": cell.get("execution_count"),
         "attachments": list(cell.get("attachments", {})),
         "outputs": [{"output_type": out.output_type,
                      "mime_types": list(out.get("data", {})),
                      "ename": out.get("ename")} for out in cell.get("outputs", [])]}
        for cell in nb.cells]}


def edit(path, patch_path):
    path, nb, digest = _read(path)
    patch = json.loads(_path(patch_path).read_text())
    if not isinstance(patch, dict) or not {"sha256", "operations"} <= set(patch) or set(patch) - {"sha256", "operations", "invalidate"}:
        raise ValueError("Patch requires sha256, operations, and optional invalidate")
    if patch["sha256"] != digest:
        raise ValueError("Stale patch hash; inspect the notebook again")
    if not isinstance(patch["operations"], list):
        raise ValueError("operations must be an array")
    changed_code = False
    changed_ids = set()
    for op in patch["operations"]:
        if not isinstance(op, dict):
            raise ValueError("Each operation must be an object")
        kind = op.get("op")
        required = {"replace": {"op", "id", "source"}, "delete": {"op", "id"},
                    "insert": {"op", "after", "cell_type", "source"}}.get(kind)
        if required is None or not required <= set(op) or set(op) - required - ({"id"} if kind == "insert" else set()):
            raise ValueError("Unknown operation or invalid operation fields")
        if kind != "delete" and not isinstance(op["source"], str):
            raise ValueError("source must be a string")
        ids = [cell.id for cell in nb.cells]
        if kind == "insert":
            if op["after"] is not None and op["after"] not in ids:
                raise ValueError("Unknown insertion anchor")
            makers = {"code": nbformat.v4.new_code_cell, "markdown": nbformat.v4.new_markdown_cell,
                      "raw": nbformat.v4.new_raw_cell}
            if op["cell_type"] not in makers:
                raise ValueError("Unsupported cell type")
            cell = makers[op["cell_type"]](op["source"])
            if "id" in op:
                cell.id = op["id"]
            nb.cells.insert(0 if op["after"] is None else ids.index(op["after"]) + 1, cell)
            changed_code |= cell.cell_type == "code"
            if cell.cell_type == "code":
                changed_ids.add(cell.id)
        else:
            if op["id"] not in ids:
                raise ValueError("Unknown cell ID")
            index = ids.index(op["id"])
            cell = nb.cells[index]
            if cell.cell_type == "code" and (kind == "delete" or cell.source != op["source"]):
                changed_code = True
                changed_ids.add(cell.id)
            if kind == "delete":
                del nb.cells[index]
            else:
                cell.source = op["source"]
        _validate(nb)
    invalidation = patch.get("invalidate")
    if "invalidate" in patch:
        code_ids = {cell.id for cell in nb.cells if cell.cell_type == "code"}
        if (not isinstance(invalidation, list)
                or any(not isinstance(cid, str) for cid in invalidation)
                or len(set(invalidation)) != len(invalidation)
                or not set(invalidation) <= code_ids):
            raise ValueError("invalidate must list unique surviving code cell IDs")
        if not changed_ids.intersection(code_ids) <= set(invalidation):
            raise ValueError("invalidate must include every changed or inserted code cell")
        if not changed_code and invalidation:
            raise ValueError("invalidate requires a computational change")
    if changed_code:
        _clear(nb, ids=invalidation)
    _save(path, nb, digest)
    return inspect(path)


def execute(path, kernel=None, timeout=600):
    path, nb, digest = _read(path)
    _clear(nb)
    cleared = copy.deepcopy(nb)
    skip_tag = "scientific-notebook-never-skip"
    tags = {tag for cell in nb.cells for tag in cell.metadata.get("tags", [])}
    while skip_tag in tags:
        skip_tag += "-"
    kwargs = dict(timeout=timeout, allow_errors=False, force_raise_errors=True,
                  skip_cells_with_tag=skip_tag, resources={"metadata": {"path": str(path.parent)}})
    if kernel is not None:
        kwargs["kernel_name"] = kernel
    try:
        NotebookClient(nb, **kwargs).execute()
    except BaseException:
        _clear(cleared, "failed")
        _save(path, cleared, digest)
        raise
    nb.metadata.scientific_notebook["execution"] = "succeeded"
    _save(path, nb, digest)
    return inspect(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("create", "inspect", "validate", "edit", "execute"):
        sub = commands.add_parser(name)
        sub.add_argument("path")
        if name == "create":
            sub.add_argument("--title", required=True)
            sub.add_argument("--point", action="append", required=True)
        elif name == "edit":
            sub.add_argument("--patch", required=True)
        elif name == "execute":
            sub.add_argument("--kernel")
            sub.add_argument("--timeout", type=int, default=600)
    args = parser.parse_args()
    try:
        if args.command == "create":
            result = create(args.path, args.title, args.point)
        elif args.command == "edit":
            result = edit(args.path, args.patch)
        elif args.command == "execute":
            result = execute(args.path, args.kernel, args.timeout)
        else:
            result = inspect(args.path)
        if args.command != "inspect":
            result = {"path": str(args.path), "sha256": result["sha256"],
                      "cell_count": len(result["cells"]),
                      "state": result["metadata"].get("scientific_notebook", {})}
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as error:
        print(f"{type(error).__name__}: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
