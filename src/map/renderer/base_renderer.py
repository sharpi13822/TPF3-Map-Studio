from abc import ABC, abstractmethod

from src.map.renderer.batch_builder import BatchBuilder
from src.map.renderer.diff_builder import DiffBuilder
from src.map.renderer.pipeline import RenderPipeline
from src.map.renderer.render_cache import RenderCache
from src.map.layer import GeometryType, Layer

class BaseRenderer(ABC):

    def __init__(self, api, layer_manager, style_resolver):
        self.api = api
        self.layer_manager = layer_manager

        self.pipeline = self.create_pipeline(style_resolver)
        self.cache = RenderCache()

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

        if not self.visible():
            return

        items = self.pipeline.build(osm)

        print(f"{self.layer}: items={len(items)}")

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

            batch = BatchBuilder.build(
                diff.updated,
            )

            self.api.update_batch(
                self.layer,
                batch,
            )

        if diff.added:

            batch = BatchBuilder.build(
                diff.added,
            )

            self.api.add_batch(
                self.layer,
                batch,
            )