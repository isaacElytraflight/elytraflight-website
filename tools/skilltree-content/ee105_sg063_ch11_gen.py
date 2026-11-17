#!/usr/bin/env python3
"""SG-063 bipolar transistors: swap the most pattern-matchable MC items.

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

SKILLS = ["bjt-struct", "bjt-iv", "bjt-action", "ebers-moll", "early", "bjt-ss"]


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
    if sid == "bjt-struct":
        return [
            ("bjt-struct-r1-q2", fresh(
                1, "sym",
                r"Write the current into the emitter in terms of the currents into the collector and the base. Use IC and IB. Every current is positive when it flows into the device.",
                "-(IC+IB)",
                {"IC": (0.05, 20), "IB": (0.001, 2)},
                r"KCL on the three terminals is \(I_C + I_B + I_E = 0\), so the current into the emitter is \(-(I_C + I_B)\). For an npn in forward-active that current is negative: conventional current leaves through the emitter, which is what the emitter arrow shows. \(I_C + I_B\) is the magnitude of that current, not the signed current into the terminal. \(I_C - I_B\) subtracts the base current instead of adding it. \(I_B - I_C\) is the wrong difference.",
                alternates=["-IC-IB", "(-1)*(IC+IB)"],
            )),
            ("bjt-struct-r1-q1", fresh(
                1, "order",
                r"Order how a vertical npn is built and then biased for forward-active use, starting at the surface. Each step after the first uses the region named in the step before it.",
                [
                    r"The surface region is a small, heavily doped n-type emitter.",
                    r"That emitter is nested inside a thin p-type base.",
                    r"The base is nested inside the n-type collector, which is the large remaining region.",
                    r"Forward-active bias then forward-biases the emitter-base junction and reverse-biases the base-collector junction.",
                ],
                r"npn names the regions in that order: n emitter, p base, n collector. The emitter is the surface diffusion, not a buried layer under the collector, and it is not beside the collector at the same depth. A pnp is the opposite stack. The collector of an npn is n-type, so the bottom region is not p-type.",
            )),
            ("bjt-struct-r3-q1", fresh(
                3, "find_error",
                r"A worked solution says what happens to the current gain when the collector and emitter leads of a real BJT are swapped. Exactly one step is wrong.",
                [
                    r"The emitter is small and very heavily doped, and the collector is large and lightly doped.",
                    r"Forward gain uses that heavy emitter doping, which keeps the current injected back into the emitter small.",
                    r"Swapping the leads makes the lightly doped collector act as the emitter.",
                    r"The current gain is unchanged, because the two junctions are the same pn junction in either direction.",
                ],
                3,
                r"The structure is built for one direction. Used in reverse, the lightly doped side injects poorly and \(\alpha_R\) is small, so the reverse gain collapses. The arrow on the symbol records that direction; it does not create it. Holes can still flow, and the base contact is not what sets the asymmetry.",
                reasons=[
                    r"Reverse operation uses the small transport factor \(\alpha_R\), so the current gain collapses.",
                    r"The two junctions are identical, so the gain is the same with the leads swapped.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "bjt-iv":
        return [
            ("bjt-iv-r3-q1", fresh(
                3, "sym",
                r"In the forward-active region, write the collector current in terms of the base current. Use beta for \(\beta_F\) and IB for the base current.",
                "beta*IB",
                {"beta": (20, 400), "IB": (0.1, 80)},
                r"Forward-active collector current is \(I_C = \beta_F I_B\), linear in the base current, so equal steps of \(I_B\) space the \(I_C\)-\(V_{CE}\) curves evenly. \(I_B/\beta_F\) is the base current that a given collector current would need, not the collector current. \(\beta_F/I_B\) falls as the base current rises. An exponential in \(I_B\) would describe \(V_{BE}\), not this family: equal \(V_{BE}\) steps are the ones that space the curves exponentially.",
                alternates=["IB*beta", "beta*(IB)"],
            )),
            ("bjt-iv-r2-q3", fresh(
                2, "order",
                r"Order the steps that say why \(I_C\) falls steeply when \(V_{BE} = 0.72\ \mathrm{V}\) and \(V_{CE}\) is only \(0.12\ \mathrm{V}\). Each step after the first uses the result of the step before it.",
                [
                    r"\(V_{BC} = V_{BE} - V_{CE}\), so the base-collector voltage is \(0.60\ \mathrm{V}\).",
                    r"That positive base-collector voltage forward-biases the base-collector junction.",
                    r"The collector junction then injects carriers back into the base.",
                    r"The reverse injection subtracts from the forward collector current, so \(I_C\) falls. The device is in saturation.",
                ],
                r"Saturation here means both junctions are forward biased, which is the steep part of the curve at low \(V_{CE}\). The emitter has not stopped injecting. The base current has not reversed. The collector junction is forward biased, not in breakdown, and this is not cutoff.",
            )),
            ("bjt-iv-r1-q2", fresh(
                1, "find_error",
                r"A worked solution names the flat part of each curve on the \(I_C\)-\(V_{CE}\) family. Exactly one step is wrong.",
                [
                    r"Past a few tenths of a volt, the curve for a fixed base current becomes nearly flat.",
                    r"In that region the collector collects the carriers the emitter injects.",
                    r"The collector current is \(\beta_F\) times the base current, and it barely depends on \(V_{CE}\).",
                    r"That flat region is saturation, where the transistor behaves as a closed switch.",
                ],
                3,
                r"The flat region is forward-active: \(I_C = \beta_F I_B\), almost independent of \(V_{CE}\). Saturation is the steep fall at very low \(V_{CE}\), where the collector junction is also forward biased. Cutoff is the axis, where the current is nearly zero. A sharp rise at high \(V_{CE}\) would be breakdown, not this flat part.",
                reasons=[
                    r"The flat region is forward-active. Saturation is the steep part at very low \(V_{CE}\).",
                    r"A flat curve means the device is off, so this region is cutoff.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "bjt-action":
        return [
            ("bjt-action-r2-q3", fresh(
                2, "sym",
                r"Write \(\beta_F\) for an npn with a short base and a short emitter. Use Dn and Dp for the electron and hole diffusion constants, NE and NB for the emitter and base doping, and WE and WB for the emitter and base widths.",
                "Dn*NE*WE/(Dp*NB*WB)",
                {"Dn": (8, 40), "Dp": (2, 15), "NE": (1e18, 1e20), "NB": (1e16, 1e18), "WE": (0.05, 1), "WB": (0.05, 0.5)},
                r"The collector current scales as \(D_n/(N_B W_B)\) and the hole current injected back into the emitter scales as \(D_p/(N_E W_E)\). Their ratio is \(D_n N_E W_E/(D_p N_B W_B)\). Putting \(N_B\) in the numerator inverts the doping. Putting \(D_p\) on top swaps which carrier crosses the base. Dropping the widths treats a wide base the same as a thin one.",
                alternates=["(Dn/Dp)*(NE/NB)*(WE/WB)", "Dn*NE*WE*Dp**(-1)*NB**(-1)*WB**(-1)"],
            )),
            ("bjt-action-r1-q1", fresh(
                1, "order",
                r"Order the path of electrons from the emitter of a forward-active npn into the collector. Each step after the first uses the result of the step before it.",
                [
                    r"The forward-biased base-emitter junction injects electrons into the p-type base.",
                    r"The law of the junction sets their density at the emitter edge of the base from \(V_{BE}\).",
                    r"The neutral base has little electric field, so the electrons diffuse down that density gradient.",
                    r"At the reverse-biased collector junction, the field sweeps those electrons into the collector.",
                ],
                r"Electrons diffuse across the neutral base and are collected by the field at the reverse-biased collector junction. They do not drift across the neutral base, and they do not tunnel through it. Recombination in a thin base removes only a small fraction; it is not the path into the collector. \(V_{CE}\) does not set the edge density. \(V_{BE}\) does.",
            )),
            ("bjt-action-r3-q2", fresh(
                3, "find_error",
                r"A worked solution says what doubling the base width does to \(I_C\) at a fixed \(V_{BE}\), while the base stays short. Exactly one step is wrong.",
                [
                    r"A fixed \(V_{BE}\) holds the electron density at the emitter edge of the base fixed.",
                    r"Across a short base the profile is nearly a straight line, from that density down to about zero at the collector edge.",
                    r"The diffusion current is proportional to that slope, the edge density divided by \(W_B\).",
                    r"Doubling \(W_B\) therefore doubles the slope, so \(I_C\) doubles.",
                ],
                3,
                r"\(I_C = qAD_n n_p(0)/W_B\). The edge density stays fixed and the distance doubles, so the slope and \(I_C\) both halve. The current does not stay the same, and it does not fall by \(\sqrt{2}\). That square-root width belongs to a long diode, not to a short base.",
                reasons=[
                    r"Doubling \(W_B\) halves the slope \(n_p(0)/W_B\), so \(I_C\) halves.",
                    r"The current scales with the square root of the width, so \(I_C\) falls by \(\sqrt{2}\).",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "ebers-moll":
        return [
            ("ebers-moll-r1-q2", fresh(
                1, "sym",
                r"Write \(I_{CS}\) from the Ebers-Moll reciprocity relation. Use alphaF and alphaR for the forward and reverse transport factors, and IES for the base-emitter saturation current.",
                "alphaF*IES/alphaR",
                {"alphaF": (0.9, 0.999), "alphaR": (0.05, 0.7), "IES": (1e-18, 1e-14)},
                r"Reciprocity is \(\alpha_F I_{ES} = \alpha_R I_{CS}\), so \(I_{CS} = \alpha_F I_{ES}/\alpha_R\). Setting \(I_{CS} = I_{ES}\) drops both transport factors. Setting \(\alpha_F = \alpha_R\) is a different claim, and it is not what reciprocity says. The product \(\alpha_F\alpha_R\) is not 1.",
                alternates=["IES*alphaF/alphaR", "alphaF*IES*alphaR**(-1)"],
            )),
            ("ebers-moll-r2-q3", fresh(
                2, "order",
                r"Order the steps that name the region when \(V_{BE} = -1.2\ \mathrm{V}\) and \(V_{BC} = 0.58\ \mathrm{V}\). Each step after the first uses the result of the step before it.",
                [
                    r"A negative \(V_{BE}\) reverse-biases the base-emitter junction, so that junction is not injecting.",
                    r"A positive \(V_{BC}\) of several tenths of a volt forward-biases the base-collector junction.",
                    r"Only the collector side injects, so the collector is playing the role of the emitter.",
                    r"Transport in that direction uses \(\alpha_R\), which is much smaller than \(\alpha_F\), so the gain is poor. This is reverse-active.",
                ],
                r"Only the base-collector junction is forward biased, so the device is reverse-active and the gain is \(\alpha_R/(1-\alpha_R)\), which is small. Both junctions forward would be saturation. Both off, or the collector reverse biased with the emitter forward, would not be this bias. \(\alpha_R\) is not close to 1, because the collector is lightly doped.",
            )),
            ("ebers-moll-r3-q3", fresh(
                3, "find_error",
                r"A worked solution says why saturation is a poor bias for a linear amplifier. Exactly one step is wrong.",
                [
                    r"In saturation both the base-emitter junction and the base-collector junction are forward biased.",
                    r"The collector junction injects carriers back into the base.",
                    r"That reverse injection cuts the net collector current, so \(I_C/I_B\) falls well below \(\beta_F\).",
                    r"The stage is then a good linear amplifier, because the gain has become infinite.",
                ],
                3,
                r"In saturation the forced ratio \(I_C/I_B\) is below \(\beta_F\), and the extra stored base charge has to leave before the device can turn off. The collector current is not zero, and the gain is not infinite. The device is not in breakdown.",
                reasons=[
                    r"The forced gain is below \(\beta_F\), and the stored charge slows the exit from saturation.",
                    r"Saturation sets \(I_C\) to zero, which is why a saturated stage has no gain.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "early":
        return [
            ("early-r2-q1", fresh(
                2, "sym",
                r"Write the factor that multiplies the ideal forward collector current once base-width modulation is included. Use VCE for the collector-emitter voltage and VA for the Early voltage.",
                "1+VCE/VA",
                {"VCE": (0.2, 12), "VA": (15, 200)},
                r"\(I_C = I_S e^{V_{BE}/V_{th}}(1 + V_{CE}/V_A)\). Every forward-active curve is zero at \(V_{CE} = -V_A\), which is why the lines meet on the negative voltage axis. \(1 - V_{CE}/V_A\) would make the current fall as \(V_{CE}\) rises. An exponential in \(V_{CE}/V_{th}\) is the junction law, not this factor. Leaving the factor at 1 is the flat curve with no Early effect.",
                alternates=["(VA+VCE)/VA", "(VA+VCE)*VA**(-1)"],
            )),
            ("early-r1-q3", fresh(
                1, "order",
                r"Order the steps that say why a higher \(V_{CE}\) raises the collector current of a forward-active BJT. Each step after the first uses the result of the step before it.",
                [
                    r"Raising \(V_{CE}\) increases the reverse bias across the collector-base junction.",
                    r"The collector depletion region widens, and part of that extra width reaches into the base.",
                    r"The neutral base becomes thinner, so the minority-carrier gradient across it becomes steeper.",
                    r"The diffusion current, which is the collector current, therefore rises.",
                ],
                r"This is base-width modulation. A thinner neutral base steepens the electron gradient, so \(I_C\) rises. The cause is not avalanche, not self-heating, and not base-emitter breakdown. The base current is not what the extra \(V_{CE}\) sets.",
            )),
            ("early-r3-q2", fresh(
                3, "find_error",
                r"A worked solution says which doping choice raises the Early voltage. Exactly one step is wrong.",
                [
                    r"The Early effect is the collector depletion region moving the edge of the neutral base.",
                    r"The depletion region spreads farther into the more lightly doped side of the junction.",
                    r"Heavy base doping, compared with the collector, keeps most of that spread in the collector.",
                    r"A thinner, more lightly doped base therefore gives a larger Early voltage.",
                ],
                3,
                r"Base-width modulation is weaker when the depletion region stays mostly in the collector, which takes \(N_B\) well above \(N_C\). A thinner, lighter base lets the depletion eat farther into the base, so \(V_A\) falls. That heavier base does trade away \(\beta_F\). A larger Early voltage is not the same thing as a larger current gain, and it is not set by the emitter area.",
                reasons=[
                    r"A heavier base keeps the depletion mostly in the collector, so the neutral base moves less. The cost is a lower \(\beta_F\).",
                    r"A lighter base raises \(\beta_F\), and a higher current gain is the same thing as a larger Early voltage.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "bjt-ss":
        return [
            ("bjt-ss-r1-q3", fresh(
                1, "sym",
                r"Write \(r_\pi\), the small-signal resistance from base to emitter. Use beta for the current gain and gm for the transconductance.",
                "beta/gm",
                {"beta": (20, 400), "gm": (0.5, 80)},
                r"\(i_b = g_m v_{be}/\beta\), so the base looks like a resistance \(\beta/g_m\). \(1/g_m\) is the resistance seen looking into the emitter when the base is driven by an ideal source, not the resistance at the base. \(g_m/\beta\) is the base conductance. \(\beta g_m\) does not have the dimensions of a resistance. Base-width modulation is \(r_o\), not \(r_\pi\).",
                alternates=["beta*gm**(-1)", "beta*(1/gm)"],
            )),
            ("bjt-ss-r3-q2", fresh(
                3, "order",
                r"Order what happens to the hybrid-pi elements when the bias current \(I_C\) is doubled, with \(\beta\) and \(V_A\) fixed. Each step after the first uses the result of the step before it.",
                [
                    r"\(g_m = I_C/V_{th}\), so doubling the bias current doubles \(g_m\).",
                    r"\(r_\pi = \beta/g_m\), and \(\beta\) is fixed, so that larger \(g_m\) cuts \(r_\pi\) in half.",
                    r"\(r_o = V_A/I_C\), so the same doubled current that raised \(g_m\) also cuts \(r_o\) in half.",
                    r"The product \(g_m r_o\) stays at \(V_A/V_{th}\), because the factor of two in \(g_m\) cancels the factor of one half in \(r_o\).",
                ],
                r"\(g_m\) is linear in \(I_C\), and both \(r_\pi\) and \(r_o\) scale as \(1/I_C\). They do not all double, and \(g_m\) does not rise by \(\sqrt{2}\). That square-root law is a MOSFET of fixed size. \(V_{th}\) here is \(kT/q\), not a MOS threshold. The intrinsic gain does not depend on the bias current.",
            )),
            ("bjt-ss-r2-q2", fresh(
                2, "find_error",
                r"A worked solution compares a BJT's \(g_m\) with a MOSFET's at the same current, for an overdrive of \(0.25\ \mathrm{V}\). Exactly one step is wrong.",
                [
                    r"Per unit of collector current, a BJT has \(g_m = 1/V_{th}\), with \(V_{th} = kT/q\).",
                    r"Per unit of drain current, a saturated MOSFET has \(g_m = 2/V_{ov}\).",
                    r"At room temperature \(1/V_{th}\) is about \(38\ \mathrm{V^{-1}}\), and at \(V_{ov} = 0.25\ \mathrm{V}\) the MOSFET figure \(2/V_{ov}\) is \(8\ \mathrm{V^{-1}}\).",
                    r"The BJT therefore has the smaller transconductance per amp, because \(\beta\) divides \(g_m\).",
                ],
                3,
                r"The exponential gives more transconductance per amp than the square law at this overdrive: about \(38\ \mathrm{V^{-1}}\) against \(8\ \mathrm{V^{-1}}\). \(\beta\) sets \(r_\pi = \beta/g_m\); it does not divide \(g_m\). The two devices do not have the same \(g_m\) per amp. Matching the BJT would take \(V_{ov} = 2V_{th}\), about \(52\ \mathrm{mV}\), which is outside ordinary square-law bias. The device area does not set this per-amp comparison.",
                reasons=[
                    r"The BJT's \(g_m\) per amp is several times larger. \(\beta\) sets \(r_\pi\), not \(g_m\).",
                    r"Both devices have the same \(g_m\) per amp, because each is a current divided by a voltage.",
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
