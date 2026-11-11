#!/usr/bin/env python3
"""Independent numeric check for nonlinear-optimization batch NB8.

Recomputes each numeric answer from the stated problems. Does not import the
generator. Symbolic keys are compared with expressions derived here, and
finish() checks those keys with SymPy.
"""
import json

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "descent-directions",
    "descent-method-framework",
    "convergence-rates",
    "exact-line-search-quadratic",
    "armijo-backtracking",
    "gradient-zigzag",
    "condition-number-gradient-rate",
    "lipschitz-gradient",
    "descent-lemma",
    "sufficient-decrease-lemma",
    "gradient-method-convergence",
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


def dot(g, d):
    g = np.asarray(g, dtype=float)
    d = np.asarray(d, dtype=float)
    return float(g @ d)


def exact_step(diag, grad, direction):
    """Exact line search for f = 1/2 x^T diag(A) x + ..., gradient given."""
    a = np.asarray(diag, dtype=float)
    g = np.asarray(grad, dtype=float)
    d = np.asarray(direction, dtype=float)
    curvature = float(np.sum(a * d * d))
    return float(-(g @ d) / curvature)


def steepest_step(diag, point):
    a = np.asarray(diag, dtype=float)
    x = np.asarray(point, dtype=float)
    g = a * x
    return exact_step(a, g, -g), g


def armijo_rhs(value, c, step, directional):
    return float(value) + float(c) * float(step) * float(directional)


def backtracking_accept(value_fn, value, c, directional, start, beta):
    """Shrink start by beta until Armijo holds. value_fn(t) is f(x + t d)."""
    t = float(start)
    for _ in range(12):
        if value_fn(t) <= armijo_rhs(value, c, t, directional) + 1e-12:
            return t
        t *= float(beta)
    raise RuntimeError("backtracking did not accept")


def kantorovich(kappa):
    ratio = (float(kappa) - 1.0) / (float(kappa) + 1.0)
    return ratio * ratio


def descent_bound(value, slope, step, lipschitz):
    return float(value) + float(slope) * float(step) + 0.5 * float(lipschitz) * float(step) ** 2


def guaranteed_drop(step, lipschitz, grad_sq):
    return float(step) * (1.0 - float(lipschitz) * float(step) / 2.0) * float(grad_sq)


def gradient_min_bound(lipschitz, gap, steps):
    """Bound on the smallest squared gradient norm for the step t = 1/L."""
    return 2.0 * float(lipschitz) * float(gap) / float(steps)


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    # Descent directions.
    expected["descent-directions-r1-q2"] = dot((3, 1), (-2, 1))
    g_scale = np.array([1.0, -2.0])
    d_scale = np.diag([2.0, 3.0]) @ g_scale
    expected["descent-directions-r3-q2"] = dot(g_scale, -d_scale)
    expected["descent-directions-r4-q2"] = dot((6, 1), (-1, 2))
    probes = [(-1, 0), (2, 1), (1, 1), (4, 1), (-3, -1)]
    signs = [dot((1, -2), d) for d in probes]
    need(mismatches, signs[0] < 0 and signs[2] < 0 and signs[4] < 0, "descent multi lost a negative direction")
    need(mismatches, signs[1] == 0 and signs[3] > 0, "descent multi kept a non-descent direction")
    need(mismatches, abs(dot((2, 2), (1, -1))) < 1e-12, "the zero directional derivative was not zero")

    # Framework displacements.
    expected["descent-method-framework-r1-q2"] = (0.5 ** 2) * float(np.dot((-4, 2), (-4, 2)))
    expected["descent-method-framework-r3-q2"] = float(np.linalg.norm((3.0, 4.0)))
    expected["descent-method-framework-r4-q2"] = (3.0 ** 2) * float(np.dot((-2, -1), (-2, -1)))
    steep = -np.array([2.0, -2.0])
    need(mismatches, np.allclose((4.0, 1.0) + steep, (2.0, 3.0)), "steepest update was not (2, 3)")
    need(mismatches, dot((2, -2), steep) < 0, "steepest direction did not descend")

    # Rates.
    errors = np.array([0.9, 0.45, 0.225])
    expected["convergence-rates-r1-q2"] = float(errors[1] / errors[0])
    quad = np.array([0.5, 0.25, 1.0 / 16.0])
    expected["convergence-rates-r3-q2"] = float(quad[2] / quad[1] ** 2)
    expected["convergence-rates-r4-q2"] = 0.01 / 0.05
    need(mismatches, abs(errors[2] / errors[1] - 0.5) < 1e-12, "the linear ratio was not constant")
    need(mismatches, abs((1 / 2) / (1 / 4) ** 2 - 1) > 1, "a geometric sequence looked quadratic")
    # (1/2)^{k^2} ratio tends to 0; 1/k ratio tends to 1.
    need(mismatches, (0.5) ** (2 * 5 + 1) < 1e-3, "squared-exponent sequence was not superlinear")

    # Exact line search.
    expected["exact-line-search-quadratic-r1-q2"] = exact_step((2, 2), (4, 2), (-4, -2))
    expected["exact-line-search-quadratic-r3-q2"] = exact_step((2, 6), (4, 3), (-2, -1))
    expected["exact-line-search-quadratic-r4-q2"] = exact_step((1, 3), (3, 3), (-1, -1))
    slope = dot((4, 0), (-2, 0))
    curv = 2.0 * 4.0
    need(mismatches, abs(-slope / curv - 1) < 1e-12, "the unit exact step drifted")
    phi = lambda t: slope * t + 0.5 * curv * t * t
    need(mismatches, phi(3) > 0 and phi(1) < 0, "steps outside (0, 2) were not increases")

    # Armijo.
    expected["armijo-backtracking-r1-q2"] = armijo_rhs(4, 0.25, 1, 4 * -1)
    expected["armijo-backtracking-r3-q2"] = backtracking_accept(
        lambda t: (2 - t) ** 2, 4, 0.25, -4, 4, 0.5
    )
    expected["armijo-backtracking-r4-q2"] = -0.2 * 2 * -5
    # f(u)=u^2 at 3, d=-1, c=1/2: accept iff t in [0, 3].
    def passes(t):
        return (3 - t) ** 2 <= armijo_rhs(9, 0.5, t, -6) + 1e-12

    need(mismatches, passes(1) and passes(2) and passes(3), "an interior Armijo trial was rejected")
    need(mismatches, not passes(4) and not passes(5), "a long Armijo trial was accepted")

    # Zigzag.
    t_a, g_a = steepest_step((1, 2), (2, 1))
    expected["gradient-zigzag-r1-q2"] = t_a
    t_b, g_b = steepest_step((2, 6), (3, 1))
    x_b = np.array([3.0, 1.0]) - t_b * g_b
    g_new = np.array([2.0, 6.0]) * x_b
    expected["gradient-zigzag-r3-q2"] = float(g_new @ g_new)
    t_c, _g_c = steepest_step((1, 5), (5, 1))
    expected["gradient-zigzag-r4-q2"] = t_c
    need(mismatches, abs(dot(g_b, g_new)) < 1e-9, "successive gradients were not orthogonal")
    pairs = [((-1, 2), (2, 1)), ((1, 1), (1, -1)), ((2, 0), (1, 1)), ((3, -1), (1, 3)), ((1, 2), (2, 2))]
    orth = [abs(dot(u, v)) < 1e-12 for u, v in pairs]
    need(mismatches, orth == [True, True, False, True, False], "orthogonal pairs drifted")

    # Condition number.
    expected["condition-number-gradient-rate-r1-q2"] = kantorovich(3)
    expected["condition-number-gradient-rate-r3-q2"] = 9 * kantorovich(5)
    expected["condition-number-gradient-rate-r4-q2"] = kantorovich(8 / 2)
    caps = [kantorovich(2 / 1), kantorovich(6 / 2), kantorovich(9 / 1), kantorovich(4 / 4), kantorovich(7 / 1)]
    need(mismatches, caps[0] <= 0.25 and caps[1] <= 0.25 and caps[3] <= 0.25, "a mild condition number was excluded")
    need(mismatches, caps[2] > 0.25 and caps[4] > 0.25, "a large condition number looked mild")

    # Lipschitz.
    expected["lipschitz-gradient-r1-q2"] = 6
    gram = np.array([[2.0, 0, 1], [0, 1, 0]], dtype=float) @ np.array([[2.0, 0], [0, 1], [1, 0]])
    expected["lipschitz-gradient-r3-q2"] = float(np.linalg.eigvalsh(gram).max())
    expected["lipschitz-gradient-r4-q2"] = abs(4 * 3 - 4 * 1) / abs(3 - 1)
    need(mismatches, abs(expected["lipschitz-gradient-r3-q2"] - 5) < 1e-9, "least-squares Lipschitz constant drifted")
    need(mismatches, 4 < 5 < 5.5, "the Lipschitz threshold was not 5")

    # Descent lemma. f(t) = 2 t^2 has L = 4. f(t) = t^2 has L = 2.
    expected["descent-lemma-r1-q2"] = descent_bound(2, 4, 1, 4)
    expected["descent-lemma-r3-q2"] = descent_bound(8, 8, 1, 4)
    expected["descent-lemma-r4-q2"] = descent_bound(4, 4, 3, 2)
    loose = descent_bound(1, 2, 2, 1)
    need(mismatches, loose < 9, "a too-small Lipschitz constant still covered f(3)")
    sharp = descent_bound(1, 2 * 1, 3, 2)
    need(mismatches, abs(sharp - 16) < 1e-9, "sharp quadratic bound missed f(4)")

    # Sufficient decrease.
    expected["sufficient-decrease-lemma-r1-q2"] = guaranteed_drop(0.25, 4, 16)
    expected["sufficient-decrease-lemma-r3-q2"] = guaranteed_drop(0.2, 5, 10)
    expected["sufficient-decrease-lemma-r4-q2"] = 2.0 / 5.0
    keep = [guaranteed_drop(t, 4, 1) for t in (0.25, 0.5, 1.0, 0.1, 0.4)]
    need(mismatches, keep[0] > 0 and keep[3] > 0 and keep[4] > 0, "a short step lost its decrease")
    need(mismatches, abs(keep[1]) < 1e-12 and keep[2] < 0, "a long step still decreased")

    # Gradient-method convergence. Step t = 1/L.
    expected["gradient-method-convergence-r1-q2"] = gradient_min_bound(2, 3, 6)
    expected["gradient-method-convergence-r3-q2"] = gradient_min_bound(4, 2, 4)
    expected["gradient-method-convergence-r4-q2"] = gradient_min_bound(3, 2, 4)
    # f(u)=u^2/2, L=1, step 3 sends u to -2u.
    need(mismatches, abs(-2) > 1, "the long gradient step did not diverge")

    expect_key(mismatches, banks, "descent-directions-r2-q3", "-p*p+q*r")
    expect_key(mismatches, banks, "descent-method-framework-r2-q3", "a+t*b")
    expect_key(mismatches, banks, "convergence-rates-r2-q3", "a*c**3")
    expect_key(mismatches, banks, "exact-line-search-quadratic-r2-q3", "-(p*u+q*v)/(a*u*u+b*v*v)")
    expect_key(mismatches, banks, "armijo-backtracking-r2-q3", "f0+c*t*s")
    expect_key(mismatches, banks, "gradient-zigzag-r2-q3", "(u*u+v*v)/(p*(u*u+v*v))")
    expect_key(mismatches, banks, "condition-number-gradient-rate-r2-q3", "gap*((r-1)/(r+1))**2")
    expect_key(mismatches, banks, "lipschitz-gradient-r2-q3", "p*p+q*q")
    expect_key(mismatches, banks, "descent-lemma-r2-q3", "f0+g*h+ell*h*h/2")
    expect_key(mismatches, banks, "sufficient-decrease-lemma-r2-q3", "t*(1-ell*t/2)*s")
    expect_key(mismatches, banks, "gradient-method-convergence-r2-q3", "2*ell*gap/m")

    markers = {
        "descent-directions": "The dock slope is -16",
        "descent-method-framework": "The crate coordinate is 7",
        "convergence-rates": "The beacon ratio is 0.125",
        "exact-line-search-quadratic": "The winch step is 3",
        "armijo-backtracking": "The latch value is 19",
        "gradient-zigzag": "The spar coordinate is 3",
        "condition-number-gradient-rate": "The hoist factor is 0.04",
        "lipschitz-gradient": "The cable constant is 12",
        "descent-lemma": "The loft bound is 16",
        "sufficient-decrease-lemma": "The ramp drop is 3",
        "gradient-method-convergence": "The trail bound is 6",
    }
    anchors = {
        "descent-directions": dot((5, -1), (-3, 1)),
        "descent-method-framework": 8 + 1 * -1,
        "convergence-rates": 0.08 / 0.64,
        "exact-line-search-quadratic": exact_step((1, 1), (3, 0), (-1, 0)),
        "armijo-backtracking": armijo_rhs(25, 0.1, 6, -10),
        "gradient-zigzag": 6 - steepest_step((1, 3), (6, 2))[0] * 6,
        "condition-number-gradient-rate": kantorovich(1.5),
        "lipschitz-gradient": 12,
        "descent-lemma": descent_bound(1, 2, 3, 2),
        "sufficient-decrease-lemma": guaranteed_drop(1 / 6, 6, 36),
        "gradient-method-convergence": gradient_min_bound(5, 6, 10),
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
