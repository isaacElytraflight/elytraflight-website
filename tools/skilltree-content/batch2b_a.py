"""batch2b group A: fb-intro, loop-gain, opamp-models, inverting"""
from batch2b_lib import *

def g_(x, n=4):
    return f"{x:.{n}g}"

def _sumj(x, y, plus_left=True):
    return b2b_circle(x, y, 10) + b2b_text(x - 16, y - 4, "+", size=11) + b2b_text(x + 8, y - 14, "+", size=11)

def fig_loop_noise(g_lab="G", f_lab="f", noise="s_noise"):
    b = (b2b_text(18, 54, "sᵢₙ") + b2b_arrow(30, 50, 82, 50) + b2b_sum(92, 50) +
         b2b_arrow(102, 50, 140, 50) + b2b_box(140, 28, 60, 44, g_lab) +
         b2b_line(200, 50, 222, 50) + _sumj(232, 50) +
         b2b_arrow(242, 50, 300, 50) + b2b_text(310, 54, "sₒᵤₜ", anchor="start") +
         b2b_arrow(232, 14, 232, 38) + b2b_text(232, 10, noise) +
         b2b_wire(272, 50, 272, 115, 200, 115) + b2b_dot(272, 50) + b2b_box(140, 93, 60, 44, f_lab) +
         b2b_wire(140, 115, 92, 115) + b2b_arrow(92, 115, 92, 62))
    return b2b_svg(370, 150, b, "Feedback loop with a disturbance at the output")

def fig_loop_broken(g_lab="G", f_lab="f"):
    b = (b2b_text(18, 54, "sᵢₙ") + b2b_arrow(30, 50, 82, 50) + b2b_sum(92, 50) +
         b2b_arrow(102, 50, 140, 50) + b2b_box(140, 28, 60, 44, g_lab) + b2b_arrow(200, 50, 268, 50) +
         b2b_text(278, 54, "sₒᵤₜ", anchor="start") +
         b2b_wire(235, 50, 235, 115, 200, 115) + b2b_dot(235, 50) + b2b_box(140, 93, 60, 44, f_lab) +
         b2b_wire(140, 115, 92, 115) + b2b_wire(92, 115, 92, 100) +
         b2b_line(78, 96, 106, 96, dash=True) + b2b_text(92, 86, "loop broken here", size=10, anchor="middle"))
    return b2b_svg(370, 150, b, "Loop broken to measure loop gain")

def fig_gm(extra=""):
    b = (b2b_text(18, 49, "v⁺") + b2b_circle(30, 45, 3) + b2b_wire(33, 45, 60, 45) +
         b2b_text(18, 99, "v⁻") + b2b_circle(30, 95, 3) + b2b_wire(33, 95, 60, 95) +
         b2b_box(60, 35, 60, 70, "Gm") + b2b_text(90, 26, "I = Gm(v⁺ − v⁻)", size=10) +
         b2b_wire(120, 70, 160, 70) + b2b_dot(160, 70) + b2b_wire(160, 70, 160, 80) +
         b2b_resistor(160, 80, 50, horiz=False, label="Rₓ", lpos=(172, 108)) + b2b_wire(160, 130, 160, 140) + b2b_ground(160, 140) +
         b2b_wire(160, 70, 200, 70, 200, 80) + b2b_dot(200, 70) + b2b_capacitor(200, 80, 50, horiz=False, label="Cₓ") +
         b2b_wire(200, 130, 200, 140) + b2b_ground(200, 140) +
         b2b_wire(200, 70, 225, 70) + b2b_box(225, 52, 40, 36, "+1") + b2b_wire(265, 70, 300, 70) +
         b2b_circle(303, 70, 3) + b2b_text(318, 74, "vₒ", anchor="start") + extra)
    return b2b_svg(350, 175, b, "Single-pole op-amp model: OTA, Rx‖Cx node, unity buffer")

# ====================================================================== fb-intro
def fb_intro():
    s = Skill('fb-intro')
    F = fig_feedback_blocks()
    s.round(1)
    s.mc(r"In the negative-feedback block diagram, the summing junction forms the error signal \(s_{err}\). Which expression gives it?",
         r"\(s_{err} = s_{in} - f\,s_{out}\)",
         [r"\(s_{err} = s_{in} + f\,s_{out}\)", r"\(s_{err} = G\,(s_{in} - s_{out})\)", r"\(s_{err} = s_{in} - s_{out}/f\)"],
         r"The feedback block \(f\) takes a fraction of the output, \(f\,s_{out}\), and the junction SUBTRACTS it from the input (that is what 'negative' feedback means): \(s_{err}=s_{in}-f\,s_{out}\) (reader Eq. 17.1)." "\n"
         r"• Adding \(f\,s_{out}\) would be positive feedback." "\n" r"• \(G\) multiplies the error afterwards; it is not part of the subtraction." "\n" r"• Dividing by \(f\) mixes up which direction the signal travels in the loop.",
         fig=F, alt="Block diagram: input s_in enters a summing junction (plus), the junction output s_err goes through forward block G to give s_out; s_out is also fed back through block f to the junction's minus input.")
    s.mc(r"A feedback amplifier has forward gain \(G\) and feedback factor \(f\). When \(Gf \gg 1\), the closed-loop gain \(G/(1+Gf)\) approaches",
         r"\(1/f\), which does not depend on \(G\)",
         [r"\(G\), the forward gain", r"\(Gf\), the loop gain", r"\(1+Gf\)"],
         r"If \(Gf\gg1\) then \(1+Gf\approx Gf\), so \(\dfrac{G}{1+Gf}\approx\dfrac{G}{Gf}=\dfrac1f\) (reader Eq. 17.8). The gain is set by the feedback network alone, so even a sloppy, drifting \(G\) gives a precise closed-loop gain." "\n"
         r"• Closed-loop gain \(\approx G\) would only happen if \(Gf\ll1\) (almost no feedback)." "\n" r"• \(Gf\) is the gain around the loop, not the gain from input to output.",
         fig=F, alt="Same negative feedback block diagram with forward gain G and feedback factor f.")
    G, f = 1000.0, 0.1
    ans = G / (1 + G * f)
    s.num(r"A feedback system has forward gain \(G=1000\) and feedback factor \(f=0.1\). What is the closed-loop gain \(s_{out}/s_{in}\)?",
          ans, "V/V",
          T(r"\(G_{closed}=\dfrac{G}{1+Gf}=\dfrac{1000}{1+1000\cdot0.1}=\dfrac{1000}{101}=<<a>>\)." "\n" r"Compare with the shortcut \(1/f=10\): since \(Gf=100\gg1\), the shortcut is within 1%. Common mistake: forgetting the 1 in the denominator and answering \(G/(Gf)=10\) exactly.", a=g_(ans, 4)),
          tol=0.01, fig=F, alt="Negative feedback block diagram with G = 1000 and f = 0.1.")
    s.round(2)
    r1, r2 = 2000.0, 38000.0
    f = r1 / (r1 + r2)
    s.num(r"A non-inverting amplifier has \(R_1 = 2\ \mathrm{k\Omega}\) (to ground) and \(R_2 = 38\ \mathrm{k\Omega}\) (from output to the inverting input). The resistive divider is the feedback network. In the limit of a very large op-amp gain, what is the closed-loop gain \(1/f\)?",
          1 / f, "V/V",
          r"The divider returns \(f=\dfrac{R_1}{R_1+R_2}=\dfrac{2}{40}=0.05\) of the output to the inverting input. For huge \(G\), the gain is \(1/f=\dfrac{R_1+R_2}{R_1}=1+\dfrac{R_2}{R_1}=1+19=20\)." "\n" r"Common mistake: using \(R_2/R_1=19\) (that is the inverting-amplifier magnitude) or \(R_1/(R_1+R_2)\) (that is \(f\), not \(1/f\)).",
          tol=0.01, fig=fig_noninverting("R₁ = 2 kΩ", "R₂ = 38 kΩ"), alt="Non-inverting op-amp amplifier: input to the + terminal, R2 from the output to the − terminal, R1 from the − terminal to ground.")
    G = 1000.0
    ans = G / (1 + G * f)
    s.num(r"The same amplifier (\(f = 0.05\)) is built with an op-amp whose finite gain is \(G = 1000\). What is the actual closed-loop gain?",
          ans, "V/V",
          T(r"\(G_{closed}=\dfrac{G}{1+Gf}=\dfrac{1000}{1+1000\cdot0.05}=\dfrac{1000}{51}=<<a>>\)." "\n" r"This is about 2% below the ideal value of 20, because \(Gf=50\) is large but not infinite.", a=g_(ans, 4)),
          tol=0.01, fig=fig_noninverting("R₁ = 2 kΩ", "R₂ = 38 kΩ"), alt="Non-inverting amplifier with R1 = 2 kΩ and R2 = 38 kΩ (f = 0.05).")
    f = 0.05
    a1 = 1000 / (1 + 1000 * f); a2 = 900 / (1 + 900 * f)
    chg = (a1 - a2) / a1 * 100
    s.mc(r"In a feedback amplifier with \(f=0.05\), the forward gain \(G\) drops by 10%, from 1000 to 900 (aging or temperature). About how much does the closed-loop gain change?",
         r"About 0.2%, much less than 10%",
         ["About 10%, the same as G", "About 5%, half of G's change", "About 2%"],
         T(r"Compute both: \(1000/(1+50)=<<a1>>\) and \(900/(1+45)=<<a2>>\). The change is \(<<c>>\%\)." "\n" r"In general \(\dfrac{dG_{cl}}{G_{cl}}=\dfrac{1}{1+Gf}\dfrac{dG}{G}\): feedback shrinks the sensitivity to \(G\) by the factor \(1+Gf\approx 50\), and \(10\%/50 = 0.2\%\). That is exactly why feedback is used for precision." "\n" r"• 10% would be the no-feedback behavior." "\n" r"• 5% and 2% don't match the factor \(1+Gf\approx50\).", a1=g_(a1, 4), a2=g_(a2, 4), c=g_(chg, 2)),
         fig=F, alt="Negative feedback loop block diagram, forward block G and feedback block f.")
    s.round(3)
    s.mc(r"As \(G\to\infty\), the error signal \(s_{err}=s_{in}/(1+Gf)\) of a negative-feedback loop goes to zero, yet the output \(s_{out}\) stays finite and equal to \(s_{in}/f\). How is that consistent?",
         r"\(s_{out}=G\,s_{err}\): a vanishing \(s_{err}\) times an enormous \(G\) leaves a finite product, \(s_{in}/f\)",
         [r"The output must also go to zero, since \(s_{out}=G\,s_{err}\) and \(s_{err}\to0\)", r"The loop breaks, so the output is undefined for infinite \(G\)", r"\(s_{err}\) is exactly zero for any finite \(G\), so the output is exactly \(s_{in}/f\) even for small \(G\)"],
         r"\(s_{err}=s_{in}/(1+Gf)\) is never exactly zero for finite \(G\); it shrinks as \(1/G\). The output is \(G\cdot s_{err}=\dfrac{G}{1+Gf}s_{in}\to\dfrac{s_{in}}{f}\)." "\n" r"This is the origin of the 'golden rules' for op-amps: the input difference is ≈ 0 BECAUSE the gain is huge, while the output is whatever value makes the feedback signal \(f\,s_{out}\) equal \(s_{in}\). The reader notes this is a '\(0\cdot\infty\)' limit." "\n"
         r"• \(s_{out}\) cannot vanish: if it did, the feedback signal would be zero and the error would equal \(s_{in}\), contradicting \(s_{err}\to0\)." "\n" r"• The loop is perfectly well defined; the equation \(s_{out}=G(s_{in}-f s_{out})\) simply solves algebraically.",
         fig=F, alt="Negative feedback block diagram with the error signal marked between the summing junction and block G.")
    pos = b2b_svg(340, 150, b2b_text(18, 54, "sᵢₙ") + b2b_arrow(30, 50, 82, 50) + b2b_circle(92, 50, 10) + b2b_text(76, 46, "+", size=11) + b2b_text(100, 78, "+", size=11) + b2b_arrow(102, 50, 140, 50) + b2b_box(140, 28, 60, 44, "G") + b2b_arrow(200, 50, 268, 50) + b2b_text(278, 54, "sₒᵤₜ", anchor="start") + b2b_wire(235, 50, 235, 115, 200, 115) + b2b_dot(235, 50) + b2b_box(140, 93, 60, 44, "f") + b2b_wire(140, 115, 92, 115) + b2b_arrow(92, 115, 92, 62), "Positive feedback loop")
    s.mc(r"A designer accidentally makes the feedback POSITIVE: \(s_{err}=s_{in}+f\,s_{out}\). The loop gain is \(Gf=0.9\) with \(G=50\). What is the closed-loop gain \(G/(1-Gf)\)?",
         r"500, ten times larger than \(G\), and very sensitive to small changes in \(Gf\)",
         [r"26.3, the negative-feedback result", r"50, the same as \(G\)", r"Infinite, because positive feedback always blows up"],
         r"With positive feedback each trip around the loop adds a copy of the output: \(G_{closed}=G(1+T+T^2+\dots)=\dfrac{G}{1-T}\) for \(|T|<1\) (reader Eq. 17.14). Here \(T=0.9\), so \(G_{closed}=50/0.1=500\)." "\n"
         r"It is only infinite when \(T=1\) exactly, and it is hypersensitive near there: change \(T\) from 0.9 to 0.95 and the gain doubles to 1000. If \(T>1\) the output grows until something saturates ('railing out')." "\n"
         r"• \(50/(1+0.9)=26.3\) is the NEGATIVE-feedback answer." "\n" r"• 'Always blows up' is false for \(T<1\).",
         fig=pos, alt="Block diagram of a POSITIVE feedback loop: both inputs of the summing junction carry plus signs; forward block G, feedback block f.")
    T_ = 999.0
    s.num(r"A designer wants the closed-loop gain to be within 0.1% of the ideal value \(1/f\), i.e. \(G_{closed}\ge 0.999/f\). What is the minimum loop gain \(T=Gf\) needed?",
          T_, "",
          r"\(G_{closed}\cdot f=\dfrac{Gf}{1+Gf}=\dfrac{T}{1+T}\). Setting \(\dfrac{T}{1+T}=0.999\) gives \(T=\dfrac{0.999}{0.001}=999\)." "\n" r"So the loop gain must be about 1000 for 0.1% accuracy: the fractional error is \(\dfrac{1}{1+T}\). Common mistake: using \(T\ge0.999\).",
          tol=0.02, fig=F, alt="Negative feedback block diagram; loop gain T = G f.")
    s.round(4)
    G, f = 1e5, 0.01
    GC = G / (1 + G * f); idl = 1 / f
    err = (idl - GC) / idl * 100
    s.num(r"Preview of feedback errors. A non-inverting amplifier uses \(R_1=1\ \mathrm{k\Omega}\) and \(R_2=99\ \mathrm{k\Omega}\) around an op-amp with finite gain \(G=10^5\). The ideal gain is \(1/f\). By what percentage is the actual gain below the ideal value?",
          err, "%",
          T(r"\(f=\dfrac{1}{100}=0.01\), so the ideal gain is \(1/f=100\). The actual gain is \(\dfrac{10^5}{1+10^5\cdot0.01}=\dfrac{10^5}{1001}=<<gc>>\)." "\n" r"Error \(=\dfrac{100-<<gc>>}{100}=<<e>>\%\), which equals \(\dfrac{1}{1+T}=\dfrac{1}{1001}\). A later skill ('static and dynamic errors') studies exactly this gain error and how it grows when \(T\) falls.", gc=g_(GC, 5), e=g_(err, 3)),
          tol=0.03, fig=fig_noninverting("R₁ = 1 kΩ", "R₂ = 99 kΩ"), alt="Non-inverting amplifier with R1 = 1 kΩ and R2 = 99 kΩ.", preview=["fb-errors", "loop-gain"])
    T_, n = 50.0, 10e-3
    ans = n / (1 + T_) * 1e3
    s.num(r"Preview of noise rejection. A disturbance of 10 mV (for example supply ripple or distortion) is injected at the amplifier's OUTPUT, as in the figure, with \(s_{in}=0\). The loop has \(G=1000\) and \(f=0.05\). How large is the disturbance's contribution to \(s_{out}\), in mV?",
          ans, "mV",
          T(r"With \(s_{in}=0\) and an additive disturbance, \(s_{out}=G(0-f\,s_{out})+s_{noise}\), so \(s_{out}=\dfrac{s_{noise}}{1+Gf}\) (reader Eq. 17.13)." "\n" r"Here \(Gf=50\), so \(s_{out}=\dfrac{10\ \mathrm{mV}}{51}=<<a>>\ \mathrm{mV}\). The loop 'sees' the disturbance as an error and fights it, rejecting it by the factor \(1+T\). Later skills (noise and distortion, output impedance) build on this.", a=g_(ans, 3)),
          tol=0.02, fig=fig_loop_noise(), alt="Feedback loop with an extra summing junction after block G where a disturbance s_noise is added to the output.",
          preview=["noise-dist", "fb-impedance"])
    G0, f, fp = 1000.0, 0.1, 1e3
    ans = fp * (1 + G0 * f) / 1e3
    s.num(r"Preview of bandwidth extension. The forward amplifier is \(G(s)=\dfrac{1000}{1+j\omega/\omega_p}\) with \(f_p=\omega_p/2\pi=1\ \mathrm{kHz}\), used inside a negative-feedback loop with \(f=0.1\). The closed-loop transfer function has the same one-pole form. Where is its pole, in kHz?",
          ans, "kHz",
          r"\(G_{closed}=\dfrac{G}{1+Gf}=\dfrac{G_0/(1+j\omega/\omega_p)}{1+G_0f/(1+j\omega/\omega_p)}=\dfrac{G_0}{(1+j\omega/\omega_p)+G_0f}=\dfrac{G_0/(1+T_0)}{1+j\omega/[\omega_p(1+T_0)]}\) with \(T_0=G_0f=100\)." "\n" r"The pole moves up by the factor \(1+T_0=101\): \(f_{p,closed}=1\ \mathrm{kHz}\times101=101\ \mathrm{kHz}\). The DC gain dropped by the same factor (1000 → 9.9), so feedback trades gain for bandwidth, the idea behind the gain-bandwidth product.",
          tol=0.02, fig=F, alt="Negative feedback block diagram with a single-pole forward amplifier G(s) and a feedback factor f = 0.1.", preview=["gbw", "opamp-fr"])
    return s

# ====================================================================== loop-gain
def loop_gain():
    s = Skill('loop-gain')
    F = fig_loop_broken()
    s.round(1)
    s.mc(r"What does the loop gain \(T\) of a feedback system measure?",
         r"The gain once around the loop (cut the loop, inject a signal, and see what comes back): \(T=G\,f\)",
         [r"The gain from the input to the output: \(G/(1+Gf)\)", r"The forward gain \(G\) alone", r"The gain of the feedback network alone, \(f\)"],
         r"Break the loop, apply a test signal at the break, and follow it through \(G\) and then \(f\): what returns is \(T=G\,f\) (reader Eq. 17.10 and Fig. 17.7a). It is the quantity that decides how strongly the feedback acts." "\n"
         r"• \(G/(1+T)\) is the closed-loop gain." "\n" r"• \(G\) and \(f\) alone are only two of the factors in \(T\).",
         fig=F, alt="Feedback block diagram with the loop opened at the feedback path (dashed break); T is the gain around the loop through G and then f.")
    s.mc(r"Which condition makes the closed-loop gain \(G/(1+T)\) depend almost only on the feedback network, \(\approx 1/f\)?",
         r"The LOOP gain must be large, \(T=Gf\gg1\)",
         [r"The forward gain \(G\) must be small", r"The feedback factor \(f\) must equal 1", r"\(G\gg1\) alone is enough, whatever \(f\) is"],
         r"\(\dfrac{G}{1+T}\to\dfrac{G}{T}=\dfrac1f\) only when \(T\gg1\)." "\n" r"The last option is the subtle trap: a huge \(G\) paired with a tiny \(f\) can still give \(T\) near 1 (for example \(G=100\) and \(f=0.005\) gives \(T=0.5\)), and then the gain is NOT \(1/f\). The reader stresses that it is important for \(T\) to be large, not just \(G\).",
         fig=fig_feedback_blocks(), alt="Negative feedback loop block diagram.")
    G, f = 2e4, 0.01
    s.num(r"An op-amp with open-loop gain \(G=2\times10^{4}\) is used in a loop with feedback factor \(f=0.01\). What is the loop gain \(T\)?",
          G * f, "",
          r"\(T=G\,f=2\times10^{4}\times0.01=200\)." "\n" r"Because \(T=200\gg1\), the closed-loop gain \(G/(1+T)\approx 1/f=100\) with an error of about \(1/(1+T)=0.5\%\).",
          tol=0.01, fig=fig_feedback_blocks(), alt="Negative feedback loop with G = 20000 and f = 0.01.")
    s.round(2)
    r1, r2, A = 1e3, 49e3, 1e4
    f = r1 / (r1 + r2); Tv = A * f
    s.num(r"A non-inverting amplifier has \(R_1=1\ \mathrm{k\Omega}\), \(R_2=49\ \mathrm{k\Omega}\) and an op-amp gain \(A=10^{4}\). What is its loop gain \(T\)?",
          Tv, "",
          r"The feedback factor is \(f=\dfrac{R_1}{R_1+R_2}=\dfrac{1}{50}=0.02\). The loop gain is \(T=A\,f=10^4\times0.02=200\)." "\n" r"Common mistake: using \(T=A\) (forgetting that the divider throws away 98% of the signal on its way back) or \(T=A\,R_2/R_1\).",
          tol=0.01, fig=fig_noninverting("R₁ = 1 kΩ", "R₂ = 49 kΩ"), alt="Non-inverting amplifier with R1 = 1 kΩ and R2 = 49 kΩ; op-amp gain A = 10^4.")
    s.mc(r"Distortion generated at the amplifier's output is reduced by feedback. If the input is adjusted so that the output signal has the same amplitude as without feedback, by what factor is the output distortion reduced?",
         r"\(1+T\)",
         [r"\(T^2\)", r"\(G\)", r"It is not reduced; feedback only changes the gain"],
         r"A disturbance \(s_{noise}\) added at the output appears at the output as \(\dfrac{s_{noise}}{1+T}\) (reader Eq. 17.13), so for the same signal level the disturbance is \(1+T\) times smaller. The loop notices any unwanted output change as an error and corrects it." "\n"
         r"• Gain \(G\) is the forward gain, not the loop's rejection factor." "\n" r"• Saying nothing changes ignores Eq. 17.13.",
         fig=fig_loop_noise(), alt="Feedback loop with a disturbance injected at the output of block G.")
    T_ = 200.0
    err = 1 / (1 + T_) * 100
    s.num(r"With a loop gain of \(T=200\), what is the fractional gain error \(\dfrac{1/f-G_{closed}}{1/f}\) of the closed-loop amplifier, in percent?",
          err, "%",
          T(r"\(G_{closed}=\dfrac{G}{1+T}\) and \(1/f=G/T\), so \(\dfrac{G_{closed}}{1/f}=\dfrac{T}{1+T}\) and the error is \(1-\dfrac{T}{1+T}=\dfrac{1}{1+T}=\dfrac{1}{201}=<<e>>\%\)." "\n" r"Rule of thumb: the percent error is about \(100/T\).", e=g_(err, 4)),
          tol=0.02, fig=fig_feedback_blocks(), alt="Negative feedback loop block diagram.")
    s.round(3)
    s.mc(r"A system without feedback has output \(G\,s_{in}+s_{noise}\). With feedback the output is \(\dfrac{G}{1+T}s_{in}+\dfrac{1}{1+T}s_{noise}\), with \(T=100\). You apply the SAME input amplitude in both cases. What happens to the signal-to-noise ratio at the output?",
         r"Unchanged: the signal AND the noise are both reduced by \(1+T\). You only gain if you raise the input to restore the output level",
         [r"Improves by a factor of 101, since the noise is divided by 101", r"Gets worse by a factor of 101, since the gain fell by 101", r"Improves by a factor of 100, since \(T=100\)"],
         r"With the same input, the output signal falls by \(1+T\) (the closed-loop gain \(G/(1+T)\) is lower) and the output noise also falls by \(1+T\), so the ratio \(\dfrac{G\,s_{in}}{s_{noise}}\) is unchanged." "\n"
         r"The benefit appears when you compare at equal OUTPUT level: the input must be \(1+T\) times larger, and the noise injected at the output is still \(1+T\) times smaller, so the SNR improves by \(1+T\) (if the input signal can be raised for free)." "\n"
         r"• 'Improves by 101' is only right when the output amplitude is held fixed; here the input is fixed.",
         fig=fig_loop_noise(), alt="Feedback loop with a disturbance injected at the output of block G.")
    A, rs, rf = 1e4, 1e3, 9e3
    s.mc(r"An inverting amplifier with \(R_S=1\ \mathrm{k\Omega}\), \(R_F=9\ \mathrm{k\Omega}\) uses an op-amp with gain \(A=10^4\). Breaking the loop at the op-amp's output, what is the magnitude of the loop gain?",
         r"\(1000\), since the voltage returning to \(V^-\) is \(R_S/(R_S+R_F)=0.1\) of \(v_o\), and \(T=A\cdot0.1\)",
         [r"\(9000\), using \(R_F/(R_S+R_F)\)", r"\(10^{4}\), the op-amp gain alone", r"\(9\times10^{4}\), using \(A\,R_F/R_S\)"],
         r"With \(v_s=0\), the output voltage reaches the inverting node through the divider \(R_S\) (to ground) and \(R_F\): \(V^-=v_o\dfrac{R_S}{R_S+R_F}=0.1\,v_o\) (reader Eq. 17.36–17.37, \(f=\dfrac{R_S}{R_S+R_F}\)). The op-amp multiplies \(V^-\) by \(-A\), so \(|T|=A f=1000\)." "\n"
         r"The OTHER divider ratio, \(g=\dfrac{R_F}{R_S+R_F}=0.9\), is how the INPUT reaches \(V^-\); it matters for the gain but not for the loop gain." "\n"
         r"Reader note: Eq. 17.36 is correct as printed (\(V^-=v_o\frac{R_S}{R_S+R_F}+v_s\frac{R_F}{R_S+R_F}\)); students often swap the two weights.",
         fig=fig_inverting("R_S = 1 kΩ", "R_F = 9 kΩ", "vₛ", "vₒ"),
         alt="Inverting op-amp amplifier with R_S = 1 kΩ in series with the input, R_F = 9 kΩ from output back to the inverting input, non-inverting input grounded.")
    f = 0.01
    Tmin = 1 / 0.0005 - 1
    s.num(r"A non-inverting amplifier has \(f=0.01\) (ideal gain 100). The gain error must be at most 0.05%. What minimum op-amp gain \(A\) is required?",
          Tmin / f, "V/V",
          T(r"The fractional error is \(\dfrac{1}{1+T}\le 0.0005\), so \(1+T\ge2000\) and \(T\ge1999\)." "\n" r"Since \(T=A f\), \(A=\dfrac{T}{f}=\dfrac{1999}{0.01}=<<a>>\), about \(2\times10^5\)." "\n" r"Note the gotcha: the required \(A\) depends on \(f\). A larger \(f\) (smaller closed-loop gain) needs proportionally less \(A\).", a=tex(Tmin / f, 4)),
          tol=0.02, fig=fig_noninverting("R₁", "R₂ = 99 R₁"), alt="Non-inverting amplifier with R2 = 99 R1 so that f = 0.01.")
    s.round(4)
    T0, fp = 2000.0, 100.0
    fu = fp * math.sqrt(T0 ** 2 - 1)
    fb = fig_bode_mag([(1, 66.02), (100, 66.02), (2e5, 0)], 1, 1e6, 80, ylab="|T| (dB)", title="Loop gain magnitude",
                      extra=lambda X, Y: b2b_text(X(100), Y(66.02) - 8, "66 dB (T₀ = 2000)", size=10, anchor="start") + b2b_text(X(2e5), Y(0) - 8, "|T| = 1 ?", size=10, anchor="middle"))
    s.num(r"Preview of gain-bandwidth. A loop has \(T(jf)=\dfrac{2000}{1+jf/(100\ \mathrm{Hz})}\). At what frequency does \(|T|\) fall to 1? Give the exact value in kHz.",
          fu / 1e3, "kHz",
          T(r"Set \(|T|=1\): \(\dfrac{2000}{\sqrt{1+(f/100)^2}}=1\Rightarrow f=100\sqrt{2000^2-1}=<<f>>\ \mathrm{Hz}\approx200\ \mathrm{kHz}\)." "\n" r"Equivalent shortcut: gain × frequency stays near \(2000\times100\ \mathrm{Hz}=200\ \mathrm{kHz}\) on the \(-20\ \mathrm{dB/decade}\) slope. This 'unity-loop-gain frequency' sets the bandwidth in the next skills.", f=tex(fu, 6)),
          tol=0.02, fig=fb,
          alt="Bode magnitude sketch: flat at 66 dB up to a 100 Hz pole, then falling at 20 dB per decade, crossing 0 dB at an unknown frequency.", preview=["gbw", "stability"])
    s.mc(r"Preview of dynamic errors. The loop gain of an amplifier is \(T(j\omega)=\dfrac{T_0}{1+j\omega/\omega_p}\). The closed-loop gain error is about \(1/|1+T|\). As the signal frequency rises well above \(\omega_p\), what happens to the gain error?",
         r"It grows, because \(|T|\) falls with frequency, so there is less loop gain to correct errors",
         [r"It stays constant at \(1/(1+T_0)\)", r"It shrinks, because high frequencies are attenuated more", r"It becomes exactly zero once \(|T|<1\)"],
         r"The error is controlled by the available loop gain AT the signal frequency. Above \(\omega_p\), \(|T|\approx T_0\omega_p/\omega\) drops by 20 dB per decade, so the error \(\approx 1/|T|\) rises by 20 dB per decade, until \(|T|\approx1\) where the feedback has essentially no effect." "\n"
         r"• It is constant only at low frequency." "\n" r"• At \(|T|<1\) the loop has almost no authority: the error is large, not zero.",
         fig=fig_bode_mag([(1, 66.02), (100, 66.02), (2e5, 0)], 1, 1e6, 80, ylab="|T| (dB)", title="Loop gain magnitude"),
         alt="Bode magnitude sketch of the loop gain: flat at 66 dB, then falling at 20 dB per decade above a pole.", preview=["fb-errors", "opamp-fr"])
    Tn = -0.8
    ans = 1 / (1 + Tn)
    s.num(r"Preview of stability. At some frequency a loop picks up so much phase lag that the loop gain is \(T=-0.8\) (magnitude 0.8, phase \(-180^\circ\)), so the feedback ADDS to the input instead of subtracting. By what factor is the closed-loop gain \(\dfrac{G}{1+T}\) larger than the forward gain \(G\) at that frequency?",
          ans, "×",
          r"\(\dfrac{G_{closed}}{G}=\dfrac{1}{1+T}=\dfrac{1}{1+(-0.8)}=\dfrac{1}{0.2}=5\)." "\n" r"So the response has a 5× peak at that frequency, even though \(|T|<1\). If \(T\) reached \(-1\) the denominator would vanish: the closed loop would produce output with no input at all, which is oscillation. That is why the stability skill asks how far \(T\) stays from \(-1\) when \(|T|=1\).",
          tol=0.02, fig=F, alt="Feedback block diagram with the loop opened; at one frequency T = -0.8.", preview=["stability"])
    return s

# ====================================================================== opamp-models
def opamp_models():
    s = Skill('opamp-models')
    GM = fig_gm()
    s.round(1)
    s.mc(r"The simplest op-amp model (a voltage-controlled voltage source) with input resistance \(R_{in}\), gain \(A\) and output resistance \(R_{out}\) captures which imperfections?",
         r"Finite gain \(A\), finite input resistance and non-zero output resistance, but NOT frequency dependence",
         [r"Only the frequency dependence of the gain", r"Slew rate and offset voltage as well as finite gain", r"Nothing: it is exactly the ideal op-amp"],
         r"The VCVS model has \(v_{out}=A\,v_{in}\) behind \(R_{out}\), with \(R_{in}\) across the input (reader Fig. 17.8). It is a linear, frequency-independent model, so it cannot describe gain falling with frequency (that needs the \(R_x\)-\(C_x\) node), slew rate, or offsets." "\n"
         r"• The ideal op-amp is the limit \(A\to\infty\), \(R_{in}\to\infty\), \(R_{out}\to0\) of this same model.",
         fig=fig_vcvs(rs=False, rl=False), alt="Op-amp VCVS model: input resistance across the input terminals; a dependent voltage source A·v_in in series with R_out drives the output.")
    s.mc(r"In terms of the VCVS model parameters \(A\), \(R_{in}\), \(R_{out}\), the IDEAL op-amp is the limit",
         r"\(A\to\infty\), \(R_{in}\to\infty\), \(R_{out}\to0\)",
         [r"\(A\to0\), \(R_{in}\to0\), \(R_{out}\to\infty\)", r"\(A\to\infty\), \(R_{in}\to0\), \(R_{out}\to\infty\)", r"\(A\to1\), \(R_{in}\to\infty\), \(R_{out}\to0\)"],
         r"An ideal voltage amplifier draws no input current (\(R_{in}=\infty\)), produces its output regardless of the load (\(R_{out}=0\)), and has unlimited gain so that the input difference is driven to zero in feedback (\(A=\infty\))." "\n" r"The other combinations describe a poor amplifier: low \(R_{in}\) loads the source, high \(R_{out}\) loses gain into a load.",
         fig=fig_vcvs(rs=False, rl=False), alt="VCVS op-amp model with R_in, A·v_in source and R_out.")
    Gm, Rx = 2e-3, 500e3
    s.num(r"In the single-pole op-amp model (figure), an ideal transconductor with \(G_m=2\ \mathrm{mS}\) drives a node with \(R_x=500\ \mathrm{k\Omega}\) in parallel with \(C_x\). What is the DC gain \(A_0=G_mR_x\)?",
          Gm * Rx, "V/V",
          r"At DC the capacitor is an open circuit, so the current \(G_m v_d\) flows only through \(R_x\): \(v_x=G_mR_xv_d\). Thus \(A_0=G_mR_x=2\times10^{-3}\ \mathrm{S}\times5\times10^{5}\ \Omega=1000\) (reader Eq. 17.15)." "\n" r"The unity buffer after the node doesn't change the gain.",
          tol=0.01, fig=GM, alt="Op-amp model: transconductor Gm driving a node with Rx and Cx to ground, followed by a unity-gain buffer to the output.")
    s.round(2)
    Gm, Rx, Cx = 1e-3, 1e6, 5e-12
    fp = 1 / (2 * math.pi * Rx * Cx)
    s.num(r"An op-amp model has \(G_m=1\ \mathrm{mS}\), \(R_x=1\ \mathrm{M\Omega}\), \(C_x=5\ \mathrm{pF}\). What is the open-loop \(-3\ \mathrm{dB}\) frequency \(f_{-3\mathrm{dB}}\), in kHz?",
          fp / 1e3, "kHz",
          T(r"The node impedance is \(R_x\parallel C_x\), a single pole at \(\omega_{-3dB}=\dfrac{1}{R_xC_x}=\dfrac{1}{10^{6}\cdot5\times10^{-12}}=2\times10^{5}\ \mathrm{rad/s}\) (reader Eq. 17.16)." "\n" r"In hertz, divide by \(2\pi\): \(f_{-3dB}=<<f>>\ \mathrm{kHz}\)." "\n" r"Common mistake: leaving the answer in rad/s (200 krad/s).", f=g_(fp / 1e3, 4)),
          tol=0.02, fig=GM, alt="Op-amp single-pole model with Rx and Cx at the high-impedance node.")
    gbw = Gm / (2 * math.pi * Cx)
    s.num(r"For the same model (\(G_m=1\ \mathrm{mS}\), \(R_x=1\ \mathrm{M\Omega}\), \(C_x=5\ \mathrm{pF}\)), what is the gain-bandwidth product \(A_0\cdot f_{-3\mathrm{dB}}\), in MHz?",
          gbw / 1e6, "MHz",
          T(r"\(A_0=G_mR_x=1000\) and \(f_{-3dB}=31.83\ \mathrm{kHz}\), so \(A_0f_{-3dB}=<<g>>\ \mathrm{MHz}\)." "\n" r"Equivalently \(\omega_u=\dfrac{G_m}{C_x}=\dfrac{10^{-3}}{5\times10^{-12}}=2\times10^{8}\ \mathrm{rad/s}\), i.e. \(f_u=\dfrac{G_m}{2\pi C_x}\): \(R_x\) cancels out of the product (reader Eq. 17.17).", g=g_(gbw / 1e6, 4)),
          tol=0.02, fig=GM, alt="Op-amp single-pole model with Gm, Rx, Cx and a unity buffer.")
    s.mc(r"In the single-pole model, \(R_x\) is doubled while \(G_m\) and \(C_x\) stay the same. What happens to the DC gain \(A_0\) and the gain-bandwidth product?",
         r"\(A_0\) doubles, the pole halves, and the gain-bandwidth product is unchanged",
         [r"\(A_0\) doubles and the gain-bandwidth product doubles", r"\(A_0\) is unchanged and the pole halves", r"\(A_0\) halves and the gain-bandwidth product halves"],
         r"\(A_0=G_mR_x\) doubles. The pole \(\omega_{-3dB}=1/(R_xC_x)\) halves. The product \(A_0\,\omega_{-3dB}=G_m/C_x\) does not contain \(R_x\), so it stays put: more DC gain is bought with less bandwidth." "\n" r"• GBW is set by \(G_m\) and \(C_x\) only.",
         fig=GM, alt="Op-amp single-pole model: Gm stage, Rx and Cx at the output node, buffer.")
    s.round(3)
    s.mc(r"A model has the transconductor \(G_m\) feeding only a capacitor \(C_x\) (there is no \(R_x\)), followed by an ideal buffer. What is true of its open-loop gain?",
         r"The DC gain is infinite (it is an integrator), yet the unity-gain frequency is still \(\omega_u=G_m/C_x\)",
         [r"The gain is zero at DC and rises at 20 dB/decade", r"The unity-gain frequency is infinite, since \(R_x\to\infty\)", r"The model has no frequency dependence"],
         r"With no resistor, DC current has nowhere to go but into \(C_x\): \(v_x=\dfrac{G_mv_d}{j\omega C_x}\), so \(A(j\omega)=\dfrac{G_m}{j\omega C_x}=\dfrac{\omega_u}{j\omega}\). The gain is infinite as \(\omega\to0\), falls at \(-20\) dB/decade, and equals 1 at \(\omega_u=G_m/C_x\) (reader Fig. 17.12 and Eq. 17.17)." "\n" r"This is the high-frequency form \(A\approx\omega_u/j\omega\) of any single-pole op-amp, extended down to DC.",
         fig=GM, alt="Op-amp model drawn with Gm, Rx and Cx; in this question Rx is removed so only Cx loads the node.")
    A, Rs, Rin, Rout, RL = 1000.0, 1e3, 9e3, 100.0, 300.0
    ans = Rin / (Rs + Rin) * A * RL / (RL + Rout)
    s.num(r"A source with \(R_s=1\ \mathrm{k\Omega}\) drives an amplifier modeled by \(R_{in}=9\ \mathrm{k\Omega}\), a VCVS \(A\,v_{in}\) with \(A=1000\), and \(R_{out}=100\ \Omega\), loaded by \(R_L=300\ \Omega\). What is the overall gain \(v_{out}/v_s\)?",
          ans, "V/V",
          T(r"Two resistive dividers hide the gain loss. Input: \(v_{in}=v_s\dfrac{R_{in}}{R_s+R_{in}}=0.9\,v_s\). Output: \(v_{out}=A\,v_{in}\dfrac{R_L}{R_L+R_{out}}=A\,v_{in}\times0.75\)." "\n" r"Overall: \(0.9\times1000\times0.75=<<a>>\) V/V, 32.5% below the 'open' gain \(A=1000\). Common mistake: reading \(A=1000\) as the gain with a source and load attached.", a=g_(ans, 4)),
          tol=0.01, fig=fig_vcvs(labels=("Rₛ = 1k", "R_in = 9k", "R_out = 100", "Rₗ = 300")), alt="Source with series resistance Rs drives the model input resistance Rin; the dependent source A·v_in with R_out drives a load RL.")
    s.mc(r"Real op-amps place an output buffer after the input transconductance (OTA) stage. Why?",
         r"The OTA stage has a very high output impedance, so a resistive load would collapse its gain; the buffer provides low output impedance",
         [r"The buffer adds extra voltage gain of 1000", r"The buffer removes the dominant pole", r"The OTA produces a voltage, which the buffer converts to a current"],
         r"The OTA converts the input voltage difference to a CURRENT into a high-impedance node (\(R_x\) and \(C_x\)); that node cannot drive a low-resistance load without its voltage collapsing (reader Sec. 17.4.5). The unity-gain buffer copies the node voltage and drives the load with a small \(R_{out}\)." "\n" r"• The buffer's gain is 1 (+1 in the figure), not 1000." "\n" r"• The pole belongs to \(R_xC_x\) and stays in the model." "\n" r"• The OTA output is a current; the buffer takes a voltage.",
         fig=GM, alt="Single-pole op-amp model: OTA, the high-impedance node Rx||Cx and the unity buffer toward the output.")
    s.round(4)
    gbw_f = 1e-3 / (2 * math.pi * 5e-12)
    ans = 0.1 * gbw_f / 1e6
    s.num(r"Preview of gain-bandwidth. The model with \(G_m=1\ \mathrm{mS}\), \(C_x=5\ \mathrm{pF}\) has \(f_u=G_m/2\pi C_x=31.83\ \mathrm{MHz}\). It is placed in a non-inverting amplifier with \(f=0.1\) (ideal gain 10). A later skill shows that the closed-loop bandwidth is \(f\cdot f_u\). What is it, in MHz?",
          ans, "MHz",
          T(r"The loop gain at DC is \(T_0=A_0f\), and feedback extends the pole by \(1+T_0\) (previous skills), giving \(\approx A_0 f\cdot f_{-3dB}=f\cdot f_u\). So \(BW_{closed}=0.1\times31.83\ \mathrm{MHz}=<<a>>\ \mathrm{MHz}\)." "\n" r"Gain 10 times the bandwidth 3.18 MHz = 31.8 MHz: the same gain-bandwidth product \(G_m/2\pi C_x\) as before. (Exactly, \((1+A_0f)f_{-3dB}=101\times31.83\ \mathrm{kHz}=3.21\ \mathrm{MHz}\); the 1% difference is within tolerance.) Reader note: Eq. 17.29 prints \(\omega_0=fT\) but should read \(\omega_0=f\,\omega_u\) (\(T=Gf\) already contains \(f\)).", a=g_(ans, 4)),
          tol=0.02, fig=fig_noninverting("R₁ (f = 0.1)", "R₂ = 9 R₁"), alt="Non-inverting amplifier with feedback factor 0.1, built from the single-pole op-amp model.", preview=["gbw"])
    Imax, Cx = 100e-6, 5e-12
    sr = Imax / Cx / 1e6
    s.mc(r"Preview of slew rate. In the model, the OTA current can never exceed \(I_{max}=100\ \mu\mathrm{A}\). For a big input step the OTA saturates and charges \(C_x=5\ \mathrm{pF}\) at constant current. How fast does the internal node ramp?",
         r"\(20\ \mathrm{V/\mu s}\)",
         [r"\(2\ \mathrm{V/\mu s}\)", r"\(200\ \mathrm{V/\mu s}\)", r"\(0.02\ \mathrm{V/\mu s}\)"],
         T(r"A constant current into a capacitor gives a linear ramp: \(\dfrac{dv_x}{dt}=\dfrac{I_{max}}{C_x}=\dfrac{100\ \mu\mathrm{A}}{5\ \mathrm{pF}}=2\times10^{7}\ \mathrm{V/s}=<<s>>\ \mathrm{V/\mu s}\) (reader Eq. 18.23)." "\n" r"Unit check: \(10^{-4}/(5\times10^{-12})=2\times10^7\), and \(1\ \mathrm{V/\mu s}=10^6\ \mathrm{V/s}\). The other choices are powers-of-ten slips. This 'speed limit' is the op-amp's slew rate.", s=g_(sr, 3)),
         fig=fig_gm(extra=b2b_text(90, 125, "I ≤ 100 µA", size=10)), alt="Single-pole op-amp model with the transconductor current limited to 100 microamps charging Cx.", preview=["slew"])
    A0, Vos = 1000.0, 2e-3
    ans = A0 * Vos
    oa, _, _, _ = b2b_opamp(130, 70, 56, 60)
    fos = b2b_svg(330, 130, oa + b2b_wire(130, 55, 105, 55) + b2b_circle(95, 55, 10) + b2b_text(95, 52, "+", size=10) + b2b_text(95, 63, "−", size=10) + b2b_text(95, 36, "V_os = 2 mV", size=11) + b2b_wire(85, 55, 60, 55, 60, 65) + b2b_ground(60, 65) + b2b_wire(130, 85, 116, 85) + b2b_ground(116, 85) + b2b_wire(186, 70, 240, 70) + b2b_circle(243, 70, 3) + b2b_text(258, 74, "vₒ = ?", anchor="start"), "Op-amp with offset source")
    s.num(r"Preview of offset voltage. Real op-amps behave as if a small DC source \(V_{os}\) sits in series with one input of an offset-free amplifier. With both inputs grounded (open loop, \(A_0=1000\) at DC) and \(V_{os}=2\ \mathrm{mV}\), what is \(v_o\)?",
          ans, "V",
          r"The offset source adds directly to the differential input: \(v_d=V_{os}-0\). The model then gives \(v_o=A_0\,v_d=1000\times2\ \mathrm{mV}=2\ \mathrm{V}\)." "\n" r"An 'ideal' model would say \(v_o=0\) for zero input. Real op-amps with 1000× gain turn a 2 mV mismatch into 2 V (and with \(A=10^5\) would rail out), which is why offset is modeled and nulled. The next skills show how feedback tames it.",
          tol=0.02, fig=fos, alt="Op-amp with both inputs grounded, and a small 2 mV offset source in series with one input.", preview=["offset"])
    return s

# ====================================================================== inverting
def inverting():
    s = Skill('inverting')
    def fi(r1, r2, vin="vᵢₙ", vout="vₒᵤₜ", **k): return fig_inverting(r1, r2, vin, vout, **k)
    s.round(1)
    s.mc(r"For an ideal op-amp, the inverting amplifier in the figure has closed-loop gain \(v_{out}/v_{in}\) equal to",
         r"\(-R_2/R_1\)",
         [r"\(+R_2/R_1\)", r"\(1+R_2/R_1\)", r"\(-R_1/R_2\)"],
         r"With the \(+\) input grounded, the inverting input is a virtual ground. The input current \(v_{in}/R_1\) must flow through \(R_2\) (the op-amp draws none), so \(v_{out}=0-\dfrac{v_{in}}{R_1}R_2\Rightarrow\dfrac{v_{out}}{v_{in}}=-\dfrac{R_2}{R_1}\) (reader Eq. 17.41)." "\n" r"• \(1+R_2/R_1\) is the NON-inverting gain." "\n" r"• \(R_1/R_2\) flips the ratio; the feedback resistor goes in the numerator.",
         fig=fi("R₁", "R₂"), alt="Inverting op-amp amplifier: R1 from the input to the − terminal, R2 from the output to the − terminal, + terminal grounded.")
    s.mc(r"In an inverting amplifier with an ideal op-amp and a normal output (not saturated), the inverting-input voltage \(V^-\) is very close to 0 V. Why?",
         r"The huge gain forces \(V^+-V^-\) to be tiny, and \(V^+\) is grounded, so \(V^-\approx0\) (a virtual ground)",
         [r"Because the inverting input is physically connected to ground", r"Because \(R_1\) and \(R_2\) are equal", r"Because the op-amp draws a large current from the input"],
         r"\(v_{out}=A(V^+-V^-)\) with finite \(v_{out}\) and \(A\to\infty\) requires \(V^+-V^-\to0\). Since \(V^+=0\), \(V^-\approx0\): a 'virtual' ground, at 0 V but NOT connected to ground." "\n" r"• The node isn't wired to ground; it sits at 0 V because of feedback." "\n" r"• Any resistor values give a virtual ground." "\n" r"• The input current of an ideal op-amp is zero.",
         fig=fi("R₁", "R₂"), alt="Inverting op-amp amplifier with the + input grounded.")
    R1, R2, vin = 2e3, 10e3, 0.3
    s.num(r"The inverting amplifier has \(R_1=2\ \mathrm{k\Omega}\), \(R_2=10\ \mathrm{k\Omega}\) and \(v_{in}=0.3\ \mathrm{V}\). With an ideal op-amp, what is \(v_{out}\)?",
          -R2 / R1 * vin, "V",
          r"Gain \(=-R_2/R_1=-10/2=-5\), so \(v_{out}=-5\times0.3\ \mathrm{V}=-1.5\ \mathrm{V}\)." "\n" r"Check with currents: \(i=0.3/2\ \mathrm{k\Omega}=150\ \mu\mathrm{A}\) flows through \(R_2\), dropping \(150\ \mu\mathrm{A}\times10\ \mathrm{k\Omega}=1.5\ \mathrm{V}\) from the virtual ground (0 V) down to \(v_{out}=-1.5\ \mathrm{V}\).",
          tol=0.01, fig=fi("R₁ = 2 kΩ", "R₂ = 10 kΩ", "0.3 V"), alt="Inverting amplifier with R1 = 2 kΩ, R2 = 10 kΩ, and a 0.3 V input.")
    s.round(2)
    s.num(r"An inverting amplifier uses \(R_1=4.7\ \mathrm{k\Omega}\) and \(R_2=47\ \mathrm{k\Omega}\) (ideal op-amp). What resistance does the source \(v_{in}\) see looking into the input terminal?",
          4.7e3, "Ω",
          r"The right end of \(R_1\) is the virtual ground, so \(i_{in}=\dfrac{v_{in}-0}{R_1}\) and \(R_{in}=\dfrac{v_{in}}{i_{in}}=R_1=4.7\ \mathrm{k\Omega}=4700\ \Omega\)." "\n" r"Unlike the non-inverting amplifier (\(R_{in}\to\infty\)), the inverting amplifier loads its source with exactly \(R_1\), a design constraint when the source is weak. Common mistake: answering \(R_1+R_2\) or \(R_1\parallel R_2\).",
          tol=0.01, fig=fi("R₁ = 4.7 kΩ", "R₂ = 47 kΩ"), alt="Inverting amplifier with R1 = 4.7 kΩ and R2 = 47 kΩ; the question asks for the resistance seen at the input.")
    A, R1, R2 = 1000.0, 1e3, 9e3
    f = R1 / (R1 + R2); gg = R2 / (R1 + R2)
    ans = -A * gg / (1 + A * f)
    s.num(r"The amplifier has \(R_1=1\ \mathrm{k\Omega}\), \(R_2=9\ \mathrm{k\Omega}\) (ideal gain \(-9\)), but the op-amp has finite gain \(A=1000\). The exact gain is \(\dfrac{v_{out}}{v_{in}}=\dfrac{-A\,g}{1+A\,f}\) with \(g=\dfrac{R_2}{R_1+R_2}\), \(f=\dfrac{R_1}{R_1+R_2}\). What is it?",
          ans, "V/V",
          T(r"\(f=0.1\), \(g=0.9\). Then \(\dfrac{-1000(0.9)}{1+1000(0.1)}=\dfrac{-900}{101}=<<a>>\)." "\n" r"That is 1% smaller in magnitude than the ideal \(-9\): the loop gain \(T=Af=100\), so the error is about \(1/(1+T)\) (reader Eq. 17.40). Common mistake: using \(A\,f\) in place of \(A\,g\) in the numerator.", a=g_(ans)),
          tol=0.01, fig=fi("R₁ = 1 kΩ", "R₂ = 9 kΩ"), alt="Inverting amplifier with R1 = 1 kΩ and R2 = 9 kΩ and a finite-gain op-amp A = 1000.")
    s.mc(r"In the inverting amplifier with an ideal op-amp, \(R_2\) is doubled while \(R_1\) and \(v_{in}\) stay fixed. What happens to the current through \(R_1\)?",
         r"It is unchanged: the virtual ground holds the right end of \(R_1\) at 0 V regardless of \(R_2\)",
         [r"It doubles", r"It halves", r"It becomes zero"],
         r"\(i_1=\dfrac{v_{in}-V^-}{R_1}=\dfrac{v_{in}}{R_1}\) because \(V^-\approx0\). Doubling \(R_2\) changes the OUTPUT voltage (the same current through a larger resistor, \(v_{out}=-i_1R_2\)), not the input current. This independence is why one can trim the gain with \(R_2\) without disturbing the source." "\n" r"• The current would only change if the virtual-ground assumption broke (for example the output saturated).",
         fig=fi("R₁", "R₂ → 2R₂"), alt="Inverting amplifier in which R2 is doubled.")
    s.round(3)
    s.mc(r"Which closed-loop voltage gain can be realized with a single ideal-op-amp stage (inverting or non-inverting)?",
         r"\(-0.1\) with an inverting stage (\(R_2=R_1/10\))",
         [r"\(+0.5\) with a non-inverting stage", r"\(+0.9\) with an inverting stage", r"\(0\) with a non-inverting stage"],
         r"The inverting gain \(-R_2/R_1\) can have any magnitude, including less than 1, but is always negative. The non-inverting gain \(1+R_2/R_1\) is always \(\ge 1\) (with \(R_2=0\) it is a follower). So the correct choice is \(-0.1\); a positive gain below 1 needs an extra divider." "\n" r"• \(+0.5\) and \(0\) are impossible for non-inverting (\(\ge1\))." "\n" r"• An inverting stage always gives a NEGATIVE gain, so \(+0.9\) is impossible.",
         fig=fi("R₁", "R₂"), alt="Inverting amplifier with R1 and R2.")
    s.mc(r"Supplies are \(\pm12\ \mathrm{V}\), \(R_2/R_1=20\) and \(v_{in}=0.8\ \mathrm{V}\) (otherwise ideal op-amp). What is \(v_{out}\)?",
         r"About \(-12\ \mathrm{V}\) (clipped at the negative rail; the ideal result of \(-16\ \mathrm{V}\) is impossible)",
         [r"\(-16\ \mathrm{V}\)", r"\(+12\ \mathrm{V}\)", r"\(0\ \mathrm{V}\), since the virtual ground forces zero output"],
         r"The ideal equation gives \(-20\times0.8=-16\ \mathrm{V}\), beyond the supply. The output cannot exceed the rails (reader Sec. 18.4.1), so it clips at about \(-12\ \mathrm{V}\) (in practice a bit less)." "\n" r"While clipped, the feedback loop is no longer in control: the input terminals are no longer at the same voltage, so the 'virtual ground' assumption (and the gain formula) fails. The largest linear input is \(12/20=0.6\ \mathrm{V}\)." "\n" r"• The virtual ground is at the inverting INPUT, not the output.",
         fig=fi("R₁", "R₂ = 20 R₁", "0.8 V", "vₒ  (rails ±12 V)"), alt="Inverting amplifier with gain -20 and a 0.8 V input; supply rails are +12 V and -12 V.")
    fu, R1, R2 = 1e6, 1e3, 9e3
    gg = R2 / (R1 + R2)
    ans = gg * fu / 1e3
    s.num(r"An op-amp has a gain-bandwidth product (unity-gain frequency) of 1 MHz. Used as an inverting amplifier with \(R_1=1\ \mathrm{k\Omega}\), \(R_2=9\ \mathrm{k\Omega}\), what is the closed-loop gain-bandwidth product \(|A_{cl}|\cdot BW\), in kHz? (Reader Eq. 17.43: \(GBW=A_0\,g\,\omega_{-3dB}\).)",
          ans, "kHz",
          T(r"The closed-loop bandwidth is \(\dfrac{f_u}{1+R_2/R_1}=\dfrac{1\ \mathrm{MHz}}{10}=100\ \mathrm{kHz}\) (set by \(f\), as for the non-inverting amplifier). But the DC gain magnitude is only \(R_2/R_1=9\), not 10, because the input is attenuated by \(g=0.9\)." "\n" r"Product: \(9\times100\ \mathrm{kHz}=<<a>>\ \mathrm{kHz}=g\,f_u\), 10% below the non-inverting amplifier's \(1\ \mathrm{MHz}\). Common mistake: assuming GBW is always the op-amp's 1 MHz." "\n" r"Reader typo: Eq. 17.42 writes \(v_o/v_o\); it should be \(v_o/v_s\).", a=g_(ans, 4)),
          tol=0.02, fig=fi("R₁ = 1 kΩ", "R₂ = 9 kΩ"), alt="Inverting amplifier built from an op-amp with 1 MHz unity-gain frequency, R1 = 1 kΩ and R2 = 9 kΩ.")
    s.round(4)
    R2 = 40e3; ra, rb = 10e3, 20e3; v1, v2 = 0.2, -0.1
    ans = -(R2 / ra * v1 + R2 / rb * v2)
    o, nin, pin, out = b2b_opamp(170, 80, 56, 60)
    fsum = b2b_svg(380, 150,
        b2b_text(14, 40, "v₁") + b2b_circle(26, 36, 3) + b2b_wire(29, 36, 40, 36) + b2b_resistor(40, 36, 60, label="10 kΩ") + b2b_wire(100, 36, 140, 36) +
        b2b_text(14, 78, "v₂") + b2b_circle(26, 74, 3) + b2b_wire(29, 74, 40, 74) + b2b_resistor(40, 74, 60, label="20 kΩ") + b2b_wire(100, 74, 120, 74, 120, 36) + b2b_dot(120, 36) +
        b2b_wire(140, 36, 140, 65, 170, 65) + b2b_dot(140, 36) + o +
        b2b_wire(170, 95, 156, 95) + b2b_ground(156, 95) + b2b_wire(140, 36, 140, 14, 160, 14) + b2b_resistor(160, 14, 70, label="R₂ = 40 kΩ", lpos=(195, 4)) +
        b2b_wire(230, 14, 255, 14, 255, 80) + b2b_wire(226, 80, 300, 80) + b2b_dot(255, 80) + b2b_circle(303, 80, 3) + b2b_text(318, 84, "vₒᵤₜ", anchor="start"), "Summing amplifier")
    s.num(r"Preview of common-source gain (an inverting stage in disguise). Two sources feed the inverting node through \(10\ \mathrm{k\Omega}\) and \(20\ \mathrm{k\Omega}\) resistors, with \(R_2=40\ \mathrm{k\Omega}\) feedback (ideal op-amp). With \(v_1=0.2\ \mathrm{V}\) and \(v_2=-0.1\ \mathrm{V}\), what is \(v_{out}\)?",
          ans, "V",
          T(r"The inverting node is a virtual ground, so the input currents add: \(i=\dfrac{v_1}{10\ \mathrm{k}}+\dfrac{v_2}{20\ \mathrm{k}}=20\ \mu\mathrm{A}-5\ \mu\mathrm{A}=15\ \mu\mathrm{A}\)." "\n" r"All of it flows through \(R_2\): \(v_{out}=-iR_2=-15\ \mu\mathrm{A}\times40\ \mathrm{k\Omega}=<<a>>\ \mathrm{V}\), i.e. \(-(4v_1+2v_2)\) (a weighted sum). Later you will meet transistor amplifiers whose gain is also an inverting ratio \(-g_mR\); the same virtual-ground thinking helps.", a=g_(ans, 3)),
          tol=0.02, fig=fsum, alt="Summing inverting amplifier: v1 through 10 kΩ and v2 through 20 kΩ into the inverting input; R2 = 40 kΩ feedback; + input grounded.", preview=["cs-analysis"])
    ip, Rf = 2e-6, 500e3
    ans = -ip * Rf
    o, nin, pin, out = b2b_opamp(150, 75, 56, 60)
    ftia = b2b_svg(340, 140,
        b2b_isource(50, 40, 50, label="2 µA") + b2b_wire(50, 40, 50, 30, 130, 30, 130, 60, 150, 60) + b2b_wire(50, 90, 50, 105) + b2b_ground(50, 105) + o +
        b2b_wire(150, 90, 136, 90) + b2b_ground(136, 90) + b2b_wire(130, 30, 130, 14, 160, 14) + b2b_dot(130, 30) +
        b2b_resistor(160, 14, 60, label="R₂ = 500 kΩ", lpos=(190, 5)) + b2b_wire(220, 14, 240, 14, 240, 75) + b2b_wire(206, 75, 280, 75) + b2b_dot(240, 75) + b2b_circle(283, 75, 3) + b2b_text(296, 79, "vₒᵤₜ", anchor="start"),
        "Transimpedance amplifier")
    s.num(r"Preview of transimpedance. A photodiode is modeled as a \(2\ \mu\mathrm{A}\) current source driving the inverting input of an ideal-op-amp inverting stage with \(R_2=500\ \mathrm{k\Omega}\) (no \(R_1\)). The current flows into the inverting node. What is \(v_{out}\)?",
          ans, "V",
          r"The virtual ground absorbs the source current with no voltage developed at the input, and the op-amp pushes that entire current through \(R_2\) (the op-amp draws none): \(v_{out}=0-i\,R_2=-2\ \mu\mathrm{A}\times500\ \mathrm{k\Omega}=-1.0\ \mathrm{V}\)." "\n" r"The circuit converts current to voltage with gain \(-R_2\) (a 'transimpedance' amplifier, as the reader notes the inverting amplifier really is). The virtual ground keeps the source operating at 0 V, which matters for photodiodes and other current-output sensors.",
          tol=0.02, fig=ftia, alt="A 2 microamp current source feeds the inverting input; a 500 kΩ resistor connects the output back to the inverting input; + input grounded.", preview=["cs-analysis", "miller"])
    R, C, vin = 10e3, 100e-9, 1.0
    slope = -vin / (R * C) / 1e3
    o, nin, pin, out = b2b_opamp(150, 75, 56, 60)
    fint = b2b_svg(340, 140,
        b2b_text(20, 49, "1 V step") + b2b_circle(60, 60, 3) + b2b_wire(63, 60, 70, 60) + b2b_resistor(70, 60, 50, label="R = 10 kΩ") + b2b_wire(120, 60, 150, 60) + b2b_dot(130, 60) +
        o + b2b_wire(150, 90, 136, 90) + b2b_ground(136, 90) + b2b_wire(130, 60, 130, 20, 150, 20) + b2b_capacitor(150, 20, 60, label="C = 100 nF") + b2b_wire(210, 20, 240, 20, 240, 75) + b2b_wire(206, 75, 280, 75) + b2b_dot(240, 75) + b2b_circle(283, 75, 3) + b2b_text(296, 79, "vₒᵤₜ", anchor="start"),
        "Inverting integrator")
    s.mc(r"Preview of the Miller effect and integrators. In the inverting stage the feedback resistor is replaced by a capacitor \(C=100\ \mathrm{nF}\), with \(R=10\ \mathrm{k\Omega}\) at the input. A \(1\ \mathrm{V}\) step is applied at \(t=0\) (initial output 0 V, ideal op-amp). How fast does \(v_{out}\) change?",
         r"\(-1\ \mathrm{V/ms}\) (a linear ramp)",
         [r"\(-10\ \mathrm{V/ms}\)", r"\(-0.1\ \mathrm{V/ms}\)", r"\(+1\ \mathrm{V/ms}\)"],
         T(r"The virtual ground gives a constant input current \(i=\dfrac{1\ \mathrm{V}}{10\ \mathrm{k\Omega}}=100\ \mu\mathrm{A}\), and that same current charges \(C\): \(i=-C\dfrac{dv_{out}}{dt}\)." "\n" r"So \(\dfrac{dv_{out}}{dt}=-\dfrac{i}{C}=-\dfrac{100\ \mu\mathrm{A}}{100\ \mathrm{nF}}=-10^{3}\ \mathrm{V/s}=<<s>>\ \mathrm{V/ms}\)." "\n" r"The inverting sign (the output goes negative for a positive input) and the ramp are the point: a capacitor in the feedback path of an inverting amplifier will later appear as an enlarged input capacitance (Miller effect).", s=g_(slope, 3)),
         fig=fint, alt="Inverting amplifier with R = 10 kΩ at the input and a 100 nF capacitor in the feedback path; a 1 V step is applied.", preview=["miller"])
    return s

BUILD = [fb_intro, loop_gain, opamp_models, inverting]
if __name__ == "__main__":
    for fn in BUILD:
        sk = fn(); sk.save(); print("wrote", sk.sid, len(sk.qs))
