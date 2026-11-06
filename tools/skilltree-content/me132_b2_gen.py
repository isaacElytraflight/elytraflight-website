#!/usr/bin/env python3
"""Generate ME 132 batch B2 banks and explainers.

Closed-form answers live here. skilltree/verify_me132_b2.py recomputes them
by signal equations, RK4, or a linear solve.
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from templates import block_diagram, mass_spring, matrix_fig, plot, splane, step_response

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

    def q(self, rnd, kind, prompt, explanation, fig=None, alt=None, preview=None, version=1, **kw):
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
        item["version"] = version
        self.qs.append(item)

    def mc(self, rnd, prompt, options, correct, explanation, fig=None, alt=None, preview=None, version=1):
        self.q(rnd, "mc", prompt, explanation, fig, alt, preview, version,
               options=options, correct_index=correct)

    def num(self, rnd, prompt, answer, unit, explanation, fig=None, alt=None, preview=None, version=1):
        self.q(rnd, "numeric", prompt, explanation, fig, alt, preview, version,
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
    text = " ".join(s["body_md"] for s in sections)
    text = re.sub(r"<svg[\s\S]*?</svg>", " ", text)
    text = re.sub(r"\\\(|\\\)|\\\[|\\\]", " ", text)
    text = re.sub(r"\\[a-zA-Z]+", " ", text)
    return len(re.findall(r"[A-Za-z0-9']+", text))


def bank_blocks():
    b = Bank("block-diagram")
    series2 = "Two labeled blocks in a row, with arrows in and out."
    series3 = "Three labeled blocks in a row, with arrows in and out."
    loop = "A forward block and a return path that comes back to the input."
    b.mc(1,
         r"Two blocks sit one after the other. The first multiplies by 6 and the second multiplies by 5. The single block that replaces both multiplies by",
         ["30", "11", "1.2", "6"], 0,
         r"Blocks in series share one signal, so their gains multiply: \(6 \times 5 = 30\). Adding them gives 11, which is the parallel rule. Dividing them gives 1.2. Keeping only 6 drops the second block.",
         block_diagram(["6", "5"], "series blocks", output_label="y"), series2)
    b.num(1,
          r"Two blocks sit in parallel. One multiplies by 4 and the other by 7, and their outputs add. The equivalent gain is",
          11, "1",
          r"Parallel blocks see the same input and their outputs add, so the gain is \(4 + 7 = 11\). Multiplying would give 28, which is the series rule. Subtracting gives \(-3\) or \(3\), and neither block is subtracted here.")
    b.mc(1,
         r"A forward block \(G\) and a return block \(H\) form a negative feedback loop: the return signal is subtracted from the reference. The closed-loop gain from reference to output is",
         [r"\(G + H\)", r"\(\dfrac{G}{1 + GH}\)", r"\(\dfrac{G}{1 - GH}\)", r"\(GH\)"], 1,
         r"Call the error \(e = r - Hy\) and the output \(y = Ge\). Substituting gives \(y = G(r - Hy)\), so \(y(1 + GH) = Gr\) and the gain is \(G/(1+GH)\). \(G+H\) adds the two blocks as if they were in parallel. The minus sign in the denominator is the positive-feedback formula. \(GH\) is the loop gain, not the closed-loop gain.",
         block_diagram(["G"], "negative feedback", feedback="H", input_label="r", output_label="y"), loop)
    b.num(2,
          r"Negative feedback. The forward gain is 8 and the return gain is 0.5. The closed-loop gain is",
          8 / (1 + 8 * 0.5), "1",
          r"The loop product is \(8 \times 0.5 = 4\). Negative feedback puts that product in the denominator: \(8/(1+4) = 1.6\). Using \(1 - 4\) changes the sign of the loop and is the positive-feedback formula. The product 4 itself is the loop gain, and \(8 + 0.5\) adds the blocks.",
          block_diagram(["8"], "forward 8", feedback="0.5", input_label="r", output_label="y"), loop)
    b.num(2,
          r"Three signals are not involved: just two blocks in series, with gains 2.5 and 4. The equivalent gain is",
          2.5 * 4, "1",
          r"Series gains multiply: \(2.5 \times 4 = 10\). Adding gives 6.5. Dividing gives 0.625. The order does not matter for the product, but dropping either factor leaves 2.5 or 4.",
          block_diagram(["2.5", "4"], "two series gains", output_label="y"), series2)
    b.mc(2,
         r"In a negative feedback loop the forward block is \(G\) and the return block is \(H\). Which expression is the loop gain?",
         [r"\(G\)", r"\(\dfrac{G}{1+GH}\)", r"\(GH\)", r"\(H\)"], 2,
         r"Start at the error and walk once around the loop: multiply by \(G\), then by \(H\), and you are back at the summing junction. That product \(GH\) is the loop gain. \(G\) skips the return path. \(G/(1+GH)\) is what the closed loop does to a reference. \(H\) is only the sensor path.",
         block_diagram(["G"], "walk the loop", feedback="H", input_label="e", output_label="y"), loop)
    b.num(3,
          r"The same blocks as a negative loop, but the return signal is added to the reference. Forward gain 2, return gain 0.2. The closed-loop gain is",
          2 / (1 - 2 * 0.2), "1",
          r"Positive feedback adds the return, so \(y = 2(r + 0.2 y)\). Then \(y(1 - 0.4) = 2r\) and the gain is \(2/0.6 = 3.333\). The negative-feedback formula \(2/(1+0.4) = 1.429\) subtracts a signal that this loop adds. The product 0.4 is the loop gain, and \(2 + 0.2\) adds the blocks as if they were side by side.",
          block_diagram(["2"], "positive feedback", feedback="0.2", input_label="r", output_label="y"), loop)
    b.mc(3,
         r"A disturbance adds at the output, after the forward block. The loop gain is \(L\). The fraction of that disturbance still present at the output is",
         [r"\(L\)", r"\(\dfrac{L}{1+L}\)", r"\(1+L\)", r"\(\dfrac{1}{1+L}\)"], 3,
         r"With the reference held at zero, \(y = d - L y\), because the loop sees the output and drives back against it. Then \(y(1+L) = d\), so the fraction is \(1/(1+L)\). \(L\) and \(1+L\) grow as the loop gets stronger, but a stronger loop rejects more of \(d\). \(L/(1+L)\) is the fraction of a reference that gets through, not of a disturbance.")
    b.num(3,
          r"Three blocks in series have gains 2, 3, and 4. The equivalent gain is",
          2 * 3 * 4, "1",
          r"Each block multiplies the signal that leaves the previous one, so the gains multiply: \(2 \times 3 \times 4 = 24\). Adding gives 9. Multiplying only the first pair leaves 6, and only the last pair leaves 12.",
          block_diagram(["2", "3", "4"], "three series blocks", output_label="y"), series3, version=2)
    b.num(4,
          r"A loop you will later write as one transfer function has forward gain 9 and return gain 2, with the return subtracted. The closed-loop gain is",
          9 / (1 + 9 * 2), "1",
          r"The loop gain is \(9 \times 2 = 18\). Negative feedback gives \(9/(1+18) = 9/19 = 0.4737\). The product 18 is the loop gain, not the closed-loop gain. \(9/(1-18)\) flips the feedback sign. \(9+2\) adds the two paths.",
          block_diagram(["9"], "one closed-loop gain", feedback="2", input_label="r", output_label="y"),
          loop, ["loop-tf"])
    b.num(4,
          r"The loop gain is 4. A disturbance adds at the output. The fraction of it that remains is",
          1 / (1 + 4), "1",
          r"Hold the reference at zero. Then \(y = d - 4y\), so \(y = d/5 = 0.2\). The complementary fraction \(4/5 = 0.8\) is how much of a reference would get through, not how much of \(d\) remains. Leaving the 4 un-normalized reports the loop gain itself.",
          block_diagram(["4"], "disturbance at the output", feedback="1", input_label="r", output_label="y"),
          loop, ["sensitivity"])
    b.num(4,
          r"The product you would plot as a loop gain is made of three series blocks, 1.5, 2, and 4. That product is",
          1.5 * 2 * 4, "1",
          r"The loop gain is the product of every block you meet on one trip around the loop. Here that trip is three blocks: \(1.5 \times 2 \times 4 = 12\). Adding gives 7.5. The first pair alone is 3, and the last pair alone is 8.",
          block_diagram(["1.5", "2", "4"], "loop product", output_label="L"),
          series3, ["nyquist"], version=2)
    b.save()


def bank_first():
    b = Bank("first-order-sys")
    rise = "A smooth curve that rises toward a horizontal line."
    pole = "One pole mark on the real axis, left of the origin."
    b.mc(1,
         r"The equation \(6\dot{y} + y = 2u\) is already arranged so the coefficient of \(y\) is 1. The time constant, in seconds, is",
         ["6", "2", "1/6", "1/3"], 0,
         r"Once \(y\) has coefficient 1, the coefficient of \(\dot{y}\) is the time constant, so \(\tau = 6\). The 2 is the DC gain. \(1/6\) is the pole location's magnitude, and \(2/6\) divides the gain by the time constant, which is the initial slope for a unit step, not \(\tau\).",
         step_response("a first-order rise", tau=6, goal=2), rise)
    b.num(1,
          r"The plant \(6\dot{y} + y = 2u\) starts at rest. The input steps to 4 and stays there. The steady output is",
          8, "1",
          r"At steady state the derivative is zero, so \(y = 2u = 2 \times 4 = 8\). The 6 never enters the steady value. Dividing the gain by 6 gives \(4/3\), and multiplying the input by 6 gives 24.",
          step_response("step of a first-order plant", tau=6, goal=8), rise)
    b.num(1,
          r"A first-order step response starts at rest. At \(t\) equal to one time constant, what fraction of the steady value has been reached?",
          1 - math.exp(-1), "1",
          r"From rest, \(y(t) = y_\infty(1 - e^{-t/\tau})\). At \(t = \tau\) the exponent is \(-1\), so the fraction is \(1 - e^{-1} = 0.632\). Half would be a different definition. \(e^{-1} = 0.368\) is the fraction still missing, and \(1 - e^{-2}\) is two time constants.",
          step_response("one time constant of rise", tau=1, goal=1), rise)
    b.num(2,
          r"A free response (input held at 0) starts at \(y(0) = 6\). The time constant is 2 s. The value at \(t = 2\) s is",
          6 * math.exp(-1), "1",
          r"Free motion is \(y(t) = 6 e^{-t/2}\). At \(t = 2\) the exponent is \(-1\), so \(y = 6/e = 2.207\). Using \(t\) itself as the exponent gives \(6e^{-2}\). Halving because one time constant passed gives 3, and that is a straight line, not an exponential.",
          step_response("free decay", fn=lambda t: 6 * math.exp(-t / 2), t_end=8, zero=True),
          "A curve that falls toward zero.")
    b.mc(2,
         r"People sometimes mark 'one time constant' at the halfway point of a step response. For a first-order rise from rest, the output at one time constant is about",
         ["half the steady value", "63% of the steady value", "the steady value", "37% of the steady value"], 1,
         r"\(1 - e^{-1}\) is about 0.632, so about 63% of the gap has been closed. Half would be \(1 - e^{-t/\tau} = 0.5\), which happens at \(t = \tau \ln 2\), earlier than one time constant. The steady value is the limit as \(t \to \infty\). 37% is the fraction still missing, \(e^{-1}\).",
         step_response("fraction of a step", tau=1.4, goal=1), rise)
    b.num(2,
          r"The plant \(4\dot{y} + y = 12u\) starts at rest and \(u\) steps to 1. The steady output is",
          12, "1",
          r"Set the derivative to zero: \(y = 12u = 12\). Dividing by the time constant gives \(12/4 = 3\), which confuses the gain with a slope. Multiplying by 4 gives 48. The time constant affects how long the rise takes, not where it ends.",
          step_response("steady value independent of the time constant", tau=4, goal=12), rise)
    b.num(3,
          r"A time constant is 0.25 s. How many time constants fit in a 1 s window?",
          4, "1",
          r"The count is the window divided by the time constant: \(1/0.25 = 4\). Multiplying the two times gives 0.25, which is one time constant, not a count. Adding them gives 1.25.",
          step_response("several time constants", tau=0.25, goal=1), rise)
    b.mc(3,
         r"A first-order system has time constant \(\tau > 0\). Its pole is at",
         [r"\(+\tau\)", r"\(0\)", r"\(-1/\tau\)", r"\(-\tau\)"], 2,
         r"The free response is \(e^{-t/\tau}\), which is \(e^{pt}\) with \(p = -1/\tau\). The pole is in the left half-plane. \(+\tau\) would grow. \(0\) is an integrator, whose output ramps rather than settling. \(-\tau\) puts the time constant in the exponent without inverting it, so the decay rate is wrong.",
         splane([(-1, 0)], [], "a single left-half pole"), pole)
    b.num(3,
          r"From rest, \(y(t) = 9(1 - e^{-t/3})\). The slope \(\dot{y}\) at \(t = 0\) is",
          3, "1/s",
          r"Differentiate: \(\dot{y} = 9 \cdot (1/3) e^{-t/3}\). At \(t = 0\) the exponential is 1, so the slope is \(9/3 = 3\). The 9 is the steady value, not the slope. \(9 \times 3 = 27\) multiplies by the time constant instead of dividing. \(1/3\) is the decay rate of the missing piece, not the initial slope of this particular step.",
          step_response("initial slope of a rise", tau=3, goal=9), rise)
    b.num(4,
          r"A later second-order plant will settle to the same kind of constant. For the first-order plant \(6\dot{y} + y = 15u\), a unit step in \(u\) settles at",
          15, "1",
          r"The derivative dies out, leaving \(y = 15u = 15\). Dividing by 6 gives 2.5 and treats the time constant as part of the gain. The product \(6 \times 15 = 90\) has the same problem in the other direction.",
          step_response("settling level", tau=6, goal=15), rise, ["second-order-sys"])
    b.num(4,
          r"Step-response specs quote a time constant. For \(1.7\dot{y} + y = 2u\), that time constant is",
          1.7, "s",
          r"With the coefficient of \(y\) equal to 1, \(\tau\) is the coefficient of \(\dot{y}\), so \(\tau = 1.7\) s. The 2 is the DC gain. Their product 3.4 and their ratio \(2/1.7\) mix the gain into the timing.",
          step_response("time constant from the equation", tau=1.7, goal=2), rise, ["step-specs"])
    b.mc(4,
         r"A proportional controller wraps a stable first-order plant. The reference steps and then holds. The error settles at",
         ["zero, because the loop is stable",
          "zero, because a first-order plant already contains an integrator",
          "a ramp that grows without bound",
          "a nonzero constant"], 3,
         r"Proportional control produces a command \(u = K_c(r - y)\). A first-order plant has a finite DC gain and no free integrator, so a constant error is required to hold a constant output. Stability says the error settles, not that it settles at zero. The plant equation \(\tau\dot{y} + y = Ku\) reaches a constant, so the error is not a ramp. An integrator would be \(\dot{y} = Ku\), which this plant is not.",
         block_diagram(["plant"], "proportional loop", feedback="1", input_label="r", output_label="y"),
         "A plant block with a return path to the input.", ["pid"])
    b.save()


def bank_method():
    b = Bank("model-method")
    mech = "A mass with a spring and a damper."
    clock = "A curve used only as a picture of a transient."
    b.mc(1,
         r"You are about to write a model for a control loop. Which quantities become the states?",
         ["The stored quantities that need initial conditions",
          "Every input the actuator can set",
          "Only the quantity printed on the reference display",
          "The disturbances, because they are unknown"], 0,
         r"A state is a stored quantity. You need its initial value, and its derivative is what the differential equation gives you. An input is chosen by the actuator or imposed from outside, so it is \(u\), not \(x\). The reference is a signal the controller compares against the measurement. A disturbance is an extra input, not a state, unless the disturbance itself has dynamics you decide to model.",
         mass_spring("stored energy in a mass and a spring"), mech)
    b.num(1,
          r"A length scale is \(0.4\ \mathrm{m}\) and a velocity scale is \(2\ \mathrm{m/s}\). The time scale formed from those two is",
          0.4 / 2, "s",
          r"Time is length over velocity: \(0.4/2 = 0.2\) s. Multiplying gives \(0.8\ \mathrm{m^2/s}\), which is not a time. Dividing the velocity by the length gives \(5\ \mathrm{s^{-1}}\), a rate, not the time scale.")
    b.mc(1,
         r"A motor's electrical transient dies in a fraction of a millisecond. The loop you care about moves a load over several seconds. A useful model of that loop",
         ["keeps every electrical state, because more states are always safer",
          "can replace the electrical transient by the gain it settles to",
          "drops the mechanical states, because they are slow",
          "uses no states at all"], 1,
         r"The loop never sees the electrical spike, so that state can be replaced by the algebraic gain it settles to. Keeping it is not free: it adds a fast pole the controller will not move. Dropping the mechanical states drops the motion the loop is for. A model with no states cannot accumulate a position or a speed.",
         step_response("a slow transient", tau=2, goal=1), clock)
    b.num(2,
          r"A shaft turns at 1500 revolutions per minute. Its speed in radians per second is",
          1500 * 2 * math.pi / 60, "rad/s",
          r"One revolution is \(2\pi\) radians, and a minute is 60 seconds: \(1500 \times 2\pi/60 = 157.1\). Dividing by 60 alone gives 25 revolutions per second, still not radians. Multiplying by \(2\pi\) and forgetting the 60 leaves the per-minute number. Using \(\pi\) instead of \(2\pi\) is half a revolution.",
          mass_spring("a rotating load, drawn as a mass with drag", spring=False),
          "A mass and a damper, no spring.")
    b.mc(2,
         r"Why divide a differential equation through by its scales before you decide a term is small?",
         ["So every term has the original units and can be checked on a bench",
          "So the initial conditions become 1",
          "So the terms are pure numbers and can be compared with each other",
          "So the time constant becomes the DC gain"], 2,
         r"After scaling, each term is a number. A term near 0.01 can be dropped beside a term near 1. Before scaling, a term in newtons cannot be called smaller than a term in meters. Scaling does not set every initial condition to 1, and it does not swap the time constant with the gain.",
         matrix_fig([["1", "0.02"], ["0", "1"]], "scaled terms of very different size"),
         "A 2 by 2 array with one entry much smaller than the others.")
    b.num(2,
          r"A sensor produces \(0.025\ \mathrm{V}\) per millimeter. A motion of 36 mm produces a voltage of",
          0.025 * 36, "V",
          r"Multiply the sensitivity by the motion: \(0.025 \times 36 = 0.9\) V. Dividing the motion by the sensitivity gives 1440, which is a count of how many 0.025 V steps fit in 36, not a voltage. Adding the two numbers mixes volts-per-millimeter with millimeters.")
    b.num(3,
          r"One stored quantity moves on a 0.04 s scale. Another moves on a 6.4 s scale. The ratio of the slow scale to the fast scale is",
          6.4 / 0.04, "1",
          r"The ratio is \(6.4/0.04 = 160\). The product \(0.256\) is a time squared over a time, not a ratio. The reciprocal \(0.00625\) compares them in the other order.",
          step_response("two widely separated scales", tau=1, goal=1), clock)
    b.mc(3,
         r"The loop must hold a constant reference with no steady error. The model used to design that loop should",
         ["omit every integrator, to keep the order low",
          "replace the plant by its high-frequency slope",
          "ignore the sensor, because the sensor is not the plant",
          "keep a free integrator if the error is supposed to vanish"], 3,
         r"A constant error goes to zero only if something in the loop integrates it. Dropping that integrator makes the design model predict an error the hardware will not have, or hide an error the hardware will have. The high-frequency slope matters for stability margins, not for the constant error. The sensor is inside the loop, so its gain belongs in the model.",
         block_diagram(["integrator"], "a free integrator", output_label="y"),
         "A single block labeled integrator.")
    b.num(3,
          r"A mass is \(1.5\ \mathrm{kg}\) and its acceleration is \(4\ \mathrm{m/s^2}\). The force that goes with those two numbers is",
          1.5 * 4, "N",
          r"Force is mass times acceleration: \(1.5 \times 4 = 6\) N. Adding gives 5.5 and mixes kilograms with meters per second squared. Dividing gives \(2.67\), which is not a force. Multiplying by \(9.81\) as well would be the weight of a different problem.",
          mass_spring("force on a mass", spring=False, damper=False),
          "A mass alone, with no spring and no damper.")
    b.num(4,
          r"A one-state model is \(\dot{y} = 2.4 - 0.3y\). Linearization will be about the resting point. The resting value of \(y\) is",
          2.4 / 0.3, "1",
          r"At rest the derivative is zero, so \(0.3y = 2.4\) and \(y = 8\). The product \(0.72\) multiplies the two coefficients. The difference \(2.1\) subtracts them. Neither is a root of the right-hand side.",
          step_response("settling to a rest value", tau=1 / 0.3, goal=8), clock, ["linearization"])
    b.num(4,
          r"A step test on a one-pole plant reaches about 63% of its steady change at 3.5 s. The time constant you would identify is",
          3.5, "s",
          r"For a first-order rise, 63% of the step happens at one time constant, so the identified \(\tau\) is 3.5 s. Half of that, 1.75 s, is closer to the halfway time \(\tau\ln 2\). Twice 3.5 is two time constants.",
          step_response("measured rise", tau=3.5, goal=1), clock, ["sys-id"])
    b.num(4,
          r"Equilibria of \(\dot{y} = -2y + u\) with the constant input \(u = 5\). The resting \(y\) is",
          5 / 2, "1",
          r"Set \(\dot{y} = 0\): \(2y = 5\), so \(y = 2.5\). The product \(10\) and the difference \(3\) are not roots. Leaving the input as the state forgets the \(-2y\) term.",
          step_response("resting value of a scaled state", tau=0.5, goal=2.5), clock, ["equilibria"])
    b.save()


def bank_pid():
    b = Bank("onoff-pid-intro")
    loop = "A controller block and a plant block, with a return path."
    # Kc=4, P=3, r=10 → y = 120/13, e = 10/13
    y_p = 4 * 3 / (1 + 4 * 3) * 10
    e_p = 10 / (1 + 12)
    b.mc(1,
         r"An on-off controller can command only 0 or full scale. While the error is nonzero it",
         ["holds one of those two commands, not a value in between",
          "produces a command proportional to the error",
          "integrates the error until the error is zero",
          "commands the derivative of the error"], 0,
         r"On-off has two legal outputs. It switches to one or the other according to the sign of the error, and it cannot sit at an intermediate command. A command proportional to the error is P control. Integrating the error is I control. Commanding the derivative is D control.",
         block_diagram(["on/off", "plant"], "two-level command", feedback="1", input_label="r", output_label="y"),
         loop)
    b.num(1,
          r"The switch is stuck on, the plant output sits at 14, and the reference is 9. The error \(r - y\) is",
          9 - 14, "1",
          r"Error is reference minus output: \(9 - 14 = -5\). The negative sign says the output is above the reference, which is why an on-off loop then switches off. The sum 23 and the difference \(14 - 9 = 5\) flip that sign. The product is not an error.",
          step_response("output above the reference", fn=lambda t: 14, t_end=4),
          "A flat line, the output while the switch stays on.")
    b.num(1,
          r"Proportional control, gain 4, on a plant of DC gain 3. The reference steps to 10. The steady output is",
          y_p, "1",
          r"The loop gain is \(4 \times 3 = 12\). The steady output is \(12/(1+12)\) of the reference: \(120/13 = 9.231\). Reporting the error \(10/13\) instead of the output, or the open-loop product \(4 \times 3 \times 10 = 120\), answers a different question.",
          block_diagram(["4", "3"], "proportional loop", feedback="1", input_label="r", output_label="y"),
          loop)
    b.num(2,
          r"Same loop: proportional gain 4, plant DC gain 3, reference 10. The steady error \(r - y\) is",
          e_p, "1",
          r"The error is the reference divided by \(1+L\): \(10/(1+12) = 10/13 = 0.769\). The output \(9.231\) is what remains after you subtract this error from 10. Zero would require an integrator, which this proportional loop does not have.",
          block_diagram(["Kc", "P"], "error of a proportional loop", feedback="1", input_label="r", output_label="y"),
          loop)
    b.mc(2,
         r"A constant reference and a constant disturbance act on a loop. Adding integral action, and no other change, makes the steady error",
         ["larger, because the integrator winds up on a constant",
          "zero, if the loop is still stable",
          "equal to the proportional-only error",
          "a ramp, because the integrator keeps moving"], 1,
         r"An integrator in a stable loop cannot settle while its input, the error, is a nonzero constant. The only steady state is zero error. Windup is what happens when the actuator saturates and the integrator is left running, which is a different regime. The proportional-only error is exactly what the integrator removes. A ramp would mean the loop never reached a steady state.",
         block_diagram(["PI", "plant"], "integral in the forward path", feedback="1", input_label="r", output_label="y"),
         loop)
    b.num(2,
          r"Proportional gain 4, plant DC gain 3, reference held at 0. A disturbance of 2 adds at the output. The steady output is",
          2 / (1 + 12), "1",
          r"The disturbance is divided by \(1+L\): \(2/13 = 0.154\). The loop gain 12 is not the output. \(2 \times 12/13\) would be the response to a reference of 2, and the sign here is an output disturbance, not a reference.",
          block_diagram(["4", "3"], "disturbance after the plant", feedback="1", input_label="r", output_label="y"),
          loop)
    b.num(3,
          r"The proportional gain in that loop is doubled, from 4 to 8. The plant DC gain is still 3 and the reference is still 10. The new steady error is",
          10 / (1 + 8 * 3), "1",
          r"The new loop gain is \(8 \times 3 = 24\). The error is \(10/(1+24) = 0.4\). The old error \(0.769\) forgot the new gain. Doubling the error instead of shrinking it goes the wrong way: more gain leaves less error, and it still does not reach zero.",
          block_diagram(["8", "3"], "higher proportional gain", feedback="1", input_label="r", output_label="y"),
          loop)
    b.mc(3,
         r"Derivative action is added to a proportional loop. The reference is a step, the disturbance is constant, and the loop stays linear. The steady error",
         ["becomes zero, because the derivative looks ahead",
          "changes sign",
          "stays the same as the proportional-only error",
          r"grows like \(t\), because a derivative emphasizes high frequency"], 2,
         r"A derivative of a constant is zero. Once the signals have settled, the D term contributes nothing, so the steady error is the P-only error. Looking ahead changes the transient, not the resting value. The sign of the error is set by the proportional balance. A growing error would mean the loop is not at a steady state.",
         block_diagram(["P+D", "plant"], "derivative added", feedback="1", input_label="r", output_label="y"),
         loop)
    b.num(3,
          r"A speed loop uses proportional gain 6 on a plant of DC gain 2. The speed reference is 8. The steady shortfall \(r - y\) is",
          8 / (1 + 6 * 2), "1",
          r"Loop gain \(6 \times 2 = 12\). The shortfall is \(8/(1+12) = 8/13 = 0.615\). The steady speed itself is \(12/13 \times 8 = 7.385\). Zero shortfall would need integral action, which this loop does not have.",
          block_diagram(["6", "2"], "speed loop", feedback="1", input_label="r", output_label="v"),
          loop)
    b.num(4,
          r"Tuning will later move this gain. For now, proportional gain 10 and plant DC gain 5 face a reference of 11. The steady error is",
          11 / (1 + 10 * 5), "1",
          r"Loop gain \(10 \times 5 = 50\). The error is \(11/51 = 0.216\). The output \(50/51 \times 11\) is not the error. A gain of 10 alone, ignoring the plant, is not the loop gain.",
          block_diagram(["10", "5"], "a gain you might tune", feedback="1", input_label="r", output_label="y"),
          loop, ["pid-tuning"])
    b.num(4,
          r"A cruise loop is proportional, gain 3, on a plant of DC gain 5. The speed reference is 18. The steady speed error is",
          18 / (1 + 3 * 5), "1",
          r"Loop gain \(3 \times 5 = 15\). The error is \(18/(1+15) = 18/16 = 1.125\). The steady speed \(15/16 \times 18\) is not the error. Open-loop, the same command would not know the reference at all.",
          block_diagram(["3", "5"], "cruise, proportional only", feedback="1", input_label="r", output_label="v"),
          loop, ["cruise-control"])
    b.mc(4,
         r"A PID controller's command is the sum of three terms. Those terms act on",
         ["the plant gain, the sensor gain, and the disturbance",
          "the reference, the output, and the loop gain",
          "the proportional gain only, written three times",
          "the error, the integral of the error, and the derivative of the error"], 3,
         r"P multiplies the error, I multiplies the running sum of the error, and D multiplies the rate of the error. The plant gain and the sensor gain are properties of the hardware around the controller. Writing the same proportional term three times does not add integral or derivative action.",
         block_diagram(["P", "I", "D"], "three terms, summed", output_label="u"),
         "Three blocks in a row, a stand-in for the three terms.", ["pid"])
    b.save()


def bank_ss():
    b = Bank("state-space-model")
    mech = "A mass, a spring, and a damper."
    # m=4, b=6, k=10 → A21=-2.5, A22=-1.5, B=0.25, rest at u=8 is x=0.8
    b.mc(1,
         r"An \(n\)th-order differential equation is written as a state model. How many states does that take?",
         ["n, one per derivative you have to remember",
          "1, because one equation is one state",
          "2, for A and for B",
          "n squared, the number of entries in A"], 0,
         r"Each extra derivative needs its own initial condition, so an \(n\)th-order equation has \(n\) states. One equation can still hide several derivatives. A and B are matrices, not a count of states. The number of entries in A is \(n^2\), which counts coefficients, not states.",
         block_diagram(["1/s", "1/s"], "a chain of integrators", output_label="y"),
         "Two integrator blocks in series.")
    b.num(1,
          r"A mass \(m = 4\), damper \(b = 6\), and spring \(k = 10\) obey \(m\ddot{y} = u - b\dot{y} - ky\). With states \((y, \dot{y})\), the lower-left entry of \(A\) is",
          -10 / 4, "1",
          r"Divide through by \(m\): \(\ddot{y} = -(k/m)y - (b/m)\dot{y} + u/m\). The coefficient of \(y\) in the \(\dot{x}_2\) row is \(-k/m = -10/4 = -2.5\). The damper term \(-b/m = -1.5\) is the other entry of that row. The positive ratio \(k/m\) drops the sign that the restoring force requires.",
          mass_spring("mass, spring, and damper"), mech)
    b.num(1,
          r"Same mass-spring-damper, \(m = 4\). The input \(u\) is the force. The lower entry of \(B\), the coefficient of \(u\) in \(\ddot{y}\), is",
          1 / 4, "1",
          r"The force is divided by the mass, so that entry is \(1/m = 0.25\). The spring and damper do not multiply \(u\). Using \(m\) itself, or \(k/m\), puts a different coefficient in the input column.",
          mass_spring("force input on the mass"), mech)
    b.num(2,
          r"Same device, \(m = 4\), \(b = 6\). The lower-right entry of \(A\), the coefficient of \(\dot{y}\) in \(\ddot{y}\), is",
          -6 / 4, "1",
          r"That entry is \(-b/m = -6/4 = -1.5\). The spring entry \(-k/m\) does not multiply \(\dot{y}\). Dropping the minus sign gives the damping ratio's ingredients with the wrong sign, and the free response would then grow.",
          mass_spring("damper contribution"), mech)
    b.mc(2,
         r"The output equation of a state model is",
         [r"\(\dot{x} = Ax + Bu\)",
          r"\(y = Cx + Du\)",
          r"\(y = Ax + Bu\)",
          r"\(x = Cy + Du\)"], 1,
         r"\(y = Cx + Du\) reads the output off the state, plus any piece that jumps straight through from the input. \(\dot{x} = Ax + Bu\) is the state equation, not the output. Swapping \(x\) and \(y\) inverts the definition. Using A and B for the output mixes the two equations.",
         matrix_fig([["c1", "c2"], ["d", "0"]], "a C row and a D entry, symbolic"),
         "A symbolic array, not a numeric answer.")
    b.num(2,
          r"Same \(A\) and \(B\) as above (\(m=4\), \(k=10\), \(b=6\)). A constant force \(u = 8\) is applied. At rest, the position \(y\) is",
          (0.25 * 8) / 2.5, "1",
          r"At rest \(\dot{y} = 0\) and \(\ddot{y} = 0\), so \(0 = -(k/m)y + u/m\). Then \(y = u/k = 8/10 = 0.8\). Dividing by the damper instead of the spring gives \(8/6\). Multiplying force by mass gives 32, which is not a position.",
          mass_spring("rest position under a constant force"), mech)
    b.num(3,
          r"A diagonal state matrix has entries \(-2\) and \(-8\) on the diagonal and zeros elsewhere. The slower eigenvalue (the one closer to zero) is",
          -2, "1",
          r"On a diagonal matrix the eigenvalues are the diagonal entries. The slower decay is the one closer to the origin, \(-2\). The \(-8\) mode dies four times faster. Their sum \(-10\) and their product \(16\) are coefficients of the characteristic polynomial, not the slower mode.",
          splane([(-2, 0), (-8, 0)], [], "two real poles"),
          "Two pole marks on the negative real axis.")
    b.mc(3,
         r"You rewrite the same ODE in a new choice of states. Which statement stays true?",
         ["A is unchanged, because the physics did not change",
          "the eigenvalues change to the new coordinates",
          "the eigenvalues stay the same",
          "B becomes the identity"], 2,
         r"A change of coordinates \(x = Tz\) replaces \(A\) by \(T^{-1}AT\). Similar matrices share their eigenvalues, so the modes do not move. A itself does change unless \(T\) commutes with it in a trivial way. B is transformed too, and it is not forced to be the identity.",
         matrix_fig([["0", "1"], ["?", "?"]], "a state matrix with the bottom row still open"),
         "A 2 by 2 matrix with the second row not filled in.")
    b.num(3,
          r"For \(m=4\), \(b=6\), \(k=10\) and states \((y,\dot{y})\), the characteristic polynomial is \(\lambda^2 - \mathrm{tr}(A)\,\lambda + \det(A)\). The coefficient of \(\lambda\) is",
          1.5, "1",
          r"That coefficient is \(-\mathrm{tr}(A)\). The diagonal of \(A\) is \(0\) and \(-b/m = -1.5\), so the trace is \(-1.5\) and the coefficient is \(1.5\). The constant term \(2.5\) is \(\det(A) = k/m\), not the coefficient of \(\lambda\). The bare trace \(-1.5\) still carries the sign of the diagonal.",
          mass_spring("trace from the damper"), mech)
    b.num(4,
          r"A one-state model for a later free-response calculation is \(\dot{x} = -x/3\). The eigenvalue is",
          -1 / 3, "1",
          r"The equation is \(\dot{x} = ax\) with \(a = -1/3\), so the eigenvalue is \(-1/3\). The positive \(1/3\) would grow. The reciprocal \(-3\) swaps the time constant with the rate.",
          step_response("free response of one state", fn=lambda t: math.exp(-t / 3), t_end=12),
          "A decaying curve.", ["ss-solution"])
    b.num(4,
          r"A realization of a third-order transfer function, with no pole-zero cancellation, uses how many states?",
          3, "1",
          r"Each pole needs a state if nothing cancels. A third-order denominator has three poles, so the realization has 3 states. A second-order pattern would leave a pole out. The number of coefficients in a generic \(3 \times 3\) matrix is 9, which is not the state count.",
          block_diagram(["1/s", "1/s", "1/s"], "three integrators", output_label="y"),
          "Three integrator blocks in a row.", ["realization"])
    b.mc(4,
         r"The modes of a linear state model are",
         ["the rows of B",
          "the entries of C",
          "the time constants of the sensors",
          "the eigenvalues of A"], 3,
         r"Each mode is \(e^{\lambda t}\) for an eigenvalue \(\lambda\) of \(A\), with a shape given by the matching eigenvector. The columns of B say how inputs reach the states. The rows of C say which combination is measured. Sensor time constants are extra poles you add only if you model the sensor.",
         splane([(-1, 0), (-4, 0)], [], "two modes"),
         "Two pole marks on the negative real axis.", ["eig-modes"])
    b.save()


def expl_blocks():
    fig = block_diagram(["5"], "worked feedback loop", feedback="0.4", input_label="r", output_label="y")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A forward block with a return path brought back to the input.",
         "body_md": r"""A block diagram is a picture of multiplications and additions. Each block is a gain, or later a transfer function, and the arrows are the signals those gains act on. The useful move is to erase the picture and leave one block that produces the same output from the same input.

Three connections cover the pictures in this skill. Series blocks share a signal: the output of one is the input of the next, so the gains multiply. Parallel blocks see the same input and their outputs are added, so the gains add. Feedback sends a function of the output back to the input. If that return is subtracted, the loop fights the error. If it is added, the loop reinforces it.

Walking once around the loop, multiplying every block you meet, gives the loop gain. The closed-loop gain is what the reference produces at the output after the subtracting."""},
        {"heading": "Key equations", "body_md": r"""Series replacement: \(G = G_1 G_2\). Parallel replacement: \(G = G_1 + G_2\).

Negative feedback, forward \(G\) and return \(H\):
\[
\frac{y}{r} = \frac{G}{1 + GH}.
\]
The loop gain is \(L = GH\). A disturbance that adds at the output, with the reference held at zero, is left with the fraction \(1/(1+L)\).

Positive feedback flips the sign in the denominator, \(G/(1 - GH)\), and only while \(GH\) is not 1. At \(GH = 1\) the picture says the output can be nonzero with no input, which is a loop sitting on the edge of running away."""},
        {"heading": "Worked example", "body_md": r"""Take a forward gain of 5 and a return gain of 0.4, subtracted. The loop gain is \(5 \times 0.4 = 2\). The closed-loop gain is
\[
\frac{5}{1 + 2} = \frac{5}{3} = 1.667.
\]
A reference of 1 produces an output of 1.667. The error is \(1 - 0.4 \times 1.667 = 0.333\), and the forward block turns that error into \(5 \times 0.333 = 1.667\), which matches the output. An output disturbance of 0.3 is divided by \(1 + L = 3\), so 0.1 of it remains. Using \(5/(1 - 2)\) would be the adding loop, and it is a different plant."""},
        {"heading": "Common pitfalls", "body_md": r"""Adding the gains of blocks that sit one after another is the parallel rule used in the wrong picture. Calling \(GH\) the closed-loop gain confuses the product around the loop with the gain from reference to output. The minus sign in \(1 - GH\) belongs only to a loop that adds the return. Leaving out a block that sits in the return path, a sensor gain for example, makes the loop gain wrong even when the forward block is copied correctly."""},
        {"heading": "Where this leads", "body_md": r"""The single closed-loop gain is the start of a loop transfer function, where each block is a function of \(s\) and the same algebra still applies. The fraction \(1/(1+L)\) is the sensitivity of the output to a disturbance. A Nyquist plot is a picture of the loop product \(L\) itself, not of the closed-loop gain."""},
    ]
    save_explainer("block-diagram", "Block-diagram algebra", sections)
    return words(sections)


def expl_first():
    fig = step_response("worked first-order step", tau=1.2, goal=10)
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A curve that rises quickly at first and then flattens.",
         "body_md": r"""A first-order system has one stored quantity. A tank level, a speed with drag and no spring, or a capacitor voltage behind a resistor all end up in the same shape of equation. After you scale the equation so the output has coefficient 1, two numbers describe it. The time constant \(\tau\) says how fast the stored quantity forgets. The DC gain \(K\) says where a constant input eventually parks the output.

From rest, a step input produces a rise that is steep at the first instant and then flattens. Nothing overshoots. The gap between the output and its eventual value is cut by the same factor in every interval of length \(\tau\). That is the whole transient. Free motion, with the input held at zero, is the same exponential running downhill from whatever value you started with."""},
        {"heading": "Key equations", "body_md": r"""Standard form:
\[
\tau \dot{y} + y = K u.
\]
The steady output for a constant input is \(y(\infty) = Ku\). The time constant does not appear in that product. From rest, a step of height \(u\) gives
\[
y(t) = Ku\left(1 - e^{-t/\tau}\right).
\]
At \(t = \tau\) the factor in parentheses is \(1 - e^{-1}\), about 0.632. The initial slope is \(Ku/\tau\). Free motion from \(y(0)\) is \(y(0) e^{-t/\tau}\). The pole sits at \(-1/\tau\)."""},
        {"heading": "Worked example", "body_md": r"""Use \(\tau = 1.2\) s and \(K = 5\), and let \(u\) step from 0 to 2. The steady output is \(5 \times 2 = 10\). One time constant after the step,
\[
y(1.2) = 10\left(1 - e^{-1}\right) = 6.321.
\]
The initial slope is \(10/1.2 = 8.333\) per second, which would reach 10 in exactly 1.2 s if the curve were a straight line. It is not: the slope falls as the gap falls, and the curve is still short of 10 at \(t = 1.2\). The pole is at \(-1/1.2\). Dividing the steady value by \(\tau\) and calling that the steady value is the initial-slope mistake."""},
        {"heading": "Common pitfalls", "body_md": r"""The steady value does not depend on \(\tau\). Dividing \(Ku\) by \(\tau\) answers the initial slope, not the resting point. The halfway time is \(\tau \ln 2\), about \(0.69\tau\), so a mark at 50% is earlier than one time constant. The pole is \(-1/\tau\), not \(-\tau\) and not \(+\tau\). A positive pole would be a runaway, and this skill's plants are the settling kind."""},
        {"heading": "Where this leads", "body_md": r"""A second-order step can overshoot; the first-order rise is the comparison that makes the overshoot obvious. Step-response specs quote the time constant, the settling level, and the initial slope you just computed. Proportional control around a first-order plant leaves a constant error, which is the reason a later PID law adds an integrator."""},
    ]
    save_explainer("first-order-sys", "First-order systems", sections)
    return words(sections)


def expl_method():
    fig = mass_spring("a model you might simplify", spring=True, damper=True)
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A mass connected to a spring and a damper.",
         "body_md": r"""Writing the differential equation is the second step. The first step is deciding what the model is for. A control model is not a catalog of every effect you can name. It is the smallest description that still gets the loop's behavior right: the right stored quantities, the right units, and the right split between fast effects you can collapse and slow effects you must keep.

A state is a stored quantity that needs an initial condition: position of a mass, charge on a capacitor, level in a tank. A command, a reference, and a disturbance are inputs unless you give them dynamics of their own.

Units catch algebra errors before any simulation does. Scaling then turns the surviving terms into pure numbers, so a coefficient of 0.01 can be compared with a coefficient of 1 and dropped on purpose."""},
        {"heading": "Key equations", "body_md": r"""A time scale from a length \(L\) and a velocity \(V\) is \(L/V\). A rotational speed in revolutions per minute becomes radians per second by
\[
\omega = N_{\mathrm{rpm}} \cdot \frac{2\pi}{60}.
\]
A sensor gain converts the measured unit into the signal unit by multiplication, not by addition. Force is mass times acceleration. At a resting point every derivative is zero, which is an algebraic equation for the state. A ratio of a slow time scale to a fast one tells you whether the fast piece can be replaced by the gain it settles to."""},
        {"heading": "Worked example", "body_md": r"""A tank level is read over a depth of 150 mm, which is 0.15 m. The flow you care about moves that surface at about 0.01 m/s, so the level time scale is \(0.15/0.01 = 15\) s. The valve that sets the flow moves in 0.05 s. The ratio of those scales is \(15/0.05 = 300\). A level loop over tens of seconds can treat the valve as an immediate gain. Entering 150 mm as 150 m would make the time scale 15000 s and send the design after the wrong plant."""},
        {"heading": "Common pitfalls", "body_md": r"""Calling an input a state, or a state an input, swaps the columns of the model you write next. Comparing terms that still carry different units will drop the wrong one. A loop that is required to have zero steady error needs the integrator that produces that fact; a model that omits it will predict an error the hardware will not show. The halfway point of a measured step is not the time constant. For one real pole, the time constant is the 63% time."""},
        {"heading": "Where this leads", "body_md": r"""Linearization builds a local linear model at the resting point you just solved. Identification reads a time constant and a gain back out of a measured step. Equilibrium calculations are the same derivative-equals-zero step, done for a plant you intend to hold."""},
    ]
    save_explainer("model-method", "Modeling methodology", sections)
    return words(sections)


def expl_pid():
    fig = block_diagram(["P"], "proportional cruise-style loop", feedback="1", input_label="r", output_label="y")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A forward block with a return path subtracted at the input.",
         "body_md": r"""On-off feedback looks at the sign of the error and commands full on or full off. It chatters near the reference, because the only way to reduce the command is to switch it off. Proportional control multiplies the error by a gain, so a small error produces a small command. It can settle. It does not settle at zero error.

Integral action adds up the error as time passes. A leftover constant error keeps the sum moving, so the command keeps changing until the error is gone. Derivative action looks at how fast the error is changing. It can calm a transient. On a constant error its contribution is zero, so it does not fix the resting value.

This skill stops at that split and at the steady error of a proportional loop. The three-term formula is a later skill."""},
        {"heading": "Key equations", "body_md": r"""On-off: \(u\) is one of two values. Proportional: \(u = K_c(r - y)\).

If the plant's DC gain is \(P\) and nothing else integrates, the loop gain is \(L = K_c P\) and a constant reference leaves
\[
y = \frac{L}{1+L} r, \qquad r - y = \frac{r}{1+L}.
\]
A disturbance of size \(d\) that adds at the output is left as \(d/(1+L)\). Raising \(K_c\) shrinks the error and never removes it. Integral action, once the loop is stable, is what makes a constant error untenable."""},
        {"heading": "Worked example", "body_md": r"""Use \(K_c = 2\) and a plant DC gain \(P = 5\), and let the reference step to 7. The loop gain is \(2 \times 5 = 10\). The steady output is
\[
y = \frac{10}{11} \times 7 = 6.364,
\]
and the steady error is \(7/11 = 0.636\). Check: the error times \(K_c\) is the command \(1.273\), and the plant turns that into \(5 \times 1.273 = 6.364\). A constant output disturbance of 1.1 contributes \(1.1/11 = 0.1\) on top of that balance. Doubling \(K_c\) would cut the error roughly in half and still leave it nonzero. An integrator would be a different controller."""},
        {"heading": "Common pitfalls", "body_md": r"""A stable proportional loop is not a zero-error loop. Zero error needs a free integrator somewhere in the loop, in the plant or in the controller. Derivative action feels like it should fix the steady error because it "anticipates," but the derivative of a constant is zero. On-off cannot hold an intermediate command, so a plant that needs an intermediate command to match the reference will oscillate around it. Doubling the gain does not double the output of a loop that is already closed: the output moves closer to the reference, and the command does not scale in the open-loop way."""},
        {"heading": "Where this leads", "body_md": r"""The proportional speed error is the cruise-control question: a grade or a drag change looks like a constant disturbance, and P control leaves a speed offset. Tuning is the decision of how large \(K_c\) may be before the transient is unacceptable. The PID law writes the three terms as one command, with a real actuator limit beside them."""},
    ]
    save_explainer("onoff-pid-intro", "On-off, P, PI, and PID", sections)
    return words(sections)


def expl_ss():
    fig = matrix_fig([["0", "1"], ["-3", "-1"]], "worked state matrix")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A 2 by 2 matrix of coefficients.",
         "body_md": r"""A state model is an ordinary differential equation written so that only first derivatives appear, and each of them sits on the left of its own line. The price is a vector. If the original equation has \(n\) derivatives of one output, you invent \(n\) states to hold the output and those derivatives, and you let a matrix remember the coefficients.

The state equation \(\dot{x} = Ax + Bu\) says how the stored quantities move. The output equation \(y = Cx + Du\) says what you measure. \(D\) is zero whenever the measurement is a state, or a mix of states, with no direct jump from the input. Choosing different states changes \(A\), \(B\), and \(C\). It does not change the eigenvalues of \(A\), which are the modes of the motion.

This skill is the packaging step. Solving the matrix exponential, testing reachability, and placing those eigenvalues come later."""},
        {"heading": "Key equations", "body_md": r"""For a mass \(m\), damper \(b\), and spring \(k\), with states \((y, \dot{y})\) and force input \(u\),
\[
\begin{bmatrix} \dot{y} \\ \ddot{y} \end{bmatrix}
=
\begin{bmatrix} 0 & 1 \\ -k/m & -b/m \end{bmatrix}
\begin{bmatrix} y \\ \dot{y} \end{bmatrix}
+
\begin{bmatrix} 0 \\ 1/m \end{bmatrix} u.
\]
The output \(y\) has \(C = [1\ 0]\) and \(D = 0\). At rest, \(Ax + Bu = 0\). The characteristic polynomial is \(\lambda^2 - \mathrm{tr}(A)\lambda + \det(A)\). A diagonal \(A\) has its eigenvalues printed on the diagonal, and the slower mode is the eigenvalue closer to zero."""},
        {"heading": "Worked example", "body_md": r"""Take \(m = 3\), \(k = 9\), and \(b = 3\). Then \(k/m = 3\) and \(b/m = 1\), so
\[
A = \begin{bmatrix} 0 & 1 \\ -3 & -1 \end{bmatrix}, \qquad B = \begin{bmatrix} 0 \\ 1/3 \end{bmatrix}.
\]
A constant force \(u = 9\) rests at \(\dot{y} = 0\) and \(0 = -3y + 9/3\), so \(y = 1\). In the state vector that is \(x = 1\) in the position slot and \(0\) in the velocity slot. The trace of \(A\) is \(-1\), so the coefficient of \(\lambda\) in the characteristic polynomial is \(1\), and the constant term is \(\det(A) = 3\). Swapping the two states would move the \(-3\) to a different corner and would leave the eigenvalues where they are."""},
        {"heading": "Common pitfalls", "body_md": r"""The spring term is \(-k/m\), with the minus sign. A plus sign is a spring that pushes away from the origin. The input column is \(1/m\), not \(m\) and not \(k\). \(D\) is not a second copy of \(B\). Counting the entries of \(A\) and calling that the number of states overcounts by a factor of \(n\). On a diagonal matrix the slower eigenvalue is the one closer to zero, not the one with the larger magnitude and not the sum of the diagonal."""},
        {"heading": "Where this leads", "body_md": r"""The free response is the matrix exponential of \(At\) applied to the initial state, which is why the eigenvalue \(-1/3\) of a one-state example matters. A realization is this packaging run backwards, from a transfer function to some \(A, B, C, D\). The modes you will plot and move are the eigenvalues of the \(A\) you just assembled."""},
    ]
    save_explainer("state-space-model", "State-space models", sections)
    return words(sections)


def lint():
    banned = re.compile(r"niknejad|åström|aström|astrom|murray|feedback systems|\breader\b|§", re.I)
    skills = ["block-diagram", "first-order-sys", "model-method", "onoff-pid-intro", "state-space-model"]
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
            if sid == "block-diagram" and q.get("figure"):
                nbox = q["figure"].count("<rect ")
                alt = q.get("figure_alt") or ""
                expect = {2: "Two ", 3: "Three "}.get(nbox)
                if expect and not alt.startswith(expect):
                    problems.append(f"{q['id']} alt {alt!r} does not match {nbox} blocks")
        if nfig < 9:
            problems.append(f"{sid} only {nfig} figures")
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
    bank_blocks()
    bank_first()
    bank_method()
    bank_pid()
    bank_ss()
    print("words", expl_blocks(), expl_first(), expl_method(), expl_pid(), expl_ss())
    lint()


if __name__ == "__main__":
    main()
