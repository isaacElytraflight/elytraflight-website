from qlib import *

def build():
    s = Skill('rc-lpf')
    s.round(1)
    s.mc("A source drives a series resistor R, and the output is taken across a capacitor C to ground (the RC low-pass filter). What is its time constant τ?",
         "τ = RC",
         ["τ = R/C", "τ = 1/(RC)", "τ = R + C"],
         "The governing equation is v_o = v_s − τ·dv_o/dt with τ = RC (reader Eq. 1.2). Units: Ω·F = seconds. R/C and R + C do not have units of time, and 1/(RC) is the corner (angular) frequency, not the time constant.")
    s.mc("A sinusoidal source with a very low frequency (ω ≪ 1/RC) drives the RC low-pass filter (output across C). What does the output look like?",
         "Almost the same as the input: about the same amplitude and nearly zero phase shift",
         ["Nearly zero amplitude, because the capacitor shorts the signal",
          "Same amplitude but delayed by 90°",
          "Twice the input amplitude"],
         "At low frequency the capacitor's current is tiny, so there is almost no voltage across R and v_o ≈ v_s: the signal passes undisturbed (reader Sec. 1.2.2).\n"
         "• Near-zero output happens at HIGH frequency, where the capacitor shorts the signal.\n"
         "• A 90° lag is the asymptotic phase at very HIGH frequency.\n"
         "• A passive RC filter cannot amplify.")
    R, C = 10e3, 10e-9
    fc = 1/(2*math.pi*R*C)
    s.num("An RC low-pass filter has R = 10 kΩ and C = 10 nF. What is its cutoff (−3 dB) frequency f_c = 1/(2πRC)?",
          fc, "Hz",
          f"τ = RC = 10 kΩ × 10 nF = 100 µs. ω_c = 1/τ = 10,000 rad/s, so f_c = ω_c/(2π) = 10,000/6.2832 = {g(fc)} Hz.\n"
          "Common mistake: quoting 1/τ = 10,000 as Hz; that is rad/s. You must divide by 2π.")
    # ---------- R2
    s.round(2)
    R, C, Vs = 2e3, 500e-9, 5.0
    tau = R*C
    t = 2e-3
    v = Vs*(1 - math.exp(-t/tau))
    # independent check: forward Euler of ODE
    dt = 1e-7; vo = 0.0
    for _ in range(int(round(t/dt))):
        vo += dt*(Vs - vo)/tau
    assert abs(vo - v) < 5e-3, (vo, v)
    s.num("An RC low-pass filter has R = 2 kΩ and C = 500 nF. The capacitor starts discharged, and at t = 0 the source steps from 0 V to 5 V. What is v_o at t = 2 ms?",
          v, "V",
          f"τ = RC = 2 kΩ × 500 nF = 1 ms. Step response: v_o(t) = V_s(1 − e^(−t/τ)).\n"
          f"At t = 2 ms = 2τ: v_o = 5(1 − e^(−2)) = 5(1 − 0.1353) = {g(v)} V.\n"
          "Common mistakes: 5e^(−2) = 0.68 V (using the decay instead of the rise), or 5(1 − e^(−1)) = 3.16 V (using t = τ).")
    tau = 100e-6; w = 20e3; Vin = 3.0
    amp = Vin/math.sqrt(1 + (w*tau)**2)
    chk = Vin*abs(1/(1 + 1j*w*tau))
    assert close(amp, chk)
    s.num("An RC low-pass filter has τ = RC = 100 µs. It is driven by v_s = 3cos(ωt) volts with ω = 20 krad/s. What is the steady-state amplitude of v_o?",
          amp, "V",
          f"ωτ = 20,000 × 100 µs = 2. Amplitude response: |V_o/V_s| = 1/√(1 + (ωτ)²) = 1/√5 = {g(1/math.sqrt(5))}.\n"
          f"Output amplitude = 3 V × 0.4472 = {g(amp)} V (and the phase is −tan⁻¹(2) = −63.4°).\n"
          "Common mistake: using 1/(1 + ωτ) = 1/3 (forgetting the square root of the sum of squares), which gives 1.0 V.")
    s.mc("An RC low-pass filter is driven by a sinusoid whose angular frequency is exactly ω = 1/τ. Compared with the input, the steady-state output has…",
         "amplitude 0.707 × input and a phase lag of 45°",
         ["amplitude 0.5 × input and a phase lag of 45°",
          "amplitude 0.707 × input and a phase LEAD of 45°",
          "amplitude 0.707 × input and a phase lag of 90°"],
         "With ωτ = 1: |H| = 1/√(1 + 1) = 0.707 (−3 dB, half the power) and ∠H = −tan⁻¹(1) = −45° (a lag).\n"
         "• 0.5 is the magnitude of a half-voltage point, not the −3 dB point.\n"
         "• The low-pass output lags the input; a lead would be for a high-pass.\n"
         "• 90° lag is only reached asymptotically at very high frequency.")
    # ---------- R3
    s.round(3)
    s.mc("The RC low-pass filter starts with the capacitor uncharged (v_o(0) = 0). At t = 0, a source v_s = V_s cos(ωt) is connected. Which description of v_o(t) for t ≥ 0 is correct?",
         "v_o(t) = steady-state sinusoid + a decaying transient K·e^(−t/τ), with K chosen so that v_o(0) = 0",
         ["v_o(t) is exactly the steady-state sinusoid |H|V_s cos(ωt + φ) for all t ≥ 0, since the input is a sinusoid",
          "v_o(t) = steady-state sinusoid + a transient that decays with time constant 1/ω",
          "v_o(t) = steady-state sinusoid + a sinusoidal transient at frequency 1/τ that never decays"],
         "The ODE v_o + τ dv_o/dt = v_s has a particular solution (the sinusoidal steady state) plus a homogeneous solution K·e^(−t/τ) that depends on the filter, not the source. The initial condition v_o(0) = 0 fixes K = −(steady-state value at t = 0).\n"
         "• The pure sinusoid would have v_o(0) = |H|V_s cos φ ≠ 0, which would require the capacitor voltage to jump (impossible).\n"
         "• The transient's time constant is τ = RC, a property of the circuit, not 1/ω.\n"
         "• The homogeneous solution is a real decaying exponential, not an undamped oscillation.\n"
         "This is why the complex-exponential method gives only the steady state.")
    R, C = 10e3, 1e-9
    tau = R*C
    tr = tau*(math.log(0.9/0.1) if False else math.log(9))  # t90 - t10 = tau*ln(0.9/0.1)... computed below exactly
    t10 = -tau*math.log(1-0.1); t90 = -tau*math.log(1-0.9)
    tr = t90 - t10
    assert close(tr, tau*math.log(9))
    s.num("An RC low-pass filter has R = 10 kΩ and C = 1 nF. A step is applied and the output rises toward its final value. What is the 10%–90% rise time of the output?",
          tr*1e6, "µs",
          f"τ = RC = 10 µs. The step response is v_o = V_f(1 − e^(−t/τ)).\n"
          f"10% point: t₁₀ = −τ ln(0.9) = {g(t10*1e6)} µs. 90% point: t₉₀ = −τ ln(0.1) = {g(t90*1e6)} µs.\n"
          f"Rise time = t₉₀ − t₁₀ = τ ln 9 = 2.197τ = {g(tr*1e6)} µs.\n"
          "Common mistakes: answering τ = 10 µs (that is the 63% time), or t₉₀ = 2.303τ = 23.0 µs (measured from t = 0 rather than from the 10% point).")
    Vs, R, RL, C = 10.0, 1e3, 1e3, 1e-6
    vf = Vs*RL/(R+RL); tau_l = (R*RL/(R+RL))*C
    assert vf == 5 and close(tau_l, 0.5e-3)
    s.mc("An RC low-pass filter (R = 1 kΩ, C = 1 µF) now has a load resistor R_L = 1 kΩ connected in parallel with C. The capacitor starts discharged and a 10 V step is applied. What are the final output voltage and the time constant?",
         "Final value 5 V, time constant 0.5 ms",
         ["Final value 10 V, time constant 1 ms",
          "Final value 5 V, time constant 1 ms",
          "Final value 10 V, time constant 0.5 ms"],
         "At DC the capacitor is an open circuit, so R and R_L form a divider: V_final = 10 × 1k/(1k + 1k) = 5 V (the load drains current, so the output no longer reaches 10 V).\n"
         "The resistance seen by the capacitor (source shorted) is R ∥ R_L = 500 Ω, so τ = (R ∥ R_L)C = 500 Ω × 1 µF = 0.5 ms.\n"
         "• '10 V, 1 ms' ignores the load completely.\n"
         "• '5 V, 1 ms' gets the divider but uses R instead of R ∥ R_L.\n"
         "• '10 V, 0.5 ms' gets the faster τ but misses the divider.")
    # ---------- R4
    s.round(4)
    tau = 1e3*159e-9; w = 2*math.pi*1000
    H = 1/(1 + 1j*w*tau)
    amp = 2*abs(H)
    assert close(amp, 2/math.sqrt(1+(w*tau)**2))
    s.num("Preview of sinusoidal steady state. A later skill shows that replacing d/dt by jω in the RC filter equation gives H(jω) = V_o/V_s = 1/(1 + jωRC). Take R = 1 kΩ, C = 159 nF and a source 2cos(2π·1000·t) V. What is the steady-state amplitude of v_o?",
          amp, "V",
          f"τ = RC = 1 kΩ × 159 nF = 159 µs. ω = 2π·1000 = 6283 rad/s, so ωτ = {g(w*tau,4)} ≈ 1.\n"
          f"|H| = 1/√(1 + (ωτ)²) = {g(abs(H),4)}, so the amplitude is 2 × {g(abs(H),4)} = {g(amp)} V.\n"
          f"The phase is ∠H = −tan⁻¹(ωτ) = {g(math.degrees(cmath.phase(H)),4)}° ≈ −45°: this is the 'corner frequency' case (f_c = 1/(2πRC) ≈ 1 kHz).",
          preview=["sinusoid-resp"])
    R, C = 2.2e3, 10e-9
    t50 = R*C*math.log(2)
    s.num("Preview of step response. A later skill uses the step response to measure delay. For an RC low-pass filter with R = 2.2 kΩ and C = 10 nF, the output is v_o = V_f(1 − e^(−t/RC)) after a step. How long does the output take to reach 50% of its final value?",
          t50*1e6, "µs",
          f"Set 1 − e^(−t/τ) = 0.5 ⇒ e^(−t/τ) = 0.5 ⇒ t = τ ln 2 = 0.693τ.\n"
          f"τ = RC = 2.2 kΩ × 10 nF = 22 µs, so t₅₀ = 0.693 × 22 µs = {g(t50*1e6)} µs.\n"
          "Common mistake: using t = τ (that is the 63.2% point).",
          preview=["step-resp"])
    # design: want |H| = 0.1 at 10 kHz
    w = 2*math.pi*1e4
    wt = math.sqrt(1/0.1**2 - 1)
    tau = wt/w
    chk = 1/math.sqrt(1+(w*tau)**2)
    assert close(chk, 0.1)
    s.num("Preview of Bode plots. A later skill plots |H| in decibels, dB = 20·log₁₀|V_o/V_s|. You want an RC low-pass filter to attenuate a 10 kHz tone by 20 dB (output amplitude = 0.1 × input). Using |H| = 1/√(1 + (ωτ)²), what time constant τ = RC is required?",
          tau*1e6, "µs",
          f"−20 dB means |H| = 10^(−20/20) = 0.1.\n"
          f"1/√(1 + (ωτ)²) = 0.1 ⇒ 1 + (ωτ)² = 100 ⇒ ωτ = √99 = {g(wt)}.\n"
          f"ω = 2π × 10 kHz = 62,832 rad/s ⇒ τ = {g(wt)}/62,832 = {g(tau*1e6)} µs.\n"
          "Common mistake: using the high-frequency approximation ωτ ≈ 10, which gives τ = 159.2 µs; it is within 0.5%, but the exact relation includes the '1 +' term.",
          preview=["bode"])
    return s
