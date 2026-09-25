from src.map.renderer.base_renderer import BaseRenderer


class GeometryRenderer(BaseRenderer):

    def __init__(
        self,
        api,
        layer_manager,
        layer,
        style_resolver,
        selector,
    ):
        self._layer = layer
        self.selector = selector

        super().__init__(
            api,
            layer_manager,
            style_resolver,
        )

    @property
    def layer(self) -> str:
        return self._layer

    def objects(self, osm):
        return self.selector(osm)

    def draw_geometry(
        self,
        object_id,
        geometry,
        style,
    ):
        # Wird beim Batch-Rendering nicht mehr verwendet.
        pass