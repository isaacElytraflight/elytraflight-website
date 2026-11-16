#!/usr/bin/env python3
"""SG-057 group 4: local linear approximation, and a finite-horizon sequence.

New core ids. Domain skills stay, with the core added as a prerequisite.
Question ids that leave a bank are retired and are not reused.
Deep questions use Bank.sym, Bank.order, Bank.find_error, and Bank.multi.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from banklib import BANK, EXP, Bank, save_explainer, words
from templates import matrix_fig, plot, splane

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GRAPH = os.path.join(ROOT, "skilltree", "ee105_skills_draft.json")
BOXES = os.path.join(ROOT, "skilltree", "collections.json")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")
TEST_CONTENT = os.path.join(ROOT, "public", "skilltree", "tests", "test-content.js")


def load(sid, kind):
    folder = BANK if kind == "bank" else EXP
    path = os.path.join(folder, sid + ".json")
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    data = json.loads(raw)
    data["_path"] = path
    data["_raw"] = raw
    return data


def dump_json(path, data, indent):
    text = json.dumps(data, indent=indent, ensure_ascii=False)
    if not text.endswith("\n"):
        text += "\n"
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def dump(data):
    path = data.pop("_path")
    raw = data.pop("_raw", None)
    indent = 2
    if raw:
        second = raw.splitlines()[1] if len(raw.splitlines()) > 1 else ""
        if second.startswith(" ") and not second.startswith("  "):
            indent = 1
        if not raw.endswith("\n"):
            text = json.dumps(data, indent=indent, ensure_ascii=False)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            return
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
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


def bump(bank):
    bank["version"] = int(bank.get("version") or 1) + 1


def set_section(exp, heading, body):
    for section in exp["sections"]:
        if section.get("heading") == heading:
            section["body_md"] = body
            return
    raise SystemExit("missing section " + heading)


def save_exp(exp):
    path = exp.get("_path")
    raw = exp.get("_raw")
    if "version" in exp:
        exp["version"] = int(exp.get("version") or 1) + 1
    else:
        ordered = {"_path": path, "_raw": raw}
        for key, value in list(exp.items()):
            if str(key).startswith("_"):
                continue
            ordered[key] = value
            if key == "title":
                ordered["version"] = 2
        exp.clear()
        exp.update(ordered)
    dump(exp)


def require_words(sid, sections):
    n = words(sections)
    print(f"  explainer {sid} words {n}")
    if not 250 <= n <= 500:
        raise SystemExit(f"{sid} explainer words {n}")
    return n


def curve():
    return plot(lambda t: 0.15 * t * t * t + 0.4, 0, 2.4, "x", "y", "A smooth curve")


def row():
    return matrix_fig([["u0", "u1", "u2"]], "Three inputs in a row")


def pair():
    return splane([(-2, 1), (-2, -1)], [], "A conjugate pair in the left half-plane")


def on_axis():
    return splane([(-4, 0), (0, 0)], [], "One mark on the axis")


def hess():
    return matrix_fig([["h", "0"], ["0", "h"]], "A square matrix of second derivatives")


def write_local_core():
    b = Bank("local-linear-approximation")
    fig = curve()
    alt = "A smooth curve that bends as its input grows."
    b.mc(
        1,
        r"The linear approximation of a smooth scalar function at a chosen point is",
        [
            r"the value at that point, plus the derivative there times the step away from it",
            r"the value at the new point, with the derivative ignored",
            r"the ratio of the function value to the coordinate, at every point",
            r"the second derivative alone, with no value and no slope",
        ],
        0,
        r"The approximation keeps the value and multiplies the derivative at the chosen point by the step. The value at the new point is what the approximation is trying to estimate, so it cannot be an ingredient. A ratio of value to coordinate is a different number from the slope. The second derivative is a later correction, not a replacement for the value and the slope.",
        fig=fig,
        alt=alt,
    )
    b.num(
        1,
        r"Let \(f(t) = t^3\). At \(t = 2\), with a step of \(0.1\), what value does the linear approximation give?",
        2.0 ** 3 + (3 * 2.0 ** 2) * 0.1,
        "",
        r"At \(t = 2\) the value is \(8\) and the derivative \(3t^2\) is \(12\). The approximation is \(8 + 12 \cdot 0.1 = 9.2\). Using the derivative at the new point \(2.1\), or reporting only the slope \(12\), answers a different question. The step is added only after it is multiplied by the slope.",
        fig=fig,
        alt=alt,
    )
    b.order(
        1,
        r"Put these steps in the order that builds a linear approximation at a chosen point.",
        [
            r"Name the chosen point and the step away from it.",
            r"Evaluate the function at the chosen point.",
            r"Evaluate the derivative at the chosen point.",
            r"Add the derivative times the step to the value.",
        ],
        r"The point comes first, because both the value and the derivative are read there. The value is the constant term. The derivative, still at that same point, multiplies the step. Adding those two pieces is the approximation. Evaluating the derivative at the far end, or adding the step without the derivative, breaks the formula.",
        fig=fig,
        alt=alt,
    )
    b.sym(
        2,
        r"The value at a chosen point \(a\) is \(p\), and the derivative there is \(m\). Write the linear approximation at a new point \(x\), in the names p, m, a, and x.",
        "p+m*(x-a)",
        {"p": (1, 6), "m": (-3, 3), "a": (0.5, 2), "x": (0.2, 4)},
        r"The approximation is the value \(p\) plus the slope \(m\) times the step \(x - a\). Leaving out \(p\) reports only the change. Using \(x\) in place of the step treats the new coordinate as if the chosen point were zero. Swapping \(p\) and \(m\) mixes a value with a slope.",
        alternates=["m*(x-a)+p", "p+(x-a)*m"],
        fig=fig,
        alt=alt,
    )
    b.num(
        2,
        r"Let \(f(x) = 1/x\). At \(x = 4\), a step of \(+0.5\) is proposed. What change does the linear approximation predict?",
        -(1.0 / 16.0) * 0.5,
        "",
        r"The derivative of \(1/x\) is \(-1/x^2\), so at \(x = 4\) the slope is \(-1/16\). The predicted change is that slope times \(0.5\), which is \(-0.03125\). The new value of the function is a different question. The slope at \(4.5\), or the ratio \(1/4\), is not the change predicted from the chosen point.",
        fig=fig,
        alt=alt,
    )
    b.multi(
        2,
        r"Which statements describe the linear approximation at a chosen point?",
        [
            r"It uses the derivative at the chosen point.",
            r"As the step shrinks to zero, the error shrinks faster than the step.",
            r"The same formula is exact for every step, however large.",
            r"It replaces the derivative by the ratio of the value to the coordinate.",
        ],
        [0, 1],
        r"The derivative is read at the chosen point, and for a smooth function the error is higher order, so it shrinks faster than the step. A large step can leave the region where that slope is representative, so the formula is not exact for every step. The ratio of value to coordinate is not the derivative.",
        fig=fig,
        alt=alt,
    )
    b.find_error(
        3,
        r"A note builds the linear approximation. Exactly one step is wrong.",
        [
            r"Name the chosen point \(a\) and the step \(h = x - a\).",
            r"Evaluate the function at \(a\).",
            r"Evaluate the derivative at the new point \(x\), and multiply that slope by \(h\).",
            r"Add that product to the value at \(a\).",
        ],
        2,
        r"The derivative belongs at the chosen point. A slope taken at the new point is a different expansion. The value at \(a\) is the constant term, and it is added to the product of that slope with the step. Dropping the value, or adding the step instead of multiplying, would be a different mistake.",
        reasons=[
            "The derivative belongs at the chosen point, not at the new point.",
            "The function value at the chosen point should be left out.",
            "The step should be added to the slope instead of multiplied.",
        ],
        correct_reason=0,
        fig=fig,
        alt=alt,
    )
    b.num(
        3,
        r"Let \(f(x) = x^2 + 3x\). What is the derivative at \(x = 1\), the slope the linear approximation uses there?",
        2.0 * 1.0 + 3.0,
        "",
        r"The derivative is \(2x + 3\). At \(x = 1\) that is \(5\). The function value \(4\) is the constant term of the approximation, not the slope. The derivative at a different point, or the ratio \(f(1)/1 = 4\), does not multiply the step.",
        fig=fig,
        alt=alt,
    )
    b.mc(
        3,
        r"Why is this approximation called local?",
        [
            r"The derivative has to be an integer.",
            r"A large step can leave the region where the slope at the chosen point still represents the function.",
            r"The formula uses no derivative at all.",
            r"The value at the chosen point is optional.",
        ],
        1,
        r"The slope is guaranteed to track the function only in a neighborhood of the chosen point. Far away, the higher-order error is no longer small. The derivative need not be an integer, the formula does use the derivative, and the value at the chosen point is the constant term.",
        fig=fig,
        alt=alt,
    )
    b.num(
        4,
        r"A stored quantity follows \(y = 4x^2\). What is the slope of its linear approximation at \(x = 1.5\)?",
        8.0 * 1.5,
        "",
        r"The derivative of \(4x^2\) is \(8x\). At \(x = 1.5\) the slope is \(12\). The value \(4 \cdot (1.5)^2 = 9\) is the constant term, not the slope. A later skill calls this slope a small-signal capacitance when the quantity is charge and the coordinate is voltage.",
        fig=fig,
        alt=alt,
        preview=["nl-cap"],
    )
    b.mc(
        4,
        r"The same replacement, applied to a rate that depends on a state and an input, is stored as two partial derivatives. Those partial derivatives are evaluated",
        [
            r"at a convenient point that is not the resting condition",
            r"only with respect to time, after the rate has been integrated",
            r"at the resting condition, once in the state and once in the input",
            r"after the rate is replaced by its second derivative",
        ],
        2,
        r"A later skill names the state partial \(A\) and the input partial \(B\), both evaluated where the rate is zero. A point that is not resting is a different expansion. Time is not one of those two variables. The second derivative is a later correction, not these two first partials.",
        fig=matrix_fig([["A", "B"]], "Two partial-derivative blocks"),
        alt="Two blocks side by side, one for each partial derivative.",
        preview=["linearization"],
    )
    b.multi(
        4,
        r"Which statements about the error of the linear approximation are true?",
        [
            r"It matches the value and the first derivative at the chosen point.",
            r"For a smooth function, the error is of higher order than the step.",
            r"The second derivative has to be matched before this first-order formula can be written.",
            r"The error is zero for every cubic, at every step.",
        ],
        [0, 1],
        r"Matching the value and the first derivative is the whole first-order formula, and the error is then higher order in the step. The second derivative is an extra term a later skill adds. It is not required before the linear formula exists. A cubic still has a nonzero error at a finite step.",
        fig=fig,
        alt=alt,
        preview=["taylor-approximation-multivariable"],
    )
    b.save()


def write_horizon_core():
    b = Bank("finite-horizon-sequence")
    fig = row()
    alt = "A short row of decision values."
    b.mc(
        1,
        r"In a finite-horizon sequence problem, the decision is",
        [
            r"a single gain, used for every future time",
            r"only the first input, with the rest of the list discarded",
            r"a finite list of inputs or states, one entry for each step of the horizon",
            r"an infinite curve, with no grid and no last step",
        ],
        2,
        r"The decision is the whole finite list. A single gain is a different object, used when the horizon is infinite and unconstrained. Keeping only the first input, and rebuilding later, is a later controller. An infinite curve is not a finite sequence.",
        fig=fig,
        alt=alt,
    )
    b.num(
        1,
        r"Three steps have stage costs \(2\), \(5\), and \(1\). What is the cost of the sequence?",
        2.0 + 5.0 + 1.0,
        "",
        r"The cost adds one term per step: \(2 + 5 + 1 = 8\). The product \(2 \cdot 5 \cdot 1 = 10\) is not the cost. The largest stage, \(5\), leaves out the other two. A sum is the cost even when one stage is larger than the others.",
        fig=matrix_fig([["2", "5", "1"]], "Three stage costs"),
        alt="Three stage costs written in a row.",
    )
    b.order(
        1,
        r"Put these steps in the order that writes a finite-horizon sequence problem.",
        [
            r"Choose the number of steps in the horizon.",
            r"Name the sequence of inputs or states as the decision.",
            r"Add a stage cost at each step to make the objective.",
            r"Write the dynamics as a constraint at each step.",
        ],
        r"The horizon length comes first, because it fixes how long the list is. The list is the decision. The objective adds a term on that list. The dynamics then restrict which lists are feasible. Treating the dynamics as the cost, or choosing the list before the horizon length is known, writes a different problem.",
        fig=fig,
        alt=alt,
    )
    b.sym(
        2,
        r"A horizon of \(n\) steps has stage cost \(c\) at every step and a terminal cost \(p\). Write the total cost in the names n, c, and p.",
        "n*c+p",
        {"n": (2, 8), "c": (0.4, 3), "p": (0.2, 4)},
        r"Each of the \(n\) steps contributes \(c\), and the terminal cost \(p\) is added once, so the total is \(nc + p\). Multiplying \(p\) by \(n\) charges the terminal cost on every step. Leaving out \(p\) drops the terminal term. A product \(ncp\) is not a sum.",
        alternates=["c*n+p", "p+n*c", "p+c*n"],
        fig=fig,
        alt=alt,
    )
    b.num(
        2,
        r"The update is \(x_{k+1} = x_k + u_k\), with \(x_0 = 3\) and inputs \(1\), \(-2\), \(4\). What is \(x_3\)?",
        3.0 + 1.0 - 2.0 + 4.0,
        "",
        r"The state adds each input in turn: \(3 + 1 = 4\), then \(4 + (-2) = 2\), then \(2 + 4 = 6\). Stopping after the first input reports \(4\). Adding the absolute values, \(3 + 1 + 2 + 4 = 10\), flips the sign of the middle input. The dynamics are a constraint the sequence has to meet, not a cost.",
        fig=fig,
        alt=alt,
    )
    b.multi(
        2,
        r"Which pieces belong in a finite-horizon sequence problem?",
        [
            r"The decision is a sequence of inputs or states.",
            r"The cost adds a term along that sequence.",
            r"The dynamics constrain which sequences are feasible.",
            r"Only the first input is kept, and the problem is rebuilt at the next sample.",
        ],
        [0, 1, 2],
        r"The decision is the sequence, the cost is a sum along it, and the dynamics are constraints. Rebuilding at the next sample, and keeping only the first input, is a later controller. It is not part of writing the one sequence.",
        fig=fig,
        alt=alt,
    )
    b.find_error(
        3,
        r"A note writes a finite-horizon problem. Exactly one step is wrong.",
        [
            r"The decision is the list of inputs over the finite horizon.",
            r"The cost adds one stage term for each step.",
            r"The dynamics replace that sum and become the objective.",
            r"A sequence that breaks the update is not feasible.",
        ],
        2,
        r"The dynamics are constraints. They do not replace the sum. The list of inputs is the decision, the sum of stage terms is the cost, and a sequence that breaks the update is rejected. Calling the dynamics the objective drops the cost.",
        reasons=[
            "The dynamics are constraints, and the sum stays the cost.",
            "The decision should be a single gain instead of a list.",
            "A sequence that breaks the update is still feasible.",
        ],
        correct_reason=0,
        fig=fig,
        alt=alt,
    )
    b.num(
        3,
        r"The inputs on three steps are \(3\), \(1\), and \(1\). What is the energy, the sum of the squared inputs?",
        3.0 ** 2 + 1.0 ** 2 + 1.0 ** 2,
        "",
        r"Square each input and add: \(9 + 1 + 1 = 11\). The sum of the inputs themselves is \(5\), which drops the squares. The product of the squares is \(9\), which is not a sum. Energy here is one kind of stage cost, still a sum along the sequence.",
        fig=matrix_fig([["3", "1", "1"]], "Three inputs"),
        alt="Three inputs written in a row.",
    )
    b.mc(
        3,
        r"A dynamics constraint on a finite sequence means",
        [
            r"a candidate list is feasible only when each next state matches the update",
            r"the cost of every feasible list is zero",
            r"the horizon has to be infinite",
            r"the stage costs are multiplied instead of added",
        ],
        0,
        r"The update ties each state to the previous state and the input. A list that breaks that tie is not feasible. The cost of a feasible list can still be positive. The horizon stays finite. The stage costs are still added.",
        fig=fig,
        alt=alt,
    )
    b.num(
        4,
        r"Samples of one coordinate sit at \(0\), \(2\), and \(5\). What is the smoothness cost, the sum of the squared steps between consecutive samples?",
        (2.0 - 0.0) ** 2 + (5.0 - 2.0) ** 2,
        "",
        r"The steps are \(2 - 0 = 2\) and \(5 - 2 = 3\). The squared lengths are \(4\) and \(9\), and the sum is \(13\). Adding the positions, \(0 + 2 + 5 = 7\), is not a sum of steps. A later skill keeps this sum and adds an obstacle that can make the feasible set nonconvex.",
        fig=matrix_fig([["0", "2", "5"]], "Three samples on a line"),
        alt="Three sample positions written in a row.",
        preview=["trajectory-optimization"],
    )
    b.mc(
        4,
        r"A later controller solves a short sequence from the current state and applies only the first input. Compared with the problem in this skill, that controller",
        [
            r"drops the sum, because a sequence cannot have a cost",
            r"rebuilds the sequence at the next sample instead of keeping one open-loop list",
            r"removes the dynamics, because a constraint cannot be written on a sequence",
            r"replaces the sequence by one gain computed for an infinite horizon",
        ],
        1,
        r"This skill decides the whole list once. The later controller throws the tail away and writes the problem again at the next sample. The sum and the dynamics stay available in both problems. An infinite-horizon gain is a different object again.",
        fig=fig,
        alt=alt,
        preview=["mpc"],
    )
    b.num(
        4,
        r"A horizon has \(7\) steps, and each step has one input. How many inputs are in the decision?",
        7.0,
        "",
        r"One input per step gives a list of length \(7\). A count of \(6\) drops the last step. A count of \(8\) adds an input past the horizon. A later controller may apply only the first of these seven and rebuild; this question asks how long the list is.",
        fig=fig,
        alt=alt,
        preview=["mpc"],
    )
    b.save()


def write_core_explainers():
    curve_fig = curve()
    save_explainer(
        "local-linear-approximation",
        "Linear approximation at an operating point",
        [
            {
                "heading": "The idea",
                "figure": curve_fig,
                "figure_alt": "A smooth curve, with room for a tangent at one point.",
                "body_md": r"A smooth function is hard to carry through a design and easy to replace near one point. Pick that point first. Read the function there, and read the derivative there. The linear approximation is the value plus the derivative times the step away from the point. Nothing in the formula looks at the function at the far end of the step.",
            },
            {
                "heading": "Key equations",
                "body_md": r"For a scalar function, \[ f(a) + f'(a)\,(x - a). \] The step is \(x - a\). The derivative is \(f'(a)\), not \(f'(x)\). If \(f\) is smooth, the error satisfies \[ f(x) - \big(f(a) + f'(a)\,(x - a)\big) = o(|x - a|) \] as the step shrinks. The error goes to zero faster than the step, which is why a small step is trustworthy and a large step is not. The same sentence in several variables uses the gradient in place of \(f'(a)\), still evaluated at the chosen point.",
            },
            {
                "heading": "Worked example",
                "body_md": r"Take \(g(z) = z^2\) at \(z = 7\), and take a step of \(0.3\). The value is \(49\). The derivative \(2z\) equals \(14\) at this point, so the predicted change is \(14 \cdot 0.3 = 4.2\) and the approximation is \(53.2\). The true value at \(7.3\) is \(53.29\). The miss is \(0.09\), much smaller than the step \(0.3\). The slope at \(7.3\) would be a different expansion. The ratio \(49/7 = 7\) is the value divided by the coordinate, not the slope that multiplies the step.",
            },
            {
                "heading": "Common pitfalls",
                "body_md": r"- Evaluating the derivative at the new point. The slope in the formula is the slope at the chosen point. - Reporting the slope and forgetting to add the value. The approximation is a value plus a change. - Using the ratio of the value to the coordinate as if it were the derivative. Those agree only for a line through the origin. - Treating a large step as if the higher-order error were still negligible. The formula does not become exact just because it was written down.",
            },
            {
                "heading": "Where this leads",
                "body_md": r"When the function is stored charge versus voltage, the slope is a small-signal capacitance. When the function is a rate that depends on a state and an input, the same replacement at a resting condition becomes two partial derivatives. When a second derivative is available, a later expansion adds that term on top of this linear model. Each of those skills starts from the value and the first derivative already built here.",
            },
        ],
    )
    save_explainer(
        "finite-horizon-sequence",
        "Finite-horizon decision sequence",
        [
            {
                "heading": "The idea",
                "figure": matrix_fig([["9", "12", "15"]], "Three stage costs"),
                "figure_alt": "Three stage costs written in a row.",
                "body_md": r"Some decisions are not a single number. They are a list: an input on each step of a finite horizon, or a state at each sample. The cost adds one term for each step of that list. The dynamics do not sit in the cost. They say which lists are allowed. A list that breaks the update is simply not a candidate.",
            },
            {
                "heading": "Key equations",
                "body_md": r"One shape is \[ \begin{aligned} & \text{minimize} && \sum_{k=0}^{N-1} \ell_k + p \\ & \text{subject to} && x_{k+1} = f(x_k, u_k). \end{aligned} \] The decision is the list \(u_0,\ldots,u_{N-1}\), or the list of states, or both. \(N\) is how many steps the list has. \(\ell_k\) is the stage cost. \(p\) is a terminal cost, added once. The update is a constraint at every step, not a second objective.",
            },
            {
                "heading": "Worked example",
                "body_md": r"Take stage costs \(9\), \(12\), and \(15\). The sum is \(36\). A terminal cost is not present, so nothing is added after the sum. The product \(9 \cdot 12 \cdot 15\) is not the cost. Now start at state \(20\), with the update \(x_+ = x + u\) and inputs \(9\) then \(12\). The states are \(20\), then \(29\), then \(41\). Any other list of states with those inputs breaks the update and is not feasible. The sum \(36\) is still the cost of the feasible list. Feasibility did not set the cost to zero.",
            },
            {
                "heading": "Common pitfalls",
                "body_md": r"- Calling the decision a single gain. A gain is what remains when the horizon is infinite and the constraints are gone. - Multiplying the stage costs, or keeping only the largest one. The cost is a sum. - Moving the dynamics into the objective and dropping the sum. The dynamics restrict the list. They do not replace the cost. - Keeping only the first input and throwing the rest away. That is a later controller, not the definition of the sequence.",
            },
            {
                "heading": "Where this leads",
                "body_md": r"One later skill transcribes the list on a fixed grid and stops. An obstacle on that grid can make the feasible set nonconvex, even when the cost is a sum of squares. Another later skill solves a short list from the measured state, applies only the first input, and writes the problem again at the next sample. Both start from a sequence, a sum, and dynamics as constraints. They differ in whether the list is kept.",
            },
        ],
    )
    for sid in ("local-linear-approximation", "finite-horizon-sequence"):
        exp = load(sid, "explainer")
        require_words(sid, exp["sections"])


def patch_linearization():
    bank = load("linearization", "bank")
    for qid in ("linearization-r1-q1", "linearization-r2-q2", "linearization-r3-q1"):
        retire(bank, qid)
    bank["questions"] += [
        built(
            "linearization", 1, "linearization-r1-q4", "order",
            r"Put these steps in the order that builds the local matrices at an equilibrium.",
            [
                r"Confirm the chosen state and input make the rate zero.",
                r"Differentiate the rate with respect to the state.",
                r"Differentiate the rate with respect to the input.",
                r"Evaluate both derivatives at that equilibrium.",
            ],
            r"The resting condition comes first. A derivative at a point that is not an equilibrium is a different expansion. The state derivative is the matrix \(A\) and the input derivative is the matrix \(B\). Both are numbers only after they are evaluated at the resting pair. Swapping the two derivatives assigns the input slope to the state matrix.",
            fig=matrix_fig([["A", "B"]], "State and input partials"),
            alt="Two blocks, one for the state partial and one for the input partial.",
        ),
        built(
            "linearization", 2, "linearization-r2-q4", "multi",
            r"Which eigenvalue patterns say the linear model at the equilibrium is locally asymptotically stable?",
            [
                r"Every eigenvalue has a negative real part.",
                r"One eigenvalue is positive and the others are negative.",
                r"An eigenvalue has real part zero.",
                r"A repeated eigenvalue is fine when every real part is still negative.",
            ],
            [0, 3],
            r"Local asymptotic stability of the linear model follows from every real part being negative, whether or not an eigenvalue is repeated. One positive real part makes the equilibrium unstable. A zero real part makes this test inconclusive. The test reads the eigenvalues of the Jacobian. It does not ask the nonlinear system to have only one equilibrium.",
            fig=pair(),
            alt="A complex conjugate pair in the left half-plane.",
        ),
        built(
            "linearization", 3, "linearization-r3-q4", "find_error",
            r"A note claims local asymptotic stability from the Jacobian. Exactly one step is false.",
            [
                r"The chosen pair is an equilibrium, so the rate is zero there.",
                r"The Jacobian eigenvalues are \(-4\) and \(0\).",
                r"A zero eigenvalue still lets the linearization test conclude local asymptotic stability.",
                r"A positive real part would have made the equilibrium unstable.",
            ],
            2,
            r"A zero real part makes the linearization test inconclusive. It does not prove local asymptotic stability. The equilibrium check is the right first step, and a positive real part would indeed mean the linear model is unstable. The eigenvalues can be read from the Jacobian only after that Jacobian is evaluated at the equilibrium.",
            reasons=[
                "A zero real part makes the linearization test inconclusive.",
                "A zero eigenvalue proves stability on its own.",
                "The equilibrium check is the false step.",
            ],
            correct_reason=0,
            fig=on_axis(),
            alt="Two marks, one in the left half-plane and one on the vertical axis.",
        ),
    ]
    bump(bank)
    dump(bank)


def patch_taylor():
    bank = load("taylor-approximation-multivariable", "bank")
    retire(bank, "taylor-approximation-multivariable-r1-q1")
    for q in bank["questions"]:
        if q.get("id") == "taylor-approximation-multivariable-r4-q1":
            q["prompt"] = r"Which statements hold for the second-order model?"
            q["options"] = [
                r"It adds \(\tfrac12 h^{T} H_f(x)\, h\) to the linear model, with the Hessian at the expansion point.",
                r"When the second derivatives are continuous, its error is \(o(\lVert h \rVert^2)\).",
                r"Dropping the one half leaves the quadratic term unchanged.",
                r"The Hessian in that term is evaluated at the new point.",
            ]
            q["correct_indices"] = [0, 1]
            q["explanation"] = (
                r"The second-order model is the linear model plus one half of \(h^{T} H h\), and the Hessian is read at the expansion point. "
                r"With continuous second derivatives the error is higher order than \(\lVert h \rVert^2\). "
                r"Dropping the one half doubles the quadratic term. Evaluating the Hessian at the new point is a different formula."
            )
            q["version"] = int(q.get("version") or 1) + 1
    bank["questions"] += [
        built(
            "taylor-approximation-multivariable", 1, "taylor-approximation-multivariable-r1-q4", "mc",
            r"The second-order model differs from the linear model by",
            [
                r"a second copy of the linear term",
                r"one half of \(h^{T} H h\), with the Hessian at the expansion point",
                r"the Hessian at the new point, with no factor of one half",
                r"the value of the function at the new point, in place of a quadratic term",
            ],
            1,
            r"The quadratic term is one half of \(h^{T} H h\), and \(H\) is the Hessian at the point where the linear model was built. A second copy of the linear term does not bring in second derivatives. Dropping the one half, or moving the Hessian to the new point, changes the formula. The value at the new point is what the model is estimating.",
            fig=hess(),
            alt="A square matrix standing in for second derivatives.",
        ),
    ]
    bump(bank)
    dump(bank)


def patch_trajectory():
    bank = load("trajectory-optimization", "bank")
    retire(bank, "trajectory-optimization-r1-q1")
    bank["questions"] += [
        built(
            "trajectory-optimization", 1, "trajectory-optimization-r1-q4", "mc",
            r"This transcription solves the grid once. What does the solver return?",
            [
                r"Only the first input, with the rest discarded at once",
                r"A gain recomputed from a new measurement",
                r"The whole input list for the grid, kept as one open-loop plan",
                r"An infinite-horizon equation with no samples",
            ],
            2,
            r"One transcription returns the whole list and stops. Discarding the tail is the receding-horizon habit, not this grid. A gain recomputed from a new measurement is a different architecture. An infinite horizon has no finite list of samples to return.",
            fig=row(),
            alt="A row of decision values on a grid.",
        ),
    ]
    bump(bank)
    dump(bank)


def patch_mpc_previews():
    bank = load("mpc", "bank")
    notes = {
        "mpc-r4-q1": (
            r" The question only clips the command for the model in hand. "
            r"A later design changes that model when a measurement shows a new condition."
        ),
        "mpc-r4-q2": (
            r" When a measurement says the model itself is out of date, a later design updates the model. "
            r"It does not stretch this horizon into an infinite unconstrained problem."
        ),
    }
    for q in bank["questions"]:
        extra = notes.get(q.get("id"))
        if not extra:
            continue
        if "adaptive" in (q.get("preview") or []):
            continue
        q["preview"] = ["adaptive"]
        q["explanation"] = q["explanation"].rstrip() + extra
        q["version"] = int(q.get("version") or 1) + 1
    bump(bank)
    dump(bank)


def patch_device_explainers():
    prefixes = {
        "nl-cap": (
            "In a non-linear capacitor the charge is not simply proportional to voltage, so a single number \\(Q/V\\) is not enough. ",
            "The linear approximation at an operating point keeps the value and the slope there. On a charge-voltage curve the ratio \\(Q/V\\) is not that slope. ",
        ),
        "diode-ss": (
            "For small signals around a DC operating point, the exponential diode looks like a straight line: ",
            "The linear approximation at a bias replaces the exponential diode law by its value and its slope. That slope is ",
        ),
        "ss-model": (
            "Transistor circuits are non-linear, but for small signals around a fixed bias point they behave linearly. ",
            "The linear approximation at a bias supplies the slopes of the device laws. ",
        ),
        "bjt-ss": (
            "The BJT's small-signal model, the **hybrid-pi**, comes from linearizing the forward-active equations around a bias point. ",
            "The hybrid-pi model is the linear approximation of the forward-active equations at a bias point. ",
        ),
    }
    for sid, (old, new) in prefixes.items():
        exp = load(sid, "explainer")
        idea = exp["sections"][0]
        if not idea["body_md"].startswith(old):
            if idea["body_md"].startswith(new):
                continue
            raise SystemExit("idea prefix drifted for " + sid)
        idea["body_md"] = new + idea["body_md"][len(old):]
        save_exp(exp)
        require_words(sid, exp["sections"])


def patch_application_explainers():
    lin = load("linearization", "explainer")
    set_section(
        lin,
        "The idea",
        r"The value-plus-derivative replacement is already the linear approximation at a chosen point. Here the function is a rate \(\dot x = f(x, u)\), and the chosen point has to be an equilibrium: \(f(x_e, u_e) = 0\), so the state stays put when nothing disturbs it. The derivative in the state is a matrix \(A\). The derivative in the input is a matrix \(B\). Both are evaluated at \((x_e, u_e)\). The eigenvalues of \(A\) then say whether that local model is asymptotically stable. A real part that is zero makes the test inconclusive. A positive real part means the local model is unstable.",
    )
    if "figure" not in lin["sections"][0]:
        lin["sections"][0]["figure"] = matrix_fig([["A", "B"]], "State and input Jacobians")
        lin["sections"][0]["figure_alt"] = "Two blocks for the state Jacobian and the input Jacobian."
    set_section(
        lin,
        "Where this leads",
        r"Feedback linearization cancels the nonlinear terms with the input, instead of stopping at these partial derivatives. Gain scheduling keeps a family of these Jacobians and switches the controller as the operating condition moves. Both are later than the local matrices computed here.",
    )
    text = " ".join(s["body_md"] for s in lin["sections"])
    if "A = -8" not in text:
        raise SystemExit("linearization explainer lost the worked example")
    save_exp(lin)
    require_words("linearization", lin["sections"])

    tay = load("taylor-approximation-multivariable", "explainer")
    idea = tay["sections"][0]["body_md"]
    old = "A Taylor model replaces a function near a chosen point by a polynomial that matches its derivatives there. The first-order model matches the value and the gradient. "
    new = "The linear approximation at a chosen point matches the value and the gradient. This skill adds the Hessian on top of that approximation. "
    if idea.startswith(old):
        tay["sections"][0]["body_md"] = new + idea[len(old):]
    elif not idea.startswith(new):
        raise SystemExit("taylor idea prefix drifted")
    if "cubic slice at x = 2" not in " ".join(s["body_md"] for s in tay["sections"]):
        raise SystemExit("taylor explainer lost the worked example")
    save_exp(tay)
    require_words("taylor-approximation-multivariable", tay["sections"])

    traj = load("trajectory-optimization", "explainer")
    set_section(
        traj,
        "The idea",
        r"A finite-horizon sequence is already a decision, a sum, and a set of dynamics constraints. This skill transcribes that sequence once, on a fixed grid, and then stops. The samples, and the inputs on the intervals if they stay free, are chosen together. The solver returns the whole list. It does not throw the tail away, and it does not rebuild the list when a new measurement arrives.",
    )
    joined = " ".join(s["body_md"] for s in traj["sections"])
    if "The anchor smoothness is 113" not in joined or "The anchor landing is 15" not in joined:
        raise SystemExit("trajectory explainer lost an anchor")
    if "(4,\\ 2)" in joined or "u_0 = 0" in joined:
        raise SystemExit("trajectory explainer repeats a quiz sample")
    save_exp(traj)
    require_words("trajectory-optimization", traj["sections"])

    mpc = load("mpc", "explainer")
    idea = mpc["sections"][0]["body_md"]
    lead = "The finite-horizon sequence, its sum, and its dynamics are the problem being solved. "
    if not idea.startswith(lead):
        mpc["sections"][0]["body_md"] = lead + idea
    set_section(
        mpc,
        "Where this leads",
        r"When a measurement shows that the model no longer matches the operating condition, a later design keeps a family of controllers indexed by that measurement. That family is not a longer copy of one horizon. Applying the whole computed sequence with no new measurement would drop the habit that makes this controller closed loop.",
    )
    if "5.61" not in " ".join(s["body_md"] for s in mpc["sections"]):
        raise SystemExit("mpc explainer lost the worked example")
    save_exp(mpc)
    require_words("mpc", mpc["sections"])


def patch_graph():
    with open(GRAPH, encoding="utf-8") as f:
        graph = json.load(f)
    skills = graph["skills"]
    by_id = {s["id"]: s for s in skills}

    def insert(skill, before):
        if skill["id"] in by_id:
            return
        skills.insert(next(i for i, s in enumerate(skills) if s["id"] == before), skill)
        by_id[skill["id"]] = skill

    insert(
        {
            "id": "local-linear-approximation",
            "name": "Linear approximation at an operating point",
            "summary": "Replace a smooth map by its value plus its derivative at a chosen point. The remainder shrinks faster than the step, and the replacement is trustworthy only nearby.",
            "prereqs": [],
            "sources": [
                {"ref": "fbs-v315", "section": "5.4", "use": "reference only"},
                {"ref": "boyd-cvx", "use": "reference only"},
                {"ref": "nw-numopt", "use": "reference only"},
            ],
        },
        "linearization",
    )
    insert(
        {
            "id": "finite-horizon-sequence",
            "name": "Finite-horizon decision sequence",
            "summary": "The decision is a sequence of inputs or states, the cost adds a term at each step, and the dynamics restrict which sequences are feasible.",
            "prereqs": [],
            "sources": [
                {"ref": "boyd-cvx", "use": "reference only"},
                {"ref": "nlo-notes", "use": "scope only"},
                {"ref": "fbs-v315", "use": "reference only"},
                {"ref": "me132-f26", "use": "scope only"},
            ],
        },
        "mpc",
    )

    def set_fields(sid, prereqs, summary=None):
        skill = by_id[sid]
        skill["prereqs"] = prereqs
        if summary is not None:
            skill["summary"] = summary

    set_fields("nl-cap", ["local-linear-approximation", "mim-cap"])
    set_fields("diode-ss", ["local-linear-approximation", "diode-iv", "junction-cap", "nl-cap"])
    set_fields("ss-model", ["local-linear-approximation", "gm", "ro"])
    set_fields("bjt-ss", ["local-linear-approximation", "early", "ss-model"])
    set_fields(
        "linearization",
        ["local-linear-approximation", "equilibria", "eig-modes"],
        "Form the Jacobians A and B at an equilibrium and read local stability from those eigenvalues.",
    )
    set_fields(
        "taylor-approximation-multivariable",
        ["local-linear-approximation", "hessian-matrix"],
        "Add the Hessian term on top of a linear approximation and read the second-order remainder.",
    )
    set_fields(
        "trajectory-optimization",
        ["finite-horizon-sequence", "optimization-problem-formulation", "optimization-problem-classes"],
        "Optional motivation, not required for later skills. One open-loop grid scores a sequence once, and an obstacle can make the feasible set nonconvex.",
    )
    set_fields(
        "mpc",
        ["finite-horizon-sequence", "state-feedback", "discrete-time"],
        "At each sample, solve a short look-ahead and apply only the first input.",
    )
    dump_json(GRAPH, graph, 1)

    with open(BOXES, encoding="utf-8") as f:
        collections = json.load(f)

    def insert_box(box_id, sid, before):
        for box in collections["boxes"]:
            if box["id"] != box_id:
                continue
            skills_in = box["skills"]
            if sid in skills_in:
                return
            skills_in.insert(skills_in.index(before), sid)
            return
        raise SystemExit("missing box " + box_id)

    insert_box("ee105-ch4", "local-linear-approximation", "nl-cap")
    insert_box("me132/m8", "local-linear-approximation", "linearization")
    insert_box("am08/ch5", "local-linear-approximation", "linearization")
    insert_box("nlo-tugraz/l3", "local-linear-approximation", "taylor-approximation-multivariable")
    insert_box("nlo-tugraz/l1", "finite-horizon-sequence", "trajectory-optimization")
    insert_box("me132/m9", "finite-horizon-sequence", "mpc")
    insert_box("am08/ch99", "finite-horizon-sequence", "mpc")
    dump_json(BOXES, collections, 2)

    with open(GRAND, encoding="utf-8") as f:
        grand = json.load(f)
    grand["skills"] = [sid for sid in grand["skills"] if sid != "linearization"]
    dump_json(GRAND, grand, 2)

    with open(TEST_CONTENT, encoding="utf-8") as f:
        text = f.read()
    if "274 live skills" not in text:
        count = text.count("272")
        if count != 8:
            raise SystemExit(f"expected 8 copies of 272, found {count}")
        text = text.replace("272", "274")
        for old, new in (
            ("skillsInBox(me132, byId).size, 61)", "skillsInBox(me132, byId).size, 63)"),
            ("skillsInBox(am08, byId).size, 75)", "skillsInBox(am08, byId).size, 77)"),
            ("skillsInBox(nlo, byId).size, 103)", "skillsInBox(nlo, byId).size, 105)"),
        ):
            if old not in text:
                raise SystemExit("missing box-size assertion: " + old)
            text = text.replace(old, new, 1)
        with open(TEST_CONTENT, "w", encoding="utf-8") as f:
            f.write(text)


def rounds(bank):
    counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for q in bank["questions"]:
        counts[q["round"]] += 1
    return counts


def report():
    deep_types = {"symbolic", "order", "error", "multi"}
    for sid in (
        "local-linear-approximation",
        "finite-horizon-sequence",
        "linearization",
        "taylor-approximation-multivariable",
        "trajectory-optimization",
        "mpc",
    ):
        bank = load(sid, "bank")
        deep = sum(1 for q in bank["questions"] if q.get("type") in deep_types)
        print(
            sid,
            "rounds",
            rounds(bank),
            "deep",
            deep,
            "retired",
            [q["id"] for q in bank.get("retired_questions") or []],
        )
        if deep < 3:
            raise SystemExit(sid + " is under the deep quota")
        if rounds(bank) != {1: 3, 2: 3, 3: 3, 4: 3}:
            raise SystemExit(sid + " round counts drifted")


def main():
    if os.path.exists(os.path.join(BANK, "local-linear-approximation.json")):
        print("cores already written")
        return
    write_local_core()
    write_horizon_core()
    write_core_explainers()
    patch_linearization()
    patch_taylor()
    patch_trajectory()
    patch_mpc_previews()
    patch_device_explainers()
    patch_application_explainers()
    patch_graph()
    report()


if __name__ == "__main__":
    main()
