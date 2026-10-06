"""
Tests fuer src/gui/stations_action.py. Qt wird durch einen Ersatz ersetzt, damit die Bedienung (Meldungen,
Dateiauswahl) ohne Oberflaeche geprueft werden kann.
"""

import importlib
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

from tests.test_network_export import SELECTION, make_osm, node
from tests.test_station_export import build_osm


class FakeBox:
    calls: list = []

    @classmethod
    def information(cls, parent, title, text):
        cls.calls.append(("information", title, text))

    @classmethod
    def warning(cls, parent, title, text):
        cls.calls.append(("warning", title, text))


class FakeFileDialog:
    answer = ("", "")
    asked = 0

    @classmethod
    def getSaveFileName(cls, *args, **kwargs):
        cls.asked += 1
        return cls.answer


def load_module():
    widgets = types.ModuleType("PySide6.QtWidgets")
    widgets.QMessageBox = FakeBox
    widgets.QFileDialog = FakeFileDialog
    pyside = types.ModuleType("PySide6")
    pyside.QtWidgets = widgets
    patcher = mock.patch.dict(sys.modules, {"PySide6": pyside, "PySide6.QtWidgets": widgets})
    patcher.start()
    sys.modules.pop("src.gui.stations_action", None)
    module = importlib.import_module("src.gui.stations_action")
    return module, patcher


class StationsActionTests(unittest.TestCase):

    def setUp(self):
        FakeBox.calls = []
        FakeFileDialog.answer = ("", "")
        FakeFileDialog.asked = 0
        self.module, self.patcher = load_module()

    def tearDown(self):
        sys.modules.pop("src.gui.stations_action", None)
        self.patcher.stop()

    def test_nothing_found_explains_and_does_not_ask_for_a_file(self):
        osm = make_osm([node(1, 0, 0), node(2, 10, 0)], [])
        self.assertFalse(self.module.save_stations_dialog(None, SELECTION, osm))
        self.assertEqual(FakeFileDialog.asked, 0)
        kind, _title, text = FakeBox.calls[0]
        self.assertEqual(kind, "information")
        self.assertIn("keine Bahnhöfe", text)

    def test_cancel_writes_nothing(self):
        FakeFileDialog.answer = ("", "")
        self.assertFalse(self.module.save_stations_dialog(None, SELECTION, build_osm()))
        self.assertEqual(FakeFileDialog.asked, 1)
        self.assertEqual(FakeBox.calls, [])

    def test_chosen_path_writes_json_and_csv_and_reports(self):
        with tempfile.TemporaryDirectory() as folder:
            FakeFileDialog.answer = (str(Path(folder) / "bahnhoefe.json"), "JSON (*.json)")
            self.assertTrue(self.module.save_stations_dialog(None, SELECTION, build_osm()))
            self.assertTrue((Path(folder) / "bahnhoefe.json").is_file())
            self.assertTrue((Path(folder) / "bahnhoefe.csv").is_file())
        kind, _title, text = FakeBox.calls[-1]
        self.assertEqual(kind, "information")
        self.assertIn("2 Bahnhöfe", text)
        self.assertIn("Gespeichert", text)

    def test_reading_error_is_reported_not_raised(self):
        with mock.patch.object(self.module, "collect_stations", side_effect=ValueError("kaputt")):
            self.assertFalse(self.module.save_stations_dialog(None, SELECTION, build_osm()))
        self.assertEqual(FakeBox.calls[0][0], "warning")
        self.assertIn("kaputt", FakeBox.calls[0][2])

    def test_unwritable_target_is_reported(self):
        with mock.patch.object(self.module, "write_stations", side_effect=OSError("kein Zugriff")):
            FakeFileDialog.answer = ("C:/x/bahnhoefe.json", "JSON (*.json)")
            self.assertFalse(self.module.save_stations_dialog(None, SELECTION, build_osm()))
        self.assertEqual(FakeBox.calls[-1][0], "warning")
        self.assertIn("kein Zugriff", FakeBox.calls[-1][2])


if __name__ == "__main__":
    unittest.main()
