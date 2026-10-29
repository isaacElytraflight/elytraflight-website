"""batch2a: pn-overview, depl-approx, contact-pot, rev-bias"""
from batch2a_lib import *
import batch2a_fig as FG
import math

def X(*lines): return "\n".join(lines)
def phibi(NA, ND): return kTq * math.log(NA * ND / ni ** 2)
def widths(NA, ND, V):   # V = total potential across the junction (phibi - VD)
    xn = math.sqrt(2 * eps_s * V / q * NA / (ND * (NA + ND)))
    xp = math.sqrt(2 * eps_s * V / q * ND / (NA * (NA + ND)))
    return xp, xn

PNALT = "Three stacked plots across a PN junction (P side left, N side right). Charge density: a negative block −qNA from −xp to 0 and a positive block +qND from 0 to xn. Field: zero outside, a negative triangle with its peak at the junction. Potential: rises smoothly (quadratic pieces) from the P-side level to the N-side level; the total step is φbi."

def pn_overview():
    s = Skill('pn-overview')
    s.round(1)
    s.mc(r"When P-type and N-type silicon first touch, majority carriers diffuse across the junction. Why does that create net CHARGE near the junction?",
         "The carriers that leave uncover fixed dopant ions: negative acceptor ions on the P side and positive donor ions on the N side",
         ["The carriers that cross pile up as a charged layer exactly at the metallurgical junction", "Electrons and holes are created at the junction by the contact", "It doesn't; both sides stay neutral and only the potential changes"],
         X(r"Each region started neutral: every ion was matched by a free carrier. When holes leave the P side, the \(N_A^-\) ions they were neutralizing stay behind, uncovered and fixed. Likewise, electrons leaving the N side expose \(N_D^+\) ions (reader Sec. 5.4.1, 5.4.3).",
           r"The crossing carriers become minority carriers and quickly recombine; they don't build a layer. The resulting dipole (− on P, + on N) creates the junction's field and potential step."),
         figure=FG.pn_block(), alt="A P region on the left and an N region on the right, with a dashed depletion region at the junction containing negative charge on the P side and positive charge on the N side.")
    s.mc(r"In equilibrium, which way does the built-in electric field point inside a PN junction (P side on the left, N side on the right)?",
         r"From the N side toward the P side (to the left, \(E < 0\))",
         ["From the P side toward the N side (to the right)", "There is no field in equilibrium, because no current flows", "It points up and down, perpendicular to the junction"],
         X(r"Field lines start on positive charge and end on negative charge: from the \(+N_D\) ions on the N side to the \(-N_A\) ions on the P side, so to the left. Reader Fig. 5.4 plots it as negative, peaking at the junction.",
           r"It points from high potential (N) to low potential (P), and it pushes holes back toward P and electrons back toward N, opposing the diffusion."),
         figure=FG.pn_profiles(NA=1, ND=1, show=("rho", "E")), alt="Charge density (negative block on the P side, positive block on the N side) and the electric field below it: a negative triangle peaking at the junction, meaning the field points from N toward P.")
    pb = phibi(1e16, 1e16)
    s.num(r"A PN junction has \(N_A = N_D = 10^{16}\ \mathrm{cm^{-3}}\). Using the region potentials \(\varphi_n = \frac{kT}{q}\ln\frac{N_D}{n_i}\) and \(\varphi_p = -\frac{kT}{q}\ln\frac{N_A}{n_i}\), what is the built-in potential \(\varphi_{bi} = \varphi_n - \varphi_p\)? (\(kT/q = 26\ \mathrm{mV}\), \(n_i = 10^{10}\ \mathrm{cm^{-3}}\))",
          pb, "V",
          X(r"\[\varphi_{bi} = \frac{kT}{q}\ln\frac{N_AN_D}{n_i^2} = 0.026\ln\frac{10^{32}}{10^{20}} = 0.026\times27.63 \approx " + g(pb, 3) + r"\ \mathrm{V}\]",
            r"Rule of thumb: 12 decades × 60 mV ≈ 0.72 V (reader Eq. 5.43–5.44)."))
    s.round(2)
    s.mc(r"In thermal equilibrium, what is true of the four current components in a PN junction: electron drift, electron diffusion, hole drift and hole diffusion?",
         "Each is nonzero, but electron drift cancels electron diffusion, and hole drift cancels hole diffusion",
         ["All four are zero, because nothing moves in equilibrium", "Electron diffusion cancels HOLE diffusion, and the drifts cancel each other", "Only the total is zero; electrons can carry net current one way and holes the other"],
         X(r"Reader Eq. 5.14–5.17: \(J_n = qn\mu_nE + qD_n\frac{dn}{dx} = 0\) and \(J_p = 0\), each on its own. If, say, \(J_n = -J_p \neq 0\), electrons would continuously flow one way and holes the other. That would be a steady current loop with nothing driving it, which equilibrium forbids.",
           r"Carriers are constantly moving; the components only cancel on average."),
         figure=FG.pn_profiles(NA=1, ND=1, show=("rho", "E")), alt=PNALT)
    pb2 = phibi(1e17, 1e16)
    s.num(r"A junction has \(N_A = 10^{17}\) on the P side and \(N_D = 10^{16}\ \mathrm{cm^{-3}}\) on the N side. What is \(\varphi_{bi}\)? (\(kT/q = 26\ \mathrm{mV}\), \(n_i = 10^{10}\ \mathrm{cm^{-3}}\))",
          pb2, "V",
          X(r"\[\varphi_{bi} = 0.026\ln\frac{(10^{17})(10^{16})}{10^{20}} = 0.026\ln(10^{13}) \approx " + g(pb2, 3) + r"\ \mathrm{V}\]",
            r"Equivalently, it is \((kT/q)\ln(n_n/n_p)\): electrons drop from \(10^{16}\) on the N side to \(n_i^2/N_A = 10^{3}\) on the P side, which is 13 decades, or about 0.78 V."))
    s.mc(r"Which expression gives the charge density inside the junction's transition region, and what is its sign on each side?",
         r"\(\rho = q(p - n + N_D - N_A)\): negative on the P side (holes depleted below \(N_A\)), positive on the N side",
         [r"\(\rho = q(p + n - N_D - N_A)\): negative on both sides", r"\(\rho = q(n - p + N_D - N_A)\): positive on the P side", r"\(\rho = 0\) everywhere, because the junction as a whole is neutral"],
         X(r"Reader Eq. 5.18–5.24. On the P side \(n \approx 0\) and \(p < N_A\), so \(\rho \approx q(p - N_A) < 0\). On the N side \(p \approx 0\) and \(n < N_D\), so \(\rho \approx q(N_D - n) > 0\).",
           r"The junction as a WHOLE is neutral (the two charges are equal and opposite), but the local density isn't zero. That's exactly where the field comes from."))
    s.round(3)
    s.mc(r"Why don't majority carriers keep diffusing across the junction until the hole and electron concentrations are uniform everywhere?",
         "The exposed ion charge builds a field whose drift current grows until it exactly cancels the diffusion; uniform carriers would leave the dopant ions hugely uncompensated",
         ["Diffusion stops once the carriers reach the metal contacts", "The carriers recombine as soon as they cross, so diffusion stops by itself", "They do; in equilibrium the concentrations become uniform"],
         X(r"Diffusion builds the dipole, and the dipole's field drives drift the other way. Equilibrium is reached when the potential step is exactly \(\varphi_{bi} = \frac{kT}{q}\ln\frac{N_AN_D}{n_i^2}\) (the Boltzmann relation from the carrier-potential skill).",
           r"Gotcha: recombination of the crossing carriers doesn't stop diffusion; it's what keeps the gradient there. Uniform carriers are impossible: the fixed dopants would then leave enormous net charge on each side."))
    dpb = kTq * math.log(100) * 1e3
    s.num(r"A junction has \(N_A = N_D = 10^{16}\ \mathrm{cm^{-3}}\). The P side's doping is raised 100 times, to \(10^{18}\ \mathrm{cm^{-3}}\). By how many mV does \(\varphi_{bi}\) increase? (\(kT/q = 26\ \mathrm{mV}\))",
          dpb, "mV",
          X(r"\[\Delta\varphi_{bi} = \frac{kT}{q}\ln\frac{N_A'}{N_A} = 26\ \mathrm{mV}\times\ln(100) \approx " + g(dpb, 3) + r"\ \mathrm{mV}\]",
            r"Gotcha: 100 times more doping only adds about 0.12 V (two decades × 60 mV), because the dependence is logarithmic. Silicon junctions sit at roughly 0.6–1 V across a huge range of dopings."))
    s.mc(r"Inside the transition region, a few minority electrons from the P side (generated near the junction) wander into the field. Which way are they swept, and which way do holes drift?",
         "Electrons are swept to the N side; holes drift toward the P side",
         ["Electrons are swept to the P side; holes drift toward the N side", "Both drift toward the N side", "Neither drifts; the field only affects majority carriers"],
         X(r"The field points from N to P (\(E < 0\)). Electrons move against \(E\), toward N; holes move with \(E\), toward P.",
           r"So the junction field sweeps minority carriers ACROSS the junction (P-side electrons to N, N-side holes to P). That is the equilibrium drift current that balances diffusion. Under reverse bias it's what remains: the small saturation current."),
         figure=FG.pn_profiles(NA=1, ND=1, show=("E",)), alt="Electric field across a PN junction: a negative triangle peaking at the junction, showing the field points from the N side toward the P side.")
    s.round(4)
    W = 1.0
    xn = W * 1e17 / (1e17 + 1e15)
    s.num(r"Preview of depletion widths: the uncovered charge on the two sides must be equal and opposite: \(qN_Ax_p = qN_Dx_n\). A junction with \(N_A = 10^{17}\) and \(N_D = 10^{15}\ \mathrm{cm^{-3}}\) has a total depletion width \(x_p + x_n = 1.0\ \mu\mathrm{m}\). How wide is the N-side part, \(x_n\), in µm?",
          xn, "µm",
          X(r"From charge balance, \(x_p/x_n = N_D/N_A = 10^{-2}\), so",
            r"\[x_n = W\frac{N_A}{N_A + N_D} = 1.0\times\frac{10^{17}}{1.01\times10^{17}} \approx " + g(xn, 4) + r"\ \mu\mathrm{m}\]",
            r"Almost the whole depletion region sits in the lightly doped side, because it needs more volume to uncover the same charge. The depletion-approximation skill turns this into a formula for the widths."),
          figure=FG.pn_profiles(NA=100, ND=1, show=("rho",)), alt="Charge density across a one-sided junction: a tall, narrow negative block on the heavily doped P side and a short, wide positive block on the lightly doped N side, with equal areas.",
          preview=["depl-approx"])
    s.mc(r"Preview of contact potentials: a junction has \(\varphi_{bi} \approx 0.7\ \mathrm{V}\). You connect a wire from the P side to the N side. Does current flow?",
         "No: the metal–semiconductor contacts develop their own contact potentials, which cancel φbi around the loop, so the junction is not a battery",
         ["Yes, about 0.7 V divided by the wire's resistance, until the junction runs down", "Yes, but only while the junction is warm", "Yes, a tiny current set by the diode's saturation current, forever"],
         X(r"A steady current with no energy supply would be a perpetual-motion machine. The wire–silicon junctions are junctions between dissimilar materials too, and in equilibrium the potential steps around any closed loop sum to zero (reader Sec. 5.4.7).",
           r"The next skill works through this KVL. (Light, heat flow or an applied voltage are what break equilibrium and let a junction deliver or carry current.)"),
         preview=["contact-pot"])
    s.mc(r"Preview of diode behaviour: an external voltage makes the N side MORE positive than the P side (reverse bias), raising the barrier. What happens to the diffusion and drift currents?",
         "Diffusion over the taller barrier drops exponentially, while the minority-carrier drift current stays about the same; a small net reverse current remains",
         ["Both grow in proportion to the voltage", "Diffusion rises and drift falls", "Both drop to exactly zero"],
         X(r"Only carriers with enough energy can diffuse over the barrier. Their number goes as \(e^{-(\text{barrier})/V_{th}}\), so raising the barrier shuts diffusion off fast.",
           r"The drift current is set by how many minority carriers wander into the field, not by the barrier height, so it doesn't change. What's left is a tiny reverse current. Lower the barrier instead (forward bias) and diffusion grows exponentially: the diode turns on (reader Sec. 6.2)."),
         figure=FG.pn_block(note="N side made more positive (reverse bias)"), alt="PN junction block diagram with its depletion region; the note says the N side is made more positive than the P side (reverse bias).",
         preview=["diode-qual"])
    return s

def depl_approx():
    s = Skill('depl-approx')
    s.round(1)
    s.mc(r"What does the depletion approximation assume about the PN junction?",
         r"Within \(-x_p < x < x_n\), all free carriers are removed, so \(\rho = -qN_A\) on the P side and \(+qN_D\) on the N side; outside, the material is neutral",
         ["The carrier concentrations change linearly across the junction", "The field is constant across the transition region", "Only the minority carriers are depleted"],
         X(r"Reader Eq. 5.27. Every 60 mV drop in potential cuts the carrier density by 10 times. After a few tenths of a volt the carriers are negligible next to the dopants, so treating the region as fully depleted is accurate.",
           r"The payoff: \(\rho\) becomes piecewise constant, so the field is piecewise linear and the potential piecewise quadratic, which is easy to solve."),
         figure=FG.pn_profiles(NA=1, ND=2), alt=PNALT)
    pb = phibi(1e16, 1e16)
    Xd = math.sqrt(2 * eps_s * pb / q * (1 / 1e16 + 1 / 1e16))
    s.num(r"Find the total zero-bias depletion width \(X_{d0} = \sqrt{\frac{2\varepsilon_s\varphi_{bi}}{q}\left(\frac{1}{N_A}+\frac{1}{N_D}\right)}\) for \(N_A = N_D = 10^{16}\ \mathrm{cm^{-3}}\). (\(\varphi_{bi} = " + g(pb, 3) + r"\ \mathrm{V}\), \(\varepsilon_s = 11.7\varepsilon_0 = 1.036\times10^{-12}\ \mathrm{F/cm}\), \(q = 1.602\times10^{-19}\ \mathrm{C}\).) Answer in µm.",
          Xd * 1e4, "µm",
          X(r"\[X_{d0} = \sqrt{\frac{2(1.036\times10^{-12})(" + g(pb, 3) + r")}{1.602\times10^{-19}}\left(2\times10^{-16}\right)} = " + sci(Xd, 3) + r"\ \mathrm{cm} \approx " + g(Xd * 1e4, 3) + r"\ \mu\mathrm{m}\]",
            r"Half on each side for a symmetric junction. Keep everything in cm: \(\varepsilon_s\) in F/cm and \(N\) in cm⁻³ give \(X\) in cm. Then convert (\(1\ \mu\mathrm{m} = 10^{-4}\) cm)."))
    s.mc(r"Under the depletion approximation, what does the electric field look like across the junction?",
         "Piecewise linear: zero at both depletion edges and largest in magnitude at the metallurgical junction (a triangle)",
         ["Constant across the depletion region and zero outside", "Largest at the depletion edges and zero at the junction", "Exponentially decaying away from the junction"],
         X(r"\(dE/dx = \rho/\varepsilon_s\) is constant on each side, so \(E\) is linear. It starts at 0 at \(-x_p\) and reaches \(-qN_Ax_p/\varepsilon_s\) at \(x = 0\) (Eq. 5.30), then returns to 0 at \(x_n\).",
           r"Gauss's law explains the peak: a box from the neutral P side to \(x\) encloses more and more negative charge until \(x = 0\); after that, positive charge starts cancelling it."),
         figure=FG.pn_profiles(NA=1, ND=1, show=("E",)), alt="Electric field across the junction: zero outside the depletion region, falling linearly to a negative peak at the junction and rising linearly back to zero at xn.")
    s.round(2)
    NA, ND = 1e18, 1e15
    pb2 = phibi(NA, ND)
    xp, xn = widths(NA, ND, pb2)
    s.num(r"A one-sided junction has \(N_A = 10^{18}\) and \(N_D = 10^{15}\ \mathrm{cm^{-3}}\), so \(\varphi_{bi} = " + g(pb2, 4) + r"\ \mathrm{V}\). Using \(x_n = \sqrt{\frac{2\varepsilon_s\varphi_{bi}}{q}\cdot\frac{N_A}{N_D(N_A+N_D)}}\), find \(x_n\) in µm. (\(\varepsilon_s = 1.036\times10^{-12}\ \mathrm{F/cm}\))",
          xn * 1e4, "µm",
          X(r"\[x_n = \sqrt{\frac{2(1.036\times10^{-12})(" + g(pb2, 4) + r")}{1.602\times10^{-19}}\cdot\frac{10^{18}}{10^{15}(1.001\times10^{18})}} = " + sci(xn, 3) + r"\ \mathrm{cm} \approx " + g(xn * 1e4, 3) + r"\ \mu\mathrm{m}\]",
            r"Since \(N_A \gg N_D\), this is almost \(\sqrt{2\varepsilon_s\varphi_{bi}/(qN_D)}\) (reader Eq. 5.38–5.39): the lightly doped side holds nearly all the depletion width."))
    Emax = q * ND * xn / eps_s
    s.num(r"For the same junction (\(N_D = 10^{15}\ \mathrm{cm^{-3}}\), \(x_n = " + g(xn * 1e4, 3) + r"\ \mu\mathrm{m}\)), what is the peak field magnitude \(|E_{max}| = qN_Dx_n/\varepsilon_s\)? Answer in kV/cm.",
          Emax / 1e3, "kV/cm",
          X(r"\[|E_{max}| = \frac{qN_Dx_n}{\varepsilon_s} = \frac{(1.602\times10^{-19})(10^{15})(" + sci(xn, 3) + r")}{1.036\times10^{-12}} \approx " + sci(Emax, 3) + r"\ \mathrm{V/cm}\]",
            r"That is about " + g(Emax / 1e3, 3) + r" kV/cm. You'd get the same answer from the P side, \(qN_Ax_p/\varepsilon_s\), because \(N_Ax_p = N_Dx_n\): the field is continuous at the junction (Eq. 5.33)."))
    s.num(r"Same junction: how wide is the P-side depletion region, \(x_p\), in nm? (Use \(N_Ax_p = N_Dx_n\) with \(x_n = " + g(xn * 1e4, 4) + r"\ \mu\mathrm{m}\).)",
          xp * 1e7, "nm",
          X(r"\[x_p = x_n\frac{N_D}{N_A} = " + g(xn * 1e4, 4) + r"\ \mu\mathrm{m}\times10^{-3} \approx " + g(xp * 1e7, 3) + r"\ \mathrm{nm}\]",
            r"Under a nanometre: the heavily doped side barely depletes at all. That's why a P⁺N junction is analysed as 'one-sided'."))
    s.round(3)
    s.mc(r"In a junction with \(N_A = 10^{17}\) and \(N_D = 10^{15}\ \mathrm{cm^{-3}}\), which side has the wider depletion region, and why?",
         "The N side (lightly doped): it has fewer ions per volume, so it must deplete a longer distance to uncover the same charge",
         ["The P side, because higher doping produces more charge", "Both are equal, because the junction is neutral", "The P side, because holes diffuse farther than electrons"],
         X(r"Neutrality of the whole dipole: \(N_Ax_p = N_Dx_n\), so \(x_n/x_p = N_A/N_D = 100\).",
           r"Gotcha: the heavily doped side has MORE charge per volume, so it needs LESS width. Equal TOTAL charge on each side doesn't mean equal width."),
         figure=FG.pn_profiles(NA=100, ND=1, show=("rho",)), alt="Charge density of an asymmetric junction: a tall, thin negative block on the heavily doped P side and a short, wide positive block on the lightly doped N side.")
    Em, Xw = 5e4, 0.3e-4
    s.num(r"In a junction the peak field magnitude is \(|E_{max}| = 50\ \mathrm{kV/cm}\) and the total depletion width is \(X_d = 0.3\ \mu\mathrm{m}\). What potential difference is dropped across the depletion region?",
          Em * Xw / 2, "V",
          X(r"The potential drop is the area under the field. The field is a triangle with base \(X_d\) and height \(|E_{max}|\):",
            r"\[\Delta\varphi = \tfrac12|E_{max}|X_d = \tfrac12(5\times10^{4})(0.3\times10^{-4}) = " + g(Em * Xw / 2, 3) + r"\ \mathrm{V}\]",
            r"Gotcha: forgetting the ½ (getting 1.5 V) treats the field as constant. This handy relation gives \(|E_{max}| = 2\varphi_{bi}/X_d\) in reverse."),
         figure=FG.pn_profiles(NA=1, ND=1, show=("E",), emax="|E_{max}| = 50 kV/cm"), alt="Triangular field profile across the depletion region with a peak of 50 kV/cm at the junction.")
    s.mc(r"In an asymmetric junction (\(N_A = 10\,N_D\)), how is the built-in potential split between the P-side and N-side parts of the depletion region?",
         "Most of it falls on the lightly doped N side: φ_N : φ_P = N_A : N_D = 10 : 1",
         ["It splits equally, 50/50", "Most falls on the heavily doped P side, in the ratio 10 : 1", "It all falls exactly at the metallurgical junction"],
         X(r"Each side's drop is a triangle area: \(\varphi_N = \tfrac12|E_{max}|x_n\) and \(\varphi_P = \tfrac12|E_{max}|x_p\), with the same peak field. So \(\varphi_N/\varphi_P = x_n/x_p = N_A/N_D\).",
           r"Gotcha: the lightly doped side takes both the width and the voltage. That's why, in a one-sided junction (and in the MOS body), you analyse only the lightly doped side."))
    s.round(4)
    VR = 3.0
    fac = math.sqrt((pb + VR) / pb)
    s.num(r"Preview of reverse bias: an applied reverse voltage \(V_R\) adds to the junction's potential step, so \(\varphi_{bi}\) becomes \(\varphi_{bi} + V_R\) in the width formula. For the symmetric \(10^{16}\) junction (\(\varphi_{bi} = " + g(pb, 3) + r"\ \mathrm{V}\)), by what factor does the depletion width grow at \(V_R = 3\ \mathrm{V}\)?",
          fac, "(factor)",
          X(r"\(X_d \propto \sqrt{\text{total potential}}\), so",
            r"\[\frac{X_d(3\ \mathrm{V})}{X_{d0}} = \sqrt{\frac{" + g(pb, 3) + r" + 3}{" + g(pb, 3) + r"}} \approx " + g(fac, 3) + r"\]",
            r"It's a square-root law: 5 times the voltage only about doubles the width. The reverse-bias skill builds on exactly this."),
          preview=["rev-bias"])
    Cj = eps_s / Xd
    s.num(r"Preview of junction capacitance: the depletion region acts like a parallel-plate capacitor with silicon as the dielectric, \(C = \varepsilon_s/X_d\) per unit area. Using \(X_{d0} = " + g(Xd * 1e4, 3) + r"\ \mu\mathrm{m}\) for the symmetric \(10^{16}\) junction, what is \(C\) in fF/µm²?",
          Cj * 1e7, "fF/µm²",
          X(r"\[C = \frac{\varepsilon_s}{X_{d0}} = \frac{1.036\times10^{-12}}{" + sci(Xd, 3) + r"} = " + sci(Cj, 3) + r"\ \mathrm{F/cm^2}\]",
            r"\(1\ \mathrm{F/cm^2} = 10^{15}\ \mathrm{fF}/10^{8}\ \mu\mathrm{m^2} = 10^{7}\ \mathrm{fF/\mu m^2}\), so \(C \approx " + g(Cj * 1e7, 3) + r"\ \mathrm{fF/\mu m^2}\).",
            r"Because \(X_d\) changes with voltage, this capacitance does too: the basis of varactors and of the parasitic capacitances in transistors."),
          preview=["junction-cap"])
    NAm = 1e17
    xdm = math.sqrt(2 * eps_s * 0.5 / (q * NAm))
    s.num(r"Preview of the MOS capacitor: under a MOS gate, the p-type body depletes like the lightly doped side of a one-sided junction. If 0.5 V is dropped across a body with \(N_A = 10^{17}\ \mathrm{cm^{-3}}\), how deep is the depletion region, \(x_d = \sqrt{2\varepsilon_s\varphi/(qN_A)}\), in nm?",
          xdm * 1e7, "nm",
          X(r"\[x_d = \sqrt{\frac{2(1.036\times10^{-12})(0.5)}{(1.602\times10^{-19})(10^{17})}} = " + sci(xdm, 3) + r"\ \mathrm{cm} \approx " + g(xdm * 1e7, 3) + r"\ \mathrm{nm}\]",
            r"The gate plays the role of the heavily doped side (a sheet of charge with zero width). The MOS skills use this result to find where the body depletes and when it inverts."),
          figure=FG.mos_stack("depletion"), alt="MOS capacitor cross-section: n+ poly gate on top with positive charge, a thin oxide, and a p-type body whose top part is a depletion region of depth xdep containing negative ions.",
          preview=["mos-regions"])
    return s

def contact_pot():
    s = Skill('contact-pot')
    s.round(1)
    pb = phibi(1e17, 1e17)
    s.num(r"What is the built-in potential of a junction with \(N_A = N_D = 10^{17}\ \mathrm{cm^{-3}}\)? (\(\varphi_{bi} = \frac{kT}{q}\ln\frac{N_AN_D}{n_i^2}\), \(kT/q = 26\ \mathrm{mV}\), \(n_i = 10^{10}\ \mathrm{cm^{-3}}\))",
          pb, "V",
          X(r"\[\varphi_{bi} = 0.026\ln\frac{10^{34}}{10^{20}} = 0.026\times32.24 \approx " + g(pb, 3) + r"\ \mathrm{V}\]",
            r"14 decades × 60 mV ≈ 0.84 V."))
    s.mc(r"The two ends of a PN junction (\(\varphi_{bi} = 0.8\ \mathrm{V}\)) are shorted with a copper wire. In equilibrium, what current flows, and why?",
         "None: the copper–P and copper–N contacts have contact potentials that exactly cancel φbi around the loop",
         ["0.8 V divided by the wire resistance", "A small leakage current, IS", "A large current at first that slowly decays as the junction discharges"],
         X(r"KVL around the loop: \(\varphi_{bi} + \varphi_{mn} - \varphi_{mp} = 0\) (reader Eq. 5.45, 5.50). Every junction of dissimilar materials, including metal–semiconductor, forms a contact potential. In equilibrium the sum around any closed loop is zero, otherwise you could extract energy from nothing.",
           r"There's no 'charge' to run down; the junction never stored usable energy."),
         figure=FG.pn_block(note="P and N ends shorted by a metal wire"), alt="PN junction with its depletion region; the note says the P and N ends are shorted by a metal wire.")
    s.mc(r"An ideal voltmeter is connected across an isolated PN junction in equilibrium (\(\varphi_{bi} = 0.7\ \mathrm{V}\)). What does it read?",
         "0 V",
         ["0.7 V", "−0.7 V", "It depends on the meter's probe metal"],
         X(r"The meter's probes make metal contacts on each side, and their contact potentials cancel the built-in potential, just like a shorting wire. The meter measures the difference in electrochemical potential, which is zero in equilibrium.",
           r"\(\varphi_{bi}\) is real (it has a field and stored charge), but you can't measure it with a voltmeter. The probe metal doesn't matter: all the contact potentials in the loop cancel."))
    s.round(2)
    phim_p = kTq * math.log(1e22 * 1e16 / ni ** 2)
    s.num(r"The reader models a metal as extremely heavily doped n-type silicon, \(N_m \approx 10^{22}\ \mathrm{cm^{-3}}\). Using \(\varphi = \frac{kT}{q}\ln\frac{n}{n_i}\) for n-type and \(\varphi = -\frac{kT}{q}\ln\frac{p}{n_i}\) for p-type, find the contact potential between such a metal and p-type silicon with \(N_A = 10^{16}\ \mathrm{cm^{-3}}\): \(\varphi_{mp} = \varphi_m - \varphi_p\).",
          phim_p, "V",
          X(r"\[\varphi_m = 0.026\ln(10^{12}) = 0.718\ \mathrm{V}, \quad \varphi_p = -0.026\ln(10^{6}) = -0.359\ \mathrm{V}\]",
            r"\[\varphi_{mp} = 0.026\ln\frac{N_mN_A}{n_i^2} = 0.026\ln(10^{18}) \approx " + g(phim_p, 3) + r"\ \mathrm{V}\]",
            r"Note: reader Eq. 5.46–5.47 write these potentials as \(\frac{kT}{q}\ln\frac{N_D}{N_A}\) and \(\frac{kT}{q}\ln\frac{N_m}{N_A}\). That's a typo: with the p-region as reference, the correct form has \(N_DN_A/n_i^2\). The cancellation argument in Eq. 5.48–5.50 still works either way."))
    phim_n = kTq * math.log(1e22 / 1e17)
    s.num(r"Same model (metal = \(10^{22}\ \mathrm{cm^{-3}}\) n-type). What is the contact potential between the metal and n-type silicon with \(N_D = 10^{17}\ \mathrm{cm^{-3}}\), \(\varphi_{mn} = \varphi_m - \varphi_n\)?",
          phim_n, "V",
          X(r"Both are n-type, so the \(n_i\) cancels:",
            r"\[\varphi_{mn} = \frac{kT}{q}\ln\frac{N_m}{N_D} = 0.026\ln(10^{5}) \approx " + g(phim_n, 3) + r"\ \mathrm{V}\]",
            r"Heavier doping in the silicon gives a smaller step to the metal. That is one reason ohmic contacts are made through heavily doped (n⁺/p⁺) regions."))
    s.mc(r"Why can't a PN junction in thermal equilibrium be used as a battery to power a resistor?",
         "In equilibrium no net energy can flow; the contact potentials around any external loop cancel φbi exactly, so the loop's net EMF is zero",
         ["Its internal resistance is too high", "The built-in field is too weak to drive current", "It can, but only until the depletion region discharges"],
         X(r"The reader compares this to a 'perfect ratchet': if a junction could drive current using only thermal energy at one temperature, it would be a perpetual-motion machine (Sec. 5.4.7).",
           r"Providing a metal path just gives carriers another route across the same barrier, and it presents an equal barrier. With an energy input (light, a temperature difference, an applied voltage), the junction can deliver power: that's a solar cell."))
    s.round(3)
    s.mc(r"One student computes potentials relative to intrinsic silicon; another uses the P region as the zero. Do they get different built-in potentials for the junction?",
         "No: φbi is a potential DIFFERENCE, so it is the same for any choice of reference",
         ["Yes; the intrinsic reference gives the larger value", "Yes; only the P-region reference gives the physical value", "They differ by the contact potential of the metal"],
         X(r"Moving the zero shifts every potential by the same constant, so differences don't change. \(\varphi_{bi} = \varphi_n - \varphi_p = \frac{kT}{q}\ln\frac{N_DN_A}{n_i^2}\) either way.",
           r"Gotcha: the reader switches references between Sec. 5.3 (intrinsic) and Sec. 5.4.7 (P region), and that can look like a different result. It isn't."))
    pa = phibi(1e18, 1e14)
    s.num(r"Junction A has \(N_A = 10^{18}\) and \(N_D = 10^{14}\ \mathrm{cm^{-3}}\). Junction B has \(N_A = N_D = 10^{16}\ \mathrm{cm^{-3}}\). What is \(\varphi_{bi}\) of junction A? (\(kT/q = 26\ \mathrm{mV}\), \(n_i = 10^{10}\ \mathrm{cm^{-3}}\))",
          pa, "V",
          X(r"\[\varphi_{bi,A} = 0.026\ln\frac{10^{18}\cdot10^{14}}{10^{20}} = 0.026\ln(10^{12}) \approx " + g(pa, 3) + r"\ \mathrm{V}\]",
            r"Gotcha: exactly the same as junction B. Only the PRODUCT \(N_AN_D\) matters. A very lopsided junction isn't automatically 'stronger'. (Their depletion widths do differ a lot.)"))
    s.mc(r"Which statement about contact potentials is correct?",
         "Every junction of dissimilar materials (P–N, metal–semiconductor, even metal–metal) has a contact potential, and in equilibrium they sum to zero around any closed loop",
         ["Only PN junctions have contact potentials; metals are equipotential", "An ohmic contact has no contact potential", "Contact potentials add up around a loop, which is how thermocouples work at a single temperature"],
         X(r"Reader Sec. 5.4.7: 'the contact between two dissimilar metals creates a potential difference' (set by the work-function difference). An 'ohmic' contact still has a contact potential; it is engineered not to RECTIFY (not to act like a diode).",
           r"Gotcha: thermocouples need two DIFFERENT temperatures. At a single temperature (equilibrium) the potentials around a loop always cancel."))
    s.round(4)
    pbm = 0.55 + kTq * math.log(5e16 / ni)
    s.num(r"Preview of the MOS capacitor: a heavily doped n⁺ polysilicon gate sits at about \(+550\ \mathrm{mV}\) relative to intrinsic silicon. It is placed over a p-type body with \(N_A = 5\times10^{16}\ \mathrm{cm^{-3}}\). What is the built-in potential between gate and body, \(\varphi_{gate} - \varphi_p\)? (\(kT/q = 26\ \mathrm{mV}\))",
          pbm, "V",
          X(r"\[\varphi_p = -0.026\ln\frac{5\times10^{16}}{10^{10}} = -0.026\times15.42 = -" + g(-(kTq * -math.log(5e16 / ni)), 3) + r"\ \mathrm{V}\]",
            r"\[\varphi_{bi} = 0.55 - (" + g(-kTq * math.log(5e16 / ni), 3) + r") \approx " + g(pbm, 3) + r"\ \mathrm{V}\]",
            r"This matches the reader's MOS example (about 0.95 V). Even with the gate shorted to the body, this potential appears across the oxide and the body surface. The MOS-structure skill picks it up from here."),
          preview=["mos-struct"])
    VR = 2.0
    s.num(r"Preview of reverse bias: a junction with \(N_A = N_D = 10^{17}\ \mathrm{cm^{-3}}\) (\(\varphi_{bi} = " + g(pb, 3) + r"\ \mathrm{V}\)) has 2 V applied with the N side positive. The contact potentials still cancel each other, so the applied voltage appears across the junction itself. What is the total potential step across the depletion region?",
          pb + VR, "V",
          X(r"KVL: applied voltage plus built-in potential, \(\varphi_{bi} + V_R = " + g(pb, 3) + r" + 2 = " + g(pb + VR, 3) + r"\ \mathrm{V}\).",
            r"No current flows (apart from a tiny leakage), so no voltage drops in the neutral regions or contacts. The depletion region must widen to hold the larger step. That's the reverse-bias skill."),
          preview=["rev-bias"])
    s.mc(r"Preview of the MOS structure: an n⁺-poly gate is shorted to a p-type body by a wire. The oxide is an insulator, so no DC current can flow. Is there an electric field in the oxide?",
         "Yes: the gate–body built-in potential (about 1 V) has to appear somewhere in the loop, and it sits across the oxide and the depleted body surface",
         ["No: shorting the terminals sets the gate and body at the same potential everywhere", "No, because an insulator can't hold a field", "Only if a voltage source is added"],
         X(r"Going around the loop (gate → wire → body contact → body → oxide → gate), the contact potentials of the wire connections and the drops inside the device must sum to zero. The gate and body are different materials with a built-in difference, so a potential drop (and field) ends up across the oxide plus a depleted layer in the body (reader Sec. 7.2.2–7.2.3).",
           r"So a MOS capacitor holds charge even at zero applied bias, a key starting point for the MOS skills."),
         figure=FG.mos_stack("neutral"), alt="MOS capacitor at zero bias: positive charge on the n+ poly gate, a thin oxide, and a shallow depletion region with negative ions at the top of the p-type body.",
         preview=["mos-struct"])
    return s

def rev_bias():
    s = Skill('rev-bias')
    s.round(1)
    s.mc(r"A PN junction is reverse biased (\(V_D < 0\): the N side is made more positive than the P side). What happens to the depletion region?",
         "It widens on both sides, uncovering more ion charge to support the larger potential step φbi − V_D",
         ["It shrinks, because the applied voltage cancels part of φbi", "It stays the same width; only the current changes", "It moves entirely into the P side"],
         X(r"The total step across the junction becomes \(\varphi_{bi} - V_D > \varphi_{bi}\). With no significant current, the only way to support more potential is more charge, which means wider depletion (reader Eq. 5.52–5.55):",
           r"\[X_d(V_D) = X_{d0}\sqrt{1 - \frac{V_D}{\varphi_{bi}}}\]",
           r"Forward bias (\(V_D > 0\)) would shrink it."),
         figure=FG.pn_profiles(NA=1, ND=1, show=("rho", "E"), bias=1.6), alt="Charge density and field for a reverse-biased junction: wider negative and positive charge blocks than at zero bias, and a larger triangular field.")
    Xd0, pb = 0.4, 0.8
    Xd = Xd0 * math.sqrt(1 + 5 / pb)
    s.num(r"A junction has \(X_{d0} = 0.40\ \mu\mathrm{m}\) at zero bias and \(\varphi_{bi} = 0.80\ \mathrm{V}\). What is the depletion width at a reverse bias of 5 V (\(V_D = -5\ \mathrm{V}\))?",
          Xd, "µm",
          X(r"\[X_d = X_{d0}\sqrt{1 - \frac{V_D}{\varphi_{bi}}} = 0.40\sqrt{1 + \frac{5}{0.8}} = 0.40\sqrt{7.25} \approx " + g(Xd, 3) + r"\ \mu\mathrm{m}\]",
            r"Common mistake: using \(1 + V_D/\varphi_{bi}\) with \(V_D = -5\), which gives the square root of a negative number. In the reader's sign convention, reverse bias makes \(V_D\) negative and \(-V_D/\varphi_{bi}\) positive."))
    s.mc(r"A reverse-biased junction carries almost no current. Which statement explains why?",
         "The taller barrier shuts off diffusion exponentially; only the tiny drift of thermally generated minority carriers remains",
         ["The depletion region contains no carriers at all, so it is a perfect insulator", "The applied voltage drops entirely across the metal contacts", "Electrons and holes recombine at the junction before crossing"],
         X(r"Majority carriers now face a barrier of \(\varphi_{bi} + V_R\), and the number able to climb it drops as \(e^{-V_R/V_{th}}\). Minority carriers that wander into the field are still swept across, giving a small, bias-independent saturation current (reader Sec. 6.2.2; footnote 3 of Ch. 5).",
           r"The depletion region isn't a PERFECT insulator, or there'd be no leakage at all."))
    s.round(2)
    NA, ND, VR = 1e16, 1e18, 3.0
    pb2 = phibi(NA, ND)
    xp, xn = widths(NA, ND, pb2 + VR)
    Q = q * NA * xp
    s.num(r"A junction has \(N_A = 10^{16}\) (P side) and \(N_D = 10^{18}\ \mathrm{cm^{-3}}\) (N side), so \(\varphi_{bi} = " + g(pb2, 4) + r"\ \mathrm{V}\). At a reverse bias of 3 V, what is the magnitude of the depletion charge per unit area on each side, \(|Q_j| = qN_Ax_p\), in nC/cm²? (\(\varepsilon_s = 1.036\times10^{-12}\ \mathrm{F/cm}\))",
          Q * 1e9, "nC/cm²",
          X(r"\[x_p = \sqrt{\frac{2\varepsilon_s(\varphi_{bi}+V_R)}{qN_A}\cdot\frac{N_D}{N_A+N_D}} = \sqrt{\frac{2(1.036\times10^{-12})(" + g(pb2 + VR, 4) + r")}{(1.602\times10^{-19})(10^{16})}\cdot\frac{10^{18}}{1.01\times10^{18}}} = " + sci(xp, 3) + r"\ \mathrm{cm}\]",
            r"\[|Q_j| = qN_Ax_p = (1.602\times10^{-19})(10^{16})(" + sci(xp, 3) + r") = " + sci(Q, 3) + r"\ \mathrm{C/cm^2} \approx " + g(Q * 1e9, 3) + r"\ \mathrm{nC/cm^2}\]",
            r"Equal and opposite charge \(qN_Dx_n\) sits on the N side. Common mistake: using \(\varphi_{bi}\) alone (the zero-bias charge) instead of \(\varphi_{bi} + V_R\)."))
    Emax = q * NA * xp / eps_s
    s.num(r"Same junction and bias (\(N_A = 10^{16}\ \mathrm{cm^{-3}}\), \(x_p = " + g(xp * 1e4, 3) + r"\ \mu\mathrm{m}\) at 3 V reverse). What is the peak field magnitude in kV/cm?",
          Emax / 1e3, "kV/cm",
          X(r"\[|E_{max}| = \frac{qN_Ax_p}{\varepsilon_s} = \frac{|Q_j|}{\varepsilon_s} = \frac{" + sci(Q, 3) + r"}{1.036\times10^{-12}} \approx " + sci(Emax, 3) + r"\ \mathrm{V/cm}\]",
            r"That is about " + g(Emax / 1e3, 3) + r" kV/cm. This is Gauss's law: the field at the junction equals the charge on one side divided by \(\varepsilon_s\). The peak field grows like \(\sqrt{V_R}\). If it reaches roughly \(3\times10^{5}\) V/cm, the junction breaks down."))
    pb3 = phibi(1e16, 1e16)
    s.num(r"A symmetric junction (\(N_A = N_D = 10^{16}\ \mathrm{cm^{-3}}\), \(\varphi_{bi} = " + g(pb3, 3) + r"\ \mathrm{V}\)) is reverse biased. What reverse voltage \(V_R\) makes the depletion width exactly TWICE its zero-bias value?",
          3 * pb3, "V",
          X(r"\(X_d \propto \sqrt{\varphi_{bi} + V_R}\). Doubling the width needs four times the total potential:",
            r"\[\varphi_{bi} + V_R = 4\varphi_{bi} \Rightarrow V_R = 3\varphi_{bi} \approx " + g(3 * pb3, 3) + r"\ \mathrm{V}\]",
            r"Common mistake: \(V_R = \varphi_{bi}\) (that only multiplies the width by \(\sqrt2\)), or \(V_R = 4\varphi_{bi}\) (forgetting that \(\varphi_{bi}\) is already there)."))
    s.round(3)
    s.mc(r"A junction with \(\varphi_{bi} = 0.8\ \mathrm{V}\) is FORWARD biased at \(V_D = +0.4\ \mathrm{V}\). Using the same depletion-width formula, what happens to the width?",
         r"It shrinks to \(\sqrt{0.5} \approx 0.71\) of its zero-bias value",
         [r"It grows to \(\sqrt{1.5} \approx 1.22\) of its zero-bias value", r"It shrinks to half its zero-bias value", "It is unchanged, since forward bias only affects the current"],
         X(r"\[\frac{X_d}{X_{d0}} = \sqrt{1 - \frac{V_D}{\varphi_{bi}}} = \sqrt{1 - \frac{0.4}{0.8}} = \sqrt{0.5} = 0.707\]",
           r"Gotcha: the sign convention. Forward bias (\(V_D > 0\)) LOWERS the step to \(\varphi_{bi} - V_D\). The width is a square root, so half the voltage gives 71%, not 50%. (Under strong forward bias the depletion approximation itself becomes shaky, because the carriers are no longer negligible.)"))
    r = math.sqrt((0.8 + 4) / (0.8 + 1))
    s.num(r"A junction (\(\varphi_{bi} = 0.8\ \mathrm{V}\)) is reverse biased first at 1 V, then at 4 V. By what factor does the stored depletion charge \(|Q_j|\) increase?",
          r, "(factor)",
          X(r"\(Q_j = qN_Ax_p \propto \sqrt{\varphi_{bi} + V_R}\) (reader Eq. 5.56):",
            r"\[\frac{Q(4\ \mathrm{V})}{Q(1\ \mathrm{V})} = \sqrt{\frac{4.8}{1.8}} \approx " + g(r, 3) + r"\]",
            r"Gotcha: four times the voltage gives only about 1.6 times the charge. \(Q\) is NOT proportional to \(V\), so this is a nonlinear capacitor. You can't use \(Q = CV\) with a single \(C\)."))
    s.mc(r"A P⁺N junction (\(N_A = 10^{19}\), \(N_D = 10^{15}\ \mathrm{cm^{-3}}\)) is reverse biased more and more. Where does the additional depletion width come from?",
         "Almost entirely from the lightly doped N side; the P⁺ side barely changes",
         ["Equally from both sides", "Mostly from the P⁺ side, since it holds more charge", "From neither; only the field increases"],
         X(r"Both \(x_n\) and \(x_p\) scale as \(\sqrt{\varphi_{bi}+V_R}\), with \(x_n/x_p = N_A/N_D = 10^{4}\). So any growth is \(10^{4}\) times larger on the N side.",
           r"Gotcha: equal CHARGE growth on both sides doesn't mean equal WIDTH growth. For a one-sided junction you can treat it as \(X_d \approx \sqrt{2\varepsilon_s(\varphi_{bi}+V_R)/(qN_D)}\)."),
         figure=FG.pn_profiles(NA=50, ND=1, show=("rho",), bias=1.4), alt="Charge density of a P+N junction under reverse bias: a thin, tall negative sheet on the P+ side and a wide, short positive block extending far into the N side.")
    s.round(4)
    NA4, ND4, VR4 = 1e19, 1e16, 2.0
    pb4 = phibi(NA4, ND4)
    xp4, xn4 = widths(NA4, ND4, pb4 + VR4)
    Cj = eps_s / (xp4 + xn4)
    s.num(r"Preview of depletion capacitance: a later skill shows that the small-signal capacitance of a reverse-biased junction is \(C_j = \varepsilon_s/X_d\) per unit area. For a P⁺N junction with \(N_A = 10^{19}\), \(N_D = 10^{16}\ \mathrm{cm^{-3}}\) (\(\varphi_{bi} = " + g(pb4, 3) + r"\ \mathrm{V}\)) at \(V_R = 2\ \mathrm{V}\), find \(C_j\) in fF/µm².",
          Cj * 1e7, "fF/µm²",
          X(r"\[X_d = \sqrt{\frac{2\varepsilon_s(\varphi_{bi}+V_R)}{q}\left(\frac{1}{N_A}+\frac{1}{N_D}\right)} = " + sci(xp4 + xn4, 3) + r"\ \mathrm{cm}\]",
            r"\[C_j = \frac{1.036\times10^{-12}}{" + sci(xp4 + xn4, 3) + r"} = " + sci(Cj, 3) + r"\ \mathrm{F/cm^2} \approx " + g(Cj * 1e7, 3) + r"\ \mathrm{fF/\mu m^2}\]",
            r"Why \(\varepsilon_s/X_d\)? A small voltage change adds or removes charge only at the two EDGES of the depletion region, which act like capacitor plates \(X_d\) apart."),
          preview=["junction-cap"])
    rat = math.sqrt((0.8 + 5) / 0.8)
    s.num(r"Preview of the varactor: a junction's small-signal capacitance goes as \(C_j \propto 1/X_d \propto 1/\sqrt{\varphi_{bi}+V_R}\). With \(\varphi_{bi} = 0.8\ \mathrm{V}\), what is the capacitance ratio \(C_j(0\ \mathrm{V})/C_j(5\ \mathrm{V\ reverse})\)?",
          rat, "(ratio)",
          X(r"\[\frac{C_j(0)}{C_j(5)} = \sqrt{\frac{0.8+5}{0.8}} = \sqrt{7.25} \approx " + g(rat, 3) + r"\]",
            r"A tuning range of about 2.7 to 1 from a DC control voltage. Radios use this to tune an LC oscillator, since \(f \propto 1/\sqrt{C}\) (reader Sec. 5.5.5)."),
          preview=["junction-cap", "diode-ss"])
    s.mc(r"Preview of transistor parasitics: a MOSFET's n⁺ source and drain regions sit inside a p-type body that is tied to the lowest voltage in the circuit, so those junctions are always reverse biased. What does this mean for the circuit?",
         "Each source/drain junction behaves as a voltage-dependent capacitor to the body; more reverse bias widens the depletion region and lowers that capacitance",
         ["The junctions conduct large currents into the body", "The junctions disappear because they are reverse biased", "They add capacitance that grows with more reverse bias"],
         X(r"A reverse-biased junction stores depletion charge that varies with voltage, so it is a nonlinear capacitor (\(C \propto 1/\sqrt{\varphi_{bi}+V_R}\)). These parasitic capacitances (\(C_{DB}\), \(C_{SB}\)) slow down circuits.",
           r"Keeping the body at the lowest voltage guarantees reverse bias, which isolates the devices from each other (reader Sec. 6.2.5) while leaving these capacitors behind."),
         preview=["mos-caps", "junction-cap"])
    return s
