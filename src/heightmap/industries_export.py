"""
Industrien aus OSM fuer TPF3 (Datei im Ordner towns_industries, Lua).

Format (aus einem Export des Spiels, industrien_test1.lua, 01.10.2026):

    { angle = 0.938, fileName = "::/industries/farm/farm.con",
      onWater = false, position = { x = -4636, y = 5072 }, tag = "farm" }

Position in Metern ab Kartenmitte, x nach Osten, y nach Norden (wie bei den
Staedten). Bestaetigt (Test im Spiel, 01.10.2026): Das Spiel nimmt alle
Industrien der gemaessigten Zone mit Dateinamen "::/industries/<tag>/<tag>.con"
an, wobei <tag> dem Icon-Namen im Wiki entspricht (gamemanual:simulation:
industriescargos): farm, livestock_farm, forest, saw_mill, bricks_works,
clay_pit, oil_platform (auf Wasser), oil_refinery, fishing_grounds (auf
Wasser), quarry, coal_mine, iron_ore_mine, sand_pit, oil_well, cotton_farm,
steel_mill, machine_factory, tool_factory, vehicle_factory, glass_works,
brewery, food_factory, furniture_factory, chemical_plant, textile_factory,
weaving_mill. Bei Kartenbeginn sind im Spiel nur einige vorhanden, die
uebrigen entstehen bei steigender Nachfrage.

NICHT geprueft: ob das Spiel jede Position annimmt (Hang, Waldrand,
Wasser) und was der Winkel genau bewirkt (hier immer 0). Die Zuordnung
"OSM-Objekt -> Industrie" ist ein Vorschlag.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from src.tpf2.tpf2_geometry import TPF2Geometry


@dataclass(frozen=True)
class IndustryRule:
    key: str            # Schluessel und tag im Spiel, z. B. "farm"
    label: str          # Anzeigename im Dialog
    on_water: bool
    default_on: bool
    needs_area: bool    # nur grosse Flaechen (Mindestgroesse)


RULES: tuple[IndustryRule, ...] = (
    IndustryRule("farm", "Farm (landuse=farmyard)", False, True, False),
    IndustryRule(
        "livestock_farm", "Viehzucht (building=cowshed/stable/sty)",
        False, True, False,
    ),
    IndustryRule("forest", "Forst (große Waldflächen)", False, False, True),
    IndustryRule("saw_mill", "Sägewerk", False, True, False),
    IndustryRule("bricks_works", "Ziegelei", False, True, False),
    IndustryRule("clay_pit", "Lehmgrube (quarry + resource=clay)", False, False, False),
    IndustryRule("quarry", "Steinbruch (landuse=quarry)", False, False, False),
    IndustryRule("sand_pit", "Sandgrube (quarry + sand/gravel)", False, False, False),
    IndustryRule("coal_mine", "Kohlemine (resource=coal)", False, False, False),
    IndustryRule("iron_ore_mine", "Eisenerzmine (resource=iron_ore)", False, False, False),
    IndustryRule("oil_well", "Ölquelle (man_made=petroleum_well)", False, True, False),
    IndustryRule("oil_platform", "Ölplattform (offshore_platform)", True, True, False),
    IndustryRule("oil_refinery", "Raffinerie", False, True, False),
    IndustryRule("steel_mill", "Stahlwerk", False, True, False),
    IndustryRule("machine_factory", "Maschinenfabrik", False, True, False),
    IndustryRule("tool_factory", "Werkzeugfabrik", False, True, False),
    IndustryRule("vehicle_factory", "Fahrzeugfabrik", False, True, False),
    IndustryRule("glass_works", "Glashütte", False, True, False),
    IndustryRule("brewery", "Brauerei", False, True, False),
    IndustryRule("food_factory", "Konservenfabrik / Lebensmittel", False, True, False),
    IndustryRule("furniture_factory", "Möbelfabrik", False, True, False),
    IndustryRule("chemical_plant", "Chemiewerk", False, True, False),
    IndustryRule("textile_factory", "Textilfabrik", False, True, False),
)

RULE_KEYS = tuple(rule.key for rule in RULES)

# OSM-Wert -> Industrie. Vorschlag, die genauen OSM-Tags der Fabriken sind
# uneinheitlich; treffen kann es nur, was in OSM so eingetragen ist.
INDUSTRIAL_MAP = {
    "sawmill": "saw_mill",
    "brickworks": "bricks_works",
    "oil": "oil_refinery",
    "refinery": "oil_refinery",
    "steel": "steel_mill",
    "steelmaking": "steel_mill",
    "steel_mill": "steel_mill",
    "metal_production": "steel_mill",
    "machine_shop": "machine_factory",
    "machinery": "machine_factory",
    "tool": "tool_factory",
    "automotive": "vehicle_factory",
    "brewery": "brewery",
    "glass": "glass_works",
    "glassworks": "glass_works",
    "chemical": "chemical_plant",
    "chemicals": "chemical_plant",
    "textile": "textile_factory",
    "furniture": "furniture_factory",
    "food": "food_factory",
    "food_production": "food_factory",
    "food_processing": "food_factory",
}

CRAFT_MAP = {
    "sawmill": "saw_mill",
    "brickmaker": "bricks_works",
    "brewery": "brewery",
}

MAN_MADE_MAP = {
    "offshore_platform": "oil_platform",
    "petroleum_well": "oil_well",
}

# man_made=works mit product=...
PRODUCT_MAP = {
    "steel": "steel_mill",
    "glass": "glass_works",
    "cars": "vehicle_factory",
    "car": "vehicle_factory",
    "vehicles": "vehicle_factory",
    "machinery": "machine_factory",
    "machines": "machine_factory",
    "tools": "tool_factory",
    "beer": "brewery",
    "chemicals": "chemical_plant",
    "bricks": "bricks_works",
    "furniture": "furniture_factory",
    "food": "food_factory",
    "textiles": "textile_factory",
    "clothes": "textile_factory",
}

# Rohstoff in landuse=quarry / industrial=mine -> Industrie
RESOURCE_MAP = {
    "coal": "coal_mine",
    "lignite": "coal_mine",
    "iron_ore": "iron_ore_mine",
    "iron": "iron_ore_mine",
    "clay": "clay_pit",
    "sand": "sand_pit",
    "gravel": "sand_pit",
}


def rules_matching(tags: dict | None) -> list[str]:
    """Schluessel aller Industrie-Arten, auf die die OSM-Tags passen."""

    if not tags:
        return []

    hits: list[str] = []

    def add(key):
        if key and key not in hits:
            hits.append(key)

    if tags.get("landuse") == "farmyard":
        add("farm")

    if tags.get("building") in ("cowshed", "stable", "sty"):
        add("livestock_farm")

    if tags.get("landuse") == "forest":
        add("forest")

    add(INDUSTRIAL_MAP.get(tags.get("industrial")))
    add(CRAFT_MAP.get(tags.get("craft")))
    add(MAN_MADE_MAP.get(tags.get("man_made")))

    if tags.get("man_made") == "works":
        for product in str(tags.get("product", "")).split(";"):
            add(PRODUCT_MAP.get(product.strip()))

    # Steinbrueche und Minen: nach Rohstoff
    if (
        tags.get("landuse") == "quarry"
        or tags.get("industrial") in ("mine", "mining", "quarry")
        or tags.get("man_made") == "mineshaft"
    ):
        resources = [
            r.strip() for r in str(tags.get("resource", "")).split(";") if r
        ]

        mapped = [RESOURCE_MAP[r] for r in resources if r in RESOURCE_MAP]

        if mapped:
            for key in mapped:
                add(key)
        elif tags.get("landuse") == "quarry":
            add("quarry")

    return hits


class Terrain:
    """
    Hoehenraster (Meter) und optional Wassermaske, wie sie exportiert werden,
    um Industrien auf Haengen und am Wasser auszusortieren. Zeile 0 ist
    Norden, Spalte 0 Westen (wie beim Hoehenraster).
    """

    def __init__(self, heights, water, width_m: float, height_m: float):
        self.heights = np.asarray(heights, dtype=np.float32)
        self.water = None if water is None else np.asarray(water, dtype=bool)
        self.width_m = float(width_m)
        self.height_m = float(height_m)
        self.h_px, self.w_px = self.heights.shape

    def _pixel(self, x: float, y: float) -> tuple[float, float]:

        col = (x + self.width_m / 2) / self.width_m * (self.w_px - 1)
        row = (self.height_m / 2 - y) / self.height_m * (self.h_px - 1)

        return row, col

    def _window(self, x: float, y: float, radius_m: float):

        row, col = self._pixel(x, y)

        pixel_m = self.width_m / (self.w_px - 1)
        radius_px = max(1, int(round(radius_m / pixel_m)))

        r0 = max(0, int(round(row)) - radius_px)
        r1 = min(self.h_px, int(round(row)) + radius_px + 1)
        c0 = max(0, int(round(col)) - radius_px)
        c1 = min(self.w_px, int(round(col)) + radius_px + 1)

        return r0, r1, c0, c1

    def relief_at(self, x: float, y: float, radius_m: float) -> float:
        """Hoechster minus tiefster Punkt im Umkreis (Meter)."""

        r0, r1, c0, c1 = self._window(x, y, radius_m)

        if r1 <= r0 or c1 <= c0:
            return 0.0

        window = self.heights[r0:r1, c0:c1]

        return float(window.max() - window.min())

    def water_near(self, x: float, y: float, radius_m: float) -> bool:
        """Liegt im Umkreis Wasser (Wassermaske)?"""

        if self.water is None:
            return False

        r0, r1, c0, c1 = self._window(x, y, radius_m)

        if r1 <= r0 or c1 <= c0:
            return False

        return bool(self.water[r0:r1, c0:c1].any())


@dataclass
class Industry:
    key: str
    label: str
    name: str
    x: float
    y: float
    on_water: bool
    area_ha: float = 0.0


def _ring_area_m2(points: list[tuple[float, float]]) -> float:

    total = 0.0

    for index in range(len(points)):
        x1, y1 = points[index]
        x2, y2 = points[(index + 1) % len(points)]
        total += x1 * y2 - x2 * y1

    return abs(total) / 2.0


def collect_industries(
    osm,
    selection,
    enabled: tuple[str, ...] | list[str] = RULE_KEYS,
    min_forest_ha: float = 200.0,
    min_distance_m: float = 800.0,
    max_per_type: int = 20,
    terrain: "Terrain | None" = None,
    max_relief_m: float = 15.0,
    relief_radius_m: float = 150.0,
    water_clear_m: float = 150.0,
    edge_margin_m: float = 500.0,
) -> list[Industry]:
    """
    Sucht passende OSM-Objekte (Knoten und Wege) im Auswahlrechteck. Eine
    Flaeche zaehlt mit ihrem Schwerpunkt. Je Art bleiben nur Objekte mit
    Mindestabstand, die groessten zuerst, hoechstens max_per_type.
    """

    center_lat, center_lon = selection.center
    geometry = TPF2Geometry(center_lat, center_lon, selection.rotation_deg)

    half_w = selection.width_m / 2
    half_h = selection.height_m / 2

    enabled = set(enabled)
    rules = {rule.key: rule for rule in RULES}

    found: dict[str, list[Industry]] = {key: [] for key in enabled}

    def consider(tags, x, y, area_ha, name_fallback):

        # Abstand zum Kartenrand: Felder, Hecken und Gruben einer Industrie
        # reichen mehrere hundert Meter ueber ihre Mitte hinaus und wuerden
        # sonst ueber den Kartenrand ins Leere ragen.
        if abs(x) > half_w - edge_margin_m or abs(y) > half_h - edge_margin_m:
            return

        for key in rules_matching(tags):

            if key not in enabled:
                continue

            rule = rules[key]

            if rule.needs_area and area_ha < min_forest_ha:
                continue

            # Nur flaches Gelaende abseits vom Wasser (sonst schneidet das
            # Spiel die Industrie in den Hang, siehe Steinbrueche am Rhein).
            if terrain is not None and not rule.on_water:

                if (
                    max_relief_m > 0
                    and terrain.relief_at(x, y, relief_radius_m)
                    > max_relief_m
                ):
                    continue

                if water_clear_m > 0 and terrain.water_near(
                    x, y, water_clear_m
                ):
                    continue

            name = tags.get("name") or name_fallback

            found[key].append(
                Industry(
                    key=key,
                    label=rule.label,
                    name=str(name),
                    x=float(x),
                    y=float(y),
                    on_water=rule.on_water,
                    area_ha=area_ha,
                )
            )

    # Knoten
    for node in osm.nodes.values():

        tags = getattr(node, "tags", None)

        if not tags:
            continue

        x, y = geometry.convert(node.lat, node.lon)

        consider(tags, x, y, 0.0, "OSM-Knoten")

    # Wege (Schwerpunkt der Eckpunkte, Flaeche bei geschlossenen Wegen)
    for way in osm.ways.values():

        tags = getattr(way, "tags", None)

        if not tags or not rules_matching(tags):
            continue

        points = []

        for node_id in way.nodes:
            node = osm.nodes.get(node_id)
            if node is not None:
                points.append(geometry.convert(node.lat, node.lon))

        if len(points) < 3:
            continue

        closed = way.nodes[0] == way.nodes[-1]

        ring = points[:-1] if closed else points

        x = sum(p[0] for p in ring) / len(ring)
        y = sum(p[1] for p in ring) / len(ring)

        area_ha = _ring_area_m2(ring) / 10_000.0 if closed else 0.0

        consider(tags, x, y, area_ha, "OSM-Weg")

    result: list[Industry] = []

    for key in RULE_KEYS:

        items = found.get(key, [])

        items.sort(key=lambda i: (-i.area_ha, i.name))

        chosen: list[Industry] = []

        for item in items:

            if len(chosen) >= max_per_type:
                break

            if any(
                math.hypot(item.x - other.x, item.y - other.y)
                < min_distance_m
                for other in chosen
            ):
                continue

            chosen.append(item)

        result.extend(chosen)

    return result


def industries_lua(industries: list[Industry]) -> str:
    """Inhalt der Lua-Datei: nur Industrien, keine Staedte."""

    lines = [
        "function data()",
        "return {",
        "  industries = {",
    ]

    for item in industries:
        lines.append(
            f'    {{ angle = 0.0, '
            f'fileName = "::/industries/{item.key}/{item.key}.con",'
        )
        lines.append(
            f"      onWater = {'true' if item.on_water else 'false'}, "
            f"position = {{ x = {item.x:.0f}, y = {item.y:.0f} }}, "
            f'tag = "{item.key}" }},'
        )

    lines += ["  },", "  towns = {", "  }", "}", "end", ""]

    return "\n".join(lines)


def write_industries_lua(path: str | Path, industries: list[Industry]) -> Path:

    path = Path(path)

    path.write_text(industries_lua(industries), encoding="utf-8")

    return path
