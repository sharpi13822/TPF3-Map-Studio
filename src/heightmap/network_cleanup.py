"""
Aufraeumen des OSM-Netzes vor dem Export (siehe network_export.collect_network).

Ausgangslage aus den Spieltests: Viele Wege scheitern im Spiel an Kollisionen,
weil OSM Fahrbahnen einzeln zeichnet:

- Zwei Richtungsfahrbahnen (je ein OSM-Weg mit oneway=yes) liegen wenige Meter
  nebeneinander. Bei Autobahnen ist jede Fahrbahn im Spiel schon eine komplette
  Autobahn mit Mittelstreifen - zwei davon uebereinander sehen falsch aus.
- Dicht oder doppelt gezeichnete Gleise (z. B. Hauptgleis und Servicegleis auf
  derselben Trasse) kollidieren.

Die Funktionen arbeiten auf der Liste "runs" aus collect_network:
    (art, vorlage, kind, grade, kategorie, stueck, way_id)
mit stueck = [(osm_knoten_id, x, y), ...] in Metern. Sie liefern eine neue
Liste und eine Statistik. Vor dem Kreuzungszaehlen aufrufen.

Verfahren: ein Weg, dessen Laenge zu mindestens `coverage` von einem anderen,
laengeren Weg abgedeckt ist, entfaellt. Seine Knoten, an denen andere Wege
haengen, werden auf den naechsten Punkt des behaltenen Weges umgehaengt.
Der behaltene Weg wird bei Richtungsfahrbahnen auf die Mitte zwischen beiden
gerueckt und bekommt die zweispurige Vorlage.
"""

from __future__ import annotations

import math
from collections import defaultdict

GRID = 40.0


def _dist(a, b) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def _closest_on_segment(p, a, b):
    """(Abstand, Punkt) von p zur Strecke a-b."""

    dx, dy = b[0] - a[0], b[1] - a[1]
    l2 = dx * dx + dy * dy

    if l2 == 0:
        return _dist(p, a), a

    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / l2))
    q = (a[0] + t * dx, a[1] + t * dy)

    return _dist(p, q), q


class _SegmentIndex:
    """Raster ueber die Strecken aller behaltenen Wege."""

    def __init__(self):
        self.cells = defaultdict(list)

    def add(self, run_index: int, points) -> None:

        for a, b in zip(points, points[1:]):

            x0, x1 = sorted((a[0], b[0]))
            y0, y1 = sorted((a[1], b[1]))

            for gx in range(int(x0 // GRID) - 1, int(x1 // GRID) + 2):
                for gy in range(int(y0 // GRID) - 1, int(y1 // GRID) + 2):
                    self.cells[(gx, gy)].append((run_index, a, b))

    def nearest(self, p, max_d, accept=None):
        """Naechster Treffer (Abstand, Punkt, run_index, a, b) oder None."""

        best = None
        seen = set()

        for item in self.cells.get((int(p[0] // GRID), int(p[1] // GRID)), ()):

            if id(item) in seen:
                continue

            seen.add(id(item))
            run_index, a, b = item

            if accept is not None and not accept(run_index, a, b):
                continue

            d, q = _closest_on_segment(p, a, b)

            if d <= max_d and (best is None or d < best[0]):
                best = (d, q, run_index, a, b)

        return best


def _length(points) -> float:
    return sum(_dist(a, b) for a, b in zip(points, points[1:]))


def _angle_diff(a, b) -> float:
    return abs((a - b + math.pi) % (2 * math.pi) - math.pi)


def _seg_angle(a, b) -> float:
    return math.atan2(b[1] - a[1], b[0] - a[0])


def _sample_points(points, step=6.0):
    """Stuetzpunkte entlang des Weges (Eckpunkte und Zwischenpunkte)."""

    out = []

    for a, b in zip(points, points[1:]):
        length = _dist(a, b)
        n = max(1, int(length // step))

        for i in range(n):
            t = i / n
            out.append((
                (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])),
                _seg_angle(a, b),
                length / n,
            ))

    return out


def _drop_and_alias(runs, drop: dict, max_d):
    """
    Entfernt die Wege in `drop` (run_index -> behaltener run_index) und haengt
    deren Knoten, die auch in anderen Wegen vorkommen, auf den naechsten Punkt
    des behaltenen Weges um.
    """

    # Knoten, die in mehreren Stuecken vorkommen
    usage = defaultdict(int)

    for i, run in enumerate(runs):
        for node_id, _x, _y in run[5]:
            usage[(node_id, run[0])] += 1

    alias: dict[tuple[int, int], tuple[int, float, float]] = {}

    for i, keeper in drop.items():

        art = runs[i][0]
        kept_points = runs[keeper][5]

        for node_id, x, y in runs[i][5]:

            key = (node_id, art)

            if usage[key] < 2 or key in alias:
                continue

            # naechster Knoten des behaltenen Weges
            best = min(kept_points, key=lambda n: _dist((x, y), (n[1], n[2])))

            if _dist((x, y), (best[1], best[2])) <= max_d:
                alias[key] = best

    out = []

    for i, run in enumerate(runs):

        if i in drop:
            continue

        art, template, kind, grade, category, piece, way_id = run

        new_piece = []

        for node_id, x, y in piece:

            hit = alias.get((node_id, art))

            if hit is not None:
                node_id, x, y = hit

            if new_piece and new_piece[-1][0] == node_id:
                continue

            new_piece.append((node_id, x, y))

        if len(new_piece) >= 2:
            out.append((art, template, kind, grade, category, new_piece, way_id))

    return out


def merge_dual_carriageways(runs, two_way_template_for, oneway_templates,
                            max_gap=None, coverage=0.7, include_oneway_roads=True):
    """
    Fasst gegenlaeufige, parallele Einbahn-Wege zu einem zweispurigen Weg
    zusammen.

    runs:                 siehe Modulbeschreibung (Fahrtrichtung = Punktreihenfolge)
    two_way_template_for: Funktion kategorie -> zweispurige Vorlage oder None
    oneway_templates:     Menge der Einbahn-Vorlagen (diese Wege sind Kandidaten)
    max_gap:              dict kategorie -> groesster Abstand der Fahrbahnen in m
                          (Standard 22 m)
    """

    max_gap = max_gap or {}

    def gap_for(category):
        return max_gap.get(category, 22.0)

    candidates = []

    for i, (art, template, kind, _g, category, piece, _w) in enumerate(runs):

        if art != 0 or kind != 0 or len(piece) < 2:
            continue

        if piece[0][0] == piece[-1][0]:  # Kreisverkehr / geschlossener Weg
            continue

        wanted = two_way_template_for(category)

        if wanted is None:
            continue

        # Autobahnen: Vorlage ist schon zweispurig, aber nur mit Einbahn-Tag
        # wissen wir die Richtung. Kandidaten sind Wege der Kategorien, die der
        # Aufrufer als Richtungsfahrbahn kennzeichnet (Einbahn-Vorlage oder
        # Autobahn).
        if (include_oneway_roads and template in oneway_templates) or category == "highway=motorway":
            candidates.append(i)

    candidates.sort(key=lambda i: -_length([(x, y) for _n, x, y in runs[i][5]]))

    index = _SegmentIndex()
    kept_polylines: dict[int, list] = {}
    drop: dict[int, int] = {}
    upgraded: set[int] = set()
    moved: dict[tuple[int, int], tuple[float, float]] = {}

    for i in candidates:

        category = runs[i][4]
        points = [(x, y) for _n, x, y in runs[i][5]]
        d = gap_for(category)

        # wird dieser Weg von einer schon behaltenen Gegenfahrbahn abgedeckt?
        total = covered = 0.0
        votes: dict[int, float] = defaultdict(float)

        for p, ang, w in _sample_points(points):

            total += w

            def accept(run_index, a, b, ang=ang):
                return (
                    runs[run_index][4] == category
                    and _angle_diff(ang, _seg_angle(a, b)) > math.radians(120)
                )

            hit = index.nearest(p, d, accept)

            if hit is not None:
                covered += w
                votes[hit[2]] += w

        if total > 0 and covered / total >= coverage and votes:
            keeper = max(votes, key=votes.get)
            drop[i] = keeper
            upgraded.add(keeper)
            continue

        index.add(i, points)
        kept_polylines[i] = points

    # Behaltene Wege, die jemanden ersetzt haben: zweispurig und in die Mitte
    # zwischen beide Fahrbahnen schieben (Abstand zu allen weggefallenen Wegen).
    dropped_index = _SegmentIndex()

    for i in drop:
        dropped_index.add(i, [(x, y) for _n, x, y in runs[i][5]])

    result_runs = list(runs)

    for k in upgraded:

        art, template, kind, grade, category, piece, way_id = runs[k]
        new_piece = []

        for node_id, x, y in piece:

            hit = dropped_index.nearest((x, y), gap_for(category))

            if hit is not None:
                nx, ny = (x + hit[1][0]) / 2, (y + hit[1][1]) / 2
                moved[(node_id, art)] = (nx, ny)
                x, y = nx, ny

            new_piece.append((node_id, x, y))

        result_runs[k] = (
            art, two_way_template_for(category), kind, grade, category, new_piece, way_id,
        )

    # Verschobene Knoten gelten fuer alle Wege, die sie benutzen
    if moved:
        for i, run in enumerate(result_runs):

            if i in drop:
                continue

            art, template, kind, grade, category, piece, way_id = run

            piece2 = [
                (n, *moved.get((n, art), (x, y))) for n, x, y in piece
            ]
            result_runs[i] = (art, template, kind, grade, category, piece2, way_id)

    cleaned = _drop_and_alias(result_runs, drop, max(gap_for(runs[i][4]) for i in drop) if drop else 0)

    stats = {"merged_pairs": len(drop), "upgraded": len(upgraded)}

    return cleaned, stats


def dedupe_tracks(runs, duplicate_m=3.0, service_m=4.5, coverage=0.8,
                  is_service_template=None):
    """
    Entfernt doppelt gezeichnete Gleise: ein Gleis, das zu `coverage` seiner
    Laenge dichter als `duplicate_m` an einem vorrangigen Gleis liegt, entfaellt;
    Servicegleise (is_service_template) schon bei `service_m`. Laengere Wege und
    wichtigere Vorlagen bleiben.
    """

    candidates = [
        i for i, run in enumerate(runs)
        if run[0] == 1 and run[2] == 0 and len(run[5]) >= 2
    ]

    def priority(i):
        service = bool(is_service_template and is_service_template(runs[i][1]))
        return (service, -_length([(x, y) for _n, x, y in runs[i][5]]))

    candidates.sort(key=priority)

    index = _SegmentIndex()
    drop: dict[int, int] = {}

    for i in candidates:

        points = [(x, y) for _n, x, y in runs[i][5]]
        service = bool(is_service_template and is_service_template(runs[i][1]))
        d = service_m if service else duplicate_m

        total = covered = 0.0
        votes: dict[int, float] = defaultdict(float)

        for p, _ang, w in _sample_points(points):

            total += w
            hit = index.nearest(p, d, lambda j, a, b: j != i)

            if hit is not None:
                covered += w
                votes[hit[2]] += w

        if total > 0 and covered / total >= coverage and votes:
            drop[i] = max(votes, key=votes.get)
            continue

        index.add(i, points)

    cleaned = _drop_and_alias(list(runs), drop, service_m + 1.0) if drop else list(runs)

    return cleaned, {"tracks_removed": len(drop)}
