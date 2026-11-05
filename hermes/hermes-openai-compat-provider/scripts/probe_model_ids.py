#!/usr/bin/env python3
"""Classify candidate model IDs on any OpenAI-compatible endpoint.

`probe_accessible_models.py` tests what `GET /v1/models` already lists. Aggregators
filter that list by the key's entitlement, so a model the gateway knows about can be
absent from it while still being a valid ID. When someone says "model X is available"
you must probe X itself. One 1-token chat call per ID classifies it:

  200      accessible
  403      the ID exists on this gateway; your key/team is not entitled to it
  400      the endpoint does not know that ID (wrong name, or wrong seller)
  401      the key itself is dead/rotated - not a model problem
  404/405  route missing -> probably not the OpenAI-compatible root

Usage:
  python probe_model_ids.py https://host/v1 KEY_ENV_NAME DeepSeek-V4.1-Flash deepseek-flash
  python probe_model_ids.py https://host/v1 sk-literal-key ID [ID ...]

The key argument is either a literal `sk-...` key or the NAME of an environment
variable holding it - prefer the name: it stays out of shell history, and this script
only ever prints the label, never key material.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

TIMEOUT = 30.0
# Bodies that mean "this endpoint has never heard of that ID" rather than "denied".
UNKNOWN_ID_HINTS = (
    "model not found", "does not exist", "does not support", "unknown model",
    "invalid model", "supported api model names", "no such model",
)


def resolve_key(value: str) -> tuple[str, str]:
    """Return (key, printable label) for a literal key or an env var name."""
    if value in os.environ:
        return os.environ[value], f"env:{value}"
    if value.startswith("sk-"):
        return value, "literal key"
    print(
        f"!! {value!r} is neither a set environment variable nor an sk-... literal",
        file=sys.stderr,
    )
    sys.exit(2)


def probe(base_url: str, key: str, model: str) -> tuple[int, str]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = json.dumps(
        {
            "model": model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 1,
        }
    ).encode()
    req = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.status, resp.read(400).decode("utf-8", "replace")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(400).decode("utf-8", "replace")
    except Exception as exc:  # DNS, TLS, timeout, connection refused
        return 0, f"{type(exc).__name__}: {exc}"


def classify(status: int, body: str) -> str:
    low = body.lower()
    if status == 200:
        return "ACCESSIBLE"
    if status == 403:
        return "EXISTS, NOT ENTITLED (team/key blocked)"
    if status == 400:
        if any(h in low for h in UNKNOWN_ID_HINTS):
            return "ID UNKNOWN AT THIS ENDPOINT"
        return "400 - read the body (shape, not access)"
    if status == 401:
        return "KEY DEAD/INVALID (rotated? wrong key_env?)"
    if status in (404, 405):
        return "ROUTE MISSING (wrong base_url?)"
    if status == 429:
        return "RATE LIMITED (retry later)"
    if status == 0:
        return "NO RESPONSE (network/DNS/TLS)"
    return f"HTTP {status}"


def main(argv: list[str]) -> int:
    if len(argv) < 4:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    base_url, key_arg, models = argv[1], argv[2], argv[3:]
    key, label = resolve_key(key_arg)
    print(f"endpoint: {base_url}   key: {label}   ids: {len(models)}\n")
    verdicts: dict[str, int] = {}
    for model in models:
        status, body = probe(base_url, key, model)
        verdict = classify(status, body)
        verdicts[verdict] = verdicts.get(verdict, 0) + 1
        snippet = " ".join(body.split())[:150]
        print(f"{status:>4}  {verdict:<38} {model}")
        if snippet:
            print(f"      {snippet}")
    print("\nsummary:")
    for verdict, count in sorted(verdicts.items(), key=lambda kv: -kv[1]):
        print(f"  {count:>3}  {verdict}")
    if any(v.startswith("EXISTS, NOT ENTITLED") for v in verdicts):
        print(
            "\nAn EXISTS/NOT-ENTITLED result is not fixable in Hermes: report the "
            "exact ID to the platform so it can be opened for this key/team, and say "
            "so plainly."
        )
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
