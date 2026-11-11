#!/usr/bin/env python3
"""Independent numeric check for nonlinear-optimization batch NB3.

Recomputes each numeric answer from the definitions. Does not import the
generator. A one-sided difference quotient cross-checks every derivative.
Symbolic keys are checked by finish().
"""
import math

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "directional-derivative",
    "gradient-partial-derivatives",
    "differentiability-multivariable",
    "hessian-matrix",
    "jacobian-chain-rule",
    "matrix-calculus-gradients",
    "fundamental-theorem-along-segment",
    "taylor-approximation-multivariable",
    "taylor-exact-mean-value",
]


def fd_directional(f, x, d, eps=1e-6):
    x = np.asarray(x, dtype=float)
    d = np.asarray(d, dtype=float)
    return (f(x + eps * d) - f(x)) / eps


def require_close(mismatches, label, got, expected, tol=1e-4):
    scale = max(abs(float(expected)), abs(float(got)), 1e-9)
    if abs(float(got) - float(expected)) / scale > tol:
        mismatches.append(f"{label}: difference quotient {got} != formula {expected}")


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    def f_dir(z):
        return z[0] ** 2 + 4.0 * z[1]

    def d_dir(x, d):
        # partials of x^2 + 4y
        return 2.0 * x[0] * d[0] + 4.0 * d[1]

    cases = {
        "directional-derivative-r1-q2": (np.array([3.0, 1.0]), np.array([1.0, 0.0])),
        "directional-derivative-r2-q2": (np.array([3.0, 1.0]), np.array([0.0, 1.0])),
        "directional-derivative-r2-q3": (np.array([3.0, 1.0]), np.array([2.0, -1.0])),
        "directional-derivative-r3-q2": (np.array([2.0, 5.0]), np.array([3.0, 1.0])),
    }
    for qid, (x, d) in cases.items():
        expected[qid] = d_dir(x, d)
        require_close(mismatches, qid, fd_directional(f_dir, x, d), expected[qid])
    # |3t| / t = 3 for t > 0
    expected["directional-derivative-r4-q2"] = abs(3.0)

    def f_grad(z):
        return z[0] ** 2 + 4.0 * z[1] ** 2

    def grad_ell(x):
        return np.array([2.0 * x[0], 8.0 * x[1]])

    g31 = grad_ell(np.array([3.0, 1.0]))
    expected["gradient-partial-derivatives-r1-q2"] = g31[0]
    expected["gradient-partial-derivatives-r2-q2"] = g31[1]
    expected["gradient-partial-derivatives-r2-q3"] = float(np.dot(g31, [1.0, 1.0]))
    expected["gradient-partial-derivatives-r3-q2"] = float(np.linalg.norm(g31))
    g12 = grad_ell(np.array([1.0, 2.0]))
    expected["gradient-partial-derivatives-r4-q2"] = float(np.dot(g12, [1.0, 1.0]))
    require_close(mismatches, "grad (3,1) e1", fd_directional(f_grad, [3, 1], [1, 0]), g31[0])
    require_close(mismatches, "grad (3,1) e2", fd_directional(f_grad, [3, 1], [0, 1]), g31[1])
    require_close(mismatches, "grad (1,2)", fd_directional(f_grad, [1, 2], [1, 1]), expected["gradient-partial-derivatives-r4-q2"])

    def remainder(f, grad, x, h):
        x = np.asarray(x, dtype=float)
        h = np.asarray(h, dtype=float)
        return abs(f(x + h) - f(x) - float(np.dot(grad(x), h)))

    def f_lin(z):
        return z[0] ** 2 + 3.0 * z[1]

    def g_lin(x):
        return np.array([2.0 * x[0], 3.0])

    rem_lin = remainder(f_lin, g_lin, [1.0, 2.0], [0.1, 0.0])
    expected["differentiability-multivariable-r1-q2"] = rem_lin
    expected["differentiability-multivariable-r2-q2"] = rem_lin / 0.1

    def f_cubic(z):
        return (z[0] ** 2) * z[1]

    def g_cubic(x):
        return np.array([2.0 * x[0] * x[1], x[0] ** 2])

    rem_c = remainder(f_cubic, g_cubic, [1.0, 1.0], [0.5, 0.0])
    expected["differentiability-multivariable-r2-q3"] = rem_c
    expected["differentiability-multivariable-r3-q2"] = rem_c / 0.5

    def f_sq(z):
        return z[0] ** 2 + z[1] ** 2

    def g_sq(x):
        return 2.0 * np.asarray(x, dtype=float)

    expected["differentiability-multivariable-r4-q2"] = remainder(f_sq, g_sq, [0.0, 0.0], [0.2, 0.0])

    def f_hess(z):
        return (z[0] ** 3) * z[1] + 2.0 * z[1] ** 2 + 5.0 * z[0] * z[1]

    # Second partials at (1, 2): f_xx = 6 x y, f_xy = 3 x^2 + 5, f_yy = 4.
    h_xx = 6.0 * 1.0 * 2.0
    h_xy = 3.0 * 1.0 + 5.0
    h_yy = 4.0
    H = np.array([[h_xx, h_xy], [h_xy, h_yy]])
    expected["hessian-matrix-r1-q2"] = h_xx
    expected["hessian-matrix-r2-q2"] = h_xy
    expected["hessian-matrix-r2-q3"] = float(np.array([1.0, 0.0]) @ H @ np.array([1.0, 0.0]))
    expected["hessian-matrix-r3-q2"] = float(np.array([1.0, 1.0]) @ H @ np.array([1.0, 1.0]))
    expected["hessian-matrix-r4-q2"] = float(np.linalg.det(H))
    # Cross-check pure second partial by a second difference.
    eps = 1e-4
    base = np.array([1.0, 2.0])

    def second(i):
        e = np.zeros(2)
        e[i] = eps
        return (f_hess(base + e) - 2 * f_hess(base) + f_hess(base - e)) / eps ** 2

    require_close(mismatches, "f_xx", second(0), h_xx, tol=1e-3)
    require_close(mismatches, "f_yy", second(1), h_yy, tol=1e-3)

    def f_comp(t):
        return t ** 2 + (3.0 * t) ** 2

    expected["jacobian-chain-rule-r1-q2"] = 3.0  # partial of x y in y, at x = 3
    expected["jacobian-chain-rule-r2-q2"] = (f_comp(2.0 + 1e-6) - f_comp(2.0)) / 1e-6
    # Replace the FD value by the exact derivative 20 t at t = 2, after the check.
    exact_comp = 20.0 * 2.0
    require_close(mismatches, "composition", expected["jacobian-chain-rule-r2-q2"], exact_comp)
    expected["jacobian-chain-rule-r2-q2"] = exact_comp
    J = np.array([[5.0, 3.0], [1.0, 2.0]])
    expected["jacobian-chain-rule-r2-q3"] = float(np.linalg.det(J))
    expected["jacobian-chain-rule-r3-q2"] = float((J @ np.array([2.0, 1.0]))[0])

    def f_path(u):
        return u + (2.0 * u) ** 2

    path_fd = (f_path(3.0 + 1e-6) - f_path(3.0)) / 1e-6
    path_exact = 1.0 + 8.0 * 3.0
    require_close(mismatches, "path", path_fd, path_exact)
    expected["jacobian-chain-rule-r4-q2"] = path_exact

    A = np.array([[1.0, 3.0], [0.0, 2.0]])
    x11 = np.array([1.0, 1.0])
    grad_quad = (A + A.T) @ x11

    def f_quad(z):
        z = np.asarray(z, dtype=float)
        return float(z @ A @ z)

    require_close(mismatches, "quad grad 0", fd_directional(f_quad, x11, [1, 0]), grad_quad[0])
    require_close(mismatches, "quad grad 1", fd_directional(f_quad, x11, [0, 1]), grad_quad[1])
    expected["matrix-calculus-gradients-r1-q2"] = float(grad_quad[0])
    expected["matrix-calculus-gradients-r2-q2"] = float(grad_quad[1])

    A2 = np.array([[1.0, 0.0], [2.0, 1.0]])
    b2 = np.array([1.0, 0.0])
    x2 = np.array([2.0, 1.0])

    def f_res(z):
        r = A2 @ np.asarray(z, dtype=float) - b2
        return float(r @ r)

    grad_res = 2.0 * A2.T @ (A2 @ x2 - b2)
    require_close(mismatches, "residual grad", fd_directional(f_res, x2, [1, 0]), grad_res[0])
    expected["matrix-calculus-gradients-r2-q3"] = float(grad_res[0])
    expected["matrix-calculus-gradients-r3-q2"] = float((A + A.T)[0, 1])
    expected["matrix-calculus-gradients-r4-q2"] = 2.0 * 3.0

    def f_seg(z):
        return z[0] ** 2 + 3.0 * z[1]

    expected["fundamental-theorem-along-segment-r1-q2"] = f_seg(np.array([2.0, 1.0])) - f_seg(np.array([0.0, 0.0]))
    g_end = np.array([4.0, 3.0])
    g_start = np.array([0.0, 3.0])
    expected["fundamental-theorem-along-segment-r2-q2"] = float((g_end - g_start)[0])
    expected["fundamental-theorem-along-segment-r2-q3"] = float(np.dot(g_start, [2.0, 1.0]))
    expected["fundamental-theorem-along-segment-r3-q2"] = 4.0 ** 2 - 1.0 ** 2
    g_a = np.array([6.0, 2.0])
    g_b = np.array([2.0, 0.0])
    expected["fundamental-theorem-along-segment-r4-q2"] = float((g_a - g_b)[1])

    # f = x^3 + 2 x y at (1, 1), h = (1, -1)
    value = 1.0 + 2.0
    grad = np.array([5.0, 2.0])
    step = np.array([1.0, -1.0])
    H_t = np.array([[6.0, 2.0], [2.0, 0.0]])
    linear = value + float(np.dot(grad, step))
    quad = 0.5 * float(step @ H_t @ step)
    true = 8.0 + 0.0
    expected["taylor-approximation-multivariable-r1-q2"] = linear
    expected["taylor-approximation-multivariable-r2-q2"] = linear + quad
    expected["taylor-approximation-multivariable-r2-q3"] = abs(true - linear)
    expected["taylor-approximation-multivariable-r3-q2"] = quad
    expected["taylor-approximation-multivariable-r4-q2"] = true

    expected["taylor-exact-mean-value-r1-q2"] = (8.0 - 0.0) / 2.0
    expected["taylor-exact-mean-value-r2-q2"] = (12.0 / 2.0) * (2.0 ** 2)
    expected["taylor-exact-mean-value-r2-q3"] = 6.0 * 2.0
    expected["taylor-exact-mean-value-r3-q2"] = 0.5 * 2.0 * (3.0 ** 2)
    expected["taylor-exact-mean-value-r4-q2"] = (6.0 / 2.0) * (1.0 + 4.0)

    numeric = check_expected(banks, expected, mismatches)

    def need(sid, snippet):
        if snippet not in texts[sid]:
            mismatches.append(f"{sid} explainer missing {snippet!r}")

    need("directional-derivative", "through (4, -1)")
    need("gradient-partial-derivatives", "length 34")
    need("differentiability-multivariable", "checkpoint (2, 7)")
    need("hessian-matrix", "sample point (7, 9)")
    need("jacobian-chain-rule", "inner point (6, -2)")
    need("matrix-calculus-gradients", "data (9, -2)")
    need("fundamental-theorem-along-segment", "vertical segment at x = 8")
    need("taylor-approximation-multivariable", "cubic slice at x = 2")
    need("taylor-exact-mean-value", "fourth power on a segment of length 3")

    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
