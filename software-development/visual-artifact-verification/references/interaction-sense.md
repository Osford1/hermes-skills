# Interaction sense in a projected 3D scene

**Trigger:** the artifact lets the user click or drag a model that lives in an axonometric or
perspective projection, and the requirement names a *direction* — "it rotates the way I drag",
"clockwise seen from the top of the z axis", "it opens away from me".

A change-detector passes while the model turns backwards. Direction has to be settled against a
ground truth that does not come from your own sign convention, and that ground truth is drawable
from the page itself.

## 1. Read the driven value, never the pixels

Have the artifact print what it is driving — an angle readout, a `data-` attribute, an `aria-live`
string. Assert the *sign and magnitude* of that number per scripted step. No pixel comparison
decides a direction: a rotating model looks plausible at every yaw.

Decide what the expected sign is **before** running, from the generator's own rotation convention,
and write that expectation into the probe's output so a future reader sees the claim and the
measurement side by side.

## 2. Turn the generator's convention into a screen-space test

- Most kits rotate about `+z` so that a **positive** angle takes `+x` onto `+y` (a right-handed
  `rotate(θ)`); confirm from the kit's own rotation function rather than from the rendered look.
- With screen `y` pointing **down**, take `u` = the drawn direction of `+x` and `v` = the drawn
  direction of `+y`, both as vectors from the drawn origin. If `cross(u, v) > 0`, a **positive**
  value reads **clockwise as seen**; `cross(u, v) < 0` reads anticlockwise.
- That sign belongs to the *plane's projection in the page*, not to the camera's azimuth: an
  azimuth swing rotates the whole image in-plane, and a plane's projection preserves orientation,
  so the sense comes out identical at two opposite azimuths (measured, not assumed).
- The practical consequence: **an inverted drag is never a camera problem.** Don't reason in words
  about which way an axis "looks" — the same axis points left at one azimuth and right at the
  other while the sense stays put. Reason with the cross product.

## 3. Locate the pivot from the artifact's own anchors

The midpoint of the drawn `+x` anchor and the drawn `−x` anchor is the drawn position of the model's
origin — the turn pivot — and the `±y` pair gives a second estimate. Take both from the labels'
bounding boxes, so no camera internals are needed:

```js
[...document.querySelectorAll('text, .axis-label')].map(e => {
  const r = e.getBoundingClientRect();
  return [e.textContent.trim(), r.left + r.width/2, r.top + r.height/2];
})
```

Group by label text, average each pair, and check the two midpoints agree within a few px: that
agreement is also the evidence that the anchors really mark the ground plane rather than a legend.

## 4. Decide which face of the model the viewer sees

A one-sided projection shows either the front or the back, and the DOM has no opinion about which.
Pick a part whose local coordinate is unambiguously the model's far side (a hinge, a back panel,
the tall edge) and project its *known* local direction into the image with the anchors:

- far-side direction must project **away** from the viewer, i.e. toward the top of the page for a
  camera above the plane: `dot(far_screen, (0, −1)) > 0`.
- State the result in words in the report, in both readings, so a mis-read is visible:
  "the hinge projects up-page → the keyboard is away from the viewer and the leading edge is
  nearest → the page shows the front."

A 180° azimuth change flips exactly this *and* reverses the pointer→ground orientation map. Those are
the same fact seen twice: from the other side of the plane, both the visible face and the drag sense
that makes the model follow the hand invert together.

## 5. Fix in the right place

- **Wrong face showing** → fix the model's *home orientation*: a rigid half-turn about `z` at the
  model's mounting level, leaving the world frame and the axis layout exactly as the generator
  draws them. A rigid rotation about the pivot does not disturb the drag mapping (the local angle
  delta equals the world delta).
- **Drag inverted** → fix the sign of the drag→value mapping. Where a helper returns an `atan2`
  delta about the pivot, that delta's sign *is* the whole decision; do not stack a camera change on
  top of it.
- **Both symptoms at once** → the home orientation first, then re-measure; one of the two is
  usually a consequence of the other, and fixing them as two independent defects trades one bug for
  another.
- **Re-measure the sense after any camera or mounting change.** Either one invalidates the earlier
  reading by construction.

## 6. Preserve the documented axis layout when the user asked for the standard frame

When the request names the common `x`/`y`/`z` frame, the generator's documented azimuth is part of
the deliverable: the ground axes read the way the references draw them. Keep that draw and move the
model instead. Swapping the azimuth to "fix" a drag also re-lays the ground, and can leave the model
drawn from behind — two defects traded for one.

## 7. Headless behaviour harness (when no browser session is available)

1. Launch, in the background, with a scratch profile:
   `chrome --headless=new --disable-gpu --no-first-run --user-data-dir=<temp>/prof --remote-debugging-port=9222 about:blank`
2. Poll `http://127.0.0.1:9222/json` until it answers and read `webSocketDebuggerUrl`.
3. In Node (globals `WebSocket` and `fetch` are present in v22+), open the socket and send
   `Runtime.enable`; per step send `Page.navigate` to the `file:///` URL, wait for load, then
   `Runtime.evaluate` with `returnByValue: true, awaitPromise: true`.
4. Drive the gesture as real input — `Input.dispatchMouseEvent` with `pressed` buttons at viewport
   coordinates (`mousePressed` → several `mouseMoved` → `mouseReleased`), or synthetic
   `pointerdown`/`pointermove`/`pointerup` on the element with the same `clientX/clientY` the
   handler reads. Then read the artifact's own readout text.
5. Print one compact JSON line per state and a one-line verdict; take pixels separately with
   `Page.captureScreenshot` when a claim needs them.
6. Keep each `Runtime.evaluate` short and sleep in the harness, not inside the evaluated script:
   a long evaluate is cut off, and the timeout arrives looking like a page failure.
7. Open the delivered path (`file:///C:/...`), not a dev server — the offline and relative-path
   behaviour is part of what is being verified.

## 8. Author the resting state

- Put the start pose into the shipped data explicitly, and make sure nothing auto-syncs from
  build-baked values or auto-plays a demo on load. Otherwise the artifact animates itself before the
  first input, and every "at rest the user sees X" claim is fiction. Assert the post-load state
  before dispatching anything.
- Keep the idling state and the driven state as separate assertions: a page that opens itself also
  makes a click *toggle* test pass for the wrong reason.
- Re-run the generator before reporting a patch series as landed. A build script that references a
  constant nobody defined throws on the next run, and a half-applied series reads as finished; the
  build's own summary line is the evidence that it ran.
