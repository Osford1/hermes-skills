---
name: offline-single-file-web-builds
description: "Use when a web build must run offline from file://."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [web, offline, file-url, canvas, verification, contrast, gsap, lenis]
    category: software-development
    related_skills: [web-design-recipes, glassy-panel-design, visual-artifact-verification, file-organization]
---

# Offline single-file web builds

This user's web deliverables are single pages they open by **double-clicking** (`file://`): widgets,
demos, 3D instruments, experiment reports, one-off gift pages. No network, no build step, no npm.

That constraint is the whole class. The failure mode is never "it looks wrong" — it is **"it silently
does nothing on their machine"**: a CDN link that never resolves, an effect that threw, a scroll that
scrolled nothing, audio the browser blocked. None of those show up in the CSS, and none of them raise
an error you would notice. So this skill is a build procedure with the verification welded on.

Aesthetics, palettes and motion recipes are `web-design-recipes`; the glass material is
`glassy-panel-design`; generic render checks are `visual-artifact-verification`. This one is the
offline build and the measurement that proves it works.

## 1. Set the folder up before writing a line

1. One build = one folder = one `index.html`, under `Deliverables/WebApps/<app>/`.
2. **Never let two sessions aim at one output path.** `write_file` overwrites, so the later writer
   destroys the earlier build with no error anywhere. If the user is A/B-ing two models (or two
   agents) on the same brief, each run gets its own folder *before the first write*, and the brief
   names the file. Recovery when it has already happened:
   `references/recovering-clobbered-files.md`.
3. Layout: `index.html`, `lib/` (vendored libraries), `assets/` (media the page expects), `NOTES.md`.
   Declare the asset filenames in a short README inside `assets/` so dropping real media in later
   cannot shift the layout.
4. **The thing you hand over is the FOLDER, never `index.html` alone.** A page with `lib/` and
   `assets/` opened without them does not degrade gracefully — it stops: the screens past the first
   are `hidden` in the markup, so the user gets a dark page and one button that does nothing. Write
   "send the whole folder" into the gate report; "a single self-contained page" invites exactly the
   wrong instinct when they copy it somewhere.
5. Procedural media (a photo that assembles itself shape-by-shape, generated textures) is built
   offline and dropped into `assets/`; recipe for primitive-style GIFs: `references/generated-image-assets.md`.
6. **Keep the sources apart and GENERATE the single file.** For a build with real logic inside it
   (a simulator, a calculator, anything whose numbers get quoted), write `engine.js` + `app.js` +
   `shell.template.html` and have a `build.py` inline the two scripts into the shipped `index.html`.
   The shipped page is then a *build product*: parity with whatever reference implementation the
   numbers came from is structural rather than hand-copied, and there is only one copy of the formulas
   to drift. Say so in the README, rebuild after every edit, and re-load the built file for the browser
   checks — a stale build is silent. Recipe, with the numeric-parity harness that proves the page's
   numbers equal the reference engine's: `references/reference-implementation-parity.md`.
7. **A modular page (`<script type="module">` + `import`) is dead on `file://` until it is inlined.**
   Chrome blocks ES module loads from a file:// page (opaque origin → the fetch fails CORS), so a
   double-clicked modular page runs *no* JavaScript: any part of it built in JS — a canvas, or an
   `<svg>` assembled with `createElementNS` — is simply absent, and every control does nothing. The
   page is correct over http; only the offline open breaks. Inlining is what fixes it, and
   **concatenating the files into one scope does not work**: four sources flattened together collided
   on a top-level `clamp` and the whole bundle died with a SyntaxError, leaving the page exactly as
   broken as before for a different reason. Scope each source and hand its exports to a registry —
   procedure, gates and the verification that catches this: `references/inlining-es-modules.md`.

## 2. Libraries: vendor them, and take exactly one scroll authority

1. **Copy libraries into `lib/`** and reference them relatively. Pinned offline-ready copies live in
   `_Knowledge/vendor/` (GSAP 3.15 core + plugins, Lenis 1.3.26, with a README recording versions,
   licence and a `selftest.html`). Plugin files must come from the same release as the core — copy the
   set out of one folder, never mix.
2. **One scroll authority.** Lenis is it. Do not also take GSAP's ScrollTrigger/ScrollSmoother for
   the same job; two of them fight over the same scroll position. Take only the plugins the build
   actually calls — an unused plugin is also an unused failure mode.
3. **Gate on network references.** Grep the shipped file for `https?://` *and* check the live DOM's
   `[src]`/`[href]`. A CDN link pasted in while debugging is the most likely way the offline promise
   quietly breaks. A grep for `src=` also matches **commented-out** markup — an `<img>` written inside
   an HTML comment as a note to the user is inert, so confirm the line is really live before calling a
   missing asset a 404.
4. **Vendor-able is not adoptable.** An animated background of
   the Vanta class is your own `<canvas>` painted from the same palette: pre-render the pattern into
   2–3 offscreen **tiles** once, then `drawImage` twice per tile per frame (offset wraps, so the tile
   repeats seamlessly). Repainting a hundred radial gradients per frame is the version that stutters.
   Before taking a real WebGL library instead — three.js + Vanta vendor cleanly (643 KB, MIT, loads
   from `file://`, zero console errors, palette reproduced exactly) — prove the frame budget on the
   *target machine*. It measured ~8x the canvas field here and dropped the page to ~18 fps, a budget
   the scroll choreography shares. Procedure, the hardware-vs-software renderer check, and the
   render-once-into-a-texture compromise: `references/effect-library-adoption.md`.
   Seams, the ball-vs-fog fix order, depth composition and pointer parallax:
   `references/canvas-field-rendering.md`.
5. **Stop painting when the tab is hidden** (`visibilitychange`), and draw a single static frame under
   `prefers-reduced-motion` rather than looping.

**A library you must also *drive*: patch the vendored copy, don't fork the source.** Read the
package's *published build* before writing any integration code — its parameter/option table is the
real public API, and an option that reads like a styling scalar can be the physical channel you
actually want (a figure's `intensity` turned out to be its hinge angle, so no source fork was needed
at all). When the public API genuinely lacks the handle, add **one documented hook line plus one
small API block** to the vendored file, expose it as a `window.__lib` handle so the harness can
assert the knob from outside, and record the patch, its reason and its exact hunk in a header comment
at the top of that file — re-vendoring then means re-applying one documented hunk instead of
re-deriving it. Prefer that to a source fork whenever the patch is a handful of lines: a fork stops
tracking the upstream version.

**An in-page overlay needs its own scroll authority — declare it, don't fight the wheel.** A
smooth-scroll library that owns the window will not hand wheel events to a modal, reader or detail
sheet sitting on top of it: give the overlay `data-lenis-prevent` (with `overscroll-behavior:
contain`) and put its content in its own `position:absolute; inset:0; overflow-y:auto` child rather
than on the scrim itself. Reach for the declarative attribute over `lenis.stop()` — freezing the
scroll authority is for holding the page behind the overlay still, not for redirecting its input.

## 3. Motion: every effect gets a reduced-motion branch

List the effects in a table — *moment / where / built with / what it does under reduced motion* — and
hold the build to it. Two rules that are easy to get wrong:

- **Zero the delays, not just the durations.** `transition-delay: calc(var(--i) * var(--step))` still
  staggers under `prefers-reduced-motion` unless the step variable is zeroed too.
- **The flow must complete with every effect off.** Some effects are decoration (a click tick, a
  float, a magnetic pull) and may simply stop. Some are functional (the "it's finished" chime) and
  should survive. Decide which is which deliberately and say so.

An element returning from `display: none` cannot transition in that frame: set the hidden state, force
a reflow (`void el.offsetHeight`), then apply the visible state on the next frame.

**Time a screen by its words, not by its animation.** When a screen advances on its own ("the intro
has finished"), the dwell is a *reading* budget — and building it out of the entrance animation is
the trap, because the two are unrelated. An entrance of `step*2 + lineDur + settle` (400 + 900 +
1500) ends at 2.8s, so a 27-word intro left the screen with its last line legible for ~1.5s: a third
of the time it takes to read, on the one screen that is actually talking to the reader. Fix:

- Count the words **from the markup at runtime** (`screen textContent` split on whitespace) and set
  the dwell to `words * 320 + 800` ms — 27 words becomes 9.4s. Keep the multiplier generous; a quiet,
  personal register is a slow reader on purpose.
- Floor it, don't replace it: `max(end of the entrance animation, read time)`. Counting from the
  markup is the same discipline as reading timing tokens back from CSS — the copy and the timer
  cannot disagree, and rewriting the words re-times the screen by itself.
- Under `prefers-reduced-motion` the entrance is 0ms, so the reading clock *is* the whole wait. One
  formula covers both branches, and a reduced-motion reader is not rushed because their animation
  was removed.
- Quote the pair in the report ("2.8s of dwell for 27 words of copy") — the two numbers together are
  what make the fix self-evidently right.

**A screen swap is also a screen-reader event.** One-screen-at-a-time pages are silent to assistive
tech — the arriving screen is nothing but elements that appeared — so the swap needs a live region, focus
moved into the incoming screen, and no `aria-disabled` on anything still selectable:
`references/flow-a11y.md`.

## 4. Verify by measurement, never by reading the CSS

"The CSS looks right" and "the page works" are different claims, and only one is checkable.

1. **Run the contrast pass on rendered pixels.** Script and the browser-side snippet to produce its
   inputs: `scripts/verify-contrast-pixels.py`. Hide every glyph, screenshot, sample the surface under
   each text run, compare against that element's real colour. Tokens cannot see the composite of
   surface + bloom + backdrop that text actually sits on — a pair that clears the contract on the flat
   canvas measured **4.53:1** on the surface the gradient actually produced, and text laid straight on
   a *moving* background measured **3.18:1** while everything on a card passed at 5.5+.
2. **Repeat per screen AND per background state.** Capture each screen at more than one point in the
   backdrop's drift and treat the worst phase as the result. A moving backdrop has no single answer.
3. **Ship a small verification seam**, e.g. `window.__build()` returning the real state — current
   screen, which effects are live, audio events, measured widths, document height. Assertions beat
   inferring behaviour from pixels, and nothing in the page may depend on the seam.
4. **Prove sound without ears.** Install a spy BEFORE the page loads
   (`Page.addScriptToEvaluateOnNewDocument`) that wraps `OscillatorNode.prototype.start` and logs
   frequency + timestamp. That turns "no audio before a user gesture" and "the chime fired on the
   final click" into assertions.
5. **Check the axis of a layout that is supposed to grow.** Panels meant to sit a viewport apart must
   STACK; inside a flex *row* they sit side by side, the document never grows, and the "smooth scroll"
   scrolls nothing. Inspect the container's `display` before blaming the scroller.
6. **Assert the transition actually moved.** Sample the element's box several times *during* the
   animation: a FLIP that jumps in one step never animated, and the final position looks identical.
7. **When a measurement says a feature is broken, check the probe before the product.** A pointer
   aimed at a coordinate the element had already leaned away from, and a frequency filter wide enough
   to count a chime note as a click tick, both looked exactly like product bugs.
8. **A metric's threshold must be absolute, never a fraction of the thing it measures.** A feature
   count that fires at "5 % above the local mean" shrinks along with the contrast it is counting, so
   flattening the field reports improvement for free. Count features *below* the background as well as
   above, or half the structure is invisible to the number. And when the ask is a *direction* rather
   than a defect, one proxy is never the verdict: read them all at once
   (`visual-artifact-verification`, "when the change is a dial, not a defect").
9. **If the page prints numbers, gate on numeric parity with a reference implementation.** Port the
   engine verbatim (same formulas, same update order, same PRNG draw order, same accumulation order),
   dump the same `(case, config, seed)` list from both sides, and compare every float element-wise —
   worst diff ~1e-11 expected, a field off by ~1e-2 is a real bug. Then cross-check the page's own
   aggregates (its batch table) against a table computed independently in the engine. Full recipe:
   `references/reference-implementation-parity.md`.

## 5. Pitfalls that cost real iterations

- **Direction is not progress.** Flattening a shape cut round-share 85 % → 43 % *and* raised edge
  energy 75 %, because compressing the vertical gradient sharpens the horizontal one — a change that
  is plainly right on one axis can be a regression on another. And check the artifact still reads as
  what it was: erasing a cloud sea to featureless grey passes "not ball-like" and fails the brief.
- **Any layout measurement taken while the element is `display: none` returns 0.** A card track
  measured at boot reported `scrollWidth 0`, and the wrap logic then wrapped around a width of
  nothing. Measure on arrival at the screen, and re-measure on resize.
- **Lenis caches its scroll limit.** Grow the document and call `scrollTo()` in the same tick and it
  completes instantly, silently, with no error. Let two frames pass and call `lenis.resize()` first.
- **An inline `style` on an element beats every stylesheet rule.** A CSS override that does nothing
  looks exactly like a broken selector — check for inline styles before rewriting the CSS. The same
  mechanism makes a *state* class unreachable on a library-animated element: GSAP writes `opacity`
  inline, so `body.is-busy .card { opacity: .7 }` never renders on a card the reveal is animating.
  The class is not weak, it is inert — check the computed style before claiming what it did.
- **`opacity` on a disabled control dims its LABEL too.** A disabled button at `opacity: .45` put its
  own text at 3.84:1. Give the disabled state its own surface and text colours.
- **A `disabled` control fires nothing at all** — no `click`, no `pointerdown`, no hover; the browser
  swallows them all. An effect hung on it (a shake on a "send" button whose URL is still a stub) can
  never run, and the dead feature only becomes visible the day the control turns on. Attach the effect
  to a wrapper, or keep the control enabled and inert.
- **Text laid straight on a moving background fails, and only that text fails.** Fix with a feathered
  scrim under the text column — not by darkening the type, which then has to out-run the background's
  whole range. The scrim's real win is that the numbers stop changing as the backdrop drifts.
- **A see-through surface is not proof the blur renders.** Compare edge sharpness of a hard-edged
  pattern inside the panel against outside it, with `backdrop-filter` on and off; an in-card gradient
  ramp only proves translucency.
- **Reserve the scrollbar gutter** (`html { scrollbar-gutter: stable }`) if the document ever becomes
  taller than the viewport mid-transition, or the page jolts sideways as the bar appears.
- **Keep timings in CSS custom properties and read them back in JS**
  (`getComputedStyle(root).getPropertyValue('--dur-scene')`) so a JS timer cannot drift from the
  animation it belongs to. That keeps an *animation* honest — an animation duration can never set a
  **reading** dwell, which is a different quantity entirely (§3).

- **A `<link rel="preconnect">` is a network reference too.** Font snippets copied off the web ship a
  preconnect pair above the stylesheet; on a `file://` page neither can warm anything, so they belong in
  the same deleted block as the CDN stylesheet (§2.3). A validator that allowlists exactly one remote URL
  still fails the run on the preconnect lines — and that failure reads as mysterious, because the line was
  doing no work.

  - **A vendored file that never downloaded fails at runtime, not at build time.** A chained `curl`
  can exit non-zero with no visible error (e.g. a write error when output is redirected), leaving a
  missing or truncated `lib/*.js` that makes the page silently dead. After every vendor download,
  assert the file exists and has plausible size (`ls -la`, or use `curl -f` to fail loudly) before
  writing any code against it.

  ## 6. How this user wants the deliverable documented

Non-negotiable on every build of this class:

- **`NOTES.md` next to the page**, updated every stage: a block-by-block map (*thing / what it is for /
  where the code lives*), every measured table, and the defects found — with the cause, not just the
  fix.
- **Comments in the code that say what a block is FOR**, not what it does, and that name the rule
  doing the work at each decision point. The user is learning the language from these files.
- **Close each stage with "try these 3 edits"** — three one-line changes they can make themselves,
  each with what they should expect to see. Prefer edits that demonstrate a *rule* (surface alpha, a
  timing token, an edge treatment) over cosmetic tweaks.
- **Mark drafted copy `DRAFT`** in the markup, so the words they will rewrite are findable.
- **Never ship a live control that goes nowhere.** A button whose URL does not exist yet renders
  `disabled` with a visible note; one edit switches it on.
- **Report measured values, and say plainly which claims you did not verify.** The user checks, and
  "measured" versus "should" is the difference they care about.
- **A number in a code comment or in `NOTES.md` is a claim like any other.** Measured-*sounding* is not
  measured: a comment asserting the dimmed labels "still measure 5.2:1" was contradicted by the first
  real capture (3.62:1), and the justification for the dim had to be withdrawn with it. Take the
  number from a capture, or write it as an expectation and label it one.
- **"Critique this" is a read-only turn.** When the user asks for thoughts on a build before any edit
  ("don't change anything, give me your thoughts first"), the ranking *is* the deliverable: what still
  deviates from the brief's letter, ranked by consequence; what is still in your voice rather than
  theirs (draft copy, empty asset slots); and what you have not actually verified. Fix nothing in that
  turn, and do not pad it with what is already right — the user is asking what is wrong.
- **Expose the knobs in one labeled `CONFIG` block at the top of the script** — passwords, copy,
  speeds, counts, asset paths — and quote its location in the handover. This user tunes builds
  themselves; "tell me how to control the speed" must be answerable with one named setting, not a
  line number buried inside a loop.

## 7. File the record

Per `file-organization`: the page + `NOTES.md` in the app folder, measurement evidence (screenshots at
each width, the text-hidden shots used for sampling, any harness script) in the project's `Working/`,
the palette JSON if one exists, and one line added to `_INDEX.md`. Keep the harness — the next change
invalidates the previous pass.
