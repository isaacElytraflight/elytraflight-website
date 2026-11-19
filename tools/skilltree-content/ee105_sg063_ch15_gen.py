#!/usr/bin/env python3
"""SG-063 multi-stage amplifiers: swap the most pattern-matchable MC items.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The new questions use the same relations as the
explainers, and the explainer worked examples do not use these prompts.
The verifier does not import this file.

Ground glyphs on the cascade-frequency and cascode figures end at y=144.
Those 140-tall viewBoxes are extended so the batch figure check can pass,
and those question versions are bumped. Swapped questions leave the live
bank, so they are not in this list.
"""
import json
import os

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "cs-cascade",
    "cs-cascade-freq",
    "cs-cap-load",
    "cascode-amp",
    "cascode-bias",
    "big-circuit",
]

# Ground glyph ends at y=144. A 140-tall viewBox fails figure_bounds.
FIGURE_FIX = {
    "cs-cascade-freq-r1-q2": ('viewBox="0 0 522 140"', 'viewBox="0 0 522 152"'),
    "cs-cascade-freq-r1-q3": ('viewBox="0 0 522 140"', 'viewBox="0 0 522 152"'),
    "cs-cascade-freq-r2-q1": ('viewBox="0 0 522 140"', 'viewBox="0 0 522 152"'),
    "cs-cascade-freq-r3-q2": ('viewBox="0 0 698 140"', 'viewBox="0 0 698 152"'),
    "cs-cascade-freq-r3-q3": ('viewBox="0 0 698 140"', 'viewBox="0 0 698 152"'),
    "cs-cascade-freq-r4-q1": ('viewBox="0 0 522 140"', 'viewBox="0 0 522 152"'),
    "cs-cascade-freq-r4-q3": ('viewBox="0 0 522 140"', 'viewBox="0 0 522 152"'),
    "cascode-amp-r2-q3": ('viewBox="0 0 522 140"', 'viewBox="0 0 522 152"'),
    "cascode-amp-r3-q1": ('viewBox="0 0 522 140"', 'viewBox="0 0 522 152"'),
}


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
    if sid == "cs-cascade":
        return [
            ("cs-cascade-r1-q2", fresh(
                1, "order",
                r"Order how a two-stage common-source cascade gets more low-frequency gain than one stage. Each step after the first uses the result of the step before it.",
                [
                    r"One stage's gain magnitude cannot pass \(g_m r_o\), and a resistor load runs out of headroom before that limit.",
                    r"The first drain drives the second gate, and that gate draws no low-frequency current, so the first stage keeps its unloaded gain.",
                    r"The second stage multiplies that voltage by its own \(-g_m(r_o\parallel r_{oc})\).",
                    r"Two minus signs make the product positive, and the magnitudes multiply, which is the same as adding the stage gains in decibels.",
                ],
                r"The next gate does not load the previous drain, so the stage gains multiply. A single larger resistor cannot pass the headroom limit or \(g_m r_o\). Dividing by an interstage input resistance invents a current the gate does not draw. Three stages would flip the sign again. The cascade's output resistance is only the last stage's parallel combination, not the product of the two output resistances.",
            )),
            ("cs-cascade-r1-q3", fresh(
                1, "sym",
                r"Write the low-frequency output resistance of a common-source cascade. Only the last stage faces the outside world. Use ro and roc for that last device and its current-source load.",
                "ro*roc/(ro+roc)",
                {"ro": (1e3, 5e5), "roc": (1e3, 5e5)},
                r"The two resistances share the output node, so \(R_{out} = r_o\parallel r_{oc} = r_or_{oc}/(r_o+r_{oc})\). The input is the first gate, infinite at low frequency, and it is not part of this parallel combination. Adding \(r_o+r_{oc}\) would put the two resistances in series. The first stage's output resistance is the interstage node, not the cascade port. An external load attaches to this node; it is not already inside \(R_{out}\).",
                alternates=[
                    "1/(1/ro+1/roc)",
                    "(ro**(-1)+roc**(-1))**(-1)",
                ],
            )),
            ("cs-cascade-r3-q1", fresh(
                3, "find_error",
                r"A worked solution gives the sign of a three-stage common-source cascade. Exactly one step is wrong.",
                [
                    r"Each common-source stage contributes one inversion.",
                    r"The next gate draws no low-frequency current, so the stage gains multiply, signs included.",
                    r"Three inversions leave an overall minus sign.",
                    r"The cascade gain is therefore positive, because multiplying the magnitudes drops every sign.",
                ],
                3,
                r"Three inversions leave a negative gain. Two stages would be positive. Adding the decibel gains adds magnitudes and does not choose the sign. The output resistance has no sign, and an interstage gate does not add an extra inversion.",
                reasons=[
                    r"Three inversions leave a negative gain. Dropping the signs is the mistake.",
                    r"Only the first inversion counts, so later stages cannot change the sign.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "cs-cascade-freq":
        return [
            ("cs-cascade-freq-r1-q1", fresh(
                1, "sym",
                r"Write the Miller estimate of the intermediate-node time constant in a two-stage common-source cascade. Stage 1's output resistance is R1. \(C_{gd2}\) is multiplied by one plus stage 2's gain magnitude, gm2 times R2, and R1 drives that whole capacitance. Use R1, Cgs2, Cdb1, Cgd2, gm2, and R2.",
                "R1*(Cgs2+Cdb1+Cgd2*(1+gm2*R2))",
                {"R1": (500, 1e5), "Cgs2": (2e-15, 2e-13), "Cdb1": (1e-15, 8e-14),
                 "Cgd2": (5e-16, 4e-14), "gm2": (2e-4, 2e-2), "R2": (200, 5e4)},
                r"The three-node model puts \(C_{gs2}\), \(C_{db1}\), and \(C_{gd2}(1+g_{m2}R_2)\) on the intermediate node and drives them with \(R_1\). That product is the Miller estimate, and the large resistance times the multiplied capacitance is why the node limits the bandwidth. The open-circuit resistance across the bridging \(C_{gd2}\) is \(R_1+R_2+g_{m2}R_1R_2\), so the open-circuit sum is larger by \(R_2C_{gd2}\). This estimate does not include that extra term. \(R_s\) drives only the input node. \(C_{gd2}\) without the Miller factor treats the bridge as a capacitor to AC ground. The product of the three capacitances is not a time constant, and \(1/(2\pi\sum\tau)\) is the bandwidth estimate rather than this one term.",
                alternates=[
                    "R1*Cgs2+R1*Cdb1+R1*Cgd2+R1*gm2*R2*Cgd2",
                    "R1*Cgs2+R1*Cdb1+R1*(1+gm2*R2)*Cgd2",
                ],
            )),
            ("cs-cascade-freq-r2-q2", fresh(
                2, "find_error",
                r"A worked solution says what happens to a two-stage common-source cascade when the source resistance \(R_s\) is lowered. Exactly one step is wrong.",
                [
                    r"The input capacitance is \(C_{gs1}+C_{gd1}(1+|A_1|)\), and \(R_s\) drives it.",
                    r"Lowering \(R_s\) shrinks that input time constant.",
                    r"The intermediate node is driven by stage 1's output resistance, not by \(R_s\).",
                    r"Every time constant of the cascade therefore shrinks, and the bandwidth rises in proportion to \(1/R_s\).",
                ],
                3,
                r"\(R_s\) sits only at the input. The intermediate node is charged through stage 1's output resistance, and the output node is charged through the last load. Lowering \(R_s\) does not change those resistances or the midband gains that set the Miller factors. A smaller input time constant helps only when that node was the one limiting the bandwidth.",
                reasons=[
                    r"Only the input time constant depends on \(R_s\). The intermediate node is untouched.",
                    r"Lowering \(R_s\) raises both stage gains, so every Miller capacitance falls.",
                ],
                correct_reason=0,
            )),
            ("cs-cascade-freq-r3-q1", fresh(
                3, "order",
                r"Order how a source follower inserted after the first common-source stage extends the cascade's bandwidth. Each step after the first uses the result of the step before it.",
                [
                    r"The follower's gain sits just below \(+1\).",
                    r"The voltage across its \(C_{gs}\) is only a small fraction of the input move, so that capacitance looks small at the follower's gate.",
                    r"Stage 1's drain therefore drives \(C_{db1}\) plus the follower's \(C_{gd}\), not the next stage's Miller capacitance.",
                    r"The follower's output resistance, about \(1/g_m\), is what charges that Miller capacitance, so the time constant there collapses too.",
                ],
                r"The follower splits the killer node: a high resistance sees a small capacitance, and a large capacitance sees about \(1/g_m\). Shorting the follower's \(C_{gs}\) would describe a diode, not the bootstrap. The follower does not raise the stage gains, and it does not remove the final output pole. Its cost is bias current and a little headroom.",
            )),
        ]
    if sid == "cs-cap-load":
        return [
            ("cs-cap-load-r1-q1", fresh(
                1, "sym",
                r"Write the gain-bandwidth product, in radians per second, of a common-source stage whose load capacitance CL sets the dominant pole. The midband gain magnitude is gm times the resistance at the drain. Use gm and CL.",
                "gm/CL",
                {"gm": (2e-4, 2e-2), "CL": (2e-13, 2e-9)},
                r"The gain magnitude is \(g_m R\) and the output pole is \(1/(RC_L)\), so the product is \(g_m/C_L\). The resistance cancels. Keeping \(R\) in the product, as \(g_m R/C_L\), still has the load in it and is not the gain-bandwidth. \(1/(RC_L)\) is the pole alone. The input Miller time constant uses the source resistance and the device capacitances; it is not this product. Halving the drain resistance doubles the bandwidth and halves the gain, and the product stays put.",
                alternates=["gm*CL**(-1)", "(CL/gm)**(-1)"],
            )),
            ("cs-cap-load-r2-q2", fresh(
                2, "find_error",
                r"A worked solution halves the drain resistance of a common-source stage whose bandwidth is set by a large load capacitance. Exactly one step is wrong.",
                [
                    r"The dominant pole sits at the output, at \(1/[(R_D\parallel r_o)C_L]\).",
                    r"Halving \(R_D\parallel r_o\) doubles that pole frequency.",
                    r"The midband gain magnitude is \(g_m(R_D\parallel r_o)\), so the same cut halves the gain.",
                    r"Gain and bandwidth therefore both double, and the gain-bandwidth product rises by four.",
                ],
                3,
                r"Bandwidth and gain trade one for one when the load capacitance dominates. Their product is \(g_m/C_L\), which has no drain resistance in it. Raising the product means raising \(g_m\) or lowering the load capacitance. The input pole does not set this trade while the load capacitance is the large one.",
                reasons=[
                    r"The gain falls by the same factor the bandwidth rises, so \(g_m/C_L\) is unchanged.",
                    r"Halving the load resistance moves the pole down, because a smaller resistance drives the capacitor more slowly.",
                ],
                correct_reason=0,
            )),
            ("cs-cap-load-r3-q3", fresh(
                3, "order",
                r"Order why a source follower is the cheaper way to drive a large load capacitance at the same gain and a higher bandwidth. Each step after the first uses the result of the step before it.",
                [
                    r"The common-source stage keeps its drain resistance, so it keeps the gain \(g_m(R_D\parallel r_o)\).",
                    r"Its drain now sees the follower's small input capacitance instead of the load capacitance.",
                    r"The load capacitance is driven by the follower's output resistance, about \(1/g_{m2}\), far below the drain resistance.",
                    r"The extra current is one follower branch. Holding the gain while cutting the drain resistance instead would raise the common-source current in proportion.",
                ],
                r"The follower moves the load capacitance off the high-resistance node without giving up the gain. Cutting the drain resistance and raising the common-source \(g_m\) to hold the product spends that current in the gain device. The follower does not multiply the load by a Miller factor. Ignoring the follower's own output pole leaves out the new time constant \(C_L/g_{m2}\).",
            )),
        ]
    if sid == "cascode-amp":
        return [
            ("cascode-amp-r1-q1", fresh(
                1, "sym",
                r"Write the exact low-frequency output resistance of a cascode, looking into the drain of the common-gate device, with the input gate at AC ground. Use ro1, ro2, and gm2.",
                "ro1+ro2+gm2*ro1*ro2",
                {"ro1": (1e3, 2e5), "ro2": (1e3, 2e5), "gm2": (2e-4, 2e-2)},
                r"The common-gate device sees \(r_{o1}\) as source degeneration, so \(R_{out} = r_{o1}+r_{o2}+g_{m2}r_{o1}r_{o2}\). The estimate \(g_m r_o^2\) drops the two unmultiplied resistances, which still matter when \(g_m r_o\) is only moderate. \(r_{o1}\parallel r_{o2}\) is a parallel pair, not this stack. A resistor load in parallel with this result hides the boost, and the gain falls back to about \(g_{m1}R_D\). The transconductance stays \(g_{m1}\); stacking the second device does not multiply \(g_m\).",
                alternates=[
                    "ro1+ro2*(1+gm2*ro1)",
                    "ro2+ro1*(1+gm2*ro2)",
                ],
            )),
            ("cascode-amp-r2-q2", fresh(
                2, "order",
                r"Order why a resistor-loaded cascode is still faster than a common-source stage of the same gain. Each step after the first uses the result of the step before it.",
                [
                    r"The internal drain looks into the common-gate source, a resistance of about \(1/g_{m2}\).",
                    r"The gain from the input gate to that drain is about \(-g_{m1}/g_{m2}\), near \(-1\) when the devices match.",
                    r"\(C_{gd1}\) is therefore multiplied by about 2, not by one plus the magnitude of the output gain.",
                    r"The input pole stays high, and the output node, at about \(R_DC_o\), is what usually sets the bandwidth.",
                ],
                r"The cascode shields \(C_{gd1}\) from the full output swing. Multiplying \(C_{gd1}\) by the output gain describes a plain common-source stage. \(C_{gd}\) of the common-gate device returns to an AC-grounded gate and is not multiplied. A current-source load can still turn the large output resistance into a large gain; the resistor is what gives that gain away. The internal node is fast because its resistance is low, not because it has no capacitance.",
            )),
            ("cascode-amp-r3-q3", fresh(
                3, "find_error",
                r"A worked solution names the node that sets the bandwidth of a resistor-loaded cascode. Exactly one step is wrong.",
                [
                    r"The internal node looks into about \(1/g_{m2}\), much smaller than the load resistance.",
                    r"Its time constant is that small resistance times the capacitance at the internal drain.",
                    r"The output time constant is about \(R_DC_o\), with the load in parallel with the cascode's large output resistance.",
                    r"The internal node has more device capacitances, so it is the one that sets the bandwidth.",
                ],
                3,
                r"A pole frequency follows \(1/(RC)\). The internal resistance is about \(1/g_m\), so that pole is high even with a few device capacitances on it. The output node carries the load resistance. With an ideal current-source load the output resistance becomes about \(g_m r_o^2\) and the output pole drops further. The input pole stays high because \(C_{gd1}\) is barely multiplied.",
                reasons=[
                    r"The output resistance is the large one, so the output node sets the bandwidth.",
                    r"The node with the most capacitors is always the dominant pole, whatever the resistances are.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "cascode-bias":
        return [
            ("cascode-bias-r1-q1", fresh(
                1, "order",
                r"Order why a cascode current source holds its current more constant than a simple mirror. Each step after the first uses the result of the step before it.",
                [
                    r"The bottom device sets the current from its gate-source voltage.",
                    r"The cascode device's gate is fixed, so its source, the bottom drain, barely moves.",
                    r"The bottom device's drain-source voltage therefore stays nearly constant as the output voltage moves.",
                    r"Channel-length modulation hardly changes the current, and the output resistance rises to about \((1+g_m r_o)r_o\).",
                ],
                r"The cascode pins the drain-source voltage of the current-setting device. A simple mirror lets that voltage equal the output, so \(r_o\) alone sets the compliance. Shorting the cascode device would remove the shield. The boosted resistance is about \((1+g_m r_o)r_o\), whose leading term is \(g_m r_o^2\), the same first-order result as looking into a cascode drain. The headroom this stack costs is a separate count from the resistance.",
            )),
            ("cascode-bias-r2-q3", fresh(
                2, "sym",
                r"Write the minimum output voltage of a standard cascode mirror that still keeps both devices in saturation. The stacked device's gate sits at twice \(V_T+V_{ov}\). Use VT and Vov.",
                "VT+2*Vov",
                {"VT": (0.25, 0.8), "Vov": (0.08, 0.4)},
                r"The cascode source sits one threshold plus one overdrive below its gate, at \(V_T+V_{ov}\), and the output must sit one more overdrive above that source. The floor is \(V_T+2V_{ov}\). A simple mirror only needs \(V_{ov}\). \(V_T+V_{ov}\) is the source voltage, one overdrive short of the floor. Twice \(V_T+V_{ov}\) is the gate bias, not the output. A high-swing gate sits at \(V_T+2V_{ov}\), and that floor falls to \(2V_{ov}\).",
                alternates=["2*Vov+VT", "Vov+VT+Vov"],
            )),
            ("cascode-bias-r4-q1", fresh(
                4, "find_error",
                r"A worked solution places the DC output of a cascode amplifier that uses a cascode current-source load. Exactly one step is wrong.",
                [
                    r"The signal branch and the load are both current sources with a very high output resistance.",
                    r"Each one is trying to set the same DC current.",
                    r"Any small mismatch between those currents has only the output node to flow into.",
                    r"The high output resistance then holds the DC voltage at mid-supply, so no extra loop is required.",
                ],
                3,
                r"Two stiff current sources cannot both win. The output voltage runs away until some transistor leaves saturation. A feedback loop has to set that DC level. The high output resistance is what makes the gain large; it does not choose the bias point. A resistor load would set the voltage by itself, and it would also throw the gain away.",
                reasons=[
                    r"A current mismatch drives the output until a device leaves saturation. Feedback has to set the DC level.",
                    r"The high resistance makes any current mismatch sit at mid-supply, so the loop can be omitted.",
                ],
                correct_reason=0,
                preview=["big-circuit"],
            )),
        ]
    if sid == "big-circuit":
        return [
            ("big-circuit-r1-q1", fresh(
                1, "order",
                r"Order the simplification of a large transistor schematic down to a familiar stage. Each step after the first uses the result of the step before it.",
                [
                    r"Trace the signal from the input device to the output node, and mark every other device as support.",
                    r"Diode-connected bias devices only set DC voltages, so treat those nodes as AC grounds.",
                    r"A device whose gate-source voltage is held constant is a current source: an open circuit at AC, or its \(r_o\) if that resistance matters.",
                    r"What remains is a known stage. In a folded stack it is a common-source device feeding a common-gate device of the opposite type.",
                ],
                r"Most transistors in a large schematic set bias. Treating a constant gate-source device as a short would ground a signal node. A diode-connected device is an AC ground at its gate, not a signal transistor. The fold node is a low-impedance current sum, not another gain node. Once the current divider is close to one, the gain that remains is about \(-g_m R_L\).",
            )),
            ("big-circuit-r1-q2", fresh(
                1, "find_error",
                r"A worked solution models the bias devices whose gate-source voltage is constant in a folded cascode. Exactly one step is wrong.",
                [
                    r"Those gates are tied to fixed bias, so the gate-source voltage does not move with the signal.",
                    r"With that voltage fixed, the device current has no signal part from the gate.",
                    r"At AC the device is a current source: an open circuit, or \(r_o\) from its drain to AC ground if that resistance matters.",
                    r"A constant current is a short circuit to AC ground, so replace each of those drains with a short.",
                ],
                3,
                r"Signal current cannot enter a fixed gate-source device through its gate. The drain node stays in the circuit, loaded only by \(r_o\) when that matters. Shorting the drain to ground would kill the signal at the fold or at the output. A diode-connected transistor is the one whose gate is an AC ground. Leaving the device in as a second common-source stage invents a gain it does not have.",
                reasons=[
                    r"A current source is an open circuit at AC. A short would be a voltage source or a diode-connected gate.",
                    r"Fixed gate-source voltage means the device is off, so both the current source and \(r_o\) should be deleted.",
                ],
                correct_reason=0,
            )),
            ("big-circuit-r3-q1", fresh(
                3, "sym",
                r"Write the resistance seen looking into the source of the common-gate device in a folded cascode. Its drain sees its own output resistance in series with the load RL, and its gate is at AC ground. Use ro3, RL, and gm3.",
                "(ro3+RL)/(1+gm3*ro3)",
                {"ro3": (2e3, 2e5), "RL": (200, 8e4), "gm3": (2e-4, 2e-2)},
                r"The source resistance is \((r_{o3}+R_L)/(1+g_{m3}r_{o3})\). When the load is only a few times \(1/g_m\) and \(g_m r_o\) is large, this is about \(1/g_{m3}\). It rises once the load becomes comparable to \(g_{m3}r_{o3}\), and the \(1/g_m\) shortcut then fails. \(1/g_{m3}\) alone drops the load. \(r_{o3}+R_L\) is the series string without the source factor. The current divider at the fold uses \(g_{m3}\), \(1/r_{o1}\), and \(1/r_{o2}\); it is not this input resistance.",
                alternates=[
                    "(RL+ro3)/(1+ro3*gm3)",
                    "(ro3+RL)/(gm3*ro3+1)",
                ],
            )),
        ]
    raise SystemExit("no swaps for " + sid)


def fix_figures(bank):
    changed = False
    for q in bank["questions"]:
        pair = FIGURE_FIX.get(q["id"])
        if not pair:
            continue
        old, new = pair
        fig = q.get("figure") or ""
        if new in fig:
            continue
        if fig.count(old) != 1:
            raise SystemExit(q["id"] + " viewBox not found once")
        q["figure"] = fig.replace(old, new, 1)
        version = q.get("version")
        q["version"] = (version if isinstance(version, int) else 1) + 1
        changed = True
    return changed


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
    if fix_figures(bank):
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
