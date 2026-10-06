"""
Bahnhoefe aus den geladenen OSM-Daten auslesen und als Datei speichern.

Gelesen wird (nur aus dem, was das Studio an OSM-Daten geladen hat):
  - Bahnhoefe und Haltepunkte: Knoten mit railway=station/halt/stop/tram_stop oder public_transport=station,
    sowie geschlossene Wege (Flaechen) mit railway=station oder public_transport=station
  - Bahnsteige: Wege mit railway=platform / public_transport=platform (und platform_edge), Knoten mit railway=platform
  - Bahnhofsgebaeude: Wege mit building=train_station / transportation oder building an einer Bahnhofsflaeche
  - Haltepositionen: Knoten mit public_transport=stop_position (Zug, S-Bahn, U-Bahn, Strassenbahn)

Alles bekommt Koordinaten in Metern ab der Kartenmitte (wie die Strassen und Gleise) und wird dem naechsten
Bahnhof innerhalb von radius_m zugeordnet. Es wird nichts im Spiel gebaut.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

from src.tpf2.tpf2_geometry import TPF2Geometry

STATION_VERSION = 1

# Bahnhofs-Anker: railway=station/halt/tram_stop. railway=stop ist eine HALTEPOSITION auf dem Gleis (ein Bahnhof
# hat meist mehrere) und wird deshalb nicht als eigener Bahnhof gezaehlt.
STATION_RAILWAY = {"station": "station", "halt": "halt", "tram_stop": "tram_stop"}
STOP_RAILWAY = "stop"

# Bahnhoefe mit anderem Lebenszyklus: Betriebsbahnhoefe (railway=service_station), stillgelegte
# (disused:railway / disused:public_transport) und Bauvorhaben (construction:railway). Beispiel Ruedesheim 2026:
# Der alte Bahnhof steht als service_station + disused:public_transport=station in OSM, der neue ist im Bau.
LIFECYCLE_KINDS = {"station": "station", "halt": "halt"}

# Bahnhoefe und Haltepunkte, die naeher beieinander liegen, gelten als derselbe Bahnhof, wenn ihr Name gleich ist
# (oder einer keinen hat oder eine Flaeche ist); Haltepositionen gleichen Namens bilden bis CLUSTER_M einen
# Bahnhof, wenn es keinen Bahnhofspunkt gibt.
MERGE_M = 150.0
CLUSTER_M = 400.0
PLATFORM_WAYS = {"platform", "platform_edge"}
BUILDING_VALUES = {"train_station"}
MODE_TAGS = ("train", "light_rail", "subway", "tram")

KEEP_TAGS = (
    "name", "alt_name", "short_name", "ref", "uic_ref", "ref:IBNR", "operator", "network", "wikidata",
    "railway", "public_transport", "train", "light_rail", "subway", "tram", "station", "usage",
    "level", "layer", "tracks", "platforms", "wheelchair", "building", "height", "width", "length",
    "local_ref", "railway:ref", "ele", "usage", "disused", "abandoned", "highway", "bus",
    "note", "old_name", "disused:railway", "disused:public_transport", "construction", "construction:railway",
)


def _station_kind(tags: dict):
    """
    Art und Status eines Bahnhofsknotens oder None, wenn es keiner ist.
    Status: "" (in Betrieb), "aufgegeben", "im_bau" oder "betriebsbahnhof".
    """

    railway = tags.get("railway")

    if tags.get("construction:railway") in LIFECYCLE_KINDS:
        return LIFECYCLE_KINDS[tags["construction:railway"]], "im_bau"

    if railway == "construction" and tags.get("construction") in LIFECYCLE_KINDS:
        return LIFECYCLE_KINDS[tags["construction"]], "im_bau"

    disused = (
        tags.get("disused:railway") in LIFECYCLE_KINDS
        or tags.get("disused:public_transport") == "station"
    )

    if railway in STATION_RAILWAY:
        return STATION_RAILWAY[railway], "aufgegeben" if disused else ""

    if railway == "service_station":
        return "service_station", "aufgegeben" if disused else "betriebsbahnhof"

    if disused:
        return LIFECYCLE_KINDS.get(tags.get("disused:railway"), "station"), "aufgegeben"

    if tags.get("public_transport") == "station" and tags.get("train") == "yes":
        return "station", ""

    return None


def _tags(obj) -> dict:
    return getattr(obj, "tags", None) or {}


def _pick(tags: dict) -> dict:
    return {key: tags[key] for key in KEEP_TAGS if key in tags}


def _polyline_length(points: list) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))


def _convex_hull(points: list) -> list:
    pts = sorted({(round(p[0], 6), round(p[1], 6)) for p in points})

    if len(pts) <= 2:
        return pts

    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])

    lower: list = []
    for p in pts:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)

    upper: list = []
    for p in reversed(pts):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)

    return lower[:-1] + upper[:-1]


def _polygon_extent(points: list) -> tuple[float, float]:
    """
    (lange Seite, kurze Seite) des kleinsten umschliessenden Rechtecks einer Flaeche in Metern.

    Bahnsteige sind in OSM oft als geschlossene Flaeche gezeichnet; der Umfang waere doppelt so lang wie
    der Bahnsteig. Fuer ein Rechteck ist das Ergebnis exakt, bei unregelmaessigen Flaechen eine gute Naeherung.
    """

    hull = _convex_hull(points)

    if len(hull) < 3:
        return (_polyline_length(points) / 2.0, 0.0)

    best = None

    for i, (x1, y1) in enumerate(hull):
        x2, y2 = hull[(i + 1) % len(hull)]
        norm = math.hypot(x2 - x1, y2 - y1)

        if norm == 0:
            continue

        ux, uy = (x2 - x1) / norm, (y2 - y1) / norm
        us = [(x - x1) * ux + (y - y1) * uy for x, y in hull]
        vs = [-(x - x1) * uy + (y - y1) * ux for x, y in hull]
        width, height = max(us) - min(us), max(vs) - min(vs)

        if best is None or width * height < best[0]:
            best = (width * height, max(width, height), min(width, height))

    return (best[1], best[2]) if best else (_polyline_length(points) / 2.0, 0.0)


def _area_and_centroid(points: list) -> tuple[float, tuple[float, float]]:
    """Flaeche (Schuhband) und Schwerpunkt eines Polygons; bei Entartung der Mittelpunkt der Punkte."""

    pts = points[:-1] if len(points) > 1 and points[0] == points[-1] else points

    if len(pts) < 3:
        cx = sum(p[0] for p in pts) / max(len(pts), 1)
        cy = sum(p[1] for p in pts) / max(len(pts), 1)
        return 0.0, (cx, cy)

    twice = cx = cy = 0.0

    for a, b in zip(pts, pts[1:] + pts[:1]):
        cross = a[0] * b[1] - b[0] * a[1]
        twice += cross
        cx += (a[0] + b[0]) * cross
        cy += (a[1] + b[1]) * cross

    if abs(twice) < 1e-9:
        return 0.0, (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))

    return abs(twice) / 2.0, (cx / (3.0 * twice), cy / (3.0 * twice))


# Bahnsteige sind in OSM oft in mehrere Wege zerteilt (Beispiel Filsen: je Gleis drei Stuecke, die
# aneinanderstossen). Wege gleicher ref, deren Enden sich beruehren, zaehlen als EIN Bahnsteig.
PLATFORM_JOIN_M = 0.5


def merge_platform_ways(platforms: list[dict], join_m: float = PLATFORM_JOIN_M) -> list[dict]:
    """
    Fasst aneinanderstossende Bahnsteig-Wege mit gleicher, nicht leerer ref zu einem Bahnsteig zusammen.

    Nur type == "platform" mit OSM-Weg. Kanten (platform_edge), Punkte und Bahnsteige ohne ref bleiben
    unberuehrt. Der zusammengefasste Eintrag behaelt alle OSM-Wege in "osm_ways", die Laenge ist die Summe;
    die Gesamtlaenge aller Bahnsteige aendert sich also nicht. Die Reihenfolge der Liste bleibt erhalten.
    """

    def near(a, b):
        return math.hypot(a[0] - b[0], a[1] - b[1]) <= join_m

    def eligible(item):
        return (
            item.get("type") == "platform"
            and item.get("osm_way") is not None
            and len(item.get("points", [])) >= 2
            and (item.get("ref") or "").strip() != ""
            and not item.get("closed")
        )

    groups: dict[str, list[tuple[int, dict]]] = {}
    positioned: list[tuple[int, dict]] = []

    for index, item in enumerate(platforms):
        if eligible(item):
            groups.setdefault(item["ref"].strip(), []).append((index, item))
        else:
            positioned.append((index, item))

    for members in groups.values():
        remaining = list(members)

        while remaining:
            first_index, first = remaining.pop(0)
            points = list(first["points"])
            ways = [first["osm_way"]]
            length = first["length_m"]
            position = first_index

            changed = True
            while changed:
                changed = False
                for k, (other_index, other) in enumerate(remaining):
                    op = other["points"]
                    if near(points[-1], op[0]):
                        points = points + list(op[1:])
                    elif near(points[-1], op[-1]):
                        points = points + list(op[-2::-1])
                    elif near(points[0], op[-1]):
                        points = list(op[:-1]) + points
                    elif near(points[0], op[0]):
                        points = list(op[:0:-1]) + points
                    else:
                        continue
                    ways.append(other["osm_way"])
                    length += other["length_m"]
                    position = min(position, other_index)
                    remaining.pop(k)
                    changed = True
                    break

            if len(ways) == 1:
                positioned.append((first_index, first))
                continue

            merged = dict(first)
            merged["osm_ways"] = ways
            merged["points"] = points
            merged["length_m"] = round(length, 1)
            positioned.append((position, merged))

    positioned.sort(key=lambda pair: pair[0])

    return [item for _index, item in positioned]


def collect_stations(osm, selection, radius_m: float = 250.0, platform_radius_m: float = 400.0) -> dict:
    """
    Liest Bahnhoefe samt Bahnsteigen, Gebaeuden und Haltepositionen. Gibt ein Woerterbuch zurueck.

    Bahnsteige liegen bei grossen Bahnhoefen weit vom Bahnhofspunkt entfernt (Mitte eines 300-m-Bahnsteigs),
    deshalb gilt fuer sie platform_radius_m (der naechste Bahnhof gewinnt).
    """

    center_lat, center_lon = selection.center
    geometry = TPF2Geometry(center_lat, center_lon, selection.rotation_deg)
    half_w, half_h = selection.width_m / 2.0, selection.height_m / 2.0

    def local(node):
        x, y = geometry.convert(node.lat, node.lon)
        return round(float(x), 2), round(float(y), 2)

    def inside(point):
        return abs(point[0]) <= half_w and abs(point[1]) <= half_h

    def way_points(way):
        pts = []
        for node_id in way.nodes:
            node = osm.nodes.get(node_id)
            if node is not None:
                pts.append(local(node))
        return pts

    anchors: list[dict] = []
    platforms: list[dict] = []
    buildings: list[dict] = []
    stops: list[dict] = []

    # --- Knoten ---------------------------------------------------------------------------
    for node in osm.nodes.values():

        tags = _tags(node)

        if not tags:
            continue

        railway = tags.get("railway")
        transport = tags.get("public_transport")

        point = None

        if railway == STOP_RAILWAY:
            point = local(node)
            if inside(point):
                stops.append({
                    "osm_node": node.id, "name": tags.get("name", ""),
                    "x": point[0], "y": point[1], "tags": _pick(tags),
                })

        elif _station_kind(tags) is not None:
            kind, status = _station_kind(tags)
            point = local(node)
            if inside(point):
                anchors.append({
                    "osm_node": node.id,
                    "name": tags.get("name") or tags.get("ref") or "",
                    "kind": kind, "status": status,
                    "x": point[0], "y": point[1],
                    "lat": round(node.lat, 7), "lon": round(node.lon, 7),
                    "tags": _pick(tags),
                })

        elif railway == "platform":
            point = local(node)
            if inside(point):
                platforms.append({
                    "osm_node": node.id, "type": "point", "ref": tags.get("ref", ""),
                    "points": [point], "length_m": 0.0, "tags": _pick(tags),
                })

        elif transport == "stop_position" and any(tags.get(m) == "yes" for m in MODE_TAGS):
            point = local(node)
            if inside(point):
                stops.append({
                    "osm_node": node.id, "name": tags.get("name", ""),
                    "x": point[0], "y": point[1], "tags": _pick(tags),
                })

    # --- Wege und Flaechen ----------------------------------------------------------------
    for way in osm.ways.values():

        tags = _tags(way)

        if not tags:
            continue

        railway = tags.get("railway")
        transport = tags.get("public_transport")

        # Bushaltestellen (highway=platform + public_transport=platform + bus=yes) kommen ueber die Strassen-
        # Abfrage mit und sind keine Bahnsteige: Es zaehlt railway=platform oder ein Zug-/S-Bahn-/U-Bahn-/
        # Strassenbahn-Tag. Ebenso bei Bahnhofsflaechen und -gebaeuden (Busbahnhoefe).
        rail_mode = any(tags.get(mode) == "yes" for mode in MODE_TAGS)
        is_platform = railway in PLATFORM_WAYS or (transport == "platform" and rail_mode)
        is_station_area = railway == "station" or (transport == "station" and rail_mode)
        is_building = tags.get("building") in BUILDING_VALUES or (
            "building" in tags and (is_station_area or railway in ("station", "halt") or (
                tags.get("building") == "transportation" and rail_mode))
        )

        if not (is_platform or is_station_area or is_building):
            continue

        pts = way_points(way)

        if len(pts) < 2:
            continue

        closed = len(way.nodes) > 2 and way.nodes[0] == way.nodes[-1]

        if is_platform:
            if any(inside(p) for p in pts):
                length_m = round(_polyline_length(pts), 1)
                extra = {}

                # Geschlossene Bahnsteigflaeche: Laenge ist die lange Seite, nicht der Umfang.
                if closed and railway != "platform_edge" and len(pts) >= 4:
                    long_side, short_side = _polygon_extent(pts)
                    extra = {"perimeter_m": length_m, "width_m": round(short_side, 1), "closed": True}
                    length_m = round(long_side, 1)

                platforms.append({
                    "osm_way": way.id,
                    "type": "edge" if railway == "platform_edge" else "platform",
                    "ref": tags.get("ref", "") or tags.get("local_ref", ""),
                    "points": pts,
                    "length_m": length_m,
                    "tags": _pick(tags),
                    **extra,
                })

        if is_building and closed:
            area, centroid = _area_and_centroid(pts)
            if inside(centroid):
                buildings.append({
                    "osm_way": way.id, "name": tags.get("name", ""),
                    "points": pts, "area_m2": round(area, 1),
                    "x": round(centroid[0], 2), "y": round(centroid[1], 2),
                    "tags": _pick(tags),
                })

        if is_station_area and closed and not is_platform:
            area, centroid = _area_and_centroid(pts)
            if inside(centroid):
                anchors.append({
                    "osm_way": way.id,
                    "name": tags.get("name") or tags.get("ref") or "",
                    "kind": STATION_RAILWAY.get(railway, "station"),
                    "x": round(centroid[0], 2), "y": round(centroid[1], 2),
                    "area_m2": round(area, 1),
                    "tags": _pick(tags),
                    "from_area": True,
                })

    # --- Anker zusammenfassen: Knoten, Flaeche und Namensvarianten desselben Bahnhofs ------------------
    def norm(name: str) -> str:
        return "".join(ch for ch in name.lower() if ch.isalnum())

    anchors.sort(key=lambda a: (a.get("from_area", False), a["name"]))
    unique: list[dict] = []

    for anchor in anchors:
        twin = None
        for other in unique:
            d = math.hypot(other["x"] - anchor["x"], other["y"] - anchor["y"])
            if d > MERGE_M:
                continue
            same_name = norm(other["name"]) == norm(anchor["name"]) and norm(anchor["name"]) != ""
            if (same_name or not other["name"] or not anchor["name"]
                    or anchor.get("from_area") or other.get("from_area") or d < 40.0):
                twin = other
                break
        if twin is None:
            unique.append(anchor)
        else:
            if anchor.get("from_area") and "area_m2" not in twin:
                twin["area_m2"] = anchor.get("area_m2")
            if not twin["name"] and anchor["name"]:
                twin["name"] = anchor["name"]

    # --- Haltepositionen ohne Bahnhofspunkt: gleichnamige zu einem Bahnhof zusammenfassen ----------------
    def near_any_anchor(x, y):
        return any(math.hypot(a["x"] - x, a["y"] - y) <= radius_m for a in unique)

    loose = [st for st in stops if st["name"] and not near_any_anchor(st["x"], st["y"])]
    groups: dict[str, list[list[dict]]] = {}

    for st in loose:
        clusters = groups.setdefault(norm(st["name"]), [])
        for cluster in clusters:
            cx = sum(m["x"] for m in cluster) / len(cluster)
            cy = sum(m["y"] for m in cluster) / len(cluster)
            if math.hypot(cx - st["x"], cy - st["y"]) <= CLUSTER_M:
                cluster.append(st)
                break
        else:
            clusters.append([st])

    for clusters in groups.values():
        for cluster in clusters:
            unique.append({
                "name": cluster[0]["name"], "kind": "halt",
                "x": round(sum(m["x"] for m in cluster) / len(cluster), 2),
                "y": round(sum(m["y"] for m in cluster) / len(cluster), 2),
                "tags": dict(cluster[0]["tags"]), "from_stops": True,
            })

    stations = []

    for index, anchor in enumerate(unique, 1):
        anchor["id"] = index
        anchor["platforms"] = []
        anchor["buildings"] = []
        anchor["stop_positions"] = []
        stations.append(anchor)

    def nearest(x, y, limit):
        best, best_d = None, limit
        for station in stations:
            d = math.hypot(station["x"] - x, station["y"] - y)
            if d <= best_d:
                best, best_d = station, d
        return best

    unassigned = {"platforms": [], "buildings": [], "stop_positions": []}

    def attach(items, key, xy, limit):
        for item in items:
            x, y = xy(item)
            station = nearest(x, y, limit)
            if station is None:
                unassigned[key].append(item)
            else:
                station[key].append(item)

    def middle(item):
        pts = item["points"]
        return (sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts))

    platforms = merge_platform_ways(platforms)

    attach(platforms, "platforms", middle, platform_radius_m)
    attach(buildings, "buildings", lambda b: (b["x"], b["y"]), radius_m)
    attach(stops, "stop_positions", lambda s: (s["x"], s["y"]), radius_m)

    for station in stations:
        station["platform_count"] = len([p for p in station["platforms"] if p["type"] != "edge"])
        station["platform_length_m"] = round(
            sum(p["length_m"] for p in station["platforms"] if p["type"] != "edge"), 1)
        # Kein Bahnhof im Sinn der Bahn: Bergbahn, Mini-Eisenbahn, Touristikbahn oder weder Halteposition
        # noch Bahnsteig (Sommerrodelbahn, Aufzug)
        station["platform_edge_count"] = len([p for p in station["platforms"] if p["type"] == "edge"])
        station["platform_osm_ways"] = sum(
            len(p.get("osm_ways") or [p.get("osm_way")])
            for p in station["platforms"] if p["type"] != "edge" and (p.get("osm_way") or p.get("osm_ways"))
        )
        station["doubtful"] = bool(
            station["tags"].get("station") in ("funicular", "miniature", "monorail")
            or station["tags"].get("usage") == "tourism"
            or (not station["stop_positions"] and station["platform_count"] == 0)
        )

    return {
        "version": STATION_VERSION,
        "map": {"center_lat": center_lat, "center_lon": center_lon,
                "width_m": selection.width_m, "height_m": selection.height_m,
                "rotation_deg": selection.rotation_deg},
        "radius_m": radius_m,
        "stations": stations,
        "unassigned": unassigned,
    }


def summary(data: dict) -> str:
    stations = data["stations"]
    kinds: dict[str, int] = {}
    for s in stations:
        kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
    parts = ", ".join(f"{n} {kind}" for kind, n in sorted(kinds.items()))
    platforms = sum(len(s["platforms"]) for s in stations)
    buildings = sum(len(s["buildings"]) for s in stations)
    loose = sum(len(v) for v in data["unassigned"].values())
    return (
        f"{len(stations)} Bahnhöfe/Haltepunkte ({parts or 'keine'}), {platforms} Bahnsteige, "
        f"{buildings} Gebäude, {sum(len(s['stop_positions']) for s in stations)} Haltepositionen; "
        f"{loose} Objekte ohne Bahnhof in {data['radius_m']:.0f} m."
    )


def write_stations(data: dict, path: str | Path) -> tuple[Path, Path]:
    """Schreibt <name>.json (alles) und <name>.csv (eine Zeile je Bahnhof, Trennzeichen Semikolon)."""

    json_path = Path(path).with_suffix(".json")
    csv_path = json_path.with_suffix(".csv")

    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(["id", "name", "art", "x_m", "y_m", "bahnsteige", "bahnsteiglaenge_m", "gebaeude",
                         "haltepositionen", "gleise_laut_osm", "betreiber", "osm", "bahnart", "nutzung",
                         "aus_haltepositionen", "zweifelhaft", "bahnsteigkanten", "status"])
        for s in data["stations"]:
            writer.writerow([
                s["id"], s["name"], s["kind"], s["x"], s["y"], s["platform_count"], s["platform_length_m"],
                len(s["buildings"]), len(s["stop_positions"]), s["tags"].get("tracks", ""),
                s["tags"].get("operator", ""), s.get("osm_node") or s.get("osm_way") or "",
                s["tags"].get("station", ""), s["tags"].get("usage", ""),
                "ja" if s.get("from_stops") else "",
                "ja" if s.get("doubtful") else "",
                s.get("platform_edge_count", 0),
                s.get("status", ""),
            ])

    return json_path, csv_path
