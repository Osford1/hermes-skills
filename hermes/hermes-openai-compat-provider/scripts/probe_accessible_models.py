#!/usr/bin/env python3
"""Probe every model on an OpenAI-compatible endpoint to find what YOUR key can actually call.

Many model aggregators serve the FULL platform catalog at GET /v1/models while the
key is bound to a team with a LIMITED subscription. This script lists the catalog,
fires a minimal chat/completions at each, and buckets them.

Usage:
    python probe_accessible_models.py <base_url> <api_key> [--max-token 1]

base_url is the OpenAI-compatible root, e.g. https://ai.paratera.com/v1
    (pass /v1, NOT the bare host). Prints three groups:
      ACCESSIBLE   -> HTTP 200 (chat-capable AND the key can use it)
      TEAM_BLOCKED -> HTTP 403 "team not allowed to access model" (key/subscription)
      OTHER        -> 4xx/5xx (non-chat model — image/video/tts/embeddings — or misc)

A 403 "team not allowed to access model" is the tell that /models lied about reach.
Non-chat models returning 400/404 to chat/completions are NOT "key broken".
"""
import json
import sys
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

BASE = sys.argv[1].rstrip("/")
KEY = sys.argv[2]


def get_catalog():
    req = urllib.request.Request(BASE + "/models", headers={"Authorization": "Bearer " + KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return [m["id"] for m in json.load(r)["data"]]


def probe(mid):
    body = json.dumps({"model": mid, "messages": [{"role": "user", "content": "hi"}], "max_tokens": 1}).encode()
    req = urllib.request.Request(BASE + "/chat/completions", data=body, headers={
        "Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    try:
        return (mid, urllib.request.urlopen(req, timeout=40).status)
    except urllib.error.HTTPError as e:
        return (mid, e.code)
    except Exception as e:
        return (mid, 0)  # network error


def main():
    models = get_catalog()
    with ThreadPoolExecutor(max_workers=16) as ex:
        results = list(ex.map(probe, models))

    ok = sorted(m for m, c in results if c == 200)
    blocked = sorted(m for m, c in results if c == 403)
    other = sorted(m for m, c in results if c not in (200, 403))

    print("CATALOG:", len(models), "ACCSESSIBLE:", len(ok), "TEAM_BLOCKED:", len(blocked), "OTHER:", len(other))
    print("\n=== ACCESSIBLE (200) ===")
    print("\n".join(ok))
    print("\n=== TEAM-BLOCKED (403) ===")
    print("\n".join(blocked))
    print("\n=== OTHER ===")
    for m in other:
        print(" ", m)


if __name__ == "__main__":
    main()
