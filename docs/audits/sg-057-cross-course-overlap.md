# SG-057 cross-course overlap audit

Audit date: 2026-11-13. Analysis and proposals only. This file does not change the skill graph, any bank, any explainer, or any app file. A later item would do each restructure, after Isaac picks which rows to build.

Overlap that already shares one skill id is a showcase. Those skills stay. This audit looks for the same concept under two or more ids, or for one shared id whose title and questions are still written in a single course's language.

Kalman is out of scope. SG-056 already made `kalman` the neutral core, with `gaussian-random-vectors` as its covariance prerequisite, `kalman-optimal-observer` as the ME 132 application, and `kalman-recursive-least-squares` plus `extended-kalman-filter` as the NLO applications.

## What was read

Source of truth:

- `skilltree/ee105_skills_draft.json`: id, display name, `owns`, summary, prerequisites. 270 skills.
- `skilltree/collections.json`: which box holds each skill.
- Explainers and question prompts in `skilltree/explainers/` and `skilltree/bank/` for the ids named below.
- `docs/dedupe-decisions.json`, the ME 132 batch plan, and the NLO batch plan, including the SG-056 note and the "kept separate" list.

Hashed files under `public/skilltree/` were not read.

Course boxes:

| Box | Skills |
| --- | --- |
| EE 105 (`ee105-ucb`) | 112 |
| ME 132 (`me132`) | 58 |
| NLO (`nlo-tugraz`) | 101 |
| Feedback Systems (`am08`) | 72 |

## Already one skill

Thirteen skills already have one id in EE 105, ME 132, and Feedback Systems:

`lti-def`, `cx-exp`, `sinusoid-resp`, `impulse-conv`, `step-resp`, `freq-char`, `tf`, `pole-zero`, `bode`, `fb-intro`, `loop-gain`, `fb-errors`, `stability`.

`gaussian-random-vectors` and `kalman` are in ME 132, NLO, and Feedback Systems. `lin-algebra-review` is in NLO and Feedback Systems. Almost every other ME 132 skill is the same id in Feedback Systems. The ME-only exception is `kalman-optimal-observer`. Feedback Systems also holds control skills that ME 132 does not list (`pid-impl`, `discrete-time`, `min-phase`, `gen-gain-phase`, `robust-perf`, `feedforward`, `perf-specs-freq`, `loop-shaping`, `fund-limits`, `lqr`, `lyapunov`, `limit-cycles`, `gen-controller`, `app-examples`, `lin-algebra-review`).

These pairs are already a core plus a course application. No new core:

| Core | Application | What the application adds |
| --- | --- | --- |
| `lti-def` | `lti-circuits`, and the differential-pair half-circuit skill `half-circuit` | Superposition on a circuit |
| `bode` | `bode-circuits` | Poles of a filter from its element values |
| `freq-char` | `freq-resp-circuits`, `freq-resp-lti` | A circuit transfer function, or \(G(j\omega)\) from a state-space model |
| `sinusoid-resp` | `phasors`, `direct-h` | Impedance of R, L, and C, then \(H(j\omega)\) by a divider |

`lti-mech` is not in that table. It also teaches natural frequency and damping, which is candidate 2.

A core's prerequisites have to be neutral. A learner in one course must not be sent through another course's domain skills. Every proposal below follows that rule. New ids are names for a later item. Nothing in this file creates them.

## Candidates

### 1. First-order linear response

**Existing ids:** `step-resp` (EE 105, ME 132, Feedback Systems), `first-order-sys` (ME 132, Feedback Systems), `rc-lpf` (EE 105), `lti-circuits` (EE 105).

**Why they overlap.** All four teach the same exponential. `first-order-sys` is \(\tau \dot y + y = Ku\), the step \(Ku(1-e^{-t/\tau})\), and the fact that one time constant covers about 63% of the gap. Its explainer names a capacitor voltage behind a resistor as the same equation. `rc-lpf` is that equation with \(\tau = RC\), plus the same 63% and \(5\tau\) rules. Eight of the twelve `step-resp` questions practice that first-order formula (the 63% point, a 90% rise time, a pulse, and a preview that compares two time constants). The impulse-to-step question can stay. `lti-circuits` opens by solving the same RC step and pulse. `first-order-sys` requires `laplace` and `step-resp`. `rc-lpf` requires only `step-resp`, so the two solution skills never meet.

**Neutral core.** Keep `first-order-sys`. Name: First-order systems. Scope: one real pole, a time constant, a DC gain, and the exponential step and free response. Add the skill to the EE 105 box.

**Prerequisites.** `step-resp` only. Drop `laplace`. Laplace is a ME 132 and Feedback Systems skill, and the RC application cannot require it.

**Course-specific skills.**

- `rc-lpf` (EE 105): \(\tau = RC\), the cutoff, and the resistance the capacitor actually sees. Prerequisite: the core.
- `step-resp` stays shared and narrows to the step as the running integral of the impulse, and a pulse as a difference of steps. The \(\tau\) drills move to the core.
- `lti-circuits` (EE 105) keeps superposition, convolution, and loading on circuit equations. It stops re-deriving the exponential. Prerequisites stay `impulse-conv`, `step-resp`, and `rc-lpf`.

`ode-model` stays the skill that writes an element law (capacitor, inductor, mass, tank). It should not also be where the exponential is solved.

**Confidence.** High.

### 2. Second-order poles: natural frequency and damping

**Existing ids:** `second-order-sys` (ME 132, Feedback Systems), `rlc` (EE 105), `lti-mech` (ME 132, Feedback Systems), `step-specs` (ME 132, Feedback Systems), `pole-zero` (EE 105, ME 132, Feedback Systems).

**Why they overlap.** `second-order-sys` is \(\omega_n\), \(\zeta\), the three damping cases, and the pole locations \(-\zeta\omega_n \pm j\omega_d\). Its key equations also give percent overshoot, time to peak, and the 2% settling time. `rlc` teaches the same standard form and writes \(\zeta = 1/(2Q)\) next to \(\omega_0 = 1/\sqrt{LC}\). High \(Q\) rings, \(Q = 1/2\) is critical damping. `lti-mech` maps \(m\), \(b\), and \(k\) onto the same \(\omega_n\) and \(\zeta\). `step-specs` computes the same overshoot and settling numbers from the same two parameters. Two `pole-zero` questions compute \(\omega_n = |p|\) and \(\zeta\) for a quadratic. `second-order-sys` requires `first-order-sys` and `pole-zero`. `rlc` requires `direct-h` and `pole-zero`. They never meet.

**Neutral core.** Keep `second-order-sys`. Name: Second-order systems. Scope: natural frequency, damping ratio, and underdamped, critically damped, and overdamped poles. The overshoot and settling formulas move to `step-specs`. Add the skill to the EE 105 box.

**Prerequisites.** `pole-zero` only. Drop `first-order-sys`, so the core does not inherit `laplace`. `pole-zero` is already in EE 105, ME 132, and Feedback Systems.

**Course-specific skills.**

- `rlc` (EE 105): series resonance, \(Q\), and \(\zeta = 1/(2Q)\). Prerequisites: the core and `direct-h`.
- `lti-mech` (ME 132, Feedback Systems): \(m\), \(b\), \(k\), and the rotational analog. Prerequisites: the core and `ode-model`.
- `step-specs` (ME 132, Feedback Systems): rise time, percent overshoot, settling time, and steady-state error. Prerequisite stays the core.
- `pole-zero` keeps what a pole and a zero are, and the term \(e^{pt}\). The drills that turn a quadratic into \(\zeta\) and \(\omega_n\) move to the core.

**Confidence.** High.

### 3. Eigenvalues and diagonalization

**Existing ids:** `lin-algebra-review` (NLO, Feedback Systems), `eig-modes` (ME 132, Feedback Systems), `spectral-decomposition` (NLO).

**Why they overlap.** `lin-algebra-review` drills rank, null space, the determinant, and the eigenvalues of a \(2\times 2\). Its summary still says the eigenvalues are "as used in control," and the skill is not in the ME 132 box. `eig-modes` teaches eigenvalues again as the modes of \(\dot x = Ax\), from `ss-solution` only, with no linear-algebra prerequisite. `spectral-decomposition` requires the review and then asks for the larger eigenvalue of another \(2\times 2\) before it reaches the symmetric fact \(A = UDU^T\). The algebra fact is one concept. Modes, and the orthonormal form for a symmetric matrix, are the course views.

**Neutral core.** New id `eigenvalues-diagonalization`. Name: Eigenvalues and diagonalization. Scope: \(Av = \lambda v\), the characteristic polynomial, and a change of basis when a full set of eigenvectors exists.

**Prerequisites.** `lin-algebra-review`, after that skill is narrowed to rank, null space, determinant, and matrix-vector products, and after the control sentence is removed from its summary. Add `lin-algebra-review` to the ME 132 box. Reachability and observability already require it, and today an ME 132 learner meets it only because it sits in Feedback Systems.

**Course-specific skills.**

- `eig-modes` (ME 132, Feedback Systems): a mode \(e^{\lambda t}v\), a time constant, a complex pair, and a Jordan block when diagonalization fails. Prerequisites: the core and `ss-solution`.
- `spectral-decomposition` (NLO): a real symmetric matrix, orthonormal eigenvectors, and \(A = UDU^T\). Prerequisite: the core.
- `rayleigh-quotient` and `power-method-eigenvector` stay downstream of `spectral-decomposition`.

**Confidence.** High.

### 4. Least squares

**Existing ids:** `linear-least-squares` (NLO), `least-squares-data-fitting` (NLO), `sys-id` (ME 132, Feedback Systems).

**Why they overlap.** `sys-id` says the fit is least squares and that the model is \(y = \Phi\theta\). One of its questions is the scalar fit of \(y = \theta u\) to three points, which is the normal equation for one unknown. `linear-least-squares` is those normal equations in matrix form. `least-squares-data-fitting` is the same fit for a line or a polynomial. The NLO skill requires `quadratic-function-minimization` and `singular-value-decomposition`, so a control learner cannot use it without the NLO optimality chain. `kalman-recursive-least-squares` is the recursive view and stays as SG-056 left it.

**Neutral core.** Keep `linear-least-squares`. Name: Linear least squares. Scope: minimize \(\lVert Ax - b\rVert^2\) and solve the normal equations when the columns are independent.

**Prerequisites.** `lin-algebra-review` only, after candidate 3 neutralizes that skill and adds it to ME 132. Drop `quadratic-function-minimization` and `singular-value-decomposition` from the core.

**Course-specific skills.**

- `sys-id` (ME 132, Feedback Systems): a DC gain from a settled step, a first-order time constant, a frequency-response fit, and a holdout residual. Prerequisites: the core, `first-order-sys`, and `freq-resp-lti`. The scalar normal-equation drill moves to the core.
- `least-squares-data-fitting` (NLO): a model that is linear in its parameters. Prerequisite stays the core.
- New NLO skill, proposed id `least-squares-quadratic`. Name: Least squares as a quadratic. Scope: derive the normal equations as the stationarity condition of a quadratic, and read the solution as a pseudoinverse. Prerequisites: the core, `quadratic-function-minimization`, and `singular-value-decomposition`.

**Confidence.** High.

### 5. Linear approximation at an operating point

**Existing ids:** `nl-cap`, `diode-ss`, `ss-model`, `bjt-ss` (all EE 105), `linearization` (ME 132, Feedback Systems), `taylor-approximation-multivariable` (NLO).

**Why they overlap.** Each one replaces a smooth map by its value and its first derivative at a chosen point, and each one warns that the model is local. `nl-cap` is \(C = dQ/dV\) at a bias. `diode-ss` is the diode conductance at a bias current. `ss-model` and `bjt-ss` turn that derivative into \(g_m\), \(r_o\), and the small-signal procedure. `linearization` is the Jacobian of \(\dot x = f(x, u)\) at an equilibrium. `taylor-approximation-multivariable` is the same first-order term plus the Hessian term. The NLO skill requires `hessian-matrix`, which sits behind the NLO derivative chain. EE 105 and ME 132 must not be sent through that chain. The four device skills should stay four skills: the shared piece is the derivative, and the rest is the device.

**Neutral core.** New id `local-linear-approximation`. Name: Linear approximation at an operating point. Scope: replace a smooth function by its value plus its derivative at a chosen point; the error is higher order and the model is local.

**Prerequisites.** None.

**Course-specific skills.**

- `nl-cap` (EE 105): small-signal capacitance. Prerequisites: the core and `mim-cap`.
- `diode-ss` (EE 105): \(r_d\) and diffusion capacitance. Prerequisites: the core, `diode-iv`, `junction-cap`, and `nl-cap`.
- `ss-model` (EE 105): the MOS small-signal procedure, \(g_m\), and \(r_o\). Prerequisites: the core, `gm`, and `ro`.
- `bjt-ss` (EE 105): the hybrid-pi model. Prerequisites: the core, `early`, and `ss-model`.
- `linearization` (ME 132, Feedback Systems): the matrices \(A\) and \(B\) at an equilibrium. Prerequisites: the core and `equilibria`. Keep `eig-modes` here if the skill still decides local stability from those eigenvalues. That prerequisite is on the application, not on the core.
- `taylor-approximation-multivariable` (NLO): the multivariable expansion through the Hessian. Prerequisites: the core and `hessian-matrix`.

`fb-linearization` stays separate. It cancels a known nonlinearity exactly. `gen-gain-phase` stays separate. A describing function averages over a sinusoid. It is not the derivative at a point.

**Confidence.** High.

### 6. Loop gain and the closed-loop formula

**Existing ids:** `fb-intro`, `loop-gain`, `fb-amp` (EE 105, and the first two also ME 132 and Feedback Systems), `loop-tf` (ME 132, Feedback Systems).

**Why they overlap.** The closed-loop formula "forward gain divided by one plus the loop gain" is practiced in `fb-intro`, `loop-gain`, `fb-amp`, and the opening questions of `loop-tf`. `loop-gain` and `fb-intro` write it as \(G/(1+Gf)\) and the ideal gain \(1/f\), which is the amplifier view, even though both skills sit in ME 132 and Feedback Systems. `fb-amp` computes that same \(T = Af\) from an op-amp and a resistor divider. `loop-tf` computes \(L\) as forward times return, then goes on to \(L = PC\) and the four closed-loop maps. The arithmetic is one concept. The resistor network, and the plant-controller product, are the course views.

**Neutral core.** Keep `loop-gain`. Name: Loop gain. Scope: the loop gain is the product around the loop, the closed-loop map is the forward gain over one plus that product, and a large loop gain makes the closed loop follow the feedback path.

**Prerequisites.** `fb-intro` and `tf`. Both are already in EE 105, ME 132, and Feedback Systems. The core's questions use a single symbol for the loop gain. The \(G\), \(f\), and \(1/f\) drills move to `fb-amp`. The \(L = PC\) drills stay in `loop-tf`.

**Course-specific skills.**

- `fb-intro` stays shared and narrows to the diagram: forward block, feedback block, summing junction, error signal, and the sign of the feedback. The closed-loop formula leaves this skill.
- `fb-amp` (EE 105): the feedback factor from the resistor network and the ideal closed-loop gain \(1/f\). Prerequisites stay `loop-gain` and `opamp-models`.
- `loop-tf` (ME 132, Feedback Systems): \(L = PC\) and the four closed-loop maps. Prerequisites stay `loop-gain` and `block-diagram`.

**Confidence.** High.

### 7. Closed-loop sensitivity

**Existing ids:** `fb-errors` (EE 105, ME 132, Feedback Systems), `sensitivity` (ME 132, Feedback Systems), and the desensitivity questions inside `loop-gain`.

**Why they overlap.** `fb-errors` defines the static fractional miss from the ideal gain \(1/f\) as \(1/(1+T_0)\), then shows that miss growing with frequency. `sensitivity` defines \(S = 1/(1+L)\) and \(T = L/(1+L)\) and drills \(S\) for a constant loop gain. Those are the same function. `loop-gain` already contains the same "loop gain 200, what is the fractional error" question. Candidate 6 moves that question. What remains here is \(S\) itself versus the control reading of \(S\) and \(T\) for disturbances and noise.

**Neutral core.** Keep the id `fb-errors` and retitle it. Name: Sensitivity of a feedback loop. Scope: \(S = 1/(1+L)\) is the fraction by which the closed loop misses the ideal feedback ratio, and that fraction grows as \(|L|\) falls.

**Prerequisites.** `loop-gain`.

**Course-specific skills.**

- `fb-amp-errors` (EE 105): the gain error of an op-amp amplifier from a finite, frequency-dependent open-loop gain. Prerequisites stay `fb-errors` and `fb-amp`.
- `sensitivity` (ME 132, Feedback Systems): disturbance, sensor noise, and tracking through \(S\) and \(T\). The constant-gain "compute \(S\)" drills move to the core. Prerequisites: the core and `loop-tf`.

Integral action in `pid` and in `integral-action` both use the steady-state fact that lives in this core. They stay two controller structures. No third skill.

**Confidence.** High.

### 8. Stability margins

**Existing ids:** `stability` (EE 105, ME 132, Feedback Systems), `amp-compensation` (EE 105), `loop-margin-design` (ME 132, Feedback Systems).

**Why they overlap.** The split into a core and two applications is already the right shape, and both applications already require `stability`. The core bank has not followed the split. It still asks for the phase margin of a loop with poles at 1 kHz and 1 MHz, and for where to put the non-dominant pole. Those are the amplifier questions that `amp-compensation` exists to own. `loop-margin-design` then teaches the design reading (about 45–60 degrees, delay margin) on top of a core the control learner has already practiced in amplifier numbers.

**Neutral core.** Keep `stability`. Name: Closed-loop stability and margins. Scope: phase margin and gain margin from where the loop gain crosses magnitude 1 and phase \(-180^\circ\), including the fact that a single-pole loop cannot reach \(-180^\circ\).

**Prerequisites.** `pole-zero`, `loop-gain`, and `bode`. Unchanged. The core's numbers stay in rad/s.

**Course-specific skills.** No new ids.

- `amp-compensation` (EE 105): dominant-pole and Miller compensation, the unity-gain follower, and a capacitive load. Prerequisites unchanged.
- `loop-margin-design` (ME 132, Feedback Systems): choosing a margin and turning a delay into a phase budget. Prerequisites unchanged.

**Confidence.** High. The work is a content move into skills that already exist.

### 9. Finite-horizon decision sequence

**Existing ids:** `trajectory-optimization` (NLO), `mpc` (ME 132, Feedback Systems).

**Why they overlap.** Both skills decide a sequence, add a cost along that sequence, and treat the dynamics as constraints. `trajectory-optimization` transcribes the whole grid once, and an obstacle makes the set nonconvex. `mpc` solves a short horizon at every sample and applies the first input. The NLO plan kept them apart and added no edge, and asked for a core to be proposed here. The Riccati gain in `lqr` is a different object. A sampled difference equation in `discrete-time` is a different object. A plant model in `state-space-model` is a different object.

**Neutral core.** New id `finite-horizon-sequence`. Name: Finite-horizon decision sequence. Scope: the decision is a sequence of inputs or states, the cost is a sum along the sequence, and the dynamics are constraints.

**Prerequisites.** None. `optimization-problem-formulation` is the right vocabulary, and its text is neutral, but it requires `rn-important-subsets`, and both skills sit only in NLO. Putting either one under `mpc` would send a control learner through the NLO box. Leave that edge on the NLO application.

**Course-specific skills.**

- `trajectory-optimization` (NLO): one open-loop transcription, including a nonconvex obstacle. Prerequisites: the core, `optimization-problem-formulation`, and `optimization-problem-classes`.
- `mpc` (ME 132, Feedback Systems): receding horizon, apply the first input, respect constraints. Prerequisites: the core, `state-feedback`, and `discrete-time`.

**Confidence.** Medium. The shared shape is real, and the two skills are short on purpose. Build this only if the showcase of one planning core is worth two new edges.

### 10. Transfer-function title

**Existing ids:** `tf` (EE 105, ME 132, Feedback Systems). `freq-resp-circuits` and `two-port` are the EE 105 applications and already depend on the right neighbors.

**Why it is on this list.** The display name and the `owns` line still say "voltage and current gain, transimpedance." The explainer and ten of the twelve questions are already the neutral object: \(H(s)\) from a linear differential equation, DC gain, series and parallel blocks. One preview uses a forward gain and a feedback factor. One preview uses a pole in kilohertz. The skill is already the core. The title still describes the circuit view.

**Neutral core.** Keep `tf`. Name: Transfer functions. Scope: the zero-state ratio of output to input, as a ratio of polynomials.

**Prerequisites.** `sinusoid-resp`. Unchanged.

**Course-specific skills.** No new skill. Move the feedback-factor preview to `fb-amp` and the kilohertz preview to `freq-resp-circuits`. `two-port` keeps loading and port resistance.

**Confidence.** High that the title should change. Low as a split: the bank is already mostly neutral.

### 11. Positive definite quadratic forms

**Existing ids:** `positive-definite-matrices` (NLO), `lyapunov` (Feedback Systems).

**Why they overlap.** Both use a symmetric matrix \(P\) with \(x^T P x > 0\). `positive-definite-matrices` is the eigenvalue test and the ellipse picture. `lyapunov` certifies an equilibrium with a function \(V\), and for a linear system it solves the Lyapunov equation for that same \(P\). The test is one concept. The certificate is the control application. `lqr` picks a gain from a quadratic cost. It is not this test, and it stays its own skill. It can list the core as a prerequisite later.

**Neutral core.** Keep `positive-definite-matrices`. Name: Positive (semi)definite matrices. Scope: \(x^T P x\) is positive for every nonzero \(x\) exactly when every eigenvalue of the symmetric matrix is positive.

**Prerequisites.** The eigenvalue core from candidate 3, instead of `spectral-decomposition`. Do this only after that core exists. Otherwise Feedback Systems would depend on the NLO spectral skill.

**Course-specific skills.**

- The ellipse picture and the Hessian link stay on the core. `convexity-second-order` already owns the Hessian test for a convex function.
- `lyapunov` (Feedback Systems): \(V\) decreasing along the motion, and the Lyapunov equation. Prerequisites: the core, `equilibria`, and `lti-stability`.

**Confidence.** Medium. The shared object is real, and each skill's theorem is its own. Worth doing after candidate 3, not before.

## Reviewed and left as they are

These pairs share a word or a picture. Each one stays two skills.

| Ids | Why they stay separate |
| --- | --- |
| `kalman`, `observer`, `kalman-optimal-observer`, `kalman-recursive-least-squares`, `extended-kalman-filter` | SG-056. The core is the recursion. The others are the pole-placed observer, the variance reading, the least-squares derivation, and the nonlinear measurement. |
| `calculus-of-variations`, `lagrange-multiplier-equality` | A stationarity condition on a curve, versus multipliers for finitely many equality constraints. |
| `calculus-of-variations`, `lqr` | A free curve, versus an infinite-horizon quadratic cost reduced to a Riccati gain. |
| `calculus-of-variations`, `cx-exp` | The Euler-Lagrange equation, versus Euler's formula for \(e^{jx}\). |
| `largest-inscribed-ellipsoid`, `positive-definite-matrices`, `spectral-decomposition` | A convex program that fits an ellipsoid, versus the definiteness test and the eigenpairs. The matrix skills stay prerequisites. |
| `trajectory-optimization`, `lqr`, `discrete-time`, `state-space-model` | Covered by candidate 9's boundary. No edge from the trajectory skill into those control skills. |
| `lqr`, `quadratic-function-minimization` | A Riccati gain, versus an unconstrained quadratic. Candidate 11 does not merge these. |
| `fb-linearization`, `linearization` | Exact cancellation where the input coefficient is nonzero, versus a local Jacobian. |
| `noise-dist`, `gaussian-random-vectors` | Op-amp noise and distortion, versus the mean and covariance of a Gaussian vector. |
| `gbw`, `perf-specs-freq`, `loop-shaping` | A gain-bandwidth product of a compensated amplifier, versus bandwidth as a loop-shape target. |
| `heavy-ball-method`, `second-order-sys` | A momentum iteration. The second-order picture in its derivation is not the damping skill, and NLO must not require the control skill. |
| `condition-number-gradient-rate`, `robust-stability` | The condition number of a quadratic, versus a plant uncertainty weight. |
| `power-method-eigenvector`, `eig-modes` | An algorithm for the top eigenvector, versus the modes of a linear system. |
| `pid`, `integral-action` | Two places the same steady-state fact is used. The fact stays in candidate 7. |
| `nyquist`, `root-locus`, `gen-gain-phase` | Three different tests. They already sit on top of `stability` or `loop-tf`. |

## Ranked summary

Build in this order. Rank is the priority. Confidence is how sure the overlap is. Kalman is excluded because SG-056 already split it.

| Rank | Candidate | Existing skill ids | Neutral core | Core prerequisites | Course-specific skills | Confidence |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | First-order linear response | `step-resp`, `first-order-sys`, `rc-lpf`, `lti-circuits` | First-order systems (keep `first-order-sys`): one real pole, time constant, DC gain, exponential step and free response | `step-resp` | `rc-lpf` (EE 105). Narrow `step-resp` to the impulse-to-step relation and pulses. `lti-circuits` stops re-deriving the RC exponential. | High |
| 2 | Second-order poles | `second-order-sys`, `rlc`, `lti-mech`, `step-specs`, `pole-zero` | Second-order systems (keep `second-order-sys`): natural frequency, damping ratio, and the three damping cases | `pole-zero` | `rlc` (EE 105, \(Q\) and resonance). `lti-mech` (ME 132 and Feedback Systems, mass-spring-damper). `step-specs` keeps overshoot, rise, and settling. | High |
| 3 | Eigenvalues and diagonalization | `lin-algebra-review`, `eig-modes`, `spectral-decomposition` | Eigenvalues and diagonalization (new id `eigenvalues-diagonalization`): \(Av = \lambda v\) and a basis of eigenvectors | `lin-algebra-review`, narrowed to rank, null space, and determinants | `eig-modes` (ME 132 and Feedback Systems, modes). `spectral-decomposition` (NLO, symmetric orthonormal form). | High |
| 4 | Least squares | `linear-least-squares`, `least-squares-data-fitting`, `sys-id` | Linear least squares (keep `linear-least-squares`): minimize the squared residual of \(Ax \approx b\) by the normal equations | `lin-algebra-review` | `sys-id` (ME 132 and Feedback Systems). `least-squares-data-fitting` (NLO). New NLO skill `least-squares-quadratic` for the quadratic and pseudoinverse derivation. | High |
| 5 | Linear approximation at an operating point | `nl-cap`, `diode-ss`, `ss-model`, `bjt-ss`, `linearization`, `taylor-approximation-multivariable` | Linear approximation at an operating point (new id `local-linear-approximation`): value plus derivative at a chosen point; the model is local | none | The four EE 105 small-signal skills. `linearization` (ME 132 and Feedback Systems). `taylor-approximation-multivariable` (NLO, adds the Hessian). | High |
| 6 | Loop gain and the closed-loop formula | `fb-intro`, `loop-gain`, `fb-amp`, `loop-tf` | Loop gain (keep `loop-gain`): product around the loop, closed loop equals forward gain over one plus loop gain | `fb-intro`, `tf` | `fb-amp` (EE 105, feedback factor). `loop-tf` (ME 132 and Feedback Systems, \(L = PC\) and the four maps). `fb-intro` keeps the diagram. | High |
| 7 | Closed-loop sensitivity | `fb-errors`, `sensitivity`, `loop-gain` | Sensitivity of a feedback loop (keep `fb-errors`, retitle): \(S = 1/(1+L)\) is the miss from the ideal feedback ratio | `loop-gain` | `fb-amp-errors` (EE 105). `sensitivity` (ME 132 and Feedback Systems: disturbance, noise, and tracking). | High |
| 8 | Stability margins | `stability`, `amp-compensation`, `loop-margin-design` | Closed-loop stability and margins (keep `stability`): gain margin and phase margin from \(L(j\omega)\) | `pole-zero`, `loop-gain`, `bode` | `amp-compensation` (EE 105). `loop-margin-design` (ME 132 and Feedback Systems). Move the amplifier-pole drills out of the core. | High |
| 9 | Finite-horizon decision sequence | `mpc`, `trajectory-optimization` | Finite-horizon decision sequence (new id `finite-horizon-sequence`): a sequence is the decision, a sum is the cost, dynamics are constraints | none | `trajectory-optimization` (NLO, one open-loop grid). `mpc` (ME 132 and Feedback Systems, receding horizon). | Medium |
| 10 | Transfer-function title | `tf` | Transfer functions (keep `tf`, retitle): zero-state output-input ratio as a ratio of polynomials | `sinusoid-resp` | No new skill. Move the two circuit-flavored preview questions to `fb-amp` and `freq-resp-circuits`. | High |
| 11 | Positive definite quadratic forms | `positive-definite-matrices`, `lyapunov` | Positive (semi)definite matrices (keep `positive-definite-matrices`): \(x^T P x > 0\) exactly when every eigenvalue is positive | the eigenvalue core from rank 3 | `lyapunov` (Feedback Systems). `lqr` stays a separate Riccati skill. | Medium |
