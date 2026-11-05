---
name: hermes-desktop-plugins
description: "Use when managing Hermes desktop UI plugins."
version: 1.0.0
metadata:
  hermes:
    tags: [hermes, desktop, plugins, ui, theme, model-labels]
---

# Hermes Desktop Plugins

Desktop plugins are UI-layer extensions the desktop app hot-loads from disk. They live at:

- `$HERMES_HOME/desktop-plugins/<name>/plugin.js` — plain ESM, `export default { id, name, register(ctx) }`
- also `$HERMES_HOME/plugins/<name>/desktop/plugin.js` (unified-package half)

The runtime loader watches these directories and hot-reloads edits. A plugin can rewrite DOM text without touching any config, so a "wrong" label in the app (model name, status pill, picker row) is often a plugin, not a provider setting.

## Diagnose a "wrong" name or label before touching config

1. Read the effective config first — `hermes config get model`, `hermes config get providers.<name>`, `hermes model` (prints current model + provider). Config is the truth; the UI label may differ from it.
2. If config already says what the user expects, grep the plugin dir for the displayed string: `grep -r "DeepSeek 4.1 Flash" desktop-plugins/`. A text-rewriting plugin (a REPLACEMENTS table) is the likely cause.
3. Distinguish the three name layers, don't conflate them: wire ID (`deepseek-flash`) → vendor display name ("DeepSeek-V4.1-Flash") → plugin rewrite on top. Retired aliases (`deepseek-chat`/`deepseek-reasoner`) are normalized to `deepseek-v4-flash`; the app's own prettifier may emit yet another form ("Deepseek V4 Flash").

## Disable a plugin reversibly

- Move the plugin directory OUT of `desktop-plugins/` to a sibling (e.g. `desktop-plugins-disabled/`). Don't delete — moving back restores it.
- Don't rename it in place (e.g. `deepseek-names.disabled/` still under `desktop-plugins/`): the loader scans every directory under the root for a `plugin.js`, so a renamed dir still loads. It must leave the tree.
- The running window has already loaded the plugin; the change applies on the next desktop-app restart. Tell the user to restart, don't claim it's live.

## Authoring pitfalls

- Write text nodes only; never add or remove DOM nodes — React reconciliation holds real node references, so structural edits break it. Label rewrites are safe only because they are node-idempotent.
- Skip the transcript (`[data-slot^="aui_thread"]`), the composer input, and code/pre — history and typed text must read back exactly as written.
- To translate the picker's controlled search input, write through the native `HTMLInputElement` prototype value setter so React's onChange sees the new value; a plain `el.value =` on a controlled input is silently overwritten.
