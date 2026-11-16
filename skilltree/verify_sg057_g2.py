#!/usr/bin/env python3
"""Independent check for SG-057 group 2.

Re-runs the batch verifiers whose banks this group edited, then recomputes
every numeric answer on the two new banks and the numeric answers added to
the edited banks. Does not import the generator.
"""
import os
import subprocess
import sys

import numpy as np

from verify_harness import check_expected, finish, load_banks

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRIOR = [
    "skilltree/verify_me132_b1.py",
    "skilltree/verify_me132_b4.py",
    "skilltree/verify_me132_b6.py",
    "skilltree/verify_nlo_nb1.py",
    "skilltree/verify_nlo_nb7.py",
]


def check_listed(banks, expected, mismatches, rel=2e-3):
    """Recompute a listed subset. Does not require every numeric in the bank."""
    from verify_harness import answer

    n = 0
    for qid, exp in expected.items():
        got = answer(banks, qid)
        n += 1
        scale = max(abs(float(exp)), 1e-9)
        if abs(got - float(exp)) / scale > rel:
            mismatches.append(f"{qid}: bank {got} != recomputed {exp}")
    return n


def main():
    mismatches = []
    for script in PRIOR:
        proc = subprocess.run(
            [sys.executable, script],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
            mismatches.append(script + " failed: " + " | ".join(tail[-8:]))

    banks = load_banks(["eigenvalues-diagonalization", "least-squares-quadratic"])
    expected = {}

    tri = np.array([[5.0, 1.0], [0.0, -2.0]])
    expected["eigenvalues-diagonalization-r1-q2"] = float(np.linalg.eigvals(tri).real.max())
    full = np.array([[6.0, 1.0], [2.0, 5.0]])
    expected["eigenvalues-diagonalization-r2-q2"] = float(np.linalg.eigvals(full).real.max())
    a_vec = np.array([[3.0, 1.0], [0.0, 4.0]])
    v = np.array([1.0, 1.0])
    stretch = a_vec @ v
    expected["eigenvalues-diagonalization-r3-q2"] = float(stretch[0] / v[0])
    closer = np.array([[-1.0, 4.0], [0.0, -6.0]])
    ev = np.linalg.eigvals(closer).real
    expected["eigenvalues-diagonalization-r4-q1"] = float(ev[np.argmin(np.abs(ev))])
    sym = np.array([[8.0, 2.0], [2.0, 5.0]])
    expected["eigenvalues-diagonalization-r4-q2"] = float(np.linalg.eigvalsh(sym).max())

    expected["least-squares-quadratic-r1-q2"] = 9.0 / 3.0
    column = np.array([[3.0], [6.0]])
    rhs = np.array([3.0, 3.0])
    expected["least-squares-quadratic-r2-q2"] = float(np.linalg.lstsq(column, rhs, rcond=None)[0][0])
    tall = np.array([[1.0], [3.0]])
    tall_b = np.array([2.0, 6.0])
    expected["least-squares-quadratic-r3-q2"] = float(np.linalg.lstsq(tall, tall_b, rcond=None)[0][0])
    expected["least-squares-quadratic-r4-q1"] = float(np.mean([1.0, 1.0, 16.0]))
    orth = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    orth_b = np.array([1.0, 9.0, 5.0])
    orth_x = np.linalg.lstsq(orth, orth_b, rcond=None)[0]
    expected["least-squares-quadratic-r4-q3"] = float(orth_x[0])

    numeric = check_expected(banks, expected, mismatches)

    edited = load_banks([
        "lin-algebra-review",
        "eig-modes",
        "spectral-decomposition",
        "linear-least-squares",
        "sys-id",
    ])
    product = np.array([[3.0, -2.0], [5.0, 1.0]]) @ np.array([2.0, 1.0])
    u = 2.0 ** -0.5
    basis = np.array([[u, u], [u, -u]])
    rebuilt = basis @ np.diag([12.0, 4.0]) @ basis.T
    mags = np.array([-9.0, 1.0])
    theta = np.linalg.lstsq(
        np.array([[2.0], [3.0], [5.0]]),
        np.array([4.0, 7.0, 8.0]),
        rcond=None,
    )[0]
    moved = {
        "lin-algebra-review-r2-q5": float(product[1]),
        "lin-algebra-review-r4-q4": float(np.linalg.matrix_rank(
            np.array([[1.0, 0.0], [2.0, 1.0], [0.0, 3.0]])
        )),
        "eig-modes-r2-q4": 1.0 / 8.0,
        "spectral-decomposition-r2-q4": float(rebuilt[0, 0]),
        "spectral-decomposition-r4-q4": float(mags[np.argmax(np.abs(mags))]),
        "linear-least-squares-r4-q4": float(theta[0]),
        "sys-id-r1-q4": 2.4,
        "sys-id-r3-q4": 5.5 - 8.0,
    }
    numeric += check_listed(edited, moved, mismatches)
    finish(numeric, mismatches, {**banks, **edited})


if __name__ == "__main__":
    main()
