"""
Staedte aus OSM fuer TPF3 (Datei im Ordner towns_industries, Lua).

Gesichert (Test im Spiel am 01.10.2026, Testdatei tpf3_test_ursprung.lua):
- Das Spiel nimmt das Format aus docs/TPF3_UMBAU.md an und zaehlt die Staedte.
- Der Koordinatenursprung ist die KARTENMITTE, x zeigt nach Osten, y nach
  Norden (Einheit Meter). Das ist dieselbe Konvention wie TPF2Geometry.

Einwohner (Tests im Spiel, 01.10.2026, alle anderen Faktoren auf 1.0):
- Die MITTLERE Zahl von sizeFactors skaliert die Anfangs-Einwohner. Faktor 1
  gibt etwa 100 Einwohner, 3 -> 298, 5 -> 500, 10 -> 999, 30 -> 2892.
- Auch Faktoren unter 1 gehen (Test 01.10.2026): 0.2 -> 19, 0.5 -> 50,
  0.8 -> 79, 1.0 -> 98 Einwohner, also etwa 98 Einwohner je Faktor.
- Faktor 100 ergab nur 4476 (nicht 10000): ab etwa dieser Groesse greift
  offenbar eine Obergrenze. Darum begrenzt der Export den Faktor (Standard 30,
  getesteter Wert).
- Die erste und dritte Zahl veraendern die Einwohner nicht (Wirkung unbekannt,
  bleiben bei 1.0).

NICHT geprueft: was die erste und dritte Zahl von sizeFactors und
landUse2CargoNeedsCategories im Spiel bewirken. Dafuer stehen die Werte aus
der Beispieldatei (Faktor 1.0 und die Frachtbeduerfnisse).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.tpf2.tpf2_geometry import TPF2Geometry

# OSM-Wert des Tags "place" -> Anzeigename
PLACE_KINDS = {
    "city": "Grossstadt (city)",
    "town": "Stadt (town)",
    "village": "Dorf (village)",
    "hamlet": "Weiler (hamlet)",
}

DEFAULT_KINDS = ("city", "town", "village")

# Aus der Beispieldatei im Umbauplan, Bedeutung fuer die Spielmechanik offen.
DEFAULT_NEEDS = '{ com = { { "fish", 1 } }, ind = { { "machines", 0.5 } } }'

# Im Spiel entspricht der mittlere Faktor 1 etwa 100 Einwohnern (linear bis 30).
INHABITANTS_PER_FACTOR = 100.0

# Hoechster Faktor (getestet: 30 -> 2892 Einwohner, 100 -> nur 4476).
DEFAULT_MAX_FACTOR = 30.0

# Kleinster Faktor (getestet: 0.2 -> 19 Einwohner; darunter ungetestet).
DEFAULT_MIN_FACTOR = 0.2

# Faktor = Massstab * Wurzel(OSM-Einwohner): grosse Staedte starten groesser,
# aber nicht proportional (Koblenz 110 643 -> ca. 10, ein Dorf mit 300 -> ca. 0,5).
DEFAULT_SCALE = 0.03

# Schaetzwert, wenn OSM keine Einwohnerzahl hat (nicht im Spiel geprueft).
FALLBACK_FACTOR = {"city": 10.0, "town": 4.0, "village": 0.5, "hamlet": 0.2}


@dataclass
class Place:
    name: str
    kind: str
    x: float
    y: float
    population: int = 0


def _parse_population(value) -> int:

    if value is None:
        return 0

    digits = "".join(ch for ch in str(value) if ch.isdigit())

    return int(digits) if digits else 0


def size_factor(
    place: "Place",
    max_factor: float = DEFAULT_MAX_FACTOR,
    use_population: bool = True,
    scale: float = DEFAULT_SCALE,
    min_factor: float = DEFAULT_MIN_FACTOR,
) -> float:
    """
    Mittlerer sizeFactors-Wert (steuert die Anfangs-Einwohner) fuer einen Ort:
    Massstab * Wurzel(Einwohner), begrenzt auf min_factor .. max_factor.
    """

    if not use_population:
        return 1.0

    if place.population > 0:
        factor = float(scale) * (place.population ** 0.5)
    else:
        factor = FALLBACK_FACTOR.get(place.kind, 1.0)

    return round(max(float(min_factor), min(factor, float(max_factor))), 2)


def collect_places(
    osm,
    selection,
    kinds=DEFAULT_KINDS,
    min_population: int = 0,
) -> list[Place]:
    """
    Sucht Orte (Knoten mit place=city/town/village/hamlet und Namen) im
    Auswahlrechteck und rechnet sie in Meter ab der Kartenmitte um.
    Gibt eine leere Liste zurueck, wenn die geladenen OSM-Daten keine
    Orts-Knoten enthalten.
    """

    center_lat, center_lon = selection.center
    geometry = TPF2Geometry(center_lat, center_lon, selection.rotation_deg)

    half_w = selection.width_m / 2
    half_h = selection.height_m / 2

    wanted = set(kinds)

    places: list[Place] = []

    for node in osm.nodes.values():

        tags = getattr(node, "tags", None) or {}

        kind = tags.get("place")

        if kind not in wanted:
            continue

        name = tags.get("name") or tags.get("name:de")

        if not name:
            continue

        population = _parse_population(tags.get("population"))

        if population < min_population:
            continue

        x, y = geometry.convert(node.lat, node.lon)

        if abs(x) > half_w or abs(y) > half_h:
            continue

        places.append(
            Place(
                name=str(name),
                kind=kind,
                x=float(x),
                y=float(y),
                population=population,
            )
        )

    # Groesste zuerst (bei gleicher Einwohnerzahl nach Name sortiert).
    places.sort(key=lambda p: (-p.population, p.name))

    return places


def _lua_string(text: str) -> str:

    escaped = (
        text.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", " ")
        .replace("\n", " ")
    )

    return f'"{escaped}"'


def towns_lua(
    places: list[Place],
    max_factor: float = DEFAULT_MAX_FACTOR,
    use_population: bool = True,
    scale: float = DEFAULT_SCALE,
    min_factor: float = DEFAULT_MIN_FACTOR,
) -> str:
    """Baut den Inhalt der Lua-Datei (Staedte, keine Industrien)."""

    lines = [
        "function data()",
        "return {",
        "  industries = {",
        "  },",
        "  towns = {",
    ]

    for place in places:
        lines.append(
            f"    {{ landUse2CargoNeedsCategories = {DEFAULT_NEEDS},"
        )
        lines.append(
            f"      name = {_lua_string(place.name)}, "
            f"position = {{ x = {place.x:.2f}, y = {place.y:.2f} }},"
        )
        middle = size_factor(
            place, max_factor, use_population, scale, min_factor
        )

        lines.append(
            f"      sizeFactors = {{ 1.00, {middle:.2f}, 1.00 }} }},"
        )

    lines += ["  }", "}", "end", ""]

    return "\n".join(lines)


def write_towns_lua(
    path: str | Path,
    places: list[Place],
    max_factor: float = DEFAULT_MAX_FACTOR,
    use_population: bool = True,
    scale: float = DEFAULT_SCALE,
    min_factor: float = DEFAULT_MIN_FACTOR,
) -> Path:

    path = Path(path)

    path.write_text(
        towns_lua(places, max_factor, use_population, scale, min_factor),
        encoding="utf-8",
    )

    return path
