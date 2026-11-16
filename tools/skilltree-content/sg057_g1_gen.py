#!/usr/bin/env python3
"""SG-057 group 1: first-order core, second-order core, transfer-function title.

Keeps the core ids. Retires moved question ids and does not reuse them.
Deep questions are built with Bank.sym, Bank.order, Bank.find_error, and Bank.multi.
Running this again does nothing once the sentinel question is already live.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from banklib import BANK, EXP, Bank, words
from templates import block_diagram, mass_spring, splane, step_response

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SENTINEL = "first-order-sys-r1-q4"


def load(sid, kind):
    folder = BANK if kind == "bank" else EXP
    path = os.path.join(folder, sid + ".json")
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    data["_path"] = path
    return data


def dump(data):
    path = data.pop("_path")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def retire(bank, qid):
    for i, q in enumerate(bank["questions"]):
        if q.get("id") == qid:
            gone = bank["questions"].pop(i)
            if not isinstance(gone.get("version"), int):
                gone["version"] = 1
            bank.setdefault("retired_questions", []).append(gone)
            return
    raise SystemExit("missing live question " + qid)


def built(sid, rnd, qid, kind, *args, **kwargs):
    slot = Bank(sid)
    getattr(slot, kind)(rnd, *args, **kwargs)
    item = slot.qs[0]
    item["id"] = qid
    item["version"] = 1
    return item


def retarget(bank, qid, preview):
    for q in bank["questions"]:
        if q.get("id") == qid:
            q["preview"] = preview
            q["version"] = int(q.get("version") or 1) + 1
            return
    raise SystemExit("missing preview question " + qid)


def bump(bank):
    bank["version"] = int(bank.get("version") or 1) + 1


def patch_first_order():
    bank = load("first-order-sys", "bank")
    for qid in ("first-order-sys-r1-q1", "first-order-sys-r2-q2", "first-order-sys-r2-q3",
                "first-order-sys-r3-q1", "first-order-sys-r4-q3"):
        retire(bank, qid)
    retarget(bank, "first-order-sys-r4-q1", ["rc-lpf"])
    retarget(bank, "first-order-sys-r4-q2", ["sys-id"])
    rise = step_response("first-order rise", tau=1.4, goal=1)
    fall = step_response("free response", tau=1.1, goal=1, fn=lambda t: math.exp(-t / 1.1), t_end=4)
    bank["questions"] += [
        built("first-order-sys", 1, "first-order-sys-r1-q4", "order",
              "Put these readings of \\(\\tau\\dot y + y = Ku\\) in the order that uses each result.",
              [
                  "Scale the equation so the coefficient of \\(y\\) is 1.",
                  "Read \\(\\tau\\) as the coefficient of \\(\\dot y\\), and \\(K\\) as the coefficient of \\(u\\).",
                  "Place the single pole at \\(-1/\\tau\\).",
                  "From rest, a constant input \\(u\\) settles at \\(Ku\\) along \\(Ku(1-e^{-t/\\tau})\\).",
              ],
              "The standard form has to come first, or \\(\\tau\\) and \\(K\\) are still mixed with a leading coefficient. The pole is \\(-1/\\tau\\) only after \\(\\tau\\) is that coefficient. The step formula uses both numbers, so it is last. Reading the pole from \\(K\\) swaps the speed with the resting level.",
              rise, "A smooth curve that rises toward a horizontal line and does not overshoot."),
        built("first-order-sys", 2, "first-order-sys-r2-q4", "sym",
              "A first-order output starts at \\(y_i\\) and a constant input would settle it at \\(y_f\\). The time constant is \\(\\tau\\). For \\(t>0\\), write \\(y(t)\\) using the names \\(yi\\), \\(yf\\), \\(tau\\), and \\(t\\).",
              "yf+(yi-yf)*exp(-t/tau)",
              {"yi": (0.4, 3.0), "yf": (4.0, 9.0), "tau": (0.3, 4.0), "t": (0.2, 6.0)},
              "The gap \\(yi-yf\\) shrinks by \\(e^{-t/\\tau}\\). Adding that shrinking gap to the final value starts at \\(yi\\) and ends at \\(yf\\). Using \\(yi\\,e^{-t/\\tau}\\) alone is the free response, which heads to 0. Swapping \\(yi\\) and \\(yf\\) starts at the wrong end.",
              alternates=["yi*exp(-t/tau)+yf*(1-exp(-t/tau))"],
              fig=fall, alt="A smooth curve that leaves one level and approaches another."),
        built("first-order-sys", 2, "first-order-sys-r2-q5", "num",
              "A first-order system has \\(\\tau=0.5\\ \\mathrm{s}\\). After a step from rest, how long does the output take to reach 90% of its final value?",
              0.5 * math.log(10), "s",
              "Set \\(1-e^{-t/\\tau}=0.9\\). Then \\(e^{-t/\\tau}=0.1\\), so \\(t=\\tau\\ln 10\\). With \\(\\tau=0.5\\ \\mathrm{s}\\) that is \\(0.5\\ln 10\\). One time constant is the 63% point, not the 90% point. Five time constants is the near-settled point, which is later than 90%.",
              rise, "A smooth rising curve with no overshoot."),
        built("first-order-sys", 3, "first-order-sys-r3-q4", "find_error",
              "A student reads the step from rest, \\(y(t)=y_\\infty(1-e^{-t/\\tau})\\), at \\(t=\\tau\\). Exactly one step is wrong.",
              [
                  "At \\(t=\\tau\\) the exponent \\(-t/\\tau\\) equals \\(-1\\).",
                  "\\(e^{-1}\\) is about \\(0.368\\).",
                  "The fraction of the step that is finished is \\(1\\) minus that value.",
                  "So the output has reached about 37% of the final value.",
              ],
              3,
              "The exponent and the value of \\(e^{-1}\\) are right. The finished fraction is \\(1-0.368\\), about 0.63, not the leftover 0.37. Keeping 0.37 reports the gap that is still open.",
              reasons=[
                  "One minus 0.368 is about 0.632, so the finished fraction is about 63%, not 37%.",
                  "The exponent at one time constant is \\(-\\tau\\), not \\(-1\\).",
                  "The output is already at the final value when \\(t=\\tau\\).",
              ],
              correct_reason=0,
              fig=rise, alt="A smooth rising curve, with no mark that states a percentage."),
        built("first-order-sys", 4, "first-order-sys-r4-q4", "num",
              "Two first-order systems have the same DC gain. Their time constants are \\(\\tau_1=1\\ \\mathrm{s}\\) and \\(\\tau_2=4\\ \\mathrm{s}\\). How long does the slower one take to reach 95% of its final value after a step from rest?",
              4 * math.log(20), "s",
              "The slower time constant is 4 s. Ninety-five percent means \\(e^{-t/\\tau}=0.05\\), so \\(t=\\tau\\ln 20\\). That is \\(4\\ln 20\\) seconds. Using \\(\\tau=1\\) answers the faster system. One time constant is the 63% point.",
              rise, "A smooth rising curve that flattens, drawn without a time label.",
              preview=["lti-circuits"]),
    ]
    bump(bank)
    dump(bank)


def patch_step():
    bank = load("step-resp", "bank")
    for qid in ("step-resp-r1-q2", "step-resp-r1-q5", "step-resp-r2-q1", "step-resp-r2-q2",
                "step-resp-r3-q2", "step-resp-r3-q3", "step-resp-r4-q1", "step-resp-r4-q2",
                "step-resp-r4-q3"):
        retire(bank, qid)
    pulse = step_response("pulse", tau=1.0, goal=1.0,
                           fn=lambda t: (1 - math.exp(-t)) if t < 1 else (1 - math.exp(-1)) * math.exp(-(t - 1)),
                           t_end=4)
    area_fig = step_response("held pulse", tau=1.0, goal=1.0, fn=lambda t: 1.0 if t < 1.2 else 0.0, t_end=3)
    bank["questions"] += [
        built("step-resp", 1, "step-resp-r1-q6", "mc",
              "For \\(t>0\\), which identity is the unit step?",
              [
                  "The running integral of a unit impulse from 0 to \\(t\\).",
                  "The derivative of a unit impulse.",
                  "The running integral of a unit step.",
                  "A pulse whose width equals its height.",
              ],
              0,
              "A unit impulse has all of its area at one instant. Integrating that area from 0 to \\(t>0\\) yields 1, which is the unit step. Differentiating the impulse is not a step. Integrating the step produces a ramp. A pulse returns to zero, so it is not a step.",
              area_fig, "A waveform that is flat for a while and then returns to the axis."),
        built("step-resp", 1, "step-resp-r1-q7", "num",
              "An input pulse is 3 V high and lasts 0.4 s. What is its area?",
              1.2, "V s",
              "Area is height times width: \\(3\\times 0.4=1.2\\ \\mathrm{V\\,s}\\). That area is the weight of the impulse that matches the pulse. The height alone is 3 V, and the width alone is 0.4 s.",
              area_fig, "A rectangular pulse with no height or width written on it."),
        built("step-resp", 2, "step-resp-r2-q5", "num",
              "A unit-DC-gain system with \\(\\tau=2\\ \\mathrm{s}\\) starts at rest. The input is a pulse of height 4 from \\(t=0\\) to \\(t=1\\ \\mathrm{s}\\), then 0. The pulse is a step minus a delayed step. What is the output at \\(t=1.5\\ \\mathrm{s}\\)?",
              4 * (1 - math.exp(-0.5)) * math.exp(-0.25), "1",
              "Up to 1 s the input is a step of height 4, so \\(y(1)=4(1-e^{-0.5})\\). From 1 s to 1.5 s the input is 0, which is the same as subtracting a step of height 4 that started at 1 s. The value already reached then decays for 0.5 s: multiply by \\(e^{-0.25}\\). Continuing to charge toward 4 forgets that the pulse has ended.",
              pulse, "A curve that rises and then falls back toward the axis."),
        built("step-resp", 2, "step-resp-r2-q6", "find_error",
              "A pulse of height \\(A\\) runs from time 0 to time \\(T\\). A student builds it from steps. Exactly one step is wrong.",
              [
                  "The pulse equals a step of height \\(A\\) at time 0 minus a step of height \\(A\\) at time \\(T\\).",
                  "Call the unit-step response \\(s(t)\\). Linearity scales it by \\(A\\).",
                  "For \\(0<t<T\\) only the first step has arrived, so the output is \\(A\\,s(t)\\).",
                  "During \\(0<t<T\\) subtract \\(A\\,s(t-T)\\) as well.",
              ],
              3,
              "The difference of steps is the right input. Before time \\(T\\) the delayed step is still zero, so subtracting it early removes a response that has not started. After \\(T\\) the subtraction is required.",
              reasons=[
                  "The delayed step is zero until time \\(T\\), so it must not be subtracted on \\(0<t<T\\).",
                  "The two steps should be added, not subtracted.",
                  "A pulse is a single step of height \\(A\\times T\\).",
              ],
              correct_reason=0,
              fig=pulse, alt="A curve that rises and later falls, with no time labels."),
        built("step-resp", 3, "step-resp-r3-q4", "mc",
              "A pulse of height 5 is on from \\(t=1\\) to \\(t=4\\) and is zero otherwise. Which difference of steps is that input? \\(u\\) is the unit step.",
              [
                  "\\(5u(t-1)-5u(t-4)\\)",
                  "\\(5u(t)-5u(t-4)\\)",
                  "\\(5u(t-1)+5u(t-4)\\)",
                  "\\(u(t-1)-u(t-4)\\)",
              ],
              0,
              "The pulse turns on at \\(t=1\\) and turns off at \\(t=4\\), so the second step is delayed by 4 and subtracted. A step at time 0 starts too early. Adding the second step doubles the height after \\(t=4\\) instead of returning to zero. Dropping the 5 is a pulse of height 1.",
              area_fig, "A rectangular pulse sitting away from the time origin."),
        built("step-resp", 3, "step-resp-r3-q5", "num",
              "A unit-DC-gain system with \\(\\tau=1\\ \\mathrm{s}\\) starts at rest. The input is a pulse of height 2 from \\(t=0\\) to \\(t=0.5\\ \\mathrm{s}\\). What is the output at \\(t=1.5\\ \\mathrm{s}\\)?",
              2 * (1 - math.exp(-0.5)) * math.exp(-1.0), "1",
              "At the end of the pulse, \\(y(0.5)=2(1-e^{-0.5})\\). The input is then zero for one more second, so that value decays by \\(e^{-1}\\). The expression \\(2(1-e^{-1.5})\\) would be a step that never turned off.",
              pulse, "A curve that rises briefly and then decays."),
        built("step-resp", 4, "step-resp-r4-q4", "num",
              "A causal impulse response is \\(h(t)=6e^{-3t}\\) for \\(t\\ge 0\\). The step response is the running integral of \\(h\\). What value does that step response settle to?",
              2.0, "1",
              "The settled step response equals the area of the impulse response: \\(\\int_0^\\infty 6e^{-3t}\\,dt=6/3=2\\). The height 6 is the impulse response at \\(t=0\\), not the settled step. Dividing by 6 leaves the decay rate.",
              step_response("settling integral", tau=1 / 3, goal=2),
              "A smooth curve that rises toward a flat level.",
              preview=["first-order-sys"]),
        built("step-resp", 4, "step-resp-r4-q5", "num",
              "A short pulse is 5 V high and lasts 0.02 s. A later circuit skill treats a pulse this short as an impulse. What area should that impulse carry?",
              0.1, "V s",
              "The matching impulse has the pulse's area: \\(5\\times 0.02=0.1\\ \\mathrm{V\\,s}\\). The height 5 V drops the duration. The duration 0.02 s drops the height.",
              area_fig, "A very narrow rectangular pulse.",
              preview=["lti-circuits"]),
        built("step-resp", 4, "step-resp-r4-q6", "num",
              "A system's unit-step response is \\(s(t)=1-e^{-t}\\) for \\(t\\ge 0\\). A unit-height pulse from \\(t=0\\) to \\(t=1\\) is a step minus a delayed step. What is the output at \\(t=2\\)?",
              math.exp(-1) - math.exp(-2), "1",
              "After the pulse ends, \\(y(t)=s(t)-s(t-1)\\). At \\(t=2\\) that is \\((1-e^{-2})-(1-e^{-1})=e^{-1}-e^{-2}\\). Reporting \\(s(2)\\) forgets to subtract the delayed step. Reporting \\(s(1)\\) stops at the instant the pulse ends.",
              pulse, "A curve that rises and then decays toward the axis.",
              preview=["rc-lpf"]),
    ]
    bump(bank)
    dump(bank)


def patch_rc():
    bank = load("rc-lpf", "bank")
    retire(bank, "rc-lpf-r1-q4")
    retire(bank, "rc-lpf-r1-q5")
    curve = step_response("rc step", tau=1.0, goal=1.0)
    bank["questions"] += [
        built("rc-lpf", 1, "rc-lpf-r1-q6", "sym",
              "A capacitor \\(C\\) is charged through a resistance \\(R\\). Write the time constant using the names \\(R\\) and \\(C\\).",
              "R*C",
              {"R": (100.0, 5000.0), "C": (1e-9, 1e-6)},
              "The time constant of this low-pass is the product \\(RC\\). Dividing \\(R\\) by \\(C\\), or adding them, does not have the dimension of time. The exponential shape is already fixed once that product is known.",
              fig=curve, alt="A smooth rising capacitor voltage with no component values printed."),
        built("rc-lpf", 1, "rc-lpf-r1-q7", "order",
              "The capacitor may see more than one resistor. Order the steps that produce its cutoff.",
              [
                  "Turn the independent sources off and find the resistance the capacitor sees.",
                  "Multiply that resistance by \\(C\\). The product is \\(\\tau\\).",
                  "The cutoff in radians per second is \\(1/\\tau\\).",
                  "A step then follows the first-order exponential that uses this \\(\\tau\\).",
              ],
              "The resistance has to be the one the capacitor sees, or \\(\\tau\\) uses the wrong resistor. The cutoff is the reciprocal of that product. The exponential is the first-order step once \\(\\tau\\) is known, so it comes last.",
              curve, "A smooth rising curve with no resistor labels."),
    ]
    bump(bank)
    dump(bank)


def patch_lti_circuits():
    bank = load("lti-circuits", "bank")
    for qid in ("lti-circuits-r1-q2", "lti-circuits-r1-q4", "lti-circuits-r2-q1",
                "lti-circuits-r2-q3", "lti-circuits-r3-q1", "lti-circuits-r3-q3",
                "lti-circuits-r3-q4"):
        retire(bank, qid)
    curve = step_response("superposed step", tau=1.2, goal=1.0)
    bank["questions"] += [
        built("lti-circuits", 1, "lti-circuits-r1-q5", "sym",
              "With the capacitor removed and the independent sources off, the capacitor's node sees \\(R_1\\) in parallel with \\(R_2\\). Write that resistance using the names \\(R1\\) and \\(R2\\).",
              "R1*R2/(R1+R2)",
              {"R1": (200.0, 4000.0), "R2": (200.0, 4000.0)},
              "Parallel resistances share the node, so the combination is the product over the sum. Adding \\(R_1\\) and \\(R_2\\) is the series total. Using only the source resistor ignores the second path.",
              alternates=["1/(1/R1+1/R2)"],
              fig=curve, alt="A smooth curve, with no resistor values on it."),
        built("lti-circuits", 1, "lti-circuits-r1-q6", "num",
              "A linear circuit starts at rest. An input of 2 V produces 0.8 V at the output node, and a separate input of 3 V produces 1.2 V there. What does an input of 5 V produce at that node?",
              2.0, "V",
              "Superposition adds the responses of inputs that add: \\(0.8+1.2=2.0\\ \\mathrm{V}\\). The 5 V input is the sum of the 2 V and 3 V inputs. Averaging 0.8 and 1.2 drops one of the contributions.",
              curve, "A smooth rising output with no voltage labels."),
        built("lti-circuits", 2, "lti-circuits-r2-q5", "num",
              "A linear circuit's impulse response is a rectangle of height 2 from \\(t=0\\) to \\(t=1\\ \\mathrm{s}\\), and 0 after that. The input is a step of height 3 that starts at \\(t=0\\). What is the output at \\(t=0.5\\ \\mathrm{s}\\)?",
              3.0, "1",
              "Convolution with a step that is still on walks over the rectangle that has occurred so far. From 0 to 0.5 s the impulse response is 2 and the input is 3, so the output is \\(3\\times 2\\times 0.5=3\\). Using the full 1 s width of the rectangle includes time that has not happened yet.",
              curve, "A smooth curve that is still rising at mid-window."),
        built("lti-circuits", 2, "lti-circuits-r2-q6", "num",
              "The same linear circuit responds to a unit step with the value 4 at a fixed time. By linearity, what does it respond with, at that same time, when the step height is 2.5?",
              10.0, "1",
              "Linearity scales the whole response by the input height: \\(2.5\\times 4=10\\). Adding 2.5 to 4 treats the step height as a second input instead of a scale factor.",
              curve, "A smooth rising curve with no scale marked."),
        built("lti-circuits", 3, "lti-circuits-r3-q5", "find_error",
              "A student finds the resistance seen by a capacitor. Exactly one step is wrong.",
              [
                  "Replace each independent voltage source by a short.",
                  "Replace each independent current source by an open.",
                  "The resistance seen by the capacitor is the resistance of what remains.",
                  "Leave a voltage source in place, because it sets the bias the capacitor will reach.",
              ],
              3,
              "The resistance is measured with the independent sources off. A voltage source that stays in the circuit is a short only after it is turned off. Leaving it in holds a node at a fixed voltage and changes the resistance.",
              reasons=[
                  "An independent voltage source is replaced by a short when the resistance is measured. Leaving it in is not that short.",
                  "Current sources should be replaced by shorts.",
                  "The capacitor stays in the network while its own resistance is measured.",
              ],
              correct_reason=0),
        built("lti-circuits", 3, "lti-circuits-r3-q6", "mc",
              "Which network, from an external input to the labeled output, is linear and time-invariant?",
              [
                  "Resistors and capacitors only, with fixed values.",
                  "The same resistors plus a diode in series with the source.",
                  "A resistor and a capacitor whose capacitance is set by a second input.",
                  "A switch that changes the resistor at a fixed time after the input arrives.",
              ],
              0,
              "Fixed resistors and capacitors obey linear element laws with constant coefficients. A diode is not linear. A capacitance set by another input multiplies two signals. A switch that moves at a set time makes the equation depend on absolute time.",
              curve, "A smooth curve that could be a linear step."),
        built("lti-circuits", 3, "lti-circuits-r3-q7", "num",
              "An impulse response is a rectangle of height 4 from \\(t=0\\) to \\(t=0.2\\ \\mathrm{s}\\). A step input of height 2 starts at \\(t=0\\). What is the output at \\(t=0.1\\ \\mathrm{s}\\)?",
              0.8, "1",
              "Only the first 0.1 s of the rectangle has been covered. The output is \\(2\\times 4\\times 0.1=0.8\\). Using the whole 0.2 s width counts time beyond the instant being asked.",
              curve, "A rising curve over a short window."),
    ]
    bump(bank)
    dump(bank)


def patch_second():
    bank = load("second-order-sys", "bank")
    for qid in ("second-order-sys-r2-q1", "second-order-sys-r2-q2", "second-order-sys-r2-q3",
                "second-order-sys-r3-q1", "second-order-sys-r4-q1", "second-order-sys-r4-q3"):
        retire(bank, qid)
    poles = splane([(-1, 3), (-1, -3)], [], "complex pair")
    bank["questions"] += [
        built("second-order-sys", 2, "second-order-sys-r2-q4", "order",
              "The characteristic polynomial is \\(s^2 + b s + c\\) with \\(c>0\\). Order the reading of the damping case.",
              [
                  "Read \\(\\omega_n\\) as the square root of \\(c\\).",
                  "Read \\(2\\zeta\\omega_n\\) from the coefficient \\(b\\).",
                  "Divide \\(b\\) by \\(2\\omega_n\\) to get \\(\\zeta\\).",
                  "Decide underdamped, critical, or overdamped by comparing \\(\\zeta\\) with 1.",
              ],
              "\\(\\omega_n\\) is needed before \\(\\zeta\\), because the linear coefficient is \\(2\\zeta\\omega_n\\). The case is a comparison of \\(\\zeta\\) with 1, so it is last. Treating \\(c\\) as \\(\\omega_n\\) skips the square root.",
              poles, "A conjugate pair of pole marks in the left half-plane."),
        built("second-order-sys", 2, "second-order-sys-r2-q5", "sym",
              "For \\(0<\\zeta<1\\), write the damped frequency \\(\\omega_d\\) using the names \\(wn\\) and \\(zeta\\).",
              "wn*sqrt(1-zeta^2)",
              {"wn": (1.0, 8.0), "zeta": (0.05, 0.9)},
              "\\(\\omega_d=\\omega_n\\sqrt{1-\\zeta^2}\\) is the imaginary part of the pole. Using \\(\\omega_n\\) alone is the natural frequency. Putting \\(\\zeta\\) in the numerator instead of under the square root is the real-part formula.",
              alternates=["wn*sqrt((1-zeta)*(1+zeta))"],
              fig=poles, alt="A conjugate pair of pole marks, with no frequencies printed."),
        built("second-order-sys", 2, "second-order-sys-r2-q6", "num",
              "\\(H(s)=8/(s^2+2s+10)\\) has a complex pair of poles. What is their natural frequency \\(\\omega_n=|p|\\)?",
              math.sqrt(10), "rad/s",
              "The constant term is \\(\\omega_n^2=10\\), so \\(\\omega_n=\\sqrt{10}\\). The poles are \\(-1\\pm j3\\), and \\(\\sqrt{1+9}\\) is the same distance. The imaginary part 3 is the damped frequency. The numerator 8 is not a pole.",
              poles, "A conjugate pair of pole marks around a point left of the origin."),
        built("second-order-sys", 3, "second-order-sys-r3-q4", "num",
              "A characteristic polynomial is \\(s^2+3s+25\\). What is the damping ratio \\(\\zeta\\)?",
              0.3, "1",
              "Match \\(s^2+2\\zeta\\omega_n s+\\omega_n^2\\). Then \\(\\omega_n=5\\) and \\(2\\zeta\\omega_n=3\\), so \\(\\zeta=3/10=0.3\\). Dividing 3 by 25 uses \\(\\omega_n^2\\). Dividing 3 by 5 drops the 2.",
              splane([(-1.5, 4.77), (-1.5, -4.77)], [], "damping pair"),
              "A conjugate pair of pole marks in the left half-plane."),
        built("second-order-sys", 4, "second-order-sys-r4-q4", "multi",
              "Select every pole pair that is underdamped. The other choices are not.",
              [
                  "\\(\\zeta=0.2\\), a complex conjugate pair",
                  "\\(\\zeta=1\\), a repeated real pole",
                  "\\(\\zeta=1.4\\), two distinct real poles",
                  "\\(\\zeta=0.7\\), a conjugate pair in the left half-plane",
              ],
              [0, 3],
              "Underdamped means \\(\\zeta<1\\), so the poles are a complex conjugate pair. \\(\\zeta=1\\) is critical damping, a repeated real pole. \\(\\zeta>1\\) is overdamped, two distinct real poles. Both listed pairs with \\(\\zeta<1\\) qualify.",
              poles, "Pole marks that could be a complex pair or real poles.",
              preview=["step-specs"]),
        built("second-order-sys", 4, "second-order-sys-r4-q5", "find_error",
              "Poles sit at \\(-1\\pm j3\\). A student names \\(\\omega_n\\). Exactly one step is wrong.",
              [
                  "The real part of each pole is \\(-1\\) and the imaginary part is \\(3\\).",
                  "The distance from the origin is \\(\\sqrt{1+9}\\).",
                  "That distance equals \\(\\omega_n\\).",
                  "So \\(\\omega_n\\) is 3, the imaginary part.",
              ],
              3,
              "The distance \\(\\sqrt{10}\\) is \\(\\omega_n\\). The imaginary part is the damped frequency \\(\\omega_d\\), which is smaller. Stopping at step three is the correct reading.",
              reasons=[
                  "The imaginary part is \\(\\omega_d\\). \\(\\omega_n\\) is the distance from the origin, \\(\\sqrt{10}\\).",
                  "The real part is the natural frequency.",
                  "A left-half-plane pair has no natural frequency.",
              ],
              correct_reason=0,
              fig=poles, alt="A conjugate pair of pole marks, distances not labeled.",
              preview=["rlc"]),
    ]
    bump(bank)
    dump(bank)


def patch_pole():
    bank = load("pole-zero", "bank")
    retire(bank, "pole-zero-r2-q2")
    retire(bank, "pole-zero-r3-q3")
    real = splane([(-4, 0)], [], "one real pole")
    zero = splane([(-2, 0)], [(-6, 0)], "a zero and a pole")
    bank["questions"] += [
        built("pole-zero", 2, "pole-zero-r2-q4", "num",
              "A transfer function has one real pole at \\(s=-4\\). Its natural term is \\(e^{-4t}\\). What is that term at \\(t=0.5\\ \\mathrm{s}\\)?",
              math.exp(-2), "1",
              "Substitute \\(t=0.5\\): \\(e^{-4\\times 0.5}=e^{-2}\\). The pole location \\(-4\\) is not the value of the term. \\(e^{-0.5}\\) uses the time and drops the pole.",
              real, "One pole mark on the negative real axis."),
        built("pole-zero", 3, "pole-zero-r3-q4", "num",
              "\\(H(s)=(s+6)/(s+2)\\). What is the magnitude of the finite zero?",
              6, "rad/s",
              "The numerator is zero at \\(s=-6\\), so the magnitude is 6. The denominator root \\(-2\\) is the pole. The DC gain is \\(6/2=3\\), which is not the zero.",
              zero, "A pole mark and a zero mark on the real axis, unlabeled."),
    ]
    bump(bank)
    dump(bank)


def patch_tf():
    bank = load("tf", "bank")
    retire(bank, "tf-r4-q2")
    retire(bank, "tf-r4-q3")
    bank["questions"] += [
        built("tf", 4, "tf-r4-q4", "num",
              "A later skill will build this ratio from impedances. For \\(H(s)=7/(s+1)\\), what is the DC gain \\(H(0)\\)?",
              7, "1",
              "DC gain is the ratio at \\(s=0\\): \\(7/1=7\\). The leading 7 is also the high-frequency story only when the degrees match, and here the denominator degree is higher, so the high-frequency gain is 0. Using \\(7/s\\) leaves the variable in the answer.",
              step_response("settled gain", tau=1.0, goal=1.0),
              "A smooth curve that settles to a flat level.",
              preview=["direct-h"]),
        built("tf", 4, "tf-r4-q5", "num",
              "\\(H(s)=(s+6)/(s+1)^2\\). What is the magnitude of the finite zero?",
              6, "rad/s",
              "The only finite zero is the root of \\(s+6\\), at \\(s=-6\\), so the magnitude is 6. The double pole at \\(-1\\) is not a zero. The DC gain \\(6/1=6\\) happens to equal that magnitude here, but the zero is read from the numerator root.",
              splane([(-1, 0)], [(-6, 0)], "zero of a ratio"),
              "A zero mark and a pole mark on the real axis.",
              preview=["pole-zero"]),
    ]
    bump(bank)
    dump(bank)


def patch_freq():
    bank = load("freq-resp-circuits", "bank")
    retire(bank, "freq-resp-circuits-r4-q3")
    bank["questions"] += [
        built("freq-resp-circuits", 4, "freq-resp-circuits-r4-q4", "num",
              "A circuit transfer function is \\(G(jf)=100/(1+jf/10\\ \\mathrm{kHz})\\). The input is a tone of amplitude 1 at 100 kHz. What is the output amplitude?",
              100 / math.sqrt(101), "1",
              "At 100 kHz the ratio \\(f/f_p\\) is 10, so \\(|G|=100/\\sqrt{1+100}=100/\\sqrt{101}\\). The output amplitude is that gain times 1. The DC gain 100 ignores the pole. One decade above the pole is about a factor of ten, not a complete stop.",
              step_response("falling gain", tau=1.0, goal=1.0, fn=lambda t: 1 / math.sqrt(1 + t * t), t_end=4),
              "A curve of magnitude that falls as frequency increases.",
              preview=["opamp-fr"]),
    ]
    bump(bank)
    dump(bank)


def patch_rlc():
    bank = load("rlc", "bank")
    retire(bank, "rlc-r4-q3")
    bank["questions"] += [
        built("rlc", 4, "rlc-r4-q4", "num",
              "A series RLC circuit has quality factor \\(Q=8\\). A later amplifier skill meets this same \\(Q\\). What is the damping ratio \\(\\zeta=1/(2Q)\\)?",
              1 / 16, "1",
              "Series resonance uses \\(\\zeta=1/(2Q)\\). With \\(Q=8\\) that is \\(1/16\\). Using \\(1/Q\\) drops the 2. Using \\(Q/2\\) inverts the formula. \\(Q=1/2\\) would be critical damping, and this \\(Q\\) is much higher, so \\(\\zeta\\) is well below 1.",
              splane([(-0.5, 3.9), (-0.5, -3.9)], [], "series poles"),
              "A conjugate pair of pole marks close to the imaginary axis.",
              preview=["opamp-fr"]),
    ]
    bump(bank)
    dump(bank)


def patch_mech():
    bank = load("lti-mech", "bank")
    for qid in ("lti-mech-r1-q1", "lti-mech-r1-q3", "lti-mech-r3-q2", "lti-mech-r4-q1"):
        retire(bank, qid)
    fig = mass_spring("mass spring damper")
    alt = "A mass tied to a wall by a spring and a damper."
    bank["questions"] += [
        built("lti-mech", 1, "lti-mech-r1-q4", "order",
              "A force \\(u\\) pushes a mass \\(m\\) on a spring \\(k\\) and a damper \\(b\\). Order the path from the free body to \\(\\zeta\\).",
              [
                  "Draw the applied force, and draw the spring and damper opposing the motion.",
                  "Write \\(m\\ddot y + b\\dot y + ky = u\\).",
                  "Read \\(\\omega_n\\) as \\(\\sqrt{k/m}\\).",
                  "Read \\(\\zeta\\) as \\(b/(2\\sqrt{km})\\).",
              ],
              "The free body fixes the signs before the standard form exists. \\(\\omega_n\\) is read from \\(k\\) and \\(m\\) before \\(\\zeta\\), because the damping ratio divides by \\(2\\sqrt{km}\\). Putting the damper on the same side as \\(u\\) would make the motion grow.",
              fig, alt),
        built("lti-mech", 1, "lti-mech-r1-q5", "find_error",
              "A student writes the equation of a mass, spring, and damper. Exactly one step is wrong.",
              [
                  "The spring force on the mass opposes the displacement.",
                  "The damper force on the mass opposes the velocity.",
                  "Newton's law sets mass times acceleration equal to the sum of the forces.",
                  "Therefore \\(m\\ddot y = u + b\\dot y + ky\\).",
              ],
              3,
              "The spring and the damper oppose the motion, so they enter Newton's law with minus signs. Moving them to the left side gives \\(m\\ddot y+b\\dot y+ky=u\\). The last step adds those forces to the applied force.",
              reasons=[
                  "Spring and damper oppose the motion, so the equation is \\(m\\ddot y+b\\dot y+ky=u\\).",
                  "The mass multiplies velocity rather than acceleration.",
                  "A damper force depends on displacement, not velocity.",
              ],
              correct_reason=0,
              fig=fig, alt=alt),
        built("lti-mech", 3, "lti-mech-r3-q4", "sym",
              "Write the damping ratio of \\(m\\ddot y+b\\dot y+ky=u\\) using the names \\(b\\), \\(k\\), and \\(m\\).",
              "b/(2*sqrt(k*m))",
              {"b": (0.5, 30.0), "k": (10.0, 400.0), "m": (0.2, 5.0)},
              "\\(\\zeta=b/(2\\sqrt{km})\\). The natural frequency \\(\\sqrt{k/m}\\) is a different combination. Doubling the mass in the denominator without the square root is not this ratio.",
              alternates=["b/(2*(k*m)^0.5)"],
              fig=fig, alt=alt),
        built("lti-mech", 4, "lti-mech-r4-q4", "num",
              "A rotational inertia \\(J=0.05\\ \\mathrm{kg\\,m^2}\\) is held by a torsional spring of stiffness \\(0.2\\ \\mathrm{N\\,m/rad}\\). What is the natural frequency \\(\\sqrt{\\kappa/J}\\)?",
              math.sqrt(0.2 / 0.05), "rad/s",
              "The rotational analog of \\(\\sqrt{k/m}\\) is \\(\\sqrt{\\kappa/J}=\\sqrt{0.2/0.05}=\\sqrt{4}=2\\). Multiplying \\(\\kappa\\) by \\(J\\) is not a frequency. Using \\(\\kappa/J\\) without the square root leaves 4, which is \\(\\omega_n^2\\).",
              mass_spring("rotational analog", damper=False),
              "A spring tied to a mass, standing in for the rotational pair.",
              preview=["sys-id"]),
    ]
    bump(bank)
    dump(bank)


def patch_fb():
    bank = load("fb-amp", "bank")
    for qid in ("fb-amp-r1-q2", "fb-amp-r2-q2", "fb-amp-r2-q3", "fb-amp-r3-q1"):
        retire(bank, qid)
    loop = block_diagram(["A"], "amplifier loop", feedback="f", input_label="r", output_label="y")
    loop_alt = "A forward block and a return path that is subtracted at the input."
    bank["questions"] += [
        built("fb-amp", 1, "fb-amp-r1-q4", "sym",
              "In a non-inverting amplifier, \\(R_2\\) runs from the output to the inverting input and \\(R_1\\) runs from that input to ground. Write the feedback factor \\(f\\) using the names \\(R1\\) and \\(R2\\).",
              "R1/(R1+R2)",
              {"R1": (500.0, 5000.0), "R2": (500.0, 80000.0)},
              "The divider that returns the output to the input is \\(R_1/(R_1+R_2)\\). The ideal closed-loop gain is the reciprocal of that factor. Using \\(R_2/(R_1+R_2)\\) is the other tap of the same divider.",
              alternates=["1/(1+R2/R1)"],
              fig=loop, alt=loop_alt),
        built("fb-amp", 2, "fb-amp-r2-q4", "num",
              "A forward gain \\(A=1000\\) is wrapped by a feedback factor \\(\\beta=0.1\\). The closed-loop gain is \\(A/(1+A\\beta)\\). What is that gain?",
              1000 / 101, "1",
              "The loop gain is \\(1000\\times 0.1=100\\). Negative feedback gives \\(1000/(1+100)=1000/101\\). The ideal gain \\(1/\\beta=10\\) is the large-loop limit, not the finite-\\(A\\) value. Using \\(1+A\\) forgets \\(\\beta\\).",
              loop, alt=loop_alt),
        built("fb-amp", 2, "fb-amp-r2-q5", "order",
              "Order the calculation of the closed-loop gain of a resistive feedback amplifier.",
              [
                  "Read the feedback factor \\(f\\) from the resistor divider.",
                  "Multiply the op-amp gain by \\(f\\) to get the loop gain.",
                  "Add 1 to that loop gain.",
                  "Divide the forward gain by that sum.",
              ],
              "The divider is the feedback path, so \\(f\\) comes first. The loop gain is the product around the loop. Negative feedback puts that product in \\(1+T\\), and the closed-loop gain divides by that sum. Dividing by \\(f\\) alone is the ideal-gain limit, which skips the finite op-amp gain.",
              loop, alt=loop_alt),
        built("fb-amp", 3, "fb-amp-r3-q4", "find_error",
              "A student computes the closed-loop gain of a negative-feedback amplifier. Exactly one step is wrong.",
              [
                  "The feedback factor of the divider is \\(f\\).",
                  "The loop gain is \\(T=A f\\).",
                  "Negative feedback puts the loop gain in the denominator as \\(1+T\\).",
                  "The closed-loop gain is \\(A/(1-A f)\\).",
              ],
              3,
              "The first three steps are the negative-feedback reading. The minus sign in the denominator is positive feedback. The closed-loop gain is \\(A/(1+Af)\\).",
              reasons=[
                  "The minus sign is the positive-feedback formula. Negative feedback adds the loop gain.",
                  "The loop gain should have been \\(A+f\\).",
                  "The ideal closed-loop gain is \\(A\\), not \\(1/f\\).",
              ],
              correct_reason=0,
              fig=loop, alt=loop_alt),
    ]
    bump(bank)
    dump(bank)


def set_section(exp, heading, body, figure=None, alt=None):
    for section in exp["sections"]:
        if section.get("heading") == heading:
            section["body_md"] = body
            if figure is not None:
                section["figure_svg"] = figure
                section["figure_alt"] = alt
            return
    raise SystemExit("missing section " + heading)


def patch_explainers():
    first = load("first-order-sys", "explainer")
    set_section(first, "Where this leads",
                "The same two numbers describe a capacitor charged through a resistor: the product of resistance and capacitance is the time constant, and the cutoff sits at one over that product. A settled step record is enough to read the DC gain and the time constant back out. A second stored quantity brings a second pole, and that pair is a different skill.")
    first["version"] = int(first.get("version") or 1) + 1
    dump(first)

    second = load("second-order-sys", "explainer")
    poles = splane([(-1.75, 6.78), (-1.75, -6.78)], [], "worked poles")
    set_section(second, "The idea",
                "A second-order system has two poles. Two numbers place them. The natural frequency \\(\\omega_n\\) is the distance from the origin to either pole, and it sets the speed of the motion. The damping ratio \\(\\zeta\\) is the cosine of the angle from the negative real axis to the pole, and it decides whether the motion rings.\n\nWhen \\(\\zeta<1\\) the poles are a complex conjugate pair and the free motion oscillates inside a decaying envelope. When \\(\\zeta=1\\) the poles are real and equal, which is critical damping. When \\(\\zeta>1\\) the poles are real and distinct, which is overdamped, and the motion does not ring. The formulas that turn \\(\\zeta\\) into a percent overshoot, a peak time, or a settling time belong to the step-response specifications, not to this placement.")
    set_section(second, "Key equations",
                "Standard form, with a unit DC gain:\n\\[\n\\ddot y + 2\\zeta\\omega_n\\dot y + \\omega_n^2 y = \\omega_n^2 u.\n\\]\nFor \\(\\zeta<1\\) the poles are \\(-\\zeta\\omega_n \\pm j\\omega_d\\) with \\(\\omega_d=\\omega_n\\sqrt{1-\\zeta^2}\\). The real part is \\(-\\zeta\\omega_n\\). Critical damping is the repeated pole \\(-\\omega_n\\). Overdamping splits that pole into two different negative real numbers whose product is \\(\\omega_n^2\\) and whose sum is \\(2\\zeta\\omega_n\\).")
    set_section(second, "Worked example",
                "Take \\(\\omega_n=7\\ \\mathrm{rad/s}\\) and \\(\\zeta=0.25\\). The real part of each pole is \\(7\\times 0.25=1.75\\). The damped frequency is\n\\[\n\\omega_d=7\\sqrt{1-0.0625}=7\\sqrt{0.9375}=6.778\\ \\mathrm{rad/s}.\n\\]\nThe poles are \\(-1.75\\pm j6.778\\). Because \\(\\zeta\\) is below 1, the pair is underdamped. Calling 6.778 the natural frequency uses the imaginary part. Calling 1.75 the natural frequency uses only the real part. The distance from the origin is 7, and that is \\(\\omega_n\\).",
                poles, "A conjugate pair of pole marks in the left half-plane, closer to the imaginary axis than to the real axis.")
    set_section(second, "Common pitfalls",
                "The natural frequency is the distance from the origin, not the ringing frequency. The ringing frequency is \\(\\omega_d\\), which is smaller than \\(\\omega_n\\) whenever \\(\\zeta>0\\). Critical damping is \\(\\zeta=1\\), not the overdamped case. Overdamping is \\(\\zeta>1\\), two distinct real poles. A sign error that puts the pair in the right half-plane is an unstable system, not a lightly damped one.")
    set_section(second, "Where this leads",
                "Step-response specifications turn \\(\\zeta\\) and \\(\\omega_n\\) into rise time, overshoot, and settling time. A series RLC circuit writes the same \\(\\zeta\\) as \\(1/(2Q)\\) next to its resonant frequency. A mass, a damper, and a spring are the same two numbers, with \\(\\omega_n=\\sqrt{k/m}\\) and \\(\\zeta=b/(2\\sqrt{km})\\).")
    second["version"] = int(second.get("version") or 1) + 1
    dump(second)

    step = load("step-resp", "explainer")
    fig = step_response("integral of an impulse", tau=0.8, goal=1.0)
    set_section(step, "The idea",
                "A unit step is the running integral of a unit impulse. Once the impulse has occurred, the step holds the value 1. Linearity moves that identity from the input to the output: the step response is the running integral of the impulse response. For a causal system the integral starts at time 0, because the impulse response is zero before the impulse.\n\nA pulse is two steps. A pulse of height \\(A\\) that turns on at time 0 and turns off at time \\(T\\) is a step of height \\(A\\) at time 0 minus a step of height \\(A\\) at time \\(T\\). Until time \\(T\\) the second step has not started, so the output is only the response to the first step. After time \\(T\\) both steps contribute, and the second one is delayed by \\(T\\).",
                fig, "A smooth curve that rises toward a flat level.")
    set_section(step, "Key equations",
                "\\[\ny_{\\mathrm{step}}(t)=\\int_0^t h(\\lambda)\\,d\\lambda\n\\]\n\\[\nu_{\\mathrm{pulse}}(t)=A\\,u(t)-A\\,u(t-T)\n\\]\nThe output follows the same difference, with the unit-step response in place of \\(u\\). The area of a pulse is its height times its width, and that area is the weight of the impulse that matches a very short pulse.")
    set_section(step, "Worked example",
                "Take the causal impulse response \\(h(t)=22e^{-8t}\\). Its area is \\(22/8=2.75\\), so the unit-step response settles at 2.75. A separate pulse of height 9 that lasts 0.7 s has area \\(9\\times 0.7=6.3\\). That pulse is a step of height 9 minus a step of height 9 that begins at 0.7 s. At \\(t=0.3\\ \\mathrm{s}\\), which is still inside the pulse, the delayed step contributes nothing, and the output is the response to the step of height 9 alone.")
    set_section(step, "Common pitfalls",
                "Integrating the impulse response from the far future back toward the impulse, instead of from 0 up to the time of interest. Subtracting the delayed step during the pulse, before that step exists. Reading a pulse's area from its height and forgetting the width.")
    set_section(step, "Where this leads",
                "The exponential shape of a single real pole, including how far a step has risen after one time constant, is the first-order skill. A circuit then uses the same pulse, built as a difference of steps, when the memory is a capacitor.")
    step["title"] = "Step and pulse response"
    step["version"] = int(step.get("version") or 1) + 1
    dump(step)

    circ = load("lti-circuits", "explainer")
    set_section(circ, "The idea",
                "A circuit of fixed resistors, capacitors, and inductors is linear and time-invariant. Superposition is the working rule: the response to a sum of inputs is the sum of the responses, and a scaled input scales the response. Time invariance says that delaying every input delays the output by the same amount.\n\nConvolution is that rule written as an integral. The impulse response is the response to a unit impulse, and the response to any other input is the input blended against that impulse response. A short pulse acts like an impulse whose weight is the area of the pulse.\n\nLoading is the same idea applied to the resistance a capacitor sees. Independent sources are turned off first: a voltage source becomes a short and a current source becomes an open. The resistance of what remains, times the capacitance, is the time constant. The exponential that uses that time constant is already known from the first-order skill.",
                step_response("linear step", tau=1.0, goal=1.0),
                "A smooth rising curve with no component values.")
    set_section(circ, "Key equations",
                "\\[\ny(a u_1+b u_2)=a\\,y(u_1)+b\\,y(u_2)\n\\]\n\\[\ny(t)=\\int_0^t h(\\lambda)\\,u(t-\\lambda)\\,d\\lambda\n\\]\n\\[\nR_{\\mathrm{th}}=R_1\\parallel R_2=\\frac{R_1 R_2}{R_1+R_2}\n\\]\nThe parallel formula is the resistance at a capacitor node that sees two resistors after the sources are removed.")
    set_section(circ, "Worked example",
                "A capacitor node sees 6 kΩ to a voltage source and 18 kΩ to ground. Turn the voltage source off and it becomes a short, so the two resistors are in parallel: \\(R_{\\mathrm{th}}=(6\\times 18)/(6+18)=4.5\\ \\mathrm{k\\Omega}\\). That is the resistance the capacitor sees. Separately, an input of 1.5 V produces 0.45 V at a linear output, so an input of 6 V produces 1.8 V there, because the circuit scales.")
    set_section(circ, "Common pitfalls",
                "Leaving an independent voltage source in place while measuring the resistance the capacitor sees. Adding the responses of two inputs that were not applied together. Using the full width of a rectangular impulse response at a time when only part of that rectangle has occurred.")
    set_section(circ, "Where this leads",
                "Open-circuit time constants, slew limits, and capacitive loads on amplifier nodes all start from the resistance a capacitor sees and from superposition of the inputs that drive it.")
    circ["version"] = int(circ.get("version") or 1) + 1
    dump(circ)

    pz = load("pole-zero", "explainer")
    set_section(pz, "The idea",
                "Factor a transfer function and the roots separate into zeros, from the numerator, and poles, from the denominator. Each pole \\(p\\) contributes a natural term \\(e^{pt}\\). A real pole at \\(s=-a\\) with \\(a>0\\) contributes \\(e^{-at}\\), which decays. A pole in the right half-plane grows, so the natural motion is unstable. The pole closest to the imaginary axis decays most slowly and usually dominates.\n\nZeros do not create natural terms. They set how strongly each term appears. A zero on top of a pole cancels that term. A zero in the right half-plane makes a step response start in the direction opposite its final value. A complex pair has a natural frequency and a damping ratio, and those two numbers are the second-order skill.")
    set_section(pz, "Key equations",
                "\\[\nH(s)=K\\frac{\\prod (s-z_i)}{\\prod (s-p_k)},\\qquad h(t)=\\sum_k r_k e^{p_k t}\n\\]\nA real pole at \\(-a\\) contributes \\(e^{-at}\\). Cancelling a factor \\((s+a)\\) that sits in both the numerator and the denominator removes that pole and that zero together.")
    set_section(pz, "Worked example",
                "Take a single pole at \\(s=-7\\). The natural term is \\(e^{-7t}\\). At \\(t=1\\ \\mathrm{s}\\) it equals \\(e^{-7}\\approx 0.000912\\). Now take \\(H(s)=(s+8)/((s+8)(s+11))\\). The zero at \\(-8\\) cancels the pole at \\(-8\\), and the natural motion that remains is \\(e^{-11t}\\). The cancelled pair does not add a second decay.",
                splane([(-3, 0)], [], "real pole"),
                "One pole mark on the negative real axis.")
    set_section(pz, "Common pitfalls",
                "Reading stability from the zeros instead of the poles. Treating a cancelled pole-zero pair as if it still contributed \\(e^{pt}\\). Calling the imaginary part of a complex pole the whole story of that pole.")
    set_section(pz, "Where this leads",
                "Pole and zero locations are the break points of a Bode plot. The natural frequency and damping ratio of a complex pair are read in the second-order skill.")
    pz["version"] = int(pz.get("version") or 1) + 1
    dump(pz)

    mech = load("lti-mech", "explainer")
    set_section(mech, "The idea",
                "A mass, a spring, and a viscous damper are linear elements: \\(F=kx\\), \\(F=b\\dot x\\), and \\(F=m\\ddot x\\). Newton's law on one mass gives a constant-coefficient equation, the same shape as any other second-order system. The natural frequency and the damping ratio are already defined. This skill is the map from the hardware numbers onto those two.\n\nA shaft is the rotational copy. Inertia \\(J\\) plays the role of mass, a torsional spring plays the role of \\(k\\), and viscous friction plays the role of \\(b\\). Speed of a shaft with inertia and friction, and no spring, is first order, with time constant \\(J/b\\).",
                mass_spring("worked mechanism"),
                "A mass, a spring, and a damper drawn between a wall and the mass.")
    set_section(mech, "Key equations",
                "\\[\nm\\ddot y+b\\dot y+ky=u,\\qquad \\omega_n=\\sqrt{k/m},\\qquad \\zeta=\\frac{b}{2\\sqrt{km}}\n\\]\n\\[\nJ\\ddot\\theta+\\kappa\\theta=\\tau_{\\mathrm{spring}}\\ \\text{gives}\\ \\omega_n=\\sqrt{\\kappa/J}.\n\\]\nThe signs matter. Spring and damper forces on the mass oppose displacement and velocity.")
    set_section(mech, "Worked example",
                "A 6 kg mass on a spring of 294 N/m with \\(b=21\\ \\mathrm{N\\,s/m}\\) has \\(\\omega_n=\\sqrt{294/6}=7\\ \\mathrm{rad/s}\\) and \\(\\zeta=21/(2\\sqrt{294\\times 6})=0.25\\). The same map on a shaft with \\(J=1.8\\ \\mathrm{kg\\,m^2}\\) and viscous friction \\(0.75\\ \\mathrm{N\\,m\\,s}\\) and no spring gives the first-order time constant \\(1.8/0.75=2.4\\ \\mathrm{s}\\).")
    set_section(mech, "Common pitfalls",
                "Using weight in place of mass. Drawing the damper force in the direction of the velocity, which is positive feedback. Mixing the rotational stiffness with the translational spring in one equation.")
    set_section(mech, "Where this leads",
                "A settled step of this model is one of the records a later identification skill can fit. Cruise control uses the first-order rotational, or translational, drag model as its plant.")
    mech["version"] = int(mech.get("version") or 1) + 1
    dump(mech)

    rc = load("rc-lpf", "explainer")
    set_section(rc, "The idea",
                "A resistor feeding a capacitor is the circuit form of a first-order system. The exponential shape, the 63% point, and the free response are already settled in that skill. What this circuit adds is the time constant \\(\\tau=RC\\), the cutoff \\(1/(RC)\\), and a warning about which resistance to use.\n\nThe capacitor cannot jump, because a jump would take infinite current. It moves from its present voltage toward the voltage a constant source eventually demands. If other resistors touch the capacitor, turn the independent sources off and use the resistance the capacitor sees. A resistor in parallel with the capacitor changes that resistance, and therefore changes both \\(\\tau\\) and the cutoff.")
    rc["title"] = "RC low-pass time constant, cutoff, and source resistance"
    rc["version"] = int(rc.get("version") or 1) + 1
    dump(rc)

    tf = load("tf", "explainer")
    tf["title"] = "Transfer functions"
    tf["version"] = int(tf.get("version") or 1) + 1
    dump(tf)

    rlc = load("rlc", "explainer")
    idea = rlc["sections"][0]["body_md"]
    if "second-order skill" not in idea:
        rlc["sections"][0]["body_md"] = idea + (
            " The three damping cases themselves are the second-order skill. Here the new fact is the series pair \\(\\omega_0=1/\\sqrt{LC}\\) and \\(\\zeta=1/(2Q)\\)."
        )
        rlc["version"] = int(rlc.get("version") or 1) + 1
        dump(rlc)


def report():
    for sid in ("first-order-sys", "step-resp", "rc-lpf", "lti-circuits", "second-order-sys",
                "pole-zero", "tf", "freq-resp-circuits", "rlc", "lti-mech", "fb-amp"):
        bank = load(sid, "bank")
        counts = {r: 0 for r in (1, 2, 3, 4)}
        deep = 0
        for q in bank["questions"]:
            counts[q["round"]] += 1
            if q["type"] in ("symbolic", "order", "error", "multi"):
                deep += 1
        exp = load(sid, "explainer")
        print(f"{sid}: rounds {counts} deep {deep} retired {len(bank.get('retired_questions') or [])} words {words(exp['sections'])}")


def main():
    sample = load("first-order-sys", "bank")
    if any(q.get("id") == SENTINEL for q in sample["questions"]):
        print("already applied")
        report()
        return
    patch_first_order()
    patch_step()
    patch_rc()
    patch_lti_circuits()
    patch_second()
    patch_pole()
    patch_tf()
    patch_freq()
    patch_rlc()
    patch_mech()
    patch_fb()
    patch_explainers()
    report()


if __name__ == "__main__":
    main()
