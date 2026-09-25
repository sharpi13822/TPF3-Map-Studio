from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ExportItem:
    """
    Ein Objekt, das für den späteren Export vorbereitet ist.
    """

    id: int
    type: str
    geometry: Any
    properties: dict