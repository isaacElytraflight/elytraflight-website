"""Shared bank and explainer writer for ME 132 batches.

B2, B3, and B4 used to paste this class. B1 keeps its own copy because its
word counter strips math differently. Do not import a verifier from here.
"""
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK = os.path.join(ROOT, "skilltree", "bank")
EXP = os.path.join(ROOT, "skilltree", "explainers")


def g(x):
    return float(f"{x:.6g}")


class Bank:
    def __init__(self, sid):
        self.sid = sid
        self.qs = []
        self.n = {1: 0, 2: 0, 3: 0, 4: 0}

    def q(self, rnd, kind, prompt, explanation, fig=None, alt=None, preview=None, version=1, **kw):
        self.n[rnd] += 1
        item = {
            "id": f"{self.sid}-r{rnd}-q{self.n[rnd]}",
            "round": rnd,
            "type": kind,
            "prompt": prompt,
            "explanation": explanation,
        }
        if fig is not None:
            item["figure"] = fig
            item["figure_alt"] = alt
        if rnd == 4:
            item["preview"] = preview
        elif preview:
            raise SystemExit("preview only in round 4")
        item.update(kw)
        item["version"] = version
        self.qs.append(item)

    def mc(self, rnd, prompt, options, correct, explanation, fig=None, alt=None, preview=None, version=1):
        self.q(rnd, "mc", prompt, explanation, fig, alt, preview, version,
               options=options, correct_index=correct)

    def num(self, rnd, prompt, answer, unit, explanation, fig=None, alt=None, preview=None, version=1):
        self.q(rnd, "numeric", prompt, explanation, fig, alt, preview, version,
               answer=g(answer), unit=unit, tolerance=0.02)

    def save(self):
        assert self.n == {1: 3, 2: 3, 3: 3, 4: 3}, (self.sid, self.n)
        path = os.path.join(BANK, f"{self.sid}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"skill_id": self.sid, "version": 1, "questions": self.qs},
                      f, indent=2, ensure_ascii=False)
            f.write("\n")


def save_explainer(sid, title, sections, version=1):
    path = os.path.join(EXP, f"{sid}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"id": sid, "title": title, "version": version, "sections": sections},
                  f, indent=2, ensure_ascii=False)
        f.write("\n")


def words(sections):
    text = " ".join(s["body_md"] for s in sections)
    text = re.sub(r"<svg[\s\S]*?</svg>", " ", text)
    text = re.sub(r"\\\(|\\\)|\\\[|\\\]", " ", text)
    text = re.sub(r"\\[a-zA-Z]+", " ", text)
    return len(re.findall(r"[A-Za-z0-9']+", text))
