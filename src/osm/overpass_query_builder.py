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
    # Neu, standardmaessig AUS: war in der bisherigen fest verdrahteten
    # Abfrage nicht enthalten - Default so gewaehlt, dass bestehendes
    # Verhalten ohne Zutun unveraendert bleibt.
    places: bool = False

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
