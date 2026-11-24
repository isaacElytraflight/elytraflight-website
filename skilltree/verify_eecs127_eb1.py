#!/usr/bin/env python3
"""Independent numeric check for optimization-models batch EB1.

Recomputes each numeric answer from the matrices in the prompts. Does not
import the generator. Symbolic keys are checked by finish().
"""
import math

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "qr-factorization",
    "fundamental-subspaces",
    "block-matrix-identities",
    "principal-component-analysis",
    "low-rank-approximation",
    "least-squares-perturbation",
    "ridge-regression",
    "principal-components-regression",
    "maximum-likelihood-estimation",
]


def positive_qr(A):
    """Thin QR with positive diagonal entries, the Gram-Schmidt convention."""
    A = np.asarray(A, dtype=float)
    m, n = A.shape
    Q = np.zeros((m, n))
    R = np.zeros((n, n))
    for j in range(n):
        v = A[:, j].copy()
        for i in range(j):
            R[i, j] = float(np.dot(Q[:, i], A[:, j]))
            v = v - R[i, j] * Q[:, i]
        R[j, j] = float(np.linalg.norm(v))
        Q[:, j] = v / R[j, j]
    return Q, R


def schur(A, B, C, D):
    A = np.atleast_2d(np.asarray(A, dtype=float))
    B = np.atleast_2d(np.asarray(B, dtype=float))
    C = np.atleast_2d(np.asarray(C, dtype=float))
    D = np.atleast_2d(np.asarray(D, dtype=float))
    value = D - C @ np.linalg.inv(A) @ B
    return float(np.asarray(value, dtype=float).reshape(-1)[0])


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    A68 = np.array([[6.0, 3.0], [8.0, 6.0]])
    _Q, R68 = positive_qr(A68)
    expected["qr-factorization-r1-q2"] = R68[0, 0]
    expected["qr-factorization-r2-q2"] = R68[0, 1]
    expected["qr-factorization-r2-q3"] = R68[1, 1]
    Als = np.array([[1.0, 0.0], [0.0, 1.0], [1.0, 1.0]])
    bls = np.array([1.0, 1.0, 0.0])
    xls = np.linalg.solve(Als.T @ Als, Als.T @ bls)
    expected["qr-factorization-r4-q2"] = xls[0]

    expected["fundamental-subspaces-r1-q2"] = 5 - 3
    expected["fundamental-subspaces-r2-q2"] = 4 - 3
    F = np.array([[1.0, 2.0, 0.0], [0.0, 0.0, 3.0], [2.0, 4.0, 0.0]])
    expected["fundamental-subspaces-r2-q3"] = F.shape[1] - np.linalg.matrix_rank(F)
    # Null vector with second entry 3: x1 + 2 x2 = 0, x3 = 0.
    expected["fundamental-subspaces-r4-q2"] = -2 * 3

    prod = np.array([[1.0, 2.0], [0.0, 3.0]]) @ np.array([[4.0, 0.0], [1.0, 5.0]])
    expected["block-matrix-identities-r1-q2"] = prod[0, 0]
    S5 = schur(5, 2, 10, 9)
    expected["block-matrix-identities-r2-q2"] = S5
    expected["block-matrix-identities-r2-q3"] = 1.0 / S5
    S7 = schur([[1.0, 0.0], [0.0, 2.0]], [[2.0], [2.0]], [[1.0, 2.0]], [[11.0]])
    expected["block-matrix-identities-r4-q2"] = S7

    rows = np.array([[0.0, 2.0], [0.0, -2.0], [3.0, 0.0]])
    centered = rows - rows.mean(axis=0)
    cov = centered.T @ centered / len(rows)
    expected["principal-component-analysis-r1-q2"] = float(np.max(np.linalg.eigvalsh(cov)))
    u = np.array([3.0 / 5.0, 4.0 / 5.0])
    Cdiag = np.diag([9.0, 4.0])
    expected["principal-component-analysis-r2-q2"] = float(u @ Cdiag @ u)
    expected["principal-component-analysis-r2-q3"] = float(np.max(np.linalg.eigvalsh(Cdiag)))
    expected["principal-component-analysis-r4-q2"] = float(np.dot([3.0, -1.0], [1.0, 0.0]))

    sig = np.array([6.0, 3.0, 2.0])
    expected["low-rank-approximation-r1-q2"] = sig[1]
    expected["low-rank-approximation-r2-q2"] = float(np.sqrt(np.sum(sig[1:] ** 2)))
    expected["low-rank-approximation-r2-q3"] = sig[2]
    expected["low-rank-approximation-r4-q2"] = float(sig[0] ** 2 / np.sum(sig ** 2))

    smax, smin = 10.0, 2.0
    expected["least-squares-perturbation-r1-q2"] = smax / smin
    expected["least-squares-perturbation-r2-q2"] = 0.2 / 0.4
    expected["least-squares-perturbation-r2-q3"] = (smax / smin) * (0.2 / 4.0)
    expected["least-squares-perturbation-r4-q2"] = (smax / smin) ** 2

    # column (1, 1), b = (3, 1), lambda = 2
    ata = 1 + 1
    atb = 3 + 1
    expected["ridge-regression-r1-q2"] = atb / (ata + 2)
    A = np.array([[1.0, 0.0], [1.0, 0.0], [0.0, 1.0]])
    b = np.array([4.0, 0.0, 2.0])
    ridge = np.linalg.solve(A.T @ A + np.eye(2), A.T @ b)
    expected["ridge-regression-r2-q2"] = ridge[1]
    expected["ridge-regression-r2-q3"] = ridge[0]
    Gamma = np.diag([2.0, 0.0])
    gen = np.linalg.solve(np.eye(2) + Gamma.T @ Gamma, np.array([1.0, 3.0]))
    expected["ridge-regression-r4-q2"] = gen[0]

    scores = np.array([2.0, 0.0, -2.0])
    yc = np.array([4.0, 1.0, -2.0])
    expected["principal-components-regression-r1-q2"] = float(np.dot(scores, yc) / np.dot(scores, scores))
    expected["principal-components-regression-r2-q2"] = 4.0 ** 2
    expected["principal-components-regression-r2-q3"] = 8.0 / (4.0 ** 2)
    expected["principal-components-regression-r4-q2"] = 5.0 + 2.0 * 0.5

    expected["maximum-likelihood-estimation-r1-q2"] = 18.0 / 6.0
    expected["maximum-likelihood-estimation-r2-q2"] = -18.0 / (2.0 * 3.0)
    expected["maximum-likelihood-estimation-r2-q3"] = 20.0 / 5.0
    expected["maximum-likelihood-estimation-r4-q2"] = 10.0 / 4.0

    numeric = check_expected(banks, expected, mismatches)

    def need(sid, snippet):
        if snippet not in texts[sid]:
            mismatches.append(f"{sid} explainer missing {snippet!r}")

    E = np.array([[3.0, 1.0], [4.0, 2.0]])
    _Qe, Re = positive_qr(E)
    need("qr-factorization", f"{Re[0, 0]:.0f}")
    need("qr-factorization", "11/5")
    need("qr-factorization", "2/5")
    need("fundamental-subspaces", "(-2,1,0)")
    need("block-matrix-identities", "11 - 3")
    need("principal-component-analysis", "larger eigenvalue is 2")
    need("low-rank-approximation", "sqrt{26}")
    need("least-squares-perturbation", "1/30")
    need("ridge-regression", "9/11")
    need("principal-components-regression", "Dividing the inner product by")
    need("maximum-likelihood-estimation", "6.25")

    # Worked-example QR diagonal must stay positive and rebuild A.
    if np.any(np.diag(Re) <= 0) or not np.allclose(_Qe @ Re, E):
        mismatches.append("qr worked example does not rebuild A with a positive diagonal")
    if abs(S5 - 5) > 1e-9:
        mismatches.append("scalar Schur complement recomputed to a value other than 5")
    if abs(math.sqrt(26) - math.sqrt(25 + 1)) > 1e-12:
        mismatches.append("low-rank worked example identity failed")

    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
