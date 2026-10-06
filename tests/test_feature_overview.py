import ast
import unittest
from pathlib import Path

PATH = Path(__file__).resolve().parent.parent / "src" / "gui" / "feature_overview_dialog.py"


def _groups():
    tree = ast.parse(PATH.read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "FEATURE_GROUPS":
            return ast.literal_eval(node.value)
    raise AssertionError("FEATURE_GROUPS nicht gefunden")


class FeatureOverviewTest(unittest.TestCase):

    def setUp(self):
        self.groups = _groups()
        self.names = [name for _menu, features in self.groups for name, _text in features]

    def test_removed_entries_are_gone(self):
        for removed in ("OSM als .osm exportieren...", "Mod-Checker...", "Import-Anleitung..."):
            self.assertNotIn(removed, self.names)

    def test_converter_command_stays(self):
        self.assertIn("Converter-Befehl anzeigen...", self.names)

    def test_new_entries_present(self):
        for added in ("Bahnhöfe aus OSM...", "Städte aus OSM...", "Industrien aus OSM...",
                      "Biome-Maske aus OSM...", "Ebene Bahnhöfe"):
            self.assertIn(added, self.names)

    def test_structure(self):
        for menu, features in self.groups:
            self.assertIsInstance(menu, str)
            self.assertTrue(features)
            for name, text in features:
                self.assertTrue(name.strip())
                self.assertTrue(text.strip())

    def test_no_stale_overpass_claim(self):
        text = PATH.read_text(encoding="utf-8")
        self.assertNotIn("exakt der alten Abfrage", text)


if __name__ == "__main__":
    unittest.main()
