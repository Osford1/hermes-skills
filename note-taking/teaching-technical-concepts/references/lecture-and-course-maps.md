# Lecture and course maps

The user works through courses as slide decks in the Brain 1 vault (`raw/<course>/Lecture notes/*.pdf`,
plus the syllabus and an `Own notes/` folder). When they ask for a flow chart of "this lecture" and
"the entire course — where we are, where we've been", they want TWO diagrams, and they want them
grounded. A position claim is only worth something if the order and the dates came out of the course's
own material; a guessed schedule is worse than no schedule.

Pair the diagrams with the `diagram-design` skill for style mechanics (dark skin, `<defs>` arrow
markers, node = mask + box + type tag, legend matching the shapes actually used).

## Ground the map first — do not skip to drawing

1. **Get the real schedule.** The intro/绪论 deck usually carries a per-session schedule slide (week,
date, topic, sometimes assessment weights). Extract it, don't infer it: run a short script over the
deck's first pages with `pymupdf` (`page.get_text()`) and read the table verbatim.
2. **Get the current lecture's section boundaries.** Page text of the lecture PDF gives them: print
pages in order and find where the section heading changes. Where a boundary is ambiguous, match the
heading string, not the page number you remember from an earlier session.
3. **Course position = schedule rows vs today.** Rows already delivered are "covered", the row just
finished is "you are here", later rows are "ahead". Put the real dates in the nodes — they are the
most useful thing on the chart.
4. **Merge rows until you have <= 9 nodes.** A node is a stage of the course, not a class session:
group two related sessions into one node (e.g. vision I+II), and group the project proposal and its
defence into one node. Keep a 3-4 character tag per node (syllabus topic number, or deck slide range)
so the chart stays traceable back to the source.

Script discipline: write the extraction script to a temp `.py` and run it with the miniconda python
with `PYTHONIOENCODING=utf-8` set, or CJK page text comes back as mojibake.

## The two diagrams

**Lecture chart** — one vertical spine, one branch, one outcome. Sections in deck order; where the
lecture teaches two equivalent routes to the same result (force view vs energy view, Newton-Euler vs
Lagrange), draw them as a two-box fork that reconverges on the result box. The result box is the only
focal node (accent), and it holds the lecture's one headline equation.

**Course chart** — one vertical timeline, one node per stage, legend of exactly three states:
covered (muted stroke, faint fill), you-are-here (accent stroke + tint), ahead (same stroke, dashed).
Mark the current node additionally with an accent `YOU ARE HERE` line — the legend alone makes the
reader hunt for it.

## Paper structure maps

A research paper is a third source type, read out of `raw/Research Papers/`. Same treatment the user
asks for on a lecture: "how the paper is structured, plus the important concepts for each section".

- **Bands in reading order** — introduction, preliminaries, method, evaluation, conclusion, top to down.
  Give the middle a two-column row (preliminaries left, method right): the method's internal pipeline
  needs vertical room, and one column forces a third screen.
- **The tag chip carries the SOURCE's own numbering** (`I`, `II.A`, `III.B.2`) — the chart's job is to be
  a map back into the paper. Reconcile every tag against the paper's headings before delivering by
  grepping the extracted text for them (`^\s*(I|II|III|IV|V)\.\s+[A-Z]`): a mis-tagged band passes
  every static checker, because those read markup and not meaning. Content that is the second half of a
  subsection belongs to that subsection — do not promote it to the next free number.
- **2–4 concept sublabels per band ARE the deliverable**, not decoration: the entities, symbols,
  hyperparameters and numbers a reader has to carry forward. A band showing only its title has failed the
  ask, however clean it looks.
- **Every number on the canvas comes out of the extracted text, never from recall.** Extract once to a
  temp file (`fitz.open(path).get_text()`), then grep each value individually. Grep with `-a`: extracted
  PDF text is sniffed as binary, and plain `grep` answers `Binary file … matches` instead of counts.
- **Hold the paper's strength of claim.** If it leans on an anytime property rather than proving
  convergence, the node says *anytime*; quote its complexity expression as written instead of glossing
  it into a friendlier "near-linear in K".
- Close with 2–3 summary cards under the canvas — the one-line argument, the pivot versus the prior art,
  the concepts worth studying. Card lists, never prose.

"Similar to the <x> chart in session <y>" is a format spec, not a hint: find that artifact in the
vault, read it end to end, mirror its tokens and CSS, and file the new chart as its sibling
(`raw/Own Notes/<slug>/<name>-structure-flowchart.html` for papers). Strip any `<link rel="preconnect">`
lines out of the copy — the checker reads them as unapproved remote references, while the single
approved font stylesheet link passes.

## Verify the rendered pixels before delivering

0. **Sweep the DOM geometry numerically first**, in JS, before spending a look at pixels: text outside
its box, text overflow past an 8px margin, text-on-text, a mask rect over a node, a connector crossing
box (exclude each path's first and last ~10px, or every legal attach point reports as a violation),
mask-to-connector clearance ≥6px, and the rendered scale. It is cheaper and stricter than reading a
screenshot, and it catches overlaps a downscaled image hides. Rule set:
`visual-artifact-verification`, `references/svg-geometry-sweeps.md`.
1. Load the file over `file://` in the browser session and capture full page:
`cdp('Page.captureScreenshot', captureBeyondViewport=True, format='png', fromSurface=True)` — a
viewport-only shot silently truncates a tall diagram and you will "verify" the top third.
2. Audit the PNG with `vision_analyze`: overflowing text, labels colliding with boxes, clipped
glyphs, arrows not meeting or badly floating off box edges, legend items missing for a shape in use.
3. **Send one `vision_analyze` per turn.** Firing it in the same block as another tool call (or two of
them at once) times out; when a lone call does time out, retry it once — that is a transient, not a
reason to change the diagram or fall back to hand-checking the SVG.
4. Geometry fixes to make after the first audit: connector endpoints stop 8px clear of the box edge
(6px reads as "arrow broken" to an auditor); every text label over a line needs an opaque mask rect
sized to the text plus clearance, or the line runs through the glyphs; on a dark page the mask fill is
the page colour, and translucent node fills need their own mask or arrows show through.
5. Re-shoot after every geometry fix. The delivered file must be the verified one.

Text sizing that survives the audit: node name 12px sans, sublabel 9px mono (equations and dates live
here — mono reads as technical, sans reads as label), type tag 7px mono, legend 8px mono, canvas
~720 units wide with text kept inside the right half of each box.

## Delivery

Save under the course folder (`raw/<course>/Diagrams/<slug>.html`), self-contained, no build step. Show
it inline with `::preview{file="<abs path>"}` on its own line and give the paths as plain text — the
user wants to look at the chart immediately and keep the file in the vault.

## Pitfalls

- The PDF text layer drops subscripts and vector components, so an equation lifted from it can be
wrong. Render the slide image at ~2.4x and read that when an equation matters.
- Some CJK filenames surface as GBK mojibake in bash output (`...½ÌÑ§´ó¸Ù.doc`). `read_file` accepts
that exact string — copy it verbatim from the directory listing instead of re-encoding the name.
The same document can exist under both the mojibake and the clean name; read both before concluding
which is the real one.
- Surface deadlines the deck states (homework due dates, exam/proposal dates) in a small summary
card next to the chart. They are on the final slides and are the part the user acts on.
