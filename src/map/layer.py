from enum import Enum


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

    @property
    def label(self):
        return self.value