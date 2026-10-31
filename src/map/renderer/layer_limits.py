"""Obergrenzen und Wichtigkeit der Objekte pro Kartenebene.

Hintergrund (Fehlerbericht zu v0.7.1): Beim Einschalten der Ebene "Fluesse"
wurden 300.000 Linien auf einmal in die Kartenansicht gelegt, die Ansicht
hing und blieb leer. Darum gelten jetzt je Ebene kleinere Grenzen, und wenn
gekuerzt werden muss, bleiben die wichtigsten Objekte (z. B. grosse Fluesse
vor kleinen Baechen, Autobahnen vor Feldwegen).

Die Grenzen betreffen nur die Anzeige in der Karte. Export und Berechnungen
arbeiten weiter mit allen geladenen OSM-Daten.
"""

from src.map.layer import Layer

# Obergrenze der angezeigten Objekte je Ebene.
LAYER_LIMITS = {
    Layer.ROADS: 80_000,
    Layer.RAILWAYS: 80_000,
    Layer.BUILDINGS: 80_000,
    Layer.WATER: 60_000,
    Layer.WATERWAYS: 60_000,
    Layer.PARKS: 60_000,
    Layer.LANDUSE: 60_000,
    Layer.VEGETATION: 60_000,
}

DEFAULT_LIMIT = 60_000

_WATERWAY_RANK = {
    "river": 0,
    "canal": 1,
    "stream": 2,
    "tidal_channel": 2,
    "drain": 3,
    "ditch": 4,
}

_HIGHWAY_RANK = {
    "motorway": 0,
    "motorway_link": 0,
    "trunk": 1,
    "trunk_link": 1,
    "primary": 2,
    "primary_link": 2,
    "secondary": 3,
    "secondary_link": 3,
    "tertiary": 4,
    "tertiary_link": 4,
    "unclassified": 5,
    "residential": 5,
    "living_street": 6,
    "service": 7,
    "track": 8,
    "path": 9,
    "footway": 9,
    "cycleway": 9,
    "bridleway": 9,
    "steps": 9,
}


def limit_for(layer) -> int:
    """Obergrenze fuer eine Ebene (Layer-Wert)."""

    return LAYER_LIMITS.get(layer, DEFAULT_LIMIT)


def _tag(obj, key):
    tags = getattr(obj, "tags", None) or {}
    return tags.get(key)


def _waterway_rank(obj) -> int:
    return _WATERWAY_RANK.get(_tag(obj, "waterway"), 5)


def _highway_rank(obj) -> int:
    return _HIGHWAY_RANK.get(_tag(obj, "highway"), 10)


def _bbox_area(geometry) -> float:
    """Flaeche des Umschliessungsrechtecks einer (auch verschachtelten) Geometrie."""

    xs_min = ys_min = float("inf")
    xs_max = ys_max = float("-inf")
    stack = [geometry]

    while stack:
        item = stack.pop()
        if not isinstance(item, (list, tuple)) or not item:
            continue
        first = item[0]
        if (
            len(item) >= 2
            and isinstance(first, (int, float))
            and isinstance(item[1], (int, float))
        ):
            x, y = item[0], item[1]
            xs_min = min(xs_min, x)
            xs_max = max(xs_max, x)
            ys_min = min(ys_min, y)
            ys_max = max(ys_max, y)
        else:
            stack.extend(item)

    if xs_min == float("inf"):
        return 0.0

    return (xs_max - xs_min) * (ys_max - ys_min)


_AREA_LAYERS = (
    Layer.BUILDINGS,
    Layer.WATER,
    Layer.PARKS,
    Layer.LANDUSE,
    Layer.VEGETATION,
)


def rank_for(layer, osm=None):
    """Sortierschluessel (kleiner = wichtiger) oder None (OSM-Reihenfolge).

    Flaechen-Ebenen (Vegetation, Wasser, Parks, Landnutzung, Gebaeude) werden
    nach Groesse sortiert, wenn die OSM-Daten uebergeben werden: grosse
    Flaechen bleiben, kleine fallen zuerst weg."""

    if layer == Layer.WATERWAYS:
        return _waterway_rank

    if layer == Layer.ROADS:
        return _highway_rank

    if osm is not None and layer in _AREA_LAYERS:

        def _area_rank(obj):
            geometry = osm.get_geometry(obj.id)
            return -_bbox_area(geometry) if geometry is not None else 0.0

        return _area_rank

    return None
