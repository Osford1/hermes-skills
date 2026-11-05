---
name: annotated-figures
description: "Use when photos need annotating for a deck or report."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [figures, images, annotation, pil, slides, bilingual]
    category: productivity
---

# Annotated figures (labelled photos) for deliverables

When the user sends photographs and asks to "annotate these" / "add them to
the slides", the deliverable is not the raw photo: it is a labelled figure
that drops into an exact slot of the document or deck, in every language that
document exists in. Pillow draws the callouts; python-pptx (or the docx
builder) embeds them.

## When to Use

- The user attaches photos and asks for them annotated, captioned, or added
  to an existing deck/report.
- A generated deliverable needs labelled evidence figures (hardware photos,
  sites, specimens, screenshots) rather than decorative stock images.
- The same figure must appear in more than one language version.

## Workflow

1. **Fix the slot before drawing anything.** Decide the on-slide size (e.g.
   three photos across a 12.35 in body with 0.25 in gaps = 3.95 x 3.10 in
   each) and make the canvas exactly that aspect. Never let PowerPoint rescale
   the figure.
2. **Read the source photos first** with `vision_analyze`, and in the same
   pass ask for feature positions **as percentages of the image** ("give x%,
   y% from top-left for the pegs holding wires, a connector at a branch end,
   the red placard"). You need numbers, not prose.
3. **Annotate with `scripts/annotate_figs.py`** (edit its `CONFIG`, run it) or
   the same recipe by hand: number badge, 2-3 leader-labelled boxes, bottom
   caption band, one output file per language.
4. **Verify the figure** with `vision_analyze`: ask what each leader dot
   actually sits on, whether any box or dot is clipped or swallowed by the
   caption band, and whether the CJK glyphs are real. Numeric sanity checks do
   not see a dot that landed next to its subject.
5. **Verify in the rendered deliverable**, not just in the figure: render the
   slide/page and confirm the caption, highlight bar and summary bar all still
   fit. The bottom third is contested space.

## Canvas arithmetic (do this, do not eyeball it)

- `CH = round(CW / (slot_w / slot_h))`. 1560 x 1224 px = 3.95 x 3.10 in at
  ~395 dpi, so a 46 px label is ~8.4 pt on the slide - the practical floor for
  projector legibility. Text drawn at "looks big enough" (20-30 px) disappears
  once the figure is scaled into a 4-inch slot.
- Font px = `pt / 72 * (CW / slot_w_in)`. Badge and band text can go one step
  larger than labels; the band is read from the back of the room.
- Insert with BOTH width and height set to the slot so nothing re-scales, and
  ignore dpi - the canvas is a fixed pixel grid.
- Draw the callouts in canvas pixel space *after* the photo is resized, so the
  text is crisp even when the photo itself is soft.

## Fitting a photo whose aspect is not the slot's

- Crop toward the slot aspect instead of letterboxing, but cap it and bias it:
  `crop=(max_frac, bias)`, `bias +1` keeps the right/bottom edge, `-1` keeps
  the left/top. Bias is how a subject at the frame edge (the near board, the
  connector at the bottom) survives the crop.
- Fill the remaining margin with the deck's/panel tint so the photo reads as
  matted rather than accidentally short.
- Map every coordinate through the crop box:
  `canvas = off + (frac * orig_dim - box_left) * scale`. Hard-coded feature
  pixels break the moment the crop is tuned; source percentages do not.
- Crop and subject are a two-way constraint: if the subject sits at 88% height,
  no bottom-side crop and no thick caption band is available. Pick the
  constraint you can actually satisfy.

## Anatomy of one annotated photo

- Number badge top-left, **plain digits** (1/2/3) - circled glyphs are
  font-dependent and can render as tofu.
- 2-3 white label boxes (~92% alpha, 3-4 px accent border, rounded) joined by
  a short leader line to a filled dot on the feature. Labels are 2-4 words;
  the sentence belongs in the slide caption under the picture.
- Choose the side (left/right) per label so boxes do not collide, then clamp
  them inside the canvas with a small margin.
- Translucent caption band across the bottom (~6% of canvas height): ordinal
  plus one short line. A 100 px band swallows a dot placed at 88% height.
- One file per language (`fig-<name>-<lang>.jpg`), each with its own label
  table. A CJK label set needs a CJK font
  (`C:/Windows/Fonts/msyhbd.ttc`, matching the deck's 微软雅黑) or PIL draws
  boxes.

## Multi-language figures are one build, not two

- Keep the label table keyed by language in the annotation script, and write
  per-language output files. The deck overlay then points each language at its
  own figure - no runtime font switching, no half-translated figure.
- Translate *labels and captions* together. An English label set under a
  Chinese caption is the classic half-localized figure.

## Wiring figures into a generator-built deliverable

- The annotation step stays a **separate script** reading
  `Reference/figures/<name>-source.png` and writing the per-language
  `fig-<name>-<lang>.jpg`. Re-run it only when a better source arrives; the
  document build never re-annotates.
- The slide spec carries `figs: [{path, cap}, ...]`; the builder inserts each
  picture at slot size and adds a caption box under it. A language overlay
  replaces the whole `figs` list (paths + captions), so layout keys stay in one
  language and the list-length assert still holds.
- **Add a slide by appending to the content list and adding its index to
  `ORDER`** - never by inserting mid-list, which renumbers every index in
  `ORDER` and in the overlay. Mirror the new entry (same key names, same list
  lengths) in the overlay in the same edit, or the equal-length assert fails
  the next build.
- Budget the bottom third before choosing the slot height: caption box +
  highlight/takeaway bar + summary bar compete for the same space. A 3.10 in
  photo + 0.78 in caption + 0.72 in bar clears a 6.62 in summary bar on a
  7.5 in slide with ~0.2 in to spare.
- **Every text bar needs its own separator.** A bold label run followed by a
  plain run renders as `Summary - text` only because the label string itself
  ends in a dash. Give each new bar (`Why this matters`, its Chinese
  counterpart) its own trailing dash, or the label reads as glued to the first
  word.

## Pitfalls

- **User-supplied photos are routinely chat-sized thumbnails** (~350 px wide).
  Check the size, and say the effective dpi out loud (~90 dpi across a 4-inch
  slot - soft from the back of a room) instead of presenting an upscale as
  print quality. A light `UnsharpMask` helps; it does not create detail. Make
  the swap cheap: named `*-source.png` inputs plus a re-runnable annotator.
- Do not judge the finished figure from the source pixels: the callouts are
  the point, so verify what each dot sits on, not just that the labels render.
- A photo's aspect decides which features can survive cropping - check the
  feature percentages against the crop window before writing labels.
- Annotation text drawn before the resize gets resampled into mush; draw last.

## Files

- `scripts/annotate_figs.py` - the annotator: canvas math, biased crop,
  leader-line label boxes, caption band, one file per language. Edit `CONFIG`,
  run it, then verify the output with `vision_analyze` before embedding.
