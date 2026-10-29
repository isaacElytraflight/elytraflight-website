from qlib import *

def build():
    s = Skill('tf')
    s.round(1)
    s.mc("The voltage transfer function (voltage gain) of a circuit at frequency ω is defined as…",
         "G_v(jω) = V_out/V_in, a complex number (ratio of output and input phasors)",
         ["G_v = V_out × V_in, a real number in volts squared",
          "G_v = I_out/I_in, a ratio of currents",
          "G_v = V_out − V_in, the voltage drop in volts"],
         "A transfer function is the ratio of an output phasor to an input phasor (reader Sec. 2.2). For voltage gain, G_v = V₂/V₁ = (|V₂|/|V₁|)e^(j(φ₂ − φ₁)). Its magnitude is the amplitude ratio and its angle is the phase shift.\n"
         "• The product of voltages is not a ratio and has units of V².\n"
         "• The ratio of currents is the CURRENT gain, G_i.\n"
         "• A difference is not a transfer function.")
    s.mc("A transimpedance amplifier (TIA) converts an input current into an output voltage. What are the units of its transfer function V_out/I_in?",
         "Ohms (Ω)",
         ["Siemens (S)", "Unitless (V/V)", "Watts (W)"],
         "Volts divided by amps is ohms, so the transfer function is an impedance-like quantity: a 'trans-impedance' (reader Eq. 2.6).\n"
         "• Siemens (A/V) is for a trans-ADMITTANCE (output current/input voltage).\n"
         "• V/V is a voltage gain; A/A would be a current gain.\n"
         "• Watts would be for power, not a ratio of signals.")
    g_ = 0.5/2e-3
    s.num("An amplifier is driven with a 2 mV amplitude sinusoid and the output amplitude is 0.5 V. What is the magnitude of its voltage gain |G_v|?",
          g_, "V/V",
          "|G_v| = |V_out|/|V_in| = 0.5 V / 0.002 V = 250. Since |G_v| > 1 the circuit has voltage gain (if it were below 1 it would attenuate). Common mistake: dividing in mV and V without converting units (0.5/2 = 0.25).")
    s.round(2)
    K = 5e-3/0.25
    s.num("A circuit has an input voltage amplitude of 250 mV and produces an output CURRENT amplitude of 5 mA. What is the magnitude of its transadmittance K = I_out/V_in? (Answer in millisiemens, mS.)",
          K*1e3, "mS",
          "K = I₂/V₁ = 5 mA / 0.25 V = 0.02 S = 20 mS. A transadmittance has units of siemens (A/V). Common mistake: dividing 0.25/5 (giving 50, i.e., Ω instead of S).")
    mag, ph = 0.8, -30.0
    out_t0 = 5*mag*math.cos(math.radians(20+ph))
    s.num("A circuit has voltage transfer function G_v(jω₀) = 0.8∠−30° at the operating frequency ω₀. The input is v_in(t) = 5cos(ω₀t + 20°) V. What is the output voltage at t = 0?",
          out_t0, "V",
          "Output amplitude = 5 × 0.8 = 4 V. Output phase = input phase + ∠G_v = 20° + (−30°) = −10°.\n"
          f"So v_out(t) = 4cos(ω₀t − 10°) and v_out(0) = 4cos(−10°) = 4 × 0.9848 = {g(out_t0)} V.\n"
          "Common mistake: using only the transfer function's phase (4cos(−30°) = 3.46 V) and forgetting the input's own +20° phase.")
    # divider with load : series 2k, shunt 6k || RL 6k
    Rs, Rsh, RL = 2e3, 6e3, 6e3
    par = Rsh*RL/(Rsh+RL)
    gv = par/(Rs+par)
    assert close(gv, 0.6)
    s.mc("A resistive voltage divider has a 2 kΩ series resistor followed by a 6 kΩ resistor to ground. A 6 kΩ load is connected across the 6 kΩ resistor, and the output is taken across the load. What is G_v = V_out/V_in?",
         "0.6",
         ["0.75", "0.4", "0.5"],
         "The load is in parallel with the 6 kΩ shunt resistor: 6 kΩ ∥ 6 kΩ = 3 kΩ. Then G_v = 3k/(2k + 3k) = 0.6.\n"
         "• 0.75 = 6k/(2k + 6k) ignores the loading by the 6 kΩ load.\n"
         "• 0.4 = 2k/(2k + 3k) divides in the wrong order (series resistor over the total).\n"
         "• 0.5 = 6k/(6k + 6k) divides the input between the two 6 kΩ resistors and ignores the 2 kΩ series resistor.\n"
         "A transfer function always depends on what is connected to the output.")
    s.round(3)
    s.mc("A series RLC circuit (passive: only R, L and C, with a voltage source) has Q = 10. Can the voltage across the capacitor be larger than the source voltage?",
         "Yes: at resonance |V_C/V_s| = Q = 10. The circuit has voltage gain but no power gain",
         ["No: a passive circuit can only attenuate, so |V_C/V_s| ≤ 1 at every frequency",
          "Yes, and since the voltage is 10× larger, the circuit also has a power gain of 10",
          "No: |V_C| = |V_L| always, so the capacitor and inductor voltages cancel and stay below the source"],
         "'Gain' of a transfer function just means |V_out/V_in| > 1; passive circuits can have it (reader Sec. 2.2.2 and 2.5.3). At resonance, I = V_s/R, so |V_C| = |I|/(ω₀C) = V_s·Q: the capacitor and inductor voltages are each Q times the source voltage (and 180° out of phase with each other, so they cancel in the KVL sum).\n"
         "This is voltage gain, not power gain: the source supplies the power dissipated in R, and no more.\n"
         "• Passive ≠ attenuation-only for voltage ratios.\n"
         "• Power gain would need an active element.\n"
         "• V_C and V_L are equal in magnitude at resonance but each is Q times V_s, which can be larger than the source.")
    # cascaded dividers, direct connection
    R1, R2 = 10e3, 10e3
    Z2in = R1 + R2
    sh1 = R2*Z2in/(R2+Z2in)
    g1 = sh1/(R1+sh1)
    g2 = R2/(R1+R2)
    tot = g1*g2
    # verify by nodal analysis
    # nodes: A (after first series R), B (after second series R). Vin=1
    G = 1/R1
    Am = np.array([[G + 1/R2 + 1/R1, -1/R1],[-1/R1, 1/R1 + 1/R2]])
    b = np.array([G, 0.0])
    vA, vB = np.linalg.solve(Am, b)
    assert close(vB, tot, 1e-9) and close(tot, 0.2)
    s.num("Two identical resistive dividers (each: 10 kΩ in series, then 10 kΩ to ground) are connected directly one after the other (no buffer). What is the overall V_out/V_in measured at the output of the second divider (open circuit)?",
          tot, "V/V",
          "Each divider alone has G = 10k/(10k + 10k) = 0.5, but the gains do NOT simply multiply (0.25), because the second divider loads the first.\n"
          "The first divider's shunt resistor sees 10 kΩ in parallel with the second divider's input resistance (10k + 10k = 20 kΩ): 10k ∥ 20k = 6.667 kΩ.\n"
          "G₁ = 6.667k/(10k + 6.667k) = 0.4. The second stage (unloaded) has G₂ = 0.5. Total = 0.4 × 0.5 = 0.2.\n"
          "(Nodal analysis confirms 0.2.) Cascading transfer functions requires including the loading effect.")
    s.mc("A circuit has voltage transfer function H = 0.5∠−90° at the frequency of the input v_in(t) = 2sin(ωt) V. Which is the steady-state output?",
         "−cos(ωt) V",
         ["sin(ωt) V", "cos(ωt) V", "−sin(ωt) V"],
         "The amplitude is 2 × 0.5 = 1 V, and the phase shift is −90° applied to a sine: 1·sin(ωt − 90°). Since sin(x − 90°) = −cos(x), the output is −cos(ωt) V.\n"
         "• sin(ωt) ignores the phase shift.\n"
         "• cos(ωt) has the wrong sign: sin(x − 90°) = −cos x, not +cos x. (sin(x + 90°) would give +cos x.)\n"
         "• −sin(ωt) is a 180° shift, not 90°.")
    s.round(4)
    gm, vgs, RD = 2e-3, 10e-3, 5e3
    vo = -gm*vgs*RD
    s.mc("Preview of the common-source amplifier. A transistor produces a drain current i_d = g_m·v_gs, a transadmittance of g_m = 2 mS (this current flows from the supply through R_D = 5 kΩ to the drain, so v_out = −i_d·R_D). The small-signal input is v_gs = 10cos(ωt) mV. What is v_out?",
         "−100cos(ωt) mV",
         ["+100cos(ωt) mV", "−20cos(ωt) mV", "−10cos(ωt) mV"],
         "Chain the two transfer functions: first a transadmittance (voltage → current), then a transimpedance with gain −R_D (current → voltage).\n"
         "i_d = 2 mS × 10 mV = 20 µA; v_out = −20 µA × 5 kΩ = −100 mV. The overall voltage gain is −g_m R_D = −10 V/V (an inverting amplifier, phase 180°).\n"
         "• +100 mV misses the inversion.\n"
         "• −20 mV forgets to multiply by R_D (20 µA is the current, not a voltage).\n"
         "• −10 mV is the gain −g_mR_D with no input amplitude applied.",
         preview=["cs-intro"])
    A, beta = 1000.0, 0.1
    Acl = A/(1+A*beta)
    s.num("Preview of feedback. A later skill shows that when a forward amplifier with voltage gain A is wrapped in a feedback path with gain β, the overall (closed-loop) transfer function is A/(1 + Aβ). Find the closed-loop gain for A = 1000 V/V and β = 0.1.",
          Acl, "V/V",
          f"A_cl = 1000/(1 + 1000 × 0.1) = 1000/101 = {g(Acl)} V/V, very close to 1/β = 10.\n"
          "Each block is a transfer function, and the loop combines them algebraically. Common mistake: computing A/(1 + A) (= 0.999, forgetting β) or 1/(1 + Aβ).",
          preview=["fb-intro"])
    A0, fp, f, vin = 100.0, 10e3, 100e3, 1e-3
    H = A0/(1+1j*f/fp)
    out = vin*abs(H)*1e3
    s.num("Preview of poles and zeros. An amplifier's gain is G_v(jω) = 100/(1 + jf/10 kHz). For a 1 mV amplitude input at 100 kHz, what is the output amplitude in mV?",
          out, "mV",
          f"At f = 100 kHz: f/f_p = 10, so |G_v| = 100/√(1 + 100) = 100/10.05 = {g(abs(H),4)}.\n"
          f"Output amplitude = 1 mV × {g(abs(H),4)} = {g(out)} mV.\n"
          "The pole at 10 kHz has cut the gain from 100 to about 10 by 100 kHz (one decade above the pole: −20 dB). Common mistake: using the DC gain, giving 100 mV.",
          preview=["pole-zero"])
    return s
