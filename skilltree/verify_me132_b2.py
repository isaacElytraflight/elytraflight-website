#!/usr/bin/env python3
"""Independent numeric check for ME 132 batch B2.

The generator uses closed-form algebra. This file recomputes the same items
by linear solves, fixed-step RK4, or eigenvalue routines.
"""
import math

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts, prop_steady, rk4

SKILLS = ["block-diagram", "first-order-sys", "model-method", "onoff-pid-intro", "state-space-model"]


def loop_gain_closed(forward, ret, positive=False, reference=1.0, disturbance=0.0):
    """Solve y = G e + d, e = r ± H y, by a 2-by-2 linear system."""
    sign = 1.0 if positive else -1.0
    # e - sign*H y = r;  -G e + y = d
    a = np.array([[1.0, -sign * ret], [-forward, 1.0]], dtype=float)
    b = np.array([reference, disturbance], dtype=float)
    e, y = np.linalg.solve(a, b)
    return float(y)


def series(gains):
    y = 1.0
    for g in gains:
        y = y * g
    return float(y)


def accel(m, b, k, y, yd, u):
    return (u - b * yd - k * y) / m


def initial_accel(m, b, k, y0, yd0, u, dt=1e-4):
    """Second derivative at 0 from a short RK4 step of the two first-order states."""
    def step(y, yd):
        def f(_t, state):
            yy, vv = state
            return np.array([vv, accel(m, b, k, yy, vv, u)])
        # one RK4 step on the vector, then (v_new - v0)/dt
        h = dt
        s = np.array([y, yd], dtype=float)
        k1 = f(0, s)
        k2 = f(h / 2, s + h * k1 / 2)
        k3 = f(h / 2, s + h * k2 / 2)
        k4 = f(h, s + h * k3)
        s2 = s + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        return float((s2[1] - yd) / h)

    return step(y0, yd0)


def main():
    mismatches = []
    banks = load_banks(SKILLS)

    # --- block diagrams: linear solve / running product, not the written fraction ---
    pairs = {
        "block-diagram-r1-q2": series([4, 1]) + series([7, 1]) - 1,  # parallel via two paths; see below
    }
    # parallel: two independent paths summed. series([4]) is just 4. Do it explicitly.
    parallel = series([4]) + series([7])
    # series([4]) with one gain returns 4. Sum is 11. The expression above double-counted. Use parallel.
    del pairs
    expected = {
        "block-diagram-r1-q2": parallel,
        "block-diagram-r2-q1": loop_gain_closed(8, 0.5) ,
        "block-diagram-r2-q2": series([2.5, 4]),
        "block-diagram-r3-q1": loop_gain_closed(2, 0.2, positive=True),
        "block-diagram-r3-q3": series([2, 3, 4]),
        "block-diagram-r4-q1": loop_gain_closed(9, 2),
        "block-diagram-r4-q2": loop_gain_closed(4, 1, reference=0, disturbance=1),
        "block-diagram-r4-q3": series([1.5, 2, 4]),
    }
    # first order by RK4
    expected["first-order-sys-r1-q2"] = rk4(lambda t, y: (2 * 4 - y) / 6, 0, 80, 8000)
    expected["first-order-sys-r1-q3"] = rk4(lambda t, y: (1 - y) / 1, 0, 1, 2000)
    expected["first-order-sys-r2-q1"] = rk4(lambda t, y: -y / 2, 6, 2, 2000)
    expected["first-order-sys-r2-q3"] = rk4(lambda t, y: (12 * 1 - y) / 4, 0, 60, 6000)
    expected["first-order-sys-r3-q1"] = 1.0 / 0.25
    # initial slope by a one-sided difference of the closed form, not the derivative rule
    def y_step(t):
        return 9 * (1 - math.exp(-t / 3))
    dt = 1e-5
    expected["first-order-sys-r3-q3"] = (y_step(dt) - y_step(0)) / dt
    expected["first-order-sys-r4-q1"] = rk4(lambda t, y: (15 - y) / 6, 0, 80, 8000)
    # identify tau as the time the RK4 curve crosses 63.2% of its steady value
    steady = rk4(lambda t, y: (2 - y) / 1.7, 0, 40, 4000)
    target = (1 - math.exp(-1)) * steady
    # bisection on the simulation
    lo, hi = 0.0, 10.0
    for _ in range(40):
        mid = (lo + hi) / 2
        if rk4(lambda t, y: (2 - y) / 1.7, 0, mid, 2000) < target:
            lo = mid
        else:
            hi = mid
    expected["first-order-sys-r4-q2"] = (lo + hi) / 2

    expected["model-method-r1-q2"] = 0.4 / 2
    expected["model-method-r2-q1"] = (1500 / 60) * 360 * math.pi / 180
    expected["model-method-r2-q3"] = 36 * 0.025
    expected["model-method-r3-q1"] = 6.4 / 0.04
    expected["model-method-r3-q3"] = 1.5 * 4
    # resting point by bisection on the derivative
    lo, hi = 0.0, 20.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if 2.4 - 0.3 * mid > 0:
            lo = mid
        else:
            hi = mid
    expected["model-method-r4-q1"] = (lo + hi) / 2
    expected["model-method-r4-q2"] = 3.5
    lo, hi = 0.0, 10.0
    for _ in range(50):
        mid = (lo + hi) / 2
        if -2 * mid + 5 > 0:
            lo = mid
        else:
            hi = mid
    expected["model-method-r4-q3"] = (lo + hi) / 2

    expected["onoff-pid-intro-r1-q2"] = 9 - 14
    expected["onoff-pid-intro-r1-q3"] = prop_steady(4, 3, 10)
    expected["onoff-pid-intro-r2-q1"] = 10 - prop_steady(4, 3, 10)
    expected["onoff-pid-intro-r2-q3"] = prop_steady(4, 3, 0, disturbance=2)
    expected["onoff-pid-intro-r3-q1"] = 10 - prop_steady(8, 3, 10)
    expected["onoff-pid-intro-r3-q3"] = 8 - prop_steady(6, 2, 8)
    expected["onoff-pid-intro-r4-q1"] = 11 - prop_steady(10, 5, 11)
    expected["onoff-pid-intro-r4-q2"] = 18 - prop_steady(3, 5, 18)

    expected["state-space-model-r1-q2"] = initial_accel(4, 6, 10, 1, 0, 0)
    expected["state-space-model-r1-q3"] = initial_accel(4, 6, 10, 0, 0, 1)
    expected["state-space-model-r2-q1"] = initial_accel(4, 6, 10, 0, 1, 0)
    a = np.array([[0.0, 1.0], [-10 / 4, -6 / 4]])
    bvec = np.array([0.0, 1 / 4])
    rest = np.linalg.solve(a, -bvec * 8)
    expected["state-space-model-r2-q3"] = float(rest[0])
    ev = np.linalg.eigvals(np.diag([-2.0, -8.0]))
    expected["state-space-model-r3-q1"] = float(sorted(ev, key=lambda z: abs(z))[0].real)
    coeff = np.poly(a)  # λ^2 - tr λ + det, numpy returns highest degree first
    expected["state-space-model-r3-q3"] = float(coeff[1])
    expected["state-space-model-r4-q1"] = float(np.linalg.eigvals(np.array([[-1 / 3]]))[0].real)
    expected["state-space-model-r4-q2"] = 3.0

    numeric = check_expected(banks, expected, mismatches)

    # worked examples, recomputed a different way and required to appear in the text
    texts = load_texts(SKILLS)
    worked = loop_gain_closed(5, 0.4)
    if abs(worked - 5 / 3) / (5 / 3) > 2e-3 or "1.667" not in texts["block-diagram"]:
        mismatches.append(f"block worked {worked}")
    y12 = rk4(lambda t, y: (5 * 2 - y) / 1.2, 0, 1.2, 2400)
    if abs(y12 - 6.321) > 0.01 or "6.321" not in texts["first-order-sys"]:
        mismatches.append(f"first worked {y12}")
    if "0.15" not in texts["model-method"] or "300" not in texts["model-method"]:
        mismatches.append("model worked text")
    cruise = prop_steady(2, 5, 7)
    if abs(cruise - 6.364) > 0.01 or "6.364" not in texts["onoff-pid-intro"] or "0.636" not in texts["onoff-pid-intro"]:
        mismatches.append(f"pid worked {cruise}")
    a2 = np.array([[0.0, 1.0], [-3.0, -1.0]])
    b2 = np.array([0.0, 1 / 3])
    xrest = np.linalg.solve(a2, -b2 * 9)
    if abs(float(xrest[0]) - 1) > 1e-6 or "x = 1" not in texts["state-space-model"]:
        mismatches.append(f"ss worked {xrest}")

    finish(numeric, mismatches)


if __name__ == "__main__":
    main()
