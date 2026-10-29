
# ===================================================================================
# batch2b SVG helpers (prefix b2b_) -- schematics, block diagrams, plots.
# All output is self-contained inline SVG: viewBox, no scripts, no external refs,
# strokes/fills use currentColor so figures follow the app's light/dark theme.
# ===================================================================================
import math as _b2b_math
from xml.sax.saxutils import escape as _b2b_esc

def b2b_svg(w, h, body, title=None):
    t = f"<title>{_b2b_esc(title)}</title>" if title else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" fill="none" '
            f'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" '
            f'font-family="sans-serif" font-size="12">{t}{body}</svg>')

def _n(x):
    return f"{x:.1f}".rstrip("0").rstrip(".")

def b2b_line(x1, y1, x2, y2, dash=False, sw=None, op=None):
    a = ' stroke-dasharray="4 3"' if dash else ""
    if sw: a += f' stroke-width="{sw}"'
    if op: a += f' stroke-opacity="{op}"'
    return f'<line x1="{_n(x1)}" y1="{_n(y1)}" x2="{_n(x2)}" y2="{_n(y2)}"{a}/>'

def b2b_poly(pts, closed=False, dash=False, sw=None, fill=None):
    d = " ".join(f"{_n(x)},{_n(y)}" for x, y in pts)
    tag = "polygon" if closed else "polyline"
    a = ' stroke-dasharray="4 3"' if dash else ""
    if sw: a += f' stroke-width="{sw}"'
    if fill: a += f' fill="{fill}" fill-opacity="0.15"'
    return f'<{tag} points="{d}"{a}/>'

def b2b_path(d, dash=False, sw=None):
    a = ' stroke-dasharray="4 3"' if dash else ""
    if sw: a += f' stroke-width="{sw}"'
    return f'<path d="{d}"{a}/>'

def b2b_text(x, y, s, anchor="middle", size=None, bold=False, italic=False):
    a = f' text-anchor="{anchor}"'
    if size: a += f' font-size="{size}"'
    if bold: a += ' font-weight="bold"'
    if italic: a += ' font-style="italic"'
    return f'<text x="{_n(x)}" y="{_n(y)}"{a} fill="currentColor" stroke="none">{_b2b_esc(s)}</text>'

def b2b_rect(x, y, w, h, fill=False, dash=False, r=0):
    a = f' rx="{r}"' if r else ""
    if fill: a += ' fill="currentColor" fill-opacity="0.10"'
    if dash: a += ' stroke-dasharray="4 3"'
    return f'<rect x="{_n(x)}" y="{_n(y)}" width="{_n(w)}" height="{_n(h)}"{a}/>'

def b2b_circle(x, y, r, fill=False):
    a = ' fill="currentColor"' if fill else ""
    return f'<circle cx="{_n(x)}" cy="{_n(y)}" r="{_n(r)}"{a}/>'

def b2b_dot(x, y):
    return b2b_circle(x, y, 2.6, True)

def b2b_arrow(x1, y1, x2, y2, head=7):
    ang = _b2b_math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * _b2b_math.cos(ang - 0.4), y2 - head * _b2b_math.sin(ang - 0.4))
    p2 = (x2 - head * _b2b_math.cos(ang + 0.4), y2 - head * _b2b_math.sin(ang + 0.4))
    return (b2b_line(x1, y1, x2, y2) +
            f'<polygon points="{_n(x2)},{_n(y2)} {_n(p1[0])},{_n(p1[1])} {_n(p2[0])},{_n(p2[1])}" fill="currentColor" stroke="none"/>')

def b2b_resistor(x, y, L=60, horiz=True, label=None, lpos=None):
    """zigzag from (x,y); horizontal goes right, vertical goes down. Label centered above/right."""
    n = 6
    lead = (L - 36) / 2
    if horiz:
        pts = [(x, y), (x + lead, y)]
        for i in range(n):
            pts.append((x + lead + 3 + i * 5, y + (-6 if i % 2 == 0 else 6)))
        pts += [(x + L - lead, y), (x + L, y)]
        out = b2b_poly(pts)
        if label: out += b2b_text(x + L / 2, y - 12, label) if lpos is None else b2b_text(*lpos, label)
    else:
        pts = [(x, y), (x, y + lead)]
        for i in range(n):
            pts.append((x + (-6 if i % 2 == 0 else 6), y + lead + 3 + i * 5))
        pts += [(x, y + L - lead), (x, y + L)]
        out = b2b_poly(pts)
        if label: out += b2b_text(x + 12, y + L / 2 + 4, label, anchor="start") if lpos is None else b2b_text(*lpos, label)
    return out

def b2b_capacitor(x, y, L=40, horiz=True, label=None):
    g = 5; pl = 9
    if horiz:
        m = x + L / 2
        out = (b2b_line(x, y, m - g, y) + b2b_line(m + g, y, x + L, y) +
               b2b_line(m - g, y - pl, m - g, y + pl) + b2b_line(m + g, y - pl, m + g, y + pl))
        if label: out += b2b_text(m, y - 14, label)
    else:
        m = y + L / 2
        out = (b2b_line(x, y, x, m - g) + b2b_line(x, m + g, x, y + L) +
               b2b_line(x - pl, m - g, x + pl, m - g) + b2b_line(x - pl, m + g, x + pl, m + g))
        if label: out += b2b_text(x + 14, m + 4, label, anchor="start")
    return out

def b2b_vsource(x, y, L=50, label=None, lside="left"):
    """circle source, + at top; terminals at (x,y) top and (x,y+L) bottom."""
    r = 12; m = y + L / 2
    out = (b2b_line(x, y, x, m - r) + b2b_line(x, m + r, x, y + L) + b2b_circle(x, m, r) +
           b2b_text(x, m - 2, "+", size=11) + b2b_text(x, m + 10, "\u2212", size=11))
    if label:
        out += b2b_text(x - 17, m + 4, label, anchor="end") if lside == "left" else b2b_text(x + 17, m + 4, label, anchor="start")
    return out

def b2b_isource(x, y, L=50, label=None, lside="right"):
    r = 12; m = y + L / 2
    out = (b2b_line(x, y, x, m - r) + b2b_line(x, m + r, x, y + L) + b2b_circle(x, m, r) +
           b2b_arrow(x, m + 8, x, m - 8, 6))
    if label:
        out += b2b_text(x + 17, m + 4, label, anchor="start") if lside == "right" else b2b_text(x - 17, m + 4, label, anchor="end")
    return out

def b2b_ground(x, y):
    return (b2b_line(x, y, x, y + 6) + b2b_line(x - 9, y + 6, x + 9, y + 6) +
            b2b_line(x - 5, y + 10, x + 5, y + 10) + b2b_line(x - 1.5, y + 14, x + 1.5, y + 14))

def b2b_opamp(x, y, w=56, h=56, plus_top=False, label_inputs=True):
    """triangle with left edge at x, vertical center y, tip at x+w. Inputs at (x,y-h/4),(x,y+h/4).
    Default: '-' on top, '+' on bottom (inverting config). Output at (x+w, y)."""
    pts = [(x, y - h / 2), (x, y + h / 2), (x + w, y)]
    out = b2b_poly(pts, closed=True)
    ty, by = y - h / 4, y + h / 4
    top, bot = ("+", "\u2212") if plus_top else ("\u2212", "+")
    if label_inputs:
        out += b2b_text(x + 7, ty + 4, top, size=12) + b2b_text(x + 7, by + 4, bot, size=12)
    return out, (x, ty), (x, by), (x + w, y)

def b2b_diode(x, y, L=44, horiz=True, label=None):
    """anode at (x,y), cathode at far end. current flows in +x (horiz) or +y (vert)."""
    t = 8
    if horiz:
        m = x + L / 2
        out = (b2b_line(x, y, m - t, y) + b2b_line(m + t, y, x + L, y) +
               b2b_poly([(m - t, y - t), (m - t, y + t), (m + t, y)], closed=True) +
               b2b_line(m + t, y - t, m + t, y + t))
        if label: out += b2b_text(m, y - 14, label)
    else:
        m = y + L / 2
        out = (b2b_line(x, y, x, m - t) + b2b_line(x, m + t, x, y + L) +
               b2b_poly([(x - t, m - t), (x + t, m - t), (x, m + t)], closed=True) +
               b2b_line(x - t, m + t, x + t, m + t))
        if label: out += b2b_text(x + 14, m + 4, label, anchor="start")
    return out

def b2b_box(x, y, w, h, label, fill=True):
    return b2b_rect(x, y, w, h, fill=fill, r=4) + b2b_text(x + w / 2, y + h / 2 + 4, label)

def b2b_sum(x, y, r=10, signs=("+", "\u2212")):
    """summing junction circle centered (x,y); left input +, bottom input -."""
    return (b2b_circle(x, y, r) + b2b_text(x - r - 6, y - 4, signs[0], size=11) +
            b2b_text(x + 8, y + r + 12, signs[1], size=11))

def b2b_axes(x0, y0, w, h, xlabel="", ylabel="", ticks_x=None, ticks_y=None):
    """axes with origin at (x0,y0) (bottom-left), extending right w and up h."""
    out = b2b_arrow(x0, y0, x0 + w, y0) + b2b_arrow(x0, y0, x0, y0 - h)
    if xlabel: out += b2b_text(x0 + w, y0 + 16, xlabel, anchor="end")
    if ylabel: out += b2b_text(x0 + 4, y0 - h - 4, ylabel, anchor="start")
    for (tx, lab) in (ticks_x or []):
        out += b2b_line(tx, y0 - 3, tx, y0 + 3) + b2b_text(tx, y0 + 15, lab, size=10)
    for (ty, lab) in (ticks_y or []):
        out += b2b_line(x0 - 3, ty, x0 + 3, ty) + b2b_text(x0 - 6, ty + 3, lab, anchor="end", size=10)
    return out

def b2b_curve(fn, xa, xb, x0, y0, sx, sy, n=80, dash=False, sw=None):
    """plot y=fn(x) for x in [xa,xb]; pixel = (x0 + sx*x, y0 - sy*y)."""
    pts = []
    for i in range(n + 1):
        x = xa + (xb - xa) * i / n
        pts.append((x0 + sx * x, y0 - sy * fn(x)))
    return b2b_poly(pts, dash=dash, sw=sw)

def b2b_wire(*c):
    """polyline from flat coords: b2b_wire(x1,y1,x2,y2,...)"""
    return b2b_poly([(c[i], c[i + 1]) for i in range(0, len(c), 2)])
