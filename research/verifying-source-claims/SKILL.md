---
name: verifying-source-claims
description: "Use when source numbers become your content."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, verification, fact-checking, numerics, ingest, sources]
    category: research
    related_skills: [grounded-citations, ocr-and-documents]
---

# Verifying Source Claims

When you take a number out of a source document and put it into something durable — a report, a
knowledge-base page, a summary, slides, a note — that value stops being the source's claim and
becomes *yours*. This skill is the check that runs in between.

It exists because sources contain typos, and because a plausible-looking digit is
indistinguishable from a correct one once it has been copied. Re-deriving is cheap; the error is
permanent and attributed to you.

## When to Use

- Ingesting a paper, lecture deck, textbook chapter, datasheet, spec sheet or report into notes
  or a wiki
- Quoting a performance figure, error bound, percentage, ratio, spec or calculated date into a
  deliverable
- Any value you are about to state as fact that you did not measure or compute yourself
- Reproducing, explaining or reimplementing a displayed equation, derivation or optimality
  condition from a paper
- Comparing your own earlier output against the current pass ("how does this differ from before?") —
  the earlier run is a source too, so it gets read, not recalled
- Reproducing, transcribing or translating teaching material — lecture decks, lab sheets, tutorial
  notebooks — whose slides print commands and the output they produced. Those printed results are
  claims even when your job is only to carry them into another language

- Persisting a summary you wrote earlier (earlier in this session, or before a context compaction)
  into a note, report or wiki page — the summary is a *recall* of the source, so its figures get
  re-read from the source before they are written down
- **Validating the user's own recap, structural map or study notes against the source** — a task
  whose output is a per-claim verdict, and where every "correct" and every "wrong" you write is
  itself a claim about the source (see *Validating the user's derived structure*, below)

Not needed for values you computed from your own data, or for claims with no numbers in them.

**When the source is an image-only scan, read `references/reading-scanned-sources.md` first** — render dpi,
how a two-page spread misleads OCR, which page number to cite, and how to re-read one table cell.

**When the source has a text layer but prints mathematics — lecture decks, worked examples, typeset numeric
tables — read `references/maths-slide-decks.md` first**: what that layer silently loses (radicals, signs,
matrices, embedded-image equations) and the render-plus-vision order of work that keeps a mis-extraction
from being reported as a defect in the source.

**When the answer depends on the picture rather than the text — which axis is which, where a dimension
starts, which way an arrow points, which label names which line — read
`references/figure-geometry-from-image.md` first**: how to split glyphs from line work so the vision tool
sees a decluttered drawing, how to get label positions to the pixel, the bounded-question phrasing that
survives, and the stopping rule for the part that never converges.

## Procedure

**1. Rank the numbers by load.** Identify the one to three values the source's argument actually
rests on — the final result, the error or amplification factor, the efficiency, the headline
spec. Verify those. Transcribing the rest of a table is fine as long as it is labelled as
transcription (step 6).

**2. Re-derive them with exact or high-precision arithmetic.** Never re-derive using the same
float pipeline whose rounding you might be investigating — that re-creates the error you are
hunting.

- Stdlib `decimal` is sufficient and needs no install: `getcontext().prec = 50`, with
  `Decimal.ln()`, `.exp()`, `.sqrt()` available.
- Reach for the project's own interpreter (the one carrying numpy/scipy) when you need linear
  algebra, but prefer exact arithmetic for anything with a cancellating subtraction in it.
- Write the arithmetic into the artifact so a reader can re-run it — show the factor, the ratio,
  the bound — not just the final value.

**3. Bound the answer independently of the source.** This is the highest-value move, and it works
*even when you cannot know the true value*:

- Derive a bracket from the problem's own structure — sign, positivity, monotonicity, a physical
  limit, a conservation law, or an inequality between two quantities you *can* integrate or bound
  that sandwich the quantity of interest.
- Then test the source's number against that bracket. A value outside a bound you derived from the
  integrand, the geometry or the physics is wrong, full stop — and you can say so without doing
  the hard problem.
- Prefer a bound over a point estimate. A second point estimate that was itself computed tells
  you nothing new; an independent inequality is real evidence.

**4. Classify any mismatch, and say which kind it is in the artifact.** There are exactly three
cases and they need different handling:

| Kind | Signature | What you write |
|---|---|---|
| **Source typo** | wrong by a factor of ten, a dropped or transposed digit, a sign flip — while the method around it is sound | the correct value, flagged as a correction to the source |
| **Under-rounded input** | the source printed a truncated seed and then a chain computed from the full-precision one, so the printed chain is unreproducible *by construction* | say the **magnitude / mechanism** is the reproducible claim, not the digits. Do not accuse the source |
| **Your own error** | your re-derivation disagrees with itself, or with a bound you derived in step 3 | fix it before writing anything, and do not narrate it |

**5. Never silently correct a source, and never repeat a number you could not reproduce.** A
correction is a *flagged* claim with its reason attached. A silent fix destroys the reader's
ability to check you; an unlabelled repeat propagates someone else's error under your name. If it
would not reproduce and you cannot classify it, write "could not reproduce" on the page.

**6. Record the status on the artifact.** One line per load-bearing number: *checked and
matches* / *corrected from X* / *could not reproduce*. This is what makes your write-up worth
more than a copy of the source, and it tells a future reader exactly how much to trust each
figure.

## Reproducing a source's worked example

When the source carries a worked example — a textbook case, a paper's numeric experiment — that
example is the source's own unit test, and reimplementing it is the cheapest verification there is.

1. **Assert the source's printed per-case answers inside the implementation.** Put the expected
   values in the script and fail loudly on mismatch, against a stated tolerance. A passing run
   upgrades the whole table from *transcription* to *reproduced* — the difference between "I copied
   these numbers" and "my code produces these numbers" — and it makes the step-6 status line
   mechanical instead of a judgement call.
2. **Treat a difference confined to the source's last printed digit as rounding, not a finding.**
   The source computed at full precision and printed a rounded result, so your exact value differs
   in the final digit (a printed 2.625 against an exact 34.15/13 = 2.6269). Say "rounding of the
   exact value" and move on; reserve the mismatch table above for differences at the source's own
   precision. Do not report it as a discrepancy, and do not silently adopt either number.
3. **Keep the source's verdict and your own analysis visibly separate in the artifact.** The
   source's numbers matching yours is one claim; what you conclude from running it is another.
   Label yours as yours — otherwise a reader attributes your finding to the source, and a later
   reader cannot tell which sentences would survive the source being corrected.
4. **When the source states its own criterion more than once, execute EVERY reading.** Sources
   restate a rule in two places in wordings that are not equivalent — "within δ of N − t others"
   against "an intersection with N − t others" differ by one member, and the two thresholds return
   different answers on the same data (the looser reading accepts everything, the stricter one
   rejects a correct entry). Do not pick the tidier phrasing, do not average them, and above all do
   not adopt whichever one reproduces the source's printed answers: implement both, print both, and
   record the spread as a finding with its status line. An ambiguity in the source is a result, not
   a reason to choose.

## Non-numeric claims: internal consistency instead of re-derivation

You cannot re-derive a measured, historical or survey quantity. Check internal consistency
instead, and say that is what you did:

- **Additivity** — do the parts sum to the stated whole? Do percentages total roughly 100?
- **Cross-source agreement** — is the same figure quoted elsewhere in the document, or in a
  sibling source? Cross-figure disagreement is a finding, not noise.
- **Claimed precision vs method** — does the source report more significant digits than its
  method, sample size or instrument can support?
- **Derived ratios** — does a stated ratio match the two numbers it is claimed to come from?
- **Round-trip the units** — check the unit conversion and the order of magnitude independently;
  a wrong unit is the most common numeric error that still looks plausible.

## Equations as claims

A displayed equation you reproduce, explain or reimplement is a claim, and it gets re-derived like
any other — but its failure modes are different, because an equation can be wrong in a way that
stays dimensionally plausible and still "works" on the authors' own examples.

1. **Re-derive it from the definition, then compare term by term.** Do the algebra yourself from
   the definition the paper states and diff against what is printed. Expect stray factors, an
   inverted sign, a dropped square.
2. **Check inter-equation consistency: does this equation FOLLOW from the one above it?** This is
   the check that catches the most, and it cannot be done by staring at one equation. Concretely:
   differentiate a printed Lagrangian and see whether it yields the printed optimality condition;
   or ask whether the printed constraint is recoverable from the printed stationarity condition.
   When the pieces of a paper do not compose, one of them is misprinted — and the DOWNSTREAM ones
   are usually the correct ones, because the real numbers were produced by the real formula.
3. **Confirm numerically with a test that would visibly break.** Evaluate the printed form at its
   claimed optimum and check the constraint it is supposed to satisfy. A flagrant violation — a
   norm constrained to ≤ 1 arriving at 2.0 — is proof of a slip, and it costs one line of code.
4. **Classify it and keep the method honest.** A factor-of-two in a multiplier's scaling is a
   *typesetting slip*, the same class as the table-typo row above. Flag it, state precisely which
   equations are affected, and say plainly whether the method's guarantees survive it. A typo must
   not be allowed to read as a refutation.
5. **An absent TERM and an unpriced term are different findings — establish which one you have
   before writing either.** "The loss contains no entropy term" and "the entropy term is there with no
   coefficient on it" are different claims about the same equation, and only one of them is usually
   true: a printed `log π` with no temperature α beside it, a regulariser written but never weighted,
   a penalty stated in prose and absent from the objective. Diff the printed form term by term, then
   write the weaker, accurate version ("present but unpriced, not absent") — the two predict different
   things about a rebuild, so the overstatement costs the reader real work.
6. **The reference list is checkable text: use it when the body declines to name the method.** A paper
   can build on a named algorithm without ever using that family's vocabulary in its own prose. Before
   reporting "the paper never says X", grep the bibliography as well as the body — a cited work's
   **title** is the source's own statement about what it is implementing, and it is quotable. Then
   attribute the framing to the citation rather than to the authors: "the term appears in no sentence of
   the paper; it appears in the title of the work it cites" is the honest form.

### Verifying an optimisation result numerically

When re-deriving a Lagrangian / dual / KKT claim, three traps produce confident wrong answers:

- **`numpy.linalg.pinv` silently DROPS the singular direction.** Evaluating a dual function at
  `λ = -λ_min` therefore returns a finite value where the mathematics gives `-inf` (the term with a
  zero denominator must diverge). Scan the dual strictly INSIDE its legal interval, never at the
  boundary, and evaluate it as the explicit eigenvalue sum rather than through a matrix inverse.
- **Complementary slackness is a free invariant — use it as an assertion, not a curiosity.** Either
  the constraint is tight or its multiplier is zero. In particular an indefinite Hessian makes the
  unconstrained problem unbounded below, so a trust-region / ball constraint MUST come out active
  (`‖w‖² = r²`). If a solve reports it slack, the solve is wrong, not the theory.
- **Get the optimum two independent ways.** Cross-check the argmax of the dual against a direct
  solve of the KKT system, and bound the primal by brute force over the constraint set (sample the
  sphere for a ball constraint). Agreement to ~1e-6 with a dual gap at machine precision is what
  makes a strong-duality claim yours rather than the paper's.

## Auditing a survey / review paper

A review paper's numbers are **quotations of other people's measurements**, so step 2 (re-derive) never
applies and step 3 (bound) usually cannot either. The checks that do apply, in this order:

1. **Name the genre on the artifact, in the first lines.** A survey has no experiments, dataset or
   results of its own, so two things follow: its "limitations" section is the authors' own list of open
   problems (usually the most useful thing in the paper — report it section by section, not merged), and
   every figure carries two layers of provenance, the original author's measurement and the survey's
   transcription. A reader who takes a survey's table as verified results has misread the genre; if you
   relayed the table without the label, that misreading is yours.
2. **Check comparability, not accuracy, in every results table.** Read one column down and ask whether
   its rows sit on the same axis: datasets, model sizes, training regime (training-free vs trained) and
   task definition routinely differ row to row. A single "success rate" column mixing benchmarks and
   parameter counts makes any gap between two rows meaningless — state which axis each row is on before
   quoting one, and say plainly when a pair is not like-for-like.
3. **Check the metric column for mixed families.** An improvement-style entry ("error reduced 35%"), an
   absolute level ("mAP 65%"), a physical unit ("115 mV/N") and a threshold (">= 0.85") in one column
   are four different questions. Sorting the rows into metric families *is* the finding.
4. **Test self-consistency across sections, especially units and scales.** A rate, latency or deadline
   asserted in one section and contradicted by the same document's own requirement in another is a
   flaggable defect — the order of magnitude decides which claim to keep (a microsecond control loop
   wrapped around a large model is not physically available, and the same paper's millisecond
   requirement elsewhere is the consistent figure).
5. **Run reference-integrity checks, and report defects without fixing them.** Two pay off fast: one
   citation number attached to two unrelated works in different sections, and the same work listed
   twice under different numbers. Both are defects in the source — flag with the location, never
   silently correct.
6. **When the source is a translation, verify against the original-language text.** Grep the extracted
   original for every figure you are about to publish: it confirms the number exists at all and catches
   translation drift. A translated file standing in `raw/` is a derived artifact — say so, and say which
   language version is authoritative.

**Comparing citation markers between a source and a translation: compare id SETS, not counts.** An
extracted source file's text normally includes the source's reference list while the translated body
carries the in-text markers only, so nearly every id shows a count difference that is not an error; range
citations (`[130-131]`) also collapse into their reference-list entries and inflate the same way. The
direction of error that matters is one-sided and absolute: **any id in the output that is absent from the
source** is an invented or renumbered citation, and that is what to check for.

## Auditing teaching material (lecture decks, lab sheets)

A deck's "results" are worked examples, printed command output and code listings. The author is
usually authoritative on the method and transcribing tool output by hand, so the failures are
structural and version-related rather than arithmetic — and, crucially, most of them are provable
without knowing the true value.

1. **Test a printed result against a structural invariant before its digits.** Rank, determinant,
   symmetry, trace, eigenvalue count, the number of independent rows. This is step 3's independent
   bound in its cheapest form: an exactly singular matrix printed together with its inverse is
   disproved by `det` and `rank` alone, and the tell sits in the printed object's own structure (a
   round-off "inverse" of a singular matrix comes out with every row proportional). Print the
   invariant and state what it makes impossible — never "the digits look off".
2. **Ask whether the question has a unique answer at all before checking the printed one.** Count
   unknowns against independent equations. A slide offering a 4-decimal vector as *the* solution of
   an underdetermined system is wrong in its claim to uniqueness, not necessarily in its digits: give
   the exact value and say the printed one is one member of an infinite family.
3. **Treat every function name, keyword and default in a listing as a claim about a tool version.**
   Grep the listing for all called symbols and confirm each against the tool's current documentation —
   the plausible-but-absent name is invisible to reading. Flag a routine that was removed or renamed
   with its modern replacement, and a call the tool never had at all. Course material is routinely a
   release or two behind.
4. **A listing is a data-flow claim: check each value is still in the form the later line needs.** A
   symbolic quantity converted to numeric before the call that needs it symbolic, a variable
   overwritten and then used as its former self, a result from one panel consumed in the other — these
   let a slide print a coherent transcript that no single run produces. Check the quoting too:
   full-width Chinese parentheses, smart quotes and CJK punctuation inside a code line will not
   evaluate when copied.
5. **Re-derive the free block-level quantities** — how many points a range generates, loop iteration
   counts, the stop or branch point, the last term of a sequence, turns implied by a parametric
   sweep. They are arithmetic independent of the method, one line each, and a mismatch localizes the
   defect to a specific line of the listing.
6. **A reconstructed object is checked against the source's OWN downstream numbers.** When you rebuild
   a derived quantity from a printed primitive — an iteration matrix `B = D⁻¹(L+U)` from the printed
   `A`, a covariance from a printed design matrix, a rate from printed counts — require the source's
   *printed* follow-on values to fall out of your reconstruction: its characteristic polynomial, its
   eigenvalue, its ρ, its standard error. Two independently printed values agreeing is what makes the
   reconstruction trustworthy; if they disagree, one of your two reads is the wrong one, and the
   re-render/re-read comes before any claim about the source.
7. **One bad row in a printed table: test the ORDERING before the arithmetic.** Iterate exactly and
   compare row by row. If a row does not lie on the true trajectory, ask whether a **different row
   order** of the same system reproduces it — an iteration matrix depends on the ordering the source
   chose, so re-run under every permutation before declaring a defect. A row that fits no permutation
   is a real defect (write it up with the exact values that belong there); a row that fits one is a
   documented reordering, not an error. Keep the printed table verbatim on the page either way and put
   the verdict in the checks section.
8. **Record it as the artifact's own checks section.** Per claim: re-derived and matches, corrected
   from X with the reason, or could not reproduce. Keep the deck's statements and your analysis
   visibly separate and label your commentary as yours.

## Claims about your own past work (before/after comparisons)

"Summarize this, and say how it differs from before" makes the earlier run a **source**, so it gets the
same treatment as one: read it, do not recall it.

1. **Establish that the earlier artifact exists at all.** A comparison needs a baseline on both sides;
   when the record shows none, say "there was no earlier one" and describe the current pass on its own
   terms. An invented baseline is worse than an absent one — the user can check your claim against their
   own record.
2. **Read the record directly instead of re-requesting a transcript.** Recollection tooling returns whole
   transcripts and spills to a file past ~100 KB, so go to the store for the two things you need: the
   request sequence (`role='user'`) and the final answer.

```python
import sqlite3, os
db = os.path.join(os.environ["LOCALAPPDATA"], "hermes", "state.db")   # == $HERMES_HOME on Windows
con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)   # mode=ro: never risk the live store
cur = con.cursor()
print([r[1] for r in cur.execute("PRAGMA table_info(messages)")])   # column names FIRST, do not guess
rows = cur.execute("select id, role, tool_name, substr(content,1,3000), timestamp "
                   "from messages where session_id=? order by id", (sid,)).fetchall()
```

The time column is `timestamp` (epoch seconds), not `created_at`; `tool_name` is populated on tool-result
rows, so reading it separates artifacts that were actually written from ones merely discussed.

3. **Attribute the difference to a mechanism, not to effort.** "The earlier pass produced a translation;
   this one adds X and Y because rule Z now applies" is checkable. "It is more thorough now" is not.

4. **A context-compaction handoff is a source, and the weakest one.** A summary carries earlier
   results, file paths and citation metadata that no longer exist anywhere you can read, so every
   value it supplies is *recalled*, not *checked*: re-resolve the DOI and re-read the source before
   a figure or a bibliographic detail from it enters the new artifact. Drifted metadata reads
   exactly like correct metadata — an article number that never appeared in that paper, a volume
   belonging to a sibling issue — and a summary is the one place where nothing flags it.

Being *close to* the source — having read it yourself, in this session or an earlier one — is not the
same as having it in hand. Recall fails in both directions at once: digits drift, and the *shape* of a
method is remembered as the standard version rather than the paper's actual one, so a heuristic
hyperparameter sweep comes back as a textbook distribution resample. Both read exactly like correct
text. **Probe the claim by searching the extracted source for its own keywords** — the sweep range, the
scheme's name, the metric — and if those words are not in the source, do not write the claim, however
sure of it you are.

## Validating the user's derived structure (recaps, study notes, section maps)

The user restates a source in their own words — a paper's skeleton, a chapter's argument, a
procedure they just read — and asks whether it is right before going deeper. The deliverable is a
verdict per claim, so the checking runs in both directions: their recap against the source, and your
verdict against the source.

1. **Extract the source once to a plain-text working copy** in a stable path and keep it for the
   whole review. Page through it (paged reads around each section boundary) instead of re-rendering
   the PDF or re-consulting the summary per claim.
2. **Map the source's top-level sections first**, then validate the recap *in the user's order*, not
   the source's. Their ordering is part of what is being checked.
3. **Grep the source for the exact term the user used before judging it.** Three outcomes, three
   different sentences: they are right (confirm, and add the mechanism clause they are missing);
   they are wrong (correct it and quote the source's own sentence); or **the source itself is
   imprecise** — then say so and say their recap is faithful to the source. A source's own sloppy
   grouping is not the user's error, and calling it one costs more trust than the nuance is worth.
4. **Number the refinements to the user's own list, and close with a verdict line** — structure
   correct / N refinements / none of them structural. They check off against their notes, so a
   refinement keyed to your ordering has to be re-found before it can be used.
5. **Verify before you assert, in both directions.** A correction is a claim (grep the term first,
   per step 3); and a quantity recalled from the *concept* rather than quoted from the source is an
   invented value wearing the conventional shape — reward or penalty magnitudes, thresholds, layer
   counts and parameter sizes all arrive from memory looking plausible while the source uses a
   different scale. Grep the value or leave it out.

6. **Validate the recap's labels before its content — which source each block claims to summarize is
   itself a claim.** Recaps get assembled, reordered and renumbered, so a correct summary can sit
   under the wrong heading and read perfectly. Grep the *claimed* source for the block's most
   distinctive vocabulary (a technology, a method family, a term of art): a zero hit there while the
   same words hit in a sibling row means the block describes a different source. Report that as the
   first refinement, before any content verdict — a faithful summary filed under the wrong title
   corrupts every citation drawn from it, and nothing inside the summary looks wrong.

7. **Read "X% of errors" and "X% error rate" as different quantities, and check the denominator.**
   Sources report the *composition* of their failure cases ("accounting for 61% of all errors")
   while a recap turns it into a rate ("61% error on that operation"); the two differ by the total
   failure count (11 of 18 here). Say which denominator the source used and confirm the share
   against the source's own per-category counts, so the wrong reading cannot survive into the note.

8. **A gap claim ("no work studies X") is a counted claim: search the vocabulary and report the
   counts.** `recover*`, `toleran*`, `bound|confidence|interval`, the method family's own name, over
   the full-text working copy. State the words searched beside every zero, because absence of a term
   is evidence only for that term — the concept can be handled under other words, and the reference
   list is checkable text (see *Equations as claims*). Counts turn a reading impression into
   something the user can re-run, and they group: one grep set backs one sentence of the artifact.

Pitfalls specific to this review:

- **"Similar to X" is an analogy, not a classification — and a recap routinely collapses the three
  roles into one.** Read one sentence past the analogy for its explicit *not the same as* clause,
  and check whether X appears elsewhere as a **baseline** rather than as the method. A heuristic
  described as similar to an RNN is not an RNN; a network family listed in the experiments is a
  competitor; a block named in the method is not the model class just because it also appears in
  bigger architectures. All three read as correct to a reader who only saw the analogy.
- **Omissions are the likeliest defect in an accurate recap, so list them separately.** A recap
  edited down from an abstract and an introduction stays structurally right while losing a whole
  family in the related work — and that family is usually what the experiments later use as
  baselines, so the omission costs the user the experiments section too. Report omissions as
  "missing, and here is why it matters downstream", not as errors.
- **A recap-level question often has its answer in a later section than the one they asked about.**
  "Is it optimal?" answered where the method is defined gives the wrong answer; the source's own
  caveat lives in the next section, and pointing at the caveat is the real reply.
- **A grep that returns nothing has not proved absence: de-hyphenate the extracted text first.** A
  text layer breaks a token at its own hyphen when the line wraps, so a source's `i9-14900KF` sits
  in the file as `i9-\n14900KF` and an exact-token search finds nothing — a miss indistinguishable
  from the value genuinely not being there, whose reflex is to "correct" a value that was right.
  Build the working copy by joining hyphen-newlines and collapsing every whitespace run to a single
  space (`re.sub(r'-\n', '', t)`), then grep that; return to the raw text only to ask whether the
  hyphen is real, since a genuine compound split across a line joins into one word.
- **A digit that greps as present is not yet attributed to a symbol.** Finding `20` in the source
  says nothing about which quantity it quantifies: a paper printing `N_max_iter = 20` and no
  numeric horizon bounds will silently absorb "20" into an artifact line labelled `Nmax`. Read the
  sentence around the value and name the symbol before it enters the chart, table or recap, and
  prefer the source's own bound names over a range you assumed. Sources print families of like
  values — a bound and an iteration cap, a rate and its threshold — so the digits alone cannot
  separate them, and the error survives every numeric check you run on it.

## Explaining your own artifact's prose back to the user

The user quotes a paragraph out of the report you produced and asks what it means. That paragraph is a
source, and the weakest kind: it was drafted from a run whose numbers are no longer in context, so a
compaction summary will offer a confident paraphrase instead of the values. Re-derive before you
explain — an explanation is itself a claim about the artifact, and every sentence that restates an
unchecked number propagates it.

1. **Re-measure every number in the paragraph from the run's own logs**, then state the measured value
   beside the printed one. Three outcomes, three sentences: it matches (say so — that is what makes the
   answer worth reading); it is a near-miss at the printed precision (a hand figure of 0.39 against
   0.404 — correct it); it does not reproduce (flag it, never quietly repeat it).
2. **A named limiter or mechanism must exist in the configuration.** "The 1 ms step became the limit",
   "saturation capped it", "the noise floor dominated" are claims about the model file: grep it for the
   sample time, the solver, the filter coefficient, the saturation block. A continuous solver at
   `MaxStep = 2e-3` with a derivative filter `N = 100` (so 0.01 s) is not a 1 ms clock, and log samples
   landing ~1.2 ms apart are a consequence of the solver, not a setting anyone chose. When the named
   limiter is absent, say which mechanism is really there and hand over the replacement sentence.
3. **A printed formula plus its printed parameter must reproduce the value that ran.** Recompute table
   entries from the equation the report prints beside them: `Ki = Kp ωn/Ti` with a printed `Ti = 0.8 s`
   gives 4004 where the run used 160, and 160 is `Kp/Ti` with the same 0.8 s — one symbol, two
   conventions, and no typo anywhere. Name the convention the code implements and give the one-line fix
   (`Ki = Kp/Ti`) instead of proposing to recompute figures that are themselves right.
4. **Re-fit any law the prose asserts.** An exponent ("error falls roughly as ωn^−1.9", measured −1.86),
   a fitted band ("stays between 0.41 and 0.48", measured 0.408–0.477) and a peak location are cheap to
   check against the sweep data, and they are where a narrative drifts from the run. Say which channel a
   number refers to: a joint-1 range quoted without its joint reads as a whole-robot claim.
5. **Explain the mechanism with the invariant, not a paraphrase.** "The torque is set by the motion, not
   by the gain" becomes an answer only when the cancelling quantity is named and numbered: the loop holds
   `e ≈ q̈d/ωn²`, so `Kp·e ≈ J·q̈d` and the bandwidth drops out (128 × 0.003 = 0.384 N·m against the plan's
   own 0.403 N·m peak). A reader can check a product; they cannot check a restatement.

## Auditing a critique of your own report

A reviewer (a friend, a supervisor, a referee) flags a sentence in your own work. The critique is a
*hypothesis*, and it gets settled against the project's own data before a word of the report changes.

1. **Reproduce the flagged claim with the code or CSV that produced it, and expect three outcomes:**
   the critique is right and the prose must move to the data; the critique is right *about a different
   defect* than the one it names (the number checks out, the justification around it does not); or it
   is wrong. Only the first two change the file, and the third is worth saying out loud.
2. **When prose and data disagree, the data wins: change the description, not the computation.** A
   table computed with cell-centre sampling but described as a corner rule keeps its numbers and gets
   a corrected rule name (plus the alternative reading's own numbers, so the choice is visible).
   Recomputing to match a sentence silently invalidates every other number derived from the old rule.
3. **A false justification is a real defect even when the value is right.** A containment claim read
   off a positive-semidefinite-order argument fails as soon as the two means differ: the order bounds
   the covariance about each own mean, it does not nest the ellipses. Replace the borrowed argument
   with the statement the algebra actually gives, and keep the empirical count as the demonstration.
4. **A claimed universal ("holds for every k", "never corrected", "is not reduced") is disproved by
   one counterexample from the report's own tables.** Look for the exception in the numbers already on
   the page before designing a new experiment; a single failing case (a quadratic form of 1.72 where
   1.0 would be containment) settles the wording.
5. **Every number you add comes from a script that ran to completion with visible output, and it goes
   into the project's harness — never from a figure recalled out of a collapsed or compacted tool
   result.** A recalled figure reads exactly like a verified one; re-run and count. When the count moves
   (27 and 7 of 800, not the 41 and 12 recalled), the report's sentence moves with it.
6. **Match the harness's dependency convention.** If the engine is stdlib-only, a new check script
   imports nothing outside the stdlib, or it dies under the interpreter the project documents as
   `python`. Confirm the interpreter before writing the import line.
8. **Critiquing a peer's submission on the same assignment runs the audit in BOTH directions — ours
   against our own raw results, theirs against their own document — and every sentence about what they
   did or did not do is grepped out of their extracted text before it is written.** A compaction
   handoff or an earlier read of that file is a *recall* of it, which is where a fabricated finding is
   born (a mismatch study and three sets of numbers attributed with confidence to a peer report that
   contains none of them, disproved by one `grep -c` on the extracted text). Negative characterizations
   are counted claims here too: search for the vocabulary of the thing you are about to say they
   skipped (`robustness`, `mismatch`, the parameter-error word in the document's own language) and
   report the zero beside the claim.
   - **Price each of their headline numbers before comparing it with yours.** A reported extreme that
     equals a product of constants the source itself states is a *mechanism*, not a result: a PID peak
     torque of 4.8005 N·m where the source's own Kp = 32 and its initial error is 0.15 rad is Kp·e(0)
     exactly, so that "peak torque" measures the initial-condition kick and says nothing about the
     control law. Compare the metrics that survive the test (tracking error) and say in the critique
     why the other one does not — an artefact mixed into one side's metric is itself the finding, and
     worth more than the ranking it replaces.
   - **Lead with what the two documents agree on when they agree exactly.** Two independent solutions
     of the same problem landing on the same derived object to every printed digit (here both mass
     matrices and both Coriolis/gravity vectors, digit for digit) is the strongest evidence either
     document carries, and it appears in neither — it belongs at the top of the comparison.
   - **Close the comparison with the gap on both sides** (what neither report does: noise, saturation,
     step reference, hardware). It is the part a grader would ask next, and stating it costs nothing
     while pre-empting the objection that the comparison was self-serving.
   re-check the contested numbers on BOTH sides against each side's own raw results — never re-serve
   the earlier write-up from recall.** Lead with the verdict, then the value table where both reports
   agree, then the points where theirs is better (and say which of those you adopted), then the
   disagreement. Check the seed count before calling a disagreement: one side's 0.27 m over 10 seeds
   became 0.73 m over 20 and matched its rival's 0.97 m over 20, so the rival was right and the thin
   sample was ours. A resolved non-disagreement is a better finding than the contradiction it was
   mistaken for. When the other report wins a point, quote its own line for it, and keep the
   comparison metric honest (a five-trajectory mean is not a per-trajectory win).

## Fast-expiring facts (liveness, availability, versions)

Some claims are not numbers inside a source at all — they are facts about the world *today*: a
repository's activity, whether code or data were released, a dataset's size, which version is
current. Those expire, and a stale one is indistinguishable from a fresh one on the page.

- **Say when you checked and how.** "As of <date> the API reports ..." / "the paper's code
  availability statement withholds the source" — not "the code is not available", which reads as
  a permanent property of the work.
- **Go to the primary artifact, not a page that quotes it.** The API response, the repository, the
  paper's own availability statement. Search snippets, blog posts and mirror sites are cached and
  frequently years out of date, and they are where the false "there is no release" claims come from.
- **Quote the checkable pair, not a verdict**: licence + last activity date, or the deposit's file
  list. "Abandoned but permissively licensed" and "active but proprietary" are different answers,
  and a bucket label hides which one you found.
- **If you could not check, write "unverified".** A plausible guess at liveness is the same failure
  mode as a plausible digit: unverifiable and attributed to you.

## Pitfalls

- **Trusting your own checker more than the input.** Before reporting failures from a script you
  just wrote — a link checker, a parser, a regex validator — run it against an input whose
  correct result you already know. A fresh checker reporting *mass* failure is more likely wrong
  than the corpus, and publishing its false failures makes you the source of the error. Debug the
  tool to at least one known-good pass before you believe a single failure.
- **A number you read off a page image is a claim from a fallible instrument, not from the source.**
  OCR and vision both replace a degraded token with a plausible one, so a single read of a
  low-resolution table cell is unchecked — and the reads that fail *into* plausibility are exactly
  the ones you will not catch by looking. Before such a figure enters a deliverable: re-render that
  region alone at 2–3× the scan's own resolution and re-read it, then settle it against the
  arithmetic the value has to satisfy. A reading of 3 quoted with ±2.0 accuracy yields the interval
  `1..5`, so `1.5` in that column is a mis-parse, not a finding — internal arithmetic is the
  cheapest oracle for a bad transcription. Two reads that disagree mean re-render the region: never
  average them, and never keep the one that fits the story you are telling.
  **A coefficient matrix has no internal arithmetic to check it against** — a misread digit breaks no
  per-cell identity and still solves to a wrong-but-plausible vector, so where the value's neighbours
  cannot regenerate it, cross-view agreement IS the check: read the full image, read 4–6× upscaled
  crops of the region, and require two views to agree before the value enters the artifact. A second
  look at the *same* resolution is not an independent view; a higher-resolution crop outranks a
  full-image read when the two disagree.
  **A figure's geometry is read on the same terms, and one class of it never converges.** Which axis is
  vertical, which way an arrow points, which label belongs to which line are NOT recoverable by better
  crops: repeated reads of the same sketch return directions that contradict each other call to call,
  while the figure's label *positions* are measurable to the pixel (take them from the component
  analysis on the threshold mask, never from the coordinates the vision tool quotes — those are
  estimates, routinely off by tens of pixels). So measure what is measurable, ask one fact per question
  with a bounded answer, and cap it at **two independent attempts**. If two attempts disagree about a
  *direction*, stop: take the convention the domain prescribes, state it as an assumption in the
  artifact, and flag that single item in the closing caveat. Then check every reading against an
  identity the object must satisfy — a frame's $x_i$ is perpendicular to the previous joint's axis by
  construction, so a figure labelling $x_1$ along the gravity arrow has a horizontal base joint, and the
  picture and the assumed convention cannot both be right. A reading that breaks an identity is *wrong,
  not difficult*; the fixed convention plus a stated assumption is a finished answer where a third round
  of crops is not. Say which part of the answer the ambiguity cannot touch (usually all but one term) —
  that is what makes the caveat worth reading instead of a hedge.
- **A printed value that looks wrong may be a symbol your extraction DROPPED.** A text layer loses
  radicals, overbars and primes and re-orders signs into separate runs, so a printed `√5/2` arrives as
  `5/2` and the minus joining two summation signs lands on its own line: both read as arithmetic
  mistakes in the source. Read the rendered page (or a zoomed crop) before accusing it, then classify —
  extraction artefact, rounding, or real defect. Conversely, a value that *reproduces* can still be
  wrong on the page; the two checks are not substitutes.
- **A table's own cells are evidence about each other.** Before trusting any single degraded cell,
  check whether the row/column it sits in is reproducible from the source's stated rule (a range is
  value ± accuracy; a computed answer is the mean of the listed terms). A cell that cannot be
  regenerated from its neighbours is the damaged one, and knowing *which* cell is damaged is worth
  more than a better read of all of them.
- **Re-deriving with the tool under test.** See step 2. Use arithmetic independent of the pipeline
  that produced the number.
- **A prediction about how the method behaves is a claim: run it, do not reason it.** Once an
  implementation exists, "under a stricter threshold nothing is rejected", "the answer stays inside
  the honest spread", "the ranking is unchanged" are each one call away — and they are exactly the
  claims that stay plausible when wrong, because they describe a *sensitivity* rather than a value
  you can picture, and an analytical guess at a parameter sweep reads like the sweep's output.
  **Run it in the regime where the parameter is live.** A knob that only acts on a branch nothing
  entered — a fallback that fires only when something is rejected, an option that only applies past
  a threshold — returns "no effect" there, and reporting that as "this choice does not matter"
  stacks a second wrong claim on the first. Sweep across the regime that exercises it, and say which
  regime you ran.
  Reconciling a disagreement between your re-derivation and the source's own method is the same
  move: the criterion as the source states it is the one to execute, before deciding whose number
  is wrong.
- **Checking every digit instead of the load-bearing ones.** Effort should scale with how much the
  argument leans on the number, not with how many numbers there are.
- **Accusing the source of a typo when the real cause is a rounded seed.** Print chains are
  frequently unreproducible from the printed inputs; check the mechanism before the digits.
- **Repeating a figure because it is plausible.** Order-of-magnitude plausibility is not verification.
  The errors worth catching are precisely the ones that stay plausible, and the failure is not confined
  to numbers: a remembered hyperparameter or algorithm step that sounds like the conventional one is the
  same error class as a transposed digit.
- **A value lifted from the user's own notes about a document is the *notes'* claim, not the
  document's.** The user keeps summary and math notes on the sources they read, with a different
  authority from the source: the notes may carry a settings table the document's text layer never
  prints, or their own reconstruction of it. The two sit in the same reading flow, so the swap is
  invisible in your own prose — and it is the expensive one, because it makes a retraction necessary
  and costs the credibility of the figures that *were* checked. Attribute each value to the file you
  actually read it in ("your notes give γ = 0.99; the paper's extracted text contains no discount
  factor"), never merge the pair into "the paper's settings", and keep the two reference paths apart
  in the artifact even when both appear on the same page of the deliverable. The document side of the
  check is cheap: grep the extracted text layer for the term — hits there are the source's, miss there
  and the claim belongs to the notes.
- **Burying the correction.** A corrected number belongs in the main text with its reason, not in
  a footnote a reader will not see. Anyone who trusts the corrected value must be able to see why.
- **A page you are only *translating* is still a source.** Translation feels like transmission, not
  authorship, which is exactly why an unchecked figure rides through unexamined and lands under your
  name in the target language. Re-derive the same way you would if you had written the page yourself;
  the disagreements then become the artifact's flags section instead of a footnote nobody reads.
- **Assuming a heavy numerical library is importable.** Establish what the running interpreter
  actually has and choose accordingly; stdlib `decimal` needs nothing, so reach for it first
  rather than assuming a third-party high-precision package is present.
- **Letting the verification live only in your working notes.** If the artifact does not carry the
  status, the next reader redoes the work or trusts the wrong number.

## Verification

Every load-bearing number in the artifact is either (a) re-derived with the arithmetic shown, or
(b) explicitly labelled as transcription from the source / not reproduced. A reader can tell
which is which without asking you.
