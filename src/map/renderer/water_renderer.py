from src.map.layer import Layer

from src.map.renderer.base_polygon_renderer import BasePolygonRenderer

from src.map.style.water_style_resolver import WaterStyleResolver


class WaterRenderer(BasePolygonRenderer):

    layer = Layer.WATER

    def __init__(
        self,
        api,
        layer_manager,
    ):
        super().__init__(
            api,
            layer_manager,
            WaterStyleResolver(),
        )

    def objects(self, osm):
        return osm.water()