import math
import unittest
from pathlib import Path

from src.heightmap.station_markers import station_marker_data
from src.map.layer import Layer
from src.tpf2.tpf2_geometry import TPF2Geometry

ROOT = Path(__file__).resolve().parent.parent


def _data(rotation=0.0):
    return {
        "map": {"center_lat": 50.2, "center_lon": 7.6, "rotation_deg": rotation,
                "width_m": 10000.0, "height_m": 50000.0},
        "stations": [
            {"id": 1, "name": "Koblenz Hbf", "kind": "station", "status": "", "x": -1200.5, "y": 8000.25},
            {"id": 2, "name": "", "kind": "halt", "status": "im_bau", "x": 300.0, "y": -4500.0},
            {"id": 3, "name": "Bergbahn", "kind": "station", "status": "", "doubtful": True,
             "x": 0.0, "y": 0.0},
        ],
    }


class StationMarkersTest(unittest.TestCase):

    def _roundtrip(self, rotation):
        data = _data(rotation)
        geo = TPF2Geometry(50.2, 7.6, rotation)
        for item, station in zip(station_marker_data(data), data["stations"]):
            x, y = geo.convert(item["lat"], item["lon"])
            self.assertLess(math.hypot(x - station["x"], y - station["y"]), 0.05)

    def test_roundtrip_without_rotation(self):
        self._roundtrip(0.0)

    def test_roundtrip_with_rotation(self):
        self._roundtrip(37.5)

    def test_center_is_map_center(self):
        item = station_marker_data(_data())[2]
        self.assertAlmostEqual(item["lat"], 50.2, places=6)
        self.assertAlmostEqual(item["lon"], 7.6, places=6)

    def test_labels(self):
        items = station_marker_data(_data())
        self.assertEqual(items[0]["label"], "Koblenz Hbf")
        self.assertEqual(items[1]["label"], "(ohne Namen) (im Bau)")
        self.assertEqual(items[2]["label"], "Bergbahn")
        self.assertTrue(items[2]["doubtful"])

    def test_label_betriebsbahnhof_short(self):
        data = _data()
        data["stations"] = [{"id": 9, "name": "Werlau", "kind": "service_station",
                             "status": "betriebsbahnhof", "doubtful": True, "x": 0.0, "y": 0.0}]
        self.assertEqual(station_marker_data(data)[0]["label"], "Werlau")

    def test_empty(self):
        data = _data()
        data["stations"] = []
        self.assertEqual(station_marker_data(data), [])

    def test_layer_enum_and_js_name(self):
        self.assertEqual(Layer.STATIONS.name.lower(), "stations")
        self.assertEqual(Layer.STATIONS.label, "Bahnhöfe")

    def test_map_js_has_stations_layer(self):
        text = (ROOT / "src" / "map" / "web" / "js" / "map.js").read_text(encoding="utf-8")
        self.assertIn('layers.register("stations");', text)
        self.assertIn("showStations(items = [])", text)
        self.assertIn("clearStations()", text)
        self.assertIn("STATION_LABEL_MIN_ZOOM = 12;", text)
        self.assertIn("tpf-labels-hidden", text)

    def test_window_has_hook(self):
        text = (ROOT / "src" / "window.py").read_text(encoding="utf-8")
        self.assertIn("def show_stations_on_map(self, data):", text)
        self.assertIn("Layer.STATIONS", text)


if __name__ == "__main__":
    unittest.main()
