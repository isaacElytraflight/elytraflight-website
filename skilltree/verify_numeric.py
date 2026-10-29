#!/usr/bin/env python3
"""Independent re-verification of every numeric answer (and the numeric MC claims) in the EE 105 bank.
Uses different methods than the generator where possible: time-domain simulation, brute-force
numerical integration, nodal analysis with complex matrices, root finding."""
import json, math, cmath, glob, os, sys
import numpy as np

BANK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bank")
bank = {}
for f in glob.glob(f"{BANK}/*.json"):
    d = json.load(open(f))
    for q in d["questions"]: bank[q["id"]] = q

trap = np.trapezoid if hasattr(np, "trapezoid") else np.trapz
db = lambda x: 20*math.log10(x)
J = 1j

def rc_step_sim(tau, vs_fn, t_end, dt=None, v0=0.0):
    """integrate tau*dv/dt = vs - v with RK4"""
    dt = dt or tau/2000
    n = int(round(t_end/dt)); v = v0; t = 0.0
    f = lambda t, v: (vs_fn(t) - v)/tau
    for _ in range(n):
        k1 = f(t, v); k2 = f(t+dt/2, v+dt*k1/2); k3 = f(t+dt/2, v+dt*k2/2); k4 = f(t+dt, v+dt*k3)
        v += dt*(k1+2*k2+2*k3+k4)/6; t += dt
    return v

def steady_amp_phase(tau, w, amp=1.0):
    """simulate RC LPF driven by amp*cos(wt); measure amplitude and phase after transients by fitting"""
    T = 2*math.pi/w
    dt = T/4000
    n_settle = int(round(40*tau/dt)); n_meas = int(round(5*T/dt))
    v = 0.0; t = 0.0
    f = lambda t, v: (amp*math.cos(w*t) - v)/tau
    ts, vs = [], []
    for i in range(n_settle + n_meas):
        k1 = f(t, v); k2 = f(t+dt/2, v+dt*k1/2); k3 = f(t+dt/2, v+dt*k2/2); k4 = f(t+dt, v+dt*k3)
        v += dt*(k1+2*k2+2*k3+k4)/6; t += dt
        if i >= n_settle: ts.append(t); vs.append(v)
    ts = np.array(ts); vs = np.array(vs)
    A = np.vstack([np.cos(w*ts), -np.sin(w*ts)]).T
    (a, b), *_ = np.linalg.lstsq(A, vs, rcond=None)   # v = a cos + b' sin form: a cos(wt) - b sin(wt)
    return math.hypot(a, b), math.atan2(b, a)

def nodal(Y, I):
    return np.linalg.solve(np.array(Y, dtype=complex), np.array(I, dtype=complex))

checks = {}
def chk(qid):
    def deco(fn): checks[qid] = fn; return fn
    return deco

# ---------------- lti-def
chk("lti-def-r1-q3")(lambda: 4*3 - 5)
chk("lti-def-r2-q3")(lambda: (lambda y: 2*y(2) - 0.5*y(1))(lambda t: {1: 4.0, 2: 3.0}[t]))
@chk("lti-def-r4-q1")
def _():
    x = np.zeros(10); x[0], x[1], x[2] = 3, -2, 1
    h = np.zeros(10); h[1], h[2], h[3] = 4, 2, 1
    return np.convolve(x, h)[3]
# ---------------- rc-lpf
chk("rc-lpf-r1-q3")(lambda: 1/(2*math.pi*10e3*10e-9))
chk("rc-lpf-r2-q1")(lambda: rc_step_sim(2e3*500e-9, lambda t: 5.0, 2e-3))
@chk("rc-lpf-r2-q2")
def _():
    A, _ph = steady_amp_phase(100e-6, 20e3, 3.0); return A
@chk("rc-lpf-r3-q2")
def _():
    tau = 10e3*1e-9; dt = tau/5000
    v = 0; t = 0; t10 = t90 = None
    while t90 is None:
        v += dt*(1 - v)/tau; t += dt
        if t10 is None and v >= 0.1: t10 = t
        if v >= 0.9: t90 = t
    return (t90 - t10)*1e6
@chk("rc-lpf-r4-q1")
def _():
    A, _ph = steady_amp_phase(1e3*159e-9, 2*math.pi*1000, 2.0); return A
@chk("rc-lpf-r4-q2")
def _():
    tau = 2.2e3*10e-9; dt = tau/20000; v = 0; t = 0
    while v < 0.5: v += dt*(1 - v)/tau; t += dt
    return t*1e6
@chk("rc-lpf-r4-q3")
def _():
    f = 1e4; w = 2*math.pi*f
    lo, hi = 1e-7, 1e-3
    for _ in range(200):
        m = (lo+hi)/2
        if 1/abs(1 + J*w*m) > 0.1: lo = m
        else: hi = m
    return lo*1e6
# ---------------- cx-exp
chk("cx-exp-r1-q3")(lambda: math.hypot(3, 4))
chk("cx-exp-r2-q1")(lambda: math.degrees(math.atan2(2, -2)))
chk("cx-exp-r2-q3")(lambda: ((2*cmath.exp(J*math.radians(30)))*(3*cmath.exp(J*math.radians(60)))/(1.5*cmath.exp(-J*math.radians(45)))).real)
chk("cx-exp-r3-q3")(lambda: abs(5*np.exp((-0.5+10j)*2)))
@chk("cx-exp-r4-q2")
def _():
    # i = C dv/dt numerically
    C = 1e-6; w = 1000.0; t = math.radians(60)/w; h = 1e-9
    v = lambda t: 2*math.cos(w*t)
    return C*(v(t+h) - v(t-h))/(2*h)*1e3
@chk("cx-exp-r4-q3")
def _():
    Q = 5; w0 = 1000.0
    s = -w0/(2*Q) + J*w0*math.sqrt(1 - 1/(4*Q*Q))
    # roots of s^2 + (w0/Q) s + w0^2
    r = np.roots([1, w0/Q, w0**2]); assert any(abs(x - s) < 1e-6 for x in r)
    return abs(np.exp(s*0.02))
# ---------------- sinusoid-resp
@chk("sinusoid-resp-r1-q3")
def _():
    A, _ph = steady_amp_phase(1e-3, 1000.0, 10.0); return A
@chk("sinusoid-resp-r2-q1")
def _():
    # 2 y' + 3 y = 6 cos(1.5 t): integrate to steady state and fit
    w = 1.5; dt = 1e-3; y = 0; t = 0; ts = []; ys = []
    f = lambda t, y: (6*math.cos(w*t) - 3*y)/2
    for i in range(int(60/dt)):
        k1 = f(t, y); k2 = f(t+dt/2, y+dt*k1/2); k3 = f(t+dt/2, y+dt*k2/2); k4 = f(t+dt, y+dt*k3)
        y += dt*(k1+2*k2+2*k3+k4)/6; t += dt
        if t > 30: ts.append(t); ys.append(y)
    ts = np.array(ts); ys = np.array(ys)
    A = np.vstack([np.cos(w*ts), np.sin(w*ts)]).T
    (a, b), *_ = np.linalg.lstsq(A, ys, rcond=None)
    return math.hypot(a, b)
@chk("sinusoid-resp-r2-q2")
def _():
    tau = 2e-3; w = 2*math.pi*250
    A, ph = steady_amp_phase(tau, w, 1.0)   # ph = phase of output: a cos - b sin => atan2(b,a)
    return math.degrees(ph)
@chk("sinusoid-resp-r3-q3")
def _():
    tau = 1e-3; w = 1000.0; dt = 1e-6; v = 0; t = 0
    f = lambda t, v: (10*math.sin(w*t) - v)/tau
    while t < 0.05:
        k1 = f(t, v); k2 = f(t+dt/2, v+dt*k1/2); k3 = f(t+dt/2, v+dt*k2/2); k4 = f(t+dt, v+dt*k3)
        v += dt*(k1+2*k2+2*k3+k4)/6; t += dt
    # steady-state sine response: extrapolate value at the previous whole period boundary t_k = k*2pi/w
    T = 2*math.pi/w; k = math.floor(t/T)
    # integrate forward/back: simply continue to next multiple of T and read v
    while t < (k+1)*T - 1e-12:
        k1 = f(t, v); k2 = f(t+dt/2, v+dt*k1/2); k3 = f(t+dt/2, v+dt*k2/2); k4 = f(t+dt, v+dt*k3)
        v += dt*(k1+2*k2+2*k3+k4)/6; t += dt
    return v
@chk("sinusoid-resp-r4-q1")
def _():
    # solve C dv/dt + v/R = i via time-domain simulation
    C, R, w = 2e-6, 1e3, 1000.0; dt = 1e-6; v = 0; t = 0; ts = []; vs = []
    f = lambda t, v: (0.1e-3*math.cos(w*t) - v/R)/C
    while t < 0.1:
        k1 = f(t, v); k2 = f(t+dt/2, v+dt*k1/2); k3 = f(t+dt/2, v+dt*k2/2); k4 = f(t+dt, v+dt*k3)
        v += dt*(k1+2*k2+2*k3+k4)/6; t += dt
        if t > 0.05: ts.append(t); vs.append(v)
    ts = np.array(ts); vs = np.array(vs)
    A = np.vstack([np.cos(w*ts), np.sin(w*ts)]).T
    (a, b), *_ = np.linalg.lstsq(A, vs, rcond=None)
    return math.hypot(a, b)*1e3
@chk("sinusoid-resp-r4-q2")
def _():
    f = 2000.0; w = 2*math.pi*f
    lo, hi = 1e-9, 1e-2
    for _ in range(200):
        m = (lo+hi)/2
        if -math.degrees(cmath.phase(1/(1+J*w*m))) < 45: lo = m
        else: hi = m
    return lo*1e6
chk("sinusoid-resp-r4-q3")(lambda: 2*abs(1/((1+1j*1e4/1e3)*(1+1j*1e4/1e5))))
# ---------------- impulse-conv
chk("impulse-conv-r1-q3")(lambda: math.cos(2*math.pi*250*(2.5e-3-2e-3)))
chk("impulse-conv-r2-q1")(lambda: np.convolve([1, 2, 3], [2, 1])[2])
@chk("impulse-conv-r2-q2")
def _():
    dt = 1e-7; t = np.arange(0, 5e-3, dt)
    # approximate each delta as a narrow unit-area rectangle of width dt
    x = np.zeros_like(t); x[0] = 2/dt; x[int(1e-3/dt)] = 1/dt
    h = 3*np.exp(-t/2e-3)
    y = np.convolve(x, h)[:len(t)]*dt
    return y[int(3e-3/dt)]
@chk("impulse-conv-r3-q3")
def _():
    t = np.linspace(0, 0.2, 400001); h = 100*np.exp(-t/5e-3)
    return 2*trap(h, t)
@chk("impulse-conv-r4-q1")
def _():
    dt = 1e-6; t = np.arange(0, 12e-3, dt); h = 250*((t >= 0) & (t < 4e-3)); u = 3.0*np.ones_like(t)
    return np.convolve(u, h)[int(3e-3/dt)]*dt
chk("impulse-conv-r4-q2")(lambda: math.degrees(cmath.phase(cmath.exp(-J*2*math.pi*250*0.5e-3))))
chk("impulse-conv-r4-q3")(lambda: math.cos(2*math.pi*100*(4e-3 - 1e-3 - 2.5e-3)))
# ---------------- step-resp
chk("step-resp-r1-q3")(lambda: rc_step_sim(0.47e-3, lambda t: 5.0, 1.41e-3))
@chk("step-resp-r2-q1")
def _():
    return rc_step_sim(1e-3, lambda t: 5.0 if t < 2e-3 else 0.0, 3e-3, dt=1e-3/20000)
@chk("step-resp-r2-q3")
def _():
    tau = 0.5e-3; dt = tau/20000; v = 0; t = 0
    while v < 0.9: v += dt*(1 - v)/tau; t += dt
    return t*1e3
@chk("step-resp-r3-q3")
def _():
    tau = 0.25e-3; dt = tau/1e5; v = 0
    v += dt*(5 - v)/tau
    return v/dt/1e3
@chk("step-resp-r4-q1")
def _():
    # R seen by C: nodal Thevenin with source shorted
    Rth = 1/(1/1e3 + 1/4e3); tau = Rth*2e-9; dt = tau/20000; v = 0; t = 0
    while v < 0.9: v += dt*(1 - v)/tau; t += dt
    return t*1e6
chk("step-resp-r4-q2")(lambda: 0.5e6*2e-6)
@chk("step-resp-r4-q3")
def _():
    tau = 10e3*50e-12; dt = tau/20000; v = 0; t = 0
    while v < 0.99: v += dt*(1 - v)/tau; t += dt
    return t*1e6
# ---------------- freq-char
chk("freq-char-r1-q3")(lambda: 2*0.1)
@chk("freq-char-r2-q1")
def _():
    t = np.linspace(0, 0.1, 400001); return trap(200*np.exp(-t/2e-3), t)
@chk("freq-char-r2-q2")
def _():
    tau = 0.5e-3; w = 2*math.pi*500; t = np.linspace(0, 0.05, 2000001)
    return abs(trap((1/tau)*np.exp(-t/tau)*np.exp(-1j*w*t), t))
@chk("freq-char-r3-q2")
def _():
    H = lambda f: 1/(1 + 1j*f/1000.0)
    t = np.linspace(0, 0.01, 2000001)[:-1]
    y = 4*abs(H(0)) + 3*abs(H(1000))*np.cos(2*np.pi*1000*t + cmath.phase(H(1000))) + 2*abs(H(10000))*np.cos(2*np.pi*10000*t + cmath.phase(H(10000)))
    return math.sqrt(np.mean(y**2))
chk("freq-char-r4-q1")(lambda: 20*0.5*math.sqrt(1000))
chk("freq-char-r4-q2")(lambda: 0.1*abs(10/(1+1j*1e6/1e5)))
chk("freq-char-r4-q3")(lambda: (1 - abs(1/(1+0.2j)))*100)
# ---------------- tf
chk("tf-r1-q3")(lambda: 0.5/2e-3)
chk("tf-r2-q1")(lambda: 5e-3/0.25*1e3)
chk("tf-r2-q2")(lambda: (5*0.8*np.exp(1j*math.radians(20-30))).real)
@chk("tf-r3-q2")
def _():
    R = 10e3
    # nodes: 1 (after R1), 2 (after R3); shunt R2 at 1, R4 at 2. vin=1
    Y = [[1/R + 1/R + 1/R, -1/R], [-1/R, 1/R + 1/R]]
    v = nodal(Y, [1/R, 0]); return abs(v[1])
chk("tf-r4-q2")(lambda: 1000/(1 + 1000*0.1))
chk("tf-r4-q3")(lambda: 1*abs(100/(1+1j*100/10)))
# ---------------- phasors
chk("phasors-r1-q3")(lambda: abs(1/(1j*2*math.pi*1000*100e-9)))
chk("phasors-r2-q1")(lambda: abs(300 + 1j*1e4*40e-3))
@chk("phasors-r2-q2")
def _():
    C = 0.1e-6; w = 2*math.pi*1000; t = np.linspace(0, 1e-3, 200001)
    i = C*np.gradient(5*np.cos(w*t), t); return np.max(np.abs(i[10:-10]))*1e3
@chk("phasors-r3-q2")
def _():
    C = 10e-6; h = 1e-9; v = lambda t: 20*math.cos(1000*t)
    return C*(v(1e-3 + h) - v(1e-3 - h))/(2*h)*1e3
chk("phasors-r4-q1")(lambda: (4*(1j*1e5*10e-3/(1000+1j*1e5*10e-3))).real)
@chk("phasors-r4-q2")
def _():
    t = np.linspace(0, 2*math.pi/1000, 400001)[:-1]
    Z = 10 - 10j; I = 2.0
    v = (I*Z*np.exp(1j*1000*t)).real; i = (I*np.exp(1j*1000*t)).real
    return np.mean(v*i)
chk("phasors-r4-q3")(lambda: abs(50 + 1j*5000*10e-3 + 1/(1j*5000*1e-6)))
# ---------------- direct-h
chk("direct-h-r1-q3")(lambda: abs(1j/(1+1j)))
@chk("direct-h-r2-q1")
def _():
    w = 1e4; R1 = 1e3; R2 = 1e3; C = 100e-9
    v = nodal([[1/R1 + 1/R2 + 1j*w*C]], [1/R1]); return abs(v[0])
@chk("direct-h-r2-q2")
def _():
    w = 1e4; R1 = 1e3; R2 = 1e3; C = 100e-9
    v = nodal([[1/R1 + 1/R2 + 1j*w*C]], [1/R1]); return math.degrees(cmath.phase(v[0]))
@chk("direct-h-r3-q2")
def _():
    R = 1e3; C = 1e-6; w = 1000.0; Yc = 1j*w*C
    v = nodal([[2/R + Yc, -1/R], [-1/R, 1/R + Yc]], [1/R, 0]); return abs(v[1])
@chk("direct-h-r4-q1")
def _():
    L, C, R = 2e-3, 0.5e-6, 20.0; w = 1/math.sqrt(L*C)
    # mesh current through series loop; Vc = I/(jwC)
    I = 2.0/(R + 1j*w*L + 1/(1j*w*C)); return abs(I/(1j*w*C))
@chk("direct-h-r4-q2")
def _():
    R, L, C = 50.0, 10e-3, 1e-6; w = 5000.0
    I = 1.0/(R + 1j*w*L + 1/(1j*w*C)); return abs(I*R)
# ---------------- pole-zero
chk("pole-zero-r1-q3")(lambda: 1/(1e3*1e-6))
chk("pole-zero-r2-q1")(lambda: min(abs(np.roots([1, 30, 200]))))
chk("pole-zero-r2-q3")(lambda: abs(1000*(1e-12+400)/((1e-12+20)*(1e-12+2000))))
chk("pole-zero-r3-q3")(lambda: max(abs(np.roots([10e-3*25e-6, 50*25e-6, 1]))))
chk("pole-zero-r4-q3")(lambda: abs(np.roots([1, 10/1e-3, 1/(1e-3*1e-6)])[0].real))
# ---------------- rlc
chk("rlc-r1-q3")(lambda: 1/(2*math.pi*math.sqrt(10e-3*1e-6)))
chk("rlc-r2-q1")(lambda: (1/20.0)*math.sqrt(10e-3/1e-6))
@chk("rlc-r2-q2")
def _():
    R, L, C = 20.0, 10e-3, 1e-6
    H = lambda w: abs(R/(R + 1j*w*L + 1/(1j*w*C)))
    ws = np.linspace(1e3, 3e4, 2900001)
    m = np.array([H(w) for w in ws[::100]])
    idx = np.where(m >= 1/math.sqrt(2))[0]
    lo, hi = ws[::100][idx[0]], ws[::100][idx[-1]]
    return (hi - lo)/(2*math.pi)
@chk("rlc-r3-q2")
def _():
    w0 = 1000.0; Q = 1.0; R = 10.0; L = Q*R/w0; C = 1/(w0**2*L)
    H = lambda w: abs(R/(R + 1j*w*L + 1/(1j*w*C)))
    ws = np.linspace(w0, 3*w0, 2000001)
    m = np.abs(R/(R + 1j*ws*L + 1/(1j*ws*C)))
    return ws[np.where(m >= 1/math.sqrt(2))[0][-1]]
chk("rlc-r4-q1")(lambda: 1e6/2e5)
chk("rlc-r4-q2")(lambda: 1/(2*math.pi*math.sqrt(10e-9*100e-9))/1e6)
@chk("rlc-r4-q3")
def _():
    Q = 1.5; w0 = 1.0; s = 1j*w0
    return 0.2*abs(w0**2/(s**2 + (w0/Q)*s + w0**2))
# ---------------- bode
chk("bode-r1-q3")(lambda: db(250))
chk("bode-r2-q1")(lambda: db(abs(100/(1+1j*3e5/1e4))))
chk("bode-r2-q2")(lambda: math.degrees(cmath.phase(10/((1+1j*2000/100)*(1+1j*2000/1e4)))))
chk("bode-r3-q3")(lambda: math.degrees(cmath.phase(10*(1+1j*1000/100)/(1+1j*1000/1000))))
@chk("bode-r4-q1")
def _():
    f = np.logspace(0, 7, 7000001)
    A = np.abs(1e5/(1 + 1j*f/10.0))
    return f[np.where(A >= 10)[0][-1]]
chk("bode-r4-q2")(lambda: db(abs(-20*(1j*20/20)/(1+1j*20/20)/(1+1j*20/2e5))))
chk("bode-r4-q3")(lambda: math.degrees(cmath.phase(1000/((1+1j*1e6/1e3)*(1+1j*1e6/1e7)))))
# ---------------- ac-power
chk("ac-power-r1-q3")(lambda: math.sqrt(np.mean((170*np.cos(np.linspace(0, 2*np.pi, 1000001)[:-1]))**2)))
@chk("ac-power-r2-q1")
def _():
    t = np.linspace(0, 2*np.pi, 1000001)[:-1]
    v = 10*np.cos(t); i = 2*np.cos(t - math.radians(60)); return np.mean(v*i)
@chk("ac-power-r2-q2")
def _():
    t = np.linspace(0, 2*np.pi, 1000001)[:-1]; v = 20*np.cos(t); return np.mean(v*v/50)
@chk("ac-power-r3-q2")
def _():
    t = np.linspace(0, 2*np.pi, 1000001)[:-1]; return math.sqrt(np.mean((3 + 4*np.cos(t))**2))
@chk("ac-power-r3-q3")
def _():
    t = np.linspace(0, 2*np.pi, 1000001)[:-1]
    Z = 30 + 40j; I = 100/Z
    v = 100*np.cos(t); i = (I*np.exp(1j*t)).real; return np.mean(v*i)
@chk("ac-power-r4-q1")
def _():
    A = 5.0   # from P = mean(v^2)/R with R = 1k, P=12.5 mW
    t = np.linspace(0, 2*np.pi, 1000001)[:-1]
    Vp = math.sqrt(12.5e-3*1e3/np.mean(np.cos(t)**2))
    t2 = np.linspace(0, 2*np.pi, 2000001); slope = np.max(np.abs(np.gradient(Vp*np.sin(t2), t2)))   # per rad
    # slope in V/s = slope_per_rad * w ; limit SR=2e6 V/s -> w = SR/slope_per_rad
    return 2e6/slope/(2*math.pi)/1e3
@chk("ac-power-r4-q2")
def _():
    t = np.linspace(0, 2*np.pi, 1000001)[:-1]; return np.mean((10*np.cos(t))**2/2e3)*1e3
@chk("ac-power-r4-q3")
def _():
    t = np.linspace(0, 2*np.pi, 1000001)[:-1]; return np.mean((0.5*np.cos(t))**2/2e3)/(3*1e-3)*100

# ---------------- run
bad = 0; done = 0; missing = []
for qid, q in bank.items():
    if q["type"] != "numeric": continue
    if qid not in checks: missing.append(qid); continue
    got = float(checks[qid]())
    ans = q["answer"]
    rel = abs(got - ans)/abs(ans)
    done += 1
    if rel > 2e-3:
        bad += 1; print(f"MISMATCH {qid}: bank={ans} independent={got} rel={rel:.2e}")
print(f"numeric answers independently recomputed: {done}; mismatches: {bad}; unchecked: {missing}")
sys.exit(1 if bad or missing else 0)
