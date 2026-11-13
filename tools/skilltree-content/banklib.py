"""Shared bank and explainer writer.

B2 and later batches use this class. B1 keeps its own copy because its word
counter strips math differently, and copies these methods onto that class.
Do not import a verifier from here.

Deep types (symbolic, order, error, multi) are written with sym, order,
find_error, and multi. A bank needs deep_quota(n) of them, at least 25%
rounded up. Banks listed in skilltree/deep_quota_grandfather.json are the
legacy set pending SG-063.
"""
import json
import os
import re

DEEP_TYPES = ("symbolic", "order", "error", "multi")


def deep_quota(n_questions):
    """Minimum deep-type questions. At least 25% of n, rounded up (3 per 12)."""
    n = int(n_questions)
    if n <= 0:
        return 0
    return (3 * n + 11) // 12


def variable_specs(variables):
    """Normalize {name: (min, max)} or a list of {name, min, max}."""
    if isinstance(variables, dict):
        return [{"name": str(name), "min": float(bounds[0]), "max": float(bounds[1])}
                for name, bounds in variables.items()]
    return list(variables)

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

    def sym(self, rnd, prompt, answer, variables, explanation, alternates=None, tolerance=1e-3,
            fig=None, alt=None, preview=None, version=1):
        """Symbolic answer. variables is {name: (min, max)}. alternates are equivalent forms."""
        kw = {
            "answer": answer,
            "variables": variable_specs(variables),
            "tolerance": float(tolerance),
        }
        if alternates:
            kw["alternates"] = list(alternates)
        self.q(rnd, "symbolic", prompt, explanation, fig, alt, preview, version, **kw)

    def order(self, rnd, prompt, steps, explanation, fig=None, alt=None, preview=None, version=1):
        """steps is the correct order. The quiz shuffles them."""
        self.q(rnd, "order", prompt, explanation, fig, alt, preview, version, steps=list(steps))

    def find_error(self, rnd, prompt, steps, flaw, explanation, reasons=None, correct_reason=None,
                   fig=None, alt=None, preview=None, version=1):
        """steps in reading order. flaw is the 0-based index of the one wrong step.

        reasons is optional. When it is set, correct_reason is the index of the right reason.
        """
        kw = {"steps": list(steps), "flaw_index": int(flaw)}
        if reasons is not None:
            if correct_reason is None:
                raise SystemExit("find_error with reasons needs correct_reason")
            kw["reasons"] = list(reasons)
            kw["correct_reason"] = int(correct_reason)
        elif correct_reason is not None:
            raise SystemExit("correct_reason without reasons")
        self.q(rnd, "error", prompt, explanation, fig, alt, preview, version, **kw)

    def multi(self, rnd, prompt, options, correct, explanation, fig=None, alt=None, preview=None, version=1):
        """correct is every correct index. Grading is all-or-nothing."""
        self.q(rnd, "multi", prompt, explanation, fig, alt, preview, version,
               options=list(options), correct_indices=[int(i) for i in correct])

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
