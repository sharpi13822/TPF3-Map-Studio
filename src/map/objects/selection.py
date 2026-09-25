from __future__ import annotations

import math
from dataclasses import dataclass


# Erdradius für die lokale, ebene Projektion (siehe corners_latlon()).
# Bei Bandlängen bis ~50-60 km ist der Fehler gegenüber einer echten
# Kartenprojektion vernachlässigbar.
_R_EARTH = 6371008.8


@dataclass
class Selection:
    """
    Kartenauswahl: entweder eine einfache achsenparallele Bounding Box
    (wie bisher) oder ein gedrehtes Kartenband mit fester Größe in
    Metern (z.B. für "Größenwahnsinnig 1:5", gedreht auf einen Flusslauf
    oder eine Bahnstrecke).

    Abwärtskompatibel: bestehender Code, der nur min_lat/min_lon/max_lat/
    max_lon verwendet, funktioniert unverändert weiter — rotation_deg
    ist standardmäßig 0.0, und für unrotierte Auswahlen bleiben
    min_lat...max_lon exakt das, was sie schon immer waren.

    Für eine gedrehte Auswahl (rotation_deg != 0) beschreiben
    min_lat...max_lon stattdessen die gerade, umschließende Bounding Box
    des gedrehten Bands (praktisch z.B. für Overpass-Anfragen, die
    ohnehin einen geraden Kasten brauchen) — die tatsächliche Form liefert
    corners_latlon().
    """

    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float

    # Nur bei einer gedrehten Auswahl gesetzt (sonst None / 0.0):
    rotation_deg: float = 0.0
    width_m: float | None = None
    height_m: float | None = None
    center_lat: float | None = None
    center_lon: float | None = None

    # ------------------------------------------------------------
    # Bestehende Eigenschaften (unverändert)
    # ------------------------------------------------------------

    @property
    def width(self) -> float:
        return self.max_lon - self.min_lon

    @property
    def height(self) -> float:
        return self.max_lat - self.min_lat

    @property
    def center(self):
        if self.center_lat is not None and self.center_lon is not None:
            return (self.center_lat, self.center_lon)
        return (
            (self.min_lat + self.max_lat) / 2,
            (self.min_lon + self.max_lon) / 2,
        )

    # ------------------------------------------------------------
    # Neu: gedrehte Auswahl
    # ------------------------------------------------------------

    @property
    def is_rotated(self) -> bool:
        return bool(self.rotation_deg)

    @classmethod
    def from_center(
        cls,
        center_lat: float,
        center_lon: float,
        width_m: float,
        height_m: float,
        rotation_deg: float = 0.0,
        margin_m: float = 0.0,
    ) -> "Selection":
        """Erstellt eine (ggf. gedrehte) Auswahl aus Mittelpunkt, realer
        Größe in Metern und Drehwinkel.

        margin_m: zusätzlicher Sicherheitsrand für die gespeicherte
        Bounding Box (min/max), z.B. damit eine nachgelagerte
        OSM-/Höhendaten-Abfrage etwas über das eigentliche Band
        hinausreicht (siehe docs/notes/edge-clipping-bug.md im
        tpf-map-studio-Schwesterprojekt — an den Kartenrändern fehlen
        sonst leicht echte Nachbarwerte).
        """
        selection = cls(
            min_lat=0.0, min_lon=0.0, max_lat=0.0, max_lon=0.0,
            rotation_deg=rotation_deg,
            width_m=width_m,
            height_m=height_m,
            center_lat=center_lat,
            center_lon=center_lon,
        )
        corners = selection.corners_latlon()
        lats = [c[0] for c in corners]
        lons = [c[1] for c in corners]

        # Sicherheitsrand in Grad umrechnen (grobe, aber für diesen Zweck
        # ausreichende Näherung).
        lat_margin = margin_m / 111_320.0
        lon_margin = margin_m / (111_320.0 * math.cos(math.radians(center_lat)) or 1e-9)

        selection.min_lat = min(lats) - lat_margin
        selection.max_lat = max(lats) + lat_margin
        selection.min_lon = min(lons) - lon_margin
        selection.max_lon = max(lons) + lon_margin

        return selection

    def corners_latlon(self) -> list[tuple[float, float]]:
        """Die vier Eckpunkte des (ggf. gedrehten) Bands als (lat, lon),
        im Uhrzeigersinn beginnend oben links.

        Bei rotation_deg == 0 entspricht das den vier Ecken der
        gespeicherten Bounding Box.
        """
        if not self.width_m or not self.height_m:
            # kein gedrehtes Band definiert -> einfache Bbox-Ecken
            return [
                (self.max_lat, self.min_lon),
                (self.max_lat, self.max_lon),
                (self.min_lat, self.max_lon),
                (self.min_lat, self.min_lon),
            ]

        center_lat, center_lon = self.center
        theta = math.radians(self.rotation_deg)
        up = (math.sin(theta), math.cos(theta))
        right = (math.sin(theta + math.pi / 2), math.cos(theta + math.pi / 2))
        cos0 = math.cos(math.radians(center_lat))
        hx, hy = self.width_m / 2, self.height_m / 2

        def local_to_latlon(x: float, y: float) -> tuple[float, float]:
            e = right[0] * x + up[0] * y
            n = right[1] * x + up[1] * y
            lat = center_lat + math.degrees(n / _R_EARTH)
            lon = center_lon + math.degrees(e / (_R_EARTH * cos0))
            return (lat, lon)

        return [
            local_to_latlon(-hx, hy),
            local_to_latlon(hx, hy),
            local_to_latlon(hx, -hy),
            local_to_latlon(-hx, -hy),
        ]