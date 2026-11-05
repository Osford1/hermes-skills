# Asserting a canvas artifact from outside the browser

A `<canvas>` has no DOM geometry: `getBoundingClientRect()` returns the element's box, never a drawn
primitive, so text painted off the canvas, an axis that does not span its data and a label plotted at a
typo'd coordinate all pass every DOM check. Assert the draw calls instead — the page's own drawing code,
run against a recording stub, is the only thing that knows where the ink went.

## Harness

Node, no browser, no dependencies. Read the built HTML, pull its script block, and give it the smallest
environment its draw code touches.

```js
const fs = require('fs');
const html = fs.readFileSync(process.argv[2], 'utf8');
const data = JSON.parse(html.match(/const __DATA__ = (\{[\s\S]*?\});/)[1]);   // the page's own numbers

const hits = [];                      // ['pt', canvasId, x, y] / ['ext', canvasId, xs, ys]
function makeCtx(cv) {
  const A = {
    moveTo:  (x, y)      => hits.push(['pt', cv.id, x, y]),
    lineTo:  (x, y)      => hits.push(['pt', cv.id, x, y]),
    arc:     (x, y, r)   => hits.push(['ext', cv.id, [x, x + r, x - r], [y, y + r, y - r]]),
    fillRect:(x, y, w, h) => hits.push(['ext', cv.id, [x, x + w], [y, y + h]]),
    // ... only the methods this page actually calls
  };
  return new Proxy({}, { get: (_, k) => A[k] || (() => { throw new Error('unknown ctx.' + k); }) });
}
```

- **Whitelist arguments per method; never sweep every argument as a coordinate.** `arc`'s third argument
  is a radius, and `lineWidth`/`font` are not positions at all. Folding them into an x/y extent reports an
  overflow the page does not have, and chasing a false defect costs a round.
- **Make the stub throw on an unknown method.** A permissive no-op hides a renamed or typo'd context call,
  which is the exact bug a stub harness exists to catch.
- **Track bounds per canvas.** Compare each recorded point against that canvas's own `width`/`height`, not
  the page's, and allow a couple of pixels of slack: a stroke of width `w` legitimately reaches `w/2` past
  its path.

## What to assert

1. **No primitive outside its canvas** — for each canvas id, `-slack <= x <= w + slack`, same for y.
2. **Only the elements that must stay in bounds.** A deliberate off-canvas ghost or a decorative overlay
   drawn in the margin is by design; scope the assertion to the ids that drive the visible plot.
3. **The plotted range spans its data.** Recompute the axis limits from the embedded data's own min/max
   and assert the fitted range contains every series. A range hardcoded in the template is the classic
   failure this catches: the data grows, the axis does not.
4. **The page's numbers equal the source's.** Compare the embedded JSON against the CSVs or `.mat` file
   that produced them. **Set the tolerance from the storage precision, not from float noise** — values
   stored to 5 significant figures cannot match to `1e-6`, so use `1e-5` with a comment saying why, or the
   harness reports rounding as a defect.
5. **Every state, not the default one.** Run each draw function across its slider extremes and its dataset
   selector, so a branch that only executes at one end of the sweep is exercised at all.

## What it does not prove

A clean run means the draw code did not throw, drew nothing outside its canvases, and plotted the source's
numbers. It does **not** prove the page paints — a canvas left at zero height by CSS, a missing stylesheet
and a webfont that never loads all pass. Pair it with a real render (a headless-Chrome screenshot) and say
which check you ran. Reading the page in the desktop preview pane is a cheap independent second check: it
returns the rendered text (labels, readouts, headings), which catches a blank or half-wired render that the
stub harness still passes.
