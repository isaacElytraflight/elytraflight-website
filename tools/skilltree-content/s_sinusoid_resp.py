from qlib import *

def build():
    s = Skill('sinusoid-resp')
    s.round(1)
    s.mc("An LTI circuit is driven by cos(ωt). In sinusoidal steady state, its output is…",
         "a sinusoid at the same frequency ω, with a different amplitude and phase",
         ["a sinusoid at frequency 2ω with the same amplitude",
          "a sinusoid at the same frequency with exactly the same amplitude and phase",
          "a constant (DC) voltage"],
         "Sinusoids/complex exponentials are eigenfunctions of LTI systems: the output is the input scaled by a complex number H(jω), which changes only the amplitude (by |H|) and the phase (by ∠H) (reader Fig. 1.6).\n"
         "LTI circuits never change the frequency, and they only leave amplitude and phase untouched if H = 1.")
    s.mc("What is d/dt of the complex exponential e^(jωt)?",
         "jω·e^(jωt)",
         ["e^(jωt)/(jω)", "ω·e^(jωt)", "−jω·e^(−jωt)"],
         "d/dt e^(jωt) = jω e^(jωt) (reader Eq. 1.27). That is why derivatives become multiplications by jω and integrals become divisions by jω.\n"
         "• e^(jωt)/(jω) is the INTEGRAL.\n"
         "• Dropping the j loses the 90° rotation.\n"
         "• −jω e^(−jωt) is the derivative of e^(−jωt), not e^(jωt).")
    tau, w, Vs = 1e-3, 1000.0, 10.0
    a = Vs/math.sqrt(1+(w*tau)**2)
    s.num("An RC low-pass filter with τ = 1 ms is driven by v_s = 10cos(ωt) V with ω = 1000 rad/s. What is the steady-state amplitude of v_o? (Use H(jω) = 1/(1 + jωτ).)",
          a, "V",
          f"ωτ = 1000 × 1 ms = 1. |H| = 1/|1 + j1| = 1/√2 = 0.7071. Output amplitude = 10 × 0.7071 = {g(a)} V.")
    s.round(2)
    # 2 y' + 3 y = x ; x amp 6 V ; w=1.5
    w = 1.5
    H = 1/(3 + 2j*w)
    a = 6*abs(H)
    assert close(a, 6/(3*math.sqrt(2)))
    s.num("A linear circuit obeys 2·dy/dt + 3y = x(t), with x(t) = 6cos(1.5t) V (t in seconds). What is the steady-state amplitude of y?",
          a, "V",
          "Let x = X e^(jωt) and y = Y e^(jωt). Then d/dt → jω: 2jωY + 3Y = X ⇒ H(jω) = Y/X = 1/(3 + j2ω).\n"
          f"At ω = 1.5: H = 1/(3 + j3), |H| = 1/√(9 + 9) = 1/(3√2) = {g(abs(H),4)}.\n"
          f"Amplitude = 6 × {g(abs(H),4)} = {g(a)} V (phase −45°).\n"
          "Common mistake: forgetting the 2 in 2jω (using 3 + jω = 3 + j1.5 gives amplitude 1.79 V).")
    tau, f = 2e-3, 250.0
    w = 2*math.pi*f
    ph = -math.degrees(math.atan(w*tau))
    assert close(ph, math.degrees(cmath.phase(1/(1+1j*w*tau))))
    s.num("A first-order low-pass has H(jω) = 1/(1 + jωτ) with τ = 2 ms. For a 250 Hz sinusoid, what is the phase of the output relative to the input, in degrees? (Give a negative number for a lag.)",
          ph, "degrees",
          f"ω = 2π·250 = 1570.8 rad/s, so ωτ = 1570.8 × 0.002 = {g(w*tau)}.\n"
          f"∠H = −tan⁻¹(ωτ) = −tan⁻¹({g(w*tau)}) = {g(ph)}°.\n"
          "Common mistake: using f instead of ω (ωτ = 0.5 gives −26.6°), forgetting the 2π.",
          tol=0.02)
    s.mc("A circuit obeys d²y/dt² + 3·dy/dt + 2y = x(t). Using complex exponentials, which expression is H(jω) = Y/X?",
         "1/((2 − ω²) + j3ω)",
         ["1/((2 + ω²) + j3ω)", "1/((2 − ω²) + 3ω)", "1/(2 + j3ω − jω²)"],
         "Substitute x = Xe^(jωt), y = Ye^(jωt): d/dt → jω and d²/dt² → (jω)² = −ω². Then (−ω² + j3ω + 2)Y = X, so H = 1/((2 − ω²) + j3ω).\n"
         "• (jω)² = −ω², not +ω² (first wrong choice).\n"
         "• The first-derivative term keeps its j (second wrong choice dropped it).\n"
         "• The second derivative gives −ω², which is REAL; it is not −jω² (third wrong choice).")
    s.round(3)
    s.mc("For a circuit made only of real-valued R, L and C elements, H(jω) = 1/(1 + jωτ). What is H(−jω) (the response to the complex exponential e^(−jωt))?",
         "1/(1 − jωτ), the complex conjugate of H(jω)",
         ["−1/(1 + jωτ)", "1/(1 + jωτ), identical to H(jω)", "−1/(1 − jωτ)"],
         "H(−ω) is found by replacing ω with −ω everywhere: 1/(1 + j(−ω)τ) = 1/(1 − jωτ) = H(jω)*.\n"
         "This is not an accident: for a real circuit, |H(−ω)| = |H(ω)| (even) and ∠H(−ω) = −∠H(ω) (odd) (reader Eqs. 1.49–1.50). It is what makes the output of a real input come out real: H(ω)e^(jωt)/2 + H(−ω)e^(−jωt)/2 is a sum of conjugates.\n"
         "The other choices change the magnitude's sign or keep the phase unchanged.")
    # HPF with DC + AC input
    tau = 1.0; w = 1.0
    Hh = 1j*w*tau/(1+1j*w*tau)
    amp = 2*abs(Hh); ph = math.degrees(cmath.phase(Hh))
    assert close(amp, 1.41421356, 1e-6) and close(ph, 45)
    s.mc("A high-pass circuit has H(jω) = jωτ/(1 + jωτ). It is driven by x(t) = 5 + 2cos(ωt) volts, where ωτ = 1. Which steady-state output is correct?",
         "1.414cos(ωt + 45°) V, with no DC component",
         ["3.54 + 1.414cos(ωt + 45°) V",
          "5 + 1.414cos(ωt + 45°) V",
          "1.414cos(ωt − 45°) V"],
         "Superposition: the DC term (ω = 0) and the AC term are treated separately, each multiplied by H at its own frequency.\n"
         "• DC: H(0) = 0, so the 5 V offset is completely blocked.\n"
         "• AC at ωτ = 1: H = j/(1 + j) = (1/√2)∠45°, so the output is 2 × 0.7071 cos(ωt + 45°) = 1.414cos(ωt + 45°).\n"
         "Mistakes: scaling the DC by |H(jω)| = 0.707 (giving 3.54 V) or passing it unchanged (5 V); a high-pass leads, not lags (phase +45°, not −45°).")
    tau, w = 1e-3, 1000.0
    Hh = 1/(1+1j*w*tau)
    val = 10*abs(Hh)*math.sin(math.radians(-45))
    assert close(val, -5, 1e-6)
    s.num("An RC low-pass filter with τ = 1 ms is driven by v_s(t) = 10sin(ωt) V with ω = 1000 rad/s. In sinusoidal steady state, what is the output voltage v_o at exactly t = 0?",
          val, "V",
          "The filter has H = 1/(1 + j) = 0.7071∠−45°. A sine is just a cosine shifted by 90°, and H applies the same amplitude scaling and phase shift to it:\n"
          "v_o(t) = 10(0.7071) sin(ωt − 45°) = 7.071 sin(ωt − 45°).\n"
          "At t = 0: 7.071 × sin(−45°) = 7.071 × (−0.7071) = −5.0 V.\n"
          "Common mistake: answering 0 V because 'sin(0) = 0'. The input is zero at t = 0, but the output is delayed by 45°, so it is not.")
    s.round(4)
    w = 1000.0; C = 2e-6; R = 1e3; I = 0.1e-3
    Z = 1/(1/R + 1j*w*C)
    v = I*abs(Z)*1e3
    # check by solving ODE C dv/dt + v/R = i via complex exp
    Vc = I/(1/R + 1j*w*C)
    assert close(abs(Vc)*1e3, v)
    s.num("Preview of transfer functions. A photodiode current i_in = 0.1cos(ωt) mA flows into a node where a 1 kΩ resistor R and a 2 µF capacitor C are in parallel to ground; the node voltage obeys C·dv/dt + v/R = i_in. For ω = 1000 rad/s, find the steady-state amplitude of v. (A later skill calls V/I a transimpedance.)",
          v, "mV",
          "Let v = V e^(jωt), i_in = I e^(jωt): d/dt → jω gives (jωC + 1/R)V = I.\n"
          f"V/I = 1/(1/R + jωC) = 1/(0.001 + j0.002) Ω, whose magnitude is 1/√(0.001² + 0.002²) = 1/0.002236 = {g(abs(Z))} Ω (phase −63.4°).\n"
          f"|V| = 0.1 mA × {g(abs(Z))} Ω = {g(v)} mV.\n"
          "Common mistake: using R alone (100 mV), ignoring that the capacitor shunts part of the current.",
          preview=["tf"])
    f = 2000.0
    tau = 1/(2*math.pi*f)
    s.num("Preview of the frequency-domain view of systems. A lab measurement of an RC-type low-pass shows that its output lags its input by exactly 45° at f = 2 kHz. For H(jω) = 1/(1 + jωτ), the phase is −tan⁻¹(ωτ). What is the time constant τ?",
          tau*1e6, "µs",
          "−tan⁻¹(ωτ) = −45° ⇒ ωτ = tan 45° = 1 ⇒ τ = 1/ω.\n"
          f"ω = 2π × 2000 = 12,566 rad/s, so τ = 1/12,566 = {g(tau*1e6)} µs.\n"
          "This 'find the corner from the 45° point' is a standard way to identify a first-order system from sinusoidal measurements. Common mistake: τ = 1/f = 500 µs (forgetting 2π).",
          preview=["freq-char"])
    w = 1e4; w1, w2 = 1e3, 1e5
    Hc = 1/((1+1j*w/w1)*(1+1j*w/w2))
    amp = 2*abs(Hc)
    assert close(abs(Hc), 1/(math.sqrt(101)*math.sqrt(1.01)))
    s.num("Preview of Bode plots. A cascade of two buffered low-pass stages has H(jω) = 1/[(1 + jω/ω₁)(1 + jω/ω₂)] with ω₁ = 10³ rad/s and ω₂ = 10⁵ rad/s. For the input 2cos(ωt) V at ω = 10⁴ rad/s, what is the steady-state output amplitude? (Magnitudes of a product multiply.)",
          amp, "V",
          f"|1 + jω/ω₁| = |1 + j10| = √101 = 10.05; |1 + jω/ω₂| = |1 + j0.1| = √1.01 = 1.005.\n"
          f"|H| = 1/(10.05 × 1.005) = {g(abs(Hc),4)}. Amplitude = 2 × {g(abs(Hc),4)} = {g(amp)} V.\n"
          "Notice the first pole does almost all the work; the second pole (still ten times away) only trims about 0.5%. This is the kind of reasoning that makes Bode plots fast.",
          preview=["bode", "pole-zero"])
    return s
