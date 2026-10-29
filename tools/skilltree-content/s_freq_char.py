from qlib import *

def build():
    s = Skill('freq-char')
    s.round(1)
    s.mc("An LTI system has input x(t), impulse response h(t) and output y(t) = h(t) ∗ x(t). In the frequency domain, what does this convolution become?",
         "A multiplication: Y(s) = H(s)·X(s)",
         ["An addition: Y(s) = H(s) + X(s)", "A convolution again: Y = H ∗ X", "A division: Y(s) = X(s)/H(s)"],
         "Convolution in time becomes multiplication in the (Laplace/Fourier) frequency domain: Y = H·X (reader Eq. 1.90). That is why filters are easiest to understand in the frequency domain: each frequency component of the input is just multiplied by H at that frequency.")
    s.mc("How is the frequency response H(jω) of an LTI circuit related to its impulse response h(t)?",
         "H(jω) is the Fourier (Laplace) transform of h(t), i.e., H(s) evaluated on the imaginary axis s = jω",
         ["H(jω) is the derivative of h(t) with respect to ω",
          "H(jω) = h(t) evaluated at t = ω",
          "They are unrelated: one is for sinusoids and the other for impulses"],
         "H(s) = ∫ h(t)e^(−st) dt (the Laplace transform), and H(jω) is that function evaluated at s = jω (reader Eq. 1.86 and 1.94). The impulse response and the transfer function are two descriptions of the same system.\n"
         "The other options are not valid relationships.")
    amp = 2*0.1
    s.num("A filter has |H| = 0.5 at 1 kHz and |H| = 0.1 at 3 kHz. The input is the sum of a 2 V (amplitude) tone at 1 kHz and a 2 V tone at 3 kHz. What is the amplitude of the 3 kHz tone at the output?",
          amp, "V",
          "Each input frequency is multiplied by the filter's gain at that frequency. 3 kHz tone: 2 V × 0.1 = 0.2 V. The 1 kHz tone becomes 2 × 0.5 = 1 V. The tones do not interact because the system is linear.\n"
          "Common mistake: using the 1 kHz gain (0.5) for both tones.")
    s.round(2)
    A, tau = 200.0, 2e-3
    tt = np.linspace(0, 0.1, 400001)
    area = (np.trapezoid if hasattr(np, 'trapezoid') else np.trapz)(A*np.exp(-tt/tau), tt)
    assert close(area, A*tau, 1e-3)
    s.num("An LTI system has impulse response h(t) = 200·e^(−t/2 ms)·u(t) s⁻¹. Using H(0) = ∫h(t)dt, what is its DC gain?",
          A*tau, "V/V",
          "At ω = 0 (s = 0) the transform integral reduces to H(0) = ∫₀^∞ h(t) dt: the area under the impulse response.\n"
          "∫₀^∞ 200e^(−t/2 ms) dt = 200 × 2 ms = 0.4. So the DC gain is 0.4.\n"
          "Common mistake: using h(0) = 200 as the gain.")
    tau, f = 0.5e-3, 500.0
    w = 2*math.pi*f
    Hjw = (1/tau)/(1/tau + 1j*w)
    mag = abs(Hjw)
    assert close(mag, 1/abs(1+1j*w*tau))
    # numeric integral check
    tt = np.linspace(0, 0.05, 2000001)
    integrand = (1/tau)*np.exp(-tt/tau)*np.exp(-1j*w*tt)
    Hn = (np.trapezoid if hasattr(np, 'trapezoid') else np.trapz)(integrand, tt)
    assert close(abs(Hn), mag, 1e-4)
    s.num("A system has impulse response h(t) = (1/τ)e^(−t/τ)u(t) with τ = 0.5 ms. Using H(jω) = ∫₀^∞ h(t)e^(−jωt)dt = (1/τ)/(1/τ + jω), what is |H| at f = 500 Hz?",
          mag, "V/V",
          "ω = 2π·500 = 3141.6 rad/s and 1/τ = 2000 rad/s.\n"
          f"|H| = 2000/√(2000² + 3141.6²) = 2000/3724.1 = {g(mag)}.\n"
          "Equivalently H(jω) = 1/(1 + jωτ) with ωτ = 1.571, so |H| = 1/√(1 + 2.467) = 0.537. Common mistake: using f instead of ω (ωτ = 0.25 gives 0.970).")
    f1 = 1000.0
    g1 = 2/math.sqrt(2)
    g2 = 1/math.sqrt(1+100)
    s.mc("A single-pole filter has H(jf) = 1/(1 + jf/1 kHz). The input is the sum of a 1 kHz tone of amplitude 2 V and a 10 kHz tone of amplitude 1 V. What are the output tone amplitudes?",
         f"1 kHz: {g(g1,4)} V, 10 kHz: {g(g2,3)} V",
         ["1 kHz: 1 V, 10 kHz: 0.091 V",
          f"1 kHz: 2 V, 10 kHz: {g(g2,3)} V",
          f"1 kHz: {g(g1,4)} V, 10 kHz: 1 V"],
         f"|H(1 kHz)| = 1/√(1 + 1²) = 0.7071 ⇒ 2 × 0.7071 = {g(g1,4)} V.\n"
         f"|H(10 kHz)| = 1/√(1 + 10²) = 1/√101 = {g(g2,4)} ⇒ 1 × {g(g2,4)} = {g(g2,3)} V.\n"
         "• '1 V and 0.091 V' uses 1/(1 + f/f_c) instead of 1/√(1 + (f/f_c)²): gains of 0.5 and 0.091.\n"
         "• '2 V' wrongly assumes the passband tone at the corner is unattenuated; at f_c the gain is 0.707.\n"
         "• '1 V' for the 10 kHz tone ignores the filter entirely.")
    s.round(3)
    s.mc("A circuit is an ALL-PASS network: |H(jω)| = 1 at every frequency, but its phase is not a linear function of ω. A signal made of several sinusoids passes through it. What can happen to the waveform?",
         "The shape can change, because different frequencies are delayed by different amounts of time, even though each tone keeps its amplitude",
         ["Nothing: equal magnitude at all frequencies guarantees an identical waveform",
          "Only the overall amplitude can change, by a common factor",
          "New frequencies appear, since the phase is non-linear"],
         "A waveform's shape depends on the relative phases of its frequency components as well as their amplitudes. If ∠H is not proportional to ω, the tones are shifted by different times and add up differently. The all-pass network keeps each tone's amplitude but can still distort the waveform ('phase distortion'). Only a linear phase (a pure delay) preserves the shape.\n"
         "• Equal magnitudes alone do not guarantee an undistorted waveform.\n"
         "• Amplitudes of the individual tones are unchanged, so it is not a uniform amplitude scaling.\n"
         "• An LTI system never creates new frequencies.")
    Hmag = lambda f: 1/math.sqrt(1+(f/1000.0)**2)
    comps = [(4.0, 0.0), (3.0*Hmag(1000), 1000.0), (2.0*Hmag(10000), 10000.0)]
    rms = math.sqrt(4.0**2 + sum(a*a/2 for a, f in comps[1:]))
    # brute force check
    tt = np.linspace(0, 0.01, 2000001)
    y = 4 + 3*Hmag(1000)*np.cos(2*np.pi*1000*tt - np.arctan(1)) + 2*Hmag(10000)*np.cos(2*np.pi*10000*tt - np.arctan(10))
    rms_n = math.sqrt(np.mean(y**2))
    assert close(rms_n, rms, 2e-4), (rms_n, rms)
    s.num("A low-pass filter has H(jf) = 1/(1 + jf/1 kHz). The input is v_in = 4 + 3cos(2π·1 kHz·t) + 2cos(2π·10 kHz·t) volts. What is the RMS value of the steady-state output? (Tones at different frequencies contribute to mean-square power additively; a DC term contributes its value squared.)",
          rms, "V rms",
          f"Output components: DC: 4 V × H(0) = 4 V. 1 kHz: 3 × 0.7071 = 2.121 V peak. 10 kHz: 2/√101 = {g(2*Hmag(10000),4)} V peak.\n"
          f"Mean square = 4² + (2.121²)/2 + ({g(2*Hmag(10000),4)}²)/2 = 16 + 2.25 + {g((2*Hmag(10000))**2/2,3)} = {g(rms**2,5)}.\n"
          f"RMS = √{g(rms**2,5)} = {g(rms)} V.\n"
          "Common mistakes: adding peak amplitudes (6.3 V), or dividing the DC term by √2 (DC is already its own RMS value).")
    s.mc("Which statement about H(s) and H(jω) of a stable LTI circuit is correct?",
         "H(jω) is H(s) evaluated on the imaginary axis; it gives the steady-state response to sinusoids, while H(s) also describes inputs of the form e^(st) with a decaying or growing real part",
         ["H(jω) describes the transient response and H(s) describes the steady state",
          "H(jω) and H(s) are different functions with no mathematical relationship",
          "H(jω) is only defined for ω > 0, and the response at −ω is unrelated to it"],
         "Setting s = jω in H(s) gives the frequency response: the eigenvalue of the system for sinusoidal (periodic) complex exponentials, hence the steady-state sinusoidal response. The general H(s) (any s = σ + jω) gives the response to est, which includes transient behavior (reader Sec. 1.6.2 and 1.10.1).\n"
         "• The roles are reversed in the first wrong option.\n"
         "• They are the same function on different parts of the complex plane.\n"
         "• For real circuits H(−jω) = H(jω)*, so negative frequencies carry no new information; they are related.")
    s.round(4)
    en, k, bw = 20e-9, 0.5, 1000.0
    vn = en*k*math.sqrt(bw)
    s.num("Preview of noise. A later skill says that white noise with density e_n (V/√Hz) passing through a filter of gain |H| over a bandwidth B has RMS value e_n·|H|·√B. An amplifier output has flat noise density 20 nV/√Hz. A filter with |H| = 0.5 from 0 to 1 kHz (and essentially 0 above) follows it. What is the RMS noise at the filter output, in nV?",
          vn*1e9, "nV",
          f"v_n = e_n·|H|·√B = 20 nV/√Hz × 0.5 × √1000 Hz = 20 × 0.5 × 31.62 = {g(vn*1e9)} nV (RMS).\n"
          "This is the 'filtering reduces noise' idea from Fig. 1.24: only the noise inside the passband gets through. Common mistake: forgetting the square root of the bandwidth (giving 10 µV).",
          preview=["noise-dist"])
    A0, fc, f = 10.0, 100e3, 1e6
    out = 0.1*A0/math.sqrt(1+(f/fc)**2)
    s.num("Preview of op-amp frequency response. A closed-loop op-amp amplifier with a low-frequency gain of 10 has the single-pole response H(jf) = 10/(1 + jf/100 kHz). For a 0.1 V amplitude tone at 1 MHz, what is the output amplitude?",
          out, "V",
          f"At f = 1 MHz, f/f_c = 10: |H| = 10/√(1 + 100) = 10/10.05 = {g(10/math.sqrt(101),4)}.\n"
          f"Output amplitude = 0.1 V × {g(10/math.sqrt(101),4)} = {g(out)} V (the gain has fallen from 10 to about 1).\n"
          "Common mistake: using the low-frequency gain of 10 (1 V). This is exactly the frequency-domain limit on how well an amplifier tracks fast signals.",
          preview=["opamp-fr"])
    wr = 0.2
    Hc = 1/(1+1j*wr)
    err = (1-abs(Hc))*100
    s.num("Preview of dynamic errors in feedback. An ideal closed-loop amplifier would have H = 1, but a real one has H(jω) = 1/(1 + jω/ω_c). At a frequency ω = 0.2ω_c, by what percentage is the MAGNITUDE of the gain below 1? (error = (1 − |H|) × 100%)",
          err, "%",
          f"|H| = 1/√(1 + 0.2²) = 1/√1.04 = {g(abs(Hc),5)}.\n"
          f"Magnitude error = (1 − {g(abs(Hc),5)}) × 100% = {g(err)}%.\n"
          "Note the phase error (−tan⁻¹ 0.2 = −11.3°) is also significant. Common mistake: answering 20% (confusing the ratio ω/ω_c with the error). For small ω/ω_c the magnitude error is only about ½(ω/ω_c)² = 2%, because the magnitude depends on the SQUARE of the ratio.",
          preview=["fb-errors"])
    return s
