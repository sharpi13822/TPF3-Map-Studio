"""
Geländeglättung gegen Treppenstufen und Facetten.

Das Copernicus-Höhenmodell hat nur etwa 30 m pro Pixel, die Heightmap für das
Spiel aber 4 m pro Pixel. Beim Hochrechnen (bilineare Interpolation) entstehen
ebene Flächen von etwa 30 m Kantenlänge mit Knicken dazwischen: Hänge sehen im
Spiel wie Treppen oder Kristallflächen aus. Eine leichte Gauß-Glättung in der
Größenordnung der Datenauflösung entfernt das, ohne das Relief zu verändern.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import gaussian_filter

# Auf dieser Größenordnung liegt die echte Datenauflösung (Copernicus GLO-30).
DEFAULT_SMOOTHING_SIGMA_M = 15.0


def smooth_terrain(
    heightmap: np.ndarray,
    sigma_m: float,
    pixel_size_m: float,
) -> np.ndarray:
    """
    Glättet das Höhenraster mit einem Gauß-Filter der Breite sigma_m.
    Liefert eine NEUE Kopie, heightmap bleibt unverändert. sigma_m <= 0
    bedeutet keine Glättung.
    """

    if sigma_m <= 0:
        return heightmap.copy()

    sigma_px = sigma_m / pixel_size_m

    smoothed = gaussian_filter(
        heightmap.astype(np.float32, copy=False),
        sigma=sigma_px,
        mode="nearest",
        truncate=3.0,
    )

    return smoothed.astype(heightmap.dtype, copy=False)


def compress_heights(
    heightmap: np.ndarray,
    water_level_m: float,
    factor: float,
) -> np.ndarray:
    """
    Staucht alle Hoehen ueber dem Wasserspiegel auf factor (0..1) ihres
    Abstands zum Wasserspiegel. Das Wasserniveau selbst bleibt unveraendert
    und der Uebergang ist stetig. Sinnvoll, wenn Hochflaechen im Spiel sonst
    ueber die Schneegrenze des Klimas ragen (weisse Flaechen).

    Liefert eine NEUE Kopie. factor >= 1 bedeutet keine Veraenderung.
    """

    if factor >= 1.0:
        return heightmap.copy()

    heights = heightmap.astype(np.float32, copy=False)

    level = np.float32(water_level_m)

    result = np.where(
        heights > level,
        level + (heights - level) * np.float32(factor),
        heights,
    )

    return result.astype(heightmap.dtype, copy=False)
