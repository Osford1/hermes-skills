---
name: web-design-recipes
description: Use when building HTML pages, frontends, or animations.
---

# Web Design Recipes

Design-token + motion-recipe system distilled from a live teardown of 14 award-grade HTML sites (HubSpot blog, "14 Stunning HTML Websites"). Goal: every frontend build starts from measured, proven systems — not from scratch.

## Full reference

`C:\Users\<you>\OneDrive\Documents\<archive>\Projects\Web-Design-System\Reference\hubspot-html-websites-teardown.md`

Read it when a build needs palettes, type pairings, or a specific recipe. Demo implementation: `Projects/Web-Design-System/Deliverables/WebApps/motion-lab-demo/index.html`.

## Mandatory boilerplate (fixes alignment drift)

Every HTML file starts with:
1. `*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }`
2. A `:root` token header: palette, type scale, spacing on a strict 4px grid, radii, easing — all as CSS vars.
3. **Flex/grid for ALL alignment.** Never magic margins, never baseline-dependent inline layouts.
4. Explicit `line-height` on body (1.5–1.6) — critical when mixing Chinese + Latin text (different baselines/x-heights).
5. One file when possible (inline CSS/JS, CDN imports).

## Measured palettes (ready to paste)

| Mood | Tokens | Source |
|---|---|---|
| Sci-fi terminal | `#000` bg, `#fff` text, `#0f0` accent, `rgba(255,255,255,.5)` lines | Earth Eclipsed |
| Dev-doc discipline | `#d30001` brand, `#261b23` ink, `#5a5153` body, 8px radii, 18px body | Ruby on Rails |
| Editorial neutral | `#efece6` bone bg, `#b7a78f` taupe | Packabo |
| Warm empathy | `#f7c455 #d29112 #dd4f5d #fcf0ea` | Neurodiversity |
| Agency red/black | `#f35422` on `#050505` | DD.NYC |
| Calming pastel | `#b9e7de #ffd05b #40d39c #b9e2f8 #ffc5c8` on `#32373c` | Guía Cardíaca |
| Video-energy dark | `#f32a72` + `#6b41f6` on `#251b4a` | IVS.tv |
| Day/night duo | `#feb19a` ⇄ `#9d8cd5` (two CSS vars, toggle swap) | Pencilvania |

## Motion recipes (pick cheapest that achieves the effect)

1. **CSS-only hovers/transitions** — always.
2. **Video hero** — `<video autoplay muted loop playsinline>` + gradient scrim for text legibility + pause control (accessibility).
3. **Scroll reveals** — IntersectionObserver + `translateY(32px)` + expo easing; no library needed.
4. **Single-var state machine** (best architecture pattern): one CSS var as the size axis (e.g. `--planet-size`), flipped by `data-state` classes, 2s transitions. No keyframes, no per-property JS.
5. **Cursor lerp** — `pos += (mouse - pos) * 0.12` on a rAF loop; dot instant + ring trailing; expands on hover targets. Low prominence only.
6. **SVG scrollytelling chapters** — illustration as structure, full-screen scenes.
7. **Audio-reactive canvas** — Web Audio `AnalyserNode` → particles; pause on `visibilitychange`.
8. **Draggable world / lateral-only narrative** (`scroll-snap-type: x mandatory`) — only when the concept demands it.

### Vendored libraries for rungs 3-4 (offline, no npm)

`_Knowledge/vendor/` carries pinned copies of **GSAP 3.15.0** (`gsap/`, core + 10 plugins) and
**Lenis 1.3.26** (`lenis/`), with a `README.md` recording versions and licence, and a
`selftest.html` that proves the whole set loads from disk. Plain `<script src>` tags — no build
step, works from `file://`, so single-file deliverables don't depend on a CDN.

Use GSAP only when CSS and IntersectionObserver genuinely can't express the effect, and Lenis only
when the *feel of scrolling itself* is the point. Procedure, plugin-registration traps, the
Lenis+ScrollTrigger handshake and the verification loop: `references/gsap.md`.
The inventory with the reasoning, including what was rejected and why:
`_Knowledge/web-animation-toolkit.md`.

## Design principles from the teardown

- **Restraint is the luxury signal** — the most expensive-looking sites (Packabo, RoR) use the fewest effects. One or two motion moments per page, not constant animation.
- **One concept per site** — a single idea executed fully beats ten half-ideas.
- **Type discipline** — one body size dominates (18px), display steps ≥2.5× body, mono font reserved for code/data.
- **Exactly one Easter egg per site** — state-flipping (e.g. hidden day/night mode), behind an inviting plain control ("Don't press this heart" → ♡/♥).
- **Palette = emotion** — pick the feeling first, tokens second.
- **Accessibility** — pause-able video, no autoplay sound, respect `prefers-reduced-motion`.

## Chat-widget builds (Hermes desktop)

When the deliverable lives inside chat: transparent background, theme tokens (`var(--foreground)`, `var(--accent)`, `var(--card)`, `var(--border)`, `var(--muted-foreground)`), no page chrome, flush left, render via `::preview{file="..."}`. Give interactive widgets `data-hermes-send="prompt"` buttons so they can message back.
