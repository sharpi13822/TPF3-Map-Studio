"""
Biome-Maske aus OSM-Landnutzung (TPF3).

Der Karteneditor von Transport Fever 3 nimmt im Biome-Tab ein 8-Bit-
Graustufenbild: fuenf gleich breite Intervalle, Grauwert 26 = Biom 0,
77 = Biom 1, 128 = Biom 2, 179 = Biom 3, 230 = Biom 4. Die Maske wird im
Spiel auf die Kartengroesse gestreckt (nur das Seitenverhaeltnis muss
stimmen).

Wie die fuenf Biome aussehen (im Spiel gesehen, 01.10.2026):
    Biom 0  helle, gruene Wiese ohne Baeume
    Biom 1  Wiese mit Baumgruppen
    Biom 2  dunkle, bewachsene Wiese ohne Baeume
    Biom 3  trockene Steppe (gelbbraun)
    Biom 4  gruen-braun gemischt (Savanne)

Die Zuordnung "OSM-Landnutzung -> Biom" in DEFAULT_ASSIGNMENT ist ein
VORSCHLAG nach dem Aussehen der Biome und im Spiel noch nicht geprueft.
Im Dialog laesst sie sich je Kategorie aendern.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from src.heightmap.water_terrain_blend import (
    _latlon_to_pixel,
    assemble_rings,
    ring_is_usable,
)
from src.tpf2.tpf2_geometry import TPF2Geometry

# Grauwerte der fuenf Biome (Mitten der Intervalle).
BIOME_GRAY = (26, 77, 128, 179, 230)

BIOME_NAMES = (
    "Biom 0 - helle Wiese",
    "Biom 1 - Wiese mit Baumgruppen",
    "Biom 2 - dunkle Wiese",
    "Biom 3 - trockene Steppe",
    "Biom 4 - gruen-braun gemischt",
)

# Biom fuer alles, was keine Kategorie trifft (und fuer Wasser).
BACKGROUND_BIOME = 0

# Kategorien in Zeichenreihenfolge: Spaetere ueberdecken fruehere.
# (Schluessel, Anzeigename, {OSM-Tag: Werte})
CATEGORIES: tuple[tuple[str, str, dict[str, frozenset[str]]], ...] = (
    (
        "grass",
        "Wiese, Weide, Park",
        {
            "landuse": frozenset(
                {"meadow", "grass", "village_green", "recreation_ground",
                 "greenfield"}
            ),
            "natural": frozenset({"grassland"}),
            "leisure": frozenset({"park", "garden", "pitch", "golf_course"}),
        },
    ),
    (
        "farmland",
        "Acker, Weinberg, Obstbau",
        {
            "landuse": frozenset(
                {"farmland", "farmyard", "vineyard", "orchard", "allotments",
                 "plant_nursery"}
            ),
        },
    ),
    (
        "wet_heath",
        "Moor, Sumpf, Heide",
        {
            "natural": frozenset({"wetland", "heath", "scrub", "fell"}),
            "landuse": frozenset({"marsh", "swamp"}),
            "wetland": frozenset(
                {"bog", "marsh", "swamp", "fen", "reedbed", "wet_meadow"}
            ),
        },
    ),
    (
        "forest",
        "Wald",
        {
            "landuse": frozenset({"forest"}),
            "natural": frozenset({"wood"}),
        },
    ),
    (
        "bare",
        "Fels, Sand, Abbau",
        {
            "natural": frozenset(
                {"bare_rock", "scree", "sand", "shingle", "beach", "cliff"}
            ),
            "landuse": frozenset({"quarry", "brownfield", "construction"}),
        },
    ),
    (
        "settlement",
        "Siedlung, Industrie, Gewerbe",
        {
            "landuse": frozenset(
                {"residential", "industrial", "commercial", "retail",
                 "railway", "garages", "military"}
            ),
        },
    ),
)

# Vorschlag (noch nicht im Spiel geprueft).
DEFAULT_ASSIGNMENT: dict[str, int | None] = {
    "grass": 0,
    "farmland": 3,
    "wet_heath": 2,
    "forest": 1,
    "bare": 3,
    "settlement": 4,
}

# Vorschaufarben (RGB) je Biom, nur fuer die Vorschau im Dialog.
BIOME_PREVIEW_RGB = (
    (150, 190, 90),
    (60, 110, 50),
    (80, 110, 60),
    (200, 170, 90),
    (170, 150, 80),
)


def category_of_tags(tags: dict | None) -> list[str]:
    """Liefert die Schluessel aller Kategorien, auf die die Tags passen."""

    if not tags:
        return []

    hits = []

    for key, _label, rules in CATEGORIES:
        for tag, values in rules.items():
            if tags.get(tag) in values:
                hits.append(key)
                break

    return hits


def _relations(osm) -> list:
    relations = getattr(osm, "relations", None)

    if relations is None:
        return []

    if isinstance(relations, dict):
        return list(relations.values())

    return list(relations)


def build_biome_index(
    osm,
    selection,
    w_px: int,
    h_px: int,
    assignment: dict[str, int | None] | None = None,
) -> np.ndarray:
    """
    Rastert die geladenen OSM-Flaechen in ein Biom-Indexbild (uint8, Werte
    0..4, Zeile 0 = Norden wie beim Hoehenraster). Kategorien mit Zuordnung
    None werden uebersprungen. Spaetere Kategorien ueberdecken fruehere.
    """

    assignment = dict(DEFAULT_ASSIGNMENT if assignment is None else assignment)

    center_lat, center_lon = selection.center
    geometry = TPF2Geometry(center_lat, center_lon, selection.rotation_deg)
    width_m, height_m = selection.width_m, selection.height_m

    def node_points(node_ids):
        points = []
        for node_id in node_ids:
            node = osm.nodes.get(node_id)
            if node is None:
                continue
            points.append(
                _latlon_to_pixel(
                    geometry, node.lat, node.lon, width_m, height_m, w_px, h_px
                )
            )
        return points

    wanted = {k for k, v in assignment.items() if v is not None}

    masks = {
        key: Image.new("L", (w_px, h_px), 0)
        for key, _label, _rules in CATEGORIES
        if key in wanted
    }
    draws = {key: ImageDraw.Draw(img) for key, img in masks.items()}

    # Einfache geschlossene Flaechen.
    for way in osm.ways.values():

        keys = [k for k in category_of_tags(way.tags) if k in wanted]

        if not keys:
            continue

        nodes = list(way.nodes)

        if len(nodes) < 4 or nodes[0] != nodes[-1]:
            continue

        points = node_points(nodes)

        if not ring_is_usable(points):
            continue

        for key in keys:
            draws[key].polygon(points, fill=255)

    # Multipolygone: aeussere Ringe fuellen, innere aushoehlen.
    for relation in _relations(osm):

        tags = getattr(relation, "tags", None) or {}

        keys = [k for k in category_of_tags(tags) if k in wanted]

        if not keys:
            continue

        outer_ways, inner_ways = [], []

        for member in relation.members:
            if member.type != "way":
                continue
            way = osm.ways.get(member.ref)
            if way is None:
                continue
            (inner_ways if member.role == "inner" else outer_ways).append(way)

        for key in keys:

            for ring in assemble_rings([w.nodes for w in outer_ways]):
                points = node_points(ring)
                if ring_is_usable(points):
                    draws[key].polygon(points, fill=255)

            for ring in assemble_rings([w.nodes for w in inner_ways]):
                points = node_points(ring)
                if ring_is_usable(points):
                    draws[key].polygon(points, fill=0)

    index = np.full((h_px, w_px), BACKGROUND_BIOME, dtype=np.uint8)

    for key, _label, _rules in CATEGORIES:

        if key not in masks:
            continue

        mask = np.array(masks[key], dtype=bool)

        index[mask] = int(assignment[key])

    return index


def index_to_gray(index: np.ndarray) -> np.ndarray:
    """Biom-Indizes 0..4 in die Grauwerte fuer die Biome-Maske umsetzen."""

    lookup = np.array(BIOME_GRAY, dtype=np.uint8)

    return lookup[np.clip(index, 0, len(BIOME_GRAY) - 1)]


def index_to_preview_rgb(index: np.ndarray) -> np.ndarray:
    lookup = np.array(BIOME_PREVIEW_RGB, dtype=np.uint8)

    return lookup[np.clip(index, 0, len(BIOME_PREVIEW_RGB) - 1)]


def save_biome_png(path: str | Path, index: np.ndarray) -> Path:
    """Schreibt die Biome-Maske als 8-Bit-Graustufen-PNG."""

    path = Path(path)

    Image.fromarray(index_to_gray(index), mode="L").save(path)

    return path


def mask_size_for_selection(selection, meters_per_pixel: float) -> tuple[int, int]:
    """Breite/Hoehe der Maske in Pixeln (Seitenverhaeltnis wie die Karte)."""

    w_px = max(2, int(round(selection.width_m / meters_per_pixel)))
    h_px = max(2, int(round(selection.height_m / meters_per_pixel)))

    return w_px, h_px
