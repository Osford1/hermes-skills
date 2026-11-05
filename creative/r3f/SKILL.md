---
name: r3f
description: "Use when building a 3D web scene (three.js or R3F)."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [threejs, react-three-fiber, webgl, 3d, visualization, robotics, gltf, shaders]
    category: creative
    related_skills: [p5js, interactive-concept-widgets, glassy-panel-design, web-design-recipes]
---

# react-three-fiber (R3F)

Declarative three.js for React: `<mesh />` becomes `new THREE.Mesh()`, and components
participate in React's state, events and scheduling. Use it when a deliverable needs a
*real 3D scene* — scene graph, cameras, lights, PBR materials, glTF assets, joints.

Worked example (verified, renders headless):
`<archive>/Sessions/2026-09-27-r3f-web3d-skill/Deliverables/WebApps/r3f-motion-lab/index.html`
— a 2-link arm tracking a circular reference with IK, a strip chart and a HUD.

## When to use it — and when not

| Want | Tool |
|---|---|
| 3D scene graph, glTF/CAD models, joints, PBR, camera control | **R3F** |
| Shader/particle/generative art, 2D-ish visuals, one-file sketches | `p5js` (no build step, own references) |
| A teaching widget with a bit of depth | CSS 3D or SVG first — cheaper, accessible, no WebGL |
| Plain three.js with no React | three.js directly; R3F's value is componentisation + state |

Do not reach for R3F just to get a moving gradient or a shader effect — that is `p5js`
territory and needs no build step at all.

## Version pairing is a hard constraint

- **@react-three/fiber 8 ↔ React 18**, **@react-three/fiber 9 ↔ React 19**.
- drei 10.x pairs with R3F 9; drei 9.x with R3F 8.
- Next.js 15 App Router must be on R3F 9 + React 19 (R3F 8 is structurally incompatible
  with the vendored React canary).

## Mode A — single file, no build (default for widgets and demos)

Verified working importmap (see `templates/single-file-r3f.html` for the full file).
Babel-standalone compiles real JSX in the browser, so **any R3F example from the docs can
be pasted in unmodified** — worth the ~3 MB and the compile delay.

```html
<script type="importmap">
{"imports": {
  "react": "https://esm.sh/react@19.1.0",
  "react/jsx-runtime": "https://esm.sh/react@19.1.0/jsx-runtime",
  "react-dom": "https://esm.sh/react-dom@19.1.0",
  "react-dom/client": "https://esm.sh/react-dom@19.1.0/client",
  "three": "https://esm.sh/three@0.170.0",
  "@react-three/fiber": "https://esm.sh/@react-three/fiber@9.1.2?external=react,react-dom,three",
  "@react-three/drei": "https://esm.sh/@react-three/drei@10.0.6?external=react,react-dom,three,@react-three/fiber"
}}
</script>
<script src="https://unpkg.com/@babel/standalone@7.26.4/babel.min.js"></script>
<script type="text/babel" data-type="module" data-presets="react"> … </script>
```

- `?external=` is required, or esm.sh bundles a **second** copy of react/three and you get
  silent hook/instance errors.
- esm.sh, jsdelivr and unpkg all resolve fine from this machine (no proxy needed; Clash is
  there if it ever stops).
- `data-type="module"` keeps `import` statements, and the import map still resolves them.

Mode B is a normal Vite + npm project — needed only for local assets (glTF, textures,
HDRIs) or a production build.

## The five patterns that matter

1. **Animate with `useFrame` + refs, never with state.** A `setState` in the frame loop
   re-renders the tree 60×/second. Write to `ref.current.rotation` etc. directly.
2. **Keep tunables in a mutable object, not props.** Sliders write `P.gain = n`; `useFrame`
   reads it. (zustand is the production version of this.)
3. **Nested `<group rotation-y={…}>` IS a kinematic chain** — each child's frame is the
   parent's. No matrix math, no transform composition by hand.
4. **Growing geometry: one preallocated buffer**, `setDrawRange(0, n)` +
   `attributes.position.needsUpdate = true`, and `frustumCulled={false}` (the bounding
   sphere is stale, so a growing line vanishes without it).
5. **HUD readouts are written imperatively** (`ref.current.textContent`) from the frame
   callback, never via state.

```jsx
<Canvas shadows dpr={[1, 2]} gl={{ antialias: true, preserveDrawingBuffer: true }}
  camera={{ position: [2.9, 2.4, 2.5], fov: 38 }}>
  <mesh position={[0, 1, 0]} onClick={…}>
    <boxGeometry args={[1, 1, 1]} /><meshStandardMaterial color="#dbe3ee" />
  </mesh>
</Canvas>
```

All three.js exports are native to R3F: camelCase props (`castShadow`, `rotation-x`),
array shorthand for vectors (`position={[x, y, z]}`, `shadow-mapSize={[1024, 1024]}`).

## Pitfalls (each one cost a real iteration)

- **Metalness without an environment map looks broken.** `metalness: 0.8` with no envMap
  reflects nothing: black faces plus blown-out highlights. Use metalness ≤ 0.3 with
  roughness ≈ 0.5, or add an `Environment`. This is the most common "my render looks
  wrong" cause.
- **1px lines are invisible at 4K.** `lineBasicMaterial.linewidth` is ignored by WebGL.
  For a stroke with weight, use `<points>` with `size` + `sizeAttenuation` over the same
  buffer, a real mesh (cylinder/ribbon), or drei's `Line` (Line2).
- **`atan2` returns (−π, π] — unwrap IK/joint angles onto the nearest revolution** before
  feeding a controller or a joint model, or the arm unwinds the long way round (a 2π jump
  made a 79 mm error spike to 1690 mm). `nearestAngle(target, current)` in the worked example.
- **Exaggerate tiny quantities, and label it.** A 70 mm error on an 850 mm circle is
  invisible. Draw it ×N (`ERR_VIS`) and say so in the UI; keep the numeric readout true.
  An unlabelled exaggeration is a lie, a labelled one is engineering practice.
- **A tone-mapped accent shifts hue.** `#ff4d4d` renders around hue 20-25°, so an exact-colour
  pixel test reported a drawn error bar as missing and sent me chasing a phantom. Classify by
  hue bucket, and print an ASCII hue map of the region before concluding anything is absent
  (`scripts/verify-render.py`).
- **Annotation geometry drawn at table level gets occluded by the mechanism's own links.** From
  an elevated camera the links project across the floor and hide a bar lying flat on it. Put
  error vectors and labels in the arm/tool plane, not on the ground.
- **A CSS class can eat your readout.** A value `<span class="v err">` silently inherited
  the page's `.err` error-box rule (`display:none`) — the value was written every frame and
  never visible. Namespace value classes away from layout classes.
- **Verify on rendered pixels, then with an eye.** Grep the DOM (numbers correct) *and*
  look at the image; both caught defects the other missed.
- **An imperative writer and its JSX node are a pair.** HUD readouts are set with
  `ref.current.textContent` from the frame loop, so deleting a readout row without deleting its
  writer leaves a null dereference that kills the whole loop — the page then looks blank for no
  obvious reason. Same trap when moving JSX out of a component's `return`: it silently becomes
  module-scope code and references its props out of scope. Keep the visible error region on the
  page; it named both bugs here in seconds.
- **Check that the layout fits by measuring, not by looking.** A panel taller than the viewport
  clips silently, and a screenshot makes that look like a rendering bug. Probe it: set
  `scrollHeight` vs `clientHeight` (and `getBoundingClientRect().bottom` against
  `innerHeight`) into the error div and read it back with `--dump-dom`. 928 px of content in a
  764 px viewport is invisible in a screenshot of a scrollable panel.

## Capturing and verifying (headless)

Full recipe: `references/headless-capture-verify.md`. The headline trap:

> **Headless Chrome's `--virtual-time-budget` starves rendering steps.** R3F then fails
> twice — `ResizeObserver` never delivers (canvas stays at its 300×150 default in the
> corner) and `requestAnimationFrame` barely ticks (0–2 frames in 8 s), so the screenshot
> is an empty page. Passing `--window-size` does not help.

Fix inside the page: an effect that explicitly `gl.setSize(w, h, false)`,
`camera.aspect = w/h; camera.updateProjectionMatrix()`, then `gl.render(scene, camera)` on
a few timers, exposing `window.__paint` for a manual trigger. In a real browser the size
check matches and it is a no-op.

**Warm-start the simulation before the first frame** (run the step function N times at
module load, seed the geometry buffers and any chart history from it). A capture lands at
frame ~1–4, so a cold start photographs the transient — including a stray approach line
across the whole scene.

```bash
CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe"
"$CHROME" --headless=new --user-data-dir="$LOCALAPPDATA/Temp/r3f-shot" \
  --window-size=1600,900 --force-device-scale-factor=2 --virtual-time-budget=15000 \
  --screenshot="C:/path/out.png" "file:///C:/path/page.html"
# state check, same page:  --dump-dom | grep -oE 'class="v[^>]*>[^<]*'
```

Pass **native `C:/…` paths** to Chrome (MSYS `/c/…` fails), and url-encode spaces in the
`file://` URL as `%20`. For interactive work prefer the `browser_exec` tool (a real
browser session) — see the pitfall about WebGL context limits there.

## Engineering-domain notes (robotics / mech)

- Build mechanisms from primitives (cylinders/boxes/spheres) when you only need to *show*
  kinematics; load glTF when geometry fidelity matters.
- STEP → glTF via FreeCAD/Blender, then `useLoader(GLTFLoader, url)` inside `<Suspense>`;
  scale mm→m (three's world unit is metres) so camera and light distances stay sane.
- Add a ground grid + ContactShadows: without a shadow the model looks like it floats.
- Label axes/scale on screen when the artifact is a measurement plot, not a pretty picture.
