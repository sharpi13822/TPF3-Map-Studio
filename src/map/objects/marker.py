from dataclasses import dataclass


@dataclass
class Marker:
    """
    Marker auf der Karte.
    """

    id: str
    lat: float
    lon: float
    text: str = ""
    icon: str = "default"

    color: str = "blue"