#!/usr/bin/env python3
"""SG-063 amplifier frequency response: swap the most pattern-matchable MC items.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The new questions use the same relations as the
explainers, and the explainer worked examples do not use these prompts.
The verifier does not import this file.

Three kept figures draw a ground symbol past a 140-tall viewBox. Those
viewBoxes are extended so the batch figure check can pass, and those
question versions are bumped.
"""
import json
import os

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = ["freq-basics", "cs-brute", "miller", "cd-freq", "cg-freq", "ft", "octc"]

# Ground glyph ends at y=144. A 140-tall viewBox fails figure_bounds.
FIGURE_FIX = {
    "cd-freq-r4-q3": ('viewBox="0 0 698 140"', 'viewBox="0 0 698 152"'),
    "octc-r3-q3": ('viewBox="0 0 522 140"', 'viewBox="0 0 522 152"'),
    "octc-r4-q1": ('viewBox="0 0 522 140"', 'viewBox="0 0 522 152"'),
}


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
    if sid == "freq-basics":
        return [
            ("freq-basics-r1-q1", fresh(
                1, "order",
                r"Order how the two families of capacitors set the midband of a discrete amplifier. Each step after the first uses the result of the step before it.",
                [
                    r"Coupling and bypass capacitors are large, so they are open at DC and nearly shorts once the signal is well above their corners.",
                    r"Device and load capacitances are small, so they stay open through the midband and shunt nodes only at high frequency.",
                    r"The midband model therefore treats every coupling and bypass capacitor as a short and every device or load capacitance as an open.",
                    r"When several low-frequency corners are far apart, the highest of them is the first one met coming down from that midband, and that corner is the low edge.",
                ],
                r"Large external capacitors set the low edge and small parasitic ones set the high edge. The flat midband sits between those two models. Device capacitances do not set the low corner, and the supply does not set either edge. \(r_o\) is a resistance, not a coupling capacitor. Shorting the device capacitances as well is the high-frequency limit, not the midband. Adding separated low-frequency corners, or taking their geometric mean, is not how the low edge is chosen.",
            )),
            ("freq-basics-r2-q2", fresh(
                2, "find_error",
                r"A worked solution locates the overall low-frequency corner of a stage with three well-separated coupling and bypass corners, at 4 Hz, 15 Hz, and 90 Hz. Exactly one step is wrong.",
                [
                    r"The three corners are far apart, so each one can be read on its own.",
                    r"Coming down from the midband, the gain stays flat until the first of those corners.",
                    r"The first corner met on the way down is the highest one, at 90 Hz.",
                    r"The overall low-frequency corner is the sum, 109 Hz, because separated corners add.",
                ],
                3,
                r"With corners this far apart, the highest one sets the low edge. The gain has already rolled off before the lower corners matter, so 4 Hz is not the edge and the three frequencies do not add. The geometric mean is not the rule either. A product of the three corners would be a different circuit, with the sections cascaded and no single dominant corner.",
                reasons=[
                    r"The highest corner sets the low edge. Separated corners do not add.",
                    r"The lowest corner sets the low edge, so 4 Hz is the answer and the sum is a side issue.",
                ],
                correct_reason=0,
            )),
            ("freq-basics-r3-q2", fresh(
                3, "sym",
                r"Write the corner frequency, in hertz, of one coupling capacitor Cc between resistances Rleft and Rright. pi is the circle constant. Use Cc, Rleft, and Rright.",
                "1/(2*pi*Cc*(Rleft+Rright))",
                {"Cc": (1e-9, 5e-6), "Rleft": (50, 2e6), "Rright": (50, 2e6)},
                r"The capacitor sees the resistance on both sides, so \(f_c = 1/[2\pi C_c(R_{left}+R_{right})]\). Using only one side drops the other resistance. The parallel combination \(R_{left}R_{right}/(R_{left}+R_{right})\) is the resistance of two resistors sharing a node, not the resistance in series with a coupling capacitor. \(1/[C_c(R_{left}+R_{right})]\) is the corner in radians per second. A bypass pole \((1+g_mR_S)/(2\pi R_SC_S)\) is a different network: the source node also sees \(1/g_m\).",
                alternates=[
                    "1/(2*pi*Cc*Rleft+2*pi*Cc*Rright)",
                    "(2*pi*Cc*(Rleft+Rright))**(-1)",
                ],
            )),
        ]
    if sid == "cs-brute":
        return [
            ("cs-brute-r1-q1", fresh(
                1, "order",
                r"Order the nodal analysis that produces the common-source high-frequency transfer function. Each step after the first uses the result of the step before it.",
                [
                    r"The high-frequency model has two unknown node voltages, the gate and the drain.",
                    r"KCL at those nodes brings in \(C_{gs}\), the bridging \(C_{gd}\), the load \(C_L\), \(g_m\), \(R_s\), and \(R_o\).",
                    r"Eliminating \(v_{gs}\) leaves a single ratio of polynomials in \(s\).",
                    r"The three capacitors form one loop, so they hold only two independent states and the denominator is quadratic.",
                ],
                r"Two unknown nodes give a second-order denominator. One equation would be a first-order model, and one equation per capacitor would count a loop of capacitors as three states. The midband gain \(-g_mR_o\) is the value at \(s = 0\), not the whole transfer function. The numerator still carries the right-half-plane zero at \(g_m/C_{gd}\).",
            )),
            ("cs-brute-r1-q3", fresh(
                1, "find_error",
                r"A worked solution places the zero of a common-source stage. Exactly one step is wrong.",
                [
                    r"The transistor draws \(g_mv_{gs}\) out of the output node.",
                    r"\(C_{gd}\) also ties the gate to the drain, so a rising gate pushes current through \(C_{gd}\) into that same node.",
                    r"The two currents cancel when \(sC_{gd} = g_m\).",
                    r"The zero is therefore in the left half plane, at \(s = -g_m/C_{gd}\).",
                ],
                3,
                r"The feedthrough current through \(C_{gd}\) opposes the transistor current, so they cancel at \(s = +g_m/C_{gd}\), on the positive real axis. The zero is not at \(-g_m/C_{gd}\). \(C_{gs}\) being larger than \(C_{gd}\) moves the input pole; it does not flip the sign of this zero. A positive \(R_s\) sets the input time constant, not the half plane of the zero.",
                reasons=[
                    r"The currents cancel at \(s = +g_m/C_{gd}\), so the zero is in the right half plane.",
                    r"\(C_{gs}\) is larger than \(C_{gd}\), and that inequality is what places the zero in the left half plane.",
                ],
                correct_reason=0,
            )),
            ("cs-brute-r2-q3", fresh(
                2, "sym",
                r"Write \(b_1\), the coefficient of \(s\) in the common-source high-frequency denominator. Use Rs, Cgs, gm, Ro, Cgd, and CL.",
                "Rs*(Cgs+(1+gm*Ro)*Cgd)+Ro*(Cgd+CL)",
                {"Rs": (100, 5e4), "Cgs": (1e-15, 2e-13), "gm": (2e-4, 2e-2),
                 "Ro": (500, 5e4), "Cgd": (5e-16, 5e-14), "CL": (1e-15, 5e-12)},
                r"\(b_1 = R_s[C_{gs}+(1+g_mR_o)C_{gd}] + R_o(C_{gd}+C_L)\). The term \(R_s(1+g_mR_o)C_{gd}\) is the Miller contribution at the input. \(b_1\) is a sum of time constants, not their product; the product structure belongs to \(b_2\). \(R_sC_{gs}\) alone drops the bridging and load terms. Because \(b_1 = 1/\omega_{p1}+1/\omega_{p2}\), the estimate \(\omega_{p1}\approx 1/b_1\) is good only when the second pole is far above the first. Setting \(R_s\) to 0 removes every term that multiplies \(R_s\) and leaves \(R_o(C_{gd}+C_L)\).",
                alternates=[
                    "Rs*Cgs+Rs*Cgd+Rs*gm*Ro*Cgd+Ro*Cgd+Ro*CL",
                    "Rs*Cgs+Rs*(1+gm*Ro)*Cgd+Ro*Cgd+Ro*CL",
                ],
            )),
        ]
    if sid == "miller":
        return [
            ("miller-r1-q1", fresh(
                1, "sym",
                r"Write the impedance from the input to ground that replaces a bridging impedance ZF across an amplifier of signed gain A. Use ZF and A.",
                "ZF/(1-A)",
                {"ZF": (10, 1e6), "A": (-40, -1.5)},
                r"The input current is \((v_{in}-Av_{in})/Z_F = v_{in}(1-A)/Z_F\), so the equivalent impedance is \(Z_F/(1-A)\). For a negative gain this is smaller than \(Z_F\), and a bridging capacitor therefore looks larger. \(Z_F(1-A)\) grows instead of shrinking. \(AZ_F\) is not an impedance from the input to ground. \(Z_F\) alone forgets the gain. The output-side equivalent is \(Z_F/(1-1/A)\), which is a different port.",
                alternates=["ZF*(1-A)**(-1)", "ZF/(-A+1)"],
            )),
            ("miller-r1-q3", fresh(
                1, "order",
                r"Order why an inverting gain multiplies a bridging capacitor. Each step after the first uses the result of the step before it.",
                [
                    r"When the input moves, the output of an inverting stage moves by the gain \(A\), and \(A\) is negative.",
                    r"The voltage across the bridging capacitor changes by the input move minus that output move.",
                    r"The difference is \((1-A)\) times the input move, which equals \((1+|A|)\) times the input move.",
                    r"The capacitor therefore draws \((1+|A|)\) times the current it would draw to ground, and the input sees the capacitance \((1-A)C\).",
                ],
                r"Capacitor current follows the voltage across the capacitor, and the far terminal moves the other way. The amplifier does not add charge by itself, and the dielectric constant does not change. The output resistance is not what multiplies the capacitor. Using \(|A|\) instead of \(1+|A|\) drops the original input swing. The same algebra with the low-frequency gain is an estimate, because the bridging element itself changes the gain at high frequency.",
            )),
            ("miller-r3-q3", fresh(
                3, "find_error",
                r"A worked solution applies Miller's theorem to \(C_{gd}\) of an inverting stage whose low-frequency gain is \(A\). Exactly one step is wrong.",
                [
                    r"The theorem replaces the bridge by an input capacitance \((1-A)C_{gd}\).",
                    r"That factor uses a gain, and the practical estimate puts in the low-frequency gain \(-g_mR_o\).",
                    r"The estimate is not exact at high frequency, because the bridging capacitor changes the gain that the theorem assumed.",
                    r"The missing piece is only \(C_{gs}\). With \(C_{gs}\) added, the Miller input pole is exact at every frequency.",
                ],
                3,
                r"Adding \(C_{gs}\) completes the input capacitance of the estimate. It does not cancel the error in \(A\). The theorem is exact only for the true frequency-dependent gain. Using \(-g_mR_o\) drops the right-half-plane zero and the interaction with the output pole. The algebra of the theorem is not restricted to resistors: the same factor applies to \(C_{gd}\).",
                reasons=[
                    r"\(C_{gs}\) belongs in the input sum, but the low-frequency gain is still an estimate. The pole is not exact.",
                    r"The theorem is algebraically wrong for capacitors, so no added term can make the pole exact.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "cd-freq":
        return [
            ("cd-freq-r1-q1", fresh(
                1, "order",
                r"Order why a source follower bootstraps \(C_{gs}\). Each step after the first uses the result of the step before it.",
                [
                    r"The drain is an AC ground, so \(C_{gd}\) loads the gate directly and does not bridge input to output.",
                    r"\(C_{gs}\) connects the gate, the input, to the source, the output.",
                    r"The follower gain is \(g_mR/(1+g_mR)\), just below \(+1\), so the two ends of \(C_{gs}\) move almost together.",
                    r"The Miller factor \(1-A_v\) equals \(1/(1+g_mR)\), and the input keeps only that fraction of \(C_{gs}\), plus the full \(C_{gd}\).",
                ],
                r"The bridging capacitor is \(C_{gs}\), not \(C_{gd}\). \(C_{db}\) goes to the body and does not set this input factor. A follower does have a bridging capacitor. Multiplying \(C_{gs}\) by a large inverting factor would describe a common-source stage. A heavy resistive load lowers \(R\), lowers the gain, and leaves a larger fraction of \(C_{gs}\) on the input.",
            )),
            ("cd-freq-r1-q3", fresh(
                1, "sym",
                r"Write the input capacitance of a source follower whose gain is \(g_mR/(1+g_mR)\). The drain is an AC ground. Use Cgd, Cgs, gm, and R.",
                "Cgd+Cgs/(1+gm*R)",
                {"Cgd": (5e-16, 3e-14), "Cgs": (5e-15, 2e-13), "gm": (2e-4, 2e-2), "R": (100, 1e5)},
                r"\(C_{in} = C_{gd} + C_{gs}/(1+g_mR)\). \(C_{gd}\) sees a grounded drain, so it is not multiplied. \(C_{gs}\) is multiplied by \(1-A_v = 1/(1+g_mR)\). Using \(C_{gs}\) alone forgets both the bootstrap and \(C_{gd}\). Multiplying \(C_{gs}\) by \(1+g_mR\) is the inverting direction. \(C_{gd}(1+g_mR)\) would be right only if \(C_{gd}\) bridged an inverting output. Lowering \(R\) raises the fraction of \(C_{gs}\) that remains.",
                alternates=[
                    "Cgd+Cgs/(1+R*gm)",
                    "(Cgd*(1+gm*R)+Cgs)/(1+gm*R)",
                ],
            )),
            ("cd-freq-r3-q1", fresh(
                3, "find_error",
                r"A worked solution explains a follower's output impedance when the gate is driven through a large \(R_s\). Exactly one step is wrong.",
                [
                    r"With the input source set to zero, the gate returns to AC ground through \(R_s\).",
                    r"At low frequency \(C_{gs}\) is open, and the resistance looking into the source is about \(1/g_m\).",
                    r"At high frequency \(C_{gs}\) shorts the gate to the source, and that resistance climbs toward \(R_s\).",
                    r"A resistance that falls with frequency is capacitive, so it cannot resonate with a capacitive load.",
                ],
                3,
                r"The resistance rises with frequency, from about \(1/g_m\) toward \(R_s\). A rising impedance looks inductive, and that inductance can resonate with \(C_L\). \(g_m\) does not rise with frequency, and \(C_{gd}\) does not become negative. A gain below one does not forbid a resonance in the output impedance.",
                reasons=[
                    r"The output resistance rises with frequency, which is inductive, and it can resonate with \(C_L\).",
                    r"\(g_m\) rises with frequency, and that rise is what makes the output capacitive.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "cg-freq":
        return [
            ("cg-freq-r1-q1", fresh(
                1, "order",
                r"Order why a common-gate stage is usually wider than a common-source stage of the same gain. Each step after the first uses the result of the step before it.",
                [
                    r"The gate is an AC ground, so neither \(C_{gs}\) nor \(C_{gd}\) connects the source node to the drain node.",
                    r"Nothing is Miller-multiplied: \(C_{gs}\) loads the source, and \(C_{gd}\) loads the drain, each to ground.",
                    r"The source node sees \(R_s\) in parallel with \(1/g_m\), a small resistance, so its pole is high.",
                    r"The drain node sees the full load resistance, so the output pole is the one that usually sets the bandwidth.",
                ],
                r"The speed comes from the missing bridge, not from a larger \(g_m\) and not from a smaller output resistance. The stage still has capacitances. The input pole is rarely the dominant one, because the source resistance is at most \(1/g_m\). A Miller pole at the gate would require a capacitor from the input to a moving output, which this gate connection does not provide.",
            )),
            ("cg-freq-r2-q3", fresh(
                2, "sym",
                r"Write the radian frequency of the common-gate input pole when \(r_o\) is ignored. The capacitance at the source node is Cgs. Use gm, Rs, and Cgs.",
                "(1+gm*Rs)/(Rs*Cgs)",
                {"gm": (2e-4, 2e-2), "Rs": (20, 5e3), "Cgs": (5e-15, 2e-13)},
                r"The source node sees \(R_s\parallel 1/g_m\), so \(\omega_{in} = (1+g_mR_s)/(R_sC_{gs})\). Using \(R_s\) alone drops the device's own \(1/g_m\) and places the pole too low. \(1/(R_LC_{out})\) is the output pole and does not use these three quantities. Multiplying \(C_{gs}\) by the voltage gain would be a Miller term. This stage has no capacitor from the input to a moving output, so that factor is not here. \(g_m/C_{gs}\) is the limit only when \(R_s\) is large compared with \(1/g_m\).",
                alternates=[
                    "1/(Rs*Cgs)+gm/Cgs",
                    "(gm*Rs+1)/(Cgs*Rs)",
                ],
            )),
            ("cg-freq-r3-q2", fresh(
                3, "find_error",
                r"A worked solution says what a finite \(r_o\) does to a common-gate stage. Exactly one step is wrong.",
                [
                    r"With \(r_o\) infinite, the source node and the drain node do not share a resistive path through the channel.",
                    r"\(C_{gs}\) then loads only the source, and \(C_{gd}\) loads only the drain, each to AC ground.",
                    r"A finite \(r_o\) ties the drain back to the source, so the current in \(r_o\) depends on both node voltages.",
                    r"That tie inserts a bridging capacitor from the source to the drain, and \(C_{gd}\) is Miller-multiplied.",
                ],
                3,
                r"Finite \(r_o\) couples the nodes resistively. The input resistance becomes \((r_o+R_L)/(1+g_mr_o)\), so it depends on the load. It does not add a capacitor, and it does not Miller-multiply \(C_{gd}\). \(r_o\) also does not short the gate. The two-pole picture is then an approximation, not an unchanged result.",
                reasons=[
                    r"Finite \(r_o\) makes the input resistance depend on the load. It does not insert a bridging capacitor.",
                    r"\(r_o\) shorts the gate, so both poles disappear.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "ft":
        return [
            ("ft-r1-q1", fresh(
                1, "order",
                r"Order how the unity-gain frequency \(f_T\) of a MOSFET is defined. Each step after the first uses the result of the step before it.",
                [
                    r"Bias the device, and short the drain to AC ground so the measurement has no load.",
                    r"With the drain shorted, \(C_{gd}\) is another capacitance from the gate to AC ground, and it is not Miller-multiplied.",
                    r"Drive the gate with a small-signal current. The short-circuit current gain is \(g_m\) over \(\omega(C_{gs}+C_{gd})\), which falls as \(1/f\).",
                    r"\(f_T\) is the frequency where that current gain crosses 1, a property of the device and its bias.",
                ],
                r"\(f_T\) is a current gain with the drain AC-shorted, not the frequency where a common-source voltage gain falls to 1, and not the \(-3\ \mathrm{dB}\) frequency with the drain open. It is not the frequency where \(C_{gs}\) equals \(C_{gd}\). Opening the drain would let the load and a Miller factor into the result. Leaving out \(2\pi\) turns the same ratio into radians per second.",
            )),
            ("ft-r1-q3", fresh(
                1, "find_error",
                r"A worked solution scales the long-channel unity-gain frequency, overlap ignored. Exactly one step is wrong.",
                [
                    r"At a fixed overdrive, \(g_m\) is proportional to \(W/L\) and \(C_{gs}\) is proportional to \(WL\).",
                    r"\(W\) cancels in \(g_m/C_{gs}\), and so does \(C_{ox}\), which sits in both.",
                    r"What remains is proportional to \(\mu_n V_{ov}/L^2\), so doubling the overdrive doubles \(f_T\).",
                    r"Halving \(L\) at the same overdrive therefore doubles \(f_T\), because the length appears to the first power.",
                ],
                3,
                r"\(f_T\) scales as \(1/L^2\), so half the length multiplies \(f_T\) by four. Doubling the width does not change this long-channel result. Doubling the overdrive doubles \(f_T\); it does not quadruple it. Halving \(C_{ox}\) does nothing, because the oxide capacitance cancels. A short-channel device in velocity saturation is closer to \(1/L\), which is a different rule.",
                reasons=[
                    r"\(f_T\) scales as \(1/L^2\), so halving \(L\) multiplies \(f_T\) by four. Doubling \(W\) does not change it.",
                    r"The overdrive is squared, so halving \(L\) only doubles \(f_T\).",
                ],
                correct_reason=0,
            )),
            ("ft-r2-q2", fresh(
                2, "sym",
                r"Write \(f_T\) in hertz for a MOSFET with the drain AC-shorted. pi is the circle constant. Use gm, Cgs, and Cgd.",
                "gm/(2*pi*(Cgs+Cgd))",
                {"gm": (2e-4, 2e-2), "Cgs": (5e-15, 2e-13), "Cgd": (5e-16, 4e-14)},
                r"\(f_T = g_m/[2\pi(C_{gs}+C_{gd})]\). Both capacitances hang on the gate once the drain is shorted. Dropping \(2\pi\) leaves the radian frequency. Using \(C_{gs}\) alone drops \(C_{gd}\). \(g_m(C_{gs}+C_{gd})\) does not have the dimensions of a frequency. At fixed capacitances, doubling the bias current of a long-channel square-law device raises \(g_m\), and therefore \(f_T\), by \(\sqrt{2}\), not by 2. Width cancels in the long-channel limit and does not appear here.",
                alternates=[
                    "gm/(2*pi*Cgs+2*pi*Cgd)",
                    "gm*(2*pi*(Cgs+Cgd))**(-1)",
                ],
            )),
        ]
    if sid == "octc":
        return [
            ("octc-r1-q1", fresh(
                1, "sym",
                r"Write the resistance seen by \(C_{gd}\) in a common-source stage, with every other capacitor open and \(r_o\) ignored. The load resistance at the drain is RL. Use Rs, gm, and RL.",
                "Rs*(1+gm*RL)+RL",
                {"Rs": (100, 5e4), "gm": (2e-4, 2e-2), "RL": (200, 5e4)},
                r"A test source across \(C_{gd}\) sees \(R_s(1+g_mR_L)+R_L\). \(C_{gs}\) sees only \(R_s\), and the load capacitor sees only \(R_L\). Those are the other open-circuit resistances, not this one. \(g_mR_LR_s\) alone drops the two unmultiplied resistances, which still matter when the gain is modest. Shorting the other capacitors is the short-circuit time-constant method. The sum of each \(C_iR_{Ci}\) is \(b_1\), and the bandwidth estimate is \(1/b_1\).",
                alternates=[
                    "Rs+gm*Rs*RL+RL",
                    "Rs+RL*(1+gm*Rs)",
                ],
            )),
            ("octc-r1-q2", fresh(
                1, "order",
                r"Order how the open-circuit time-constant estimate is built. Each step after the first uses the result of the step before it.",
                [
                    r"Zero the independent sources: voltage sources become shorts, and current sources become opens.",
                    r"Open every capacitor except the one whose resistance you are finding.",
                    r"Apply a test source across that capacitor's own two terminals and read the resistance.",
                    r"Multiply each resistance by its capacitance, add those products, and estimate the dominant pole as the reciprocal.",
                ],
                r"Each resistance is found with the other capacitors open and the independent sources off. Shorting the other capacitors is a different method. The DC bias resistance at a node is not automatically \(R_{Ci}\), and the input source has to be off. The largest capacitance is not the term that limits the bandwidth; the largest product is. The sum estimates the dominant pole. It does not locate the second pole.",
            )),
            ("octc-r3-q2", fresh(
                3, "find_error",
                r"A worked solution says whether the open-circuit time-constant bandwidth estimate is high or low for an all-pole circuit. Exactly one step is wrong.",
                [
                    r"Each capacitor contributes \(C_iR_{Ci}\), with \(R_{Ci}\) found while every other capacitor is open.",
                    r"The sum of those time constants is \(b_1\), the coefficient of \(s\) in the denominator.",
                    r"\(b_1\) is also the sum of \(1/\omega_i\) over the poles, so it is at least \(1/\omega_1\).",
                    r"The estimate \(\omega_1 \approx 1/b_1\) therefore sits above the true dominant pole, and the estimate is optimistic.",
                ],
                3,
                r"\(b_1 = \sum 1/\omega_i\) is at least \(1/\omega_1\), so \(1/b_1\) is smaller than the true dominant pole. The bandwidth estimate is conservative. It is not exact just because there are two or more capacitors, and it is not unrelated to the bandwidth. The higher poles are what make \(b_1\) a little larger than \(1/\omega_1\).",
                reasons=[
                    r"\(1/b_1\) is below the true dominant pole, so the estimate is conservative.",
                    r"The estimate is exact for two or more capacitors, so it is neither high nor low.",
                ],
                correct_reason=0,
            )),
        ]
    raise SystemExit("no swaps for " + sid)


def fix_figures(bank):
    changed = False
    for q in bank["questions"]:
        pair = FIGURE_FIX.get(q["id"])
        if not pair:
            continue
        old, new = pair
        fig = q.get("figure") or ""
        if new in fig:
            continue
        if fig.count(old) != 1:
            raise SystemExit(q["id"] + " viewBox not found once")
        q["figure"] = fig.replace(old, new, 1)
        version = q.get("version")
        q["version"] = (version if isinstance(version, int) else 1) + 1
        changed = True
    return changed


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
    if fix_figures(bank):
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
