from qlib import *

def build():
    s = Skill('direct-h')
    s.round(1)
    s.mc("For the RC low-pass filter (series R, output across C), which expression is H(jω) = V_o/V_s obtained with the voltage-divider formula?",
         "H(jω) = (1/(jωC)) / (R + 1/(jωC)) = 1/(1 + jωRC)",
         ["H(jω) = R/(R + 1/(jωC)) = jωRC/(1 + jωRC)",
          "H(jω) = 1/(1 + ωRC)",
          "H(jω) = 1/(1 − jωRC)"],
         "Treat the capacitor as an impedance Z_C = 1/(jωC) and use the divider (reader Eq. 2.32): H = Z_C/(Z_C + R) = 1/(1 + jωRC). Multiply numerator and denominator by jωC.\n"
         "• R/(R + Z_C) is the output across R (a high-pass).\n"
         "• 1/(1 + ωRC) drops the j (it would be real, with no phase shift).\n"
         "• 1/(1 − jωRC) has the wrong sign: it would be a phase lead for a low-pass.")
    s.mc("What is the first step to find H(jω) 'directly' for an AC circuit (no differential equations)?",
         "Replace each capacitor by 1/(jωC) and each inductor by jωL, then solve as if the circuit were resistive (divider, KCL/KVL, nodal analysis)",
         ["Write the circuit's differential equation and solve it with the initial conditions",
          "Set ω = 0 and replace capacitors by open circuits",
          "Convert every signal to the time domain and find v(t) at t = 0"],
         "The point of phasors is that the e^(jωt) factors cancel and differential equations become algebra: every element becomes an impedance, and all the resistive-circuit tools (voltage divider, Thévenin, nodal analysis) apply (reader Sec. 2.4.4).\n"
         "• Solving a differential equation is the 'hard way'.\n"
         "• Setting ω = 0 gives only the DC gain, not H(jω).\n"
         "• Time-domain evaluation at t = 0 does not give a frequency response.")
    R, C = 1e3, 1e-6
    w = 1/(R*C)
    H = 1j*w*R*C/(1+1j*w*R*C)
    s.num("An RC high-pass filter (series capacitor, output across the resistor to ground) has H(jω) = jωRC/(1 + jωRC). What is |H| at ω = 1/(RC)?",
          abs(H), "V/V",
          "At ω = 1/(RC), ωRC = 1, so H = j/(1 + j). |H| = 1/√(1² + 1²) = 1/√2 = 0.7071 (−3 dB, the corner frequency). The phase is 90° − 45° = +45°.")
    s.round(2)
    R1, R2, C, w = 1e3, 1e3, 100e-9, 10e3
    Zp = 1/(1/R2 + 1j*w*C)
    H = Zp/(R1 + Zp)
    # verify by nodal analysis
    Y = 1/R2 + 1j*w*C
    Vn = (1/R1)/(1/R1 + Y)
    assert close(abs(H), abs(Vn)) and close(abs(H), math.sqrt(0.2))
    s.num("A source drives a 1 kΩ resistor R₁ in series; the output node connects to ground through a 1 kΩ resistor R₂ in parallel with a 100 nF capacitor. At ω = 10 krad/s, what is |V_o/V_s|?",
          abs(H), "V/V",
          "Z_p = R₂ ∥ Z_C = 1000/(1 + jωR₂C). With ωR₂C = (10⁴)(10³)(10⁻⁷) = 1: Z_p = 1000/(1 + j) = 500 − j500 Ω.\n"
          "H = Z_p/(R₁ + Z_p) = (500 − j500)/(1500 − j500).\n"
          f"|numerator| = 707.1, |denominator| = 1581.1, so |H| = {g(abs(H),4)}.\n"
          "Common mistake: treating the parallel RC as if it were just R₂ (H = 0.5) or just C.")
    ph = math.degrees(cmath.phase(H))
    assert close(ph, -26.565, 1e-3)
    s.num("For the same circuit (R₁ = 1 kΩ in series; R₂ = 1 kΩ ∥ C = 100 nF to ground; ω = 10 krad/s), what is the phase of V_o/V_s in degrees? (Give a negative number for a lag.)",
          ph, "degrees",
          f"H = (500 − j500)/(1500 − j500). Phase of numerator: −45°. Phase of denominator: −tan⁻¹(500/1500) = −18.43°.\n"
          f"∠H = −45° − (−18.43°) = {g(ph)}°.\n"
          "Common mistake: subtracting in the wrong direction (−63.4°), or reporting only the numerator's phase (−45°).",
          tol=0.03)
    s.mc("A series R–L–C circuit is driven by v_s. The output v_o is taken across the capacitor. Which expression gives H(jω) = V_o/V_s?",
         "1/(1 − ω²LC + jωRC)",
         ["1/(1 + ω²LC + jωRC)",
          "jωRC/(1 − ω²LC + jωRC)",
          "1/(1 − ω²LC + ωRC)"],
         "Voltage divider: H = Z_C/(R + jωL + Z_C) with Z_C = 1/(jωC). Multiply top and bottom by jωC: H = 1/(jωRC + (jω)²LC + 1) = 1/(1 − ω²LC + jωRC).\n"
         "• (jω)² = −ω², so the LC term is −ω²LC, not +ω²LC.\n"
         "• jωRC/(…) is the output across R (band-pass).\n"
         "• The R term must keep its j (it is the reactive/phase part of the divider).")
    s.round(3)
    R, RL = 1e3, 3e3
    s.mc("An RC low-pass filter (R, C) drives a load resistor R_L connected in parallel with C. Which expression is H(jω) = V_o/V_s?",
         "H = [R_L/(R + R_L)] · 1/(1 + jω(R ∥ R_L)C)",
         ["H = 1/(1 + jωRC)",
          "H = [R_L/(R + R_L)] · 1/(1 + jωRC)",
          "H = 1/(1 + jω(R ∥ R_L)C)"],
         "Use Thévenin at the capacitor: the Thévenin voltage is V_s·R_L/(R + R_L) and the Thévenin resistance is R ∥ R_L. The capacitor then forms a low-pass with this source: H = [R_L/(R + R_L)]/(1 + jω(R ∥ R_L)C).\n"
         "Check the extremes: at DC H = R_L/(R + R_L) < 1 (the load draws current through R), and the pole moves to 1/((R ∥ R_L)C), higher than 1/(RC).\n"
         "• '1/(1 + jωRC)' ignores the load.\n"
         "• Keeping the DC divider but the old pole mixes the two effects.\n"
         "• Keeping the new pole but H(0) = 1 ignores the DC loss.")
    R, C, w = 1e3, 1e-6, 1000.0
    # two-stage RC ladder at wRC = 1; nodal analysis
    Y1 = 1/R
    Yc = 1j*w*C
    A = np.array([[1/R + Yc + 1/R, -1/R], [-1/R, 1/R + Yc]], dtype=complex)
    b = np.array([1/R, 0], dtype=complex)
    v1, v2 = np.linalg.solve(A, b)
    H2 = 1/(1 + 3j*w*R*C + (1j*w*R*C)**2)
    assert close(abs(v2), 1/3, 1e-9) and close(abs(H2), 1/3, 1e-9)
    s.num("A two-stage RC ladder has R₁ = R₂ = 1 kΩ in series and C₁ = C₂ = 1 µF to ground: v_s → R₁ → node 1 (C₁ to ground) → R₂ → output (C₂ to ground), with no load. At ω = 1000 rad/s (ωRC = 1), what is |V_o/V_s|?",
          abs(v2), "V/V",
          "Nodal analysis: for the ladder, H = 1/[1 + 3jωRC + (jωRC)²]. At ωRC = 1: H = 1/(1 + 3j − 1) = 1/(3j), so |H| = 1/3 = 0.3333 (phase −90°).\n"
          "Common mistake: multiplying two single-stage responses, (0.7071)² = 0.5. The second stage loads the first, so the stages do not simply multiply.")
    s.mc("A source v_s drives a parallel LC tank (inductor L in parallel with capacitor C) in series with a resistor R. The output v_o is the voltage across R to ground. What is |V_o/V_s| at the tank's resonant frequency ω₀ = 1/√(LC)?",
         "0, because the parallel LC tank looks like an open circuit at ω₀",
         ["1, because the L and C cancel and the signal passes", "0.5, because the tank and R divide equally", "It depends on Q, but it is never exactly 0"],
         "H = R/(R + Z_tank) with Z_tank = jωL/(1 − ω²LC). At ω₀, 1 − ω₀²LC = 0 so Z_tank → ∞ (equivalently the admittance jωC + 1/(jωL) = 0), so no current can flow: H = 0.\n"
         "A SERIES LC resonance does the opposite (a short, so the signal passes). Parallel resonance blocks.\n"
         "• '1' is the series LC behavior.\n"
         "• '0.5' would need the tank impedance to equal R.\n"
         "• For ideal L and C the null is exact for any Q.")
    # numeric verification of the tank claim
    L, C, Rr = 1e-3, 1e-6, 100.0
    w0 = 1/math.sqrt(L*C)
    Yt = 1j*w0*C + 1/(1j*w0*L)
    assert abs(Yt) < 1e-9
    s.round(4)
    L, C, R = 2e-3, 0.5e-6, 20.0
    w0 = 1/math.sqrt(L*C)
    HC = 1/(1 - w0**2*L*C + 1j*w0*R*C)
    out = 2.0*abs(HC)
    # direct impedance check
    Zc = 1/(1j*w0*C); Zt = R + 1j*w0*L + Zc
    assert close(abs(Zc/Zt), abs(HC))
    s.num("Preview of series RLC circuits. Using the result from this skill, the capacitor-output transfer function of a series RLC is H_C = 1/(1 − ω²LC + jωRC). For L = 2 mH, C = 0.5 µF, R = 20 Ω, a 2 V amplitude source operates at the resonant frequency ω₀ = 1/√(LC). What is the amplitude of the capacitor voltage? (A later skill shows this is 'Q × V_s'.)",
          out, "V",
          f"ω₀ = 1/√(LC) = 1/√(10⁻⁹) = {g(w0)} rad/s, so ω₀²LC = 1 and the real part of the denominator vanishes.\n"
          f"H_C = 1/(jω₀RC) = 1/j(31,623 × 20 × 0.5×10⁻⁶) = 1/j0.3162, so |H_C| = {g(abs(HC),4)} (this is Q = (1/R)√(L/C)).\n"
          f"V_C = 2 V × {g(abs(HC),4)} = {g(out)} V: the capacitor voltage is larger than the source voltage.\n"
          "Common mistake: assuming |H| ≤ 1 because the circuit is passive.",
          preview=["rlc"])
    R, L, C, w = 50.0, 10e-3, 1e-6, 5000.0
    Zs = R + 1j*w*L + 1/(1j*w*C)
    HR = R/Zs
    s.num("Preview of series RLC circuits. The same direct method gives, for output across R, H_R = jωRC/(1 − ω²LC + jωRC) = R/(R + jωL + 1/(jωC)). For R = 50 Ω, L = 10 mH, C = 1 µF at ω = 5000 rad/s (half of the resonant frequency 10,000 rad/s), what is |H_R|?",
          abs(HR), "V/V",
          "ω²LC = (5000)²(10⁻²)(10⁻⁶) = 0.25. ωRC = 5000 × 50 × 10⁻⁶ = 0.25.\n"
          f"Denominator: 1 − 0.25 + j0.25 = 0.75 + j0.25, magnitude √(0.5625 + 0.0625) = 0.7906. Numerator magnitude: 0.25.\n"
          f"|H_R| = 0.25/0.7906 = {g(abs(HR),4)} (and the phase is +71.6°).\n"
          "Below resonance the response is small; it peaks at 1 only at ω₀. Common mistake: dropping the imaginary part of the denominator (0.25/0.75 = 0.333).",
          preview=["rlc"])
    s.mc("Preview of series RLC circuits. For the series RLC with output across R, H(jω) = jωRC/(1 − ω²LC + jωRC). Check its limits with the impedance picture (C open at DC, L open at very high frequency). What type of filter is this?",
         "Band-pass: |H| → 0 at ω → 0 and ω → ∞, with |H| = 1 at ω₀ = 1/√(LC)",
         ["Low-pass: |H| = 1 at DC and → 0 at high frequency",
          "High-pass: |H| → 0 at DC and → 1 at high frequency",
          "Notch: |H| = 1 away from ω₀ and 0 at ω₀"],
         "Direct impedance reasoning: at ω → 0, the capacitor is an open circuit, so no current flows and V_R = 0. At ω → ∞, the inductor is an open circuit, so again V_R = 0. At ω₀ the L and C impedances cancel, leaving only R, so V_R = V_s and |H| = 1. This is a band-pass response.\n"
         "The formula agrees: numerator ~ ω at low ω (→ 0), and for large ω the denominator ~ ω² (→ 0); at ω₀ the denominator is jω₀RC = numerator.",
         preview=["rlc"])
    return s
