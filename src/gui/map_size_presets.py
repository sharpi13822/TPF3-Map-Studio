"""
Offizielle TPF2-Kartengrößen (Name -> Pixelgröße und reale Meter).

Quelle für alle 35 Kombinationen (7 Größenstufen x 5 Seitenverhältnisse):
TPF2-Wiki (gamemanual:mapsizes) - vollständige Tabelle, vom Nutzer am
25.09.2026 bereitgestellt. Alle 35 daraus berechneten Pixelwerte sind
exakte Ganzzahlen (starkes Indiz für eine präzise Quelle), und 9 von 10
zuvor unabhängig bestätigten Werten stimmen exakt überein.

KORREKTUR ggü. einer früheren Version dieser Datei: "Mittel 1:1" stand
vorher fälschlich mit 3073x3073 px (12,288 km) drin - die TPF2-Wiki-
Tabelle bestätigt zusammen mit den anderen 9 übereinstimmenden Werten
2817x2817 px (11,264 km) als richtig.

Fehlt trotzdem eine Kombination oder gibt es Zweifel an einem Wert:
NICHT raten - im TPF2-Karteneditor eine leere Karte dieser Größe
anlegen, einmal als PNG exportieren und die tatsächliche Pixelgröße
dort ablesen.
"""

from __future__ import annotations

from dataclasses import dataclass

METERS_PER_PIXEL = 4.0

_WIKI_SOURCE = "TPF2-Wiki (gamemanual:mapsizes)"


@dataclass(frozen=True)
class MapSize:
    label: str
    width_px: int
    height_px: int
    confirmed_via: str

    @property
    def width_m(self) -> float:
        return (self.width_px - 1) * METERS_PER_PIXEL

    @property
    def height_m(self) -> float:
        return (self.height_px - 1) * METERS_PER_PIXEL


# Alle 35 Kombinationen aus der TPF2-Wiki-Tabelle (gamemanual:mapsizes).
ALL_MAP_SIZES: list[MapSize] = [

    # --- Winzig ---------------------------------------------------
    MapSize("Winzig 1:1", 1025, 1025, _WIKI_SOURCE),
    MapSize("Winzig 1:2", 641, 1281, _WIKI_SOURCE),
    MapSize("Winzig 1:3", 513, 1537, _WIKI_SOURCE),
    MapSize("Winzig 1:4", 513, 1537, _WIKI_SOURCE),
    MapSize("Winzig 1:5", 385, 1921, _WIKI_SOURCE),

    # --- Klein ------------------------------------------------------
    MapSize("Klein 1:1", 2049, 2049, _WIKI_SOURCE),
    MapSize("Klein 1:2", 1409, 2817, _WIKI_SOURCE),
    MapSize("Klein 1:3", 1153, 3457, _WIKI_SOURCE),
    MapSize("Klein 1:4", 1025, 4097, _WIKI_SOURCE),
    MapSize("Klein 1:5", 897, 4481, _WIKI_SOURCE),

    # --- Mittel -----------------------------------------------------
    MapSize("Mittel 1:1", 2817, 2817, _WIKI_SOURCE),
    MapSize("Mittel 1:2", 2049, 4097, _WIKI_SOURCE),
    MapSize("Mittel 1:3", 1665, 4993, _WIKI_SOURCE),
    MapSize("Mittel 1:4", 1409, 5633, _WIKI_SOURCE),
    MapSize("Mittel 1:5", 1281, 6401, _WIKI_SOURCE),

    # --- Groß ---------------------------------------------------
    MapSize("Groß 1:1", 3585, 3585, _WIKI_SOURCE),
    MapSize("Groß 1:2", 2561, 5121, _WIKI_SOURCE),
    MapSize("Groß 1:3", 2049, 6145, _WIKI_SOURCE),
    MapSize("Groß 1:4", 1793, 7169, _WIKI_SOURCE),
    MapSize("Groß 1:5", 1537, 8065, _WIKI_SOURCE),

    # --- Sehr groß ----------------------------------------------
    MapSize("Sehr groß 1:1", 4097, 4097, _WIKI_SOURCE),
    MapSize("Sehr groß 1:2", 2817, 5633, _WIKI_SOURCE),
    MapSize("Sehr groß 1:3", 2305, 6913, _WIKI_SOURCE),
    MapSize("Sehr groß 1:4", 2049, 8193, _WIKI_SOURCE),
    MapSize("Sehr groß 1:5", 1793, 8961, _WIKI_SOURCE),

    # --- Riesig -----------------------------------------------------
    MapSize("Riesig 1:1", 5121, 5121, _WIKI_SOURCE),
    MapSize("Riesig 1:2", 3585, 7169, _WIKI_SOURCE),
    MapSize("Riesig 1:3", 2945, 8833, _WIKI_SOURCE),
    MapSize("Riesig 1:4", 2561, 10241, _WIKI_SOURCE),
    MapSize("Riesig 1:5", 2177, 10881, _WIKI_SOURCE),

    # --- Größenwahnsinnig --------------------------------------
    MapSize("Größenwahnsinnig 1:1", 6145, 6145, _WIKI_SOURCE),
    MapSize("Größenwahnsinnig 1:2", 4225, 8449, _WIKI_SOURCE),
    MapSize("Größenwahnsinnig 1:3", 3457, 10369, _WIKI_SOURCE),
    MapSize("Größenwahnsinnig 1:4", 3073, 12289, _WIKI_SOURCE),
    MapSize("Größenwahnsinnig 1:5", 2689, 13441, _WIKI_SOURCE),

]


def get_by_label(label: str) -> MapSize | None:
    for size in ALL_MAP_SIZES:
        if size.label == label:
            return size
    return None
