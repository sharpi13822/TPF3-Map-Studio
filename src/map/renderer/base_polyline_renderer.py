from src.map.renderer.base_renderer import BaseRenderer


class BasePolylineRenderer(BaseRenderer):

    def draw_geometry(
        self,
        object_id,
        geometry,
        style,
    ):

        self.api.draw(
            self.layer,
            object_id,
            geometry,
            style,
        )