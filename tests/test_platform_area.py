import math
import unittest

from src.heightmap.station_export import _polygon_extent, collect_stations, merge_platform_ways
from src.tpf2.tpf2_geometry import TPF2Geometry


def _rect(length, width, angle_deg, cx=0.0, cy=0.0):
    a = math.radians(angle_deg)
    ux, uy = math.cos(a), math.sin(a)
    vx, vy = -uy, ux
    corners = []
    for s, t in ((0, 0), (1, 0), (1, 1), (0, 1)):
        x = (s - 0.5) * length
        y = (t - 0.5) * width
        corners.append([cx + x * ux + y * vx, cy + x * uy + y * vy])
    return corners


class _Node:
    def __init__(self, node_id, lat, lon, tags=None):
        self.id, self.lat, self.lon, self.tags = node_id, lat, lon, tags or {}


class _Way:
    def __init__(self, way_id, nodes, tags):
        self.id, self.nodes, self.tags = way_id, nodes, tags


class _Osm:
    def __init__(self, nodes, ways):
        self.nodes = {n.id: n for n in nodes}
        self.ways = {w.id: w for w in ways}
        self.relations = {}


class _Selection:
    center = (50.0, 8.0)
    rotation_deg = 0.0
    width_m = 2000.0
    height_m = 2000.0


class PolygonExtentTest(unittest.TestCase):

    def test_rotated_rectangle(self):
        for angle in (0, 30, 77, 133):
            long_side, short_side = _polygon_extent(_rect(250.0, 10.0, angle) + [_rect(250.0, 10.0, angle)[0]])
            self.assertAlmostEqual(long_side, 250.0, places=2)
            self.assertAlmostEqual(short_side, 10.0, places=2)

    def test_concave_shape_uses_hull(self):
        pts = [[0, 0], [100, 0], [100, 10], [60, 10], [60, 4], [40, 4], [40, 10], [0, 10], [0, 0]]
        long_side, short_side = _polygon_extent(pts)
        self.assertAlmostEqual(long_side, 100.0, places=2)
        self.assertAlmostEqual(short_side, 10.0, places=2)


class CollectClosedPlatformTest(unittest.TestCase):

    def _osm(self, closed, ref="1"):
        geo = TPF2Geometry(50.0, 8.0, 0.0)
        corners = _rect(250.0, 10.0, 30.0, cx=0.0, cy=120.0)
        nodes = [_Node(1, 50.0, 8.0, {"railway": "halt", "name": "Teststation"})]
        ids = []
        for i, (x, y) in enumerate(corners):
            lat, lon = geo.inverse(x, y)
            nodes.append(_Node(100 + i, lat, lon))
            ids.append(100 + i)
        if closed:
            ids.append(ids[0])
        way = _Way(500, ids, {"railway": "platform", "ref": ref})
        return _Osm(nodes, [way])

    def test_closed_platform_length_is_long_side(self):
        data = collect_stations(self._osm(closed=True), _Selection())
        platform = data["stations"][0]["platforms"][0]
        self.assertAlmostEqual(platform["length_m"], 250.0, delta=0.2)
        self.assertAlmostEqual(platform["perimeter_m"], 520.0, delta=0.5)
        self.assertAlmostEqual(platform["width_m"], 10.0, delta=0.2)
        self.assertEqual(data["stations"][0]["platform_count"], 1)
        self.assertAlmostEqual(data["stations"][0]["platform_length_m"], 250.0, delta=0.2)

    def test_open_platform_length_unchanged(self):
        data = collect_stations(self._osm(closed=False), _Selection())
        platform = data["stations"][0]["platforms"][0]
        self.assertNotIn("perimeter_m", platform)
        self.assertAlmostEqual(platform["length_m"], 250.0 + 10.0 + 250.0, delta=0.5)

    def test_closed_platforms_are_not_merged(self):
        a = {"osm_way": 1, "type": "platform", "ref": "1", "closed": True,
             "points": [[0.0, 0.0], [10.0, 0.0], [10.0, 5.0], [0.0, 0.0]], "length_m": 10.0}
        b = {"osm_way": 2, "type": "platform", "ref": "1", "closed": True,
             "points": [[10.0, 0.0], [20.0, 0.0], [20.0, 5.0], [10.0, 0.0]], "length_m": 10.0}
        self.assertEqual(len(merge_platform_ways([a, b])), 2)


if __name__ == "__main__":
    unittest.main()
