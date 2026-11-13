#!/usr/bin/env python3
"""SG-063 chapter 1 of EE 105: swap the most pattern-matchable MC items.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The verifier does not import this file.
"""
import json
import os
import re

from banklib import Bank
from templates import plot

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "lti-def",
    "rc-lpf",
    "cx-exp",
    "sinusoid-resp",
    "impulse-conv",
    "step-resp",
    "freq-char",
    "lti-circuits",
    "freq-resp-circuits",
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


def cap_impedance_figure():
    """A falling magnitude. The curve does not state the expression."""
    svg = plot(lambda w: 1.0 / (1.0 + w), 0.0, 4.0, "f", "|Z|", "Impedance magnitude")
    alt = "A smooth curve of impedance magnitude that falls as frequency increases."
    return svg, alt


CAP_SVG, CAP_ALT = cap_impedance_figure()


def swaps_for(sid):
    """(old mc id, replacement) in the order that assigns q4, then q5."""
    if sid == "lti-def":
        return [
            ("lti-def-r1-q1", fresh(
                1, "order",
                "Put these checks in the order used to test whether a system is linear.",
                [
                    "Drive the system with two inputs separately and record each output.",
                    "Drive it with one weighted sum of those same two inputs.",
                    "Form that same weighted sum from the two recorded outputs.",
                    "Compare the prediction with the output the weighted sum actually produced.",
                ],
                "Superposition is a prediction: the response to a sum has to equal the sum of the responses. The separate runs come first, or there is nothing to add. The comparison is last, because it is the test rather than a setup step. Adding the outputs before the inputs have been applied skips the prediction the definition asks for.",
            )),
            ("lti-def-r2-q1", fresh(
                2, "multi",
                "Select every system that is linear. Time invariance is not required. The input is \\(x(t)\\) and the output is \\(y(t)\\).",
                [
                    r"\(y(t) = 4x(t-3)\)",
                    r"\(y(t) = x(t) + 6\)",
                    r"\(y(t) = t\,x(t)\)",
                    r"\(y(t) = x(t)\,|x(t)|\)",
                ],
                [0, 2],
                "A constant-gain delay passes scaling and addition straight through, and so does multiplication by the clock reading \\(t\\). Both are linear. Adding 6 fails because a zero input does not produce a zero output, and doubling the input does not double the output. The product \\(x|x|\\) squares the size, so doubling a positive input multiplies the output by four.",
            )),
            ("lti-def-r3-q2", fresh(
                3, "find_error",
                r"A student tests \(y(t) = x(3t)\). Exactly one step is wrong.",
                [
                    r"The map is linear: the response to \(a x_1 + b x_2\) is \(a y_1 + b y_2\), because every term is read at the same time argument \(3t\).",
                    r"An input delayed by \(t_0\) is \(x(t-t_0)\), and the system returns \(x(3t-t_0)\).",
                    r"Delaying the original output instead gives \(x(3(t-t_0)) = x(3t-3t_0)\).",
                    "Those two signals match for every delay, so the system is time-invariant.",
                ],
                3,
                r"Linearity does hold: a sum is evaluated at \(3t\) on both sides. Time invariance does not. The response to a delayed input is \(x(3t-t_0)\), while the delayed response is \(x(3t-3t_0)\). Those agree for every delay only when the factor in front of \(t\) is 1. The factor 3 compresses time; it does not break superposition.",
                reasons=[
                    r"The delayed input is compressed about the origin, while a delayed output is compressed about \(t_0\), so the waveforms differ.",
                    "The factor 3 makes the system nonlinear.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "rc-lpf":
        return [
            ("rc-lpf-r1-q1", fresh(
                1, "sym",
                r"A capacitor starts at voltage \(V_i\) and a constant source settles it at \(V_f\). The time constant is \(\tau\). For \(t>0\), write \(v_o(t)\) using the name \(Vf\) for \(V_f\), the name \(Vi\) for \(V_i\), the name \(t\) for time, and the name \(tau\) for \(\tau\).",
                "Vf+(Vi-Vf)*exp(-t/tau)",
                {"Vf": (-5, 12), "Vi": (-5, 12), "t": (0.05, 4), "tau": (0.1, 3)},
                r"The stored voltage closes the gap \(V_i-V_f\) by the factor \(e^{-t/\tau}\), so \(v_o = V_f + (V_i-V_f)e^{-t/\tau}\). Writing \(V_f e^{-t/\tau}\) drops the settled value and decays toward 0. Writing \(V_i(1-e^{-t/\tau})\) is only the special case that starts at 0 and ends at \(V_i\).",
                alternates=[
                    "Vf+(Vi-Vf)*e**(-t/tau)",
                    "Vi*exp(-t/tau)+Vf*(1-exp(-t/tau))",
                ],
            )),
            ("rc-lpf-r2-q3", fresh(
                2, "find_error",
                r"A student describes the steady output of an RC low-pass filter at \(\omega = 1/\tau\). Exactly one step is wrong.",
                [
                    r"The frequency response is \(H(j\omega) = 1/(1+j\omega\tau)\).",
                    r"At \(\omega\tau = 1\), this equals \(1/(1+j)\).",
                    r"The magnitude is \(1/\sqrt{2}\), about 0.707 times the input.",
                    r"The phase is \(-90^\circ\), because a capacitor's current leads its voltage by a right angle.",
                ],
                3,
                r"\(1+j\) has equal real and imaginary parts, so its angle is \(45^\circ\), and inverting it makes the output lag by \(45^\circ\). That lag, together with the factor \(1/\sqrt{2}\), is the cutoff. A \(-90^\circ\) shift would need a purely imaginary denominator. The magnitude \(1/\sqrt{2}\) is the right one; half amplitude is a higher frequency than the cutoff.",
                reasons=[
                    r"The denominator \(1+j\) sits at \(+45^\circ\), so the output lags by \(45^\circ\), not \(90^\circ\).",
                    r"The magnitude at this frequency is \(1/2\).",
                ],
                correct_reason=0,
            )),
            ("rc-lpf-r1-q2", fresh(
                1, "order",
                r"The capacitor is uncharged. At \(t=0\) a constant source \(V_s\) is connected through \(R\). Order the derivation of \(v_o(t)\). Each step uses the result of the step before it.",
                [
                    r"The series resistor and capacitor give the node equation \(RC\,v'+v = V_s\).",
                    r"The general solution of that equation is \(V_s + A e^{-t/(RC)}\).",
                    r"The capacitor voltage is continuous and started at 0, so set that general solution equal to 0 at \(t=0\). This forces \(A = -V_s\).",
                    r"Substitute that constant to obtain \(v_o(t) = V_s(1-e^{-t/(RC)})\).",
                ],
                r"The node equation has to be written before it can be solved. The general solution still has a free constant, so the continuity condition is applied to that expression and cannot come first. The waveform is what remains after the constant is known. A growing exponential would run away from \(V_s\) instead of approaching it.",
            )),
        ]
    if sid == "cx-exp":
        return [
            ("cx-exp-r2-q2", fresh(
                2, "sym",
                r"One phasor has magnitude \(r\) and angle \(a\) radians. Another has magnitude \(s\) and angle \(b\) radians. Write the real part of their product, using the names \(r\), \(s\), \(a\), and \(b\).",
                "r*s*cos(a+b)",
                {"r": (0.3, 4), "s": (0.3, 4), "a": (-2, 2), "b": (-2, 2)},
                "Magnitudes multiply and angles add. The real part of a phasor is its magnitude times the cosine of its angle, so the product contributes \\(rs\\cos(a+b)\\). Sine of the summed angle is the imaginary part. Adding the magnitudes, or multiplying the cosines of the separate angles, is rectangular arithmetic applied to the wrong form.",
                alternates=["s*r*cos(b+a)", "r*s*cos(b+a)"],
            )),
            ("cx-exp-r1-q2", fresh(
                1, "find_error",
                r"A student evaluates \(|e^{j\omega t}|\) for real \(\omega\) and \(t\). Exactly one step is wrong.",
                [
                    r"Euler's formula writes \(e^{j\omega t} = \cos(\omega t) + j\sin(\omega t)\).",
                    r"The magnitude is \(\sqrt{\cos^2(\omega t)+\sin^2(\omega t)}\).",
                    r"The identity \(\cos^2+\sin^2 = 1\) makes that square root equal to 1.",
                    r"Therefore \(|e^{j\omega t}| = e^{\omega t}\), because an exponential grows with its exponent.",
                ],
                3,
                r"A real exponential \(e^{\sigma t}\) has magnitude \(e^{\sigma t}\). Here the exponent is \(j\omega t\), whose real part is 0, so the magnitude is \(e^{0} = 1\). The sine and cosine already showed that. Replacing the imaginary exponent by \(\omega t\) confuses the speed of rotation with growth.",
                reasons=[
                    r"The exponent is imaginary, so the point stays on the unit circle. \(e^{\omega t}\) is the magnitude only for a real exponent.",
                    r"The magnitude is the arc length \(\omega t\).",
                ],
                correct_reason=0,
            )),
            ("cx-exp-r1-q1", fresh(
                1, "order",
                r"A principal arctangent returns only a value between \(-\pi/2\) and \(\pi/2\). Order the conversion of a nonzero number \(a+jb\) into polar form that starts from that limited value. Each step uses the result of the step before it.",
                [
                    r"Form the ratio of the imaginary part to the real part, \(b/a\).",
                    r"Take the principal arctangent of that ratio. The result lies between \(-\pi/2\) and \(\pi/2\).",
                    r"When \(a\) is negative, add \(\pi\) if \(b\ge 0\) and subtract \(\pi\) if \(b<0\). That shift uses the principal value from the previous step.",
                    r"Attach the magnitude \(\sqrt{a^2+b^2}\) to that corrected angle and write \(r e^{j\theta}\).",
                ],
                r"The ratio has to exist before its arctangent is taken. The principal value sits in the wrong half-plane whenever \(a\) is negative, so the shift by \(\pi\) corrects that value and cannot come first. The polar expression needs the corrected angle, so it is last. A plain arctangent of \(b/a\) reports \(3+3j\) and \(-3-3j\) at the same angle.",
            )),
        ]
    if sid == "sinusoid-resp":
        return [
            ("sinusoid-resp-r1-q2", fresh(
                1, "sym",
                r"A first-order lag has \(H(j\omega) = 1/(1+j\omega\tau)\). Write \(|H(j\omega)|\) using the name \(w\) for \(\omega\) and the name \(tau\) for \(\tau\).",
                "1/sqrt(1+(w*tau)^2)",
                {"w": (0.2, 20), "tau": (0.05, 5)},
                r"The numerator has magnitude 1. The denominator \(1+j\omega\tau\) has magnitude \(\sqrt{1+(\omega\tau)^2}\). Dropping the 1 under the square root is the high-frequency approximation, not the exact magnitude. The phase \(-\arctan(\omega\tau)\) is a different function and is not this magnitude.",
                alternates=["1/sqrt(1+w^2*tau^2)", "(1+(w*tau)^2)^(-0.5)"],
            )),
            ("sinusoid-resp-r2-q3", fresh(
                2, "order",
                r"Order the substitution that turns a constant-coefficient linear differential equation into \(H(j\omega)\).",
                [
                    r"Replace the input by the complex exponential \(e^{j\omega t}\).",
                    r"Replace every derivative by one factor of \(j\omega\).",
                    "Cancel the common exponential and solve for the ratio of output amplitude to input amplitude.",
                    "Read the steady sinusoid from the magnitude and angle of that ratio.",
                ],
                r"The exponential is an eigenfunction, so it is substituted before derivatives become algebra. Each derivative brings one factor \(j\omega\), and a second derivative brings \(-\omega^2\). The ratio is \(H(j\omega)\). Magnitude and angle are applied to the real drive only after that ratio exists. The procedure never solves for a new frequency: a linear constant-coefficient equation does not create one.",
            )),
            ("sinusoid-resp-r3-q3", fresh(
                3, "find_error",
                r"\(H(j\omega_0) = 0.8\angle -25^\circ\), and the input is \(4\sin(\omega_0 t)\). A student finds the steady output. Exactly one step is wrong.",
                [
                    r"Write \(\sin(\omega_0 t) = \cos(\omega_0 t - 90^\circ)\).",
                    r"Multiply the amplitude by \(|H|\): \(4 \times 0.8 = 3.2\).",
                    r"Add \(\angle H = -25^\circ\) to the cosine's \(-90^\circ\).",
                    r"The steady output is \(3.2\cos(\omega_0 t - 65^\circ)\).",
                ],
                3,
                r"A lag is added to the angle the input already has. The sine is a cosine delayed by \(90^\circ\), and the system delays by another \(25^\circ\), so the cosine's angle is \(-115^\circ\). The value \(-65^\circ\) is \(-90^\circ+25^\circ\), which would be a lead. The amplitude 3.2 is the right product. The same output is \(3.2\sin(\omega_0 t-25^\circ)\).",
                reasons=[
                    r"Adding \(-25^\circ\) to \(-90^\circ\) gives \(-115^\circ\), so the cosine is \(\cos(\omega_0 t-115^\circ)\).",
                    "The amplitude should stay 4, because a sine already has unit peak in its own formula.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "impulse-conv":
        return [
            ("impulse-conv-r1-q1", fresh(
                1, "order",
                "Order the argument that builds an LTI output from the impulse response.",
                [
                    "Split the input into thin pulses, each short enough to act as an impulse.",
                    "Scale each pulse by the input value at its time, times the pulse width.",
                    r"The response to a pulse at time \(\tau\) is that scale times \(h(t-\tau)\).",
                    r"Add every shifted copy. The sum is the convolution of the input with \(h\).",
                ],
                "The impulse response is useful only after the input has been broken into impulses. Scaling comes before the shift is copied, because a taller pulse makes a taller copy of \\(h\\). Superposition adds the copies. Integrating \\(h\\) alone, with no input samples, is the step response rather than the response to this input.",
            )),
            ("impulse-conv-r2-q3", fresh(
                2, "multi",
                "Select every impulse response that is causal.",
                [
                    r"\(h(t) = 5e^{-3t}u(t)\)",
                    r"\(h(t) = e^{-|t|}\)",
                    r"\(h(t) = 0\) for \(t<0\), and \(h(t) = 2\) on \(0 \le t \le 4\)",
                    r"\(h(t) = \delta(t+2)\)",
                ],
                [0, 2],
                r"Causal means the impulse at time 0 produces nothing earlier, so \(h(t) = 0\) for \(t<0\). The one-sided exponential and the pulse that starts at 0 both qualify. \(e^{-|t|}\) is already nonzero for negative time. An impulse at \(t=-2\) fires before the kick that was applied at 0.",
            )),
            ("impulse-conv-r1-q2", fresh(
                1, "sym",
                r"The impulse response is \(h_0\) at index 0 and \(h_1\) at index 1, and 0 elsewhere. The input is \(x_0\) at index 0 and \(x_1\) at index 1, and 0 elsewhere. Write the output sample at index 1, using the names \(x0\), \(x1\), \(h0\), and \(h1\).",
                "x0*h1+x1*h0",
                {"x0": (-3, 3), "x1": (-3, 3), "h0": (-3, 3), "h1": (-3, 3)},
                "At index 1 the new input sample meets \\(h_0\\), and the previous input sample meets the shifted \\(h_1\\). Those are the only overlaps. The product of the two index-0 samples is the output at index 0. The product of the two index-1 samples is the output at index 2. Adding all four products counts samples that are not lined up yet.",
                alternates=["h1*x0+h0*x1", "x1*h0+x0*h1"],
            )),
        ]
    if sid == "step-resp":
        return [
            ("step-resp-r2-q3", fresh(
                2, "sym",
                r"A causal impulse response is \(h(t) = a e^{-b t}\) for \(t \ge 0\), with \(a\) and \(b\) positive. Write the unit-step response for \(t \ge 0\), using the names \(a\), \(b\), and \(t\).",
                "(a/b)*(1-exp(-b*t))",
                {"a": (0.4, 6), "b": (0.3, 4), "t": (0.05, 3)},
                r"The unit-step response is the running integral of \(h\). Integrating \(a e^{-b\tau}\) from 0 to \(t\) produces \((a/b)(1-e^{-bt})\). The factor \(a/b\) is the final value, the whole area under \(h\). Leaving out \(1/b\) treats the exponent as if its coefficient were 1. The expression \(a e^{-bt}\) is still the impulse response, not the step.",
                alternates=["a*(1-exp(-b*t))/b", "a/b-a*exp(-b*t)/b"],
            )),
            ("step-resp-r1-q1", fresh(
                1, "order",
                "Order the link from an impulse response to a step-response specification.",
                [
                    "A unit step is the running integral of a unit impulse.",
                    "By linearity, the step response is the running integral of the impulse response.",
                    "For a causal impulse response, start that integral at time 0.",
                    "Read rise and settling from that integral, not from the height of the impulse response.",
                ],
                "The input identity comes first, and linearity carries it over to the output. The lower limit is 0 only after causality is used; a two-sided impulse response needs the integral from the distant past. Rise and settling describe the step waveform. Reading them off the peak of the impulse response confuses the kick with the accumulated response.",
            )),
            ("step-resp-r1-q3", fresh(
                1, "find_error",
                r"A student reads the first-order step \(y(t) = y_\infty(1-e^{-t/\tau})\) at \(t=\tau\). Exactly one step is wrong.",
                [
                    r"Substitute \(t = \tau\), so the exponent is \(-1\).",
                    r"\(e^{-1}\) is about 0.37.",
                    "The fraction of the gap that is still open is that 0.37.",
                    r"Therefore the output has reached half of \(y_\infty\).",
                ],
                3,
                r"The exponential has fallen to about 37% of the gap, so the output has closed about 63% of it. Half of the step is the time when \(1-e^{-t/\tau} = 1/2\), which is \(t = \tau\ln 2\), about \(0.69\tau\), earlier than one time constant. The value 0.37 itself is right.",
                reasons=[
                    "One minus about 0.37 is about 0.63 of the final value, not one half.",
                    "The time constant is defined as the 50% point, so half is the right reading.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "freq-char":
        return [
            ("freq-char-r1-q1", fresh(
                1, "order",
                r"Order the passage from a convolution \(y = h * x\) to the frequency-domain product.",
                [
                    "Take the Fourier transform of both sides.",
                    "Apply the convolution theorem to the transform of the convolution.",
                    r"Write \(Y(j\omega) = H(j\omega)\,X(j\omega)\).",
                    "For a single sinusoid, read the output amplitude and phase from that product at one frequency.",
                ],
                "The transform is applied before the theorem has a product to offer. The theorem replaces convolution by multiplication, not by another convolution and not by addition. A sinusoid's steady response is the last reading, because it uses the product at one frequency. Dividing the input transform by \\(H\\) would invert the system.",
            )),
            ("freq-char-r1-q2", fresh(
                1, "sym",
                r"A gain \(g\) is a positive amplitude ratio. Write that gain in decibels with the natural log, using only the name \(g\).",
                "20*ln(g)/ln(10)",
                {"g": (0.05, 30)},
                r"Decibels for an amplitude are \(20\log_{10}(g)\). Change of base writes \(\log_{10}(g) = \ln(g)/\ln(10)\). A factor of 10 instead of 20 is the rule for a power ratio, and it is half of this expression. Using \(\ln(g)\) alone leaves the result in nepers.",
                alternates=["20*log(g)/log(10)", "(20/ln(10))*ln(g)"],
            )),
            ("freq-char-r3-q3", fresh(
                3, "multi",
                r"For a stable LTI system, select every statement that is true of \(H(s)\) and \(H(j\omega)\).",
                [
                    r"\(H(j\omega)\) is \(H(s)\) with \(s\) set to \(j\omega\).",
                    r"\(H(j\omega)\) fixes the steady amplitude and phase of a sinusoid at frequency \(\omega\).",
                    "Stability puts the imaginary axis inside the region where the transform converges, so that substitution is legal.",
                    r"\(H(j\omega)\) and \(H(s)\) are unrelated, one for impulses and one for steps.",
                ],
                [0, 1, 2],
                r"The frequency response is the transfer function on the imaginary axis, and that complex value scales and shifts a persistent sinusoid. Stability puts every pole in the open left half-plane, so the axis is inside the region of convergence. The two symbols are one function on two sets of \(s\). Transients are the part contributed by those poles, not a second meaning of \(H(j\omega)\).",
            )),
        ]
    if sid == "lti-circuits":
        return [
            ("lti-circuits-r1-q1", fresh(
                1, "sym",
                r"A series resistor \(R\) feeds an uncharged capacitor \(C\). At \(t=0\) the source steps to a constant \(V_s\). Write \(v_o(t)\) for \(t\ge 0\), using the names \(V_s\), \(t\), \(R\), and \(C\). Use a name \(Vs\) for \(V_s\).",
                "Vs*(1-exp(-t/(R*C)))",
                {"Vs": (0.5, 9), "t": (0.01, 2), "R": (1, 20), "C": (0.05, 2)},
                r"The capacitor starts at 0 and the open-circuit final value is the source, because a settled capacitor draws no current through \(R\). The time constant is \(RC\). A falling exponential from \(V_s\) is the discharge that happens when the source is replaced by a short, not this step.",
                alternates=["Vs-Vs*exp(-t/(R*C))", "Vs*(1-e**(-t/(R*C)))"],
            )),
            ("lti-circuits-r2-q2", fresh(
                2, "order",
                r"An RC low-pass filter is at rest. A constant input of height \(V_s\) turns on at time \(t_0\), not at time 0. Order the reasoning for the output after \(t_0\).",
                [
                    r"Before \(t_0\) the input is still 0, so the output stays 0.",
                    r"After \(t_0\) the final value is \(V_s\).",
                    r"Measure the exponent from the switching instant, so the elapsed time is \(t-t_0\).",
                    r"For \(t>t_0\), write \(v_o(t) = V_s\left(1-e^{-(t-t_0)/\tau}\right)\).",
                ],
                r"A time-invariant circuit does not care that the clock read 0 at some earlier moment. The transient starts when the input changes. Using \(t\) rather than \(t-t_0\) in the exponent pretends the step happened at 0, so the output would already have risen by \(t_0\). The final value is still the input, because the capacitor current dies out.",
            )),
            ("lti-circuits-r3-q2", fresh(
                3, "find_error",
                r"A capacitor sits at 1.5 V. At \(t=0\) the input steps to 6 V and stays there. The time constant is \(\tau\). A student writes the output. Exactly one step is wrong.",
                [
                    "The final value is the new input, 6 V.",
                    "The initial value is the stored capacitor voltage, 1.5 V.",
                    "The gap that must close is \\(6 - 1.5 = 4.5\\) V.",
                    r"Therefore \(v_o(t) = 6e^{-t/\tau}\).",
                ],
                3,
                r"The waveform is the final value plus the initial gap times a decaying exponential: \(6 + (1.5-6)e^{-t/\tau} = 6 - 4.5e^{-t/\tau}\). It starts at 1.5 V, because the capacitor voltage is continuous, and it settles at 6 V. The expression \(6e^{-t/\tau}\) starts at 6 V and settles at 0, which is a discharge into a shorted source. The 4.5 V gap is the right subtraction.",
                reasons=[
                    r"The exponential multiplies the gap, so \(v_o(t) = 6 - 4.5e^{-t/\tau}\), which starts at 1.5 V.",
                    "The capacitor voltage jumps to 6 V at the instant the input steps.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "freq-resp-circuits":
        return [
            ("freq-resp-circuits-r3-q1", fresh(
                3, "find_error",
                r"A circuit of real \(R\), \(L\), and \(C\) has \(H(j\omega) = 1/(1+j\omega\tau)\). A student evaluates \(H(-j\omega)\). Exactly one step is wrong.",
                [
                    r"Substitute \(-\omega\) for \(\omega\) in \(1/(1+j\omega\tau)\).",
                    r"The denominator becomes \(1 - j\omega\tau\).",
                    r"Real element values make \(H(-j\omega)\) the complex conjugate of \(H(j\omega)\).",
                    r"Therefore \(H(-j\omega) = H(j\omega)\), because the circuit cannot tell the sign of frequency.",
                ],
                3,
                r"Conjugation flips the sign of the imaginary part. \(1+j\omega\tau\) becomes \(1-j\omega\tau\), which is what the substitution already produced, so those two steps agree. They do not agree with claiming the value is unchanged. The magnitude is even in \(\omega\) and the phase is odd: the gain at \(-\omega\) has the opposite phase. It is not the negation of the whole complex number, and it is not the same complex number.",
                reasons=[
                    r"The conjugate of \(1/(1+j\omega\tau)\) is \(1/(1-j\omega\tau)\), which equals \(H(-j\omega)\) and not \(H(j\omega)\).",
                    r"Negative frequency reverses every impedance, so \(H(-j\omega) = -H(j\omega)\).",
                ],
                correct_reason=0,
            )),
            ("freq-resp-circuits-r1-q3", fresh(
                1, "multi",
                r"Select every statement that is true of a circuit's voltage gain \(G_v(j\omega)\).",
                [
                    "It is the ratio of the output voltage phasor to the input voltage phasor.",
                    "It is dimensionless.",
                    "Its magnitude is the steady amplitude ratio, and its angle is the phase shift of the sinusoid.",
                    "It equals the output voltage in volts when the input current is 1 A.",
                ],
                [0, 1, 2],
                "Voltage gain compares two voltages, so the unit cancels and the result is a complex number. Magnitude and angle are the sinusoidal steady-state scale and shift. An output voltage per ampere of input current is a transimpedance, in ohms, which is a different ratio.",
            )),
            ("freq-resp-circuits-r2-q1", fresh(
                2, "sym",
                r"A capacitor \(C\) is driven at angular frequency \(w\) in radians per second. Write the magnitude of its impedance, using the names \(w\) and \(C\).",
                "1/(w*C)",
                {"w": (1, 40), "C": (0.1, 4)},
                r"The impedance is \(1/(j\omega C)\). The factor \(j\) has magnitude 1, so the magnitude is \(1/(\omega C)\). Multiplying by \(\omega C\) is the admittance magnitude, the reciprocal. A resistor's impedance does not fall as frequency rises.",
                alternates=["1/(C*w)"],
                fig=CAP_SVG,
                alt=CAP_ALT,
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
