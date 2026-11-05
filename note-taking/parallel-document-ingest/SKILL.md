---
name: parallel-document-ingest
description: "Use when many sources must become cross-linked notes."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ingest, documents, delegation, subagents, notes, knowledge-base, ocr]
    related_skills: [obsidian, ocr-and-documents, file-organization]
---

# Parallel Document Ingest

Use when the user drops **more sources than one context can hold** — a folder of lecture decks, a
batch of papers, a set of syllabuses, a whole course — and wants each turned into structured notes
that cross-link. One agent can do it, but it will skim or truncate. Splitting across subagents works
only if you avoid two failure modes: **two writers inventing the same concept page under different
names**, and **N writers clobbering the shared index**.

## 0. Ask the placement questions ONCE, up front

Bulk ingest forks on schema decisions the user cares about: where the new pages live, whether a new
top-level folder/domain may be created, how deep to go (whole decks? the textbook chapters they sit
next to? the reference-paper archives?). Put **every** such question into a single form before
writing anything.

- These questions are independent, so one batch costs one round trip. Discovering a fork mid-write
  costs rework or leaves a dangling link.
- Put your recommended default first in each question, and carry the reason in the question text so
  the user can disagree with the reasoning, not just the option.
- While you wait, do the parts that don't depend on the answer (inventory, extraction, the pieces
  whose placement is already settled).

## 1. Inventory before you assign anything

Never size the work from filenames. Probe every source and write the result down:

- sizes and counts per folder;
- for PDFs, **page count plus the first ~200 characters of page 1** — that one line usually identifies
  the document (lecture deck vs paper vs scanned textbook);
- for `.pptx`, slide count and the first few slides' text;
- which files are **archives** (`.rar`/`.zip`) — list their contents, and do not extract into the
  user's source tree;
- which PDFs have **no text layer** (see §6).
- **Inventory the existing notes as well as the sources.** A source ingested in an earlier session is
already answered, and re-extracting it costs the same as the first time while producing a second page
under a different name — the duplicate is the expensive part. Search the notes for the *source* (author
surname, chapter number, title in both languages, `search_files(pattern='...', path='<vault>/notes')`)
and hand the child the existing page to extend instead of a blank one. When the user asks a question
about a source rather than asking for an ingest, the existing page alone usually answers it — read it
before reaching for the scan.

The inventory is what lets you write accurate task specs, count how many subagents the job needs, and
catch the source the user *thought* they added but didn't. **An empty folder is a finding worth
reporting**, not a silent no-op — it usually means a syllabus or reading list is still missing.

## 2. Extract once, into a scratch dir outside the user's tree

Pre-extract the text of every source **yourself** into one scratch directory, then point every child
at those files. If each child re-parses a 200-page PDF you pay that cost N times and each may get a
different slice.

- Keep scratch output **outside the user's source tree** (e.g. `$LOCALAPPDATA/Temp/<job>/` on
  Windows) so the source folder stays pristine and the dumps don't become clutter to clean up.
- One file per source, page-delimited (`===== PAGE n =====`) so children can cite and you can grep.
- **Build a title map before writing task specs**: dump the first non-empty line of every page or
  slide. That is the document's real structure in ~50 lines, and it is what makes a per-lecture spec
  accurate instead of guessed. It also lets you audit what a child later claims the source said.

## 3. Split by source; assign output paths AND ownership

- **One child per source** (per lecture, per chapter, per paper). Aim for children that each own a
  coherent argument, not for equal page counts.
- **Name every output path exactly.** "Write a concept page about the Kalman filter" yields a
  different filename in every child.
- **Assign artifact ownership explicitly.** Give child A `particle-filter.md` and child B
  `dempster-shafer-evidence-theory.md`; otherwise both write their own version of the shared idea and
  you get duplicates plus dangling links. Where a concept genuinely spans two sources, name the one
  owner and tell everyone else to link to it.
- **Sibling pages that don't exist yet are still cross-linked.** Tell children to link a page another
  child owns even though it isn't written yet — the ingest completes together. Say this out loud or
  they hedge and omit the link.
- **Cap the concept-page count per child** ("up to N; merge or drop rather than pad"). Unbounded,
  children produce thin pages to look fuller.

## 3b. Uniform-contract extraction (machine-consumed JSON, not prose pages)

When each child returns a **fixed-schema fragment you will merge** — graph nodes/edges, index rows,
embedding manifests — the assignment rules change:

- **Measure every source's text size first, then balance chunks by size** instead of one-source-per-
  child. A 25-page paper and a three-paragraph note are not comparable units; the child handed both
  will skim the paper. Count words per file (a `pypdf` loop is enough) and pack to a per-child budget.
- **Precompute every identifier yourself and paste it into the task spec.** If the contract needs
  deterministic ids (`{stem}_{entity}`), normalise the stems in one script and hand each child its
  stem list verbatim. Two children asked to normalise "the same way" will not.
- **Pass the schema verbatim in full, in every task**, including the closed enumerations (allowed
  `file_type` / `relation` / `confidence` values) and the no-prose / JSON-only rule. A child given a
  paraphrased schema emits a fragment the merge silently drops.
- **Give each child an absolute output path you chose.** A child that invents its own filename loses
  its entire chunk, and the loss is invisible until the merge counts come up short.
- **Dispatch every child in a single turn.** Splitting the dispatches across turns serialises the job
  and throws away the parallelism that justified delegating.
- **Merge in a script that reads files off disk**, not one that consumes the children's own reports.

## 3c. Sizing a uniform-contract job before you commit to it

Count the corpus, print the per-source word counts, and decide the chunk count from that — then show
one line of arithmetic. "11 files, 119k words, ~5 children at ~30k words each, roughly 15k tokens per
child" is what lets the user accept the cost or scope it down. A corpus this size is worth flagging as
a one-time build cost with cheap re-runs afterward, because that is the trade the user is actually
approving.

## 3d. Filing the derived artifacts back into a notes vault

When the ingest also produces **tool artifacts** over the vault (a knowledge graph, a search or
embedding index, a build output), keep two locations apart:

- **Working copy outside the vault** — source clone, intermediate chunks, rebuild script. The user's
  drive may be near-full, and if the vault is OneDrive-synced you do not want 500 MB of intermediates
  in the sync set.
- **Finished artifacts inside the vault, in a dot-folder at the root** (`.graphify/`, `.index/`).
  Obsidian ignores any folder starting with `.` — the same mechanism as the vault's own `.obsidian/` —
  so the note tree, search and Graph View stay clean and nothing is mistaken for a curated page.
  Never file them as notes: they are derived and rebuildable.
- **Do not touch the vault's own catalogue for them.** A vault with an `index.md`/`log.md` contract
  governs *wiki pages*; logging a dot-folder artifact is the user's call — ask rather than assume.
- **Put a `README.md` inside** saying what the artifact is, the command that regenerates it, how to
  query it (with the absolute path flag it needs), and its caveats — especially if the artifact's
  internal paths point at the staging copy of the sources rather than the vault's own `raw/`.
- **Make generated HTML work with the network off** (inline any CDN script; see the offline-artifact
  rule in the vault's own skill) and **verify the artifact still opens from its new path** before
  reporting the move done.

## 4. Reserve the shared catalogue files for yourself

Any index, catalogue, changelog, task list, or schema file is shared state. Tell **every** child,
verbatim, not to touch it — children create/edit only the pages named in their task. Then update the
catalogue once, yourself, from the verified file list.

## 5. Repeat the whole style contract in every child's context

Children cannot see each other or your conversation. Restate the full block in every task: house
style, frontmatter schema, naming rule, link format, exact output paths, honesty rules, and the
don't-touch-the-catalogue prohibition. Two things get silently dropped if you don't say them:

- **Figure/asset depth.** "Extract diagrams to `<assets>/<slug>/`, check each with vision before
  captioning, and cite by page/slide number instead if vision fails" — omit this and children skip
  figures entirely.
- **The navigation convention**, if the user's schema requires one (e.g. a per-topic index of related
  pages under each heading). Children won't infer it from a sibling page they never read.

Also point each child at the existing pages it must cross-link, and tell it to say where any
non-obvious claim came from.

## 6. Handle sources that don't yield text

- **Scanned PDFs** (no text layer): confirm with `page.get_text().strip() == ""` plus non-empty
  `get_images(full=True)`, checking page 1 **and** a middle page — a text layer on page 1 can vanish
  later. Then render at 250 dpi and OCR with `rapidocr_onnxruntime` (~100MB, frequently already
  installed): a middle option between "pymupdf can't" and a multi-GB OCR stack. **Start that batch in
  the background before dispatching children** — it takes minutes — and write each output file only
  once, at the end of its source, so a present file is a complete file and the job is restartable.
- **OCR flattens structure.** Have children recover headings, figures and boxed algorithms with
  vision on the rendered page rather than trusting the transcription, require OCR-derived pages to be
  labelled as such, and require unreadable passages to be marked unreadable.
- **A scan sheet may be a TWO-PAGE SPREAD, and spread OCR reads in horizontal bands, so it interleaves
  the facing pages line by line** — every sentence faithful on its own, consecutive ones belonging to
  different pages. A child handed that text will assemble a chapter out of interleaved pages and never
  notice. Tell children explicitly: clip the sheet in half and read each half with vision
  (`page.get_pixmap(dpi=320, clip=pymupdf.Rect(x0, y0, x0+w/2, y1))` and its right-hand mirror), never
  infer order, headings or structure from spread OCR, and cite the **printed folio** rather than the PDF
  page index. Compute the sheet→folio map once, yourself, and paste it into the task spec — the offset
  is constant within a scan, so it costs one pass and every child otherwise re-derives it.
- **Numbers in scanned tables are the part most likely to be wrong**, and a child will not re-check a
  number it transcribed successfully. Require a figure that enters a page to be re-read from a 600 dpi
  crop of its own region whenever the first read was doubtable, and settle it by the arithmetic it has
  to satisfy — see the `verifying-source-claims` skill.
- **Slide decks often carry their equations as embedded images**, so extracted text has gaps exactly
  where the maths is. Tell children to **triangulate against a text-layer companion** — a tutorial
  paper, a textbook treatment of the same lecture, the deck's own cited source in the same folder —
  and to say where an equation came from. Never let a gap be filled from memory.
- **Archives**: `bsdtar -tf <file>.rar` lists contents when nothing else will. Document what the
  assigned reading is; don't extract into the source tree.

## 7. Verify the output yourself — a child's "done" is a claim

Children report success they have not checked. After they return:

- **Count.** Reconcile the page list you asked for against the files that exist on disk (`ls`,
  `find -newermt`, or a script). Missing pages and renames both surface here.
- **Resolve every link.** Run the shipped checker over every page written:

  ```bash
  python scripts/verify_md_links.py "<root>" "notes/**/*.md" --fm title,type,created,updated
  ```

- **Check the specifics you demanded**, not just that files exist: search for the required sections,
  the required cross-links, the required flags/honesty block. A well-formed page that skipped the
  content you specified passes a filename check and fails the user.
- Read at least one child's full output yourself before reporting success.
- **For JSON contracts, validate on disk, never from the report**: the file exists, `json.loads`
  succeeds, the expected top-level keys are present, and the per-chunk counts sum to the merge total.
  A child can report "valid JSON, verified" while a later edit in that same child failed — only the
  file on disk witnesses what happened. Reconcile the merged node/edge count against the sum of the
  chunk counts before any downstream build.
- Then update the catalogue and changelog **once**, from the verified list — never from the children's
  summaries.

## Pitfalls

- **A dangling cross-link is the signature failure of parallel writing**, because each child knows
  only its own slug list. It is invisible until someone clicks it, so verify rather than assume.
- **Inside a markdown table a wikilink's pipe is escaped** (`[[wiki/x/y\|Display]]`), so a naive
  `\[\[([^\]|]+)` scan captures `wiki/x/y\` with a trailing backslash and reports **every** table link
  as dangling. Strip it, and resolve by basename as a second chance — many editors resolve links by
  name, so a path-differing link is a warning, not an error. Never loosen the regex to silence a
  false positive.
- **Don't accept a summary in place of the pages.** If a summary was what you wanted you wouldn't
  have delegated a page list; require the written file paths in the report.
- **Never invent the content of a gap** — a missing equation, an unreadable scan, a lecture with no
  deck. Report the gap; a fabricated equation is worse than a hole, and it will be read back as fact
  months later.
- **Don't let one child own two big sources just because it finished early.** Re-splitting costs
  less than a child that skimmed the second half.
- If a child's report and the filesystem disagree, **the filesystem wins**.
