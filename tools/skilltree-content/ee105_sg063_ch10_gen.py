#!/usr/bin/env python3
"""SG-063 MOSFET capacitance and body effect: swap the most pattern-matchable MC items.

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

SKILLS = ["mos-caps", "body-effect"]


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
    if sid == "mos-caps":
        return [
            ("mos-caps-r1-q1", fresh(
                1, "sym",
                r"Write the gate-source capacitance of a saturated MOSFET. Use W for the width, L for the channel length, Cox for the oxide capacitance per area, and Cov for the overlap capacitance.",
                "(2/3)*W*L*Cox+Cov",
                {"W": (1, 40), "L": (0.1, 2), "Cox": (1, 20), "Cov": (0.05, 8)},
                r"In saturation the inversion charge is wedge-shaped and tied to the source, so the gate sees two thirds of \(WLC_{ox}\), plus the overlap along the source edge. Half of \(WLC_{ox}\) is the deep-triode split, not this value. Overlap alone is \(C_{gd}\) in saturation. The full \(WLC_{ox}\) would treat the channel charge as if pinch-off did not weight it toward the source.",
                alternates=["2*W*L*Cox/3+Cov", "Cov+2*W*L*Cox/3"],
            )),
            ("mos-caps-r1-q3", fresh(
                1, "order",
                r"Order the steps that say why \(C_{gd}\) of a saturated MOSFET is only overlap plus fringe. Each step after the first uses the result of the step before it.",
                [
                    r"In saturation the channel pinches off at the drain end.",
                    r"Past that pinch-off point, the inversion charge is set by the gate-source voltage.",
                    r"A change in drain-source voltage therefore does not change the channel charge.",
                    r"The remaining gate-to-drain capacitance is the overlap of the gate with the drain diffusion, plus fringe.",
                ],
                r"Past pinch-off the channel charge depends on \(V_{GS}\), not \(V_{DS}\), so the only gate-drain coupling is the gate overlapping the drain diffusion. Reverse bias of the drain to the body is what sets \(C_{db}\), not why the channel term of \(C_{gd}\) vanishes. \(C_{gd}\) is not identically zero, and the oxide is not thicker at the drain.",
            )),
            ("mos-caps-r3-q2", fresh(
                3, "find_error",
                r"A worked solution says what happens to \(C_{db}\) when the drain-body reverse bias is increased. Exactly one step is wrong.",
                [
                    r"\(C_{db}\) is the capacitance of the drain diffusion's junction to the body.",
                    r"Raising the drain-body voltage increases the reverse bias on that junction.",
                    r"The depletion region widens, and the separated charge on the two sides of the junction grows.",
                    r"Capacitance is that stored charge, so \(C_{db}\) rises with the reverse bias.",
                ],
                3,
                r"\(C_{db}\) is a reverse-biased junction capacitance, and it falls as \(1/\sqrt{1+V_{DB}/\varphi_{bi}}\). The stored charge does grow, but capacitance is the slope \(dQ/dV\), and a wider depletion region makes that slope smaller. The capacitance is not a fixed parasitic, and the junction stays reverse-biased, so this is not a forward-bias diffusion capacitance.",
                reasons=[
                    r"Capacitance is \(dQ/dV\). A wider depletion region makes that slope smaller, so \(C_{db}\) falls.",
                    r"The stored depletion charge is the capacitance, so more reverse bias raises \(C_{db}\).",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "body-effect":
        return [
            ("body-effect-r1-q3", fresh(
                1, "sym",
                r"Write \(\eta\), the factor \(g_{mb}/g_m\). Use gamma for the body-effect coefficient, phi for the positive bulk term \(-2\varphi_p\), and VSB for the source-body voltage.",
                "gamma/(2*sqrt(phi+VSB))",
                {"gamma": (0.2, 0.9), "phi": (0.4, 1.2), "VSB": (0, 4)},
                r"\(\eta=\gamma/(2\sqrt{-2\varphi_p+V_{SB}})\), which is also \(\partial V_T/\partial V_{SB}\). Then \(g_{mb}=\eta g_m\), and that derivative is \(\partial I_D/\partial V_{BS}\), so raising the body increases the current. Writing \(g_{mb}=\gamma g_m\) drops the square-root factor. Writing \(g_{mb}=g_m/\eta\) inverts it. Taking \(\partial I_D/\partial V_{SB}\) and calling the result a positive \(g_{mb}\) flips the sign, because a larger \(V_{SB}\) raises the threshold and lowers the current.",
                alternates=["(1/2)*gamma/sqrt(phi+VSB)", "gamma*(phi+VSB)**(-1/2)/2"],
            )),
            ("body-effect-r1-q2", fresh(
                1, "order",
                r"Order the steps that say why a positive source-body voltage raises an NMOS threshold. Each step after the first uses the result of the step before it.",
                [
                    r"A positive source-body voltage reverse-biases the body under the channel.",
                    r"The depletion region widens, so the bulk charge grows.",
                    r"The gate must support that extra bulk charge through the oxide before the surface inverts.",
                    r"The gate-source voltage at the onset of inversion, the threshold, therefore rises.",
                ],
                r"The body acts as a back gate. Reverse body bias adds depletion charge, which the gate must support before inversion, so \(V_T\) rises. The oxide capacitance does not fall. The source-body junction is reverse-biased, not forward-biased. The channel is not shortened; that is a different effect.",
            )),
            ("body-effect-r2-q2", fresh(
                2, "find_error",
                r"A worked solution says when the body effect drops out of an NMOS. Exactly one step is wrong.",
                [
                    r"The threshold shift and the body transconductance both require a voltage between the source and the body.",
                    r"Tying the source to the body holds \(V_{SB}\) at zero and holds \(v_{bs}\) at zero.",
                    r"The threshold then stays at \(V_{T0}\), and \(g_{mb}v_{bs}\) drops out of the small-signal model.",
                    r"Grounding the body does the same for every source voltage, because a grounded body forces \(V_{SB}\) to zero.",
                ],
                3,
                r"With the body at ground, a source above ground still has \(V_{SB}>0\), and a signal on that source still produces \(v_{bs}\). Only tying the source to the body removes both. Saturation does not remove the shift, and a large \(r_o\) does not either.",
                reasons=[
                    r"A source above a grounded body still has \(V_{SB}>0\), and a signal on that source still produces \(v_{bs}\).",
                    r"A grounded body forces \(V_{SB}\) to zero no matter where the source sits, so the body effect is absent.",
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
