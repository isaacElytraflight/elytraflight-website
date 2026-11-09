# Notation registry

Areas are tags, not owners. A symbol can mean different things in different areas. The sentence has to say which area it is in. B1 adds the rows marked "added in B1".

## signals

| symbol | meaning | aliases |
|---|---|---|
| \(t\) | time, seconds | |
| \(s\) | Laplace variable | |
| \(\omega\) | radian frequency | not hertz, unless the sentence says Hz |
| \(f(t), F(s)\) | a signal and its transform | capital for the transform |

## feedback-loop

Added in B1, aligned with the control skills. The amplifier skill `fb-intro` already uses a different set; both stay.

| symbol | meaning | aliases |
|---|---|---|
| \(r\) | reference | `fb-intro` calls the input \(x\) |
| \(y\) | output | |
| \(u\) | command into the plant | |
| \(e = r - y\) | error, negative feedback | |
| \(d\) | disturbance, at the actuator or the output | |
| \(n\) | sensor noise | added in B1 |
| \(K_c\) | proportional gain | added in B1 |
| \(L\) | loop gain, product of the forward gains | alias \(T = af\) in `fb-intro` |
| \(P\) | plant gain | alias \(a\) in `fb-intro` |
| \(A\) | not used for loop gain | `fb-intro` uses \(A = a/(1+af)\) for closed-loop gain. Do not reuse that \(A\) in a control skill. |

## laplace

Added in B1.

| symbol | meaning | aliases |
|---|---|---|
| \(\mathcal{L}\) | Laplace transform | |
| \(F(s)\) | transform of \(f\) | |
| final value | \(\lim_{t\to\infty} f(t) = \lim_{s\to 0} sF(s)\), only when every pole of \(sF(s)\) is in the open left half-plane | |
| initial value | \(\lim_{t\to 0^+} f(t) = \lim_{s\to\infty} sF(s)\) when that limit exists | |

## linear-algebra

Added in B1. Domain-neutral: no plant in the practice rounds.

| symbol | meaning | aliases |
|---|---|---|
| \(A, B, C\) | matrices | this \(A\) is not tank area and not the closed-loop gain |
| \(\lambda\) | eigenvalue | |
| \(\det\), trace | determinant and trace | characteristic polynomial \(\lambda^2 - (\mathrm{tr})\lambda + \det\) |
| rank, nullity | independent columns, and dimension of the null space | rank + nullity = number of columns |

## frequency-response

| symbol | meaning | aliases |
|---|---|---|
| phase | degrees, unless the sentence says radians | |
| slope | dB per decade | \(-20n\) dB/decade sits near \(-90n\) degrees on a minimum-phase sketch |
| minimum phase | every zero in the open left half-plane, and no time delay | added in B1 |

## physical-models

Added in B1 for `ode-model`.

| symbol | meaning | aliases |
|---|---|---|
| \(m, b, k, F\) | mass, viscous coefficient, spring, force | |
| \(J, \tau\) | inertia and torque | \(\tau\) is also a time constant when the sentence is about a first-order lag. Do not use both meanings in one sentence. |
| \(R, L, C, v, i\) | resistance, inductance, capacitance, voltage, current | |
| \(A, h, q, R\) | tank surface area, height, volume flow, hydraulic resistance | this \(A\) is not a matrix; this \(R\) is not ohms. The sentence names the tank. |
| time constant | \(m/b\), \(J/b\), \(L/R\), \(RC\), \(AR\) | not \(R/L\) or \(R/C\) |

## state-space

Added in B2 for `state-space-model`, extended in B3 for `ss-solution` and `equilibria`.

| symbol | meaning | aliases |
|---|---|---|
| \(x\) | state vector | |
| \(A, B, C, D\) | state-space matrices | this \(A\) is not tank area; context tells which |
| \(\dot{x} = Ax + Bu\) | state equation | |
| \(y = Cx + Du\) | output equation | |
| \(\lambda\) | eigenvalue of \(A\) | mode |
| \(e^{At}\) | matrix exponential, the free-response operator | added in B3 |
| \(x_e\) | equilibrium point, where \(\dot{x} = 0\) | added in B3 |

## second-order-systems

Added in B3 for `second-order-sys`.

| symbol | meaning | aliases |
|---|---|---|
| \(\omega_n\) | natural frequency, rad/s | undamped natural frequency |
| \(\zeta\) | damping ratio | |
| poles | \(-\zeta\omega_n \pm \omega_n\sqrt{\zeta^2 - 1}\) | when \(\zeta < 1\), a conjugate pair |
| \(M_p\) | percent overshoot | peak overshoot |
| \(t_p\) | time to peak | |
| \(t_s\) | settling time, usually 2% or 5% of steady value | |

## loop-transfer-function

Added in B3 for `loop-tf`.

| symbol | meaning | aliases |
|---|---|---|
| \(L(s)\) | loop transfer function, product around the loop | loop gain when evaluated |
| \(T(s)\) | complementary sensitivity \(L/(1+L)\) | equals closed-loop \(G/(1+GH)\) only for unity feedback |
| \(S(s)\) | sensitivity \(1/(1+L)\) | |
| \(1 + L(s)\) | return difference | |

Note: The identity \(T + S = 1\) holds for \(T = L/(1+L)\) and \(S = 1/(1+L)\). For non-unity feedback (\(H \ne 1\)), the closed-loop gain \(G/(1+GH)\) differs from \(L/(1+L)\).

## pid-control

Added in B4 for `pid`.

| symbol | meaning | aliases |
|---|---|---|
| \(K_p\) | proportional gain | |
| \(K_i\) | integral gain | |
| \(K_d\) | derivative gain | |
| \(\tau_i = K_p/K_i\) | integral time constant | |
| \(\tau_d = K_d/K_p\) | derivative time constant | |

## nyquist-stability

Added in B4 for `nyquist`.

| symbol | meaning | aliases |
|---|---|---|
| GM | gain margin, factor by which loop gain can increase | in dB: \(20\log_{10}(\text{GM})\) |
| PM | phase margin, degrees from \(-180°\) at \(|L|=1\) | |
| \(M_s\) | peak sensitivity \(\max|S(j\omega)|\) | reciprocal of closest approach to \(-1\) |
| \(-1\) | critical point on the Nyquist plot | encirclement count determines stability |

## discrete-time-systems

Added in B4 for `discrete-time`.

| symbol | meaning | aliases |
|---|---|---|
| \(z\) | z-transform variable | \(z = e^{sT}\) |
| \(T\) | sample period, seconds | sample time |
| \(f_N = 1/(2T)\) | Nyquist frequency, Hz | folding frequency |
| \(z^{-1}\) | one-sample delay | unit delay |
| unit circle | stability boundary in the z-plane | \(|z| = 1\) |

## optimization

Added for the nonlinear optimization skills. In this area \(x\) is a decision vector, not a state, and \(A\) is a data matrix, not a state matrix. A sentence that uses both areas names which one it means.

| symbol | meaning | aliases |
|---|---|---|
| \(x \in \mathbb{R}^n\) | decision vector | |
| \(f(x)\) | objective | |
| \(A\) | real matrix, taken symmetric when it is diagonalized by an orthogonal matrix | not a state matrix |
| \(\lambda\) | eigenvalue of a symmetric matrix | |
| \(\sigma\) | singular value | \(\sigma_i = \sqrt{\lambda_i(A^T A)}\) |
| \(\lVert x \rVert_p\) | vector \(\ell_p\) norm | \(p = 1, 2, \infty\) |
| \(\langle x, y \rangle\) | inner product | \(x^T y\) for the standard dot product |
| \(R(x)\) | Rayleigh quotient \(x^T A x / x^T x\) | |
| \(U, \Sigma, V\) | singular-value factors | \(A = U \Sigma V^T\) |
| PSD, PD | positive semidefinite, positive definite | \(x^T A x \ge 0\), or \(> 0\) for every \(x \ne 0\) |
