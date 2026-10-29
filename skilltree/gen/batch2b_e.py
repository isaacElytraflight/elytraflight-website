"""batch2b group E: diode-qual, diode-iv, diode-ss"""
from batch2b_lib import *
from batch2b_b import g_
from batch2b_d import fig_pn, q, Vt, ni

def fig_iv(title="Diode I–V curve", mark=None, log=False):
    x0, y0 = 200, 100
    b = b2b_line(20, y0, 330, y0, op=0.6) + b2b_line(x0, 130, x0, 10, op=0.6)
    b += b2b_text(328, y0 + 14, "V_D", anchor="end", size=10) + b2b_text(x0 + 6, 16, "I_D", anchor="start", size=10)
    f = lambda v: min(85.0, 1.2 * (math.exp(v / 12.0) - 1))
    pts = [(x0 + v, y0 - f(v)) for v in range(-170, 61, 2)]
    b += b2b_poly(pts, sw=2.2)
    b += b2b_text(60, y0 + 18, "reverse: I ≈ −I_S", size=10) + b2b_text(180, 30, "forward: exponential", size=10, anchor="end")
    return b2b_svg(340, 140, b, title)

def fig_diode_ckt(src="V", r="R", title="Diode circuit"):
    b = b2b_vsource(100, 25, 70, src) + b2b_wire(100, 25, 140, 25) + b2b_resistor(140, 25, 60, label=r) + b2b_wire(200, 25, 250, 25)
    b += b2b_diode(250, 25, 70, horiz=False, label="D") + b2b_wire(100, 95, 250, 95) + b2b_ground(175, 95)
    return b2b_svg(320, 125, b, title)

def fig_bands(kind="eq", title="Barrier and currents"):
    # potential-energy barrier sketch for electrons: high on P side, low on N side
    h = {"eq": 50, "rev": 75, "fwd": 25}[kind]
    b = b2b_poly([(20, 90 - h), (130, 90 - h), (190, 90), (320, 90)], sw=2.2)
    b += b2b_text(70, 90 - h - 6, "P side", size=10) + b2b_text(260, 84, "N side", size=10)
    b += b2b_arrow(300, 115, 300, 90, 5) if False else ""
    b += b2b_line(150, 90, 150, 90 - h, dash=True) + b2b_text(146, 90 - h / 2, "barrier", anchor="end", size=10)
    lab = {"eq": "equilibrium: q·φ_bi", "rev": "reverse bias: q(φ_bi + V_R)", "fwd": "forward bias: q(φ_bi − V_D)"}[kind]
    b += b2b_text(170, 125, lab, size=11)
    return b2b_svg(340, 135, b, title)

def fig_ss(title="Diode small-signal model"):
    b = b2b_wire(40, 25, 280, 25) + b2b_wire(40, 115, 280, 115) + b2b_circle(40, 25, 3) + b2b_circle(40, 115, 3) + b2b_text(30, 74, "v_d", anchor="end")
    b += b2b_resistor(100, 25, 90, horiz=False) + b2b_text(112, 74, "r_d = 1/g_d", anchor="start", size=11) + b2b_dot(100, 25) + b2b_dot(100, 115)
    b += b2b_capacitor(195, 25, 90, horiz=False, label="C_j") + b2b_dot(195, 25) + b2b_dot(195, 115)
    b += b2b_capacitor(260, 25, 90, horiz=False, label="C_diff") + b2b_dot(260, 25) + b2b_dot(260, 115)
    return b2b_svg(330, 135, b, title)

def Id(V, Is, n=1.0): return Is * (math.exp(V / (n * Vt)) - 1)

# ====================================================================== diode-qual
def diode_qual():
    s = Skill('diode-qual')
    s.round(1)
    s.mc(r"In thermal equilibrium (no applied bias), why is the net current through a PN junction zero?",
         r"For each carrier type, the diffusion current over the barrier exactly balances the drift current of minority carriers swept across by the field",
         [r"Because no carriers move at all", r"Because the depletion region is a perfect insulator with no field", r"Because only electrons flow and they cancel holes"],
         r"Carriers move constantly, but the few majority carriers energetic enough to diffuse over the built-in barrier are balanced by minority carriers that wander to the junction and drift back across (reader Sec. 6.2.1). The depletion region has a strong field; that's what drives the drift.",
         fig=fig_bands("eq"), alt="Energy barrier for electrons between the P side (high) and the N side (low) in equilibrium.")
    s.mc(r"Under reverse bias, the diode current saturates at a small value \(-I_S\). Why doesn't it grow with more reverse voltage?",
         r"The reverse current is drift of minority carriers that reach the junction, which doesn't depend on the barrier height; diffusion is already shut off",
         [r"Because the depletion region stops growing", r"Because the diode breaks down", r"Because diffusion current grows to cancel it"],
         r"Reader Sec. 6.2.2: a larger barrier suppresses diffusion exponentially, leaving only the drift of thermally generated minority carriers. Their supply is fixed by generation near the junction, not by the voltage, so the current saturates at \(I_S\).",
         fig=fig_bands("rev"), alt="Energy barrier raised by reverse bias.")
    dv = Vt * math.log(10) * 1e3
    s.num(r"In forward bias the diode current grows as \(e^{V_D/V_t}\) with \(V_t=25.9\ \mathrm{mV}\). By how much must \(V_D\) increase to multiply the current by 10, in mV?",
          dv, "mV",
          T(r"\(e^{\Delta V/V_t}=10\Rightarrow\Delta V=V_t\ln10=25.9\ \mathrm{mV}\times2.303=<<d>>\ \mathrm{mV}\)." "\n" r"About 60 mV per decade of current at room temperature: a key rule of thumb.", d=g_(dv, 4)),
          tol=0.01, fig=fig_iv(), alt="Diode I-V curve: tiny constant reverse current, exponential forward current.")
    s.round(2)
    s.mc(r"A forward bias \(V_D\) is applied to a junction with built-in potential \(\phi_{bi}\). What barrier do majority carriers now have to climb?",
         r"\(q(\phi_{bi}-V_D)\), lowered by the applied voltage",
         [r"\(q(\phi_{bi}+V_D)\)", r"\(q\phi_{bi}\), unchanged", r"\(qV_D\)"],
         r"Forward bias opposes the built-in potential, so the barrier drops to \(q(\phi_{bi}-V_D)\) (reader Eq. 6.17). Reverse bias raises it to \(q(\phi_{bi}+V_R)\). The diffusion current depends exponentially on this barrier.",
         fig=fig_bands("fwd"), alt="Energy barrier lowered by forward bias.")
    dV = 0.12
    s.num(r"By what factor does the diffusion current increase when the forward bias rises by 0.12 V (\(V_t=25.9\ \mathrm{mV}\))?",
          math.exp(dV / Vt), "×",
          T(r"The number of carriers able to cross scales as \(e^{-\text{barrier}/kT}\), so lowering the barrier by \(0.12\ \mathrm{eV}\) gives \(e^{0.12/0.0259}=e^{4.633}=<<f>>\)." "\n" r"Check: 0.12 V ≈ 2 decades at 60 mV/decade, ≈ 100×.", f=g_(math.exp(dV / Vt), 4)),
          tol=0.02, fig=fig_bands("fwd"), alt="Energy barrier lowered by forward bias.")
    s.mc(r"Which carriers make up the reverse saturation current \(I_S\)?",
         r"Minority carriers generated within about a diffusion length of the junction, which drift across it",
         [r"Majority carriers diffusing over the barrier", r"Electrons tunneling through the oxide", r"Carriers injected from the metal contacts"],
         r"Only minority carriers that reach the depletion edge before recombining get swept across (reader Sec. 6.2.1). They are scarce (\(n_p=n_i^2/N_A\)), so \(I_S\) is tiny.",
         fig=fig_bands("rev"), alt="Energy barrier under reverse bias.")
    s.round(3)
    s.mc(r"An ideal diode is reverse-biased first at 1 V, then at 5 V. How do the currents compare?",
         r"Essentially equal (both \(\approx-I_S\))",
         [r"5× larger at 5 V, like a resistor", r"\(e^{4/V_t}\) times larger at 5 V", r"Zero at 5 V"],
         r"Once \(|V_D|\gg V_t\), \(I=I_S(e^{V_D/V_t}-1)\approx-I_S\) regardless of \(V_D\). Real diodes show some increase (generation in the widening depletion region, and eventually breakdown), but the ideal model saturates.",
         fig=fig_iv(), alt="Diode I-V curve.")
    ratio = Id(0.1, 1.0) / abs(Id(-0.1, 1.0))
    s.num(r"For an ideal diode, what is the ratio of the forward current at \(+0.1\ \mathrm{V}\) to the magnitude of the reverse current at \(-0.1\ \mathrm{V}\) (\(V_t=25.9\ \mathrm{mV}\))?",
          ratio, "×",
          T(r"\(\dfrac{e^{x}-1}{1-e^{-x}}=e^{x}\) for \(x=0.1/0.0259=3.861\): ratio \(=e^{3.861}=<<r>>\)." "\n" r"Gotcha: at only ±0.1 V the diode already rectifies about 47:1; the 'turn-on voltage' of ~0.7 V is about currents in the mA range, not about where rectification starts.", r=g_(ratio, 4)),
          tol=0.02, fig=fig_iv(), alt="Diode I-V curve.")
    s.mc(r"In an integrated PN diode built in an N-well on a P substrate, why is the substrate tied to the most negative voltage?",
         r"To keep the parasitic N-well/substrate diode reverse-biased so it isolates the device",
         [r"To forward-bias the parasitic diode and add current", r"To set the diode's built-in potential", r"Because the substrate is the diode's anode"],
         r"The N-well and P substrate form an unwanted diode. Reverse-biasing it (substrate at the lowest potential) keeps it off, isolating the diode from everything else on the chip (reader Sec. 6.2.5)." "\n" r"Reader note: Sec. 6.2.5 says the cathode connects to the P region and the N+ contact is at the anode; for a P-in-N-well diode the P region is the ANODE and the N+ well contact is the CATHODE.",
         fig=b2b_svg(340, 120, b2b_rect(20, 60, 300, 50, fill=True) + b2b_text(170, 104, "P substrate (most negative)", size=10) + b2b_rect(60, 30, 220, 55) + b2b_text(170, 80, "N-well", size=10) + b2b_rect(90, 30, 60, 20, fill=True) + b2b_text(120, 44, "P+ (anode)", size=9) + b2b_rect(190, 30, 60, 20, fill=True) + b2b_text(220, 44, "N+ (cathode)", size=9), "IC diode cross-section"),
         alt="Cross-section: P substrate containing an N-well; inside the well a P+ anode region and an N+ cathode contact.")
    s.round(4)
    Is, V = 1e-14, 0.65
    s.num(r"Preview of the ideal diode equation. With \(I=I_S(e^{V_D/V_t}-1)\), \(I_S=10^{-14}\ \mathrm{A}\) and \(V_t=25.9\ \mathrm{mV}\), what current flows at \(V_D=0.65\ \mathrm{V}\), in mA?",
          Id(V, Is) * 1e3, "mA",
          T(r"\(V_D/V_t=25.10\), \(e^{25.10}=7.93\times10^{10}\), so \(I=<<i>>\ \mathrm{mA}\)." "\n" r"The next skill derives \(I_S\) from the minority-carrier profiles.", i=g_(Id(V, Is) * 1e3, 4)),
          tol=0.02, fig=fig_iv(), alt="Diode I-V curve.", preview=["diode-iv"])
    NA, phi, VD = 1e17, 0.8, 0.6
    pn = NA * math.exp(-(phi - VD) / Vt)
    s.num(r"Preview of minority-carrier profiles. Boltzmann's law gives the hole density at the N-side depletion edge as \(p_n(x_n)=N_Ae^{-(\phi_{bi}-V_D)/V_t}\). With \(N_A=10^{17}\ \mathrm{cm^{-3}}\), \(\phi_{bi}=0.8\ \mathrm{V}\), \(V_D=0.6\ \mathrm{V}\), what is it, in units of \(10^{13}\ \mathrm{cm^{-3}}\)?",
          pn / 1e13, "×10¹³ cm⁻³",
          T(r"\(p_n=10^{17}\times e^{-0.2/0.0259}=10^{17}\times4.43\times10^{-4}=<<p>>\ \mathrm{cm^{-3}}\)." "\n" r"Holes from the P side that clear the lowered barrier become minority carriers on the N side. Reader note: Eq. 6.18 labels \(p_n\) as the 'minority e⁻ concentration'; \(p_n\) is the minority HOLE density on the N side.", p=tex(pn, 3)),
          tol=0.02, fig=fig_pn(), alt="PN junction with depletion edges.", preview=["minority-profile"])
    s.mc(r"Preview of solar cells. Light shining on a junction generates extra electron-hole pairs near it. Using the drift/diffusion picture, how does the I–V curve change?",
         r"Extra minority carriers add to the reverse (drift) current, so the whole curve shifts downward by a light-generated current",
         [r"The forward diffusion current increases, shifting the curve up", r"The built-in potential disappears", r"Nothing; light doesn't affect diodes"],
         r"Minority carriers generated within a diffusion length are swept across by the junction field, exactly like the thermal ones that make \(-I_S\), only many more. That adds a reverse current \(-I_L\) at every voltage: the principle of the solar cell.",
         fig=fig_iv("Diode I–V (shifts down under light)"), alt="Diode I-V curve.", preview=["solar-cell"])
    return s

# ====================================================================== diode-iv
def diode_iv():
    s = Skill('diode-iv')
    s.round(1)
    s.mc(r"Which equation is the ideal diode law (ideality factor \(n\), \(V_t=kT/q\))?",
         r"\(I_D=I_S\left(e^{V_D/nV_t}-1\right)\)",
         [r"\(I_D=I_S\,e^{-V_D/nV_t}\)", r"\(I_D=V_D/R\)", r"\(I_D=I_S\left(1-e^{V_D/nV_t}\right)\)"],
         r"Forward: grows exponentially. Reverse: approaches \(-I_S\) (reader Eq. 6.25 has the same form, with \(n=1\)). The '\(-1\)' makes \(I_D=0\) at \(V_D=0\).",
         fig=fig_iv(), alt="Diode I-V curve.")
    Is, V = 2e-15, 0.7
    s.num(r"A diode has \(I_S=2\times10^{-15}\ \mathrm{A}\), \(n=1\), \(V_t=25.9\ \mathrm{mV}\). What current flows at \(V_D=0.7\ \mathrm{V}\), in mA?",
          Id(V, Is) * 1e3, "mA",
          T(r"\(V_D/V_t=27.03\), \(e^{27.03}=5.47\times10^{11}\), \(I=2\times10^{-15}\times5.47\times10^{11}=<<i>>\ \mathrm{mA}\).", i=g_(Id(V, Is) * 1e3, 4)),
          tol=0.02, fig=fig_diode_ckt(), alt="Source, resistor and diode circuit.")
    Is, I = 1e-15, 1e-3
    V = Vt * math.log(I / Is + 1)
    s.num(r"What forward voltage gives \(I_D=1\ \mathrm{mA}\) for \(I_S=10^{-15}\ \mathrm{A}\) (\(n=1\), \(V_t=25.9\ \mathrm{mV}\)), in V?",
          V, "V",
          T(r"\(V_D=V_t\ln\!\left(\dfrac{I_D}{I_S}+1\right)=0.0259\times\ln(10^{12})=0.0259\times27.63=<<v>>\ \mathrm{V}\).", v=g_(V, 4)),
          tol=0.01, fig=fig_iv(), alt="Diode I-V curve.")
    s.round(2)
    A, Dp, ND, Wn, Dn, NA, Wp = 1e-6, 10.0, 1e17, 1e-4, 30.0, 1e18, 1e-4
    jh, je = Dp / (ND * Wn), Dn / (NA * Wp)
    Is = q * A * ni ** 2 * (jh + je)
    s.num(r"A short-base diode (\(L\gg W\)) has area \(100\ \mu\mathrm{m^2}\). N side: \(N_D=10^{17}\ \mathrm{cm^{-3}}\), \(W_n=1\ \mu\mathrm{m}\), \(D_p=10\ \mathrm{cm^2/s}\). P side: \(N_A=10^{18}\ \mathrm{cm^{-3}}\), \(W_p=1\ \mu\mathrm{m}\), \(D_n=30\ \mathrm{cm^2/s}\). \(n_i=10^{10}\ \mathrm{cm^{-3}}\). Using \(I_S=qAn_i^2\left(\dfrac{D_p}{N_DW_n}+\dfrac{D_n}{N_AW_p}\right)\), what is \(I_S\) in aA (\(1\ \mathrm{aA}=10^{-18}\ \mathrm{A}\))?",
          Is * 1e18, "aA",
          T(r"Units in cm: \(A=10^{-6}\ \mathrm{cm^2}\), \(W=10^{-4}\ \mathrm{cm}\)." "\n" r"\(\dfrac{D_p}{N_DW_n}=\dfrac{10}{10^{13}}=10^{-12}\), \(\dfrac{D_n}{N_AW_p}=\dfrac{30}{10^{14}}=3\times10^{-13}\) (cm⁴/s)." "\n" r"\(I_S=1.602\times10^{-19}\times10^{-6}\times10^{20}\times1.3\times10^{-12}=<<i>>\ \mathrm{A}=<<f>>\ \mathrm{aA}\) (reader Eq. 6.25 times area). Tiny, because \(n_i^2\) is tiny; real diodes add sidewall and generation currents.", i=tex(Is, 3), f=g_(Is * 1e18, 3)),
          tol=0.02, fig=fig_pn(), alt="Abrupt PN junction.")
    frac = jh / (jh + je) * 100
    s.num(r"In that diode, what percentage of the current is carried by holes injected into the N side?",
          frac, "%",
          T(r"Each side's share is set by \(D/(NW)\): holes \(10^{-12}\), electrons \(3\times10^{-13}\). Hole fraction \(=\dfrac{1}{1.3}=<<p>>\%\)." "\n" r"The LIGHTLY doped side receives most of the injection: fewer majority carriers there means more minority carriers injected into it.", p=g_(frac, 4)),
          tol=0.01, fig=fig_pn(), alt="Abrupt PN junction.")
    dv = 1.5 * Vt * math.log(10) * 1e3
    s.mc(r"A real diode has ideality factor \(n=1.5\). How much must \(V_D\) increase per decade of current (\(V_t=25.9\ \mathrm{mV}\))?",
         T(r"About <<d>> mV", d=g_(dv, 3)),
         [r"About 59.6 mV", r"About 119 mV", r"About 38.9 mV"],
         T(r"\(\Delta V=nV_t\ln10=1.5\times59.6\ \mathrm{mV}=<<d>>\ \mathrm{mV}\)." "\n" r"• 59.6 mV is the ideal \(n=1\) value." "\n" r"• 119 mV would be \(n=2\)." "\n" r"• 38.9 mV is \(1.5\times V_t\) without the \(\ln10\).", d=g_(dv, 3)),
         fig=fig_iv(), alt="Diode I-V curve.")
    s.round(3)
    s.mc(r"Two identical diodes are connected in parallel and together carry the same total current that one diode carried before. How does the voltage change?",
         r"It drops by \(V_t\ln2\approx18\ \mathrm{mV}\): each diode carries half the current (equivalently, \(I_S\) doubles)",
         [r"It halves", r"It doesn't change", r"It drops by 60 mV"],
         r"Doubling the area doubles \(I_S\). For a fixed current, \(V=V_t\ln(I/I_S)\) falls by \(V_t\ln2=17.9\ \mathrm{mV}\). Exponential devices respond logarithmically to current or area changes: a factor of 10 is 60 mV, a factor of 2 is 18 mV.",
         fig=fig_iv(), alt="Diode I-V curve.")
    dv2 = Vt * math.log(2) * 1e3
    s.num(r"A diode's current doubles from 1 mA to 2 mA (\(n=1\), \(V_t=25.9\ \mathrm{mV}\)). By how much does \(V_D\) increase, in mV?",
          dv2, "mV",
          T(r"\(\Delta V=V_t\ln(I_2/I_1)=25.9\ \mathrm{mV}\times\ln2=<<d>>\ \mathrm{mV}\), independent of \(I_S\)." "\n" r"Gotcha: the diode isn't a 0.7 V battery, but it isn't far off: doubling the current costs only 18 mV.", d=g_(dv2, 4)),
          tol=0.01, fig=fig_iv(), alt="Diode I-V curve.")
    s.mc(r"For an ideal diode with \(I_S=10^{-14}\ \mathrm{A}\), what current flows at \(V_D=-5\ \mathrm{V}\)?",
         r"\(\approx-10^{-14}\ \mathrm{A}\) (that is, \(-I_S\))",
         [r"\(-10^{-14}e^{5/V_t}\ \mathrm{A}\), an enormous negative current", r"0 A exactly", r"\(+10^{-14}\ \mathrm{A}\)"],
         r"\(I=I_S(e^{-5/0.0259}-1)=I_S(e^{-193}-1)\approx-I_S\). The exponential term vanishes; only the \(-1\) survives. (Real diodes leak more because of generation in the depletion region, and break down at large reverse voltage.)",
         fig=fig_iv(), alt="Diode I-V curve.")
    s.round(4)
    I = 1e-3
    s.num(r"Preview of the small-signal model. Differentiate the diode law: what is the incremental resistance \(r_d=\left(\dfrac{dI_D}{dV_D}\right)^{-1}\) at \(I_D=1\ \mathrm{mA}\) (\(n=1\), \(V_t=25.9\ \mathrm{mV}\)), in Ω?",
          Vt / I, "Ω",
          r"\(\dfrac{dI_D}{dV_D}=\dfrac{I_Se^{V_D/V_t}}{V_t}\approx\dfrac{I_D}{V_t}\), so \(r_d=\dfrac{V_t}{I_D}=\dfrac{25.9\ \mathrm{mV}}{1\ \mathrm{mA}}=25.9\ \Omega\). The diode small-signal skill builds on this.",
          tol=0.01, fig=fig_iv(), alt="Diode I-V curve.", preview=["diode-ss"])
    IL, Is = 30e-3, 1e-12
    Voc = Vt * math.log(IL / Is + 1)
    s.num(r"Preview of solar cells. An illuminated diode is modeled as \(I=I_S(e^{V/V_t}-1)-I_L\) with \(I_L=30\ \mathrm{mA}\) and \(I_S=10^{-12}\ \mathrm{A}\). What is the open-circuit voltage (\(I=0\)), in V?",
          Voc, "V",
          T(r"\(I=0\Rightarrow e^{V/V_t}-1=I_L/I_S\Rightarrow V_{oc}=V_t\ln\!\left(\dfrac{I_L}{I_S}+1\right)=0.0259\ln(3\times10^{10})=<<v>>\ \mathrm{V}\)." "\n" r"The same diode law, now with the light current pushing it into forward bias.", v=g_(Voc, 4)),
          tol=0.01, fig=fig_iv("I–V of an illuminated diode"), alt="Diode I-V curve.", preview=["solar-cell"])
    s.mc(r"Preview of BJTs. A bipolar transistor's collector current follows the same law, \(I_C=I_Se^{V_{BE}/V_t}\). If \(V_{BE}\) rises by 60 mV, what happens to \(I_C\)?",
         r"It increases about 10×",
         [r"It doubles", r"It increases by 60 mA", r"It increases about 2.3×"],
         r"\(e^{0.060/0.0259}=e^{2.32}\approx10.1\): the 60 mV/decade rule carries straight over. BJT design reuses everything you know about the diode exponential.",
         fig=fig_iv(), alt="Diode I-V curve.", preview=["bjt-iv"])
    return s

# ====================================================================== diode-ss
def diode_ss():
    s = Skill('diode-ss')
    s.round(1)
    s.mc(r"The small-signal conductance of a forward-biased diode at bias current \(I_D\) is",
         r"\(g_d=\dfrac{I_D}{V_t}=\dfrac{qI_D}{kT}\)",
         [r"\(g_d=\dfrac{V_t}{I_D}\)", r"\(g_d=\dfrac{I_D}{V_D}\)", r"\(g_d=\dfrac{I_S}{V_t}\)"],
         r"\(g_d=\dfrac{dI_D}{dV_D}=\dfrac{qI_D}{kT}\) (reader Eq. 6.28): the slope of the exponential is proportional to the current itself. \(I_D/V_D\) is the large-signal ratio, a different (much smaller) number. \(V_t/I_D\) is \(r_d\), the reciprocal.",
         fig=fig_ss(), alt="Diode small-signal model: r_d in parallel with C_j and C_diff.")
    I = 0.5e-3
    s.num(r"What is the small-signal resistance \(r_d\) of a diode biased at 0.5 mA (\(V_t=25.9\ \mathrm{mV}\)), in Ω?",
          Vt / I, "Ω",
          r"\(r_d=\dfrac{V_t}{I_D}=\dfrac{25.9\ \mathrm{mV}}{0.5\ \mathrm{mA}}=51.8\ \Omega\).",
          tol=0.01, fig=fig_ss(), alt="Diode small-signal model.")
    s.mc(r"The diode small-signal model is valid when the signal voltage \(v_d\) satisfies",
         r"\(|v_d|\ll V_t\approx26\ \mathrm{mV}\)",
         [r"\(|v_d|\ll0.7\ \mathrm{V}\)", r"\(|v_d|\ll V_D\)", r"Any amplitude, as long as the diode is forward-biased"],
         r"Linearizing \(e^{v_d/V_t}\approx1+v_d/V_t\) requires \(v_d/V_t\ll1\) (reader Sec. 6.6). Even 10 mV gives a noticeable error. The relevant scale is \(V_t\), not the bias voltage.",
         fig=fig_iv(), alt="Diode I-V curve.")
    s.round(2)
    tau, I = 2e-9, 1e-3
    Cd = tau * I / Vt
    s.num(r"A diode with transit time \(\tau_F=2\ \mathrm{ns}\) is biased at 1 mA. What is its diffusion capacitance \(C_{diff}=\tau_F\dfrac{I_D}{V_t}\), in pF?",
          Cd * 1e12, "pF",
          T(r"\(C_{diff}=\tau_Fg_d=2\times10^{-9}\times\dfrac{10^{-3}}{0.0259}=<<c>>\ \mathrm{pF}\) (reader Eq. 6.33). It comes from stored minority charge \(Q_s=I_D\tau_F\).", c=g_(Cd * 1e12, 4)),
          tol=0.02, fig=fig_ss(), alt="Diode small-signal model.")
    Cj = 1.4 * 1e-12
    s.num(r"For that diode (\(C_{diff}=77.2\ \mathrm{pF}\)), \(C_{j0}=1\ \mathrm{pF}\). Using the reader's forward-bias estimate \(C_j\approx1.4C_{j0}\), what is the total small-signal capacitance, in pF?",
          (Cd + Cj) * 1e12, "pF",
          T(r"The two capacitances are in parallel (Fig. 6.14): \(C_{tot}=C_j+C_{diff}=1.4+77.2=<<c>>\ \mathrm{pF}\)." "\n" r"In forward bias at mA currents the diffusion capacitance dominates.", c=g_((Cd + Cj) * 1e12, 4)),
          tol=0.02, fig=fig_ss(), alt="Diode small-signal model.")
    s.mc(r"Which capacitance dominates the diode's small-signal model in strong forward bias, and which in reverse bias?",
         r"Forward: diffusion capacitance (grows with \(I_D\)); reverse: junction (depletion) capacitance, since \(C_{diff}\approx0\)",
         [r"Junction capacitance in both", r"Diffusion capacitance in both", r"Forward: junction; reverse: diffusion"],
         r"\(C_{diff}=\tau_FI_D/V_t\) is proportional to current, large in forward bias and negligible when \(I_D\approx-I_S\). \(C_j\) exists in both regions but is only a few pF; in reverse bias it's all that's left (and \(g_d\approx0\)).",
         fig=fig_ss(), alt="Diode small-signal model.")
    s.round(3)
    x = 10e-3 / Vt
    err = ((math.exp(x) - 1) / x - 1) * 100
    s.num(r"A diode is biased at \(I_D\) and a \(+10\ \mathrm{mV}\) step is applied. The exact current change is \(I_D(e^{v/V_t}-1)\); the small-signal estimate is \(g_dv\). By what percentage does the exact change exceed the estimate (\(V_t=25.9\ \mathrm{mV}\))?",
          err, "%",
          T(r"\(x=10/25.9=0.386\). Exact/linear \(=\dfrac{e^{x}-1}{x}=\dfrac{0.4712}{0.386}=1.2203\), so the estimate is <<e>>% low." "\n" r"Gotcha: 10 mV is not ≪ 26 mV. For a 1% error you need \(|v|\lesssim0.5\ \mathrm{mV}\).", e=g_(err, 4)),
          tol=0.02, fig=fig_iv(), alt="Diode I-V curve.")
    s.mc(r"Two diodes, one with 10× the area (10× \(I_S\)) of the other, are both biased at 1 mA. How do their small-signal resistances compare?",
         r"They are equal (\(r_d=V_t/I_D=25.9\ \Omega\)); the larger diode just needs a lower \(V_D\)",
         [r"The larger diode has 10× lower \(r_d\)", r"The larger diode has 10× higher \(r_d\)", r"The larger diode has \(\sqrt{10}\) lower \(r_d\)"],
         r"\(g_d=I_D/V_t\) contains no \(I_S\): at a given CURRENT the slope of an exponential is the same. Area only shifts the curve in voltage by \(V_t\ln10=60\ \mathrm{mV}\). (Its junction capacitance is larger, though.)",
         fig=fig_iv(), alt="Diode I-V curve.")
    s.mc(r"What is the small-signal model of a diode reverse-biased at \(-3\ \mathrm{V}\)?",
         r"Essentially just the junction capacitance \(C_j(-3\ \mathrm{V})\); \(g_d\approx0\) and \(C_{diff}\approx0\)",
         [r"A 25.9 Ω resistor", r"A short circuit", r"\(g_d=I_S/V_t\) in parallel with a large \(C_{diff}\)"],
         r"With \(I_D\approx-I_S\), \(g_d=\dfrac{dI}{dV}=\dfrac{I_Se^{V/V_t}}{V_t}\approx0\) and no minority charge is stored, so \(C_{diff}\approx0\). What's left is the depletion capacitance, which is how varactors are used. (\(I_S/V_t\) would be the conductance at zero bias, not at \(-3\ \mathrm{V}\).)",
         fig=fig_ss(), alt="Diode small-signal model.")
    s.round(4)
    I = 1e-3
    s.num(r"Preview of the BJT small-signal model. A BJT's collector current \(I_C=I_Se^{V_{BE}/V_t}\) has transconductance \(g_m=dI_C/dV_{BE}\). At \(I_C=1\ \mathrm{mA}\), what is \(g_m\), in mS?",
          I / Vt * 1e3, "mS",
          r"Same derivative as the diode: \(g_m=I_C/V_t=1\ \mathrm{mA}/25.9\ \mathrm{mV}=38.6\ \mathrm{mS}\). The BJT small-signal model starts from the diode's \(g_d\).",
          tol=0.01, fig=fig_ss(), alt="Diode small-signal model.", preview=["bjt-ss"])
    tau = 50e-12
    fT = 1 / (2 * math.pi * tau) / 1e9
    s.num(r"Preview of \(f_T\). When \(C_{diff}\) dominates, the diode's \(g_d\) and \(C_{diff}=\tau_Fg_d\) set a corner frequency \(\dfrac{g_d}{2\pi C_{diff}}\). For \(\tau_F=50\ \mathrm{ps}\), what is it, in GHz?",
          fT, "GHz",
          T(r"\(\dfrac{g_d}{2\pi\tau_Fg_d}=\dfrac{1}{2\pi\tau_F}=\dfrac{1}{2\pi\times50\times10^{-12}}=<<f>>\ \mathrm{GHz}\), independent of the current." "\n" r"Transistors have an analogous speed limit, their unity-gain frequency \(f_T\).", f=g_(fT, 4)),
          tol=0.02, fig=fig_ss(), alt="Diode small-signal model.", preview=["ft"])
    R, I = 1e3, 1e-3
    rd = Vt / I
    frac = rd / (R + rd) * 100
    s.mc(r"Preview of small-signal analysis. A diode is biased at 1 mA through \(R=1\ \mathrm{k\Omega}\) from a DC source, and a small AC signal is added to that source. What fraction of the AC signal appears across the diode?",
         T(r"About <<p>>%: \(r_d/(R+r_d)\) with \(r_d=25.9\ \Omega\)", p=g_(frac, 2)),
         [r"About 70%, since the diode drops 0.7 V", r"100%, since the diode is forward-biased", r"0%, since the DC source shorts AC"],
         T(r"For small signals, replace the DC source by a short (its AC part remains), and the diode by \(r_d=V_t/I_D=25.9\ \Omega\). Then it's a divider: \(\dfrac{25.9}{1025.9}=<<p>>\%\)." "\n" r"This 'DC bias, then linear small-signal circuit' recipe is the core of the small-signal-model skills.", p=g_(frac, 3)),
         fig=fig_diode_ckt("V_DC + v_s", "R = 1 kΩ", "Biased diode with a small AC signal"), alt="Source with DC and small AC parts, a 1 kΩ resistor and a diode to ground.", preview=["ss-model"])
    return s

BUILD = [diode_qual, diode_iv, diode_ss]
if __name__ == "__main__":
    for fn in BUILD:
        sk = fn(); sk.save(); print("wrote", sk.sid, len(sk.qs))
