# Capturing and verifying an R3F artifact headlessly (Windows)

## 1. The trap: virtual time starves the rendering steps

`chrome --headless=new --screenshot` waits with `--virtual-time-budget=N`. Under virtual
time the renderer fast-forwards timers but does **not** deliver the two things R3F needs:

| Starved | Symptom |
|---|---|
| `ResizeObserver` | canvas keeps its default 300x150 box in the top-left corner; the rest of the page is empty |
| `requestAnimationFrame` | the render loop never paints; screenshot is a black canvas |

Measured: 0-2 rAF ticks in 8 s of virtual time, while `setTimeout` fires normally. WebGL
itself is fine — Chrome reports `webgl2=YES` and a real renderer:

- `--disable-gpu --enable-unsafe-swiftshader` → `ANGLE (… SwiftShader driver)`
- no flags → `ANGLE (AMD, AMD Radeon … D3D11)` — use this one, it is the real GPU.

`--window-size` does **not** fix the 300x150 canvas.

## 2. The fix: paint explicitly

In a `useEffect` inside the Canvas subtree, size and render without rAF:

```js
const paint = () => {
  const el = gl.domElement, p = el.parentElement
  const w = Math.max(p.clientWidth, window.innerWidth || 800)
  const h = Math.max(p.clientHeight, window.innerHeight || 600)
  el.style.width = '100%'; el.style.height = '100%'; el.style.display = 'block'
  if (el.width !== w * gl.getPixelRatio() || el.height !== h * gl.getPixelRatio()) {
    gl.setSize(w, h, false)                 // false: do not rewrite CSS
    camera.aspect = w / h
    camera.updateProjectionMatrix()
  }
  gl.render(scene, camera)
}
window.__paint = paint
const timers = [0, 150, 700, 1600].map(ms => setTimeout(paint, ms))
```

In a real browser the size check matches and this is a no-op.

## 3. Warm-start so frame 1 is the steady state

A capture lands at frame ~1-4. Anything that converges over time (a control loop, a
settling animation, an accumulating trail) photographs as a transient — and a recorded
trail from a cold start draws a stray line across the whole scene.

Solution: extract a pure `step(state, dt)`, then run it N times **at module load**
(before React renders), discarding the transient and pre-filling buffers/chart history
from it. Reuse the same function in `useFrame` so the initial state and the live sim agree.

## 4. Capture commands

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
URL="file:///C:/Users/<you>/path/page.html"      # native C:/ paths; %20 for spaces

# state check (DOM text)
"$CHROME" --headless=new --user-data-dir="$LOCALAPPDATA/Temp/r3f-dom" \
  --virtual-time-budget=15000 --dump-dom "$URL" 2>/dev/null \
  | grep -oE 'class="v[^"]*">[^<]*' | sed 's/class="v[^"]*">//'

# image
"$CHROME" --headless=new --user-data-dir="$LOCALAPPDATA/Temp/r3f-shot" \
  --window-size=1600,900 --force-device-scale-factor=2 --virtual-time-budget=15000 \
  --screenshot="C:/path/out.png" "$URL"

# console + uncaught errors
"$CHROME" --headless=new --enable-logging=stderr --v=0 --virtual-time-budget=9000 \
  --dump-dom "$URL" 2>&1 | grep -iE 'CONSOLE|Uncaught|THREE\.'
```

Keep each capture in its own `--user-data-dir`; a dir reused mid-run behaves differently.
A running interactive Chrome may swallow `--version` ("Opening in existing browser session")—that is harmless.

## 5. Verify pixels, then look at it

Exact-colour matching is too strict: a semi-transparent accent over a dark table lands far
from its nominal RGB. Classify by **hue bucket and saturation** instead (Pillow):

```python
sat = (mx - mn) / mx                 # keep sat >= 0.30 and value >= 60
hue = colorsys.rgb_to_hsv(...)[0] * 360
# amber 25-55   teal 150-200   red >=340 or <15
```

Also measure occupancy in the region the scene should cover (a "lower/middle band" of
0.0 % means the canvas is empty, whatever the file size suggests). A ~1 % saturated-pixel
frame of thin strokes on dark is normal and healthy.

Then check the picture with a vision pass. Both layers earn their place — real defects
caught this way: a readout span that inherited `display:none` from a colliding CSS class,
a 1 px error vector that was invisible, a trace ring that visually merged with the
reference ring, an unlit metal look, and a stray transient line from a cold start.

## 6. Browser-session caveat

Driving many tabs in one automated browser session can exhaust WebGL contexts — after
several loads a fresh tab came up with an uninitialised 300x150 canvas and no rAF frames,
while the same file rendered fine in headless. Prefer one tab, reload it, and keep heavy
capture work in headless Chrome.

## 7. Measure the layout, don't eyeball it

Clipping is the defect a screenshot hides best: a scrollable panel that overflows looks like a
broken render, and a stale readout looks like a styling choice. Probe the geometry from inside
the page and read it back as text:

```js
// append to a COPY of the page (never the deliverable), then --dump-dom and grep the marker
let tries = 0
const timer = setInterval(() => {
  const p = document.querySelector('.panel'), f = document.querySelector('.footer')
  if (!p || !f) { if (++tries > 20) clearInterval(timer); return }
  const e = document.getElementById('err'); e.style.display = 'block'
  e.textContent = 'FIT panelContent=' + p.scrollHeight + ' visible=' + p.clientHeight +
    ' window=' + window.innerHeight + ' clipped=' + (p.scrollHeight > p.clientHeight) +
    ' footerBottom=' + Math.round(f.getBoundingClientRect().bottom)
  clearInterval(timer)
}, 300)
```

Grep for the value that follows the marker (`grep -oE '<div id="err"[^>]*>[^<]*'`), not for the
marker text itself — the probe's own source is in the DOM too and matches first.

Also worth knowing: `--window-size=1600,900` gave a **802 px** viewport in this Chrome build, so
size the probe against `innerHeight`, not against the number you passed to the flag.

