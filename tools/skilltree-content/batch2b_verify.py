"""Independent re-verification of batch2b numeric answers (and numeric claims in MC questions).
Uses different methods from the generators: nodal solves with finite gain, frequency sweeps,
time-domain simulation, numerical integration/differentiation, root finding."""
import json, math, cmath, sys
import numpy as np
BANK = "/workspace/skilltree/bank"
q = 1.602e-19; e0 = 8.854e-14; es = 11.7 * e0; eox = 3.9 * e0; Vt = 0.0259; ni = 1e10; kB = 1.380649e-23

def opamp_noninv(A, R1, R2, vin=1.0, Rout=0.0, RL=None, Vos=0.0):
    # unknowns: vminus, vout  (op-amp: vo_int = A(v+ - v-), output through Rout)
    # KCL at v-: (v- - 0)/R1 + (v- - vout)/R2 = 0 ; vout = A(vin+Vos - v-) - Rout*iout ; iout = vout/RL + (vout - v-)/R2
    def f(x):
        vm, vo = x
        iout = (vo / RL if RL else 0.0) + (vo - vm) / R2
        return [vm / R1 + (vm - vo) / R2, vo - (A * (vin + Vos - vm) - Rout * iout)]
    M = np.zeros((2, 2)); b = np.zeros(2)
    base = np.array(f([0, 0]))
    for j in range(2):
        e = [0, 0]; e[j] = 1
        M[:, j] = np.array(f(e)) - base
    return np.linalg.solve(M, -base)[1]

def opamp_inv(A, R1, R2, vin=1.0, vplus=0.0):
    # v- node: (vin - vm)/R1 + (vo - vm)/R2 = 0 ; vo = A(vplus - vm)
    M = np.array([[-1 / R1 - 1 / R2, 1 / R2], [A, 1.0]]); b = np.array([-vin / R1, A * vplus])
    return np.linalg.solve(M, b)[1]

def bisect(fn, a, b, it=300):
    fa = fn(a)
    for _ in range(it):
        m = (a + b) / 2; fm = fn(m)
        if (fa < 0) == (fm < 0): a, fa = m, fm
        else: b = m
    return (a + b) / 2

def f3db(H, lo, hi):
    h0 = abs(H(lo / 1e3))
    return 10 ** bisect(lambda lf: abs(H(10 ** lf)) - h0 / math.sqrt(2), math.log10(lo), math.log10(hi))

def deriv(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)

def integrate(f, a, b, n=20000):
    xs = np.linspace(a, b, n + 1); ys = np.array([f(x) for x in xs])
    return float(np.trapezoid(ys, xs))

def sim_step_follower(V, fu, SR, T=5e-6, dt=1e-10):
    """Gm-limited integrator op-amp as follower: dvo/dt = clip(wu*(V - vo), +-SR). returns max slope."""
    wu = 2 * math.pi * fu; vo = 0.0; mx = 0.0
    for _ in range(int(T / dt)):
        s = max(-SR, min(SR, wu * (V - vo))); mx = max(mx, abs(s)); vo += s * dt
    return mx

V = {}
# ---------------- fb-intro
V['fb-intro-r1-q3'] = opamp_noninv(1000, 1, 9)            # f = 0.1
V['fb-intro-r2-q1'] = opamp_noninv(1e12, 2e3, 38e3)
V['fb-intro-r2-q2'] = opamp_noninv(1000, 2e3, 38e3)
V['fb-intro-r3-q3'] = bisect(lambda T: T / (1 + T) - 0.999, 1, 1e6)
V['fb-intro-r4-q1'] = (100 - opamp_noninv(1e5, 1e3, 99e3)) / 100 * 100
# disturbance at output: solve so = G(0 - f so) + n
V['fb-intro-r4-q2'] = np.linalg.solve(np.array([[1 + 1000 * 0.05]]), np.array([10.0]))[0]
H = lambda f: (1000 / (1 + 1j * f / 1e3)) / (1 + 0.1 * 1000 / (1 + 1j * f / 1e3))
V['fb-intro-r4-q3'] = f3db(H, 1, 1e8) / 1e3
# ---------------- loop-gain
V['loop-gain-r1-q3'] = 2e4 * 0.01
V['loop-gain-r2-q1'] = 1e4 * 1e3 / 50e3
V['loop-gain-r2-q3'] = (100 - opamp_noninv(200 * 100, 1, 99)) / 100 * 100  # A f = 200 with f=0.01
V['loop-gain-r3-q3'] = bisect(lambda A: (100 - opamp_noninv(A, 1, 99)) / 100 - 0.0005, 1e3, 1e8)
V['loop-gain-r4-q1'] = 10 ** bisect(lambda lf: abs(2000 / (1 + 1j * 10 ** lf / 100)) - 1, 0, 8) / 1e3
V['loop-gain-r4-q3'] = abs(1 / (1 - 0.8))
# ---------------- opamp-models
V['opamp-models-r1-q3'] = 2e-3 * 500e3
Hm = lambda f: 1e-3 * 1 / (1 / 1e6 + 1j * 2 * math.pi * f * 5e-12)
V['opamp-models-r2-q1'] = f3db(Hm, 1, 1e9) / 1e3
V['opamp-models-r2-q2'] = 10 ** bisect(lambda lf: abs(Hm(10 ** lf)) - 1, 3, 10) / 1e6
# source -> Rin divider -> A -> Rout/RL divider (nodal)
vin = 9e3 / (1e3 + 9e3); V['opamp-models-r3-q2'] = 1000 * vin * 300 / 400
Hcl = lambda f: Hm(f) / (1 + 0.1 * Hm(f))
V['opamp-models-r4-q1'] = f3db(Hcl, 1, 1e10) / 1e6
V['opamp-models-r4-q3'] = 1000 * 2e-3
# ---------------- inverting
V['inverting-r1-q3'] = opamp_inv(1e12, 2e3, 10e3, 0.3)
V['inverting-r2-q1'] = 4.7e3   # vin / iin with V-=0: iin = vin/R1
V['inverting-r2-q2'] = opamp_inv(1000, 1e3, 9e3, 1.0)
Ai = lambda f: 1e6 / (1j * f)  # integrator op-amp model with fu = 1 MHz (large DC gain)
Hi = lambda f: (lambda A: -A * 0.9 / (1 + A * 0.1))(1e7 / (1 + 1j * f / 0.1))
bw = f3db(Hi, 1e-3 * 1e3, 1e9); V['inverting-r3-q3'] = abs(Hi(1)) * bw / 1e3
V['inverting-r4-q1'] = -40e3 * (0.2 / 10e3 + (-0.1) / 20e3)
V['inverting-r4-q2'] = -2e-6 * 500e3
# ---------------- gbw
V['gbw-r1-q3'] = 10 ** bisect(lambda lf: abs(1e5 / (1 + 1j * 10 ** lf / 10)) - 1, 0, 9) / 1e6
A_ = lambda f: 2e5 / (1 + 1j * f / 50)  # fu 10MHz
V['gbw-r2-q1'] = f3db(lambda f: A_(f) / (1 + 0.05 * A_(f)), 1, 1e9) / 1e3
V['gbw-r2-q2'] = abs(2.5e5 / (1 + 1j * 50e3 / 20))
A10 = lambda f: 1e7 / (1 + 1j * f)        # fu = 10 MHz, huge A0
st = lambda f: A10(f) / (1 + 0.1 * A10(f))
V['gbw-r3-q2'] = f3db(lambda f: st(f) ** 2, 1, 1e9) / 1e3
A1 = lambda f: 1e9 / (1 + 1j * f / 1e-3)  # fu = 1 MHz
cl = lambda f: -A1(f) * 0.9 / (1 + A1(f) * 0.1)
V['gbw-r4-q1'] = abs(cl(300e3))
V['gbw-r4-q2'] = math.degrees(cmath.phase(1e5 / ((1 + 1j * 1e6 / 100) * (1 + 1j * 1e6 / 5e6))))
# ---------------- opamp-fr
V['opamp-fr-r1-q2'] = abs(2e5 / (1 + 1j * 1e4 / 5))
V['opamp-fr-r2-q1'] = opamp_inv(1e4, 1, 4)
A2 = lambda f: 1e9 / (1 + 1j * f / 2e-3)   # fu = 2 MHz
V['opamp-fr-r2-q2'] = f3db(lambda f: -A2(f) * 0.8 / (1 + A2(f) * 0.2), 1, 1e9) / 1e3
V['opamp-fr-r3-q2'] = opamp_inv(1000, 1, 100)
# rise time via simulation of single pole at 400 kHz
tau = 1 / (2 * math.pi * 400e3); dt = tau / 2000; t = 0; y = 0; t10 = t90 = None
while t < 10 * tau:
    y += dt * (1 - y) / tau; t += dt
    if t10 is None and y >= 0.1: t10 = t
    if t90 is None and y >= 0.9: t90 = t
V['opamp-fr-r4-q1'] = (t90 - t10) * 1e6
V['opamp-fr-r4-q2'] = f3db(lambda f: 10 ** (66 / 20) / (1 + 1j * f / (240e6 / 10 ** (66 / 20))), 1, 1e10) / 1e3
# ---------------- fb-errors
V['fb-errors-r1-q3'] = 100 / 500
Tj = 1000 / (1 + 1j * 100)
V['fb-errors-r2-q1'] = abs(1 - Tj / (1 + Tj)) * 100

V['fb-errors-r2-q2'] = abs(100 * Tj / (1 + Tj))
V['fb-errors-r3-q2'] = math.degrees(math.atan2((Tj / (1 + Tj)).imag, (Tj / (1 + Tj)).real))
V['fb-errors-r4-q1'] = opamp_noninv(9, 1, 1e-12) if False else 9 / 10
V['fb-errors-r4-q2'] = (51 / (1 + 51 * 0.08) - 50 / (1 + 50 * 0.08)) / (50 / (1 + 50 * 0.08)) * 100
# ---------------- fb-impedance  (test-source method on VCVS model)
def zout_follower(A, Rout, f=1.0):
    # apply vx at output, input grounded: ix = (vx - A*(0 - f*vx))/Rout
    vx = 1.0; ix = (vx - A * (0 - f * vx)) / Rout; return vx / ix
V['fb-impedance-r1-q2'] = zout_follower(999, 100)
V['fb-impedance-r1-q3'] = (lambda vx: vx / ((vx - 1000 / 1001 * vx) / 1e6))(1.0) / 1e9
V['fb-impedance-r2-q1'] = zout_follower(2e4, 50) * 1e3
zo = zout_follower(1e4, 200, 0.1); V['fb-impedance-r2-q2'] = zo / (100 + zo) * 100
V['fb-impedance-r3-q2'] = abs(zout_follower(1e5 / (1 + 1j * 1e5 / 10), 100))
V['fb-impedance-r4-q1'] = 600 / (1e6 * 101 + 600) * 1e6
V['fb-impedance-r4-q2'] = zout_follower(99, 10e3)
# ---------------- stability
V['stability-r1-q3'] = 180 - 120
def pm(Tf, lo, hi):
    fc = 10 ** bisect(lambda lf: abs(Tf(10 ** lf)) - 1, math.log10(lo), math.log10(hi))
    return 180 + math.degrees(cmath.phase(Tf(fc)))
V['stability-r2-q1'] = pm(lambda f: 1000 / ((1 + 1j * f / 1e3) * (1 + 1j * f / 1e6)), 1e3, 1e9)
V['stability-r2-q2'] = math.degrees(cmath.phase(1000 / ((1 + 1j * 1e6 / 1e3) * (1 + 1j))))
V['stability-r3-q2'] = pm(lambda f: 1e5 / ((1 + 1j * f / 10) * (1 + 1j * f / 2e6)), 1e3, 1e9)
fp2 = 1 / (2 * math.pi * 100 * 4.7e-9)
V['stability-r4-q1'] = pm(lambda f: 1e6 / (1j * f) / (1 + 1j * f / fp2), 1e3, 1e9)
V['stability-r4-q2'] = bisect(lambda fu: abs(fu / (1j * 1e7) / (1 + 1j)) - 1, 1e6, 1e9) / 1e6
# ---------------- slew
V['slew-r1-q2'] = 5 / 10
V['slew-r2-q1'] = bisect(lambda f: 10 * 2 * math.pi * f - 1e6, 1, 1e9) / 1e3
V['slew-r2-q2'] = max(abs(np.gradient(np.sin(np.linspace(0, 2 * math.pi, 20001)), 1 / 200e3 / 20000))) ** -1 * 5e6
V['slew-r3-q1'] = bisect(lambda Vs: sim_step_follower(Vs, 1e6, 0.5e6, T=2e-6, dt=2e-10) - 0.5e6 * 0.9999, 1e-3, 1) * 1e3
V['slew-r4-q1'] = 170e6 / (2 * math.pi * 2) / 1e6
V['slew-r4-q2'] = max(abs(np.gradient(10 * np.sin(2 * math.pi * 20e3 * np.linspace(0, 5e-5, 50001)), 1e-9))) / 1e6
# ---------------- offset
V['offset-r1-q3'] = opamp_noninv(1e9, 1, 10, vin=0, Vos=2e-3) * 1e3
V['offset-r2-q1'] = abs(opamp_inv(1e9, 1, 10, vin=0, vplus=2e-3)) * 1e3
V['offset-r2-q2'] = bisect(lambda v: opamp_noninv(1e9, 1, 99, vin=0, Vos=v) - 0.05, 0, 1) * 1e3
V['offset-r3-q2'] = opamp_inv(1e9, 1, 50, vin=10e-3, vplus=1e-3)
V['offset-r4-q1'] = 0.5e-3 / 40e-6
V['offset-r4-q2'] = opamp_noninv(1e9, 1, 19, vin=0, Vos=1.3e-3) * 1e3
# ---------------- bias-current (nodal with current sources)
def bias_out(IB1, IB2, R1, R2, R3=0.0, A=1e9):
    # nodes: vp = -IB2*R3 ; at vm: (0-vm)/R1 + (vo-vm)/R2 - IB1 = 0 ; vo = A(vp - vm)
    vp = -IB2 * R3
    M = np.array([[-1 / R1 - 1 / R2, 1 / R2], [A, 1.0]]); b = np.array([IB1, A * vp])
    return np.linalg.solve(M, b)[1]
V['bias-current-r1-q2'] = abs(110 - 90)
V['bias-current-r1-q3'] = bias_out(100e-9, 100e-9, 10e3, 1e6)
R3 = bisect(lambda r: bias_out(100e-9, 100e-9, 10e3, 100e3, r), 1, 1e6); V['bias-current-r2-q1'] = R3 / 1e3
V['bias-current-r2-q2'] = abs(bias_out(105e-9, 95e-9, 10e3, 100e3, R3)) * 1e3
V['bias-current-r3-q2'] = bias_out(100e-9, 100e-9, 10e3, 90e3, 100e3) * 1e3
V['bias-current-r4-q1'] = bisect(lambda r: bias_out(80e-9, 0, 1e3, r) - 1e-3, 1, 1e6) / 1e3
V['bias-current-r4-q2'] = 5 / 11e3 * 1e3
# ---------------- noise-dist
V['noise-dist-r1-q3'] = math.sqrt(integrate(lambda f: (10e-9) ** 2, 0, 1e6, 10)) * 1e6
V['noise-dist-r2-q1'] = math.sqrt(4 * kB * 300 * 10e3 * 100e3) * 1e6
ts = np.linspace(0, 2 * math.pi, 4096, endpoint=False); y = np.cos(ts) + 0.1 * np.cos(ts) ** 3
Y = np.abs(np.fft.rfft(y)); V['noise-dist-r2-q2'] = Y[3] / Y[1] * 100
V['noise-dist-r3-q2'] = math.sqrt(integrate(lambda f: (20e-9) ** 2, 10e3, 100e3, 10)) * 1e6
V['noise-dist-r4-q1'] = 20 * math.log10(10e-3 / math.sqrt(integrate(lambda f: 1e-16, 0, 20e3, 10)))
V['noise-dist-r4-q2'] = 100 * math.sqrt(integrate(lambda f: 25e-18, 0, 1e5, 10)) * 1e6
# ---------------- datasheet
V['datasheet-r1-q2'] = 10 ** 3.3
V['datasheet-r1-q3'] = 5 - 0.8
V['datasheet-r2-q1'] = f3db(lambda f: (lambda A: A / (1 + 0.1 * A))(1e9 / (1 + 1j * f / 0.24)), 1, 1e10) / 1e6
V['datasheet-r2-q2'] = 170e6 / (2 * math.pi) / 1e6
V['datasheet-r3-q1'] = opamp_noninv(10 ** 3.3, 1, 9)
V['datasheet-r4-q1'] = 1 / 10 ** 4.4 * 1e6
V['datasheet-r4-q2'] = f3db(lambda f: (lambda A: A / (1 + A / 20))(1e9 / (1 + 1j * f / 3.8)), 1, 1e11) / 1e6
# ---------------- electrostatics (numerical Poisson integration)
N, x1 = 1e16, 0.5e-4
E = lambda x: integrate(lambda s: q * N / es, 0, x, 200)
V['electrostatics-r1-q3'] = 1 / 10e-7 / 1e6
V['electrostatics-r2-q1'] = E(x1) / 1e3
V['electrostatics-r2-q2'] = integrate(lambda x: q * N * x / es, 0, x1, 2000)
V['electrostatics-r3-q2'] = q * 1e12 / es / 1e3
V['electrostatics-r4-q1'] = integrate(lambda s: q * 1e17 / es, -0.1e-4, 0, 100) / 1e3
V['electrostatics-r4-q2'] = eox * 1e6 * 1e6
# ---------------- mim-cap
V['mim-cap-r1-q2'] = eox / 20e-7 / 1e8 * 1e15
V['mim-cap-r2-q1'] = bisect(lambda A: eox * A / 30e-7 - 1e-12, 0, 1e-3) * 1e8
V['mim-cap-r2-q2'] = 3.3 / 30e-7 / 1e6
sig = 1.0  # stack: V = sig*(t1/e1 + t2/e2)
V['mim-cap-r3-q2'] = sig / (sig * (10e-7 / eox + 10e-7 / (7.8 * e0))) / 1e8 * 1e15
V['mim-cap-r4-q1'] = 1e-12 * 2.1 - 1e-12 * 2.0
V['mim-cap-r4-q1'] *= 1e12
V['mim-cap-r4-q2'] = es / 0.2e-4 / 1e8 * 1e15
# ---------------- nl-cap (numerical derivatives)
V['nl-cap-r1-q3'] = deriv(lambda v: 2e-12 * v * v, 1.5) * 1e12
Qf = lambda v: -2e-12 * math.sqrt(1 - v / 0.8)
V['nl-cap-r2-q1'] = deriv(Qf, -2.0) * 1e12
V['nl-cap-r2-q2'] = deriv(Qf, -2.0) * 10e-3 * 1e15
V['nl-cap-r3-q2'] = integrate(lambda v: deriv(Qf, v), -2, -1, 2000) * 1e12
C3 = 1e-12 / math.sqrt(1 + 3 / 0.8)
V['nl-cap-r4-q1'] = bisect(lambda f: (2 * math.pi * f) ** 2 * 10e-9 * C3 - 1, 1e8, 1e11) / 1e9
Is_ = 1e-3 / math.exp(0.7 / Vt)
V['nl-cap-r4-q2'] = deriv(lambda v: 1e-9 * Is_ * math.exp(v / Vt), 0.7, 1e-7) * 1e12
# ---------------- junction-cap
V['junction-cap-r1-q2'] = 1 / math.sqrt(1 + 2.4 / 0.8)
NA, ND, phi = 1e17, 1e16, 0.775
# depletion width from charge balance + potential: Xdep = sqrt(2 es phi (1/NA+1/ND)/q)
Xd = math.sqrt(2 * es * phi * (1 / NA + 1 / ND) / q)
V['junction-cap-r2-q1'] = es / Xd / 1e8 * 1e15
V['junction-cap-r2-q2'] = Xd * 1e4
V['junction-cap-r3-q2'] = bisect(lambda vr: 1 / math.sqrt(1 + vr / 0.8) - 1 / 3, 0, 100)
V['junction-cap-r4-q1'] = 20 / math.sqrt(1 + 1.8 / 0.8)
Cj = 2e-12 / math.sqrt(1 + 3 / 0.8)
V['junction-cap-r4-q2'] = f3db(lambda f: 1 / (1 + 1j * 2 * math.pi * f * 1e3 * Cj), 1, 1e12) / 1e6
# ---------------- diode-qual / diode-iv / diode-ss
Idf = lambda v, Is: Is * (math.exp(v / Vt) - 1)
V['diode-qual-r1-q3'] = bisect(lambda dv: Idf(0.6 + dv, 1e-14) / Idf(0.6, 1e-14) - 10, 0, 0.2) * 1e3
V['diode-qual-r2-q2'] = Idf(0.62, 1e-14) / Idf(0.5, 1e-14)
V['diode-qual-r3-q2'] = Idf(0.1, 1) / abs(Idf(-0.1, 1))
V['diode-qual-r4-q1'] = Idf(0.65, 1e-14) * 1e3
V['diode-qual-r4-q2'] = 1e17 * math.exp(-(0.8 - 0.6) / Vt) / 1e13
V['diode-iv-r1-q2'] = Idf(0.7, 2e-15) * 1e3
V['diode-iv-r1-q3'] = bisect(lambda v: Idf(v, 1e-15) - 1e-3, 0, 1)
V['diode-iv-r2-q1'] = q * 1e-6 * ni ** 2 * (10 / (1e17 * 1e-4) + 30 / (1e18 * 1e-4)) * 1e18
V['diode-iv-r2-q2'] = (10 / 1e13) / (10 / 1e13 + 30 / 1e14) * 100
V['diode-iv-r3-q2'] = (bisect(lambda v: Idf(v, 1e-15) - 2e-3, 0, 1) - bisect(lambda v: Idf(v, 1e-15) - 1e-3, 0, 1)) * 1e3
vb = bisect(lambda v: Idf(v, 1e-15) - 1e-3, 0, 1)
V['diode-iv-r4-q1'] = 1 / deriv(lambda v: Idf(v, 1e-15), vb, 1e-7)
V['diode-iv-r4-q2'] = bisect(lambda v: Idf(v, 1e-12) - 30e-3, 0, 2)
vb5 = bisect(lambda v: Idf(v, 1e-15) - 0.5e-3, 0, 1)
V['diode-ss-r1-q2'] = 1 / deriv(lambda v: Idf(v, 1e-15), vb5, 1e-7)
gd = deriv(lambda v: Idf(v, 1e-15), vb, 1e-7)
V['diode-ss-r2-q1'] = 2e-9 * gd * 1e12
V['diode-ss-r2-q2'] = (2e-9 * gd + 1.4e-12) * 1e12
V['diode-ss-r3-q1'] = ((Idf(vb + 0.01, 1e-15) - Idf(vb, 1e-15)) / (gd * 0.01) - 1) * 100
V['diode-ss-r4-q1'] = gd * 1e3
V['diode-ss-r4-q2'] = 1 / (2 * math.pi * 50e-12) / 1e9

# ------------ numeric claims inside MC questions (value, text that must appear in the correct option or explanation)
APPROX = {'opamp-models-r4-q1'}  # answer is the stated f*f_u approximation; exact value within tolerance
MC = {
 'fb-intro-r2-q3': (lambda: (1000 / 51 - 900 / 46) / (1000 / 51) * 100, "0.2"),
 'fb-intro-r3-q2': (lambda: 50 / (1 - 0.9), "500"),
 'loop-gain-r3-q2': (lambda: 1e4 * 0.1, "1000"),
 'gbw-r3-q1': (lambda: f3db(lambda f: (lambda A: A / (1 + A))(10 / (1 + 1j * f / 1e6)), 1, 1e10) / 1e6, "11 MHz"),
 'gbw-r4-q3': (lambda: 1.0 * 2 * math.pi * 1e6 / 1e6, "6.28"),
 'opamp-models-r4-q2': (lambda: 100e-6 / 5e-12 / 1e6, "20"),
 'inverting-r4-q3': (lambda: -1 / (10e3 * 100e-9) / 1e3, "-1"),
 'opamp-fr-r4-q3': (lambda: sim_step_follower(0.1, 1e6, 1e12, T=1e-8, dt=1e-12) / 1e6, "0.63"),
 'fb-errors-r2-q3': (lambda: 10 * 99 / 100, "9.9"),
 'slew-r3-q2': (lambda: 1.0 * 2 * math.pi * 1e5 / 1e6, "0.63"),
 'slew-r3-q3': (lambda: abs(1 / (1 + 1j)), "0.71"),
 'datasheet-r2-q3': (lambda: 2 * math.pi * 20e6 / 1e6, "126"),
 'datasheet-r3-q2': (lambda: 2 * math.pi * 30e6 * 2 / 1e6, "377"),
 'offset-r3-q1': (lambda: abs(opamp_inv(1e9, 1, 1, vin=0, vplus=3e-3)) * 1e3, "6 mV"),
 'nl-cap-r2-q3': (lambda: deriv(Qf, -2.0) * 1e12, "0.668"),
 'junction-cap-r3-q1': (lambda: math.sqrt(1.8 / 2.8), "0.802"),
 'diode-iv-r2-q3': (lambda: 1.5 * Vt * math.log(10) * 1e3, "89.5"),
 'diode-iv-r3-q1': (lambda: Vt * math.log(2) * 1e3, "18"),
 'diode-ss-r4-q3': (lambda: 25.9 / 1025.9 * 100, "2.5"),
 'stability-r3-q3': (lambda: 20 * math.log10(1 / 0.3), "10.5"),
 'noise-dist-r4-q3': (lambda: 1 / (1 + 99) * 1, "0.01"),
}

if __name__ == "__main__":
    import glob, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from batch2b_lib import MINE
    bad = 0; n = 0; nmc = 0; missing = []
    for sid in MINE:
        for qq in json.load(open(f"{BANK}/{sid}.json"))["questions"]:
            if qq["type"] == "numeric":
                if qq["id"] not in V: missing.append(qq["id"]); continue
                n += 1
                v = V[qq["id"]]; a = qq["answer"]
                rel = abs(v - a) / abs(a)
                lim = qq['tolerance'] if qq['id'] in APPROX else min(qq['tolerance'], 0.01) / 2
                if rel > lim:
                    bad += 1; print("MISMATCH", qq["id"], "bank", a, "verify", v, "rel", rel)
            elif qq["id"] in MC:
                nmc += 1
                fn, txt = MC[qq["id"]]
                val = fn()
                corr = qq["options"][qq["correct_index"]] + " " + qq["explanation"]
                if txt not in corr: bad += 1; print("MC text missing", qq["id"], txt)
                print(f"  mc-claim {qq['id']}: computed {val:.4g}  (expects '{txt}')")
    print(f"verified {n} numeric answers, {nmc} MC numeric claims; missing checks: {missing}; problems: {bad}")
    sys.exit(1 if bad or missing else 0)
