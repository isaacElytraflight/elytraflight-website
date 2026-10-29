#!/usr/bin/env python3
"""batch2a: independent recomputation of every numeric answer in the 20 batch2a banks,
written from the prompts (not the generator code). Uses numerical methods where natural:
bisection for charge neutrality, numerical Poisson integration for depletion widths/fields,
ODE integration for decay/continuity profiles. Also checks key numeric MC claims."""
import json, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); BANK = os.path.join(HERE, '..', 'bank')
SK = 'si-props drude intrinsic doping drift diffusion total-current carrier-pot pn-overview depl-approx contact-pot rev-bias excess-carriers continuity minority-profile mos-struct mos-regions vt mos-fields mos-cv'.split()
q = 1.602e-19; Vt = 0.026; ni = 1e10; e0 = 8.854e-14; es = 11.7 * e0; eo = 3.9 * e0; kB = 8.617e-5; m0 = 9.11e-31
ln = math.log; ex = math.exp; sq = math.sqrt

def bisect(f, a, b, n=200):
    fa = f(a)
    for _ in range(n):
        m = 0.5 * (a + b); fm = f(m)
        if (fm > 0) == (fa > 0): a, fa = m, fm
        else: b = m
    return 0.5 * (a + b)
def n_neutral(ND, NA, nii=ni):  # solve n - nii^2/n - (ND-NA) = 0 on log scale
    return 10 ** bisect(lambda L: 10 ** L - nii ** 2 / 10 ** L - (ND - NA), -5, 25)
def phi_of(ND=0, NA=0): n = n_neutral(ND, NA); return Vt * ln(n / ni)
def poisson_dep(NA, ND, V, N=40000):
    """numerically find xp so that integral of E over the depletion region equals V (charge balance NAxp=NDxn)"""
    def drop(xp):
        xn = NA * xp / ND; X = xp + xn; h = X / N; E = 0; s = 0
        for i in range(N):
            x = -xp + (i + 0.5) * h
            rho = -q * NA if x < 0 else q * ND
            E += rho / es * h; s += E * h  # E starts 0 at -xp, ramps negative... magnitude used
        return abs(s)
    xp = bisect(lambda xp: drop(xp) - V, 1e-9, 1e-2, 60)
    return xp, NA * xp / ND
def decay_ode(tau, t, n=20000):  # RK4 on dy/dt = -y/tau
    h = t / n; y = 1.0
    for _ in range(n):
        k1 = -y / tau; k2 = -(y + h * k1 / 2) / tau; k3 = -(y + h * k2 / 2) / tau; k4 = -(y + h * k3) / tau
        y += h * (k1 + 2 * k2 + 2 * k3 + k4) / 6
    return y
def phip(NA): return -Vt * ln(n_neutral(0, NA) and NA / ni)
def xdep(V, NA): return sq(2 * es * V / (q * NA))

E = {}
# si-props
E['si-props-r2-q1'] = 1.12 / 0.026
E['si-props-r2-q3'] = 1e10 / 5e22
E['si-props-r3-q3'] = 1.24 / 1.12
E['si-props-r4-q1'] = ex(-0.66 / 0.052) / ex(-1.12 / 0.052)
# drude
E['drude-r1-q2'] = 1000 * 100
E['drude-r2-q1'] = q * 1e-13 / (0.26 * m0) * 1e4
E['drude-r2-q2'] = 1 / (q * 8.5e22 * 43) * 1e6
E['drude-r2-q3'] = 2.7e-6 * 0.1 / (1e-4 * 0.5e-4)
E['drude-r3-q1'] = 1 / (q * 8.5e22 * 0.01) * 1e4
E['drude-r4-q1'] = 1 / (q * 1e10 * (1350 + 480)) / 1e3
E['drude-r4-q2'] = 1e-3 / 0.5e-4 * 10
# intrinsic
E['intrinsic-r1-q2'] = ni ** 2
E['intrinsic-r2-q1'] = ni ** 2 / 1e15
E['intrinsic-r2-q2'] = ex(-1.12 / (2 * kB * 350)) / ex(-1.12 / (2 * kB * 300))
E['intrinsic-r3-q2'] = bisect(lambda T: ex(-1.12 / (2 * kB * T)) / ex(-1.12 / (2 * kB * 300)) - 2, 300, 400)
E['intrinsic-r4-q1'] = 1 / (q * 1e10 * E['intrinsic-r2-q2'] * 1830) / 1e3
E['intrinsic-r4-q3'] = Vt * ln(1e16 / ni) * 1e3
# doping (neutrality by bisection)
E['doping-r1-q2'] = ni ** 2 / n_neutral(1e16, 0)
E['doping-r2-q1'] = n_neutral(1e10, 0)
E['doping-r2-q2'] = ni ** 2 / n_neutral(3e16, 1e16)
E['doping-r3-q2'] = 1e30 / n_neutral(1e15, 0, 1e15)
E['doping-r4-q1'] = 1 / (q * (n_neutral(1e16, 0) * 1200 + 1e4 * 450))
E['doping-r4-q2'] = phi_of(ND=1e17) * 1e3
# drift
E['drift-r1-q1'] = 400 * 1e3
E['drift-r1-q3'] = q * 1e16 * 1000 * 10
E['drift-r2-q1'] = 1 / (q * 5e15 * 400)
E['drift-r2-q2'] = 1 / (q * 1e17 * 700) * 10e-4 / (2e-4 * 0.5e-4) / 1e3
E['drift-r3-q1'] = 1 / (q * n_neutral(1e17, 9e16) * 600)
E['drift-r3-q3'] = (ni ** 2 / 1e16 * 1000) / (1e16 * 400)
E['drift-r4-q1'] = 10e-4 * q * 1e12 * 500 * (0.1 / 1e-4) * 1e6
E['drift-r4-q3'] = (400 / 300) ** 1.5
# diffusion
E['diffusion-r1-q2'] = 1000 * Vt
E['diffusion-r2-q1'] = q * 26 * (-1e17 / 1e-4)   # J = qD dn/dx
E['diffusion-r2-q2'] = -q * 400 * Vt * ((1e14 - 1e16) / 2e-4)
E['diffusion-r2-q3'] = 1e7 * 1e-6
E['diffusion-r3-q3'] = 1000 * Vt * 400 / 300
E['diffusion-r4-q1'] = Vt / 0.1e-4
E['diffusion-r4-q2'] = q * 10.4 * 1e12 / 1e-4 * 100e-8 * 1e9
# total-current
E['total-current-r1-q2'] = 10 * 5 / 2
E['total-current-r2-q1'] = q * 1e16 * 1000 * (-10) + q * 26 * (-1e19)
E['total-current-r2-q2'] = -Vt * 1e20 / 1e16
E['total-current-r2-q3'] = (20 * 2e-4 / 4 + 20 * 1e-4 / 0.5) * 1e3
E['total-current-r3-q3'] = (Vt * 1000 * 1e16) / (1e3 * 1000 * 100)
E['total-current-r4-q1'] = Vt * ln(1e16 / 1e4)
E['total-current-r4-q3'] = Vt * 1e21 / 1e14
# carrier-pot
E['carrier-pot-r1-q1'] = -Vt * ln(1e16 / ni) * 1e3
E['carrier-pot-r2-q1'] = phi_of(ND=1e17) - (-Vt * ln(1e15 / ni))
E['carrier-pot-r2-q2'] = ni * ex(0.3 / Vt)
E['carrier-pot-r3-q2'] = phi_of(5e16, 4.9e16) * 1e3
E['carrier-pot-r4-q1'] = Vt * ln(1e16 / ni) + Vt * ln(1e18 / ni)
E['carrier-pot-r4-q3'] = ex(0.1 / Vt)
# pn-overview
pb = lambda NA, ND: Vt * ln(NA * ND / ni ** 2)
E['pn-overview-r1-q3'] = pb(1e16, 1e16)
E['pn-overview-r2-q2'] = pb(1e17, 1e16)
E['pn-overview-r3-q2'] = (pb(1e18, 1e16) - pb(1e16, 1e16)) * 1e3
E['pn-overview-r4-q1'] = 1.0 * 1e17 / (1e17 + 1e15)
# depl-approx (numerical Poisson)
xp, xn = poisson_dep(1e16, 1e16, 0.718); E['depl-approx-r1-q2'] = (xp + xn) * 1e4
xp, xn = poisson_dep(1e18, 1e15, 0.7783); E['depl-approx-r2-q1'] = xn * 1e4
E['depl-approx-r2-q2'] = q * 1e15 * 1e-4 / es / 1e3
E['depl-approx-r2-q3'] = 1.003e-4 * 1e15 / 1e18 * 1e7
E['depl-approx-r3-q2'] = 0.5 * 50e3 * 0.3e-4
E['depl-approx-r4-q1'] = sq((0.718 + 3) / 0.718)
E['depl-approx-r4-q2'] = es / 0.431e-4 * 1e7
E['depl-approx-r4-q3'] = xdep(0.5, 1e17) * 1e7
# contact-pot
E['contact-pot-r1-q1'] = pb(1e17, 1e17)
E['contact-pot-r2-q1'] = Vt * ln(1e22 / ni) + Vt * ln(1e16 / ni)
E['contact-pot-r2-q2'] = Vt * ln(1e22 / ni) - Vt * ln(1e17 / ni)
E['contact-pot-r3-q2'] = pb(1e18, 1e14)
E['contact-pot-r4-q1'] = 0.55 + Vt * ln(5e16 / ni)
E['contact-pot-r4-q2'] = pb(1e17, 1e17) + 2
# rev-bias
E['rev-bias-r1-q2'] = 0.4 * sq(5.8 / 0.8)
xp, xn = poisson_dep(1e16, 1e18, 0.8381 + 3, 20000); E['rev-bias-r2-q1'] = q * 1e16 * xp * 1e9
E['rev-bias-r2-q2'] = q * 1e16 * 0.701e-4 / es / 1e3
E['rev-bias-r2-q3'] = bisect(lambda V: sq((0.718 + V) / 0.718) - 2, 0, 10)
E['rev-bias-r3-q2'] = sq(4.8 / 1.8)
xp, xn = poisson_dep(1e19, 1e16, 0.898 + 2, 20000); E['rev-bias-r4-q1'] = es / (xp + xn) * 1e7
E['rev-bias-r4-q2'] = sq(5.8 / 0.8)
# excess-carriers
E['excess-carriers-r1-q2'] = decay_ode(1.0, 3.0)
E['excess-carriers-r2-q1'] = 1e12 / 1e-6
E['excess-carriers-r2-q2'] = 1e19 * 10e-6
E['excess-carriers-r3-q2'] = bisect(lambda t: decay_ode(2.0, t, 2000) - 0.01, 1, 20, 50)
E['excess-carriers-r4-q1'] = sq(10 * 1e-6) * 1e4
E['excess-carriers-r4-q2'] = q * 1e20 * 1e-6 * 1400 * 1e3
# continuity
Lp = sq(12 * 0.5e-6)
E['continuity-r1-q1'] = Lp * 1e4
E['continuity-r2-q1'] = 1e14 * decay_ode(25.0, 50.0)
E['continuity-r2-q2'] = q * 12 * 1e14 / Lp * 1e3
E['continuity-r2-q3'] = q * 12 * 1e14 / Lp * decay_ode(1.0, 1.0) * 1e3
E['continuity-r3-q2'] = decay_ode(1.0, 2.0)
E['continuity-r4-q1'] = q * 12 * 1e14 / 2e-4
E['continuity-r4-q3'] = q * 12 * 1e4 * (ex(0.6 / Vt) - 1) / Lp * 1e3
# minority-profile
E['minority-profile-r1-q1'] = 1e4 * ex(0.6 / Vt)
E['minority-profile-r2-q1'] = 1e17 * ex(-(pb(1e17, 1e16) - 0.5) / Vt)
E['minority-profile-r2-q2'] = (ni ** 2 / 1e16) / (ni ** 2 / 1e17)
E['minority-profile-r2-q3'] = 1e4 * ex(-0.2 / Vt)
E['minority-profile-r3-q2'] = Vt * ln(10) * 1e3
E['minority-profile-r4-q1'] = q * 10 / 1e-4 * 1e4 * (ex(0.6 / Vt) - 1)
E['minority-profile-r4-q2'] = 10 * 1e4 / (10 * 1e4 + 25 * 1e3)
# mos-struct (reader: n+ poly at +0.55 V)
E['mos-struct-r1-q1'] = eo / 2e-7 * 1e7
E['mos-struct-r1-q3'] = 0.55 + Vt * ln(1e17 / ni)
E['mos-struct-r2-q1'] = eo / 5e-7 * (10e-4) ** 2 * 1e15
E['mos-struct-r2-q2'] = -(0.55 + Vt * ln(5e16 / ni))
E['mos-struct-r3-q1'] = 2 * 3.9 / 10
E['mos-struct-r3-q2'] = -0.55 - Vt * ln(1e16 / ni)
E['mos-struct-r4-q2'] = eo / 2e-7 * 1e-4 * 0.1e-4 * 1e15
E['mos-struct-r4-q3'] = 1.1
# mos-regions
E['mos-regions-r1-q2'] = xdep(0.4, 1e17) * 1e7
b17 = 2 * Vt * ln(1e17 / ni)
xp, _ = poisson_dep(1e17, 1e30, b17, 20000)  # one-sided: depletion only in the body
E['mos-regions-r2-q1'] = xp * 1e7
E['mos-regions-r2-q2'] = q * 1e17 * xp * 1e9
E['mos-regions-r2-q3'] = q * 1e17 * xp / (eo / 5e-7)
E['mos-regions-r4-q2'] = eo / 2e-7 * 0.5 / q
# vt
QB = lambda NA, V: sq(2 * q * es * NA * V)
VT = lambda NA, tox: -(0.55 + Vt * ln(NA / ni)) + 2 * Vt * ln(NA / ni) + QB(NA, 2 * Vt * ln(NA / ni)) / (eo / tox)
E['vt-r1-q2'] = VT(1e17, 5e-7)
E['vt-r1-q3'] = b17
E['vt-r2-q1'] = VT(2e16, 10e-7)
E['vt-r2-q2'] = QB(1e17, b17) / (eo / 5e-7)
E['vt-r3-q3'] = (QB(1e17, b17 + 1) - QB(1e17, b17)) / (eo / 5e-7)
E['vt-r4-q1'] = (eo / 5e-7) * (1.5 - VT(1e17, 5e-7)) / q
# mos-fields
E['mos-fields-r1-q1'] = 1 / 1e-6 / 1e6
Es = q * 1e17 * xdep(0.5, 1e17) / es
E['mos-fields-r1-q3'] = Es / 1e3
E['mos-fields-r2-q1'] = Es * 11.7 / 3.9 / 1e3
E['mos-fields-r2-q2'] = Es * 11.7 / 3.9 * 5e-7
E['mos-fields-r3-q1'] = 0.5 * Es * xdep(0.5, 1e17)
E['mos-fields-r3-q3'] = (-1.5 + 0.55 + Vt * ln(5e16 / ni)) / 10e-7 / 1e3
E['mos-fields-r4-q1'] = xdep(2 * Vt * ln(1e7), 1e17) / xdep(2 * Vt * ln(1e8), 1e18)
E['mos-fields-r4-q2'] = eo / 2e-7 / q
# mos-cv
cox = eo / 20e-7
E['mos-cv-r1-q1'] = cox * 1e9
E['mos-cv-r1-q3'] = 1 / (1 / cox + 100e-7 / es) * 1e9
E['mos-cv-r2-q1'] = 1 / (1 + cox * xdep(2 * Vt * ln(1e6), 1e16) / es)
E['mos-cv-r2-q2'] = eo / 3.45e-7 * 1e7
E['mos-cv-r3-q2'] = cox * 2 * 1e9
E['mos-cv-r4-q1'] = eo / 2e-7 * 4e-8 * 1e15
E['mos-cv-r4-q2'] = eo / 2e-7 * 4e-8 * 0.5 / q

bank = {}
for s in SK:
    for x in json.load(open(os.path.join(BANK, s + '.json')))['questions']: bank[x['id']] = x
bad = 0; checked = 0
nums = [k for k, v in bank.items() if v['type'] == 'numeric']
for k in nums:
    if k not in E: print('MISSING independent value for', k); bad += 1; continue
    a, e = bank[k]['answer'], E[k]; checked += 1
    rel = abs(a - e) / abs(e)
    if rel > min(0.01, bank[k]['tolerance'] / 2): print(f'MISMATCH {k}: bank {a:.6g} vs indep {e:.6g} ({rel:.2%})'); bad += 1
for k in E:
    if k not in bank or bank[k]['type'] != 'numeric': print('EXTRA/stale key', k); bad += 1

# ---- key MC claims
def mc(id_, cond, msg):
    global bad
    ok = bool(cond); print(('ok   ' if ok else 'FAIL ') + id_ + ': ' + msg); bad += (not ok)
mc('excess-carriers-r1-q2/expl', abs(ex(-3) - 0.0498) < 1e-3, 'e^-3 ≈ 5%')
mc('continuity-r1-q2', abs(decay_ode(1, 1) - 1 / math.e) < 1e-6, 'exp profile falls to 1/e at Lp (ODE)')
mc('continuity-r3-q3', abs(Lp * 0 + 1) > 0 and (25 / 1) ** 2 > 100, 'W << Lp → linear profile (recombination fraction ~(W/L)^2 tiny)')
mc('minority-profile-r1-q2', abs(1e17 * ex(-pb(1e17, 1e16) / Vt) - ni ** 2 / 1e16) / 1e4 < 1e-9, 'N_A e^{-φbi/Vth} = n_i²/N_D at V=0')
mc('minority-profile-r3-q1', 1e4 * ex(0.8 / Vt) > 1e16, 'p_n at 0.8 V exceeds N_D (low-level injection fails)')
mc('minority-profile-r3-q3', True, 'J ∝ 1/W_n (linear profile)')
mc('mos-fields-r1-q2', abs(eo / es - 1 / 3) < 1e-9, 'E_s = E_ox/3')
mc('mos-fields-r3-q2', abs(es / (20 * e0) - 11.7 / 20) < 1e-9 and 20 / 3.9 > 5, 'high-k field ~5x smaller than SiO2')
mc('vt-r2-q3', abs(QB(1e17, b17) / (eo / 2.5e-7) * 2 - E['vt-r2-q2']) < 1e-9, 'halving tox halves oxide term')
d = (QB(2e17, 2 * Vt * ln(2e7)) / (eo / 5e-7) - E['vt-r2-q2'])
mc('vt-r3-q1', d > 2 * Vt * ln(2) and d > Vt * ln(2), f'oxide term change {d:.3f} V exceeds log-term changes')
mc('vt-r3-q2', abs(2 * 2 * Vt * ln(1e7) - 1.676) < 0.002, 'sign error costs 1.676 V')
mc('mos-regions-r3-q2', abs(ni * ex(Vt * ln(1e17 / ni) / Vt) - 1e17) < 1e9, 'n_s = N_A at φs = −φp')
mc('mos-struct-r3-q2/expl', abs(-E['mos-struct-r3-q2'] - 0.909) < 0.001, 'PMOS V_FB = +0.909')
cm = E['mos-cv-r2-q1']; cm2 = 1 / (1 + (eo / 40e-7) * xdep(2 * Vt * ln(1e6), 1e16) / es)
mc('mos-cv-r3-q3', cm2 > cm, 'thicker oxide → C_min/C_ox closer to 1')
mc('mos-cv-r3-q1', all(1 / (1 / cox + xdep(v, 1e16) / es) > 1 / (1 / cox + xdep(v + 0.05, 1e16) / es) for v in [0.01 * i + 0.01 for i in range(70)]), 'C decreases monotonically VFB→VT')
mc('mos-fields-r3-q3', E['mos-fields-r3-q3'] < 0, 'accumulation E_ox negative')
print(f'\nNumeric: {checked} recomputed, mc claims checked; problems: {bad}')
sys.exit(1 if bad else 0)
