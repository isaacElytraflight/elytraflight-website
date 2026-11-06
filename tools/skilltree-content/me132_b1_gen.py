#!/usr/bin/env python3
"""Generate ME 132 batch B1 banks and explainers.

Numeric answers in this file come from closed-form algebra. skilltree/verify_me132_b1.py
recomputes them by simulation, eigenvalues, or complex arithmetic.
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from me132_b1_figs import (
    bars, bode_slope, car, closed_loop, decay_shape, delay_blocks, eigen_plane,
    inductor_h, inverse_step, mass_spring, matrix_fig, open_loop, plot,
    proportional, rc_circuit, rl_circuit, rotor, series_blocks, sine_shape,
    splane, step_shape, tank, vectors,
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK = os.path.join(ROOT, "skilltree", "bank")
EXP = os.path.join(ROOT, "skilltree", "explainers")


def g(x):
    return float(f"{x:.6g}")


class Bank:
    def __init__(self, sid):
        self.sid = sid
        self.qs = []
        self.n = {1: 0, 2: 0, 3: 0, 4: 0}

    def q(self, rnd, kind, prompt, explanation, fig=None, alt=None, preview=None, **kw):
        self.n[rnd] += 1
        item = {
            "id": f"{self.sid}-r{rnd}-q{self.n[rnd]}",
            "round": rnd,
            "type": kind,
            "prompt": prompt,
            "explanation": explanation,
        }
        if fig is not None:
            item["figure"] = fig
            item["figure_alt"] = alt
        if rnd == 4:
            item["preview"] = preview
        elif preview:
            raise SystemExit("preview only in round 4")
        item.update(kw)
        item.setdefault("version", 1)
        self.qs.append(item)

    def mc(self, rnd, prompt, options, correct, explanation, fig=None, alt=None, preview=None):
        self.q(rnd, "mc", prompt, explanation, fig, alt, preview,
               options=options, correct_index=correct)

    def num(self, rnd, prompt, answer, unit, explanation, fig=None, alt=None, preview=None):
        self.q(rnd, "numeric", prompt, explanation, fig, alt, preview,
               answer=g(answer), unit=unit, tolerance=0.02)

    def save(self):
        assert self.n == {1: 3, 2: 3, 3: 3, 4: 3}, (self.sid, self.n)
        path = os.path.join(BANK, f"{self.sid}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"skill_id": self.sid, "version": 1, "questions": self.qs},
                      f, indent=2, ensure_ascii=False)
            f.write("\n")


def save_explainer(sid, title, sections, version=1):
    path = os.path.join(EXP, f"{sid}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"id": sid, "title": title, "version": version, "sections": sections},
                  f, indent=2, ensure_ascii=False)
        f.write("\n")


def words(sections):
    text = "\n".join(s["body_md"] for s in sections)
    text = re.sub(r"\\\([\s\S]*?\\\)|\\\[[\s\S]*?\\\]", " ", text)
    text = re.sub(r"[#*_`>|]", " ", text)
    return len(text.split())


# ---------------------------------------------------------------------------
# fb-concepts
# ---------------------------------------------------------------------------

def bank_fb():
    b = Bank("fb-concepts")
    loop = closed_loop("Closed loop: reference, controller, actuator, plant, sensor")
    loop_alt = "Closed loop. Reference r enters a summing junction, then a controller C, an actuator, and a plant. The output y is measured by a sensor and subtracted at the junction."
    b.mc(1,
         "In closed-loop control, what signal does the controller act on?",
         [
             "The difference between the reference and the measured output",
             "The reference alone, with the measurement used only for logging",
             "The disturbance, which the controller is assumed to know exactly",
             "The plant output, added to the reference rather than subtracted",
         ], 0,
         "The controller's job in a negative-feedback loop is to drive the error, reference minus measurement, toward zero. The measurement is not a log: it is subtracted at the summing junction and that difference is the controller input.\n"
         "• Feeding the reference alone is open-loop control. The loop is not closed.\n"
         "• A disturbance is usually unmeasured. The controller sees it only through the error it causes.\n"
         "• Adding the measurement to the reference is positive feedback, which reinforces the error instead of reducing it.",
         loop, loop_alt)
    b.mc(1,
         "Which block turns the controller's command into a physical cause acting on the plant?",
         [
             "The sensor, because it is the only block that touches the real hardware",
             "The actuator",
             "The reference, because a larger reference produces a larger force",
             "The disturbance, because it is the unwanted physical input",
         ], 1,
         "The actuator is the block that converts the command (a voltage, a valve position, a throttle) into the physical quantity the plant actually feels. The sensor does the opposite job: it reports the output. The reference is a number we choose, and a disturbance is an input we do not choose.",
         closed_loop("Blocks of a feedback loop, with the actuator between the controller and the plant"),
         "Feedback loop with blocks labeled controller, actuator, plant, and sensor.")
    b.num(1,
          r"A fan is run open loop. Each volt of drive produces \(3.2\ \mathrm{rad/s}\) of speed, and the model is exact. What drive, in V, produces \(8\ \mathrm{rad/s}\)?",
          8 / 3.2, "V",
          r"Open loop sets the command from the model alone: \(u = 8/3.2 = 2.5\ \mathrm{V}\). Nothing is measured, so this is right only while the fan really does deliver \(3.2\ \mathrm{rad/s}\) per volt."
          "\n• Dividing the other way, \(3.2/8\), gives the reciprocal \(0.4\ \mathrm{V}\).\n"
          "• Multiplying \(3.2 \times 8\) gives \(25.6\), which is a speed, not a drive.\n"
          "• Treating \(3.2\) as already the answer forgets to scale it to the requested speed.",
          open_loop("Open-loop fan: reference becomes a drive, then an actuator, then the fan"),
          "Open-loop chain from a speed reference through a command block and an actuator to a plant. No measurement returns.")
    b.num(2,
          r"An open-loop speed command is calibrated as \(u = r/4\), in volts, for a plant of \(4\ \mathrm{rad/s}\) per volt. The real plant is \(5.2\ \mathrm{rad/s}\) per volt. For \(r = 10\ \mathrm{rad/s}\), how far is the actual speed from \(10\ \mathrm{rad/s}\)? Give a positive number, in rad/s.",
          abs(5.2 * (10 / 4) - 10), "rad/s",
          r"The frozen command is \(u = 10/4 = 2.5\ \mathrm{V}\). The real speed is \(5.2 \times 2.5 = 13\ \mathrm{rad/s}\), so the miss is \(13 - 10 = 3\ \mathrm{rad/s}\). Open loop has no measurement to pull the speed back."
          "\n• \(5.2 - 4 = 1.2\) subtracts the gains and never applies them to the reference.\n"
          "• \(10/5.2 = 1.92\) would be the command that would have worked, not the error of the command that was sent.\n"
          "• \(5.2 \times 10 = 52\) multiplies the reference by the plant gain and ignores that the command was only \(2.5\ \mathrm{V}\).",
          open_loop("Open-loop speed command with no return path from the measured speed"),
          "Open-loop chain from reference to command, actuator, and plant, with the output leaving the diagram.")
    b.mc(2,
         "An open-loop heater holds a fixed command. A disturbance then adds \(2\) degrees at the plant output. What happens to the output?",
         [
             "The disturbance is divided by \(1+L\), even though nothing is measured",
             "The output does not move, because the command was calibrated",
             "The output shifts by the full \(2\) degrees",
             "The output shifts by \(2\) times the plant gain",
         ], 2,
         "With no measurement there is no loop gain to attenuate anything. An output disturbance adds directly: the shift is \(2\) degrees.\n"
         "• Division by \(1+L\) is the closed-loop sensitivity. It needs a measured error.\n"
         "• Calibration matched the model at one operating point. It does not cancel a new disturbance.\n"
         "• Multiplying by the plant gain would be right for a disturbance at the plant input, not for one already at the output.",
         open_loop("Open-loop plant with a disturbance added at the output", disturbance=True),
         "Open-loop chain with a disturbance arrow added at the output. No sensor path returns.")
    b.mc(2,
         r"A proportional loop has loop gain \(L = 20\) and a constant reference. Which description of the steady output is right?",
         [
             "The output equals \(L\) times the reference, because each pass around the loop multiplies by \(L\)",
             "The output equals the reference divided by \(L\)",
             "The output sits at half the reference, because half the gain is used up by feedback",
             r"The output equals \(\dfrac{L}{1+L}\) times the reference, here \(20/21\) of it",
         ], 3,
         r"Solving \(y = L(r-y)\) gives \(y = \dfrac{L}{1+L} r = \dfrac{20}{21} r\). The output is close to the reference, short by the sensitivity \(1/21\)."
         "\n• \(L r\) is the open command applied once, not the fixed point of the loop.\n"
         "• \(r/L\) is what you would get by inverting the loop gain instead of using it as feedback.\n"
         "• Nothing in \(L/(1+L)\) says the result is one half. One half would need \(L = 1\).",
         bars("Qualitative comparison of a large open-loop shift and a small closed-loop shift"),
         "Two pairs of bars. The open-loop pair changes height a lot. The closed-loop pair barely changes.")
    b.mc(3,
         "A loop has a large loop gain at the frequencies where a sensor is noisy. What does the loop do with that noise?",
         [
             "It copies the noise onto the output, because the loop treats the noisy measurement as the truth",
             "It rejects sensor noise by \(1+L\), the same factor that rejects an output disturbance",
             "It ignores the noise, because a sensor is outside the plant",
             "It is less affected than an open-loop controller would be, because open loop also reads the sensor",
         ], 0,
         "The tracking factor \(T = L/(1+L)\) multiplies both the reference and the sensor noise. When \(L\) is large, \(T\) is near \(1\), so the output follows the noisy measurement. Output disturbances see the small factor \(S = 1/(1+L)\), not \(T\). Open loop does not read the sensor at all, so it does not pass sensor noise, and it also does not reject disturbances.",
         closed_loop("Sensor noise added on the return path of a feedback loop", noise=True),
         "Closed loop with an extra noise arrow entering the sensor on the return path.")
    b.num(3,
          r"A proportional position loop has controller gain \(9\), plant gain \(1\), and a reference of \(0\). A disturbance adds \(4\ \mathrm{m}\) at the output. What is the steady output, in m?",
          4 / (1 + 9 * 1), "m",
          r"The loop equation is \(y = 9(0 - y) + 4\). Then \(10y = 4\) and \(y = 0.4\ \mathrm{m}\). The same result is \(d/(1+L)\) with \(L = 9\)."
          "\n• Leaving the disturbance unattenuated gives \(4\ \mathrm{m}\).\n"
          "• Multiplying by the loop gain gives \(36\ \mathrm{m}\).\n"
          "• Using \(L/(1+L)\) instead of \(1/(1+L)\) gives \(3.6\ \mathrm{m}\), which is the response to a reference, not to an output disturbance.",
          closed_loop("Disturbance added at the plant output of a closed loop", disturbance=True),
          "Closed loop with a disturbance arrow entering at the output, after the plant.")
    b.mc(3,
         "The plant gain used for an open-loop calibration is \(50\\%\) low. A closed loop around the same plant has loop gain about \(20\). Which comparison is right?",
         [
             "Both outputs move by about \(50\\%\), because the plant moved by \(50\\%\)",
             "The open-loop output moves by about \(50\\%\). The closed-loop output moves by only a few percent",
             "The closed-loop output moves more, because the loop gain multiplies the plant error",
             "The open-loop output does not move, because the command was computed from the old model",
         ], 1,
         "Open loop applies a frozen command, so the output scales with the plant: a \(50\\%\) plant error is a \(50\\%\) output error. Closed loop, the fractional output change is about \(1/(1+L)\) times the fractional plant change. With \(L \\approx 20\) that factor is about \(1/21\), a few percent, not \(50\\%\).\n"
         "• The loop gain does not multiply the error. It is what makes the sensitivity small.\n"
         "• A command computed from the old model is exactly why the open-loop output is wrong after the plant changes.",
         )
    b.mc(4,
         "Two blocks stand in series. The first has gain \(3\), the second gain \(4\). What single gain replaces them?",
         [
             "\(7\), because series gains add",
             "\(3/4\), the ratio of the two gains",
             "\(12\), the product of the two gains",
             "\(1\), because the second block undoes the first",
         ], 2,
         "Blocks in series multiply. The equivalent gain is \(3 \\times 4 = 12\). Addition is the rule for signals that meet at a summing junction, not for blocks one after another. A ratio would be a feedback or a divider. Nothing here cancels: cancellation would need a block of gain \(1/3\) after the first block.",
         series_blocks("Two blocks in series, gains 3 and 4"),
         "Two blocks one after another, labeled gain 3 and gain 4, with an arrow into the first and an arrow out of the second.",
         ["block-diagram"])
    b.mc(4,
         r"A proportional controller uses \(K_c = 5\). The reference is \(6\) and the measured output is \(4\). What command does it send?",
         [
             "\(30\), the gain times the reference",
             "\(20\), the gain times the measurement",
             "\(-10\), the gain times the measurement minus the reference",
             "\(10\), the gain times the reference minus the measurement",
         ], 3,
         r"Proportional control acts on the error: \(u = K_c(r-y) = 5(6-4) = 10\)."
         "\n• \(K_c r = 30\) forgets to subtract the measurement.\n"
         "• \(K_c y = 20\) feeds the measurement forward instead of the error.\n"
         "• \(-10\) flips the sign, which is positive feedback and drives the output away from the reference.",
         proportional("Proportional controller: command equals gain times the error"),
         "Summing junction forming an error from reference and measured output, then a block labeled Kc producing a command.",
         ["onoff-pid-intro"])
    b.num(4,
          r"A speed loop has already been reduced to a loop gain \(L = 19\). The reference is \(0\). A grade disturbance adds the equivalent of \(2\ \mathrm{m/s}\) at the output. What steady speed does that disturbance produce, in m/s?",
          2 / (1 + 19), "m/s",
          r"The fixed point is \(y = L(0-y) + 2\), so \(y(1+19) = 2\) and \(y = 0.1\ \mathrm{m/s}\). A large loop gain turns a \(2\ \mathrm{m/s}\) disturbance into a tenth of a meter per second. This is the same sensitivity a cruise-control loop uses on a grade."
          "\n• Reporting \(2\ \mathrm{m/s}\) ignores the feedback.\n"
          "• \(19 \times 2 = 38\) multiplies the disturbance by the loop gain.\n"
          "• \(19/20 \times 2 = 1.9\) uses the tracking factor \(T\) where the sensitivity \(S\) belongs.",
          car("Vehicle pushed by a force, the plant inside a speed loop"),
          "Side view of a vehicle with a force arrow at the rear.",
          ["cruise-control"])
    b.save()
    return b


def expl_fb():
    fig = closed_loop("Reference compared with a sensed output, with a disturbance at the plant output", disturbance=True)
    alt = "Closed loop with controller, actuator, plant, and sensor, plus a disturbance entering at the output."
    sections = [
        {"heading": "The idea",
         "figure": fig, "figure_alt": alt,
         "body_md": (
             "Open-loop control computes a command from the reference and a model, then sends it. "
             "A valve, a heater, or a motor voltage is chosen ahead of time. If the plant matches the model and nothing else pushes on the output, the result is right. "
             "Real plants drift. Loads, grade, and supply changes show up one-for-one at the output, because nothing is watching that output.\n\n"
             "Closed-loop control measures the output, subtracts the measurement from the reference, and lets the controller act on the error. "
             "The plant is the thing being controlled. The actuator turns the command into a physical cause. The sensor reports the output. "
             "The reference is the desired output. A disturbance is an unwanted input, at the actuator or at the output. Sensor noise is a false piece of the measurement.\n\n"
             "The loop can reject disturbances and make the output less sensitive to plant changes. The price is that the loop can oscillate, and sensor noise is driven into the command. "
             "Those tradeoffs are why feedback is designed, not just switched on."
         )},
        {"heading": "Key equations",
         "body_md": (
             "Open loop, with a command \(u\) chosen from the reference,\n"
             r"\[ y = P u + d. \]"
             "\nIf the model says the plant gain is \(P_\\mathrm{model}\), the usual command is \(u = r/P_\\mathrm{model}\). "
             "The true output is then \((P/P_\\mathrm{model}) r + d\).\n\n"
             "Closed loop with the proportional law \(u = K_c(r-y)\) and the same output disturbance,\n"
             r"\[ y = \frac{L}{1+L} r + \frac{1}{1+L} d, \qquad L = K_c P. \]"
             "\nThe tracking factor \(T = L/(1+L)\) multiplies the reference and the sensor noise. "
             "The sensitivity \(S = 1/(1+L)\) multiplies an output disturbance and, approximately, a fractional plant change. "
             "Large \(L\) makes \(T\) near \(1\) and \(S\) near \(0\)."
         )},
        {"heading": "Worked example",
         "body_md": (
             "A flow plant is modeled as \(7\ \\mathrm{L/min}\) per volt. The reference is \(14\ \\mathrm{L/min}\), so the open-loop command is \(2\ \\mathrm{V}\). "
             "If the true gain is \(9\ \\mathrm{L/min}\) per volt, the flow is \(18\ \\mathrm{L/min}\), which is \(4\ \\mathrm{L/min}\) above the reference.\n\n"
             "Close the loop with \(K_c = 3\ \\mathrm{V}\) per \((\mathrm{L/min})\). On the model gain the loop gain is \(21\), and the flow is \(13.36\ \\mathrm{L/min}\). "
             "An extra \(4.4\ \\mathrm{L/min}\) of output disturbance contributes only \(0.20\ \\mathrm{L/min}\). "
             "With the true gain \(9\), the loop gain is \(27\) and the flow is \(13.50\ \\mathrm{L/min}\), still near the reference of \(14\)."
         )},
        {"heading": "Common pitfalls",
         "body_md": (
             "- Treating a calibrated open-loop command as if it rejected disturbances.\n"
             "- Swapping \(S\) and \(T\). Disturbances and plant changes see \(S\). The reference and sensor noise see \(T\).\n"
             "- Forgetting that the actuator and the sensor are real blocks, with their own limits.\n"
             "- Adding the measurement instead of subtracting it. The denominator becomes \(1-L\), and a large loop gain makes the loop run away."
         )},
        {"heading": "Where this leads",
         "body_md": (
             "Block-diagram algebra collapses series and feedback pictures to one gain. "
             "On-off and proportional laws are the first controllers that close the loop. "
             "A vehicle speed loop is the same picture, with drag as the plant and grade as the disturbance."
         )},
    ]
    save_explainer("fb-concepts", "What feedback does: open vs closed loop", sections)
    return words(sections)


# ---------------------------------------------------------------------------
# laplace
# ---------------------------------------------------------------------------

def bank_laplace():
    b = Bank("laplace")
    b.mc(1,
         r"What is the Laplace transform of a unit step (the signal \(1\) for \(t \ge 0\))?",
         [
             r"\(\dfrac{1}{s}\)",
             r"\(\dfrac{1}{s+1}\)",
             r"\(s\)",
             r"\(\dfrac{1}{s^2}\)",
         ], 0,
         r"Integrate \(\int_0^\infty e^{-st}\,dt = 1/s\), for \(\mathrm{Re}(s)>0\). "
         r"\(1/(s+1)\) is the transform of \(e^{-t}\). \(1/s^2\) is the transform of a unit ramp. "
         r"Multiplying by \(s\) is what a derivative does to a transform, not the transform of a step.",
         step_shape("Unit step and a smooth rise toward a constant"),
         "A curve that rises from zero and levels off.")
    b.num(1,
          r"A signal has transform \(F(s) = \dfrac{8}{s(s+4)}\). Every pole of \(sF(s)\) is in the left half-plane. What is \(\lim_{t \to \infty} f(t)\)?",
          2.0, "1",
          r"The final-value theorem says the limit is \(\lim_{s \to 0} s F(s) = \lim_{s \to 0} 8/(s+4) = 8/4 = 2\). "
          r"Partial fractions give \(F = 2/s - 2/(s+4)\), so \(f(t) = 2 - 2e^{-4t}\), which settles at \(2\)."
          "\n• \(8/s\) at \(s = 0\) is undefined. The factor of \(s\) in the theorem cancels the pole at the origin first.\n"
          "• \(8\) forgets to evaluate the remaining factor at \(s = 0\).\n"
          "• \(4\) is the pole, not the final value.",
          step_shape("Smooth rise toward a constant final level", tau=0.25, goal=1),
          "A curve that rises quickly and then flattens.")
    b.mc(1,
         r"A signal \(y(t)\) has transform \(Y(s)\) and initial value \(y(0)\). What is the transform of \(\dot y\)?",
         [
             r"\(sY(s) + y(0)\)",
             r"\(sY(s) - y(0)\)",
             r"\(Y(s)/s\)",
             r"\(sY(s)\)",
         ], 1,
         r"Integration by parts on \(\int_0^\infty \dot y\, e^{-st}\,dt\) produces \(sY(s) - y(0)\). "
         r"The sign on \(y(0)\) is a minus: the initial value is subtracted, not added. "
         r"\(Y/s\) is the integral rule. Dropping \(y(0)\) is legitimate only when the signal starts at rest.",
         decay_shape("A signal that starts away from zero and decays"),
         "A decaying curve that starts above zero.")
    b.num(2,
          r"The ODE \(\dot y + 3y = 6\) has \(y(0) = 0\). What value does \(y\) settle to?",
          2.0, "1",
          r"At rest \(\dot y = 0\), so \(3y = 6\) and \(y = 2\). By transforms, \(sY + 3Y = 6/s\), \(Y = 6/(s(s+3))\), and \(\lim sY = 6/3 = 2\). "
          r"The time solution is \(y = 2(1-e^{-3t})\)."
          "\n• \(6\) is the input, not the steady output. The steady gain of this ODE is \(1/3\).\n"
          "• \(3\) is the coefficient of \(y\), not the steady value.\n"
          "• \(18\) multiplies the input by the coefficient instead of dividing.",
          step_shape("First-order rise toward a steady value", tau=1 / 3),
          "A curve rising toward a horizontal asymptote.")
    b.mc(2,
         r"What is the Laplace transform of \(\sin(5t)\)?",
         [
             r"\(\dfrac{1}{s+5}\)",
             r"\(\dfrac{s}{s^2+25}\)",
             r"\(\dfrac{5}{s^2+25}\)",
             r"\(\dfrac{25}{s^2+25}\)",
         ], 2,
         r"\(\mathcal{L}\{\sin \omega t\} = \omega/(s^2+\omega^2)\) with \(\omega = 5\), so the numerator is \(5\) and the constant term under \(s^2\) is \(25\). "
         r"The cosine transform puts \(s\) in the numerator instead. \(1/(s+5)\) is a real exponential. Using \(\omega^2\) in the numerator double-counts the \(25\).",
         sine_shape("One arch of a sine wave and the start of the next"),
         "A sine wave crossing zero at the origin, rising, then falling.")
    b.num(2,
          r"The ODE \(\dot y + 2y = 0\) has \(y(0) = 4\). What is \(y\) at \(t = 0.5\ \mathrm{s}\)?",
          4 * math.exp(-1), "1",
          r"The solution is \(y = 4e^{-2t}\). At \(t = 0.5\), the exponent is \(-1\), so \(y = 4/e = 1.47152\). "
          r"The transform is \(Y = 4/(s+2)\), whose inverse is the same exponential."
          "\n• \(4 \times 0.5 = 2\) multiplies by time instead of exponentiating.\n"
          "• \(4e^{-0.5} = 2.426\) uses the rate \(1\) instead of \(2\).\n"
          "• \(4e^{-2} = 0.541\) evaluates at \(t = 1\) rather than at \(t = 0.5\).",
          decay_shape("Free decay of a first-order signal"),
          "A smooth decay from a positive start toward zero.")
    b.num(3,
          r"Use the initial-value theorem on \(F(s) = \dfrac{3s+1}{s^2+4s+5}\). What is \(f(0+)\)?",
          3.0, "1",
          r"\(\lim_{s \to \infty} s F(s) = \lim_{s \to \infty} s(3s+1)/(s^2+4s+5) = 3\). "
          r"The inverse is \(e^{-2t}(3\cos t - 5\sin t)\), which equals \(3\) at \(t = 0\)."
          "\n• The constant \(1\) in the numerator is not the initial value.\n"
          "• \(5\), the constant term of the denominator, is not it either.\n"
          "• \(1/5\) would be a final-value misreading. This transform has no pole at the origin, and the initial-value theorem takes \(s\) to infinity, not to zero.",
          splane([(-2, 1), (-2, -1)], [], "Complex poles of a damped oscillator"),
          "s-plane with a complex conjugate pair of poles in the left half-plane.")
    b.mc(3,
         r"\(F(s) = 1/(s-2)\). The algebraic limit \(\lim_{s \to 0} s F(s)\) exists and equals \(0\). What is the final value of \(f(t)\)?",
         [
             r"\(0\), because the formula returned \(0\)",
             r"\(1\), the numerator",
             r"\(-2\), the pole location",
             "The theorem does not apply: \(f(t)\) grows without bound",
         ], 3,
         r"\(f(t) = e^{2t}\) grows. The final-value theorem requires every pole of \(sF(s)\) to lie in the open left half-plane. "
         r"Here \(sF(s) = s/(s-2)\) has a pole at \(+2\), so the algebraic limit \(0\) is not the limit of the signal. "
         r"The numerator \(1\) and the pole location \(-2\) are not values of \(f\).",
         plot(lambda t: math.exp(0.4 * t), 0, 4, "t", "f", "A signal that grows"),
         "A curve that starts near one and bends upward.")
    b.num(3,
          r"\(f(t) = 2e^{-3t}\) for \(t \ge 0\). What is \(\int_0^{\infty} f(t)\,dt\)?",
          2.0 / 3.0, "1",
          r"The transform is \(F(s) = 2/(s+3)\). The integral from \(0\) to \(\infty\) is \(\lim_{s \to 0} F(s) = 2/3 = 0.666667\). "
          r"Directly, \(\int_0^\infty 2e^{-3t}\,dt = 2/3\)."
          "\n• \(2\) is the initial value, not the area. A faster decay has the same starting height and a smaller area.\n"
          "• \(3\) is the decay rate.\n"
          "• \(6\) multiplies them.",
          step_shape("Running accumulation of a decaying pulse", tau=1.0, goal=1.0),
          "A curve that rises and levels off, the shape of an accumulated pulse.")
    b.num(4,
          r"A storage element obeys \(0.4\,\dot y + y = 7u\). The input \(u\) is a unit step, and \(y(0) = 0\). What does \(y\) settle to?",
          7.0, "1",
          r"In steady state the derivative is zero, so \(y = 7\). The transform is \(Y = 7/(s(0.4s+1))\), and \(\lim sY = 7\). "
          r"The \(0.4\) sets the time constant of a first-order step response. It does not change the final level."
          "\n• \(7/0.4 = 17.5\) divides by the time constant.\n"
          "• \(0.4 \times 7 = 2.8\) multiplies by it.\n"
          "• \(1\) is the step height, not the gain.",
          step_shape("First-order step response leveling off", tau=0.4, goal=1),
          "A slow rise that flattens.",
          ["first-order-sys"])
    b.num(4,
          r"A mass-spring-damper at rest obeys \(2\ddot y + 8\dot y + 18 y = u\). The force \(u\) steps to \(9\). Using the final-value theorem on \(Y(s)\), what is the steady displacement, in m?",
          0.5, "m",
          r"With zero initial conditions, \(Y(s) = 9/(s(2s^2+8s+18))\). Then \(\lim_{s \to 0} sY = 9/18 = 0.5\ \mathrm{m}\). "
          r"At rest the spring alone holds the load: \(18y = 9\). Mass and damping affect the transient, which is the subject of second-order response, not the resting point."
          "\n• \(9/8 = 1.125\) divides by the damping.\n"
          "• \(9/2 = 4.5\) divides by the mass.\n"
          "• \(18/9 = 2\) inverts the spring law.",
          mass_spring("Mass, spring, and damper with an applied force"),
          "A mass tied to a wall by a spring and a damper, with a force arrow on the mass.",
          ["second-order-sys"])
    b.num(4,
          r"A controller is \(C(s) = 2 + \dfrac{5}{s}\). At what positive number, in rad/s, does its zero sit?",
          2.5, "rad/s",
          r"\(C(s) = (2s+5)/s\). The zero is the root of \(2s+5 = 0\), so \(s = -2.5\). The positive frequency asked for is \(2.5\ \mathrm{rad/s}\). "
          r"The pole is at the origin, which is what integral action contributes. A later skill uses this zero to shape a PI loop."
          "\n• \(5\) is the integral gain, not the zero.\n"
          "• \(2\) is the proportional gain.\n"
          "• \(5/2\) written as a pole instead of a zero still has magnitude \(2.5\); calling it \(0\) confuses the zero with the pole at the origin.",
          proportional("Controller block that can hold a proportional term and an integral term"),
          "A summing junction and a controller block producing a command from an error.",
          ["pid"])
    b.save()


def expl_laplace():
    sections = [
        {"heading": "The idea",
         "figure": step_shape("A step in time, the signal whose transform is 1/s"),
         "figure_alt": "A curve that rises from rest toward a constant level.",
         "body_md": (
             "The Laplace transform turns a time signal into a function of a complex variable \(s\). "
             "Differentiation becomes multiplication by \(s\), so a linear constant-coefficient differential equation becomes algebra. "
             "That is why the same transform produces transfer functions: solve for the output transform and divide by the input transform, with the initial state at rest.\n\n"
             "The integral runs from the instant we start caring, \(t = 0\), out to infinity: multiply the signal by a decaying exponential \(e^{-st}\) and add it up. "
             "Pick the real part of \(s\) large enough and that decay wins for any signal a stable piece of hardware can produce. "
             "The transform is linear, so the transform of a sum is the sum of the transforms. A delay in time becomes a factor \(e^{-sT}\) in \(s\)."
         )},
        {"heading": "Key equations",
         "body_md": (
             r"\[ \mathcal{L}\{1\} = \frac{1}{s}, \qquad \mathcal{L}\{e^{-at}\} = \frac{1}{s+a}, \qquad \mathcal{L}\{t\} = \frac{1}{s^2}. \]"
             "\n"
             r"\[ \mathcal{L}\{\sin \omega t\} = \frac{\omega}{s^2+\omega^2}, \qquad \mathcal{L}\{\cos \omega t\} = \frac{s}{s^2+\omega^2}. \]"
             "\n"
             r"\[ \mathcal{L}\{\dot f\} = sF(s) - f(0), \qquad \mathcal{L}\!\left\{\int_0^t f(\tau)\,d\tau\right\} = \frac{F(s)}{s}. \]"
             "\nIf every pole of \(sF(s)\) is in the open left half-plane, the final-value theorem says "
             r"\(\lim_{t \to \infty} f(t) = \lim_{s \to 0} sF(s)\). "
             "The initial-value theorem needs no stability caveat of that kind: "
             r"\(\lim_{t \to 0+} f(t) = \lim_{s \to \infty} sF(s)\)."
         )},
        {"heading": "Worked example",
         "body_md": (
             "A level obeys \(\\dot h + 5h = 20 u\) with \(h(0) = 2\) and \(u\) a unit step. "
             "Transform both sides: \(sH - 2 + 5H = 20/s\), so\n"
             r"\[ H(s) = \frac{2(s+10)}{s(s+5)}. \]"
             "\nThe final-value theorem gives \(\\lim sH = 20/5 = 4\). The initial-value theorem gives \(\\lim sH = 2\), matching \(h(0)\). "
             "The time function is \(h(t) = 4 - 2e^{-5t}\). At \(t = 0.2\\ \\mathrm{s}\) the exponent is \(-1\), so the level is \(4 - 2/e = 3.264\)."
         )},
        {"heading": "Common pitfalls",
         "body_md": (
             "- Dropping \(f(0)\) in the derivative rule when the state does not start at rest.\n"
             "- Applying the final-value theorem to a right-half-plane pole. The algebraic limit can exist while the signal diverges.\n"
             "- Swapping sine and cosine. Sine carries \(\\omega\) in the numerator. Cosine carries \(s\).\n"
             "- Using the integral rule on a derivative, or the reverse. One divides by \(s\). The other multiplies by \(s\) and corrects the initial value."
         )},
        {"heading": "Where this leads",
         "body_md": (
             "A first-order step response is the inverse transform of \(K/(s(\\tau s+1))\). "
             "A second-order plant produces a quadratic denominator, and the final-value theorem still reads the resting point off the constant terms. "
             "A PI controller is \(K_p + K_i/s\), a zero over a pole at the origin, which is the same algebra."
         )},
    ]
    save_explainer("laplace", "Laplace transform and its properties", sections, version=2)
    return words(sections)


# ---------------------------------------------------------------------------
# lin-algebra-review
# ---------------------------------------------------------------------------

def bank_lin():
    b = Bank("lin-algebra-review")
    b.mc(1,
         "The rank of a matrix is…",
         [
             "the number of linearly independent columns",
             "always equal to the number of rows, even if two rows match",
             "the product of the diagonal entries",
             "the largest absolute value in the matrix",
         ], 0,
         "Rank is the dimension of the column space, which equals the dimension of the row space. Duplicate rows do not add to it, so rank need not equal the row count. "
         "The product of the diagonal entries is not the determinant once there are off-diagonal terms, and it is not the rank. The largest entry is a size, not a count of independent directions.",
         vectors("Three arrows from one point, one of them in the span of the others"),
         "Three arrows from a common origin. Two point in clearly different directions. The third lies between them.")
    b.num(1,
          r"What is \(\det \begin{bmatrix} 2 & 1 \\ 0 & 3 \end{bmatrix}\)?",
          6.0, "1",
          r"For \(\begin{bmatrix} a & b \\ c & d \end{bmatrix}\) the determinant is \(ad-bc = 2\cdot 3 - 1\cdot 0 = 6\). "
          r"It is also the product of the eigenvalues. This matrix is triangular, so those eigenvalues are the diagonal entries \(2\) and \(3\)."
          "\n• \(2+3 = 5\) is the trace, the sum of the eigenvalues, not the product.\n"
          "• \(2 \times 1 \times 3 = 6\) happens to match only because the off-diagonal \(0\) drops out. Including a nonzero \(c\) that way would be wrong.\n"
          "• \(1\) is an entry, not the determinant.",
          matrix_fig(["2   1", "0   3"], "A 2 by 2 matrix"),
          "A 2 by 2 matrix with first row 2, 1 and second row 0, 3.")
    b.mc(1,
         "The null space of a matrix \(A\) is the set of vectors \(x\) such that…",
         [
             "\(x = Av\) for some vector \(v\)",
             "\(Ax = 0\)",
             "\(x\) is an eigenvalue of \(A\)",
             "\(x\) is a row of \(A\)",
         ], 1,
         "The null space is every \(x\) that \(A\) sends to the zero vector. The set of all \(Av\) is the column space, a different object. "
         "Eigenvalues are scalars, not the vectors in the null space, though a zero eigenvalue means the null space is nontrivial. A row of \(A\) is not, in general, sent to zero.",
         matrix_fig(["1   2", "2   4"], "A matrix with proportional rows"),
         "A 2 by 2 matrix whose second row is twice the first.")
    b.num(2,
          r"What is the larger eigenvalue of \(\begin{bmatrix} 4 & 1 \\ 2 & 3 \end{bmatrix}\)?",
          5.0, "1",
          r"The trace is \(7\) and the determinant is \(12-2 = 10\). The characteristic polynomial is \(\lambda^2 - 7\lambda + 10 = (\lambda-5)(\lambda-2)\). "
          r"The eigenvalues are \(5\) and \(2\). The larger one is \(5\)."
          "\n• \(7\) is the trace, the sum, not the larger root.\n"
          "• \(10\) is the determinant, the product.\n"
          "• \(2\) is the other eigenvalue.",
          matrix_fig(["4   1", "2   3"], "A 2 by 2 matrix with a full set of entries"),
          "A 2 by 2 matrix with first row 4, 1 and second row 2, 3.")
    b.mc(2,
         "If \(B = P^{-1} A P\) with \(P\) invertible, what must \(A\) and \(B\) share?",
         [
             "The same eigenvectors, written in the same coordinates",
             "Every entry, so \(B\) equals \(A\)",
             "The same eigenvalues",
             "Only the determinant. The eigenvalues can change",
         ], 2,
         r"This is a similarity transform, a change of coordinates. If \(Av = \lambda v\), then \(B(P^{-1}v) = \lambda (P^{-1}v)\). The eigenvalues match. The eigenvectors are the same geometric directions only after they are rewritten in the new coordinates. "
         r"The matrices are equal only when \(P\) commutes in a trivial way. The determinant is preserved because it is the product of the eigenvalues, so preserving the determinant is weaker than, and a consequence of, preserving the eigenvalues.",
         eigen_plane("A complex plane with two marks on the real axis"),
         "Real and imaginary axes with two cross marks on the real axis, one on each side of the origin.")
    b.num(2,
          r"How many dimensions does the null space of \(\begin{bmatrix} 1 & 2 \\ 2 & 4 \end{bmatrix}\) have?",
          1.0, "1",
          r"The second row is twice the first, so the rank is \(1\). A \(2\)-column matrix then has nullity \(2 - 1 = 1\). "
          r"One null vector is \((2,-1)\), since \(1\cdot 2 + 2\cdot(-1) = 0\). It is not the zero matrix, so the nullity is not \(2\)."
          "\n• \(0\) would mean the two columns are independent, but the second column is twice the first.\n"
          "• \(2\) would mean every vector is sent to zero.\n"
          "• \(4\) is an entry, not a dimension.",
          matrix_fig(["1   2", "2   4"], "Two proportional rows"),
          "A 2 by 2 matrix with rows 1, 2 and 2, 4.")
    b.num(3,
          r"Solve \(\begin{bmatrix} 3 & 1 \\ 1 & 2 \end{bmatrix}\begin{bmatrix} x \\ y \end{bmatrix} = \begin{bmatrix} 5 \\ 4 \end{bmatrix}\). What is \(x\)?",
          1.2, "1",
          r"The equations are \(3x + y = 5\) and \(x + 2y = 4\). From the second, \(x = 4 - 2y\). Substitute: \(3(4-2y) + y = 5\), so \(12 - 5y = 5\), \(y = 1.4\), and \(x = 4 - 2.8 = 1.2\). "
          r"Check: \(3(1.2)+1.4 = 5\) and \(1.2+2(1.4) = 4\)."
          "\n• \(1.4\) is \(y\), not \(x\).\n"
          "• \(5/3 = 1.667\) drops the second unknown.\n"
          "• \(4/2 = 2\) does the same with the other equation.",
          matrix_fig(["3   1", "1   2"], "Coefficient matrix of a 2 by 2 linear system"),
          "A 2 by 2 matrix with first row 3, 1 and second row 1, 2.")
    b.mc(3,
         r"A \(2 \times 2\) matrix has trace \(5\) and determinant \(6\). Which polynomial is \(\det(A - \lambda I)\), up to the conventional sign that makes the leading term \(+\lambda^2\)? More usefully: the characteristic polynomial \(\det(\lambda I - A)\) is…",
         [
             r"\(\lambda^2 + 5\lambda + 6\)",
             r"\(\lambda^2 - 6\lambda + 5\)",
             r"\(\lambda^2 - 5\lambda - 6\)",
             r"\(\lambda^2 - 5\lambda + 6\)",
         ], 3,
         r"\(\det(\lambda I - A) = \lambda^2 - (\mathrm{tr}\, A)\lambda + \det(A)\). With trace \(5\) and determinant \(6\) that is \(\lambda^2 - 5\lambda + 6\). "
         r"A plus sign on the trace term flips every eigenvalue's sign. Swapping trace and determinant mixes the sum of the roots with their product. A minus on the determinant makes the product of the roots negative, which a positive determinant forbids.",
         eigen_plane("Real axis where eigenvalues of a 2 by 2 matrix would be marked"),
         "Axes labeled real and imaginary, with the real axis drawn as the place eigenvalues can sit.")
    b.num(3,
          r"The eigenvalues of \(\begin{bmatrix} 0 & -2 \\ 1 & -3 \end{bmatrix}\) are real and negative. Which one is closer to zero?",
          -1.0, "1",
          r"The trace is \(-3\) and the determinant is \(2\). Then \(\lambda^2 + 3\lambda + 2 = (\lambda+1)(\lambda+2)\). The roots are \(-1\) and \(-2\). The one closer to zero is \(-1\)."
          "\n• \(-2\) is the faster mode.\n"
          "• \(-3\) is the trace, the sum of the roots.\n"
          "• \(+1\) flips the sign. Both roots are in the left half-plane.",
          matrix_fig(["0   -2", "1   -3"], "A 2 by 2 matrix with a zero in the corner"),
          "A 2 by 2 matrix with first row 0, -2 and second row 1, -3.")
    b.num(4,
          r"For \(A = \begin{bmatrix} 0 & 1 \\ 0 & -2 \end{bmatrix}\) and \(B = \begin{bmatrix} 0 \\ 1 \end{bmatrix}\), the controllability matrix is \(\begin{bmatrix} B & AB \end{bmatrix}\). What is its rank?",
          2.0, "1",
          r"\(AB = \begin{bmatrix} 1 \\ -2 \end{bmatrix}\), so the controllability matrix is \(\begin{bmatrix} 0 & 1 \\ 1 & -2 \end{bmatrix}\). Its determinant is \(-1\), not zero, so the rank is \(2\). "
          r"Full rank is the reachability test for a two-state linear system.",
          matrix_fig(["0   1", "1  -2"], "A 2 by 2 controllability matrix"),
          "A 2 by 2 matrix with first row 0, 1 and second row 1, -2.",
          ["reachability"])
    b.num(4,
          r"For \(A = \begin{bmatrix} -1 & 0 \\ 0 & -3 \end{bmatrix}\) and \(C = \begin{bmatrix} 1 & 0 \end{bmatrix}\), the observability matrix stacks \(C\) over \(CA\). What is its rank?",
          1.0, "1",
          r"\(CA = \begin{bmatrix} -1 & 0 \end{bmatrix}\). Stacking gives \(\begin{bmatrix} 1 & 0 \\ -1 & 0 \end{bmatrix}\). The second row is \(-1\) times the first, and the second column is zero, so the rank is \(1\), not \(2\). "
          r"A rank short of the state dimension means the pair is not observable: the mode at \(-3\) never appears in the output.",
          matrix_fig(["1   0", "-1  0"], "A 2 by 2 observability matrix with a zero column"),
          "A 2 by 2 matrix with first row 1, 0 and second row -1, 0.",
          ["observability"])
    b.num(4,
          r"Pole placement wants the closed-loop characteristic polynomial \((s+2)(s+5)\). What is the coefficient of \(s\)?",
          7.0, "1",
          r"\((s+2)(s+5) = s^2 + 7s + 10\). The coefficient of \(s\) is the sum of the desired poles, \(2+5 = 7\). "
          r"State feedback chooses a gain so the closed-loop matrix has exactly this characteristic polynomial."
          "\n• \(10\) is the constant term, the product of the poles.\n"
          "• \(2\) or \(5\) is one pole, not the sum.\n"
          "• \(-7\) flips the sign that the monic polynomial \(\det(sI - A)\) uses.",
          eigen_plane("Left half-plane, where assigned closed-loop poles are placed"),
          "Real and imaginary axes. The left half of the real axis is the side on which stable poles sit.",
          ["state-feedback"])
    b.save()


def expl_lin():
    sections = [
        {"heading": "The idea",
         "figure": vectors("Two independent arrows and a third arrow in their plane"),
         "figure_alt": "Three arrows from one origin in a plane. Two point in different directions.",
         "body_md": (
             "Four facts from linear algebra do almost all of the bookkeeping for linear state models, and none of them requires a particular physical plant. "
             "Rank counts independent directions. The null space is every vector a matrix sends to zero. "
             "Eigenvalues and eigenvectors describe directions the matrix only stretches. "
             "A similarity \(P^{-1}AP\) changes coordinates and leaves the eigenvalues alone, so the natural modes do not depend on which variables were called the states.\n\n"
             "For a square matrix the rank-nullity theorem says rank plus the dimension of the null space equals the number of columns. "
             "A matrix with a zero eigenvalue is exactly a matrix with a nontrivial null space. "
             "That single link is why a controllability or observability matrix is tested by rank: a lost direction is a mode you cannot reach or cannot see."
         )},
        {"heading": "Key equations",
         "body_md": (
             r"For \(A = \begin{bmatrix} a & b \\ c & d \end{bmatrix}\),"
             "\n"
             r"\[ \det A = ad - bc, \qquad \mathrm{tr}\, A = a + d. \]"
             "\nEigenvalues solve \(\\det(\\lambda I - A) = 0\), which for \(2 \\times 2\) is\n"
             r"\[ \lambda^2 - (\mathrm{tr}\, A)\,\lambda + \det A = 0. \]"
             "\nThe sum of the eigenvalues is the trace. Their product is the determinant. "
             "A nonzero vector \(v\) is an eigenvector when \(Av = \\lambda v\)."
         )},
        {"heading": "Worked example",
         "body_md": (
             r"Take \(A = \begin{bmatrix} 5 & 2 \\ 1 & 4 \end{bmatrix}\). The trace is \(9\) and the determinant is \(20 - 2 = 18\). "
             r"The characteristic polynomial is \(\lambda^2 - 9\lambda + 18 = (\lambda - 6)(\lambda - 3)\). The eigenvalues are \(6\) and \(3\). "
             r"Check: \(A\begin{bmatrix} 2 \\ 1 \end{bmatrix} = \begin{bmatrix} 12 \\ 6 \end{bmatrix} = 6\begin{bmatrix} 2 \\ 1 \end{bmatrix}\), and "
             r"\(A\begin{bmatrix} 1 \\ -1 \end{bmatrix} = \begin{bmatrix} 3 \\ -3 \end{bmatrix}\)."
             "\n\n"
             r"Separately, \(B = \begin{bmatrix} 2 & 6 \\ 1 & 3 \end{bmatrix}\) has determinant \(0\), rank \(1\), and null vector \(\begin{bmatrix} 3 \\ -1 \end{bmatrix}\). "
             r"And \(C\begin{bmatrix} x \\ y \end{bmatrix} = \begin{bmatrix} 7 \\ 8 \end{bmatrix}\) with \(C = \begin{bmatrix} 5 & 1 \\ 2 & 3 \end{bmatrix}\) "
             r"gives \(x = 1\), \(y = 2\): from \(5x + y = 7\) and \(2x + 3y = 8\), elimination produces \(13y = 26\)."
         )},
        {"heading": "Common pitfalls",
         "body_md": (
             "- Writing \(\\lambda^2 + (\\mathrm{tr})\\lambda + \\det\). The trace term is subtracted in \(\\det(\\lambda I - A)\).\n"
             "- Calling a matrix full rank because no entry is zero. A matrix can have every entry nonzero and still have rank \(1\).\n"
             "- Confusing the column space (everything \(A\) can produce) with the null space (everything \(A\) kills).\n"
             "- Expecting a change of coordinates to change the eigenvalues. It changes the eigenvectors' coordinates, not the eigenvalues."
         )},
        {"heading": "Where this leads",
         "body_md": (
             "Reachability stacks the columns \(B, AB, A^2B, \\ldots\) and asks whether the rank equals the number of states. "
             "Observability stacks \(C, CA, CA^2, \\ldots\) and asks the same question. "
             "Pole placement chooses a gain so the closed-loop matrix has a characteristic polynomial you picked. "
             "The coefficient of \(s\) in that monic polynomial is the sum of the desired poles."
         )},
    ]
    save_explainer("lin-algebra-review", "Linear algebra for state space", sections)
    return words(sections)


# ---------------------------------------------------------------------------
# min-phase
# ---------------------------------------------------------------------------

def bank_min():
    b = Bank("min-phase")
    b.mc(1,
         "A minimum-phase loop gain holds a slope of \(-40\\ \\mathrm{dB}\) per decade across a wide band around crossover. About what phase does that slope imply?",
         [
             r"about \(-180^\circ\)",
             r"about \(-90^\circ\)",
             r"about \(-270^\circ\)",
             r"about \(0^\circ\), because phase is set by the gain at one frequency, not by the slope",
         ], 0,
         "For a minimum-phase frequency response, a slope of \(-20n\\ \\mathrm{dB}\) per decade, held over a wide band, corresponds to a phase near \(-90n\) degrees. "
         "Here \(n = 2\), so the phase is near \(-180^\\circ\). A single pole (\(n = 1\)) would be near \(-90^\\circ\), and three poles near \(-270^\\circ\). "
         "The phase tracks the slope, not the absolute gain. The rule fails if the system has a right-half-plane zero or a delay: those add lag the magnitude plot does not show.",
         bode_slope("Magnitude falling, then falling steeper, with the steeper region marked -40"),
         "A Bode magnitude sketch that is shallow, then steeper. The steeper region is marked -40. No phase axis is shown.")
    b.num(1,
          r"A pure delay of \(0.02\ \mathrm{s}\) has frequency response \(e^{-j\omega T}\). What is its phase lag at \(\omega = 50\ \mathrm{rad/s}\), in degrees? Give a positive number.",
          math.degrees(50 * 0.02), "deg",
          r"The phase is \(-\omega T\) radians. \(\omega T = 50 \times 0.02 = 1\) radian, and \(1 \times 180/\pi = 57.2958\) degrees of lag. "
          r"The magnitude of a delay is \(1\) at every frequency, so a magnitude plot cannot see this lag."
          "\n• \(50 \\times 0.02 = 1\) leaves the answer in radians.\n"
          "• \(0.02 \\times 180/\\pi = 1.15\) forgets to multiply by \(\\omega\).\n"
          "• \(360 \\times 0.02 = 7.2\) treats the delay as a fraction of a one-second period.",
          delay_blocks("A block that delays its input"),
          "A single block on a signal path, labeled as a delay.")
    b.mc(1,
         "You may multiply a transfer function by one of the following without changing its magnitude Bode plot. Which choice adds phase lag?",
         [
             r"Multiplying by \(s+z\) for \(z>0\), a new left-half-plane zero",
             r"Multiplying by \(\dfrac{z-s}{z+s}\) for \(z>0\)",
             r"Multiplying by a positive constant gain",
             r"Multiplying by \(\dfrac{s+z}{z-s}\) and then taking the magnitude only",
         ], 1,
         r"\((z-s)/(z+s)\) is an all-pass: its magnitude is \(1\) at every imaginary \(s = j\omega\), and its phase is \(-2\tan^{-1}(\omega/z)\), which is lag. "
         r"A new left-half-plane zero \((s+z)\) raises the magnitude by \(20\ \mathrm{dB}\) per decade and adds phase lead, not lag. "
         r"A positive constant changes the magnitude by a fixed number of decibels and adds no phase. "
         r"Looking only at the magnitude of the reciprocal all-pass throws away exactly the phase the question is about.",
         splane([], [( -3, 0), (3, 0)], "One zero in each half-plane"),
         "s-plane with the imaginary axis drawn and one open circle in each half-plane.")
    b.num(2,
          r"The all-pass \((7-s)/(7+s)\) is evaluated at \(\omega = 14\ \mathrm{rad/s}\). What is its phase, in degrees? Give the signed number.",
          math.degrees(math.atan2(-14, 7) - math.atan2(14, 7)), "deg",
          r"At \(s = j14\), the numerator \(7-j14\) has angle \(\tan^{-1}(-14/7) = \tan^{-1}(-2)\), and the denominator \(7+j14\) has the opposite angle. "
          r"The phase is \(-2\tan^{-1}(2) = -126.870\) degrees. Equivalently, a delay-free all-pass of this form contributes \(-2\tan^{-1}(\omega/z)\)."
          "\n• \(-63.4\) degrees counts only one of the two factors.\n"
          "• \(+126.9\) flips the sign, which would be lead.\n"
          "• \(-90\) would be the phase at \(\\omega = 7\), the corner, not at twice that frequency.",
          delay_blocks("An all-pass block on a signal path"),
          "A block in series on a signal path.")
    b.mc(2,
         "Which transfer function is minimum phase?",
         [
             r"\(\dfrac{s-3}{(s+1)(s+8)}\)",
             r"\(\dfrac{e^{-0.1 s}}{s+1}\)",
             r"\(\dfrac{s+3}{(s+1)(s+8)}\)",
             r"\(\dfrac{3-s}{s+3}\)",
         ], 2,
         "Minimum phase means every zero is in the open left half-plane and there is no time delay. "
         r"\((s+3)/((s+1)(s+8))\) has its only zero at \(-3\). "
         r"\((s-3)/((s+1)(s+8))\) has a zero at \(+3\). "
         r"A factor \(e^{-0.1 s}\) is a delay, which adds lag at every frequency and is not minimum phase. "
         r"\((3-s)/(s+3)\) is an all-pass with a right-half-plane zero.",
         splane([(-1, 0), (-8, 0)], [(-3, 0)], "Poles and a zero, all in the left half-plane"),
         "s-plane with two poles and one zero, all on the negative real axis.")
    b.num(2,
          r"\(H(s) = \dfrac{s+5}{s+20}\). What is the phase of \(H(j5)\), in degrees? Give the signed number.",
          math.degrees(math.atan2(5, 5) - math.atan2(5, 20)), "deg",
          r"The zero at \(-5\) contributes \(\tan^{-1}(5/5) = 45^\circ\). The pole at \(-20\) contributes \(-\tan^{-1}(5/20) = -14.036^\circ\). "
          r"The sum is \(+30.964\) degrees. Both factors are minimum phase, so the zero's lead is only partly cancelled by a pole that is still well above this frequency."
          "\n• \(45\) degrees keeps the zero and forgets the pole.\n"
          "• \(-45\) degrees gives the zero the sign of a right-half-plane zero.\n"
          "• \(14\) degrees is only the pole's contribution.",
          bode_slope("Magnitude that is flat, then rises through a zero before a later pole"),
          "A magnitude sketch that changes slope. No phase numbers are printed.")
    b.num(3,
          r"\(H(s) = \dfrac{10}{s(s+10)}\). What is the phase of \(H(j1)\), in degrees? Give the signed number.",
          math.degrees(cmath_phase_10()), "deg",
          r"At \(s = j\), the denominator is \(j(10+j) = -1 + 10j\). The angle of \(-1+10j\) is \(\tan^{-1}(10/1)\) measured from the negative real axis, \(180^\circ - 84.289^\circ = 95.711^\circ\). "
          r"The numerator is positive, so the phase of \(H\) is \(-95.711\) degrees. "
          r"A pure \(1/s\) would contribute exactly \(-90^\circ\). The extra pole at \(-10\) has only begun to add lag at \(\omega = 1\)."
          "\n• \(-90\) ignores the pole at \(-10\).\n"
          "• \(-84.3\) uses \(\tan^{-1}(10)\) with the wrong quadrant, as if the real part were positive.\n"
          "• \(-180\) would be the high-frequency phase, two poles past both corners.",
          bode_slope("Magnitude with a low-frequency slope and a steeper high-frequency slope"),
          "A Bode magnitude that starts with a gentle negative slope and then steepens.")
    b.mc(3,
         "A step response first moves opposite the direction it finally settles. Which feature produces that inverse response?",
         [
             "A left-half-plane zero, which adds a derivative kick of the same sign as the final value",
             "Extra damping, which slows the rise but does not reverse it",
             "A pure time delay, which shifts the whole response later",
             "A right-half-plane zero",
         ], 3,
         "A right-half-plane zero makes the high-frequency gain opposite in sign to the low-frequency gain, so the first motion opposes the final value. "
         "A left-half-plane zero can add an initial kick, but of the same sign as the settling value. "
         "Damping changes speed and overshoot, not the initial direction. "
         "A pure delay postpones the response and does not reverse it.",
         inverse_step("Step response that dips below zero before settling positive"),
         "A curve that starts at zero, dips below the axis, then climbs and settles above the axis.")
    b.num(3,
          r"Evaluate the all-pass \((8-s)/(8+s)\) at \(\omega = 4\ \mathrm{rad/s}\). What is its phase, in degrees? Give the signed number.",
          math.degrees(math.atan2(-4, 8) - math.atan2(4, 8)), "deg",
          r"The phase of \((z-s)/(z+s)\) on \(s = j\omega\) is \(-2\tan^{-1}(\omega/z)\). With \(\omega/z = 0.5\), \(\tan^{-1}(0.5) = 26.565^\circ\) and the phase is \(-53.130\) degrees. "
          r"The magnitude is exactly \(1\), so this lag is invisible on a magnitude plot."
          "\n• \(-26.6\) degrees counts one factor.\n"
          "• \(-90\) would require \(\omega = z\).\n"
          "• \(+53.1\) is the phase of the minimum-phase mirror \((s+8)/(8)\), not of this all-pass.",
          delay_blocks("All-pass factor in series"),
          "A series block on a signal path.")
    b.num(4,
          r"Replacing a left-half-plane zero at \(-12\) by a right-half-plane zero at \(+12\) multiplies the transfer function by the all-pass \((12-s)/(12+s)\). At \(\omega = 4\ \mathrm{rad/s}\), how much extra phase does that all-pass add, in degrees? Give the signed number.",
          math.degrees(math.atan2(-4, 12) - math.atan2(4, 12)), "deg",
          r"The extra phase is \(-2\tan^{-1}(4/12) = -2\tan^{-1}(1/3) = -36.870\) degrees. "
          r"That lag is the price of the right-half-plane zero at this frequency. It is a fundamental limit: the magnitude plot is unchanged, but phase margin shrinks, so the usable crossover has to stay well below the zero."
          "\n• \(-18.4\) degrees is a single \(\tan^{-1}(1/3)\).\n"
          "• \(-90\) is the all-pass phase at \(\omega = 12\), not at \(4\).\n"
          "• \(+36.9\) would be lead, which a right-half-plane zero does not provide.",
          splane([], [(12, 0)], "A zero on the positive real axis"),
          "s-plane with one zero to the right of the imaginary axis.",
          ["fund-limits"])
    b.num(4,
          r"A design plans to cross over at \(40\ \mathrm{rad/s}\) and must live with a \(5\ \mathrm{ms}\) delay. How many degrees of phase lag does that delay add at crossover? Give a positive number.",
          math.degrees(40 * 0.005), "deg",
          r"Lag is \(\omega T\) radians: \(40 \times 0.005 = 0.2\) radian, times \(180/\pi\), is \(11.459\) degrees. "
          r"The delay does not change \(|L|\). It only spends phase margin. Keeping that lag small is one of the limits on how high the crossover can sit."
          "\n• \(0.2\) leaves the unit in radians.\n"
          "• \(40/0.005 = 8000\) divides instead of multiplying.\n"
          "• \(5\) is the delay in milliseconds, not the phase.",
          delay_blocks("Delay block ahead of a loop crossover"),
          "A delay block in a signal path.",
          ["fund-limits"])
    b.num(4,
          r"A right-half-plane zero sits at \(+6\). Consider the factor \((6-s)\) alone. What is its phase, in degrees, at \(\omega = 6\ \mathrm{rad/s}\)? Give the signed number.",
          -45.0, "deg",
          r"\(6 - j6\) lies at angle \(\tan^{-1}(-6/6) = -45^\circ\). A left-half-plane zero at \(-6\) would have contributed \(+45^\circ\) at this frequency. "
          r"The \(90^\circ\) gap between those two is the all-pass penalty at the zero's own frequency, and it is why an right-half-plane zero near crossover is expensive.",
          splane([], [(6, 0)], "Right-half-plane zero on the real axis"),
          "s-plane with a single zero on the positive real axis.",
          ["fund-limits"])
    b.save()


def cmath_phase_10():
    import cmath
    return cmath.phase(10 / (1j * (1j + 10)))


def expl_min():
    sections = [
        {"heading": "The idea",
         "figure": bode_slope("Magnitude slope in two regions, the clue a minimum-phase phase curve follows"),
         "figure_alt": "A magnitude curve with a gentle negative slope, then a steeper one. Slope labels are -20 and -40. No phase curve is drawn.",
         "body_md": (
             "On a minimum-phase frequency response, the magnitude slope and the phase are tied together. "
             "A slope of \(-20\\ \\mathrm{dB}\) per decade, held across a wide band, sits near \(-90^\\circ\). "
             "A slope of \(-40\\ \\mathrm{dB}\) per decade sits near \(-180^\\circ\), and \(-60\) near \(-270^\\circ\). "
             "Phase does not snap to the new slope at a corner. It still reflects the slopes in a band around that frequency, so a corner you only just passed still shows the old slope in the phase.\n\n"
             "A system is minimum phase when every zero is in the open left half-plane and there is no time delay. "
             "Hold the magnitude curve fixed and slide a zero across the imaginary axis: the lag grows and the magnitude does not. That is the low-lag placement. "
             "A right-half-plane zero matches the magnitude of its left-half-plane mirror and contributes the opposite phase, toward \(-90^\\circ\) instead of \(+90^\\circ\). "
             "The ratio of those two factors is an all-pass of magnitude \(1\). A delay \(e^{-sT}\) also has magnitude \(1\) and adds lag \(\\omega T\) radians. Both eat phase margin as the bandwidth goes up.\n\n"
             "A right-half-plane zero shows up in time as well. The step response first moves the wrong way, then settles in the commanded direction. That initial reversal is inverse response."
         )},
        {"heading": "Key equations",
         "body_md": (
             "Wideband slope of \(-20n\\ \\mathrm{dB}/\\mathrm{decade}\) implies phase near \(-90n\) degrees, for a minimum-phase response.\n"
             r"\[ \frac{z-s}{z+s}\ \text{on}\ s = j\omega \quad\text{has magnitude}\ 1\ \text{and phase}\ -2\tan^{-1}(\omega/z). \]"
             "\nA delay of \(T\) seconds has phase \(-\omega T\) radians. "
             "The gap between a right-half-plane zero and its left-half-plane mirror, at the frequency \(\\omega = z\), is \(90^\\circ\) of extra lag."
         )},
        {"heading": "Worked example",
         "body_md": (
             "Take \(H(s) = (10 - s)/(s + 4)\) at \(\\omega = 7\ \\mathrm{rad/s}\). "
             "The numerator magnitude is \(\\sqrt{10^2 + 7^2} = \\sqrt{149}\) and the denominator magnitude is \(\\sqrt{4^2 + 7^2} = \\sqrt{65}\), so \(|H| = 1.514\). "
             "The numerator angle is \(\\tan^{-1}(-7/10)\) and the denominator angle is \(\\tan^{-1}(7/4)\).\n\n"
             "Compare the right-half-plane zero with a left-half-plane zero at \(-10\). The mirror would have contributed \(+\\tan^{-1}(7/10)\) instead of \(-\\tan^{-1}(7/10)\). "
             "The difference is the all-pass phase \(-2\\tan^{-1}(7/10) = -69.98^\\circ\). "
             "A separate \(12\\ \\mathrm{ms}\) delay at \(25\\ \\mathrm{rad/s}\) adds another \(0.3\) radian, which is \(17.19^\\circ\), with no change in magnitude."
         )},
        {"heading": "Common pitfalls",
         "body_md": (
             "- Reading phase off the magnitude slope when the system has a right-half-plane zero or a delay. The slope rule is only for minimum-phase systems.\n"
             "- Treating a right-half-plane zero as an unstable pole. Poles in the right half-plane make the free response grow. Zeros there do not, by themselves.\n"
             "- Swapping the sign of the zero's phase. Left-half-plane zeros lead. Right-half-plane zeros lag.\n"
             "- Expecting the phase to jump the instant the magnitude slope changes. The phase moves gradually, over about a decade on either side of a corner."
         )},
        {"heading": "Where this leads",
         "body_md": (
             "Feedback runs into this tie as a design limit. An right-half-plane zero or a delay adds lag that no magnitude shaping can remove. "
             "Crossover has to stay well below that zero, and well below \(1/T\) for a delay, if phase margin is still required. "
             "A steeper loop slope near crossover costs the same margin, which is why loop shaping and the waterbed constraint are the next questions."
         )},
    ]
    save_explainer("min-phase", "Bode gain-phase relations and minimum-phase systems", sections, version=2)
    return words(sections)


# ---------------------------------------------------------------------------
# ode-model
# ---------------------------------------------------------------------------

def bank_ode():
    b = Bank("ode-model")
    b.mc(1,
         "A capacitor has capacitance \(C\) and voltage \(v\) across it. Which relation is the element law?",
         [
             r"\(i = C\,\dfrac{dv}{dt}\)",
             r"\(v = C\,\dfrac{di}{dt}\)",
             r"\(i = C v\)",
             r"\(i = v/C\)",
         ], 0,
         "Charge is \(q = Cv\), and current is the derivative of charge, so \(i = C\\,dv/dt\). "
         "The inductor law is the one that puts a derivative on the current: \(v = L\\,di/dt\). Putting \(C\) in that slot mixes the two storage elements. "
         "\(i = Cv\) and \(i = v/C\) are algebraic, like a resistor, and a capacitor does not obey Ohm's law.",
         rc_circuit("Series resistor and capacitor driven by a voltage source"),
         "A voltage source, a series resistor, and a capacitor to the return node.")
    b.num(1,
          r"A \(4\ \mathrm{kg}\) mass slides with viscous friction \(8\ \mathrm{N\,s/m}\) and no spring. A constant \(24\ \mathrm{N}\) force is applied. What speed does it settle to, in m/s?",
          24 / 8, "m/s",
          r"Newton's law along the motion is \(4\dot v = 24 - 8v\). At rest \(\dot v = 0\), so \(v = 24/8 = 3\ \mathrm{m/s}\). "
          r"The mass sets how fast the speed approaches that value. It does not set the value."
          "\n• \(24/4 = 6\) is the initial acceleration in \(\mathrm{m/s^2}\), if the mass starts from rest, not a speed.\n"
          "• \(8/4 = 2\) is the reciprocal of the time constant, in \(\mathrm{s^{-1}}\).\n"
          "• \(24 \times 8\) multiplies the two coefficients.",
          mass_spring("Mass with damping, pulled by a constant force"),
          "A mass connected to a wall through a damper, with a force arrow.")
    b.mc(1,
         r"A tank of surface area \(A\) is filled by a volume flow \(q_\mathrm{in}\). The outflow is linearized as \(q_\mathrm{out} = h/R\). Which height equation matches the volume balance?",
         [
             r"\(\dot h = A\left(q_\mathrm{in} - h/R\right)\)",
             r"\(A\dot h = q_\mathrm{in} - h/R\)",
             r"\(A\dot h = q_\mathrm{in} + h/R\)",
             r"\(\dot h = q_\mathrm{in} - h/R\)",
         ], 1,
         "Volume in the tank is \(Ah\). Its derivative equals inflow minus outflow, so \(A\\dot h = q_\\mathrm{in} - h/R\). "
         "Putting \(A\) on the wrong side makes the time constant \(1/(AR)\) instead of \(AR\). "
         "A plus sign on the outflow says the tank is filling from the drain, which is unstable and physically backwards. "
         "Dropping \(A\) is right only for a tank of unit area.",
         tank("Tank with inflow at the top and outflow at the side"),
         "A tank outline, a dashed height line, an inflow arrow, and an outflow arrow.")
    b.num(2,
          r"A coil \(L = 0.5\ \mathrm{H}\) is in series with \(R = 4\ \Omega\), and \(12\ \mathrm{V}\) is applied. The current starts at \(0\). What current does it settle to, in A?",
          12 / 4, "A",
          r"The loop law is \(0.5\,\dot\imath + 4\imath = 12\). In steady state \(\dot\imath = 0\), so \(\imath = 12/4 = 3\ \mathrm{A}\). "
          r"The inductance sets the time constant \(L/R = 0.125\ \mathrm{s}\). It stores energy. It does not drop DC voltage."
          "\n• \(12/0.5 = 24\) divides by the inductance and gives the initial \(\mathrm{d}\imath/\mathrm{d}t\) in amperes per second.\n"
          "• \(0.5/4 = 0.125\) is the time constant in seconds.\n"
          "• \(12 \times 4 = 48\) multiplies the source by the resistance.",
          rl_circuit("Series inductor and resistor driven by a DC source"),
          "A voltage source in series with an inductor and a resistor.")
    b.mc(2,
         "A mass \(m\) is tied to a fixed wall by a spring \(k\), with no damper. An external force \(u\) pushes the mass, and \(y\) is the stretch of the spring. Which equation is Newton's law?",
         [
             r"\(m\ddot y = u + ky\)",
             r"\(m\dot y = u - ky\)",
             r"\(m\ddot y = u - ky\)",
             r"\(k\ddot y = u - my\)",
         ], 2,
         "The spring force on the mass pulls back toward the unstretched position, so it enters with a minus: \(m\\ddot y = u - ky\). "
         "A plus sign on \(ky\) would push the mass further out as it moves out, which is unstable. "
         "The mass multiplies acceleration, not velocity. Swapping \(m\) and \(k\) assigns inertia to the spring and a spring law to the mass.",
         mass_spring("Mass and spring, no damper drawn in the force balance"),
         "A mass, a spring to a wall, and an applied force.")
    b.num(2,
          r"A rotor has inertia \(J = 0.4\ \mathrm{kg\,m^2}\) and viscous friction \(0.08\ \mathrm{N\,m\,s}\). A constant torque of \(0.16\ \mathrm{N\,m}\) is applied. What speed does it settle to, in rad/s?",
          0.16 / 0.08, "rad/s",
          r"\(J\dot\omega = \tau - b\omega\). In steady state \(b\omega = \tau\), so \(\omega = 0.16/0.08 = 2\ \mathrm{rad/s}\). "
          r"The inertia cancels out of the resting speed. The time constant is \(J/b = 5\ \mathrm{s}\)."
          "\n• \(0.16/0.4 = 0.4\) is the initial angular acceleration, in \(\mathrm{rad/s^2}\).\n"
          "• \(0.4/0.08 = 5\) is the time constant, in seconds.\n"
          "• \(0.16 \times 0.08\) is not a speed.",
          rotor("Rotor with an applied torque"),
          "A disk on a shaft with a torque arrow and a label for inertia.")
    b.num(3,
          r"A tank has surface area \(3\ \mathrm{m^2}\). Outflow is \(q = h/R\) with \(R = 0.4\ \mathrm{m/(m^3/s)}\). Inflow steps to \(0.5\ \mathrm{m^3/s}\). What height does the water settle to, in m?",
          0.5 * 0.4, "m",
          r"Volume balance: \(3\dot h = 0.5 - h/0.4\). At rest, \(h/0.4 = 0.5\), so \(h = 0.2\ \mathrm{m}\). "
          r"The area does not appear in the resting height. It appears in the time constant \(AR = 1.2\ \mathrm{s}\)."
          "\n• \(0.5/3 = 0.167\) divides the inflow by the area. That is a velocity of the free surface only if nothing flows out.\n"
          "• \(0.5 \times 3 = 1.5\) multiplies by the area.\n"
          "• \(0.4\) is the resistance, not the height.",
          tank("Tank whose outflow depends on height"),
          "A tank with inflow and outflow arrows and a marked waterline.")
    b.num(3,
          r"A capacitor \(C = 200\ \mu\mathrm{F}\) charges from a \(10\ \mathrm{V}\) source through \(R = 5\ \mathrm{k\Omega}\). It starts at \(0\ \mathrm{V}\). What is the capacitor voltage at \(t = 1\ \mathrm{s}\), in V?",
          10 * (1 - math.exp(-1)), "V",
          r"The element laws give \(C\dot v = (10 - v)/R\), or \(\dot v + v/(RC) = 10/(RC)\). "
          r"Here \(RC = 5000 \times 200 \times 10^{-6} = 1\ \mathrm{s}\). The solution is \(v = 10(1 - e^{-t})\). "
          r"At \(t = 1\), \(v = 10(1 - e^{-1}) = 6.32121\ \mathrm{V}\)."
          "\n• \(10\) is the final voltage, reached only after several time constants.\n"
          "• \(10/e = 3.679\) is the amount still missing, not the voltage reached.\n"
          "• \(5\) would be a halfway guess. One time constant reaches about \(63\\%\), not \(50\\%\).",
          rc_circuit("Resistor and capacitor in series with a DC source"),
          "A source, a resistor, and a capacitor to ground.")
    b.mc(3,
         "Which pair can be the state of a circuit made of resistors, capacitors, and inductors?",
         [
             "The voltage across a resistor and the current through that same resistor",
             "The source voltage and nothing else",
             "The current through a resistor, because resistors store charge",
             "Inductor current and capacitor voltage",
         ], 3,
         "Inductors store energy in current, and capacitors store energy in voltage. Those are the quantities whose derivatives are fixed by the element laws, so they are the states. "
         "A resistor is algebraic: its voltage and current are locked by Ohm's law and do not need an initial condition. "
         "The source is an input, not a state. Calling a resistor a storage element double-counts a variable the algebra already removed.",
         rl_circuit("Inductor current is one stored quantity"),
         "A source feeding an inductor and a resistor, the inductor marked as the storage element.")
    b.num(4,
          r"States of a mass-spring-damper are position and velocity, in that order. The parameters are \(m = 5\ \mathrm{kg}\), \(b = 4\ \mathrm{N\,s/m}\), \(k = 20\ \mathrm{N/m}\). In \(\dot x = Ax + Bu\), what is the entry in the second row and first column of \(A\)?",
          -20 / 5, "1/s^2",
          r"\(\dot x_1 = x_2\) and \(\dot x_2 = -(k/m) x_1 - (b/m) x_2 + u/m\). The \((2,1)\) entry is \(-k/m = -20/5 = -4\). "
          r"The minus sign is the restoring spring. Writing the state equation this way is the step from a scalar ODE to a state-space model."
          "\n• \(+4\) drops the restoring sign.\n"
          "• \(-20\) forgets to divide by the mass.\n"
          "• \(-b/m = -0.8\) is the \((2,2)\) entry, the damping term.",
          mass_spring("Mass, spring, and damper whose states are position and velocity"),
          "Mass-spring-damper with force and displacement marked.",
          ["state-space-model"])
    b.num(4,
          r"A vehicle of mass \(1200\ \mathrm{kg}\) has linear drag \(80\ \mathrm{N}\) per \((\mathrm{m/s})\). The engine holds a constant \(400\ \mathrm{N}\). There is no grade. What speed does it settle to, in m/s?",
          400 / 80, "m/s",
          r"\(1200\,\dot v = 400 - 80 v\). At rest, \(v = 400/80 = 5\ \mathrm{m/s}\). "
          r"This balance is the plant a cruise-control loop closes. The mass again sets the time constant \(1200/80 = 15\ \mathrm{s}\), not the cruising speed."
          "\n• \(400/1200 = 0.333\) is the initial acceleration in \(\mathrm{m/s^2}\).\n"
          "• \(80/1200\) is the reciprocal time constant.\n"
          "• \(400 \times 80\) is not a speed.",
          car("Vehicle with mass and a driving force"),
          "A vehicle in side view with a drive-force arrow.",
          ["cruise-control"])
    b.num(4,
          r"A tank's time constant is \(8\ \mathrm{s}\). The behavior that matters lasts \(40\ \mathrm{s}\). How many time constants long is that window?",
          40 / 8, "1",
          r"\(40/8 = 5\). Five time constants is long enough that a first-order transient has essentially settled, which is the kind of scaling check a modeling pass makes before adding more detail. "
          r"Keeping the time constant and throwing away the horizon, or the reverse, answers a different question."
          "\n• \(8/40 = 0.2\) inverts the ratio.\n"
          "• \(40 - 8 = 32\) subtracts instead of scaling.\n"
          "• \(40\) counts seconds, not time constants.",
          tank("Tank used as a process whose speed is one time constant"),
          "A tank with inflow and outflow, used as a process to be scaled in time.",
          ["model-method"])
    b.save()


def expl_ode():
    sections = [
        {"heading": "The idea",
         "figure": tank("A tank is a volume balance: area times height rate equals net flow"),
         "figure_alt": "A tank with a waterline, an inflow arrow, and an outflow arrow.",
         "body_md": (
             "A model starts from a balance. For a mass, Newton's second law says mass times acceleration equals the sum of forces. "
             "For a rotor, torque equals inertia times angular acceleration. For a capacitor, current is capacitance times the derivative of voltage. "
             "For an inductor, voltage is inductance times the derivative of current. For a tank, area times the rate of change of height equals inflow minus outflow.\n\n"
             "Each stored quantity becomes a state: velocity, angular velocity, capacitor voltage, inductor current, or height. "
             "Algebraic elements, resistors and linearized orifices, relate effort to flow with no derivative and no initial condition. "
             "Write the derivatives on the left and everything else on the right. "
             "The sign of a restoring element comes from the free-body diagram. A spring pulls back toward the unstretched length. A damper opposes velocity. Outflow leaves the tank. A resistor drops voltage in the direction of the current."
         )},
        {"heading": "Key equations",
         "body_md": (
             r"\[ m\dot v = F - bv, \qquad J\dot\omega = \tau - b\omega. \]"
             "\n"
             r"\[ L\dot\imath = v - R\imath, \qquad C\dot v = (v_s - v)/R. \]"
             "\n"
             r"\[ A\dot h = q_\mathrm{in} - h/R. \]"
             "\nThe steady values are \(F/b\), \(\\tau/b\), \(v/R\), \(v_s\), and \(q_\\mathrm{in} R\). "
             "The time constants are \(m/b\), \(J/b\), \(L/R\), \(RC\), and \(AR\). "
             "Storage elements set the time constants. They cancel out of the steady values."
         )},
        {"heading": "Worked example",
         "body_md": (
             "A pump fills a tank of area \(0.8\ \\mathrm{m^2}\). The outlet is linearized with \(R = 5\ \\mathrm{m}\) per \((\mathrm{m^3/s})\), and the inflow steps from \(0\) to \(0.3\ \\mathrm{m^3/s}\). Height starts at \(0\).\n\n"
             "The balance is \(0.8\\,\\dot h = 0.3 - h/5\). The steady height is \(0.3 \\times 5 = 1.50\ \\mathrm{m}\). "
             "The time constant is \(0.8 \\times 5 = 4\ \\mathrm{s}\), so \(h(t) = 1.50\\,(1 - e^{-t/4})\). "
             "At \(t = 4\ \\mathrm{s}\), one time constant, \(h = 1.50\\,(1 - 1/e) = 0.948\ \\mathrm{m}\).\n\n"
             "Beside it, a coil \(L = 0.4\ \\mathrm{H}\) with \(R = 10\ \\Omega\) is switched onto \(25\ \\mathrm{V}\). "
             "Steady current is \(25/10 = 2.50\ \\mathrm{A}\), and the time constant is \(L/R = 0.04\ \\mathrm{s}\). "
             "The same pattern, a storage element and a resistive drop, produced both numbers."
         )},
        {"heading": "Common pitfalls",
         "body_md": (
             "- Using weight \(mg\) in place of mass. That inserts \(g\) into a time constant where the balance does not have it.\n"
             "- Sign errors on the spring, the damper, or the tank outflow. Those move a stable pole into the right half-plane.\n"
             "- Treating a resistor or a linear orifice as a state. They are algebraic and should be eliminated.\n"
             "- Swapping the time constant. It is \(RC\) and \(L/R\), not \(R/C\) or \(R/L\)."
         )},
        {"heading": "Where this leads",
         "body_md": (
             "Collecting the stored variables produces a state equation \(\\dot x = Ax + Bu\). "
             "A vehicle speed balance, mass times acceleration equals engine force minus drag, is the plant inside a cruise-control loop. "
             "Choosing units, and deciding which effects are large enough to keep over the time window you care about, is the modeling pass that follows."
         )},
    ]
    save_explainer("ode-model", "Modeling with differential equations", sections)
    return words(sections)


def lint():
    banned = re.compile(r"niknejad|åström|aström|astrom|murray|feedback systems|\breader\b|§", re.I)
    problems = []
    for sid in ("fb-concepts", "laplace", "lin-algebra-review", "min-phase", "ode-model"):
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
                if q.get("figure_alt") and banned.search(q["figure_alt"]):
                    problems.append(f"{q['id']} alt banned")
            if q["type"] == "mc":
                idxs.append(q["correct_index"])
        if nfig < 9:
            problems.append(f"{sid} only {nfig} figures")
        # balanced: each index used equally often, or as evenly as a multiple of 4 allows
        if len(idxs) % 4 == 0:
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
    bank_fb()
    bank_laplace()
    bank_lin()
    bank_min()
    bank_ode()
    print("words", "fb", expl_fb(), "laplace", expl_laplace(), "lin", expl_lin(), "min", expl_min(), "ode", expl_ode())
    lint()


if __name__ == "__main__":
    main()
