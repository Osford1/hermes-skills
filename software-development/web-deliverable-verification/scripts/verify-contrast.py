#!/usr/bin/env python3
"""Measure text contrast and glass readability on a RENDERED page.

Why this exists: CSS can be entirely correct and still ship unreadable text.
`opacity`, a translucent surface, a moving background and a disabled state all change
what is actually behind a glyph. Only the pixels answer it.

Input: a directory of capture pairs made by the browser step:
    <screen>.png         the page screenshotted with every glyph hidden, via
                         *,*::before,*::after{color:transparent!important;
                                             -webkit-text-fill-color:transparent!important}
    <screen>.rects.json  one entry per visible text run:
                         {t, c, col, fs, x, y, x2, y2, w, h}
                         col = that element's computed colour (captured BEFORE hiding);
                         x,y and x2,y2 = two sample points inside the run

Capture one pair per screen — a page whose screens are hidden one at a time has
nothing to sample on the screens that are not up. Copy every capture to its own
filename as you take it; a fixed capture path overwrites the previous shot.

Usage:   python verify_contrast.py <capture-dir>
Contract: text >= 4.5:1. Exit 0 = all pass, 1 = at least one failure.
Also reports the in-card luminance ramp (a flat result means the "glass" is an
opaque fill, whatever the CSS claims); target >= 2.5 L* per card.

Requires Pillow.
"""
import json
import os
import sys
from PIL import Image

MIN_TEXT = 4.5
MIN_RAMP = 2.5


def lin(c):
    c = c / 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lum(rgb):
    r, g, b = rgb[:3]
    return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)


def contrast(a, b):
    la, lb = lum(a), lum(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def lstar(rgb):
    y = lum(rgb)
    return 116 * y ** (1 / 3) - 16 if y > 0.008856 else 903.3 * y


def parse_color(s):
    """'rgb(28, 42, 40)' or 'rgba(28,42,40,0.5)' -> (28, 42, 40)"""
    body = s[s.find("(") + 1:s.find(")")]
    out = []
    for n in body.replace(",", " ").split()[:3]:
        out.append(round(float(n[:-1]) * 2.55) if n.endswith("%") else int(round(float(n))))
    return tuple(out)


def patch(img, x, y, k=2):
    """average a small square so one stray antialiased pixel cannot decide anything"""
    px = img.load()
    W, H = img.size
    acc, n = [0, 0, 0], 0
    for dx in range(-k, k + 1):
        for dy in range(-k, k + 1):
            p = px[min(max(x + dx, 0), W - 1), min(max(y + dy, 0), H - 1)]
            for i in range(3):
                acc[i] += p[i]
            n += 1
    return tuple(v // n for v in acc)


def main(d):
    screens = sorted({f.split(".rects.json")[0] for f in os.listdir(d)
                      if f.endswith(".rects.json")})
    if not screens:
        print(f"no <screen>.rects.json pairs in {d}")
        return 1

    all_rows, fails = [], []
    for name in screens:
        img = Image.open(os.path.join(d, f"{name}.png")).convert("RGB")
        rows = json.load(open(os.path.join(d, f"{name}.rects.json")))
        print(f"\n=== {name} ({img.size[0]}x{img.size[1]}) — {len(rows)} text runs ===")
        for r in rows:
            col = parse_color(r["col"])
            bg = min((patch(img, r["x"], r["y"]), patch(img, r["x2"], r["y2"])), key=lum)
            c = contrast(col, bg)
            all_rows.append(c)
            ok = c >= MIN_TEXT
            if not ok:
                fails.append((name, r.get("t", "?"), r.get("c", "?"), round(c, 2), col, bg,
                              r.get("fs")))
            print(f"  {'OK  ' if ok else 'FAIL'} {c:5.2f}:1  {r.get('t','?'):7s} "
                  f"{str(r.get('c',''))[:22]:22s} {str(r.get('fs','')):>6s}  "
                  f"text#{''.join(f'{v:02x}' for v in col)}  "
                  f"on#{''.join(f'{v:02x}' for v in bg)}")

    # in-card ramp: a vertical strip inside each card, top against bottom
    for name in screens:
        rows = [r for r in json.load(open(os.path.join(d, f"{name}.rects.json")))
                if str(r.get("c", "")).startswith("card") and r.get("h", 0) > 40]
        if not rows:
            continue
        img = Image.open(os.path.join(d, f"{name}.png")).convert("RGB")
        print(f"\n=== in-card ramp — {name} ===")
        for i, r in enumerate(rows, 1):
            x = r["x2"] - 12
            ys = [r["y"] - 10 + k for k in range(0, max(r["h"] - 20, 8), 6)]
            ls = [lstar(patch(img, x, y, 1)) for y in ys]
            ramp = max(ls) - min(ls)
            verdict = "OK (>= %.1f)" % MIN_RAMP if ramp >= MIN_RAMP else "FLAT"
            print(f"  card {i:>2}  h={r['h']:>3}px  L* {min(ls):5.1f} -> {max(ls):5.1f}  "
                  f"ramp = {ramp:4.2f} L*   {verdict}")

    print(f"\n{'=' * 66}")
    print(f"text runs measured: {len(all_rows)}")
    print(f"worst contrast overall: {min(all_rows):.2f}:1")
    print(f"failures (<{MIN_TEXT}:1): {len(fails)}")
    for f in fails:
        print("  ", f)
    return 1 if fails else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
