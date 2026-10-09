"""
Hoehenzonen fuer die Vorschau: gruen, Fels, Schnee.

Reine Berechnung ohne Qt. Die Grenzen sind Meter ueber dem Wasserspiegel und
gelten nur fuer die Vorschau, nicht fuer den Export. Echter Fels haengt im
Spiel zusaetzlich an der Neigung; hier werden nur Hoehenzonen gezeigt.
"""

from __future__ import annotations

import numpy as np

ZONE_GREEN = 0
ZONE_ROCK = 1
ZONE_SNOW = 2

# Mitten der beobachteten Spannen (Fels etwa 325-350 m, Schnee etwa
# 375-425 m). Keine gemessenen Werte, deshalb im Dialog einstellbar.
DEFAULT_ROCK_M = 340.0
DEFAULT_SNOW_M = 390.0

COLOR_GREEN = (70, 150, 70)
COLOR_ROCK = (140, 125, 110)
COLOR_SNOW = (240, 245, 255)


def normalize_limits(rock_m: float, snow_m: float) -> tuple[float, float]:
    """Felsgrenze nicht unter 0, Schneegrenze nie unter der Felsgrenze."""
    rock = max(float(rock_m), 0.0)
    snow = max(float(snow_m), rock)
    return rock, snow


def classify_zones(heights, water_level_m, rock_m, snow_m) -> np.ndarray:
    """Pro Pixel 0 = gruen, 1 = Fels, 2 = Schnee (Hoehe ueber Wasser)."""
    rock, snow = normalize_limits(rock_m, snow_m)
    above = np.asarray(heights, dtype=np.float32) - np.float32(water_level_m)
    zones = np.zeros(above.shape, dtype=np.uint8)
    zones[above >= np.float32(rock)] = ZONE_ROCK
    zones[above >= np.float32(snow)] = ZONE_SNOW
    return zones


def zone_shares(heights, water_level_m, rock_m, snow_m) -> dict:
    """Flaechenanteile in Prozent (ganze Karte) und Maximum ueber Wasser."""
    zones = classify_zones(heights, water_level_m, rock_m, snow_m)
    total = max(zones.size, 1)
    above = np.asarray(heights, dtype=np.float32) - np.float32(water_level_m)
    return {
        "green": 100.0 * float(np.count_nonzero(zones == ZONE_GREEN)) / total,
        "rock": 100.0 * float(np.count_nonzero(zones == ZONE_ROCK)) / total,
        "snow": 100.0 * float(np.count_nonzero(zones == ZONE_SNOW)) / total,
        "max_above_m": float(above.max()) if above.size else 0.0,
    }


def zone_overlay_rgba(
    heights, water_level_m, rock_m, snow_m, alpha: int = 170
) -> np.ndarray:
    """Farbbild (H, W, 4, uint8) der Zonen fuer die Vorschau."""
    zones = classify_zones(heights, water_level_m, rock_m, snow_m)
    palette = np.array([COLOR_GREEN, COLOR_ROCK, COLOR_SNOW], dtype=np.uint8)
    rgba = np.empty(zones.shape + (4,), dtype=np.uint8)
    rgba[..., :3] = palette[zones]
    rgba[..., 3] = np.uint8(max(0, min(255, int(alpha))))
    return rgba