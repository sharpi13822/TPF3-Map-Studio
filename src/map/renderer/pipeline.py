from collections.abc import Callable

from src.map.renderer.render_item import RenderItem

class RenderPipeline:
    """Erzeugt RenderItems aus OSM-Objekten."""

    def __init__(
        self,
        selector: Callable,
        style_resolver,
    ):
        self.selector = selector
        self.style_resolver = style_resolver

    def build(
        self,
        osm,
        zoom: int | None = None,
    ) -> list[RenderItem]:
        """Erzeugt alle RenderItems für einen Layer.

        Der Parameter ``zoom`` wird aktuell noch nicht verwendet,
        ist aber bereits für zoomabhängige Styles und Level-of-Detail
        vorgesehen.
        """

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
                    geometry=geometry,
                    style=style.to_dict(),
                )
            )

        return items