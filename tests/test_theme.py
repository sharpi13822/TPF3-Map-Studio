import re
import unittest
from pathlib import Path

from src.gui import icon_set, theme

ROOT = Path(__file__).resolve().parent.parent
ICONS = ROOT / "src" / "gui" / "icons"


class ThemeTest(unittest.TestCase):

    def setUp(self):
        self.css = theme.build_stylesheet(ICONS)

    def test_palette_colors_are_hex(self):
        for name, value in theme.PALETTE.items():
            self.assertRegex(value, r"^#[0-9a-f]{6}$", name)

    def test_no_unresolved_placeholders(self):
        self.assertNotIn("$", self.css)

    def test_braces_balanced(self):
        self.assertEqual(self.css.count("{"), self.css.count("}"))

    def test_declarations_are_well_formed(self):
        text = re.sub(r"/\*.*?\*/", "", self.css, flags=re.S)
        for block in re.findall(r"\{([^{}]*)\}", text):
            for declaration in [d for d in block.split(";") if d.strip()]:
                self.assertIn(":", declaration, declaration)

    def test_referenced_images_exist(self):
        urls = re.findall(r"url\(([^)]+)\)", self.css)
        self.assertGreaterEqual(len(urls), 8)
        for url in urls:
            self.assertNotIn("\\", url)
            self.assertTrue(Path(url).exists(), url)

    def test_main_widgets_are_styled(self):
        for selector in ("QMenuBar", "QMenu", "QToolBar", "QToolButton", "QDockWidget", "QPushButton", "QComboBox",
                         "QAbstractSpinBox", "QCheckBox::indicator", "QRadioButton::indicator", "QSlider", "QScrollBar"):
            self.assertIn(selector, self.css, selector)


class IconSetTest(unittest.TestCase):

    def test_all_mapped_icons_exist_in_all_variants(self):
        for _keyword, name in icon_set.ACTION_ICONS:
            for variant in icon_set.VARIANTS:
                self.assertTrue(icon_set.icon_path(name, variant).exists(), f"{name}{variant}")

    def test_layer_and_tool_icons_exist(self):
        for name in ("strassen", "bahn", "gebaeude", "wasser", "fluesse", "parks", "landnutzung", "vegetation", "bahnhoefe",
                     "marker", "auswahl", "messen", "zeichnen"):
            self.assertTrue(icon_set.icon_path(name, "_hell").exists(), name)

    def test_name_matching(self):
        self.assertEqual(icon_set.icon_name_for("&Öffnen..."), "oeffnen")
        self.assertEqual(icon_set.icon_name_for("Projekt-Dashboard..."), "dashboard")
        self.assertEqual(icon_set.icon_name_for("Projekteigenschaften..."), "eigenschaften")
        self.assertEqual(icon_set.icon_name_for("Rückgängig"), "rueckgaengig")
        self.assertEqual(icon_set.icon_name_for("Rechteck-Tool"), "rechteck")
        self.assertEqual(icon_set.icon_name_for("Heightmap herunterladen"), "heightmap")
        self.assertIsNone(icon_set.icon_name_for("Etwas ganz anderes"))

    def test_window_applies_theme_and_icons(self):
        text = (ROOT / "src" / "window.py").read_text(encoding="utf-8")
        self.assertIn("apply_theme(QApplication.instance())", text)
        self.assertIn("def _apply_action_icons(self):", text)
        self.assertIn("QTimer.singleShot(0, self._apply_action_icons)", text)


class LayerUiTest(unittest.TestCase):

    def test_layer_row_has_no_emoji_and_known_icons(self):
        import ast

        source = (ROOT / "src" / "gui" / "layer_row.py").read_text(encoding="utf-8")
        for emoji in ("🔒", "🔓", "⬆", "⬇", "🛣", "📄"):
            self.assertNotIn(emoji, source)
        tree = ast.parse(source)
        names = None
        for node in tree.body:
            if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "ICON_NAMES":
                names = ast.literal_eval(node.value)
        self.assertIsNotNone(names)
        for icon_name in list(names.values()) + ["schloss_zu", "schloss_offen", "pfeil_hoch", "pfeil_runter"]:
            self.assertTrue(icon_set.icon_path(icon_name, "_hell").exists(), icon_name)
            self.assertTrue(icon_set.icon_path(icon_name, "_grau").exists(), icon_name)

    def test_map_panel_images_exist(self):
        web = ROOT / "src" / "map" / "web"
        html = (web / "index.html").read_text(encoding="utf-8")
        images = re.findall(r'src="(icons/[^"]+)"', html)
        self.assertGreaterEqual(len(images), 8)
        for image in images:
            self.assertTrue((web / image).exists(), image)

    def test_map_panel_keeps_ids_used_by_scripts(self):
        html = (ROOT / "src" / "map" / "web" / "index.html").read_text(encoding="utf-8")
        for element_id in ("layers-on", "layers-off", "export-json", "import-json", "json-file",
                           "draw-tools", "draw-road", "draw-river", "draw-building", "draw-finish", "layer-control"):
            self.assertIn(f'id="{element_id}"', html, element_id)
        self.assertEqual(html.count('name="base-layer"'), 4)
        self.assertIn('data-layer="openrailwaymap"', html)
        self.assertIn('data-layer="measurement-grid"', html)
        self.assertNotIn("<style>", html)

    def test_css_balanced_and_dark(self):
        css = (ROOT / "src" / "map" / "web" / "css" / "style.css").read_text(encoding="utf-8")
        self.assertEqual(css.count("{"), css.count("}"))
        for color in ("#141e26", "#15b9f9", "#0a81c2", "#d5dee5"):
            self.assertIn(color, css)
        self.assertNotIn("rgba(255,255,255,0.95)", css)


class DetailFixesTest(unittest.TestCase):

    def test_status_bar_items_have_no_border(self):
        css = theme.build_stylesheet(ICONS)
        self.assertIn("QStatusBar::item", css)
        self.assertIn("QSizeGrip", css)

    def test_leaflet_controls_are_dark(self):
        css = (ROOT / "src" / "map" / "web" / "css" / "style.css").read_text(encoding="utf-8")
        self.assertIn(".leaflet-bar a", css)
        self.assertIn(".leaflet-control-attribution", css)
        html = (ROOT / "src" / "map" / "web" / "index.html").read_text(encoding="utf-8")
        self.assertIn("css/style.css?v=4", html)

    def test_layer_panel_title_is_hidden_but_kept(self):
        source = (ROOT / "src" / "gui" / "layer_panel.py").read_text(encoding="utf-8")
        self.assertIn("title.hide()", source)
        self.assertLess(source.index("layout.addWidget(title)"), source.index("title.hide()"))
        self.assertIn("insertWidget(1 + index, row)", source)


if __name__ == "__main__":
    unittest.main()
