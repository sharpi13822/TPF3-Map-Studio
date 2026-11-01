"""Reihenpfade fuer Weinberge und Felder aus einem OSM-Umriss.

Legt parallele Linien im Reihenabstand in die Flaeche (Spielmeter ab
Kartenmitte, x nach Osten, y nach Norden). Richtung: 0 = Norden, 90 = Osten.
Die Linien sind Grundlage zum Platzieren von Reihen-Objekten.
"""

from __future__ import annotations

import math

Point = tuple[float, float]
Segment = tuple[Point, Point]


def row_paths(
    ring: list[Point],
    direction_deg: float,
    spacing_m: float,
    min_length_m: float = 3.0,
    max_rows: int = 2000,
) -> list[Segment]:
    """Parallele Reihen innerhalb des Rings (auch bei nicht konvexen Formen).

    Gibt eine Liste von Strecken ((x1, y1), (x2, y2)) zurueck, sortiert
    von einer Seite zur anderen. Zu kurze Stuecke werden weggelassen.
    """

    if spacing_m <= 0 or len(ring) < 3:
        return []

    theta = math.radians(direction_deg)
    dx, dy = math.sin(theta), math.cos(theta)  # entlang der Reihe
    nx, ny = math.cos(theta), -math.sin(theta)  # quer zur Reihe

    offsets = [p[0] * nx + p[1] * ny for p in ring]
    lo, hi = min(offsets), max(offsets)
    count = int((hi - lo) / spacing_m)
    if count < 1:
        return []
    count = min(count, max_rows)

    # Reihen mittig in der Flaeche verteilen.
    start = lo + ((hi - lo) - (count - 1) * spacing_m) / 2.0

    n = len(ring)
    result: list[Segment] = []
    for i in range(count):
        o = start + i * spacing_m
        along: list[float] = []
        for k in range(n):
            ax, ay = ring[k]
            bx, by = ring[(k + 1) % n]
            oa = ax * nx + ay * ny
            ob = bx * nx + by * ny
            if (oa <= o < ob) or (ob <= o < oa):
                t = (o - oa) / (ob - oa)
                px = ax + t * (bx - ax)
                py = ay + t * (by - ay)
                along.append(px * dx + py * dy)
        along.sort()
        for j in range(0, len(along) - 1, 2):
            s0, s1 = along[j], along[j + 1]
            if s1 - s0 < min_length_m:
                continue
            result.append(
                (
                    (s0 * dx + o * nx, s0 * dy + o * ny),
                    (s1 * dx + o * nx, s1 * dy + o * ny),
                )
            )
    return result


def total_length(paths: list[Segment]) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in paths)
