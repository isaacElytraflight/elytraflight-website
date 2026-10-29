from qlib import *

def build():
    s = Skill('phasors')
    s.round(1)
    s.mc("What is the impedance of an ideal capacitor C at angular frequency ω?",
         "Z_C = 1/(jωC)",
         ["Z_C = jωC", "Z_C = −jωC", "Z_C = C/(jω)"],
         "From I = jωC·V (reader Eq. 2.26), Z_C = V/I = 1/(jωC) = −j/(ωC). It is purely imaginary, with magnitude 1/(ωC) that shrinks as frequency rises.\n"
         "• jωC is the ADMITTANCE Y_C, not the impedance.\n"
         "• −jωC has the wrong dependence on ω (it would grow with frequency).\n"
         "• C/(jω) has wrong units.")
    s.mc("In sinusoidal steady state, how do an ideal capacitor and an ideal inductor behave as ω → 0 (near DC)?",
         "The capacitor acts like an open circuit; the inductor acts like a short circuit",
         ["The capacitor acts like a short circuit; the inductor acts like an open circuit",
          "Both act like short circuits",
          "Both act like open circuits"],
         "|Z_C| = 1/(ωC) → ∞ as ω → 0 (open circuit), and |Z_L| = ωL → 0 (short circuit). At very high frequency the roles reverse: the capacitor shorts and the inductor opens.")
    C, f = 100e-9, 1000.0
    Z = 1/(2*math.pi*f*C)
    s.num("What is the magnitude of the impedance of a 100 nF capacitor at f = 1 kHz?",
          Z, "Ω",
          f"|Z_C| = 1/(ωC) = 1/(2π × 1000 × 100×10⁻⁹) = 1/(6.283×10⁻⁴) = {g(Z)} Ω.\n"
          "Common mistake: using f instead of ω (1/(1000 × 10⁻⁷) = 10 kΩ).")
    s.round(2)
    R, L, w = 300.0, 40e-3, 10e3
    Zt = R + 1j*w*L
    assert close(abs(Zt), 500)
    s.num("A 300 Ω resistor is in series with a 40 mH inductor. What is the magnitude of the total impedance at ω = 10,000 rad/s?",
          abs(Zt), "Ω",
          "Z = R + jωL = 300 + j(10⁴ × 0.04) = 300 + j400 Ω.\n"
          "|Z| = √(300² + 400²) = √250,000 = 500 Ω (a 3-4-5 triangle).\n"
          "Common mistake: adding magnitudes, 300 + 400 = 700 Ω. Resistance and reactance are 90° apart in the complex plane, so they add as vectors.")
    C, f, V = 0.1e-6, 1000.0, 5.0
    Ipk = 2*math.pi*f*C*V
    # check via complex
    I = 1j*2*math.pi*f*C*V
    assert close(abs(I), Ipk)
    s.num("A 0.1 µF capacitor has the voltage v(t) = 5cos(2π·1000·t) V across it. What is the PEAK value of the current through it?",
          Ipk*1e3, "mA",
          f"Phasor relation: I = jωC·V, so |I| = ωC|V| = 2π(1000)(0.1×10⁻⁶)(5) = {g(Ipk*1e3)} mA.\n"
          "(The current leads the voltage by 90°.) Common mistake: forgetting 2π, which gives 0.5 mA.")
    s.mc("For a single circuit element, the voltage is v(t) = 10cos(ωt) V and the current is i(t) = 2cos(ωt − 90°) A with ω = 1000 rad/s. What is the element?",
         "An inductor of 5 mH",
         ["A capacitor of 200 µF", "A resistor of 5 Ω", "An inductor of 5 H"],
         "The current LAGS the voltage by 90°, which is the signature of an inductor (V = jωL·I, so V leads I by 90°). |Z| = 10 V/2 A = 5 Ω = ωL ⇒ L = 5/1000 = 5 mH.\n"
         "• A capacitor's current would LEAD the voltage by 90°; 200 µF would have 1/(ωC) = 5 Ω but the wrong phase relationship.\n"
         "• A resistor would have current in phase with voltage.\n"
         "• 5 H would make ωL = 5000 Ω, not 5 Ω (units slip).")
    s.round(3)
    s.mc("A series circuit of an inductor and a capacitor is driven by a sinusoidal source. The measured voltage amplitudes are |V_L| = 40 V and |V_C| = 30 V. What is the amplitude of the source voltage?",
         "10 V",
         ["70 V", "50 V", "35 V"],
         "In a series circuit the same current flows through both, so V_L = jωL·I leads I by 90° and V_C = I/(jωC) lags I by 90°: the two voltages are 180° out of phase and subtract. Source = |40 − 30| = 10 V (phasor addition, reader Fig. 2.12).\n"
         "• 70 V adds the magnitudes as if they were in phase.\n"
         "• 50 V is the Pythagorean sum (√(40² + 30²)), which would be right if they were 90° apart (e.g., one was a resistor voltage).\n"
         "• 35 V is just their average.")
    C, w, V = 10e-6, 1000.0, 20.0
    t = 1e-3
    i = w*C*V*math.cos(w*t + math.pi/2)
    # check using derivative: i = C dv/dt = -C V w sin(wt)
    assert close(i, -C*V*w*math.sin(w*t))
    s.num("A 10 µF capacitor has v(t) = 20cos(1000t) V across it (t in seconds). What is the current i(t) at t = 1 ms? (Use the reference direction that makes i = C·dv/dt.)",
          i*1e3, "mA",
          "Phasor: I = jωC·V = j(1000)(10×10⁻⁶)(20) = j0.2 A = 0.2∠90° A. So i(t) = 0.2cos(1000t + 90°) = −0.2 sin(1000t) A.\n"
          f"At t = 1 ms: ωt = 1 rad, so i = −0.2 sin(1 rad) = −0.2 × 0.8415 = {g(i*1e3)} mA.\n"
          "(Check with the time-domain relation i = C dv/dt = 10 µF × (−20000 sin(1000t)) = −0.2 sin(1000t) A ✔.)\n"
          "Common mistakes: working in degrees (sin 1° = 0.0175) or dropping the 90° phase lead (0.2cos(1) = +108 mA).")
    s.mc("Using a cosine reference, which phasor represents v(t) = 10sin(ωt + 30°) V?",
         "10∠−60° V",
         ["10∠30° V", "10∠120° V", "10∠60° V"],
         "Phasors are defined relative to cos(ωt + φ). Convert: sin(x) = cos(x − 90°), so 10sin(ωt + 30°) = 10cos(ωt + 30° − 90°) = 10cos(ωt − 60°). The phasor is 10∠−60°.\n"
         "• 10∠30° treats the sine as a cosine (no conversion).\n"
         "• 10∠120° adds 90° instead of subtracting it (that would represent −sin).\n"
         "• 10∠60° flips the sign of the correct phase.")
    s.round(4)
    R, L, w = 1e3, 10e-3, 100e3
    H = 1j*w*L/(R+1j*w*L)
    v0 = 4*abs(H)*math.cos(cmath.phase(H))
    assert close(v0, 2.0)
    s.num("Preview of finding H(jω) directly. A later skill shows that a series R–L circuit with the output taken across the inductor has H(jω) = jωL/(R + jωL). With R = 1 kΩ, L = 10 mH, ω = 100 krad/s and v_in(t) = 4cos(ωt) V, what is the steady-state output v_out at t = 0?",
          v0, "V",
          "Phasor impedances: Z_L = jωL = j(10⁵)(0.01) = j1000 Ω. H = j1000/(1000 + j1000) = j/(1 + j) = 0.7071∠(90° − 45°) = 0.7071∠45°.\n"
          "Output = 4 × 0.7071 = 2.828 V amplitude with a +45° phase: v_out = 2.828cos(ωt + 45°).\n"
          f"At t = 0: 2.828cos 45° = {g(v0)} V.\n"
          "Common mistake: using −45° (for a low-pass) or forgetting that an inductor's impedance is a positive-imaginary number.",
          preview=["direct-h"])
    R, w, I = 10.0, 1000.0, 2.0
    C = 1/(w*10.0)
    Z = R + 1/(1j*w*C)
    P = 0.5*I**2*Z.real
    assert close(P, 20)
    s.num("Preview of AC power. A later skill shows that the average power into a load is P = ½|I|²·Re{Z}, where I is the peak current phasor. A load is a 10 Ω resistor in series with a capacitor whose reactance magnitude is 10 Ω at ω = 1000 rad/s (C = 100 µF). The peak current is 2 A. What is the average power?",
          P, "W",
          "Z = R + 1/(jωC) = 10 − j10 Ω, so Re{Z} = 10 Ω (the imaginary part comes from the capacitor).\n"
          "P = ½(2 A)²(10 Ω) = 20 W. The capacitor's reactance does not change the answer: only the resistive part dissipates power.\n"
          "Common mistake: using |Z| = 14.1 Ω (gives 28.3 W) or forgetting the ½ for a peak (not RMS) current (40 W).",
          preview=["ac-power"])
    R, L, C, w = 50.0, 10e-3, 1e-6, 5000.0
    Z = R + 1j*w*L + 1/(1j*w*C)
    assert close(abs(Z), math.sqrt(50**2+150**2))
    s.num("Preview of series RLC circuits. A series circuit has R = 50 Ω, L = 10 mH and C = 1 µF. (A later skill shows it resonates at ω₀ = 1/√(LC) = 10,000 rad/s, where Im Z = 0.) What is the magnitude of the total impedance at ω = 5000 rad/s, half the resonant frequency?",
          abs(Z), "Ω",
          "Z = R + jωL + 1/(jωC).\n"
          "jωL = j(5000)(0.01) = +j50 Ω. 1/(jωC) = −j/(5000 × 10⁻⁶) = −j200 Ω.\n"
          "Z = 50 + j(50 − 200) = 50 − j150 Ω.\n"
          f"|Z| = √(50² + 150²) = √25,000 = {g(abs(Z))} Ω (capacitive, since the capacitor's reactance dominates below resonance).\n"
          "Common mistake: adding the reactances with the same sign (50 + 200 = 250), or adding magnitudes of everything (300 Ω).",
          preview=["rlc"])
    return s
