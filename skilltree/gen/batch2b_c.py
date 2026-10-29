"""batch2b group C: slew, offset, bias-current, noise-dist, datasheet"""
from batch2b_lib import *
from batch2b_b import fig_step, bode_ol, g_

kB, TK = 1.380649e-23, 300.0

def fig_sine_slew(title="Sine distorted by slew-rate limiting"):
    x0, y0, W, H = 30, 70, 290, 55
    b = b2b_line(x0, y0, x0 + W, y0, op=0.5) + b2b_text(x0 + W, y0 + 14, "t", anchor="end", size=10)
    b += b2b_curve(lambda t: 50 * math.sin(t / 22), 0, W - 10, x0, y0, 1, 1, dash=True, n=120)
    # triangle-ish slewed version
    pts = []
    for i in range(0, W - 9, 2):
        tt = i
        sv = 50 * math.sin(tt / 22)
        pts.append((tt, sv))
    out = [pts[0][1] * 0]
    cur = 0.0; lim = 1.25
    res = []
    for tt, sv in pts:
        d = max(-lim * 2, min(lim * 2, sv - cur)); cur += d; res.append((x0 + tt, y0 - cur))
    b += b2b_poly(res, sw=2.2) + b2b_text(x0 + 4, 16, "dashed: ideal sine   solid: slew-limited output", size=10, anchor="start")
    return b2b_svg(340, 140, b, title)

def fig_os(where="+", title="Op-amp with input offset source"):
    o, _, _, _ = b2b_opamp(150, 70, 56, 60)
    b = o + b2b_wire(150, 85, 125, 85) + b2b_circle(115, 85, 10) + b2b_text(115, 82, "+", size=10) + b2b_text(115, 93, "−", size=10) + b2b_text(115, 112, "V_os", size=11) + b2b_wire(105, 85, 90, 85, 90, 95) + b2b_ground(90, 95)
    b += b2b_wire(150, 55, 120, 55, 120, 20, 160, 20) + b2b_resistor(160, 20, 50, label="R₂", lpos=(185, 10)) + b2b_wire(210, 20, 225, 20, 225, 70)
    b += b2b_wire(120, 55, 60, 55) + b2b_dot(120, 55) + b2b_resistor(60, 55, 0) if False else ""
    b += b2b_wire(120, 55, 110, 55) + b2b_resistor(50, 55, 60, label="R₁") + b2b_wire(110, 55, 120, 55) + b2b_dot(120, 55) + b2b_wire(50, 55, 35, 55, 35, 70) + b2b_ground(35, 70)
    b += b2b_wire(206, 70, 260, 70) + b2b_dot(225, 70) + b2b_circle(263, 70, 3) + b2b_text(276, 74, "vₒ", anchor="start")
    return b2b_svg(320, 135, b, title)

def fig_bias(r3=False, title="Input bias currents in an inverting configuration"):
    o, _, _, _ = b2b_opamp(150, 70, 56, 60)
    b = o + b2b_wire(150, 55, 120, 55) + b2b_dot(120, 55) + b2b_resistor(50, 55, 60, label="R₁") + b2b_wire(110, 55, 120, 55) + b2b_wire(50, 55, 35, 55, 35, 70) + b2b_ground(35, 70)
    b += b2b_wire(120, 55, 120, 20, 160, 20) + b2b_resistor(160, 20, 50, label="R₂", lpos=(185, 10)) + b2b_wire(210, 20, 225, 20, 225, 70)
    b += b2b_arrow(128, 49, 146, 49, 5) + b2b_text(137, 44, "I_B1", size=9)
    if r3:
        b += b2b_wire(150, 85, 120, 85, 120, 90) + b2b_resistor(120, 90, 40, horiz=False, label="R₃", lpos=(128, 113)) + b2b_ground(120, 130)
    else:
        b += b2b_wire(150, 85, 120, 85) + b2b_ground(120, 85)
    b += b2b_arrow(128, 91, 146, 91, 5) + b2b_text(137, 103, "I_B2", size=9)
    b += b2b_wire(206, 70, 260, 70) + b2b_dot(225, 70) + b2b_circle(263, 70, 3) + b2b_text(276, 74, "vₒ", anchor="start")
    return b2b_svg(320, 150, b, title)

# ====================================================================== slew
def slew():
    s = Skill('slew')
    s.round(1)
    s.mc(r"What is an op-amp's slew rate (SR)?",
         r"The maximum rate of change of the output voltage, \(SR=\left.\dfrac{dV_o}{dt}\right|_{max}\), usually quoted in \(\mathrm{V/\mu s}\)",
         [r"The frequency at which the gain falls to 1", r"The time the output takes to settle within 1%", r"The maximum output voltage swing"],
         r"Reader Eq. 18.17. However the input moves, the output can't change faster than SR; for big, fast signals the output becomes a straight ramp of slope SR (the 'slew-limited region' in the figure)." "\n" r"• The unity-gain frequency is a LINEAR (small-signal) limit." "\n" r"• Settling time and swing are different specs.",
         fig=fig_step("slew", "Slew-limited step response"), alt="Large step response: the output ramps at a constant slope equal to the slew rate, then settles exponentially.")
    SR, dV = 10.0, 5.0
    s.num(r"An op-amp with \(SR=10\ \mathrm{V/\mu s}\) must make a 5 V output step. Ignoring the final exponential settling, how long does the slew-limited ramp take, in µs?",
          dV / SR, "µs",
          r"A ramp at constant slope: \(t=\dfrac{\Delta V}{SR}=\dfrac{5\ \mathrm{V}}{10\ \mathrm{V/\mu s}}=0.5\ \mu\mathrm{s}\)." "\n" r"Common mistake: multiplying instead of dividing (50 µs).",
          tol=0.01, fig=fig_step("slew", "5 V step with slewing"), alt="Output ramping at the slew rate toward a 5 V final value.")
    s.mc(r"How does slew-rate limiting differ from a bandwidth limit for a large sine wave?",
         r"Slewing is NONLINEAR (the sine is distorted toward a triangle); a bandwidth limit is linear (a sine stays a sine, just smaller and phase-shifted)",
         [r"They are the same effect described in two ways", r"A bandwidth limit distorts the sine; slewing only delays it", r"Slewing affects only small signals"],
         r"Reader Sec. 18.4.2: the finite bandwidth is a linear phenomenon and preserves the sinusoidal shape. Slewing caps the slope, so the steep parts of the sine are replaced by straight ramps (harmonics appear). It depends on amplitude; a bandwidth limit doesn't." "\n" r"• Slewing is a LARGE-signal effect.",
         fig=fig_sine_slew(), alt="A dashed ideal sine wave and a solid output waveform whose steep parts are replaced by straight ramps, looking triangular.")
    s.round(2)
    SR, V = 1e6, 10.0
    fmax = SR / (2 * math.pi * V) / 1e3
    s.num(r"An op-amp has \(SR=1\ \mathrm{V/\mu s}\) and a rated maximum output of \(V_{o,max}=10\ \mathrm{V}\) peak. What is its full-power bandwidth \(f_{max}=\dfrac{SR}{2\pi V_{o,max}}\), in kHz?",
          fmax, "kHz",
          T(r"A sine \(V\sin\omega t\) has maximum slope \(V\omega\) (reader Eq. 18.26). Setting \(2\pi f V=SR\): \(f_{max}=\dfrac{10^6\ \mathrm{V/s}}{2\pi\times10\ \mathrm{V}}=<<f>>\ \mathrm{kHz}\) (Eq. 18.28)." "\n" r"Common mistakes: forgetting \(2\pi\) (100 kHz) or using \(\mathrm{V/\mu s}\) as \(\mathrm{V/s}\).", f=g_(fmax, 4)),
          tol=0.02, fig=fig_sine_slew("Full-power sine near the slew limit"), alt="Ideal and slew-limited sine waves.")
    SR, f = 5e6, 200e3
    Vp = SR / (2 * math.pi * f)
    s.num(r"An op-amp with \(SR=5\ \mathrm{V/\mu s}\) must output a 200 kHz sine without slewing. What is the largest peak amplitude it can deliver, in V?",
          Vp, "V",
          T(r"Require \(V_p\,\omega\le SR\): \(V_p\le\dfrac{SR}{2\pi f}=\dfrac{5\times10^6}{2\pi\times2\times10^5}=<<v>>\ \mathrm{V}\)." "\n" r"Above this amplitude the waveform turns triangular even though 200 kHz may be far below the op-amp's bandwidth.", v=g_(Vp, 4)),
          tol=0.02, fig=fig_sine_slew(), alt="Ideal and slew-limited sine waves.")
    s.mc(r"A sine wave far above the full-power bandwidth is applied at large amplitude to a follower. What does the output look like?",
         r"Close to a triangle wave, with slopes \(\pm SR\), and smaller than the ideal amplitude",
         [r"A clean sine, just phase-shifted", r"A square wave at the supply rails", r"A clean sine of the full amplitude, delayed by \(1/SR\)"],
         r"When the required slope \(V\omega\) far exceeds SR, the output spends almost all its time ramping at \(+SR\) or \(-SR\): a triangle whose amplitude is limited to about \(\dfrac{SR\cdot T}{4}\). That is non-sinusoidal distortion (reader Fig. 18.17)." "\n" r"• Rails clip in voltage, not in slope.",
         fig=fig_sine_slew(), alt="Ideal sine and a triangle-like slew-limited output.")
    s.round(3)
    SR, fu = 0.5e6, 1e6
    vmax = SR / (2 * math.pi * fu) * 1e3
    s.num(r"A follower uses an op-amp with \(SR=0.5\ \mathrm{V/\mu s}\) and \(f_u=1\ \mathrm{MHz}\). What is the largest input step that settles linearly (no slewing at all), in mV?",
          vmax, "mV",
          T(r"The linear response \(V(1-e^{-\omega_ut})\) starts with slope \(V\omega_u\) (reader Eq. 18.20–18.21). No slewing requires \(V\omega_u<SR\):" "\n" r"\[V<\dfrac{SR}{\omega_u}=\dfrac{5\times10^5}{2\pi\times10^6}=<<v>>\ \mathrm{mV}\]" "\n" r"Gotcha: even a sub-0.1 V step can slew in a fast op-amp. 'Large signal' is relative to \(SR/\omega_u\), not to the supply.", v=g_(vmax, 4)),
          tol=0.02, fig=fig_step("exp", "Linear (non-slewing) step response"), alt="Small step and an exponential response.")
    s.mc(r"An op-amp (\(f_u=1\ \mathrm{MHz}\), \(SR=0.5\ \mathrm{V/\mu s}\)) is used in a gain-10 non-inverting amplifier. A 0.1 V input step makes a 1 V output step. Does it slew?",
         r"Yes: the closed-loop bandwidth is \(f_u/10\), so the linear initial slope is \(1\ \mathrm{V}\times2\pi\times100\ \mathrm{kHz}=0.63\ \mathrm{V/\mu s}>SR\)",
         [r"No: the input step is only 0.1 V", r"No: higher gain means a slower amplifier, which can't slew", r"Yes, and its slope is 10 times larger than for a 0.1 V step in a follower"],
         r"Output slope \(=V_{o,step}\,\omega_0=(10\times0.1)\times\dfrac{\omega_u}{10}=0.1\times\omega_u=0.63\ \mathrm{V/\mu s}\). The gain multiplies the step but divides the bandwidth by the same factor, so the initial slope equals the follower's with the same INPUT step. It exceeds 0.5 V/µs, so the output slews." "\n" r"Gotcha: higher gain doesn't protect you from slewing.",
         fig=fig_noninverting("R₁", "R₂ = 9 R₁"), alt="Non-inverting amplifier of gain 10.")
    s.mc(r"A follower uses an op-amp with \(SR=10\ \mathrm{V/\mu s}\) and \(f_u=1\ \mathrm{MHz}\). A 1 V-peak, 1 MHz sine is applied. What is the output?",
         r"A sine of about 0.71 V peak, lagging \(45^\circ\): bandwidth-limited, not slew-limited (it needs only \(6.3\ \mathrm{V/\mu s}\))",
         [r"A triangle wave, because 1 MHz is too fast", r"A 1 V-peak sine, unaffected", r"A sine of about 0.5 V peak due to slewing"],
         r"Slope needed: \(V\omega=2\pi\times10^6\times1=6.3\ \mathrm{V/\mu s}<10\ \mathrm{V/\mu s}\), so no slewing. But 1 MHz is the follower's \(-3\ \mathrm{dB}\) frequency (\(f_u\)), so the LINEAR response is \(1/\sqrt2\approx0.71\) of the input with \(-45^\circ\) phase." "\n" r"Gotcha: check both limits; here the linear one bites first.",
         fig=fig_follower(), alt="Unity-gain follower.")
    s.round(4)
    SR, V = 170e6, 2.0
    fp = SR / (2 * math.pi * V) / 1e6
    s.num(r"Preview of datasheets. The ADA4891 (reader Sec. 18.6) has \(SR=170\ \mathrm{V/\mu s}\). For a 2 V-peak output sine, what is its full-power bandwidth, in MHz?",
          fp, "MHz",
          T(r"\(f_{max}=\dfrac{SR}{2\pi V}=\dfrac{1.7\times10^8}{2\pi\times2}=<<f>>\ \mathrm{MHz}\)." "\n" r"Its GBW is 240 MHz, but a 2 V-peak sine distorts above ~13.5 MHz: datasheets list both because either can be the limit.", f=g_(fp, 4)),
          tol=0.02, fig=fig_sine_slew("Slew limit for a 2 V-peak sine"), alt="Ideal and slew-limited sine waves.", preview=["datasheet"])
    f, V = 20e3, 10.0
    need = 2 * math.pi * f * V / 1e6
    s.num(r"Preview of datasheets. An audio amplifier stage must deliver 10 V peak at 20 kHz without slewing. What minimum slew rate must you look for on the datasheet, in \(\mathrm{V/\mu s}\)?",
          need, "V/µs",
          T(r"\(SR_{min}=2\pi fV=2\pi\times2\times10^4\times10=1.257\times10^6\ \mathrm{V/s}=<<n>>\ \mathrm{V/\mu s}\)." "\n" r"In practice designers add margin (2–5×). A classic 0.5 V/µs part would distort here.", n=g_(need, 4)),
          tol=0.02, fig=fig_sine_slew(), alt="Ideal and slew-limited sine waves.", preview=["datasheet"])
    s.mc(r"Preview of datasheets. You need a gain of 10 delivering a 1 MHz sine of 5 V peak. Which op-amp (GBW, SR) meets both the bandwidth and the slew requirement?",
         r"GBW 240 MHz, SR 170 V/µs",
         [r"GBW 10 MHz, SR 5 V/µs", r"GBW 1 MHz, SR 50 V/µs", r"GBW 3 MHz, SR 0.5 V/µs"],
         r"Bandwidth: gain 10 needs GBW well above \(10\times1\ \mathrm{MHz}=10\ \mathrm{MHz}\). Slew: \(2\pi\times10^6\times5=31.4\ \mathrm{V/\mu s}\)." "\n" r"• GBW 10 MHz puts 1 MHz right at the \(-3\) dB point, and 5 V/µs slews badly." "\n" r"• GBW 1 MHz gives only 100 kHz bandwidth at gain 10." "\n" r"• GBW 3 MHz and 0.5 V/µs fail both." "\n" r"Only the 240 MHz / 170 V/µs part passes both.",
         fig=fig_noninverting("R₁", "R₂ = 9 R₁"), alt="Non-inverting amplifier of gain 10.", preview=["datasheet"])
    return s

# ====================================================================== offset
def offset():
    s = Skill('offset')
    s.round(1)
    s.mc(r"How is an op-amp's input offset voltage \(V_{os}\) modeled?",
         r"As a small DC voltage source in series with one input of an otherwise offset-free op-amp",
         [r"As a resistor in series with the output", r"As a small AC noise source at the output", r"As a current source between the two inputs"],
         r"Reader Fig. 18.1: mismatches inside the op-amp act like a DC voltage at the input. Because its sign is random from part to part, it can be drawn at either input. It shifts the input-output transfer curve sideways (Fig. 18.2)." "\n" r"• Noise is random AC; offset is a DC value fixed for a given part.",
         fig=fig_os(), alt="Op-amp with R1 and R2 and a small source V_os in series with the non-inverting input.")
    s.mc(r"An op-amp with \(A_0=10^5\) and \(V_{os}=1\ \mathrm{mV}\) is used OPEN LOOP with both inputs grounded, on \(\pm12\ \mathrm{V}\) supplies. What is the output?",
         r"Saturated at one rail (about \(\pm12\ \mathrm{V}\)); the ideal 100 V is impossible",
         [r"0 V, since the inputs are grounded", r"100 mV", r"1 mV"],
         r"\(A_0V_{os}=10^5\times1\ \mathrm{mV}=100\ \mathrm{V}\), far beyond the supplies, so the output rails out (reader Sec. 18.2.1). Which rail depends on the sign of \(V_{os}\), which differs part to part." "\n" r"That's why op-amps are almost always used with negative feedback.",
         fig=fig_os(), alt="Op-amp with an offset source in series with one input.")
    Vos, G = 2e-3, 11.0
    s.num(r"A non-inverting amplifier has \(R_2/R_1=10\) (gain 11) and an op-amp with \(V_{os}=2\ \mathrm{mV}\). With the input grounded, what is the output offset voltage, in mV?",
          Vos * G * 1e3, "mV",
          r"\(V_{os}\) sits in series with the \(+\) input, exactly where the signal goes, so it is amplified by the non-inverting gain: \(V_o=V_{os}(1+R_2/R_1)=2\ \mathrm{mV}\times11=22\ \mathrm{mV}\).",
          tol=0.01, fig=fig_os(), alt="Amplifier with R1, R2 and an offset source at the non-inverting input, which is otherwise grounded.")
    s.round(2)
    s.num(r"An INVERTING amplifier has \(R_2/R_1=10\) (signal gain \(-10\)) and an op-amp with \(V_{os}=2\ \mathrm{mV}\). With the signal input grounded, what is the magnitude of the output offset, in mV?",
          22.0, "mV",
          r"With \(v_{in}=0\), the inverting amplifier's input resistor \(R_1\) goes to ground, so the circuit is identical to a non-inverting amplifier for \(V_{os}\): the offset sees the 'noise gain' \(1+R_2/R_1=11\). \(|V_o|=11\times2\ \mathrm{mV}=22\ \mathrm{mV}\), not 20 mV." "\n" r"Common mistake: multiplying by the signal gain 10.",
          tol=0.01, fig=fig_os(), alt="Op-amp with R1 to ground, R2 feedback, and V_os in series with the non-inverting input.")
    s.num(r"A gain-100 non-inverting amplifier must have an output offset below 50 mV. What is the largest acceptable \(|V_{os}|\), in mV?",
          0.5, "mV",
          r"\(|V_{o}|=100|V_{os}|\le50\ \mathrm{mV}\Rightarrow|V_{os}|\le0.5\ \mathrm{mV}\). High-gain DC amplifiers need low-offset (or trimmed) op-amps.",
          tol=0.01, fig=fig_os(), alt="Non-inverting amplifier with an offset source.")
    s.mc(r"A datasheet lists an offset voltage of 2 mV. How should you interpret it for a batch of parts?",
         r"Each part has its own fixed offset with random sign; 2 mV describes the statistical spread (the reader notes it is usually the standard deviation), so some parts exceed it",
         [r"Every part has exactly \(+2\ \mathrm{mV}\)", r"The offset changes sign every cycle like an AC signal", r"It's the output offset in any circuit"],
         r"Offset comes from random mismatch (reader Sec. 18.2.1), so it varies from part to part, with either sign. For a robust design use the worst-case or several-σ value, and remember the circuit multiplies it by the noise gain.",
         fig=fig_os(), alt="Op-amp with an offset source.")
    s.round(3)
    s.mc(r"An inverting amplifier with gain \(-1\) (\(R_2=R_1\)) uses an op-amp with \(V_{os}=3\ \mathrm{mV}\). What is the output offset magnitude?",
         r"6 mV (offset gain \(1+R_2/R_1=2\))",
         [r"3 mV (gain magnitude 1)", r"0 V, because the gain is \(-1\) and the offset cancels", r"1.5 mV"],
         r"The offset is amplified by \(1+R_2/R_1=2\), the gain from the \(+\) input, whatever the signal gain is. A '\(-1\)' stage still doubles the offset.",
         fig=fig_os(), alt="Op-amp with equal R1 and R2 and an offset source.")
    vin, k, Vos = 10e-3, 50.0, 1e-3
    vo = -k * vin + (1 + k) * Vos
    s.num(r"An inverting amplifier has \(R_2/R_1=50\), a DC input \(v_{in}=+10\ \mathrm{mV}\), and \(V_{os}=+1\ \mathrm{mV}\) modeled in series with the \(+\) input (so \(V^+=+1\ \mathrm{mV}\)). What is \(v_o\), in V?",
          vo, "V",
          T(r"Superpose: the signal gives \(-50\times10\ \mathrm{mV}=-0.5\ \mathrm{V}\); the offset gives \(+(1+50)\times1\ \mathrm{mV}=+0.051\ \mathrm{V}\)." "\n" r"\(v_o=-0.5+0.051=<<v>>\ \mathrm{V}\). A 10% error from a 1 mV offset! Common mistake: amplifying \(V_{os}\) by 50 (giving \(-0.45\ \mathrm{V}\)).", v=g_(vo, 4)),
          tol=0.01, fig=fig_os(), alt="Inverting configuration with an offset source in series with the non-inverting input.")
    s.mc(r"In a non-inverting amplifier (gain \(1+R_2/R_1=100\)), a large capacitor is placed in series with \(R_1\) (between \(R_1\) and ground). What happens to the output offset due to \(V_{os}\)?",
         r"It drops to just \(V_{os}\): at DC the capacitor is open so the DC gain is 1, while signals well above the RC corner still get gain 100",
         [r"It is unchanged at \(100\,V_{os}\)", r"It becomes zero", r"It increases to \(\infty\) since the DC gain becomes infinite"],
         r"At DC no current flows through \(R_1\), so the feedback network becomes a direct connection: the circuit is a follower for DC and \(V_o=V_{os}\). At signal frequencies the capacitor is a short and the gain is \(1+R_2/R_1\). This 'AC-coupled feedback' trick is common in audio amplifiers.",
         fig=fig_os(), alt="Non-inverting amplifier with R1 and R2; the question adds a capacitor in series with R1.")
    s.round(4)
    Vos, sens = 0.5e-3, 40e-6
    s.num(r"Preview of datasheets. A thermocouple produces \(40\ \mu\mathrm{V/^\circ C}\). Its amplifier's op-amp has \(V_{os}=0.5\ \mathrm{mV}\). How large a temperature error (in °C) does the untrimmed offset look like?",
          Vos / sens, "°C",
          r"The offset adds to the input like a signal: \(\dfrac{0.5\ \mathrm{mV}}{40\ \mu\mathrm{V/^\circ C}}=12.5\ ^\circ\mathrm{C}\). Precision sensor front-ends need low-offset or 'zero-drift' op-amps, which is why you read that line of a datasheet first.",
          tol=0.01, fig=fig_os(), alt="Amplifier with an offset source.", preview=["datasheet"])
    Vos, Vb, G = 1e-3, 0.3e-3, 20.0
    s.num(r"Preview of input bias current. Another DC error appears as an extra \(0.3\ \mathrm{mV}\) at the \(+\) input (bias current flowing through the source resistance). Worst case it has the same sign as \(V_{os}=1\ \mathrm{mV}\). In a gain-20 non-inverting amplifier, what is the worst-case output DC error, in mV?",
          (Vos + Vb) * G * 1e3, "mV",
          r"Both are DC sources at the same input, so they add before the gain: \((1+0.3)\ \mathrm{mV}\times20=26\ \mathrm{mV}\). The bias-current skill shows where such input voltages come from and how to cancel them.",
          tol=0.01, fig=fig_os(), alt="Non-inverting amplifier with an offset source at the + input.", preview=["bias-current"])
    s.mc(r"Preview of datasheets. An op-amp's offset is trimmed to zero at 25 °C. The datasheet lists an offset drift of \(10\ \mu\mathrm{V/^\circ C}\). The circuit (gain 100) then runs at 75 °C. What output offset do you expect?",
         r"About 50 mV: \(10\ \mu\mathrm{V/^\circ C}\times50\ ^\circ\mathrm{C}=0.5\ \mathrm{mV}\) at the input, times 100",
         [r"0 V, since it was trimmed", r"About 5 mV", r"About 0.5 mV"],
         r"Trimming (reader Sec. 18.2.2) zeroes the offset at ONE temperature. Drift is a separate spec: \(\Delta V_{os}=10\ \mu\mathrm{V/^\circ C}\times50=0.5\ \mathrm{mV}\), and the output sees \(100\times0.5\ \mathrm{mV}=50\ \mathrm{mV}\)." "\n" r"• 0.5 mV forgets the gain; 5 mV is a factor-of-10 slip.",
         fig=fig_os(), alt="Amplifier with an offset source.", preview=["datasheet"])
    return s

# ====================================================================== bias-current
def bias_current():
    s = Skill('bias-current')
    s.round(1)
    s.mc(r"For an op-amp with input currents \(I_{B1}\) and \(I_{B2}\), how are the input bias current \(I_B\) and the input offset current \(I_{OS}\) defined?",
         r"\(I_B=\dfrac{I_{B1}+I_{B2}}{2}\) (the average) and \(I_{OS}=|I_{B1}-I_{B2}|\) (the mismatch)",
         [r"\(I_B=I_{B1}+I_{B2}\) and \(I_{OS}=I_{B1}/I_{B2}\)", r"\(I_B=|I_{B1}-I_{B2}|\) and \(I_{OS}=\dfrac{I_{B1}+I_{B2}}{2}\)", r"\(I_B=I_{B1}\) and \(I_{OS}=I_{B2}\)"],
         r"Reader Eqs. 18.1–18.2. These are DC currents the input transistors need (often BJT base currents, \(I_C/\beta\)). \(I_{OS}\) is typically about 10× smaller than \(I_B\)." "\n" r"They are NOT caused by a finite input resistance: they flow even with both inputs at 0 V.",
         fig=fig_bias(), alt="Inverting configuration showing bias currents I_B1 into the inverting input and I_B2 into the non-inverting input.")
    s.num(r"An op-amp's inputs draw \(I_{B1}=110\ \mathrm{nA}\) and \(I_{B2}=90\ \mathrm{nA}\). What is the input offset current \(I_{OS}\), in nA?",
          20.0, "nA",
          r"\(I_{OS}=|I_{B1}-I_{B2}|=|110-90|=20\ \mathrm{nA}\). (The bias current is the average, 100 nA.)",
          tol=0.01, fig=fig_bias(), alt="Op-amp with bias currents shown at both inputs.")
    IB, R2 = 100e-9, 1e6
    s.num(r"In the circuit shown (inverting configuration, signal input grounded through \(R_1\), \(+\) input grounded), \(R_2=1\ \mathrm{M\Omega}\) and \(I_{B1}=100\ \mathrm{nA}\) flows into the inverting input. Ignoring \(V_{os}\), what is \(v_o\), in V?",
          IB * R2, "V",
          r"\(V^-\approx0\) (virtual ground, \(V^+=0\)), so no current flows in \(R_1\). The bias current must come from the output through \(R_2\): \(v_o=0+I_{B1}R_2=100\ \mathrm{nA}\times1\ \mathrm{M\Omega}=0.1\ \mathrm{V}\) (reader Eq. 18.3).",
          tol=0.01, fig=fig_bias(), alt="Inverting configuration with R1 to ground, R2 feedback and bias currents.")
    s.round(2)
    R1, R2 = 10e3, 100e3
    R3 = R1 * R2 / (R1 + R2)
    s.num(r"To cancel the effect of the bias currents, a resistor \(R_3\) is placed between the \(+\) input and ground. With \(R_1=10\ \mathrm{k\Omega}\) and \(R_2=100\ \mathrm{k\Omega}\), what value of \(R_3\) cancels equal bias currents, in kΩ?",
          R3 / 1e3, "kΩ",
          T(r"The reader shows \(V_o=0\) for \(I_{B1}=I_{B2}\) when \(R_3=\dfrac{R_2}{1+R_2/R_1}=R_1\parallel R_2\) (Eq. 18.6)." "\n" r"\(R_3=\dfrac{10\times100}{110}=<<r>>\ \mathrm{k\Omega}\): both inputs then see the same DC resistance to ground.", r=g_(R3 / 1e3, 4)),
          tol=0.01, fig=fig_bias(True), alt="Op-amp with R1, R2, and a compensation resistor R3 from the non-inverting input to ground.")
    IOS = 10e-9
    s.num(r"With \(R_3=R_1\parallel R_2\) in place and \(R_2=100\ \mathrm{k\Omega}\), the bias currents differ by \(I_{OS}=10\ \mathrm{nA}\). What is the magnitude of the remaining output offset, in mV?",
          IOS * R2 * 1e3, "mV",
          r"With the matched \(R_3\), only the mismatch remains: \(|V_o|=I_{OS}R_2=10\ \mathrm{nA}\times100\ \mathrm{k\Omega}=1\ \mathrm{mV}\), about 10× better than \(I_BR_2\) (reader Sec. 18.2.5).",
          tol=0.01, fig=fig_bias(True), alt="Op-amp with R1, R2, R3 and bias currents.")
    s.mc(r"Why does \(R_3=R_1\parallel R_2\) cancel the effect of equal bias currents?",
         r"\(I_{B2}\) through \(R_3\) makes \(V^+=-I_BR_3\); feedback copies it to \(V^-\), which pulls exactly the right current through \(R_1\) to offset \(I_{B1}\) in \(R_2\)",
         [r"\(R_3\) blocks the bias current from flowing", r"\(R_3\) changes the signal gain so that the offset is divided out", r"\(R_3\) makes the op-amp's input impedance infinite"],
         r"Both inputs then see the same DC resistance (\(R_1\parallel R_2\) on the inverting side, \(R_3\) on the other), so equal currents produce equal input voltages and the op-amp sees no difference. The bias currents still flow; their effects cancel. \(R_3\) carries no signal current, so the ideal gain is unchanged." "\n" r"Sign note: with currents defined INTO the inputs, \(v_o=I_{B1}R_2-I_{B2}R_3(1+R_2/R_1)\). Reader Eqs. 18.4 and 18.6 have the opposite overall sign (inconsistent with Eq. 18.3), but the cancellation condition is the same.",
         fig=fig_bias(True), alt="Op-amp with R1, R2, R3 and bias currents.")
    s.round(3)
    s.mc(r"In the uncompensated circuit (\(+\) input grounded), \(v_o=I_{B1}R_2\). If \(R_1\) is changed from \(10\ \mathrm{k\Omega}\) to \(1\ \mathrm{k\Omega}\) (with \(R_2\) fixed), what happens to the bias-current output offset?",
         r"Nothing: \(R_1\) has 0 V across it (both ends at ground potential), so it carries no bias current",
         [r"It grows 10×, like the signal gain", r"It shrinks 10×", r"It doubles"],
         r"\(V^-\approx V^+=0\) and the other end of \(R_1\) is grounded, so the bias current can only come through \(R_2\) from the output. The output offset \(I_{B1}R_2\) doesn't depend on \(R_1\) (unlike the offset-voltage error, which scales with \(1+R_2/R_1\)).",
         fig=fig_bias(), alt="Inverting configuration with bias currents.")
    IB, Rs, R1, R2 = 100e-9, 100e3, 10e3, 90e3
    vo = IB * R2 - IB * Rs * (1 + R2 / R1)
    s.num(r"A non-inverting amplifier (\(R_1=10\ \mathrm{k\Omega}\), \(R_2=90\ \mathrm{k\Omega}\)) is driven from a sensor with \(100\ \mathrm{k\Omega}\) source resistance (signal set to 0 V). Both inputs draw \(I_B=100\ \mathrm{nA}\) (into the op-amp). What is the output offset, in mV (with sign)?",
          vo * 1e3, "mV",
          T(r"The \(+\) input current flows through the source resistance: \(V^+=-I_BR_s=-10\ \mathrm{mV}\), amplified by \(1+R_2/R_1=10\): \(-100\ \mathrm{mV}\). The \(-\) input current flows through \(R_2\): \(+I_BR_2=+9\ \mathrm{mV}\)." "\n" r"Total \(v_o=<<v>>\ \mathrm{mV}\). Gotcha: the SOURCE resistance multiplied by the noise gain dominates. Making \(R_1\parallel R_2=R_s\) would cancel it.", v=g_(vo * 1e3, 3)),
          tol=0.02, fig=fig_noninverting("R₁ = 10 kΩ", "R₂ = 90 kΩ", "Rₛ = 100 kΩ"), alt="Non-inverting amplifier fed from a source with 100 kΩ resistance.")
    s.mc(r"A student argues: 'An op-amp with infinite input resistance can't have an input bias current.' What's wrong?",
         r"Bias current is a DC current the input devices need to operate (for example a BJT base current), not current through an input resistance, so it exists even with \(R_{in}=\infty\)",
         [r"Nothing: infinite input resistance means zero bias current", r"Bias current only flows at high frequency", r"Bias current is the same thing as offset voltage"],
         r"The reader stresses that the bias current is a DC current, not due to the input impedance (Sec. 18.2.3); it's modeled as current sources at the inputs of an ideal op-amp. CMOS-input op-amps have tiny bias currents (pA) because MOS gates draw almost none, not because of the input resistance number on the datasheet.",
         fig=fig_bias(), alt="Op-amp with current sources at its inputs representing bias currents.")
    s.round(4)
    IB, Vmax = 80e-9, 1e-3
    s.num(r"Preview of datasheets. An op-amp's datasheet gives \(I_B=80\ \mathrm{nA}\). In an uncompensated inverting stage, the bias-current output error \(I_BR_2\) must stay below 1 mV. What is the largest \(R_2\), in kΩ?",
          Vmax / IB / 1e3, "kΩ",
          r"\(R_2\le\dfrac{1\ \mathrm{mV}}{80\ \mathrm{nA}}=12.5\ \mathrm{k\Omega}\). Datasheet specs directly limit resistor values; a CMOS op-amp with pA bias current would allow MΩ resistors.",
          tol=0.01, fig=fig_bias(), alt="Inverting configuration with bias currents.", preview=["datasheet"])
    Vo, R1, R2 = 5.0, 1e3, 10e3
    s.num(r"Preview of datasheets. To shrink bias-current errors you use small resistors: \(R_1=1\ \mathrm{k\Omega}\), \(R_2=10\ \mathrm{k\Omega}\) in a non-inverting stage. At \(v_o=5\ \mathrm{V}\), how much current must the op-amp output supply into the feedback network alone, in mA?",
          Vo / (R1 + R2) * 1e3, "mA",
          r"The output drives \(R_2\) in series with \(R_1\) to ground: \(I=\dfrac{5\ \mathrm{V}}{11\ \mathrm{k\Omega}}=0.455\ \mathrm{mA}\). Smaller resistors mean more output current and power, which is why the reader notes that lower \(R_2\) needs a higher-power op-amp; the datasheet's output-current spec bounds this trade.",
          tol=0.01, fig=fig_noninverting("R₁ = 1 kΩ", "R₂ = 10 kΩ"), alt="Non-inverting amplifier with 1 kΩ and 10 kΩ resistors.", preview=["datasheet"])
    s.mc(r"Preview of noise. Resistors in the feedback network convert the op-amp's input currents into voltage errors. Which design choice reduces BOTH DC bias-current errors and (as you'll see) the random noise contributed by the feedback resistors?",
         r"Using smaller resistor values (at the cost of more output current)",
         [r"Using larger resistor values", r"Adding a capacitor in series with \(R_2\)", r"Increasing the supply voltage"],
         r"Bias error \(\approx I_BR_2\) scales with resistance. Resistor thermal noise also grows with \(R\) (\(v_n\propto\sqrt{R}\)), and noise currents turn into voltages through the same resistors. The reader notes low-noise designs favor small feedback resistors.",
         fig=fig_bias(), alt="Inverting configuration with bias currents.", preview=["noise-dist"])
    return s

# ====================================================================== noise-dist
def noise_dist():
    s = Skill('noise-dist')
    def spec(title="Harmonics produced by a nonlinearity"):
        b = b2b_axes(30, 110, 290, 90, "frequency", "amplitude")
        for x, h, lab in [(80, 80, "ω"), (150, 30, "2ω"), (220, 18, "3ω")]:
            b += b2b_line(x, 110, x, 110 - h, sw=3) + b2b_text(x, 124, lab, size=10)
        return b2b_svg(340, 135, b, title)
    def scurve(title="S-shaped amplifier transfer curve"):
        b = b2b_axes(170, 120, 150, 100, "vᵢ", "vₒ") + b2b_line(20, 70, 320, 70, op=0.3) + b2b_line(170, 125, 170, 15, op=0.3)
        b += b2b_curve(lambda x: 45 * math.tanh(x / 45), -140, 140, 170, 70, 1, 1, sw=2.2)
        return b2b_svg(340, 135, b, title)
    s.round(1)
    s.mc(r"A signal \(\cos(\omega t)\) passes through a square-law nonlinearity. Using \(\cos^2(\omega t)=\tfrac12\left(1+\cos 2\omega t\right)\), which frequencies appear at the output?",
         r"DC and \(2\omega\) (second harmonic)",
         [r"Only \(\omega\)", r"\(\omega\) and \(3\omega\)", r"Only \(2\omega\)"],
         r"Reader Eq. 18.30. Squaring a sinusoid creates a DC term \(\tfrac12\) and a second harmonic \(\tfrac12\cos2\omega t\). A real amplifier with \(a_1v+a_2v^2\) therefore outputs the fundamental (from \(a_1\)) plus DC and \(2\omega\) (from \(a_2\)).",
         fig=spec(), alt="Spectrum sketch with lines at the fundamental, second and third harmonic.")
    s.mc(r"Op-amp datasheets quote input voltage noise in \(\mathrm{nV/\sqrt{Hz}}\). How do you get the RMS noise voltage over a bandwidth \(B\) (white noise)?",
         r"Multiply the density by \(\sqrt{B}\)",
         [r"Multiply the density by \(B\)", r"Divide the density by \(B\)", r"The density already is the RMS voltage"],
         r"The noise POWER per hertz is \(e_n^2\) (in \(\mathrm{V^2/Hz}\)); for a flat spectrum the power in \(B\) is \(e_n^2B\), and the RMS voltage is \(e_n\sqrt B\) (reader Sec. 18.5.2). That's why the unit has a square root of hertz.",
         fig=spec("Noise vs signal spectra"), alt="Spectrum sketch.")
    en, B = 10e-9, 1e6
    s.num(r"An op-amp has white input noise \(e_n=10\ \mathrm{nV/\sqrt{Hz}}\). What is the RMS input noise in a 1 MHz bandwidth, in µV?",
          en * math.sqrt(B) * 1e6, "µV",
          r"\(e_n\sqrt B=10\ \mathrm{nV/\sqrt{Hz}}\times\sqrt{10^6\ \mathrm{Hz}}=10\ \mathrm{nV}\times1000=10\ \mu\mathrm{V}\) RMS.",
          tol=0.01, fig=spec("White noise"), alt="Spectrum sketch.")
    s.round(2)
    R, B = 10e3, 100e3
    vn = math.sqrt(4 * kB * TK * R * B) * 1e6
    s.num(r"What is the RMS thermal noise voltage of a \(10\ \mathrm{k\Omega}\) resistor at 300 K in a 100 kHz bandwidth, \(v_R=\sqrt{4kTR\Delta f}\), in µV? (\(k=1.381\times10^{-23}\ \mathrm{J/K}\))",
          vn, "µV",
          T(r"\(4kTR\Delta f=4(1.381\times10^{-23})(300)(10^4)(10^5)=1.657\times10^{-11}\ \mathrm{V^2}\); square root \(=<<v>>\ \mu\mathrm{V}\) (reader Eq. 18.35)." "\n" r"Rule-of-thumb check: 1 kΩ in 1 MHz ≈ 4 µV; 10× the resistance and 1/10 the bandwidth gives the same \(R\Delta f\), so ≈ 4 µV ✔.", v=g_(vn, 4)),
          tol=0.02, fig=b2b_svg(240, 90, b2b_resistor(40, 45, 70, label="R = 10 kΩ") + b2b_vsource(160, 20, 50, "v_R (noise)", lside="right") + b2b_wire(110, 45, 140, 45, 140, 20, 160, 20) + b2b_wire(40, 45, 25, 45, 25, 80, 160, 80, 160, 70), "Resistor noise model"),
          alt="A resistor in series with a noise voltage source v_R.")
    a1, a3, A = 1.0, 0.1, 1.0
    h3 = a3 * A ** 3 / 4; h1 = a1 * A + 0.75 * a3 * A ** 3
    s.num(r"An amplifier has \(v_o=a_1v_i+a_3v_i^3\) with \(a_1=1\) and \(a_3=0.1\ \mathrm{V^{-2}}\). For \(v_i=1\ \mathrm{V}\cdot\cos\omega t\), what is the third-harmonic amplitude as a percentage of the fundamental? Use \(\cos^3x=\tfrac34\cos x+\tfrac14\cos3x\).",
          h3 / h1 * 100, "%",
          T(r"\(a_3\cos^3\omega t=0.1\left(\tfrac34\cos\omega t+\tfrac14\cos3\omega t\right)\) (reader Eq. 18.33)." "\n" r"Fundamental: \(1+0.075=1.075\). Third harmonic: \(0.025\). Ratio \(=<<h>>\%\)." "\n" r"Common mistake: forgetting that the cubic term also adds to the fundamental (giving 2.5%).", h=g_(h3 / h1 * 100, 4)),
          tol=0.01, fig=scurve(), alt="S-shaped transfer curve that compresses at large inputs.")
    s.mc(r"How does op-amp noise differ from offset voltage?",
         r"Noise is a random AC signal described by its spectral density (and RMS value); offset is a fixed DC value for a given part",
         [r"They are the same thing", r"Noise is a fixed DC value; offset is random AC", r"Noise only appears at the output, offset only at the input"],
         r"Both are modeled as sources at the input of an ideal op-amp (reader Fig. 18.21 and 18.1), but offset is a constant (random only across parts), while noise fluctuates in time with a flat ('white') spectrum, so it's specified per root hertz and integrated over bandwidth.",
         fig=spec("White noise vs a DC offset"), alt="Spectrum sketch.")
    s.round(3)
    s.mc(r"Two uncorrelated noise sources contribute 3 µV RMS and 4 µV RMS at the same node. What is the total RMS noise?",
         r"5 µV (powers add: \(\sqrt{3^2+4^2}\))",
         [r"7 µV (amplitudes add)", r"1 µV (they partially cancel)", r"3.5 µV (the average)"],
         r"Uncorrelated random signals add in POWER (mean-square): \(v^2=3^2+4^2=25\ \mu\mathrm{V^2}\), so 5 µV RMS. Adding RMS values directly would only hold for perfectly correlated (identical) signals.",
         fig=spec("Two noise contributions"), alt="Spectrum sketch.")
    en, f1, f2 = 20e-9, 10e3, 100e3
    vn = en * math.sqrt(f2 - f1) * 1e6
    s.num(r"An amplifier with \(e_n=20\ \mathrm{nV/\sqrt{Hz}}\) (white) is followed by an ideal band-pass filter from 10 kHz to 100 kHz. What is the RMS noise, in µV?",
          vn, "µV",
          T(r"The noise bandwidth is the WIDTH of the band, \(100-10=90\ \mathrm{kHz}\), not 100 kHz: \(20\ \mathrm{nV}\times\sqrt{90\,000}=<<v>>\ \mu\mathrm{V}\)." "\n" r"Using 100 kHz would give 6.32 µV.", v=g_(vn, 4)),
          tol=0.02, fig=b2b_svg(330, 120, b2b_axes(30, 100, 280, 80, "f", "e_n²") + b2b_rect(110, 50, 150, 50, fill=True) + b2b_line(30, 50, 300, 50, dash=True) + b2b_text(110, 114, "10 kHz", size=10) + b2b_text(260, 114, "100 kHz", size=10), "Band-limited white noise"),
          alt="Flat noise spectrum with the band from 10 kHz to 100 kHz shaded.")
    s.mc(r"An amplifier's transfer curve is odd-symmetric, \(v_o(-v_i)=-v_o(v_i)\), like the S-curve shown. Driven by a pure sine, which harmonics can appear?",
         r"Only odd harmonics (\(3\omega\), \(5\omega\), …)",
         [r"Only even harmonics (\(2\omega\), \(4\omega\), …)", r"All harmonics equally", r"No harmonics, since the curve is symmetric"],
         r"An odd function has only odd powers in its Taylor series (\(a_1v+a_3v^3+a_5v^5\dots\)), and odd powers of \(\cos\) contain only odd harmonics (Eq. 18.33). Even harmonics come from even powers like \(v^2\), which an odd-symmetric curve lacks. Differential (balanced) circuits use this to cancel even-order distortion.",
         fig=scurve(), alt="Odd-symmetric S-shaped transfer curve.")
    s.round(4)
    sig, en, B = 10e-3, 10e-9, 20e3
    nv = en * math.sqrt(B)
    snr = 20 * math.log10(sig / nv)
    s.num(r"Preview of datasheets. A 10 mV RMS audio signal is amplified by an op-amp with \(e_n=10\ \mathrm{nV/\sqrt{Hz}}\) over a 20 kHz bandwidth. Considering only that noise, what is the SNR at the input, in dB?",
          snr, "dB",
          T(r"Noise \(=10\ \mathrm{nV}\times\sqrt{20\,000}=1.414\ \mu\mathrm{V}\). \(SNR=20\log_{10}\dfrac{10\ \mathrm{mV}}{1.414\ \mu\mathrm{V}}=<<s>>\ \mathrm{dB}\)." "\n" r"Datasheet noise specs let you predict SNR before building anything.", s=g_(snr, 4)),
          tol=0.01, fig=spec("Signal and noise"), alt="Spectrum sketch.", preview=["datasheet"])
    G, en, fu = 100.0, 5e-9, 10e6
    B = fu / G
    out = G * en * math.sqrt(B) * 1e6
    s.num(r"Preview of datasheets. A gain-100 non-inverting amplifier uses an op-amp with \(e_n=5\ \mathrm{nV/\sqrt{Hz}}\) and \(f_u=10\ \mathrm{MHz}\). Treat the closed-loop bandwidth \(f_u/100\) as a brick wall. What RMS noise appears at the output, in µV?",
          out, "µV",
          T(r"Bandwidth \(=100\ \mathrm{kHz}\). Input noise \(=5\ \mathrm{nV}\times\sqrt{10^5}=1.58\ \mu\mathrm{V}\). The input noise source is amplified like a signal at the \(+\) input: \(\times100\Rightarrow<<o>>\ \mu\mathrm{V}\) RMS." "\n" r"(Real single-pole roll-off adds a factor \(\pi/2\) to the noise bandwidth, a refinement for later.)", o=g_(out, 4)),
          tol=0.02, fig=fig_noninverting("R₁", "R₂ = 99 R₁"), alt="Non-inverting amplifier of gain 100.", preview=["datasheet"])
    s.mc(r"Preview of datasheets. An op-amp stage has 1% distortion open-loop. Wrapped in feedback with loop gain \(T=99\) and compared at the same output amplitude, about how much distortion remains (this is how datasheet THD figures are measured)?",
         r"About 0.01%",
         [r"About 1%", r"About 0.1%", r"About 0.0001%"],
         r"Distortion generated inside the loop is reduced by \(1+T=100\) at equal output level (the noise-rejection result from the loop-gain skill): \(1\%/100=0.01\%\). This is why the reader says harmonics are tiny in negative-feedback circuits.",
         fig=scurve(), alt="S-shaped transfer curve.", preview=["datasheet"])
    return s

# ====================================================================== datasheet
def datasheet():
    s = Skill('datasheet')
    def table(rows, title="Datasheet excerpt"):
        b = ""
        y = 22
        b += b2b_rect(10, 6, 320, 22 * len(rows) + 10, fill=True, r=4)
        for k, v in rows:
            b += b2b_text(22, y + 6, k, anchor="start", size=11) + b2b_text(318, y + 6, v, anchor="end", size=11, bold=True)
            y += 22
        return b2b_svg(340, 22 * len(rows) + 22, b, title)
    ADA = table([("Gain-bandwidth product", "240 MHz"), ("Slew rate", "170 V/µs"), ("Input offset voltage", "2 mV"), ("Open-loop gain", "66 dB"), ("Input resistance", "5 GΩ"), ("Input common-mode range", "−Vs − 0.3 V to +Vs − 0.8 V"), ("CMRR", "88 dB")], "ADA4891 key specs (reader Sec. 18.6)")
    alt = "Table of ADA4891 specs: GBW 240 MHz, slew rate 170 V/µs, offset 2 mV, open-loop gain 66 dB, input resistance 5 GΩ, input common-mode range -Vs-0.3 V to +Vs-0.8 V, CMRR 88 dB."
    s.round(1)
    s.mc(r"Which datasheet number most directly tells you the small-signal bandwidth you'll get for a closed-loop gain of \(G\)?",
         r"The gain-bandwidth product (bandwidth \(\approx GBW/G\) for a non-inverting gain \(G\))",
         [r"The slew rate", r"The input offset voltage", r"The input resistance"],
         r"For a single-pole op-amp, closed-loop bandwidth \(\approx f\cdot f_u=GBW/G_{noninv}\). Slew rate limits LARGE signals; offset and input resistance are DC specs.",
         fig=ADA, alt=alt)
    s.num(r"The ADA4891 lists an open-loop gain of 66 dB. What is that as a ratio (V/V)?",
          10 ** (66 / 20), "V/V",
          r"\(10^{66/20}=10^{3.3}=1995\). Only about 2000: a fast CMOS op-amp trades DC gain for speed, so gain errors are larger than with a 100+ dB part.",
          tol=0.01, fig=ADA, alt=alt)
    s.num(r"The ADA4891's input common-mode range is \(-V_s-0.3\ \mathrm{V}\) to \(+V_s-0.8\ \mathrm{V}\). On \(\pm5\ \mathrm{V}\) supplies (\(V_s=5\ \mathrm{V}\)), what is the highest input voltage that keeps it working properly, in V?",
          4.2, "V",
          r"\(+V_s-0.8=5-0.8=4.2\ \mathrm{V}\). The inputs can go slightly below the negative rail (\(-5.3\ \mathrm{V}\)) but not to the positive one. A follower with a 4.5 V input would misbehave even though it is inside the supplies.",
          tol=0.01, fig=ADA, alt=alt)
    s.round(2)
    s.num(r"Using the ADA4891 (GBW = 240 MHz) as a gain-10 non-inverting amplifier, what closed-loop bandwidth should you expect, in MHz?",
          24.0, "MHz",
          r"\(BW\approx\dfrac{GBW}{G}=\dfrac{240\ \mathrm{MHz}}{10}=24\ \mathrm{MHz}\).",
          tol=0.01, fig=ADA, alt=alt)
    fp = 170e6 / (2 * math.pi * 1.0) / 1e6
    s.num(r"Using the ADA4891 (SR = 170 V/µs), what is the full-power bandwidth for a 1 V-peak output sine, in MHz?",
          fp, "MHz",
          T(r"\(f_{max}=\dfrac{SR}{2\pi V}=\dfrac{1.7\times10^8}{2\pi\times1}=<<f>>\ \mathrm{MHz}\).", f=g_(fp, 4)),
          tol=0.02, fig=ADA, alt=alt)
    s.mc(r"With the ADA4891 at gain 10, you want a 1 V-peak sine at 20 MHz. Which limit matters?",
         r"Bandwidth: 20 MHz is close to the 24 MHz closed-loop corner (gain already down ~2 dB); the slew need of 126 V/µs is within 170 V/µs",
         [r"Slew rate: 126 V/µs exceeds 170 V/µs", r"Neither: 20 MHz is far below 240 MHz", r"Offset voltage"],
         r"Slew: \(2\pi\times20\ \mathrm{MHz}\times1\ \mathrm{V}=126\ \mathrm{V/\mu s}<170\) ✔. Bandwidth: the closed-loop pole is at 24 MHz, so at 20 MHz \(|H|=10/\sqrt{1+(20/24)^2}=7.7\) (−2.3 dB). Comparing 20 MHz with the 240 MHz GBW forgets that gain 10 divides it.",
         fig=ADA, alt=alt)
    s.round(3)
    A0 = 10 ** (66 / 20); Tl = A0 / 10
    G = 10 * Tl / (1 + Tl)
    s.num(r"Gotcha check: with only 66 dB of open-loop gain, what is the actual DC gain of an ADA4891 non-inverting amplifier designed for gain 10 (\(f=0.1\))?",
          G, "V/V",
          T(r"\(A_0=1995\), \(T_0=A_0f=199.5\). \(G=\dfrac{1}{f}\cdot\dfrac{T_0}{1+T_0}=10\times\dfrac{199.5}{200.5}=<<g>>\), a 0.5% error, larger than 0.1%-tolerance resistors.", g=g_(G, 4)),
          tol=0.002, fig=ADA, alt=alt)
    s.mc(r"With the ADA4891 at gain 2 (240 MHz GBW, so 120 MHz bandwidth), you need a 2 V-peak sine at 30 MHz. What happens?",
         r"It slew-limits: the sine needs \(2\pi\times30\ \mathrm{MHz}\times2\ \mathrm{V}=377\ \mathrm{V/\mu s}\), more than 170 V/µs, even though 30 MHz is well inside the 120 MHz bandwidth",
         [r"It works fine; 30 MHz is far below the 120 MHz bandwidth", r"It is bandwidth-limited to −3 dB", r"The offset voltage clips it"],
         r"Bandwidth is fine (30 ≪ 120 MHz), but the slope needed exceeds SR, so the output distorts toward a triangle. Gotcha: a big GBW doesn't guarantee large-signal speed; check SR separately.",
         fig=ADA, alt=alt)
    s.mc(r"The reader compares the fastest Analog Devices op-amps (GHz GBW, slew rates near \(1\ \mathrm{GV/s}\)) with ultra-low-power parts (sub-µA supply current). What trade-off do these tables show?",
         r"Speed (GBW and slew rate) costs supply current: the fastest parts draw tens of mA, while sub-µA parts are very slow",
         [r"Faster op-amps always use less power", r"Power consumption doesn't depend on speed", r"Low-power parts have higher slew rates"],
         r"Slew rate \(\approx I_{max}/C_x\) and GBW \(\approx G_m/C_x\) both need bias current to charge internal capacitances quickly. That's why IoT/sensor op-amps sacrifice speed, and GHz op-amps burn power (reader Sec. 18.6). Read the supply-current line next to the speed specs.",
         fig=table([("Fast part: GBW", "3.8 GHz"), ("Fast part: supply current", "≈ tens of mA"), ("Micropower part: supply current", "< 1 µA"), ("Micropower part: GBW", "≈ kHz range")], "Speed vs power (illustrative)"),
         alt="Table contrasting a fast op-amp (3.8 GHz GBW, tens of mA) with a micropower op-amp (under 1 µA, kHz-range GBW).")
    s.round(4)
    cm = 10 ** (88 / 20)
    err = 1 / cm * 1e6
    s.num(r"Preview of CMRR. The ADA4891 lists CMRR = 88 dB. Treat it as: a 1 V change of both inputs together looks like a differential input error of \(1\ \mathrm{V}/\mathrm{CMRR}\). How big is that equivalent input error, in µV?",
          err, "µV",
          T(r"\(\mathrm{CMRR}=10^{88/20}=2.51\times10^4\). Equivalent error \(=\dfrac{1\ \mathrm{V}}{2.51\times10^4}=<<e>>\ \mu\mathrm{V}\), small compared with the 2 mV offset. CMRR gets its own skill with differential pairs.", e=g_(err, 4)),
          tol=0.02, fig=ADA, alt=alt, preview=["cmrr"])
    s.num(r"Preview of transistor speed. The fastest op-amp in the reader's table has GBW = 3.8 GHz. Used at a non-inverting gain of 20, what closed-loop bandwidth would it give, in MHz?",
          3.8e9 / 20 / 1e6, "MHz",
          r"\(3.8\ \mathrm{GHz}/20=190\ \mathrm{MHz}\). GBW ultimately comes from how fast the internal transistors are; a later skill defines a transistor's own unity-gain frequency \(f_T\), which caps what any op-amp built from it can do.",
          tol=0.01, fig=table([("Gain-bandwidth product", "3.8 GHz")], "Fastest op-amp in the table"), alt="Table: gain-bandwidth product 3.8 GHz.", preview=["ft"])
    s.mc(r"Preview of differential pairs. Why does an op-amp datasheet give the input offset as a statistical value of random sign, not a fixed polarity?",
         r"Offset comes from random mismatch between the two nominally identical halves of the input stage (a differential pair), so each part's offset is a different random number",
         [r"The manufacturer deliberately adds a random offset", r"Offset is caused by the power supply polarity", r"Offset depends only on the signal applied"],
         r"The reader explains that offset arises from mismatches between the input differential-pair transistors or load resistors (Sec. 18.2.1). Mismatch is random, so offset is characterized statistically. The differential-pair skills explain the circuit behind this.",
         fig=ADA, alt=alt, preview=["diff-intro"])
    return s

BUILD = [slew, offset, bias_current, noise_dist, datasheet]
if __name__ == "__main__":
    for fn in BUILD:
        sk = fn(); sk.save(); print("wrote", sk.sid, len(sk.qs))
