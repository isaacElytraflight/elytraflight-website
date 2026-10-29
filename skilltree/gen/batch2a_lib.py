"""batch2a_lib.py - question-builder for the batch2a skills (ch 3, 5, 6, 7 device physics).
Same schema as qlib.Skill, plus optional figure / figure_alt, LaTeX math in \\( \\) and \\[ \\]."""
import json, math, re

BANK = "/workspace/skilltree/bank"
SKILLS = ['si-props', 'drude', 'intrinsic', 'doping', 'drift', 'diffusion', 'total-current', 'carrier-pot', 'excess-carriers',
          'continuity', 'minority-profile', 'pn-overview', 'depl-approx', 'contact-pot', 'rev-bias', 'mos-struct', 'mos-regions',
          'vt', 'mos-fields', 'mos-cv']

# ---- physical constants (reader conventions, CGS-cm units)
q = 1.602e-19          # C
kTq = 0.026            # V  (reader: kT/q ≈ 26 mV at 300 K)
ni = 1e10              # cm^-3 (reader Eq. 3.27)
eps0 = 8.854e-14       # F/cm
eps_s = 11.7 * eps0    # 1.036e-12 F/cm
eps_ox = 3.9 * eps0    # 3.45e-13 F/cm

def close(a, b, rel=1e-6): return abs(a - b) <= rel * max(1e-300, abs(b))

def g(x, n=3):
    """plain number with n significant digits (no exponent for moderate values)."""
    if x == 0: return "0"
    e = math.floor(math.log10(abs(x)))
    if -3 <= e <= 5:
        d = max(0, n - 1 - e)
        s = f"{x:.{d}f}"
        if "." in s: s = s.rstrip("0").rstrip(".")
        return s
    return sci(x, n)

def sci(x, n=3):
    """LaTeX scientific notation (to be used INSIDE \\( \\)): 1.5\\times10^{16}"""
    if x == 0: return "0"
    e = math.floor(math.log10(abs(x)))
    m = x / 10 ** e
    ms = f"{m:.{n-1}f}".rstrip("0").rstrip(".")
    if ms in ("10",): ms, e = "1", e + 1
    return f"10^{{{e}}}" if ms == "1" else f"{ms}\\times10^{{{e}}}"

def F(template, **kw):
    """Fill <<name>> placeholders (lets us write LaTeX braces freely)."""
    def rep(m):
        k = m.group(1)
        if k not in kw: raise KeyError(k)
        return str(kw[k])
    return re.sub(r"<<(\w+)>>", rep, template)

class Skill:
    def __init__(self, sid):
        self.sid, self.qs, self.rnd, self.qn, self.mcn = sid, [], 1, 0, 0
        self.off = SKILLS.index(sid)
    def round(self, r): self.rnd, self.qn = r, 0
    def _id(self):
        self.qn += 1
        return f"{self.sid}-r{self.rnd}-q{self.qn}"
    def _fig(self, q, figure, alt):
        if figure:
            assert alt, "figure needs alt text"
            q["figure"], q["figure_alt"] = figure, alt
    def mc(self, prompt, correct, wrongs, expl, preview=None, figure=None, alt=None):
        assert len(wrongs) == 3, (self.sid, prompt[:60])
        assert len(set([correct] + list(wrongs))) == 4, ("dup options", self.sid, prompt[:60])
        pos = (self.mcn * 3 + self.off) % 4
        self.mcn += 1
        opts = list(wrongs); opts.insert(pos, correct)
        q = {"id": self._id(), "round": self.rnd, "type": "mc", "prompt": prompt, "options": opts, "correct_index": pos, "explanation": expl}
        self._fig(q, figure, alt)
        if self.rnd == 4: assert preview; q["preview"] = preview
        self.qs.append(q)
    def num(self, prompt, answer, unit, expl, tol=0.02, preview=None, figure=None, alt=None):
        q = {"id": self._id(), "round": self.rnd, "type": "numeric", "prompt": prompt, "answer": float(f"{answer:.6g}"),
             "unit": unit, "tolerance": tol, "explanation": expl}
        self._fig(q, figure, alt)
        if self.rnd == 4: assert preview; q["preview"] = preview
        self.qs.append(q)
    def save(self):
        assert len(self.qs) == 12, (self.sid, len(self.qs))
        with open(f"{BANK}/{self.sid}.json", "w") as f:
            json.dump({"skill_id": self.sid, "version": 1, "questions": self.qs}, f, indent=2, ensure_ascii=False)
