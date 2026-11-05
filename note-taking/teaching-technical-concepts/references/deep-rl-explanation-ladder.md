# Deep RL / actor-critic: the explanation ladder

For questions about reinforcement learning — value functions, Q-learning, actor-critic, SAC, and the
memory-augmented variants used in the user's reading (HSAC, hidden action, non-Markovian state,
RNN/LSTM comparisons). The user already knows optimal control, so the ladder starts there and never
starts from a textbook.

## The rung order (each rung is a prerequisite for the next)

Do not jump rungs. Every time a rung was skipped, the recap that came back the following turn had the
skipped thing wrong.

| # | Rung | The one-line gloss that lands |
|---|---|---|
| 1 | reward `r` vs return | `r` is one step's score; the return is everything from here on |
| 2 | `Q(s,a)` | "from this situation, if I take this action and then behave sensibly, how much total reward do I collect?" |
| 3 | why an actor exists | plain Q-learning needs `max_a Q(s,a)`; 7 joints make that unsearchable in real time, so a second network learns the argmax. **"Actor-critic = can't argmax, so learn the argmax."** |
| 4 | critic = predictor, not judge | the environment is the scoreboard; the critic is a *prediction of the final score*; the actor is whichever move raises the prediction |
| 5 | walking uphill | the actor only ever sees the critic's slope — never a reward, never a label. Literature name: policy gradient ascent |
| 6 | on- vs off-policy | on-policy bins its data every update (valid by construction, but sample-hungry); off-policy keeps a replay buffer and needs correction machinery |
| 7 | stochastic policy + entropy | entropy = how spread out the choice is, measured in nats; SAC pays a bonus for staying undecided and prices it with a temperature α |
| 8 | the assembly | **SAC = DDPG + twin critics + target networks + stochastic policy + entropy bonus** |
| 9 | memory-augmented variant | extra policy output fed back as next cycle's input, trained only through the value function |

## Glosses and analogies that landed (reuse these)

- **Q ≈ cost-to-go.** `V(x) = xᵀPx` is the optimal-control cousin; Riccati hands you `P` because the
  model is known, RL has to learn it. The actor is the analogue of `u = -Kx`.
- **The critic's label is computed, not given.** Keep this in the user's own words: *the answer key is
  made by the student.* It explains in one line why target networks and twin critics exist.
- **Entropy is a count of surprise, in nats.** Anchor it with values rather than adjectives:
  50/50 → 0.6931, 90/10 → 0.3251, 99/1 → 0.0560, uniform over 7 → 1.9459. "Locked in" has near-zero
  entropy; "undecided" has maximum.
- **Ancestor failures → fixes**, three pairs: continuous actions can't be argmaxed → add an actor;
  the label moves while you fit it and drifts optimistic → twin critics (take the smaller) plus slow
  target copies; the policy locks onto its first habit → output a distribution and pay for uncertainty.
- **A hop, not a mode.** Where a fallback path runs every cycle rather than on entry, say so in exactly
  those words — "patching isn't a mode you enter, it's the default that's always running" pre-empted a
  wrong recap about which controller the arm follows.
- **Squashed Gaussian / reparameterisation.** Actor emits `μ` and `σ`, samples `a = μ + σ·ε`, then
  `tanh`s the result into range: you cannot backprop through "random", but this rewrite puts `μ` and `σ`
  in plain arithmetic. `tanh` is an activation function, the same object as the sigmoid at the network's
  output that they met before.

## Compute these; never state them from memory

Each of these was wrong or unsourced when recalled, and one call fixes it. Put the numbers in the reply.

- Entropy values in nats (see above) — the demo is three lines.
- A reward-vs-return contrast: an episode's penalty total against `4000 - 10·N_step` and against the
  score of a single bad decision, as a share of the success bonus.
- A bootstrapping sweep on a 3-state chain, to show the value estimate crawling back to the true value.
- A reward-free ascent demo: a 1-D quadratic score, four steps of following the slope only. The absence
  of any reward from that loop *is* the lesson about policy gradients.
- The γ horizon: `0.99^100 ≈ 0.366`, `0.99^1000 ≈ 4e-5`.

## Grounding a video question

When the user asks how a concept relates to a video they learn from, build the bridge on the video's
**published chapter list**, not on a guessed memory of the content — and say plainly which parts of the
mapping are inferred from chapter titles. Identify the video with the oEmbed endpoint (title, author,
canonical URL) and read the chapter list out of the watch page's own description block; both come back
without any player or caption access. The user's standing references: a deep-learning series whose rungs
map to network, gradient descent, backpropagation, and a single reinforcement-learning overview whose
chapters map to MDP, Monte Carlo, temporal difference, Q-networks and policy gradients.

## Answering a recap

- **Correct it; do not restate it.** Name the clause that is wrong, say that clause is the whole concept,
  then give the corrected version in the user's own vocabulary. "Your analogy is 80% right — and the 20%
  that's wrong is the whole concept" is the shape that works.
- **A recap that merges two roles will merge them again next turn.** Count the distinct objects (networks,
  roles, inputs) explicitly; "two networks" for a five-network cast is the error to expect.
- **Multiple asks in one message get answered in one pass**, in the order asked, each with its own header.
  Do not split them across turns.
- **Close on limitations if the topic is a paper's claim.** The user reads critically and wants the gaps:
  missing baselines, absent ablations, unstated parity between method and baseline, and a term the write-up
  drops are the four that recur.
