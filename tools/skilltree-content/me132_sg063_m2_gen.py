#!/usr/bin/env python3
"""SG-063 first- and second-order systems and PID: swap pattern-matchable MC items.

Scope is the ME 132 section after me132/m1, which is me132/m2, intersected
with the grandfather list and capped at the first five in graph order. That
intersection is exactly five banks: laplace, step-specs, pid, windup,
pid-tuning. step-resp, fb-errors, first-order-sys, second-order-sys, and
lti-mech sit in the section and are not grandfathered.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The new questions use the same relations as the
explainers, and the explainer worked examples do not use these prompts.
The verifier does not import this file.

Symbolic ranges are closed boxes on which the key stays finite and keeps one
sign. No key is a difference of two independent positives, so a remainder
cannot come out negative or pass through zero. Every denominator is a single
variable, or a sum or product of quantities, bounded away from zero.
"""
import json
import os

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "laplace",
    "step-specs",
    "pid",
    "windup",
    "pid-tuning",
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
    if sid == "laplace":
        return [
            ("laplace-r1-q1", fresh(
                1, "sym",
                r"Write the Laplace transform of a step of height \(A\) that turns on at \(t = 0\). The Laplace variable is \(s\), with positive real part. Use \(A\) and \(s\).",
                "A/s",
                {"A": (0.5, 25), "s": (0.2, 30)},
                r"Integrating \(A e^{-st}\) from \(0\) to infinity gives \(A/s\) when the real part of \(s\) is positive. \(A/(s+A)\) is a decaying exponential, not a step. \(A/s^2\) is a ramp of slope \(A\). \(s/A\) is what a derivative does to a transform, upside down, and it is not the transform of a step.",
                alternates=["A*s**(-1)", "(1/s)*A"],
            )),
            ("laplace-r1-q3", fresh(
                1, "order",
                r"Order the derivative rule for a signal that does not start at rest. Each step after the first uses the result of the step before it.",
                [
                    r"Take the transform \(F\) of the signal, and read the initial value \(f(0)\) off the time signal.",
                    r"Multiply that transform by \(s\). Call the product \(sF\). It equals the transform of the derivative only when \(f(0)\) is zero.",
                    r"Subtract the initial value read in the first step from the product in the previous step.",
                    r"That difference, \(sF - f(0)\), is the transform of the derivative. Do not divide it by \(s\); dividing by \(s\) is the integral rule.",
                ],
                r"Integration by parts puts a minus on the initial value, so the transform of \(\dot f\) is \(sF - f(0)\). Adding \(f(0)\) flips that sign. Dropping \(f(0)\) is legitimate only when the signal starts at rest. \(F/s\) is the integral of \(f\), and applying it after the derivative rule would integrate the derivative back toward \(f\).",
            )),
            ("laplace-r2-q2", fresh(
                2, "find_error",
                r"A worked solution writes the Laplace transform of \(\sin(w t)\) for \(t \ge 0\). The frequency \(w\) is positive. Exactly one step is wrong.",
                [
                    r"The signal is a sine of radian frequency \(w\), starting at \(t = 0\).",
                    r"The denominator of the transform is \(s^2 + w^2\).",
                    r"The numerator is the frequency \(w\), not \(s\).",
                    r"The transform is therefore \(s/(s^2 + w^2)\).",
                ],
                3,
                r"The sine transform is \(w/(s^2+w^2)\). The cosine transform is the one with \(s\) in the numerator and the same denominator. \(1/(s+w)\) is a real exponential. Putting \(w^2\) in the numerator double-counts the frequency.",
                reasons=[
                    r"Sine carries \(w\) in the numerator. The step that writes \(s\) there has copied the cosine transform.",
                    r"Sine and cosine share the numerator \(s\). Only the sign inside the denominator changes.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "step-specs":
        return [
            ("step-specs-r1-q1", fresh(
                1, "order",
                r"Order a 10% to 90% rise-time measurement on a step response. Each step after the first uses the result of the step before it.",
                [
                    r"Wait until the output has settled, and read that final value. The percentages are fractions of this value.",
                    r"Mark the instant the output crosses 10% of the final value read in the previous step.",
                    r"After that 10% instant, mark the next instant the output crosses 90% of the same final value.",
                    r"Subtract the 10% instant from the 90% instant marked in the previous step. That positive difference is the rise time.",
                ],
                r"The 10% to 90% rise time skips the slow start and stops before overshoot. A 0% to 100% interval is ambiguous once the output goes past the final value. The peak-to-final interval is settling, not rise time. A 50% to 100% interval drops the early part of the rise. The subtraction has to be the later instant minus the earlier one.",
            )),
            ("step-specs-r2-q3", fresh(
                2, "find_error",
                r"A worked solution says what percent overshoot of an underdamped second-order step depends on. Exactly one step is wrong.",
                [
                    r"Percent overshoot is \(100\) times \(e\) to the power \(-\pi\zeta/\sqrt{1-\zeta^2}\).",
                    r"That expression contains the damping ratio \(\zeta\) and does not contain \(\omega_n\).",
                    r"Two loops with the same \(\zeta\) and different \(\omega_n\) therefore have the same percent overshoot.",
                    r"Raising \(\omega_n\) while holding \(\zeta\) fixed cuts that percent overshoot, because the peaks arrive sooner.",
                ],
                3,
                r"Overshoot depends only on \(\zeta\). \(\omega_n\) scales time, so the peak arrives sooner, and the percent by which the peak passes the final value does not change. Settling time is the specification that depends on the product \(\zeta\omega_n\). A larger \(\zeta\) is what cuts overshoot.",
                reasons=[
                    r"Overshoot is fixed by \(\zeta\) alone. A larger \(\omega_n\) moves the peak earlier and leaves the percent unchanged.",
                    r"Overshoot depends on the product \(\zeta\omega_n\), so raising \(\omega_n\) at fixed \(\zeta\) reduces it.",
                ],
                correct_reason=0,
            )),
            ("step-specs-r3-q3", fresh(
                3, "sym",
                r"Write the steady error of a type-0 loop to a unit step. The DC loop gain is the positive number \(K\). Use \(K\).",
                "1/(1+K)",
                {"K": (0.25, 40)},
                r"With no free integrator, the DC error to a unit step is \(1/(1+K)\). \(K/(1+K)\) is the closed-loop DC gain, the fraction of the step that is achieved, not the miss. \(1/K\) is the ramp error of a type-1 loop. Zero is the step error only when the loop already has a free integrator. Raising \(K\) shrinks the error and does not remove it.",
                alternates=["1/(K+1)", "(1+K)**(-1)"],
            )),
        ]
    if sid == "pid":
        return [
            ("pid-r1-q1", fresh(
                1, "order",
                r"Order the parallel PID law, starting from the proportional term. Each step after the first uses the result of the step before it.",
                [
                    r"Start from the proportional term \(K_p\), a constant gain on the error.",
                    r"Add \(K_i/s\) to that constant. The sum now has a pole at the origin, which is what drives a constant error to zero.",
                    r"Add \(K_d s\) to the sum from the previous step. The numerator is now quadratic, and the denominator is still \(s\).",
                    r"Write that three-term sum as the single fraction \((K_d s^2 + K_p s + K_i)/s\). Do not cancel the pole at the origin from the second step.",
                ],
                r"The integral term is the one that removes a constant error, because its pole sits at the origin. The derivative term is the one that adds high-frequency phase lead. Adding the derivative before the integral would leave a sum with no pole at the origin, which is a PD law, not this PID fraction. Canceling the pole deletes the term that zeros a constant error. Proportional control alone cannot do that.",
            )),
            ("pid-r1-q3", fresh(
                1, "find_error",
                r"A worked solution says what raising \(K_p\) does in a stable loop that has no integral term. Exactly one step is wrong.",
                [
                    r"Raising \(K_p\) raises the loop gain \(L\).",
                    r"The steady error to a constant reference is \(1/(1+L)\), so the larger \(L\) shrinks that error.",
                    r"Any finite \(K_p\) leaves a nonzero steady error, because this loop has no integral term.",
                    r"A large enough \(K_p\) makes that steady error exactly zero, and a further increase cannot destabilize the loop.",
                ],
                3,
                r"Without an integrator, the steady error is \(1/(1+L)\) and stays positive for every finite \(K_p\). Raising \(K_p\) shrinks it. The same increase can push a stable loop across the stability boundary. Integral action is what makes a constant error rest at zero. Stability is not immune to gain.",
                reasons=[
                    r"A larger \(K_p\) only shrinks \(1/(1+L)\). The error stays nonzero with no integrator, and enough gain can destabilize the loop.",
                    r"Raising \(K_p\) removes the steady error and leaves the stability margins unchanged.",
                ],
                correct_reason=0,
            )),
            ("pid-r2-q1", fresh(
                2, "sym",
                r"A PD controller is \(K_p + K_d s\), with \(K_p\) and \(K_d\) positive. Its zero is in the open left half-plane. Write the positive distance from the origin to that zero. Use \(K_p\) and \(K_d\).",
                "Kp/Kd",
                {"Kp": (0.4, 25), "Kd": (0.05, 8)},
                r"The zero solves \(K_p + K_d s = 0\), so \(s = -K_p/K_d\). The distance from the origin is the positive number \(K_p/K_d\). \(K_d/K_p\) inverts the ratio and moves the break frequency. \(K_p K_d\) multiplies the two gains and is not a frequency. \(K_p + K_d\) adds them. The derivative term's phase lead comes from this zero, not from a pole at the origin. Infinite DC gain is the integral term.",
                alternates=["Kp*Kd**(-1)", "(1/Kd)*Kp"],
            )),
        ]
    if sid == "windup":
        return [
            ("windup-r1-q1", fresh(
                1, "order",
                r"Order integrator windup and the overshoot it adds. Each step after the first uses the result of the step before it.",
                [
                    r"The command passes the actuator limit, so the plant input sticks at the limit while the error is still nonzero.",
                    r"The integrator does not see that limit and keeps adding \(K_i\) times the error from the previous step, so its state climbs past the value that matches the limit.",
                    r"The output then reaches the reference and the error changes sign, but the state climbed in the previous step is still large.",
                    r"The command therefore stays saturated in the old direction until that large state has integrated back down. That extra travel is the overshoot.",
                ],
                r"Windup is the integrator running past the actuator limit while the error is still nonzero. A sign change in the error starts the unwinding and does not finish it, so the actuator stays saturated on the way back. Nothing in the plain PID law resets the state in one step. Zero proportional gain is a different detuning, and a zero error does not wind anything up.",
            )),
            ("windup-r2-q2", fresh(
                2, "sym",
                r"Back-calculation adds \((u_{\mathrm{sat}} - u)/T_t\) to the integrator input. The unsaturated command is above the limit, and excess is the positive amount \(u - u_{\mathrm{sat}}\). The tracking time is \(T_t\). Write the added rate. Use excess and Tt.",
                "-excess/Tt",
                {"excess": (0.5, 30), "Tt": (0.1, 5)},
                r"The added rate is \((u_{\mathrm{sat}} - u)/T_t = -excess/T_t\). It is negative, so the state unwinds instead of climbing. \(+excess/T_t\) is the opposite sign, \(u - u_{\mathrm{sat}}\) over \(T_t\), and it winds the integrator further into the stop. \(excess \cdot T_t\) grows with the tracking time, which is the wrong direction: a longer \(T_t\) should unwind more slowly. The rate is never zero while the command is strictly above the limit.",
                alternates=["-(excess/Tt)", "(-1)*excess/Tt", "-excess*Tt**(-1)"],
            )),
            ("windup-r3-q1", fresh(
                3, "find_error",
                r"A worked solution says when clamping stops the integrator. Exactly one step is wrong.",
                [
                    r"The actuator is already against its stop.",
                    r"The error has the sign that would drive the command further into that stop.",
                    r"Clamping stops the integrator in that direction only.",
                    r"Clamping also freezes the integrator after the error reverses, so the state can never unwind.",
                ],
                3,
                r"Clamping freezes only the direction that deepens saturation. When the error reverses, integration runs again and the state can come back down. Freezing whenever the error is nonzero also freezes ordinary tracking, inside the limits. Freezing at zero error does nothing, because the integrand is already zero. The derivative term is not the signal being clamped.",
                reasons=[
                    r"Clamping stops only the direction that pushes further into the stop. A reversed error is allowed to integrate, which is how the state unwinds.",
                    r"Clamping freezes the integrator whenever the error is nonzero, in either direction, until the error is exactly zero.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "pid-tuning":
        return [
            ("pid-tuning-r1-q1", fresh(
                1, "order",
                r"Order the ultimate-gain PID rule. Each step after the first uses the result of the step before it.",
                [
                    r"Close the loop with proportional control only, and raise that gain until the output oscillates at constant amplitude.",
                    r"From that oscillation, read \(K_u\) as the gain just reached, and read \(T_u\) as one full period of it. A half-cycle of the same oscillation is not \(T_u\).",
                    r"Set \(K_p\) to \(0.6\) times the \(K_u\) read in the previous step. This \(K_p\) does not use the period.",
                    r"Using the \(T_u\) read in the second step, and leaving the \(K_p\) written in the previous step unchanged, set \(\tau_i = T_u/2\) and \(\tau_d = T_u/8\).",
                ],
                r"\(K_u\) is the proportional gain on the stability boundary, and \(T_u\) is one full period of that oscillation. \(K_p = 0.6 K_u\) does not depend on \(T_u\). The two times do. Calling a half-cycle \(T_u\) leaves \(K_p\) alone and cuts both times in half. An open-loop step fit is the reaction-curve experiment, not this one.",
            )),
            ("pid-tuning-r2-q2", fresh(
                2, "sym",
                r"Write the PID reaction-curve proportional gain. The open-loop step fit has gain \(K\), lag \(\tau\), and delay \(L\), all positive, and \(a = KL/\tau\). The PID rule is \(K_p = 1.2/a\). Use \(K\), \(L\), and \(\tau\).",
                "1.2*tau/(K*L)",
                {"K": (0.4, 15), "L": (0.15, 6), "tau": (0.4, 25)},
                r"Substitute \(a = KL/\tau\) into \(K_p = 1.2/a\) and the gain is \(1.2\,\tau/(KL)\). \(1.2 a\) inverts the rule, so a larger delay would raise \(K_p\) instead of lowering it. \(0.9/a\) is the PI reaction-curve gain, not the PID gain. Dropping \(L\) is the mistake of treating a plant with delay as a plant with none. The ultimate-gain rule is a different experiment and does not use \(K\), \(\tau\), and \(L\).",
                alternates=["1.2/(K*L/tau)", "(1.2/K)*(tau/L)", "1.2*tau/(L*K)"],
            )),
            ("pid-tuning-r3-q1", fresh(
                3, "multi",
                r"A plant has a positive gain, lag, and delay. Which statements about the tuning rules are true? Select every correct statement.",
                [
                    r"Lambda tuning sets \(K_p = \tau/(K(\lambda+L))\) and \(\tau_i = \tau\). A larger \(\lambda\) lowers \(K_p\).",
                    r"Lambda tuning is the milder rule because it deletes the plant delay from \(K_p\).",
                    r"On the same step fit, the PI reaction-curve gain \(0.9/a\) is smaller than the PID gain \(1.2/a\).",
                    r"The reaction-curve experiment raises the proportional gain until the closed loop oscillates at constant amplitude.",
                ],
                [0, 2],
                r"Lambda tuning keeps the delay inside \(\lambda+L\), and a larger requested closed-loop time constant lowers \(K_p\). That is why it is milder than sitting on the stability boundary. The PI reaction-curve coefficient is \(0.9\), the PID coefficient is \(1.2\), and \(a\) is the same positive number, so the PI gain is the smaller one. Driving the closed loop to constant-amplitude oscillation is the ultimate-gain experiment, not the open-loop step fit.",
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
