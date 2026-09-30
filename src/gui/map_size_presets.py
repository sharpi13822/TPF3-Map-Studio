"""
Offizielle TPF3-Kartengroessen (Name -> Pixelgroesse und reale Meter).

Quelle: TPF3-Wiki (gamemanual:mapsizes), 8 Groessenstufen x 5 Seitenver-
haeltnisse = 40 Kombinationen. Die deutschen Namen stammen aus dem
Groessen-Dropdown des TPF3-Karteneditors (Screenshot 30.09.2026), die
Schreibweise ist dort "Gross", "Sehr gross" und "Grössenwahnsinnig" (also
"ss" statt Eszett). Die Groessen Winzig ... Groessenwahnsinnig sind
identisch mit TPF2, "Gigantomanisch" (Gigantomaniac) ist neu.

Bestaetigt am Spiel: "Grössenwahnsinnig 1:5" = 2689 x 13441 px (die
Heightmap aus dem Studio wurde in dieser Groesse importiert). Die im
Import-Dialog angezeigte Groesse in km ist gerundet (Beispiel: "10,5 x
52,5 km" bei exakt 10,752 x 53,76 km).

Alte Beschriftungen mit Eszett ("Groß", "Größenwahnsinnig") werden von
get_by_label() weiterhin gefunden (siehe _normalize).

Fehlt trotzdem eine Kombination oder gibt es Zweifel an einem Wert:
NICHT raten - im TPF3-Karteneditor eine leere Karte dieser Groesse
anlegen, als PNG exportieren und die Pixelgroesse dort ablesen.
"""

from __future__ import annotations

from dataclasses import dataclass

METERS_PER_PIXEL = 4.0

_WIKI_SOURCE = "TPF3-Wiki (gamemanual:mapsizes)"


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

    @property
    def size_name(self) -> str:
        """Name der Groessenstufe, z.B. 'Sehr gross'."""
        return self.label.rsplit(" ", 1)[0]

    @property
    def ratio(self) -> str:
        """Seitenverhaeltnis, z.B. '1:5'."""
        return self.label.rsplit(" ", 1)[1]


# Alle 40 Kombinationen (Groessen wie im TPF3-Karteneditor).
ALL_MAP_SIZES: list[MapSize] = [

    # --- Winzig ---------------------------------------------------
    MapSize("Winzig 1:1", 1025, 1025, _WIKI_SOURCE),
    MapSize("Winzig 1:2", 641, 1281, _WIKI_SOURCE),
    MapSize("Winzig 1:3", 513, 1537, _WIKI_SOURCE),
    MapSize("Winzig 1:4", 513, 1537, _WIKI_SOURCE),
    MapSize("Winzig 1:5", 385, 1921, _WIKI_SOURCE),

    # --- Klein ----------------------------------------------------
    MapSize("Klein 1:1", 2049, 2049, _WIKI_SOURCE),
    MapSize("Klein 1:2", 1409, 2817, _WIKI_SOURCE),
    MapSize("Klein 1:3", 1153, 3457, _WIKI_SOURCE),
    MapSize("Klein 1:4", 1025, 4097, _WIKI_SOURCE),
    MapSize("Klein 1:5", 897, 4481, _WIKI_SOURCE),

    # --- Mittel ---------------------------------------------------
    MapSize("Mittel 1:1", 2817, 2817, _WIKI_SOURCE),
    MapSize("Mittel 1:2", 2049, 4097, _WIKI_SOURCE),
    MapSize("Mittel 1:3", 1665, 4993, _WIKI_SOURCE),
    MapSize("Mittel 1:4", 1409, 5633, _WIKI_SOURCE),
    MapSize("Mittel 1:5", 1281, 6401, _WIKI_SOURCE),

    # --- Gross ----------------------------------------------------
    MapSize("Gross 1:1", 3585, 3585, _WIKI_SOURCE),
    MapSize("Gross 1:2", 2561, 5121, _WIKI_SOURCE),
    MapSize("Gross 1:3", 2049, 6145, _WIKI_SOURCE),
    MapSize("Gross 1:4", 1793, 7169, _WIKI_SOURCE),
    MapSize("Gross 1:5", 1537, 8065, _WIKI_SOURCE),

    # --- Sehr gross -----------------------------------------------
    MapSize("Sehr gross 1:1", 4097, 4097, _WIKI_SOURCE),
    MapSize("Sehr gross 1:2", 2817, 5633, _WIKI_SOURCE),
    MapSize("Sehr gross 1:3", 2305, 6913, _WIKI_SOURCE),
    MapSize("Sehr gross 1:4", 2049, 8193, _WIKI_SOURCE),
    MapSize("Sehr gross 1:5", 1793, 8961, _WIKI_SOURCE),

    # --- Riesig ---------------------------------------------------
    MapSize("Riesig 1:1", 5121, 5121, _WIKI_SOURCE),
    MapSize("Riesig 1:2", 3585, 7169, _WIKI_SOURCE),
    MapSize("Riesig 1:3", 2945, 8833, _WIKI_SOURCE),
    MapSize("Riesig 1:4", 2561, 10241, _WIKI_SOURCE),
    MapSize("Riesig 1:5", 2177, 10881, _WIKI_SOURCE),

    # --- Groessenwahnsinnig ---------------------------------------
    MapSize("Grössenwahnsinnig 1:1", 6145, 6145, _WIKI_SOURCE),
    MapSize("Grössenwahnsinnig 1:2", 4225, 8449, _WIKI_SOURCE),
    MapSize("Grössenwahnsinnig 1:3", 3457, 10369, _WIKI_SOURCE),
    MapSize("Grössenwahnsinnig 1:4", 3073, 12289, _WIKI_SOURCE),
    MapSize("Grössenwahnsinnig 1:5", 2689, 13441, _WIKI_SOURCE),

    # --- Gigantomanisch (neu in TPF3) -----------------------------
    MapSize("Gigantomanisch 1:1", 7169, 7169, _WIKI_SOURCE),
    MapSize("Gigantomanisch 1:2", 5121, 10241, _WIKI_SOURCE),
    MapSize("Gigantomanisch 1:3", 4097, 12289, _WIKI_SOURCE),
    MapSize("Gigantomanisch 1:4", 3585, 14337, _WIKI_SOURCE),
    MapSize("Gigantomanisch 1:5", 3201, 16001, _WIKI_SOURCE),

]


def _normalize(label: str) -> str:
    """Vergleichsform: Eszett als 'ss', Gross-/Kleinschreibung egal."""
    return label.replace("ß", "ss").casefold().strip()


def get_by_label(label: str) -> MapSize | None:
    wanted = _normalize(label)
    for size in ALL_MAP_SIZES:
        if _normalize(size.label) == wanted:
            return size
    return None


def find_by_pixels(width_px: int, height_px: int) -> list[MapSize]:
    """Alle Groessen mit genau diesen Pixelmassen. Meist genau eine;
    'Winzig 1:3' und 'Winzig 1:4' haben laut Tabelle dieselben Masse."""
    return [
        size
        for size in ALL_MAP_SIZES
        if (size.width_px, size.height_px) == (width_px, height_px)
    ]
