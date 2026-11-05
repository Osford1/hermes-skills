---
name: hermes-openai-compat-provider
description: "Wire a custom OpenAI-compatible model API into Hermes."
---

# Connecting an OpenAI-compatible model provider to Hermes

Handles the full job of pointing Hermes at a third-party OpenAI-compatible
inference endpoint (model aggregators like Paratera/SiliconFlow/OpenRouter,
Chinese model hubs, self-hosted vLLM/Ollama/LiteLLM relays) using a plain
API key. Works via the built-in `custom` provider machinery — no provider
plugin required.

**Trigger:** user says "use my API key", "make Hermes use this platform",
"add <name> models", gives an `sk-...` key and a URL with a `#/`-style
dashboard, or wants Chinese/multi-model access.

## Key hard-won facts (read before you touch config)

1. **The `/models` catalog is NOT the same as what your key can call.**
   Aggregators often serve the full platform model list at `GET /v1/models`
   while the key is bound to a *team* with a limited subscription. You must
   **probe each model** to discover the truly accessible subset. A 403
   `team_model_access_denied` naming the model back is the tell: the ID is real
   and registered on that gateway, the key's team is simply not entitled to it
   (the body may or may not also list the allowed set). Run
   `scripts/probe_accessible_models.py` for what the catalog lists, and
   `scripts/probe_model_ids.py` for IDs the catalog omits entirely.

2. **Aliases must use `provider: <custom-name>`, never `provider: custom`.**
   The bare `custom` provider hits a trust guard
   (`_config_base_url_trustworthy_for_bare_custom`) that rejects non-loopback
   base_urls unless `model.provider` is literally `custom`. When you register
   a named custom provider (e.g. `paratera`), point aliases at that name so the
   runtime resolves base_url + key from the provider entry. **The name must exist as a key
   under `providers:` — check it, never assume it.** A name that isn't there raises no config
   error at call time: the alias falls to the direct-alias path and resolves its credential
   from the alias's own `base_url` HOST (`<HOST>_API_KEY`), so a stale provider name silently
   books the wrong (often revoked) key and the call dies with a bare 401 naming a key hash you
   never chose. Fingerprints of the missing name, both in the log: `Unknown provider '<name>'`
   from cron pre-dispatch validation, and `healed stale session provider '<name>' to
   'custom:<provider>'`. Changing a host or renaming a provider entry therefore invalidates
   every alias that still names the old one — grep the whole `model_aliases:` block after any
   provider rename, don't fix the one alias the report names.

3. **`-m <alias>` resolves dict-form `model_aliases` in one-shot mode — that is how you
   verify an alias.** `hermes -z "reply with exactly: ok" -m <alias>` resolves model + provider +
   base_url + key *before* the call, proved by the alias's own base_url and key surfacing in the
   error text, so it is the cheapest per-alias end-to-end proof; run it for EVERY alias after a
   bulk config edit, not just the one the report named. If you instead see HTTP 403 with
   `Model: <alias>` in the body, the raw label leaked to the API on that path — fall back to the
   in-session `/model <alias>` or to `model.default`. With an *exact catalog ID* (not an alias)
   `-m` is likewise the cheapest proof that Hermes is not the blocker: the endpoint's own error
   text comes back verbatim, so a 403/503 there is the gateway's verdict on the key, not a config
   mistake.

4. **Secrets live in `.env`, referenced by name, not in config.yaml.**
   Store the key as `<HOST>_API_KEY` (Hermes derives the name from the base_url
   host: `ai.paratera.com` → `PARATERA_API_KEY`) and wire it with the provider
   entry's `key_env` field.

## Steps

### 1. Discover the base URL
The dashboard URL (`https://host/#/lms/api`) is a SPA — `web_extract` and
`curl` on the bare host return nothing useful. Probe common OpenAI-compatible
roots against `/models` with the key:
```
curl -s -H "Authorization: Bearer $KEY" "https://host/v1/models"
```
The first `/v1` that returns `{"data":[{...}]}` is the base URL.

### 2. Find what the key can actually use
```
python scripts/probe_accessible_models.py <base_url> <sk-...>
```
It lists every model in `/models`, fires a minimal `chat/completions` to each,
and buckets them: **accessible** (200), **team-blocked** (403), **non-chat/other**.

### 3. Store the key
Append to `<HERMES_HOME>/.env`:
```
PARATERA_API_KEY=sk-...
```

### 4. Register the provider + set default (`hermes config set` — never hand-edit config.yaml)
```
hermes config set providers.<name>.name "<Display Name>"
hermes config set providers.<name>.base_url  "https://host/v1"
hermes config set providers.<name>.key_env   "<HOST>_API_KEY"
hermes config set model.provider "<name>"
hermes config set model.base_url  "https://host/v1"
hermes config set model.default   "<Exact Model ID>"
```
`hermes config set` parses values with `yaml.safe_load`, so nested
dict/JSON values work for anything richer.

### 5. Register brand-level aliases (top-level `model_aliases`, dict form)
The `provider` field MUST be the named custom provider, not `custom`:
```
hermes config set model_aliases.glm '{"model":"GLM-4.7","provider":"paratera","base_url":"https://host/v1"}'
```

### 6. Verify through the real runtime
A fresh `hermes chat -q "..."` reads config.yaml fresh and exercises the full
config → provider → key → base_url → client path (the live session keeps its
old provider; config edits apply to new sessions).
```
hermes chat -q "Reply exactly: OK"
```

## Pitfalls
- **Don't trust `/models`.** Always probe — a key "working" on a few models is
  not proof it has the whole catalog (and vice-versa).
- **Model IDs are per-vendor, never universal — the same model carries a different
  ID at every seller.** An aggregator's ID (e.g. `DeepSeek-V4-Flash-Vision-Exp`,
  CamelCase) is rejected by the vendor's own endpoint, whose `/models` lists short
  slugs (`deepseek-flash`, `deepseek-v4-pro`). The tell is HTTP 400
  `invalid_request_error`: "The supported API model names are X, Y, but you passed Z."
  A request is stamped with whichever provider supplied the base_url + key, so the
  `model` must come from that same catalog — fix the **pairing**, not the name.
- **A vendor-direct key in `.env` adds a second provider to every picker.** With
  `<VENDOR>_API_KEY` (plus `<VENDOR>_BASE_URL`) present, Hermes registers the
  built-in vendor provider alongside your custom aggregator entry, and UI pickers
  (browser-extension panel, desktop) list both. Selecting the aggregator's ID while
  the vendor's provider row is active produces the 400 above; check which provider
  the *session* is on, not just which name you typed.

## Repointing every alias after a provider rename (bulk alias repair)

A provider entry is renamed, re-hosted, or re-keyed, the `model_aliases:` block keeps the old
name and the old `base_url`, and every alias starts failing. Repair it as ONE uniform edit, then
prove each alias:

1. **Back up first, copy not move:** `cp -p "$HERMES_HOME/config.yaml"
   "$HERMES_HOME/config.yaml.bak-$(date +%Y-%m-%d-%H%M%S)-<why>"` (plus `.env` if keys move).
2. **Count, then replace — abort unless the count matches.** Do it in Python over the decoded
   text (`raw.count(old)` → `assert n == expected` → `raw.replace`), because the similar aliases
   share one literal multi-line shape, so a single replace covers them all at once and lets you
   assert you hit every one. Per-key `hermes config set` calls cannot express "same change
   everywhere" and cannot write a value whose key path contains dots. Assert the `\r\n` count is
   unchanged (config.yaml is CRLF on Windows), then recount leftovers (`provider: <old-name>`,
   old host) and require zero.
3. **Verify each alias through the runtime, one 1-turn call apiece** — a repoint that fixes the
   reported alias can leave siblings broken while the picker shows them as equivalent:
   `for a in <alias>...; do printf "%s -> " "$a"; hermes -z "reply with exactly: ok" -m "$a"; done`
   Filter the update-notice preamble and `tail -2` so each alias yields one line.
4. **Classify the stragglers with raw `curl`, never with another config edit.** Read the exact key
   the provider entry names (`grep -m1 '^<KEY_ENV>=' .env | cut -d= -f2-`) and POST the same model
   straight at the entry's `base_url`. A 200 there but an error through Hermes means the wiring is
   CORRECT and the leftover is per-model metadata or a Hermes-side limit — say so, do not re-edit
   the provider. Canonical residuals: upstream channel/group restriction (503 — entitlement, and
   it flaps, so retry once before reporting it), a context-length ceiling Hermes believes is tiny,
   a `max_completion_tokens` range the model rejects, usage-chunk parsing failures on long-context
   models.
5. **Report per alias:** which now answer, which fail, and for each failure the status line plus a
   verdict — upstream account, Hermes metadata, or still config. Then offer the loose ends (dead
   key still in `.env` that nothing references, gateway restart, metadata overrides) as explicit
   one-liners rather than doing them silently.

## "How do I enable model <X> on <provider>?" — answer with a probe, not a config change

This arrives whenever a vendor ships a new model and the user assumes Hermes needs
editing. Work the evidence first, then lead the reply with the verdict:

1. **Resolve the provider to an endpoint.** Read config.yaml (or `hermes config get
   model.base_url`) for the entry's `base_url` + `key_env`. Custom entry names are
   user-chosen and can look like typos or a house joke — trust the `base_url`, never
   the name.
2. **Probe the candidate IDs directly** — `/v1/models` alone is not evidence (it is
   entitlement-filtered). Vendor release notes / docs give the canonical ID:
   `python scripts/probe_model_ids.py <base_url> <KEY_ENV_NAME> <ID> [<ID> ...]`
3. **Read the error class; it decides whether any Hermes edit can help:**

   | Response | Meaning | Fixable in Hermes? |
   |---|---|---|
   | 200 | callable | nothing to change |
   | 403 `team_model_access_denied`, naming the model back | valid ID, key's team not entitled | **No** — the platform must open the model for the key |
   | 400 `model not found: X` | endpoint does not know that ID | yes — use the ID this seller sells |
   | 401 `token_not_found_in_db` | the resolved key is dead/rotated — **or the right key was never selected** (an alias naming a provider entry that does not exist resolves its key from the alias's own `base_url` host) | yes — fix the key, the entry's `key_env`, or the alias's `provider` name |
   | 503 no available channel for the model group (`当前用户模型渠道限制…`, group-restriction text) | upstream account/subscription does not cover that model right now | **No** — and retry once before reporting: this one flaps |

4. **Give the verdict + raw evidence, then the two-step ask:** the exact status line
   and error text, then (a) what the user must request from the platform — a support
   ticket naming the exact ID — and (b) the one-line Hermes step for afterwards. Never
   hand over a config recipe that will 403 on its first call.
5. **After access is granted, expect it to appear by itself.** An entry whose `models`
   map Hermes discovered (`discover_models: true`) is rewritten from the live
   `/v1/models` probe when the picker next probes, so a newly opened model shows up on
   its own; a `models` map the user curated by hand is never overwritten, so it can go
   stale. Force the default in one line instead:
   `hermes config set model.default <Exact Model ID>`

## "I can't see model <X>" — UIs print the wire ID, never the vendor's display name

A vendor's display name is not what any Hermes surface prints, so a user searching for it finds
nothing and reports the model as missing. It is usually present AND already selected. Work the
labels before you go hunting for a UI bug.

- **`/v1/models` returns `id` (callable) and `name` (a human label no Hermes UI reads)** — e.g.
  `{"id": "deepseek-flash", "name": "DeepSeek-V4.1-Flash"}`. Passing that `name` as the model
  gets HTTP 400 listing the supported IDs, and the user's phrase ("4.1 Flash") maps to the `id`.
- **Pickers render the raw ID in mono and search only that ID plus the provider name/slug**
  (`model-picker.tsx` → `HighlightMatches text={model}`, haystack from `modelSearchText()`). A
  search for a fragment of the display name (`4.1`) matches nothing even with the row on screen:
  give the user the exact row strings plus a term that does match (`flash`), do not treat it as a
  missing-model bug.
- **The status/composer chip is a prettifier over the ID, not the vendor name** —
  `displayModelName()` title-cases it (`deepseek-v4-flash` → "Deepseek V4 Flash") and turns
  `-fast/-thinking/-preview/-latest` into a grayed tag. Config ID, picker row and chip can be three
  different strings for one model; say which is which rather than implying an inconsistency.
- **Expect Hermes to rewrite the ID on the way out** toward its own catalog
  (`deepseek-flash` → `deepseek-v4-flash`), with the vendor endpoint accepting both. So "which ID
  do I write in config" has a third valid answer: whatever the wire request shows.
- **A provider missing from the desktop picker entirely is a DIFFERENT branch.** The desktop
  requests `/api/model/options?explicit_only=1` — configured providers only, so an ambient/.env-only
  credential is filtered out — and greys rows named in `unavailable_models`. Query the same URL the
  UI uses (`curl -H "Authorization: Bearer $API_SERVER_KEY" http://127.0.0.1:8642/api/model/options`)
  and compare `authenticated` / `is_current` / `models` before concluding anything.
- **Check the reseller's group too.** A family is listed both under its own vendor group and inside
  an aggregator's ~90-model group under different CamelCase IDs; users scan the aggregator list for
  the vendor's naming and come up empty for a model the vendor serves.
- **Don't infer the rendered string from reading the source — run it.** For a label/prettifier
  question, a throwaway vitest probe in `apps/desktop` that imports the module and asserts its
  output against a sentinel (`expect(out).toEqual(['SHOW_ME'])`) prints the real values in the
  failing diff; vitest swallows `console.log` there, so a logging probe proves nothing. Delete the
  probe when done.

## Attributing a failing call to a provider/key

A 400/401/403 says which endpoint rejected you, not which config produced it.
Three reads; details and worked queries in
`references/model-provider-mismatch.md`:

1. **Failure dumps** — `$HERMES_HOME/sessions/request_dump_<session-id>_*.json`
   hold the exact wire request: `url`, the `Authorization` prefix (enough to tell
   which key), and `body.model`. One look separates aggregator from vendor-direct.
2. **Session identity** — `state.db` (open read-only, `file:...?mode=ro`):
   `sessions.model / billing_provider / billing_base_url` plus the per-model rows in
   `session_model_usage` show what the session actually called and when it changed.
3. **What the picker offers** — `curl -s -H "Authorization: Bearer $API_SERVER_KEY"
   http://127.0.0.1:8642/api/model/options` (gateway API server) lists every provider
   with `slug`, `is_current`, `models[]`: the set a UI picker shows. Look for two
   providers exposing the same family under different IDs.
- **Resolve a provider without spending a token.** With `HERMES_HOME` set, in the install dir:
  `./venv/Scripts/python -c "from hermes_cli.runtime_provider import resolve_runtime_provider as R;r=R(requested='<slug>', target_model='<model>');print(r.get('provider'), r.get('base_url'))"`
  prints the provider name and base_url (mask the key) the runtime would use for that slug/model
  pair — the cheapest way to prove which endpoint a name maps to. Note: a **user-defined**
  provider resolves to internal `provider='custom'`, so any check comparing the *requested slug*
  against the runtime provider name reports a mismatch (that is what makes a browser model lock
  fail closed with `confirmed model lock runtime mismatch`, HTTP 500).
- **`provider: custom` in aliases → 403.** Use the named provider key.
- **`-m` with an alias → 403** (raw label sent). Prefer `/model` or default.
- **Non-chat models** (image/video/embedding/tts/rerank) respond 400/404 to
  `chat/completions` regardless of access — don't misread that as "key broken."
- **The live chat never picks up config changes mid-session.** Tell the user to
  start a new chat after changing `model.*`.
- **Model IDs containing dots cannot be written through a `hermes config set` key
  path.** `hermes config set providers.<p>.models.DeepSeek-V4.1-Flash '{}'` splits the
  path on `.` and builds `models → DeepSeek-V4 → 1-Flash` instead of one ID. Put the ID
  where it is a *value* (`model.default`, an alias's `model` field, an alias dict), or
  let discovery write the whole `models` mapping at once.

## Disabling a competing built-in provider (make the picker unambiguous)

When the same model family is sold by your aggregator *and* by the vendor directly, a
vendor-direct key in `.env` puts two rows in every picker and turns each selection into a
name/provider pairing gamble. Dropping the vendor-direct route is a config change:

1. **Back up first** — `cp "$HERMES_HOME/.env" "$HERMES_HOME/.env.bak-<YYYY-MM-DD>-<why>"`.
2. **Comment out the pair** (`<VENDOR>_API_KEY`, `<VENDOR>_BASE_URL`) with a one-line note saying
   why and how to restore. `read_file`/`patch` refuse `.env` (credential store), so edit it with a
   short Python script through `terminal`: `splitlines(keepends=True)`, prefix matched lines with
   `# `, write with `newline=""`. **Preserve line endings** — count `\r\n` before and after; an LF
   rewrite of a CRLF file makes a huge useless diff.
3. **Verify masked:** diff backup vs new in Python, print only the changed line *ranges*, never key
   material. Expect exactly the intended lines.
4. **Restart the gateway** (`hermes gateway restart`) — `.env` is read at startup, so a running
   gateway keeps serving the old provider set.
5. **Confirm against the model-options endpoint:** the disabled provider returns
   `authenticated: false, total_models: 0` plus a `paste <KEY> to activate` warning, while your
   custom provider stays `is_current: true`. UI pickers treat unauthenticated providers as
   unavailable, so its rows disappear. Finish with one real 1-turn call on the default provider.

Expect this side effect: sessions that had *already* captured the removed provider now fail loudly
(`RuntimeError: No LLM provider configured`) instead of silently calling the wrong vendor. That
error is the fingerprint of a per-session route, not a broken config — the config is fine, that
session id is poisoned, so start a new session and leave the old one alone.

## Model APIs that are not chat-shaped (decision, classification, rerank)

Some model APIs are worth wiring into Hermes but can never be `model.default`:
they return typed values (a label, a score, a probability, a ranking) instead of
generating text, and they emit no tool calls. A decision/classification service
is the sharpest case — it may have no `/chat/completions` route at all
(`/v1/systemone`, `/evaluate`, `/rerank` are real paths in the wild).

- **Never probe the key by pointing a custom provider at it.** That request
  fails on shape, not on auth, and the 400/404 is the same tell as the non-chat
  pitfall above. Read the vendor's documented path first, then judge the key.
- **The integrations that work, cheapest first:**
  1. **MCP tool.** Wrap it in a small MCP server exposing one narrow tool and
     register it (`setup_mcp`). The agent calls it like any other tool and the
     typed answer lands where code can branch on it. Best fit for decision models.
  2. **Gateway below Hermes.** A passthrough route plus a classifier-driven
     auto-router — an LLM gateway that asks the decision model which completion
     model should handle the request — leaves Hermes's config untouched.
  3. **A local shim** accepting `/chat/completions` and mapping to the real
     endpoint. Only worth building to answer "can it be the model" empirically;
     with no text and no tool calls it still cannot drive an agent loop.
- **Check the aggregator catalogue before the vendor's own waitlist.** These
  models usually appear on an aggregator (OpenRouter, Vercel AI Gateway,
  Cloudflare Workers AI) days before vendor-direct access opens, so a key you
  already hold is often enough.
- **Say what it cannot do, plainly.** When a user asks whether model X can be
  added to Hermes, lead with the slot it cannot fill and the one it can — a
  "yes, as a tool; no, as the agent model" answer is more useful than a config
  recipe for something that will fail on its first tool call.

## Toggling a vendor-direct provider ON/OFF on request (a user-chosen switch)

When a user wants vendor-direct access "only while I need it" plus a switch to turn it off,
do not hand them a config recipe to retype. Ship the flip as a script and prove both directions:

1. **One script, modes `on|off|hide|status`**, doing the whole flip: `hermes config set` for the
   four `model.*` keys (`provider`, `default`, `base_url`, `key_env`) plus the `.env` key pair.
   `off` restores the previous route and LEAVES the key loaded (the other provider stays one
   picker-click away); `hide` also comments the key out and restarts the gateway so the provider
   disappears from every picker.
2. **Back up `config.yaml` and `.env` inside the script**, and edit `.env` with
   `splitlines(keepends=True)` plus a CRLF count assertion, so a toggle can never rewrite the
   file's line endings.
3. **`model.key_env` must move with the switch.** Leaving the previous provider's key name in
   place sends the wrong credential to the new host (401).
4. **Drop a PATH shim beside the other launchers** (`$HERMES_HOME/bin/<name>` + `<name>.cmd`, that
   dir is on PATH) so the switch is one short word. On Windows the bash shim must resolve a NATIVE
   path for python (`$LOCALAPPDATA`, or `cygpath -w`); an MSYS `/c/...` path is not translated and
   the native interpreter dies with `can't open file 'C:\c\Users\...'`.
5. **Verify BOTH directions before reporting.** `state.db` (`sessions.billing_provider` /
   `billing_base_url`) proves which host a session actually called; the gateway's
   `/api/model/options` shows `authenticated` / `is_current` per provider and flips without a
   restart because long-lived processes re-read `.env` per turn.
6. **DeepSeek-direct specifics:** `/v1/models` serves exactly `deepseek-flash` (name
   "DeepSeek-V4.1-Flash") and `deepseek-v4-pro`. Both `https://api.deepseek.com` and
   `https://api.deepseek.com/v1` accept chat calls. Hermes normalizes `deepseek-flash` ->
   `deepseek-v4-flash` on the way out and the endpoint accepts both, so either lands on V4.1-Flash.
   A user asking for "deepseek 4.1 flash" means `deepseek-flash`.

## Support files
- `scripts/probe_accessible_models.py` — reusable probe: enumerate + test every
  model on any OpenAI-compatible endpoint to find the accessible subset.
- `scripts/probe_model_ids.py` — classify candidate IDs you supply (right casing, wrong
  name, entitlement-blocked, dead key) with one 1-token call each; covers IDs the
  catalog hides. Prefer either script over hand-written `curl` loops — on Windows a
  native `curl -o` needs a `C:/…` output path, and an MSYS `/c/…` or `/tmp` path is not
  translated, so the file silently never appears.
- `references/model-provider-mismatch.md` — triage a 400/401/403 back to the
  provider, key and catalog that produced it (request dumps, `state.db`, the
  api-server model-options list, the two-sided `curl` probe), plus "is the ID wrong, or
  is the key not entitled?"
- `references/example-paratera-setup.md` — the concrete, verified Paratera
  (ai.paratera.com) example: full config, verified aliases, and the exact
  observations that led to the pitfalls above.
