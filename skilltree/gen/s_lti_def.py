from qlib import *

def build():
    s = Skill('lti-def')
    # ---------- Round 1
    s.round(1)
    s.mc("Which equation is the definition of a LINEAR system L (with scalars α, β and input signals x(t), y(t))?",
         "L[αx(t) + βy(t)] = αL[x(t)] + βL[y(t)]",
         ["L[x(t − T)] = L[x](t − T) for every delay T",
          "L[x(t)·y(t)] = L[x(t)]·L[y(t)]",
          "L[x(t)] is always a positive number when x(t) is positive"],
         "Linearity means superposition: the response to a weighted sum of inputs is the same weighted sum of the individual responses (reader Eq. 1.20).\n"
         "• 'L[x(t − T)] = L[x](t − T)' is the definition of TIME INVARIANCE, a different property.\n"
         "• Multiplying signals is not what linearity says; products of signals are nonlinear operations.\n"
         "• Positivity of the output has nothing to do with linearity.")
    s.mc("A system is TIME-INVARIANT if…",
         "delaying the input by T seconds just delays the output by the same T seconds",
         ["doubling the input exactly doubles the output",
          "its output never changes with time, even when the input changes",
          "its output depends only on the present value of the input, never on the past"],
         "Time invariance: if input x(t) gives output y(t), then input x(t − T) gives output y(t − T). The system has no 'clock': it behaves the same whenever you apply the input (reader Eq. 1.22).\n"
         "• 'Doubling the input doubles the output' is homogeneity, part of LINEARITY.\n"
         "• A time-invariant system can certainly have a changing output (RC filters do).\n"
         "• Memory (dependence on the past) is allowed; capacitors and inductors have memory and are still time-invariant.")
    # numeric: 4*x1 - x2
    y1, y2 = 3.0, 5.0
    ans = 4*y1 - y2
    assert ans == 7
    s.num("A linear system is driven by input x₁(t); at t = 1 ms its output is 3 V. When it is driven by input x₂(t), its output at t = 1 ms is 5 V. What is the output at t = 1 ms when the input is 4x₁(t) − x₂(t)?",
          ans, "V",
          "By linearity, the output for 4x₁ − x₂ is 4·y₁ − y₂ at every time instant.\n"
          "At t = 1 ms: 4·(3 V) − 5 V = 12 V − 5 V = 7 V.\n"
          "Common mistake: forgetting to scale y₁ by 4 (giving 3 − 5 = −2 V) or adding instead of subtracting (17 V).")
    # ---------- Round 2
    s.round(2)
    s.mc("Which of these systems (input x(t), output y(t)) is both linear and time-invariant?",
         "y(t) = 2x(t) − 3·dx/dt",
         ["y(t) = x(t)²",
          "y(t) = x(t) + 2",
          "y(t) = t·x(t)"],
         "Check each system against superposition and time-shifting.\n"
         "• y = 2x − 3 dx/dt: scaling and adding inputs scales/adds outputs (differentiation is linear), and delaying x delays y. LTI. ✔\n"
         "• y = x²: doubling x quadruples y, so it is nonlinear.\n"
         "• y = x + 2: zero input gives output 2, and doubling x does not double y (2x + 2 ≠ 2(x + 2)), so it is not linear (it is 'affine').\n"
         "• y = t·x(t): linear, but the gain depends on t, so delaying the input does not simply delay the output. Not time-invariant.")
    s.mc("Which of the following circuits, driven by a source v_s(t) with output v_o(t), is an LTI system?",
         "A network of fixed resistors, capacitors, inductors and a linear dependent source",
         ["A resistor in series with a diode, output across the diode",
          "A resistor in series with a capacitor whose value varies as C(t) = C₀(1 + 0.2cos(2π·1 kHz·t)), output across C",
          "A resistor whose value grows with time as R(t) = R₀(1 + 0.1t), with a fixed capacitor, output across C"],
         "LTI circuits are built from fixed (constant-value) linear elements: R, L, C, mutual inductors, and linear dependent sources.\n"
         "• The diode has an exponential I–V curve, so the circuit is nonlinear.\n"
         "• A capacitor whose value changes in time is linear but time-VARYING (the circuit behaves differently depending on when the input arrives).\n"
         "• A resistor drifting with time is likewise linear but time-varying.\n"
         "Only the fixed-element network satisfies both properties.")
    y1ms, y2ms = 4.0, 3.0
    ans = 2*y2ms - 0.5*y1ms
    assert ans == 4
    s.num("An LTI system driven by x(t) produces output y(t) with y(1 ms) = 4 V and y(2 ms) = 3 V. The input is now changed to x_new(t) = 2x(t) − 0.5x(t − 1 ms). What is the new output at t = 2 ms?",
          ans, "V",
          "Use linearity (scale and add) and time invariance (a 1 ms delay of the input delays the output by 1 ms):\n"
          "y_new(t) = 2y(t) − 0.5y(t − 1 ms).\n"
          "At t = 2 ms: y_new = 2·y(2 ms) − 0.5·y(1 ms) = 2·3 − 0.5·4 = 6 − 2 = 4 V.\n"
          "Common mistake: using y(2 ms) for the delayed term instead of y(2 ms − 1 ms) = y(1 ms), which gives 6 − 1.5 = 4.5 V.")
    # ---------- Round 3
    s.round(3)
    s.mc("An amplifier has the input-output relation v_out = 2v_in + 1 (volts). A student says: 'The graph is a straight line, so this is a linear system and superposition applies.' What is the correct assessment?",
         "It is NOT linear: zero input gives 1 V out and doubling the input does not double the output. Superposition holds only for the incremental part (v_out − 1).",
         ["It is linear and time-invariant, because a straight line is the graph of a linear function",
          "It is linear but not time-invariant, because of the offset of 1 V",
          "It is linear only for inputs larger than 0.5 V"],
         "A 'linear system' in the sense of superposition must satisfy L[αx] = αL[x]. Here L[0] = 1 ≠ 0, so it fails. Test: x = 1 gives 3 V, x = 2 gives 5 V, but 2·(3 V) = 6 V ≠ 5 V.\n"
         "The relation is affine (a line that does not pass through the origin). The offset is a constant that is just carried along, so for CHANGES in the input the system behaves linearly: Δv_out = 2Δv_in. This 'linearize around an operating point' idea is exactly how transistors are analyzed later (small-signal models).\n"
         "• The offset is constant in time, so the system is still time-invariant; the failure is linearity, not time invariance.\n"
         "• There is no input range where an offset system satisfies homogeneity.")
    # do check
    f = lambda t, x: t*x
    s.mc("Which of these systems is linear but NOT time-invariant?",
         "y(t) = t·x(t)",
         ["y(t) = x(t − 1 ms)",
          "y(t) = x(t)²",
          "y(t) = 3·dx/dt"],
         "• y = t·x(t): scaling/adding inputs scales/adds outputs (linear). But if the input is delayed by T, the output becomes t·x(t − T), whereas the delayed output would be (t − T)·x(t − T). These differ, so it is time-varying. ✔\n"
         "• y = x(t − 1 ms) is a pure delay: LTI.\n"
         "• y = x² is time-invariant but nonlinear.\n"
         "• y = 3 dx/dt is LTI (differentiation is linear and has no explicit time dependence).")
    s.mc("A circuit is driven by a pure 1 kHz sine wave. Its measured output contains components at 1 kHz AND at 3 kHz. Which conclusion is justified?",
         "The circuit cannot be LTI: it is nonlinear and/or time-varying, since an LTI system never creates frequencies that are not in its input",
         ["The circuit is LTI with a high-Q resonance near 3 kHz",
          "The circuit is LTI and has a pole near 3 kHz that creates the extra tone",
          "The 3 kHz component must have come from the source, because LTI circuits only change phase"],
         "A sinusoid (complex exponential) is an eigenfunction of every LTI system: the output is the same-frequency sinusoid with a new amplitude and phase. So an LTI circuit driven at 1 kHz can only produce 1 kHz (reader Sec. 1.4.4).\n"
         "A 3 kHz output means new frequencies were generated, which happens in nonlinear circuits (distortion, e.g., a clipping amplifier or diode) or time-varying circuits (mixers).\n"
         "• A resonance or a pole near 3 kHz can only attenuate or boost what is present at that frequency; it cannot create 3 kHz content from a pure 1 kHz input.\n"
         "• The source is stated to be a pure 1 kHz sine, so it is not the origin.\n"
         "• LTI circuits change amplitude AND phase, but that is not the point here.")
    # ---------- Round 4
    s.round(4)
    # discrete convolution preview: pulses at 0, 1, 2 ms: weights 3, -2, 1 ; h(1,2,3 ms) = 4,2,1
    h = {0: 0, 1: 4, 2: 2, 3: 1}
    wts = {0: 3, 1: -2, 2: 1}
    t = 3
    ans = sum(w*h[t-k] for k, w in wts.items())
    # independent check with numpy convolve
    chk = np.convolve([3, -2, 1], [0, 4, 2, 1])[3]
    assert ans == chk == 3
    s.num("Preview of impulse response & convolution. An LTI system's response to ONE unit pulse applied at t = 0 is measured (in volts) at t = 0, 1, 2, 3 ms as h = 0, 4, 2, 1. The system is now driven by three pulses: weight 3 at t = 0, weight −2 at t = 1 ms, and weight +1 at t = 2 ms. Using only linearity and time invariance, what is the output at t = 3 ms?",
          ans, "V",
          "Each input pulse produces a scaled, delayed copy of h:\n"
          "• pulse at 0 (weight 3) contributes 3·h(3 ms) = 3·1 = 3 V\n"
          "• pulse at 1 ms (weight −2) contributes −2·h(2 ms) = −2·2 = −4 V\n"
          "• pulse at 2 ms (weight +1) contributes 1·h(1 ms) = 1·4 = 4 V\n"
          "Sum at t = 3 ms: 3 − 4 + 4 = 3 V.\n"
          "This sum-of-delayed-and-scaled-responses is exactly what the convolution y = h ∗ x computes, which you will meet in the impulse-response skill. Common mistake: using h at the wrong delay (e.g., h(3 ms) for every pulse).",
          preview=["impulse-conv"])
    s.mc("Preview of sinusoidal steady state. For one particular LTI circuit, the input cos(ωt) (ω = 1 krad/s) produces the steady-state output 0.5cos(ωt − 60°). Using only linearity and time invariance, what is the steady-state output for the input 4cos(ωt + 30°)?",
         "2cos(ωt − 30°)",
         ["2cos(ωt − 60°)",
          "0.5cos(ωt − 30°)",
          "2cos(ωt − 90°)"],
         "4cos(ωt + 30°) is the input cos(ωt) scaled by 4 and time-shifted so its phase advances by 30°. Linearity scales the output by 4: amplitude 4·0.5 = 2. Time invariance shifts the output by the same time shift, so its phase also advances by 30°: −60° + 30° = −30°.\n"
         "Result: 2cos(ωt − 30°). (Later you will see this as 'multiply the amplitude by |H| and ADD ∠H to the input phase'.)\n"
         "• 2cos(ωt − 60°) forgets the input's own +30° phase.\n"
         "• 0.5cos(ωt − 30°) forgets to scale the amplitude by 4.\n"
         "• 2cos(ωt − 90°) subtracts the input phase (−60° − 30°) instead of adding it.",
         preview=["sinusoid-resp"])
    s.mc("Preview of transfer functions. A circuit is LTI. At 1 kHz its frequency response is H = 0.2∠−45° and at 5 kHz it is H = 0.1∠−80° (magnitude ∠phase). The input is 3cos(2π·1k·t) + 3cos(2π·5k·t + 20°) volts. Which output is correct in steady state?",
         "0.6cos(2π·1k·t − 45°) + 0.3cos(2π·5k·t − 60°) V",
         ["0.6cos(2π·1k·t − 45°) + 0.3cos(2π·5k·t − 80°) V",
          "0.9cos(2π·1k·t − 45°) V (the tones merge into one at the lower frequency)",
          "0.3cos(2π·1k·t − 45°) + 0.6cos(2π·5k·t − 60°) V"],
         "By superposition, treat each tone separately; the output contains only the same two frequencies.\n"
         "• 1 kHz tone: amplitude 3·0.2 = 0.6 V, phase 0° + (−45°) = −45°.\n"
         "• 5 kHz tone: amplitude 3·0.1 = 0.3 V, phase 20° + (−80°) = −60°.\n"
         "Mistakes: using the filter phase alone (−80°) ignores the input's +20°; merging tones is impossible for an LTI system; swapping the gains applies H at the wrong frequency.",
         preview=["tf"])
    return s
