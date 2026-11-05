# Design system — inherited from the precedent chart family

The master chart and every generated zoom page share one design system. Both were cloned from the
family precedent in the vault (`GBP-DualArm/paper2-structure-flowchart.html`): inherit its CSS and
geometry grammar, but write a fresh accessible `<svg>` opening — the installed precedent predates the
gate and fails it.

## Palette (CSS custom properties, repeated in the SVG as literals)

| Token | Value | Used for |
|---|---|---|
| `--paper` | `#2d3142` | page and canvas background |
| `--paper-2` | `#393e53` | node / box fill |
| `--ink` | `#f5f5f5` | headings, node titles, box strokes |
| `--muted` | `#bfc0c0` | body text, canvas body lines |
| `--soft` | `#8e98ac` | eyebrow, sub, tags, chip text |
| `--rule` | `rgba(245,245,245,0.12)` | hairlines, card borders, dashed boxes |
| `--accent` | `#f08a59` | the load-bearing path: focal node, loop, arrows in the pivot |
| `--accent-tint` | `rgba(240,138,89,0.10)` | focal node wash |

Hover state: chips and link rules go to the accent, chip text to ink — so every clickable thing
announces itself on hover.

## Type

| Role | Family | Size |
|---|---|---|
| page body | Geist, system-ui fallback | 14px / 1.6 |
| title `h1` | Instrument Serif | 38px |
| eyebrow, sub, footer | Geist Mono | 9–9.5px, letter-spacing 0.04–0.18em |
| canvas body lines | Geist Mono | 9px |
| canvas node titles | Geist, weight 600 | 12px |
| node tags, chips | Geist Mono | 7–8.5px, letter-spacing 0.08–0.16em |

The only remote reference any page may carry is
`https://fonts.googleapis.com/css2?family=Geist...&family=Geist+Mono...&family=Instrument+Serif...`
(the gate rejects every other remote `<link>`/`src`).

## Geometry constants

```
W, MARGIN = 880, 40        # canvas width, margin
CW        = 800            # content width: every box spans x = 40 .. 840
CHAIN_X   = 200            # vertical spine inside the canvas
LOOP_X0, LOOP_X1 = 260, 340  # accent self-loop attach points
LINE_PITCH = 20            # baseline-to-baseline inside a band
GAP, GAP_LOOP, ROW_GAP = 40, 64, 24
```

Canvas height is computed from the plan (master `880×1700`, children vary: 592–1556 in the worked
set), so a page is exactly as tall as its content.

## Font metrics — the numbers the overflow check uses

Per-character advance in px, measured in-browser:

| Constant | Value | Applies to |
|---|---|---|
| `MONO9` | 5.4 | 9px mono body lines (the wrap/limit math) |
| `TITLE12` | 6.65 | 12px node titles |
| `MONO85` | 5.1 | 8.5px mono labels |
| `TAG8` | 6.2 | 8px mono tag text (tags are wide-glyph, don't reuse `MONO9`) |
| `MONO_ADV` | 5.6 | 8px mono **with** 0.06em tracking (chip/legend item widths) |

Line ceiling: `(box_width - 32) / per_char`. For a full-width band (800) that is ~142 characters, and
in practice ~138 for a line starting at `x = 56`. **Verify with the pixel audit, not with this table** —
the table tells you where to look, `getBBox()` tells you the truth.

## Page anatomy

```html
<html lang="en">
  <head> meta, <title>, the one allowed font stylesheet </head>
  <body>
    <div class="wrap">
      <p class="eyebrow">…</p>
      <h1>…</h1>
      <p class="sub">…<br>…</p>
      <hr class="rule">
      <div class="canvas">
        <svg viewBox="0 0 880 H" role="img" aria-labelledby="<slug>-title <slug>-desc">
          <title id="<slug>-title">…</title>   <!-- first child: the gate checks this -->
          <desc  id="<slug>-desc">…</desc>     <!-- second child -->
          … canvas …
        </svg>
      </div>
      <div class="cards"> <article class="card"> … </article> … </div>
      <footer> provenance lines </footer>
    </div>
  </body>
</html>
```

The `<svg>` must be the page's first SVG-bearing element, title-first, with ids derived from the slug
(`<slug>-title`, `<slug>-desc`) and `aria-labelledby` pointing at them.

## Canvas anatomy (master and children alike)

- **Header band**: the page's own anchor chip top-left; a label `ZOOM 3 OF 8 · §3.1–3.2 · <name>`
  beside it; top-right, right-aligned, the return sentence `re-enters the master chart at §3.1–3.2`.
- **Spine**: `chain` bands down the canvas, connected by short vertical connectors; a band carrying
  `focal` gets the accent-left treatment; a band carrying `chip` gets a chip in its top-right corner.
- **Rows**: side-by-side boxes below the spine, entered by an arrow when `incoming` is set.
- **Hand-off band**: a solid terminator box (`ZOOM BACK OUT`) plus a dashed box titled
  `NEXT ZOOMS — one concept at a time` listing 2–3 forward links, each marked built or still to build.
- **Legend**: items wrap into rows; `legend_note` sits on its own row beneath them.
- **Footer**: monospace provenance lines, including where every value on the page was read from.

## Chip anatomy (the handle — identical on master and children)

```html
<a class="zlink" href="<target>.html"
   data-hermes-send="Open <topic> zoom Z4 — §3.3 <what it covers> (<relative path>)">
  <title>open zoom chart Z4 — §3.3 — <what it covers></title>
  <rect x="…" y="…" width="36" height="24" rx="3" fill="transparent"/>   <!-- hit area ≥24px tall -->
  <rect class="chipbox" x="…" y="…" width="24" height="12" rx="2"
        fill="rgba(142,152,172,0.08)" stroke="rgba(142,152,172,0.75)" stroke-width="0.8"/>
  <text class="chiptxt" x="…" y="…" font-size="7" fill="#8e98ac"
        text-anchor="middle" letter-spacing="0.08em">Z4</text>
</a>
```

Three things make the chip a handle rather than decoration: the `<a href>` (works as a file link), the
`data-hermes-send` prompt (clicking it in the Hermes preview asks for the zoom), and the `<title>`
(the tooltip names the destination). The hit rect is 36×24 so the 24×12 badge is comfortably clickable.
