from src.map.layer import Layer

from src.map.renderer.base_polygon_renderer import BasePolygonRenderer

from src.map.style.vegetation_style_resolver import VegetationStyleResolver


class VegetationRenderer(BasePolygonRenderer):

    layer = Layer.VEGETATION

    def __init__(
        self,
        api,
        layer_manager,
    ):
        super().__init__(
            api,
            layer_manager,
            VegetationStyleResolver(),
        )

    def objects(self, osm):
        return osm.vegetation()