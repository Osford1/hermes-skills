# Deriving a source's proofs for the user

Use when the user points at a lecture deck, PDF, or paper and says they cannot follow the proofs
or the equations. The deliverable is a derivation pass they can walk, not a summary of results.

## Order of work

1. **Read the whole source's move structure before writing a line.** Say how many moves the source
   makes ("all of this is three moves, repeated") and name them. A hundred pages of algebra reads as
   noise until the reader has the count.
2. **Establish the page map before quoting any location.** Open the PDF with pymupdf and print the
   page count plus the opening ~120 characters of every page. That gives the real section
   boundaries and lets you cite page numbers the user sees in their own reader. **Also print the
   footer strip of every page** — `page.get_text("text", clip=pymupdf.Rect(0, page.rect.height*0.90,
   page.rect.width, page.rect.height))` — because that is where the deck's own printed slide number
   sits, and the user counts by *that* number, not by the reader's page index. Read the two against
   each other once and state the mapping; when they coincide (one slide per page), say so, because
   it is a coincidence and not the default. Never carry a "slides N–M" range forward from an earlier
   session's note without re-checking it — slide numbers and PDF page numbers drift apart.
   When the user pastes ONE slide as an image instead of naming a range, do not explain it from the
   image alone: match it against the page dump to fix which slide and which block it sits in. What
   makes the explanation land is the slides around it — the block it opens, the ones it closes, and
   which of the deck's repeated patterns it is an instance of.
   Print a few pages per call and check the dump actually arrived before reasoning on it; a dump
   long enough to come back empty or collapsed leaves you explaining content you never saw.
3. **Extract text only as a survey, never for the formulas.** A PDF text layer garbles or
   interleaves displayed mathematics. Use the dump to find WHERE a derivation sits, then render
   those pages to images and read them with vision for the actual symbols, at a scale where
   sub- and superscripts stay legible. When the source is a small screenshot rather than a
   rendered page, lift the scale yourself: tile the image on a 3x3 grid with ~12px overlap,
   upscale each tile 4x (LANCZOS), and ask one terse question per tile in a single batched turn
   ("Transcribe every Chinese string; if none, say none" — without that clause the model
   describes the diagram instead). One whole-image read of a sub-700px screenshot does not fail
   loudly: it returns a plausible wrong character or a neighbouring label repeated, which is
   exactly the error the user cannot catch. Trust a string confirmed by two overlapping crops,
 and re-crop alone at 6x when two tiles disagree rather than picking the more likely one.
 **The PDF's own span geometry outranks the vision read.** `page.get_text("dict")`, walking
 blocks→lines→spans and sorting the spans by `bbox[1]` then `bbox[0]`, prints each text object in
 glyph order with the sub- and superscripts intact, and leaves a blank run where the operators are
 drawn in a font whose glyphs do not map to Unicode. Reconstruct the equation from that dump and
 then confirm it against the rendered read. A vision transcription of an equation is a hypothesis,
 not a source: it returns a self-consistent-looking equation with one sign flipped, and it will
 report two different sign conventions for the SAME equation across two reads. When the dump and
 the read disagree, re-render at higher zoom and read again — never pick the more plausible one.
 **Choose the vision payload by slide density.** Sparse figure pages can share a stacked image; dense
 formula pages are cheaper to read one slide at a time with a targeted question than through repeated
 whole-pair failures. To stack, open a new document, add one page of double height, and
 `show_pdf_page`-ing each source page into its own half; render JPEG with
 `pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2)); pix.save(path, jpg_quality=65)` and ask for
 "TOP is slide 46, BOTTOM is slide 47" with separate output. If a stacked batch stalls, change the
 transport: smaller single-slide JPEGs, small batches, and one narrow transcription target per slide.
 Do not lower the verification bar — disputed glyphs still need two independent reads.
4. **Recompute the source's worked examples BEFORE writing prose.** One anchor example can serve a
   narrow question; a whole-deck pass requires every worked example and every printed table row that
   the answer cites. Implement from the primitive problem data (for a solver, the original $A$, $b$
   and update law), not from the source's derived matrix or recurrence alone, or the check will clone
   the same algebra error. Check the result independently — exact solve or residual, an eigenvalue
   identity, or a numerical minimisation of a claimed optimum. Use `fractions.Fraction` for exact
   hand-iterations when a rounding discrepancy matters. Quote actual outputs, and distinguish an
   asymptotic error-contraction estimate from a measured iteration count.

   **Verify the mechanism that motivates the method, not only the final answer.** Check its claimed
   identities (residual, orthogonality/conjugacy, optimality) and run a contrast method on the same
   primitive input when the lesson is why the new method exists; matching one final vector does not
   substantiate those claims. Keep exact-arithmetic properties (finite termination, zero inner products)
   separate from floating-point behaviour, and a comparison of convergence bounds separate from a claim
   that one method wins on every run.

   **When a printed cell disagrees, prove the mismatch before calling it a typo.** Confirm the
   primitive inputs on the render, read the cell with `page.get_text("words")` (which preserves table
   values as complete strings), and inspect a tight high-resolution crop. Then run adjacent iterations:
   if the printed value equals a neighbouring $k$, report the shifted/duplicated row and its actual
   location. Give printed value, independently computed value, and any off-by-one diagnosis; never
   silently substitute the computed number.
5. **One rung at a time, each with four parts:** the claim; why the step is legitimate; *the trap*
   (the mistake that step invites — the wrong denominator, a sign convention, a stationary point
   that could be a maximum); and what the source asserts without proving. The trap line is what
   makes the explanation land; sources never mark it.
6. **Name the reconciling insight in one sentence.** Where two formalisms turn out to be the same
   equation (a sensor-fusion rule and a filter gain both being $1/P = 1/P_1 + 1/P_2$), say so and
   point at the page gap between them — the reader's real confusion is usually that the source
   spread one idea across thirty pages without admitting it was one idea.
7. **Close with what the source leaves unproven, then the offer — not the edit.** Do not patch the
   user's vault note as part of the explanation. State what could now be fixed in it (a caveat that
   equations were unrecoverable, now recovered) and offer.

## Checking the source's own algebra (it is wrong more often than you expect)

- **Substitute the source's printed law back into the model it stated one line earlier.** When a
  slide prints an equation of motion and then a control law "solved from" it, redo the substitution
  before explaining either. This is how a coefficient that does not follow gets caught — a
  reference-force term printed as $+F_d$ where the algebra gives $-\frac{m}{M_d}F_d$. The deck's own
  other slides are the witness: when a later slide's equation for the SAME model is self-consistent,
  the inconsistent one is a transcription slip, not a different sign convention.
- **Report the discrepancy as printed and flag it — never silently fix it, never propagate it.**
  Give the printed form, the corrected form, and the one clause that makes it harmless in context
  (a constant reference force can be absorbed as a feedforward). The user reads sources critically
  and wants the gap, not a smoothed version of the slide.
- **Cross-check numbers that live on different slides.** A requirement on the task slide and the
  commanded reference on the algorithm slide can disagree; state both, say the deck never reconciles
  them, and leave the reconciliation to the reader or the lecturer.
- **Read each slide's own definition line before trusting any sign.** One deck will use
  $e = q^d - q$ for the motion block and $e = X - X_d$ for the interaction block, and every "why is
  this minus here" question depends on which convention the slide in front of you chose. Announce
  the flip when you cross the boundary.
- **Attribute what is printed versus what is yours.** Mark your own readings out loud ("that is my
  reading, not a slide statement"), and correct the source's typos to the real name while saying the
  deck spells it otherwise (a 1985 impedance paper attributed to "Hogon").

## Notation discipline (the #1 cause of re-explanation loops)

When the user says "I don't understand this step", the cause is almost always a symbol YOU
introduced, not the mathematics. Expect to re-explain the same section three or four times, each
round stripping one layer of outside shorthand. Rules that cut the rounds:

- **Every symbol in the explanation must be traceable to the source, or be defined in one line at
  first use.** Do not silently import textbook notation. Writing $A_i$ for the source's
  $T_{i-1}^{i}$, or `skew`, or $\dot RR^{\mathsf T}$ without a one-line definition, costs a full
  round-trip per symbol.
- **When the user asks for a step again "without <tool>", give the derivation that never needed it**
  — not the same derivation with the name deleted. Example that works: drop the skew-matrix
  formalism entirely and show the plain $3\times3$ multiplication, then read the three surviving
  entries off the result. Same answer, no new object introduced.
- **When a symbol appears, answer the smallest question asked** ("what is $q_j$") as its own short
  reply: what it is, a concrete table of its values for THIS problem, and what a derivative w.r.t.
  it means. Do not fold it into a re-derivation.
- **Justify structural claims with a number, not a diagram.** "Only one factor of the product holds
  $q_j$" lands when backed by a run showing which factors move under each derivative, quoted as
  output.
- **Re-attach the verification to the exact formulation you just posted.** The user's trust
  follows the numbers; if the numbers were produced for a differently-framed derivation, rerun them
  in the new framing and say so.

## Delivering it

- Plain English, one idea per line, short lines, answer first, no trailing quiz.
- A page number for every claim about the source's content.
- Ship the companion interactive widget alongside the explanation — see
  `interactive-concept-widgets`, one tab per rung, and file it beside the source deck with the temp
  copy left in place for `::preview`.
- When the source is one of a course's lecture decks, the vault convention is a synthesis note at
  `wiki/synthesis/sources/<date>-<course-slug>-lecture-N-<topic>.md` and concept notes under
  `wiki/concepts/<course-slug>/`; read them before writing so the new pass extends rather than
  duplicates them.

## Progress recap ("zoom out for me")

When the user has read up to a slide and asks what has been covered so far, the deliverable is the
*shape* of the material, not a list of slides. Deliver in this order:

1. **Where the marker sits** — one line saying which block the last-read slide closes and what
   begins next. Derive it from the page map just built, never from memory.
2. **A slide-range → block table** for the range read so far, 4–7 rows. This is the only place
   slide numbers appear.
3. **The one question the whole block answers**, in a single sentence.
4. **The moves in order**, each named by the idea and the reason it exists — not by slide title.
5. **The through-lines** — the three to five patterns that recur across the block and are what the
   material is actually teaching (a constraint count driving the order of every method; a
   smoothness ladder of position → velocity → acceleration; one compute-vs-predictability
   trade-off reappearing in four guises). This is the section that earns the recap its length;
   per-slide coverage does not.
6. **A short self-check** — what they should be able to produce cold, without notes — and **what is
   next**.

Keep it English-only unless pinyin was asked for; a recap is not the moment to introduce Chinese
terminology the user has already read past.

A FORWARD request ("explain slides N onwards") is not this recap: it wants the material itself.
Open with the block table for the requested range so they know what is coming, then walk it one rung
at a time, then close with the source's gaps. Do not hand back through-lines and a self-check when
they asked for the content.
