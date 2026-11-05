# Interactive teaching widgets (HTML in chat)

Use when a concept is spatial or temporal and a static explanation won't land (state-space
maps, offsets, accumulation, integration order, switching manifolds, phases).

## Delivery
- Write the HTML, then put `::preview{file="C:/.../name.html"}` alone on its own line.
- **Theme vars only** for color: `var(--foreground)`, `var(--muted-foreground)`, `var(--accent)`,
  `var(--border)`, `var(--card)`. Do NOT set a background/font/margins — the frame themes it.
  Content flush-left, no centering wrapper (it otherwise measures full-bleed). Apply them through CSS
  classes rather than copying computed colours into attributes: `var()` works directly on SVG
  `fill`/`stroke`, so the theme stays live and the file still reads standalone.
- **SVG, not canvas, when the payload is geometric** — lines, vectors, dashed families, arrowheads,
  labels. The traps that cost time there (pointer mapping through the border box, a drag handle that
  pivots on the state it edits, label-vs-handle clearance) are collected in the
  `interactive-concept-widgets` skill.

## Canvas specifics
- Set **fixed `width`/`height` attributes** + `canvas { width:100% }` CSS. Do NOT read
  `getBoundingClientRect()` at init — a `display:none` tab returns 0 and breaks sizing.
- Fetch theme colors for canvas strokes/text once at load:
  `getComputedStyle(document.documentElement).getPropertyValue('--accent').trim()`. Canvas
  can't read CSS vars directly.
- Tabs: toggle `.active` on the button + the matching `.panel`; keep **all** canvases
  animating via a persistent `requestAnimationFrame` loop regardless of which tab is visible,
  so a panel is already drawn when first shown.
- Split signals into stacked plot areas (shared time axis optional); use small `series`/
  `fillUnder` helpers keyed to plot coords.

## Verify before delivering (a widget that renders but throws is worse than none)
- In `browser_exec`: `new_tab('file:///' + path.replace('\\','/'))`; then `wait_for_load()`.
- Assert each canvas has non-zero pixels: `getImageData` → count non-zero RGB; confirm > 0.
- Confirm no thrown JS error (wrap state reads in try/catch and print).
- Hit-test at least 2 tabs to confirm both draw.
- **Expose a probe hook.** Attach the drawing-independent logic to `window.__w = {blocked, state, set, ink, …}` so the probe calls the real math instead of scraping pixels.
- **Check the OPENING state is valid, not merely drawable.** A configuration-space widget that opens with the arm already in collision teaches the wrong lesson on first look; verify the default state and make the HTML's defaults match what you checked.
- **Drive real input, not just a state setter.** Dispatch a synthetic `pointerdown` at the pixel that *should* map to a known value and assert the state equals it (e.g. the pixel for θ₁=90°, θ₂=200° must yield exactly those angles), and assert the marker's pixel turns the collision colour inside a forbidden cell. That verifies the coordinate mapping, which a state setter bypasses.

## Linked views: one object, two spaces (what landed for configuration space)
- **Two panels, one state.** Show the object where it physically is (workspace) beside the space it must be *planned* in (joint/state space), both draggable — dragging the marker in the abstract space and watching the robot obey it is the most convincing single move; sliders alone don't land it.
- **Design the elements after the physics.** Place the obstacle by what forbidden region it produces (a full-height stripe = downstream joints are powerless to help; a curved band = some joint does help), not by what looks tidy in a sketch.
- **Name the two spaces inside the widget**, including the trap: one of the red shapes is in the room, the other is not. Repeat that warning in the reply.

## Honesty & correctness
- **Label a constructed demo as illustrative.** If the widget shows a *mechanism* using a made-up
  schedule rather than a solved or measured result (e.g. a chattering control whose switch times
  are chosen to converge), say so IN the widget — never let a schematic read as computed output.
- **Verify the phenomenon, not just the pixels.** Recompute the demo's math (in-page or separately)
  and confirm it produces the effect — the trajectory converges, the count accumulates. Non-zero
  pixels prove it draws, not that it demonstrates the thing.
