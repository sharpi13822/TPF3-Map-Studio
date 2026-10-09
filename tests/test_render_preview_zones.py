import unittest

import numpy as np

from src.heightmap.water_level import render_preview


class RenderPreviewZonesTest(unittest.TestCase):
    def test_zones_change_land_pixels_only(self):
        row = np.linspace(0.0, 500.0, 60, dtype=np.float32)
        heights = np.tile(row, (60, 1))
        plain = render_preview(heights, 0.0, 0.0, 500.0)
        zoned = render_preview(
            heights, 0.0, 0.0, 500.0, zone_limits=(340.0, 390.0)
        )
        self.assertEqual(plain.size, zoned.size)
        # Hoechste Stelle (Schnee) wird eingefaerbt, Wasser (Spalte 0) nicht
        self.assertNotEqual(plain.getpixel((59, 45)), zoned.getpixel((59, 45)))
        self.assertEqual(plain.getpixel((0, 45)), zoned.getpixel((0, 45)))


if __name__ == "__main__":
    unittest.main()