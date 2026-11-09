#!/usr/bin/env python3
"""Generate ME 132 batch B5 banks and explainers.

Closed-form answers live here. skilltree/verify_me132_b5.py recomputes them
by complex arithmetic, Fourier integrals, finite differences, eigenvalues,
or polynomial routines. Do not import this file from the verifier.
"""
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from templates import (
    block_diagram, bode, mass_spring, matrix_fig, nyquist, parallel_sum,
    plot, splane, step_response,
)
from banklib import BANK, EXP, Bank, g, save_explainer, words


def show(x):
    return f"{g(x):.6g}"


def loop(blocks, title, fb="1"):
    return block_diagram(blocks, title, feedback=fb, input_label="r", output_label="y", error_label="e")


def series(blocks, title):
    return block_diagram(blocks, title, input_label="in", output_label="out")


def rise(title, tau=1.1):
    return step_response(title, tau=tau, goal=1.0)


# ---------------------------------------------------------------------------
# feedforward
# ---------------------------------------------------------------------------

def bank_feedforward():
    b = Bank("feedforward")
    two = "Two paths add before the plant."
    fb = "A feedback loop with a plant block."
    fig_add = parallel_sum(["C", "F"], "feedback plus feedforward", output_label="u")
    fig_loop = loop(["P"], "unity feedback plant")
    fig_pre = series(["F", "P"], "reference feedforward")
    fig_step = rise("tracking with feedforward", 0.8)

    d_in = 1.6
    k_dc = 2.5
    d_out, p_out = 2.0, 5.0
    p_true, p_hat = 10.0, 8.0
    t_dc = 0.75
    l_dc = 6.0
    d_hat, d_true = 2.3, 2.0

    b.mc(1,
         r"Reference feedforward is a second path from \(r\) into the command \(u\). It is used so that",
         ["the feedback loop can be left unchanged while the reference response is shaped",
          r"the loop gain \(L\) must be redesigned whenever the reference changes",
          "sensor noise is removed before it reaches the controller",
          "the plant poles are moved by the feedforward block alone"], 0,
         r"A prefilter or a feedforward path shapes how \(r\) enters, and it does not change the loop gain built from the feedback of \(y\). Redesigning \(L\) is what the feedback block does. Feedforward of \(r\) does not see sensor noise, and it does not move the closed-loop poles.",
         fig_add, two)
    b.num(1,
          r"A measured disturbance adds at the plant input. Its value is 1.6. The feedforward command that cancels it is",
          -d_in, "1",
          r"The net input is \(u + d\). Cancellation needs \(u = -d = " + show(-d_in) + r"\). The choice \(+d\) pushes in the same direction as the disturbance. Dividing by the plant gain is the cancellation for a disturbance that adds at the output.",
          fig_add, two)
    b.num(1,
          r"A plant has DC gain 2.5. The static feedforward gain that inverts that plant at DC is",
          1 / k_dc, "1",
          r"Ideal static inversion uses \(F = 1/P = 1/2.5 = " + show(1 / k_dc) + r"\). Using \(P\) itself, 2.5, amplifies the reference instead of inverting the plant. Using \(1 + P\) is the feedback sensitivity factor, not the inverse.",
          fig_pre, "A feedforward block in series with the plant.")

    b.num(2,
          r"A disturbance of size 2 adds at the plant output. The plant DC gain is 5. The input command that cancels that disturbance in steady state is",
          -d_out / p_out, "1",
          r"An output disturbance \(d\) is cancelled by a plant input \(-d/P\). Here that is \(-2/5 = " + show(-d_out / p_out) + r"\). The command \(-d = -2\) would be right only if the disturbance added at the input. The command \(-P d = -10\) has the plant gain in the numerator.",
          fig_loop, fb)
    b.mc(2,
         r"Adding a reference prefilter in front of an otherwise unchanged feedback loop",
         ["moves every closed-loop pole",
          "leaves the loop gain, and therefore the stability margins, unchanged",
          "removes steady-state error even when the loop has no integrator",
          "makes the sensitivity function identically zero"], 1,
         r"The prefilter multiplies the reference and does not sit inside the loop, so \(L\) and the margins stay put. Poles of the loop are roots of \(1 + L = 0\) and do not move. A prefilter cannot create the infinite DC loop gain that an integrator provides, and \(S = 1/(1+L)\) is unchanged.",
         fig_pre, "A block in front of a plant.")
    b.num(2,
          r"The true plant DC gain is 10 and the model used for inversion has DC gain 8. With no feedback, the reference-to-output gain is",
          p_true / p_hat, "1",
          r"Open-loop inversion sets \(F = 1/8\), so \(y/r = P F = 10/8 = " + show(p_true / p_hat) + r"\). Perfect inversion would give 1, which is what the model promised, not what the true plant does. The ratio \(8/10 = 0.8\) inverts the two gains.",
          fig_pre, "A feedforward block in series with the plant.")

    b.mc(3,
         r"The same mismatched inverse is used, so a unit reference produces output 1.25 with no feedback. The steady error is 0.25 because",
         ["feedforward always leaves a 25 percent error",
          "the feedback loop is unstable",
          "the true plant is larger than the model, so the output overshoots the reference",
          r"sensor noise was amplified by \(S\)"], 2,
         r"\(P F = 1.25\), so the output sits 0.25 above a unit reference. That fraction is this particular mismatch, not a fixed property of feedforward. No feedback loop is present in this calculation, and sensor noise enters through \(S\), which was not in the path.",
         fig_step, "A step that settles above the final command.")
    b.num(3,
          r"A unity-feedback loop has complementary sensitivity \(T(0) = 0.75\). A reference prefilter \(F\) is placed in front of the loop. The DC value of \(F\) that makes the overall DC gain equal to 1 is",
          1 / t_dc, "1",
          r"The prefilter sees the closed-loop map, so the overall gain is \(F\, T(0)\). Setting that to 1 gives \(F = 1/0.75 = " + show(1 / t_dc) + r"\). Using \(T\) itself, 0.75, would make the overall gain \(0.5625\). Using \(1 - T = 0.25\) is the sensitivity, not the required prefilter.",
          series(["F", "T"], "prefilter on a closed loop"), "A prefilter in series with a closed-loop block.")
    b.num(3,
          r"A unity-feedback loop has DC loop gain \(L(0) = 6\), with \(L\) real and positive. The prefilter that restores overall DC gain 1, placed in front of this loop, has gain",
          (1 + l_dc) / l_dc, "1",
          r"\(T(0) = L/(1+L) = 6/7\). The prefilter is \(1/T = 7/6 = " + show((1 + l_dc) / l_dc) + r"\). Using \(1 + L = 7\) ignores that most of the reference already gets through. Using \(L = 6\) is the loop gain, not the prefilter.",
          fig_loop, fb)

    b.num(4,
          r"A measured input disturbance is really 2, but the measurement used for cancellation reads 2.3. The feedforward command is \(-2.3\). The residual disturbance at the plant input is",
          d_true - d_hat, "1",
          r"The plant input sees \(d + u = 2 - 2.3 = " + show(d_true - d_hat) + r"\). A perfect measurement would leave 0, which cannot be the graded value. The residual \(2.3 - 2 = +0.3\) has the sign of the measurement error rather than the sign of \(d + u\).",
          fig_add, two, ["gen-controller"])
    b.mc(4,
         r"A plant has a right-half-plane zero. A feedforward block that inverts the whole plant model",
         ["is always a stable, proper filter",
          "can cancel that zero with a stable pole",
          "moves the closed-loop poles into the left half-plane by itself",
          "asks for an unstable or non-causal inverse, so only the stable part of the model is inverted"], 3,
         r"Inverting a right-half-plane zero produces a right-half-plane pole, which is an unstable filter. Cancelling that zero with a stable pole is not inversion. Feedforward does not place the loop poles, and a full inverse of a non-minimum-phase plant is not a stable proper filter.",
         splane([(1.5, 0)], [], "a right-half-plane zero of the plant"),
         "A mark on the positive real axis.", ["gen-controller"])
    b.num(4,
          r"Disturbance feedforward is perfect at DC and the feedback sensitivity at DC is \(S(0) = 0.12\). A unit output disturbance that is not measured still appears at the output with size",
          0.12, "1",
          r"Feedforward never sees an unmeasured disturbance, so the feedback path still passes it through \(S\). The output piece is \(0.12\). The complementary value \(1 - 0.12 = 0.88\) is \(T\), the reference map, not the disturbance map. Zero would require the disturbance to be measured and cancelled.",
          fig_loop, fb, ["gen-controller"])
    b.save()


def expl_feedforward():
    fig = parallel_sum(["C", "F"], "two-degree-of-freedom command", output_label="u")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A feedback path and a feedforward path add to form the plant command.",
         "body_md": r"""Feedback acts only after an error exists. Feedforward acts on a signal that is already known: the reference, or a measured disturbance. The two paths add at the plant command. Because the feedforward path is outside the loop, it does not change the loop gain, the sensitivity function, or the stability margins. It changes the particular response to the signal it measures.

That split is what a two-degree-of-freedom controller is for. One degree of freedom sets how hard the loop fights uncertainty and unmeasured disturbances. The other sets how the known reference or the known load shows up in the output. A good feedback design can then stay put while the feedforward path is adjusted."""},
        {"heading": "Key equations", "body_md": r"""If a disturbance \(d\) adds at the plant input, the cancelling command is \(u = -d\). If \(d\) adds at the output of a plant with DC gain \(P\), the steady command that cancels it is \(u = -d/P\).

A reference prefilter \(F\) in front of a unity-feedback loop produces the overall map \(F\, T\), with \(T = L/(1+L)\). The DC choice \(F = 1/T(0)\) makes a constant reference come through with gain 1. Open-loop inversion of a model \(P_0\) uses \(F = 1/P_0\). On the true plant the gain is \(P/P_0\), which equals 1 only when the model matches."""},
        {"heading": "Worked example", "body_md": r"""A heater has DC gain 3.5 from valve command to temperature. A measured inlet disturbance of 0.8 adds at the valve, so the cancelling feedforward command is \(-0.8\). Separately, the static inverse that would turn a reference step into the same steady temperature with no feedback is \(1/3.5 \approx 0.286\). If the real gain is a little higher than 3.5, that inverse overshoots, and the feedback loop, if it is present, only has to trim the residual."""},
        {"heading": "Common pitfalls", "body_md": r"""The sign has to oppose the disturbance. A flipped sign doubles the load instead of removing it. Input and output disturbances use different formulas: dividing by \(P\) is correct only when the disturbance is downstream of the plant. A prefilter cannot supply the infinite DC gain of an integrator, so it does not by itself remove the steady error of a type-0 loop. Inverting a right-half-plane zero builds an unstable filter. Invert the stable, well-known part of the model and leave the rest to feedback."""},
        {"heading": "Where this leads", "body_md": r"""The same two paths reappear when state feedback is combined with a reference model and an observer. The feedback piece stabilizes and rejects what was not measured. The feedforward piece carries the planned trajectory. Saturation still has to be respected, because a perfect inverse can ask for a command the actuator cannot produce."""},
    ]
    save_explainer("feedforward", "Feedforward and two-degree-of-freedom control", sections)
    return words(sections)


# ---------------------------------------------------------------------------
# freq-resp-lti
# ---------------------------------------------------------------------------

def bank_freq_resp():
    b = Bank("freq-resp-lti")
    bode_fig = bode([(0.3, 12), (1, 10), (3, 4), (10, -8)], "magnitude versus frequency")
    bode_alt = "A magnitude curve that falls as frequency rises."
    pole_fig = splane([(-3, 0)], [], "a real pole")
    pole_alt = "One pole mark on the negative real axis."
    step_fig = rise("sinusoid settling sketch", 0.6)
    step_alt = "A transient that dies toward a steady oscillation envelope."

    g1 = 12 / abs(complex(3, 4))
    ph1 = math.degrees(math.atan2(-4, 3))
    g2 = 5 / abs(complex(2, 2))
    amp2 = 3 * g2
    g3 = 20 / abs(complex(1, 6))
    ph3 = math.degrees(math.atan2(2, 1) - math.atan2(2, 4))
    gss = abs(4 / complex(3, 2) * 2 + 1)

    b.mc(1,
         r"A stable linear system is driven by a sinusoid that has been on for a long time. The steady output is",
         [r"a sinusoid at the same frequency, scaled and shifted by \(G(j\omega)\)",
          "a sinusoid at twice the input frequency",
          "a constant equal to the DC gain, for any input frequency",
          "a growing oscillation, because every sinusoid is an unstable mode"], 0,
         r"For an asymptotically stable linear system the transients die, and the particular solution is a sinusoid at the driving frequency. Its scale is \(|G(j\omega)|\) and its phase shift is the angle of \(G(j\omega)\). Doubling the frequency would be a nonlinear effect. The DC gain applies only at \(\omega = 0\). A persistent sinusoid is an input, not a natural mode.",
         bode_fig, bode_alt)
    b.num(1,
          r"\(G(s) = 12/(s+3)\). At \(\omega = 4\) rad/s the magnitude \(|G(j\omega)|\) is",
          g1, "1",
          r"\(G(j4) = 12/(3+j4)\), so \(|G| = 12/\sqrt{3^2+4^2} = 12/5 = " + show(g1) + r"\). The DC gain \(12/3 = 4\) drops the \(j4\) term. The reciprocal \(5/12\) inverts the magnitude.",
          pole_fig, pole_alt)
    b.num(1,
          r"For the same \(G(s) = 12/(s+3)\) at \(\omega = 4\) rad/s, the phase of \(G(j\omega)\), in degrees, is",
          ph1, "deg",
          r"The denominator \(3+j4\) has angle \(\tan^{-1}(4/3)\), and the numerator is positive, so the phase is \(-53.13^\circ\), stored as " + show(ph1) + r". Reporting the positive angle drops the sign of a lag. Using the magnitude 2.4 as if it were a phase mixes the two parts of the complex value.",
          bode([(1, 0), (4, ph1), (10, -80)], "phase of a real pole", phase=[(1, -20), (4, ph1), (10, -75)]),
          "A phase curve that becomes more negative as frequency rises.")

    b.num(2,
          r"Now \(G(s) = 5/(s+2)\) and the input is \(3\sin(2t)\). The steady-state output amplitude is",
          amp2, "1",
          r"\(|G(j2)| = 5/|2+j2| = 5/\sqrt{8}\). Times the input amplitude 3, the output amplitude is " + show(amp2) + r". Reporting \(|G|\) alone forgets the input amplitude. Using the DC gain \(5/2 = 2.5\) times 3 gives 7.5 and ignores the \(j2\) term.",
          bode_fig, bode_alt)
    b.mc(2,
         r"The frequency-response formula \(y(t) = |G(j\omega)|\,A\sin(\omega t + \angle G)\) requires the system to be",
         ["unstable, so that a natural mode can grow",
          "asymptotically stable, so that every natural mode has died away",
          r"marginally stable, with a pole on the imaginary axis at \(j\omega\)",
          r"nonlinear, so that the amplitude can depend on \(A\)"], 1,
         r"The formula is the forced response after the homogeneous solution has vanished. That happens when every eigenvalue has a negative real part. An unstable mode grows and swamps the sinusoid. A pole at \(j\omega\) resonates with the input and the amplitude is not given by a finite \(G(j\omega)\). Amplitude dependence on \(A\) is a nonlinear effect.",
         step_fig, step_alt)
    b.num(2,
          r"\(G(s) = 8/(s+2)\). The magnitude \(|G(j\omega)|\) at \(\omega = 0\) is",
          4.0, "1",
          r"At \(\omega = 0\), \(G(0) = 8/2 = " + show(4.0) + r"\). That is the DC gain. The high-frequency magnitude tends to 0, which is not the value at \(\omega = 0\). Twice the DC gain, 8, forgets the pole.",
          pole_fig, pole_alt)

    b.mc(3,
         r"For a state-space model the same frequency response is",
         [r"\(A + B + C + D\)",
          r"the eigenvalues of \(A\), plotted against \(\omega\)",
          r"\(C(j\omega I - A)^{-1}B + D\)",
          r"\(e^{At}\) evaluated at \(t = \omega\)"], 2,
         r"Substituting \(s = j\omega\) into \(C(sI-A)^{-1}B+D\) gives the frequency response. Adding the four matrices is not that formula. The eigenvalues are the natural modes, not the response at one frequency. The matrix exponential is the free-response operator in time, not \(G(j\omega)\).",
         bode_fig, bode_alt, version=2)
    b.num(3,
          r"\(G(s) = 20/(s^2 + 2s + 10)\). At \(\omega = 3\) rad/s the magnitude is",
          g3, "1",
          r"The denominator at \(s = j3\) is \(10 - 9 + j6 = 1 + j6\), with magnitude \(\sqrt{37}\). Then \(|G| = 20/\sqrt{37} = " + show(g3) + r"\). The DC gain \(20/10 = 2\) evaluates \(s = 0\). Using \(\omega_n = \sqrt{10}\) as the magnitude confuses the natural frequency with \(|G|\).",
          bode_fig, bode_alt)
    b.num(3,
          r"\(G(s) = (s+1)/(s+4)\). At \(\omega = 2\) rad/s the phase, in degrees, is",
          ph3, "deg",
          r"The angle is \(\angle(1+j2) - \angle(4+j2)\). That difference is " + show(ph3) + r" degrees. Each term is a lead, and the zero is closer to the origin, so the phase is positive. Adding the two angles instead of subtracting them is the angle of the product, not the quotient. The magnitude \(|G|\) is not a phase.",
          bode([(0.5, 10), (2, 5), (8, -5)], "lead magnitude", phase=[(0.5, 20), (2, ph3), (8, 10)]),
          "A phase curve of a lead network.")

    b.num(4,
          r"A first-order lag has time constant \(0.25\) s. Its bandwidth, the frequency where the magnitude is \(1/\sqrt{2}\) of the DC gain, is",
          4.0, "rad/s",
          r"For \(1/(\tau s+1)\) the bandwidth is \(1/\tau = 1/0.25 = " + show(4.0) + r"\) rad/s. The time constant itself, 0.25, is not a frequency. Twice that corner, 8, is a different definition and not the \(-3\) dB point of a first-order lag.",
          bode([(0.2, 0), (1, -1), (4, -3), (20, -14)], "first-order magnitude"),
          "A flat magnitude that then falls.", ["time-delay"])
    b.mc(4,
         r"A pair of complex poles with a small damping ratio shows up in \(|G(j\omega)|\) as",
         ["a notch that goes to zero at the natural frequency",
          "a magnitude that is exactly the DC gain at every frequency",
          r"a slope of \(-20\) dB/decade that never changes",
          "a peak near the natural frequency"], 3,
         r"Light damping produces a resonance peak near \(\omega_n\). A notch is a zero on the imaginary axis, not a lightly damped pole pair. The magnitude is not flat unless the damping is heavy and the zeros compensate the poles. A single real pole gives a slope near \(-20\) dB/decade; a complex pair eventually falls at \(-40\).",
         bode([(0.5, 6), (2, 8), (3, 14), (5, 4), (12, -8)], "resonance peak"),
         "A magnitude curve with a hump before it falls.", ["sys-id"])
    b.num(4,
          r"A scalar state-space model has \(A = -3\), \(B = 2\), \(C = 4\), \(D = 1\). At \(\omega = 2\) rad/s the magnitude of \(C(j\omega - A)^{-1}B + D\) is",
          gss, "1",
          r"\(j\omega - A = 3 + j2\). Then \(C B /(j\omega-A) + D = 8/(3+j2) + 1\), whose magnitude is " + show(gss) + r". Dropping \(D\) leaves only the strict-feedthrough piece. Evaluating at \(\omega = 0\) gives \(8/3 + 1\), the DC gain, not the value at 2 rad/s.",
          matrix_fig([["A=-3", "B=2"], ["C=4", "D=1"]], "scalar state-space data"),
          "Four scalar state-space entries.", ["adaptive"])
    b.save()


def expl_freq_resp():
    fig = bode([(0.4, 8), (1.5, 6), (4, 0), (12, -10)], "steady-state magnitude",
               phase=[(0.4, -15), (1.5, -40), (4, -70), (12, -95)])
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "Magnitude and phase curves versus frequency.",
         "body_md": r"""A stable linear system answers a lasting sinusoid with a sinusoid of the same frequency. The amplitude is multiplied by \(|G(j\omega)|\) and the wave is shifted by the angle of \(G(j\omega)\). Nothing in that steady picture depends on the initial state, because every natural mode has already decayed.

The same complex number is what a Bode plot draws, what a Nyquist plot traces, and what a state-space model computes from \(C(j\omega I - A)^{-1}B + D\). Transfer-function algebra and the resolvent are two ways to the same \(G(j\omega)\). The formula is a property of the forced response. It is not a description of an unstable transient."""},
        {"heading": "Key equations", "body_md": r"""For \(G(s) = 1/(\tau s + 1)\), \(|G(j\omega)| = 1/\sqrt{1 + \omega^2\tau^2}\) and the phase is \(-\tan^{-1}(\omega\tau)\). The bandwidth, where the magnitude is \(1/\sqrt{2}\) of the DC value, sits at \(\omega = 1/\tau\).

For a state-space model,
\[
G(j\omega) = C(j\omega I - A)^{-1}B + D.
\]
The angle of a quotient is the angle of the numerator minus the angle of the denominator. A real negative pole contributes lag. A real negative zero contributes lead."""},
        {"heading": "Worked example", "body_md": r"""Take \(G(s) = 9/(s+3)\) and a unit cosine at \(\omega = 3\). Then \(G(j3) = 9/(3+j3)\). The magnitude is \(9/\sqrt{18} \approx 2.121\) and the phase is \(-45^\circ\). After the transient \(e^{-3t}\) has died, the output is \(2.121\cos(3t - 45^\circ)\). The DC gain would have said 3, which is the answer only at \(\omega = 0\)."""},
        {"heading": "Common pitfalls", "body_md": r"""The formula does not apply while an unstable mode is still growing, and it does not apply at a pole on the imaginary axis, where the response contains a resonant term that the finite value \(G(j\omega)\) cannot represent. Magnitude and phase are different numbers: a phase in degrees is not the modulus. Evaluating \(G(0)\) when the question names a nonzero \(\omega\) drops the imaginary part. For a state-space model the feedthrough \(D\) is part of \(G\), so leaving it out shifts both the magnitude and the phase."""},
        {"heading": "Where this leads", "body_md": r"""Time delay multiplies \(G(j\omega)\) by a phase \(-\omega T\) with no change in magnitude. Identification reads \(G(j\omega)\) off measured sinusoids. Loop shaping then asks this same \(G(j\omega)\) to be large at low frequency and small at high frequency, with a gentle phase near crossover."""},
    ]
    save_explainer("freq-resp-lti", "Frequency response of a linear system", sections)
    return words(sections)


# ---------------------------------------------------------------------------
# gen-gain-phase
# ---------------------------------------------------------------------------

def bank_gen_gain():
    b = Bank("gen-gain-phase")
    nyq = nyquist([(1.6, 0.1), (0.4, -0.8), (-0.35, -0.15), (-0.2, 0.05)], "Nyquist curve near the critical point")
    nyq_alt = "A curve in the complex plane with the point -1 marked."
    ncurve = plot(lambda t: 4 * 2 / (math.pi * (t + 0.5)), 0, 3.5, "a", "N", "relay gain versus amplitude")
    n_alt = "A curve that falls as amplitude grows."

    n_relay = 4 * 3 / (math.pi * 1.5)
    inv = -1 / n_relay
    a_for_2 = 4 * 2 / (math.pi * 2)
    delta = 0.5
    n_sat = (2 / math.pi) * (math.asin(delta) + delta * math.sqrt(1 - delta ** 2))
    n_big = 4 * 5 / (math.pi * 4)
    a_small = 4 * 1 / (math.pi * 2)
    harm = 1 / 3

    b.mc(1,
         r"A describing function replaces a nonlinearity, for a sinusoidal input of amplitude \(a\), by",
         [r"one complex gain for the fundamental harmonic, which may depend on \(a\)",
          "the exact response, including every higher harmonic",
          "a linear gain that does not depend on amplitude",
          "the DC gain of the nonlinearity"], 0,
         r"The describing function keeps the fundamental and discards the harmonics. It is a gain, often real, and for a saturation or a relay it falls as \(a\) grows. It is not exact, because the harmonics are real. A gain with no amplitude dependence is the linear case. The DC gain misses the fundamental of an odd nonlinearity, which has no DC term.",
         ncurve, n_alt)
    b.num(1,
          r"An ideal relay switches between \(-3\) and \(+3\). For a sinusoidal error of amplitude 1.5, its describing function \(N(a) = 4M/(\pi a)\) equals",
          n_relay, "1",
          r"\(N = 4\cdot 3/(\pi\cdot 1.5) = " + show(n_relay) + r"\). Using \(M/a = 2\) drops the Fourier factor \(4/\pi\). Using \(4M/\pi\) and forgetting to divide by \(a\) leaves the fundamental coefficient, not the gain.",
          ncurve, n_alt)
    b.num(1,
          r"That relay describing function is real and positive. The point \(-1/N\) on the real axis is",
          inv, "1",
          r"Limit-cycle balance is \(G(j\omega) = -1/N\). With \(N = " + show(n_relay) + r"\), the point is " + show(inv) + r". Plotting \(-N\) puts the critical point on the wrong side of \(-1\) and far too far left. Plotting \(-a\) uses the amplitude instead of the gain.",
          nyq, nyq_alt)

    b.num(2,
          r"An ideal relay of level \(M = 2\) has describing function \(4M/(\pi a)\). The amplitude \(a\) that makes \(N(a) = 2\) is",
          a_for_2, "1",
          r"\(8/(\pi a) = 2\) gives \(a = 4/\pi = " + show(a_for_2) + r"\). Solving \(4M/(\pi N)\) with the numbers swapped, \(a = 2\pi/4\), inverts the role of \(N\). The level \(M = 2\) is not the amplitude.",
          ncurve, n_alt)
    b.mc(2,
         r"A predicted limit cycle of a relay feedback loop is the intersection of",
         ["the Nyquist plot of the linear plant with the origin",
          r"the Nyquist plot of the linear plant with the locus \(-1/N(a)\)",
          "the step response with the saturation limits",
          "the root locus with the imaginary axis, for every amplitude"], 1,
         r"The harmonic-balance condition is \(G(j\omega) N(a) = -1\), so \(G(j\omega)\) meets \(-1/N(a)\). The origin is the high-frequency end of many Nyquist plots, not the balance point. Step-response limits are a time-domain picture. The root locus does not carry the amplitude parameter \(a\).",
         nyq, nyq_alt)
    b.num(2,
          r"A unit-slope saturation clips at \(\pm 1\). The input amplitude is 2, so the linear region covers only half of the sine wave. The describing function is",
          n_sat, "1",
          r"With \(\delta = M/(k a) = 1/2\), \(N = (2/\pi)(\sin^{-1}\delta + \delta\sqrt{1-\delta^2}) = " + show(n_sat) + r"\). The unsaturated gain would stay 1, which is the answer only for amplitudes below the clip. The relay formula \(4/(\pi a)\) is a different nonlinearity.",
          plot(lambda t: (2 / math.pi) * (math.asin(1 / (t + 1.2)) + (1 / (t + 1.2)) * math.sqrt(1 - 1 / (t + 1.2) ** 2)), 0, 2.8, "a", "N", "saturation gain"),
          "A gain that falls once the amplitude exceeds the clip.")

    b.mc(3,
         r"The describing-function approximation is most believable when",
         ["the plant gain is highest at the third harmonic",
          "the nonlinearity is the only block and there is no plant",
          "the plant is low-pass, so the harmonics are smaller at the nonlinearity's input than the fundamental",
          "the linear plant is unstable for every gain"], 2,
         r"The method assumes the input of the nonlinearity is nearly sinusoidal. A low-pass plant attenuates the harmonics before they come around the loop. A plant that amplifies the third harmonic breaks that assumption. With no plant there is no loop to balance. Instability of every linear gain is a different question.",
         bode([(0.4, 10), (1, 6), (3, -4), (9, -16)], "low-pass plant"),
         "A magnitude that is already small at the third harmonic.")
    b.num(3,
          r"An ideal relay of level 5 and a sine of amplitude 4 have describing function",
          n_big, "1",
          r"\(N = 4\cdot 5/(\pi\cdot 4) = 5/\pi = " + show(n_big) + r"\). The ratio \(M/a = 1.25\) omits \(4/\pi\). The product \(M a = 20\) is not a gain.",
          ncurve, n_alt)
    b.num(3,
          r"A relay of level \(M = 1\) is in feedback with a linear plant. The balance \(N(a) = 2\) occurs at amplitude",
          a_small, "1",
          r"\(4\cdot 1/(\pi a) = 2\) so \(a = 2/\pi = " + show(a_small) + r"\). Using \(a = N\) gives 2, which sets the amplitude equal to the gain. Using \(a = 4M/\pi\) forgets to divide by the required \(N\).",
          nyq, nyq_alt)

    b.num(4,
          r"A linear block has peak gain 1.8. The small-gain idea says the loop stays stable for every stable perturbation whose gain is below",
          1 / 1.8, "1",
          r"The product of the two gains has to stay below 1, so the perturbation gain must stay below \(1/1.8 = " + show(1 / 1.8) + r"\). The peak gain 1.8 itself is already larger than 1 and is not a sufficient bound on the perturbation. Half of 1.8 is a guess, not the reciprocal.",
          bode([(0.2, 2), (1, 5), (2, 5.1), (8, -6)], "a peaked gain"),
          "A magnitude with a modest peak.", ["robust-stability"])
    b.mc(4,
         r"An odd, memoryless nonlinearity such as an ideal relay or a saturation has a describing function that is",
         [r"always \(+90^\circ\), like a differentiator",
          "complex, with a lag that grows with amplitude",
          "zero for every amplitude",
          "real and nonnegative"], 3,
         r"Odd memoryless maps produce a fundamental that is in phase with the sine, so \(N(a)\) is real. A relay with hysteresis is the case that adds a phase lag, because it has memory. A differentiator's \(+90^\circ\) is a linear phase, not a describing function. \(N(a)\) is zero only in the trivial case of no output.",
         ncurve, n_alt, ["lyapunov"])
    b.num(4,
          r"The Fourier series of an ideal relay (a square wave) has a third harmonic whose amplitude is what fraction of the fundamental?",
          harm, "1",
          r"The square-wave coefficients fall as \(1/n\) for odd \(n\). The third harmonic is \(1/3\) of the fundamental, so the fraction is " + show(harm) + r". A fraction of \(1/9\) would be the square of that decay, which is not how the series works. A fraction of 1 would say the harmonic is as large as the fundamental, which is the case the describing function refuses.",
          ncurve, n_alt, ["adaptive"])
    b.save()


def expl_gen_gain():
    fig = nyquist([(1.4, 0.2), (0.2, -0.9), (-0.55, -0.2), (-0.25, 0.1)], "plant curve and the critical point")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A Nyquist curve with the point -1 marked.",
         "body_md": r"""Gain and phase are linear words. A relay, a saturation, or a dead zone does not have one gain. The describing function keeps the one number that matters for a nearly sinusoidal oscillation: the gain of the fundamental, as a function of amplitude. Higher harmonics are left out on purpose.

Plotted as \(-1/N(a)\), that gain becomes a locus a linear Nyquist curve can intersect. An intersection is a candidate limit cycle: a frequency from the plant curve and an amplitude from the nonlinearity. The small-gain idea is the linear cousin of the same picture. If the product of two gains stays below 1, the perturbation cannot push the loop through the critical point."""},
        {"heading": "Key equations", "body_md": r"""An ideal relay of levels \(\pm M\), driven by \(a\sin\omega t\), has
\[
N(a) = \frac{4M}{\pi a}.
\]
It is real, positive, and falls as \(a\) grows. A unit-slope saturation that clips at \(\pm M\) keeps \(N = 1\) for \(a \le M\). For larger \(a\), with \(\delta = M/a\),
\[
N(a) = \frac{2}{\pi}\left(\sin^{-1}\delta + \delta\sqrt{1-\delta^2}\right).
\]
Balance against a linear plant \(G\) is \(G(j\omega) = -1/N(a)\). The small-gain bound says that a peak gain of \(2.5\) tolerates an uncertain gain only up to \(0.4\)."""},
        {"heading": "Worked example", "body_md": r"""A relay with levels \(\pm 6\) sees a sine of amplitude 2. The describing function is \(4\cdot 6/(\pi\cdot 2) = 12/\pi \approx 3.82\). The matching critical point is \(-1/N \approx -0.262\), on the negative real axis. If the plant Nyquist curve crosses the real axis at \(-0.262\), this amplitude is the predicted oscillation. A plant that never gets closer to the origin than \(0.1\) on the negative real axis does not intersect \(-1/N\) for this relay, so the approximation predicts no cycle."""},
        {"heading": "Common pitfalls", "body_md": r"""\(N(a)\) is a gain, so the locus is \(-1/N\), not \(-N\). An odd memoryless map has a real describing function; hysteresis is what adds phase. The third harmonic of a relay is a third of the fundamental, which is small only if the plant kills it. If the plant amplifies that harmonic, the sine-in, fundamental-out story is wrong and the predicted amplitude can be badly off. Small-gain is sufficient, not necessary: a larger perturbation can still be stable if its phase does not point at the critical point."""},
        {"heading": "Where this leads", "body_md": r"""Robust stability turns the small-gain idea into a test on \(T\) and a multiplicative weight. Lyapunov arguments cover the same nonlinear loop without dropping harmonics. Adaptive schemes change the linear gain on purpose, which moves the Nyquist curve relative to \(-1/N(a)\) and can create or destroy the intersection."""},
    ]
    save_explainer("gen-gain-phase", "Describing functions and the small-gain idea", sections, version=2)
    return words(sections)


# ---------------------------------------------------------------------------
# linearization
# ---------------------------------------------------------------------------

def bank_linearization():
    b = Bank("linearization")
    ms = mass_spring("mass, spring, and damper")
    ms_alt = "A mass connected to a spring and a damper, with an applied force."
    poles = splane([(-1, 2), (-1, -2)], [], "local linear poles")
    pole_alt = "A complex pair of pole marks in the left half-plane."
    mat = matrix_fig([["df/dx", "df/du"]], "jacobian entries")
    mat_alt = "A row of two partial derivatives."

    a_cube = -3 * 2 ** 2
    a_tank = -2 * 0.5 / math.sqrt(9)
    wn = math.sqrt(10)
    a_mid = -3 * (1.5 ** 2)
    a_log = 1 - 2 * 3
    a_cubic_eq = 1 - 3 * (1 ** 2)

    b.mc(1,
         r"Linearization of \(\dot x = f(x, u)\) about an equilibrium \((x_e, u_e)\) replaces \(f\) by",
         [r"its Jacobian in \(x\) and in \(u\), and is accurate for small deviations",
          r"the value \(f(x_e, u_e)\), which is the whole story for large deviations too",
          "a linear model that is exact for every initial state",
          "the second derivative only, ignoring the slope"], 0,
         r"The first-order Taylor expansion is \(\delta\dot x = A\,\delta x + B\,\delta u\), with \(A\) and \(B\) the partial derivatives at the equilibrium. \(f(x_e, u_e)\) is zero by the definition of equilibrium, so it does not describe the motion. The linear model is local, not exact on the whole state space. The second derivative is the next term, the one the linear model drops.",
         mat, mat_alt)
    b.num(1,
          r"The scalar system is \(\dot x = -x^3 + u\). It rests at \(x = 2\), which needs \(u = 8\). The linearized \(A = \partial f/\partial x\) there is",
          a_cube, "1",
          r"\(\partial f/\partial x = -3x^2\). At \(x = 2\) that is \(-12\), so \(A = " + show(a_cube) + r"\). The value \(-3x = -6\) drops one factor of \(x\). The equilibrium input 8 is \(u_e\), not the Jacobian.",
          mat, mat_alt)
    b.num(1,
          r"For the same \(\dot x = -x^3 + u\), the input Jacobian \(B = \partial f/\partial u\) is",
          1.0, "1",
          r"The input enters as \(+u\), so \(B = " + show(1.0) + r"\) at every state. Using \(A = -12\) as if it were \(B\) mixes the two partial derivatives. Using \(u_e = 8\) reports the equilibrium input instead of the slope in \(u\).",
          mat, mat_alt)

    b.num(2,
          r"A tank obeys \(\dot h = -2\sqrt{h} + q\). It rests at \(h = 9\). The linearized coefficient of \(\delta h\) is",
          a_tank, "1",
          r"The derivative of \(-2 h^{1/2}\) is \(-h^{-1/2} = -1/3\) at \(h = 9\), so \(A = " + show(a_tank) + r"\). The outflow \(-2\sqrt{9} = -6\) is the equilibrium flow, not the slope. Half of that slope, \(-1/6\), comes from differentiating \(\sqrt{h}\) and forgetting the constant 2, or from differentiating and then dividing an extra time.",
          ms, ms_alt)
    b.mc(2,
         r"The equilibrium of a smooth nonlinear system is locally asymptotically stable when",
         ["the Jacobian has at least one eigenvalue with a negative real part",
          "every eigenvalue of the Jacobian has a negative real part",
          "the Jacobian is the zero matrix",
          "the nonlinear system has only one equilibrium in the whole state space"], 1,
         r"Local asymptotic stability follows when the linearization is asymptotically stable and no eigenvalue sits on the imaginary axis. One stable eigenvalue is not enough if another has a positive real part. The zero matrix is a critical case, not a stable one. A single equilibrium can still be unstable.",
         poles, pole_alt)
    b.num(2,
          r"A pendulum linearizes, near the bottom, to \(\ddot\theta + (g/L)\theta = 0\) with \(g/L = 10\). The natural frequency of that small motion is",
          wn, "rad/s",
          r"The standard form is \(\ddot\theta + \omega_n^2\theta = 0\), so \(\omega_n = \sqrt{g/L} = \sqrt{10} = " + show(wn) + r"\). The ratio \(g/L = 10\) is \(\omega_n^2\), not \(\omega_n\). Half of 10 is not the square root.",
          ms, ms_alt)

    b.mc(3,
         r"The Jacobian test is inconclusive when",
         ["every eigenvalue has a negative real part",
          "the equilibrium input is zero",
          "an eigenvalue lies on the imaginary axis",
          "the state dimension is 2"], 2,
         r"An eigenvalue with zero real part is the critical case: the linear terms do not decide stability, and the nonlinear terms can go either way. A full set of open-left-half-plane eigenvalues is conclusive and says locally stable. A zero input is just a choice of coordinates. Dimension 2 is ordinary and not a special case.",
         splane([(0, 1.5), (0, -1.5)], [], "eigenvalues on the imaginary axis"),
         "A conjugate pair sitting on the imaginary axis.")
    b.num(3,
          r"Near the origin, \(\dot x_1 = x_2\) and \(\dot x_2 = -2 x_1 + 0.5 x_2^2 + u\). The determinant of the Jacobian \(A\) is",
          2.0, "1",
          r"The quadratic term \(0.5 x_2^2\) has zero derivative at the origin, so \(A = \begin{bmatrix} 0 & 1 \\ -2 & 0 \end{bmatrix}\). Its determinant is \(2\), stored as " + show(2.0) + r". The trace is 0, which is not the determinant. The entry \(-2\) is one corner of \(A\), not \(\det A\).",
          ms, ms_alt, version=2)
    b.num(3,
          r"Return to \(\dot x = -x^3 + u\), now at the equilibrium \(x = 1.5\). The state Jacobian \(A\) is",
          a_mid, "1",
          r"\(A = -3x^2 = -3\cdot 2.25 = " + show(a_mid) + r"\). The value at \(x = 2\), which is \(-12\), belongs to a different equilibrium. The equilibrium input \(u = x^3 = 3.375\) is not \(A\).",
          mat, mat_alt)

    b.num(4,
          r"The system \(\dot x = x(1-x) + u\) rests at \(x = 3\). The linearized \(A\) is",
          a_log, "1",
          r"\(f = x - x^2 + u\), so \(A = 1 - 2x = 1 - 6 = " + show(a_log) + r"\). The factor \(1 - x = -2\) forgets the product rule and is not the derivative of \(x - x^2\). The equilibrium input, which is 6, is \(u_e\), not \(A\).",
          poles, pole_alt, ["fb-linearization"])
    b.mc(4,
         r"Gain scheduling uses linearization by",
         ["building one linear model and using it at every operating point",
          "cancelling every nonlinearity exactly, with no model error",
          "ignoring equilibria and controlling the full nonlinear vector field",
          "building a family of Jacobians along an operating curve and switching the controller as the state moves"], 3,
         r"Each equilibrium has its own Jacobian, so a scheduled controller carries several local models and interpolates among them. One model is ordinary linear control. Exact cancellation of the nonlinearity is feedback linearization, a different construction. The equilibria are exactly where each local model is built.",
         ms, ms_alt, ["gain-scheduling"])
    b.num(4,
          r"The scalar system \(\dot x = x - x^3\) has an equilibrium at \(x = 1\). The Jacobian there is",
          a_cubic_eq, "1",
          r"\(A = 1 - 3x^2\). At \(x = 1\), \(A = " + show(a_cubic_eq) + r"\). At the origin the same formula gives \(+1\), which is the unstable equilibrium, not this one. The value \(-3x = -3\) drops a factor of \(x\).",
          splane([(-2, 0)], [], "a stable real pole of the linearization"),
          "One pole mark on the negative real axis.", ["gain-scheduling"])
    b.save()


def expl_linearization():
    fig = mass_spring("local model of a mass-spring-damper")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A mass, a spring, and a damper with an external force.",
         "body_md": r"""A nonlinear state equation \(\dot x = f(x, u)\) is hard to design with and easy to approximate near a resting point. An equilibrium is a pair \((x_e, u_e)\) where \(f\) is zero, so the state stays put if nothing disturbs it. For a small step away from that point the first derivatives of \(f\) tell the story. Those derivatives are the matrices \(A\) and \(B\) of a linear system in the deviation variables.

The approximation is local. Far from the equilibrium the higher-order terms matter, and a different equilibrium has a different Jacobian. Stability of the linear model, when no eigenvalue has zero real part, decides local stability of the nonlinear equilibrium."""},
        {"heading": "Key equations", "body_md": r"""Write \(\delta x = x - x_e\) and \(\delta u = u - u_e\). Then
\[
\delta\dot x = A\,\delta x + B\,\delta u, \quad A = \frac{\partial f}{\partial x},\quad B = \frac{\partial f}{\partial u},
\]
with both partial derivatives evaluated at \((x_e, u_e)\). For a scalar \(f\), \(A\) is one number, the ordinary derivative in \(x\).

A pendulum \(\ddot\theta + (g/L)\sin\theta = 0\) becomes \(\ddot\theta + (g/L)\theta = 0\) near the bottom, so the natural frequency is \(\sqrt{g/L}\). Near the inverted position the same derivative flips sign and the linear model is unstable."""},
        {"heading": "Worked example", "body_md": r"""Take \(\dot x = -x^2 + 2u\). It rests at \(x = 4\) when \(2u = 16\), so \(u = 8\). The state derivative is \(\partial f/\partial x = -2x\), so at this equilibrium \(A = -8\) and \(B = 2\). A deviation of a few tenths decays about as \(e^{-8t}\). The same formula at \(x = 0.5\) would give \(A = -1\), which is a different operating point and a slower local mode."""},
        {"heading": "Common pitfalls", "body_md": r"""The equilibrium condition \(f(x_e, u_e) = 0\) has to be checked before the Jacobian is evaluated. Differentiating and then plugging in a point that is not an equilibrium describes a different expansion. For a product such as \(x - x^2\), the derivative is \(1 - 2x\), not \(1 - x\). A zero real-part eigenvalue means the linear test is silent. And \(B\) is the slope in \(u\), not the number \(u_e\)."""},
        {"heading": "Where this leads", "body_md": r"""Feedback linearization cancels the nonlinear terms with the input, instead of merely approximating them. Gain scheduling keeps a table of these Jacobians and interpolates the controller as the operating point moves. Both start from the same partial derivatives computed here."""},
    ]
    save_explainer("linearization", "Linearization about an equilibrium", sections, version=2)
    return words(sections)


# ---------------------------------------------------------------------------
# lti-stability
# ---------------------------------------------------------------------------

def bank_lti_stability():
    b = Bank("lti-stability")
    lhp = splane([(-1, 0), (-2, 0)], [], "left-half-plane poles")
    lhp_alt = "Two pole marks on the negative real axis."
    rhp = splane([(0.5, 0)], [], "a right-half-plane pole")
    rhp_alt = "A pole mark on the positive real axis."
    imag = splane([(0, 2), (0, -2)], [], "poles on the imaginary axis")
    imag_alt = "A conjugate pair on the imaginary axis."
    step_ok = rise("a decaying step", 0.9)
    step_alt = "A curve that settles to a constant."

    b.mc(1,
         r"A continuous-time linear system \(\dot x = Ax\) is asymptotically stable when",
         [r"every eigenvalue of \(A\) has a negative real part",
          "at least one eigenvalue has a negative real part",
          r"the trace of \(A\) is negative, with no other condition",
          "every eigenvalue has a positive real part"], 0,
         r"Asymptotic stability needs the whole spectrum in the open left half-plane. One stable eigenvalue does not rescue an unstable partner. A negative trace is necessary for a second-order system but not sufficient. Positive real parts are the unstable case.",
         lhp, lhp_alt)
    b.num(1,
          r"The polynomial \(s^2 + 3s + 2\) has two real roots. The one closer to the imaginary axis is",
          -1.0, "rad/s",
          r"\(s^2 + 3s + 2 = (s+1)(s+2)\). The roots are \(-1\) and \(-2\). The slower one is " + show(-1.0) + r". Reporting \(-2\) names the faster pole. Reporting \(+1\) flips the stable sign.",
          lhp, lhp_alt)
    b.num(1,
          r"For \(s^3 + 4s^2 + 6s + 4\), the Routh quantity \(ab - c\) (with \(a = 4\), \(b = 6\), \(c = 4\)) is",
          4 * 6 - 4, "1",
          r"The third-order test needs \(a\), \(b\), and \(c\) positive and \(ab > c\). Here \(ab - c = 24 - 4 = " + show(20) + r"\), so this polynomial passes. The product \(ab = 24\) forgets to subtract \(c\). The difference \(a - c = 0\) is not the Hurwitz minor.",
          lhp, lhp_alt)

    b.num(2,
          r"Poles lie at \(-1 \pm j5\) and at \(-8\). The time constant of the slowest mode is",
          1.0, "s",
          r"The real parts are \(-1\) and \(-8\). The slowest decay is \(e^{-t}\), so the time constant is \(1/1 = " + show(1.0) + r"\) s. The fast time constant is \(1/8\). The imaginary part 5 is an oscillation rate, not a time constant.",
          splane([(-1, 5), (-1, -5), (-8, 0)], [], "a slow pair and a fast pole"),
          "Three pole marks, one pair closer to the imaginary axis.")
    b.mc(2,
         r"A transfer function is BIBO stable while a state-space realization of it is not asymptotically stable when",
         ["every pole and every eigenvalue is in the open left half-plane",
          r"a right-half-plane eigenvalue is cancelled and does not appear as a pole of \(G(s)\)",
          "the realization is minimal",
          "the input is a sinusoid"], 1,
         r"Cancellation hides a mode from the input-output map. If that mode is unstable, the transfer function can be BIBO stable while the internal state still runs away. A minimal realization has no such hidden mode, so the two stability notions agree. A sinusoid input does not create a hidden eigenvalue.",
         rhp, rhp_alt)
    b.num(2,
          r"The polynomial \(s^2 + 1.5 s - 1\) has one root with a positive real part. That unstable root is",
          0.5, "rad/s",
          r"\((s+2)(s-0.5) = s^2 + 1.5s - 1\). The positive root is " + show(0.5) + r". The stable root \(-2\) is the other factor. The coefficient 1.5 is the sum of the root magnitudes with a sign pattern, not the unstable root itself.",
          rhp, rhp_alt)

    b.mc(3,
         r"Simple poles on the imaginary axis, and no poles in the right half-plane, mean the free response is",
         ["asymptotically stable",
          "unstable and growing",
          "bounded but not asymptotically stable",
          "identically zero for every initial state"], 2,
         r"A simple pair at \(\pm j\omega\) produces a sustained sinusoid. The state stays bounded and does not return to the origin, so the system is not asymptotically stable. Growth would require a positive real part, or a repeated imaginary pole. The zero response is only the zero initial state.",
         imag, imag_alt)
    b.num(3,
          r"The polynomial is \(s^3 + 2s^2 + 3s + k\), with \(k > 0\). The Routh boundary \(ab = c\) is crossed at \(k =\)",
          6.0, "1",
          r"Here \(a = 2\) and \(b = 3\), so \(ab = 6\). The constant term \(k\) must stay below " + show(6.0) + r". The sum \(a + b = 5\) is not the critical value. The product \(a b c\) cannot be formed until \(k\) is known, and it is not the test.",
          imag, imag_alt)
    b.num(3,
          r"Poles sit at \(-1 \pm j2\). Their damping ratio \(\zeta = |\sigma|/\sqrt{\sigma^2 + \omega^2}\) is",
          1 / math.sqrt(5), "1",
          r"The natural frequency is \(\sqrt{1^2 + 2^2} = \sqrt{5}\), and \(\zeta = 1/\sqrt{5} = " + show(1 / math.sqrt(5)) + r"\). Using the imaginary part 2 as \(\zeta\) confuses frequency with a ratio. Using \(1/2 = 0.5\) drops the real part inside the square root, and it is not the same number.",
          splane([(-1, 2), (-1, -2)], [], "a damped pair"),
          "A conjugate pair in the open left half-plane.", version=2)

    b.num(4,
          r"\(A = \begin{bmatrix} -1 & 4 \\ 0 & -3 \end{bmatrix}\). The eigenvalue closer to the imaginary axis is",
          -1.0, "rad/s",
          r"The matrix is triangular, so the eigenvalues are the diagonal entries \(-1\) and \(-3\). The slower one is " + show(-1.0) + r". The off-diagonal 4 is not an eigenvalue. The faster pole \(-3\) is the other diagonal entry.",
          matrix_fig([["-1", "4"], ["0", "-3"]], "an upper-triangular state matrix"),
          "A two-by-two triangular matrix.", ["root-locus"])
    b.mc(4,
         r"The Routh-Hurwitz test is used instead of the quadratic formula when",
         ["the polynomial is first order and the root is obvious",
          "the system is nonlinear",
          "a root is already known to be positive",
          "one only needs to know whether every root is in the open left half-plane, not the root values"], 3,
         r"Routh reads stability from the coefficients, which is what a design sweep wants. A first-order polynomial does not need it. The test is for linear characteristic polynomials, not for nonlinear vector fields. A known positive root already answers the stability question.",
         step_ok, step_alt, ["lyapunov"])
    b.num(4,
          r"For \(s^3 + 5s^2 + 8s + 6\), the Routh quantity \(ab - c\) is",
          5 * 8 - 6, "1",
          r"\(a = 5\), \(b = 8\), \(c = 6\), so \(ab - c = 40 - 6 = " + show(34) + r"\). All three coefficients are positive and this minor is positive, so the polynomial is stable. The product \(ab = 40\) forgets to subtract \(c\). The sum of the coefficients, 19, is not the Hurwitz minor.",
          lhp, lhp_alt, ["root-locus"])
    b.save()


def expl_lti_stability():
    fig = splane([(-1.2, 1.5), (-1.2, -1.5), (-4, 0)], [], "stable eigenvalues")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "Three pole marks in the open left half-plane.",
         "body_md": r"""Asymptotic stability of \(\dot x = Ax\) is a statement about every free response. Each mode behaves like \(e^{\lambda t}\) for an eigenvalue \(\lambda\). The mode decays if and only if the real part of \(\lambda\) is negative. One unstable eigenvalue is enough to make some initial states run away, so the whole spectrum has to sit in the open left half-plane.

BIBO stability asks a different question: does every bounded input produce a bounded output? For a minimal realization the two answers agree, because every eigenvalue is a pole of \(G(s)\). A cancelled mode is invisible at the output. If that hidden mode is unstable, the transfer function can look fine while the state does not."""},
        {"heading": "Key equations", "body_md": r"""Asymptotic stability: \(\mathrm{Re}(\lambda) < 0\) for every eigenvalue of \(A\). A simple pair on the imaginary axis keeps the state bounded and is not asymptotic stability.

For the characteristic polynomial \(s^3 + a s^2 + b s + c\), the Routh-Hurwitz test says every root is in the open left half-plane when \(a > 0\), \(b > 0\), \(c > 0\), and \(ab > c\). The boundary \(ab = c\) is where a root crosses the imaginary axis.

The damping ratio of a pair \(-\sigma \pm j\omega\) is \(\zeta = \sigma/\sqrt{\sigma^2 + \omega^2}\). Small \(\zeta\) is a slow decay compared with the oscillation, not a separate stability test."""},
        {"heading": "Worked example", "body_md": r"""The polynomial \(s^3 + 6s^2 + 11s + 6\) factors as \((s+1)(s+2)(s+3)\). Every root is real and negative, so the system is asymptotically stable. The Routh quantity is \(ab - c = 6\cdot 11 - 6 = 60\), comfortably positive, and \(a\), \(b\), and \(c\) are positive. The slowest time constant is \(1\), from the root at \(-1\). Moving the constant term past \(66\) would flip the sign of \(ab - c\) and create a right-half-plane root without anyone solving the cubic."""},
        {"heading": "Common pitfalls", "body_md": r"""The trace being negative is only part of the test. A positive determinant condition, or the full Routh array, still has to hold. BIBO stability of \(G(s)\) does not see a cancelled unstable mode, so an internal check still looks at the eigenvalues of \(A\). Poles on the imaginary axis are not "basically stable." And the eigenvalue closest to the axis, not the one with the largest magnitude, sets the slowest decay."""},
        {"heading": "Where this leads", "body_md": r"""Root locus watches these eigenvalues move as a gain changes, and the crossing of the imaginary axis is the stability boundary the Routh quantity just computed. Lyapunov functions give a way to prove stability when the system is no longer linear and an eigenvalue test is not available."""},
    ]
    save_explainer("lti-stability", "Stability of linear systems", sections)
    return words(sections)


# ---------------------------------------------------------------------------
# perf-specs-freq
# ---------------------------------------------------------------------------

def bank_perf():
    b = Bank("perf-specs-freq")
    mag = bode([(0.2, 18), (1, 16), (4, 6), (10, 0), (30, -12)], "loop magnitude")
    mag_alt = "A loop-gain magnitude that is high at low frequency and then crosses downward."
    sens = bode([(0.2, -20), (1, -8), (4, 2), (10, 0), (30, 0)], "sensitivity magnitude")
    sens_alt = "A sensitivity curve that is small at low frequency and rises toward 0 dB."
    step = rise("a closed-loop step", 0.5)
    step_alt = "A step response that settles."

    s36 = 1 / (2 * math.sin(math.radians(18)))
    tr = 2.2 / 5
    dist = 1 / 1.5
    pm_need = math.degrees(2 * math.asin(1 / (2 * 1.4)))

    b.mc(1,
         r"Closed-loop bandwidth \(\omega_b\) is the frequency where",
         [r"\(|T(j\omega)|\) has fallen to \(1/\sqrt{2}\) of its low-frequency value",
          r"\(|L(j\omega)|\) first equals 1",
          r"the phase of \(L\) equals \(-180^\circ\)",
          r"\(|S(j\omega)|\) is largest"], 0,
         r"Bandwidth is a property of the complementary sensitivity \(T\), 3 dB below the low-frequency plateau. The frequency where \(|L| = 1\) is the gain crossover, which is related but not the same definition. Phase of \(-180^\circ\) is the phase crossover. The peak of \(|S|\) is the peak sensitivity, not the bandwidth.",
         mag, mag_alt)
    b.num(1,
          r"At the gain crossover, \(|S| = 1/(2\sin(\mathrm{PM}/2))\). For a phase margin of \(36^\circ\) that sensitivity is",
          s36, "1",
          r"Half of \(36^\circ\) is \(18^\circ\), and \(\sin 18^\circ \approx 0.309\), so \(|S| = 1/(2\cdot 0.309) = " + show(s36) + r"\). Using \(\sin 36^\circ\) in the denominator forgets the half-angle in the distance formula. The phase margin itself, 36, is a number of degrees, not a sensitivity.",
          sens, sens_alt)
    b.num(1,
          r"A first-order closed loop has bandwidth 5 rad/s. Its 10% to 90% rise time is about \(2.2/\omega_b\), which equals",
          tr, "s",
          r"\(t_r \approx 2.2/5 = " + show(tr) + r"\) s. The reciprocal of the bandwidth, 0.2 s, is the time constant, and the 10% to 90% rise is \(\ln 9\) time constants, not one. Twice the bandwidth in the denominator would give 0.22 s and is a different rule of thumb.",
          step, step_alt)

    b.num(2,
          r"The loop transfer function is \(L(s) = 12/s\). The gain crossover frequency, where \(|L| = 1\), is",
          12.0, "rad/s",
          r"\(|L(j\omega)| = 12/\omega\). Setting that equal to 1 gives \(\omega_c = " + show(12.0) + r"\) rad/s. The square root of 12 is a different crossover, for a \(1/s^2\) loop. Half of 12 would be the crossover of \(6/s\).",
          mag, mag_alt)
    b.mc(2,
         r"A specification \(M_s \le 1.5\) limits how close the Nyquist curve may come to \(-1\). A larger allowed \(M_s\) means",
         [r"the curve must stay farther from \(-1\)",
          r"the curve may come closer to \(-1\), so the robustness demand is weaker",
          "the bandwidth must be cut in half",
          "the phase margin must be exactly 90 degrees"], 1,
         r"Peak sensitivity is the reciprocal of the distance from the curve to \(-1\). Allowing a larger peak allows a smaller distance. The stricter spec is the smaller \(M_s\). Bandwidth is not fixed by \(M_s\) alone, and a 90 degree phase margin is a much stronger requirement than \(M_s = 1.5\).",
         nyquist([(2.2, 0), (0.6, -1.1), (-0.4, -0.3), (-0.15, 0)], "Nyquist curve and the point -1"),
         "A Nyquist curve and the marked point -1.")
    b.num(2,
          r"The design requires \(M_s \le 1.5\). The Nyquist curve must therefore stay at least this far from \(-1\):",
          dist, "1",
          r"The distance is \(1/M_s = 1/1.5 = " + show(dist) + r"\). The peak 1.5 itself is the reciprocal of the distance, not the distance. Twice the reciprocal, \(1.333\), doubles the clearance the spec actually demands.",
          sens, sens_alt)

    b.mc(3,
         r"Tracking and disturbance rejection both want \(|L|\) large at low frequency. Sensor-noise rejection wants",
         [r"\(|L|\) large at high frequency as well",
          r"\(|S|\) large at high frequency",
          r"\(|T|\) small at high frequency, which means \(|L|\) small there",
          r"the crossover as high as the actuator can stand, with no further condition"], 2,
         r"Noise enters through \(T\). Making \(|T|\) small at high frequency means rolling \(|L|\) off. Keeping \(|L|\) large up there would pass the noise. A large \(|S|\) is the high-frequency fate of every proper loop, not a design goal by itself. Crossover has to stop somewhere because of that noise, the actuator, and the phase lag.",
         mag, mag_alt)
    b.num(3,
          r"At a frequency where the loop gain is real and equal to 0.25, the complementary sensitivity \(|T|\) is",
          0.25 / 1.25, "1",
          r"\(T = L/(1+L) = 0.25/1.25 = " + show(0.2) + r"\). The sensitivity \(S = 1/1.25 = 0.8\) is the other closed-loop map. The loop gain 0.25 itself is not \(T\).",
          sens, sens_alt)
    b.num(3,
          r"The gain crossover has a phase margin of \(50^\circ\). The phase of \(L\) at that frequency, in degrees, is",
          -130.0, "deg",
          r"Phase margin is the distance above \(-180^\circ\), so the phase is \(-180 + 50 = " + show(-130.0) + r"\). Reporting \(+50\) gives the margin rather than the phase. Reporting \(-50\) measures down from 0 instead of up from \(-180\).",
          bode([(1, 12), (5, 0), (20, -16)], "crossover magnitude", phase=[(1, -90), (5, -130), (20, -170)]),
          "Magnitude crossing 0 dB, with a phase curve.")

    b.num(4,
          r"The crossover formula \(|S| = 1/(2\sin(\mathrm{PM}/2))\) is required to be at most 1.4. The smallest phase margin that meets the formula, in degrees, is",
          pm_need, "deg",
          r"Set \(1/(2\sin(\mathrm{PM}/2)) = 1.4\), so \(\sin(\mathrm{PM}/2) = 1/2.8\). Then \(\mathrm{PM}/2 \approx 20.92^\circ\) and \(\mathrm{PM} = " + show(pm_need) + r"\). Using the half-angle as the answer reports about 20.9 degrees. A margin of 60 degrees gives \(|S| = 1\), which is stricter than 1.4.",
          sens, sens_alt, ["loop-shaping"])
    b.mc(4,
         r"Raising the gain crossover, while the plant phase is still falling, usually",
         ["increases the phase margin",
          "leaves both bandwidth and overshoot unchanged",
          "removes the need for a roll-off at high frequency",
          "speeds the response and spends phase margin"], 3,
         r"A higher crossover uses a frequency where a typical plant has more lag, so the phase margin shrinks, while the closed-loop bandwidth and the speed both go up. The margin does not increase. Overshoot tends to grow as the margin shrinks. The high-frequency roll-off is still required, and it gets harder as the crossover moves up.",
         mag, mag_alt, ["fund-limits"])
    b.num(4,
          r"Below 2 rad/s the spec is \(|S| \le 0.1\), and \(L\) is real and positive. The smallest such \(L\) that makes \(|S| = 0.1\) is",
          9.0, "1",
          r"\(1/(1+L) = 0.1\) gives \(1+L = 10\) and \(L = " + show(9.0) + r"\). The value 10 is \(1+L\), one step short of the loop gain. The value 0.1 is the sensitivity spec itself.",
          sens, sens_alt, ["loop-shaping"])
    b.save()


def expl_perf():
    fig = bode([(0.3, 16), (1, 14), (6, 0), (20, -14)], "crossover sketch",
               phase=[(0.3, -90), (1, -110), (6, -140), (20, -175)])
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A magnitude curve crossing from high gain to low gain, with a phase curve.",
         "body_md": r"""Time-domain specs say how fast a step rises and how much it overshoots. Frequency-domain specs say the same things in the language of \(L(j\omega)\), \(S\), and \(T\). Bandwidth is where the closed-loop map \(T\) has dropped 3 dB. Gain crossover is where \(|L| = 1\). Phase margin is how far the phase of \(L\) sits from \(-180^\circ\) at that crossover. Peak sensitivity is how close the Nyquist curve comes to \(-1\).

These are design targets. A loop that is large at low frequency tracks and rejects disturbances. A loop that is small at high frequency refuses sensor noise. The crossover is the compromise, and the phase there decides how oscillatory the compromise is."""},
        {"heading": "Key equations", "body_md": r"""For a first-order loop, \(\omega_b = 1/\tau\) and the 10% to 90% rise time is about \(2.2/\omega_b\).

When \(|L| = 1\), the distance from that point to \(-1\) is \(2\sin(\mathrm{PM}/2)\), so
\[
|S| = \frac{1}{2\sin(\mathrm{PM}/2)}
\]
at crossover. This is the sensitivity at one frequency. The peak \(M_s\) is at least this large. The clearance from the Nyquist curve to \(-1\) is \(1/M_s\).

If \(L\) is real and positive, \(|S| = 1/(1+L)\) and \(|T| = L/(1+L)\). A demand \(|S| \le 0.25\) then asks for \(L \ge 3\)."""},
        {"heading": "Worked example", "body_md": r"""A phase margin of \(48^\circ\) puts the crossover sensitivity at \(1/(2\sin 24^\circ)\). Since \(\sin 24^\circ \approx 0.407\), the sensitivity is about \(1.23\). That is already above 1, so the Nyquist curve is not far from \(-1\), but it is not a 30-degree design either. A first-order bandwidth of 10 rad/s would rise from 10% to 90% in about \(2.2/10 = 0.22\) s. The two numbers are a speed target and a damping target, and a later loop-shape has to meet both at once."""},
        {"heading": "Common pitfalls", "body_md": r"""Crossover of \(L\) is not the bandwidth of \(T\), though they are often near each other. The crossover formula gives \(|S|\) at one frequency, not automatically the peak over all frequencies. Phase margin is not the phase: a 50 degree margin means the phase is \(-130^\circ\), not \(-50^\circ\). And a larger allowed \(M_s\) is a weaker robustness spec, because it permits the curve to pass closer to \(-1\)."""},
        {"heading": "Where this leads", "body_md": r"""Loop shaping moves \(\omega_c\), the slope near crossover, and the low-frequency gain until these targets are met. Fundamental limits then say how high \(\omega_c\) can go before a right-half-plane zero, a delay, or the Bode sensitivity integral makes the spec impossible."""},
    ]
    save_explainer("perf-specs-freq", "Frequency-domain performance specifications", sections, version=2)
    return words(sections)


# ---------------------------------------------------------------------------
# pid-impl
# ---------------------------------------------------------------------------

def bank_pid_impl():
    b = Bank("pid-impl")
    pid = loop(["PID", "P"], "sampled PID loop")
    pid_alt = "A PID block and a plant inside a feedback loop."
    step = rise("derivative kick sketch", 0.4)
    step_alt = "A step that jumps and then settles."
    filt = bode([(1, 0), (10, 0), (40, -6), (200, -20)], "filtered derivative magnitude")
    filt_alt = "A flat magnitude that rolls off after a corner."

    tau_f = 0.4 / 10
    ki_t = 5 * 0.02
    d_term = 0.25 * (3.2 - 2.0) / 0.05
    tustin = 2 / 0.01
    z_fwd = 1 + (-50) * 0.05
    z_bwd = 1 / (1 - (-25) * 0.1)
    pole_f = -1 / (0.16 / 8)
    z_filter = 1 / (1 - (-50) * 0.02)

    b.mc(1,
         r"A pure derivative term \(K_d s\) is avoided in a real controller because",
         ["it amplifies high-frequency sensor noise, so a low-pass filter is put on the derivative",
          "it removes the proportional gain",
          "it makes the controller improper in a way that no filter can fix",
          "it cancels the integrator exactly"], 0,
         r"Differentiating noise makes the command chatter. A filter \(s/(\tau_f s+1)\) keeps the phase lead over a limited band and then rolls off. The proportional term is a separate path. The filtered derivative is proper. It does not cancel the integrator; the two terms sit at opposite ends of the frequency axis.",
         filt, filt_alt)
    b.num(1,
          r"The derivative time is \(\tau_d = 0.4\) s and the filter ratio is \(N = 10\), with \(\tau_f = \tau_d/N\). The filter time constant is",
          tau_f, "s",
          r"\(\tau_f = 0.4/10 = " + show(tau_f) + r"\) s. The product \(N\tau_d = 4\) puts the ratio in upside down. The derivative time 0.4 is \(\tau_d\), not the filter time.",
          filt, filt_alt)
    b.num(1,
          r"The integral gain is \(K_i = 5\) and the sample period is \(T = 0.02\) s. With backward Euler, the integrator adds this much times the current error at every sample:",
          ki_t, "1",
          r"The update is \(I[k] = I[k-1] + K_i T\, e[k]\). The coefficient of the error is \(5\cdot 0.02 = " + show(ki_t) + r"\). Using \(K_i/T = 250\) inverts the sample period. Using \(K_i\) alone forgets that the gain is per second and the sample only lasts \(T\).",
          pid, pid_alt)

    b.num(2,
          r"The derivative uses \(K_d = 0.25\) and \(T = 0.05\) s. The error is 3.2 now and was 2.0 one sample ago. The derivative's contribution to the command is",
          d_term, "1",
          r"The difference quotient is \((3.2-2.0)/0.05 = 24\). Times \(K_d\) that is " + show(d_term) + r". Reporting the difference quotient 24 leaves \(K_d\) out. Reporting \(K_d\) times the error, \(0.25\cdot 3.2 = 0.8\), treats the derivative as a proportional term.",
          step, step_alt)
    b.mc(2,
         r"Setpoint weight \(c = 0\) on the derivative means the derivative acts on",
         ["the reference only",
          "the measured output only, so a step in the reference does not kick the derivative",
          "the integral state",
          "the actuator command after saturation"], 1,
         r"With \(c = 0\) the derivative sees \(-y\), not \(c r - y\). A step in \(r\) no longer differentiates into a spike. Differentiating the reference is the \(c = 1\) choice, which is exactly the kick. The integral and the saturated command are other signals.",
         step, step_alt)
    b.num(2,
          r"Tustin's substitution uses the factor \(2/T\). For a sample period \(T = 0.01\) s that factor is",
          tustin, "1",
          r"\(2/T = 2/0.01 = " + show(tustin) + r"\). The sample period 0.01 is \(T\), not the scale. The forward-Euler factor \(1/T = 100\) is a different discretization.",
          filt, filt_alt)

    b.mc(3,
         r"A fast, stable continuous pole is mapped into discrete time. Which statement is right?",
         ["Forward Euler always keeps it inside the unit circle",
          "Tustin maps the imaginary axis to a vertical line",
          "Backward Euler maps the open left half-plane into the open unit disk",
          "A one-sample computational delay adds phase lead"], 2,
         r"Backward Euler sends \(\mathrm{Re}\, s < 0\) to \(|z| < 1\). Forward Euler can send a stable pole with a large negative real part outside the unit circle, as the next question shows. Tustin maps the imaginary axis to the unit circle, not to a vertical line. A delay of one sample adds phase lag.",
         filt, filt_alt)
    b.num(3,
          r"A continuous pole at \(s = -50\) is discretized with forward Euler, \(z = 1 + sT\), and \(T = 0.05\) s. The discrete pole is",
          z_fwd, "1",
          r"\(z = 1 + (-50)(0.05) = 1 - 2.5 = " + show(z_fwd) + r"\). That point is outside the unit circle even though the continuous pole was stable. The backward-Euler image of this same pole is inside the disk. The value \(1 + 50\cdot 0.05 = 3.5\) flips the sign of a left-half-plane pole.",
          filt, filt_alt)
    b.num(3,
          r"A continuous pole at \(s = -25\) is discretized with backward Euler, \(z = 1/(1 - sT)\), and \(T = 0.1\) s. The discrete pole is",
          z_bwd, "1",
          r"\(1 - sT = 1 - (-25)(0.1) = 3.5\), so \(z = 1/3.5 = " + show(z_bwd) + r"\). Forward Euler would have given \(1 + sT = -1.5\), outside the unit circle. The denominator 3.5 is not the discrete pole.",
          filt, filt_alt)

    b.num(4,
          r"The derivative time is \(0.16\) s and \(N = 8\). The filter pole, at \(-1/\tau_f\), is",
          pole_f, "rad/s",
          r"\(\tau_f = 0.16/8 = 0.02\) s, so the pole is \(-1/0.02 = " + show(pole_f) + r"\) rad/s. The positive value 50 drops the sign of a stable filter pole. The derivative time 0.16 is not the pole location.",
          filt, filt_alt, ["time-delay"])
    b.mc(4,
         r"A practical sample rate for a PID loop is set by the closed-loop bandwidth because",
         ["sampling faster than the bandwidth makes the discrete controller identical to the continuous one with no phase error",
          "the sample period must equal the derivative time exactly",
          "aliasing is impossible once a derivative filter is present",
          "one sample of computation delay costs little phase when there are many samples per rise"], 3,
         r"A delay of one sample is \(\omega T\) radians of phase at the crossover. Keeping \(T\) well below the rise time keeps that phase small. Sampling faster reduces the error; it does not delete it. The derivative time and the sample period are independent knobs. A derivative filter is not an anti-alias filter on the measurement.",
         pid, pid_alt, ["integral-action"])
    b.num(4,
          r"The derivative filter pole at \(-50\) rad/s is discretized with backward Euler and \(T = 0.02\) s. The resulting \(z\)-plane pole is",
          z_filter, "1",
          r"\(z = 1/(1 - (-50)(0.02)) = 1/2 = " + show(z_filter) + r"\). Forward Euler of the same pole and sample period lands at \(1 - 1 = 0\), a different map. The continuous pole \(-50\) is not a \(z\)-plane number.",
          filt, filt_alt, ["mpc"])
    b.save()


def expl_pid_impl():
    fig = loop(["PID", "P"], "PID in front of a plant")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A PID controller and a plant in a feedback loop.",
         "body_md": r"""The three-term sum \(K_p e + K_i\int e + K_d \dot e\) is not what a computer should run. A pure derivative amplifies the measurement noise, and a step in the reference becomes a spike if the derivative looks at the error. The integral and the derivative also have to become updates that use samples, and a one-sample delay is part of the loop whether or not the algebra mentions it.

The practical repair is small. Filter the derivative. Let the proportional and derivative terms look at a weighted reference, often with no derivative on the reference at all. Then replace \(s\) by a discrete map and check that stable continuous poles stay inside the unit circle."""},
        {"heading": "Key equations", "body_md": r"""The filtered derivative is \(K_d s/(\tau_f s + 1)\) with \(\tau_f = \tau_d/N\). The filter pole sits at \(-N/\tau_d\). Setpoint weights \(b\) and \(c\) form the proportional input \(b r - y\) and the derivative input \(c r - y\). The choice \(c = 0\) keeps a reference step out of the derivative. These weights do not change the loop gain, which is still measured from \(y\).

Forward Euler uses \(z = 1 + sT\). Backward Euler uses \(z = 1/(1 - sT)\). Tustin uses \(s = (2/T)(z-1)/(z+1)\). The integral update with backward Euler adds \(K_i T\) times the current error at every sample."""},
        {"heading": "Worked example", "body_md": r"""Take \(\tau_d = 0.32\) s and \(N = 4\). The filter time constant is \(0.32/4 = 0.08\) s, and the filter pole is at \(-12.5\) rad/s. A sample period of \(0.03\) s sits comfortably under that corner. Forward Euler sends a continuous pole at \(-12\) to \(z = 1 + (-12)(0.03) = 0.64\), inside the unit circle. The same map on a pole at \(-80\) gives \(z = 1 - 2.4 = -1.4\), outside the disk. The filter corner and the sample period have to be chosen together."""},
        {"heading": "Common pitfalls", "body_md": r"""Forward Euler is the easy formula and the one that can turn a stable fast pole into an unstable discrete pole. Backward Euler and Tustin do not. The factor in the integrator is \(K_i T\), not \(K_i/T\). Setpoint weighting changes the zeros from reference to output and does not retune the loop gain. And a derivative filter is not a license to sample slowly: one sample of delay is still \(\omega T\) radians of phase at the crossover."""},
        {"heading": "Where this leads", "body_md": r"""A computational delay is a time delay in the loop, with the phase lag that delay always adds. Integral action in state feedback meets the same windup problem once the command saturates. Model-predictive controllers take the saturation into the optimization instead of repairing it afterward."""},
    ]
    save_explainer("pid-impl", "Implementing a PID controller", sections, version=2)
    return words(sections)


# ---------------------------------------------------------------------------
# pid-tuning
# ---------------------------------------------------------------------------

def bank_pid_tuning():
    b = Bank("pid-tuning")
    step = rise("reaction curve", 1.4)
    step_alt = "A delayed rise toward a steady value."
    osc = plot(lambda t: math.exp(-0.02 * t) * math.sin(2 * math.pi * t / 4), 0, 16, "t", "y", "ultimate oscillation")
    osc_alt = "A nearly constant oscillation."
    loopfig = loop(["PID", "P"], "PID being tuned")
    loop_alt = "A PID controller and a plant in feedback."

    kp_u = 0.6 * 5
    ti = 4 / 2
    td = 4 / 8
    a_re = 2 * 1.5 / 6
    kp_pid = 1.2 / a_re
    kp_pi = 0.9 / a_re
    kp_lam = 6 / (2 * (3 + 1.5))
    kd_u = (0.6 * 12) * (1.6 / 8)
    a2 = 4 * 0.5 / 8
    kp2 = 1.2 / a2

    b.mc(1,
         r"The ultimate-gain experiment, used to tune a PID from one number and one period,",
         ["raises the proportional gain until the loop oscillates at constant amplitude",
          "applies a step with the loop open and fits a delay",
          "sets the integral gain to zero and the derivative gain to the plant gain",
          "measures the DC sensitivity and stops"], 0,
         r"The ultimate gain \(K_u\) is the proportional gain on the stability boundary, and \(T_u\) is the period of that oscillation. A step on the open plant is the reaction-curve experiment, a different test. Zeroing the integral and copying the plant gain is not the procedure. DC sensitivity does not locate the boundary.",
         osc, osc_alt)
    b.num(1,
          r"The ultimate-gain PID rule uses \(K_p = 0.6 K_u\). For \(K_u = 5\), the proportional gain is",
          kp_u, "1",
          r"\(K_p = 0.6 \cdot 5 = " + show(kp_u) + r"\). Using the whole ultimate gain, 5, skips the 0.6 factor and is a more aggressive starting point than the rule. Half of \(K_u\) is 2.5, which is not 0.6.",
          loopfig, loop_alt)
    b.num(1,
          r"The same rule uses \(\tau_i = T_u/2\). For an ultimate period \(T_u = 4\) s, the integral time is",
          ti, "s",
          r"\(\tau_i = 4/2 = " + show(ti) + r"\) s. The period itself, 4 s, would be \(\tau_i\) only if the factor were 1. A quarter period, 1 s, is closer to the derivative time than to the integral time.",
          osc, osc_alt)

    b.num(2,
          r"Still with \(T_u = 4\) s, the ultimate-gain rule sets \(\tau_d = T_u/8\). The derivative time is",
          td, "s",
          r"\(\tau_d = 4/8 = " + show(td) + r"\) s. Half the period, 2 s, is the integral time from the same rule. The period 4 s is \(T_u\), not \(\tau_d\).",
          osc, osc_alt)
    b.mc(2,
         r"The reaction-curve method, as opposed to the ultimate-gain experiment,",
         ["drives the closed loop to the edge of stability",
          "fits a gain, a lag, and a delay to an open-loop step, and never needs the critical gain",
          "works only for plants with no delay",
          "returns the three PID gains with no plant model at all"], 1,
         r"A step is applied to the plant alone. The response is summarized by a gain \(K\), a time constant \(\tau\), and a delay \(L\). The ultimate-gain test is the one that sits on the stability boundary. The fit is built for plants that do have a delay. The arithmetic still uses \(K\), \(\tau\), and \(L\).",
         step, step_alt)
    b.num(2,
          r"A plant fit has \(K = 2\), \(\tau = 6\) s, and delay \(L = 1.5\) s. With \(a = KL/\tau\) and the PID rule \(K_p = 1.2/a\), the proportional gain is",
          kp_pid, "1",
          r"\(a = 2\cdot 1.5/6 = 0.5\), so \(K_p = 1.2/0.5 = " + show(kp_pid) + r"\). Using \(1.2\, a = 0.6\) inverts the rule. Using the PI coefficient 0.9 in place of 1.2 is a different rule and a smaller gain.",
          step, step_alt, version=2)

    b.mc(3,
         r"Lambda tuning of the same first-order-plus-delay plant is usually",
         ["more oscillatory than the ultimate-gain rule, on purpose",
          "independent of the desired closed-loop time constant",
          r"milder, because the designer names a closed-loop time constant \(\lambda\) instead of sitting on the stability boundary",
          "a way to remove the plant delay from the model"], 2,
         r"The lambda rule \(K_p = \tau/(K(\lambda+L))\) gets smaller as the requested closed-loop time constant gets larger, so it is the detuned, explicit choice. The ultimate-gain rule does not ask for \(\lambda\). A larger \(\lambda\) is the milder loop. The delay stays in the formula; it is not deleted.",
         step, step_alt)
    b.num(3,
          r"For that same plant, \(a = 0.5\). The PI reaction-curve rule \(K_p = 0.9/a\) gives",
          kp_pi, "1",
          r"\(K_p = 0.9/0.5 = " + show(kp_pi) + r"\). The PID coefficient 1.2 would give 2.4 on this same \(a\). Using \(0.9\, a = 0.45\) inverts the fraction.",
          step, step_alt)
    b.num(3,
          r"Lambda tuning uses \(K_p = \tau/(K(\lambda+L))\). With \(K = 2\), \(\tau = 6\), \(L = 1.5\), and \(\lambda = 3\), the proportional gain is",
          kp_lam, "1",
          r"The denominator is \(K(\lambda+L) = 2\cdot 4.5 = 9\), so \(K_p = 6/9 = " + show(kp_lam) + r"\). Dropping the delay and using \(\tau/(K\lambda) = 6/6 = 1\) is the delay-free rule. The reaction-curve value 2.4 ignores \(\lambda\) entirely.",
          loopfig, loop_alt)

    b.num(4,
          r"Ultimate gain \(K_u = 12\) and ultimate period \(T_u = 1.6\) s. The PID rule gives \(K_p = 0.6 K_u\) and \(\tau_d = T_u/8\). The derivative gain \(K_d = K_p \tau_d\) is",
          kd_u, "1",
          r"\(K_p = 0.6\cdot 12 = 7.2\) and \(\tau_d = 1.6/8 = 0.2\), so \(K_d = 7.2\cdot 0.2 = " + show(kd_u) + r"\). Reporting \(\tau_d = 0.2\) stops one multiplication early. Reporting \(K_p = 7.2\) is the proportional gain, not \(K_d\).",
          osc, osc_alt, ["loop-shaping"])
    b.mc(4,
         r"If the ultimate period is read off a half-cycle and then used as \(T_u\),",
         [r"\(K_p\) doubles, because \(K_p\) depends on \(T_u\)",
          r"the derivative time is unchanged, because \(\tau_d\) does not use \(T_u\)",
          "the experiment has to be repeated at a different sample rate before any gain is valid",
          r"the integral time \(\tau_i = T_u/2\) comes out half of what the full period would have given"], 3,
         r"\(K_p = 0.6 K_u\) does not use the period at all. Both \(\tau_i\) and \(\tau_d\) scale with \(T_u\), so a half-period reading cuts both of them in half. The sample rate is a separate implementation choice and does not repair a misread period.",
         osc, osc_alt, ["gain-scheduling"])
    b.num(4,
          r"A second plant fit has \(K = 4\), \(\tau = 8\) s, and \(L = 0.5\) s. The PID reaction-curve gain \(K_p = 1.2\,\tau/(KL)\) is",
          kp2, "1",
          r"\(KL/\tau = 4\cdot 0.5/8 = 0.25\), so \(K_p = 1.2/0.25 = " + show(kp2) + r"\). Using \(\tau/(KL) = 4\) drops the 1.2. Using the previous plant's \(a = 0.5\) gives 2.4 and ignores these new numbers.",
          step, step_alt, ["robust-perf"])
    b.save()


def expl_pid_tuning():
    fig = step_response("open-loop reaction curve", tau=1.6, goal=1.0)
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A smooth rise toward a steady value.",
         "body_md": r"""The three PID gains are a design, not a guess, once the plant has been summarized by one experiment. Two classical experiments are enough to get a starting point. The ultimate-gain test closes the loop with proportional control and turns the gain up until the output oscillates at constant amplitude. The reaction-curve test leaves the loop open, steps the plant, and fits a gain, a lag, and a delay.

Both rules are aggressive starting points. Lambda tuning uses the same three plant numbers and one extra choice, the closed-loop time constant the designer actually wants, and it usually comes out milder."""},
        {"heading": "Key equations", "body_md": r"""From an ultimate gain \(K_u\) and period \(T_u\), the PID starting point is
\[
K_p = 0.6 K_u, \quad \tau_i = T_u/2, \quad \tau_d = T_u/8.
\]
The derivative gain in parallel form is \(K_d = K_p \tau_d\).

From a first-order-plus-delay fit, \(a = KL/\tau\). The PID reaction-curve gain is \(K_p = 1.2/a\), and the PI version uses \(0.9/a\). Lambda tuning sets
\[
K_p = \frac{\tau}{K(\lambda + L)}, \quad \tau_i = \tau.
\]
A larger \(\lambda\) is a slower, gentler loop."""},
        {"heading": "Worked example", "body_md": r"""Suppose the ultimate test oscillates at gain 11 with period 7.5 s. Then \(K_p = 0.6\cdot 11 = 6.6\), the integral time is \(7.5/2 = 3.75\) s, and the derivative time is \(7.5/8 = 0.9375\) s. The parallel derivative gain is \(6.6 \times 0.9375\). Nothing in that arithmetic looked at a desired overshoot. If the oscillation looks fierce on the real plant, the lambda rule on a step fit is the systematic way to back off, by naming a larger closed-loop time constant rather than by nudging \(K_p\) at random."""},
        {"heading": "Common pitfalls", "body_md": r"""\(K_p\) from the ultimate-gain rule does not depend on \(T_u\). Misreading a half-cycle as the full period leaves \(K_p\) alone and cuts \(\tau_i\) and \(\tau_d\) in half. The reaction-curve gain is \(1.2/a\), not \(1.2\, a\). Lambda tuning still contains the delay: dropping \(L\) out of \(\lambda + L\) is the rule for a plant that has no delay. And a negative plant gain, used with a positive controller gain, closes positive feedback. The sign of \(K\) has to end up as negative feedback."""},
        {"heading": "Where this leads", "body_md": r"""Loop shaping replaces these fixed coefficients with a Bode target: a crossover, a slope, and a phase margin. Gain scheduling repeats the fit at several operating points when \(K\) and \(\tau\) move. Robust performance then asks whether the tuned loop still meets the spec when \(K\), \(\tau\), and \(L\) are only known inside a range."""},
    ]
    save_explainer("pid-tuning", "Tuning a PID controller", sections)
    return words(sections)


# ---------------------------------------------------------------------------
# realization
# ---------------------------------------------------------------------------

def bank_realization():
    b = Bank("realization")
    mat = matrix_fig([["0", "1"], ["-a0", "-a1"]], "controllable companion matrix")
    mat_alt = "A companion matrix with a symbolic last row."
    poles = splane([(-2, 0), (-5, 0)], [], "two real poles")
    pole_alt = "Two pole marks on the negative real axis."
    seriesfig = series(["G"], "a transfer function as one block")
    series_alt = "A single block labeled as the plant."

    b.mc(1,
         r"A realization of a transfer function \(G(s)\) is",
         [r"any state-space model whose input-output map is \(G(s)\)",
          r"the unique set of matrices \(A, B, C, D\) that can ever represent \(G\)",
          r"the inverse of \(G(s)\)",
          "a list of the poles with the zeros thrown away"], 0,
         r"Many state-space models share one transfer function. A change of state basis produces another realization of the same \(G\). There is no unique quadruple \((A,B,C,D)\). The inverse is a different system. Poles alone do not fix the zeros or the gain.",
         seriesfig, series_alt)
    b.num(1,
          r"\(G(s) = 8/(s+2)\) has no cancellation. A minimal realization uses this many states:",
          1.0, "1",
          r"The denominator degree is 1, so the minimal state dimension is " + show(1.0) + r". A two-state model would hide a cancelled mode. The numerator 8 is a gain, not a state count.",
          splane([(-2, 0)], [], "one real pole"),
          "One pole mark on the negative real axis.", version=2)
    b.num(1,
          r"\(G(s) = (s+3)/(s^2 + 7s + 10)\) has no cancellation. A minimal realization uses this many states:",
          2.0, "1",
          r"The denominator is degree 2 and nothing cancels, so the minimal dimension is " + show(2.0) + r". The single zero does not reduce the state count. A first-order model would drop a pole.",
          poles, pole_alt)

    b.num(2,
          r"In controllable canonical form, the denominator \(s^2 + 4s + 5\) puts \(-a_0\) in the bottom-left entry of \(A\). That entry is",
          -5.0, "1",
          r"\(a_0 = 5\), so the bottom-left entry is \(-5\), stored as " + show(-5.0) + r". The coefficient \(a_1 = 4\) belongs in the bottom-right entry, with a minus sign, as \(-4\). Using \(+5\) drops the sign in the companion matrix.",
          mat, mat_alt)
    b.mc(2,
         r"If \(x = Tz\) with \(T\) invertible, the new realization has",
         [r"a different transfer function and a similar \(A\)",
          r"the same transfer function, and an \(A\) matrix similar to the old one",
          r"the same \(A\) matrix, entry by entry",
          r"new poles, equal to the eigenvalues of \(T\)"], 1,
         r"A change of basis preserves the input-output map and replaces \(A\) by \(T^{-1}AT\), or \(TAT^{-1}\), depending on which way \(T\) is defined. The entries of \(A\) change unless \(T\) is trivial. The poles stay the eigenvalues of \(A\), not the eigenvalues of \(T\).",
         mat, mat_alt)
    b.num(2,
          r"\(G(s) = 6(s+1)/((s+1)(s+3))\) cancels to a first-order system. The DC gain of that minimal model is",
          2.0, "1",
          r"After cancelling \(s+1\), \(G(s) = 6/(s+3)\) and \(G(0) = 6/3 = " + show(2.0) + r"\). The uncancelled expression at \(s = 0\) is also \(6/3 = 2\), so the cancellation does not change the gain. The state count 1 is the order, not the DC gain.",
          seriesfig, series_alt)

    b.mc(3,
         r"Observable canonical form, compared with controllable canonical form of the same \(G(s)\),",
         ["has different poles",
          "uses a different transfer function",
          "is the transpose structure: the coefficients run down a column instead of along the last row",
          r"exists only when \(G\) has no zeros"], 2,
         r"The two companion forms are transposes of each other, up to the way \(B\) and \(C\) carry the numerator. They realize the same \(G\) and therefore have the same poles. Zeros are allowed in both forms; they move into \(C\) or into \(B\).",
         mat, mat_alt)
    b.num(3,
          r"\(G(s) = (3s+9)/(s^2 + 4s + 18)\). The DC gain is",
          9 / 18, "1",
          r"\(G(0) = 9/18 = " + show(0.5) + r"\). The ratio of the leading coefficients, \(3/1 = 3\), is the high-frequency behavior of a relative-degree-1 system only after dividing by \(s\), not the DC gain. The pole sum 4 is the coefficient of \(s\), not \(G(0)\).",
          seriesfig, series_alt)
    b.num(3,
          r"A controllable companion matrix is \(A = \begin{bmatrix} 0 & 1 \\ -2 & -7 \end{bmatrix}\). In \(s^2 + a_1 s + a_0\), the coefficient \(a_1\) is",
          7.0, "1",
          r"The last row is \((-a_0,\; -a_1) = (-2,\; -7)\), so \(a_1 = " + show(7.0) + r"\). The constant term \(a_0\) is 2. The trace of \(A\) is \(-7\), which is \(-a_1\), not \(a_1\).",
          matrix_fig([["0", "1"], ["-2", "-7"]], "a numerical companion matrix"),
          "A companion matrix with a numerical last row.")

    b.num(4,
          r"\(G(s) = (s+4)/((s+4)(s+1)(s+6))\) has one cancellation. A minimal realization uses this many states:",
          2.0, "1",
          r"The written denominator has degree 3 and one factor cancels, leaving degree 2. The minimal state count is " + show(2.0) + r". Keeping all three poles counts a hidden mode. Cancelling and then dropping a second pole would leave a first-order model of the wrong system.",
          poles, pole_alt, ["reachability"])
    b.mc(4,
         r"A non-minimal realization hides a mode. That mode is",
         [r"always slower than every pole of \(G(s)\)",
          "visible in the transfer function as an extra zero that does not cancel",
          r"a pole of \(G(s)\) that was never an eigenvalue",
          "either unreachable or unobservable, which is why it cancels"], 3,
         r"Cancellation means the hidden eigenvalue does not appear in \(G(s)\). The mode is unreachable, unobservable, or both. It need not be the slowest mode. An extra zero that does not cancel is visible and does not by itself add a hidden state. Every pole of a realization's transfer function is an eigenvalue; the hidden ones are the eigenvalues that are not poles.",
         poles, pole_alt, ["observability"])
    b.num(4,
          r"The denominator \(s^2 + 9s + 14\) is written in controllable canonical form. The determinant of \(A\), which equals \(a_0\), is",
          14.0, "1",
          r"For the companion matrix, \(\det A = a_0 = " + show(14.0) + r"\). The coefficient 9 is \(a_1\), which is minus the trace, not the determinant. The product of the two coefficients is not \(a_0\).",
          mat, mat_alt, ["state-feedback"])
    b.save()


def expl_realization():
    fig = matrix_fig([["0", "1"], ["-a0", "-a1"]], "controllable canonical form")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A companion matrix with symbols in the last row.",
         "body_md": r"""Going from a transfer function back to state space is the opposite of the resolvent formula, and it does not have one answer. Any matrices whose input-output map equals \(G(s)\) are a realization. A change of coordinates produces another one, with a similar \(A\) and the same poles.

The useful normal forms put the denominator coefficients in a fixed place. Controllable canonical form writes them along the last row. Observable canonical form writes them down a column. Both are valid. A realization is minimal when nothing cancels, so the number of states equals the degree of \(G\) after common factors are removed."""},
        {"heading": "Key equations", "body_md": r"""For \(G(s) = (b_1 s + b_0)/(s^2 + a_1 s + a_0)\), one controllable form is
\[
A = \begin{bmatrix} 0 & 1 \\ -a_0 & -a_1 \end{bmatrix}, \quad
B = \begin{bmatrix} 0 \\ 1 \end{bmatrix}, \quad
C = \begin{bmatrix} b_0 & b_1 \end{bmatrix}.
\]
The characteristic polynomial is \(\det(sI - A) = s^2 + a_1 s + a_0\). The DC gain of a strictly proper \(G\) is \(b_0/a_0\).

If a factor \((s-z)\) sits in both the numerator and the denominator, a minimal realization deletes it. The cancelled eigenvalue can still be placed in a larger non-minimal model, where it is unreachable or unobservable."""},
        {"heading": "Worked example", "body_md": r"""Take \(G(s) = (6s + 24)/(s^2 + 13s + 16)\). Then \(a_0 = 16\), \(a_1 = 13\), \(b_0 = 24\), and \(b_1 = 6\). The companion matrix has last row \((-16,\; -13)\), and \(C = (24,\; 6)\). The DC gain is \(24/16 = 1.5\). Nothing cancels, so two states are necessary and sufficient. A different basis would scramble the entries and leave \(G(0) = 1.5\) and the poles alone."""},
        {"heading": "Common pitfalls", "body_md": r"""The bottom-left entry is \(-a_0\), not \(a_0\), and not \(-a_1\). Counting states from the written denominator, before cancellation, inflates a non-minimal model. DC gain is \(b_0/a_0\) for the form above, not the ratio of the highest coefficients. And similar matrices share eigenvalues, so a change of basis cannot move a pole, even though every entry of \(A\) may change."""},
        {"heading": "Where this leads", "body_md": r"""Reachability asks whether the input can excite every state of this realization, and observability asks whether every state appears at the output. State feedback then places the eigenvalues of \(A - BK\), which is legal in the controllable form precisely because that form was built to be controllable when nothing has cancelled."""},
    ]
    save_explainer("realization", "Realizations of a transfer function", sections)
    return words(sections)


# ---------------------------------------------------------------------------
# uncertainty
# ---------------------------------------------------------------------------

def bank_uncertainty():
    b = Bank("uncertainty")
    bode_u = bode([(0.3, 2), (1, 4), (4, 8), (15, 14)], "a weight that grows with frequency")
    bode_alt = "A magnitude that rises toward high frequency."
    plant = series(["P0"], "nominal plant")
    plant_alt = "A single block for the nominal plant."
    band = plot(lambda w: 0.15 + 0.05 * (w + 0.5), 0, 5.5, "w", "Wm", "relative uncertainty")
    band_alt = "A bound that grows as frequency increases."

    b.mc(1,
         r"Multiplicative uncertainty describes the plant error by bounding",
         [r"the relative error \(|P - P_0|/|P_0|\)",
          r"the absolute error \(|P - P_0|\) only",
          r"the sensitivity function \(S\)",
          r"the closed-loop bandwidth"], 0,
         r"A multiplicative weight says \(|P - P_0| \le |W_m|\,|P_0|\), which is a relative bound. The absolute error is the additive weight \(W_a\). Sensitivity is a closed-loop map, not a description of the plant error. Bandwidth is a performance number.",
         band, band_alt)
    b.num(1,
          r"The nominal gain is \(P_0 = 10\) and the true gain is \(P = 12\). The relative error \(|P-P_0|/|P_0|\) is",
          abs(12 - 10) / 10, "1",
          r"\(|12-10|/10 = " + show(0.2) + r"\). The absolute error is 2, which is the additive mismatch, not the relative one. The ratio \(12/10 = 1.2\) is the gain ratio, one plus the relative error.",
          plant, plant_alt)
    b.num(1,
          r"The nominal gain is 4 and the additive bound is \(|P - P_0| \le 0.5\). The largest possible \(|P|\) in that bound is",
          4.5, "1",
          r"The plant can sit 0.5 above the nominal, so the largest magnitude in the bound is \(4 + 0.5 = " + show(4.5) + r"\). The nominal 4 leaves the whole uncertainty budget unused. Twice the bound, 1, is not a plant gain.",
          plant, plant_alt)

    b.num(2,
          r"A gain is known to within \(\pm 35\) percent. The multiplicative weight \(|W_m|\) that covers that range is",
          0.35, "1",
          r"A \(\pm 35\) percent gain error is exactly \(|W_m| = " + show(0.35) + r"\). The factor 1.35 is the largest gain ratio \(P/P_0\), which is \(1 + W_m\), not the weight. Half of 35 percent would be a one-sided reading of a two-sided statement.",
          band, band_alt)
    b.mc(2,
         r"A resonant mode that was left out of the model is usually drawn as",
         ["a constant parametric interval on the DC gain",
          "dynamic uncertainty whose weight grows where the missing mode can be large",
          "a change of the reference",
          "sensor noise, which is an external input rather than a plant error"], 1,
         r"An unmodeled resonance is dynamics, and it shows up over a band of frequencies, so \(|W|\) is larger there. A constant interval on the DC gain is parametric uncertainty and does not capture a peak at one frequency. The reference is a command, not a plant error. Sensor noise is a different input to the loop.",
         bode_u, bode_alt)
    b.num(2,
          r"The nominal gain is 8 and the additive weight is \(|W_a| = 2.4\). The equivalent relative weight \(|W_a|/|P_0|\) is",
          2.4 / 8, "1",
          r"Dividing the additive bound by the nominal gain gives \(2.4/8 = " + show(0.3) + r"\). The additive number 2.4 stays absolute until it is divided by \(P_0\). The sum \(8 + 2.4 = 10.4\) is the largest plant gain, not the relative weight.",
          plant, plant_alt)

    b.mc(3,
         r"A resistor that lies somewhere in a known interval, with no extra dynamics, is",
         ["unmodeled high-frequency dynamics",
          "multiplicative uncertainty that must grow with frequency",
          "parametric uncertainty",
          "a right-half-plane zero"], 2,
         r"One real parameter in an interval is the definition of parametric uncertainty. Unmodeled dynamics are extra states or extra modes, not a number in a range. A multiplicative weight may be used to cover the interval, but it does not have to grow with frequency if the error is a pure gain. A right-half-plane zero is a feature of the nominal model, not of an interval.",
         plant, plant_alt)
    b.num(3,
          r"The nominal gain is 5 and a measurement of the plant gives 6.5. The absolute error \(|P - P_0|\) is",
          1.5, "1",
          r"\(|6.5 - 5| = " + show(1.5) + r"\). The relative error is \(1.5/5 = 0.3\), which divides by the nominal gain. The measured value 6.5 is the plant, not the error.",
          plant, plant_alt)
    b.num(3,
          r"The nominal gain is 8 and \(|W_m| = 0.25\). The largest plant gain allowed by that multiplicative bound is",
          8 * 1.25, "1",
          r"\(P\) can be as large as \(P_0(1 + |W_m|) = 8\cdot 1.25 = " + show(10) + r"\). The weight 0.25 is the relative budget, not a gain. The nominal 8 ignores the budget.",
          band, band_alt)

    b.num(4,
          r"A multiplicative weight has \(|W_m| = 0.4\). The small-gain test \(|T W_m| < 1\) allows \(|T|\) up to",
          1 / 0.4, "1",
          r"The product bound rearranges to \(|T| < 1/|W_m| = 1/0.4 = " + show(2.5) + r"\). The weight 0.4 itself is not a limit on \(T\). Twice the reciprocal, 5, doubles the room the test actually gives.",
          bode_u, bode_alt, ["robust-stability"])
    b.mc(4,
         r"Making an uncertainty weight larger than the error you can actually justify",
         ["makes every spec easier to meet",
          "does not change the controller, because weights are not part of the model",
          "shrinks the set of plants under consideration",
          "is conservative: the spec is asked to hold for plants you do not believe are real"], 3,
         r"A larger weight covers more plants, including ones outside the evidence. A controller that works for all of them is harder to find, not easier. The weight is part of the model. Shrinking the set would mean a smaller weight.",
         band, band_alt, ["robust-perf"])
    b.num(4,
          r"The nominal gain is 20 and the multiplicative uncertainty is 30 percent. The largest plant gain in that bound is",
          20 * 1.3, "1",
          r"\(P \le 20\cdot 1.30 = " + show(26) + r"\). Thirty percent of 20 is 6, which is the additive half-width, not the largest gain. The nominal 20 leaves the uncertainty out.",
          plant, plant_alt, ["robust-perf"])
    b.save()


def expl_uncertainty():
    fig = bode([(0.4, 0), (1, 2), (3, 6), (10, 12)], "growing uncertainty weight")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A weight whose magnitude rises with frequency.",
         "body_md": r"""A nominal plant \(P_0\) is a model, not the hardware. Uncertainty is the explicit statement of how far the hardware may be from that model. Two shapes cover most of the statements used in loop design. An additive weight bounds the absolute error \(|P - P_0|\). A multiplicative weight bounds the relative error \(|P - P_0|/|P_0|\).

A parameter that simply sits in an interval, such as a gain known to ten percent, is parametric uncertainty. A resonance that was never written into \(P_0\) is dynamic uncertainty. Dynamic error is usually small at low frequency, where the model was fitted, and large at high frequency, where the neglected modes live. The weight is drawn so that it grows there."""},
        {"heading": "Key equations", "body_md": r"""Additive form: \(P = P_0 + W_a \Delta\) with \(|\Delta| \le 1\), so \(|P - P_0| \le |W_a|\). Multiplicative form: \(P = P_0(1 + W_m \Delta)\) with \(|\Delta| \le 1\), so
\[
\frac{|P - P_0|}{|P_0|} \le |W_m|.
\]
A \(\pm 22\) percent gain error is \(|W_m| = 0.22\), and the plant gain then lies between \(0.78|P_0|\) and \(1.22|P_0|\). Dividing an additive bound by \(|P_0|\) converts it into a relative one at that frequency. The small-gain test on a multiplicative weight will later demand \(|T W_m| < 1\)."""},
        {"heading": "Worked example", "body_md": r"""Suppose the nominal gain is 7 and a bench measurement reads 9. The absolute error is \(9 - 7 = 2\). The relative error is \(2/7 \approx 0.286\). An additive weight of 2 covers this one measurement with nothing to spare. A multiplicative weight of 0.286 covers it as a fraction of the nominal gain. If the next unit on the production line could be another 10 percent high, the weight has to grow past 0.286. Using 0.286 because it matches today's bench is how an uncertainty model becomes too small."""},
        {"heading": "Common pitfalls", "body_md": r"""Relative and absolute errors are not interchangeable: an error of 2 on a gain of 7 is not an error of 2 on a gain of 70. A weight that is larger than the evidence is conservative and can make an otherwise fine spec look impossible. A weight that is smaller than the evidence is optimistic, and the robust test will pass for a set of plants that does not include the real one. Where \(|W_m|\) reaches 1, the model no longer determines the sign of the plant, and the loop gain at that frequency should already be small."""},
        {"heading": "Where this leads", "body_md": r"""Robust stability turns \(|W_m|\) into a limit on \(|T|\). Robust performance asks the sensitivity spec to hold for every plant inside the weight, not only for \(P_0\). Both of those tests are only as honest as the weight written down here."""},
    ]
    save_explainer("uncertainty", "Modeling uncertainty", sections, version=2)
    return words(sections)


# ---------------------------------------------------------------------------
# windup
# ---------------------------------------------------------------------------

def bank_windup():
    b = Bank("windup")
    cmd = plot(lambda t: 5.0 if t > 0.8 else 6 * t, 0, 4, "t", "u", "command against a limit")
    cmd_alt = "A command that rises and then sits flat at a limit."
    step = rise("a step with a long tail", 1.3)
    step_alt = "A step response with a slow return."
    loopfig = loop(["PI", "P"], "PI loop with a limited actuator")
    loop_alt = "A PI controller and a plant in feedback."

    growth = 4 * 2 * 3
    excess = 16 - 10
    rate = (8 - 18) / 0.5
    tt = math.sqrt(4 * 0.64)
    would = 2.5 * 1.2
    frac = 4 / 9
    unwind = (8 - 15) / 0.2
    prevented = 6 * 0.5 * 4

    b.mc(1,
         r"Integrator windup is what happens when",
         ["the actuator is stuck at a limit and the integrator keeps accumulating the error",
          "the proportional gain is set to zero",
          "the derivative filter is removed",
          "the reference is zero and the error is zero"], 0,
         r"While the actuator cannot follow the command, a nonzero error is still integrated, so the integrator state runs far past the value that the limit can actually produce. Zero proportional gain is a different detuning. The derivative filter is about noise, not about a stuck actuator. Zero error does not wind anything up.",
         cmd, cmd_alt)
    b.num(1,
          r"During saturation the error stays at 2 for 3 seconds, and \(K_i = 4\). The integrator state grows by",
          growth, "1",
          r"The integrator adds \(K_i\) times the error times the duration: \(4\cdot 2\cdot 3 = " + show(growth) + r"\). Using \(K_i\) times the error, 8, forgets how long the saturation lasts. Using the duration alone, 3, forgets the gain.",
          cmd, cmd_alt)
    b.num(1,
          r"The unsaturated command is 16 and the actuator limit is \(\pm 10\). The amount by which the command exceeds the limit is",
          excess, "1",
          r"The excess is \(16 - 10 = " + show(excess) + r"\). The limit 10 is what the actuator actually applies, not the excess. The unsaturated command 16 is the controller output before the limit.",
          cmd, cmd_alt)

    b.num(2,
          r"Back-calculation adds \((u_{\mathrm{sat}} - u)/T_t\) to the integrator input. With \(u = 18\), \(u_{\mathrm{sat}} = 8\), and \(T_t = 0.5\) s, that added rate is",
          rate, "1",
          r"\((8 - 18)/0.5 = " + show(rate) + r"\). The positive difference \((u - u_{\mathrm{sat}})/T_t = +20\) has the wrong sign and would wind the integrator further. The tracking time 0.5 is not itself the rate.",
          loopfig, loop_alt)
    b.mc(2,
         r"After the error changes sign, a wound-up integrator",
         ["releases the actuator immediately, because the error changed sign",
          "keeps the actuator saturated until the accumulated state has unwound",
          "resets to zero in one sample, with no extra logic",
          "has no effect, because saturation only matters while the error is growing"], 1,
         r"The integrator state is still large, so the command stays beyond the limit until that state comes back down. A sign change in the error starts the unwinding; it does not finish it. Nothing in the plain PID equation resets the state. Saturation matters on the way back as well as on the way out, which is why the overshoot gets worse.",
         step, step_alt)
    b.num(2,
          r"A common tracking time is \(T_t = \sqrt{\tau_i \tau_d}\). With \(\tau_i = 4\) s and \(\tau_d = 0.64\) s, that tracking time is",
          tt, "s",
          r"\(\sqrt{4 \cdot 0.64} = \sqrt{2.56} = " + show(tt) + r"\) s. The integral time 4 s is one of the inputs, not the geometric mean. The product \(4\cdot 0.64 = 2.56\) still needs the square root.",
          loopfig, loop_alt)

    b.mc(3,
         r"Clamping (conditional integration) stops the integrator when",
         ["the error is zero, whether or not the actuator is saturated",
          "the command is below the limit and could still grow",
          "the actuator is saturated and the error has the sign that would push the command further into the limit",
          "the derivative term is nonzero"], 2,
         r"Clamping freezes the integrator only in the direction that makes saturation worse. If the error reverses, integration is allowed again so the state can unwind. Stopping at zero error does nothing useful, because the integrand is already zero. Stopping while the command is inside the limits disables integral action during normal operation. The derivative term is not the signal being clamped.",
         cmd, cmd_alt)
    b.num(3,
          r"With \(K_i = 2.5\) and error 1.2, the integrator would grow at this rate if it were not clamped:",
          would, "1",
          r"The unsaturated rate is \(K_i e = 2.5\cdot 1.2 = " + show(would) + r"\). Clamping replaces that rate by zero while the saturation condition holds. The error 1.2 alone is not a rate. The gain 2.5 alone is the rate for a unit error.",
          cmd, cmd_alt)
    b.num(3,
          r"The command calls for 9 and the actuator can deliver 4. The fraction of the requested command that actually reaches the plant is",
          frac, "1",
          r"The plant sees \(4/9 = " + show(frac) + r"\) of the request. The excess fraction \((9-4)/9 = 5/9\) is the part that was cut off, not the part that got through. The limit 4 is an absolute command, not a fraction.",
          cmd, cmd_alt)

    b.num(4,
          r"Back-calculation uses \(T_t = 0.2\) s. The command is 15 and the limit is 8. The rate added to the integrator is",
          unwind, "1",
          r"\((u_{\mathrm{sat}} - u)/T_t = (8-15)/0.2 = " + show(unwind) + r"\). The excess \(15-8 = 7\) is the numerator before dividing by \(T_t\), and with the opposite sign. The tracking time 0.2 is not the rate.",
          loopfig, loop_alt, ["integral-action"])
    b.mc(4,
         r"Anti-windup logic",
         ["replaces the need for a stable feedback loop",
          "cancels plant uncertainty",
          "removes the proportional term during saturation",
          "handles the intervals when the actuator is saturated, and does not stabilize an otherwise unstable loop"], 3,
         r"Clamping and back-calculation repair the integrator while the command is beyond the limit. The loop still has to be stable when the actuator is inside its range. Uncertainty is a plant-model question. The proportional term keeps running; it is the integrator that is frozen or rewound.",
         step, step_alt, ["mpc"])
    b.num(4,
          r"Clamping is active for 4 seconds, with \(K_i = 6\) and error 0.5. The integrator growth that the clamp prevents is",
          prevented, "1",
          r"Without the clamp the state would grow by \(6\cdot 0.5\cdot 4 = " + show(prevented) + r"\). The rate \(K_i e = 3\) is the growth per second, not the growth over 4 seconds. The duration 4 s is not a change in the integrator state.",
          step, step_alt, ["pid-impl"])
    b.save()


def expl_windup():
    fig = plot(lambda t: 4.0 if 0.6 < t < 3.2 else (6 * t if t <= 0.6 else 4.0 - 1.5 * (t - 3.2)),
               0, 5, "t", "u", "saturation and release")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A command that flattens at a limit and later comes back down.",
         "body_md": r"""A PI or PID controller tells the actuator what to do, and the actuator has a limit. Once the command sits beyond that limit, the plant input is stuck, but the error is often still large. The integrator does not know about the limit. It keeps adding, so its state climbs far above the value that corresponds to the actuator's actual output. That climb is windup.

When the output finally reaches the reference and the error changes sign, the integrator is still huge. The command stays saturated in the old direction until the state has integrated back down. The result is a large overshoot that the linear tuning never predicted. Anti-windup stops the state from running away, or drags it back toward the limit, during the saturated interval."""},
        {"heading": "Key equations", "body_md": r"""If the error is constant while the actuator is saturated, the integrator grows by \(K_i\, e\, t\).

Clamping refuses that growth when the actuator is at a stop and the error has the sign that would drive the command further into the stop. When the error reverses, integration is allowed again.

Back-calculation adds an extra input to the integrator,
\[
\frac{u_{\mathrm{sat}} - u}{T_t},
\]
where \(u\) is the unsaturated command and \(T_t\) is a tracking time. One common choice is \(T_t = \sqrt{\tau_i \tau_d}\). The added term is negative when \(u\) is above the limit, so the state unwinds instead of climbing."""},
        {"heading": "Worked example", "body_md": r"""Take \(K_i = 1.7\) and an error of 3.5 that lasts 2.2 s while the valve is hard against its stop. The integrator would grow by \(1.7 \cdot 3.5 \cdot 2.2 = 13.09\) if nothing stopped it. Separately, suppose the unsaturated command is 22, the valve can deliver 7, and the tracking time is 0.3 s. Back-calculation then adds \((7 - 22)/0.3 = -50\) to the integrator input, a strong unwind. The two numbers describe the same saturated moment: how fast the state would have run away, and how hard the extra feedback pulls it back."""},
        {"heading": "Common pitfalls", "body_md": r"""The back-calculation sign is \(u_{\mathrm{sat}} - u\), not \(u - u_{\mathrm{sat}}\). The second of those winds the integrator further into the stop. Clamping is not "freeze the integrator whenever the error is nonzero"; it freezes only the direction that deepens saturation. And neither trick stabilizes a loop that is unstable inside the linear range. They only repair the saturated intervals. A tracking time that is very long barely unwinds. A tracking time that is very short can chatter as the command enters and leaves the limit."""},
        {"heading": "Where this leads", "body_md": r"""State feedback with an extra integrator has the same state and the same saturation problem; the anti-windup path has to be wired into that augmented controller too. Model-predictive control takes the actuator limit as a constraint inside the optimization, so the command it issues is already something the actuator can produce."""},
    ]
    save_explainer("windup", "Integrator windup and anti-windup", sections)
    return words(sections)


def lint():
    banned = re.compile(
        r"niknejad|åström|aström|astrom|murray|feedback systems|ziegler|nichols|\breader\b|§",
        re.I,
    )
    skills = [
        "feedforward", "freq-resp-lti", "gen-gain-phase", "linearization", "lti-stability",
        "perf-specs-freq", "pid-impl", "pid-tuning", "realization", "uncertainty", "windup",
    ]
    problems = []
    import json
    from collections import Counter
    for sid in skills:
        bank = json.load(open(os.path.join(BANK, f"{sid}.json"), encoding="utf-8"))
        exp = json.load(open(os.path.join(EXP, f"{sid}.json"), encoding="utf-8"))
        nfig = 0
        idxs = []
        for q in bank["questions"]:
            blob = json.dumps(q, ensure_ascii=False)
            if banned.search(blob):
                problems.append(f"{q['id']} banned wording")
            if q.get("figure"):
                nfig += 1
            if q["type"] == "mc":
                idxs.append(q["correct_index"])
        if nfig < 9:
            problems.append(f"{sid} only {nfig} figures")
        if len(idxs) % 4 == 0 and idxs:
            c = Counter(idxs)
            if len(c) != 4 or len(set(c.values())) != 1:
                problems.append(f"{sid} MC positions {dict(c)}")
        wc = words(exp["sections"])
        if not (250 <= wc <= 500):
            problems.append(f"{sid} explainer words {wc}")
        blob = json.dumps(exp, ensure_ascii=False)
        if banned.search(re.sub(r"<svg[\s\S]*?</svg>", "", blob)):
            problems.append(f"{sid} explainer banned wording")
        print(f"{sid}: questions {len(bank['questions'])}, figures {nfig}, MC idx {idxs}, explainer words {wc}")
    if problems:
        print("LINT FAIL")
        for p in problems:
            print(" ", p)
        sys.exit(1)
    print("lint ok")


def main():
    bank_feedforward()
    bank_freq_resp()
    bank_gen_gain()
    bank_linearization()
    bank_lti_stability()
    bank_perf()
    bank_pid_impl()
    bank_pid_tuning()
    bank_realization()
    bank_uncertainty()
    bank_windup()
    print(
        "words",
        expl_feedforward(),
        expl_freq_resp(),
        expl_gen_gain(),
        expl_linearization(),
        expl_lti_stability(),
        expl_perf(),
        expl_pid_impl(),
        expl_pid_tuning(),
        expl_realization(),
        expl_uncertainty(),
        expl_windup(),
    )
    lint()


if __name__ == "__main__":
    main()
