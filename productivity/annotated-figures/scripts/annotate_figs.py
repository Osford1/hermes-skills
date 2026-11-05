# annotate_figs.py - draw callouts onto photos so they can be embedded as
# labelled figures, one output file per language.
#
# Edit CONFIG, then:  python annotate_figs.py
#
# The canvas is sized to the SLOT the figure occupies in the deck/page:
#   canvas px = 1560 x 1224  ==  3.95in x 3.10in  (font px = pt/72 * CW/slot_w_in)
# Callouts are drawn in canvas pixels, after the photo is resized, so the text
# stays crisp even when the photo itself is soft.
# Needs Pillow >= 8.2 (rounded_rectangle, textbbox) and a CJK-capable TTF if
# any label is Chinese.

import os

from PIL import Image, ImageDraw, ImageFont, ImageFilter

CW, CH = 1560, 1224                      # canvas = the slide slot's aspect
OUT = "figures"                          # output dir (created if missing)
FONTS = {"en": "C:/Windows/Fonts/msyhbd.ttc",
         "zh": "C:/Windows/Fonts/msyhbd.ttc"}   # swap for the deck's font
PURPLE, INK, PANEL = (0x6C, 0x22, 0x80), (0x2B, 0x2B, 0x33), (0xF5, 0xF2, 0xF9)
LSIZE, BSIZE, DSIZE = 46, 40, 50         # label, band, badge px
BAND_H, BAND_A, MARGIN, LEAD = 74, 165, 16, 78

# name -> source photo, crop, and per-language strings.
# crop = (max fraction of the axis that may be cropped, bias) with
#   bias -1 = keep the left/top edge, +1 = keep the right/bottom edge.
# label = (text, x% of source width, y% of source height, "left"|"right")
# The x/y percentages come from a vision_analyze pass on the source photo.
CONFIG = {
    "sample": dict(
        src="sample-source.png",
        crop=(0.24, 0.0),
        band={"en": "1 \u00b7 One line describing this photo",
              "zh": "1 \u00b7 \u4e00\u53e5\u8bdd\u63cf\u8ff0\u8fd9\u5f20\u7167\u7247"},
        labels={"en": [("Short label here", 55, 52, "left"),
                       ("Second label", 48, 62, "right")],
                "zh": [("\u8fd9\u91cc\u5199\u77ed\u6807\u7b7e", 55, 52, "left"),
                       ("\u7b2c\u4e8c\u4e2a\u6807\u7b7e", 48, 62, "right")]},
    ),
}


def fit(im, crop):
    """Crop toward the canvas aspect within crop[0], biased by crop[1].

    Returns (resized photo, crop box in source px, scale).
    """
    max_frac, bias = crop
    w, h = im.size
    target = CW / float(CH)
    box = (0, 0, w, h)
    if w / float(h) > target:                 # too wide: crop the sides
        nw = int(round(h * target))
        cut = w - nw
        if cut <= max_frac * w:
            ox = int(round(cut * (0.5 + 0.5 * bias)))
            box = (ox, 0, ox + nw, h)
    else:                                     # too tall: crop top/bottom
        nh = int(round(w / target))
        cut = h - nh
        if cut <= max_frac * h:
            oy = int(round(cut * (0.5 + 0.5 * bias)))
            box = (0, oy, w, oy + nh)
    im = im.crop(box)
    scale = min(CW / float(im.width), CH / float(im.height))
    size = (int(round(im.width * scale)), int(round(im.height * scale)))
    return im.resize(size, Image.LANCZOS), box, scale


def compose(name, cfg, lang):
    src = Image.open(cfg["src"]).convert("RGB")
    print("%-26s %s src %dx%d" % (name, lang, src.width, src.height))
    src = src.filter(ImageFilter.UnsharpMask(radius=2, percent=60, threshold=3))
    photo, box, scale = fit(src, cfg["crop"])
    ox, oy = (CW - photo.width) // 2, (CH - photo.height) // 2
    canvas = Image.new("RGB", (CW, CH), PANEL)
    canvas.paste(photo, (ox, oy))
    draw = ImageDraw.Draw(canvas, "RGBA")

    font_l = ImageFont.truetype(FONTS[lang], LSIZE)
    font_b = ImageFont.truetype(FONTS[lang], BSIZE)
    font_d = ImageFont.truetype(FONTS[lang], DSIZE)

    def xy(fx, fy):
        """Source percentage -> canvas px, carried through the crop box."""
        return (ox + ((fx / 100.0) * src.width - box[0]) * scale,
                oy + ((fy / 100.0) * src.height - box[1]) * scale)

    for text, lx, ly, side in cfg["labels"][lang]:
        tw = draw.textbbox((0, 0), text, font=font_l)[2]
        bw, bh = tw + 36, LSIZE + 28
        cx, cy = xy(lx, ly)
        bx = cx - LEAD - bw if side == "left" else cx + LEAD
        by = cy - bh / 2.0
        bx = max(MARGIN, min(bx, CW - MARGIN - bw))
        by = max(MARGIN, min(by, CH - BAND_H - MARGIN - bh))
        if side == "left":
            draw.line([(bx + bw, cy), (cx, cy)], fill=PURPLE + (235,), width=7)
        else:
            draw.line([(bx, cy), (cx, cy)], fill=PURPLE + (235,), width=7)
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=12,
                               fill=(255, 255, 255, 235),
                               outline=PURPLE + (255,), width=4)
        draw.text((bx + 18, by + 13), text, font=font_l, fill=INK)
        draw.ellipse([cx - 24, cy - 24, cx + 24, cy + 24], fill=PURPLE + (255,))
        draw.ellipse([cx - 17, cy - 17, cx + 17, cy + 17],
                     outline=(255, 255, 255, 255), width=5)

    draw.rectangle([0, CH - BAND_H, CW, CH], fill=(18, 12, 24, BAND_A))
    draw.text((28, (CH - BAND_H) + (BAND_H - BSIZE) / 2.0 - 6), cfg["band"][lang],
              font=font_b, fill=(255, 255, 255))
    r = 40
    draw.ellipse([34, 34, 34 + 2 * r, 34 + 2 * r], fill=PURPLE + (255,))
    num = str(list(CONFIG).index(name) + 1)
    draw.text((34 + r, 34 + r - 4), num, font=font_d, fill=(255, 255, 255),
              anchor="mm")

    if not os.path.isdir(OUT):
        os.makedirs(OUT)
    path = os.path.join(OUT, "fig-%s-%s.jpg" % (name, lang))
    canvas.save(path, quality=92, optimize=True)
    print("  -> %s %d bytes" % (path, os.path.getsize(path)))


if __name__ == "__main__":
    for key, conf in CONFIG.items():
        for language in conf["band"]:
            compose(key, conf, language)
