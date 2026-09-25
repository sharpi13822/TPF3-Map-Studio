from dataclasses import dataclass, field

from src.export.export_item import ExportItem


@dataclass(slots=True)
class ExportData:
    """
    Enthält alle für den Export vorbereiteten Objekte.
    """

    roads: list[ExportItem] = field(
        default_factory=list
    )

    railways: list[ExportItem] = field(
        default_factory=list
    )

    buildings: list[ExportItem] = field(
        default_factory=list
    )

    water: list[ExportItem] = field(
        default_factory=list
    )

    waterways: list[ExportItem] = field(
        default_factory=list
    )

    parks: list[ExportItem] = field(
        default_factory=list
    )

    landuse: list[ExportItem] = field(
        default_factory=list
    )

    vegetation: list[ExportItem] = field(
        default_factory=list
    )