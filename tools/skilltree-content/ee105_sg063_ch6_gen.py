#!/usr/bin/env python3
"""SG-063 PN currents: swap the most pattern-matchable MC items.

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
    "diode-qual",
    "excess-carriers",
    "continuity",
    "minority-profile",
    "diode-iv",
    "diode-ss",
    "solar-cell",
    "led",
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
    if sid == "diode-qual":
        return [
            ("diode-qual-r2-q1", fresh(
                2, "sym",
                r"Forward bias makes the applied voltage positive and smaller than the built-in potential. Write the potential barrier that majority carriers must climb, using the name phibi for the built-in potential and the name VD for the applied voltage.",
                "phibi-VD",
                {"phibi": (0.6, 1.1), "VD": (-0.4, 0.45)},
                r"Forward bias opposes the built-in potential, so the barrier falls from the built-in potential to that potential minus the applied voltage. Reverse bias makes the applied voltage negative, and the barrier grows. The energy of the barrier is that potential times \(q\).",
                alternates=["-VD+phibi", "phibi+(-1)*VD"],
            )),
            ("diode-qual-r1-q1", fresh(
                1, "order",
                r"Order the steps that say why an equilibrium PN junction carries no net current. Each step after the first uses the result of the step before it.",
                [
                    r"Majority carriers that clear the built-in barrier diffuse across the junction.",
                    r"That diffusion current would keep charging the junction unless an equal current flows the other way.",
                    r"The current the other way is the drift of minority carriers swept across by the built-in field.",
                    r"With those two currents equal, the net current of each carrier is zero.",
                ],
                r"Equilibrium does not stop the carriers. Diffusion over the barrier and drift of the minorities that reach the field are equal and opposite, so each carrier's net current is zero.",
            )),
            ("diode-qual-r1-q2", fresh(
                1, "find_error",
                r"A worked solution explains the reverse current of an ideal diode. Exactly one step is wrong.",
                [
                    r"Reverse bias raises the barrier above the built-in potential.",
                    r"Majority diffusion over that taller barrier is shut off.",
                    r"What remains is drift of minority carriers generated near the junction.",
                    r"A larger reverse voltage supplies more of those minority carriers, so the current keeps growing.",
                ],
                3,
                r"Once majority diffusion is shut off, the remaining current is set by how many minorities are generated near the junction, not by the barrier height. In the ideal model that supply does not grow with reverse voltage, so the current saturates.",
                reasons=[
                    r"Generation near the junction sets the supply, so the ideal reverse current saturates.",
                    r"A taller barrier generates more minorities, so the reverse current keeps growing.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "excess-carriers":
        return [
            ("excess-carriers-r1-q1", fresh(
                1, "sym",
                r"Write the excess hole concentration, using the name p for the hole concentration and the name p0 for its equilibrium value.",
                "p-p0",
                {"p": (0.2, 8), "p0": (0.2, 8)},
                r"Only the departure from equilibrium drives net recombination or generation. The excess is the concentration minus its equilibrium value, and it is negative where the concentration has been pulled below that value.",
                alternates=["-p0+p", "p+(-1)*p0"],
            )),
            ("excess-carriers-r2-q3", fresh(
                2, "sym",
                r"Write the minority-carrier lifetime, using the name cp for the capture coefficient and the name NT for the trap density.",
                "1/(cp*NT)",
                {"cp": (0.2, 5), "NT": (0.2, 8)},
                r"Each trap is another place a minority carrier can be captured, so the lifetime is the reciprocal of the capture coefficient times the trap density. Doubling the trap density halves the lifetime, and the steady excess \(G_L\tau\) halves with it.",
                alternates=["1/cp*(1/NT)", "(cp*NT)**(-1)"],
            )),
            ("excess-carriers-r3-q3", fresh(
                3, "find_error",
                r"A worked solution says what happens to minority holes next to a reverse-biased junction. Exactly one step is wrong.",
                [
                    r"The minority concentration is below its equilibrium value, so the excess is negative.",
                    r"The rate of change of that excess is the negative of the excess divided by the lifetime.",
                    r"A negative excess makes that rate positive.",
                    r"The concentration therefore keeps falling.",
                ],
                3,
                r"A positive rate of change means the concentration is rising, not falling. With the excess negative, generation beats recombination and pushes the concentration back toward equilibrium. That generation feeds the reverse leakage.",
                reasons=[
                    r"A positive rate means generation, which pushes the concentration back up toward equilibrium.",
                    r"A negative excess means recombination continues, so the concentration keeps falling.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "continuity":
        return [
            ("continuity-r1-q2", fresh(
                1, "sym",
                r"Excess holes are injected into a long n-type region and the excess far away is zero. Write the excess at a distance from the injecting edge, using the name dp0 for the excess at that edge, the name x for the distance, and the name Lp for the diffusion length.",
                "dp0*exp(-x/Lp)",
                {"dp0": (0.2, 6), "x": (0.05, 4), "Lp": (0.2, 5)},
                r"The steady profile in a long region is a sum of a decaying exponential and a growing one. The excess has to vanish far away, so the growing term is zero, and the value at the edge fixes the rest. A straight line is the short-region profile, where recombination inside the region is negligible.",
                alternates=["dp0*e**(-x/Lp)", "exp(-x/Lp)*dp0"],
            )),
            ("continuity-r1-q3", fresh(
                1, "sym",
                r"Write the hole diffusion length, using the name Dp for the hole diffusivity and the name taup for the hole lifetime.",
                "sqrt(Dp*taup)",
                {"Dp": (0.2, 6), "taup": (0.2, 6)},
                r"The diffusion length is how far an excess minority carrier typically spreads before it recombines. It grows with the square root of diffusivity times lifetime. At one diffusion length the excess in a long region has fallen to \(1/e\) of its edge value; it never falls exactly to zero.",
                alternates=["sqrt(taup*Dp)"],
            )),
            ("continuity-r3-q3", fresh(
                3, "find_error",
                r"A worked solution describes the excess-hole profile in a region much shorter than the diffusion length. Exactly one step is wrong.",
                [
                    r"The region is much shorter than the diffusion length.",
                    r"Almost no recombination happens inside that short region.",
                    r"With no recombination the second derivative of the excess is about zero, so the profile is a straight line.",
                    r"The hole current therefore decays exponentially along the region.",
                ],
                3,
                r"A straight line has a constant slope, so the diffusion current is nearly the same at every point. The exponential decay belongs to a long region, where recombination removes holes as they travel.",
                reasons=[
                    r"A straight profile has a constant slope, so the hole current stays nearly the same along the region.",
                    r"Any injected profile decays exponentially, so the current falls along even a short region.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "minority-profile":
        return [
            ("minority-profile-r1-q2", fresh(
                1, "sym",
                r"The applied voltage is positive. Write the hole concentration at the n-side edge of the junction, using the name pn0 for the equilibrium minority concentration, the name VD for the applied voltage, and the name Vt for \(kT/q\).",
                "pn0*exp(VD/Vt)",
                {"pn0": (0.2, 5), "VD": (0.02, 0.2), "Vt": (0.02, 0.05)},
                r"Forward bias lowers the barrier, so the edge concentration is the equilibrium minority value times \(e^{V_D/V_t}\). At zero bias the exponential is 1 and the edge sits at equilibrium. The law assumes that injected concentration stays far below the majority doping.",
                alternates=["pn0*e**(VD/Vt)", "exp(VD/Vt)*pn0"],
            )),
            ("minority-profile-r3-q1", fresh(
                3, "find_error",
                r"A worked solution applies the junction-edge law at a large forward bias. Exactly one step is wrong.",
                [
                    r"The edge law assumes the injected minority concentration stays far below the majority doping.",
                    r"At this bias the computed edge concentration is larger than that doping.",
                    r"The injected holes then outnumber the majority electrons.",
                    r"The edge law still applies, because it never used that comparison.",
                ],
                3,
                r"The edge law is derived under low-level injection. Once the injected holes exceed the majority doping, charge neutrality pulls the electron concentration up as well, and the simple edge law no longer holds.",
                reasons=[
                    r"The edge law needs low-level injection, so it fails once the injected minorities exceed the doping.",
                    r"The edge law is exact at any bias, so the comparison with the doping does not matter.",
                ],
                correct_reason=0,
            )),
            ("minority-profile-r3-q3", fresh(
                3, "sym",
                r"The excess falls in a straight line to zero across a short neutral region. Write the hole current density, using the name q for the elementary charge, the name Dp for the diffusivity, the name dp for the excess at the injecting edge, and the name W for the region width.",
                "q*Dp*dp/W",
                {"q": (0.2, 4), "Dp": (0.2, 6), "dp": (0.2, 6), "W": (0.1, 4)},
                r"Diffusion current is charge times diffusivity times the slope. A straight drop of the excess over the width has slope equal to that excess divided by the width, so halving the width doubles the current. In a long region the diffusion length takes the place of the width.",
                alternates=["q*Dp*(dp/W)", "(q*Dp*dp)/W"],
            )),
        ]
    if sid == "diode-iv":
        return [
            ("diode-iv-r1-q1", fresh(
                1, "sym",
                r"Write the ideal diode current, using the name IS for the saturation current, the name VD for the applied voltage, the name n for the ideality factor, and the name Vt for \(kT/q\).",
                "IS*(exp(VD/(n*Vt))-1)",
                {"IS": (0.2, 5), "VD": (-0.2, 0.25), "n": (1, 2), "Vt": (0.02, 0.05)},
                r"Forward bias makes the current grow exponentially. Reverse bias drives the exponential to zero, so the current approaches the negative of the saturation current. The \(-1\) is what makes the current zero at zero voltage.",
                alternates=["IS*exp(VD/(n*Vt))-IS", "IS*(e**(VD/(n*Vt))-1)"],
            )),
            ("diode-iv-r2-q3", fresh(
                2, "sym",
                r"Write how much the diode voltage must rise for a tenfold increase in forward current, using the name n for the ideality factor and the name Vt for \(kT/q\).",
                "n*Vt*ln(10)",
                {"n": (1, 2), "Vt": (0.02, 0.05)},
                r"Current depends on \(e^{V/(nV_t)}\), so a factor of ten in current needs \(nV_t\ln 10\) of extra voltage. For an ideality factor of 1 that is about 60 mV. Multiplying \(V_t\) by the ideality factor and forgetting \(\ln 10\) is short by that factor.",
                alternates=["n*Vt*log(10)", "Vt*n*ln(10)"],
            )),
            ("diode-iv-r3-q1", fresh(
                3, "sym",
                r"Two identical diodes share, equally, a fixed total current that one diode carried alone. Write how much each diode's voltage falls, using the name Vt for \(kT/q\).",
                "Vt*ln(2)",
                {"Vt": (0.02, 0.05)},
                r"Each diode now carries half the current, which is the same as doubling the saturation current at fixed current. The voltage of an exponential falls by \(V_t\ln 2\), about 18 mV, not by half and not by the 60 mV of a tenfold change.",
                alternates=["Vt*log(2)", "ln(2)*Vt"],
            )),
        ]
    if sid == "diode-ss":
        return [
            ("diode-ss-r1-q1", fresh(
                1, "sym",
                r"Write the small-signal conductance of an ideal forward-biased diode, using the name ID for the bias current and the name Vt for \(kT/q\).",
                "ID/Vt",
                {"ID": (0.2, 6), "Vt": (0.02, 0.05)},
                r"The slope of the exponential is the current divided by \(V_t\). The ratio of current to voltage is a different, smaller number: it is the slope of the line from the origin, not the tangent. The reciprocal of this conductance is the small-signal resistance.",
                alternates=["ID*(1/Vt)", "(1/Vt)*ID"],
            )),
            ("diode-ss-r1-q3", fresh(
                1, "find_error",
                r"A worked solution says when a diode voltage signal is small enough to linearize. Exactly one step is wrong.",
                [
                    r"The exponential is replaced by 1 plus the signal divided by \(V_t\).",
                    r"That replacement needs the signal divided by \(V_t\) to be much smaller than 1.",
                    r"The scale of that comparison is \(V_t\), about 26 mV.",
                    r"Any signal much smaller than the 0.7 V turn-on voltage is therefore small enough.",
                ],
                3,
                r"The expansion is in the signal divided by \(V_t\), not by the bias voltage. A signal of 100 mV is far below 0.7 V and still several times \(V_t\), so the linear model is already poor.",
                reasons=[
                    r"The comparison is with \(V_t\), so a signal well below the turn-on voltage can still be too large.",
                    r"The comparison is with the turn-on voltage, so anything below 0.7 V is small-signal.",
                ],
                correct_reason=0,
            )),
            ("diode-ss-r2-q3", fresh(
                2, "multi",
                r"Select every statement that is true of a diode's small-signal capacitances.",
                [
                    r"Diffusion capacitance grows with the forward current.",
                    r"Diffusion capacitance is negligible in reverse bias.",
                    r"Junction capacitance disappears in forward bias.",
                    r"In reverse bias the small-signal model is essentially the junction capacitance.",
                ],
                [0, 1, 3],
                r"Diffusion capacitance is stored minority charge and grows with forward current, so it dominates in strong forward bias and vanishes in reverse. Junction capacitance is still there in forward bias; in reverse bias it is what remains, because both the conductance and the diffusion capacitance are about zero.",
            )),
        ]
    if sid == "solar-cell":
        return [
            ("solar-cell-r3-q1", fresh(
                3, "sym",
                r"Write the open-circuit voltage of a short-base solar cell, using the name Vt for \(kT/q\), the name tau for the minority-carrier lifetime, the name GL for the generation rate, the name ND for the doping, and the name ni for the intrinsic concentration.",
                "Vt*ln(tau*GL*ND/(ni*ni))",
                {"Vt": (0.02, 0.05), "tau": (2, 6), "GL": (2, 6), "ND": (2, 6), "ni": (0.2, 1)},
                r"Open-circuit voltage rises with lifetime, generation rate, and doping, and it falls as the intrinsic concentration rises. A shorter lifetime, lighter doping, or dimmer light all lower it.",
                alternates=["Vt*ln(GL*tau*ND/(ni**2))", "Vt*log(tau*GL*ND/(ni*ni))"],
            )),
            ("solar-cell-r1-q3", fresh(
                1, "find_error",
                r"A worked solution gives the excess minority concentration at the edge of a short-circuited solar cell. Exactly one step is wrong.",
                [
                    r"A short circuit holds the junction voltage at zero.",
                    r"The edge law sets the excess at the depletion edge from that voltage.",
                    r"At zero voltage that edge excess is zero.",
                    r"Light still raises the edge excess to the generation rate times the lifetime.",
                ],
                3,
                r"At zero voltage the edge law pins the excess at the depletion edge to zero. The generation-rate times lifetime is the excess far from that sink, where carriers are not being swept out. The zero at the edge is what draws the photocurrent.",
                reasons=[
                    r"Zero voltage pins the edge excess at zero. The generation-rate times lifetime is the excess far from the junction.",
                    r"Light sets the edge excess to the generation rate times the lifetime even at zero voltage.",
                ],
                correct_reason=0,
            )),
            ("solar-cell-r2-q2", fresh(
                2, "order",
                r"Order the steps that say which photogenerated carriers add to the short-circuit current. Each step after the first uses the result of the step before it.",
                [
                    r"Light generates carriers throughout the neutral region.",
                    r"A generated carrier adds to the short-circuit current only if it reaches the junction.",
                    r"Recombination removes a carrier before it can travel much farther than a diffusion length.",
                    r"Carriers generated much farther than a diffusion length therefore do not add to the short-circuit current.",
                ],
                r"The junction collects only the carriers that arrive. Beyond about one diffusion length, recombination wins, the excess flattens, and there is no diffusion current left to collect.",
            )),
        ]
    if sid == "led":
        return [
            ("led-r3-q3", fresh(
                3, "sym",
                r"Write the energy of one photon, using the name h for Planck's constant, the name c for the speed of light, and the name lam for the wavelength.",
                "h*c/lam",
                {"h": (0.2, 4), "c": (0.2, 6), "lam": (0.2, 5)},
                r"A shorter wavelength is a larger photon energy. The colour follows that wavelength: visible light is roughly 400 to 700 nm, and a longer wavelength is infrared.",
                alternates=["h*(c/lam)", "(h*c)/lam"],
            )),
            ("led-r1-q1", fresh(
                1, "order",
                r"Order the steps that say what makes a band gap direct. Each step after the first uses the result of the step before it.",
                [
                    r"A photon carries almost no momentum.",
                    r"A transition that emits a photon must keep the electron's momentum nearly the same.",
                    r"That is possible when the conduction-band minimum and the valence-band maximum occur at the same momentum.",
                    r"That alignment is a direct gap, and recombination can then emit a photon by itself.",
                ],
                r"A photon cannot make up a large change in crystal momentum. When the two band edges already share a momentum, the electron can drop and emit the photon alone. An indirect gap needs a phonon to supply the difference, so radiative recombination is rare.",
            )),
            ("led-r1-q3", fresh(
                1, "find_error",
                r"A worked solution says whether silicon makes a good LED. Exactly one step is wrong.",
                [
                    r"Silicon's conduction-band minimum and valence-band maximum occur at different momenta.",
                    r"A photon cannot supply that momentum difference.",
                    r"Radiative recombination is therefore rare, and most recombination makes heat.",
                    r"Silicon is therefore an efficient LED, because every recombination emits a photon.",
                ],
                3,
                r"The indirect gap is why a photon alone cannot finish the transition. Radiative recombination is rare, so silicon turns the recombination energy into heat rather than light.",
                reasons=[
                    r"The indirect gap makes radiative recombination rare, so silicon is a poor LED material.",
                    r"Every recombination emits a photon, so the momentum difference does not matter.",
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
