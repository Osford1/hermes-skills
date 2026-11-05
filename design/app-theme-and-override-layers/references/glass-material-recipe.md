# Glass material recipe for a host app

Companion to the SKILL.md procedure. Use it when the host's theme API carries colours only and
the material has to be delivered as a scoped stylesheet.

## Variable map (Hermes desktop app; transpose to the host's own tokens)

| Concern | Variables to drive |
|---|---|
| Field / canvas | `background-color` + `background-image` on `body`, `background-attachment: fixed` |
| Bypass neutral mixing | `--theme-mix-chrome/sidebar/card/elevated/bubble: 100%` |
| Bars (titlebar, status) | `--ui-bg-chrome` |
| Rail | `--ui-bg-sidebar`, `--sidebar-edge-border` |
| Thread / cards | `--ui-bg-editor`, `--ui-chat-surface-background`, `--ui-widget-surface-background` |
| Overlays | `--ui-bg-elevated` |
| Chips / input | `--ui-bg-card`, `--ui-bg-input` |
| Edges | `--ui-stroke-primary/secondary/tertiary/quaternary` |
| Depth | `--shadow-nous`, plus a rule on the named surfaces |
| Radii | `--radius-scalar` (one notch) + explicit 18 px overlays / 20 px composer |
| Type scale | `--conversation-text/tool/caption-font-size`, `--conversation-line-height` |
| Text tiers | `--ui-text-tertiary/quaternary`, `--conversation-scaffold-text/meta` |

## Values that read as glass (light / dark)

| Element | Light | Dark |
|---|---|---|
| Bars | 94 % paper | 72 % paper |
| Rail | 74 % shell | 52 % shell |
| Thread, cards | 88 % paper | 36 % paper |
| Chips, widgets | 92 % paper | 45 % paper |
| Composer | 90 % paper | 44 % paper |
| Overlays | 92 % paper | 76 % paper |

Recipes tuned for a small panel must be re-anchored at window scale (see SKILL.md). Working form
for ~1300 px — corner radials plus one diagonal that crosses the middle:

```css
/* dark; light uses 14 % -> 5 % on the diagonal and 26 %/16 %/8 % radials */
linear-gradient(157deg, color-mix(in srgb, accent 36%, transparent) 0%,
  color-mix(in srgb, accent 11%, transparent) 42%, transparent 74%),
radial-gradient(46% 42% at 3%   -8%, color-mix(in srgb, accent 62%, transparent), transparent 62%),
radial-gradient(42% 38% at 105% 110%, color-mix(in srgb, accent 44%, transparent), transparent 64%),
radial-gradient(28% 26% at 90%  38%, color-mix(in srgb, accent 22%, transparent), transparent 66%);
```

## Measured thresholds that passed

| Check | Result |
|---|---|
| Panel ramp, dark (text-free column, top->bottom) | `(22,43,45) -> (16,25,28)`, dLum **0.0120** |
| Panel ramp, light | dLum **0.0049** — deliberately quiet; light separates by hairline |
| Rail ramp | 0.0046 dark; **0.0000** at the card alpha in light |
| Text tiers after re-basing | dark 15.1 / 9.5 / 5.4 / 4.8 / 4.8 :1 - light 10.2 / 5.7 / 5.1 / 5.1 / 5.1 :1 |
| Same tiers before re-basing, light | 10.3 / 5.8 / **3.29 / 2.94** :1 |
| Composite paper alpha under the content surface | **88 %** before clearing the intermediate painters, **36 %** after |
| Solved hairline alphas | sidebar edge `line` 78-80 % of shell (dark) / 95 % (light); bubble edge `accent` 62-65 % / 76-77 % |
| Palette contract | text >= 4.5:1, boundaries >= 3:1, every pair in both appearances, validated by script to exit 0 |

## Tier re-basing

Text tiers are alphas of one foreground over the surface, so solve the alpha against the surface
it actually composites over, per appearance (dark 50-58 %, light ~70 % for the two lowest tiers
cleared 4.5:1 on the palettes measured here). Re-solve rather than reuse when the canvas L*
changes — a warmer or darker canvas moves the floor.
