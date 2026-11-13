"""
Bauvorlage als Bild (Wunsch aus der Community, Th3_d4rk_sh4d0w).

Zeichnet Strassen (alle Klassen, nach Klasse eingefaerbt), Gleise im
Trackmap-Stil (schwarz-weiss geblockt) und Bahnsteige (graue Flaechen) aus
den geladenen OSM-Daten in ein Bild in der Groesse der Karte. Zeile 0 ist
Norden, Pixel liegen auf demselben Raster wie die Heightmap. Die Vorlage
dient zum 1:1-Nachbauen im Spiel; gebaut wird nichts.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from src.heightmap.water_terrain_blend import _latlon_to_pixel
from src.tpf2.tpf2_geometry import TPF2Geometry

BACKGROUND = (255, 255, 255)

# Strassenklasse -> (Farbe, Breite in Metern), in Zeichenreihenfolge
# (spaetere liegen oben). Breiten grob nach echten Fahrbahnen.
ROAD_STYLES: tuple[tuple[str, tuple[int, int, int], float], ...] = (
    ("path", (190, 170, 140), 2.0),
    ("track", (170, 130, 80), 3.0),
    ("service", (175, 175, 175), 4.0),
    ("living_street", (150, 150, 150), 5.0),
    ("residential", (130, 130, 130), 6.0),
    ("unclassified", (120, 120, 120), 6.0),
    ("tertiary", (230, 200, 60), 7.0),
    ("secondary", (240, 160, 40), 8.0),
    ("primary", (230, 110, 40), 10.0),
    ("trunk", (210, 60, 50), 14.0),
    ("motorway", (170, 30, 120), 22.0),
)

_HIGHWAY_CLASS = {
    "motorway": "motorway", "motorway_link": "motorway",
    "trunk": "trunk", "trunk_link": "trunk",
    "primary": "primary", "primary_link": "primary",
    "secondary": "secondary", "secondary_link": "secondary",
    "tertiary": "tertiary", "tertiary_link": "tertiary",
    "unclassified": "unclassified", "residential": "residential",
    "living_street": "living_street", "service": "service",
    "track": "track", "pedestrian": "path", "footway": "path",
    "cycleway": "path", "path": "path", "bridleway": "path", "steps": "path",
}

# Gleisart -> Breite in Metern (Hauptbahn breiter als Tram)
RAIL_WIDTH_M = {
    "rail": 6.0, "light_rail": 5.0, "subway": 5.0, "narrow_gauge": 4.0,
    "tram": 3.0, "funicular": 3.0, "monorail": 3.0,
}
RAIL_MIN_PX = 3
RAIL_BLOCK_M = 40.0          # Laenge eines schwarzen/weissen Blocks
RAIL_COLOR = (0, 0, 0)
RAIL_TUNNEL_COLOR = (110, 110, 110)
PLATFORM_COLOR = (150, 150, 150)
PLATFORM_LINE_WIDTH_M = 4.0


def road_class(tags) -> str | None:
    """Klasse fuer ROAD_STYLES oder None (kein Strassenweg)."""

    tags = tags or {}
    return _HIGHWAY_CLASS.get(tags.get("highway"))


def rail_kind(tags) -> str | None:
    tags = tags or {}
    kind = tags.get("railway")
    return kind if kind in RAIL_WIDTH_M else None


def is_platform(tags) -> bool:
    tags = tags or {}
    return tags.get("railway") == "platform" or (
        tags.get("public_transport") == "platform"
        and any(tags.get(k) == "yes" for k in ("train", "light_rail", "subway", "tram"))
    )


def _width_px(width_m: float, px_per_m: float) -> int:
    return max(1, int(round(width_m * px_per_m)))


def _dashes(points, block_px: float):
    """Teilt eine Linie in Stuecke der Laenge block_px; liefert jedes zweite
    (die weissen Bloecke), fortlaufend ueber die Knicke hinweg."""

    pieces, current = [], []
    pos = 0.0
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        seg = math.hypot(x1 - x0, y1 - y0)
        if seg <= 0:
            continue
        done = 0.0
        while done < seg:
            block = int(pos // block_px)
            step = min(seg - done, (block + 1) * block_px - pos)
            t0, t1 = done / seg, (done + step) / seg
            a = (x0 + (x1 - x0) * t0, y0 + (y1 - y0) * t0)
            b = (x0 + (x1 - x0) * t1, y0 + (y1 - y0) * t1)
            if block % 2 == 1:
                if not current:
                    current = [a]
                current.append(b)
            elif current:
                pieces.append(current)
                current = []
            done += step
            pos += step
            if block % 2 == 1 and int(pos // block_px) != block and current:
                pieces.append(current)
                current = []
    if len(current) >= 2:
        pieces.append(current)
    return pieces


def render_build_template(
    osm,
    selection,
    w_px: int,
    h_px: int,
    roads: bool = True,
    rails: bool = True,
    platforms: bool = True,
) -> Image.Image:
    """Zeichnet die Bauvorlage (RGB, w_px x h_px, Zeile 0 = Norden)."""

    center_lat, center_lon = selection.center
    geometry = TPF2Geometry(
        center_lat, center_lon, selection.rotation_deg,
        getattr(selection, "scale_factor", 1.0),
    )
    width_m, height_m = selection.width_m, selection.height_m
    px_per_m = w_px / width_m

    def points_of(way):
        pts = []
        for node_id in way.nodes:
            node = osm.nodes.get(node_id)
            if node is not None:
                pts.append(_latlon_to_pixel(geometry, node.lat, node.lon, width_m, height_m, w_px, h_px))
        return pts

    image = Image.new("RGB", (w_px, h_px), BACKGROUND)
    draw = ImageDraw.Draw(image)

    road_ways = {name: [] for name, _c, _w in ROAD_STYLES}
    rail_ways, platform_ways = [], []

    for way in osm.ways.values():
        tags = getattr(way, "tags", None) or {}
        if roads:
            klass = road_class(tags)
            if klass is not None:
                road_ways[klass].append(way)
                continue
        if rails and rail_kind(tags) is not None:
            rail_ways.append(way)
            continue
        if platforms and is_platform(tags):
            platform_ways.append(way)

    for way in platform_ways:
        pts = points_of(way)
        if len(pts) < 2:
            continue
        if len(pts) >= 4 and way.nodes[0] == way.nodes[-1]:
            draw.polygon(pts, fill=PLATFORM_COLOR)
        else:
            draw.line(pts, fill=PLATFORM_COLOR, width=_width_px(PLATFORM_LINE_WIDTH_M, px_per_m), joint="curve")

    for name, color, road_width_m in ROAD_STYLES:
        width = _width_px(road_width_m, px_per_m)
        for way in road_ways[name]:
            pts = points_of(way)
            if len(pts) >= 2:
                draw.line(pts, fill=color, width=width, joint="curve")

    block_px = max(2.0, RAIL_BLOCK_M * px_per_m)
    for way in rail_ways:
        pts = points_of(way)
        if len(pts) < 2:
            continue
        tags = way.tags or {}
        # mindestens 3 Pixel, sonst bleibt fuer die weissen Bloecke kein Platz
        width = max(RAIL_MIN_PX, _width_px(RAIL_WIDTH_M[rail_kind(tags)], px_per_m))
        tunnel = tags.get("tunnel") not in (None, "no")
        draw.line(pts, fill=RAIL_TUNNEL_COLOR if tunnel else RAIL_COLOR, width=width, joint="curve")
        inner = width - 2
        if inner >= 1:
            for piece in _dashes(pts, block_px):
                draw.line(piece, fill=BACKGROUND, width=inner)

    return image


def save_build_template(image: Image.Image, path: str | Path) -> list[Path]:
    """Speichert als .tga und .png (gleicher Name); liefert beide Pfade."""

    base = Path(path).with_suffix("")
    tga, png = base.with_suffix(".tga"), base.with_suffix(".png")
    image.save(tga)
    image.save(png)
    return [tga, png]


def legend_rows() -> list[tuple[str, tuple[int, int, int]]]:
    """Farben fuer die Erklaerung im Dialog (Name, RGB)."""

    return [(name, color) for name, color, _w in reversed(ROAD_STYLES)] + [
        ("rail", RAIL_COLOR), ("platform", PLATFORM_COLOR)
    ]
