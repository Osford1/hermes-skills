---
name: document-cleanup-pass
description: Use when cleaning a document's markup, grammar, or dashes.
---

# Document cleanup pass

Apply a style, grammar or markup cleanup to a document the user already owns, leaving the content identical. This skill exists to prevent one specific failure: a plausible-looking rewrite that silently invents content.

For *what* to strip from the prose (AI-isms, hedging, em-dash overuse), see the `humanizer` skill. This skill covers *how* to apply any such pass without damaging the document.

Two kinds of pass arrive under this name, and they differ in how much text may change:

- **Markup / grammar / mark-removal pass** — content identical afterwards; only marks, punctuation and grammatical errors move. Most of this skill.
- **Wording pass** — the user asks for concision or a house voice ("make it more concise", "rephrase the sentences that sound robotic"). Sentences are deliberately rewritten, so the safety net is not "change as little as possible" but "every rewrite is an exact pair, and the diff is the change record". See *Prose pass* below.

## Rule zero: transform, never regenerate

Never write the cleaned file from your own reading of it. Express the pass only as an ordered list of exact `(old, new)` string pairs, and assert each `old` occurs the expected number of times. If a change cannot be written as a pair, you do not understand it well enough to make it.

Rewriting from memory invents content. You will produce table cells, bullet lists and formulas that read perfectly, fit the surrounding argument, and are wrong. Nothing in your own output will flag them. Only a diff against the pre-edit file will.

## Procedure

1. **Back up and hash first.** Copy to a `Working/backups/<name>.pre-edit.md` sibling, record `sha256sum`, confirm with `ls -l`. No edit without a restore point. For a deliverable inside the user's vault, their archive convention is `Working/<kind>/_archive/<name>.before-<pass>-<YYYYmmdd-HHMMSS>.<ext>`; quote that path in the reply so they can diff or restore it themselves.
2. **Inventory the marks.** Run a counting script over the original and print exact counts per mark type. You need the before-numbers to prove the after-numbers exist. **Print `repr()` of every line you intend to touch** (`for n in range(a,b+1): print(n, repr(lines[n-1]))`) and work from those line numbers, never from an earlier read or a rendered view.
3. **Resolve ambiguity before editing.** One word often names three different things. "Remove all `-`" could mean punctuation dashes (`—` `–`), in-word hyphens (`fault-tolerant`), or markdown structure (list bullets, table separator cells). Ask which, then hold the answer for the whole pass. Do not guess: deleting every hyphen in a document with a large table also breaks the table.
4. **Apply as checked pairs.** Loop the list, `assert s.count(old) == expected`, replace, and report any pair whose count is not what you expected. A count of 0 means the key is stale or mistyped; a count above 1 may be correct (a global rename) but must be deliberate. Do not use wholesale `write_file` of composed prose.
5. **Strip emphasis with scoped regexes,** in this order: `\*\*\*(.+?)\*\*\*` then `\*\*(.+?)\*\*` then `(?<!\*)\*([^*]+?)\*(?!\*)`. **Never add `re.S`** — a DOTALL triple-asterisk pattern matches from one horizontal rule to the next across hundreds of lines and deletes the rules on the way through. A `***` alone on a line is a horizontal rule, not emphasis; the three passes above leave it alone because it has no inner text. Decide explicitly whether rules stay (default: keep them, they are structure) and say which you did.
6. **Preserve line endings.** Check the original for `\r\n` and write with `newline=""` or in binary mode. Python text-mode write on Windows converts every `\n` to `\r\n` across the whole file, which shows up as a spurious full-file diff and buries the real changes.
7. **Repair structural damage, narrowly.** Run a whitespace pass over non-table lines only: collapse runs of spaces, pull spaces off the front of `, . : ;`, strip trailing whitespace. Never run it over `|` lines — table padding is meaningful. Add the blank line markdown needs after a table block and where a heading immediately follows another heading, otherwise the table or heading merges on render.
8. **Verify mechanically against the backup.** Run `scripts/verify_mechanical_edit.py BACKUP CLEANED`. It hard-asserts that no removed mark survives, no number disappeared, and no table changed shape, then prints the prose lines that differ so you can check each one against your pair list. Read "verification passed" as "the only lines that changed are the ones I meant to change", not as "the file looks fine".
9. **Report counts and judgement calls,** not a process narrative. Formatting changed *N* marks; the following lines were also rewritten for grammar; these factual corrections were made.

### Where pairs are anchored in a wrapping source

Prose wraps at the author's margins, so a pair's `old` string must sit **inside one line**. An `old` copied from the rendered text can straddle a line break and never assert — when an assertion fails on text you can see in the file, the phrase you meant usually starts one line earlier. Anchor on a short substring of the target line and apply it there: `assert lines[n-1].count(old) == 1; lines[n-1] = lines[n-1].replace(old, new)`. Line numbers stay valid for the whole pass because nothing is inserted or deleted, and the diff stays readable. Write back with `open(path, "w", encoding="utf-8", newline="")`.

## Prose pass: concision and house voice

Always-on style rules for this user's documents. Detail and worked examples: `references/wording-pass.md`.

- **No dash used as punctuation.** The standing rule is "no `-` unless it is a heading". Turn `---` / ` -- ` between clauses into a comma, a colon or brackets, chosen by role: an aside becomes brackets, an explanation takes a comma or colon, an enumeration takes a colon. **Keep**: hyphens inside compound words (`wheel-only`, `line-of-sight`), en dashes in numeric and reference ranges (`$0.41$--$0.51\unit{m}$`, `Figures~8--12`, `Eqs.~(4)--(5)`), name pairs (`Box--Muller`), dashes inside headings, and table separators. State that allow-list in the reply so the user can overrule it.
- **Rule of three**: a three-item list written for rhythm rather than for count. Count the items and print the real number (four items means "Four observations", not "Three").
- **Antithesis** (`X, not Y`; `not merely X, but Y`): keep only where the contrast *is* the content (a sign check, a definitional difference, a necessary distinction); otherwise fold it into one clause.
- **Verdict sentences that judge instead of stating** ("...is honest", "Nobody uses X", "A sensor you cannot trust is worse than none"): replace with the mechanism or the number already in the paragraph. This is the shape the user names when they say a sentence "sounds robotic".
- **Opener tics** ("Note finally that", "Finally, note what", "It is worth noting", "That is a reminder that") and **tailing negations** ("...to its own accuracy, no better"): delete the frame, keep the sentence; fold the negation into the positive claim.
- **Fix broken sentences found en route and report them in their own list** — a clause whose grammar collapses, a sentence naming a file that does not exist. Never silently, and never as if the user had written it that way.
- **Never reverse a user's decision**: a claim they deleted stays deleted, a parked section stays parked, a filename they chose is only flagged. Reply shape: dash counts before/after, a handful of rewrite examples (lead with whichever sentence the user quoted), the trims, the fixes as a separate list, what was left alone and why, the build status, the backup path. Do not paste the whole pair list.

## Factual errors found during the pass

Verification surfaces real errors: a cross-reference that contradicts its source, a direct quote that has been altered, a claim stated backwards relative to the document's own data. Fix them, but only after confirming against the source document, and report them **separately** from the formatting changes. The user needs to know that content changed, not just the surface, or they will attribute the difference to your formatting pass.

**A reported defect is a hypothesis until it meets the document's own data.** Claims arriving from a subagent, a reviewer pass, or an earlier read of the file are worth checking, not repeating: confirm each against the table, caption or number it contradicts, and expect a share to dissolve (a range that reads inconsistent is often scoped to a different case; a cell highlighted in one column can be right for that column). Report the survivors with the line number and the contradicting data, and keep the dismissal to one line or none.

**When the pass is a translation, the source-language file is not yours to correct.** A defect found in the original is reported with its line number and evidence and left in place, because the translation is supposed to mirror it; apply the fix only to a file the user asked you to change, or after they say yes.

**Check every path, filename and artifact the document names against the filesystem.** A document that cites its own outputs goes stale silently: prose pointing at `index.html` while the build writes `Visualisation.html` compiles and reads perfectly. List the directory, fix the reference, report it as a factual correction.

**A defect inside disabled or parked content is flagged, not fixed.** A `\ref` whose label lives inside `\begin{comment}` renders as `??`; that is the user's parked section, not your broken reference. One line in the reply, no edit.

Do not "improve" prose beyond grammar and the marks the user named. A wording pass happens only when the user asks for one (concision, de-roboticising, house voice); unrequested taste edits are indistinguishable from fabrication and they bury the diff. When one *is* requested, every rewritten sentence still enters as a pair, so the diff remains the change record.

## Number revisions: when the fix is a re-run, not a reword

A review against a second source hands you corrections whose evidence is a computation, not the document's own table. Every rule above still applies, plus these. Full recipe with commands: `references/number-revision.md`.

- **A published number is only replaceable if you can reproduce it.** Reproduce the *current* value under the *current* protocol before accepting any recomputation: that reproduction is what validates your mapping from code to table cell, and it fails often (see the dispersion-convention trap in the reference). A cell you cannot reproduce from the stored outputs gets a prose caveat, never a new number.
- **Before re-baselining a mean ± sd comparison, re-run it at double the sample.** A conclusion drawn from few runs can rest on a tail that is invisible at the smaller count: if the spread explodes at twice the runs, the old claim was an artefact of the sample, not a finding. Report the per-run minimum and maximum, not only the mean.
- **A peer document's more dispersed result is evidence about your sample size, not about their error.** Two means disagreeing by ~2 sd, theirs the wider, usually means the smaller sample is the under-sampled one.
- **Fix the claim against the table, not the table against the claim.** "Better by three orders of magnitude", "to three digits", "300 times fewer" are hand-typed comparisons: check the exponent, the item count and the direction against the numbers already printed.
- **Every configuration the document quotes must exist in the code's experiment matrix.** Suites reported from ad-hoc runs are unreproducible: add the missing entries, re-run, and assert the regenerated values equal the published ones before claiming the code reproduces the report.
- **Say what you did not re-baseline, and why.** When a full re-baseline would move many cells whose derivation you cannot verify, record the new protocol's finding where it decides the argument, then offer the full pass as separate work. A silent partial re-baseline leaves tables drawn from two protocols with nothing in the document saying so.

## Pitfalls

- **A vault document may be another session's rewrite of the same deliverable.** Check for a sibling rendered artifact (`.pdf`) and for a `_manifest.md` before editing, and never overwrite a file another agent wrote without reading it first.
- **Editing one artifact in a set leaves the others stale.** If you clean a `.md` that was rendered to a `.pdf`, say so and offer to re-render, rather than silently leaving two versions that disagree.
- **Judgement calls belong in the final message, not buried in the diff.** Bibliography page ranges (en dash is standard in citations), running heads, horizontal rules, and compound names joined by a dash are all places where the user's blanket instruction and the document's convention disagree. Flag them so they can overrule.
- **Do not count marks by eye.** Emphasis nests, and `***x***` reads as both bold and italic. Count with a script, and scope the count away from horizontal rules and table separators.
- **A pair-list transform is self-documenting.** Each `(old, new)` pair is the change record. When the user asks what changed, the list is the answer, and it is checkable.

## Files

- `scripts/verify_mechanical_edit.py` — post-pass verification: mark inventory, line-ending check, prose-line exceptions, numeric-token set diff, table-shape comparison.
- `references/mark-stripping-recipes.md` — the ordered pipeline with exact regexes, the ambiguity decision table, and the pair-list assertion pattern.
- `references/wording-pass.md` — the wording pass end to end: order of work, the line-anchored pair pattern for a wrapping source, the leftover-mark greps, the LaTeX two-pass build check (run 1's nonzero exit is normal), the dash decision table, and worked rewrite examples for register.
- `references/number-revision.md` — revising figures rather than words: scratch-copy re-runs, the reproduce-before-recompute validation gate, the sample-sd vs population-sd trap, tail checks, exact closed forms in decimal arithmetic, and the rebuild verification.
