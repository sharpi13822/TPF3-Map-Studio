from dataclasses import dataclass


@dataclass
class Selection:
    """
    Rechteckauswahl.
    """

    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float

    @property
    def width(self) -> float:
        return self.max_lon - self.min_lon

    @property
    def height(self) -> float:
        return self.max_lat - self.min_lat

    @property
    def center(self):
        return (
            (self.min_lat + self.max_lat) / 2,
            (self.min_lon + self.max_lon) / 2
        )