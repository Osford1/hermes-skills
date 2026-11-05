# Three.js Particle Galaxy (plain three.js, no React)

Verified recipe from a personal particle page (30k particles, drag/tilt/zoom, particle heart,
DOM labels synced to 3D orbits). Plain three.js r128 UMD — right choice over R3F when the
deliverable is one HTML file with multiple DOM scenes and no React state.

## Architecture

- One `THREE.Group` per rotating system. Put every orbiting object (galaxy points, dust,
  heart, mini-hearts) in the group; drag/spin = `group.rotation.y`, tilt = `group.rotation.x`.
  Rotating the GROUP, not the camera, keeps drag inertia and label sync trivial.
- All particle systems share one `ShaderMaterial` factory: uniforms `uTime` (twinkle +
  drift), `uFade` (scene transitions), texture = a 64px radial-gradient canvas sprite,
  `AdditiveBlending`, `depthWrite:false`, `vertexColors:true`, per-particle `aSeed`
  attribute drives phase offsets.

## Spiral arms (CPU-built once, static buffers)

```js
const N=30000, R=30, arms=3;
for(let i=0;i<N;i++){
  const r = Math.pow(Math.random(),.62)*R + 3.2;      // radius, denser core
  const a = (i%arms)/arms*Math.PI*2 + r*0.34          // logarithmic winding
          + (Math.random()-.5)*(0.55 - r/R*0.3);      // scatter, tighter at rim
  // position = cos/sin(a)*r + gaussian scatter; y squashed ×0.34 (disk)
  // color = lerp(core→mid→rim by t) × brightness falloff (1-t)^1.6
}
```

## Particle heart (the shape that matters)

Parametric curve `x=16sin³t, y=13cos t−5cos2t−2cos3t−cos4t`, filled by scaling each
sample by `∛random` (uniform fill, denser rim), `+1.2` y-lift. For mini copies: same
curve at smaller scale, ONE shared BufferGeometry + ONE shared material across all
instances — 8 hearts = 1 draw call, and one `uTime` drives every twinkle.

## Sharpness (the #1 visual complaint)

Blurry points = twinkle multiplying `gl_PointSize` + a deep brightness floor. Fix:
keep twinkle in the COLOR varying only (`vTw = 0.88 + 0.12*sin(...)`, never below ~0.85),
and compute size independently: `gl_PointSize = uSize * (140.0 / -mv.z)`.

## Interaction pattern (all four verified)

- Drag spin: `rotation.y += dx*0.005`; velocity for inertia = `dx*0.005 / (dt/16.7)`;
  on release ease velocity back toward cruise: `spinVel += (cruise-spinVel)*0.02`.
- Drag tilt: separate `tiltTarget` clamped (`[-0.2, 1.2]`), ease `rotation.x` toward it.
- Zoom: wheel scales `camTarget`, ease `camDist += (camTarget-camDist)*.08`, then
  `camera.position.set(0, camDist*.59, camDist)` keeps a pleasant ~36° elevation.
- Explosion transition: read the heart's `position` attribute, transform each point by
  `group.matrixWorld`, give radial velocity, integrate in a `requestAnimationFrame` loop
  while `uFade` ramps the whole scene out. Camera dives simultaneously
  (`camTarget = start * max(.32, 1-dt*.9)`).

## DOM labels synced to 3D orbits

Labels live in the DOM (clickable, styled chips), hearts in the scene. Each frame:
local orbit pos → `heart.position.copy(local)` (rides the group's rotation) →
`v3.applyMatrix4(group.matrixWorld).project(camera)` → chip `left/top`. Depth from
`v3.z` drives chip opacity/scale/pointerEvents — chips behind the galaxy shrink, fade,
and stop receiving clicks. Do NOT add a `sin(t)` bob to label y — it reads as a bug,
not life.

## Pitfalls

- ShaderMaterial + `vertexColors:true` needs the geometry `color` attribute AND
  `varying vec3 vColor = color` in the vertex shader — missing either = black points.
- Surface shader-compile errors: after `renderer.compile(scene,camera)`, walk
  `renderer.info.programs` and print any `p.diagnostics` into an on-page box — a silent
  shader fail on the recipient's machine is otherwise a black page with no clue.
- `THREE.Points` in the same group as the thing they orbit must have positions set in
  LOCAL space; applying `matrixWorld` to the Points' own transform double-rotates them.
- 30k particles + additive blending runs fine on integrated graphics; 50k+ is a
  marketing number that just brightens the blob on a dark palette.
