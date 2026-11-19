#!/usr/bin/env python3
"""SG-063 differential amplifiers: swap the most pattern-matchable MC items.

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

SKILLS = [
    "diff-intro",
    "diff-dc",
    "half-circuit",
    "cmrr",
    "mirror-load",
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
    if sid == "diff-intro":
        return [
            ("diff-intro-r1-q2", fresh(
                1, "order",
                r"Order how a source-coupled pair is put together, and what that wiring does to the currents. Each step after the first uses the result of the step before it.",
                [
                    r"Start with two matched transistors.",
                    r"Tie their sources to one current source, so the drain currents are forced to sum to \(I_{SS}\).",
                    r"Return each drain to the supply through its own load, so that device's current becomes its own drain voltage.",
                    r"Use the two gates as the inputs: they only steer the fixed sum, and a pure common-mode move leaves both currents, and both drain voltages, unchanged.",
                ],
                r"One shared tail is what makes the pair a pair. Two devices in series between the rails are a stack, not a current splitter. Separate source resistors to ground are two independent common-source stages, and each can change its current on its own. The gates steer the split; they do not set the sum, and with an ideal tail they draw no signal current.",
            )),
            ("diff-intro-r1-q1", fresh(
                1, "find_error",
                r"A worked solution says what an ideal-tail pair does with a disturbance that lands equally on both inputs. Exactly one step is wrong.",
                [
                    r"Supply ripple, ground bounce, and coupled noise tend to move both inputs by the same amount.",
                    r"With a fixed tail and matched devices, that shared move cannot change either drain current.",
                    r"Each drain voltage therefore shifts by \(g_m R_D\) times the common-mode input.",
                    r"The quantity the next stage should use is the difference of the two drain voltages, which stays put when the two currents do.",
                ],
                2,
                r"Equal inputs leave the split where it was, so neither drain current changes and neither drain voltage moves. Multiplying the common-mode input by \(g_m R_D\) is the differential gain, applied to a signal the tail has already rejected. Taking one drain instead of the difference does not create that gain when both drains are still. Two separate common-source stages would each amplify the disturbance; the shared tail is what stops them.",
                reasons=[
                    r"The currents do not change, so the drains do not move. Applying \(g_m R_D\) to the common-mode input is the mistake.",
                    r"Common-mode rejection requires the tail current to double, so both drains fall together.",
                ],
                correct_reason=0,
            )),
            ("diff-intro-r2-q3", fresh(
                2, "sym",
                r"An ideal tail carries \(I_{SS}\), and M1's drain current is \(I_{D1}\). Write M2's drain current. Use ISS and ID1.",
                "ISS-ID1",
                {"ISS": (1e-3, 2e-3), "ID1": (2e-5, 5e-4)},
                r"The tail fixes the sum, so \(I_{D2} = I_{SS} - I_{D1}\). A rise in one current is an equal fall in the other. \(I_{SS}/2\) is only the balance value, not the current at an arbitrary split. \(I_{D1} + I_{SS}\) would make the sum larger than the tail. \(2I_{SS} - I_{D1}\) leaves M2 carrying more than \(I_{SS}\) whenever M1 carries a positive current. With the tail ideal, a common-mode input does not appear in this relation.",
                alternates=["-ID1+ISS", "ISS+(-1)*ID1"],
            )),
        ]
    if sid == "diff-dc":
        return [
            ("diff-dc-r2-q2", fresh(
                2, "sym",
                r"At balance each device of a source-coupled pair carries half the tail current \(I_{SS}\), at overdrive \(V_{ov}\). Write that device's \(g_m\). Use ISS and Vov.",
                "ISS/Vov",
                {"ISS": (1e-4, 2e-3), "Vov": (0.08, 0.5)},
                r"A MOSFET at current \(I_D\) has \(g_m = 2I_D/V_{ov}\). Here \(I_D = I_{SS}/2\), so \(g_m = I_{SS}/V_{ov}\). That is also the slope of \(I_{D1}-I_{D2}\) versus \(v_{id}\) at balance. \(I_{SS}/(2V_{ov})\) treats the whole tail as one device's current and then halves the result a second time. \(2I_{SS}/V_{ov}\) forgets the split and doubles \(g_m\). The square-law form \(\sqrt{k I_{SS}}\) equals this only after \(V_{ov}\) is substituted; it is not an expression in \(I_{SS}\) and \(V_{ov}\). The slope holds near balance, not out at the steering limit.",
                alternates=["(ISS/2)/(Vov/2)", "(2*(ISS/2))/Vov"],
            )),
            ("diff-dc-r1-q2", fresh(
                1, "order",
                r"Order the large-signal curve of \(I_{D1}-I_{D2}\) as \(|v_{id}|\) grows from zero. Each step after the first uses the result of the step before it.",
                [
                    r"At \(v_{id} = 0\) the devices share \(I_{SS}\) equally, so the current difference is zero.",
                    r"Near that point the difference rises with slope \(g_m = I_{SS}/V_{ov}\).",
                    r"Farther out the square law bends the curve, and the slope falls below that small-signal value.",
                    r"At \(|v_{id}| = \sqrt{2}\,V_{ov}\) one device cuts off, and the difference stops at \(\pm I_{SS}\).",
                ],
                r"The tail caps the difference at \(I_{SS}\). A straight line for every input ignores the cutoff. An exponential transfer is the bipolar pair, not this square-law pair. A parabola with a minimum at zero would fall and then rise. Past cutoff the winning device already has the whole tail, so more input difference does not raise its current.",
            )),
            ("diff-dc-r3-q1", fresh(
                3, "find_error",
                r"A worked solution narrows both devices of a pair while keeping \(I_{SS}\) fixed, so \(V_{ov}\) rises. Exactly one step is wrong.",
                [
                    r"Each device still carries \(I_{SS}/2\) at balance, because the tail current did not change.",
                    r"A narrower device needs a larger overdrive to carry that same current.",
                    r"Since \(g_m = I_{SS}/V_{ov}\), the larger overdrive raises \(g_m\).",
                    r"Full steering still occurs at \(|v_{id}| = \sqrt{2}\,V_{ov}\), so that input range gets wider.",
                ],
                2,
                r"\(g_m = I_{SS}/V_{ov}\) falls when \(V_{ov}\) rises. The wider steering range and the smaller transconductance are the same trade. Narrowing the devices does not raise both. The balance current stays \(I_{SS}/2\) only because the tail was held fixed; changing \(I_{SS}\) would move \(g_m\) the other way. The linear slope does not remain valid out to the new cutoff.",
                reasons=[
                    r"\(g_m = I_{SS}/V_{ov}\) falls as the overdrive rises. The range widens and the gain drops.",
                    r"A larger overdrive always means more transconductance, so both the range and \(g_m\) increase.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "half-circuit":
        return [
            ("half-circuit-r1-q3", fresh(
                1, "sym",
                r"Write the common-mode gain from \(v_{CM}\) to one drain of a symmetric resistor-loaded pair. Each common-mode half is a common-source stage degenerated by \(2R_{SS}\). Use gm, RD, and RSS.",
                "-gm*RD/(1+2*gm*RSS)",
                {"gm": (2e-4, 2e-2), "RD": (200, 5e4), "RSS": (1e3, 5e5)},
                r"Both halves push current into the same tail, so each half sees \(2R_{SS}\). The gain of that degenerated stage is \(-g_m R_D/(1+2g_m R_{SS})\). Dropping the 1 is the estimate \(-R_D/(2R_{SS})\), which is not this exact gain. Using \(R_{SS}\) instead of \(2R_{SS}\) forgets that the two sides share the tail. The differential half circuit grounds the source, so its gain \(g_m R_D\) has no \(R_{SS}\) in it. A positive sign would be a follower, and this half is still a common-source stage.",
                alternates=[
                    "-RD/(1/gm+2*RSS)",
                    "-(gm*RD)/(1+2*gm*RSS)",
                    "-gm*RD/(2*gm*RSS+1)",
                ],
            )),
            ("half-circuit-r1-q2", fresh(
                1, "order",
                r"Order why the shared source is an AC ground in the differential half circuit of a symmetric pair. Each step after the first uses the result of the step before it.",
                [
                    r"A pure differential input raises one gate by \(v_{DM}/2\) and lowers the other by the same amount.",
                    r"The two devices therefore carry signal currents of equal size and opposite sign.",
                    r"Those currents cancel at the shared source, so none of the signal current flows in the tail resistance.",
                    r"The source voltage does not move, and each half is a grounded-source stage whose gain does not contain \(R_{SS}\).",
                ],
                r"Equal and opposite currents leave the tail node still, which is why it is an AC ground and why \(R_{SS}\) is absent from the differential gain. An open circuit at that node would describe a missing tail, not a fixed voltage. Putting \(2R_{SS}\) in this half is the common-mode construction. The drain loads are not what holds the source still.",
            )),
            ("half-circuit-r2-q3", fresh(
                2, "find_error",
                r"A worked solution applies half circuits to a pair whose two drain loads differ. Exactly one step is wrong.",
                [
                    r"With equal loads, a differential drive and a common-mode drive can be solved on two separate half circuits and added.",
                    r"The differential half places an AC ground at the tail node.",
                    r"The common-mode half places \(2R_{SS}\) in the source of each side.",
                    r"Unequal drain loads do not disturb that split, so the same two half circuits still give each output.",
                ],
                3,
                r"Half circuits need the two sides to be mirror images. Different loads turn part of a common-mode input into a differential output, so the modes no longer separate and the full circuit has to be solved. An ideal tail does not restore the symmetry the loads broke. The differential and common-mode definitions of the inputs are still valid; what fails is solving them on two independent halves.",
                reasons=[
                    r"Unequal loads convert common mode into a differential output, so the two half circuits no longer separate.",
                    r"Half circuits fail only for an ideal tail. Load mismatch does not couple the modes.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "cmrr":
        return [
            ("cmrr-r1-q1", fresh(
                1, "sym",
                r"Write the single-ended CMRR of a symmetric resistor-loaded pair, the ratio of the one-output differential gain to the magnitude of the common-mode gain. \(R_D\) cancels. Use gm and RSS.",
                "(1+2*gm*RSS)/2",
                {"gm": (2e-4, 2e-2), "RSS": (1e3, 5e5)},
                r"The one-output differential gain has magnitude \(g_m R_D/2\), and the common-mode gain has magnitude \(g_m R_D/(1+2g_m R_{SS})\). Dividing them leaves \((1+2g_m R_{SS})/2\). Inverting the ratio gives \(|A_{CM}/A_{DM}|\). Using the drain-to-drain gain \(g_m R_D\) in the numerator, without the extra factor of 2, doubles this result. The estimate \(g_m R_{SS}\) drops both the \(1/2\) and the 1 inside the exact ratio. A differential output on a matched pair is a different case: that common-mode piece cancels, and mismatch sets the ratio.",
                alternates=["0.5+gm*RSS", "1/2+gm*RSS", "(2*gm*RSS+1)/2"],
            )),
            ("cmrr-r1-q3", fresh(
                1, "order",
                r"Order why a stiffer tail raises the single-ended CMRR. Each step after the first uses the result of the step before it.",
                [
                    r"In the common-mode half circuit each device is degenerated by \(2R_{SS}\).",
                    r"Raising \(R_{SS}\) therefore lowers the common-mode gain, whose magnitude is about \(R_D/(2R_{SS})\).",
                    r"The differential half circuit still has an AC ground at the source, so the one-output differential gain \(g_m R_D/2\) does not depend on \(R_{SS}\).",
                    r"The ratio of those gains rises with \(R_{SS}\). A cascode current source is one way to make that resistance large.",
                ],
                r"CMRR is \(|A_{DM}/A_{CM}|\). Lowering \(R_D\) cuts both gains, and the single-ended ratio \((1+2g_m R_{SS})/2\) has no \(R_D\) in it. Setting the tail current to zero removes the bias rather than raising the ratio. Driving only one input does not change \(R_{SS}\). Capacitance across the tail does the opposite at high frequency: it lowers the impedance the common-mode half sees.",
            )),
            ("cmrr-r2-q2", fresh(
                2, "find_error",
                r"A worked solution gives the CMRR of a perfectly matched pair whose output is taken differentially. Exactly one step is wrong.",
                [
                    r"A common-mode input pushes the same signal current through both matched halves.",
                    r"The two drain voltages therefore move by the same amount.",
                    r"A finite tail resistance still leaves a differential residue, so \(R_{SS}\) alone sets a finite differential CMRR.",
                    r"Subtracting the two drains cancels that shared move, and any real differential residue comes from mismatch.",
                ],
                2,
                r"Perfect matching makes the two common-mode outputs identical, so their difference is zero whatever \(R_{SS}\) is. A finite tail limits the single-ended common-mode gain, not this differential residue. Mismatch of the loads or of the two transconductances is what converts the common-mode current into a differential output. The supply voltage does not appear in that cancellation.",
                reasons=[
                    r"With perfect matching the differential common-mode gain is zero. A finite tail limits only the single-ended common-mode gain.",
                    r"Matching does not matter. The tail resistance is what remains in the differential output.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "mirror-load":
        return [
            ("mirror-load-r1-q3", fresh(
                1, "sym",
                r"Write the small-signal output resistance of a mirror-loaded pair, looking into the joined drains of the input device and the mirror device. Use ro2 and ro4.",
                "ro2*ro4/(ro2+ro4)",
                {"ro2": (1e3, 5e5), "ro4": (1e3, 5e5)},
                r"The two drains share the output node, so \(R_{out} = r_{o2}\parallel r_{o4} = r_{o2}r_{o4}/(r_{o2}+r_{o4})\). Adding \(r_{o2}+r_{o4}\) puts the two resistances in series. \(1/g_{m3}\) is the resistance of the diode-connected side, not of this node. \(R_{SS}\) is the tail, behind the sources. An external load connects to this node afterward; it is not already inside \(R_{out}\).",
                alternates=[
                    "1/(1/ro2+1/ro4)",
                    "(ro2**(-1)+ro4**(-1))**(-1)",
                ],
            )),
            ("mirror-load-r1-q2", fresh(
                1, "order",
                r"Order how a current-mirror load delivers the full differential transconductance to one output. \(v_{id}\) is the difference of the two gate voltages, and each input device has transconductance \(g_m\). Each step after the first uses the result of the step before it.",
                [
                    r"A differential input raises one input current by \(g_m v_{id}/2\) and lowers the other by the same amount.",
                    r"The diode-connected transistor takes the increased current, and the mirror copies that increase into the output node.",
                    r"The other input device's decrease is already leaving that same output node.",
                    r"The two changes add, so the short-circuit output current is \(g_m v_{id}\), not half of it.",
                ],
                r"Resistor loads leave one drain with only its own \(g_m v_{id}/2\). The mirror turns the other half around and adds it, which is why \(G_m = g_m\). The tail current does not change under a pure differential input, and the tail is still what sets the sum. The two drains are not made identical: one side is a diode and the other is the high-impedance output. Half-circuit gain formulas do not apply to this asymmetric load.",
            )),
            ("mirror-load-r3-q2", fresh(
                3, "find_error",
                r"A worked solution analyses a mirror-loaded pair with half circuits. Exactly one step is wrong.",
                [
                    r"One load device is diode-connected, and the other is the mirror's output transistor.",
                    r"Half circuits require the two halves to be mirror images, so a common-mode input produces no differential output.",
                    r"Replacing the diode with \(1/g_m\) and cutting the circuit down the middle restores that symmetry.",
                    r"The stage is instead read from \(G_m = g_m\) and from \(R_{out} = r_{o2}\parallel r_{o4}\) at the single output.",
                ],
                2,
                r"A diode on one side and a current source on the other are not mirror images, so the modes mix. Substituting \(1/g_m\) for the diode does not make a legal half circuit. An ideal tail does not repair the asymmetry. \(G_m\) and \(R_{out}\) on the whole circuit are the small-signal description that remains. The gain is not \(g_m/2\); that factor belongs to one resistor-loaded drain.",
                reasons=[
                    r"The loads are not symmetric, so the modes mix. \(G_m\) and \(R_{out}\) replace the half circuits.",
                    r"A diode becomes \(1/g_m\), and that substitution is enough to keep the differential half circuit valid.",
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
