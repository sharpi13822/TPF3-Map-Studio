"""
Meeresboden absenken (Wunsch aus der Community, MattiZockt1234).

Die Hoehenquellen (Copernicus, DGM1 ...) enthalten keine Meerestiefen. Das
offene Meer liegt deshalb flach auf 0 m, also hoechstens knapp unter dem
Wasserspiegel. Im Spiel faellt es dann leicht trocken (Strand statt Wasser),
und eine Kuestenlinie ist kaum zu erkennen.

Dieses Modul senkt alle Meerespixel unter den Wasserspiegel ab: an der Kueste
um `coast_depth_m`, mit wachsendem Abstand zur Kueste weich (Smoothstep) bis
`depth_m` nach `ramp_m` Metern. Land bleibt unveraendert, und Meerespixel, die
schon tiefer liegen, werden nicht angehoben.
"""

from __future__ import annotations

import numpy as np
from scipy.ndimage import distance_transform_edt

DEFAULT_SEA_DEPTH_M = 10.0
DEFAULT_COAST_DEPTH_M = 2.0
DEFAULT_RAMP_M = 300.0


def _smoothstep(t: np.ndarray) -> np.ndarray:
    t = np.clip(t, 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def lower_sea_floor(
    heightmap: np.ndarray,
    sea_mask,
    water_level_m: float,
    pixel_size_m: float,
    depth_m: float = DEFAULT_SEA_DEPTH_M,
    coast_depth_m: float = DEFAULT_COAST_DEPTH_M,
    ramp_m: float = DEFAULT_RAMP_M,
) -> np.ndarray:
    """Gibt ein neues Raster zurueck; ohne Meer (Maske leer/None/falsche Form)
    das unveraenderte Original."""

    if (
        sea_mask is None
        or getattr(sea_mask, "shape", None) != heightmap.shape
        or not np.any(sea_mask)
    ):
        return heightmap

    depth = max(float(depth_m), 0.5)
    coast = min(max(float(coast_depth_m), 0.5), depth)
    sea = np.asarray(sea_mask, dtype=bool)

    dist_m = distance_transform_edt(sea).astype(np.float32) * float(pixel_size_m)
    t = _smoothstep(dist_m[sea] / max(float(ramp_m), 1.0))
    target = float(water_level_m) - (coast + (depth - coast) * t)

    out = np.array(heightmap, dtype=np.float32, copy=True)
    out[sea] = np.minimum(out[sea], target.astype(np.float32))
    return out
