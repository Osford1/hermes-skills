"""Generic markdown -> DOCX + designed HTML exporter (the HTML feeds the pdf skill's
html_to_pdf.js for a PDF; all three formats stay in sync from ONE source markdown).

Usage (run with miniconda python -- it has python-docx):
    C:/Users/<you>/miniconda3/python.exe md_export.py <src.md> <out.docx> <out.html> "<Doc title>"

Handles: h1-h4, paragraphs, bullet + numbered lists, pipe tables, fenced code,
blockquotes, hr, and inline **bold** / `code` / *italic*. The CSS is Paged.js-safe
(no CSS counters; page numbers come from the @page bottom-centre margin box).
"""
import html
import os
import re
import sys

from docx import Document
from docx.shared import Pt, RGBColor

TOKEN = re.compile(r"(\*\*.+?\*\*|`[^`]+`)")


def inline_html(text):
    out = []
    for part in TOKEN.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            out.append("<strong>" + html.escape(part[2:-2]) + "</strong>")
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            out.append("<code>" + html.escape(part[1:-1]) + "</code>")
        else:
            s = html.escape(part)
            out.append(re.sub(r"\*([^*]+)\*", r"<em>\1</em>", s))
    return "".join(out)


def inline_runs(par, text):
    for part in TOKEN.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            par.add_run(part[2:-2]).bold = True
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            r = par.add_run(part[1:-1])
            r.font.name = "Consolas"
            r.font.size = Pt(8.5)
            r.font.color.rgb = RGBColor(0x9B, 0x1C, 0x31)
        else:
            s = part
            if s.startswith("*") and s.endswith("*") and len(s) > 2:
                par.add_run(s[1:-1]).italic = True
            else:
                par.add_run(s)


def parse_blocks(md_text):
    """Yield ('h',level,text) ('p',text) ('ul',[items]) ('ol',[items]) ('table',rows)
    ('code',[lines]) ('quote',text) ('hr',None)."""
    lines = md_text.split("\n")
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):
            i += 1
            buf = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            yield ("code", buf)
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            yield ("h", len(m.group(1)), m.group(2))
            i += 1
            continue
        if re.fullmatch(r"-{3,}", s):
            yield ("hr", None)
            i += 1
            continue
        if s.startswith("|") and s.endswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set(":- ") for c in cells):
                    rows.append(cells)
                i += 1
            yield ("table", rows)
            continue
        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip())
                i += 1
            yield ("quote", " ".join(x for x in buf if x))
            continue
        m = re.match(r"^[-*]\s+(.*)$", s)
        if m:
            items = []
            while i < len(lines) and re.match(r"^[-*]\s+", lines[i].strip()):
                items.append(re.match(r"^[-*]\s+(.*)$", lines[i].strip()).group(1))
                i += 1
            yield ("ul", items)
            continue
        m = re.match(r"^\d+\.\s+(.*)$", s)
        if m:
            items = []
            while i < len(lines) and re.match(r"^\d+\.\s+", lines[i].strip()):
                items.append(re.match(r"^\d+\.\s+(.*)$", lines[i].strip()).group(1))
                i += 1
            yield ("ol", items)
            continue
        yield ("p", s)
        i += 1


def to_docx(md_text, out_path):
    doc = Document()
    doc.styles["Normal"].font.name = "Calibri"
    doc.styles["Normal"].font.size = Pt(10)
    for blk in parse_blocks(md_text):
        kind = blk[0]
        if kind == "h":
            inline_runs(doc.add_heading(level=min(blk[1], 4)), blk[2])
        elif kind == "p":
            inline_runs(doc.add_paragraph(), blk[1])
        elif kind == "ul":
            for it in blk[1]:
                inline_runs(doc.add_paragraph(style="List Bullet"), it)
        elif kind == "ol":
            for it in blk[1]:
                inline_runs(doc.add_paragraph(style="List Number"), it)
        elif kind == "code":
            r = doc.add_paragraph().add_run("\n".join(blk[1]))
            r.font.name = "Consolas"
            r.font.size = Pt(8.5)
        elif kind == "quote":
            p = doc.add_paragraph()
            inline_runs(p, blk[1])
            for r in p.runs:
                r.italic = True
        elif kind == "hr":
            doc.add_paragraph("_" * 58)
        elif kind == "table":
            rows = blk[1]
            if not rows:
                continue
            ncols = max(len(r) for r in rows)
            t = doc.add_table(rows=0, cols=ncols)
            t.style = "Light Grid Accent 1"
            for ri, row in enumerate(rows):
                row = row + [""] * (ncols - len(row))
                cells = t.add_row().cells
                for ci, val in enumerate(row):
                    p = cells[ci].paragraphs[0]
                    inline_runs(p, val)
                    for r in p.runs:
                        r.font.size = Pt(8.5)
                        if ri == 0:
                            r.bold = True
            doc.add_paragraph()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    doc.save(out_path)
    return out_path


CSS = """
@page { size: A4; margin: 18mm 16mm 20mm 16mm;
  @bottom-center { content: counter(page); font-family: Georgia, serif; font-size: 9pt; color: #666; } }
@page :first { @bottom-center { content: ""; } }
body { font-family: "Segoe UI", Calibri, sans-serif; font-size: 9.6pt; line-height: 1.48; color: #1b1b1b; margin: 0; }
h1 { font-size: 19pt; line-height: 1.22; color: #0f2b46; margin: 0 0 6px 0; border-bottom: 3px solid #0f2b46; padding-bottom: 8px; }
h2 { font-size: 13pt; color: #0f2b46; margin: 18px 0 6px 0; padding-bottom: 3px; border-bottom: 1px solid #c9d4e0; break-after: avoid; }
h3 { font-size: 11pt; color: #17456e; margin: 13px 0 4px 0; break-after: avoid; }
h4 { font-size: 10pt; color: #17456e; margin: 10px 0 3px 0; break-after: avoid; }
p { margin: 5px 0; }
table.data { border-collapse: collapse; width: 100%; margin: 8px 0 10px 0; font-size: 8.4pt; }
table.data th { background: #eef3f8; border-top: 1.4pt solid #0f2b46; border-bottom: 0.8pt solid #0f2b46;
                text-align: left; padding: 4px 5px; color: #0f2b46; }
table.data td { border-bottom: 0.5pt solid #dbe3ec; padding: 4px 5px; vertical-align: top; }
table.data tr { break-inside: avoid; }
code { font-family: Consolas, monospace; font-size: 8.4pt; background: #f3f5f8; padding: 0 2px; color: #9b1c31; }
pre { background: #f6f8fa; border-left: 3px solid #b9c6d6; padding: 7px 9px; font-size: 8.2pt;
      font-family: Consolas, monospace; white-space: pre-wrap; break-inside: avoid; margin: 7px 0; }
blockquote { border-left: 3px solid #0f2b46; background: #f7f9fb; margin: 8px 0; padding: 7px 11px;
             font-style: italic; color: #33404f; break-inside: avoid; }
ul, ol { margin: 5px 0; padding-left: 20px; }
li { margin: 2px 0; }
hr { border: none; border-top: 1px solid #d5dde6; margin: 14px 0; }
strong { color: #0f2b46; }
"""


def to_html(md_text, out_path, title):
    body = []
    for blk in parse_blocks(md_text):
        kind = blk[0]
        if kind == "h":
            tag = "h%d" % min(blk[1], 4)
            body.append("<%s>%s</%s>" % (tag, inline_html(blk[2]), tag))
        elif kind == "p":
            body.append("<p>" + inline_html(blk[1]) + "</p>")
        elif kind == "ul":
            body.append("<ul>" + "".join("<li>" + inline_html(x) + "</li>" for x in blk[1]) + "</ul>")
        elif kind == "ol":
            body.append("<ol>" + "".join("<li>" + inline_html(x) + "</li>" for x in blk[1]) + "</ol>")
        elif kind == "code":
            body.append("<pre>" + "\n".join(html.escape(l) for l in blk[1]) + "</pre>")
        elif kind == "quote":
            body.append("<blockquote>" + inline_html(blk[1]) + "</blockquote>")
        elif kind == "hr":
            body.append("<hr>")
        elif kind == "table":
            rows = blk[1]
            if not rows:
                continue
            ncols = max(len(r) for r in rows)
            out = []
            for ri, row in enumerate(rows):
                row = row + [""] * (ncols - len(row))
                t = "th" if ri == 0 else "td"
                out.append("<tr>" + "".join("<%s>%s</%s>" % (t, inline_html(c), t) for c in row) + "</tr>")
            body.append('<table class="data">' + "".join(out) + "</table>")
    doc = ("<!DOCTYPE html><html lang='en'><head><meta charset='utf-8'><title>" + html.escape(title) +
           "</title><style>" + CSS + "</style></head><body>" + "\n".join(body) + "</body></html>")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    open(out_path, "w", encoding="utf-8").write(doc)
    return out_path


if __name__ == "__main__":
    src, out_docx, out_html, title = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    md = open(src, encoding="utf-8").read()
    print("docx:", to_docx(md, out_docx))
    print("html:", to_html(md, out_html, title))
