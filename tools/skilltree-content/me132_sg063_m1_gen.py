#!/usr/bin/env python3
"""SG-063 feedback basics and block diagrams: swap pattern-matchable MC items.

Scope is the first ME 132 section, me132/m1, in collections order, intersected
with the grandfather list. That is six banks, which is the cap. fb-intro is in
the section and is not grandfathered. feedforward and app-examples are
grandfathered and are not in this section.

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
    "fb-concepts",
    "block-diagram",
    "onoff-pid-intro",
    "ode-model",
    "cruise-control",
    "model-method",
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


def swaps_for(sid):
    """(old mc id, replacement) in the order that assigns the next free ids."""
    if sid == "fb-concepts":
        return [
            ("fb-concepts-r1-q1", fresh(
                1, "order",
                r"Order the path that lets a controller act on the error. Each step after the first uses the result of the step before it.",
                [
                    r"Measure the output and subtract that measurement from the reference.",
                    r"Hand the controller that difference. It does not see the reference alone.",
                    r"The actuator turns the controller's command into a physical cause on the plant.",
                    r"The plant's new output is measured again, so a later disturbance can change the error.",
                ],
                r"The controller's input is the error, the reference minus the measurement. Acting on the reference alone is open loop, and nothing then opposes a disturbance. The actuator is what makes the command physical. The sensor is what reports the output. Adding the measurement instead of subtracting it flips the sign in the denominator, and a large loop gain then runs away.",
            )),
            ("fb-concepts-r2-q3", fresh(
                2, "sym",
                r"Write the steady output of a proportional loop as a multiple of a constant reference \(r\). The loop gain is \(L\). Use \(L\) and \(r\).",
                "L*r/(1+L)",
                {"L": (1, 40), "r": (0.5, 30)},
                r"The fixed point is \(y = L(r-y)\), so \(y(1+L) = L r\) and \(y = L r/(1+L)\). Reporting \(L r\) is the product with the feedback left open. Reporting \(r/(1+L)\) is the steady error, not the output. Reporting \(L/(1+L)\) drops the reference. A large \(L\) makes the fraction near 1, so the output sits close to the reference and not on it.",
                alternates=[
                    "r*L/(1+L)",
                    "r/(1/L+1)",
                    "(L/(1+L))*r",
                ],
            )),
            ("fb-concepts-r3-q1", fresh(
                3, "find_error",
                r"A worked solution says what a large loop gain does with sensor noise. Exactly one step is wrong.",
                [
                    r"The tracking factor is \(T = L/(1+L)\), and a large loop gain drives \(T\) toward 1.",
                    r"Sensor noise is added to the measurement, so the loop sees it on the same path as the reference.",
                    r"The noise is therefore multiplied by \(T\), the same factor as the reference.",
                    r"A large loop gain drives \(T\) toward 0, so the noise is rejected and the output stays quiet.",
                ],
                3,
                r"Sensor noise rides in with the measurement, so it is multiplied by \(T\), which is near 1 when \(L\) is large. An output disturbance is the signal multiplied by \(S = 1/(1+L)\). Swapping those two is the usual mistake. The loop still rejects a real disturbance. That rejection is why the noise gets a ride.",
                reasons=[
                    r"Large loop gain copies sensor noise onto the output. It rejects an output disturbance, not the measurement.",
                    r"Sensor noise is an output disturbance, so a large loop gain multiplies it by \(1/(1+L)\).",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "block-diagram":
        return [
            ("block-diagram-r1-q1", fresh(
                1, "order",
                r"Order the reduction of two blocks that sit one after the other. Each step after the first uses the result of the step before it.",
                [
                    r"The output of the first block is the only input of the second.",
                    r"Multiply the two gains. The second block never sees the original input by itself.",
                    r"Replace the pair by one block whose gain is that product.",
                    r"A later loop reduction uses that one block. It does not add the two gains back together.",
                ],
                r"Series blocks share a signal, so the gains multiply. Adding them is the parallel rule, for two blocks that see the same input and whose outputs sum. The product is not yet the closed-loop gain. Feedback, if there is any, is reduced after the series pair has become one block.",
            )),
            ("block-diagram-r1-q3", fresh(
                1, "sym",
                r"Write the closed-loop gain from reference to output for negative feedback. The forward block is \(G\), the return block is \(H\), and the return is subtracted. Use \(G\) and \(H\).",
                "G/(1+G*H)",
                {"G": (0.5, 20), "H": (0.05, 5)},
                r"The output is \(G\) times the error, and the error is the reference minus \(H\) times the output, so \(y = G(r - H y)\) and \(y/r = G/(1+GH)\). The product \(GH\) is the loop gain, not this gain. \(G/(1-GH)\) is the loop that adds the return. \(G+H\) adds a forward block to a return block that are not in parallel. The denominator is 1 only when the return path is open.",
                alternates=[
                    "G/(1+H*G)",
                    "1/(1/G+H)",
                    "(1+G*H)**(-1)*G",
                ],
            )),
            ("block-diagram-r2-q3", fresh(
                2, "find_error",
                r"A worked solution names the loop gain of a negative feedback loop and then the closed-loop gain. Exactly one step is wrong.",
                [
                    r"Walk once around the loop, through the forward block \(G\) and the return block \(H\).",
                    r"The loop gain is the product \(GH\).",
                    r"Negative feedback subtracts the returned signal from the reference.",
                    r"The closed-loop gain equals that same product \(GH\), because the reference is multiplied by every block in the loop.",
                ],
                3,
                r"Walking around the loop gives the loop gain \(GH\). The reference reaches the output through the forward block only, after the subtraction, so the closed-loop gain is \(G/(1+GH)\). Calling \(GH\) the closed-loop gain confuses the product around the loop with the gain from reference to output. Adding \(G\) and \(H\) is the parallel rule used on the wrong picture.",
                reasons=[
                    r"The closed-loop gain is \(G/(1+GH)\). \(GH\) is only the product around the loop.",
                    r"The closed-loop gain is \(G+H\), because the return block adds a second path from the reference.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "onoff-pid-intro":
        return [
            ("onoff-pid-intro-r1-q1", fresh(
                1, "order",
                r"Order what an on-off controller does with a nonzero error. Each step after the first uses the result of the step before it.",
                [
                    r"Read the sign of the error. The size of the error does not set an intermediate command.",
                    r"Command one of the two allowed values, full on or full off.",
                    r"The only way to reduce that command is to switch it to the other value.",
                    r"A plant that needs an intermediate command to hold the reference therefore chatters around it.",
                ],
                r"On-off feedback has no command between its two levels. Proportional control is the law that scales the command with the error. Holding full on while the output already sits past the reference drives the error the wrong way. The chatter is the controller hunting for a command it is not allowed to hold.",
            )),
            ("onoff-pid-intro-r2-q2", fresh(
                2, "find_error",
                r"A worked solution adds integral action to a stable loop with a constant reference and a constant disturbance. Exactly one step is wrong.",
                [
                    r"Proportional control alone can rest with a nonzero constant error.",
                    r"Integral action adds that error up as time passes.",
                    r"A nonzero constant error keeps the sum moving, so the command is still changing.",
                    r"The error can rest at that nonzero value, because a constant integrator output needs a constant error to hold it.",
                ],
                3,
                r"A leftover constant error keeps the integral moving, so the command cannot sit still. The only steady point of a stable loop is zero error. Derivative action is the term that is zero on a constant, and it does not move that resting point. An unstable loop is not a way to claim zero error. The integrator has to sit inside a loop that still settles.",
                reasons=[
                    r"A nonzero constant error never lets the integrator rest, so a stable loop cannot settle until the error is zero.",
                    r"Integral action zeros the error only after the loop has been made unstable.",
                ],
                correct_reason=0,
            )),
            ("onoff-pid-intro-r3-q2", fresh(
                3, "sym",
                r"Write the steady error of a proportional loop. The loop gain is the proportional gain \(K_c\) times the plant DC gain \(P\), and the reference \(r\) is constant. Derivative action adds nothing to this value. Use \(r\), \(K_c\), and \(P\).",
                "r/(1+Kc*P)",
                {"r": (1, 40), "Kc": (0.4, 15), "P": (0.4, 12)},
                r"The steady output is \(L r/(1+L)\) with \(L = K_c P\), so the error is \(r - y = r/(1+L)\). The derivative of a constant error is zero, which is why adding derivative action leaves this value unchanged. Reporting \(r\) is the miss of a plant that produces nothing. Reporting \(K_c P r\) is a command, not the error. Reporting \(r/(K_c P)\) drops the 1 in the denominator. Raising \(K_c\) shrinks the error and does not remove it.",
                alternates=[
                    "r/(1+P*Kc)",
                    "r*(1+Kc*P)**(-1)",
                    "r/(Kc*P+1)",
                ],
            )),
        ]
    if sid == "ode-model":
        return [
            ("ode-model-r1-q1", fresh(
                1, "sym",
                r"Write the current through a capacitor. The capacitance is \(C\) and the voltage across it changes at the rate \(vdot\). Use \(C\) and \(vdot\).",
                "C*vdot",
                {"C": (1e-7, 5e-3), "vdot": (0.1, 50)},
                r"The element law is \(i = C\) times the voltage rate. The rate is the derivative of the capacitor voltage, not a second state. Reporting \(C/vdot\) inverts the law. Reporting \(vdot/C\) has the shape of a reciprocal time constant, not a current. A resistor's law is algebraic and has no derivative and no initial condition.",
                alternates=["vdot*C"],
            )),
            ("ode-model-r2-q2", fresh(
                2, "find_error",
                r"A worked solution writes Newton's law for a mass tied to a fixed wall by a spring, with no damper. The external force is \(u\) and \(y\) is the stretch. Exactly one step is wrong.",
                [
                    r"Mass times acceleration equals the sum of the forces on the mass.",
                    r"The external force \(u\) is taken as positive in the direction of increasing \(y\).",
                    r"The spring pulls the mass back toward the unstretched length, opposite the stretch.",
                    r"Newton's law is therefore mass times acceleration \(= u + ky\), because a restoring spring adds to the external force.",
                ],
                3,
                r"The free-body diagram puts the spring force against the displacement. The sign \(-ky\) is what keeps the motion oscillatory rather than runaway. Writing \(+ky\) turns a restoring force into a push that grows with stretch. Dropping the spring deletes the element that sets the stiffness. A damper, if there were one, would oppose velocity, not add another \(+ky\).",
                reasons=[
                    r"The spring opposes the stretch, so the force on the mass is \(-ky\) and the law is mass times acceleration \(= u - ky\).",
                    r"The spring is algebraic, so it drops out and the law is mass times acceleration \(= u\).",
                ],
                correct_reason=0,
            )),
            ("ode-model-r3-q3", fresh(
                3, "order",
                r"Order how you choose the state of a circuit made of resistors, capacitors, and inductors. Each step after the first uses the result of the step before it.",
                [
                    r"Mark the inductors and the capacitors, the elements that store energy.",
                    r"Take inductor current and capacitor voltage as the stored quantities that need initial conditions.",
                    r"Leave the resistors off that list. A resistor has no derivative and no initial condition.",
                    r"Eliminate the resistor variables. The derivatives that remain are the state equations.",
                ],
                r"A state needs an initial condition. Inductor current and capacitor voltage are those quantities. Resistor voltage is fixed once the currents are known, so treating it as a state adds an algebraic variable. Charge instead of capacitor voltage counts the same storage twice. The steady values do not depend on the storage elements. The time constants do.",
            )),
        ]
    if sid == "cruise-control":
        return [
            ("cruise-control-r1-q1", fresh(
                1, "order",
                r"Order how a proportional cruise loop treats a grade or a headwind. Each step after the first uses the result of the step before it.",
                [
                    r"The grade or the headwind pushes the speed away from the driver's reference.",
                    r"That push is a disturbance. It is not a new reference, and it is not by itself a new throttle command.",
                    r"The speed error grows, and the proportional controller changes the throttle command.",
                    r"At steady state a constant output disturbance \(d\) leaves the speed offset \(d/(1+L)\), where \(L\) is the loop gain.",
                ],
                r"Grades, headwinds, and rolling resistance are disturbances the loop has to reject. Calling the grade a reference change would make the controller chase the disturbance. The fraction that remains is \(1/(1+L)\), not the whole disturbance and not the loop gain itself. Integral action is what would remove a constant offset. Proportional control only shrinks it.",
            )),
            ("cruise-control-r2-q2", fresh(
                2, "find_error",
                r"A worked solution adds integral action to a stable cruise loop. Exactly one step is wrong.",
                [
                    r"Proportional cruise control leaves the steady speed error \(r/(1+L)\), with \(L\) the loop gain.",
                    r"Integral action accumulates that speed error over time.",
                    r"While the error is a nonzero constant, the integral command is still changing.",
                    r"The speed can therefore settle with that same nonzero error, which is the point of the integrator.",
                ],
                3,
                r"The integrator cannot rest while the speed error is a nonzero constant. Zero steady error is the only settling point, and only if the loop is still stable. Proportional control is what leaves \(r/(1+L)\). Raising the proportional gain shrinks that error and does not zero it. The integrator is the term that does.",
                reasons=[
                    r"A nonzero constant error keeps the integrator moving, so a stable cruise loop settles only at zero speed error.",
                    r"The integrator holds the proportional error in place so the throttle can rest.",
                ],
                correct_reason=0,
            )),
            ("cruise-control-r3-q3", fresh(
                3, "sym",
                r"Write the steady speed error of proportional cruise control. The loop gain is \(K_c\) times the plant DC gain \(P\), and the speed reference is \(r\). Use \(r\), \(K_c\), and \(P\).",
                "r/(1+Kc*P)",
                {"r": (2, 40), "Kc": (0.5, 12), "P": (0.5, 12)},
                r"The steady speed is \(L r/(1+L)\) with \(L = K_c P\), so the shortfall is \(r/(1+L)\). Raising \(K_c\) makes the denominator larger and the error smaller. The error stays positive for any finite gain. Reporting \(r/(K_c P)\) drops the 1. Reporting \(K_c P\) is the loop gain, not the error. Reporting \(r\) is the error only if the throttle does nothing. Zero error needs integral action, not a larger \(K_c\).",
                alternates=[
                    "r/(1+P*Kc)",
                    "r*(1+Kc*P)**(-1)",
                    "r/(P*Kc+1)",
                ],
            )),
        ]
    if sid == "model-method":
        return [
            ("model-method-r1-q1", fresh(
                1, "order",
                r"Order the choice of what a control model keeps. Each step after the first uses the result of the step before it.",
                [
                    r"Name the behavior the loop has to get right, and set aside effects that do not change it.",
                    r"From what remains, list every stored quantity that needs an initial condition. Those are the candidate states.",
                    r"Drop each candidate that has already settled before that behavior starts, and replace it by the gain it settles to. The shorter list is the state.",
                    r"Take that shorter list as closed. A command or a disturbance stays an input, and it is not added back onto the state unless you give it dynamics of its own.",
                ],
                r"A state is a stored quantity with an initial condition. The candidates are listed first. A fast electrical transient is then dropped from that list and replaced by the gain it settles to. Only that shorter list is the state. A command or a disturbance is labeled an input afterward, and it is not added back unless it has dynamics of its own. Calling the command a state swaps the columns of the model you write next. Dropping the integrator that the loop needs for zero error makes the model predict an offset the hardware will not show.",
            )),
            ("model-method-r1-q3", fresh(
                1, "find_error",
                r"A worked solution models a motor whose electrical transient dies in a fraction of a millisecond, for a loop that moves a load over several seconds. Exactly one step is wrong.",
                [
                    r"The electrical transient is over long before the load has moved appreciably.",
                    r"The ratio of the slow time scale to the fast one is large.",
                    r"During the motion that matters, the electrical part sits at the value its fast dynamics settle to.",
                    r"The model should keep the electrical differential equation, because a stored quantity is always a state of the loop.",
                ],
                3,
                r"A control model keeps the stored quantities that move on the time window of the loop. The electrical transient has already settled, so it contributes its steady gain, not another differential equation. Keeping it is faithful and unnecessary. Dropping the slow load equation would delete the motion the loop is for. The scale ratio justifies the replacement, and it has to be computed after the equations are in comparable units.",
                reasons=[
                    r"When the scale ratio is large, replace the fast transient by the gain it settles to. The loop model follows the load.",
                    r"A large scale ratio means the electrical pole dominates, so the load equation is the one to drop.",
                ],
                correct_reason=0,
            )),
            ("model-method-r2-q2", fresh(
                2, "multi",
                r"A differential equation has been written. Which statements about dividing through by its scales are true? Select every correct statement.",
                [
                    r"The terms become pure numbers, so a coefficient can be compared with 1.",
                    r"A term that is tiny on that scale can be dropped on purpose for the time window you care about.",
                    r"Scaling moves the steady resting value to a different physical equilibrium.",
                    r"Coefficients can be compared while the terms still carry different units, because a small number is always a small effect.",
                ],
                [0, 1],
                r"Dividing by the scales strips the units, which is the only way a coefficient of 0.01 and a coefficient of 1 are the same kind of number. The resting value is fixed by setting the derivative to zero, and scaling does not move it. Comparing raw coefficients that still have different units drops the wrong term. A sensor gain converts units by multiplication, not by this comparison.",
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
