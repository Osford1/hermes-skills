# Control-theory foundations (chain of integrators, time-optimal)

Teaching content for the Karpathy-style concept ladder that clicks with this user.
Present in this order; one tab/rung each in the widget. Each entry: the class definition
first, then the paper term.

## The system: chain of integrators
- A cascade of accumulators. Control `u` is the **top derivative**; position is the last
  integral. `ẋ_k = x_{k-1}`, `ẋ_1 = u`.
- Physical mapping for order `n` (control = nth derivative of position):
  - order 2: position, velocity; u = accel
  - order 3: +accel; u = jerk
  - order 4: +jerk; u = snap
  - order 5: +snap; u = crackle
- **Analogy:** each `∫` is an accumulation tub; the overflow of one tub is the inflow of the
  next (a cascade of bathtubs).

## Integrator = accumulator
- `x(t) = ∫ u dt`; discrete `x += u·Δt`. Rate in, level out; shut the tap (`u=0`) and the
  level holds (you've stored it).
- **Analogy:** bathtub — tap flow is the rate, water level is the accumulated amount.
- Every integration makes the output **smoother** than the input (square-wave jerk → silky
  position). This is why the control (roughest) must be bounded and why real motion is smooth.

## Order
- Order `n` = number of integrators = number of states modeled = how far down the derivative
  ladder you go. NOT "more data" — a more detailed model (ignores derivatives you don't model).
- A choice, not a requirement. Pick the order = the derivatives that are actually limited by
  the hardware and matter for the application (order 3 jerk-limited for CNC/robots; 4–5 for
  ultra-precision wafer stages, where snap/crackle excite structural vibration → settling
  time → lost wafers).

## Constraints & objective
- Input saturation `|u| ≤ M0`; full state constraints `|x_k| ≤ M_k` (a box the trajectory
  must stay inside — position limit is the "wall").
- Time-optimal: minimize `t_f = ∫dt` (the clock, not smoothness).

## Bang-bang & Bang-Singular-Bang
- Bang-bang: full accel then full decel (input limits only).
- Bang-Singular-Bang (with state constraints): full on → **ride the constraint** (`u=0`,
  "singular") → full off. The control is `{M0, 0, −M0}` almost everywhere (Prop 1).
- **Key rule:** any time you're not at a derivative limit you're losing time. Time-optimal =
  always pinned to a limit (halfway is slow).

## PMP / costate
- Costate `λ(t)` = the "shadow price" of each state (how the objective changes if you nudge
  that state). Evolves by `λ̇_k = −∂H/∂x_k`.
- Hamiltonian `H = λ0 + λ1 u + Σ λ_k x_{k-1} + Σ η_k(|x_k| − M_k)`; PMP: choose `u` that
  minimizes `H`. So `u=+M0` when `λ1<0`, `−M0` when `λ1>0`, singular when `λ1=0`.
- The control's sign is entirely dictated by the costate's sign.

## Switching manifold
- The surface/curve in state-space where `λ1=0` (control flips). Class definition: "a curve
  or surface inside a bigger space." For a double integrator reaching the origin it's
  `x = −v|v|/(2A)`.
- Time-optimal move = a sequence of \"riding one constraint at a time\"; the manifold is the
  boundary where each ride ends.
- Higher order: the curve becomes a higher-dim "sheet" — same idea, can't draw it.
- **Junction condition:** `λ` can jump when a state hits a bound (subtleties in Sec III).

## Chattering
- Control wants to switch infinitely often in a finite window; occurs for order ≥ 4; breaks
  numerical solvers. Why no working 4th-order method existed before this paper.

## MIM (the paper's algorithm)
- Manifold-intercept method; greedy but conservative. Compare current position to the
  (n−1)-order optimal-trajectory manifold (the "proper position"); if "higher", slam to
  min-velocity and glide (`u=0`) until you intercept the lower-order manifold, then ride it
  (Bellman's principle of optimality). Built by induction from `n=1`.
- Time-optimal at n≤3; near-optimal, non-chattering for n≥4 (negligible extra time); open
  source. Compares vs Ruckig (no position constraints), SOCPs/Gurobi, Yop/CasADi; ~2 orders
  of magnitude faster, 100% success.
- **S-curve (jerk-limited) contrast:** industry default; feasible but suboptimal —
  "underutilizes the inertia" because it doesn't push the limits.

## Why it matters (applications)
- One problem, four expensive places: CNC/machine tools (cycle time = part cost),
  semiconductor/wafer stages (throughput; top-derivative limits kill vibration), robotics
  (joint trajectories; arbitrary terminal states enable clean blends), chip placers, and
  autonomous driving (comfort via jerk limits).
- The unifying trait: **cycle time is the product and they're already limit-constrained.**
