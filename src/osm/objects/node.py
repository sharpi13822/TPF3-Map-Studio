from dataclasses import dataclass, field


@dataclass
class Node:
    """
    OpenStreetMap-Knoten.
    """

    id: int

    lat: float

    lon: float

    tags: dict[str, str] = field(default_factory=dict)