from enum import Enum


class GeometryType(Enum):

    POLYLINE = "polyline"

    POLYGON = "polygon"

class Layer(Enum):

    ROADS = (
        "Straßen",
        "drawRoad",
        "clearRoads",
    )

    RAILWAYS = (
        "Bahn",
        "drawRailway",
        "clearRailways",
    )

    BUILDINGS = (
        "Gebäude",
        "drawBuilding",
        "clearBuildings",
    )

    WATER = (
        "Wasser",
        "drawWater",
        "clearWater",
    )

    WATERWAYS = (
        "Flüsse",
        "drawWaterway",
        "clearWaterways",
    )

    PARKS = (
        "Parks",
        "drawPark",
        "clearParks",
    )

    LANDUSE = (
        "Landnutzung",
        "drawLanduse",
        "clearLanduse",
    )

    VEGETATION = (
        "Vegetation",
        "drawVegetation",
        "clearVegetation",
    )

    def __init__(
        self,
        label,
        draw_method,
        clear_method,
    ):
        self.label = label
        self.draw_method = draw_method
        self.clear_method = clear_method