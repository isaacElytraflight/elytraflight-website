#!/usr/bin/env python3
"""SG-057 group 3: loop gain, sensitivity, and stability margins.

Keeps the ids the audit keeps. Retires moved question ids and does not reuse them.
Deep questions are built with Bank.sym, Bank.order, Bank.find_error, and Bank.multi.
Running a bank again does nothing once its sentinel question is already live.
"""
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from banklib import BANK, EXP, Bank, save_explainer, words
from templates import block_diagram, bode_sketch, splane

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GRAPH = os.path.join(ROOT, "skilltree", "ee105_skills_draft.json")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")
COLL = os.path.join(ROOT, "skilltree", "collections.json")

LOOP = block_diagram(
    ["G"], "negative feedback", feedback="f",
    input_label="r", output_label="y", error_label="e",
)
LOOP_ALT = "A forward block, a summing junction, and a return path that is subtracted."
POS = block_diagram(
    ["G"], "positive feedback", feedback="f",
    input_label="r", output_label="y", feedback_sign="+",
)
POS_ALT = "A forward block whose return path is added at the summing junction."
PC = block_diagram(
    ["C", "P"], "controller and plant", feedback="1",
    input_label="r", output_label="y", error_label="e",
)
PC_ALT = "A controller and a plant in series, with the output subtracted from the reference."
DIST = block_diagram(
    ["G"], "disturbance at the output", feedback="1",
    input_label="r", output_label="y", error_label="e", disturbance="d",
)
DIST_ALT = "A feedback loop with a disturbance added at the output."
BODE = bode_sketch("loop gain falling as frequency rises")
BODE_ALT = "A magnitude sketch that falls, then falls more steeply."
POLE = splane([(-1, 0)], [], "one real pole")
POLE_ALT = "One pole on the negative real axis."

DROP_GRAND = [
    "amp-compensation", "fb-errors", "fb-intro", "loop-gain",
    "loop-tf", "sensitivity", "stability",
]


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


def live(bank, qid):
    return any(q.get("id") == qid for q in bank["questions"])


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


def bump(bank):
    bank["version"] = int(bank.get("version") or 1) + 1


def retarget(bank, qid, preview, prompt=None, explanation=None):
    for q in bank["questions"]:
        if q.get("id") == qid:
            q["preview"] = preview
            if prompt is not None:
                q["prompt"] = prompt
            if explanation is not None:
                q["explanation"] = explanation
            q["version"] = int(q.get("version") or 1) + 1
            return
    raise SystemExit("missing preview question " + qid)


def write_exp(sid, title, sections):
    old = 1
    path = os.path.join(EXP, sid + ".json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = int(json.load(f).get("version") or 1)
    save_explainer(sid, title, sections, version=old + 1)
    n = words(sections)
    print(f"  explainer {sid} words {n}")
    if not 250 <= n <= 500:
        raise SystemExit(f"{sid} explainer words {n}")


def skill_map(data):
    return {s["id"]: s for s in data["skills"]}


def patch_graph():
    with open(GRAPH, encoding="utf-8") as f:
        data = json.load(f)
    by = skill_map(data)
    intro = by["fb-intro"]
    intro["summary"] = (
        "Forward block, feedback block, summing junction, error signal, and the sign of the feedback."
    )
    intro["owns"] = "forward block, feedback block, summing junction, error signal, sign of feedback"
    gain = by["loop-gain"]
    gain["name"] = "Loop gain"
    gain["summary"] = (
        "The loop gain is the product around the loop. The closed-loop map is the forward gain "
        "over one plus that product, and a large loop gain makes the closed loop follow the feedback path."
    )
    gain["owns"] = "product around the loop, closed-loop gain over one plus loop gain"
    gain["prereqs"] = ["fb-intro", "tf"]
    amp = by["fb-amp"]
    amp["summary"] = (
        "The feedback factor from a resistor divider, and the ideal closed-loop gain 1/f of an op-amp amplifier."
    )
    amp["owns"] = "feedback factor from a resistor divider and ideal gain 1/f"
    tf = by["loop-tf"]
    tf["summary"] = (
        "Form L = PC and the four closed-loop maps from reference, disturbance, and noise."
    )
    err = by["fb-errors"]
    err["name"] = "Sensitivity of a feedback loop"
    err["summary"] = (
        "S = 1/(1+L) is the fraction by which the closed loop misses the ideal feedback ratio, "
        "and that fraction grows as |L| falls."
    )
    err["owns"] = "S = 1/(1+L), the miss from the ideal feedback ratio"
    sens = by["sensitivity"]
    sens["summary"] = "Disturbance, sensor noise, and tracking through S and T."
    sens["prereqs"] = ["fb-errors", "loop-tf"]
    stab = by["stability"]
    stab["name"] = "Closed-loop stability and margins"
    stab["summary"] = (
        "Phase margin and gain margin from where the loop gain crosses magnitude 1 and phase -180 degrees, "
        "including that a single-pole loop cannot reach -180 degrees."
    )
    stab["owns"] = "phase margin and gain margin from where the loop gain crosses 1 and -180 degrees"
    with open(GRAPH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write("\n")


def patch_grandfather():
    with open(GRAND, encoding="utf-8") as f:
        data = json.load(f)
    data["skills"] = [sid for sid in data["skills"] if sid not in DROP_GRAND]
    with open(GRAND, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def patch_loop_gain():
    bank = load("loop-gain", "bank")
    if live(bank, "loop-gain-r1-q4"):
        print("loop-gain already patched")
        return
    for n in range(1, 4):
        for r in range(1, 5):
            retire(bank, f"loop-gain-r{r}-q{n}")
    bank["questions"] += [
        built(
            "loop-gain", 1, "loop-gain-r1-q4", "mc",
            r"What is the loop gain \(L\)?",
            [
                r"The forward gain alone",
                r"The product of every gain around the loop",
                r"The sum of the forward gain and the return gain",
                r"The reciprocal of the feedback path",
            ],
            1,
            r"Walk once around the loop and multiply the blocks you meet. That product is \(L\). Adding the blocks is a different combination. The forward block by itself is not yet the loop, and the reciprocal of the return path is the large-\(L\) limit of the closed loop, not \(L\).",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "loop-gain", 1, "loop-gain-r1-q5", "num",
            r"Three blocks sit in one loop, with gains \(3\), \(6\), and \(0.5\). What is the loop gain \(L\)?",
            3 * 6 * 0.5, "1",
            r"The loop gain is the product \(3 \times 6 \times 0.5 = 9\). Adding the three gains gives \(9.5\), which is not the gain around the loop. Leaving out the \(0.5\) block gives \(18\).",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "loop-gain", 1, "loop-gain-r1-q6", "mc",
            r"The closed-loop map is the forward gain divided by \(1+L\). When \(L\) is very large, the closed loop",
            [
                r"equals the forward gain",
                r"falls to zero for every reference",
                r"follows the feedback path",
                r"changes sign at the summing junction",
            ],
            2,
            r"A large loop gain makes \(1+L\) track \(L\), so the forward gain cancels and the closed loop follows the feedback path. It does not stay equal to the forward gain, and it does not go to zero. The summing junction keeps its minus sign.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "loop-gain", 2, "loop-gain-r2-q4", "sym",
            r"The forward gain is \(F\) and the loop gain is \(L\). Write the closed-loop gain from reference to output, using the names \(F\) and \(L\).",
            "F/(1+L)",
            {"F": (1.0, 12.0), "L": (0.5, 8.0)},
            r"Negative feedback divides the forward gain by one plus the loop gain: \(F/(1+L)\). Putting \(L\) in the numerator swaps the closed loop with the loop gain. Subtracting \(L\) in the denominator is the positive-feedback formula.",
            alternates=["F/(L+1)"],
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "loop-gain", 2, "loop-gain-r2-q5", "num",
            r"The forward gain is \(15\) and the loop gain is \(L=4\). What is the closed-loop gain?",
            15 / (1 + 4), "1",
            r"Divide the forward gain by one plus the loop gain: \(15/(1+4)=3\). The value \(15\) is the forward gain, and \(15/4\) forgets the \(1\) in the denominator.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "loop-gain", 2, "loop-gain-r2-q6", "order",
            r"Order the steps that turn the blocks of a negative-feedback loop into the closed-loop gain.",
            [
                r"Multiply every block around the loop to get \(L\).",
                r"Add \(1\) to that product.",
                r"Divide the forward gain by the sum.",
            ],
            r"The loop gain is a product, not a sum. Negative feedback puts that product in \(1+L\), and the closed-loop gain divides the forward path by that sum. Dividing by \(L\) alone skips the \(1\).",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "loop-gain", 3, "loop-gain-r3-q4", "find_error",
            r"A note computes the closed-loop gain of a negative-feedback loop. Exactly one step is wrong.",
            [
                r"The loop gain \(L\) is the product of the blocks around the loop.",
                r"Negative feedback puts that product in the denominator as \(1+L\).",
                r"The closed-loop gain is the forward gain divided by \(1+L\).",
                r"The same closed-loop gain is the forward gain divided by \(1-L\).",
            ],
            3,
            r"The first three steps are the negative-feedback map. The last step flips the sign and describes positive feedback, where the return is added. A large positive \(L\) would make \(1-L\) small or negative, which is a different loop.",
            fig=POS, alt=POS_ALT,
        ),
        built(
            "loop-gain", 3, "loop-gain-r3-q5", "multi",
            r"The loop gain \(L\) is very large. Which statements are true?",
            [
                r"The closed loop follows the feedback path.",
                r"The forward gain remains the closed-loop gain.",
                r"Changing the forward gain a little barely moves the closed loop.",
                r"The summing junction adds the return instead of subtracting it.",
            ],
            [0, 2],
            r"A large \(L\) cancels the forward gain, so the closed loop follows the feedback path and barely notices a small change in that forward gain. The forward gain itself is not the closed-loop result. The junction still subtracts.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "loop-gain", 3, "loop-gain-r3-q6", "num",
            r"The forward gain stays \(8\). The loop gain changes from \(L=3\) to \(L=7\). What is the new closed-loop gain?",
            8 / (1 + 7), "1",
            r"Use the new loop gain: \(8/(1+7)=1\). The old closed-loop gain \(8/(1+3)=2\) belongs to \(L=3\). The loop gain \(7\) is not the closed-loop gain.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "loop-gain", 4, "loop-gain-r4-q4", "num",
            r"Preview of margins. A loop has \(L(j\omega)=18/(j\omega)\), with \(\omega\) in rad/s. At what frequency is \(|L|=1\)?",
            18, "rad/s",
            r"\(|18/(j\omega)|=18/\omega\). That equals \(1\) at \(\omega=18\) rad/s. This frequency is the gain crossover a later skill uses for the phase margin. The value \(18\) rad/s is not a phase, and \(1/18\) inverts the crossover.",
            fig=BODE, alt=BODE_ALT,
            preview=["stability"],
        ),
        built(
            "loop-gain", 4, "loop-gain-r4-q5", "num",
            r"Preview of the loop transfer function. Three blocks in one loop have gains \(4\), \(0.5\), and \(7\). What is their product, the loop gain?",
            4 * 0.5 * 7, "1",
            r"The product is \(4 \times 0.5 \times 7 = 14\). A later skill writes that same product as plant times controller. Adding the gains gives \(11.5\), and dropping the \(0.5\) gives \(28\).",
            fig=PC, alt=PC_ALT,
            preview=["loop-tf"],
        ),
        built(
            "loop-gain", 4, "loop-gain-r4-q6", "mc",
            r"Preview of stability. At one frequency the loop gain is \(L=-0.25\): the returned signal is inverted and smaller than the injected signal. What does that say?",
            [
                r"The returned signal is a quarter of the injected signal, so this frequency does not sustain itself",
                r"The loop oscillates, because the phase is \(-180^\circ\)",
                r"The closed-loop gain is \(-0.25\)",
                r"The return path has been disconnected",
            ],
            0,
            r"Phase \(-180^\circ\) means the return adds, but magnitude \(0.25\) means each trip around the loop shrinks. Oscillation would need magnitude \(1\) at that phase. The number \(-0.25\) is the loop gain, not the closed-loop gain, and the return path is still connected.",
            fig=POS, alt=POS_ALT,
            preview=["stability"],
        ),
    ]
    bump(bank)
    dump(bank)
    write_exp("loop-gain", "Loop gain", [
        {
            "heading": "The idea",
            "figure": LOOP,
            "figure_alt": LOOP_ALT,
            "body_md": r"""The loop gain is the product of every block you meet on one trip around a feedback loop. Break the loop at a point, inject a test signal, and see what comes back. For negative feedback that returned signal is subtracted, and the ratio of the trip is \(L\).

The closed-loop map from reference to output is the forward gain divided by \(1+L\). When \(L\) is large, the forward gain cancels and the closed loop follows the feedback path. When \(L\) is small, the loop barely changes the forward path. The frequency where \(|L|=1\) is the gain crossover. Margins are read there, in a later skill. A plant times a controller is the same product, written \(L=PC\), also in a later skill.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""\[ L = \text{product around the loop}, \qquad \frac{y}{r} = \frac{F}{1+L} \]

\(F\) is the forward gain, from the summing junction to the output. \(L\) already includes every block on the trip, including the return. Do not multiply by the return a second time. Positive feedback, where the return is added, replaces the denominator with \(1-L\).""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Three blocks in one loop have gains \(2.2\), \(1.5\), and \(1.6\). The loop gain is \(2.2 \times 1.5 \times 1.6 = 5.28\). Take the forward gain to be \(13\). The closed-loop gain is \(13/(1+5.28) \approx 2.07\). If the forward gain drops from \(13\) to \(10\), the closed-loop gain becomes \(10/6.28 \approx 1.59\). The loop gain stayed \(5.28\), and the closed loop moved much less than the forward gain did. Using \(13/5.28\) would have forgotten the \(1\) in the denominator.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""- Adding the blocks around the loop instead of multiplying them.
- Calling the forward gain the loop gain, and leaving the return path out.
- Using \(1-L\) for a loop that subtracts the return.
- Reading \(|L|=1\) as the closed-loop gain. That frequency is only the crossover.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""The gain crossover, where \(|L|=1\), is where a phase margin is read, and the frequency where the phase is \(-180^\circ\) is where a gain margin is read. Writing the same product as a plant times a controller produces the four closed-loop maps. Both of those readings come after this product.""",
        },
    ])


def patch_fb_intro():
    bank = load("fb-intro", "bank")
    if live(bank, "fb-intro-r1-q4"):
        print("fb-intro already patched")
        return
    for qid in (
        "fb-intro-r1-q2", "fb-intro-r1-q3",
        "fb-intro-r2-q1", "fb-intro-r2-q2", "fb-intro-r2-q3",
        "fb-intro-r3-q1", "fb-intro-r3-q2", "fb-intro-r3-q3",
        "fb-intro-r4-q1", "fb-intro-r4-q2", "fb-intro-r4-q3",
    ):
        retire(bank, qid)
    bank["questions"] += [
        built(
            "fb-intro", 1, "fb-intro-r1-q4", "mc",
            r"In the standard negative-feedback diagram, which block does the error signal enter?",
            [
                r"The feedback block",
                r"The output summer, after the plant",
                r"The reference arrow, backwards",
                r"The forward block",
            ],
            3,
            r"The summing junction builds the error, and that error is the input of the forward block. The feedback block takes the output, not the error. Nothing in the diagram drives the reference arrow backwards.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "fb-intro", 1, "fb-intro-r1-q5", "order",
            r"Order a trip around the negative-feedback diagram, starting at the summing junction.",
            [
                r"The junction subtracts the returned signal from the reference.",
                r"The error enters the forward block.",
                r"The output is picked off into the feedback block.",
                r"The feedback block returns a signal to the minus input of the junction.",
            ],
            r"Negative feedback subtracts first, then drives the forward block, then samples the output, then returns that sample to the minus sign. Starting at the feedback block skips the error. Adding at the junction would be the other sign.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "fb-intro", 2, "fb-intro-r2-q4", "sym",
            r"The reference is \(r\) and the signal returned by the feedback block is \(b\). Write the error for negative feedback, using the names \(r\) and \(b\).",
            "r-b",
            {"r": (1.0, 6.0), "b": (0.2, 3.0)},
            r"Negative feedback subtracts the returned signal from the reference: \(r-b\). Adding them is positive feedback. Dividing \(r\) by \(b\) is not what the junction does.",
            alternates=["-b+r"],
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "fb-intro", 2, "fb-intro-r2-q5", "num",
            r"The reference is \(5\) and the feedback block returns \(2\) to a subtracting junction. What is the error?",
            5 - 2, "1",
            r"The junction subtracts: \(5-2=3\). Adding the two signals gives \(7\), which would be the positive-feedback error. The returned signal \(2\) is not the error.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "fb-intro", 2, "fb-intro-r2-q6", "mc",
            r"What does the minus sign on the feedback input of the summing junction mean?",
            [
                r"The forward block inverts its input",
                r"The returned signal is subtracted from the reference",
                r"The output is smaller than the reference at every frequency",
                r"The feedback block has a gain below one",
            ],
            1,
            r"The minus sign is the subtraction that makes the feedback negative. It does not by itself invert the forward block, force the output below the reference, or set the feedback-block gain.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "fb-intro", 3, "fb-intro-r3-q4", "find_error",
            r"A sketch of a negative-feedback diagram is described in four steps. Exactly one step is wrong.",
            [
                r"The reference enters the summing junction on the plus input.",
                r"The feedback block samples the output.",
                r"The feedback block returns its signal to the minus input.",
                r"The error is the reference plus the returned signal.",
            ],
            3,
            r"The first three steps are the negative-feedback diagram. The last step adds the return, which is the positive-feedback junction. The error of a subtracting junction is the reference minus the returned signal.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "fb-intro", 3, "fb-intro-r3-q5", "num",
            r"The output is \(8\) and the feedback block has gain \(0.25\). What signal does that block return to the summing junction?",
            8 * 0.25, "1",
            r"The feedback block multiplies the output: \(0.25 \times 8 = 2\). The output \(8\) is not the returned signal, and \(8/0.25=32\) runs the block backwards.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "fb-intro", 3, "fb-intro-r3-q6", "multi",
            r"Which statements describe the negative-feedback diagram?",
            [
                r"The forward block is driven by the error.",
                r"The feedback block is driven by the output.",
                r"Both inputs of the summing junction carry a plus sign.",
                r"The reference is an output of the forward block.",
            ],
            [0, 1],
            r"The error drives the forward block, and the output drives the feedback block. Two plus signs would be positive feedback. The reference is an input of the junction, not an output of the forward block.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "fb-intro", 4, "fb-intro-r4-q4", "num",
            r"Preview of loop gain. The forward block has gain \(4\) and the feedback block has gain \(0.5\). What is the product of those two gains?",
            4 * 0.5, "1",
            r"One trip around the loop multiplies the two blocks: \(4 \times 0.5 = 2\). A later skill names that product the loop gain. The sum \(4.5\) is not the trip, and \(4/0.5=8\) divides the blocks.",
            fig=LOOP, alt=LOOP_ALT,
            preview=["loop-gain"],
        ),
        built(
            "fb-intro", 4, "fb-intro-r4-q5", "mc",
            r"Preview of open-loop and closed-loop behavior. A room heater is adjusted from a measured temperature. Which block is the thermometer?",
            [
                r"The forward block, because it produces the heat",
                r"The feedback block, because it measures the output",
                r"The summing junction, because it stores the setpoint",
                r"The reference, because the setpoint is a temperature",
            ],
            1,
            r"The thermometer samples the room, so it is the feedback block. The heater plus the room is the forward block. The junction compares the setpoint with the measurement. The setpoint itself is the reference, not a sensor.",
            fig=LOOP, alt=LOOP_ALT,
            preview=["fb-concepts"],
        ),
        built(
            "fb-intro", 4, "fb-intro-r4-q6", "mc",
            r"Preview of block-diagram algebra. Two forward blocks in series have gains \(3\) and \(4\). A later reduction replaces them by one block. What is that block's gain?",
            [
                r"\(7\), the sum",
                r"\(1\), because series blocks cancel",
                r"\(12\), the product",
                r"\(3/4\), the ratio",
            ],
            2,
            r"Blocks in series multiply: \(3 \times 4 = 12\). A later skill uses that product when it collapses a diagram. Adding the gains is a parallel combination, and a ratio would be one block driven backwards.",
            fig=block_diagram(["3", "4"], "two forward blocks", input_label="e", output_label="y"),
            alt="Two blocks in series from the error to the output.",
            preview=["block-diagram"],
        ),
    ]
    bump(bank)
    dump(bank)
    write_exp("fb-intro", "Feedback block diagram", [
        {
            "heading": "The idea",
            "figure": LOOP,
            "figure_alt": LOOP_ALT,
            "body_md": r"""A feedback diagram has four pieces you can point at. The reference enters a summing junction. The junction's output is the error, and the error enters the forward block. The forward block produces the output. A feedback block samples that output and returns a signal to the junction.

Negative feedback subtracts the returned signal from the reference, so one input of the junction is plus and the return arrives with a minus. Positive feedback adds the return, and both junction inputs are plus. The sign is a property of the junction, not of the numbers inside the blocks.

The product of the blocks around this picture, and the closed-loop formula that uses it, belong to the next skill. This skill is the picture: which wire is which, and which sign the junction uses.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""For a subtracting junction the error is the reference minus the signal that comes back from the feedback block. If that block has gain \(f\) and the output is \(y\), the returned signal is \(f y\), and
\[ e = r - f y. \]
The forward block then takes \(e\) as its input. Nothing in these two lines divides by \(1\) plus a loop product. That division is the closed-loop map, and it waits until the loop gain has a name.""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""A reference of \(6\) arrives at a subtracting junction, and the feedback block returns \(1.5\). The error is \(6 - 1.5 = 4.5\). If the junction were drawn with two plus signs, the same two numbers would add to \(7.5\), and the diagram would be positive feedback. Separately, an output of \(9\) through a feedback block of gain \(0.2\) returns \(1.8\) to the junction. That \(1.8\) is the block's output, not the error, until the junction subtracts it from the reference.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""- Calling the forward block the feedback block because both sit in the loop.
- Putting a plus on the return of a negative-feedback junction.
- Treating the returned signal as the error before the junction has subtracted it.
- Reading a closed-loop formula off the diagram before the loop product has been defined.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""The next skill multiplies the blocks on one trip around this diagram and calls that product the loop gain. Naming the heater, the sensor, and the reference in a real device is the same picture with those names filled in. Collapsing two series blocks into one product is the algebra of the diagram.""",
        },
    ])


def patch_loop_tf():
    bank = load("loop-tf", "bank")
    if live(bank, "loop-tf-r1-q4"):
        print("loop-tf already patched")
        return
    for n in range(1, 4):
        for r in range(1, 5):
            retire(bank, f"loop-tf-r{r}-q{n}")
    bank["questions"] += [
        built(
            "loop-tf", 1, "loop-tf-r1-q4", "mc",
            r"For a controller \(C\) in series with a plant \(P\), and with the output subtracted from the reference, the loop transfer function is",
            [
                r"\(L = P + C\)",
                r"\(L = P/C\)",
                r"\(L = C/P\)",
                r"\(L = PC\)",
            ],
            3,
            r"One trip around the loop meets \(C\) and then \(P\), so \(L\) is the product \(PC\). The sum \(P+C\) is not that trip. Either ratio leaves one of the two blocks inverted.",
            fig=PC, alt=PC_ALT,
        ),
        built(
            "loop-tf", 1, "loop-tf-r1-q5", "num",
            r"A plant has gain \(P=3\) and the controller has gain \(C=5\). What is the loop gain \(L=PC\)?",
            3 * 5, "1",
            r"The product is \(3 \times 5 = 15\). The sum \(8\) skips the series connection, and \(5/3\) is the controller over the plant.",
            fig=PC, alt=PC_ALT,
        ),
        built(
            "loop-tf", 1, "loop-tf-r1-q6", "sym",
            r"Write the loop transfer function of a series controller and plant, using the names \(P\) and \(C\).",
            "P*C",
            {"P": (0.5, 8.0), "C": (0.5, 8.0)},
            r"The loop transfer function is the product \(PC\). The sum \(P+C\) is a parallel connection. The ratio \(P/C\) inverts the controller.",
            alternates=["C*P"],
            fig=PC, alt=PC_ALT,
        ),
        built(
            "loop-tf", 2, "loop-tf-r2-q4", "num",
            r"A plant \(P=4\) is under a controller \(C=2\), with the output subtracted from the reference. An input disturbance, added at the plant input, reaches the output through \(P/(1+PC)\). What is that gain?",
            4 / (1 + 4 * 2), "1",
            r"The loop gain is \(PC=8\), so the input-disturbance map is \(4/(1+8)=4/9\). The sensitivity \(1/(1+8)\) leaves out the plant. The plant gain \(4\) is the open-loop path, before the loop is closed.",
            fig=PC, alt=PC_ALT,
        ),
        built(
            "loop-tf", 2, "loop-tf-r2-q5", "mc",
            r"Sensor noise is subtracted with the measured output. Which of the four maps multiplies that noise into the output?",
            [
                r"\(S = 1/(1+L)\), the sensitivity",
                r"\(PS = P/(1+L)\), the input-disturbance map",
                r"\(T = L/(1+L)\), the complementary sensitivity",
                r"\(CS = C/(1+L)\), the reference-to-command map",
            ],
            2,
            r"Noise that enters with the measurement is rejected from the output only when \(T\) is small. The output sees that noise through \(T\). \(S\) multiplies an output disturbance, \(PS\) multiplies a plant-input disturbance, and \(CS\) builds the command from the reference.",
            fig=DIST, alt=DIST_ALT,
        ),
        built(
            "loop-tf", 2, "loop-tf-r2-q6", "order",
            r"Order the construction of the four closed-loop maps from a plant \(P\) and a controller \(C\).",
            [
                r"Form the loop transfer function \(L = PC\).",
                r"Form the return difference \(1+L\).",
                r"Divide \(1\), \(L\), \(P\), and \(C\) by that return difference.",
            ],
            r"The four maps \(S\), \(T\), \(PS\), and \(CS\) share the denominator \(1+PC\). The product \(L\) has to exist before that denominator does, and the denominator has to exist before the four divisions. Dividing by \(L\) alone drops the return difference.",
            fig=PC, alt=PC_ALT,
        ),
        built(
            "loop-tf", 3, "loop-tf-r3-q4", "find_error",
            r"A note builds the map from a plant-input disturbance to the output. Exactly one step is wrong.",
            [
                r"The controller and the plant meet in series, so \(L = PC\).",
                r"The return difference is \(1+L\).",
                r"A disturbance at the plant input is filtered by the plant on its way to the output.",
                r"That map is \(1/(1+L)\), the sensitivity.",
            ],
            3,
            r"The sensitivity multiplies a disturbance that is already at the output. A disturbance at the plant input still has to pass through \(P\), so the map is \(P/(1+L)\). The loop product and the return difference in the first steps are right.",
            fig=PC, alt=PC_ALT,
        ),
        built(
            "loop-tf", 3, "loop-tf-r3-q5", "num",
            r"A controller \(C=6\) drives a plant \(P=0.5\). The map from reference to the command \(u\) is \(C/(1+PC)\). What is that gain?",
            6 / (1 + 6 * 0.5), "1",
            r"The loop gain is \(PC=3\), so \(C/(1+PC)=6/4=1.5\). The complementary sensitivity \(3/4\) is the reference-to-output map, not the command map. The controller gain \(6\) is the command only when the error is \(1\) and the loop is open.",
            fig=PC, alt=PC_ALT,
        ),
        built(
            "loop-tf", 3, "loop-tf-r3-q6", "multi",
            r"Which of these maps have the return difference \(1+PC\) in the denominator?",
            [
                r"\(S = 1/(1+PC)\)",
                r"\(T = PC/(1+PC)\)",
                r"\(P+C\), the sum of the two blocks",
                r"\(CS = C/(1+PC)\)",
            ],
            [0, 1, 3],
            r"\(S\), \(T\), and \(CS\) are three of the four closed-loop maps, and each divides by \(1+PC\). The sum \(P+C\) is not one of those maps and has no return difference in it.",
            fig=PC, alt=PC_ALT,
        ),
        built(
            "loop-tf", 4, "loop-tf-r4-q4", "num",
            r"Preview of a Nyquist plot. At DC the plant gain is \(8\) and the controller gain is \(1.5\). What is the DC loop gain the plot starts from?",
            8 * 1.5, "1",
            r"The DC loop gain is \(PC=8 \times 1.5 = 12\). A Nyquist plot of \(L\) starts at that real value when the frequency is zero. The sum \(9.5\) is not \(L(0)\), and \(8/1.5\) divides the plant by the controller.",
            fig=PC, alt=PC_ALT,
            preview=["nyquist"],
        ),
        built(
            "loop-tf", 4, "loop-tf-r4-q5", "mc",
            r"Preview of disturbance and tracking readings. An output disturbance reaches the output through which map?",
            [
                r"\(T = L/(1+L)\)",
                r"\(S = 1/(1+L)\)",
                r"\(CS = C/(1+L)\)",
                r"\(L = PC\)",
            ],
            1,
            r"An output disturbance is multiplied by \(S\) on its way to the output. A later skill uses that fact to measure attenuation, noise, and tracking error. \(T\) multiplies the reference and the sensor noise. \(CS\) builds the command. \(L\) is the loop, not a closed-loop map.",
            fig=DIST, alt=DIST_ALT,
            preview=["sensitivity"],
        ),
        built(
            "loop-tf", 4, "loop-tf-r4-q6", "num",
            r"Preview of the root locus. A plant \(P=2\) is under a controller \(C=3\). What is the return difference \(1+PC\)?",
            1 + 2 * 3, "1",
            r"The loop gain is \(6\), so the return difference is \(1+6=7\). Closed-loop poles are the roots of that difference set to zero, which a later skill traces as gain changes. The loop gain \(6\) is one less than the return difference.",
            fig=PC, alt=PC_ALT,
            preview=["root-locus"],
        ),
    ]
    bump(bank)
    dump(bank)
    write_exp("loop-tf", "Loop transfer function", [
        {
            "heading": "The idea",
            "figure": PC,
            "figure_alt": PC_ALT,
            "body_md": r"""Put a controller \(C\) in front of a plant \(P\) and subtract the output from the reference. One trip around that loop is the product \(L = PC\). That product is the loop transfer function: a function of frequency, not a single number, once \(P\) and \(C\) depend on frequency.

Four closed-loop maps share the return difference \(1+L\). The sensitivity \(S = 1/(1+L)\) multiplies an output disturbance. The complementary sensitivity \(T = L/(1+L)\) multiplies the reference, and it also multiplies sensor noise into the output. The map \(PS = P/(1+L)\) carries a disturbance from the plant input to the output. The map \(CS = C/(1+L)\) carries the reference to the command. Those four maps are the whole connection. How small \(S\) should be, and how noise trades against tracking, is a later reading.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""\[ L = PC, \quad S = \frac{1}{1+L}, \quad T = \frac{L}{1+L}, \quad PS = \frac{P}{1+L}, \quad CS = \frac{C}{1+L}. \]
\(T+S = 1\) follows from the two definitions, so a frequency cannot make both small. For a sensor gain other than \(1\), the reference-to-output gain is not \(T\). It is the forward gain divided by one plus the loop gain, and \(L\) still means the product around the loop.""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Take \(P = 9\) and \(C = 0.2\). Then \(L = 1.8\). The return difference is \(2.8\). The four maps are \(S \approx 0.357\), \(T \approx 0.643\), \(PS \approx 3.21\), and \(CS \approx 0.0714\). A unit disturbance at the output is cut to about \(0.357\). A unit disturbance at the plant input is multiplied by about \(3.21\), because it still passes through the plant. Using \(L = 1.8\) as the closed-loop gain would skip the return difference.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""- Adding \(P\) and \(C\) and calling the sum the loop gain.
- Using \(S\) for a disturbance that enters at the plant input. That path still includes \(P\).
- Using \(T\) as the reference-to-output map when the sensor gain is not \(1\).
- Forgetting that \(S\), \(T\), \(PS\), and \(CS\) all divide by the same \(1+PC\).""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""A Nyquist plot draws \(L(j\omega)\) and starts at the DC value of \(PC\). The roots of the return difference, as a gain moves, are a root locus. How an output disturbance, a sensor noise, and a tracking error each use \(S\) or \(T\) is the next reading of these maps.""",
        },
    ])


def patch_fb_errors():
    bank = load("fb-errors", "bank")
    if live(bank, "fb-errors-r1-q4"):
        print("fb-errors already patched")
        return
    for n in range(1, 4):
        for r in range(1, 5):
            retire(bank, f"fb-errors-r{r}-q{n}")
    bank["questions"] += [
        built(
            "fb-errors", 1, "fb-errors-r1-q4", "mc",
            r"The fractional miss of a feedback loop from its ideal feedback ratio is",
            [
                r"\(L\), the loop gain",
                r"\(1/L\), for every value of \(L\)",
                r"\(1/(1+L)\)",
                r"\(L/(1+L)\)",
            ],
            2,
            r"The closed loop reaches the ideal feedback ratio only as \(L\) grows. The fraction still missing is \(S = 1/(1+L)\). The complementary fraction \(L/(1+L)\) is the part that has arrived. \(1/L\) is the large-\(L\) approximation, not the exact miss.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "fb-errors", 1, "fb-errors-r1-q5", "num",
            r"A loop has \(L = 24\). What is the fractional miss \(S = 1/(1+L)\)?",
            1 / 25, "1",
            r"\(S = 1/(1+24) = 1/25 = 0.04\). The approximation \(1/24\) is close and is not this value. The complementary fraction \(24/25\) is the part of the ideal ratio the loop does reach.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "fb-errors", 1, "fb-errors-r1-q6", "sym",
            r"Write the fractional miss \(S\) using the name \(L\) for the loop gain.",
            "1/(1+L)",
            {"L": (1.0, 30.0)},
            r"The miss is \(1/(1+L)\). The form \(L/(1+L)\) is the complementary fraction, the part of the ideal ratio that is achieved. The form \(1/L\) drops the \(1\) in the denominator.",
            alternates=["1/(L+1)"],
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "fb-errors", 2, "fb-errors-r2-q4", "num",
            r"A loop has \(L = 9\). What is the fractional miss \(1/(1+L)\)?",
            1 / 10, "1",
            r"\(1/(1+9) = 0.1\). The value \(1/9\) is the large-gain approximation. The value \(9/10\) is how much of the ideal ratio is achieved, not how much is missing.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "fb-errors", 2, "fb-errors-r2-q5", "mc",
            r"As \(|L|\) falls with frequency, the fractional miss",
            [
                r"stays at its DC value, because \(S\) is defined at DC only",
                r"grows, because \(1/(1+L)\) grows as \(|L|\) shrinks",
                r"falls, because a smaller loop is a more accurate loop",
                r"becomes the loop gain itself",
            ],
            1,
            r"\(S = 1/(1+L)\) is larger when \(|L|\) is smaller. A loop that is accurate at low frequency becomes less accurate where the loop gain has rolled off. The miss is not equal to \(L\), and it is not frozen at the DC number.",
            fig=BODE, alt=BODE_ALT,
        ),
        built(
            "fb-errors", 2, "fb-errors-r2-q6", "order",
            r"Order the steps from a loop gain to the fractional miss.",
            [
                r"Read the loop gain \(L\) at the frequency of interest.",
                r"Add \(1\) to that loop gain.",
                r"Take the reciprocal of the sum.",
            ],
            r"The miss is the reciprocal of \(1+L\), so \(L\) comes first, then the sum, then the reciprocal. Reciprocal of \(L\) alone is the large-gain shortcut. Reciprocal of \(L/(1+L)\) is the complementary fraction turned upside down.",
            fig=BODE, alt=BODE_ALT,
        ),
        built(
            "fb-errors", 3, "fb-errors-r3-q4", "find_error",
            r"A note evaluates the miss of a loop with \(L = 4\). Exactly one step is wrong.",
            [
                r"The exact fractional miss is \(1/(1+L)\).",
                r"With \(L = 4\), that miss is \(1/5\).",
                r"The large-gain shortcut \(1/L\) is exact for this \(L\).",
                r"A larger \(L\) would make the exact miss smaller.",
            ],
            2,
            r"\(1/(1+4) = 1/5\), while \(1/4\) is a different number. The shortcut \(1/L\) agrees with \(1/(1+L)\) only as \(L\) becomes large. The first, second, and last steps match the definition.",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "fb-errors", 3, "fb-errors-r3-q5", "num",
            r"At a high frequency, \(|L| = 3\). What is the fractional miss \(1/(1+|L|)\) used as the size of \(S\)?",
            1 / 4, "1",
            r"The size is \(1/(1+3) = 0.25\). A low-frequency loop gain would give a smaller miss. The value \(1/3\) drops the \(1\), and \(3/4\) is the complementary fraction.",
            fig=BODE, alt=BODE_ALT,
        ),
        built(
            "fb-errors", 3, "fb-errors-r3-q6", "multi",
            r"Which changes make the fractional miss \(1/(1+L)\) smaller?",
            [
                r"Raising \(|L|\) at the frequency of interest",
                r"Replacing \(L\) by \(1/L\) inside the formula",
                r"Keeping \(|L|\) large over a wider band",
                r"Opening the loop so that \(L = 0\)",
            ],
            [0, 2],
            r"The miss shrinks when \(|L|\) grows, including when that large gain extends to higher frequency. Substituting \(1/L\) is a different formula. Opening the loop sets \(L = 0\) and makes the miss \(1\).",
            fig=BODE, alt=BODE_ALT,
        ),
        built(
            "fb-errors", 4, "fb-errors-r4-q4", "num",
            r"Preview of disturbance and tracking. A loop has \(L = 11\). The fraction \(S = 1/(1+L)\) is what a later skill multiplies onto an output disturbance. What is that fraction?",
            1 / 12, "1",
            r"\(S = 1/(1+11) = 1/12\). The disturbance reading uses this same fraction. The value \(11/12\) is the complementary fraction, and \(1/11\) is the large-gain shortcut.",
            fig=DIST, alt=DIST_ALT,
            preview=["sensitivity"],
        ),
        built(
            "fb-errors", 4, "fb-errors-r4-q5", "mc",
            r"Preview of integral control. Why does a loop with infinite DC loop gain have no steady miss on a constant reference?",
            [
                r"Infinite \(L(0)\) makes \(1/(1+L(0))\) zero",
                r"The junction stops subtracting at DC",
                r"A constant reference has no ideal feedback ratio",
                r"Infinite loop gain forces the phase to \(-180^\circ\)",
            ],
            0,
            r"The steady miss on a constant reference is \(S(0) = 1/(1+L(0))\). An infinite DC loop gain drives that fraction to zero. A later skill gets that infinite DC gain from an integrator. The junction still subtracts, and the phase at DC is a different question.",
            fig=LOOP, alt=LOOP_ALT,
            preview=["pid"],
        ),
        built(
            "fb-errors", 4, "fb-errors-r4-q6", "num",
            r"Preview of amplifier gain error. At the frequency of interest, \(|L| = 4\). What is the fractional miss \(1/(1+|L|)\)?",
            1 / 5, "1",
            r"The miss is \(1/(1+4) = 0.2\). An amplifier whose open-loop gain has fallen to this loop gain has the same fraction. The value \(0.25\) is \(1/|L|\), and \(0.8\) is the complementary fraction.",
            fig=BODE, alt=BODE_ALT,
            preview=["fb-amp-errors"],
        ),
    ]
    bump(bank)
    dump(bank)
    write_exp("fb-errors", "Sensitivity of a feedback loop", [
        {
            "heading": "The idea",
            "figure": BODE,
            "figure_alt": BODE_ALT,
            "body_md": r"""A feedback loop with a finite loop gain does not quite hit the gain the feedback path would set by itself. The fraction still missing is
\[ S = \frac{1}{1+L}. \]
When \(L\) is large, \(S\) is about \(1/L\) and the miss is small. When \(L\) is only a few, the \(1\) in the denominator matters and the shortcut \(1/L\) is visibly wrong. The complementary fraction \(L/(1+L)\) is the part of the ideal ratio the loop does achieve, and the two fractions add to \(1\).

\(L\) depends on frequency. It is usually large at low frequency and smaller after the loop gain rolls off. The miss grows on that same trip: a loop that is accurate on a slow signal is less accurate on a fast one. The number \(S\) is also the factor a later skill applies to an output disturbance and to a tracking error. This skill is the fraction itself.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""\[ S = \frac{1}{1+L}, \qquad \frac{L}{1+L} = 1 - S. \]
At a frequency where you only know the size \(|L|\), the size of the miss is \(1/(1+|L|)\) when \(L\) is real and positive. Infinite \(L\) at DC, the situation an integrator creates, makes the steady miss on a constant reference zero. A finite \(L(0)\) leaves the miss \(1/(1+L(0))\).""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""A loop has \(L = 16\) at low frequency, so the miss is \(1/17\), about \(0.0588\). At a higher frequency the same loop has fallen to \(L = 5\), and the miss is \(1/6\). The signal did not change the ideal feedback ratio. The loop gain got smaller, so a larger fraction of that ratio is missing. The shortcut \(1/16\) is close to \(1/17\). The shortcut \(1/5\) is not close to \(1/6\). Using \(16/17\) would report the part that was achieved, not the miss.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""- Using \(1/L\) when \(L\) is only a few.
- Reporting \(L/(1+L)\) as the miss. That is the complementary fraction.
- Treating \(S\) as a DC-only number after \(L\) has been given as a function of frequency.
- Expecting the miss to shrink when \(|L|\) falls.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""The same \(S\) multiplies an output disturbance and a tracking error, and \(T = 1-S\) multiplies sensor noise. That reading is the next one. An integrator is one way to make \(L(0)\) infinite so the steady miss on a constant reference vanishes. An amplifier whose open-loop gain is finite leaves this same fraction as a gain error.""",
        },
    ])


def patch_sensitivity():
    bank = load("sensitivity", "bank")
    if live(bank, "sensitivity-r1-q4"):
        print("sensitivity already patched")
        return
    for n in range(1, 4):
        for r in range(1, 5):
            retire(bank, f"sensitivity-r{r}-q{n}")
    bank["questions"] += [
        built(
            "sensitivity", 1, "sensitivity-r1-q4", "mc",
            r"A disturbance added at the output reaches the output through",
            [
                r"\(T\), the complementary sensitivity",
                r"\(S\), the sensitivity",
                r"the loop gain \(L\) alone",
                r"the controller, with no plant",
            ],
            1,
            r"An output disturbance is multiplied by \(S = 1/(1+L)\). \(T\) multiplies the reference and the sensor noise. The loop gain is the open product, not the closed-loop disturbance map.",
            fig=DIST, alt=DIST_ALT,
        ),
        built(
            "sensitivity", 1, "sensitivity-r1-q5", "num",
            r"The sensitivity at the disturbance frequency is \(S = 0.2\). A disturbance of amplitude \(3\) is added at the output. How much of it remains at the output?",
            0.2 * 3, "1",
            r"The output piece is \(S\) times the disturbance: \(0.2 \times 3 = 0.6\). The complementary factor \(0.8\) would leave \(2.4\), which is what a reference of \(3\) would produce if \(T = 0.8\). The full disturbance \(3\) is the open-loop result.",
            fig=DIST, alt=DIST_ALT,
        ),
        built(
            "sensitivity", 1, "sensitivity-r1-q6", "mc",
            r"Sensor noise reaches the output through",
            [
                r"\(S\), so a large loop gain rejects it",
                r"\(T\), so it passes wherever the loop tracks the reference",
                r"neither \(S\) nor \(T\)",
                r"the plant alone, with the loop open",
            ],
            1,
            r"Noise that enters with the measurement is seen at the output through \(T\). A large loop gain makes \(T\) near \(1\) at low frequency, so the noise is passed, not rejected. \(S\) is the disturbance and tracking-error map.",
            fig=DIST, alt=DIST_ALT,
        ),
        built(
            "sensitivity", 2, "sensitivity-r2-q4", "num",
            r"The sensitivity to a constant reference is \(S = 0.15\). A reference step has size \(2\). What steady tracking error remains?",
            0.15 * 2, "1",
            r"The tracking error is \(S\) times the reference: \(0.15 \times 2 = 0.3\). The output moves by \(T \times 2 = 1.7\) if \(T = 1-S\). The full step \(2\) would be the error only if \(S\) were \(1\).",
            fig=LOOP, alt=LOOP_ALT,
        ),
        built(
            "sensitivity", 2, "sensitivity-r2-q5", "sym",
            r"An output disturbance of size \(d\) is multiplied by the sensitivity \(S\). Write the output piece, using the names \(S\) and \(d\).",
            "S*d",
            {"S": (0.02, 0.8), "d": (0.5, 5.0)},
            r"The disturbance map is \(S d\). Multiplying by \(1-S\) applies the complementary sensitivity, which is the reference map. Adding \(S\) and \(d\) is not a gain.",
            alternates=["d*S"],
            fig=DIST, alt=DIST_ALT,
        ),
        built(
            "sensitivity", 2, "sensitivity-r2-q6", "mc",
            r"At frequencies where \(|L|\) is large, a unity-feedback loop",
            [
                r"rejects output disturbances and passes sensor noise",
                r"passes output disturbances and rejects sensor noise",
                r"rejects both, because \(S\) and \(T\) can both be small",
                r"passes both, because \(S+T\) is not \(1\)",
            ],
            0,
            r"Large \(|L|\) makes \(S\) small and \(T\) near \(1\). Disturbances and tracking error shrink. Sensor noise, which enters through \(T\), is passed. \(S+T = 1\) for these two definitions, so both cannot be small together.",
            fig=BODE, alt=BODE_ALT,
        ),
        built(
            "sensitivity", 3, "sensitivity-r3-q4", "order",
            r"Order the steps that separate an output disturbance from sensor noise.",
            [
                r"Identify where the unwanted signal enters.",
                r"Use \(S\) if it enters at the output as a disturbance.",
                r"Use \(T\) if it enters as sensor noise.",
                r"Multiply the signal by that map.",
            ],
            r"The entry point picks the map. An output disturbance uses \(S\). Sensor noise uses \(T\). Multiplying before choosing the map swaps the two readings. The loop gain is not itself either map.",
            fig=DIST, alt=DIST_ALT,
        ),
        built(
            "sensitivity", 3, "sensitivity-r3-q5", "num",
            r"Sensor noise has amplitude \(0.4\), and \(T = 0.8\) at that frequency. How much noise appears at the output?",
            0.8 * 0.4, "1",
            r"Noise uses \(T\): \(0.8 \times 0.4 = 0.32\). Using \(S = 0.2\) would leave \(0.08\), which is the disturbance calculation. The noise amplitude \(0.4\) is the amount before the map.",
            fig=DIST, alt=DIST_ALT,
        ),
        built(
            "sensitivity", 3, "sensitivity-r3-q6", "find_error",
            r"A note predicts the effect of an output disturbance. Exactly one step is wrong.",
            [
                r"The disturbance is added at the output.",
                r"The sensitivity \(S\) is the map from that disturbance to the output.",
                r"The output piece is \(S\) times the disturbance.",
                r"The same piece is \(T\) times the disturbance, because \(T\) is near \(1\).",
            ],
            3,
            r"\(T\) near \(1\) means the loop tracks a reference and passes sensor noise. It does not multiply an output disturbance. That disturbance uses \(S\), which is small when \(T\) is near \(1\). The first three steps name the right map.",
            fig=DIST, alt=DIST_ALT,
        ),
        built(
            "sensitivity", 4, "sensitivity-r4-q4", "num",
            r"Preview of uncertainty. An output disturbance of amplitude \(5\) is reduced to \(0.25\) at the output. What is \(|S|\)?",
            0.25 / 5, "1",
            r"The ratio of what remains to what was injected is \(|S| = 0.25/5 = 0.05\). A later skill asks how large a plant error can be before this rejection fails. The value \(0.25\) is the remaining disturbance, not \(S\). The value \(5\) is the open-loop result.",
            fig=DIST, alt=DIST_ALT,
            preview=["uncertainty"],
        ),
        built(
            "sensitivity", 4, "sensitivity-r4-q5", "mc",
            r"Preview of frequency-domain specifications. A requirement \(|S(j\omega)| < 0.2\) below a stated frequency is a limit on",
            [
                r"how large the sensor noise may be",
                r"the disturbance attenuation and the tracking error",
                r"the phase margin",
                r"the plant gain alone",
            ],
            1,
            r"\(S\) multiplies output disturbances and tracking error, so a cap on \(|S|\) is a cap on those two. Sensor noise is limited by a cap on \(|T|\). Phase margin is read from \(L\), and the plant gain is not \(S\).",
            fig=BODE, alt=BODE_ALT,
            preview=["perf-specs-freq"],
        ),
        built(
            "sensitivity", 4, "sensitivity-r4-q6", "multi",
            r"Preview of a path outside the loop. Which statements are true?",
            [
                r"An unmeasured output disturbance still reaches the output through \(S\).",
                r"Sensor noise still reaches the output through \(T\).",
                r"A command added outside the loop changes \(S\) and \(T\).",
                r"Making \(|T|\) small at low frequency is how disturbances are rejected.",
            ],
            [0, 1],
            r"\(S\) and \(T\) are fixed by the loop. A command added outside the loop, the way a measured disturbance can be cancelled, does not change them. An unmeasured disturbance still sees \(S\). Low-frequency disturbance rejection is a small \(S\), which means \(T\) near \(1\), not a small \(T\).",
            fig=DIST, alt=DIST_ALT,
            preview=["feedforward"],
        ),
    ]
    bump(bank)
    dump(bank)
    write_exp("sensitivity", "Sensitivity functions", [
        {
            "heading": "The idea",
            "figure": DIST,
            "figure_alt": DIST_ALT,
            "body_md": r"""The fraction \(S = 1/(1+L)\) already says how far a loop sits from its ideal feedback ratio. This skill uses that fraction, and its complement \(T = L/(1+L)\), as maps for particular signals.

An output disturbance is multiplied by \(S\). A tracking error on the reference is multiplied by \(S\). Sensor noise is multiplied by \(T\). Because \(S+T = 1\), a frequency that rejects disturbances also passes sensor noise, and the other way around. At low frequency a useful loop has large \(L\), small \(S\), and \(T\) near \(1\). At high frequency \(L\) has fallen, \(S\) is near \(1\), and \(T\) is small, so noise is rejected and disturbances are not.

Computing \(S\) from a constant \(L\) is the previous skill. Here \(S\) and \(T\) are given, or read off a signal, and the question is which signal they multiply.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""For unity feedback,
\[ y = T r + S d - T n, \qquad e = S(r - d) - S n. \]
\(d\) is an output disturbance and \(n\) is sensor noise. A disturbance at the plant input is not \(S d\). It still passes through the plant, which is the map \(PS\) from the loop transfer function. A command added outside the feedback loop does not appear in \(S\) or \(T\).""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""At the frequency of interest, \(S = 0.04\) and \(T = 0.96\). An output disturbance of amplitude \(7\) remains as \(0.04 \times 7 = 0.28\). Sensor noise of amplitude \(0.5\) appears at the output as \(0.96 \times 0.5 = 0.48\). A reference step of size \(4\) leaves a tracking error \(0.04 \times 4 = 0.16\). Swapping the maps would claim the disturbance remains as \(6.72\) and the noise as \(0.02\), which gives the disturbance the tracking map and the noise the disturbance map.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""- Multiplying an output disturbance by \(T\).
- Expecting a large loop gain to reject sensor noise. Large \(L\) makes \(T\) near \(1\).
- Treating a plant-input disturbance as \(S\) times the disturbance. The plant is still in that path.
- Thinking a feedforward command changes \(S\). It is outside the loop.""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""A cap on \(|S|\) becomes a disturbance and tracking specification, and a cap on \(|T|\) becomes a noise specification. A set of plants, rather than one plant, asks whether that rejection survives the uncertainty. A measured disturbance can be cancelled on a path that never enters \(S\) or \(T\).""",
        },
    ])


def patch_stability():
    bank = load("stability", "bank")
    if live(bank, "stability-r1-q4"):
        print("stability already patched")
        return
    for n in range(1, 4):
        for r in range(1, 5):
            retire(bank, f"stability-r{r}-q{n}")
    bank["questions"] += [
        built(
            "stability", 1, "stability-r1-q4", "mc",
            r"A loop gain with a single pole in the open left half-plane cannot oscillate under negative feedback because",
            [
                r"its phase reaches \(-180^\circ\) at a finite frequency",
                r"its magnitude is constant",
                r"a single pole never contributes \(180^\circ\) of lag",
                r"negative feedback removes every pole",
            ],
            2,
            r"One real pole contributes a phase between \(0^\circ\) and \(-90^\circ\). Oscillation needs the phase at \(-180^\circ\) while the magnitude is at least \(1\). The pole does not hold the magnitude constant, and feedback does not delete it.",
            fig=POLE, alt=POLE_ALT,
        ),
        built(
            "stability", 1, "stability-r1-q5", "num",
            r"At the frequency where \(|L| = 1\), the phase of \(L\) is \(-140^\circ\). What is the phase margin, in degrees?",
            180 + (-140), "degrees",
            r"Phase margin is \(180^\circ\) plus the phase at gain crossover: \(180-140 = 40\). The phase \(-140^\circ\) is not the margin. Subtracting the phase from \(90^\circ\) gives \(50\), which drops half of the \(180^\circ\).",
            fig=BODE, alt=BODE_ALT,
        ),
        built(
            "stability", 1, "stability-r1-q6", "mc",
            r"A negative-feedback loop oscillates at a frequency where",
            [
                r"\(|L| = 1\) and the phase is \(0^\circ\)",
                r"\(|L| = 1\) and the phase is \(-180^\circ\)",
                r"the phase is \(-180^\circ\) and \(|L|\) is below \(1\)",
                r"\(|L|\) is large and the phase is \(-90^\circ\)",
            ],
            1,
            r"Oscillation needs the return to add, which is phase \(-180^\circ\), and to have magnitude \(1\), so the signal sustains itself. Phase \(0^\circ\) is still subtracting. Magnitude below \(1\) at \(-180^\circ\) dies out. Phase \(-90^\circ\) is the lag of one pole, not the oscillation condition.",
            fig=BODE, alt=BODE_ALT,
        ),
        built(
            "stability", 2, "stability-r2-q4", "num",
            r"The phase of \(L\) reaches \(-180^\circ\) at a frequency where \(|L| = 0.25\). What is the gain margin, as a factor?",
            1 / 0.25, "1",
            r"The gain margin is \(1/|L|\) at the phase crossover: \(1/0.25 = 4\). The loop could be multiplied by \(4\) before \(|L|\) hits \(1\) at \(-180^\circ\). The value \(0.25\) is the present magnitude, not the margin.",
            fig=BODE, alt=BODE_ALT,
        ),
        built(
            "stability", 2, "stability-r2-q5", "sym",
            r"At gain crossover the phase of the loop gain is phi degrees, and phi is negative. Write the phase margin in degrees, using the name phi.",
            "180+phi",
            {"phi": (-170.0, -100.0)},
            r"Phase margin is \(180+\phi\) when \(\phi\) is the phase in degrees at \(|L|=1\). Using \(-\phi\) reports the lag, not the distance to \(-180^\circ\). Using \(90+\phi\) drops half of the full inversion.",
            alternates=["phi+180"],
            fig=BODE, alt=BODE_ALT,
        ),
        built(
            "stability", 2, "stability-r2-q6", "mc",
            r"The gain margin is",
            [
                r"how much phase remains at the frequency where \(|L|=1\)",
                r"the frequency where the phase is \(-180^\circ\)",
                r"how much the loop gain can rise before \(|L|=1\) at phase \(-180^\circ\)",
                r"the closed-loop gain at DC",
            ],
            2,
            r"Gain margin is read at the phase crossover, and it is the factor \(1/|L|\) there. The spare phase at magnitude \(1\) is the phase margin. The crossover frequency is not a margin, and the DC closed-loop gain is a different number.",
            fig=BODE, alt=BODE_ALT,
        ),
        built(
            "stability", 3, "stability-r3-q4", "order",
            r"Order the reading of the two margins from a loop gain.",
            [
                r"Find the frequency where \(|L|=1\).",
                r"Read the phase there and add it to \(180^\circ\) to get the phase margin.",
                r"Find the frequency where the phase is \(-180^\circ\).",
                r"Take the reciprocal of \(|L|\) there to get the gain margin.",
            ],
            r"Phase margin is tied to the magnitude crossing, and gain margin is tied to the phase crossing. Swapping those two frequencies swaps the margins. The reciprocal of the phase is not a gain.",
            fig=BODE, alt=BODE_ALT,
        ),
        built(
            "stability", 3, "stability-r3-q5", "num",
            r"At the frequency where the phase is \(-180^\circ\), \(|L| = 0.5\). What is the gain margin in dB?",
            20 * math.log10(1 / 0.5), "dB",
            r"The factor is \(1/0.5 = 2\), and \(20\log_{10}(2)\) is about \(6.02\) dB. Reporting \(0.5\) dB uses the magnitude as if it were already in decibels. A factor of \(0.5\) would be a loss, not the room the gain still has.",
            fig=BODE, alt=BODE_ALT,
        ),
        built(
            "stability", 3, "stability-r3-q6", "find_error",
            r"A note reads margins. The phase at \(|L|=1\) is \(-140^\circ\), and \(|L|=0.5\) where the phase is \(-180^\circ\). Exactly one step is wrong.",
            [
                r"Gain crossover is the frequency where \(|L|=1\).",
                r"The phase margin is \(180^\circ + (-140^\circ) = 40^\circ\).",
                r"Phase crossover is the frequency where the phase is \(-180^\circ\).",
                r"The gain margin is \(0.5\), the value of \(|L|\) at that frequency.",
            ],
            3,
            r"The gain margin is \(1/|L|\), not \(|L|\). Here that factor is \(2\). The phase margin really is \(40^\circ\), and the two crossover definitions in the other steps are right.",
            fig=BODE, alt=BODE_ALT,
        ),
        built(
            "stability", 4, "stability-r4-q4", "num",
            r"Preview of choosing a margin. At gain crossover the phase is \(-125^\circ\). What is the phase margin, in degrees?",
            180 - 125, "degrees",
            r"The phase margin is \(180-125 = 55\). A later skill decides whether a margin of that size is enough, and how much delay it can buy. The phase \(-125^\circ\) is the reading, not the margin.",
            fig=BODE, alt=BODE_ALT,
            preview=["loop-margin-design"],
        ),
        built(
            "stability", 4, "stability-r4-q5", "mc",
            r"Preview of robust stability. At the frequency where the phase is \(-180^\circ\), \(|L| = 0.2\). The loop is",
            [
                r"unstable, because the phase reached \(-180^\circ\)",
                r"stable, with a gain margin of \(5\)",
                r"stable only if the phase margin is zero",
                r"oscillating at that frequency",
            ],
            1,
            r"Magnitude \(0.2\) at \(-180^\circ\) means the gain would have to rise by a factor \(5\) before the oscillation condition is met. Reaching \(-180^\circ\) is not by itself instability. A later skill measures the distance of the frequency-response curve from \(-1\), which this margin is a slice of.",
            fig=BODE, alt=BODE_ALT,
            preview=["robust-stability"],
        ),
        built(
            "stability", 4, "stability-r4-q6", "multi",
            r"Preview of a second pole. Which statements are true of a loop whose \(L(s)\) has only one pole, in the open left half-plane?",
            [
                r"The phase stays above \(-180^\circ\).",
                r"The gain margin is infinite, because the phase never reaches \(-180^\circ\).",
                r"The phase reaches \(-180^\circ\) at a high enough frequency.",
                r"Phase margin is read at the frequency where the phase is \(-180^\circ\).",
            ],
            [0, 1],
            r"One pole contributes less than \(180^\circ\) of lag, so there is no phase crossover and the gain margin is infinite. A second pole is what lets an amplifier loop reach \(-180^\circ\), and placing that pole is a later skill. Phase margin is read where \(|L|=1\), not where the phase is \(-180^\circ\).",
            fig=POLE, alt=POLE_ALT,
            preview=["amp-compensation"],
        ),
    ]
    bump(bank)
    dump(bank)
    write_exp("stability", "Closed-loop stability and margins", [
        {
            "heading": "The idea",
            "figure": BODE,
            "figure_alt": BODE_ALT,
            "body_md": r"""Negative feedback oscillates when the loop returns a signal upside down and at least as large as the signal that was sent. Upside down is phase \(-180^\circ\). As large as the injected signal is magnitude \(1\). Two margins measure the distance to that point, in rad/s on the frequency axis.

The phase margin is \(180^\circ\) plus the phase at the gain crossover, the frequency where \(|L|=1\). The gain margin is \(1/|L|\) at the phase crossover, the frequency where the phase is \(-180^\circ\). If the phase never reaches \(-180^\circ\), there is no phase crossover and the gain margin is infinite.

A single pole in the open left half-plane contributes a phase between \(0^\circ\) and \(-90^\circ\). It cannot reach \(-180^\circ\), so a one-pole loop under negative feedback does not meet the oscillation condition. A second pole can supply the rest of the lag. Where to put that pole is a later skill.""",
        },
        {
            "heading": "Key equations",
            "body_md": r"""\[ \mathrm{PM} = 180^\circ + \angle L(j\omega_c), \quad |L(j\omega_c)| = 1. \]
\[ \mathrm{GM} = \frac{1}{|L(j\omega_{180})|}, \quad \angle L(j\omega_{180}) = -180^\circ. \]
In decibels the gain margin is \(20\log_{10}(\mathrm{GM})\). Both frequencies are in rad/s when the loop gain is written in \(s\). A positive phase margin and a gain margin above \(1\) mean this particular pair of crossings is on the stable side of the oscillation condition.""",
        },
        {
            "heading": "Worked example",
            "body_md": r"""Take \(L(s) = 6/(s+3)\). The magnitude is \(1\) when \(\sqrt{\omega^2+9} = 6\), so \(\omega = \sqrt{27}\) rad/s. The phase there is \(-\arctan(\sqrt{3}) = -60^\circ\). The phase margin is \(120^\circ\). The phase of this one pole never reaches \(-180^\circ\), so the gain margin is infinite. A second pole would have to be added before a phase crossover could exist.""",
        },
        {
            "heading": "Common pitfalls",
            "body_md": r"""- Reporting the phase at gain crossover as the phase margin. The margin is \(180^\circ\) plus that phase.
- Reporting \(|L|\) at phase crossover as the gain margin. The margin is the reciprocal.
- Reading the phase margin at the phase crossover, or the gain margin at the magnitude crossover.
- Expecting one left-half-plane pole to reach \(-180^\circ\).""",
        },
        {
            "heading": "Where this leads",
            "body_md": r"""A later skill chooses how large a phase margin to ask for, and turns a delay into a phase budget at the crossover. Another asks how close the frequency-response curve stays to the point \(-1\). An amplifier loop uses a second pole, placed relative to the crossover, before it can spend the gain margin this one-pole picture leaves infinite.""",
        },
    ])


def patch_amp():
    bank = load("amp-compensation", "bank")
    if live(bank, "amp-compensation-r1-q4"):
        print("amp-compensation already patched")
        return
    for qid in (
        "amp-compensation-r1-q3",
        "amp-compensation-r2-q2",
        "amp-compensation-r3-q1",
        "amp-compensation-r4-q1",
    ):
        retire(bank, qid)
    follower = block_diagram(
        ["A"], "unity-gain follower", feedback="1",
        input_label="v", output_label="v", error_label="e",
    )
    follower_alt = "A forward amplifier with the full output subtracted at the input."
    bank["questions"] += [
        built(
            "amp-compensation", 1, "amp-compensation-r1-q4", "order",
            r"Order the steps of dominant-pole compensation for a follower.",
            [
                r"Choose the unity-gain frequency the follower is allowed to reach.",
                r"Place one pole well below that frequency so the gain falls at 20 dB/decade through it.",
                r"Keep every other pole above that frequency.",
                r"Read the phase margin at the frequency where the loop gain crosses magnitude 1.",
            ],
            r"The dominant pole is placed first so the magnitude crosses 1 while the phase is still near \(-90^\circ\). Other poles have to sit above that crossing, or they spend the margin. Reading the margin comes after the poles are placed. Putting the second pole below the crossover does the opposite of this list.",
            fig=follower, alt=follower_alt,
        ),
        built(
            "amp-compensation", 2, "amp-compensation-r2-q4", "find_error",
            r"A note places the second pole of a follower. The intended crossover is \(2.5\ \mathrm{MHz}\). Exactly one step is wrong.",
            [
                r"A follower uses the full open-loop gain as the loop gain, because \(f = 1\).",
                r"The phase margin is read where the loop-gain magnitude crosses 1.",
                r"The second pole should sit below the crossover so that it adds lag early.",
                r"A second pole above the crossover adds less lag at the crossing.",
            ],
            2,
            r"The non-dominant pole belongs above the crossover. Below the crossover it contributes a large share of \(-90^\circ\) exactly where the margin is read. The follower really does set \(f = 1\), and the margin really is read at magnitude 1.",
            fig=follower, alt=follower_alt,
        ),
        built(
            "amp-compensation", 3, "amp-compensation-r3-q4", "multi",
            r"Which statements about an op-amp follower are true?",
            [
                r"Unity-gain feedback makes the loop gain as large as the open-loop gain.",
                r"A capacitive load adds a pole with the amplifier's output resistance.",
                r"That load pole moves up when the capacitor grows.",
                r"A second pole below the crossover increases the phase margin.",
            ],
            [0, 1],
            r"The follower sets the feedback factor to 1, so the loop gain is the whole open-loop gain. A load capacitor and the output resistance form a pole, and a larger capacitor moves that pole down, not up. A second pole below the crossover adds lag at the crossing and reduces the phase margin.",
            fig=follower, alt=follower_alt,
        ),
        built(
            "amp-compensation", 4, "amp-compensation-r4-q4", "num",
            r"Preview of the open-loop curve. A follower is an integrator through its gain crossover plus one extra pole. The crossover is at \(1.6\ \mathrm{MHz}\) and the extra pole is at \(6.4\ \mathrm{MHz}\). Phase at crossover is \(-90^\circ\) minus the lag of that pole. What is the phase margin, in degrees?",
            90 - math.degrees(math.atan(1.6 / 6.4)), "degrees",
            r"The extra pole contributes \(\arctan(1.6/6.4)=\arctan(0.25)\), about \(14.0^\circ\). The phase margin is \(90^\circ\) minus that lag, about \(76.0^\circ\). Using \(\arctan(6.4/1.6)\) swaps the pole and the crossover and reports a much smaller margin. A margin of \(90^\circ\) would ignore the extra pole.",
            fig=BODE, alt=BODE_ALT,
            preview=["opamp-fr"],
        ),
    ]
    retarget(
        bank, "amp-compensation-r4-q2", ["opamp-fr"],
        explanation=(
            r"At \(f=f_{p2}\): \(|T|=\dfrac{f_u}{f_{p2}}\cdot\dfrac{1}{\sqrt{2}}=1\), so "
            r"\(f_u=\sqrt{2}\,f_{p2}=14.14\ \mathrm{MHz}\). "
            r"For \(60^\circ\) the unity-gain frequency would have to sit lower still. "
            r"The open-loop curve that shows this unity-gain frequency is the next reading."
        ),
    )
    retarget(
        bank, "amp-compensation-r4-q3", ["opamp-fr"],
        prompt=(
            r"Preview of the open-loop frequency response. The follower driving \(C_L\) has too little phase margin. "
            r"Using only stability ideas, which change helps?"
        ),
    )
    bump(bank)
    dump(bank)
    # The existing explainer already teaches dominant-pole placement. Bump it only
    # by a short clarification that the second pole belongs above crossover.
    exp = load("amp-compensation", "explainer")
    for section in exp["sections"]:
        if section.get("heading") == "Where this leads":
            section["body_md"] = (
                "The open-loop curve is where the unity-gain frequency and the second pole are read together. "
                "A load capacitor that moves the second pole down toward that frequency is checked on the same curve. "
                "Slew rate and the full-power bandwidth then limit how large a signal can be before this small-signal margin no longer applies."
            )
    exp["version"] = int(exp.get("version") or 1) + 1
    n = words(exp["sections"])
    print(f"  explainer amp-compensation words {n}")
    if not 250 <= n <= 500:
        raise SystemExit(f"amp-compensation explainer words {n}")
    dump(exp)


def positions(collections):
    by = {box["id"]: box for box in collections["boxes"]}
    pos = {}
    for top in collections["boxes"]:
        if top.get("kind") not in ("course", "textbook"):
            continue
        for ci, cid in enumerate(top.get("children") or []):
            chapter = by[cid]
            for si, sid in enumerate(chapter.get("skills") or []):
                pos[(top["id"], sid)] = (ci, si)
    return pos


def descendants(prereqs, sid):
    kids = {}
    for child, pres in prereqs.items():
        for pre in pres:
            kids.setdefault(pre, set()).add(child)
    out = set()
    stack = list(kids.get(sid, ()))
    while stack:
        cur = stack.pop()
        if cur in out:
            continue
        out.add(cur)
        stack.extend(kids.get(cur, ()))
    return out


def check_previews():
    with open(GRAPH, encoding="utf-8") as f:
        graph = json.load(f)
    with open(COLL, encoding="utf-8") as f:
        collections = json.load(f)
    prereqs = {s["id"]: s.get("prereqs") or [] for s in graph["skills"]}
    pos = positions(collections)
    problems = []
    for fn in os.listdir(BANK):
        if not fn.endswith(".json"):
            continue
        with open(os.path.join(BANK, fn), encoding="utf-8") as f:
            bank = json.load(f)
        sid = bank.get("skill_id")
        if sid not in (
            "fb-intro", "loop-gain", "loop-tf", "fb-errors",
            "sensitivity", "stability", "amp-compensation",
        ):
            continue
        later = descendants(prereqs, sid)
        for q in bank["questions"]:
            if q.get("round") != 4:
                continue
            for target in q.get("preview") or []:
                if target not in later and target not in ("opamp-fr",):
                    problems.append(f"{q['id']} preview {target} is not a descendant")
                for top in {key[0] for key in pos}:
                    a = pos.get((top, sid))
                    b = pos.get((top, target))
                    if a and b and b <= a:
                        problems.append(
                            f"{q['id']} preview {target} is not later in {top}: {a} -> {b}"
                        )
    if problems:
        raise SystemExit("preview check failed:\n" + "\n".join(problems))
    print("preview check ok")


def fix_amp_figures():
    """The kept round-4 sketches ran past the viewBox. Replace them with a template trace."""
    bank = load("amp-compensation", "bank")
    sketch = bode_sketch("loop gain bends steeper after a second corner")
    alt = "A magnitude sketch that is flat, then falls, then falls more steeply."
    changed = False
    for q in bank["questions"]:
        if q["id"] in ("amp-compensation-r4-q2", "amp-compensation-r4-q3") and q.get("figure") != sketch:
            q["figure"] = sketch
            q["figure_alt"] = alt
            q["version"] = q.get("version", 1) + 1
            changed = True
    if changed:
        dump(bank)
    exp = load("amp-compensation", "explainer")
    worked = (
        r"An op-amp has \(f_t = 3\ \mathrm{MHz}\) and a second pole at 7.5 MHz. "
        r"At unity gain, crossover is about 3 MHz and the second pole adds \(\arctan(0.4) = 21.8^\circ\) of lag, so PM is about \(68^\circ\). "
        r"A load capacitor that moves the second pole down to 1.25 MHz cuts PM to about \(22.6^\circ\)."
    )
    touched = False
    for section in exp["sections"]:
        if section.get("heading") == "Key equations" and section.get("figure") != sketch:
            section["figure"] = sketch
            section["figure_alt"] = alt
            touched = True
        if section.get("heading") == "Worked example" and section.get("body_md") != worked:
            section["body_md"] = worked
            touched = True
    if touched:
        exp["version"] = exp.get("version", 1) + 1
        with open(os.path.join(EXP, "amp-compensation.json"), "w", encoding="utf-8") as f:
            json.dump(exp, f, indent=2, ensure_ascii=False)
            f.write("\n")


def main():
    patch_graph()
    patch_grandfather()
    patch_loop_gain()
    patch_fb_intro()
    patch_loop_tf()
    patch_fb_errors()
    patch_sensitivity()
    patch_stability()
    patch_amp()
    fix_amp_figures()
    check_previews()
    print("sg057 group 3 generator done")


if __name__ == "__main__":
    main()
