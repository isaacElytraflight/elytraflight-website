#!/usr/bin/env python3
"""Independent numeric check for optimization-models batch EB3.

Recomputes each numeric answer from the data in the prompts. Does not import
the generator. Symbolic keys are checked by finish().
"""
import math

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "quadratic-program",
    "quadratically-constrained-quadratic-program",
    "second-order-cone-program",
    "semidefinite-program",
    "conic-duality",
    "lasso-stationarity",
    "coordinate-descent",
    "equality-constrained-newton",
    "barrier-interior-point",
]


def soft(z, threshold):
    if z > threshold:
        return z - threshold
    if z < -threshold:
        return z + threshold
    return 0.0


def line_value(ax, ay, total):
    """Optimal value of (x-ax)^2+(y-ay)^2 subject to x+y=total."""
    # y = total - x. Derivative 2(x-ax) - 2(total-x-ay) = 0.
    x = (ax + total - ay) / 2.0
    y = total - x
    return (x - ax) ** 2 + (y - ay) ** 2


def disk_gap_sq(point, center, radius):
    gap = float(np.linalg.norm(np.subtract(point, center)) - radius)
    return gap ** 2


def newton_step(grad, rows):
    """One feasible equality Newton step for f=x^2+y^2, Hessian 2I.

    Returns the step and the multiplier.
    """
    grad = np.array(grad, dtype=float)
    A = np.array(rows, dtype=float)
    n = grad.size
    m = A.shape[0]
    kkt = np.zeros((n + m, n + m))
    kkt[:n, :n] = 2.0 * np.eye(n)
    kkt[:n, n:] = A.T
    kkt[n:, :n] = A
    rhs = np.concatenate([-grad, np.zeros(m)])
    sol = np.linalg.solve(kkt, rhs)
    return sol[:n], sol[n:]


def psd_min_t(off, pivot):
    """Smallest t with [[t, off], [off, pivot]] positive semidefinite, pivot>0."""
    return (off ** 2) / pivot


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    expected["quadratic-program-r1-q2"] = line_value(0.0, 0.0, 4.0)
    expected["quadratic-program-r2-q2"] = line_value(1.0, 4.0, 7.0)
    expected["quadratic-program-r2-q3"] = 4.0 * 3.0 ** 2
    # min x^2+(y-5)^2 on x+2y=5. y=(5-x)/2.
    # derivative of x^2+((5-x)/2-5)^2 is 2x+(x+5)/2 = 0.
    x_star = -1.0
    y_star = (5.0 - x_star) / 2.0
    expected["quadratic-program-r4-q2"] = x_star ** 2 + (y_star - 5.0) ** 2

    expected["quadratically-constrained-quadratic-program-r1-q2"] = (2.0 - 6.0) ** 2
    expected["quadratically-constrained-quadratic-program-r2-q2"] = disk_gap_sq(
        (5.0, 5.0), (2.0, 1.0), 3.0
    )
    expected["quadratically-constrained-quadratic-program-r2-q3"] = disk_gap_sq(
        (1.0, 1.0), (4.0, 5.0), 2.0
    )
    expected["quadratically-constrained-quadratic-program-r4-q2"] = disk_gap_sq(
        (8.0, 0.0), (0.0, 0.0), 3.0
    )

    expected["second-order-cone-program-r1-q2"] = math.hypot(3.0, -4.0)
    expected["second-order-cone-program-r2-q2"] = math.hypot(2.0 * 3.0, 9.0 - 1.0)
    expected["second-order-cone-program-r2-q3"] = 6.0 / math.sqrt(2.0)
    expected["second-order-cone-program-r4-q2"] = (5.0 + 1.0) / 3.0

    expected["semidefinite-program-r1-q2"] = 4.0 * 4.0 - 1.0 ** 2
    expected["semidefinite-program-r2-q2"] = psd_min_t(3.0, 4.0)
    hess = np.array([[6.0, 2.0], [2.0, 3.0]])
    expected["semidefinite-program-r2-q3"] = float(np.min(np.linalg.eigvalsh(hess)))
    expected["semidefinite-program-r4-q2"] = psd_min_t(6.0, 2.0)

    expected["conic-duality-r1-q2"] = 3.0 * 5.0
    expected["conic-duality-r2-q2"] = min(2.0, 5.0)
    expected["conic-duality-r2-q3"] = 4.0 * 1.0 + 1.0 * 3.0 - 4.0 * 1.0
    expected["conic-duality-r4-q2"] = 1.0 * 2.0

    expected["lasso-stationarity-r1-q2"] = soft(4.0, 1.0)
    expected["lasso-stationarity-r2-q2"] = soft(-4.0, 1.0)
    expected["lasso-stationarity-r2-q3"] = soft(5.0, 1.0)
    z_swap = np.array([[0.0, 1.0], [1.0, 0.0]]) @ np.array([6.0, 1.0])
    expected["lasso-stationarity-r4-q2"] = soft(float(z_swap[1]), 2.0)

    expected["coordinate-descent-r1-q2"] = soft(6.0, 2.0)
    # (x+y)^2+(x-4)^2 from (0,0): x first, then y.
    x_cd = 2.0
    y_cd = -x_cd
    expected["coordinate-descent-r2-q2"] = y_cd
    expected["coordinate-descent-r2-q3"] = soft(8.0, 3.0)
    expected["coordinate-descent-r4-q2"] = soft(-2.0, 1.0)

    step, mult = newton_step([0.0, 8.0], [[1.0, 1.0]])
    expected["equality-constrained-newton-r1-q2"] = 0.0 + float(step[0])
    step2, _mult2 = newton_step([12.0, 0.0], [[1.0, 2.0]])
    expected["equality-constrained-newton-r2-q2"] = 0.0 + float(step2[1])
    expected["equality-constrained-newton-r2-q3"] = float(mult[0])
    step4, _mult4 = newton_step([0.0, 4.0], [[1.0, 1.0]])
    expected["equality-constrained-newton-r4-q2"] = 0.0 + float(step4[0])

    expected["barrier-interior-point-r1-q2"] = 2.0 + 6.0
    expected["barrier-interior-point-r2-q2"] = 2.0
    expected["barrier-interior-point-r2-q3"] = 1.0
    expected["barrier-interior-point-r4-q2"] = 5.0 + 4.0

    numeric = check_expected(banks, expected, mismatches)

    def need(sid, snippet):
        if snippet not in texts[sid]:
            mismatches.append(f"{sid} explainer missing {snippet!r}")

    need("quadratic-program", "equals 18")
    need("quadratically-constrained-quadratic-program", "equals 36")
    need("second-order-cone-program", "equals 15")
    need("semidefinite-program", "25/4")
    need("conic-duality", "matching dual value is 6")
    need("lasso-stationarity", "equals 7")
    need("coordinate-descent", "lands on 9")
    need("equality-constrained-newton", "multiplier equals -10")
    need("barrier-interior-point", "weight is 72")

    if abs(line_value(9.0, 2.0, 5.0) - 18.0) > 1e-12:
        mismatches.append("quadratic worked value is not 18")
    if (4.0 - 10.0) ** 2 != 36.0:
        mismatches.append("qcqp worked value is not 36")
    if abs(math.hypot(9.0, 12.0) - 15.0) > 1e-12:
        mismatches.append("socp worked norm is not 15")
    if abs(psd_min_t(5.0, 4.0) - 25.0 / 4.0) > 1e-12:
        mismatches.append("sdp worked bound is not 25/4")
    # min 5x+2y on x+2y=6, x,y>=0. Cost 30-8y, best y=3, value 6.
    if abs(30.0 - 8.0 * 3.0 - 6.0) > 1e-12:
        mismatches.append("conic worked value is not 6")
    if soft(9.0, 2.0) != 7.0 or soft(-1.0, 2.0) != 0.0:
        mismatches.append("lasso worked threshold is not 7 and 0")
    if soft(11.0, 2.0) != 9.0 or soft(-6.0, 2.0) != -4.0:
        mismatches.append("coordinate worked point is not (9, -4)")
    worked_step, worked_mult = newton_step([0.0, 20.0], [[1.0, 1.0]])
    if abs(float(worked_step[0]) - 5.0) > 1e-9 or abs(float(worked_mult[0]) + 10.0) > 1e-9:
        mismatches.append("newton worked step is not x-step 5 with multiplier -10")
    barrier_resid = 2.0 * (7.0 - 16.0) + 72.0 / (11.0 - 7.0)
    if abs(barrier_resid) > 1e-12:
        mismatches.append("barrier worked stationarity residual is not 0")

    # Residuals that justify the hand-picked interior points.
    interval_resid = 1.0 - 3.0 / 2.0 + 3.0 / (8.0 - 2.0)
    if abs(interval_resid) > 1e-12:
        mismatches.append("barrier interval point is not stationary")
    quad_resid = 2.0 * (1.0 - 10.0) + 18.0 / (2.0 - 1.0)
    if abs(quad_resid) > 1e-12:
        mismatches.append("barrier quadratic point is not stationary")

    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
