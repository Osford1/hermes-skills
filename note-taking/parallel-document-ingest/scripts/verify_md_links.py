#!/usr/bin/env python3
"""Verify wikilinks and frontmatter across many markdown files.

Built for bulk ingests, where pages are written in parallel and the failure mode is a
cross-link to a slug another writer never created, or named slightly differently.

Usage:
  python verify_md_links.py ROOT GLOB [GLOB ...] [--fm key1,key2]

  python verify_md_links.py "C:/Vault" "wiki/**/*.md"
  python verify_md_links.py "C:/Vault" "notes/2026-*.md" --fm title,type

Exit code 1 if any page has a dangling link or is missing a required frontmatter key.
Exit code 2 on bad usage.

TABLE-ESCAPE TRAP: inside a markdown table a wikilink's pipe is escaped, so a scan that
captures everything up to the first pipe picks up a trailing backslash and then reports
every table link as dangling. This script strips that trailing backslash. Do not silence
such a false positive by loosening the regex -- strip the backslash instead.
"""
import glob
import os
import re
import sys

LINK_RE = re.compile(r"\[\[([^\]|#]+)")
FM_RE = re.compile(r"^\s*---\n(.*?)\n---", re.S)
KEY_RE = re.compile(r"^(\w+):", re.M)
SKIP_DIRS = {"raw", ".obsidian", ".trash", ".git", ".claude", "node_modules"}


def index_by_basename(root):
    """basename(lower) -> [root-relative paths], for every .md under root."""
    by_base = {}
    for cur, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".md"):
                rel = os.path.relpath(os.path.join(cur, f), root).replace(os.sep, "/")
                by_base.setdefault(f[:-3].lower(), []).append(rel)
    return by_base


def links_in(text):
    out = []
    for m in LINK_RE.finditer(text):
        t = m.group(1).strip().rstrip("\\").strip()  # rstrip: table pipe-escaping
        if t.endswith(".md"):
            t = t[:-3]
        if t:
            out.append(t.lstrip("/"))
    return out


def fm_keys(text):
    m = FM_RE.match(text)
    return set(KEY_RE.findall(m.group(1))) if m else set()


def main(argv):
    raw = argv[1:]
    required, cleaned, skip_next = [], [], False
    for a in raw:
        if skip_next:
            skip_next = False
            continue
        if a == "--fm":
            skip_next = True
            continue
        if a.startswith("--fm="):
            continue
        cleaned.append(a)
    for i, a in enumerate(raw):  # support both --fm k1,k2 and --fm=k1,k2
        if a == "--fm" and i + 1 < len(raw):
            required = [k.strip() for k in raw[i + 1].split(",") if k.strip()]
        elif a.startswith("--fm="):
            required = [k.strip() for k in a.split("=", 1)[1].split(",") if k.strip()]

    if len(cleaned) < 2:
        print(__doc__)
        return 2
    root, patterns = cleaned[0], cleaned[1:]
    if not os.path.isdir(root):
        print("root is not a directory:", root)
        return 2

    by_base = index_by_basename(root)
    pages = []
    for pat in patterns:
        pages.extend(sorted(glob.glob(os.path.join(root, pat), recursive=True)))
    if not pages:
        print("no files matched:", patterns)
        return 1

    problems = 0
    for path in pages:
        rel = os.path.relpath(path, root).replace(os.sep, "/")
        text = open(path, encoding="utf-8", errors="replace").read()
        missing = [k for k in required if k not in fm_keys(text)]
        dangling, by_name = [], []
        for target in sorted(set(links_in(text))):
            if os.path.exists(os.path.join(root, target + ".md")):
                continue
            hits = by_base.get(os.path.basename(target).lower())
            if hits:
                by_name.append((target, hits[0]))
            else:
                dangling.append(target)

        ok = not dangling and not missing
        print(("[OK]      " if ok else "[PROBLEM] ") + rel)
        for k in missing:
            problems += 1
            print("    missing frontmatter key:", k)
        for t in dangling:
            problems += 1
            print("    DANGLING link:", t)
        for t, actual in by_name:
            print("    path differs, name-resolves:", t, "->", actual)

    print("\n%d page(s) checked, %d problem(s)." % (len(pages), problems))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
