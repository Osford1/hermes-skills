---
name: consolidated-report-deliverables
description: "Use when compiling scattered records into one report or deck."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [report, consolidation, provenance, docx, pdf, markdown, verification]
    category: productivity
    related_skills: [experiment-session-report, pdf, docx, file-organization, grounded-citations]
---

# Consolidated report deliverables

For rolling a project's **scattered records into one report** and shipping it in a format the user
can forward (MD + DOCX + PDF). Distinct from `experiment-session-report`, which logs one live
session: here no new data is produced, so the deliverable's value is **completeness** (nothing in
the record is missed) and **honesty** (nothing unmeasured is invented).

## When to Use
- "Pull up the data from <project> — only the experiments and findings — compile it into a single report."
- "Send it over as a PDF." / any ask for a long report in a shareable format.
- A series of runs exists across several folders with no single write-up.
- A new artifact (a teammate's report, a late video, a log) arrives that must be folded into an
  existing compile.

## Phase 1 — Inventory before writing a word

1. Enumerate **every** place the project's records live: the working workspace, the wiki/vault
   `raw/<project>/` and any `translations/`, the media/report folder, the chat file drop
   (`C:/Users/<you>/Downloads/xwechat_files/<wxid>/msg/file/<YYYY-MM>/`), and any prior compiled report.
2. Sort by mtime so the newest artifacts stand out:
   `find <dir> -type f -printf "%TY-%Tm-%Td %TH:%TM  %10s  %p\n" | sort`
   An artifact newer than the last compile is usually exactly what the report is missing.
3. **Look for a prior compile first** and say in the report whether yours supersedes it. Extend it
   rather than silently re-deriving — the user may not remember it exists, and duplicating it wastes
   the work twice over.
4. Read or grep each source. For .docx/.pdf read the extracted text; never summarise a file you have
   not opened. Probe video evidence with `ffprobe` (duration, geometry, codec) so the report can
   describe it factually.

## Phase 2 — Report structure that survives review

1. **Master index table** — one row per experiment: ID, date, platform, config, observed outcome,
   evidence path. Completeness becomes checkable at a glance.
2. **Group by series, not by date** — real-hardware runs, software/simulation-only runs, and
   non-robot lab experiments each get a section; cross-cutting findings get one of their own.
3. **Findings only, and name the exclusions.** When asked for "only the experiments and findings",
   drop proposals, roadmaps, protocols, tutorials and coursework — then list them in an explicit
   *excluded on purpose* line so the reader knows the gap is deliberate.
4. **Measurement ledger — the honesty core.** One table: quantity → `measured` (with its value) or
   **NOT MEASURED**. Never estimate a number to fill a cell; if you truly must extrapolate, label it
   *inferred* and state from what. If every headline metric is empty, say so in bold: a series with
   no measured success rate IS the headline finding, not a gap to bury.
5. **Flag contradictions instead of resolving them silently** — e.g. one document asserts a setting
   the session log leaves blank, an artifact exists for a run the log says never launched, or a
   device index differs between data collection and evaluation. Report both readings.
6. **Provenance table** — every claim traceable to a path. If the machine clock disagrees with the
   artifacts' own timestamps, note the discrepancy and state that the report's dates are the
   artifacts' dates.
7. Conclusions state effects plainly, and mark qualitative observations as qualitative ("operator
   observed X" is not "measured X").

## When the report is for an outsider

Bankers, advisors, a supervisor, an interview panel — they read it once, cold, and share none of the
project's vocabulary. The same records, restructured:

- **Open with the plain sentence, not the architecture.** Who is involved, what money/scope is at
  stake, what the process does — then what it is **not** (no algorithmic execution, no prediction,
  no leverage, no options). The "not" list is what stops an outsider assuming the worst case.
- **Every piece of jargon gets one line at first use**, in a small term → what-it-does-here table.
  Assume nothing about their familiarity with the tooling; a reader who stalls on a term stops
  trusting the numbers behind it.
- **Order the results: process output → money → what went wrong, costliest first.** Process counts
  (how many evaluated, how many scored, how many rejected, the score range) establish that a method
  exists before any number is judged; a review that opens with the P/L reads as a story.
- **Every performance figure carries its benchmark and its denominators.** A return paired with the
  index over the same window; the return on capital actually deployed *and* on the total budget
  (both are true, and the first looks far worse); cost-basis approximations stated in the same
  sentence as the number, not in a footnote.
- **A price that ships is the latest completed session close, stamped in the artifact's header.**
  An intraday mark taken while writing cannot be reproduced the next morning and gives the reader
  nothing to tie it to; put the close date in the header, not in a footnote.
- **Convert process failures into dollars, with the counterfactual.** "The rule said sell and nobody
  executed" is the finding; the money sitting in that unexecuted call, plus what the corrected rule
  would have cost on the same position, is the evidence that anything changed.
- **Pre-answer the four questions an outsider always asks** — what is the edge, why the loss, how
  much is the tool deciding rather than the humans, what changes at larger scale. Short Q&A lines
  near the end, before they have to voice the doubt themselves.
- **Deliver the file, summarise in chat.** The full write-up goes as a forwardable file plus a short
  plain-text message carrying the same sections and every number (see `chat-message-delivery` for
  the ≤3200-char rule); the outsider gets the file, the user gets the gist on their phone.

## Phase 3 — One source, several formats

`soffice` is not installed on this Windows box, and bare `typst` only consumes `.typ` — so this
route builds the PDF from HTML instead. Note that `pandoc` **is** present at
`%LOCALAPPDATA%\Pandoc\pandoc.exe` (call it by absolute path; it may not be on bash's PATH), so if
the deliverable is markdown-only with no DOCX requirement, the shorter route is
`markdown-to-pdf-render`'s pandoc→typst pipeline — take this HTML route when DOCX is wanted too.
The verified route:

1. Write the report **once** as markdown, e.g. `Deliverables/MD/<name>.md`.
2. `scripts/md_export.py <src.md> <out.docx> <out.html> "<Title>"` produces the DOCX (python-docx)
   and a designed HTML in one run. Run it with the **miniconda python**
   (`C:/Users/<you>/miniconda3/python.exe`): it has python-docx; the Hermes venv python does not.
3. HTML → PDF with the `pdf` skill's bundled Playwright/Chromium renderer:
   `cd <pdf-skill>/scripts/html2pdf && node html_to_pdf.js "C:/abs/in.html" --output "C:/abs/out.pdf"`
   Use **native `C:/` paths** — Node does not translate MSYS `/c/...`.
   Keep the HTML Paged.js-safe: **no CSS `counter-*`** (Paged.js reorders the DOM and breaks them).
   Page numbers come from `@page { @bottom-center { content: counter(page); } }`, cleared on
   `@page :first`.
4. Keep all three: MD for edits, DOCX for submission, PDF for forwarding. Same content, one source.

### Deck (pptx) — when it has to be presented, not read

The same compile in another medium: same source markdown, same numbers, no new claims. Rules:

- **A named template beats your own design.** When the user says "use the official <institution>
  template", download the real file from the institution's own site, keep a working copy in the
  project's `Reference/`, and **clone its own slides** so every page inherits the master's title,
  rule and logo. Restyling a blank deck only approximates it.
- **Fill the slide.** A deck is rejected for thinness, not length: content stopping well above the
  footer reads as "too simplified" however good it is. Distribute leftover vertical space across
  table rows, and leave a ~0.3 in gutter rather than sizing to the exact body width.
- **Keep the rejected version.** Move a superseded deck to `Deliverables/_superseded/` and deliver
  pptx + PDF + a contact sheet; the user compares the two rather than discarding the old one.
- **Build it from a script kept beside the deck** (`deck/build-deck.py`), with all wording in one
  `CONTENT` block at the top, so an updated figure is a rerun rather than a hand-edit across slides.
- **Speaker notes on every slide.** The user presents from this deck; the argument and the caveats
  belong in the notes, not left implicit in the bullets.
- **Every slide gets a real title placeholder, and every slide is reviewed as pixels** before it
  ships. The build shape, the PowerPoint-COM render route for a machine without LibreOffice, the
  layout traps, the clone-an-official-template procedure, the density rules and the editorial shape
  for a supervisor-facing pitch deck are all in `references/pptx-deck-build-and-verify.md`.

Ship the `.pptx` **and** its exported `.pdf` (pptx to edit, PDF to forward) next to the project's own
docs, with the generator and render helper kept alongside them.

## Phase 4 — Verify, then file

- Read the HTML→PDF renderer's stdout: it reports page count, table count, blank pages and overflow.
- Extract the PDF text (`pdfplumber`, per page) and assert the load-bearing tokens are present —
  key numbers, table headers, section names, the author's name. A missing token is a real rendering
  fault; "it converted" is not verification.
- `pypdf`'s `Could not get FontBBox from font descriptor` lines on Chromium output are **noise**
  (emoji/symbol font fallback), not a defect — don't chase them.
- File per `file-organization`: deliverable in the project's `Deliverables/<TYPE>/`, the source
  material it was built from (someone else's report, the CN original, raw media) in `Reference/`;
  then update the scope's `_manifest.md` and `_INDEX.md`. Never move the live project folders.
- For a bilingual deliverable, follow the user's convention: **EN first, then CN**
  (see `experiment-report-bilingual`).

## Pitfalls

- **An artifact with no written record is evidence, not a result.** A video or log named for a run
  the records never mention proves the run happened, not what it achieved. Report it as "video
  exists, no log/hyperparameters/metric — outcome undocumented" and say which section it
  contradicts; do not infer the outcome. Deriving a plausible number here is the single most
  damaging failure mode of a consolidation report.
- **Two sources disagreeing is a finding. Pick neither.** Flag it in a dedicated discrepancies table
  with why it matters.
- **Don't let the compile imply more than was measured.** An operator's impression ("the motion
  improved") sits in the report labelled as an impression, next to the empty success-rate cells.
- **Adding an artifact can invalidate a prior claim.** When new material arrives after a compile
  (a teammate's report, a late video), state explicitly which sections it changes and offer to
  re-issue the affected deliverables rather than quietly leaving the old file authoritative.
- **Version drift across machines is a real finding, not noise.** When the same stack runs on two
  boxes with different library versions, that difference often explains why one path worked
  out-of-the-box and the other needed fixes — call it out in the report.
- **Deliverables are files, not chat text.** Long reports go as attachments (`MEDIA:` path); keep
  the chat message to the headline findings and what changed.

## Support files
- `references/pptx-deck-build-and-verify.md` — house shape for a deck deliverable, real title
  placeholders, the PowerPoint-COM → PDF → PNG render route when `soffice` is absent, the per-slide
  `vision_analyze` review, the layout traps that cost time, the clone-an-official-template procedure,
  the density rules, and the editorial shape for a supervisor-facing pitch deck.
- `scripts/pptx_to_pdf_win.py` — export a .pptx to PDF (and optional per-slide PNGs) with PowerPoint
  COM + poppler, for Windows boxes without LibreOffice.
- `scripts/md_export.py` — markdown → DOCX + designed HTML (Paged.js-safe CSS, tables, code blocks,
  blockquotes, inline emphasis) in one run; feed the HTML to the pdf skill's renderer for the PDF.
