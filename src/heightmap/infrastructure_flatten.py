"""
Trassen und Siedlungen einebnen.

Bahnstrecken, groessere Strassen und Ortschaften (Gebaeude) sollen im Spiel
auf moeglichst ebenem Gelaende liegen, sonst braucht man dort viele Rampen und
Einschnitte. Die Funktion legt aus den OSM-Daten eine Maske dieser Flaechen an
und blendet dort das Gelaende in eine kraeftig geglaettete Fassung. Ausserhalb
der Maske bleibt es unveraendert, dazwischen vermittelt ein weicher Uebergang.

Bewusster Kompromiss: Einschnitte, Daemme und kleine Kuppen entlang der Trasse
werden abgeflacht - die echte Geländeform weicht dort geringfuegig ab.
"""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import distance_transform_edt, gaussian_filter

from src.heightmap.water_terrain_blend import _latlon_to_pixel
from src.tpf2.tpf2_geometry import TPF2Geometry

# Strassen: nur die groesseren (Wege, Pfade und Waldstrassen gaebe es tausende
# und sind fuer die Bebaubarkeit unwichtig).
FLATTEN_HIGHWAY_TYPES = frozenset({
    "motorway", "motorway_link", "trunk", "trunk_link",
    "primary", "primary_link", "secondary", "secondary_link",
    "tertiary", "tertiary_link",
})

FLATTEN_RAILWAY_TYPES = frozenset({
    "rail", "light_rail", "narrow_gauge", "tram", "subway",
})


def build_infrastructure_mask(
    osm,
    selection,
    w_px: int,
    h_px: int,
    pixel_size_m: float,
    line_width_m: float = 24.0,
    building_margin_m: float = 30.0,
) -> np.ndarray:
    """
    Binaere Maske (True = einebnen) im Raster des Hoehenrasters:
    Bahnstrecken und groessere Strassen als Linien der Breite line_width_m,
    Gebaeude als gefuellte Flaechen, um building_margin_m erweitert
    (Umgriff der Siedlung).
    """

    center_lat, center_lon = selection.center
    geometry = TPF2Geometry(center_lat, center_lon, selection.rotation_deg)
    width_m, height_m = selection.width_m, selection.height_m

    lines = Image.new("L", (w_px, h_px), 0)
    lines_draw = ImageDraw.Draw(lines)

    buildings = Image.new("L", (w_px, h_px), 0)
    buildings_draw = ImageDraw.Draw(buildings)

    line_width_px = max(1, int(round(line_width_m / pixel_size_m)))

    def way_points(way):

        points = []

        for node_id in way.nodes:

            node = osm.nodes.get(node_id)

            if node is None:
                continue

            points.append(
                _latlon_to_pixel(
                    geometry, node.lat, node.lon,
                    width_m, height_m, w_px, h_px,
                )
            )

        return points

    for way in osm.ways.values():

        tags = way.tags

        if tags.get("railway") in FLATTEN_RAILWAY_TYPES:

            points = way_points(way)

            if len(points) >= 2:
                lines_draw.line(points, fill=255, width=line_width_px)

        elif tags.get("highway") in FLATTEN_HIGHWAY_TYPES:

            points = way_points(way)

            if len(points) >= 2:
                lines_draw.line(points, fill=255, width=line_width_px)

        elif "building" in tags:

            points = way_points(way)

            if len(points) >= 3:
                buildings_draw.polygon(points, fill=255)

    mask = np.array(lines, dtype=bool)

    building_mask = np.array(buildings, dtype=bool)

    if building_mask.any() and building_margin_m > 0:

        margin_px = building_margin_m / pixel_size_m

        building_mask = distance_transform_edt(~building_mask) <= margin_px

    return mask | building_mask


def flatten_infrastructure(
    heightmap: np.ndarray,
    mask: np.ndarray,
    pixel_size_m: float,
    sigma_m: float = 60.0,
    feather_m: float = 40.0,
    strength: float = 1.0,
) -> np.ndarray:
    """
    Blendet das Gelaende innerhalb von mask in eine mit sigma_m geglaettete
    Fassung. feather_m ist die Breite des weichen Uebergangs ausserhalb der
    Maske. Liefert eine NEUE Kopie, heightmap bleibt unveraendert.
    """

    if heightmap.shape != mask.shape:
        raise ValueError(
            "heightmap und mask muessen dieselbe Form haben "
            f"({heightmap.shape} != {mask.shape})"
        )

    if not mask.any() or strength <= 0 or sigma_m <= 0:
        return heightmap.copy()

    heights = heightmap.astype(np.float32, copy=False)

    smooth = gaussian_filter(
        heights,
        sigma=sigma_m / pixel_size_m,
        mode="nearest",
        truncate=3.0,
    )

    feather_px = max(1.0, feather_m / pixel_size_m)

    distance_px = distance_transform_edt(~mask)

    t = np.clip(1.0 - distance_px / feather_px, 0.0, 1.0)

    weight = (t * t * (3 - 2 * t) * float(min(1.0, strength))).astype(
        np.float32
    )

    result = heights * (1 - weight) + smooth * weight

    return result.astype(heightmap.dtype, copy=False)
