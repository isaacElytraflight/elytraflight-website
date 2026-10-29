from qlib import *

def build():
    s = Skill('cx-exp')
    s.round(1)
    s.mc("Euler's relation states that e^(jx) equals…",
         "cos x + j·sin x",
         ["cos x − j·sin x", "cos x + sin x", "e^x·(cos x + j·sin x)"],
         "Euler's relation (reader Eq. 1.29): e^(jx) = cos x + j sin x. The point e^(jx) sits on the unit circle at angle x.\n"
         "• cos x − j sin x equals e^(−jx), the conjugate.\n"
         "• cos x + sin x is a real number; it leaves out the j that puts sin on the imaginary axis.\n"
         "• An extra factor e^x would only appear if the exponent had a real part.")
    s.mc("For real x, what is the magnitude |e^(jωt)|?",
         "1 for every t",
         ["ωt", "0", "e^(ωt)"],
         "|e^(jx)| = √(cos²x + sin²x) = 1 for any real x (reader Eq. 1.30). So e^(jωt) just rotates counter-clockwise around the unit circle at ω rad/s; its length never changes.")
    z = 3 + 4j
    s.num("An impedance is Z = 3 + j4 Ω. What is its magnitude |Z|?", abs(z), "Ω",
          "|Z| = √(x² + y²) = √(3² + 4²) = √25 = 5 Ω. Common mistake: adding the parts, 3 + 4 = 7 Ω.")
    s.round(2)
    z = -2 + 2j
    ph = math.degrees(cmath.phase(z))
    assert close(ph, 135)
    s.num("Find the phase angle of z = −2 + j2, in degrees (measured counter-clockwise from the positive real axis, between −180° and +180°).",
          ph, "degrees",
          "z lies in the second quadrant (negative real part, positive imaginary part).\n"
          "tan⁻¹(y/x) = tan⁻¹(2/(−2)) = tan⁻¹(−1) = −45°, but that calculator value points to the fourth quadrant. Add 180° to land in the correct quadrant: −45° + 180° = 135°.\n"
          "Check: z = 2√2·e^(j135°) = 2.828(cos 135° + j sin 135°) = −2 + j2 ✔.",
          tol=0.02)
    s.mc("Which expression correctly writes cos(ωt) using complex exponentials?",
         "(e^(jωt) + e^(−jωt))/2",
         ["e^(jωt) + e^(−jωt)", "(e^(jωt) − e^(−jωt))/(2j)", "(e^(jωt) − e^(−jωt))/2"],
         "From Euler: e^(jωt) = cos ωt + j sin ωt and e^(−jωt) = cos ωt − j sin ωt. Adding, the sines cancel: e^(jωt) + e^(−jωt) = 2cos ωt, so cos ωt = (e^(jωt) + e^(−jωt))/2 (reader Eq. 1.32).\n"
         "• Without the /2 you would have 2cos ωt.\n"
         "• (e^(jωt) − e^(−jωt))/(2j) is sin ωt (Eq. 1.33).\n"
         "• (e^(jωt) − e^(−jωt))/2 equals j sin ωt, purely imaginary.")
    z = (2*cmath.rect(1, math.radians(30)))*(3*cmath.rect(1, math.radians(60)))/(1.5*cmath.rect(1, math.radians(-45)))
    ans = z.real
    assert close(abs(z), 4) and close(math.degrees(cmath.phase(z)), 135)
    s.num("Evaluate Re{ (2∠30°)(3∠60°) / (1.5∠−45°) }, where each number is written as magnitude∠angle.",
          ans, "(unitless)",
          "Multiply magnitudes and add angles in the numerator; divide magnitudes and subtract angles for the quotient.\n"
          "Magnitude: (2·3)/1.5 = 4. Angle: 30° + 60° − (−45°) = 135°.\n"
          f"Result: 4∠135° = 4cos 135° + j·4 sin 135°. Real part = 4·(−0.7071) = {g(ans)}.\n"
          "Common mistake: subtracting the −45° incorrectly (30° + 60° − 45° = 45°), which would give +2.83.")
    s.round(3)
    s.mc("Which of these complex exponentials has a real part equal to sin(ωt)?",
         "e^(j(ωt − 90°))",
         ["e^(j(ωt + 90°))", "j·e^(jωt)", "e^(jωt)"],
         "Re{e^(j(ωt − 90°))} = cos(ωt − 90°) = sin(ωt) ✔.\n"
         "• Re{e^(j(ωt + 90°))} = cos(ωt + 90°) = −sin(ωt): wrong sign.\n"
         "• j·e^(jωt) = j cos ωt − sin ωt, so Re = −sin(ωt): wrong sign again.\n"
         "• Re{e^(jωt)} = cos(ωt), not sin.\n"
         "Rule: sin(ωt) is cos(ωt) delayed by 90°, i.e., the phase is −90°.")
    # verify numerically
    t = np.linspace(0, 1, 7); w = 5.0
    assert np.allclose(np.real(np.exp(1j*(w*t - np.pi/2))), np.sin(w*t))
    s.mc("A student computes the product of two real signals x(t) = cos(ωt) and y(t) = cos(ωt + φ) by multiplying their complex exponentials: 'x·y = Re{ e^(jωt) · e^(j(ωt+φ)) } = cos(2ωt + φ)'. What is wrong?",
         "The Re{ } trick only works for linear operations; the true product is ½cos φ + ½cos(2ωt + φ), which includes a constant (DC) term",
         ["Nothing is wrong: the product of two cosines is cos(2ωt + φ)",
          "The result should be cos(φ), with no time dependence at all",
          "The result should be ½cos(2ωt + φ), because of the ½ in Euler's formula"],
         "Taking the real part commutes with linear operations (scaling, adding, differentiating, integrating), but NOT with multiplication: Re{ab} ≠ Re{a}·Re{b}.\n"
         "Correct product: cos(ωt)cos(ωt + φ) = ½[cos φ + cos(2ωt + φ)]. Check at φ = 0: cos²(ωt) = ½ + ½cos(2ωt) ✔, which has an average value of ½.\n"
         "• cos(2ωt + φ) alone loses the constant term ½cos φ.\n"
         "• cos φ alone loses the 2ω term and the ½ factors.\n"
         "• ½cos(2ωt + φ) also loses the constant term.\n"
         "This is why power (a product of v and i) needs care, as you will see in AC power.")
    tt = np.linspace(0, 2, 11); ph = 0.7; w = 3.0
    assert np.allclose(np.cos(w*tt)*np.cos(w*tt+ph), 0.5*np.cos(ph)+0.5*np.cos(2*w*tt+ph))
    val = abs(5*cmath.exp((-0.5+10j)*2))
    assert close(val, 5*math.exp(-1))
    s.num("A decaying oscillation is written as the complex exponential v(t) = 5·e^((−0.5 + j10)t) volts, with t in seconds. What is |v(t)| at t = 2 s?",
          val, "V",
          "Split the exponent: e^((−0.5 + j10)t) = e^(−0.5t)·e^(j10t). The factor e^(j10t) has magnitude 1, but e^(−0.5t) is a REAL exponential and does shrink.\n"
          f"|v(2)| = 5·e^(−0.5·2)·1 = 5e^(−1) = {g(val)} V.\n"
          "Common mistake: saying 'the magnitude of a complex exponential is always 1' and answering 5 V; that rule holds only for a purely imaginary exponent.")
    s.round(4)
    H = 0.6 - 0.3j
    A = 2*abs(H); th = math.degrees(cmath.phase(H))
    s.mc("Preview of sinusoidal steady state. A later skill says that for the input 2cos(ωt) = Re{2e^(jωt)}, an LTI circuit with frequency response H = 0.6 − j0.3 produces the output Re{2H·e^(jωt)}. Write this output as A·cos(ωt + θ).",
         f"{g(A,4)}cos(ωt − {g(abs(th),4)}°)",
         [f"{g(A,4)}cos(ωt + {g(abs(th),4)}°)",
          f"1.8cos(ωt − {g(abs(th),4)}°)",
          f"{g(A,4)}cos(ωt − {g(math.degrees(math.atan2(0.6,0.3)),4)}°)"],
         f"Write H in polar form: |H| = √(0.6² + 0.3²) = {g(abs(H),4)}, and ∠H = tan⁻¹(−0.3/0.6) = {g(th,4)}° (fourth quadrant, so negative).\n"
         f"Then 2H·e^(jωt) = 2·{g(abs(H),4)}·e^(j(ωt {g(th,4)}°)), and the real part is {g(A,4)}cos(ωt − {g(abs(th),4)}°).\n"
         "• A + sign on the angle mistakes the sign of the imaginary part.\n"
         "• 1.8 comes from adding the real and imaginary parts (2·(0.6 + 0.3)), but magnitudes of complex numbers combine as √(a² + b²).\n"
         f"• −{g(math.degrees(math.atan2(0.6,0.3)),4)}° uses tan⁻¹(0.6/0.3), swapping real and imaginary parts.",
         preview=["sinusoid-resp", "tf"])
    w = 1000; C = 1e-6; V = 2.0
    I = 1j*w*C*V
    i_t = abs(I)*1e3*math.cos(math.radians(60) + cmath.phase(I))
    assert close(i_t, -math.sqrt(3), 1e-6)
    s.num("Preview of phasors. A later skill shows that a capacitor's phasor current is I = jωC·V. A 1 µF capacitor has voltage v(t) = 2cos(ωt) V with ω = 1000 rad/s. Using j = e^(j90°), find the current i(t) at the instant when ωt = 60° (π/3 rad).",
          i_t, "mA",
          "I = jωC·V = j·(1000)(1×10⁻⁶)(2) = j·0.002 A = 2 mA ∠+90°, so i(t) = 2cos(ωt + 90°) mA = −2 sin(ωt) mA.\n"
          f"At ωt = 60°: i = 2cos(150°) = 2(−0.866) = {g(i_t)} mA (equivalently −2 sin 60°).\n"
          "Multiplying by j rotates by +90° (the current leads the voltage). Common mistake: using −90° (+1.73 mA), or forgetting that j is not just 'a factor' but a rotation.",
          preview=["phasors"])
    Q, w0 = 5, 1000.0
    s_pole = -w0/(2*Q) + 1j*w0*math.sqrt(1 - 1/(4*Q**2))
    mag = abs(cmath.exp(s_pole*0.02))
    assert close(mag, math.exp(-2))
    s.num("Preview of poles and series RLC. A later skill shows that a series RLC circuit with ω₀ = 1000 rad/s and Q = 5 has a response containing e^(st) with s = −ω₀/(2Q) + jω₀√(1 − 1/(4Q²)) = −100 + j995 s⁻¹. Compared with its value at t = 0 (where |e^(st)| = 1), what is |e^(st)| at t = 20 ms?",
          mag, "(unitless)",
          "Write e^(st) = e^(−100t)·e^(j995t). The second factor has magnitude 1 (it just rotates), so only the real part of s sets the decay: |e^(st)| = e^(−100t).\n"
          f"At t = 20 ms: e^(−100 × 0.02) = e^(−2) = {g(mag)}.\n"
          "The oscillation frequency 995 rad/s does not change the magnitude. Common mistake: including 995 in the exponent, or saying the magnitude stays 1.",
          preview=["rlc", "pole-zero"])
    return s
