#!/usr/bin/env python3
"""SG-063 current mirrors and biasing: swap the most pattern-matchable MC items.

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

SKILLS = ["high-load", "diode-conn", "mirror", "degeneration", "cascode-src", "ref-gen"]


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
    if sid == "high-load":
        return [
            ("high-load-r2-q3", fresh(
                2, "sym",
                r"Write the magnitude of the gain of a current-source-loaded common-source stage. The gain device has overdrive Vov, and the NMOS and PMOS channel-length parameters are lamn and lamp. Use Vov, lamn, and lamp.",
                "2/(Vov*(lamn+lamp))",
                {"Vov": (0.08, 0.5), "lamn": (0.02, 0.25), "lamp": (0.02, 0.3)},
                r"\(g_m = 2I_D/V_{ov}\) and \(r_{on}\parallel r_{op} = 1/(I_D(\lambda_n+\lambda_p))\), so the current cancels and the magnitude is \(2/(V_{ov}(\lambda_n+\lambda_p))\). The gain itself is negative. Halving the bias current halves \(g_m\) and doubles both output resistances, so this expression does not change. \(2/(V_{ov}\lambda_n)\) drops the load. \(V_{ov}(\lambda_n+\lambda_p)/2\) inverts the ratio. \(2V_{ov}/(\lambda_n+\lambda_p)\) puts the overdrive on top, which is not this product of \(g_m\) and the parallel resistance.",
                alternates=["2/(Vov*lamn+Vov*lamp)", "2*Vov**(-1)*(lamn+lamp)**(-1)"],
            )),
            ("high-load-r1-q1", fresh(
                1, "order",
                r"Order why a current-source load gives a large common-source gain without a large DC drop. Each step after the first uses the result of the step before it.",
                [
                    r"A resistor-loaded gain magnitude is about \(2V_{RD}/V_{ov}\), so a large gain asks the resistor for a large DC drop.",
                    r"That drop comes out of the supply, so a low-voltage supply then has little room left for the signal.",
                    r"A current-source load avoids that drop: at DC it needs only about one overdrive, while the signal still sees \(r_{op}\).",
                    r"The gain magnitude is then \(g_m(r_{on}\parallel r_{op})\), which stays large without spending the supply on the resistor drop.",
                ],
                r"The current source separates the DC drop from the small-signal resistance. It does not raise the gain by lowering the bias current, and it does not make the gain independent of \(g_m\). The supply is still required. A resistor that matched \(r_{op}\) would spend far more voltage at the same current.",
            )),
            ("high-load-r3-q2", fresh(
                3, "find_error",
                r"A worked solution says where the DC output of a current-source-loaded common-source stage sits. Exactly one step is wrong.",
                [
                    r"The NMOS and the PMOS are both current sources tied to one output node.",
                    r"Each device's output resistance is large, so the resistance of the parallel combination is still large.",
                    r"A small difference between the two bias currents has to flow through that large resistance.",
                    r"The output therefore stays at mid-supply for any mismatch, because two complementary devices always split the supply in half.",
                ],
                3,
                r"The voltage that absorbs the mismatch is that current times the large parallel resistance, so a tiny mismatch moves the DC output a long way. Nothing in the two current sources prefers mid-supply. Feedback is what pins the node in a practical circuit. A small \(g_m\) is not what sets this DC point, and the PMOS still has a threshold.",
                reasons=[
                    r"The mismatch current times the large resistance swings the output, so the DC point is not a supply split.",
                    r"The DC output is fixed by \(g_m\), and a small \(g_m\) holds the node at mid-supply.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "diode-conn":
        return [
            ("diode-conn-r3-q2", fresh(
                3, "sym",
                r"Write the small-signal resistance of a diode-connected MOSFET when channel-length modulation and the body effect are ignored. Use kn for \(\mu_n C_{ox} W/L\) and IB for the bias current.",
                "1/sqrt(2*kn*IB)",
                {"kn": (1e-4, 2e-2), "IB": (5e-6, 4e-4)},
                r"\(I_B = \frac{1}{2} k_n V_{ov}^2\) gives \(V_{ov} = \sqrt{2I_B/k_n}\), and \(g_m = \sqrt{2 k_n I_B}\). The resistance is \(1/g_m\). Doubling the current multiplies \(g_m\) by \(\sqrt{2}\) and cuts the resistance by \(\sqrt{2}\), not by 2. \(1/(2 k_n I_B)\) is not a resistance of this device. \(\sqrt{2 k_n I_B}\) is \(g_m\) itself. Including \(r_o\) would put that resistance in parallel; it is not this expression.",
                alternates=["1/sqrt(2*IB*kn)", "(2*kn*IB)**(-1/2)"],
            )),
            ("diode-conn-r1-q1", fresh(
                1, "order",
                r"Order why a diode-connected MOSFET stays in saturation whenever it conducts. Each step after the first uses the result of the step before it.",
                [
                    r"The gate is tied to the drain, so \(V_{DS}\) equals \(V_{GS}\).",
                    r"Saturation requires \(V_{DS}\) to be at least \(V_{GS} - V_T\).",
                    r"With those two voltages equal, the saturation test becomes \(V_{GS} \ge V_{GS} - V_T\), a margin of exactly one threshold.",
                    r"Every conducting current therefore keeps the device saturated, and the device cannot sit in triode.",
                ],
                r"\(V_{DS} = V_{GS}\) is always one threshold above the saturation boundary \(V_{GS}-V_T\). The current source that feeds the device does not decide the region, and neither does a large \(r_o\). The drain is not required to sit at the supply. A device whose gate is not tied to its drain can leave saturation; this one cannot, while it conducts.",
            )),
            ("diode-conn-r2-q1", fresh(
                2, "find_error",
                r"A worked solution says what four times the width does to a diode-connected device at fixed current. Exactly one step is wrong.",
                [
                    r"At a fixed current, four times the width cuts the overdrive in half, because the overdrive scales as \(1/\sqrt{W/L}\).",
                    r"\(g_m = 2I_B/V_{ov}\), so half the overdrive doubles \(g_m\).",
                    r"With channel-length modulation ignored, the small-signal resistance is \(1/g_m\).",
                    r"The resistance therefore doubles, because \(g_m\) doubled.",
                ],
                3,
                r"\(1/g_m\) halves when \(g_m\) doubles. The resistance does not stay put just because the current is fixed, and it does not fall by four. \(r_o\) is in parallel and is usually the larger of the two, so it is not the resistance this width change sets. \(V_{GS}\) falls toward \(V_T\); it does not rise.",
                reasons=[
                    r"Doubling \(g_m\) halves \(1/g_m\). The resistance does not double with \(g_m\).",
                    r"The resistance is \(r_o\), which does not change when the device is made wider.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "mirror":
        return [
            ("mirror-r1-q3", fresh(
                1, "sym",
                r"Write the output current of a saturated mirror when channel-length modulation is ignored. Use IREF for the reference current, WL2 for the output device's \(W/L\), and WL1 for the reference device's \(W/L\).",
                "IREF*WL2/WL1",
                {"IREF": (1e-6, 5e-4), "WL2": (0.5, 40), "WL1": (0.5, 20)},
                r"Matched devices share \(\mu_n C_{ox}\) and \(V_T\), so those cancel and the currents stand in the ratio of the two \(W/L\) values. \(I_{REF} \cdot WL1/WL2\) inverts the ratio. \(I_{REF}(WL2-WL1)\) subtracts geometries that should divide. The factor \((1+\lambda V_{DS2})/(1+\lambda V_{DS1})\) is the channel-length correction this expression leaves out; it is 1 only when the two drains sit at the same voltage or \(\lambda = 0\).",
                alternates=["WL2*IREF/WL1", "IREF*(WL2/WL1)"],
            )),
            ("mirror-r2-q3", fresh(
                2, "order",
                r"Order how one reference current biases several separate branches. Each step after the first uses the result of the step before it.",
                [
                    r"The diode-connected reference turns \(I_{REF}\) into one gate-source voltage.",
                    r"Each output device ties its gate to that same node and its source to the same source, so every output sees that \(V_{GS}\).",
                    r"Matched devices at that shared \(V_{GS}\) carry current in proportion to \(W/L\), each scaled from \(I_{REF}\) by its own ratio.",
                    r"The drains stay separate, so the branches do not have to be wired in series and do not need a resistor to split the reference.",
                ],
                r"One diode sets a gate voltage, and every output that shares it copies a sized fraction of \(I_{REF}\). Each branch does not need its own reference resistor. Tying the outputs in series would stack the devices instead of copying the current. Connecting the drains together would add the currents into one node, which is not a set of separate biases.",
            )),
            ("mirror-r3-q2", fresh(
                3, "find_error",
                r"A worked solution states the lowest output voltage at which a basic mirror still copies. Exactly one step is wrong.",
                [
                    r"The reference device is diode-connected, so its drain sits at \(V_{GS}\).",
                    r"The output device shares that gate and the same source, so it has the same \(V_{GS}\).",
                    r"The output stays saturated when its own \(V_{DS}\) is at least \(V_{GS}-V_T\), which is the overdrive.",
                    r"The output node must therefore stay above the reference drain's \(V_{GS}\), or the copy fails.",
                ],
                3,
                r"The compliance floor is the overdrive of the output device, not the diode voltage and not \(V_T\) alone. The reference drain sits at \(V_{GS}\) only because its gate is tied to its drain. The output drain does not have that tie, so it may sit much lower and still be saturated. Below the overdrive the output device enters triode and the copy collapses.",
                reasons=[
                    r"The floor is the output overdrive. The reference drain is at \(V_{GS}\) only because that device is diode-connected.",
                    r"Saturation is set by \(V_T\) alone, so the output must stay above the threshold.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "degeneration":
        return [
            ("degeneration-r1-q3", fresh(
                1, "sym",
                r"Write the effective transconductance \(G_m = i_{out}/v_{in}\) of a source-degenerated stage. Ignore \(r_o\) and the body effect. Use gm and RS.",
                "gm/(1+gm*RS)",
                {"gm": (2e-4, 2e-2), "RS": (50, 5000)},
                r"The source resistor drops \(g_m v_{gs} R_S\), so \(v_{gs}(1+g_m R_S) = v_{in}\) and \(G_m = g_m/(1+g_m R_S)\). When \(g_m R_S \gg 1\) this tends to \(1/R_S\), which is the limit, not the expression at a moderate loop gain. Using \(g_m\) alone forgets the feedback. \(g_m R_S\) is dimensionless. \(g_m/(1-g_m R_S)\) has the wrong sign in the feedback term.",
                alternates=["1/(1/gm+RS)", "(gm**(-1)+RS)**(-1)"],
            )),
            ("degeneration-r3-q2", fresh(
                3, "order",
                r"Order why source degeneration makes the input-to-current curve straighter. Each step after the first uses the result of the step before it.",
                [
                    r"Current in the source resistor lifts the source, so only the fraction \(1/(1+g_m R_S)\) of the input appears as \(v_{gs}\).",
                    r"The device's square-law curvature then acts on that reduced \(v_{gs}\), not on the whole input.",
                    r"The resulting current is converted through \(R_S\), and the resistor is linear.",
                    r"\(G_m\) therefore moves less when \(g_m\) changes, and the stage is straighter than the bare device.",
                ],
                r"Local feedback keeps most of the input across the resistor. Degeneration does not cancel the square law exactly, and it does not push the device into triode. It does not raise the overdrive at a fixed current. The same feedback also raises the resistance seen at the drain; that is a separate result, not the reason the curve is straighter.",
            )),
            ("degeneration-r2-q3", fresh(
                2, "find_error",
                r"A worked solution doubles \(R_S\) in a stage that started at \(g_m R_S = 4\). Exactly one step is wrong.",
                [
                    r"At \(g_m R_S = 4\), \(G_m = g_m/(1+4) = g_m/5\).",
                    r"Doubling \(R_S\) makes \(g_m R_S = 8\), so the new value is \(g_m/(1+8) = g_m/9\).",
                    r"The new transconductance over the old one is \((g_m/9)/(g_m/5) = 5/9\).",
                    r"\(G_m\) therefore halves, because the resistor doubled and \(g_m\) did not change.",
                ],
                3,
                r"The ratio \(5/9\) is a drop of four ninths, not a factor of one half. \(G_m\) does not stay constant, and it does not double. Halving would be right only for a \(1/R_S\) limit in which \(g_m R_S\) stayed large on both sides. Here \(g_m R_S\) goes from 4 to 8, and the exact formula is \(g_m/(1+g_m R_S)\).",
                reasons=[
                    r"\(G_m\) falls from \(g_m/5\) to \(g_m/9\), which is \(5/9\) of the old value, not half.",
                    r"\(g_m\) is fixed, so doubling \(R_S\) cannot change \(G_m\).",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "cascode-src":
        return [
            ("cascode-src-r2-q3", fresh(
                2, "sym",
                r"Write the factor \(v_x/v_{out}\) for a cascode current source, body effect ignored, in the limit where the output resistance is about \(g_{m2} r_{o2} r_{o1}\). Use gm2 and ro2.",
                "1/(gm2*ro2)",
                {"gm2": (2e-4, 2e-2), "ro2": (1e4, 2e5)},
                r"\(R_{out} \approx g_{m2} r_{o2} r_{o1}\) and the move at node X is the output move times \(r_{o1}/R_{out}\), so the factor is \(1/(g_{m2} r_{o2})\). It is not 1: node X does not follow the output. It is not \(1/2\). It is not zero, because \(r_{o1}\) is finite. Adding \(g_{mb2}\) replaces \(g_{m2}\) by \(g_{m2}+g_{mb2}\) and makes the factor slightly smaller. \(g_{m2} r_{o2}\) is the reciprocal of this factor.",
                alternates=["(gm2*ro2)**(-1)", "1/gm2/ro2"],
            )),
            ("cascode-src-r1-q2", fresh(
                1, "order",
                r"Order why stacking the cascode device makes the output current almost insensitive to the output voltage. Each step after the first uses the result of the step before it.",
                [
                    r"A rise at the output tries to increase the current in the cascode device.",
                    r"That extra current can come only through the bottom device, so node X would have to rise across the bottom device's \(r_o\).",
                    r"The cascode gate is fixed, so a rise at X reduces \(v_{gs}\) and the cascode device opposes the current change.",
                    r"Node X therefore moves by about the output move divided by \(g_m r_o\), and the output current barely changes.",
                ],
                r"The cascode device holds node X nearly still, so the bottom device's current barely changes. The two \(r_o\) values do not merely add in series. The cascode device does not double the current, and it does not push the bottom device into triode. The multiplication is about \(g_m r_o\), which is why the resistance is about \(g_m r_o^2\).",
            )),
            ("cascode-src-r1-q3", fresh(
                1, "find_error",
                r"A worked solution states the lowest output voltage of a cascode current source. Exactly one step is wrong.",
                [
                    r"Both the bottom device and the cascode device must stay saturated.",
                    r"The bottom device needs its drain, node X, at least one overdrive above its source.",
                    r"The cascode device needs the output at least one overdrive above node X.",
                    r"The second requirement replaces the first, so the output still needs only a single overdrive, the same compliance as one device.",
                ],
                3,
                r"The two overdrives add. An ideal gate bias needs about \(2V_{ov}\) at the output. A diode-stack bias holds the cascode gate near \(2V_T+2V_{ov}\) and needs \(V_T+2V_{ov}\). Neither floor is one overdrive, and the cascode is not in triode at that limit. The price of the large output resistance is this extra headroom, not a larger bias current.",
                reasons=[
                    r"The two overdrives stack. Ideal bias needs about \(2V_{ov}\); a diode stack needs \(V_T+2V_{ov}\).",
                    r"The cascode device is in triode at the compliance limit, so it adds no voltage of its own.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "ref-gen":
        return [
            ("ref-gen-r1-q2", fresh(
                1, "sym",
                r"Write the transconductance of the unit device in a constant-\(g_m\) reference. Use K for the width ratio of the wide device to the unit device, and R for the resistor in the wide device's source.",
                "2*(1-1/sqrt(K))/R",
                {"K": (1.5, 25), "R": (200, 50000)},
                r"The gate-source difference of the two NMOS devices sits across \(R\), and solving gives \(g_m = 2(1-1/\sqrt{K})/R\). Only the resistor and the ratio appear. The supply does not. \(\mu_n C_{ox} W/L\) sets the current, not this \(g_m\). \(2(1-\sqrt{K})/R\) puts the square root on the wrong side and is negative for \(K>1\). \(2(1-1/\sqrt{K})\) has dropped \(R\). The current \(2(1-1/\sqrt{K})^2/(k R^2)\) is a different result, and it still depends on the process parameter \(k\).",
                alternates=["2/R-2/(R*sqrt(K))", "(2/R)*(1-K**(-0.5))"],
            )),
            ("ref-gen-r2-q2", fresh(
                2, "order",
                r"Order why a self-biased constant-\(g_m\) reference can fail to start. Each step after the first uses the result of the step before it.",
                [
                    r"The mirror forces the two branch currents to be equal.",
                    r"Zero current in both branches meets that equality, and both NMOS devices are off.",
                    r"The intended bias is a second solution of the same loop, with a nonzero current set by \(K\) and \(R\).",
                    r"Nothing in the loop prefers the nonzero solution, so without a start-up path the circuit can remain off.",
                ],
                r"The zero-current state is a consistent solution, which is why a start-up circuit has to kick the loop into the intended one. Start-up does not set \(K\), and it is not there to cancel channel-length modulation. It also does not limit the running current. Once the nonzero solution is reached, the start-up path should let go so it does not keep adding current.",
            )),
            ("ref-gen-r2-q3", fresh(
                2, "find_error",
                r"A worked solution raises the supply of an ideal constant-\(g_m\) reference from \(2.0\ \mathrm{V}\) to \(3.3\ \mathrm{V}\). Exactly one step is wrong.",
                [
                    r"The current is fixed by the difference of two gate-source voltages across \(R\), and the supply is not in that equation.",
                    r"Ideally the current depends on \(K\), \(R\), and the unit device's \(\mu_n C_{ox} W/L\).",
                    r"Raising the supply does increase the drain-source voltage of the mirror devices.",
                    r"The current therefore scales in proportion to the supply, the same way a resistor from the supply to ground would.",
                ],
                3,
                r"Ideally the current is unchanged, because the supply never entered the loop equation. Finite output resistance lets channel-length modulation raise the current slightly; it does not make the current proportional to the supply, and it does not halve it. The square of the supply does not appear either. The same slight rise is why a real reference is not perfectly flat.",
                reasons=[
                    r"Ideally the current is unchanged. Channel-length modulation lets it rise only slightly.",
                    r"The extra supply reduces the overdrive, so the current halves.",
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
