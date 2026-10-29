"""batch2a: mos-struct, mos-regions, vt, mos-fields, mos-cv"""
from batch2a_lib import *
import batch2a_fig as FG
import math
def X(*l): return "\n".join(l)
Vth = kTq
PHG = 0.55  # reader: n+ poly at +550 mV
def phip(NA): return -Vth * math.log(NA / ni)

def mos_struct():
    s = Skill('mos-struct')
    s.round(1)
    cox = eps_ox / 2e-7
    s.num(r"Compute the oxide capacitance per area \(C_{ox} = \varepsilon_{ox}/t_{ox}\) for \(t_{ox} = 2\ \mathrm{nm}\) (\(\varepsilon_{ox} = 3.45\times10^{-13}\ \mathrm{F/cm}\)), in fF/µm².",
          cox * 1e7, "fF/µm²",
          X(r"\[C_{ox} = \frac{3.45\times10^{-13}}{2\times10^{-7}} = 1.725\times10^{-6}\ \mathrm{F/cm^2}\]",
            r"Since \(1\ \mathrm{F/cm^2} = 10^{7}\ \mathrm{fF/\mu m^2}\), this is \(" + g(cox * 1e7, 4) + r"\ \mathrm{fF/\mu m^2}\)."),
          figure=FG.mos_stack('flatband'), alt="MOS capacitor cross-section: a gate on top, a thin oxide layer of thickness tox, and a p-type silicon substrate with a body contact.")
    s.mc(r"In an n+ poly / SiO₂ / p-Si MOS capacitor, which layer stops DC current from flowing between the gate and the body?",
         "The SiO₂ gate oxide, an insulator", ["The n+ polysilicon gate", "The p-type substrate", "The depletion region in the silicon"],
         X(r"The oxide is an excellent insulator (band gap about 9 eV). So the structure is a capacitor: charge on the gate is mirrored by charge in the silicon, and no DC current flows through.",
           r"The gate is a heavily doped conductor, and the substrate is a conducting semiconductor body."))
    pb = PHG - phip(1e17)
    s.num(r"An n+ poly gate sits at \(\varphi_{n^+} \approx +0.55\ \mathrm{V}\) relative to intrinsic silicon (the reader's value for degenerate n+ poly). It is on p-Si with \(N_A = 10^{17}\ \mathrm{cm^{-3}}\). Treating the stack like a junction, the built-in potential is \(\varphi_{bi} = \varphi_{n^+} - \varphi_p\) (\(V_{th} = 26\ \mathrm{mV}\), \(n_i = 10^{10}\)). Find \(\varphi_{bi}\) in V.",
          pb, "V",
          X(r"\[\varphi_p = -0.026\ln(10^{7}) = -0.419\ \mathrm{V}\]",
            r"\[\varphi_{bi} = 0.55 + 0.419 \approx " + g(pb, 3) + r"\ \mathrm{V}\]",
            r"The n+ gate's potential is capped near \(+0.55\ \mathrm{V}\) (its Fermi level reaches the conduction-band edge), so we don't use \(\ln(N_D/n_i)\) for degenerate doping."))
    s.round(2)
    C = eps_ox / 5e-7 * 100e-8
    s.num(r"A MOS capacitor has a \(10\ \mu\mathrm{m}\times10\ \mu\mathrm{m}\) gate with \(t_{ox} = 5\ \mathrm{nm}\). What is its oxide capacitance, in fF?",
          C * 1e15, "fF",
          X(r"\[C_{ox} = \frac{3.45\times10^{-13}}{5\times10^{-7}} = 6.9\times10^{-7}\ \mathrm{F/cm^2} = 6.9\ \mathrm{fF/\mu m^2}\]",
            r"\[C = 6.9\times100\ \mu\mathrm{m^2} = " + g(C * 1e15, 3) + r"\ \mathrm{fF}\]"))
    vfb = -(PHG - phip(5e16))
    s.num(r"The flat-band voltage is \(V_{FB} = -\varphi_{bi}\) (no oxide charge). For an n+ poly gate (\(\varphi_{n^+} = +0.55\ \mathrm{V}\)) on p-Si with \(N_A = 5\times10^{16}\ \mathrm{cm^{-3}}\), find \(V_{FB}\) in V.",
          vfb, "V",
          X(r"\(V_{FB}\) is the gate voltage that cancels the built-in potential, which leaves the bands flat and no charge anywhere:",
            r"\[\varphi_p = -0.026\ln(5\times10^{6}) = -0.401\ \mathrm{V},\quad V_{FB} = -(0.55 + 0.401) \approx " + g(vfb, 3) + r"\ \mathrm{V}\]",
            r"Negative: at \(V_{GB} = 0\) the p-surface is already somewhat depleted. (The reader's worked example quotes \(-0.952\ \mathrm{V}\); with these constants it comes out to \(-0.951\ \mathrm{V}\). That's a rounding difference.)"),
          tol=0.02)
    s.mc(r"At \(V_{GB} = 0\), an n+ poly gate on p-Si is connected through the external wire. Which way does charge settle?",
         "The silicon surface becomes depleted (negative acceptor charge) and the gate holds a matching positive charge, because the gate's Fermi level was higher",
         ["No charge anywhere; zero volts means flat bands", "Holes accumulate at the surface", "The oxide holds the charge"],
         X(r"As in a pn junction, electrons flow from the n+ gate (high Fermi level) to the p body until the Fermi levels line up. That leaves the gate positive and the surface depleted. A built-in potential \(\varphi_{bi}\) drops across the oxide plus the silicon.",
           r"To get flat bands you must apply \(V_{GB} = V_{FB} = -\varphi_{bi} < 0\)."),
         figure=FG.mos_stack('depletion'), alt="MOS cross-section with positive charge on the gate and a depletion layer of negative acceptor ions under the oxide.")
    s.round(3)
    eot = 2.0 * 3.9 / 10
    s.num(r"A high-k dielectric with \(\varepsilon_r = 10\) and thickness 2 nm replaces SiO₂. What is its 'equivalent oxide thickness' (the SiO₂ thickness with the same \(C_{ox}\)), in nm?",
          eot, "nm",
          X(r"\[C = \frac{\varepsilon_{hk}}{t_{hk}} = \frac{\varepsilon_{SiO_2}}{EOT} \Rightarrow EOT = t_{hk}\frac{3.9}{10} = " + g(eot, 3) + r"\ \mathrm{nm}\]",
            r"Gotcha: a thicker film gives MORE capacitance than a thin SiO₂ layer. The physical thickness limits gate leakage (tunnelling), while the EOT sets the electrical behaviour."))
    pmos = -PHG - Vth * math.log(1e16 / ni)
    s.num(r"For a p+ poly gate (\(\varphi_{p^+} \approx -0.55\ \mathrm{V}\)) on n-type silicon (\(N_D = 10^{16}\ \mathrm{cm^{-3}}\)), what is \(\varphi_{bi} = \varphi_{gate} - \varphi_{body}\), in V?",
          pmos, "V",
          X(r"\[\varphi_n = +0.026\ln10^{6} = 0.359\ \mathrm{V}\]",
            r"\[\varphi_{bi} = -0.55 - 0.359 \approx " + g(pmos, 3) + r"\ \mathrm{V}\]",
            r"Gotcha: the sign flips compared with n+/p (so \(V_{FB} = +" + g(-pmos, 3) + r"\ \mathrm{V}\)), and \(\varphi_{bi}\) is not just \(\varphi_{p^+}\)."))
    s.mc(r"A student says: 'Since the oxide is an insulator, the MOS capacitor's gate voltage can't affect the silicon underneath.' What's the error?",
         "The field passes through the insulator: gate charge induces an equal and opposite charge in the silicon, and that charge changes the carrier concentrations at the surface",
         ["Nothing; the gate controls only the oxide", "Current tunnels through even thick oxides, which is how the gate works", "The gate only affects the silicon if it's metal, not poly"],
         X(r"An insulator blocks current, not electric fields. By Gauss's law, gate charge \(Q_G\) is balanced by \(-Q_G\) in the silicon: holes (accumulation), ionised acceptors (depletion) or electrons (inversion).",
           r"This 'field effect' is what makes the MOSFET work."))
    s.round(4)
    s.mc(r"Preview of the MOSFET: adding n+ source and drain regions on either side of the MOS capacitor's gate turns it into an NMOS transistor. Why does that only conduct once the surface is inverted?",
         "Inversion forms an n-type electron channel at the surface that connects the n+ source to the n+ drain; otherwise they're separated by p-type silicon (back-to-back diodes)",
         ["The source and drain conduct through the oxide", "Accumulation is what forms the channel", "The p-substrate conducts between them at any gate voltage"],
         X(r"n+ / p / n+ without a channel is two pn junctions back to back, so no current flows. Inversion puts electrons under the gate, giving a continuous n path.",
           r"The gate voltage at which that happens is the threshold voltage \(V_T\) (the vt skill)."),
         preview=["mosfet-struct", "vt"])
    cg = eps_ox / 2e-7 * 1e-4 * 0.1e-4
    s.num(r"Preview of gate capacitance: a MOSFET gate is \(W = 1\ \mu\mathrm{m}\) wide and \(L = 0.1\ \mu\mathrm{m}\) long, with \(t_{ox} = 2\ \mathrm{nm}\). What is \(C_{ox}WL\), in fF?",
          cg * 1e15, "fF",
          X(r"\[C_{ox} = 17.25\ \mathrm{fF/\mu m^2},\quad WL = 0.1\ \mu\mathrm{m^2} \Rightarrow C = " + g(cg * 1e15, 3) + r"\ \mathrm{fF}\]",
            r"Tiny capacitances like this, times how many gates switch, set digital speed and power (\(CV^2f\))."),
          preview=["mos-caps"])
    vt_shift = 2 * PHG
    s.num(r"Preview of gate material: changing an n+ poly gate to a p+ poly gate on the same p-Si body changes \(\varphi_{gate}\) from \(+0.55\) to \(-0.55\ \mathrm{V}\). By how much does \(V_{FB}\) (and therefore \(V_T\)) shift, in V?",
          vt_shift, "V",
          X(r"\[\Delta V_{FB} = -\Delta\varphi_{gate} = -(-0.55 - 0.55) = +" + g(vt_shift, 3) + r"\ \mathrm{V}\]",
            r"About a band gap. Gate material is a major knob for setting threshold voltages."),
          preview=["vt"])
    return s

def mos_regions():
    s = Skill('mos-regions')
    s.round(1)
    s.mc(r"For an n+ poly / p-Si MOS capacitor, list the regions of operation as \(V_{GB}\) increases.",
         "Accumulation (V_GB < V_FB) → depletion (V_FB < V_GB < V_T) → inversion (V_GB > V_T)",
         ["Depletion → accumulation → inversion", "Inversion → depletion → accumulation", "Accumulation → inversion → depletion"],
         X(r"Below \(V_{FB}\) the negative gate attracts holes (accumulation). Above it, holes are pushed away, leaving ionised acceptors (depletion). Past \(V_T\), the surface potential reaches \(-2\varphi_p\) and electrons collect at the surface (inversion)."),
         figure=FG.mos_stack('inversion'), alt="MOS cross-section in inversion: positive gate charge, a thin layer of electrons at the silicon surface, and a depletion region of acceptor ions beneath it.")
    xd = math.sqrt(2 * eps_s * 0.4 / (q * 1e17))
    s.num(r"A p-Si MOS capacitor (\(N_A = 10^{17}\ \mathrm{cm^{-3}}\)) in depletion has a surface potential \(\varphi_s - \varphi_p = 0.4\ \mathrm{V}\) dropped across the silicon. Find the depletion depth \(X_d = \sqrt{2\varepsilon_s(0.4)/(qN_A)}\) in nm.",
          xd * 1e7, "nm",
          X(r"\[X_d = \sqrt{\frac{2(1.036\times10^{-12})(0.4)}{(1.602\times10^{-19})(10^{17})}} = " + sci(xd, 3) + r"\ \mathrm{cm} \approx " + g(xd * 1e7, 3) + r"\ \mathrm{nm}\]",
            r"This is the one-sided junction result: the silicon drop alone sets \(X_d\)."))
    s.mc(r"In the depletion region of an n+/p MOS capacitor, what charge sits in the silicon to balance the positive gate charge?",
         "Negative ionised acceptors (Nₐ⁻) in a depletion layer of depth X_d, with almost no mobile carriers",
         ["Holes piled up at the surface", "Electrons at the surface", "Positive donor ions"],
         X(r"Holes are pushed away from the surface, uncovering the fixed acceptors: \(Q_B = -qN_AX_d\). Electrons only appear in large numbers once the surface inverts."),
         figure=FG.mos_stack('depletion'), alt="MOS cross-section in depletion: positive gate charge and a layer of negative acceptor ions of depth Xd.")
    s.round(2)
    NA = 1e17
    pp = phip(NA)
    xdm = math.sqrt(2 * eps_s * (-2 * pp) / (q * NA))
    s.num(r"At the onset of inversion the silicon drop is \(-2\varphi_p\). For \(N_A = 10^{17}\ \mathrm{cm^{-3}}\), find the maximum depletion depth \(X_{d,max}\) in nm.",
          xdm * 1e7, "nm",
          X(r"\[\varphi_p = -0.026\ln10^{7} = " + g(pp, 4) + r"\ \mathrm{V},\quad -2\varphi_p = " + g(-2 * pp, 4) + r"\ \mathrm{V}\]",
            r"\[X_{d,max} = \sqrt{\frac{2\varepsilon_s(-2\varphi_p)}{qN_A}} \approx " + g(xdm * 1e7, 3) + r"\ \mathrm{nm}\]",
            r"Beyond threshold, the extra gate charge goes into electrons and \(X_d\) stays roughly at this value."))
    QB = q * 1e17 * xdm
    s.num(r"With \(X_{d,max}\) from the previous step (\(N_A = 10^{17}\ \mathrm{cm^{-3}}\)), what is the magnitude of the depletion charge \(|Q_B| = qN_AX_{d,max}\), in nC/cm²?",
          QB * 1e9, "nC/cm²",
          X(r"\[|Q_B| = (1.602\times10^{-19})(10^{17})(" + sci(xdm, 3) + r") \approx " + g(QB * 1e9, 3) + r"\ \mathrm{nC/cm^2}\]",
            r"Equivalently, \(\sqrt{2q\varepsilon_sN_A(-2\varphi_p)}\)."))
    vox = QB / (eps_ox / 5e-7)
    s.num(r"That depletion charge (\(" + g(QB * 1e9, 3) + r"\ \mathrm{nC/cm^2}\)) is mirrored on the gate. With \(t_{ox} = 5\ \mathrm{nm}\), what voltage drops across the oxide, \(V_{ox} = |Q_B|/C_{ox}\)?",
          vox, "V",
          X(r"\[C_{ox} = 6.9\times10^{-7}\ \mathrm{F/cm^2},\quad V_{ox} = \frac{" + sci(QB, 3) + r"}{6.9\times10^{-7}} \approx " + g(vox, 3) + r"\ \mathrm{V}\]",
            r"So at threshold, \(V_{GB} = V_{FB} + (-2\varphi_p) + V_{ox}\). The next skill puts these together."))
    s.round(3)
    s.mc(r"Increasing \(V_{GB}\) well above \(V_T\) adds more gate charge. Where does the matching silicon charge go?",
         "Almost entirely into inversion electrons at the surface; the depletion depth stays pinned near X_d,max",
         ["Into a deeper depletion layer, growing as √V_GB", "Into accumulated holes", "Into the oxide"],
         X(r"Electron density rises exponentially with surface potential, so a tiny increase in \(\varphi_s\) supplies lots of charge. The surface potential and \(X_d\) hardly change: \(Q_n \approx -C_{ox}(V_{GB} - V_T)\).",
           r"Gotcha: the depletion formula stops applying past threshold. (Reader Fig. 7.9 labels this \(V_{GS} - V_T\); for a capacitor it should be \(V_{GB}\).)"))
    s.mc(r"The surface 'inverts' when the surface potential reaches \(\varphi_s = -\varphi_p\) (so the band bending is \(-2\varphi_p\)). Why that value rather than \(\varphi_s = 0\)?",
         "At φs = 0 the surface is merely intrinsic (n = p = nᵢ); at φs = −φp the surface electron density equals the bulk hole density Nₐ, i.e. 'as n-type as the bulk is p-type'",
         ["At φs = 0 the bands are flat", "−2φp is where the oxide breaks down", "It's arbitrary; any value works"],
         X(r"With \(n = n_ie^{\varphi_s/V_{th}}\), \(\varphi_s = -\varphi_p\) gives \(n = n_i\cdot N_A/n_i = N_A\). That's the reader's threshold condition. At midgap (\(\varphi_s = 0\)) the electron density is still tiny."))
    s.mc(r"In accumulation (\(V_{GB} < V_{FB}\)), where is the silicon charge and how deep does it go?",
         "A thin sheet of holes right at the surface; there's essentially no depletion layer",
         ["A depletion layer of acceptors, X_d deep", "Electrons at the surface", "Holes spread uniformly through the substrate"],
         X(r"The negative gate attracts majority holes, which pile up within a few nm of the surface (like a metal plate). Gotcha: so the capacitance is just \(C_{ox}\), and there's no \(X_d\) to compute."),
         figure=FG.mos_stack('accumulation'), alt="MOS cross-section in accumulation: negative gate charge and a thin layer of holes at the silicon surface.")
    s.round(4)
    s.mc(r"Preview of the MOSFET in triode: in an NMOS transistor with \(V_{GS} > V_T\) and a small \(V_{DS}\), what carries the drain current?",
         "The inversion-layer electrons, drifting from source to drain, with sheet charge ≈ C_ox(V_GS − V_T)",
         ["Holes in the substrate", "Depletion charge", "Gate current through the oxide"],
         X(r"The inversion layer is a resistor whose sheet charge the gate controls. So \(I_D \approx \mu_nC_{ox}\frac{W}{L}(V_{GS}-V_T)V_{DS}\) for small \(V_{DS}\)."),
         preview=["nmos-regions", "triode"])
    Qn = (eps_ox / 2e-7) * 0.5 / q
    s.num(r"Preview of channel charge: with \(t_{ox} = 2\ \mathrm{nm}\) and \(V_{GB} - V_T = 0.5\ \mathrm{V}\), what is the inversion electron density \(|Q_n|/q = C_{ox}(V_{GB}-V_T)/q\), in electrons/cm²? Scientific notation is fine.",
          Qn, "cm⁻²",
          X(r"\[\frac{|Q_n|}{q} = \frac{(1.725\times10^{-6})(0.5)}{1.602\times10^{-19}} \approx " + sci(Qn, 3) + r"\ \mathrm{cm^{-2}}\]"),
          preview=["nmos-regions"])
    s.mc(r"Preview of drain bias: in an NMOS transistor, raising the drain voltage raises the channel potential near the drain. What does that do to the inversion layer there?",
         "It reduces it, because the local gate-to-channel voltage V_GS − V(x) shrinks; when it falls to V_T at the drain the channel 'pinches off'",
         ["It thickens the channel near the drain", "It has no effect", "It accumulates holes"],
         X(r"The local inversion charge is \(C_{ox}(V_{GS} - V(x) - V_T)\). At \(V_{DS} = V_{GS} - V_T\) this reaches zero at the drain: saturation."),
         preview=["saturation", "nmos-regions"])
    return s

def vt():
    s = Skill('vt')
    NA = 1e17; pp = phip(NA); tox = 5e-7; cox = eps_ox / tox
    vfb = -(PHG - pp)
    QB = math.sqrt(2 * q * eps_s * NA * (-2 * pp))
    VT = vfb - 2 * pp + QB / cox
    s.round(1)
    s.mc(r"Which expression is the threshold voltage of an n+ poly / p-Si MOS capacitor?",
         r"\(V_T = V_{FB} - 2\varphi_p + \frac{1}{C_{ox}}\sqrt{2q\varepsilon_sN_A(-2\varphi_p)}\)",
         [r"\(V_T = V_{FB} + 2\varphi_p\)", r"\(V_T = -2\varphi_p + C_{ox}\sqrt{2q\varepsilon_sN_A}\)", r"\(V_T = V_{FB} - \frac{1}{C_{ox}}\sqrt{2q\varepsilon_sN_A(-2\varphi_p)}\)"],
         X(r"Three terms: flatten the bands (\(V_{FB}\)), bend the silicon by \(-2\varphi_p\), and drop \(|Q_B|/C_{ox}\) across the oxide to support the depletion charge.",
           r"Note \(\varphi_p < 0\), so \(-2\varphi_p > 0\)."))
    s.num(r"Find \(V_T\) for an n+ poly gate (\(\varphi_{n^+} = +0.55\ \mathrm{V}\)) on p-Si with \(N_A = 10^{17}\ \mathrm{cm^{-3}}\) and \(t_{ox} = 5\ \mathrm{nm}\).",
          VT, "V",
          X(r"\[V_{FB} = " + g(vfb, 4) + r",\quad -2\varphi_p = " + g(-2 * pp, 4) + r",\quad \frac{|Q_B|}{C_{ox}} = \frac{" + sci(QB, 3) + r"}{6.9\times10^{-7}} = " + g(QB / cox, 4) + r"\ \mathrm{V}\]",
            r"\[V_T \approx " + g(vfb, 4) + r" + " + g(-2 * pp, 4) + r" + " + g(QB / cox, 4) + r" = " + g(VT, 3) + r"\ \mathrm{V}\]"),
          tol=0.03)
    s.num(r"For \(N_A = 10^{17}\ \mathrm{cm^{-3}}\), what is the band bending needed for inversion, \(-2\varphi_p\), in V? (\(V_{th} = 26\ \mathrm{mV}\))",
          -2 * pp, "V",
          X(r"\[-2\varphi_p = 2(0.026)\ln\frac{10^{17}}{10^{10}} = 0.052\times16.12 \approx " + g(-2 * pp, 3) + r"\ \mathrm{V}\]"))
    s.round(2)
    NA2 = 2e16; pp2 = phip(NA2); cox2 = eps_ox / 10e-7
    vfb2 = -(PHG - pp2)
    QB2 = math.sqrt(2 * q * eps_s * NA2 * (-2 * pp2))
    VT2 = vfb2 - 2 * pp2 + QB2 / cox2
    s.num(r"Repeat with \(N_A = 2\times10^{16}\ \mathrm{cm^{-3}}\) and \(t_{ox} = 10\ \mathrm{nm}\) (n+ poly gate, \(\varphi_{n^+} = +0.55\ \mathrm{V}\)).",
          VT2, "V",
          X(r"\[V_{FB} = " + g(vfb2, 4) + r",\ -2\varphi_p = " + g(-2 * pp2, 4) + r",\ |Q_B| = " + sci(QB2, 3) + r"\ \mathrm{C/cm^2},\ C_{ox} = 3.45\times10^{-7}\]",
            r"\[V_T \approx " + g(VT2, 3) + r"\ \mathrm{V}\]",
            r"Lighter doping gives a smaller \(V_T\)."),
          tol=0.03)
    s.num(r"In the \(N_A = 10^{17}\), \(t_{ox} = 5\ \mathrm{nm}\) device, how much of \(V_T\) is the oxide term \(|Q_B|/C_{ox}\)? Answer in V.",
          QB / cox, "V",
          X(r"\[|Q_B| = \sqrt{2q\varepsilon_sN_A(-2\varphi_p)} = " + sci(QB, 3) + r"\ \mathrm{C/cm^2},\quad \frac{|Q_B|}{C_{ox}} \approx " + g(QB / cox, 3) + r"\ \mathrm{V}\]"))
    s.mc(r"How does \(V_T\) change if \(t_{ox}\) is halved, with everything else the same (n+/p, \(N_A = 10^{17}\))?",
         "It decreases: the |Q_B|/C_ox term halves, while V_FB and −2φp are unchanged",
         ["It doubles", "It's unchanged, because V_T depends only on doping", "It increases, because the field is stronger"],
         X(r"Only the oxide term depends on \(t_{ox}\): \(\frac{|Q_B|}{C_{ox}} \propto t_{ox}\). For our device it goes from " + g(QB / cox, 3) + r" to " + g(QB / cox / 2, 3) + r" V."))
    s.round(3)
    s.mc(r"Doubling \(N_A\) changes all three \(V_T\) terms. Which changes the most (for \(N_A \sim 10^{17}\), \(t_{ox} = 5\ \mathrm{nm}\))?",
         r"The \(|Q_B|/C_{ox}\) term, which grows roughly as \(\sqrt{N_A}\); \(V_{FB}\) and \(-2\varphi_p\) change only by about \(V_{th}\ln2\)",
         [r"\(-2\varphi_p\), which doubles", r"\(V_{FB}\), which doubles", "None change"],
         X(r"Logarithmic terms: \(\Delta(-2\varphi_p) = 2V_{th}\ln2 \approx 36\ \mathrm{mV}\) and \(\Delta V_{FB} = -18\ \mathrm{mV}\). Square-root term: \(\times\sqrt2\cdot\sqrt{1+\ldots}\), about \(+" + g(QB / cox * (math.sqrt(2 * (2 * Vth * math.log(2e17 / ni)) / (-2 * pp)) - 1), 2) + r"\ \mathrm{V}\) here.",
           r"Gotcha: doubling the doping does NOT double \(V_T\)."))
    s.mc(r"For p-type silicon, \(\varphi_p = -0.419\ \mathrm{V}\) (\(N_A = 10^{17}\)). A student plugs this into \(V_T = V_{FB} + 2\varphi_p + |Q_B|/C_{ox}\). What goes wrong?",
         r"The sign is wrong: the band bending must be \(-2\varphi_p = +0.838\ \mathrm{V}\), so their \(V_T\) comes out about 1.68 V too low",
         ["Nothing; the two forms are equivalent", "V_T comes out 0.42 V too high", "Only V_FB is affected"],
         X(r"Bending the surface from \(\varphi_p\) to \(-\varphi_p\) takes \(-2\varphi_p > 0\). Writing \(+2\varphi_p\) subtracts 0.838 V instead of adding it, a 1.676 V error.",
           r"Gotcha: sign slips with \(\varphi_p\) are the most common \(V_T\) error. For n+/p, every term except \(V_{FB}\) should be positive."))
    s.num(r"A body bias \(V_{SB}\) adds to the needed silicon drop, changing \(|Q_B|\) to \(\sqrt{2q\varepsilon_sN_A(-2\varphi_p + V_{SB})}\). For the \(N_A = 10^{17}\), \(t_{ox} = 5\ \mathrm{nm}\) device with \(V_{SB} = 1\ \mathrm{V}\), by how much does \(V_T\) rise, in V?",
          (math.sqrt(2 * q * eps_s * NA * (-2 * pp + 1)) - QB) / cox, "V",
          X(r"\[\Delta V_T = \frac{\sqrt{2q\varepsilon_sN_A}}{C_{ox}}\left(\sqrt{-2\varphi_p + V_{SB}} - \sqrt{-2\varphi_p}\right) = \gamma(\sqrt{1.838} - \sqrt{0.838})\]",
            r"\[\gamma = " + g(math.sqrt(2 * q * eps_s * NA) / cox, 3) + r"\ \sqrt{\mathrm{V}} \Rightarrow \Delta V_T \approx " + g((math.sqrt(2 * q * eps_s * NA * (-2 * pp + 1)) - QB) / cox, 3) + r"\ \mathrm{V}\]",
            r"Gotcha: the change goes as a square root, not linearly with \(V_{SB}\)."),
          tol=0.03)
    s.round(4)
    Qn = cox * (1.5 - VT) / q
    s.num(r"Preview of drive: the \(N_A = 10^{17}\), \(t_{ox} = 5\ \mathrm{nm}\) device (\(V_T \approx " + g(VT, 3) + r"\ \mathrm{V}\)) is biased at \(V_{GB} = 1.5\ \mathrm{V}\). What is the inversion electron density \(C_{ox}(V_{GB}-V_T)/q\), in cm⁻²? Scientific notation is fine.",
          Qn, "cm⁻²",
          X(r"\[n_s = \frac{(6.9\times10^{-7})(1.5 - " + g(VT, 3) + r")}{1.602\times10^{-19}} \approx " + sci(Qn, 3) + r"\ \mathrm{cm^{-2}}\]",
            r"This sheet charge carries the MOSFET current."),
          tol=0.03, preview=["nmos-regions", "triode"])
    s.mc(r"Preview of body bias: the reverse source-to-body bias \(V_{SB}\) raises \(V_T\) as above. Where does this matter in circuits?",
         "In stacked transistors (e.g. the upper NMOS in a NAND gate or a source follower), whose sources sit above ground, so their V_T is higher",
         ["Only in PMOS transistors", "Nowhere; the body is always tied to the source", "Only in the oxide breakdown rating"],
         X(r"Any NMOS whose source is not at the body (ground) potential sees \(V_{SB} > 0\). This 'body effect' reduces the drive and the gain of a source follower."),
         preview=["body-effect"])
    s.mc(r"Preview of PMOS: for a p+ poly gate on n-type silicon, what's the sign of \(V_T\), and what gate voltage turns the device on?",
         "V_T is negative; the gate must go below V_T (more negative) to invert the n-surface into a hole channel",
         ["Positive, like NMOS", "Zero always", "Negative, but a positive gate turns it on"],
         X(r"Everything mirrors: \(\varphi_n > 0\), so the band bending is \(-2\varphi_n < 0\), and the depletion charge is positive donors, so the oxide term is negative. Holes form the channel."),
         preview=["pmos"])
    return s

def mos_fields():
    s = Skill('mos-fields')
    s.round(1)
    s.num(r"A 1 V drop across a \(t_{ox} = 10\ \mathrm{nm}\) gate oxide (uniform field) gives what oxide field, in MV/cm?",
          1.0, "MV/cm",
          X(r"\[E_{ox} = \frac{V_{ox}}{t_{ox}} = \frac{1}{10^{-6}\ \mathrm{cm}} = 10^{6}\ \mathrm{V/cm} = 1\ \mathrm{MV/cm}\]",
            r"SiO₂ breaks down around 10 MV/cm, so real devices keep \(E_{ox}\) a few times below that."),
          figure=FG.mos_profiles(), alt="Electric field versus depth in a MOS capacitor: a constant field in the oxide, a step down at the oxide–silicon interface, then a linear decrease to zero at the depletion edge.")
    s.mc(r"At the oxide–silicon interface (with no interface charge), how does the field jump?",
         r"\(\varepsilon_{ox}E_{ox} = \varepsilon_sE_s\), so \(E_s = E_{ox}\cdot3.9/11.7 = E_{ox}/3\)",
         [r"\(E_s = E_{ox}\) (the field is continuous)", r"\(E_s = 3E_{ox}\)", r"\(E_s = 0\) at the interface"],
         X(r"The normal component of \(D = \varepsilon E\) is continuous where there's no sheet charge. Silicon has three times the permittivity, so it has a third of the field."))
    xd = math.sqrt(2 * eps_s * 0.5 / (q * 1e17))
    Es = q * 1e17 * xd / eps_s
    s.num(r"In depletion (\(N_A = 10^{17}\ \mathrm{cm^{-3}}\), silicon drop 0.5 V), find the surface field \(E_s = qN_AX_d/\varepsilon_s\) in kV/cm.",
          Es / 1e3, "kV/cm",
          X(r"\[X_d = \sqrt{\frac{2\varepsilon_s(0.5)}{qN_A}} = " + g(xd * 1e7, 3) + r"\ \mathrm{nm},\quad E_s = \frac{qN_AX_d}{\varepsilon_s} \approx " + g(Es / 1e3, 3) + r"\ \mathrm{kV/cm}\]",
            r"The field decreases linearly to zero at \(X_d\) (uniform charge)."))
    s.round(2)
    Eox = Es * eps_s / eps_ox
    s.num(r"For that same depletion state (\(E_s = " + g(Es / 1e3, 3) + r"\ \mathrm{kV/cm}\)), what is the oxide field, in kV/cm?",
          Eox / 1e3, "kV/cm",
          X(r"\[E_{ox} = \frac{\varepsilon_s}{\varepsilon_{ox}}E_s = 3E_s \approx " + g(Eox / 1e3, 3) + r"\ \mathrm{kV/cm}\]"))
    s.num(r"For that same state, how much voltage drops across a 5 nm oxide? (\(V_{ox} = E_{ox}t_{ox}\))",
          Eox * 5e-7, "V",
          X(r"\[V_{ox} = " + sci(Eox, 3) + r"\times5\times10^{-7} \approx " + g(Eox * 5e-7, 3) + r"\ \mathrm{V}\]",
            r"So \(V_{GB} = V_{FB} + 0.5 + " + g(Eox * 5e-7, 3) + r"\ \mathrm{V}\)."))
    s.mc(r"What's the shape of the potential \(\varphi(x)\) in the silicon depletion region?",
         "A parabola: the field falls linearly with depth, so the potential rises quadratically to the surface",
         ["Linear, like in the oxide", "Exponential", "Constant"],
         X(r"Uniform charge gives a linear field, which integrates to a quadratic potential. The total drop is the triangle area \(E_sX_d/2\). In the charge-free oxide the field is constant, so the potential there is linear."),
         figure=FG.mos_profiles(), alt="MOS field profile: constant in the oxide, stepping down at the interface, then decreasing linearly to zero at Xd.")
    s.round(3)
    psi = Es * xd / 2
    s.num(r"Gotcha check: with \(E_s = " + g(Es / 1e3, 3) + r"\ \mathrm{kV/cm}\) and \(X_d = " + g(xd * 1e7, 3) + r"\ \mathrm{nm}\), the silicon drop is NOT \(E_sX_d\). What is it, in V?",
          psi, "V",
          X(r"\[\Delta\varphi = \frac{1}{2}E_sX_d = \frac{1}{2}(" + sci(Es, 3) + r")(" + sci(xd, 3) + r") \approx " + g(psi, 3) + r"\ \mathrm{V}\]",
            r"It's the triangle area under a linearly falling field, which recovers the 0.5 V we started with."))
    s.mc(r"A high-k gate dielectric (\(\varepsilon_r = 20\)) replaces SiO₂ at the same physical thickness and the same silicon surface field. What happens to the field inside the dielectric?",
         "It's 20/3.9 ≈ 5 times SMALLER than in SiO₂, since ε_hk·E_hk = ε_s·E_s",
         ["It's 5 times larger", "It's unchanged", "It equals E_s"],
         X(r"Continuity of \(D\): \(E_{hk} = \varepsilon_sE_s/\varepsilon_{hk}\). Gotcha: a higher permittivity lowers the field (and the voltage drop) for the same charge."))
    vfbA = -(PHG - phip(5e16)); EoxA = (-1.5 - vfbA) / 10e-7
    s.num(r"An n+ poly / p-Si capacitor (\(N_A = 5\times10^{16}\ \mathrm{cm^{-3}}\), \(V_{FB} = " + g(vfbA, 3) + r"\ \mathrm{V}\), \(t_{ox} = 10\ \mathrm{nm}\)) is biased in accumulation at \(V_{GB} = -1.5\ \mathrm{V}\). Holes at the surface act like a metal plate, so essentially all of \(V_{GB} - V_{FB}\) drops across the oxide. Find \(E_{ox}\) in kV/cm, with sign (\(+x\) points from the gate into the silicon).",
          EoxA / 1e3, "kV/cm",
          X(r"\[E_{ox} = \frac{V_{GB} - V_{FB}}{t_{ox}} = \frac{-1.5 - (" + g(vfbA, 3) + r")}{10^{-6}\ \mathrm{cm}} \approx " + g(EoxA / 1e3, 3) + r"\ \mathrm{kV/cm}\]",
            r"Gotcha: the sign is negative. The field points from the silicon back toward the more negative gate. Using \(V_{GB}\) alone (\(-1.5\ \mathrm{MV/cm}\)) ignores the built-in part \(V_{FB}\). In depletion and inversion, \(E_{ox} > 0\)."),
          figure=FG.mos_stack('accumulation'), alt="MOS cross-section in accumulation: negative gate charge and a thin layer of holes at the silicon surface.")
    s.round(4)
    r = math.sqrt((2 * Vth * math.log(1e17 / ni)) / (2 * Vth * math.log(1e18 / ni)) * (1e18 / 1e17)) 
    s.num(r"Preview of scaling: \(X_{d,max} = \sqrt{2\varepsilon_s(-2\varphi_p)/(qN_A)}\). By what factor does it shrink when \(N_A\) goes from \(10^{17}\) to \(10^{18}\ \mathrm{cm^{-3}}\)? Give \(X_{d,max}(10^{17})/X_{d,max}(10^{18})\).",
          1 / math.sqrt((math.log(1e18 / ni) / 1e18) / (math.log(1e17 / ni) / 1e17)), "(ratio)",
          X(r"\[\frac{X(10^{17})}{X(10^{18})} = \sqrt{10\cdot\frac{\ln10^{7}}{\ln10^{8}}} = \sqrt{10\times0.875} \approx " + g(1 / math.sqrt((math.log(1e18 / ni) / 1e18) / (math.log(1e17 / ni) / 1e17)), 3) + r"\]",
            r"Heavier doping keeps the depletion shallow. That is part of how short-channel MOSFETs suppress drain influence."),
          preview=["nmos-regions"])
    d = eps_ox / 2e-7 / q
    s.num(r"Preview of gate control: with \(t_{ox} = 2\ \mathrm{nm}\), each extra volt of \(V_{GB}-V_T\) adds how many inversion electrons per cm²? Scientific notation is fine.",
          d, "cm⁻²",
          X(r"\[\frac{C_{ox}}{q} = \frac{1.725\times10^{-6}}{1.602\times10^{-19}} \approx " + sci(d, 3) + r"\ \mathrm{cm^{-2}V^{-1}}\]"),
          preview=["triode", "saturation"])
    s.mc(r"Preview of MOSFET reliability: why must \(t_{ox}\) scale down with the supply voltage rather than faster?",
         "Thinner oxide raises E_ox = V/t_ox toward breakdown and increases tunnelling leakage, so V_DD and t_ox must shrink together",
         ["Oxide thickness doesn't affect the field", "Thinner oxide reduces C_ox", "Only doping limits the field"],
         X(r"At 1 V across 2 nm, \(E_{ox} = 5\ \mathrm{MV/cm}\), already half of breakdown. High-k dielectrics relieve the leakage."),
         preview=["mos-caps"])
    return s

def mos_cv():
    s = Skill('mos-cv')
    cox = eps_ox / 2e-7 / 10  # 20 nm -> 172.5 nF
    cox = eps_ox / 20e-7
    s.round(1)
    s.num(r"A MOS capacitor has \(t_{ox} = 20\ \mathrm{nm}\). What is its capacitance per area in accumulation, in nF/cm²?",
          cox * 1e9, "nF/cm²",
          X(r"In accumulation the holes act like a metal plate at the surface, so \(C = C_{ox} = \frac{3.45\times10^{-13}}{2\times10^{-6}} = " + g(cox * 1e9, 4) + r"\ \mathrm{nF/cm^2}\)."),
          figure=FG.cv_curve(), alt="Low-frequency MOS C–V curve: flat at Cox in accumulation, dipping to a minimum in depletion near threshold, and rising back to Cox in inversion.")
    s.mc(r"In depletion, the MOS capacitance is modelled as:",
         r"\(C_{ox}\) in series with the depletion capacitance \(C_{dep} = \varepsilon_s/X_d\)",
         [r"\(C_{ox}\) in parallel with \(C_{dep}\)", r"Just \(C_{dep}\)", r"\(C_{ox}+C_{dep}\) in series with a resistor"],
         X(r"A small change in gate charge is mirrored at the depletion edge, a depth \(X_d\) below the oxide, so the two dielectrics are in series: \(\frac{1}{C} = \frac{1}{C_{ox}} + \frac{X_d}{\varepsilon_s}\)."),
         figure=FG.cv_curve(), alt="MOS C–V curve with the depletion dip marked.")
    cs = 1 / (1 / cox + 100e-7 / eps_s)
    s.num(r"With \(t_{ox} = 20\ \mathrm{nm}\) and \(X_d = 100\ \mathrm{nm}\), what is the series capacitance per area, in nF/cm²?",
          cs * 1e9, "nF/cm²",
          X(r"\[C_{dep} = \frac{1.036\times10^{-12}}{10^{-5}} = 103.6\ \mathrm{nF/cm^2},\quad C = \frac{172.5\times103.6}{172.5+103.6} \approx " + g(cs * 1e9, 3) + r"\ \mathrm{nF/cm^2}\]"))
    s.round(2)
    xdm = math.sqrt(2 * eps_s * (-2 * phip(1e16)) / (q * 1e16))
    cmin = 1 / (1 / cox + xdm / eps_s)
    s.num(r"For \(N_A = 10^{16}\ \mathrm{cm^{-3}}\) and \(t_{ox} = 20\ \mathrm{nm}\), estimate the high-frequency minimum \(C_{min}/C_{ox}\), using \(X_{d,max}\).",
          cmin / cox, "(ratio)",
          X(r"\[X_{d,max} = \sqrt{\frac{2\varepsilon_s(" + g(-2 * phip(1e16), 3) + r")}{qN_A}} \approx " + g(xdm * 1e7, 3) + r"\ \mathrm{nm}\]",
            r"\[\frac{C_{min}}{C_{ox}} = \frac{1}{1 + C_{ox}X_{d,max}/\varepsilon_s} \approx " + g(cmin / cox, 3) + r"\]"))
    tox = eps_ox / 3.45e-7
    s.num(r"An accumulation measurement gives \(C_{ox} = 3.45\ \mathrm{fF/\mu m^2}\). What is \(t_{ox}\), in nm?",
          tox * 1e7, "nm",
          X(r"\[3.45\ \mathrm{fF/\mu m^2} = 3.45\times10^{-7}\ \mathrm{F/cm^2},\quad t_{ox} = \frac{3.45\times10^{-13}}{3.45\times10^{-7}} = 10^{-6}\ \mathrm{cm} = " + g(tox * 1e7, 3) + r"\ \mathrm{nm}\]",
            r"That is the standard way to measure oxide thickness electrically."))
    s.mc(r"At LOW frequency, why does the C–V curve rise back to \(C_{ox}\) in inversion?",
         "Inversion electrons can form and vanish fast enough to follow the signal, so the charge changes right at the surface, just like in accumulation",
         ["The depletion layer disappears", "The oxide thickness changes", "Holes accumulate again"],
         X(r"At high frequency, minority electrons (made by slow thermal generation) can't keep up. Then only \(X_{d,max}\) responds and \(C\) stays at \(C_{min}\)."),
         figure=FG.cv_curve(cmin_label=True), alt="C–V curve rising back to Cox at low frequency in inversion, with a dashed high-frequency curve staying at Cmin.")
    s.round(3)
    s.mc(r"Within the depletion approximation, how does the capacitance of an n+/p MOS capacitor change as \(V_{GB}\) rises from \(V_{FB}\) to \(V_T\)?",
         r"It falls steadily from \(C_{ox}\) toward \(C_{min}\): \(X_d\) grows (as the square root of the silicon drop), so the series \(C_{dep} = \varepsilon_s/X_d\) shrinks",
         [r"It stays at \(C_{ox}\) until \(V_T\), then drops suddenly", r"It rises, because more gate charge means more capacitance", r"It falls linearly with \(V_{GB}\) and reaches zero at \(V_T\)"],
         X(r"\[\frac{1}{C} = \frac{1}{C_{ox}} + \frac{X_d}{\varepsilon_s},\quad X_d = \sqrt{\frac{2\varepsilon_s\psi_s}{qN_A}}\]",
           r"At \(V_{FB}\), \(X_d = 0\) and \(C = C_{ox}\). As the band bending \(\psi_s\) grows to \(-2\varphi_p\), \(X_d\) reaches \(X_{d,max}\) and C reaches \(C_{min}\). Gotcha: capacitance is \(dQ/dV\), not \(Q/V\), and it never goes to zero, because \(C_{ox}\) is still in series with a finite \(C_{dep}\)."),
         figure=FG.cv_curve(), alt="MOS C–V curve: flat at Cox in accumulation, decreasing through depletion from VFB to VT.")
    Q = cox * 2.0
    s.num(r"In accumulation, the \(t_{ox} = 20\ \mathrm{nm}\) capacitor is driven 2 V below \(V_{FB}\). What is the magnitude of the accumulated hole charge, in nC/cm²?",
          Q * 1e9, "nC/cm²",
          X(r"\[|Q| = C_{ox}|V_{GB}-V_{FB}| = 172.5\times2 = " + g(Q * 1e9, 4) + r"\ \mathrm{nC/cm^2}\]",
            r"Gotcha: use \(V_{GB}-V_{FB}\), not \(V_{GB}\). The charge is zero at flat band, not at 0 V."))
    s.mc(r"Gotcha: a C–V curve measured on a device with a THICKER oxide but the same doping would show:",
         "A lower C_ox plateau and a shallower relative dip (C_min/C_ox closer to 1)",
         ["A higher plateau", "The same plateau, just shifted", "A deeper relative dip"],
         X(r"\(C_{min}/C_{ox} = 1/(1 + C_{ox}X_d/\varepsilon_s)\). A smaller \(C_{ox}\) makes the oxide dominate the series combination, so the depletion layer matters less."))
    s.round(4)
    Cg = eps_ox / 2e-7 * 4e-8
    s.num(r"Preview of MOSFET gate capacitance: a gate \(W = 2\ \mu\mathrm{m}\) by \(L = 2\ \mu\mathrm{m}\) with \(t_{ox} = 2\ \mathrm{nm}\) is in strong inversion. What is \(C_{ox}WL\), in fF?",
          Cg * 1e15, "fF",
          X(r"\[C_{ox} = 17.25\ \mathrm{fF/\mu m^2},\quad C = 17.25\times4 = " + g(Cg * 1e15, 3) + r"\ \mathrm{fF}\]",
            r"In saturation only about \(\frac{2}{3}\) of it appears from gate to source; that's covered in the device-capacitance skill."),
          preview=["mos-caps"])
    ne = Cg * 0.5 / q
    s.num(r"Preview of channel charge: with that 69 fF gate at \(V_{GB}-V_T = 0.5\ \mathrm{V}\), how many electrons are in the channel?",
          ne, "electrons",
          X(r"\[N = \frac{C(V_{GB}-V_T)}{q} = \frac{" + sci(Cg, 3) + r"\times0.5}{1.602\times10^{-19}} \approx " + g(ne, 3) + r"\]"),
          tol=0.02, preview=["triode"])
    s.mc(r"Preview of the operating regions: in an NMOS transistor biased at \(V_{GS} < V_T\), what charge does the gate capacitance mostly 'see'?",
         "Depletion charge in the body (C_ox in series with C_dep), with almost no channel; the transistor is in cutoff",
         ["The full inversion channel", "Accumulation holes", "Charge in the source only"],
         X(r"Below threshold there's no inversion layer, so the gate couples to the body through the depletion layer. Above threshold the channel shields the body, and the gate sees about \(C_{ox}WL\)."),
         preview=["nmos-regions", "mos-caps"])
    return s
