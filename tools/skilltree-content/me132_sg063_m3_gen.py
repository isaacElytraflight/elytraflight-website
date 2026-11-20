#!/usr/bin/env python3
"""SG-063 LTI response, Nyquist, and margins: swap pattern-matchable MC items.

Scope is me132/m3, me132/m4, and me132/m5 intersected with the grandfather
list. That intersection is exactly five banks: lti-stability, freq-resp-lti,
nyquist, uncertainty, loop-margin-design. The other skills in those sections
are not grandfathered. Nothing is added to the grandfather list.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The new questions use the same relations as the
explainers, and the explainer worked examples do not use these prompts.
The verifier does not import this file.

Symbolic ranges are closed boxes on which the key stays finite and positive.
No key is a difference of two independent positives. Every denominator is one
declared variable, or a square root of a sum of squares, and is bounded away
from zero. Prompt names are the graded identifiers (P0, not P_0).
"""
import json
import os

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "lti-stability",
    "freq-resp-lti",
    "nyquist",
    "uncertainty",
    "loop-margin-design",
]


def qnum(qid):
    return int(qid.rsplit("-q", 1)[1])


def fresh(rnd, kind, *args, **kwargs):
    built = Bank("_slot")
    getattr(built, kind)(rnd, *args, **kwargs)
    item = built.qs[0]
    item.pop("id", None)
    item["version"] = 1
    return item


def swaps_for(sid):
    """(old mc id, replacement) in the order that assigns the next free ids."""
    if sid == "lti-stability":
        return [
            ("lti-stability-r1-q1", fresh(
                1, "order",
                r"Order the Routh-Hurwitz test for \(s^3 + a s^2 + b s + c\). Each step after the first uses the result of the step before it.",
                [
                    r"Read a, b, and c, and keep them only if all three are positive. If one is not positive, the polynomial already fails the test.",
                    r"Multiply the a and b kept in the previous step. Call that product the first part of the Hurwitz minor.",
                    r"Subtract c from the product in the previous step. That signed difference is the Hurwitz minor.",
                    r"Every root is in the open left half-plane only when the minor from the previous step is strictly positive. A zero minor puts a root on the imaginary axis.",
                ],
                r"The cubic test needs a, b, and c positive and \(ab > c\). The product \(ab\) without subtracting c is not the minor. A negative trace-style reading of a alone misses b and c. A zero minor is the boundary, where a root is not in the open left half-plane. Solving the cubic is a different route to the same yes-or-no fact.",
            )),
            ("lti-stability-r2-q2", fresh(
                2, "find_error",
                r"A worked solution compares BIBO stability of a transfer function with asymptotic stability of one realization. Exactly one step is wrong.",
                [
                    r"BIBO stability means every bounded input produces a bounded output.",
                    r"A mode cancelled between the numerator and the denominator does not appear as a pole of the transfer function.",
                    r"If that cancelled mode is unstable, the state can grow while every pole of the transfer function stays in the open left half-plane.",
                    r"Therefore every BIBO-stable transfer function comes from an asymptotically stable realization.",
                ],
                3,
                r"Cancellation hides a mode from the input-output map. An unstable hidden mode leaves the transfer function BIBO stable and the realization not asymptotically stable. A minimal realization has no cancelled mode, so the two tests agree. A sinusoid input does not create the hidden mode.",
                reasons=[
                    r"A cancelled unstable mode is invisible in the transfer function, so BIBO stability does not make every realization asymptotically stable.",
                    r"Cancellation deletes the mode from the state as well, so a BIBO-stable transfer function always has an asymptotically stable realization.",
                ],
                correct_reason=0,
            )),
            ("lti-stability-r3-q1", fresh(
                3, "sym",
                r"For \(s^3 + a s^2 + b s + c\), write the critical constant term at which the Routh minor changes sign. a and b are positive. Use a and b.",
                "a*b",
                {"a": (0.25, 12), "b": (0.25, 12)},
                r"The boundary is c = a*b. a+b adds two coefficients and is not the minor. a/b is a ratio of the first two coefficients, not the critical constant term. The sign test also needs a, b, and the constant term positive, and a strictly larger product is the open left half-plane rather than the boundary.",
                alternates=["b*a"],
            )),
        ]
    if sid == "freq-resp-lti":
        return [
            ("freq-resp-lti-r1-q1", fresh(
                1, "order",
                r"Order the steady output of an asymptotically stable linear system driven by a long-running sinusoid. Each step after the first uses the result of the step before it.",
                [
                    r"Read the driving frequency w and the input amplitude A from the sinusoid.",
                    r"Evaluate G at j times the frequency w read in the previous step. Call that complex value Gjw.",
                    r"Multiply the input amplitude A by the modulus of Gjw from the previous step. Call that product the output amplitude.",
                    r"The steady output is a sinusoid at the same frequency w, using the output amplitude from the previous step and shifted by the angle of Gjw.",
                ],
                r"After every natural mode has decayed, the steady output is a sinusoid at the driving frequency. Its amplitude is the input amplitude times \(|G(jw)|\), and its phase shift is the angle of \(G(jw)\). Doubling the frequency is a nonlinear effect. The value \(G(0)\) is the answer only at frequency 0. A pole on the imaginary axis at the driving frequency is not this finite steady sinusoid.",
            )),
            ("freq-resp-lti-r2-q2", fresh(
                2, "find_error",
                r"A worked solution states when \(y = |G(jw)|\,A\sin(wt + \angle G)\) is the steady output. Exactly one step is wrong.",
                [
                    r"The input is a sinusoid of frequency w that has already been applied for a long time.",
                    r"Every eigenvalue has a negative real part, so every natural mode has decayed.",
                    r"The steady output is then a sinusoid at that same frequency w.",
                    r"Moving a pole of G onto jw leaves the amplitude formula valid, because that pole cancels inside G(jw).",
                ],
                3,
                r"The formula is the forced response after the homogeneous solution has vanished, which needs every eigenvalue in the open left half-plane. A pole at the driving frequency resonates, and a finite value \(G(jw)\) does not give the amplitude. An unstable mode grows over the sinusoid. Amplitude that depends on A is a nonlinear effect.",
                reasons=[
                    r"A pole at jw resonates with the input, so the finite value G(jw) does not give the steady amplitude.",
                    r"A pole at jw is still one complex number, so the amplitude formula is unchanged.",
                ],
                correct_reason=0,
            )),
            ("freq-resp-lti-r3-q1", fresh(
                3, "sym",
                r"The transfer function is K/(s+a), with K and a positive. Write its magnitude at the positive frequency w. Use K, a, and w.",
                "K/sqrt(a**2 + w**2)",
                {"K": (0.5, 40), "a": (0.25, 20), "w": (0.25, 30)},
                r"Substitute s = jw. The numerator magnitude is K and the denominator magnitude is the square root of a squared plus w squared. K/a is the magnitude only at w = 0. sqrt(a**2 + w**2)/K inverts the magnitude. K/w drops the pole's real part. The state-space form C(jw I - A)^{-1}B + D is this same number when the transfer function is K/(s+a).",
                alternates=["K/sqrt(w**2 + a**2)", "K*(a**2 + w**2)**(-0.5)"],
            )),
        ]
    if sid == "nyquist":
        return [
            ("nyquist-r1-q1", fresh(
                1, "order",
                r"Order the Nyquist count that decides closed-loop stability. Each step after the first uses the result of the step before it.",
                [
                    r"Draw the curve of L(jw) in the complex plane and mark the point -1.",
                    r"On the curve from the previous step, count the clockwise encirclements of the marked point -1. Call that count N.",
                    r"Add the open-loop right-half-plane pole count P to the N from the previous step. Call the sum Z.",
                    r"The closed loop is stable only when the Z from the previous step is zero. A positive Z is the number of closed-loop right-half-plane poles.",
                ],
                r"The criterion is Z = N + P, with N the clockwise encirclements of -1 and P the open-loop right-half-plane poles. Stability needs Z = 0. Requiring |L| < 1 at every frequency is a stricter and different test. The origin is not the critical point. A counter-clockwise encirclement subtracts from the clockwise count rather than adding another positive N.",
            )),
            ("nyquist-r1-q2", fresh(
                1, "sym",
                r"A stable open-loop Nyquist curve crosses the negative real axis at -d. d is positive and less than 1. Write the gain margin as a factor. Use d.",
                "1/d",
                {"d": (0.05, 0.9)},
                r"The crossing is at -d, so the loop gain can be multiplied by 1/d before the crossing reaches -1. d itself is the distance from the origin, not the margin. 1-d is the gap from the crossing to -1 in the plane, not the gain factor. -1/d is the same factor with the wrong sign. The phase margin is read on the unit circle, not at this real-axis crossing.",
                alternates=["d**(-1)"],
            )),
            ("nyquist-r2-q3", fresh(
                2, "find_error",
                r"A worked solution says where phase margin is read on a Nyquist plot. Exactly one step is wrong.",
                [
                    r"Phase margin is the extra phase lag that would put the loop on the stability boundary.",
                    r"That extra lag is measured at the frequency where the magnitude of L is 1.",
                    r"On the Nyquist plot, magnitude 1 is the unit circle centered at the origin.",
                    r"Phase margin is therefore the distance from the origin to the negative-real crossing.",
                ],
                3,
                r"Phase margin is an angle at the gain crossover, where the curve meets the unit circle. The negative-real crossing is the phase crossover, and the factor 1 over its distance from the origin is the gain margin. Requiring the curve to pass through -1 would mean the margin is already zero. The largest imaginary part is not a margin.",
                reasons=[
                    r"The negative-real crossing is where gain margin is read. Phase margin is the angle where the curve meets the unit circle.",
                    r"Phase margin and gain margin are the same number, so either crossing measures both.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "uncertainty":
        return [
            ("uncertainty-r1-q1", fresh(
                1, "sym",
                r"The nominal gain is P0 and the multiplicative weight magnitude is Wm. Both are positive. Write the largest plant gain that weight allows. Use P0 and Wm.",
                "P0*(1+Wm)",
                {"P0": (0.4, 40), "Wm": (0.05, 1.5)},
                r"The upper end of the multiplicative bound is P0*(1+Wm). P0*Wm is only the amount added to the nominal gain, not the largest gain. P0/(1+Wm) shrinks the nominal gain. P0+Wm adds a relative weight to a gain as if the weight were already absolute. An additive weight bounds |P-P0| directly and is a different model.",
                alternates=["P0+P0*Wm", "(1+Wm)*P0"],
            )),
            ("uncertainty-r2-q2", fresh(
                2, "order",
                r"Order a multiplicative weight that covers one measured gain. Each step after the first uses the result of the step before it.",
                [
                    r"Read the nominal gain P0, which is not zero, and one measured plant gain P.",
                    r"From P and the P0 read in the previous step, take the absolute value of P minus P0. Call that the absolute error.",
                    r"Divide the absolute error from the previous step by the same P0. That quotient is the relative error.",
                    r"Set the multiplicative weight magnitude Wm equal to the relative error from the previous step, so this measurement sits on the boundary of the bound.",
                ],
                r"The relative error is the absolute error divided by the nominal gain, and a multiplicative weight has to be at least that large to cover the measurement. The absolute error alone is an additive weight. Dividing by the measured gain instead of the nominal gain is a different ratio. A weight smaller than the relative error leaves this measurement outside the bound.",
            )),
            ("uncertainty-r3-q1", fresh(
                3, "find_error",
                r"A worked solution classifies a gain that lies in a known interval and adds no poles or zeros. Exactly one step is wrong.",
                [
                    r"A gain that lies in a known interval, with no extra poles or zeros, is parametric uncertainty.",
                    r"A multiplicative weight can cover that interval.",
                    r"When the entire error is a pure gain, the weight does not have to grow with frequency.",
                    r"That same pure-gain interval is unmodeled dynamics, so the weight is required to grow with frequency.",
                ],
                3,
                r"One real parameter in an interval is parametric uncertainty. Unmodeled dynamics are extra modes the nominal model left out, and those are what make a weight grow with frequency. A multiplicative weight may cover a pure gain interval, and it can be constant across frequency. A right-half-plane zero would be part of the nominal model, not this interval.",
                reasons=[
                    r"A pure gain in an interval is parametric. A weight has to grow with frequency when the model left dynamics out, not for this interval.",
                    r"Every multiplicative weight has to grow with frequency, including one that only covers a constant gain interval.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "loop-margin-design":
        return [
            ("loop-margin-design-r1-q1", fresh(
                1, "order",
                r"Order a delay-margin calculation from a loop transfer L. Each step after the first uses the result of the step before it.",
                [
                    r"Find the gain crossover wc, the frequency where the magnitude of L is 1.",
                    r"At the frequency wc from the previous step, convert 180 degrees plus the phase of L into radians. Call that number pm.",
                    r"Divide the pm from the previous step by the same wc. That quotient is the delay margin in seconds.",
                    r"A pure delay longer than the margin from the previous step spends the phase margin and puts the loop on the stability boundary.",
                ],
                r"Delay margin is the phase margin in radians divided by the gain-crossover frequency. Dividing degrees by rad/s does not give seconds. The gain margin is a factor on |L| at the phase crossover and does not by itself give this delay. A larger crossover at the same phase margin leaves less room for delay.",
            )),
            ("loop-margin-design-r1-q3", fresh(
                1, "find_error",
                r"A worked solution explains a gain margin of 6 dB. Exactly one step is wrong.",
                [
                    r"Gain margin is how far the magnitude of L sits below 1 at the frequency where the phase is -180 degrees.",
                    r"6 dB is a factor of 2.",
                    r"Doubling the loop gain would move that negative-real crossing onto -1.",
                    r"Halving the loop gain would also move that same crossing onto -1.",
                ],
                3,
                r"A gain margin of 6 dB means the loop gain can increase by a factor of about 2 before the phase-crossover point reaches -1. Cutting the gain moves that crossing toward the origin, farther from -1. A positive margin means the loop is stable on the model. The margin is not an overshoot in dB.",
                reasons=[
                    r"Halving the gain moves a crossing near -0.5 toward the origin. The factor of 2 is the increase that reaches -1.",
                    r"Gain margin is symmetric, so the same factor reaches -1 when the gain is raised or lowered.",
                ],
                correct_reason=0,
            )),
            ("loop-margin-design-r3-q3", fresh(
                3, "multi",
                r"Which statements about margins are true? Select every correct statement.",
                [
                    r"The delay margin, in seconds, equals the phase margin in radians divided by the gain-crossover frequency.",
                    r"A phase margin of 30 degrees means the closed loop is already unstable.",
                    r"The sensitivity peak is the reciprocal of the closest distance from the Nyquist curve of L to -1.",
                    r"Phase margin is the quantity that sets the steady-state error of a step.",
                ],
                [0, 2],
                r"Delay margin spends the phase margin, in radians, at the rate of the crossover frequency. The sensitivity peak is 1 over the distance from the curve to -1. A phase margin of 30 degrees is still a positive margin, so the model loop is stable, with a lightly damped step. Steady-state error is set by the loop gain and the system type, not by the phase margin.",
            )),
        ]
    raise SystemExit("no swaps for " + sid)


def apply_skill(sid):
    path = os.path.join(BANK_DIR, sid + ".json")
    with open(path, encoding="utf-8") as f:
        bank = json.load(f)
    live = {q["id"]: i for i, q in enumerate(bank["questions"])}
    retired = list(bank.get("retired_questions") or [])
    changed = False
    for old_id, new in swaps_for(sid):
        if old_id not in live:
            continue
        idx = live[old_id]
        old = bank["questions"][idx]
        if old.get("type") != "mc":
            raise SystemExit(old_id + " is no longer multiple choice")
        rnd = old["round"]
        used = []
        for q in bank["questions"]:
            if q.get("round") == rnd:
                used.append(qnum(q["id"]))
        for q in retired:
            if q.get("round") == rnd:
                used.append(qnum(q["id"]))
        number = max(used) + 1
        new = dict(new)
        new["id"] = f"{sid}-r{rnd}-q{number}"
        new["round"] = rnd
        new["version"] = 1
        if not isinstance(old.get("version"), int):
            old["version"] = 1
        retired.append(old)
        bank["questions"][idx] = new
        live[new["id"]] = idx
        del live[old_id]
        changed = True
    if not changed:
        print(sid, "already swapped")
        return
    bank["retired_questions"] = retired
    bank["version"] = int(bank.get("version") or 1) + 1
    seen = []
    for q in bank["questions"] + retired:
        if q["id"] in seen:
            raise SystemExit(sid + " duplicate id " + q["id"])
        seen.append(q["id"])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)
        f.write("\n")
    deep = sum(1 for q in bank["questions"] if q["type"] in ("symbolic", "order", "error", "multi"))
    figs = sum(1 for q in bank["questions"] if q.get("figure"))
    print(f"{sid} version {bank['version']}: {deep}/{len(bank['questions'])} deep, {figs} figures, retired {len(retired)}")


def drop_grandfather():
    with open(GRAND, encoding="utf-8") as f:
        data = json.load(f)
    before = len(data["skills"])
    if len(data["skills"]) != len(set(data["skills"])):
        raise SystemExit("grandfather already has duplicate ids")
    drop = set(SKILLS)
    missing = sorted(drop - set(data["skills"]))
    if missing:
        raise SystemExit("not on the grandfather list: " + ", ".join(missing))
    data["skills"] = [sid for sid in data["skills"] if sid not in drop]
    if len(data["skills"]) != len(set(data["skills"])):
        raise SystemExit("grandfather gained a duplicate")
    added = set(data["skills"]) - set(json.load(open(GRAND, encoding="utf-8"))["skills"])
    if added:
        raise SystemExit("grandfather gained ids: " + ", ".join(sorted(added)))
    with open(GRAND, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("grandfather", before, "->", len(data["skills"]))


def main():
    for sid in SKILLS:
        apply_skill(sid)
    drop_grandfather()


if __name__ == "__main__":
    main()
