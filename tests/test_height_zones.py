import unittest

import numpy as np

from src.heightmap.height_zones import (
    ZONE_GREEN,
    ZONE_ROCK,
    ZONE_SNOW,
    classify_zones,
    normalize_limits,
    zone_overlay_rgba,
    zone_shares,
)


class HeightZonesTest(unittest.TestCase):
    def test_zone_values(self):
        heights = np.array([[0, 100, 350, 400, 500]], dtype=np.float32)
        zones = classify_zones(heights, 0.0, 340.0, 390.0)
        self.assertEqual(
            zones.tolist(),
            [[ZONE_GREEN, ZONE_GREEN, ZONE_ROCK, ZONE_SNOW, ZONE_SNOW]],
        )

    def test_snow_never_below_rock(self):
        self.assertEqual(normalize_limits(400.0, 300.0), (400.0, 400.0))
        heights = np.array([[350, 450]], dtype=np.float32)
        zones = classify_zones(heights, 0.0, 400.0, 300.0)
        self.assertEqual(zones.tolist(), [[ZONE_GREEN, ZONE_SNOW]])

    def test_water_and_below_stay_green(self):
        heights = np.array([[-30, 507, 507]], dtype=np.float32)
        zones = classify_zones(heights, 507.0, 340.0, 390.0)
        self.assertTrue(np.all(zones == ZONE_GREEN))

    def test_shares_sum_to_100(self):
        heights = np.array([[0, 100, 350, 400, 500]], dtype=np.float32)
        shares = zone_shares(heights, 0.0, 340.0, 390.0)
        self.assertAlmostEqual(shares["green"], 40.0)
        self.assertAlmostEqual(shares["rock"], 20.0)
        self.assertAlmostEqual(shares["snow"], 40.0)

    def test_max_above_water(self):
        heights = np.array([[507, 811]], dtype=np.float32)
        shares = zone_shares(heights, 507.0, 340.0, 390.0)
        self.assertAlmostEqual(shares["max_above_m"], 304.0)

    def test_overlay_shape_and_colors(self):
        heights = np.array([[0, 350, 500]], dtype=np.float32)
        rgba = zone_overlay_rgba(heights, 0.0, 340.0, 390.0, alpha=100)
        self.assertEqual(rgba.shape, (1, 3, 4))
        self.assertTrue(np.all(rgba[..., 3] == 100))
        self.assertNotEqual(rgba[0, 0, :3].tolist(), rgba[0, 2, :3].tolist())


if __name__ == "__main__":
    unittest.main()