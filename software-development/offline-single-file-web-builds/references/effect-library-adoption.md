# Should we vendor a GPU-heavy effect library? (three.js / Vanta class)

"Can we just vendor it?" is two questions in order, and only the second one is hard:

1. **Does it vendor at all** — disk, licence, offline, no CDN at runtime.
2. **Can the target machine afford it per frame** — measured, never inferred from the library's
   reputation.

Answer the first by downloading it; answer the second by benchmarking against the implementation you
already have. A yes to (1) is not a yes to (2), and the whole cost of this decision is forgetting
that.

## 1. Does it vendor?

- Check `_Knowledge/vendor/` first. Vendor sets are pinned per release and copied as a set; adding
  one library means adding its whole dependency chain.
- Fetch the pinned file to a scratch dir and measure real bytes — a CDN's advertised size is
  gzipped, and from `file://` nothing is compressed:
  `curl -sL -o three.min.js "https://unpkg.com/three@0.134.0/build/three.min.js"`, then `ls -l`.
  three r134 is **601 KB**; Vanta's clouds 15 KB and fog 13 KB ride on top of it — **643 KB total**,
  MIT, all of it loadable from disk.
- Confirm what you downloaded is the real artifact: grep the revision
  (`grep -o 'REVISION="[0-9]*"'`) and check the licence header. A truncated redirect lands as a
  broken `<script>` that fails silently.
- **Count the WebGL contexts the design needs.** A cross-fade between two library effects (cloud
  sea → fog bank) means both alive at once, which is the documented ceiling for this class of
  library and where context loss appears. If the design calls for a cross-fade, that alone can
  disqualify it — the hand-built field does it with two 2D canvases and no such limit.

## 2. Confirm the benchmark is measuring the GPU and not a fallback

Do this before believing any number, including a bad one:

```js
const c  = document.createElement('canvas');
const gl = c.getContext('webgl2') || c.getContext('webgl');
const d  = gl.getExtension('WEBGL_debug_renderer_info');
gl.getParameter(d.UNMASKED_RENDERER_WEBGL);
// real hardware: "ANGLE (AMD, AMD Radeon(TM) Graphics (0x00001681) Direct3D11 vs_5_0 ps_5_0, D3D11)"
// software render: names SwiftShader / llvmpipe — the numbers are CPU-rendered and meaningless
```

## 3. Measure work-per-frame against what you already ship

- Same browser, same machine as the user, at the viewport the deliverable is actually read at.
- A plain `requestAnimationFrame` loop recording deltas into a rolling window (~240–400 samples),
  reporting **median and p90**.
- **Establish that the loop is unthrottled before comparing.** If rAF runs faster than the display's
  refresh (a ~7 ms median is ~143 fps), it is unthrottled — so the reading is *work per frame* and
  comparable across implementations. If both implementations read the vsync cap (~16.7 ms), the
  comparison says nothing: push the workload up until one of them breaks the cap.
- **Benchmark the configuration you would ship**, not a convenient toy. Two effects sharing a
  half-height split read 27.8 ms; the same clouds effect full screen read **55.6 ms** (p90 76.2).
  Sample for ~7 s so the median is stable.

Measured on this user's laptop (AMD Radeon integrated, D3D11 via ANGLE — hardware, verified above):

| implementation | median | p90 | ceiling |
|---|---|---|---|
| canvas field (pre-rendered tiles + blit) | 7.0 ms | — | ~143 fps |
| three r134 + `VANTA.CLOUDS`, full screen 1440x900 | 55.6 ms | 76.2 ms | **~18 fps** |

**The decisive argument is the shared budget, not the background.** On a page whose point is its
scroll choreography — smooth-scroll library, FLIP/shared-element focus, backdrop blur — a background
that eats 55 ms of every frame drags the whole page to 18 fps. Say that plainly: the richest
background in the world is a regression if it costs the transition that carries the piece.

## 4. Say what the library would NOT fix

Adopting the "authentic" implementation does not automatically fix a complaint about the look —
check the complaint against a real capture of the library's output before promising a fix. Two
instances:

- The reference's own sun is a diffuse bloom that barely registers at this viewport (its position
  and size are shader-fixed), so "the sun isn't clear enough" is a property of the *reference*, not a
  fidelity bug in the repaint. The hand-built version actually showed the sun more clearly.
- Its fog effect is flat isotropic turbulence: no horizon, no light direction. If the design wants a
  horizon in the fog, the library is not the answer.

## 5. The middle path, when the look is wanted and the cost is not

- **Render the effect ONCE into an offscreen canvas at load**, then feed that texture into the cheap
  tile/blit engine (drift, parallax, cross-fade all unchanged). Authentic output for a one-off cost
  at load, then canvas-field cost every frame after.
- Or tune the hand-built field toward a captured frame of the library's output — matching its banding
  and cloud-top horizon is free at runtime.

## 6. How to report it

Keep the spike: libs + spike HTML + a labelled side-by-side composite in the project's `Working/`, so
 the user can open it and move the mouse over the interaction themselves.

The composite carries: same viewport, same palette, one panel per implementation, each panel's frame
 number in its header, and a footer naming the conditions (viewport, GPU, unthrottled rAF). A number
the user can read next to the picture settles the question in one glance — and if the library looks
richer, say so in the same breath as the cost. Don't argue against a good-looking option; price it.
