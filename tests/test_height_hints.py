import unittest
from pathlib import Path

from src.heightmap.height_hints import HIGH_TERRAIN_M, SNOW_LINE_M, height_hint

ROOT = Path(__file__).resolve().parent.parent


class HeightHintTest(unittest.TestCase):

    def test_bern_without_relative_warns(self):
        # Heightmap-Dialog bei Bern: 488 bis 936 m, Wasserhoehe 496 m
        hint = height_hint(488, 936, 496, relative=False)
        self.assertIsNotNone(hint)
        self.assertIn("komplett weiß", hint)
        self.assertIn("Werte auf Wasserhöhe 0 beziehen", hint)

    def test_bern_relative_is_snow_note_only_when_high(self):
        # 936 - 496 = 440 m ueber dem Wasser: Hinweis auf Schneegrenze, nicht auf "alles weiss"
        hint = height_hint(488, 936, 496, relative=True)
        self.assertIsNotNone(hint)
        self.assertIn("440", hint)
        self.assertNotIn("komplett", hint)

    def test_after_compression_no_hint(self):
        # ca. 75 %: hoechste Stelle bei etwa 330 m ueber dem Wasser
        self.assertIsNone(height_hint(-8, 330, 0, relative=True))

    def test_rhine_needs_no_hint(self):
        self.assertIsNone(height_hint(62, 320, 70, relative=False))

    def test_thresholds(self):
        self.assertIsNone(height_hint(HIGH_TERRAIN_M - 1, SNOW_LINE_M - 1, 0, relative=False))
        self.assertIsNotNone(height_hint(HIGH_TERRAIN_M, HIGH_TERRAIN_M + 10, 0, relative=False))
        self.assertIsNotNone(height_hint(100, SNOW_LINE_M, 0, relative=False))

    def test_high_range_but_low_min_gives_snow_note_without_all_white(self):
        hint = height_hint(150, 900, 160, relative=False)
        self.assertIn("900", hint)
        self.assertNotIn("komplett", hint)

    def test_dialog_uses_the_hint(self):
        source = (ROOT / "src" / "gui" / "heightmap_dialog.py").read_text(encoding="utf-8")
        self.assertIn("from src.heightmap.height_hints import height_hint", source)
        self.assertIn("hint = height_hint(", source)

    def test_guide_explains_absolute_heights(self):
        guide = (ROOT / "src" / "gui" / "heightmap_guide.py").read_text(encoding="utf-8")
        self.assertIn("zählt die Höhe über Meer", guide)
        self.assertIn("Bern", guide)
        self.assertNotIn("Das Spiel färbt nach der\nHöhe über dem Wasser", guide)


if __name__ == "__main__":
    unittest.main()
