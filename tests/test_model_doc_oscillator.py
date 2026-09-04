"""Focused behavior tests for the overdamped oscillator model example."""

from __future__ import annotations

import importlib.util
import math
import subprocess
import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = (
    REPOSITORY_ROOT
    / "skills"
    / "model-documentation"
    / "examples"
    / "overdamped-harmonic-oscillator"
    / "model.py"
)
SPEC = importlib.util.spec_from_file_location("overdamped_harmonic_oscillator", MODEL_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("Unable to load the overdamped oscillator model.")
OSCILLATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(OSCILLATOR)


class OverdampedOscillatorTests(unittest.TestCase):
    def terminal_errors(self, dt: float) -> tuple[float, float]:
        t, x, v = OSCILLATOR.integrate(dt=dt, steps=round(1.0 / dt))[-1]
        exact_x, exact_v = OSCILLATOR.exact_state(t, 1.0, 5.0, 4.0, 0.01, 0.0)
        return abs(x - exact_x), abs(v - exact_v)

    def run_model(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(MODEL_PATH), *arguments],
            cwd=REPOSITORY_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

    def test_default_rates_and_exact_initial_state(self):
        self.assertEqual(OSCILLATOR.decay_rates(1.0, 5.0, 4.0), (-1.0, -4.0))
        position, velocity = OSCILLATOR.exact_state(0.0, 1.0, 5.0, 4.0, 0.01, -0.02)
        self.assertAlmostEqual(position, 0.01, places=15)
        self.assertAlmostEqual(velocity, -0.02, places=15)

    def test_backward_euler_agrees_with_exact_solution_at_small_timestep(self):
        position_error, velocity_error = self.terminal_errors(0.001)

        self.assertLess(position_error, 3e-6)
        self.assertLess(velocity_error, 1e-6)

    def test_backward_euler_error_decreases_under_timestep_refinement(self):
        coarse_position_error, coarse_velocity_error = self.terminal_errors(0.02)
        fine_position_error, fine_velocity_error = self.terminal_errors(0.01)

        self.assertLess(fine_position_error, 0.7 * coarse_position_error)
        self.assertLess(fine_velocity_error, 0.7 * coarse_velocity_error)

    def test_rejects_nonfinite_or_nonpositive_mechanical_parameters(self):
        defaults = [1.0, 5.0, 4.0]
        for index, name in enumerate(("mass", "drag", "stiffness")):
            for value in (math.nan, math.inf, -math.inf, 0.0, -1.0):
                with self.subTest(parameter=name, value=value):
                    parameters = defaults.copy()
                    parameters[index] = value
                    with self.assertRaises(ValueError):
                        OSCILLATOR.decay_rates(*parameters)

    def test_rejects_nonfinite_time_state_and_timestep_inputs(self):
        defaults = [0.0, 1.0, 5.0, 4.0, 0.01, 0.0]
        for index, name in ((0, "time"), (4, "x0"), (5, "v0")):
            for value in (math.nan, math.inf, -math.inf):
                with self.subTest(parameter=name, value=value):
                    arguments = defaults.copy()
                    arguments[index] = value
                    with self.assertRaises(ValueError):
                        OSCILLATOR.exact_state(*arguments)
        with self.assertRaises(ValueError):
            OSCILLATOR.exact_state(-0.01, 1.0, 5.0, 4.0, 0.01, 0.0)
        for dt in (math.nan, math.inf, -math.inf, 0.0, -0.01):
            with self.subTest(timestep=dt):
                with self.assertRaises(ValueError):
                    OSCILLATOR.integrate(dt=dt)

    def test_rejects_nonrepresentable_roots_and_exact_state(self):
        parameters = (1e-200, 1e150, 1e-200)

        with self.assertRaisesRegex(ValueError, "characteristic roots"):
            OSCILLATOR.decay_rates(*parameters)
        with self.assertRaisesRegex(ValueError, "characteristic roots"):
            OSCILLATOR.exact_state(0.01, *parameters, 0.01, 0.0)
        with self.assertRaisesRegex(ValueError, "characteristic roots"):
            OSCILLATOR.integrate(m=parameters[0], gamma=parameters[1], k=parameters[2])

    def test_rejects_nonrepresentable_exact_output(self):
        with self.assertRaisesRegex(ArithmeticError, "exact solution"):
            OSCILLATOR.exact_state(0.0, 1.0, 5.0, 4.0, 1e308, 0.0)

    def test_cli_reports_representability_errors_without_csv_or_traceback(self):
        root_failure = self.run_model(
            "--mass", "1e-200", "--drag", "1e150", "--stiffness", "1e-200"
        )
        output_failure = self.run_model("--x0", "1e308", "--steps", "0")

        for result, message in (
            (root_failure, "characteristic roots"),
            (output_failure, "exact solution"),
        ):
            with self.subTest(message=message):
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn(message, result.stderr)
                self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
