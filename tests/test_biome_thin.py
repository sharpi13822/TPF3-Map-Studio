import unittest

import numpy as np

from src.heightmap.biome_mask import thin_forest_by_height


class ThinForestTest(unittest.TestCase):
    def test_only_biome_1_above_limit_is_replaced(self):
        index = np.array([[1, 1, 3, 1]], dtype=np.uint8)
        heights = np.array([[10, 400, 500, 340]], dtype=np.float32)
        result = thin_forest_by_height(index, heights, 0.0, 340.0, 0)
        self.assertEqual(result.tolist(), [[1, 0, 3, 0]])

    def test_water_level_is_subtracted(self):
        index = np.array([[1, 1]], dtype=np.uint8)
        heights = np.array([[507, 850]], dtype=np.float32)
        result = thin_forest_by_height(index, heights, 507.0, 340.0, 2)
        self.assertEqual(result.tolist(), [[1, 2]])

    def test_different_raster_size_and_input_untouched(self):
        index = np.ones((4, 4), dtype=np.uint8)
        heights = np.array([[0, 500], [0, 500]], dtype=np.float32)
        result = thin_forest_by_height(index, heights, 0.0, 340.0, 0)
        self.assertEqual(result.shape, (4, 4))
        self.assertEqual(result[:, :2].tolist(), [[1, 1]] * 4)
        self.assertEqual(result[:, 2:].tolist(), [[0, 0]] * 4)
        self.assertTrue(np.all(index == 1))


if __name__ == "__main__":
    unittest.main()