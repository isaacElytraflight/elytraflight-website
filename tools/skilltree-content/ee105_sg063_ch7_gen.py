#!/usr/bin/env python3
"""SG-063 MOS capacitor: swap the most pattern-matchable MC items.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Retiring vt-r2-q3 also drops the live figure whose label sits above the
view box. Does not write explainers. The verifier does not import this file.
"""
import json
import os

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = ["mos-struct", "mos-regions", "vt", "mos-fields", "mos-cv"]


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
    if sid == "mos-struct":
        return [
            ("mos-struct-r1-q2", fresh(
                1, "sym",
                r"Write the oxide capacitance per unit area, using the name eox for the oxide permittivity and the name tox for the oxide thickness.",
                "eox/tox",
                {"eox": (0.2, 5), "tox": (0.05, 4)},
                r"The oxide is the insulator between two conductors, so its capacitance per area is its permittivity divided by its thickness. A thinner oxide is a larger capacitance. The oxide blocks DC current; it does not block the field that this capacitance describes.",
                alternates=["eox*(1/tox)", "(eox)/tox"],
            )),
            ("mos-struct-r2-q3", fresh(
                2, "order",
                r"The applied gate-to-body voltage is zero. Order the steps that say why the silicon surface is still depleted. Each step after the first uses the result of the step before it.",
                [
                    r"The n+ gate's Fermi level sits above the p-body's Fermi level.",
                    r"Electrons flow from the gate to the body until those two Fermi levels line up.",
                    r"That flow leaves the gate positive and uncovers acceptors at the silicon surface.",
                    r"Those uncovered acceptors are a depletion layer, so the surface is depleted at zero applied voltage.",
                ],
                r"Zero applied voltage is not flat band. The work-function difference moves electrons off the gate, the gate stays positive, and the matching negative charge is uncovered acceptor ions at the surface.",
            )),
            ("mos-struct-r3-q3", fresh(
                3, "find_error",
                r"A worked solution says whether the gate can change the silicon under the oxide. Exactly one step is wrong.",
                [
                    r"The oxide blocks DC current between the gate and the body.",
                    r"It does not block the electric field of the charge on the gate.",
                    r"That field induces an equal and opposite charge in the silicon.",
                    r"The gate voltage therefore cannot change the carrier density at the silicon surface.",
                ],
                3,
                r"An insulator blocks current, not field. The induced silicon charge is holes in accumulation, uncovered acceptors in depletion, or electrons in inversion, so the gate does change the surface carriers.",
                reasons=[
                    r"The induced charge is a change in the surface carriers, so the gate does control the silicon.",
                    r"Blocking the current also blocks the field, so the surface carriers are unaffected.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "mos-regions":
        return [
            ("mos-regions-r3-q2", fresh(
                3, "sym",
                r"Write the electron concentration at the silicon surface, using the name ni for the intrinsic concentration, the name phis for the surface potential, and the name Vt for \(kT/q\).",
                "ni*exp(phis/Vt)",
                {"ni": (0.2, 4), "phis": (-0.3, 0.3), "Vt": (0.025, 0.05)},
                r"Electrons follow the potential: the surface concentration is the intrinsic concentration times \(e^{\varphi_s/V_t}\). It equals the bulk doping when the surface potential is the negative of the bulk potential, which is the inversion condition. At zero surface potential the surface is only intrinsic.",
                alternates=["ni*e**(phis/Vt)", "exp(phis/Vt)*ni"],
            )),
            ("mos-regions-r1-q1", fresh(
                1, "order",
                r"An n+ poly gate sits on p-type silicon. Order the regions as the gate voltage rises. Each step after the first uses the result of the step before it.",
                [
                    r"Below flat band the gate is negative enough to pull majority holes to the surface.",
                    r"That hole sheet is accumulation, and it ends when the gate voltage reaches flat band.",
                    r"Above flat band the holes leave, and a depletion layer of uncovered acceptors grows.",
                    r"Once the surface electron density reaches the bulk doping, further gate charge goes into an inversion layer of electrons.",
                ],
                r"Accumulation, depletion, then inversion. The hole sheet ends at flat band, the uncovered acceptors grow after that, and inversion starts when the surface is as n-type as the bulk is p-type.",
            )),
            ("mos-regions-r3-q1", fresh(
                3, "find_error",
                r"A worked solution says where extra gate charge goes once the device is past threshold. Exactly one step is wrong.",
                [
                    r"Past threshold, extra gate voltage barely moves the surface potential.",
                    r"The depletion depth is set by that surface potential.",
                    r"The depletion depth therefore stays nearly pinned.",
                    r"The added gate charge still goes into making the depletion layer deeper.",
                ],
                3,
                r"With the surface potential pinned, the depletion depth is pinned too. The extra gate charge is matched by inversion electrons at the surface, not by a deeper layer of uncovered acceptors.",
                reasons=[
                    r"The pinned depletion depth means the extra charge is inversion electrons at the surface.",
                    r"Gate charge above threshold keeps uncovering acceptors, so the depletion layer keeps growing.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "vt":
        return [
            ("vt-r1-q1", fresh(
                1, "sym",
                r"The bulk potential of the p-type body is negative. Write the threshold voltage, using the name VFB for the flat-band voltage, the name phip for that bulk potential, the name Cox for the oxide capacitance per area, the name q for the elementary charge, the name es for the silicon permittivity, and the name NA for the acceptor concentration.",
                "VFB-2*phip+(1/Cox)*sqrt(2*q*es*NA*(-2*phip))",
                {"VFB": (-1, 0.2), "phip": (-0.6, -0.2), "Cox": (0.4, 4), "q": (0.2, 3), "es": (0.4, 4), "NA": (0.4, 6)},
                r"Threshold is three pieces: the flat-band voltage, the band bending \(-2\varphi_p\) (positive, because \(\varphi_p\) is negative), and the oxide drop that supports the depletion charge. That oxide drop is the depletion-charge magnitude divided by the oxide capacitance.",
                alternates=["VFB-2*phip+sqrt(2*q*es*NA*(-2*phip))/Cox"],
            )),
            ("vt-r2-q3", fresh(
                2, "sym",
                r"Write the oxide-voltage term of the threshold, using the name QB for the magnitude of the depletion charge per area and the name Cox for the oxide capacitance per area.",
                "QB/Cox",
                {"QB": (0.2, 6), "Cox": (0.2, 5)},
                r"Supporting the depletion charge takes a voltage equal to that charge divided by the oxide capacitance. Halving the oxide thickness doubles the capacitance, so this term halves. The flat-band voltage and the band bending do not depend on the thickness.",
                alternates=["QB*(1/Cox)", "(1/Cox)*QB"],
            )),
            ("vt-r3-q2", fresh(
                3, "find_error",
                r"A worked solution writes the band-bending term of the threshold for p-type silicon. Exactly one step is wrong.",
                [
                    r"For p-type silicon the bulk potential is negative.",
                    r"Threshold bends the surface from that bulk potential to the negative of the bulk potential.",
                    r"The bend is minus twice the bulk potential, and that quantity is positive.",
                    r"The threshold formula therefore adds twice the bulk potential itself.",
                ],
                3,
                r"Adding twice a negative bulk potential subtracts a positive voltage. The bend from \(\varphi_p\) to \(-\varphi_p\) is \(-2\varphi_p\), which is positive and must be added.",
                reasons=[
                    r"The bend is minus twice the bulk potential, so adding twice the bulk potential itself has the wrong sign.",
                    r"Twice the bulk potential is already positive, so adding it is the right band bending.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "mos-fields":
        return [
            ("mos-fields-r1-q2", fresh(
                1, "sym",
                r"No charge sits on the oxide-silicon interface. Write the silicon field, using the name Eox for the oxide field, the name eox for the oxide permittivity, and the name es for the silicon permittivity.",
                "Eox*eox/es",
                {"Eox": (0.2, 6), "eox": (0.2, 5), "es": (0.4, 6)},
                r"With no sheet charge, permittivity times normal field is the same on both sides. Silicon's larger permittivity means a smaller field. The potential is what stays continuous; the field jumps.",
                alternates=["Eox*(eox/es)", "(eox/es)*Eox"],
            )),
            ("mos-fields-r2-q3", fresh(
                2, "order",
                r"Order the steps that give the shape of the potential in the silicon depletion region. Each step after the first uses the result of the step before it.",
                [
                    r"Uncovered acceptors fill the depletion region at a uniform density.",
                    r"That uniform charge makes the field fall in a straight line from its peak at the surface to zero at the depletion edge.",
                    r"The potential drop is the area under that straight-line field, which is a triangle.",
                    r"A potential whose slope is that triangle is a parabola from the surface down to the depletion edge.",
                ],
                r"Uniform charge makes a linear field, and the integral of a linear field is a parabola. In the charge-free oxide the field is constant, so the potential there is a straight line.",
            )),
            ("mos-fields-r3-q2", fresh(
                3, "find_error",
                r"A worked solution replaces the oxide with a dielectric of higher permittivity, at the same silicon surface field. Exactly one step is wrong.",
                [
                    r"No sheet charge sits on the dielectric-silicon boundary.",
                    r"Permittivity times normal field is therefore the same on both sides.",
                    r"The new dielectric has a larger permittivity than the oxide, and the silicon field is unchanged.",
                    r"The field inside the new dielectric is therefore larger than the oxide field was.",
                ],
                3,
                r"The same product of permittivity and field, with a larger permittivity, means a smaller field. A higher-permittivity dielectric drops less voltage for the same silicon field.",
                reasons=[
                    r"A larger permittivity at the same product means a smaller field in the dielectric.",
                    r"A larger permittivity needs a larger field to match the silicon side.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "mos-cv":
        return [
            ("mos-cv-r1-q2", fresh(
                1, "sym",
                r"Write the capacitance per unit area in depletion, using the name Cox for the oxide capacitance per area, the name es for the silicon permittivity, and the name Xd for the depletion depth.",
                "1/(1/Cox+Xd/es)",
                {"Cox": (0.2, 5), "es": (0.2, 5), "Xd": (0.1, 4)},
                r"The oxide and the depletion layer are two dielectrics in series. The depletion capacitance per area is the silicon permittivity divided by the depletion depth, and series capacitances add as reciprocals.",
                alternates=["(1/Cox+Xd/es)**(-1)", "1/(Xd/es+1/Cox)"],
            )),
            ("mos-cv-r3-q1", fresh(
                3, "order",
                r"Order the steps that say how the capacitance changes from flat band to threshold. Each step after the first uses the result of the step before it.",
                [
                    r"From flat band toward threshold the band bending in the silicon increases.",
                    r"The depletion depth grows as the square root of that band bending.",
                    r"Depletion capacitance is the silicon permittivity divided by that depth, so a larger depth is a smaller depletion capacitance.",
                    r"That depletion capacitance is in series with the oxide, so the measured capacitance falls from the oxide value.",
                ],
                r"A deeper depletion layer is a smaller series capacitor, so the measured capacitance falls from the oxide value at flat band toward its minimum at threshold. It does not stay at the oxide value, and it does not fall in a straight line to zero.",
            )),
            ("mos-cv-r3-q3", fresh(
                3, "find_error",
                r"A worked solution compares a thicker oxide with the same doping. Exactly one step is wrong.",
                [
                    r"A thicker oxide has a smaller oxide capacitance.",
                    r"The minimum capacitance is the series combination of that oxide capacitance and the depletion capacitance.",
                    r"Making the oxide capacitance smaller lets the oxide dominate that series combination.",
                    r"The ratio of the minimum capacitance to the oxide capacitance therefore gets smaller.",
                ],
                3,
                r"When the oxide dominates the series combination, the depletion layer changes the total less. The ratio of the minimum to the oxide capacitance moves closer to 1, so the relative dip is shallower, and the oxide plateau itself is lower.",
                reasons=[
                    r"Oxide dominance makes the ratio closer to 1, so the relative dip is shallower.",
                    r"A smaller oxide capacitance deepens the relative dip.",
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
    drop = set(SKILLS)
    data["skills"] = [sid for sid in data["skills"] if sid not in drop]
    with open(GRAND, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("grandfather", len(data["skills"]))


def main():
    for sid in SKILLS:
        apply_skill(sid)
    drop_grandfather()


if __name__ == "__main__":
    main()
