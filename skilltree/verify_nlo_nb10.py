#!/usr/bin/env python3
"""Independent numeric check for nonlinear-optimization batch NB10.

Recomputes each numeric answer from the stated problems. Does not import the
generator. Symbolic keys are compared with expressions derived here, and
finish() checks those keys with SymPy.
"""
import json

import numpy as np

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "newton-method-optimization",
    "newton-local-quadratic-convergence",
    "newton-globalization",
    "wolfe-conditions",
    "quasi-newton-secant",
    "bfgs-update",
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


def newton_scalar(deriv, second):
    return -float(deriv) / float(second)


def shifted_step(deriv, second, shift):
    return -float(deriv) / (float(second) + float(shift))


def bfgs_inverse(approximation, step, change):
    """Inverse BFGS update. approximation is the old inverse Hessian."""
    matrix = np.array(approximation, dtype=float)
    step = np.array(step, dtype=float)
    change = np.array(change, dtype=float)
    rho = 1.0 / float(change @ step)
    eye = np.eye(len(step))
    left = eye - rho * np.outer(step, change)
    right = eye - rho * np.outer(change, step)
    return left @ matrix @ right + rho * np.outer(step, step)


def wolfe_pair(alpha, c1=0.1, c2=0.5):
    """f(t)=t^2, start 2, direction -1. Returns decrease, curvature, y^T s."""
    old_dir = 4.0 * -1.0
    new_point = 2.0 - float(alpha)
    new_dir = (2.0 * new_point) * -1.0
    decrease = new_point ** 2 <= 4.0 + c1 * float(alpha) * old_dir
    curvature = new_dir >= c2 * old_dir
    # s = alpha * d, y = f'(new) - f'(old) = 2*new_point - 4
    product = float(alpha) * (new_dir - old_dir)
    return decrease, curvature, product, new_dir


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    # Newton minimization. f = 2x^2 + y^2 - 8x + 6y at (1, 1).
    grad = np.array([4.0 * 1.0 - 8.0, 2.0 * 1.0 + 6.0])
    hess = np.diag([4.0, 2.0])
    step = -np.linalg.solve(hess, grad)
    expected["newton-method-optimization-r1-q2"] = float(step[1])
    need(mismatches, np.allclose(step, [1.0, -4.0]), "2D Newton step was not (1, -4)")
    cubic_step = newton_scalar(3 * 4 - 6, 6 * 2)
    expected["newton-method-optimization-r3-q2"] = cubic_step
    wrong_second = newton_scalar(6, 6)
    need(mismatches, abs(cubic_step - (-0.5)) < 1e-12, "cubic Newton step was not -1/2")
    need(mismatches, abs(wrong_second - (-1)) < 1e-12 and abs(wrong_second - cubic_step) > 1e-9,
         "replacing 6t by 6 did not change the step")
    # f(t) = -2 t^2 at t = 3 lands on the maximizer 0.
    max_step = newton_scalar(-4 * 3, -4)
    need(mismatches, abs((3 + max_step) - 0) < 1e-12, "negative curvature did not land on 0")
    # f(t) = 3t^2 - 12t at 0. Directional derivative along the Newton step.
    plain = newton_scalar(-12, 6)
    expected["newton-method-optimization-r4-q2"] = (-12) * plain
    need(mismatches, abs(plain - 2) < 1e-12, "descent Newton step was not 2")

    # Local quadratic rate. f' = t(t-2), f'' = 2t-2, minimizer 2.
    def deriv(t):
        return t * (t - 2)

    def second(t):
        return 2 * t - 2

    next_from_3 = 3 + newton_scalar(deriv(3), second(3))
    expected["newton-local-quadratic-convergence-r1-q2"] = abs(next_from_3 - 2)
    next_from_4 = 4 + newton_scalar(deriv(4), second(4))
    expected["newton-local-quadratic-convergence-r3-q2"] = abs(next_from_4 - 2)
    need(mismatches, abs(second(1)) < 1e-12, "the singular start is not singular")
    need(mismatches, abs(deriv(0)) < 1e-12 and second(0) < 0, "t=0 is not the other stationary point")
    closer = []
    for start in (3, 1.5, 4):
        nxt = start + newton_scalar(deriv(start), second(start))
        closer.append(abs(nxt - 2) < abs(start - 2) - 1e-12 and second(start) > 0)
    need(mismatches, all(closer), "a listed interior start did not move closer")
    next_from_half = 0.5 + newton_scalar(deriv(0.5), second(0.5))
    need(mismatches, second(0.5) < 0 and abs(next_from_half - 2) > abs(0.5 - 2),
         "t=0.5 was inside the minimizer basin")
    expected["newton-local-quadratic-convergence-r4-q2"] = abs(second(5) - second(2)) / 3

    # Globalization.
    expected["newton-globalization-r1-q2"] = shifted_step(6, -2, 6)
    unshifted = newton_scalar(6, -2)
    need(mismatches, unshifted > 0 and 6 * unshifted > 0, "the unshifted step was not uphill")
    expected["newton-globalization-r3-q2"] = 4 * shifted_step(4, -3, 5)
    bad_shift = shifted_step(4, -3, 1)
    need(mismatches, abs((-3 + 1) - (-2)) < 1e-12 and abs(bad_shift - 2) < 1e-12, "flawed shift arithmetic drifted")
    need(mismatches, 4 * bad_shift > 0 and expected["newton-globalization-r3-q2"] < 0,
         "the small shift was not uphill, or the large shift was not descent")
    # Smallest integer shift for diag(-1, 4).
    expected["newton-globalization-r4-q2"] = 2
    need(mismatches, (-1 + 1) == 0 and (-1 + 2) > 0 and (4 + 2) > 0, "integer shift test drifted")

    # Wolfe. Negative-curvature decrease on f(t)=-t^2.
    y_neg = (-2 * 2) - (-2 * 1)
    expected["wolfe-conditions-r1-q2"] = y_neg * 1
    need(mismatches, expected["wolfe-conditions-r1-q2"] < 0, "the decrease step did not have negative curvature")
    accepted = []
    for alpha, want_both in ((0.5, False), (1, True), (2, True), (4, False)):
        decrease, curvature, product, _new = wolfe_pair(alpha)
        both = decrease and curvature
        if both != want_both:
            mismatches.append(f"Wolfe length {alpha}: both={both}, expected {want_both}")
        accepted.append(both)
        if alpha == 1:
            expected["wolfe-conditions-r3-q2"] = product
    need(mismatches, accepted == [False, True, True, False], "Wolfe length pattern drifted")
    # Curvature threshold for c2 = 0.9: alpha >= 2(1-c2).
    expected["wolfe-conditions-r4-q2"] = 2 * (1 - 0.9)
    _, curvature_small, _, _ = wolfe_pair(0.2 - 1e-9, c2=0.9)
    decrease_edge, curvature_edge, _, _ = wolfe_pair(0.2, c2=0.9)
    need(mismatches, (not curvature_small) and curvature_edge and decrease_edge,
         "c2=0.9 threshold is not 0.2")
    # The flawed note: alpha 1/2 has decrease and fails curvature, and -3 <= -2 is the wrong direction.
    decrease_half, curvature_half, _, new_half = wolfe_pair(0.5)
    need(mismatches, decrease_half and (not curvature_half) and abs(new_half - (-3)) < 1e-12,
         "the length 1/2 check does not fail only curvature")

    # Secant.
    expected["quasi-newton-secant-r1-q2"] = (-2) / (-1)
    curvature = (6 * 2) / (2 * 2)
    expected["quasi-newton-secant-r3-q2"] = curvature
    expected["quasi-newton-secant-r4-q2"] = 2 - 4 * 1
    for step_s, change_y, positive in ((2, 6, True), (2, -6, False), (-1, -2, True), (-4, -8, True)):
        value = change_y / step_s
        if (value > 0) != positive:
            mismatches.append(f"secant pair {(step_s, change_y)} sign drifted")
    need(mismatches, abs(curvature - 3) < 1e-12, "secant curvature was not 3")

    # BFGS.
    eye = np.eye(2)
    good = bfgs_inverse(eye, (1, 0), (2, 0))
    expected["bfgs-update-r1-q2"] = float(good[0, 0])
    wider = bfgs_inverse(eye, (1, 0), (4, 0))
    expected["bfgs-update-r3-q2"] = float(wider[0, 0])
    lost = bfgs_inverse(eye, (1, 0), (-1, 0))
    need(mismatches, abs(lost[0, 0] - (-1)) < 1e-12 and np.linalg.eigvalsh(lost)[0] < 0,
         "the negative pair did not lose positive definiteness")
    need(mismatches, np.allclose(good @ np.array([2.0, 0.0]), [1.0, 0.0]), "secant failed for y=(2,0)")
    need(mismatches, np.allclose(wider @ np.array([4.0, 0.0]), [1.0, 0.0]), "secant failed for y=(4,0)")
    direction = -np.diag([0.5, 1.0]) @ np.array([2.0, 0.0])
    expected["bfgs-update-r4-q2"] = float(direction[0])
    products = {
        ((1, 0), (2, 0)): True,
        ((1, 0), (-1, 0)): False,
        ((1, 1), (1, 2)): True,
        ((1, 0), (0, 1)): False,
        ((2, -1), (0, -2)): True,
    }
    for (step_s, change_y), positive in products.items():
        prod = float(np.dot(change_y, step_s))
        if (prod > 0) != positive:
            mismatches.append(f"BFGS pair {step_s, change_y} product {prod} drifted")

    expect_key(mismatches, banks, "newton-method-optimization-r2-q3", "-a/p-b/q")
    expect_key(mismatches, banks, "newton-local-quadratic-convergence-r2-q3", "(L*z*z)/(2*h)")
    expect_key(mismatches, banks, "newton-globalization-r2-q3", "-g/(h+m)")
    expect_key(mismatches, banks, "wolfe-conditions-r2-q3", "t*(c-1)*g")
    expect_key(mismatches, banks, "quasi-newton-secant-r2-q3", "y/s")
    expect_key(mismatches, banks, "bfgs-update-r2-q2", "s/y")

    markers = {
        "newton-method-optimization": "The latch step is 3",
        "newton-local-quadratic-convergence": "The spool error is 0.642857",
        "newton-globalization": "The cleat shift step is 5",
        "wolfe-conditions": "The hawser product is 8",
        "quasi-newton-secant": "The reed curvature is 4",
        "bfgs-update": "The anvil entry is 3",
    }
    # Worked examples use none of the quiz inputs. Anchors are recomputed here.
    local_deriv = 3 * 81 - 12 * 9 - 36
    local_second = 6 * 9 - 12
    local_next = 9 + newton_scalar(local_deriv, local_second)
    anchors = {
        "newton-method-optimization": newton_scalar(-15, 5),
        "newton-local-quadratic-convergence": abs(local_next - 6),
        "newton-globalization": shifted_step(-15, -1, 4),
        "wolfe-conditions": ((8 * 2) - (8 * 3)) * (-1),
        "quasi-newton-secant": 20 / 5,
        "bfgs-update": float(bfgs_inverse(eye, (3, 0), (1, 0))[0, 0]),
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
        for question in banks[sid]["questions"]:
            if question.get("type") == "numeric" and abs(float(question["answer"]) - anchors[sid]) <= 1e-9 * max(1.0, abs(anchors[sid])):
                mismatches.append(f"{sid} worked example repeats numeric answer {question['id']}")

    numeric = check_expected(banks, expected, mismatches)
    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
