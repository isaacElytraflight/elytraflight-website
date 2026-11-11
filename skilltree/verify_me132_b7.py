#!/usr/bin/env python3
"""Independent numeric check for ME 132 batch B7.

The generator stores closed forms. This file recomputes them by matching
characteristic polynomials, by the sensitivity-area balance, and by the
gradient update. It does not import the generator.
"""
import math

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = ["adaptive", "fund-limits", "observer", "robust-perf", "state-feedback"]


def match_k(a, b, desired):
    """Row gain K such that the characteristic polynomial of A - B K is desired.

    desired is [1, coeff of s, constant term] for a quadratic, highest power first.
    The polynomial is affine in the entries of K, so two probes determine it.
    """
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    desired = np.asarray(desired, float)
    n = a.shape[0]
    base = np.poly(a)
    cols = []
    for i in range(n):
        k = np.zeros((1, n))
        k[0, i] = 1.0
        cols.append(np.poly(a - b @ k) - base)
    system = np.column_stack(cols)[1:]
    rhs = desired[1:] - base[1:]
    return np.linalg.solve(system, rhs)


def match_l(a, c, desired):
    """Column L such that A - L C has the desired polynomial. Dual of match_k."""
    a = np.asarray(a, float)
    c = np.asarray(c, float).reshape(1, -1)
    return match_k(a.T, c.T, desired)


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    expected = {}

    # Scalar: 3 - 2K = -5. Companion: constant term 3 + k1 = 12.
    expected["state-feedback-r1-q2"] = (3.0 - (-5.0)) / 2.0
    expected["state-feedback-r1-q3"] = 2.0 + 8.0
    expected["state-feedback-r2-q2"] = float(match_k(
        [[0.0, 1.0], [-3.0, -1.0]], [[0.0], [1.0]], [1.0, 7.0, 12.0]
    )[0])
    expected["state-feedback-r4-q1"] = float(match_k(
        [[0.0, 1.0], [-3.0, -2.0]], [[0.0], [0.5]], [1.0, 4.0, 16.0]
    )[0])

    # Scalar: -2 - 4L = -9. Coefficient of s for poles -6 and -10.
    expected["observer-r1-q2"] = (-2.0 - (-9.0)) / 4.0
    expected["observer-r1-q3"] = 6.0 + 10.0
    expected["observer-r2-q2"] = float(match_l(
        [[0.0, 1.0], [-4.0, -3.0]], [1.0, 0.0], [1.0, 12.0, 32.0]
    )[0])
    expected["observer-r4-q1"] = float(match_l(
        [[0.0, 1.0], [-6.0, -1.0]], [0.0, 1.0], [1.0, 12.0, 35.0]
    )[1])

    # |S|=1/4 on width 2, hump width 4, zero area. Integral pi*(1.5+3.5).
    # Hump |S|=8 balances a dip |S|=1/2 of width 9. Window 20/2 - 2*2.5.
    expected["fund-limits-r1-q2"] = math.exp(math.log(4.0) * 2.0 / 4.0)
    expected["fund-limits-r1-q3"] = math.pi * (1.5 + 3.5)
    expected["fund-limits-r2-q2"] = math.log(2.0) * 9.0 / math.log(8.0)
    expected["fund-limits-r4-q1"] = 20.0 / 2.0 - 2.0 * 2.5

    expected["robust-perf-r1-q2"] = 0.40 + 0.35
    expected["robust-perf-r1-q3"] = 1.2 * 0.5
    expected["robust-perf-r2-q2"] = 0.5 * 0.9 + 0.4 * 1.1
    expected["robust-perf-r4-q1"] = 1.0 - (0.55 + 0.30)

    # eps = 8 - 1*2, rate = 0.5 * eps * 2. Certainty equivalence 4/2.
    # Normalized 0.4*5*3/(1+3^2). Euler 1.5 + 0.2*0.5*4*2.
    expected["adaptive-r1-q2"] = 0.5 * (8.0 - 1.0 * 2.0) * 2.0
    expected["adaptive-r1-q3"] = 4.0 / 2.0
    expected["adaptive-r2-q2"] = 0.4 * 5.0 * 3.0 / (1.0 + 3.0 ** 2)
    expected["adaptive-r4-q1"] = 1.5 + 0.2 * 0.5 * 4.0 * 2.0

    numeric = check_expected(banks, expected, mismatches)

    texts = load_texts(SKILLS)
    needles = {
        "state-feedback": "9.875",
        "observer": "1.726",
        "fund-limits": "5.341",
        "robust-perf": "0.617",
        "adaptive": "0.571",
    }
    for sid, needle in needles.items():
        if needle not in texts[sid]:
            mismatches.append(sid + " worked text missing " + needle)
        if needle in json_blob(banks[sid]):
            mismatches.append(sid + " worked number leaked into the bank: " + needle)

    finish(numeric, mismatches, banks)


def json_blob(bank):
    import json
    return json.dumps(bank, ensure_ascii=False)


if __name__ == "__main__":
    main()
