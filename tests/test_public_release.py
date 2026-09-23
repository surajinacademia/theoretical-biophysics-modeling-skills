"""Distribution invariants for the approved eight-skill release."""
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT if (ROOT / "release-manifest.json").exists() else ROOT / "public/theoretical-biophysics-modeling-skills"
SKILLS = {"computational-modeling", "model-documentation", "scientific-notebook",
          "linear-stability-analysis", "data-visualization", "schematic-designer",
          "lets-be-clear", "slurm"}


class PublicReleaseTests(unittest.TestCase):
    def test_versions_and_catalog_agree(self):
        manifest = json.loads((PUBLIC / "release-manifest.json").read_text())
        self.assertEqual(set(manifest["skills"]), SKILLS)
        self.assertEqual({p.name for p in (PUBLIC / "skills").iterdir() if p.is_dir()}, SKILLS)
        for name in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json", "gemini-extension.json"):
            package = json.loads((PUBLIC / name).read_text())
            self.assertEqual(package["version"], manifest["version"])
            self.assertNotEqual(package.get("license"), "MIT")

    def test_export_hashes_and_containment(self):
        files = json.loads((PUBLIC / "release-manifest.json").read_text())["files"]
        for name, expected in files.items():
            with self.subTest(path=name):
                path = PUBLIC / name
                self.assertFalse(path.is_symlink())
                self.assertTrue(path.resolve().is_relative_to(PUBLIC.resolve()))
                self.assertNotIn("..", Path(name).parts)
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected)
                self.assertFalse(any(part in {"gotcha", "paper-reproduce", "local-history", "__pycache__"}
                                     for part in path.relative_to(PUBLIC).parts))

    def test_diagram_notices_travel_with_sources_and_specimens(self):
        base = PUBLIC / "skills/schematic-designer"
        gallery = json.loads((base / "assets/examples/tikz/manifest.json").read_text())
        original = {"learning-dynamics", "chemoattraction"}
        for entry in gallery["examples"]:
            if entry["slug"] in original:
                continue
            case = base / "assets/examples/tikz" / entry["slug"]
            with self.subTest(case=entry["slug"]):
                self.assertTrue((case / "ATTRIBUTION.md").is_file())
                self.assertTrue((case / "source.tex").is_file())
                self.assertTrue((case / "figures/figure.pdf").is_file())
                self.assertTrue((case / "figures/figure.svg").is_file())
        vigil = base / "assets/examples/matplotlib/vigil"
        self.assertTrue((vigil / "ATTRIBUTION.md").is_file())
        self.assertTrue((vigil / "LICENSE").is_file())
        self.assertFalse((base / "archives/imported-tikz-gallery/tkz-linknodes-examples/tkz-linknodes.sty").exists())


if __name__ == "__main__":
    unittest.main()
