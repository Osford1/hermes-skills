#!/usr/bin/env python3
"""Verify a mechanical cleanup pass against its pre-edit backup.

Usage:
    python verify_mechanical_edit.py BACKUP.md CLEANED.md

Hard assertions (exit 1 on failure): no semicolon, no em/en dash, no
space-before-punctuation, no stray asterisk outside a horizontal rule, no
number lost, no table block changed column count.

Reported for human review: every prose line that differs from the backup.
Each one must be a deliberate (old, new) pair from your transform list; if a
differing line is not in that list, the pass invented it.

Lines that are only markers (--- *** ___) are excluded from mark counting and
from the prose comparison, since they are structure, not emphasis.
"""
from __future__ import annotations

import collections
import re
import sys

HR = re.compile(r"^[*_-]{3,}$")
TABLE = re.compile(r"^\s*\|")
NUMBER = re.compile(r"\d+(?:\.\d+)?")

# name -> (pattern, severity). "hard" fails the run, "report" only prints.
MARKS = {
    "semicolon": (re.compile(r";"), "hard"),
    "em dash": (re.compile("\u2014"), "hard"),
    "en dash": (re.compile("\u2013"), "hard"),
    "space before , . : ;": (re.compile(r"\s+[,.:;]"), "hard"),
    "asterisk outside rules": (re.compile(r"\*"), "hard"),
    "double underscore emphasis": (re.compile(r"(?<![\w_])__(?=\S)"), "report"),
}


def read_text(path: str) -> str:
    with open(path, "rb") as fh:
        return fh.read().decode("utf-8-sig")


def strip_rules(text: str) -> str:
    return "\n".join(line for line in text.splitlines() if not HR.match(line.strip()))


def count_marks(text: str) -> dict:
    body = strip_rules(text)
    return {name: len(pattern.findall(body)) for name, (pattern, _) in MARKS.items()}


def normalise(line: str) -> str:
    return re.sub(r"\s+", " ", line.strip())


def prose_lines(text: str) -> list:
    return [normalise(l) for l in strip_rules(text).splitlines() if l.strip()]


def table_shapes(lines: list) -> list:
    """Column counts for each contiguous table block, in order."""
    shapes, run = [], []
    for line in lines:
        if TABLE.match(line):
            run.append(line.count("|"))
        elif run:
            shapes.append(tuple(run))
            run = []
    if run:
        shapes.append(tuple(run))
    return shapes


def line_endings(path: str) -> tuple:
    with open(path, "rb") as fh:
        raw = fh.read()
    crlf = raw.count(b"\r\n")
    return crlf, raw.count(b"\n") - crlf


def main(argv: list) -> int:
    if len(argv) != 3:
        print(__doc__)
        return 2

    backup_path, cleaned_path = argv[1], argv[2]
    before, after = read_text(backup_path), read_text(cleaned_path)
    failed = False

    print("== marks ==")
    marks_before, marks_after = count_marks(before), count_marks(after)
    for name, (_, severity) in MARKS.items():
        print(f"  {name:28s} {marks_before[name]:5d} -> {marks_after[name]:5d}")
        if marks_after[name] and severity == "hard":
            print(f"  FAIL: {name!r} survives in the cleaned file")
            failed = True

    print("\n== line endings ==")
    for label, path in (("backup", backup_path), ("cleaned", cleaned_path)):
        crlf, lone_lf = line_endings(path)
        print(f"  {label:8s} crlf={crlf:6d} lone_lf={lone_lf:6d}")
    if line_endings(backup_path)[0] == 0 and line_endings(cleaned_path)[0] > 0:
        print("  FAIL: the cleaned file gained CRLF; rewrite with newline=''")
        failed = True

    print("\n== prose lines differing from the backup ==")
    pool = collections.Counter(prose_lines(before))
    changed = [line for line in prose_lines(after) if not pool[line]]
    print(f"  {len(changed)} line(s). Each must be a deliberate pair in your transform list:")
    for line in changed:
        print(f"    - {line[:160]}")

    print("\n== numeric tokens ==")
    numbers_before = set(NUMBER.findall(strip_rules(before)))
    numbers_after = set(NUMBER.findall(strip_rules(after)))
    gained = sorted(numbers_after - numbers_before)
    lost = sorted(numbers_before - numbers_after)
    print(f"  gained: {', '.join(gained) if gained else 'none'}")
    print(f"  lost:   {', '.join(lost) if lost else 'none'}")
    if lost:
        print("  FAIL: a number disappeared, content was dropped")
        failed = True
    if gained:
        print("  REVIEW: a number appeared. It must be a correction you verified")

    print("\n== table shapes ==")
    shapes_before = table_shapes(strip_rules(before).splitlines())
    shapes_after = table_shapes(strip_rules(after).splitlines())
    if shapes_before == shapes_after:
        print(f"  {len(shapes_before)} block(s), unchanged")
    else:
        print("  FAIL: table structure changed")
        print(f"    backup:  {shapes_before}")
        print(f"    cleaned: {shapes_after}")
        failed = True

    print("\nRESULT:", "FAIL" if failed else "no hard failures")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
