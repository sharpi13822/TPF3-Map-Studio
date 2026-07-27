from dataclasses import dataclass

from src.map.renderer.render_item import RenderItem


@dataclass(slots=True)
class RenderDiff:
    added: list[RenderItem]
    updated: list[RenderItem]
    removed: list[int]