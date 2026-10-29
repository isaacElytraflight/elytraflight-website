"""o_figs: SVG figures for the ORIGINAL 14 banks (circuit schematics, waveforms, Bode sketches,
pole-zero plots, phasor diagrams, block diagrams). Prefix o_. Reuses figlib (b2b_*), batch2a_fig.plot and
batch2b_lib.fig_bode_mag. Attached by question id in qlib.Skill.save() (question text/answers untouched).
All output: inline SVG with viewBox, currentColor strokes/text, no scripts/links/images."""
import math
from figlib import (b2b_svg, b2b_line, b2b_poly, b2b_path, b2b_text, b2b_rect, b2b_circle, b2b_dot, b2b_arrow,
                    b2b_resistor, b2b_capacitor, b2b_vsource, b2b_isource, b2b_ground, b2b_box, b2b_sum, b2b_wire)
import batch2a_fig as FG
from batch2b_lib import fig_bode_mag, fig_feedback_blocks

def _n(x): return f"{x:.1f}".rstrip("0").rstrip(".")

# ---------------------------------------------------------------- elements
def o_inductor(x, y, L=60, horiz=True, label=None):
    k, r = 4, 5.0
    lead = (L - 2 * r * k) / 2
    if horiz:
        d = f"M{_n(x)},{_n(y)} h{_n(lead)}" + "".join(f" a{r},{r} 0 0 1 {2*r},0" for _ in range(k)) + f" h{_n(lead)}"
        out = b2b_path(d)
        if label: out += b2b_text(x + L / 2, y - 12, label)
    else:
        d = f"M{_n(x)},{_n(y)} v{_n(lead)}" + "".join(f" a{r},{r} 0 0 1 0,{2*r}" for _ in range(k)) + f" v{_n(lead)}"
        out = b2b_path(d)
        if label: out += b2b_text(x + 14, y + L / 2 + 4, label, anchor="start")
    return out

def _elem(kind, x, y, L, horiz, label):
    if kind == 'R': return b2b_resistor(x, y, L, horiz, label)
    if kind == 'C': return b2b_capacitor(x, y, L, horiz, label)
    if kind == 'L': return o_inductor(x, y, L, horiz, label)
    if kind == 'D':
        from figlib import b2b_diode
        return b2b_diode(x, y, L, horiz, label)
    if kind == 'W':
        return b2b_line(x, y, x + L, y) if horiz else b2b_line(x, y, x, y + L)
    if kind == 'LCpar':   # horizontal only: L on top branch, C on bottom branch
        m = 22
        return (b2b_line(x, y, x + 8, y) + b2b_line(x + 8, y - m, x + 8, y + m) + b2b_line(x + L - 8, y - m, x + L - 8, y + m) +
                o_inductor(x + 8, y - m, L - 16, True, None) + b2b_capacitor(x + 8, y + m, L - 16, True, None) + b2b_line(x + L - 8, y, x + L, y) +
                b2b_text(x + L / 2, y - m - 10, (label or "L ∥ C").split('|')[0]) + b2b_text(x + L / 2, y + m + 22, "C", size=11))
    raise ValueError(kind)

def o_circuit(stages, vs="vₛ", out="vₒ", title="Circuit", isrc=False, width=None, top=46, bot=126):
    """stages: list of (series, shunts). series: (kind,label) or None; shunts: list of (kind,label)."""
    b = ""
    x0 = 46 + max(0, int(6.5 * len(vs)) - 22)
    b += (b2b_isource(x0, top, bot - top, vs, lside="left") if isrc else b2b_vsource(x0, top, bot - top, vs)) + b2b_ground(x0, bot)
    x = x0
    b += b2b_line(x, top, x + 18, top); x += 18
    for ser, shunts in stages:
        if ser:
            L = 84 if ser[0] == 'LCpar' else 70
            b += _elem(ser[0], x, top, L, True, ser[1]); x += L
        if shunts:
            for k, (kind, lab) in enumerate(shunts):
                gap = 22 if k == 0 else max(34, int(6.5 * len(shunts[k - 1][1] or "")) + 26)
                b += b2b_line(x, top, x + gap, top); x += gap
                b += b2b_dot(x, top) + _elem(kind, x, top + 10, bot - top - 20, False, lab) + b2b_line(x, top, x, top + 10) + b2b_line(x, bot - 10, x, bot) + b2b_ground(x, bot)
        b += b2b_line(x, top, x + 14, top); x += 14
    b += b2b_line(x, top, x + 16, top); x += 16
    b += b2b_circle(x + 3, top, 3) + b2b_text(x + 10, top + 4, out, anchor="start")
    if out:
        b += b2b_text(x + 3, top + 22, "+", size=11) + b2b_text(x + 3, bot - 2, "−", size=11)
    if shunts_last := (stages[-1][1] or []):
        pass
    W = width or int(x + 30 + 7 * len(out or ""))
    return b2b_svg(W, bot + 22, b, title)

def o_rc(vs="vₛ", out="vₒ", rl="R", cl="C", title="RC low-pass filter", load=None, hp=False):
    if hp:
        return o_circuit([(('C', cl), [('R', rl)] + ([('R', load)] if load else []))], vs, out, title)
    return o_circuit([(('R', rl), [('C', cl)] + ([('R', load)] if load else []))], vs, out, title)

# ---------------------------------------------------------------- plots
P = FG.plot
def o_wave(fns, xlim, ylim, xlabel="t", ylabel="", **kw):
    return P([dict(fn=f, **({} if not isinstance(f, tuple) else {})) if callable(f) else f for f in fns], xlim, ylim, xlabel, ylabel, **kw)

def o_stems(vals, labels, ylabel="h", xlabel="t (ms)", title="Samples", w=300, h=170, ymax=None):
    b = ""
    x0, y0, W, H = 40, h - 34, w - 70, h - 64
    ymax = ymax or max(abs(v) for v in vals) or 1
    ymin = min(0, min(vals))
    sy = H / (ymax - ymin)
    yz = y0 - (-ymin) * sy
    b += b2b_arrow(x0, yz, x0 + W + 10, yz) + b2b_arrow(x0, y0 + 4, x0, y0 - H - 10)
    b += b2b_text(x0 + W + 10, yz - 6, xlabel, anchor="end", size=10) + b2b_text(x0 + 6, y0 - H - 12, ylabel, anchor="start", size=11)
    n = len(vals)
    for i, (v, lab) in enumerate(zip(vals, labels)):
        x = x0 + 20 + i * (W - 50) / max(1, n - 1) if n > 1 else x0 + W / 2
        y = yz - v * sy
        b += b2b_line(x, yz, x, y, sw=2) + b2b_circle(x, y, 3.5, True) + b2b_text(x, yz + 15, lab, size=10)
        b += b2b_text(x + 9, y - 3 if v >= 0 else y + 12, f"{v:g}", anchor="start", size=10)
    return b2b_svg(w, h, b, title)

def o_splane(poles=(), zeros=(), xr=(-3, 1), yr=(-2, 2), title="s-plane", w=260, h=200, labels=True, ticks=()):
    b = ""
    x0, y0, W, H = 20, 16, w - 40, h - 40
    X = lambda s: x0 + (s - xr[0]) / (xr[1] - xr[0]) * W
    Y = lambda s: y0 + H - (s - yr[0]) / (yr[1] - yr[0]) * H
    b += b2b_arrow(x0, Y(0), x0 + W + 8, Y(0)) + b2b_arrow(X(0), y0 + H + 6, X(0), y0 - 6)
    b += b2b_text(x0 + W + 8, Y(0) + 16, "σ", anchor="end", size=12) + b2b_text(X(0) + 6, y0 + 2, "jω", anchor="start", size=12)
    for v, lab in ticks:
        b += b2b_line(X(v), Y(0) - 3, X(v), Y(0) + 3) + b2b_text(X(v), Y(0) + 15, lab, size=9)
    for (re_, im) in poles:
        x, y = X(re_), Y(im); d = 6
        b += b2b_line(x - d, y - d, x + d, y + d, sw=2.2) + b2b_line(x - d, y + d, x + d, y - d, sw=2.2)
    for (re_, im) in zeros:
        b += b2b_circle(X(re_), Y(im), 6) 
    if labels:
        b += b2b_text(w - 6, h - 4, "× pole   ○ zero", anchor="end", size=9)
    return b2b_svg(w, h, b, title)

def o_phasors(vecs, R=1.0, title="Phasor diagram", w=240, h=220, axes_labels=("Re", "Im")):
    """vecs: list of (mag, angle_deg, label, dashed)"""
    b = ""
    cx, cy, r = w / 2, h / 2, min(w, h) / 2 - 26
    b += b2b_arrow(14, cy, w - 10, cy) + b2b_arrow(cx, h - 10, cx, 10)
    b += b2b_text(w - 10, cy + 16, axes_labels[0], anchor="end", size=10) + b2b_text(cx + 6, 18, axes_labels[1], anchor="start", size=10)
    for v in vecs:
        mag, ang, lab = v[0], v[1], v[2]
        dash = len(v) > 3 and v[3]
        a = math.radians(ang)
        x2, y2 = cx + r * mag / R * math.cos(a), cy - r * mag / R * math.sin(a)
        if dash:
            b += b2b_line(cx, cy, x2, y2, dash=True) + b2b_circle(x2, y2, 2.5, True)
        else:
            b += b2b_arrow(cx, cy, x2, y2, 8)
        lx, ly = x2 + 10 * math.cos(a), y2 - 10 * math.sin(a)
        anc = "start" if math.cos(a) >= -0.2 else "end"
        if anc == "start" and lx + 6.5 * len(lab) > w - 4:
            anc, lx, ly = "end", min(lx, w - 4), ly + (14 if math.sin(a) <= 0 else -12)
        b += b2b_text(lx, ly + 4, lab, anchor=anc, size=11)
    return b2b_svg(w, h, b, title)

def o_blocks(items, title="Block diagram", w=None, h=70):
    """items: alternating signal labels and box labels: ['x(t)', 'h(t)', 'y(t)'] or with more boxes."""
    b = ""
    x, y = 10, h / 2
    bw = 76
    for i, it in enumerate(items):
        if i % 2 == 0:
            if i == 0:
                b += b2b_text(x, y - 8, it, anchor="start", size=11)
                b += b2b_arrow(x, y, x + 56, y); x += 56
            else:
                b += b2b_arrow(x, y, x + 50, y) + b2b_text(x + 54, y + 4, it, anchor="start", size=11); x += 50
                if i < len(items) - 1: x -= 50
        else:
            b += b2b_box(x, y - 18, bw, 36, it); x += bw
            if i + 1 < len(items) - 1:
                b += b2b_arrow(x, y, x + 40, y) + b2b_text(x + 20, y - 8, items[i + 1], size=10); x += 40
    W = w or int(x + 60)
    # fix: intermediate signal arrows already drawn; skip their duplicate end arrows
    return b2b_svg(W, h, b, title)

def o_chain(boxes, sin="x(t)", sout="y(t)", mids=None, title="Block diagram", h=70):
    b = ""; y = h / 2; x = 10
    la = max(50, int(6.5 * len(sin)) + 14)
    b += b2b_text(x, y - 8, sin, anchor="start", size=11) + b2b_arrow(x, y, x + la, y); x += la
    for k, lab in enumerate(boxes):
        bw = max(60, 9 * len(lab) + 18)
        b += b2b_box(x, y - 18, bw, 36, lab); x += bw
        if k < len(boxes) - 1:
            b += b2b_arrow(x, y, x + 46, y)
            if mids: b += b2b_text(x + 23, y - 8, mids[k], size=10)
            x += 46
    b += b2b_arrow(x, y, x + 46, y) + b2b_text(x + 50, y + 4, sout, anchor="start", size=11); x += 46
    return b2b_svg(int(x + 12 + 8 * len(sout)), h, b, title)

def o_bode(segs, fmin, fmax, dbmax, xlab="ω (rad/s)", ylab="|H| (dB)", title="Bode magnitude (asymptotic)", dbmin=None, marks=(), w=340, h=200, exact=None):
    """generic asymptotic Bode sketch: segs = [(w, dB), ...] polyline; dbmin may be negative."""
    dbmin = 0 if dbmin is None else dbmin
    x0, y0, W, H = 52, h - 36, w - 80, h - 60
    lf0, lf1 = math.log10(fmin), math.log10(fmax)
    X = lambda f: x0 + W * (math.log10(f) - lf0) / (lf1 - lf0)
    Y = lambda d: y0 - H * (d - dbmin) / (dbmax - dbmin)
    b = b2b_arrow(x0, y0, x0 + W + 8, y0) + b2b_arrow(x0, y0, x0, y0 - H - 10)
    b += b2b_text(x0 + W + 8, y0 + 28, xlab, anchor="end", size=10) + b2b_text(x0 + 4, y0 - H - 14, ylab, anchor="start", size=10)
    step = 20 if dbmax - dbmin > 50 else 10
    d = math.ceil(dbmin / step) * step
    while d <= dbmax + 1e-9:
        b += b2b_line(x0 - 3, Y(d), x0 + 3, Y(d)) + b2b_text(x0 - 6, Y(d) + 3, str(int(d)), anchor="end", size=10)
        if d == 0 and dbmin < 0: b += b2b_line(x0, Y(0), x0 + W, Y(0), dash=True, op=0.5)
        d += step
    for k in range(int(math.ceil(lf0 - 1e-9)), int(math.floor(lf1 + 1e-9)) + 1):
        tx = X(10 ** k)
        sup = str(k).replace('-', '⁻').translate(str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹'))
        b += b2b_line(tx, y0 - 3, tx, y0 + 3) + b2b_text(tx, y0 + 15, "10" + sup if k not in (0, 1) else ("1" if k == 0 else "10"), size=10)
    b += b2b_poly([(X(f), Y(dd)) for f, dd in segs], sw=2.2)
    if exact:
        pts = []
        for i in range(121):
            f = 10 ** (lf0 + (lf1 - lf0) * i / 120)
            dv = exact(f)
            if dbmin - 5 <= dv <= dbmax + 5: pts.append((X(f), Y(max(dbmin, min(dbmax, dv)))))
        b += b2b_poly(pts, dash=True)
    for f, dd, lab in marks:
        b += b2b_circle(X(f), Y(dd), 3, True) + b2b_text(X(f) + 6, Y(dd) - 6, lab, anchor="start", size=10)
    return b2b_svg(w, h, b, title)

def o_sine_pair(a1, ph1, a2, ph2, l1="input", l2="output", title="Input and output sinusoids", ymax=None):
    ym = ymax or max(a1, a2) * 1.25
    return P([dict(fn=lambda t: a1 * math.cos(t + math.radians(ph1)), label=l1, lx=6.9, ly=a1 * 0.95, anchor="end"),
              dict(fn=lambda t: a2 * math.cos(t + math.radians(ph2)), dash="5 4", label=l2, lx=6.9, ly=-ym * 0.85, anchor="end")],
             (0, 4 * math.pi), (-ym, ym), "ωt", "v", label=title, w=360, h=200)

E = math.exp
def step_rc(t, tau=1.0, V=1.0): return V * (1 - E(-t / tau)) if t > 0 else 0.0

# ---------------------------------------------------------------- the map
def build_map():
    M = {}
    def add(qid, svg, alt): M[qid] = (svg, alt)
    # ---------- lti-def
    add('lti-def-r1-q3', o_chain(["L"], "4x₁(t) − x₂(t)", "y(t) = ?", title="Linear system"), "A linear system L driven by the input 4 x1(t) minus x2(t); the output is unknown.")
    add('lti-def-r2-q3', P([dict(pts=[(0, 0), (0.0001, 0), (1, 4), (2, 3), (3, 1.5)], label="y(t)", lx=2.2, ly=3.4)], (0, 3.2), (0, 5), "t (ms)", "y (V)",
                           marks=[(1, 4, "4 V", 6, -6), (2, 3, "3 V", 6, -6)], xticks=[(1, "1"), (2, "2"), (3, "3")], label="Measured output y(t)"),
        "Sketch of the original output y(t), passing 4 V at t = 1 ms and 3 V at t = 2 ms.")
    add('lti-def-r3-q1', P([dict(fn=lambda v: 2 * v + 1, label="v_out = 2v_in + 1", lx=0.15, ly=4.4)], (-1, 2), (-2, 5), "v_in (V)", "v_out (V)", zero_axis=True, marks=[(0, 1, "1 V at v_in = 0", 6, -8)], label="Input-output line"),
        "Straight line v_out = 2 v_in + 1 that crosses the vertical axis at 1 V, not at the origin.")
    add('lti-def-r3-q3', P([dict(fn=lambda f: 0, pts=[(1, 0), (1, 1)], label="1 kHz", lx=1.1, ly=0.95), dict(pts=[(3, 0), (3, 0.3)], label="3 kHz", lx=3.1, ly=0.32)], (0, 4.5), (0, 1.2), "f (kHz)", "output spectrum", label="Output spectrum"),
        "Output spectrum with a tall line at 1 kHz and a smaller line at 3 kHz, although only 1 kHz was applied.")
    add('lti-def-r4-q1', o_stems([0, 4, 2, 1], ["0", "1", "2", "3"], ylabel="h (V)", title="Response to one unit pulse"), "Stem plot of the single-pulse response: 0, 4, 2 and 1 volts at t = 0, 1, 2 and 3 ms.")
    add('lti-def-r4-q2', o_sine_pair(1, 0, 0.5, -60, "input cos(ωt)", "output 0.5cos(ωt − 60°)", "Measured response of the LTI circuit"), "Input cosine of amplitude 1 and output cosine of amplitude 0.5 lagging it by 60 degrees.")
    # ---------- rc-lpf
    add('rc-lpf-r1-q1', o_rc(), "Voltage source vs driving series resistor R; the output vo is taken across capacitor C to ground.")
    add('rc-lpf-r1-q3', o_rc(rl="10 kΩ", cl="10 nF"), "RC low-pass filter with R = 10 kilohms and C = 10 nanofarads.")
    add('rc-lpf-r2-q1', o_rc(vs="0 → 5 V", rl="2 kΩ", cl="500 nF", title="RC low-pass with a step input"), "RC low-pass filter, R = 2 kilohms, C = 500 nanofarads, driven by a step from 0 to 5 V.")
    add('rc-lpf-r2-q3', o_bode([(0.01, 0), (1, 0), (100, -40)], 0.01, 100, 5, dbmin=-40, xlab="ωτ", title="RC low-pass magnitude", exact=lambda x: -10 * math.log10(1 + x * x), marks=[(1, 0, "ω = 1/τ")]),
        "Bode magnitude of the RC low-pass: flat, then falling 20 dB per decade beyond the corner at omega = 1/tau; the exact curve is dashed.")
    add('rc-lpf-r3-q1', P([dict(fn=lambda t: 0.7 * math.cos(t - 0.8) - 0.7 * math.cos(0.8) * E(-t / 1.2), label="v_o(t)", lx=9, ly=0.85), dict(fn=lambda t: math.cos(t), dash="5 4", label="v_s", lx=12.2, ly=1.05, anchor="end")],
                          (0, 12.5), (-1.2, 1.3), "t", "v", label="Switch-on of a sinusoid"), "The source cosine (dashed) and the capacitor voltage, which starts at zero and settles into a sinusoid.")
    add('rc-lpf-r3-q2', P([dict(fn=lambda t: 1 - E(-t), label="v_o", lx=3.2, ly=0.85)], (0, 5), (0, 1.15), "t", "v_o / V_final", hlines=[(0.9, "90%"), (0.1, "10%")], label="Step response with 10% and 90% levels"),
        "Rising exponential step response with dashed lines at 10 percent and 90 percent of the final value.")
    add('rc-lpf-r3-q3', o_rc(vs="10 V step", rl="R = 1 kΩ", cl="1 µF", load="R_L = 1 kΩ", title="RC low-pass with a load resistor"), "RC low-pass filter with a load resistor RL = 1 kilohm in parallel with the 1 microfarad capacitor, driven by a 10 V step.")
    add('rc-lpf-r4-q2', P([dict(fn=lambda t: 1 - E(-t), label="v_o / V_f", lx=3, ly=0.85)], (0, 4), (0, 1.15), "t / RC", "", hlines=[(0.5, "50%")], label="Step response reaching 50%"),
        "Normalized RC step response with a dashed line at 50 percent of the final value.")
    add('rc-lpf-r4-q3', o_bode([(10, 0), (1e3, 0), (1e5, -40)], 10, 1e5, 5, dbmin=-40, xlab="f (Hz)", title="Want −20 dB at 10 kHz", marks=[(1e4, -20, "−20 dB at 10 kHz")]),
        "Asymptotic low-pass Bode plot with a marked point at minus 20 dB at 10 kilohertz.")
    # ---------- cx-exp
    add('cx-exp-r1-q1', o_phasors([(1, 50, "e^{jx}")], title="Unit circle"), "A unit-length arrow at angle x on the complex plane, ending on the unit circle.")
    add('cx-exp-r1-q3', o_phasors([(5, 53.13, "Z = 3 + j4"), (3, 0, "3", True), (4, 90, "j4", True)], R=5.5, title="Impedance on the complex plane"), "Arrow from the origin to 3 + j4 on the complex plane, with its real part 3 and imaginary part 4 marked.")
    add('cx-exp-r2-q1', o_phasors([(2.83, 135, "−2 + j2")], R=3, title="z on the complex plane"), "Arrow pointing into the second quadrant to the point minus 2 plus j2.")
    add('cx-exp-r2-q3', o_phasors([(2, 30, "2∠30°"), (3, 60, "3∠60°"), (1.5, -45, "1.5∠−45°")], R=3.4, title="The three factors"), "Three arrows on the complex plane: 2 at 30 degrees, 3 at 60 degrees, and 1.5 at minus 45 degrees.")
    add('cx-exp-r3-q3', P([dict(fn=lambda t: 5 * E(-0.5 * t) * math.cos(10 * t), label="Re v(t)", lx=3.4, ly=2.6), dict(fn=lambda t: 5 * E(-0.5 * t), dash="5 4", label="envelope", lx=1.2, ly=3.6), dict(fn=lambda t: -5 * E(-0.5 * t), dash="5 4")],
                          (0, 6), (-5.5, 5.5), "t (s)", "v (V)", label="Decaying oscillation"), "A cosine oscillation inside a dashed exponentially decaying envelope starting at 5 V.")
    add('cx-exp-r4-q1', o_phasors([(0.67, -26.57, "H = 0.6 − j0.3")], R=0.8, title="H on the complex plane"), "Arrow to 0.6 minus j0.3, slightly below the positive real axis.")
    add('cx-exp-r4-q3', o_splane(poles=[(-100, 995), (-100, -995)], xr=(-1200, 300), yr=(-1200, 1200), title="Poles near the jω axis", ticks=[(-100, "−100")]), "Two complex-conjugate poles close to the imaginary axis at minus 100 plus or minus j995.")
    # ---------- sinusoid-resp
    add('sinusoid-resp-r1-q1', o_chain(["LTI"], "cos(ωt)", "?", title="LTI circuit driven by a sinusoid"), "Block diagram: cos(omega t) into an LTI block, output unknown.")
    add('sinusoid-resp-r1-q3', o_rc(vs="10cos(ωt)", title="RC low-pass, τ = 1 ms"), "RC low-pass filter driven by 10 cos(omega t).")
    add('sinusoid-resp-r2-q2', o_bode([(10, 0), (500, 0), (5e4, -40)], 10, 5e4, 5, dbmin=-40, xlab="f (Hz)", title="First-order low-pass, corner ≈ 80 Hz", exact=lambda f: -10 * math.log10(1 + (2 * math.pi * f * 2e-3) ** 2)),
        "Magnitude response of a first-order low-pass with its corner near 80 hertz.") if False else None
    add('sinusoid-resp-r3-q2', P([dict(fn=lambda t: 5 + 2 * math.cos(t), label="x(t) = 5 + 2cos(ωt)", lx=0.2, ly=7.6)], (0, 13), (0, 8.5), "ωt", "x (V)", hlines=[(5, "DC 5 V")], label="Input: DC plus a sinusoid"),
        "Input waveform: a 2 V cosine riding on a 5 V DC level.")
    add('sinusoid-resp-r3-q3', o_sine_pair(1, -90, 0.707, -135, "input 10sin(ωt)", "output", "Input and lagging output (shape only)"), "Input sine and a smaller output sine that lags it.")
    add('sinusoid-resp-r4-q1', o_circuit([(None, [('R', "R = 1 kΩ"), ('C', "C = 2 µF")])], vs="i_in", out="v", title="Photodiode current into R ∥ C", isrc=True), "A current source feeding a node with a 1 kilohm resistor and a 2 microfarad capacitor in parallel to ground.")
    add('sinusoid-resp-r4-q3', o_bode([(10, 0), (1e3, 0), (1e5, -40), (1e6, -80)], 10, 1e6, 5, dbmin=-80, title="Two cascaded poles", marks=[(1e4, -20, "ω = 10⁴")]),
        "Asymptotic Bode magnitude with poles at 10^3 and 10^5 rad/s; the slope is minus 20 dB per decade between them.")
    # ---------- impulse-conv
    add('impulse-conv-r1-q1', o_chain(["h(t)"], "δ(t)", "h(t)", title="Impulse in, impulse response out"), "Block diagram: a delta function into the system gives the impulse response h(t).")
    add('impulse-conv-r1-q3', o_chain(["delay 2 ms"], "x(t)", "x(t − 2 ms)", title="Pure delay"), "Block diagram of a pure 2 millisecond delay.")
    add('impulse-conv-r2-q1', o_stems([2, 1], ["h[0]", "h[1]"], ylabel="h (V)", title="Impulse response samples", w=240), "Stem plot of the impulse response: 2 V at n = 0 and 1 V at n = 1.")
    add('impulse-conv-r2-q2', P([dict(fn=lambda t: 3 * E(-t / 2) if t >= 0 else 0, label="h(t) = 3e^{−t/2ms}", lx=1.5, ly=2.6)], (0, 8), (0, 3.4), "t (ms)", "h (V)", label="Impulse response"), "Decaying exponential impulse response starting at 3 V with a 2 millisecond time constant.")
    add('impulse-conv-r3-q1', P([dict(pts=[(0, 0), (0, 500), (2, 500), (2, 0)], label="h(t)", lx=2.2, ly=480)], (-0.5, 4.5), (0, 650), "t (ms)", "h (s⁻¹)", xticks=[(2, "2")], label="Rectangular impulse response"), "Rectangular impulse response of height 500 per second from 0 to 2 ms.")
    add('impulse-conv-r3-q2', P([dict(fn=lambda t: E(-t), label="(1/τ)e^{−t/τ}", lx=1.2, ly=0.5)], (0, 5), (0, 1.1), "τ' (age of the input)", "weight", label="Memory weighting"), "Exponentially decaying weight versus how long ago an input value occurred.")
    add('impulse-conv-r4-q1', P([dict(pts=[(0, 0), (0, 250), (4, 250), (4, 0)], label="h(t)", lx=4.2, ly=230)], (-0.5, 6), (0, 320), "t (ms)", "h (s⁻¹)", xticks=[(4, "4")], label="Moving-average impulse response"), "Rectangular impulse response of 250 per second lasting 4 ms.")
    add('impulse-conv-r4-q3', o_chain(["δ(t − 1 ms)", "δ(t − 2.5 ms)"], "x(t)", "y(t)", title="Two delays in cascade"), "Two delay blocks in series, 1 ms and 2.5 ms.")
    # ---------- step-resp
    add('step-resp-r1-q1', o_rc(vs="step 0 → Vₛ", title="RC low-pass with a step input"), "RC low-pass filter driven by a step from 0 to Vs.")
    add('step-resp-r1-q2', P([dict(fn=lambda t: 1 - E(-t), label="v_o / V_final", lx=2.6, ly=0.8)], (0, 5), (0, 1.15), "t / τ", "", xticks=[(1, "1"), (2, "2"), (3, "3")], label="RC step response"), "Normalized RC step response rising toward 1.")
    add('step-resp-r1-q3', o_rc(vs="5 V step", rl="10 kΩ", cl="47 nF"), "RC low-pass filter, 10 kilohms and 47 nanofarads, with a 5 V step input.")
    add('step-resp-r2-q1', P([dict(pts=[(-0.5, 0), (0, 0), (0, 5), (2, 5), (2, 0), (4, 0)], label="v_s", lx=0.4, ly=5.3), dict(fn=lambda t: 0 if t < 0 else (5 * (1 - E(-t)) if t < 2 else 5 * (1 - E(-2)) * E(-(t - 2))), dash="5 4", label="v_o", lx=2.3, ly=4.5)],
                           (-0.5, 4), (0, 6), "t (ms)", "v (V)", xticks=[(2, "2"), (3, "3")], label="Pulse and RC response"), "A 5 V, 2 ms input pulse (solid) and the RC output (dashed) rising then decaying.")
    add('step-resp-r2-q2', P([dict(pts=[(0, 0), (1.5, 0), (1.5, 2), (5, 2)], label="v_s", lx=3.8, ly=2.2)], (0, 5), (0, 2.6), "t", "v (V)", xticks=[(1.5, "t₀")], label="Delayed step"), "A 2 V step that begins at t = t0 instead of t = 0.")
    add('step-resp-r3-q1', P([dict(pts=[(0, 0), (0, 5), (0.15, 5), (0.15, 0), (3, 0)], label="10 µs pulse (not to scale)", lx=0.3, ly=5.2)], (-0.2, 3), (0, 6), "t", "v_s (V)", label="Very short pulse"), "A narrow 5 V input pulse, very short compared with the time constant.")
    add('step-resp-r3-q2', P([dict(fn=lambda t: 5 - 3 * E(-t), label="v_o", lx=3, ly=4.6)], (0, 5), (0, 5.6), "t / τ", "v (V)", hlines=[(5, "5 V")], marks=[(0, 2, "2 V at t = 0", 6, 12)], label="Starting from 2 V"),
        "Capacitor voltage starting at 2 V and rising toward 5 V.")
    add('step-resp-r3-q3', P([dict(fn=lambda t: 5 * (1 - E(-t / 0.25)), label="v_o", lx=0.9, ly=4.2)], (0, 1.2), (0, 6), "t (ms)", "v (V)", label="Initial slope of the step response"),
        "Step response of an RC filter rising from 0 toward 5 V.")
    add('step-resp-r4-q1', o_circuit([(('R', "1 kΩ"), [('R', "4 kΩ"), ('C', "2 nF")])], vs="v", out="node", title="Find the resistance seen by C"), "A source in series with 1 kilohm feeding a node with a 4 kilohm resistor and a 2 nanofarad capacitor to ground.")
    add('step-resp-r4-q3', P([dict(fn=lambda t: 1 - E(-t), label="v_out", lx=3, ly=0.85)], (0, 6), (0, 1.15), "t / τ", "", hlines=[(0.99, "99%")], label="Settling to 1%"), "Normalized step response approaching 1 with a dashed line at 99 percent.")
    # ---------- freq-char
    add('freq-char-r1-q1', o_chain(["h(t)"], "x(t)", "y(t) = h ∗ x", title="Time-domain view"), "Block diagram: x(t) through h(t) gives y(t) equals h convolved with x.")
    add('freq-char-r1-q3', P([dict(pts=[(1, 0), (1, 2)], label="input 1 kHz", lx=1.1, ly=2.05), dict(pts=[(3, 0), (3, 2)], label="input 3 kHz", lx=3.1, ly=2.05)], (0, 4.6), (0, 2.6), "f (kHz)", "amplitude (V)", label="Input spectrum"),
        "Input spectrum with two 2 V lines at 1 kHz and 3 kHz.")
    add('freq-char-r2-q2', o_bode([(10, 0), (318, 0), (1e5, -50)], 10, 1e5, 5, dbmin=-50, xlab="f (Hz)", title="Single-pole response, corner ≈ 318 Hz", exact=lambda f: -10 * math.log10(1 + (f / 318.3) ** 2), marks=[(500, -10 * math.log10(1 + (500 / 318.3) ** 2), "500 Hz")]),
        "Single-pole magnitude response with its corner near 318 hertz and a marked point at 500 hertz.")
    add('freq-char-r2-q3', o_bode([(100, 0), (1e3, 0), (1e5, -40)], 100, 1e5, 5, dbmin=-40, xlab="f (Hz)", title="H(jf) = 1/(1 + jf/1 kHz)", exact=lambda f: -10 * math.log10(1 + (f / 1e3) ** 2)),
        "Asymptotic and exact magnitude of a single-pole filter with a 1 kilohertz corner.")
    add('freq-char-r3-q2', P([dict(pts=[(0.02, 0), (0.02, 4)], label="DC 4 V", lx=0.12, ly=4.05), dict(pts=[(1, 0), (1, 3)], label="3 V @ 1 kHz", lx=1.1, ly=3.05), dict(pts=[(10, 0), (10, 2)], label="2 V @ 10 kHz", lx=9.8, ly=2.4, anchor="end")], (0, 11), (0, 4.8), "f (kHz)", "amplitude (V)", label="Input spectrum"),
        "Input spectrum: 4 V DC, 3 V at 1 kHz and 2 V at 10 kHz.")
    add('freq-char-r4-q2', o_bode([(1e3, 20), (1e5, 20), (1e7, -20)], 1e3, 1e7, 30, dbmin=-20, xlab="f (Hz)", title="Closed-loop gain 10 with a 100 kHz pole", marks=[(1e6, 0, "1 MHz")]),
        "Asymptotic Bode magnitude flat at 20 dB up to 100 kHz then falling 20 dB per decade; 1 MHz is marked.")
    add('freq-char-r4-q3', o_bode([(0.01, 0), (1, 0), (100, -40)], 0.01, 100, 5, dbmin=-40, xlab="ω/ω_c", title="Gain error grows toward ω_c", exact=lambda x: -10 * math.log10(1 + x * x), marks=[(0.2, -10 * math.log10(1.04), "0.2ω_c")]),
        "Single-pole closed-loop magnitude with a marked point at 0.2 omega_c, slightly below 0 dB.")
    # ---------- tf
    add('tf-r1-q2', o_chain(["TIA"], "i_in", "v_out", title="Transimpedance amplifier"), "Block diagram: an input current into a transimpedance amplifier gives an output voltage.")
    add('tf-r2-q2', o_phasors([(1, 20, "V_in"), (0.8, -10, "V_out")], R=1.2, title="Input and output phasors (shape)"), "Two phasors: the input at plus 20 degrees and a slightly shorter output at minus 10 degrees.")
    add('tf-r2-q3', o_circuit([(('R', "2 kΩ"), [('R', "6 kΩ"), ('R', "6 kΩ load")])], vs="v_in", out="v_out", title="Divider with a load"), "Voltage divider: 2 kilohms in series, then 6 kilohms to ground, with a 6 kilohm load in parallel.")
    add('tf-r3-q1', o_circuit([(('R', "R"), None), (('L', "L"), [('C', "C")])], vs="vₛ", out="v_C", title="Series RLC, output across C"), "Series RLC circuit driven by a voltage source with the output taken across the capacitor.")
    add('tf-r3-q2', o_circuit([(('R', "10 kΩ"), [('R', "10 kΩ")]), (('R', "10 kΩ"), [('R', "10 kΩ")])], vs="v_in", out="v_out", title="Two dividers, no buffer"), "Two identical 10 kilohm dividers connected directly one after the other.")
    add('tf-r4-q2', fig_feedback_blocks(g_lab="A", f_lab="β", sin="sᵢₙ", sout="sₒᵤₜ", title="Feedback loop"), "Feedback block diagram: a forward amplifier A with a feedback path beta to a summing junction.")
    add('tf-r4-q3', o_bode([(1e2, 40), (1e4, 40), (1e6, 0)], 1e2, 1e6, 45, xlab="f (Hz)", title="G_v = 100/(1 + jf/10 kHz)", marks=[(1e5, 20, "100 kHz")]),
        "Asymptotic Bode magnitude at 40 dB falling 20 dB per decade beyond 10 kHz; 100 kHz is marked.")
    # ---------- phasors
    add('phasors-r1-q2', o_circuit([(('L', "L"), [('C', "C")])], vs="vₛ", out="", title="L and C at low frequency"), "A source driving an inductor in series and a capacitor to ground.")
    add('phasors-r2-q1', o_circuit([(('R', "300 Ω"), None), (('L', "40 mH"), None)], vs="vₛ", out="", title="Series R–L"), "A 300 ohm resistor in series with a 40 millihenry inductor.")
    add('phasors-r2-q3', o_sine_pair(1, 0, 0.6, -90, "v(t)", "i(t) (scaled)", "Voltage and current of the element"), "Voltage cosine and a current cosine lagging it by 90 degrees.")
    add('phasors-r3-q1', o_phasors([(40, 90, "V_L"), (30, -90, "V_C"), (1, 0, "I", True)], R=45, title="Phasors in the series L–C"), "Inductor voltage phasor pointing up and capacitor voltage phasor pointing down, along with the common current reference.")
    add('phasors-r4-q1', o_circuit([(('R', "1 kΩ"), [('L', "10 mH")])], vs="v_in", out="v_out", title="R–L high-pass"), "A 1 kilohm resistor in series with the output taken across a 10 millihenry inductor to ground.")
    add('phasors-r4-q3', o_circuit([(('R', "50 Ω"), None), (('L', "10 mH"), None), (('C', "1 µF"), None)], vs="vₛ", out="", title="Series RLC"), "Series RLC: 50 ohms, 10 millihenries, 1 microfarad.")
    # ---------- direct-h
    add('direct-h-r1-q1', o_rc(), "RC low-pass filter with series R and output across C.")
    add('direct-h-r1-q3', o_rc(hp=True, title="RC high-pass filter"), "RC high-pass filter: series capacitor and output across the resistor to ground.")
    add('direct-h-r2-q1', o_circuit([(('R', "R₁ = 1 kΩ"), [('R', "R₂ = 1 kΩ"), ('C', "100 nF")])], title="R₁ in series, R₂ ∥ C to ground"), "Source, series 1 kilohm R1, and an output node with R2 = 1 kilohm in parallel with 100 nanofarads to ground.")
    add('direct-h-r2-q2', o_circuit([(('R', "R₁"), [('R', "R₂"), ('C', "C")])], title="Same circuit"), "Series R1 with R2 in parallel with C to ground.")
    add('direct-h-r2-q3', o_circuit([(('R', "R"), None), (('L', "L"), [('C', "C")])], title="Series RLC, output across C"), "Series RLC with the output taken across the capacitor.")
    add('direct-h-r3-q1', o_rc(load="R_L", title="RC low-pass with load"), "RC low-pass with a load resistor RL in parallel with C.")
    add('direct-h-r3-q2', o_circuit([(('R', "R₁"), [('C', "C₁")]), (('R', "R₂"), [('C', "C₂")])], title="Two-stage RC ladder"), "Two-stage RC ladder: R1, C1 to ground, R2, C2 to ground.")
    add('direct-h-r3-q3', o_circuit([(('LCpar', "L ∥ C tank"), [('R', "R")])], title="Parallel LC tank in series, output across R"), "A parallel LC tank in series with the source and a resistor R to ground at the output.")
    add('direct-h-r4-q2', o_circuit([(('C', "1 µF"), None), (('L', "10 mH"), [('R', "50 Ω")])], title="Series RLC, output across R"), "Series RLC with the output across the 50 ohm resistor.")
    add('direct-h-r4-q3', o_bode([(0.01, -40), (1, 0), (100, -40)], 0.01, 100, 5, dbmin=-45, xlab="ω/ω₀", title="Which filter type?", exact=None) if False else
        o_circuit([(('C', "C"), None), (('L', "L"), [('R', "R")])], title="Series RLC, output across R"), "Series RLC circuit with the output across R.")
    # ---------- pole-zero
    add('pole-zero-r1-q2', o_splane(poles=[(-1, 0)], xr=(-2, 1), yr=(-1, 1), title="s-plane", ticks=[(-1, "?")]), "s-plane axes with a single pole on the real axis at an unlabeled location.") if False else None
    add('pole-zero-r2-q1', o_splane(poles=[(-10, 0), (-20, 0)], zeros=[(-200, 0)], xr=(-220, 30), yr=(-60, 60), title="Poles and zero of H(s)", ticks=[(-200, "−200")]), "s-plane with two real poles near the origin and a zero further out at minus 200.")
    add('pole-zero-r2-q2', o_splane(poles=[(-1000, 0)], zeros=[(0, 0)], xr=(-1300, 300), yr=(-500, 500), title="RC high-pass in the s-plane", ticks=[(-1000, "−1000")]), "s-plane with a zero at the origin and a pole at minus 1000.")
    add('pole-zero-r2-q3', o_splane(poles=[(-20, 0), (-2000, 0)], zeros=[(-400, 0)], xr=(-2200, 200), yr=(-500, 500), title="H(s) = 1000(s + 400)/((s + 20)(s + 2000))", ticks=[(-2000, "−2000"), (-400, "−400")]), "s-plane with poles at minus 20 and minus 2000 and a zero at minus 400.")
    add('pole-zero-r3-q2', o_splane(poles=[(-500, 0), (-1000, 0)], zeros=[(-500, 0)], xr=(-1200, 200), yr=(-400, 400), title="Pole-zero map", ticks=[(-1000, "−1000"), (-500, "−500")]), "s-plane with poles at minus 500 and minus 1000 and a zero sitting on the pole at minus 500.")
    add('pole-zero-r3-q3', o_circuit([(('R', "50 Ω"), None), (('L', "10 mH"), [('C', "25 µF")])], title="Series RLC, output across C"), "Series RLC with 50 ohms, 10 millihenries and 25 microfarads; output across C.")
    add('pole-zero-r4-q1', o_bode([(1, 33.98), (20, 33.98), (400, 7.96), (2000, 7.96), (1e5, -26)], 1, 1e5, 40, dbmin=-30, xlab="ω (rad/s)", title="Bode sketch: breaks at 20, 400, 2000"), "Asymptotic Bode magnitude with breaks at 20, 400 and 2000 rad/s.")
    add('pole-zero-r4-q3', o_splane(poles=[(-5000, 31225), (-5000, -31225)], xr=(-40000, 10000), yr=(-40000, 40000), title="Complex RLC poles"), "Two complex-conjugate poles in the left half-plane.")
    # ---------- rlc
    add('rlc-r1-q2', o_circuit([(('R', "R"), None), (('L', "L"), None), (('C', "C"), None)], out="", title="Series RLC: Z = R + jωL + 1/(jωC)"), "Series RLC circuit across a source.")
    add('rlc-r2-q1', o_circuit([(('R', "20 Ω"), None), (('L', "10 mH"), None), (('C', "1 µF"), None)], out="", title="Series RLC"), "Series RLC with 20 ohms, 10 millihenries and 1 microfarad.")
    add('rlc-r2-q2', o_bode([(100, -40), (1e4, 0), (1e6, -40)], 100, 1e6, 5, dbmin=-45, xlab="ω (rad/s)", title="Band-pass (output across R)", exact=lambda w: -10 * math.log10(1 + (5 * (w / 1e4 - 1e4 / w)) ** 2)),
        "Band-pass magnitude of the series RLC peaking at 0 dB at omega0 = 10^4 rad/s.")
    add('rlc-r2-q3', o_circuit([(('R', "R"), None), (('C', "C"), [('L', "L")])], vs="2 V", out="v_L", title="Voltage across L at resonance"), "Series RLC driven by 2 V with the output taken across the inductor.")
    add('rlc-r3-q2', o_bode([(10, -40), (1e3, 0), (1e5, -40)], 10, 1e5, 5, dbmin=-45, xlab="ω (rad/s)", title="Low-Q band-pass, ω₀ = 1000", exact=lambda w: -10 * math.log10(1 + (w / 1e3 - 1e3 / w) ** 2), marks=[(1e3, 0, "ω₀")]),
        "Broad band-pass magnitude centered at 1000 rad/s.")
    add('rlc-r3-q3', P([dict(fn=lambda x: 1 / math.sqrt((1 - x * x) ** 2 + (2 * x) ** 2), label="Q = 0.5 (shape)", lx=1.2, ly=0.55)], (0, 3), (0, 1.2), "ω/ω₀", "|V_C/V_s|", label="Capacitor-output magnitude"), "Capacitor-output magnitude of a Q = 0.5 series RLC versus normalized frequency.")
    add('rlc-r4-q2', o_circuit([(('C', "100 nF"), None), (('L', "ESL 10 nH"), None)], out="", title="Real capacitor = series LC"), "A 100 nanofarad capacitor drawn in series with its 10 nanohenry parasitic inductance.")
    add('rlc-r4-q3', o_bode([(0.01, 0), (1, 0), (100, -80)], 0.01, 100, 25, dbmin=-40, xlab="ω/ω₀", title="Second-order low-pass with peaking", exact=lambda x: -10 * math.log10((1 - x * x) ** 2 + (x / 5) ** 2)),
        "Second-order low-pass magnitude with a resonant peak near omega0.")
    # ---------- bode
    add('bode-r1-q1', o_bode([(0.01, 0), (1, 0), (100, -40)], 0.01, 100, 10, dbmin=-45, xlab="ω/ω_p", title="First-order low-pass (asymptotes)"), "Asymptotic Bode magnitude of a first-order low-pass: flat, then a straight falling line beyond the pole.")
    add('bode-r2-q1', o_bode([(100, 40), (1e4, 40), (1e6, 0)], 100, 1e6, 45, title="H = 100/(1 + jω/10⁴)", marks=[(3e5, 40 - 20 * math.log10(30), "3×10⁵")]), "Asymptotic Bode plot at 40 dB with a pole at 10^4 rad/s; the point at 3 times 10^5 rad/s is marked.")
    add('bode-r2-q2', P([dict(fn=lambda lw: -math.degrees(math.atan(10 ** lw / 100) + math.atan(10 ** lw / 1e4)), label="∠H", lx=3.6, ly=-60)], (0, 6), (-190, 10), "log₁₀ ω", "phase (°)", hlines=[(-90, "−90°"), (-180, "−180°")], xticks=[(2, "10²"), (4, "10⁴")], label="Phase of the two-pole response"),
        "Phase of a two-pole response falling from 0 toward minus 180 degrees, with poles at 10^2 and 10^4 rad/s.")
    add('bode-r2-q3', o_bode([(1, 60), (10, 60), (1e3, 20), (1e5, -60)], 1, 1e5, 65, dbmin=-60, title="H = 1000/[(1 + jω/10)(1 + jω/1000)]"), "Asymptotic Bode magnitude with poles at 10 and 1000 rad/s starting at 60 dB.")
    add('bode-r3-q1', o_bode([(0.01, 0), (1, 0), (100, -80)], 0.01, 100, 10, dbmin=-80, xlab="ω/ω_p", title="Double pole: asymptote vs exact", exact=lambda x: -20 * math.log10(1 + x * x), marks=[(1, 0, "ω_p")]),
        "Double-pole Bode magnitude: the asymptote has a corner at omega_p while the exact dashed curve sits below it.")
    add('bode-r3-q3', o_bode([(1, 20), (100, 20), (1e3, 40), (1e5, 40)], 1, 1e5, 45, title="Zero at 100, pole at 1000", exact=lambda w: 20 + 10 * math.log10(1 + (w / 100) ** 2) - 10 * math.log10(1 + (w / 1e3) ** 2)),
        "Bode magnitude rising from 20 dB to 40 dB between a zero at 100 and a pole at 1000 rad/s.")
    add('bode-r4-q1', o_bode([(1, 100), (10, 100), (1e6, 0), (1e7, -20)], 1, 1e7, 105, dbmin=-20, xlab="f (Hz)", title="Op-amp open loop: A₀ = 10⁵, pole at 10 Hz"), "Op-amp open-loop Bode magnitude: 100 dB to 10 Hz, then falling 20 dB per decade.")
    add('bode-r4-q2', o_bode([(1, 0), (20, 26.02), (2e5, 26.02), (1e7, -7.96)], 1, 1e7, 30, dbmin=-10, xlab="f (Hz)", title="AC-coupled amplifier", exact=lambda f: 26.02 + 20 * math.log10((f / 20) / math.sqrt(1 + (f / 20) ** 2)) - 10 * math.log10(1 + (f / 2e5) ** 2)),
        "Band-pass shaped Bode magnitude: rising to 26 dB at 20 Hz, flat, then falling beyond 200 kHz.")
    add('bode-r4-q3', o_bode([(10, 60), (1e3, 60), (1e6, 0), (1e7, -20), (1e8, -60)], 10, 1e8, 65, dbmin=-60, title="Loop gain L(jω)", marks=[(1e6, 0, "|L| ≈ 1")]), "Asymptotic loop-gain magnitude crossing 0 dB near 10^6 rad/s, before the second pole at 10^7.")
    # ---------- ac-power
    add('ac-power-r1-q1', P([dict(fn=lambda t: math.sin(2 * t) * 0.5, label="p(t) = v·i", lx=0.3, ly=0.62)], (0, 2 * math.pi), (-0.8, 0.8), "ωt", "p", zero_axis=True, label="Capacitor power over one cycle"), "Instantaneous capacitor power alternating equally above and below zero.")
    add('ac-power-r2-q1', o_phasors([(1, 0, "V"), (0.7, -60, "I (lags 60°)")], R=1.1, title="V and I phasors"), "Voltage phasor along the real axis and a current phasor lagging it by 60 degrees.")
    add('ac-power-r2-q3', o_phasors([(10, 53.13, "Z = 6 + j8 Ω"), (6, 0, "Re Z", True)], R=11, title="Load impedance"), "Impedance arrow to 6 + j8 ohms, with its real part 6 marked.")
    add('ac-power-r3-q1', o_phasors([(1, 30, "V = 10∠30°"), (0.6, -30, "I = 2∠−30°")], R=1.15, title="Load phasors"), "Voltage phasor at 30 degrees and current phasor at minus 30 degrees.")
    add('ac-power-r3-q2', P([dict(fn=lambda t: 3 + 4 * math.cos(t), label="v(t)", lx=0.3, ly=7.4)], (0, 4 * math.pi), (-1.5, 8), "ωt", "v (V)", hlines=[(3, "3 V DC")], label="DC plus a sinusoid"), "Waveform of a 4 V peak cosine riding on a 3 V DC level.")
    add('ac-power-r3-q3', o_circuit([(('R', "30 Ω"), None), (('L', "j40 Ω"), None)], vs="100cos(ωt)", out="", title="Load Z = 30 + j40 Ω"), "Source driving a load of 30 ohms in series with a reactance of j40 ohms.")
    add('ac-power-r4-q2', o_circuit([(None, [('R', "2 kΩ load")])], vs="±10 V peak", out="v_out", title="Op-amp output into 2 kΩ"), "Output swinging plus or minus 10 V peak into a 2 kilohm load.")
    return {k: v for k, v in M.items() if v and v[0]}

MAP = build_map()

if __name__ == '__main__':
    import collections
    c = collections.Counter(k.rsplit('-r', 1)[0] for k in MAP)
    print(len(MAP), dict(c))
