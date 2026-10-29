"""batch2a: drift, diffusion, total-current, carrier-pot"""
from batch2a_lib import *
import batch2a_fig as FG
import math

def X(*lines): return "\n".join(lines)

def lin_profile(y0lab, y1lab, ylab, title="", x1lab="W"):
    return FG.plot([dict(pts=[(0, 1.0), (1, 0.05)])], (0, 1.2), (0, 1.25), "x", ylab, w=340, h=200,
                   marks=[(0, 1.0, y0lab, 8, -4), (1, 0.05, y1lab, 6, -10)], xticks=[(0, "0"), (1, x1lab)], label=title or f"{ylab} falling linearly with x")

def drift():
    s = Skill('drift')
    s.round(1)
    s.num(r"Holes in silicon have mobility \(\mu_p = 400\ \mathrm{cm^2/(V\cdot s)}\). What is their drift velocity in a field of \(E = 1\ \mathrm{kV/cm}\)?",
          400 * 1e3, "cm/s",
          X(r"\[v_{dr} = \mu_p E = 400 \times 1000 = 4\times10^{5}\ \mathrm{cm/s}\]",
            r"Holes drift ALONG the field (positive charge). Electrons drift against it, and at the same field they are faster: with \(\mu_n \approx 1000\) they would reach \(10^6\) cm/s."))
    s.mc(r"A field \(E\) points to the right in a silicon bar containing both electrons and holes (see figure). Which way do the electron drift current and the hole drift current point?",
         "Both point to the right, along E, so they add",
         ["Electron current to the left, hole current to the right, so they partly cancel", "Both point to the left", "Electron current to the right, hole current to the left"],
         X(r"Holes move with \(E\): current to the right. Electrons move against \(E\) (to the left), but they carry negative charge, so their current is also to the right.",
           r"\[J_{drift} = q\,n\,\mu_n E + q\,p\,\mu_p E = q(n\mu_n + p\mu_p)E\]",
           r"Both terms have the sign of \(E\), so conductivities add. The carriers MOVE in opposite directions, but the CURRENTS don't."),
         figure=FG.bar(vlabel="", elabel="E", carriers="e"), alt="A silicon bar with an applied voltage, positive on the left. The field E points right and a dashed arrow shows electrons drifting left.")
    J = q * 1e16 * 1000 * 10
    s.num(r"An n-type region has \(n = 10^{16}\ \mathrm{cm^{-3}}\) and \(\mu_n = 1000\ \mathrm{cm^2/(V\cdot s)}\). A field \(E = 10\ \mathrm{V/cm}\) is applied. What is the electron drift current density?",
          J, "A/cm²",
          X(r"\[J_n = q\,n\,\mu_n E = (1.602\times10^{-19})(10^{16})(1000)(10) \approx " + g(J, 4) + r"\ \mathrm{A/cm^2}\]",
            r"The minority holes (\(10^4\ \mathrm{cm^{-3}}\)) contribute nothing measurable."))
    s.round(2)
    rho = 1 / (q * 5e15 * 400)
    s.num(r"A p-type silicon wafer is doped with \(N_A = 5\times10^{15}\ \mathrm{cm^{-3}}\), and \(\mu_p = 400\ \mathrm{cm^2/(V\cdot s)}\). What is its resistivity?",
          rho, "Ω·cm",
          X(r"\(p_0 \approx N_A\), and the minority electrons are negligible:",
            r"\[\rho = \frac{1}{qN_A\mu_p} = \frac{1}{(1.602\times10^{-19})(5\times10^{15})(400)} \approx " + g(rho, 3) + r"\ \Omega\cdot\mathrm{cm}\]",
            r"Common mistake: using the electron mobility. For a p-type sample the holes carry the current."))
    rho2 = 1 / (q * 1e17 * 700)
    R2 = rho2 * 10e-4 / (2e-4 * 0.5e-4)
    s.num(r"An IC resistor is a bar of n-type silicon with \(N_D = 10^{17}\ \mathrm{cm^{-3}}\) (at this doping \(\mu_n = 700\ \mathrm{cm^2/(V\cdot s)}\)). It is \(L = 10\ \mu\mathrm{m}\) long, \(W = 2\ \mu\mathrm{m}\) wide and \(t = 0.5\ \mu\mathrm{m}\) thick. What is its resistance in kΩ?",
          R2 / 1e3, "kΩ",
          X(r"\[\rho = \frac{1}{qN_D\mu_n} = \frac{1}{(1.602\times10^{-19})(10^{17})(700)} = " + g(rho2, 3) + r"\ \Omega\cdot\mathrm{cm}\]",
            r"\[R = \rho\frac{L}{Wt} = " + g(rho2, 3) + r"\times\frac{10\times10^{-4}}{(2\times10^{-4})(0.5\times10^{-4})} \approx " + g(R2, 3) + r"\ \Omega\]",
            r"That is about " + g(R2 / 1e3, 3) + r" kΩ. Convert µm to cm (\(1\ \mu\mathrm{m} = 10^{-4}\) cm) before mixing with Ω·cm."),
          figure=FG.bar(llabel="L = 10 µm", acap="W×t = 2 µm × 0.5 µm", vlabel="", elabel="E", carriers="e"), alt="An n-type silicon bar 10 µm long with a 2 µm by 0.5 µm cross-section; the field points along the bar and electrons drift the opposite way.")
    s.mc(r"Reader Fig. 3.16 shows silicon mobility falling as the total dopant concentration rises (for electrons, from about 1400 down to about 100 cm²/(V·s)). Why?",
         "Ionized dopant atoms break the lattice's periodicity and scatter carriers, so the mean free time τ (and μ = qτ/m*) drops",
         ["Dopants add carriers, and carriers moving together slow each other down", "The band gap closes at high doping, making carriers heavier", "Dopants lower the thermal velocity of the carriers"],
         X(r"A perfect lattice doesn't scatter carriers. Lattice vibrations and impurities do (reader Sec. 3.2.7, 3.6.3). Each charged dopant ion is a scattering site, so more dopants mean shorter \(\tau\) and lower \(\mu\).",
           r"What matters is the TOTAL dopant density \(N_D + N_A\): compensating dopants still scatter, even though they cancel each other's carriers."))
    s.round(3)
    rho3 = 1 / (q * 1e16 * 600)
    s.num(r"Compensated silicon: \(N_D = 10^{17}\) and \(N_A = 9\times10^{16}\ \mathrm{cm^{-3}}\). The electron mobility depends on the TOTAL dopant density: \(\mu_n \approx 600\ \mathrm{cm^2/(V\cdot s)}\) at \(1.9\times10^{17}\ \mathrm{cm^{-3}}\), but \(\approx 1250\) at \(10^{16}\ \mathrm{cm^{-3}}\). What is the resistivity?",
          rho3, "Ω·cm",
          X(r"Carriers: \(n_0 = N_D - N_A = 10^{16}\ \mathrm{cm^{-3}}\). Scattering: all \(1.9\times10^{17}\) ions scatter, so \(\mu_n \approx 600\).",
            r"\[\rho = \frac{1}{q\,n_0\,\mu_n} = \frac{1}{(1.602\times10^{-19})(10^{16})(600)} \approx " + g(rho3, 3) + r"\ \Omega\cdot\mathrm{cm}\]",
            r"Gotcha: using the mobility for \(10^{16}\) (1250) gives 0.50 Ω·cm, a factor of 2 too low. Using \(n = 10^{17}\) gives about 0.10 Ω·cm. Net doping sets the carrier count; total doping sets the mobility."))
    s.mc(r"In intrinsic silicon under a field, electrons drift one way and holes the other. A student says: 'equal numbers of carriers moving in opposite directions, so the currents cancel.' What is right?",
         r"The currents ADD: \(J = q\,n_i(\mu_n + \mu_p)E\)",
         ["The currents cancel exactly, so intrinsic silicon carries no drift current", r"They cancel partly, leaving \(J = q\,n_i(\mu_n - \mu_p)E\)", "Only the faster electrons carry current"],
         X(r"Opposite motion of opposite charges gives current in the SAME direction. The conductivity is \(\sigma = q(n\mu_n + p\mu_p)\), a sum of positive terms.",
           r"Gotcha: the subtraction \(\mu_n - \mu_p\) would be right for the net PARTICLE flux, not the current. (Reader Eq. 3.14 writes \(J = J^+ - J^-\) with \(J^-\) carrying its own negative sign, which can mislead; the conductivity in Eq. 3.15 is a sum.)"))
    ratio = (1e4 * 1000) / (1e16 * 400)
    s.num(r"In p-type silicon with \(N_A = 10^{16}\ \mathrm{cm^{-3}}\) (\(\mu_n = 1000\), \(\mu_p = 400\ \mathrm{cm^2/(V\cdot s)}\), \(n_i = 10^{10}\ \mathrm{cm^{-3}}\)), what is the ratio of electron drift current to hole drift current, \(J_n/J_p\), in a uniform field? Scientific notation is fine.",
          ratio, "(ratio)",
          X(r"\(p_0 = 10^{16}\), \(n_0 = n_i^2/N_A = 10^{4}\ \mathrm{cm^{-3}}\). Both see the same \(E\):",
            r"\[\frac{J_n}{J_p} = \frac{n_0\mu_n}{p_0\mu_p} = \frac{10^{4}\times1000}{10^{16}\times400} = " + sci(ratio, 2) + r"\]",
            r"Gotcha: the higher electron mobility doesn't come close to making up for \(10^{12}\) times fewer electrons. Minority carriers essentially never carry DRIFT current. When minority carriers do matter (in diodes), they move by diffusion."))
    s.round(4)
    I = 1e-3 * q * 1e12 * 500 * (0.1 / 1e-4)
    s.num(r"Preview of the MOSFET channel: a later skill models a transistor channel as a thin sheet of electrons. Suppose the sheet holds \(10^{12}\) electrons per cm² with \(\mu_n = 500\ \mathrm{cm^2/(V\cdot s)}\). It is \(W = 10\ \mu\mathrm{m}\) wide and \(L = 1\ \mu\mathrm{m}\) long, with 0.1 V across its length. Treating it as drift of a sheet (current = width × sheet charge × velocity), what current flows, in µA?",
          I * 1e6, "µA",
          X(r"Field along the channel: \(E = V/L = 0.1/(10^{-4}\ \mathrm{cm}) = 10^{3}\ \mathrm{V/cm}\), so \(v = \mu_n E = 5\times10^{5}\ \mathrm{cm/s}\).",
            r"Sheet charge: \(Q = qN_s = 1.602\times10^{-7}\ \mathrm{C/cm^2}\).",
            r"\[I = W\,Q\,v = (10^{-3}\ \mathrm{cm})(1.602\times10^{-7})(5\times10^{5}) \approx " + g(I * 1e6, 3) + r"\ \mu\mathrm{A}\]",
            r"In the MOSFET skills the gate voltage sets \(Q\), and this same drift picture becomes the triode-region current. More sheet charge or a wider device gives proportionally more current."),
          preview=["triode"])
    s.mc(r"Preview of total current: two bars, A (\(\sigma_A = 2\ \mathrm{S/cm}\)) and B (\(\sigma_B = 0.5\ \mathrm{S/cm}\)), with the same cross-section are joined end to end and carry a steady current. How do the fields inside them compare?",
         r"\(E_B = 4E_A\): the same current density needs a larger field in the less conductive bar",
         [r"\(E_A = E_B\), since the bars are in series", r"\(E_A = 4E_B\)", r"\(E_B = 2E_A\)"],
         X(r"In steady state no charge piles up, so the current density is the same in both bars: \(J = \sigma_AE_A = \sigma_BE_B\). That gives \(E_B/E_A = \sigma_A/\sigma_B = 4\).",
           r"This is the same as series resistors: the bigger resistance takes the bigger share of the voltage. The total-current skill uses this boundary condition (reader Eq. 3.58–3.60)."),
         preview=["total-current"])
    Rt = (400 / 300) ** 1.5
    s.num(r"Preview of temperature effects in transistors: in a doped resistor, the carrier count is set by the dopants and barely changes with temperature, while lattice scattering makes the mobility fall roughly as \(\mu \propto T^{-3/2}\). By what factor does the resistance of an n-type silicon resistor rise from 300 K to 400 K?",
          Rt, "(ratio)",
          X(r"\(R \propto \rho = 1/(qN_D\mu)\), with \(N_D\) fixed, so \(R \propto 1/\mu \propto T^{3/2}\):",
            r"\[\frac{R(400)}{R(300)} = \left(\frac{400}{300}\right)^{3/2} \approx " + g(Rt, 3) + r"\]",
            r"Unlike pure silicon, whose resistance collapses as \(n_i\) grows, a doped resistor behaves like a metal. The same mobility drop is why a hot MOSFET carries LESS current at a fixed gate voltage, which makes power transistors share current well."),
          preview=["triode", "total-current"])
    return s

def diffusion():
    s = Skill('diffusion')
    s.round(1)
    s.mc(r"Perfume released in one corner spreads through a room, even with no wind. In the same way, carriers in a semiconductor diffuse. Which way is the NET particle flow?",
         "From high concentration toward low concentration",
         ["From low concentration toward high concentration", "Along the electric field", "In all directions equally, so there is no net flow"],
         X(r"Each particle moves randomly: left or right is equally likely. Where there are more particles, more of them cross a given plane heading toward the sparse side than come back. Net flux: \(F = -v_{th}\lambda\,\frac{dn}{dx}\) (reader Eq. 3.48–3.50), which runs down the gradient.",
           r"No field is needed for diffusion. Individual motion is random in every direction, but the NET flow is not."))
    Dn = kTq * 1000
    s.num(r"Electrons in a silicon sample have \(\mu_n = 1000\ \mathrm{cm^2/(V\cdot s)}\). Using the Einstein relation with \(kT/q = 26\ \mathrm{mV}\), what is their diffusion constant \(D_n\)?",
          Dn, "cm²/s",
          X(r"\[D_n = \frac{kT}{q}\,\mu_n = 0.026\ \mathrm{V}\times1000\ \mathrm{cm^2/(V\cdot s)} = 26\ \mathrm{cm^2/s}\]",
            r"Mobility and diffusion both come from the same random thermal motion and collisions, so they are tied together (reader Eq. 3.56). Faster drift goes with faster diffusion."))
    s.mc(r"The electron concentration falls with \(x\) as shown. In which direction does the electron DIFFUSION CURRENT point?",
         r"\(-x\): electrons diffuse toward \(+x\), and negative charge moving \(+x\) is current in \(-x\)",
         [r"\(+x\), the direction the electrons diffuse", r"There is no current, only particle flow", r"It depends on the sign of the electric field"],
         X(r"Particle flux runs down the gradient, toward \(+x\) here. Electron current is \(J_n = -qF = qD_n\frac{dn}{dx}\) (reader Eq. 3.51). Since \(dn/dx < 0\), \(J_n < 0\), pointing toward \(-x\).",
           r"For holes the sign flips: \(J_p = -qD_p\frac{dp}{dx}\), so hole diffusion current runs WITH the hole flow. Diffusion doesn't depend on any field."),
         figure=lin_profile("high n", "low n", "n(x)"), alt="Plot of electron concentration n(x) falling linearly from a high value at x = 0 to a low value at x = W.")
    s.round(2)
    J = q * Dn * (-1e17 / 1e-4)
    s.num(r"Electron concentration falls linearly from \(10^{17}\ \mathrm{cm^{-3}}\) at \(x = 0\) to zero at \(x = 1\ \mu\mathrm{m}\). Take \(D_n = 26\ \mathrm{cm^2/s}\). What is the electron diffusion current density, with sign (\(+\) means \(+x\))?",
          J, "A/cm²",
          X(r"\[\frac{dn}{dx} = \frac{0 - 10^{17}}{10^{-4}\ \mathrm{cm}} = -10^{21}\ \mathrm{cm^{-4}}\]",
            r"\[J_n = qD_n\frac{dn}{dx} = (1.602\times10^{-19})(26)(-10^{21}) \approx " + g(J, 4) + r"\ \mathrm{A/cm^2}\]",
            r"The current flows toward \(-x\) while the electrons diffuse toward \(+x\). The magnitude is huge because the gradient is steep: diffusion can carry very large currents. Common mistake: dropping the minus sign, or leaving 1 µm in µm."),
          figure=lin_profile("10^{17} cm^{-3}", "0", "n(x)", x1lab="1 µm"), alt="Electron concentration falling linearly from 1e17 per cubic cm at x = 0 to zero at x = 1 µm.")
    Dp = kTq * 400
    dpdx = (1e14 - 1e16) / 2e-4
    Jp = -q * Dp * dpdx
    s.num(r"In a region of silicon, the hole concentration falls linearly from \(10^{16}\ \mathrm{cm^{-3}}\) at \(x = 0\) to \(10^{14}\ \mathrm{cm^{-3}}\) at \(x = 2\ \mu\mathrm{m}\). Holes have \(\mu_p = 400\ \mathrm{cm^2/(V\cdot s)}\) and \(kT/q = 26\ \mathrm{mV}\). What is the hole diffusion current density, with sign (\(+\) means \(+x\))?",
          Jp, "A/cm²",
          X(r"Einstein: \(D_p = 0.026 \times 400 = " + g(Dp, 3) + r"\ \mathrm{cm^2/s}\).",
            r"\[\frac{dp}{dx} = \frac{10^{14} - 10^{16}}{2\times10^{-4}} = " + sci(dpdx, 3) + r"\ \mathrm{cm^{-4}}\]",
            r"\[J_p = -qD_p\frac{dp}{dx} = -(1.602\times10^{-19})(" + g(Dp, 3) + r")(" + sci(dpdx, 3) + r") \approx +" + g(Jp, 3) + r"\ \mathrm{A/cm^2}\]",
            r"Positive: holes diffuse toward \(+x\) and carry current that way. Common mistakes: using \(D_n\), or the electron sign convention \(+qD\,dp/dx\)."))
    s.num(r"In the reader's model, diffusion comes from thermal motion: \(D = v_{th}\lambda\), where \(\lambda = v_{th}\tau_c\) is the mean free path. Take \(v_{th} = 10^{7}\ \mathrm{cm/s}\) and \(\lambda = 10^{-6}\ \mathrm{cm}\) (the reader's values). Estimate \(D\).",
          1e7 * 1e-6, "cm²/s",
          X(r"\[D = v_{th}\lambda = (10^{7})(10^{-6}) = 10\ \mathrm{cm^2/s}\]",
            r"Same order as the Einstein-relation values (holes about 10, electrons about 26 cm²/s). Reader Eq. 3.54 shows \(v_{th}\lambda = v_{th}^2\tau_c = (kT/m^*)\tau_c = (kT/q)(q\tau_c/m^*) = (kT/q)\mu\), which is where the Einstein relation comes from."))
    s.round(3)
    s.mc(r"Silicon is doped with a uniform, very high \(10^{19}\ \mathrm{cm^{-3}}\) donors. With no applied field, what is the electron diffusion current?",
         "Zero: diffusion depends only on the concentration GRADIENT, and a uniform concentration has none",
         ["Very large, because so many electrons are moving randomly", r"\(qD_nN_D\) per unit length", "Equal and opposite to the hole diffusion current"],
         X(r"\(J_n = qD_n\,dn/dx\). With uniform \(n\), as many electrons cross any plane from the left as from the right, so the fluxes cancel no matter how big \(n\) is.",
           r"Gotcha: a high concentration means fast random motion, but no NET flow. 'Equal and opposite to holes' would still need a gradient."))
    s.mc(r"Light is absorbed near the surface \(x = 0\), so excess electrons and holes have the SAME profile, decreasing with \(x\). Both diffuse toward \(+x\). Which statement about the diffusion CURRENTS is correct? (\(D_n > D_p\))",
         r"They point in opposite directions: holes give current in \(+x\), electrons in \(-x\). The net current points in \(-x\) because \(D_n > D_p\)",
         ["They point the same way and add", "They cancel exactly, because the profiles are identical", r"The net current points in \(+x\), because holes carry positive charge"],
         X(r"\(J_n = qD_n\frac{dn}{dx} < 0\) and \(J_p = -qD_p\frac{dp}{dx} > 0\). With \(dn/dx = dp/dx\):",
           r"\[J = J_n + J_p = q(D_n - D_p)\frac{dn}{dx} < 0\]",
           r"Gotcha: identical PARTICLE flows of opposite charges give opposite currents, and they don't cancel because electrons diffuse faster. (In real samples a small field builds up to keep the two moving together, but that is for later.)"))
    D400 = kTq * 400 / 300 * 1000
    s.num(r"At 300 K, \(kT/q = 26\ \mathrm{mV}\). Suppose a carrier's mobility stays at \(1000\ \mathrm{cm^2/(V\cdot s)}\) when the sample is heated to 400 K. What is its diffusion constant at 400 K?",
          D400, "cm²/s",
          X(r"The Einstein relation uses the thermal voltage at the ACTUAL temperature: \(kT/q \propto T\).",
            r"\[\frac{kT}{q}\Big|_{400\,K} = 26\ \mathrm{mV}\times\frac{400}{300} = 34.7\ \mathrm{mV}, \quad D = 0.0347\times1000 \approx " + g(D400, 3) + r"\ \mathrm{cm^2/s}\]",
            r"Gotcha: '26 mV' is not a constant of nature; it is \(kT/q\) at room temperature. (In reality \(\mu\) also falls with \(T\), so the actual \(D\) changes less.)"))
    s.round(4)
    L = 1e-5
    Ereq = kTq / L
    s.num(r"Preview of the PN junction: in equilibrium the electron current must be zero even where the electron concentration varies. Suppose \(n(x) = 10^{16}e^{-x/L}\) with \(L = 0.1\ \mu\mathrm{m}\). Using drift current \(J_{drift} = qn\mu_nE\) and the Einstein relation (\(kT/q = 26\ \mathrm{mV}\)), what field magnitude makes drift exactly cancel diffusion?",
          Ereq, "V/cm",
          X(r"Diffusion: \(J_{diff} = qD_n\frac{dn}{dx} = -qD_n\frac{n}{L}\). Setting \(qn\mu_nE + J_{diff} = 0\):",
            r"\[E = \frac{D_n}{\mu_n}\cdot\frac{1}{L} = \frac{kT/q}{L} = \frac{0.026}{10^{-5}\ \mathrm{cm}} = " + g(Ereq, 3) + r"\ \mathrm{V/cm}\]",
            r"The concentration and the mobility both cancel; only \(kT/q\) and the gradient length matter. Exactly this built-in field appears inside every PN junction, holding back the diffusion of carriers."),
          preview=["total-current", "pn-overview"])
    Dp4 = kTq * 400
    I4 = q * Dp4 * 1e12 / 1e-4 * 1e-6
    s.num(r"Preview of diode current: in a short region, injected holes fall linearly from \(10^{12}\ \mathrm{cm^{-3}}\) at \(x = 0\) to zero at \(x = 1\ \mu\mathrm{m}\). Take \(D_p = 10.4\ \mathrm{cm^2/s}\). If the junction area is \(100\ \mu\mathrm{m}^2\), what diffusion current flows, in nA?",
          I4 * 1e9, "nA",
          X(r"\[J_p = -qD_p\frac{dp}{dx} = (1.602\times10^{-19})(10.4)\frac{10^{12}}{10^{-4}} = " + sci(I4 / 1e-6, 3) + r"\ \mathrm{A/cm^2}\]",
            r"Area: \(100\ \mu\mathrm{m^2} = 10^{-6}\ \mathrm{cm^2}\), so \(I = " + g(I4 * 1e9, 3) + r"\ \mathrm{nA}\).",
            r"In the diode skills, the forward voltage sets the concentration at the edge exponentially (\(\propto e^{qV/kT}\)), which turns this linear-profile diffusion current into the diode's exponential I–V curve."),
          figure=lin_profile("10^{12} cm^{-3}", "0", "p(x)", x1lab="1 µm"), alt="Hole concentration falling linearly from 1e12 per cubic cm at x = 0 to zero at x = 1 µm.",
          preview=["diode-iv"])
    s.mc(r"Preview of the PN junction: a block of p-type silicon (\(p \approx 10^{16}\)) is brought into contact with a block of n-type silicon (\(n \approx 10^{16}\ \mathrm{cm^{-3}}\)). What happens first, at the moment of contact?",
         "Holes diffuse from the P side into the N side and electrons diffuse from the N side into the P side, driven by enormous concentration gradients",
         ["Nothing, because there is no applied voltage", "Electrons diffuse from P to N and holes from N to P", "Only electrons move, because they are lighter"],
         X(r"Diffusion needs only a gradient. Holes go from \(10^{16}\) (P) toward \(10^{4}\) (N), and electrons from \(10^{16}\) (N) toward \(10^{4}\) (P).",
           r"Both currents point from P to N (holes moving P→N, and electrons moving N→P, which is current P→N). The charge they leave behind builds the junction's field, which later stops the flow. Coming up in the PN junction skills."),
         figure=FG.pn_block(show_dep=False), alt="A P-type block on the left touching an N-type block on the right.",
         preview=["pn-overview"])
    return s

def total_current():
    s = Skill('total-current')
    s.round(1)
    s.mc(r"Which expression gives the TOTAL electron current density when both a field and a concentration gradient are present?",
         r"\(J_n = q\,n\,\mu_n E + qD_n\frac{dn}{dx}\)",
         [r"\(J_n = q\,n\,\mu_n E - qD_n\frac{dn}{dx}\)", r"\(J_n = q\,n\,\mu_n E\) only, since diffusion carries no charge", r"\(J_n = qD_n\frac{dn}{dx}\) only, since fields only move holes"],
         X(r"Drift plus diffusion (reader Eq. 3.57): \(J_n = q\mu_nnE + qD_n\,dn/dx\). The electron diffusion term has a PLUS sign because the flux \(-D_n\,dn/dx\) is multiplied by charge \(-q\).",
           r"For holes, \(J_p = q\mu_ppE - qD_p\,dp/dx\). The minus-sign version is the hole form applied to electrons."))
    E2 = 10 * 5 / 2
    s.num(r"Steady current flows through two materials joined at an interface (see figure): \(\sigma_1 = 10\ \mathrm{S/cm}\) with field \(E_1 = 5\ \mathrm{V/cm}\), then \(\sigma_2 = 2\ \mathrm{S/cm}\). What is the field \(E_2\)?",
          E2, "V/cm",
          X(r"No charge piles up, so \(J_1 = J_2\): \(\sigma_1E_1 = \sigma_2E_2\) (reader Eq. 3.58–3.60).",
            r"\[E_2 = \frac{\sigma_1}{\sigma_2}E_1 = \frac{10}{2}\times5 = 25\ \mathrm{V/cm}\]",
            r"The field JUMPS at the interface, and it is larger in the poorer conductor."),
          figure=FG.plot([dict(pts=[(0, 1), (1, 1), (1, 5), (2, 5)])], (0, 2.2), (0, 6), "x", "E(x)", w=320, h=190, xticks=[(0.5, "σ₁"), (1.5, "σ₂")],
                         label="Field steps up at an interface", texts=[(0.5, 1.6, "E₁"), (1.5, 5.5, "E₂ = ?")]),
          alt="Step plot of field E(x): a low constant value E1 in material 1 (left), jumping at the interface to a higher constant value E2 in material 2 (right).")
    s.mc(r"In an ordinary doped silicon resistor carrying current, which component dominates?",
         "Drift of the majority carriers; the carrier concentration is uniform, so diffusion is about zero",
         ["Diffusion of majority carriers", "Drift of minority carriers", "Drift and diffusion are always equal"],
         X(r"In a uniformly doped bar \(dn/dx \approx 0\), so \(J \approx q n\mu_n E\) with the majority carriers (reader Sec. 3.7.4: 'In resistors ... the second term is nearly zero').",
           r"Minority carriers are \(10^{10}\)–\(10^{12}\) times fewer. Diffusion only matters where concentrations change, such as near junctions."))
    s.round(2)
    Jdr = q * 1e16 * 1000 * (-10)
    Jdf = q * kTq * 1000 * (-1e19)
    s.num(r"At one point in silicon: \(n = 10^{16}\ \mathrm{cm^{-3}}\), \(\mu_n = 1000\ \mathrm{cm^2/(V\cdot s)}\), \(D_n = 26\ \mathrm{cm^2/s}\), field \(E = -10\ \mathrm{V/cm}\) (pointing toward \(-x\)), and \(dn/dx = -10^{19}\ \mathrm{cm^{-4}}\). What is the total electron current density, with sign?",
          Jdr + Jdf, "A/cm²",
          X(r"\[J_{drift} = qn\mu_nE = (1.602\times10^{-19})(10^{16})(1000)(-10) = " + g(Jdr, 4) + r"\ \mathrm{A/cm^2}\]",
            r"\[J_{diff} = qD_n\frac{dn}{dx} = (1.602\times10^{-19})(26)(-10^{19}) = " + g(Jdf, 4) + r"\ \mathrm{A/cm^2}\]",
            r"\[J_n = " + g(Jdr + Jdf, 4) + r"\ \mathrm{A/cm^2}\]",
            r"Both terms point toward \(-x\), so they add. Signs matter: track \(E\) and \(dn/dx\) separately."))
    Eeq = -kTq * 1e20 / 1e16
    s.num(r"In thermal equilibrium (no net current), at one point the electron concentration is \(n = 10^{16}\ \mathrm{cm^{-3}}\) and is INCREASING with \(x\) at \(dn/dx = 10^{20}\ \mathrm{cm^{-4}}\). With \(kT/q = 26\ \mathrm{mV}\), what is the electric field there, with sign?",
          Eeq, "V/cm",
          X(r"Set \(J_n = qn\mu_nE + qD_n\frac{dn}{dx} = 0\) and use \(D_n/\mu_n = kT/q\):",
            r"\[E = -\frac{kT}{q}\cdot\frac{1}{n}\frac{dn}{dx} = -0.026\times\frac{10^{20}}{10^{16}} = " + g(Eeq, 3) + r"\ \mathrm{V/cm}\]",
            r"Electrons diffuse toward \(-x\) (current in \(+x\)). The field points toward \(-x\), so it pushes electrons toward \(+x\) (current in \(-x\)), and the two cancel."))
    J3, L1, s1, L2, s2 = 20.0, 2e-4, 4.0, 1e-4, 0.5
    V3 = J3 * (L1 / s1 + L2 / s2)
    s.num(r"A current density of \(J = 20\ \mathrm{A/cm^2}\) flows through two layers in series: layer 1 is 2 µm thick with \(\sigma_1 = 4\ \mathrm{S/cm}\), and layer 2 is 1 µm thick with \(\sigma_2 = 0.5\ \mathrm{S/cm}\). What is the total voltage across the stack, in mV?",
          V3 * 1e3, "mV",
          X(r"Same \(J\) in both layers, so \(E_i = J/\sigma_i\): \(E_1 = 5\ \mathrm{V/cm}\), \(E_2 = 40\ \mathrm{V/cm}\).",
            r"\[V = E_1L_1 + E_2L_2 = 5(2\times10^{-4}) + 40(10^{-4}) = 1\ \mathrm{mV} + 4\ \mathrm{mV} = " + g(V3 * 1e3, 3) + r"\ \mathrm{mV}\]",
            r"The thinner but more resistive layer drops most of the voltage, just like series resistors."))
    s.round(3)
    s.mc(r"Silicon has a non-uniform doping profile, and the sample is in thermal equilibrium with no connections. Which statement is correct?",
         "A built-in electric field exists, and for EACH carrier type drift exactly cancels diffusion: Jₙ = 0 and Jₚ = 0 separately",
         ["No field can exist, because no current flows", "A field exists, but only the total J = Jₙ + Jₚ is zero; Jₙ and Jₚ can each be nonzero", "Diffusion is impossible in equilibrium, so the carriers redistribute until they are uniform"],
         X(r"With a doping gradient, the carriers follow the dopants, so concentration gradients exist and so does diffusion. Equilibrium needs zero current of each type separately (otherwise electrons or holes would keep piling up somewhere, and energy would be dissipated with nothing supplying it). So a field forms: \(E = -\frac{kT}{q}\frac{1}{n}\frac{dn}{dx}\).",
           r"Gotcha: zero current does NOT mean zero field. The carriers can't become uniform, because the fixed ions would then leave huge net charge."))
    s.mc(r"Electron concentration INCREASES with \(x\), and an electric field points toward \(+x\). Which way do the electron drift current and the electron diffusion current point?",
         r"Both point toward \(+x\), so they add",
         [r"Drift toward \(+x\), diffusion toward \(-x\): they oppose", r"Drift toward \(-x\), diffusion toward \(+x\)", r"Both point toward \(-x\)"],
         X(r"Drift current always follows \(E\) for both carriers: \(+x\).",
           r"Diffusion: electrons flow down the gradient toward \(-x\). Negative charge moving toward \(-x\) is current toward \(+x\) (\(J = qD_n\,dn/dx > 0\)).",
           r"Gotcha: it's tempting to say drift and diffusion 'fight', but they only oppose each other when the field points the other way, as in equilibrium."))
    ratio3 = (kTq * 1000 * 1e16) / (1e3 * 1000 * 100)
    s.num(r"In p-type silicon (\(N_A = 10^{17}\ \mathrm{cm^{-3}}\)), the minority electrons have \(n = 10^{3}\ \mathrm{cm^{-3}}\) and \(\mu_n = 1000\ \mathrm{cm^2/(V\cdot s)}\). The field is \(E = 100\ \mathrm{V/cm}\). Injected electrons make a gradient of \(|dn/dx| = 10^{16}\ \mathrm{cm^{-4}}\). What is the ratio \(|J_{n,diff}|/|J_{n,drift}|\)? Use \(kT/q = 26\ \mathrm{mV}\); scientific notation is fine.",
          ratio3, "(ratio)",
          X(r"\[\frac{|J_{diff}|}{|J_{drift}|} = \frac{D_n|dn/dx|}{n\mu_nE} = \frac{26\times10^{16}}{10^{3}\times1000\times100} = " + sci(ratio3, 2) + r"\]",
            r"Gotcha: for minority carriers, drift is negligible because \(n\) is tiny, but diffusion depends on the GRADIENT, which can be large. Minority-carrier currents are diffusion currents. That's the key simplification behind the diode equation."))
    s.round(4)
    dphi = kTq * math.log(1e16 / 1e4)
    s.num(r"Preview of the PN junction's barrier: in equilibrium, \(J_n = 0\) gives \(E = -\frac{kT}{q}\frac{1}{n}\frac{dn}{dx}\). Combine this with \(E = -d\varphi/dx\) and integrate across a region where \(n\) changes from \(10^{4}\) to \(10^{16}\ \mathrm{cm^{-3}}\). What is the potential difference \(\varphi_{high\,n} - \varphi_{low\,n}\)? (\(kT/q = 26\ \mathrm{mV}\))",
          dphi, "V",
          X(r"\[\frac{d\varphi}{dx} = \frac{kT}{q}\frac{1}{n}\frac{dn}{dx} = \frac{kT}{q}\frac{d\ln n}{dx} \Rightarrow \Delta\varphi = \frac{kT}{q}\ln\frac{n_2}{n_1}\]",
            r"\[\Delta\varphi = 0.026\ln(10^{12}) = 0.026 \times 27.63 \approx " + g(dphi, 3) + r"\ \mathrm{V}\]",
            r"The high-\(n\) side is about 0.72 V higher. That is the built-in potential of a junction between \(10^{16}\) n-type and \(10^{16}\) p-type silicon (where \(n_p = 10^{4}\)), which you'll meet next."),
          preview=["pn-overview"])
    s.mc(r"Preview of the continuity equation: in steady state (nothing changing in time), the electron current density \(J_n\) gets smaller along \(x\) through some region. What must be happening in that region?",
         "Electrons are recombining (disappearing) there; charge can't pile up, so a shrinking current means carriers are being removed",
         ["Electrons are piling up, so the charge density is growing", "Nothing special; currents can vary freely in steady state", "The electric field must be zero there"],
         X(r"Count the carriers in a thin slice: more flowing in than out means either accumulation (not allowed in steady state) or loss. The loss is recombination.",
           r"The continuity equation writes this as \(dJ_p/dx = -q\cdot(\text{net recombination rate})\) for holes. In a diode it is how injected minority carriers die off over a diffusion length, with majority-carrier current taking over so the TOTAL current stays constant."),
         preview=["continuity"])
    Eb = kTq * 1e21 / 1e14
    s.num(r"Preview of fields in a PN junction: in the junction's transition region, the electron gradient is \(|dn/dx| = 10^{21}\ \mathrm{cm^{-4}}\) at a point where \(n = 10^{14}\ \mathrm{cm^{-3}}\). Electron current is zero in equilibrium. What field magnitude is needed? (\(kT/q = 26\ \mathrm{mV}\))",
          Eb, "V/cm",
          X(r"\[|E| = \frac{kT}{q}\cdot\frac{|dn/dx|}{n} = 0.026\times\frac{10^{21}}{10^{14}} = " + sci(Eb, 2) + r"\ \mathrm{V/cm}\]",
            r"Fields of tens to hundreds of kV/cm are normal inside junctions, because drift has to cancel a huge diffusion current (here about \(4\times10^{3}\ \mathrm{A/cm^2}\) of diffusion alone). The depletion-approximation skill computes this field from the charge instead."),
          preview=["pn-overview", "depl-approx"])
    return s

def carrier_pot():
    s = Skill('carrier-pot')
    s.round(1)
    phip = -kTq * math.log(1e16 / ni)
    s.num(r"Relative to intrinsic silicon, what is the potential \(\varphi_p\) of a p-type region with \(N_A = 10^{16}\ \mathrm{cm^{-3}}\)? Use \(\varphi_p = -\frac{kT}{q}\ln\frac{p_0}{n_i}\), \(kT/q = 26\ \mathrm{mV}\), \(n_i = 10^{10}\ \mathrm{cm^{-3}}\). Answer in mV, with sign.",
          phip * 1e3, "mV",
          X(r"\[\varphi_p = -0.026\ln\frac{10^{16}}{10^{10}} = -0.026\times13.82 \approx " + g(phip * 1e3, 3) + r"\ \mathrm{mV}\]",
            r"Quick check with the reader's rule: 6 decades × 60 mV = −360 mV (Sec. 5.3). The sign is negative because p-type has FEWER electrons than intrinsic."),
          figure=FG.band_diagram("p"), alt="Band diagram of p-type silicon: the Fermi level EF lies below the mid-gap intrinsic level Ei, near the valence band.")
    s.mc(r"Taking intrinsic silicon as the zero of potential, what are the signs of the equilibrium potentials of n-type and p-type regions?",
         "n-type is positive, p-type is negative",
         ["n-type is negative, p-type is positive", "Both are positive and grow with doping", "Both are zero, since each region is neutral"],
         X(r"\(n = n_ie^{\varphi/V_{th}}\) (reader Eq. 5.5). More electrons than \(n_i\) means \(\varphi > 0\); fewer (p-type: \(n = n_i^2/N_A < n_i\)) means \(\varphi < 0\).",
           r"Electrons collect where the potential is HIGH (their energy \(-q\varphi\) is low). Being charge-neutral doesn't make the potential zero: neutral regions sit at different potentials, and that difference is what a junction exposes."))
    s.mc(r"At 300 K, about how much does the equilibrium potential of a region change for each factor-of-10 increase in its electron concentration?",
         "About +60 mV",
         ["About +26 mV", "About +600 mV", "About +2.3 mV"],
         X(r"\[\Delta\varphi = \frac{kT}{q}\ln 10 = 26\ \mathrm{mV}\times2.303 \approx 60\ \mathrm{mV\ per\ decade}\]",
           r"(Reader Eq. 5.12.) 26 mV is per factor of \(e\), not per factor of 10. This 60 mV/decade rule makes potentials quick to estimate: for \(10^{17}\) n-type, 7 decades above \(n_i\), it's about 420 mV."))
    s.round(2)
    dphi = kTq * math.log(1e17 * 1e15 / ni ** 2)
    s.num(r"An n-type region (\(N_D = 10^{17}\ \mathrm{cm^{-3}}\)) and a p-type region (\(N_A = 10^{15}\ \mathrm{cm^{-3}}\)) are each in equilibrium. Using \(\varphi = \pm\frac{kT}{q}\ln(\text{majority}/n_i)\), what is \(\varphi_n - \varphi_p\)? (\(kT/q = 26\ \mathrm{mV}\), \(n_i = 10^{10}\ \mathrm{cm^{-3}}\))",
          dphi, "V",
          X(r"\[\varphi_n = 0.026\ln(10^{7}) = 0.419\ \mathrm{V}, \quad \varphi_p = -0.026\ln(10^{5}) = -0.299\ \mathrm{V}\]",
            r"\[\varphi_n - \varphi_p = 0.026\ln\frac{N_DN_A}{n_i^2} = 0.026\ln(10^{12}) \approx " + g(dphi, 3) + r"\ \mathrm{V}\]",
            r"Check: 12 decades × 60 mV ≈ 0.72 V. Common mistake: subtracting the magnitudes (0.12 V) instead of the signed values."),
          figure=FG.plot([dict(pts=[(0, -0.3), (1, -0.3), (1.5, 0.42), (2.5, 0.42)])], (0, 2.6), (-0.5, 0.6), "x", "φ (V)", w=330, h=210,
                         texts=[(0.5, -0.4, "p-type"), (2.0, 0.5, "n-type")], hlines=[(0, "intrinsic = 0")], label="Potential of p and n regions"),
          alt="Potential versus position: a p-type region on the left sits below zero (intrinsic reference), and an n-type region on the right sits above zero.")
    n2 = ni * math.exp(0.3 / kTq)
    s.num(r"A region of silicon in equilibrium sits at \(\varphi = +0.30\ \mathrm{V}\) relative to intrinsic silicon. What is its electron concentration? (\(n = n_ie^{\varphi/(kT/q)}\), \(kT/q = 26\ \mathrm{mV}\), \(n_i = 10^{10}\ \mathrm{cm^{-3}}\)) Scientific notation is fine.",
          n2, "cm⁻³",
          X(r"\[n = 10^{10}\exp\!\left(\frac{0.30}{0.026}\right) = 10^{10}e^{11.54} \approx " + sci(n2, 3) + r"\ \mathrm{cm^{-3}}\]",
            r"Rule-of-thumb check: \(300/60 = 5\) decades, giving about \(10^{15}\). The exponential is very sensitive: an error of 26 mV in \(\varphi\) changes \(n\) by a factor of \(e\). That's why the answer tolerance is set by the exact formula."),
          tol=0.03)
    s.mc(r"Two points A and B are in the same piece of silicon in equilibrium, and B's potential is 120 mV higher than A's. How do their electron concentrations compare? (\(kT/q = 26\ \mathrm{mV}\))",
         r"\(n_B \approx 100\,n_A\) (that is, \(e^{120/26}\))",
         [r"\(n_B \approx n_A/100\)", r"\(n_B \approx 4.6\,n_A\)", r"\(n_B = n_A\), since equilibrium means uniform concentration"],
         X(r"\[\frac{n_B}{n_A} = e^{(\varphi_B-\varphi_A)/V_{th}} = e^{120/26} = e^{4.62} \approx 101\]",
           r"Two decades at 60 mV each. A higher potential attracts electrons. 4.6 is the exponent, not the ratio, and equilibrium does NOT require uniform concentrations; it requires zero current, which this Boltzmann relation guarantees."))
    s.round(3)
    s.mc(r"In equilibrium, point B is 60 mV LOWER in potential than point A. Compare the HOLE concentrations.",
         r"\(p_B \approx 10\,p_A\): holes are more plentiful where the potential is lower",
         [r"\(p_B \approx p_A/10\): fewer carriers where the potential is lower", r"\(p_B = p_A\): potential only affects electrons", r"\(p_B \approx 60\,p_A\)"],
         X(r"Holes follow the opposite exponent: \(p = n_ie^{-\varphi/V_{th}}\) (from Eq. 5.9 and 5.10). A 60 mV DROP means one decade MORE holes, and electrons fall by 10 times, so \(np = n_i^2\) still holds.",
           r"Gotcha: a lower potential is lower energy for a positive charge, so holes gather there, while electrons gather at HIGH potential."))
    phic = kTq * math.log((5e16 - 4.9e16) / ni)
    s.num(r"A compensated region has \(N_D = 5\times10^{16}\) and \(N_A = 4.9\times10^{16}\ \mathrm{cm^{-3}}\). What is its potential relative to intrinsic silicon, in mV? (\(kT/q = 26\ \mathrm{mV}\), \(n_i = 10^{10}\ \mathrm{cm^{-3}}\))",
          phic * 1e3, "mV",
          X(r"Net doping sets the carriers: \(n_0 = N_D - N_A = 10^{15}\ \mathrm{cm^{-3}}\).",
            r"\[\varphi = 0.026\ln\frac{10^{15}}{10^{10}} = 0.026\times11.51 \approx " + g(phic * 1e3, 3) + r"\ \mathrm{mV}\]",
            r"Gotcha: using \(N_D\) alone gives 401 mV, and adding the dopants (\(N_D + N_A\)) gives 419 mV. The potential tracks the free-carrier concentration, which depends on the difference."))
    s.mc(r"Electrons have charge \(-q\). In equilibrium, they collect where the electrostatic potential is HIGH. Why is that consistent with 'things settle at low energy'?",
         r"An electron's potential energy is \(-q\varphi\), so a high \(\varphi\) is LOW energy for an electron",
         ["It isn't; electrons are pushed to high energy by diffusion", "Potential and energy are the same thing for any charge", "Electrons gain kinetic energy at high potential, which keeps them there"],
         X(r"\(U = (-q)\varphi\). Raising \(\varphi\) by 1 V lowers an electron's energy by 1 eV. That's why the reader says an electron 'floats' to the high-potential point (Sec. 4.4.3), and why \(n \propto e^{+q\varphi/kT}\) is a Boltzmann factor \(e^{-U/kT}\) in disguise.",
           r"Band diagrams plot ELECTRON energy, so they look 'upside down' compared with potential plots. Keep the sign straight."))
    s.round(4)
    phibi = kTq * math.log(1e16 * 1e18 / ni ** 2)
    s.num(r"Preview of the junction's built-in potential: an n-type region (\(N_D = 10^{16}\)) touches a p-type region (\(N_A = 10^{18}\ \mathrm{cm^{-3}}\)). In equilibrium each keeps its own \(\varphi\) relative to intrinsic silicon. What is the potential step \(\varphi_n - \varphi_p\) across the junction? (\(kT/q = 26\ \mathrm{mV}\))",
          phibi, "V",
          X(r"\[\varphi_n - \varphi_p = 0.026\left[\ln\frac{10^{16}}{10^{10}} + \ln\frac{10^{18}}{10^{10}}\right] = 0.026\ln(10^{14}) \approx " + g(phibi, 3) + r"\ \mathrm{V}\]",
            r"That's the junction's built-in potential: the barrier electrons on the N side must climb to reach the P side. Heavier doping on either side makes it larger, but only logarithmically (each decade adds 60 mV)."),
          figure=FG.pn_profiles(NA=100, ND=1, show=("phi",), phibi="φ_n − φ_p"), alt="Potential across a PN junction rising smoothly from the P-side level to the higher N-side level; the total step is labelled φn − φp.",
          preview=["contact-pot", "pn-overview"])
    s.mc(r"Preview of the PN junction: in a junction in equilibrium, which side sits at the higher potential, and what does that mean for the electrons on the N side?",
         "The N side is higher; electrons on the N side sit in an energy valley and must climb a barrier to diffuse into the P side",
         ["The P side is higher, so electrons are pulled into it", "Both sides are at the same potential, because the junction is neutral", "The N side is higher, so electrons slide easily into the P side"],
         X(r"\(\varphi_n > 0 > \varphi_p\). For an electron, energy is \(-q\varphi\), so the N side is LOW energy. Getting to the P side means climbing an energy step of \(q(\varphi_n - \varphi_p)\).",
           r"Only the few electrons with enough thermal energy make it. That's why the equilibrium diffusion current is small, and why changing the barrier height with an applied voltage changes the current exponentially."),
         preview=["pn-overview"])
    f = math.exp(0.1 / kTq)
    s.num(r"Preview of diode behaviour: the number of electrons that can climb a potential barrier scales as \(e^{-q\Delta\varphi/kT}\). If an applied voltage LOWERS the barrier by 0.1 V, by what factor does the number of electrons able to cross grow? (\(kT/q = 26\ \mathrm{mV}\))",
          f, "(factor)",
          X(r"\[\frac{e^{-(\varphi_{bi}-0.1)/V_{th}}}{e^{-\varphi_{bi}/V_{th}}} = e^{0.1/0.026} = e^{3.85} \approx " + g(f, 3) + r"\]",
            r"About 47 times more for just 100 mV. A further 60 mV gives another 10 times. That's the diode's exponential I–V law in the making: forward bias lowers the barrier, and the current soars."),
          preview=["diode-qual", "pn-overview"])
    return s
