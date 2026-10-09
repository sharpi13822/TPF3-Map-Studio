import unittest

import numpy as np

from src.heightmap.terrain_smoothing import compress_heights


def _terrain():
    # Wasser bei 507 m, Gipfel bei 2534 m, dazwischen eine Rampe.
    row = np.linspace(469.0, 2534.0, 200, dtype=np.float32)
    return np.tile(row, (20, 1))


class CompressLowFactorTest(unittest.TestCase):
    def test_peak_lands_on_factor(self):
        water = 507.0
        for factor in (0.05, 0.15, 0.17):
            result = compress_heights(_terrain(), water, factor)
            expected = water + (2534.0 - water) * factor
            self.assertAlmostEqual(float(result.max()), expected, delta=1.0)

    def test_water_level_and_order_kept(self):
        water = 507.0
        original = _terrain()
        result = compress_heights(original, water, 0.05)
        below = original <= water
        self.assertTrue(np.array_equal(result[below], original[below]))
        self.assertTrue(np.all(np.diff(result[0]) >= 0.0))


if __name__ == "__main__":
    unittest.main()
