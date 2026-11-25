#!/usr/bin/env python3
"""Sum up 25 November 2026's world news in one image.

Writes a single deterministic 1024x1024 PNG to /output/entry.png
(or ./output/entry.png when /output is not writable).
No network use. Running it twice writes identical bytes.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W = H = 1024

FONT_CANDIDATES_BOLD = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
]
FONT_CANDIDATES_REG = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
]


def font(size, bold=False):
    for path in FONT_CANDIDATES_BOLD if bold else FONT_CANDIDATES_REG:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, max_width):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if draw.textbbox((0, 0), trial, font=fnt)[2] <= max_width:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def fit_headline(draw, text, max_width, max_lines=2, start=27, floor=20):
    """Largest bold font whose wrapping of text fits max_lines lines.

    Long headlines shrink instead of spilling past their card; short
    ones keep the full start size.
    """
    size = start
    while size > floor:
        lines = wrap(draw, text, font(size, True), max_width)
        if len(lines) <= max_lines:
            return size, lines
        size -= 1
    return floor, wrap(draw, text, font(floor, True), max_width)


STORIES = [
    ("MIDDLE EAST", (176, 42, 42),
     "Tankers hit mines in the Strait of Hormuz",
     "Iran's IRGC says two oil tankers struck naval mines, exploded and "
     "caught fire on an unauthorised route - jolting the world's key oil artery."),
    ("EUROPE", (31, 78, 140),
     "Russian strikes hit Odesa and Kyiv",
     "Two people were killed in Odesa and three hurt, including a child. "
     "In Kyiv, a strike set a tower block ablaze and injured two."),
    ("GAZA", (184, 102, 26),
     "Israeli strike kills Hamas security chief",
     "Gaza medics say the strike killed Mohammad Abuelouf, who headed "
     "Hamas's interior security, along with his wife and two children."),
    ("AFRICA - SUDAN", (38, 110, 63),
     "Drone strikes kill 19 civilians in Sudan",
     "Rights group Emergency Lawyers says RSF drones killed 19 people "
     "and wounded 20 in two cities - the civil war's latest toll on civilians."),
    ("PACIFIC", (14, 116, 124),
     "Solomon Islands signs treaty with Australia",
     "The pact confirms no foreign military or security base will be set "
     "up in the Solomons - a shift in the Pacific balance, watched in Beijing."),
    ("CLIMATE", (94, 74, 150),
     "Pope Leo laments COP31 climate deadlock",
     "Pope Leo XIV voiced concern that COP31 failed to reach agreement, "
     "warning extreme events linked to the climate crisis grow more frequent."),
]

FOOTER = ("ALSO TODAY:  Huawei convicted in the U.S. of trade-secret conspiracy "
          "and bank fraud  |  Landmine casualties near 7,000 in 2025, a 5-year high")


def main():
    img = Image.new("RGB", (W, H), (247, 244, 238))
    d = ImageDraw.Draw(img)

    # Header
    d.rectangle([0, 0, W, 148], fill=(15, 35, 64))
    d.rectangle([0, 148, W, 154], fill=(201, 162, 39))
    d.text((36, 26), "THE WORLD IN ONE DAY", font=font(54, True), fill=(255, 255, 255))
    d.text((38, 96), "Wednesday, 25 November 2026  -  the day's news in a single frame",
           font=font(24), fill=(203, 216, 235))

    # Cards: 2 columns x 3 rows
    margin, gap, top = 32, 20, 172
    cw = (W - 2 * margin - gap) // 2
    ch = 240
    for i, (label, accent, head, body) in enumerate(STORIES):
        x = margin + (i % 2) * (cw + gap)
        y = top + (i // 2) * (ch + gap)
        d.rounded_rectangle([x, y, x + cw, y + ch], radius=14,
                            fill=(255, 255, 255), outline=(216, 210, 198), width=2)
        d.rounded_rectangle([x, y, x + cw, y + 44], radius=14, fill=accent)
        d.rectangle([x, y + 22, x + cw, y + 44], fill=accent)
        d.text((x + 18, y + 10), label, font=font(22, True), fill=(255, 255, 255))
        # Accent stripe down the card's left edge, in the story's colour
        d.rounded_rectangle([x + 10, y + 58, x + 16, y + ch - 14], radius=3, fill=accent)
        ty = y + 58
        hsize, hlines = fit_headline(d, head, cw - 36)
        for line in hlines:
            d.text((x + 26, ty), line, font=font(hsize, True), fill=(24, 28, 36))
            ty += hsize + 6
        ty += 6
        for line in wrap(d, body, font(21), cw - 44):
            d.text((x + 26, ty), line, font=font(21), fill=(74, 80, 92))
            ty += 27

    # Footer
    fy = top + 3 * ch + 2 * gap + 14
    d.rounded_rectangle([margin, fy, W - margin, fy + 62], radius=12, fill=(15, 35, 64))
    lines = wrap(d, FOOTER, font(19, True), W - 2 * margin - 36)
    ty = fy + 10
    for line in lines[:2]:
        d.text((margin + 18, ty), line, font=font(19, True), fill=(235, 229, 205))
        ty += 24

    out_dir = "/output" if os.path.isdir("/output") and os.access("/output", os.W_OK) \
        else os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, "entry.png")
    img.save(out, format="PNG", optimize=True)
    print(out)


if __name__ == "__main__":
    main()
