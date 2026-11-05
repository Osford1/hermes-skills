---
name: cross-domain-ideation
description: "Source ideas and prior art from outside engineering."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ideation, analogy, biomimicry, patents, prior-art, cross-domain, innovation]
    category: research
    related_skills: [grounded-citations, scholarly-api-sourcing, blocked-page-recovery, spike, reddit-reading]
---

# Cross-Domain Ideation

Deliberate retrieval of solutions from **fields that are not yours** — biology, art,
craft, music, sport, medicine, history, toys, food — and the engineering discipline to
move one in without fooling yourself. Two directions: import (other field -> your
problem) and export (your engineering practice -> someone else's field).

This skill does not generate ideas by vibes. Every donor claim carries a URL, every
candidate carries its cheapest falsification test, and surface analogies are rejected.

## When to use

- "Is there something outside engineering that already does this?" / "who else solves this?"
- Biomimicry / bio-inspired, nature-inspired, or art-inspired design requests
- Stuck on a mechanism, joint, seal, damper, gripper, latch, packaging, sensor, layout, or airflow problem and want an unfamiliar starting point
- Prior-art sweep before building or publishing (does another industry already do this?)
- Reverse direction: applying control systems / precision engineering / metrology practice to a craft, art, sport, or lab process

**Don't use for:** conventional literature review in your own field (`scholarly-api-sourcing`, `arxiv`); product feature brainstorming where the method is already known (use `spike`); decorating a concept with a nature metaphor for a slide deck.

## Prerequisites

- `python` on PATH (script is stdlib-only). Verified with Python 3.11.
- `web_search`, `web_extract`, `browser_exec` (AskNature and other Cloudflare-walled
  donor databases only render in a real browser).
- **China/GFW:** `patents.google.com`, `worldwide.espacenet.com`, `patentscope.wipo.int`,
  `archive.org` are unreachable without the local proxy. Add
  `--proxy http://127.0.0.1:7897` to `curl`. `api.openalex.org` works either way.

## How to run

```bash
S=~/.hermes/skills/research/cross-domain-ideation/scripts/ideas.py   # Windows: "$LOCALAPPDATA/hermes/skills/research/cross-domain-ideation/scripts/ideas.py"

python "$S" add --problem "6-DOF arm cable routing" --donor "luthiery / violin bow" \
  --source "https://doi.org/10.xxxx" --analogy structural \
  --conflict "stiffness vs damping" --mechanism "stick-slip at the bow-hair interface converts
  a slow input into high-frequency excitation — a tunable friction drive, not a gear" \
  --invariants "hair tension constant; relative velocity above slip threshold" \
  --test "spin a bobbin against a felt pad and log torque vs speed" \
  --transfer-cost 2 --novelty-risk 3 --payoff 4 --test-cost 1

python "$S" score     # ranked table + math
python "$S" list --top 5 --md
python "$S" board     # writes cross-domain-ideas/board.html for ::preview
```

Ledger lives in `./cross-domain-ideas/candidates.jsonl` (override `--dir`). Append-only:
never rewrite a row, add a new one.

## Procedure

1. **Abstract the problem into a function + a conflict.** Do not carry a single
   domain word into the search. Write: *"<system> must <VERB + OBJECT + QUANTITY>
   while <CONSTRAINT>, without <PAIN>."* Then name the **conflict pair** (TRIZ-style:
   stiffness/lightness, speed/precision, friction/wear, force/compliance,
   sensitivity/range, transparency/strength, cost/tolerance).
   *Done when:* the problem statement contains no proper noun, no part name, and a
   stranger from another field would recognise the function.
2. **Pick 5-8 donor domains for distance, not depth.** At least one living system,
   one performing or fine art, one traditional craft, one extinct/historical
   technology, one game/toy/hobby, and one non-technical service field (surgery,
   conservation, logistics, cooking). Six biology sub-domains is not a slate.
   See `references/donor-domains.md` (40+ fields, each with what it solves well and
   the words outsiders should search).
   *Done when:* the slate spans 5 distinct top-level categories.
3. **Search in donor vocabulary, using the donor's own databases.** Function words
   retrieve the donor.
   - Which fields already publish on this function: OpenAlex `group_by` (playbook §1).
   - Other industries that already reduced it to practice: Google Patents **scoped to a
     CPC section you don't work in** (playbook §2) — the highest-yield cross-field move.
   - Living systems: AskNature function search in the browser (playbook §3).
   - Craft/art/object donors: V&A and Met collection APIs (playbook §4); old trade
     manuals and mechanism catalogues from archive.org (playbook §5).
   *Done when:* each of the 5-8 domains has at least 3 retrieved donor candidates
   with a URL, or is explicitly marked "nothing found".
4. **Extract the mechanism, not the metaphor.** One line per hit:
   *donor system -> the physics/mechanism that resolves the conflict -> what it costs
   the donor.* Label every candidate `structural` (the mechanism transfers) or
   `surface` (it only looks alike). Reject `surface` — record it, don't pursue it.
   *Done when:* every surviving candidate names a physical effect, not a resemblance.
5. **Transfer audit — the gate that stops expensive nonsense.** For each survivor,
   test the analogy against the mismatch axes and write the **invariants** (what must
   stay true for the mechanism to still work) plus the **cheapest falsification test**:
   | Axis | Ask |
   |---|---|
   | Physics regime | Re, We, Bo, Pe — does the mechanism survive at my size/speed? (gecko setae and lotus effects die at manufacturing tolerance) |
   | Materials & process | Can my process make it, at tolerance, at cost, at volume? |
   | Environment | Dirt, UV, heat, vibration, maintenance interval. Biology self-heals — your part does not. |
   | Control budget | Does it need sensing/feedback I don't have? |
   | Energy & safety | Power budget, standards, failure mode, regulation. |
   | IP | Patented in my jurisdiction and application? |
   *Done when:* each survivor has invariants, a falsification test, and a transfer cost
   (1-5) in the ledger. Prefer the cheapest test that can kill the idea — `spike`.
6. **Prior-art and buy-vs-build check.** Before committing: patents (step 3 scope) plus
   papers (`scholarly-api-sourcing`). Two outcomes matter equally — *blocked* (risk) and
   *already a purchasable part* (shortcut: somebody else's catalogue is a valid answer).
   *Done when:* each survivor is marked novel / adjacent / blocked / buyable with a source.
7. **Score, rank, and deliver.** `score` ranks by composite; the top 1-3 get a named
   next action. Deliverable = ledger + short brief (claim -> mechanism -> invariant ->
   test -> cost), cited per `grounded-citations`. Optionally `board` for a visual
   comparison in chat via `::preview{file=".../board.html"}`.
   *Done when:* every ranked candidate traces to a retrieved source URL, and the top
   one has a falsification test someone could start today.

## Reverse direction (exporting engineering practice)

Same loop, mirror-swapped: the *donor* is your field, the *problem* belongs to an
artist, craftsperson, coach, or lab scientist. Retrieve by their bottleneck (repeatability,
cycle time, scrap rate, unmeasured variability), then translate an engineering discipline
into their vocabulary — SPC and gauge R&R into a ceramics studio; PID and feedforward into
a camera-rig or a musical-instrument tuning process; tolerance stack-up into pattern
cutting; DMAIC into a design studio's review loop. Deliverable here is usually an adapted
*method* plus a before/after measurement, not a part. Keep the measurement — export
without evidence is just consulting talk.

## Quick reference

| Need | Move |
|---|---|
| Which fields publish on this function | OpenAlex `?search=...&group_by=primary_topic.field.id` |
| Another industry already did it | Google Patents XHR, `cpc=` a section you don't work in |
| Nature's version of a function | AskNature `?s=<function>&post_type=strategies` (browser) |
| Craft/art objects as mechanisms | V&A / Met collection APIs |
| Historical and trade mechanism catalogues | archive.org (proxy), 507 Mechanical Movements, Reuleaux |
| Generation checklist when the slate is thin | TRIZ 40 principles / contradiction matrix, SCAMPER |
| Domain practitioners' own words | `reddit-reading`, `youtube-content` on the donor field |
| Blocked page / paywall | `blocked-page-recovery` |

## Pitfalls

- **Searching "biomimicry <my problem>" is the weakest possible query.** It returns
  press releases and consultancy pages. Search the biology directly — functional
  morphology, biomechanics, the organism's own literature — via AskNature functions
  and OpenAlex field groups.
- **Confabulated nature facts.** Model knowledge of biology is full of plausible
  mechanism stories that are wrong or oversimplified (shark-skin drag claims, lotus
  effect on real dirty surfaces). No donor claim enters the ledger without a URL.
- **Surface analogy in engineering clothing.** "Swarm intelligence for our 4-node
  system" — if the physics doesn't change at your scale, the transfer is decoration.
  The script refuses `--analogy surface` without `--force` for this reason.
- **Biology's hidden subsidies.** Self-repair, active cooling, and free material
  synthesis are not transferable; budget for them or don't claim the analogy.
- **Art is not a mechanism library — it is a constraint library.** Steal the process
  (one idea worked hard in many variants, material honesty, iteration against a harsh
  judge), not the aesthetic. Conversely, don't dress a mechanism as art to dodge
  engineering review.
- **Scale and cost kill more transfers than physics** does. Run the transfer audit
  before the prototype, and the cheapest test before the good prototype.
- **Novelty is not usefulness**, and the transfer IS the contribution — so it must be
  measured on your hardware, not asserted from the donor paper. Say plainly what part
  is the donor's and what part is yours.
- **Don't let the donor dictate the target.** Adapt the mechanism to your constraints;
  never copy the artifact (a lobster-inspired gripper does not need a shell).
- **A donor database can return nothing, and that is a result.** Museum APIs are weak for
  mechanism vocabulary; a bare-function OpenAlex probe mostly echoes your own field.
  Record the negative explicitly (in the ledger or the brief) instead of padding the
  candidate list with the closest-looking hit.

## Verification

- `python scripts/ideas.py list --md` returns the expected candidate count and every row
  has a non-empty `source`; surface-only rows are flagged.
- Each ranked candidate has invariants + a falsification test + a prior-art verdict.
- Any claim in the brief resolves to a retrieved URL; unverified model claims are
  labelled as such (`grounded-citations`).
- For exports: a before/after number exists, not just an anecdote.
