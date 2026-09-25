from collections.abc import Iterable

from src.map.renderer.render_item import RenderItem


class BatchBuilder:
    """Konvertiert RenderItems in das JSON-Format für Leaflet."""

    @staticmethod
    def build(items: Iterable[RenderItem]) -> list[dict]:

        return [
            {
                "id": item.id,
                "type": item.type,
                "geometry": item.geometry,
                "style": item.style,
                "properties": item.properties,
            }
            for item in items
        ]