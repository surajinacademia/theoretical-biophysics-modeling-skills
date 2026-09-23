"""Integrity of renderer-organized examples and their preserved provenance."""

import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/schematic-designer"
EXAMPLES = SKILL / "assets/examples"
ACTIVE = EXAMPLES / "tikz"
MATPLOTLIB = EXAMPLES / "matplotlib"
ARCHIVE = SKILL / "archives/imported-tikz-gallery"
LOCAL_TIKZ = {"learning-dynamics", "chemoattraction"}
MATPLOTLIB_FINALS = {
    "activator-inhibitor", "collective-cell-model-classes", "learning-dynamics", "vigil",
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class TikzGalleryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((ACTIVE / "manifest.json").read_text())
        cls.entries = cls.manifest["examples"]

    def contained_file(self, root, relative):
        """Reject traversal and symlinked ancestors before opening a manifest input."""
        relative = Path(relative)
        self.assertFalse(relative.is_absolute(), relative)
        self.assertNotIn("..", relative.parts)
        path = root / relative
        for part in (path, *path.parents):
            self.assertFalse(part.is_symlink(), part)
            if part == root:
                break
        self.assertTrue(path.resolve().is_relative_to(root.resolve()), path)
        self.assertTrue(path.is_file(), path)
        return path

    def case_files(self, entry):
        return entry.get("files", self.manifest["files"])

    def test_examples_are_grouped_by_source_renderer(self):
        self.assertEqual({p.name for p in EXAMPLES.iterdir() if p.is_dir()},
                         {"tikz", "matplotlib"})
        for suffix, renderer in ((".tex", ACTIVE), (".py", MATPLOTLIB)):
            sources = list(EXAMPLES.rglob(f"*{suffix}"))
            self.assertTrue(sources)
            for source in sources:
                with self.subTest(source=source):
                    self.contained_file(renderer, source.relative_to(renderer))
        self.assertEqual({p.name for p in MATPLOTLIB.iterdir() if p.is_dir()},
                         MATPLOTLIB_FINALS | {"chemoattraction"})
        for slug in MATPLOTLIB_FINALS:
            folder = MATPLOTLIB / slug
            self.contained_file(folder, "README.md")
            pdfs = list((folder / "figures").glob("*.pdf"))
            self.assertEqual(len(pdfs), 1, slug)
            self.contained_file(folder, pdfs[0].relative_to(folder))
            self.contained_file(folder, pdfs[0].with_suffix(".svg").relative_to(folder))
        self.contained_file(MATPLOTLIB, "chemoattraction/matplotlib-panels.py")
        self.contained_file(MATPLOTLIB, "chemoattraction/README.md")
        self.assertFalse((MATPLOTLIB / "chemoattraction/figures").exists(),
                         "Hybrid final outputs belong beside their TikZ compositor")

    def test_every_tikz_case_has_a_complete_buildable_record(self):
        original = json.loads((ARCHIVE / "manifest.json").read_text())
        original_slugs = {entry["slug"] for entry in original["examples"]}
        active_slugs = {entry["slug"] for entry in self.entries}
        self.assertEqual(len(self.entries), len(active_slugs))
        self.assertEqual(len(active_slugs), 19)
        self.assertEqual(original_slugs | LOCAL_TIKZ, active_slugs)
        self.assertEqual(active_slugs, {p.name for p in ACTIVE.iterdir() if p.is_dir()})

        script_dir = SKILL / "scripts"
        spec = importlib.util.spec_from_file_location("gallery_builder", script_dir / "build_example.py")
        builder = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(script_dir))
        try:
            spec.loader.exec_module(builder)
        finally:
            sys.path.pop(0)
        self.assertEqual(set(builder.TIKZ_CASES), active_slugs)
        self.assertEqual(set(builder.IMPORTED_TIKZ_CASES), original_slugs)
        self.assertEqual(set(builder.CASES), {
            "activator-inhibitor", "collective-cell-model-classes", "learning-dynamics",
            "learning-tikz", "chemoattraction", "vigil",
        } | {f"tikz-{slug}" for slug in original_slugs})

        for entry in self.entries:
            with self.subTest(case=entry["slug"]):
                expected_build = {"learning-dynamics": "learning-tikz",
                                  "chemoattraction": "chemoattraction"}.get(
                                      entry["slug"], f"tikz-{entry['slug']}")
                self.assertEqual(entry["build_case"], expected_build)
                folder = ACTIVE / entry["slug"]
                files = self.case_files(entry)
                self.assertTrue({"source", "pdf", "svg"} <= files.keys())
                for name in files.values():
                    self.contained_file(folder, name)
                self.contained_file(folder, "README.md")

    def test_build_record_detects_source_style_or_artifact_drift(self):
        profile_digest = digest(SKILL / "assets/styles/minimalist_profile.py")
        self.assertEqual(self.manifest["current_profile_sha256"], profile_digest)
        recorded_profile = self.manifest["shared_profile_sha256"]
        self.assertRegex(recorded_profile, r"^[0-9a-f]{64}$")
        self.assertTrue(self.manifest["profile_change_note"].strip())
        original = json.loads((ARCHIVE / "manifest.json").read_text())
        imported_slugs = {entry["slug"] for entry in original["examples"]}
        required_inputs = {
            "learning-dynamics": {"assets/styles/tikz/learning-dynamics-2406.sty"},
            "chemoattraction": {
                "assets/styles/tikz/scientific-neutral.sty",
                "assets/examples/matplotlib/chemoattraction/matplotlib-panels.py",
            },
        }
        for entry in self.entries:
            with self.subTest(case=entry["slug"]):
                folder = ACTIVE / entry["slug"]
                self.assertEqual(entry["profile_sha256"], recorded_profile)
                if entry["slug"] in imported_slugs:
                    self.assertEqual(entry["archived_source_sha256"], digest(
                        self.contained_file(ARCHIVE, f"{entry['slug']}/source.tex")))
                else:
                    self.assertNotIn("archived_source_sha256", entry)
                for kind in ("source", "pdf", "svg"):
                    path = self.contained_file(folder, self.case_files(entry)[kind])
                    self.assertEqual(entry[f"{kind}_sha256"], digest(path))
                inputs = entry["inputs"]
                self.assertIsInstance(inputs, dict)
                self.assertTrue(required_inputs.get(entry["slug"], set()) <= inputs.keys())
                for relative, expected in inputs.items():
                    self.assertEqual(expected, digest(self.contained_file(SKILL, relative)))

    def test_all_svgs_are_self_contained_with_outlined_text(self):
        for entry in self.entries:
            with self.subTest(case=entry["slug"]):
                path = self.contained_file(ACTIVE / entry["slug"], self.case_files(entry)["svg"])
                document = ET.parse(path)
                tags = {node.tag.split("}")[-1] for node in document.iter()}
                self.assertIn("path", tags)
                if entry["slug"] == "spherical-and-cartesian-grids":
                    self.assertIn("radialGradient", tags, "Preserve the original 3D ball lighting")
                self.assertFalse({"text", "foreignObject"} & tags)
                # The owner retained the original physics-card blur shadows.
                # Only their individually recorded opacity masks may be raster.
                layers = entry.get("svg_embedded_layers", [])
                self.assertIsInstance(layers, list)
                declared = {layer["id"]: layer for layer in layers}
                self.assertEqual(len(declared), len(layers))
                images = [node for node in document.iter()
                          if node.tag.split("}")[-1] == "image"]
                image_ids = {node.get("id") for node in images}
                self.assertEqual(len(image_ids), len(images))
                self.assertEqual(image_ids, set(declared))
                if layers:
                    self.assertEqual(entry["slug"], "model-physics")
                    self.assertEqual(len(layers), 18)
                    self.assertTrue(entry.get("svg_embedded_layers_reason", "").strip())
                all_ids = [node.get("id") for node in document.iter() if node.get("id")]
                self.assertEqual(len(all_ids), len(set(all_ids)))
                parents = {child: parent for parent in document.iter() for child in parent}
                masked_nodes = {child for node in document.iter()
                                if node.tag.split("}")[-1] == "mask"
                                for child in node.iter()}
                referenced_images = set()
                for node in images:
                    layer = declared[node.get("id")]
                    self.assertEqual(layer["kind"], "shadow-opacity-mask")
                    ancestor = parents.get(node)
                    while ancestor is not None and ancestor.tag.split("}")[-1] != "defs":
                        ancestor = parents.get(ancestor)
                    self.assertIsNotNone(ancestor, "Raster masks must be defined, not directly drawn")
                    hrefs = [value for key, value in node.attrib.items()
                             if key.split("}")[-1] == "href"]
                    self.assertEqual(len(hrefs), 1)
                    prefix = "data:image/png;base64,"
                    self.assertTrue(hrefs[0].startswith(prefix))
                    data = base64.b64decode(hrefs[0][len(prefix):], validate=True)
                    self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
                    self.assertEqual(hashlib.sha256(data).hexdigest(), layer["sha256"])
                for node in document.iter():
                    for key, value in node.attrib.items():
                        if key.split("}")[-1] == "href" and node not in images:
                            self.assertTrue(value.startswith("#"), value)
                            if value[1:] in image_ids:
                                self.assertEqual(node.tag.split("}")[-1], "use")
                                self.assertIn(node, masked_nodes)
                                referenced_images.add(value[1:])
                        # An image reference through paint/filter/style attributes
                        # would bypass the mask-only <use> restriction above.
                        if node not in images:
                            for reference in re.findall(r"url\(\s*['\"]?#([^)'\"\s]+)", value):
                                self.assertNotIn(reference, image_ids)
                        self.assertNotIn("font-family", key)
                        self.assertNotIn("font-family", value)
                self.assertEqual(referenced_images, image_ids)


if __name__ == "__main__":
    unittest.main()
