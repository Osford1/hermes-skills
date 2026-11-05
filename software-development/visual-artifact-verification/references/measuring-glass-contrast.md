# Measuring text contrast over what is really behind the glyphs

A palette ratio is not a contrast measurement. Any surface that is translucent, blurred,
gradient-filled, animated, or painted by a canvas shows a *different* composite behind every
glyph, so the number that matters is the **worst** one. This is the recipe that produces it.

## Procedure

1. **Enumerate text runs, not elements.** Select the visible screen's text-bearing elements, skip
   any with `display:none` / `visibility:hidden` / `opacity < 0.05`, and keep only those that own a
   text node directly (`[...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim())`) —
   otherwise a wrapper is measured in place of the run that actually paints. Record
   `getComputedStyle(e).color` and `fontSize` **before** hiding anything; that colour is the ink
   you compare against.

2. **Make the ink transparent — never hide the element.** `visibility:hidden` and `opacity:0`
   also remove the element's own glass fill, rim, border and gradient, which is the very surface
   you are trying to measure against. Transparent colour leaves the whole box rendered and takes
   away only the glyphs:
   ```js
   e.style.setProperty('color', 'transparent', 'important');
   e.style.setProperty('-webkit-text-fill-color', 'transparent', 'important'); // else a -webkit rule still paints
   e.style.setProperty('text-shadow', 'none', 'important');                    // else the halo samples as background
   ```
   Note in the report that the shadow was disabled: the ratio is then the **no-halo worst case**,
   which is conservative — a halo in the real render only helps. Do not present it as if the
   halo had been counted.

3. **Sample line boxes, not the element box.** Take the rects from a `Range` over the element
   (`rg.selectNodeContents(e); [...rg.getClientRects()]`) and sample across each at 20 / 50 / 80 %
   of its width, at mid-height. The element's own box is often much taller than the ink — with
   `line-height > 1` the difference is a whole line — and its corners can sit on a neighbouring
   card, so a bounding-box sample measures a surface no glyph touches.

4. **Two phases when anything moves.** A background that drifts, blurs, or animates presents a
   different composite every frame, so one screenshot is one arbitrary frame. Capture the same
   screen twice, ~1.2 s apart, and take the worst across both. (A static background needs one.)

5. **Worst case per point.** Average a k=2 px neighbourhood at each sample point — a single pixel
   can land on a compression artefact or a hairline — then take the minimum ratio over every
   point and every phase.

6. **Compute WCAG in code**, never by eye: sRGB-linearise each channel
   (`c/12.92` below 0.04045, else `((c+0.055)/1.055)**2.4`), relative luminance
   `0.2126R + 0.7152G + 0.0722B`, ratio `(Lhi + 0.05) / (Llo + 0.05)`.

7. **Report three falsifiable numbers**, not an adjective: total samples, failure count, worst
   ratio — plus the per-screen worst, so the screen that actually changed is visible in the
   result. Run the shared evaluator — `scripts/verify-contrast-pixels.py` in the
   `offline-single-file-web-builds` skill — over a directory of captures: one JSON of runs plus
   one screenshot per animation phase. Do not write a second evaluator; that one is already wired
   to the contract above and gates on exit code.

8. **Scope the re-run to what you touched.** List the generator functions you edited and the
   states they feed. A background you did not touch is byte-identical and keeps its earlier
   numbers — say that explicitly, and never imply you re-measured a screen you did not.

## The ramp probe: proving a surface is translucent at all

A glass panel that actually renders as an opaque fill passes a contrast check and looks absurd
next to the rest of the page. Sample a vertical strip inside the panel and check the values
*vary*: a real translucent material moves with whatever is behind it, an opaque fill returns one
flat value. Run this whenever a material was just changed and the result looks suspiciously
even.

## Pitfalls

- **Two colours on one element.** `::before`/`::after` decorations, and
  `-webkit-text-fill-color`, can paint something other than what `color` reports. If a run
  measures oddly, check both before believing the number.
- **Never force a state on to measure it.** Toggling classes or `hidden` from the console shows
  a composite the artifact would have rebuilt on entry. Drive the real control — the app's own
  navigation function, or a click — for the reason in the main skill's "forcing a view visible"
  pitfall.
- **Record the viewport and capture at `deviceScaleFactor: 1`.** Blur radii and the sampling behind
  a glass layer are resolution-dependent, so a ratio measured at one viewport width is not the
  same measurement at another. Set the viewport explicitly and put it in the report.
- **A ratio that fails is a surface problem, not a glyph problem.** Fix it with a scrim, a darker
  ink, or a stronger backing behind the words. Adding a `text-shadow` shifts the problem instead
  of solving it — and it disappears from your own measurement the moment you disable it in step 2.
