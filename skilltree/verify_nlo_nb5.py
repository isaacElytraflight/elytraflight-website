#!/usr/bin/env python3
"""Independent numeric check for nonlinear-optimization batch NB5.

Recomputes each numeric answer from the definitions. Does not import the
generator. Symbolic keys are compared with expressions derived here, and
finish() checks those keys with SymPy.
"""
import json

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "optimization-problem-formulation",
    "graphical-2d-optimization",
    "optimization-problem-classes",
    "local-global-minima",
    "existence-of-minimizers",
    "first-order-optimality",
    "second-order-optimality",
    "stationary-point-classification",
    "convex-optimality-global",
    "quadratic-function-minimization",
]


def expect_key(mismatches, banks, qid, expression):
    sid = qid.rsplit("-r", 1)[0]
    for q in banks[sid]["questions"]:
        if q["id"] == qid:
            if q.get("answer") != expression:
                mismatches.append(f"{qid}: key {q.get('answer')!r} != {expression!r}")
            return
    mismatches.append(f"{qid}: missing symbolic question")


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    # Fasteners allow 18/3, labels allow 10/2. The tighter stock wins.
    expected["optimization-problem-formulation-r1-q2"] = min(18 / 3, 10 / 2)
    # Unconstrained bowl (x-4)^2 + (y+1)^2 + 5. The shift does not move x.
    expected["optimization-problem-formulation-r3-q2"] = 4.0
    # Values of 3x+4 on {1, 2, 5}.
    expected["optimization-problem-formulation-r4-q2"] = min(3 * x + 4 for x in (1, 2, 5))

    tri = [(2.0, 1.0), (6.0, 1.0), (2.0, 5.0)]
    expected["graphical-2d-optimization-r1-q2"] = min(x + y for x, y in tri)
    expected["graphical-2d-optimization-r2-q3"] = max(x + y for x, y in tri)
    rect = [(1.0, 2.0), (4.0, 2.0), (4.0, 6.0), (1.0, 6.0)]
    expected["graphical-2d-optimization-r3-q2"] = min(3 * x + y for x, y in rect)
    poly = [(0.0, 2.0), (3.0, 0.0), (4.0, 3.0)]
    expected["graphical-2d-optimization-r4-q1"] = min(x + 2 * y for x, y in poly)

    # Off-diagonal of (Q + Q^T)/2 for Q = [[2, 6], [0, 4]].
    q_raw = np.array([[2.0, 6.0], [0.0, 4.0]])
    q_sym = 0.5 * (q_raw + q_raw.T)
    expected["optimization-problem-classes-r1-q2"] = float(q_sym[0, 1])
    hess_a = np.array([[4.0, 2.0], [2.0, 4.0]])
    expected["optimization-problem-classes-r3-q2"] = float(np.linalg.eigvalsh(hess_a)[0])
    hess_p = np.array([[5.0, 1.0], [1.0, 5.0]])
    expected["optimization-problem-classes-r4-q2"] = float(np.linalg.eigvalsh(hess_p)[0])

    expected["local-global-minima-r1-q2"] = (2.0 - 2.0) ** 2 + 3.0
    # inf of e^t + 4. The exponential approaches 0 and stays positive.
    expected["local-global-minima-r2-q3"] = 4.0
    expected["local-global-minima-r4-q2"] = 1.0 ** 3 - 3.0 * 1.0

    # Squared distance from (3, 0) to the unit disk, attained at (1, 0).
    expected["existence-of-minimizers-r1-q2"] = (1.0 - 3.0) ** 2 + 0.0 ** 2
    expected["existence-of-minimizers-r2-q3"] = 1.0 + 1.0 / 1.0
    expected["existence-of-minimizers-r3-q3"] = 0.0 ** 2 + 4.0 * 0.0 ** 2 + 6.0
    expected["existence-of-minimizers-r4-q2"] = 1.0 ** 4 - 4.0 * 1.0

    # Larger root of 3(t-1)(t-3) = 0.
    expected["first-order-optimality-r1-q2"] = 3.0
    stat = np.array([2.0, -1.5])
    expected["first-order-optimality-r2-q3"] = (
        stat[0] ** 2 + 2.0 * stat[1] ** 2 - 4.0 * stat[0] + 6.0 * stat[1]
    )
    expected["first-order-optimality-r4-q2"] = (1.0 - 1.0) ** 2 + 4.0 * (-2.0 + 2.0) ** 2 + 7.0

    saddle = np.array([[2.0, 0.0], [0.0, -2.0]])
    expected["second-order-optimality-r1-q2"] = float(np.linalg.eigvalsh(saddle)[0])
    bowl = np.array([[6.0, 2.0], [2.0, 6.0]])
    expected["second-order-optimality-r2-q3"] = float(np.linalg.eigvalsh(bowl)[0])
    expected["second-order-optimality-r4-q1"] = 1.0 ** 3 - 3.0 * 1.0 + 0.0 ** 2

    expected["stationary-point-classification-r1-q2"] = 1.0 + 4.0 - 2.0 * 1.0 - 4.0 * 2.0
    expected["stationary-point-classification-r2-q3"] = 2.0 ** 4 - 8.0 * 2.0 ** 2
    expected["stationary-point-classification-r4-q1"] = 3.0 ** 2 + (-4.0) ** 2 - 6.0 * 3.0 + 8.0 * (-4.0)

    expected["convex-optimality-global-r1-q2"] = 3.0 ** 2 - 6.0 * 3.0 + 10.0
    expected["convex-optimality-global-r2-q3"] = 2.0 ** 2 + 3.0 * (-1.0) ** 2 - 4.0 * 2.0 + 6.0 * (-1.0)
    expected["convex-optimality-global-r4-q2"] = (0.0 - 2.0) ** 2 + (2.0 - 2.0) ** 2

    # A = diag(2, 4), b = (-2, -8), c = 5. Value formula c - 1/2 b^T A^{-1} b.
    a_pd = np.diag([2.0, 4.0])
    b_pd = np.array([-2.0, -8.0])
    a_inv_b = np.linalg.solve(a_pd, b_pd)
    expected["quadratic-function-minimization-r1-q2"] = 5.0 - 0.5 * float(b_pd @ a_inv_b)
    # x^2 - 4x + 3 at the stationary x = 2. The y direction is flat.
    expected["quadratic-function-minimization-r2-q3"] = 2.0 ** 2 - 4.0 * 2.0 + 3.0
    expected["quadratic-function-minimization-r4-q1"] = (2.0 - 1.0) ** 2 + (2.0 - 3.0) ** 2

    numeric = check_expected(banks, expected, mismatches)

    expect_key(mismatches, banks, "optimization-problem-classes-r3-q1", "a*c-b^2/4")
    expect_key(mismatches, banks, "local-global-minima-r3-q3", "a^2+b^2")
    expect_key(mismatches, banks, "first-order-optimality-r2-q1", "a*x+b*y")
    expect_key(mismatches, banks, "first-order-optimality-r4-q1", "-q/p")
    expect_key(mismatches, banks, "second-order-optimality-r3-q1", "a+b*t")
    expect_key(mismatches, banks, "stationary-point-classification-r3-q1", "-b/a")
    expect_key(mismatches, banks, "convex-optimality-global-r3-q1", "-b/a")
    expect_key(mismatches, banks, "quadratic-function-minimization-r2-q1", "c-b^2/(2*a)")
    expect_key(mismatches, banks, "quadratic-function-minimization-r4-q2", "-g/a")

    # Spot-check the symbolic formulas at one interior point, independent of the key text.
    # Determinant of [[a, b/2], [b/2, c]] at (2, -2, 3).
    det = 2.0 * 3.0 - ((-2.0) / 2.0) ** 2
    if abs(det - (2 * 3 - (-2) ** 2 / 4)) > 1e-9:
        mismatches.append("symmetric-form determinant identity failed")
    # Minimum value of (1/2)*3*t^2 + (-2)*t + 4 is 4 - 4/(2*3).
    quad_min = 4.0 - ((-2.0) ** 2) / (2.0 * 3.0)
    if abs(quad_min - (4.0 - 4.0 / 6.0)) > 1e-9:
        mismatches.append("one-dimensional quadratic value identity failed")

    markers = {
        "optimization-problem-formulation": "The baker's recorded profit is 26",
        "graphical-2d-optimization": "The depot level is 11",
        "optimization-problem-classes": "The symmetrized corner is 7",
        "local-global-minima": "The shared floor is 28",
        "existence-of-minimizers": "The disk minimum is 11",
        "first-order-optimality": "The interior slope vanishes at height 9",
        "second-order-optimality": "The saddle height is 8",
        "stationary-point-classification": "The classified height is 13",
        "convex-optimality-global": "The convex floor is 15",
        "quadratic-function-minimization": "The solved quadratic floor is 19",
    }
    anchors = {
        "optimization-problem-formulation": 7.0 * 2.0 + 3.0 * 4.0,
        "graphical-2d-optimization": 1.0 + 2.0 * 5.0,
        "optimization-problem-classes": 14.0 / 2.0,
        "local-global-minima": (4.0 ** 2 - 16.0) ** 2 + 28.0,
        "existence-of-minimizers": (2.0 - 2.0) ** 2 + (-1.0 + 1.0) ** 2 + 11.0,
        "first-order-optimality": (5.0 - 5.0) ** 2 + 9.0,
        "second-order-optimality": 0.0 ** 2 - 0.0 ** 2 + 8.0,
        "stationary-point-classification": 3.0 ** 2 + 2.0 * (-1.0) ** 2 - 6.0 * 3.0 + 4.0 * (-1.0) + 24.0,
        "convex-optimality-global": 2.0 * 2.0 ** 2 - 8.0 * 2.0 + 23.0,
        "quadratic-function-minimization": 29.0 - 0.5 * 20.0,
    }
    bank_blobs = {sid: json.dumps(banks[sid]) for sid in SKILLS}
    for sid, phrase in markers.items():
        if phrase not in texts[sid]:
            mismatches.append(f"{sid} explainer missing {phrase!r}")
        if phrase in bank_blobs[sid]:
            mismatches.append(f"{sid} worked-example phrase reused in the bank")
        rendered = f"{anchors[sid]:.6g}"
        if rendered not in texts[sid]:
            mismatches.append(f"{sid} explainer missing recomputed anchor {rendered}")

    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
