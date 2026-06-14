"""
share_card.py — Branded Shareable Result Card (PNG)
===================================================
Generates a 1200x630 (LinkedIn-friendly) image of the student's score so they
can post "I'm X% ready for {role}!" — which also markets the app.
Uses Pillow (already installed via pdfplumber).
"""

import io
from PIL import Image, ImageDraw, ImageFont

_BOLD = ["C:/Windows/Fonts/arialbd.ttf", "C:/Windows/Fonts/seguibl.ttf",
         "DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
_REG = ["C:/Windows/Fonts/arial.ttf", "C:/Windows/Fonts/segoeui.ttf",
        "DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]


def _font(size, bold=False):
    for path in (_BOLD if bold else _REG):
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def build_share_card(role, match_percent, readiness, name="", top_skills=None) -> bytes:
    W, H = 1200, 630
    img = Image.new("RGB", (W, H), (7, 11, 22))
    d = ImageDraw.Draw(img)
    # vertical gradient
    for y in range(H):
        t = y / H
        r = int(7 + t * 12); g = int(11 + t * 8); b = int(22 + t * 26)
        d.line([(0, y), (W, y)], fill=(r, g, b))
    # accent corner glow strips
    d.rectangle([0, 0, W, 8], fill=(0, 229, 255))
    d.rectangle([0, H - 8, W, H], fill=(123, 47, 247))

    d.text((60, 54), "SkillBridge", font=_font(56, True), fill=(0, 229, 255))
    d.text((64, 126), "AI CAREER GUIDANCE · SKILL-GAP ANALYZER",
           font=_font(22), fill=(150, 170, 200))

    d.text((60, 220), f"I'm {match_percent}% ready", font=_font(74, True), fill=(255, 255, 255))
    d.text((60, 312), f"for {role}", font=_font(50, True), fill=(179, 136, 255))
    d.text((60, 392), str(readiness), font=_font(34), fill=(0, 229, 160))

    bx, by, bw, bh = 60, 462, 1080, 30
    d.rounded_rectangle([bx, by, bx + bw, by + bh], radius=15, fill=(40, 46, 70))
    fillw = max(15, int(bw * max(0, min(100, match_percent)) / 100))
    d.rounded_rectangle([bx, by, bx + fillw, by + bh], radius=15, fill=(0, 200, 170))

    if top_skills:
        d.text((60, 524), "Now building: " + ", ".join(list(top_skills)[:6]),
               font=_font(24), fill=(200, 210, 230))
    tag = (name + " · " if name else "") + "Made with SkillBridge"
    d.text((60, 578), tag, font=_font(20), fill=(120, 130, 150))

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
