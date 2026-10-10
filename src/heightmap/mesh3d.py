"""
Netz fuer die 3D-Vorschau: Raster herunterrechnen, Hoehen ueber Wasser,
Zonenfarben pro Punkt. Reine Berechnung ohne Qt.
"""

from __future__ import annotations

import base64

import numpy as np

from src.heightmap.height_zones import (
    COLOR_GREEN,
    COLOR_ROCK,
    COLOR_SNOW,
    classify_zones,
)

MESH_SIZE = 512


def target_shape(rows: int, cols: int, size: int = MESH_SIZE) -> tuple[int, int]:
    """Zielgroesse: laengste Seite hoechstens size, nie hochgerechnet."""
    scale = min(1.0, float(size) / float(max(rows, cols)))
    return (
        max(2, min(rows, int(round(rows * scale)))),
        max(2, min(cols, int(round(cols * scale)))),
    )


def downsample_heights(heights, size: int = MESH_SIZE) -> np.ndarray:
    array = np.asarray(heights, dtype=np.float32)
    if array.ndim != 2 or min(array.shape) < 2:
        raise ValueError("Raster braucht mindestens 2 x 2 Punkte")
    rows, cols = array.shape
    target_rows, target_cols = target_shape(rows, cols, size)
    row_index = np.linspace(0, rows - 1, target_rows).round().astype(int)
    col_index = np.linspace(0, cols - 1, target_cols).round().astype(int)
    return array[np.ix_(row_index, col_index)]


def build_mesh_payload(
    heights,
    water_level_m: float,
    rock_m: float,
    snow_m: float,
    pixel_size_m: float,
    size: int = MESH_SIZE,
    show_zones: bool = True,
) -> dict:
    """Daten fuer die Web-Seite. Hoehen sind Meter ueber dem Wasserspiegel."""
    source = np.asarray(heights, dtype=np.float32)
    small = downsample_heights(source, size)
    rows, cols = small.shape

    above = small - np.float32(water_level_m)
    zones = classify_zones(small, water_level_m, rock_m, snow_m)
    palette = np.array([COLOR_GREEN, COLOR_ROCK, COLOR_SNOW], dtype=np.uint8)
    colors = palette[zones]
    if not show_zones:
        colors = np.full(colors.shape, 185, dtype=np.uint8)

    cell_m = float(pixel_size_m) * (source.shape[1] - 1) / (cols - 1)

    return {
        "rows": int(rows),
        "cols": int(cols),
        "cell_m": cell_m,
        "max_above_m": float(above.max()),
        "min_above_m": float(above.min()),
        "heights_b64": base64.b64encode(
            np.ascontiguousarray(above.astype("<f4")).tobytes()
        ).decode("ascii"),
        "colors_b64": base64.b64encode(
            np.ascontiguousarray(colors).tobytes()
        ).decode("ascii"),
    }