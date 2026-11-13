#!/usr/bin/env python3
"""Fail when a question bank is below the 25% deep-type quota.

A bank of n questions needs at least ceil(3n/12) questions whose type is
symbolic, order, error, or multi. That is 25% rounded up: 3 of 12. Those
types are the ones newer batches use for a justified step, a flaw, a
counterexample, a trace, or a multi-step application.

Banks listed in skilltree/deep_quota_grandfather.json were written before
the quota. They stay exempt until SG-063 rebuilds them. Do not add ids.
Wording-only edits do not take a bank off that list.

  python3 tools/skilltree-content/deep_quota_gate.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SKILLTREE = os.path.join(ROOT, "skilltree")
if SKILLTREE not in sys.path:
    sys.path.insert(0, SKILLTREE)

from validator_domain import deep_quota_warnings  # noqa: E402


def main():
    import json
    path = os.path.join(SKILLTREE, "deep_quota_grandfather.json")
    with open(path, encoding="utf-8") as f:
        grandfather = set(json.load(f)["skills"])
    warns = deep_quota_warnings(os.path.join(SKILLTREE, "bank"), grandfather)
    if warns:
        print(f"FAILED deep-quota gate: {len(warns)} bank(s) under 25%")
        for msg in warns:
            print(" ", msg)
        return 1
    print(f"OK: deep-quota gate, 0 banks under 25% ({len(grandfather)} legacy banks pending SG-063)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
