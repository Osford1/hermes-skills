# Typeset maths in a PDF: what the text layer loses

A PDF that prints equations usually HAS a text layer, so it reads fine as prose and lies as
mathematics. These are the failure modes and the order of work that keeps a mis-extraction from being
reported as a defect in the source. Applies to lecture decks, worked examples, typeset numeric tables.

## Failure modes
- **Radicals vanish.** A printed `√5/2` extracts as `5/2` — a value that looks like a source error and
  is not. Any constant carrying a symbol (root, overbar, prime, superscript) needs the rendered page
  before it is quoted, and it must never be classified as a typo from the text layer alone.
- **Signs and glyphs get orphaned onto their own runs.** A minus joining two summation signs can
  extract as a separate line, so taking the runs in order reads the formula with the wrong sign; a
  recurring-decimal dot arrives as an Ethiopic syllable *before* the digit it sits over.
- **Matrices arrive as hand-laid ASCII art** or one character per run. Never type them from the dump —
  rebuild from the equations and check against the source's own printed results.
- **Bold/italic copy doubles glyphs**, so a column count off by one is usually extraction, not a typo.
- **The maths is often an embedded image**, in which case the layer has a gap exactly where the
  equations are — that gap is information, not an empty page.

## Order of work
1. Extract the text layer for *navigation*: page markers plus visual-line grouping (`x,y | text`) is
   enough to see the slide count, the structure, and which pages carry maths.
2. Render every page to PNG (pymupdf, 200–320 dpi) and `vision_analyze` the pages that carry signs,
   matrices, radicals, sub/superscripts or a numeric table. Prose pages can be taken from the layer
   as-is. Batch several pages per call; this is the cost of the job.
3. **Re-derive every asserted number in exact arithmetic** (sympy / `fractions.Fraction`) *before*
   drafting, so no table cell gets written twice — a render that corrects the draft means re-drafting
   every cell it touched.
4. Reconstruct each derived object from the printed primitive and require the source's own printed
   follow-ons to fall out of it (an iteration matrix from the printed matrix, then its printed
   characteristic polynomial, eigenvalue and ρ). See the SKILL.md checklist *Auditing teaching
   material* for how to classify a mismatch — artefact, rounding, ordering, or real defect.
5. Keep the printed object verbatim on the page, with the verdict in the checks section rather than a
   silent correction in the line.

## A crop beats a full-page read
When one symbol decides the value, re-render that region alone at 2–3× and read the clip
(`page.get_pixmap(dpi=600, clip=pymupdf.Rect(x0, y0, x1, y1))`). Two reads at the same resolution are
not independent views; a higher-resolution crop outranks a full-page read when they disagree, and
three-way disagreement means *could not read*, not the most plausible candidate.
