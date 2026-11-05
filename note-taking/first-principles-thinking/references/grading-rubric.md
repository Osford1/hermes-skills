# Grading rubric — first-principles answers

Four failure modes. Name the one you see, out loud, in the reply. Unnamed errors don't transfer to
the next attempt.

## A. Restate instead of derive
**Signature:** the answer repeats the lecture's sentence; Q4 is empty or is the conclusion again.
**What's wrong:** they memorised the path's endpoint, not the path.
**Fix to hand them:** "write the step where the answer could have come out differently."

## B. Assumption filed as a law (the most common)
**Signature:** "you need six joints", "the loop has to run at 1 kHz", "we use a GRU for that".
**Discriminator:** *who would have to be lying for this to be false?* Nobody ⇒ assumption.
**Fix:** move it to the assumption bin, then check whether the argument survives its deletion.

## C. Derivation with no boundary
**Signature:** Q5 empty, or the model "just works".
**What's wrong:** an unbreakable rule in a physical system means they haven't located the model's
validity limit — which is exactly where the interesting research questions live.
**Fix:** point them at the assumption's own failure regime (saturation, noise, unmodelled dynamics).

## D. No prior failure (Q1 skipped)
**Signature:** the concept feels arbitrary and they can't say why anyone invented it.
**Fix:** find the thing that broke before it (if genuinely nothing broke, it's a definition — say so).

## E. Wrong DEPTH of assumption — the incidental one, not the load-bearing one
**Signature:** they name a real assumption, so B does not apply, but it is an assumption the method
survives deleting. Observed: asked what Cramer's rule stands on, they answered "even a GPU-class
machine is too slow" — the machine rate, not the determinant-as-primitive.
**Discriminator to hand them — the delete-test:** *delete the assumption and look at what is left.*
If the same algorithm just runs slower (or faster), the assumption is **incidental**. If deleting it
changes what the algorithm **is**, it is **load-bearing**. A faster machine is the textbook
incidental: prove it with scaling rather than asserting it — for Cramer, $10^6\times$ more speed
moves the 1-second cliff only from $n\approx13$ to $n\approx18$, and a machine that solves $n=25$
in one second (4.03e26 ops/s) still takes 0.65 years at $n=30$. Speed buys unknowns *logarithmically*;
a factorial eats it.
**Fix:** after the proof, give the direction, not the answer ("the assumption is about what counts as
the primitive operation, not about the hardware") and let them re-answer the box.

## Pass test
Can they state the concept in two sentences to someone who wasn't in the lecture, **using only the
Q2 quantities**? If they need a jargon term that wasn't derived, it's a restate.

## Extended failure modes (engineering-specific)
- **Re-deriving solved problems.** The answer is technically sound and the field settled it years
  ago. This is a knowledge gap, not a discovery — check prior art before crediting it. If a search
  is needed, do the search rather than letting them build on it.
- **Deriving what should be looked up.** Standards, tribology, material fatigue, biology, prices.
  Tell them plainly: this one is a lookup; principles are only for spotting contradictions.
- **Welded axes.** Two independent choices presented as one (feedback vs feedforward, target vs
  constraint, the gripper's command vs its achieved position). Top-priority correction whenever it
  appears; split it with a three-column table (where it lives / its axes / what a point means).

## What to say when they fail a question
1. One line of credit for what was right.
2. "Not quite —" + the corrected line in their vocabulary.
3. The failure-mode name, so they can catch it themselves next time.
4. The next rung's single question.
Never open with the answer; never hand them the derivation they were supposed to attempt. A hint or
the discriminator table is the right amount of help.
