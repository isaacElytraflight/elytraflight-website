#!/usr/bin/env python3
"""Independent check for SG-057 group 4.

Re-runs the batch verifiers whose banks this group edited, then recomputes
every numeric answer on the two new banks. Does not import the generator.
"""
import os
import subprocess
import sys

from verify_harness import check_expected, finish, load_banks

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PRIOR = [
    "skilltree/verify_me132_b5.py",
    "skilltree/verify_me132_b8.py",
    "skilltree/verify_nlo_nb3.py",
    "skilltree/verify_nlo_intro.py",
]


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

    banks = load_banks(["local-linear-approximation", "finite-horizon-sequence"])
    expected = {}

    # f(t) = t^3 at t = 2, step 0.1. Value 8, derivative 12.
    expected["local-linear-approximation-r1-q2"] = 2.0 ** 3 + (3 * 2.0 ** 2) * 0.1
    # f(x) = 1/x at x = 4. Derivative -1/16, step +0.5. The predicted change.
    expected["local-linear-approximation-r2-q2"] = -(1.0 / 16.0) * 0.5
    # f(x) = x^2 + 3x at x = 1. The derivative is 2x + 3.
    expected["local-linear-approximation-r3-q2"] = 2.0 * 1.0 + 3.0
    # y = 4 x^2 at x = 1.5. The slope is 8x.
    expected["local-linear-approximation-r4-q1"] = 8.0 * 1.5

    expected["finite-horizon-sequence-r1-q2"] = 2.0 + 5.0 + 1.0
    expected["finite-horizon-sequence-r2-q2"] = 3.0 + 1.0 + (-2.0) + 4.0
    expected["finite-horizon-sequence-r3-q2"] = 3.0 ** 2 + 1.0 ** 2 + 1.0 ** 2
    expected["finite-horizon-sequence-r4-q1"] = (2.0 - 0.0) ** 2 + (5.0 - 2.0) ** 2
    expected["finite-horizon-sequence-r4-q3"] = 7.0

    numeric = check_expected(banks, expected, mismatches)
    finish(numeric, mismatches, banks)
    return 1 if mismatches else 0


if __name__ == "__main__":
    sys.exit(main())
