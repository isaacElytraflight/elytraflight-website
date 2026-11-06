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
