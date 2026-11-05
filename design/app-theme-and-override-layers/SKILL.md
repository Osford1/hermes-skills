---
name: app-theme-and-override-layers
description: Use when theming or overriding a host app's UI.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [design, theming, css, override, glassmorphism, contrast, verification]
    category: design
    related_skills: [apple-design, glassy-panel-design, file-organization, inspecting-hermes-desktop-dom]
---

# App theme and override layers

The class of work where the app is not yours to rebuild: a browser extension, a packaged
Electron app, a vendor web UI. You audit it with measured numbers, then ship the fix or the
theme as an **override layer** dropped into the app's own extension point — so it survives
updates and reverting it is deleting one file. This skill covers the extension point, the
CSS-authoring traps that fail silently, the material thresholds that make translucency read,
and how to prove any of it on rendered pixels.

The *design spec* (CIE L\* ladder, material table, palette validator) lives with the user's
notes at `_Knowledge/glassy-panel-design-metrics.md` and the `glassy-panel-design` skill.
CDP mechanics for the Hermes desktop app live in `inspecting-hermes-desktop-dom`. This skill is
the delivery-and-verification half; do not restate those two.

## When to Use

- "Make this app look like <palette / reference>" on an app you did not write.
- "This interface is hard to read" — audit first, then ship the fix as a layer.
- Any change that must survive the host's updater, or be reverted by the user in one step.

**Not for:** apps whose source you own and can rebuild — edit the source. A source edit to a
packaged install is reverted by the next updater run, which is exactly the failure this class
exists to avoid.

## Procedure

1. **Find the extension point, cheapest first.** User-scoped plugin/theme directory → app
   setting (custom CSS/theme field) → source. A user-scoped directory that the app loads and
   hot-reloads is the right default: no build step, no install-tree edit. Record the door in
   the deliverable so the user can find it later.
2. **Scope every rule to one attribute.** `:root[data-theme='x']` / `:root[data-layer='on']`
   for every selector. That one choice makes the layer revertable (delete the file, or flip
   one attribute) and guarantees it cannot bleed into another theme.
3. **Author the layer** (read the traps below before generating any CSS):
   - An **unlayered** injected `<style>` beats the host's `@layer base` tokens with no
     `!important`.
   - Clamp utility micro-type by exact class string: `[class~='text-[0.65rem]'] { font-size: … }`
     — the attribute selector matches the literal class, brackets included. A host with a long
     Tailwind arbitrary-value tail (100+ call sites under 12 px) is fixed in one rule set this
     way; raising a root font-size instead drags every `rem` layout value with it.
   - Drive the host's **process-token variables** (control sizes, radii, surface tokens, text
     tiers). Per-component `h-5`/`h-6` sizes are not safely overridable — leave those to the
     host.
4. **Collapse stacked surface alphas** before tuning any leaf alpha. Hosts nest painters
   (bar 72 % over a wrapper 36 % over the content surface 36 %), and they multiply:
   `1 - Π(1-a)` = 88 % paper, which is why no token change alone can read as translucent.
   Clear the ancestors that *contain* the content surface (leave the bars) and recompute the
   composite; 36 % is the dark target.
5. **Re-base the text tiers per appearance** (see the pitfall below). The host's tiers are
   usually alphas of one foreground tuned against a dark canvas, and they fail over tinted
   glass in light.
6. **Answer the preferences**, always all three: `prefers-reduced-transparency: reduce` →
   surfaces solid, blur and bloom off; `prefers-contrast: more` → solid, bloom off, strokes at
   full strength; `forced-colors: active` → boundaries from `CanvasText` / `GrayText`.
7. **Verify before you claim** (below), then file the deliverable with its revert path.

## What makes translucency read (thresholds, not taste)

- **Put a gradient behind it.** A tint or blur over a flat fill is a flat fill; the ramp across
  a panel measures 0.000 and the result reads as an opaque theme. Build the bloom first.
- **The bloom is scale-bound.** A recipe tuned for a 320–420 px panel spreads into a uniform
  wash at ~1300 px. Anchor radials to the corners with tighter radii and higher alphas, and add
  **one window-spanning diagonal wash** — the diagonal is what carries a ramp through the middle
  of a large canvas, where corner radials never reach.
- **Surface alpha has a threshold:** ~36 % paper on a dark canvas reads and still holds ~14:1
  for text; on a light canvas the same card needs ~88 %, or the bloom looks like staining.
- **The tallest surface needs the lightest fill.** A full-height rail at the card alpha measured
  a 0.0000 ramp — a whole column with no glass in it. Give the rail more field than a card gets
  (74 % light / ~50 % dark).
- **Separate surfaces with a hairline and depth, not with value.** Paper sits only 4–8 L\* above
  the canvas: the 1 px edge (`color-mix(paper 50%, line)`) and a two-part shadow (inset top rim
  + wide soft depth) do the work. Solve the hairline alpha against the fill it sits on rather
  than picking one — a 3:1 edge over the shell needed `line` at 78–95 %.
- **One accent focus ring**, 3 px at ~26 % — never a second outline.

## Pitfalls

- **Two override layers at equal specificity resolve on DOM order.** A peer layer scoped
  `:root[data-a='on']` silently beat one scoped `:root[data-theme='x']` because its `<style>` was
  appended later. Raise the layer that must own a token (`:root:root[data-theme='x']`) instead of
  scattering `!important`, and name the owner of each token in the file header.
- **Never redeclare the host's own custom-property names in your layer.** Writing
  `--foreground: #1b1b1f` (or any host token) into your `:root` does not create a fallback: your layer
  is injected after the host's and ties on specificity, so the later declaration *replaces the host's
  live theme* — and it fails silently, because the host still reports its own tokens as set, so a
  "did my layer land?" check passes while the appearance is wrong. Alias instead, host variable first
  with the fallback inside the `var()`: `--layer-fg: var(--foreground, #1b1b1f);`. The same authoring
  choice breaks any feature test that detects the host by reading one of those names (`--foreground`
  non-empty means "host present" — untrue once you define it yourself).
- **Generated CSS fails silently; verify the rule landed, not the file you wrote.** A `{{`/`}}`
  pair left behind by templating makes a rule unparseable and the browser drops it with no error;
  concatenating a comma-separated selector list with a descendant (`A, B` + ` body`) makes the
  first selector the root element, so the whole block lands on `<html>`. Check
  `styleEl.sheet.cssRules.length` plus one computed value after every edit.
- **Host text tiers do not survive a light translucent appearance.** Alphas tuned against a
  near-black canvas measured 3.29:1 and 2.94:1 over tinted glass in light (the same tiers were
  4.8:1+ dark — they were never neutral). A theme must carry its own ladder per appearance.
- **Only a pixel ramp proves glass.** The palette can pass its validator, the tokens can equal
  the design, and the panels still be flat fills. Sample a text-free column inside a panel,
  compare top against bottom, and report the Δluminance.
- **`backdrop-filter` on a giant content surface** costs frames for a backdrop that is already a
  gradient. Keep blur for floating controls and overlays.
- **Do not read contrast off the token table.** Resolve each colour through a canvas (or sample
  the rendered pixels) before computing WCAG — `color-mix()`, `oklab()` and alpha compositing
  over translucent surfaces are not readable as written.
- **Never present an unapplied change as applied.** If the layer could not be verified in the
  user's own window, say which part is measured and which part is expected.

## Verification

1. **Authoring proof:** rule count up, and one computed value changed to the value you intended.
2. **Visual proof:** a pixel ramp (Δluminance across a panel) plus a screenshot of both
   appearances.
3. **Contrast proof:** tier colours composited over the *measured* surface, reported as numbers
   (text ≥ 4.5:1, boundaries ≥ 3:1).
4. **Live proof:** when the user's window has no debug port, have the layer's entry point write a
   receipt through the host's scoped storage and grep for it in the app's local storage — that is
   what proves the running app loaded it.

## Deliverable shape

One override file (plus its notes) filed per the `file-organization` skill: the layer itself,
notes carrying the palette/contrast/material tables and how to dial them, screenshots of both
appearances, and the revert path (exact UI path or the file to delete). Keep the change set to
one file plus one attribute so "revert" is a single action.

Depth file: `references/glass-material-recipe.md` — variable map for driving a host's surface
tokens, the working bloom values, and the measured thresholds that passed.
