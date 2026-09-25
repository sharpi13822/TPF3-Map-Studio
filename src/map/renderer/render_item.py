import json

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class RenderItem:
    """Ein vollständig vorbereitetes Renderobjekt."""

    id: int
    type: str
    geometry: Any
    style: dict
    properties: dict

    @property
    def geometry_hash(self) -> int:
        return hash(
            json.dumps(
                self.geometry,
                sort_keys=True,
            )
        )

    @property
    def style_hash(self) -> int:
        return hash(
            json.dumps(
                self.style,
                sort_keys=True,
            )
        )

    @property
    def properties_hash(self) -> int:
        return hash(
            json.dumps(
                self.properties,
                sort_keys=True,
            )
        )