#!/usr/bin/env python3
"""SG-063 op-amp non-idealities: swap the most pattern-matchable MC items.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The new questions use the same relations as the
explainers, and the explainer worked examples do not use these prompts.
The verifier does not import this file.

Symbolic ranges are closed boxes on which the key stays finite and keeps a
valid sign. No sampled point is a difference of two independent positives, so
a remainder cannot come out negative or pass through zero. Every denominator
is a sum or a product of quantities bounded away from zero.
"""
import json
import os

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "offset",
    "bias-current",
    "opamp-fr",
    "slew",
    "noise-dist",
    "datasheet",
]

# Axis label sits at y=136 inside a 135-tall viewBox. Widen once.
CLIPPED_VIEWBOX = 'viewBox="0 0 340 135"'
FIXED_VIEWBOX = 'viewBox="0 0 340 148"'


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
    if sid == "offset":
        return [
            ("offset-r1-q1", fresh(
                1, "order",
                r"Order how a feedback amplifier with its signal source grounded turns the input offset into an output voltage. Each step after the first uses the result of the step before it.",
                [
                    r"Model \(V_{os}\) as a DC source in series with one input of an otherwise ideal op-amp. The sign differs from part to part and stays fixed on a given part.",
                    r"With the signal source grounded, that source is the only voltage the loop has to accommodate.",
                    r"Negative feedback drives the differential input toward zero, the same action as a non-inverting stage of gain \(1+R_2/R_1\).",
                    r"The output therefore sits near \(V_{os}(1+R_2/R_1)\). The inverting signal gain \(-R_2/R_1\) is not the gain this source sees.",
                ],
                r"Offset is a DC input error, so the loop amplifies it by the noise gain \(1+R_2/R_1\), whether the signal path is inverting or not. Multiplying by \(-R_2/R_1\) uses the signal gain and invents a sign the datasheet does not fix. Treating \(V_{os}\) as a source already at the output skips the gain. An AC source would be specified per root hertz and would not sit at one DC value. Open loop, the same millivolt times \(A_0\) rails the output instead of stopping at the noise gain.",
            )),
            ("offset-r2-q3", fresh(
                2, "find_error",
                r"A worked solution budgets the output offset of an inverting stage from a datasheet offset of a few millivolts. Exactly one step is wrong.",
                [
                    r"The datasheet number is a bound on the magnitude. The sign is random from part to part, and it stays fixed on a given part.",
                    r"With the signal input grounded, \(V_{os}\) is the only input the feedback loop sees.",
                    r"An inverting stage of signal gain \(-R_2/R_1\) therefore multiplies that offset by \(-R_2/R_1\), so every part produces the same negative output offset.",
                    r"The output offset to budget is the datasheet magnitude times the noise gain \(1+R_2/R_1\), and the sign is not known before the part is measured.",
                ],
                2,
                r"A grounded signal leaves \(V_{os}\) as a source at the input. Feedback amplifies it by \(1+R_2/R_1\), the gain from the non-inverting side, even when the signal path is inverting. \(-R_2/R_1\) is the signal gain and also invents a sign. Reading the datasheet number as an output voltage skips the noise gain. Reading it as a guaranteed positive value on every part ignores the random mismatch. Temperature drift changes the magnitude later; it does not fix the sign.",
                reasons=[
                    r"Offset sees the noise gain \(1+R_2/R_1\), not the inverting signal gain, and the datasheet does not fix the sign.",
                    r"The inverting signal gain sets the offset too, so a gain of \(-10\) produces \(-10\) times the datasheet offset on every part.",
                ],
                correct_reason=0,
            )),
            ("offset-r3-q1", fresh(
                3, "sym",
                r"Write the output offset of a feedback amplifier with the signal source grounded. The offset is amplified by the noise gain, in either the inverting or the non-inverting connection. Use Vos, R1, and R2.",
                "Vos*(1+R2/R1)",
                # All three stay positive, so 1+R2/R1 stays above 1 and the product cannot change sign or hit zero.
                {"Vos": (2e-4, 6e-3), "R1": (400, 6000), "R2": (400, 80000)},
                r"With the signal grounded, \(V_{os}\) is amplified by \(1+R_2/R_1\). \(V_{os} R_2/R_1\) drops the 1 and keeps only the extra term. \(-V_{os} R_2/R_1\) applies the inverting signal gain, which is the wrong gain and the wrong sign. \(V_{os}\) alone is the follower result, the case \(R_2 = 0\). \(A_0 V_{os}\) is the open-loop product, which saturates rather than equaling this closed-loop offset.",
                alternates=["Vos*(R1+R2)/R1", "Vos*(1+R2*R1**(-1))", "(Vos*(R1+R2))/R1"],
            )),
        ]
    if sid == "bias-current":
        return [
            ("bias-current-r1-q1", fresh(
                1, "sym",
                r"Write the resistor \(R_3\) from the \(+\) input to ground that gives that input the same DC resistance the inverting network presents. \(R_1\) returns to ground and \(R_2\) is the feedback resistor. Use R1 and R2.",
                "R1*R2/(R1+R2)",
                # Both resistances stay positive, so the sum in the denominator is at least 20500 and the parallel result stays positive.
                {"R1": (500, 20000), "R2": (20000, 400000)},
                r"The inverting side, with the signal grounded, presents \(R_1 \parallel R_2 = R_1 R_2/(R_1+R_2)\). Matching \(R_3\) to that value lets equal bias currents drop equal voltages. \(R_1+R_2\) is the series sum, too large, and it leaves a residual from the average bias current. \(R_1\) alone, or \(R_2\) alone, matches only one of the two resistors. The remaining error after this match is set by \(I_{OS} R_2\), not by \(R_3\) itself.",
                alternates=["1/(1/R1+1/R2)", "(R1*R2)/(R2+R1)", "R2/(1+R2/R1)"],
            )),
            ("bias-current-r2-q3", fresh(
                2, "order",
                r"Order why \(R_3 = R_1 \parallel R_2\) removes the output error from equal input bias currents. Each step after the first uses the result of the step before it.",
                [
                    r"Each input draws a DC bias current even when both pins are held at 0 V.",
                    r"\(R_3 = R_1 \parallel R_2\) gives the \(+\) input the same resistance the inverting network presents at DC.",
                    r"Equal currents in equal resistances then drop the same voltage, so the differential voltage from the matched currents is about zero.",
                    r"The loop is left with the mismatch only, and the remaining output error is about \(I_{OS} R_2\).",
                ],
                r"Matched bias currents cancel when both inputs see \(R_1 \parallel R_2\). The currents still flow: \(R_3\) does not block them, and it does not change the signal gain. \(R_3 = R_1+R_2\) is the series sum, not the resistance the inverting side presents. Without \(R_3\), the \(+\) input is grounded and the output shifts by about \(I_B R_2\), which uses \(R_2\) rather than \(R_1\). An infinite input resistance does not remove these currents.",
            )),
            ("bias-current-r3-q3", fresh(
                3, "find_error",
                r"A worked solution explains the input bias current of an op-amp whose input resistance is infinite. Exactly one step is wrong.",
                [
                    r"Bipolar input transistors need a DC base current to stay in the forward-active region.",
                    r"That current is modeled as a source at each input pin, and it flows with both pins held at 0 V.",
                    r"Infinite input resistance forces those currents to zero, because no current can enter an infinite resistance.",
                    r"The resistance and the bias current are separate models. A CMOS input is small because the gate draws almost no DC current, not because a resistance number forbids the source.",
                ],
                2,
                r"\(I_B\) is the current the input devices require. It is drawn with the pins at the same voltage, so it is not \(v/R_{in}\). Setting \(R_{in}\) to infinity removes the resistive loading and leaves the bias sources in place. A CMOS input is tiny because a gate has almost no DC current, which is a device fact, not a consequence of quoting a large resistance. Offset voltage is a different error: a series voltage, not these currents.",
                reasons=[
                    r"Bias current is a device current, modeled as a source. It is not the current through \(R_{in}\), so an infinite \(R_{in}\) does not set it to zero.",
                    r"Infinite input resistance means zero input current of every kind, including bias current.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "opamp-fr":
        return [
            ("opamp-fr-r1-q1", fresh(
                1, "order",
                r"Order how a single-pole op-amp reaches a phase of \(-90^\circ\) well above its dominant pole. Each step after the first uses the result of the step before it.",
                [
                    r"The open-loop gain is \(A_0/(1+j\omega/\omega_p)\), with one pole at \(\omega_p\).",
                    r"Far above \(\omega_p\) the 1 in the denominator is negligible, leaving \(A_0 \omega_p/(j\omega)\).",
                    r"The product \(A_0 \omega_p\) is the unity-gain frequency \(\omega_u\), so the gain is \(\omega_u/(j\omega)\).",
                    r"Dividing by \(j\) is a phase of \(-90^\circ\). One pole can move the phase by only that much, so it never reaches \(-180^\circ\).",
                ],
                r"Above the dominant pole the op-amp is an integrator, phase \(-90^\circ\). The phase is \(-45^\circ\) only at the pole itself, not everywhere above it. \(-180^\circ\) would take a second pole. A phase of \(0^\circ\) is the low-frequency result, where the denominator is still real. The closed-loop bandwidth is a different frequency: it sits near \(f\,\omega_u\), not at \(\omega_p\).",
            )),
            ("opamp-fr-r1-q3", fresh(
                1, "sym",
                r"Write the approximate closed-loop bandwidth of an inverting amplifier built on a single-pole op-amp. The noise gain is \(1+R_2/R_1\), and the unity-gain frequency is \(\omega_u\). Use wu, R1, and R2.",
                "wu/(1+R2/R1)",
                # R1 and R2 stay positive, so the noise gain stays above 1 and the bandwidth stays positive and below wu.
                {"wu": (2e5, 5e7), "R1": (800, 8000), "R2": (800, 60000)},
                r"The closed-loop corner is \(\omega_u\) divided by the noise gain \(1+R_2/R_1\), not by the signal gain \(R_2/R_1\). Multiplying \(\omega_u\) by \(1+R_2/R_1\) would make a higher gain faster, which is backwards. \(\omega_u\) itself is the follower bandwidth, the case \(R_2 = 0\). The open-loop pole \(\omega_u/A_0\) is far below this closed-loop corner. For a large ratio the noise gain and the signal gain nearly agree, which is why the gain-bandwidth product is quoted as \(\omega_u\).",
                alternates=["wu/((R1+R2)/R1)", "wu*R1/(R1+R2)", "wu/(1+R2*R1**(-1))"],
            )),
            ("opamp-fr-r3-q1", fresh(
                3, "find_error",
                r"A worked solution describes a non-inverting amplifier above its closed-loop bandwidth. Exactly one step is wrong.",
                [
                    r"The closed-loop gain is \(A/(1+Af)\), flat near \(1/f\) at low frequency.",
                    r"That flat region ends near \(f\,\omega_u\), where the falling open-loop curve meets \(1/f\).",
                    r"Well above that corner the loop gain is still large, so the closed-loop magnitude stays flat at \(1/f\) all the way to \(\omega_u\).",
                    r"Once \(|Af|\) drops below 1, feedback stops holding the gain, and the closed-loop curve lies on the open-loop curve, falling at 20 dB/decade.",
                ],
                2,
                r"\(A_{CL}=A/(1+Af)\) stays near \(1/f\) only while \(|Af|\) is large. Past \(f\,\omega_u\), \(|Af|<1\) and \(A_{CL}\approx A\), on the open-loop \(-20\) dB/decade line. A slope of \(-40\) dB/decade would need a second pole. The curve does not climb back toward the open-loop DC gain. Staying flat out to \(\omega_u\) would require the loop gain to remain large, which is the claim that fails.",
                reasons=[
                    r"Above \(f\,\omega_u\) the loop gain is below 1, so the closed-loop curve merges with \(|A|\approx\omega_u/\omega\) instead of staying flat.",
                    r"The closed-loop gain stays at \(1/f\) until the unity-gain frequency, because feedback remains strong across that whole span.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "slew":
        return [
            ("slew-r1-q1", fresh(
                1, "order",
                r"Order why a large fast sine wave comes out of a slew-limited op-amp looking like a triangle. Each step after the first uses the result of the step before it.",
                [
                    r"A sine of peak \(V_p\) has its steepest slope \(\omega V_p\) at the zero crossings.",
                    r"The compensation capacitor can be charged only by a limited current, so the output slope cannot exceed the slew rate.",
                    r"When \(\omega V_p\) is larger than that slew rate, the output cannot follow the steep parts of the sine.",
                    r"Those parts become straight ramps at \(+SR\) and \(-SR\), and the waveform looks triangular rather than sinusoidal.",
                ],
                r"Slewing replaces the steep parts of a large sine with ramps at \(\pm SR\). A bandwidth limit is linear and would leave a smaller, phase-shifted sine. Clipping at the rails limits the voltage, not the slope, and flattens the peaks rather than making a triangle. The ramp time of a step is \(\Delta V/SR\), a different use of the same cap. Full-power bandwidth is the frequency where \(\omega V_p\) equals \(SR\), not a frequency where every amplitude is already a triangle.",
            )),
            ("slew-r1-q3", fresh(
                1, "find_error",
                r"A worked solution compares a bandwidth limit with slew-rate limiting for a large sine. Exactly one step is wrong.",
                [
                    r"A small-signal bandwidth limit is linear: it changes the amplitude and phase of a sine and leaves the shape sinusoidal.",
                    r"Slew rate is a hard cap on output slope, set by the current available to charge the compensation capacitor.",
                    r"A sine whose steepest slope exceeds the slew rate is therefore still a clean sine, only smaller and phase-shifted.",
                    r"The parts steeper than the slew rate become straight ramps, so the output grows harmonics and can look triangular.",
                ],
                2,
                r"Bandwidth limiting stays linear and preserves a sine. Slewing does not: once \(\omega V_p\) exceeds \(SR\), the output follows \(\pm SR\) instead of the sine and the spectrum grows harmonics. The effect depends on amplitude. A full-scale sine can slew at a frequency where a small sine is only bandwidth-limited. Rail clipping is a voltage limit, not this slope limit.",
                reasons=[
                    r"Exceeding the slew rate is nonlinear. The steep parts become ramps, so the output is not a phase-shifted copy of the sine.",
                    r"Any limit that reduces a sine, bandwidth or slew, leaves a clean sine of smaller amplitude.",
                ],
                correct_reason=0,
            )),
            ("slew-r2-q3", fresh(
                2, "sym",
                r"Write the full-power bandwidth: the highest frequency at which a sine of peak \(V_p\) still has a maximum slope no larger than the slew rate. \(SR\) is in volts per second and \(V_p\) is in volts, so the result is in hertz. Use SR and Vp.",
                "SR/(2*pi*Vp)",
                # SR and Vp stay positive, so the quotient stays positive. pi is the constant, not a sampled variable.
                {"SR": (2e5, 4e7), "Vp": (0.4, 10)},
                r"The steepest slope of \(V_p\sin\omega t\) is \(\omega V_p\). Setting that equal to \(SR\) gives \(f = SR/(2\pi V_p)\). \(SR/(2\pi)\) drops the amplitude and is the bandwidth only for a 1 V peak. \(SR/V_p\) is a radian rate and is missing the \(2\pi\) that converts it to hertz. Putting the peak-to-peak swing in place of \(V_p\) halves the bandwidth. \(SR\) times \(V_p\) is not a frequency.",
                alternates=["(SR/Vp)/(2*pi)", "SR*(2*pi*Vp)**(-1)", "SR/(pi*2*Vp)"],
            )),
        ]
    if sid == "noise-dist":
        return [
            ("noise-dist-r1-q2", fresh(
                1, "sym",
                r"Write the RMS noise voltage of white input noise with density \(e_n\), integrated over a bandwidth \(B\). Use en and B.",
                "en*sqrt(B)",
                # en and B stay positive, so the square root is defined and the product cannot change sign or vanish.
                {"en": (2e-9, 4e-8), "B": (2000, 500000)},
                r"The density \(e_n\) is in volts per root hertz, so the RMS voltage in a flat band is \(e_n\sqrt{B}\). Multiplying by \(B\) treats the density as if it were already a voltage per hertz and overstates the noise by \(\sqrt{B}\). Dividing by \(B\), or by \(\sqrt{B}\), goes the wrong direction. \(e_n\) alone is the density, not the integrated voltage. Two uncorrelated contributions still have to be combined as the square root of a sum of squares after each one is integrated this way.",
                alternates=["sqrt(B)*en", "en*B**(1/2)"],
            )),
            ("noise-dist-r1-q1", fresh(
                1, "order",
                r"Order what a square-law term does to a pure cosine. Each step after the first uses the result of the step before it.",
                [
                    r"The square of \(\cos\omega t\) is \(\frac{1}{2}+\frac{1}{2}\cos 2\omega t\).",
                    r"The constant term is a DC shift, present even though the input cosine had no DC.",
                    r"The double-frequency term is a second harmonic at \(2\omega\).",
                    r"The original frequency \(\omega\) is absent from the square. It appears only when a linear term sits beside the square-law term.",
                ],
                r"Squaring \(\cos\omega t\) produces DC and \(2\omega\), not the fundamental and not the third harmonic. A cubic term is what produces \(3\omega\). A random noise waveform does not create these discrete lines: a harmonic is deterministic distortion. Dropping the constant term misses the even-order DC shift. An odd-symmetric curve has no square-law term, so it produces neither this DC nor this second harmonic.",
            )),
            ("noise-dist-r2-q3", fresh(
                2, "find_error",
                r"A worked solution adds two op-amp errors that both sit at the input. Exactly one step is wrong.",
                [
                    r"Offset is one DC voltage for a given part. Its sign varies from part to part and does not fluctuate in time.",
                    r"Input noise is a random waveform, quoted as a density in volts per root hertz and turned into an RMS value over the bandwidth.",
                    r"Two uncorrelated noise voltages add by summing those RMS values, the same way two DC offsets of known sign would add.",
                    r"Uncorrelated noise adds in power, so the total RMS is the square root of the sum of the squares, and that total is still noise rather than an offset.",
                ],
                2,
                r"Offset is a fixed DC value. Noise fluctuates and is integrated from its density with a square root of bandwidth. Two uncorrelated contributions combine as \(\sqrt{v_1^2+v_2^2}\), not as \(v_1+v_2\). Adding the RMS values is right only for fully correlated sources. Multiplying the density by \(B\) instead of \(\sqrt{B}\) confuses power with voltage. Feedback can shrink distortion inside the loop, but it does not turn the noise into a DC offset.",
                reasons=[
                    r"Uncorrelated noise adds in power. Summing the RMS values treats them like a pair of signed DC offsets.",
                    r"RMS noise voltages add directly, because every random voltage combines the way a pair of DC sources does.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "datasheet":
        return [
            ("datasheet-r1-q1", fresh(
                1, "sym",
                r"Write the approximate closed-loop bandwidth of a non-inverting stage whose ideal gain is \(G\), for a single-pole op-amp whose gain-bandwidth product is GBW. Use GBW and G.",
                "GBW/G",
                # G stays at least 2, so the denominator cannot vanish and the bandwidth stays strictly below GBW.
                {"GBW": (2e6, 4e8), "G": (2, 80)},
                r"On a single-pole op-amp the closed-loop bandwidth is about \(GBW/G\) for a non-inverting gain \(G\). \(GBW\) times \(G\) would make a higher gain faster. \(GBW\) alone is the follower bandwidth, the case \(G = 1\). The slew-rate limit is a separate line and does not appear in this small-signal bandwidth. Offset and input resistance are DC specs; they do not set the corner.",
                alternates=["GBW*G**(-1)", "1/(G/GBW)", "GBW*(1/G)"],
            )),
            ("datasheet-r3-q3", fresh(
                3, "order",
                r"Order why a faster op-amp draws more supply current. Each step after the first uses the result of the step before it.",
                [
                    r"Both the gain-bandwidth product and the slew rate are set by how fast an internal capacitor can be charged.",
                    r"Charging that capacitor quickly takes current: the slew rate is about that current over the capacitance, and the transconductance that sets the gain-bandwidth product also rises with bias current.",
                    r"A part with a much higher gain-bandwidth product and slew rate therefore runs at a much higher supply current.",
                    r"A part biased at a tiny supply current has to give that speed up. The speed lines and the supply-current line move together.",
                ],
                r"Speed and supply current are tied by the current available to charge the compensation capacitor. A faster part does not draw less current. Supply current is not independent of the speed lines, and a micropower part is not the one with the higher slew rate. Offset and noise are separate lines; they do not set this speed-versus-current trade.",
            )),
            ("datasheet-r4-q3", fresh(
                4, "find_error",
                r"A worked solution says how to read the input-offset line on an op-amp datasheet. Exactly one step is wrong.",
                [
                    r"The input stage is a differential pair: two devices that are drawn as identical.",
                    r"Real devices mismatch by a random amount, so the voltage that balances the pair is a different number on every part.",
                    r"The datasheet therefore lists one fixed polarity, the same sign on every unit, equal to the typical value.",
                    r"What the line actually gives is a statistical bound on the magnitude. The sign is not known until that part is measured.",
                ],
                2,
                r"Offset comes from random mismatch between the two halves of the input pair, so the sign differs from part to part. A datasheet maximum is a bound on that magnitude, not a guaranteed positive voltage and not the output offset. The circuit still multiplies it by the noise gain. Supply polarity does not set the offset sign, and the offset does not follow the signal.",
                reasons=[
                    r"Mismatch is random, so the offset sign is not fixed. The datasheet number is a statistical bound on the magnitude.",
                    r"The datasheet polarity is the sign every unit ships with, so the typical value can be dropped straight into the gain formula.",
                ],
                correct_reason=0,
            )),
        ]
    raise SystemExit("no swaps for " + sid)


def widen_clipped_figures(bank):
    changed = False
    for q in bank["questions"]:
        fig = q.get("figure")
        if isinstance(fig, str) and CLIPPED_VIEWBOX in fig:
            q["figure"] = fig.replace(CLIPPED_VIEWBOX, FIXED_VIEWBOX, 1)
            q["version"] = int(q.get("version") or 1) + 1
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
        if rnd == 4:
            preview = old.get("preview")
            if not preview:
                raise SystemExit(old_id + " is round 4 and has no preview to copy")
            new["preview"] = list(preview)
        if not isinstance(old.get("version"), int):
            old["version"] = 1
        retired.append(old)
        bank["questions"][idx] = new
        live[new["id"]] = idx
        del live[old_id]
        changed = True
    if widen_clipped_figures(bank):
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
