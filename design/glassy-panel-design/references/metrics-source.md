# Where the numbers came from

Measured on the Hermes browser-extension side panel (v0.3.1), 320/420 px, captured
headless via CDP and sampled with Pillow.

- Full spec: `C:\Users\<you>\OneDrive\Documents\<archive>\_Knowledge\glassy-panel-design-metrics.md`
- Validator: `_Knowledge/theme-contrast-check.mjs` (`node theme-contrast-check.mjs <theme.json>`, exit 0 = pass)
- Palettes: `_Knowledge/sunstone-theme.json` (warm), `_Knowledge/glacier-theme.json` (cool dark)
- Reference implementation of the material recipe: section 9 of
  `C:\Users\<you>\hermes-browser-extension\extension\sidepanel-legibility.css`
- Session record: `OneDrive\Documents\<archive>\Sessions\2026-09-20-hermes-extension-readability\`

Hard numbers worth quoting without re-deriving:

| Measure | Value |
| --- | --- |
| Card surface ramp at 36 % paper over the bloom | `#0d2527` → `#193437` → `#0b1417` down one card |
| Same at 46 % paper (rejected as too subtle) | `#0d2123` → `#0c1519` |
| Ink on the lightest composite | 13.97:1 |
| Surface step paper−canvas | 4–8 L\* (3.9–7.8 across the two themes) |
| Tightest pair in either theme | Sunstone light `line on canvas` 3.37:1 |
