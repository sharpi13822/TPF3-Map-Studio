from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class RenderState:
    """Beschreibt den Renderzustand eines Objekts."""

    geometry_hash: int
    style_hash: int