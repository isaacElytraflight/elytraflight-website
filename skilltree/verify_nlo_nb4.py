#!/usr/bin/env python3
"""Independent numeric check for nonlinear-optimization batch NB4.

Recomputes each numeric answer from the definitions. Does not import the
generator. Finite differences cross-check the derivative formulas.
Symbolic keys are checked by finish().
"""
import math

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "convex-functions",
    "convexity-first-order",
    "convexity-second-order",
    "finite-difference-derivatives",
    "computational-graphs",
    "ad-forward-mode",
    "ad-reverse-mode",
    "hessian-vector-products-ad",
    "backprop-neural-network",
]


def require_close(mismatches, label, got, expected, tol=1e-6):
    scale = max(abs(float(expected)), abs(float(got)), 1e-9)
    if abs(float(got) - float(expected)) / scale > tol:
        mismatches.append(f"{label}: cross-check {got} != {expected}")


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    # Chord of t^2 from 1 to 5, midpoint height.
    expected["convex-functions-r1-q2"] = (1.0 ** 2 + 5.0 ** 2) / 2.0
    # |x|+2|y| at (2,-4) and (-6,2), weight 1/4 on the second point.
    def f_norm(z):
        return abs(z[0]) + 2.0 * abs(z[1])
    a = np.array([2.0, -4.0])
    b = np.array([-6.0, 2.0])
    expected["convex-functions-r2-q2"] = 0.75 * f_norm(a) + 0.25 * f_norm(b)
    # t^2 from 0 to 4, weight 1/4 on the right: chord minus function.
    point = 0.75 * 0.0 + 0.25 * 4.0
    chord = 0.75 * 0.0 + 0.25 * (4.0 ** 2)
    expected["convex-functions-r3-q2"] = chord - point ** 2
    # Euclidean norm, chord from (3,0) to (0,4), gap at the midpoint.
    left = np.array([3.0, 0.0])
    right = np.array([0.0, 4.0])
    mid = 0.5 * (left + right)
    expected["convex-functions-r4-q2"] = 0.5 * (np.linalg.norm(left) + np.linalg.norm(right)) - np.linalg.norm(mid)

    def f_ell(z):
        return z[0] ** 2 + 3.0 * z[1] ** 2

    def g_ell(z):
        return np.array([2.0 * z[0], 6.0 * z[1]])

    base = np.array([2.0, 1.0])
    other = np.array([0.0, 2.0])
    step = other - base
    linear = float(np.dot(g_ell(base), step))
    under = f_ell(base) + linear
    expected["convexity-first-order-r1-q2"] = under
    expected["convexity-first-order-r2-q2"] = f_ell(other) - under
    expected["convexity-first-order-r3-q2"] = linear
    base2 = np.array([1.0, 0.0])
    other2 = np.array([1.0, 2.0])
    expected["convexity-first-order-r4-q2"] = f_ell(base2) + float(np.dot(g_ell(base2), other2 - base2))
    require_close(
        mismatches, "first-order gap",
        f_ell(other) - under,
        f_ell(other) - (f_ell(base) + float(np.dot(g_ell(base), step))),
    )

    # Smaller eigenvalue of diag(6, 10).
    hess_diag = np.array([[6.0, 0.0], [0.0, 10.0]])
    expected["convexity-second-order-r1-q2"] = float(np.linalg.eigvalsh(hess_diag)[0])
    hess_off = np.array([[2.0, -1.0], [-1.0, 2.0]])
    expected["convexity-second-order-r2-q2"] = float(np.linalg.eigvalsh(hess_off)[0])

    def f_sq(z):
        return (z[0] + 2.0 * z[1] - 1.0) ** 2

    def mixed_partial(z, eps=1e-5):
        # f_xy by a centered difference of partials.
        def fx(p):
            e = np.array([eps, 0.0])
            return (f_sq(p + e) - f_sq(p - e)) / (2.0 * eps)
        ey = np.array([0.0, eps])
        return (fx(z + ey) - fx(z - ey)) / (2.0 * eps)

    sample = np.array([0.3, -0.4])
    expected["convexity-second-order-r3-q2"] = mixed_partial(sample)
    # 2 A^T A for A with columns (1,0,1) and (0,2,1): bottom-right is 2 * ||second column||^2.
    col2 = np.array([0.0, 2.0, 1.0])
    expected["convexity-second-order-r4-q2"] = 2.0 * float(np.dot(col2, col2))

    def cube(t):
        return t ** 3

    def fourth(t):
        return t ** 4

    h = 0.1
    expected["finite-difference-derivatives-r1-q2"] = (cube(2.0 + h) - cube(2.0)) / h
    expected["finite-difference-derivatives-r2-q2"] = (cube(2.0 + h) - cube(2.0 - h)) / (2.0 * h)
    exact = 3.0 * 2.0 ** 2
    expected["finite-difference-derivatives-r3-q1"] = expected["finite-difference-derivatives-r1-q2"] - exact
    h4 = 0.5
    expected["finite-difference-derivatives-r4-q1"] = (fourth(1.0 + h4) - fourth(1.0 - h4)) / (2.0 * h4)
    # Leading forward truncation (h/2) f'' plus (h^2/6) f''' for t^3.
    predicted = exact + (h / 2.0) * (6.0 * 2.0) + (h ** 2 / 6.0) * 6.0
    require_close(mismatches, "cube forward", expected["finite-difference-derivatives-r1-q2"], predicted)

    def f_graph(x, y):
        return (x * y + 3.0) ** 2 + x

    expected["computational-graphs-r1-q2"] = f_graph(2.0, 4.0)
    expected["computational-graphs-r2-q2"] = f_graph(2.0, 5.0)
    expected["computational-graphs-r3-q2"] = 1.0 * 7.0 + 3.0
    expected["computational-graphs-r4-q2"] = f_graph(1.0, 7.0)

    def grad_graph(x, y):
        s = x * y + 3.0
        return np.array([2.0 * s * y + 1.0, 2.0 * s * x])

    def fd_grad(x, y, eps=1e-6):
        return np.array([
            (f_graph(x + eps, y) - f_graph(x - eps, y)) / (2.0 * eps),
            (f_graph(x, y + eps) - f_graph(x, y - eps)) / (2.0 * eps),
        ])

    g24 = grad_graph(2.0, 4.0)
    require_close(mismatches, "grad x", g24[0], fd_grad(2.0, 4.0)[0])
    require_close(mismatches, "grad y", g24[1], fd_grad(2.0, 4.0)[1])
    expected["ad-forward-mode-r1-q2"] = float(np.dot(g24, [1.0, 0.0]))
    expected["ad-forward-mode-r2-q2"] = float(np.dot(g24, [0.0, 1.0]))
    expected["ad-forward-mode-r3-q1"] = float(np.dot(g24, [1.0, 1.0]))
    g12 = grad_graph(1.0, 2.0)
    expected["ad-forward-mode-r4-q1"] = float(np.dot(g12, [1.0, 0.0]))

    expected["ad-reverse-mode-r1-q2"] = float(g24[0])
    expected["ad-reverse-mode-r2-q2"] = float(g24[1])
    expected["ad-reverse-mode-r3-q1"] = float(g12[1])
    # Adjoint of s = xy + 3 is 2 s, since the output adjoint is 1 and f = s^2 + x.
    expected["ad-reverse-mode-r4-q1"] = 2.0 * (2.0 * 4.0 + 3.0)

    def hess_graph(x, y):
        return np.array([
            [2.0 * y * y, 2.0 * (2.0 * x * y + 3.0)],
            [2.0 * (2.0 * x * y + 3.0), 2.0 * x * x],
        ])

    def fd_hess_col(x, y, d, eps=1e-5):
        return (grad_graph(x + eps * d[0], y + eps * d[1]) - grad_graph(x - eps * d[0], y - eps * d[1])) / (2.0 * eps)

    h24 = hess_graph(2.0, 4.0)
    col = h24 @ np.array([1.0, 0.0])
    require_close(mismatches, "H e1", col[0], fd_hess_col(2.0, 4.0, np.array([1.0, 0.0]))[0])
    both = h24 @ np.array([1.0, 1.0])
    expected["hessian-vector-products-ad-r1-q2"] = float(col[0])
    expected["hessian-vector-products-ad-r2-q2"] = float(col[1])
    expected["hessian-vector-products-ad-r3-q1"] = float(both[0])
    direction = np.array([1.0, 1.0])
    expected["hessian-vector-products-ad-r4-q1"] = float(direction @ both)

    def backprop(x, w1, b1, w2, b2, y):
        z = w1 * x + b1
        h = z if z > 0.0 else 0.0
        yhat = w2 * h + b2
        residual = yhat - y
        hidden = residual * w2
        gate = 1.0 if z > 0.0 else 0.0
        return {
            "dw2": residual * h,
            "dw1": hidden * gate * x,
            "db1": hidden * gate,
            "db2": residual,
        }

    first = backprop(3.0, 2.0, -1.0, 4.0, 1.0, 11.0)
    expected["backprop-neural-network-r1-q2"] = first["dw2"]
    expected["backprop-neural-network-r2-q2"] = first["dw1"]
    expected["backprop-neural-network-r3-q1"] = first["db1"]
    second = backprop(2.0, 3.0, 0.0, -1.0, 8.0, -4.0)
    expected["backprop-neural-network-r4-q1"] = second["dw1"]
    # Negative pre-activation: hidden value and activation derivative are both 0.
    # Every weight gradient is 0. The output bias still equals the residual.
    blocked = backprop(1.0, -2.0, -1.0, 4.0, 1.0, 5.0)
    require_close(mismatches, "blocked first weight", blocked["dw1"], 0.0, tol=0.0)
    require_close(mismatches, "blocked first bias", blocked["db1"], 0.0, tol=0.0)
    require_close(mismatches, "blocked output weight", blocked["dw2"], 0.0, tol=0.0)
    require_close(mismatches, "open output bias", blocked["db2"], 1.0 - 5.0, tol=0.0)
    blocked_q = next(
        q for q in banks["backprop-neural-network"]["questions"]
        if q["id"] == "backprop-neural-network-r3-q3"
    )
    if blocked_q["options"][blocked_q["correct_index"]] != "the output bias":
        mismatches.append("backprop-neural-network-r3-q3 marks a zero partial derivative")

    numeric = check_expected(banks, expected, mismatches)

    markers = {
        "convex-functions": "sample chord height is 90",
        "convexity-first-order": "tangent value is 55",
        "convexity-second-order": "Hessian entries 14 and 18",
        "finite-difference-derivatives": "central value is 48.04",
        "computational-graphs": "inner point (6, -2)",
        "ad-forward-mode": "tangent total is 16",
        "ad-reverse-mode": "adjoint pair 14 and 8",
        "hessian-vector-products-ad": "product entries 11 and 2",
        "backprop-neural-network": "first-layer gradient is 288",
    }
    # Recompute the worked-example anchors. The phrase has to appear in the
    # explainer and must not be copied into the bank.
    anchors = {
        "convex-functions": (6.0 ** 2 + 12.0 ** 2) / 2.0,
        "convexity-first-order": 25.0 + 10.0 * (8.0 - 5.0),
        "convexity-second-order": 14.0,
        "finite-difference-derivatives": (4.2 ** 3 - 3.8 ** 3) / 0.4,
        "computational-graphs": (6.0 + -2.0) * 6.0 + 5.0,
        "ad-forward-mode": (2.0 * 6.0 + -2.0) + 6.0,
        "ad-reverse-mode": (2.0 * 8.0 + -2.0),
        "hessian-vector-products-ad": 6.0 * 2.0 + 1.0 * -1.0,
        "backprop-neural-network": ((3.0 * 7.0 - 5.0) - 4.0) * 3.0 * 8.0,
    }
    bank_blobs = {sid: json_blob(banks[sid]) for sid in SKILLS}
    for sid, phrase in markers.items():
        if phrase not in texts[sid]:
            mismatches.append(f"{sid} explainer missing {phrase!r}")
        if phrase in bank_blobs[sid]:
            mismatches.append(f"{sid} worked-example phrase reused in the bank")
        number = anchors[sid]
        rendered = f"{number:.6g}"
        if rendered not in texts[sid]:
            mismatches.append(f"{sid} explainer missing recomputed anchor {rendered}")

    finish(numeric, mismatches, banks)


def json_blob(bank):
    import json
    return json.dumps(bank)


if __name__ == "__main__":
    main()
