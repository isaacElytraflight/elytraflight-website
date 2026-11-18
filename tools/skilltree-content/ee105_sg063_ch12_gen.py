#!/usr/bin/env python3
"""SG-063 single-stage amplifiers: swap the most pattern-matchable MC items.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The new questions use the same relations as the
explainers, and the explainer worked examples do not use these prompts.
The verifier does not import this file.
"""
import json
import os

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = ["two-port", "bias-coupling", "cs-analysis", "cg", "cd", "amp-choice"]


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
    if sid == "two-port":
        return [
            ("two-port-r2-q2", fresh(
                2, "sym",
                r"Write the open-circuit voltage gain of a transconductance two-port. The controlled current is \(G_m v_{in}\) drawn out of the output node. Use Gm and Rout.",
                "-Gm*Rout",
                {"Gm": (0.2, 40), "Rout": (0.5, 80)},
                r"With the load open, the whole controlled current flows through \(R_{out}\), and the sign is negative because that current leaves the output node. The open-circuit voltage gain is \(-G_m R_{out}\). \(G_m/R_{out}\) divides where it should multiply. \(-G_m\) has dropped the resistance, so it is not a voltage gain. \(G_m R_{in}\) uses the input resistance, which does not set the open-circuit output.",
                alternates=["-(Gm*Rout)", "(-1)*Gm*Rout"],
            )),
            ("two-port-r1-q1", fresh(
                1, "order",
                r"Order the resistance test that finds a two-port's output resistance. Each step after the first uses the result of the step before it.",
                [
                    r"Switch off the independent source at the input, and leave the resistance that belonged to that source in place.",
                    r"Dependent sources stay in the circuit, because they still respond once a test source is applied.",
                    r"Drive the output port with a test source and record the current that test source delivers.",
                    r"Divide the test voltage by that current. The quotient is the output resistance.",
                ],
                r"An impedance test kills independent sources and keeps dependent ones. The source resistance stays, because it still affects internal controlling voltages. Dividing the open-circuit output by the input current is a gain, not this resistance. Shorting the output and reading the input current measures neither port. Leaving the input source running mixes a signal into the test.",
            )),
            ("two-port-r3-q2", fresh(
                3, "find_error",
                r"A worked solution says how a stage's output resistance should compare with the next stage's input resistance when the goal is voltage gain. Exactly one step is wrong.",
                [
                    r"The first stage's output resistance and the next stage's input resistance form a divider.",
                    r"The fraction of the open-circuit voltage that arrives at the next input is the next input resistance divided by the sum of those two resistances.",
                    r"That fraction is nearly one when the first output resistance is much smaller than the next input resistance.",
                    r"Setting the two resistances equal is better, because the most power transferred is the same goal as the most voltage gain.",
                ],
                3,
                r"The divider is \(R_{in}/(R_{out}+R_{in})\). Equal resistances hand over half the voltage and do maximize power. Voltage gain wants \(R_{out}\) much smaller than the next \(R_{in}\), so almost all of the voltage arrives. A much larger output resistance does the opposite. The comparison is not optional.",
                reasons=[
                    r"Equal resistances maximize power. Voltage gain wants the output resistance much smaller than the next input resistance.",
                    r"The two resistances cancel, so their ratio does not change the voltage that arrives.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "bias-coupling":
        return [
            ("bias-coupling-r1-q2", fresh(
                1, "sym",
                r"Write the magnitude of a coupling capacitor's impedance. Use omega for the radian frequency and C for the capacitance.",
                "1/(omega*C)",
                {"omega": (1e3, 1e7), "C": (1e-11, 1e-7)},
                r"The impedance is \(1/(j\omega C)\), so its magnitude is \(1/(\omega C)\). At DC the magnitude is infinite and the bias points stay apart. At a high signal frequency the magnitude is small and the signal passes. A short at DC would tie the bias points together. A resistor would pass DC. An open circuit at every frequency would block the signal along with the bias.",
                alternates=["(omega*C)**(-1)", "1/omega/C"],
            )),
            ("bias-coupling-r2-q3", fresh(
                2, "order",
                r"Order what a large capacitor placed across a source resistor does, from DC up to the signal frequency. Each step after the first uses the result of the step before it.",
                [
                    r"At DC the capacitor is an open circuit, so none of the bias current flows in it.",
                    r"The source resistor still carries that bias current, and it still sets the DC source voltage.",
                    r"At the signal frequency the same capacitor is nearly a short circuit.",
                    r"The source node is then at signal ground, so the signal does not see the source resistor, while the drain still receives the transistor's signal current.",
                ],
                r"A bypass capacitor is open for bias and a short for the signal. Taking the resistor out of the bias would move the operating point. The capacitor does not lift the DC source voltage, and it does not stop the signal current from reaching the drain.",
            )),
            ("bias-coupling-r1-q1", fresh(
                1, "find_error",
                r"A worked solution joins a drain biased at \(1.0\ \mathrm{V}\) straight to a gate that was designed for \(0.7\ \mathrm{V}\). Exactly one step is wrong.",
                [
                    r"The first drain is held at \(1.0\ \mathrm{V}\), and the second gate was designed to sit at \(0.7\ \mathrm{V}\).",
                    r"A direct wire connects the drain to the gate, so the two nodes must share one DC voltage.",
                    r"The shared voltage is \(1.0\ \mathrm{V}\), the voltage the first stage already holds at its drain.",
                    r"The second stage still runs at its designed overdrive, because a wire leaves every stage's bias independent.",
                ],
                3,
                r"Direct coupling makes the bias points depend on each other. The wire puts \(1.0\ \mathrm{V}\) on a gate designed for \(0.7\ \mathrm{V}\), so the second device runs at a larger overdrive than intended. The wire does carry the signal. It does not set the first stage's gain to zero, and it does not add a separate noise source. The harm is the shared DC level.",
                reasons=[
                    r"The wire sets the second gate to \(1.0\ \mathrm{V}\), so that stage's bias is no longer the \(0.7\ \mathrm{V}\) it was designed for.",
                    r"A wire cannot pass a signal, so the second stage simply receives nothing.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "cs-analysis":
        return [
            ("cs-analysis-r3-q1", fresh(
                3, "sym",
                r"Write the magnitude of a resistor-loaded common-source gain when the drain resistor is much smaller than \(r_o\). Use VRD for the DC drop across that resistor and Vov for the overdrive.",
                "2*VRD/Vov",
                {"VRD": (0.05, 2.5), "Vov": (0.08, 0.6)},
                r"\(g_m = 2I_D/V_{ov}\) and the drop is \(V_{RD} = I_D R_D\), so \(g_m R_D = 2V_{RD}/V_{ov}\). Using \(V_{RD}/V_{ov}\) leaves out the 2 from the square-law slope. \(2V_{ov}/V_{RD}\) inverts the ratio, so a larger drop would look like less gain. A supply divided by a thermal voltage is not this resistor-loaded gain.",
                alternates=["2*(VRD/Vov)", "(2*VRD)/Vov"],
            )),
            ("cs-analysis-r2-q2", fresh(
                2, "order",
                r"Order what happens to the gain when the drain resistor is doubled, the bias current stays fixed, the device stays saturated, and the resistor remains much smaller than \(r_o\). Each step after the first uses the result of the step before it.",
                [
                    r"The bias current is fixed, so \(g_m = 2I_D/V_{ov}\) stays fixed.",
                    r"With the drain resistor much smaller than \(r_o\), the gain magnitude is \(g_m R_D\).",
                    r"Doubling the resistor doubles that product, because \(g_m\) did not change.",
                    r"The device is still saturated, so the same small-signal result still applies and the gain magnitude roughly doubles.",
                ],
                r"While \(R_D \ll r_o\), the gain magnitude tracks \(R_D\). It does not stay put just because \(g_m\) is constant, and it does not halve. A factor of \(\sqrt{2}\) is what a fixed-size device does when its current changes, which is not this change. The DC drop across the resistor doubles too, so the headroom shrinks even as the gain rises.",
            )),
            ("cs-analysis-r1-q2", fresh(
                1, "find_error",
                r"A worked solution states the low-frequency port resistances of a common-source stage. Exactly one step is wrong.",
                [
                    r"At low frequency the gate draws no signal current.",
                    r"The input resistance is therefore infinite.",
                    r"With the input held at zero the controlled source is off, and the drain node is left with \(r_o\) in parallel with \(R_D\).",
                    r"The output resistance is \(1/g_m\), because every port of a MOSFET has that resistance.",
                ],
                3,
                r"The insulated gate takes no current, so \(R_{in}\) is infinite at low frequency. With \(v_{in} = 0\) the controlled source is dead and only \(r_o\) and \(R_D\) remain, so \(R_{out} = r_o\parallel R_D\). \(1/g_m\) is the resistance at a common-gate source, not at this drain. \(R_D\) is not the input resistance, and \(r_o\) alone is not the input either.",
                reasons=[
                    r"The output resistance is \(r_o\) in parallel with \(R_D\). \(1/g_m\) is the common-gate input, not this drain resistance.",
                    r"The gate current is zero, so the output resistance is infinite as well.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "cg":
        return [
            ("cg-r3-q3", fresh(
                3, "sym",
                r"Write the input resistance at the source of a common-gate stage whose body is grounded, with \(r_o\) very large. Use gm and gmb.",
                "1/(gm+gmb)",
                {"gm": (0.3, 30), "gmb": (0.05, 8)},
                r"A voltage at the source appears as \(-v_{gs}\) and, with the body grounded, as \(-v_{bs}\). Both controlled sources conduct, so the conductance is \(g_m+g_{mb}\) and the resistance is \(1/(g_m+g_{mb})\). Subtracting \(g_{mb}\) would raise the resistance. Grounding the gate does not turn the body source off, and the resistance does not become infinite.",
                alternates=["(gm+gmb)**(-1)", "(gmb+gm)**(-1)"],
            )),
            ("cg-r3-q2", fresh(
                3, "order",
                r"Order why a common-gate input resistance is low when the body effect is left out. Each step after the first uses the result of the step before it.",
                [
                    r"The gate is an AC ground, so a voltage \(v\) applied at the source appears entirely as \(v_{gs} = -v\).",
                    r"The controlled source then draws \(g_m v\) out of the source node.",
                    r"The current that must be supplied to the source, per volt of \(v\), is therefore \(g_m\).",
                    r"The input resistance is the reciprocal of that conductance, about \(1/g_m\).",
                ],
                r"The device itself is a conductance \(g_m\) from the source to signal ground. The drain resistor is not in series with this input, and the bias source is not what makes the resistance small. An open gate is a high resistance, which is the common-source input, not this one.",
            )),
            ("cg-r2-q2", fresh(
                2, "find_error",
                r"A worked solution gives the short-circuit current gain of a common-gate stage. Exactly one step is wrong.",
                [
                    r"Signal current driven into the source has to leave through one of the other terminals.",
                    r"The gate oxide takes none of that signal current.",
                    r"The current that entered the source therefore leaves through the drain.",
                    r"The short-circuit ratio of drain current to source current is \(g_m r_o\).",
                ],
                3,
                r"The current into the source leaves through the drain, so the short-circuit current gain is about 1. \(g_m r_o\) is the intrinsic voltage gain with the drain left open, not this current ratio. \(-g_m R_D\) is a voltage gain. A ratio near 0 would mean the current never reached the drain. The stage is a current buffer: low input resistance, high output resistance.",
                reasons=[
                    r"Drain current equals source current, so the short-circuit current gain is about 1. \(g_m r_o\) is an open-drain voltage gain.",
                    r"The gate takes the input current, so the current gain is about 0.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "cd":
        return [
            ("cd-r2-q2", fresh(
                2, "sym",
                r"Write the small-signal output resistance of a source follower whose body is grounded. Ignore \(r_o\) and the bias-source resistance. Use gm and gmb.",
                "1/(gm+gmb)",
                {"gm": (0.4, 25), "gmb": (0.04, 6)},
                r"A test voltage at the source drives both \(v_{gs}\) and \(v_{bs}\) to the negative of that voltage, so the gate source and the body source both conduct. The resistance seen there is \(1/(g_m+g_{mb})\). Using only \(1/g_m\) drops the body source. Subtracting \(g_{mb}\) moves the resistance the wrong way. \(1/g_{mb}\) would require the gate source to be absent.",
                alternates=["(gm+gmb)**(-1)", "1/(gmb+gm)"],
            )),
            ("cd-r1-q2", fresh(
                1, "order",
                r"Order the properties that make a source follower a voltage buffer. Each step after the first uses the result of the step before it.",
                [
                    r"The signal enters at the gate, and that gate draws no low-frequency current, so the input resistance is very high.",
                    r"The output is taken at the source, and the source voltage moves in the same direction as the gate.",
                    r"That motion is a gain just under 1, rather than a large inverting gain.",
                    r"Looking back into the source, the device presents a small resistance, so the stage can drive a load that a high-resistance drain could not.",
                ],
                r"The follower copies the gate onto a low-resistance source. It is not a high-gain inverter, and it is not a current buffer, which would have a low input resistance. It is not a differential pair. The low output resistance is what lets it drive a small load without throwing away the preceding stage's gain.",
            )),
            ("cd-r3-q2", fresh(
                3, "find_error",
                r"A worked solution states the DC relationship of a source follower. Exactly one step is wrong.",
                [
                    r"The bias current leaving the source is set by the current source under the follower.",
                    r"That current fixes the gate-source voltage of the device.",
                    r"The source terminal therefore sits one \(V_{GS}\) below the gate.",
                    r"The DC output equals the DC input, because a follower's gain is exactly 1.",
                ],
                3,
                r"The bias current sets \(V_{GS}\), and the source sits that far below the gate. A small-signal gain near 1 does not cancel the shift. The output is not one threshold above the input, and it is not stuck at half the supply. The shift is useful between stages and expensive in headroom.",
                reasons=[
                    r"A small-signal gain near 1 does not remove the DC shift. The output sits one \(V_{GS}\) below the input.",
                    r"The output sits one threshold above the input, because the body effect adds a threshold.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "amp-choice":
        return [
            ("amp-choice-r3-q2", fresh(
                3, "sym",
                r"Write the transconductance that makes a common-gate input resistance equal a required match resistance. Ignore \(r_o\) and the body effect. Use Rmatch for that resistance.",
                "1/Rmatch",
                {"Rmatch": (10, 500)},
                r"With the body effect left out and \(r_o\) large, the common-gate input resistance is \(1/g_m\), so the match is \(g_m = 1/R_{match}\). A large drain resistor does not set this input resistance. A follower's low resistance is at its output, not its input. Setting the output resistance equal to the match terminates the wrong port. A gate input is a capacitance here, not a resistive match.",
                alternates=["Rmatch**(-1)", "1/(Rmatch)"],
            )),
            ("amp-choice-r1-q1", fresh(
                1, "order",
                r"Order the choice of one stage for a sensor whose output resistance is \(100\ \mathrm{k\Omega}\) when the required voltage gain is about 20. Each step after the first uses the result of the step before it.",
                [
                    r"The source resistance is high, so the stage's input resistance has to be high or the input divider throws the signal away.",
                    r"A gate input has that high resistance, while a common-gate input near \(1/g_m\) would load this sensor.",
                    r"The required gain is about 20, and a source follower has a gain below 1, so a follower cannot be the whole amplifier.",
                    r"A common-source stage keeps the high input resistance and supplies the voltage gain.",
                ],
                r"A common-gate input would divide a \(100\ \mathrm{k\Omega}\) source down to almost nothing. A follower keeps the sensor voltage and then misses the gain. One transistor stage can do the job. The limit is the port resistances, not a rule against amplifying from a high source resistance.",
            )),
            ("amp-choice-r2-q2", fresh(
                2, "find_error",
                r"A worked solution names the stage whose input resistance is about \(1/g_m\), whose output resistance is about \(R_D\), and whose gain is the positive quantity \(g_m R_D\). Exactly one step is wrong.",
                [
                    r"An input resistance near \(1/g_m\) means the signal enters a source, not a gate.",
                    r"An output resistance near \(R_D\) means the output is a drain with a drain resistor.",
                    r"A positive \(g_m R_D\) means the drain voltage rises when the source voltage rises.",
                    r"Those three facts describe a common-source stage.",
                ],
                3,
                r"A common-source stage has an infinite input resistance and a negative gain. The low input resistance, the drain load, and the positive \(g_m R_D\) belong to the common-gate stage. A follower has a gain below 1 and an output resistance near \(1/(g_m+g_{mb})\), not \(R_D\). A cascode current source is a bias element, not this voltage amplifier.",
                reasons=[
                    r"A common-source stage has infinite input resistance and a negative gain. This signature is the common-gate stage.",
                    r"The same three facts describe a source follower, whose output resistance is near \(1/g_m\).",
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
