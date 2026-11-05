---
name: glassy-panel-design
description: Use when building a glassmorphic panel or translucent UI.
version: 1.0.0
author: Nous Research
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, ui, glassmorphism, accessibility, contrast, palette, typography]
    category: design
    related_skills: [apple-design, file-organization, r3f]
---

# Glassy panel design

For requests like "make this UI feel like glass", "translucent sidebar", "warm/cool
theme", or "redo the interface so it is easier to read". The full spec with measured
tables lives at:

`C:\Users\<you>\OneDrive\Documents\<archive>\_Knowledge\glassy-panel-design-metrics.md`

with a standalone validator `theme-contrast-check.mjs` and two reference palettes
(`sunstone-theme.json` warm, `glacier-theme.json` cool) in the same folder. Read it
before designing; this skill is the working summary.

## The three rules that decide whether it looks like glass

1. **Put a gradient behind the blur.** A blur over a flat fill is a flat fill — the
   first attempt at this was judged "transparency implied rather than demonstrated".
   Build a bloom (3 radial gradients from the accent colour) anchored to the shell,
   not to the scroll container.
2. **Surface alpha is a dial with a threshold, not a taste.** On a dark canvas, 46 %
   paper measures ~1.6 luminance steps of variation across a card — real but
   invisible; **36 %** reads and still holds ~14:1 for text. On a *light* canvas the
   opposite: **88 %**, or the bloom looks like a stain on the white.
3. **Separate surfaces with a hairline and depth, not with value.** Paper sits only
   4–8 L\* above the canvas, so the border (`1px color-mix(paper 50%, line)`) and the
   two-part shadow do the work.

## Recipe

- Palette: one hue family, roles on a **CIE L\* ladder** (canvas, paper +4–8 L\*,
  ink, muted ~L\* 37 light / 71 dark, line ~L\* 50, accent L\* 40 light / 73 dark at
  high saturation, shell just past the canvas).
- Contrast contract: text **≥4.5:1**, boundaries **≥3:1**, all 16 pairs, both
  appearances. Validate with the script — never eyeball.
- Material table: cards 36 % paper + `blur(24px) saturate(150%)`, radius 18 px;
  chips 45 % + `blur(12px)`, radius 14; input 44 % + `blur(20px)`, radius 20; bars
  (header/dock) 72 % + `blur(22px)`, no border; overlays 76 % + `blur(24px)`.
- Type: body 14 px / 1.6 / tracking 0; headings 21…14 px / 1.18 / −0.01em; a hard
  11 px floor for labels with +0.07em tracking; size-specific tracking is not
  optional (large text tightens, small text loosens).
- Answer every preference: `prefers-reduced-transparency` → solid paper,
  `prefers-contrast: more` → solid + drop bloom, `prefers-reduced-motion` → no
  transitions.

## Refractive glass (Apple "Liquid Glass")

A different material from the blur/saturate glass above. This one *bends* what is behind
it at the edges (SVG `feDisplacementMap` against a backdrop snapshot, or a shader), adds
chromatic aberration, and follows the pointer elastically.

- Ready-made in React: `liquid-glass-react` (`npm i liquid-glass-react`) — knobs are
  `displacementScale`, `blurAmount`, `saturation`, `aberrationIntensity`, `elasticity`,
  `cornerRadius`, `padding`, plus `mouseContainer` to track the pointer over a parent.
- **Decorative chrome only.** Displacement glass breaks the contrast contract: what sits
  under the text is no longer a known colour, so `≥4.5:1` cannot be proven. Put it on a
  dock, a hero, a card rim — never under body copy.
- **Assume it degrades.** Safari and Firefox do not render the displacement (plain blur
  only), so design the *fallback* as the real design. If it only works in Chrome, it is a
  Chrome demo, not a UI.
- **Cost:** an SVG filter re-renders the backdrop per frame. One or two per view, never
  full-viewport, and drop it under `prefers-reduced-transparency` / `prefers-reduced-motion`.
- Verify on pixels, not on CSS: sample inside the panel and confirm the backdrop is
  visibly *displaced*, not merely blurred.

## Glass over a moving background (measured on a live page)

One colour, one moving background, two states (clouds → fog) — the failure modes
are predictable once you have hit them:

- **An evenly lit background makes every card opaque.** Measure the in-card ramp:
  screenshot with the text hidden (`color: transparent`), then sample a column
  inside a card top-to-bottom. Measured: an evenly-lit fog state gave **0.9–1.5 L\***
  per card — the spec's "real but invisible" — while the same card over a sloped
  background gave **2.5–3.6 L\***. Aim ≥2.5. The fix is always the same: give the
  background a slope across the card's own height. At 36 % surface alpha and a
  1440×900 viewport, budget **~8 L\* of total background change** top to bottom to
  produce ~2.5 L\* inside a 430 px card.
- **Every background state needs its own contrast pass.** Strong text contrast in
  state A says nothing about state B. Re-measure the same text rects per state.
- **A drifting background can slide its brightest band behind text.** Find the
  brightest pixel and ask which text sits near it. If none does, that is a
  documented *constraint for the next change*, not a pass — and holding the
  contrast rule even there may cost the gradient (a fog's top stop cut from 0.16
  to 0.11 alpha drops the in-card ramp from 2.9 to ~2.2 L\*). Say which side of
  that trade the page took.
- **Stronger bloom lowers text contrast — measure both ends.** At one state the
  ramp was 3.2–7.8 L\* but secondary text fell to **4.84:1**; the shipped settings
  gave 2.5–3.6 L\* with secondary text never below **5.06:1**. Both sides want
  margin, because a moving background cannot be reasoned about, only re-measured.

## Showing clouds, haze or fog behind glass

What the second attempt at a two-state background taught, after "the clouds look like
balls" was the feedback:

- **Never build cloud from radial gradients.** A radial gradient is a disc: it has a
  centre, and a centre is a shape. Two on-canvas radials read as literal balls however
  much blur you put on them. Use a *ramp* (a linear gradient has no centre, so it can
  only read as light) plus a band mask, and get the cloud texture from **procedural
  noise painted once into a small canvas at load**.
- **Normalise a procedural field before you threshold it.** A sum of smooth octaves
  clusters hard around its own mean — cutting it at 0.56 "raw" left 0.5 % of the layer
  above the line, i.e. an invisible cloud bank, and the peak alpha came out at 0.18 of
  the 0.8 asked for. Measure the field's min/max in pass one, stretch it across 0..1,
  *then* apply the knee.
- **Define the noise in fractions of the canvas, then use a small canvas.** Feature
  size on screen is unchanged by canvas resolution, so 256×160 costs 11.4 ms where
  512×320 cost 103 ms — a visible stall — and looks identical under the layer's blur.
- **Give the card band a flat sky.** A horizon glow rising through the band cancels the
  fog's own fall and the ramps collapse (measured: 3.1–3.7 L* → 1.3–2.0 L*). Keep the
  sky's slope out of 25–75 % of the viewport; put the horizon in the bottom quarter.
- **Attribute per layer before tuning.** Hide one background layer at a time and re-read
  the same columns. This is how the last ramp bug was found: the fog's own fall was
  right (12.7 L* at the top, 4.7 in the middle) and a single radial floor-light reaching
  1.5 L* up into the cards was cancelling it.
- **A two-state background must change state.** Cross-fading a bright layer over another
  is a tint, not a state: fade the departing layer (to ~0.3) and let the arriving one
  carry the gradient. Re-measure the ramps and every text pair afterwards — they moved
  in opposite directions here (ramps held at 2.83–3.67 L*, card text improved
  5.71→6.45:1).
- **Pick a metric that can see the thing you are judging.** A 180 px-ring prominence
  cannot see a 600 px-wide glow, so "zero bumps" scored a smooth wash the same as a
  disc. Say what the metric cannot see instead of letting it stand in for the eye.

## Motion and layout traps this work found

- **An element coming back from `display: none` cannot transition in that frame.**
  Set the hidden state, force a reflow (`void el.offsetHeight`), then apply the
  visible state on the *next* animation frame (double `requestAnimationFrame` for
  staggered children). Without this, `opacity: 0 → 1` simply appears.
- **Anything that makes the document taller than the viewport mid-transition makes
  a scrollbar appear and jolts the whole page sideways (~15 px).** Reserve it:
  `html { scrollbar-gutter: stable }`. Verify by reading a fixed element's width
  at rest, mid-transition and after — it must not change.
- **Keep timing in CSS custom properties and read them back in JS**
  (`getComputedStyle(root).getPropertyValue('--dur-scene')`). One source of truth
  stops a JS timer drifting from the CSS animation it belongs to, and a single
  reduced-motion rule that zeroes the tokens flattens both.
- **Zero the *delays* too, not just the durations.** `transition-delay:
  calc(var(--i) * var(--line-step))` still staggers under `prefers-reduced-motion`
  unless `--line-step` is zeroed as well.
- **A CSS-only "smooth scroll" is a lie.** If a transition is meant to be a
  scroll, two screens must genuinely occupy the page one height apart so the
  scroll container is really that tall — otherwise the smoothing engine finds
  nothing to scroll and completes instantly, with no error anywhere.

## Pitfalls (each cost a real iteration)

- **Text-size settings must reach every tier.** A zoom variable that touched 22 of
  927 rules produced 8 px labels that never grew.
- **Sweep for hard-coded brand colours.** Two controls painted `#0505e8` regardless
  of theme and clashed with every palette; point them at accent tokens.
- **A light translucent card needs its own edge treatment** — reusing the dark
  recipe gives cards that merge with the canvas.
- **Deepening a light canvas and lightening an accent fight each other**; budget for
  it (a canvas change pushed `accent on canvas` from 4.9:1 to 4.42:1).
- **Windows + screenshot harnesses:** a `:` in a generated filename creates an NTFS
  alternate data stream and the file vanishes. Sanitise `[:\\/*?"<>|]`.
- **Verify on rendered pixels.** Sample a text-free column inside a card and compare
  top to bottom; a flat result means the "glass" is opaque, whatever the CSS says.
  Verify the final artifact — every CSS change invalidates the previous e2e pass.
- **MSYS paths:** Node cannot read `/c/Users/...`; pass `C:/Users/...` to native tools.

## Deliverable shape

When delivering a theme: the palette document + a notes file (palette table, contrast
numbers, the material values, how to dial it) + rendered screenshots, filed per the
`file-organization` skill (reusable specs → `_Knowledge/`, session artifacts → the
session folder). Keep the change set revertable: one override file plus one `<link>`,
so "revert" is deleting one file and one line.
