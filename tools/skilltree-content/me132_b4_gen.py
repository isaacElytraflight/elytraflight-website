#!/usr/bin/env python3
"""Generate ME 132 batch B4 banks and explainers.

Skills: discrete-time, eig-modes, limit-cycles, nyquist, pid, sensitivity, ss-to-tf, step-specs
Closed-form answers live here. skilltree/verify_me132_b4.py recomputes them
by signal equations, RK4, eigenvalue routines, or matrix exponentials.
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from templates import (
    block_diagram, bode, matrix_fig, nyquist, plot, splane, step_response,
)

from banklib import BANK, EXP, Bank, save_explainer, words


def second_order_step(zeta, wn, goal, t_end):
    """Second-order step response for zeta < 1 (underdamped)."""
    if zeta >= 1:
        raise ValueError("use this only for underdamped")
    wd = wn * math.sqrt(1 - zeta**2)
    def y(t):
        if t <= 0:
            return 0.0
        return goal * (1 - math.exp(-zeta * wn * t) * (
            math.cos(wd * t) + (zeta / math.sqrt(1 - zeta**2)) * math.sin(wd * t)
        ))
    return plot(y, 0, t_end, "t", "y", "second-order step", zero=False)


def overshoot_pct(zeta):
    return 100 * math.exp(-math.pi * zeta / math.sqrt(1 - zeta**2))


def time_to_peak(zeta, wn):
    wd = wn * math.sqrt(1 - zeta**2)
    return math.pi / wd


def settling_time_2pct(zeta, wn):
    return 4 / (zeta * wn)


def rise_time_approx(zeta, wn):
    """10% to 90% rise time approximation for second-order."""
    wd = wn * math.sqrt(1 - zeta**2)
    return (math.pi - math.atan2(math.sqrt(1 - zeta**2), zeta)) / wd


def unit_circle_fig(title, poles=None, show_unit=True):
    """z-plane with unit circle for discrete-time stability."""
    from figlib import b2b_svg, b2b_circle, b2b_arrow, b2b_text, b2b_line
    w, h = 280, 240
    cx, cy = 140, 120
    r = 80
    body = ""
    if show_unit:
        body += f'<circle cx="{cx}" cy="{cy}" r="{r}" stroke-dasharray="4 3"/>'
    body += b2b_arrow(30, cy, 250, cy)
    body += b2b_arrow(cx, 210, cx, 30)
    body += b2b_text(245, cy + 16, "Re", anchor="end", size=11)
    body += b2b_text(cx + 8, 28, "Im", anchor="start", size=11)
    body += b2b_text(cx + r, cy + 14, "1", size=10)
    if poles:
        for pr, pi in poles:
            px = cx + r * pr
            py = cy - r * pi
            body += b2b_line(px - 5, py - 5, px + 5, py + 5, sw=1.6)
            body += b2b_line(px - 5, py + 5, px + 5, py - 5, sw=1.6)
    return b2b_svg(w, h, body, title)


def limit_cycle_fig(title):
    """Phase portrait with a limit cycle."""
    from figlib import b2b_svg, b2b_circle, b2b_arrow, b2b_text, b2b_poly
    w, h = 280, 240
    cx, cy = 140, 120
    body = b2b_arrow(30, cy, 250, cy)
    body += b2b_arrow(cx, 210, cx, 30)
    body += b2b_text(245, cy + 16, r"x₁", anchor="end", size=11)
    body += b2b_text(cx + 8, 28, r"x₂", anchor="start", size=11)
    body += f'<circle cx="{cx}" cy="{cy}" r="60" stroke-dasharray="4 3"/>'
    pts = []
    for i in range(37):
        th = 2 * math.pi * i / 36
        r_sp = 30 + 25 * (1 - math.exp(-th))
        pts.append((cx + r_sp * math.cos(th), cy - r_sp * math.sin(th)))
    body += b2b_poly(pts, sw=1.8)
    return b2b_svg(w, h, body, title)


def pid_block(kp, ki, kd, title):
    """PID controller block with plant."""
    return block_diagram([f"PID"], title, feedback="1",
                        input_label="r", output_label="y", error_label="e")


def bank_step_specs():
    b = Bank("step-specs")
    step_fig = "A curve that rises, overshoots, and then settles."
    pole_fig = "Two pole marks in the left half-plane."

    z1, wn1 = 0.5, 4.0
    z2, wn2 = 0.4, 5.0
    z3, wn3 = 0.6, 3.0

    b.mc(1,
         r"Step-response specifications include rise time, overshoot, settling time, and steady-state error. Rise time is typically measured",
         ["from 10% to 90% of the final value",
          "from 0% to 100% of the final value",
          "from the peak to the final value",
          "from 50% to 100% of the final value"], 0,
         r"The 10% to 90% rise time avoids the slow initial start and the overshoot. The 0% to 100% definition is ambiguous when there is overshoot. The peak-to-final definition is settling, not rise time. The 50% to 100% definition misses the early part of the rise.",
         second_order_step(z1, wn1, 1, 4),
         step_fig)
    b.num(1,
          r"A second-order system has \(\zeta = 0.5\) and \(\omega_n = 4\) rad/s. The percent overshoot is",
          overshoot_pct(z1), "%",
          r"Only \(\zeta\) enters the overshoot formula, so \(\omega_n = 4\) does not change the percentage. For \(\zeta = 0.5\), \(\sqrt{1-\zeta^2} = 0.866\) and the exponent is \(-\pi \times 0.5/0.866\), which makes \(100\) times that exponential equal \(16.3\). Reporting \(0.5\) confuses the damping ratio with the percentage. Reporting \(0.163\) forgot to turn the fraction into a percent.",
          second_order_step(z1, wn1, 1, 4),
          step_fig, version=2)
    b.num(1,
          r"Same system, \(\zeta = 0.5\), \(\omega_n = 4\). The approximate 2% settling time is",
          settling_time_2pct(z1, wn1), "s",
          r"A 2% envelope is about four time constants, and the time constant here is \(1/(\zeta\omega_n)\). The product \(\zeta\omega_n = 0.5 \times 4 = 2\), so the estimate is \(4/2 = 2\) s. Swapping in a factor of 5 is the tighter 1% estimate. Dividing 4 by \(\omega_n\) alone ignores damping and returns 1 s.",
          second_order_step(z1, wn1, 1, 4),
          step_fig, version=2)

    b.num(2,
          r"For \(\zeta = 0.4\) and \(\omega_n = 5\) rad/s, the time to the first peak is",
          time_to_peak(z2, wn2), "s",
          r"The first peak is half a cycle of the damped ringing: \(t_p = \pi/\omega_d\). With \(\zeta = 0.4\), \(\omega_d = 5 \times 0.917 = 4.58\), and \(\pi/4.58 = 0.685\) s. Dividing by the natural frequency instead gives \(\pi/5 = 0.628\) s, which is half a period of the undamped system.",
          second_order_step(z2, wn2, 1, 3),
          step_fig, version=3)
    b.num(2,
          r"Same system, \(\zeta = 0.4\), \(\omega_n = 5\). The damped frequency is",
          wn2 * math.sqrt(1 - z2**2), "rad/s",
          r"\(\omega_d = \omega_n\sqrt{1-\zeta^2} = 5 \times 0.917 = 4.58\) rad/s. The natural frequency 5 is not the damped frequency. The real part \(-2\) is the decay rate, not the ringing rate.",
          splane([(-z2 * wn2, wn2 * math.sqrt(1 - z2**2)), (-z2 * wn2, -wn2 * math.sqrt(1 - z2**2))], [], "closed-loop poles"),
          pole_fig)
    b.mc(2,
         r"A specification calls for overshoot below 10%. The damping ratio must be",
         ["below 0.5",
          "above 0.6",
          "exactly 0.5",
          "above 1.0"], 1,
         r"The overshoot formula \(M_p = 100 e^{-\pi\zeta/\sqrt{1-\zeta^2}}\) gives 9.5% at \(\zeta = 0.6\). Higher damping gives lower overshoot. Below 0.5 gives more than 16%. Exactly 0.5 gives 16.3%. Above 1.0 is overdamped with no overshoot but is stricter than needed.",
         second_order_step(0.6, 4, 1, 4),
         step_fig)

    b.num(3,
          r"A system has \(\zeta = 0.6\) and \(\omega_n = 3\) rad/s. The percent overshoot is",
          overshoot_pct(z3), "%",
          r"Overshoot depends on damping alone: \(100\exp(-\pi\zeta/\sqrt{1-\zeta^2})\). With \(\zeta = 0.6\), \(\sqrt{1-0.36} = 0.8\), and \(100\exp(-\pi\times 0.6/0.8) = 9.48\%\). The natural frequency 3 never enters. Putting \(\omega_n\) into that exponent mixes a time scale into a percentage.",
          second_order_step(z3, wn3, 1, 5),
          step_fig, version=2)
    b.num(3,
          r"Same system. The approximate 2% settling time is",
          settling_time_2pct(z3, wn3), "s",
          r"The settling time is \(4/(\zeta\omega_n) = 4/(0.6 \times 3) = 2.22\) s. Using 5 instead of 4 gives 2.78 s. Using \(\omega_n\) alone gives 1.33 s.",
          second_order_step(z3, wn3, 1, 5),
          step_fig)
    b.mc(3,
         r"Steady-state error to a unit step for a type-0 system with DC gain \(K\) is",
         [r"\(1/K\)",
          r"\(K/(1+K)\)",
          r"\(1/(1+K)\)",
          r"zero"], 2,
         r"For a type-0 system (no free integrator), the DC error is \(1/(1+K)\). Type-1 and higher systems have zero steady-state error to a step. \(1/K\) is the error to a ramp for type-1. \(K/(1+K)\) is the closed-loop gain, not the error.",
         block_diagram(["K"], "DC error", feedback="1", input_label="r", output_label="y"),
         "A forward block with unity feedback.")

    b.num(4,
          r"Design targets: 5% settling time under 1 s with \(\zeta = 0.45\) (about 20% overshoot). The minimum \(\omega_n\) is",
          3 / (0.45 * 1.0), "rad/s",
          r"The 5% settling rule is \(t_s \approx 3/(\zeta\omega_n)\). With \(t_s = 1\) and \(\zeta = 0.45\), \(\omega_n = 3/(0.45 \times 1) = 6.67\) rad/s. The 2% rule uses 4 in the numerator and would ask for 8.89.",
          second_order_step(0.45, 4, 1, 3),
          step_fig, ["perf-specs-freq"], version=2)
    b.num(4,
          r"A closed-loop has poles at \(-3 \pm j4\). The natural frequency is",
          5.0, "rad/s",
          r"\(\omega_n = \sqrt{3^2 + 4^2} = 5\) rad/s. The real part 3 is not the natural frequency. The imaginary part 4 is the damped frequency.",
          splane([(-3, 4), (-3, -4)], [], "closed-loop poles"),
          pole_fig, ["perf-specs-freq"])
    b.mc(4,
         r"A designer picks \(\zeta \approx 0.7\) as a step-response target. The step response of that loop",
         ["never overshoots",
          "overshoots by about 50%",
          "oscillates forever",
          "overshoots by about 5% and settles quickly"], 3,
         r"At \(\zeta \approx 0.7\) the overshoot formula returns roughly 5%, and the transient still rings once before it dies. A loop that never overshoots would need \(\zeta \ge 1\). A 50% overshoot belongs near \(\zeta \approx 0.2\). A response that never stops oscillating is the undamped case \(\zeta = 0\).",
          second_order_step(0.7, 3, 1, 4), step_fig, ["perf-specs-freq"], version=2)
    b.save()


def bank_pid():
    b = Bank("pid")
    loop = "A PID controller and plant in a feedback loop."
    step_fig = "A curve that rises and settles."

    Kp1, Ki1 = 4.0, 2.0
    Kp2, Kd2 = 3.0, 0.5

    b.mc(1,
         r"A PID controller has three terms: proportional, integral, and derivative. The integral term",
         ["eliminates steady-state error to a step",
          "speeds up the transient response",
          "adds damping",
          "has no effect at low frequency"], 0,
         r"The integral term builds up whenever an error persists, driving the steady error to zero for a step input. The derivative term speeds up response and adds damping. The proportional term alone cannot eliminate steady error.",
         pid_block(1, 1, 1, "PID controller"),
         loop)
    b.num(1,
          r"A PI controller has \(K_p = 4\) and \(K_i = 2\). The transfer function is \(K_p + K_i/s\). At \(s = 1\), the magnitude is",
          abs(Kp1 + Ki1 / 1.0), "1",
          r"At the real point \(s = 1\), \(C(1) = 4 + 2/1 = 6\), so the magnitude is 6. Evaluating \(K_p + K_i/(j\omega)\) at \(\omega = 1\) instead gives \(4 - 2j\), whose magnitude is about 4.47. That is a frequency-response number, not \(C(1)\).",
          pid_block(Kp1, Ki1, 0, "PI controller"),
          loop, version=2)
    b.mc(1,
         r"Increasing the proportional gain \(K_p\) in a stable loop",
         ["increases the loop gain and reduces steady error",
          "has no effect on stability",
          "always makes the loop unstable",
          "eliminates steady error entirely"], 0,
         r"Higher \(K_p\) raises the loop gain, which reduces the steady error \(1/(1+L)\). It can eventually destabilize the loop if raised too far. It does not eliminate error without integral action.",
         pid_block(4, 0, 0, "P controller"),
         loop)

    b.mc(2,
         r"The derivative term in a PID controller provides",
         ["phase lead at high frequencies",
          "infinite gain at DC",
          "phase lag at all frequencies",
          "zero gain at high frequencies"], 0,
         r"The derivative \(K_d s\) has magnitude growing with frequency and adds up to +90° phase. This phase lead helps compensate lag from the plant. Integral provides phase lag and infinite gain at DC. The derivative has increasing gain, not zero, at high frequency.",
         pid_block(1, 0, 1, "PD controller"),
         loop)
    b.num(2,
          r"A PD controller has \(K_p = 3\) and \(K_d = 0.5\). The zero is at \(s = \)",
          -Kp2 / Kd2, "rad/s",
          r"The PD transfer function \(K_d(s + K_p/K_d) = 0.5(s + 6)\) has a zero at \(-6\). The zero location is \(-K_p/K_d = -6\). The gain ratio \(K_d/K_p\) is the reciprocal.",
          splane([], [(-Kp2 / Kd2, 0)], "PD zero"),
          "A zero mark on the negative real axis.")
    b.num(2,
          r"Same PD controller, \(K_p = 3\), \(K_d = 0.5\). At \(\omega = 10\) rad/s, the magnitude is approximately",
          math.sqrt(Kp2**2 + (Kd2 * 10)**2), "1",
          r"At \(s = j10\), \(C(j10) = 3 + 0.5 \times j10 = 3 + 5j\). The magnitude is \(\sqrt{9 + 25} = 5.83\). The derivative term dominates at high frequency.",
          pid_block(Kp2, 0, Kd2, "PD magnitude"),
          loop)

    Kp3, Ki3, Kd3 = 5.0, 10.0, 0.2
    b.num(3,
          r"A full PID has \(K_p = 5\), \(K_i = 10\), \(K_d = 0.2\). The number of zeros in the controller transfer function is",
          2.0, "1",
          r"The PID transfer function \((K_d s^2 + K_p s + K_i)/s\) has two zeros (roots of the numerator quadratic) and one pole at the origin. The integral gives the pole. The proportional, integral, and derivative terms together give the second-order numerator.",
          pid_block(Kp3, Ki3, Kd3, "PID zeros"),
          loop)
    b.mc(3,
         r"Integral windup occurs when",
         ["the integrator accumulates error while the actuator is saturated",
          "the derivative gain is too high",
          "the proportional gain is zero",
          "the plant has no integrator"], 0,
         r"When the actuator saturates, the control signal cannot increase further, but the integral of error keeps growing. When the setpoint changes or saturation ends, the large integral causes overshoot. Anti-windup techniques limit the integrator during saturation.",
         pid_block(1, 1, 0, "windup"),
         loop)
    b.num(3,
          r"A PI controller with \(K_p = 2\) and \(K_i = 4\) on a plant with DC gain 5. The closed-loop DC gain is",
          1.0, "1",
          r"The integral term gives infinite loop gain at DC, so the closed-loop gain is exactly 1. The steady-state error to a step is zero. Without integral, the DC gain would be \(L/(1+L)\), which is less than 1.",
          pid_block(2, 4, 0, "PI DC gain"),
          loop)

    b.num(4,
          r"PID tuning from a step test: plant gain \(K = 3\), time constant \(\tau = 2\) s, apparent delay \(L = 0.3\) s. The reaction-curve rule \(K_p \approx 1.2\,\tau/(KL)\) gives",
          1.2 * 2 / (3 * 0.3), "1",
          r"\(K_p = 1.2 \tau / (K L) = 1.2 \times 2 / (3 \times 0.3) = 2.67\). Writing the fraction upside down, \(1.2 L/(K\tau)\), gives about 0.06 and is not this rule. The number is a starting gain, not a finished design.",
          step_response("Ziegler-Nichols step", tau=2, goal=3),
          step_fig, ["pid-tuning"], version=2)
    b.mc(4,
         r"Feedforward combined with PID",
         ["cannot improve tracking",
          "acts before the feedback loop sees an error",
          "replaces the feedback loop",
          "has no effect on step response"], 1,
         r"Feedforward uses the reference directly to generate part of the control signal, reducing the error the feedback loop must correct. It complements, not replaces, feedback. It can significantly improve step response by reducing the initial error.",
          pid_block(1, 1, 1, "feedforward + PID"), loop, ["pid-impl"])
    b.num(4,
          r"A PI controller with \(K_p = 6\), \(K_i = 12\). The integral time constant \(\tau_i = K_p/K_i\) is",
          0.5, "s",
          r"\(\tau_i = K_p/K_i = 6/12 = 0.5\) s. This is the time for the integral term alone to ramp up to the proportional term's value. The reciprocal 2 is the integral frequency in rad/s.",
          pid_block(6, 12, 0, "PI time constant"),
          loop, ["pid-tuning"])
    b.save()


def bank_sensitivity():
    b = Bank("sensitivity")
    loop = "A forward block and a return path."
    nyq_fig = "A curve in the complex plane with the critical point marked."

    L1 = 8.0
    L2 = 15.0

    b.mc(1,
         r"The sensitivity function \(S(s)\) gives the transfer function from",
         ["disturbance at the output to the output",
          "reference to output",
          "reference to the control signal",
          "noise to control signal"], 0,
         r"With the definitions used here, \(S = 1/(1+L)\) multiplies a disturbance added at the output. Reference to output is the complementary sensitivity \(T\). Reference to the control signal is the control sensitivity, not \(S\).",
         block_diagram(["G"], "sensitivity", feedback="1", input_label="r", output_label="y", disturbance="d"),
         "A loop with a disturbance added at the output.", version=2)
    b.num(1,
          r"A loop has loop gain \(L = 8\). The sensitivity \(S = 1/(1+L)\) is",
          1 / (1 + L1), "1",
          r"\(S = 1/(1+8) = 1/9 = 0.111\). The complementary sensitivity \(T = 8/9\) is one minus \(S\). The loop gain 8 is not the sensitivity.",
          block_diagram(["8"], "S calculation", feedback="1", input_label="r", output_label="y"),
          loop)
    b.num(1,
          r"Same loop, \(L = 8\). The complementary sensitivity \(T\) is",
          L1 / (1 + L1), "1",
          r"\(T = L/(1+L) = 8/9 = 0.889\). Check: \(T + S = 8/9 + 1/9 = 1\). The sensitivity 0.111 is not the complementary sensitivity.",
          block_diagram(["8"], "T calculation", feedback="1", input_label="r", output_label="y"),
          loop)

    b.mc(2,
         r"For \(S = 1/(1+L)\) and \(T = L/(1+L)\), the identity \(S + T = 1\) holds",
         ["only when the closed loop is stable",
          r"at every frequency where \(L\) is defined",
          "only at DC",
          "only when the open loop is unstable"], 1,
         r"Adding the definitions gives \(1/(1+L) + L/(1+L) = 1\) wherever \(L\) is defined, stable or not. Unity feedback is a separate fact: it makes \(T\) equal the reference-to-output map. A non-unity sensor changes that map, not this algebra. The identity is not limited to DC.",
         block_diagram(["G"], "S + T", feedback="1", input_label="r", output_label="y"),
         loop, version=2)
    b.num(2,
          r"A loop has \(L = 15\). A unit disturbance at the output is attenuated to",
          1 / (1 + L2), "1",
          r"The disturbance is multiplied by \(S = 1/16 = 0.0625\). A larger loop gain gives more attenuation. The complementary sensitivity \(15/16\) is what the reference sees.",
          block_diagram(["15"], "disturbance attenuation", feedback="1", input_label="r", output_label="y", disturbance="d"),
          "A loop with a disturbance at the output.")
    b.mc(2,
         r"At frequencies where \(|L(j\omega)|\) is large,",
         [r"\(|S|\) is small and \(|T| \approx 1\)",
          r"\(|S| \approx 1\) and \(|T|\) is small",
          r"\(|S| = |T| = 0.5\)",
          r"\(|S|\) and \(|T|\) are both large"], 0,
         r"When \(|L| \gg 1\), \(S \approx 1/L \to 0\) and \(T \approx L/L = 1\). This is the low-frequency region for most loops. At high frequency where \(|L| \ll 1\), \(S \approx 1\) and \(T \approx L \to 0\).",
         block_diagram(["G(s)"], "frequency behavior", feedback="1", input_label="r", output_label="y"),
         loop)

    Ms = 2.0
    b.num(3,
          r"A design limits the peak sensitivity \(M_s = \max |S(j\omega)|\) to 2. The minimum distance from the Nyquist curve to \(-1\) is",
          1 / Ms, "1",
          r"The peak sensitivity is the reciprocal of the closest approach to \(-1\). If \(M_s = 2\), the curve comes within \(1/2 = 0.5\) of the critical point. A larger \(M_s\) means the curve comes closer to instability.",
          nyquist([(0, 0), (-0.6, 0.4), (-0.8, 0.1), (-0.5, -0.3), (0, 0)], "Nyquist approach to -1"),
          nyq_fig)
    b.mc(3,
         r"The waterbed effect says",
         ["reducing \(|S|\) at one frequency must increase it elsewhere",
          "\(|S|\) can be made small at all frequencies",
          "\(|T|\) is always smaller than \(|S|\)",
          "peak sensitivity has no lower bound"], 0,
         r"For a stable plant with at least one right-half plane zero or time delay, the area under \(\ln|S|\) is fixed. Pushing \(|S|\) down at low frequency pushes it up at high frequency. There is no free lunch in sensitivity.",
         block_diagram(["G(s)"], "waterbed", feedback="C(s)", input_label="r", output_label="y"),
         loop)
    b.num(3,
          r"A loop has \(L(0) = 20\). The steady-state error to a unit step reference is",
          1 / 21, "1",
          r"At DC, \(S(0) = 1/(1+20) = 1/21 = 0.048\). The error is \(S \cdot r = 0.048 \times 1\). The complementary sensitivity \(20/21\) is what the output reaches.",
          block_diagram(["20"], "DC error", feedback="1", input_label="r", output_label="y"),
          loop)

    b.num(4,
          r"At the phase crossover, \(|L| = 0.1\). The gain margin in dB is",
          20 * math.log10(1 / 0.1), "dB",
          r"Gain margin is read where the phase is \(-180^\circ\), not at the gain crossover where \(|L| = 1\). Here \(|L| = 0.1\), so the gain can increase by a factor of 10 before that crossing reaches \(-1\). In decibels that factor is \(20\log_{10}(10) = 20\).",
          nyquist([(2, 0), (0.8, -0.9), (0.05, -0.45), (-0.55, 0)], "phase crossover"),
          "A Nyquist curve that crosses the negative real axis.", ["robust-stability"], version=2)
    b.mc(4,
         r"The Gang of Four in feedback analysis consists of",
         [r"\(S\), \(T\), \(PS\), and \(CS\)",
          r"\(P\), \(C\), \(S\), and \(T\)",
          r"\(L\), \(G\), \(H\), and \(1+L\)",
          r"four different controllers"], 0,
         r"The Gang of Four are the four closed-loop transfer functions: \(S\) (sensitivity), \(T\) (complementary sensitivity), \(PS\) (output to disturbance), and \(CS\) (control sensitivity). They fully characterize the closed-loop behavior.",
          block_diagram(["C", "P"], "Gang of Four", feedback="1", input_label="r", output_label="y"), loop, ["robust-perf"])
    b.num(4,
          r"A specification requires \(|S(j\omega)| < 0.1\) at \(\omega = 0.1\) rad/s. The minimum \(|L(j0.1)|\) is",
          9.0, "1",
          r"From \(|S| = 1/|1+L| < 0.1\), we need \(|1+L| > 10\), so approximately \(|L| > 9\). The exact bound depends on the phase of \(L\), but for real \(L > 0\), \(L > 9\) suffices.",
          block_diagram(["L"], "low-frequency requirement", feedback="1", input_label="r", output_label="y"),
          loop, ["perf-specs-freq"])
    b.save()


def bank_nyquist():
    b = Bank("nyquist")
    nyq_fig = "A curve in the complex plane with the critical point marked."
    pole_fig = "Pole marks in the complex plane."

    b.mc(1,
         r"The Nyquist criterion determines closed-loop stability by",
         ["counting encirclements of \(-1\) by \(L(j\omega)\)",
          "checking if \(|L(j\omega)| < 1\) at all frequencies",
          "finding where \(L(j\omega) = 0\)",
          "measuring the phase margin only"], 0,
         r"The Nyquist plot is \(L(j\omega)\) in the complex plane. The number of encirclements of \(-1\) equals the difference between closed-loop and open-loop RHP poles. Checking \(|L| < 1\) everywhere is too restrictive. \(L = 0\) is not the critical point.",
         nyquist([(3, 0), (1, -2), (-0.5, -1), (-0.3, 0), (-0.5, 1), (1, 2), (3, 0)], "Nyquist curve"),
         nyq_fig)
    b.mc(1,
         r"A stable open-loop system has the Nyquist curve that does not encircle \(-1\). The closed-loop is",
         ["stable with zero RHP poles",
          "unstable with one RHP pole",
          "marginally stable",
          "unstable with two RHP poles"], 0,
         r"For a stable open-loop (no RHP poles), \(Z = N + P = 0 + 0 = 0\). The closed-loop is stable. If the curve encircles \(-1\) once clockwise, there would be one closed-loop RHP pole.",
          nyquist([(2, 0), (1, -1), (0, -0.5), (-0.3, 0), (0, 0.5), (1, 1), (2, 0)], "stable Nyquist"),
          nyq_fig)
    b.mc(1,
         r"At the gain crossover frequency, \(|L(j\omega_c)| = 1\). On the Nyquist plot, this corresponds to",
         ["the curve crossing the unit circle centered at the origin",
          "the curve crossing the real axis",
          "the curve crossing \(-1\)",
          "the curve at its maximum imaginary part"], 0,
         r"The gain crossover is where the magnitude of \(L\) is 1, which is the unit circle on the Nyquist plot. The phase crossover is where the curve crosses the negative real axis. Crossing \(-1\) would mean instability is imminent.",
         nyquist([(1.5, 0), (0.8, -0.6), (0, -1), (-0.5, -0.8), (-0.7, 0)], "gain crossover"),
         nyq_fig)

    b.num(2,
          r"The Nyquist curve crosses the negative real axis at \(-0.5\). The gain margin is",
          2.0, "1",
          r"Gain margin is how much the loop gain can increase before the crossing reaches \(-1\). If the crossing is at \(-0.5\), the gain can double: \(GM = 1/0.5 = 2\). In dB, that is about 6 dB.",
          nyquist([(2, 0), (1, -1), (0, -1), (-0.5, 0), (0, 1), (1, 1), (2, 0)], "gain margin"),
          nyq_fig)
    b.num(2,
          r"Same curve, crossing at \(-0.5\). The gain margin in dB is",
          20 * math.log10(2), "dB",
          r"GM in dB is \(20 \log_{10}(2) = 6.02\) dB. The factor of 2 corresponds to about 6 dB. A crossing at \(-0.25\) would give 12 dB.",
          nyquist([(2, 0), (1, -1), (0, -1), (-0.5, 0), (0, 1), (1, 1), (2, 0)], "GM in dB"),
          nyq_fig)
    b.mc(2,
         r"Phase margin is measured at",
         ["the gain crossover frequency where \(|L| = 1\)",
          "the phase crossover frequency where the phase is \(-180°\)",
          "DC where \(L\) is largest",
          "the frequency of maximum \(|L|\)"], 0,
         r"Phase margin is how much additional phase lag can be added before instability. At \(|L| = 1\), the distance from \(-180°\) to the actual phase is the phase margin. Gain margin is measured at the phase crossover.",
         nyquist([(1, 0), (0.7, -0.7), (0, -1)], "phase margin"),
         nyq_fig)

    b.num(3,
          r"A loop has phase margin 45°. At the gain crossover, the phase of \(L(j\omega_c)\) is",
          -135.0, "deg",
          r"Phase margin is \(180° + \angle L\). If PM = 45°, then \(\angle L = -180° + 45° = -135°\). The phase at crossover is not \(-45°\); that would be 135° of margin.",
          nyquist([(2, 0), (1, -1), (0, -1.5)], "phase at crossover"),
          nyq_fig)
    b.mc(3,
         r"For a stable open-loop with one clockwise encirclement of \(-1\), the closed-loop has",
         ["zero RHP poles",
          "one RHP pole",
          "two RHP poles",
          "the same number of RHP poles as the open-loop"], 1,
         r"Nyquist formula: \(Z = N + P\). With \(P = 0\) (stable open-loop) and \(N = 1\) (one clockwise encirclement), \(Z = 1\). The closed-loop has one unstable pole.",
         nyquist([(2, 0), (0, -2), (-1.5, -0.5), (-1, 0), (-1.5, 0.5), (0, 2), (2, 0)], "one encirclement"),
         nyq_fig)
    b.num(3,
          r"A loop has gain margin 4 (factor) and the plant gain increases by a factor of 3. The new gain margin is",
          4.0 / 3, "1",
          r"The new loop gain is 3 times the old. The crossing point moves closer to \(-1\). The new margin is \(4/3 = 1.33\). The system is still stable but with less margin.",
          nyquist([(3, 0), (1.5, -1.5), (-0.75, 0)], "reduced margin"),
          nyq_fig)

    b.mc(4,
         r"For describing function analysis of a nonlinear system, the Nyquist plot is used to",
         ["find intersections that predict limit cycles",
          "determine the DC gain only",
          "calculate the exact step response",
          "design the optimal controller"], 0,
         r"The describing function is the complex gain of a nonlinearity as a function of amplitude. Where the negative inverse intersects the Nyquist curve of the linear part, a limit cycle may occur. This extends Nyquist to nonlinear prediction.",
         nyquist([(1, 0), (0, -1), (-0.8, -0.5), (-0.6, 0)], "describing function"),
         nyq_fig, ["gen-gain-phase"])
    b.num(4,
          r"The Nyquist curve's closest approach to \(-1\) is 0.4. The peak sensitivity \(M_s\) is",
          1 / 0.4, "1",
          r"Peak sensitivity is the reciprocal of the minimum distance to \(-1\): \(M_s = 1/0.4 = 2.5\). A smaller distance means larger sensitivity peak and less robust stability.",
          nyquist([(1, 0), (0, -1), (-0.6, -0.3), (-0.5, 0)], "peak sensitivity"),
          nyq_fig, ["gen-gain-phase"])
    b.mc(4,
         r"An open-loop unstable system with two RHP poles needs the Nyquist curve to",
         ["not encircle \(-1\) at all",
          "encircle \(-1\) twice counter-clockwise",
          "encircle \(-1\) twice clockwise",
          "pass through \(-1\)"], 1,
         r"For \(Z = 0\) closed-loop RHP poles, we need \(N = -P = -2\). Two counter-clockwise encirclements (negative in the convention) cancel the two open-loop RHP poles. Clockwise encirclements would add unstable poles.",
         splane([(1, 0), (2, 0)], [], "two OL RHP poles"),
         pole_fig, ["gen-gain-phase"])
    b.save()


def bank_discrete_time():
    b = Bank("discrete-time")
    zplane = "The z-plane with the unit circle."
    step_fig = "A discrete step response."

    b.mc(1,
         r"A discrete-time system is stable when all poles are",
         ["inside the unit circle",
          "in the left half-plane",
          "on the unit circle",
          "at the origin"], 0,
         r"In the z-plane, the stability boundary is the unit circle, not the imaginary axis. Poles inside \(|z| < 1\) decay. Poles on the unit circle give sustained oscillation. Poles outside grow without bound.",
         unit_circle_fig("z-plane stability", poles=[(0.5, 0.3), (0.5, -0.3)]),
         zplane)
    b.num(1,
          r"A first-order discrete system has pole at \(z = 0.8\). The equivalent continuous-time pole, if the sample time is \(T = 0.1\) s, is at",
          math.log(0.8) / 0.1, "1/s",
          r"The mapping is \(z = e^{sT}\), so \(s = \ln(z)/T = \ln(0.8)/0.1 = -2.23\). The pole is in the left half-plane, corresponding to a decaying mode.",
          unit_circle_fig("z to s mapping", poles=[(0.8, 0)]),
          zplane)
    b.num(1,
          r"Same pole at \(z = 0.8\), sample time 0.1 s. The time constant of the discrete mode is",
          -0.1 / math.log(0.8), "s",
          r"The continuous pole is \(s = \ln(0.8)/0.1 = -2.23\). The time constant is \(1/|-2.23| = 0.45\) s. This is how long the mode takes to decay by \(e^{-1}\).",
          unit_circle_fig("time constant", poles=[(0.8, 0)]),
          zplane)

    b.mc(2,
         r"The z-transform maps a continuous-time pole at \(s = -a\) with sample time \(T\) to",
         [r"\(z = e^{-aT}\)",
          r"\(z = -aT\)",
          r"\(z = 1/(aT)\)",
          r"\(z = a + T\)"], 0,
         r"The exact discretization gives \(z = e^{sT}\). For \(s = -a\), that is \(z = e^{-aT}\). The pole moves inside the unit circle if \(a > 0\). The other options are not the correct mapping.",
         unit_circle_fig("s to z mapping", poles=[(math.exp(-1), 0)]),
         zplane)
    b.num(2,
          r"A continuous pole at \(s = -2\) with sample time \(T = 0.5\) s maps to \(z =\)",
          math.exp(-2 * 0.5), "1",
          r"\(z = e^{-2 \times 0.5} = e^{-1} = 0.368\). The pole is well inside the unit circle, indicating a fast decay relative to the sample rate.",
          unit_circle_fig("s=-2 discretized", poles=[(math.exp(-1), 0)]),
          zplane)
    b.mc(2,
         r"Aliasing occurs when",
         ["the signal frequency exceeds half the sample rate",
          "the pole is inside the unit circle",
          "the sample rate is too high",
          "the z-transform has no poles"], 0,
         r"Nyquist's theorem requires sampling at more than twice the signal frequency. Frequencies above half the sample rate (the Nyquist frequency) fold back as aliases. This is a sampling limitation, not a stability issue.",
         unit_circle_fig("aliasing", poles=[(0.6, 0.6), (0.6, -0.6)]),
         zplane)

    T3 = 0.2
    tau3 = 1.0
    b.num(3,
          r"A first-order plant \(G(s) = 1/(s+1)\) is sampled at \(T = 0.2\) s. The discrete pole is at \(z =\)",
          math.exp(-1 * T3), "1",
          r"The continuous pole is at \(s = -1\). Discretized, \(z = e^{-1 \times 0.2} = e^{-0.2} = 0.819\). This is a standard zero-order hold discretization.",
          unit_circle_fig("first-order discretized", poles=[(math.exp(-T3), 0)]),
          zplane)
    b.num(3,
          r"A discrete system has poles at \(z = 0.6 \pm 0.5j\). The magnitude is",
          math.sqrt(0.6**2 + 0.5**2), "1",
          r"\(|z| = \sqrt{0.36 + 0.25} = 0.78\). Since \(|z| < 1\), the system is stable. The poles are a conjugate pair giving an oscillatory but decaying response.",
          unit_circle_fig("complex poles", poles=[(0.6, 0.5), (0.6, -0.5)]),
          zplane)
    b.mc(3,
         r"Faster sampling (smaller \(T\)) moves discrete poles",
         ["closer to \(z = 1\)",
          "closer to \(z = 0\)",
          "outside the unit circle",
          "has no effect on pole location"], 0,
         r"As \(T \to 0\), \(z = e^{sT} \to 1\) for any finite \(s\). Faster sampling means the pole is closer to \(z = 1\), which represents a slower decay per sample. Numerical issues can arise when \(T\) is too small.",
         unit_circle_fig("fast sampling", poles=[(0.99, 0)]),
         zplane)

    b.num(4,
          r"A sampled-data system has sample time 0.05 s. The Nyquist frequency is",
          1 / (2 * 0.05), "Hz",
          r"The Nyquist frequency is half the sample rate: \(f_N = 1/(2T) = 10\) Hz. Signals above 10 Hz will alias. In rad/s, the Nyquist rate is \(2\pi \times 10 = 62.8\) rad/s.",
          unit_circle_fig("Nyquist frequency"),
          zplane, ["freq-resp-lti"])
    b.mc(4,
         r"A digital controller has a computational delay of one sample. In the z-domain, this delay is represented by",
         [r"\(z^{-1}\)",
          r"\(e^{-sT}\)",
          r"\(1/(s+1)\)",
          r"\(z\)"], 0,
         r"One sample delay multiplies the transfer function by \(z^{-1}\). This shifts the output by one sample. Multiple delays give \(z^{-n}\). The continuous delay \(e^{-sT}\) is the time-domain equivalent.",
         unit_circle_fig("one-sample delay"),
         zplane, ["time-delay"])
    b.num(4,
          r"A rule of thumb: sample at least 10 times per time constant. For a plant with \(\tau = 0.5\) s, the maximum sample period is",
          0.05, "s",
          r"The sample period should be \(T \le \tau/10 = 0.5/10 = 0.05\) s. This ensures the discrete controller captures the plant dynamics. Sampling too slowly loses information.",
          unit_circle_fig("sampling rate"),
          zplane, ["pid-impl"])
    b.save()


def bank_eig_modes():
    b = Bank("eig-modes")
    pole_fig = "Pole marks in the complex plane."
    mode_fig = "Curves showing mode contributions."
    decay = "A curve that decays toward zero."

    b.mc(1,
         r"The eigenvalues of the system matrix \(A\) determine",
         ["the modes of the free response",
          "the input matrix \(B\)",
          "the output matrix \(C\)",
          "the feedthrough matrix \(D\)"], 0,
         r"Each eigenvalue gives a mode: exponential decay for real negative, oscillation for complex pairs. The eigenvectors determine how much each initial condition excites each mode. \(B\), \(C\), and \(D\) affect forced response and output, not the natural modes.",
         splane([(-1, 0), (-2, 1), (-2, -1)], [], "eigenvalues"),
         pole_fig)
    b.num(1,
          r"A 2x2 diagonal matrix has entries \([-2, -5]\). The slower eigenvalue is",
          -2.0, "1",
          r"The eigenvalue \(-2\) is closer to zero than \(-5\), so it decays more slowly. The time constant of the slow mode is \(1/2 = 0.5\) s. The fast mode has time constant \(1/5 = 0.2\) s.",
          splane([(-2, 0), (-5, 0)], [], "diagonal eigenvalues"),
          pole_fig)
    b.num(1,
          r"Same matrix. The time constant of the fast mode is",
          0.2, "s",
          r"The fast eigenvalue is \(-5\). The time constant is \(\tau = 1/|-5| = 0.2\) s. After \(0.2\) s, this mode decays by \(e^{-1}\).",
          splane([(-2, 0), (-5, 0)], [], "fast mode"),
          pole_fig)

    b.mc(2,
         r"A complex eigenvalue \(\lambda = -1 + 2j\) contributes a mode that",
         ["decays monotonically",
          "oscillates at 2 rad/s while decaying",
          "grows without bound",
          "oscillates at 1 rad/s while decaying"], 1,
         r"The real part \(-1\) gives exponential decay. The imaginary part \(\pm 2\) gives oscillation at 2 rad/s. The conjugate pair together produce a real-valued damped sinusoid.",
         splane([(-1, 2), (-1, -2)], [], "complex eigenvalue"),
         pole_fig)
    b.num(2,
          r"A complex eigenvalue is \(-3 + 4j\). The natural frequency (distance to origin) is",
          5.0, "rad/s",
          r"\(\omega_n = \sqrt{3^2 + 4^2} = 5\) rad/s. The damping ratio is \(\zeta = 3/5 = 0.6\). The decay rate is the real part, 3.",
          splane([(-3, 4), (-3, -4)], [], "natural frequency"),
          pole_fig)
    b.num(2,
          r"Same eigenvalue, \(-3 + 4j\). The damping ratio is",
          0.6, "1",
          r"The damping ratio is \(\zeta = |\mathrm{Re}|/\omega_n = 3/5 = 0.6\). This is the cosine of the angle from the negative real axis to the pole.",
          splane([(-3, 4), (-3, -4)], [], "damping ratio"),
          pole_fig)

    A_ex = [[-1, 2], [0, -3]]
    eigvals = [-1, -3]
    b.num(3,
          r"The matrix \(A = \begin{bmatrix}-1 & 2 \\ 0 & -3\end{bmatrix}\) is upper triangular. Its slower eigenvalue is",
          -1.0, "1",
          r"For a triangular matrix, the eigenvalues are the diagonal entries \(-1\) and \(-3\). The slower one is closer to the origin, so it is \(-1\). The other eigenvalue, \(-3\), decays three times faster.",
          splane([(-1, 0), (-3, 0)], [], "triangular eigenvalues"),
          pole_fig, version=2)
    b.num(3,
          r"Same matrix. If the initial state is \([1, 0]^T\), which is an eigenvector for \(\lambda = -1\), the state at \(t = 1\) is entirely in the first mode with value",
          math.exp(-1), "1",
          r"Starting on an eigenvector, only that mode is excited: \(x_1(t) = e^{-t}\). At \(t = 1\), \(x_1 = e^{-1} = 0.368\). The second mode is not excited.",
          step_response("single mode", fn=lambda t: math.exp(-t), t_end=5),
          decay)
    b.mc(3,
         r"If \(A\) is diagonalizable as \(A = V \Lambda V^{-1}\), the matrix exponential is",
         [r"\(e^{At} = e^{Vt} \Lambda e^{-Vt}\)",
          r"\(e^{At} = A^t\)",
          r"\(e^{At} = V e^{\Lambda t} V^{-1}\)",
          r"\(e^{At} = e^A e^t\)"], 2,
         r"Diagonalization gives \(e^{At} = V e^{\Lambda t} V^{-1}\), where \(e^{\Lambda t}\) is diagonal with entries \(e^{\lambda_i t}\). This is the standard formula for computing the matrix exponential.",
         matrix_fig([[r"e^{\lambda_1 t}", "0"], ["0", r"e^{\lambda_2 t}"]], "diagonal exponential"),
         "A diagonal matrix of exponentials.")

    b.num(4,
          r"A realization has eigenvalues \(-0.5\), \(-2\), and \(-4\). After 10 s, the response is dominated by the slowest mode. The dominant eigenvalue is",
          -0.5, "1",
          r"The eigenvalue \(-0.5\) has time constant 2 s. After 10 s (5 time constants), the other modes are negligible. The slow mode dominates the long-term response.",
          splane([(-0.5, 0), (-2, 0), (-4, 0)], [], "dominant mode"),
          pole_fig, ["realization"])
    b.num(4,
          r"The trace of a 2x2 matrix with eigenvalues \(-1\) and \(-4\) is",
          -5.0, "1",
          r"The trace equals the sum of eigenvalues: \(-1 + (-4) = -5\). The determinant is the product: \((-1)(-4) = 4\). These are the invariants of the characteristic polynomial.",
          matrix_fig([[r"-1", "?"], ["?", r"-4"]], "trace and determinant"),
          "A matrix with diagonal entries shown.", ["lin-algebra-review"])
    b.mc(4,
         r"For observability: if a mode is unobservable,",
         ["the mode grows without bound",
          "the mode cannot be excited by input",
          "the mode determines the DC gain",
          "the mode cannot be seen at the output"], 3,
         r"An unobservable mode does not appear in the output regardless of initial conditions. It may still evolve internally. An uncontrollable mode cannot be excited by input. These are dual concepts.",
          splane([(-1, 0), (-2, 0)], [], "observable modes"), pole_fig, ["observability"])
    b.save()


def bank_ss_to_tf():
    b = Bank("ss-to-tf")
    pole_fig = "Pole marks in the s-plane."
    mat_fig = "A matrix expression."

    b.mc(1,
         r"The transfer function from state-space form is",
         [r"\(G(s) = C(sI - A)^{-1}B + D\)",
          r"\(G(s) = A(sI - B)^{-1}C + D\)",
          r"\(G(s) = (sI - A)^{-1}\)",
          r"\(G(s) = A + B + C + D\)"], 0,
         r"The state-space to transfer function formula is \(G(s) = C(sI - A)^{-1}B + D\). The matrix \((sI - A)^{-1}\) is the resolvent. \(D\) is the direct feedthrough. The other formulas have incorrect matrix ordering.",
         matrix_fig([["C", r"(sI-A)^{-1}", "B", "+", "D"]], "state to transfer"),
         mat_fig)
    b.mc(1,
         r"The poles of the transfer function are",
         ["the roots of \(\det(sI - A) = 0\)",
          "the diagonal of \(A\)",
          "the roots of \(\det(B)\)",
          "the eigenvalues of \(C\)"], 0,
         r"The poles are where \((sI - A)^{-1}\) blows up, which is where \(\det(sI - A) = 0\). These are the eigenvalues of \(A\). The diagonal entries are eigenvalues only for diagonal matrices.",
         splane([(-1, 0), (-2, 0)], [], "poles from eigenvalues"),
         pole_fig)
    b.num(1,
          r"A state-space system has \(A = -3\), \(B = 1\), \(C = 2\), \(D = 0\). The DC gain \(G(0)\) is",
          2 * (1 / 3) * 1, "1",
          r"\(G(0) = C(0 - A)^{-1}B = 2 \times (1/3) \times 1 = 0.667\). At DC, \((sI - A)^{-1}\) becomes \(-A^{-1} = 1/3\). The pole at \(-3\) means the system is stable.",
         splane([(-3, 0)], [], "DC gain"),
         pole_fig)

    b.num(2,
          r"A diagonal \(A = \mathrm{diag}(-2, -5)\) has its slower pole at",
          -2.0, "rad/s",
          r"The eigenvalues of a diagonal matrix are its diagonal entries, so the poles are \(-2\) and \(-5\). The slower pole is the one closer to the origin, \(-2\). Entering \(-5\) names the faster pole.",
          splane([(-2, 0), (-5, 0)], [], "diagonal poles"),
          pole_fig, version=2)
    b.mc(2,
         r"If the state-space realization is minimal (controllable and observable), the transfer function poles",
         ["equal the eigenvalues of \(A\)",
          "are fewer than the eigenvalues",
          "are more than the eigenvalues",
          "are always at the origin"], 0,
         r"A minimal realization has no pole-zero cancellations. The transfer function degree equals the state dimension. Non-minimal realizations may have hidden modes that cancel, giving fewer poles than eigenvalues.",
         splane([(-1, 0), (-3, 0)], [], "minimal realization"),
         pole_fig)
    b.num(2,
          r"A 2x2 system has \(A = \begin{bmatrix}-1 & 0 \\ 0 & -4\end{bmatrix}\), \(B = \begin{bmatrix}1 \\ 1\end{bmatrix}\), \(C = [1\; 1]\), \(D = 0\). The DC gain is",
          1 * 1 / 1 + 1 * 1 / 4, "1",
          r"\(G(0) = C(-A)^{-1}B = [1\; 1] \begin{bmatrix}1 & 0 \\ 0 & 1/4\end{bmatrix} \begin{bmatrix}1 \\ 1\end{bmatrix} = 1 + 0.25 = 1.25\). Each mode contributes to the DC gain.",
          matrix_fig([["-1", "0"], ["0", "-4"]], "diagonal A"),
          mat_fig)

    b.num(3,
          r"A first-order system has a pole at \(-2\) and DC gain 3. If \(D = 0\), the product \(CB\) is",
          3.0 * 2.0, "1",
          r"With \(D = 0\), the DC gain is \(CB/|A|\). The pole at \(-2\) means \(|A| = 2\), and the DC gain is 3, so \(CB/2 = 3\) and \(CB = 6\). Reporting 3 repeats the DC gain instead of the product.",
          splane([(-2, 0)], [], "first-order gain"),
          pole_fig, version=2)
    b.mc(3,
         r"A zero of the transfer function corresponds to",
         ["a pole-zero cancellation in a mode",
          "an eigenvalue of \(A\)",
          "a frequency where \(C(sI-A)^{-1}B + D = 0\)",
          "a DC gain of infinity"], 2,
         r"Zeros are where the numerator is zero, meaning \(G(s) = 0\). For SISO, this is where \(C(sI-A)^{-1}B + D = 0\). Zeros can affect the transient response shape and the high-frequency rolloff.",
         splane([(-2, 0)], [(-4, 0)], "pole and zero"),
         "A pole cross and a zero circle.")
    b.num(3,
          r"A system has poles at \(-1\) and \(-3\). The denominator of \(G(s)\) is \(s^2 + as + b\). The value of \(a\) is",
          4.0, "1",
          r"The denominator is \((s+1)(s+3) = s^2 + 4s + 3\). So \(a = 4\) and \(b = 3\). The sum of the poles' magnitudes is 4; the product is 3.",
          splane([(-1, 0), (-3, 0)], [], "characteristic polynomial"),
          pole_fig)

    b.num(4,
          r"A system with \(A = \begin{bmatrix}-2 & 1 \\ 0 & -2\end{bmatrix}\) has repeated eigenvalue at \(-2\). The denominator of \(G(s)\) is \((s+2)^n\). The value of \(n\) is",
          2.0, "1",
          r"The matrix has a repeated eigenvalue \(-2\) with algebraic multiplicity 2. The characteristic polynomial is \((s+2)^2\). The transfer function denominator is at most this, possibly less if there are cancellations.",
          splane([(-2, 0)], [], "repeated pole"),
          pole_fig, ["realization"])
    b.mc(4,
         r"A state transformation \(T\) changes \(A\) to \(TAT^{-1}\). The transfer function",
         ["is unchanged",
          "is multiplied by \(T\)",
          "is multiplied by \(\det(T)\)",
          "has new poles"], 0,
         r"A similarity transformation does not change the transfer function. The eigenvalues (poles) are preserved. The state representation changes, but the input-output behavior is the same.",
          matrix_fig([["T", "A", r"T^{-1}"]], "similarity transform"), mat_fig, ["realization"])
    b.num(4,
          r"A transfer function \(G(s) = 5/(s+4)\) has one pole. A minimal realization needs at least how many states?",
          1.0, "1",
          r"The transfer function order is 1 (one pole, no cancellation). A minimal realization has state dimension equal to the transfer function order. More states would introduce hidden modes.",
          splane([(-4, 0)], [], "first-order TF"),
          pole_fig, ["realization"])
    b.save()


def bank_limit_cycles():
    b = Bank("limit-cycles")
    phase_fig = "A phase portrait with trajectories."
    cycle_fig = "A closed orbit in the phase plane."

    b.mc(1,
         r"A limit cycle is",
         ["a closed orbit that nearby trajectories approach or leave",
          "an equilibrium point",
          "any oscillation in a linear system",
          "the same as a center"], 0,
         r"A limit cycle is an isolated periodic orbit. Nearby trajectories spiral toward (stable) or away from (unstable) it. Equilibrium points are single points, not orbits. Linear systems cannot have isolated limit cycles.",
         limit_cycle_fig("limit cycle"),
         cycle_fig)
    b.mc(1,
         r"Limit cycles can exist in",
         ["only linear systems",
          "only nonlinear systems",
          "any system with feedback",
          "only systems without damping"], 1,
         r"Limit cycles require nonlinearity to sustain oscillation. Linear systems have either stable nodes/spirals, centers (non-isolated orbits), or unstable trajectories. The nonlinearity provides energy to maintain the cycle.",
         limit_cycle_fig("nonlinear cycle"),
         cycle_fig)
    b.mc(1,
         r"A stable limit cycle is approached by",
         ["trajectories starting from any initial condition",
          "trajectories from nearby initial conditions",
          "only trajectories exactly on the cycle",
          "no trajectories"], 1,
         r"A stable limit cycle is an attractor for nearby trajectories, which spiral in from outside or out from inside. Global stability (from any IC) is not guaranteed. Unstable limit cycles repel nearby trajectories.",
         limit_cycle_fig("stable cycle"),
         cycle_fig)

    b.mc(2,
         r"The Van der Pol oscillator has",
         ["a single stable limit cycle for positive \(\mu\)",
          "no limit cycles",
          "infinitely many limit cycles",
          "only unstable limit cycles"], 0,
         r"The Van der Pol equation \(\ddot{x} - \mu(1-x^2)\dot{x} + x = 0\) has one stable limit cycle for \(\mu > 0\). The nonlinear damping term sustains oscillation by providing negative damping for small amplitude and positive damping for large amplitude.",
         limit_cycle_fig("Van der Pol"),
         cycle_fig)
    b.mc(2,
         r"A bifurcation is a qualitative change in system behavior as",
         ["a parameter varies",
          "time increases",
          "the initial condition changes",
          "the input oscillates"], 0,
         r"A bifurcation occurs when varying a parameter crosses a threshold that changes the number or stability of equilibria or limit cycles. Time evolution does not cause bifurcation; parameter changes do.",
         limit_cycle_fig("bifurcation"),
         cycle_fig)
    b.mc(2,
         r"A Hopf bifurcation creates or destroys",
         ["a limit cycle as eigenvalues cross the imaginary axis",
          "an equilibrium point",
          "a saddle-node connection",
          "multiple equilibria"], 0,
         r"In a Hopf bifurcation, a complex conjugate pair of eigenvalues crosses the imaginary axis. A stable focus becomes unstable, and a limit cycle appears (or vice versa). This is distinct from saddle-node bifurcation of equilibria.",
         splane([(0, 2), (0, -2)], [], "Hopf eigenvalues"),
         "Eigenvalues on the imaginary axis.")

    b.mc(3,
         r"Relay (on-off) control can cause",
         ["limit cycles due to switching",
          "exponential stability",
          "linear response",
          "no oscillation"], 0,
         r"Relay control switches between two states based on the error sign. This nonlinearity can create self-sustained oscillation (chattering or limit cycles) around the setpoint. The amplitude and frequency depend on the plant and relay hysteresis.",
         limit_cycle_fig("relay cycle"),
         cycle_fig)
    b.mc(3,
         r"The describing function method",
         ["approximates a nonlinearity's response to sinusoidal input",
          "finds exact solutions for limit cycles",
          "applies only to linear systems",
          "requires all nonlinearities to be saturation"], 0,
         r"The describing function is the complex gain of a nonlinearity as a function of input amplitude. It approximates the fundamental harmonic response. Combined with the Nyquist plot, it predicts limit cycle amplitude and frequency.",
         limit_cycle_fig("describing function"),
         cycle_fig)
    b.num(3,
          r"A relay oscillation has period 2 s. The frequency is",
          0.5, "Hz",
          r"Frequency is the reciprocal of period: \(f = 1/2 = 0.5\) Hz. In rad/s, that is \(\omega = 2\pi \times 0.5 = \pi\) rad/s.",
          limit_cycle_fig("relay period"),
          cycle_fig)

    b.mc(4,
         r"A region of attraction is",
         ["the set of initial conditions that converge to an equilibrium or limit cycle",
          "the limit cycle itself",
          "the set of all equilibria",
          "the entire state space"], 0,
         r"The region of attraction (basin of attraction) is the set of initial conditions from which trajectories converge to a particular attractor. Different attractors have different basins. The basin may not be the entire state space.",
         limit_cycle_fig("basin of attraction"),
         cycle_fig, ["lyapunov"])
    b.mc(4,
         r"Multiple equilibria in a nonlinear system mean",
         ["the long-term behavior depends on the initial condition",
          "the system is linear",
          "all trajectories go to the same point",
          "there are no limit cycles"], 0,
         r"With multiple equilibria, different initial conditions may converge to different resting states. The system has multiple basins of attraction. This is typical of nonlinear systems; linear systems have at most one equilibrium.",
         limit_cycle_fig("multiple equilibria"),
         phase_fig, ["lyapunov"])
    b.mc(4,
         r"Poincar\u00e9 map analysis of periodic orbits",
         ["records successive crossings of a surface of section and studies that map",
          "uses only linear analysis",
          "finds all equilibria",
          "applies only in one dimension"], 0,
         r"A Poincar\u00e9 map records where a trajectory crosses a surface of section, then studies that map. For a limit cycle the crossing is a fixed point, and the orbit is stable when that fixed point is. Sampling at a fixed clock period is a stroboscopic map, which is a different construction. The method is not limited to one dimension and it is not a search for every equilibrium.",
         limit_cycle_fig("Poincare map"),
         cycle_fig, ["gen-gain-phase"], version=2)
    b.save()


def expl_step_specs():
    fig = second_order_step(0.4, 4, 1, 4)
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A curve that rises, overshoots, and then settles.",
         "body_md": r"""Step-response specifications quantify transient behavior in terms that designers and customers can discuss. Rise time says how fast the output gets to the setpoint. Overshoot says how far past it goes. Settling time says when oscillations die out. Steady-state error says the remaining offset.

These specs map directly to the s-plane for second-order systems. The damping ratio controls overshoot. The natural frequency and damping ratio together control rise time and settling time. Higher loop gain reduces steady-state error but can increase overshoot if not carefully tuned."""},
        {"heading": "Key equations", "body_md": r"""Rise time (10% to 90%), approximate:
\[
t_r \approx \frac{1.8}{\omega_n} \quad (\text{for } \zeta \approx 0.7).
\]

Percent overshoot:
\[
M_p = 100 \, e^{-\pi\zeta/\sqrt{1-\zeta^2}}.
\]

Time to peak: \(t_p = \pi/\omega_d\).

2% settling time: \(t_s \approx 4/(\zeta\omega_n)\). 5% settling: \(t_s \approx 3/(\zeta\omega_n)\).

Steady-state error to a unit step (type-0): \(e_{ss} = 1/(1+K)\)."""},
        {"heading": "Worked example", "body_md": r"""A spec requires overshoot below 10% and settling time under 1.5 s. First, 10% overshoot gives \(\zeta = 0.6\) (from the overshoot formula). Then, \(t_s = 4/(\zeta\omega_n) < 1.5\) requires \(\omega_n > 4/(0.6 \times 1.5) = 4.44\) rad/s. Poles at \(-2.67 \pm j3.56\) satisfy both specs. Checking: overshoot is \(100 e^{-1.885/0.8} = 9.5\%\), settling time is \(4/(0.6 \times 4.44) = 1.5\) s."""},
        {"heading": "Common pitfalls", "body_md": r"""Rise time formulas vary by definition (0–90% vs 10–90%). Always state which. Overshoot depends only on \(\zeta\), not \(\omega_n\). Settling time depends on the product \(\zeta\omega_n\). Increasing \(\omega_n\) alone speeds settling but does not reduce overshoot. The formulas assume dominant second-order poles; additional poles change the actual response."""},
        {"heading": "Where this leads", "body_md": r"""PID tuning translates specs into controller gains. Root locus and frequency-domain design shape the closed-loop poles to meet specs. Higher-order systems are approximated by dominant poles. Frequency-domain specs (bandwidth, phase margin) connect to time-domain specs through closed-loop resonance."""},
    ]
    save_explainer("step-specs", "Step-response specifications", sections)
    return words(sections)


def expl_pid():
    fig = pid_block(1, 1, 1, "PID controller")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A PID controller in a feedback loop.",
         "body_md": r"""The PID controller is the workhorse of industrial control. It combines three terms: proportional (P) reacts to the current error, integral (I) accumulates past error to eliminate steady-state offset, and derivative (D) anticipates future error by acting on the rate of change.

Together, these three knobs give enough flexibility to achieve good tracking and disturbance rejection for a wide range of plants. The challenge is tuning: too much gain gives overshoot and oscillation; too little gives sluggish response and lingering error."""},
        {"heading": "Key equations", "body_md": r"""Control law in parallel form:
\[
u(t) = K_p e(t) + K_i \int_0^t e(\tau)\,d\tau + K_d \frac{de}{dt}.
\]

Transfer function (ideal PID):
\[
C(s) = K_p + \frac{K_i}{s} + K_d s = \frac{K_d s^2 + K_p s + K_i}{s}.
\]

The integral adds a pole at the origin and eliminates DC error. The derivative adds phase lead at high frequency. The two zeros of the numerator can be placed to cancel or compensate plant poles."""},
        {"heading": "Worked example", "body_md": r"""A first-order plant \(G(s) = 2/(s+1)\) with PI control \(C(s) = 3 + 4/s\). The loop gain is \(L(s) = C(s)G(s) = (3s+4) \times 2 / [s(s+1)] = (6s+8)/[s(s+1)]\). The zero at \(s = -4/3\) adds phase. At DC, the loop gain is infinite, so steady-state error to a step is zero. The closed-loop poles come from the characteristic equation \(s(s+1) + 6s + 8 = s^2 + 7s + 8 = 0\), giving poles at \(-1\) and \(-8\)."""},
        {"heading": "Common pitfalls", "body_md": r"""The derivative term amplifies noise. Practical controllers filter the derivative or use \(K_d s / (1 + \tau_f s)\). Integral windup occurs when the actuator saturates while the integrator builds up. Anti-windup schemes limit the integrator during saturation. The ideal PID transfer function is improper (degree of numerator exceeds denominator); implementations add a fast pole."""},
        {"heading": "Where this leads", "body_md": r"""Tuning rules (Ziegler-Nichols, Cohen-Coon, lambda tuning) provide starting points. Frequency-domain design shapes the loop gain for desired margins. State-space methods (pole placement, LQR) can synthesize PID-like controllers. Feedforward complements PID for known disturbances or reference profiles."""},
    ]
    save_explainer("pid", "PID control law", sections)
    return words(sections)


def expl_sensitivity():
    fig = block_diagram(["G"], "sensitivity functions", feedback="1", input_label="r", output_label="y", disturbance="d")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A feedback loop with reference and disturbance inputs.",
         "body_md": r"""The sensitivity function \(S(s)\) tells how much of a disturbance appears at the output. With loop gain \(L\), \(S = 1/(1+L)\). When \(L\) is large, \(S\) is small and disturbances are attenuated. The complementary sensitivity \(T = L/(1+L)\) is the fraction of the loop that tracks a reference when feedback is unity.

These two functions satisfy \(S + T = 1\). This constraint means you cannot make both small at the same frequency. At low frequencies you want \(T \approx 1\) and \(S \approx 0\). At high frequencies you want \(S \approx 1\) (inevitable) and \(T \approx 0\) (to reject noise)."""},
        {"heading": "Key equations", "body_md": r"""With \(L\) the loop gain:
\[
S(s) = \frac{1}{1 + L(s)}, \quad T(s) = \frac{L(s)}{1 + L(s)}, \quad S + T = 1.
\]

Those two definitions add to 1 at every frequency where \(L\) is defined. For unity feedback, a disturbance at the output reaches the output through \(S\), the reference reaches the output through \(T\), and the reference reaches the error through \(S\).

Peak sensitivity \(M_s = \max_\omega |S(j\omega)|\) is a robustness measure. The reciprocal \(1/M_s\) is the closest approach of the Nyquist curve to \(-1\)."""},
        {"heading": "Worked example", "body_md": r"""A loop has \(L(j\omega) = 10\) at \(\omega = 0.1\) rad/s. The sensitivity is \(S = 1/11 = 0.091\). A disturbance of amplitude 5 at the output is reduced to \(0.091 \times 5 = 0.45\) at the output after the loop responds. The complementary sensitivity is \(T = 10/11 = 0.91\), so a reference of 10 gives output \(0.91 \times 10 = 9.1\). The tracking error is \(10 - 9.1 = 0.9 = S \times 10\)."""},
        {"heading": "Common pitfalls", "body_md": r"""\(S + T = 1\) follows from the definitions of \(S\) and \(T\). It does not require stability, and it is not only a DC identity. Unity feedback is what makes \(T\) equal the reference-to-output map. With a sensor \(H \ne 1\), that map is \(G/(1+GH)\), which is not \(T = L/(1+L)\). Confusing \(S\) and \(T\) swaps disturbance rejection and tracking. A small \(|S|\) means disturbances at the output are attenuated, not that every signal in the loop is insensitive."""},
        {"heading": "Where this leads", "body_md": r"""The Gang of Four (\(S\), \(T\), \(PS\), \(CS\)) fully characterizes a loop. Robust stability bounds \(|T \cdot \Delta| < 1\) for multiplicative uncertainty. Robust performance bounds combine \(S\) and \(T\) with uncertainty models. The waterbed effect and Bode integrals show fundamental limits on \(S\)."""},
    ]
    save_explainer("sensitivity", "Sensitivity functions", sections, version=2)
    return words(sections)


def expl_nyquist():
    fig = nyquist([(3, 0), (1, -2), (-0.5, -1), (-0.3, 0), (-0.5, 1), (1, 2), (3, 0)], "Nyquist plot")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A curve in the complex plane encircling the critical point.",
         "body_md": r"""The Nyquist plot traces the loop transfer function \(L(j\omega)\) in the complex plane as \(\omega\) goes from 0 to infinity. The critical point is \(-1\). If the open-loop is stable (no RHP poles), the closed-loop is stable if and only if the Nyquist curve does not encircle \(-1\).

More generally, the Nyquist stability criterion counts encirclements: the number of closed-loop RHP poles equals the number of clockwise encirclements of \(-1\) plus the number of open-loop RHP poles. Zero encirclements for a stable open-loop means closed-loop stability."""},
        {"heading": "Key equations", "body_md": r"""Nyquist criterion:
\[
Z = N + P,
\]
where \(Z\) = closed-loop RHP poles, \(N\) = clockwise encirclements of \(-1\), \(P\) = open-loop RHP poles. Stability requires \(Z = 0\).

Gain margin: the factor by which \(|L|\) can increase before the curve crosses \(-1\). If the negative-real crossing is at \(-1/k\), GM \(= k\).

Phase margin: at \(|L| = 1\), the angle from \(-180°\) to the phase of \(L\). PM \(= 180° + \angle L(j\omega_c)\)."""},
        {"heading": "Worked example", "body_md": r"""An open-loop stable system has \(L(s) = 10/[(s+1)(s+2)]\). At low frequency, \(L(j0) = 10/2 = 5\). As \(\omega \to \infty\), \(|L| \to 0\). The curve starts at 5 on the positive real axis, loops through the second and third quadrants, and returns to the origin. It does not encircle \(-1\), so the closed-loop is stable. The phase crossover (where the curve crosses the negative real axis) determines the gain margin; if it crosses at \(-0.4\), GM \(= 1/0.4 = 2.5\)."""},
        {"heading": "Common pitfalls", "body_md": r"""Counter-clockwise encirclements are negative in some conventions. Be consistent with the sign of \(N\). The complete Nyquist contour includes the infinite semicircle in the RHP, which matters for systems with poles on the imaginary axis. Open-loop unstable systems need net counter-clockwise encirclements to stabilize."""},
        {"heading": "Where this leads", "body_md": r"""Robust stability uses the Nyquist plot with uncertainty circles. Describing function analysis intersects the Nyquist curve with the negative inverse describing function to predict limit cycles. M- and N-circles help read closed-loop gain and phase from the Nyquist plot. Nichols charts are an alternative presentation."""},
    ]
    save_explainer("nyquist", "Nyquist plot and stability criterion", sections)
    return words(sections)


def expl_discrete_time():
    fig = unit_circle_fig("z-plane stability", poles=[(0.7, 0.3), (0.7, -0.3)])
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "The z-plane with poles inside the unit circle.",
         "body_md": r"""Discrete-time systems operate on sampled data: the state updates at fixed intervals \(T\) seconds apart. Instead of differential equations, we have difference equations. Instead of the s-plane, we use the z-plane.

Stability shifts from the left half-plane to the inside of the unit circle. A pole at \(z = 0.9\) is stable (decaying); a pole at \(z = 1.1\) is unstable (growing). The mapping \(z = e^{sT}\) connects continuous and discrete poles. Faster sampling (smaller \(T\)) moves poles closer to \(z = 1\)."""},
        {"heading": "Key equations", "body_md": r"""Difference equation: \(x[k+1] = A_d x[k] + B_d u[k]\).

Discretization of \(s\)-plane pole: \(z = e^{sT}\).

A pole at \(s = -a\) maps to \(z = e^{-aT}\).

Stability: all poles inside \(|z| < 1\).

Nyquist frequency: \(f_N = 1/(2T)\). Frequencies above \(f_N\) alias."""},
        {"heading": "Worked example", "body_md": r"""A continuous system has pole at \(s = -4\) with sample time \(T = 0.1\) s. The discrete pole is \(z = e^{-4 \times 0.1} = e^{-0.4} = 0.67\). This is inside the unit circle, so the discrete mode decays. The decay per sample is 0.67, meaning each step the mode loses about 33% of its value. After 10 samples (1 s), the mode is at \(0.67^{10} = 0.018\), consistent with \(e^{-4 \times 1} = 0.018\)."""},
        {"heading": "Common pitfalls", "body_md": r"""Aliasing occurs when sampling below the Nyquist rate. Frequencies above \(f_N = 1/(2T)\) fold back and appear as low-frequency artifacts. Numerical issues arise when \(T\) is very small compared to the system time constants, as poles cluster near \(z = 1\). Computational delay of one sample is \(z^{-1}\), which adds phase lag."""},
        {"heading": "Where this leads", "body_md": r"""Digital PID requires discretization (Tustin, forward Euler, backward Euler). Z-transform analysis mirrors Laplace methods. Multirate systems sample different signals at different rates. Anti-aliasing filters are essential before sampling. The bilinear (Tustin) transform preserves frequency-domain characteristics."""},
    ]
    save_explainer("discrete-time", "Discrete-time systems", sections)
    return words(sections)


def expl_eig_modes():
    fig = splane([(-1, 2), (-1, -2), (-4, 0)], [], "eigenvalue modes")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "Eigenvalues in the s-plane with a complex pair and a real pole.",
         "body_md": r"""The eigenvalues of the system matrix \(A\) are the modes of the free response. Each eigenvalue contributes a term to the solution: \(e^{\lambda t}\) for a simple eigenvalue, \(t^k e^{\lambda t}\) for repeated ones. The eigenvectors determine how the initial condition excites each mode.

A real negative eigenvalue gives exponential decay. A complex conjugate pair gives damped oscillation. The time constant is the reciprocal of the real-part magnitude. The imaginary part is the oscillation frequency. Stability requires all eigenvalues in the open left half-plane."""},
        {"heading": "Key equations", "body_md": r"""Free response: \(x(t) = e^{At} x(0)\).

Diagonalizable case: \(A = V \Lambda V^{-1}\), so \(e^{At} = V e^{\Lambda t} V^{-1}\).

Mode from eigenvalue \(\lambda = \sigma + j\omega\): decays at rate \(|\sigma|\), oscillates at \(\omega\).

Natural frequency: \(\omega_n = |\lambda|\). Damping ratio: \(\zeta = |\sigma|/\omega_n\)."""},
        {"heading": "Worked example", "body_md": r"""Consider \(A\) with eigenvalues \(-2\) and \(-1 \pm 3j\). The real eigenvalue at \(-2\) contributes \(c_1 e^{-2t}\). The complex pair contributes \(e^{-t}(c_2 \cos 3t + c_3 \sin 3t)\). The mode at \(-2\) has time constant 0.5 s. The oscillatory mode has time constant 1 s and frequency 3 rad/s. After 3 s (six time constants of the fast mode), the \(-2\) mode is at \(e^{-6} = 0.0025\) and the response is dominated by the slower oscillating mode."""},
        {"heading": "Common pitfalls", "body_md": r"""The eigenvalue's imaginary part is the oscillation frequency in rad/s, not the time constant. Repeated eigenvalues may have \(t e^{\lambda t}\) terms; check the Jordan form. Diagonalization fails if eigenvectors are not independent. Computing \(e^{At}\) element-wise is wrong; use the spectral decomposition."""},
        {"heading": "Where this leads", "body_md": r"""Reachability asks which initial conditions each mode can be driven to. Observability asks which modes appear in the output. State feedback places eigenvalues. Observers estimate modes that are not directly measured. The eigenvalue-eigenvector decomposition is the foundation of modal analysis."""},
    ]
    save_explainer("eig-modes", "Eigenvalues and modes", sections)
    return words(sections)


def expl_ss_to_tf():
    fig = matrix_fig([["C", r"(sI-A)^{-1}", "B", "+", "D"]], "state to transfer")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "The formula G(s) = C(sI-A)^-1 B + D.",
         "body_md": r"""The transfer function of a state-space system summarizes the input-output behavior. The formula \(G(s) = C(sI - A)^{-1}B + D\) comes from taking the Laplace transform of the state equations and solving for the output.

The poles of \(G(s)\) are the values where \((sI - A)^{-1}\) blows up, which are the eigenvalues of \(A\). The zeros come from the numerator polynomial. A minimal realization has no pole-zero cancellations, so the transfer function order equals the state dimension."""},
        {"heading": "Key equations", "body_md": r"""State equations:
\[
\dot{x} = Ax + Bu, \quad y = Cx + Du.
\]

Transfer function:
\[
G(s) = C(sI - A)^{-1}B + D.
\]

Poles: roots of \(\det(sI - A) = 0\) (eigenvalues of \(A\)).

DC gain: \(G(0) = -CA^{-1}B + D\) (assuming \(A\) invertible)."""},
        {"heading": "Worked example", "body_md": r"""A first-order system has \(A = -3\), \(B = 2\), \(C = 4\), \(D = 0\). Then \((sI - A)^{-1} = 1/(s + 3)\). The transfer function is \(G(s) = 4 \cdot (1/(s+3)) \cdot 2 = 8/(s+3)\). The pole is at \(-3\), matching the eigenvalue. The DC gain is \(G(0) = 8/3 = 2.67\). Alternatively, \(-CA^{-1}B = -4 \cdot (-1/3) \cdot 2 = 8/3\)."""},
        {"heading": "Common pitfalls", "body_md": r"""The order matters: \(C\) on the left, \(B\) on the right. For MIMO systems, \(G\) is a matrix. Non-minimal realizations have hidden modes that cancel in the transfer function. The DC gain formula requires \(A\) to be invertible (no eigenvalue at zero)."""},
        {"heading": "Where this leads", "body_md": r"""Realization goes the other way: from \(G(s)\) to state-space form, with non-uniqueness. Controllable and observable canonical forms are standard constructions. Balancing and reduction techniques trim states that contribute little to input-output behavior. Frequency response \(G(j\omega)\) is evaluated from either representation."""},
    ]
    save_explainer("ss-to-tf", "State space to transfer function", sections)
    return words(sections)


def expl_limit_cycles():
    fig = limit_cycle_fig("stable limit cycle")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A phase portrait with trajectories spiraling toward a closed orbit.",
         "body_md": r"""A limit cycle is an isolated periodic orbit in a nonlinear system. Nearby trajectories either spiral in (stable limit cycle) or spiral out (unstable). Unlike centers in linear systems, limit cycles are isolated: there is no continuous family of periodic orbits at different amplitudes.

Limit cycles require nonlinearity to sustain oscillation. The Van der Pol oscillator has negative damping at small amplitude and positive damping at large amplitude, which drives all trajectories toward a unique orbit. Relay control and saturation can also create limit cycles."""},
        {"heading": "Key equations", "body_md": r"""Van der Pol oscillator:
\[
\ddot{x} - \mu(1 - x^2)\dot{x} + x = 0.
\]
For \(\mu > 0\), there is a stable limit cycle.

Hopf bifurcation: a limit cycle is born when a complex eigenvalue pair crosses the imaginary axis.

Describing function: approximate nonlinearity gain \(N(a)\) for input amplitude \(a\). Limit cycle where \(G(j\omega) = -1/N(a)\)."""},
        {"heading": "Worked example", "body_md": r"""A relay controller switches at zero error. The plant is \(G(s) = 1/[s(s+1)]\). The describing function of an ideal relay with amplitude \(M\) is \(N(a) = 4M/(\pi a)\). Intersection of \(-1/N(a)\) with the Nyquist plot of \(G\) gives the limit cycle. If the intersection is at amplitude \(a = 2\) and frequency \(\omega = 1\) rad/s, the relay system oscillates with peak-to-peak swing of 4 and period \(2\pi\) s."""},
        {"heading": "Common pitfalls", "body_md": r"""Linear systems cannot have isolated limit cycles; they have either stable equilibria, unstable trajectories, or (marginally) centers with a continuum of closed orbits. The describing function is an approximation; it assumes the nonlinearity sees a sinusoid and higher harmonics are filtered. Multiple limit cycles can coexist in some systems."""},
        {"heading": "Where this leads", "body_md": r"""Bifurcation theory classifies how limit cycles appear and disappear. Poincaré maps reduce periodic orbit analysis to fixed-point analysis. Lyapunov methods estimate the region of attraction. Describing functions extend to saturation, backlash, and dead zone. Anti-windup and dither mitigate relay chatter."""},
    ]
    save_explainer("limit-cycles", "Limit cycles and nonlinear behavior", sections)
    return words(sections)


def lint():
    banned = re.compile(r"niknejad|åström|aström|astrom|murray|feedback systems|\breader\b|§", re.I)
    skills = ["step-specs", "pid", "sensitivity", "nyquist", "discrete-time", "eig-modes", "ss-to-tf", "limit-cycles"]
    problems = []
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
            from collections import Counter
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
    bank_step_specs()
    bank_pid()
    bank_sensitivity()
    bank_nyquist()
    bank_discrete_time()
    bank_eig_modes()
    bank_ss_to_tf()
    bank_limit_cycles()
    print("words", expl_step_specs(), expl_pid(), expl_sensitivity(), expl_nyquist(), 
          expl_discrete_time(), expl_eig_modes(), expl_ss_to_tf(), expl_limit_cycles())
    lint()


if __name__ == "__main__":
    main()
