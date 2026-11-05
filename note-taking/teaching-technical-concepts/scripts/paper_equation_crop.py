"""Crop a labelled equation out of a paper PDF at glyph-readable resolution.

WHY THIS EXISTS
---------------
A paper's text layer linearises two-dimensional mathematics into a token stream and silently
DROPS calligraphic letters. An objective ``J_s(q)`` comes back as a bare ``s(q)``; a weighted
``W_k`` norm comes back as a bare ``k``; a null-space basis matrix comes back as nothing at
all. Nothing warns you. A notation glossary, a reimplementation or a summary built on that
extraction will define the wrong symbol with total confidence.

Read the RENDERED crop instead, and use the text layer only for structural cues.

QUICK USE
---------
    python paper_equation_crop.py PAPER.pdf --index            # what is on each page
    python paper_equation_crop.py PAPER.pdf --index 5 6 7      # just these pages
    python paper_equation_crop.py PAPER.pdf "(16)" --page 6 -o eq16.png
    python paper_equation_crop.py PAPER.pdf "(2a)" --page 5 --up 45 --down 40

Then hand the PNG to vision_analyze with a CHARACTER-LEVEL question::

    "State the EXACT letter of the symbol before the summation and its subscript.
     If the glyph is unclear, say so. Do not infer from context."

GEOMETRY RULES THAT COST TIME WHEN IGNORED
------------------------------------------
* Locate by the equation NUMBER, never by content. ``search_for("(16)")`` returns the
  number's bbox and the body sits just LEFT of it, within that column.
* The body can run several lines ABOVE the number -- pad the top generously.
* A multi-line equation's number usually sits on a MIDDLE line, so the equation's LAST line
  is BELOW the number. If the transcription stops short, raise --down and re-crop.
* 600 dpi is the working setting for glyphs. A 150-200 dpi whole-page render is fine for
  layout and useless for reading a subscript.
* Two-column papers: the number's x position tells you which column you are in.

CROSS-CHECK PROTOCOL
--------------------
Neither source is authoritative alone. Require the crop and the text layer to agree before
relying on a symbol. Where they disagree, the crop wins for glyph IDENTITY and the prose
wins for what the symbol MEANS -- papers gloss their own notation inconsistently. Do not
silently "repair" oddities: papers really do print two letterforms for one quantity, and
really do print a transposed abbreviation. Report "as printed" and gloss the meaning.
"""

from __future__ import annotations

import argparse
import re
import sys

import pymupdf  # pip install pymupdf  (the old `fitz` alias also works but warns)

HEADING_RE = re.compile(r"^\d+(\.\d+)*\.?\s+[A-Z]")
EQNUM_RE = re.compile(r"\(([0-9]+[a-z]?)\)")


def cmd_index(doc, args) -> int:
    """Per-page text weight, the equation numbers present, and heading-ish lines."""
    for i, page in enumerate(doc, start=1):
        if args.pages and i not in args.pages:
            continue
        text = page.get_text()
        eqs = EQNUM_RE.findall(text)
        print(f"p{i:>3}  {len(text):>6} chars   eqs: {', '.join(eqs[:14]) or '-'}")
        for line in text.splitlines():
            s = line.strip()
            if s and len(s) < 70 and HEADING_RE.match(s):
                print(f"            {s}")
    return 0


def _pick_hit(page, label: str, side: str):
    hits = page.search_for(label)
    if not hits:
        return None
    if side == "left":
        return min(hits, key=lambda r: r.x0)
    if side == "top":
        return min(hits, key=lambda r: r.y0)
    return max(hits, key=lambda r: r.x1)   # default: rightmost = the equation number


def cmd_crop(doc, args) -> int:
    page = doc[args.page - 1]
    hit = _pick_hit(page, args.label, args.side)
    if hit is None:
        print(f"!! {args.label!r} not found on page {args.page}", file=sys.stderr)
        print("   run --index on that page and check the number is not split across\n"
              "   lines or objects (try the bare digits, e.g. '16')", file=sys.stderr)
        return 1

    print(f"  {args.label}  x {hit.x0:.0f}-{hit.x1:.0f}  y {hit.y0:.0f}-{hit.y1:.0f}")

    rect = pymupdf.Rect(hit.x1 - args.width, hit.y0 - args.up,
                        hit.x1 + args.pad_right, hit.y1 + args.down)
    rect &= page.rect            # clamp inside the page
    pix = page.get_pixmap(dpi=args.dpi, clip=rect)

    out = args.out or f"eq_p{args.page}_{label.strip('()')}.png"
    pix.save(out)
    print(f"  clip {rect}  ->  {out}  ({pix.width}x{pix.height} at {args.dpi} dpi)")
    print("  if the last line is cut off, re-run with a larger --down;")
    print("  if the first line is cut off, a larger --up.")
    return 0


def cmd_locate(doc, args) -> int:
    page = doc[args.page - 1]
    hits = page.search_for(args.label)
    if not hits:
        print(f"!! {args.label!r} not found on page {args.page}", file=sys.stderr)
        return 1
    for r in hits:
        print(f"  x {r.x0:7.1f}-{r.x1:7.1f}   y {r.y0:7.1f}-{r.y1:7.1f}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Crop a labelled equation out of a paper PDF at glyph-readable resolution.",
        epilog="Run --index first to see which pages carry equations.")
    ap.add_argument("pdf")
    ap.add_argument("label", nargs="?", help="equation label as printed, e.g. '(2a)' or '(16)'")
    ap.add_argument("--page", type=int, default=1, help="1-based page number")
    ap.add_argument("--index", nargs="*", type=int, default=None, metavar="PAGE",
                    help="print a per-page index (optionally for these pages) and exit")
    ap.add_argument("--locate", action="store_true", help="only print bboxes, do not render")
    ap.add_argument("--side", choices=["right", "left", "top"], default="right",
                    help="which search hit is the equation number (default rightmost)")
    ap.add_argument("--dpi", type=int, default=600)
    ap.add_argument("--width", type=float, default=235.0, help="crop width in points, leftward from the label")
    ap.add_argument("--up", type=float, default=35.0, help="points to include ABOVE the label's top")
    ap.add_argument("--down", type=float, default=38.0, help="points to include BELOW the label's bottom")
    ap.add_argument("--pad-right", type=float, default=4.0)
    ap.add_argument("-o", "--out", default=None)
    args = ap.parse_args(argv)

    doc = pymupdf.open(args.pdf)
    print(f"{args.pdf}  ({doc.page_count} pages)")

    if args.index is not None:
        args.pages = set(args.index) or None
        return cmd_index(doc, args)
    if args.label is None:
        ap.error("give an equation label, or use --index")
    if args.locate:
        return cmd_locate(doc, args)
    return cmd_crop(doc, args)


if __name__ == "__main__":
    sys.exit(main())
