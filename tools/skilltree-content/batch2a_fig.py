"""batch2a_fig.py - SVG figure helpers for the batch2a question banks (device-physics diagrams).
Self-contained inline SVG (viewBox, no scripts, no external refs); strokes/text = currentColor.
Text mini-markup: 'V_{GB}', 'x_p', 'N_A^-', 'cm^{-3}' -> sub/superscript tspans."""
import math
from xml.sax.saxutils import escape

def _mk(s, size):
    out, i, s = [], 0, str(s)
    sm = max(7, int(size * 0.72))
    while i < len(s):
        c = s[i]
        if c in "_^" and i + 1 < len(s):
            if s[i + 1] == "{":
                j = s.index("}", i); tok = s[i + 2:j]; i = j + 1
            else:
                tok = s[i + 1]; i += 2
            dy = size * (0.28 if c == "_" else -0.4)
            out.append(f'<tspan font-size="{sm}" dy="{dy:.1f}">{escape(tok)}</tspan><tspan dy="{-dy:.1f}"></tspan>')
        else:
            j = i
            while j < len(s) and s[j] not in "_^": j += 1
            out.append(escape(s[i:j])); i = j
    return "".join(out)

class Fig:
    def __init__(self, w, h, label=""):
        self.w, self.h, self.label, self.parts = w, h, label, []
    def add(self, s): self.parts.append(s); return self
    def line(self, x1, y1, x2, y2, w=1.5, dash=None, op=None):
        a = f' stroke-dasharray="{dash}"' if dash else ''
        b = f' stroke-opacity="{op}"' if op is not None else ''
        return self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke-width="{w}"{a}{b}/>')
    def rect(self, x, y, w, h, fill=0.0, sw=1.5, dash=None, nostroke=False):
        a = f' stroke-dasharray="{dash}"' if dash else ''
        st = ' stroke="none"' if nostroke else f' stroke-width="{sw}"'
        f = f' fill="currentColor" fill-opacity="{fill}"' if fill else ''
        return self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"{f}{st}{a}/>')
    def circle(self, cx, cy, r, fill=False, op=None, sw=1.5):
        f = ' fill="currentColor"' if fill else ''
        o = f' fill-opacity="{op}"' if (op is not None and fill) else ''
        return self.add(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}"{f}{o} stroke-width="{sw}"/>')
    def poly(self, pts, closed=False, fill=0.0, w=1.5, dash=None, nostroke=False):
        p = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        a = f' stroke-dasharray="{dash}"' if dash else ''
        f = f' fill="currentColor" fill-opacity="{fill}"' if fill else ' fill="none"'
        st = ' stroke="none"' if nostroke else f' stroke-width="{w}"'
        return self.add(f'<{"polygon" if closed else "polyline"} points="{p}"{f}{st}{a} stroke-linejoin="round"/>')
    def arrow(self, x1, y1, x2, y2, w=1.5, head=7, dash=None):
        self.line(x1, y1, x2, y2, w=w, dash=dash)
        ang = math.atan2(y2 - y1, x2 - x1)
        p1 = (x2 - head * math.cos(ang - 0.4), y2 - head * math.sin(ang - 0.4))
        p2 = (x2 - head * math.cos(ang + 0.4), y2 - head * math.sin(ang + 0.4))
        return self.poly([(x2, y2), p1, p2], closed=True, fill=1.0, nostroke=True)
    def text(self, x, y, s, anchor="middle", size=12, bold=False, rot=None, op=None):
        tr = f' transform="rotate({rot} {x:.1f} {y:.1f})"' if rot else ''
        b = ' font-weight="bold"' if bold else ''
        o = f' fill-opacity="{op}"' if op is not None else ''
        return self.add(f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" font-size="{size}"{b}{o} fill="currentColor" stroke="none"{tr}>{_mk(s, size)}</text>')
    def svg(self):
        lab = escape(self.label, {'"': '&quot;'})
        return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{lab}" '
                f'fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" font-family="sans-serif" '
                f'style="max-width:{min(self.w, 520)}px;width:100%;height:auto">' + "".join(self.parts) + '</svg>')

def dim_arrow(f, x1, y1, x2, y2, label=None, off=(0, -6), size=11, anchor="middle"):
    f.arrow(x1, y1, x2, y2, head=5); f.arrow(x2, y2, x1, y1, head=5)
    if label: f.text((x1 + x2) / 2 + off[0], (y1 + y2) / 2 + off[1], label, size=size, anchor=anchor)

# ---------------------------------------------------------------- generic plot
def plot(curves, xlim, ylim, xlabel="", ylabel="", w=360, h=230, title="", label="", hlines=(), vlines=(), marks=(), xticks=(), yticks=(), zero_axis=None, texts=()):
    """curves: dict(fn=callable | pts=[(x,y)], label, dash, lx, ly, anchor). hlines/vlines: (value, text). marks: (x,y,text,dx,dy). texts: (x,y,text)."""
    f = Fig(w, h, label or title or "plot")
    L, R, T, B = 56, 22, 30 if title else 22, 40
    X0, Y0, W, H = L, T, w - L - R, h - T - B
    ax = lambda x: X0 + (x - xlim[0]) / (xlim[1] - xlim[0]) * W
    ay = lambda y: Y0 + H - (y - ylim[0]) / (ylim[1] - ylim[0]) * H
    xaxis_y = ay(0) if (zero_axis or (zero_axis is None and ylim[0] < 0 < ylim[1])) else Y0 + H
    f.arrow(X0, xaxis_y, X0 + W, xaxis_y); f.arrow(X0, Y0 + H, X0, Y0)
    if xlabel: f.text(X0 + W, Y0 + H + 30, xlabel, anchor="end", size=11)
    if ylabel: f.text(X0 - 8, Y0 - 8, ylabel, anchor="start", size=11)
    if title: f.text(w / 2, 15, title, size=12, bold=True)
    for v, t in hlines:
        f.line(X0, ay(v), X0 + W, ay(v), dash="4 3", w=1, op=0.7); f.text(X0 + W, ay(v) - 4, t, anchor="end", size=10)
    for v, t in vlines:
        f.line(ax(v), Y0 + H, ax(v), Y0, dash="4 3", w=1, op=0.7); f.text(ax(v), Y0 + H + 16, t, size=10)
    for v, t in xticks:
        f.line(ax(v), xaxis_y - 3, ax(v), xaxis_y + 3, w=1.2); f.text(ax(v), Y0 + H + 16, t, size=10)
    for v, t in yticks:
        f.line(X0 - 3, ay(v), X0 + 3, ay(v), w=1.2); f.text(X0 - 7, ay(v) + 4, t, anchor="end", size=10)
    for c in curves:
        pts = c.get("pts") or [(x, c["fn"](x)) for x in [xlim[0] + (xlim[1] - xlim[0]) * i / 100 for i in range(101)]]
        pp = [(ax(x), ay(y)) for x, y in pts if ylim[0] - 1e-9 <= y <= ylim[1] + 1e-9]
        f.poly(pp, w=2.0, dash=c.get("dash"))
        if c.get("label"):
            lx, ly = c.get("lx", pts[-1][0]), c.get("ly", pts[-1][1])
            f.text(ax(lx), ay(ly), c["label"], size=11, anchor=c.get("anchor", "start"))
    for x, y, t, dx, dy in marks:
        f.circle(ax(x), ay(y), 3.2, fill=True); f.text(ax(x) + dx, ay(y) + dy, t, size=10, anchor="start" if dx >= 0 else "end")
    for x, y, t in texts: f.text(ax(x), ay(y), t, size=10)
    return f.svg()

# ---------------------------------------------------------------- band diagrams
def band_diagram(kind="intrinsic", ef_frac=None, w=300, h=190, gap="E_g", ec="E_c", ev="E_v", ei=True, label="", ef_label="E_F"):
    """Energy bands. ef_frac in [0,1] (0=Ev, 1=Ec) overrides kind (intrinsic .5, n .85, p .15)."""
    f = Fig(w, h, label or f"Band diagram ({kind})")
    x0, x1 = 56, w - 46
    yc, yv = 48, h - 48
    f.rect(x0, 10, x1 - x0, yc - 10, fill=0.12, nostroke=True); f.rect(x0, yv, x1 - x0, h - 10 - yv, fill=0.12, nostroke=True)
    f.line(x0, yc, x1, yc, w=2.4); f.line(x0, yv, x1, yv, w=2.4)
    f.text(x0 - 6, yc + 4, ec, anchor="end"); f.text(x0 - 6, yv + 4, ev, anchor="end")
    f.text((x0 + x1) / 2 + 20, 28, "conduction band", size=10, op=0.7); f.text((x0 + x1) / 2 + 20, h - 20, "valence band", size=10, op=0.7)
    ym = (yc + yv) / 2
    frac = ef_frac if ef_frac is not None else {"intrinsic": 0.5, "n": 0.85, "p": 0.15}.get(kind, 0.5)
    ye = yv - frac * (yv - yc)
    if ei: f.line(x0, ym, x1, ym, dash="5 4", w=1.2); f.text(x1 + 4, ym + 4, "E_i", anchor="start", size=11)
    if abs(ye - ym) > 2: f.line(x0, ye, x1, ye, w=2); f.text(x1 + 4, ye + 4, ef_label, anchor="start", size=11)
    else: f.text(x1 + 4, ym + 18, ef_label + "=E_i", anchor="start", size=10)
    if gap:
        xg = x0 + 20
        f.arrow(xg, ym - 6, xg, yc + 1, head=5); f.arrow(xg, ym + 6, xg, yv - 1, head=5); f.text(xg + 6, ym + 4, gap, anchor="start", size=11)
    return f.svg()

def lattice(dopant=None, broken=False, w=300, h=210, label=""):
    f = Fig(w, h, label or "2D silicon bond model")
    cols, rows, dx, dy, ox, oy = 4, 3, 62, 60, 50, 36
    pos = {(i, j): (ox + i * dx, oy + j * dy) for i in range(cols) for j in range(rows)}
    for (i, j), (x, y) in pos.items():
        if i + 1 < cols: f.line(x, y, pos[(i + 1, j)][0], y, w=2.2, op=0.5)
        if j + 1 < rows: f.line(x, y, x, pos[(i, j + 1)][1], w=2.2, op=0.5)
    for (i, j), (x, y) in pos.items():
        sp = bool(dopant) and (i, j) == (1, 1)
        f.circle(x, y, 11, fill=not sp, op=0.18 if not sp else None)
        f.text(x, y + 4, "Si" if not sp else ("P" if dopant == "donor" else "B"), size=11, bold=sp)
    x, y = pos[(1, 1)]
    if dopant == "donor":
        f.circle(x + 36, y - 30, 3.8, fill=True); f.text(x + 44, y - 34, "free e^-", anchor="start", size=10)
        f.text(x, y + 28, "fixed +", size=10)
    elif dopant == "acceptor":
        f.circle(x + 31, y + 2, 4.5); f.text(x + 38, y - 8, "free h^+", anchor="start", size=10)
        f.text(x, y + 28, "fixed –", size=10)
    if broken:
        x, y = pos[(2, 2)]
        f.circle(x + 30, y - 24, 3.8, fill=True); f.text(x + 38, y - 28, "e^-", anchor="start", size=10)
        f.circle(x + 31, y, 4.5); f.text(x + 38, y + 14, "h^+", anchor="start", size=10)
    return f.svg()

def bar(w=380, h=150, llabel="L", acap="cross-section A", vlabel="V", carriers="e", elabel="E", label="", ilabel=None):
    """Semiconductor bar with V across, E arrow, carrier drift arrow."""
    f = Fig(w, h, label or "Semiconductor bar with applied voltage")
    x0, x1, y0, y1 = 70, w - 80, 46, 96
    ym = (y0 + y1) / 2
    f.rect(x0, y0, x1 - x0, y1 - y0, fill=0.10)
    f.line(x0 - 40, ym, x0, ym); f.line(x1, ym, x1 + 40, ym)
    f.text(x0 - 30, ym - 8, "+", size=14, bold=True); f.text(x1 + 30, ym - 8, "–", size=14, bold=True)
    f.text((x0 + x1) / 2, 16, vlabel, size=11)
    f.arrow(x0 + 40, y0 + 12, x1 - 40, y0 + 12); f.text((x0 + x1) / 2, y0 - 3, elabel, size=11)
    if carriers == "e": f.arrow(x1 - 50, y1 - 12, x0 + 50, y1 - 12, w=1.2, dash="4 3"); f.text((x0 + x1) / 2, y1 - 17, "electrons", size=10, op=0.8)
    elif carriers == "h": f.arrow(x0 + 50, y1 - 12, x1 - 50, y1 - 12, w=1.2, dash="4 3"); f.text((x0 + x1) / 2, y1 - 17, "holes", size=10, op=0.8)
    dim_arrow(f, x0, y1 + 20, x1, y1 + 20, llabel, off=(0, 16))
    f.text(x1 + 6, y1 + 20, acap, anchor="start", size=10, op=0.8)
    if ilabel: f.arrow(8, ym - 10, 34, ym - 10, head=5); f.text(8, ym - 16, ilabel, anchor="start", size=10)
    return f.svg()

def rg_centers(w=330, h=190, label=""):
    """Trap-assisted generation/recombination: bands with a mid-gap trap level."""
    f = Fig(w, h, label or "Trap-assisted recombination and generation")
    x0, x1, yc, yv = 40, w - 20, 46, h - 46
    f.rect(x0, 10, x1 - x0, yc - 10, fill=0.12, nostroke=True); f.rect(x0, yv, x1 - x0, h - 10 - yv, fill=0.12, nostroke=True)
    f.line(x0, yc, x1, yc, w=2.4); f.line(x0, yv, x1, yv, w=2.4)
    f.text(x0 - 4, yc + 4, "E_c", anchor="end"); f.text(x0 - 4, yv + 4, "E_v", anchor="end")
    ym = (yc + yv) / 2
    f.line(x0 + 30, ym, x1 - 30, ym, dash="5 4"); f.text(x1 - 28, ym + 14, "trap level", anchor="end", size=10)
    xr = x0 + 90
    f.circle(xr, yc - 14, 4, fill=True); f.arrow(xr, yc - 6, xr, ym - 4, head=5); f.arrow(xr + 20, ym + 4, xr + 20, yv - 10, head=5)
    f.circle(xr + 20, yv + 14, 4); f.text(xr + 8, yc - 18, "e^-", anchor="start", size=10)
    f.text(xr + 10, h - 6, "recombination", size=10)
    xg = x1 - 90
    f.circle(xg, yv + 14, 4); f.arrow(xg, yv - 6, xg, ym + 4, head=5); f.arrow(xg + 20, ym - 4, xg + 20, yc + 6, head=5); f.circle(xg + 20, yc - 14, 4, fill=True)
    f.text(xg + 10, h - 6, "generation", size=10)
    return f.svg()

# ---------------------------------------------------------------- PN junction
def pn_profiles(NA=1.0, ND=1.0, show=("rho", "E", "phi"), w=360, label="", bias=None, annotate=True, mark_xp="-x_p", mark_xn="x_n", emax="E_{max}", phibi="φ_{bi}"):
    """Qualitative stacked plots (depletion approximation). Depletion widths: x_p : x_n = ND : NA. bias: width multiplier."""
    n = len(show); ph = 100
    h = 24 + n * ph + 14
    f = Fig(w, h, label or "PN junction charge density, electric field and potential")
    x0, x1 = 44, w - 24
    xj = (x0 + x1) / 2
    tot = 130.0 * (bias or 1.0)
    a = tot * ND / (NA + ND); b = tot * NA / (NA + ND)
    xl, xr = xj - a, xj + b
    for k, key in enumerate(show):
        top = 20 + k * ph; mid = top + 42; bot = top + 82
        f.line(x0, mid, x1, mid, w=1.2); f.text(x1, mid + 14, "x", anchor="end", size=10)
        f.line(xj, top + 6, xj, bot, dash="2 3", w=0.8, op=0.6)
        if key == "rho":
            hp, hn = 30 * NA / max(NA, ND), 30 * ND / max(NA, ND)
            f.rect(xl, mid, xj - xl, hp, fill=0.22); f.rect(xj, mid - hn, xr - xj, hn, fill=0.22)
            f.line(x0, mid, xl, mid, w=2.2); f.line(xr, mid, x1, mid, w=2.2)
            f.text(x0 - 36, top + 12, "ρ(x)", anchor="start", size=11, bold=True)
            if annotate:
                f.text((xl + xj) / 2, mid + hp + 12, "–qN_A", size=10); f.text((xj + xr) / 2, mid - hn - 4, "+qN_D", size=10)
        if key == "E":
            pk = 32
            f.poly([(x0, mid), (xl, mid), (xj, mid + pk), (xr, mid), (x1, mid)], w=2.2)
            f.text(x0 - 36, top + 12, "E(x)", anchor="start", size=11, bold=True)
            f.text(xj + 8, mid + pk + 2, emax, anchor="start", size=10)
        if key == "phi":
            lo, hi = mid + 30, mid - 30
            A, B = xj - xl, xr - xj; T = A + B
            def pf(x): return (x - xl) ** 2 / (A * T) if x <= xj else 1 - (xr - x) ** 2 / (B * T)
            pts = [(x0, lo)] + [(x, lo + pf(x) * (hi - lo)) for x in [xl + (xr - xl) * i / 60 for i in range(61)]] + [(x1, hi)]
            f.poly(pts, w=2.2)
            f.text(x0 - 36, top + 12, "φ(x)", anchor="start", size=11, bold=True)
            f.line(x0, lo, xl, lo, dash="3 3", w=0.8, op=0.6); f.line(xr, hi, x1, hi, dash="3 3", w=0.8, op=0.6)
            f.arrow(x1 - 8, lo - 1, x1 - 8, hi + 2, head=5); f.text(x1 - 12, (lo + hi) / 2 + 4, phibi, anchor="end", size=11)
        if k == n - 1:
            f.text(xl, bot + 14, mark_xp, size=10); f.text(xr, bot + 14, mark_xn, size=10)
            f.line(xl, mid - 3, xl, mid + 3, w=1.2); f.line(xr, mid - 3, xr, mid + 3, w=1.2)
    f.text(x0 + 4, h - 3, "P side", anchor="start", size=10, op=0.7); f.text(x1 - 4, h - 3, "N side", anchor="end", size=10, op=0.7)
    return f.svg()

def pn_block(w=340, h=130, note=None, show_dep=True, label="", left="P", right="N"):
    """PN junction block diagram with depletion region."""
    f = Fig(w, h, label or "PN junction block diagram")
    x0, xj, x1, y0, y1 = 30, w / 2, w - 30, 30, 90
    f.rect(x0, y0, xj - x0, y1 - y0, fill=0.05); f.rect(xj, y0, x1 - xj, y1 - y0, fill=0.16)
    f.text((x0 + xj - 40) / 2, (y0 + y1) / 2 + 5, left, size=16, bold=True); f.text((xj + 40 + x1) / 2, (y0 + y1) / 2 + 5, right, size=16, bold=True)
    if show_dep:
        f.rect(xj - 22, y0, 44, y1 - y0, dash="4 3", sw=1.2)
        f.text(xj - 11, (y0 + y1) / 2 + 4, "–", size=14, bold=True); f.text(xj + 11, (y0 + y1) / 2 + 4, "+", size=14, bold=True)
        f.text(xj, y1 + 16, "depletion region", size=10)
    if note: f.text(w / 2, 16, note, size=11)
    return f.svg()

# ---------------------------------------------------------------- MOS capacitor
def mos_stack(region="depletion", w=340, h=232, vlabel=None, label="", xdep_label="x_{dep}", extra=()):
    """NMOS-C cross-section. region: accumulation | flatband | depletion | inversion | threshold | neutral."""
    f = Fig(w, h, label or f"MOS capacitor ({region})")
    x0, x1 = 64, w - 64
    gy0, gy1, oy1 = 24, 54, 72
    by0, by1 = oy1, h - 26
    f.rect(x0, gy0, x1 - x0, gy1 - gy0, fill=0.25); f.text(x1 + 6, (gy0 + gy1) / 2 + 4, "n⁺ poly gate", anchor="start", size=10)
    f.rect(x0, gy1, x1 - x0, oy1 - gy1, fill=0.05); f.text(x1 + 6, (gy1 + oy1) / 2 + 4, "oxide", anchor="start", size=10)
    f.rect(x0, by0, x1 - x0, by1 - by0, fill=0.12); f.text(x1 + 6, by1 - 8, "p-type body", anchor="start", size=10)
    f.line((x0 + x1) / 2, 8, (x0 + x1) / 2, gy0); f.text((x0 + x1) / 2 + 6, 14, "G", anchor="start", size=12, bold=True)
    f.text(x0 - 6, by1 - 8, "B", anchor="end", size=12, bold=True)
    if vlabel: f.text(x0 - 6, 14, vlabel, anchor="end", size=11)
    def row(y, ch, n):
        for i in range(n): f.text(x0 + 14 + i * (x1 - x0 - 28) / (n - 1), y + 4, ch, size=14, bold=True)
    if region == "accumulation":
        row(gy1 - 9, "–", 9); row(by0 + 10, "+", 9); f.text((x0 + x1) / 2, by0 + 40, "holes pile up at surface", size=10, op=0.8)
    elif region == "flatband":
        f.text((x0 + x1) / 2, gy1 - 8, "Q_G = 0", size=10); f.text((x0 + x1) / 2, by0 + 20, "Q_B = 0, no depletion", size=10)
    elif region in ("depletion", "neutral"):
        row(gy1 - 9, "+", 7); xd = 56 if region == "depletion" else 36
        f.rect(x0, by0, x1 - x0, xd, dash="5 3", sw=1.2); row(by0 + xd / 2, "–", 6)
        dim_arrow(f, x0 - 14, by0, x0 - 14, by0 + xd); f.text(x0 - 20, by0 + xd / 2 + 4, xdep_label, anchor="end", size=10)
        f.text(x1 - 4, by0 + xd + 15, "neutral p-type", anchor="end", size=10, op=0.7)
    elif region in ("inversion", "threshold"):
        row(gy1 - 9, "+", 10); xd = 70
        f.rect(x0, by0, x1 - x0, xd, dash="5 3", sw=1.2)
        if region == "inversion":
            f.rect(x0, by0, x1 - x0, 7, fill=0.35, nostroke=True); f.text(x1 - 4, by0 + 22, "electron layer (inversion)", anchor="end", size=10)
        row(by0 + 40, "–", 6)
        dim_arrow(f, x0 - 14, by0, x0 - 14, by0 + xd); f.text(x0 - 20, by0 + xd / 2 + 4, xdep_label, anchor="end", size=10)
    for x, y, t in extra: f.text(x, y, t, size=10)
    return f.svg()

def mos_profiles(w=360, label="", show=("E", "phi")):
    """Qualitative E(x) and φ(x) from gate (left) through oxide into body (right) in depletion (depletion approximation)."""
    n = len(show); ph = 108; h = 22 + n * ph + 22
    f = Fig(w, h, label or "Field and potential through oxide and body")
    x0, xo, xd, x1 = 44, 120, 250, w - 18
    for k, key in enumerate(show):
        top = 20 + k * ph; mid = top + 38; bot = top + 90
        f.line(x0 - 10, mid, x1, mid, w=1.2); f.text(x1, mid + 14, "x", anchor="end", size=10)
        f.line(x0, top + 4, x0, bot, dash="2 3", w=0.8, op=0.5); f.line(xo, top + 4, xo, bot, dash="2 3", w=0.8, op=0.6); f.line(xd, top + 4, xd, bot, dash="2 3", w=0.8, op=0.4)
        if key == "E":
            eox, esi = 42, 14
            f.poly([(x0, mid), (x0, mid - eox), (xo, mid - eox), (xo, mid - esi), (xd, mid)], w=2.2)
            f.text(x0 - 40, top + 10, "E(x)", anchor="start", size=11, bold=True)
            f.text((x0 + xo) / 2, mid - eox - 5, "E_{ox}", size=10); f.text(xo + 6, mid - esi - 12, "E_s (surface)", anchor="start", size=10)
            f.text((x0 + xo) / 2, mid + 14, "oxide", size=10, op=0.7); f.text((xo + xd) / 2, mid + 14, "depletion", size=10, op=0.7)
        else:
            lo = mid + 6
            def pf(x):
                if x <= xo: return 1.0 - 0.55 * (x - x0) / (xo - x0)
                if x <= xd: return 0.45 * (1 - (x - xo) / (xd - xo)) ** 2
                return 0.0
            pts = [(x, lo - pf(x) * 62) for x in [x0 + (xd - x0) * i / 80 for i in range(81)]] + [(x1, lo)]
            f.poly(pts, w=2.2)
            f.text(x0 - 40, top + 10, "φ(x)", anchor="start", size=11, bold=True)
            f.text(x0 + 4, lo - 62 - 4, "φ_{gate}", anchor="start", size=10); f.text(xo + 4, lo - 0.45 * 62 - 6, "ψ_s", anchor="start", size=11)
            f.text(x1 - 4, lo + 14, "φ_p (bulk)", anchor="end", size=10)
            f.text((x0 + xo) / 2, bot + 6, "oxide", size=10, op=0.7); f.text((xo + xd) / 2, bot + 6, "depletion", size=10, op=0.7)
    f.text(xo, h - 4, "x = 0", size=10); f.text(xd, h - 4, "x_{dep}", size=10); f.text(x0, h - 4, "–t_{ox}", size=10)
    return f.svg()

def cv_curve(w=360, h=220, vfb="V_{FB}", vt="V_T", cmin=0.35, label="", cmin_label=None):
    """MOS C-V (low-frequency): flat C_ox, dip, back to C_ox."""
    f = Fig(w, h, label or "MOS capacitance versus gate voltage")
    X0, Y0, W, H = 56, 24, w - 80, h - 66
    f.arrow(X0, Y0 + H, X0 + W, Y0 + H); f.arrow(X0, Y0 + H, X0, Y0)
    f.text(X0 + W, Y0 + H + 30, "V_{GB}", anchor="end", size=11); f.text(X0 - 8, Y0 - 8, "C (per area)", anchor="start", size=11)
    xa, xb = X0 + W * 0.30, X0 + W * 0.70
    ytop = Y0 + 22; ybot = ytop + (1 - cmin) * (Y0 + H - 6 - ytop)
    xm = xa + (xb - xa) * 0.8
    pts = [(X0 + 4, ytop), (xa, ytop)] + [(xa + (xm - xa) * t / 10, ytop + (ybot - ytop) * (1 - (1 - t / 10) ** 2)) for t in range(1, 11)] \
          + [(xm + (xb - xm) * t / 6, ybot + (ytop - ybot) * (t / 6) ** 1.4) for t in range(1, 7)] + [(X0 + W - 6, ytop)]
    f.poly(pts, w=2.4)
    f.text(X0 - 6, ytop + 4, "C_{ox}", anchor="end", size=11)
    for x, t in ((xa, vfb), (xb, vt)):
        f.line(x, Y0 + H, x, Y0 + 8, dash="3 3", w=0.9, op=0.6); f.text(x, Y0 + H + 16, t, size=11)
    f.text((X0 + xa) / 2 + 4, ytop - 8, "accumulation", size=10); f.text((xa + xb) / 2 - 8, Y0 + H - 6, "depletion", size=10); f.text((xb + X0 + W) / 2, ytop - 8, "inversion", size=10)
    if cmin_label: f.line(X0, ybot, xm, ybot, dash="3 3", w=0.9, op=0.6); f.text(X0 - 6, ybot + 4, cmin_label, anchor="end", size=10)
    return f.svg()

def profile_decay(w=360, h=210, ylabel="Δp(x)", label="", long=False, L_label="L_p", y0_label="Δp(0)"):
    """Excess-carrier profile: exponential decay, or a straight line when there is no recombination."""
    f = Fig(w, h, label or "Excess minority carrier profile")
    X0, Y0, W, H = 56, 24, w - 84, h - 64
    f.arrow(X0, Y0 + H, X0 + W, Y0 + H); f.arrow(X0, Y0 + H, X0, Y0)
    f.text(X0 + W, Y0 + H + 30, "x", anchor="end", size=11); f.text(X0 - 8, Y0 - 8, ylabel, anchor="start", size=11)
    if not long:
        f.poly([(X0 + W * t / 100, Y0 + H - (H - 14) * math.exp(-4.0 * t / 100)) for t in range(0, 101)], w=2.4)
        xl = X0 + W * 0.25
        f.line(xl, Y0 + H, xl, Y0 + H - (H - 14) * math.exp(-1), dash="3 3", w=1); f.text(xl, Y0 + H + 16, L_label, size=11)
        f.text(xl + 6, Y0 + H - (H - 14) * math.exp(-1) - 6, y0_label + "/e", anchor="start", size=10)
    else:
        f.poly([(X0, Y0 + 14), (X0 + W * 0.8, Y0 + H)], w=2.4); f.text(X0 + W * 0.8, Y0 + H + 16, "W", size=11)
    f.text(X0 - 6, Y0 + 18, y0_label, anchor="end", size=10)
    return f.svg()

def resistor_circuit(w=300, h=130, rlabel="R", vlabel="V", ilabel="I", label=""):
    """Source + series resistor loop."""
    f = Fig(w, h, label or "Voltage source driving a resistor")
    xl, xr, yt, yb = 60, w - 50, 26, h - 26
    zx0, zx1 = xl + 70, xr - 40
    f.line(xl, yt, zx0, yt)
    pts = [(zx0, yt)]; seg = (zx1 - zx0 - 20) / 6
    for i in range(6): pts.append((zx0 + 10 + seg * (i + 0.5), yt + (-9 if i % 2 == 0 else 9)))
    pts.append((zx1, yt)); f.poly(pts); f.line(zx1, yt, xr, yt)
    f.line(xr, yt, xr, yb); f.line(xr, yb, xl, yb)
    ym = (yt + yb) / 2
    f.line(xl, yt, xl, ym - 15); f.line(xl, ym + 15, xl, yb); f.circle(xl, ym, 15)
    f.text(xl, ym - 1, "+", size=11); f.text(xl, ym + 11, "–", size=11)
    f.text(xl - 22, ym + 4, vlabel, anchor="end", size=11); f.text((zx0 + zx1) / 2, yt - 14, rlabel, size=11)
    f.arrow(xl + 14, yt + 14, xl + 44, yt + 14, head=5); f.text(xl + 29, yt + 28, ilabel, size=10)
    return f.svg()
