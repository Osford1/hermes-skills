---
name: teaching-technical-concepts
description: "Use when explaining a technical concept to the user."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [teaching, explanation, concept, analogy, user-preferences]
    related_skills: [brain1-wiki-agent, lerobot-embodied-ai, first-principles-thinking]
---

# Teaching technical concepts to the user

The user learns engineering/ML concepts (motion control, robotics, embodied AI, optimal
control) by asking for explanations — usually while reading a paper or building a robot.
They want the concept to actually LAND, tied to their own project and the source paper,
not a textbook dump. This is the method that works for them.

When the ask is to explain the *proofs* in a source they are reading (a lecture deck, a paper),
run the pass in `references/deriving-source-proofs.md` first (it also carries the glyph-level
formula transcription and the source-algebra cross-checks) — the move-count, the page map, the
rendered-page read for garbled formulas, and the numpy recomputation of the source's own worked
example are prerequisites for everything below.

When the ask is to work through one of his **coursework/project questions part by part** ("rework
this with me, starting with 1(a), relate it back to <note>"), follow
`references/walking-assignment-solutions.md` — equation-order steps, every number sourced from the
project's verified engine plus an independent recomputation, a section-by-section map back to the
note he named, and notation restated in every message.

When the ask is to turn a course or a lecture into a **map** — a structure flow chart, a "where are
we in this course" progress diagram — work from `references/lecture-and-course-maps.md`. It covers
pulling the real session schedule and the lecture's section boundaries out of the source decks before
anything is drawn, the two-diagram shape the user expects, and the rendered-pixel check that catches
box overflows and broken connector gaps before delivery.

**Never introduce a term the user has not met without defining it in the same breath.** This is a
standing instruction, restated at the start of any heavy topic ("remember not to create any words or
terms without explaining them"), so it is not a per-reply nicety. Gloss the term in the sentence that
uses it, in plain words, then use it freely afterwards; if the gloss itself needs a second undefined
term, drop the term and describe the thing instead. Every gloss carries at least one of: a
plain-language phrase, a concrete number, or a tie to the user's own project or source. A definition
made only of other jargon is not a definition.

**When a phrase is your own shorthand rather than the field's, say so and hand over the real name.**
Invented metaphors are the best teaching tool here and they also read as terminology: an image like
"walking up the critic's slope" lands as a concept but arrives as if it were the accepted term. Own it
in one clause — "that's my phrase, sorry; the literature calls this gradient ascent" — and the metaphor
becomes an aid instead of a fake fact that a look-up will contradict.

**When the topic is machine learning or reinforcement learning** (value functions, actor-critic, SAC,
memory-augmented policies, non-Markovian state), read `references/deep-rl-explanation-ladder.md` first:
the rung order, the gloss that lands at each rung, and the quantities that must be computed rather
than recalled.

## Reading displayed mathematics out loud
When the ask is "how do I read these equations/inequalities", do not re-derive — *sentence*
every display, one line at a time, out loud.

- **Frame the whole display first:** the left side is the quantity wanted and unknowable; the
  right side is built only from quantities that are known. If an unknown survives on the right,
  the estimate is worthless — say so.
- **Name the single moving quantity** and collapse the display to it (定理2.30 is really
  $c/(1-c)$ with $c=\operatorname{Cond}(A)\|\delta A\|/\|A\|$), then read the two regimes: small
  $c$ gives back the simpler earlier bound, $c\to1$ kills the bound, and the hypothesis is just
  the statement that you stay inside.
- **State which way every $\le$ points and why** — each step replaces an unknown by a known
  quantity that is no *smaller*, so the chain may only climb. Point out where a denominator moves
  down as the bound moves up (slide 24's last line): that is exactly the step a reader distrusts,
  and naming it prevents the confusion instead of curing it later.
- **Finish with the paper's/deck's own numbers** pushed through the chain by a computation you
  actually ran. Symbols alone never land for this user; real output does.
- **"What is this used for" gets application buckets, each backed by a computation.** Tie them to
  their own domains (robot arm, CAD/FEA, precision motion control, semiconductors/EVs,
  learning-based feedforward) and run a small demo per claim — e.g. a 2R arm's $\operatorname{Cond}(J)$
  and damped-least-squares bias, or the $0.41n^{2}$ growth of an FEA stiffness matrix. When they
  restate the concept ("so it's an error analysis tool"), confirm the instinct and correct the one
  word that matters: it measures the *problem*, not the *calculation*.

## When to use
Any "explain X" / "what does X mean" / "zoom out" / "the heck is X" / "where does X fit"
request, walking them through a paper, or teaching a concept off the back of a project.
Also the **paper↔project** ask — "explain it to me with context with the SRT project", "how does
this relate to what I'm building" — which has its own procedure below.
And when they are **learning a new tool or framework hands-on** (ROS 2, a simulator, a CLI) and stop
mid-procedure to ask a definition question — "what is a topic?", "what is `--no-daemon`?" — which has
its own procedure below.

## Method (in order)
0. **Lead with WHY it matters — real-world applications before mechanism.** When the user meets a
   new paper/tool, give the payoff first ("what real problems does this solve?") before any math
   or jargon. They ask for this ordering explicitly. Then descend: why → what → how → limits.
1. **Anchor and build up; never assume a term.** If a term could be unknown, define it from
   zero first (integrator = an accumulator; manifold = a curve/surface in a space; order =
   how many derivatives deep you model). Then climb. **A mid-lesson "what does <term> mean?" is a
   definition detour, not drift** — it happens in paper walk-throughs exactly as it does in tool
   walk-throughs, and usually for a word *you* used loosely ("score"). Same rule: define it from
   zero, spell out where it sits in the method, then hand the pending rung back verbatim.
   **When the concept is a SET or a SPACE, never define it by what it does — derive it by the count
   that creates it, starting one rung BELOW where it appears.** Defining the null space as "the
   directions that don't move the hand" is a *result*, not a construction: it reads as a magic
   property that some directions happen to have, and the user cannot see where the set comes from —
   they will report being lost even after being told it twice. The version that lands is arithmetic:
   count the controls against the requirements at 1 joint, then 2, then 3 — not enough, exactly
   enough (so there is no freedom at all), one spare (so a whole family exists, and that family IS
   the space). Same move for any kernel, feasible set, solution manifold, redundant-DOF space or
   invariant subspace: show the degenerate case where the dimension vanishes, then add the single
   degree that creates it. Follow immediately with a **body demo** when the concept is kinematic
   (palm flat on a wall, move the elbow — the palm does not move, and that motion is a null-space
   direction), then give the formal definition, then reach for the widget: **make the COUNT visible,
   and give it a control that destroys the space** (add one constraint, the arithmetic drops to zero
   and the slider dies). A drawn region teaches far less than watching the dimension go to zero.
2. **Use the user's go-to physical analogies, matched to the MECHANISM, not the surface:**
   - accumulator = bathtub (rate in → level out).
   - position = the caboose of a freight train (last, laggiest to respond → brake early).
   - overshoot / position-constraint = swing-past-then-pull-back = parking past a wall.
   - bang-bang / ride-the-limits = race-car driver, pedal always floored/braked/neutral.
   - **constraint tightness = a bead pressed against a wire.** A Lagrange multiplier is a *force*,
     not an abstract number. Nothing resisting ⇒ λ = 0; the constraint biting ⇒ λ > 0. It answers
     "how hard is this constraint pushing?" This user is a mechatronics engineer, so the mechanics
     reading lands where a "price" metaphor alone does not — and the force picture makes
     complementary slackness obvious instead of arbitrary.
   **For the dual problem, lead with the FLOOR — it is the one idea that makes `max` stop feeling
   backwards.** Write the Lagrangian as `objective + λ·(violation)`; when the constraint holds the
   violation is ≤ 0, so minimising the Lagrangian can never beat the true constrained optimum.
   Therefore *every λ hands you a guaranteed floor on the answer*, and `max_λ g(λ)` is just
   "raise the best floor you can prove". Weak duality is that inequality, and it is free for any
   problem; strong duality is the floor meeting the answer exactly, which must be *earned* (and is
   precisely what a nonconvex paper has to argue). Do not open with the saddle-point picture — it
   arrives as geometry with no motivation and is why this concept reads as circular.
3. **Untangle conflated concepts with the "two axes / two different X" trick.** Explicitly
   split whatever is being merged before explaining: feedback vs feedforward; target vs
   constraint; imitation vs RL; "who collects data" vs "learning signal"; control vs policy.
   This user reasons by merging analogous things — separate them first. Three shapes recur:
   **two objects sharing one name in different spaces** (the obstacle vs its C-obstacle; the
   configuration vs "the position of all the points"), **a definition read as an identity**
   ("X is a *specification of* Y" read as "X is Y"), and **one word covering a signal, its actuation,
   and the physical result** ("the gripper closed" = the policy's gripper dimension / the servo's
   achieved position / the fingers actually holding the object) — ask which level they observed before
   explaining a cause, since each level has a different fix. Diagnose which one it is as a
   member-vs-set or a recipe-vs-result confusion, then split it with a three-column table —
   *where it lives / its axes / what a point in it means*. The table does more work than any
   paragraph of prose.
   **The fourth shape, and the most common one in a methods paper: one word naming quantities that
   live at different STAGES of the pipeline, or with different AUDIENCES.** Their restates repeatedly
   weld these together, so expect to split one in every correction cycle. The recurring pairs:
   - **built once vs evaluated every step** — a quality score computed while constructing the target
     (does this plan even work?) versus a term evaluated in the training signal every frame.
   - **the target vs the learning signal** — the reference motion the model is told to aim at, versus
     the model's own practice attempts, which is what it actually learns from. The reference traces
     the exam paper; the practice is the study material.
   - **the model's objective vs the number reported to the reader** — the reward the policy optimises
     versus the error metrics printed in the paper's tables. Different purposes, so a gap between them
     is a finding, not an inconsistency.
   - **the plan's validity vs the action's magnitude** — "can this grip hold at all" versus "how hard
     to squeeze". One is a property of the shape, the other of the motors.
   The deciding artefact for every one of these: **does the learned model ever receive this number at
   run time?** If it does not, it shaped the target before training and the model never sees it — say
   so plainly, because their default assumption is that the model consumes every number mentioned.
   **The fifth shape: a list of method names offered as "solutions" to the headline problem.** A slide,
   a related-work list, or a paper's abstract almost never contains N solutions to one problem. It
   contains methods for *relaxations* of it, plus one or two that solve a neighbouring problem instead.
   Split it with a four-column table — *name as given / what it actually solves / is it a solution to
   the headline problem / the measurable difference* — and lead with the **strict test** for the
   headline question, because that is what decides membership. For an agreement or consensus problem the
   test is observable: after the method runs, do all the honest nodes hold *the same* value? A non-zero
   spread between nodes means you are looking at the relaxed version, by design, not at the original.
   Expect **one name to cover two different published algorithms** (same author, different paper — an
   exact protocol and a relaxed one): say which one the list means and how you know, from the company it
   keeps and from the example numbers.
4. **Correct the mental model explicitly, don't layer.** "Not quite" / "the weak link is step
   5" / a before-after correction table. They want to be corrected, not coddled. **Correct your
   own oversimplification the same way:** when their restate exposes a claim you stated too
   generously, say so in the first person, restate the wrong sentence, and replace it with the
   accurate one-liner. Quietly refining it later leaves the wrong version standing as the thing
   they memorized.
5. **Offer an interactive widget for spatial/temporal concepts** — see
   `references/interactive-teaching-widgets.md`. Offer, don't force.
   **When the quantity is only meaningful up to an arbitrary choice, give the arbitrariness its own
   control and let everything else hold still.** This user's default is that every number in an equation
   is a property of the object, so a scale, a reference point or a parametrisation must be shown to be a
   *choice*: one slider that multiplies the arbitrary parameters, plus a readout table that visibly
   splits into the rows that move and the rows that refuse to. That single move carried the whole margin
   argument (multiplying `w, b` by *c* moved `‖w‖`, the functional margin and the objective by *c*, *c*
   and *c²* while the line, the geometric distance *r* and the street `2r` stayed identical), and it
   generalises to any gauge freedom — a potential's zero, a normalisation convention, a Jacobian's
   scaling. Add the mirror move for the object of study: a button that finds the *optimum* of the thing
   the widget draws (widest street, minimum energy), so the abstract objective the deck states in one
   line arrives as something they watch happen. Both belong in the same widget, and the button must
   compute its answer (a real scan/optimisation) — never a hand-placed "good" configuration.
6. **Tie it to a real project only where the link is genuine — then deliberately go OUTSIDE their frame.**
   Their correction (2026-09): *"I think I'm restricting myself by always pointing back to the SRT project."*
   So: name the SRT / SO-101 / motion-lab link when one honestly exists, but **never manufacture one** —
   a forced project link flattens a concept into the one case they already know, and stops teaching.
   After (or instead of) the project tie, reach for **1–2 applications they almost certainly haven't
   considered** — outside robotics, outside their coursework, ideally in a field they've never touched
   (medicine, chemistry, energy markets). Catalogue + how-to: `references/applications-outside-robotics.md`.
   Robotics-lab examples are the *expected* answer; the value is in the surprise.
7. **Close with an offer + a restate invite — and run it as graded cycles.** Set ONE test
   question with a hint, never a quiz battery — except that this user's standing preference is no
   trailing quiz at all, so the test question is skipped unless they asked for exercises. **When the rung is a classification (type A vs
   type B), make the test a borderline case, not a textbook one** — their failure mode is filing
   something under the wrong type, and only a case that could plausibly go either way exercises
   the discriminator. Hand them the discriminator as a two-column table whose first row is *where
   the opposition sits* (one element, two opposite values ⇒ A; two separately measurable
   quantities ⇒ B), plus the artefact that decides it (can this be filled into a lookup table?) so
   their answer is falsifiable rather than a vibe. When they answer, credit what was right in a
   line, then list the corrections in priority order (the user merges separate axes, so the top
   correction is usually "you welded two independent choices together"). **Finish by rewriting their
   whole recap as ONE accurate paragraph** — a bare list of fixes leaves their welded version standing
   as the thing they memorised, and they will recap again a few turns later; the rewrite is what
   replaces it. Then end every reply with the NEXT rung's question — **but read the skips.**
   This user answers one instruction at a time, and mid-paper they are frequently in a rapid
   definition pass: a run of "what is X" questions with every set question passed over.
   - **First one or two skips:** answer theirs first, then fold the pending test answer in as a
     worked example rather than re-asking it.
   - **By the third consecutive skip the question is the wrong shape for the moment.** Stop setting
     them, say so in one plain line, and deliver definitions until the user asks for an exercise.
     Re-setting a question into a definition pass reads as nagging and spends the reply that the
     answer should have filled.
   - **A skipped question is not disengagement.** The reasoning habit often surfaces instead as a
     question the user asks unprompted — reaching from the paper's solver to a method in another
     field and asking whether the resemblance is real. That is the exercise succeeding by a better
     route, so credit it explicitly instead of reading the skips as failure. Its answer is the thing
     worth keeping, not the quiz.
8. **Match length to the ask** — tables for comparisons; plain-English jargon glosses; get to
   the concept, don't pad.

## Walking through a paper (the order that lands)

**First, extract the PDF once and never re-open it.** Dump every page's text to one JSON file with
PyMuPDF (`import pymupdf`; the old `fitz` alias still works but warns). Then build a **heading map**
before reading anything — regex each page for numbered headings and print only those lines, so you
learn the section ranges without reading the paper twice, and can then print just the pages a section
owns:

```python
for pg in pages:
    heads = [l.strip() for l in pg["text"].splitlines()
             if re.match(r'^\d+(\.\d+)*\.?\s+[A-Z]', l.strip()) and len(l.strip()) < 70]
    if heads: print(f"p{pg['page']}: {heads}")
```

Unlike a lecture deck (see the slide-deck section below), a journal paper normally has a real text
layer on **every** page — so a page coming back near-empty is holding a figure or a full-page table.
Render exactly those pages and read them with `vision_analyze`; do not assume the extraction failed.
Keep the JSON file and the extraction script in the paper's project folder, so a later session on the
same paper greps instead of re-extracting.

1. **Why / applications** first (step 0 above).
2. **The research gap** — "what open problem does this fill?" Best delivered as a table of prior
   methods and what each can't do, landing on the intersection nobody covered. **The gap must also
   survive compression to ONE paragraph** — this user asks for the compressed version mid-thread
   ("summarize the gaps for me in one paragraph"), so be able to hand it over verbatim without
   re-expanding it. One paragraph, then hand the pending rung straight back.
3. **State the input modality before the mechanism, as a small table.** This user defaults to assuming
   the method consumes video or pixels. For an embodied-AI / robotics paper the input is usually
   **pre-tracked numbers** (a pose time-series, object trajectories) with no pixels and no language
   anywhere. Answer "text, video, or simulation?" explicitly: what goes in, where the supervision
   labels came from, which stage is learned versus plain optimisation, and where it runs (simulation
   or real hardware). Getting this wrong re-frames the whole paper.
4. **Concepts** from zero, one rung at a time (the rest of this skill).
5. **The mechanism** (assumptions, math sketch) — only after the concepts land.
6. **The full concept inventory, when the ask is "list out all the concepts in it".** That is a
different deliverable from an explanation — they want the *map*, to re-read the paper against. Full
procedure and the grouping that makes it readable: `references/paper-concept-splits.md`. The two rules
that carry it: group the terms by the **job each does in the pipeline** (never one flat list — at 60–80
terms the reading order *is* the lesson), and close with a **splits table** of the pairs that look like
one idea, because this user welds independent axes together and the splits are the part they keep. Then
add a short **"which part is actually new"** table separating the paper's own contributions from the
prior art it borrows from — they read with a supervisor in mind and will ask this. File the full
inventory as a note in the paper's project folder; the chat copy is for reading now, the note for next
month.
7. **Its own limitations, proactively.** Surface what the paper admits it can't do (near- vs
   exactly-optimal, unproven conjectures, analysis deferred to a companion paper, scope limits
   like single-axis-only). The user WILL ask "does it mention what it's unable to do?" — answer
   before they ask; never present only the highlights.
8. **Audit the numbers before relaying them.** Five checks that reliably find something:
   (a) were all rows run under identical conditions — a success rate measured from fixed safe
   initial poses is not comparable to one measured from random starts; (b) did the baselines get
   a matched compute budget — an iteration cap versus a sampling-attempt cap is not matched;
   (c) does the abstract's claim match the paper's own table (a "microsecond" claim sitting
   above a millisecond table is an internal inconsistency worth naming); (d) **does your own
   extraction faithfully pair the rows** — on a two-column paper the automatic PDF text extractor
   silently truncates paragraphs mid-sentence and mis-pairs the rows of a two-series table, so a
   count gets attributed to the wrong row with no visible sign; re-extract the affected pages with
   PyMuPDF (`import pymupdf`; the `fitz` alias still works but warns) and **verify by summing the per-item figures against a total the paper
   states elsewhere**. That sum check is what catches a mis-paired column, and it fails loudly when
   the columns are mixed. Report each as a caveat
   with its evidence; never present a headline number as comparable when the paper's own table
   shows it isn't; (e) **do the rows of one comparison table sit on different axes?** A single
   success-rate column routinely mixes a whole competing *method*, a *solver* swapped into the paper's
   own framework, and an *external framework* — three different questions scored in one column. State
   which axis each row belongs to before quoting any gap between two of them, and count how many rows
   are genuinely testing the paper's own contribution rather than a swap-in.
9. **Application status.** "Is it on real hardware yet?" Check open-source code, citations,
   follow-ups; if it isn't deployed, say so plainly and distinguish a demo from a contribution —
   and say whether code exists to reuse (a MATLAB prototype with no release means "reimplement
   the idea", not "run their code").
This mirrors how they read a paper with a supervisor in mind: gap, contribution, honest limits.

### Filing the paper's notes (the two-file ask)

The read-through habitually turns into a filing request, and it always has the same shape:
*"file this summary in `<folder>/<name> summary.md` — include the overall summary and the concept
explanations; then zoom into the specifics, so the methods and the math, explain the math in deep
detail and file it in `<folder>/<name> math.md`; keep the methods in the summary file; then zoom out
and tell me how this relates to the overall paper, then to the field, industrial robots, the other
papers, and how it can be applied — those stay in the summary."* Treat it as a fixed deliverable
contract, not a one-off:

1. **Two files, split by kind, not by length.** `summary.md` carries the plain-language summary, the
   concept glosses, the **methods**, the zoom-out sections, and the caveats. `math.md` carries every
   equation, every derivation, the notation table and the printed-vs-derived audit. Methods stay out of
   the math file and the algebra stays out of the summary — that is the whole point of the split, and
   they will ask for it again on the next paper. Cross-link them both ways (`[[<name> math]]` in the
   summary's frontmatter, `[[<name> summary]]` in the math note's).
2. **Frontmatter that survives a re-read:** title, the paper's full citation as one line, journal, doi,
   author affiliation (name the lab when it is the user's own supervisor's group), the source PDF's
   vault path, a `math_note` link, tags, date, and a status field.
3. **The zoom-out block, in this order** — it is a rubric they gave, so keep the order: (a) how the
   module relates to *the paper's own argument* — say which parts are load-bearing versus decorative and
   what the headline claim would do without each one; (b) where it sits in the **field** (name the
   tradition: safety filter, options/HRL, layered stack, end-to-end — and what the paper's assumption
   breaks); (c) the **industrial / manufacturing** reading, including the incumbent practice it argues
   against, the assumptions that match a real cell, and the blockers to certification; (d) **the other
   papers**, as two tables — the user's own lab's lineage (what each cited group paper is and how this
   one extends it) and the neighbouring literature it positions against; (e) **how it can be applied**,
   as the whole framework *and* as separable components, ending with what it means for the user's own
   hardware and the gap it leaves open for their own work.
4. **Caveats get their own numbered section**, and it is the part they read closest — the audit findings
   from rung 8, the paper's own stated limits, and any internal inconsistency, each as a claim you can
   defend from the text.
5. **Close the note with a list of concept pages still to be written** (`control-barrier-function`,
   `rrt-connect`, …) plus the links section. The note is then a worklist for the vault, not a dead file.
6. **MathJax in Obsidian:** `$$…$$` and `\tag{n}` render; `\eqref` does not — there are no labels in a
   file of pasted equations, so never reach for it. Unicode from the PDF extractor is fine inline.

**Every number in a filed note must come from a fresh read of the extracted per-page text.** An earlier
chat message in the same session is not a source: quoting a parameter table from from-memory costs a
correction later, and the note outlives the conversation that produced it. Same rule for the paper's own
constants — recompute them (see `references/paper-math-notes.md`).

### When the paper is a survey or review, not a method paper

The rungs above assume the paper did something. A review did not, and the genre changes three of them:

1. **Say the genre in the first lines, before any content.** A survey has no experiments, dataset or
   results of its own, so rung 7 (limitations) is not "what the paper admits it can't do" — it is the
   authors' own per-section list of open problems, and that list is the paper's most useful output.
   Report it section by section (per perception / navigation / manipulation, per chapter), never merged
   into one blob.
2. **Treat every number as a quotation and label it that way.** A survey's results tables are a
   catalogue of other people's measurements, not evidence. Run the survey-audit procedure in the
   `verifying-source-claims` skill (comparability down a column, mixed metric families, same-document
   unit/scale contradictions, reference integrity) and carry the labels into the summary.
3. **Keep the source's own structure visible, and name its organising claim.** For a three-domain
   survey deliver one block per domain — objective → method families → the authors' open problems — then
   state the paradigm thesis the whole review is built around ("perception-driven → cognition-driven").
   That thesis, not any table row, is what a supervisor will ask about, so it must not be buried inside
   a paragraph of method names.

**When the user asks which skills governed an answer, or how it differs from what you would have
produced before**, reply with a per-skill table naming the concrete change each one made — the
structure it imposed, the checks it ran, what it flagged — and keep the honest part honest: say so
plainly when the content did not change and only the provenance, the ordering and the flags did. Never
answer with a bare list of skill names, and never claim a richer summary than the skills actually
produced. This user asks the question because they are building the library, so the answer doubles as
their view of what each skill is good for.

## Relating a paper to one of the user's own projects (the "with context" ask)

When the user asks you to explain a paper *against* their project, the paper's own framing is not
the answer — the mapping is. Procedure:

1. **Read the project's LIVE state before writing a word.** The project root's `AGENTS.md`
   (workspace rules + the live status table), its objective/roadmap doc, and the **latest
   session log**. The log outranks the roadmap and every earlier doc: status lines lag reality,
   and the newest log carries today's numbers. **Never assert a project figure (step count,
   episode count, gate status, what's blocked) from memory or from an older doc** — check the
   log, then quote it.
2. **Locate the paper on the user's OWN scaffold, in their vocabulary, before using the paper's.**
   Lead with which rung of *their* stack it occupies (for the arm work: explicit control / IL / RL)
   and say whether it complements or competes with what they are running right now. "Two halves of
   the same layer, and you only have one" is usually the true and most useful relation.
3. **Give a division-of-labor table:** their task decomposed into layers (decide → plan → time →
   track), which layer the paper covers, which layer is their empty slot. Anchor each cell to a real
   artifact of theirs (a policy's action chunk, a named phase, a specific gate).
4. **Then say plainly what the paper CANNOT do for their task, and why.** A planner that only holds
   collision distance ≥ 0 can never grasp — its entire job is free-space motion, and their task is
   contact. A deformable/translucent target has no signed-distance function to plan against. The
   relation must survive the user's implicit "so does this actually solve my task?" — **overstating
   the connection is the failure mode**, and a paper that merely moves between the places their task
   happens must be described exactly that way.
5. **Flag group lineage in the first line.** When the paper is from the user's own supervisor's or
   lab's group, say so up front and keep "future-lab context" separate from "current-project
   deliverable" — they need to know which hat they are reading it under.
6. **Name the hardware caveat when the paper assumes capability their robot lacks** (e.g. a method
   requiring redundant DOF applied to a 5-joint arm leaves almost no null space to search). This is
   the concrete reason a method is or isn't a drop-in for them.
7. **Park the speculative follow-ons** the paper's own future work suggests (hybrid planner +
   learned controller, learned initializers for the optimizer) as backlog notes — do not propose
   building them. Staged delivery applies here as everywhere.
8. **Still close with a restate invite**, phrased on the part that actually matters for their
   understanding ("why does X matter, and why search there instead of Y?"), not on the paper's
   overall thesis.

## Explaining a topic out of a course lecture deck (slides)

The user's coursework arrives as PDF decks in the vault (lecture notes, prescribed textbook scans,
papers). Their question names one topic — "explain the Byzantine Generals Problem" — and the deck is
the primary source. Decks break the paper procedure in one specific way: **the slides that carry the
content often have no text layer at all**, so an extraction that looks successful returns the title
and nothing else, with no warning that anything is missing. Procedure:

1. **Check the vault first.** If a wiki agent has been ingesting the course, the concept page and the
   source page for that deck already exist. Grep the vault for the topic before re-deriving anything;
   the answer then becomes *the pages to read, plus the gap between them*. Read the source page's
   **Flags** section **before relaying any number from the deck** — it records which slide's figures
   the extractor scrambled and which in-class questions were never recovered.
   **Grep the course's `Assignments/` folder too — the user asks in the vocabulary of their own
   solutions.** A question's wording can be verbatim a section heading in the solutions note they are
   reading ("consecutive transforms", "base-frame transforms"), and that note also names the figure and
   the numbers they already trust. Treat it as the anchor rather than the authority: re-derive its
   numbers independently (rebuild the frame table in numpy, multiply the chain back) and quote the
   agreement, because a faulty solutions note entering an explanation is worse than a slow one.
2. **Locate the slides cheaply — build the whole-deck page index first.** Extract every page's text
   **once** into a JSON file (later calls then never re-open the PDF), then print a per-page map:
   page number, text-layer char count, and the first three non-empty lines. Grep that file with a
   **distinctive fragment** — `yzantine` finds "Byzantine" without the false hits a longer pattern
   collects. Two triage reads pay off immediately:
   - **A slide deck's text layer is thin by nature — threshold at ~120 chars, not 40.** A slide whose
     extract is "title + one fragment" (40–120 chars, e.g. "Linear Separators / Which of the linear
     separators is optimal?") is a *figure or formula* slide, not a text slide. The deck-wide total is
     also a signal: 93 pages yielding ~15.6k chars means ~85% of the content is images.
   - **Do not reuse the paper section's numbered-heading regex on a deck.** Slide titles are rarely
     numbered, so it returns nothing and the deck looks empty. The first-three-lines map is the deck's
     equivalent of the heading map.
3. **Treat a one-line extract as a content slide, not an empty one.** A page whose text layer is just
   the title is the page holding the figure, the equation and the numbers. Render exactly those pages
   (`page.get_pixmap(dpi=150)`, save PNG) and read each with `vision_analyze`, asking for the labels,
   the arrows and the numeric table rather than a general description. **Choose the vision payload by
   slide density.** For sparse, figure-heavy decks, halve the calls by stacking two slides per image
   (`2000×2260` at dpi 150 reads well) and ask explicitly for "top = slide N, bottom = slide M". For
   formula-dense decks, prefer one slide per image with a targeted transcription. If paired reads
   stall, switch to smaller single-slide JPEGs in small batches rather than repeating the same heavy
   batch; keep character-level crops for any disputed glyph.
4. **A slide's formula is usually a raster image pasted on it — and the vision model re-derives it
   instead of reading it.** When a question turns on an equation, do not trust a whole-page or
   half-page read. Pull the embedded raster out of the page (`page.get_images(full=True)` →
   `doc.extract_image(xref)`; `page.get_image_rects(xref)` tells you which raster is the equation by
   its shape — a wide, short one like 879×73 next to the bullet, versus a 949×413 decorative figure),
   then read that image **alone**, magnified 3–6× and cut into narrow overlapping crops, with
   character-level questions ("is the glyph before the log a plus or a minus?"). Require two
   independent reads to agree. Recipe, cross-check protocol and the hallucination tells:
 `references/reading-formulas-from-slides.md`.
 **A FIGURE that is vector art can be read exactly, with no vision call at all — reach for this
 the moment `vision_analyze` refuses a crop.** On this host it times out above roughly a dozen KB
 (a 17 KB render failed, the same figure cut to 8–12 KB read fine), so a whole-page or half-page
 figure is unreadable while tight crops work; before giving up, dump the page's own drawing
 geometry — `page.get_drawings()` yields every segment, every filled arrowhead triangle and every
 text anchor with coordinates, which is enough to reconstruct a kinematic diagram to the
 millimetre. Two traps: handle `it[0]` of `'l'` **and** `'re'`/`'qu'`/`'c'` (arrow shafts are
 often quads rather than lines, so a lines-only pass silently loses them and the figure looks
 like it has floating arrowheads), and pin the **projection** before interpreting anything —
 which page direction is which axis, and whether it is 1:1 — by measuring a bar that carries a
 dimension label (here the 3.5 in bar measured 3.5 in on the page, so page millimetres were true
 inches). Then check the reading by the drawing's own labels: multiply the frame chain you read
 back together and see whether it reproduces the frame origins the figure itself marks.

 **An apparently garbled symbol in homework is usually notation the deck defines.** Re-read the
 lecture for the frame names before calling it a typo: an assignment rotating about `OW` and `OV`
 mixed with `OX`/`OZ`/`OY` reads as a typo until the deck shows `OXYZ` = reference frame and
 `OUVW` = body frame with its left-multiply / right-multiply rule — and then the "typo" turns out
 to be the entire point of those two questions. Same move for a duplicated denominator and a
 letter that is not in the alphabet you assumed.
**When the ask is "explain slides N and M — I don't see the difference between X and Y", the
deliverable is the CONTRAST, and the deck's own worked example is often what hid it.** Run the two
descriptions side by side in a terminal before writing anything. If two adjacent slides print the
*same* matrix or number for two different procedures, the deck picked the one pair of cases where the
two readings coincide — classically, rotations about the **world** axes in order (A, B) equal
rotations about the **body** axes in the reverse order (B, A), so both slides reduce to one product.
Say that coincidence out loud in a line or two: it is usually the entire confusion, and the user
cannot tell "same product, two readings" from "I am misreading the rule". Then re-run the comparison
with **only** the variable under test changed and quote the two now-different results in a small
table. Do not restate the slide's rule — they have read it. Supply the mechanism the slide skips
(for a multiply-order rule: which side the newest matrix lands on, *because* that is the only slot in
which it acts in the coordinates it was written in), then the numbers, then one by-hand check they can
re-run themselves ("the final frame's last-rotated axis must sit exactly where the intermediate
frame's does"). Close with where the rule bites in their own work — a serial-chain transform is
post-multiply all the way, because every joint turns in the frame the previous joints already moved.

**"What's the difference between A and B" is not always two procedures — check whether A and B are two
ways of LABELLING one object before you contrast them.** When they are (consecutive vs base-frame
transforms: the same pose written against the parent link or against the base), the answer must open by
saying they are *not two different operations*, in one line with a metaphor that names the single object
("same pose, two rulers") — otherwise a table of the two sets of numbers reads as two different results
and the user keeps asking. Then, in this order: (a) the notation rule that decodes which one you are
looking at, since the symbols already say it (a leading superscript = the frame the numbers are *measured
in*, a subscript = the frame being *described*); (b) one table of the same quantity in both spellings,
with the numbers from the user's own figure, and a sentence on why the components differ (the parent's
axes are tilted, so the same displacement needs different components — the notation hides that flip
inside the reference frame, which is the whole trick); (c) where each set comes from — one is written by
hand from the geometry or the DH parameters, the other is the running product, and to re-express a
child in an outer frame you PRE-multiply by that frame's transform, while extending the chain at the tip
POST-multiplies; (d) a "which one you actually want" table, including the cheap-inverse asymmetry: the
link form inverts for free (`[Rᵀ, −Rᵀp]`) and the base-frame form needs the whole product reversed, which
is why robots store links and not world poses. **When the new contrast resembles a rule you taught
earlier in the same thread, say which question each answers and that they are not the same rule** —
same algebra, different question — because the user will otherwise reach for the earlier rule and misapply
it to the new pair.

**A companion translation flattens the figure captions, so check it against the original render.**
The vault keeps `<deck-stem>(translated).md` beside the deck page, which is the fastest way to read a
non-English deck — but it collapses each slide's figure text into a single `**Figure text:**` line in
reading order, so which caption sits under which sub-figure is lost. When the question turns on that
pairing (which axis is rotated in which frame, which curve belongs to which panel), render the
original page and read it. Read the `.md`, not a `.pdf` export of it, whose text layer can fail
outright on a long document.

5. **Re-derive every displayed formula yourself before explaining it, and flag the slide when the
   derivation disagrees.** Do the algebra from the definition, then compare term by term. Slides carry
   stray factors, inverted signs and flipped determinant ratios, and a history-flavoured bullet is the
   likeliest place for one. Name which terms differ, hand over the clean derivation as the thing to
   carry, and say whether the deck ever uses that equation again ("it never reappears; the later slides
   rebuild from scratch") so they know what is safe to ignore. Never relay a slide's printed constants
   as derived truth. **For a whole-deck pass, run the worked-example audit in
   `references/deriving-source-proofs.md` on every example, not just a representative one.**
6. **Keep the extraction artifacts OUT of the vault.** `raw/` is immutable and the vault has a fixed
   directory schema, so the deck's JSON, PNGs and extraction script live in a scratch dir outside it
   (e.g. `~/dev/<topic>-deck/`). Give the cache path in the answer: they come back with follow-up
   questions on the same deck, and grepping that JSON beats re-rendering.
7. **Cite the slide numbers you actually read**, as a small table (slide → what is on it), and say which
   slides yielded nothing. The user reads along in the deck while reading the answer.
8. **State what the deck does not say.** Decks omit bounds, derivations and the problem each listed
   algorithm solves. Say plainly which parts of your answer come from the textbook or the classic
   result rather than from these slides — the user is being examined on the course, not on your reading.
   Name the deck's own leftovers too, because those are what they get examined on: the exercise it sets
   and never solves, the "what you need to know" / exam-scope slide, and the strictly decorative asides
   (marketing screenshots, an instructor's side topic) that carry no examinable content.
9. **A bare "explain these slides" is a full-deck pass, not only a summary.** Diff against the
   previous deck before treating repeated pages as new material; map their old slide numbers and carry
   forward verified corrections instead of presenting the overlap as a new lesson. Open with what the
   deck adds and a slide-range map; then explain every block as claim → **why this concept is needed** →
   plain meaning → the one mechanism to retain → its own computed example → the trap or scope limit.
   Close with the revision rules, verified slide corrections, and what the deck does not prove. When the
   user asks why each concept is used, add a compact **concept → job in the method** table so the purpose
   of every named object remains visible after the derivations. A roadmap without block-by-block teaching
   is not completion.
   **When the ask is "summarise this deck, I'll be asking questions"**, deliver in this order: what it is
   (course, lecture number, date, where it sits in the course roadmap) → why the material matters → a
   **slide-range roadmap table** (*slides / block / what it does*) → the one derivation chain to be able
   to retell → the deck's notation traps → what the deck does NOT contain. Then work slide-by-slide out
   of the cached extraction as the questions come.
   **The same ask also arrives as "what is the POINT of this deck, where is it used, and how does it
   relate to the previous lectures"** — three additions for that phrasing: (a) state the **thesis** in one
   sentence, framed as the gap the previous lecture left (a chapter about *computing* an answer becomes one
   about *measuring* it; the deck exists to turn "the error is small" from a slogan into a theorem);
   (b) make the uses a table of **use → the theorem it rests on**, not use → prose, since that is what makes
   it revision material; (c) for each earlier lecture, name the **substantive bridge**, never "it follows on" —
   a stability condition written with absolute values of scalars IS the one-dimensional shadow of an
   operator-norm bound, and a factorisation's positive-minor test IS the algebraic form of "not near-singular"
   that the condition number later quantifies. Carry the earlier decks' unanswered questions forward (a
   red-boxed question can reappear in the next deck and still be unanswered), and finish by naming which
   theorem in this deck exists purely to serve the NEXT one.

Prerequisite: `python -m pip install pymupdf` (plus Pillow for stacking pages and magnifying rasters).
The index / triage / render / stack / equation-image steps are packaged as
`scripts/slide_deck_locate.py`, whose docstring carries the inline equivalent. Reading a formula off a
raster equation: `references/reading-formulas-from-slides.md`.

### Reading a deck linearly: "where is the reason?" and "what is X again?"

Once the deck has been translated and the user is reading it start to finish, the questions change
shape: they are **placement** questions about the page, not requests for a longer explanation. Answer by
the shape of the blockage:

- **"How did you get these numbers?"** — give a raw-input-to-result trace, not the theorem again. Define
  the norm or test being used, calculate it from the source's primitive data, show the actual iterates or
  input vectors, perform the subtraction/component operation, then substitute into the bound. Quote only
  intermediates from a fresh computation. For example, distinguish a vector's infinity norm (largest
  absolute component) from a matrix's infinity norm (largest absolute row sum) before using either;
  otherwise the reader cannot see where the scalar in the final formula came from.
- **"Is the explanation/proof in the later slides?"** — answer with a *map* plus the mechanism, never
  with a pointer alone. Name the slide where the vocabulary is introduced, the slides where the theorem
  bounds it, and the slide where the worked example attains the bound; then say plainly that the deck
  **never proves the motivating example** (a red 原因？ / 说明什么？ is a rhetorical prompt, not a pointer to
  a proof). Hand over the two-line mechanism on the spot — algebraic (the quantity being divided by is
  the same order as the perturbation, so the quotient moves by order 1) and geometric (near-parallel
  rows, so the intersection slides) — so the reader is not stalled for eight slides. Close with the
  deck's own later caveat when it has one (a small determinant is a *symptom*, not the test), because
  that is the claim they would otherwise carry away.
- **"What is X again?"** — X was defined in an **earlier** deck. Grep the vault's pages for the term,
  find the definition/theorem number that owns it, and answer in **that page's notation and numbering**
  (`定理2.14`, `定义2.15`), with its own formula and the properties the course lists. A generic textbook
  version owns a different definition number and reads as a different concept to someone cross-checking
  the page in front of them. Recompute every number you quote in the terminal (a product, a $\log_{10}$,
  a digit count) instead of restating it.
- **"I don't understand slide N in the translated file — what is <English term>?"** — treat it as a
  **defect report about the page**, not a question about the mathematics. The term is usually the
  *translator's* wording for a Chinese term the deck names differently, or a term defined on an earlier
  page and reused here bare. Answer from the source's own definition, then **fix the page at exactly
  that sentence** (gloss + cross-link), re-render its companion PDF in the same pass, and verify the
  edited page. The user is mid-read; the fix is what stops the next stall.
 - **"Why isn't it <the formula I would write>?"** — the user pastes their own version of a slide's
 formula, which means they have *read* the page, disagreed with it, and are showing you the
 alternative. Do not re-derive at them; establish what the page actually prints. Render it and read
 the disputed glyph with two agreeing character-level reads, check the **adjacent slide** for the same
 formula (a deck usually prints it correctly once, and that sibling is the deck's own witness for
 which version is intended), then settle it from the line the formula was derived *from*. Say which
 version is right in the first line of the reply — their version usually is. A misprint in an
 *iterative* formula is falsifiable rather than merely flaggable: build what the printed form implies,
 run it, and quote what the error costs (`references/reading-formulas-from-slides.md`).
 - **"Explain in words how to read the equations / the inequalities on slides N–M."** — the ask is a
  **reading skill**, not more derivation: the symbols are right and the reader still cannot say what each
  display asserts. Deliver a spoken sentence per display in the deck's order, then the reduction that
  turns the section into one idea.
  1. **Give the template sentence once, at the top:** *the left side is the quantity you want and cannot
     compute; the right side is built only from sizes you know.* An unknown surviving on the right is
     what tells them a display is unfinished rather than merely hard.
  2. **One sentence per display, proof steps included**, saying what each line DOES — "expand, cancel the
     unperturbed equation, what is left must cancel to zero"; "divide through"; "replace the unknown
     gain by its ceiling". A step that only rearranges gets one clause; the step that spends the
     hypothesis gets the paragraph.
  3. **Reduce before explaining: find the ONE moving quantity and give it a letter.** A bound written
     `Cond(A)·r/(1 − Cond(A)·r)` is one sentence once `c = Cond(A)·r` is named — relative error ≤
     `c/(1−c)` — and the reader stops parsing a fraction. The extremes then carry the meaning: small `c`
     reproduces the simpler sibling theorem's flat factor, `c → 1` sends the bound to infinity, which is
     exactly what the hypothesis forbids. Compute `c` against the bound on the deck's own matrix (three
     values, one near the edge) and quote the numbers.
  4. **State the direction of every `≤` once, then point at the step that looks like a mistake.** In a
     chain each step may only replace an unknown by something known that is no smaller; the step that
     puts a *larger* number inside a *subtracted* denominator shrinks the denominator and grows the
     fraction — legal for that exact reason, and the step every reader suspects. Name it out loud.
  5. **Close with the sibling theorems side by side** — one flat constant versus the same bound carrying
     a `1/(1−c)` tax, the hypothesis of one being a special case of the other — and say which inequality
     of the NEXT theorem they have already met. They are revising a section, so the comparison row is
     worth more than added depth on any single theorem.
  6. **Then fix the page in place** (reading-recipe callout at those slides + re-render + verify the
     rendered page), exactly as for the defect report above. This ask is the one case where a
     **live-numbers widget is right for a bound**: one row per line of the chain, each row evaluating its
     own left and right side so the `≤` is watched holding, plus a button that drives the state to the
     source's own worst case. The "no widget" rule in the inequalities-and-their-USE procedure is scoped
     to that ask, where what is missing is placement and consequence rather than the reading of the symbols themselves itself.

## Giving a worked example ("use a simple dataset and show me")

When the ask is for an *example* rather than an explanation — "I need an example to understand
this", "classify a chessboard with an SVM and a kernel" — the deliverable is **computed output,
not an illustration**. A hand-drawn plausible table teaches the wrong thing the moment one number
is off, and this user checks.

1. **Fit it for real first, in the terminal**, with what is already installed (`sklearn`, `numpy`,
   `scipy`). Print every number you intend to quote, then quote the printed values. Generate the
   widget's data from the *same* script and embed it as inline JSON
   (`<script type="application/json">`), so the picture cannot drift from the computation.
2. **Order it smallest-to-largest:** a two-point case whose arithmetic they can redo from memory
   first — their own paper check is what convinces them — then the real dataset, then the version
   that *fails*, so the boundary of validity is visible instead of asserted. Name the failure's
   cause (a checkerboard is unreachable for a degree-2 polynomial and for any straight line).
3. **Verify the identity the concept claims, numerically, and quote the residual.** "Rebuilding the
   weights from those three multipliers reproduces the fitted weights to 1e-17" is what makes a
   dual / multiplier / KKT story land. The plot is decoration beside it.
4. **Report the number that means something, and say which number is noise.** Accuracy on 16 toy
   training points means nothing; accuracy on fresh points drawn from the true generative rule is
   the measurement — a model can score 62% on the toy points and 52% on the real pattern. Never
   present a toy-training figure as evidence.
5. **Say it when the demo contradicts the story being taught.** Sparsity collapsed (every point was
   a support vector) because the set was tiny and the penalty large. The honest exception is more
   instructive than the polished case, and it stops them memorising a slogan — "SVMs are always
   sparse" is a property of easy data, not of the method.
6. **Look for the concept's own rules firing at both extremes and measure them.** Every multiplier
   pinned at the cap when the fit fails, none near it when it succeeds, plus the geometry each
   implies. A rule confirmed at both ends is what converts "the slide says" into "I checked".
7. **Audit your own table like a paper's** (rung 8 of the paper procedure). You authored it, so you
   own the comparability caveats — state them in the reply, not in a footnote.
8. **Test whether the documented recipe's steps do anything — the collapse is the best teaching
   line.** When a method arrives as a numbered procedure, do not transcribe the steps; check each
   one's effect. A substitution, fallback or repair step that the final average undoes means the
   whole recipe collapses to something shorter, and that identity is the one sentence that makes the
   method land — "collect the readings, filter the acceptable ones, compute a representative,
   replace the rejects, average" IS "average the acceptable readings", with the residual quoted
   beside the short form. Give the long recipe afterwards, as the bookkeeping the source actually
   specifies rather than as the method.

**When the user relays a critique of your teaching** (usually pasted from another model), check the
pasted artifact before accepting the complaint: copying an answer out of the chat duplicates every
equation (rendered text plus LaTeX source), which reads as "malformed notation" that was never in
the output. Then take the **one structural fix** the critique actually contains, check any proposed
ruleset for a missing length/format governor — rules demanding "every algebraic step, two
applications and three questions" on *every* reply legislate the unreadable density the user
complained about — and merge into the existing skill rather than replacing it.

## Profiling a method (what it is → what it's for → how it relates → the algorithm)

The ask recurs in exactly this form: *"tell me what it is, what it's used for, zoom out and tell me how
it relates to the others, then give me the step-by-step algorithm."* Answer in that order — it is the
deliverable, not a preamble to one. A follow-up *"can you do the same for X?"* means reuse this
skeleton and the same checks, not invent a fresh shape.

1. **What it is** — one paragraph, and make the *representation* the content (a factorization, a basis,
   a decomposition), then say which parts of it are free and which are computed. "It is Doolittle
   restricted to a tridiagonal matrix, so both factors are bidiagonal and the superdiagonal survives
   untouched" beats any amount of mechanism.
2. **What it's for** — a use → why-this-is-the-tool table. Always include the **reuse** case
   (factorize once, many right-hand sides) and the honest **scope limit** (the band width, the
   symmetry, the size at which it stops being the right tool).
3. **How it relates — name every relation in words. Never one bare arrow across a list.** A single `→`
   spanning six relationships silently carries six meanings, and the user will stop the lesson to ask
   what the arrows mean. Label each edge by its kind, and say which kind it is:
   **identical computation** (Gauss elimination ↔ Doolittle: same arithmetic, two names — the naming is
   what makes reuse possible); **restricted case** (chasing and Cholesky are Doolittle with stricter
   hypotheses and thinner factors); **repair that widens the class** (pivoting drops the Δᵢ ≠ 0
   hypothesis by factorizing a permuted matrix); **same object renamed** (Doolittle ↔ Crout ↔ LDU);
   **contrast, sharing only a goal** (direct vs iterative). When a containment is *exact*, show it with
   the actual identity and verify it numerically before claiming it — Cholesky's L IS Doolittle's L
   with column j scaled by √u_jj (checked on the deck's own SPD example).
4. **The algorithm** — numbered steps in the order the method must run them, each with its formula,
   plus *why that order* (which quantity has to exist before the next step divides by it — the row of
   U before the column of L, because the division by u_kk needs u_kk). Then the costs, then the code.
5. **Run it before writing it.** Implement the method in the terminal and reproduce the source's own
   worked example — the printed factors, the intermediate vector, the answer, the residual — and quote
   the check rather than the derivation. Verify the structural claim too (for LU: L@U == A, and U's
   superdiagonal equals the original in the tridiagonal case). This is what turns "the slide says"
   into evidence, and it is how a source's own misreading gets caught.
6. **Give the honest caveats with operation counts, not clocks.** Compare in counts (chasing 8n−7 vs
   dense (n³−n)/3) and give the **crossover where the constant factors still favour the naive method**
   (n ≤ 4, so chasing only wins from n = 5). Say outright when a wall-clock number *understates* the
   algorithmic gap — a pure-Python loop against vectorised LAPACK did. A method that is not better at
   every size is the interesting fact, not a footnote.
7. **"How did we get this formula?"** — do not restate the formula. Expand the full sum from the
   definition of the operation, apply the factor's sparsity to kill the terms one at a time, and
   **name which structural property did the killing** (a zero triangle stops the sum at one index; a
   unit diagonal turns the last remaining term into the unknown). Then check it on the source's own
   numbers. Close by tying the structural property back to the existence condition the user already
   met — "the u_kk you divide by are the pivots, so dividing is legal exactly when Δᵢ ≠ 0".
   8. **Close a multi-method lesson with a slide-level coverage map when they ask "is that the whole
      lecture?"** They will ask, and the honest answer is a table: slide range → content → *where it was
      covered and at what depth*. Name the blocks you only used rather than derived (the earlier chapter's
      overlap), the one genuine gap, and the boundary of the source itself ("the deck stops at 例2.7;
      iterative methods are a later lecture"). Do not claim full coverage when a proof was only cited —
      the user is checking what to revise, and an overstated "yes" sends them into an exam missing the one
      block that was skipped.

### When the ask is anchored to one of the user's own solved questions

*"Explain the chasing method with the context of question 10's solution."* Same order as the profiling
skeleton, with five additions — the anchor changes what has to be supplied:

1. **Derive the recurrences from the first line of the system; never hand them over as given.** A formula
   stated is memorised; the same formula reached from "row 1 has no $x_0$, so divide it through by $b_1$"
   is retained, because the user now knows *why* that row is the special one. Two lines of substitution
   produce the pair of recurrences — and naming what the denominator IS (the pivot of the elimination)
   converts two unexplained formulas into Gauss elimination seen through a keyhole.
2. **Explain the method's name once, and make it the shape of the algorithm.** "Chasing" is the forward
   sweep marching down the matrix then the back sweep retracing: one sentence, and the two passes are
   remembered as one object instead of two loops.
3. **Prove the pattern; never write "the pattern is clear".** Three terms is a guess, and this user asks
   whether it holds. Run the induction on the pivot, close it on the base case, and say that the
   induction closes. Where a closed form can be substituted back into the recurrence, do that instead of
   a third numeric step.
4. **Then answer "why does the answer look like that?" from the operator's own structure** — the rung the
   profiling skeleton lacks, and the one that makes the numbers mean something. The matrix IS the
   second-difference operator; a second difference annihilates straight lines identically, so the interior
   equations impose no shape at all and the source term alone fixes the slope. The answer is a ramp
   because it cannot be anything else. Verify the annihilation numerically on the answer itself and quote
   it (`2x_i - x_{i-1} - x_{i+1} = 0` at every interior row), then say what the answer *is* in the source's
   language — a unit impulse at node 1, so the response is the discrete Green's function.
5. **Close on the identities between questions in the same set.** The user is revising a set, not one
   problem: here the chaser's denominators are the same ladder as the positive-definite test's leading
   minors ($p_i=\Delta_i/\Delta_{i-1}$), and chasing a symmetric tridiagonal system is the same algorithm
   as the dense Cholesky question. Naming those two is worth more than any added depth on the method
   itself, and it is what makes the material read as one body rather than eight answers.

## When the concept still hasn't landed (two follow-up asks with fixed shapes)

Both arrive *after* a correct explanation, so both mean the previous answer was in the wrong SHAPE,
not too short. Neither is answered by explaining the concept again — and re-running the same
explanation longer is the failure mode to avoid.

### "What do these inequalities mean, and how are they USED?"
The user pastes the page back and says they don't fully understand it. The previous answer defined the
objects and stopped, leaving no consequence attached.

1. **Name where the page sits** in one line — which slide, which definition or theorem — so they know
   which rung they are standing on.
2. **Decode the display into its halves, one table row per half, and label what each half COSTS.** In a
   two-sided inequality chain, one direction is usually free and the other carries a constant or a
   hypothesis; the mechanism of the constant goes in one clause (n terms each at most the max → the
   factor n; the corners of the unit ball → √n). State which half is the strong claim.
3. **Then the "how it's used" list — numbered, 3–5 items, each ending in a number you computed.**
   "It lets you transfer bounds between norms" does not land; "at n = 10⁶ a per-coordinate tolerance of
   1e-6 permits a 1-norm error of 1" does. Prefer uses stated in the user's own units — a per-joint
   spec versus an RMS budget, a DOF count, a convergence threshold.
4. **Close with the two reading traps** — what it is *not*: the bound is sharp (attained at the worst
   case), not an approximation; and a result should be *stated* in the smallest norm you can prove it
   in, because that is the strongest claim.
5. No widget and no diagram for this ask. What was missing is placement and consequence, not picture.

### "Show me an example of it being applied as part of the solution steps"
The construct is machinery — it turns up inside a proof or a formula and the user cannot see what work
it does. The deliverable is a **numbered procedure in which the construct is one step**, not a clearer
definition of the construct. (The dataset-example section above is for *fitting a method to data*; this
is for *placing a construct in a pipeline*.)

1. **Pick the physical case where the construct is unavoidable, and say why it is unavoidable there.**
   A Jordan form belongs to *critical damping* — the repeated eigenvalue that leaves only one
   eigenvector — not to an abstract 2×2. Anchor to the engineer's canonical instance of the pathology.
2. **Number the steps 1…N and mark where the construct enters** ("Step 3 — the check that tells you to
   use it"; "Step 5 — it appears here"). The question is *where in the pipeline*, so the answer has to
   be a pipeline.
3. **Show the step immediately before it FAILING.** The eigenvalue-only step must visibly run out — two
   initial conditions, one solution. That wall is what makes the construct necessary instead of
   decorative; without it the example reads as a technique someone happened to like.
4. **Verify every step against an independent implementation** (`scipy.linalg.expm`, `np.linalg.eig` for
   the multiplicities) and quote the agreement, then apply the initial condition and quote the closed
   form against the numeric values.
5. **Close with the contrast case where the construct is ABSENT** — a two-row table: the normal case
   (distinct eigenvalues ⇒ a plain sum of exponentials, no extra term) beside the exceptional one. The
   contrast answers the silent "so when do I actually need this?" and is what makes the exception stick.
6. **Then show the same pattern in the source's own use** — the theorem in their lecture is this same
   procedure run as a proof, or the next chapter is where the construct pays off.
7. Keep the honest caveat attached when it applies: a proof tool is often not an algorithm (a Jordan
   form is ill-posed to compute, which is why real software uses Schur/QR instead).

### "Rewrite it using only the notation from the slides"
The third shape, and the only one that arrives as a *rewrite* request rather than a question. The
concept explanation was sound and the user still cannot follow it, because **the symbols are not the ones
in their own source**: your shorthand compressed the source's arrays (a method the deck writes with three
sequences, delivered as two), and the user — reading the slide beside your answer — finds none of the
symbols you used and concludes they are looking at a different method. Nothing about the content is
wrong; the letters are.

1. **Read the source's own presentation, then rebuild on its route as well as its letters.** If the deck
derives the factors by multiplying the decomposition out and matching entries, derive it that way rather
than by the equivalent substitution you personally find shorter — the reader holds two documents side by
side and checks them line by line.
2. **Open with a reading guide**, one row per symbol in plain words, so the answer can be mapped onto the
slide without holding both. Name what each symbol *is* in the method, not just what it is called.
3. **Retire the old symbols completely.** Grep for them and require zero hits — a single leftover
paragraph re-triggers the confusion. Where one of those letters also does a second job elsewhere in the
same answer (a slope, a summation counter), rename it rather than leaving the reader to disambiguate: two
meanings for one letter is exactly the collision they cannot see past.
4. **Say plainly that the shorthand was yours and that this is why the source looked unfamiliar.** The
user has been sitting with the mismatch long enough to doubt their own lecture notes; naming the cause is
part of the fix.
5. **Where the source ships its own worked example of the same method, run the comparison in its
notation** — the same formulas on the slide's numbers, plus the clause naming why the exercise's numbers
collapse into clean patterns where the slide's do not. That is what turns the rewrite into extra evidence
rather than a translation.

**General rule:** when the user says they are still confused, the earlier answer supplied the object but
not its **placement**, its **necessity**, or the **symbols their own source uses**. Fix those — and
before re-explaining anything, diff your notation against the source's, because a rewrite request names a
mismatch that more explanation in the same letters cannot close. Do not re-explain the definition.

## Teaching a new tool or framework (hands-on, not a paper)

When the user is learning a *tool* — a middleware, a simulator, a CLI — rather than a paper's concept.
They will interrupt the procedure to ask what a term means, and the answer only lands when it is tied to
the system they are actually running.

1. **Teach against their own live system, never the tutorial's toy example.** Ground every concept in a
   measured fact from their running stack (a topic with zero publishers, two topics carrying an identical
   message type, their own QoS settings, their own timing) pulled live. A tutorial's turtlesim keeps the
   idea abstract; their own robot makes it checkable.
2. **Measure before explaining.** Run the command and read the real number (a flag's timing, an exit code,
   what a service returns) instead of quoting documentation — the explanation then carries evidence, and
   the measurement is also what catches the cases where their box does not behave as documented.
3. **Expect the definition detour and protect the thread.** A "what is X?" for a term *you* used is not
   drift and not a challenge — answer it completely, in their style, then hand back the exact pending
   command so the procedure resumes where it stopped. Never answer it with a pointer back to the step.
4. **Split the tool's own vocabulary when it collides.** Framework names conflate tiers exactly as paper
   vocabulary does (topic = the channel vs message = the payload vs command = a *role*; publish vs call).
   Apply the three-column split from step 3 as soon as the collision appears — that is where their model
   breaks, and they will ask about it.
5. **Offer the next-step menu once, recommend one, then follow their pick.** They may deliberately choose
   the learning path over the fastest unblocker; re-asking or re-pushing the branch you recommended reads as
   not having listened.

## Standing preferences (always-on for this user)
- Analogy-heavy, jargon-glossed ("high-schooler with key terms kept"), plain-English.
- **Plain English is the default, not a fallback (user instruction, 2026-09-16).** Short sentences, one
  idea per paragraph, and no coined vocabulary used bare. The failure that triggered this: a lesson
  carried by the invented labels *load-bearing assumption*, *incidental* and *welded axes* — all three had
  to be retranslated mid-lesson and derailed the exercise. Gloss any needed label in plain words in the
  same sentence it first appears, or drop the label and describe the thing instead.
- Tied to their real code/hardware and the source paper — *where the link is real*. Don't anchor every
  explanation to SRT; see step 6. A surprising application from another field beats a forced project tie.
- Wants conceptual correction in their own words; staged delivery (park implementation as a
  note unless they ask to build it).
- **No trailing test question unless the user asked for exercises** — this overrides the "set ONE test
  question with a hint" step above. The user's standing preference is that a reply answers the ask and
  stops; when a question has been skipped two or three times, or was never requested, do not re-set it.
- **When the source is a course taught in Chinese, print the course's own term beside each concept it
  names** (主元 pivot, 残量 residual, 条件数 condition number), so the lesson maps onto the lecture they
  are revising from instead of floating free of it. **The condition is "the ask is anchored to the
  Chinese source"** — the user's copy of the deck, its worked example, the lecture being revised. A bare
  conceptual ask ("explain Kalman filters") is not anchored, and the vault's bilingual pages must not
  donate their Chinese column to it; 卡尔曼增益 in an English reply reads as invented vocabulary.
- **Ground a course-topic explanation in the numbers their own machine produced.** When the lesson
  follows work the user just ran (their MATLAB output, their fit, their plot), read the concept off
  those values — the same figures they already have on screen, now interpreted. A textbook's numbers
  make the lesson unverifiable; theirs make it evidence, and one arithmetic bridge from a toy case to
  their measured number does more than any additional analogy.
- Don't over-format or pad. **But drop to full ELI5 on request:** when they say they've lost
  the thread of a paper, or ask to have it "re-explained like I'm 5", they want the
  `session-focus-guard` recap (goal / covered / parked / next) *plus* a zero-jargon re-tell of
  everything covered — narrative, short sentences, one idea per paragraph, no term they haven't
  already met. Deliver both; the recap alone leaves them stranded in the jargon they got lost in.

## Answering "explain these notations" (the glossary contract — user correction, 2026-09-24)

When the user points at an equation and asks what the notation means, the answer is a
**lookup list indexed by the equation's own tokens, in reading order** — not an essay.
The failure they called out by pasting a model example they found easier: the reply was
organised by the *argument* being made (why the source is loose, where the idea reappears,
what to be ready for), so the symbol they asked about had to be hunted out of prose.

1. **One token per line, in reading order:** bold symbol → what it is in plain words → why
   it is there. One idea per line; nothing else on that line.
2. **Everything that is not a symbol goes in a short block after the list** — one paragraph
   of "what the whole equation says", then any caveats. Never interleave with definitions.
3. **No forward references** ("this comes back on slide 46"), no bookkeeping (slide numbers,
   extraction paths, verification narration), and no trailing test question, unless the ask
   was for those.
4. **Define from zero in the line where the symbol appears.** The list must stand alone — do
   not lean on a label coined earlier in the session ("the street", "the gauge").
5. **Short sentences.** One clause per line. No em-dash aside buried inside a definition.

Cost of this format: it hides nuance, and the generic version of it contains loose claims
(calling `wᵀxᵢ` "the decision boundary equation" is wrong — the boundary is `wᵀx+b=0`).
Keep the nuance; move it below the list instead of dropping it.

**When the ask is ONE letter — "what is $k$ in the Cholesky decomposition?" — the answer is its RANGE and
the identity it comes from, not a gloss of the letter.** The user is not asking what the symbol denotes;
they suspect it is a special constant of the method, and "it's the summation index" leaves that suspicion
standing. Supply, in this order: the entry-wise identity both formulas are solving
($a_{ij}=\sum_{k=1}^{\min(i,j)}l_{ik}l_{jk}$ — the dot product of two rows of $L$, terminating at the
smaller index because $L$ is triangular); the reason the sum stops where it does (the $k=j$ term IS the
unknown, so it moves to the other side — which is why there are two formulas and not one); **that the
letter is a dummy and can be renamed**, the single fact that retires the "special constant" reading; and a
table walking $k$ through the user's own matrix entry by entry — one row per $l_{ij}$, the range the sum
runs over, what it evaluates to. State the degenerate case explicitly: the first column's sum is empty,
which is why $l_{11}=\sqrt{a_{11}}$ looks like a separate rule and is not. Close by checking whether the
same letter carries a different job elsewhere in the same document (in a solution set, $k$ also numbers
eigenvalues in $\lambda_k=2-2\cos(k\pi/4)$) and say which is which — two meanings for one letter is exactly
the collision this user cannot see past.

**Get the glyphs right BEFORE writing the list — a paper's text layer garbles mathematics.** The
extractor linearises two-dimensional math into a token stream and silently DROPS calligraphic
letters: an objective `𝒥_s` comes back as a bare `s`, a weighted norm's `𝒲_k` as a bare `k`, and a
null-space basis `𝓔_task` as nothing at all. Nothing warns you. A glossary built on that extraction
defines the wrong symbol with total confidence.

- **Locate the equation by its NUMBER, not by its content.** `page.search_for("(16)")` gives the
  number's bbox; the body sits just left of it. `page.get_pixmap(dpi=600, clip=Rect(...))` renders a
  tight crop that is legible at glyph level.
- **Ask the vision model a character-level question and require agreement.** "State the EXACT letter
  and its subscript; if the glyph is unclear, say so." Use the crop for glyph identity and the text
  layer for which symbols exist and what the prose calls them — neither alone is reliable.
- **Never read mathematics off a full page.** A whole-page read returned `J_c` for a symbol a
  600-dpi crop shows unambiguously as `𝒥_s`, and on another page placed an objective function where
  a null-space basis matrix belongs. A magnified crop is authoritative; a page-scale read is a guess.
- **Report genuine symbol drift as printed rather than normalising it away.** Papers really do print
  two letterforms for one quantity (italic `D_o` in prose, calligraphic `𝒟` in the equation) and
  really do print a transposed abbreviation (`KF` for forward kinematics). Say "as printed", gloss
  the meaning, and do not silently repair the source.

Recipe: `scripts/paper_equation_crop.py`.

**Before defining a symbol, count its occurrences in the user's own materials — a ZERO hit is the
answer, not an empty search.** They ask about notation they met somewhere in their reading, and a
hit count across the sources they actually hold (the assignment PDF, the course deck, the tutorial
translation, the paper) is the first move, because it settles whether the question is about a symbol
in front of them at all. Two facts fall out of it:

- **The hat is a universal convention; the tilde is not.** x̂ is an estimate, always, and it is the
  carat that carries the state: diacritic-free x is the unknown truth, a "−" superscript is the
  predicted/prior estimate, no superscript is the updated/posterior one. Quote the source's own
  sentence for this when it prints one. Tilde, bar and prime are **author-local shorthand** with no
  standard meaning, so the only authority is the defining line in that document. Its three usual jobs:
  the estimation error (x̃ = x − x̂), the innovation / measurement residual (ỹ = z − h(x̂⁻)), and the
  nominal point a linearisation is taken about (x = x̃ + δx). Their own tutorial writes the estimation
  error as e_k ≡ x_k − x̂_k, i.e. the same object with no tilde — which is why "what does the tilde
  mean" has no transferable answer.
- **A lookalike `~` between a variable and a distribution name is a verb, not a modifier:** `x ~ N(μ, σ²)`
  reads "x is distributed as". In any Gaussian-heavy course this is the likeliest thing the user
  actually saw, and answering it as a decoration on x sends them looking for a definition that does
  not exist.

Then anchor the answer to the symbols their own materials **do** print (the assignment's z, p⁻, P⁻ and
its plain `e` for the innovation; the deck's own name for z − x̂). A glossary that only explains the
absent symbol leaves them hunting a page that never had it. When the ask compares two symbols rather
than defining one, open with a **comparison table** — one row per symbol: whose convention it is, and
what it means — and put the jobs in prose after the table, since the deliverable is the discriminator,
not a lookup list.

**General rule this generalises to:** lead with the deliverable the ask names (a notation
list, a number, a verdict) in the shape they expect to read it, and put teaching extras
after it. Density, not length, is the failure mode — three clauses in one line is harder to
read than three short lines.

## Delivery gate (run before sending any explanation)

The rules above are prose, so they get compiled away at write time. Before sending an explanation, run
these four checks; if any fails, rewrite rather than trim. Trigger case: a bare "explain Kalman filters"
ask came back carrying the Chinese glossary of the bilingual vault page and four applications the user
had never met — while the vault's own page on the topic opens with a plain-English sentence and glosses
`K` and *innovation* on first use. The notes were better than the reply.

1. **One example, reused.** The first concrete example carries the whole explanation, and a second is
   allowed only once the first is exhausted. A general ask gets exactly one.
2. **Every term glossed in the sentence where it first appears, in ≤8 plain words.** If the gloss needs
   more than one clause, the term isn't needed — describe the mechanism instead. Invented labels are the
   recurring failure (*load-bearing assumption*, *welded axes*, *dimmer switch*, "the gain is the
   bandwidth"); the user has to retranslate them mid-lesson.
3. **No non-English term unless the ask is anchored to that language's source** — see the course-term
   rule and its condition above.
4. **Project/assignment mapping goes in one clearly-marked section at the end**, and only when the ask
   touches the project. Answer the asked question first: the user's own numbers are the payoff for a
   course question and noise for a general one.

**Default length is the short form:** target under ~500 words for "explain X to me", short lines, one idea
per paragraph. Long form — derivations, tables of limits, failure modes, the source's own worked example
walked in full — only when asked ("go deep", "full version") or when the ask is explicitly a lecture/deck
pass. Depth is what they like *after* the concept lands, not instead of it.

**Self-check that catches all four:** list every term you used that the user has not met, and every
example you used. Either list longer than 1 on a general ask means rewrite.

## Pitfalls
- **Compressing a vault page into a reply drops operators.** Paraphrasing a note is not re-deriving it:
  a summary of the Kalman page wrote $K_\infty\approx Q/R$ where both the note and the arithmetic say
  $\sqrt{Q/R}$. Recompute every number and formula you carry across from a note, and drop any figure you
  cannot reproduce from the stated inputs — an unverifiable number costs more trust than it buys.
- **Don't get pulled off the session's main thread.** The user will spin off into adjacent
  topics while learning (e.g. mid-paper they pivoted to the arm/ROS2/RL/sim-to-real). Park
  each tangent in the project tracker / a note, then re-anchor — "back to the paper." They
  value being brought back AND the tangent being parked, not lost. One rung at a time, then
  check understanding.
- **Never frame a method in the vocabulary of the assumption it removes.** Teaching something
  whose whole point is to *replace* a default model, using that default model's own words,
  re-installs it — describing a contradiction-resolution method as "the parameter you're willing
  to see get worse" reads as "what you give up", and the user then answered with the trade-off
  framing the method exists to kill. Coin the framing sentence from the new method's side ("a
  constraint you refuse to concede") and check the restate for the old vocabulary. They memorise
  your sentence, not your intent.

## Support files

- `first-principles-thinking` skill — the user is training first-principles reasoning and wants it
  as the **default critique mode**. After a concept explanation, end with ONE strip-and-rebuild rung
  from that skill rather than a second explanation of your own.
- `references/interactive-teaching-widgets.md` — when and how to offer a widget; see the
  `interactive-concept-widgets` skill for the build and browser-verification rules.
- `references/applications-outside-robotics.md` — the surprise-application catalogue for step 6.
- `references/paper-concept-splits.md` — the concept-inventory procedure (group by pipeline job) plus
  the catalogue of recurring "looks like one thing, is actually two" splits in a methods paper. Load it
  on any "list out all the concepts" ask.
- `references/triz.md` — teaching notes, vocabulary, verified data source and separation axes for
  TRIZ / contradiction-based invention. Load it when the topic is TRIZ, inventive problem solving,
  or cross-domain solution transfer.
- `scripts/slide_deck_locate.py` — build a per-page text index of a deck PDF, grep it for a topic, flag
  the image-only slides, render them singly or two-per-PNG for `vision_analyze`, and pull the embedded
  raster out of a formula slide (optionally magnified). Run it before answering any question that cites
  slides.
- `references/reading-formulas-from-slides.md` — how to find and read a slide's raster equation without
  the vision model silently re-deriving or repairing it, plus the cross-check protocol and the
  hallucination tells. The journal-paper counterpart (vector text layer that silently drops
  calligraphic glyphs) is the glossary-contract section above.
- `scripts/paper_equation_crop.py` — crop a labelled equation out of a paper PDF at glyph-readable
  resolution: build a per-page index with the equation numbers, locate `(2a)` by number, render a
  tight 600-dpi crop for `vision_analyze`. Run it before writing any notation list or reimplementation.
- `references/paper-math-notes.md` — the procedure for the `math.md` half of a filed paper note:
  per-page text extraction, reading equations by number with block geometry as a second read, deriving
  every equation and auditing the printed forms, and the shape of the finished note. Load it on any
  "write up the methods and the math" or "file the math" ask.
