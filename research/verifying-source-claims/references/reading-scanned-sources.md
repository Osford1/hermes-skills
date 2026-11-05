# Reading a scanned source

A page image is an instrument, and every number taken from one is that instrument's reading rather than
the source's own claim. These are the mechanics that make such a reading trustworthy and repeatable.
They apply to any image-only source: textbook chapters, lecture scans, photographed tables, PDFs that
arrived through a chat app.

## Render before you read

`read_file` yields nothing usable from an image-only PDF — every page reports as needing OCR. Render the
page instead; use pymupdf, which is already installed alongside the extractor's dependencies:

```python
import pymupdf
doc = pymupdf.open(path)
doc[8].get_pixmap(dpi=320).save("p8.png")          # one sheet at 320 dpi
```

- **300–320 dpi is the floor for tables and small type.** 150 dpi does not fail loudly; it substitutes
  plausible digits.
- Render into a scratch dir outside the user's document tree (`$LOCALAPPDATA/Temp/<topic>/` on Windows).
- Then read with `vision_analyze`, naming the exact thing wanted — the heading, the whole table, one
  column, a specific cell. A vague prompt returns a vague read.

## Two-page spreads

A scanned sheet is often **two facing book pages**, and spread OCR reads in horizontal bands, so it
interleaves the facing pages *line by line*. Each sentence is faithful on its own; consecutive ones
belong to different pages. Therefore:

- Never infer order, numbering, headings or structure from spread OCR.
- Never stitch spread OCR text into a document.
- Clip the sheet in half and read each half:

```python
page = doc[pno]
r = page.rect
page.get_pixmap(dpi=320, clip=pymupdf.Rect(r.x0, r.y0, r.x0 + r.width/2, r.y1)).save("L.png")
page.get_pixmap(dpi=320, clip=pymupdf.Rect(r.x0 + r.width/2, r.y0, r.x1, r.y1)).save("R.png")
```

## Cite the printed folio, not the page index

Quote the **folio printed on the page**, read off the rendered image — never the PDF page index and never
the sheet number. Build the sheet→folio map once per scan: the offset is constant within one file, so it
costs a single pass and holds for the whole document. Keep both numbers in your notes; the PDF index is
how you re-render that page later, the folio is what a reader can find.

## Re-read the region, not the page

When one cell matters, crop to its table and raise the dpi before trusting it:

```python
page.get_pixmap(dpi=600, clip=pymupdf.Rect(x0, y0, x1, y1)).save("cell.png")
```

Then settle the value by the arithmetic it has to satisfy — a second harder look at a degraded cell is
not independent evidence, but `3 ± 2.0 = 1..5` is. If reads still disagree at 600 dpi, write *could not
read* for that cell rather than the most plausible candidate.

## Bound the span you actually read

A chapter scan routinely opens with the previous chapter's tail or stops mid-section. State where the
material starts and ends instead of implying a complete chapter; the first and last rendered pages tell
you, and a reader who assumes completeness will attribute the gap to you.

## A two-page spread is also where the structure hides

Section numbering on a spread can be shifted against the chapter's own roadmap (a heading says §11.5
where the introduction promised §11.6). Trust the headings read off the page, not the roadmap, and say
which one you followed.
