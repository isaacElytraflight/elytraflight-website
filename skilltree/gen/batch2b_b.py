"""batch2b group B: gbw, opamp-fr, fb-errors, fb-impedance, stability"""
from batch2b_lib import *

def g_(x, n=4):
    return f"{x:.{n}g}"

def bisect(fn, a, b, it=200):
    fa = fn(a)
    for _ in range(it):
        m = 0.5 * (a + b); fm = fn(m)
        if (fa < 0) == (fm < 0): a, fa = m, fm
        else: b = m
    return 0.5 * (a + b)

def bisect_log(fn, a, b):
    return 10 ** bisect(lambda lx: fn(10 ** lx), math.log10(a), math.log10(b))

def bode_ol(a0db=100, fp=10, fu=1e6, fmin=1, fmax=1e7, extra=lambda X, Y: "", title="Open-loop gain |A| (asymptotic)", dbmax=None):
    return fig_bode_mag([(fmin, a0db), (fp, a0db), (fu, 0)], fmin, fmax, dbmax or a0db * 1.15, extra=extra, title=title)

def bode_ol_cl(a0db, fp, fu, cldb, fmin=1, fmax=1e7, title="Open-loop and closed-loop gain"):
    fcl = fu / 10 ** (cldb / 20)
    def ex(X, Y):
        return (b2b_poly([(X(fmin), Y(cldb)), (X(fcl), Y(cldb))], sw=2.2, dash=True) +
                b2b_text(X(fmin) + 6, Y(cldb) - 6, "closed loop", size=10, anchor="start") +
                b2b_text(X(fp) + 6, Y(a0db) - 6, "open loop A", size=10, anchor="start") +
                b2b_line(X(fcl), Y(cldb) + 4, X(fcl), Y(0), dash=True, op=0.5))
    return fig_bode_mag([(fmin, a0db), (fp, a0db), (fu, 0)], fmin, fmax, a0db * 1.15, extra=ex, title=title)

def fig_step(kind="exp", title="Follower step response"):
    x0, y0, W, H = 40, 120, 270, 90
    b = b2b_axes(x0, y0, W, H, "t", "vₒ")
    b += b2b_poly([(x0, y0), (x0 + 15, y0), (x0 + 15, y0 - 80), (x0 + W - 10, y0 - 80)], dash=True)
    b += b2b_text(x0 + W - 10, y0 - 84, "input step", size=10, anchor="end")
    if kind == "exp":
        b += b2b_curve(lambda t: 80 * (1 - math.exp(-t / 35)), 0, W - 25, x0 + 15, y0, 1, 1, sw=2.2)
    else:
        pts = [(x0 + 15, y0), (x0 + 95, y0 - 64)]
        pts += [(x0 + 95 + t, y0 - (64 + 16 * (1 - math.exp(-t / 20)))) for t in range(0, W - 105, 5)]
        b += b2b_poly(pts, sw=2.2) + b2b_text(x0 + 52, y0 - 46, "slope = SR", size=10, anchor="end")
    return b2b_svg(330, 140, b, title)

# ====================================================================== gbw
def gbw():
    s = Skill('gbw')
    s.round(1)
    s.mc(r"On an op-amp's open-loop Bode plot, the unity-gain frequency \(\omega_u\) is",
         r"the frequency at which \(|A(j\omega)|=1\) (0 dB)",
         [r"the \(-3\ \mathrm{dB}\) frequency of the open-loop gain", r"the frequency at which the phase reaches \(-180^\circ\)", r"the frequency at which \(|A|\) has dropped to half its DC value"],
         r"\(\omega_u\) is where the open-loop magnitude crosses 0 dB (reader Eq. 17.19). For a single-pole op-amp, \(\omega_u\approx A_0\,\omega_{-3dB}\), which is why it is also called the gain-bandwidth product." "\n" r"• The \(-3\) dB frequency is the (much lower) dominant pole." "\n" r"• A single pole never reaches \(-180^\circ\)." "\n" r"• Half the DC gain is the \(-6\) dB point, near the pole.",
         fig=bode_ol(extra=lambda X, Y: b2b_text(X(1e6), Y(0) + 14, "ω_u", size=11)), alt="Asymptotic Bode magnitude of an op-amp: flat at 100 dB to 10 Hz, falling 20 dB/decade, crossing 0 dB at 1 MHz.")
    s.mc(r"Closing a feedback loop around a single-pole op-amp with DC loop gain \(T_0\) does what to the DC gain and the bandwidth?",
         r"Divides the gain by \(1+T_0\) and multiplies the bandwidth by \(1+T_0\), so gain × bandwidth is unchanged",
         [r"Multiplies both the gain and the bandwidth by \(1+T_0\)", r"Divides both the gain and the bandwidth by \(1+T_0\)", r"Leaves the bandwidth unchanged and lowers the gain"],
         r"From \(G_{CL}=\dfrac{A_0/(1+T_0)}{1+j\omega\tau/(1+T_0)}\) (reader Eq. 17.26), the DC gain falls by \(1+T_0\) and the pole moves up by \(1+T_0\). Their product, the gain-bandwidth, stays at \(\approx\omega_u\): you can trade gain for bandwidth but not get both.",
         fig=bode_ol_cl(100, 10, 1e6, 40), alt="Bode sketch: open-loop gain 100 dB with a 10 Hz pole, and a closed-loop gain of 40 dB that stays flat out to 10 kHz where it meets the open-loop line.")
    A0, fp = 1e5, 10.0
    s.num(r"An op-amp has DC gain \(A_0=10^5\) (100 dB) and a dominant pole at \(f_{-3dB}=10\ \mathrm{Hz}\). What is its unity-gain frequency \(f_u\), in MHz?",
          A0 * fp / 1e6, "MHz",
          r"\(f_u\approx A_0\,f_{-3dB}=10^5\times10\ \mathrm{Hz}=10^6\ \mathrm{Hz}=1\ \mathrm{MHz}\) (reader Eq. 17.21)." "\n" r"On the Bode plot: 100 dB must be lost at 20 dB/decade, i.e. 5 decades above 10 Hz.",
          tol=0.01, fig=bode_ol(), alt="Bode magnitude: 100 dB flat to 10 Hz then falling at 20 dB per decade.")
    s.round(2)
    fu, G = 10e6, 20.0
    s.num(r"An op-amp with \(f_u=10\ \mathrm{MHz}\) is used in a non-inverting amplifier with gain 20 (\(f=0.05\)). What is the closed-loop bandwidth, in kHz?",
          fu / G / 1e3, "kHz",
          r"Closed-loop bandwidth \(\approx f\cdot f_u=0.05\times10\ \mathrm{MHz}=500\ \mathrm{kHz}\) (reader Eq. 17.27–17.29)." "\n" r"Check: gain × bandwidth \(=20\times500\ \mathrm{kHz}=10\ \mathrm{MHz}=f_u\). Common mistake: dividing \(f_u\) by \(1+20\).",
          tol=0.01, fig=fig_noninverting("R₁", "R₂ = 19 R₁"), alt="Non-inverting amplifier with gain 20.")
    fu, fp, f = 5e6, 20.0, 50e3
    A0 = fu / fp
    mag = A0 / math.sqrt(1 + (f / fp) ** 2)
    s.num(r"An op-amp has \(f_u=5\ \mathrm{MHz}\) and a dominant pole at 20 Hz. What is its open-loop gain magnitude \(|A|\) at 50 kHz?",
          mag, "V/V",
          T(r"Far above the pole, \(A(j\omega)\approx\dfrac{\omega_u}{j\omega}\) (reader Eq. 17.22), so \(|A|\approx\dfrac{f_u}{f}=\dfrac{5\ \mathrm{MHz}}{50\ \mathrm{kHz}}=100\)." "\n" r"Exact: \(A_0=f_u/f_p=2.5\times10^5\) and \(|A|=\dfrac{A_0}{\sqrt{1+(50000/20)^2}}=<<m>>\). The open-loop gain at signal frequencies can be far below the datasheet's DC gain.", m=g_(mag, 6)),
          tol=0.01, fig=bode_ol(108, 20, 5e6, 1, 1e8), alt="Asymptotic Bode magnitude: about 108 dB to 20 Hz, falling to 0 dB at 5 MHz.")
    s.mc(r"A unity-gain follower (\(f=1\)) uses an op-amp with unity-gain frequency \(f_u\). What is the closed-loop bandwidth?",
         r"About \(f_u\): the follower uses the full gain-bandwidth",
         [r"About \(f_u/2\)", r"The op-amp's open-loop \(-3\ \mathrm{dB}\) frequency", r"Infinite, since the gain is 1"],
         r"Closed-loop bandwidth \(\approx f\cdot f_u\), and \(f=1\) for a follower, so the bandwidth is \(\approx f_u\) (reader Sec. 17.5.6 and Fig. 17.18). It is the widest-band configuration because it has the lowest gain." "\n" r"• \(f_u/2\) is the bandwidth of a gain \(-1\) INVERTING stage (noise gain 2)." "\n" r"• The open-loop pole is \(1+T_0\) times lower.",
         fig=fig_follower(), alt="Unity-gain follower: input to the + terminal, output tied directly to the − terminal.")
    s.round(3)
    s.mc(r"A (weak) op-amp has \(A_0=10\) and a single pole at 1 MHz, so \(A_0f_{-3dB}=10\ \mathrm{MHz}\). It is connected as a unity-gain follower. What is the closed-loop \(-3\ \mathrm{dB}\) bandwidth?",
         r"11 MHz",
         [r"10 MHz", r"1 MHz", r"0.91 MHz"],
         r"Exactly, the pole moves to \((1+T_0)f_{-3dB}=(1+10\cdot1)\times1\ \mathrm{MHz}=11\ \mathrm{MHz}\) (reader Eq. 17.27), with DC gain \(10/11=0.909\)." "\n" r"The shortcut 'bandwidth \(=f\cdot f_u\)' assumes \(T_0\gg1\) (it replaces \(1+T_0\) by \(T_0\)); with \(T_0=10\) it is 10% off. Gain × bandwidth is still \(0.909\times11=10\ \mathrm{MHz}\).",
         fig=fig_follower(), alt="Unity-gain follower built with an op-amp of DC gain 10.")
    fu, Gs = 10e6, 10.0
    f1 = fu / Gs
    fbw = f1 * math.sqrt(math.sqrt(2) - 1)
    s.num(r"You need a gain of 100. Option 1: one non-inverting stage of gain 100. Option 2: two cascaded stages of gain 10 each. Each op-amp has \(f_u=10\ \mathrm{MHz}\). What is the \(-3\ \mathrm{dB}\) bandwidth of Option 2, in kHz? (Option 1 gives 100 kHz.)",
          fbw / 1e3, "kHz",
          T(r"Each gain-10 stage has a single pole at \(f_u/10=1\ \mathrm{MHz}\). Cascaded, \(|H|=\dfrac{100}{1+(f/1\ \mathrm{MHz})^2}\), which is \(1/\sqrt2\) of its DC value when \(1+(f/f_1)^2=\sqrt2\):" "\n" r"\[f_{-3dB}=f_1\sqrt{\sqrt2-1}=0.6436\times1\ \mathrm{MHz}=<<b>>\ \mathrm{kHz}\]" "\n" r"Splitting the gain wins a 6.4× wider bandwidth, but NOT the naive 1 MHz: two equal poles each contribute \(-1.5\ \mathrm{dB}\) at \(0.64f_1\). Common mistake: answering 1000 kHz.", b=g_(fbw / 1e3, 4)),
          tol=0.02, fig=b2b_svg(360, 80, b2b_text(16, 39, "vᵢₙ") + b2b_arrow(28, 35, 70, 35) + b2b_box(70, 15, 90, 40, "×10") + b2b_arrow(160, 35, 200, 35) + b2b_box(200, 15, 90, 40, "×10") + b2b_text(180, 70, "each stage: op-amp with f_u = 10 MHz", size=10) + b2b_arrow(290, 35, 330, 35) + b2b_text(340, 39, "vₒ", anchor="start"), "Two-stage cascade"),
          alt="Two gain-of-10 amplifier stages in cascade, each built from an op-amp with 10 MHz unity-gain frequency.")
    s.mc(r"An OTA (no output buffer) with internal capacitance \(C_x\) drives a load capacitor \(C_L=4C_x\) directly. How does its gain-bandwidth product compare with the unloaded value \(G_m/C_x\)?",
         r"It drops by a factor of 5, to \(G_m/(C_x+C_L)\)",
         [r"It is unchanged; the GBW depends only on \(G_m\) and \(C_x\)", r"It drops by a factor of 4", r"It increases by a factor of 5"],
         r"Without a buffer, the load capacitance sits in parallel with \(C_x\) at the high-impedance node, so the pole becomes \(\dfrac{1}{R_x(C_x+C_L)}\) (reader Eq. 17.18; the printed form '\(\frac{1}{R_x}(C_x+C_L)\)' is missing parentheses). The DC gain \(G_mR_x\) is unchanged, so GBW \(=\dfrac{G_m}{C_x+C_L}=\dfrac{G_m}{5C_x}\)." "\n" r"• 'Unchanged' would be true with an ideal buffer isolating \(C_L\)." "\n" r"• The total is \(C_x+4C_x=5C_x\), not \(4C_x\).",
         fig=fig_gm_load(), alt="OTA driving a node with Rx, Cx and an external load capacitor CL all to ground; no output buffer.")
    s.round(4)
    fu, R2R1, f = 1e6, 9.0, 300e3
    fcl = fu / (1 + R2R1)
    mag = R2R1 / math.sqrt(1 + (f / fcl) ** 2)
    s.num(r"Preview of closed-loop frequency response. An inverting amplifier with \(R_2/R_1=9\) uses an op-amp with \(f_u=1\ \mathrm{MHz}\). Its closed-loop response is one-pole with the pole at \(f_u/(1+R_2/R_1)\). What is \(|v_o/v_s|\) at 300 kHz?",
          mag, "V/V",
          T(r"Closed-loop pole: \(\dfrac{1\ \mathrm{MHz}}{1+9}=100\ \mathrm{kHz}\) (the 'noise gain' \(1+R_2/R_1=1/f\) sets it, not \(R_2/R_1\))." "\n" r"\(|H|=\dfrac{9}{\sqrt{1+(300/100)^2}}=\dfrac{9}{\sqrt{10}}=<<m>>\)." "\n" r"The op-amp frequency-response skill applies this to real inverting and non-inverting amplifiers.", m=g_(mag, 4)),
          tol=0.02, fig=fig_inverting("R₁", "R₂ = 9 R₁"), alt="Inverting amplifier with R2 = 9 R1 using a 1 MHz op-amp.", preview=["opamp-fr"])
    A0, fp1, fp2, f, fb = 1e5, 100.0, 5e6, 1e6, 0.1
    ph = -math.degrees(math.atan(f / fp1) + math.atan(f / fp2))
    s.num(r"Preview of stability. An op-amp has \(A_0=10^5\), a dominant pole at 100 Hz (so \(f_u=10\ \mathrm{MHz}\)) and a second pole at 5 MHz. With \(f=0.1\) the loop gain \(T=Af\) crosses unity near \(f\cdot f_u=1\ \mathrm{MHz}\). What is the phase of \(T\) at 1 MHz, in degrees?",
          ph, "degrees",
          T(r"\(\angle T=-\tan^{-1}\!\dfrac{1\ \mathrm{MHz}}{100\ \mathrm{Hz}}-\tan^{-1}\!\dfrac{1\ \mathrm{MHz}}{5\ \mathrm{MHz}}=-89.99^\circ-11.31^\circ=<<p>>^\circ\)." "\n" r"The loop is about \(79^\circ\) away from \(-180^\circ\) where \(|T|=1\): that margin is what the stability skill calls phase margin. Lowering the gain toward a follower (\(f=1\)) pushes the crossover up toward the 5 MHz pole and eats the margin.", p=g_(ph, 4)),
          tol=0.02, fig=bode_ol(100, 100, 10e6, 1, 1e8, extra=lambda X, Y: b2b_text(X(5e6), Y(0) - 12, "2nd pole 5 MHz", size=10)), alt="Open-loop Bode magnitude: 100 dB to 100 Hz, then -20 dB/decade, with a second pole marked at 5 MHz.", preview=["stability"])
    fu = 1e6
    slope = 1.0 * 2 * math.pi * fu / 1e6
    s.mc(r"Preview of slew rate. A follower built from an op-amp with \(f_u=1\ \mathrm{MHz}\) responds to a small step linearly: \(v_o(t)=V_i(1-e^{-\omega_ut})\). For a \(V_i=1\ \mathrm{V}\) step, what initial slope \(dv_o/dt\) would the linear model demand?",
         r"\(6.28\ \mathrm{V/\mu s}\)",
         [r"\(1\ \mathrm{V/\mu s}\)", r"\(0.159\ \mathrm{V/\mu s}\)", r"\(62.8\ \mathrm{V/\mu s}\)"],
         T(r"The follower's time constant is \(\tau=1/\omega_u\) (bandwidth = full GBW). The initial slope is \(V_i\,\omega_u=1\ \mathrm{V}\times2\pi\times10^6\ \mathrm{s^{-1}}=<<s>>\ \mathrm{V/\mu s}\) (reader Eq. 18.20)." "\n" r"• \(1\ \mathrm{V/\mu s}\) forgets the \(2\pi\)." "\n" r"• \(0.159\ \mathrm{V/\mu s}\) divides by \(2\pi\) instead." "\n" r"If the op-amp's maximum slew rate is below this, the output ramps at the slew rate instead: the next skills explain when that happens.", s=g_(slope, 3)),
         fig=fig_step("exp"), alt="Step input and the exponential output of a follower.", preview=["slew"])
    return s

def fig_gm_load():
    b = (b2b_text(18, 49, "v⁺") + b2b_circle(30, 45, 3) + b2b_wire(33, 45, 60, 45) + b2b_text(18, 99, "v⁻") + b2b_circle(30, 95, 3) + b2b_wire(33, 95, 60, 95) +
         b2b_box(60, 35, 60, 70, "Gm") + b2b_wire(120, 70, 280, 70) +
         b2b_dot(160, 70) + b2b_resistor(160, 70, 60, horiz=False, label="Rₓ", lpos=(172, 104)) + b2b_ground(160, 130) +
         b2b_dot(210, 70) + b2b_capacitor(210, 70, 60, horiz=False, label="Cₓ") + b2b_ground(210, 130) +
         b2b_dot(260, 70) + b2b_capacitor(260, 70, 60, horiz=False, label="C_L") + b2b_ground(260, 130) +
         b2b_circle(283, 70, 3) + b2b_text(296, 74, "vₒ", anchor="start"))
    return b2b_svg(330, 160, b, "OTA driving a capacitive load")

# ====================================================================== opamp-fr
def opamp_fr():
    s = Skill('opamp-fr')
    s.round(1)
    s.mc(r"For a single-pole op-amp \(A(j\omega)=\dfrac{A_0}{1+j\omega/\omega_{-3dB}}\), what is the phase of \(A\) at frequencies far above \(\omega_{-3dB}\)?",
         r"About \(-90^\circ\)",
         [r"About \(-180^\circ\)", r"About \(-45^\circ\)", r"About \(0^\circ\)"],
         r"For \(\omega\gg\omega_{-3dB}\), \(A\approx\dfrac{\omega_u}{j\omega}\) (reader Eq. 18.8): dividing by \(j\) is a \(-90^\circ\) phase shift. It is exactly \(-45^\circ\) only AT the pole, and a single pole can never reach \(-180^\circ\).",
         fig=bode_ol(), alt="Op-amp open-loop Bode magnitude with a dominant pole at 10 Hz and unity gain at 1 MHz.")
    A0, fp, f = 2e5, 5.0, 10e3
    mag = A0 / math.sqrt(1 + (f / fp) ** 2)
    s.num(r"An op-amp has \(A_0=2\times10^5\) and \(f_{-3dB}=5\ \mathrm{Hz}\). What is \(|A|\) at 10 kHz?",
          mag, "V/V",
          T(r"\(f_u=A_0f_{-3dB}=1\ \mathrm{MHz}\). Far above the pole \(|A|\approx f_u/f=10^6/10^4=100\)." "\n" r"Exact: \(\dfrac{2\times10^5}{\sqrt{1+2000^2}}=<<m>>\). A '106 dB' op-amp has only 40 dB of gain at 10 kHz.", m=g_(mag, 6)),
          tol=0.01, fig=bode_ol(106, 5, 1e6, 1, 1e7), alt="Open-loop Bode magnitude: 106 dB to 5 Hz, then -20 dB/decade to 0 dB at 1 MHz.")
    s.mc(r"An inverting amplifier (\(R_1\), \(R_2\)) uses a single-pole op-amp with unity-gain frequency \(\omega_u\). Its closed-loop bandwidth is approximately",
         r"\(\omega_0=\dfrac{\omega_u}{1+R_2/R_1}\)",
         [r"\(\omega_0=\dfrac{\omega_u}{R_2/R_1}\)", r"\(\omega_0=\omega_u\,(1+R_2/R_1)\)", r"\(\omega_0=\omega_{-3dB}\), unchanged by feedback"],
         r"Reader Eq. 18.15: \(\omega_0=\dfrac{A_0\omega_{-3dB}}{1+R_2/R_1}=\dfrac{\omega_u}{1+R_2/R_1}\). The factor \(1+R_2/R_1=1/f\) (the 'noise gain') appears, not the signal gain \(R_2/R_1\); for large gains the two are nearly equal, which is why the reader concludes GBW \(\approx\omega_u\) (Eq. 18.16)." "\n" r"• Multiplying would make high gain faster, which is backwards." "\n" r"• Feedback does extend the bandwidth beyond the open-loop pole.",
         fig=fig_inverting("R₁", "R₂"), alt="Inverting amplifier with R1 and R2 (Fig. 18.8 style).")
    s.round(2)
    A0, k = 1e4, 4.0
    ans = -k / (1 + (1 + k) / A0)
    s.num(r"An inverting amplifier has \(R_2/R_1=4\) and an op-amp with DC gain \(A_0=10^4\). Using \(G=-\dfrac{R_2}{R_1}\cdot\dfrac{1}{1+(1+R_2/R_1)/A}\) (reader Eq. 18.9), what is the DC gain?",
          ans, "V/V",
          T(r"\(G=-4\cdot\dfrac{1}{1+5/10^4}=-4\times0.9995=<<a>>\)." "\n" r"The error \(\approx(1+R_2/R_1)/A_0=0.05\%\) is the familiar \(1/T\) with \(T=A_0f\), \(f=1/5\).", a=g_(ans, 5)),
          tol=0.005, fig=fig_inverting("R₁", "R₂ = 4 R₁"), alt="Inverting amplifier with R2 = 4 R1.")
    fu = 2e6
    s.num(r"Same amplifier (\(R_2/R_1=4\)), op-amp \(f_u=2\ \mathrm{MHz}\). What is the closed-loop \(-3\ \mathrm{dB}\) frequency, in kHz?",
          fu / (1 + k) / 1e3, "kHz",
          r"\(f_0=\dfrac{f_u}{1+R_2/R_1}=\dfrac{2\ \mathrm{MHz}}{5}=400\ \mathrm{kHz}\)." "\n" r"Common mistake: dividing by 4 (500 kHz); the noise gain \(1+R_2/R_1=5\) sets the bandwidth.",
          tol=0.01, fig=fig_inverting("R₁", "R₂ = 4 R₁"), alt="Inverting amplifier with R2 = 4 R1 and a 2 MHz op-amp.")
    s.mc(r"For the inverting amplifier (\(R_2/R_1=4\), closed-loop pole \(f_0=400\ \mathrm{kHz}\)), what is the phase of \(v_o/v_s\) at \(f=f_0\)?",
         r"\(+135^\circ\) (equivalently \(-225^\circ\)): \(180^\circ\) from the inversion plus \(-45^\circ\) from the pole",
         [r"\(-45^\circ\)", r"\(+180^\circ\)", r"\(-90^\circ\)"],
         r"\(G(j\omega)\approx-\dfrac{R_2}{R_1}\cdot\dfrac{1}{1+j\omega/\omega_0}\) (reader Eq. 18.14). The minus sign is \(\pm180^\circ\); at \(\omega=\omega_0\) the pole adds \(-45^\circ\). Total \(180^\circ-45^\circ=135^\circ\)." "\n" r"• \(-45^\circ\) forgets the inversion." "\n" r"• \(180^\circ\) is the low-frequency phase." "\n" r"• \(-90^\circ\) is the pole's phase far above \(\omega_0\), still without the inversion.",
         fig=fig_inverting("R₁", "R₂ = 4 R₁"), alt="Inverting amplifier with R2 = 4 R1.")
    s.round(3)
    s.mc(r"A non-inverting amplifier has closed-loop gain \(1/f\) and bandwidth \(f\cdot\omega_u\). Well ABOVE that bandwidth, how does its closed-loop magnitude behave?",
         r"It merges with the open-loop curve \(|A|\approx\omega_u/\omega\): the loop gain is \(<1\), so feedback no longer acts",
         [r"It drops at \(-40\ \mathrm{dB/decade}\), twice as fast as the op-amp", r"It stays flat at \(1/f\)", r"It rises back toward the open-loop DC gain"],
         r"\(A_{CL}=\dfrac{A}{1+Af}\). Above \(f\omega_u\), \(|Af|<1\) and \(A_{CL}\approx A\): the closed-loop curve lies on top of the open-loop \(-20\ \mathrm{dB/decade}\) line (reader Fig. 17.17 and 18.9). One pole, one slope: no \(-40\) dB/decade.",
         fig=bode_ol_cl(100, 10, 1e6, 40), alt="Bode sketch of open-loop gain and a 40 dB closed-loop gain that meets the open-loop line at 10 kHz and follows it beyond.")
    A0, k = 1000.0, 100.0
    ans = -k / (1 + (1 + k) / A0)
    s.num(r"Gotcha check: an inverting amplifier with \(R_2/R_1=100\) is built from an op-amp with only \(A_0=1000\). What is its actual DC gain?",
          ans, "V/V",
          T(r"\(G=-\dfrac{100}{1+101/1000}=-\dfrac{100}{1.101}=<<a>>\), about 9% below \(-100\)." "\n" r"The loop gain is only \(T=A_0/(1+R_2/R_1)=1000/101\approx9.9\), not 1000. A high closed-loop gain eats the loop gain. Common mistake: assuming the error is \(1/A_0=0.1\%\).", a=g_(ans, 4)),
          tol=0.01, fig=fig_inverting("R₁", "R₂ = 100 R₁"), alt="Inverting amplifier with R2 = 100 R1 using an op-amp with DC gain 1000.")
    s.mc(r"Two amplifiers both have \(|\text{gain}|=1\): a follower and an inverting stage with \(R_2=R_1\). Same op-amp, \(f_u=10\ \mathrm{MHz}\). How do their bandwidths compare?",
         r"Follower about 10 MHz; inverting about 5 MHz, because its noise gain \(1+R_2/R_1\) is 2",
         [r"Both about 10 MHz, since both have unity gain", r"Both about 5 MHz", r"Follower about 5 MHz; inverting about 10 MHz"],
         r"Bandwidth \(=f_u\cdot f\). The follower has \(f=1\). The inverting stage returns only \(f=R_1/(R_1+R_2)=1/2\) of the output to \(V^-\), so its bandwidth is \(f_u/2=5\ \mathrm{MHz}\) even though \(|\text{gain}|=1\). The signal gain and the feedback factor differ in the inverting topology.",
         fig=fig_inverting("R₁", "R₂ = R₁"), alt="Inverting amplifier with R2 equal to R1 (gain -1).")
    s.round(4)
    fu, k = 2e6, 4.0
    f0 = fu / (1 + k)
    tr = 2.2 / (2 * math.pi * f0) * 1e6
    s.num(r"Preview of slewing. The inverting amplifier with \(R_2/R_1=4\) and \(f_u=2\ \mathrm{MHz}\) is driven by a SMALL input step. Its response is a single-pole exponential with \(\tau=1/\omega_0\). What is the 10%–90% rise time, \(2.2\tau\), in µs?",
          tr, "µs",
          T(r"\(f_0=400\ \mathrm{kHz}\), so \(\tau=\dfrac{1}{2\pi\cdot4\times10^5}=0.398\ \mu\mathrm{s}\) and \(t_r=2.2\tau=<<t>>\ \mu\mathrm{s}\)." "\n" r"That's the linear (small-signal) speed. For large steps the op-amp may hit its slew-rate limit and ramp more slowly; the slew skill compares the two.", t=g_(tr, 3)),
          tol=0.02, fig=fig_step("exp", "Small-step response"), alt="Small input step and an exponential output.", preview=["slew"])
    gbw_, a0db = 240e6, 66.0
    fp = gbw_ / 10 ** (a0db / 20) / 1e3
    s.num(r"Preview of datasheets. A datasheet (the ADA4891 discussed in the reader) lists GBW \(=240\ \mathrm{MHz}\) and open-loop gain \(=66\ \mathrm{dB}\). Assuming a single dominant pole, where is the open-loop \(-3\ \mathrm{dB}\) frequency, in kHz?",
          fp, "kHz",
          T(r"\(A_0=10^{66/20}=1995\). Then \(f_{-3dB}=\dfrac{GBW}{A_0}=\dfrac{240\ \mathrm{MHz}}{1995}=<<f>>\ \mathrm{kHz}\)." "\n" r"Datasheets usually give GBW and DC gain, not the pole: you back it out with the single-pole model. Common mistake: using \(10^{66/10}\).", f=g_(fp, 4)),
          tol=0.02, fig=bode_ol(66, 120e3, 240e6, 1e3, 1e9), alt="Asymptotic Bode magnitude: 66 dB flat to an unknown pole, then -20 dB/decade to 0 dB at 240 MHz.", preview=["datasheet"])
    fu, V, SR = 1e6, 0.1, 0.5
    need = V * 2 * math.pi * fu / 1e6
    s.mc(r"Preview of slew rate. A follower uses an op-amp with \(f_u=1\ \mathrm{MHz}\) and a maximum output slope of \(0.5\ \mathrm{V/\mu s}\). A \(0.1\ \mathrm{V}\) step is applied. What happens?",
         r"The linear response would start at \(0.63\ \mathrm{V/\mu s}\), above the limit, so the output first ramps at \(0.5\ \mathrm{V/\mu s}\), then settles exponentially",
         [r"It settles purely exponentially, since \(0.1\ \mathrm{V}\) is a small step", r"The output never reaches \(0.1\ \mathrm{V}\)", r"The output rises instantly, since the follower has gain 1"],
         T(r"The linear model gives \(v_o=V(1-e^{-\omega_ut})\) with initial slope \(V\omega_u=0.1\times2\pi\times10^6=<<n>>\ \mathrm{V/\mu s}\). That exceeds \(0.5\ \mathrm{V/\mu s}\), so the start is slope-limited (a ramp); once the remaining slope falls below the limit, the exponential takes over (reader Fig. 18.13–18.15). 'Small' is relative to \(SR/\omega_u=0.08\ \mathrm{V}\).", n=g_(need, 3)),
         fig=fig_step("slew", "Large-step response"), alt="Step response that first ramps linearly at a fixed slope, then settles exponentially.", preview=["slew"])
    return s

# ====================================================================== fb-errors
def fb_errors():
    s = Skill('fb-errors')
    F = fig_feedback_blocks()
    s.round(1)
    s.mc(r"For a feedback amplifier with DC loop gain \(T_0\), the static (DC) fractional gain error relative to the ideal \(1/f\) is",
         r"\(\dfrac{1}{1+T_0}\)",
         [r"\(\dfrac{1}{T_0^2}\)", r"\(\dfrac{T_0}{1+T_0}\)", r"\(\dfrac{1}{f}\)"],
         r"\(G_{cl}=\dfrac1f\cdot\dfrac{T_0}{1+T_0}=\dfrac1f\left(1-\dfrac{1}{1+T_0}\right)\). The shortfall is \(\dfrac{1}{1+T_0}\approx\dfrac{1}{T_0}\)." "\n" r"• \(\dfrac{T_0}{1+T_0}\) is the ratio actual/ideal, not the error." "\n" r"• \(1/f\) is the ideal gain itself.",
         fig=F, alt="Negative feedback block diagram.")
    s.mc(r"What is meant by a 'dynamic' error in a feedback amplifier, as opposed to a static error?",
         r"An error that grows with signal frequency (or shows up in transients) because the loop gain \(|T(j\omega)|\) falls at high frequency",
         [r"An error caused only by the resistor tolerances", r"An error that exists only at DC", r"An error caused by the power supply turning on"],
         r"The static error \(1/(1+T_0)\) uses the DC loop gain. At higher frequencies \(|T(j\omega)|\) drops (above the op-amp's dominant pole it falls 20 dB/decade), so the error \(\left|\dfrac{1}{1+T(j\omega)}\right|\) rises, in magnitude and phase. A step response that settles with a time constant is the same effect in the time domain." "\n" r"• Resistor tolerances set the IDEAL gain \(1/f\), they are not a loop-gain error.",
         fig=fig_bode_mag([(1, 60), (100, 60), (1e5, 0)], 1, 1e6, 70, ylab="|T| (dB)", title="Loop gain falls with frequency"), alt="Bode magnitude of loop gain: 60 dB to 100 Hz, then falling to 0 dB at 100 kHz.")
    T0 = 499.0
    s.num(r"An amplifier has DC loop gain \(T_0=499\). What is its static gain error, in percent?",
          100 / (1 + T0), "%",
          r"\(\dfrac{1}{1+T_0}=\dfrac{1}{500}=0.2\%\). The closed-loop gain is 0.2% below \(1/f\).",
          tol=0.01, fig=F, alt="Negative feedback block diagram with T0 = 499.")
    s.round(2)
    T0, fp, f = 1000.0, 100.0, 10e3
    Tj = T0 / (1 + 1j * f / fp)
    err = abs(1 / (1 + Tj)) * 100
    fig_T = fig_bode_mag([(1, 60), (100, 60), (1e5, 0)], 1, 1e6, 70, ylab="|T| (dB)", title="Loop gain T(jf)", extra=lambda X, Y: b2b_line(X(1e4), Y(0), X(1e4), Y(20), dash=True) + b2b_text(X(1e4) + 4, Y(20) - 6, "10 kHz", size=10, anchor="start"))
    s.num(r"The loop gain is \(T(jf)=\dfrac{1000}{1+jf/100\ \mathrm{Hz}}\). For a 10 kHz sine, what is the magnitude of the error ratio \(\left|\dfrac{s_{err}}{s_{in}}\right|=\left|\dfrac{1}{1+T}\right|\), in percent?",
          err, "%",
          T(r"\(T(j10^4)=\dfrac{1000}{1+j100}=\dfrac{1000(1-j100)}{10001}=0.09999-j9.999\)." "\n" r"\(1+T=1.09999-j9.999\), \(|1+T|=10.06\), so \(|1/(1+T)|=<<e>>\%\)." "\n" r"At DC the error was 0.1%; at 10 kHz, where \(|T|\approx10\), it is about 10%. Common mistake: using \(1/(1+|T|)=9.1\%\), which ignores that \(T\) is almost purely imaginary here.", e=g_(err, 4)),
          tol=0.02, fig=fig_T, alt="Loop gain Bode magnitude with a marker at 10 kHz where |T| is about 20 dB.")
    fb = 0.01
    G = (1 / fb) * abs(Tj / (1 + Tj))
    s.num(r"The same loop (\(T=\dfrac{1000}{1+jf/100\ \mathrm{Hz}}\)) has \(f=0.01\), so the ideal gain is 100. What is the closed-loop gain MAGNITUDE \(\dfrac1f\left|\dfrac{T}{1+T}\right|\) at 10 kHz?",
          G, "V/V",
          T(r"\(\left|\dfrac{T}{1+T}\right|=\dfrac{|0.09999-j9.999|}{|1.09999-j9.999|}=\dfrac{9.9995}{10.059}=0.99407\), so \(|G_{cl}|=<<g>>\)." "\n" r"Only 0.6% low in magnitude, even though the error ratio is about 10%. The error is mostly in QUADRATURE (90° out of phase), so it mainly shifts the phase instead of shrinking the magnitude.", g=g_(G, 4)),
          tol=0.005, fig=fig_T, alt="Loop gain Bode magnitude with a 10 kHz marker.")
    T0, fb = 99.0, 0.1
    out = (1 / fb) * T0 / (1 + T0)
    s.mc(r"A feedback amplifier with ideal gain 10 (\(f=0.1\)) and DC loop gain \(T_0=99\) receives a 1 V input step. What is the output after it has settled?",
         T(r"<<v>> V", v=g_(out, 3)),
         [r"10 V", r"9.09 V", r"10.1 V"],
         T(r"After settling, the DC loop gain applies: \(v_o=\dfrac1f\cdot\dfrac{T_0}{1+T_0}\times1\ \mathrm{V}=10\times\dfrac{99}{100}=<<v>>\ \mathrm{V}\). A 1% static error remains forever; the transient only decides how fast you get there." "\n" r"• 10 V would need \(T_0=\infty\)." "\n" r"• 9.09 V is \(10/(1+0.1)\), a mis-use of the formula." "\n" r"• 10.1 V applies the 1% error with the wrong sign: feedback amplifiers fall SHORT of \(1/f\).", v=g_(out, 3)),
         fig=F, alt="Negative feedback block diagram.")
    s.round(3)
    s.mc(r"In the 10 kHz example, the error ratio \(|1/(1+T)|\) was about 10%, but the closed-loop gain magnitude was only 0.6% low. Why the difference?",
         r"At 10 kHz \(T\) is almost purely imaginary, so the error adds at nearly \(90^\circ\): it mostly creates a phase error, and the magnitude changes only to second order",
         [r"Because the error ratio formula is wrong at high frequencies", r"Because the ideal gain \(1/f\) changes with frequency", r"Because 10% and 0.6% are the same error expressed in dB"],
         r"\(\dfrac{T}{1+T}=1-\dfrac{1}{1+T}\). With \(T\approx-j10\), the error term is \(\approx\dfrac{1}{1-j10}\approx j0.1\): perpendicular to 1. Adding a perpendicular 0.1 to 1 changes the length by only \(\sqrt{1+0.01}-1\approx0.5\%\) but rotates it by \(\approx5.7^\circ\)." "\n" r"So a single 'percent error' isn't enough at high frequency; magnitude and phase errors behave differently.",
         fig=b2b_svg(300, 130, b2b_arrow(30, 100, 230, 100) + b2b_text(130, 118, "1 (ideal)", size=11) + b2b_arrow(230, 100, 230, 80) + b2b_text(236, 92, "≈ j0.1 error", size=11, anchor="start") + b2b_arrow(30, 100, 230, 80) + b2b_text(120, 80, "actual T/(1+T)", size=11), "Phasor picture of the error"),
         alt="Phasor sketch: the ideal value is a long horizontal arrow of length 1; the error is a short perpendicular arrow; the actual value is the slightly rotated, nearly equal-length arrow.")
    ph = math.degrees(cmath.phase(Tj / (1 + Tj)))
    s.num(r"For the same loop at 10 kHz (\(T=\dfrac{1000}{1+j100}\)), what is the phase of the closed-loop gain relative to the ideal, \(\angle\dfrac{T}{1+T}\), in degrees?",
          ph, "degrees",
          T(r"\(\dfrac{T}{1+T}=\dfrac{0.09999-j9.999}{1.09999-j9.999}\). Angles: numerator \(-89.43^\circ\), denominator \(-83.72^\circ\); difference \(=<<p>>^\circ\)." "\n" r"About \(-5.7^\circ\) of phase lag (\(\approx-\tan^{-1}(1/|T|)\)), while the magnitude was only 0.6% low.", p=g_(ph, 4)),
          tol=0.02, fig=fig_T, alt="Loop gain Bode magnitude with a 10 kHz marker.")
    s.mc(r"An op-amp is modeled as a pure integrator \(A=\omega_u/(j\omega)\) (infinite DC gain), with \(f_u=1\ \mathrm{MHz}\) and \(f=0.1\). Which describes its errors?",
         r"Zero static error, but a dynamic error of about \(|1/(1+T)|\approx10\%\) at 10 kHz, where \(|T|\approx10\)",
         [r"Zero error at every frequency, since the gain is infinite", r"A static error of 10%, constant with frequency", r"Infinite error at DC"],
         r"\(T=Af=\dfrac{f\,\omega_u}{j\omega}\): infinite at DC, so the static error \(1/(1+T_0)\) is 0. At 10 kHz, \(|T|=0.1\times10^6/10^4=10\) and \(|1/(1+T)|=1/|1-j10|\approx9.95\%\)." "\n" r"'Infinite gain' only at DC: the trap is equating infinite DC gain with perfect accuracy at all frequencies.",
         fig=fig_bode_mag([(1, 100), (1e5, 0)], 1, 1e6, 110, ylab="|T| (dB)", title="Integrator loop gain"), alt="Loop gain of an integrator: a straight line falling at 20 dB/decade, reaching 0 dB at 100 kHz.")
    s.round(4)
    Tl = 9.0
    s.num(r"Preview of the source follower. Later you will see a transistor follower whose voltage gain has the form \(\dfrac{T}{1+T}\), i.e. a feedback loop with \(f=1\) and loop gain \(T\). If \(T=9\), what is its gain?",
          Tl / (1 + Tl), "V/V",
          r"\(\dfrac{T}{1+T}=\dfrac{9}{10}=0.9\). With \(f=1\) the ideal gain is 1, and the static error \(1/(1+T)=10\%\) explains why such followers have gain a bit below 1. More loop gain gives a better follower.",
          tol=0.01, fig=fig_feedback_blocks("T", "1"), alt="Feedback block diagram with forward block T and feedback block 1.", preview=["cd"])
    G1, G2, Tf = 50.0, 51.0, 4.0
    f = Tf / G1
    c = ((G2 / (1 + G2 * f)) / (G1 / (1 + G1 * f)) - 1) * 100
    s.num(r"Preview of source degeneration (local feedback). A stage has forward gain \(G=50\) and feedback that makes \(T=4\), so its gain is \(G/(1+T)=10\). The device's \(G\) increases by 2% (to 51, with \(f\) unchanged). By what percent does the closed-loop gain change?",
          c, "%",
          T(r"\(f=T/G=0.08\). New gain \(=\dfrac{51}{1+51\times0.08}=\dfrac{51}{5.08}=10.039\), a change of \(<<c>>\%\)." "\n" r"Sensitivity is reduced by \(1+T=5\): \(2\%/5=0.4\%\). Degeneration in transistor amplifiers uses exactly this trade (gain for stability against device variation).", c=g_(c, 3)),
          tol=0.03, fig=fig_feedback_blocks("G = 50", "f = 0.08"), alt="Feedback block diagram with G = 50 and f = 0.08.", preview=["degeneration"])
    s.mc(r"Preview of transistor amplifiers. A transistor gain stage has a voltage gain that varies by \(\pm30\%\) with temperature and manufacturing. You need a gain accurate to \(\pm0.3\%\). Using only ideas from feedback errors, what works?",
         r"Make a stage with about \(100\times\) more gain than needed and close a loop with a precise \(f\), so \(T\approx100\) divides the variation by \(\sim100\)",
         [r"Use the stage open-loop and select parts carefully", r"Close a loop with \(T\approx1\)", r"Add a second identical stage in series to average the errors"],
         r"Closed-loop sensitivity is the open-loop sensitivity divided by \(1+T\): \(30\%/101\approx0.3\%\). That requires excess forward gain (\(G=T/f\)) which is then 'spent' on accuracy. A cascade without feedback multiplies variations instead of averaging them; \(T\approx1\) only halves them.",
         fig=fig_feedback_blocks("G (±30%)", "precise f"), alt="Feedback block diagram with a poorly controlled forward gain and a precise feedback factor.", preview=["cs-analysis"])
    return s

# ====================================================================== fb-impedance
def fb_impedance():
    s = Skill('fb-impedance')
    def fz(label="Z_out,fb", title="Voltage amplifier in a series-shunt feedback loop"):
        return fig_noninverting("R₁", "R₂", "vᵢₙ", "vₒᵤₜ", title) 
    s.round(1)
    s.mc(r"For an op-amp in the non-inverting ('voltage') feedback configuration, how does feedback change the input and output impedance of the amplifier?",
         r"Input impedance rises by \(1+T\); output impedance falls by \(1+T\)",
         [r"Both rise by \(1+T\)", r"Both fall by \(1+T\)", r"Input impedance falls by \(1+T\); output impedance rises by \(1+T\)"],
         r"Reader Sec. 17.8: \(Z_{in,fb}=R_{in}(1+Af)\) because the op-amp input only sees the tiny error voltage; \(Z_{out,fb}=\dfrac{R_{out}}{1+Af}\) because the loop fights any output change caused by the load. Feedback makes a voltage amplifier more ideal on both ports.",
         fig=fig_noninverting(), alt="Non-inverting amplifier with R1 and R2; input and output impedances are of interest.")
    Rout, T_ = 100.0, 999.0
    s.num(r"An op-amp has open-loop output resistance \(R_{out}=100\ \Omega\). In a voltage-feedback configuration with loop gain \(T=Af=999\), what is the closed-loop output resistance?",
          Rout / (1 + T_), "Ω",
          r"\(Z_{out,fb}=\dfrac{R_{out}}{1+T}=\dfrac{100\ \Omega}{1000}=0.1\ \Omega\) (reader Eq. 17.47).",
          tol=0.01, fig=fig_vcvs(rs=False, rl=True, labels=("", "R_in", "R_out = 100 Ω", "Rₗ")), alt="VCVS op-amp model with R_out = 100 Ω driving a load.")
    Rin, T_ = 1e6, 1000.0
    s.num(r"An op-amp's differential input resistance is \(R_{in}=1\ \mathrm{M\Omega}\). In the non-inverting configuration with \(T=1000\), what input resistance does the source see, in GΩ?",
          Rin * (1 + T_) / 1e9, "GΩ",
          r"\(Z_{in,fb}=R_{in}(1+T)=10^6\times1001=1.001\times10^9\ \Omega=1.001\ \mathrm{G\Omega}\) (reader Eq. 17.45). The input current is set by the error voltage, which is \(1+T\) times smaller than the input.",
          tol=0.01, fig=fig_noninverting(), alt="Non-inverting amplifier.")
    s.round(2)
    A, Rout = 2e4, 50.0
    z = Rout / (1 + A) * 1e3
    s.num(r"A unity-gain follower (\(f=1\)) uses an op-amp with \(A=2\times10^4\) and \(R_{out}=50\ \Omega\). What is its output resistance, in mΩ?",
          z, "mΩ",
          T(r"\(T=Af=2\times10^4\), so \(Z_{out}=\dfrac{50}{1+2\times10^4}=<<z>>\ \mathrm{m\Omega}\). This is why op-amp followers are used as buffers: high \(Z_{in}\), tiny \(Z_{out}\) (reader Sec. 17.8.2).", z=g_(z, 4)),
          tol=0.01, fig=fig_follower(), alt="Unity-gain follower.")
    A, f, Rout, RL = 1e4, 0.1, 200.0, 100.0
    zo = Rout / (1 + A * f)
    drop = zo / (RL + zo) * 100
    s.num(r"A gain-10 non-inverting amplifier (\(f=0.1\)) uses an op-amp with \(A=10^4\) and \(R_{out}=200\ \Omega\). It drives \(R_L=100\ \Omega\). By what percentage does the load reduce the output voltage compared with no load?",
          drop, "%",
          T(r"\(T=1000\), \(Z_{out,fb}=200/1001=0.1998\ \Omega\). The output divider gives \(\dfrac{R_L}{R_L+Z_{out,fb}}\), a drop of \(\dfrac{0.1998}{100.1998}=<<d>>\%\)." "\n" r"Without feedback the same 200 Ω output into 100 Ω would lose 67% of the signal.", d=g_(drop, 4)),
          tol=0.02, fig=fig_noninverting("R₁", "R₂ = 9 R₁", "vᵢₙ", "vₒᵤₜ → R_L = 100 Ω"), alt="Non-inverting amplifier of gain 10 driving a 100 Ω load.")
    s.mc(r"Why does series (voltage) feedback at the input RAISE the input impedance?",
         r"The op-amp input resistance sees only the error voltage \(v_x-f\,v_{out}\approx v_x/(1+T)\), so the current drawn is \(1+T\) times smaller",
         [r"Because the feedback resistors add in series with the input", r"Because the op-amp gain makes the input resistor physically larger", r"Because feedback lowers the input voltage to zero"],
         r"\(i_x=\dfrac{v_x-f\,v_{out}}{R_{in}}\) and \(v_{out}\approx\dfrac{A}{1+Af}v_x\), giving \(i_x=\dfrac{v_x}{R_{in}(1+Af)}\) (reader Eq. 17.44–17.45). The feedback voltage 'bootstraps' the other end of \(R_{in}\) almost up to \(v_x\)." "\n" r"• The divider resistors are not in the input path." "\n" r"• The input voltage stays \(v_x\); only the DIFFERENCE across \(R_{in}\) shrinks.",
         fig=fig_noninverting(), alt="Non-inverting amplifier; the input impedance is boosted by feedback.")
    s.round(3)
    zfig = b2b_svg(340, 160, b2b_axes(40, 130, 280, 110, "f (log)", "|Z_out|") +
                   b2b_poly([(40, 115), (110, 115), (230, 45), (310, 45)], sw=2.2) +
                   b2b_text(60, 110, "R_out/(1+T₀)", size=10, anchor="start") + b2b_text(250, 40, "R_out", size=10, anchor="start") +
                   b2b_line(110, 127, 110, 133) + b2b_text(110, 147, "f_p", size=10) + b2b_line(230, 127, 230, 133) + b2b_text(230, 147, "≈ f·f_u", size=10),
                   "Closed-loop output impedance vs frequency")
    s.mc(r"How does the closed-loop output impedance of a voltage-feedback op-amp amplifier behave versus frequency?",
         r"Low (\(R_{out}/(1+T_0)\)) at DC, rising at \(+20\ \mathrm{dB/decade}\) above the op-amp's dominant pole (like an inductor), back to \(R_{out}\) once the loop gain falls below 1",
         [r"Constant at \(R_{out}/(1+T_0)\) at all frequencies", r"Highest at DC and falling with frequency, like a capacitor", r"Zero at all frequencies for an ideal op-amp model with a pole"],
         r"\(Z_{out}=\dfrac{R_{out}}{1+A(j\omega)f}\) and \(|A|\) falls above \(\omega_{-3dB}\), so \(|Z_{out}|\) rises with frequency (a zero at the op-amp pole), reaching \(R_{out}\) near the unity-loop-gain frequency (reader Eq. 17.48 and Fig. 17.26). Rising impedance with frequency looks inductive, which matters when driving capacitive loads." "\n" r"Reader typo: the sentence after Eq. 17.48 says the unity-gain frequency is '\(\omega_0(1+Af)\)'; it should be \(\omega_0(1+A_0f)\).",
         fig=zfig, alt="Sketch of output impedance magnitude versus log frequency: flat and low, rising between the op-amp pole and the loop crossover, then flat at R_out.")
    Rout, A0, fp, f, fq = 100.0, 1e5, 10.0, 1.0, 100e3
    A = A0 / (1 + 1j * fq / fp)
    Z = abs(Rout / (1 + A * f))
    s.num(r"A follower uses an op-amp with \(R_{out}=100\ \Omega\), \(A_0=10^5\) and a dominant pole at 10 Hz. What is \(|Z_{out}|\) at 100 kHz?",
          Z, "Ω",
          T(r"\(A(j\,100\ \mathrm{kHz})=\dfrac{10^5}{1+j10^4}\approx-j10\) (that is, \(f_u/f=10\)). Then \(|1+A|=|1+0.001-j10|\approx10.05\) and \(|Z_{out}|=\dfrac{100}{10.05}=<<z>>\ \Omega\)." "\n" r"At DC it was \(1\ \mathrm{m\Omega}\); at 100 kHz only a 10× improvement remains. Common mistake: using the DC loop gain at all frequencies.", z=g_(Z, 4)),
          tol=0.02, fig=fig_follower(), alt="Unity-gain follower.")
    s.mc(r"An INVERTING amplifier has \(R_1=1\ \mathrm{k\Omega}\), \(R_2=10\ \mathrm{k\Omega}\), and an op-amp with \(A=10^5\), \(R_{in}=1\ \mathrm{M\Omega}\). What input resistance does the source see?",
         r"About \(1\ \mathrm{k\Omega}\) (just \(R_1\), into a virtual ground)",
         [r"About \(10^{11}\ \Omega\), boosted by \(1+T\)", r"About \(11\ \mathrm{k\Omega}\)", r"About \(1\ \mathrm{M\Omega}\)"],
         r"The \(1+T\) boost applies when the feedback voltage is subtracted in SERIES with the input (non-inverting). In the inverting amplifier, the feedback current is subtracted at the input node (a shunt connection), which makes \(V^-\) a low-impedance virtual ground. The source sees \(R_1\) into ≈0 V: \(R_{in}\approx1\ \mathrm{k\Omega}\)." "\n" r"Gotcha: 'feedback raises input impedance' is not universal; it depends on how the feedback is connected at the input.",
         fig=fig_inverting("R₁ = 1 kΩ", "R₂ = 10 kΩ"), alt="Inverting amplifier with R1 = 1 kΩ and R2 = 10 kΩ.")
    s.round(4)
    Rs, Rin, T_ = 600.0, 1e6, 100.0
    Zin = Rin * (1 + T_)
    loss = Rs / (Zin + Rs) * 1e6
    s.num(r"Preview of impedance matching in cascades. A 600 Ω source drives a non-inverting op-amp stage with \(R_{in}=1\ \mathrm{M\Omega}\) and \(T=100\). How much of the signal is lost to the input divider, in parts per million?",
          loss, "ppm",
          T(r"\(Z_{in}=R_{in}(1+T)=101\ \mathrm{M\Omega}\). The fraction lost is \(\dfrac{R_s}{Z_{in}+R_s}=\dfrac{600}{1.01\times10^8}=<<l>>\ \mathrm{ppm}\)." "\n" r"Cascades work best when each stage has high input impedance compared with the previous stage's output impedance: feedback makes that easy.", l=g_(loss, 3)),
          tol=0.02, fig=fig_noninverting("R₁", "R₂", "600 Ω source"), alt="A 600 ohm source drives a non-inverting amplifier.", preview=["z-match"])
    Ro, T_ = 10e3, 99.0
    s.num(r"Preview of the source follower. A buffer stage has a poor open-loop output resistance of \(10\ \mathrm{k\Omega}\), but it is wrapped in a voltage-feedback loop with \(T=99\). What output resistance does the load see?",
          Ro / (1 + T_), "Ω",
          r"\(Z_{out}=\dfrac{10\ \mathrm{k\Omega}}{1+99}=100\ \Omega\). Later you will see a single-transistor follower whose low output resistance arises the same way: its built-in feedback divides a large resistance by \(1+T\).",
          tol=0.01, fig=fig_follower(), alt="Unity-gain follower buffer.", preview=["cd"])
    s.mc(r"Preview of degeneration. Voltage feedback senses the output VOLTAGE and lowers \(Z_{out}\). Suppose instead a loop senses the output CURRENT (through a small sense resistor) and corrects it. What would you expect for the output impedance?",
         r"It rises by about \(1+T\): the loop keeps the current constant when the load changes, which is what a high-impedance current source does",
         [r"It falls by \(1+T\), like voltage feedback", r"It is unchanged, since feedback never affects impedance", r"It becomes zero"],
         r"Whatever quantity the loop senses, it stabilizes. Keeping the voltage fixed against load changes means a low output impedance; keeping the CURRENT fixed means a high output impedance (the voltage changes freely while the current doesn't). Source degeneration in transistor stages is exactly this current-sensing feedback.",
         fig=fig_feedback_blocks("G", "f (senses i_out)"), alt="Feedback block diagram where the feedback block senses the output current.", preview=["degeneration"])
    return s

# ====================================================================== stability
def stability():
    s = Skill('stability')
    def two_pole_T(T0, f1, f2): return lambda f: T0 / ((1 + 1j * f / f1) * (1 + 1j * f / f2))
    def fig_two_pole(T0db, f1, f2, fmin, fmax, title="Loop gain with two poles"):
        fc2 = 10 ** (T0db / 20)  # placeholder
        segs = [(fmin, T0db), (f1, T0db), (f2, T0db - 20 * math.log10(f2 / f1))]
        end_db = T0db - 20 * math.log10(f2 / f1) - 40 * math.log10(fmax / f2)
        segs.append((fmax, end_db))
        return fig_bode_mag(segs, fmin, fmax, T0db * 1.15, ylab="|T| (dB)", title=title)
    s.round(1)
    s.mc(r"Why can a negative-feedback loop whose loop gain has only ONE pole never become unstable?",
         r"A single pole contributes at most \(-90^\circ\) of phase, so \(T\) can never reach \(-180^\circ\) (i.e. \(T=-1\))",
         [r"Because a single pole has no gain", r"Because a single pole makes the loop gain grow with frequency", r"Because single-pole loops have no feedback"],
         r"\(\angle\dfrac{T_0}{1+j\omega\tau}=-\tan^{-1}(\omega\tau)\to-90^\circ\) at most (reader Eq. 17.50 and Sec. 17.9.2). The feedback never turns positive, so there is always at least \(90^\circ\) of phase margin.",
         fig=fig_bode_mag([(1, 60), (100, 60), (1e5, 0)], 1, 1e6, 70, ylab="|T| (dB)", title="Single-pole loop gain"), alt="Single-pole loop gain Bode magnitude.")
    s.mc(r"A feedback system oscillates at a frequency \(\omega_x\) when",
         r"\(T(j\omega_x)=-1\): unity magnitude with \(-180^\circ\) phase, so the closed-loop gain \(G/(1+T)\) is infinite",
         [r"\(T(j\omega_x)=+1\)", r"\(T(j\omega_x)=0\)", r"\(|T(j\omega_x)|\) is very large with \(0^\circ\) phase"],
         r"With \(T=-1\), the denominator \(1+T\) vanishes (reader Sec. 17.9.3): a signal going around the loop comes back with the same size and inverted twice (the \(-180^\circ\) plus the subtraction), so it sustains itself without any input." "\n" r"• \(T=+1\) gives \(1+T=2\), harmless in negative feedback." "\n" r"• Large \(T\) at \(0^\circ\) is just strong, well-behaved negative feedback.",
         fig=fig_feedback_blocks(), alt="Negative feedback loop block diagram.")
    s.num(r"At the frequency where \(|T|=1\), the loop-gain phase is \(-120^\circ\). What is the phase margin, in degrees?",
          60.0, "degrees",
          r"Phase margin \(=180^\circ+\angle T\) at the unity-loop-gain frequency \(=180^\circ-120^\circ=60^\circ\). The reader recommends at least \(60^\circ\) for a good design.",
          tol=0.01, fig=fig_two_pole(60, 100, 1e5, 1, 1e7), alt="Bode magnitude of a two-pole loop gain.")
    s.round(2)
    T0, f1, f2 = 1000.0, 1e3, 1e6
    Tf = two_pole_T(T0, f1, f2)
    fc = bisect_log(lambda f: abs(Tf(f)) - 1, 1e3, 1e8)
    pm = 180 + math.degrees(cmath.phase(Tf(fc)))
    s.num(r"A loop gain has \(T(jf)=\dfrac{1000}{(1+jf/1\ \mathrm{kHz})(1+jf/1\ \mathrm{MHz})}\). Find the frequency where \(|T|=1\) numerically and give the phase margin, in degrees.",
          pm, "degrees",
          T(r"The asymptotes say the crossover is near 1 MHz, right at the second pole, where the actual \(|T|\) is \(1/\sqrt2\) below the asymptote. Solving \(|T(jf)|=1\) gives \(f_c=<<fc>>\ \mathrm{kHz}\)." "\n" r"\(\angle T(f_c)=-\tan^{-1}(f_c/1\ \mathrm{kHz})-\tan^{-1}(f_c/1\ \mathrm{MHz})=<<ph>>^\circ\), so PM \(=<<pm>>^\circ\)." "\n" r"Using the asymptotic crossover (1 MHz) would give \(45^\circ\); the true answer is better because the crossover is lower.", fc=g_(fc / 1e3, 4), ph=g_(pm - 180, 4), pm=g_(pm, 3)),
          tol=0.02, fig=fig_two_pole(60, 1e3, 1e6, 10, 1e8), alt="Two-pole loop gain Bode magnitude: 60 dB to 1 kHz, -20 dB/decade to 1 MHz, then -40 dB/decade.")
    ph = math.degrees(cmath.phase(Tf(1e6)))
    s.num(r"For the same loop gain (poles at 1 kHz and 1 MHz), what is \(\angle T\) at exactly 1 MHz, in degrees?",
          ph, "degrees",
          T(r"\(-\tan^{-1}(1000)-\tan^{-1}(1)=-89.94^\circ-45^\circ=<<p>>^\circ\)." "\n" r"Two poles approach \(-180^\circ\) only asymptotically (reader Fig. 17.28); at the second pole you are \(45^\circ\) short of it.", p=g_(ph, 5)),
          tol=0.01, fig=fig_two_pole(60, 1e3, 1e6, 10, 1e8), alt="Two-pole loop gain Bode magnitude.")
    s.mc(r"In a loop with a dominant pole and one non-dominant pole, where should the non-dominant pole be placed for a comfortable phase margin?",
         r"Well above the unity-loop-gain frequency, so it adds little phase where \(|T|=1\) (at the crossover it would give only about \(45^\circ\))",
         [r"Exactly at the unity-loop-gain frequency, giving \(90^\circ\) margin", r"Below the dominant pole", r"Anywhere: non-dominant poles do not affect stability"],
         r"At crossover the dominant pole already contributes \(\approx-90^\circ\). A second pole AT the crossover adds \(-45^\circ\) (PM \(\approx45^\circ\)); at \(\sim1.7\times\) the crossover it adds \(\approx-30^\circ\) (PM \(\approx60^\circ\)). So non-dominant poles belong well above the crossover (reader Sec. 17.9.2)." "\n" r"• A pole below the dominant one would make IT the dominant pole.",
         fig=fig_two_pole(60, 1e3, 1e6, 10, 1e8), alt="Two-pole loop gain Bode magnitude.")
    s.round(3)
    s.mc(r"An op-amp is stable as a gain-of-10 amplifier but oscillates when connected as a unity-gain follower. Why?",
         r"With \(f=1\) the loop gain \(T=Af\) is 10× larger, so the crossover moves up toward the non-dominant poles and the phase margin shrinks",
         [r"Because the follower has no feedback", r"Because the follower's gain of 1 means \(T=1\) at all frequencies", r"Because lower closed-loop gain always gives MORE phase margin, so this can't happen"],
         r"\(T=A(j\omega)f\): raising \(f\) from 0.1 to 1 lifts the whole \(|T|\) curve by 20 dB, so the unity crossing moves from \(\approx f_u/10\) to \(\approx f_u\), closer to the extra poles. The follower is the hardest case, which is why datasheets advertise 'unity-gain stable' op-amps." "\n" r"Gotcha: low closed-loop gain means HIGH loop gain, and less margin.",
         fig=fig_follower(), alt="Unity-gain follower.")
    A0, f1, f2 = 1e5, 10.0, 2e6
    Af = lambda f: A0 / ((1 + 1j * f / f1) * (1 + 1j * f / f2))
    fc = bisect_log(lambda f: abs(Af(f)) - 1, 1e3, 1e9)
    pm_f = 180 + math.degrees(cmath.phase(Af(fc)))
    s.num(r"An op-amp has \(A(jf)=\dfrac{10^5}{(1+jf/10\ \mathrm{Hz})(1+jf/2\ \mathrm{MHz})}\) (\(f_u\approx1\ \mathrm{MHz}\)). Connected as a follower (\(f=1\)), what is the phase margin? Solve \(|T|=1\) numerically.",
          pm_f, "degrees",
          T(r"\(T=A\). Solving \(|A(jf)|=1\): \(f_c=<<fc>>\ \mathrm{kHz}\) (a bit below 1 MHz because the second pole already bends the curve)." "\n" r"\(\angle T=-\tan^{-1}(f_c/10)-\tan^{-1}(f_c/2\ \mathrm{MHz})\approx-90^\circ-<<p2>>^\circ\), so PM \(=<<pm>>^\circ\)." "\n" r"With \(f=0.1\) the crossover drops to \(\approx100\ \mathrm{kHz}\) and PM \(\approx87^\circ\): same op-amp, very different margin.", fc=g_(fc / 1e3, 4), p2=g_(math.degrees(math.atan(fc / f2)), 3), pm=g_(pm_f, 3)),
          tol=0.02, fig=fig_two_pole(100, 10, 2e6, 1, 1e8, "Op-amp gain with a 2 MHz second pole"), alt="Bode magnitude of an op-amp with poles at 10 Hz and 2 MHz.")
    s.mc(r"At the frequency where \(\angle T=-180^\circ\), a loop has \(|T|=0.3\). Is it stable?",
         r"Yes: the feedback is positive at that frequency, but with \(|T|<1\) the signal shrinks each trip around the loop (gain margin about 10.5 dB)",
         [r"No: any loop that reaches \(-180^\circ\) oscillates", r"No: \(|T|=0.3\) is too small for feedback to work", r"It can't be determined without the DC gain"],
         r"Oscillation needs \(T=-1\). With \(T=-0.3\), the closed-loop gain is \(G/(1-0.3)=1.43G\): a mild peak, not instability (reader Sec. 17.9.4: unstable if \(|T|>1\) at \(-180^\circ\)). The distance \(20\log(1/0.3)=10.5\ \mathrm{dB}\) is the gain margin." "\n" r"Gotcha: reaching \(-180^\circ\) is not by itself fatal; it's the magnitude there that matters.",
         fig=fig_two_pole(60, 1e3, 1e6, 10, 1e8), alt="Two-pole loop gain Bode magnitude.")
    s.round(4)
    Ro, CL, fu = 100.0, 4.7e-9, 1e6
    fp2 = 1 / (2 * math.pi * Ro * CL)
    Tl = lambda f: (fu / (1j * f)) / (1 + 1j * f / fp2)
    fc = bisect_log(lambda f: abs(Tl(f)) - 1, 1e3, 1e9)
    pmc = 180 + math.degrees(cmath.phase(Tl(fc)))
    s.num(r"Preview of capacitive loads. A follower's op-amp (\(A\approx f_u/jf\), \(f_u=1\ \mathrm{MHz}\)) has \(R_{out}=100\ \Omega\) and drives \(C_L=4.7\ \mathrm{nF}\). The load adds a pole at \(1/(2\pi R_{out}C_L)\). What is the phase margin? Solve \(|T|=1\) numerically.",
          pmc, "degrees",
          T(r"Load pole: \(f_{p2}=\dfrac{1}{2\pi\cdot100\ \Omega\cdot4.7\ \mathrm{nF}}=<<fp>>\ \mathrm{MHz}\). With \(T=\dfrac{f_u}{jf}\cdot\dfrac{1}{1+jf/f_{p2}}\), \(|T|=1\) at \(f_c=<<fc>>\ \mathrm{kHz}\)." "\n" r"\(\angle T=-90^\circ-\tan^{-1}(f_c/f_{p2})\), so PM \(=<<pm>>^\circ\): below the 60° target. Common-source stages with big capacitive loads face the same pole.", fp=g_(fp2 / 1e6, 3), fc=g_(fc / 1e3, 4), pm=g_(pmc, 3)),
          tol=0.02, fig=b2b_svg(330, 130, (lambda o: o[0])(b2b_opamp(110, 60, 56, 60, plus_top=True)) + b2b_text(18, 49, "vᵢₙ") + b2b_circle(30, 45, 3) + b2b_wire(33, 45, 110, 45) + b2b_wire(110, 75, 95, 75, 95, 110, 220, 110, 220, 60) + b2b_wire(166, 60, 240, 60) + b2b_dot(220, 60) + b2b_dot(240, 60) + b2b_capacitor(240, 60, 40, horiz=False, label="C_L = 4.7 nF") + b2b_ground(240, 100) + b2b_text(170, 50, "R_out = 100 Ω", size=10, anchor="start"), "Follower driving a capacitive load"),
          alt="Unity-gain follower whose output, with 100 ohm output resistance, drives a 4.7 nF load capacitor.", preview=["cs-cap-load"])
    fp2 = 10e6
    fu_need = math.sqrt(2) * fp2
    s.num(r"Preview of compensation. A follower's loop gain is \(T=\dfrac{f_u}{jf}\cdot\dfrac{1}{1+jf/f_{p2}}\) with a non-dominant pole \(f_{p2}=10\ \mathrm{MHz}\). Dominant-pole compensation sets \(f_u\). Which \(f_u\) puts the crossover exactly at \(f_{p2}\) (phase margin \(45^\circ\)), in MHz?",
          fu_need / 1e6, "MHz",
          T(r"At \(f=f_{p2}\): \(|T|=\dfrac{f_u}{f_{p2}}\cdot\dfrac{1}{\sqrt2}=1\Rightarrow f_u=\sqrt2\,f_{p2}=<<f>>\ \mathrm{MHz}\)." "\n" r"For 60° you would need \(f_u\) lower still. Designers lower \(f_u\) by enlarging the dominant capacitance, often with the Miller effect, which is coming soon.", f=g_(fu_need / 1e6, 4)),
          tol=0.02, fig=fig_two_pole(60, 1e4, 1e7, 100, 1e9, "Loop gain with a 10 MHz non-dominant pole"), alt="Two-pole loop gain Bode magnitude with the second pole at 10 MHz.", preview=["miller"])
    s.mc(r"Preview of compensation. The follower driving \(C_L\) has too little phase margin. Using only stability ideas, which change helps?",
         r"Lower the op-amp's \(f_u\) (more dominant-pole compensation), so the crossover moves well below the load pole",
         [r"Increase \(C_L\) further", r"Raise \(f_u\) so the loop is faster", r"Increase the feedback factor beyond 1"],
         r"Phase margin improves when the crossover sits far below the non-dominant pole. Lowering \(f_u\) moves the crossover down. A larger \(C_L\) moves the load pole DOWN (worse). Raising \(f_u\) pushes the crossover up into the pole (worse). \(f\) can't exceed 1 with a passive network." "\n" r"Miller compensation is the classic way to lower \(f_u\) on-chip.",
         fig=fig_two_pole(60, 1e3, 1e6, 10, 1e8), alt="Two-pole loop gain Bode magnitude.", preview=["miller", "cs-cap-load"])
    return s

BUILD = [gbw, opamp_fr, fb_errors, fb_impedance, stability]
if __name__ == "__main__":
    for fn in BUILD:
        sk = fn(); sk.save(); print("wrote", sk.sid, len(sk.qs))
