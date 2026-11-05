# Example: Paratera (ai.paratera.com) wired into Hermes

Verified end-to-end against both hosts of the same platform. This is the concrete instance that
produced the pitfalls in the parent skill — keep it as a working reference, not as dogma. The
entry name, the `base_url` and the resolved `key_env` move together; changing one alone is what
breaks a whole alias block.

## Facts discovered
- **Base URL:** `https://ai.paratera.com/v1` (OpenAI-compatible). The dashboard
  `https://ai.paratera.com/#/lms/api` is an SPA — `web_extract` and `curl` on
  the bare host return the app shell, not data.
- **The HOST in the `base_url` decides which `<HOST>_API_KEY` Hermes resolves** (`ai.paratera.com`
  → `PARATERA_API_KEY`, `llmapi.paratera.com` → a differently-named var), and ONE key can be valid
  on both hosts. So repointing an alias at the other host silently swaps its credential instead of
  erroring — 93 IDs on `llmapi.paratera.com`, 92 on `ai.paratera.com`, both accepting chat calls
  with the same live key. Decide the host first, then pin `key_env` on the provider entry so an
  alias never guesses.
- `/v1/models` returned **92** model IDs (the full platform catalog), but the
  probe found only **~66** were actually callable. The rest would 403 or are
  non-chat (image/video/tts/embedding). The platform key was **team-limited**.
- A real chat/tool-calling call with an accessible model (`DeepSeek-V3.2`,
  `GLM-4.7`, `Qwen3.7-Max`) all returned correct responses. `-m <alias>` and
  `-m provider/model` both failed with HTTP 403 — see pitfalls.

## Config that worked
```
# .env (append; never put the key in config.yaml)
HERMES_CUSTOM_HERPES_API_KEY=sk-...

# hermes config set ...  (never hand-edit config.yaml)
config set providers.herpes.name "Paratera"
config set providers.herpes.base_url  "https://llmapi.paratera.com"
config set providers.herpes.key_env   "HERMES_CUSTOM_HERPES_API_KEY"
config set providers.herpes.discover_models true
config set model.provider "herpes"
config set model.base_url  "https://llmapi.paratera.com"
config set model.default   "DeepSeek-V4-Flash-Vision-Exp"
```
An earlier route used `providers.paratera` + `https://ai.paratera.com/v1` + `PARATERA_API_KEY`;
that token was later revoked server-side (`401 token_not_found_in_db` on BOTH hosts) while the
aliases kept naming `paratera` and the old host. The entry name is user-chosen and may be a house
joke or a typo — resolve it by `base_url` + `key_env`, never by the name.

## Aliases that worked (all under top-level `model_aliases`, dict form)
`provider` MUST be a name that actually exists under `providers:`. With the provider entry holding
base_url + key_env, an alias needs neither of its own:
```
config set model_aliases.glm  '{"model":"GLM-4.7","provider":"herpes"}'
config set model_aliases.ds   '{"model":"DeepSeek-V3.2","provider":"herpes"}'
```
An alias that carries its own `base_url` gets its key from that URL's host instead — which is
precisely how a renamed/re-hosted provider leaves a whole block of aliases holding a revoked key.
Also mirrored: `ds-flash`→DeepSeek-V4-Flash, `ds-pro`→DeepSeek-V4-Pro,
`glm5`→GLM-5, `qwen`→Qwen3.7-Max, `qwen-plus`→Qwen3.6-Plus, `kimi`→Kimi-K3,
`minimax`→MiniMax-M3, `mmx-m2`→MiniMax-M2.7, `ernie`→ERNIE-4.5-Turbo-128K,
`ernie5`→ERNIE-5.0-Thinking-Preview, `glm-v`→GLM-4.6V, `qwen-long`→Qwen-Long.

## Diagnostic trail (the actual gotchas, in order)
1. Naive approach set aliases with `provider: custom` + base_url. `resolve_alias`
   returned `('custom','GLM-4.7','glm')` fine, but the runtime then rejected the
   non-loopback base_url via `_config_base_url_trustworthy_for_bare_custom`
   (because `model.provider` is `paratera`, not literal `custom`). Fix: `provider: paratera`.
2. One-shot `-m <alias>` DOES resolve a dict-form `model_aliases` entry — model, provider,
   base_url and key are all resolved before the call, and the failure text names the alias's own
   host/key, which is how you tell which route an alias is really on. It is the standard per-alias
   proof. Only if you see HTTP 403 `Model: <alias>` did the raw label leak on that path; then use
   in-session `/model <alias>` (sends the resolved ID via `resolve_alias`) or set `model.default`.
3. The 403 body `team not allowed to access model ... models=['GLM-Embedding-2',
   'Qwen3.7-Plus', ...]` is the platform telling you the key's real access set —
   list the catalog, probe it, trust the probe over the catalog.

## Verification that worked
```
# default route, real runtime
hermes -z "reply with exactly: ok"
# every alias, one line each — the bulk-repair proof after any config edit
for a in ds glm kimi qwen ...; do printf "%s -> " "$a"; hermes -z "reply with exactly: ok" -m "$a"; done
# raw-endpoint check with the exact key the entry names: separates wiring from per-model limits
H=$(grep -m1 '^HERMES_CUSTOM_HERPES_API_KEY=' .env | cut -d= -f2-)
curl -s -o C:/Temp/o.json -w '%{http_code}\n' -X POST https://llmapi.paratera.com/v1/chat/completions \
  -H "Authorization: Bearer $H" -H 'Content-Type: application/json' \
  -d '{"model":"Kimi-K3","messages":[{"role":"user","content":"say ok"}],"max_tokens":8}'
```
A fresh `hermes -z` / `hermes chat -q` reads config.yaml fresh; the already-running chat does not —
tell the user to start a new chat after editing `model.*`. On Windows, give a native `curl -o` a
`C:/Temp/...` path; an MSYS `/tmp` path is not translated and the file never appears.

## Per-model residuals once the wiring is proven (not provider bugs)
A model can be wired correctly and still fail through Hermes while answering 200 to raw curl. Name
the side that owns each one instead of re-editing the provider: upstream channel/group restriction
(503, flaps — retry once before reporting), a context-length ceiling Hermes believes is tiny
(`Cannot compress further` on a 24-token window), a `max_completion_tokens` range the model rejects
(400), and usage-chunk/streaming failures on long-context models. All four are per-model metadata
or limits, so the report is "wiring fixed, model needs an override" — not "provider still broken."
