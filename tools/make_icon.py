"""
Erzeugt das Programmsymbol (app.ico) fuer die EXE: dunkler Grund, Berge,
eine Gleiskurve und eine gelbe 3. Rein geometrisch gezeichnet, ohne
Schriftarten, damit das Ergebnis auf jedem Rechner gleich aussieht.

Aufruf im Projektordner:  python tools/make_icon.py
Ergebnis: src/icons/app.ico und docs/images/app-icon-vorschau.png
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ICO_PATH = ROOT / "src" / "icons" / "app.ico"
PREVIEW_PATH = ROOT / "docs" / "images" / "app-icon-vorschau.png"

ICO_SIZES = (16, 24, 32, 48, 64, 128, 256)
BASE = 1024  # in hoher Aufloesung zeichnen, danach verkleinern (glatte Kanten)

BACKGROUND = (28, 34, 40)
MOUNTAIN_FAR = (52, 62, 78)
MOUNTAIN_NEAR = (38, 46, 58)
RAIL = (190, 198, 208)
SLEEPER = (90, 98, 108)
ACCENT = (255, 200, 40)


def _mountains(draw: ImageDraw.ImageDraw) -> None:
    far = [(-50, 800), (200, 560), (380, 720), (620, 480), (860, 700), (1100, 600)]
    near = [(-50, 900), (250, 740), (500, 880), (780, 720), (1100, 880)]
    for pts, color in ((far, MOUNTAIN_FAR), (near, MOUNTAIN_NEAR)):
        draw.polygon(pts + [(1100, 1100), (-50, 1100)], fill=color)


def _track(draw: ImageDraw.ImageDraw) -> None:
    cx, cy, radius = -120, 1144, 880
    for k in range(25):
        a = math.radians(272 + k * 3.7)
        x, y = cx + radius * math.cos(a), cy + radius * math.sin(a)
        dx, dy = math.cos(a) * 70, math.sin(a) * 70
        draw.line((x - dx, y - dy, x + dx, y + dy), fill=SLEEPER, width=14)
    for r in (radius - 40, radius + 40):
        draw.arc((cx - r, cy - r, cx + r, cy + r), 268, 365, fill=RAIL, width=14)


def _three(draw: ImageDraw.ImageDraw, size: int) -> None:
    """Die Ziffer 3 aus zwei dicken Kreisboegen mit runden Enden."""

    w = round(0.125 * size)
    half = w / 2
    cx = 0.50 * size

    bowls = (
        (0.355 * size, 0.165 * size, ((205, 360), (0, 90))),
        (0.645 * size, 0.195 * size, ((270, 360), (0, 155))),
    )

    for cy, r, arcs in bowls:
        box = (cx - r, cy - r, cx + r, cy + r)
        for start, end in arcs:
            draw.arc(box, start, end, fill=ACCENT, width=w)
        for angle in (arcs[0][0], arcs[-1][1]):
            a = math.radians(angle)
            rr = r - half
            ex, ey = cx + rr * math.cos(a), cy + rr * math.sin(a)
            draw.ellipse((ex - half, ey - half, ex + half, ey + half), fill=ACCENT)

    y = 0.50 * size
    draw.rounded_rectangle(
        (cx - 0.085 * size, y - half, cx + 0.02 * size, y + half),
        radius=half,
        fill=ACCENT,
    )


def render(size: int = BASE) -> Image.Image:
    img = Image.new("RGBA", (size, size), BACKGROUND + (255,))
    draw = ImageDraw.Draw(img)
    _mountains(draw)
    _track(draw)
    _three(draw, size)

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (0, 0, size - 1, size - 1), radius=round(0.22 * size), fill=255
    )
    img.putalpha(mask)
    return img


def main() -> None:
    big = render()
    images = [big.resize((s, s), Image.LANCZOS) for s in ICO_SIZES]

    ICO_PATH.parent.mkdir(parents=True, exist_ok=True)
    images[-1].save(
        ICO_PATH,
        format="ICO",
        sizes=[(s, s) for s in ICO_SIZES],
        append_images=images[:-1],
    )

    PREVIEW_PATH.parent.mkdir(parents=True, exist_ok=True)
    big.resize((256, 256), Image.LANCZOS).save(PREVIEW_PATH)

    print("OK", ICO_PATH)


if __name__ == "__main__":
    main()