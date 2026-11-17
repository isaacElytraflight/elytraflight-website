#!/usr/bin/env python3
"""SG-063 MOS small-signal models: swap the most pattern-matchable MC items.

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

SKILLS = ["cs-intro", "gm", "ro", "ss-model"]


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
    if sid == "cs-intro":
        return [
            ("cs-intro-r1-q3", fresh(
                1, "sym",
                r"Write the drain current the load resistor allows, as a function of the drain-source voltage. Use VDD for the supply, VDS for the drain-source voltage, and RD for the load resistance.",
                "(VDD-VDS)/RD",
                {"VDD": (1.2, 3.3), "VDS": (0.05, 1.1), "RD": (1, 40)},
                r"KVL on the drain resistor gives \(I_D=(V_{DD}-V_{DS})/R_D\), a straight line from \((V_{DD},0)\) to \((0,V_{DD}/R_D)\) with slope \(-1/R_D\). A parabola through the origin is the device curve, not the resistor. A horizontal line would be a current source, and a vertical line would be a fixed drain voltage. The bias point is where this line crosses the device curve for the applied gate-source voltage.",
                alternates=["(VDD-VDS)*RD**(-1)", "VDD/RD-VDS/RD"],
            )),
            ("cs-intro-r1-q2", fresh(
                1, "order",
                r"As the input of a resistor-loaded common-source stage rises from zero to the supply, order what the output does. Each step after the first uses the result of the step before it.",
                [
                    r"Below threshold the device is off, so the drain current is zero and the output sits at the supply.",
                    r"Past threshold the device is saturated, and the drain current grows with the square of the overdrive.",
                    r"That growing current increases the drop across the load resistor, so the output falls steeply.",
                    r"The output keeps falling until the drain voltage reaches the overdrive; below that the device is in triode and the curve flattens toward zero.",
                ],
                r"Below threshold there is no drop across the load, so the output stays at the supply. In saturation the drop grows with the square of the overdrive and the stage inverts, so the output falls rather than rises. The fall is not a straight line over the whole sweep, and it does not wait for triode: triode is where the curve flattens, after the drain has already fallen to the overdrive.",
            )),
            ("cs-intro-r2-q3", fresh(
                2, "find_error",
                r"A worked solution says what happens when the drain resistor of a saturated common-source stage is doubled, with the gate-source voltage held fixed. Exactly one step is wrong.",
                [
                    r"In saturation the drain current is set by the gate-source voltage.",
                    r"Doubling the resistor therefore doubles the voltage that current drops.",
                    r"The DC output falls by that extra drop.",
                    r"The current rises in proportion to the resistor, so the output cannot fall below the overdrive.",
                ],
                3,
                r"In saturation \(I_D\) depends on \(V_{GS}\), not on \(R_D\), so the drop \(I_DR_D\) doubles and the output falls. It does not rise, and it does not stay put. If the output falls below the overdrive, the device leaves saturation and only then does the current drop. The current does not rise with \(R_D\).",
                reasons=[
                    r"The current stays set by the gate until the drain falls below the overdrive, so a large resistor can push the device into triode.",
                    r"A larger resistor draws more current, which keeps the device in saturation.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "gm":
        return [
            ("gm-r1-q2", fresh(
                1, "sym",
                r"At fixed \(W/L\), write the factor by which \(g_m\) changes when the saturation current goes from ID1 to ID2.",
                "sqrt(ID2/ID1)",
                {"ID1": (20, 800), "ID2": (20, 800)},
                r"\(g_m=\sqrt{2\mu_n C_{ox}(W/L)I_D}\). At fixed size only the current changes, so the ratio of the transconductances is the square root of the current ratio. Doubling the current multiplies \(g_m\) by \(\sqrt{2}\), not by 2 and not by 4. The form \(g_m=2I_D/V_{ov}\) gives the same factor, because the overdrive itself grows as \(\sqrt{I_D}\).",
                alternates=["(ID2/ID1)**(1/2)"],
            )),
            ("gm-r2-q1", fresh(
                2, "order",
                r"The drain current is held fixed while the device is made wider. Order the steps that say what that does to \(g_m\). Each step after the first uses the result of the step before it.",
                [
                    r"The saturation current is fixed, and it obeys \(I_D \propto (W/L)V_{ov}^2\).",
                    r"A larger \(W/L\) therefore meets that current at a smaller overdrive, and the overdrive falls as \(1/\sqrt{W/L}\).",
                    r"\(g_m=2I_D/V_{ov}\), so that smaller overdrive raises \(g_m\).",
                    r"Substituting the overdrive's dependence on \(W/L\) into that formula shows \(g_m\) rises as \(\sqrt{W/L}\), not in proportion to \(W/L\).",
                ],
                r"At fixed current, \(V_{ov}\propto 1/\sqrt{W/L}\) and \(g_m=2I_D/V_{ov}\), so a wider device has a higher \(g_m\). The rise follows the square root of \(W/L\). \(g_m\) is not fixed by the current alone, and making the device wider does not lower it.",
            )),
            ("gm-r3-q2", fresh(
                3, "find_error",
                r"A worked solution says what it costs to raise \(g_m\) by lowering the overdrive at a fixed drain current. Exactly one step is wrong.",
                [
                    r"\(g_m=2I_D/V_{ov}\), so a lower overdrive raises \(g_m\) at fixed current.",
                    r"The square law needs \(W/L \propto I_D/V_{ov}^2\), so the device must be wider.",
                    r"The wider device has more gate capacitance, and a very small overdrive leaves the square-law region.",
                    r"Because the supply now drives a larger current, the power also rises.",
                ],
                3,
                r"Power is set by the drain current and the supply. The current is fixed, so the power does not change, and the gate still draws no current. The price is width: halving \(V_{ov}\) needs four times \(W/L\), which adds capacitance and slows the circuit, and a very small overdrive leaves the square law.",
                reasons=[
                    r"At fixed current the power is unchanged. The price is a wider device, more capacitance, and less margin to the square-law edge.",
                    r"Lowering the overdrive at fixed current raises the power, because the supply delivers more current.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "ro":
        return [
            ("ro-r2-q3", fresh(
                2, "sym",
                r"Write the drain-source voltage at which the extended saturated output curves cross the voltage axis. Use lam for the channel-length-modulation parameter.",
                "-1/lam",
                {"lam": (0.02, 0.5)},
                r"A saturated line is \(I_0(1+\lambda V_{DS})\), which is zero at \(V_{DS}=-1/\lambda\), for every gate voltage. The intercept is on the negative axis. \(+1/\lambda\) is the same distance on the wrong side, the lines are not parallel, and they do not meet at the origin.",
                alternates=["-(1/lam)", "(-1)*lam**(-1)"],
            )),
            ("ro-r1-q1", fresh(
                1, "order",
                r"Order the steps that say why a saturated MOSFET's drain current rises slightly as the drain-source voltage rises. Each step after the first uses the result of the step before it.",
                [
                    r"A higher drain-source voltage widens the depletion region at the drain.",
                    r"The pinch-off point therefore moves toward the source.",
                    r"The effective channel length \(L-\Delta L\) shrinks.",
                    r"The current, which scales as \(1/L_{\mathrm{eff}}\), rises.",
                ],
                r"The drain depletion region eats into the channel, so \(L_{\mathrm{eff}}=L-\Delta L\) and \(I_D\propto 1/L_{\mathrm{eff}}\). That is channel-length modulation. The threshold does not rise with \(V_{DS}\), a mobility increase is not what raises the current, and the oxide thickness does not change.",
            )),
            ("ro-r3-q2", fresh(
                3, "find_error",
                r"A worked solution doubles the width, and with it the current, of a saturated device at fixed overdrive and channel length. Exactly one step is wrong.",
                [
                    r"At fixed overdrive, doubling the width doubles the drain current.",
                    r"\(g_m=2I_D/V_{ov}\), so \(g_m\) doubles as well.",
                    r"\(r_o=1/(\lambda I_D)\), so the output resistance halves.",
                    r"The intrinsic gain \(g_mr_o\) therefore doubles.",
                ],
                3,
                r"At fixed \(V_{ov}\), \(g_m\propto I_D\) and \(r_o\propto 1/I_D\). Doubling the width and the current doubles \(g_m\) and halves \(r_o\), so \(g_mr_o\) is unchanged. The product depends only on \(\lambda\) and \(V_{ov}\). It does not double, and \(r_o\) does not stay put or double.",
                reasons=[
                    r"\(g_m\) doubles and \(r_o\) halves, so their product is unchanged.",
                    r"\(g_m\) doubles with the current and \(r_o\) is set by the channel length, so the intrinsic gain doubles.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "ss-model":
        return [
            ("ss-model-r3-q1", fresh(
                3, "sym",
                r"Write the small-signal gate-source voltage. Use vg for the movement of the gate node and vs for the movement of the source node.",
                "vg-vs",
                {"vg": (-0.04, 0.04), "vs": (-0.04, 0.04)},
                r"\(v_{gs}=v_g-v_s\). A source that rises while the gate is held still makes \(v_{gs}\) negative, not positive and not zero. Adding the two movements drops the difference, and using the source movement alone is not this definition. The sign is the usual slip when the source node, rather than the gate, carries the signal.",
                alternates=["-vs+vg", "vg+(-1)*vs"],
            )),
            ("ss-model-r1-q1", fresh(
                1, "order",
                r"Order the small-signal analysis procedure. Each step after the first uses the result of the step before it.",
                [
                    r"Solve the DC bias and confirm the region, which fixes the operating point.",
                    r"Compute \(g_m\) and \(r_o\) at that operating point.",
                    r"Replace every transistor with the linear model that uses those values, short the DC voltage sources, and open the DC current sources.",
                    r"Solve the resulting linear circuit for the gain and the port resistances.",
                ],
                r"The model parameters depend on the operating point, so the bias comes first. Drawing the linear model before the bias, or zeroing the supplies before the bias is known, leaves nothing to linearize around. The gain is not read from the DC transfer curve alone: that curve is what the bias step solves, and the small-signal result is the slope at the point.",
            )),
            ("ss-model-r1-q2", fresh(
                1, "find_error",
                r"A worked solution says what a DC supply and a DC bias current source become in the small-signal circuit. Exactly one step is wrong.",
                [
                    r"A DC source has no incremental part, so its small-signal value is zero.",
                    r"A voltage fixed at zero is a short.",
                    r"A current fixed at zero is an open.",
                    r"The supply is therefore opened, and the bias current source is shorted.",
                ],
                3,
                r"A constant voltage has zero incremental voltage, which is a short to ground. A constant current has zero incremental current, which is an open. Opening the supply, or shorting the current source, swaps those two. Both sources do not become shorts, and both do not become opens.",
                reasons=[
                    r"The voltage source becomes a short and the current source becomes an open.",
                    r"The voltage source becomes an open and the current source becomes a short.",
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
    with open(path, "w", encoding="utf-8") as f:
        json.dump(bank, f, indent=2, ensure_ascii=False)
        f.write("\n")
    deep = sum(1 for q in bank["questions"] if q["type"] in ("symbolic", "order", "error", "multi"))
    figs = sum(1 for q in bank["questions"] if q.get("figure"))
    print(f"{sid} version {bank['version']}: {deep} deep, {figs} figures, retired {len(retired)}")


def drop_grandfather():
    with open(GRAND, encoding="utf-8") as f:
        data = json.load(f)
    before = len(data["skills"])
    drop = set(SKILLS)
    data["skills"] = [sid for sid in data["skills"] if sid not in drop]
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
