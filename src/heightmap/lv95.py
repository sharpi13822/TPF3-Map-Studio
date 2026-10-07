"""
Umrechnung WGS84 (Breite/Laenge in Grad) <-> Schweizer Landeskoordinaten LV95 (EPSG:2056).

Die Formeln sind die Naeherungsloesungen von swisstopo ("Naeherungsloesungen fuer die direkte
Transformation WGS84 -> CH1903 / LV95"), auf etwa 1 m genau. Das reicht fuer Heightmaps mit
4 m pro Pixel. Die Rueckrichtung wird mit einer kleinen Newton-Iteration aus der Hinrichtung
gebildet, damit beide Richtungen zueinander passen. Vektorisiert auf numpy-Arrays, ohne pyproj.
"""

from __future__ import annotations

import numpy as np

# Kennzahl der Schweizer Kacheln in den Zwischenspeicher-Namen und im Mosaik (EPSG-Code)
LV95_ZONE = 2056

# Grober Umriss von Schweiz und Liechtenstein (Breite von/bis, Laenge von/bis); nur dafuer,
# die swissALTI3D-Auswahl bei passenden Karten anzubieten.
SWISS_BOUNDS = (45.7, 47.9, 5.9, 10.6)


def latlon_to_lv95(lat, lon):
    """(Breite, Laenge) in Grad -> (Ost, Nord) in Metern, LV95."""

    lat = np.asarray(lat, dtype=np.float64)
    lon = np.asarray(lon, dtype=np.float64)

    p = (lat * 3600.0 - 169028.66) / 10000.0
    l = (lon * 3600.0 - 26782.5) / 10000.0

    east = (
        2600072.37
        + 211455.93 * l
        - 10938.51 * l * p
        - 0.36 * l * p**2
        - 44.54 * l**3
    )

    north = (
        1200147.07
        + 308807.95 * p
        + 3745.25 * l**2
        + 76.63 * p**2
        - 194.56 * l**2 * p
        + 119.79 * p**3
    )

    return east, north


def _approx_inverse(east, north):
    """Naeherung der Rueckrichtung (Startwert fuer die Iteration)."""

    y = (np.asarray(east, dtype=np.float64) - 2600000.0) / 1_000_000.0
    x = (np.asarray(north, dtype=np.float64) - 1200000.0) / 1_000_000.0

    l = (
        2.6779094
        + 4.728982 * y
        + 0.791484 * y * x
        + 0.1306 * y * x**2
        - 0.0436 * y**3
    )

    p = (
        16.9023892
        + 3.238272 * x
        - 0.270978 * y**2
        - 0.002528 * x**2
        - 0.0447 * y**2 * x
        - 0.0140 * x**3
    )

    return p * 100.0 / 36.0, l * 100.0 / 36.0


def lv95_to_latlon(east, north, iterations: int = 3):
    """(Ost, Nord) in Metern, LV95 -> (Breite, Laenge) in Grad."""

    east = np.asarray(east, dtype=np.float64)
    north = np.asarray(north, dtype=np.float64)

    lat, lon = _approx_inverse(east, north)

    step = 1e-5

    for _ in range(iterations):

        e0, n0 = latlon_to_lv95(lat, lon)
        e_lat, n_lat = latlon_to_lv95(lat + step, lon)
        e_lon, n_lon = latlon_to_lv95(lat, lon + step)

        a = (e_lat - e0) / step
        b = (e_lon - e0) / step
        c = (n_lat - n0) / step
        d = (n_lon - n0) / step

        det = a * d - b * c

        de = east - e0
        dn = north - n0

        lat = lat + (d * de - b * dn) / det
        lon = lon + (-c * de + a * dn) / det

    return lat, lon
