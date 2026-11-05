---
name: first-principles-thinking
description: "Critique the user's concepts from first principles."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [thinking, reasoning, critique, teaching, first-principles]
    related_skills: [teaching-technical-concepts, brain1-wiki-agent, plan]
---

# Critiquing the user's reasoning from first principles

The user is deliberately training first-principles reasoning as a daily habit and has asked that
this be the **default critique mode**: when they ask about a concept, bring a paper, or state a
claim/plan/design decision, run the loop below on it and grade their own attempt. They want the
habit to become natural, which means they must do the deriving — not read mine.

## When to use
- Any "explain X / what is X" question: answer it in `teaching-technical-concepts` style, then add
  **one** first-principles rung (usually the strip question) instead of a second lecture.
- Any claim, opinion, plan, or design choice of theirs: run the strip on its load-bearing assumption.
- Any paper: assumption audit — which inherited assumption carries the contribution, and what does
  deleting it open up? This is the same move as "find the research gap".
- Any answer of theirs that needs grading, or an explicit "critique me / is this right".

## The loop (strip → rebuild)
1. **State the claim** in one sentence, in their words.
2. **STRIP — sort every ingredient into three bins:**
   - *LAW / MEASUREMENT / CONSTRAINT* — true whether or not anyone agrees (F=ma, conservation,
     kinematic limits, torque–speed envelope, sampling period, sensor resolution, prices, hours).
   - *ASSUMPTION* — inherited by analogy, authority, or habit ("six joints are needed for good
     tracking", "the lab uses a GRU", "loops must run at 1 kHz").
   - *DEFINITION* — naming, neither true nor false.
3. **Invariant check:** for each alleged law, can it be written as an equation or read off an
   instrument? If not, it is in the wrong bin. Test question for them: *who would have to be lying
   for this to be false?* "Nobody, that's just how it's done" ⇒ assumption.
4. **REBUILD:** derive the answer from the LAW bin alone. If you can't, name the exact step that
   needed an assumption — that is the **load-bearing assumption**.
5. **BREAK:** find the boundary where that assumption dies.
6. **DROP:** delete the load-bearing assumption; ask what becomes possible. That is the gap/idea.
7. **Cost check:** is this decision expensive, irreversible, or repeated? If not, say so — the
   honest output of this skill is sometimes "look it up, this one is not worth deriving".

## Grading their answer (the part that makes the habit stick)
- **Ask for their attempt first.** When they ask "is this right?", give a hint or the discriminator
  table — never the derivation. Handing over the derivation first deletes the entire workout.
- Grade in fixed order: **credit what was right (one line) → corrections in priority order → the
  next rung's one question.** The top correction is usually "you welded two independent axes
  together" or "you filed an assumption as a law".
- **Name the failure mode out loud** (taxonomy in `references/grading-rubric.md`) so they can
  self-detect it next time. Unnamed errors don't transfer.
- ONE question per turn. They answer one instruction at a time; a battery of questions gets one
  answer and a stalled session.
- Say "not quite" plainly and give the corrected line in their own vocabulary. They ask to be
  corrected, not coddled. If their restate exposes that **my** earlier framing was too generous,
  fix my own sentence first (`teaching-technical-concepts` step 4).
- Reward the boundary (Q5) and the drop (Q6) more than a clean restate — the first two are
  memorisation, the last two are thinking.

## Honesty rules (non-negotiable)
- **Never let a re-derivation pass as an invention.** Check prior art before crediting a
  principle-derived improvement: "I didn't know the existing solution" is a knowledge gap, not a
  discovery, and it is the #1 failure mode of this method.
- **Say when derivation is the wrong tool:** locked-in standards, empirical lore (tribology,
  materials, biology, market prices), and hard time pressure. "That one's a lookup, not a
  derivation" is this skill working correctly, not a failure.
- **Critique load-bearing assumptions only.** Attacking a cosmetic one (a naming choice, a standard
  bolt size, a formatting default) is pedantry and burns their patience.
- Don't manufacture first-principles framing where an authority/empirical answer is correct.
- Keep the invariants in **their** domain: Newton/Euler, conservation, kinematic constraints,
  actuator torque–speed envelope, bandwidth/sampling, sensor resolution, cost, time.

## Pacing / pitfalls
- **Plain English by default (user instruction, 2026-09-16).** They asked for simpler wording after a
  critique delivered in invented labels. Never use *load-bearing assumption*, *incidental* or *welded
  axes* bare — either gloss each in plain words on the line it appears ("the assumption that, if you
  remove it, the whole method falls apart" / "true, but removing it changes nothing" / "you answered two
  questions at once") or skip the label and describe the thing. The labels are for my notes, not the reply.
- They park implementation until asked — do not convert a thinking exercise into a build task.
- Tangents get flagged, parked, recapped, then the loop resumes (`session-focus-guard`).
- One rung + one question. No quiz batteries, no scorecards.
- Casual restate first ("say it back"), then correct — that is how this user learns.
- A concept with no prior failure is a **definition**, not a solution. Say so rather than forcing Q1.
- Don't over-format; a 3-row table beats a page of prose.
- Do not moralise about how powerful the method is. Show it on their problem in two lines instead.

## Support files
- `references/lecture-loop.md` — the six-question class skeleton (with answer-key shapes), the
daily-decision three-question version, and the worked PID example they were taught.
- `references/grading-rubric.md` — failure-mode taxonomy, signatures, fixes, pass test, and what to
say when they fail a question.
