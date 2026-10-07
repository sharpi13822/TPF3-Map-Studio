"""Prueft, dass Beschreibungen und Oberflaeche zusammenpassen (Hilfetexte, README, Funktionsuebersicht)."""

import ast
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _read(*parts):
    return (ROOT.joinpath(*parts)).read_text(encoding="utf-8")


def _assigned(source, name):
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == name:
            return ast.literal_eval(node.value)
    raise AssertionError(f"{name} nicht gefunden")


class NoEsriTest(unittest.TestCase):

    FILES = (
        ("README.md",), ("THIRD_PARTY_NOTICES.md",),
        ("src", "map", "web", "index.html"), ("src", "map", "web", "js", "map.js"),
        ("src", "gui", "docks.py"), ("src", "gui", "feature_overview_dialog.py"), ("src", "window.py"),
    )

    def test_no_esri_or_satellite_left(self):
        for parts in self.FILES:
            text = _read(*parts).lower()
            self.assertNotIn("esri", text, "/".join(parts))
            self.assertNotIn("satellit", text, "/".join(parts))
            self.assertNotIn("arcgisonline", text, "/".join(parts))

    def test_base_layer_radios_match_map_js(self):
        html = _read("src", "map", "web", "index.html")
        radios = re.findall(r'name="base-layer" value="([^"]+)"', html)
        js = _read("src", "map", "web", "js", "map.js")
        block = js[js.index("static BASE_LAYERS = {"):js.index("#baseLayer = null;")]
        keys = re.findall(r"^        (\w+): \{", block, flags=re.M)
        self.assertEqual(sorted(radios), sorted(keys))
        self.assertEqual(sorted(radios), ["osm", "osm_relief"])


class HelpTextsTest(unittest.TestCase):

    def test_dock_guide_names_every_layer(self):
        source = _read("src", "map", "layer.py")
        layer_block = source[source.index("class Layer("):]
        labels = re.findall(r'^    [A-Z_]+ = "([^"]+)"', layer_block, flags=re.M)
        self.assertGreaterEqual(len(labels), 9)
        guide = _read("src", "gui", "docks.py")
        for label in labels:
            self.assertIn(f"<b>{label}:</b>", guide, label)

    def test_dock_guide_has_no_old_layer_names(self):
        guide = _read("src", "gui", "docks.py")
        for old in ("<b>Schienen:</b>", "<b>Wasserwege:</b>"):
            self.assertNotIn(old, guide)

    def test_layer_help_mentions_lock_and_right_click(self):
        window = _read("src", "window.py")
        help_text = window[window.index('LAYER_HELP_HTML = """'):window.index("class _OsmWorker")]
        for word in ("Haken", "Schloss", "Balken", "Pfeile", "Rechtsklick"):
            self.assertIn(word, help_text, word)


class ReadmeInstallTest(unittest.TestCase):

    def test_install_steps_present(self):
        readme = _read("README.md")
        for needle in ("python -m venv .venv", "Activate.ps1", "pip install -r requirements.txt", "python -m src.main",
                       "pip install pyinstaller", "pyinstaller build.spec", "dist\\TPF3-Map-Studio\\TPF3-Map-Studio.exe",
                       "Add python.exe to PATH", "Set-ExecutionPolicy"):
            self.assertIn(needle, readme, needle)

    def test_python_version_is_the_tested_one(self):
        readme = _read("README.md")
        self.assertIn("Python 3.11.9", readme)
        self.assertNotIn("Python 3.12.x", readme)

    def test_files_named_in_readme_exist(self):
        for name in ("requirements.txt", "build.spec", "LICENSE", "THIRD_PARTY_NOTICES.md"):
            self.assertTrue((ROOT / name).exists(), name)
        self.assertTrue((ROOT / "src" / "main.py").exists())


class HeightmapDialogDocumentedTest(unittest.TestCase):

    # Knopf- oder Haken-Text im Dialog -> Stichwort, das in der Funktionsuebersicht stehen muss.
    KEYWORDS = {
        "Schnellvorschau": "Schnellvorschau",
        "Höhendaten herunterladen": "Höhendaten herunterladen",
        "Ausreißer": "Ausreißer",
        "Wasserhöhe aus den OSM-Gewässern vorschlagen": "Wasserhöhe aus den OSM-Gewässern vorschlagen",
        "Gelände glätten": "Gelände glätten",
        "Trassen und Siedlungen einebnen": "Trassen und Siedlungen einebnen",
        "Gefälle ausgleichen": "Gefälle ausgleichen",
        "Wasser nur dort": "Wasser nur dort",
        "Terrain sanft": "Terrain sanft",
        "Werte auf Wasserhöhe 0": "Werte auf Wasserhöhe 0",
        "Exportieren": "Exportieren",
        "Biome-Maske": "Biome-Maske",
        "Städte aus OSM": "Städte aus OSM",
        "Industrien aus OSM": "Industrien aus OSM",
        "Bahnhöfe aus OSM": "Bahnhöfe aus OSM",
    }
    IGNORED = ("Anleitung (F1)", "Schließen", "Straßen und Gleise")

    @unittest.skipUnless((ROOT / "src" / "gui" / "heightmap_dialog.py").exists(), "heightmap_dialog.py fehlt")
    def test_every_dialog_control_is_known_and_documented(self):
        dialog = _read("src", "gui", "heightmap_dialog.py")
        labels = [m.group(2) for m in re.finditer(r'(QPushButton|QCheckBox)\(\s*\n?\s*"([^"]+)"', dialog)]
        self.assertGreaterEqual(len(labels), 10)
        groups = _assigned(_read("src", "gui", "feature_overview_dialog.py"), "FEATURE_GROUPS")
        overview = " ".join(f"{name} {text}" for _menu, features in groups for name, text in features)
        for label in labels:
            if label.startswith(self.IGNORED):
                continue
            keyword = next((k for prefix, k in self.KEYWORDS.items() if label.startswith(prefix)), None)
            self.assertIsNotNone(keyword, f"neues Bedienelement ohne Beschreibung: {label}")
            self.assertIn(keyword, overview, label)

    def test_overview_covers_source_options(self):
        groups = _assigned(_read("src", "gui", "feature_overview_dialog.py"), "FEATURE_GROUPS")
        overview = " ".join(f"{name} {text}" for _menu, features in groups for name, text in features)
        for word in ("Copernicus", "DGM1", "Eigene Kacheln", "Voreinstellung", "16-Bit-PNG"):
            self.assertIn(word, overview, word)


class HeightmapGuideTest(unittest.TestCase):

    @unittest.skipUnless((ROOT / "src" / "gui" / "heightmap_guide.py").exists(), "heightmap_guide.py fehlt")
    def test_guide_is_current(self):
        guide = _assigned(_read("src", "gui", "heightmap_guide.py"), "GUIDE_HTML")
        self.assertNotIn("Satellit", guide)
        self.assertIn("Karte + Relief", guide)
        self.assertNotIn("Glättung 1000 m", guide)
        self.assertIn("Glättung 400 m", guide)
        for button in ("Biome-Maske aus OSM", "Städte aus OSM", "Industrien aus OSM", "Bahnhöfe aus OSM"):
            self.assertIn(button, guide, button)

    def test_overview_covers_menus_and_rectangle_fields(self):
        groups = _assigned(_read("src", "gui", "feature_overview_dialog.py"), "FEATURE_GROUPS")
        text = " ".join(f"{menu} {name} {desc}" for menu, features in groups for name, desc in features)
        for word in ("Ansicht-Menü", "Neu und Projekt schließen", "Speichern und Speichern unter", "Marker und Auswahl", "Sicherheitsrand", "Drehwinkel",
                     "heightmaps-Ordner", "ergänzt das Studio aus Copernicus"):
            self.assertIn(word, text, word)


class SwissSourceDocumentedTest(unittest.TestCase):

    def test_attribution_is_everywhere_it_matters(self):
        guide = _assigned(_read("src", "gui", "heightmap_guide.py"), "GUIDE_HTML") if (ROOT / "src" / "gui" / "heightmap_guide.py").exists() else ""
        notices = _read("THIRD_PARTY_NOTICES.md")
        readme = _read("README.md")
        self.assertIn("swissALTI3D", guide)
        self.assertIn("Bundesamt für Landestopografie swisstopo", guide)
        self.assertIn("Quellenangabe ist Pflicht", notices)
        self.assertIn("https://www.swisstopo.admin.ch/en/terms-of-use-free-geodata-and-geoservices", notices)
        self.assertIn("swissALTI3D", readme)
        self.assertIn("Bundesamt für Landestopografie swisstopo", readme)

    def test_overview_names_the_swiss_source(self):
        groups = _assigned(_read("src", "gui", "feature_overview_dialog.py"), "FEATURE_GROUPS")
        text = " ".join(f"{name} {desc}" for _menu, features in groups for name, desc in features)
        self.assertIn("swissALTI3D Schweiz", text)

    def test_license_file_stays_mit(self):
        self.assertIn("MIT License", _read("LICENSE"))


if __name__ == "__main__":
    unittest.main()
