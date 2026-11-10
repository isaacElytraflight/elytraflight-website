#!/usr/bin/env python3
"""Independent numeric check for nonlinear-optimization batch NB1.

Recomputes each numeric answer with numpy. Does not import the generator.
"""
import math

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "rn-important-subsets",
    "spectral-decomposition",
    "positive-definite-matrices",
    "singular-value-decomposition",
    "rayleigh-quotient",
    "inner-products",
    "vector-norms-lp",
    "cauchy-schwarz-inequality",
]


def rayleigh(A, x):
    x = np.asarray(x, dtype=float)
    return float(x @ A @ x / (x @ x))


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    expected["rn-important-subsets-r1-q2"] = 3
    expected["rn-important-subsets-r2-q2"] = (2 + 10) / 2
    expected["rn-important-subsets-r2-q3"] = 0.2 + 0.5 + 0.3
    expected["rn-important-subsets-r3-q1"] = 4 - 1
    expected["rn-important-subsets-r3-q3"] = 0.25 * 12
    expected["rn-important-subsets-r4-q2"] = 0.5 * 10

    A = np.array([[4.0, 2.0], [2.0, 4.0]])
    ev = np.linalg.eigvalsh(A)
    expected["spectral-decomposition-r1-q2"] = ev.max()
    expected["spectral-decomposition-r2-q2"] = np.linalg.det(A)
    expected["spectral-decomposition-r2-q3"] = np.trace(A)
    D = np.diag([5.0, 1.0])
    x = np.array([2.0, 0.0])
    expected["spectral-decomposition-r3-q2"] = float(x @ D @ x)
    expected["spectral-decomposition-r3-q3"] = np.linalg.eigvalsh(D)[0]
    expected["spectral-decomposition-r4-q2"] = ev.max()

    P = np.diag([2.0, 8.0])
    ones = np.array([1.0, 1.0])
    expected["positive-definite-matrices-r1-q2"] = float(ones @ P @ ones)
    Q = np.array([[1.0, 2.0], [2.0, 1.0]])
    qev = np.linalg.eigvalsh(Q)
    expected["positive-definite-matrices-r2-q2"] = qev.min()
    expected["positive-definite-matrices-r2-q3"] = np.linalg.det(Q)
    # 2 x^2 + 8 y^2 = 8 => x^2/4 + y^2 = 1, semi-axis sqrt(4) = 2
    expected["positive-definite-matrices-r3-q2"] = math.sqrt(8 / 2)
    Z = np.diag([1.0, 0.0])
    v = np.array([3.0, 4.0])
    expected["positive-definite-matrices-r3-q3"] = float(v @ Z @ v)
    expected["positive-definite-matrices-r4-q1"] = min(9.0, 4.0)

    S = np.array([[3.0, 0.0], [0.0, -4.0]])
    svals = np.linalg.svd(S, compute_uv=False)
    expected["singular-value-decomposition-r1-q2"] = svals.max()
    C = np.array([[1.0, 1.0], [0.0, 0.0]])
    cvals = np.linalg.svd(C, compute_uv=False)
    expected["singular-value-decomposition-r2-q1"] = int(np.sum(cvals > 1e-12))
    expected["singular-value-decomposition-r2-q3"] = cvals.max()
    expected["singular-value-decomposition-r3-q2"] = float(np.sum(svals ** 2))
    expected["singular-value-decomposition-r3-q3"] = float(np.prod(svals))
    expected["singular-value-decomposition-r4-q1"] = svals.max()

    R = np.diag([4.0, 1.0])
    expected["rayleigh-quotient-r1-q2"] = rayleigh(R, [1.0, 1.0])
    T = np.array([[5.0, 1.0], [1.0, 3.0]])
    expected["rayleigh-quotient-r2-q1"] = np.trace(T)
    M = np.array([[2.0, 1.0], [1.0, 2.0]])
    expected["rayleigh-quotient-r2-q3"] = np.linalg.det(M)
    expected["rayleigh-quotient-r3-q2"] = rayleigh(M, [1.0, 0.0])
    rev = np.linalg.eigvalsh(R)
    expected["rayleigh-quotient-r3-q3"] = rev.max() - rev.min()
    expected["rayleigh-quotient-r4-q1"] = rev.max() / rev.min()

    expected["inner-products-r1-q2"] = float(np.dot([1, 2, 3], [2, 0, -1]))
    FA = np.array([[1.0, 0.0], [2.0, 3.0]])
    FB = np.array([[1.0, 1.0], [0.0, 1.0]])
    expected["inner-products-r2-q1"] = float(np.sum(FA * FB))
    expected["inner-products-r2-q3"] = float(np.dot([3, 4], [4, 3]))
    expected["inner-products-r3-q2"] = float(np.linalg.norm([3, 4]))
    expected["inner-products-r3-q3"] = 0 * 0 - 1 * 1
    expected["inner-products-r4-q1"] = float(np.linalg.norm([3, 4]) * np.linalg.norm([4, 3]))

    x34 = np.array([3.0, -4.0])
    expected["vector-norms-lp-r1-q2"] = float(np.sum(np.abs(x34)))
    expected["vector-norms-lp-r2-q1"] = float(np.linalg.norm(x34))
    expected["vector-norms-lp-r2-q3"] = float(np.max(np.abs(x34)))
    expected["vector-norms-lp-r3-q2"] = float(np.sum(np.abs([1.0, 1.0, 1.0])))
    expected["vector-norms-lp-r3-q3"] = float(np.linalg.norm([1.0, -1.0, 0.0]))
    expected["vector-norms-lp-r4-q2"] = float(np.sum(np.abs(x34)) / np.max(np.abs(x34)))

    a = np.array([1.0, 2.0])
    c = np.array([2.0, 1.0])
    expected["cauchy-schwarz-inequality-r1-q2"] = float(np.linalg.norm(a) * np.linalg.norm(c))
    expected["cauchy-schwarz-inequality-r2-q1"] = float(np.dot(a, c))
    expected["cauchy-schwarz-inequality-r2-q3"] = float(np.linalg.norm([3.0, 4.0]))
    u = np.array([2.0, 0.0])
    w = np.array([6.0, 0.0])
    expected["cauchy-schwarz-inequality-r3-q2"] = abs(float(np.dot(u, w))) / (
        float(np.linalg.norm(u)) * float(np.linalg.norm(w))
    )
    expected["cauchy-schwarz-inequality-r3-q3"] = float(np.linalg.norm([3.0, 0.0]) + np.linalg.norm([0.0, 4.0]))
    expected["cauchy-schwarz-inequality-r4-q2"] = float(np.linalg.norm(a))

    numeric = check_expected(banks, expected, mismatches)

    def need(sid, snippet):
        if snippet not in texts[sid]:
            mismatches.append(f"{sid} explainer missing {snippet!r}")

    mid = ((4 + 10) / 2, (8 + 16) / 2)
    need("rn-important-subsets", f"({mid[0]:.0f}, {mid[1]:.0f})")
    spec = np.linalg.eigvalsh(np.diag([11.0, 3.0]))
    need("spectral-decomposition", f"{spec.max():.0f} and {spec.min():.0f}")
    form = float(np.array([1.0, 1.0]) @ np.diag([3.0, 12.0]) @ np.array([1.0, 1.0]))
    need("positive-definite-matrices", f"equals {form:.0f}")
    need("positive-definite-matrices", "1.5")
    sig = np.linalg.svd(np.array([[0.0, 6.0], [0.0, 0.0]]), compute_uv=False).max()
    need("singular-value-decomposition", f"singular value {sig:.0f}")
    rq = rayleigh(np.diag([7.0, 5.0]), [1.0, 1.0])
    need("rayleigh-quotient", f"equals {rq:.0f}")
    dot = float(np.dot([3, 2], [2, -3]))
    need("inner-products", f"dot product {dot:.0f}")
    fro = float(np.sum(np.array([[6.0, 1.0], [0.0, 2.0]]) * np.array([[1.0, 0.0], [4.0, 1.0]])))
    need("inner-products", f"value {fro:.0f}")
    vec = np.array([6.0, -8.0])
    need("vector-norms-lp", f"length is {np.linalg.norm(vec):.0f}")
    need("vector-norms-lp", f"sum of absolutes {np.sum(np.abs(vec)):.0f}")
    ip = float(np.dot([3, 1], [1, 3]))
    prod = float(np.linalg.norm([3, 1]) * np.linalg.norm([1, 3]))
    need("cauchy-schwarz-inequality", f"inner product is {ip:.0f}")
    need("cauchy-schwarz-inequality", f"product of the lengths is {prod:.0f}")

    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
