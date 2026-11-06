#!/usr/bin/env python3
"""Load banks, compare numeric answers, and report for one batch verifier.

Answer formulas stay in ``verify_me132_bN.py``. This module does not import a
generator, so a closed-form mistake in the generator is not reused here.

``python3 skilltree/verify_me132_bN.py`` remains the command each batch runs.
"""
import json
import os

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BANK = os.path.join(ROOT, "skilltree", "bank")
EXP = os.path.join(ROOT, "skilltree", "explainers")


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


def finish(numeric, mismatches):
    print(f"numeric {numeric}, mismatches {len(mismatches)}, worked examples checked")
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
