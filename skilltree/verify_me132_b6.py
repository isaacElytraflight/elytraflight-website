#!/usr/bin/env python3
"""Independent numeric check for ME 132 batch B6.

The generator stores closed forms. This file recomputes them with ranks,
determinants, a Kronecker Lyapunov solve, least squares, and trigonometry.
It does not import the generator.
"""
import math

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "loop-shaping", "lyapunov", "observability", "reachability",
    "robust-stability", "root-locus", "sys-id", "time-delay",
]


def lyapunov_p(a, q):
    """Solve A^T P + P A = -Q. Returns P with columns stacked in Fortran order."""
    n = a.shape[0]
    eye = np.eye(n)
    kron = np.kron(eye, a.T) + np.kron(a.T, eye)
    rhs = (-q).reshape(-1, order="F")
    return np.linalg.solve(kron, rhs).reshape((n, n), order="F")


def ctrb(a, b, n):
    cols = [np.array(b, dtype=float).reshape(-1)]
    for _ in range(n - 1):
        cols.append(a @ cols[-1])
    return np.column_stack(cols)


def obsv(a, c, n):
    rows = [np.array(c, dtype=float).reshape(-1)]
    for _ in range(n - 1):
        rows.append(rows[-1] @ a)
    return np.vstack(rows)


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    expected = {}

    expected["loop-shaping-r1-q2"] = math.degrees(math.asin((3 - 1) / (3 + 1)))
    expected["loop-shaping-r1-q3"] = math.sqrt(4 * 16)
    expected["loop-shaping-r2-q2"] = 1.0 / 0.25
    expected["loop-shaping-r4-q1"] = 1.0 / 5.0

    expected["lyapunov-r1-q2"] = 12.0 / (2.0 * 3.0)
    expected["lyapunov-r1-q3"] = 2 * 0.5 * (-4 * 0.5)
    a_lyap = np.array([[0.0, 1.0], [-2.0, -3.0]])
    expected["lyapunov-r2-q2"] = float(lyapunov_p(a_lyap, np.eye(2))[0, 0])
    expected["lyapunov-r4-q1"] = 8 * 1.5 * (-0.5 * 1.5)

    a_obs = np.array([[0.0, 1.0], [-3.0, -4.0]])
    expected["observability-r1-q2"] = abs(float(np.linalg.det(obsv(a_obs, [1.0, 0.0], 2))))
    a_miss = np.diag([-2.0, -5.0])
    expected["observability-r1-q3"] = int(np.linalg.matrix_rank(obsv(a_miss, [1.0, 0.0], 2)))
    a3 = np.diag([-1.0, -2.0, -3.0])
    rank3 = int(np.linalg.matrix_rank(obsv(a3, [1.0, 0.0, 1.0], 3), tol=1e-8))
    expected["observability-r2-q2"] = 3 - rank3
    a_det = np.diag([-1.0, -4.0])
    expected["observability-r4-q1"] = abs(float(np.linalg.det(obsv(a_det, [2.0, 5.0], 2))))

    a_reach = np.array([[0.0, 1.0], [-2.0, -5.0]])
    expected["reachability-r1-q2"] = abs(float(np.linalg.det(ctrb(a_reach, [0.0, 1.0], 2))))
    a_gap = np.diag([-1.0, -3.0])
    expected["reachability-r1-q3"] = int(np.linalg.matrix_rank(ctrb(a_gap, [2.0, 0.0], 2)))
    a_three = np.diag([-2.0, -3.0, -4.0])
    rank_r = int(np.linalg.matrix_rank(ctrb(a_three, [1.0, 0.0, 1.0], 3), tol=1e-8))
    expected["reachability-r2-q2"] = 3 - rank_r
    a_mass = np.array([[0.0, 1.0], [0.0, -0.4]])
    expected["reachability-r4-q1"] = abs(float(np.linalg.det(ctrb(a_mass, [0.0, 2.5], 2))))

    expected["robust-stability-r1-q2"] = 1.0 / 1.6
    expected["robust-stability-r1-q3"] = 0.5 * 1.4
    expected["robust-stability-r2-q2"] = max(0.3 * 2.0, 0.9 * 0.5)
    expected["robust-stability-r4-q1"] = 1.0 / 0.5

    # Breakaway of 1/(s(s+6)): K = -s(s+6), critical point where dK/ds = 0.
    s_break = -3.0
    expected["root-locus-r1-q2"] = -s_break * (s_break + 6.0)
    expected["root-locus-r1-q3"] = (-1.0 - 4.0 - 7.0) / 3.0
    expected["root-locus-r2-q2"] = 180.0 / 3.0
    other = np.array([-2.0, -2.0])
    here = np.array([-2.0, 2.0])
    angle = math.degrees(math.atan2(*(here - other)[::-1]))
    expected["root-locus-r4-q1"] = 180.0 - angle

    u = np.array([1.0, 2.0, 3.0])
    y = np.array([2.0, 4.0, 7.0])
    theta, *_ = np.linalg.lstsq(u.reshape(-1, 1), y, rcond=None)
    expected["sys-id-r1-q2"] = 10.0 / 4.0
    expected["sys-id-r1-q3"] = float(theta[0])
    expected["sys-id-r2-q2"] = 6.0 / math.sqrt(1.0 + 2.0 ** 2)
    expected["sys-id-r4-q1"] = 11.4 - 2.5 * 4.0

    expected["time-delay-r1-q2"] = math.degrees(0.04 * 10.0)
    expected["time-delay-r1-q3"] = -2.0 / 0.25
    expected["time-delay-r2-q2"] = math.radians(50.0) / 8.0
    expected["time-delay-r4-q1"] = abs(complex(math.cos(-20.0 * 0.15), math.sin(-20.0 * 0.15)))

    numeric = check_expected(banks, expected, mismatches)

    texts = load_texts(SKILLS)
    needles = {
        "loop-shaping": "48.59",
        "lyapunov": "3.75",
        "observability": "0.35",
        "reachability": "-2.56",
        "robust-stability": "0.408",
        "root-locus": "17.5",
        "sys-id": "0.15",
        "time-delay": "0.12",
    }
    for sid, needle in needles.items():
        if needle not in texts[sid]:
            mismatches.append(sid + " worked text missing " + needle)
        bank_blob = json_blob(banks[sid])
        if needle in bank_blob:
            mismatches.append(sid + " worked number leaked into the bank: " + needle)

    finish(numeric, mismatches, banks)


def json_blob(bank):
    import json
    return json.dumps(bank, ensure_ascii=False)


if __name__ == "__main__":
    main()
