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

## feedforward

Added in B5 for `feedforward`.

| symbol | meaning | aliases |
|---|---|---|
| \(F\) | feedforward gain | reference prefilter, or the gain that cancels a measured disturbance |
| \(P\) | plant | same \(P\) as in the feedback-loop area |
| \(P_0\) | nominal plant model used to build \(F\) | not the true plant when the two are compared |

## describing-function

Added in B5 for `gen-gain-phase`.

| symbol | meaning | aliases |
|---|---|---|
| \(N(a)\) | describing function at amplitude \(a\) | fundamental gain of a nonlinearity |
| \(a\) | amplitude of the sinusoid at the nonlinearity | |
| \(M\) | relay level or saturation limit | |
| \(-1/N(a)\) | describing-function critical point | intersection with \(G(j\omega)\) predicts a limit cycle |

## linearization

Added in B5 for `linearization`.

| symbol | meaning | aliases |
|---|---|---|
| \(x_e, u_e\) | equilibrium state and input, where \(f(x_e, u_e) = 0\) | |
| \(A = \partial f/\partial x\) | Jacobian in the state, evaluated at equilibrium | local \(A\), not a global system matrix |
| \(B = \partial f/\partial u\) | Jacobian in the input | |

## lti-stability

Added in B5 for `lti-stability`. The amplifier skill `stability` keeps its own margin language. This area is the eigenvalue test.

| symbol | meaning | aliases |
|---|---|---|
| asymptotic stability | every eigenvalue of \(A\) has a negative real part | internal stability for a minimal realization |
| BIBO stability | a bounded input produces a bounded output | transfer-function poles in the open left half-plane |
| Routh array | sign test on the coefficients of the characteristic polynomial | for \(s^3 + a s^2 + b s + c\), need \(a, b, c > 0\) and \(ab > c\) |

## performance-frequency

Added in B5 for `perf-specs-freq`. \(M_s\) is also listed under nyquist-stability.

| symbol | meaning | aliases |
|---|---|---|
| \(\omega_b\) | closed-loop bandwidth, where \(|T|\) is 3 dB below its low-frequency value | rad/s |
| \(\omega_c\) | gain crossover, where \(|L(j\omega_c)| = 1\) | |
| crossover sensitivity | \(\|S\| = 1/(2\sin(\mathrm{PM}/2))\) at the frequency where \(|L| = 1\) | not automatically the peak \(M_s\) |

## pid-implementation

Added in B5 for `pid-impl`. \(K_p, K_i, K_d, \tau_i, \tau_d\) stay in pid-control. \(T\) and \(z\) stay in discrete-time-systems.

| symbol | meaning | aliases |
|---|---|---|
| \(N\) | derivative filter ratio | \(\tau_f = \tau_d / N\), pole at \(-N/\tau_d\) |
| \(\tau_f\) | derivative filter time constant | |
| \(b, c\) | setpoint weights on the proportional and derivative terms | \(c = 0\) keeps derivative off the reference |
| \(2/T\) | Tustin frequency scale | \(s = (2/T)(z-1)/(z+1)\) |

## pid-tuning

Added in B5 for `pid-tuning`.

| symbol | meaning | aliases |
|---|---|---|
| \(K_u\) | ultimate gain, the proportional gain at the stability boundary | critical gain |
| \(T_u\) | ultimate period of that oscillation | |
| ultimate-gain PID | \(K_p = 0.6 K_u\), \(\tau_i = T_u/2\), \(\tau_d = T_u/8\) | |
| reaction curve | first-order-plus-delay fit, \(a = KL/\tau\) | PID uses \(K_p = 1.2/a\) |
| \(\lambda\) | desired closed-loop time constant in lambda tuning | \(K_p = \tau/(K(\lambda+L))\), \(\tau_i = \tau\) |

## realization-forms

Added in B5 for `realization`.

| symbol | meaning | aliases |
|---|---|---|
| controllable canonical form | for denominator \(s^2 + a_1 s + a_0\), the last row of \(A\) is \(-a_0, -a_1\) and \(B\) is a column whose only 1 is at the bottom | controller form, companion matrix |
| minimal realization | no cancelled hidden mode | state dimension equals the degree of \(G\) after cancellation |

## uncertainty

Added in B5 for `uncertainty`. \(P_0\) here is the nominal plant. In feedforward the same symbol is the model used to build \(F\).

| symbol | meaning | aliases |
|---|---|---|
| \(W_a\) | additive weight, \(\|P - P_0\| \le \|W_a\|\) | |
| \(W_m\) | multiplicative weight, \(\|P - P_0\|/\|P_0\| \le \|W_m\|\) | relative uncertainty |
| \(\Delta\) | normalized unknown with \(\|\Delta\| \le 1\) | |

## windup

Added in B5 for `windup`.

| symbol | meaning | aliases |
|---|---|---|
| \(u_{\mathrm{sat}}\) | command after the actuator limit | saturated input |
| \(T_t\) | back-calculation tracking time | unwind rate \((u_{\mathrm{sat}} - u)/T_t\) added to the integrator |

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
| \(\lVert A \rVert\) | matrix norm induced by a vector norm | \(\max_{\lVert x \rVert = 1} \lVert Ax \rVert\) |
| \(\lVert A \rVert_1\) | induced 1-norm | maximum absolute column sum |
| \(\lVert A \rVert_\infty\) | induced infinity-norm | maximum absolute row sum |
| \(\lVert A \rVert_2\) | induced 2-norm | largest singular value, \(\sigma_{\max}(A)\) |
| \(\lVert A \rVert_F\) | Frobenius norm | \(\sqrt{\sum_{ij} a_{ij}^2} = \sqrt{\sum_i \sigma_i^2}\) |
| \(\lVert A \rVert_{S_p}\) | Schatten \(p\)-norm | \((\sum_i \sigma_i^p)^{1/p}\); \(p=1\) nuclear, \(p=\infty\) spectral |
| \(B(x, r)\) | open ball | \(\{y : \lVert y - x \rVert < r\}\) |
| \(\overline{B}(x, r)\) | closed ball | the same inequality with \(\le\) |
| \(\mathrm{lev}(f, a)\) | sublevel set | \(\{x : f(x) \le a\}\) |
| \(\mathrm{con}(f, a)\) | contour set | \(\{x : f(x) = a\}\) |
| \(f'(x; d)\) | directional derivative | one-sided limit of \([f(x+td)-f(x)]/t\) as \(t \downarrow 0\). Added in NB3 |
| \(\nabla f(x)\) | gradient, a column of partial derivatives | \(\partial f/\partial x\). The Jacobian of a scalar \(f\) is the row \(\nabla f(x)^T\). Added in NB3 |
| \(H_f(x)\), \(\nabla^2 f(x)\) | Hessian of second partials | symmetric when the second partials are continuous. Added in NB3 |
| \(J_F(x)\) | Jacobian of a map \(F\) | rows are gradients of the components; shape is outputs by inputs. Added in NB3 |
| \(o(\lVert h \rVert)\) | little-o remainder | the remainder divided by \(\lVert h \rVert\) tends to 0. Added in NB3 |
| \(T_1\), \(T_2\) | first- and second-order Taylor models | \(T_1\) uses \(\nabla f\); \(T_2\) adds \(\tfrac12 h^T H_f h\). Added in NB3 |
| convex \(f\) | chord inequality | \(f((1-t)x+ty)\le (1-t)f(x)+tf(y)\) for \(t\in[0,1]\). Strict when the inequality is strict for \(t\in(0,1)\) and \(x\ne y\). Added in NB4 |
| first-order convexity | tangent underestimator | \(f(y)\ge f(x)+\nabla f(x)^T(y-x)\). Added in NB4 |
| second-order convexity | Hessian test on an open convex set | \(H_f(x)\) positive semidefinite at every point. Added in NB4 |
| \(\delta_+ f\) | forward difference | \([f(x+h)-f(x)]/h\), truncation \(O(h)\). Added in NB4 |
| \(\delta_c f\) | central difference | \([f(x+h)-f(x-h)]/(2h)\), truncation \(O(h^2)\). Added in NB4 |
| \(\varepsilon_{\mathrm{mach}}\) | unit roundoff | round-off of a difference quotient grows like \(\varepsilon_{\mathrm{mach}}/h\). Added in NB4 |
| computational graph | elementary operations as nodes | values computed in topological order. Added in NB4 |
| \(\dot v\) | forward-mode tangent of a node | directional derivative of that node. Added in NB4 |
| \(\bar v\) | reverse-mode adjoint of a node | partial derivative of the scalar output with respect to that node. Added in NB4 |
| \(H_f(x)\, d\) | Hessian-vector product | forward-over-reverse, or reverse-over-forward with \(d\) held fixed. Added in NB4 |
| \(\mathcal{X}\) | feasible set | a subset of \(\mathbb{R}^n\). Added in NB5 |
| \(p^\star\) | optimal value | \(\inf_{x\in\mathcal{X}} f(x)\). Finite values need not be attained. Added in NB5 |
| \(x^\star\), \(\operatorname{argmin}\) | a minimizer, and the set of them | \(f(x^\star)=p^\star\) with \(x^\star\in\mathcal{X}\). Added in NB5 |
| local minimizer | \(f(x^\star)\le f(x)\) for feasible \(x\) in some ball about \(x^\star\) | strict when the inequality is strict for every other such point. Added in NB5 |
| global minimizer | the same inequality for every feasible \(x\) | strict when no other feasible point ties the value. Added in NB5 |
| stationary point | \(\nabla f(x)=0\) | Fermat: an interior local minimizer of a differentiable \(f\) is stationary. Added in NB5 |
| second-order necessary | \(H_f(x^\star)\) positive semidefinite at an interior local minimizer | not sufficient. Added in NB5 |
| second-order sufficient | \(\nabla f(x^\star)=0\) and \(H_f(x^\star)\) positive definite | strict local minimizer. A zero eigenvalue is inconclusive. Added in NB5 |
| coercive | \(f(x)\to +\infty\) as \(\lVert x\rVert\to\infty\) | a continuous coercive function on a nonempty closed set attains a minimum. Added in NB5 |
| LP | linear program | affine objective and affine constraints. Added in NB5 |
| QP | quadratic program | quadratic objective and affine constraints. Convex when the Hessian is positive semidefinite. Added in NB5 |
| quadratic objective | \(\tfrac12 x^T A x + b^T x + c\) with \(A\) symmetric | gradient \(Ax+b\). Unique minimizer \(x=-A^{-1}b\) when \(A\) is positive definite. This \(A\) is not the LQR state matrix, and \(b\) is not a control vector. Added in NB5 |
| standard form | minimize \(c^T x\) subject to \(Ax=b\), \(x\ge 0\) | a maximization is rewritten by minimizing \(-c^T x\). Added in NB6 |
| slack | nonnegative \(s\) with \(a^T x + s = \beta\) | replaces \(a^T x \le \beta\). Added in NB6 |
| surplus | nonnegative \(s\) with \(a^T x - s = \beta\) | replaces \(a^T x \ge \beta\). Added in NB6 |
| free split | \(x = x^+ - x^-\) with both parts nonnegative | replaces a variable that may be negative. An absolute value \(\lvert x\rvert\) becomes \(x^+ + x^-\) together with that split. Added in NB6 |
| basis \(B\) | an invertible set of \(m\) columns of \(A\) | the other columns are nonbasic. Added in NB6 |
| basic solution | \(x_B = B^{-1}b\), \(x_N = 0\) | a basic feasible solution when \(x_B \ge 0\). Added in NB6 |
| reduced cost \(\bar{c}_j\) | \(c_j - c_B^T B^{-1} A_j\) | for minimization, a negative value means the objective falls as that nonbasic variable increases. Added in NB6 |
| ratio \(\theta\) | \(\min_i\{\bar{b}_i/\bar{a}_{ij}:\bar{a}_{ij}>0\}\) | longest step that keeps the basic variables nonnegative. No positive entry means an unbounded ray. Added in NB6 |
| phase I | minimize the sum of artificial variables on \(Ax+a=b\), \(x\ge 0\), \(a\ge 0\), after making \(b\ge 0\) | optimal value 0 if and only if the original standard-form system is feasible. Added in NB6 |
| \(L(x,\lambda,\nu)\) | Lagrangian | \(f(x)+\lambda^T h(x)+\nu^T g(x)\) for equalities \(h(x)=0\) and inequalities \(g(x)\le 0\). Added in NB7 |
| dual function \(\theta(\lambda,\nu)\) | infimum of the Lagrangian over \(x\), multipliers held fixed | a dual-feasible value is a lower bound on the primal optimal value. Added in NB7 |
| weak duality | \(\theta(\lambda,\nu)\le p^\star\) when \(\nu\ge 0\) and the infimum is finite | the dual maximizes \(\theta\). Added in NB7 |
| regularity | constraint gradients at the point are linearly independent | also called a constraint qualification for the multiplier rule. Added in NB7 |
| KKT | stationarity, primal feasibility, nonnegative inequality multipliers, and complementary slackness | equality multipliers stay free. Added in NB7 |
| complementary slackness | \(\nu_i g_i(x)=0\) | a positive multiplier forces the inequality to be active. Added in NB7 |
| LP dual | maximize \(b^T y\) subject to \(A^T y \le c\) | dual of minimize \(c^T x\) subject to \(Ax=b\), \(x\ge 0\). Added in NB7 |
| half-space projection | \(z-a(a^T z-\beta)/(a^T a)\) when \(a^T z>\beta\), and \(z\) itself when \(a^T z\le \beta\) | from the KKT system of \(\tfrac12\lVert x-z\rVert^2\). Added in NB7 |
| normal equations | \(A^T A x = A^T b\) | unique when \(A\) has full column rank. The solution is \((A^T A)^{-1} A^T b\). Added in NB7 |
| residual Jacobian \(J_r(x)\) | derivatives of the residual vector | one row per residual, one column per parameter. Added in NB7 |
| algebraic circle | \(x^2+y^2+cx+dy+e=0\) | linear in \((c,d,e)\). Center \((-c/2,-d/2)\), and \(r^2=c^2/4+d^2/4-e\). Added in NB7 |
| geometric margin | \(y_i(w^T x_i+b)/\lVert w\rVert\) for a correctly signed point | normalizing the smallest functional margin to 1 yields minimize \(\tfrac12\lVert w\rVert^2\) subject to \(y_i(w^T x_i+b)\ge 1\). Added in NB7 |
| descent direction | \(\nabla f(x)^T d < 0\) | a short enough step along \(d\) decreases \(f\). Added in NB8 |
| scaled descent direction | \(d = -D\nabla f(x)\) with \(D\) symmetric positive definite | steepest descent is \(D = I\). Added in NB8 |
| descent step | \(x^+ = x + t d\) with \(t > 0\) | direction, step length, and a stopping test are chosen separately. Added in NB8 |
| Q-linear rate | successive error ratios tend to \(\mu \in (0, 1)\) | superlinear when the ratio tends to 0; quadratic when the ratio against the squared error stays bounded; sublinear when the errors go to 0 but the ratio tends to 1. Added in NB8 |
| exact line-search step | \(t = -\nabla f(x)^T d / (d^T A d)\) | for \(f(x) = \tfrac12 x^T A x + b^T x\) with \(A\) symmetric positive definite and \(d \ne 0\). Added in NB8 |
| Armijo | \(f(x + t d) \le f(x) + c\, t\, \nabla f(x)^T d\) | \(c \in (0, 1)\). Backtracking replaces a rejected \(t\) by \(\beta t\), \(\beta \in (0, 1)\). Added in NB8 |
| gradient condition factor | \((( \kappa - 1)/(\kappa + 1))^2\) | \(\kappa = \lambda_{\max}(A)/\lambda_{\min}(A)\). This factor bounds the excess of steepest descent with exact line search. Added in NB8 |
| \(L\)-smooth | \(\lVert\nabla f(y) - \nabla f(x)\rVert \le L \lVert y - x\rVert\) | a bound on the induced 2-norm of the Hessian is such an \(L\). Added in NB8 |
| descent lemma | \(f(y) \le f(x) + \nabla f(x)^T(y - x) + \tfrac{L}{2}\lVert y - x\rVert^2\) | an upper bound from a Lipschitz gradient. Added in NB8 |
| sufficient decrease | \(f(x) - f(x - t\nabla f(x)) \ge t(1 - Lt/2)\lVert\nabla f(x)\rVert^2\) | for \(0 < t < 2/L\). The step \(t = 1/L\) gives the coefficient \(1/(2L)\). Added in NB8 |
| gradient-method rate | \(\min_{i < k}\lVert\nabla f(x_i)\rVert^2 \le 2L(f(x_0) - f^\star)/k\) | for the constant step \(t = 1/L\), when \(f\) is bounded below by \(f^\star\). Added in NB8 |

## loop-shaping

Added in B6 for `loop-shaping`. \(L\) is the loop transfer from the loop-transfer-function area. \(\alpha\) here is not a plant pole.

| symbol | meaning | aliases |
|---|---|---|
| lead | zero closer to the origin than the pole, both in the open left half-plane | phase is positive between the corners |
| lag | pole closer to the origin than the zero | high-frequency gain drops |
| \(\alpha\) | lead ratio, pole magnitude over zero magnitude, \(\alpha > 1\) | |
| \(\phi_m\) | peak lead, \(\arcsin((\alpha-1)/(\alpha+1))\) | at \(\omega_m = \sqrt{\|z\|\,\|p\|}\) |

## lyapunov

Added in B6 for `lyapunov`. \(P\) here is the certificate matrix, not the plant. \(Q\) is a chosen positive definite matrix, not a weight in a later regulator.

| symbol | meaning | aliases |
|---|---|---|
| \(V(x)\) | Lyapunov function, positive definite, with \(V(0) = 0\) | |
| \(\dot{V}\) | derivative of \(V\) along the differential equation | negative definite for asymptotic stability |
| \(A^T P + PA = -Q\) | Lyapunov equation for \(\dot{x} = Ax\) | \(P \succ 0\) and \(Q \succ 0\) certify asymptotic stability |

## reachability

Added in B6 for `reachability`. The same \([B\ AB\ \cdots]\) test is the controllability test for these continuous-time models.

| symbol | meaning | aliases |
|---|---|---|
| \(\mathcal{C}\) | controllability matrix \([B\ AB\ \cdots\ A^{n-1}B]\) | reachability matrix |
| reachable | \(\mathrm{rank}\,\mathcal{C} = n\) | controllable |

## observability

Added in B6 for `observability`. Dual of reachability: \((A, C)\) is observable exactly when \((A^T, C^T)\) is reachable.

| symbol | meaning | aliases |
|---|---|---|
| \(\mathcal{O}\) | observability matrix with rows \(C, CA, \ldots, CA^{n-1}\) | |
| observable | \(\mathrm{rank}\,\mathcal{O} = n\) | |

## robust-stability

Added in B6 for `robust-stability`. \(W_m\), \(P_0\), and \(\Delta\) stay as in the uncertainty area. \(T = L/(1+L)\).

| symbol | meaning | aliases |
|---|---|---|
| \(\|T W_m\|_\infty < 1\) | sufficient robust stability for \(P = P_0(1 + W_m \Delta)\) with \(\|\Delta\|_\infty \le 1\), nominal loop stable | small-gain test on the complementary sensitivity |

## root-locus

Added in B6 for `root-locus`. Positive gain means \(1 + K G(s) = 0\) with \(K \ge 0\).

| symbol | meaning | aliases |
|---|---|---|
| \(n - m\) | excess of poles over zeros | number of asymptotes |
| centroid | \((\sum p - \sum z)/(n-m)\) | |
| asymptote angles | \((2q+1)180^\circ/(n-m)\) for \(K > 0\) | even multiples of \(180^\circ/(n-m)\) are the negative-gain locus |
| real-axis rule | a real test point is on the positive-gain locus when an odd number of real poles and zeros lie to its right | |

## sys-id

Added in B6 for `sys-id`. The data matrix is \(\Phi\), not the state matrix \(A\). The optimization area's least-squares \(A\) is a different object.

| symbol | meaning | aliases |
|---|---|---|
| \(K, \tau\) | DC gain and time constant of a first-order fit | read from a held step only after the record settles |
| \(\theta\) | parameter vector in a model that is linear in \(\theta\) | |
| \(\Phi\) | regressor matrix, one row per record | normal equations \(\Phi^T \Phi \theta = \Phi^T y\) |

## time-delay

Added in B6 for `time-delay`. \(T_d\) is a pure delay. The discrete-time area uses \(T\) for the sample period, and the feedback-loop area uses \(d\) for a disturbance. Do not reuse those letters for the delay.

| symbol | meaning | aliases |
|---|---|---|
| \(e^{-s T_d}\) | transfer function of a delay of \(T_d\) seconds | magnitude 1, phase \(-\omega T_d\) radians |
| Padé, first order | \((1 - s T_d/2)/(1 + s T_d/2)\) | right-half-plane zero at \(2/T_d\), pole at \(-2/T_d\) |
| delay margin | \(\mathrm{PM}/\omega_c\) with the margin in radians | seconds of delay until the phase margin is spent |

## state-feedback

Added in B7 for `state-feedback`. \(K\) is the state-feedback row. It is not the proportional gain \(K_p\), and it is not the DC gain \(K\) of a first-order fit in the sys-id area. The sentence says state feedback.

| symbol | meaning | aliases |
|---|---|---|
| \(u = -Kx\) | state feedback | |
| \(A - BK\) | closed-loop state matrix | |
| Ackermann | the single-input formula for \(K\) from the desired characteristic polynomial, when the pair is reachable | |

## observer

Added in B7 for `observer`. \(L\) here is the observer gain, not the loop transfer. The estimation error is \(\tilde{x} = x - \hat{x}\), not the tracking error \(e = r - y\).

| symbol | meaning | aliases |
|---|---|---|
| \(\hat{x}\) | state estimate | |
| \(L\) | observer gain | |
| \(\tilde{x}\) | estimation error \(x - \hat{x}\) | |
| \(A - LC\) | estimation-error matrix | \(\dot{\tilde{x}} = (A - LC)\tilde{x}\) when the model matches |

## fundamental-limitations

Added in B7 for `fund-limits`. \(S\) and \(T\) stay as in the loop-transfer-function area. \(z\) here is a right-half-plane zero, not the discrete-time variable.

| symbol | meaning | aliases |
|---|---|---|
| Bode integral | \(\int_0^{\infty} \ln|S(j\omega)|\,d\omega = \pi \sum \mathrm{Re}(p_k)\) over the right-half-plane poles of a loop that rolls off at least as \(1/\omega^2\). The sum is empty, and the integral is 0, when the open loop is stable. | waterbed |
| interpolation | an uncancelled right-half-plane zero \(z\) of the loop satisfies \(S(z) = 1\) | |

## robust-performance

Added in B7 for `robust-perf`. \(W_m\) stays as in the uncertainty area. \(S\) and \(T\) stay as in the loop-transfer-function area.

| symbol | meaning | aliases |
|---|---|---|
| \(W_s\) | weight on sensitivity in a performance spec | |
| robust performance | \(\||W_s S| + |W_m T|\|_\infty < 1\) for multiplicative uncertainty | stricter than nominal performance and stricter than robust stability |

## adaptive-control

Added in B7 for `adaptive`. \(\gamma\) is the adaptation gain, not a lead ratio. \(\varepsilon\) is the prediction error, not the tracking error \(e = r - y\). \(\hat{\theta}\) is a parameter estimate, not the state estimate \(\hat{x}\).

| symbol | meaning | aliases |
|---|---|---|
| \(\hat{\theta}\) | parameter estimate used inside the controller | |
| \(\gamma\) | adaptation gain | |
| \(\varepsilon\) | prediction error \(y - \hat{y}\) | |
| certainty equivalence | build the control law from \(\hat{\theta}\) as if the estimate were the true parameter | |

## gaussian-vectors

Added in B8 for `gaussian-random-vectors`. \(x\) here is a random vector. In state-space, \(x\) is the state. A sentence that uses both says which.

| symbol | meaning | aliases |
|---|---|---|
| \(\mu\) | mean \(\mathbb{E}[x]\) | |
| \(P\) | covariance \(\mathbb{E}[(x-\mu)(x-\mu)^T]\) | this \(P\) is not the plant and not the Lyapunov certificate |
| \(A P A^T\) | covariance of \(A x\) when \(A\) is deterministic | a constant shift of \(x\) does not change \(P\) |

## kalman-filter

Added in B8 for `kalman`. The model is discrete. \(L_k\) is the filter gain. It is not the observer polynomial gain, and it is not the loop transfer. \(Q\) and \(R\) are noise covariances, not the regulator weights in the LQR area. \(P_{k|k-1}\) is the predicted error covariance.

| symbol | meaning | aliases |
|---|---|---|
| \(x_{k+1} = A x_k + w_k\) | state model | \(w_k\) is process noise |
| \(y_k = C x_k + v_k\) | measurement model | \(v_k\) is measurement noise |
| \(Q, R\) | covariances of \(w_k\) and \(v_k\) | |
| predict | \(\hat{x}_{k|k-1} = A \hat{x}_{k-1|k-1}\), \(P_{k|k-1} = A P_{k-1|k-1} A^T + Q\) | a known input is added to the state predict and does not enter \(P\) |
| \(L_k\) | filter gain \(P_{k|k-1} C^T (C P_{k|k-1} C^T + R)^{-1}\) | alias \(K_k\). Not the state-feedback row |
| update | \(\hat{x}_{k|k} = \hat{x}_{k|k-1} + L_k (y_k - C \hat{x}_{k|k-1})\), \(P_{k|k} = (I - L_k C) P_{k|k-1}\) | the simplified covariance update uses this \(L_k\) |

## lqr

Added in B8 for `lqr`. \(Q\) and \(R\) are cost weights. They are not the noise covariances in the Kalman area. \(P\) is the solution of the algebraic Riccati equation, not the Lyapunov certificate, though the two equations share a shape. \(K\) is the state-feedback row from that \(P\).

| symbol | meaning | aliases |
|---|---|---|
| \(\int_0^{\infty} (x^T Q x + u^T R u)\, dt\) | infinite-horizon quadratic cost | |
| \(A^T P + P A - P B R^{-1} B^T P + Q = 0\) | algebraic Riccati equation | |
| \(K = R^{-1} B^T P\) | optimal gain | |

## mpc

Added in B8 for `mpc`. \(N\) is the horizon in samples. \(T\) in this area is the sample period only when a sentence is computing a look-ahead time; the discrete-time area also uses \(T\).

| symbol | meaning | aliases |
|---|---|---|
| \(N\) | number of steps in the horizon | |
| receding horizon | apply the first computed input, then build the problem again at the next sample | |
| \(u_{\min}, u_{\max}\) | bounds on the command inside that finite problem | |

## separation

Added in B8 for `separation`. \(K\) and \(L\) keep the meanings from state-feedback and observer.

| symbol | meaning | aliases |
|---|---|---|
| \(u = -K \hat{x}\) | output feedback through an estimate | |
| eigenvalue split | the joint eigenvalues are those of \(A-BK\) and those of \(A-LC\), when the observer model matches the plant | separation |

## integral-action

Added in B8 for `integral-action`. \(\xi\) is the integrator state. It is not a schedule variable and not a damping ratio.

| symbol | meaning | aliases |
|---|---|---|
| \(\dot{\xi} = r - y\) | integrator on the tracking error | |
| \(u = -K x + k_i \xi\) | state feedback plus the integrator gain | \(k_i > 0\) raises the command when \(\xi\) has accumulated a positive error on a positive-gain plant |

## feedback-linearization

Added in B8 for `fb-linearization`. This is not the Jacobian in the linearization area.

| symbol | meaning | aliases |
|---|---|---|
| \(\dot{x} = f(x) + g(x) u\) | control-affine model | |
| \(u = (v - f(x))/g(x)\) | input that leaves \(\dot{x} = v\), where \(g(x) \neq 0\) | |
| \(v\) | new input, designed as a linear state feedback | |

## gain-scheduling

Added in B8 for `gain-scheduling`. \(\rho\) is the measured schedule. It is not the adaptation gain \(\gamma\).

| symbol | meaning | aliases |
|---|---|---|
| \(\rho\) | measured schedule variable | |
| \(K(\rho)\) | controller gain interpolated from designs at fixed values of \(\rho\) | frozen at one \(\rho\), this is one linear controller |

## two-degree-of-freedom

Added in B8 for `gen-controller`. \(F\) is the feedforward gain from the reference. The feedforward area uses the same letter for a prefilter.

| symbol | meaning | aliases |
|---|---|---|
| \(u = F r - K \hat{x}\) | command with a reference term and an estimate term | two degrees of freedom |
| \(F\) | gain chosen so a constant reference is matched in steady state | does not move the eigenvalues of \(A-BK\) |
