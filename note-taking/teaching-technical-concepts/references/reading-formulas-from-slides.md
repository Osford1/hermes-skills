# Reading a formula off a slide (raster equations)

Formulas on lecture slides are almost always **pasted raster images**, not text. The page's text layer
therefore shows the slide title and nothing else, and the equation is invisible to `grep` and to any
text extraction. Two failure modes follow, and both are silent:

1. You report "no equation on that slide" because the extract has no equation in it.
2. You ask a vision model to read a formula and it **hands you a different, plausible formula** —
   often the one that would be mathematically correct, which is exactly how a typo on the slide gets
   healed into something the deck never printed.

## Recipe

1. **Triage the page** — a text layer of ~40–120 chars (title + one fragment) is a formula slide.
2. **Find the raster.** `page.get_images(full=True)` lists the xrefs embedded on the page;
   `page.get_image_rects(xref)` gives where each one sits. The equation is the **wide, short** raster
   sitting beside or under the bullet it belongs to (e.g. 879×73 = one line of math). Decorative
   figures are large and square-ish (e.g. 949×413 = a network diagram). Ignore the tiny repeated tiles
   (15×15 bullet glyphs).
   ```python
   for xref, *_ in page.get_images(full=True):
       d = doc.extract_image(xref)            # original bytes, no re-encoding
       open(f"p{n}_img{xref}.{d['ext']}", "wb").write(d["image"])
   ```
3. **Magnify and cut.** Upscale 3–6× with `Image.LANCZOS`, then crop into two or three **narrow
   overlapping** horizontal thirds. Read the thirds separately — a whole-line read of a long equation
   is where the invented terms appear.
4. **Ask character-level questions, not "transcribe this".** The prompt that works is a targeted
   discriminator: *"list each glyph in order, licence-plate style; is the symbol before the log a plus
   or a minus?; which subscript comes first?; is there a fraction attached to the log?; if a symbol is
   unclear, say it is unclear."* "Transcribe this equation" invites the model to complete it from memory.
5. **Require two independent reads to agree**, ideally of *different crops* (one tight on the first
   term, one on the tail). Agreement on every glyph is the bar; "looks right" is not.
6. **Re-derive it yourself** from the surrounding slides' definitions and compare term by term. Report
   the differences explicitly rather than absorbing them.

## Hallucination tells

| Tell | What you see | What it means |
|---|---|---|
| Foreign symbols | The crop returns variables that appear nowhere on the slide (a `tr(·)` term, `mu`, an extra fraction) | The model is reconstructing a remembered formula, not reading. Discard and re-crop. |
| Repaired constants | The read is *exactly* the textbook version of the formula, suspiciously tidy | Highest-risk case: it may be fixing the slide's own error. Check against a raw crop. |
| Flat contradiction | One crop says the ratio is `|Σ₂|/|Σ₁|`, another says the tail cannot be read at all | Sub-region reads are unreliable; go tighter, and trust only glyph-level agreement. |
| Phantom absence | "No formula is visible" for a crop you know is on top of the equation | The crop is misplaced. Re-check the raster's rect before believing it. |

## Reporting it to the user

- Give the equation **as printed**, in a display block, before explaining any symbol — they read along
  in the PDF and need to see the same glyphs they are looking at.
- Then a **symbol table** (*symbol / what it is / shape*: vector `d×1`, matrix `d×d`, scalar), one row
  per glyph, including the ones that look obvious (the `½`, the transpose, the determinant bars).
- Then the **derivation** — where each symbol came from — and a plain statement of the payline (e.g.
  "set the two covariances equal and the quadratic terms cancel, leaving a straight line").
- Then the **flag**: which terms of the printed version disagree with the derivation, and whether the
  deck reuses the equation later. "Treat the printed constants as unreliable, carry the derivation" is
  the instruction the user needs; they are being examined on the course, not on the slide.
- Tell them the equation is a **raster image, so it will not copy or search** in the PDF — otherwise
  they will spend time trying to select text that isn't there.
- Keep the extracted rasters next to the deck's JSON cache so a follow-up question about the same
  equation costs nothing to answer.

## When the reader says the slide is wrong ("why isn't it …?")

A user handing you their own version of a formula is making a **claim that the page is wrong**, not
asking for a derivation. Settle it with three checks, in this order:

1. **Read the disputed glyph off the render** — ask the character-level discriminator ("what sign
   precedes the second summation?"). A question about the slide is answered by the slide, not by
   algebra, and this is the only check that can tell a misprint from a misreading.
2. **Find the same formula on an adjacent slide.** Decks print a formula correctly once and misprint it
   another time; the sibling page is the deck's own witness for the intended version, and it convinces
   the user far better than your derivation does.
3. **Settle it from the line the formula was derived FROM** — the single move that produces the
   disputed sign (a term crossing the equals sign flips it; only one direction of travel exists, so
   every moved term takes the same sign).

Then open the reply by naming which version is right; the user's version usually is.

**Falsify, don't just flag — run what the misprint implies.** For a formula defining an *iteration,
recursion or filter*, build the object the printed version produces (its iteration matrix), run it, and
quote where it lands. A sign flip in an iteration usually still **converges**, because the misprinted
form is itself a fixed-point iteration for a *different* system: the wrong Jacobi sign still had
$\rho(B)<1$ and still converged smoothly — to the exact solution of $(A+2U)x=b$, where $U$ is the
upper-triangular part of the split $A=D-L-U$, landing 0.4 away from the true solution. Two rules follow:

- **Validate an iterative solver on the residual $Ax-b$, not on the size of the increment**
  $x^{(k)}-x^{(k-1)}$. The wrong-system run passes every increment-based check, because its increments
  shrink exactly as fast as the correct one's — a stopping rule on successive differences cannot see a
  wrong sign, a residual test can.
- Quote the two numbers (the wrong limit, the residual it leaves) instead of saying "that would be a
  bug". The user hand-writes this code and the numbers are what stop them copying the slide.
