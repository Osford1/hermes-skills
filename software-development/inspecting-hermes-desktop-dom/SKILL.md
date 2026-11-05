---
name: inspecting-hermes-desktop-dom
description: "Read the live Hermes desktop DOM/CSS over CDP."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [desktop, electron, cdp, dom, ui-verification, self-inspection]
    related_skills: [node-inspect-debugger, systematic-debugging, dogfood]
---

# Inspecting the live Hermes desktop DOM

## Overview

When you are developing `apps/desktop` and the user is running that same app
(`hgui` / `npm run dev`), you can read the **live rendered DOM** of the window
they are looking at — computed styles, geometry, which CSS rule actually won,
console output — instead of inferring it from `.tsx` and being wrong.

Dev-server runs open a Chrome DevTools Protocol port on `127.0.0.1:9222`
automatically. The renderer is a Chromium page, so everything DevTools can read,
a script can read.

**This does not replace looking at it.** CDP answers *factual* questions ("what
is the computed padding", "did this element render", "which selector matches").
It cannot tell you whether the result looks good. Colour balance, spacing feel,
and "is this ugly" still need the user's eyes or a screenshot. Answer facts with
CDP; hand aesthetics to the user.

## When to Use

- Verifying a UI change actually took effect in the running app
- "Why is this element still X?" — find the winning rule before editing anything
- Locating a stable selector for a component you're about to change
- Checking a design token's computed value on a real node
- Reading renderer console errors the user mentions but can't copy out

**Don't use for:** perf profiling or heap work (`node-inspect-debugger`,
`debugging-hermes-desktop`), or anything where the real question is "does this
look right".

## The port

Open on `127.0.0.1:9222` for any dev-server run. Closed in exactly two cases
(`apps/desktop/electron/dev-cdp.ts`):

- **packaged builds** — always, and no environment value overrides it;
- **no `HERMES_DESKTOP_DEV_SERVER`** — an unpackaged `electron .` against
  `dist/` is how the packaged app gets smoke tested, so it behaves like one.

`HERMES_DESKTOP_CDP_PORT` moves the port (`=9333`) or disables it (`=off`).

Check before doing anything else:

```bash
curl -s --max-time 3 http://127.0.0.1:${HERMES_DESKTOP_CDP_PORT:-9222}/json/version
```

Empty → no port. Do not guess another port silently.

**Never relaunch the user's app to get a port.** That destroys their session and
their state. Launch your own isolated instance instead (below).

## Reading the DOM

`apps/desktop/scripts/eval.mjs` is the one-liner:

```bash
cd apps/desktop
node scripts/eval.mjs "document.querySelectorAll('[data-slot]').length"
```

For multi-step work use the shared client — it has target discovery and
promise-aware eval:

```js
import { CDP, SELECTORS } from './scripts/perf/lib/cdp.mjs'

const cdp = await CDP.connect({ port: 9222, match: '5174' })
const out = await cdp.eval(`JSON.stringify({
  radius: getComputedStyle(document.documentElement).getPropertyValue('--radius-scalar').trim(),
  composer: !!document.querySelector('[data-slot="composer-rich-input"]')
})`)
cdp.close()
```

`SELECTORS` in `scripts/perf/lib/cdp.mjs` holds the stable `data-slot` hooks
(composer, thread viewport, assistant message, turn pair, profile rail). Prefer
them over inventing a `querySelector` — they are updated as a unit when
components move.

## The question this is best at: which rule won?

Editing every call site because a style "isn't applying" is the classic waste.
Read the real node first:

```js
const el = document.querySelector('[data-slot="aui_assistant-message-root"] a')
JSON.stringify({
  ownClasses: el.className,
  weight: getComputedStyle(el).fontWeight,
  parents: (() => {
    const out = []
    let n = el
    while ((n = n.parentElement) && out.length < 6) out.push(n.className)
    return out
  })()
})
```

If the node carries no class of its own, the value is **inherited** — sweeping
call sites will not fix it, and you need the ancestor rule. A plugin stylesheet
(e.g. `@tailwindcss/typography`'s `prose a { font-weight: 500 }`) routinely beats
a utility class; override on the shared class, not at each usage.

## Your own isolated instance

When there is no port, or you must not disturb the user's window:

```bash
cd apps/desktop
HERMES_HOME=/tmp/cdp-probe-home \
HERMES_DESKTOP_DEV_SERVER=http://127.0.0.1:5174 \
HERMES_DESKTOP_CDP_PORT=9333 \
  npx electron . --user-data-dir=/tmp/cdp-probe-userdata
```

The separate `--user-data-dir` dodges Electron's single-instance lock, so it
cannot collide with a running `hgui`; the separate `HERMES_HOME` keeps it away
from real sessions. Pick a port other than 9222 for the same reason. Run it in
the background and kill it when done.

`npm run perf:serve` does the same with a temp `HERMES_HOME` baked in, if you
also want the perf harness.

## Packaged build, no dev server (`apps/desktop/release/win-unpacked`)

The app's own C DP gate stays closed in a packaged build, but Electron's argv flag still
opens the port:

```bash
cd apps/desktop/release/win-unpacked
HERMES_HOME=C:/Users/<user>/AppData/Local/Temp/hprobe-home \
  ./Hermes.exe --user-data-dir=C:/Users/<user>/AppData/Local/Temp/hprobe-ud \
  --remote-debugging-port=9333
```

`--user-data-dir` dodges the single-instance lock, `HERMES_HOME` keeps real sessions out, and
the port answers `curl http://127.0.0.1:9333/json/list` within ~10 s. With no backend the app
shows onboarding/empty shell and **exits on its own after a few minutes** — read promptly, and
launch a fresh one per measurement round. Always confirm the user's own processes are still
alive afterwards (5 `Hermes.exe` PIDs is normal).

No `ws`/playwright needed for evaluation — Python's `websockets` is installed: connect to the
page target's `webSocketDebuggerUrl` and send `Runtime.evaluate` with `returnByValue: true`;
`Page.captureScreenshot` returns the PNG at **device** pixels (CSS × DPR), so multiply by
`devicePixelRatio` when mapping a measured CSS rect onto the image.

## Reading the shipped bundle when no port will ever open

A packaged install can often be answered statically, and sometimes must be (the user's
own window has no port and never will):

- App root: `$LOCALAPPDATA/hermes/hermes-agent/apps/desktop/release/win-unpacked` — that
  `Hermes.exe` is what the user runs, with its source tree beside it.
- **Renderer assets are marked `unpacked: true`**, so every `dist/` file also exists literally
  under `resources/app.asar.unpacked/dist/`. Grep *there* and skip asar parsing: a header parse
  that reads the trailing 4 padding bytes alongside the JSON length throws `UnicodeDecodeError`
  (header = `u32 pickle_size, u32, u32 json_size` at offset 0, JSON at offset 16, files base
  `8 + pickle_size`).
- App settings live in `%APPDATA%\Hermes\Local Storage\leveldb\*`: keys are ASCII framed
  `file://\x00\x01<key>`, values UTF-16LE. An **absent** key means the default — no
  `hermes-desktop-theme-v2` means the default skin (`nous`).
- Resolve a stack against the machine before naming a font: `--dt-font-sans` leads with
  `Segoe WPC`, which is absent on a default Windows box and per-user font dir, so Segoe UI is
  what actually paints. Check `C:\Windows\Fonts`, `%LOCALAPPDATA%\Microsoft\Windows\Fonts`, and
  the `Fonts` registry values to be sure.
- Long inline shell one-liners containing `{n,m}` regex braces trip the hardline command
  blocklist — use `search_files`/pygount-style Python scans instead of `grep -o` with braces.

## Measuring colour and contrast (the numbers, not adjectives)

`getComputedStyle` hands back `color(srgb r g b / a)`, `oklab(...)`, `oklch(...)` and unresolved
`color-mix(...)` — none of it directly comparable. **Do not** walk ancestors for a background
colour: on this app's translucent glass surfaces an ancestor's `backgroundColor` resolves over
white and reports a light surface that is not on screen. Instead:

1. Fill a 2×2 canvas with the backdrop colour, then fill again with the foreground colour, and
   read the pixel — canvas does the alpha compositing for every colour syntax.
2. Sample the flat surface colours from the captured PNG itself (`PIL`, mode of a 9×9 patch).
3. Compute WCAG contrast in Python/the evaluate expression from those two resolved RGB values.

## Shipping a UI fix without touching app source

User desktop plugins load from `$HERMES_HOME/desktop-plugins/<id>/plugin.js`, are **enabled by
default**, and hot-reload on save — so a plugin is the update-safe home for an override layer
(the install tree is reverted by `hermes update`; the plugin dir is not).

- The app's tokens live in `@layer base` in `src/styles.css`. An **unlayered** `:root` rule in an
  injected `<style>` beats them outright — no `!important` needed, and `:root[data-x='on'] ...`
  scoping makes the layer toggleable by flipping one attribute.
- Type scale is a long tail of Tailwind arbitrary values (`text-[0.6875rem]` ×108, `text-[0.65rem]`
  ×54, …). Clamp them with `[class~='text-[0.65rem]'] { font-size: … }` — the attribute value
  matches the literal class string, brackets and all.
- Process-token variables (`--titlebar-control-size`, `--composer-control-size`) override cleanly;
  per-component `h-5`/`h-6` sizes do not — leave those to a source change.
- **Prove it loaded in the user's own app**, which has no debug port: have `register()` write a
  receipt through `ctx.storage` and grep the renderer's LevelDB
  (`%APPDATA%\Hermes\Local Storage\leveldb\*`). A hit for `hermes.plugin.<id>.*` means the running
  app loaded the file; an absent key means it did not.

## Pitfalls

- **Never kill the user's dev server or app to "free" anything.** A mid-serve
  kill nukes Chromium's socket pool, and the resulting `ERR_NETWORK_CHANGED`
  gets blamed on whatever you just changed.
- **A throwaway `HERMES_HOME` has no backend.** The app logs `ECONNREFUSED` for
  `hermes:api` and may exit on its own. The renderer still mounts and the DOM is
  readable — read promptly, and don't mistake a self-exited probe for a broken
  port. Chromium logs `DevTools listening on ws://127.0.0.1:<port>/…` when it
  binds; that line is the proof the port opened.
- **Poll, don't probe once.** A just-launched app needs a second or two before
  the port answers.
- **Never dump the whole DOM.** The desktop renders hundreds of nodes and
  `outerHTML` will bury your context. Project down to a small JSON object inside
  the evaluated expression.
- **Pass `match` to `CDP.connect`.** Without it you may attach to the pet
  overlay, quick-entry window, or a devtools target instead of the main window.
- **`cdp.eval` returns the value; raw `Runtime.evaluate` double-nests it**
  (`.result.result.value`). Use the wrapper.
- **`import.meta.env.DEV` is `true` under `vite dev`** in this repo. The note in
  `apps/desktop/scripts/profile-typing-lag.md` claiming otherwise is stale.
- **Killing your probe kills your own shell.** `Get-CimInstance Win32_Process | Where CommandLine
  -like '*hprobe-ud*' | Stop-Process` also matches the bash/PowerShell process running that very
  command (its command line contains the pattern), so the call returns 4294967295 and you lose the
  rest of the output. Kill by the returned session/PID instead, or exclude the current PID.
