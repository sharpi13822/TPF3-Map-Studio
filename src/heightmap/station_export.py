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

STATION_RAILWAY = {"station": "station", "halt": "halt", "stop": "stop", "tram_stop": "tram_stop"}
PLATFORM_WAYS = {"platform", "platform_edge"}
BUILDING_VALUES = {"train_station", "transportation"}
MODE_TAGS = ("train", "light_rail", "subway", "tram")

KEEP_TAGS = (
    "name", "alt_name", "short_name", "ref", "uic_ref", "ref:IBNR", "operator", "network", "wikidata",
    "railway", "public_transport", "train", "light_rail", "subway", "tram", "station", "usage",
    "level", "layer", "tracks", "platforms", "wheelchair", "building", "height", "width", "length",
    "local_ref", "railway:ref", "ele",
)


def _tags(obj) -> dict:
    return getattr(obj, "tags", None) or {}


def _pick(tags: dict) -> dict:
    return {key: tags[key] for key in KEEP_TAGS if key in tags}


def _polyline_length(points: list) -> float:
    return sum(math.hypot(b[0] - a[0], b[1] - a[1]) for a, b in zip(points, points[1:]))


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


def collect_stations(osm, selection, radius_m: float = 250.0) -> dict:
    """Liest Bahnhoefe samt Bahnsteigen, Gebaeuden und Haltepositionen. Gibt ein Woerterbuch zurueck."""

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

        if railway in STATION_RAILWAY or (transport == "station" and tags.get("train") == "yes"):
            point = local(node)
            if inside(point):
                anchors.append({
                    "osm_node": node.id,
                    "name": tags.get("name") or tags.get("ref") or "",
                    "kind": STATION_RAILWAY.get(railway, "station"),
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

        is_platform = railway in PLATFORM_WAYS or transport == "platform"
        is_station_area = railway == "station" or transport == "station"
        is_building = tags.get("building") in BUILDING_VALUES or (
            "building" in tags and (is_station_area or tags.get("railway") == "station")
        )

        if not (is_platform or is_station_area or is_building):
            continue

        pts = way_points(way)

        if len(pts) < 2:
            continue

        closed = len(way.nodes) > 2 and way.nodes[0] == way.nodes[-1]

        if is_platform:
            if any(inside(p) for p in pts):
                platforms.append({
                    "osm_way": way.id,
                    "type": "edge" if railway == "platform_edge" else "platform",
                    "ref": tags.get("ref", "") or tags.get("local_ref", ""),
                    "points": pts,
                    "length_m": round(_polyline_length(pts), 1),
                    "tags": _pick(tags),
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

    # --- doppelte Anker (Knoten UND Flaeche desselben Bahnhofs) zusammenfassen ----------------
    anchors.sort(key=lambda a: (a.get("from_area", False), a["name"]))
    unique: list[dict] = []

    for anchor in anchors:
        twin = next((u for u in unique if math.hypot(u["x"] - anchor["x"], u["y"] - anchor["y"]) < 60.0
                     and (not u["name"] or not anchor["name"] or u["name"] == anchor["name"])), None)
        if twin is None:
            unique.append(anchor)
        elif anchor.get("from_area") and "area_m2" not in twin:
            twin["area_m2"] = anchor.get("area_m2")

    stations = []

    for index, anchor in enumerate(unique, 1):
        anchor["id"] = index
        anchor["platforms"] = []
        anchor["buildings"] = []
        anchor["stop_positions"] = []
        stations.append(anchor)

    def nearest(x, y):
        best, best_d = None, radius_m
        for station in stations:
            d = math.hypot(station["x"] - x, station["y"] - y)
            if d <= best_d:
                best, best_d = station, d
        return best

    unassigned = {"platforms": [], "buildings": [], "stop_positions": []}

    def attach(items, key, xy):
        for item in items:
            x, y = xy(item)
            station = nearest(x, y)
            if station is None:
                unassigned[key].append(item)
            else:
                station[key].append(item)

    attach(platforms, "platforms", lambda p: p["points"][len(p["points"]) // 2])
    attach(buildings, "buildings", lambda b: (b["x"], b["y"]))
    attach(stops, "stop_positions", lambda s: (s["x"], s["y"]))

    for station in stations:
        station["platform_count"] = len([p for p in station["platforms"] if p["type"] != "edge"])
        station["platform_length_m"] = round(
            sum(p["length_m"] for p in station["platforms"] if p["type"] != "edge"), 1)

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
                         "haltepositionen", "gleise_laut_osm", "betreiber", "osm"])
        for s in data["stations"]:
            writer.writerow([
                s["id"], s["name"], s["kind"], s["x"], s["y"], s["platform_count"], s["platform_length_m"],
                len(s["buildings"]), len(s["stop_positions"]), s["tags"].get("tracks", ""),
                s["tags"].get("operator", ""), s.get("osm_node") or s.get("osm_way") or "",
            ])

    return json_path, csv_path
