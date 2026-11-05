---
name: interactive-concept-widgets
description: "Use when building an interactive HTML widget for teaching."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [windows, macos, linux]
metadata:
  hermes:
    tags: [visualization, html, canvas, teaching, widget]
    related_skills: [brain1-wiki-agent, pretext, p5js]
---

# Interactive concept widgets

Build a self-contained interactive HTML visualization that renders inline in the Hermes
desktop chat (`::preview{file="...html"}`) to teach a concept. Used when the user asks to
visualize or "make it click" a technical idea — typically right after a conceptual
explanation.

## How this user learns (always-on)

This user studies control-theory / motion-control papers for research prep and learns
intuitively first, casual register. Lead the teaching with these rules:

1. **Plain-language analogy before math.** Open with a concrete everyday analogy
   (bathtub = integrator/accumulator; freight train with the caboose = derivative inertia,
   position is the last/slowest car; parking-with-a-wall = state constraints).
2. **Then map the analogy onto the paper's jargon** term by term. The user's confusion is
   almost always "what does this scary word mean," so translate each term once.
3. **Then offer to build/visualize.** After a concept clicks, offer the widget; after a
   widget, offer to go deeper on one panel. Don't dump implementation unless asked (the
   user parks implementation until knowingly requested — staged delivery).
4. Respect casual, direct language. Blunt pushback ("what the heck is a manifold") is
   engagement, not hostility — meet it with a clearer analogy, never more jargon.
5. When introducing a term, give the *class* definition first ("a manifold is just a curve
   or surface inside a bigger space") before the technical one.
6. **Legibility floor: body text ≥14px, any generated label ≥13px.** Dense readouts are tempting
   at 12.5px and read as noise — matrix cells, state lines and control labels all get bumped to
   the floor before delivering, and the widget's own `font-size` is set explicitly rather than
   inherited from the frame.

## Building the widget

**Pick the substrate before you write anything — not every concept widget is a canvas.** A canvas
is for things that must be *drawn*: plots, fields, animations, geometry. A widget whose payload is
a **lookup table, a classification, a browsable catalogue, or a set of parameter pairs** is better
as DOM — every cell is a real element, so hit-testing, hover readouts, focus, tooltips and
selection state come free, and size is a non-issue (a 39×39 grid is 1521 `<i>` tags and renders
instantly). Steps 4–6 below apply only when you are actually drawing. A DOM widget still gets the
probe hook (step 7) and still gets browser-verified (step 8) — assert element counts, computed
dimensions and class state instead of `getImageData`.

**SVG is the third substrate, and it is the right one for geometric figures.** Lines, dashed families,
arrowheads, vectors, rotated labels and circles are first-class SVG elements — dash patterns, marker
arrowheads and text anchoring come free, and a re-render is just new `innerHTML`. Don't hand-roll those
in canvas. Two rules carry it:
- **Paint from CSS classes, never from JS-read colours.** `.s-fg{stroke:var(--foreground,#2b2b2b)}`
  works directly on SVG `fill`/`stroke`, so the theme stays live *and* the file reads correctly when
  opened standalone. Copying a colour into an attribute from a JS fetch is a canvas-only necessity and
  is what produces a washed-out standalone render.
- **Clip a line family with `clipPath`, never by solving the intersection yourself.** Drop
  `<g clip-path="url(#plotrect)">` around it and draw every wall, ray and `y = x` guide from −1000 to
  +1000 in data units; the renderer trims it. Hand-computed endpoints are where "the line stops short of
  the frame" and "the walls miss the corner" come from.
- **A parametrised 3D figure needs a projection helper, not a 3D library.** For coordinate frames,
  vectors and rotation diagrams, build an orthographic camera basis from two angles and push every 3D
  point through it: `f = (cosEl·cosAz, cosEl·sinAz, sinEl)`, `right = (−sinAz, cosAz, 0)`,
  `up = f × right`, `screen = (cx + s·(v·right), cy − s·(v·up))`. Then the whole figure is straight SVG
  lines between projected endpoints, and axis length/scale is one number. Put the helper on the probe
  hook (`project(v)`, `drawnEnd(i)`) and assert that a drawn line's `x2,y2` equals
  `project(expected_unit_vector)` to <0.01px — that is the geometry check no screenshot can give you,
  and it catches a transposed matrix or a flipped `up` instantly. Colour each axis from its own class
  (`.ax-x{stroke:var(--w-x)}`) so the theme stays live, and give each a matching `marker-end`
  arrowhead class.
- **Namespace every `id` per SVG panel — paint-server references are document-wide.** A `marker-end="url(#ar-x)"`, gradient or `clipPath` reference is looked up across the whole document, so it resolves to the FIRST element carrying that id. Draw several panels into one page and the ids collide: while a hidden tab is `display:none` its defs stop rendering, so the arrows in the panel you ARE looking at silently lose their heads — no console error, every DOM and count assertion still passing. Generate ids from a per-draw prefix (`ar-${MK}-x`, `clip-plot-b`) set at the top of each draw function, then assert it per panel: for every `[marker-end]` in that SVG, `/url\(#(.+?)\)/` the value and require `svg.querySelector('#'+id)` to be non-null, reporting the misses as a list. - **SVG has no `<sub>`/`<sup>` — an unknown element's text simply does not render.** A label written
 `x<sub>0</sub>` into SVG `innerHTML` shows as `x`, losing the index that carries the meaning, and
 nothing errors. Use a `<tspan>` with a smaller `font-size` and a positive `dy` (and make it the last
 child of the `<text>`). The tell is nasty: `textContent` still returns `x0`, so a textContent
 assertion passes while the render is wrong — assert the `<tspan>` exists (count children, or check
 `dy`) instead of only the string.
 - **Namespace the helpers you add to a widget's IIFE.** Re-declaring a name already used (a new
 subscript helper called `sub` when `sub` is the vector-subtract helper) is a parse error, and a parse
 error kills the entire script: nothing draws, the page's own text renders, no console error, and the
 probe hook is undefined. Prefix each new helper by what it makes (`ssub`, `svgLabel`, `proj`) rather
 than by a plausible one-word name.
 - **An auto-fitted scale must include everything you DRAW, not just the data.** When the projection's
 scale and offset are fitted to the content's bounding box, feed the fitter the extremes of the
 decorative overhang too — guide axes drawn out to fixed limits, arrowhead tips, label offsets — or
 the guides and their labels clip at the panel edge while the data sits comfortably inside.
 - **When one object is the subject and the rest are context, shrink the context.** Draw the
 non-subject frames/triads at about a third of the length, at low opacity, and WITHOUT arrowheads
 (the heads are what make N small figures read as clutter); give the subject the full length and the
 saturated palette. **Two arrows that deliberately end on the same point need their labels offset
 apart** — the shared endpoint is the lesson, and without the offset a reviewer reports the
 coincidence as a rendering collision.

 ### SVG interaction traps that cost real time
- **Never map pointer px through the border box.** `getBoundingClientRect().width` includes the 1px frame
  you drew, and the resulting ~0.3% scale error is invisible by eye but wrong in *every* drag. Use
  `new DOMPoint(e.clientX, e.clientY).matrixTransform(svg.getScreenCTM().inverse())`, which also absorbs
  CSS scaling and the viewBox; if you need a manual fallback use the CONTENT box (`clientWidth`). Then
  assert it: move the mouse N px along a known unit direction and require the state delta to equal `N/scale`
  to five decimals.
- **A drag handle must not pivot on the state it edits.** Pointing the rotate handle at the point of the
  figure nearest the data centroid looks natural, but that point moves as the angle turns, so every move
  re-derives the angle from a pivot that just moved — a feedback loop. One 30° drag spun the figure 187°,
  and 40 small steps reproduced the same 187°. Anchor the handle to something angle-independent (the data
  centroid, the plot centre, the origin), then the mapping is exact in one step *and* in forty — test both,
  requiring the handle to land within ~1px of the pointer.
- **Offset a label past the handle and measure the clearance.** A label 16px from a 7px-radius ring still
  reads as touching it, because the label's own box (say 10×12) puts its near corner 2px off the circle.
  Push it beyond `radius + half the box diagonal + 6px` and assert the box-to-circle-edge gap numerically.
- **A title that opens with a lowercase symbol reads as a truncated title.** A reader reported
  "r, the street, and why…" as cut off mid-word. Open with a capitalised noun phrase and let the sentence
  live in the sub-line.

**Anchor-verify a dataset-driven widget's data BEFORE writing any render code.** When the widget
is fed by a table scraped from a page or an API, the scrape is the likeliest source of a wrong
answer, and a wrong cell renders just as confidently as a right one. Get a machine-readable
source, then assert the values against **independently confirmable anchors** and print the checks:
at minimum three cells, including any example the source page states in prose (those are free
ground truth), and the cell the widget will open on. Popular reference pages often render cells
as concatenated digits with no separators (`158<br>2934`), which is ambiguous to parse — treat
agreement with a real anchor as the only proof you decoded it correctly, and ship nothing until
it agrees.

**Feed the widget from the run's own data through a generator, never by hand.** When the widget
explains the user's own study, read the numbers out of their data files (`Working/results/*.csv`,
`*.mat`, a constants file) in a small `build_*.py`, inject them into a `template.html` at a
placeholder, and write the page beside the study under `Working/`. Hand-typed numbers drift from the
CSV the report quotes, and the tell is a page and a report disagreeing about the same run; with a
generator, a data change is one rebuild.

**When the lesson is that a simplified model fails, draw the simplification's prediction beside the
measured truth.** The course deck's assumption (each joint controlled alone, the coupling treated as a
disturbance) is a *second series* you can compute from the same logged run — re-simulate under the
assumption (only the diagonal of the mass matrix, no gravity, no friction) and the gap between it and
the measured curve IS the explanation. A widget plotting only the real response shows the symptom; the
pair shows the cause, and it is the panel the user comes back to.

1. **Order the concept ladder** — smallest/truest concept first (how one integrator works),
   then build up (chain → order), then the hard one (manifold). One tab per rung.
   **When the lesson is a CONTRAST, hold everything fixed and flip exactly one control.** If the source's
   own examples make two different procedures produce the *same* numbers, the widget's first job is to
   break that coincidence: pin the axes, the angles and the order, and let a single toggle switch only the
   variable under test (world axes vs the frame's own axes). Then make the quantity that actually differs
   its own visual element with a numeric readout — highlight the axis the rotation really spins about and
   print that axis in world coordinates, so the two modes differ in a number the user can point at. A
   widget that varies two things at once reproduces the source's confusion instead of resolving it, and a
   contrast with no readout leaves them unable to say what changed.
2. **Write one self-contained .html** to a temp path unless the user wants to keep it;
   offer to save it durably afterward. When it belongs to a named study thread, file it under
   the archive's `Projects/<topic>/Working/` so the chat link survives the session. When the
   widget explains a specific paper or lecture deck in the vault, COPY it beside that source as
   `<deck-stem>(topic-widget).html` (`wiki/synthesis/courses/<course>/`, `raw/.../Lecture notes/`
   for the originals) and leave the temp original in place — the `::preview{file=...}` path in
   chat points at the temp copy, and a move would break it.
3. **Use the desktop theme vars, never override the frame.** The app injects
   `--foreground`, `--muted-foreground`, `--accent`, `--border`, `--card`, the app font,
   zero margins, and a transparent background. Use `var(--...)` for every color; set no
   `background`/`font-family`/`margin` on the page. Lay content flush-left (no centering
   wrapper — the frame measures width from the first span).
4. **Canvas sizing:** set `width`/`height` attributes to a fixed internal resolution and let
   CSS `max-width:100%` scale it. Do NOT size off `getBoundingClientRect` — a hidden tab
   reports 0 and blanks the canvas. Handle the device-pixel ratio with
   `ctx.setTransform(dpr,0,0,dpr,0,0)`. **Capture the intended CSS size BEFORE assigning
   `canvas.width`:** assigning it rewrites the `width` attribute, so the natural-looking
   `c.style.width = c.getAttribute('width')+'px'` sets the CSS box to the *backing-store* size and
   the canvas renders at dpr× its intended size (double, at dpr 2) while every pixel assertion
   still passes. Read both attributes into locals, set the backing store from the locals, then set
   the style from the same locals — and assert the rendered box matches the intent
   (`getBoundingClientRect().width` equals `canvas.width/dpr`).
5. **Draw every frame** with `requestAnimationFrame`; a `Play`/`Reset` pair toggles a
   `playing` flag and drives a stepped time cursor.
6. **Split static from dynamic drawing.** Pre-render the layer that only changes when the
   world changes (a sampled forbidden region, a wireframe surface) into an offscreen canvas
   once; per frame, blit it and draw only the marker/trail. Recompute the static layer only
   when its inputs change (e.g. the user drags an obstacle). Rebuilding a 60 000-cell grid
   inside a `pointermove` handler stutters visibly.
7. **Bake a probe hook into the artifact** — `window.__w = {state(), set(), ink(id),
   circles(id)}`. Verification then costs one JS expression instead of DOM spelunking, and
   the hook doubles as a smoke test if the widget is reopened later.
8. **Verify in-browser before presenting** — this is the step that catches silent failures.
   **If `browser_exec` times out or its backend is down, do not ship unverified — switch to local
   headless Chrome and keep the same assertions.** Append a `<pre id="TESTOUT">` plus a test
   `<script>` to a COPY of the widget (the copy is what you load; the delivered file stays clean),
   have that script wrap its body in `try/catch` and `JSON.stringify` the probe results into the
   `<pre>`, then run `chrome --headless=new --disable-gpu --virtual-time-budget=6000 --dump-dom
   <file:///…>` and parse the `<pre>` out of stdout (`html.unescape` it first). Match the `<pre>` by
   its tag, never by the marker string — the marker also appears in the dumped `<script>` source and
   an unanchored regex will grab that instead. Add `--screenshot=out.png --window-size=W,H` for the
   vision pass in the same run. Notes: the widget reports `standalone: true` (no frame vars), so this
   checks the FALLBACK palette — verify the framed path separately by setting `--foreground` on
   `documentElement` and confirming a node's computed colour changes; the OS colour scheme reaches
   headless Chrome, so a dark-OS run exercises the dark fallback; and a luminance helper must parse
   `#rrggbb`, not only `rgb()` — `'#e9e9f0'.match(/\d+/g)` quietly yields `[9,9,0]` and every
   contrast ratio comes out near 1.0, which reads as a failure when the palette is fine.
   Load the file with `browser_exec` as a `file:///` URL (percent-encode spaces) and confirm
   (a) no JS errors, (b) every canvas has non-zero pixels (`getImageData`, count
   non-transparent), (c) **the widget's own premise holds on its INITIAL state** — a widget
   built to show "this configuration is legal" must open in a legal one, and a default that
   violates its own claim is the most embarrassing way to pass a pixel check, (d) interactive
   mapping is exact, by dispatching synthetic `PointerEvent`s at computed pixels and asserting
   the resulting model state, and (e) state-dependent rendering, by sampling the pixel that
   should change colour. A blank canvas with zero errors means the draw code silently failed.
   You cannot see the render — the probe IS your eyes, so assert numerically. Recipe:
   `references/widget-verification-probes.md`.
   **Order the checks cheapest-first: parse → geometry → readouts → pixels.** (i) extract the
   `<script>` body and `node --check` it — a parse error leaves the static HTML rendered and nothing
   else, with no console line; (ii) run the page's own script under node against a recording canvas
   stub (`scripts/canvas-page-check.js`): no browser needed, and it reports non-finite coordinates,
   geometry drawn outside a canvas, labels built from `NaN`, and canvases that recorded no calls at
   all — the geometry bugs a screenshot hides and the eye forgives; (iii) open the file in the desktop
   preview pane and **read** it: the JS-populated readouts (values the script writes into the page
   after load) are the proof the script ran to completion, since a throw leaves the static prose
   present and those numbers blank, and the pane puts the widget beside the user's chat where they
   will look first; (iv) a browser/pixel pass where one is available.
   **Where a screenshot IS available, split the two jobs instead of trusting one.** Loading a
   capture of the page and inspecting it catches appearance and meaning that no probe asks about:
   wrong or missing glyphs, broken typesetting, unreadable colour, a label sitting on the element it
   annotates. It will also state *geometry* — extents, centring, symmetry, alignment — confidently
   and wrongly, and a plausible-sounding measurement is the most dangerous output in the whole loop
   because it reads like evidence. So: **vision for appearance and meaning; pixel measurement for
   geometry.** The same split governs any rendered figure you hand over, including a video still.
   **Capture full-page, and copy each shot to its own filename.** Set
   `cdp('Emulation.setDeviceMetricsOverride', width=…, height=<full page height>, …)` before
   shooting: a viewport-height capture makes a reviewer report a clipped title and a missing trace
   that are artefacts of the crop. And copy each capture away immediately, because the screenshot
   helper reuses one path — capturing the next tab silently overwrites the previous one.

## Pitfalls

- **Blank canvas = silent failure.** Always assert non-zero pixels on each canvas via
  `browser_exec` before presenting; a math/axis bug shows up as empty, not as an error.
- **A duplicate `id` kills the entire script silently.** `getElementById` returns the first match in
  document order, so a canvas and a readout `<span>` sharing an id hand back the span and the first
  `getContext` call throws — leaving the page's HTML rendered and nothing else, which reads as "the
  title loaded, no error, no widget". Prefix canvas ids away from the value elements they feed
  (`clrplot` vs the `clr` readout span). The same total failure comes from a parse error — most often in
  a hand-built widget, a helper name reused later in the same IIFE — and a missing probe hook
  (`window.__w === undefined`) is the tell that it is a parse error rather than a draw bug, since a
  draw bug still leaves the hook defined. Do this BEFORE the first browser load — it costs a second, a failed load costs a whole
   round-trip. Diagnose cheapest-first: extract the `<script>` body to a
   file and `node --check` it to rule out a parse error, then re-evaluate that body inside a try/catch
  in the page to surface the real throw —
  `js("(function(){try{" + code + ";return 'OK'}catch(e){return 'ERR '+e.message+' @@ '+e.stack}})()")`
  — which turns "nothing works" into a file:line in one expression.
- **A class you emit but never define renders as unstyled run-on text.** A generated
  `<div class="grid3">` while only `.grid4` exists in the stylesheet loses its columns and
  brackets: the matrix becomes one wrapped line of numbers, which reads as a formatting
  accident rather than a bug, and no count or DOM assertion notices — element counts, text
  content and zero errors all pass. Every class name that appears in a template literal must
  have a rule; grep the classes you emit against the `<style>` block, or just expect the
  rendered-pixel pass ("is the 3x3 a bracketed grid?") to be the only thing that catches it.
- **A probe setter must write back to the controls, not only to the model.** A `set({a:30})`
  that updates state without moving the slider and its value label leaves the UI reading the
  previous value, so the next state you set appears to contradict what the panel shows (a
  "GIMBAL LOCK" banner under a slider still reading 60°). Someone reading the screenshot then
  reports a widget bug that does not exist. Treat the setter as a user-equivalent action: state,
  input value, and every derived label in one function — which is also what makes a screenshot
  trustworthy as supporting evidence. **And keep the HTML defaults in step with the model
  defaults** — the first paint reads the model, so a slider (or its value label) left at its old
  `value=` attribute shows a state the widget never ran, before any `set()` is called.
- **An axis range is data, not a constant.** Derive each panel's limits from every series it will
  draw (min/max over the whole payload, padded, snapped to a readable step), never from a hand-picked
  range that fits the first dataset you opened: a hardcoded y-range silently clips the series that
  moves furthest, and the clipped curve still renders, still logs nothing, and reads to the user as a
  bug in their own data. Compute the limits per panel from the payload and let the harness assert that
  every canvas's recorded extents fall inside its box.
- **Don't size a canvas off a hidden tab's DOM rect** — it's 0 and you get a blank
  artboard. Use fixed attributes + CSS scaling.
- **Every color must come from a theme var**; a hardcoded dark fill reads invisible on the
  dark frame. **And make the `var()` fallbacks scheme-aware** — the user also opens these files
  standalone in their own browser, not only in the chat frame, so a dark-only fallback palette
  renders near-white text on their white page *while the text inside the cards still looks fine*.
  That asymmetry is the tell, and it was reported 2026-09-18. **Alias the app's vars; never
  redeclare them.** Declaring `--foreground` / `--accent` / `--border` / `--card` yourself breaks two
  things at once, both silently: your `<style>` is injected AFTER the frame's and `:root` ties on
  specificity, so your hardcoded fallback *replaces the app's live theme* (a light palette kills a
  dark frame); and the frame-absent test reads exactly that variable, so defining it yourself makes
  `standalone` never apply. Declare prefixed aliases instead, app var first with the fallback inside
  the `var()` — `--w-fg: var(--foreground, #1b1b1f);` — repeating the block under
  `@media (prefers-color-scheme: dark)` to swap the *fallback* values, plus your own set for colours
  the frame does not supply (`--w-alert`, `--w-ok`). Paint the page from
  `body.standalone{background:var(--w-card);color:var(--w-fg)}`, the class added only when
  `getComputedStyle(document.documentElement).getPropertyValue('--foreground').trim() === ''`.
  Also drop `font-family` from your `:root` — same trap, the frame injects the app font.
  **Choose the extra colours from the FRAME's own text luminance, not the OS media query** — a dark
  app on a light OS is routine, and the media query picks the wrong palette for it. Verify contrast
  numerically on BOTH schemes by emulating each with
  `cdp('Emulation.setEmulatedMedia', features=[{'name':'prefers-color-scheme','value':scheme}])`
  before each reload — assert the computed colour and its ratio against the *painted* background,
  not merely that something rendered. Then prove the framed path wins by setting `--foreground` via
  JS and confirming the extra colours flip against the OS scheme.
- **A vision read is not authoritative for colour either.** Reviewing a rendered flowchart, one model
  listed the legend swatches and their hues in the right ORDER but named the colours wrongly (teal for
  the blue section, purple for the teal one) and described a box's blue stroke as "yellow/gold". Assert
  palette correctness by comparing computed colours (`getComputedStyle(...).backgroundColor` of the
  legend swatch vs the tick vs the node's `borderLeftColor`) and by counting pixels in the screenshot —
  vision is for layout, meaning and what looks broken, not for "which colour is this".
- **A vision read is not authoritative for glyphs.** One screenshot review confidently reported a
  label's `R₁` subscript as `R₂`; sub/superscripts and other single-character differences are exactly
  where it fails. Assert every label string through `textContent` in the probe, and never "fix" code
  from a screenshot — vision judges layout and readability, `textContent` says what the label is.
  The same split runs the other way: never reword a label *because* the capture looked odd.
- **Never put your expected value inside the vision prompt.** Asking "do the components read
  `3, 1, 0` and `−3.5, 0, 0`?" produced a confident "no — the matrix shows `0, 3, 1`", i.e. the model
  graded the wrong number you supplied, correctly contradicted it, and reported a defect that did not
  exist. Ask open-ended ("what are the two arrow labels and the two translation columns?") and do the
  comparison yourself against the probe; a leading question converts the reviewer into an echo.
- Present with `::preview{file="absolute/path"}` alone on its own line; a relative or
  unqualified path won't render.
- **A slider must control the same scalar the readout and the source quote — derive it; do not assume
  the slider value IS the norm.** A perturbation built as `t·(cos θ, sin θ)` has ∞-norm `0.707·t` at 45°
  and 135°, so a widget claiming to reproduce the source's `‖δb‖∞ = 0.01` printed `14.135` where the
  worked example says `19.99`. Normalise the direction by `max(|cos θ|, |sin θ|)` for an ∞-norm display
  (and by nothing for the 2-norm), then re-read every readout against the source's own numbers.
- **When the widget illustrates a chain, give every line of the chain its own live row.** Showing only
  the final inequality hides which step moves. A table of rows — `‖δx‖ ≤ ‖A⁻¹‖‖δb‖`, `1/‖x‖ ≤ ‖A‖/‖b‖`,
  their product — each with both sides evaluated at the current state, lets the reader watch the `≤` hold
  and see which line is loose. Pair it with a button that drives the state to the source's own worst
  case, so the tightness of the bound is a number read off rather than a claim.
- **Verify a widget's NUMBERS against an independent computation, at several control positions.**
  Recompute the model in numpy at three settings — the source's own printed example, the extreme the
  widget calls worst, and a harmless one — and assert the invariant the widget teaches (a quantity
  constant in one slider; a maximum attained at the named direction). Readouts that render correctly
  prove nothing about the arithmetic: the ∞-norm slider bug above passed every DOM, count and range check.
- **Assert the initial state, not just that something drew.** Zero errors plus painted pixels
  still lets a widget open in a state that contradicts what it teaches; check the premise
  (free vs colliding, valid vs invalid) through the probe hook before presenting it.
- **Let the user drive the object in every representation it has.** When the widget exists to
  show that two views are one thing (joint space ↔ Cartesian, time ↔ frequency), make each
  panel draggable back into the model — dragging the *dot* and watching the arm obey is what
  makes the correspondence land. A read-only second panel is a missed teaching beat.
- **Measure a rendered figure's geometry; never accept a model's bounding-box claim.** Classify each
  pixel to the *nearest palette colour* and print, per colour, the row bands and x-extents. Prefer
  nearest-colour assignment over loose channel thresholds — a `G>140, R<160, B<150` mask silently
  catches light grey text and inflates one label's extent from ~330px to ~630px, which then reads as
  a collision that is not there. A vision model reported a centred, near-full-width divider as
  "right-shifted, x 490→830"; measurement showed x 66→787 of 854, correctly centred.
- **Two labels sharing a row band with overlapping x-extents read as ONE sentence, even when the
  glyphs never touch.** No overlap test catches this and a quick eyeball usually misses it. Worse,
  each nudge of one label can land it on a third element (a caption, a marker dot), so moving it once
  is not the fix: relocate one out of the band, then **re-measure until the bands are disjoint**. The
  tell that a model has merged two labels is that it recites them as a single continuous string.
  Antialiased edges misclassify, so trust a band only when its pixel count is well above the fringe.
- **Bounding-box overlap is not visual collision**, and the converse holds too: coloured extents can
  intersect on both axes while the glyphs never touch (a subscript's row band sitting beneath a line
  of text). Judge collision by looking; reserve the numeric check for extent, centring and symmetry.

- **Never put two different quantities on one y-axis, and never let the default state make two
  series coincide.** A gain and a variance that both happen to sit near 1 at the widget's default
  σ render as ONE curve, and a reviewer reports the missing series as a broken panel — the
  arithmetic was right, the default was wrong. Give each quantity its own panel, or plot the
  second against a normalised reference stroke (a wide dashed line drawn *under* the solid one) and
  pick opening parameters where the two visibly separate. Where two series are legitimately equal
  in one mode, say it in the title ("equal only when there is no prior") — otherwise the overlap
  reads as a rendering bug, not as the lesson.
- **Canvas text does not wrap: an over-long title is clipped in silence.** Measure before drawing
  (`ctx.measureText` against the plot width), push any offender into an array the probe hook
  exposes (`overflow()`), and assert that array is empty during verification. A tab title at the
  default 13.5px fits about 78 characters — past that, shorten the string rather than shrinking
  every font on the panel. A screenshot is how you confirm the result, not how you find this.
- **Round the ticks, and derive the label precision from the tick step.** `[lo, (lo+hi)/2, hi]`
  prints "arbitrary-looking" values (`0.0951 / 4.3426 / 8.5901`) and makes every panel read as
  noise. Snap to 1/2/5 × 10^k steps sized near (hi−lo)/3, and format each label from the step — one
  decimal at step ≥1, two in the tenths, three in the hundredths. Keep an explicit `0` (or whatever
  value the lesson turns on) in the set even when the nice-step walk skips it.

## Support files

- `scripts/canvas-page-check.js` — headless node harness for a generated widget: runs the page's own
  `<script>` against a recording canvas stub, drives `--set id=value` / `--call "expr"` / `--frames N`,
  and reports parse errors and throws, non-finite coordinates, labels containing `NaN`, draws outside a
  canvas, canvases with no calls, and a `--expect N` payload-count check.
- `references/control-theory-foundations.md` — the concept ladder + analogies for teaching
  time-optimal / chain-of-integrators control (what was actually taught this user).
- `references/widget-verification-probes.md` — the browser-verification recipe: probe-hook
  shape, error/ink assertions, canvas coordinate mapping, synthetic drag tests, pixel sampling,
  and (§7) tuning parameters you cannot see via an anchor-verified Node replica of the model,
  and (§9) checking a teaching widget's maths element-by-element against the source's own printed
  closed form — the convention check (which axis turns first, intrinsic vs extrinsic, ZYZ vs ZXZ).
- `templates/widget-scaffold.html` — a compact working canvas scaffold (alias-based theme block,
  standalone fallback, tabs, canvas DPR helper, animate loop, one plot, probe hook) to copy and
  extend.
- `templates/svg-widget-scaffold.html` — the SVG-first counterpart for geometric figures: theme alias
  block with hue-switching off the frame's text luminance, a row layout of figure + readout cards, a
  seg-button contrast toggle, the orthographic projection helper, and a probe hook carrying
  `project` / `drawnEnd` / `text` / `svgCounts`. Copy it when the widget draws frames, vectors or a
  diagram rather than a plot.
