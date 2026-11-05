---
name: paper-structure-maps
description: "Use when a paper becomes a zoomable structure map."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [papers, diagrams, study, html, verification]
    category: note-taking
    related_skills: [diagram-design, verifying-source-claims, visual-artifact-verification]
---

# Paper structure maps

Turning a research paper into an HTML structure map the user reads *in layers*: a master chart of how
the paper is built, then per-concept charts they zoom into, then a zoom back out to see how each
concept sits in the whole. The deliverable is a study artifact, not a copy of the paper's figures — it
answers "how is this paper put together, and which parts do I actually have to understand?".

The user's loop, stated as the requirement every time: **read the master chart → zoom into one concept →
get a focused sub-chart for it → zoom back out and see where it fits.** The master chart is the index;
its job is to make the sub-charts attachable.

## Procedure

1. **Extract the paper's text once to a plain-text working copy** and keep it for the whole session.
   Page through that copy for section boundaries; do not re-render the PDF per claim.
2. **Map the top-level sections before drawing anything**, sub-sections included, and note which
   section is the method's load-bearing one. The chart needs the paper's real shape, not its abstract.
3. **If the user supplies their own outline, that outline wins the ordering** — validate it against the
   paper first, then rebuild the chart to their order. Report per-claim verdicts, the omissions, and
   any error of your own the pass turned up (see `verifying-source-claims`).
4. **Build the master chart**, one node per section or argument beat, ≤9 nodes. Load `diagram-design`
   for the visual language, then read the precedent chart for this document family and inherit its CSS
   before touching the body. That skill is user-owned — read it, never edit it.
5. **Add the zoom anchors** (see below) at the same time as the nodes, not afterwards.
6. **Verify in two passes**: the skill's static self-check, then a measured audit of the rendered SVG.
7. **Re-measure after every edit**, then report. Sub-charts get built on request, one anchor at a time.

## Zoom anchors

- **One stable anchor id per concept (`Z1`, `Z2`, …), rendered as a small chip on its node** — top-right,
  soft stroke, same weight as any section-tag chip. The chip is the handle: it survives re-layout, it
  names the sub-chart, and it is the link back to the master.
- **Never renumber anchors when editing the master — append `Z8`, never renumber `Z1..Z7`.** Sub-charts
  already built reference their anchor by id, so a renumber silently invalidates all of them.
- **Make the chip do something:** `data-hermes-send="Build the Z3 sub-chart: <concept>, <what it must
  cover>"`, so clicking it in the Hermes preview pane returns that concept as a prompt.
- **Fix the return convention before the second chart exists.** The sub-chart repeats its own chip and
  names the master node it re-enters ("re-enters node 4, §III.A"); without that the zoom-out direction
  is guesswork.
- **Explain the convention on the chart**: one legend entry (`ZOOM ANCHOR`) and one card stating the
  loop. Unexplained chips read as decoration and the reader never finds the workflow.

## Nodes, tags, and what to highlight

- **Merge two outline entries that make the same argument at two depths.** A paper's abstract-level
  argument and its Introduction are one beat; spending two of nine nodes on it costs a section that
  genuinely needs one. Say that you merged them.
- **Tag every node with the paper's own numbering, at the sub-level the content actually is** —
  `III.B.2`, not `III.B`, and never a `III.C` that does not exist. A wrong tag sends the reader to the
  wrong page, which is worse than no tag. Widen the tag chip rather than shrinking its text.
- **Highlight the concepts the reader cannot re-derive**, not the section titles: which factors the
  method is built from and in what role, which levels the parallelism is exploited at, which baseline
  belongs to which family, what the paper's stated limitation is.
- **Keep the paper's own honesty markers on the chart.** A method with no convergence proof, an
  anytime variant, a baseline limited to offline planning — those are findings the user wants, not
  footnotes.

## Numbers on the canvas

- **Every value that reaches the canvas is grepped out of the extracted text first.** Numbers recalled
  from having read the paper are the standard failure here, and a chart makes them look measured.
  Load `verifying-source-claims` and follow it.
- **Attach each value to the symbol the paper gave it** — a horizon bound and an iteration cap print as
  two naked integers, and the digit alone cannot tell you which is which.

## Verify the render, not the markup

The static check does not tell you the chart renders correctly. Measure the rendered SVG in a browser
too, on these checks:

- every text inside its node rect with ≥6 px margin on all four sides; report the tightest margin;
- element rects not overlapping each other;
- connector strokes starting and ending on a box edge;
- no connector passing through a box interior;
- pairwise connector crossings, counted;
- ≥6 px between any connector-label mask rect and any connector stroke.

Pitfalls that make this audit lie:

- **Exclude the canvas background rect before collecting node rects.** A size filter such as
  `width >= 300` matches the full-canvas background rectangle, and then every text and every connector
  reports a violation *against it* — dozens of false positives that read exactly like a badly broken
  chart. Exclude the max-area rect before measuring, and sanity-check the element counts against the
  markup you wrote.
- **Re-measure after every text edit.** Label lengths change margins; a clean audit from before a
  wording fix says nothing about the file afterwards.
- **A vision read of the rendered PNG is the weaker check.** It catches clipping and layout collapse,
  but it misattributes long elbow connectors to the nearest label and cannot resolve small chips. Take
  structural truth from the measured audit; use vision only to confirm nothing looks broken.
- **Run the shipped gate, and never copy the precedent's `<head>` or `<svg>` opening tag.** Installed
  precedent charts predate `diagram-design/scripts/self_check.py` and fail it: their two
  `<link rel="preconnect">` tags are rejected remote references (only the `/css2` stylesheet URL is
  allowed), and their `<svg>` lacks `<title>`/`<desc>`, is not title-first, has bare ids and uses
  `aria-label` instead of `aria-labelledby`. Inherit their CSS and geometry grammar only; write a
  fresh accessible opening. The gate needs a native path (`C:/...`) — MSYS `/c/...` paths make it
  report a bogus "No such file or directory".
- **Read long HTML deliverables in ≤70-line chunks** when preparing an edit, so the change is made
  against the actual bytes rather than against your impression of the file.

## Filing

One folder per source document, following the precedent already in the vault:
`<vault>/raw/Own Notes/<topic-slug>/<doc>-structure-flowchart.html`. Read the precedent chart for the
family first — the CSS and design system are inherited and must survive a restructure.
