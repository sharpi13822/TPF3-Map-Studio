"""Tests fuer src/heightmap/station_export.py (ohne Oberflaeche, ohne Spiel)."""

import json
import tempfile
import unittest
from pathlib import Path

from src.heightmap import station_export as se
from src.osm.objects.way import Way
from tests.test_network_export import SELECTION, make_osm, node


def build_osm():
    nodes = [
        node(1, 0, 0, {"railway": "station", "name": "Teststadt Hbf", "operator": "DB", "tracks": "4"}),
        node(2, 800, 0, {"railway": "halt", "name": "Dorf"}),
        node(3, 5, 40, {"public_transport": "stop_position", "train": "yes", "name": "Teststadt Hbf"}),
        node(4, 5, 40, {}),
        # Bahnsteig 1 (zwei Punkte) und 2
        node(10, -60, 20), node(11, 60, 20),
        node(12, -60, 30), node(13, 60, 30),
        # Gebaeude als Quadrat 20 x 20 m um (0, -50)
        node(20, -10, -60), node(21, 10, -60), node(22, 10, -40), node(23, -10, -40),
        # fremder Bahnsteig weit weg (kein Bahnhof in 250 m)
        node(30, 3000, 3000), node(31, 3100, 3000),
        # ausserhalb der Karte
        node(40, 9000, 0, {"railway": "station", "name": "Draussen"}),
    ]
    ways = [
        Way(100, [10, 11], {"railway": "platform", "ref": "1"}),
        Way(101, [12, 13], {"public_transport": "platform", "ref": "2"}),
        Way(102, [20, 21, 22, 23, 20], {"building": "train_station", "name": "Empfangsgebaeude"}),
        Way(103, [30, 31], {"railway": "platform"}),
        Way(104, [1, 2], {"railway": "rail"}),   # gewoehnliches Gleis: wird ignoriert
    ]
    return make_osm(nodes, ways)


class StationExportTests(unittest.TestCase):

    def setUp(self):
        self.data = se.collect_stations(build_osm(), SELECTION)

    def test_stations_and_halts_inside_the_map(self):
        names = {s["name"]: s for s in self.data["stations"]}
        self.assertEqual(set(names), {"Teststadt Hbf", "Dorf"})
        self.assertEqual(names["Teststadt Hbf"]["kind"], "station")
        self.assertEqual(names["Dorf"]["kind"], "halt")
        self.assertAlmostEqual(names["Dorf"]["x"], 800.0, delta=1.0)

    def test_platforms_buildings_and_stops_go_to_the_nearest_station(self):
        hbf = [s for s in self.data["stations"] if s["name"] == "Teststadt Hbf"][0]
        self.assertEqual(hbf["platform_count"], 2)
        self.assertAlmostEqual(hbf["platform_length_m"], 240.0, delta=2.0)
        self.assertEqual({p["ref"] for p in hbf["platforms"]}, {"1", "2"})
        self.assertEqual(len(hbf["buildings"]), 1)
        self.assertAlmostEqual(hbf["buildings"][0]["area_m2"], 400.0, delta=2.0)
        self.assertEqual(len(hbf["stop_positions"]), 1)
        dorf = [s for s in self.data["stations"] if s["name"] == "Dorf"][0]
        self.assertEqual(dorf["platform_count"], 0)

    def test_far_objects_stay_unassigned_and_plain_tracks_are_ignored(self):
        self.assertEqual(len(self.data["unassigned"]["platforms"]), 1)
        total_platforms = sum(len(s["platforms"]) for s in self.data["stations"])
        self.assertEqual(total_platforms, 2)

    def test_nothing_without_station_data(self):
        empty = se.collect_stations(make_osm([node(1, 0, 0), node(2, 10, 0)], [Way(1, [1, 2], {"highway": "primary"})]), SELECTION)
        self.assertEqual(empty["stations"], [])
        self.assertIn("0 Bahnhöfe", se.summary(empty))

    def test_station_area_without_node_becomes_a_station(self):
        nodes = [node(1, 0, 0), node(2, 100, 0), node(3, 100, 100), node(4, 0, 100)]
        ways = [Way(1, [1, 2, 3, 4, 1], {"railway": "station", "name": "Flaechenbahnhof"})]
        data = se.collect_stations(make_osm(nodes, ways), SELECTION)
        self.assertEqual([s["name"] for s in data["stations"]], ["Flaechenbahnhof"])
        self.assertAlmostEqual(data["stations"][0]["x"], 50.0, delta=1.0)
        self.assertAlmostEqual(data["stations"][0]["area_m2"], 10000.0, delta=20.0)

    def test_node_and_area_of_the_same_station_are_merged(self):
        nodes = [node(1, 50, 50, {"railway": "station", "name": "Doppelt"}),
                 node(2, 0, 0), node(3, 100, 0), node(4, 100, 100), node(5, 0, 100)]
        ways = [Way(1, [2, 3, 4, 5, 2], {"railway": "station", "name": "Doppelt"})]
        data = se.collect_stations(make_osm(nodes, ways), SELECTION)
        self.assertEqual(len(data["stations"]), 1)
        self.assertIn("area_m2", data["stations"][0])

    def test_files_are_written_and_readable(self):
        with tempfile.TemporaryDirectory() as folder:
            json_path, csv_path = se.write_stations(self.data, Path(folder) / "bahnhoefe")
            loaded = json.loads(json_path.read_text(encoding="utf-8"))
            self.assertEqual(len(loaded["stations"]), 2)
            lines = csv_path.read_text(encoding="utf-8-sig").strip().splitlines()
            self.assertEqual(len(lines), 3)                       # Kopf + 2 Bahnhoefe
            self.assertTrue(lines[0].startswith("id;name;art"))
            self.assertIn("Teststadt Hbf", "\n".join(lines))

    def test_summary_text(self):
        text = se.summary(self.data)
        self.assertIn("2 Bahnhöfe", text)
        self.assertIn("2 Bahnsteige", text)


if __name__ == "__main__":
    unittest.main()
