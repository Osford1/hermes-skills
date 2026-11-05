# Motion assertions — what fails silently, and how to catch it

Every failure below produced **no console error and nothing visibly wrong**: a movement that
never happened, or a value that settled somewhere the code did not intend. Motion cannot be
verified by looking at the page, because a tween that never ran looks exactly like one that did.

## The general shape

1. Read the geometry **immediately after the trigger** (0–50 ms) — the only chance to see the
   starting state.
2. Read it again **in flight**.
3. Read it again **at rest**.

"Early = the source box, rest = the target's own box" is the proof. Three samples is enough.

Keep each scripted step short and sleep *between* calls: a single evaluate that waits for several
seconds gets cut off, and the timeout arrives looking like a page failure instead of a limit.

## Per mechanism

**CSS transition on an element that was `display: none`**
- Fails: the property lands on its final value in the frame the element is first rendered; the
  transition never plays.
- Cause: an element that has just come from `display: none` has no previous computed value to
  transition *from*.
- Fix: set the hidden state, force a reflow (`void el.offsetHeight`), then apply the visible state on
  a later frame — double `requestAnimationFrame` when children are staggered.
- Assert: sample at ~30 ms; the value should be part-way, not final.

**`prefers-reduced-motion` — delays are separate from durations**
- Fails: zeroing the durations still leaves a staggered entrance, because the stagger lives in
  `transition-delay: calc(var(--i) * var(--line-step))`.
- Fix: zero the delay tokens too, and switch CSS animations off outright (`animation: none`) rather
  than relying on a 0 ms duration.
- Assert: with the preference emulated, every element is at its final state within ~70 ms.

**JS timing that has to match CSS**
- Read the timings back out of the CSS (`getComputedStyle(root).getPropertyValue('--dur-line')`) so
  the token block is the single source of truth. A timer guessed separately drifts from the
  animation it belongs to, and a reduced-motion rule then only changes one of them.

**A transition that is supposed to be a scroll**
- Fails: the smoothing library finds nothing to scroll because the container is not actually
  taller, so the "scroll" completes instantly. Nothing errors.
- Assert: the distance travelled equals the container height, and the document really was taller for
  the duration of the move.

**GSAP Flip between two different elements**
- Fails: giving the source and the target the same `data-flip-id` animates nothing when the source
  node is still in the DOM (only `display: none`) — Flip matches the original element, finds it
  collapsed, and has nothing to move.
- Fix: read the source rect *before* the layout change, `gsap.set` the target into that box
  (`x`/`y`/`scaleX`/`scaleY`, `transformOrigin: 'top left'`), `Flip.getState(target)`,
  `clearProps: 'transform'`, then `Flip.from(state, { absolute: true, scale: true })`.
- Assert: the target's box at 0–50 ms equals the source's box, and at rest equals its own. Then grep
  the element's inline style — a flight that did not clean up leaves `transform-origin` behind.

**GSAP Draggable — an infinite track**
- Fails: `inertia: true` together with a `modifiers` wrap lets the throw animate past the wrap
  (measured: `x` reached −1231 against a range of [−1040, 0)), leaving a gap at the end of the track.
- Fix: wrap in `modifiers` for the drag itself, and settle in `onDragEnd` with a tween on the
  Draggable's own `x` (`gsap.to(this, { x: wrapX(...) })`).
- Assert: at rest, `x` is an exact multiple of the item pitch and inside the wrap range.

**GSAP InertiaPlugin**
- Fails: `gsap.to(el, { inertia: { x: 0, y: 0 } })` does nothing at all — no error, the element stays
  exactly where it was. The form that works keeps the end values in the tween:
  `{ x: 0, y: 0, inertia: true }`.
- Assert: read the property after the release; it must be back to 0.

**Pointer-reactive (magnetic) elements**
- Fails twice over: measuring the pull against the element's own moving box feeds the offset back
  into itself and oscillates, and on a touch screen there is no hover to pull towards at all.
- Fix: capture the resting box on `pointerenter` while zeroing the transform, clamp the
  displacement, and build the effect only behind `matchMedia('(hover: hover)')`.
- Assert: displaced under the pointer and within the clamp, exactly 0,0 after it leaves.

**Cloned sets (carousels, infinite rows)**
- Fails: cloned nodes carry no listeners, so half the visible items do nothing; and duplicated state
  attributes (`aria-current`) make the chosen item count twice.
- Fix: delegate clicks on the container rather than per item; mark duplicates `aria-hidden="true"`
  and `tabindex="-1"` and strip the state attributes from them.
- Assert: click a *visible* item and confirm the state actually changed; count `:not(.is-clone)`
  separately from the duplicates instead of counting everything.

**Layout that grows mid-transition**
- Fails: a document that is momentarily taller than the viewport summons a scrollbar and shifts
  everything sideways ~15 px for the duration.
- Fix: `html { scrollbar-gutter: stable }`.
- Assert: a fixed layer's width (or one anchored element's box) at rest, mid-transition and after —
  all three identical.

**Reduced motion, the whole page**
- Assert the flow still *completes* with every effect switched off. A static branch that strands the
  user is a worse defect than the animation it replaced.
