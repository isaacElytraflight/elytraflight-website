#!/usr/bin/env python3
"""SG-063 AC circuits: swap the most pattern-matchable MC items.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The verifier does not import this file.
"""
import json
import math
import os

from banklib import Bank
from templates import plot

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "tf",
    "phasors",
    "direct-h",
    "pole-zero",
    "rlc",
    "bode",
    "ac-power",
    "bode-circuits",
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


def falling_impedance():
    """A falling curve. The samples are not the graded expression."""
    svg = plot(lambda w: 1.0 / (0.4 + w), 0.0, 4.0, "f", "|Z|", "Impedance magnitude")
    alt = "A smooth curve of impedance magnitude that falls as frequency increases."
    return svg, alt


def resistor_power():
    """Rippling non-negative power. The drawing does not state the average."""
    svg = plot(lambda t: math.cos(t) ** 2, 0.0, 6.28, "t", "p", "Resistor power")
    alt = "Instantaneous power that stays non-negative and ripples twice per cycle."
    return svg, alt


Z_SVG, Z_ALT = falling_impedance()
P_SVG, P_ALT = resistor_power()


def swaps_for(sid):
    """(old mc id, replacement) in the order that assigns q4, then q5."""
    if sid == "tf":
        return [
            ("tf-r1-q1", fresh(
                1, "order",
                r"The system is linear, with constant coefficients, and it starts at rest. The polynomial that multiplies the output is not identically zero, and the input transform is not identically zero. Order the steps that produce \(H(s)=Y(s)/X(s)\). Each step after the first uses the result of the step before it.",
                [
                    r"Replace every derivative by a power of \(s\). The equation is now one polynomial in \(s\) times \(Y(s)\), equal to another polynomial in \(s\) times \(X(s)\).",
                    r"Divide both sides of that equation by the polynomial that multiplies \(Y(s)\), so \(Y(s)\) stands alone on the left.",
                    r"Divide both sides of that new equation by \(X(s)\).",
                    r"The quotient that remains is \(H(s)\).",
                ],
                r"Zero initial conditions are what let a derivative become a power of \(s\) with no extra terms. The first division uses that transformed equation, and the second division uses the equation it produced. The quotient of those two divisions is \(Y/X\). Multiplying the transforms, or dividing the polynomials in the other order, is a different function.",
            )),
            ("tf-r1-q2", fresh(
                1, "sym",
                r"A system at rest obeys \(a\,y''+b\,y'+c\,y = d\,x\). Write \(H(s)=Y(s)/X(s)\) using the name \(a\) for the coefficient of \(y''\), \(b\) for the coefficient of \(y'\), \(c\) for the coefficient of \(y\), \(d\) for the coefficient of \(x\), and \(s\) for the transform variable.",
                "d/(a*s^2+b*s+c)",
                {"a": (0.3, 6), "b": (0.3, 6), "c": (0.3, 6), "d": (0.3, 6), "s": (0.1, 4)},
                r"Each derivative brings one factor of \(s\), and the initial conditions contribute nothing because the system starts at rest. The input coefficient stays in the numerator and the output coefficients stay in the denominator. Swapping them writes the reciprocal, which is \(X/Y\).",
                alternates=["d/(a*s*s+b*s+c)", "d/(c+b*s+a*s^2)"],
            )),
            ("tf-r3-q2", fresh(
                3, "find_error",
                r"A forward block \(G(s)=K/(s+a)\), with \(a>0\) and \(K>0\), sits in a unity negative-feedback loop. A student finds the closed-loop transfer function. Exactly one step is wrong.",
                [
                    r"The forward path is \(G(s)\) and the feedback path is 1, so the loop gain is \(G(s)\).",
                    r"Negative feedback puts that loop gain in the denominator with a plus sign: \(G/(1+G)\).",
                    r"Substitute \(G=K/(s+a)\).",
                    r"The closed-loop transfer function is \(K/(s+a-K)\).",
                ],
                3,
                r"\(G/(1+G)\) with this \(G\) is \(K/(s+a+K)\). The minus sign would be the positive-feedback formula \(G/(1-G)\). Leaving the loop open would keep \(K/(s+a)\). The algebra that clears the inner denominator adds \(K\), it does not subtract it.",
                reasons=[
                    r"Negative unity feedback gives \(K/(s+a+K)\). The minus sign is the positive-feedback denominator.",
                    r"The closed-loop transfer function is \(K/(s+a)\).",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "phasors":
        return [
            ("phasors-r1-q1", fresh(
                1, "sym",
                r"An ideal capacitor \(C\) is used at angular frequency \(\omega\). Write the magnitude of its impedance using the name \(w\) for \(\omega\) and the name \(C\) for the capacitance.",
                "1/(w*C)",
                {"w": (0.2, 20), "C": (0.05, 5)},
                r"The impedance is \(1/(j\omega C)\). The factor \(j\) has magnitude 1, so the magnitude is \(1/(\omega C)\). Multiplying by \(\omega C\) is the admittance magnitude. A resistor's impedance does not depend on frequency.",
                alternates=["1/(C*w)"],
                fig=Z_SVG,
                alt=Z_ALT,
            )),
            ("phasors-r1-q2", fresh(
                1, "multi",
                r"Select every statement that is true as the angular frequency \(\omega\) approaches 0.",
                [
                    r"The magnitude of an ideal capacitor's impedance grows without bound.",
                    r"The magnitude of an ideal inductor's impedance grows without bound.",
                    r"The magnitude of an ideal inductor's impedance approaches 0.",
                    r"An ideal capacitor approaches a short circuit.",
                ],
                [0, 2],
                r"A capacitor's impedance magnitude is \(1/(\omega C)\), which grows as \(\omega\) falls, so the capacitor approaches an open circuit. An inductor's impedance magnitude is \(\omega L\), which vanishes at DC, so the inductor approaches a short. The two elements trade roles at high frequency, not at DC.",
            )),
            ("phasors-r3-q3", fresh(
                3, "order",
                r"Phasors use a cosine reference and peak values. Order the conversion of \(A\sin(\omega t+\phi)\) into its phasor. Each step after the first uses the result of the step before it.",
                [
                    r"Subtract \(90^\circ\) from the sine phase \(\phi\). Call the result \(\theta\).",
                    r"Rewrite the waveform as \(A\cos(\omega t+\theta)\) using that \(\theta\).",
                    r"Read the amplitude \(A\) and the phase \(\theta\) from that cosine.",
                    r"The peak phasor is the pair just read.",
                ],
                r"A sine is a cosine delayed by a quarter cycle, so \(\theta\) has to exist before the cosine can be written. The amplitude and the phase are read from that cosine, and the phasor is the pair that was read. Keeping the original sine phase reports a phasor \(90^\circ\) too high. Adding \(90^\circ\) instead of subtracting it points the other way.",
            )),
        ]
    if sid == "direct-h":
        return [
            ("direct-h-r1-q1", fresh(
                1, "sym",
                r"A series resistor \(R\) and capacitor \(C\) form a low-pass divider, with the output across the capacitor. Write \(|H(j\omega)|\) using the name \(w\) for \(\omega\), the name \(R\) for the resistance, and the name \(C\) for the capacitance.",
                "1/sqrt(1+(w*R*C)^2)",
                {"w": (0.1, 20), "R": (0.2, 8), "C": (0.05, 4)},
                r"The divider is \(Z_C/(R+Z_C)\) with \(Z_C=1/(j\omega C)\). Clearing \(j\omega C\) produces \(1/(1+j\omega RC)\), whose magnitude is \(1/\sqrt{1+(\omega RC)^2}\). Dropping the 1 under the square root is the high-frequency approximation. The phase is a different function.",
                alternates=["1/sqrt(1+w*w*R*R*C*C)", "(1+(w*R*C)^2)^(-0.5)"],
            )),
            ("direct-h-r1-q2", fresh(
                1, "order",
                r"Order the direct calculation of \(H(j\omega)\) for a linear RLC circuit in sinusoidal steady state. Each step after the first uses the result of the step before it.",
                [
                    r"Replace each inductor by \(j\omega L\), each capacitor by \(1/(j\omega C)\), and leave each resistor as \(R\).",
                    r"Using those impedances, write the output as the source times a ratio of impedances.",
                    r"The ratio that multiplies the source in that expression does not contain the source.",
                    r"That ratio is \(H(j\omega)\).",
                ],
                r"The impedances have to be in place before the output can be written as the source times a ratio. That ratio is the coefficient of the source in the expression just written, so it is identified from that expression, and it is \(H(j\omega)\). Starting from a differential equation, or from the circuit at DC, answers a different question.",
            )),
            ("direct-h-r2-q3", fresh(
                2, "find_error",
                r"A series resistor \(R\), inductor \(L\), and capacitor \(C\) is driven by \(v_s\). The output is the capacitor voltage. A student writes \(|H(j\omega)|\). Exactly one step is wrong.",
                [
                    r"The capacitor impedance is \(1/(j\omega C)\), and the series impedance is \(R+j\omega L+1/(j\omega C)\).",
                    r"The divider is the capacitor impedance divided by that series impedance.",
                    r"Clearing the common factor \(j\omega C\) produces \(1/(1-\omega^2 LC+j\omega RC)\).",
                    r"The magnitude is \(1/|1-\omega^2 LC|\), because a resistor does not change a capacitor voltage.",
                ],
                3,
                r"The cleared denominator is the complex number \(1-\omega^2 LC+j\omega RC\). Its magnitude is \(\sqrt{(1-\omega^2 LC)^2+(\omega RC)^2}\), so the resistor term stays inside the square root. Dropping it is the lossless formula. The sign in front of \(\omega^2 LC\) is already right; flipping it would move the resonance.",
                reasons=[
                    r"The resistor remains in the magnitude, as \((\omega RC)^2\) under the square root.",
                    r"The magnitude is \(1/|1+\omega^2 LC|\).",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "pole-zero":
        return [
            ("pole-zero-r1-q1", fresh(
                1, "order",
                r"\(H(s)=N(s)/D(s)\), and \(N\) and \(D\) share no common root. Order the reading of one real pole \(p=-a\) with \(a>0\) into its natural term. Each step after the first uses the result of the step before it.",
                [
                    r"Solve \(D(s)=0\) and take the real root \(p=-a\).",
                    r"The mode attached to that root is \(e^{pt}\).",
                    r"Substitute \(p=-a\) so the mode is \(e^{-at}\).",
                    r"That decaying exponential is the natural term of this pole.",
                ],
                r"The root has to be known before a mode can be attached to it. Substituting \(p=-a\) uses that mode. The decaying exponential is the result of the substitution, so it is last. A root of the numerator would be a zero and would not create this term. A positive real part would grow instead of decay.",
            )),
            ("pole-zero-r1-q2", fresh(
                1, "sym",
                r"A transfer function has one real pole at \(s=-a\) with \(a>0\). Write the natural term that pole contributes, using the name \(a\) for that positive number and the name \(t\) for time.",
                "exp(-a*t)",
                {"a": (0.2, 6), "t": (0.05, 3)},
                r"A pole at \(s=p\) contributes \(e^{pt}\). Here \(p=-a\), so the term is \(e^{-at}\). The sign in the exponent is the sign of the pole: a pole at \(+a\) would grow. The imaginary part, which this pole does not have, would have set an oscillation frequency rather than the decay.",
                alternates=["e**(-a*t)", "exp(-t*a)"],
            )),
            ("pole-zero-r1-q3", fresh(
                1, "find_error",
                r"A system has poles at \(s=-1\pm j3\). A student names the natural response. Exactly one step is wrong.",
                [
                    r"The poles are \(-1+j3\) and \(-1-j3\).",
                    r"The real part of each pole is \(-1\).",
                    r"The natural response contains \(e^{-t}\) times a sinusoid at \(3\ \mathrm{rad/s}\).",
                    r"The oscillation grows, because the imaginary part is not zero.",
                ],
                3,
                r"Growth or decay is the real part. Both poles have real part \(-1\), so the envelope is \(e^{-t}\). The imaginary part \(3\) is the oscillation frequency in radians per second. A growing oscillation would need a positive real part. A real pole would have no oscillation at all.",
                reasons=[
                    r"The imaginary part sets the frequency. The negative real part makes the envelope decay.",
                    r"The envelope is \(e^{3t}\).",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "rlc":
        return [
            ("rlc-r1-q1", fresh(
                1, "sym",
                r"A series circuit has an ideal inductance \(L\) and an ideal capacitance \(C\). Write the resonant frequency in radians per second using the name \(L\) for the inductance and the name \(C\) for the capacitance.",
                "1/sqrt(L*C)",
                {"L": (0.1, 4), "C": (0.1, 4)},
                r"Resonance is where the inductor and capacitor impedances cancel, \(\omega L=1/(\omega C)\), so \(\omega=1/\sqrt{LC}\). The resistance does not appear. Multiplying \(L\) by \(C\) without the reciprocal, or using \(R/L\), is a different rate.",
                alternates=["1/sqrt(C*L)", "(L*C)^(-0.5)"],
            )),
            ("rlc-r1-q2", fresh(
                1, "find_error",
                r"A student finds the input impedance of a series RLC circuit at its resonant frequency. Exactly one step is wrong.",
                [
                    r"The inductor impedance is \(j\omega L\) and the capacitor impedance is \(1/(j\omega C)\).",
                    r"At \(\omega=1/\sqrt{LC}\) those two impedances have equal magnitude and opposite sign.",
                    r"Their sum is 0.",
                    r"The input impedance is 0, because resonance cancels the resistor as well.",
                ],
                3,
                r"The inductor and the capacitor cancel each other, and the resistor is what remains. The input impedance at resonance is the real number \(R\), which is also the minimum of \(|Z|\). A short circuit would require \(R=0\). An open circuit is the parallel tank, not the series one.",
                reasons=[
                    r"The reactive parts cancel and the resistor remains, so the impedance is \(R\).",
                    r"The impedance is infinite.",
                ],
                correct_reason=0,
            )),
            ("rlc-r3-q1", fresh(
                3, "multi",
                r"In a series RLC circuit the output is taken across the resistor. \(R\) is doubled. \(L\) and \(C\) stay the same. Select every statement that is true.",
                [
                    r"The resonant frequency is unchanged.",
                    r"The quality factor is halved.",
                    r"The half-power bandwidth doubles.",
                    r"The peak gain at resonance is halved.",
                ],
                [0, 1, 2],
                r"The resonant frequency \(1/\sqrt{LC}\) does not involve \(R\). The quality factor of the series circuit is \(\omega_0 L/R\), so doubling \(R\) halves it, and the bandwidth \(\omega_0/Q=R/L\) doubles. At resonance the inductor and capacitor cancel, so the gain from the source to the resistor voltage is still 1.",
            )),
        ]
    if sid == "bode":
        return [
            ("bode-r2-q3", fresh(
                2, "order",
                r"Order the straight-line magnitude sketch of a first-order low-pass \(H=K/(1+j\omega/\omega_p)\) with \(K>0\) and \(\omega_p>0\). Each step after the first uses the result of the step before it.",
                [
                    r"Convert the low-frequency gain \(K\) into decibels.",
                    r"Draw that decibel level as a horizontal line from low frequency up to the break \(\omega_p\).",
                    r"From the decibel value at the break, drop \(20\ \mathrm{dB}\) for each decade above \(\omega_p\).",
                    r"Join the horizontal piece to that falling piece. The join is the magnitude asymptote.",
                ],
                r"The horizontal level is the decibel value of \(K\), so the conversion comes first. The falling ray starts at the break from that same level, so it cannot be drawn before the corner value exists. The asymptote is the join of the two pieces. A rise of \(20\ \mathrm{dB}\) per decade would be a zero, not this pole. The true curve sits \(3\ \mathrm{dB}\) below the corner; the asymptote itself does not.",
            )),
            ("bode-r1-q2", fresh(
                1, "sym",
                r"A Bode magnitude plot has a constant gain \(K>0\). Write that gain in decibels using the name \(K\).",
                "20*ln(K)/ln(10)",
                {"K": (0.2, 80)},
                r"Decibels are \(20\log_{10}(K)\). The natural log converts by \(\log_{10}(K)=\ln(K)/\ln(10)\). Using \(10\log_{10}\) is the power ratio, and it is half of this voltage or amplitude ratio. A gain of 100 is \(40\ \mathrm{dB}\), not \(20\ \mathrm{dB}\).",
                alternates=["20*log(K)/log(10)"],
            )),
            ("bode-r3-q2", fresh(
                3, "find_error",
                r"Compare \(H_L=1+j\omega/\omega_z\) with \(H_R=1-j\omega/\omega_z\), for \(\omega_z>0\) and \(\omega>0\). A student compares their Bode plots. Exactly one step is wrong.",
                [
                    r"Both factors have magnitude \(\sqrt{1+(\omega/\omega_z)^2}\).",
                    r"The phase of \(H_L\) is \(+\arctan(\omega/\omega_z)\).",
                    r"The phase of \(H_R\) is \(-\arctan(\omega/\omega_z)\).",
                    r"The two phase curves therefore match, because every zero contributes positive phase.",
                ],
                3,
                r"The magnitudes match, and above \(\omega_z\) both rise at \(+20\ \mathrm{dB}\) per decade. The phases are mirrors: the left-half-plane zero climbs toward \(+90^\circ\) and the right-half-plane zero falls toward \(-90^\circ\). Saying every zero has positive phase erases that mirror.",
                reasons=[
                    r"The phases are opposite. Only the left-half-plane zero climbs toward \(+90^\circ\).",
                    r"The right-half-plane zero has a falling magnitude.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "ac-power":
        return [
            ("ac-power-r1-q1", fresh(
                1, "find_error",
                r"A sinusoidal voltage is applied across an ideal capacitor. A student finds the average power over one cycle. Exactly one step is wrong.",
                [
                    r"In sinusoidal steady state the capacitor current leads the voltage by \(90^\circ\).",
                    r"Instantaneous power is the product \(v(t)i(t)\).",
                    r"That product oscillates at twice the drive frequency and has average zero.",
                    r"The average power is \(\tfrac{1}{2} V_p I_p\), the same product used for a resistor.",
                ],
                3,
                r"The factor \(\tfrac12 V_p I_p\) is the average power only when voltage and current are in phase. A \(90^\circ\) shift makes the average of the product zero: the capacitor stores energy for a quarter cycle and returns it over the next. Frequency changes the current, not that average. An ideal inductor does the same.",
                reasons=[
                    r"The quarter-cycle shift makes the average of \(v i\) zero. The in-phase formula does not apply.",
                    r"The average power is \(V_p I_p\).",
                ],
                correct_reason=0,
            )),
            ("ac-power-r1-q2", fresh(
                1, "sym",
                r"A resistor \(R\) is driven by \(v(t)=V_p\cos(\omega t)\), with \(V_p\) the peak voltage. Write the average power using the name \(Vp\) for \(V_p\) and the name \(R\) for the resistance.",
                "Vp^2/(2*R)",
                {"Vp": (0.5, 12), "R": (0.2, 20)},
                r"The average of \(\cos^2\) over a cycle is \(1/2\), so \(P=V_p^2/(2R)\). Using \(V_p^2/R\) forgets that average and treats the peak as if it were a DC voltage. Using \(V_p^2/(4R)\) replaces the peak by an RMS value and then halves a second time. The frequency does not appear.",
                alternates=["Vp*Vp/(2*R)", "(Vp^2)/(2*R)"],
                fig=P_SVG,
                alt=P_ALT,
            )),
            ("ac-power-r3-q1", fresh(
                3, "multi",
                r"Each element below is in sinusoidal steady state. Select every one that absorbs a positive average power.",
                [
                    r"A resistor with a sinusoidal voltage across it.",
                    r"An ideal capacitor.",
                    r"A series combination of a resistor and an inductor, with a nonzero resistance, carrying a sinusoidal current.",
                    r"An ideal inductor.",
                ],
                [0, 2],
                r"Average power is \(\tfrac12 \mathrm{Re}(V I^\ast)\) with peak phasors. A resistor has voltage and current in phase, so the real part is positive. An ideal capacitor or inductor has them a quarter cycle apart, so the average is zero. A series inductor does not remove the resistor's average power.",
            )),
        ]
    if sid == "bode-circuits":
        return [
            ("bode-circuits-r1-q1", fresh(
                1, "sym",
                r"An RC low-pass filter has \(H(s)=1/(1+s\tau)\) with \(\tau>0\). Write the pole location using the name \(tau\) for \(\tau\).",
                "-1/tau",
                {"tau": (0.05, 8)},
                r"The denominator is zero when \(1+s\tau=0\), so the pole is at \(s=-1/\tau\), on the negative real axis. The positive value \(+1/\tau\) is the break frequency on a frequency-response sketch, not the pole. A zero of this low-pass would require a root in the numerator, and the numerator is 1.",
                alternates=["-1/(tau)", "-(1/tau)"],
            )),
            ("bode-circuits-r2-q1", fresh(
                2, "find_error",
                r"An RC high-pass filter has \(H(s)=s\tau/(1+s\tau)\) with \(\tau=1\ \mathrm{ms}\). A student places its pole and zero. Exactly one step is wrong.",
                [
                    r"The numerator is zero at \(s=0\), so there is a zero at the origin.",
                    r"The denominator is zero at \(s=-1/\tau\).",
                    r"With \(\tau=1\ \mathrm{ms}\), that pole is at \(-1000\ \mathrm{rad/s}\).",
                    r"Above the pole the magnitude keeps rising at \(+20\ \mathrm{dB}\) per decade, because the zero's slope never stops.",
                ],
                3,
                r"The zero at the origin contributes \(+20\ \mathrm{dB}\) per decade, and the pole contributes \(-20\ \mathrm{dB}\) per decade. Above the pole those slopes cancel and the magnitude flattens. The zero and the pole locations in the first three steps are the right ones. A pole at \(+1000\) would be in the right half-plane.",
                reasons=[
                    r"Past the pole the \(+20\) and \(-20\ \mathrm{dB}\) per decade cancel, so the magnitude levels off.",
                    r"The pole is at \(+1000\ \mathrm{rad/s}\).",
                ],
                correct_reason=0,
            )),
            ("bode-circuits-r3-q1", fresh(
                3, "multi",
                r"A circuit has two capacitors, three resistors, and one independent voltage source. Select every statement that is true of its transfer function.",
                [
                    r"It has at most two poles.",
                    r"It has exactly two poles for every way of connecting those two capacitors.",
                    r"Two capacitors in parallel need not contribute two poles.",
                    r"Each resistor contributes one pole.",
                ],
                [0, 2],
                r"Each independent capacitor voltage can add one state, so two capacitors give at most two poles. Two capacitors in parallel share one voltage and behave as a single capacitor, so the count can be lower. A resistor does not add a state. An inductor is what would add a further pole, and this circuit has none.",
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
