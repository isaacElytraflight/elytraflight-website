from qlib import *

def build():
    s = Skill('step-resp')
    s.round(1)
    s.mc("A voltage step (0 V to V_s at t = 0) is applied to an RC low-pass filter with the capacitor initially discharged. What is the output v_o(t) for t > 0?",
         "v_o(t) = V_s(1 − e^(−t/τ))",
         ["v_o(t) = V_s·e^(−t/τ)", "v_o(t) = V_s(1 − e^(−tτ))", "v_o(t) = V_s immediately, with no delay"],
         "The step response is V_s(1 − e^(−t/τ)) (reader Eq. 1.82): it starts at 0 and rises exponentially toward V_s.\n"
         "• V_s e^(−t/τ) is a decay starting at V_s (the response of a charged capacitor discharging, or the impulse response shape).\n"
         "• The exponent must be −t/τ (dimensionless), not −tτ.\n"
         "• A capacitor voltage cannot change instantly through a resistor, so the output smooths the step.")
    s.mc("After a step is applied to an RC low-pass filter, how long does the output take to reach about 63% of its final value?",
         "One time constant, t = τ = RC",
         ["Two time constants, t = 2τ", "t = τ/2", "It takes exactly 5τ"],
         "At t = τ: 1 − e^(−1) = 0.632, i.e., about 63% of the final value. After 2τ it is 86.5%, after 5τ it is 99.3% (essentially settled).")
    tau, V, t = 0.47e-3, 5.0, 1.41e-3
    v = V*(1-math.exp(-t/tau))
    s.num("An RC low-pass has R = 10 kΩ and C = 47 nF, with the capacitor initially discharged. A 5 V step is applied at t = 0. What is the output at t = 1.41 ms?",
          v, "V",
          f"τ = RC = 10 kΩ × 47 nF = 0.47 ms. The time t = 1.41 ms is exactly 3τ.\n"
          f"v_o = 5(1 − e^(−3)) = 5(1 − 0.0498) = {g(v)} V.")
    s.round(2)
    tau, V, w = 1e-3, 5.0, 2e-3
    v_end = V*(1-math.exp(-w/tau))
    v3 = v_end*math.exp(-1e-3/tau)
    chk = V*(1-math.exp(-3e-3/tau)) - V*(1-math.exp(-(3e-3-w)/tau))
    assert close(v3, chk)
    s.num("An RC low-pass filter with τ = 1 ms (capacitor initially discharged) receives a 5 V pulse of width 2 ms (5 V from t = 0 to 2 ms, then back to 0 V). What is the output at t = 3 ms?",
          v3, "V",
          "Phase 1 (0 < t < 2 ms): v_o = 5(1 − e^(−t/τ)). At t = 2 ms: v_o = 5(1 − e^(−2)) = 4.323 V.\n"
          f"Phase 2 (t > 2 ms): the input is 0, so the capacitor discharges from 4.323 V: v_o = 4.323·e^(−(t − 2 ms)/τ). At t = 3 ms: 4.323 × e^(−1) = {g(v3)} V.\n"
          f"Check by superposition: a pulse is a step minus a delayed step: 5(1 − e^(−3)) − 5(1 − e^(−1)) = 4.751 − 3.161 = {g(chk)} V ✔.\n"
          "Common mistake: restarting the clock and using 4.323 e^(−3), or continuing to charge toward 5 V.")
    s.mc("An RC low-pass filter has time constant τ and starts discharged. A 2 V step is applied at t = t₀ (not at t = 0). What is v_o(t) for t > t₀?",
         "2(1 − e^(−(t − t₀)/τ))",
         ["2(1 − e^(−t/τ))", "(1 − e^(−(t − t₀)/τ))", "2(1 − e^(−(t − t₀)τ))"],
         "Time invariance: delaying the input by t₀ delays the output by t₀, so t is replaced by t − t₀ in the exponent. Linearity scales the unit-step response by 2.\n"
         "• 2(1 − e^(−t/τ)) forgets the delay (the output would start rising before the step arrives).\n"
         "• Dropping the factor of 2 is the response to a 1 V step.\n"
         "• The exponent needs division by τ, not multiplication.")
    tau = 0.5e-3
    t90 = tau*math.log(10)
    assert close(1-math.exp(-t90/tau), 0.9)
    s.num("An RC low-pass filter has τ = 0.5 ms. After a step input from rest, how long does the output take to reach 90% of its final value?",
          t90*1e3, "ms",
          f"1 − e^(−t/τ) = 0.9 ⇒ e^(−t/τ) = 0.1 ⇒ t = τ ln 10 = 2.303τ.\n"
          f"t = 2.303 × 0.5 ms = {g(t90*1e3)} ms.\n"
          "Common mistake: answering t = τ = 0.5 ms (that is the 63% point).")
    s.round(3)
    V, w, tau = 5.0, 10e-6, 1e-3
    peak = V*(1 - math.exp(-w/tau))
    s.mc("A 5 V pulse of width 10 µs drives an RC low-pass with τ = 1 ms (capacitor initially discharged). Roughly what is the peak output voltage?",
         "About 50 mV (≈ 5 V × 10 µs / 1 ms)",
         ["5 V, because the input reaches 5 V", "About 3.2 V (63% of 5 V)", "About 0.5 V"],
         f"The pulse is much shorter than τ, so the capacitor barely charges. Exact: peak = 5(1 − e^(−0.01)) = {g(peak*1e3)} mV, which is ≈ 5 × (10 µs/1 ms) = 50 mV (using 1 − e^(−x) ≈ x for small x).\n"
         "The filter output looks like a scaled copy of the impulse response, with size set by the pulse AREA (5 V × 10 µs) divided by τ.\n"
         "• 5 V would need the pulse to last many time constants.\n"
         "• 63% applies only after one full τ of input.\n"
         "• 0.5 V is 10 times too large (would be a 100 µs pulse).")
    s.mc("An RC low-pass filter's capacitor starts at 2 V when a step input of 5 V is applied (τ = RC). What is v_o(t) for t ≥ 0?",
         "5 − 3e^(−t/τ)",
         ["5(1 − e^(−t/τ))", "5 − 2e^(−t/τ)", "2 + 5(1 − e^(−t/τ))"],
         "General first-order response: v(t) = v_final + (v_initial − v_final)e^(−t/τ) = 5 + (2 − 5)e^(−t/τ) = 5 − 3e^(−t/τ). It starts at 2 V and approaches 5 V.\n"
         "• 5(1 − e^(−t/τ)) starts at 0 V (assumes the capacitor was discharged).\n"
         "• 5 − 2e^(−t/τ) uses the initial voltage rather than the initial DISTANCE to the final value (starts at 3 V).\n"
         "• 2 + 5(1 − e^(−t/τ)) heads to 7 V: the step contributes only the 3 V difference, not the full 5 V.")
    tau, V = 0.25e-3, 5.0
    slope = V/tau/1e3
    # numeric derivative check
    dt = 1e-9
    num = (V*(1-math.exp(-dt/tau)) - 0)/dt/1e3
    assert close(num, slope, 1e-4)
    s.num("An RC low-pass filter with τ = 0.25 ms (capacitor discharged) receives a 5 V step at t = 0. What is the slope dv_o/dt of the output immediately after t = 0?",
          slope, "V/ms",
          "From the circuit equation v_o + τ dv_o/dt = v_s: at t = 0⁺, v_o = 0 and v_s = 5 V, so dv_o/dt = (v_s − v_o)/τ = 5/0.25 ms = 20 V/ms.\n"
          "Equivalent view: the tangent at t = 0 would reach the final value 5 V after exactly one time constant (5 V ÷ 0.25 ms). Common mistake: using the average rate over the first τ, or 5 V/ms.")
    s.round(4)
    R1, R2, C = 1e3, 4e3, 2e-9
    Rth = R1*R2/(R1+R2); tau = Rth*C
    t90 = tau*math.log(10)
    s.num("Preview of open-circuit time constants. A later skill finds a circuit's time constant as τ = R_th·C, where R_th is the resistance seen by the capacitor with the independent sources turned off. A node has C = 2 nF, with 1 kΩ and 4 kΩ resistors connecting it to the source and to ground (the source is an ideal voltage source). After a step, how long does the voltage across C take to reach 90% of its final value?",
          t90*1e6, "µs",
          f"With the source off (a short), the capacitor sees 1 kΩ ∥ 4 kΩ = {g(Rth)} Ω.\n"
          f"τ = R_th·C = 800 Ω × 2 nF = 1.6 µs. Reaching 90% takes t = τ ln 10 = 2.303τ = {g(t90*1e6)} µs.\n"
          "Common mistake: using R₁ + R₂ = 5 kΩ (a series sum) instead of the parallel combination.",
          preview=["octc"])
    SR, tau = 0.5e6, 2e-6
    Vmax = SR*tau
    s.num("Preview of slew rate. An op-amp stage that follows an RC filter (τ = 2 µs) can only change its output by at most SR = 0.5 V/µs. The filter's output has its steepest slope, V_s/τ, right after a step of height V_s. What is the largest step V_s that keeps the maximum slope within the slew-rate limit?",
          Vmax, "V",
          "Maximum slope of the step response: (dv_o/dt) at t = 0⁺ = V_s/τ. Require V_s/τ ≤ SR ⇒ V_s ≤ SR·τ = (0.5 V/µs)(2 µs) = 1 V.\n"
          "Larger steps force the amplifier into slewing (a straight-line ramp) instead of the clean exponential. Common mistake: using τ in the wrong place (V_s ≤ SR/τ gives nonsense units).",
          preview=["slew"])
    Ro, CL = 10e3, 50e-12
    tau = Ro*CL
    ts = tau*math.log(100)
    s.num("Preview of capacitive loading. A common-source amplifier's output node behaves, for small signals, like an RC low-pass with R_o = 10 kΩ driving a load capacitance C_L = 50 pF. After a small input step, how long does the output take to settle to within 1% of its final value?",
          ts*1e6, "µs",
          f"τ = R_o·C_L = 10 kΩ × 50 pF = 0.5 µs. Within 1% means e^(−t/τ) = 0.01 ⇒ t = τ ln 100 = 4.605τ.\n"
          f"t = 4.605 × 0.5 µs = {g(ts*1e6)} µs.\n"
          "Common mistake: using 1τ = 0.5 µs (that is the 63% point, not 1% settling).",
          preview=["cs-cap-load"])
    return s
