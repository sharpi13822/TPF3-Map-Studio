from abc import ABC, abstractmethod

from src.map.renderer.batch_builder import BatchBuilder
from src.map.renderer.diff_builder import DiffBuilder
from src.map.renderer.pipeline import RenderPipeline
from src.map.renderer.render_cache import RenderCache
from src.map.layer import GeometryType, Layer
from src.map.renderer.layer_limits import limit_for, rank_for

# Allgemeine Obergrenze (Hoechstwert). Millionen Objekte lassen die
# Kartenansicht (Chromium) einfrieren; je Ebene gelten kleinere Grenzen
# (siehe layer_limits.py), und es bleiben die wichtigsten Objekte.
MAX_ITEMS_PER_LAYER = 300_000

# Objekte pro JavaScript-Aufruf (kein riesiger Einzelaufruf).
BATCH_CHUNK_SIZE = 5_000


def chunked(seq, size=BATCH_CHUNK_SIZE):
    """Zerlegt eine Liste in Stuecke mit hoechstens size Eintraegen."""

    for start in range(0, len(seq), size):
        yield seq[start:start + size]


class BaseRenderer(ABC):

    def __init__(self, api, layer_manager, style_resolver):
        self.api = api
        self.layer_manager = layer_manager

        self.pipeline = self.create_pipeline(style_resolver)
        self.cache = RenderCache()
        self.limit = min(MAX_ITEMS_PER_LAYER, limit_for(self.layer))
        self.truncated = False

    @property
    @abstractmethod
    def layer(self) -> str:
        ...

    @abstractmethod
    def objects(self, osm):
        ...

    def create_pipeline(
            self,
            style_resolver,
    ) -> RenderPipeline:

        geometry_type = (
            GeometryType.POLYGON
            if self.layer in {
                Layer.BUILDINGS,
                Layer.WATER,
                Layer.PARKS,
                Layer.LANDUSE,
                Layer.VEGETATION,
            }
            else GeometryType.POLYLINE
        )

        return RenderPipeline(
            selector=self.objects,
            style_resolver=style_resolver,
            geometry_type=geometry_type,
        )

    def clear(self):
        self.api.clear(self.layer)
        self.cache.clear()

    def visible(self) -> bool:
        return self.layer_manager.is_visible(self.layer)

    def draw(self, osm):

        # Auch ausgeblendete Ebenen werden an die Karte gesendet. Ob sie
        # sichtbar sind, entscheidet allein die Karte (set_layer_visible).
        # So erscheinen die Daten sofort, sobald man den Haken setzt.

        items = self.pipeline.build(
            osm,
            limit=self.limit + 1,
            rank=rank_for(self.layer, osm),
        )

        self.truncated = len(items) > self.limit

        if self.truncated:
            items = items[:self.limit]

        print(
            f"{self.layer}: items={len(items)}"
            + (f" (auf {self.limit} begrenzt)" if self.truncated else "")
        )

        diff = DiffBuilder.build(
            items,
            self.cache,
        )

        print(
            f"{self.layer}: "
            f"added={len(diff.added)} "
            f"updated={len(diff.updated)} "
            f"removed={len(diff.removed)}"
        )

        if diff.removed:
            self.api.remove(
                self.layer,
                diff.removed,
            )

        if diff.updated:

            for part in chunked(diff.updated):

                self.api.update_batch(
                    self.layer,
                    BatchBuilder.build(part),
                )

        if diff.added:

            for part in chunked(diff.added):

                self.api.add_batch(
                    self.layer,
                    BatchBuilder.build(part),
                )
