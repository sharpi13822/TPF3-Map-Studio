import unittest
from pathlib import Path

from src.heightmap.station_export import merge_platform_ways

ROOT = Path(__file__).resolve().parent.parent


def _platform(way, ref, points, length, ptype="platform"):
    return {"osm_way": way, "type": ptype, "ref": ref, "points": points, "length_m": length, "tags": {}}


def _filsen():
    """Echte Koordinaten aus bahnhoefe.json (Filsen): je Gleis drei aneinanderstossende Wege."""
    return [
        _platform(375462086, "2", [[-4705.3, 13082.18], [-4704.31, 13085.41], [-4701.99, 13092.26],
                                   [-4695.26, 13116.02], [-4687.27, 13141.46], [-4679.55, 13162.29],
                                   [-4672.29, 13182.04], [-4667.1, 13194.82], [-4665.88, 13197.83]], 122.3),
        _platform(375462088, "1", [[-4696.04, 13079.19], [-4695.25, 13082.04], [-4693.18, 13088.67],
                                   [-4686.35, 13111.35], [-4678.18, 13138.18], [-4671.21, 13158.53],
                                   [-4663.22, 13178.57], [-4657.72, 13191.38], [-4656.99, 13193.09]], 120.5),
        _platform(384717528, "2", [[-4665.88, 13197.83], [-4654.53, 13223.61]], 28.2),
        _platform(384717530, "1", [[-4646.07, 13219.07], [-4638.52, 13235.99]], 18.5),
        _platform(384717531, "1", [[-4656.99, 13193.09], [-4646.07, 13219.07]], 28.2),
        _platform(384717534, "2", [[-4654.53, 13223.61], [-4647.18, 13240.18]], 18.1),
    ]


class PlatformMergeTest(unittest.TestCase):

    def test_filsen_has_two_platforms(self):
        result = merge_platform_ways(_filsen())
        self.assertEqual(len(result), 2)
        by_ref = {p["ref"]: p for p in result}
        self.assertEqual(by_ref["2"]["length_m"], 168.6)
        self.assertEqual(by_ref["1"]["length_m"], 167.2)
        self.assertEqual(sorted(by_ref["2"]["osm_ways"]), [375462086, 384717528, 384717534])
        self.assertEqual(sorted(by_ref["1"]["osm_ways"]), [375462088, 384717530, 384717531])

    def test_total_length_unchanged(self):
        before = sum(p["length_m"] for p in _filsen())
        after = sum(p["length_m"] for p in merge_platform_ways(_filsen()))
        self.assertAlmostEqual(before, after, places=1)

    def test_merged_points_form_one_line(self):
        by_ref = {p["ref"]: p for p in merge_platform_ways(_filsen())}
        points = by_ref["2"]["points"]
        self.assertEqual(points[0], [-4705.3, 13082.18])
        self.assertEqual(points[-1], [-4647.18, 13240.18])
        self.assertEqual(len(points), 9 + 1 + 1)

    def test_input_is_not_modified(self):
        data = _filsen()
        merge_platform_ways(data)
        self.assertEqual(len(data), 6)
        self.assertNotIn("osm_ways", data[0])

    def test_same_ref_without_touching_stays_separate(self):
        a = _platform(1, "1", [[0.0, 0.0], [10.0, 0.0]], 10.0)
        b = _platform(2, "1", [[50.0, 0.0], [60.0, 0.0]], 10.0)
        self.assertEqual(len(merge_platform_ways([a, b])), 2)

    def test_touching_but_different_ref_stays_separate(self):
        a = _platform(1, "1", [[0.0, 0.0], [10.0, 0.0]], 10.0)
        b = _platform(2, "2", [[10.0, 0.0], [20.0, 0.0]], 10.0)
        self.assertEqual(len(merge_platform_ways([a, b])), 2)

    def test_empty_ref_is_never_merged(self):
        a = _platform(1, "", [[0.0, 0.0], [10.0, 0.0]], 10.0)
        b = _platform(2, "", [[10.0, 0.0], [20.0, 0.0]], 10.0)
        self.assertEqual(len(merge_platform_ways([a, b])), 2)

    def test_edges_and_points_untouched(self):
        a = _platform(1, "1", [[0.0, 0.0], [10.0, 0.0]], 10.0, ptype="edge")
        b = _platform(2, "1", [[10.0, 0.0], [20.0, 0.0]], 10.0, ptype="edge")
        point = {"osm_node": 5, "type": "point", "ref": "1", "points": [[10.0, 0.0]], "length_m": 0.0, "tags": {}}
        result = merge_platform_ways([a, b, point])
        self.assertEqual(len(result), 3)

    def test_reversed_way_is_joined(self):
        a = _platform(1, "1", [[0.0, 0.0], [10.0, 0.0]], 10.0)
        b = _platform(2, "1", [[20.0, 0.0], [10.0, 0.0]], 10.0)
        result = merge_platform_ways([a, b])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["points"], [[0.0, 0.0], [10.0, 0.0], [20.0, 0.0]])

    def test_order_is_kept(self):
        point = {"osm_node": 5, "type": "point", "ref": "", "points": [[1.0, 1.0]], "length_m": 0.0, "tags": {}}
        result = merge_platform_ways([point] + _filsen())
        self.assertIs(result[0], point)

    def test_collect_stations_calls_merge_before_attach(self):
        text = (ROOT / "src" / "heightmap" / "station_export.py").read_text(encoding="utf-8")
        self.assertLess(
            text.index("platforms = merge_platform_ways(platforms)"),
            text.index('attach(platforms, "platforms", middle, platform_radius_m)'),
        )


if __name__ == "__main__":
    unittest.main()
