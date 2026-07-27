from src.map.layer import Layer

from src.map.renderer.base_polyline_renderer import BasePolylineRenderer

from src.map.style.road_style_resolver import RoadStyleResolver


class RoadRenderer(BasePolylineRenderer):

    layer = Layer.ROADS

    def __init__(
        self,
        api,
        layer_manager,
    ):
        super().__init__(
            api,
            layer_manager,
            RoadStyleResolver(),
        )

    def objects(self, osm):
        return osm.highways()