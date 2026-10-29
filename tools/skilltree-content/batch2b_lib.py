"""batch2b helpers: question builder (with figure/figure_alt, LaTeX math) + shared figure builders."""
import json, math, cmath, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from figlib import *   # b2b_* SVG helpers (shared file)

BANK = "/workspace/skilltree/bank"
MINE = ['bias-current','datasheet','fb-errors','fb-impedance','fb-intro','gbw','inverting','loop-gain','noise-dist','offset',
        'opamp-fr','opamp-models','slew','stability','electrostatics','mim-cap','nl-cap','junction-cap','diode-iv','diode-qual','diode-ss']

def close(a, b, rel=1e-6):
    return abs(a - b) <= rel * max(1e-300, abs(b))

def dB(x): return 20 * math.log10(x)

def g(x, n=3):
    return f"{x:.{n}g}"

def tex(x, n=3):
    """number -> LaTeX string with scientific notation when needed (no delimiters)."""
    if x == 0: return "0"
    s = f"{x:.{n}g}"
    if "e" in s:
        m, e = s.split("e")
        return f"{m}\\times10^{{{int(e)}}}"
    return s

def T(_tpl, **kw):
    """template: replace <<key>> by str(value)."""
    for k, v in kw.items():
        _tpl = _tpl.replace(f"<<{k}>>", str(v))
    assert "<<" not in _tpl, _tpl
    return _tpl

class Skill:
    def __init__(self, sid):
        self.sid = sid
        self.qs = []
        self.rnd = 1
        self.qn = 0
        self.mcn = 0
        self.off = MINE.index(sid)
    def round(self, r):
        self.rnd = r; self.qn = 0
    def _id(self):
        self.qn += 1
        return f"{self.sid}-r{self.rnd}-q{self.qn}"
    def _fig(self, q, fig, alt):
        if fig is not None:
            assert alt, "figure needs alt"
            q["figure"] = fig; q["figure_alt"] = alt
    def mc(self, prompt, correct, wrongs, expl, fig=None, alt=None, preview=None):
        assert len(wrongs) == 3, (self.sid, prompt)
        opts_all = [correct] + list(wrongs)
        assert len(set(opts_all)) == 4, ("dup options", self.sid, prompt, opts_all)
        pos = (self.mcn * 3 + self.off) % 4
        self.mcn += 1
        opts = list(wrongs); opts.insert(pos, correct)
        q = {"id": self._id(), "round": self.rnd, "type": "mc", "prompt": prompt,
             "options": opts, "correct_index": pos, "explanation": expl}
        self._fig(q, fig, alt)
        if self.rnd == 4:
            assert preview, "round 4 needs preview"; q["preview"] = preview
        self.qs.append(q)
    def num(self, prompt, answer, unit, expl, tol=0.02, fig=None, alt=None, preview=None):
        q = {"id": self._id(), "round": self.rnd, "type": "numeric", "prompt": prompt,
             "answer": float(f"{answer:.6g}"), "unit": unit, "tolerance": tol, "explanation": expl}
        self._fig(q, fig, alt)
        if self.rnd == 4:
            assert preview, "round 4 needs preview"; q["preview"] = preview
        self.qs.append(q)
    def save(self):
        assert len(self.qs) == 12, (self.sid, len(self.qs))
        data = {"skill_id": self.sid, "version": 1, "questions": self.qs}
        with open(f"{BANK}/{self.sid}.json", "w") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

# ----------------------------------------------------------------- shared figures
def fig_inverting(rin="R₁", rf="R₂", vin="vᵢₙ", vout="vₒᵤₜ", title="Inverting amplifier", extra=""):
    o, nin, pin, out = b2b_opamp(130, 75, 56, 60)
    b = (b2b_text(24, 50, vin, anchor="start") + b2b_circle(30, 60, 3) +
         b2b_wire(33, 60, 45, 60) + b2b_resistor(45, 60, 65, label=rin) +
         b2b_wire(110, 60, 130, 60) + b2b_dot(110, 60) + o +
         b2b_wire(130, 90, 116, 90) + b2b_ground(116, 90) +
         b2b_wire(110, 60, 110, 25, 125, 25) + b2b_resistor(125, 25, 65, label=rf, lpos=(157, 14)) +
         b2b_wire(190, 25, 205, 25, 205, 75) + b2b_wire(186, 75, 240, 75) + b2b_dot(205, 75) +
         b2b_circle(243, 75, 3) + b2b_text(262, 79, vout, anchor="start") + extra)
    return b2b_svg(380, 130, b, title)

def fig_noninverting(r1="R₁", r2="R₂", vin="vᵢₙ", vout="vₒᵤₜ", title="Non-inverting amplifier"):
    o, pin, nin, out = b2b_opamp(130, 75, 56, 60, plus_top=True)
    b = (b2b_text(24, 50, vin, anchor="start") + b2b_circle(30, 60, 3) + b2b_wire(33, 60, 130, 60) + o +
         b2b_wire(130, 90, 112, 90, 112, 135) + b2b_dot(112, 135) +
         b2b_wire(112, 135, 125, 135) + b2b_resistor(125, 135, 65) + b2b_text(157, 125, r2) +
         b2b_wire(190, 135, 205, 135, 205, 75) + b2b_wire(186, 75, 240, 75) + b2b_dot(205, 75) +
         b2b_circle(243, 75, 3) + b2b_text(262, 79, vout, anchor="start") +
         b2b_resistor(112, 135, 50, horiz=False) + b2b_text(124, 164, r1, anchor="start") + b2b_ground(112, 185))
    return b2b_svg(380, 205, b, title)

def fig_follower(vin="vᵢₙ", vout="vₒᵤₜ", title="Unity-gain follower"):
    o, pin, nin, out = b2b_opamp(110, 60, 56, 60, plus_top=True)
    b = (b2b_text(18, 49, vin) + b2b_circle(30, 45, 3) + b2b_wire(33, 45, 110, 45) + o +
         b2b_wire(110, 75, 95, 75, 95, 110, 190, 110, 190, 60) + b2b_wire(166, 60, 225, 60) + b2b_dot(190, 60) +
         b2b_circle(228, 60, 3) + b2b_text(247, 64, vout, anchor="start"))
    return b2b_svg(310, 125, b, title)

def fig_feedback_blocks(g_lab="G", f_lab="f", sin="sᵢₙ", sout="sₒᵤₜ", serr="sₑᵣᵣ", title="Negative feedback loop"):
    b = (b2b_text(18, 54, sin) + b2b_arrow(30, 50, 82, 50) + b2b_sum(92, 50) +
         b2b_arrow(102, 50, 140, 50) + b2b_text(121, 40, serr, size=10) +
         b2b_box(140, 28, 60, 44, g_lab) + b2b_arrow(200, 50, 268, 50) + b2b_text(278, 54, sout, anchor="start") +
         b2b_wire(235, 50, 235, 115, 200, 115) + b2b_dot(235, 50) +
         b2b_box(140, 93, 60, 44, f_lab) +
         b2b_wire(140, 115, 92, 115) + b2b_arrow(92, 115, 92, 62))
    return b2b_svg(370, 150, b, title)

def sci(v):
    k = int(round(math.log10(v)))
    if k == 0: return "1"
    if k == 1: return "10"
    sup = {"0":"⁰","1":"¹","2":"²","3":"³","4":"⁴","5":"⁵","6":"⁶","7":"⁷","8":"⁸","9":"⁹","-":"⁻"}
    return "10" + "".join(sup[c] for c in str(k))

def fig_bode_mag(segs, fmin, fmax, dbmax, width=340, height=190, ylab="|A| (dB)", extra=lambda X, Y: "", title="Bode magnitude (asymptotic)", dbstep=20):
    """segs: list of (f, dB) breakpoints (polyline). freq log axis. returns svg."""
    x0, y0, W, H = 50, height - 36, width - 80, height - 66
    lf0, lf1 = math.log10(fmin), math.log10(fmax)
    X = lambda f: x0 + W * (math.log10(f) - lf0) / (lf1 - lf0)
    Y = lambda d: y0 - H * (d / dbmax)
    b = b2b_axes(x0, y0, W, H, "", ylab) + b2b_text(x0 + W, y0 - 6, "f (Hz)", anchor="end", size=10) + b2b_poly([(X(f), Y(d)) for f, d in segs], sw=2.2)
    for d in range(0, int(dbmax) + 1, dbstep):
        b += b2b_line(x0 - 3, Y(d), x0 + 3, Y(d)) + b2b_text(x0 - 6, Y(d) + 3, str(d), anchor="end", size=10)
    for k in range(int(math.ceil(lf0)), int(math.floor(lf1)) + 1):
        tx = X(10 ** k)
        b += b2b_line(tx, y0 - 3, tx, y0 + 3) + b2b_text(tx, y0 + 15, sci(10 ** k), size=10)
    b += b2b_line(x0, Y(0), x0 + W, Y(0), dash=True, op=0.5)
    b += extra(X, Y)
    return b2b_svg(width, height, b, title)

def fig_vcvs(rs=True, rl=True, labels=("Rₛ","R_in","R_out","Rₗ"), title="Op-amp VCVS model"):
    """Source Rs -> [Rin | Avin VCVS | Rout] -> RL. Simple one-line model."""
    b = ""
    b += b2b_circle(20, 40, 3) + b2b_text(14, 25, "vₛ") + b2b_wire(23, 40, 40, 40)
    if rs: b += b2b_resistor(40, 40, 50, label=labels[0])
    else: b += b2b_wire(40, 40, 90, 40)
    b += b2b_wire(90, 40, 100, 40, 100, 50) + b2b_dot(100, 40)
    b += b2b_resistor(100, 50, 60, horiz=False, label=labels[1], lpos=(108, 84)) + b2b_wire(100, 110, 100, 130) + b2b_ground(100, 130)
    b += b2b_text(100, 38, "v_in", size=10) if False else ""
    # dependent source
    b += b2b_wire(100, 40, 125, 40) + b2b_wire(125, 40, 125, 40)
    # VCVS: diamond-like circle
    b += b2b_circle(180, 85, 22) + b2b_text(180, 82, "A·v_in", size=10) + b2b_text(180, 94, "+  \u2212", size=10)
    b += b2b_wire(180, 63, 180, 40) + b2b_resistor(180, 40, 50, label=labels[2]) + b2b_wire(180, 107, 180, 130) + b2b_ground(180, 130)
    b += b2b_wire(230, 40, 255, 40, 255, 50) + b2b_dot(255, 40)
    if rl:
        b += b2b_resistor(255, 50, 60, horiz=False, label=labels[3], lpos=(263, 84)) + b2b_wire(255, 110, 255, 130) + b2b_ground(255, 130)
    b += b2b_wire(255, 40, 285, 40) + b2b_circle(288, 40, 3) + b2b_text(300, 44, "v_out", anchor="start")
    return b2b_svg(350, 160, b, title)
