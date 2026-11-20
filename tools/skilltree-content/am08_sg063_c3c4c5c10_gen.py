#!/usr/bin/env python3
"""SG-063 Feedback Systems, four banks.

Scope is the Examples, Dynamic behavior, Linear systems, and PID control
sections intersected with the grandfather list. That intersection is exactly
four banks: app-examples, limit-cycles, discrete-time, pid-impl. The other
four grandfathered ids (min-phase, gen-gain-phase, feedforward,
perf-specs-freq) stay on the list for the next slice. Nothing is added.

Each swapped multiple-choice question is kept on retired_questions under its
old id. The replacement gets the next free id in that round and starts at
version 1. Running this again does not swap a question twice.

Does not write explainers. The new questions use the same relations as the
explainers, and the explainer worked examples do not use these prompts.
The verifier does not import this file.

Symbolic ranges are closed boxes on which the key stays finite and positive.
No key is a difference of two independent positives. Every denominator is
bounded away from zero on the box. Prompt names are the graded identifiers
(a, b, not a_1).
"""
import itertools
import json
import os
import re

from banklib import Bank

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK_DIR = os.path.join(ROOT, "skilltree", "bank")
GRAND = os.path.join(ROOT, "skilltree", "deep_quota_grandfather.json")

SKILLS = [
    "app-examples",
    "limit-cycles",
    "discrete-time",
    "pid-impl",
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
    if sid == "app-examples":
        return [
            ("app-examples-r1-q1", fresh(
                1, "order",
                r"Order the linear model of one tank with constant surface area \(A > 0\), hydraulic resistance \(R > 0\), and a constant inflow. Each step after the first uses the result of the step before it.",
                [
                    r"The stored quantity is the liquid level \(h\). The constant inflow is an input of this tank, and the resistance \(R\) is a parameter.",
                    r"Write a volume balance for the level named in the previous step. \(A\) times the derivative of \(h\) equals the constant inflow minus the outflow, and that outflow equals \(h/R\).",
                    r"Divide the balance from the previous step by the positive area \(A\). The coefficient of \(h\) is \(-1/(AR)\), so the time constant of this first-order model is the product \(AR\).",
                    r"Set the derivative in the equation from the previous step to zero. The coefficient of \(h\) is nonzero, so there is exactly one equilibrium level, and that level equals the constant inflow times \(R\).",
                ],
                r"The level is the state. The balance is \(A\dot{h} = q_{in} - h/R\). Dividing by \(A\) gives \(\dot{h} = -h/(AR) + q_{in}/A\), so the time constant is \(AR\) and the coefficient of \(h\) is \(-1/(AR)\). Setting the derivative to zero gives the one equilibrium \(h = q_{in} R\). The inflow is an input, the outflow is fixed by the level, and the resistance is a parameter. Using \(R\) alone as the time constant drops the area.",
            )),
            ("app-examples-r2-q1", fresh(
                2, "find_error",
                r"A worked solution classifies quantities in a tank and in the motor model \(J\dot{\omega} = K_t i - b\omega\). Exactly one step is wrong.",
                [
                    r"In the tank, the level is a state because it stores liquid. The hydraulic resistance is a parameter.",
                    r"The tank outflow equals the level divided by the resistance, so the outflow is fixed by that state and that parameter. It is not an extra state.",
                    r"In the motor equation, the speed \(\omega\) is a state. The inertia \(J\) and the torque constant \(K_t\) are parameters.",
                    r"In that same motor equation, the armature current \(i\) is always a second state, because the equation writes \(i\) next to \(\omega\).",
                ],
                3,
                r"The mechanical equation has one state, the speed. In \(J\dot{\omega} = K_t i - b\omega\) the current is the input. It becomes a state only if a later model adds the electrical dynamics, which this equation does not. The tank level is the tank state, the outflow \(h/R\) is algebraic, and the resistance, the inertia, and the torque constant are parameters.",
                reasons=[
                    r"In \(J\dot{\omega} = K_t i - b\omega\) the current is the input. It is a state only in a larger model that adds the electrical dynamics.",
                    r"Every symbol written next to the speed is a state, so the current is always a second state of this equation.",
                ],
                correct_reason=0,
            )),
            ("app-examples-r3-q1", fresh(
                3, "sym",
                r"a and b are positive. A pendulum is linearized at the downward equilibrium, with gravitational acceleration a and length b. Write the square of the natural frequency. Use a and b.",
                "a/b",
                {"a": (0.25, 18), "b": (0.25, 18)},
                r"The linearized equation at the downward equilibrium is \(\ddot{\theta} + (a/b)\theta = 0\), so the square of the natural frequency is \(a/b\). The product \(a*b\) is not that square. The reciprocal \(b/a\) is a time squared. The upright equilibrium linearizes with the opposite sign and is not this oscillation.",
                alternates=["a*b**(-1)", "(a)/(b)", "a*(b**(-1))"],
            )),
        ]
    if sid == "limit-cycles":
        return [
            ("limit-cycles-r1-q1", fresh(
                1, "order",
                r"Order how a stable limit cycle differs from a closed orbit of a linear planar center. Each step after the first uses the result of the step before it.",
                [
                    r"Start with a closed orbit: the state returns to its starting point after a positive period, and the orbit is not a single equilibrium.",
                    r"Keep the orbit from the previous step only when some neighborhood of it contains no other closed orbit. The orbit is then isolated. A linear planar center fails this test, because its closed orbits form a continuous family.",
                    r"Keep the isolated orbit from the previous step only when every trajectory that starts close enough to it, and not on it, approaches it as time increases. That orbit is a stable limit cycle.",
                    r"Collect every initial condition that approaches the stable limit cycle named in the previous step. That set is its region of attraction. The set contains a neighborhood of the cycle, and it need not be the whole plane.",
                ],
                r"A limit cycle is an isolated periodic orbit. Stability means nearby trajectories approach it. A linear planar center has a continuous family of closed orbits, so none of them is isolated. The region of attraction is the set of states that approach the cycle. Stability guarantees a neighborhood of the cycle, not the whole plane.",
            )),
            ("limit-cycles-r1-q2", fresh(
                1, "multi",
                r"Which statements about periodic orbits are true? Select every correct statement.",
                [
                    r"If \(\dot{x} = Ax\) has a nonconstant periodic solution \(x(t)\), then \(c\, x(t)\) is a periodic solution on a different orbit for every real \(c\) near 1 with \(c \neq 1\). An autonomous linear system therefore has no isolated periodic orbit.",
                    r"The Van der Pol equation \(\ddot{x} - \mu(1-x^2)\dot{x} + x = 0\), with \(\mu > 0\), has exactly one periodic orbit, and that orbit is stable.",
                    r"In a Hopf bifurcation, an equilibrium persists while a complex conjugate pair of its eigenvalues crosses the imaginary axis, and a limit cycle is created or destroyed.",
                    r"Every feedback loop has a limit cycle.",
                ],
                [0, 1, 2],
                r"Scaling a nonconstant periodic solution of \(\dot{x} = Ax\) by a factor near 1 produces a nearby periodic orbit, so no periodic orbit of an autonomous linear system is isolated. The stated Van der Pol equation has one stable periodic orbit when \(\mu > 0\). A Hopf bifurcation keeps the equilibrium and creates or destroys a limit cycle as the critical pair crosses the imaginary axis. A stable linear feedback loop has no limit cycle, so feedback alone does not produce one.",
            )),
            ("limit-cycles-r2-q2", fresh(
                2, "find_error",
                r"A worked solution states general facts about bifurcations. Exactly one step is wrong.",
                [
                    r"Varying a parameter can produce a bifurcation: a qualitative change in the number or the stability of equilibria or of periodic orbits.",
                    r"Moving the initial condition from one region of attraction to another changes which attractor is approached. That is not a bifurcation, because the vector field is unchanged.",
                    r"In a Hopf bifurcation, an equilibrium persists while a complex conjugate pair of its eigenvalues crosses the imaginary axis, and a limit cycle is created or destroyed.",
                    r"A bifurcation also occurs when every parameter is held fixed and only time increases, because the state moves.",
                ],
                3,
                r"A bifurcation is a change in the vector field as a parameter varies. Changing the initial condition selects another basin and leaves the vector field alone. In a Hopf bifurcation the equilibrium persists and a limit cycle is created or destroyed. The passage of time at a fixed parameter is an ordinary trajectory, not a bifurcation.",
                reasons=[
                    r"A bifurcation is a change in the vector field as a parameter varies. Time evolution at fixed parameters is not a bifurcation.",
                    r"Letting time increase at fixed parameters is a bifurcation, because the state eventually changes.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "discrete-time":
        return [
            ("discrete-time-r1-q1", fresh(
                1, "order",
                r"Order the exact sampling of one real continuous-time pole and the stability reading of its image. Each step after the first uses the result of the step before it.",
                [
                    r"Start from a real continuous-time pole at \(-a\) with \(a > 0\). The pole lies in the open left half-plane, so the continuous mode decays.",
                    r"Sample the pole from the previous step with period \(b > 0\) under the exact map \(z = e^{s b}\). The image is the real number \(e^{-a b}\), strictly between 0 and 1.",
                    r"The image from the previous step has absolute value strictly less than 1, so that discrete mode decays to zero. A pole whose absolute value is strictly greater than 1 grows, and a pole whose absolute value equals 1 does not decay to zero.",
                    r"Keep the decay to zero stated in the previous step, and replace the sample period that produced that image by a smaller positive period. The new image lies strictly between the old image and 1, so it is closer to 1 and the decay to zero still holds.",
                ],
                r"A real pole at \(-a\) with \(a > 0\) decays in continuous time. Exact sampling with period \(b > 0\) sends it to \(e^{-a b}\), which lies in \((0, 1)\) and so decays in discrete time. A pole with absolute value greater than 1 grows, and a pole with absolute value 1 does not decay to zero. A smaller positive period moves the same continuous pole closer to \(z = 1\) without leaving the open unit disk.",
            )),
            ("discrete-time-r2-q1", fresh(
                2, "sym",
                r"a and b are positive. Write the exact discrete-time image of the continuous-time pole at -a when the sample period is b. Use a and b.",
                "exp(-a*b)",
                {"a": (0.25, 4), "b": (0.25, 4)},
                r"The exact map is \(z = e^{s b}\) with \(s = -a\), so the discrete pole is \(\exp(-a b)\). For positive \(a\) and \(b\) this number lies in \((0, 1)\). The product \(a*b\) is the exponent, not the pole. Forward Euler would give \(1 - a*b\), which is a different map. The reciprocal \(1/(a*b)\) is not this image.",
                alternates=["exp(-(a*b))", "exp(-b*a)", "e**(-a*b)"],
            )),
            ("discrete-time-r2-q3", fresh(
                2, "find_error",
                r"A worked solution states facts about sampling with a fixed period \(T > 0\). Exactly one step is wrong.",
                [
                    r"The Nyquist frequency in hertz is \(1/(2T)\).",
                    r"A continuous-time sinusoid whose frequency in hertz is strictly larger than \(1/(2T)\) aliases to a lower frequency when it is sampled at period \(T\).",
                    r"A discrete pole inside the open unit disk says that the corresponding mode decays. That fact does not, by itself, decide whether a continuous-time sinusoid was aliased.",
                    r"Raising the sample rate, while holding the sinusoid's frequency fixed, is what creates the alias.",
                ],
                3,
                r"The Nyquist frequency is \(1/(2T)\) hertz, and a sinusoid strictly above it aliases to a lower frequency. A discrete pole inside the open unit disk says the mode decays. It is not an aliasing test. Raising the sample rate raises the Nyquist frequency and can put the sinusoid below it. The wrong step reverses that effect.",
                reasons=[
                    r"Aliasing appears when the sample rate is too low for the sinusoid. Raising the sample rate raises the Nyquist frequency. A pole inside the unit disk is a stability fact, not an aliasing test.",
                    r"A higher sample rate folds the sinusoid downward, so increasing the sample rate is what creates the alias.",
                ],
                correct_reason=0,
            )),
        ]
    if sid == "pid-impl":
        return [
            ("pid-impl-r1-q1", fresh(
                1, "order",
                r"Order the practical derivative path of a PID controller. Each step after the first uses the result of the step before it.",
                [
                    r"A pure derivative \(K_d s\) amplifies high-frequency measurement noise, so the implemented derivative is not left as \(K_d s\).",
                    r"Replace the pure derivative from the previous step by \(K_d s/(\tau_f s + 1)\), where \(\tau_f = \tau_d/N\) with \(\tau_d > 0\) and \(N > 0\). The filter pole is at \(-N/\tau_d\). The denominator degree equals the numerator degree, so the transfer function is proper.",
                    r"Drive the filtered derivative from the previous step with \(c r - y\). The weight \(c = 0\) makes the driving signal \(-y\), so a step in the reference \(r\) does not reach the derivative.",
                    r"Read the loop gain from the measured output \(y\) used in the driving signal of the previous step. Changing the weight \(c\) changes the response from the reference to the output and does not change that loop gain.",
                ],
                r"A pure derivative amplifies measurement noise, so the derivative is filtered as \(K_d s/(\tau_f s + 1)\) with \(\tau_f = \tau_d/N\). That filter is proper, and its pole is at \(-N/\tau_d\). The weight \(c = 0\) drives the derivative with \(-y\), so a reference step does not kick it. The loop gain is read from \(y\). The weight \(c\) changes the reference response and does not change that loop gain.",
            )),
            ("pid-impl-r2-q2", fresh(
                2, "multi",
                r"Which statements about a PID implementation are true? Select every correct statement.",
                [
                    r"With derivative setpoint weight \(c = 0\), the derivative is driven by \(-y\). A step in the reference does not kick the derivative.",
                    r"For every sample period \(T > 0\), backward Euler \(z = 1/(1 - s T)\) maps every finite pole with negative real part into the open unit disk.",
                    r"On the unit circle \(z = e^{j\omega T}\) with \(|\omega T| < \pi\), a one-sample delay \(z^{-1}\) has phase \(-\omega T\) radians.",
                    r"Forward Euler \(z = 1 + s T\) maps every stable continuous pole into the open unit disk for every sample period \(T > 0\).",
                ],
                [0, 1, 2],
                r"The weight \(c = 0\) drives the derivative with \(-y\), so a reference step does not reach it. For \(T > 0\) and \(\mathrm{Re}(s) < 0\), the backward-Euler denominator has real part greater than 1, so its image lies in the open unit disk. A one-sample delay contributes phase \(-\omega T\) on \(z = e^{j\omega T}\) when \(|\omega T| < \pi\). Forward Euler does not keep every stable pole inside that disk: the pole at \(-40\) with \(T = 0.1\) maps to \(-3\).",
            )),
            ("pid-impl-r3-q1", fresh(
                3, "sym",
                r"a and b are positive. A continuous-time pole at -a is discretized with backward Euler and sample period b. Write the discrete pole. Use a and b.",
                "1/(1+a*b)",
                {"a": (0.25, 18), "b": (0.25, 18)},
                r"Backward Euler sets \(z = 1/(1 - s b)\) with \(s = -a\), which simplifies to \(1/(1 + a b)\). The denominator is greater than 1, so the value lies in \((0, 1)\). Forward Euler would write \(1 - a b\), and that value lies outside the unit disk when \(a b > 2\). The exact map \(\exp(-a b)\) is a different expression. The product \(a*b\) alone is not the discrete pole.",
                alternates=["1/(1+b*a)", "(1+a*b)**(-1)", "1/(1+(a*b))"],
            )),
        ]
    raise SystemExit("no swaps for " + sid)


def assert_item(item):
    """Reject a symbolic box whose key is not finite and positive at every corner."""
    if item.get("type") != "symbolic":
        return
    import sympy as sp
    specs = item["variables"]
    names = [spec["name"] for spec in specs]
    for name in names:
        if re.search(r"(?<![A-Za-z0-9_])" + re.escape(name) + r"(?![A-Za-z0-9_])", item["prompt"]) is None:
            raise SystemExit("prompt misses graded name " + name)
    local = {name: sp.Symbol(name) for name in names}
    local["exp"] = sp.exp
    local["e"] = sp.E
    local["pi"] = sp.pi
    expr = sp.parse_expr(item["answer"], local_dict=local)
    used = {str(symbol) for symbol in expr.free_symbols}
    missing = [name for name in names if name not in used]
    if missing:
        raise SystemExit("answer misses " + ", ".join(missing))
    bounds = []
    for spec in specs:
        lo, hi = float(spec["min"]), float(spec["max"])
        if lo <= 0 or hi <= lo:
            raise SystemExit("nonpositive range for " + spec["name"])
        bounds.append((lo, hi))
    for corner in itertools.product(*bounds):
        value = complex(expr.subs(dict(zip(names, corner))))
        if abs(value.imag) > 1e-9 or not (value.real > 0) or value.real != value.real:
            raise SystemExit(f"corner {corner} gives {value} for {item['answer']}")
    for alt in item.get("alternates") or []:
        alt_expr = sp.parse_expr(alt, local_dict=local)
        if sp.simplify(expr - alt_expr) != 0:
            raise SystemExit("alternate not equivalent: " + alt)


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
        for _old, new in swaps_for(sid):
            assert_item(new)
    for sid in SKILLS:
        apply_skill(sid)
    drop_grandfather()


if __name__ == "__main__":
    main()
