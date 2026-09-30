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


# Bis zu diesem Anteil der neuen Gipfelhoehe (ueber dem Wasser) bleibt das
# Gelaende unveraendert. Erst darueber wird weich gestaucht.
COMPRESS_KNEE_SHARE = 0.6


def _log_compress(excess: np.ndarray, scale: float) -> np.ndarray:
    return scale * np.log1p(excess / scale)


def compress_heights(
    heightmap: np.ndarray,
    water_level_m: float,
    factor: float,
) -> np.ndarray:
    """
    Begrenzt die Hoehen ueber dem Wasserspiegel "mit Knie": Die hoechste Stelle
    landet auf factor (0..1) ihrer urspruenglichen Hoehe ueber dem Wasser.
    Unterhalb des Knies (COMPRESS_KNEE_SHARE der neuen Gipfelhoehe) bleibt das
    Gelaende UNVERAENDERT - Talhaenge und Schluchtwaende behalten ihre Steilheit.
    Darueber wird logarithmisch (weich, ohne Knick in der Steigung) gestaucht,
    so dass Hochflaechen unter der Schnee-/Felsgrenze des Spiels bleiben und
    ihr Relief trotzdem nicht flachgedrueckt wird.

    Das Wasserniveau selbst bleibt unveraendert, der Uebergang ist stetig.
    Liefert eine NEUE Kopie. factor >= 1 bedeutet keine Veraenderung.
    """

    if factor >= 1.0:
        return heightmap.copy()

    heights = heightmap.astype(np.float32, copy=False)

    level = np.float32(water_level_m)

    max_above = float(heights.max()) - float(level)

    cap = max_above * float(factor)

    knee = cap * COMPRESS_KNEE_SHARE

    # Nichts zu tun, wenn schon alles unter dem Knie liegt.
    if max_above <= knee or cap <= 0.0:
        return heightmap.copy()

    # Skalenwert so bestimmen, dass die hoechste Stelle genau auf cap landet
    # (Bisektion; die Kurve waechst mit dem Skalenwert stetig an).
    top_excess = max_above - knee
    target = cap - knee

    low, high = 1e-3, max(top_excess, 1.0)

    for _ in range(60):
        mid = 0.5 * (low + high)
        if float(_log_compress(np.float64(top_excess), mid)) < target:
            low = mid
        else:
            high = mid

    scale = 0.5 * (low + high)

    above = heights - level

    excess = np.maximum(above - np.float32(knee), 0.0)

    compressed = np.float32(knee) + _log_compress(excess, np.float32(scale))

    result = np.where(
        above > np.float32(knee),
        level + compressed,
        heights,
    )

    return result.astype(heightmap.dtype, copy=False)
