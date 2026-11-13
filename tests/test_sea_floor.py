import unittest

import numpy as np

from src.heightmap.sea_floor import lower_sea_floor

PIXEL = 4.0


def _kueste():
    """Links Land (50 m), rechts offenes Meer (0 m)."""
    h = np.zeros((40, 400), dtype=np.float32)
    h[:, :100] = 50.0
    sea = np.zeros(h.shape, dtype=bool)
    sea[:, 100:] = True
    return h, sea


class SeaFloorTest(unittest.TestCase):
    def test_meer_liegt_unter_dem_wasserspiegel(self):
        h, sea = _kueste()
        out = lower_sea_floor(h, sea, 1.0, PIXEL, depth_m=10.0)
        self.assertTrue(np.all(out[sea] < 1.0 - 1.9))

    def test_weit_draussen_volle_tiefe(self):
        h, sea = _kueste()
        out = lower_sea_floor(h, sea, 1.0, PIXEL, depth_m=10.0, ramp_m=300.0)
        self.assertAlmostEqual(float(out[20, 399]), -9.0, delta=0.01)

    def test_an_der_kueste_flach(self):
        h, sea = _kueste()
        out = lower_sea_floor(h, sea, 1.0, PIXEL, depth_m=10.0, coast_depth_m=2.0)
        self.assertAlmostEqual(float(out[20, 100]), -1.0, delta=0.2)

    def test_tiefe_nimmt_stetig_zu(self):
        h, sea = _kueste()
        out = lower_sea_floor(h, sea, 1.0, PIXEL)
        row = out[20, 100:]
        self.assertTrue(np.all(np.diff(row) <= 1e-4))

    def test_land_unveraendert(self):
        h, sea = _kueste()
        out = lower_sea_floor(h, sea, 1.0, PIXEL)
        self.assertTrue(np.array_equal(out[:, :100], h[:, :100]))

    def test_tieferes_meer_wird_nicht_angehoben(self):
        h, sea = _kueste()
        h[:, 300:] = -50.0
        out = lower_sea_floor(h, sea, 1.0, PIXEL, depth_m=10.0)
        self.assertTrue(np.all(out[:, 300:] == -50.0))

    def test_ohne_meer_original(self):
        h, _ = _kueste()
        self.assertIs(lower_sea_floor(h, None, 1.0, PIXEL), h)
        self.assertIs(lower_sea_floor(h, np.zeros(h.shape, bool), 1.0, PIXEL), h)
        self.assertIs(lower_sea_floor(h, np.ones((3, 3), bool), 1.0, PIXEL), h)


if __name__ == "__main__":
    unittest.main()
