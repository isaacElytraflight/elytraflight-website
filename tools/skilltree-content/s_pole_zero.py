from qlib import *

def build():
    s = Skill('pole-zero')
    s.round(1)
    s.mc("For a transfer function H = N(s)/D(s), what are the 'poles' and 'zeros'?",
         "Zeros are the roots of the numerator N (where H = 0); poles are the roots of the denominator D (where H blows up)",
         ["Poles are the roots of the numerator; zeros are the roots of the denominator",
          "Poles are the frequencies where H = 0; zeros are the frequencies where |H| = 1",
          "Poles and zeros are both roots of the denominator, for the real and imaginary parts respectively"],
         "Zeros ('stakes in the ground' of the tent) are values of s where the numerator vanishes, so H = 0. Poles are values of s where the denominator vanishes, so |H| → ∞ (the poles holding the tent up) (reader Sec. 2.3.2).\n"
         "The other options swap the roles or invent definitions.")
    s.mc("The RC low-pass filter has H(s) = 1/(1 + sτ). Where is its pole?",
         "At s = −1/τ (on the negative real axis)",
         ["At s = +1/τ", "At s = jτ", "At s = 0"],
         "Set the denominator to zero: 1 + sτ = 0 ⇒ s = −1/τ. A negative real pole means a decaying exponential e^(−t/τ) in the response. The magnitude of the pole, 1/τ, is the corner (break) frequency in rad/s.\n"
         "A positive pole would mean an exponentially growing response (unstable); s = 0 would be an integrator.")
    R, C = 1e3, 1e-6
    wp = 1/(R*C)
    s.num("An RC low-pass has R = 1 kΩ and C = 1 µF. At what angular frequency (rad/s) is its pole?",
          wp, "rad/s",
          "H(s) = 1/(1 + sRC) has its pole at s = −1/(RC) = −1/(10³ × 10⁻⁶) = −1000. The pole frequency is ω_p = 1000 rad/s (f_p = 159 Hz).\n"
          "Common mistake: answering in Hz (159 Hz) when asked for rad/s.")
    s.round(2)
    poles = np.roots([1, 30, 200])
    zero = -200
    slow = min(abs(poles))
    assert close(slow, 10)
    s.num("The transfer function H(s) = (s + 200)/(s² + 30s + 200) has real poles. What is the magnitude, in rad/s, of the pole CLOSEST to the origin (the lowest-frequency pole)?",
          slow, "rad/s",
          "Factor the denominator: s² + 30s + 200 = (s + 10)(s + 20), so the poles are at s = −10 and s = −20 rad/s. The zero (from s + 200 = 0) is at s = −200.\n"
          "The pole closest to the origin has magnitude 10 rad/s. Common mistake: reading −200 (the zero) as a pole, or using the sum 30.")
    s.mc("An RC high-pass filter has H(jω) = jωτ/(1 + jωτ), τ = 1 ms. Which statement describes its pole and zero?",
         "One zero at s = 0 and one pole at s = −1000 rad/s",
         ["One zero at s = −1000 rad/s and one pole at s = 0",
          "One zero at s = 0 and one pole at s = +1000 rad/s",
          "No zero, and one pole at s = −1000 rad/s"],
         "With s = jω: H(s) = sτ/(1 + sτ). The numerator vanishes at s = 0 (a zero at the origin: no DC transmission). The denominator vanishes at s = −1/τ = −1000 rad/s (a pole in the left half-plane).\n"
         "• Swapping the two reverses the high-pass into something like an integrator.\n"
         "• A positive pole would mean an unstable (growing) response.\n"
         "• The numerator is not a constant, so there is a zero.")
    H0 = 1000*400/(20*2000)
    # evaluate at small s
    Hs = lambda s_: 1000*(s_+400)/((s_+20)*(s_+2000))
    assert close(Hs(1e-9), 10)
    s.num("A circuit has H(s) = 1000(s + 400)/((s + 20)(s + 2000)). What is its DC gain H(0)?",
          H0, "V/V",
          "At DC, s = 0: H(0) = 1000 × 400/(20 × 2000) = 400,000/40,000 = 10.\n"
          "In normalized form, H = 10(1 + s/400)/[(1 + s/20)(1 + s/2000)]: DC gain 10, a zero at 400 rad/s, poles at 20 and 2000 rad/s. Common mistake: including s in the DC evaluation or forgetting the factor 1000.")
    s.round(3)
    s.mc("A circuit contains two capacitors and three resistors (and a voltage source). Which statement about the number of poles of its transfer function is correct?",
         "There are at most 2 poles, and fewer if the capacitors are not independent (e.g., two capacitors in parallel behave as one)",
         ["There are always exactly 2 poles", "There are 5 poles, one for each element", "There are no poles unless an inductor is present"],
         "The number of poles equals the number of independent energy-storage elements (the order of the circuit's differential equation) (reader Sec. 2.3.2). Resistors do not add poles.\n"
         "Two capacitors in parallel combine into C₁ + C₂ (one independent state) and give only one pole; so can a capacitor loop or a capacitor in series with another one, depending on the connection. So 'at most 2', not always 2.\n"
         "RC circuits have poles without any inductor.")
    roots = np.roots([1, 1500, 500000])
    assert sorted(roots.real) == [-1000, -500] or np.allclose(sorted(roots.real), [-1000, -500])
    s.mc("A circuit has H(s) = (s + 500)/(s² + 1500s + 500000). Which description of its behavior is correct?",
         "The zero at −500 cancels the pole at −500, so it behaves like a single-pole low-pass with a pole at 1000 rad/s",
         ["It is second-order with poles at 500 and 1000 rad/s, plus a zero at 500 rad/s that makes it a high-pass",
          "It has a single pole at 500 rad/s",
          "It has two complex poles and shows resonant peaking"],
         "Factor the denominator: s² + 1500s + 500000 = (s + 500)(s + 1000). So H = (s + 500)/[(s + 500)(s + 1000)] = 1/(s + 1000).\n"
         "The zero at −500 cancels one pole exactly, leaving a first-order low-pass with pole at 1000 rad/s (DC gain 10⁻³).\n"
         "• Don't count the cancelled pair as separate features.\n"
         "• The remaining pole is at 1000, not 500.\n"
         "• The discriminant 1500² − 4(500000) = 250,000 > 0, so the poles are real (no peaking).")
    L, C, R = 10e-3, 25e-6, 50.0
    rts = np.roots([L*C, R*C, 1])
    big = max(abs(rts))
    assert close(big, 4000) and close(min(abs(rts)), 1000)
    s.num("A series RLC circuit with R = 50 Ω, L = 10 mH, C = 25 µF has output across C: H(s) = 1/(1 + sRC + s²LC). Its poles are real. What is the magnitude, in rad/s, of the HIGHER-frequency pole?",
          big, "rad/s",
          "Poles satisfy s²LC + sRC + 1 = 0, i.e., s² + (R/L)s + 1/(LC) = 0, with R/L = 5000 s⁻¹ and 1/(LC) = 4×10⁶ s⁻².\n"
          "s = [−5000 ± √(5000² − 4×4×10⁶)]/2 = [−5000 ± √(9×10⁶)]/2 = (−5000 ± 3000)/2 → s = −1000 and −4000 rad/s.\n"
          "The higher pole has magnitude 4000 rad/s. Notice neither pole equals ω₀ = 1/√(LC) = 2000 rad/s or R/L = 5000 s⁻¹: the poles split around ω₀ (their geometric mean is ω₀: √(1000 × 4000) = 2000).\n"
          "Common mistake: using ω₀ = 2000 for both poles.")
    s.round(4)
    s.mc("Preview of Bode plots. A later skill says: each pole bends the magnitude slope by −20 dB/decade at its break frequency, and each zero bends it by +20 dB/decade. For H(s) = 1000(s + 400)/((s + 20)(s + 2000)), what is the slope of |H| (in dB/decade) between 400 rad/s and 2000 rad/s?",
         "0 dB/decade (flat)",
         ["−20 dB/decade", "−40 dB/decade", "+20 dB/decade"],
         "Break frequencies: pole at 20, zero at 400, pole at 2000 rad/s. Start at DC with slope 0.\n"
         "• Above 20 rad/s (pole): slope = −20 dB/dec.\n"
         "• Above 400 rad/s (zero): slope = −20 + 20 = 0 dB/dec.\n"
         "• Above 2000 rad/s (pole): slope = 0 − 20 = −20 dB/dec.\n"
         "So between 400 and 2000 rad/s the magnitude is flat (the zero cancels the first pole's slope).\n"
         "Common mistake: forgetting that a zero bends the slope upward, giving −20 or −40.",
         preview=["bode"])
    s.mc("Preview of stability. A later skill says that a pole at s = p contributes a response term e^(pt), so a system is stable only if every pole has a negative real part. Which pole set describes a system whose natural response decays to zero?",
         "Poles at s = −3 ± j4",
         ["Poles at s = +2 ± j5", "Poles at s = 0 ± j10", "A single pole at s = +1"],
         "e^(pt) with p = σ + jω has magnitude e^(σt) (the jω part only rotates). It decays only when σ < 0.\n"
         "• −3 ± j4: e^(−3t) → decays while oscillating at 4 rad/s. ✔\n"
         "• +2 ± j5: e^(+2t) grows without bound.\n"
         "• 0 ± j10: e^(0·t) = 1, a sustained oscillation that neither decays nor grows (marginal).\n"
         "• +1: e^(t) grows exponentially.",
         preview=["stability"])
    R, L = 10.0, 1e-3
    C = 1e-6
    w0 = 1/math.sqrt(L*C); Q = (1/R)*math.sqrt(L/C)
    alpha = w0/(2*Q)
    rts = np.roots([1, R/L, 1/(L*C)])
    assert close(-rts[0].real, alpha) and close(alpha, 5000)
    s.num("Preview of series RLC circuits. A later skill writes the poles of the series RLC as s = −ω₀/(2Q) ± jω₀√(1 − 1/(4Q²)), where ω₀ = 1/√(LC) and Q = (1/R)√(L/C). For R = 10 Ω, L = 1 mH, C = 1 µF, what is the decay rate α = −Re{s} (in s⁻¹) of the circuit's natural response?",
          alpha, "s⁻¹",
          f"ω₀ = 1/√(10⁻⁹) = {g(w0)} rad/s. Q = (1/10)√(10⁻³/10⁻⁶) = (1/10)√1000 = {g(Q,4)}.\n"
          f"α = ω₀/(2Q) = {g(w0)}/(2 × {g(Q,4)}) = {g(alpha)} s⁻¹ (which also equals R/(2L) = 10/(2 × 10⁻³) = 5000).\n"
          "The natural response decays as e^(−5000t) while oscillating at ω₀√(1 − 1/(4Q²)) ≈ 31,225 rad/s. Common mistake: using ω₀/Q = 10,000 (the full bandwidth, twice α).",
          preview=["rlc"])
    return s
