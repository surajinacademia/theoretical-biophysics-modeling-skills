"""Illustrative overdamped oscillator in SI units; see model.md for the model."""

import argparse
import csv
import math
import sys


def decay_rates(m: float, gamma: float, k: float) -> tuple[float, float]:
    """Return the slow and fast characteristic roots, both negative, in 1/s."""
    if not all(math.isfinite(q) and q > 0 for q in (m, gamma, k)):
        raise ValueError("Mass, damping coefficient, and stiffness must be finite and positive.")
    discriminant = gamma * gamma - 4 * m * k
    if not math.isfinite(discriminant) or discriminant <= 0:
        raise ValueError("This example requires two distinct overdamped roots: gamma**2 > 4*m*k.")
    root_denominator = 2 * m
    if not math.isfinite(root_denominator):
        raise ValueError("The characteristic roots exceed floating-point range.")
    fast = -(gamma + math.sqrt(discriminant)) / root_denominator
    # The root product avoids subtraction of nearly equal numbers for strong damping.
    root_product = m * fast
    if not math.isfinite(root_product) or root_product == 0:
        raise ValueError("The characteristic roots exceed floating-point range.")
    slow = k / root_product
    if not (math.isfinite(slow) and math.isfinite(fast) and fast < slow < 0):
        raise ValueError("The characteristic roots exceed floating-point range.")
    return slow, fast


def exact_state(
    t: float, m: float, gamma: float, k: float, x0: float, v0: float
) -> tuple[float, float]:
    """Evaluate the two-exponential solution at nonnegative time t."""
    if not all(math.isfinite(q) for q in (t, x0, v0)) or t < 0:
        raise ValueError("Time must be finite and nonnegative; initial state must be finite.")
    slow, fast = decay_rates(m, gamma, k)
    root_gap = slow - fast
    if not math.isfinite(root_gap) or root_gap <= 0:
        raise ArithmeticError("The exact solution exceeds floating-point range.")
    amplitude_slow = (v0 - fast * x0) / root_gap
    amplitude_fast = (slow * x0 - v0) / root_gap
    if not all(math.isfinite(q) for q in (amplitude_slow, amplitude_fast)):
        raise ArithmeticError("The exact solution exceeds floating-point range.")
    slow_term = amplitude_slow * math.exp(slow * t)
    fast_term = amplitude_fast * math.exp(fast * t)
    position = slow_term + fast_term
    velocity = slow * slow_term + fast * fast_term
    if not all(math.isfinite(q) for q in (position, velocity)):
        raise ArithmeticError("The exact solution exceeds floating-point range.")
    return position, velocity


def integrate(
    *, m: float = 1.0, gamma: float = 5.0, k: float = 4.0,
    x0: float = 0.01, v0: float = 0.0, dt: float = 0.01, steps: int = 500,
) -> list[tuple[float, float, float]]:
    """Return (time, position, velocity) at every step, including the initial state."""
    decay_rates(m, gamma, k)
    if not all(math.isfinite(q) for q in (x0, v0, dt)) or dt <= 0:
        raise ValueError("Initial state must be finite and the timestep finite and positive.")
    if isinstance(steps, bool) or not isinstance(steps, int) or steps < 0:
        raise ValueError("The number of steps must be a nonnegative integer.")
    if not math.isfinite(steps * dt):
        raise ValueError("The final time must be finite.")
    denominator = m + gamma * dt + k * dt * dt
    if not math.isfinite(denominator):
        raise ValueError("The backward Euler denominator exceeds floating-point range.")

    x, v = x0, v0
    trajectory = [(0.0, x, v)]
    for n in range(steps):
        v_next = (m * v - dt * k * x) / denominator
        x_next = x + dt * v_next
        if not math.isfinite(x_next) or not math.isfinite(v_next):
            raise ArithmeticError("The numerical state exceeds floating-point range.")
        x, v = x_next, v_next
        trajectory.append(((n + 1) * dt, x, v))
    return trajectory


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mass", type=float, default=1.0, help="Mass in kg")
    parser.add_argument("--drag", type=float, default=5.0, help="Damping coefficient in kg/s")
    parser.add_argument("--stiffness", type=float, default=4.0, help="Spring stiffness in N/m")
    parser.add_argument("--x0", type=float, default=0.01, help="Initial displacement in m")
    parser.add_argument("--v0", type=float, default=0.0, help="Initial velocity in m/s")
    parser.add_argument("--dt", type=float, default=0.01, help="Timestep in s")
    parser.add_argument("--steps", type=int, default=500, help="Number of timesteps")
    args = parser.parse_args()
    try:
        trajectory = integrate(
            m=args.mass, gamma=args.drag, k=args.stiffness,
            x0=args.x0, v0=args.v0, dt=args.dt, steps=args.steps,
        )
        rows = []
        for t, x, v in trajectory:
            exact_x, exact_v = exact_state(
                t, args.mass, args.drag, args.stiffness, args.x0, args.v0,
            )
            energy = 0.5 * args.mass * v * v + 0.5 * args.stiffness * x * x
            if not math.isfinite(energy):
                raise ArithmeticError("The reported energy exceeds floating-point range.")
            rows.append((t, x, v, energy, exact_x, exact_v))
    except (ValueError, ArithmeticError) as error:
        parser.error(str(error))

    writer = csv.writer(sys.stdout)
    writer.writerow(("time_s", "position_m", "velocity_m_per_s", "energy_J",
                     "exact_position_m", "exact_velocity_m_per_s"))
    writer.writerows(rows)


if __name__ == "__main__":
    main()
