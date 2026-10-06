"""
Tests fuer die Bahnhofs-Kategorie im Overpass-Baukasten (overpass_query_builder.py).

Die Datei wird per Pfad geladen (sie liegt in src/...), damit der Test nicht von ihrem genauen Ordner abhaengt.
"""

import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


def load_builder():
    root = Path(__file__).resolve().parent.parent
    path = next((root / "src").rglob("overpass_query_builder.py"))
    spec = importlib.util.spec_from_file_location("overpass_query_builder_under_test", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module          # noetig fuer @dataclass mit "from __future__ import annotations"
    spec.loader.exec_module(module)
    return module


def plain_selection():
    return SimpleNamespace(
        is_rotated=False, min_lat=50.0, min_lon=7.0, max_lat=50.1, max_lon=7.1,
        corners_latlon=lambda: [],
    )


class StationQueryTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.builder = load_builder()

    def query(self, **kwargs):
        config = self.builder.OverpassQueryConfig(**kwargs)
        return self.builder.build_query(plain_selection(), config)

    def test_stations_are_on_by_default(self):
        self.assertTrue(self.builder.OverpassQueryConfig().stations)

    def test_query_asks_for_station_nodes_platforms_buildings_and_stop_positions(self):
        q = self.query()
        self.assertIn('node["railway"~"^(station|halt|stop|tram_stop)$"]', q)
        self.assertIn('node["railway"="platform"]', q)
        self.assertIn('way["railway"~"^(station|halt|platform|platform_edge)$"]', q)
        self.assertIn('way["building"~"^(train_station|transportation)$"]', q)
        self.assertIn('node["public_transport"~"^(station|stop_position)$"]["train"="yes"]', q)
        self.assertIn('way["public_transport"~"^(station|platform)$"]["tram"="yes"]', q)

    def test_query_also_asks_for_service_disused_and_planned_stations(self):
        q = self.query()
        self.assertIn('node["railway"="service_station"]', q)
        self.assertIn('node["disused:railway"~"^(station|halt)$"]', q)
        self.assertIn('node["disused:public_transport"="station"]', q)
        self.assertIn('node["construction:railway"~"^(station|halt)$"]', q)
        self.assertIn('node["railway"="construction"]["construction"~"^(station|halt)$"]', q)

    def test_lifecycle_lines_disappear_with_stations_off(self):
        q = self.query(stations=False)
        self.assertNotIn("service_station", q)
        self.assertNotIn("disused:", q)
        self.assertNotIn("construction:railway", q)

    def test_stations_off_leaves_them_out(self):
        q = self.query(stations=False)
        self.assertNotIn("train_station", q)
        self.assertNotIn("stop_position", q)
        self.assertNotIn('node["railway"', q)

    def test_stations_work_even_if_railways_and_buildings_are_off(self):
        q = self.query(railways=False, buildings=False, stations=True)
        self.assertIn('node["railway"~"^(station|halt|stop|tram_stop)$"]', q)
        self.assertNotIn('way["railway"]', q)
        self.assertNotIn('way["building"]', q)

    def test_old_templates_without_the_key_get_the_default(self):
        old = {"railways": True, "highways": False}
        config = self.builder.OverpassQueryConfig.from_dict(old)
        self.assertTrue(config.stations)
        self.assertFalse(config.highways)

    def test_other_categories_are_unchanged(self):
        q = self.query()
        for part in ('way["highway"]', 'way["building"]', 'way["railway"]', 'node["place"~',
                     'way["waterway"]', '["industrial"~'):
            self.assertIn(part, q)

    def test_query_uses_the_same_bbox_everywhere(self):
        q = self.query()
        self.assertGreaterEqual(q.count("(50.0,7.0,50.1,7.1)"), 20)
        self.assertIn("out body;", q)

    def test_rotated_selection_uses_the_polygon_filter_for_stations_too(self):
        selection = plain_selection()
        selection.is_rotated = True
        selection.corners_latlon = lambda: [(50.0, 7.0), (50.1, 7.0), (50.1, 7.1), (50.0, 7.1)]
        q = self.builder.build_query(selection, self.builder.OverpassQueryConfig())
        self.assertIn('node["railway"~"^(station|halt|stop|tram_stop)$"](poly:"50.0 7.0 50.1 7.0 50.1 7.1 50.0 7.1");', q)


if __name__ == "__main__":
    unittest.main()
