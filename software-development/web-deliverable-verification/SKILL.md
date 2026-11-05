---
name: web-deliverable-verification
description: "Use when shipping a web page: verify it on rendered pixels."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web, verification, contrast, accessibility, staged-delivery, browser]
    related_skills: [web-design-recipes, glassy-panel-design, visual-artifact-verification]
---

# Shipping a web deliverable

How to build and hand over a web page for this user so that "done" means verified rather than
plausible. Companion to the design skills — this one is the **delivery workflow and the gates**,
not the visual recipes.

- Design recipes, tokens, palettes, motion: `web-design-recipes`
- Glass/translucency material and the palette contrast contract: `glassy-panel-design`
- Generic HTML/SVG artifact rendering: `visual-artifact-verification`

## When to use

Any build the user will open themselves — a gift page, a portfolio, a demo, a widget, a
single-file app. Also when a build is already in progress and a stage is being handed over.

## 1. Stage the build — one stage per turn

A build of real size is delivered in **stages, one per turn**, and each stage ends with the path
and a stop:

1. **Skeleton + flow** — every screen, the real words, working Next/Back. Plain styling, no
   libraries, no background, no audio. Goal: the flow runs start to finish.
2. **The look** — tokens, type scale, spacing, the material, both widths.
3. **Background and transitions.**
4. **Motion** — sliders, FLIP, magnetic buttons, floating text.
5. **Audio, the shake, the external link.**

- **Stop and say so.** A build that jumps four stages in one pass cannot be debugged, because a
  break has no known cause. Put the stop into the brief so the model executing it obeys.
- **Keep `NOTES.md` beside the page** — a block-by-block map (what each block is for, where the
  code lives), the measured tables, the defects each stage found, and a per-stage **"Try these 3
  edits"**: three one-line changes the user makes themselves, each with what to expect. That
  block is the lesson; the page is the excuse.
- **Comment the CSS in plain English** — what each block is FOR, not what it does — and name the
  brief rule doing the work at each decision point.
- **Draft missing copy and tag it.** `<!-- DRAFT -->` plus a cap on length. Never filler: filler
  is what makes a page read as generic.
- **Stubs ship disabled.** A control that depends on content which does not exist yet (a form
  URL, an external link) renders `disabled` behind one constant with a `TODO`.
- **A labelled placeholder is not a loader.** A stage-1 block that prints the filename it wants
  (`<span class="slot">navy.jpg</span>`) tells the reader where an asset goes but never reads it.
  Grep for the loader (`<img`, `url(`, `background-image`, `new Image`) before answering "where do
  I put the photos", and say plainly that dropping the files in changes nothing on screen until
  the slot renders them — otherwise the user files six photos and reasonably reports the page as
  broken.

## 2. One writer per output path

Give each build its own app folder (`Deliverables/WebApps/<app>/`) so there is exactly one
`index.html` per app. **Never write a page into a path another session may own** — two sessions
on one path is how a finished build gets destroyed. When `write_file` warns that a sibling session
modified the file, treat that as a stop signal: read the file first, or choose your own path.
Recovering one that was already overwritten: `session-transcript-recovery`.

## 3. The gates — run these before calling a stage done

Report the numbers, not a verdict.

1. **Offline.** `grep -c 'https\?://' page.html` = 0, and the same count over `[src]`/`[href]` in
   the rendered DOM. A CDN added "just to make it work" is the most common quiet breach of an
   offline brief — grep the *rendered* DOM too, not only the source.
2. **Walk the flow in a real browser, using the build's own selectors.** Every screen, and Back
   from each. A CSS class existing does not mean a click target exists; a walk driven by
   selectors invented from a different build tests nothing and reads as a failure of the page.
3. **Measure contrast on rendered pixels**, per screen, and **twice per screen when the backdrop
   animates** — `scripts/verify-contrast.py`. A drifting backdrop puts a different band behind the
   same words a second later, so one capture is a sample, not a measurement.
4. **Zero horizontal overflow** at laptop and phone widths
   (`document.documentElement.scrollWidth <= innerWidth`).
5. **Every preference branch still completes the flow** — reduced motion, reduced transparency,
   more contrast. Motion may vanish; the way through may not.
6. **State the deviations** from any spec being followed (a spec tuned for a 320 px side panel is
   not a spec for a 1440 px page) rather than silently bending it.

Brief template, the acceptance list in full, the five blanks that decide quality, and the
iteration prompt: `references/staged-build-brief.md`.

## 4. Contrast is measured on pixels, not read off the CSS

**Method.** For each screen: collect every visible text run's rect *and* its computed colour, hide
the glyphs
(`*,*::before,*::after{color:transparent!important;-webkit-text-fill-color:transparent!important}`),
screenshot, then sample the surface under each run and compare. Capture one pair **per screen** —
a page whose screens show one at a time has nothing to sample on the screens that are not up.
`scripts/verify-contrast.py` runs the sweep and also reports the in-card luminance ramp.

Two defects this catches that reading the CSS does not:

- **A disabled state built from `opacity`.** `opacity` composites the label with the background,
  so a filled button's *text* contrast falls with the fill — a 45 % dim measured **3.84:1** on a
  button whose enabled form measured **10.8:1**. Give the disabled state its own surface and text
  colours (`opacity: 1`) and re-measure.
- **The transient states are the ones nobody measures**, because each exists for a second
  mid-transition: busy, pending, mid-FLIP. A 0.70 dim across the controls put a payment button's
  labels at **3.62:1** against **5.50:1** undimmed — and the dim had been justified in a comment by
  a "5.2:1" nobody had ever captured. Two shots answer the whole question without building a
  variant: the dimmed frame plus the text-hidden frame recover the undimmed colour per channel
  (`T = (A - (1-o)*B) / o`, cross-checked to (229,233,231) against the declared (238,244,242)) and
  predict the contrast at **any** opacity. Then let the prediction decide the affordance: holding
  4.5:1 here would need **~0.90**, and a state that close to solid is not an affordance — so signal
  "busy" by refusing the interaction (`cursor: progress` plus the click guard that was already
  swallowing clicks) and leave the labels at their measured colour.
- **A "glass" surface that is really an opaque fill.** Sample a vertical strip inside a card with
  the text hidden: a flat result means the blur sits over a flat fill. Target **≥2.5 L\*** of
  change top to bottom; a bloom behind the content is what produces it.

**Text on a moving background needs a scrim, not a darker colour.** Measured on a page whose
backdrop drifts: every failure sat on text with **no surface under it** — body copy straight on
the drifting field fell to **3.18:1**, a footer note to **4.21:1**, while every run inside a card
passed at 5.5:1 or better. Darkening the text does not fix it, because the band behind it keeps
changing. Put a soft feathered veil under the text column (`.screen::before` — a near-white radial
gradient at ~90 % fading to transparent, `filter: blur(12px)`, `z-index: -1`, with `isolation:
isolate` on the parent so it stays above the background and below the text) and **re-measure**:
those two runs went to **6.29:1**, and the two phases of the animation then reported *identical*
numbers — which is the point, because the text has stopped depending on what is drifting past.

- **A scrim is sized for what it protects.** One built to sit behind a 68ch column of body copy
  becomes a full-page white sheet the moment that screen goes full-bleed, and the background
  vanishes under it. A screen with no body copy (a splash: one heading, one button) needs none.
- **A scrim behind the glass turns the glass opaque, so the veil belongs on the words, not on the
  page.** The screen-wide veil above fixes text contrast and quietly destroys the material: the
  same card over the same backdrop read `#f4f9fc` with the veil behind it and `#c6e0f8` without —
  **9–10 L\* inside the cards, while the bare backdrop 60 px away moved 1.5**. The glass was
  faithfully showing the veil, which is why a transparent surface kept reading as a white panel
  while its CSS said otherwise. Put the backing on each run of TEXT instead (its own small blurred
  pseudo-element, or a text shadow) and let the panels sit on the real background: same contrast
  guarantee, one layer lower. Probe it by sampling a card's interior with the veil enabled and
  disabled — a number that barely moves means the veil is not the cause

**Two probes for the material itself**, both cheap, both better than reading the CSS:

| question | probe | what to expect |
|---|---|---|
| Is the surface see-through? | screenshot the same element over a **flat white** backdrop, then over a **flat dark** one, sampling the same pixels | opaque reads **0.00 L\*** apart; genuinely transparent moves **9–17 L\***. A blur cannot fake this — blurring a flat colour leaves it flat |
| Is the blur rendering at all? | put a **hard-edged striped wall** behind it, then force `backdrop-filter: none` and shoot again; compare edge sharpness inside the element against just outside it on the same stripes | blur on erases the stripes (inside/outside ≈ **0.01**); forced off leaves them (≈ **0.6**) |
| Does the backdrop **refract** (Apple "Liquid Glass")? | reference an SVG `feDisplacementMap` filter from `backdrop-filter` and put a **hard-edged grid** behind the page; compare an identical-CSS pair against the displaced one | a *turbulence* map **marbles** the grid inside the panel — it churns the backdrop instead of bending it, and takes the text's contrast with it. An **edge-vector** map (R/G encoding an outward radial direction whose magnitude grows toward the rim) is what lenses. If you cannot build that, the material's readable cues are all rim: a crisp 1 px rim, a flare just inside it, a top specular, opposed cyan/warm 1 px fringes, light pooling below, and a near-clear middle — say plainly that the panel flares where the reference bends |

For the transparency question the stripe pitch must be **coarser than the blur radius**. At 16 px
against an 18 px blur the probe measures the blur, not the transparency, and reports "opaque" for
a surface that is visibly shifting 12 L\*.

**Re-run the whole pass after any CSS change** — every change invalidates the previous pass, and a
moving background invalidates it by definition.

## 5. What pixels cannot show — probe the state instead

Contrast and layout are visible; **whether an effect ran is not**. An audio cue, a library
instance, a tween, a scroll that actually moved — any of these can be silently absent while the
page still looks finished. Give the page a small read-back seam and assert on it:

```js
window.__app = () => ({ screen, reduced, lenis: !!lenis, audio: Sound.log, docHeight, … });
```

Then read it after each step of the flow (`js('JSON.stringify(window.__app())')`). This is how the
things a screenshot cannot show get proven: **zero oscillators before any user gesture** (the
autoplay policy failing silently), the chime firing *inside* the click handler, the reduced-motion
branch genuinely switching libraries off, and a smoothed scroll passing through intermediate
positions instead of jumping.

- **A scroll that "works" has to be caught in the act.** Sample `scrollY` every ~200 ms across the
  transition and count the distinct intermediate values: eight steps on a deceleration curve is a
  real smoothed scroll; `0 → 900` between two samples is a jump dressed as one.
- **Spy before the page loads.** For anything that must *not* happen at load, install the probe
  with CDP `Page.addScriptToEvaluateOnNewDocument` and patch the prototype
  (`OscillatorNode.prototype.start`) before navigation — a probe installed after load cannot see
  what already fired.
- **Keep the spy's filter narrow.** A frequency window wide enough to include the cue you are
  trying to exclude counts it, and the total then looks wrong for the wrong reason.
- **Assert the flag, not the appearance.** `is-active`, `disabled`, `scrollHeight` before and
  after — a class that exists in the markup proves nothing about what the code did.

## 6. When the browser harness is down: drive headless Chrome directly

The `browser_exec` harness can fail mid-task — a wedged daemon port file, or its browser binary
gone (`[WinError 2] The system cannot find the file specified`). That is not a reason to hand over
unverified work, and not a reason to guess: layout, computed style and geometry are all measurable
with Chrome alone.

**A page that is *served* rather than opened from disk wants a persistent session, not a one-shot dump.**
ES modules, `fetch()` and any relative path need `http://`, so `file://` is not available: run a tiny
static server over the build folder and drive one long-lived Chrome over CDP, taking a screenshot at
each state of the flow. That makes verification a re-runnable artifact — the same step script re-shoots
every state after each edit, and the numbers are comparable across passes. Server rules, launch flags,
the step-script schema and the failures that cost a run each: `references/cdp-step-harness.md`.

**Method.** Write a *copy* of the build **beside the original** — same directory, so its relative
`lib/` and asset paths still resolve; a copy in a temp dir 404s its own scripts and you then measure
a page with no JS — with a probe `<script>` appended before `</body>`, then:

```
chrome --headless=new --no-first-run --no-default-browser-check \
       --user-data-dir=<fresh temp dir> --window-size=1440,900 \
       --force-device-scale-factor=1 --virtual-time-budget=20000 \
       --dump-dom  file:///<the probe copy>
```

- `--virtual-time-budget` lets **timers** run through before the dump, so you measure after boot
  instead of mid-load. Real CPU work still takes real time — a WebGL bake on a cold GPU takes
  seconds — so give the command a generous timeout rather than blaming the page.
- **It does not drive `requestAnimationFrame`.** Under `--headless=new --dump-dom` timers fire and
  rAF does not: a probe that waits on rAF waits forever, and GSAP (which ticks on rAF) sits frozen at
  its first frame while `setTimeout`-driven code walks past it. Measured: three awaited waits ran,
  the click was dispatched, and not one frame callback arrived — the dump carried the probe's
  progress markers and no samples. Shim it in the page **head, before the app's own script** —
  `requestAnimationFrame = cb => setTimeout(() => cb(performance.now()), 16)` (plus the
  `cancelAnimationFrame` twin) — and virtual time drives the animation, the library and the probe
  together. Timestamps stay meaningful because the shim passes a clock reading, not a frame id.
- **`--dump-dom` is the read-back seam.** Have the probe write one `PROBEOUT {json}` text node:
  quotes survive serialisation intact, so one regex plus `json.loads` returns every number. Parse
  the JSON and print named keys; dumping the raw DOM to stdout buries the answer in 100 KB of HTML.
- `--screenshot=<abs path>` in a second run of the same flags gives the picture for a vision check.
  A fresh `--user-data-dir` keeps all of this clear of the user's own browser session.
- **Make the before/after a same-page comparison.** Have the probe measure the new state, then undo
  the change (clear the inline width/margin the rule would have set), measure again, and report
  both. A remembered "before", or a second run against a different copy, is not evidence.
- Grid to include every time: the boxes that must NOT move (the reading column), the box that must
  (the thing being changed), first-child position, `scrollWidth` vs `clientWidth`, the computed
  value of any token the rule relies on, a console-error count, and — when a transition's handover
  depends on it — the *other* layout state, measured by adding and removing its class.
- Delete the probe copy when done. It is a copy, not a deliverable.

## Pitfalls

- **Never judge a page from its CSS.** Every defect above was invisible in the stylesheet and
  obvious in a screenshot.
- **Do not spot-check contrast.** Sample every text run: the failures live on controls in their
  non-default state (disabled, pressed, hovered).
- **Copy each screenshot to its own filename immediately** — a fixed capture path silently
  overwrites the previous shot, and a `:` in a generated filename creates an NTFS alternate data
  stream on Windows, so the file vanishes. Sanitise `[:\\/*?"<>|]`.
- **Stage 1 must stand alone.** A page with no libraries is the cheapest thing to debug; do not
  pull a library forward into it because the final page will need one.
- **A measurement that cannot tell your two hypotheses apart is worse than no measurement,
  because it reads as evidence.** Before trusting a number, ask what the *other* explanation
  would have produced. Three that reported product bugs and were instrument faults: a stripe
  probe finer than the blur it was measuring; a magnetic-button probe aimed at a coordinate
  captured *before* the element leaned away from it (so it measured the release, not the lean);
  and a click-driven capture pass that navigated to the next screen and so photographed a screen
  with no cards on it. Re-aim, re-pitch, or re-order the capture — then re-run.
- **Layout is not paint: assert the subject painted, not that it is on screen.** A hidden subtree
  keeps its box, so every rect, transform and computed position still reads correct while the pixels
  show nothing. A single wrapper carrying both the copy and the figure had `opacity: 0` applied to
  hide the *copy*, and took the figure with it — every geometric probe agreed the figure was in
  place, and the screenshot was empty. Rule the CSS by *what the wrapper contains*, and assert a
  render by counting non-background pixels inside the element's rect (or sampling max luminance) at
  each state. When a vision read says "nothing is there" and your geometry says otherwise, the two
  are not in conflict: believe the pixels and go looking for a visibility rule on an **ancestor**.
- **A rect used for a zoom or framing calculation must be read in the parent transform's identity
  space.** `getBoundingClientRect()` already includes every ancestor transform, so a camera or frame
  factor computed from it and then applied on top double-counts the scale. The symptom is an
  over-zoom by roughly the intended factor squared, with the subject thrown off-screen — while the
  arithmetic reads as correct, which is what makes it expensive.
- **To fill the frame with a drawn object and still keep its border visible, frame the outline's
  axis-aligned bounding box, not its largest inscribed rectangle.** A rotated or skewed face
  inscribes a box about a quarter of its own extent, so framing the inscribed rect over-zooms
  (~2.2×) and crops the object away; the inscribed rect is the right target only for the *content
  box* that sits inside the object.
## 7. A designed transition that jumps: sample the arriving element frame by frame

When someone says a transition "snaps / jumps / isn't smooth", do not read the CSS and guess.
Drive the *real* control (click the real button) with a rAF sampler that records, every frame:
the scroll position, the arriving element's `getBoundingClientRect().top`, and the state flag or
class the transition flips. Two numbers name the cause: the largest single-frame **delta** of that
rect (that is the snap, and its exact size identifies what is being added or deleted mid-flight),
and the largest single-frame **time gap** (a long task inside the click). Two families, two fixes:

- **An offset that exists only during the journey.** If a `.is-travelling`-style rule styles the
  *incoming* screen (extra padding, transform), the handover — which removes the class and resets
  the scroll in the same frame — deletes that offset, so the content steps by exactly that amount.
  Measure the arriving screen's rect in its **resting** state first, then make the travelling rule
  match it pixel for pixel. A scroll that lands at `scrollTo(innerHeight)` already puts the next
  screen where it will rest; any extra padding there is pure jump.
- **A one-off long task inside the handler that starts the tween.** Time-based easing (Lenis
  `scrollTo({duration})`, GSAP) does not pause for a stalled frame — its clock runs on, so the next
  frame jumps the ease forward (measured: a 714 ms stall made the first scroll step cover 36 % of
  the whole journey). Find the stall by comparing a cold page with a warm one: a **reload** makes
  rasters cold but keeps browser-level state (audio devices, GPU caches), which separates "first
  paint" from "one-off API cost". Classic offender — audio: `new AudioContext()` with the default
  `latencyHint` measured **569 ms**, with `{latencyHint:'playback'}` **1 ms**, while the actual
  *device open* (first `resume()` + oscillator start) costs ~**0.5 s** either way. Pay it once, in
  the **capture** phase of the first click, so it is always spent before any handler can start a
  transition; and only start a scroll tween after the click path has stopped blocking.

### Prove the state is up before you sample it.** A capture pass that sets the state through the
  build's own function can hide everything and still write a screenshot: driving this page with
  `show('s2')` while its sections were keyed `data-screen="2"` matched no section, so the function
  **hid every screen and then threw** — and the pass dutifully captured the bare background,
  reporting text runs at **4.04:1** (they measure 6.10:1 with the text actually on screen). Those
  numbers look exactly like real contrast failures, which is what makes this expensive. Assert
  `element.hidden === false` / `classList.contains('is-shown')` on the target before every capture,
  and print the assertion with the result. Related: the same trap caught a pass that clicked
  through to the next screen and photographed one with no cards on it.
- **Measure against the box the layout actually uses.** Under `scrollbar-gutter: stable` the
  content box is the viewport minus the reserved gutter (1440 − 15 = 1425), so a correctly
  centred element sits at 712.5 and reads as "7.5 px off centre" against `innerWidth`. Compare
  against `documentElement.getBoundingClientRect()`, not `innerWidth`.
- **Anything measured while a `display:none` ancestor is still in effect is 0.** `scrollWidth`,
  `getBoundingClientRect()` and every offset metric report zero for a hidden subtree — a carousel
  measured at build time then wraps around a width of nothing. Measure on arrival, when it is up.
- **A transformed element is no longer where you sampled it.** Read the rect immediately before
  dispatching a pointer event, and re-read it between the steps of a hover or lean test.
- **Do not mix captures from different passes.** A "final" sweep that reuses files measured before
  the last change is not measuring the artifact you are shipping. Clear the old set or give every
  pass fresh filenames.
- **A feature query is not a render test.** `CSS.supports('backdrop-filter','url(#f)')` returns
  true while `-webkit-backdrop-filter: url(#f)` returns false in the same build, and neither says
  whether the filter paints. Get an A/A control on pixels before designing around any capability
  claim, and always declare the plain fallback **first** so an unsupported value is dropped rather
  than fatal.
- **A smooth-scroll library caches its scroll limit.** After the document grows, `scrollTo()` has
  nothing to travel and completes **instantly and silently** — no error, no movement, and the
  read-back seam still shows the target screen, so it reads as a working transition. Let the layout
  land (two frames) and call the library's own `resize()` before scrolling.
- **A handler attached before a list is duplicated never reaches the clones.** A carousel that
  clones its items to wrap re-creates them after the initial wiring, so per-item listeners cover
  half the set and the effect looks broken on every other card. Attach after duplication, or
  delegate from an ancestor; mark clones `aria-hidden` + `tabindex="-1"`. A clone also **doubles
  every DOM query** — a six-item row returns **12** matching nodes — so a count or a loop taken
  straight from a query is not the item count: dedupe by the item's own identity key before
  counting, looping or asserting.
- **A measure in `ch` is only a measure on the element whose font it was chosen for.** `68ch` on a
  44 px heading is >1600 px, so a `max-width:68ch` intended to hold a text column in place caps
  nothing: the heading's box went 587 → 982 px while the body text next to it stayed at 453, and the
  screen then read as three different alignments. To hold a measure across a font-size change, cap
  the box whose font the measure was chosen in, not each differently-sized child.
- **Break the one element out, not the whole screen.** Widening a screen out of its reading column
  moves its copy too, so every transition into that screen shifts the text horizontally (a jump of
  ~380 px, and this user *will* report a jump). Break out the element that needs the width —
  `width:100vw; margin-inline:calc(50% - 50vw)` on that child — and leave the column alone.
- **A viewport-unit break-out is exactly one scrollbar too wide where the scrollbar is classic.**
  `100vw` includes it, so a naive full bleed overflows the page sideways by ~15 px. It is safe only
  if the page already clips (`overflow-x:hidden` on the container) or reserves
  (`scrollbar-gutter:stable`); either way **assert `scrollWidth <= clientWidth` afterwards**, don't
  assume it. `padding-inline` on an `overflow:hidden` row does not undo the bleed — the clip region
  is the padding *box*, so it insets where the content starts while the row is still seen edge to
  edge (first card landed on the 24 px page gutter, row box unchanged at 1403 px).

## 8. A FLIP inverted a frame late is painted at its destination first

A FLIP (`getState` → mutate the DOM → `Flip.from`) reports as two complaints that read as separate
bugs: *"the picture will zoom in first"* and *"the others lag behind"*. Both come from **where the
inversion happens**, and one run of the frame sampler above catches both: record the moving
element's rect, the neighbour that must not move, and `getComputedStyle(el).position`, every frame,
through a real click.

- **Invert in the same frame as the DOM change.** Wrapping `Flip.from` in `requestAnimationFrame`
  "so the layout has landed" *is* the bug: the mutation is synchronous, so the intervening frame is
  laid out **and painted with the element already at its destination** — one frame of the end state
  (measured: the photo sitting in its destination box, already grown 206×275 → 220×293, 16 ms after
  the click) — and then the invert lands, the element snaps back to its source and travels. That
  flash is "it zooms in first". `Flip.from` forces the reflow it needs when it reads the rect, so
  the wrapper buys nothing.
- **`absolute:true` takes the element out of flow for the whole flip, so everything it was holding
  up collapses.** The neighbour below jumps up by *exactly the element's height* — measured: the
  panel's copy 461 → 168 the moment the flip began, against the element's own height of 293 — and
  only drops back when the flip ends, ~460 ms later, i.e. *after* the element lands. That is the
  others "lagging behind". With `scale:true` and no `absolute`, the destination box is live layout
  from frame 0, the size change rides a transform, and nothing underneath moves. Keep
  `absolute:true` for the case where the surroundings **must** reflow.
- **Prove the fix against the old behaviour from the same build**, not a remembered one:
  monkey-patch the library call inside the probe (`Flip.from = (s, v) =>
  requestAnimationFrame(() => orig(s, {...v, absolute:true}))`) behind an env flag and run both. The
  old signature — a destination-box frame *before* the invert, two distinct neighbour positions,
  `position:absolute` present — either reproduces or the diagnosis is wrong.
- **Re-measure the return trip.** The same call is usually written twice (open and close); a
  one-line fix applied to only one of them leaves half the bug. Both directions, every card
  position (first, middle, last of the row), zero console errors.

## 9. Copy that lives in two places: the visible DOM and the attributes the renderer reads

A card, tile or list item carries its copy twice — once as markup a person reads, once as `data-*`
attributes the script reads to paint somewhere else (a detail panel, a dialog, a summary line).
Editing only the visible half leaves the page contradicting itself: the card reads one way, and the
panel it opens carries the placeholder text. Before changing copy on such a list, grep the item
markup for `data-` and the script for `dataset.`, then change every copy in the same pass.

- **Write the attributes from the visible text, not by hand.** Parse each item block, read the
  visible span, set the attribute from it. Long copy retyped into a second place is where
  transcription errors live, and they surface only on the one screen nobody opened.
- **Count what you changed, and print the count.** A pattern keyed to an exact class list silently
  skips the item carrying an extra class — `<button class="card">` matched **5 of 6** items because
  the locked one was `class="card is-locked"`. The script's own "found: N" line is what catches it;
  compare N against the number of items you expect before trusting the edit.
- **A shared name is a second place to update.** If the item also names an asset the user must
  supply, the same filename lives in the attribute, the fallback label and the folder's README.
  Change all three, or the instructions the user follows contradict the page.
- **Verify through the rendered consequence, not the markup.** The attributes are right when what
  they feed says the right words: drive each item's real control, then read back the panel title,
  the panel body, the asset filename the panel is now carrying, and the summary line — asserting
  each equals the item's own text. A grep for the new string proves the edit landed; only the
  read-back proves it reached the screen.
- **Meet a gate through the build's own control.** A locked item refuses to open until its
  precondition is met (a level picked, a tier chosen). Satisfy it by clicking the control that sets
  it, then assert the item opened — that tests the lock instead of bypassing it.
- **A comparison against an element meant to be empty is the probe's bug, not a defect.** One item
  showed a lock note where the others showed a description, so its visible description read `null`
  and the attribute comparison "failed" while the panel was in fact correct. Decide the empty case
  inside the assertion (compare against the attribute alone) rather than reporting a defect.

## 10. Wiring real image files into a node a transition reparents

- **Probe the file, then fill the slot.** `new Image()`, `onload` adds the image and a `has-photo`
  class, `onerror` leaves the labelled placeholder exactly as it was. A missing or misspelled asset
  then degrades to the empty state you already shipped instead of a broken-image icon, and the
  assets can arrive one at a time. Never assume all files are present.
- **Fixed-ratio box + `object-fit:cover`, or the photo moves the page.** The slot keeps its
  `aspect-ratio` and the image fills it, so any source size lands without shifting anything. Prove
  it: measure the box, remove the image from the DOM, measure again — the delta must be `[0,0,0,0]`
  — and re-measure the surrounding geometry against the numbers recorded *before* the images existed.
- **Anything that writes `el.textContent = ...` deletes the node's children.** A placeholder label
  and a real image in the same box means the label needs its own element, and every painter must be
  repointed at it. Check who writes into the box *before* you put an image in it.
- **Set the travelling pointer before painting, not after.** A panel that paints "the element in
  flight" reads whatever pointer was set last; if the open sequence assigns it after the paint call,
  the second item paints into the *first* item's node — silently, because a filename looks plausible.
  Symptom with images: opening card B shows card A the next card's photo. Order the open sequence
  `pointer := incoming; paint()`.
- **One element that travels beats a re-render.** Assert the panel received the *same* node by
  marking it before the click (`el.dataset.probeMark = 'A'`) and reading it back after: same node
  means the already-decoded image travels with it — no second fetch, no flash of an empty box.
- **Measure the element you mean.** In one run the "row" was read off the 12-card track instead of
  the slider window and "overflow" off that track instead of the document, which reported a
  3000 px overflow that did not exist. Read the invalidating metric (`documentElement.scrollWidth`
  vs the window's box) from the element the layout decision is made on.
- **Anchored markers can match your own probe source.** `PROGRESS ([^<]*)` also matched the marker's
  source text in the dumped DOM; bound the capture (`[^<\s]{0,20}`) and de-duplicate.

## Support files

- `scripts/verify-contrast.py` — the rendered-pixel sweep: per-run contrast against its own
  sampled background, plus the in-card ramp. Exit 0 = all pass.
- `references/staged-build-brief.md` — the first-prompt template, the iteration prompt, what
  reference material can and cannot tell you, and the acceptance list in full.
- `references/cdp-step-harness.md` — serving the build over http and driving one Chrome session
  through a step script: the two-file shape, server and launch flags, the step schema, and the
  failures that cost a run each time.
