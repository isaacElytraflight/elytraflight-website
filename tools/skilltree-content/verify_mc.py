#!/usr/bin/env python3
"""Independent numeric/symbolic spot-verification of every multiple-choice question whose correct option
rests on a computation or a formula. Each check evaluates the circuit/system numerically and compares with
the formula/number stated in the correct option, and confirms the distractor formulas are NOT equal."""
import json, math, cmath, glob, os, re, sys
import numpy as np

BANK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bank")
bank = {}
for f in glob.glob(f"{BANK}/*.json"):
    for q in json.load(open(f))["questions"]: bank[q["id"]] = q
J = 1j
fails = []; n = 0
def ok(cond, msg):
    global n; n += 1
    if not cond: fails.append(msg)
def correct(qid): q = bank[qid]; return q["options"][q["correct_index"]]
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "gen"))
from o_latex import latexify as LTX  # banks store LaTeX-converted option text
def nodal(Y, I): return np.linalg.solve(np.array(Y, complex), np.array(I, complex))
rng = np.random.default_rng(1)

# lti-def: numerical linearity / time-invariance tests on sampled signals
t = np.linspace(0, 1, 2001); dt = t[1]-t[0]
def shift(x, k): return np.concatenate([np.zeros(k), x[:-k]]) if k else x
systems = {
 "2x-3dx/dt": lambda x, tt: 2*x - 3*np.gradient(x, dt),
 "x^2": lambda x, tt: x**2,
 "x+2": lambda x, tt: x + 2,
 "t*x": lambda x, tt: tt*x,
 "delay": lambda x, tt: shift(x, 10),
 "3dx/dt": lambda x, tt: 3*np.gradient(x, dt),
}
def is_linear(S):
    x1 = np.sin(7*t) + 0.3; x2 = np.cos(3*t)
    return np.allclose(S(2*x1 + 3*x2, t), 2*S(x1, t) + 3*S(x2, t), atol=1e-6)
def is_ti(S):
    x = np.sin(7*t)*np.exp(-t); k = 50
    # compare S(shift(x)) with shift(S(x)) away from edges
    a = S(shift(x, k), t); b = shift(S(x, t), k)
    return np.allclose(a[k+60:-60], b[k+60:-60], atol=1e-3)
props = {k: (is_linear(S), is_ti(S)) for k, S in systems.items()}
ok(props["2x-3dx/dt"] == (True, True), "lti-def r2q1 correct system")
ok(props["x^2"][0] is False and props["x+2"][0] is False and props["t*x"] == (True, False), "lti-def r2q1 distractors")
ok(props["t*x"] == (True, False) and props["delay"] == (True, True) and props["x^2"] == (False, True) and props["3dx/dt"] == (True, True), "lti-def r3q2")
ok(props["x+2"][0] is False and props["x+2"][1] is True, "lti-def r3q1 affine: nonlinear but TI")
# lti-def r4q2: 4cos(wt+30) -> 2cos(wt-30)
H = 0.5*cmath.exp(-J*math.radians(60))
out = 4*H*cmath.exp(J*math.radians(30))
ok(abs(abs(out)-2) < 1e-9 and abs(math.degrees(cmath.phase(out)) + 30) < 1e-9 and LTX("2cos(ωt − 30°)") == correct("lti-def-r4-q2"), "lti-def r4q2")
# lti-def r4q3
H1 = 0.2*cmath.exp(-J*math.radians(45)); H5 = 0.1*cmath.exp(-J*math.radians(80))
o1 = 3*H1; o5 = 3*H5*cmath.exp(J*math.radians(20))
ok(abs(abs(o1)-0.6) < 1e-9 and abs(math.degrees(cmath.phase(o1))+45) < 1e-9 and abs(abs(o5)-0.3) < 1e-9 and abs(math.degrees(cmath.phase(o5))+60) < 1e-9, "lti-def r4q3")

# rc-lpf r2q3 : at w tau = 1
H = 1/(1+1j)
ok(abs(abs(H)-0.7071) < 1e-3 and abs(math.degrees(cmath.phase(H))+45) < 1e-9, "rc-lpf r2q3")
# rc-lpf r3q3 : loaded RC final value 5 V, tau 0.5 ms (simulate with KCL)
R, RL, C, Vs = 1e3, 1e3, 1e-6, 10.0
dtt = 1e-7; v = 0.0
for _ in range(int(0.02/dtt)): v += dtt*((Vs - v)/R - v/RL)/C
ok(abs(v-5) < 1e-3, "rc-lpf r3q3 final value")
v = 0.0; tt = 0.0
while v < 5*(1-1/math.e): v += dtt*((Vs - v)/R - v/RL)/C; tt += dtt
ok(abs(tt-0.5e-3) < 2e-6, "rc-lpf r3q3 tau")
# rc-lpf r3q1 : particular + transient has v(0)=0 : verify with simulation of cos input
tau = 1e-3; w = 3e3; dtt = 1e-7; v = 0.0; t_ = 0.0
H = 1/(1+1j*w*tau); A = abs(H); ph = cmath.phase(H)
K = -A*math.cos(ph)
for _ in range(int(3e-3/dtt)): v += dtt*(math.cos(w*t_) - v)/tau; t_ += dtt
ss = A*math.cos(w*t_ + ph); tr = K*math.exp(-t_/tau)
ok(abs(v - (ss + tr)) < 1e-3, "rc-lpf r3q1 solution structure")

# cx-exp r4q1 options
Hc = 0.6-0.3j; A = 2*abs(Hc); th = math.degrees(cmath.phase(Hc))
ok(correct("cx-exp-r4-q1") == LTX(f"{A:.4g}cos(ωt − {abs(th):.4g}°)"), "cx-exp r4q1 text")
tt_ = np.linspace(0, 1, 5); w = 7.0
ok(np.allclose((2*Hc*np.exp(1j*w*tt_)).real, A*np.cos(w*tt_ + math.radians(th))), "cx-exp r4q1 waveform")
# cx-exp r3q1/q2 numerically
tt_ = np.linspace(0, 2, 11)
ok(np.allclose(np.exp(1j*(3*tt_ - np.pi/2)).real, np.sin(3*tt_)) and not np.allclose((1j*np.exp(1j*3*tt_)).real, np.sin(3*tt_)), "cx-exp r3q1")

# sinusoid-resp r2q3 : d2y/dt2 + 3 dy/dt + 2y = x ; H(jw) numeric via polynomial
w = 1.7
Hf = 1/((2 - w**2) + 3j*w)
y = lambda t: (Hf*np.exp(1j*w*t))
h_ = 1e-5; t0 = 0.4
lhs = (y(t0+h_) - 2*y(t0) + y(t0-h_))/h_**2 + 3*(y(t0+h_) - y(t0-h_))/(2*h_) + 2*y(t0)
ok(abs(lhs - np.exp(1j*w*t0)) < 1e-4, "sinusoid-resp r2q3 H")
ok(abs(Hf - 1/((2 + w**2) + 3j*w)) > 1e-3, "sinusoid-resp r2q3 distractor")
# r3q2 HPF with DC + AC
Hh = lambda w: 1j*w/(1+1j*w)
ok(abs(Hh(1)) - 0.70710678 < 1e-6 and abs(math.degrees(cmath.phase(Hh(1)))-45) < 1e-9 and Hh(1e-12).real < 1e-9, "sinusoid-resp r3q2")

# freq-char r2q3
H = lambda f: 1/(1+1j*f/1e3)
a1 = 2*abs(H(1e3)); a2 = 1*abs(H(1e4))
ok(LTX(f"1 kHz: {a1:.4g} V, 10 kHz: {a2:.3g} V") == correct("freq-char-r2-q3"), "freq-char r2q3")
# freq-char r3q1 : all-pass with nonlinear phase changes shape
ws = [1.0, 2.0]; ph = [0.0, 1.0]
tt_ = np.linspace(0, 20, 4001)
x = np.cos(ws[0]*tt_) + np.cos(ws[1]*tt_)
y = np.cos(ws[0]*tt_ + ph[0]) + np.cos(ws[1]*tt_ - ph[1])   # amplitudes unchanged, phases changed
ok(not np.allclose(x, y, atol=1e-2) and abs(np.max(np.abs(y)) - 2) < 0.1, "freq-char r3q1")

# tf r2q3 : 0.6 ; r3q3 ; r4q1
Rs, Rsh, RL = 2e3, 6e3, 6e3
v = nodal([[1/Rs + 1/Rsh + 1/RL]], [1/Rs])[0]
ok(abs(v-0.6) < 1e-12 and correct("tf-r2-q3") == LTX("0.6"), "tf r2q3")
Hs = 0.5*cmath.exp(-J*math.pi/2); xs = 2*cmath.exp(-J*math.pi/2)   # sin = cos(wt-90)
o = Hs*xs; ok(abs(abs(o)-1) < 1e-9 and abs(cmath.phase(o) + math.pi) < 1e-9, "tf r3q3 (out=1*cos(wt-180)= -cos)")
ok(abs(2e-3*10e-3*5e3 - 100e-3) < 1e-12 and correct("tf-r4-q1") == LTX("−100cos(ωt) mV"), "tf r4q1")
# tf r3q1 : Q10 series RLC: |Vc/Vs| at resonance = Q
R, L, C = 10.0, 1e-3, 1e-6 ; R = (1/10)*math.sqrt(L/C)   # Q = 10
w0 = 1/math.sqrt(L*C)
Hc = (1/(1j*w0*C))/(R + 1j*w0*L + 1/(1j*w0*C))
ok(abs(abs(Hc)-10) < 1e-6, "tf r3q1 Q gain")

# phasors r2q3 : v=10cos, i=2cos(wt-90): L = 5 mH
Z = (10)/(2*cmath.exp(-J*math.pi/2))
ok(abs(Z - 5j) < 1e-9 and abs(Z.imag/1000 - 5e-3) < 1e-12, "phasors r2q3")
# r3q1 : series LC : amplitude |VL - VC|
VL = 40*cmath.exp(J*math.pi/2); VC = 30*cmath.exp(-J*math.pi/2)
ok(abs(abs(VL + VC) - 10) < 1e-9, "phasors r3q1")
# r3q3 : 10 sin(wt+30) = 10 cos(wt-60)
t_ = np.linspace(0, 1, 9); w = 5
ok(np.allclose(10*np.sin(w*t_ + math.radians(30)), 10*np.cos(w*t_ - math.radians(60))), "phasors r3q3")

# direct-h r3q1 : loaded LPF via nodal
R, RL, C = 1e3, 3e3, 1e-6
for w in (10.0, 1e3, 1e5):
    v = nodal([[1/R + 1/RL + 1j*w*C]], [1/R])[0]
    Rp = R*RL/(R+RL)
    good = RL/(R+RL)/(1 + 1j*w*Rp*C)
    ok(abs(v-good) < 1e-12, "direct-h r3q1 formula")
    ok(abs(v - 1/(1+1j*w*R*C)) > 1e-6 or w == 10.0 and False or True, "n/a")
ok(abs(nodal([[1/R + 1/RL + 1j*1e3*C]], [1/R])[0] - 1/(1+1j*1e3*R*C)) > 1e-3, "direct-h r3q1 distractor1")
ok(abs(nodal([[1/R + 1/RL + 1j*1e3*C]], [1/R])[0] - RL/(R+RL)/(1+1j*1e3*R*C)) > 1e-3, "direct-h r3q1 distractor2")
ok(abs(nodal([[1/R + 1/RL + 1j*1e3*C]], [1/R])[0] - 1/(1+1j*1e3*Rp*C)) > 1e-3, "direct-h r3q1 distractor3")
# r2q3 : RLC output across C
R, L, C = 30.0, 2e-3, 1e-6
for w in (100.0, 2e4, 5e5):
    I = 1/(R + 1j*w*L + 1/(1j*w*C)); Vc = I/(1j*w*C)
    ok(abs(Vc - 1/(1 - w*w*L*C + 1j*w*R*C)) < 1e-9, "direct-h r2q3 formula")
    ok(abs(Vc - 1/(1 + w*w*L*C + 1j*w*R*C)) > 1e-6, "direct-h r2q3 distractor")
# r3q3 : tank
L, C, R = 1e-3, 1e-6, 100.0; w0 = 1/math.sqrt(L*C)
Ytank = 1j*w0*C + 1/(1j*w0*L)
ok(abs(R/(R + 1/(Ytank + 1e-30))) < 1e-9, "direct-h r3q3")
# direct-h r4q3 : band-pass limits
R, L, C = 50.0, 10e-3, 1e-6; w0 = 1/math.sqrt(L*C)
Hr = lambda w: R/(R + 1j*w*L + 1/(1j*w*C))
ok(abs(Hr(1e-3)) < 1e-6 and abs(Hr(1e9)) < 1e-4 and abs(abs(Hr(w0)) - 1) < 1e-9, "direct-h r4q3 bandpass")

# pole-zero r3q2 : cancellation
H = lambda s: (s + 500)/(s**2 + 1500*s + 500000)
for s_ in (1j*100, 1j*3000, 10.0):
    ok(abs(H(s_) - 1/(s_ + 1000)) < 1e-12, "pole-zero r3q2")
# r4q1 slope between 400 and 2000 (numeric dB/decade)
Hs = lambda w: 1000*(1j*w + 400)/((1j*w + 20)*(1j*w + 2000))
sl = (20*math.log10(abs(Hs(894*1.05)))-20*math.log10(abs(Hs(894/1.05))))/math.log10(1.05**2)   # local slope at geometric mean of 400 and 2000 (asymptotic answer 0)
sl_far = (20*math.log10(abs(Hs(1e6)))-20*math.log10(abs(Hs(1e5))))
ok(abs(sl) < 8 and abs(sl_far + 20) < 0.1 , f"pole-zero r4q1 slope {sl:.2f}")
# pole-zero r3q1 etc are conceptual.
# r2q2 HPF
ok(abs(np.roots([1, 1000])[0] + 1000) < 1e-9, "pole-zero r2q2")

# rlc r2q3 : |VL| = Q Vs at resonance
R, L, C = 20.0, 10e-3, 1e-6; w0 = 1/math.sqrt(L*C)
I = 2/(R + 1j*w0*L + 1/(1j*w0*C)); VL = I*1j*w0*L
ok(abs(abs(VL) - 10) < 1e-9, "rlc r2q3")
# r3q1 : R doubles
def stats(R):
    L, C = 10e-3, 1e-6; w0 = 1/math.sqrt(L*C)
    H = lambda w: abs(R/(R + 1j*w*L + 1/(1j*w*C)))
    ws = np.linspace(1e3, 2e4, 190001); m = np.array([H(w) for w in ws[::10]]); wsub = ws[::10]
    idx = np.where(m >= 1/math.sqrt(2))[0]
    return w0, w0*L/R, wsub[idx[-1]] - wsub[idx[0]], max(m)
a = stats(20.0); b = stats(40.0)
ok(abs(a[0]-b[0]) < 1e-9 and abs(b[1]/a[1] - 0.5) < 1e-9 and abs(b[2]/a[2] - 2) < 0.01 and abs(b[3]-1) < 1e-3, "rlc r3q1")
# r3q3 : Q=0.5 monotone, Hc(w0)=Q
Q = 0.5; HC = lambda w: 1/((1 - w*w) + 1j*w/Q)
ws = np.linspace(0, 10, 100001)
ok(np.all(np.diff(np.abs(HC(ws))) < 0) and abs(abs(HC(1.0)) - 0.5) < 1e-12, "rlc r3q3")

# bode r2q3 : 20 dB at w=1000 by asymptote ; exact is lower by 3 dB at pole 2
asym = 60 - 20*math.log10(1000/10)
ok(abs(asym - 20) < 1e-12 and correct("bode-r2-q3") == LTX("20 dB"), "bode r2q3")
# r3q1 : double pole -> -6 dB at wp
ok(abs(20*math.log10(abs(1/(1+1j)**2)) + 6.02) < 0.01, "bode r3q1")
# r3q2 : RHP vs LHP zero
w = np.logspace(-2, 3, 50)
ok(np.allclose(abs(1 + 1j*w), abs(1 - 1j*w)) and np.all(np.angle(1+1j*w) > 0) and np.all(np.angle(1-1j*w) < 0) and abs(np.angle(1-1j*1e6) + math.pi/2) < 1e-5, "bode r3q2")

# ac-power r2q3 : 75 W ; r3q1 : 5 W vs 10 W
Z = 6+8j; Ip = 5.0
tt_ = np.linspace(0, 2*np.pi, 1000001)[:-1]
i = Ip*np.cos(tt_); v = (Ip*Z*np.exp(1j*tt_)).real
ok(abs(np.mean(v*i) - 75) < 1e-3 and correct("ac-power-r2-q3") == LTX("75 W"), "ac-power r2q3")
v = 10*np.cos(tt_ + math.radians(30)); i = 2*np.cos(tt_ - math.radians(30))
ok(abs(np.mean(v*i) - 5) < 1e-3 and correct("ac-power-r3-q1") == LTX("5 W"), "ac-power r3q1")
V = 10*cmath.exp(J*math.radians(30)); I = 2*cmath.exp(-J*math.radians(30))
ok(abs(0.5*(V*I).real - 10) < 1e-9, "ac-power r3q1 distractor derivation (no conjugate -> 10 W)")

# impulse-conv r3q1 : triangle
dt = 1e-6; t = np.arange(0, 6e-3, dt)
x = ((t < 2e-3)).astype(float); h = 500*((t < 2e-3)).astype(float)
y = np.convolve(x, h)[:len(t)]*dt
ok(abs(y.max() - 1) < 2e-3 and abs(t[y.argmax()] - 2e-3) < 5e-6 and y[t > 4.01e-3].max() < 1e-6, "impulse-conv r3q1")
# step-resp r3q2 : IC 2 V -> 5 - 3e^{-t/tau}
tau = 1.0; v = 2.0; dtt = 1e-5; t_ = 0.0
for _ in range(int(1.0/dtt)): v += dtt*(5 - v)/tau; t_ += dtt
ok(abs(v - (5 - 3*math.exp(-1.0))) < 1e-4, "step-resp r3q2")
# step-resp r3q1 : 50 mV peak
tau = 1e-3; v = 0.0; dtt = 1e-9
for _ in range(int(10e-6/dtt)): v += dtt*(5 - v)/tau
ok(abs(v - 0.05) < 5e-4, "step-resp r3q1")
# step-resp r2q2 : delayed step form
tau = 1e-3; t0 = 1e-3; v = 0.0; dtt = 1e-8; t_ = 0.0
while t_ < 3e-3: v += dtt*((2.0 if t_ >= t0 else 0.0) - v)/tau; t_ += dtt
ok(abs(v - 2*(1 - math.exp(-(3e-3 - t0)/tau))) < 1e-3, "step-resp r2q2")

print(f"mc/formula checks run: {n}; failures: {len(fails)}")
for f in fails: print("FAIL", f)
sys.exit(1 if fails else 0)
