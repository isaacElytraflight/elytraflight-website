from qlib import *

def build():
    s = Skill('impulse-conv')
    s.round(1)
    s.mc("What is the impulse response h(t) of an LTI system?",
         "The output of the system when the input is a delta function δ(t)",
         ["The output when the input is a unit step u(t)",
          "The output when the input is a sinusoid at 1 rad/s",
          "The derivative of the input signal"],
         "h(t) ≡ L[δ(t)] (reader Eq. 1.72): you 'hit' the system with an ideal very short, very tall impulse (like a hammer blow) and record the response. For an LTI system, h(t) contains all the information about the system.\n"
         "• The response to a step is the STEP response (related to h by integration).\n"
         "• A sinusoid probes the frequency response, not the impulse response.")
    s.mc("An LTI system has impulse response h(t) and is driven by x(t). The output y(t) is given by…",
         "the convolution y(t) = ∫ h(t − τ)x(τ) dτ  (written h ∗ x)",
         ["the product y(t) = h(t)·x(t)", "the sum y(t) = h(t) + x(t)", "the ratio y(t) = x(t)/h(t)"],
         "Write x as a sum of weighted, shifted impulses, then use linearity and time invariance: y(t) = ∫ x(τ)h(t − τ) dτ = (h ∗ x)(t) (reader Eq. 1.73–1.74).\n"
         "A pointwise product, sum, or ratio of the two functions would not respect the system's memory.")
    ans = math.cos(2*math.pi*250*(2.5e-3 - 2e-3))
    assert close(ans, math.sqrt(0.5))
    s.num("A pure delay system has impulse response h(t) = δ(t − 2 ms), so y(t) = x(t − 2 ms). It is driven by x(t) = cos(2π·250·t) V. What is the output at t = 2.5 ms?",
          ans, "V",
          "Convolving with a shifted delta delays the input: y(t) = x(t − 2 ms). At t = 2.5 ms, y = x(0.5 ms) = cos(2π × 250 × 0.0005) = cos(π/4) = 0.7071 V.\n"
          "Common mistake: evaluating x at 2.5 ms (cos(5π/4) = −0.707), i.e., forgetting to delay.")
    s.round(2)
    x = [1, 2, 3]; h = [2, 1]
    y = np.convolve(x, h)
    assert y[2] == 8
    s.num("A sampled LTI system (samples every 1 ms) has impulse response h[0] = 2 V, h[1] = 1 V (and h = 0 afterward). The input samples are x[0] = 1, x[1] = 2, x[2] = 3. Using y[n] = Σ x[k]·h[n − k], what is y[2] (the output at t = 2 ms) in volts?",
          y[2], "V",
          "y[2] = x[0]h[2] + x[1]h[1] + x[2]h[0] = (1)(0) + (2)(1) + (3)(2) = 0 + 2 + 6 = 8 V.\n"
          "Each input sample launches a delayed copy of h, and y[2] adds all contributions that are present at time index 2. A common error is to pair the samples without reversing the index (x[0]h[0] + x[1]h[1] + x[2]h[2] = 2 + 2 + 0 = 4).")
    tau = 2e-3
    h_t = lambda t: 3*math.exp(-t/tau) if t >= 0 else 0.0
    yv = 2*h_t(3e-3) + 1*h_t(3e-3 - 1e-3)
    assert close(yv, 6*math.exp(-1.5) + 3*math.exp(-1))
    s.num("An LTI system has impulse response h(t) = 3e^(−t/2 ms)·u(t) volts (per unit-weight impulse). The input is two impulses: x(t) = 2δ(t) + 1δ(t − 1 ms). What is the output at t = 3 ms?",
          yv, "V",
          "By linearity and time invariance, y(t) = 2h(t) + 1·h(t − 1 ms).\n"
          f"At t = 3 ms: 2h(3 ms) = 2·3e^(−1.5) = {g(2*h_t(3e-3))} V; h(2 ms) = 3e^(−1) = {g(h_t(2e-3))} V.\n"
          f"Sum = {g(yv)} V.\n"
          "Common mistake: using h(3 ms) for both impulses, forgetting that the second impulse started only 2 ms ago.")
    s.mc("Which of these impulse responses could belong to a CAUSAL LTI system?",
         "h(t) = e^(−t)·u(t)",
         ["h(t) = e^(−|t|)", "h(t) = e^(−t)·u(t + 1)", "h(t) = δ(t + 2 ms)"],
         "A causal system cannot respond before the input arrives. The impulse is applied at t = 0, so h(t) must be 0 for all t < 0 (reader Fig. 1.15). e^(−t)u(t) satisfies this.\n"
         "• e^(−|t|) is nonzero for t < 0 (it would be a response before the impulse).\n"
         "• u(t + 1) turns on at t = −1, so the response begins before t = 0.\n"
         "• δ(t + 2 ms) is a response 2 ms BEFORE the impulse: it would need to see the future.")
    s.round(3)
    # moving average: input 1V pulse 0..2ms; h = 500/s for 0..2ms ; check triangle
    dt = 1e-6
    t = np.arange(0, 6e-3, dt)
    xx = ((t >= 0) & (t < 2e-3)).astype(float)
    hh = 500*((t >= 0) & (t < 2e-3)).astype(float)
    yy = np.convolve(xx, hh)[:len(t)]*dt
    assert abs(yy.max() - 1) < 2e-3 and abs(t[yy.argmax()] - 2e-3) < 5e-6
    assert yy[t > 4.01e-3].max() < 1e-6
    s.mc("A 1 V rectangular pulse lasting from t = 0 to 2 ms is applied to an LTI system whose impulse response is a rectangle h(t) = 500 s⁻¹ for 0 < t < 2 ms (zero elsewhere), so ∫h dt = 1. What does the output look like?",
         "A triangle from 0 to 4 ms, peaking at 1 V at t = 2 ms",
         ["A rectangle from 0 to 2 ms with height 1 V",
          "A triangle from 0 to 2 ms, peaking at 0.5 V",
          "A rectangle from 0 to 4 ms with height 1 V"],
         "Convolving two equal-width rectangles gives a triangle whose total duration is the SUM of the widths: 2 ms + 2 ms = 4 ms.\n"
         "Here h is a 'moving-average' filter (area 1): the output at time t is the average of the input over the previous 2 ms. It rises linearly while the window slides into the pulse, reaches 1 V when the window is exactly over the pulse (t = 2 ms), then falls linearly to 0 at t = 4 ms.\n"
         "• A rectangle from 0 to 2 ms would be the output of a memoryless system.\n"
         "• A 2 ms-wide triangle ignores that durations add.\n"
         "• A 4 ms rectangle ignores that the window only fully overlaps the pulse at one instant.")
    s.mc("An LTI system has impulse response h(t) = (1/τ)e^(−t/τ)u(t). To compute the output y(t₀) at some time t₀ from the input, which input value is given the LARGEST weight?",
         "The present value x(t₀); older values are weighted by an exponentially decaying factor",
         ["The value at t = 0, because that is when the impulse was applied",
          "A future value x(t₀ + τ), because the system anticipates the input",
          "All past values equally, so the system just averages them"],
         "y(t₀) = ∫ x(τ′)h(t₀ − τ′) dτ′. The weight on the input value from T seconds ago is h(T) = (1/τ)e^(−T/τ). It is largest at T = 0 (the present) and fades with time constant τ: the system 'remembers' about the last τ seconds (reader Sec. 1.8.1).\n"
         "• The system is causal, so no future values contribute (h = 0 for negative T).\n"
         "• The weighting is not uniform; old values are gradually forgotten.\n"
         "• There is no special significance of t = 0 for a time-invariant system.")
    A, tau, X = 100.0, 5e-3, 2.0
    gain = A*tau
    # numeric integral check
    tt = np.linspace(0, 0.1, 200001)
    area = np.trapezoid(A*np.exp(-tt/tau), tt) if hasattr(np, 'trapezoid') else np.trapz(A*np.exp(-tt/tau), tt)
    assert close(area, gain, 1e-3)
    s.num("An LTI system has impulse response h(t) = 100·e^(−t/5 ms)·u(t) s⁻¹. A constant input x = 2 V has been applied for a very long time. What is the steady output?",
          X*gain, "V",
          "For a constant input, y = x·∫h(τ)dτ: the DC gain of an LTI system is the AREA under its impulse response.\n"
          f"∫₀^∞ 100e^(−τ/5 ms) dτ = 100 × 5 ms = 0.5 (dimensionless). So y = 2 V × 0.5 = {g(X*gain)} V.\n"
          "Common mistake: using h(0) = 100 as the gain, or forgetting the time-constant factor when integrating.")
    s.round(4)
    h_amp, W, Vstep, t0 = 250.0, 4e-3, 3.0, 3e-3
    y = Vstep*h_amp*min(t0, W)
    dt = 1e-6
    t = np.arange(0, 12e-3, dt)
    hh = h_amp*((t >= 0) & (t < W))
    uu = Vstep*(t >= 0)
    yc = np.convolve(uu, hh)[:len(t)]*dt
    assert abs(yc[int(round(t0/dt))] - y) < 5e-3
    s.num("Preview of step response. A 'moving-average' system has impulse response h(t) = 250 s⁻¹ for 0 < t < 4 ms (zero elsewhere). A 3 V step is applied at t = 0. Using the convolution integral y(t) = ∫ x(t − τ)h(τ)dτ, find the output at t = 3 ms. (A later skill shows that the step response is the running integral of h.)",
          y, "V",
          "For t > 0 and a step input, x(t − τ) = 3 V for τ < t and 0 for τ > t. So y(t) = 3·∫₀^min(t, 4 ms) h(τ)dτ.\n"
          "At t = 3 ms (still inside the window): y = 3 × 250 × 0.003 = 2.25 V. After t = 4 ms the output stops growing and stays at 3 × 250 × 0.004 = 3 V.\n"
          "Common mistake: using the full window (3 V) at 3 ms, as if all of h had already contributed.",
          preview=["step-resp"])
    T = 0.5e-3; f = 250.0
    ph = -math.degrees(2*math.pi*f*T)
    s.num("Preview of the frequency-domain view. Drive a pure delay system h(t) = δ(t − T), T = 0.5 ms, with the complex exponential e^(jωt). Convolution gives y = e^(jω(t − T)) = e^(−jωT)·e^(jωt), so H(jω) = e^(−jωT). What is the phase ∠H in degrees at f = 250 Hz?",
          ph, "degrees",
          "∠H = −ωT = −2π(250)(0.0005) = −0.7854 rad = −45°.\n"
          "A pure delay therefore gives a phase shift that grows linearly with frequency, with magnitude |H| = 1 (it passes every tone unchanged in size). Common mistake: using f instead of ω (−0.125 rad).",
          preview=["freq-char"])
    T1, T2 = 1e-3, 2.5e-3
    val = math.cos(2*math.pi*100*(4e-3 - (T1 + T2)))
    s.num("Preview of transfer functions. Two pure-delay systems (delays 1 ms and 2.5 ms) are cascaded. The overall impulse response is the convolution of the two individual ones, δ(t − 1 ms) ∗ δ(t − 2.5 ms). If the input is x(t) = cos(2π·100·t) V, what is the output at t = 4 ms?",
          val, "V",
          "Convolving two shifted deltas adds the shifts: δ(t − T₁) ∗ δ(t − T₂) = δ(t − (T₁ + T₂)). The total delay is 3.5 ms.\n"
          f"y(4 ms) = x(4 ms − 3.5 ms) = x(0.5 ms) = cos(2π·100·0.0005) = cos(0.3142) = cos 18° = {g(val)} V.\n"
          "In the frequency domain this is H₁H₂ = e^(−jωT₁)e^(−jωT₂): convolution in time ↔ multiplication in frequency.",
          preview=["freq-char"])
    return s
