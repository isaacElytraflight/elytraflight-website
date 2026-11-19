#!/usr/bin/env python3
"""SG-063 feedback and op-amps: swap the most pattern-matchable MC items.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The new questions use the same relations as the
explainers, and the explainer worked examples do not use these prompts.
The verifier does not import this file.

Symbolic ranges are closed boxes on which the key stays finite and keeps a
valid sign. No sampled point is a difference of two independent positives, so
a remainder cannot come out negative or pass through zero.
"""
import json
import os

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "opamp-models",
    "gbw",
    "inverting",
    "fb-impedance",
    "fb-amp-errors",
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
    if sid == "opamp-models":
        return [
            ("opamp-models-r1-q2", fresh(
                1, "order",
                r"Order how the voltage-controlled voltage source becomes the ideal op-amp, and what that forces once negative feedback holds the output finite. Each step after the first uses the result of the step before it.",
                [
                    r"Start from the controlled source: the output is \(A\) times the input difference, taken behind \(R_{out}\), with \(R_{in}\) across the two inputs.",
                    r"Send \(R_{in}\) to infinity: the current drawn from the source goes to zero at any finite input voltage.",
                    r"Send \(R_{out}\) to zero: none of that amplified voltage is then lost in the output resistance, so a load sees the full \(A\) times the input difference.",
                    r"Send \(A\) to infinity while negative feedback keeps the output finite: the input difference that the previous step multiplies has to go to zero, so the two inputs match.",
                ],
                r"Infinite input resistance is what stops the amplifier from loading its source, zero output resistance is what lets the load see the full amplified voltage, and infinite gain is what forces the input difference to zero once feedback holds the output finite. Taking \(A\) to 0 kills the amplifier. Taking \(R_{in}\) to 0 shorts the source. Taking \(R_{out}\) to infinity leaves the load with nothing. Infinite gain with no feedback does not equalize the inputs: the output runs to the rail instead. This limit has no frequency dependence; the controlled source is flat.",
            )),
            ("opamp-models-r2-q3", fresh(
                2, "sym",
                r"Write the unity-gain frequency of a single-pole OTA, the frequency where the open-loop magnitude crosses 1. \(R_x\) sets both the DC gain and the dominant pole, and it cancels in the product. Use Gm and Cx.",
                "Gm/Cx",
                # Gm > 0 and Cx > 0, so the quotient stays positive and at least 5e-4/4e-11.
                {"Gm": (5e-4, 5e-2), "Cx": (4e-12, 4e-11)},
                r"\(A_0 = G_m R_x\) and the dominant pole is \(1/(R_x C_x)\), so their product is \(\omega_u = G_m/C_x\). Raising \(R_x\) buys DC gain and gives up the same factor in bandwidth. \(G_m R_x\) is the DC gain, not this frequency. \(1/(R_x C_x)\) is the pole, far below \(\omega_u\). \(G_m C_x\) is not a frequency. Dropping \(R_x\) entirely, so the transconductor feeds only \(C_x\), leaves this same unity-gain frequency.",
                alternates=["Gm*Cx**(-1)", "1/(Cx/Gm)", "Gm*(1/Cx)"],
            )),
            ("opamp-models-r3-q1", fresh(
                3, "find_error",
                r"A worked solution describes an OTA whose transconductor feeds only \(C_x\), with no \(R_x\), followed by an ideal buffer. Exactly one step is wrong.",
                [
                    r"With no resistor, a DC current has nowhere to go but into \(C_x\).",
                    r"The node voltage is \(G_m v_d/(j\omega C_x)\), so the gain is \(G_m/(j\omega C_x)\).",
                    r"That gain is zero at DC and rises at 20 dB/decade, because a capacitor blocks DC current.",
                    r"The magnitude equals 1 at \(\omega_u = G_m/C_x\), the same unity-gain frequency the resistor would have set.",
                ],
                2,
                r"DC current into a capacitor integrates, so \(A(j\omega) = G_m/(j\omega C_x)\). The magnitude is infinite as \(\omega\) goes to 0 and falls at 20 dB/decade, crossing 1 at \(G_m/C_x\). Zero gain at DC is a high-pass zero, not this integrator. Removing \(R_x\) does not erase the frequency dependence, and it does not send \(\omega_u\) to infinity. The buffer that follows the node has a gain of 1; it does not set the slope.",
                reasons=[
                    r"The capacitor integrates DC current, so the gain is infinite at DC and falls at 20 dB/decade. Zero at DC is the high-pass case.",
                    r"Removing \(R_x\) removes the frequency dependence, so the gain is the constant \(G_m\).",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "gbw":
        return [
            ("gbw-r1-q2", fresh(
                1, "sym",
                r"Write the approximate closed-loop bandwidth of a single-pole op-amp loop with feedback factor \(f\) and unity-gain frequency \(\omega_u\). This is the estimate used when the DC loop gain is large. Use f and wu.",
                "f*wu",
                # f stays in (0, 1] and wu stays large, so the product cannot vanish or go negative.
                {"f": (0.05, 1.0), "wu": (1e5, 1e8)},
                r"On the open-loop slope, gain times frequency stays near \(\omega_u\). Feedback asks for a low-frequency gain of about \(1/f\), and the closed-loop curve holds that gain until the open-loop curve falls down to meet it, at about \(f\,\omega_u\). \(\omega_u/f\) turns the trade around and would give the highest gain the widest band. \(f\) times the open-loop pole is far too low: that pole sits near \(\omega_u/A_0\). \((1+T_0)\) times the open-loop pole is the exact move, and it matches \(f\,\omega_u\) only after \(T_0 = A_0 f\) is large enough to drop the 1. A follower is the case \(f = 1\), so its bandwidth is about \(\omega_u\).",
                alternates=["wu*f", "wu/(1/f)", "f*(wu)"],
            )),
            ("gbw-r2-q3", fresh(
                2, "order",
                r"Order why a unity-gain follower uses the whole gain-bandwidth of a single-pole op-amp. Each step after the first uses the result of the step before it.",
                [
                    r"Past its dominant pole the open-loop gain falls at 20 dB/decade and crosses 1 at the unity-gain frequency \(\omega_u\).",
                    r"A follower returns the entire output, so the feedback factor is 1 and the ideal closed-loop gain is 1.",
                    r"The closed-loop gain stays near that value of 1 until the falling open-loop curve meets it.",
                    r"The curves meet at \(\omega_u\), so the follower's bandwidth is about \(\omega_u\). A higher closed-loop gain would have met the open-loop curve sooner.",
                ],
                r"The follower has \(f = 1\), so it meets the open-loop curve where that curve crosses 1 and uses the whole gain-bandwidth. Half of \(\omega_u\) is the bandwidth of a loop whose feedback factor is \(1/2\), including an inverting gain of \(-1\), whose noise gain is 2. The open-loop pole is about \(\omega_u/A_0\), not the closed-loop bandwidth. A closed-loop gain of 1 does not delete the pole. Infinite bandwidth would require an infinite unity-gain frequency.",
            )),
            ("gbw-r3-q3", fresh(
                3, "find_error",
                r"A worked solution gives the gain-bandwidth of an OTA with no output buffer, driving a load capacitor \(C_L\) in parallel with its internal \(C_x\). Exactly one step is wrong.",
                [
                    r"Without a buffer, \(C_L\) sits on the same high-impedance node as \(C_x\).",
                    r"At DC the capacitor is a short circuit, so the load reduces the DC gain \(G_m R_x\).",
                    r"The pole frequency is \(1/(R_x(C_x+C_L))\).",
                    r"DC gain times that pole, the gain-bandwidth product, therefore falls from \(G_m/C_x\) to \(G_m/(C_x+C_L)\).",
                ],
                1,
                r"A capacitor is an open circuit at DC, so \(C_L\) does not change \(G_m R_x\). It does add to the capacitance that sets the pole, and the product of the unchanged DC gain and the new pole is \(G_m/(C_x+C_L)\). Calling the capacitor a short would collapse the bias point, which a capacitive load does not do. An ideal buffer holds \(C_L\) off that node and leaves the product at \(G_m/C_x\). Series capacitors, or a pole set by \(C_L\) alone, describe a different circuit.",
                reasons=[
                    r"A capacitor is open at DC, so \(C_L\) leaves \(G_m R_x\) alone and only lowers the gain-bandwidth product to \(G_m/(C_x+C_L)\).",
                    r"Any load capacitor reduces the DC gain, because it shunts \(R_x\) at every frequency including DC.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "inverting":
        return [
            ("inverting-r1-q1", fresh(
                1, "sym",
                r"Write the ideal closed-loop gain \(v_{out}/v_{in}\) of an inverting amplifier. The \(+\) input is grounded, the op-amp draws no input current, and the output is in its linear range. Use R1 and R2.",
                "-R2/R1",
                # Both resistances stay positive, so the gain stays strictly negative and the denominator cannot be 0.
                {"R1": (800, 3500), "R2": (400, 25000)},
                r"The \(+\) input is grounded, so the inverting node is a virtual ground. The input current \(v_{in}/R_1\) flows entirely through \(R_2\), and the output has to go negative to sink it, which gives \(-R_2/R_1\). The positive ratio \(R_2/R_1\) drops that sign. \(1+R_2/R_1\) is the non-inverting gain. \(-R_1/R_2\) puts the input resistor in the numerator. The divider ratio \(R_1/(R_1+R_2)\) is the feedback factor, not the gain. Finite open-loop gain multiplies this ideal result by \(T/(1+T)\), and that correction needs \(A\), which is not in this expression.",
                alternates=["-(R2/R1)", "(-1)*R2/R1", "-R2*R1**(-1)"],
            )),
            ("inverting-r1-q2", fresh(
                1, "order",
                r"Order why the inverting input of an ideal inverting amplifier sits at 0 V while the output is in its linear range. Each step after the first uses the result of the step before it.",
                [
                    r"The \(+\) input is connected to ground, so its voltage is 0.",
                    r"The output equals \(A\) times the difference of the two input voltages, and in the linear range that output stays finite.",
                    r"A finite output from an arbitrarily large \(A\) is possible only when that input difference shrinks toward 0.",
                    r"The inverting input is therefore held near 0 V. The current through \(R_1\) still flows on through \(R_2\), because the op-amp pin draws none.",
                ],
                r"\(v_{out} = A(V^{+} - V^{-})\) stays finite while \(A\) is huge only if the input difference vanishes. With the \(+\) input at ground, the inverting input sits at 0 V. It is not a wire to ground: a real ground would steal the input current and the gain formula would not hold. Equal resistors are not required. The ideal op-amp draws no input current; a large input current is the opposite model. The virtual ground fails if the output saturates, because the loop is then no longer keeping the difference at zero.",
            )),
            ("inverting-r3-q1", fresh(
                3, "find_error",
                r"A worked solution lists the closed-loop gains one ideal op-amp stage can realize, inverting or non-inverting. Exactly one step is wrong.",
                [
                    r"An inverting stage has gain \(-R_2/R_1\), so the gain is negative and its magnitude can sit above or below 1.",
                    r"A non-inverting stage has gain \(1+R_2/R_1\), which cannot fall below 1 with a passive divider.",
                    r"Setting \(R_2 = 0\) on that non-inverting stage leaves a follower, whose gain is \(+1\).",
                    r"A positive gain of \(0.5\) is then available from the same follower by setting the two resistors equal.",
                ],
                3,
                r"\(-R_2/R_1\) can be any negative number, including a magnitude below 1. \(1+R_2/R_1\) is at least 1: equal resistors give \(+2\), and \(R_2 = 0\) is a follower with gain \(+1\). A positive gain below 1, such as \(+0.5\), cannot come from one non-inverting stage. Setting the resistors equal does not halve the non-inverting gain. An inverting stage cannot produce a positive gain either. A positive attenuation needs another divider.",
                reasons=[
                    r"\(1+R_2/R_1\) never drops below 1. Equal resistors give \(+2\), and \(R_2 = 0\) gives \(+1\). A gain of \(+0.5\) needs another divider.",
                    r"Equal resistors on a non-inverting stage set the gain to \(1/2\), the resistor ratio.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "fb-impedance":
        return [
            ("fb-impedance-r1-q1", fresh(
                1, "sym",
                r"Write the closed-loop output impedance of a voltage-feedback amplifier. The loop senses the output voltage and fights a load-induced change. Use Rout, A, and f.",
                "Rout/(1+A*f)",
                # Rout, A, and f stay positive with A*f at least 4, so the denominator is at least 5 and the result stays positive.
                {"Rout": (10, 200), "A": (40, 500), "f": (0.1, 1.0)},
                r"Voltage feedback senses the output voltage and corrects it, so the closed-loop output impedance is \(R_{out}/(1+A f)\). Multiplying \(R_{out}\) by \(1+A f\) is the series-output result, the rise you get when the loop senses current instead. \(R_{out}/(1+A)\) drops the feedback factor and is right only for unity feedback. \(R_{out}/(A f)\) is the large-loop-gain estimate, missing the 1 that matters when \(A f\) is modest. \(R_{in}(1+A f)\) is the series-input impedance, the other port. The inverting amplifier's source resistance is not this output formula.",
                alternates=["Rout/(1+f*A)", "Rout/(A*f+1)", "Rout*(1+A*f)**(-1)"],
            )),
            ("fb-impedance-r2-q3", fresh(
                2, "order",
                r"Order why series mixing at the input raises the impedance a source sees. Each step after the first uses the result of the step before it.",
                [
                    r"Negative feedback sets the output near \(A/(1+A f)\) times the source voltage \(v_x\).",
                    r"The feedback network returns \(f\) times that output, which sits close to \(v_x\) when \(A f\) is large.",
                    r"The op-amp's own input resistance then has only the error \(v_x - f v_{out}\) across it, about \(v_x/(1+A f)\).",
                    r"The source current is that small voltage divided by \(R_{in}\), so the impedance the source sees is \(R_{in}(1+A f)\).",
                ],
                r"The source still applies \(v_x\). Feedback lifts the other side of \(R_{in}\) nearly to \(v_x\), so the resistor sees only about \(v_x/(1+A f)\) and the current is smaller by that factor. The impedance is \(R_{in}(1+A f)\). The feedback resistors are not stacked in series with the source, and \(R_{in}\) does not change as a component. Shunt mixing, as in the inverting amplifier, does the opposite: the input node is held still and the source sees a low impedance. Dividing \(R_{in}\) by \(1+A f\) is that shunt result, not this series one.",
            )),
            ("fb-impedance-r3-q3", fresh(
                3, "find_error",
                r"A worked solution gives the resistance a source sees at the input of an inverting amplifier. Exactly one step is wrong.",
                [
                    r"Series mixing multiplies the op-amp's own input resistance by \(1+T\).",
                    r"The inverting amplifier returns feedback current to the input node, a shunt connection, and the loop holds that node near 0 V.",
                    r"The source therefore sees about \(R_{in}(1+T)\), the same boost the non-inverting amplifier gets.",
                    r"What the source actually sees is \(R_1\) into that virtual ground. The \(1+T\) boost belongs to series mixing, not to this shunt input.",
                ],
                2,
                r"Series mixing multiplies an impedance by \(1+T\); shunt mixing divides it. The inverting input is a shunt: feedback current and source current meet at one node, and the loop holds that node near 0 V. The source sees \(R_1\) into the virtual ground, not \(R_{in}(1+T)\). \(R_1+R_2\) would be the series sum only if the node were free. The op-amp's own \(R_{in}\) sits across the inputs and, with the summing node already near 0 V, does not set the source resistance. The non-inverting amplifier is the circuit that receives the \(1+T\) boost.",
                reasons=[
                    r"Shunt mixing holds the summing node near 0 V, so the source sees \(R_1\). The \(1+T\) boost is the series-mixing result.",
                    r"Every feedback loop raises input resistance by \(1+T\), and the inverting stage is no exception.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "fb-amp-errors":
        return [
            ("fb-amp-errors-r2-q3", fresh(
                2, "sym",
                r"Write the exact fraction of its ideal gain that a feedback amplifier misses, when the open-loop gain is \(a\) and the feedback factor is \(f\). The loop gain is the product \(a f\). Use a and f.",
                "1/(1+a*f)",
                # a*f stays between 5 and 100, so the miss stays between about 0.01 and 1/6. Never negative, never near 0 or 1.
                {"a": (100, 400), "f": (0.05, 0.25)},
                r"The actual gain is the ideal gain times \(T/(1+T)\), with \(T = a f\), so the missing fraction is \(1/(1+a f)\). \(1/(a f)\) is the large-\(T\) estimate, slightly larger than the exact miss, and the two are not equal. \(a f\) itself is the loop gain, not the error. \(a/(1+a f)\) is the noninverting closed-loop gain, ideal value times \(T/(1+T)\), not the fraction that is missing. A follower, \(f = 1\), has the smallest miss this op-amp can have, because it returns the whole output. Resistor tolerance in the feedback network is not in this expression: that error sits in the ideal gain, and the loop does not divide it by \(1+T\).",
                alternates=["1/(1+f*a)", "(1+a*f)**(-1)", "1/(a*f+1)"],
            )),
            ("fb-amp-errors-r1-q2", fresh(
                1, "order",
                r"Order why a larger ideal noninverting gain has a larger static gain error on the same op-amp. Each step after the first uses the result of the step before it.",
                [
                    r"The ideal noninverting gain is \(1/f\), so asking for more gain means a smaller feedback factor.",
                    r"Loop gain is the product \(T = a f\), so the smaller \(f\) cuts \(T\) even though \(a\) is the same op-amp.",
                    r"The fraction of the ideal gain that is missing is exactly \(1/(1+T)\).",
                    r"The high-gain stage therefore misses by more. Returning a larger share of the output would have raised \(T\) and shrunk that fraction.",
                ],
                r"Ideal gain \(1/f\) and loop gain \(T = a f\) move in opposite directions, and the miss is \(1/(1+T)\). The stage that returns less of its output has the larger error. The same open-loop gain does not mean the same error. More feedback reduces the miss; it does not increase it. \(T \approx 1\) only about halves the miss. Quoting \(a\) alone, without \(f\), skips the quantity that actually differs between a low-gain stage and a high-gain stage.",
            )),
            ("fb-amp-errors-r3-q3", fresh(
                3, "find_error",
                r"A worked solution compares magnitude and phase errors of a single-pole closed-loop response at one tenth of its pole frequency \(f_c\). Exactly one step is wrong.",
                [
                    r"At \(f = f_c/10\) the closed-loop factor is \(1/(1+j0.1)\).",
                    r"The magnitude of that factor is about 10% low, because each error simply tracks \(f/f_c\).",
                    r"The phase is \(-\arctan(0.1)\), about \(-5.7\) degrees.",
                    r"Magnitude error grows with the square of \(f/f_c\), so it is only about half a percent here, while the phase has already moved by several degrees.",
                ],
                1,
                r"\(1/(1+j0.1)\) has magnitude \(1/\sqrt{1.01} \approx 0.995\), about half a percent low, and phase \(-\arctan(0.1) \approx -5.7^\circ\). The 10% figure is the frequency ratio \(f/f_c\), not either error. Magnitude error grows as \((f/f_c)^2\) and phase error nearly as \(f/f_c\), so a timing-sensitive loop feels the phase first. The two errors are not both 10%, and the phase is not exact. At the pole itself the magnitude is 3 dB down and the phase is \(-45^\circ\); a tenth of the way there is still close to the low-frequency gain.",
                reasons=[
                    r"The magnitude is \(1/\sqrt{1.01}\), about 0.5% low. The 10% figure is \(f/f_c\), not the magnitude error.",
                    r"At a tenth of the pole, magnitude and phase are both off by about 10%, since each tracks \(f/f_c\).",
                ],
                correct_reason=0,
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
        if rnd == 4:
            raise SystemExit(old_id + " is round 4; copy its preview onto the replacement")
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
