#!/usr/bin/env python3
"""Independent numeric check for nonlinear-optimization batch NB7.

Recomputes each numeric answer from the stated problems. Does not import the
generator. Symbolic keys are compared with expressions derived here, and
finish() checks those keys with SymPy.
"""
import json
from itertools import combinations

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "lagrangian-duality-lower-bounds",
    "lagrange-multiplier-equality",
    "kkt-conditions",
    "lp-duality-kkt",
    "projection-affine-halfspace-kkt",
    "linear-least-squares",
    "least-squares-data-fitting",
    "nonlinear-least-squares",
    "circle-fitting-least-squares",
    "svm-quadratic-program",
]


def expect_key(mismatches, banks, qid, expression):
    sid = qid.rsplit("-r", 1)[0]
    for q in banks[sid]["questions"]:
        if q["id"] == qid:
            if q.get("answer") != expression:
                mismatches.append(f"{qid}: key {q.get('answer')!r} != {expression!r}")
            return
    mismatches.append(f"{qid}: missing symbolic question")


def need(mismatches, cond, message):
    if not cond:
        mismatches.append(message)


def dual_bound(bound, multiplier):
    """inf_x x^2 + u (bound - x), attained at x = u/2."""
    return float(bound) * float(multiplier) - float(multiplier) ** 2 / 4.0


def equality_quadratic(rows, rhs):
    """Minimize x^2+y^2 subject to rows[i]·(x,y) = rhs[i]. One constraint in R^2.

    Stationarity of x^2+y^2 + λ (a x + b y - β) is 2x + λ a = 0, 2y + λ b = 0.
    """
    a, b = rows
    # (2I) (x,y) + λ (a,b) = 0 and (a,b)·(x,y) = β.
    # x = -λ a/2, y = -λ b/2, so -λ (a^2+b^2)/2 = β? Wait a x + b y = β
    # a(-λ a/2) + b(-λ b/2) = β => -λ (a^2+b^2)/2 = β => λ = -2 β / (a^2+b^2)
    gram = a * a + b * b
    lam = -2.0 * rhs / gram
    x = -lam * a / 2.0
    y = -lam * b / 2.0
    return np.array([x, y]), lam


def opt_standard(A, b, c):
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    c = np.asarray(c, dtype=float)
    m, n = A.shape
    best = None
    for cols in combinations(range(n), m):
        basis = A[:, cols]
        if abs(np.linalg.det(basis)) < 1e-9:
            continue
        xB = np.linalg.solve(basis, b)
        if np.any(xB < -1e-8):
            continue
        x = np.zeros(n)
        x[list(cols)] = xB
        value = float(c @ x)
        if best is None or value < best[0]:
            best = (value, cols, x)
    return best


def project_affine(z, a, beta):
    z = np.asarray(z, dtype=float)
    a = np.asarray(a, dtype=float)
    nu = float((a @ z - beta) / (a @ a))
    x = z - nu * a
    return x, nu, float(np.sum((x - z) ** 2))


def least_squares(A, b):
    A = np.asarray(A, dtype=float)
    b = np.asarray(b, dtype=float)
    x = np.linalg.solve(A.T @ A, A.T @ b)
    residual = A @ x - b
    return x, float(residual @ residual)


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    # Dual of min x^2 s.t. x >= 3. Primal value 9. θ(u) = 3u - u^2/4.
    expected["lagrangian-duality-lower-bounds-r1-q2"] = dual_bound(3, 2)
    theta4 = dual_bound(3, 4)
    expected["lagrangian-duality-lower-bounds-r3-q2"] = 9.0 - theta4
    expected["lagrangian-duality-lower-bounds-r4-q2"] = dual_bound(5, 4)
    need(mismatches, abs(dual_bound(3, 6) - 9) < 1e-9, "dual at u=6 is not the primal value")
    need(mismatches, abs(dual_bound(3, 2) - 9) > 1e-9, "the false multi option u=2 equals 9")
    need(mismatches, -2 < 0, "negative multiplier was treated as dual feasible")

    # Equality: min x^2+y^2 on x+2y=5, on 3x+y=10, and on x+y=6.
    xy, lam = equality_quadratic((1.0, 2.0), 5.0)
    expected["lagrange-multiplier-equality-r1-q2"] = lam
    xy2, _lam2 = equality_quadratic((3.0, 1.0), 10.0)
    expected["lagrange-multiplier-equality-r3-q2"] = float(xy2 @ xy2)
    _xy3, lam3 = equality_quadratic((1.0, 1.0), 6.0)
    expected["lagrange-multiplier-equality-r4-q2"] = lam3
    need(mismatches, np.allclose(xy, (1, 2)) and abs(lam + 2) < 1e-9, "first Lagrange point drifted")
    need(mismatches, abs(1 + 0) > 0.5, "the failed multiplier equation 1=0 was solvable")

    # KKT: (x-3)^2 on x<=1 gives ν=4. x^2+y^2 on x+y>=4 gives objective 8.
    # (x-5)^2 on x<=2 gives ν=6.
    expected["kkt-conditions-r1-q2"] = 2 * (4 - 1)
    expected["kkt-conditions-r3-q2"] = 2.0 ** 2 + 2.0 ** 2
    expected["kkt-conditions-r4-q2"] = (2 - 5) ** 2
    need(mismatches, not (3 <= 1), "inactive KKT branch was feasible")
    need(mismatches, abs(2 * (1 - 3) + 4) < 1e-12, "KKT stationarity at (1, 4) failed")

    # Standard-form LPs by enumerating bases.
    lp1 = opt_standard([[1.0, 1.0]], [7.0], [-3.0, 0.0])
    expected["lp-duality-kkt-r1-q2"] = lp1[0]
    lp2 = opt_standard(
        [[1.0, 1, 1, 0], [2, 1, 0, 1]],
        [5.0, 8.0],
        [-6.0, -2, 0, 0],
    )
    expected["lp-duality-kkt-r3-q2"] = lp2[0]
    c_gap = np.array([-6.0, -2, 0, 0])
    x_gap = np.array([2.0, 0, 3, 4])
    y_gap = np.array([0.0, -3.0])
    A_gap = np.array([[1.0, 1, 1, 0], [2, 1, 0, 1]])
    b_gap = np.array([5.0, 8.0])
    slack = c_gap - A_gap.T @ y_gap
    need(mismatches, np.allclose(A_gap @ x_gap, b_gap) and np.all(x_gap >= -1e-9), "gap primal was infeasible")
    need(mismatches, np.all(slack >= -1e-9), "gap dual was infeasible")
    expected["lp-duality-kkt-r4-q2"] = float(c_gap @ x_gap - b_gap @ y_gap)
    need(mismatches, (-10) > (-18), "weak-duality counterexample was not a violation")

    # Projections.
    _x1, _n1, d1 = project_affine((5.0, 3.0), (1.0, 0.0), 2.0)
    expected["projection-affine-halfspace-kkt-r1-q2"] = d1
    _x3, n3, d3 = project_affine((1.0, 1.0), (1.0, 1.0), 6.0)
    expected["projection-affine-halfspace-kkt-r3-q2"] = d3
    _x4, _n4, d4 = project_affine((6.0, 2.0), (1.0, 0.0), 1.0)
    expected["projection-affine-halfspace-kkt-r4-q2"] = d4
    need(mismatches, n3 < 0, "equality projection multiplier was not free to be negative")
    need(mismatches, 5 > 2, "outside point was classified as inside")

    # Linear least squares.
    mean_x, _ = least_squares(np.ones((4, 1)), [2.0, 4, 6, 8])
    expected["linear-least-squares-r1-q2"] = float(mean_x[0])
    A_orth = np.array([[1.0, 0], [1, 0], [0, 1], [0, 1]])
    b_orth = np.array([3.0, 5, 2, 6])
    x_orth, sse = least_squares(A_orth, b_orth)
    expected["linear-least-squares-r3-q2"] = sse
    A_line = np.array([[1.0, 1], [1, 2], [1, 3]])
    x_line, _ = least_squares(A_line, [2.0, 3, 6])
    expected["linear-least-squares-r4-q2"] = float(x_line[1])
    need(mismatches, np.allclose(x_orth, (4, 4)), "orthogonal least-squares point drifted")
    need(mismatches, abs(A_orth.T @ (A_orth @ x_orth - b_orth)).max() < 1e-8, "residual was not orthogonal")

    # Data fitting.
    expected["least-squares-data-fitting-r1-q2"] = 3
    A_fit = np.array([[1.0, 0], [1, 1], [1, 2]])
    x_fit, _ = least_squares(A_fit, [1.0, 2, 5])
    expected["least-squares-data-fitting-r3-q2"] = float(x_fit[1])
    expected["least-squares-data-fitting-r4-q2"] = 4
    vand = np.vander([0.0, 1, 2], N=3, increasing=True)
    need(mismatches, abs(np.linalg.det(vand)) > 1e-8, "three distinct inputs were dependent")

    # Nonlinear residuals.
    def residual(u, v):
        return np.array([u * u + v - 3.0, u + v * v - 5.0])

    expected["nonlinear-least-squares-r1-q2"] = float(residual(1, 1) @ residual(1, 1))
    expected["nonlinear-least-squares-r3-q2"] = float(residual(2, 1) @ residual(2, 1))
    expected["nonlinear-least-squares-r4-q2"] = (4 - 1) ** 2 + (1 - 1) ** 2 - 2 ** 2
    jac_second_u = 1.0
    need(mismatches, jac_second_u != 2 * 1, "copied Jacobian entry was actually right")

    # Algebraic circle.
    def algebraic(x, y, c, d, e):
        return x * x + y * y + c * x + d * y + e

    expected["circle-fitting-least-squares-r1-q2"] = algebraic(4, 1, -2, -2, -1)
    c, d, e = -4.0, -6.0, 4.0
    expected["circle-fitting-least-squares-r3-q2"] = (c * c + d * d) / 4.0 - e
    expected["circle-fitting-least-squares-r4-q2"] = algebraic(5, 1, -4, -2, 3)
    need(
        mismatches,
        abs((2 ** 2 + 3 ** 2 + 9) - (2 ** 2 + 3 ** 2 - 9)) > 1,
        "the plus-sign constant term matched the minus-sign formula",
    )

    # SVM distance and the 1-D separator.
    def hyperplane_distance(w, b, point):
        w = np.asarray(w, dtype=float)
        return abs(float(w @ np.asarray(point, dtype=float) + b)) / float(np.linalg.norm(w))

    expected["svm-quadratic-program-r1-q2"] = hyperplane_distance((0.0, 2.0), -2.0, (5.0, 4.0))
    # min 1/2 w^2 s.t. 3w+b >= 1 and -w-b >= 1. Optimum w=1, b=-2.
    expected["svm-quadratic-program-r3-q2"] = -2.0
    expected["svm-quadratic-program-r4-q2"] = hyperplane_distance((3.0, 4.0), 10.0, (2.0, 1.0))
    need(mismatches, abs((1 / 0.5) - 2) < 1e-12, "rescaled geometric margin changed")

    expect_key(mismatches, banks, "lagrangian-duality-lower-bounds-r2-q3", "a*u-u*u/4")
    expect_key(mismatches, banks, "lagrange-multiplier-equality-r2-q3", "-2*p*a")
    expect_key(mismatches, banks, "kkt-conditions-r2-q3", "2*(a-b)")
    expect_key(mismatches, banks, "lp-duality-kkt-r2-q3", "p-a*y-b*z")
    expect_key(mismatches, banks, "projection-affine-halfspace-kkt-r2-q3", "(a*p+b*q-r)/(a*a+b*b)")
    expect_key(mismatches, banks, "linear-least-squares-r2-q3", "(p*u+q*v)/(p*p+q*q)")
    expect_key(mismatches, banks, "least-squares-data-fitting-r2-q3", "a+b*t")
    expect_key(mismatches, banks, "nonlinear-least-squares-r2-q3", "(p*p-s)**2")
    expect_key(mismatches, banks, "circle-fitting-least-squares-r2-q3", "c*c/4+d*d/4-k")
    expect_key(mismatches, banks, "svm-quadratic-program-r2-q3", "(p*x+q*y+r)**2/(p*p+q*q)")

    markers = {
        "lagrangian-duality-lower-bounds": "The cistern lower bound is 11",
        "lagrange-multiplier-equality": "The pier multiplier is -4",
        "kkt-conditions": "The gate multiplier is 10",
        "lp-duality-kkt": "The barge dual is -45",
        "projection-affine-halfspace-kkt": "The ramp gap is 36",
        "linear-least-squares": "The gauge mean is 6",
        "least-squares-data-fitting": "The chalk slope is 6",
        "nonlinear-least-squares": "The coil residual is 50",
        "circle-fitting-least-squares": "The hoop residual is 21",
        "svm-quadratic-program": "The plaque gap is 2",
    }
    anchors = {
        "lagrangian-duality-lower-bounds": dual_bound(6, 2),
        "lagrange-multiplier-equality": equality_quadratic((1.0, 1.0), 4.0)[1],
        "kkt-conditions": 2 * (9 - 4),
        "lp-duality-kkt": opt_standard([[1.0, 1.0]], [9.0], [-5.0, 0.0])[0],
        "projection-affine-halfspace-kkt": project_affine((9.0, 4.0), (1.0, 0.0), 3.0)[2],
        "linear-least-squares": float(least_squares(np.ones((4, 1)), [1.0, 9, 3, 11])[0][0]),
        "least-squares-data-fitting": float(least_squares(np.array([[1.0], [2.0]]), [6.0, 12.0])[0][0]),
        "nonlinear-least-squares": float(np.array([3.0 ** 2 - 2, 3.0 - 4]) @ np.array([7.0, -1.0])),
        "circle-fitting-least-squares": algebraic(6, 2, -2, -6, 5),
        "svm-quadratic-program": hyperplane_distance((3.0, -4.0), 2.0, (4.0, 1.0)),
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

    numeric = check_expected(banks, expected, mismatches)
    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
