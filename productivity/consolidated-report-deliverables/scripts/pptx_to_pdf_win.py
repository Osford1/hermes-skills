#!/usr/bin/env python
"""Export a .pptx to PDF with PowerPoint COM, for Windows boxes without LibreOffice.

Usage:
    python pptx_to_pdf_win.py deck.pptx [-o out.pdf] [--pngs DIR] [--dpi 110]

Requires pywin32 (win32com) and PowerPoint installed. The optional PNG step needs
poppler's pdftoppm (ships with MiKTeX on this box).

Prints the PDF path, then each PNG path. Exits non-zero on failure.
"""

import argparse
import os
import shutil
import subprocess
import sys

PDF_FORMAT = 32  # PowerPoint ppSaveAsPDF
MIKTEX_PDFTOPPM = r"C:\Users\<you>\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdftoppm.exe"


def export_pdf(pptx: str, pdf: str) -> None:
    import win32com.client  # imported late so --help works without pywin32

    app = win32com.client.Dispatch("PowerPoint.Application")
    pres = None
    try:
        pres = app.Presentations.Open(os.path.abspath(pptx), WithWindow=False)
        pres.SaveAs(os.path.abspath(pdf), PDF_FORMAT)
    finally:
        if pres is not None:
            pres.Close()
        app.Quit()


def find_pdftoppm():
    exe = shutil.which("pdftoppm")
    if exe:
        return exe
    if os.path.exists(MIKTEX_PDFTOPPM):
        return MIKTEX_PDFTOPPM
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description="pptx -> PDF (+ per-slide PNGs) via PowerPoint COM")
    ap.add_argument("pptx")
    ap.add_argument("-o", "--out", help="output PDF path (default: beside the pptx)")
    ap.add_argument("--pngs", help="directory for per-slide PNGs")
    ap.add_argument("--dpi", type=int, default=110)
    args = ap.parse_args()

    pdf = args.out or os.path.splitext(args.pptx)[0] + ".pdf"
    try:
        export_pdf(args.pptx, pdf)
    except Exception as exc:  # COM failures are opaque; surface them plainly
        print(f"export failed: {exc}", file=sys.stderr)
        return 1
    print(os.path.abspath(pdf))

    if not args.pngs:
        return 0

    os.makedirs(args.pngs, exist_ok=True)
    exe = find_pdftoppm()
    if not exe:
        print("pdftoppm not found: PDF written, no PNGs", file=sys.stderr)
        return 0
    subprocess.run(
        [exe, "-png", "-r", str(args.dpi), os.path.abspath(pdf), os.path.join(args.pngs, "slide")],
        check=True,
    )
    for name in sorted(os.listdir(args.pngs)):
        if name.startswith("slide") and name.endswith(".png"):
            print(os.path.join(args.pngs, name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
