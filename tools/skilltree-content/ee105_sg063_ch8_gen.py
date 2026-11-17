#!/usr/bin/env python3
"""SG-063 MOSFET device physics: swap the most pattern-matchable MC items.

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

SKILLS = ["mosfet-struct", "nmos-regions", "triode", "square-law", "pmos"]


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
    """(old mc id, replacement) in the order that assigns q4, then q5."""
    if sid == "mosfet-struct":
        return [
            ("mosfet-struct-r1-q2", fresh(
                1, "sym",
                r"Two NMOS transistors have the same gate, drain, and source voltages. Write the ratio of the second drain current to the first. Use W1 and L1 for the first device's width and length, and W2 and L2 for the second.",
                "W2*L1/(W1*L2)",
                {"W1": (0.4, 8), "L1": (0.1, 2), "W2": (0.4, 8), "L2": (0.1, 2)},
                r"At a fixed bias the drain current scales with \(W/L\). \(L\) is the source-to-drain distance under the gate, and \(W\) is the width across the current. The ratio of the currents is therefore the ratio of the two aspect ratios. Using width alone, or using the gate area \(WL\), answers a different question: area sets the oxide capacitance, not the current.",
                alternates=["(W2/L2)/(W1/L1)", "(W2*L1)/(L2*W1)"],
            )),
            ("mosfet-struct-r2-q2", fresh(
                2, "order",
                r"An NMOS sits in a p-type body. Order the steps that say why that body is tied to the lowest supply. Each step after the first uses the result of the step before it.",
                [
                    r"The source and the drain are n+ regions in the p-type body.",
                    r"Each of those n+ regions forms a pn junction with the body.",
                    r"A pn junction stays reverse biased only when the body is at or below both n+ voltages.",
                    r"Tying the body to the lowest supply keeps both junctions reverse biased for every allowed source and drain voltage.",
                ],
                r"The body tie is a junction constraint. It does not turn the channel on, and it does not set the oxide capacitance. The gate does that. Putting the body above a source or drain node forward-biases that junction, so the body has to be the lowest node.",
            )),
            ("mosfet-struct-r3-q2", fresh(
                3, "find_error",
                r"A worked solution says how to tell the source from the drain of a symmetric NMOS. Exactly one step is wrong.",
                [
                    r"The layout places an n+ region at each end of the gate.",
                    r"Those two regions are doped the same way, so the layout does not mark one of them as the source.",
                    r"Electrons enter the channel from the n+ region that sits at the lower potential.",
                    r"That lower-potential region is the drain.",
                ],
                3,
                r"The layout is symmetric. Electrons come from the n+ end at the lower potential, and that end is the source. Calling it the drain reverses the terminal names. The symbol arrow does not pick the source of a symmetric device; the voltages do.",
                reasons=[
                    r"The lower-potential n+ region supplies the electrons, so it is the source.",
                    r"The lower-potential end is the drain, because that is where the current leaves the channel.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "nmos-regions":
        return [
            ("nmos-regions-r3-q2", fresh(
                3, "sym",
                r"Write the smallest drain-source voltage that puts an NMOS into saturation. Use Vgs for the gate-source voltage and Vt for the threshold.",
                "Vgs-Vt",
                {"Vgs": (0.9, 2.4), "Vt": (0.15, 0.7)},
                r"Saturation starts when \(V_{DS}\) reaches the overdrive \(V_{GS}-V_T\). Below that voltage the inversion layer still reaches the drain, which is triode. Using \(V_{GS}\) itself, or the threshold alone, puts the boundary at the wrong place. The same test written on the nodes is \(V_D \ge V_G - V_T\): the drain may sit up to one threshold below the gate.",
                alternates=["-Vt+Vgs", "Vgs+(-1)*Vt"],
            )),
            ("nmos-regions-r2-q2", fresh(
                2, "order",
                r"The gate-source voltage is fixed above threshold. Order the regions as the drain-source voltage rises from zero. Each step after the first uses the result of the step before it.",
                [
                    r"At zero drain-source voltage the channel is a uniform sheet, so the current starts with a straight rise.",
                    r"That straight rise is the deep-triode part of the triode region.",
                    r"As the drain-source voltage approaches the overdrive, the drain end of the channel thins and the curve bends.",
                    r"Once the drain-source voltage passes the overdrive, the channel pinches off and the current saturates.",
                ],
                r"An on device is not saturated at small \(V_{DS}\). It is a resistor first, then the curve bends, and only past \(V_{ov}\) does it saturate. Starting in saturation and moving into triode runs that sequence backwards. Cut-off is not in this sweep, because the gate is already above threshold.",
            )),
            ("nmos-regions-r3-q1", fresh(
                3, "find_error",
                r"A worked solution places the source above ground and decides the region from the node voltages. Exactly one step is wrong.",
                [
                    r"The gate-source voltage is the gate node minus the source node.",
                    r"The drain-source voltage is the drain node minus the source node.",
                    r"The overdrive is that gate-source voltage minus the threshold.",
                    r"The device is saturated only when the drain node is above the gate node.",
                ],
                3,
                r"Region tests use \(V_{GS}\) and \(V_{DS}\), not the node voltages measured to ground. Saturation is \(V_{DS} \ge V_{GS}-V_T\), which is \(V_D \ge V_G - V_T\). The drain can sit as much as one threshold below the gate and the device is still saturated. Requiring the drain to be above the gate marks some saturated biases as triode.",
                reasons=[
                    r"Saturation allows the drain to sit as much as one threshold below the gate.",
                    r"The drain has to be above the gate, or the device is in triode.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "triode":
        return [
            ("triode-r2-q2", fresh(
                2, "sym",
                r"Write the deep-triode on-resistance, for a drain-source voltage much smaller than the overdrive. Use unCox for the product of electron mobility and oxide capacitance per area, WL for the ratio of width to length, and Vov for the overdrive.",
                "1/(unCox*WL*Vov)",
                {"unCox": (0.2, 4), "WL": (1, 40), "Vov": (0.15, 1.6)},
                r"In deep triode the channel is a uniform sheet whose charge is proportional to the overdrive, so the conductance is \(\mu_n C_{ox}(W/L)V_{ov}\). Resistance is the reciprocal, and it falls as \(1/V_{ov}\), not as \(1/V_{ov}^2\). Raising the gate adds inversion charge and lowers \(R_{on}\). Dropping \(W/L\), or squaring the overdrive, uses the saturation current instead of this conductance.",
                alternates=["(unCox*WL*Vov)**(-1)", "1/(WL*unCox*Vov)"],
            )),
            ("triode-r3-q3", fresh(
                3, "order",
                r"Order the steps that turn the local channel current into the triode formula. Each step after the first uses the result of the step before it.",
                [
                    r"At a point along the channel, the inversion charge per area is the oxide capacitance times \(V_{GS} - V - V_T\).",
                    r"The drift current is that charge, times the mobility, times the electric field, times the width.",
                    r"The field is the slope of the channel potential, so the current is \(\mu_n C_{ox} W (V_{GS}-V-V_T)\) times \(dV/dy\).",
                    r"Integrating from source to drain turns that into \(\mu_n C_{ox}(W/L)(V_{ov}-V_{DS}/2)V_{DS}\).",
                ],
                r"The triode law is an integral of drift current along the channel. Diffusion along the channel, or a displacement current \(C\,dV/dt\), is a different mechanism and does not produce the \((V_{ov}-V_{DS}/2)V_{DS}\) factor. The integral has to come last, after the local charge and the field are named.",
            )),
            ("triode-r1-q3", fresh(
                1, "find_error",
                r"A worked solution says why the triode current bends downward as the drain-source voltage grows. Exactly one step is wrong.",
                [
                    r"At a point in the channel, the gate-to-channel voltage is \(V_{GS}\) minus the local channel potential.",
                    r"Inversion charge is the oxide capacitance times the excess of that voltage over the threshold.",
                    r"The channel potential is higher toward the drain, so the inversion charge is thinner there.",
                    r"The curve therefore bends down because the threshold voltage rises with \(V_{DS}\).",
                ],
                3,
                r"The local inversion charge is \(C_{ox}(V_{GS}-V(y)-V_T)\). A higher channel potential near the drain means less charge there, so the average conductance falls. That is the \(-V_{DS}/2\) term. In this model the threshold does not rise with \(V_{DS}\), and a mobility drop is not what bends the curve.",
                reasons=[
                    r"The bend is the thinner inversion charge near the drain. The threshold is not what changes.",
                    r"A threshold that rises with \(V_{DS}\) is what pulls the current below the straight line.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "square-law":
        return [
            ("square-law-r2-q1", fresh(
                2, "sym",
                r"Write the mobile inversion charge per unit area at a point in the channel. Use Cox for the oxide capacitance per area, Vgs for the gate-source voltage, Vy for the channel potential at that point, and Vt for the threshold.",
                "-Cox*(Vgs-Vy-Vt)",
                {"Cox": (0.3, 4), "Vgs": (1.2, 2.6), "Vy": (0.05, 0.45), "Vt": (0.15, 0.45)},
                r"The gate sees \(V_{GS}-V(y)\) across the oxide, and only the excess over \(V_T\) is inversion charge. The charge is negative because the carriers are electrons. Using \(-C_{ox}(V_{GS}-V_T)\) everywhere drops the channel potential, so the charge would not fall toward the drain. Using \(-C_{ox}V(y)\) keeps the channel potential and drops the gate. The depletion charge \(-qN_AX_d\) is a different sheet.",
                alternates=["-(Cox*(Vgs-Vy-Vt))", "Cox*(Vy+Vt-Vgs)"],
            )),
            ("square-law-r2-q3", fresh(
                2, "order",
                r"Order the steps that produce the factor of one half in the saturation current. Each step after the first uses the result of the step before it.",
                [
                    r"From the source to the pinch-off point, the channel potential rises from zero to the overdrive.",
                    r"The inversion charge falls in a straight line from \(C_{ox}V_{ov}\) at the source to zero at pinch-off.",
                    r"The average of a straight line that falls to zero is half of its value at the start.",
                    r"Integrating \((V_{ov}-V)\,dV\) from zero to \(V_{ov}\) therefore gives \(V_{ov}^2/2\).",
                ],
                r"The one half is the average of a charge that falls from \(C_{ox}V_{ov}\) to zero. It is not one half because the channel has two ends, and it is not because half the carriers are holes. The integral has to come after the charge profile, because the profile is what gets integrated.",
            )),
            ("square-law-r1-q3", fresh(
                1, "find_error",
                r"A worked solution states the gate-to-drain voltage at pinch-off, and the charge there. Exactly one step is wrong.",
                [
                    r"Pinch-off is the bias where \(V_{DS}\) equals \(V_{GS}-V_T\).",
                    r"The gate-to-drain voltage is \(V_{GS}\) minus \(V_{DS}\).",
                    r"At that bias the gate-to-drain voltage equals the threshold.",
                    r"The inversion charge at the drain end is then \(C_{ox}\) times the overdrive.",
                ],
                3,
                r"At pinch-off \(V_{GD}=V_{GS}-V_{DS}=V_T\), so the excess over threshold at the drain end is zero and the inversion layer vanishes there. \(C_{ox}V_{ov}\) is the charge at the source, not at the pinched-off end. The current does not stop: carriers are swept across the high-field region into the drain.",
                reasons=[
                    r"The drain end is exactly at threshold, so the inversion charge there is zero.",
                    r"Pinch-off leaves a full \(C_{ox}V_{ov}\) of inversion charge at the drain end.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "pmos":
        return [
            ("pmos-r1-q1", fresh(
                1, "sym",
                r"Write the smallest source-drain voltage that keeps a PMOS in saturation. Use Vsg for the source-gate voltage and Vtp for the magnitude of the threshold. Both names are positive.",
                "Vsg-Vtp",
                {"Vsg": (0.7, 2.2), "Vtp": (0.15, 0.55)},
                r"With source-referenced positive voltages, saturation starts at \(V_{SD}=V_{SG}-|V_{Tp}|\), the same overdrive rule as an NMOS. Adding the threshold instead of subtracting it, or requiring \(V_{SD}\ge V_{SG}\), uses the wrong boundary. The drain of a saturated PMOS may sit up to one threshold above the gate, which is \(V_D \le V_G+|V_{Tp}|\).",
                alternates=["-Vtp+Vsg", "Vsg+(-1)*Vtp"],
            )),
            ("pmos-r1-q3", fresh(
                1, "order",
                r"A PMOS source is fixed at the positive supply. Order the wiggle test for a small rise in the gate voltage. Each step after the first uses the result of the step before it.",
                [
                    r"The source voltage stays put while the gate voltage rises.",
                    r"The source-gate voltage therefore falls by that same rise.",
                    r"Less source-gate voltage means less inversion charge, so the drain current falls.",
                    r"The small-signal current has the sign of \(v_{sg}\), which is negative for this rise.",
                ],
                r"Raising the gate of a PMOS weakens the channel. The current falls. Treating the device like an NMOS, and letting the current rise, skips the drop in \(V_{SG}\). The supply is fixed, so the source does not move with the gate, and the current does not reverse direction.",
            )),
            ("pmos-r2-q2", fresh(
                2, "find_error",
                r"A worked solution builds the small-signal model of a saturated PMOS. Exactly one step is wrong.",
                [
                    r"With the source at the top, the controlling voltage is \(v_{sg}\).",
                    r"The controlled source pushes a current \(g_m v_{sg}\) from the source toward the drain.",
                    r"Turned over, that element is \(g_m v_{gs}\) from drain to source, the same element an NMOS uses.",
                    r"Because the device is a PMOS, the value of \(g_m\) in that element is negative.",
                ],
                3,
                r"The PMOS model drawn upside down is the NMOS model. \(g_m v_{sg}\) from source to drain is the same as \(g_m v_{gs}\) from drain to source, and \(g_m\) is positive. A minus sign on \(g_m\), on top of the flipped drawing, counts the polarity twice. \(r_o\) still sits between drain and source.",
                reasons=[
                    r"\(g_m\) stays positive. The source-referenced voltage already carries the PMOS sign.",
                    r"A PMOS needs a negative \(g_m\), with the NMOS model otherwise left as it is.",
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
