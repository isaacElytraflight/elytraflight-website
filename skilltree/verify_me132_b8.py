#!/usr/bin/env python3
"""Independent numeric check for ME 132 batch B8.

The generator stores closed forms. This file recomputes them from the
covariance map, the scalar Riccati, and the one-step quadratic. It does
not import the generator.
"""
import json
import math

from verify_harness import check_expected, check_symbolic, finish, load_banks, load_texts

SKILLS = [
    "fb-linearization",
    "gain-scheduling",
    "gen-controller",
    "integral-action",
    "gaussian-random-vectors",
    "kalman",
    "kalman-optimal-observer",
    "lqr",
    "mpc",
    "separation",
]


def steady_predicted(q, r):
    """Positive root of P^2 - q P - q r = 0, for a = 1 and c = 1."""
    return (q + math.sqrt(q * q + 4.0 * q * r)) / 2.0


def filter_gain(p, c, r):
    return (p * c) / (c * c * p + r)


def joseph(p, ell, c, r):
    return (1.0 - ell * c) ** 2 * p + (ell ** 2) * r


def lqr_gain(a, b, q, r):
    """Stabilizing scalar gain. The quadratic is (b^2/r) P^2 - 2 a P - q = 0."""
    aa = (b * b) / r
    bb = -2.0 * a
    cc = -q
    p = (-bb + math.sqrt(bb * bb - 4.0 * aa * cc)) / (2.0 * aa)
    return (b / r) * p


def one_step(x, rho, bound):
    raw = -x / (1.0 + rho)
    return max(-bound, min(bound, raw))


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    expected = {}

    # c^2 v, 1^2*2 + 2^2*5, (A P A^T)_11 for A=[[0,2],[1,0]] and P=diag(3,5).
    # Predicted 0.5^2 * 1 + 0.1.
    expected["gaussian-random-vectors-r1-q2"] = 3.0 ** 2 * 4.0
    expected["gaussian-random-vectors-r1-q3"] = 1.0 ** 2 * 2.0 + 2.0 ** 2 * 5.0
    expected["gaussian-random-vectors-r2-q2"] = 2.0 * 5.0 * 2.0
    expected["gaussian-random-vectors-r4-q1"] = 0.5 ** 2 * 1.0 + 0.1

    # a^2 P + Q, L = P/(P+R), posterior (1-L)P, steady predicted variance.
    expected["kalman-r1-q2"] = 0.5 ** 2 * 4.0 + 1.0
    expected["kalman-r1-q3"] = filter_gain(2.0, 1.0, 2.0)
    expected["kalman-r2-q2"] = (1.0 - 0.5 * 1.0) * 2.0
    expected["kalman-r4-q1"] = steady_predicted(2.0, 4.0)

    # Minimum posterior, innovation variance, Joseph gap, steady posterior.
    p1, r1 = 8.0, 2.0
    l1 = filter_gain(p1, 1.0, r1)
    expected["kalman-optimal-observer-r1-q2"] = (1.0 - l1) * p1
    expected["kalman-optimal-observer-r1-q3"] = p1 + r1
    hand = joseph(5.0, 0.2, 1.0, 5.0)
    opt = joseph(5.0, filter_gain(5.0, 1.0, 5.0), 1.0, 5.0)
    expected["kalman-optimal-observer-r2-q2"] = hand - opt
    steady_p = steady_predicted(4.0, 3.0)
    steady_l = filter_gain(steady_p, 1.0, 3.0)
    expected["kalman-optimal-observer-r4-q1"] = (1.0 - steady_l) * steady_p

    # Real-part sums and the coefficient of s for a pair of eigenvalues.
    expected["separation-r1-q2"] = -2.0 - 3.0 - 8.0 - 10.0
    expected["separation-r1-q3"] = -((2.0 - 1.0 * 5.0) + (2.0 - 6.0 * 1.0))
    expected["separation-r2-q2"] = -1.0 - 2.0 * 3.0
    expected["separation-r4-q1"] = -1.0 - 4.0 - 6.0 - 6.0

    # Command F r - K x, and the steady feedforward F = K - a/b.
    expected["gen-controller-r1-q2"] = 4.0 * 1.0 - 1.5 * 2.0
    expected["gen-controller-r1-q3"] = 3.0 - (-2.0) / 4.0
    expected["gen-controller-r2-q2"] = 2.5 * 2.0 - 0.5 * 3.0
    expected["gen-controller-r4-q1"] = 2.5 - (-1.0) / 2.0

    # Constant term fixes k_i; coefficient of s fixes k; xi = u / k_i.
    expected["integral-action-r1-q2"] = 1.0 * 2.0
    expected["integral-action-r1-q3"] = 10.0 / 2.0
    expected["integral-action-r2-q2"] = (5.0 + 1.0) / 2.0
    expected["integral-action-r4-q1"] = 4.0 / 0.5

    expected["lqr-r1-q2"] = math.sqrt(4.0 / 1.0)
    expected["lqr-r1-q3"] = math.sqrt(9.0 / 4.0)
    expected["lqr-r2-q2"] = lqr_gain(1.0, 1.0, 3.0, 1.0)
    expected["lqr-r4-q1"] = math.sqrt(36.0 / 4.0)

    expected["mpc-r1-q2"] = 4.0 * 0.5
    expected["mpc-r1-q3"] = one_step(6.0, 2.0, 1.0)
    expected["mpc-r2-q2"] = one_step(5.0, 4.0, 100.0)
    expected["mpc-r4-q1"] = one_step(9.0, 2.0, 1.5)

    # u = (v - f) / g.
    expected["fb-linearization-r1-q2"] = (0.0 - 3.0 ** 2) / 2.0
    expected["fb-linearization-r1-q3"] = (-8.0 - 8.0) / 4.0
    expected["fb-linearization-r2-q2"] = (-2.0 - 1.0) / 0.5
    expected["fb-linearization-r4-q1"] = (-2.0 * 1.5 - 4.5) / 1.5

    expected["gain-scheduling-r1-q2"] = 2.0 + (8.0 - 2.0) * (2.5 / 10.0)
    expected["gain-scheduling-r1-q3"] = 1.0 + (5.0 - 1.0) * ((6.0 - 4.0) / (12.0 - 4.0))
    expected["gain-scheduling-r2-q2"] = (1.0 - 0.25) * 4.0 + 0.25 * 12.0
    expected["gain-scheduling-r4-q1"] = 0.5 * 6.0 + 0.5 * 14.0

    numeric = check_expected(banks, expected, mismatches)

    texts = load_texts(SKILLS)
    needles = {
        "gaussian-random-vectors": "1.156",
        "kalman": "0.87",
        "kalman-optimal-observer": "0.5625",
        "lqr": "1.69",
        "mpc": "5.61",
        "separation": "4.70",
        "integral-action": "3.04",
        "fb-linearization": "2.375",
        "gain-scheduling": "2.15",
        "gen-controller": "1.15",
    }
    for sid, needle in needles.items():
        if needle not in texts[sid]:
            mismatches.append(sid + " worked text missing " + needle)
        if needle in json.dumps(banks[sid], ensure_ascii=False):
            mismatches.append(sid + " worked number leaked into the bank: " + needle)

    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
