#!/usr/bin/env python3
"""SG-063 semiconductors: swap the most pattern-matchable MC items.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The verifier does not import this file.
"""
import json
import os

from banklib import Bank
from templates import plot

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "drude",
    "si-props",
    "intrinsic",
    "doping",
    "drift",
    "diffusion",
    "total-current",
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


def falling_profile():
    """A falling concentration. The samples are not the graded current."""
    svg = plot(lambda x: 5.0 / (1.0 + x), 0.0, 4.0, "x", "n", "Electron concentration")
    alt = "Electron concentration that falls smoothly as position increases."
    return svg, alt


N_SVG, N_ALT = falling_profile()


def swaps_for(sid):
    """(old mc id, replacement) in the order that assigns q4, then q5."""
    if sid == "drude":
        return [
            ("drude-r1-q1", fresh(
                1, "order",
                r"In the gas model, a steady field is applied to a metal and the electrons keep colliding. Order the steps that produce a constant average velocity. Each step after the first uses the result of the step before it.",
                [
                    r"Between collisions the field adds momentum along the field. The added momentum is proportional to the time since that electron's last collision.",
                    r"The next collision erases the momentum added since the previous collision and leaves a random direction.",
                    r"Average over many electrons. The random directions cancel, and the momentum gained since the last collision remains.",
                    r"That remaining average is a drift velocity proportional to the field, and it does not grow with time.",
                ],
                r"The field's momentum has to be added before a collision can erase it. The average is taken over those reset trajectories, and the drift velocity is that average. A free particle with no collisions would keep accelerating. Random thermal speeds cancel in the average; they are not the drift.",
            )),
            ("drude-r1-q3", fresh(
                1, "sym",
                r"Mobility relates the drift speed of a carrier to the field. Write the drift speed using the name mu for the mobility \(\mu\) and the name F for the field magnitude.",
                "mu*F",
                {"mu": (50, 2000), "F": (10, 4000)},
                r"The defining relation is drift speed \(= \mu\) times the field magnitude. Dividing the mobility by the field, or multiplying by the field squared, is a different quantity. The units \(\mathrm{cm^2/(V\cdot s)}\) are what make that product a speed when the field is in \(\mathrm{V/cm}\).",
                alternates=["F*mu"],
            )),
            ("drude-r3-q3", fresh(
                3, "find_error",
                r"A metal wire is heated and its resistance rises. A student accounts for that in the gas model. Exactly one step is wrong.",
                [
                    r"The conductivity is \(n q^2 \tau/m\).",
                    r"In a metal the free-electron density \(n\) stays about one electron per atom.",
                    r"Heating strengthens the lattice vibrations, so electrons scatter more often and the mean free time \(\tau\) gets shorter.",
                    r"A shorter mean free time raises the mobility, so the resistance falls.",
                ],
                3,
                r"Mobility is \(q\tau/m\). A shorter mean free time lowers it, and with \(n\) fixed the conductivity falls, so the resistance rises. The electron density of a metal does not drop when the wire is heated. In a semiconductor the carrier density can rise fast enough to win, which is the opposite trend.",
                reasons=[
                    r"A shorter mean free time lowers the mobility. With \(n\) fixed, the conductivity falls and the resistance rises.",
                    r"Heating frees fewer electrons, so \(n\) drops and the resistance rises.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "si-props":
        return [
            ("si-props-r1-q1", fresh(
                1, "order",
                r"Order the bond count for one silicon atom in the crystal. Each step after the first uses the result of the step before it.",
                [
                    r"Count the outer-shell electrons of this group IV atom. There are 4.",
                    r"Place one of those 4 electrons into a bond toward each of the 4 nearest neighbours.",
                    r"Each neighbour puts one of its own electrons into the same bond, so each bond holds 2 electrons.",
                    r"The atom therefore forms 4 covalent bonds, one to each nearest neighbour.",
                ],
                r"The valence count has to come first, because those electrons are what get placed into bonds. The neighbour's electron is added to a bond that already holds this atom's electron. Counting 8 bonds would count each shared electron as a separate bond. Only the two \(3p\) electrons bonding would leave the outer shell unfinished.",
            )),
            ("si-props-r1-q2", fresh(
                1, "multi",
                r"Pure silicon is cooled to \(0\ \mathrm{K}\). Select every statement that is true.",
                [
                    r"Every valence electron is locked in a covalent bond.",
                    r"The valence band is full and the conduction band is empty.",
                    r"Holes are present even though no bond is broken.",
                    r"There are no free carriers, so the crystal does not conduct.",
                ],
                [0, 1, 3],
                r"At \(0\ \mathrm{K}\) no bond is broken, so the valence band is full, the conduction band is empty, and nothing can carry a current. A hole exists only after a bond breaks. The four valence electrons are bonding electrons, not a metal's free-electron gas. Stopping the lattice vibrations does not create carriers.",
            )),
            ("si-props-r3-q1", fresh(
                3, "find_error",
                r"A band is completely filled. A student decides what current it carries when a field is applied. Exactly one step is wrong.",
                [
                    r"Every state in the band is occupied.",
                    r"The occupied states come in pairs with velocities \(+v\) and \(-v\).",
                    r"The charge-weighted sum of those velocities is zero.",
                    r"A field therefore drives a net current proportional to the number of electrons in the band.",
                ],
                3,
                r"In a full band every \(+v\) is paired with a filled \(-v\), so the sum is zero. A field cannot change which states are filled when there is no empty state to move into. Current appears only when the band is partly empty. Writing the valence band as a full band minus the missing electrons is what produces the hole current.",
                reasons=[
                    r"A full band's paired velocities already sum to zero. Net current needs a partly empty band.",
                    r"The current is proportional to the number of electrons and flows opposite the field.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "intrinsic":
        return [
            ("intrinsic-r1-q3", fresh(
                1, "order",
                r"The recombination rate constant is a positive number. Order the steps from thermal equilibrium to the mass-action law. Each step after the first uses the result of the step before it.",
                [
                    r"In equilibrium the thermal generation rate equals the recombination rate.",
                    r"Write recombination as that positive constant times \(n\) times \(p\), and solve for the product \(np\). It equals the generation rate divided by the constant.",
                    r"Generation depends only on temperature, so the product just obtained is fixed once the temperature is fixed.",
                    r"That temperature-fixed product is \(n_i^2\), so the mass-action law is \(np = n_i^2\).",
                ],
                r"Equilibrium is the equality of the two rates, so the product is solved from that equality. The generation rate has to be known to depend only on temperature before the product can be called a function of temperature alone. Naming it \(n_i^2\) uses that fixed product. Setting both rates to zero would empty the crystal, which is not equilibrium.",
            )),
            ("intrinsic-r2-q3", fresh(
                2, "sym",
                r"Away from equilibrium, recombination uses both the electron concentration and the hole concentration. Write the recombination rate using the name k for the positive rate constant, the name n for the electron concentration, and the name p for the hole concentration.",
                "k*n*p",
                {"k": (0.2, 5), "n": (0.3, 8), "p": (0.3, 8)},
                r"The rate is the constant times the product \(np\). Doubling both concentrations multiplies the rate by 4, which is the product of the two factors. Adding the concentrations, or using only one of them, counts meetings that do not use both partners. Thermal generation stays a function of temperature and is not this rate.",
                alternates=["k*p*n", "n*p*k"],
            )),
            ("intrinsic-r3-q3", fresh(
                3, "find_error",
                r"Steady light shines on pure silicon and a steady state is reached. A student applies the mass-action law. Exactly one step is wrong.",
                [
                    r"With no light, equilibrium sets \(knp\) equal to thermal generation.",
                    r"The light adds a second generation rate, on top of thermal generation.",
                    r"In the illuminated steady state, recombination equals the sum of those two generation rates.",
                    r"The mass-action law still forces \(np = n_i^2\), because that law does not care which process generates the pairs.",
                ],
                3,
                r"Mass action is the equilibrium balance against thermal generation alone. With light, recombination balances thermal generation plus optical generation, so the steady product \(np\) is larger than \(n_i^2\). The light makes pairs, so \(n\) and \(p\) both rise.",
                reasons=[
                    r"Mass action is the dark equilibrium. Extra generation raises the steady product \(np\) above \(n_i^2\).",
                    r"Light raises \(n\) and lowers \(p\) so the product stays \(n_i^2\).",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "doping":
        return [
            ("doping-r2-q3", fresh(
                2, "sym",
                r"In a uniformly doped region the charge density is \(\rho\). Write \(\rho/q\) using the name p for the hole concentration, the name n for the electron concentration, the name ND for the ionized donor concentration, and the name NA for the ionized acceptor concentration.",
                "p-n+ND-NA",
                {"p": (0.2, 8), "n": (0.2, 8), "ND": (0.2, 8), "NA": (0.2, 8)},
                r"Holes and ionized donors are positive, so they enter with a plus. Electrons and ionized acceptors are negative, so they enter with a minus. The combination is zero only when the region is neutral. The expression itself is \(\rho/q\). Swapping the signs of \(n\) and \(p\) counts every carrier with the wrong charge. The product \(np\) is the mass-action law, not the charge density.",
                alternates=["p+ND-n-NA", "ND-NA+p-n"],
            )),
            ("doping-r3-q1", fresh(
                3, "multi",
                r"Donors and acceptors are added at the same concentration, and that concentration is far above \(n_i\). Select every statement that is true in equilibrium.",
                [
                    r"Charge neutrality requires the electron and hole concentrations to be equal.",
                    r"Both carrier concentrations are about \(n_i\).",
                    r"The majority-carrier concentration is about the donor concentration.",
                    r"The donor and acceptor ions are still in the crystal and still scatter carriers.",
                ],
                [0, 1, 3],
                r"Equal donor and acceptor concentrations cancel in the neutrality equation, so \(n = p\), and mass action then forces both to \(n_i\). The ions remain and still scatter, which is why the mobility is not the pure-crystal value. The majority concentration is not the donor concentration, because each donated electron has filled an acceptor.",
            )),
            ("doping-r3-q3", fresh(
                3, "find_error",
                r"A student explains why adding donors lowers the hole concentration. Exactly one step is wrong.",
                [
                    r"Thermal generation depends on temperature and does not change when donors are added.",
                    r"The recombination rate is proportional to the product of the electron and hole concentrations.",
                    r"The donors raise the electron concentration, so that product, and the recombination rate, rise.",
                    r"Each donor ion then captures one hole, and that capture is what lowers the hole concentration.",
                ],
                3,
                r"The higher electron concentration raises recombination, so holes are removed until \(np\) returns to \(n_i^2\). A positive donor ion repels a hole; it does not bind one. Generation was already fixed by the temperature, so the new balance is a lower hole concentration \(p = n_i^2/n\).",
                reasons=[
                    r"The higher electron concentration raises recombination until \(np\) returns to \(n_i^2\). The donor ion does not bind a hole.",
                    r"Each donor converts one hole into one electron.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "drift":
        return [
            ("drift-r1-q2", fresh(
                1, "order",
                r"A field points to the right in silicon that contains both electrons and holes. Order the directions of the two drift currents. Each step after the first uses the result of the step before it.",
                [
                    r"Holes are positive, so they drift to the right, and their current points to the right.",
                    r"Electrons are negative, so they drift to the left, opposite that hole drift.",
                    r"Electron current points opposite the electron velocity, because the charge they carry is negative.",
                    r"That electron current points to the right, the same way as the hole current, so the two currents add.",
                ],
                r"The hole drift has to be known before the electron drift can be called opposite to it. The electron current is read from that velocity by reversing it, and only then does it line up with the hole current. The carriers move in opposite directions. The currents do not.",
            )),
            ("drift-r2-q3", fresh(
                2, "find_error",
                r"A student explains why the mobility falls as the dopant concentration rises. Exactly one step is wrong.",
                [
                    r"Carriers cross a perfect periodic lattice without scattering.",
                    r"Each ionized dopant is a charge sitting off that periodic pattern.",
                    r"More ionized dopants therefore mean more scattering and a shorter mean free time \(\tau\).",
                    r"Mobility is \(q\tau/m^*\), so the shorter mean free time raises the mobility.",
                ],
                3,
                r"Mobility is \(q\tau/m^*\), so a shorter mean free time lowers it. The scattering sites are the ions. Compensating dopants still scatter, because the total ion density \(N_D+N_A\) is what breaks the lattice, not the net carrier density.",
                reasons=[
                    r"A shorter mean free time lowers \(q\tau/m^*\). The ions are the scattering sites, and compensated dopants still count.",
                    r"A shorter mean free time raises the mobility because the carriers become lighter.",
                ],
                correct_reason=0,
            )),
            ("drift-r3-q2", fresh(
                3, "multi",
                r"Intrinsic silicon is under an applied field. Select every statement that is true.",
                [
                    r"Electrons and holes drift in opposite directions.",
                    r"The electron and hole drift currents point in the same direction.",
                    r"The drift current density is \(q\,n_i(\mu_n-\mu_p)E\).",
                    r"The drift current density is \(q\,n_i(\mu_n+\mu_p)E\).",
                ],
                [0, 1, 3],
                r"Opposite charges drifting in opposite directions give current in the same direction, so the mobilities add. The difference \(\mu_n-\mu_p\) describes a net particle flux, not the current. Intrinsic silicon does carry a drift current.",
            )),
        ]
    if sid == "diffusion":
        return [
            ("diffusion-r1-q1", fresh(
                1, "order",
                r"No field is applied. Order the steps that give the net diffusion flow. Each step after the first uses the result of the step before it.",
                [
                    r"Each carrier steps left or right with equal probability, so one carrier has no preferred direction.",
                    r"Because that step is unbiased, the number crossing a plane from one side equals the number of carriers sitting on that side.",
                    r"The high-concentration side therefore sends more carriers across the plane than the low-concentration side sends back.",
                    r"The net flow is that difference, and it points from high concentration toward low concentration.",
                ],
                r"The unbiased step is what makes the crossing count equal the population on that side. The high side then outnumbers the low side, and the net flow is the difference of those two counts. A field is not required. Equal traffic in every direction would be true of one carrier, not of the net flow.",
            )),
            ("diffusion-r1-q3", fresh(
                1, "sym",
                r"Electrons diffuse where their concentration changes with position. Write the electron diffusion current density using the name q for the elementary charge, the name Dn for the electron diffusivity, and the name gn for the gradient \(dn/dx\).",
                "q*Dn*gn",
                {"q": (0.2, 4), "Dn": (0.2, 6), "gn": (-6, 6)},
                r"Electrons flow down the gradient. When \(dn/dx\) is negative, that flow is toward \(+x\). Negative charge moving toward \(+x\) is a current toward \(-x\), so the current density is \(q D_n\) times the gradient and carries the gradient's sign. Hole diffusion current has the opposite sign in front of the gradient. The drift term is absent when there is no field.",
                alternates=["Dn*q*gn", "q*gn*Dn"],
                fig=N_SVG,
                alt=N_ALT,
            )),
            ("diffusion-r3-q2", fresh(
                3, "find_error",
                r"Light near \(x = 0\) gives electrons and holes the same profile, falling as \(x\) increases, and \(D_n > D_p\). A student finds the diffusion currents. Exactly one step is wrong.",
                [
                    r"Both carrier types diffuse toward \(+x\), down the shared gradient.",
                    r"Hole current points with the hole flow, toward \(+x\).",
                    r"Electron current points opposite the electron flow, toward \(-x\).",
                    r"The two currents cancel, because the two concentration profiles are the same.",
                ],
                3,
                r"The currents point in opposite directions. They would cancel only if the diffusivities were equal. With \(D_n > D_p\) the net current is \(q(D_n-D_p)\,dn/dx\), which points toward \(-x\). Identical particle flows of opposite charges are opposite currents.",
                reasons=[
                    r"The currents point opposite ways. With \(D_n > D_p\) they do not cancel, and the net current points toward \(-x\).",
                    r"Both currents point toward \(+x\) and add.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "total-current":
        return [
            ("total-current-r1-q1", fresh(
                1, "sym",
                r"Both a field and a concentration gradient act on the electrons. Write the total electron current density using the name q for the elementary charge, the name n for the electron concentration, the name mun for the electron mobility, the name F for the electric field, the name Dn for the electron diffusivity, and the name gn for the gradient \(dn/dx\).",
                "q*n*mun*F+q*Dn*gn",
                {"q": (0.2, 3), "n": (0.3, 6), "mun": (0.2, 5), "F": (0.2, 5), "Dn": (0.2, 5), "gn": (-4, 4)},
                r"Drift contributes \(q n \mu_n\) times the field, and diffusion contributes \(q D_n\) times the gradient. The electron diffusion term is positive in front of \(dn/dx\), because the particle flux \(-D_n\,dn/dx\) is multiplied by the charge \(-q\). The hole formula puts a minus in front of the hole gradient. Dropping either term is the pure-drift or pure-diffusion case.",
                alternates=["q*(n*mun*F+Dn*gn)", "q*Dn*gn+q*n*mun*F"],
            )),
            ("total-current-r1-q3", fresh(
                1, "multi",
                r"An ordinary doped silicon resistor carries a steady current. The doping is uniform. Select every statement that is true.",
                [
                    r"The majority-carrier concentration does not change along the bar.",
                    r"Majority-carrier diffusion is about zero.",
                    r"The current is the drift of the majority carriers.",
                    r"Minority carriers carry about as much of the current as the majority carriers.",
                ],
                [0, 1, 2],
                r"Uniform doping means a vanishing gradient, so diffusion is about zero and drift of the majority carriers carries the current. Minority carriers are fewer by many orders of magnitude. Diffusion matters where the concentration changes, as it does near a junction.",
            )),
            ("total-current-r3-q1", fresh(
                3, "order",
                r"A sample has a doping gradient, is in thermal equilibrium, and has no contacts. Order the steps that produce the built-in field. Each step after the first uses the result of the step before it.",
                [
                    r"The carriers follow the dopants, so the doping gradient produces a carrier-concentration gradient.",
                    r"That concentration gradient drives a diffusion current of each carrier type.",
                    r"Equilibrium forbids a continuing current of either type, so a field grows until the drift of each type cancels the diffusion of that same type.",
                    r"With each of those currents equal to zero, the field that remains is the built-in field.",
                ],
                r"The concentration gradient is what the diffusion current is built from, and the cancelling field is built to stop that current. Calling the field built-in uses the cancellation. Zero total current is not enough: each carrier type must be separately balanced, or that type would keep piling up. A uniform carrier profile would have nothing for the field to cancel.",
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
