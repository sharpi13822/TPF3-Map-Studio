import base64
import unittest

import numpy as np

from src.heightmap.height_zones import COLOR_GREEN, COLOR_ROCK, COLOR_SNOW
from src.heightmap.mesh3d import (
    build_mesh_payload,
    downsample_heights,
    target_shape,
)


class MeshShapeTest(unittest.TestCase):

    def test_large_raster_is_reduced(self):
        self.assertEqual(target_shape(3585, 3585, 512), (512, 512))
        rows, cols = target_shape(1000, 4000, 512)
        self.assertEqual(cols, 512)
        self.assertEqual(rows, 128)

    def test_small_raster_is_not_enlarged(self):
        self.assertEqual(target_shape(40, 50, 512), (40, 50))

    def test_downsample_keeps_corners(self):
        data = np.arange(100 * 200, dtype=np.float32).reshape(100, 200)
        out = downsample_heights(data, 50)
        self.assertEqual(out.shape, (25, 50))
        self.assertEqual(out[0, 0], data[0, 0])
        self.assertEqual(out[-1, -1], data[-1, -1])

    def test_too_small_raster_raises(self):
        with self.assertRaises(ValueError):
            downsample_heights(np.zeros((1, 5)))


class MeshPayloadTest(unittest.TestCase):

    def _decode(self, payload):
        heights = np.frombuffer(
            base64.b64decode(payload["heights_b64"]), dtype="<f4"
        ).reshape(payload["rows"], payload["cols"])
        colors = np.frombuffer(
            base64.b64decode(payload["colors_b64"]), dtype=np.uint8
        ).reshape(payload["rows"], payload["cols"], 3)
        return heights, colors

    def test_heights_are_relative_to_water_and_zones_colored(self):
        data = np.array([[0.0, 100.0, 450.0], [50.0, 440.0, 500.0]], dtype=np.float32)
        payload = build_mesh_payload(data, 100.0, 340.0, 390.0, pixel_size_m=4.0)
        heights, colors = self._decode(payload)
        np.testing.assert_allclose(heights, data - 100.0)
        # 450-100 = 350 -> Fels, 440-100 = 340 -> Fels, 500-100 = 400 -> Schnee
        self.assertEqual(tuple(colors[0, 0]), COLOR_GREEN)
        self.assertEqual(tuple(colors[0, 2]), COLOR_ROCK)
        self.assertEqual(tuple(colors[1, 2]), COLOR_SNOW)
        self.assertAlmostEqual(payload["max_above_m"], 400.0, places=3)
        self.assertAlmostEqual(payload["min_above_m"], -100.0, places=3)

    def test_without_zones_everything_is_neutral_gray(self):
        data = np.array([[0.0, 450.0], [500.0, 50.0]], dtype=np.float32)
        payload = build_mesh_payload(
            data, 0.0, 340.0, 390.0, pixel_size_m=4.0, show_zones=False
        )
        _heights, colors = self._decode(payload)
        self.assertEqual(len(set(map(tuple, colors.reshape(-1, 3)))), 1)

    def test_cell_size_follows_reduction(self):
        data = np.zeros((1025, 1025), dtype=np.float32)
        payload = build_mesh_payload(data, 0.0, 340.0, 390.0, pixel_size_m=4.0, size=513)
        self.assertEqual(payload["cols"], 513)
        self.assertAlmostEqual(payload["cell_m"], 8.0, places=6)


if __name__ == "__main__":
    unittest.main()