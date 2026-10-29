import json, math, cmath, os
import numpy as np

BANK = "/workspace/skilltree/bank"
ORDER = ['lti-def','rc-lpf','cx-exp','sinusoid-resp','impulse-conv','step-resp','freq-char','tf','phasors','direct-h','pole-zero','rlc','bode','ac-power']

def close(a, b, rel=1e-6):
    return abs(a - b) <= rel * max(1e-12, abs(b))

def g(x, n=4):
    """format number with n significant digits, no trailing junk"""
    s = f"{x:.{n}g}"
    return s

class Skill:
    def __init__(self, sid):
        self.sid = sid
        self.qs = []
        self.rnd = 1
        self.qn = 0
        self.mcn = 0
        self.off = ORDER.index(sid)
    def round(self, r):
        self.rnd = r
        self.qn = 0
    def _id(self):
        self.qn += 1
        return f"{self.sid}-r{self.rnd}-q{self.qn}"
    def mc(self, prompt, correct, wrongs, expl, preview=None):
        assert len(wrongs) == 3, (self.sid, prompt)
        opts_all = [correct] + list(wrongs)
        assert len(set(opts_all)) == 4, ("dup options", self.sid, prompt, opts_all)
        pos = (self.mcn * 3 + self.off) % 4   # cycles through all 4 positions
        self.mcn += 1
        opts = list(wrongs)
        opts.insert(pos, correct)
        q = {"id": self._id(), "round": self.rnd, "type": "mc", "prompt": prompt,
             "options": opts, "correct_index": pos, "explanation": expl}
        if self.rnd == 4:
            assert preview, "round 4 needs preview"
            q["preview"] = preview
        self.qs.append(q)
    def num(self, prompt, answer, unit, expl, tol=0.02, preview=None):
        q = {"id": self._id(), "round": self.rnd, "type": "numeric", "prompt": prompt,
             "answer": float(f"{answer:.6g}"), "unit": unit, "tolerance": tol, "explanation": expl}
        if self.rnd == 4:
            assert preview, "round 4 needs preview"
            q["preview"] = preview
        self.qs.append(q)
    def save(self):
        assert len(self.qs) == 12, (self.sid, len(self.qs))
        # retrofit: LaTeX \( \) math + figures by question id (ids/answers untouched)
        from o_latex import latexify
        from o_figs import MAP as FIGS
        for q in self.qs:
            for k in ("prompt", "explanation", "preview"):
                if q.get(k): q[k] = latexify(q[k])
            if "options" in q: q["options"] = [latexify(o) for o in q["options"]]
            if q["id"] in FIGS:
                q["figure"], q["figure_alt"] = FIGS[q["id"]]
        data = {"skill_id": self.sid, "version": 1, "questions": self.qs}
        with open(f"{BANK}/{self.sid}.json", "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

def brentq(f, a, b, tol=1e-12):
    """bisection root finder (stand-in for scipy.optimize.brentq)"""
    fa, fb = f(a), f(b)
    assert fa*fb < 0, "no sign change"
    for _ in range(200):
        m = 0.5*(a+b); fm = f(m)
        if fa*fm <= 0: b, fb = m, fm
        else: a, fa = m, fm
        if abs(b-a) < tol*max(1, abs(a)): break
    return 0.5*(a+b)
