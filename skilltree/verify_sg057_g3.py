#!/usr/bin/env python3
"""Independent check for SG-057 group 3.

Re-runs the batch verifiers whose banks this group edited, then recomputes
every numeric answer on the loop-gain, diagram, sensitivity-core, margin,
and amplifier-compensation banks. Does not import the generator.
"""
import cmath
import math
import os
import subprocess
import sys

from verify_harness import check_expected, finish, load_banks

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRIOR = [
    "skilltree/verify_me132_b3.py",
    "skilltree/verify_me132_b4.py",
]


def crossover_margin(fu, fp):
    """Phase margin of an integrator plus one real pole, from a magnitude bisection."""
    def mag(freq):
        return (fu / freq) / math.sqrt(1 + (freq / fp) ** 2)

    lo, hi = fu / 1000.0, fu
    for _ in range(60):
        mid = (lo + hi) / 2
        if mag(mid) > 1:
            lo = mid
        else:
            hi = mid
    fc = (lo + hi) / 2
    return 90 - math.degrees(math.atan(fc / fp))


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
            mismatches.append(script + " failed: " + " | ".join(tail[-8:]))

    banks = load_banks([
        "loop-gain", "fb-intro", "fb-errors", "stability", "amp-compensation",
    ])
    expected = {}

    expected["loop-gain-r1-q5"] = 3 * 6 * 0.5
    expected["loop-gain-r2-q5"] = 15 / 5
    expected["loop-gain-r3-q6"] = 8 / 8
    w = 18.0
    expected["loop-gain-r4-q4"] = w if abs(abs(18 / (1j * w)) - 1) < 1e-9 else -1
    expected["loop-gain-r4-q5"] = 4 * 0.5 * 7

    expected["fb-intro-r2-q5"] = 5 - 2
    expected["fb-intro-r3-q5"] = 0.25 * 8
    expected["fb-intro-r4-q4"] = 4 * 0.5

    expected["fb-errors-r1-q5"] = 1 / (1 + 24)
    expected["fb-errors-r2-q4"] = 1 / (1 + 9)
    expected["fb-errors-r3-q5"] = 1 / (1 + 3)
    expected["fb-errors-r4-q4"] = 1 / (1 + 11)
    expected["fb-errors-r4-q6"] = 1 / (1 + 4)

    expected["stability-r1-q5"] = 180 - 140
    expected["stability-r2-q4"] = 1 / 0.25
    expected["stability-r3-q5"] = 20 * math.log10(2)
    expected["stability-r4-q4"] = 180 - 125

    ro, cl = 50.0, 10e-9
    fp = 1 / (2 * math.pi * ro * cl)
    expected["amp-compensation-r3-q2"] = crossover_margin(1e6, fp)
    expected["amp-compensation-r4-q2"] = math.sqrt(2) * 10
    lag = cmath.phase(1 / (1j * (1 + 0.25j)))
    expected["amp-compensation-r4-q4"] = 180 + math.degrees(lag)

    numeric = check_expected(banks, expected, mismatches)
    finish(numeric, mismatches, banks)


if __name__ == "__main__":
    main()
