import py_compile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class FeaturesTest(unittest.TestCase):
    def test_importer_hidden(self):
        from src.features import VACUUMTUBE_IMPORTER
        self.assertIs(VACUUMTUBE_IMPORTER, False)

    def test_window_compiles(self):
        py_compile.compile(str(ROOT / "src" / "window.py"), doraise=True)

    def test_window_guards_menu_entries(self):
        text = (ROOT / "src" / "window.py").read_text(encoding="utf-8")
        self.assertIn("from src.features import VACUUMTUBE_IMPORTER", text)
        self.assertEqual(text.count("if VACUUMTUBE_IMPORTER:"), 5)

    def test_short_segment_menu_entry_guarded(self):
        text = (ROOT / "src" / "window.py").read_text(encoding="utf-8")
        guard = text.index("if VACUUMTUBE_IMPORTER:", text.index("tools_menu = menu.addMenu"))
        entries = [
            text.index(name)
            for name in ('"OSM als .osm exportieren..."', '"Converter-Befehl anzeigen..."',
                         '"Kurze Verbindungssegmente..."', '"Mod-Checker..."')
        ]
        for position in entries:
            self.assertLess(guard, position)

    def test_stations_collected_after_osm_load(self):
        text = (ROOT / "src" / "window.py").read_text(encoding="utf-8")
        loaded = text.index("def _on_osm_loaded")
        failed = text.index("def _on_osm_failed")
        self.assertIn("self._auto_show_stations(osm)", text[loaded:failed])
        self.assertIn("from src.heightmap.station_export import collect_stations", text)

    def test_import_guide_menu_guarded(self):
        text = (ROOT / "src" / "window.py").read_text(encoding="utf-8")
        guard = text.index("if VACUUMTUBE_IMPORTER:", text.index('help_menu = menu.addMenu(tr("Hilfe"))'))
        self.assertLess(guard, text.index('"Import-Anleitung..."'))
        self.assertLess(text.index('"Import-Anleitung..."'), text.index('"Funktionsübersicht..."'))

    def test_dock_help_has_no_hidden_features(self):
        text = (ROOT / "src" / "gui" / "docks.py").read_text(encoding="utf-8")
        self.assertNotIn("Import-Anleitung", text)
        self.assertNotIn("Mod-Checker", text)
        self.assertNotIn("OSM-Export", text)
        self.assertIn("<b>Bahnhöfe:</b>", text)

    def test_short_segment_export_button_guarded(self):
        text = (ROOT / "src" / "gui" / "short_segment_dialog.py").read_text(encoding="utf-8")
        self.assertIn("from src.features import VACUUMTUBE_IMPORTER", text)
        self.assertEqual(text.count("if VACUUMTUBE_IMPORTER:"), 1)
        self.assertLess(
            text.index("if VACUUMTUBE_IMPORTER:"),
            text.index("Vereinfacht als .osm exportieren"),
        )

    def test_short_segment_dialog_compiles(self):
        py_compile.compile(
            str(ROOT / "src" / "gui" / "short_segment_dialog.py"), doraise=True
        )


if __name__ == "__main__":
    unittest.main()
