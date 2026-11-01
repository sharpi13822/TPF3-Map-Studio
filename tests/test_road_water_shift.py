import unittest
from types import SimpleNamespace

try:
    from src.heightmap import network_export as ne
except ImportError:
    from heightmap import network_export as ne


def _way(ids):
    return SimpleNamespace(art=ne.ART_STREET, kind=ne.KIND_NORMAL, nodes=ids)


class RoadWaterShiftTest(unittest.TestCase):

    def test_parallel_road_is_moved_away_from_river(self):
        nodes = [(0.0, 5.0), (50.0, 5.0), (100.0, 5.0)]
        network = SimpleNamespace(nodes=nodes, ways=[_way([1, 2, 3])])
        segments = [(-50.0, 0.0, 250.0, 0.0, 250.0, 14.0)]
        moved = ne.separate_roads_from_water(network, segments, max_shift=10.0)
        self.assertEqual(moved, 3)
        for x, y in network.nodes:
            self.assertGreaterEqual(y, 13.9)

    def test_crossing_road_stays(self):
        nodes = [(50.0, -30.0), (50.0, 3.0), (50.0, 30.0)]
        network = SimpleNamespace(nodes=list(nodes), ways=[_way([1, 2, 3])])
        segments = [(-50.0, 0.0, 250.0, 0.0, 250.0, 14.0)]
        moved = ne.separate_roads_from_water(network, segments, max_shift=10.0)
        self.assertEqual(moved, 0)
        self.assertEqual(network.nodes, nodes)

    def test_far_road_and_switch_off(self):
        nodes = [(0.0, 40.0), (50.0, 40.0)]
        network = SimpleNamespace(nodes=list(nodes), ways=[_way([1, 2])])
        segments = [(-50.0, 0.0, 250.0, 0.0, 250.0, 14.0)]
        self.assertEqual(ne.separate_roads_from_water(network, segments), 0)
        self.assertEqual(ne.separate_roads_from_water(network, segments, max_shift=0), 0)
        self.assertEqual(ne.separate_roads_from_water(network, []), 0)


if __name__ == "__main__":
    unittest.main()
