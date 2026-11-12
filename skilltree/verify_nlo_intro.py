#!/usr/bin/env python3
"""Independent numeric check for the optional NLO introduction batch.

Recomputes each numeric answer from the stated problems. Does not import the
generator. Symbolic keys are compared with expressions derived here, and
finish() checks those keys with SymPy.
"""
import math

from verify_harness import check_expected, finish, load_banks, load_texts

SKILLS = [
    "calculus-of-variations",
    "largest-inscribed-ellipsoid",
    "trajectory-optimization",
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


def question(banks, qid):
    sid = qid.rsplit("-r", 1)[0]
    for q in banks[sid]["questions"]:
        if q["id"] == qid:
            return q
    raise SystemExit("missing " + qid)


def matvec_diag(diag, vector):
    return tuple(d * v for d, v in zip(diag, vector))


def norm(vector):
    return math.sqrt(sum(v * v for v in vector))


def containment(diag, normal, center):
    return norm(matvec_diag(diag, normal)) + dot(normal, center)


def main():
    mismatches = []
    banks = load_banks(SKILLS)
    texts = load_texts(SKILLS)
    for sid, text in texts.items():
        if "The anchor curvature is -9" in text and sid != "calculus-of-variations":
            mismatches.append(sid + " borrowed the brachistochrone worked example")
        if "The anchor length is 7" in text and sid != "largest-inscribed-ellipsoid":
            mismatches.append(sid + " borrowed the ellipsoid worked example")
        if "The anchor smoothness is 113" in text and sid != "trajectory-optimization":
            mismatches.append(sid + " borrowed the trajectory worked example")
    expected = {}

    # Slope partial of (y')^2 + 3 y is 2 y'. At slope 4 the value is 8.
    slope = 4
    expected["calculus-of-variations-r1-q2"] = 2 * slope
    need(mismatches, 2 * slope == 8, "slope partial was not 8")
    # Cycloid y = r (1 - cos theta), r = 3, theta = pi.
    radius = 3
    expected["calculus-of-variations-r3-q2"] = radius * (1 - math.cos(math.pi))
    need(mismatches, abs(math.cos(math.pi) + 1) < 1e-12, "cos pi was not -1")
    # y = x^2, L = (y')^2 + 5 y, at x = 1.
    # slope = 2x = 2, slope partial = 2 * slope = 4x = 4, derivative 4.
    # height partial 5. Residual 4 - 5.
    x_sample = 1
    slope_partial_deriv = 4  # d/dx (2 * 2x) = 4
    height_partial = 5
    expected["calculus-of-variations-r4-q2"] = slope_partial_deriv - height_partial
    need(
        mismatches,
        2 * (2 * x_sample) == 4 and slope_partial_deriv - height_partial == -1,
        "EL residual was not -1",
    )
    # Integrands with no explicit height: indices 0, 1, 4.
    no_height = [True, True, False, False, True]
    cov_yes = [i for i, flag in enumerate(no_height) if flag]
    need(mismatches, cov_yes == [0, 1, 4], f"height-free indices {cov_yes}")
    need(
        mismatches,
        question(banks, "calculus-of-variations-r2-q2")["correct_indices"] == [0, 1, 4],
        "height-free multi indices",
    )
    # The note's line y = x has slope-partial derivative 0 and height partial 2.
    need(mismatches, 0 != 2, "the note's two sides unexpectedly agree")
    need(
        mismatches,
        question(banks, "calculus-of-variations-r3-q1")["flaw_index"] == 3,
        "calculus-of-variations flaw index",
    )
    # L = (a/2) (y')^2 - b y. EL: a y'' = -b, so y'' = -b/a.
    expect_key(mismatches, banks, "calculus-of-variations-r2-q3", "-b/a")
    probe_a, probe_b = 2, 4
    need(mismatches, -probe_b / probe_a == -2, "EL probe was not -2")

    # B = diag(2, 1), a = (3, 0), d = (1, 4).
    expected["largest-inscribed-ellipsoid-r1-q2"] = containment((2, 1), (3, 0), (1, 4))
    need(
        mismatches,
        abs(containment((2, 1), (3, 0), (1, 4)) - 9) < 1e-12,
        "first containment was not 9",
    )
    # B = diag(3, 1), a = (0, 4), d = (2, 1).
    expected["largest-inscribed-ellipsoid-r3-q2"] = containment((3, 1), (0, 4), (2, 1))
    need(
        mismatches,
        abs(containment((3, 1), (0, 4), (2, 1)) - 8) < 1e-12,
        "second containment was not 8",
    )
    # Slacks for diag(1, 2), center 0.
    slack_a = 5 - containment((1, 2), (2, 0), (0, 0))
    slack_b = 4 - containment((1, 2), (0, 1), (0, 0))
    expected["largest-inscribed-ellipsoid-r4-q2"] = min(slack_a, slack_b)
    need(mismatches, abs(slack_a - 3) < 1e-12 and abs(slack_b - 2) < 1e-12, "slacks drifted")
    # Strip -2 <= x1 <= 2. For diag(p, q), p > 0: p + d1 <= 2 and p - d1 <= 2.
    strip_cases = [(1, 0), (1, 1.5), (0.5, 1), (2, 0), (1, 0)]

    def in_strip(p, d1):
        return p + d1 <= 2 + 1e-12 and p - d1 <= 2 + 1e-12

    strip_yes = [i for i, (p, d1) in enumerate(strip_cases) if in_strip(p, d1)]
    need(mismatches, strip_yes == [0, 2, 3, 4], f"strip indices {strip_yes}")
    need(
        mismatches,
        question(banks, "largest-inscribed-ellipsoid-r2-q2")["correct_indices"] == [0, 2, 3, 4],
        "strip multi indices",
    )
    # Unit disk versus x1 + x2 <= 1. Length of (1, 1) is sqrt(2) > 1.
    need(mismatches, math.sqrt(2) > 1, "sqrt(2) is not greater than 1")
    need(
        mismatches,
        question(banks, "largest-inscribed-ellipsoid-r3-q1")["flaw_index"] == 3,
        "ellipsoid flaw index",
    )
    # B = diag(p, q), a = (1, 0), d = (c, 0). Left-hand side is p + c.
    expect_key(mismatches, banks, "largest-inscribed-ellipsoid-r2-q3", "p+c")
    # Same volume: det diag(4, 1) = det diag(2, 2) = 4.
    need(mismatches, 4 * 1 == 2 * 2, "the two determinants are not equal")

    # Smoothness of (0,0), (1,0), (1,2), (4,2).
    samples = [(0, 0), (1, 0), (1, 2), (4, 2)]
    squares = [norm(tuple(b - a for a, b in zip(p, q))) ** 2 for p, q in zip(samples, samples[1:])]
    expected["trajectory-optimization-r1-q2"] = sum(squares)
    need(mismatches, squares == [1, 4, 9] and sum(squares) == 14, f"smoothness squares {squares}")
    # Energy of controls 2, -1, 2.
    controls = (2, -1, 2)
    expected["trajectory-optimization-r3-q2"] = sum(u * u for u in controls)
    need(mismatches, sum(u * u for u in controls) == 9, "energy was not 9")
    # x+ = 2x + u, x0 = 1, u = (0, 1).
    state = 1
    for control in (0, 1):
        state = 2 * state + control
    expected["trajectory-optimization-r4-q2"] = state
    need(mismatches, state == 5, f"final state was {state}")
    # Outside a disk, and a union of two disjoint intervals, are the nonconvex options.
    nonconvex = [True, False, False, True, False]
    traj_yes = [i for i, flag in enumerate(nonconvex) if flag]
    need(mismatches, traj_yes == [0, 3], f"nonconvex indices {traj_yes}")
    need(
        mismatches,
        question(banks, "trajectory-optimization-r2-q2")["correct_indices"] == [0, 3],
        "nonconvex multi indices",
    )
    # Average of (1, 2) and (1, -2) is (1, 0), distance 0 from (1, 0), not 2.
    mid = ((1 + 1) / 2, (2 + (-2)) / 2)
    gap = norm(tuple(m - c for m, c in zip(mid, (1, 0))))
    need(mismatches, mid == (1, 0) and gap == 0, f"averaged sample {mid} gap {gap}")
    need(
        mismatches,
        question(banks, "trajectory-optimization-r3-q1")["flaw_index"] == 3,
        "trajectory flaw index",
    )
    # Cost w * (s^2 + (4 - s)^2) = w * (2 s^2 - 8 s + 16).
    expect_key(mismatches, banks, "trajectory-optimization-r2-q3", "w*(s^2+(4-s)^2)")
    probe_s = 1
    expanded = probe_s ** 2 + (4 - probe_s) ** 2
    need(mismatches, expanded == 2 * probe_s ** 2 - 8 * probe_s + 16, "smoothness expansion drifted")

    # Worked-example numbers stay out of the banks. Quiz phrases stay out of explainers.
    cov_text = texts["calculus-of-variations"]
    ell_text = texts["largest-inscribed-ellipsoid"]
    traj_text = texts["trajectory-optimization"]
    need(mismatches, "The anchor curvature is -9" in cov_text, "missing curvature marker")
    need(mismatches, "The bead drop is 10" in cov_text, "missing bead marker")
    need(mismatches, "The anchor length is 7" in ell_text, "missing length marker")
    need(mismatches, "The anchor determinant is 21" in ell_text, "missing determinant marker")
    need(mismatches, "The anchor smoothness is 113" in traj_text, "missing smoothness marker")
    need(mismatches, "The anchor landing is 15" in traj_text, "missing landing marker")
    for sid, phrase in (
        ("calculus-of-variations", "The anchor curvature is -9"),
        ("largest-inscribed-ellipsoid", "The anchor length is 7"),
        ("trajectory-optimization", "The anchor smoothness is 113"),
    ):
        raw_bank = "".join(q.get("prompt", "") + q.get("explanation", "") for q in banks[sid]["questions"])
        if phrase in raw_bank:
            mismatches.append(sid + " worked example reused in the bank")
    if "(y^{\\prime})^2 + 3 y" in cov_text or "(y^{\\prime})^2 + 5 y" in cov_text:
        mismatches.append("brachistochrone explainer repeats a quiz integrand")
    if "\\mathrm{diag}(2,\\ 1)" in ell_text or "\\sqrt{2} \\le 1" in ell_text:
        mismatches.append("ellipsoid explainer repeats a quiz figure")
    if "(4,\\ 2)" in traj_text or "u_0 = 0" in traj_text:
        mismatches.append("trajectory explainer repeats a quiz sample")

    numeric = check_expected(banks, expected, mismatches)
    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
