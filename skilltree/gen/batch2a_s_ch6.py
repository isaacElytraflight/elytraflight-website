"""batch2a: excess-carriers, continuity, minority-profile"""
from batch2a_lib import *
import batch2a_fig as FG
import math

def X(*lines): return "\n".join(lines)

def excess_carriers():
    s = Skill('excess-carriers')
    s.round(1)
    s.mc(r"In n-type silicon, the excess hole concentration \(\Delta p\) is defined as:",
         r"\(\Delta p = p - p_0\), how far the hole concentration is above its thermal-equilibrium value \(p_0 = n_i^2/N_D\)",
         [r"\(\Delta p = p - n_i\)", r"\(\Delta p = N_D - p\)", r"\(\Delta p = p\cdot n - n_i^2\)"],
         X(r"Reader Eq. 6.3. Only the departure from equilibrium drives recombination or generation. In equilibrium, \(\Delta p = 0\) even though \(p_0 \neq n_i\) in doped material.",
           r"\(\Delta p\) can be negative too (fewer holes than in equilibrium, as next to a reverse-biased junction)."))
    frac = math.exp(-3)
    s.num(r"Excess holes in n-type silicon decay as \(\Delta p(t) = \Delta p(0)\,e^{-t/\tau_p}\) once the light is switched off. With \(\tau_p = 1\ \mu\mathrm{s}\), what fraction of the excess remains after 3 µs?",
          frac, "(fraction)",
          X(r"\[\frac{\Delta p(3\ \mu s)}{\Delta p(0)} = e^{-3} \approx " + g(frac, 3) + r"\]",
            r"About 5% after three lifetimes. This follows from \(\frac{d\Delta p}{dt} = -\frac{\Delta p}{\tau_p}\) (reader Eq. 6.4): the recombination rate is proportional to how many excess carriers there are."),
          figure=FG.plot([dict(fn=lambda t: math.exp(-t))], (0, 4), (0, 1.1), "t (µs)", "Δp/Δp(0)", w=330, h=200, xticks=[(1, "1"), (2, "2"), (3, "3")], marks=[(3, math.exp(-3), "?", 6, -8)], label="Exponential decay of excess holes"),
          alt="Plot of the excess hole fraction decaying exponentially from 1 at t = 0, with a marked point at t = 3 µs.")
    s.mc(r"In silicon, how do most electron–hole pairs recombine?",
         "Through 'traps': defect or impurity levels near the middle of the gap that capture an electron and then a hole",
         ["Directly across the gap, giving off a photon each time", "By two electrons colliding", "Only at the metal contacts"],
         X(r"Reader Sec. 6.3.2. Direct band-to-band recombination is very unlikely in silicon (an indirect-gap material). Instead, an R–G centre at energy \(E_t\) near mid-gap holds an electron temporarily until a hole arrives (and generation runs the same steps in reverse).",
           r"So material quality (the trap density \(N_T\)) controls the lifetime. That's also why silicon makes poor LEDs."),
         figure=FG.rg_centers(), alt="Band diagram with a dashed mid-gap trap level. Left: an electron drops from the conduction band to the trap, then to the valence band (recombination). Right: the reverse two-step process (generation).")
    s.round(2)
    R = 1e12 / 1e-6
    s.num(r"In n-type silicon, \(\Delta p = 10^{12}\ \mathrm{cm^{-3}}\) and \(\tau_p = 1\ \mu\mathrm{s}\). What is the net recombination rate \(\Delta p/\tau_p\)? Scientific notation is fine.",
          R, "cm⁻³s⁻¹",
          X(r"\[U = \frac{\Delta p}{\tau_p} = \frac{10^{12}}{10^{-6}} = 10^{18}\ \mathrm{cm^{-3}s^{-1}}\]",
            r"This is the NET rate: total recombination minus the steady thermal generation, which only the excess carriers drive."))
    GL, tau = 1e19, 10e-6
    s.num(r"Steady light generates \(G_L = 10^{19}\) electron–hole pairs per cm³ per second, uniformly in n-type silicon with \(\tau_p = 10\ \mu\mathrm{s}\). What is the steady-state excess hole concentration?",
          GL * tau, "cm⁻³",
          X(r"In steady state, generation balances net recombination: \(G_L = \Delta p/\tau_p\), so",
            r"\[\Delta p = G_L\tau_p = (10^{19})(10^{-5}) = 10^{14}\ \mathrm{cm^{-3}}\]",
            r"A longer lifetime lets more excess carriers build up for the same light. That's why solar-cell material must be high quality."))
    s.mc(r"The minority-carrier lifetime is \(\tau_p = 1/(c_pN_T)\), where \(N_T\) is the trap density. A process step accidentally doubles \(N_T\) (say, metal contamination). What happens to \(\tau_p\), and to the excess holes under the same steady light?",
         "τp halves, and the steady-state excess Δp = G_L τp also halves",
         ["τp doubles, because there are more places for carriers to rest", "τp is unchanged; only generation is affected", "τp halves, but Δp stays the same because G_L is unchanged"],
         X(r"More traps give minority carriers more chances to recombine, so they live shorter: \(\tau_p \propto 1/N_T\) (reader Eq. 6.4). Then \(\Delta p = G_L\tau_p\) halves too.",
           r"Lifetime can range from nanoseconds to microseconds depending on process quality."))
    s.round(3)
    s.mc(r"n-type silicon (\(N_D = 10^{16}\ \mathrm{cm^{-3}}\)) is lit, generating \(\Delta n = \Delta p = 10^{13}\ \mathrm{cm^{-3}}\). Which carrier's LIFETIME sets how fast the excess decays, and why?",
         "The minority holes': a hole is surrounded by electrons and recombines quickly, while the majority electron count is essentially unchanged",
         ["The majority electrons', because there are more of them", "Both lifetimes average together equally", "Neither; recombination depends only on the trap density"],
         X(r"Each recombination removes one electron and one hole. The rate is limited by the scarce carrier, the hole, which easily finds an electron. So \(\frac{d\Delta p}{dt} = -\Delta p/\tau_p\) with the MINORITY lifetime.",
           r"Gotcha: majority carriers don't have a meaningful 'lifetime' here. Their relative change is tiny (\(10^{13}\) on \(10^{16}\)). This is low-level injection: \(\Delta p \ll N_D\)."))
    t1 = 2e-6 * math.log(100)
    s.num(r"With \(\tau_p = 2\ \mu\mathrm{s}\), how long after the light is switched off does the excess hole concentration fall to 1% of its starting value? Answer in µs.",
          t1 * 1e6, "µs",
          X(r"\[e^{-t/\tau_p} = 0.01 \Rightarrow t = \tau_p\ln100 = 2\ \mu\mathrm{s}\times4.605 \approx " + g(t1 * 1e6, 3) + r"\ \mu\mathrm{s}\]",
            r"Gotcha: it isn't \(100\tau_p\) or \(2\tau_p\) (the time for a half-life is \(\tau_p\ln2\)). Each lifetime cuts the excess by \(e\), so getting down to 1% takes 4.6 lifetimes. Stored minority charge also limits how fast a diode switches off."))
    s.mc(r"Next to a reverse-biased junction, the minority holes in the n-region are swept away, so \(p < p_0\) (that is, \(\Delta p < 0\)). What does \(\frac{d\Delta p}{dt} = -\frac{\Delta p}{\tau_p}\) say happens there?",
         "Net thermal GENERATION: the rate −Δp/τp is positive, so carriers are created to push p back toward p₀",
         ["Net recombination continues, making p even smaller", "Nothing, because the equation only applies to excess carriers", "Generation stops completely"],
         X(r"With \(\Delta p < 0\), \(-\Delta p/\tau_p > 0\): generation now beats recombination (\(np < n_i^2\), so \(G > R\)).",
           r"Gotcha: the same law covers both directions. This generation near the junction feeds the reverse-bias leakage current."))
    s.round(4)
    Lp = math.sqrt(10 * 1e-6)
    s.num(r"Preview of the diffusion length: excess holes injected at one point both diffuse and recombine. A later skill shows they travel about \(L_p = \sqrt{D_p\tau_p}\) before recombining. For \(D_p = 10\ \mathrm{cm^2/s}\) and \(\tau_p = 1\ \mu\mathrm{s}\), find \(L_p\) in µm.",
          Lp * 1e4, "µm",
          X(r"\[L_p = \sqrt{D_p\tau_p} = \sqrt{10\times10^{-6}} = \sqrt{10^{-5}}\ \mathrm{cm} = 3.16\times10^{-3}\ \mathrm{cm} \approx " + g(Lp * 1e4, 3) + r"\ \mu\mathrm{m}\]",
            r"Tens of micrometres: much longer than the depletion regions and often longer than the device itself. When the region is SHORTER than \(L_p\), carriers cross before they can recombine. That's the key to diodes and bipolar transistors."),
          preview=["continuity", "minority-profile"])
    GL2 = 1e20
    dsig = q * GL2 * 1e-6 * (1000 + 400)
    s.num(r"Preview of optical generation: a photodetector region is lit with \(G_L = 10^{20}\ \mathrm{cm^{-3}s^{-1}}\), and \(\tau = 1\ \mu\mathrm{s}\). The extra pairs raise the conductivity by \(\Delta\sigma = q\,\Delta n(\mu_n + \mu_p)\), with \(\mu_n = 1000\) and \(\mu_p = 400\ \mathrm{cm^2/(V\cdot s)}\). Find \(\Delta\sigma\) in mS/cm.",
          dsig * 1e3, "mS/cm",
          X(r"\(\Delta n = \Delta p = G_L\tau = 10^{14}\ \mathrm{cm^{-3}}\), and both carriers add to the conductivity:",
            r"\[\Delta\sigma = (1.602\times10^{-19})(10^{14})(1400) \approx " + sci(dsig, 3) + r"\ \mathrm{S/cm} = " + g(dsig * 1e3, 3) + r"\ \mathrm{mS/cm}\]",
            r"That is a photoconductor. Solar cells and photodiodes instead use a junction's field to collect these pairs as a current."),
          preview=["solar-cell"])
    s.mc(r"Preview of injected minority carriers: a forward-biased junction keeps injecting holes into an n-region. In steady state, what stops the hole concentration from building up indefinitely farther into the n-region?",
         "Recombination: holes are lost at the rate Δp/τp as they diffuse, so the excess dies out a few diffusion lengths from the junction",
         ["The electric field in the n-region pushes them back", "They pile up until they equal the electron concentration", "The metal contact absorbs them immediately, at any distance"],
         X(r"Steady state means injection is balanced by recombination. Combined with diffusion, that gives an excess that decays roughly as \(e^{-x/L_p}\) (next skills: continuity and minority-carrier profiles).",
           r"The electrons that recombine with the holes are supplied by the majority current, which keeps the total current constant along the device."),
         preview=["minority-profile", "continuity"])
    return s

def continuity():
    s = Skill('continuity')
    s.round(1)
    Lp = math.sqrt(12 * 0.5e-6)
    s.num(r"Holes in n-type silicon have \(D_p = 12\ \mathrm{cm^2/s}\) and \(\tau_p = 0.5\ \mu\mathrm{s}\). What is the diffusion length \(L_p = \sqrt{D_p\tau_p}\), in µm?",
          Lp * 1e4, "µm",
          X(r"\[L_p = \sqrt{12\times0.5\times10^{-6}} = \sqrt{6\times10^{-6}}\ \mathrm{cm} = " + sci(Lp, 3) + r"\ \mathrm{cm} \approx " + g(Lp * 1e4, 3) + r"\ \mu\mathrm{m}\]",
            r"Common mistake: forgetting the square root, or entering \(\tau\) in µs (giving 2.45 cm)."))
    s.mc(r"Excess holes are continuously injected at \(x = 0\) into a long n-type region, with \(\Delta p(\infty) = 0\). In steady state, \(\frac{d^2\Delta p}{dx^2} = \frac{\Delta p}{L_p^2}\). What is the profile?",
         r"\(\Delta p(x) = \Delta p(0)\,e^{-x/L_p}\)",
         [r"\(\Delta p(x) = \Delta p(0)(1 - x/L_p)\)", r"\(\Delta p(x) = \Delta p(0)\,e^{+x/L_p}\)", r"\(\Delta p(x) = \Delta p(0)\cos(x/L_p)\)"],
         X(r"The general solution is \(Ae^{-x/L_p} + Be^{x/L_p}\) (reader Eq. 6.13). \(\Delta p(\infty) = 0\) forces \(B = 0\), and the value at \(x = 0\) gives \(A = \Delta p(0)\).",
           r"A straight line is the no-recombination (short-region) case. A cosine would solve \(\Delta p'' = -\Delta p/L^2\), which has the wrong sign."),
         figure=FG.profile_decay(), alt="Excess hole concentration Δp(x) decaying exponentially from Δp(0) at x = 0; at x = Lp it has fallen to Δp(0)/e.")
    s.mc(r"What does the diffusion length \(L_p\) represent physically?",
         "The typical distance an excess minority carrier diffuses before it recombines; at x = Lp the excess has fallen to 1/e of its starting value",
         ["The width of the depletion region", "The distance a carrier moves between collisions", "The distance at which the excess has fallen exactly to zero"],
         X(r"\(L_p = \sqrt{D_p\tau_p}\) combines how fast carriers spread (\(D_p\)) with how long they last (\(\tau_p\)). It's typically micrometres to millimetres, far longer than the mean free path (about 10 nm) and usually longer than the depletion width.",
           r"An exponential never reaches exactly zero; after \(3L_p\) about 5% remains."))
    s.round(2)
    d0 = 1e14
    Lp2 = 25e-4
    v = d0 * math.exp(-50e-4 / Lp2)
    s.num(r"Excess holes are injected with \(\Delta p(0) = 10^{14}\ \mathrm{cm^{-3}}\) into a long n-region with \(L_p = 25\ \mu\mathrm{m}\). What is \(\Delta p\) at \(x = 50\ \mu\mathrm{m}\)? Scientific notation is fine.",
          v, "cm⁻³",
          X(r"\[\Delta p(50\ \mu m) = 10^{14}e^{-50/25} = 10^{14}e^{-2} \approx " + sci(v, 3) + r"\ \mathrm{cm^{-3}}\]",
            r"Two diffusion lengths, so \(e^{-2} \approx 13.5\%\) is left."))
    J0 = q * 12 * d0 / Lp
    s.num(r"Holes are injected into a long n-region with \(\Delta p(0) = 10^{14}\ \mathrm{cm^{-3}}\), \(D_p = 12\ \mathrm{cm^2/s}\) and \(L_p = " + g(Lp * 1e4, 3) + r"\ \mu\mathrm{m}\). What is the hole diffusion current density at \(x = 0\), in mA/cm²?",
          J0 * 1e3, "mA/cm²",
          X(r"\[J_p(x) = -qD_p\frac{d\Delta p}{dx} = \frac{qD_p\Delta p(0)}{L_p}e^{-x/L_p}\]",
            r"\[J_p(0) = \frac{(1.602\times10^{-19})(12)(10^{14})}{" + sci(Lp, 3) + r"} = " + sci(J0, 3) + r"\ \mathrm{A/cm^2} \approx " + g(J0 * 1e3, 3) + r"\ \mathrm{mA/cm^2}\]",
            r"It's like a linear profile that drops to zero over one diffusion length. (Reader Eq. 6.15 leaves out the factor \(qD_p\) in this result. That's a typo; the units only work with it.)"))
    s.num(r"Same region (\(J_p(0) = " + g(J0 * 1e3, 3) + r"\ \mathrm{mA/cm^2}\)). What is the hole diffusion current density at \(x = L_p\), in mA/cm²?",
          J0 / math.e * 1e3, "mA/cm²",
          X(r"The current is proportional to the slope, which decays like the profile itself:",
            r"\[J_p(L_p) = J_p(0)e^{-1} = " + g(J0 * 1e3, 3) + r"\times0.368 \approx " + g(J0 / math.e * 1e3, 3) + r"\ \mathrm{mA/cm^2}\]",
            r"The 'missing' hole current became recombination between 0 and \(L_p\). The next question asks where it went."))
    s.round(3)
    s.mc(r"In the long n-region above, the hole current decays as \(e^{-x/L_p}\), yet in steady state the TOTAL current through the device has to be the same at every \(x\). How?",
         "Majority electrons carry the rest: an electron current flows in to recombine with the holes, so Jₙ(x) + Jₚ(x) = Jₚ(0) everywhere",
         ["The total current also decays; charge builds up in the n-region", "The lost holes leave through the sides of the device", "Displacement current makes up the difference"],
         X(r"Each recombination removes one hole and one electron. The electrons come from the n-contact as majority current, so where \(J_p\) shrinks, \(J_n\) grows by the same amount (reader Sec. 6.4.3).",
           r"Gotcha: 'current decays' sounds like charge is lost, but it only changes CARRIER TYPE. In steady state nothing builds up and nothing changes in time, so there's no displacement current."),
         figure=FG.profile_decay(ylabel="J_p(x)", y0_label="J_p(0)", L_label="L_p"), alt="Hole current density Jp(x) decaying exponentially from Jp(0); the remainder of the constant total current is carried by electrons.")
    s.num(r"In that long n-region, what fraction of the total current is carried by HOLES at \(x = 2L_p\)?",
          math.exp(-2), "(fraction)",
          X(r"The total current equals \(J_p(0)\) everywhere, and the hole part is \(J_p(0)e^{-x/L_p}\):",
            r"\[\frac{J_p(2L_p)}{J_{total}} = e^{-2} \approx 0.135\]",
            r"The other 86.5% is electron current at that point. By about 5 diffusion lengths, essentially all the current is carried by majority carriers, as in an ordinary resistor."))
    s.mc(r"An n-region is only \(W = 1\ \mu\mathrm{m}\) long, with \(L_p = 25\ \mu\mathrm{m}\). Holes are injected at \(x = 0\), and an ohmic contact at \(x = W\) holds \(\Delta p(W) = 0\). What does the excess-hole profile look like?",
         "Nearly a straight line from Δp(0) to 0: almost no recombination happens, so the hole current is nearly the same at every x",
         ["An exponential with decay length Lp, cut off at W", "An exponential with decay length W", "Flat at Δp(0) up to W, then a sudden drop to zero"],
         X(r"With \(W \ll L_p\), the \(\Delta p/L_p^2\) term is negligible: \(\Delta p'' \approx 0\), so the profile is LINEAR (reader Sec. 6.5.2 and Fig. 6.11). A constant slope means a constant current: \(J_p = qD_p\Delta p(0)/W\).",
           r"Gotcha: copying the long-region exponential gets both the shape and the current wrong. The current is larger by about \(L_p/W\), because the gradient is much steeper."),
         figure=FG.profile_decay(long=True), alt="Excess hole concentration falling in a straight line from Δp(0) at x = 0 to zero at x = W.")
    s.round(4)
    Js = q * 12 * 1e14 / 2e-4
    s.num(r"Preview of the diode equation: holes are injected with \(\Delta p(0) = 10^{14}\ \mathrm{cm^{-3}}\) into a SHORT n-region of width \(W_n = 2\ \mu\mathrm{m}\) (\(\ll L_p\)), with \(D_p = 12\ \mathrm{cm^2/s}\). What hole current density flows, in A/cm²?",
          Js, "A/cm²",
          X(r"Linear profile, so the slope is \(\Delta p(0)/W_n\):",
            r"\[J_p = \frac{qD_p\Delta p(0)}{W_n} = \frac{(1.602\times10^{-19})(12)(10^{14})}{2\times10^{-4}} \approx " + g(Js, 3) + r"\ \mathrm{A/cm^2}\]",
            r"That's about " + g(Js / J0, 3) + r" times the long-region value, because \(L_p/W_n\) is that big. In the diode skill, \(\Delta p(0)\) is set by the applied voltage."),
          preview=["minority-profile", "diode-iv"])
    s.mc(r"Preview of the bipolar transistor: a BJT injects minority electrons into a thin p-type 'base', and they must diffuse across it to be collected on the other side. Why is the base made much thinner than the electrons' diffusion length \(L_n\)?",
         "So that almost every injected electron crosses before it recombines; recombination in the base would waste current",
         ["So that the electrons recombine quickly, which keeps the transistor cool", "To make the electron profile exponential instead of linear", "Because a thin base has a longer lifetime"],
         X(r"With \(W_B \ll L_n\) the profile is nearly linear, and only a tiny fraction (of order \((W_B/L_n)^2\)) of the electrons recombine. So the current that leaves is almost all of the current injected.",
           r"That near-perfect transfer is what makes 'transistor action' possible; the BJT skills build on it."),
         preview=["bjt-action"])
    dp0 = 1e4 * (math.exp(0.6 / kTq) - 1)
    Jd = q * 12 * dp0 / Lp
    s.num(r"Preview of forward-biased diodes: forward bias \(V\) raises the hole concentration at the edge of an n-region to \(p_{n0}e^{V/(kT/q)}\), so \(\Delta p(0) = p_{n0}(e^{V/V_{th}} - 1)\). For \(N_D = 10^{16}\ \mathrm{cm^{-3}}\) (\(p_{n0} = 10^{4}\)) and \(V = 0.6\ \mathrm{V}\) (\(V_{th} = 26\ \mathrm{mV}\)), with a long n-region (\(D_p = 12\ \mathrm{cm^2/s}\), \(L_p = " + g(Lp * 1e4, 3) + r"\ \mu\mathrm{m}\)), find the hole current density at the edge, in mA/cm².",
          Jd * 1e3, "mA/cm²",
          X(r"\[\Delta p(0) = 10^{4}\left(e^{0.6/0.026} - 1\right) = 10^{4}e^{23.08} \approx " + sci(dp0, 3) + r"\ \mathrm{cm^{-3}}\]",
            r"\[J_p = \frac{qD_p\Delta p(0)}{L_p} = \frac{(1.602\times10^{-19})(12)(" + sci(dp0, 3) + r")}{" + sci(Lp, 3) + r"} \approx " + g(Jd * 1e3, 3) + r"\ \mathrm{mA/cm^2}\]",
            r"Every 60 mV of extra forward bias multiplies this by 10: the exponential diode law."),
          tol=0.03, preview=["diode-iv", "minority-profile"])
    return s

def minority_profile():
    s = Skill('minority-profile')
    s.round(1)
    pe = 1e4 * math.exp(0.6 / kTq)
    s.num(r"A diode's n-side has \(N_D = 10^{16}\ \mathrm{cm^{-3}}\), so \(p_{n0} = n_i^2/N_D = 10^{4}\ \mathrm{cm^{-3}}\). At a forward bias of \(V_D = 0.6\ \mathrm{V}\), what is the hole concentration at the n-side edge of the depletion region, \(p_n(x_n) = p_{n0}e^{V_D/V_{th}}\)? (\(V_{th} = 26\ \mathrm{mV}\)) Scientific notation is fine.",
          pe, "cm⁻³",
          X(r"\[p_n(x_n) = 10^{4}\exp\!\left(\frac{0.6}{0.026}\right) = 10^{4}e^{23.08} \approx " + sci(pe, 3) + r"\ \mathrm{cm^{-3}}\]",
            r"That's 10 orders of magnitude above equilibrium, yet still well below \(N_D = 10^{16}\), so low-level injection holds. (Rule of thumb: 0.6 V / 60 mV = 10 decades.)"),
          tol=0.03)
    s.mc(r"Boltzmann's law at the junction edge is written \(p_n(x_n) = N_Ae^{-(\varphi_{bi}-V_D)/V_{th}}\). What does \(N_A\) represent here, and what happens at \(V_D = 0\)?",
         r"\(N_A\) is the majority-hole concentration on the OTHER (P) side; at \(V_D = 0\) the expression reduces to \(p_{n0} = n_i^2/N_D\)",
         [r"\(N_A\) is the acceptor density on the N side; at \(V_D = 0\) it gives \(n_i\)", r"\(N_A\) is the hole concentration at the edge; at \(V_D = 0\) the expression is zero", r"\(N_A\) is the minority concentration; at \(V_D = 0\) it gives \(N_A\)"],
         X(r"Holes on the P side (\(p \approx N_A\)) must climb the barrier \(\varphi_{bi} - V_D\) to reach the N-side edge (reader Eq. 6.17–6.18, Note 1).",
           r"At \(V_D = 0\): \(N_Ae^{-\varphi_{bi}/V_{th}} = N_A\cdot\frac{n_i^2}{N_AN_D} = \frac{n_i^2}{N_D}\), the equilibrium value (Note 2). Forward bias multiplies it by \(e^{V_D/V_{th}}\).",
           r"(Reader Eq. 6.18 labels this 'minority e⁻ concentration'. That's a typo: \(p_n\) is the minority HOLE concentration on the N side.)"))
    s.mc(r"Under forward bias, what do the minority-carrier profiles look like in the two neutral regions when both are much LONGER than the diffusion lengths?",
         "Raised to their Boltzmann values at the depletion edges, then decaying exponentially (over Lₚ and Lₙ) back to equilibrium",
         ["Constant across each neutral region", "Rising linearly toward the contacts", "Zero at the depletion edges and maximum at the contacts"],
         X(r"Injection sets the edge values; diffusion plus recombination (\(\Delta p'' = \Delta p/L_p^2\)) gives \(e^{-x/L}\) decay (reader Fig. 6.10).",
           r"In SHORT regions (\(W \ll L\)) the profiles are straight lines down to the equilibrium value at the contacts (Fig. 6.11)."),
         figure=FG.profile_decay(ylabel="p_n(x)", y0_label="p_n(x_n)", L_label="x_n + L_p"), alt="Hole concentration on the n side of a forward-biased junction: highest at the depletion edge xn and decaying exponentially, falling by a factor of e at one diffusion length.")
    s.round(2)
    NA, ND = 1e17, 1e16
    pb = kTq * math.log(NA * ND / ni ** 2)
    pe2 = NA * math.exp(-(pb - 0.5) / kTq)
    s.num(r"A junction has \(N_A = 10^{17}\) and \(N_D = 10^{16}\ \mathrm{cm^{-3}}\), so \(\varphi_{bi} = " + g(pb, 4) + r"\ \mathrm{V}\). Using \(p_n(x_n) = N_Ae^{-(\varphi_{bi}-V_D)/V_{th}}\), find the edge hole concentration at \(V_D = 0.5\ \mathrm{V}\). (\(V_{th} = 26\ \mathrm{mV}\)) Scientific notation is fine.",
          pe2, "cm⁻³",
          X(r"\[p_n(x_n) = 10^{17}\exp\!\left(-\frac{" + g(pb, 4) + r" - 0.5}{0.026}\right) = 10^{17}e^{-" + g((pb - 0.5) / kTq, 4) + r"} \approx " + sci(pe2, 3) + r"\ \mathrm{cm^{-3}}\]",
            r"Check with the other form: \(p_{n0}e^{V_D/V_{th}} = 10^{4}e^{19.23} = " + sci(1e4 * math.exp(0.5 / kTq), 3) + r"\) ✔. Both forms are the same law."),
          tol=0.03)
    s.num(r"Same junction (\(N_A = 10^{17}\), \(N_D = 10^{16}\ \mathrm{cm^{-3}}\)) at the same forward bias. What is the ratio of injected hole concentration at the n-edge to injected electron concentration at the p-edge, \(p_n(x_n)/n_p(-x_p)\)?",
          NA / ND, "(ratio)",
          X(r"Both edges get the same factor \(e^{V_D/V_{th}}\) above equilibrium:",
            r"\[\frac{p_n(x_n)}{n_p(-x_p)} = \frac{n_i^2/N_D}{n_i^2/N_A} = \frac{N_A}{N_D} = 10\]",
            r"The heavily doped side injects more minority carriers into the lightly doped side. That's why a BJT's emitter is doped much more heavily than its base."))
    pr = 1e4 * math.exp(-0.2 / kTq)
    s.num(r"Now the \(N_D = 10^{16}\ \mathrm{cm^{-3}}\) diode is REVERSE biased at \(V_D = -0.2\ \mathrm{V}\). What is the hole concentration at the n-side depletion edge, \(p_{n0}e^{V_D/V_{th}}\)? (\(p_{n0} = 10^{4}\ \mathrm{cm^{-3}}\), \(V_{th} = 26\ \mathrm{mV}\))",
          pr, "cm⁻³",
          X(r"\[p_n(x_n) = 10^{4}e^{-0.2/0.026} = 10^{4}e^{-7.69} \approx " + g(pr, 3) + r"\ \mathrm{cm^{-3}}\]",
            r"Essentially zero next to \(p_{n0} = 10^{4}\): the edge is drained of minority carriers (\(\Delta p \approx -p_{n0}\)). Nearby holes diffuse toward the edge and are swept across, and thermal generation replaces them. That's the small reverse saturation current."),
          tol=0.03)
    s.round(3)
    pbad = 1e4 * math.exp(0.8 / kTq)
    s.mc(r"Someone applies \(V_D = 0.8\ \mathrm{V}\) to the \(N_D = 10^{16}\ \mathrm{cm^{-3}}\) diode and computes \(p_n(x_n) = 10^{4}e^{0.8/0.026} \approx " + sci(pbad, 2) + r"\ \mathrm{cm^{-3}}\). What's wrong?",
         r"Low-level injection has failed: the injected holes exceed the majority \(N_D = 10^{16}\), so the Boltzmann edge law (which assumes \(p_n \ll N_D\)) no longer holds",
         ["Nothing; the formula is exact at any bias", r"The exponent should be \(-V_D/V_{th}\)", r"The answer must be capped at \(n_i\)"],
         X(r"Reader Note 3: the edge relations need \(p_n \ll N_D\) and \(n_p \ll N_A\). At \(" + sci(pbad, 2) + r"\ \mathrm{cm^{-3}}\) the 'minority' holes outnumber the electrons, so charge neutrality forces \(n\) up as well, and the simple law breaks down.",
           r"Gotcha: real diodes at high current depart from the ideal \(e^{V/V_{th}}\) behaviour (and series resistance adds to the problem)."))
    dv = kTq * math.log(10) * 1e3
    s.num(r"By how many millivolts must the forward bias increase to multiply the injected minority concentration at the junction edge by exactly 10? (\(V_{th} = 26\ \mathrm{mV}\))",
          dv, "mV",
          X(r"\[e^{\Delta V/V_{th}} = 10 \Rightarrow \Delta V = V_{th}\ln10 = 26\times2.303 \approx " + g(dv, 3) + r"\ \mathrm{mV}\]",
            r"Gotcha: it's not 26 mV (that gives a factor of \(e\)) and not 10 times the voltage. Since the diffusion current is proportional to this edge concentration, a diode's current rises 10 times for about every 60 mV."))
    s.mc(r"Both neutral regions of a diode are SHORT (\(W \ll L\)), so the injected profiles are straight lines from the edge values down to the equilibrium values at the contacts. If the n-region width \(W_n\) is cut in half, what happens to the hole current?",
         "It doubles: the same concentration drop over half the distance gives twice the gradient",
         ["It halves, because there's less volume for holes to diffuse through", "It is unchanged, because the edge concentration sets the current", "It increases by √2"],
         X(r"\[J_p = qD_p\frac{p_n(x_n) - p_{n0}}{W_n} \propto \frac{1}{W_n}\]",
           r"Gotcha: the edge concentration is fixed by the voltage, but the CURRENT depends on the slope. This is reader Eq. 6.24 (short-diode form). In long regions \(L_p\) takes the place of \(W_n\)."),
         figure=FG.profile_decay(long=True, ylabel="Δp_n(x)", y0_label="Δp_n(x_n)"), alt="Excess hole concentration in a short n-region, falling in a straight line from its edge value to zero at the contact a distance W away.")
    s.round(4)
    Jp = q * 10 * 1e4 * (math.exp(0.6 / kTq) - 1) / 1e-4
    s.num(r"Preview of the ideal diode equation: in a short diode the hole current is \(J_p = \frac{qD_p}{W_n}p_{n0}\left(e^{V_D/V_{th}} - 1\right)\). Take \(D_p = 10\ \mathrm{cm^2/s}\), \(W_n = 1\ \mu\mathrm{m}\), \(p_{n0} = 10^{4}\ \mathrm{cm^{-3}}\) and \(V_D = 0.6\ \mathrm{V}\). Find \(J_p\) in A/cm².",
          Jp, "A/cm²",
          X(r"\[J_p = \frac{(1.602\times10^{-19})(10)}{10^{-4}}(10^{4})\left(e^{23.08}-1\right) \approx " + g(Jp, 3) + r"\ \mathrm{A/cm^2}\]",
            r"Over a \(10\ \mu\mathrm{m}\times10\ \mu\mathrm{m}\) diode (\(10^{-6}\ \mathrm{cm^2}\)) that's about " + g(Jp * 1e6 * 1e6, 3) + r" µA. Adding the electron term from the P side gives the full ideal diode equation, \(I = I_S(e^{V_D/V_{th}} - 1)\)."),
          tol=0.03, preview=["diode-iv"])
    fh = (10 * 1e4 / 1e-4) / (10 * 1e4 / 1e-4 + 25 * 1e3 / 1e-4)
    s.num(r"Preview of injection efficiency: in a short diode both sides contribute. The hole term is \(\propto D_pp_{n0}/W_n\) and the electron term is \(\propto D_nn_{p0}/W_p\). Take \(D_p = 10\), \(p_{n0} = 10^{4}\) (\(N_D = 10^{16}\)), \(D_n = 25\ \mathrm{cm^2/s}\), \(n_{p0} = 10^{3}\) (\(N_A = 10^{17}\)) and \(W_n = W_p = 1\ \mu\mathrm{m}\). What fraction of the total diode current is carried by holes?",
          fh, "(fraction)",
          X(r"\[\frac{J_p}{J_p + J_n} = \frac{D_pp_{n0}}{D_pp_{n0} + D_nn_{p0}} = \frac{10\times10^{4}}{10\times10^{4} + 25\times10^{3}} = \frac{10^{5}}{1.25\times10^{5}} = " + g(fh, 3) + r"\]",
            r"The side that injects more is the more heavily doped one (the P side here injects holes into the N side). In a BJT the emitter is doped very heavily so this fraction, the 'emitter efficiency', is close to 1."),
          preview=["diode-iv", "bjt-action"])
    s.mc(r"Preview of the BJT: in a forward-active NPN transistor, the emitter junction is forward biased (raising the electron concentration at the base's emitter edge), and the collector junction is reverse biased (draining the electrons at the base's collector edge). With a base much shorter than \(L_n\), what is the electron profile across the base?",
         "A straight line from a high value at the emitter edge down to about zero at the collector edge; its slope sets the collector current",
         ["An exponential decaying from the collector edge", "Flat across the base, so there is no current", "Highest in the middle of the base"],
         X(r"Edge values: forward-biased emitter junction, \(n_{p0}e^{V_{BE}/V_{th}}\); reverse-biased collector junction, about 0. In a short region the profile between them is linear, so a uniform diffusion current flows across the base and is swept into the collector.",
           r"That's the core of bipolar transistor action: the collector current is controlled exponentially by \(V_{BE}\)."),
         preview=["bjt-action"])
    return s
