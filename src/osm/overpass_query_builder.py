"""
Overpass-Abfrage-Baukasten.

Baut die Overpass-QL-Abfrage aus einzelnen, togglebaren Kategorien statt
wie bisher komplett fest verdrahtet (siehe OverpassClient._build_query).
Mit allen Kategorien auf ihrem Standardwert entspricht das Ergebnis genau
der bisherigen, fest verdrahteten Abfrage - bestehendes Verhalten bleibt
also unveraendert, wenn niemand etwas umstellt.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

from src.map.objects.selection import Selection


TEMPLATES_PATH = Path.home() / ".tpf2_map_studio" / "overpass_templates.json"

LANDUSE_VALUES = (
    "farmland|farmyard|grass|meadow|orchard|vineyard|"
    "plant_nursery|greenhouse_horticulture|forest|reservoir"
)
WATER_VALUES = "lake|pond|reservoir|basin"
PLACE_VALUES = "city|town|village|hamlet"

# Zusaetzliche Flaechen fuer die Biome-Maske aus OSM (Siedlung, Heide, Moor,
# Fels, Sand). Nur geschlossene Flaechen werden in der Maske verwendet.
BIOME_LANDUSE_VALUES = (
    "residential|industrial|commercial|retail|quarry|brownfield|"
    "construction|village_green|recreation_ground|greenfield|allotments|"
    "marsh"
)
BIOME_NATURAL_VALUES = (
    "heath|scrub|wetland|grassland|fell|bare_rock|scree|sand|shingle|beach"
)
BIOME_LEISURE_VALUES = "pitch|golf_course"

# Objekte fuer "Industrien aus OSM" (Saegewerk, Ziegelei, Raffinerie,
# Oelplattform). Hoefe (landuse=farmyard) kommen ueber "Flaechennutzung",
# Steinbrueche ueber die Biome-Flaechen, Waelder ueber "Vegetation".
INDUSTRY_INDUSTRIAL_VALUES = (
    "sawmill|brickworks|oil|refinery|steel|steelmaking|steel_mill|"
    "metal_production|machine_shop|machinery|tool|automotive|brewery|glass|"
    "glassworks|chemical|chemicals|textile|furniture|food|food_production|"
    "food_processing|mine|mining|quarry"
)
INDUSTRY_CRAFT_VALUES = "sawmill|brickmaker|brewery"
INDUSTRY_MAN_MADE_VALUES = (
    "offshore_platform|petroleum_well|works|mineshaft"
)

# Objekte fuer "Bahnhoefe aus OSM" (Bahnhoefe, Haltepunkte, Bahnsteige,
# Bahnhofsgebaeude, Haltepositionen). Die Bahnhofspunkte (railway=station/halt)
# sind in OSM meist einzelne Knoten ohne Weg und kamen bisher nicht mit.
STATION_RAILWAY_VALUES = "station|halt|stop|tram_stop"
STATION_WAY_RAILWAY_VALUES = "station|halt|platform|platform_edge"
STATION_BUILDING_VALUES = "train_station|transportation"
STATION_MODES = ("train", "light_rail", "subway", "tram")
# Betriebsbahnhoefe, stillgelegte und im Bau befindliche Bahnhoefe (OSM-Lebenszyklus-Tags), zum Beispiel
# Ruedesheim 2026: railway=service_station + disused:public_transport=station.
STATION_LIFECYCLE_LINES = (
    'node["railway"="service_station"]',
    'node["disused:railway"~"^(station|halt)$"]',
    'node["disused:public_transport"="station"]',
    'node["construction:railway"~"^(station|halt)$"]',
    'node["railway"="construction"]["construction"~"^(station|halt)$"]',
)


@dataclass
class OverpassQueryConfig:
    """
    Eine Kategorie = ein Haekchen im Overpass-Baukasten-Dialog.

    include_tram wirkt nur, wenn railways=True: bei include_tram=False
    werden Strassenbahngleise (railway=tram) aus der Gleis-Abfrage
    ausgeschlossen statt mitgeliefert.
    """

    railways: bool = True
    include_tram: bool = True
    highways: bool = True
    buildings: bool = True
    parks: bool = True
    landuse: bool = True
    vegetation: bool = True
    water: bool = True
    # Orte (Staedte, Doerfer): jetzt standardmaessig AN, damit der Export
    # "Staedte aus OSM" ohne Handarbeit Orte findet.
    places: bool = True
    # Siedlungs-, Heide-, Moor- und Felsflaechen fuer die Biome-Maske aus OSM.
    # Standardmaessig AN, macht den OSM-Download aber groesser.
    biome_areas: bool = True
    # Objekte fuer die Industrien-Erzeugung aus OSM (klein, wenige Treffer).
    industry: bool = True
    # Bahnhoefe, Haltepunkte, Bahnsteige und Bahnhofsgebaeude fuer
    # "Bahnhoefe aus OSM" (wenige zusaetzliche Objekte, auch wenn
    # railways/buildings ausgeschaltet sind).
    stations: bool = True

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "OverpassQueryConfig":

        known_fields = {f for f in cls.__dataclass_fields__}

        filtered = {
            key: value
            for key, value in data.items()
            if key in known_fields
        }

        return cls(**filtered)


def build_query(
    selection: Selection,
    config: OverpassQueryConfig | None = None,
) -> str:
    """
    Baut die Overpass-QL-Abfrage passend zu den aktivierten Kategorien.
    """

    if config is None:
        config = OverpassQueryConfig()

    # Bei einer gedrehten Auswahl ist min_lat/min_lon/max_lat/max_lon
    # bewusst die groessere, umschliessende Bounding Box (siehe
    # Selection-Klasse) - fuer die eigentliche Overpass-Abfrage brauchen
    # wir hier aber die TATSAECHLICHE gedrehte Flaeche, sonst wuerden
    # OSM-Daten fuer den viel groesseren, nicht gedrehten Umkreis
    # geladen statt nur fuer das gedrehte Kartenband selbst. Overpass
    # unterstuetzt dafuer den poly:-Filter (beliebiges Polygon) als
    # Alternative zur rechteckigen bbox.
    if selection.is_rotated:

        corner_pairs = " ".join(
            f"{lat} {lon}"
            for lat, lon in selection.corners_latlon()
        )

        bbox = f'poly:"{corner_pairs}"'

    else:

        bbox = (
            f"{selection.min_lat},{selection.min_lon},"
            f"{selection.max_lat},{selection.max_lon}"
        )

    lines: list[str] = []

    if config.highways:
        lines.append(f'  way["highway"]({bbox});')

    if config.buildings:
        lines.append(f'  way["building"]({bbox});')

    if config.railways:

        if config.include_tram:
            lines.append(f'  way["railway"]({bbox});')
        else:
            lines.append(f'  way["railway"]["railway"!="tram"]({bbox});')

    if config.parks:
        lines.append(f'  way["leisure"~"^(park|garden)$"]({bbox});')

    if config.landuse:
        lines.append(f'  way["landuse"~"^({LANDUSE_VALUES})$"]({bbox});')

    if config.vegetation and config.water:
        # Historisch ein gemeinsamer Filter (natural=wood/tree_row/water) -
        # bei getrennten Toggles wird er entsprechend aufgespalten.
        lines.append(f'  way["natural"~"^(wood|tree_row|water)$"]({bbox});')
    elif config.vegetation:
        lines.append(f'  way["natural"~"^(wood|tree_row)$"]({bbox});')
    elif config.water:
        lines.append(f'  way["natural"="water"]({bbox});')

    if config.water:
        lines.append(f'  way["water"~"^({WATER_VALUES})$"]({bbox});')
        lines.append(f'  way["waterway"]({bbox});')
        lines.append(
            f'  relation["type"="multipolygon"]["natural"="water"]({bbox});'
        )
        lines.append(
            f'  relation["type"="multipolygon"]["water"~"^({WATER_VALUES})$"]({bbox});'
        )
        lines.append(
            f'  relation["type"="multipolygon"]["landuse"="reservoir"]({bbox});'
        )

    if config.vegetation:
        lines.append(f'  relation["natural"="wood"]({bbox});')
        lines.append(f'  relation["landuse"="forest"]({bbox});')

    if config.biome_areas:
        lines.append(
            f'  way["landuse"~"^({BIOME_LANDUSE_VALUES})$"]({bbox});'
        )
        lines.append(
            f'  way["natural"~"^({BIOME_NATURAL_VALUES})$"]({bbox});'
        )
        lines.append(
            f'  way["leisure"~"^({BIOME_LEISURE_VALUES})$"]({bbox});'
        )
        lines.append(
            f'  relation["type"="multipolygon"]'
            f'["landuse"~"^({BIOME_LANDUSE_VALUES})$"]({bbox});'
        )
        lines.append(
            f'  relation["type"="multipolygon"]'
            f'["natural"~"^({BIOME_NATURAL_VALUES})$"]({bbox});'
        )

    if config.industry:
        for kind in ("node", "way"):
            lines.append(
                f'  {kind}["industrial"~"^({INDUSTRY_INDUSTRIAL_VALUES})$"]'
                f'({bbox});'
            )
            lines.append(
                f'  {kind}["craft"~"^({INDUSTRY_CRAFT_VALUES})$"]({bbox});'
            )
            lines.append(
                f'  {kind}["man_made"~"^({INDUSTRY_MAN_MADE_VALUES})$"]'
                f'({bbox});'
            )

    if config.stations:
        lines.append(
            f'  node["railway"~"^({STATION_RAILWAY_VALUES})$"]({bbox});'
        )
        lines.append(f'  node["railway"="platform"]({bbox});')
        lines.append(
            f'  way["railway"~"^({STATION_WAY_RAILWAY_VALUES})$"]({bbox});'
        )
        lines.append(
            f'  way["building"~"^({STATION_BUILDING_VALUES})$"]({bbox});'
        )
        for pattern in STATION_LIFECYCLE_LINES:
            lines.append(f'  {pattern}({bbox});')
        for mode in STATION_MODES:
            lines.append(
                f'  node["public_transport"~"^(station|stop_position)$"]'
                f'["{mode}"="yes"]({bbox});'
            )
            lines.append(
                f'  way["public_transport"~"^(station|platform)$"]'
                f'["{mode}"="yes"]({bbox});'
            )

    if config.places:
        lines.append(f'  node["place"~"^({PLACE_VALUES})$"]({bbox});')

    body = "\n".join(lines)

    return f"""
[out:json][timeout:180];

(
{body}
);

(._;>;);

out body;
"""


# ---------------------------------------------------------------------------
# Vorlagen (wiederverwendbare Konfigurationen)
# ---------------------------------------------------------------------------

def load_templates() -> dict[str, OverpassQueryConfig]:

    if not TEMPLATES_PATH.is_file():
        return {}

    try:
        raw = json.loads(TEMPLATES_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}

    return {
        name: OverpassQueryConfig.from_dict(data)
        for name, data in raw.items()
    }


def save_template(name: str, config: OverpassQueryConfig):

    templates = load_templates()
    templates[name] = config

    TEMPLATES_PATH.parent.mkdir(parents=True, exist_ok=True)

    data = {
        template_name: template_config.to_dict()
        for template_name, template_config in templates.items()
    }

    TEMPLATES_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def delete_template(name: str):

    templates = load_templates()

    if name not in templates:
        return

    del templates[name]

    data = {
        template_name: template_config.to_dict()
        for template_name, template_config in templates.items()
    }

    TEMPLATES_PATH.parent.mkdir(parents=True, exist_ok=True)

    TEMPLATES_PATH.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
