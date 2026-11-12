#!/usr/bin/env python3
"""Independent numeric check for nonlinear-optimization batch NB9.

Recomputes each numeric answer from the stated problems. Does not import the
generator. Symbolic keys are compared with expressions derived here, and
finish() checks those keys with SymPy.
"""
import json

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "gauss-newton-method",
    "levenberg-marquardt",
    "incremental-gradient-methods",
    "kalman-recursive-least-squares",
    "extended-kalman-filter",
    "newton-root-finding",
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


def gn_step(residual, jacobian):
    """Scalar Gauss-Newton step. residual and jacobian are columns."""
    r = np.asarray(residual, dtype=float)
    j = np.asarray(jacobian, dtype=float)
    gram = float(j @ j)
    grad = float(j @ r)
    return -grad / gram, grad, gram


def lm_step(gram, grad, damping):
    return -float(grad) / (float(gram) + float(damping))


def gain(variance, row, meas_var):
    return float(variance) * float(row) / (float(row) ** 2 * float(variance) + float(meas_var))


def newton_scalar(value, derivative, point):
    return float(point) - float(value) / float(derivative)


def incremental_pass(start, step, centers):
    u = float(start)
    for center in centers:
        u = u - float(step) * (u - float(center))
    return u


def pass_fixed_point(step, first, second):
    """Fixed point of one pass on 1/2 (u-a)^2 + 1/2 (u-b)^2."""
    t = float(step)
    return ((1.0 - t) * float(first) + float(second)) / (2.0 - t)


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    # Gauss-Newton.
    d_lin, g_lin, gram_lin = gn_step((-1.0, -4.0), (1.0, 2.0))
    expected["gauss-newton-method-r1-q2"] = d_lin
    d_nl, g_nl, gram_nl = gn_step((-6.0, 0.0), (4.0, 2.0))
    expected["gauss-newton-method-r3-q2"] = d_nl
    expected["gauss-newton-method-r4-q2"] = g_nl * d_nl
    need(mismatches, abs(gram_lin - 5) < 1e-12 and abs(d_lin - 1.8) < 1e-12, "linear GN step drifted")
    need(mismatches, abs(gram_nl - 20) < 1e-12 and abs(g_nl - (-24)) < 1e-12, "nonlinear GN gradient drifted")
    # Dropped Hessian term r1 * r1'' = -6 * 2, true Hessian 20 - 12.
    need(mismatches, abs((20 - 12) - 8) < 1e-12, "true Hessian was not 8")
    updated = 2.0 + d_nl
    residual_after = (updated ** 2 - 10.0, 2.0 * updated - 4.0)
    need(mismatches, abs(residual_after[0] - 0.24) < 1e-9 and abs(residual_after[1] - 2.4) < 1e-9,
         "nonlinear residual after the step was not (0.24, 2.4)")
    # Wrong Jacobian (2, 1) is not the derivative 2x at x = 2.
    need(mismatches, abs((2 * 2) - 2) > 1e-12, "2x and x agreed at the sample point")
    wrong_j_step, _, _ = gn_step((-1.0, 1.0), (2.0, 1.0))
    true_j_step, true_g, true_gram = gn_step((-1.0, 1.0), (4.0, 1.0))
    need(mismatches, abs(true_gram - 17) < 1e-12 and abs(true_g - (-3)) < 1e-12, "find-error Gram drifted")
    need(mismatches, abs(true_j_step - 3 / 17) < 1e-12, "true GN step was not 3/17")
    need(mismatches, abs(wrong_j_step - true_j_step) > 1e-6, "the wrong Jacobian reproduced the true step")

    # Levenberg-Marquardt.
    expected["levenberg-marquardt-r1-q2"] = lm_step(2, 4, 2)
    expected["levenberg-marquardt-r3-q2"] = lm_step(2, 4, 14)
    expected["levenberg-marquardt-r4-q2"] = 4 * lm_step(2, 4, 2)
    short = abs(lm_step(2, 4, 6))
    long = abs(lm_step(2, 4, 2))
    need(mismatches, short < long and abs(lm_step(2, 4, 0) - (-2)) < 1e-12, "damping did not shorten toward GN")
    need(mismatches, lm_step(2, 4, 2) < 0 and (2 + 2) > 0, "damped step was not a negative descent step")
    # Objective 1/2 ((u+3)^2 + (u+1)^2) falls from 5 at 0 to 2 at -1.
    def lm_objective(u):
        return 0.5 * ((u + 3.0) ** 2 + (u + 1.0) ** 2)

    need(mismatches, abs(lm_objective(0) - 5) < 1e-12 and abs(lm_objective(-1) - 2) < 1e-12,
         "accepted damped step did not decrease the objective")

    # Incremental gradient.
    expected["incremental-gradient-methods-r1-q2"] = incremental_pass(0, 1, (2, 6))
    expected["incremental-gradient-methods-r3-q2"] = incremental_pass(0, 0.5, (2, 6))
    full_grad = (0 - 2) + (0 - 6)
    expected["incremental-gradient-methods-r4-q2"] = 0 - 0.5 * full_grad
    end_long = incremental_pass(6, 1, (2, 6))
    need(mismatches, abs(end_long - 6) < 1e-12, "the length-1 pass did not stay at 6")
    need(mismatches, abs((2 * 6 - 8) - 4) < 1e-12, "full gradient at 6 was not 4")
    batch_long = 0 - 1.0 * full_grad
    need(mismatches, abs(batch_long - 8) < 1e-12 and abs(expected["incremental-gradient-methods-r1-q2"] - 6) < 1e-12,
         "batch and incremental length-1 steps agreed")
    fixed_half = pass_fixed_point(0.5, 2, 6)
    need(mismatches, abs(fixed_half - 14 / 3) < 1e-12, "half-step fixed point drifted")
    need(mismatches, abs(pass_fixed_point(1e-6, 2, 6) - 4) < 1e-4, "vanishing step did not approach 4")
    need(mismatches, abs(2 * fixed_half - 8) > 0.1, "half-step fixed point looked stationary")

    # Recursive least squares, scalar Kalman measurement update.
    k1 = gain(4, 1, 4)
    expected["kalman-recursive-least-squares-r1-q2"] = k1
    expected["kalman-recursive-least-squares-r3-q2"] = (1 - k1 * 1) * 4
    k2 = gain(2, 1, 2)
    expected["kalman-recursive-least-squares-r4-q2"] = 4 + k2 * (7 - 4)
    need(mismatches, abs(k1 - 0.5) < 1e-12, "first gain drifted")
    need(mismatches, abs(2 + k1 * (6 - 2) - 4) < 1e-12, "adding the correction missed the midpoint")
    wrong_update = 2 - k1 * (6 - 2)
    right_update = 2 + k1 * (6 - 2)
    need(mismatches, abs(wrong_update - 6) > abs(right_update - 6),
         "subtracting the correction moved toward the measurement")
    k_tight = gain(4, 1, 1)
    need(mismatches, k_tight > k1, "a smaller measurement variance did not raise the gain")
    need(mismatches, 0 < k1 < 1 and expected["kalman-recursive-least-squares-r3-q2"] < 4,
         "variance did not shrink")

    # Extended update for h(u) = u^2.
    jacobian = 2 * 3
    innovation = 15 - 3 ** 2
    k_ext = gain(1, jacobian, 12)
    updated_u = 3 + k_ext * innovation
    updated_p = (1 - k_ext * jacobian) * 1
    expected["extended-kalman-filter-r1-q2"] = jacobian
    expected["extended-kalman-filter-r3-q2"] = updated_u
    expected["extended-kalman-filter-r4-q2"] = updated_p
    need(mismatches, abs(k_ext - 1 / 8) < 1e-12 and abs(innovation - 6) < 1e-12, "extended gain drifted")
    # True nonlinear cost 1/2 (u-3)^2 + (15-u^2)^2 / (2*12).
    def nl_cost_grad(u):
        return (u - 3.0) - (15.0 - u * u) * u / 6.0

    need(mismatches, abs(nl_cost_grad(updated_u) - 21 / 128) < 1e-9, "nonlinear cost derivative was not 21/128")
    need(mismatches, abs(2 * updated_u - jacobian) > 1, "Jacobian did not change after the update")
    wrong_gain = gain(1, 3, 12)
    need(mismatches, abs(wrong_gain - k_ext) > 1e-6, "using the estimate as the Jacobian matched the true gain")

    # Newton.
    expected["newton-root-finding-r1-q2"] = newton_scalar(2, 4, 2)
    expected["newton-root-finding-r3-q2"] = -2.0 / 4.0
    expected["newton-root-finding-r4-q2"] = newton_scalar(14, -8, -4)
    # Cubic start 1/2 of t^3 - t lands on -1, not on the nearest roots 0 and 1.
    cubic_next = newton_scalar(0.125 - 0.5, 3 * 0.25 - 1, 0.5)
    need(mismatches, abs(cubic_next - (-1)) < 1e-12, "cubic Newton step missed -1")
    need(mismatches, abs(0.5 - 0) < abs(0.5 - (-1)), " -1 was nearer to 1/2 than 0 is")
    affine_next = newton_scalar(2 * 5 - 6, 2, 5)
    need(mismatches, abs(affine_next - 3) < 1e-12, "affine Newton step missed the root")
    need(mismatches, expected["newton-root-finding-r4-q2"] < 0 < expected["newton-root-finding-r1-q2"],
         "the two starts did not separate the roots")

    expect_key(mismatches, banks, "gauss-newton-method-r2-q3", "-(p*a+q*b)/(p*p+q*q)")
    expect_key(mismatches, banks, "levenberg-marquardt-r2-q3", "-(p*a+q*b)/(p*p+q*q+mu)")
    expect_key(mismatches, banks, "incremental-gradient-methods-r2-q3", "u-t*(a*u+b)")
    expect_key(mismatches, banks, "kalman-recursive-least-squares-r2-q3", "p*c/(c*c*p+r)")
    expect_key(mismatches, banks, "extended-kalman-filter-r2-q3", "p*j/(j*j*p+r)")
    expect_key(mismatches, banks, "newton-root-finding-r2-q3", "u-v/p")

    markers = {
        "gauss-newton-method": "The hatch step is 3",
        "levenberg-marquardt": "The cleat step is -0.5",
        "incremental-gradient-methods": "The crate reading is 14.8",
        "kalman-recursive-least-squares": "The buoy estimate is 5.75",
        "extended-kalman-filter": "The dock position is 6.66667",
        "newton-root-finding": "The pier guess is 3.1",
    }
    # Worked examples use none of the quiz inputs. Anchors are recomputed here.
    anchors = {
        "gauss-newton-method": gn_step((-6.0, -3.0), (2.0, 1.0))[0],
        "levenberg-marquardt": lm_step(5, 3, 1),
        "incremental-gradient-methods": incremental_pass(14, 0.4, (9, 19)),
        "kalman-recursive-least-squares": 8 + gain(9, 1, 3) * (5 - 8),
        "extended-kalman-filter": 5 + gain(1, 10, 20) * (45 - 25),
        "newton-root-finding": newton_scalar(19, 10, 5),
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
