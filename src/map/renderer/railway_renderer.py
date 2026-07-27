from src.map.layer import Layer

from src.map.renderer.base_polyline_renderer import BasePolylineRenderer

from src.map.style.railway_style_resolver import RailwayStyleResolver


class RailwayRenderer(BasePolylineRenderer):

    layer = Layer.RAILWAYS

    def __init__(
        self,
        api,
        layer_manager,
    ):
        super().__init__(
            api,
            layer_manager,
            RailwayStyleResolver(),
        )

    def objects(self, osm):
        return osm.railways()