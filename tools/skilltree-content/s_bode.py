from qlib import *

def dB(x): return 20*math.log10(x)

def build():
    s = Skill('bode')
    s.round(1)
    s.mc("A first-order low-pass has H = 1/(1 + jω/ω_p). On a Bode magnitude plot (dB versus log frequency), what does the plot look like far above ω_p?",
         "A straight line falling at −20 dB per decade",
         ["A straight line falling at −40 dB per decade", "A flat line at 0 dB", "A straight line rising at +20 dB per decade"],
         "For ω ≫ ω_p, |H| ≈ ω_p/ω. Each factor of 10 in frequency divides |H| by 10, which is −20 dB (reader Sec. 1.2 and 2.6). Equivalently, doubling the frequency lowers the gain by 6 dB.\n"
         "• −40 dB/decade needs two poles.\n"
         "• 0 dB flat is the passband.\n"
         "• +20 dB/decade is the slope of a zero (or of jωτ).")
    s.mc("An amplifier has a voltage gain of 100 V/V. What is that gain in decibels?",
         "40 dB",
         ["20 dB", "100 dB", "10 dB"],
         "Voltage-gain decibels are dB = 20·log₁₀|G|: 20·log₁₀(100) = 20 × 2 = 40 dB. The factor 20 (not 10) is used because power goes as voltage squared (reader Eq. 1.16).\n"
         "• 20 dB corresponds to a gain of 10.\n"
         "• 100 dB would be a gain of 100,000.\n"
         "• 10 dB would be a gain of 3.16 (or would come from forgetting the log).")
    G = 250.0
    s.num("A voltage amplifier has |G_v| = 250 V/V. What is its gain in dB (dB = 20·log₁₀|G_v|)?",
          dB(G), "dB",
          f"20·log₁₀(250) = 20 × 2.3979 = {g(dB(G))} dB.\n"
          "Check: 250 = 2.5 × 100, so 20log(2.5) + 40 dB = 7.96 + 40 = 47.96 dB. Common mistake: using 10·log₁₀ (24 dB).")
    s.round(2)
    wp, A0, w = 1e4, 100.0, 3e5
    H = A0/math.sqrt(1+(w/wp)**2)
    val = dB(H)
    asym = 40 - 20*math.log10(w/wp)
    assert abs(val - asym) < 0.01
    s.num("An amplifier has H(jω) = 100/(1 + jω/10⁴) with ω in rad/s. What is |H| in dB at ω = 3×10⁵ rad/s?",
          val, "dB",
          f"DC gain: 20·log₁₀(100) = 40 dB. ω/ω_p = 30, so |H| = 100/√(1 + 900) = 100/30.02 = {g(H,4)}, which is {g(val)} dB.\n"
          f"Asymptotic check: 40 dB − 20·log₁₀(30) = 40 − 29.54 = {g(asym,4)} dB ✔ (a factor of 30 above the pole).\n"
          "Common mistake: forgetting to include the 40 dB DC gain (−29.5 dB).")
    w = 2000.0
    ph = math.degrees(-math.atan(w/100) - math.atan(w/1e4))
    Hc = 10/((1+1j*w/100)*(1+1j*w/1e4))
    assert close(ph, math.degrees(cmath.phase(Hc)), 1e-9)
    s.num("An amplifier has H(jω) = 10/[(1 + jω/100)(1 + jω/10⁴)] with ω in rad/s. What is the phase of H at ω = 2000 rad/s, in degrees (negative for lag)?",
          ph, "degrees",
          f"Phases of the denominator factors add, and the total phase is the NEGATIVE of their sum:\n"
          f"∠H = −tan⁻¹(2000/100) − tan⁻¹(2000/10⁴) = −tan⁻¹(20) − tan⁻¹(0.2) = −87.14° − 11.31° = {g(ph)}°.\n"
          "Common mistake: using only the first pole (−87.1°) or adding the factors with positive signs.",
          tol=0.02)
    # asymptotic gain at w=1000 for 1000/((1+s/10)(1+s/1000))
    asym = 60 - 20*math.log10(1000/10) - 0
    assert close(asym, 20)
    s.mc("An amplifier has H(jω) = 1000/[(1 + jω/10)(1 + jω/1000)] with ω in rad/s. According to the asymptotic Bode magnitude plot, what is |H| in dB at ω = 1000 rad/s?",
         "20 dB",
         ["60 dB", "40 dB", "0 dB"],
         "DC gain = 1000 = 60 dB. The plot is flat at 60 dB up to the first pole at ω = 10 rad/s.\n"
         "Between 10 and 1000 rad/s (two decades) the slope is −20 dB/decade, so the gain falls by 40 dB: 60 − 40 = 20 dB at ω = 1000 rad/s (just where the second pole starts to bend the curve).\n"
         "• 60 dB forgets the first pole.\n"
         "• 40 dB counts only one decade of roll-off.\n"
         "• 0 dB is not reached until about ω ≈ 3162 rad/s, after the −40 dB/decade section has taken another 20 dB off.")
    s.round(3)
    assert close(abs(1/(1+1j)**2), 0.5)
    s.mc("The transfer function H = 1/(1 + jω/ω_p)² has a double pole at ω_p. What is its actual magnitude at ω = ω_p, compared with the asymptotic Bode plot (which says 0 dB there)?",
         "−6 dB (twice the 3 dB error of a single pole)",
         ["−3 dB", "0 dB", "−40 dB"],
         "At ω = ω_p: H = 1/(1 + j)² = 1/(2j) ⇒ |H| = 0.5 ⇒ 20·log₁₀(0.5) = −6.02 dB. Each factor contributes the usual −3.01 dB error at its own break point, and the errors add in dB (the phase is −90° there).\n"
         "• −3 dB is the value for a single pole.\n"
         "• 0 dB is the asymptotic approximation, which ignores the error at the break point.\n"
         "• −40 dB/decade is the slope above ω_p, not a gain value at ω_p.")
    # RHP zero
    w = np.array([0.1, 1, 10, 100.0])
    Hl = 1 + 1j*w; Hr = 1 - 1j*w
    assert np.allclose(abs(Hl), abs(Hr))
    assert np.all(np.angle(Hl) > 0) and np.all(np.angle(Hr) < 0)
    s.mc("Compare a left-half-plane zero, H_L = 1 + jω/ω_z, with a right-half-plane zero, H_R = 1 − jω/ω_z (ω_z > 0). Which statement is correct?",
         "They have identical magnitude plots (rising at +20 dB/decade above ω_z), but H_R has phase going from 0° to −90° while H_L goes from 0° to +90°",
         ["H_R has a falling magnitude above ω_z, and its phase goes from 0° to +90°",
          "They have identical magnitudes and identical phases",
          "H_R has a flat magnitude, but its phase goes from 0° to −90°"],
         "|1 − jx| = |1 + jx| = √(1 + x²) for real x, so the magnitude plots are identical: flat, then rising +20 dB/decade above ω_z, with the same +3 dB error at ω_z.\n"
         "The phases differ in sign: ∠(1 + jx) = +tan⁻¹x, while ∠(1 − jx) = −tan⁻¹x. The RHP zero adds phase LAG while boosting gain, which is bad for stability: an RHP zero can't be spotted from a magnitude plot alone.\n"
         "The other options misstate either the magnitude slope or the phase sign.")
    w = 1000.0
    Hc = 10*(1+1j*w/100)/(1+1j*w/1000)
    ph = math.degrees(cmath.phase(Hc))
    assert close(ph, math.degrees(math.atan(10) - math.atan(1)))
    s.num("A circuit has H(jω) = 10(1 + jω/100)/(1 + jω/1000) with ω in rad/s. What is the EXACT phase of H at ω = 1000 rad/s, in degrees?",
          ph, "degrees",
          f"Numerator zero contributes +tan⁻¹(1000/100) = +tan⁻¹(10) = +84.29°.\n"
          f"Denominator pole contributes −tan⁻¹(1000/1000) = −45°.\n"
          f"Total: ∠H = 84.29° − 45° = {g(ph)}°.\n"
          "The straight-line (asymptotic) phase approximation would give roughly +90° − 45° = +45° here; the exact result differs by several degrees. Common mistake: adding the pole phase with a plus sign (129°).",
          tol=0.02)
    s.round(4)
    A0, fp = 1e5, 10.0
    # find f where |A| = 10
    f = fp*math.sqrt((A0/10)**2 - 1)
    s.num("Preview of gain-bandwidth. A later skill finds the bandwidth of a feedback amplifier from the op-amp's open-loop Bode plot. An op-amp has A(jf) = 10⁵/(1 + jf/10 Hz). Using the Bode plot (−20 dB/decade above the 10 Hz pole), at what frequency does |A| fall to 10 (20 dB), the closed-loop gain you want?",
          f, "Hz",
          f"DC gain = 10⁵ = 100 dB. From the 10 Hz pole, the gain falls 20 dB/decade. To go from 100 dB to 20 dB you need 80 dB = 4 decades: 10 Hz × 10⁴ = 10⁵ Hz.\n"
          f"Exact: |A| = 10 ⇒ √(1 + (f/10)²) = 10⁴ ⇒ f = {g(f,6)} Hz ≈ 100 kHz.\n"
          "Note that gain × frequency stays constant (10⁵ × 10 Hz = 10 × 10⁵ Hz = 10⁶ Hz): the 'gain-bandwidth product' of 1 MHz. Common mistake: counting only 80 dB/20 = 4 but multiplying by 4 instead of 10⁴.",
          preview=["gbw"])
    f = 20.0
    H = -20*(1j*f/20)/(1+1j*f/20)/(1+1j*f/200e3)
    val = dB(abs(H))
    s.num("Preview of coupling capacitors and frequency response. An AC-coupled amplifier has H(jf) = −20·[jf/(20 Hz)]/[1 + jf/(20 Hz)] · 1/[1 + jf/(200 kHz)]. What is |H| in dB at f = 20 Hz (the low corner)? (The 200 kHz pole is so far away that it contributes almost nothing.)",
          val, "dB",
          f"Mid-band gain: 20·log₁₀(20) = 26.02 dB. At the low corner f = 20 Hz, the high-pass factor jf/f_L/(1 + jf/f_L) = j/(1 + j) has magnitude 0.7071 (−3.01 dB). The 200 kHz pole's factor is 1/√(1 + 10⁻⁸) ≈ 1.\n"
          f"|H| = 20 × 0.7071 = 14.14 → {g(val)} dB (26.02 − 3.01).\n"
          "Common mistake: reading the mid-band 26 dB as the gain at the corner; the corner is by definition 3 dB below mid-band.",
          preview=["freq-basics"])
    w = 1e6
    L = 1000/((1+1j*w/1e3)*(1+1j*w/1e7))
    ph = math.degrees(cmath.phase(L))
    assert close(ph, -math.degrees(math.atan(1000)+math.atan(0.1)), 1e-9)
    s.num("Preview of stability. A later skill checks how close a feedback loop's phase is to −180° when its gain falls to 1. A loop gain is L(jω) = 1000/[(1 + jω/10³)(1 + jω/10⁷)] (ω in rad/s). By the asymptotic Bode magnitude, |L| ≈ 1 near ω = 10⁶ rad/s. What is the exact phase of L at ω = 10⁶ rad/s, in degrees?",
          ph, "degrees",
          "The phase of a product is the sum of phases: ∠L = −tan⁻¹(10⁶/10³) − tan⁻¹(10⁶/10⁷) = −tan⁻¹(1000) − tan⁻¹(0.1) = −89.94° − 5.71° = −95.65°.\n"
          "The first pole alone already gives almost −90°, and the distant second pole adds about −6°. The loop is still ≈ 84° away from −180° at this frequency: a comfortable margin (compare with a loop whose second pole sits at 10⁶ rad/s: −89.9° − 45° = −135°).\n"
          "Common mistake: assuming the distant pole contributes nothing, or using degrees for the arithmetic of ω ratios.",
          preview=["stability"], tol=0.02)
    return s
