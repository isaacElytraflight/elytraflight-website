from qlib import *

def build():
    s = Skill('rlc')
    s.round(1)
    s.mc("What is the resonant frequency of a series RLC circuit (ideal L and C)?",
         "ω₀ = 1/√(LC)",
         ["ω₀ = √(LC)", "ω₀ = 1/(RC)", "ω₀ = R/L"],
         "Resonance occurs when the inductor and capacitor reactances cancel: ω₀L = 1/(ω₀C) ⇒ ω₀ = 1/√(LC) (reader Eq. 2.36). It does not depend on R.\n"
         "• √(LC) has wrong units (it is a time).\n"
         "• 1/(RC) is the corner of an RC filter.\n"
         "• R/L is the decay rate scale of an RL circuit, not the resonance of an LC pair.")
    s.mc("What is the series RLC circuit's input impedance Z at resonance (ω = ω₀)?",
         "Purely real and equal to R (the minimum magnitude of |Z|)",
         ["Infinite (an open circuit)", "Zero (a short circuit)", "Purely imaginary, equal to 2jω₀L"],
         "Z = R + jωL + 1/(jωC) = R + j(ωL − 1/(ωC)). At ω₀ the bracket vanishes: Z = R, which is the smallest |Z| the circuit ever has, so the current is largest (reader Sec. 2.5.3).\n"
         "• Infinite impedance is the PARALLEL LC resonance.\n"
         "• The resistor is still in series, so Z cannot be zero.\n"
         "• The reactances cancel rather than add.")
    L, C = 10e-3, 1e-6
    f0 = 1/(2*math.pi*math.sqrt(L*C))
    s.num("A series RLC circuit has L = 10 mH and C = 1 µF. What is its resonant FREQUENCY f₀ in hertz?",
          f0, "Hz",
          f"ω₀ = 1/√(LC) = 1/√(10⁻²·10⁻⁶) = 1/√(10⁻⁸) = 10⁴ rad/s.\n"
          f"f₀ = ω₀/(2π) = 10,000/6.2832 = {g(f0)} Hz. Common mistake: reporting 10,000 (that is in rad/s).")
    s.round(2)
    R, L, C = 20.0, 10e-3, 1e-6
    w0 = 1/math.sqrt(L*C); Q = w0*L/R
    assert close(Q, 5)
    s.num("A series RLC circuit has R = 20 Ω, L = 10 mH and C = 1 µF. What is its quality factor Q = ω₀L/R?",
          Q, "(unitless)",
          "ω₀ = 1/√(LC) = 10⁴ rad/s. Q = ω₀L/R = (10⁴)(0.01)/20 = 100/20 = 5.\n"
          "Equivalent forms (reader Eq. 2.40): Q = 1/(ω₀RC) = (1/R)√(L/C) = Z₀/R. Check: (1/20)√(0.01/10⁻⁶) = (1/20)(100) = 5 ✔.")
    bw_rad = w0/Q
    bwf = bw_rad/(2*math.pi)
    # check against exact -3dB points
    def H(w): return (1j*w*R*C)/(1 - w*w*L*C + 1j*w*R*C)

    wl = brentq(lambda w: abs(H(w))**2 - 0.5, 1e3, w0)
    wh = brentq(lambda w: abs(H(w))**2 - 0.5, w0, 1e5)
    assert close(wh - wl, bw_rad, 1e-6)
    s.num("For the series RLC circuit of the previous problem (R = 20 Ω, L = 10 mH, C = 1 µF, Q = 5), with the output taken across R, what is the −3 dB bandwidth Δf in hertz? (Δω = ω₀/Q.)",
          bwf, "Hz",
          f"Δω = ω₀/Q = 10⁴/5 = 2000 rad/s (also R/L = 20/0.01 = 2000 ✔).\n"
          f"Δf = Δω/(2π) = 2000/6.2832 = {g(bwf)} Hz.\n"
          "Common mistake: stating 2000 (rad/s) as the answer in Hz. (Numerically solving |H|² = ½ gives ω₊ − ω₋ = 2000 rad/s exactly.)")
    s.mc("A series RLC circuit has Q = 5 and is driven by a source of amplitude 2 V at its resonant frequency. What is the amplitude of the voltage across the inductor?",
         "10 V",
         ["2 V", "0 V", "50 V"],
         "At resonance I = V_s/R, so V_L = jω₀L·I = jω₀L·V_s/R = jQ·V_s. Amplitude = Q × 2 V = 10 V, leading the source by 90° (reader Eq. 2.37). The capacitor voltage has the same magnitude and opposite sign, so V_L + V_C = 0 and the source voltage appears entirely across R.\n"
         "• 2 V forgets the voltage multiplication.\n"
         "• 0 V confuses the net reactive voltage (which is zero) with the individual element voltage.\n"
         "• 50 V uses Q² instead of Q.")
    s.round(3)
    s.mc("In a series RLC circuit (output across R), the resistance R is doubled while L and C stay the same. Which set of statements is correct?",
         "ω₀ is unchanged, Q is halved, the bandwidth doubles, and the peak gain |H(jω₀)| is still 1",
         ["ω₀ doubles, Q is halved, the bandwidth is unchanged, and the peak gain is still 1",
          "ω₀ is unchanged, Q is halved, the bandwidth doubles, and the peak gain is halved",
          "ω₀ falls by √2, Q doubles, the bandwidth halves, and the peak gain is still 1"],
         "ω₀ = 1/√(LC) does not contain R, so it is unchanged. Q = ω₀L/R halves. The bandwidth Δω = ω₀/Q = R/L doubles. At resonance, L and C cancel and V_R = V_s, so the peak gain is 1 regardless of R (reader: 'the peak gain is always unity, regardless of Q').\n"
         "Each wrong option makes at least one error: R does not set ω₀, a larger R makes the circuit LESS selective (wider, not narrower), and the peak of V_R/V_s does not depend on R.")
    Q, w0 = 1.0, 1000.0
    wh_formula = w0*(math.sqrt(1 + 1/(4*Q*Q)) + 1/(2*Q))
    R = 1.0; L = Q*R/w0; C = 1/(w0*w0*L)
    def H(w): return (1j*w*R*C)/(1 - w*w*L*C + 1j*w*R*C)

    wh = brentq(lambda w: abs(H(w))**2 - 0.5, w0, 1e5)
    assert close(wh, wh_formula, 1e-6)
    s.num("A series RLC band-pass circuit (output across R) has ω₀ = 1000 rad/s and Q = 1. What is the exact UPPER −3 dB frequency ω₊ in rad/s? (The approximation ω₀ + Δω/2 is not accurate at low Q.)",
          wh, "rad/s",
          "Set |H|² = 1/2, i.e., (ω₀² − ω²)/(ω₀ω/Q) = ±1. For the upper edge: ω² + (ω₀/Q)ω − ω₀² = 0, so ω₊ = ω₀[√(1 + 1/(4Q²)) + 1/(2Q)].\n"
          f"With Q = 1: ω₊ = 1000(√1.25 + 0.5) = 1000(1.1180 + 0.5) = {g(wh)} rad/s. The lower edge is ω₋ = 1000(1.1180 − 0.5) = 618.0 rad/s.\n"
          "Note ω₊ − ω₋ = 1000 = ω₀/Q ✔ and √(ω₊ω₋) = 1000 = ω₀ (geometric mean). The naive estimate ω₀ + Δω/2 = 1500 rad/s is 7% too low.")
    # Q=0.5 capacitor output
    Q = 0.5; w0 = 1.0
    HC = lambda w: 1/((1 - w*w) + 1j*w/Q)
    ws = np.linspace(0, 5, 5001)
    mags = np.abs(HC(ws))
    assert np.all(np.diff(mags) < 0) and close(abs(HC(1.0)), Q) and close(abs(HC(0)), 1)
    s.mc("A series RLC circuit has Q = 0.5, and the output is the voltage across the capacitor. Which statement about |V_C/V_s| versus frequency is correct?",
         "It starts at 1 at DC and decreases monotonically; there is no resonant peak, and at ω₀ it equals Q = 0.5",
         ["It peaks at exactly ω₀ with a peak value of Q = 0.5",
          "It peaks at ω₀ with a peak value of 1",
          "It rises above 1 near ω₀ because the capacitor voltage is multiplied by Q"],
         "H_C = 1/(1 − (ω/ω₀)² + j(ω/ω₀)/Q). For Q = 0.5 the poles are real and coincident (critical damping): |H_C| = 1/(1 + (ω/ω₀)²), which falls monotonically from 1. At ω₀ it equals Q = 0.5.\n"
         "The 'voltage multiplication by Q' only produces a peak when Q is large enough (peaking exists only for Q > 1/√2 ≈ 0.707). For Q ≈ 10 the peak is near ω₀ and ≈ Q, but here Q < 0.707 so there is none.\n"
         "• The first wrong option claims a peak of 0.5 (lower than the DC gain of 1).\n"
         "• A peak of 1 at ω₀ would be the R-output of the circuit, not the C-output.")
    s.round(4)
    w0 = 1e6; coef = 2e5
    Q = w0/coef
    s.num("Preview of stability. A later skill analyzes feedback amplifiers whose closed-loop response has the denominator s² + 2×10⁵·s + 10¹² (s in rad/s). Compare it with the series-RLC form s² + (R/L)s + 1/(LC) = s² + (ω₀/Q)s + ω₀² . What Q does this feedback amplifier have?",
          Q, "(unitless)",
          "Match coefficients: ω₀² = 10¹² ⇒ ω₀ = 10⁶ rad/s. ω₀/Q = 2×10⁵ ⇒ Q = 10⁶/(2×10⁵) = 5.\n"
          "A Q of 5 means a lightly damped, strongly peaking response: the poles are very close to the jω axis, where an amplifier would ring badly or oscillate. Keeping Q low enough (well below 1) is a key goal of the stability skill. Common mistake: using Q = ω₀/(2 × 2×10⁵) = 2.5; the s-coefficient is ω₀/Q itself, with no extra factor of 2.",
          preview=["stability"])
    L, C = 10e-9, 100e-9
    f0 = 1/(2*math.pi*math.sqrt(L*C))
    s.num("Preview of coupling capacitors and frequency response. A real 100 nF capacitor has a parasitic series inductance (ESL) of 10 nH, so it behaves like a series LC. Using the series-resonance formula, at what frequency (in MHz) does it stop acting like a capacitor and start behaving inductively?",
          f0/1e6, "MHz",
          f"ω₀ = 1/√(LC) = 1/√(10⁻⁸ × 10⁻⁷) = 1/√(10⁻¹⁵) = {g(1/math.sqrt(L*C))} rad/s.\n"
          f"f₀ = ω₀/(2π) = {g(f0/1e6)} MHz. Above f₀ the inductor's reactance exceeds the capacitor's and the part looks like an inductor, so a 'coupling capacitor' is no longer a good signal path (or bypass).\n"
          "Common mistake: forgetting to divide by 2π (giving 31.6 Mrad/s ≈ 31.6 'MHz').",
          preview=["freq-basics"])
    Q = 1.5; vin = 0.2
    HC = lambda w: 1/((1 - w*w) + 1j*w/Q)
    out = vin*abs(HC(1.0))
    s.num("Preview of op-amp frequency response. A closed-loop op-amp stage has a second-order low-pass response H = ω₀²/(s² + (ω₀/Q)s + ω₀²), which at s = jω₀ has magnitude Q (the same voltage multiplication you saw for the series RLC's capacitor). With Q = 1.5, what is the output amplitude for a 0.2 V amplitude tone at ω = ω₀?",
          out, "V",
          "At ω = ω₀: H = ω₀²/(−ω₀² + j(ω₀²/Q) + ω₀²) = ω₀²/(jω₀²/Q) = Q/j, so |H| = Q = 1.5.\n"
          "Output amplitude = 0.2 V × 1.5 = 0.3 V: a 'gain 1' amplifier actually amplifies tones near ω₀ by 50%, i.e., about +3.5 dB of peaking. This is the same phenomenon as an RLC resonance, and it limits the usable bandwidth of the stage.\n"
          "Common mistake: assuming |H| ≤ 1 because the DC gain is 1.",
          preview=["opamp-fr"])
    return s
