from src.map.layer import Layer

from src.map.renderer.base_polyline_renderer import BasePolylineRenderer

from src.map.style.waterway_style_resolver import WaterwayStyleResolver


class WaterwayRenderer(BasePolylineRenderer):

    layer = Layer.WATERWAYS

    def __init__(
        self,
        api,
        layer_manager,
    ):
        super().__init__(
            api,
            layer_manager,
            WaterwayStyleResolver(),
        )

    def objects(self, osm):
        return osm.waterways()