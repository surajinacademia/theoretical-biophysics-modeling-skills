"""Shared visual defaults stay aligned across Matplotlib and generated TikZ."""

import importlib.util
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch


PROFILE = Path(__file__).resolve().parents[1] / "skills/schematic-designer/assets/styles/minimalist_profile.py"
SPEC = importlib.util.spec_from_file_location("schematic_minimalist_profile", PROFILE)
profile = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(profile)


class SchematicStyleTests(unittest.TestCase):
    def setUp(self):
        self.colors = ["#123ABC", "#abcdef", "#654321"]
        self.minimalist = types.ModuleType("minimalist")
        self.minimalist.get_cmap = Mock(return_value=self.colors)
        self.minimalist.use_style = Mock(side_effect=AssertionError("must not apply upstream style"))
        self.mpl = types.ModuleType("matplotlib")
        self.mpl.use = Mock()
        self.mpl.get_backend = Mock(return_value="pgf")
        self.mpl.rcParams = {}
        self.mpl.cycler = lambda **kwargs: kwargs
        modules = patch.dict(sys.modules, {"matplotlib": self.mpl, "minimalist": self.minimalist})
        modules.start()
        self.addCleanup(modules.stop)

    def test_palette_reaches_both_renderers_without_copy_or_reordering(self):
        profile.apply_style()
        source = profile.tikz_style()
        self.assertEqual(self.mpl.rcParams["axes.prop_cycle"]["color"], self.colors)
        for index, color in enumerate(self.colors, 1):
            self.assertIn(r"\definecolor{msColor" + str(index) + "}{HTML}{" + color[1:] + "}", source)
        self.assertNotIn("msColor4", source)
        self.minimalist.get_cmap.assert_called_with("qualitative")
        self.minimalist.use_style.assert_not_called()
        returned = profile.palette()
        returned.append("#000000")
        self.assertEqual(len(self.colors), 3)

    def test_rejects_unsafe_or_empty_palette(self):
        for colors in ([], "#123456", ["red"], ["#abc"], ["#123456\n"],
                       [r"#123456}\input{bad}"], [None]):
            with self.subTest(colors=colors):
                self.minimalist.get_cmap.return_value = colors
                with self.assertRaises(ValueError):
                    profile.tikz_style()

    def test_neutral_tints_match_both_renderers_after_role_changes(self):
        with patch.object(profile, "MUTED", "#000000"), \
             patch.dict(profile.OPACITY, context=.2, fill=.1):
            colors = profile.neutral_colors()
            self.assertEqual(colors, {'faint':'#666666', 'grid':'#CCCCCC', 'panel':'#E6E6E6'})
            source = profile.tikz_style()
            for role, color in colors.items():
                self.assertIn(r"\definecolor{ms" + role.title() + "}{HTML}{" + color[1:] + "}", source)

    def test_missing_package_warns_and_returns_fresh_native_palette(self):
        native_colors = ["#1f77b4", "#ff7f0e"]
        cycle = Mock()
        cycle.by_key.return_value = {"color": native_colors}
        self.mpl.rcParamsDefault = {"axes.prop_cycle": cycle}
        with patch.dict(sys.modules, {"minimalist": None}):
            with self.assertWarnsRegex(RuntimeWarning, "default color cycle"):
                returned = profile.palette()
            self.assertEqual(returned, native_colors)
            self.assertIsNot(returned, native_colors)
            returned[0] = "#000000"
            returned.append("#FFFFFF")
            with self.assertWarnsRegex(RuntimeWarning, "Colors differ from bundled specimens"):
                fresh = profile.palette()
            self.assertEqual(fresh, ["#1f77b4", "#ff7f0e"])
            self.assertEqual(native_colors, ["#1f77b4", "#ff7f0e"])
        self.minimalist.get_cmap.assert_not_called()
        self.minimalist.use_style.assert_not_called()

    def test_existing_unrelated_backend_is_not_switched(self):
        self.mpl.get_backend.return_value = "agg"
        with patch.dict(sys.modules, {"matplotlib.pyplot": types.ModuleType("matplotlib.pyplot")}):
            with self.assertRaisesRegex(RuntimeError, "before importing pyplot"):
                profile.apply_style()
        self.mpl.use.assert_not_called()
        self.minimalist.get_cmap.assert_not_called()

    def test_typography_and_opaque_text_have_no_fallback(self):
        profile.apply_style()
        rc = self.mpl.rcParams
        self.assertTrue(rc["text.usetex"])
        self.assertFalse(rc["pgf.rcfonts"])
        self.assertEqual(rc["pgf.texsystem"], "lualatex")
        self.assertEqual(rc["font.sans-serif"], ["CMU Sans Serif"])
        self.assertEqual(rc["font.serif"], ["CMU Serif"])
        self.assertIn(r"\usepackage[no-math]{fontspec}", rc["pgf.preamble"])
        source = profile.tikz_style()
        self.assertIn(r"\RequireLuaTeX", source)
        self.assertIn(r"\RequirePackage[no-math]{fontspec}", source)
        self.assertIn(r"execute at begin picture={\everymath=\expandafter{\the\everymath\displaystyle}}", source)
        self.assertIn(r"ms fill/.style={fill opacity=\msOpacityFill,text opacity=1}", source)
        self.assertNotIn("figure.figsize", rc)
        self.assertEqual(rc["axes.titleweight"], "bold")
        self.assertIn(r"\fontsize{\msFontPanel}{12pt}\selectfont\bfseries", source)
        self.assertIn("ms body,text=msInk,color=msInk", source)
        self.assertNotIn("draw=msInk", source)

    def test_inherited_presentation_is_reset_and_text_stays_opaque(self):
        self.mpl.rcParams.update({"axes.grid": True, "savefig.transparent": True,
                                  "lines.dash_capstyle": "round", "axes.labelweight": "bold"})
        with patch.dict(profile.OPACITY, foreground=0.6):
            profile.apply_style()
            source = profile.tikz_style()
        self.assertFalse(self.mpl.rcParams["axes.grid"])
        self.assertFalse(self.mpl.rcParams["savefig.transparent"])
        self.assertEqual(self.mpl.rcParams["axes.labelweight"], "normal")
        self.assertEqual(self.mpl.rcParams["lines.dash_capstyle"], "butt")
        self.assertIn("line cap=butt,line join=round", source)
        self.assertIn("show background rectangle", source)
        self.assertIn("background rectangle/.style={fill=msPaper,fill opacity=1,draw=none}", source)
        self.assertNotIn(r"text opacity=\msOpacityForeground", source)
        self.assertIn("text opacity=1", source)

    def test_custom_roles_use_same_physical_units_and_patterns(self):
        with patch.dict(profile.FONT_PT, body=8.5), patch.dict(profile.LINE_PT, structure=0.9), \
             patch.dict(profile.MARKER_PT, point=3.5), patch.dict(profile.SPACE_PT, group=10), \
             patch.dict(profile.OPACITY, fill=0.2), patch.dict(profile.DASH_PT, dashed=(4, 3)):
            profile.apply_style()
            source = profile.tikz_style()
            self.assertEqual(self.mpl.rcParams["font.size"], 8.5)
            self.assertEqual(self.mpl.rcParams["lines.linewidth"], 0.9)
            self.assertEqual(self.mpl.rcParams["lines.markersize"], 3.5)
            self.assertFalse(self.mpl.rcParams["lines.scale_dashes"])
            self.assertEqual(self.mpl.rcParams["lines.dashed_pattern"], (4, 3))
            for prefix, roles, unit in (("Font", profile.FONT_PT, "pt"),
                                        ("Line", profile.LINE_PT, "bp"),
                                        ("Marker", profile.MARKER_PT, "bp"),
                                        ("Space", profile.SPACE_PT, "bp"),
                                        ("Opacity", profile.OPACITY, "")):
                for role, value in roles.items():
                    self.assertIn(r"\newcommand{\ms" + prefix + role.title()
                                  + "}{" + f"{value:g}{unit}" + "}", source)
            self.assertIn(r"\newcommand{\msDashDashedOn}{4bp}", source)
            self.assertIn(r"\newcommand{\msDashDashedOff}{3bp}", source)

    def test_invalid_numeric_override_is_rejected_before_import(self):
        for value in (float("nan"), float("inf"), -1, 0, "8bp", True):
            with self.subTest(value=value), patch.dict(profile.FONT_PT, body=value):
                with self.assertRaises(ValueError):
                    profile.apply_style()
        with patch.dict(profile.OPACITY, fill=1.2), self.assertRaises(ValueError):
            profile.tikz_style()
        with patch.dict(profile.DASH_PT, dashed=(0, 2)), self.assertRaises(ValueError):
            profile.tikz_style()
        self.minimalist.get_cmap.assert_not_called()


class RealMatplotlibTests(unittest.TestCase):
    @unittest.skipUnless(importlib.util.find_spec("matplotlib"), "Matplotlib unavailable")
    def test_actual_rcparams_backend_and_axes_methods(self):
        # Use a subprocess so a test suite's existing GUI/Agg backend is untouched.
        code = r'''
import importlib.util
import sys
import types
from matplotlib.axes import Axes
before = dict(vars(Axes))
spec = importlib.util.spec_from_file_location("profile", sys.argv[1])
profile = importlib.util.module_from_spec(spec)
spec.loader.exec_module(profile)
try:
    installed = importlib.util.find_spec("minimalist") is not None
except ValueError:
    installed = False
if not installed:
    fake = types.ModuleType("minimalist")
    fake.get_cmap = lambda kind: ["#123456", "#abcdef"]
    sys.modules["minimalist"] = fake
profile.apply_style()
import matplotlib as mpl
assert mpl.get_backend().lower() == "pgf"
assert mpl.rcParams["text.usetex"]
assert mpl.rcParams["pgf.texsystem"] == "lualatex"
assert mpl.rcParams["axes.prop_cycle"].by_key()["color"] == profile.palette()
assert dict(vars(Axes)) == before, "Profile or palette import changed Axes class"
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
line, = ax.plot([0, 1], [0, 1], marker="o", linestyle="--")
assert line.get_color() == profile.palette()[0]
assert line.get_linewidth() == profile.LINE_PT["structure"]
assert line.get_markersize() == profile.MARKER_PT["point"]
assert line._dash_pattern[0] == 0
assert tuple(line._dash_pattern[1]) == profile.DASH_PT["dashed"]
plt.close(fig)
'''
        with tempfile.TemporaryDirectory(prefix="schematic-mpl-test-") as cache:
            result = subprocess.run([sys.executable, "-B", "-c", code, str(PROFILE)],
                                    env={**os.environ, "MPLCONFIGDIR": cache},
                                    capture_output=True, text=True, timeout=60)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
