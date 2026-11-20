#!/usr/bin/env python3
"""SG-063 Feedback Systems, final four banks.

Scope is Frequency domain analysis and Frequency domain design intersected
with the grandfather list. That intersection is exactly four banks:
min-phase, gen-gain-phase, feedforward, perf-specs-freq. This is the last
slice, so the grandfather list is empty afterward. Nothing is added.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The new questions use the same relations as the
explainers, and the explainer worked examples do not use these prompts.
The verifier does not import this file.

Symbolic ranges are closed boxes on which the key stays finite and positive.
No key is a difference of two independent positives. Every denominator is
bounded away from zero on the box. Prompt names are the graded identifiers
(a, b, M, not a_1).
"""
import itertools
import json
import os
import re

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "min-phase",
    "gen-gain-phase",
    "feedforward",
    "perf-specs-freq",
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
    if sid == "min-phase":
        return [
            ("min-phase-r1-q1", fresh(
                1, "order",
                r"Order the minimum-phase slope rule, then the addition that breaks it. Each step after the first uses the result of the step before it.",
                [
                    r"A frequency response is minimum phase when every finite zero lies in the open left half-plane and there is no time delay. For that response, a magnitude slope held across a wide band fixes the phase.",
                    r"Hold the minimum-phase response from the previous step at a slope of \(-20\ \mathrm{dB}\) per decade across a wide band. The phase in that band is near \(-90^\circ\).",
                    r"Double the wideband slope from the previous step, to \(-40\ \mathrm{dB}\) per decade. The same rule then puts the phase near \(-180^\circ\).",
                    r"Start from the near \(-180^\circ\) phase given by the previous step, and multiply by either a pure time delay or the all-pass \((z-s)/(z+s)\) for some \(z > 0\). Each factor has magnitude 1, so the magnitude slope is unchanged, and each adds negative phase at every positive frequency. The phase is then more negative than the slope rule predicted.",
                ],
                r"For a minimum-phase response, a wideband slope of \(-20n\ \mathrm{dB}\) per decade sits near \(-90n\) degrees. So \(-20\) sits near \(-90^\circ\) and \(-40\) sits near \(-180^\circ\). A pure delay and the all-pass \((z-s)/(z+s)\) each have magnitude 1, so they leave that slope unchanged and add lag the slope rule does not predict.",
            )),
            ("min-phase-r1-q3", fresh(
                1, "sym",
                r"a and b are positive. A pure delay of a seconds is evaluated at frequency b radians per second. Write the phase lag in radians. Use a and b.",
                "a*b",
                {"a": (0.05, 2), "b": (0.5, 20)},
                r"A delay of \(a\) seconds has frequency response \(e^{-j b a}\). The phase is \(-a b\) radians, so the positive lag is \(a b\) radians. The ratio \(a/b\) is a time, not this lag. The sum \(a+b\) is not the lag. A minimum-phase factor has no delay, so this product is exactly the extra lag a delay adds on top of the slope rule.",
                alternates=["b*a", "(a)*(b)", "a*b*1"],
            )),
            ("min-phase-r2-q2", fresh(
                2, "multi",
                r"Which statements about minimum phase are true? Select every correct statement.",
                [
                    r"A transfer function is minimum phase when every finite zero lies in the open left half-plane and there is no time delay.",
                    r"\(\dfrac{s+3}{(s+1)(s+8)}\) is minimum phase: its only finite zero is at \(-3\), and it has no time delay.",
                    r"For every \(z > 0\), \(\dfrac{z-s}{z+s}\) has magnitude 1 at every \(s = j\omega\) with \(\omega\) real, and for every \(\omega > 0\) its phase equals \(-2\tan^{-1}(\omega/z)\), which is lag.",
                    r"A transfer function is minimum phase whenever every pole lies in the open left half-plane, including when it has a right-half-plane zero or a pure delay.",
                ],
                [0, 1, 2],
                r"Minimum phase is a condition on the finite zeros and on time delay, not on the poles. \((s+3)/((s+1)(s+8))\) has its only finite zero at \(-3\) and no delay. For \(z > 0\), \((z-s)/(z+s)\) is an all-pass: magnitude 1 on the imaginary axis, and phase \(-2\tan^{-1}(\omega/z)\) for \(\omega > 0\). A stable pole set does not cancel a right-half-plane zero or a delay.",
            )),
        ]
    if sid == "gen-gain-phase":
        return [
            ("gen-gain-phase-r1-q1", fresh(
                1, "order",
                r"Order how a describing function predicts a periodic orbit of a relay or a saturation. Each step after the first uses the result of the step before it.",
                [
                    r"Drive an odd memoryless nonlinearity with one sine of amplitude \(a\). The describing function \(N(a)\) is the complex gain of the fundamental component of the output. Higher harmonics are discarded.",
                    r"Restrict the nonlinearity of the previous step to an ideal relay or a saturation with no hysteresis. Then \(N(a)\) is real and positive. For the ideal relay, \(N(a)\) falls as \(a\) grows.",
                    r"Place the real positive describing function from the previous step in negative feedback with a linear plant \(G\). A predicted periodic orbit satisfies \(G(j\omega)\, N(a) = -1\).",
                    r"Read the balance equation from the previous step on the Nyquist diagram. The curve of \(G\) intersects the locus \(-1/N(a)\). The curve of \(G\) supplies the frequency, and the locus supplies the amplitude.",
                ],
                r"The describing function keeps the fundamental and drops the harmonics. An ideal relay or a memoryless saturation has a real positive \(N(a)\), and the relay's \(N(a) = 4M/(\pi a)\) falls as \(a\) grows. Negative feedback with a linear plant balances at \(G(j\omega) N(a) = -1\), which is an intersection of the plant Nyquist curve with \(-1/N(a)\).",
            )),
            ("gen-gain-phase-r2-q2", fresh(
                2, "sym",
                r"M and a are positive. An ideal relay switches between -M and M. For one sine of amplitude a, write the describing function. Use M and a.",
                "4*M/(pi*a)",
                {"M": (0.25, 12), "a": (0.25, 12)},
                r"The fundamental of an ideal relay of levels \(\pm M\), driven by a sine of amplitude \(a\), is \(N(a) = 4M/(\pi a)\). The value is real and positive, and it falls as \(a\) grows. The product \(M*a\) is not that gain. The reciprocal \(a/M\) is not that gain. The locus used in the Nyquist balance is \(-1/N(a)\), not \(N(a)\) itself.",
                alternates=["(4*M)/(pi*a)", "4*M/(a*pi)", "(4/(pi))*(M/a)"],
            )),
            ("gen-gain-phase-r3-q1", fresh(
                3, "find_error",
                r"A worked solution states facts about the describing-function approximation. Exactly one step is wrong.",
                [
                    r"The describing function keeps the fundamental component and discards the higher harmonics. The resulting gain may depend on the amplitude.",
                    r"An odd memoryless map has a real describing function. A relay with hysteresis has memory, so its describing function is complex and includes phase lag.",
                    r"The approximation is most believable when the linear plant is low-pass, so each harmonic is smaller at the nonlinearity input than the fundamental is.",
                    r"The approximation becomes exact when the plant gain is largest at the third harmonic, because that larger harmonic makes the input closer to one pure sine.",
                ],
                3,
                r"The method needs a nearly sinusoidal input to the nonlinearity. A low-pass plant attenuates harmonics before they return, which supports that assumption. A plant that amplifies the third harmonic breaks the assumption, so the approximation is less believable there. An odd memoryless map has a real describing function. Hysteresis adds memory and can make the describing function complex.",
                reasons=[
                    r"A low-pass plant attenuates harmonics before they return. A plant that amplifies the third harmonic breaks the nearly sinusoidal assumption.",
                    r"A larger third harmonic is closer to a pure sine, so the describing function becomes exact.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "feedforward":
        return [
            ("feedforward-r1-q1", fresh(
                1, "order",
                r"Order what a reference prefilter changes and what it leaves alone. Each step after the first uses the result of the step before it.",
                [
                    r"Start from a unity-feedback loop with loop gain \(L\). The sensitivity is \(S = 1/(1+L)\) and the complementary sensitivity is \(T = L/(1+L)\). The poles of this feedback loop are the roots of \(1+L = 0\).",
                    r"Place a reference prefilter \(F\) in front of the loop from the previous step, and leave the feedback path unchanged. The loop gain, the stability margins, \(S\), and \(T\) all stay the same.",
                    r"Multiply the unchanged \(T\) from the previous step by the prefilter \(F\). The reference-to-output map is \(F\) times \(T\). Changing \(F\) changes that map and does not move the poles of the feedback loop.",
                    r"Hold the map \(F\) times \(T\) from the previous step fixed, and change only the reference waveform. The loop gain does not depend on that waveform, so this change does not require a redesign of \(L\).",
                ],
                r"A reference prefilter sits outside the loop, so \(L\), the margins, \(S\), and \(T\) stay put. The reference-to-output map is \(F T\), and the poles of the feedback loop remain the roots of \(1+L = 0\). Changing the reference waveform does not change \(L\). The prefilter does not see sensor noise on the measured output, and it does not by itself create the infinite DC loop gain of an integrator.",
            )),
            ("feedforward-r2-q2", fresh(
                2, "sym",
                r"a and b are positive. The true plant DC gain is a. The model used for open-loop inversion has DC gain b. With no feedback, write the reference-to-output DC gain. Use a and b.",
                "a/b",
                {"a": (0.25, 20), "b": (0.25, 20)},
                r"Open-loop inversion uses the feedforward gain \(1/b\). On the true plant the DC gain is \(a/b\). The gain equals 1 only when \(a = b\). The product \(a*b\) is not the closed reference gain. The reciprocal \(b/a\) is the gain of the opposite mismatch. With no feedback, nothing trims the residual \(a/b - 1\).",
                alternates=["a*b**(-1)", "(a)/(b)", "a*(1/b)"],
            )),
            ("feedforward-r3-q1", fresh(
                3, "find_error",
                r"A worked solution states facts about feedforward. Exactly one step is wrong.",
                [
                    r"A reference prefilter placed in front of an otherwise unchanged feedback loop leaves the loop gain and the stability margins unchanged.",
                    r"When a measured disturbance adds at the plant input, the cancelling command is the negative of that disturbance. When that disturbance adds at the plant output and the plant DC gain \(P\) is finite and nonzero, the steady cancelling command is the negative of the disturbance divided by \(P\).",
                    r"Inverting a right-half-plane zero produces a right-half-plane pole. A stable feedforward block cannot include that pole.",
                    r"Reference feedforward is driven by the measured output, so it removes sensor noise before that noise reaches the controller.",
                ],
                3,
                r"Reference feedforward is driven by the reference, not by the measured output, so it does not see sensor noise on that measurement. A prefilter outside the loop leaves \(L\) and the margins unchanged. An input disturbance is cancelled by the opposite command. An output disturbance is cancelled in steady state by \(-d/P\) when \(P\) is finite and nonzero. Inverting a right-half-plane zero produces a right-half-plane pole, which a stable block cannot include.",
                reasons=[
                    r"Reference feedforward is driven by the reference, not by the measured output. Sensor noise on that measurement enters through the feedback path.",
                    r"Adding the reference into the command subtracts the sensor noise, so the feedforward path removes it.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "perf-specs-freq":
        return [
            ("perf-specs-freq-r1-q1", fresh(
                1, "order",
                r"Order the frequency-domain targets from closed-loop bandwidth to the high-frequency noise demand. Each step after the first uses the result of the step before it.",
                [
                    r"Closed-loop bandwidth is the lowest frequency where \(|T(j\omega)|\) has fallen to \(1/\sqrt{2}\) of its low-frequency value. It is a property of \(T\).",
                    r"Separate the bandwidth defined in the previous step from the gain crossover. The gain crossover is the frequency where \(|L|\) equals 1. That equality is not the definition of bandwidth.",
                    r"Move well below the gain crossover named in the previous step. For a unity-feedback loop, tracking and disturbance rejection want \(|L|\) large there, so that \(|S| = 1/|1+L|\) is small.",
                    r"Reverse the demand on \(|L|\) made in the previous step. Well above that same crossover, sensor noise passes through \(T\), so noise rejection wants \(|L|\) small there, which makes \(|T|\) small.",
                ],
                r"Bandwidth is a 3 dB drop in \(|T|\) relative to its low-frequency value. Gain crossover is where \(|L| = 1\), which is a different definition. Below crossover, a unity-feedback loop wants \(|L|\) large so that \(|S|\) is small. Above crossover, sensor noise passes through \(T\), so the loop wants \(|L|\) small. A larger allowed peak sensitivity permits the Nyquist curve to come closer to \(-1\).",
            )),
            ("perf-specs-freq-r2-q2", fresh(
                2, "sym",
                r"a is positive and less than \(\pi\). At the gain crossover, \(|L| = 1\) and the phase of \(L\) is \(-\pi + a\). Write the sensitivity magnitude there. Use a.",
                "1/(2*sin(a/2))",
                {"a": (0.25, 1.4)},
                r"At gain crossover, \(L = e^{j(-\pi+a)}\) when the phase margin is \(a\) radians and \(|L| = 1\). Then \(|1+L| = 2\sin(a/2)\) for \(a\) in \((0, \pi)\), so \(|S| = 1/(2\sin(a/2))\). This is the sensitivity at that one frequency, not automatically the peak over all frequencies. The reciprocal \(2\sin(a/2)\) is the distance from \(L\) to \(-1\), not \(|S|\).",
                alternates=["(2*sin(a/2))**(-1)", "1/(2*sin((1/2)*a))"],
            )),
            ("perf-specs-freq-r3-q1", fresh(
                3, "multi",
                r"Which statements about frequency-domain specifications are true? Select every correct statement.",
                [
                    r"Closed-loop bandwidth is the lowest frequency where \(|T|\) has fallen to \(1/\sqrt{2}\) of its low-frequency value. The frequency where \(|L| = 1\) is the gain crossover, which is a different definition.",
                    r"When the Nyquist curve of \(L\) does not pass through \(-1\), the peak sensitivity \(M_s\) equals the reciprocal of the smallest distance from that curve to \(-1\). A larger allowed \(M_s\) therefore permits the curve to come closer to \(-1\).",
                    r"For a unity-feedback loop, sensor-noise rejection wants \(|T|\) small at high frequency, and \(|T|\) small implies \(|L|\) small there.",
                    r"Raising the allowed peak sensitivity \(M_s\) forces the phase margin to be exactly \(\pi/2\) radians and cuts the bandwidth in half.",
                ],
                [0, 1, 2],
                r"Bandwidth is a drop in \(|T|\), not the frequency where \(|L| = 1\). Peak sensitivity is the reciprocal of the distance from the Nyquist curve to \(-1\), so a larger allowed peak permits a smaller distance. For unity feedback, \(L = T/(1-T)\), so a small \(|T|\) forces a small \(|L|\). The allowed peak does not fix the phase margin at \(\pi/2\) and does not set the bandwidth by itself.",
            )),
        ]
    raise SystemExit("no swaps for " + sid)


def assert_item(item):
    """Reject a symbolic box whose key is not finite and positive at every corner."""
    if item.get("type") != "symbolic":
        return
    import sympy as sp
    specs = item["variables"]
    names = [spec["name"] for spec in specs]
    for name in names:
        if re.search(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])", item["prompt"]) is None:
            raise SystemExit("prompt misses graded name " + name)
    local = {name: sp.Symbol(name) for name in names}
    local["exp"] = sp.exp
    local["sin"] = sp.sin
    local["e"] = sp.E
    local["pi"] = sp.pi
    expr = sp.parse_expr(item["answer"], local_dict=local)
    expr = expr.subs(sp.Symbol("pi"), sp.pi)
    used = {str(symbol) for symbol in expr.free_symbols}
    missing = [name for name in names if name not in used]
    if missing:
        raise SystemExit("answer misses " + ", ".join(missing))
    bounds = []
    for spec in specs:
        lo, hi = float(spec["min"]), float(spec["max"])
        if lo <= 0 or hi <= lo:
            raise SystemExit("nonpositive range for " + spec["name"])
        bounds.append((lo, hi))
    for corner in itertools.product(*bounds):
        value = complex(expr.subs(dict(zip(names, corner))).evalf())
        if abs(value.imag) > 1e-9 or not (value.real > 0) or value.real != value.real:
            raise SystemExit(f"corner {corner} gives {value} for {item['answer']}")
    for alt in item.get("alternates") or []:
        alt_expr = sp.parse_expr(alt, local_dict=local).subs(sp.Symbol("pi"), sp.pi)
        if sp.simplify(expr - alt_expr) != 0:
            raise SystemExit("alternate not equivalent: " + alt)


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
        original = json.load(f)
    data = json.loads(json.dumps(original))
    before = len(data["skills"])
    if len(data["skills"]) != len(set(data["skills"])):
        raise SystemExit("grandfather already has duplicate ids")
    drop = set(SKILLS)
    missing = sorted(drop - set(data["skills"]))
    if missing:
        raise SystemExit("not on the grandfather list: " + ", ".join(missing))
    data["skills"] = [sid for sid in data["skills"] if sid not in drop]
    if data["skills"]:
        raise SystemExit("grandfather not empty: " + ", ".join(data["skills"]))
    if len(data["skills"]) != len(set(data["skills"])):
        raise SystemExit("grandfather gained a duplicate")
    added = set(data["skills"]) - set(original["skills"])
    if added:
        raise SystemExit("grandfather gained ids: " + ", ".join(sorted(added)))
    with open(GRAND, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("grandfather", before, "->", len(data["skills"]))


def main():
    for sid in SKILLS:
        for _old, new in swaps_for(sid):
            assert_item(new)
    for sid in SKILLS:
        apply_skill(sid)
    drop_grandfather()


if __name__ == "__main__":
    main()
