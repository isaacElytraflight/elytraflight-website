#!/usr/bin/env python3
"""SG-063 IC passives: swap the most pattern-matchable MC items.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The verifier does not import this file.
"""
import json
import os

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "ic-fab",
    "sheet-res",
    "electrostatics",
    "mim-cap",
    "nl-cap",
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
    """(old mc id, replacement) in the order that assigns q4, then q5."""
    if sid == "ic-fab":
        return [
            ("ic-fab-r1-q2", fresh(
                1, "order",
                r"The substrate is already prepared. Order the making of a doped region. Each step after the first uses the result of the step before it.",
                [
                    r"Grow the oxide layer that will become the implant mask.",
                    r"Coat that oxide with photoresist and expose the resist through a mask, so the resist records where the windows belong.",
                    r"Develop the exposed resist and etch, opening windows in the oxide where the resist was removed.",
                    r"Implant through those windows, then heat the wafer so the ions that passed through the windows move onto lattice sites.",
                ],
                r"The oxide has to exist before the resist can record windows in it. The etch uses that record, and the implant uses the windows the etch opened. The heat is last because it moves the ions the implant just placed. Implanting before the windows exist would dope the whole surface.",
            )),
            ("ic-fab-r2-q3", fresh(
                2, "find_error",
                r"A positive photoresist is exposed to ultraviolet light through a mask and then developed. Exactly one step is wrong.",
                [
                    r"Ultraviolet light passes through the clear parts of the mask and hits the resist.",
                    r"The exposed resist changes chemically.",
                    r"Development removes the resist that was changed.",
                    r"The regions shaded by the mask are the ones that wash away.",
                ],
                3,
                r"Positive resist washes away where the light hit. The shaded resist was not changed, so it stays and protects the film underneath. A negative resist would reverse that. Exposure does not remove the oxide by itself; the etch does that after the resist has been developed.",
                reasons=[
                    r"Positive resist washes away where the ultraviolet light hit. The shaded resist stays.",
                    r"Exposure hardens the whole film, so none of the resist is removed.",
                ],
                correct_reason=0,
            )),
            ("ic-fab-r3-q2", fresh(
                3, "multi",
                r"Select every property that makes silicon dioxide useful while shaping a silicon wafer.",
                [
                    r"It can be grown on the silicon surface.",
                    r"It insulates.",
                    r"It conducts well enough to replace a metal interconnect.",
                    r"A thick layer of it can mask an implant.",
                ],
                [0, 1, 3],
                r"The oxide grows on the wafer, blocks current, and stops ions outside the etched windows. It is not the interconnect metal. Its permittivity is also lower than silicon's, which matters for capacitors and is not a reason to call the oxide a conductor.",
            )),
        ]
    if sid == "sheet-res":
        return [
            ("sheet-res-r1-q1", fresh(
                1, "sym",
                r"A straight rectangular body is cut from a uniform sheet. Write its resistance using the name Rs for the sheet resistance, the name L for the length, and the name W for the width.",
                "Rs*L/W",
                {"Rs": (0.2, 20), "L": (0.2, 8), "W": (0.2, 8)},
                r"The body is \(L/W\) squares, and each square contributes the sheet resistance, so the resistance is that sheet resistance times \(L/W\). A square has equal length and width, and its resistance is the sheet resistance at any size. Multiplying by the width instead of dividing by it scales the resistance the wrong way. Thickness and doping are already inside the sheet resistance.",
                alternates=["Rs*(L/W)", "(Rs*L)/W", "L*Rs/W"],
            )),
            ("sheet-res-r3-q2", fresh(
                3, "multi",
                r"Two bodies are drawn in the same sheet. Body A is \(2\ \mu\mathrm{m}\) wide and \(20\ \mu\mathrm{m}\) long. Body B is \(10\ \mu\mathrm{m}\) wide and \(100\ \mu\mathrm{m}\) long. Select every statement that is true.",
                [
                    r"Each body is 10 squares long.",
                    r"The two body resistances are equal.",
                    r"Body B covers 25 times the area of body A.",
                    r"Body B has 5 times the resistance of body A.",
                ],
                [0, 1, 2],
                r"Only \(L/W\) enters the resistance: \(20/2 = 100/10 = 10\) squares, so the resistances match. The area ratio is \((10\times 100)/(2\times 20) = 25\). The larger body is used when matching or current capacity needs the area, not when a larger resistance is needed.",
            )),
            ("sheet-res-r3-q3", fresh(
                3, "find_error",
                r"A student compares a polysilicon resistor, sitting on oxide, with a diffusion resistor when the parasitic capacitance matters. Exactly one step is wrong.",
                [
                    r"A diffusion resistor forms a junction against the substrate.",
                    r"That junction is a capacitor distributed along the resistor.",
                    r"A polysilicon film lies on the oxide, with the substrate farther away.",
                    r"The film therefore has more capacitance to the substrate than the diffusion resistor.",
                ],
                3,
                r"Moving the film onto the oxide increases the distance to the substrate and removes the junction, so the parasitic capacitance falls. That smaller capacitance is the reason to prefer the film when parasitics matter. A higher sheet resistance, or the absence of contacts, is a different claim.",
                reasons=[
                    r"The oxide increases the distance to the substrate, so the film's parasitic capacitance is smaller.",
                    r"Polysilicon needs no contacts, so it has no capacitance at all.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "electrostatics":
        return [
            ("electrostatics-r1-q1", fresh(
                1, "order",
                r"A region contains no charge. Order the reading of Poisson's equation there. Each step after the first uses the result of the step before it.",
                [
                    r"Poisson's equation sets the slope of the electric field equal to the charge density divided by the permittivity.",
                    r"With no charge, that slope is zero, so the field does not change with position.",
                    r"A field that does not change with position is a constant, and the constant may be nonzero.",
                    r"The potential's slope is the negative of that constant field, so the potential changes linearly with position.",
                ],
                r"The zero slope is Poisson's equation with the charge removed, so it uses that equation. The constant field is what a zero slope means, and the linear potential is the integral of that constant. A charge-free insulator, such as the dielectric of a charged capacitor, can hold a large uniform field. A constant potential would require the field itself to be zero.",
            )),
            ("electrostatics-r1-q2", fresh(
                1, "sym",
                r"The potential changes with position, and that slope is known. Write the electric field using the name s for the slope \(d\phi/dx\).",
                "-s",
                {"s": (-4, 4)},
                r"The field is the negative of the potential's slope, so it points from high potential toward low potential. Using the slope itself points the field uphill. A positive charge is pushed toward lower potential. Setting the field to zero whenever the slope is nonzero would erase that push.",
                alternates=["-1*s", "0-s"],
            )),
            ("electrostatics-r2-q3", fresh(
                2, "sym",
                r"No charge sits on an oxide/silicon interface. Write the oxide field using the name Esi for the silicon field, the name es for the silicon permittivity, and the name eox for the oxide permittivity.",
                "Esi*es/eox",
                {"Esi": (0.2, 6), "es": (0.5, 8), "eox": (0.4, 5)},
                r"A pillbox with no enclosed charge forces the two products of permittivity and normal field to match, so the oxide field is the silicon field times the silicon permittivity divided by the oxide permittivity. The material with the lower permittivity holds the larger field. For 11.7 and 3.9 that ratio is 3. The potential is what stays continuous. Setting the two fields equal skips the permittivities.",
                alternates=["(es/eox)*Esi", "es*Esi/eox"],
            )),
        ]
    if sid == "mim-cap":
        return [
            ("mim-cap-r1-q1", fresh(
                1, "sym",
                r"A parallel-plate capacitor has a uniform dielectric. Write its capacitance using the name eps for the permittivity, the name A for the plate area, and the name t for the dielectric thickness.",
                "eps*A/t",
                {"eps": (0.2, 6), "A": (0.2, 8), "t": (0.05, 4)},
                r"The field is the voltage divided by the thickness, and the plate charge is permittivity times field times area. Capacitance is that charge per volt, so it grows with area and permittivity and shrinks with thickness. Multiplying by the thickness, or dividing by the area, inverts the dependence.",
                alternates=["eps*(A/t)", "(eps*A)/t", "A*eps/t"],
            )),
            ("mim-cap-r1-q3", fresh(
                1, "order",
                r"Order the reason the two plates of a capacitor carry equal and opposite charge. Each step after the first uses the result of the step before it.",
                [
                    r"The insulator between the plates holds no charge.",
                    r"With no charge there, the field does not change from one plate to the other.",
                    r"The lines of that uniform field leave one plate and have nowhere to end except on the other plate.",
                    r"The charge on the second plate is therefore equal in size and opposite in sign.",
                ],
                r"The empty insulator is what makes the field uniform, and the uniform field is what forces every line that leaves one plate to end on the other. The opposite charge is that ending. Equal plate areas are not the reason, and the battery does not set a different charge on each plate.",
            )),
            ("mim-cap-r2-q3", fresh(
                2, "find_error",
                r"The dielectric of a parallel-plate capacitor is made half as thick. The applied voltage is unchanged. Exactly one step is wrong.",
                [
                    r"The capacitance is the permittivity times the area, divided by the thickness.",
                    r"Halving the thickness doubles the capacitance.",
                    r"The field in the dielectric is the voltage divided by the thickness.",
                    r"At the same voltage the field stays the same, because the voltage did not change.",
                ],
                3,
                r"The field is the voltage divided by the thickness. Halving the thickness at fixed voltage doubles the field as well as the capacitance. That is why a thinner dielectric stores more charge per volt and also reaches breakdown sooner. Leaving the field unchanged would require the voltage to be halved along with the thickness.",
                reasons=[
                    r"The field is the voltage divided by the thickness, so halving the thickness doubles the field at the same voltage.",
                    r"Halving the thickness halves the capacitance and doubles the field.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "nl-cap":
        return [
            ("nl-cap-r1-q1", fresh(
                1, "sym",
                r"A device stores charge equal to a constant times the square of the voltage. Write the small-signal capacitance at a positive bias, using the name K for that constant and the name V for the bias.",
                "2*K*V",
                {"K": (0.2, 5), "V": (0.2, 6)},
                r"The small-signal capacitance is the slope of charge versus voltage. For a constant times \(V^2\), that slope is twice the constant times \(V\). The ratio of charge to voltage is the slope of the line from the origin, and it equals the tangent only on a straight line through the origin. Using the constant alone forgets the bias.",
                alternates=["K*2*V", "(2*K)*V"],
            )),
            ("nl-cap-r1-q2", fresh(
                1, "find_error",
                r"A student compares \(Q/V\) with the small-signal capacitance of a bent charge-voltage curve. Exactly one step is wrong.",
                [
                    r"\(Q/V\) is the slope of the line from the origin to the bias point.",
                    r"\(dQ/dV\) is the slope of the tangent at the bias point.",
                    r"On a curve that bends, those two slopes are different.",
                    r"So \(Q/V\) is still the small-signal capacitance at every bias.",
                ],
                3,
                r"The two slopes agree for every bias only when the charge-voltage curve is a straight line through the origin. On a bent curve the tangent is the small-signal capacitance and the line from the origin is not. The sign of the bias does not restore the equality.",
                reasons=[
                    r"On a bent curve the tangent, not \(Q/V\), is the small-signal capacitance.",
                    r"\(Q/V\) equals the tangent whenever the bias is positive.",
                ],
                correct_reason=0,
            )),
            ("nl-cap-r3-q3", fresh(
                3, "multi",
                r"A junction capacitance is \(C_{j0}/\sqrt{1-V/\phi_b}\), with \(\phi_b>0\). The reverse bias is made stronger, so \(V\) becomes more negative. Select every statement that is true.",
                [
                    r"The capacitance decreases.",
                    r"Doubling \(\phi_b-V\) divides the capacitance by \(\sqrt{2}\), not by 2.",
                    r"The capacitance stays at \(C_{j0}\).",
                    r"The depletion layer gets wider, so the effective plate spacing grows.",
                ],
                [0, 1, 3],
                r"A more negative \(V\) makes \(1-V/\phi_b\) larger, so the capacitance shrinks, and the square root means a doubled \(\phi_b-V\) only divides the capacitance by \(\sqrt{2}\). The depletion layer is what widens. The capacitance does not stay at the zero-bias value, and it does not fall in a straight line to zero.",
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
