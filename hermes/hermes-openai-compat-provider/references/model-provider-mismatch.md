# Model-ID / provider mismatch: triage a failing LLM call back to its config

Symptom shape: the agent answers normally in one surface but a turn in another
returns HTTP 400/401/403 from an endpoint you did not knowingly target — e.g.
`The supported API model names are deepseek-flash, deepseek-v4-pro, but you passed
DeepSeek-V4-Flash-Vision-Exp.` The name is valid; it is valid *somewhere else*.

Root cause: an LLM call is stamped with the provider that owns the base_url and
key, while the model ID travels separately. Model IDs are per-vendor, so an ID
from seller A sent with seller B's credentials is a 400 even though both sell the
same family. Any UI that lets a user pick a model (browser-extension panel,
desktop) sends `provider` + `model` per turn, so the two can drift apart.

## Triage order (cheapest first)

### 1. The failure dump
```
ls -t "$HERMES_HOME/sessions/request_dump_<session-id>_*.json" | head
```
Read `request.url`, `request.headers.Authorization` (prefix only — enough to
identify which key), and `request.body.model`. This is ground truth for what went
on the wire; it appears whenever the turn failed with a non-retryable client error.

### 2. Session identity in `state.db`
Use the install's own interpreter so no SQLite client is needed:
```
./venv/Scripts/python - <<'PY'
import sqlite3
con = sqlite3.connect("file:state.db?mode=ro", uri=True); cur = con.cursor()
for r in cur.execute("SELECT id, model, billing_provider, billing_base_url, started_at "
                     "FROM sessions WHERE id LIKE '%<session-fragment>%' ORDER BY started_at DESC LIMIT 5"):
    print(r)
for r in cur.execute("SELECT session_id, model, billing_provider, billing_base_url, api_call_count, last_seen "
                     "FROM session_model_usage WHERE session_id LIKE '%<session-fragment>%'"):
    print(r)
PY
```
Rows are per `(session, model, provider, base_url)`, so they show **when** a
session switched provider — a model row with two different `billing_base_url`
values is the drift. `sessions.model_config` (JSON, nullable) carries persisted
per-session overrides.

### 3. What each side actually offers
Vendor's own catalog:
```
curl -s -H "Authorization: Bearer $VENDOR_KEY" https://api.<vendor>.com/models
```
Aggregator's catalog (and what a picker will show for your custom provider):
```
curl -s -H "Authorization: Bearer $API_SERVER_KEY" http://127.0.0.1:8642/api/model/options
```
`/api/model/options` returns every provider the runtime knows, each with `slug`,
`is_current`, `is_user_defined`, `total_models`, `base_url` and a `models[]` list —
both the built-in vendor provider (from `<VENDOR>_API_KEY`/`<VENDOR>_BASE_URL` in
`.env`) and the custom aggregator entry. Two hits for the same model family under
different IDs is the mismatch.

### 4. Confirm both directions before changing anything
```
# expected to fail: aggregator ID against the vendor's endpoint
curl -s -X POST https://api.<vendor>.com/chat/completions \
  -H "Authorization: Bearer $VENDOR_KEY" -H 'Content-Type: application/json' \
  -d '{"model":"<Aggregator-CamelCase-ID>","messages":[{"role":"user","content":"hi"}],"max_tokens":1}'

# expected to succeed: the vendor's own slug
curl -s -X POST https://api.<vendor>.com/chat/completions \
  -H "Authorization: Bearer $VENDOR_KEY" -H 'Content-Type: application/json' \
  -d '{"model":"<vendor-slug>","messages":[{"role":"user","content":"say ok"}],"max_tokens":8}'
```

## Is the ID wrong, or is the key not entitled?

Both look like "the model is not there"; only one of them is a config problem.

- **Absence from `/v1/models` proves nothing, and casing is per-seller.** Aggregators
  filter that catalog by the key's entitlement, so a model the gateway knows about can
  be missing from it while still being a perfectly valid ID. Only a direct probe
  separates `400 model not found: X` (the endpoint has never heard of it) from
  `403 team_model_access_denied` (valid, registered, not yours to call) — test the
  CamelCase ID *and* the vendor's lowercase slug before concluding the name is wrong:
  `python scripts/probe_model_ids.py <base_url> <KEY_ENV_NAME> <ID> [<ID> ...]`
- **The 403 body may or may not carry the allowed set.** When it includes a
  `models=[...]` list, that list is the key's real access set — trust it over the
  catalog. When it only reads `team not allowed to access model. Tried to access <ID>`,
  the ID is still proven to exist; the allowed set has to come from `/v1/models` plus
  probing.
- **A vendor's rename does not reach the aggregator.** When a vendor ships a new
  generation and starts routing retired IDs to it, an aggregator usually keeps selling
  the old IDs under their old names, sometimes still on the old weights. A model that
  exists upstream is not a model this key can call — the seller's own catalog is the
  only authority for what is purchasable here, and asking them when the new ID lands is
  a legitimate part of the answer.

## Where the fix belongs

| Situation | Fix |
|---|---|
| Aggregator provider is intended (its key + base_url) | Keep the CamelCase ID; correct the *session/picker* selection so it sits under that provider row. Nothing in `config.yaml` is wrong. |
| Vendor-direct is intended | Use the vendor's slug and let the built-in provider resolve base_url/key from `.env`. |
| A valid ID returns 403 `team_model_access_denied` | Nothing in Hermes can help — the gateway is rejecting the *key's team*, not misreading a name. Report it as an access request naming the exact ID, never as a config bug. |
| Both should be selectable | Leave both registered; the IDs must never be mixed. Names that collide with a built-in provider's family invite this — say so when choosing the custom provider's alias/ID set. |

Tell the user which surfaces are unaffected: sessions on the *other* provider
(desktop chat, messaging gateway, cron jobs) keep working, because the mismatch is
per-session, not global. If the picker is a browser-extension panel, the selection
lives in Chrome extension storage — it must be changed in the panel, not in Hermes
config.
