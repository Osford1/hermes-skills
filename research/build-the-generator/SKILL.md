---
name: build-the-generator
description: "Use when work repeats: build the generator, not the output."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [frameworks, scaling, experiments, systems, research-workflow]
    related_skills: [experiment-session-report, experiment-report-bilingual, staged-deliverable-builds]
---

# Build the Generator, Not the Output

A framework for work that has to happen many times: build the machine that produces the
output instead of the output itself. Distilled from a solo game developer's devlog
(Project Tomorrow) and adapted for research, engineering and reporting work.
Domain-neutral. No tool dependency — it is a way of deciding what to build.

## When to Use
- A deliverable will be produced more than a handful of times (experiments, variants, reports).
- A pipeline exists as a pile of one-off scripts or hand-edited runs.
- Planning an experiment campaign, or the user asks how to scale a body of work.
- Writing up work that has to read as earned rather than lucky.
- Don't use for: a genuinely one-off artifact. If the machine costs more than the single
  output, produce the output by hand and say so plainly.

## The Core Rule
Build the thing that produces the output, not the output.
Generated work scales. Authored work does not.

## The Two Benefits — do not weld them
| Benefit | What builds it | Example |
|---|---|---|
| **Variety** — each output differs, at no extra cost | Parameterise the generator | change one value, the whole surface changes |
| **Quantity** — many outputs, same cost each | Reuse instances; update many through shared systems | pooled bullets, thousands of enemies |

Variety comes from parameterising. Quantity comes from reuse.
"The products change and can still be mass produced" needs both machines. One alone gives neither.

## Where the Fixed Thing Sits
Ordinary mass production fixes the product, so copies are cheap and retooling is expensive.
The framework moves the fixed thing up one level: **the rules are fixed, the product varies.**
Setup is paid once per rule set instead of once per product. That is mass customisation,
and the economics of scale are unchanged.

## The Three Limits
1. **Outputs are correlated.** They are variations on one theme — coherent, not arbitrary.
2. **There is a valid range.** Push a parameter far and quality degrades. The generator is only good inside the range it was designed for.
3. **Parameterise high, not low.** Free the layer that every output passes through. Freeing one leaf still leaves you painting leaves.

## Research and Engineering Translation
| The machine | Your work |
|---|---|
| Material graph → variety | Condition generator: plant parameters, trajectory family, operating points |
| Pooling / shared systems → quantity | Cheap runner: batched, preallocated, one entry point per condition |
| The finding | Where the family breaks, not where it holds |

Two rules that flip sign between a game and research:
- A game wants coherent output. Research wants the edge of the range — the reportable result is the failure at the boundary.
- Reuse the machine, never the samples. Disjoint training and test conditions, or the scale is fake.

## The Narrative Skeleton (for the write-up)
1. **Constraint first**, before the method. It kills the objections before they are raised.
2. **System**, not settings. "A condition-family sweep with disjoint train/test" beats "we tuned it".
3. **Measured result**, with the comparability caveat stated by you, not discovered by a reviewer.
4. **Cost**, honestly, including what failed. The failure montage is why the rest is believed.

## Procedure
1. Count how many times the output must be produced. Below roughly five, stop — build it by hand.
   *Done when: the count is written down.*
2. Find the layer every output passes through and parameterise that one.
   *Done when: one parameter change alters the family with no code edits.*
3. Split the two benefits explicitly: what varies, what repeats. Name which machine delivers each.
   *Done when: the variety list and the quantity list are separate.*
4. Build the condition generator: one config object plus a sampled family over it.
   *Done when: the family is a data structure, not a comment.*
5. Build the cheap runner: one entry point, fixed buffers, results appended to one file, one table out.
   *Done when: the whole results table comes from a single command.*
6. Enforce sample hygiene: training conditions and test conditions disjoint, asserted in code.
   *Done when: the assertion fires if the sets overlap.*
7. Report the family and hunt the edge. Name which conditions break it, with numbers.
   *Done when: at least one failure region is named.*
8. Write it up in constraint → system → result → cost order.
   *Done when: the constraint appears before the method.*

## Worked Example (the user's own lab)
`C:/Users/<you>/dev/motion-ff-lab` — a hands-on feedforward demo, agent-built 2026-08-31.
- **Variety**: one hardcoded reference trajectory and default plant params → a trajectory family plus a sampled `PlantParams` range.
- **Quantity**: `run()` in `run_baseline.py` is already the shared runner. Batch it, preallocate its log arrays.
- **Validity gap**: training and evaluation share one trajectory, so the reported improvement is a fitting score, not generalisation.
- **Honest status**: a toy 1-DOF sim with no disturbance and no sensor noise. It demonstrates the mechanism; it is not evidence about real hardware.

## Pitfalls
- **Welding variety and quantity into one claim.** They come from two different machines.
- **Fake scale.** Many runs over one condition is not a family. Vary the condition, not just the seed.
- **Demo numbers presented as evidence.** A toy plant with no disturbance, no noise and train-on-eval supports "the mechanism works", never "the method is better". Label which numbers are which.
- **Parameterising low.** One freed asset is not a generator.
- **Expecting arbitrary variety.** Outputs inherit the rule set; they are a family, and the family has an edge.
- **Building a machine when one copy would do.**

## Verification
- Change one parameter and rerun: does the output family change with no code edits?
- Is the whole results table reproducible from one command?
- Are train and test conditions provably disjoint?
- Does the write-up name the constraint before the method, and state what the numbers do not support?
