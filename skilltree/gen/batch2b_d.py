"""batch2b group D: electrostatics, mim-cap, nl-cap, junction-cap"""
from batch2b_lib import *
from batch2b_b import g_

q = 1.602e-19
e0 = 8.854e-14          # F/cm
es = 11.7 * e0          # silicon, F/cm (reader: 11.7 eps0)
eox = 3.9 * e0          # SiO2, F/cm (reader: 3.9 eps0 = 3.45e-13 F/cm)
Vt = 0.0259
ni = 1e10

def fig_plates(t_lab="t_ox", V_lab="V", title="Parallel-plate (MIM) capacitor", stack=None):
    b = b2b_rect(60, 30, 200, 12, fill=True) + b2b_rect(60, 92, 200, 12, fill=True)
    if stack:
        b += b2b_line(60, 67, 260, 67, dash=True) + b2b_text(270, 58, stack[0], anchor="start", size=10) + b2b_text(270, 84, stack[1], anchor="start", size=10)
    else:
        b += b2b_text(160, 72, "insulator, ε", size=11)
    b += b2b_text(160, 24, "top plate (+Q)", size=10) + b2b_text(160, 120, "bottom plate (−Q)", size=10)
    b += b2b_arrow(45, 42, 45, 92, 5) + b2b_arrow(45, 92, 45, 42, 5) + b2b_text(38, 71, t_lab, anchor="end", size=11)
    for x in (90, 130, 170, 210, 240):
        b += b2b_arrow(x, 46, x, 88, 5)
    b += b2b_text(300, 24, V_lab, anchor="end", size=11)
    return b2b_svg(340, 130, b, title)

def fig_rho_E(kind="uniform", title="Charge density and field"):
    """two stacked plots: rho(x) and E(x) for a uniform slab from 0 to x1 (kind='neg': negative charge)."""
    if kind == "neg":
        b = b2b_line(40, 40, 300, 40) + b2b_text(304, 44, "x", anchor="start", size=10) + b2b_text(44, 14, "ρ(x)", anchor="start", size=10)
        b += b2b_poly([(40, 40), (40, 66), (150, 66), (150, 40)], fill="currentColor") + b2b_text(95, 80, "ρ = −qN_A", size=10)
        b += b2b_line(40, 120, 300, 120) + b2b_text(304, 124, "x", anchor="start", size=10) + b2b_text(44, 94, "E(x)", anchor="start", size=10)
        b += b2b_poly([(40, 120), (150, 150), (290, 150)], sw=2.2) + b2b_text(150, 112, "E decreases (slope ρ/ε < 0)", size=10, anchor="start")
        return b2b_svg(330, 165, b, title)
    b = b2b_axes(40, 55, 260, 45, "x", "ρ(x)") + b2b_poly([(40, 55), (40, 25), (150, 25), (150, 55)], fill="currentColor")
    b += b2b_text(150, 68, "x₁", size=10) + b2b_text(95, 20, "ρ₀ = qN", size=10)
    b += b2b_axes(40, 140, 260, 60, "x", "E(x)") + b2b_poly([(40, 140), (150, 95), (290, 95)], sw=2.2) + b2b_text(150, 153, "x₁", size=10)
    return b2b_svg(330, 160, b, title)

def fig_interface(title="Oxide / silicon interface", sheet=False):
    b = b2b_rect(40, 20, 120, 90, fill=True) + b2b_text(100, 15, "SiO₂ (3.9ε₀)", size=10)
    if sheet:
        b += b2b_line(160, 20, 160, 110, sw=4) + "".join(b2b_text(168, y, "+", size=11) for y in (35, 55, 95)) + b2b_text(230, 100, "sheet σ", size=10)
    b += b2b_rect(160, 20, 140, 90) + b2b_text(230, 15, "Si (11.7ε₀)", size=10)
    b += b2b_arrow(60, 65, 140, 65) + b2b_text(100, 58, "E_ox", size=11)
    b += b2b_arrow(180, 65, 220, 65) + b2b_text(200, 58, "E_si", size=11)
    return b2b_svg(330, 120, b, title)

def fig_pn(title="Abrupt PN junction with depletion region", labels=("−xₚ", "0", "xₙ")):
    b = b2b_rect(20, 30, 300, 50) + b2b_rect(120, 30, 110, 50, fill=True)
    b += b2b_line(170, 30, 170, 80) + b2b_text(70, 60, "P (N_A)", size=11) + b2b_text(275, 60, "N (N_D)", size=11)
    b += b2b_text(145, 60, "− − −", size=11) + b2b_text(200, 60, "+ + +", size=11)
    b += b2b_text(120, 96, labels[0], size=10) + b2b_text(170, 96, labels[1], size=10) + b2b_text(230, 96, labels[2], size=10)
    b += b2b_text(175, 22, "depletion region X_dep", size=10)
    return b2b_svg(340, 105, b, title)

def fig_cv(cj0=1.0, phi=0.8, vmin=-4, title="Junction capacitance vs bias", mark=None):
    x0, y0, W, H = 290, 120, 260, 95
    sx = W / (-vmin); sy = H / 1.25
    b = b2b_line(20, y0, x0 + 20, y0) + b2b_line(x0, y0 + 5, x0, y0 - H - 5)
    b += b2b_text(30, y0 + 15, f"V_D = {vmin} V", anchor="start", size=10) + b2b_text(x0, y0 + 15, "0", size=10) + b2b_text(x0 - 4, y0 - H, "C_j", anchor="end", size=11)
    b += b2b_curve(lambda v: cj0 / math.sqrt(1 - v / phi), vmin, 0, x0, y0, sx, sy, sw=2.2)
    b += b2b_text(x0 + 6, y0 - sy * cj0 + 4, "C_j0", anchor="start", size=10)
    if mark is not None:
        cm = cj0 / math.sqrt(1 - mark / phi)
        b += b2b_dot(x0 + sx * mark, y0 - sy * cm)
    return b2b_svg(330, 140, b, title)

def fig_qv(fn, vmin, vmax, title="Non-linear Q–V curve", bias=None, ylab="Q"):
    x0, y0, W, H = 30, 120, 280, 100
    ys = [fn(vmin + (vmax - vmin) * i / 50) for i in range(51)]
    lo, hi = min(ys + [0]), max(ys + [0])
    sx = W / (vmax - vmin); sy = H / (hi - lo if hi > lo else 1)
    X = lambda v: x0 + (v - vmin) * sx
    Y = lambda qv: y0 - (qv - lo) * sy
    b = b2b_line(x0, Y(0), x0 + W, Y(0), op=0.5) + b2b_text(x0 + W, Y(0) + 14, "V", anchor="end", size=10)
    b += b2b_poly([(X(vmin + (vmax - vmin) * i / 60), Y(fn(vmin + (vmax - vmin) * i / 60))) for i in range(61)], sw=2.2)
    b += b2b_text(x0 + 4, 14, ylab, anchor="start", size=11)
    if bias is not None:
        v0 = bias; q0 = fn(v0); d = (vmax - vmin) * 1e-4
        sl = (fn(v0 + d) - fn(v0 - d)) / (2 * d)
        dv = (vmax - vmin) * 0.18
        b += b2b_line(X(v0 - dv), Y(q0 - sl * dv), X(v0 + dv), Y(q0 + sl * dv), dash=True) + b2b_dot(X(v0), Y(q0))
        b += b2b_text(X(v0 + dv), Y(q0 + sl * dv) - 6, "slope = C", size=10)
    return b2b_svg(330, 140, b, title)

# ====================================================================== electrostatics
def electrostatics():
    s = Skill('electrostatics')
    s.round(1)
    s.mc(r"In one dimension, Poisson's equation is \(\dfrac{dE}{dx}=\dfrac{\rho}{\varepsilon}\). What does it imply about the electric field in a region with no charge?",
         r"The field is constant (it can be nonzero, but it doesn't change with \(x\))",
         [r"The field must be zero", r"The field grows linearly with \(x\)", r"The potential must be constant"],
         r"With \(\rho=0\), \(dE/dx=0\), so \(E\) is constant (reader Sec. 4.4.1). It can still be large: the insulator of a charged capacitor is charge-free but has a uniform field. A constant nonzero \(E\) means the potential changes linearly, not that it's constant.",
         fig=fig_plates(), alt="Parallel-plate capacitor with uniform field arrows across the insulator.")
    s.mc(r"The potential \(\phi(x)\) increases with \(x\). Which way does the electric field point?",
         r"Toward \(-x\), since \(E=-d\phi/dx<0\): fields point from high to low potential",
         [r"Toward \(+x\), along the increasing potential", r"There is no field unless charge is present", r"Perpendicular to \(x\)"],
         r"Reader Eq. 4.11: \(E=-\dfrac{d\phi}{dx}\). A positive slope gives a negative field. A positive charge is pushed downhill in potential, while an electron 'floats' toward higher potential.",
         fig=b2b_svg(300, 110, b2b_axes(30, 90, 250, 70, "x", "φ(x)") + b2b_line(40, 85, 260, 30, sw=2.2) + b2b_arrow(220, 100, 150, 100) + b2b_text(185, 96, "E ?", size=11), "Potential increasing with x"),
         alt="Plot of potential rising linearly with x.")
    V, t = 1.0, 10e-7
    s.num(r"A uniform field exists across a 10 nm oxide with 1 V applied. What is the field, in MV/cm?",
          V / t / 1e6, "MV/cm",
          r"Uniform field: \(E=V/t=\dfrac{1\ \mathrm{V}}{10^{-6}\ \mathrm{cm}}=10^6\ \mathrm{V/cm}=1\ \mathrm{MV/cm}\) (10 nm \(=10^{-6}\) cm). For scale, SiO₂ breaks down around 10 MV/cm.",
          tol=0.01, fig=fig_plates("10 nm", "1 V"), alt="Capacitor with a 10 nm insulator and 1 V across it.")
    s.round(2)
    N, x1 = 1e16, 0.5e-4
    Ex = q * N * x1 / es
    s.num(r"A slab of uniform charge \(\rho_0=qN\) with \(N=10^{16}\ \mathrm{cm^{-3}}\) occupies \(0<x<0.5\ \mu\mathrm{m}\) in silicon (\(\varepsilon_s=11.7\varepsilon_0\), \(\varepsilon_0=8.854\times10^{-14}\ \mathrm{F/cm}\)). With \(E(0)=0\), what is \(E(x_1)\) at \(x_1=0.5\ \mu\mathrm{m}\), in kV/cm?",
          Ex / 1e3, "kV/cm",
          T(r"Integrate Poisson: \(E(x_1)=\dfrac{qN}{\varepsilon_s}x_1\) (reader Eq. 4.10)." "\n" r"\(=\dfrac{1.602\times10^{-19}\times10^{16}\times0.5\times10^{-4}}{1.036\times10^{-12}}=<<e>>\ \mathrm{V/cm}\approx<<k>>\ \mathrm{kV/cm}\)." "\n" r"Keep everything in cm: \(0.5\ \mu\mathrm{m}=0.5\times10^{-4}\ \mathrm{cm}\).", e=tex(Ex, 4), k=g_(Ex / 1e3, 4)),
          tol=0.02, fig=fig_rho_E(), alt="Top: uniform charge density from 0 to x1. Bottom: field rising linearly from 0 to x1, then constant.")
    dphi = q * N * x1 ** 2 / (2 * es)
    s.num(r"For the same slab (\(N=10^{16}\ \mathrm{cm^{-3}}\), \(0<x<0.5\ \mu\mathrm{m}\), \(E(0)=0\)), what is the magnitude of the potential change from \(x=0\) to \(x_1\), in V?",
          dphi, "V",
          T(r"\(\phi(x_1)-\phi(0)=-\int_0^{x_1}E\,dx=-\dfrac{qN}{\varepsilon_s}\dfrac{x_1^2}{2}\) (the area under the linear field: a triangle)." "\n" r"\(|\Delta\phi|=\dfrac{E(x_1)\,x_1}{2}=\dfrac{7.73\times10^4\times0.5\times10^{-4}}{2}=<<p>>\ \mathrm{V}\)." "\n" r"Common mistake: using \(E(x_1)x_1\) (rectangle), which doubles it.", p=g_(dphi, 4)),
          tol=0.02, fig=fig_rho_E(), alt="Charge slab and its linearly rising field.")
    s.mc(r"At a charge-free oxide/silicon interface, how do the fields on the two sides compare (\(\varepsilon_{ox}=3.9\varepsilon_0\), \(\varepsilon_s=11.7\varepsilon_0\))?",
         r"\(E_{ox}=3E_{si}\), since \(\varepsilon_{ox}E_{ox}=\varepsilon_sE_{si}\)",
         [r"\(E_{ox}=E_{si}\): fields are always continuous", r"\(E_{ox}=E_{si}/3\)", r"\(E_{ox}=0\)"],
         r"Gauss's law on a thin pillbox with no enclosed charge gives \(\varepsilon_1E_1=\varepsilon_2E_2\) (reader Eq. 4.18–4.19). So \(E_{ox}/E_{si}=\varepsilon_s/\varepsilon_{ox}=11.7/3.9=3\): the lower-permittivity material holds the larger field. The POTENTIAL is continuous; the field jumps.",
         fig=fig_interface(), alt="Oxide region on the left and silicon on the right, with field arrows in each.")
    s.round(3)
    s.mc(r"Which quantity must be continuous across any interface, even one that carries a sheet of charge?",
         r"The potential \(\phi\); the field may jump",
         [r"The electric field \(E\)", r"Both \(E\) and \(\phi\)", r"Neither"],
         r"A jump in \(\phi\) would need an infinite field (infinite force), so \(\phi\) is continuous (reader Sec. 4.4.4). The field jumps at a dielectric change (\(\varepsilon_1E_1=\varepsilon_2E_2\)) and at a sheet of charge (by \(\sigma/\varepsilon\)), giving kinks, not breaks, in \(\phi(x)\).",
         fig=fig_interface(), alt="Interface between oxide and silicon.")
    sigma = q * 1e12
    E2 = sigma / es
    s.num(r"A sheet of positive charge \(\sigma=q\times10^{12}\ \mathrm{cm^{-2}}\) lies at an oxide/silicon interface. The field in the oxide is zero. What is the field just inside the silicon, in kV/cm?",
          E2 / 1e3, "kV/cm",
          T(r"Gauss's pillbox around the sheet: \(\varepsilon_sE_{si}-\varepsilon_{ox}E_{ox}=\sigma\). With \(E_{ox}=0\): \(E_{si}=\dfrac{\sigma}{\varepsilon_s}=\dfrac{1.602\times10^{-7}\ \mathrm{C/cm^2}}{1.036\times10^{-12}\ \mathrm{F/cm}}=<<e>>\ \mathrm{kV/cm}\)." "\n" r"Use \(\varepsilon_s\), the permittivity on the side where the field is.", e=g_(E2 / 1e3, 4)),
          tol=0.02, fig=fig_interface("Sheet charge at the interface", sheet=True), alt="Oxide/silicon interface with a sheet of charge.")
    s.mc(r"A region holds uniform NEGATIVE charge (\(\rho=-qN_A\), like the P side of a depletion region). What is the shape of \(\phi(x)\) there?",
         r"A parabola curving upward (concave up), since \(d^2\phi/dx^2=-\rho/\varepsilon=+qN_A/\varepsilon>0\)",
         [r"A parabola curving downward", r"A straight line", r"A constant"],
         r"Reader Eq. 4.15: \(\dfrac{d^2\phi}{dx^2}=-\dfrac{\rho}{\varepsilon}\). Negative charge gives positive curvature. The field \(E=-d\phi/dx\) then decreases linearly (\(dE/dx=\rho/\varepsilon<0\)). Sign slips here cause most depletion-region mistakes.",
         fig=fig_rho_E("neg"), alt="Uniform charge slab and its field.")
    s.round(4)
    NA, xp = 1e17, 0.1e-4
    Em = q * NA * xp / es
    s.num(r"Preview of the depletion approximation. In a PN junction, the P side holds \(\rho=-qN_A\) for \(-x_p<x<0\) with \(N_A=10^{17}\ \mathrm{cm^{-3}}\), \(x_p=0.1\ \mu\mathrm{m}\), and the field is zero outside. What is the field magnitude at \(x=0\), in kV/cm?",
          Em / 1e3, "kV/cm",
          T(r"Integrating from \(-x_p\) where \(E=0\): \(|E(0)|=\dfrac{qN_Ax_p}{\varepsilon_s}=\dfrac{1.602\times10^{-19}\times10^{17}\times10^{-5}}{1.036\times10^{-12}}=<<e>>\ \mathrm{kV/cm}\)." "\n" r"Here the field peaks at the junction, a triangle shape that the depletion-approximation skill builds from both sides.", e=g_(Em / 1e3, 4)),
          tol=0.02, fig=fig_pn(), alt="Abrupt PN junction with negative depletion charge on the P side and positive on the N side.", preview=["depl-approx", "rev-bias"])
    E = 1e6
    sig = eox * E * 1e6
    s.num(r"Preview of MIM capacitors. The field in an SiO₂ capacitor dielectric is 1 MV/cm (\(\varepsilon_{ox}=3.9\varepsilon_0=3.45\times10^{-13}\ \mathrm{F/cm}\)). By Gauss's law, what charge per area sits on each plate, in \(\mu\mathrm{C/cm^2}\)?",
          sig, "µC/cm²",
          T(r"Just inside the plate the field is \(E\) and zero in the metal, so \(\sigma=\varepsilon_{ox}E=3.453\times10^{-13}\times10^6=<<s>>\ \mu\mathrm{C/cm^2}\)." "\n" r"Combine with \(E=V/t\) and you get \(Q=\dfrac{\varepsilon A}{t}V\): the capacitor formula is next.", s=g_(sig, 4)),
          tol=0.02, fig=fig_plates(), alt="Parallel-plate capacitor.", preview=["mim-cap"])
    s.mc(r"Preview of the MOS structure. A gate oxide sits on silicon with no interface charge. Where is the field larger, just above or just below the interface?",
         r"In the oxide, about 3× larger, because \(\varepsilon_{ox}E_{ox}=\varepsilon_sE_{si}\)",
         [r"In the silicon, 3× larger", r"They are equal", r"The oxide field is zero because it's an insulator"],
         r"\(E_{ox}=\dfrac{\varepsilon_s}{\varepsilon_{ox}}E_{si}=3E_{si}\). Insulators carry field just fine. In the MOS capacitor, this boundary condition ties the oxide voltage drop to the charge in the silicon.",
         fig=fig_interface(), alt="Oxide/silicon interface with fields on both sides.", preview=["mos-struct", "mos-regions"])
    return s

# ====================================================================== mim-cap
def mim_cap():
    s = Skill('mim-cap')
    s.round(1)
    s.mc(r"For a parallel-plate (MIM) capacitor with area \(A\), dielectric thickness \(t\) and permittivity \(\varepsilon\), the capacitance is",
         r"\(C=\dfrac{\varepsilon A}{t}\)",
         [r"\(C=\dfrac{\varepsilon t}{A}\)", r"\(C=\dfrac{At}{\varepsilon}\)", r"\(C=\varepsilon At\)"],
         r"The field is \(E=V/t\) (Eq. 4.20), Gauss gives \(Q=\varepsilon EA\) (Eq. 4.21), so \(Q=\dfrac{\varepsilon A}{t}V\) (Eq. 4.22). A bigger area or a thinner dielectric gives more capacitance.",
         fig=fig_plates(), alt="Parallel-plate capacitor with insulator thickness t_ox.")
    Cox = eox / 20e-7
    s.num(r"What is the oxide capacitance per area of a 20 nm SiO₂ layer (\(\varepsilon_{ox}=3.45\times10^{-13}\ \mathrm{F/cm}\)), in \(\mathrm{fF/\mu m^2}\)?",
          Cox * 1e15 / 1e8, "fF/µm²",
          T(r"\(C_{ox}=\dfrac{\varepsilon_{ox}}{t_{ox}}=\dfrac{3.45\times10^{-13}}{2\times10^{-6}\ \mathrm{cm}}=1.73\times10^{-7}\ \mathrm{F/cm^2}=173\ \mathrm{nF/cm^2}\)." "\n" r"Since \(1\ \mathrm{cm^2}=10^8\ \mu\mathrm{m^2}\): \(1.73\times10^{-7}\ \mathrm{F}/10^8=<<c>>\ \mathrm{fF/\mu m^2}\)." "\n" r"Reader note: the Sec. 7.6.4 example writes this result as '172.5 nF'; the unit should be nF/cm².", c=g_(Cox * 1e7, 4)),
          tol=0.02, fig=fig_plates("20 nm"), alt="Capacitor with a 20 nm oxide.")
    s.mc(r"Why are the charges on the two plates of a capacitor equal and opposite?",
         r"The insulator is charge-free, so the field is uniform across it; by Gauss's law, the field lines leaving the top plate must all end on the bottom plate",
         [r"Because the plates have the same area", r"Because the battery forces it, independent of electrostatics", r"They aren't; the top plate always has more charge"],
         r"Reader Fig. 4.12: with \(\rho=0\) between the plates, \(E\) is constant, and Gauss's law at each plate gives \(+Q\) and \(-Q\) of the same size.",
         fig=fig_plates(), alt="Parallel-plate capacitor with field lines from the top plate to the bottom plate.")
    s.round(2)
    C, t = 1e-12, 30e-7
    A = C * t / eox * 1e8
    s.num(r"Design a 1 pF MIM capacitor with a 30 nm SiO₂ dielectric. What plate area is needed, in \(\mu\mathrm{m^2}\)?",
          A, "µm²",
          T(r"\(A=\dfrac{Ct}{\varepsilon_{ox}}=\dfrac{10^{-12}\times3\times10^{-6}}{3.453\times10^{-13}}=8.69\times10^{-6}\ \mathrm{cm^2}=<<a>>\ \mu\mathrm{m^2}\) (about \(29.5\ \mu\mathrm{m}\) on a side)." "\n" r"Capacitors are expensive in chip area.", a=g_(A, 4)),
          tol=0.02, fig=fig_plates("30 nm"), alt="MIM capacitor with a 30 nm dielectric.")
    V, t = 3.3, 30e-7
    s.num(r"That capacitor (30 nm dielectric) has 3.3 V across it. What is the field in the dielectric, in MV/cm?",
          V / t / 1e6, "MV/cm",
          r"\(E=V/t=3.3/(3\times10^{-6}\ \mathrm{cm})=1.1\times10^6\ \mathrm{V/cm}=1.1\ \mathrm{MV/cm}\), comfortably below the ~10 MV/cm breakdown of SiO₂.",
          tol=0.01, fig=fig_plates("30 nm", "3.3 V"), alt="MIM capacitor with 3.3 V across a 30 nm dielectric.")
    s.mc(r"The dielectric thickness of a MIM capacitor is halved, at the same applied voltage. What happens?",
         r"\(C\) doubles and the field in the dielectric doubles",
         [r"\(C\) doubles and the field is unchanged", r"\(C\) halves and the field doubles", r"\(C\) is unchanged and the field doubles"],
         r"\(C=\varepsilon A/t\) doubles. \(E=V/t\) also doubles, which is why thin dielectrics give dense capacitors but limit the maximum voltage (breakdown).",
         fig=fig_plates(), alt="Parallel-plate capacitor.")
    s.round(3)
    s.mc(r"A MIM capacitor's bottom plate has a large parasitic capacitance to the substrate. One terminal connects to a sensitive high-impedance node, the other to a low-impedance driven node. How should you connect it?",
         r"Bottom plate to the low-impedance node, top plate to the sensitive node",
         [r"Bottom plate to the sensitive node", r"It doesn't matter; the capacitor is symmetric", r"Connect both plates to the sensitive node"],
         r"The bottom-plate parasitic (reader Sec. 4.5.1) loads whatever node the bottom plate touches. On a driven (low-impedance) node it does little harm; on a high-impedance node it adds capacitance and couples substrate noise. The physical structure is NOT symmetric.",
         fig=fig_plates(title="MIM capacitor above the substrate"), alt="Parallel-plate capacitor; the bottom plate is closer to the substrate.")
    t1, t2, k2 = 10e-7, 10e-7, 7.8
    Ca = 1 / (t1 / eox + t2 / (k2 * e0))
    s.num(r"A capacitor dielectric is a stack: 10 nm of SiO₂ (\(3.9\varepsilon_0\)) on 10 nm of a high-k film (\(7.8\varepsilon_0\)). What is the capacitance per area, in \(\mathrm{fF/\mu m^2}\)?",
          Ca * 1e7, "fF/µm²",
          T(r"With no charge at the internal interface, \(D=\varepsilon E\) is the same in both layers, so the voltages add: \(V=\sigma\left(\dfrac{t_1}{\varepsilon_1}+\dfrac{t_2}{\varepsilon_2}\right)\). That's two capacitors in series." "\n" r"\(\dfrac{C}{A}=\dfrac{1}{t_1/\varepsilon_1+t_2/\varepsilon_2}\): the high-k layer acts like 5 nm of SiO₂, so it's like a 15 nm oxide: \(\dfrac{3.453\times10^{-13}}{1.5\times10^{-6}}=<<c>>\ \mathrm{fF/\mu m^2}\)." "\n" r"Common mistake: averaging the permittivities (\(5.85\varepsilon_0\) over 20 nm gives 2.59 fF/µm²).", c=g_(Ca * 1e7, 4)),
          tol=0.02, fig=fig_plates("20 nm", stack=("SiO₂ 10 nm", "high-k 10 nm"), title="Two-layer dielectric"), alt="Capacitor with a two-layer dielectric stack.")
    s.mc(r"For an ideal capacitor with perfect metal plates, where does the charge reside?",
         r"At the plate surfaces facing the dielectric (a thin sheet, like a delta function), with zero field inside the metal",
         [r"Uniformly throughout the plate thickness", r"Spread uniformly through the dielectric", r"At the outer surfaces facing away from the dielectric"],
         r"The field inside an ideal conductor is zero, so by Gauss's law there is no net charge inside the metal; it sits at the surface facing the other plate (reader Fig. 4.13(b)). Because the charge stays at a fixed separation \(t\), \(Q=CV\) is linear. When charge penetrates into the plates (as in semiconductors), that changes.",
         fig=fig_plates(), alt="Parallel-plate capacitor.")
    s.round(4)
    s.num(r"Preview of small-signal capacitance. A linear 1 pF capacitor is biased at 2.0 V, and the voltage rises to 2.1 V. How much extra charge flows onto it, in pC?",
          0.1, "pC",
          r"\(\Delta Q=C\,\Delta V=1\ \mathrm{pF}\times0.1\ \mathrm{V}=0.1\ \mathrm{pC}\). For a linear capacitor \(\Delta Q/\Delta V=Q/V=C\) at every bias. The next skill meets capacitors where \(dQ/dV\) depends on the bias.",
          tol=0.01, fig=fig_qv(lambda v: v, 0, 3, "Linear Q–V", bias=2.0), alt="A straight-line Q-V plot with a bias point at 2 V.", preview=["nl-cap"])
    X = 0.2e-4
    Ca = es / X
    s.num(r"Preview of junction capacitance. A depleted silicon layer \(0.2\ \mu\mathrm{m}\) thick behaves like a parallel-plate dielectric (\(\varepsilon_s=11.7\varepsilon_0\)). What capacitance per area would it have, in \(\mathrm{fF/\mu m^2}\)?",
          Ca * 1e7, "fF/µm²",
          T(r"\(C/A=\varepsilon_s/X=\dfrac{1.036\times10^{-12}}{2\times10^{-5}\ \mathrm{cm}}=5.18\times10^{-8}\ \mathrm{F/cm^2}=<<c>>\ \mathrm{fF/\mu m^2}\)." "\n" r"The PN-junction capacitance has exactly this form, \(\varepsilon_s/X_{dep}\), except that \(X_{dep}\) changes with bias.", c=g_(Ca * 1e7, 4)),
          tol=0.02, fig=fig_pn(), alt="PN junction with depletion region.", preview=["junction-cap"])
    s.mc(r"Preview of non-linear capacitors. Suppose a 'plate' isn't an ideal metal, so its charge spreads into a layer whose thickness grows with the applied voltage. What happens to the Q–V curve?",
         r"It becomes non-linear: the effective plate separation changes with \(V\), so \(Q/V\) and \(dQ/dV\) depend on bias",
         [r"It stays linear, \(Q=CV\)", r"The capacitance becomes zero", r"The charges on the two plates become unequal"],
         r"\(C=\varepsilon A/t\) assumes the charges sit at a fixed separation. If the charge layer thickens with \(V\), the charge centroid moves and the effective \(t\) changes, so \(Q(V)\) bends (reader Fig. 4.14–4.15). Charge neutrality still holds.",
         fig=fig_qv(lambda v: math.copysign(math.sqrt(abs(v)), v), -3, 3, "Non-linear Q–V"), alt="A curved Q-V characteristic.", preview=["nl-cap"])
    return s

# ====================================================================== nl-cap
def nl_cap():
    s = Skill('nl-cap')
    s.round(1)
    s.mc(r"For a non-linear capacitor with \(Q=f(V)\), the small-signal capacitance at a bias \(V_0\) is",
         r"\(C=\left.\dfrac{df}{dV}\right|_{V_0}\), the slope of the Q–V curve at the bias point",
         [r"\(C=f(V_0)/V_0\)", r"\(C=f(V_0)\)", r"The average slope from 0 to \(V_0\)"],
         r"Reader Eqs. 4.24–4.28: Taylor-expanding about \(V_0\), the small charge is \(q\approx\left.\dfrac{df}{dV}\right|_{V_0}v\), so \(C\) is the local slope. \(Q/V\) equals the slope only for a linear capacitor.",
         fig=fig_qv(lambda v: math.copysign(math.sqrt(abs(v)), v), -3, 3, bias=1.5), alt="Curved Q-V characteristic with a tangent line at the bias point labeled slope = C.")
    s.mc(r"For a non-linear capacitor, is \(Q/V\) at the bias point equal to the small-signal capacitance?",
         r"Not in general; only for a linear (straight-line through the origin) Q–V curve",
         [r"Yes, always", r"Yes, but only when \(V>0\)", r"Only for negative charge"],
         r"\(Q/V\) is the slope of the line from the origin to the bias point (a 'large-signal' average), while \(dQ/dV\) is the local tangent slope. They differ whenever the curve bends.",
         fig=fig_qv(lambda v: math.copysign(math.sqrt(abs(v)), v), -3, 3, bias=1.5), alt="Curved Q-V characteristic with a tangent line.")
    K, V = 2e-12, 1.5
    s.num(r"A device has \(Q(V)=KV^2\) with \(K=2\ \mathrm{pC/V^2}\). What is its small-signal capacitance at \(V=1.5\ \mathrm{V}\), in pF?",
          2 * K * V * 1e12, "pF",
          r"\(C=dQ/dV=2KV=2\times2\ \mathrm{pC/V^2}\times1.5\ \mathrm{V}=6\ \mathrm{pF}\). Note \(Q/V=KV=3\ \mathrm{pF}\), half the small-signal value.",
          tol=0.01, fig=fig_qv(lambda v: 2 * v * v, 0, 3, bias=1.5), alt="Parabolic Q-V curve with a tangent at 1.5 V.")
    s.round(2)
    Q0, phi, V = 2e-12, 0.8, -2.0
    Qf = lambda v: -Q0 * math.sqrt(1 - v / phi)
    C = Q0 / (2 * phi * math.sqrt(1 - V / phi))
    s.num(r"A junction stores \(Q_j(V)=-Q_0\sqrt{1-V/\phi_b}\) with \(Q_0=2\ \mathrm{pC}\), \(\phi_b=0.8\ \mathrm{V}\) (reader Eq. 4.29 form). What is its small-signal capacitance at \(V=-2\ \mathrm{V}\), in pF?",
          C * 1e12, "pF",
          T(r"\(C=\dfrac{dQ_j}{dV}=\dfrac{Q_0}{2\phi_b\sqrt{1-V/\phi_b}}\) (Eq. 4.30). At \(V=-2\): \(\sqrt{1+2.5}=1.871\), so \(C=\dfrac{2\ \mathrm{pC}}{1.6\ \mathrm{V}\times1.871}=<<c>>\ \mathrm{pF}\).", c=g_(C * 1e12, 4)),
          tol=0.02, fig=fig_qv(Qf, -4, 0.6, "Q_j(V) of a junction", bias=-2.0), alt="Junction charge versus voltage, a square-root curve, with a tangent at -2 V.")
    v = 10e-3
    s.num(r"At that bias (\(V=-2\ \mathrm{V}\), \(C=0.668\ \mathrm{pF}\)), a small signal \(v=10\ \mathrm{mV}\) is superimposed. How much small-signal charge \(q\) flows, in fC?",
          C * v * 1e15, "fC",
          T(r"\(q=C\,v=0.668\ \mathrm{pF}\times10\ \mathrm{mV}=<<q>>\ \mathrm{fC}\) (reader Eq. 4.27). The DC charge \(Q_j(-2\ \mathrm{V})\) stays as the 'operating point' part.", q=g_(C * v * 1e15, 4)),
          tol=0.02, fig=fig_qv(Qf, -4, 0.6, "Q_j(V) of a junction", bias=-2.0), alt="Junction Q-V curve with a tangent at -2 V.")
    QV = Qf(V) / V
    s.mc(r"For the same junction at \(V=-2\ \mathrm{V}\), which value is the small-signal capacitance?",
         T(r"<<c>> pF, the slope \(dQ/dV\)", c=g_(C * 1e12, 3)),
         [T(r"<<c>> pF, the ratio \(Q/V\)", c=g_(QV * 1e12, 3)), r"2 pF, the value of \(Q_0\)", r"0 pF, since the junction is reverse-biased"],
         T(r"\(Q_j(-2)=-2\times1.871=-3.74\ \mathrm{pC}\), so \(Q/V=<<r>>\ \mathrm{pF}\), a large-signal average. The small-signal value is the local slope, <<c>> pF. Reverse-biased junctions certainly have capacitance (the depletion charge moves with \(V\)).", r=g_(QV * 1e12, 3), c=g_(C * 1e12, 3)),
         fig=fig_qv(Qf, -4, 0.6, "Q_j(V) of a junction", bias=-2.0), alt="Junction Q-V curve with a tangent at -2 V.")
    s.round(3)
    s.mc(r"The junction above is biased at \(-2\ \mathrm{V}\) and driven by a 1 V-amplitude signal. Is \(q=C(-2\ \mathrm{V})\cdot v\) still accurate?",
         r"No: the Taylor expansion assumes \(|v|\) is small compared with the scale over which \(C\) changes; a 1 V swing changes \(C\) noticeably, so the charge response is distorted",
         [r"Yes: the small-signal capacitance works for any amplitude", r"Yes, as long as the signal is a sine wave", r"No, because the capacitance becomes negative"],
         r"The small-signal model keeps only the linear term of \(f(V_0+v)\) (reader Eq. 4.24). With \(|v|\) comparable to \(|V_0-\phi_b|\), higher-order terms matter: the charge is a distorted copy of the voltage. 'Small' means small enough that the slope is nearly constant over the swing.",
         fig=fig_qv(Qf, -4, 0.6, "Large swing on a curved Q–V", bias=-2.0), alt="Junction Q-V curve with a tangent at -2 V.")
    dQ = Qf(-1.0) - Qf(-2.0)
    s.num(r"Compute the EXACT charge change of the junction (\(Q_0=2\ \mathrm{pC}\), \(\phi_b=0.8\ \mathrm{V}\)) when \(V\) goes from \(-2\ \mathrm{V}\) to \(-1\ \mathrm{V}\), in pC.",
          dQ * 1e12, "pC",
          T(r"\(\Delta Q=Q_j(-1)-Q_j(-2)=-2\left[\sqrt{1+1.25}-\sqrt{1+2.5}\right]=-2[1.5-1.871]=<<d>>\ \mathrm{pC}\)." "\n" r"The small-signal estimate \(C(-2)\times1\ \mathrm{V}=0.668\ \mathrm{pC}\) is about 10% low, because \(C\) grows as the bias approaches \(\phi_b\).", d=g_(dQ * 1e12, 4)),
          tol=0.02, fig=fig_qv(Qf, -4, 0.6, "Q_j(V) of a junction"), alt="Junction Q-V curve.")
    s.mc(r"For \(C_j(V)=\dfrac{C_{j0}}{\sqrt{1-V/\phi_b}}\), what happens to the capacitance as the reverse bias increases (\(V\) more negative)?",
         r"It decreases, slowly (as \(1/\sqrt{\phi_b-V}\))",
         [r"It increases", r"It stays at \(C_{j0}\)", r"It drops linearly to zero at \(V=-\phi_b\)"],
         r"More reverse bias makes \(1-V/\phi_b\) larger, so \(C_j\) shrinks; doubling \(\phi_b-V\) only divides \(C\) by \(\sqrt2\). Physically the depletion region widens, so the 'plates' move apart.",
         fig=fig_cv(), alt="Plot of junction capacitance decreasing as reverse bias increases.")
    s.round(4)
    L, C0, phi, VR = 10e-9, 1e-12, 0.8, 3.0
    C3 = C0 / math.sqrt(1 + VR / phi)
    f3 = 1 / (2 * math.pi * math.sqrt(L * C3)) / 1e9
    s.num(r"Preview of varactors. A 10 nH inductor resonates with a junction capacitor \(C(V_R)=\dfrac{1\ \mathrm{pF}}{\sqrt{1+V_R/0.8\ \mathrm{V}}}\) (\(V_R\) = reverse bias). What is the resonant frequency \(f=\dfrac{1}{2\pi\sqrt{LC}}\) at \(V_R=3\ \mathrm{V}\), in GHz?",
          f3, "GHz",
          T(r"\(C=1/\sqrt{1+3.75}=1/2.179=<<c>>\ \mathrm{pF}\). Then \(f=\dfrac{1}{2\pi\sqrt{10^{-8}\times<<c>>\times10^{-12}}}=<<f>>\ \mathrm{GHz}\) (it was 1.59 GHz at 0 V)." "\n" r"A voltage-tuned capacitor tunes an oscillator, as in reader Sec. 5.5.5.", c=g_(C3 * 1e12, 4), f=g_(f3, 4)),
          tol=0.02, fig=fig_cv(mark=-3.0), alt="Junction capacitance versus bias with a marker at -3 V.", preview=["junction-cap"])
    tau, I = 1e-9, 1e-3
    Cd = tau * I / Vt * 1e12
    s.num(r"Preview of diffusion capacitance. A forward-biased diode stores charge \(Q(V)=\tau I_se^{V/V_t}\) with \(\tau=1\ \mathrm{ns}\), and at the bias point \(I=I_se^{V/V_t}=1\ \mathrm{mA}\) (\(V_t=25.9\ \mathrm{mV}\)). What is \(dQ/dV\) there, in pF?",
          Cd, "pF",
          T(r"\(\dfrac{dQ}{dV}=\dfrac{\tau I_se^{V/V_t}}{V_t}=\dfrac{\tau I}{V_t}=\dfrac{10^{-9}\times10^{-3}}{0.0259}=<<c>>\ \mathrm{pF}\)." "\n" r"Same definition, new charge function: the diode small-signal skill calls this the diffusion capacitance.", c=g_(Cd, 4)),
          tol=0.02, fig=fig_qv(lambda v: math.exp(v / 0.0259 * 0.25), 0, 1.0, "Exponential Q–V", bias=0.8), alt="Exponentially rising Q-V curve with a tangent.", preview=["diode-ss"])
    s.mc(r"Preview of junction capacitance. \(C_j=\dfrac{C_{j0}}{\sqrt{1-V/\phi_b}}\) predicts infinite capacitance at \(V=\phi_b\) (forward bias). How should you read that?",
         r"As a breakdown of the model: the assumptions behind the \(Q(V)\) formula fail near \(V=\phi_b\), so it can't be trusted there",
         [r"The junction really has infinite capacitance at \(\phi_b\)", r"The capacitance becomes zero at \(\phi_b\)", r"The formula is exact for all \(V\)"],
         r"Taking the derivative of a model is only as good as the model. The square-root charge law comes from an approximation that fails as the depletion region collapses in forward bias; the reader instead uses a practical estimate for forward-biased junctions in the diode chapter.",
         fig=fig_cv(), alt="Junction capacitance versus bias.", preview=["junction-cap", "diode-ss"])
    return s

# ====================================================================== junction-cap
def junction_cap():
    s = Skill('junction-cap')
    s.round(1)
    s.mc(r"Increasing the reverse bias on a PN junction does what to its depletion capacitance \(C_j\)?",
         r"Decreases it, because the depletion region widens",
         [r"Increases it", r"Has no effect", r"Makes it negative"],
         r"\(C_j=\varepsilon_s/X_{dep}\) (reader Eq. 5.63) and \(X_{dep}\propto\sqrt{\phi_{bi}-V_D}\) grows with reverse bias. Wider 'plate' spacing means less capacitance: that's what makes a varactor.",
         fig=fig_cv(), alt="Junction capacitance decreasing with reverse bias.")
    cj0, phi, VD = 1.0, 0.8, -2.4
    s.num(r"A junction has \(C_{j0}=1\ \mathrm{pF}\) and \(\phi_{bi}=0.8\ \mathrm{V}\). What is \(C_j\) at \(V_D=-2.4\ \mathrm{V}\), in pF?",
          cj0 / math.sqrt(1 - VD / phi), "pF",
          r"\(C_j=\dfrac{C_{j0}}{\sqrt{1-V_D/\phi_{bi}}}=\dfrac{1}{\sqrt{1+3}}=0.5\ \mathrm{pF}\) (reader Eq. 5.60).",
          tol=0.01, fig=fig_cv(mark=-2.4), alt="Junction capacitance versus bias with a marker at -2.4 V.")
    s.mc(r"The reader interprets the depletion capacitance as \(C_j=\varepsilon_s/X_{dep}\) per area. What does that mean physically?",
         r"Small charge changes happen at the two EDGES of the depletion region, separated by \(X_{dep}\), as if metal plates sat there with silicon as the dielectric",
         [r"The charge is stored uniformly throughout the N region", r"The P and N regions are insulators", r"The capacitance comes from free electrons crossing the junction"],
         r"When \(V_D\) changes slightly, the depletion region grows or shrinks at its edges \(-x_p\) and \(x_n\); the incremental charges sit \(X_{dep}\) apart (reader Sec. 5.5.4). That's why the parallel-plate form works, with a bias-dependent spacing.",
         fig=fig_pn(), alt="PN junction with the depletion region between -xp and xn.")
    s.round(2)
    NA, ND, phi = 1e17, 1e16, 0.775
    Cj0 = math.sqrt(q * es * NA * ND / (2 * phi * (NA + ND)))
    s.num(r"An abrupt junction has \(N_A=10^{17}\ \mathrm{cm^{-3}}\), \(N_D=10^{16}\ \mathrm{cm^{-3}}\), \(\phi_{bi}=0.775\ \mathrm{V}\). Using \(C_{j0}=\sqrt{\dfrac{q\varepsilon_s}{2\phi_{bi}}\dfrac{N_AN_D}{N_A+N_D}}\) (reader Eq. 5.61), what is \(C_{j0}\) in \(\mathrm{fF/\mu m^2}\)?",
          Cj0 * 1e7, "fF/µm²",
          T(r"\(\dfrac{N_AN_D}{N_A+N_D}=9.09\times10^{15}\ \mathrm{cm^{-3}}\). \(q\varepsilon_s=1.602\times10^{-19}\times1.036\times10^{-12}=1.66\times10^{-31}\)." "\n" r"\(C_{j0}=\sqrt{\dfrac{1.66\times10^{-31}\times9.09\times10^{15}}{1.55}}=<<c>>\ \mathrm{F/cm^2}=<<f>>\ \mathrm{fF/\mu m^2}\).", c=tex(Cj0, 3), f=g_(Cj0 * 1e7, 3)),
          tol=0.02, fig=fig_pn(), alt="Abrupt PN junction.")
    X0 = es / Cj0 * 1e4
    s.num(r"For the same junction, what is the zero-bias depletion width \(X_{dep0}=\varepsilon_s/C_{j0}\), in µm?",
          X0, "µm",
          T(r"\(X_{dep0}=\dfrac{1.036\times10^{-12}}{3.12\times10^{-8}}=3.32\times10^{-5}\ \mathrm{cm}=<<x>>\ \mu\mathrm{m}\) (reader Eq. 5.62). Most of it lies on the lightly doped N side.", x=g_(X0, 3)),
          tol=0.02, fig=fig_pn(), alt="Abrupt PN junction.")
    s.mc(r"In a one-sided junction with \(N_A\gg N_D\), which doping mainly sets \(C_{j0}\)?",
         r"The lighter doping \(N_D\): \(\dfrac{N_AN_D}{N_A+N_D}\approx N_D\)",
         [r"The heavier doping \(N_A\)", r"Both equally: \(C_{j0}\propto N_A+N_D\)", r"Neither: \(C_{j0}\) depends only on area"],
         r"The 'series' combination \(\dfrac{N_AN_D}{N_A+N_D}\) is dominated by the smaller one, just as the depletion region extends mostly into the lightly doped side. So \(C_{j0}\approx\sqrt{\dfrac{q\varepsilon_sN_D}{2\phi_{bi}}}\).",
         fig=fig_pn(), alt="Abrupt PN junction.")
    s.round(3)
    r = math.sqrt((0.8 + 1) / (0.8 + 2))
    s.mc(r"With \(\phi_{bi}=0.8\ \mathrm{V}\), the reverse bias is doubled from 1 V to 2 V. How does \(C_j\) change?",
         T(r"It falls by only about <<p>>%, to \(\sqrt{1.8/2.8}=<<r>>\) of its value", p=g_((1 - r) * 100, 2), r=g_(r, 3)),
         [r"It halves", r"It falls to \(1/\sqrt2=0.707\) of its value", r"It doubles"],
         T(r"\(C_j\propto(\phi_{bi}-V_D)^{-1/2}\), and \(\phi_{bi}-V_D\) goes from 1.8 V to 2.8 V, not a factor of 2. Ratio \(=\sqrt{1.8/2.8}=<<r>>\)." "\n" r"Gotcha: forgetting \(\phi_{bi}\) gives the \(1/\sqrt2\) answer.", r=g_(r, 3)),
         fig=fig_cv(), alt="Junction capacitance versus bias.")
    VR = 8 * 0.8
    s.num(r"With \(\phi_{bi}=0.8\ \mathrm{V}\), what reverse-bias magnitude \(V_R=-V_D\) makes \(C_j=C_{j0}/3\), in V?",
          VR, "V",
          r"\(\sqrt{1+V_R/\phi_{bi}}=3\Rightarrow1+V_R/0.8=9\Rightarrow V_R=6.4\ \mathrm{V}\)." "\n" r"Cutting \(C\) by 3 needs a 9× larger \(\phi_{bi}-V_D\); varactor tuning ranges are limited by this square-root law. Common mistake: \(V_R=2\phi_{bi}\).",
          tol=0.01, fig=fig_cv(), alt="Junction capacitance versus bias.")
    s.mc(r"In the formula \(C_j=\varepsilon_s/X_{dep}\), what distance is \(X_{dep}\)?",
         r"The total depletion width \(x_p+x_n\) at the bias point",
         [r"Only \(x_n\), the N-side width", r"Only \(x_p\), the P-side width", r"The distance between the two metal contacts"],
         r"The incremental charges appear at both edges, \(-x_p\) and \(x_n\), so the effective plate spacing is \(X_{dep}=x_p+x_n\) (reader Eq. 5.54, 5.62). The contacts are far away in the neutral regions, which conduct.",
         fig=fig_pn(), alt="PN junction depletion region between -xp and xn.")
    s.round(4)
    A, cj0a, VR, phi = 20.0, 1.0, 1.8, 0.8
    C = A * cj0a / math.sqrt(1 + VR / phi)
    s.num(r"Preview of MOSFET capacitances. A transistor's drain diffusion forms a \(20\ \mu\mathrm{m^2}\) junction with the body, \(C_{j0}=1\ \mathrm{fF/\mu m^2}\), \(\phi_{bi}=0.8\ \mathrm{V}\), reverse-biased by 1.8 V. What is its capacitance, in fF?",
          C, "fF",
          T(r"\(C=\dfrac{20\times1\ \mathrm{fF}}{\sqrt{1+1.8/0.8}}=\dfrac{20}{1.803}=<<c>>\ \mathrm{fF}\)." "\n" r"Every MOSFET drain and source has such a junction; they show up as \(C_{DB}\) and \(C_{SB}\), which slow down circuits.", c=g_(C, 4)),
          tol=0.02, fig=fig_cv(mark=-1.8), alt="Junction capacitance versus bias with a marker at -1.8 V.", preview=["mos-caps"])
    cj0, phi, VR, R = 2e-12, 0.8, 3.0, 1e3
    C = cj0 / math.sqrt(1 + VR / phi)
    fc = 1 / (2 * math.pi * R * C) / 1e6
    s.num(r"Preview of the diode small-signal model. A reverse-biased diode (\(C_{j0}=2\ \mathrm{pF}\), \(\phi_{bi}=0.8\ \mathrm{V}\), \(V_R=3\ \mathrm{V}\)) acts as just a capacitor. Driven through \(1\ \mathrm{k\Omega}\), what is the RC corner frequency \(1/(2\pi RC_j)\), in MHz?",
          fc, "MHz",
          T(r"\(C_j=\dfrac{2}{\sqrt{1+3.75}}=0.918\ \mathrm{pF}\). \(f_c=\dfrac{1}{2\pi\times10^3\times0.918\times10^{-12}}=<<f>>\ \mathrm{MHz}\)." "\n" r"In forward bias the diode model adds a conductance and a second capacitance; that's next.", f=g_(fc, 4)),
          tol=0.02, fig=b2b_svg(300, 110, b2b_vsource(30, 25, 60, "vₛ") + b2b_wire(30, 25, 60, 25) + b2b_resistor(60, 25, 60, label="1 kΩ") + b2b_wire(120, 25, 170, 25) + b2b_capacitor(170, 25, 60, horiz=False, label="C_j(V_R)") + b2b_wire(30, 85, 170, 85) + b2b_ground(100, 85), "Reverse-biased diode as a capacitor"),
          alt="Source driving a 1 kΩ resistor into a junction capacitance to ground.", preview=["diode-ss"])
    s.mc(r"Preview of MOSFET capacitances. Which change REDUCES the junction capacitance of a transistor's drain region?",
         r"Making the junction area smaller (and/or increasing its reverse bias)",
         [r"Making the area larger", r"Forward-biasing the junction", r"Increasing the doping of the lightly doped side"],
         r"\(C=A\cdot C_{j0}/\sqrt{1-V_D/\phi_{bi}}\): smaller area and more reverse bias both help. Forward bias increases \(C_j\). Heavier doping on the light side shrinks \(X_{dep}\) and raises \(C_{j0}\propto\sqrt{N}\). Layout tricks such as sharing drains cut \(C_{DB}\).",
         fig=fig_pn(), alt="PN junction.", preview=["mos-caps"])
    return s

BUILD = [electrostatics, mim_cap, nl_cap, junction_cap]
if __name__ == "__main__":
    for fn in BUILD:
        sk = fn(); sk.save(); print("wrote", sk.sid, len(sk.qs))
