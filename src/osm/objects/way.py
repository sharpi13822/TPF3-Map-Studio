from dataclasses import dataclass, field


@dataclass
class Way:
    """
    OpenStreetMap-Weg.
    """

    id: int

    nodes: list[int] = field(default_factory=list)

    tags: dict[str, str] = field(default_factory=dict)