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
        Way(101, [12, 13], {"public_transport": "platform", "train": "yes", "ref": "2"}),
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


class StopPositionTests(unittest.TestCase):
    """railway=stop ist eine Halteposition auf dem Gleis, kein eigener Bahnhof."""

    def stations(self, nodes, ways=None):
        return se.collect_stations(make_osm(nodes, ways or []), SELECTION)

    def test_stop_next_to_a_station_node_is_a_stop_position_not_a_second_station(self):
        data = self.stations([
            node(1, 0, 0, {"railway": "station", "name": "Teststadt"}),
            node(2, 30, 10, {"railway": "stop", "name": "Teststadt", "public_transport": "stop_position"}),
            node(3, -40, 20, {"railway": "stop", "name": "Teststadt"}),
        ])
        self.assertEqual(len(data["stations"]), 1)
        self.assertEqual(len(data["stations"][0]["stop_positions"]), 2)
        self.assertEqual(data["stations"][0]["kind"], "station")

    def test_same_named_stops_without_a_station_node_make_one_station(self):
        data = self.stations([
            node(1, 1000, 0, {"railway": "stop", "name": "Kaub"}),
            node(2, 1070, 20, {"railway": "stop", "name": "Kaub"}),
            node(3, 1130, 10, {"railway": "stop", "name": "Kaub"}),
        ])
        self.assertEqual(len(data["stations"]), 1)
        station = data["stations"][0]
        self.assertEqual(station["name"], "Kaub")
        self.assertEqual(station["kind"], "halt")
        self.assertTrue(station["from_stops"])
        self.assertEqual(len(station["stop_positions"]), 3)
        self.assertAlmostEqual(station["x"], 1066.67, delta=1.0)

    def test_stops_with_the_same_name_far_apart_are_two_stations(self):
        data = self.stations([
            node(1, 0, 0, {"railway": "stop", "name": "Neustadt"}),
            node(2, 3000, 0, {"railway": "stop", "name": "Neustadt"}),
        ])
        self.assertEqual(len(data["stations"]), 2)

    def test_unnamed_stops_stay_unassigned(self):
        data = self.stations([node(1, 0, 0, {"railway": "stop"})])
        self.assertEqual(data["stations"], [])
        self.assertEqual(len(data["unassigned"]["stop_positions"]), 1)

    def test_a_station_area_with_another_name_is_merged_into_the_node(self):
        nodes = [node(1, 100, 50, {"railway": "station", "name": "Koblenz Hbf"}),
                 node(2, 0, 0), node(3, 200, 0), node(4, 200, 100), node(5, 0, 100)]
        ways = [Way(1, [2, 3, 4, 5, 2], {"railway": "station", "name": "Hauptbahnhof Koblenz"})]
        data = self.stations(nodes, ways)
        self.assertEqual(len(data["stations"]), 1)
        self.assertEqual(data["stations"][0]["name"], "Koblenz Hbf")
        self.assertIn("area_m2", data["stations"][0])

    def test_two_named_station_nodes_100_m_apart_stay_separate(self):
        data = self.stations([
            node(1, 0, 0, {"railway": "station", "name": "Nord"}),
            node(2, 100, 0, {"railway": "station", "name": "Sued"}),
        ])
        self.assertEqual(len(data["stations"]), 2)

    def test_csv_has_the_new_columns(self):
        data = self.stations([
            node(1, 0, 0, {"railway": "station", "name": "Bergbahn", "station": "funicular", "usage": "tourism"}),
            node(2, 3000, 0, {"railway": "stop", "name": "Dorf"}),
        ])
        with tempfile.TemporaryDirectory() as folder:
            _json, csv_path = se.write_stations(data, Path(folder) / "b")
            lines = csv_path.read_text(encoding="utf-8-sig").strip().splitlines()
        self.assertTrue(lines[0].endswith("bahnart;nutzung;aus_haltepositionen;zweifelhaft;bahnsteigkanten;status"))
        by_name = {line.split(";")[1]: line.split(";") for line in lines[1:]}
        self.assertEqual(by_name["Bergbahn"][-6:], ["funicular", "tourism", "", "ja", "0", ""])
        self.assertEqual(by_name["Dorf"][-4], "ja")          # aus Haltepositionen gebildet


class DoubtfulAndPlatformRadiusTests(unittest.TestCase):

    def stations(self, nodes, ways=None):
        return se.collect_stations(make_osm(nodes, ways or []), SELECTION)

    def test_stations_without_stops_and_platforms_are_doubtful_real_ones_are_not(self):
        data = self.stations([
            node(1, 0, 0, {"railway": "station", "name": "Sommerrodelbahn"}),
            node(2, 2000, 0, {"railway": "station", "name": "Echter Bahnhof"}),
            node(3, 2010, 15, {"railway": "stop", "name": "Echter Bahnhof"}),
            node(4, 4000, 0, {"railway": "halt", "name": "Bergbahn", "station": "funicular"}),
            node(5, 4005, 15, {"railway": "stop", "name": "Bergbahn"}),
        ])
        flags = {s["name"]: s["doubtful"] for s in data["stations"]}
        self.assertEqual(flags, {"Sommerrodelbahn": True, "Echter Bahnhof": False, "Bergbahn": True})

    def test_a_platform_300_m_away_belongs_to_the_station_but_not_a_1_km_one(self):
        nodes = [
            node(1, 0, 0, {"railway": "station", "name": "Gross"}),
            node(2, 300, -20), node(3, 400, -20),        # Bahnsteig, Mitte 350 m entfernt
            node(4, 1500, 0), node(5, 1600, 0),          # Bahnsteig 1,5 km entfernt
        ]
        ways = [Way(1, [2, 3], {"railway": "platform"}), Way(2, [4, 5], {"railway": "platform"})]
        data = self.stations(nodes, ways)
        self.assertEqual(data["stations"][0]["platform_count"], 1)
        self.assertEqual(len(data["unassigned"]["platforms"]), 1)

    def test_a_platform_goes_to_the_nearest_of_two_stations(self):
        nodes = [
            node(1, 0, 0, {"railway": "station", "name": "A"}),
            node(2, 700, 0, {"railway": "station", "name": "B"}),
            node(3, 560, 10), node(4, 640, 10),          # Mitte 600 m: naeher an B (100 m) als an A (600 m)
        ]
        data = self.stations(nodes, [Way(1, [3, 4], {"railway": "platform"})])
        by = {s["name"]: s for s in data["stations"]}
        self.assertEqual(by["B"]["platform_count"], 1)
        self.assertEqual(by["A"]["platform_count"], 0)


class BusPlatformTests(unittest.TestCase):
    """Bushaltestellen kommen ueber die Strassenabfrage mit und duerfen nicht als Bahnsteige zaehlen."""

    def stations(self, nodes, ways):
        return se.collect_stations(make_osm(nodes, ways), SELECTION)

    def base(self):
        return [node(1, 0, 0, {"railway": "station", "name": "Bahnhof"}),
                node(2, 40, 0), node(3, 52, 0), node(4, 60, 10), node(5, 72, 10),
                node(6, 80, 20), node(7, 120, 20), node(8, 90, 30), node(9, 130, 30)]

    def test_bus_platforms_are_ignored_and_do_not_end_up_unassigned(self):
        ways = [
            Way(1, [2, 3], {"highway": "platform", "public_transport": "platform", "bus": "yes", "ref": "A"}),
            Way(2, [4, 5], {"highway": "platform", "public_transport": "platform"}),
            Way(3, [6, 7], {"railway": "platform", "ref": "1"}),
            Way(4, [8, 9], {"public_transport": "platform", "train": "yes", "ref": "2"}),
        ]
        data = self.stations(self.base(), ways)
        self.assertEqual(data["stations"][0]["platform_count"], 2)
        self.assertEqual({p["ref"] for p in data["stations"][0]["platforms"]}, {"1", "2"})
        self.assertEqual(data["unassigned"]["platforms"], [])

    def test_a_bus_station_area_is_not_a_station_but_a_rail_one_is(self):
        nodes = [node(2, 0, 0), node(3, 100, 0), node(4, 100, 100), node(5, 0, 100),
                 node(6, 2000, 0), node(7, 2100, 0), node(8, 2100, 100), node(9, 2000, 100)]
        ways = [Way(1, [2, 3, 4, 5, 2], {"public_transport": "station", "bus": "yes", "name": "ZOB"}),
                Way(2, [6, 7, 8, 9, 6], {"public_transport": "station", "train": "yes", "name": "Bahnhof"})]
        data = self.stations(nodes, ways)
        self.assertEqual([s["name"] for s in data["stations"]], ["Bahnhof"])

    def test_building_transportation_counts_only_with_a_rail_tag(self):
        nodes = [node(1, 0, 0, {"railway": "station", "name": "Bahnhof"}),
                 node(2, 20, 20), node(3, 40, 20), node(4, 40, 40), node(5, 20, 40),
                 node(6, 60, 20), node(7, 80, 20), node(8, 80, 40), node(9, 60, 40)]
        ways = [Way(1, [2, 3, 4, 5, 2], {"building": "transportation"}),
                Way(2, [6, 7, 8, 9, 6], {"building": "transportation", "train": "yes"})]
        data = self.stations(nodes, ways)
        self.assertEqual(len(data["stations"][0]["buildings"]), 1)
        self.assertEqual(data["unassigned"]["buildings"], [])

    def test_platform_edges_are_counted_in_their_own_column(self):
        nodes = [node(1, 0, 0, {"railway": "station", "name": "Bahnhof"}),
                 node(2, 20, 10), node(3, 120, 10), node(4, 20, 20), node(5, 120, 20)]
        ways = [Way(1, [2, 3], {"railway": "platform_edge"}), Way(2, [4, 5], {"railway": "platform_edge"})]
        data = self.stations(nodes, ways)
        station = data["stations"][0]
        self.assertEqual(station["platform_count"], 0)
        self.assertEqual(station["platform_edge_count"], 2)


class LifecycleStationTests(unittest.TestCase):
    """Betriebsbahnhoefe, stillgelegte und im Bau befindliche Bahnhoefe (Beispiel Ruedesheim 2026)."""

    def one(self, tags):
        data = se.collect_stations(make_osm([node(1, 0, 0, tags)], []), SELECTION)
        self.assertEqual(len(data["stations"]), 1, tags)
        return data["stations"][0]

    def test_the_real_ruedesheim_node_is_found_as_disused(self):
        station = self.one({
            "disused:public_transport": "station", "long_name": "Rüdesheim Bahnhof", "name": "Rüdesheim Bf",
            "note": "Personenverkehr wird im Zuge der Generalsanierung 2026 verlegt",
            "old_name": "Rüdesheim (Rhein)", "operator": "DB InfraGO AG", "railway": "service_station",
            "railway:ref": "FRDH", "uic_ref": "8005213",
        })
        self.assertEqual(station["name"], "Rüdesheim Bf")
        self.assertEqual(station["kind"], "service_station")
        self.assertEqual(station["status"], "aufgegeben")
        self.assertEqual(station["tags"]["old_name"], "Rüdesheim (Rhein)")

    def test_plain_service_station_is_an_operating_yard(self):
        station = self.one({"railway": "service_station", "name": "Betriebsbahnhof X"})
        self.assertEqual((station["kind"], station["status"]), ("service_station", "betriebsbahnhof"))

    def test_station_under_construction(self):
        for tags in ({"construction:railway": "station", "name": "Neu"},
                     {"railway": "construction", "construction": "halt", "name": "Neu"}):
            station = self.one(tags)
            self.assertEqual(station["status"], "im_bau")
        self.assertEqual(self.one({"railway": "construction", "construction": "halt", "name": "N"})["kind"], "halt")

    def test_disused_station_without_a_railway_tag(self):
        station = self.one({"disused:railway": "station", "name": "Alt"})
        self.assertEqual((station["kind"], station["status"]), ("station", "aufgegeben"))

    def test_normal_stations_have_an_empty_status(self):
        for tags in ({"railway": "station", "name": "A"}, {"railway": "halt", "name": "B"}):
            self.assertEqual(self.one(tags)["status"], "")

    def test_an_ordinary_construction_node_is_not_a_station(self):
        data = se.collect_stations(make_osm([node(1, 0, 0, {"railway": "construction", "construction": "rail"})], []), SELECTION)
        self.assertEqual(data["stations"], [])

    def test_status_is_written_to_the_csv(self):
        data = se.collect_stations(make_osm([node(1, 0, 0, {"railway": "service_station", "name": "Hof",
                                                           "disused:public_transport": "station"})], []), SELECTION)
        with tempfile.TemporaryDirectory() as folder:
            _json, csv_path = se.write_stations(data, Path(folder) / "b")
            lines = csv_path.read_text(encoding="utf-8-sig").strip().splitlines()
        self.assertEqual(lines[1].split(";")[-1], "aufgegeben")


if __name__ == "__main__":
    unittest.main()
