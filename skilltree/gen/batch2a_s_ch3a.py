"""batch2a: si-props, drude, intrinsic, doping"""
from batch2a_lib import *
import batch2a_fig as FG
import math

def X(*lines): return "\n".join(lines)
me = 9.109e-31
kB = 8.617e-5  # eV/K

def lat_alt(kind):
    return {None: "A 4 by 3 grid of silicon atoms, each joined to its four neighbours by covalent bonds (two electrons per bond).",
            "broken": "Silicon bond lattice with one broken bond: a free electron (filled dot) has left, leaving an empty bond site, the hole (open circle).",
            "donor": "Silicon lattice in which one atom is replaced by phosphorus (P). A loosely bound fifth electron is shown free in the crystal; the P site is a fixed positive ion.",
            "acceptor": "Silicon lattice in which one atom is replaced by boron (B). One bond next to B is missing an electron: a mobile hole; the B site is a fixed negative ion."}[kind]

def si_props():
    s = Skill('si-props')
    s.round(1)
    s.mc(r"Silicon is a group IV element. In the silicon crystal (shown in the 2D bond model), how many valence electrons does each atom have, and how many covalent bonds does it form?",
         "4 valence electrons; 4 bonds, one to each nearest neighbour",
         ["4 valence electrons; 8 bonds, one per electron it shares or borrows", "2 valence electrons (the 3p²); 2 bonds", "14 electrons, all of which take part in bonding"],
         X(r"Silicon's outer shell holds 4 electrons (\(3s^2 3p^2\), which hybridize into 4 \(sp^3\) orbitals in the crystal). Each atom bonds to 4 neighbours in the diamond lattice, and each bond holds 2 electrons: one contributed by each atom (reader Sec. 3.3.2, 3.3.6).",
           r"• 8 bonds double-counts: each atom 'sees' 8 electrons around it (4 own + 4 shared), but that is still 4 bonds.",
           r"• Only the two 3p electrons bonding would not fill the shell; the hybridized state uses all four.",
           r"• The 10 core electrons are tightly bound and never take part in bonding or conduction."),
         figure=FG.lattice(), alt=lat_alt(None))
    s.mc(r"Pure (undoped) silicon is cooled to \(T = 0\ \mathrm{K}\). How well does it conduct, and why?",
         "Essentially not at all: every valence electron is locked in a covalent bond, so there are no free carriers",
         ["Very well: each atom has 4 free valence electrons", "Moderately: holes conduct even when no bonds are broken", "Perfectly: lattice vibrations stop, so there is no scattering"],
         X(r"At 0 K no bond is broken. The valence band is completely full and the conduction band is empty, so nothing can carry a net current: silicon is an insulator (reader Sec. 3.3.6).",
           r"• The 4 valence electrons are the bonding electrons, not free ones (that picture fits a metal's 'electron gas').",
           r"• A hole only exists once a bond has been broken.",
           r"• Having no scattering doesn't help if there are no carriers to move."))
    s.mc(r"At room temperature a lattice vibration breaks one Si–Si bond (see figure). What does that create?",
         "One free electron and one hole: an electron–hole pair",
         ["One free electron only; the lattice stays neutral", "Two free electrons, one from each atom of the bond", "One hole only; the electron stays bound to its atom"],
         X(r"The freed electron leaves behind an empty bond site that has net charge \(+q\). A neighbouring bonding electron can hop into it, so the vacancy moves through the crystal like a free positive particle: the hole (Sec. 3.3.7–3.3.8).",
           r"Thermal generation always makes carriers in pairs. That is why pure silicon has \(n = p\)."),
         figure=FG.lattice(broken=True), alt=lat_alt("broken"))
    s.round(2)
    Eg, kt = 1.12, 0.026
    s.num(r"Silicon's band gap is \(E_g = 1.12\ \mathrm{eV}\). At 300 K the thermal energy is \(kT \approx 26\ \mathrm{meV}\). How many times larger than \(kT\) is the gap? (Give \(E_g/kT\).)",
          Eg / kt, "(unitless)",
          X(r"\[\frac{E_g}{kT} = \frac{1.12\ \mathrm{eV}}{0.026\ \mathrm{eV}} \approx " + g(Eg / kt, 3) + r"\]",
            r"An average carrier has far too little energy to cross the gap. Only the rare carriers in the high-energy tail of the thermal distribution make it. That is why silicon has so few free carriers, and why their number depends so strongly (exponentially) on temperature (reader Sec. 3.3.4)."),
          figure=FG.band_diagram("intrinsic", gap="E_g = 1.12 eV"), alt="Band diagram: conduction band edge Ec on top, valence band edge Ev at bottom, separated by the gap Eg = 1.12 eV, with the intrinsic level Ei dashed at mid-gap.")
    s.mc(r"The reader quotes these conductivities: copper 6.4×10⁷ S/m at 273 K and 4.46×10⁶ S/m at 373 K; germanium 0.5 S/m at 273 K and 833 S/m at 500 K. Which explanation of the opposite temperature trends is right?",
         "In Ge, heating breaks exponentially more bonds, so the carrier count soars; in Cu the carrier count is fixed and more lattice vibration (scattering) lowers the conductivity",
         ["In both, heating increases scattering, but Ge has more room for its electrons to speed up", "Cu loses free electrons as it is heated, while Ge gains mobility",
          "Ge's band gap closes completely above room temperature, turning it into a metal"],
         X(r"Conductivity is \(\sigma = q(n\mu_n + p\mu_p)\).",
           r"• Semiconductor: \(n\) and \(p\) come from thermally broken bonds, \(\propto e^{-E_g/2kT}\). That grows by orders of magnitude, so it swamps the mild drop in mobility.",
           r"• Metal: every atom already gives up an electron, so \(n\) is fixed. Heating only adds lattice vibrations (phonons), which shorten the time between collisions and lower \(\mu\).",
           r"The gap doesn't close; it shrinks only slightly with temperature."))
    Nat = 5e22
    s.num(r"Silicon has about \(5\times10^{22}\) atoms per cm³, and at 300 K the free-electron concentration of pure Si is \(n_i = 10^{10}\ \mathrm{cm^{-3}}\). Each free electron corresponds to one broken bond. What fraction of the atoms have lost an electron (free electrons per atom)? Scientific notation is fine.",
          ni / Nat, "(fraction)",
          X(r"\[\frac{n_i}{N_{Si}} = \frac{10^{10}}{5\times10^{22}} = 2\times10^{-13}\]",
            r"Only about one atom in 5 trillion contributes a free electron at room temperature. Compare a metal, where every atom contributes about one. This is why intrinsic silicon is such a poor conductor."))
    s.round(3)
    s.mc(r"A band is completely filled with electrons. The electrons are still moving around inside their bonds. What net current can that band carry when a field is applied?",
         "Zero: for a completely filled band, the velocities of all electrons sum to zero",
         ["A large current, since it holds the most electrons", "A current proportional to the number of electrons, but flowing opposite to the field", "Zero at 0 K only; at room temperature its electrons carry current"],
         X(r"Reader Eq. 3.19: \(\sum_{\text{filled band}} (-q)\,v_i = 0\). In a full band, every state with velocity \(+v\) is paired with a filled state at \(-v\), so the field cannot change the occupation pattern.",
           r"Current only appears when the band is partly empty. Writing the partly filled band as 'full band minus missing electrons' gives \(J_{vb} = \sum_{\text{empty}} q\,v_i\) (Eq. 3.21): positive carriers, the holes.",
           r"Temperature doesn't change this: a band that stays completely full still gives zero."))
    s.mc(r"In the bond model, a hole drifts to the RIGHT across the crystal. What are the actual electrons doing, and which way does the conventional current flow?",
         "Bonding electrons hop one by one to the LEFT into the vacancy; the current flows to the RIGHT",
         ["Bonding electrons hop to the RIGHT along with the hole; the current flows to the LEFT", "A positive ion core moves to the right; the current flows to the right",
          "Free conduction-band electrons move left; the current flows to the left"],
         X(r"Each time a neighbouring valence electron jumps into the empty bond, the vacancy moves one site the opposite way. A hole moving right means a chain of valence electrons, each moving left (reader Fig. 3.11).",
           r"Negative charge moving left is the same current as positive charge moving right, so the current points right, along the hole's motion. The ion cores never move, and the hole lives in the valence band, not the conduction band."),
         figure=FG.lattice(broken=True), alt=lat_alt("broken"))
    lam = 1.24 / Eg
    s.num(r"Light can break a Si–Si bond if one photon carries at least the band-gap energy \(E_g = 1.12\ \mathrm{eV}\). Using \(E_{photon} = 1.24/\lambda\) (eV, with \(\lambda\) in µm), what is the LONGEST wavelength that can still create electron–hole pairs in silicon?",
          lam, "µm",
          X(r"\[\lambda_{max} = \frac{1.24}{E_g} = \frac{1.24}{1.12} \approx " + g(lam, 4) + r"\ \mu\mathrm{m}\]",
            r"Gotcha: a longer wavelength means LESS energy per photon. Photons longer than about 1.1 µm (such as the 1.3 µm and 1.55 µm telecom bands) pass straight through silicon, which is why fibre-optic detectors use other materials. Shorter wavelengths all work; the extra energy above \(E_g\) is lost as heat."),
          figure=FG.band_diagram("intrinsic", gap="E_g"), alt="Band diagram with conduction band edge Ec above valence band edge Ev, separated by the band gap Eg; a photon must supply at least Eg to lift an electron across.")
    s.round(4)
    r = math.exp((1.12 - 0.66) / (2 * 0.026))
    s.num(r"Preview of intrinsic carrier concentration: a later skill shows that the number of thermally broken bonds scales roughly as \(n_i \propto e^{-E_g/2kT}\). Germanium has \(E_g = 0.66\ \mathrm{eV}\) and silicon \(1.12\ \mathrm{eV}\). Ignoring every other difference between the two, estimate \(n_{i,Ge}/n_{i,Si}\) at 300 K (\(kT = 0.026\ \mathrm{eV}\)).",
          r, "(ratio)",
          X(r"\[\frac{n_{i,Ge}}{n_{i,Si}} = \exp\!\left(\frac{E_{g,Si}-E_{g,Ge}}{2kT}\right) = \exp\!\left(\frac{0.46}{0.052}\right) = e^{8.85} \approx " + g(r, 3) + r"\]",
            r"A gap only 0.46 eV smaller gives thousands of times more free carriers. That exponential sensitivity is why the reader's germanium conducts so much better than silicon, and why it is so temperature sensitive. (The measured ratio is about 2×10³ because the prefactors differ; the exponential dominates.)"),
          preview=["intrinsic"])
    s.mc(r"Preview of doping: one silicon atom is replaced by phosphorus, a group V element with 5 valence electrons (see figure). In the bond model, what happens?",
         "Four of P's electrons form the four bonds; the fifth is barely bound and is easily freed, leaving a fixed positive P⁺ ion",
         ["P forms five bonds, so no free carriers appear", "P takes an electron from a neighbour, creating a hole", "The fifth electron stays bound at room temperature, so nothing changes"],
         X(r"Only four bonds are available in the diamond lattice. The fifth electron isn't needed for bonding, so at room temperature it is essentially always free. The P atom left behind is a positive ion that cannot move.",
           r"This is the idea behind doping: an impurity that donates a free electron without creating a hole (reader Sec. 3.5.1). A group III atom (boron) does the opposite."),
         figure=FG.lattice("donor"), alt=lat_alt("donor"), preview=["doping"])
    s.mc(r"Preview of doping: one silicon atom is replaced by boron, a group III element with only 3 valence electrons. What does the bond model predict?",
         "B grabs an electron from a neighbouring bond to complete its four bonds, creating a mobile hole and a fixed negative B⁻ ion",
         ["B releases a free electron, leaving a positive ion", "B forms only three bonds and the crystal stays neutral with no carriers", "B creates an electron–hole pair, like a broken bond"],
         X(r"With only three electrons, one of B's four bonds is incomplete. An electron from a nearby Si–Si bond fills it. That vacancy moves away as a free hole, and the boron becomes a fixed negative ion (reader Sec. 3.5.3).",
           r"Unlike a thermally broken bond, no free electron is created, so the material gains holes only (p-type). Group III dopants are 'acceptors'; group V dopants are 'donors'."),
         figure=FG.lattice("acceptor"), alt=lat_alt("acceptor"), preview=["doping"])
    return s

def drude():
    s = Skill('drude')
    s.round(1)
    tpts = []
    t = 0.0
    for k, tau in enumerate([1.0, 0.6, 1.3, 0.8, 1.1, 0.7, 1.0]):
        tpts += [(t, 0.0), (t + tau, tau)]
        t += tau
    s.mc(r"In the gas (Drude) model of conduction, a steady electric field is applied to a metal. What happens to the AVERAGE velocity of the electrons?",
         r"It settles at a constant drift velocity proportional to the field, \(\bar u = \mu E\), because collisions keep resetting the momentum",
         [r"It grows linearly with time, \(\bar u = qEt/m\), as for a free particle", r"It stays zero, because collisions randomize every direction", r"It is proportional to \(E^2\), since the energy gained goes as \(E^2\)"],
         X(r"Between collisions each electron gains momentum \(qEt\), but every collision randomizes its velocity. Averaged over many carriers, the random parts cancel and the field part gives \(M\bar u = qE\tau\), so \(\bar u = (q\tau/M)E = \mu E\) (reader Eq. 3.10–3.12).",
           r"The figure shows the sawtooth: velocity builds, then resets at each collision, so the average is constant. That proportionality of current to field is Ohm's law."),
         figure=FG.plot([dict(pts=tpts)], (0, t + 0.2), (0, 1.6), "t", "velocity gained along E", hlines=[(0.5, "average = μE")], label="Sawtooth velocity versus time"),
         alt="Velocity gained along the field versus time: it ramps up linearly, drops to zero at each random collision, and ramps again, giving a sawtooth whose average is a constant dashed line labelled average = μE.")
    v = 1000 * 100
    s.num(r"Electrons in a silicon bar have mobility \(\mu_n = 1000\ \mathrm{cm^2/(V\cdot s)}\). The field is \(E = 100\ \mathrm{V/cm}\). What is the drift speed?",
          v, "cm/s",
          X(r"\[v_{dr} = \mu_n E = 1000 \times 100 = 10^5\ \mathrm{cm/s}\]",
            r"That is 1 km/s, still 100 times slower than the random thermal speed (about \(10^7\) cm/s), so the drift is a small bias on top of very fast random motion."),
          figure=FG.bar(vlabel="E = 100 V/cm", elabel="E"), alt="A semiconductor bar with a voltage applied, positive on the left. An arrow labelled E points right inside the bar and a dashed arrow shows electrons drifting left.")
    s.mc(r"Mobility is defined by \(v_{dr} = \mu E\). What are its usual units in device work?",
         r"\(\mathrm{cm^2/(V\cdot s)}\)",
         [r"\(\mathrm{cm/s}\)", r"\(\mathrm{V\cdot s/cm^2}\)", r"\(\mathrm{S/cm}\)"],
         X(r"\[\mu = \frac{v}{E} = \frac{\mathrm{cm/s}}{\mathrm{V/cm}} = \frac{\mathrm{cm^2}}{\mathrm{V\cdot s}}\]",
           r"cm/s is a velocity, V·s/cm² is the inverse, and S/cm is conductivity, \(\sigma = qn\mu\)."))
    s.round(2)
    tau, mstar = 1e-13, 0.26 * me
    mu = q * tau / mstar * 1e4
    s.num(r"Electrons in silicon have an effective mass \(m^* = 0.26\,m_0\) (\(m_0 = 9.11\times10^{-31}\) kg) and a mean free time between collisions of \(\tau = 10^{-13}\) s. Using \(\mu = q\tau/m^*\), what is the mobility in \(\mathrm{cm^2/(V\cdot s)}\)?",
          mu, "cm²/(V·s)",
          X(r"Work in SI units, then convert:",
            r"\[\mu = \frac{q\tau}{m^*} = \frac{(1.602\times10^{-19})(10^{-13})}{0.26 \times 9.11\times10^{-31}} = " + g(mu / 1e4, 3) + r"\ \mathrm{m^2/(V\cdot s)}\]",
            r"\[1\ \mathrm{m^2} = 10^4\ \mathrm{cm^2} \Rightarrow \mu \approx " + g(mu, 3) + r"\ \mathrm{cm^2/(V\cdot s)}\]",
            r"That's the right order of magnitude for electrons in lightly doped silicon. Common mistake: forgetting the \(10^4\) conversion (answer 0.068)."))
    n, mu_cu = 8.5e22, 43
    sig = q * n * mu_cu
    rho_uohm = 1 / sig * 1e6
    s.num(r"Copper has about \(8.5\times10^{22}\) free electrons per cm³ and an electron mobility of about \(43\ \mathrm{cm^2/(V\cdot s)}\). Using \(\sigma = qn\mu\), what is its resistivity in µΩ·cm?",
          rho_uohm, "µΩ·cm",
          X(r"\[\sigma = qn\mu = (1.602\times10^{-19})(8.5\times10^{22})(43) = " + sci(sig, 3) + r"\ \mathrm{S/cm}\]",
            r"\[\rho = 1/\sigma = " + sci(1 / sig, 3) + r"\ \Omega\cdot\mathrm{cm} \approx " + g(rho_uohm, 3) + r"\ \mu\Omega\cdot\mathrm{cm}\]",
            r"That matches the handbook value for copper (1.7 µΩ·cm). Its mobility is LOWER than silicon's; copper conducts well because \(n\) is enormous, not because \(\mu\) is large."))
    rho, L, W, t = 2.7e-6, 0.1, 1e-4, 0.5e-4
    R = rho * L / (W * t)
    s.num(r"An aluminium interconnect on a chip has resistivity \(\rho = 2.7\ \mu\Omega\cdot\mathrm{cm}\). It is 1 mm long, 1 µm wide and 0.5 µm thick. What is its resistance?",
          R, "Ω",
          X(r"Convert everything to cm: \(L = 0.1\) cm, \(A = (10^{-4})(0.5\times10^{-4}) = 5\times10^{-9}\ \mathrm{cm^2}\).",
            r"\[R = \rho\frac{L}{A} = 2.7\times10^{-6}\cdot\frac{0.1}{5\times10^{-9}} = " + g(R, 3) + r"\ \Omega\]",
            r"Tens of ohms is significant on a chip, which is why long wires need care. Common mistake: mixing µm and cm (off by factors of \(10^4\))."),
          figure=FG.bar(llabel="L = 1 mm", acap="1 µm × 0.5 µm", vlabel="", carriers=None, elabel=""), alt="A rectangular bar of length L = 1 mm with cross-section 1 µm by 0.5 µm.")
    s.round(3)
    I, A = 1.0, 0.01
    v = I / A / (n * q)
    s.num(r"A copper wire with a 1 mm² cross-section carries 1 A. Copper has \(n = 8.5\times10^{22}\ \mathrm{cm^{-3}}\) free electrons. What is the electrons' average DRIFT speed in µm/s?",
          v * 1e4, "µm/s",
          X(r"\(J = I/A = 1\ \mathrm{A} / 0.01\ \mathrm{cm^2} = 100\ \mathrm{A/cm^2}\), and \(J = qnv\):",
            r"\[v = \frac{J}{qn} = \frac{100}{(1.602\times10^{-19})(8.5\times10^{22})} = " + sci(v, 3) + r"\ \mathrm{cm/s} \approx " + g(v * 1e4, 3) + r"\ \mu\mathrm{m/s}\]",
            r"Gotcha: the electrons crawl at less than 0.1 mm/s, while their random thermal speed is about \(10^{7}\) cm/s. The signal travels fast because the field, not the electrons, propagates down the wire. Common mistake: forgetting to convert mm² to cm² (\(1\ \mathrm{mm^2} = 0.01\ \mathrm{cm^2}\))."))
    s.mc(r"A field points in the \(+x\) direction in a conductor whose carriers are electrons, so the electrons drift toward \(-x\). In which direction does the current density \(J\) point?",
         r"\(+x\), along the field: negative charge moving in \(-x\) is a current in \(+x\)",
         [r"\(-x\), the direction the electrons move", r"There is no net current, because the electrons' random velocities cancel", r"\(+x\) only if holes are also present"],
         X(r"\(J = (-q)\,n\,v\) with \(v = -\mu_n E\) gives \(J = qn\mu_n E\), which is parallel to \(E\). The reader's sign bookkeeping (Eq. 3.14–3.15) shows positive and negative carriers both add to the conductivity: \(\sigma = q^2(N^+\tau^+/M^+ + N^-\tau^-/M^-)\).",
           r"Random thermal velocities do cancel; the drift velocity does not."),
         figure=FG.bar(vlabel="E along +x", elabel="E (+x)", carriers="e"), alt="A bar with the field E pointing right (+x) and a dashed arrow showing electrons drifting left (−x).")
    s.mc(r"Heating a metal wire raises its resistance (copper's conductivity drops about 30% from 273 K to 373 K). In the Drude picture, what causes this?",
         "Stronger lattice vibrations scatter electrons more often, shortening the mean free time τ and so lowering the mobility; the electron density barely changes",
         ["Heating frees fewer electrons, so n drops", "Faster thermal motion makes the electrons drift backwards", "Heat ionizes impurities, which add electrons that block conduction"],
         X(r"\(\sigma = nq^2\tau/m\). In a metal \(n\) is fixed (one electron per atom). Reader Sec. 3.2.7: electrons pass through a perfect periodic lattice unscattered; scattering comes from deviations from periodicity, namely thermal vibrations (phonons) and impurities.",
           r"More vibration means shorter \(\tau\), lower \(\mu\) and lower \(\sigma\). (In a semiconductor the opposite usually wins, because \(n\) rises exponentially with temperature.)"))
    s.round(4)
    sig_i = q * 1e10 * (1350 + 480)
    s.num(r"Preview of silicon's carriers: the gas model allows positive AND negative carriers, \(\sigma = q(n\mu_n + p\mu_p)\). Pure silicon at 300 K has \(n = p = 10^{10}\ \mathrm{cm^{-3}}\), \(\mu_n = 1350\) and \(\mu_p = 480\ \mathrm{cm^2/(V\cdot s)}\). What is its resistivity in kΩ·cm?",
          1 / sig_i / 1e3, "kΩ·cm",
          X(r"\[\sigma = q\,n_i(\mu_n+\mu_p) = (1.602\times10^{-19})(10^{10})(1830) = " + sci(sig_i, 3) + r"\ \mathrm{S/cm}\]",
            r"\[\rho = 1/\sigma \approx " + sci(1 / sig_i, 3) + r"\ \Omega\cdot\mathrm{cm} = " + g(1 / sig_i / 1e3, 3) + r"\ \mathrm{k}\Omega\cdot\mathrm{cm}\]",
            r"That is about \(10^{11}\) times copper's resistivity. Upcoming skills explain why silicon has so few carriers and how adding dopants makes it useful."),
          preview=["si-props", "drift"])
    rho_f, tf, LW = 1e-3, 0.5e-4, 10
    s.num(r"Preview of sheet resistance: a thin doped film has resistivity \(\rho = 10^{-3}\ \Omega\cdot\mathrm{cm}\) and thickness \(t = 0.5\ \mu\mathrm{m}\). A resistor drawn in it is 10 times longer than it is wide (\(L/W = 10\)). What is its resistance?",
          rho_f / tf * LW, "Ω",
          X(r"\[R = \rho\frac{L}{W t} = \frac{\rho}{t}\cdot\frac{L}{W} = \frac{10^{-3}}{0.5\times10^{-4}} \times 10 = 20\ \Omega \times 10 = 200\ \Omega\]",
            r"The width cancels except through the ratio \(L/W\). The combination \(\rho/t\) (here 20 Ω) depends only on the film, so an IC designer just counts 'squares' of length/width. That quantity is the sheet resistance, coming up next."),
          preview=["sheet-res"])
    s.mc(r"Preview of drift in silicon: electrons and holes have similar mean free times, but a hole's effective mass is larger than an electron's. With \(\mu = q\tau/m^*\), which carrier has the higher mobility, and what follows for transistors?",
         "Electrons; so for the same size and voltages, electron-based (n-type) devices conduct more current",
         ["Holes, because heavier particles keep their momentum longer", "They are equal, since mobility depends only on τ", "Holes, because they are positive and are pushed along the field"],
         X(r"\(\mu \propto 1/m^*\) at fixed \(\tau\), so lighter electrons are more mobile. The reader quotes typical silicon values of about \(\mu_n \approx 1000\) and \(\mu_p \approx 400\ \mathrm{cm^2/(V\cdot s)}\) ('electrons go faster as they are lighter').",
           r"Later you'll see that this is why an NMOS transistor carries more current than a PMOS of the same size. The sign of the charge decides the drift DIRECTION, not the speed."),
         preview=["drift"])
    return s

def intrinsic():
    s = Skill('intrinsic')
    s.round(1)
    s.mc(r"Pure (intrinsic) silicon is in thermal equilibrium at 300 K. How do the free-electron concentration \(n\) and hole concentration \(p\) compare?",
         r"\(n = p = n_i \approx 10^{10}\ \mathrm{cm^{-3}}\)",
         [r"\(n > p\), because electrons are lighter and break free more easily", r"\(n = 2n_i\) and \(p = 0\)", r"\(n = p = 5\times10^{22}\ \mathrm{cm^{-3}}\), one per atom"],
         X(r"Every thermally broken bond creates one electron AND one hole, and every recombination removes one of each, so \(n_0 = p_0\) (reader Sec. 3.4.1). Their common value is the intrinsic concentration, \(n_i \approx 10^{10}\ \mathrm{cm^{-3}}\) at 300 K (Eq. 3.27).",
           r"The electron's lighter mass affects mobility, not the count. One carrier per atom describes a metal."),
         figure=FG.band_diagram("intrinsic"), alt="Band diagram of intrinsic silicon: the Fermi level EF coincides with the dashed intrinsic level Ei at mid-gap.")
    s.num(r"For silicon at 300 K, \(n_i = 10^{10}\ \mathrm{cm^{-3}}\). What is the equilibrium product \(n\,p\)? Scientific notation is fine.",
          ni ** 2, "cm⁻⁶",
          X(r"The law of mass action: \(n\,p = n_i^2 = (10^{10})^2 = 10^{20}\ \mathrm{cm^{-6}}\) (reader Eq. 3.28).",
            r"This product is fixed by temperature and material alone. It holds in ANY silicon in thermal equilibrium, doped or not, which is what makes it so useful."))
    s.mc(r"'Thermal equilibrium' in a semiconductor means which of the following?",
         "Carriers are still constantly generated and recombining, but the two rates are exactly equal, so the concentrations don't change",
         ["No bonds break and no carriers recombine", "All carriers have recombined, so n = p = 0", "Generation is faster than recombination, but the extra carriers leave through the contacts"],
         X(r"Equilibrium is a dynamic balance: \(G_{th}(T) = R = k\,n\,p\) (reader Eq. 3.24–3.26). Bonds break and carriers annihilate all the time; on average the rates cancel. Setting them equal is exactly what gives \(np = G_{th}/k = n_i^2\)."))
    s.round(2)
    nx = 1e15
    s.num(r"In a piece of silicon at 300 K in thermal equilibrium, the electron concentration is known to be \(n = 10^{15}\ \mathrm{cm^{-3}}\). What is the hole concentration? (\(n_i = 10^{10}\ \mathrm{cm^{-3}}\))",
          ni ** 2 / nx, "cm⁻³",
          X(r"\[p = \frac{n_i^2}{n} = \frac{10^{20}}{10^{15}} = 10^{5}\ \mathrm{cm^{-3}}\]",
            r"Raising \(n\) by \(10^5\) above \(n_i\) lowers \(p\) by \(10^5\): with more electrons around, holes recombine faster until the product falls back to \(n_i^2\). Common mistake: assuming \(p\) stays at \(n_i\)."))
    ratio = math.exp(1.12 / (2 * kB) * (1 / 300 - 1 / 350))
    s.num(r"Using \(n_i \propto e^{-E_g/2kT}\) (ignore the weaker temperature dependence of the prefactor), with \(E_g = 1.12\ \mathrm{eV}\) and \(k = 8.617\times10^{-5}\ \mathrm{eV/K}\): by what factor does silicon's \(n_i\) grow when it is heated from 300 K to 350 K?",
          ratio, "(ratio)",
          X(r"\[\frac{n_i(350)}{n_i(300)} = \exp\!\left[\frac{E_g}{2k}\left(\frac{1}{300}-\frac{1}{350}\right)\right]\]",
            r"\[\frac{E_g}{2k} = \frac{1.12}{1.7234\times10^{-4}} = 6499\ \mathrm{K}, \quad \frac{1}{300}-\frac{1}{350} = 4.762\times10^{-4}\ \mathrm{K^{-1}}\]",
            r"\[\text{factor} = e^{3.095} \approx " + g(ratio, 3) + r"\]",
            r"A 50 K rise gives about 20 times more carriers. Common mistakes: forgetting the 2 in \(2kT\) (giving about 490) or using \(T\) in °C."))
    s.mc(r"Away from equilibrium, the recombination rate is modelled as \(R = k\,n\,p\). In a sample where both \(n\) and \(p\) are suddenly doubled, how does \(R\) change (at first)?",
         "It becomes 4 times larger",
         ["It doubles", "It does not change, because the generation rate is fixed", "It halves"],
         X(r"\(R' = k(2n)(2p) = 4\,knp = 4R\). Meanwhile thermal generation \(G_{th}(T)\) stays the same, so \(R > G\) and the excess carriers recombine until \(np\) falls back to \(n_i^2\).",
           r"This is the 'chance of meeting' picture: twice as many electrons, each finding twice as many holes."))
    s.round(3)
    s.mc(r"At 300 K, rank the intrinsic carrier concentrations of germanium (\(E_g = 0.66\) eV), silicon (1.12 eV) and gallium arsenide (1.42 eV).",
         r"\(n_{i,Ge} > n_{i,Si} > n_{i,GaAs}\)",
         [r"\(n_{i,GaAs} > n_{i,Si} > n_{i,Ge}\)", r"They are all equal at the same temperature", r"\(n_{i,Si} > n_{i,Ge} > n_{i,GaAs}\)"],
         X(r"\(n_i \propto e^{-E_g/2kT}\): a SMALLER gap gives exponentially MORE carriers. Each 0.1 eV of gap is a factor of \(e^{0.1/0.052} \approx 7\).",
           r"Gotcha: a wider gap does not mean 'more energy available'; it is a taller wall to jump. Equal temperature doesn't mean equal carriers; the gap matters exponentially. (Approximate values: Ge about \(2\times10^{13}\), Si \(10^{10}\), GaAs about \(2\times10^{6}\ \mathrm{cm^{-3}}\).)"))
    T2 = 1 / (1 / 300 - math.log(2) / (1.12 / (2 * kB)))
    s.num(r"With \(n_i \propto e^{-E_g/2kT}\), \(E_g = 1.12\ \mathrm{eV}\), \(k = 8.617\times10^{-5}\ \mathrm{eV/K}\): to what temperature must silicon be heated from 300 K to DOUBLE \(n_i\)? Give the answer in kelvin to the nearest 0.5 K.",
          T2, "K",
          X(r"Set \(\exp[\tfrac{E_g}{2k}(\tfrac{1}{300}-\tfrac{1}{T})] = 2\):",
            r"\[\frac{1}{T} = \frac{1}{300} - \frac{\ln 2}{E_g/2k} = 3.3333\times10^{-3} - \frac{0.6931}{6499} = 3.2267\times10^{-3}\ \mathrm{K^{-1}}\]",
            r"\[T \approx " + g(T2, 4) + r"\ \mathrm{K}\]",
            r"Gotcha: only about 10 K doubles the carrier count. You might expect 'double \(T\)' or a linear rule. This extreme sensitivity is exactly why circuits can't rely on intrinsic carriers."),
          tol=0.004)
    s.mc(r"Steady light shines on a piece of pure silicon, generating extra electron–hole pairs. In the steady state under illumination, how does \(np\) compare with \(n_i^2\)?",
         r"\(np > n_i^2\): the mass-action law holds only in thermal equilibrium, and the light adds generation",
         [r"\(np = n_i^2\) always, because the mass-action law is universal", r"\(np < n_i^2\), because recombination speeds up", r"\(n\) rises and \(p\) falls so that \(np\) stays equal to \(n_i^2\)"],
         X(r"\(np = n_i^2\) came from \(G_{th} = knp\). With light, \(G = G_{th} + G_{opt}\) (Eq. 3.22), so the steady state has \(knp = G_{th} + G_{opt}\), giving \(np > n_i^2\).",
           r"Gotcha: light makes PAIRS, so \(n\) and \(p\) both rise; nothing pushes either down. This non-equilibrium situation is the basis of solar cells and of forward-biased diodes."))
    s.round(4)
    rho300 = 1 / (q * ni * (1350 + 480))
    s.num(r"Preview of why we dope silicon: pure Si at 300 K has \(\rho \approx " + g(rho300 / 1e3, 3) + r"\ \mathrm{k}\Omega\cdot\mathrm{cm}\) (with \(\mu_n + \mu_p = 1830\ \mathrm{cm^2/(V\cdot s)}\)). Heating to 350 K multiplies \(n_i\) by " + g(ratio, 3) + r" (as computed from \(e^{-E_g/2kT}\)). Ignoring changes in mobility, what is the resistivity at 350 K, in kΩ·cm?",
          rho300 / ratio / 1e3, "kΩ·cm",
          X(r"\(\sigma = q n_i(\mu_n+\mu_p)\) is proportional to \(n_i\), so \(\rho\) falls by the same factor:",
            r"\[\rho(350\ \mathrm{K}) = \frac{" + g(rho300 / 1e3, 3) + r"}{" + g(ratio, 3) + r"} \approx " + g(rho300 / ratio / 1e3, 3) + r"\ \mathrm{k}\Omega\cdot\mathrm{cm}\]",
            r"A resistor whose value drops by 20 times over a 50 K swing would be useless in a circuit (though fine as a temperature sensor). The next skill, doping, fixes the carrier concentration with impurities instead of leaving it to temperature."),
          preview=["doping"])
    s.mc(r"Preview of doping: suppose \(10^{16}\ \mathrm{cm^{-3}}\) extra free electrons are added to silicon by impurities (with no extra holes). After the sample returns to thermal equilibrium at 300 K, what is the hole concentration?",
         r"About \(10^{4}\ \mathrm{cm^{-3}}\): extra electrons make holes recombine faster until \(np = n_i^2\) again",
         [r"Still \(10^{10}\ \mathrm{cm^{-3}}\); the impurities only add electrons", r"About \(10^{16}\ \mathrm{cm^{-3}}\), matching the electrons", r"Zero: every hole recombines"],
         X(r"Mass action still holds in equilibrium: \(p = n_i^2/n = 10^{20}/10^{16} = 10^{4}\ \mathrm{cm^{-3}}\).",
           r"The impurities raise \(n\) by a factor of \(10^6\), and recombination pushes \(p\) DOWN by the same factor. Holes become the rare 'minority' carriers. Holes don't vanish completely, because thermal generation keeps making a few."),
         preview=["doping"])
    phi = kTq * math.log(1e16 / ni)
    s.num(r"Preview of carrier concentration versus potential: a later skill shows that in equilibrium, a region with electron concentration \(n\) sits at an electrostatic potential \(\varphi = \frac{kT}{q}\ln\frac{n}{n_i}\) relative to intrinsic silicon. Evaluate \(\varphi\) in mV for \(n = 10^{16}\ \mathrm{cm^{-3}}\), with \(kT/q = 26\ \mathrm{mV}\).",
          phi * 1e3, "mV",
          X(r"\[\varphi = 26\ \mathrm{mV}\times\ln(10^{6}) = 26 \times 13.82 \approx " + g(phi * 1e3, 3) + r"\ \mathrm{mV}\]",
            r"Handy shortcut: \(\ln 10 \times 26\ \mathrm{mV} \approx 60\ \mathrm{mV}\) per decade above \(n_i\), so 6 decades give about 360 mV. These potentials are what build the barrier inside a PN junction."),
          preview=["carrier-pot"])
    return s

def doping():
    s = Skill('doping')
    s.round(1)
    s.mc(r"Phosphorus (group V) is added to silicon. What kind of dopant is it, and what type of silicon results?",
         "A donor; it makes n-type silicon (electrons are the majority carriers)",
         ["An acceptor; it makes p-type silicon", "A donor; it makes p-type silicon because it leaves positive ions", "Neither; group V atoms don't fit in the lattice"],
         X(r"P's fifth valence electron isn't needed for bonding, so it is donated to the crystal as a free electron (reader Sec. 3.5.1). Free electrons outnumber holes, so the material is n-type.",
           r"The positive P⁺ ions are fixed in place and carry no current, so they don't make the material p-type. Acceptors (boron, group III) make p-type."),
         figure=FG.lattice("donor"), alt=lat_alt("donor"))
    ND = 1e16
    s.num(r"Silicon is doped with \(N_D = 10^{16}\ \mathrm{cm^{-3}}\) donors at 300 K (\(n_i = 10^{10}\ \mathrm{cm^{-3}}\)). What is the equilibrium hole concentration \(p_0\)? Scientific notation is fine.",
          ni ** 2 / ND, "cm⁻³",
          X(r"Because \(N_D \gg n_i\), \(n_0 \approx N_D = 10^{16}\). By mass action:",
            r"\[p_0 = \frac{n_i^2}{N_D} = \frac{10^{20}}{10^{16}} = 10^{4}\ \mathrm{cm^{-3}}\]",
            r"Holes are the minority carriers, outnumbered \(10^{12}\) to 1 (reader Eq. 3.36)."))
    s.mc(r"Silicon is doped with boron at \(N_A = 10^{17}\ \mathrm{cm^{-3}}\). Which carriers are the majority, and about how many are there?",
         r"Holes, \(p_0 \approx 10^{17}\ \mathrm{cm^{-3}}\)",
         [r"Electrons, \(n_0 \approx 10^{17}\ \mathrm{cm^{-3}}\)", r"Holes, \(p_0 \approx 10^{10}\ \mathrm{cm^{-3}}\)", r"Electrons, \(n_0 \approx 10^{3}\ \mathrm{cm^{-3}}\)"],
         X(r"Boron is an acceptor: each atom accepts a bonding electron and releases a free hole, so \(p_0 \approx N_A = 10^{17}\) (Eq. 3.37).",
           r"The electrons drop to \(n_0 = n_i^2/N_A = 10^{3}\ \mathrm{cm^{-3}}\): they are the minority carriers."),
         figure=FG.lattice("acceptor"), alt=lat_alt("acceptor"))
    s.round(2)
    NDs = 1e10
    n0 = (NDs + math.sqrt(NDs ** 2 + 4 * ni ** 2)) / 2
    s.num(r"Very light doping: \(N_D = 10^{10}\ \mathrm{cm^{-3}}\), equal to \(n_i = 10^{10}\ \mathrm{cm^{-3}}\). The approximation \(n_0 \approx N_D\) fails here. Use the exact charge-neutrality result \(n_0 = \frac{N_D + \sqrt{N_D^2 + 4n_i^2}}{2}\) to find \(n_0\). Scientific notation is fine.",
          n0, "cm⁻³",
          X(r"\[n_0 = \frac{10^{10} + \sqrt{10^{20} + 4\times10^{20}}}{2} = 10^{10}\cdot\frac{1 + \sqrt5}{2} \approx " + sci(n0, 4) + r"\ \mathrm{cm^{-3}}\]",
            r"Not \(N_D + n_i = 2\times10^{10}\): the extra electrons speed up recombination, which also removes some of the thermally generated pairs. Check: \(p_0 = n_i^2/n_0 = 6.18\times10^{9}\), and \(n_0 - p_0 = 10^{10} = N_D\), so the sample is charge-neutral."))
    NDc, NAc = 3e16, 1e16
    p0 = ni ** 2 / (NDc - NAc)
    s.num(r"A silicon sample contains both donors \(N_D = 3\times10^{16}\) and acceptors \(N_A = 10^{16}\ \mathrm{cm^{-3}}\) (compensation). What is the equilibrium hole concentration \(p_0\) at 300 K? (\(n_i = 10^{10}\ \mathrm{cm^{-3}}\))",
          p0, "cm⁻³",
          X(r"The acceptors soak up \(10^{16}\) of the donated electrons, so the material is n-type with \(n_0 \approx N_D - N_A = 2\times10^{16}\) (reader Eq. 3.39).",
            r"\[p_0 = \frac{n_i^2}{N_D - N_A} = \frac{10^{20}}{2\times10^{16}} = 5\times10^{3}\ \mathrm{cm^{-3}}\]",
            r"Common mistakes: using \(N_A\) as the hole density (the acceptors' holes recombined with donor electrons), or using \(N_D\) alone (gives \(10^4/3\))."))
    s.mc(r"Which equation states charge neutrality in a uniformly doped region (ionized donors \(N_D\), ionized acceptors \(N_A\))?",
         r"\(q\,(p_0 - n_0 + N_D - N_A) = 0\)",
         [r"\(q\,(p_0 + n_0 - N_D - N_A) = 0\)", r"\(q\,(n_0 - p_0 + N_D - N_A) = 0\)", r"\(p_0\,n_0 = N_D N_A\)"],
         X(r"Count the charge signs: holes \(+q\), electrons \(-q\), ionized donors \(N_D^+\) are \(+q\) (they gave away an electron), ionized acceptors \(N_A^-\) are \(-q\). So \(\rho = q(p_0 - n_0 + N_D - N_A) = 0\) (reader Eq. 3.30, 5.18).",
           r"Combined with \(n_0p_0 = n_i^2\), this gives all the doping results. \(p_0n_0 = N_DN_A\) is a mash-up of mass action that isn't true."))
    s.round(3)
    s.mc(r"A silicon sample is doped with EQUAL concentrations of donors and acceptors, \(N_D = N_A = 10^{17}\ \mathrm{cm^{-3}}\). What are its equilibrium carrier concentrations?",
         r"\(n_0 = p_0 \approx n_i = 10^{10}\ \mathrm{cm^{-3}}\): fully compensated, it behaves like intrinsic silicon as far as carrier counts go",
         [r"\(n_0 = p_0 = 10^{17}\ \mathrm{cm^{-3}}\)", r"\(n_0 = 2\times10^{17}\ \mathrm{cm^{-3}}\), \(p_0 = 5\times10^{2}\ \mathrm{cm^{-3}}\)", r"\(n_0 = 10^{17}\), \(p_0 = 10^{3}\ \mathrm{cm^{-3}}\)"],
         X(r"Neutrality: \(p_0 - n_0 + N_D - N_A = 0 \Rightarrow p_0 = n_0\). Mass action: \(n_0p_0 = n_i^2 \Rightarrow n_0 = p_0 = n_i\).",
           r"Gotcha: every donated electron fills an acceptor's empty bond, so the dopants cancel. The dopant IONS are still there, \(2\times10^{17}\ \mathrm{cm^{-3}}\) of them. They don't add carriers, but they do scatter carriers (lower mobility), so the sample isn't truly identical to pure silicon."))
    nih, NDh = 1e15, 1e15
    n0h = (NDh + math.sqrt(NDh ** 2 + 4 * nih ** 2)) / 2
    p0h = nih ** 2 / n0h
    s.num(r"Hot silicon: at about 600 K, \(n_i \approx 10^{15}\ \mathrm{cm^{-3}}\). A sample doped with \(N_D = 10^{15}\ \mathrm{cm^{-3}}\) is at that temperature. What is the hole concentration \(p_0\)? (Careful about which approximation is valid.)",
          p0h, "cm⁻³",
          X(r"Here \(N_D\) is NOT much larger than \(n_i\), so \(n_0 \approx N_D\) is wrong. Use the exact result:",
            r"\[n_0 = \frac{N_D + \sqrt{N_D^2 + 4n_i^2}}{2} = 10^{15}\cdot\frac{1+\sqrt5}{2} = " + sci(n0h, 4) + r"\ \mathrm{cm^{-3}}\]",
            r"\[p_0 = \frac{n_i^2}{n_0} = \frac{10^{30}}{" + sci(n0h, 4) + r"} \approx " + sci(p0h, 3) + r"\ \mathrm{cm^{-3}}\]",
            r"Gotcha: the naive \(p_0 = n_i^2/N_D = 10^{15}\) is off by 60%. At high temperature 'minority' holes are almost as plentiful as electrons, and the doping no longer controls the material. This is why chips have a maximum operating temperature."))
    s.mc(r"Adding donors to silicon LOWERS the hole concentration, even though donors never touch the holes directly. What is the mechanism?",
         "The extra electrons raise the recombination rate (∝ np), while thermal generation stays the same, so holes are destroyed faster until np = nᵢ² again",
         ["Each donor ion captures a hole and neutralizes it", "Donors turn holes into electrons", "Holes are not affected; only the ratio n/p changes"],
         X(r"\(G_{th}(T)\) depends only on temperature, but \(R = k\,n\,p\). More electrons mean a hole finds a partner sooner. The new balance needs a lower \(p\): \(p_0 = n_i^2/n_0\) (reader Sec. 3.5.4).",
           r"Gotcha: the fixed donor ions are positive and would REPEL holes; they don't bind them. 'Turning holes into electrons' doesn't conserve anything; recombination removes one of each."))
    s.round(4)
    ND4, mu4 = 1e16, 1200
    rho4 = 1 / (q * ND4 * mu4)
    s.num(r"Preview of drift current: conductivity is \(\sigma = q(n\mu_n + p\mu_p)\). For silicon doped with \(N_D = 10^{16}\ \mathrm{cm^{-3}}\) (\(\mu_n = 1200\), \(\mu_p = 450\ \mathrm{cm^2/(V\cdot s)}\)), what is the resistivity in Ω·cm?",
          rho4, "Ω·cm",
          X(r"\(n_0 \approx 10^{16}\), while \(p_0 = 10^{4}\) contributes \(10^{-12}\) as much, so ignore it:",
            r"\[\rho \approx \frac{1}{qN_D\mu_n} = \frac{1}{(1.602\times10^{-19})(10^{16})(1200)} \approx " + g(rho4, 3) + r"\ \Omega\cdot\mathrm{cm}\]",
            r"Compared with pure silicon (about 340 kΩ·cm), adding one dopant per 5 million atoms lowers \(\rho\) by about \(10^{6}\). That control of conductivity is what the drift skill builds on."),
          preview=["drift"])
    phi4 = kTq * math.log(1e17 / ni)
    s.num(r"Preview of carrier concentration versus potential: later you'll see that an n-type region sits at \(\varphi_n = \frac{kT}{q}\ln\frac{n_0}{n_i}\) above intrinsic silicon. Find \(\varphi_n\) in mV for \(N_D = 10^{17}\ \mathrm{cm^{-3}}\) (\(kT/q = 26\ \mathrm{mV}\), \(n_i = 10^{10}\ \mathrm{cm^{-3}}\)).",
          phi4 * 1e3, "mV",
          X(r"\(n_0 \approx N_D = 10^{17}\) (doping fixes \(n_0\)), so",
            r"\[\varphi_n = 26\ \mathrm{mV}\times\ln(10^{7}) = 26 \times 16.12 \approx " + g(phi4 * 1e3, 3) + r"\ \mathrm{mV}\]",
            r"The '60 mV per decade' rule gives \(7 \times 60 = 420\) mV. A p-type region would come out NEGATIVE by the same amount. Put the two side by side and you get a built-in voltage: the PN junction."),
          preview=["carrier-pot"])
    s.mc(r"Preview of excess carriers: n-type silicon (\(N_D = 10^{16}\ \mathrm{cm^{-3}}\)) is lit, generating an extra \(10^{12}\ \mathrm{cm^{-3}}\) electron–hole pairs. Which statement is right?",
         r"The minority holes rise from \(10^{4}\) to about \(10^{12}\ \mathrm{cm^{-3}}\), a huge relative change, while the majority electrons change by only 0.01%",
         [r"The electrons double, while the holes barely change", r"Both change by the same relative amount, a factor of 2", r"Nothing changes, because \(np\) must stay equal to \(n_i^2\)"],
         X(r"\(n = 10^{16} + 10^{12}\): up by 0.01%. \(p = 10^{4} + 10^{12} \approx 10^{12}\): up by a factor of \(10^{8}\).",
           r"Because the minority population starts so tiny, any disturbance is dominated by what happens to the MINORITY carriers. The excess-carrier and diode skills build on exactly this idea. (\(np = n_i^2\) only holds in equilibrium; under light \(np \gg n_i^2\).)"),
         preview=["excess-carriers"])
    return s
