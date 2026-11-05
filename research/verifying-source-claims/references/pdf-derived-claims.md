# Claims drawn from a PDF source

When a derivative artifact (summary, diagram, report) restates a source's numbers, sections or results, check the derived content against the source *text*, never against recall.

## Extract once, then grep each value
- Pull the source text to a temp file once, then grep each individual value. Do not re-extract per question.
- **Grep with `-a`.** Extracted PDF text is frequently sniffed as binary, and plain `grep` answers `Binary file … matches` instead of the matching lines or counts.
- PyMuPDF does the extraction reliably: `fitz.open(path).get_text()`.
- Grep for the exact figure the artifact prints, plus a looser pattern for the same quantity, so a transcription slip surfaces as a mismatch rather than as silence.

## Labels that must map to the source
- Any section/subsection number, figure or equation reference on a derivative artifact must be the numbering the SOURCE uses for that content. Reconcile each one against the extracted heading list (e.g. `grep -aE '^\s*(I|II|III|IV|V)\.\s+[A-Z]' `) before shipping.
- Content that is the second half of a subsection belongs to that subsection — do not promote it to the next free number. **A wrong label passes every format and lint check**, because validators read structure and markup, not meaning. This reconciliation is always manual.

## Claim strength
- Do not upgrade the source's epistemic status. If it leans on an anytime property rather than proving convergence, the artifact says *anytime*.
- Quote complexity and performance expressions as written. Glossing them into a friendlier shape ("near-linear in K") asserts something the source did not claim.
- Where the source quantifies a result across runs, carry both the mean and the worst case if the source reports both; a single number drops the caveat the source kept.

## Report
State which values and labels were checked, and against what text, rather than reporting that the artifact "matches the paper".
