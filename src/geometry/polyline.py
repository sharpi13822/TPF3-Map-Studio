from dataclasses import dataclass, field


@dataclass
class Polyline:

    id: str

    text: str = ""

    points: list = field(
        default_factory=list
    )

    properties: dict = field(
        default_factory=dict
    )