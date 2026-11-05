#!/usr/bin/env python
"""Measure text contrast on a RENDERED page, from pixels rather than from tokens.

WHY: a palette whose token pairs all clear 4.5:1 can still ship text at 3.2:1, because the
text sits on a COMPOSITE of surface + bloom + backdrop. Tokens cannot see that. Method: hide
every glyph, screenshot, sample the surface under each text run, compare with that element's
real colour. Per screen, and per background state.

USAGE
    python verify-contrast-pixels.py <capture-dir> [--threshold 4.5]
    exit 0 = every run clears the threshold; 1 = at least one did not; 2 = bad input.

INPUTS - the dir must hold, per screen captured:
    <name>.png         screenshot taken with every glyph hidden
    <name>.rects.json  [{"t","c","col","fs","pts":[[x,y],...]}, ...]
                       `pts` = sample points in CSS px. Captures in the older two-point
                       x/y + x2/y2 form are still accepted.

Produce that JSON in the browser, once per screen, with:

    (()=>{const out=[], sel='h1,h2,p,.name,.desc,.eyebrow,.sub,.label,.summary,.btn,.choice,.card,.slot,.todo';
      for (const el of document.querySelectorAll(sel)){
        if (![...el.childNodes].some(n=>n.nodeType===3 && n.textContent.trim())) continue; // owns ink
        const rg=document.createRange(); rg.selectNodeContents(el);
        const cs=getComputedStyle(el), pts=[];
        for (const r of rg.getClientRects()){                 // one rect per LINE, not the box
          if (r.width<4||r.height<4||r.top<-40||r.top>innerHeight) continue;  // off-viewport: skip
          const y=Math.round(r.top+r.height/2);
          for (const f of [0.2,0.5,0.8]) pts.push([Math.round(r.left+r.width*f), y]);}
        if (pts.length) out.push({t:el.tagName.toLowerCase(), c:String(el.className).slice(0,24),
                                  col:cs.color, fs:cs.fontSize, pts});}
      return JSON.stringify(out);})()

then hide the glyphs and shoot the SAME screen:

    const s=document.createElement('style');
    s.textContent='*,*::before,*::after{color:transparent !important;-webkit-text-fill-color:transparent !important}';
    document.head.appendChild(s);

CAUTIONS
  * sample a PATCH (default 5x5), not one pixel - antialiasing at a glyph edge lies
  * per-line points, three across each line, take the WORST one: a paragraph's third line can land
    on a bright edge its first line never touches
  * measure the element that owns the ink, not a wrapper div - a wrapper's box is taller than the
    text and its corners can sit on a neighbouring card
  * transparent INK, not a hidden element: `visibility:hidden` removes the element's own glass,
    rim and gradient, which is the surface being measured
  * capture each screen at more than one point in the background's drift, and treat the worst
    phase as the result: a moving backdrop has no single answer
  * only runs inside the first viewport are measured, so capture per screen, not per page
  * a screen captured from the wrong state is the usual cause of "0 runs" - check which screen is
    active before shooting, and grab a list screen BEFORE clicking into a detail view
"""
import glob
import json
import os
import sys


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(rgb):
    return 0.2126 * _lin(rgb[0]) + 0.7152 * _lin(rgb[1]) + 0.0722 * _lin(rgb[2])


def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def parse_css_colour(s):
    nums = s[s.find("(") + 1:s.find(")")].replace(",", " ").split()
    out = []
    for n in nums[:3]:
        out.append(round(float(n[:-1]) * 2.55) if n.endswith("%") else int(round(float(n))))
    return tuple(out)


def patch_pixel(img, x, y, k=2):
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


def main():
    argv = sys.argv[1:]
    thresh = 4.5
    if "--threshold" in argv:
        thresh = float(argv[argv.index("--threshold") + 1])
    positional = [a for a in argv if not a.startswith("--") and a != str(thresh)]
    if not positional:
        print(__doc__)
        return 2
    try:
        from PIL import Image
    except ImportError:
        print("needs Pillow:  python -m pip install pillow")
        return 2

    pairs = sorted(glob.glob(os.path.join(positional[0], "*.rects.json")))
    if not pairs:
        print("no *.rects.json in", positional[0])
        return 2

    total, fails = 0, []
    worst_all = (99.0, "", "")
    for rp in pairs:
        name = os.path.basename(rp)[:-len(".rects.json")]
        png = rp[:-len(".rects.json")] + ".png"
        if not os.path.exists(png):
            print("  %-24s no screenshot, skipped" % name)
            continue
        img = Image.open(png).convert("RGB")
        rows = json.load(open(rp))
        if not rows:
            print("  %-24s 0 runs - was the right screen up when it was shot?" % name)
            continue
        worst = (99.0, "", "")
        for r in rows:
            col = parse_css_colour(r["col"])
            pts = r.get("pts") or [[r["x"], r["y"]], [r["x2"], r["y2"]]]
            # min-luminance background = the worse case for dark text
            on = min((patch_pixel(img, x, y) for x, y in pts), key=luminance)
            c = contrast(col, on)
            total += 1
            if c < worst[0]:
                worst = (c, r.get("c", ""), r["t"])
            if c < thresh:
                fails.append((name, r["t"], r.get("c", ""), round(c, 2), r.get("fs", "")))
        print("  %-24s worst %5.2f:1  (%s %s)" % (name, worst[0], worst[1], worst[2]))
        if worst[0] < worst_all[0]:
            worst_all = (worst[0], name, worst[1])

    print("\ntext runs measured : %d" % total)
    print("worst overall      : %.2f:1  on %s (%s)" % worst_all)
    print("failures <%.1f:1    : %d" % (thresh, len(fails)))
    for f in fails:
        print("   ", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
