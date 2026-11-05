# Pitfalls from a real build (scroll state, motion, contrast)

Found while verifying a Lenis-based one-page site in headless Chrome. Each one
rendered plausibly while being broken — the pixels could not tell you.

## 1. Position the page through the site's own scroll API
A smooth-scroll library (Lenis etc.) keeps its own animated value. A native
`window.scrollTo()` moves the DOM but leaves that value stale, so the library drags
the page back on the next frame — and the capture you take after the jump is
whatever the library decided. Call the library's API (`lenis.scrollTo(y, {
{immediate:true, force:true}})`) so it adopts the position instead of fighting it.

Watch for top-of-page rules: a site that treats `scrollY < 6` as "go back to the
intro" will reinterpret your jump to 0 as a user gesture. Drive to y=0 only where
the test means it.

## 2. Reduced motion skips animation, not states
A state machine fed by animation callbacks dead-ends if the reduced-motion branch
calls the callback directly. Real case: `if (reduced) { setTimeout(finish, 500);
return; }` where `finish()` was `expand()` — and `expand()` early-returned unless
state was `framed`. Under `prefers-reduced-motion: reduce` the page stayed in
`opening` forever: cover up, scroll library never started, nothing clickable. An
unscrollable site for exactly the users who asked for less motion.

Fix shape: snap the animated value to the target the animation would have reached,
then enter the next state normally.

## 3. Verify the state machine, not only the picture
A stalled state photographs perfectly. Read state/scroll/overflow numbers back from
the page (`Runtime.evaluate`) at each step, and expose a small read-back seam from
the app under test (state, max scroll, transform, internal scroll offsets).

## 4. A "quiet" colour token can sit below the legibility floor
Measure every token used as small text, not just the body copy. Real case: a
"faint" tier at `#4A4F57` measured 2.0–2.4:1 across 24 runs. The fix is not always
the brighter token — on a near-black ground the usable text range can be ink
(~17:1) → muted (~5.2:1) → floor (~4.5:1), with no room for a third dimmer tier.
Hold the quiet tier with size, tracking and case instead.

Check who else uses the token before changing it: dead stub markup can hide that a
token is shared with live rules in an earlier, already-verified stage.

## 5. Take text-on shots as well as text-hidden ones
Contrast tooling needs a shot with the glyphs hidden (sample the background through
the text). Those shots are useless for judging layout, hierarchy or "does it look
finished" — take a second, text-on set for the visual read.

## 6. Know your harness's own flags before judging an affordance
Headless Chrome launched with `--hide-scrollbars` shows no scrollbar, so "there is
no scroll cue" may be your own flag, not the page. Check the CSS (`overflow-y`,
scrollbar rules) before reporting it as a finding. Same for emulation: touch,
device metrics and forced colours all change what renders.

## 7. Distinguish a defect from a framing choice
The capture crop is not the design. A kicker "clipped at the top edge" was the
capture's scroll offset, and a "misaligned column" was deliberate optical centring —
both rows measured centred on one axis to the pixel. When an eye-read flags
something, measure the element rects before acting on it.
