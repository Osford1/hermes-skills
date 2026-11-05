# Verifying a widget in the browser (the numeric recipe)

The agent cannot see the render. Every claim about a widget's behaviour must come back as a
number or an exact value from `browser_exec`, not from a screenshot and not from reading the
source and hoping.

## 1. Build the probe hook into the widget

Expose the model, not the DOM:

```js
window.__w = {
  state:  function(){ return {t1:t1, t2:t2, trail:trail.length}; },
  set:    function(a,b){ t1=a; t2=b; syncControls(); onMove(); },  // drive the model AND write it back
  circles:function(id){ var c=document.getElementById(id); return [c.width,c.height]; },
  ink:    function(id){                                     // non-transparent pixel count
    var c=document.getElementById(id), g=c.getContext('2d');
    var d=g.getImageData(0,0,c.width,c.height).data, n=0;
    for(var i=3;i<d.length;i+=4){ if(d[i]>8) n++; }
    return n;
  }
};
```

**`set()` must not be model-only:** write the new values back into the range inputs, checkboxes and their value labels in the same call. A setter that moves only the model leaves the visible controls reading the previous state, so a screenshot taken as verification appears to contradict the state you set (a computed "GIMBAL LOCK" under a slider still showing 60°), and any real preset path through that setter shows the user the same lie. Merge the two: state, input value, and every derived label in one function. Also install an error sink so a swallowed exception is still visible:

```js
var ERRORS=[];
window.addEventListener('error', function(e){ ERRORS.push(String(e.message)); });
window.__wErrors = ERRORS;
```

An error sink catches *async* throws. A throw during init is better caught by re-evaluating the
script body in a try/catch (see the duplicate-`id` pitfall in SKILL.md), because an exception
before the hook is assigned leaves you no hook to read the sink through.

## 2. Load and assert

`file:///` URL, spaces percent-encoded (`%20`). If the browser daemon refuses to start — a stale
endpoint, e.g. a permission error unlinking its `runtime/bu-default.port` — re-issue the *same*
call with a named `session="<name>"`: a named session gets its own daemon and endpoint and the call
then runs normally. A daemon that dies MID-session — a connection-refused socket error on a call that worked a minute ago — needs no diagnosis either: re-issue the call and it restarts, then `new_tab(url)` before asserting, because the old page died with it. Do not go hunting processes to clear it: the user's own Chrome shares the `chrome.exe` image name and a broad kill closes their browser. One expression returns everything:

```js
({errors: window.__wErrors,
  state: window.__w.state(),
  sizes: {a: window.__w.circles('a'), b: window.__w.circles('b')},
  ink:   {a: window.__w.ink('a'), b: window.__w.ink('b')}})
```

| Assertion | What it catches |
|---|---|
| `errors` empty | a thrown exception inside an init path |
| `sizes` match the intended internal resolution | a canvas silently sized 0 (hidden-tab layout) |
| `ink > 0` on every canvas | draw code that ran without painting — a blank artboard with a clean console |
| **the initial state satisfies the widget's premise** | opening in the very state the widget is meant to demonstrate as wrong/illegal |

The premise check is the one that gets skipped and the one that matters most: "it rendered"
and "it starts in a sensible state" are different claims. Ask the model for the start
condition and assert it (free / valid / in-range), then pick the default until it passes.

**A widget that exists to show an invariant must expose that invariant as a number.** When the whole
point is "this quantity never changes", put it in the probe as a spread — the max deviation across
the full sweep, not a single reading — and assert it is at machine epsilon. Pinning the hand, holding
the pose, preserving an energy: a max-deviation-of-1e-15 across every state is the proof, and a
single spot-check is not. **A number the widget PRINTS is itself an assertion — read it on load.** Where a panel displays a computed identity ("max error 0", an agreement fraction, a collapse check), assert that printed value equals its exact target in the initial state. A panel claiming "the chain collapses to one matrix — max error 0" while composing in the wrong order prints a real non-zero error and no other check in the loop notices, because the page renders perfectly. The mechanism is worth memorising: to apply operations IN SEQUENCE, pre-multiply each new one into the accumulator (`A = mm(op, A)`); `A = mm(A, op)` silently reproduces the reverse order.

## 3. Canvas coordinate mapping (the thing that silently breaks probes)

A canvas has an INTERNAL pixel grid (`width`/`height` attributes) that CSS scales. Model code
draws in internal coordinates; a pointer event arrives in client coordinates. Convert both ways
and never mix them:

```js
// client -> internal (for dispatching events)
const r = canvas.getBoundingClientRect();
const x = (clientX - r.left) * (canvas.width  / r.width);
const y = (clientY - r.top ) * (canvas.height / r.height);

// internal -> client (for probing a pixel you expect the draw code to have painted)
const clientX = r.left + xInternal * (r.width  / canvas.width);
```

`getImageData(xInternal, yInternal, 1, 1)` takes INTERNAL coordinates. Probing a pixel at the
client coordinate silently samples the wrong place and returns a false negative.

**Never use `window.devicePixelRatio` in a probe — derive the ratio from the element.**
`canvas.width / getBoundingClientRect().width` is always right; `window.devicePixelRatio` is right
only until something changes the emulation. Setting device metrics *after* the page loaded
retro-changes `devicePixelRatio` while the canvas keeps the resolution it was built with, so probes
sampling at `x * dpr` land outside the bitmap and `getImageData` returns transparent — which reads as
"nothing was painted" and sends you hunting a draw bug that does not exist. Either set the metrics
*before* loading, or `location.reload()` after setting them, and derive the ratio from the canvas in
every case.

Note this conversion is only needed when you *dispatch* pixels or *probe* pixels. A widget driven by
plain form controls (a range input, a checkbox, a button) needs no coordinate maths at all: drive it
by dispatching `new Event('input')` / `new Event('change')` on the element and assert the model state
from the probe. Prefer that when the concept allows it — it removes the whole class of mapping bugs.

## 4. Test interaction by dispatching synthetic events

Assert the mapping is exact — not "something moved":

```js
const fire = (type, clientX, clientY) => canvas.dispatchEvent(
  new PointerEvent(type, {clientX, clientY, pointerId:1, bubbles:true}));
fire('pointerdown', X, Y);
// then: state must equal the model value that pixel encodes (within float epsilon)
```

`pointerdown` + `setPointerCapture` is what the widget listens for; dispatch that, not `mousedown`.

## 5. State-dependent rendering

When a render path branches on the model (a marker turning red inside a forbidden region),
prove both branches by sampling the same pixel in both states and comparing channels:

```js
// colliding state -> pixel should be the alert colour
// free state      -> same pixel should not be
```

Count the alpha channel for coverage, sample RGB for meaning.

## 6. What this proves, and what it does not

Proves: the code runs, paints, maps input exactly, and branches correctly on state.
Does not prove: that it *looks* good — layout, contrast, overlap, whether an annotation sits on
top of the art. Say so rather than claiming the visual is verified.

## 7. Tuning parameters you cannot see (anchored replica, then gated search)

When the widget's *content* depends on tunable numbers — obstacle placements, thresholds, which rows
of a dataset to show — and the quality test is "does this read well", you cannot judge candidates by
eye any more than you can judge the render. Do not hand-guess one candidate, reload, and squint.

1. **Replicate the model in a standalone Node script** using the widget's own equations, copied
   verbatim. Keep it next to the widget so a later edit re-tunes instead of re-deriving.
2. **Anchor-verify the replica BEFORE tuning.** Run it with the widget's *current* parameters and
   assert it reproduces the browser probe's numbers exactly — series length, min, max, argmax, any
   count. A replica that disagrees is tuning a different widget; a disagreement in only the last
   digits of an invariant means you changed an operation order, and is worth resolving before you
   trust a search. Ship nothing from a search until this agrees.
3. **Gate the search on teaching criteria, not on one optimum.** Random-sample the parameter space,
   keep only candidates passing several gates *at once*, then rank the survivors. Typical gates: the
   **opening state must be legal** (the §2 premise rule — a widget must not open in the state it is
   teaching you to avoid), the interesting regime must be present at a useful fraction (say a fifth
   to a third of the sweep), one clear best case exists and is not pinned to either end, and the best
   stands well clear of the median so it reads as a peak rather than a plateau.
4. **Apply the winner, reload, and re-assert** that the browser probe now matches the replica's
   prediction. Two independent implementations agreeing is the proof; either one alone is not.
5. **Report how many candidates passed the gates.** If the answer is zero, the gates contradict the
   widget and one of them is wrong — loosen deliberately and say which, rather than quietly shipping
   the least-bad sample.

## 8. Verifying a redraw, and verifying the verifier

**`ink > 0` cannot detect a failed redraw when a fill covers the panel.** A background region painted
across the whole plot keeps the non-transparent count identical between two different models, so the
assertion passes while the picture is stale. Verify a redraw by (a) a checksum over the pixel data and
(b) sampling pixels whose EXPECTED value you took from the source array — colour versus sign, class
versus label — comparing each probe against the widget's own indexing of that array. Report the
result as an agreement fraction, not as "the redraw works".

**Sample the layer you mean.** A probe at a data marker's centre reads the marker, not the background
beneath it. Offset scatter probes by a fraction of a cell so they land on the layer under test, and
keep note of which layer each probe targets.

**When every probe fails, look for one global error, not N local ones.** Zero of sixteen disagreeing
is not sixteen bugs: it is a flipped axis, an inverted colour-to-class map, or a source array read
with the wrong row convention (row-major with the first row at the *smallest* y, while the canvas
draws row 0 at the *top*). Re-derive one expected value by hand from the source data before touching
the widget.

**Verify the verifier.** Before reporting a defect the probe found, re-derive the expected value
independently: most of the faults a fresh probe reports are its own coordinate-frame bugs (a stale
device-pixel ratio, a probe parked on a marker, a mirrored grid). Drawing code that agrees with its
own arithmetic, its own pixel mapping and an independent hand-check is verified; a probe that
disagrees is the first suspect.

## 9. Verify the maths against the source's own closed form

A teaching widget built from a paper or lecture deck must reproduce THAT source's printed formula, not merely "a" correct rotation matrix — convention is where the errors hide (which axis turns first, intrinsic vs extrinsic, ZYZ vs ZXZ, and which of two matrices a source prints for a dual reading, since the same matrix can be described by body axes in one order or reference axes in the reverse order). Take the closed form the source prints, evaluate it at two or three angle triples, and compare element-by-element with the widget's own matrix at ~1e-4, printing the max element error. Implement the reference in Python/numpy inside `execute_code` so the check is a second implementation rather than the widget agreeing with itself. This is §2's dataset anchor rule applied to formulas instead of cells: the source's own stated example is free ground truth, and agreement is what proves the convention baked into the widget is the source's convention.
