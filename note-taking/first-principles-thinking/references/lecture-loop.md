# The lecture loop — six questions per concept

Fill these in the margin while the lecturer talks. One line each; not an essay per box.

| # | Question | What a real answer looks like |
|---|----------|-------------------------------|
| Q1 | **Problem** — what broke before this existed? | A named prior failure, not "it's important". No prior failure ⇒ it's a definition, not a solution. |
| Q2 | **Raw** — the facts: equations, measured quantities, hard constraints | 2–4 items you could write as an equation or read off an instrument. |
| Q3 | **Assumption** — which step is inherited, not forced? | Exactly one is usually load-bearing. Mark it. |
| Q4 | **Rebuild** — can I get the result from Q2 alone? | A 3-line derivation, or the exact step where Q3 gets smuggled in. |
| Q5 | **Break** — where does it fail? | The boundary condition / the regime where the assumption dies. |
| Q6 | **Drop** — delete the assumption: what becomes possible? | The research-gap generator. Half-formed is fine. |

Pass test for any concept: **state it in two sentences to someone who wasn't in the lecture, using
only Q2 quantities.** If you can only quote the slide, Q4 is empty.

## Worked example — PID, done as a first-principles rebuild

- **Q1** Proportional-only control can't remove a *standing* error (gravity, friction, a constant
  load); pushing gain up forever is the only way, and that destabilises the loop.
- **Q2** Raw facts: plant is `m·x'' = u − b·x' − d`; actuator output `u` is bounded; the encoder
  quantises and the sample period `Ts` exists; `d` is not measured.
- **Q3** Load-bearing assumption: *the disturbance is unknown and unknowable in advance.*
  (Also inherited: linear plant, time-invariant `d`.)
- **Q4** Rebuild: finite gain + a standing error ⇒ you need a state that **accumulates** the error
  and keeps acting until it is zero → integrator. Error's own *rate* anticipates the future error
  by one step → derivative buys phase lead. The three terms are the minimal response to three
  physical obstructions — no magic constants required.
- **Q5** Break: integrator + saturated actuator = windup; derivative + quantised encoder = noise
  amplification. Both are the failure of an assumption, not of the tuning.
- **Q6** Drop: if `d` *is* known one step ahead (it's the commanded trajectory), feedback is the
  wrong tool — nothing inside the loop can act before the error physically exists. That is why
  feedforward exists, and why learning-based feedforward is a research direction and not a tuning
  exercise.

(Use this one when they ask what their supervisor's feedforward work is *for*. Note the honest link:
feedback/feedforward split is the real relation; don't inflate it into "this is the paper" unless
the paper is in front of them.)

## Worked example 2 — Cramer's rule → Gauss elimination (Ch 2.1 of the Tsinghua maths course)

This is the pair that teaches the *what vs how* split, which is the same weld as "target vs constraint".
Use it whenever a lecture offers a closed-form formula and then a working algorithm for the same problem.

- **Q1 promise** — a **closed form**: `x_i = det(A_i)/det(A)`. It says *what the answer is*, exactly,
  in terms of things already defined. It never says how to get it. "Too slow" is the failure of that
  promise, not the promise. (Their first attempt answered Q1 with the cost — failure mode: welded axes,
  *what the solution is* vs *how to compute it*.)
- **Q2 raw facts** — verified, not quoted: a determinant by cofactor/Leibniz costs `n!` terms; Cramer
  needs `n+1` of them = `26·25! = 26! ≈ 4.03e26` ops at `n=25`; `10^12` ops/s is itself an assumption;
  `1 yr = 3.1536e7 s` ⇒ `1.28e7` years. The useful number is the **crossover**: 1 s at `n≈13`,
  1.6 years at `n=20`. Gauss for contrast: `(n³−n)/3` mults = 5,200 at `n=25`, `3.3e8` at `n=1000`.
- **Q3 load-bearing assumption** — *the determinant is the primitive*: every unknown is assembled
  independently from full-matrix determinants and the intermediate work is discarded. (Their first
  answer was the machine rate — incidental; see failure mode E in the grading rubric.)
- **Q4 rebuild** — only three row operations preserve the solution set (swap; scale by nonzero; add a
  multiple of one row to another), so clearing a column is *free* in the sense that costs no information;
  and the multipliers you used to do it are exactly the sub-diagonal entries of `L`. Refusing to form a
  determinant gives `A = LU` and `O(n³)`.
- **Q5 break** — the pivot. `顺序` (in-sequence) elimination takes `a_kk` as pivot come what may; a pivot
  that is merely *small* destroys the answer in floating point (例 2.2: 3-digit garbage from a perfectly
  nonsingular system). "Unique solution" is a statement about *exact* arithmetic; the machine does not
  have exact arithmetic. Same disease as Ch 1 例 1.8.
- **Q6 drop** — delete "compute the determinant" and ask what `A` is *for*: with a fixed `A` and many
  right-hand sides, Cramer pays the full `n!` every time, so it is throwing away reusable work. That
  reuse is the factorization, and it is why every FEA package factorises a stiffness matrix once and
  then runs thousands of load cases through it.

## Daily-life version — three questions before a decision

The user asked for daily life too. Same loop, compressed:
1. **What do I actually want?** (the objective function, in one measurable line — not "be better at
   control" but "finish the ROS 2 phase gate by Friday")
2. **What are the hard constraints?** (hours available, money, hardware on hand, deadlines — things
   that don't move when you argue)
3. **Which of my reasons is inherited?** ("masters students should publish", "everyone in the lab
   works weekends", "I need a GPU"). Delete each one and see whether the decision survives.

If the decision is cheap and reversible (which file name, which library), **stop** — copy the
convention and spend the derivation elsewhere. Say that out loud when they bring one.

## Blank template to copy

```
Concept: ____
Q1 prior failure:
Q2 raw facts (equations / measurements / constraints):
Q3 the assumption (load-bearing one marked *):
Q4 rebuild in my own 3 lines:
Q5 where it breaks:
Q6 if I drop the assumption:
```
