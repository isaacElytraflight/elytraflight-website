#!/usr/bin/env python3
"""Generate ME 132 batch B3 banks and explainers.

Skills: app-examples, cruise-control, equilibria, loop-tf, second-order-sys, ss-solution
Closed-form answers live here. skilltree/verify_me132_b3.py recomputes them
by signal equations, RK4, eigenvalue routines, or matrix exponentials.
"""
import json
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from templates import (
    block_diagram, mass_spring, matrix_fig, plot, splane, step_response,
)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
BANK = os.path.join(ROOT, "skilltree", "bank")
EXP = os.path.join(ROOT, "skilltree", "explainers")


def g(x):
    return float(f"{x:.6g}")


class Bank:
    def __init__(self, sid):
        self.sid = sid
        self.qs = []
        self.n = {1: 0, 2: 0, 3: 0, 4: 0}

    def q(self, rnd, kind, prompt, explanation, fig=None, alt=None, preview=None, version=1, **kw):
        self.n[rnd] += 1
        item = {
            "id": f"{self.sid}-r{rnd}-q{self.n[rnd]}",
            "round": rnd,
            "type": kind,
            "prompt": prompt,
            "explanation": explanation,
        }
        if fig is not None:
            item["figure"] = fig
            item["figure_alt"] = alt
        if rnd == 4:
            item["preview"] = preview
        elif preview:
            raise SystemExit("preview only in round 4")
        item.update(kw)
        item["version"] = version
        self.qs.append(item)

    def mc(self, rnd, prompt, options, correct, explanation, fig=None, alt=None, preview=None, version=1):
        self.q(rnd, "mc", prompt, explanation, fig, alt, preview, version,
               options=options, correct_index=correct)

    def num(self, rnd, prompt, answer, unit, explanation, fig=None, alt=None, preview=None, version=1):
        self.q(rnd, "numeric", prompt, explanation, fig, alt, preview, version,
               answer=g(answer), unit=unit, tolerance=0.02)

    def save(self):
        assert self.n == {1: 3, 2: 3, 3: 3, 4: 3}, (self.sid, self.n)
        path = os.path.join(BANK, f"{self.sid}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"skill_id": self.sid, "version": 1, "questions": self.qs},
                      f, indent=2, ensure_ascii=False)
            f.write("\n")


def save_explainer(sid, title, sections, version=1):
    path = os.path.join(EXP, f"{sid}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"id": sid, "title": title, "version": version, "sections": sections},
                  f, indent=2, ensure_ascii=False)
        f.write("\n")


def words(sections):
    text = " ".join(s["body_md"] for s in sections)
    text = re.sub(r"<svg[\s\S]*?</svg>", " ", text)
    text = re.sub(r"\\\(|\\\)|\\\[|\\\]", " ", text)
    text = re.sub(r"\\[a-zA-Z]+", " ", text)
    return len(re.findall(r"[A-Za-z0-9']+", text))


def second_order_step(zeta, wn, goal, t_end):
    """Second-order step response for zeta < 1 (underdamped)."""
    if zeta >= 1:
        raise ValueError("use this only for underdamped")
    wd = wn * math.sqrt(1 - zeta**2)
    def y(t):
        if t <= 0:
            return 0.0
        return goal * (1 - math.exp(-zeta * wn * t) * (
            math.cos(wd * t) + (zeta / math.sqrt(1 - zeta**2)) * math.sin(wd * t)
        ))
    return plot(y, 0, t_end, "t", "y", "second-order step", zero=False)


def overshoot_pct(zeta):
    """Percent overshoot for underdamped second-order."""
    return 100 * math.exp(-math.pi * zeta / math.sqrt(1 - zeta**2))


def time_to_peak(zeta, wn):
    """Time to first peak for underdamped second-order."""
    wd = wn * math.sqrt(1 - zeta**2)
    return math.pi / wd


def settling_time_2pct(zeta, wn):
    """Approximate 2% settling time."""
    return 4 / (zeta * wn)


def bank_second_order():
    b = Bank("second-order-sys")
    step_fig = "A curve that rises, overshoots, and then settles."
    pole_fig = "Two pole marks in the left half-plane."
    wn1, z1 = 4.0, 0.4
    wn2, z2 = 5.0, 0.5
    wn3, z3 = 3.0, 0.3
    b.mc(1,
         r"A second-order plant has two poles. If those poles are a complex conjugate pair in the left half-plane, the step response",
         ["overshoots and then oscillates before settling",
          "settles without oscillation",
          "grows without bound",
          "settles instantly"], 0,
         r"Complex poles in the left half-plane give an underdamped response. The imaginary part makes the exponential ring, so the step response overshoots and oscillates before dying out. Real poles settle without oscillation. Right-half poles grow. Instant settling is not physical.",
         second_order_step(0.3, 4, 1, 4),
         step_fig)
    b.num(1,
          r"A standard second-order system has natural frequency \(\omega_n = 4\) rad/s and damping ratio \(\zeta = 0.4\). The magnitude of the real part of each pole is",
          z1 * wn1, "rad/s",
          r"The poles are at \(-\zeta\omega_n \pm j\omega_n\sqrt{1-\zeta^2}\). The real part is \(-\zeta\omega_n = -1.6\), so its magnitude is 1.6. The natural frequency 4 is the distance from the origin to the pole, not the real part. The imaginary part is about 3.67.",
          splane([(-z1 * wn1, wn1 * math.sqrt(1 - z1**2)), (-z1 * wn1, -wn1 * math.sqrt(1 - z1**2))], [], "underdamped poles"),
          pole_fig)
    b.num(1,
          r"Same system, \(\omega_n = 4\), \(\zeta = 0.4\). The damped frequency \(\omega_d\) is",
          wn1 * math.sqrt(1 - z1**2), "rad/s",
          r"\(\omega_d = \omega_n\sqrt{1-\zeta^2} = 4\sqrt{1-0.16} = 4 \times 0.9165 = 3.666\). The natural frequency 4 is not the damped frequency. Squaring \(\zeta\) and subtracting from 1 before the square root is the correct order.",
          splane([(-z1 * wn1, wn1 * math.sqrt(1 - z1**2)), (-z1 * wn1, -wn1 * math.sqrt(1 - z1**2))], [], "underdamped poles"),
          pole_fig)
    b.num(2,
          r"For \(\omega_n = 5\) rad/s and \(\zeta = 0.5\), the percent overshoot of a unit step is",
          overshoot_pct(z2), "%",
          r"Percent overshoot is \(100 e^{-\pi\zeta/\sqrt{1-\zeta^2}}\). With \(\zeta = 0.5\), that is \(100 e^{-\pi \times 0.5/0.866} = 16.3\%\). The damping ratio 0.5 is not the overshoot. Leaving out the 100 gives the fractional overshoot.",
          second_order_step(z2, wn2, 1, 3),
          step_fig)
    b.num(2,
          r"Same system. The time to the first peak is",
          time_to_peak(z2, wn2), "s",
          r"\(t_p = \pi/\omega_d\). With \(\omega_d = 5 \times 0.866 = 4.33\), the peak time is \(\pi/4.33 = 0.725\) s. Using \(\omega_n\) instead of \(\omega_d\) gives \(\pi/5 = 0.628\), which is the wrong frequency.",
          second_order_step(z2, wn2, 1, 3),
          step_fig)
    b.mc(2,
         r"If the damping ratio \(\zeta\) is increased toward 1 while \(\omega_n\) stays the same, the step response",
         ["overshoots more",
          "oscillates faster",
          "grows without bound",
          "overshoots less and eventually does not overshoot at all"], 3,
         r"Raising \(\zeta\) adds more damping. At \(\zeta = 1\) the poles are real and equal, and the response is critically damped with no overshoot. Higher damping means less overshoot, not more. Faster oscillation would need a larger \(\omega_d\), but \(\omega_d\) shrinks as \(\zeta\) rises. The system is not growing, so it is not unstable.",
         second_order_step(0.7, 4, 1, 3),
         step_fig)
    b.num(3,
          r"A second-order system has \(\omega_n = 3\) rad/s and \(\zeta = 0.3\). The approximate 2% settling time is",
          settling_time_2pct(z3, wn3), "s",
          r"The rule of thumb is \(t_s \approx 4/(\zeta\omega_n)\). With \(\zeta = 0.3\) and \(\omega_n = 3\), that is \(4/(0.9) = 4.44\) s. Using 5 instead of 4 gives the 1% rule. Using \(\omega_n\) alone gives \(4/3\), which drops the damping ratio.",
          second_order_step(z3, wn3, 1, 8),
          step_fig)
    b.num(3,
          r"Same \(\omega_n = 3\), \(\zeta = 0.3\). The magnitude of the imaginary part of each pole is",
          wn3 * math.sqrt(1 - z3**2), "rad/s",
          r"The imaginary part is \(\pm\omega_n\sqrt{1-\zeta^2} = 3 \times 0.954 = 2.86\). The real part is \(-0.9\). The natural frequency 3 is the distance from the origin, not the imaginary part.",
          splane([(-z3 * wn3, wn3 * math.sqrt(1 - z3**2)), (-z3 * wn3, -wn3 * math.sqrt(1 - z3**2))], [], "underdamped poles"),
          pole_fig)
    b.mc(3,
         r"A critically damped system (\(\zeta = 1\)) reaches its final value",
         ["with infinite oscillation",
          "slower than any underdamped case",
          "as fast as possible without overshoot",
          "with 100% overshoot"], 2,
         r"Critical damping is the boundary between underdamped and overdamped. It reaches the final value faster than any overdamped case without overshooting. An underdamped case can cross the final value sooner but then rings. Infinite oscillation is \(\zeta = 0\). Slower than underdamped would be overdamped, not critical.",
         step_response("critically damped", tau=1, goal=1),
         "A curve that rises smoothly with no overshoot.")
    b.num(4,
          r"Transient specs often quote percent overshoot. For \(\zeta = 0.6\) and \(\omega_n = 2\) rad/s, the percent overshoot is",
          overshoot_pct(0.6), "%",
          r"Overshoot is \(100 e^{-\pi \times 0.6 / 0.8} = 9.48\%\). The formula involves \(\zeta\) but not \(\omega_n\) directly. Using \(\omega_n\) in the exponent mixes the two parameters.",
          second_order_step(0.6, 2, 1, 5), step_fig, ["step-specs"])
    b.num(4,
          r"Step-response specs quote the ringing frequency. For closed-loop poles with \(\zeta = 0.4\) and \(\omega_n = 5\), the damped frequency is",
          5 * math.sqrt(1 - 0.16), "rad/s",
          r"\(\omega_d = \omega_n\sqrt{1-\zeta^2} = 5 \times 0.9165 = 4.58\) rad/s. The natural frequency 5 is not the ringing frequency. The real part \(-2\) is the decay rate, not the ringing rate.",
          splane([(-2, 5 * math.sqrt(1 - 0.16)), (-2, -5 * math.sqrt(1 - 0.16))], [], "closed-loop poles"),
          pole_fig, ["step-specs"])
    b.mc(4,
         r"PID tuning aims for a closed-loop damping ratio around 0.7. Such a loop",
         ["never overshoots",
          "overshoots by about 5% and settles quickly",
          "overshoots by about 50%",
          "oscillates forever"], 1,
         r"\(\zeta = 0.7\) gives about 4.6% overshoot, which is close to 5%. It is underdamped, so there is some overshoot. 50% overshoot is around \(\zeta = 0.16\). Infinite oscillation is \(\zeta = 0\).",
          second_order_step(0.7, 3, 1, 4), step_fig, ["pid-tuning"])
    b.save()


def bank_ss_solution():
    b = Bank("ss-solution")
    decay = "A curve that decays toward zero."
    modes = "Pole marks on the negative real axis."
    b.mc(1,
         r"The free response of \(\dot{x} = Ax\) from initial state \(x(0)\) is",
         [r"\(x(t) = e^{At} x(0)\)",
          r"\(x(t) = A x(0)\)",
          r"\(x(t) = x(0) + At\)",
          r"\(x(t) = x(0) e^{-t}\)"], 0,
         r"The matrix exponential \(e^{At}\) generalizes the scalar exponential. It multiplies the initial state to give the state at time \(t\). \(Ax(0)\) is a single derivative, not the time evolution. \(x(0) + At\) is a linear ramp. \(x(0)e^{-t}\) assumes a specific eigenvalue of \(-1\).",
         step_response("free response", fn=lambda t: math.exp(-0.5 * t), t_end=10),
         decay)
    lam1 = -0.5
    b.num(1,
          r"A one-state system has \(\dot{x} = -0.5 x\). From \(x(0) = 4\), the state at \(t = 2\) is",
          4 * math.exp(lam1 * 2), "1",
          r"\(x(t) = e^{-0.5 t} x(0) = e^{-1} \times 4 = 1.472\). The eigenvalue is \(-0.5\), so the decay is slower than \(e^{-t}\). Using \(e^{-2}\) instead of \(e^{-1}\) squares the exponent.",
          step_response("one-mode decay", fn=lambda t: 4 * math.exp(lam1 * t), t_end=8),
          decay)
    lam2, lam3 = -1.0, -3.0
    b.num(1,
          r"A diagonal \(A\) has eigenvalues \(-1\) and \(-3\). The slower mode decays with time constant",
          1.0, "s",
          r"The time constant is \(1/|\lambda|\). The slower mode is \(\lambda = -1\), so \(\tau = 1\) s. The \(-3\) mode has \(\tau = 1/3\). Adding the eigenvalues gives \(-4\), which is not a time constant.",
          splane([(-1, 0), (-3, 0)], [], "two real eigenvalues"),
          modes)
    b.num(2,
          r"Starting from \(x_1(0) = 1\), \(x_2(0) = 0\), the decoupled system \(\dot{x}_1 = -2x_1\), \(\dot{x}_2 = -4x_2\) has \(x_1(1)\) equal to",
          math.exp(-2), "1",
          r"The first state evolves as \(x_1(t) = e^{-2t}\). At \(t = 1\), that is \(e^{-2} = 0.135\). The second state stays at zero because its initial condition is zero. Using \(e^{-4}\) applies the wrong eigenvalue.",
          step_response("fast and slow modes", fn=lambda t: math.exp(-2 * t), t_end=3),
          decay)
    b.mc(2,
         r"The matrix exponential of a diagonal matrix \(\mathrm{diag}(\lambda_1, \lambda_2)\) is",
         [r"\(e^{(\lambda_1 + \lambda_2) t}\)",
          r"\(\mathrm{diag}(e^{\lambda_1 t}, e^{\lambda_2 t})\)",
          r"\(\mathrm{diag}(\lambda_1 t, \lambda_2 t)\)",
          r"\(\mathrm{diag}(\lambda_1, \lambda_2)\)"], 1,
         r"The exponential of a diagonal matrix is the diagonal of the exponentials. Each mode evolves independently. The sum of eigenvalues in the exponent would collapse the two modes into one; that is wrong. A linear term \(\lambda t\) is not an exponential. The original matrix without time evolution is missing the \(t\) dependence.",
         matrix_fig([["e^{\u03bb\u2081t}", "0"], ["0", "e^{\u03bb\u2082t}"]], "diagonal exponential"),
         "A 2 by 2 diagonal matrix of exponentials.")
    b.num(2,
          r"An eigenvalue is \(-4\). The time for that mode to decay to \(e^{-1}\) of its initial value is",
          0.25, "s",
          r"One time constant is \(\tau = 1/4 = 0.25\) s. At that time the exponential is \(e^{-4 \times 0.25} = e^{-1}\). Using the eigenvalue itself as the time gives \(e^{-16}\), which is far too small.",
          splane([(-4, 0)], [], "one real eigenvalue"),
          "One pole mark on the negative real axis.")
    b.num(3,
          r"Two eigenvalues are \(-2\) and \(-6\). The state after 10 time constants of the slower mode is dominated by",
          -2, "1",
          r"After many time constants the faster mode is negligible. The slower eigenvalue \(-2\) dominates. The \(-6\) mode dies in about \(10/6 = 1.67\) s while the \(-2\) mode takes 5 s to decay by \(e^{-10}\).",
          splane([(-2, 0), (-6, 0)], [], "slow and fast modes"),
          modes)
    b.mc(3,
         r"If all eigenvalues of \(A\) have negative real parts, the free response",
         ["grows without bound",
          "oscillates forever at constant amplitude",
          "stays constant",
          "decays to zero"], 3,
         r"Every mode is a decaying exponential times a sinusoid (or just the exponential for real eigenvalues). All modes die out, so the state decays to zero. Right-half eigenvalues would grow. Purely imaginary eigenvalues would oscillate forever. A constant state would need an eigenvalue at zero.",
         splane([(-1, 2), (-1, -2)], [], "stable complex pair"),
         "Two pole marks in the left half-plane.")
    b.num(3,
          r"A complex eigenvalue is \(-1 + 2j\). The envelope of that mode decays with time constant",
          1.0, "s",
          r"The envelope decays as \(e^{-|\mathrm{Re}(\lambda)|t} = e^{-t}\), so \(\tau = 1\) s. The imaginary part 2 sets the oscillation frequency, not the decay rate. Using 2 as the time constant confuses oscillation with decay.",
          splane([(-1, 2), (-1, -2)], [], "complex pair"),
          "Two pole marks forming a conjugate pair.")
    b.num(4,
          r"For mode analysis: a diagonal \(A\) has entries \(-0.5\) and \(-2\). From \(x(0) = [1, 1]^T\), the value of \(x_2\) at \(t = 1\) is",
          math.exp(-2), "1",
          r"\(x_2(t) = e^{-2t} x_2(0) = e^{-2}\). The first state uses \(-0.5\), but this question asks about the second. Mixing the eigenvalues gives \(e^{-0.5}\), which is the first component.",
          splane([(-0.5, 0), (-2, 0)], [], "two modes"),
          modes, ["eig-modes"])
    b.num(4,
          r"A 3-by-3 realization of a transfer function has eigenvalues \(-1\), \(-2\), \(-5\). The slowest mode has time constant",
          1.0, "s",
          r"The slowest eigenvalue is \(-1\), so \(\tau = 1\) s. The \(-2\) mode has \(\tau = 0.5\) s and the \(-5\) mode has \(\tau = 0.2\) s. The sum of eigenvalues is not a time constant.",
          splane([(-1, 0), (-2, 0), (-5, 0)], [], "three real modes"),
          "Three pole marks on the negative real axis.", ["realization"])
    b.mc(4,
         r"An LTI system is stable when",
         [r"any eigenvalue is zero",
          r"all eigenvalues are purely imaginary",
          r"all eigenvalues of \(A\) have negative real parts",
          r"the trace of \(A\) is positive"], 2,
         r"Every eigenvalue in the open left half-plane means every mode decays. A zero eigenvalue is a free integrator, which drifts rather than settling. Purely imaginary eigenvalues are marginally stable and oscillate forever. A positive trace can still have stable eigenvalues in some cases, but it is not sufficient for stability.",
          splane([(-1, 0), (-3, 0)], [], "stable eigenvalues"),
          modes, ["lti-stability"])
    b.save()


def bank_loop_tf():
    b = Bank("loop-tf")
    loop = "A forward block and a return path that is subtracted at the input."
    nyq = "A curve in the complex plane with the critical point marked."
    G1, H1 = 10, 0.2
    G2, H2 = 6, 1
    b.mc(1,
         r"The loop transfer function \(L(s)\) is the product of",
         ["every block you meet walking once around the loop",
          "the reference and the output",
          "the closed-loop gain and the sensitivity",
          "the numerator and denominator of the plant"], 0,
         r"Walk from the error, through the forward path, through the return path, back to the summing junction. Multiply every block you pass. That product is \(L(s)\). The reference and output are signals, not gains. The closed-loop gain times sensitivity equals \(T \cdot S = L/(1+L)^2\), which is not \(L\). The numerator and denominator of the plant describe only the forward block.",
         block_diagram(["G"], "loop product", feedback="H", input_label="r", output_label="y", error_label="e"),
         loop)
    b.num(1,
          r"The forward gain is 10 and the return gain is 0.2. The loop gain \(L\) is",
          G1 * H1, "1",
          r"\(L = GH = 10 \times 0.2 = 2\). Adding the gains gives 10.2, which is not the loop product. Dividing gives 50, which is the inverse of the return gain times the forward gain.",
          block_diagram(["10"], "loop with return 0.2", feedback="0.2", input_label="r", output_label="y"),
          loop)
    b.num(1,
          r"Same loop. The closed-loop gain is",
          G1 / (1 + G1 * H1), "1",
          r"\(T = G/(1+L) = 10/(1+2) = 10/3 = 3.333\). The loop gain 2 is not the closed-loop gain. Adding 1 to \(G\) instead of to \(L\) gives \(10/11\), which is wrong.",
          block_diagram(["10"], "closed-loop gain", feedback="0.2", input_label="r", output_label="y"),
          loop)
    b.num(2,
          r"A unity-feedback loop has forward gain \(G = 6\). The loop gain is",
          G2 * H2, "1",
          r"Unity feedback means \(H = 1\), so \(L = G \times 1 = 6\). The closed-loop gain \(6/7\) is not the loop gain. Subtracting 1 from 6 gives 5, which is not defined by the diagram.",
          block_diagram(["6"], "unity feedback", feedback="1", input_label="r", output_label="y"),
          loop)
    b.num(2,
          r"Same unity loop with \(G = 6\). The sensitivity \(S = 1/(1+L)\) is",
          1 / (1 + G2), "1",
          r"\(S = 1/(1+6) = 1/7 = 0.143\). The complementary sensitivity \(T = 6/7\) is one minus this. The loop gain 6 is not the sensitivity.",
          block_diagram(["6"], "sensitivity", feedback="1", input_label="r", output_label="y"),
          loop)
    b.mc(2,
         r"The complementary sensitivity \(T(s)\) and the sensitivity \(S(s)\) satisfy",
         [r"\(T + S = 0\)",
          r"\(T \cdot S = 1\)",
          r"\(T - S = L\)",
          r"\(T + S = 1\)"], 3,
         r"\(T = L/(1+L)\) and \(S = 1/(1+L)\). Their sum is \((L+1)/(1+L) = 1\). Zero is wrong because both \(T\) and \(S\) are positive. Their product is \(L/(1+L)^2\), not 1. Their difference is \((L-1)/(1+L)\), not \(L\).",
         block_diagram(["G"], "T and S", feedback="H", input_label="r", output_label="y"),
         loop)
    G3, H3 = 8, 0.5
    b.num(3,
          r"Forward gain 8, return gain 0.5. The return difference \(1 + L\) is",
          1 + G3 * H3, "1",
          r"\(L = 8 \times 0.5 = 4\), so \(1 + L = 5\). The loop gain 4 is one less than the return difference. The closed-loop gain \(8/5\) is not the return difference.",
          block_diagram(["8"], "return difference", feedback="0.5", input_label="r", output_label="y"),
          loop)
    b.num(3,
          r"Same loop. A disturbance of magnitude 1 adds at the output. The fraction remaining at steady state is",
          1 / (1 + G3 * H3), "1",
          r"A disturbance at the output is divided by \(1 + L = 5\), so \(1/5 = 0.2\) remains. The closed-loop gain \(8/5\) is what a reference sees, not a disturbance. The loop gain 4 is not the rejection ratio.",
          block_diagram(["8"], "disturbance rejection", feedback="0.5", input_label="r", output_label="y", disturbance="d"),
          "A forward block, a return subtracted at the input, and a disturbance added at the output.")
    b.mc(3,
         r"On a Nyquist plot, the loop gain \(L(j\omega)\) is plotted as \(\omega\) sweeps from 0 to \(\infty\). The critical point is at",
         [r"\(0\)",
          r"\(-1\)",
          r"\(1\)",
          r"\(j\)"], 1,
         r"Stability depends on encirclements of \(-1\), the point where \(1 + L = 0\). The origin is where \(L = 0\), not the critical point. The point \(+1\) is where \(L = 1\), which is not the instability boundary. The point \(j\) is on the imaginary axis and is not special for stability.",
         splane([], [(-1, 0)], "critical point"),
         "A zero mark at minus one on the real axis.")
    G4 = 12
    b.num(4,
          r"A Nyquist plot is drawn for \(L(s)\). The forward gain is 12 and the return is unity. The loop gain magnitude at DC is",
          G4, "1",
          r"At \(s = 0\), the loop gain is \(L(0) = 12 \times 1 = 12\). The closed-loop gain \(12/13\) is what the reference sees. The sensitivity \(1/13\) is the disturbance attenuation.",
          block_diagram(["12"], "DC loop gain", feedback="1", input_label="r", output_label="y"),
          loop, ["nyquist"])
    G5, H5 = 5, 0.4
    b.num(4,
          r"For sensitivity analysis: forward gain 5, return gain 0.4. The sensitivity \(S\) is",
          1 / (1 + G5 * H5), "1",
          r"\(L = 2\), so \(S = 1/3 = 0.333\). The complementary sensitivity \(2/3\) is what the reference sees. The loop gain 2 is not the sensitivity.",
          block_diagram(["5"], "sensitivity", feedback="0.4", input_label="r", output_label="y"),
          loop, ["sensitivity"])
    b.mc(4,
         r"Robust performance requires that the loop gain satisfy constraints on",
         ["only the forward gain",
          "only the return gain",
          "both magnitude and phase across frequency",
          "only the DC gain"], 2,
         r"Robust performance bounds depend on how \(L(j\omega)\) moves in the complex plane. That requires magnitude and phase at every frequency. The DC gain alone is a single point. The forward or return alone is not the loop product.",
          block_diagram(["G(s)"], "frequency-dependent loop", feedback="H(s)", input_label="r", output_label="y"),
          loop, ["robust-perf"])
    b.save()


def bank_equilibria():
    b = Bank("equilibria")
    decay = "A curve that settles to a constant."
    phase = "Arrows showing the direction of motion on a phase portrait."
    b.mc(1,
         r"An equilibrium point of \(\dot{x} = f(x, u)\) with constant \(u\) is a state where",
         [r"\(\dot{x} = 0\)",
          r"\(x = 0\)",
          r"\(u = 0\)",
          r"\(\dot{x}\) is maximized"], 0,
         r"At equilibrium the state does not change, so \(\dot{x} = 0\). The state itself need not be zero; the resting level depends on the input. The input need not be zero either. Maximizing the derivative is not equilibrium.",
         step_response("settling to equilibrium", tau=2, goal=3),
         decay)
    b.num(1,
          r"The one-state system \(\dot{x} = 5 - 2x\) has equilibrium at \(x =\)",
          5 / 2, "1",
          r"Set \(\dot{x} = 0\): \(5 = 2x\), so \(x = 2.5\). The coefficients 5 and 2 are not the equilibrium. Their difference 3 and their sum 7 are not solutions.",
          step_response("resting at 2.5", tau=0.5, goal=2.5),
          decay)
    b.num(1,
          r"With constant \(u = 3\), the system \(\dot{x} = u - 0.6x\) rests at \(x =\)",
          3 / 0.6, "1",
          r"Set \(\dot{x} = 0\): \(3 = 0.6x\), so \(x = 5\). The input 3 is not the equilibrium. Dividing 0.6 by 3 gives 0.2, which is the inverse.",
          step_response("equilibrium with input", tau=1 / 0.6, goal=5),
          decay)
    b.num(2,
          r"A two-state system in equilibrium satisfies \(Ax + Bu = 0\). If \(A = \begin{bmatrix}-1 & 0 \\ 0 & -2\end{bmatrix}\), \(B = \begin{bmatrix}1 \\ 2\end{bmatrix}\), and \(u = 4\), the first component \(x_1\) is",
          4.0, "1",
          r"Solve \(-x_1 + 4 = 0\) for the first row: \(x_1 = 4\). The second row gives \(-2x_2 + 8 = 0\), so \(x_2 = 4\). The eigenvalues \(-1, -2\) are not the equilibrium.",
          matrix_fig([["-1", "0"], ["0", "-2"]], "diagonal A"),
          "A 2 by 2 diagonal matrix.")
    b.mc(2,
         r"If the eigenvalues of \(A\) have negative real parts and the input is constant, the state",
         ["diverges from equilibrium",
          "converges to equilibrium from any initial condition",
          "oscillates around equilibrium forever",
          "stays at the initial condition"], 1,
         r"Negative real parts mean every mode decays. The state settles to the unique equilibrium determined by \(Ax + Bu = 0\). Divergence needs a positive eigenvalue. Perpetual oscillation needs a purely imaginary eigenvalue.",
         splane([(-1, 0), (-2, 0)], [], "stable eigenvalues"),
         "Two pole marks on the negative real axis.")
    b.num(2,
          r"The scalar system \(\dot{x} = 4 - x\) starts at \(x(0) = 0\). The equilibrium it approaches is",
          4.0, "1",
          r"Set \(\dot{x} = 0\): \(x = 4\). The initial condition 0 is not the equilibrium. The coefficient 1 is the decay rate, not the resting value.",
          step_response("approaching 4", tau=1, goal=4),
          decay)
    b.num(3,
          r"A tank level obeys \(\dot{h} = q_{in} - 0.5h\) with \(q_{in} = 2\). The equilibrium height is",
          4.0, "1",
          r"Set \(\dot{h} = 0\): \(2 = 0.5h\), so \(h = 4\). The inflow 2 is not the height. The decay coefficient 0.5 is the reciprocal of the time constant.",
          step_response("tank settling", tau=2, goal=4),
          decay)
    b.mc(3,
         r"A nonlinear system \(\dot{x} = x(1 - x)\) has equilibria at",
         [r"\(x = 0\) only",
          r"\(x = 1\) only",
          r"\(x = 0\) and \(x = 1\)",
          r"\(x = 0.5\)"], 2,
         r"Set the product to zero: \(x = 0\) or \(1 - x = 0\). Both \(x = 0\) and \(x = 1\) are equilibria. The midpoint 0.5 is not a root. The derivative at 0.5 is \(0.5 \times 0.5 = 0.25\), not zero.",
         step_response("logistic equilibrium", fn=lambda t: 1 / (1 + math.exp(-t + 2)), t_end=8),
         "A curve that rises from near zero toward one.")
    b.num(3,
          r"A rotor obeys \(\dot{\omega} = \tau/J - b\omega/J\) with \(\tau = 6\) Nm, \(J = 2\) kg m\(^2\), \(b = 0.5\) Nm s. The equilibrium speed is",
          6 / 0.5, "rad/s",
          r"Set \(\dot{\omega} = 0\): \(\tau = b\omega\), so \(\omega = 6/0.5 = 12\) rad/s. The inertia \(J\) affects how fast the rotor reaches equilibrium, not where it stops.",
          step_response("rotor settling", tau=2 / 0.5, goal=12),
          decay)
    b.num(4,
          r"Before linearization, find the equilibrium. For \(\dot{x} = 3u - 0.5x\) with \(u = 2\), the resting \(x\) is",
          6 / 0.5, "1",
          r"Set \(\dot{x} = 0\): \(6 = 0.5x\), so \(x = 12\). The input 2 is not the equilibrium. The product 6 is the numerator, not the answer.",
          step_response("equilibrium for linearization", tau=2, goal=12),
          decay, ["linearization"])
    b.num(4,
          r"After linearization, a plant settles to \(y = 8\) when \(u = 2\). The DC gain of the linearized model is",
          4.0, "1",
          r"DC gain is \(y/u = 8/2 = 4\). The equilibrium 8 is not the gain. The input 2 is not the gain. The ratio is what a step test on the linearized model shows.",
          step_response("step test settling", tau=1, goal=8),
          decay, ["linearization"])
    b.mc(4,
         r"Limit cycles exist when",
         ["all equilibria are stable",
          "the system is linear",
          "the input is zero",
          "nonlinearity sustains a periodic orbit that is not an equilibrium"], 3,
         r"A limit cycle is a closed orbit that is not a single point. Linear systems have no limit cycles; they can only have equilibria or unbounded growth. Stable equilibria are points, not cycles. Zero input does not create a cycle; nonlinearity is required.",
          step_response("oscillation", fn=lambda t: math.sin(t), t_end=10, zero=True),
          "A sinusoidal curve.", ["limit-cycles"])
    b.save()


def bank_cruise():
    b = Bank("cruise-control")
    loop = "A controller and a plant in a speed loop."
    step_fig = "A curve that rises and settles."
    Kc1, P1 = 3, 5
    Kc2, P2 = 4, 6
    b.mc(1,
         r"A cruise-control loop holds a car's speed at a reference by adjusting the throttle. A grade or a headwind acts as",
         ["a disturbance",
          "the reference",
          "the sensor",
          "the controller gain"], 0,
         r"A grade or wind changes the load on the engine without being commanded. That is a disturbance. The reference is the speed the driver sets, not an external load. The sensor measures the speed. The controller gain is a design parameter, not an external effect.",
         block_diagram(["Kc", "P"], "cruise loop", feedback="1", input_label="r", output_label="v", disturbance="d"),
         "A controller, a plant, and a disturbance at the output.")
    b.num(1,
          r"Proportional cruise control with \(K_c = 3\) on a plant of DC gain 5. The loop gain is",
          Kc1 * P1, "1",
          r"\(L = K_c P = 15\). The closed-loop gain \(15/16\) is not the loop gain. Adding 3 and 5 gives 8, which is not the product.",
          block_diagram(["3", "5"], "cruise loop gain", feedback="1", input_label="r", output_label="v"),
          loop)
    b.num(1,
          r"Same loop. The speed reference is 20. The steady speed is",
          Kc1 * P1 / (1 + Kc1 * P1) * 20, "1",
          r"\(v = L/(1+L) \times r = 15/16 \times 20 = 18.75\). The reference 20 is not the speed. The loop gain 15 is not the speed. The error \(20 - 18.75 = 1.25\) is what remains.",
          block_diagram(["3", "5"], "steady speed", feedback="1", input_label="r", output_label="v"),
          loop)
    b.num(2,
          r"With \(K_c = 4\) and plant gain 6, a speed reference of 25. The steady error \(r - v\) is",
          25 / (1 + Kc2 * P2), "1",
          r"Error is \(r/(1+L) = 25/25 = 1\). The steady speed \(24\) is not the error. The loop gain 24 is not the error. Subtracting 24 from 25 verifies the answer.",
          block_diagram(["4", "6"], "cruise error", feedback="1", input_label="r", output_label="v"),
          loop)
    b.mc(2,
         r"Adding integral action to a cruise loop, if the loop stays stable, makes the steady error",
         ["larger",
          "zero",
          "equal to the proportional-only error",
          "oscillate"], 1,
         r"Integral action cannot settle while a constant error remains. The only steady state is zero error. Proportional-only error is positive. Larger error goes the wrong way. Oscillation is a transient issue, not the steady value.",
         block_diagram(["PI", "plant"], "PI cruise", feedback="1", input_label="r", output_label="v"),
         loop)
    b.num(2,
          r"A disturbance of \(-0.5\) adds at the output (a drag increase). With \(L = 20\), the speed offset due to the disturbance is",
          -0.5 / (1 + 20), "1",
          r"The disturbance is divided by \(1 + L = 21\), so the offset is \(-0.5/21 = -0.024\). The disturbance \(-0.5\) itself is not the offset. The loop gain 20 is not the offset.",
          block_diagram(["K", "P"], "cruise with drag", feedback="1", input_label="r", output_label="v", disturbance="d"),
          "A loop with a disturbance added at the output.")
    Kc3, P3 = 2, 8
    b.num(3,
          r"A cruise system has \(K_c = 2\) and plant gain 8. The sensitivity \(S = 1/(1+L)\) is",
          1 / (1 + Kc3 * P3), "1",
          r"\(L = 16\), so \(S = 1/17 = 0.059\). The complementary sensitivity \(16/17\) is what the reference sees. The loop gain 16 is not the sensitivity.",
          block_diagram(["2", "8"], "cruise sensitivity", feedback="1", input_label="r", output_label="v"),
          loop)
    b.num(3,
          r"Same loop. A grade adds an output disturbance of \(-1\). The speed drops by",
          1 / (1 + Kc3 * P3), "1",
          r"The drop is \(|d| \times S = 1 \times 0.059 = 0.059\). The disturbance 1 is not the drop. The loop gain 16 is not the drop. The sign of the disturbance is negative, but the question asks for the magnitude of the drop.",
          block_diagram(["2", "8"], "grade disturbance", feedback="1", input_label="r", output_label="v", disturbance="d"),
          "A loop with a disturbance added at the output.")
    b.mc(3,
         r"Increasing the proportional gain \(K_c\) in a stable cruise loop",
         ["increases the steady error",
          "has no effect on the steady error",
          "makes the loop unstable",
          "decreases the steady error"], 3,
         r"Higher \(K_c\) raises \(L\), which shrinks \(1/(1+L)\). The error decreases. Increasing the error goes the wrong way. No effect is wrong because \(K_c\) appears in \(L\). The loop can become unstable if \(K_c\) is raised too far, but that is a separate limit, not the immediate consequence.",
          block_diagram(["Kc", "P"], "higher gain", feedback="1", input_label="r", output_label="v"),
          loop)
    Kc4, P4 = 5, 4
    b.num(4,
          r"PID tuning on a cruise loop: \(K_c = 5\), plant gain 4, reference 30. The P-only steady error is",
          30 / (1 + Kc4 * P4), "1",
          r"\(L = 20\), so error is \(30/21 = 1.43\). The speed \(28.57\) is not the error. The loop gain 20 is not the error. Tuning will try to reduce this.",
          block_diagram(["5", "4"], "P-only error", feedback="1", input_label="r", output_label="v"),
          loop, ["pid-tuning"])
    b.num(4,
          r"A feedforward term \(K_{ff}\) is added to P control with \(K_c = 3\) on a plant of gain 4. The ideal feedforward gain that makes the DC closed-loop gain exactly 1 is",
          (1 + 12) / 4, "1",
          r"The closed-loop gain is \((K_{ff} P + K_c P)/(1 + K_c P)\). For DC gain 1, \(K_{ff} P + K_c P = 1 + K_c P\), so \(K_{ff} = (1 + L)/P = 13/4 = 3.25\). Using \(K_c\) alone gives 3, which does not account for the closed-loop denominator.",
          block_diagram(["Kc+Kff", "4"], "feedforward cruise", feedback="1", input_label="r", output_label="v"),
          loop, ["feedforward"])
    b.mc(4,
         r"Gain scheduling adjusts \(K_c\) based on operating point. This is useful when",
         ["the plant gain does not change",
          "the reference is constant",
          "the plant gain varies with speed or load",
          "no disturbance is present"], 2,
         r"Gain scheduling compensates for plant variation. If the plant gain is constant, a fixed \(K_c\) suffices. A constant reference does not require scheduling. No disturbance means a smaller steady-state problem but not a need for scheduling.",
          block_diagram(["Kc(v)", "P(v)"], "scheduled cruise", feedback="1", input_label="r", output_label="v"),
          loop, ["gain-scheduling"])
    b.save()


def bank_app_examples():
    b = Bank("app-examples")
    tank = "A tank with an inflow and an outflow."
    pend = "A pendulum hanging from a pivot."
    motor = "A motor driving a load."
    b.mc(1,
         r"A mixing tank has inflow rate \(q_{in}\) and outflow rate \(q_{out} = h/R\), where \(h\) is the level and \(R\) is the hydraulic resistance. The state is",
         [r"the level \(h\)",
          "the inflow rate",
          "the outflow rate",
          r"the resistance \(R\)"], 0,
         r"The level is a stored quantity that needs an initial condition. The inflow is an input, not a state. The outflow is a function of the state, not the state itself. The resistance is a parameter, not a dynamic quantity.",
         step_response("tank level", tau=2, goal=3),
         tank)
    b.num(1,
          r"The tank has area \(A = 2\) m\(^2\) and resistance \(R = 4\) s/m\(^2\). The time constant is",
          2 * 4, "s",
          r"The time constant is \(AR = 8\) s. The area 2 is not the time constant. The resistance 4 is not the time constant. The ratio \(A/R = 0.5\) is the reciprocal.",
          step_response("tank time constant", tau=8, goal=1),
          tank)
    b.num(1,
          r"A constant inflow of \(q_{in} = 0.5\) m\(^3\)/s fills the tank. At equilibrium the level is",
          0.5 * 4, "m",
          r"At equilibrium \(q_{in} = h/R\), so \(h = q_{in} R = 0.5 \times 4 = 2\) m. The inflow 0.5 is not the level. The time constant 8 is not the level.",
          step_response("tank equilibrium", tau=8, goal=2),
          tank)
    b.mc(2,
         r"A DC motor obeys \(J\dot{\omega} = K_t i - b\omega\), where \(\omega\) is the speed and \(i\) is the armature current. The state is",
         [r"the current \(i\)",
          r"the torque constant \(K_t\)",
          r"the inertia \(J\)",
          r"the speed \(\omega\)"], 3,
         r"The speed is the stored quantity that evolves over time. The current is an input (or another state if the electrical dynamics are included). The torque constant and inertia are parameters, not dynamic states.",
         step_response("motor speed", tau=1, goal=10),
         motor)
    b.num(2,
          r"A motor has inertia \(J = 0.1\) kg m\(^2\) and damping \(b = 0.5\) Nm s. The mechanical time constant is",
          0.1 / 0.5, "s",
          r"The time constant is \(J/b = 0.2\) s. The inertia 0.1 is not the time constant. The damping 0.5 is not the time constant. The product \(Jb = 0.05\) is not dimensionally correct.",
          step_response("motor time constant", tau=0.2, goal=1),
          motor)
    b.num(2,
          r"The motor's torque constant is \(K_t = 0.4\) Nm/A. A current of 5 A produces a torque of",
          0.4 * 5, "Nm",
          r"Torque is \(K_t i = 0.4 \times 5 = 2\) Nm. The current 5 is not the torque. The torque constant 0.4 is not the torque. The ratio \(i/K_t = 12.5\) is the inverse.",
          step_response("motor torque", tau=0.2, goal=2),
          motor)
    b.mc(3,
         r"A linearized pendulum near the downward equilibrium has \(\ddot{\theta} = -g\theta/\ell\). The natural frequency squared is",
         [r"\(g\ell\)",
          r"\(g/\ell\)",
          r"\(\ell/g\)",
          r"\(1/g\ell\)"], 1,
         r"The equation is \(\ddot{\theta} + (g/\ell)\theta = 0\), so \(\omega_n^2 = g/\ell\). The product \(g\ell\) has units of m\(^2\)/s\(^2\), not 1/s\(^2\). The reciprocal \(\ell/g\) is a time squared.",
         splane([(0, math.sqrt(9.81)), (0, -math.sqrt(9.81))], [], "pendulum poles"),
         "Two pole marks on the imaginary axis.")
    b.num(3,
          r"A pendulum has length \(\ell = 1\) m and \(g = 10\) m/s\(^2\). The natural frequency is",
          math.sqrt(10), "rad/s",
          r"\(\omega_n = \sqrt{g/\ell} = \sqrt{10} = 3.16\) rad/s. The length 1 is not the frequency. The gravity 10 is \(\omega_n^2\), not \(\omega_n\).",
          splane([(0, math.sqrt(10)), (0, -math.sqrt(10))], [], "pendulum poles"),
         "Two pole marks on the imaginary axis.")
    b.num(3,
          r"A tank's level decays with time constant 5 s. Starting at \(h = 3\) m with no inflow, the level at \(t = 5\) s is",
          3 * math.exp(-1), "m",
          r"At one time constant, \(h = 3 e^{-1} = 1.10\) m. The initial level 3 is not the answer. Half of 3 is 1.5, which is not \(e^{-1}\) of 3.",
          step_response("tank decay", fn=lambda t: 3 * math.exp(-t / 5), t_end=15),
          tank)
    b.num(4,
          r"A realization writes the tank as \(\dot{h} = -h/(AR) + q_{in}/A\). With \(A = 2\) and \(R = 3\), the coefficient of \(h\) is",
          -1 / 6, "1/s",
          r"The coefficient is \(-1/(AR) = -1/6 = -0.167\). The time constant \(AR = 6\) is the reciprocal. The area 2 and resistance 3 are not the coefficient.",
          step_response("tank state coefficient", tau=6, goal=1),
          tank, ["realization"])
    b.num(4,
          r"For discrete-time: a tank has time constant 4 s. The sample period that captures the dynamics well is about one-tenth of that, or",
          0.4, "s",
          r"A rule of thumb is to sample at least 10 times per time constant. \(4/10 = 0.4\) s. Sampling at 4 s misses most of the transient. Sampling at 0.04 s is unnecessarily fast.",
          step_response("sampled tank", tau=4, goal=1),
          tank, ["discrete-time"])
    b.mc(4,
         r"Linearization of the pendulum is valid",
         ["for any angle",
          "only when damping is zero",
          "only near the equilibrium where the linearization was done",
          "only for vertical orientation"], 2,
         r"Linearization keeps only the first-order Taylor term. The approximation is accurate only near the expansion point. For any angle is wrong because large angles break the approximation. Damping does not change where the linearization is valid. Vertical orientation is not required; the equilibrium can be at any position.",
          splane([(0, 3), (0, -3)], [], "linearized pendulum"),
          "Two pole marks on the imaginary axis.", ["linearization"])
    b.save()


def expl_second_order():
    fig = second_order_step(0.4, 4, 1, 4)
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A curve that rises, overshoots, and then settles.",
         "body_md": r"""A second-order system has two poles. If those poles are a complex conjugate pair in the left half-plane, the step response overshoots and oscillates before settling. Two numbers capture the shape: the natural frequency \(\omega_n\) and the damping ratio \(\zeta\).

The natural frequency is the distance from the origin to the pole. It sets the overall speed of the response. The damping ratio is the cosine of the angle from the negative real axis to the pole. It sets how much the response rings. A damping ratio of 1 is critical damping, where the poles are real and equal and the response settles as fast as possible without overshooting."""},
        {"heading": "Key equations", "body_md": r"""Standard second-order form:
\[
\ddot{y} + 2\zeta\omega_n\dot{y} + \omega_n^2 y = \omega_n^2 u.
\]
Poles at \(-\zeta\omega_n \pm j\omega_n\sqrt{1-\zeta^2}\) for \(\zeta < 1\). The damped frequency is \(\omega_d = \omega_n\sqrt{1-\zeta^2}\).

Percent overshoot: \(M_p = 100 e^{-\pi\zeta/\sqrt{1-\zeta^2}}\). Time to peak: \(t_p = \pi/\omega_d\). Approximate 2% settling time: \(t_s \approx 4/(\zeta\omega_n)\)."""},
        {"heading": "Worked example", "body_md": r"""Take \(\omega_n = 5\) rad/s and \(\zeta = 0.5\). The poles are at \(-2.5 \pm j4.33\). The damped frequency is \(\omega_d = 5 \times 0.866 = 4.33\) rad/s. The percent overshoot is
\[
M_p = 100 e^{-\pi \times 0.5/0.866} = 16.3\%.
\]
The time to peak is \(t_p = \pi/4.33 = 0.725\) s. The settling time is about \(4/(2.5) = 1.6\) s. Using \(\omega_n = 5\) instead of \(\omega_d\) in the peak time formula gives \(\pi/5 = 0.628\) s, which is wrong."""},
        {"heading": "Common pitfalls", "body_md": r"""The natural frequency is not the ringing frequency. The ringing frequency is the damped frequency \(\omega_d\), which is smaller than \(\omega_n\) when \(\zeta > 0\). The percent overshoot formula does not depend on \(\omega_n\) directly; it depends only on \(\zeta\). Confusing \(\omega_n\) with \(\omega_d\) in the peak-time formula gives the wrong answer. Critical damping (\(\zeta = 1\)) is not overdamping; overdamping has \(\zeta > 1\)."""},
        {"heading": "Where this leads", "body_md": r"""Step-response specifications quote percent overshoot, rise time, and settling time. PID tuning often aims for a closed-loop damping ratio around 0.7, which gives about 5% overshoot. Nyquist and Bode plots relate the loop gain to the closed-loop damping ratio through phase and gain margins."""},
    ]
    save_explainer("second-order-sys", "Second-order systems", sections)
    return words(sections)


def expl_ss_solution():
    fig = step_response("free response", fn=lambda t: math.exp(-0.5 * t), t_end=10)
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A curve that decays toward zero.",
         "body_md": r"""The free response of a linear state-space model is \(x(t) = e^{At} x(0)\), where \(e^{At}\) is the matrix exponential. This operator generalizes the scalar exponential \(e^{\lambda t}\) to systems with multiple states. Each eigenvalue of \(A\) contributes a mode, and the overall response is a sum of those modes weighted by the initial conditions.

For a diagonal matrix, the exponential is the diagonal of the scalar exponentials. For a general matrix, the calculation involves the eigenvalues and eigenvectors or a series expansion. The key result is that the state decays to zero if and only if all eigenvalues have negative real parts."""},
        {"heading": "Key equations", "body_md": r"""Free response: \(x(t) = e^{At} x(0)\).

For a diagonal \(A = \mathrm{diag}(\lambda_1, \ldots, \lambda_n)\):
\[
e^{At} = \mathrm{diag}(e^{\lambda_1 t}, \ldots, e^{\lambda_n t}).
\]
The time constant of mode \(i\) is \(\tau_i = 1/|\mathrm{Re}(\lambda_i)|\). Forced response with constant input \(u\) adds a particular solution to the homogeneous one. The complete solution is \(x(t) = e^{At} x(0) + \int_0^t e^{A(t-\tau)} Bu\, d\tau\)."""},
        {"heading": "Worked example", "body_md": r"""Take \(A = \mathrm{diag}(-1, -3)\) and \(x(0) = [2, 1]^T\). The solution is
\[
x(t) = \begin{bmatrix} 2 e^{-t} \\ e^{-3t} \end{bmatrix}.
\]
At \(t = 1\), \(x_1 = 2 e^{-1} = 0.736\) and \(x_2 = e^{-3} = 0.050\). The \(-3\) mode is three times faster than the \(-1\) mode. After a few seconds the \(-3\) mode is negligible and the state is dominated by the slower \(-1\) mode. Using \(e^{-3}\) for the first component instead of \(e^{-1}\) applies the wrong eigenvalue."""},
        {"heading": "Common pitfalls", "body_md": r"""The matrix exponential is not the element-wise exponential of \(A\). For a non-diagonal matrix, you cannot just exponentiate the entries. The time constant is the reciprocal of the magnitude of the real part, not the eigenvalue itself. A complex eigenvalue gives an oscillating mode with an envelope that decays at rate \(|\mathrm{Re}(\lambda)|\). Confusing the imaginary part with the decay rate gives the wrong time constant."""},
        {"heading": "Where this leads", "body_md": r"""The eigenvalues of \(A\) are the modes that reachability and observability tests analyze. A realization of a transfer function assigns those eigenvalues to the poles. State feedback moves the eigenvalues by adding \(BK\) to \(A\), which changes the modes without changing the input matrix \(B\). Stability of a linear system is entirely determined by the eigenvalue locations."""},
    ]
    save_explainer("ss-solution", "State-space solution", sections)
    return words(sections)


def expl_loop_tf():
    fig = block_diagram(["G"], "loop transfer function", feedback="H", input_label="r", output_label="y", error_label="e")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A forward block and a return path that is subtracted at the input.",
         "body_md": r"""The loop transfer function \(L(s)\) is the product of every block you meet walking once around the loop. Start at the error, go through the forward path to the output, then through the return path back to the summing junction. That product tells you the loop gain at each frequency and determines stability and performance.

The closed-loop transfer function \(T(s) = G/(1+GH)\) is what the reference sees. The sensitivity \(S(s) = 1/(1+L)\) is what a disturbance sees. Together \(T + S = 1\). The return difference \(1 + L\) is what converts open-loop behavior to closed-loop behavior."""},
        {"heading": "Key equations", "body_md": r"""Loop gain: \(L(s) = G(s) H(s)\).

Closed-loop (complementary sensitivity): \(T(s) = \dfrac{G(s)}{1 + G(s)H(s)} = \dfrac{L(s)}{1 + L(s)}\).

Sensitivity: \(S(s) = \dfrac{1}{1 + L(s)}\).

Constraint: \(T(s) + S(s) = 1\). A disturbance at the output is multiplied by \(S\), so larger \(L\) means smaller disturbance effect."""},
        {"heading": "Worked example", "body_md": r"""Take \(G = 10\) and \(H = 0.2\). The loop gain is \(L = 10 \times 0.2 = 2\). The closed-loop gain is \(T = 10/3 = 3.333\). The sensitivity is \(S = 1/3 = 0.333\). Check: \(T + S = 3.333 + 0.333 \approx 1\) after rounding. A unit disturbance at the output is reduced to 0.333. Using the loop gain 2 as the closed-loop gain is wrong; 2 is the product around the loop, not the gain from reference to output."""},
        {"heading": "Common pitfalls", "body_md": r"""The loop gain is not the closed-loop gain. The loop gain is the open-loop product around the loop. The closed-loop gain divides by \(1 + L\). Confusing sensitivity with complementary sensitivity swaps what the reference sees and what the disturbance sees. The return difference \(1 + L\) is not the loop gain; it is one more than the loop gain. On a Nyquist plot, the critical point is \(-1\), not \(0\) or \(1\)."""},
        {"heading": "Where this leads", "body_md": r"""A Nyquist plot draws \(L(j\omega)\) in the complex plane and counts encirclements of \(-1\) to determine stability. Sensitivity analysis asks how large \(S(j\omega)\) can be before the loop is too sensitive to disturbances. Robust performance bounds combine \(S\) and \(T\) with uncertainty descriptions. The loop transfer function is the central object in all of these analyses."""},
    ]
    save_explainer("loop-tf", "Loop transfer function", sections)
    return words(sections)


def expl_equilibria():
    fig = step_response("settling to equilibrium", tau=2, goal=3)
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A curve that settles to a constant.",
         "body_md": r"""An equilibrium point is a state where the system does not change. For the model \(\dot{x} = f(x, u)\) with a constant input \(u\), the equilibrium satisfies \(f(x_e, u) = 0\). The state \(x_e\) is where the system rests if it starts there or settles there from nearby initial conditions.

Finding equilibria is the first step before linearization. You expand the nonlinear model around the equilibrium to get a linear model that is accurate for small deviations. The equilibrium depends on the input: a larger input usually shifts the resting state."""},
        {"heading": "Key equations", "body_md": r"""Equilibrium condition: \(\dot{x} = 0\).

For a linear system \(\dot{x} = Ax + Bu\), the equilibrium is \(x_e = -A^{-1} B u\) when \(A\) is invertible.

For a scalar system \(\dot{x} = a - bx\), the equilibrium is \(x_e = a/b\).

Stability: if all eigenvalues of \(A\) (or \(\partial f/\partial x\) at equilibrium) have negative real parts, the equilibrium is asymptotically stable and the state converges to it from nearby."""},
        {"heading": "Worked example", "body_md": r"""Take \(\dot{x} = 4 - 0.5x\). Set the right-hand side to zero: \(4 = 0.5x\), so \(x_e = 8\). The coefficient of \(x\) is \(-0.5\), which is negative, so the equilibrium is stable. Starting from \(x(0) = 0\), the state rises toward 8. Starting from \(x(0) = 12\), the state falls toward 8. The time constant is \(1/0.5 = 2\) s. Using the input 4 as the equilibrium is wrong; the equilibrium is the input divided by the decay coefficient."""},
        {"heading": "Common pitfalls", "body_md": r"""The equilibrium is not zero unless the input is zero and the unforced system has a resting point at the origin. The equilibrium depends on the input. Confusing the equilibrium with the initial condition misses the point: the equilibrium is where the system ends up, not where it starts. For a nonlinear system, there may be multiple equilibria, and not all of them are stable."""},
        {"heading": "Where this leads", "body_md": r"""Linearization builds a linear model around the equilibrium. The eigenvalues of the linearized \(A\) matrix determine local stability. System identification measures the equilibrium and the response to small perturbations. Limit cycles are periodic orbits that are not equilibria; they require nonlinearity."""},
    ]
    save_explainer("equilibria", "Equilibrium points", sections)
    return words(sections)


def expl_cruise():
    fig = block_diagram(["Kc", "P"], "cruise loop", feedback="1", input_label="r", output_label="v", disturbance="d")
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A controller, a plant, and a disturbance at the output.",
         "body_md": r"""A cruise-control system holds a car's speed at a reference set by the driver. The throttle is the actuator, and the speed is the output. Grades, headwinds, and rolling resistance act as disturbances that the loop must reject.

Proportional control multiplies the speed error by a gain \(K_c\). The loop gain is \(L = K_c P\), where \(P\) is the plant's DC gain. A larger loop gain reduces the steady error and the effect of disturbances, but it also risks instability if the plant has lags or delays. Integral action can eliminate steady error entirely."""},
        {"heading": "Key equations", "body_md": r"""Loop gain: \(L = K_c P\).

Steady speed: \(v = \dfrac{L}{1+L} r\). Steady error: \(e = r - v = \dfrac{r}{1+L}\).

Disturbance effect: a disturbance \(d\) at the output adds \(\dfrac{d}{1+L}\) to the speed. Sensitivity: \(S = \dfrac{1}{1+L}\)."""},
        {"heading": "Worked example", "body_md": r"""Take \(K_c = 4\) and plant gain \(P = 5\). The loop gain is \(L = 20\). With a speed reference of 25, the steady speed is \(v = 20/21 \times 25 = 23.81\), and the steady error is \(25/21 = 1.19\). A drag increase of \(d = -1\) drops the speed by \(1/21 = 0.048\). Using the loop gain 20 as the speed is wrong; the speed is the fraction \(L/(1+L)\) of the reference. Doubling \(K_c\) halves the error but cannot reach zero without integral action."""},
        {"heading": "Common pitfalls", "body_md": r"""Proportional control cannot eliminate steady error. The error is \(r/(1+L)\), which is positive no matter how large \(L\) is. Integral action is needed for zero steady error. Confusing the loop gain with the closed-loop gain gives the wrong speed. Increasing \(K_c\) too far can destabilize the loop, especially if the plant has high-frequency dynamics."""},
        {"heading": "Where this leads", "body_md": r"""PID tuning adjusts \(K_c\), the integral gain, and the derivative gain to meet transient and steady-state specs. Feedforward can reduce the error before the feedback loop sees it. Gain scheduling adjusts \(K_c\) as the plant gain changes with speed or load. Robust design accounts for uncertainty in the plant model."""},
    ]
    save_explainer("cruise-control", "Cruise control", sections)
    return words(sections)


def expl_app_examples():
    fig = step_response("tank level", tau=8, goal=2)
    sections = [
        {"heading": "The idea", "figure_svg": fig,
         "figure_alt": "A curve that rises and settles.",
         "body_md": r"""State-space models apply to any system with stored quantities. A tank stores liquid, so the level is the state. A motor stores angular momentum, so the speed is the state. A pendulum stores energy in position and velocity, so it has two states.

The modeling process is the same: identify the stored quantities, write the balance laws, and package them as \(\dot{x} = Ax + Bu\). The parameters change (tank area instead of inertia, hydraulic resistance instead of damping), but the structure is the same. This lets you reuse the same analysis tools across domains."""},
        {"heading": "Key equations", "body_md": r"""Tank: \(\dot{h} = \dfrac{q_{in}}{A} - \dfrac{h}{AR}\). Time constant \(\tau = AR\).

Motor: \(\dot{\omega} = \dfrac{K_t i}{J} - \dfrac{b\omega}{J}\). Time constant \(\tau = J/b\).

Pendulum (linearized near downward): \(\ddot{\theta} + \dfrac{g}{\ell}\theta = 0\). Natural frequency \(\omega_n = \sqrt{g/\ell}\)."""},
        {"heading": "Worked example", "body_md": r"""A tank has area \(A = 2\) m\(^2\) and hydraulic resistance \(R = 4\) s/m\(^2\). The time constant is \(\tau = 2 \times 4 = 8\) s. With inflow \(q_{in} = 0.5\) m\(^3\)/s, the equilibrium level is \(h_e = q_{in} R = 0.5 \times 4 = 2\) m. The state-space coefficient is \(-1/(AR) = -1/8 = -0.125\). Using the area or the resistance alone as the time constant is wrong; the time constant is their product."""},
        {"heading": "Common pitfalls", "body_md": r"""Different domains use different symbols for the same concept. The time constant is \(J/b\) for a motor and \(AR\) for a tank, but both are the ratio of storage capacity to dissipation. Confusing the input with the state (like calling the inflow a state) gives the wrong model. The linearized pendulum is valid only for small angles; large swings break the approximation."""},
        {"heading": "Where this leads", "body_md": r"""Realization writes a transfer function as a state-space model. Discrete-time models sample the continuous model at fixed intervals. Linearization builds a linear model around an operating point of a nonlinear system. All of these steps start with the state-space form that this skill introduces."""},
    ]
    save_explainer("app-examples", "Application examples", sections)
    return words(sections)


def lint():
    banned = re.compile(r"niknejad|åström|aström|astrom|murray|feedback systems|\breader\b|§", re.I)
    skills = ["second-order-sys", "ss-solution", "loop-tf", "equilibria", "cruise-control", "app-examples"]
    problems = []
    for sid in skills:
        bank = json.load(open(os.path.join(BANK, f"{sid}.json"), encoding="utf-8"))
        exp = json.load(open(os.path.join(EXP, f"{sid}.json"), encoding="utf-8"))
        nfig = 0
        idxs = []
        for q in bank["questions"]:
            blob = json.dumps(q, ensure_ascii=False)
            if banned.search(blob):
                problems.append(f"{q['id']} banned wording")
            if q.get("figure"):
                nfig += 1
            if q["type"] == "mc":
                idxs.append(q["correct_index"])
        if nfig < 9:
            problems.append(f"{sid} only {nfig} figures")
        if len(idxs) % 4 == 0 and idxs:
            from collections import Counter
            c = Counter(idxs)
            if len(c) != 4 or len(set(c.values())) != 1:
                problems.append(f"{sid} MC positions {dict(c)}")
        wc = words(exp["sections"])
        if not (250 <= wc <= 500):
            problems.append(f"{sid} explainer words {wc}")
        blob = json.dumps(exp, ensure_ascii=False)
        if banned.search(re.sub(r"<svg[\s\S]*?</svg>", "", blob)):
            problems.append(f"{sid} explainer banned wording")
        print(f"{sid}: questions {len(bank['questions'])}, figures {nfig}, MC idx {idxs}, explainer words {wc}")
    if problems:
        print("LINT FAIL")
        for p in problems:
            print(" ", p)
        sys.exit(1)
    print("lint ok")


def main():
    bank_second_order()
    bank_ss_solution()
    bank_loop_tf()
    bank_equilibria()
    bank_cruise()
    bank_app_examples()
    print("words", expl_second_order(), expl_ss_solution(), expl_loop_tf(), expl_equilibria(), expl_cruise(), expl_app_examples())
    lint()


if __name__ == "__main__":
    main()
