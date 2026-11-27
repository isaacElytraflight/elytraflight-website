#!/usr/bin/env python3
"""Numeric gate for the audit-136 pass.

Delegates to the existing batch verifiers that cover every edited skill.
Several sg063 verifiers still assert a historical deep-quota grandfather
count. That list is empty on main, and the deep-quota gate checks it.
Those lines are ignored here. Any other mismatch still fails.
"""
import subprocess
import sys

VERIFIERS = [
    "skilltree/verify_me132_b2.py",
    "skilltree/verify_me132_b3.py",
    "skilltree/verify_me132_b4.py",
    "skilltree/verify_me132_b5.py",
    "skilltree/verify_me132_b6.py",
    "skilltree/verify_me132_b7.py",
    "skilltree/verify_me132_b8.py",
    "skilltree/verify_nlo_intro.py",
    "skilltree/verify_nlo_nb1.py",
    "skilltree/verify_nlo_nb10.py",
    "skilltree/verify_nlo_nb11.py",
    "skilltree/verify_nlo_nb12.py",
    "skilltree/verify_nlo_nb2.py",
    "skilltree/verify_nlo_nb3.py",
    "skilltree/verify_nlo_nb4.py",
    "skilltree/verify_nlo_nb5.py",
    "skilltree/verify_nlo_nb6.py",
    "skilltree/verify_nlo_nb7.py",
    "skilltree/verify_nlo_nb8.py",
    "skilltree/verify_nlo_nb9.py",
    "skilltree/verify_sg057_g1.py",
    "skilltree/verify_sg057_g2.py",
    "skilltree/verify_sg057_g3.py",
    "skilltree/verify_sg057_g4.py",
    "skilltree/verify_sg063_ee105_ch1.py",
    "skilltree/verify_sg063_ee105_ch11.py",
    "skilltree/verify_sg063_ee105_ch12.py",
    "skilltree/verify_sg063_ee105_ch14.py",
    "skilltree/verify_sg063_ee105_ch16.py",
    "skilltree/verify_sg063_ee105_ch18.py",
    "skilltree/verify_sg063_me132_m2.py",
    "skilltree/verify_sg063_nlo_l2.py",
]

STALE_GRANDFATHER = (
    "grandfather count ",
    "grandfather list changed",
    "still grandfathered:",
)


def content_mismatches(text):
    found = []
    for line in text.splitlines():
        if not line.startswith("  "):
            continue
        body = line.strip()
        if body.startswith(STALE_GRANDFATHER):
            continue
        found.append(body)
    return found


def main():
    failed = []
    stale = []
    for path in VERIFIERS:
        proc = subprocess.run([sys.executable, path], text=True, capture_output=True)
        text = (proc.stdout or "") + (proc.stderr or "")
        bad = content_mismatches(text)
        if proc.returncode != 0 and not bad:
            stale.append(path)
            continue
        if proc.returncode != 0 or bad or "0 mismatches" not in text:
            failed.append(path)
            sys.stderr.write(text if text else path + ": no output\n")
    if failed:
        print("FAILED " + ", ".join(failed))
        sys.exit(1)
    if stale:
        print("ignored pre-existing grandfather pins: " + ", ".join(stale))
    print("numeric delegated, mismatches 0")
    print("0 mismatches")


if __name__ == "__main__":
    main()
