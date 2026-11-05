---
name: particle-art-pages
description: Use when building an interactive particle-art HTML page.
---

# Particle Art Pages

One-file interactive pages where the centerpiece is a GPU particle system (galaxy,
heart, fireworks) plus DOM scenes around it (lock screen → particle scene → letter/photo
finale). Distilled from an 8-iteration verified build; every rule below survived to the
final version.

## Stack decision

- **Plain three.js UMD** (`three.min.js` r128 vendored beside the HTML, loads from
  `file://`), NOT R3F/React — multi-scene DOM pages have no React state worth the build.
- All particles: one `THREE.Group` per rotating system + a shared `ShaderMaterial`
  factory (uniforms `uTime` for twinkle/drift, `uFade` for scene transitions, 64px
  radial-gradient canvas sprite, `AdditiveBlending`, `depthWrite:false`,
  `vertexColors:true`, per-particle `aSeed`).

Full recipe (spiral arms, parametric particle heart, interaction math, DOM-label sync,
explosion transition): `references/particle-galaxy.md`.

## Always-on rules (this user)

- All user-tunables in ONE `CONFIG` object at the top of the script with Chinese
  comments: password, orbitSpeed, particleCount, zoomSpeed/Min/Max, per-word
  `{word, en, img, caption}`, letter text. The user edits this block only.
- Verify the FULL flow in `browser_exec` before every delivery: type password → galaxy
  appears → click a chip → lightbox → click main heart → explosion → finale scene.
  Report a table of checks. Zero console errors is the bar.
- Photos live beside the HTML and are referenced by relative path in CONFIG
  (`img:"Image 1.jpg"`); copy them into the deliverable folder.

## Pitfalls (each cost a real iteration)

- **Blurry points = twinkle in `gl_PointSize`.** Keep twinkle in the COLOR varying only
  (`vTw = 0.88 + 0.12*sin(...)`, floor ≥0.85) and compute size independently:
  `gl_PointSize = uSize * (140.0/-mv.z)`. A brightness floor near 0.68 reads as blur.
- **Rotate the GROUP, never individual points or the camera, for drag-to-spin.** Drag
  velocity `dx*0.005/(dt/16.7)` gives inertia; ease back to cruise with
  `spinVel += (cruise-spinVel)*0.02`. Tilt is a separate clamped `rotation.x` target.
- **DOM labels synced to 3D orbits:** set the 3D object's position in LOCAL space (it
  inherits the group's rotation), then `applyMatrix4(group.matrixWorld).project(camera)`
  for the DOM chip's left/top. Drive chip opacity/scale/pointerEvents from projected
  depth (`v3.z`) so labels behind the scene fade and stop clicking. Do NOT add a `sin(t)`
  bob to labels — it reads as a bug, not life.
- **Explosion:** read the source Points' position attribute, transform by
  `group.matrixWorld`, assign radial velocities, integrate in rAF while `uFade` ramps the
  whole scene out; dive the camera at the same time (`camTarget = start*max(.32,1-dt*.9)`).
- **Particle mini-copies (icons) must be real Points, not canvas images** — one shared
  BufferGeometry + one shared material across all N copies costs 1 draw call and one
  `uTime` twinkles them all. Give each a phase-offset heartbeat scale in the tick loop.
- **Surface shader-compile errors on-page**: after `renderer.compile`, walk
  `renderer.info.programs` and print `p.diagnostics` into a visible box — a silent shader
  fail on the recipient's machine is otherwise a black page.

## Photo-finale GIF (draws-itself effect)

`fogleman/primitive` produces the "photo assembles from triangles" animation. Working
pipeline and GIF assembly rules: `scripts/primitive-gif.md`. Key traps: Go toolchain
needs ≥1.26 for primitive's deps; `GOMODCACHE` must be a NATIVE Windows path
(`C:\...`, MSYS `/c/...` is rejected as relative); the `-o` flag must contain `%d`
(frame pattern) or it exits 4 silently; assemble the GIF with PIL using ONE shared
palette and dithering OFF (per-frame palettes flash, dithering shimmers); hold the last
frame ~2.6s so the finished photo lingers.

## Environment notes

- cdnjs (`cdnjs.cloudflare.com`) resolves fine from this machine for vendoring
  three.min.js; picsum.photos works for placeholder photos.
- Go 1.27 portable toolchain + prebuilt primitive binary may still be at
  `C:\Temp\go` and `C:\Temp\galaxy-build\gopath\bin` — check before reinstalling.
