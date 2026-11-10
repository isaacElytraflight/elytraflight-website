#!/usr/bin/env python3
"""Independent numeric check for nonlinear-optimization batch NB2.

Recomputes each numeric answer with numpy. Does not import the generator.
Symbolic keys are checked by finish().
"""
import math

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "induced-matrix-norms",
    "frobenius-schatten-norms",
    "open-closed-sets",
    "compact-sets",
    "level-sets-contours",
    "convex-sets",
]


def induced_1(A):
    A = np.abs(np.asarray(A, dtype=float))
    return float(np.max(np.sum(A, axis=0)))


def induced_inf(A):
    A = np.abs(np.asarray(A, dtype=float))
    return float(np.max(np.sum(A, axis=1)))


def induced_2(A):
    singular = np.linalg.svd(np.asarray(A, dtype=float), compute_uv=False)
    return float(np.max(singular))


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    A14 = np.array([[1.0, -4.0], [2.0, 3.0]])
    expected["induced-matrix-norms-r1-q2"] = induced_1(A14)
    expected["induced-matrix-norms-r2-q2"] = induced_inf(A14)
    expected["induced-matrix-norms-r2-q3"] = induced_2(np.diag([3.0, -5.0]))
    expected["induced-matrix-norms-r3-q2"] = induced_2(np.array([[0.0, -6.0], [0.0, 0.0]]))
    expected["induced-matrix-norms-r4-q2"] = induced_2(np.diag([4.0, 7.0]))

    D34 = np.diag([3.0, -4.0])
    sig34 = np.linalg.svd(D34, compute_uv=False)
    expected["frobenius-schatten-norms-r1-q2"] = float(np.linalg.norm(D34, ord="fro"))
    expected["frobenius-schatten-norms-r2-q2"] = float(np.sum(sig34))
    off = np.array([[0.0, 5.0], [12.0, 0.0]])
    sig_off = np.linalg.svd(off, compute_uv=False)
    expected["frobenius-schatten-norms-r2-q3"] = float(np.max(sig_off))
    expected["frobenius-schatten-norms-r3-q2"] = float(np.linalg.norm(off, ord="fro"))
    expected["frobenius-schatten-norms-r4-q2"] = float(np.sum(sig_off ** 2))

    expected["open-closed-sets-r1-q2"] = 7 - np.linalg.norm([2.0, 0.0])
    expected["open-closed-sets-r2-q2"] = min(4 - 1, 8 - 4)
    expected["open-closed-sets-r2-q3"] = 3 + 1  # three given points, plus the limit 0
    expected["open-closed-sets-r3-q2"] = 4.0
    expected["open-closed-sets-r4-q2"] = float(np.dot([1.0, 2.0], [1.0, 2.0]))

    expected["compact-sets-r1-q2"] = float(np.linalg.norm([5.0, 12.0]))
    expected["compact-sets-r2-q2"] = float(np.linalg.norm([6.0, 8.0]))
    expected["compact-sets-r2-q3"] = 1  # bounded, not closed
    pts = np.array([[1.0, 2.0], [4.0, -2.0], [-5.0, 0.0]])
    expected["compact-sets-r3-q2"] = float(np.max(np.linalg.norm(pts, axis=1)))
    expected["compact-sets-r4-q2"] = (3 - 3) ** 2 + 4

    expected["level-sets-contours-r1-q2"] = math.sqrt(16)
    expected["level-sets-contours-r2-q2"] = math.sqrt(16 / 4)
    expected["level-sets-contours-r3-q2"] = 10 - 2 * 3
    expected["level-sets-contours-r4-q2"] = math.sqrt(36 / 4)

    expected["convex-sets-r1-q2"] = (2 + 8) / 2
    expected["convex-sets-r2-q2"] = 0.25 * 12
    mid = 0.5 * (np.array([2.0, 1.0]) + np.array([4.0, 3.0]))
    expected["convex-sets-r2-q3"] = float(mid[0] + 2 * mid[1])
    combo = 0.5 * np.array([0.0, 0.0]) + 0.25 * np.array([8.0, 0.0]) + 0.25 * np.array([0.0, 8.0])
    expected["convex-sets-r3-q2"] = float(combo[0])
    mid2 = 0.5 * np.array([4.0, 2.0])
    expected["convex-sets-r4-q2"] = float(mid2[0] + 2 * mid2[1])

    numeric = check_expected(banks, expected, mismatches)

    def need(sid, snippet):
        if snippet not in texts[sid]:
            mismatches.append(f"{sid} explainer missing {snippet!r}")

    rows = np.array([[8.0, 0.0, 0.0], [1.0, 1.0, 1.0]])
    need("induced-matrix-norms", f"1-norm is {induced_1(rows):.0f}")
    need("induced-matrix-norms", f"infinity-norm is {induced_inf(rows):.0f}")
    worked = np.diag([6.0, -8.0])
    wsig = np.linalg.svd(worked, compute_uv=False)
    need("frobenius-schatten-norms", f"Frobenius norm is {np.linalg.norm(worked, ord='fro'):.0f}")
    need("frobenius-schatten-norms", f"nuclear norm is {np.sum(wsig):.0f}")
    need("frobenius-schatten-norms", f"spectral norm is {np.max(wsig):.0f}")
    gap = 6 - abs(5 - 2)
    need("open-closed-sets", f"gap is {gap:.0f}")
    corner = float(np.linalg.norm([8.0, 15.0]))
    need("compact-sets", f"distance is {corner:.0f}")
    need("level-sets-contours", "semi-axes are 5 and 3")
    lhs = 3 + 3 * 2
    need("convex-sets", f"left-hand side is {lhs:.0f}")

    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
