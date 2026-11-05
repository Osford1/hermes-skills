#!/usr/bin/env python3
"""Verify a rendered 3D artifact from its pixels. Usage: verify-render.py shot.png [x0 y0 x1 y1]

No region  -> hue-bucket census over the whole frame (skips a 320px HUD on the left at 2x).
With region-> ASCII hue map of that rectangle, for finding out what is actually drawn.

Why hue buckets and not exact colours: a tone-mapped accent shifts hue. #ff4d4d under ACES
renders around hue 20-25 deg, so a naive "red = hue < 20" test reports a drawn element as
missing. Always print the map before concluding something is absent.
"""
import sys, colorsys
from PIL import Image


def hue_class(r, g, b):
    mx, mn = max(r, g, b), min(r, g, b)
    if mx == 0:
        return None, 0
    return colorsys.rgb_to_hsv(r/255, g/255, b/255)[0]*360, (mx-mn)/mx


def census(path, hud_px=700):
    im = Image.open(path).convert('RGB')
    W, H = im.size
    px = im.load()
    counts = {'red': 0, 'amber': 0, 'green': 0, 'teal': 0, 'blue': 0}
    strong = tot = 0
    red_pts = []
    for y in range(0, H, 2):
        for x in range(hud_px, W, 2):
            h, s = hue_class(*px[x, y]); tot += 1
            if h is None or s < 0.22 or max(px[x, y]) < 45:
                continue
            strong += 1
            if h >= 330 or h < 25:   k = 'red'
            elif h < 60:             k = 'amber'
            elif h < 150:            k = 'green'
            elif h < 210:            k = 'teal'
            else:                    k = 'blue'
            counts[k] += 1
            if k == 'red':
                red_pts.append((x, y))
    print(f"{path}: {W}x{H}  saturated={strong/tot*100:.2f}% of scene area")
    print("  " + "  ".join(f"{k}={v/tot*100:.3f}%" for k, v in counts.items() if v))
    if red_pts:
        xs = [p[0] for p in red_pts]; ys = [p[1] for p in red_pts]
        print(f"  red extent {max(xs)-min(xs)} x {max(ys)-min(ys)} px ({len(red_pts)} samples)"
              " — a long thin extent means a bar/line, a small square means a dot")


def hmap(path, x0, y0, x1, y1, step=4):
    im = Image.open(path).convert('RGB')
    px = im.load()
    print(f"hue map x {x0}..{x1} y {y0}..{y1}  (1 char = {step}px; R A G T B = hue, W light, g grey, . dark)")
    for y in range(y0, y1, step):
        row = ''
        for x in range(x0, x1, step):
            r, g, b = px[x, y]
            h, s = hue_class(r, g, b)
            mx = max(r, g, b)
            if mx < 40:              ch = '.'
            elif s < 0.20:           ch = 'W' if mx > 150 else 'g'
            elif h >= 330 or h < 25: ch = 'R'
            elif h < 60:             ch = 'A'
            elif h < 150:            ch = 'G'
            elif h < 210:            ch = 'T'
            else:                    ch = 'B'
            row += ch
        print(f"{y:5d} {row}")


if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) >= 5:
        hmap(args[0], *[int(v) for v in args[1:5]])
    else:
        census(args[0])
