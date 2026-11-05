# GSAP in a single-file page

GSAP is the heavy tool for when CSS and IntersectionObserver genuinely can't do it. Cadence:
**CSS transition → IntersectionObserver + transform → GSAP → Lenis → R3F.** Reach down the list
only when the rung above can't express the thing.

Since Webflow acquired GreenSock, **GSAP 3.13+ made every plugin free**, including commercial use
(SplitText, MorphSVG, DrawSVG, MotionPath, Draggable, Inertia, Flip). Licence is GSAP's own Standard
Licence — free to use, **not MIT**; don't repeat the MIT claim.

## Loading

Pinned local copies (no npm, no CDN, works from `file://`):
`_Knowledge/vendor/gsap/` — core + 10 plugins, all at the same version (plugins must match the
core). Lenis sits next to it in `_Knowledge/vendor/lenis/`.

**Paths below are relative to `vendor/`** — either copy the two or three files you need into the
project next to the page, or point back with a relative path to the vendor folder. Copying is
usually cleaner than reaching across folders. Order is not optional: **core → plugins →
`registerPlugin()` → animate.**

```html
<script src="gsap/gsap.min.js"></script>
<script src="gsap/ScrollTrigger.min.js"></script>
<script src="gsap/SplitText.min.js"></script>
<script>
  gsap.registerPlugin(ScrollTrigger, SplitText)   // before any animation code
</script>
```

For a multi-file project, `npm install gsap` and import the same plugin paths (`gsap/ScrollTrigger`).

## Registering plugins — and the false negative

`gsap.registerPlugin(...)` is **mandatory** whenever the plugin is imported as a module, because a
build tool's tree-shaking will drop an unregistered plugin. (Registering twice is harmless.) With
plain `<script>` tags GSAP tries to auto-register, but call it anyway so the same page works either
way.

**Checking whether a plugin is live:** `gsap.core.globals()` lists most of them — but **SplitText is
not listed in 3.13+ even when working**. Verified: `globals()` reported `SplitText:MISSING` while
`new SplitText('#head', {type:'chars,words'})` returned 24 chars from a 4-word heading. Verify
SplitText by **constructing it**, never by introspecting globals.

## The core API, in the order you'll need it

```js
// the four tweens — to (→ target), from (start at), fromTo (both), set (instant)
gsap.to('.card',  { y: 0,  opacity: 1, duration: 0.6, ease: 'power3.out', stagger: 0.08 })
gsap.from('.hero h1', { y: 32, opacity: 0, duration: 0.8 })
gsap.set('.list', { autoAlpha: 0 })            // autoAlpha = opacity + visibility

// a timeline is the reason to use GSAP: one playhead, sequenced, scrubable
const tl = gsap.timeline({ defaults: { duration: 0.5, ease: 'power2.out' }, paused: true })
tl.to('.step-1', { x: 40 }).to('.step-2', { x: 40 }, '-=0.2')   // overlap by 0.2 s
tl.progress(0.5)          // scrub to the middle — exact, and the pattern to verify with
```

**Verified scrub arithmetic** (so you can trust `progress()`): a tween from `x:180` to `x:50` read
back `gsap.getProperty('#dot','x') === 115` at `progress(0.5)` — exactly half way.

## ScrollTrigger

```js
ScrollTrigger.create({ trigger: '#section-2', start: 'top 80%', end: 'bottom 20%',
  toggleActions: 'play none none reverse' })

// scrubbed instead: progress follows the scrollbar
gsap.to('.parallax', { y: -120, ease: 'none',
  scrollTrigger: { trigger: '#section-2', start: 'top bottom', end: 'bottom top', scrub: true } })
```

- `markers: true` while building, delete before shipping.
- **Call `ScrollTrigger.refresh()`** after anything that changes layout height: fonts loading,
  images arriving, an accordion opening. ScrollTriggers computed before a web font swaps are wrong.
- `pin: true` uses a spacer element — check it doesn't fight a `position: sticky` parent.

## React (the R3F / widget case)

Animations live in an effect and **must be cleaned up**, or StrictMode's double-invoke fires them
twice and route changes leave orphans:

```jsx
useEffect(() => {
  const ctx = gsap.context(() => { gsap.from('.card', { y: 24, opacity: 0, stagger: 0.06 }) }, ref)
  return () => ctx.revert()          // ctx.revert() undoes the tweens AND the inline styles
}, [])
```

For SplitText, revert it too — you cannot re-split an already-split element:

```jsx
const st = new SplitText(el, { type: 'chars' })
// later: st.revert()
```

`useGSAP()` from `@gsap/react` is the packaged version of this; plain `gsap.context` is fine and
needs no extra dependency.

## Reduced motion — required, not optional

A page that animates on scroll must answer `prefers-reduced-motion`. GSAP's own helper expresses
both branches in one place:

```js
const mm = gsap.matchMedia()
mm.add({
  reduce: '(prefers-reduced-motion: reduce)',
  ok:     '(prefers-reduced-motion: no-preference)',
}, (ctx) => {
  const { reduce } = ctx.conditions
  if (reduce) gsap.set('.card', { clearProps: 'all' })      // land in the final state, no motion
  else        gsap.from('.card', { y: 24, opacity: 0, stagger: 0.06 })
})
```

`mm.revert()` on cleanup. Lenis already honours the same setting by itself.

## Lenis + ScrollTrigger (when both are in play)

Smooth scroll and scroll triggers must share one clock, or triggers fire against a stale position:

```js
const lenis = new Lenis({ autoRaf: true, anchors: true })
lenis.on('scroll', ScrollTrigger.update)
gsap.ticker.add((time) => lenis.raf(time * 1000))   // GSAP time is seconds, Lenis wants ms
gsap.ticker.lagSmoothing(0)                          // or scroll animations lag on a hitch
```

With `autoRaf: true` on Lenis, drop the `gsap.ticker.add` line and pick one rAF owner — running both
means the scroll is integrated twice per frame.

## SVG plugins

| Plugin | Use | Note |
|---|---|---|
| SplitText | chars/words/lines for typography | must `revert()` before re-splitting |
| DrawSVGPlugin | line-drawing effect | `gsap.set(path, { drawSVG: '0% 50%' })`; needs a real `stroke` |
| MotionPathPlugin | move along a path | writes a transform — verified |
| MorphSVGPlugin | morph between paths | mismatched point counts need `shapeIndex: 'auto'` |

These are the ones with a robotics-shaped use: a trajectory, a tool path or a cable route is a
path, so `MotionPath` or a scrubbed `DrawSVG` shows it being traced.

## Pitfalls

- **The static state must be the final state.** Never let a tween be the only thing that makes
  content visible. A bar chart whose bars were `transform: scaleX(0)` in CSS and revealed by
  `gsap.to(..., {scaleX: 1})` came out invisible under `prefers-reduced-motion`, because the tween
  is exactly what gets skipped. Default to the finished look in CSS and animate **from** the hidden
  state: `gsap.from('.bar', { scaleX: 0 })`. Same reason `from` tweens are the safe direction for
  text and diagrams — if the script dies, the content is still there.
- **Clamp `dt` from below, not just above.** `Math.min(dt, 0.05)` still lets a clock that goes
  briefly backwards produce a negative step, and an exponential filter then integrates the *wrong
  way*. Use `Math.max(0, Math.min(dt, 0.05))`. This silently inverted a lag until the numbers were
  compared against the closed form.
- **Animate `transform` and `opacity`, not layout.** Animating `top`/`width`/`height` re-lays-out the
  page every frame. `x`/`y`/`scale`/`rotation`/`autoAlpha` are the cheap ones.
- **Kill what you create.** `tl.kill()`, `ctx.revert()`, `ScrollTrigger.getAll().forEach(t => t.kill())`.
  Orphaned triggers keep firing after a section is gone.
- **Loading order in a single file:** core first. A plugin loading before the core attaches to
  nothing and fails silently.
- **Plugin/core version mismatch** breaks in confusing ways. Keep them from the same release.
- **Don't ship `markers: true`.**
- **Two smooth-scrollers at once** (Lenis + GSAP's ScrollSmoother) is a bug, not a feature. Pick one.

### With Lenis on the page

- **`window.scrollTo()` does not work.** Lenis owns the scroll position and snaps back to its own
  state on the next frame, so a programmatic jump silently does nothing — and in a headless capture
  it looks like a blank page rather than a failed scroll. Use `lenis.scrollTo(y, {immediate: true})`,
  and expose the instance (`window.__lenis = lenis`) so navs, deep links and checks can reach it.
- One rAF owner only: `autoRaf: true` on Lenis **or** `gsap.ticker.add(...)`, never both.
- `anchors: true` or in-page anchor links stop working.

## Verifying it actually ran

Headless, text-first — the same loop used elsewhere in this library:

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
"$CHROME" --headless=new --user-data-dir="$LOCALAPPDATA/Temp/gsap-check" \
  --virtual-time-budget=8000 --dump-dom "file:///C:/path/page.html" 2>&1 | grep -iE 'CONSOLE|id="report"'
```

Write a marker into the DOM from the page (a `#report` div is enough) and have it state:
`gsap.version`, whether each plugin resolved **by constructing it**, one `gsap.getProperty()` read
back at a known timeline `progress()`, and one `getComputedStyle` of something a plugin touched
(DrawSVG's `strokeDasharray`). Numbers that match hand-computed values are the proof; a page that
looks animated in one browser session is not.

Two habits that pay off:

- **Cross-check one plugin against the maths it replaces.** Placing a dot with `MotionPathPlugin`
  *and* computing the same point with `path.getPointAtLength(progress * totalLength)` gives two
  independent answers; when they agreed to `0.00px` the placement was proven. Same trick for a drawn
  quantity: the error segment read `288.73px`, and the chord formula `2R·sin(θ/2)` predicts
  `288.4px`.
- **A vision pass reads topology and layout reliably, and digits unreliably.** It caught a
  diagram drawn as a series compensator when the caption described a parallel feedforward
  structure — a real error — and separately misread `6.203`, `160.8` and `3.15.0` as other numbers.
  Fix what it says about *structure*; grep the file for anything it says about *values*.

A ready-made instance of exactly this: `_Knowledge/vendor/selftest.html`, and a full worked page at
`Projects/Web-Design-System/Deliverables/WebApps/scroll-story-demo/` (with its own `README.md`
recording what was verified and the numbers it produced).
