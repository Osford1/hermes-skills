---
name: research-gap-ledger
description: "Use when a paper needs adding to the thesis gap ledger."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [research, thesis, gaps, papers, ledger]
    related_skills: [okr-smart-project-roadmap, first-principles-thinking, arxiv, grounded-citations]
---

# Thesis gap ledger — adding papers, summarising gaps

Single source of truth:
`C:\Users\<you>\OneDrive\Documents\<archive>\Projects\thesis-direction\Working\gap-ledger.md`

The user is hunting a thesis direction while under my supervisor (precision
motion control, learning-based feedforward). The ledger turns reading into a
comparable set of gap candidates so a direction can be chosen instead of
drifted into. Read the file before editing it — the Queue and Ledger sections
carry state.

## Division of labour (do not blur this)
- **User:** reads the paper, judges whether a gap is worth attacking.
- **Hermes:** fetches, extracts, records, matches, counts, clusters, summarises.

A gap the user did not form is not theirs. They already stalled once on "this
topic doesn't feel mine" — handing them ready-made gaps recreates that exactly.
Drafting a gap sentence is fine; leaving it `DRAFT` until they accept or rewrite
it is required.

## Adding a paper
1. Get the paper: user pastes a title / arXiv ID / PDF, or drops it in chat.
   Fetch abstract + PDF; paywalled PDFs go to the vault `raw/` per
   `brain1-wiki-agent`.
2. Extract two things, with section/page:
   - the **limitations / future-work paragraph**, quoted
   - the **tested conditions** — one robot? one trajectory family? one speed?
     sim only? what baselines were skipped?
3. Draft the gap as a claim: `X works for [A]; untested for [B]`. Tag `DRAFT`.
4. Append the row to the Ledger table + a detail block (evidence, prior-work
   check, fits-my-setup, question for the group).
5. Say plainly whether it matches a gap already in the file, or is new.
6. Move the paper out of the Queue.

## Summarising ("what are the gaps?")
Produce, in this order: **clusters** (gaps that repeat across papers — three
papers is an area, one paper is a paper) → **shortlist** scored against the
5-point filter in the file (still open / reachable with their setup / supervisor
can guide it / fits the thesis clock / someone outside academia would care) with
the failing item named → **what changed** since last summary → **the thinnest
area**.

## Pitfalls
- **Never write a gap for a paper the user hasn't read.** Queue, not Ledger.
- **`unchecked` is not `open`.** A gap only counts as open after a prior-work
  search; record who checked and when. "I didn't know the existing solution" is
  a knowledge gap, not a discovery.
- **Count in code, not by eye.** When reporting how many papers/gaps are in the
  file, parse the file and count — declared totals are assertions.
- **Don't let the ledger become a reading log.** A row with no gap sentence is
  an unread paper wearing a row.
- **Supervisor directions get their own thread** in the file (e.g. "look into
  end effectors") so they don't get lost or silently become the whole thesis.
  **The user's own direction ideas get the same thread treatment** (e.g. "robots that
  plug wires so machine builders assemble faster") — label which is which, and scope a
  user-originated thread to the supervisor's method families before queueing papers, or
  it reads as a business plan instead of a thesis.
- **A source map is not a queue.** When the user asks "find me papers on X", collect the
  whole field into `Reference/<topic>-sources.md` (grouped by sub-problem, with free/paywalled
  marked) and queue only 2–3 rows in the ledger. A 20-row queue recreates the end-effector
  stall; a map satisfies the request without becoming homework. Download exactly the one
  paper you ranked first, verify the PDF, and stop.
- The ledger lives in OneDrive, not the Obsidian vault: it is a work artifact
  with statuses, not a concept note. Link to it from the vault if useful.
