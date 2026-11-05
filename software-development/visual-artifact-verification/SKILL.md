---
name: visual-artifact-verification
description: "Verify a generated HTML/SVG artifact renders right, including multi-screen flows and animation."
---

# Verifying generated visual artifacts

**Trigger:** any session that produced a visual deliverable — a diagram, chart,
widget, mockup, poster, or report page — or any time the user reports that such
an artifact looks wrong.

## Why this exists

Generated markup fails in ways static review cannot catch: a label sitting on
the line it annotates, two connectors entering the same box edge and reading as
one merged arrow, an accent colour used four times where two were intended, text
spilling its box, a panel border cutting through the frame. Your own arithmetic
is usually right — the failure is in what the renderer does with it. Render it
and look at it before you hand it over.

## Procedure

1. **Render.** Open the file in the browser, wait for load, then sleep ~3s: web
   fonts arrive late and shift every metric you computed.
2. **Capture the whole page, not the viewport.** A viewport screenshot cuts the
   frame and produces false defects ("the bottom band is missing", "this line is
   unterminated"). Use a full-page capture:
   ```python
   js("window.scrollTo(0,0)")
   import base64, os
   res = cdp('Page.captureScreenshot', format='png', captureBeyondViewport=True)
   p = os.path.join(os.environ['BH_AGENT_WORKSPACE'], 'full.png')
   open(p, 'wb').write(base64.b64decode(res['data']))
   ```
   If that capture times out, get the same page a different way: enlarge the emulated
   viewport (`cdp('Emulation.setDeviceMetricsOverride', width=880, height=1000,
   deviceScaleFactor=2, mobile=False)`) and capture the viewport with `capture_screenshot()`.
   Same full page in one call, and the 2x device scale makes the step-6 region crops sharp
   enough to read small labels without a separate zoom step.

   **Clipping the capture to the single element you care about beats mapping regions afterwards.**
   When the deliverable is one figure inside a page, ask the DOM for its box and hand that to the
   capture as a `clip`: no scroll/`devicePixelRatio` mapping in step 6, and `scale` supersamples the
   crop in the renderer.
   ```python
   r = js("(() => {const b = document.querySelector('figure svg').getBoundingClientRect(); return JSON.stringify({x: b.left + window.scrollX, y: b.top + window.scrollY, w: b.width, h: b.height});})()")
   d = json.loads(r)
   res = cdp('Page.captureScreenshot', format='png', captureBeyondViewport=True,
             clip={'x': d['x'], 'y': d['y'], 'width': d['w'], 'height': d['h'], 'scale': 1.6})
   ```
   The `clip` is in **page** coordinates, not viewport ones: without adding `window.scrollX/scrollY`
   a scrolled page crops a band of empty canvas, and the "clean" verdict is then about pixels nobody
   looked at. `captureBeyondViewport=True` is what lets the clip reach below the fold. Check the PNG's
   size before reading it — the blank-capture rule below applies to clips too.

   When the browser session itself is
   gone (endpoint lock, daemon restart), take the same pixels with headless Chrome from the
   terminal — same file, real renderer, no session:
   ```bash
   "/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new --disable-gpu \
     --hide-scrollbars --force-device-scale-factor=2 --window-size=1100,1300 \
     --virtual-time-budget=8000 --user-data-dir="$LOCALAPPDATA/Temp/chrome-shot" \
     --screenshot="$LOCALAPPDATA/Temp/shot.png" "file:///C:/path/to/artifact.html"
   ```
   Pass native forward-slash paths to native Chrome, and check the PNG's size before believing it
   (a few KB is a blank frame). Capture at 1× is not enough for labels under ~10px: build a temp
   wrapper that inlines the artifact's own `<style>` block and its `<svg>`, sets the svg width to
   S× its original, and clips to the region of interest with `overflow:hidden` on a container plus
   negative `left:`/`top:` offsets. Same markup, same CSS, so the glyphs are faithful — at 2× a 7px
   chip label renders at 14px and `vision_analyze` reads it, where the shipped-size page does not.
   This is also the right render path for one artifact the chat surface never shows at all.

   **A self-contained page carrying tens of MB of embedded base64 media breaks capture.**
   With ~18 inlined `<video>` elements the compositor is slow enough that
   `Page.captureScreenshot` either times out on the IPC or *succeeds with a uniform blank
   frame* — a ~9 KB file for a text-dense region (any text region should be >40 KB at q70),
   including when a `clip` is passed with `captureBeyondViewport=False`. Treat a tiny file
   as "no pixels", not as "the page is black": check `dst.stat().st_size` before believing a
   capture, retry once after the page has painted (`document.readyState === 'complete'` and
   a non-trivial `document.body.innerText.length` are necessary but **not** sufficient — the
   paint can still lag a 29 MB parse), then fall back to the DOM assertions below instead of
   burning calls on the screenshot. Say plainly in the report which check ran and which did not.
3. **Qualitative pass.** Load the image with `vision_analyze` and ask the defect
   questions in one call, not six: does any label touch or overlap its
   connector; do any two connectors overlap or share a path; does any connector
   cross a box that is not its endpoint; is the accent colour on more than two
   elements; does any text overflow or collide; does anything look broken.
   On a tall diagram, send **three or four region crops instead of the whole page** — the
   equation/box band, the label band, the accent rail, the legend — as separate calls batched
   together: a whole-page image of a 900px-tall figure is the call that times out, while each
   crop returns in seconds and is sharp enough to read 9px mono equations in.
4. **Fix in the file** with targeted patches — never by redrawing the whole
   artifact, and never by moving a label to a spot you have not re-checked.
5. **Quantitative pass.** Verify counts and coordinates yourself; the image is
   not evidence of a number. A number *written into a label* — "three inversions", "N = 20", a
   percentage — is a claim of the same kind: re-derive it from the source it came from before delivery,
   because a wrong count in prose passes every geometry, DOM and pixel check. Accent budget: count occurrences in the file
   (`grep -c '#<accent-hex>'`) and subtract the legend key and any CSS custom
   property. Geometry: ask the DOM.
 ```python
 js("[...document.querySelectorAll('text')].map(e => [e.textContent, Math.round(e.getBoundingClientRect().left), Math.round(e.getBoundingClientRect().top)])")
 ```
 Contrast: compute WCAG relative luminance in code and quote the ratio; never
 assert "it looks fine". Text over a translucent or glass surface must be
 measured against the composite that is really behind the glyphs, not against
 the palette: hide the text, capture, sample inside each text block's
 `getBoundingClientRect()`, and take the lightest pixel as the worst case.
 Re-derive it whenever the background animates or the layer changes — a ratio
 measured against a flat palette does not carry over to glass. Full recipe
 (hiding the text, sampling, and the ramp probe that proves a surface is
 translucent at all): `references/measuring-glass-contrast.md`. A runnable evaluator for a
  directory of captures (JSON + one screenshot per animation phase): `scripts/contrast_pass.py`.
**Geometry probe on a generated SVG — classify before you report.** Ask the SVG in user units, not
client rects, or a scaled canvas silently turns every measurement into a fraction of itself:

```python
js("""(() => { const svg = document.querySelector('svg'); const box = svg.viewBox.baseVal;
  const out = { viewBox: [box.width, box.height], labelMismatch: [], right: 0, bottom: 0 };
  for (const t of svg.querySelectorAll('text')) {
    const b = t.getBBox();
    out.right = Math.max(out.right, b.x + b.width);
    out.bottom = Math.max(out.bottom, b.y + b.height);
    const m = t.previousElementSibling;                     // its mask rect, if any
    if (m && m.tagName === 'rect' && +m.getAttribute('height') < 20)
      out.labelMismatch.push([t.textContent, Math.round(b.width), +m.getAttribute('width')]);
  }
  return JSON.stringify(out); })()""")
```

Classify every entry before writing one sentence about defects, because a generated diagram's
coordinate list is *mostly by design*: a legend swatch and a role/tag chip sit under their own text
on purpose, so "a rect overlaps this text" is not a finding. Only two results are findings — label
text **wider than its own mask** (it will spill across the stroke) and content **outside the
viewBox** (clipped on delivery). Reporting the raw count as "N issues" is how a clean artifact gets
patched into a broken one.

**A hand-coded rounded elbow must consume its own straight runs.** At a 90° turn the arc radius
comes out of *both* adjacent segments; start the curve at the corner and one arm goes
negative-length and inverts, so the connector doubles back along itself. Put the arc's tangent
points `r` either side of the corner, shorten both straights by `r`, and confirm every connector's
first and last path points sit **on** a node edge (compare against the node rects) rather than near
one — several connectors entering the same edge also read as one merged arrow.

6. **Zoom-verify what you changed.** Map source coordinates to screenshot
   pixels at capture time — the factor depends on rendered width, scroll and
   `devicePixelRatio`, so compute it, never hardcode it:
   ```python
   js("""(() => { const r = document.querySelector('svg').getBoundingClientRect();
     const dpr = window.devicePixelRatio || 1, f = r.width / VIEWBOX_W;
     const map = (x1,y1,x2,y2) => [Math.round((r.left+x1*f)*dpr), Math.round((r.top+y1*f)*dpr),
                                  Math.round((r.left+x2*f)*dpr), Math.round((r.top+y2*f)*dpr)];
     return JSON.stringify(map(SRC_X1,SRC_Y1,SRC_X2,SRC_Y2)); })()""")
   ```
   Feed that array straight into `vision_analyze(image_url=..., region=[...])`.
7. **Run the generating skill's own checker** if it ships one (the diagram skill
   has `scripts/self_check.py`). If a checker exists only in a repo checkout
   while you have an installed skill, run what you have and say plainly which
   check you could not run — do not imply you ran it.
8. **Deliver** once the second pass is clean: the absolute path in prose, plus
   the host's inline preview directive when it has one.

## Interactive and multi-screen artifacts

**Trigger:** the artifact has more than one state — screens, tabs, a wizard, a
slider, a modal, a form with a gated control.

A screenshot of the first screen proves the first screen. When the deliverable is
a flow, the flow is what gets verified: walk it from the start to the end state
with real clicks and assert every transition.

1. **Open it the way the user will.** `file:///C:/...` when they will
double-click it, not a dev server — a server hides the offline, relative-path and
CORS failures that only show up on the real delivery path.
2. **Drive it with real DOM clicks inside `js()`.** `el.click()` dispatches a
bubbling event, so delegated handlers, focus moves and state changes run exactly
as they do for a mouse. (Scope every lookup to the visible view — see the
label-matching pitfall below; this is the mistake that makes a walkthrough
confidently wrong.)
3. **Assert each step, don't admire it.** Build a list of `(action, expected
state)` pairs and print `ok`/`FAIL` per step. A wall of screenshots hides the one
transition that silently did nothing — including the case where Back works on
nine screens and quietly misroutes on the tenth.
4. **Reload between independent scenarios** (`goto_url`). App state lives for the
life of the page, so scenario two inherits scenario one's leftovers and the FAIL
it reports is fiction.
5. **Reach a state by walking the flow, never by forcing it** — see the pitfall
below.
6. **Check the viewports the user named** with
`cdp('Emulation.setDeviceMetricsOverride', width=..., height=..., deviceScaleFactor=2, mobile=...)`,
and check for real overflow by comparing
`document.documentElement.scrollWidth` with `clientWidth` — a screenshot can look
perfect while the page scrolls sideways.
7. **Test the edges of the flow, not just the middle:** the start screen's back
control (holds still rather than erroring), and every gated control (its disabled
state, then its enabled state once the gate is satisfied).
8. **When offline is a requirement, grep for it and quote the result:**
`grep -n -E "https?://|src=|href=|url\("` over the shipped file.

### When the flow crosses files

**Trigger:** the deliverable is a set of pages read as zoom levels — a map whose numbered anchors
each open their own detail page.

- **Each anchor is a real `<a href="sibling.html">`**, not a chat-only click handler, so the set
  opens from `file://` in any browser; enlarge the target with a transparent hit rect over the small
  chip and name the destination in a `<title>`.
- **Every anchor resolves to a file that exists.** When a detail page is not built yet, ship a
  placeholder stating what it will cover: a chip that leads nowhere or dies reads as a bug, and the
  placeholder is the build spec for the next zoom. Give the placeholder the child's **final filename**,
  so building the real page later is a drop-in replacement and no parent or sibling link is re-pointed.
- **Give the child a way back** (its own top-left chip plus any re-enter link) and assert the return
  in the walkthrough. Arrival alone is not the assertion — the round trip is.
- **Rebuild whole elements when patching SVG in code.** A run-level regex that matches a `<text>`
  opening tag and replaces through its close drops the element's inner text and ships an empty chip
  label — invisible in review, obvious in a pixel read.
- **Pixel-read the smallest text on the page**, which is the anchor chips. A DOM assertion proves the
  string exists, not that it renders.

Recipe, markup and the four-pass list: `references/linked-artifact-sets.md`.

### When the artifact moves

**Trigger:** any animation, transition, drag, or timed state change. Movement fails
differently from layout, and it fails quietly.

- **Assert geometry at known moments, not presence.** A tween that never ran looks
  identical to one that did if you only look at the page. Read
  `getBoundingClientRect()` right after the trigger and again once it should have
  settled: an element that expands out of another must *start* on the source's box
  (within ~50 ms) and *finish* on its own, and a dragged row must come to rest on an
  exact multiple of its own pitch. Early / middle / rest is enough to prove a flight
  really happened.
- **Re-run the whole flow with the motion preference on.** Emulate it with
  `cdp('Emulation.setEmulatedMedia', features=[{"name": "prefers-reduced-motion", "value": "reduce"}])`,
  then walk every step again and assert the *static* state of each effect: no
  scroll-linked movement, no drag inertia, no pointer-follow, an instant swap instead
  of a flight. A branch that was never run is not a branch that works.
- **Count the nodes the design intends, not the nodes you find.** A carousel that
  duplicates its set to wrap seamlessly doubles every `querySelectorAll('.card')`
  answer (8 where the design has 4), so a count assertion starts passing or failing
  for the wrong reason. Scope to the originals (`:not(.is-clone)` or the real rows),
  and check the duplicates separately for what only an original should carry:
  listeners, focusability, `aria-current`.
- **Keep each scripted step short and wait between steps.** Do the sleeping in the
  calling language rather than inside one long `js()` — a single evaluate that sleeps
  for several seconds is cut off, and the timeout arrives looking like a page failure
  instead of a harness limit.
- **Check the layout does not shift mid-transition.** Read one anchored element's box
  (or a fixed layer's width) at rest, during the transition and after it. A document
  that grows taller for a moment can summon a scrollbar and shove the whole page
  sideways, and no screenshot of the settled state shows it.

`references/motion-assertions.md` is the per-mechanism table for this section: what each plugin and
CSS transition fails at *silently* (Flip's id matching, the InertiaPlugin vars shape, a Draggable
throw running past its wrap, delay tokens surviving a reduced-motion rule) and the exact assertion
that catches each one.

`templates/flow-walkthrough.js` is a ready harness for steps 2, 3, 4 and 6 —
copy it into the `js()` call and edit its step list.

### When the artifact moves a model, not just a control

**Trigger:** a click or drag turns, opens or moves a drawn model inside an axonometric or
perspective projection, and the requirement names a **direction** ("it rotates the way I drag",
"clockwise seen from the top of z").

- **Assert the sense, not just that the value moved.** "The yaw changed by 25°" passes while the
  model spins backwards. Fix the expected sign before running and print it beside the measurement.
- **Read the driven value from the artifact's own readout** — a printed angle, a `data-` attribute,
  an `aria-live` string. No pixel diff or visual impression settles a direction, and your own sign
  convention is not evidence.
- **Never fix an inverted drag by moving the camera.** The drawn sense of a positive rotation is
  invariant under an azimuth swing (the swing rotates the image in-plane, and a plane's projection
  preserves orientation), so a camera change cannot correct it — but it *does* swap which side of the
  model faces the viewer, turning a correct drag into one that looks wrong.
- **Check which face the viewer sees, and say it in words.** A one-sided projection can draw the
  model's back with its front hidden and nothing in the DOM reports it: read a part you know is the
  far side against the drawn ground anchors and state it as "the hinge projects up-page, so the
  keyboard is away and the leading edge is nearest — front, not back."
- **Fix the model's home orientation, not the view.** A rigid half-turn about z at the model's
  mounting level keeps the world frame and axis layout as the generator draws them, and leaves the
  drag's sense alone.
- **Author the resting state.** If the generator bakes values into the shipped data *and* the page
  syncs or plays a demo on load, the artifact animates itself before the first input; assert the
  post-load state before dispatching anything, and keep it separate from the toggle assertions.
- **Re-run the generator before reporting a patch series as landed** — a build script referencing a
  constant that was never defined throws on the next build, and a half-applied series reads as
  finished.

Anchor geometry, the cross-product ground truth, the far-side test and a headless Chrome + CDP
behaviour harness: `references/interaction-sense.md`.

## When the change is a dial, not a defect

A request for a *direction* — "more foggy", "warmer", "less busy", "smoother",
"less ball-like" — is not a bug report, so there is no fault to find and no single
correct output. The failure mode is overshooting into the opposite fault and calling it
done because the number moved. Run it as a measurement loop:

1. **Turn the adjective into 2-4 proxies before editing anything.** "Ball-like" becomes a
   feature count, the share of features that are round, edge energy at the feature scale, and
   one large-scale contrast measure so that *flat* is detectable in the same run. Choosing the
   proxies first is what stops the metric being fitted to whatever you happened to change.
2. **A/B on a deterministic artifact, never on two screenshots.** Give the generator an explicit
   `seed` parameter and build both versions at the same seed and size, then diff the numbers.
   Screenshots differ by animation phase, cursor position and elapsed time, so comparing them
   numerically measures noise. Keep the full-page shots for the human and the numbers for the
   decision.
3. **Read every proxy, including the ones you are not trying to move.** Flattening a shape can
   cut roundness *and* raise edge energy at the same time — with one metric you ship a
   regression as a success.
4. **Absolute thresholds, never a fraction of the amplitude you are measuring.** A test like
   "5 % above the local mean" shrinks along with the thing it counts and reports improvement
   for free. This is the specific way a metric lies; express thresholds in absolute units.
5. **Count both polarities.** Features *below* the background are as much of the structure as
   the bright ones; a bright-only counter sees half the artifact and can read "0" while the
   field is still visibly there.
6. **Restore volume, not edges.** Softening removes the sense of depth along with the fault, so
   bring the large-scale range back with one broad gradient (or a wider light, a lower alpha) —
   a single smooth ramp cannot read as a shape, which is why it is the safe way to add contrast.
7. **Re-run the contrast pass** — the change invalidates any earlier pixel pass by definition.
8. **Report the axis, not a verdict**, and name the one dial back: "no balls left, but it is at
   the far end of foggy — the single number to come back is X."

## Pitfalls

- **A probe that returns nothing is not a probe that passed.** An empty or truncated tool result tells you
the call ran, not that the artifact renders — re-run it printing one compact line (the assertion booleans,
the element counts, the extents) and only then report the artifact as verified. Same family as the
blank-capture rule in step 2: a bad result and a *missing* result both get stated plainly in the report,
never quietly upgraded into a pass.
- **A page carrying math fails silently when the renderer never loads.** KaTeX (or MathJax) pulled from a
CDN leaves the raw `$$…$$` sitting on screen, which reads as deliberate typesetting rather than a fault,
and every DOM, count and pixel assertion still passes. Verify by count *and* by absence: the number of
`.katex` nodes equals the number of display blocks you wrote, and `document.body.innerText` contains no
literal `$$`. Keep the numbers in plain HTML (a constants table, plain-text readouts) so the page still
reads when the CDN is slow, blocked, or the file is opened offline.
- **Narrow the re-verification to what you actually changed.** Before re-running an expensive
  pass, list the functions you edited and the states they feed; anything fed by untouched code
  is byte-identical and keeps its earlier numbers. Say which states you re-measured and which
  you did not — implying a screen was re-checked when it wasn't is the whole risk.
- **A leftover harness may be the evaluator only.** A capture/evaluate split has two halves; if
  the capture code is gone, the sample points were derived at capture time and are not
  reversible from the screenshots and JSON. Do not reverse-engineer the old point math — write a
  fresh capture pass from the recipe, which is faster than guessing and gives you a method you
  can state out loud.
- **Forcing a view visible to inspect it shows you stale content.** Toggling
  `hidden`/classes from the console bypasses the code that renders on entry, so
  what you screenshot is state the artifact would have rebuilt on arrival — and
  you then report (or worse, "fix") something the user will never see. Walk the
  flow, or reload and jump through the real controls.
- **A helper that matches controls by label hits views that are not on screen.**
  A document-wide `querySelectorAll('button')` returns the controls of every
  hidden view too, so "click Back" can exercise a different view's Back and
  produce a walkthrough that is confidently wrong in a way that reads as an app
  bug. Match inside the currently visible view only.
- **A disabled control is usually the correct state, not a defect.** Where the
  artifact refuses to act until real data exists (no URL supplied, no record
  selected), disabled is the requirement being met. Verify it is disabled *and*
  labelled, verify the gate switches it on when satisfied, and never "fix" it by
  enabling it or by shipping a placeholder value in its place.
- **Anything measured on an element that is not laid out is a zero, silently.**
  `getBoundingClientRect()` returns zeros for a `display: none` element, so geometry
  read from — or written into a width variable for — an element that has not been
  shown yet collapses the layout with nothing thrown. Show the element, force layout,
  then measure, and treat any zero-sized box as "not shown yet" rather than as a real
  measurement.
- **Glyph coverage cannot be proved with `measureText` in CJK text.** Comparing each
  character's advance width against the `U+FFFF` notdef width flags every capital `A`
  (its advance happens to equal the notdef box) and clears the CJK you actually care
  about, because every CJK glyph is exactly `1em` wide by design — a real tofu box
  measures the same as a real glyph. Test coverage by codepoint instead: every character
  in `U+4E00–U+9FFF` is covered by the platform CJK fallback (the same font stack already
  rendering the rest of the document), so grep the new text for anything *outside* that
  range — Ext-A `U+3400–4DBF`, compatibility `U+F900–FAFF`, or anything non-BMP — and
  read those few glyphs in the render. Quote the count and the range in the report.
- **Write sub/superscripts as `<tspan dy>` shifts, never as Unicode super/subscript characters.**
  Geist/Consolas-class faces do not reliably carry `⁻`, `ᵀ` or `S⁻¹`, and a missing glyph is a
  tofu box in a figure whose whole point is legibility. The pattern: `x̂<tspan dy="-3.5"
  font-size="6.8">−</tspan><tspan dy="3.5">&#160;= A x̂</tspan>` — the negative `dy` raises the mark
  and the matching positive `dy` puts the remainder back on the baseline. **Begin every
  continuation tspan with `&#160;` (NBSP)**: SVG collapses a leading space at a tspan boundary, so
  the plain space vanishes and the equation prints `x̂⁻= A`. A combining circumflex (`x` + `U+0302`)
  is the one diacritic worth trusting — it sits over the letter and held up in a pixel read on the
  fallback stack, which is also how you prove a band survives a webfont that never loads. Where a
  symbol is glyph-risky (a Greek gate threshold, `≤ γ`), spell it out in words inside the figure and
  keep the maths in the prose: a diagram that needs a maths font to be readable is broken on the
  machine that has none.
- **When pixels are unavailable, assert layout from the DOM and name the limitation.**
  Per table cell, `cell.scrollWidth > cell.clientWidth` finds text that is clipped or
  ellipsised; `document.documentElement.scrollWidth - clientWidth` finds sideways scroll;
  `row.cells.length` per row finds a merged or dropped column; compare the counts in the
  two language builds (rows, `ol > li`, `ul > li`) to catch a section added to one template
  and not the other. This is weaker than a render pass — a DOM check cannot see a glyph that
  renders as a box or a table that paints over a video — so report it as a DOM-level check.
- **A `<canvas>` has no DOM geometry to assert at all** — the element box says nothing about what was
  painted, so text drawn off the canvas, an axis that does not span its data and a typo'd coordinate all
  pass every DOM check. Drive the page's own draw code through a stubbed 2D context in Node and
  bounds-check each recorded primitive, plus its plotted numbers against the source data:
  `references/canvas-draw-assertions.md`.
- **Vision is qualitative, not quantitative.** It will overcount accent
  elements (a tinted node fill plus that node's own label read as two) and
  misjudge whether an arrowhead is centred on an edge. Confirm counts from the
  file and coordinates from the DOM; use vision for "does this look broken".
  It also sees a *downscaled* crop, so smooth low-contrast texture comes back as
  "flat and featureless" whatever structure is really there — vision cannot
  arbitrate a softness, density, or "is this still the same look" question, and
  its wording must never be quoted as the result.
  **Text it reports that you never authored is unverified until you grep the file for the string:** an
  invented line arrives as a plausible label carrying a real company name or term of art, so the file
  is the only authority on what the page says. Likewise, a capture that the fold cuts mid-box is a
  crop, not clipped content — treat "text runs off the bottom" from a partial capture as a harness
  artifact and re-read the file or the DOM before changing anything.
- **A missing arrowhead is not a defect when the element is a path's origin.**
  Arrowheads sit at destinations. Check the path direction before patching, or
  you will "fix" a correct connector into a wrong one.
- **Move a label and its mask rect together — and re-derive the mask from its connector, not from the
  label.** After content shifts, a mask left at its old coordinates prints a solid paper pill over empty
  canvas or swallows a neighbour, and every text assertion still passes because the label's own string
  and width are unchanged: the mask must clear *its own* connector's stroke by 6–10px and sit inside no
  later-painted node after the move, not before it.
- **Label-to-line clearance must be visible, not merely non-overlapping.** A
  mask rect stopping 2px from the stroke reads as a label sitting on the line at
  render scale; keep 6-10px and measure it in source coordinates.
- **Watch the render scale before trusting a crowded verdict.** The same file
  reads cramped in a 1x screenshot and clean full-size. Judge crowding on a
  region crop at full resolution, not on the downscaled whole-page image.
- **Fix in rounds.** Patch, re-render, re-inspect the changed regions; stop when
  a pass comes back clean rather than polishing by feel.
- **Nothing about a render survives a font change.** If text looks shifted or
  unspaced, check that the webfont actually loaded before touching geometry.

## Neighbouring skills

- `diagram-design` — generates the artifact and owns its type refs, style gate
  and complexity budget; this skill is the verification loop that runs after it.
- `dogfood` — exploratory QA of an app the user runs; this skill verifies a
  single artifact you just produced.
