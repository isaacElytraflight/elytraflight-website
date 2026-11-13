#!/usr/bin/env python3
"""Fail when learner-facing Skill Tree content names a source.

Scans question banks, explainers, skill titles and summaries, chapter and box
titles, the built public copies of those files, and the learner UI
(public/skilltree/skilltree.js and index.html).

University names and course numbers may appear only as an exact course
selector label, and only in a collections tab_title. Those labels are listed
in the allowlist. The gate still fails when the same words appear anywhere
else, and a professor, textbook, reader, week, or lecture still fails inside
a selector label.

Authoring metadata is not learner-facing: sources arrays, ids, prerequisites,
and the retired bank. Generator scripts are not scanned; the JSON they emit is.

  python3 tools/skilltree-content/reference_gate.py

Exceptions live in reference_allowlist.txt next to this file.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ALLOW = os.path.join(os.path.dirname(__file__), "reference_allowlist.txt")

# Keys that are not shown to a learner. tab_title is shown, and is scanned.
SKIP_KEYS = {
    "answer",
    "children",
    "color_index",
    "correct_index",
    "correct_indices",
    "depends_on",
    "id",
    "kind",
    "owns",
    "prereqs",
    "preview",
    "round",
    "skill_id",
    "skills",
    "sources",
    "status",
    "tolerance",
    "type",
    "version",
}

PATTERNS = [
    ("reader", re.compile(r"\breaders?\b", re.I)),
    ("textbook", re.compile(r"\btextbooks?\b|\bthe book\b", re.I)),
    ("lecture", re.compile(r"\blectures?\s+\d+\b|\blecture notes\b|\bin lecture\b", re.I)),
    # A bare "slides" is the motion verb ("a mass slides"). Lecture slides are a
    # numbered slide or one of the phrases below.
    ("slides", re.compile(
        r"\b(?:lecture slides|slide deck|the slides|on the slides|from the slides)\b|\bslides?\s+\d+\b",
        re.I,
    )),
    ("week", re.compile(r"\bweeks?\s+\d+\b", re.I)),
    ("chapter_num", re.compile(r"\bchapters?\s+\d+\b", re.I)),
    ("section_num", re.compile(
        r"(?<![-A-Za-z])sections?\s+\d+(?:\.\d+)*\b|\bsec\.\s*\d|\bfig\.\s*\d|\beq\.\s*\d",
        re.I,
    )),
    ("homework", re.compile(r"\b(?:homework|discussion)\s*#?\s*\d+\b|\bhw\s*#?\s*\d+\b", re.I)),
    ("professor", re.compile(r"\b(?:professor|instructor|lecturer)\b", re.I)),
    ("university", re.compile(r"\b(?:berkeley|stanford|caltech|ucla|graz|princeton)\b|\bmit\b", re.I)),
    ("course_code", re.compile(r"\b(?:EECS|EE|ME|CS|PHYSICS|MATH)\s*\d{2,3}[A-Za-z]?\b")),
    ("author", re.compile(r"\b(?:Niknejad|Sedra|Åström|Astrom)\b")),
    ("further_reading", re.compile(r"\bfurther reading\b", re.I)),
]


def load_allow():
    """Path rules, plus the exact course-selector labels (pointer column "=")."""
    rules = []
    labels = set()
    with open(ALLOW, encoding="utf-8") as f:
        for line in f:
            raw = line.strip()
            if not raw or raw.startswith("#"):
                continue
            parts = raw.split("\t")
            if len(parts) < 3:
                raise SystemExit("bad allowlist line: " + raw)
            if parts[1] == "=":
                labels.add(parts[2])
                continue
            rules.append((parts[0], parts[1], parts[2]))
    return rules, labels


def allowed(rules, path, pointer):
    rel = os.path.relpath(path, ROOT)
    for rule_path, rule_ptr, _reason in rules:
        if rel == rule_path or rel.endswith("/" + rule_path) or path.endswith(rule_path):
            if rule_ptr == "*" or pointer == rule_ptr or pointer.startswith(rule_ptr + "/"):
                return True
    return False


def selector_label(pointer, value, labels):
    """University and course-number hits are waived only for an exact tab_title."""
    return str(pointer).endswith("/tab_title") and value in labels


def walk(node, pointer, out, key=None):
    if key in SKIP_KEYS:
        return
    if key == "reader_section":
        out.append((pointer or "/", "reader_section", str(node)))
        return
    if isinstance(node, dict):
        for k, v in node.items():
            child = f"{pointer}/{k}" if pointer else "/" + k
            walk(v, child, out, k)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{pointer}/{i}", out, key)
    elif isinstance(node, str) and node.strip():
        out.append((pointer or "/", None, node))


def json_strings(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    found = []
    walk(data, "", found)
    return found


def js_literals(text):
    """String literals in source order. An apostrophe inside double quotes stays there."""
    out = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c == "/" and i + 1 < n and text[i + 1] == "/":
            i = text.find("\n", i)
            if i < 0:
                break
            continue
        if c == "/" and i + 1 < n and text[i + 1] == "*":
            end = text.find("*/", i + 2)
            i = n if end < 0 else end + 2
            continue
        if c in "'\"`":
            raw, i = read_js_string(text, i)
            if raw is not None:
                out.append(raw)
            continue
        i += 1
    return out


def read_js_string(text, i):
    quote = text[i]
    j, n = i + 1, len(text)
    while j < n:
        c = text[j]
        if c == "\\":
            j += 2
            continue
        if quote == "`" and c == "$" and j + 1 < n and text[j + 1] == "{":
            j = skip_js_expr(text, j + 2)
            continue
        if c == quote:
            return text[i + 1:j], j + 1
        j += 1
    return None, i + 1


def skip_js_expr(text, i):
    depth = 1
    n = len(text)
    while i < n and depth:
        c = text[i]
        if c in "'\"`":
            _, i = read_js_string(text, i)
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    return i


def ui_strings(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    found = []
    for i, raw in enumerate(js_literals(text)):
        # The collections kind "textbook" is an internal id, not a sentence about a book.
        if raw == "textbook":
            continue
        if raw.strip():
            found.append((f"/literal/{i}", None, raw))
    return found


def scan_text(path, items, rules, hits, labels=()):
    for pointer, forced, value in items:
        if allowed(rules, path, pointer):
            continue
        if forced:
            hits.append((path, pointer, forced, value[:180].replace("\n", " ")))
            continue
        waive = selector_label(pointer, value, labels)
        for name, cre in PATTERNS:
            if waive and name in ("university", "course_code"):
                continue
            m = cre.search(value)
            if m:
                start = max(0, m.start() - 40)
                snippet = value[start:m.end() + 40].replace("\n", " ")
                hits.append((path, pointer, name, snippet))


def targets():
    paths = []
    bank = os.path.join(ROOT, "skilltree", "bank")
    expl = os.path.join(ROOT, "skilltree", "explainers")
    paths.extend(sorted(glob.glob(os.path.join(bank, "*.json"))))
    paths.extend(sorted(glob.glob(os.path.join(expl, "*.json"))))
    paths.append(os.path.join(ROOT, "skilltree", "collections.json"))
    paths.append(os.path.join(ROOT, "skilltree", "ee105_skills_draft.json"))
    public = os.path.join(ROOT, "public", "skilltree")
    for pattern in ("skills.*.json", "collections.*.json", "banks/*.json", "explainers/*.json"):
        paths.extend(sorted(glob.glob(os.path.join(public, pattern))))
    paths.append(os.path.join(public, "skilltree.js"))
    paths.append(os.path.join(public, "index.html"))
    return [p for p in paths if os.path.isfile(p)]


def self_check(rules, labels):
    """The four selector labels pass. The same words fail outside tab_title."""
    ee = "Microelectronic Devices and Circuits (Berkeley EE 105)"
    me = "Dynamic Systems and Feedback (Berkeley ME 132)"
    generic = "Feedback Systems (Generic)"
    nlo = "Nonlinear Optimization (TU Graz)"
    samples = [
        ("/boxes/0/tab_title", ee, False),
        ("/boxes/1/tab_title", me, False),
        ("/boxes/2/tab_title", generic, False),
        ("/boxes/3/tab_title", nlo, False),
        ("/boxes/3/tab_title", "EECS 127", True),
        ("/boxes/0/title", ee, True),
        ("/boxes/1/title", "A course at Berkeley", True),
        ("/skills/0/summary", "See EE 105 for the diode equation.", True),
        ("/boxes/0/tab_title", ee + " from the professor", True),
        ("/boxes/3/title", "Nonlinear Optimization (TU Graz)", True),
    ]
    bad = []
    for pointer, value, expect_hit in samples:
        found = []
        scan_text("skilltree/collections.json", [(pointer, None, value)], rules, found, labels)
        if bool(found) != expect_hit:
            bad.append((pointer, value, expect_hit, found[:2]))
    missing = [label for label in (ee, me, generic, nlo) if label not in labels]
    if missing or bad:
        print("FAILED reference gate self-check")
        for label in missing:
            print(f"  allowlist missing: {label}")
        for row in bad:
            print(f"  {row}")
        return False
    return True


def main():
    rules, labels = load_allow()
    if not self_check(rules, labels):
        return 1
    hits = []
    for path in targets():
        if path.endswith(".json"):
            scan_text(path, json_strings(path), rules, hits, labels)
        else:
            scan_text(path, ui_strings(path), rules, hits, labels)
    if hits:
        print(f"FAILED reference gate: {len(hits)} hit(s)")
        for path, pointer, name, snippet in hits[:50]:
            rel = os.path.relpath(path, ROOT)
            print(f"  {name}: {rel} {pointer}: {snippet}")
        if len(hits) > 50:
            print(f"  ... {len(hits) - 50} more")
        return 1
    print("OK: reference gate, 0 hits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
