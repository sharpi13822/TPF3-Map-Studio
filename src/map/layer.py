from enum import Enum

from src.i18n import tr


class GeometryType(Enum):

    POLYLINE = "polyline"

    POLYGON = "polygon"


class Layer(Enum):

    ROADS = "Straßen"

    RAILWAYS = "Bahn"

    BUILDINGS = "Gebäude"

    WATER = "Wasser"

    WATERWAYS = "Flüsse"

    PARKS = "Parks"

    LANDUSE = "Landnutzung"

    VEGETATION = "Vegetation"

    STATIONS = "Bahnhöfe"

    @property
    def label(self):
        # Anzeigename in der aktiven Sprache. Der Wert (self.value) bleibt
        # der deutsche Name, weil er als Kennung im Projekt und in der
        # Karte benutzt wird.
        return tr(self.value)