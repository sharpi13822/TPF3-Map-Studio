"""
Offizielle TPF2-Kartengrößen (Name -> Pixelgröße und reale Meter).

WICHTIG zur Genauigkeit: Für die 1:1-Größen (Tiny bis Megalomaniac)
stimmen mehrere unabhängige Community-Quellen überein, die sind
verlässlich. Für andere Seitenverhältnisse als 1:1 ist die Beziehung
zwischen Verhältnis und Pixelgröße NICHT linear (TPF2 versucht laut
Community offenbar, die Gesamtfläche über alle Verhältnisse hinweg
ungefähr gleich zu halten, nicht eine Seite fix zu lassen). Deshalb
sind hier nur die Megalomaniac-Verhältnisse eingetragen, die in diesem
Projekt tatsächlich schon verwendet und bestätigt wurden:

  - 1:1 über mehrere Community-Quellen (6145x6145 px)
  - 1:2 über einen verifizierten Foren-Export (4225x8449 px)
  - 1:3 über die in-game Lexikon-Anzeige im Nürnberg-Projekt bestätigt
    (13.824 x 41.472 km -> 3457x10369 px)
  - 1:5 über die offizielle TPF2-Wiki-Tabelle (gamemanual:mapsizes),
    2689x13441 px - das ist die Größe, die für Halle-Leipzig usw.
    verwendet wurde.

Fehlt eine Kombination (z.B. Large 1:3), bitte NICHT raten: im TPF2-
Karteneditor eine leere Karte dieser Größe anlegen, einmal als PNG
exportieren und die tatsächliche Pixelgröße dort ablesen - das ist die
einzige zuverlässige Quelle, mehrere Community-Threads bestaetigen
dieses Vorgehen als Standardweg.
"""

from __future__ import annotations

from dataclasses import dataclass

METERS_PER_PIXEL = 4.0


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


# 1:1 Basisgrößen - über mehrere unabhängige Community-Quellen bestätigt
MAP_SIZES_1_1: list[MapSize] = [
    MapSize("Winzig 1:1", 1025, 1025, "Community (mehrfach bestätigt)"),
    MapSize("Klein 1:1", 2049, 2049, "Community (mehrfach bestätigt)"),
    MapSize("Mittel 1:1", 3073, 3073, "Community (mehrfach bestätigt)"),
    MapSize("Groß 1:1", 3585, 3585, "Community (mehrfach bestätigt)"),
    MapSize("Sehr groß 1:1", 4097, 4097, "Community (mehrfach bestätigt)"),
    MapSize("Riesig 1:1", 5121, 5121, "Community (Muster N*1024+1, nicht separat exportiert)"),
    MapSize("Größenwahnsinnig 1:1", 6145, 6145, "Community (mehrfach bestätigt)"),
]

# Größenwahnsinnig bei anderen Seitenverhältnissen - nur die in diesem
# Projekt tatsächlich verwendeten/bestätigten Werte, siehe Moduldoku.
MAP_SIZES_MEGALOMANIAC: list[MapSize] = [
    MapSize("Größenwahnsinnig 1:2", 4225, 8449, "Community-Export (Steam-Forum)"),
    MapSize("Größenwahnsinnig 1:3", 3457, 10369, "In-Game-Lexikon (Nürnberg-Projekt)"),
    MapSize("Größenwahnsinnig 1:5", 2689, 13441, "TPF2-Wiki (gamemanual:mapsizes)"),
]

ALL_MAP_SIZES: list[MapSize] = MAP_SIZES_1_1 + MAP_SIZES_MEGALOMANIAC


def get_by_label(label: str) -> MapSize | None:
    for size in ALL_MAP_SIZES:
        if size.label == label:
            return size
    return None