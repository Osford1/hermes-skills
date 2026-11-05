# Procedural canvas fields (tiles, fog, depth, parallax)

For backdrops a CSS gradient cannot fake: a cloud sea, a fog bank, a drifting particle field. §2.4
of the main skill gives the one-line version (pre-render tiles, blit twice per frame). This is the
depth: keeping it seamless, keeping it *tunable*, and the fixes for a field that looks like a pile
of spheres.

## Architecture

- **Two stacked full-bleed canvases whenever two fields cross-fade** (cloud sea → fog bank). One
  context cannot fade two fields independently; two layers can be cross-faded from scroll position
  or a scene change, each with its own opacity.
- **Build once, blit always.** `makeFieldTile(w, h, seed)` renders the whole static field into an
  offscreen canvas at build time and on resize; the rAF loop then does `drawImage` (two calls per
  layer) with the current offset. Per-frame cost stops depending on how many hundreds of elements
  the field contains. Rebuilding the tile per frame is the version that stutters.
- **Take an explicit `seed` and use your own PRNG.** `Math.random()` in a field builder makes every
  run a different artifact, so two builds cannot be compared — which kills the A/B loop you need to
  tune it (see `visual-artifact-verification`, "when the change is a dial, not a defect").
- **Expose the builder and the layer state on `window`**, so the verification seam (§4.3) can read
  real numbers instead of inferring them from pixels: a test calls
  `makeFieldTile(1944, 900, 11).toDataURL()` to diff two versions of the field at one seed, and
  reads drift rate, parallax offset and the reduced-motion flag directly. A top-level `function`
  declaration in a classic script is already global — nothing has to be wired up.
- **`prefers-reduced-motion` means do not start the loop at all**, and make that state readable so
  the check is observable rather than assumed.

## Tile seams

- Blit the tile at `x - w` and `x` so the field is horizontally continuous — which only works if the
  tile itself is seamless, or the join shows as a vertical band every repeat.
- **Blurring a tile fades its own edges**, because the filter samples beyond them; bake a blur into a
  repeated tile and you get a seam at every repeat. Fix: lay the tile down three times across a
  canvas widened by ~4σ each side, apply `ctx.filter` to that composite, then copy out the middle
  copy. Verify by tiling the result twice in a scratch canvas and looking for a band.
- **`ctx.filter` support**: assign and read back (`ctx.filter = 'blur(4px)'; if (ctx.filter !==
  'blur(4px)') …`). An engine that ignores it leaves the tile merely unsoftened — graceful, but it
  means the field's whole look must not depend on the blur alone.

## A field that looks like a pile of balls

A radial-gradient fill is a sphere, and "ball-like" is usually three things at once, worth fixing
as a set: **separation** (sky visible between masses), a **specular cap** (a bright highlight near
 the top of the body), and **roundness**.

Order of impact: remove the specular (spread the light wide at roughly a third of its alpha) →
overlap the masses so they read as one deck → flatten the shape. Shape alone does the least work.

- **Squashing a radial gradient *raises* edge energy.** Flattening compresses the vertical
  derivative while the horizontal one is untouched, so the field goes stripy rather than soft. It
  made the measurement worse, not better — flatten for shape, and soften with blur, alpha or
  overlap instead.
- To squash a gradient *and* keep its fade: `save(); translate(cx, cy); scale(1, squash);
  translate(-cx, -cy)` and fill a **circle**, so the gradient squashes with the shape. Filling an
  ellipse path with an unsquashed gradient clips the fade flat at the top and bottom edges.
- **Softening deletes the sense of depth too.** Restore it with one broad linear gradient across the
  field — a single smooth ramp cannot read as a shape, which is exactly why it is the safe way to put
  contrast back — rather than by re-adding edges.
- Blur radius as a fraction of tile height: ~**0.4 %** is the polish point, and once the structural
  changes are in, 0.4 % and 0.8 % measure nearly the same. If the number barely moves between them,
  the blur is not the mechanism and you are turning a knob that does nothing.

## Composition that reads as depth

- Rows descending toward the camera with radius growing per row (e.g. `0.03 → 0.22 × height`); a
  bright hazy band at the horizon (roughly 38–66 % of height, peaking at 50 %); the sky lightening
  toward it.
- A cross-fade between two fields tracks scroll (`clouds 0.97 → 0.00` while `fog 0.03 → 1.00`).
  Judge the transition frame itself as well as both endpoints — the midpoint is what people see.
- Keep the frame's large-scale range measurable (band-mean profile across the height) so "it went
  flat" is detectable in the same run as "the balls are gone".

## Pointer parallax on a canvas layer

- **Chase beats snap**: `t += (target - t) * (1 - exp(-dt / tau))` with `tau ≈ 150 ms`, plus a depth
  split between layers (near field 1.0, far wisps ~0.34). A snap carries no depth cue at all.
- Keep the sweep small — roughly 3–4 % of each dimension at the extremes.
- **Overscan the layer by ~8 % (±4 %)** so the whole sweep stays inside the drawn field: cheaper
  than padding every tile, and it leaves the horizon exactly where it was.
- Exclude anything "at infinity" (sun, moon) from the parallax, and disable the whole mechanism
  under `prefers-reduced-motion`.
- Measure it as a pixel shift with a same-position control: a field that moved ~100 px while the
  control read ~0 px is the proof, and a null result on an unstructured row (haze, sky) is expected,
  not a failure.
