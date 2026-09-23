"""Behavioral tests for surgical notebook edits and honest saved execution state."""
import copy
import importlib.util
import json
import os
import sys
from pathlib import Path
import stat
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import nbformat
from nbclient.exceptions import CellExecutionError


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "scientific_notebook_helper", ROOT / "skills/scientific-notebook/scripts/notebook.py")
helper = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(helper)


class NotebookTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name).resolve()
        self.path = self.directory / "analysis.ipynb"
        self.patch_path = self.directory / "patch.json"
        kernel_dir = self.directory / "jupyter" / "kernels" / "notebook-test"
        kernel_dir.mkdir(parents=True)
        (kernel_dir / "kernel.json").write_text(json.dumps({
            "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
            "display_name": "Notebook test", "language": "python"}))
        env = patch.dict(os.environ, {"JUPYTER_PATH": str(self.directory / "jupyter"),
                                    "IPYTHONDIR": str(self.directory / "ipython")})
        env.start()
        self.addCleanup(env.stop)
        self.nb = nbformat.v4.new_notebook(cells=[
            nbformat.v4.new_markdown_cell("Original", id="intro", attachments={
                "image.png": {"image/png": "YWJj"}}, metadata={"custom": {"keep": True}}),
            nbformat.v4.new_code_cell("x = 1\nprint(x)", id="first", execution_count=1,
                outputs=[nbformat.v4.new_output("stream", name="stdout", text="1\n")]),
            nbformat.v4.new_raw_cell("Raw untouched", id="raw"),
            nbformat.v4.new_code_cell("print(2)", id="second", execution_count=2,
                outputs=[nbformat.v4.new_output("stream", name="stdout", text="2\n")]),
        ], metadata={"custom": [1, 2], "scientific_notebook": {
            "execution": "succeeded", "interpretation": "reviewed"},
            "widgets": {"application/vnd.jupyter.widget-state+json": {"state": {},
                "version_major": 2, "version_minor": 0}}})
        self.write()

    def write(self):
        self.path.write_text(nbformat.writes(self.nb))

    def read(self):
        return nbformat.read(self.path, as_version=4)

    def edit(self, operations, **extra):
        payload = {"sha256": helper.inspect(self.path)["sha256"],
                   "operations": operations, **extra}
        self.patch_path.write_text(json.dumps(payload))
        return helper.edit(self.path, self.patch_path)

    def test_markdown_preserves_outputs_metadata_attachments_and_raw(self):
        self.path.chmod(0o640)
        before = self.read()
        self.edit([{"op": "replace", "id": "intro", "source": "Revised"}])
        after = self.read()
        self.assertEqual(before.cells[1:], after.cells[1:])
        self.assertEqual(before.metadata, after.metadata)
        self.assertEqual(before.cells[0].attachments, after.cells[0].attachments)
        self.assertEqual(before.cells[0].metadata, after.cells[0].metadata)
        self.assertEqual(stat.S_IMODE(self.path.stat().st_mode), 0o640)

    def test_code_change_defaults_to_clearing_all(self):
        self.edit([{"op": "replace", "id": "first", "source": "x = 3"}])
        nb = self.read()
        for cell in nb.cells:
            if cell.cell_type == "code":
                self.assertEqual(cell.outputs, [])
                self.assertIsNone(cell.execution_count)
        self.assertNotIn("widgets", nb.metadata)
        self.assertEqual(nb.metadata.scientific_notebook,
                         {"execution": "stale", "interpretation": "review_required"})
        self.assertEqual(nb.cells[0].source, "Original")

    def test_explicit_invalidation_preserves_independent_output(self):
        self.nb.cells[3].outputs = [nbformat.v4.new_output("display_data", data={
            "application/vnd.jupyter.widget-view+json": {
                "model_id": "independent-widget", "version_major": 2, "version_minor": 0},
            "text/plain": "Independent widget"})]
        widget_state = self.nb.metadata.widgets["application/vnd.jupyter.widget-state+json"]
        widget_state["state"]["independent-widget"] = {
            "model_name": "TestModel", "model_module": "test", "model_module_version": "1.0",
            "state": {"value": 2}}
        self.write()
        before = self.read()
        self.edit([{"op": "replace", "id": "first", "source": "x = 4"}], invalidate=["first"])
        after = self.read()
        self.assertEqual(after.cells[3], before.cells[3])
        self.assertEqual(after.metadata.widgets, before.metadata.widgets)
        self.assertEqual(after.cells[1].outputs, [])

    def test_save_preserves_conventional_multiline_serialization(self):
        self.nb.cells[1].outputs[0].text = "First line\nSecond line\n"
        self.write()
        original = json.loads(self.path.read_text())
        self.assertIsInstance(original["cells"][1]["source"], list)
        self.assertIsInstance(original["cells"][1]["outputs"][0]["text"], list)
        self.edit([{"op": "replace", "id": "intro", "source": "Revised\nIntroduction"}])
        saved = json.loads(self.path.read_text())
        self.assertEqual(saved["cells"][1:], original["cells"][1:])
        self.assertEqual(saved["cells"][0]["source"], ["Revised\n", "Introduction"])
        self.assertEqual(self.read().cells[1].outputs[0].text, "First line\nSecond line\n")

    def test_insert_delete_and_explicit_deleted_dependency(self):
        self.edit([{"op": "insert", "after": None, "cell_type": "raw", "source": "First", "id": "new"},
                   {"op": "delete", "id": "first"}], invalidate=["second"])
        nb = self.read()
        self.assertEqual([c.id for c in nb.cells], ["new", "intro", "raw", "second"])
        self.assertEqual(nb.cells[-1].outputs, [])

    def test_bad_patches_are_atomic(self):
        bad = [
            ([{"op": "replace", "id": "intro", "source": "Changed"}, {"op": "delete", "id": "missing"}], {}),
            ([{"op": "replace", "id": "first", "source": "Changed"}], {"invalidate": []}),
            ([{"op": "insert", "after": "intro", "cell_type": "code", "source": "pass", "id": "intro"}], {}),
            ([{"op": "replace", "id": "intro", "source": "ok", "extra": True}], {}),
            ([], {"invalidate": ["raw"]}),
        ]
        original = self.path.read_bytes()
        for operations, extra in bad:
            with self.subTest(operations=operations):
                with self.assertRaises((ValueError, nbformat.ValidationError)):
                    self.edit(operations, **extra)
                self.assertEqual(self.path.read_bytes(), original)
        self.assertEqual(list(self.directory.glob(".*.tmp")), [])

    def test_stale_patch_rejected(self):
        self.patch_path.write_text(json.dumps({"sha256": "stale", "operations": []}))
        original = self.path.read_bytes()
        with self.assertRaisesRegex(ValueError, "Stale"):
            helper.edit(self.path, self.patch_path)
        self.assertEqual(self.path.read_bytes(), original)

    def test_old_v4_ids_stable_and_persist_only_on_edit(self):
        data = json.loads(self.path.read_text())
        data["nbformat_minor"] = 4
        for cell in data["cells"]:
            cell.pop("id")
        self.path.write_text(json.dumps(data))
        original = self.path.read_bytes()
        first = helper.inspect(self.path)
        self.assertEqual(first, helper.inspect(self.path))
        self.assertEqual(self.path.read_bytes(), original)
        self.edit([])
        self.assertEqual([c["id"] for c in first["cells"]], [c.id for c in self.read().cells])

    def test_symlinks_rejected(self):
        link = self.directory / "link.ipynb"
        link.symlink_to(self.path)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            helper.inspect(link)
        parent = self.directory / "linked"
        parent.symlink_to(self.directory, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            helper.inspect(parent / self.path.name)
        self.patch_path.symlink_to(self.path)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            helper.edit(self.path, self.patch_path)

    def test_create_uses_template_and_refuses_overwrite(self):
        path = self.directory / "new.ipynb"
        helper.create(path, "Example", ["One", "Two", "Three"])
        template = nbformat.read(ROOT / "skills/scientific-notebook/assets/notebook-template.ipynb", as_version=4)
        created = nbformat.read(path, as_version=4)
        self.assertEqual(created.cells[1:], template.cells[1:])
        self.assertEqual(created.cells[0].source, "# Example\n\n- One\n- Two\n- Three")
        original = path.read_bytes()
        with self.assertRaises(FileExistsError):
            helper.create(path, "Other", ["a", "b", "c"])
        self.assertEqual(path.read_bytes(), original)
        with self.assertRaises(ValueError):
            helper.create(self.directory / "bad.ipynb", "Title", [])

    def test_create_accepts_concise_opening(self):
        for points in (["One point"], ["First point", "Second point"]):
            with self.subTest(points=points):
                path = self.directory / f"concise-{len(points)}.ipynb"
                helper.create(path, "Concise", points)
                nb = nbformat.read(path, as_version=4)
                self.assertEqual(nb.cells[0].source,
                                 "# Concise\n\n" + "\n".join("- " + p for p in points))
        with self.assertRaises(ValueError):
            helper.create(self.directory / "blank.ipynb", "Title", [" "])

    def test_create_through_skill_discovery_link(self):
        installed = self.directory / "installed-skill"
        installed.symlink_to(ROOT / "skills/scientific-notebook", target_is_directory=True)
        path = self.directory / "from-installed-skill.ipynb"
        result = subprocess.run(
            [sys.executable, str(installed / "scripts/notebook.py"), "create", str(path),
             "--title", "Installed skill", "--point", "Use the canonical template."],
            capture_output=True, text=True, timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        created = nbformat.read(path, as_version=4)
        nbformat.validate(created)
        self.assertEqual(created.cells[0].source,
                         "# Installed skill\n\n- Use the canonical template.")
        self.assertEqual(created.metadata.scientific_notebook.interpretation, "not_requested")

    def test_code_edit_does_not_request_interpretation(self):
        for initial in (None, "not_requested"):
            with self.subTest(initial=initial):
                if initial is None:
                    self.nb.metadata.pop("scientific_notebook", None)
                else:
                    self.nb.metadata.scientific_notebook = {"interpretation": initial}
                self.write()
                before_sources = [c.source for c in self.nb.cells if c.cell_type != "code"]
                self.edit([{"op": "replace", "id": "first", "source": "x = 5"}])
                nb = self.read()
                self.assertEqual(nb.metadata.scientific_notebook,
                                 {"execution": "stale", "interpretation": "not_requested"})
                self.assertEqual([c.source for c in nb.cells if c.cell_type != "code"], before_sources)

    def test_execution_preserves_interpretation_not_requested(self):
        self.nb.metadata.scientific_notebook.interpretation = "not_requested"
        self.write()
        helper.execute(self.path, kernel="notebook-test", timeout=30)
        self.assertEqual(self.read().metadata.scientific_notebook,
                         {"execution": "succeeded", "interpretation": "not_requested"})
        self.nb.cells[3].source = "raise ValueError('intentional test failure')"
        self.write()
        with self.assertRaises(CellExecutionError):
            helper.execute(self.path, kernel="notebook-test", timeout=30)
        self.assertEqual(self.read().metadata.scientific_notebook,
                         {"execution": "failed", "interpretation": "not_requested"})

    def test_create_atomic_no_clobber(self):
        path = self.directory / "race.ipynb"
        real_link = helper.os.link
        def competitor(source, destination):
            Path(destination).write_text("Concurrent owner")
            return real_link(source, destination)
        with patch.object(helper.os, "link", side_effect=competitor):
            with self.assertRaises(FileExistsError):
                helper.create(path, "Example", ["a", "b", "c"])
        self.assertEqual(path.read_text(), "Concurrent owner")
        self.assertEqual(list(self.directory.glob(".*.tmp")), [])

    def test_execute_fresh_kernel_cwd_and_no_skip_tags(self):
        self.nb.cells[1].source = "from pathlib import Path\nassert 'persisted' not in globals()\npersisted = 1\nprint(Path.cwd())"
        self.nb.cells[1].metadata.tags = ["skip-execution", "scientific-notebook-never-skip"]
        self.write()
        for _ in range(2):
            helper.execute(self.path, kernel="notebook-test", timeout=30)
        nb = self.read()
        self.assertIn(str(self.directory), nb.cells[1].outputs[0].text)
        self.assertEqual(nb.metadata.scientific_notebook.execution, "succeeded")
        self.assertEqual(nb.metadata.scientific_notebook.interpretation, "review_required")

    def test_execute_expected_error_still_fails_and_clears_everything(self):
        self.nb.cells[3].source = "raise ValueError('intentional test failure')"
        self.nb.cells[3].metadata.tags = ["raises-exception"]
        self.write()
        original = copy.deepcopy(self.nb)
        with self.assertRaises(CellExecutionError):
            helper.execute(self.path, kernel="notebook-test", timeout=30)
        nb = self.read()
        self.assertEqual(nb.metadata.scientific_notebook.execution, "failed")
        self.assertEqual([c.source for c in nb.cells], [c.source for c in original.cells])
        self.assertTrue(all(not c.outputs and c.execution_count is None for c in nb.cells if c.cell_type == "code"))

    def test_execute_does_not_overwrite_concurrent_edit(self):
        self.nb.cells[1].source = "from pathlib import Path\nPath('analysis.ipynb').write_text('Concurrent user edit')"
        self.write()
        with self.assertRaisesRegex(ValueError, "concurrently"):
            helper.execute(self.path, kernel="notebook-test", timeout=30)
        self.assertEqual(self.path.read_text(), "Concurrent user edit")
        self.assertEqual(list(self.directory.glob(".*.tmp")), [])


if __name__ == "__main__":
    unittest.main()
