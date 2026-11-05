# Reinforcement learning foundations — the teaching ladder (SAC / actor-critic)

Load when the user is learning RL off a robotics paper (HSAC / SAC / PPO / TD3), asks what a
Q-value, actor, critic, on-policy or off-policy is, or says a previous explanation was not enough
to implement from.

## Lead with the framing that resolves most of the confusion: why an actor exists
Plain Q-learning picks actions by `max_a Q(s,a)`. You cannot argmax a network over a continuous
action space in real time, so a second network gets trained to approximate the argmax. That network
is the actor. The critic exists to give the actor a gradient. One line: "actor-critic = can't
argmax, so learn the argmax." Say this before any loss function — it answers the "why two networks"
question the user actually has.

## Check the first restate for these four errors
1. **"Both networks receive the reward."** Neither does — `r` only ever builds the critic's LABEL.
   The actor never touches `r`; it reads the critic's slope. Framing that lands: the environment is
   the scoreboard, the critic predicts the final score, the actor moves toward the higher prediction.
   The critic is NOT a judge handing out praise — it is a predictor with no opinion of its own.
2. **"The reward IS the Q-value."** `r` is one step and it is observed; `Q` is the discounted sum of
   all future steps and it is predicted. Worked pair to quote: r at step 0 = 1.00 while
   Q(s0,a0) = 5.9203.
3. **Network count.** SAC is five networks, two roles: actor π, critics Q1 Q2, target critics Q1' Q2'.
   "Actor-critic" names the two jobs, not the number of nets.
4. **"The critic tells the actor good/bad."** The actor ascends the critic's gradient, not a message.

## Q in this user's own domain (the bridge that lands)
Q is a *learned cost-to-go*. LQR's `V(x) = xᵀPx` is the same object; Riccati hands you P because the
model is linear and known, RL learns it because it isn't. `u = −Kx` is the greedy step down that
surface — the actor is that step. Say it once, early, then drop it.

## The equations, read out loud (a few lines each, no more)
- return: `G_t = r_t + γ r_{t+1} + γ² r_{t+2} + …`
- the self-referential identity the critic must satisfy: `Q(s,a) = r + γ Q(s',a')` — "the score of
  this move is the reward it just earned, plus a discounted score of where I ended up."
- the training target and loss: `y = r + γ( min_i Q'_i(s',a') − α log π(a'|s') )`,
  `loss = mean (Q − y)²`. Read it term by term: `y` = the answer key, `min` = pessimist of two
  critics, `θ'` = frozen slow copy, `α log π` = entropy bonus. Then name the consequence: the critic
  is supervised regression with self-made labels.
- **A paper's printed SAC losses often omit the entropy term and the temperature α.** Check for a
  missing α before teaching SAC out of a paper and say so — the user is rebuilding from these
  equations, and the temperature is often what stops a policy locking onto one behaviour.
- γ as a horizon, by arithmetic not adjectives: γ=0.99 makes a step 100 ahead count 0.37 and 1000
  ahead count 4×10⁻⁵; effective horizon 1/(1−γ) = 100 steps. Say that γ is chosen so the horizon
  covers the episode (≈120-step episodes ⇒ 0.99).

## Three demos that carry the lesson (numbers, never symbols alone)
Run these in Python and paste the output. Symbols alone do not land for this user; real output does.
1. **r vs return** on one 3-step trajectory (rewards 1,2,3; γ=0.99): step 0 has r=1.00 but the return
   from there is 5.9203 — the critic never sees 5.9203, it *predicts* it from the 1.00.
2. **Bellman sweeps from all-zero values** on a 3-state chain: 0,0,0 → 0,0,1 → 0,0.99,1 →
   0.9801,0.99,1. The values creep backward one state per sweep. Name it: that backward creep IS
   bootstrapping, and no dynamics model was ever supplied.
3. **The actor climbing a FIXED critic** `Q(a) = −(a−2)² + 5`, from a=0, lr 0.1 → 1.83 (best 2.0).
   There is no reward anywhere in that loop — it is the proof that the actor never sees `r`.

## on-policy vs off-policy — one question: whose data may you learn from?
On-policy (PPO, A2C): data must come from the policy you have now; after an update it is stale and
thrown away. Off-policy (SAC, TD3, DDPG, Q-learning): data from any policy, including your own past
selves — hence the replay buffer, and hence a Q-function to correct for data that was scored under
an old definition of "sensible". Keep the coupling explicit: off-policy ⇒ replay ⇒ Q-function.

What on-policy actually BUYS (asked directly, so answer it directly):
- every update is valid by construction; no off-policy correction machinery
- you can use `V(s)` plus the returns you just observed instead of a Q-function: **one value net
  where SAC needs four** — that is the concrete price of off-policy, not just "more samples"
- no replay buffer: less memory, and no stale-data poisoning of the critic
- PPO is hyperparameter-robust out of the box, which is why it is the safe default when samples are cheap
- tolerates a fast-moving policy or target
Cost: it bins its data every update, so it needs millions of steps. That is fatal when one step is a
real 7-DOF arm in front of a person — which is exactly why a safety paper goes off-policy.

## "Is there a hard SAC?" — two readings, both real, answer both
1. **Name axis.** "Soft" = a smoothed max inside the Bellman target, and that smoothing is exactly
   where the entropy bonus and the temperature α come from. The hard counterpart is DDPG
   (deterministic, plain max, no entropy); soft-Q-learning → SAC.
2. **Safety axis — the axis of this user's own paper.** Soft = a penalty inside the reward (e.g. −3
   inside a danger band, −200 per replan). Hard = the unsafe action is unreachable because it is a
   constraint (a CBF-QP safety filter physically cannot emit it). Papers claiming "coordination"
   often run both: soft shaping to teach the policy, hard constraint as the final guarantee. Do not
   answer "don't worry about hard ones" — this reading IS the paper's contribution.

## The missing-before-implement list (asked for right after the first explanation)
MDP (s, a, r, γ, done — the reward is the engineering, the nets are boilerplate); the Bellman label
and TD error; target networks (the label contains Q, so regressing Q onto itself chases its own
tail); twin critics + min (overestimation bias); the replay buffer; the actor updated by gradient
rather than by a message; reparameterisation `a = tanh(μ + σε)` so the gradient flows through the
sample; the entropy temperature α; the loop shape (collect N steps → store → K updates → repeat, NOT
one episode per update). Then the project's own delta on top — the extra head, its own past action
fed back as an input, that value stored in the buffer, plus the curriculum.

## Deliverable shape that worked for a paper-wide concept study
A dark-mode HTML sheet: tiers ranked by load-bearing-ness, then per concept three blocks (used for in
this paper / used for in general / how you would use it technically), then an equation map grouped by
pipeline stage, then a constants table. Quote only numbers grepped out of the paper's own text — see
the attribution pitfall in the parent skill.
