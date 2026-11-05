#!/usr/bin/env python3
"""Index a slide-deck PDF, flag the image-only slides, and prepare them for vision reading.

Prereq:  python -m pip install pymupdf
         python -m pip install pillow      # only needed for --stack and --zoom

Usage:
    python slide_deck_locate.py deck.pdf --triage
    python slide_deck_locate.py deck.pdf --grep yzantine
    python slide_deck_locate.py deck.pdf --render 47-50 --dpi 150
    python slide_deck_locate.py deck.pdf --stack "17,19;22,24;25,26"
    python slide_deck_locate.py deck.pdf --images 14 --zoom 5

Behaviour:
  * --grep / --triage print a per-page map: page number, text-layer size, the first three non-empty
    lines, and a THIN flag for pages whose text layer is too small to be the real content.
  * THIN defaults to 120 chars, not 40: on a slide deck a 40-120 char extract is "title + one
    fragment", which is still a figure/formula slide. Lower it with --thin for a paper's text pages.
  * A THIN page is a content slide, not an empty one - read it with vision_analyze instead of trusting
    the extract. Use a distinctive keyword fragment ('yzantine' beats 'Byzantine').
  * --render writes page<NN>.png for the given page range at --dpi (150 default: formulas need it).
  * --stack writes pair_<a>_<b>.png with the two pages stacked vertically, so ONE vision_analyze call
    covers two slides - roughly halves the calls on a formula-heavy deck.
  * --images extracts the rasters embedded on the given pages (the equations), prints each one's size
    and its rect on the page, and with --zoom writes an upscaled copy to read glyph-by-glyph. The
    equation is the wide short raster next to the bullet; the big square-ish one is the decorative
    figure. See references/reading-formulas-from-slides.md.

Inline equivalent of what this wraps:
    import pymupdf
    doc = pymupdf.open(pdf)
    for i, page in enumerate(doc, 1):
        print(i, len(page.get_text().strip()), page.get_text()[:120].replace('\n', ' | '))
    pix = doc[n - 1].get_pixmap(dpi=150)   # n is a 1-based page number
    pix.save(f"page{n}.png")
"""
from __future__ import annotations

import argparse
import os
import sys
import tempfile

THIN_CHARS = 120


def parse_pages(spec: str, total: int):
    out = set()
    for part in spec.split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            lo, hi = part.split("-", 1)
            out.update(range(int(lo), int(hi) + 1))
        else:
            out.add(int(part))
    return sorted(p for p in out if 1 <= p <= total)


def parse_pairs(spec: str, total: int):
    pairs = []
    for chunk in spec.split(";"):
        chunk = chunk.strip()
        if not chunk:
            continue
        a, b = (int(x) for x in chunk.split(","))
        if 1 <= a <= total and 1 <= b <= total:
            pairs.append((a, b))
    return pairs


def stack_pages(doc, a: int, b: int, dpi: int, outdir: str):
    """Two slides, one image: the cheap way to halve vision_analyze calls."""
    from PIL import Image  # noqa: PLC0415

    ims = []
    for n in (a, b):
        path = os.path.join(outdir, f"p{n}.png")
        doc[n - 1].get_pixmap(dpi=dpi).save(path)
        ims.append(Image.open(path).convert("RGB"))
    w = max(i.width for i in ims)
    h = sum(i.height for i in ims) + 10
    canvas = Image.new("RGB", (w, h), "white")
    y = 0
    for im in ims:
        canvas.paste(im, (0, y))
        y += im.height + 10
    out = os.path.join(outdir, f"pair_{a}_{b}.png")
    canvas.save(out)
    print(f"stacked {out}  (top = slide {a}, bottom = slide {b})")


def dump_images(doc, page_no: int, outdir: str, zoom: int):
    """Pull the rasters off one slide - this is how a pasted equation is read at all."""
    page = doc[page_no - 1]
    for idx, info in enumerate(page.get_images(full=True)):
        xref = info[0]
        rects = page.get_image_rects(xref)
        data = doc.extract_image(xref)
        path = os.path.join(outdir, f"p{page_no}_img{idx}.{data['ext']}")
        with open(path, "wb") as fh:
            fh.write(data["image"])
        shape = "wide+short -> likely the EQUATION" if info[2] > 3 * info[3] else "large -> figure/tile"
        print(f"{path}  {info[2]}x{info[3]}px  {shape}")
        print(f"      rects on page: {[tuple(round(v) for v in r) for r in rects]}")
        if zoom > 1:
            try:
                from PIL import Image  # noqa: PLC0415
            except ImportError:
                print("      (pillow missing - skipping --zoom)")
                continue
            im = Image.open(path).convert("L")
            big = im.resize((im.width * zoom, im.height * zoom), Image.LANCZOS)
            zpath = os.path.join(outdir, f"p{page_no}_img{idx}_x{zoom}.png")
            big.save(zpath)
            w, h = big.size
            print(f"      magnified -> {zpath} {w}x{h}")
            third = w // 3
            for k in range(3):
                x0 = max(0, k * third - 40)
                x1 = min(w, (k + 1) * third + 40)
                cpath = os.path.join(outdir, f"p{page_no}_img{idx}_x{zoom}_c{k}.png")
                big.crop((x0, 0, x1, h)).save(cpath)
            print(f"      crops     -> {page_no}_img{idx}_x{zoom}_c0..2.png (read each separately)")


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("pdf")
    ap.add_argument("--grep", help="case-insensitive keyword; a distinctive fragment works better")
    ap.add_argument("--triage", action="store_true", help="map every page's text density")
    ap.add_argument("--render", help="page range to render, e.g. 47-50 or 47,49")
    ap.add_argument("--stack", help='pairs to stack into one image: "17,19;22,24"')
    ap.add_argument("--images", help="page numbers whose embedded rasters to extract, e.g. 14")
    ap.add_argument("--zoom", type=int, default=4, help="magnification for --images (default 4)")
    ap.add_argument("--dpi", type=int, default=150)
    ap.add_argument("--thin", type=int, default=THIN_CHARS)
    ap.add_argument("--context", type=int, default=2, help="extra pages either side of a --grep hit")
    ap.add_argument("--outdir", default=os.path.join(tempfile.gettempdir(), "slide_pages"))
    args = ap.parse_args()

    try:
        import pymupdf
    except ImportError:
        print("pymupdf missing - run: python -m pip install pymupdf", file=sys.stderr)
        return 2

    doc = pymupdf.open(args.pdf)
    total = doc.page_count
    texts = [pg.get_text() for pg in doc]
    chars = sum(len(t.strip()) for t in texts)
    print(f"{os.path.basename(args.pdf)}: {total} pages, {chars} chars of text layer")
    if chars < 200 * total:
        print("  -> deck is mostly images; expect THIN to be the rule, not the exception")

    show = set()
    if args.grep:
        needle = args.grep.lower()
        hits = [i + 1 for i, t in enumerate(texts) if needle in t.lower()]
        print(f"hits for {args.grep!r}: {hits or 'none'}")
        for h in hits:
            show.update(range(max(1, h - args.context), min(total, h + args.context) + 1))
    elif args.triage or not (args.render or args.stack or args.images):
        show = set(range(1, total + 1))

    for n in sorted(show):
        body = texts[n - 1]
        lines = [l.strip() for l in body.splitlines() if l.strip()]
        flag = "THIN -> render + vision_analyze" if len(body.strip()) < args.thin else ""
        print(f"p{n:>3} [{len(body.strip()):>4} chars] {flag}")
        preview = " | ".join(lines[:3])[:160] if lines else "(no text layer)"
        print("      " + preview)

    os.makedirs(args.outdir, exist_ok=True)
    if args.render:
        for n in parse_pages(args.render, total):
            path = os.path.join(args.outdir, f"page{n}.png")
            doc[n - 1].get_pixmap(dpi=args.dpi).save(path)
            print(f"rendered {path}")
    if args.stack:
        for a, b in parse_pairs(args.stack, total):
            stack_pages(doc, a, b, args.dpi, args.outdir)
    if args.images:
        for n in parse_pages(args.images, total):
            print(f"--- rasters on p{n} ---")
            dump_images(doc, n, args.outdir, args.zoom)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
