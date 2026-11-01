"""Platzierungshilfe fuer den Natur-Details-Mod aus OSM.

Liest Weinberge, Obstwiesen, Mauern und Hecken aus den geladenen OSM-Daten
und schreibt sie als Liste (CSV/JSON) mit Lage in Spielmetern ab Kartenmitte
(x nach Osten, y nach Norden, wie im Staedte-Export). Es baut nichts im Spiel:
Die Liste ist eine Vorlage zum Nachbauen mit dem Zaunbaukasten.

Spielmeter = echte Meter / Stauchfaktor (wie TPF2Geometry).
"""

from __future__ import annotations

import csv
import json
import math
from dataclasses import dataclass, field
from pathlib import Path

from src.heightmap.nature_rows import row_paths
from src.tpf2.tpf2_geometry import TPF2Geometry

KIND_VINEYARD = "vineyard"
KIND_ORCHARD = "orchard"
KIND_WALL = "wall"
KIND_HEDGE = "hedge"
KIND_FIELD = "field"

KIND_NAMES = {
    KIND_VINEYARD: "Weinberg",
    KIND_ORCHARD: "Obstwiese",
    KIND_WALL: "Mauer",
    KIND_HEDGE: "Hecke",
    KIND_FIELD: "Feld",
}

AREA_KINDS = (KIND_VINEYARD, KIND_ORCHARD, KIND_FIELD)
LINE_KINDS = (KIND_WALL, KIND_HEDGE)

DEFAULT_ROW_SPACING_M = 2.0


@dataclass
class NatureFeature:
    kind: str
    osm_id: int
    x: float
    y: float
    length_m: float = 0.0
    area_m2: float = 0.0
    row_direction_deg: float | None = None
    rows: int = 0
    points: list[tuple[float, float]] = field(default_factory=list)
    note: str = ""
    row_paths: list = field(default_factory=list)


def classify(tags: dict) -> str | None:
    """OSM-Tags -> Art, oder None."""

    landuse = tags.get("landuse")
    if landuse == "vineyard":
        return KIND_VINEYARD
    if landuse == "orchard":
        return KIND_ORCHARD
    if landuse == "farmland":
        return KIND_FIELD

    barrier = tags.get("barrier")
    if barrier in ("wall", "retaining_wall"):
        return KIND_WALL
    if barrier == "hedge":
        return KIND_HEDGE

    return None


def _polygon_area(points) -> float:
    total = 0.0
    n = len(points)
    for i in range(n):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % n]
        total += x1 * y2 - x2 * y1
    return abs(total) / 2.0


def _polygon_centroid(points) -> tuple[float, float]:
    n = len(points)
    return (
        sum(p[0] for p in points) / n,
        sum(p[1] for p in points) / n,
    )


def _length(points) -> float:
    return sum(
        math.hypot(points[i + 1][0] - points[i][0], points[i + 1][1] - points[i][1])
        for i in range(len(points) - 1)
    )


def _longest_edge_direction(points) -> float:
    """Richtung der laengsten Kante in Grad (0 = Norden, 90 = Osten, 0-180)."""

    best = 0.0
    direction = 0.0
    for i in range(len(points)):
        x1, y1 = points[i]
        x2, y2 = points[(i + 1) % len(points)]
        d = math.hypot(x2 - x1, y2 - y1)
        if d > best:
            best = d
            direction = math.degrees(math.atan2(x2 - x1, y2 - y1)) % 180.0
    return direction


def estimate_rows(points, direction_deg: float, spacing_m: float) -> int:
    """Grobe Zahl der Reihen: Breite des Feldes quer zur Reihenrichtung
    geteilt durch den Reihenabstand."""

    if spacing_m <= 0 or len(points) < 3:
        return 0

    theta = math.radians(direction_deg)
    # Einheitsvektor quer zur Reihenrichtung
    nx, ny = math.cos(theta), -math.sin(theta)
    offsets = [p[0] * nx + p[1] * ny for p in points]
    return max(1, int((max(offsets) - min(offsets)) / spacing_m))


def collect_features(
    osm,
    selection,
    kinds=tuple(KIND_NAMES),
    row_spacing_m: float = DEFAULT_ROW_SPACING_M,
    min_area_m2: float = 0.0,
    min_length_m: float = 0.0,
) -> list[NatureFeature]:
    """Sucht die gewuenschten Arten im Auswahlrechteck (Mitte der Form)."""

    center_lat, center_lon = selection.center
    geometry = TPF2Geometry(
        center_lat,
        center_lon,
        getattr(selection, "rotation_deg", 0.0),
        getattr(selection, "scale_factor", 1.0),
    )
    half_w = selection.width_m / 2
    half_h = selection.height_m / 2
    wanted = set(kinds)

    result: list[NatureFeature] = []

    for way in osm.ways.values():
        kind = classify(getattr(way, "tags", None) or {})
        if kind is None or kind not in wanted:
            continue

        points = []
        for node_id in way.nodes:
            node = osm.nodes.get(node_id)
            if node is None:
                continue
            points.append(geometry.convert(node.lat, node.lon))

        if len(points) < 2:
            continue

        if kind in AREA_KINDS:
            ring = points[:-1] if points[0] == points[-1] else points
            if len(ring) < 3:
                continue
            area = _polygon_area(ring)
            if area < min_area_m2:
                continue
            cx, cy = _polygon_centroid(ring)
            if abs(cx) > half_w or abs(cy) > half_h:
                continue
            direction = _longest_edge_direction(ring)
            has_rows = kind in (KIND_VINEYARD, KIND_FIELD)
            rows = estimate_rows(ring, direction, row_spacing_m) if has_rows else 0
            paths = row_paths(ring, direction, row_spacing_m) if has_rows else []
            result.append(
                NatureFeature(
                    kind=kind,
                    osm_id=way.id,
                    x=cx,
                    y=cy,
                    area_m2=area,
                    row_direction_deg=direction,
                    rows=rows,
                    points=ring,
                    row_paths=paths,
                    note=str(way.tags.get("crop") or way.tags.get("trees") or ""),
                )
            )
        else:
            length = _length(points)
            if length < min_length_m:
                continue
            mid = points[len(points) // 2]
            if abs(mid[0]) > half_w or abs(mid[1]) > half_h:
                continue
            result.append(
                NatureFeature(
                    kind=kind,
                    osm_id=way.id,
                    x=mid[0],
                    y=mid[1],
                    length_m=length,
                    points=points,
                    note=str(way.tags.get("material") or way.tags.get("height") or ""),
                )
            )

    result.sort(key=lambda f: (f.kind, -(f.area_m2 or f.length_m)))
    return result


def summarize(features) -> dict:
    """Anzahl, Flaeche (ha) und Laenge (m) je Art."""

    out = {}
    for kind in KIND_NAMES:
        items = [f for f in features if f.kind == kind]
        out[kind] = {
            "count": len(items),
            "area_ha": round(sum(f.area_m2 for f in items) / 10_000.0, 3),
            "length_m": round(sum(f.length_m for f in items), 1),
        }
    return out


def write_csv(features, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(
            ["Art", "OSM-ID", "x_m", "y_m", "Laenge_m", "Flaeche_m2",
             "Reihenrichtung_Grad", "Reihen", "Hinweis"]
        )
        for f in features:
            writer.writerow(
                [
                    KIND_NAMES[f.kind], f.osm_id, round(f.x, 1), round(f.y, 1),
                    round(f.length_m, 1), round(f.area_m2, 1),
                    "" if f.row_direction_deg is None else round(f.row_direction_deg, 0),
                    f.rows or "", f.note,
                ]
            )


def write_json(features, path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "summary": summarize(features),
        "features": [
            {
                "kind": f.kind,
                "osm_id": f.osm_id,
                "x": round(f.x, 1),
                "y": round(f.y, 1),
                "length_m": round(f.length_m, 1),
                "area_m2": round(f.area_m2, 1),
                "row_direction_deg": f.row_direction_deg,
                "rows": f.rows,
                "note": f.note,
                "points": [[round(px, 1), round(py, 1)] for px, py in f.points],
                "row_paths": [
                    [[round(a, 1), round(b, 1)], [round(c, 1), round(d, 1)]]
                    for (a, b), (c, d) in f.row_paths
                ],
            }
            for f in features
        ],
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
