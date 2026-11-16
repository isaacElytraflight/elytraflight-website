#!/usr/bin/env python3
"""Independent check for SG-057 group 1.

Re-runs the batch verifiers whose banks this group edited, then recomputes
the numeric answers that those verifiers do not cover: every numeric item
on the mechanical and feedback-amplifier banks, and the numeric items added
to the other edited banks. Does not import the generator.
"""
import math
import os
import subprocess
import sys

from verify_harness import answer, check_expected, finish, load_banks

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRIOR = [
    "skilltree/verify_me132_b2.py",
    "skilltree/verify_me132_b3.py",
    "skilltree/verify_sg063_ee105_ch1.py",
    "skilltree/verify_sg063_ee105_ch2.py",
]


def check_listed(banks, expected, mismatches, rel=2e-3):
    """Recompute a listed subset. Does not require every numeric in the bank."""
    n = 0
    for qid, exp in expected.items():
        got = answer(banks, qid)
        n += 1
        scale = max(abs(float(exp)), 1e-9)
        if abs(got - float(exp)) / scale > rel:
            mismatches.append(f"{qid}: bank {got} != recomputed {exp}")
    return n


def main():
    mismatches = []
    for script in PRIOR:
        proc = subprocess.run(
            [sys.executable, script],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        if proc.returncode != 0:
            tail = ((proc.stdout or "") + (proc.stderr or "")).strip().splitlines()
            mismatches.append(script + " failed: " + " | ".join(tail[-6:]))

    banks = load_banks(["lti-mech", "fb-amp"])
    expected = {}
    # mass settles at F/k
    expected["lti-mech-r1-q2"] = 10 / 400
    expected["lti-mech-r2-q1"] = math.sqrt(200 / 0.5)
    expected["lti-mech-r2-q2"] = 4 / (2 * math.sqrt(200 * 0.5))
    expected["lti-mech-r2-q3"] = 0.5 / 0.1
    # |1 / (k - m w^2 + j b w)| * force amplitude, w = 5
    expected["lti-mech-r3-q1"] = 3 / abs(complex(25 - 25, 2 * 5))
    expected["lti-mech-r4-q2"] = 2 * (2 * math.pi / 0.5) ** 2
    tau = 1200 / 60
    expected["lti-mech-r4-q3"] = (600 / 60) * (1 - math.exp(-20 / tau))
    expected["lti-mech-r4-q4"] = math.sqrt(0.2 / 0.05)

    expected["fb-amp-r1-q1"] = 2e4 * 0.01
    feedback = 3 / (3 + 27)
    loop = 2000 * feedback
    expected["fb-amp-r1-q3"] = (1 / feedback) * (loop / (1 + loop))
    expected["fb-amp-r2-q1"] = (2 + 38) / 2
    expected["fb-amp-r2-q4"] = 1000 / (1 + 1000 * 0.1)
    expected["fb-amp-r3-q2"] = (1 / 0.0005 - 1) / 0.01
    expected["fb-amp-r3-q3"] = 5000 * (2 / (2 + 18))
    sense = 1 / (1 + 99)
    expected["fb-amp-r4-q1"] = 100 / (1 + 1e5 * sense)
    expected["fb-amp-r4-q2"] = 10 * (1 + 1e5 * (1 / 20)) / 1000

    numeric = check_expected(banks, expected, mismatches)

    moved = {
        "step-resp-r1-q7": 3 * 0.4,
        "step-resp-r2-q5": 4 * (1 - math.exp(-0.5)) * math.exp(-0.25),
        "step-resp-r3-q5": 2 * (1 - math.exp(-0.5)) * math.exp(-1),
        "step-resp-r4-q4": 6 / 3,
        "step-resp-r4-q5": 5 * 0.02,
        "step-resp-r4-q6": math.exp(-1) - math.exp(-2),
        "lti-circuits-r1-q6": 0.8 + 1.2,
        "lti-circuits-r2-q5": 2 * 3 * 0.5,
        "lti-circuits-r2-q6": 2.5 * 4,
        "lti-circuits-r3-q7": 2 * 4 * 0.1,
        "pole-zero-r2-q4": math.exp(-4 * 0.5),
        "pole-zero-r3-q4": 6,
        "tf-r4-q4": 7 / 1,
        "tf-r4-q5": 6,
        "freq-resp-circuits-r4-q4": 100 / math.sqrt(1 + (100 / 10) ** 2),
        "rlc-r4-q4": 1 / (2 * 8),
    }
    others = load_banks(["step-resp", "lti-circuits", "pole-zero", "tf", "freq-resp-circuits", "rlc"])
    numeric += check_listed(others, moved, mismatches)
    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
