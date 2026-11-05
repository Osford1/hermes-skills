---
name: brain1-wiki-agent
description: "Brain 1 Obsidian vault wiki agent: ingest/query/lint/add."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Obsidian, wiki, notes, ingest, knowledge-management]
    related_skills: [obsidian]
---

# Brain 1 — Wiki Agent (LLM)

You are the wiki agent for the **Brain 1** Obsidian vault. The vault's `CLAUDE.md`
is the **source of truth** for all conventions — read it in full at the start of any
session working in this vault, before anything else. This skill adds the durable,
repeatable layer (exact paths, the operations, the PDF tooling) so behavior stays
consistent across sessions.

## When to Use
Load this skill whenever we work in the **Brain 1 Obsidian vault** — the user asks to
ingest a source, answer a question from the wiki, run a lint/health check, add a page,
or continues the robot-arm / BTCH30003 / investing work described there. Trigger words:
"Brain 1", "the vault", "ingest", "the wiki", subject names (NEUR30002, ELEN30014,
BTCH30003, MCEN30021), or any page path under the vault root.

## Vault location (resolve this, don't guess)

```
C:\Users\<you>\OneDrive\Documents\Desktop\Brain 1
```

- Path contains spaces → **prefer file tools** (`read_file`, `write_file`, `patch`,
  `search_files`) over shell commands whenever possible; resolve the absolute path first.
- On Windows/git-bash the MSYS form is `<vault>`.
- Pass native forward-slash paths (`C:/Users/<you>/...`) to native Windows tools.

## Read this first

1. `CLAUDE.md` (vault root) — schema + rules. Re-read at session start.
2. `index.md` — the catalog. Read it first when answering a query; it lists every page.
3. `log.md` — append-only operations timeline (shows what has been done / the established practice).
4. `tasks.md` — daily/weekly tracker (Today / This Week / Backlog / Waiting / Done).
5. `questions.md` — parking lot for non-urgent open questions.

## `tasks.md` is USER-OWNED — read-only (hard rule, 2026-10-12)

The user maintains `tasks.md` himself and asked, after repeated unwanted edits: **never
change anything inside it unless he explicitly asks for that file.**

- Reading it is fine and encouraged (deadline context). Writing is not.
- This overrides every other instruction in this skill, including the ingest step that used
to "carry syllabus dates into `tasks.md`'s deadline radar" and the parent-only reservation
that let the parent edit it during a multi-agent ingest. Neither happens any more.
- Subagents were already told to keep their hands off it — say so again in every brief.
- When an ingest produces something that *belongs* in `tasks.md` (new deadlines, new
tasks, status changes), **report it in chat as a proposed edit and wait**: "I'd add to
`tasks.md`: <exact lines>. Want me to?" Only write after an explicit yes, and then only
those lines — never a restructure or a re-flow of the sections.
- Same courtesy for any other file the user has not asked you to touch. If a change is
"obviously" wanted, still ask.

## Directory structure (actual)

```
Brain 1/
├── CLAUDE.md            ← schema + rules (source of truth)
├── index.md             ← catalog; update on every ingest/query-filing/lint
├── log.md               ← append-only operations timeline; append on every op
├── tasks.md             ← task tracker
├── questions.md         ← open-questions parking lot
├── moving-inventory.md, Robot arm manufacturing plan.md  ← operational notes
├── raw/                 ← IMMUTABLE user sources — never modify (read/analyze only)
│   └── assets/          ← the ONE sanctioned write dir: rendered/extracted figures for wiki pages
├── .claude/skills/extract-pdf/  ← the PDF-extraction skill (PyMuPDF)
├── Collab Investing/    ← sibling stock-research project (own CLAUDE.md, read-only from here)
└── wiki/
    ├── sources/                            ← a few recent source pages (e.g. 2026-07-21 ROS2 course)
    ├── synthesis/sources/                  ← established home for most source pages (YYYY-MM-DD-slug.md)
    ├── entities/                           ← people/orgs/products/subject-hubs (flat)
    ├── concepts/<domain>/                  ← ideas/frameworks (domain groups)
    └── synthesis/<domain>/                 ← analyses, active-recall sets, quizzes/, meta/
```

**Important location nuance:** `CLAUDE.md`'s tree names `wiki/sources/` for source pages,
but the actual established practice is `wiki/synthesis/sources/` (a convention noted in
`log.md` 2026-07-01). Some recent batches (e.g. the ROS 2 course) used `wiki/sources/`.
**Rule:** when writing/updating a source page, match the location of the *adjacent
existing* source pages (check `index.md` → Sources). Don't create a new subfolder unless
the user asks or no precedent exists.

Domain folders (canonical — don't invent new ones without asking):
`neuroscience`, `robotics`, `biotech-pharma`, `finance-investing`, `signals-circuits`,
`digital-logic`, `optimization-math`, `ai-hardware`, `computing`, + `meta/` under synthesis.

## Naming convention

All wiki filenames lowercase-hyphenated, no spaces:
- Sources: `YYYY-MM-DD-slug.md`
- Entities: `firstname-lastname.md` or `organization-name.md`
- Concepts: `<domain>/concept-name.md`; Synthesis: `<domain>/topic-or-question.md`

## Page frontmatter

```yaml
---
title: "Human Readable Title"
type: source | entity | concept | synthesis
tags: [tag1, tag2]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [wiki/synthesis/sources/slug.md]
related: [wiki/concepts/foo.md]
---
```
Omit fields that don't apply. Always bump `updated` when editing.

## Operations

### INGEST (source dropped in `raw/`, user says "ingest X")
Collaborative — you MUST brief the user and get confirmation before writing.
1. Read source in full (use extract-pdf for PDFs — see below; figures matter).
2. Brief: 3–5 bullet key takeaways + ask "anything to emphasize/de-emphasize?"
3. Wait for confirmation / adjustment.
4. Write source page (`wiki/synthesis/sources/YYYY-MM-DD-slug.md`).
5. Update/create entity pages. 6. Update/create concept pages.
7. If a notable insight → write a synthesis page.
8. **Backfill the per-topic concept index** on the source page (see below).
9. Update `index.md` (add all new/updated pages) → 10. Append to `log.md`.
11. Report the list of files touched.
Expect a single source to touch 5–15 wiki pages — that's normal and good.

**Source page structure — per-topic concept index (the navigation hub):** under every
`## topic` heading that relates to concept page(s), put a bold `**Related concept pages:**`
bulleted list **before the prose**, one concept per line, each with a one-line
*why-it's-relevant-to-this-section* gloss. List EVERY concept the section touches, even if
also linked inline. Only sections genuinely related to concepts get the index (no
"none" lines). Add/finalize these in step 8 once the full concept set is known.

**On contradiction:** if a new source contradicts an existing wiki claim, update the page
to note BOTH positions with source citations — do not silently overwrite. Flag it to the user.

**Provenance discipline:** research-front / primary-source teaching (e.g. Song Yao's own
neurogenesis, Andrew Allen's sympathetic-respiratory coupling, Menuet 2017) — add a
"Provenance note" callout and keep claims labeled as the lecturer's own work, not textbook.

### QUERY (user asks a question about the wiki)
1. Read `index.md` → find relevant pages. 2. Read those pages.
3. Synthesize with inline wiki-links. 4. Ask "should I file this as a synthesis page?"
   If yes → write to `wiki/synthesis/<domain>/`, update `index.md` + `log.md`.
Match output format to the question (prose / table / list / comparison).

### LINT ("lint the wiki" / "health check")
Report: orphan pages · concepts cited in multiple pages but missing their own page ·
contradictions · stale claims · missing cross-refs · data gaps. Then ask which to fix.

### ADD PAGE (create a page directly, not from a source)
Follow frontmatter + naming; update `index.md`; log it.

## PDF extraction (the figures gateway)

The old agent's `extract-pdf` skill uses **PyMuPDF** because `pdftoppm` isn't installed.
It IS available here — verified: `/c/Users/<you>/miniconda3/python` has `fitz` (PyMuPDF). Use it:

```bash
/c/Users/<you>/miniconda3/python \
  "<vault>/.claude/skills/extract-pdf/extract_pdf.py" \
  "<vault>/raw/<file>.pdf" \
  [--mode auto|text|pages|all] [--pages 4-9] [--dpi 200]
```

- `auto` (default): slide decks → render every page to PNG; prose → text + figure pages.
- Output: text to temp; figures to `raw/assets/<stem>/page-NN.png`; a `<<<JSON…>>>` summary
  with the `rendered` array.
- THEN read the rendered PNGs with vision and the text dump — this is how you actually SEE
  the diagrams. Link figure-important ones inline relative: `![label](../../raw/assets/<stem>/page-NN.png)`.
- Guardrails: never modify `raw/` source PDFs (read/render only); `raw/assets/` is the one
  sanctioned write; cap rendering (default 80) — re-run with `--pages` if hit.

### Scanned PDFs (no text layer) — the OCR path

Some `raw/` sources are image-only scans (e.g. the Brooks & Iyengar textbook chapters in the
multisensor-fusion folder). Detection: `fitz.open(p)[0].get_text().strip()` returns `''` and
`get_images()` is non-empty. Then:

- OCR with **rapidocr_onnxruntime** on the miniconda python: render each page at 250 dpi
  (`page.get_pixmap(dpi=250).save(png)`) then `RapidOCR()(png)` → join `r[1]` for each hit.
- Write OCR text to a **working dir OUTSIDE the vault** (e.g.
  `$LOCALAPPDATA/Temp/<task>/txt/`) so `raw/` stays untouched and the dumps aren't clutter.
  One `===== PAGE n =====`-delimited file per source; write the file only at chapter end so a
  present file is a complete file (makes re-running the script safely idempotent).
- OCR ~50 book pages takes several minutes — start it in the background FIRST, then do the
  rest of the work while it runs.
- OCR mangles headings and hyphenation and loses hierarchy; recover the real section structure
  and any diagram/algorithm box with `vision_analyze` on a rendered page. Always label OCR-derived
  pages as OCR-derived in the wiki page, and mark unreadable sections as unreadable.
- `.rar` reading packs: `bsdtar -tf <file>.rar` lists contents (bsdtar ships with miniconda).
  List them to document what the assigned reading is; do NOT extract into `raw/`.

## Course lecture decks (`.pptx`) — the ingest path

When a course's own slides arrive (often the first real teaching material a syllabus-only course has produced, closing several of its plan's open items — and able to *contradict* the syllabus):

- **Do NOT parse a big `.pptx` with python-pptx.** Open it as a zip and read `ppt/slides/slideN.xml`, pulling `<a:t>` runs per shape (split on `<p:sp>|<p:pic>|<p:graphicFrame>`); use `ppt/slides/_rels/slideN.xml.rels` to map a slide to its `ppt/media/*` images and `ppt/notesSlides/*` for speaker notes. Fast and immune to embedded media — a 624 MB deck (10 mp4 + 2 mov inside) read in seconds.
- **To see the diagrams, render the slides.** `win32com.client.Dispatch("PowerPoint.Application")` → `Presentations.Open(path, ReadOnly=True, WithWindow=False)` → `Slides(i).Export(png, "PNG", 1400, 788)`. That deck opened in 2.7 s and exported 30 chosen slides in 7 s. PowerPoint is installed and `pywin32` is in the miniconda python. The WMF/EMF files inside the zip are the original vector figures and are not readable — always render.
- **Delete the extracted media once the renders exist.** Dumping every `ppt/media/*` duplicated each embedded video and put **1.2 GB** into `raw/assets/`; keeping only `slides/*.png` + the manifest took it to 36 MB (the videos remain inside the untouched source deck). Check with `du -sh` — this vault lives on a nearly-full C: drive.
- **Verify multi-panel figures per panel, never from a montage.** A 2×2 montage vision read of an "order = 1/2/3/9 polynomial fit" sequence produced a *wrong* colour→order mapping (it captioned a "short green segment" that is really the order-2 curve, and gave the blue curve orders 2–3). Counting colour bands per slide with PIL settled it in seconds: the fits are **cumulative overlays**, one added per slide. The deck's own **red heading text contaminates colour counts** — compare relative counts across slides rather than thresholding one.
- **A deck and its syllabus can disagree on grading.** Write both positions side by side and call it a contradiction; a logistics deck dated in the current term usually outranks an undated syllabus, but say so as an inference. Give week-number→date estimates only as **labelled arithmetic**, with a note to confirm against the real calendar.
- Course-administration facts (lecturers, offices, textbooks, prerequisites, teaching order, project deadlines, report format) belong on **both** the study plan and their own source page: the source page carries the argument, the plan carries the actions (deadlines marked in the week table, gates/KRs extended, glossary extended, open items closed and added).

## Semester courses

When the user drops course folders (Chinese-named) into `raw/`:

- **Study plans live in `wiki/synthesis/courses/<subject-slug>-study-plan.md`**, with
  `wiki/synthesis/courses/index.md` as the semester map + credit audit. The index carries the
  course table (code/group/credits), the requirement-group audit, the ingested-material status
  table, and a flagged-issues list. Update the index whenever a new syllabus arrives.
- A study plan must be *specific to the user*, not a topic list: header block (code, credits,
  language of instruction, lecturer, assessment — say "unknown" rather than inventing), topic
  map with a why-it-matters-to-him column and priority flags, prior-knowledge bridge
  (already-know vs formal-gap per topic), week-by-week schedule, active-recall artefacts,
  a Chinese-English glossary of the terms he'll hear (courses are taught in Chinese), and an
  "Open items to confirm with the lecturer" list. Never invent exam dates or calendar dates.
- Cross-link each plan into his live projects (robot arm, motion-ff-lab, A17 machining,
  ROS 2 stack) — that is what makes it worth keeping.
- **Filing rule — concepts go by COURSE, not by domain.** The user overrode the original
  domain-filing design (2026-09-15) because it was confusing. One folder per subject:
  `wiki/concepts/<course-slug>/` — e.g. `multisensor-fusion/`, `engineering-mathematics/`,
  `machine-learning/`. This applies to **any material the course prescribed, including research
  papers sitting in the course's `Lecture notes/` folder** — the rule keys on where the material
  lives, not on whether it is a slide deck. Only genuinely *independent* reading (a paper ingested
  on its own merits) keeps its domain folder (`optimization-math/`, `robotics/`, …).
- **Course material is ALSO laid out per course:** `wiki/synthesis/courses/<course-slug>/<course-slug>-study-plan.md`,
  with that course's bilingual/lecture pages beside it and `courses/index.md` staying at the root
  as the semester map. **Filenames deliberately keep their subject prefix** — five files named
  `study-plan.md` would make Obsidian's short-form `[[…]]` resolution ambiguous, so don't "tidy"
  them into shorter names.
- **A lecture delivered as a research paper still yields a source page**
  (`wiki/synthesis/sources/YYYY-MM-DD-<author>-<year>-<slug>.md`) *and* concept pages. First check
  whether the assigned set contains a **contradiction**: if two prescribed papers disagree, write
  ONE reconciliation page yourself (`wiki/synthesis/<domain>/`) rather than letting one subagent
  per paper each assert their own side. Give each child its paper's position plus an explicit
  instruction NOT to adjudicate, and hand both children the exact path of the page you will write
  so they can link it.

## A syllabus (or any single course file) arriving from chat

When the user drops one course document from WeChat/Downloads ("this is the syllabus for X, add it to my obsidian"):

- **File it first, then write.** Copy it byte-for-byte into `raw/<course-folder>/Lecture notes/` — the sub-folder
  every course folder in `raw/` already uses (`Own notes/` is the user's own, and a 0-byte stub there was already
  flagged as clutter, so don't create one). Verify the copy with a sha256 comparison against the source; `raw/` sources
  are never modified, and `cp -p` keeps the original timestamps and read-only mode.
- **The deliverable is not the file.** For a course, the expected artefacts are the **course page** and the **study
  plan** — the semester map's flagged issues already say the plan "can't be written until the syllabus exists", so
  the ingest is what closes them. Write both, plus the lecturer as an entity page, and update `courses/index.md`
  (course-load row, material-status row, flagged issues, folder tree), the root `index.md` and `log.md`.
- **An English-language syllabus still gets the bilingual treatment.** The convention `…-syllabus-bilingual.md` is about
  the *annotation*, not the source language: keep the document's English and add **pīnyīn + a one-line English gloss for
  every Chinese character it hands out raw**. A course aimed at students with no Chinese hands out long bare-character
  lists (vocabulary, names, plaques) with no readings — that is the highest-value thing you can add, and it doubles as
  the drill sheet for any brush/calligraphy assignment.
- **A dated syllabus outranks week numbers.** Rare, and worth shouting about: one syllabus in this vault states real
  dates for all 15 lectures and both deadlines while stating no assessment weights, i.e. the mirror image of every other
  course (marks without dates). Use its real dates as the anchor for reading everyone else's "week N" — but do NOT write them into
  `tasks.md` (see the hard rule above); propose the lines in chat and wait for a yes.

### Vision vs the text layer on dense CJK — the text layer usually wins

Reading a rendered page (170 dpi) with `vision_analyze` is still the right way to check a date or a weight, but on
*characters* it is unreliable in a specific, predictable way: it substitutes a common glyph for a rare one. In one
syllabus it returned 白**鹤** for 白**鹇**, 搏埴 for 摶埴 and 造**棋** for 造**栱** — three words out of canonical lists
(the Qing 补子 rank badges, the 考工记's craft divisions, the 营造法式's bracket nomenclature) where the text layer was
right all three times. **Rule: when vision and a text layer disagree on a character that belongs to a known list, check
it against the list and trust the text layer; then record the disagreement on the page rather than smoothing it over.**

The same trap sits in `read_file`'s own extraction: a rare glyph came through as `张希���式雷` where the actual text is
`张希圣，样式雷`. Dump the text with PyMuPDF (`page.get_text()`) before quoting a character run.

### Table escaping and checker false positives

- **`\\|` inside a wiki-link in a GFM table is broken.** Five rows of `courses/index.md` carried a *double* backslash
  before the display alias (`…-study-plan\\|Study plan]]`), which splits the cell and leaks a stray `\`. Repair to a
  single `\|` when you touch such a table, and say so in the log.
- **A link checker that captures the target must strip a trailing `\`** (the escaping artefact), or it reports every
  table-row link as dangling — 6 phantom breaks in one run. Same family as the `.md`-before-`.md` bug: fix the checker,
  not the vault.

## Running a large ingest in parallel

For a multi-deck/multi-chapter ingest, split it across subagents — one per lecture/chapter —
but:
- **Reserve `index.md`, `log.md` and `tasks.md` for the parent agent.** Tell every child
  explicitly not to touch them, or ten writers will clobber the catalog.
- Give each child an explicit page list (exact paths) and tell it which concepts it OWNS, so two
  children don't both invent `bayesian-inference.md`. Sibling pages that don't exist yet are
  still cross-linked — the ingest completes together.
- **Verify your own brief against the source BEFORE dispatching it.** A wrong claim in a brief becomes
  a claim in the vault unless the child pushes back — subagent briefs are where a bad fact enters an
  ingest. In one ingest my brief asserted a 1.4 T sparse-MoE experiment and an `N^0.66` aspect-ratio
  result that **neither paper contained**, plus wrong section maps for both; the children searched the
  full text, refused to write it, and flagged it. So: (a) check each factual assertion you put in a
  brief against the extracted text, and (b) **explicitly instruct children to flag brief errors rather
  than fit content to your outline**, and to follow the paper's real structure when your outline is wrong.
  Then honour the flag — fix your own catalogue entries, since the child's page may be honest while the
  parent's `index.md`/`log.md` entries repeat the error.
- Repeat the full house-rules block in every child's context; they cannot see each other's
  instructions. Tell them the figure depth (raw/assets/<slug>/ + `vision_analyze` before
  captioning) or they will skip figures entirely.
- **Expect — and welcome — children who correct your brief.** In one ingest a child's per-panel
  pixel check overturned a figure caption in *my own* source page, and another caught two false
  claims in my brief (a slide that does not name self-supervised learning, and a screenshot whose
  query I had mis-transcribed from my own earlier vision read). **Verify the correction yourself,
  then fix the parent's page** — and log the correction, or `index.md`/`log.md` keep carrying the error.
- Pre-extract deck text to the working dir yourself so children don't each re-parse a 200-page
  PDF. For `.pptx`, reading the slide XML from the zip (see *Course lecture decks* above) works for
  any size; note that deck equations are often embedded images, so the text has gaps exactly where
  the maths is — warn the child and let it triangulate against a text-layer companion (e.g. the
  Welch & Bishop Kalman tutorial that sits next to the Kalman deck) instead of inventing equations.

## House style & preferences

- **Translated pages are named after their SOURCE file, not after the course.** The user renamed the whole engineering-mathematics folder: `engineering-mathematics-ch22-slides-bilingual.md` → `2.2-线性方程组直接法(translated).md`, matching `raw/…/2.2-线性方程组直接法.pdf`, with the `.pdf` snapshot taking the same stem. Use ASCII parens, keep the marker identical across the pair, and name future translations the same way. Two judgement calls to repeat: a study plan keeps its `…-study-plan.md` name (it translates nothing), and when the source name is **mojibake** (a `.doc` whose name is GB2312 read as cp1252) use the readable Chinese form of the same document (`工程硕士数学教学大纲(translated).md`) and say so in the log.
- **Clean-up means "out of the vault", not `rm`.** Derived artefacts (render-check `*.png`, `cmp_*.png` comparisons, `.typ`/`.main.typ` build files, `.body.md` working copies) go to `%LOCALAPPDATA%\Temp\brain1-<course>-cleanup-<date>\` so they are recoverable, and the vault keeps only content markdown + content PDF. Before removing a `.body.md`, prove it is a working copy: a CJK-stream diff showing it 100% covered by the canonical page, with identical headings.
- **A rename is not done until a vault-wide resolver says so.** After renaming, substitute the stem (it also hits `related:` frontmatter, inline links and the ops header) and then re-run the resolver built over **every** vault file, reporting the dangling count. Update historical path strings in `log.md` in place — paths only, never the claims — and record in the new log entry that you did, so the append-only timeline stays readable and nothing dangles.
- **Windows file locks block renames.** A PDF the user has open in a viewer cannot be renamed (`WinError 32`, sharing violation). Retry a few times, then leave that one file and report it — never force, never delete to work around it. Expect the `.md`/`.pdf` pair to end up half-renamed when this happens.
- **Do a filesystem/link job directly, not via a subagent.** It is link-sensitive work on the user's vault where verification is cheap for the parent (a resolver run, a folder listing) and expensive to delegate.

- **Plain-English / "high-schooler with key terms kept"** explainers; analogies; inline
  jargon glosses (expression, phosphorylation, GPCR, synapse, etc.).
- Keep the user's own margin notes / `[Your thoughts:]` blockquotes verbatim (fold stray
  casual notes into clean `> [Your thoughts:]` blocks).
- Flag **honest negatives** — budget overshoots, "the counterintuitive result," unverified
  items (mark suspicions as suspicions, not findings). Verify a thing exists before committing to it.
- Active-recall sets: `#/Question/Answer` tables with `> **A:**` blockquote answers, by
  topic, ⭐ high-yield flags, trailing "thoughts" blockquote.
- Interactive quizzes live in `wiki/synthesis/<domain>/quizzes/` (self-contained HTML, green
  dark theme, instant-feedback toggle, per-topic score breakdown), registered in a quizzes
  `index.md` table.
- Cross-link domains through `related:` frontmatter and `[[wiki/<other-domain>/page]]` links —
  don't duplicate pages.

## Every operation ends with
- `index.md` updated (Entries/categories + top `updated`/`last_op`).
- `log.md` appended as `## [YYYY-MM-DD] <operation> | <summary>` listing files touched.
- `raw/` source files untouched.
- `tasks.md`, `questions.md` and every other user-owned file untouched unless the user
  explicitly asked for that file in this session. `tasks.md` in particular is read-only by
  default (hard rule, 2026-10-12) — propose edits in chat instead of making them.

## Verifying your own work (do this — several of my own checks were wrong before the pages were)

A link/lint checker that is itself buggy is worse than none: it manufactures false alarms and hides
real breakage. When you write one:

- **Strip a trailing `.md` BEFORE re-appending it.** `os.path.exists(f"{root}/{link}.md")` on a link
  written `…/page.md` tests `page.md.md` and reports a false break. Obsidian accepts both forms.
- **Ignore `[[*.png]]` / `[[Pasted image …]]` embeds and documentation placeholders.** Attachment
  embeds resolve against non-`.md` attachment files, so a `.md`-only resolver flags dozens of
  perfectly good embeds (67 of 92 "dangling" hits in one run). Build the resolver's name set from
  *all* vault files, and skip placeholders in `CLAUDE.md` / `Welcome.md` / prose about link syntax
  (`[[…]]`, `[[path/to/page]]`, `[[wiki/<other-domain>/page]]`).
- **Never write notation in bare double brackets.** `[[R, p], [0, 1]]` or `[[a₁₁, a₁₂]]` written as
  matrix notation is parsed by Obsidian as a wiki-link and renders broken; wrap it in backticks.
  This bug has already produced a junk note file whose *name* is matrix notation.
- **Compare timestamps as FULL datetimes, never hour:minute alone.** A "was this file written during
  my turn?" test that ignores the date fires on the **previous session's** edits whenever they share
  a clock time, and wrongly reports subagents as having touched reserved files.
- **Prove a reserved-file violation from CONTENT, not mtime.** Grep the reserved files for the topic
  of the work; no hit means no child logged there. Something outside your session may also touch a
  file's mtime — check `tasks.md` against the user's own edits before accusing a child.
- **A slides page built from a PDF text layer is unreadable until it is LaTeX.** The text layer pastes mangled Unicode maths (`𝑎𝑖11`, `𝛥𝑖`, `Σ(k=1..n)`) into every Chinese line *and again* into that line's pīnyīn, and matrices arrive as hand-laid ASCII art in fenced blocks (87 of them on the Ch 2.2 page, with 0 display maths). Convert every formula to `$…$`/`$$…$$`, reduce the pīnyīn parenthetical to the Chinese words only (symbols and numerals dropped — the Ch 2.3 page's convention), then verify: per-environment `\begin`/`\end` counts (`\begin{array}` also matches prose *mentioning* it), the column count of every table line with `\|` treated as literal, and `pandoc page.md -t html5 -o out.html` for zero `Could not convert` fallbacks. Three traps found this way: (a) a recurring-decimal dot extracts as **U+1236, an Ethiopic syllable, emitted *before* the digit it sits over** — settle it by arithmetic against the slide's own solution, never by reading; (b) a bare `|entry|` or `[[link|alias]]` inside a table cell splits the row into extra cells; (c) a line inside a fenced block that begins with `|` looks like a table row to any naive checker, so count rows before believing a table lost data. Prove nothing was dropped with a CJK-only `difflib` diff of old vs new (report unmatched runs ≥6 characters), not with a whole-line match — the maths rewrite changes every line by construction.
- **Before moving or renaming pages**, check what depends on the old form: relative markdown links
  (`](file.md)`) break on a move, and bare-basename wiki-links break if two pages end up sharing a
  basename. Grep for both before committing to a layout.
- **A checker that normalises text reports a different size than the raw file — that is not an
  external edit.** A "9 characters vanished from the study plan" alarm was my own checker doing
  `.replace("\\|", "|")` on escaped pipes and `.read()` collapsing 378 CRLF pairs; the file was
  byte-identical. Before accusing a child of writing a reserved file, re-measure with the *same*
  method (`len(open(p).read())` ≠ `len(open(p,'rb').read())` on this vault).
- **Verify a child's page after it FINISHES, not when the file first appears.** One child wrote its
  page, then merged and renumbered it (24 sections → 20) minutes later; a link check run in between
  validated a state that no longer existed. If a child renumbers sections, **check its internal
  `§N` / "see section N" cross-references for dangling targets** — and remap them by context, never
  by global substitution, because the old and new numbers overlap (`§18`/`§19` were both valid
  before *and* after the merge, pointing at different sections).
- **Recount derived numbers from the source before trusting them.** A subagent's diff table said a
  bibliography went "7 entries → 8"; counting the entries in both extracted documents showed
  **8 → 9** (the reviewer had missed an entry that was already there in both years). Counts of
  entries, criteria, sections and pages are the easiest thing to get wrong and the cheapest to check —
  and when one child flags another child's number, treat the flag as a claim to verify, not to average.

- **Never write a long log/index entry as an inline Python string.** LaTeX-laden prose in a normal Python string eats real characters: `\frac` → form-feed, `\rho` → CR, `\approx` → BEL, `\begin` → backspace — and the file *looks* written (2–3 control characters buried in 6 KB of prose, no error). Write the entry to a `.md` with the file tools and append that, then audit the result: `{hex(ord(c)): … for c in set(text) if ord(c) < 32 and c not in '\r\n\t'}` must be empty.
- **Diff a new deck against the previous one BEFORE translating it.** `difflib.SequenceMatcher` on whitespace-stripped `page.get_text()` for every page pair, and print the best match per page with its ratio: consecutive decks in a course repeat the previous deck's tail verbatim (0.92–1.00 here), which turns "annotate 32 slides" into "map 7, translate 25". Also diff the *overlapping* pages against each other rather than eyeballing — the only real differences are then visible (a changed heading, one dropped sentence, one added special case), and they are exactly what a reader of the second file needs told.
- **Check whether the deck's printed footer matches its PDF page.** One maths deck numbered its slides one less than the physical page (slide 8 printed "7"), so every quoted "slide N" lands a slide early; say the offset in the page and use PDF page order throughout.
- **Running `index.md`'s ops header: demote, don't delete.** The header keeps the newest op on its own line and prefixes the previous one with `‖ Prior: `; older entries live on in `log.md`. Say in the log that a header line moved out of the header, so nobody later reads the removal as lost content.

## Pitfalls
- **A `raw/` file ending `.doc` may actually be a DOCX (OOXML zip).** Tsinghua/Chinese sources arrive with mangled extensions. `read_file` will fail with "document extraction failed"; confirm with a magic-byte check (`open(p,'rb').read(2) == b'PK'`), then `zipfile.ZipFile(p).read('word/document.xml')` and strip `<w:t>` tags per `<w:p>` paragraph. Do NOT try utf-16/GB18030 decoding of the raw bytes — it produces plausible-looking CJK garbage.
- **Mojibake filenames in `raw/` are real filenames.** Copy them byte-for-byte (e.g. `Advanced Manufactuing Technology½ÌÑ§´ó¸Ù (1).doc` = 教学大纲 in GB2312→cp1252). Don't "repair" them; use `os.listdir()` in python to obtain the exact name rather than retyping it — retyped names silently fail to resolve.
- `raw/` is immutable — never edit a source; the only authorized write is to `raw/assets/`.
- Don't invent new domain folders or `wiki/` subfolders without asking the user.
- Path has spaces — don't rely on shell globbing; use file tools or quoted paths.
- The Hermes venv python has NO pip; use the **miniconda** python (`/c/Users/<you>/miniconda3/python`)
  for anything needing libraries (fitz, pdfplumber, numpy, etc.).
