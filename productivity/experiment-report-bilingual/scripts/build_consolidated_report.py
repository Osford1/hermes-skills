"""Build the SRT experiment-series report: self-contained HTML (EN + CN) and .docx (EN + CN).

Usage:  C:/Users/<you>/miniconda3/python.exe build_report.py
Input:  content_en.md / content_zh.md  (tiny markup, see parse())
Output: ../SRT_experiments_report.html, ../SRT_experiments_report_中文.html,
        ../SRT_experiments_report.docx, ../SRT_experiments_report_中文.docx
"""
import base64, os, pathlib, re, shutil, sys

BASE = pathlib.Path(r"<project-dir>")
NEW = BASE / "SRT_experiments_report"
WORK = NEW / "_report_work"
SRC = BASE / "9_9_2026"
MEDIA = WORK / "media"
CLEAN = WORK / "clean"
for d in (MEDIA, CLEAN):
    d.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------- media staging
COPIES = {
    "fig_start.jpg":   SRC / "yellow block initial position.jpg",
    "fig_goal.jpg":    SRC / "yellow block final position.jpg",
    "poster_demo.jpg": SRC / "_report_work/posters/clean_poster_demo.jpg",
    "poster_2k.jpg":   SRC / "_report_work/posters/clean_poster_2k.jpg",
    "poster_30k.jpg":  SRC / "_report_work/posters/clean_poster_30k.jpg",
    "clip_demo.mp4":   SRC / "_report_work/one training episode.h264.mp4",
    "clip_2k.mp4":     SRC / "_report_work/2000 steps training.h264.mp4",
    "clip_30k.mp4":    SRC / "_report_work/30000 steps training.h264.mp4",
}
for name, src in COPIES.items():
    if not src.exists():
        sys.exit(f"MISSING SOURCE MEDIA: {src}")
    shutil.copy2(src, MEDIA / name)

# python-docx cannot read some valid JPEGs (non-JFIF header) -> re-save via PIL
from PIL import Image
for p in MEDIA.glob("*.jpg"):
    Image.open(p).convert("RGB").save(CLEAN / p.name, "JPEG", quality=90, subsampling=0)

FIG_POSTER = {"demo": "poster_demo.jpg", "2k": "poster_2k.jpg", "30k": "poster_30k.jpg"}
FIG_FILE   = {"start": "fig_start.jpg", "goal": "fig_goal.jpg"}
VID_FILE   = {"demo": "clip_demo.mp4", "2k": "clip_2k.mp4", "30k": "clip_30k.mp4"}
FIG_ORDER  = {"start": 1, "goal": 2}
VID_ORDER  = {"demo": 1, "2k": 2, "30k": 3}
VID_LABEL  = {"demo": "one training episode.mp4",
              "2k": "2000 steps training.mp4",
              "30k": "30000 steps training.mp4"}

# ---------------------------------------------------------------- parsing
BLOCK_RE = re.compile(r"^(#|##|###|~|\||>|-|\[FIG:|\[VID:|\d+\.\s)")

def parse(path):
    """Return a flat list of blocks. Block = dict(type=..., payload...)."""
    lines = pathlib.Path(path).read_text(encoding="utf-8").splitlines()
    blocks, i = [], 0
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1
            continue
        if s.startswith("```"):
            buf, i = [], i + 1
            while i < len(lines) and not lines[i].strip().startswith("```"):
                buf.append(lines[i]); i += 1
            i += 1
            blocks.append({"type": "code", "text": "\n".join(buf)})
            continue
        m = re.match(r"^\[(FIG|VID):([a-z0-9]+)\|(.+)\]$", s)
        if m:
            blocks.append({"type": "fig" if m.group(1) == "FIG" else "vid",
                           "key": m.group(2), "caption": m.group(3)})
        elif s.startswith("### "):
            blocks.append({"type": "h3", "text": s[4:]})
        elif s.startswith("## "):
            blocks.append({"type": "h2", "text": s[3:]})
        elif s.startswith("# "):
            blocks.append({"type": "h1", "text": s[2:]})
        elif s.startswith("~ "):
            blocks.append({"type": "meta", "text": s[2:]})
        elif s.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-{2,}:?", c) or c == "" for c in cells):
                    rows.append(cells)
                i += 1
            # pipe inside cells was escaped as \| ; split() above already handled plain pipes
            blocks.append({"type": "table", "rows": rows})
            continue
        elif s.startswith("> "):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip().lstrip(">").strip()); i += 1
            blocks.append({"type": "note", "text": " ".join(buf)})
            continue
        elif s.startswith("- "):
            buf = []
            while i < len(lines) and lines[i].strip().startswith("- "):
                buf.append(lines[i].strip()[2:]); i += 1
            blocks.append({"type": "ul", "items": buf})
            continue
        else:
            blocks.append({"type": "p", "text": s})
        i += 1
    return blocks

# ---------------------------------------------------------------- inline markup
def inline_html(t):
    t = (t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"`(.+?)`", r"<code>\1</code>", t)
    return t

def split_bold(t):
    """-> [(text, bold)] for python-docx runs"""
    out = []
    for part in re.split(r"(\*\*.+?\*\*)", t):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            out.append((part[2:-2], True))
        else:
            out.append((part, False))
    return out

def data_uri(p, mime):
    return f"data:{mime};base64," + base64.b64encode(pathlib.Path(p).read_bytes()).decode()

# ---------------------------------------------------------------- HTML
CSS = """
*{box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue","Microsoft YaHei",sans-serif;
 color:#1C2330;line-height:1.62;max-width:920px;margin:0 auto;padding:36px 32px 80px;background:#fff}
h1{font-size:27px;line-height:1.3;margin:0 0 8px;letter-spacing:-.2px}
.meta{color:#5B6472;font-size:12.5px;margin:2px 0;line-height:1.55}
h2{font-size:19px;margin:40px 0 10px;padding-bottom:7px;border-bottom:1px solid #E3E7EE;color:#0F172A}
h3{font-size:15.5px;margin:26px 0 8px;color:#25314A}
p{margin:10px 0}
ul{margin:10px 0 10px 4px;padding-left:20px}
li{margin:4px 0}
table{border-collapse:collapse;width:100%;margin:16px 0;font-size:13px}
th,td{border:1px solid #DCE1E8;padding:7px 9px;text-align:left;vertical-align:top}
th{background:#F4F6FA;font-weight:600;color:#25314A}
tbody tr:nth-child(even) td{background:#FBFCFE}
.note{background:#FFF8E6;border-left:4px solid #F0B429;padding:12px 15px;margin:18px 0;border-radius:4px;font-size:13.5px}
figure{margin:24px 0;text-align:center}
figure img{width:430px;max-width:100%;border:1px solid #E3E7EE;border-radius:6px}
figure video{width:330px;max-width:100%;border-radius:6px;background:#000;display:block;margin:0 auto}
figcaption{color:#5B6472;font-size:12.5px;line-height:1.55;margin:10px auto 0;text-align:left;max-width:660px}
figcaption strong{color:#25314A}
code{background:#F4F6FA;padding:1px 5px;border-radius:3px;font-size:12.5px;
 font-family:ui-monospace,SFMono-Regular,Consolas,monospace;color:#0B3A82}
pre{background:#0F172A;color:#E6EDF7;padding:13px 15px;border-radius:6px;overflow-x:auto;
 font-size:12px;line-height:1.55;font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
pre code{background:none;color:inherit;padding:0}
hr{border:none;border-top:1px solid #E3E7EE;margin:20px 0}
.footer{color:#8A93A2;font-size:11.5px;margin-top:34px}
@media print{body{padding:0;max-width:none}figure video{width:280px}}
"""

def build_html(blocks, out_path, lang, title_fallback):
    parts, h1_done = [], False
    for b in blocks:
        t = b["type"]
        if t == "h1":
            parts.append(f"<h1>{inline_html(b['text'])}</h1>"); h1_done = True
        elif t == "meta":
            parts.append(f'<div class="meta">{inline_html(b["text"])}</div>')
        elif t == "h2":
            parts.append(f"<h2>{inline_html(b['text'])}</h2>")
        elif t == "h3":
            parts.append(f"<h3>{inline_html(b['text'])}</h3>")
        elif t == "p":
            parts.append(f"<p>{inline_html(b['text'])}</p>")
        elif t == "note":
            parts.append(f'<div class="note">{inline_html(b["text"])}</div>')
        elif t == "ul":
            parts.append("<ul>" + "".join(f"<li>{inline_html(x)}</li>" for x in b["items"]) + "</ul>")
        elif t == "code":
            esc = b["text"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            parts.append(f"<pre><code>{esc}</code></pre>")
        elif t == "table":
            rows = b["rows"]
            head = "".join(f"<th>{inline_html(c)}</th>" for c in rows[0])
            body = "".join("<tr>" + "".join(f"<td>{inline_html(c)}</td>" for c in r) + "</tr>"
                           for r in rows[1:])
            parts.append(f"<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>")
        elif t == "fig":
            p = MEDIA / FIG_FILE[b["key"]]
            parts.append('<figure><img src="' + data_uri(p, "image/jpeg") + '" alt="figure">'
                         f'<figcaption>{inline_html(b["caption"])}</figcaption></figure>')
        elif t == "vid":
            key = b["key"]
            p = MEDIA / VID_FILE[key]
            label = VID_LABEL[key]
            cap = b["caption"] + (f'<br>File: <code>{label}</code>' if lang == "en"
                                  else f'<br>文件：<code>{label}</code>')
            parts.append('<figure><video controls preload="metadata" playsinline '
                         'src="' + data_uri(p, "video/mp4") + '"></video>'
                         f'<figcaption>{inline_html(cap)}</figcaption></figure>')
    html = (f'<!DOCTYPE html>\n<html lang="{lang}">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
            f"<title>{title_fallback}</title>\n<style>{CSS}</style>\n</head>\n<body>\n"
            + "\n".join(parts) + "\n</body>\n</html>\n")
    pathlib.Path(out_path).write_text(html, encoding="utf-8")
    return html

# ---------------------------------------------------------------- DOCX
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

INK, MUTED, ACCENT = RGBColor(0x1C, 0x23, 0x30), RGBColor(0x5B, 0x64, 0x72), RGBColor(0x25, 0x63, 0xEB)

def shade(par, hexcolor):
    pPr = par._p.get_or_add_pPr(); shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), hexcolor)
    pPr.append(shd)

def rule(par, color="D7DBDF", size=8):
    pPr = par._p.get_or_add_pPr(); pbdr = OxmlElement("w:pBdr"); b = OxmlElement("w:bottom")
    b.set(qn("w:val"), "single"); b.set(qn("w:sz"), str(size))
    b.set(qn("w:space"), "3"); b.set(qn("w:color"), color)
    pbdr.append(b); pPr.append(pbdr)

def build_docx(blocks, out_path):
    doc = Document()
    sec = doc.sections[0]
    sec.left_margin = sec.right_margin = Cm(2.2)
    sec.top_margin = sec.bottom_margin = Cm(2.0)
    st = doc.styles["Normal"]; st.font.name = "Calibri"; st.font.size = Pt(10.5)
    st.font.color.rgb = INK; st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.25
    for i, b in enumerate(blocks):
        t = b["type"]
        if t == "h1":
            p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(4)
            r = p.add_run(b["text"]); r.bold = True; r.font.size = Pt(20); r.font.color.rgb = INK
        elif t == "meta":
            p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(2)
            r = p.add_run(b["text"]); r.font.size = Pt(8.5); r.font.color.rgb = MUTED
        elif t in ("h2", "h3"):
            h = doc.add_heading(b["text"], level=1 if t == "h2" else 2)
            for r in h.runs:
                r.font.name = "Calibri"; r.font.color.rgb = INK if t == "h2" else RGBColor(0x25, 0x31, 0x4A)
                r.font.size = Pt(14.5 if t == "h2" else 12)
            if t == "h2":
                rule(h)
        elif t == "p":
            p = doc.add_paragraph()
            for txt, bold in split_bold(b["text"]):
                r = p.add_run(txt); r.bold = bold
        elif t == "note":
            p = doc.add_paragraph()
            for txt, bold in split_bold(b["text"]):
                r = p.add_run(txt); r.bold = bold; r.font.size = Pt(10)
            shade(p, "FFF8E6"); p.paragraph_format.space_after = Pt(10)
        elif t == "ul":
            for item in b["items"]:
                p = doc.add_paragraph(style="List Bullet")
                for txt, bold in split_bold(item):
                    r = p.add_run(txt); r.bold = bold; r.font.size = Pt(10.5)
        elif t == "code":
            for line in b["text"].split("\n"):
                p = doc.add_paragraph(); p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.0
                r = p.add_run(line if line else " "); r.font.name = "Consolas"; r.font.size = Pt(8.5)
            shade(p, "F2F4F8")
        elif t == "table":
            rows = b["rows"]
            tbl = doc.add_table(rows=1 + len(rows) - 1, cols=len(rows[0]))
            tbl.style = "Light Grid Accent 1"; tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            for c, cell_text in enumerate(rows[0]):
                cell = tbl.rows[0].cells[c]; cell.text = ""
                for txt, bold in split_bold(cell_text):
                    r = cell.paragraphs[0].add_run(txt); r.bold = True; r.font.size = Pt(8.5)
            for ri, rdata in enumerate(rows[1:], start=1):
                for c, val in enumerate(rdata):
                    cell = tbl.rows[ri].cells[c]; cell.text = ""
                    for txt, bold in split_bold(val):
                        r = cell.paragraphs[0].add_run(txt); r.bold = bold; r.font.size = Pt(8.5)
            doc.add_paragraph().paragraph_format.space_after = Pt(4)
        elif t == "fig":
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str(CLEAN / FIG_FILE[b["key"]]), width=Cm(10.5))
            c = doc.add_paragraph()
            for txt, bold in split_bold(b["caption"].replace("**", "")):
                r = c.add_run(txt); r.italic = True; r.font.size = Pt(8.5); r.font.color.rgb = MUTED
            c.paragraph_format.space_after = Pt(12)
        elif t == "vid":
            key = b["key"]
            p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.add_run().add_picture(str(CLEAN / FIG_POSTER[key]), width=Cm(7.5))
            c = doc.add_paragraph()
            r = c.add_run(b["caption"].replace("**", "")); r.italic = True
            r.font.size = Pt(8.5); r.font.color.rgb = MUTED
            f = c.add_run(f"\nVideo file (travels with this document): {VID_LABEL[key]}")
            f.italic = True; f.font.size = Pt(8); f.font.color.rgb = MUTED
            c.paragraph_format.space_after = Pt(12)
    doc.save(str(out_path))
    return out_path

# ---------------------------------------------------------------- run
en_blocks = parse(WORK / "content_en.md")
zh_blocks = parse(WORK / "content_zh.md")

html_en = build_html(en_blocks, NEW / "SRT_experiments_report.html", "en",
                     "SRT Embodied-AI — SO-101 Experiment Series Report")
html_zh = build_html(zh_blocks, NEW / "SRT_experiments_report_中文.html", "zh-CN",
                     "SRT 具身智能 — SO-101 抓取放置实验系列报告")
build_docx(en_blocks, NEW / "SRT_experiments_report.docx")
build_docx(zh_blocks, NEW / "SRT_experiments_report_中文.docx")

for f in sorted(NEW.iterdir()):
    if f.is_file():
        print(f"{f.stat().st_size/1024:9.1f} KB  {f.name}")
for name, txt in (("EN", html_en), ("CN", html_zh)):
    left = re.findall(r"\{[A-Z_0-9]+\}", txt)
    print(f"{name}: <video>={txt.count('<video')} <img>={txt.count('<img')} "
          f"placeholders={len(left)} len={len(txt)}")
