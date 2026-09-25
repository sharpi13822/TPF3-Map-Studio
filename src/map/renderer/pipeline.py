from collections.abc import Callable

from src.map.layer import GeometryType
from src.map.renderer.render_item import RenderItem


class RenderPipeline:
    """Erzeugt RenderItems aus OSM-Objekten."""

    def __init__(
        self,
        selector: Callable,
        style_resolver,
        geometry_type: GeometryType,
    ):
        self.selector = selector
        self.style_resolver = style_resolver
        self.geometry_type = geometry_type

    def build(
        self,
        osm,
        zoom: int | None = None,
    ) -> list[RenderItem]:

        items: list[RenderItem] = []

        for obj in self.selector(osm):

            geometry = osm.get_geometry(obj.id)

            if geometry is None:
                continue

            style = self.style_resolver.resolve(
                obj,
                zoom=zoom,
            )

            items.append(
                RenderItem(
                    id=obj.id,
                    type=self.geometry_type.value,
                    geometry=geometry,
                    style=style.to_dict(),
                    properties=dict(
                        getattr(obj, "tags", {})
                    ),
                )
            )

        return items