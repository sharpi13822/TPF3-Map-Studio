import unittest

import numpy as np

from src.heightmap.water_terrain_blend import (
    enforce_osm_water,
    level_terrain_to_rivers,
)

PX = 4.0
LEVEL = 372.0


def _valley(rows=200, cols=240):
    """Tal, das entlang des Flusses um 19 m faellt, mit einer Huegelkette daneben."""
    y, x = np.mgrid[0:rows, 0:cols].astype(np.float32)
    heights = 382.0 - 0.08 * x + 6.0 * np.sin(y / 25.0)
    mask = np.zeros((rows, cols), dtype=bool)
    mask[40:43, :] = True
    return heights.astype(np.float32), mask


class LevelToRiversTest(unittest.TestCase):

    def test_fluss_liegt_auf_wasserhoehe(self):
        heights, mask = _valley()
        out = level_terrain_to_rivers(heights, mask, LEVEL, PX, reach_m=200.0)
        river = out[40:43, 60:180]
        self.assertLess(float(np.abs(river - LEVEL).max()), 1.5)
        # vorher lag der Fluss bis zu 10 m neben dem Wasserspiegel
        self.assertGreater(float(np.abs(heights[40:43, 60:180] - LEVEL).max()), 5.0)

    def test_weit_weg_unveraendert(self):
        heights, mask = _valley()
        out = level_terrain_to_rivers(heights, mask, LEVEL, PX, reach_m=200.0)
        self.assertTrue(np.allclose(out[190:, :], heights[190:, :]))

    def test_ohne_fluss_unveraendert(self):
        heights, _ = _valley()
        empty = np.zeros(heights.shape, dtype=bool)
        out = level_terrain_to_rivers(heights, empty, LEVEL, PX)
        self.assertTrue(np.array_equal(out, heights))


class EnforceWithLevelingTest(unittest.TestCase):

    def _run(self, reach):
        heights, mask = _valley()
        return enforce_osm_water(
            heights, mask, LEVEL, PX,
            transition_m=10.0, max_height_above_water_m=40.0,
            min_area_px=0, level_reach_m=reach,
        )

    def test_weniger_steile_ufer_als_ohne(self):
        old = self._run(0.0)
        new = self._run(400.0)
        steep_old = float(np.abs(np.diff(old[:, 60:180], axis=0)).max())
        steep_new = float(np.abs(np.diff(new[:, 60:180], axis=0)).max())
        self.assertLess(steep_new, steep_old)

    def test_wasser_bleibt_schmal(self):
        new = self._run(400.0)
        wet_rows = (new[:, 100] < LEVEL).sum()
        # 3 Pixel Fluss (12 m) plus hoechstens je 2 Pixel Ufer
        self.assertLessEqual(int(wet_rows), 7)
        self.assertGreaterEqual(int(wet_rows), 3)

    def test_nur_ausserhalb_fluss_ist_land(self):
        new = self._run(400.0)
        self.assertGreaterEqual(float(new[0:20, 100].min()), LEVEL + 1.9)


if __name__ == "__main__":
    unittest.main()
