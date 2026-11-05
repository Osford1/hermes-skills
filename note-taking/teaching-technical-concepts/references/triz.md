# TRIZ: teaching notes + verified data source

For when the topic is TRIZ ("Theory of Inventive Problem Solving", Altshuller, USSR, 1946+),
inventive problem solving, or cross-domain solution transfer. TRIZ's premise is that **inventive
solutions are a small finite set of patterns and they recur across unrelated fields** — which makes
it a natural fit for this user (mechatronics, precision motion, patent-adjacent research prep).

## Sell it as a lead generator, never an oracle

State the limits yourself, up front, because this user reads critically and will find them:

- It only knows what has **already been patented** — it cannot surface a genuinely new mechanism.
- The 39 parameters are **20th-century mechanical/thermal vocabulary**. No latency, bandwidth,
  compute or data quality; economics and schedule have no representation at all. Darrell Mann's
  2003 rework widens it; Altshuller's original does not cover software-shaped problems.
- **Of the 1482 off-diagonal cells in the original matrix, 292 are blank.** A blank means "no
  strong signal in the patent record", not "no solution".
- The flagship patent-count claim varies by source (400,000 analysed vs ~200,000 reviewed with
  ~40,000 judged genuinely inventive). Give the order of magnitude and flag the spread rather than
  repeating one number.

## The rung order that landed

1. **Why it matters** — the wall is that improving one thing degrades another, and TRIZ's claim is
   that the Pareto curve is usually not the frontier: someone in another field already killed this
   exact trade-off.
2. **Contradiction, not trade-off** — contrast "more strength costs mass, pick a point" against
   "strength ↑ *forces* mass ↑, so dissolve the contradiction".
3. **Technical vs physical** (below) — the load-bearing distinction.
4. **The toolkit in one pass** — 40 principles, 39 parameters + matrix, laws of evolution, ARIZ,
   five levels of invention.
5. **Worked lookups in their own domain**, then deliberately outside it.
6. **Limits**, then the borderline classification test.

## Framing sentence (get this one right)

Describe the worsening parameter as **the constraint you refuse to concede** — never as something
"you're willing to see get worse". The trade-off reading re-imports the exact model TRIZ removes,
and the restate will come back as "what we are willing to give up". See the SKILL.md pitfall.

## Technical vs physical (the discriminator to hand them as a table)

| | Technical | Physical |
|---|---|---|
| Opposition sits | between **two different parameters** | between **two values of one property, one element** |
| Phrasing | "improving 28 degrades 9" | "X must be P **and** ¬P" |
| Resolved by | the 40 principles, via the matrix | the separation axes |
| Invention level | usually L2 | usually L3+ |

Tell: if the matrix returns generic mush, or you cannot name two parameters, it is physical. That
is a *feature* — physical contradictions are where the matrix goes quiet and the big inventions are.

## Data source (verify before quoting any cell)

`cells["<improving>,<worsening>"] = [principle ids, strongest first]`.

- `https://raw.githubusercontent.com/Antropocosmist/triz-engineering-solver/main/resources/contradiction_matrix.json`
  — full 39×39, 1190 populated cells; siblings `39_parameters.md`, `40_principles.md`,
  `separation_principles.md` carry the descriptions.
- **Do not scrape triz40.com's matrix page** — it renders each cell as concatenated digits with no
  separators (`158<br>2934`), ambiguous to parse.
- **Anchor-verify, printing the checks.** The page states its own worked example in prose: improve
  *strength* (14) without worsening *mass* (2) → principles 40, 26, 27, 1. That is free ground
  truth. A mismatch anywhere means the wrong matrix, not a typo.

## Separation axes (for physical contradictions)

Never compromise ("make it semi-stiff") — that is bad at both jobs. Move the properties apart.
Search cheapest-first: **space → time → condition → system level.**

| Axis | The move | Motion-control reading |
|---|---|---|
| **Space** | A in region X, ¬A in region Y, same element | rigid link + elastic joint (series elasticity) |
| **Time** | A during t₁, ¬A during t₂ | stiff in approach, soft at touchdown |
| **Condition** | A under one load/stimulus, ¬A under another; nothing switched deliberately | stiffness that is a function of contact load |
| **System level** | A at the component, ¬A at the assembly | a brush: soft fibres, stiff whole |

Most real cases admit two or three; choosing between them is engineering judgement and a cost
question, not the TRIZ part. If none fits, the contradiction is mis-framed.

## Vocabulary lists

**39 parameters:** 1 Weight of moving object · 2 Weight of stationary object · 3 Length of moving
object · 4 Length of stationary object · 5 Area of moving object · 6 Area of stationary object ·
7 Volume of moving object · 8 Volume of stationary object · 9 Speed · 10 Force (intensity) ·
11 Stress or pressure · 12 Shape · 13 Stability of the object's composition · 14 Strength ·
15 Duration of action by moving object · 16 Duration of action by stationary object ·
17 Temperature · 18 Illumination intensity · 19 Use of energy by moving object · 20 Use of energy
by stationary object · 21 Power · 22 Loss of energy · 23 Loss of substance · 24 Loss of information ·
25 Loss of time · 26 Quantity of substance/matter · 27 Reliability · 28 Measurement accuracy ·
29 Manufacturing precision · 30 Object-affected harmful factors · 31 Object-generated harmful
factors · 32 Ease of manufacture · 33 Ease of operation · 34 Ease of repair · 35 Adaptability or
versatility · 36 Device complexity · 37 Difficulty of detecting and measuring · 38 Extent of
automation · 39 Productivity

**40 principles:** 1 Segmentation · 2 Taking out · 3 Local quality · 4 Asymmetry · 5 Merging ·
6 Universality · 7 Nested doll · 8 Anti-weight · 9 Preliminary anti-action · 10 Preliminary action ·
11 Beforehand cushioning · 12 Equipotentiality · 13 The other way round · 14 Spheroidality ·
15 Dynamics · 16 Partial or excessive actions · 17 Another dimension · 18 Mechanical vibration ·
19 Periodic action · 20 Continuity of useful action · 21 Skipping · 22 Blessing in disguise ·
23 Feedback · 24 Intermediary · 25 Self-service · 26 Copying · 27 Cheap short-living objects ·
28 Mechanics substitution · 29 Pneumatics and hydraulics · 30 Flexible shells and thin films ·
31 Porous materials · 32 Color changes · 33 Homogeneity · 34 Discarding and recovering ·
35 Parameter changes · 36 Phase transitions · 37 Thermal expansion · 38 Strong oxidants ·
39 Inert atmosphere · 40 Composite materials

A principle is a prompt, not a solution — always finish the translation step ("what would
*segmentation* look like for this part?"). The 40 are also the answer set for the separation axes.

## Closing test to use

End on a **borderline classification**, not a textbook one — the failure mode is filing something
under the wrong type. Good discriminator question: *"the stage must arrive fast and settle with no
overshoot — technical or physical, and what's the tell?"* (Technical: speed and stability are two
separately nameable parameters.)

Catalogue the widget beside this file: a DOM grid contradiction-matrix explorer was built and
verified for this topic — see the `interactive-concept-widgets` skill for the build and probe rules.
