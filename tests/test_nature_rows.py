import math
import unittest

from src.heightmap.nature_rows import row_paths, total_length


class RowPathsTest(unittest.TestCase):
    def test_square_north_rows(self):
        ring = [(0, 0), (100, 0), (100, 50), (0, 50)]
        paths = row_paths(ring, 0.0, 2.0)
        self.assertEqual(len(paths), 50)
        for (x1, y1), (x2, y2) in paths:
            self.assertAlmostEqual(x1, x2, places=6)
            self.assertAlmostEqual(abs(y2 - y1), 50.0, places=6)
        xs = [p[0][0] for p in paths]
        self.assertAlmostEqual(xs[1] - xs[0], 2.0, places=6)

    def test_east_direction_rows_horizontal(self):
        ring = [(0, 0), (100, 0), (100, 50), (0, 50)]
        paths = row_paths(ring, 90.0, 5.0)
        self.assertEqual(len(paths), 10)
        for (x1, y1), (x2, y2) in paths:
            self.assertAlmostEqual(y1, y2, places=6)
            self.assertAlmostEqual(abs(x2 - x1), 100.0, places=6)

    def test_concave_splits_rows(self):
        # U-Form: Aussparung in der Mitte oben
        ring = [(0, 0), (30, 0), (30, 30), (20, 30), (20, 10), (10, 10),
                (10, 30), (0, 30)]
        paths = row_paths(ring, 0.0, 2.0, min_length_m=1.0)
        counts = {}
        for (x1, _), _ in paths:
            counts[round(x1, 3)] = counts.get(round(x1, 3), 0) + 1
        self.assertTrue(any(c == 1 for c in counts.values()))
        self.assertTrue(all(c <= 2 for c in counts.values()))
        mid = [p for p in paths if 10 < p[0][0] < 20]
        self.assertTrue(mid)
        for (_, y1), (_, y2) in mid:
            self.assertLessEqual(abs(y2 - y1), 10.0 + 1e-6)

    def test_short_pieces_dropped(self):
        ring = [(0, 0), (100, 0), (100, 2), (0, 2)]
        self.assertEqual(row_paths(ring, 90.0, 5.0), [])

    def test_bad_input(self):
        self.assertEqual(row_paths([(0, 0), (1, 1)], 0.0, 2.0), [])
        self.assertEqual(row_paths([(0, 0), (9, 0), (9, 9)], 0.0, 0.0), [])

    def test_total_length(self):
        ring = [(0, 0), (100, 0), (100, 50), (0, 50)]
        self.assertAlmostEqual(total_length(row_paths(ring, 0.0, 2.0)), 2500.0, places=3)

    def test_max_rows(self):
        ring = [(0, 0), (1000, 0), (1000, 50), (0, 50)]
        self.assertEqual(len(row_paths(ring, 0.0, 0.5, max_rows=100)), 100)


if __name__ == "__main__":
    unittest.main()
