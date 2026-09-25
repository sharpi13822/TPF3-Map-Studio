from src.map.renderer.render_cache import RenderCache
from src.map.renderer.render_diff import RenderDiff
from src.map.renderer.render_item import RenderItem
from src.map.renderer.render_state import RenderState


class DiffBuilder:
    """Ermittelt die Änderungen zwischen zwei Renderdurchläufen."""

    @staticmethod
    def build(
        items: list[RenderItem],
        cache: RenderCache,
    ) -> RenderDiff:

        added: list[RenderItem] = []
        updated: list[RenderItem] = []

        current_ids: set[int] = set()

        for item in items:

            current_ids.add(item.id)

            state = RenderState(
                geometry_hash=item.geometry_hash,
                style_hash=item.style_hash,
                properties_hash=item.properties_hash,
            )

            previous = cache.get(item.id)

            if previous is None:
                added.append(item)

            elif previous != state:
                updated.append(item)

            cache.store(
                item.id,
                state,
            )

        removed = list(
            cache.ids - current_ids
        )

        for object_id in removed:
            cache.remove(object_id)

        return RenderDiff(
            added=added,
            updated=updated,
            removed=removed,
        )