#!/usr/bin/env python3
"""SG-063 PN equilibrium: swap the most pattern-matchable MC items.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

The one-sided reverse-bias charge plot is redrawn so its N-side block stays
inside the view box. Does not write explainers. The verifier does not import
this file.
"""
import json
import os
import sys

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "carrier-pot",
    "pn-overview",
    "depl-approx",
    "contact-pot",
    "rev-bias",
    "junction-cap",
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
    if sid == "carrier-pot":
        return [
            ("carrier-pot-r1-q3", fresh(
                1, "sym",
                r"In equilibrium the electron concentration rises by a factor of ten. Write the change in potential, using the name Vt for \(kT/q\).",
                "Vt*ln(10)",
                {"Vt": (0.02, 0.05)},
                r"\(n = n_i e^{\varphi/V_t}\), so a factor of ten in \(n\) needs \(\Delta\varphi = V_t\ln 10\). That is about 60 mV at room temperature. \(V_t\) itself, about 26 mV, is the change for a factor of \(e\), not a factor of ten.",
                alternates=["Vt*log(10)", "ln(10)*Vt"],
            )),
            ("carrier-pot-r2-q3", fresh(
                2, "sym",
                r"Point B is higher in equilibrium potential than point A. Write the ratio of the electron concentration at B to the electron concentration at A. Use the name dphi for that potential difference and the name Vt for \(kT/q\).",
                "exp(dphi/Vt)",
                {"dphi": (0.02, 0.25), "Vt": (0.02, 0.05)},
                r"\(n = n_i e^{\varphi/V_t}\), so \(n_B/n_A = e^{(\varphi_B-\varphi_A)/V_t}\). Equilibrium does not require the concentration to be the same everywhere; the potential difference sets the ratio. A 120 mV difference is about a hundredfold ratio.",
                alternates=["e**(dphi/Vt)"],
            )),
            ("carrier-pot-r3-q3", fresh(
                3, "find_error",
                r"A worked solution explains why electrons collect at the high-potential point. Exactly one step is wrong.",
                [
                    r"An electron's charge is \(-q\).",
                    r"Its potential energy is that charge times the potential, so \(-q\varphi\).",
                    r"Raising \(\varphi\) therefore lowers the electron's energy.",
                    r"Electrons avoid the high-potential point, because a high potential means a high energy for them.",
                ],
                3,
                r"The first three steps are the chain: negative charge, energy \(-q\varphi\), and a lower energy where \(\varphi\) is higher. The last step reverses that conclusion. Electrons collect at high potential, and holes collect at low potential.",
                reasons=[
                    r"The energy is \(-q\varphi\), so the high-potential point is the low-energy point and electrons collect there.",
                    r"Electrons avoid high potential because \(-q\varphi\) is larger there.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "pn-overview":
        return [
            ("pn-overview-r2-q3", fresh(
                2, "sym",
                r"Inside the junction transition region the charge density is \(\rho\). Write \(\rho/q\) using the name p for the hole concentration, n for the electron concentration, ND for the ionized donor concentration, and NA for the ionized acceptor concentration.",
                "p-n+ND-NA",
                {"p": (0.2, 8), "n": (0.2, 8), "ND": (0.2, 8), "NA": (0.2, 8)},
                r"Every hole and every uncovered donor contributes \(+q\); every electron and every uncovered acceptor contributes \(-q\). So \(\rho/q = p - n + N_D - N_A\). On the P side, \(p < N_A\) leaves a negative density; on the N side, \(n < N_D\) leaves a positive density. The whole junction can still be neutral.",
                alternates=["p+ND-n-NA", "-n+p-NA+ND"],
            )),
            ("pn-overview-r2-q1", fresh(
                2, "find_error",
                r"A worked solution says which currents cancel in an equilibrium junction. Exactly one step is wrong.",
                [
                    r"In equilibrium the electron current is separately zero.",
                    r"Electron drift therefore cancels electron diffusion.",
                    r"The hole current is also separately zero, so hole drift cancels hole diffusion.",
                    r"Electron diffusion instead cancels hole diffusion, and the two drifts cancel each other.",
                ],
                3,
                r"Equilibrium sets each carrier's current to zero on its own. Drift of one carrier cancels diffusion of that same carrier. A nonzero pair with the electron current only the negative of the hole current would still move charge around the device.",
                reasons=[
                    r"Each carrier's drift cancels that same carrier's diffusion. An electron current that is only the negative of the hole current is not equilibrium.",
                    r"The two diffusion currents cancel each other, and the two drift currents cancel each other.",
                ],
                correct_reason=0,
            )),
            ("pn-overview-r1-q2", fresh(
                1, "order",
                r"The P side is on the left and the N side is on the right. Order the steps that give the built-in field direction. Each step after the first uses the result of the step before it.",
                [
                    r"Leaving majority carriers uncovers positive donor ions on the N side and negative acceptor ions on the P side.",
                    r"Field lines start on those positive ions and end on those negative ions.",
                    r"With the P side on the left, those lines point to the left.",
                    r"A field pointing to the left pushes holes back toward the P side and electrons back toward the N side.",
                ],
                r"The uncovered ions are a dipole, positive on the N side. The field points from that positive charge toward the negative charge on the P side, so it points left and returns each carrier to its own side.",
            )),
        ]
    if sid == "depl-approx":
        return [
            ("depl-approx-r1-q1", fresh(
                1, "order",
                r"Order the consequences of the depletion approximation. Each step after the first uses the result of the step before it.",
                [
                    r"Inside the depletion region the free carriers are removed.",
                    r"The charge density there is the uncovered ions: \(-qN_A\) on the P side and \(+qN_D\) on the N side.",
                    r"That piecewise-constant charge density makes the electric field piecewise linear.",
                    r"The piecewise-linear field makes the potential piecewise quadratic.",
                ],
                r"Removing the carriers leaves the dopant ions. Poisson's equation then makes the field linear on each side, zero at both edges and largest at the junction, and the potential is the integral of that field.",
            )),
            ("depl-approx-r3-q1", fresh(
                3, "sym",
                r"Write the ratio of the N-side depletion width to the P-side depletion width. Use the name NA for the acceptor concentration and the name ND for the donor concentration.",
                "NA/ND",
                {"NA": (0.2, 8), "ND": (0.2, 8)},
                r"The two sides hold equal and opposite charge, so \(N_A x_p = N_D x_n\). The width ratio is therefore \(x_n/x_p = N_A/N_D\). The lightly doped side is the wide side. Equal charge does not mean equal width.",
                alternates=["NA*(1/ND)"],
            )),
            ("depl-approx-r3-q3", fresh(
                3, "find_error",
                r"A worked solution says which side of the junction takes most of the built-in potential. Exactly one step is wrong.",
                [
                    r"The peak field is the height of the voltage triangle on both sides.",
                    r"Each side's potential drop is half that peak field times that side's width.",
                    r"Because the drop is proportional to the width, the larger drop is on the wider side, and that wider side is the lightly doped one.",
                    r"Most of the built-in potential therefore falls on the heavily doped side.",
                ],
                3,
                r"The two voltage triangles share the peak field, so the potential split equals the width split. The lightly doped side is both wider and the side that holds most of the built-in potential.",
                reasons=[
                    r"The potential split follows the widths, so most of the built-in potential falls on the lightly doped side.",
                    r"Equal charge on the two sides puts most of the potential on the heavily doped side.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "contact-pot":
        return [
            ("contact-pot-r3-q1", fresh(
                3, "sym",
                r"Write the built-in potential of a PN junction in equilibrium. Use the name Vt for \(kT/q\), the name NA for the acceptor concentration, the name ND for the donor concentration, and the name ni for the intrinsic concentration.",
                "Vt*ln(NA*ND/(ni*ni))",
                {"Vt": (0.02, 0.05), "NA": (2, 8), "ND": (2, 8), "ni": (0.2, 1)},
                r"Each side's potential relative to intrinsic material is \(V_t\ln(N/n_i)\), and the built-in potential is the difference: \(V_t\ln(N_A N_D/n_i^2)\). Moving the zero of potential changes both sides by the same amount, so the difference does not change.",
                alternates=["Vt*ln(ND*NA/(ni**2))", "Vt*log(NA*ND/(ni*ni))"],
            )),
            ("contact-pot-r3-q3", fresh(
                3, "multi",
                r"Select every statement that is true of contact potentials in equilibrium.",
                [
                    r"A PN junction has a contact potential.",
                    r"A metal-semiconductor contact has a contact potential.",
                    r"An ohmic contact has no contact potential.",
                    r"Around a closed loop the contact potentials sum to zero.",
                ],
                [0, 1, 3],
                r"Every junction of dissimilar materials has a contact potential, including an ohmic contact. The ohmic contact is built so it does not rectify; the potential is still there. In equilibrium those potentials sum to zero around any loop, which is why a PN junction alone is not a battery.",
            )),
            ("contact-pot-r1-q3", fresh(
                1, "find_error",
                r"A worked solution says what an ideal voltmeter reads across an open PN junction. Exactly one step is wrong.",
                [
                    r"The built-in potential is a real potential step inside the junction.",
                    r"Each meter probe adds its own metal-semiconductor contact to that same loop.",
                    r"Those contact potentials cancel the built-in step, so the loop sum is zero.",
                    r"The meter therefore reads the built-in potential.",
                ],
                3,
                r"The step inside the junction is real, and so are the probe contacts. They cancel around the loop. An ideal voltmeter on an equilibrium junction reads zero, not the built-in potential.",
                reasons=[
                    r"The contact potentials cancel the built-in potential, so the meter reads zero.",
                    r"The probes are metal, so they add nothing and the meter reads the built-in potential.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "rev-bias":
        return [
            ("rev-bias-r1-q1", fresh(
                1, "order",
                r"A PN junction is reverse biased. Order the steps that say what happens to the depletion region. Each step after the first uses the result of the step before it.",
                [
                    r"Reverse bias increases the potential step the junction must support.",
                    r"With almost no current, that extra step cannot be dropped in the neutral regions.",
                    r"The depletion region uncovers more ion charge so the field can hold the larger step.",
                    r"Uncovering more ion charge means the depletion region widens.",
                ],
                r"The total step is the built-in potential minus the applied voltage, and reverse bias makes that applied voltage negative, so the step is larger than the built-in potential. More uncovered charge is the only way to hold it, and more charge means a wider depletion region.",
            )),
            ("rev-bias-r1-q3", fresh(
                1, "find_error",
                r"A worked solution explains the tiny current of a reverse-biased junction. Exactly one step is wrong.",
                [
                    r"Reverse bias makes the barrier taller than the built-in potential.",
                    r"The number of majority carriers that can climb that taller barrier falls exponentially.",
                    r"The remaining current is the minority carriers that reach the field and are swept across.",
                    r"The depletion region contains no carriers, so that remaining current is exactly zero.",
                ],
                3,
                r"The taller barrier shuts off majority diffusion. The minority carriers that wander into the field are still swept across, which is why the reverse current is small but not exactly zero.",
                reasons=[
                    r"The swept minority carriers are a small current, so the junction is not a perfect insulator.",
                    r"With the majority current shut off, nothing is left to cross, so the current is exactly zero.",
                ],
                correct_reason=0,
            )),
            ("rev-bias-r3-q1", fresh(
                3, "sym",
                r"The applied voltage is positive and smaller than the built-in potential. Write the depletion width divided by its zero-bias width. Use the name VD for the applied voltage and the name phibi for the built-in potential.",
                "sqrt(1-VD/phibi)",
                {"VD": (0.05, 0.45), "phibi": (0.6, 1.2)},
                r"The potential step is the built-in potential minus the applied voltage, and the width follows the square root of that step divided by the built-in potential. With the applied voltage positive the step is smaller, so the width shrinks. Half the voltage does not give half the width.",
                alternates=["sqrt((phibi-VD)/phibi)"],
            )),
        ]
    if sid == "junction-cap":
        return [
            ("junction-cap-r1-q3", fresh(
                1, "sym",
                r"Write the depletion capacitance per unit area. Use the name eps for the silicon permittivity and the name Xd for the total depletion width.",
                "eps/Xd",
                {"eps": (0.2, 5), "Xd": (0.1, 4)},
                r"The incremental charge sits on the two depletion edges, separated by the total depletion width. That is a parallel plate, so the capacitance per area is the permittivity divided by that width. A wider depletion region is a smaller capacitance.",
                alternates=["eps*(1/Xd)"],
            )),
            ("junction-cap-r2-q3", fresh(
                2, "find_error",
                r"A worked solution says which doping sets the zero-bias capacitance of a one-sided junction. Exactly one step is wrong.",
                [
                    r"The depletion region extends mostly into the lightly doped side.",
                    r"When the acceptor concentration is much larger than the donor concentration, that lightly doped side is the N side.",
                    r"The zero-bias capacitance depends on the width of that N side.",
                    r"The zero-bias capacitance is therefore set by the heavier doping.",
                ],
                3,
                r"The product of the two dopings, divided by their sum, is about the smaller doping. The zero-bias capacitance of a junction with a very heavy P side is set by the lighter N-side doping, not by the heavy side.",
                reasons=[
                    r"The width, and so the capacitance, is set by the lighter doping.",
                    r"The heavier side holds more ions per length, so it sets the capacitance.",
                ],
                correct_reason=0,
            )),
            ("junction-cap-r3-q3", fresh(
                3, "order",
                r"Order the steps that say what distance enters the depletion capacitance. Each step after the first uses the result of the step before it.",
                [
                    r"A small voltage change moves both depletion edges.",
                    r"The incremental charge appears at those two edges, one on the P side and one on the N side.",
                    r"The two edges are separated by the sum of the two depletion widths.",
                    r"That separation is the plate spacing in the depletion capacitance.",
                ],
                r"The plates are the two edges of the depletion region, not one side and not the metal contacts. Their spacing is the sum of the two depletion widths, and the capacitance per area is the permittivity divided by that sum.",
            )),
        ]
    raise SystemExit("no swaps for " + sid)


def fit_rev_bias_figure(bank):
    """Redraw the one-sided charge block so it stays inside the view box.

    A donor-to-acceptor ratio of 1/50 and a width multiplier of 1.4 pushed
    the N-side rectangle to x = 368 in a 360-wide view box. A multiplier of
    1.15 keeps the thin P+ sheet and the wide N-side block, and the block
    ends before x = 360.
    """
    sys.path.insert(0, os.path.join(ROOT, "skilltree", "gen"))
    import batch2a_fig
    for q in bank["questions"]:
        if q.get("id") != "rev-bias-r3-q3":
            continue
        q["figure"] = batch2a_fig.pn_profiles(NA=50, ND=1, show=("rho",), bias=1.15)
        q["version"] = 2
        return
    raise SystemExit("rev-bias-r3-q3 is not a live question")


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
    if sid == "rev-bias":
        fit_rev_bias_figure(bank)
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
