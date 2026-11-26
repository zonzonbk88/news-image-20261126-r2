#!/usr/bin/env python3
"""Render a newspaper front page summing up Thursday 26 November 2026.

Draws the whole page with Pillow: masthead, one lead story, six more
stories in a two-column grid, and a footer line. The output is a fixed
1024x1024 PNG; no clock, no randomness, no network, so repeated runs
produce identical bytes.
"""

import textwrap

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (250, 246, 236)
INK = (18, 18, 18)
RULE = (90, 84, 72)
ACCENT = (146, 28, 28)
MUTED = (96, 90, 80)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning lines that fit inside max_w pixels."""
    lines = []
    for chunk in text.split("\n"):
        words = chunk.split()
        cur = ""
        for w in words:
            trial = (cur + " " + w).strip()
            if draw.textlength(trial, font=fnt) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, max_w, leading, color=INK):
    """Draw wrapped text, return the y just below the last line."""
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=color)
        y += leading
    return y


def hline(draw, x0, x1, y, width=2, color=RULE):
    draw.line([(x0, y), (x1, y)], fill=color, width=width)


def kicker(draw, x, y, label):
    fnt = font(SANS_B, 17)
    draw.text((x, y), label.upper(), font=fnt, fill=ACCENT)
    return y + 24


def story(draw, x, y, w, tag, headline, body, head_size=23, body_size=17):
    """One boxed story: red kicker, bold headline, short body text."""
    y = kicker(draw, x, y, tag)
    y = para(draw, x, y, headline, font(SERIF_B, head_size), w, head_size + 5)
    y += 4
    y = para(draw, x, y, body, font(SANS, body_size), w, body_size + 6, color=(40, 38, 34))
    return y


def draw_tariff_bars(draw, x, y, w, h):
    """Small bar chart: tariff rate steps up to 25% across partners."""
    vals = [10, 12, 15, 15, 18, 20, 25]
    labels = ["A", "B", "C", "D", "E", "F", "G"]
    draw.rectangle([x, y, x + w, y + h], outline=RULE, width=2)
    base = y + h - 26
    bw = (w - 24) // len(vals)
    for i, v in enumerate(vals):
        bx = x + 12 + i * bw
        bh = int((h - 44) * v / 25)
        draw.rectangle([bx, base - bh, bx + bw - 8, base], fill=ACCENT)
        draw.text((bx + 2, base + 4), labels[i], font=font(SANS, 13), fill=MUTED)
    draw.text((x + 8, y + 6), "Tariff rate, %", font=font(SANS_B, 14), fill=INK)


def draw_rocket(draw, x, y, s):
    """Simple rocket pictogram for the astronaut story."""
    # body: nose triangle over a rectangle, two fins, flame
    draw.polygon([(x + s // 2, y), (x + s * 3 // 4, y + s // 3),
                  (x + s // 4, y + s // 3)], fill=ACCENT)
    draw.rectangle([x + s // 4, y + s // 3, x + s * 3 // 4, y + s * 2 // 3],
                   fill=(52, 84, 138))
    draw.polygon([(x + s // 4, y + s * 2 // 3), (x, y + s),
                  (x + s // 4, y + s * 5 // 6)], fill=ACCENT)
    draw.polygon([(x + s * 3 // 4, y + s * 2 // 3), (x + s, y + s),
                  (x + s * 3 // 4, y + s * 5 // 6)], fill=ACCENT)
    draw.ellipse([x + s // 4, y + s // 4, x + s * 3 // 4, y + s // 2], fill=PAPER)


def draw_shield(draw, x, y, s):
    """Shield pictogram for the security-pact story."""
    draw.polygon([(x + s // 2, y), (x + s, y + s // 4), (x + s, y + s * 2 // 3),
                  (x + s // 2, y + s), (x, y + s * 2 // 3), (x, y + s // 4)],
                 fill=(52, 84, 138))
    draw.line([(x + s // 4, y + s // 2), (x + s // 2, y + s * 3 // 4),
               (x + s * 3 // 4, y + s // 3)], fill=PAPER, width=4)


def draw_flag(draw, x, y, w, h):
    """A plain flag on a pole, for the expulsion story."""
    draw.line([(x, y), (x, y + h)], fill=INK, width=3)
    draw.polygon([(x, y), (x + w, y + h // 4), (x, y + h // 2)], fill=ACCENT)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, W - 11, H - 11], outline=INK, width=3)

    # ---- Masthead -------------------------------------------------------
    d.text((W // 2, 28), "THE WORLD TODAY", font=font(SERIF_B, 58),
           fill=INK, anchor="mt")
    d.text((W // 2, 100), "THURSDAY 26 NOVEMBER 2026  ·  ONE DAY, SEVEN STORIES",
           font=font(SANS_B, 18), fill=ACCENT, anchor="mt")
    hline(d, 34, W - 34, 136, width=4)
    hline(d, 34, W - 34, 142, width=1)

    # ---- Lead story: US tariffs ----------------------------------------
    lx, ly, lw = 34, 158, 956
    ly = kicker(d, lx, ly, "Washington  ·  Lead story")
    ly = para(d, lx, ly, "U.S. plans tariffs of up to 25% on 14 trading partners",
              font(SERIF_B, 36), lw, 44)
    ly += 4
    body = ("The White House says the new duties, the steepest in a generation, "
            "will apply to goods from fourteen countries and take effect within "
            "weeks, raising the prospect of retaliation from partners.")
    ly = para(d, lx, ly, body, font(SANS, 20), lw - 250, 28)
    draw_tariff_bars(d, lx + lw - 230, ly - 100, 230, 100)
    hline(d, 34, W - 34, ly + 12, width=3)

    # ---- Six stories in a two-column grid -------------------------------
    top = ly + 30
    col_w = 462
    gap = 32
    x0, x1 = 34, 34 + col_w + gap
    row_h = 184
    vline_x = W // 2
    d.line([(vline_x, top), (vline_x, top + 3 * row_h)], fill=RULE, width=1)

    stories = [
        ("Asia · Space", "Pakistan's first astronaut to fly on China's Shenzhou-24",
         "Islamabad names its first citizen to fly to space, aboard a Chinese "
         "crewed mission.",
         "rocket"),
        ("Latin America", "20 hostages freed after 17-hour supermarket siege in Colombia",
         "Police end a day-long standoff, freeing twenty people held inside; "
         "the gunman is arrested.",
         None),
        ("Pacific", "Australia and Solomon Islands sign security pact",
         "Canberra and Honiara agree a new security deal, deepening defence "
         "cooperation across the Pacific.",
         "shield"),
        ("Asia · Diplomacy", "North Korea expels the Swiss envoy",
         "Pyongyang orders Switzerland's ambassador to leave, the latest break "
         "in its thin diplomatic ties.",
         "flag"),
        ("South Asia · Labour", "Bangladesh garment workers win a 36% pay rise",
         "Millions of factory workers making clothes for global brands secure "
         "a large wage increase.",
         None),
        ("Asia · Defence", "India urges human control of AI in military operations",
         "New Delhi calls for people, not machines, to keep the final say over "
         "lethal force.",
         None),
    ]

    for i, (tag, head, body, pic) in enumerate(stories):
        col = i % 2
        row = i // 2
        x = x0 if col == 0 else x1
        y = top + row * row_h
        if pic == "rocket":
            draw_rocket(d, x + col_w - 52, y + 8, 44)
            y = story(d, x, y, col_w - 60, tag, head, body)
        elif pic == "shield":
            draw_shield(d, x + col_w - 52, y + 8, 44)
            y = story(d, x, y, col_w - 60, tag, head, body)
        elif pic == "flag":
            draw_flag(d, x + col_w - 56, y + 10, 44, 40)
            y = story(d, x, y, col_w - 64, tag, head, body)
        else:
            y = story(d, x, y, col_w, tag, head, body)
        if row < 2:
            hline(d, x, x + col_w, top + (row + 1) * row_h - 14, width=1)

    # ---- Footer ----------------------------------------------------------
    hline(d, 34, W - 34, H - 62, width=3)
    d.text((W // 2, H - 48),
           "All events first reported on Thursday 26 November 2026  ·  THE WORLD TODAY",
           font=font(SANS, 16), fill=MUTED, anchor="mt")

    img.save("entry.png", format="PNG", optimize=True, compress_level=9)
    print("wrote entry.png")


if __name__ == "__main__":
    main()
