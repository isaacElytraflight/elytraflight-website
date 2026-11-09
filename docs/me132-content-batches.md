# ME 132 / Feedback Systems content batches

No batch plan was in the repo (no docs entry, no changelog, no earlier ME 132 content PR). This is the breadth-first plan for the 56 skills that were still `coming-soon` when this file was written.

A skill is eligible for a batch only when every prerequisite is already playable, or sits in an earlier batch. Batches hold 5–15 skills. Within a batch the skills do not depend on each other, except for the one pair called out in B8.

The longest prerequisite chain in the coming-soon set has nine skills:

`ode-model` → `state-space-model` → `ss-solution` → `ss-to-tf` → `realization` → `reachability` → `state-feedback` → `separation` → `gen-controller`

Nine skills in a chain need nine prerequisite-closed batches. Eight batches of at least five skills cannot all be prerequisite-closed. B8 is the batch that absorbs that constraint: write `separation` before `gen-controller`. Every other B8 skill depends only on B1–B7.

Shared skills stay domain-neutral cores. No batch adds an EE-only prerequisite. Slugs stay flat and global. Nothing in B1 was split or merged with an existing skill; the dedupe notes are under B1.

## B1 (this batch) — prerequisites already playable

| id | prereqs already playable |
|---|---|
| `fb-concepts` | `fb-intro` |
| `laplace` | `cx-exp` |
| `lin-algebra-review` | (none) |
| `min-phase` | `bode`, `stability` |
| `ode-model` | `lti-def` |

`lin-algebra-review` and `min-phase` live in the Feedback Systems collection and not in the ME 132 course box. They are still the rest of the ready frontier. Leaving them out would make B1 only three skills.

Dedupe, no splits:

- Ids already exist. No new slug, no retirement.
- `lin-algebra-review` stays a core with an empty prerequisite list. Practice rounds are matrices only. Round 4 names reachability, observability, and pole placement as later uses.
- `ode-model` is not `lti-mech`. `lti-mech` owns natural frequency and damping ratio for mechanical LTI models. `ode-model` owns balance laws for a mass, a rotor, an inductor, a capacitor, and a tank.
- `laplace` is not `tf` or `pole-zero`. It owns transform rules and the initial- and final-value theorems.
- `fb-concepts` is not `fb-intro` or `loop-gain`. It owns the open-loop versus closed-loop contrast and the names of the blocks.
- `min-phase` is not the Bode magnitude rules. It owns the slope-to-phase tie, all-pass excess lag, delay, and inverse response.

## B2

`block-diagram`, `first-order-sys`, `model-method`, `onoff-pid-intro`, `state-space-model`

- `block-diagram` is not `fb-concepts`. The earlier skill names the blocks and contrasts open loop with closed loop. This skill multiplies series blocks, adds parallel blocks, and reduces a feedback loop to one gain.
- `first-order-sys` is not `laplace` and not `step-resp`. It owns the time constant, the DC gain, and the step and free response of one real pole.
- `model-method` is not `ode-model`. It owns the choice of states, unit checks, time-scale ratios, and how much detail a control model needs. Nothing lists it as a prerequisite, so round 4 points at linearization, identification, and equilibria.
- `onoff-pid-intro` is not `fb-errors` and not `pid`. It compares on-off, P, PI, and D at the level of steady error. The later `pid` skill owns the three-term law in equations.
- `state-space-model` is not `ode-model` and not `lin-algebra-review`. It owns the A, B, C, D packaging of an ODE. Matrix arithmetic stays in the algebra review.

## B3

`app-examples`, `cruise-control`, `equilibria`, `loop-tf`, `second-order-sys`, `ss-solution`

## B4

`discrete-time`, `eig-modes`, `limit-cycles`, `nyquist`, `pid`, `sensitivity`, `ss-to-tf`, `step-specs`

## B5

`feedforward`, `freq-resp-lti`, `gen-gain-phase`, `linearization`, `lti-stability`, `perf-specs-freq`, `pid-impl`, `pid-tuning`, `realization`, `uncertainty`, `windup`

Dedupe, no splits:

- Ids already exist. No new slug, no retirement.
- `feedforward` is not `sensitivity`. Sensitivity owns \(S\) and \(T\). Feedforward owns the extra path from a measured reference or disturbance.
- `freq-resp-lti` is not `bode` and not `sinusoid-resp`. It owns \(G(j\omega)\) for a general transfer function or state-space model, and the steady sinusoid that follows when the system is stable.
- `gen-gain-phase` is not `nyquist`. Nyquist owns encirclements of a linear loop. This skill owns the describing function and the small-gain idea.
- `linearization` is not `equilibria`. Equilibria finds the resting point. This skill owns the Jacobian at that point.
- `lti-stability` is not `stability` and not `eig-modes`. It owns the half-plane test, Routh-Hurwitz, and the gap between asymptotic and BIBO stability.
- `perf-specs-freq` is not `step-specs` and not `sensitivity`. It turns bandwidth, crossover, and crossover sensitivity into design targets.
- `pid-impl` is not `pid` and not `discrete-time`. It owns derivative filtering, setpoint weighting, and one sample of a discrete PID update.
- `pid-tuning` is not `pid`. The three-term law is the earlier skill. This skill owns ultimate-gain numbers, the reaction-curve fit, and lambda tuning.
- `realization` is not `ss-to-tf`. That skill goes from matrices to \(G(s)\). This skill builds a state-space model from \(G(s)\).
- `uncertainty` is not `sensitivity`. It owns additive and multiplicative weights around a nominal plant.
- `windup` is not `pid`. It owns actuator saturation of the integrator, and clamping or back-calculation.

## B6

`loop-shaping`, `lyapunov`, `observability`, `reachability`, `robust-stability`, `root-locus`, `sys-id`, `time-delay`

## B7

`adaptive`, `fund-limits`, `observer`, `robust-perf`, `state-feedback`

## B8

Write `separation` before `gen-controller`. The other six do not depend on either of those two.

`fb-linearization`, `gain-scheduling`, `gen-controller`, `integral-action`, `kalman`, `lqr`, `mpc`, `separation`
