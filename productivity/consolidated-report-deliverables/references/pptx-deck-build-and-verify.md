# Building and verifying a pptx deck

## When this applies

The user wants the compile as slides — they will present it, forward it, or hand it to someone who
reads it cold. The bundled `powerpoint` skill covers python-pptx mechanics and its spec-driven
`pptx_create.py` (leave that skill alone — it is bundled and not ours to edit); this file is the
house shape and the verification route the spec path does not cover.

## Build: a script, not a spec file

- Run the build with the **miniconda python** (`C:/Users/<you>/miniconda3/python.exe`): python-pptx
  lives there, not in the Hermes venv python.
- Keep `deck/build-deck.py` beside the deck. All wording sits in a `CONTENT` block at the top
  (titles, bullets, table rows, notes) and geometry lives in helpers — `heading()`, `box()`,
  `panel()`, `table()`, `hbar()`, `chevron()`, `footer()`. A changed figure is a rerun, never a
  hand-edit inside a slide.
- 16:9: `prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)`.
- Dark house theme: near-black slide background, one step lighter for panels, a single accent for
  rules and headers, semantic green/red reserved for P/L, amber for caution; body text ≥14pt,
  decoration quiet. Define the palette as constants at the top so a retheme is one edit.
- Tables: python-pptx exposes no table-style API — set `fill.fore_color.rgb`, cell margins and the
  run font/size/colour on **every** cell, or the default banded blue style shows through and fights
  the theme.
- Why not the spec route: `pptx_create.py` styles bullets but not table cells, and a blank layout
  leaves `slide.shapes.title` as `None`, so the outline pane ends up with no titles.

## Titles must be real placeholders

- Build slides from the `title_only` layout (`prs.slide_layouts[5]` in the default template; 0 =
  title, 1 = title + content, 6 = blank) and write the heading into `slide.shapes.title`.
- Set font, size, bold and colour on the title run explicitly — the placeholder inherits theme
  styling that will fight a dark deck.
- A heading drawn as a plain textbox looks identical on the slide but is **invisible** to the outline
  pane, Presenter view and screen readers.
- Reading back: `pptx_read.py out.pptx --outline` reports placeholder text inside each slide's
  `texts` array. If the outline appears to show no titles, check `slide.shapes.title.text` directly
  before "fixing" anything — an absent key in the outline output is not absent text in the file.

## Render and review — the step that catches real defects

LibreOffice is not installed here, so `pptx_render.py` returns `{"rendered": false}`. PowerPoint
itself is the renderer (Office is present on this box):

```python
import os, win32com.client
app = win32com.client.Dispatch("PowerPoint.Application")
pres = app.Presentations.Open(os.path.abspath(pptx), WithWindow=False)
pres.SaveAs(os.path.abspath(pdf), 32)      # 32 = ppSaveAsPDF
pres.Close(); app.Quit()
```

`scripts/pptx_to_pdf_win.py` wraps exactly this (plus the PNG step). Then rasterise:

```bash
pdftoppm -png -r 110 deck.pdf slide     # → slide-01.png … slide-NN.png
```

poppler ships with MiKTeX on this box, at
`/c/Users/<you>/AppData/Local/Programs/MiKTeX/miktex/bin/x64/pdftoppm` (may not be on bash's PATH).

- Review **every** slide with `vision_analyze`, one targeted question per slide type, ending with
  **"Report exact problems only"** — without that clause the model describes the slide back to you;
  with it you get clipped text, overlap, off-slide content and footer collisions. Name the specific
  risk in the question ("does the table still clear the callout panel below it").
- **After any geometry fix: rebuild → re-render → re-review the affected slides.** A change to one
  shape may move nothing else — only pixels prove that.
- Finish with the structural pass: `pptx_read.py out.pptx --outline` for slide count, titles and
  notes. Vision catches layout; the outline catches a slide whose notes never landed.

## Layout traps that cost real time

- **Summed row heights beat the table frame's height.** If the row heights add up to more than the
  space budgeted, the table grows downward and silently covers whatever sits below it (a callout
  panel, in the case that taught this). Add the heights up before rendering; trim them to the next
  shape's top edge.
- **Never add an empty shape as spacing.** A zero-height callout renders as a visible sliver —
  position the next element instead.
- **Deck wording lives in Python literals.** Text containing `"` needs `\"` (or a single-quoted
  outer literal); a missing escape is a SyntaxError that only appears when the script runs.
- Build the deck **after** the written rundown exists: the deck is a projection of it, and building
  from the same markdown is what keeps both sets of numbers identical.

## A named institutional template: get the real file, then clone its slides

- The template lives on the institution's own site — university comms / 院系 download pages are plain
  HTML, so `curl` + `web_extract` reach them. Aggregator or reseller copies are the wrong file.
- Annual template sets ship several themes. Download the whole set, inspect each with
  `pptx_read.py tpl.pptx --outline`, render them, and pick the variant whose skeleton matches the
  deck you are building.
- Copy the chosen template into the project's `Reference/` and build from that copy: downloads land
  in a temp dir that gets cleared, and the deck has to stay rebuildable months later.
- Lift the template's fonts and palette from its own run properties (`Counter` over `run.font.name`
  and `run.font.color.rgb`) and use those exact values — a hand-picked "close" brand colour reads as
  off-brand to the person who sees these decks daily.
- A template full of sample slides is a parts bin, not a layout list: duplicate the sample slide
  whose skeleton is closest to the content (`pptx_edit.py --duplicate-slide N`), strip the body
  shapes you do not want (`sp._element.getparent().remove(sp._element)`), keep the title
  placeholder, the rule and the logo, then place content as your own textboxes/tables at your own
  coordinates. Building on a blank layout loses the per-slide decoration that makes it read as
  official.
- Working skeleton: the template's title slide (filled in) → one cloned slide per section → the
  template's own closing / thank-you slide.

## Density: what "too simplified" usually means

- Content stopping at roughly 60 % of the page height reads as thin whatever it says. Two layouts
  fill a slide: a full-width table, or two balanced bullet columns plus a chip/strip band sitting on
  the footer line.
- Auto-distribute table row heights: measure the table's top and bottom, subtract the header, and
  give each data row an equal share of the remainder (weight by expected line count when rows differ
  a lot). Hard-coded heights drift on a machine with different font metrics.
- Normalise column widths: a cloned table can be wider than the usable body. Rescale `col.width`
  proportionally so the total lands just under the body width, or the right edge runs off the slide.
- Keep a ~0.3 in gutter at the body edge. python-pptx cannot measure rendered text, so PowerPoint
  wraps to more lines than a character-count estimate — sizing to the exact body width overflows
  elsewhere.
- Highlight the rows that matter with a noticeably deeper fill **and** bold text: an
  alternating-row tint of the same hue is indistinguishable from a highlight, and colour alone does
  not survive a projector.
- Put any bottom strip or chip band on the same y as the footer bar on the other slides — one
  optical baseline for the whole deck.

## python-pptx traps that bite mid-build

- XML-level handles are `shape._element`, `run._r`, `paragraph._p`. There is no `run._element`; a
  wrong attribute name is an AttributeError part-way through a build, after the file is half-written.
- Iterate `para.runs[1:]` when restyling a cloned title — a template title may carry zero or one
  run, so indexing a run unconditionally crashes the first run of the script.
- Table text does not inherit the placeholder font: write into `cell.text_frame.paragraphs[0]` and
  set the run font/size/colour explicitly; cell shading is `cell.fill.solid()` +
  `cell.fill.fore_color.rgb`.

## Advisor / supervisor-facing pitch decks

When the deck exists to get a verdict on a research direction rather than to present finished
results:

- One line stating the research direction, then Problem → prior art → Proposal → narrowing options,
  with the sections labelled.
- Give prior art real context: what each sub-field actually measures and over what horizon. The gap
  is the argument; a list of names is not.
- Say what the proposal *gives*, and demote methods to a "potential methods" table so the pitch does
  not over-promise what is not done yet.
- Delete the ask / question / next-steps slides when the user says he will raise the questions
  verbally — leftover ask slides read as a template rather than a proposal.
- Keep the weakest point visible (a "what we are not claiming" strip, an open-question row). The
  honest risk is what the verdict turns on.

## Ship

Deliver `.pptx` and the exported `.pdf` as `MEDIA:` paths in chat, plus a contact sheet PNG of all
slides (Pillow paste into a grid) so the whole deck can be judged in one look; keep the generator
and render helper in `deck/` beside them so the next update is a rerun, not a rebuild.

Move a rejected version to `Deliverables/_superseded/` rather than deleting it — the user compares
the two. In the delivery message name what changed structurally, what was verified on pixels, which
placeholders are still theirs to fill (a name / date field), any normalisation you made to their own
wording so it can be reverted in one edit, and where the wording knobs live (the `CONTENT` block).
