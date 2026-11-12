#!/usr/bin/env python3
"""Independent numeric check for nonlinear-optimization batch NB11.

Recomputes each numeric answer from the stated problems. Does not import the
generator. Symbolic keys are compared with expressions derived here, and
finish() checks those keys with SymPy.
"""
import json

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "gram-schmidt-orthogonalization",
    "q-conjugate-directions",
    "conjugate-gradient-method",
    "heavy-ball-method",
    "nesterov-accelerated-gradient",
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


def dot(left, right):
    return sum(a * b for a, b in zip(left, right))


def qdot(diag, left, right):
    return sum(d * a * b for d, a, b in zip(diag, left, right))


def gram_coeff(accepted, new, diag=None):
    if diag is None:
        numer = dot(new, accepted)
        denom = dot(accepted, accepted)
    else:
        numer = qdot(diag, new, accepted)
        denom = qdot(diag, accepted, accepted)
    coeff = numer / denom
    result = tuple(n - coeff * a for n, a in zip(new, accepted))
    return coeff, result


def exact_step(grad, direction, diag):
    numer = -dot(grad, direction)
    denom = qdot(diag, direction, direction)
    return numer / denom


def heavy_ball(position, previous, grad, step, momentum):
    return tuple(
        p - step * g + momentum * (p - r)
        for p, r, g in zip(position, previous, grad)
    )


def nesterov_extrapolation(position, previous, momentum):
    return tuple(p + momentum * (p - r) for p, r in zip(position, previous))


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    expected = {}

    # Gram-Schmidt. Dot product of (3, 1) against (1, 2).
    coeff_12, remain_12 = gram_coeff((1, 2), (3, 1))
    expected["gram-schmidt-orthogonalization-r1-q2"] = remain_12[0]
    need(mismatches, abs(coeff_12 - 1) < 1e-12 and remain_12 == (2, -1),
         "dot-product remainder was not (2, -1)")
    # Q = diag(4, 1), (2, 5) against (1, 0).
    coeff_q, remain_q = gram_coeff((1, 0), (2, 5), diag=(4, 1))
    expected["gram-schmidt-orthogonalization-r3-q2"] = remain_q[1]
    need(mismatches, abs(coeff_q - 2) < 1e-12 and remain_q == (0, 5),
         "Q-inner remainder was not (0, 5)")
    # Coefficient of u2 = (0, 1, 0) in (2, 3, 4).
    coeff_u2, remain_u3 = gram_coeff((0, 1, 0), (2, 3, 4))
    coeff_u1, _ = gram_coeff((1, 0, 0), (2, 3, 4))
    expected["gram-schmidt-orthogonalization-r4-q2"] = coeff_u2
    # The remainder after both subtractions is (0, 0, 4).
    both = tuple(
        v - coeff_u1 * e1 - coeff_u2 * e2
        for v, e1, e2 in zip((2, 3, 4), (1, 0, 0), (0, 1, 0))
    )
    need(mismatches, abs(coeff_u1 - 2) < 1e-12 and abs(coeff_u2 - 3) < 1e-12 and both == (0, 0, 4),
         "third-vector coefficients drifted")
    # The flawed note: skipping the subtraction leaves (6, 4), not (0, 4).
    coeff_note, remain_note = gram_coeff((2, 0), (6, 4))
    need(mismatches, abs(coeff_note - 3) < 1e-12 and remain_note == (0, 4),
         "the note's subtraction does not produce (0, 4)")
    # Orthogonal pairs. Indices 0, 1, 3 are the zeros.
    gs_pairs = [
        ((1, -2), (4, 2)),
        ((2, 3), (3, -2)),
        ((1, 1), (2, -1)),
        ((0, 5), (3, 0)),
        ((2, 2), (1, 1)),
    ]
    gs_zero = [i for i, (u, v) in enumerate(gs_pairs) if abs(dot(u, v)) < 1e-12]
    need(mismatches, gs_zero == [0, 1, 3], f"orthogonal pairs {gs_zero}")

    # Conjugate directions.
    product = qdot((3, 1), (1, 1), (1, 2))
    expected["q-conjugate-directions-r1-q2"] = product
    need(mismatches, abs(product - 5) < 1e-12, "conjugacy product was not 5")
    length = exact_step((6, 4), (-1, 1), (3, 1))
    expected["q-conjugate-directions-r3-q2"] = length
    need(mismatches, abs(length - 0.5) < 1e-12, "exact step was not 1/2")
    # Flawed conjugacy note: product is 2, not 0.
    note_product = qdot((4, 1), (1, 2), (1, -1))
    need(mismatches, abs(note_product - 2) < 1e-12, "the note's product was not 2")
    # Exact step from the origin along (-1, 0).
    grad0 = (4, -6)
    step0 = exact_step(grad0, (-1, 0), (2, 6))
    point = (step0 * -1, 0)
    grad1 = (2 * point[0] + 4, 6 * point[1] - 6)
    expected["q-conjugate-directions-r4-q2"] = grad1[1]
    need(mismatches, abs(step0 - 2) < 1e-12 and abs(dot(grad1, (-1, 0))) < 1e-12,
         "new gradient is not orthogonal to the step")
    cd_pairs = [
        ((4, 1), (2, -1)),
        ((1, 1), (4, -1)),
        ((2, 0), (0, 3)),
        ((1, 2), (4, 1)),
        ((1, -1), (8, 2)),
    ]
    cd_zero = [i for i, (u, v) in enumerate(cd_pairs) if abs(qdot((2, 8), u, v)) < 1e-12]
    need(mismatches, cd_zero == [1, 2, 4], f"Q-conjugate pairs {cd_zero}")

    # Conjugate gradient.
    beta = (0 + 4) / (9 + 0)
    expected["conjugate-gradient-method-r1-q2"] = beta
    need(mismatches, abs(beta - 4 / 9) < 1e-12, "beta was not 4/9")
    # First step: gradient (4, 2), Q = diag(1, 2), direction = -gradient.
    g = (4, 2)
    curv = qdot((1, 2), g, g)
    t_first = dot(g, g) / curv
    expected["conjugate-gradient-method-r3-q2"] = t_first
    need(mismatches, abs(t_first - 20 / 24) < 1e-12, "first CG step was not 5/6")
    # Flawed direction uses +beta * old gradient. Correct uses +beta * old direction.
    beta_note = 36 / 9
    wrong_dir = (0 - 0 + beta_note * 3, -6 + beta_note * 0)
    right_dir = (0 + beta_note * -3, -6 + beta_note * 0)
    need(mismatches, abs(beta_note - 4) < 1e-12 and wrong_dir == (12, -6) and right_dir == (-12, -6),
         "CG direction sign did not flip")
    base = (2 - 1) / (2 + 1)
    expected["conjugate-gradient-method-r4-q2"] = base
    steep = (4 - 1) / (4 + 1)
    need(mismatches, abs(base - 1 / 3) < 1e-12 and abs(steep - 0.6) < 1e-12 and abs(base - steep) > 1e-9,
         "CG base collided with the steepest-descent base")

    # Heavy ball.
    nxt = heavy_ball((3, 1), (1, 1), (2, 4), 0.5, 0.5)
    expected["heavy-ball-method-r1-q2"] = nxt[1]
    need(mismatches, nxt == (3, -1), f"heavy-ball point was {nxt}")
    mu, big_l = 1.0, 4.0
    root_l, root_mu = big_l ** 0.5, mu ** 0.5
    momentum = ((root_l - root_mu) / (root_l + root_mu)) ** 2
    alpha = 4 / (root_l + root_mu) ** 2
    expected["heavy-ball-method-r3-q2"] = momentum
    expected["heavy-ball-method-r4-q2"] = alpha
    need(mismatches, abs(momentum - 1 / 9) < 1e-12 and abs(alpha - 4 / 9) < 1e-12,
         "tuned heavy-ball parameters drifted")
    need(mismatches, abs(momentum - alpha) > 1e-9, "momentum and step size agree, so the questions collide")
    # Flawed sign: 4 - 2 - 1.5 = 0.5, correct is 4 - 2 + 1.5 = 3.5.
    need(mismatches, abs((4 - 2 - 1.5) - 0.5) < 1e-12 and abs((4 - 2 + 1.5) - 3.5) < 1e-12,
         "heavy-ball sign check drifted")

    # Nesterov.
    extra = nesterov_extrapolation((4, 2), (0, 2), 0.75)
    expected["nesterov-accelerated-gradient-r1-q2"] = extra[0]
    need(mismatches, extra == (7, 2), f"extrapolated point was {extra}")
    gap = 2 * 5 * 4 / (4 + 1) ** 2
    expected["nesterov-accelerated-gradient-r3-q2"] = gap
    need(mismatches, abs(gap - 1.6) < 1e-12, "gap bound was not 1.6")
    sched = (7 - 1) / (7 + 2)
    expected["nesterov-accelerated-gradient-r4-q2"] = sched
    need(mismatches, abs(sched - 2 / 3) < 1e-12, "schedule was not 2/3")
    # Flawed Nesterov step subtracts the gradient at the current point.
    extrapolated = 5 + 0.5 * (5 - 1)
    need(mismatches, abs(extrapolated - 7) < 1e-12 and abs((7 - 4) - 3) < 1e-12 and abs((7 - 2) - 5) < 1e-12,
         "Nesterov evaluation point drifted")

    # Multi-select indices stored in the banks must match the recomputed pairs.
    for qid, want in (
        ("gram-schmidt-orthogonalization-r2-q2", gs_zero),
        ("q-conjugate-directions-r2-q2", cd_zero),
    ):
        sid = qid.rsplit("-r", 1)[0]
        found = None
        for q in banks[sid]["questions"]:
            if q["id"] == qid:
                found = list(q.get("correct_indices") or [])
        if found != want:
            mismatches.append(f"{qid}: correct_indices {found} != {want}")

    expect_key(mismatches, banks, "gram-schmidt-orthogonalization-r2-q3", "(a*c+b*d)/(a*a+b*b)")
    expect_key(mismatches, banks, "q-conjugate-directions-r2-q3", "-(g*u+h*v)/(a*u*u+b*v*v)")
    expect_key(mismatches, banks, "conjugate-gradient-method-r2-q3", "(p*p+q*q)/(a*p*p+b*q*q)")
    expect_key(mismatches, banks, "heavy-ball-method-r2-q3", "a-s*g+m*(a-b)")
    expect_key(mismatches, banks, "nesterov-accelerated-gradient-r2-q3", "a+m*(a-b)")

    markers = {
        "gram-schmidt-orthogonalization": "The keel coefficient is 1.5",
        "q-conjugate-directions": "The spar step is 4",
        "conjugate-gradient-method": "The cleat weight is 0.625",
        "heavy-ball-method": "The drum position is 3.6",
        "nesterov-accelerated-gradient": "The buoy point is 11",
    }
    # Worked examples use none of the quiz inputs. Anchors are recomputed here.
    keel_coeff, keel_remain = gram_coeff((4, 0), (6, 8))
    spar = exact_step((8, 1), (-2, 0), (1, 3))
    cleat = (1 + 4) / (4 + 4)
    drum = 6 - 1 * 3 + 0.2 * (6 - 3)
    buoy = 9 + (1 / 3) * (9 - 3)
    anchors = {
        "gram-schmidt-orthogonalization": keel_coeff,
        "q-conjugate-directions": spar,
        "conjugate-gradient-method": cleat,
        "heavy-ball-method": drum,
        "nesterov-accelerated-gradient": buoy,
    }
    need(mismatches, abs(keel_coeff - 1.5) < 1e-12 and keel_remain == (0, 8), "keel remainder drifted")
    need(mismatches, abs(spar - 4) < 1e-12, "spar step drifted")
    need(mismatches, abs(cleat - 0.625) < 1e-12, "cleat weight drifted")
    need(mismatches, abs(drum - 3.6) < 1e-12, "drum position drifted")
    need(mismatches, abs(buoy - 11) < 1e-12, "buoy point drifted")
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
