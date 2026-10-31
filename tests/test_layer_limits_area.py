import unittest

from src.map.layer import Layer
from src.map.renderer.layer_limits import rank_for
from src.map.renderer.pipeline import RenderPipeline


class _Obj:
    def __init__(self, i):
        self.id = i
        self.tags = {}


class _Osm:
    def __init__(self, geoms):
        self.geoms = geoms

    def get_geometry(self, i):
        return self.geoms[i]


class _Style:
    def to_dict(self):
        return {}


class _Resolver:
    def resolve(self, obj, zoom=None):
        return _Style()


def _quad(size):
    return [[0.0, 0.0], [0.0, size], [size, size], [size, 0.0], [0.0, 0.0]]


class FlaechenRangTest(unittest.TestCase):

    def _build(self, layer, geoms, limit):
        objs = [_Obj(i) for i in range(len(geoms))]
        osm = _Osm(geoms)
        pipe = RenderPipeline(
            selector=lambda o: iter(objs),
            style_resolver=_Resolver(),
            geometry_type=type("G", (), {"value": "polygon"})(),
        )
        return [it.id for it in pipe.build(osm, limit=limit, rank=rank_for(layer, osm))]

    def test_groesste_flaechen_bleiben(self):
        geoms = [_quad(s) for s in (1, 5, 2, 9, 3)]
        ids = self._build(Layer.VEGETATION, geoms, limit=2)
        self.assertEqual(ids, [3, 1])

    def test_verschachtelte_geometrie(self):
        geoms = [[_quad(1)], [_quad(7), _quad(2)], [_quad(3)]]
        ids = self._build(Layer.WATER, geoms, limit=1)
        self.assertEqual(ids, [1])

    def test_ohne_osm_bleibt_reihenfolge(self):
        self.assertIsNone(rank_for(Layer.VEGETATION))

    def test_linien_ebenen_unveraendert(self):
        self.assertIsNotNone(rank_for(Layer.WATERWAYS))
        self.assertIsNotNone(rank_for(Layer.ROADS))


if __name__ == "__main__":
    unittest.main()
