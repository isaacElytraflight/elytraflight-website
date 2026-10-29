from qlib import *

def build():
    s = Skill('ac-power')
    s.round(1)
    s.mc("A sinusoidal voltage is applied across an ideal capacitor. What is the average power absorbed over one full cycle?",
         "Zero: the capacitor stores energy during part of the cycle and returns it during the rest",
         ["Half of V·I at the peak values", "V_rms × I_rms, since the capacitor draws current", "It depends on the frequency but is always positive"],
         "For an ideal capacitor (or inductor) the current is 90° out of phase with the voltage, so p(t) = v(t)i(t) is positive for half of its cycle and negative for the other half; the average is cos(90°)·(…) = 0 (reader Sec. 2.7.1, 2.7.4). Power flows in and out, but there is no net dissipation.\n"
         "Only the resistive part of a load dissipates real power.")
    s.mc("A resistor R is driven by v(t) = V_p·cos(ωt). What is the average power dissipated?",
         "V_p²/(2R)",
         ["V_p²/R", "V_p²/(4R)", "V_p/(2R)"],
         "p(t) = V_p²cos²(ωt)/R, and the average of cos² over a cycle is ½, so P = V_p²/(2R) = V_rms²/R. The ½ is crucial: the voltage is at its peak only momentarily.\n"
         "• V_p²/R is the instantaneous power at the peak, not the average.\n"
         "• V_p²/(4R) double-counts the averaging.\n"
         "• V_p/(2R) has wrong units (it is a current).")
    Vp = 170.0
    Vrms = Vp/math.sqrt(2)
    s.num("The US 'wall-socket' voltage has a peak value of about 170 V. What is its RMS value?",
          Vrms, "V",
          f"For a sinusoid, V_rms = V_p/√2 = 170/1.4142 = {g(Vrms)} V (the familiar 120 V_rms). Common mistake: dividing by 2 (85 V) or multiplying by √2.")
    s.round(2)
    P = 0.5*10*2*math.cos(math.radians(60))
    s.num("A load has voltage amplitude 10 V (peak) and current amplitude 2 A (peak), with the current lagging the voltage by 60°. What is the average power, P = ½|V||I|cos(φ_v − φ_i)?",
          P, "W",
          "P = ½(10)(2)cos(60°) = 10 × 0.5 = 5 W. The cos(60°) = 0.5 is the power factor.\n"
          "Common mistake: forgetting the ½ for peak values (10 W) or ignoring the phase (10 W).")
    Vp, R = 20.0, 50.0
    P = Vp**2/(2*R)
    s.num("A 50 Ω resistor has the voltage v(t) = 20cos(ωt) V across it. What is the average power it dissipates?",
          P, "W",
          "P = V_p²/(2R) = 400/(2 × 50) = 4 W. Equivalent: V_rms = 20/√2 = 14.14 V and P = V_rms²/R = 200/50 = 4 W. Common mistake: V_p²/R = 8 W.")
    Z = 6 + 8j; Ip = 5.0
    P = 0.5*Ip**2*Z.real
    s.mc("A load has impedance Z = 6 + j8 Ω and the peak current through it is 5 A. What is the average power, P = ½|I|²·Re{Z}?",
         "75 W",
         ["125 W", "150 W", "100 W"],
         "Only the resistive part dissipates: P = ½|I|²·Re{Z} = ½(25)(6) = 75 W.\n"
         "• 125 W uses |Z| = 10 Ω instead of Re{Z} (it would be the apparent power ½|I|²|Z|).\n"
         "• 150 W omits the ½ (as if I were an RMS value).\n"
         "• 100 W uses the reactance 8 Ω, which stores energy rather than dissipating it.")
    s.round(3)
    V = 10*cmath.rect(1, math.radians(30)); I = 2*cmath.rect(1, math.radians(-30))
    P_right = 0.5*(V*I.conjugate()).real
    P_wrong = 0.5*(V*I).real
    assert close(P_right, 5) and close(P_wrong, 10)
    s.mc("The phasors for a load (cosine reference, peak values) are V = 10∠30° V and I = 2∠−30° A. What is the average power absorbed?",
         "5 W",
         ["10 W", "8.66 W", "17.3 W"],
         "Average power is P = ½Re{V·I*} = ½|V||I|cos(φ_v − φ_i) = ½(10)(2)cos(30° − (−30°)) = 10 cos 60° = 5 W.\n"
         "• 10 W comes from ½Re{V·I} WITHOUT the conjugate: ½(20)cos(30° + (−30°)) = 10. Power is non-linear (a product), so you cannot just multiply the phasors (reader Eq. 2.73): the conjugate is essential.\n"
         "• 8.66 W uses cos(30°), the phase of the voltage alone, not the phase DIFFERENCE.\n"
         "• 17.3 W drops the ½ and also uses cos 30°.")
    a, b, c = 3.0, 4.0, 0.0
    rms = math.sqrt(a*a + b*b/2)
    tt = np.linspace(0, 1, 2000001)[:-1]
    chk = math.sqrt(np.mean((3 + 4*np.cos(2*np.pi*tt*7))**2))
    assert close(chk, rms, 1e-5)
    s.num("A voltage is v(t) = 3 + 4cos(ωt) volts (a 3 V DC offset plus a 4 V peak sinusoid). What is its RMS value?",
          rms, "V rms",
          "Mean square: ⟨v²⟩ = ⟨9 + 24cos(ωt) + 16cos²(ωt)⟩ = 9 + 0 + 16/2 = 17. The cross term averages to zero, and cos² averages to ½.\n"
          f"RMS = √17 = {g(rms)} V.\n"
          "In other words, the DC and AC parts add in mean-square power: V_rms² = V_DC² + V_p²/2. Common mistakes: 3 + 4/√2 = 5.83 V (adding RMS values) or 7/√2 = 4.95 V (treating the peak value 7 V as if the whole waveform were sinusoidal).")
    V = 100.0; Z = 30 + 40j
    I = V/Z
    P = 0.5*(V*I.conjugate()).real
    S = 0.5*V*abs(I)
    assert close(P, 60) and close(S, 100)
    s.num("A load Z = 30 + j40 Ω is driven by v(t) = 100cos(ωt) V. What is the average power absorbed by the load?",
          P, "W",
          "I = V/Z = 100/(30 + j40) = 100/(50∠53.13°) = 2∠−53.13° A.\n"
          "P = ½|V||I|cos(φ_v − φ_i) = ½(100)(2)cos(53.13°) = 100 × 0.6 = 60 W. (Check: ½|I|²Re{Z} = ½(4)(30) = 60 W ✔.)\n"
          "The product ½|V||I| = 100 is the 'apparent power' (volt-amperes); the power factor 0.6 cuts it to the real power. Common mistake: answering 100 W (ignoring the phase between v and i).")
    s.round(4)
    P0, RL, SR = 12.5e-3, 1e3, 2e6
    Vp = math.sqrt(2*P0*RL)
    fmax = SR/(2*math.pi*Vp)
    assert close(Vp, 5)
    s.num("Preview of slew rate. A later skill says a sinusoid A·sin(ωt) has a maximum slope of Aω, so an amplifier with slew rate SR can only produce an undistorted peak amplitude A up to the frequency f = SR/(2πA). An op-amp is rated to deliver 12.5 mW of average sinusoidal power into a 1 kΩ load, and its slew rate is 2 V/µs. At what frequency (in kHz) can it still deliver that full power without slew limiting?",
          fmax/1e3, "kHz",
          f"Step 1: find the peak amplitude from the power: P = V_p²/(2R) ⇒ V_p = √(2PR) = √(2 × 0.0125 × 1000) = {g(Vp)} V.\n"
          f"Step 2: f = SR/(2πV_p) = (2×10⁶ V/s)/(2π × 5 V) = {g(fmax/1e3)} kHz.\n"
          "Common mistake: using V_rms (3.54 V) as the amplitude in the slope formula, which would give 90 kHz.",
          preview=["slew"])
    Vp, R = 10.0, 2e3
    P = Vp**2/(2*R)
    s.num("Preview of reading datasheets. An op-amp datasheet says the output can swing ±10 V (peak) into a 2 kΩ load. What is the maximum average power a sinusoidal output can deliver to that load, in mW?",
          P*1e3, "mW",
          f"For a sinusoid, P = V_p²/(2R) = 100/(2 × 2000) = {g(P*1e3)} mW (equivalently V_rms = 7.07 V, P = 50/2000 = 25 mW).\n"
          "Datasheet figures for swing are peak values, so be careful to use the ½. Common mistake: V_p²/R = 50 mW.",
          preview=["datasheet"])
    VDD, ID, RD, vo = 3.0, 1e-3, 2e3, 0.5
    Pdc = VDD*ID
    Pac = vo**2/(2*RD)
    frac = Pac/Pdc*100
    s.num("Preview of bias points. A common-source amplifier has a DC (bias) supply of V_DD = 3 V and bias current I_D = 1 mA. The signal at the drain across R_D = 2 kΩ is a sinusoid with 0.5 V peak amplitude. What percentage of the DC supply power appears as average AC signal power in R_D?",
          frac, "%",
          f"DC supply power: P_DC = V_DD·I_D = 3 V × 1 mA = 3 mW.\n"
          f"AC signal power in R_D: P_AC = V_p²/(2R_D) = 0.25/(2 × 2000) = 62.5 µW.\n"
          f"Ratio = 62.5 µW/3 mW = {g(frac)}%. This is why bias (large-signal) power and signal (small-signal) power are analyzed separately.\n"
          "Common mistake: forgetting the ½ (125 µW → 4.17%).",
          preview=["op-point"])
    return s
