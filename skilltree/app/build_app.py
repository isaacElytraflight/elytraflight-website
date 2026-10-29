#!/usr/bin/env python3
"""Build the single-file Skillgrove demo.

Usage:  python3 /workspace/skilltree/app/build_app.py
Reads   ../ee105_skills_draft.json and ../bank/*.json, plus template.html
Writes  skilltree.html (self-contained; data inlined; works from file://)
"""
import json, glob, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SKILLS = os.path.join(ROOT, "ee105_skills_draft.json")
BANK = os.path.join(ROOT, "bank", "*.json")
TEMPLATE = os.path.join(HERE, "template.html")
OUT = os.path.join(HERE, "skilltree.html")
PLACEHOLDER = "/*__SKILLTREE_DATA__*/null"


def main():
    d = json.load(open(SKILLS, encoding="utf-8"))
    skills = d["skills"]
    ids = [s["id"] for s in skills]
    assert len(ids) == len(set(ids)), "duplicate skill ids"
    idset = set(ids)
    for s in skills:
        for p in s["prereqs"]:
            assert p in idset, f"{s['id']}: unknown prereq {p}"
    bank = {}
    seen_q = set()
    for f in sorted(glob.glob(BANK)):
        b = json.load(open(f, encoding="utf-8"))
        sid = b["skill_id"]
        if sid not in idset:
            print(f"warning: bank {f} for unknown skill {sid}; skipped", file=sys.stderr)
            continue
        qs = []
        for q in b["questions"]:
            assert q["id"] not in seen_q, f"duplicate question id {q['id']}"
            seen_q.add(q["id"])
            assert q["type"] in ("mc", "numeric"), q["id"]
            assert q["round"] in (1, 2, 3, 4), q["id"]
            if q["type"] == "mc":
                assert len(q["options"]) >= 2 and 0 <= q["correct_index"] < len(q["options"]), q["id"]
            else:
                assert isinstance(q["answer"], (int, float)), q["id"]
            for p in q.get("preview", []) or []:
                assert p in idset, f"{q['id']}: preview {p} unknown"
            keep = {k: q[k] for k in ("id", "round", "type", "prompt", "options", "correct_index",
                                      "answer", "unit", "tolerance", "explanation", "preview", "figure", "figure_alt") if k in q}
            qs.append(keep)
        bank[sid] = {"version": b.get("version", 1), "questions": qs}
    data = {
        "course": d.get("course", "EE 105"),
        "source": d.get("source", ""),
        "version": d.get("version"),
        "chapters": d["chapters"],
        "skills": [{k: s[k] for k in ("id", "name", "chapter", "reader_section", "prereqs")} for s in skills],
        "bank": bank,
    }
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    blob = blob.replace("</", "<\\/").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    tpl = open(TEMPLATE, encoding="utf-8").read()
    assert tpl.count(PLACEHOLDER) == 1, "placeholder missing in template"
    html = tpl.replace(PLACEHOLDER, blob)
    open(OUT, "w", encoding="utf-8").write(html)
    nq = sum(len(b["questions"]) for b in bank.values())
    print(f"wrote {OUT}: {len(html)/1024:.0f} KB, {len(skills)} skills, {len(bank)} with banks, {nq} questions")


if __name__ == "__main__":
    main()
