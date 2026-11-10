#!/usr/bin/env python3
"""Load banks, compare numeric answers, and report for one batch verifier.

Answer formulas stay in ``verify_me132_bN.py``. This module does not import a
generator, so a closed-form mistake in the generator is not reused here.

``python3 skilltree/verify_me132_bN.py`` remains the command each batch runs.
"""
import json
import math
import os
import random

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BANK = os.path.join(ROOT, "skilltree", "bank")
EXP = os.path.join(ROOT, "skilltree", "explainers")
from expr import ExprError, evaluate, parse  # noqa: E402

_SYMPY_GLOBAL = None


def load_banks(skills):
    return {
        sid: json.load(open(os.path.join(BANK, sid + ".json"), encoding="utf-8"))
        for sid in skills
    }


def load_texts(skills):
    return {
        sid: json.dumps(json.load(open(os.path.join(EXP, sid + ".json"), encoding="utf-8")))
        for sid in skills
    }


def skill_of(qid):
    return qid.rsplit("-r", 1)[0]


def answer(banks, qid):
    sid = skill_of(qid)
    for q in banks[sid]["questions"]:
        if q["id"] == qid:
            return float(q["answer"])
    raise SystemExit("missing " + qid)


def numeric_ids(banks):
    ids = []
    for bank in banks.values():
        for q in bank["questions"]:
            if q.get("type") == "numeric":
                ids.append(q["id"])
    return ids


def check_expected(banks, expected, mismatches, rel=2e-3):
    """Compare every supplied recomputation. Every numeric question must be listed."""
    present = numeric_ids(banks)
    present_set = set(present)
    for qid in present:
        if qid not in expected:
            mismatches.append(f"{qid}: numeric question has no independent check")
    for qid in expected:
        if qid not in present_set:
            mismatches.append(f"{qid}: check has no numeric question")
    n = 0
    for qid, exp in expected.items():
        if qid not in present_set:
            continue
        n += 1
        got = answer(banks, qid)
        scale = max(abs(float(exp)), 1e-9)
        if abs(got - float(exp)) / scale > rel:
            mismatches.append(f"{qid}: bank {got} != recomputed {exp}")
    return n


def _sympy_global():
    global _SYMPY_GLOBAL
    if _SYMPY_GLOBAL is None:
        import sympy as sp
        _SYMPY_GLOBAL = {
            "Symbol": sp.Symbol,
            "Integer": sp.Integer,
            "Float": sp.Float,
            "Rational": sp.Rational,
        }
    return _SYMPY_GLOBAL


def _to_sympy(text, names):
    import sympy as sp
    from sympy.parsing.sympy_parser import (
        convert_xor,
        implicit_multiplication_application,
        parse_expr,
        standard_transformations,
    )
    local = {name: sp.Symbol(name) for name in names}
    if "pi" not in local:
        local["pi"] = sp.pi
    if "e" not in local:
        local["e"] = sp.E
    local.update({
        "sqrt": sp.sqrt,
        "abs": sp.Abs,
        "exp": sp.exp,
        "ln": sp.log,
        "log": sp.log,
        "sin": sp.sin,
        "cos": sp.cos,
        "tan": sp.tan,
    })
    trans = standard_transformations + (convert_xor, implicit_multiplication_application)
    return parse_expr(
        text,
        local_dict=local,
        global_dict=_sympy_global(),
        transformations=trans,
        evaluate=True,
    )


def _equivalent(left, right):
    import sympy as sp
    if sp.simplify(left - right) == 0:
        return True
    try:
        return bool(left.equals(right))
    except Exception:
        return False


def _check_symbolic_question(q, mismatches):
    qid = q.get("id", "<no id>")
    variables = q.get("variables")
    if not isinstance(variables, list) or not variables:
        mismatches.append(f"{qid}: symbolic question has no variables")
        return
    names = []
    for spec in variables:
        if not isinstance(spec, dict) or "name" not in spec:
            mismatches.append(f"{qid}: bad variable spec")
            return
        names.append(spec["name"])
    answer = q.get("answer")
    if not isinstance(answer, str):
        mismatches.append(f"{qid}: symbolic key is not text")
        return
    try:
        key_ast = parse(answer, names)
    except ExprError as exc:
        mismatches.append(f"{qid}: key is not a valid expression ({exc})")
        return
    try:
        key_sp = _to_sympy(answer, names)
    except Exception as exc:
        mismatches.append(f"{qid}: SymPy rejected the key ({exc})")
        return
    for alt in q.get("alternates") or []:
        try:
            parse(alt, names)
            alt_sp = _to_sympy(alt, names)
        except Exception as exc:
            mismatches.append(f"{qid}: alternate {alt!r} is not well formed ({exc})")
            continue
        if not _equivalent(key_sp, alt_sp):
            mismatches.append(f"{qid}: alternate {alt!r} is not equivalent to the key")
    import sympy as sp
    symbols = [sp.Symbol(name) for name in names]
    try:
        fn = sp.lambdify(symbols, key_sp, modules="math")
    except Exception as exc:
        mismatches.append(f"{qid}: SymPy could not evaluate the key ({exc})")
        return
    rng = random.Random(0)
    hits = 0
    tries = 0
    while hits < 6 and tries < 24:
        tries += 1
        env = {}
        for spec in variables:
            env[spec["name"]] = rng.uniform(float(spec["min"]), float(spec["max"]))
        got = evaluate(key_ast, env)
        try:
            spv = fn(*[env[name] for name in names])
            spv = float(spv)
        except Exception:
            spv = None
        if got is None or spv is None or not math.isfinite(spv):
            continue
        scale = max(abs(got), abs(spv), 1e-9)
        if abs(got - spv) > 1e-6 * scale:
            mismatches.append(f"{qid}: app parser and SymPy disagree on the key")
            return
        hits += 1
    if hits < 6:
        mismatches.append(f"{qid}: key is not finite on the declared ranges")


def check_symbolic(banks, mismatches):
    """CAS-check every symbolic key: well formed, finite on its ranges, alternates equivalent.

    Returns the number of symbolic questions. Does nothing when there are none.
    """
    pending = []
    for bank in banks.values():
        for q in bank.get("questions") or []:
            if q.get("type") == "symbolic":
                pending.append(q)
    if not pending:
        return 0
    for q in pending:
        _check_symbolic_question(q, mismatches)
    return len(pending)


def finish(numeric, mismatches, banks=None):
    symbolic = check_symbolic(banks, mismatches) if banks is not None else 0
    print(f"numeric {numeric}, symbolic {symbolic}, mismatches {len(mismatches)}, worked examples checked")
    for item in mismatches:
        print(" ", item)
    if mismatches:
        raise SystemExit(1)
    print("0 mismatches")


def rk4(f, y0, t_end, steps):
    """Fixed-step scalar RK4. ``steps`` is the step count, not a time increment."""
    y = float(y0)
    h = t_end / steps
    t = 0.0
    for _ in range(steps):
        k1 = f(t, y)
        k2 = f(t + h / 2, y + h * k1 / 2)
        k3 = f(t + h / 2, y + h * k2 / 2)
        k4 = f(t + h, y + h * k3)
        y += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        t += h
    return y


def rk4_vec(f, y0, t_end, steps):
    y = np.array(y0, dtype=float)
    h = t_end / steps
    t = 0.0
    for _ in range(steps):
        k1 = f(t, y)
        k2 = f(t + h / 2, y + h * k1 / 2)
        k3 = f(t + h / 2, y + h * k2 / 2)
        k4 = f(t + h, y + h * k3)
        y = y + h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
        t += h
    return y


def prop_steady(kc, p, reference, disturbance=0.0, tau=0.4):
    """RK4 of a first-order plant under proportional control. ``d`` adds at the output."""
    def f(_t, yp):
        measured = yp + disturbance
        u = kc * (reference - measured)
        return (p * u - yp) / tau
    yp = rk4(f, 0.0, 40 * tau, 4000)
    return yp + disturbance
