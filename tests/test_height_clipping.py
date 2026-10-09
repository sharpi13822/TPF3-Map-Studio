import tempfile
import unittest
from pathlib import Path

import numpy as np

from src.heightmap.height_clipping import (
    GAME_MAX_M,
    GAME_MAX_SPAN_M,
    GAME_MIN_M,
    MODE_CAP,
    MODE_CUT,
    MODE_SQUEEZE,
    MODES,
    apply_height_window,
    default_window,
    describe_report,
    limit_warning,
    normalize_heights,
    window_slider_range,
)

ROOT = Path(__file__).resolve().parent.parent


def _ramp(low, high, rows=40, cols=50):
    """Raster, dessen Hoehe von low (oben) bis high (unten) gleichmaessig steigt."""
    column = np.linspace(low, high, rows, dtype=np.float32)
    return np.tile(column[:, None], (1, cols))


class GameLimitsTest(unittest.TestCase):

    def test_limits_are_the_tested_editor_values(self):
        self.assertEqual(GAME_MIN_M, -100.0)
        self.assertEqual(GAME_MAX_M, 3177.0)
        self.assertEqual(GAME_MAX_SPAN_M, 3277.0)


class ApplyWindowTest(unittest.TestCase):

    def test_cap_flattens_the_top(self):
        heights = _ramp(0, 4000)
        out, report = apply_height_window(heights, 0, 3177, MODE_CAP)
        self.assertEqual(float(out.max()), 3177.0)
        self.assertEqual(float(out.min()), 0.0)
        self.assertGreater(report.lowered_fraction, 0.1)
        self.assertEqual(report.raised_fraction, 0.0)
        # unterhalb der Grenze bleibt alles unveraendert
        below = heights < 3177
        np.testing.assert_array_equal(out[below], heights[below])

    def test_cut_flattens_the_bottom(self):
        heights = _ramp(-500, 2000)
        out, report = apply_height_window(heights, GAME_MIN_M, 2000, MODE_CUT)
        self.assertEqual(float(out.min()), GAME_MIN_M)
        self.assertEqual(float(out.max()), 2000.0)
        self.assertEqual(report.lowered_fraction, 0.0)
        self.assertGreater(report.raised_fraction, 0.1)

    def test_input_is_not_modified(self):
        heights = _ramp(0, 4000)
        before = heights.copy()
        for mode in MODES:
            apply_height_window(heights, 0, 3000, mode)
        np.testing.assert_array_equal(heights, before)

    def test_terrain_inside_the_window_is_unchanged(self):
        heights = _ramp(100, 900)
        for mode in MODES:
            out, report = apply_height_window(heights, 0, 3177, mode)
            np.testing.assert_allclose(out, heights, atol=1e-3, err_msg=mode)
            self.assertEqual(report.changed_fraction, 0.0, mode)

    def test_result_always_lies_in_the_window(self):
        heights = _ramp(-800, 5000)
        for mode in MODES:
            out, _report = apply_height_window(heights, -20, 3177, mode, anchor=70)
            self.assertGreaterEqual(float(out.min()), -20.0, mode)
            self.assertLessEqual(float(out.max()), 3177.0, mode)

    def test_fraction_is_measured_on_the_full_raster(self):
        heights = np.zeros((100, 100), dtype=np.float32)
        heights[:5, :] = 500.0  # 5 % der Flaeche zu hoch
        _out, report = apply_height_window(heights, 0, 100, MODE_CAP)
        self.assertAlmostEqual(report.lowered_fraction, 0.05, places=6)
        self.assertIn("5,0 % der Fläche werden planiert", describe_report(report))

    def test_invalid_window_and_mode_raise(self):
        with self.assertRaises(ValueError):
            apply_height_window(_ramp(0, 10), 5, 5)
        with self.assertRaises(ValueError):
            apply_height_window(_ramp(0, 10), 0, 10, "wuerfeln")


class SqueezeTest(unittest.TestCase):

    def test_squeeze_keeps_the_anchor_and_the_order(self):
        heights = _ramp(0, 4200)
        out, report = apply_height_window(heights, 0, 3177, MODE_SQUEEZE, anchor=70)
        # Reihenfolge der Hoehen bleibt erhalten (keine Umkehrung)
        self.assertTrue(np.all(np.diff(out[:, 0]) >= 0))
        self.assertAlmostEqual(float(out.max()), 3177.0, delta=0.01)
        self.assertLess(report.scale_up, 1.0)
        self.assertEqual(report.scale_down, 1.0)

    def test_squeeze_value_at_anchor_is_exactly_kept(self):
        heights = np.array([[0.0, 70.0, 4200.0]], dtype=np.float32)
        out, _report = apply_height_window(heights, 0, 3177, MODE_SQUEEZE, anchor=70)
        self.assertAlmostEqual(float(out[0, 1]), 70.0, places=3)
        self.assertAlmostEqual(float(out[0, 0]), 0.0, places=3)
        self.assertAlmostEqual(float(out[0, 2]), 3177.0, places=2)

    def test_squeeze_below_the_anchor(self):
        heights = np.array([[-500.0, 70.0, 300.0]], dtype=np.float32)
        out, report = apply_height_window(heights, -20, 3177, MODE_SQUEEZE, anchor=70)
        self.assertAlmostEqual(float(out[0, 0]), -20.0, places=3)
        self.assertAlmostEqual(float(out[0, 1]), 70.0, places=3)
        self.assertAlmostEqual(float(out[0, 2]), 300.0, places=3)
        self.assertLess(report.scale_down, 1.0)
        self.assertEqual(report.scale_up, 1.0)

    def test_squeeze_never_stretches(self):
        heights = _ramp(100, 200)
        out, report = apply_height_window(heights, -20, 3177, MODE_SQUEEZE)
        np.testing.assert_allclose(out, heights, atol=1e-3)
        self.assertEqual(report.scale_up, 1.0)

    def test_flat_terrain_does_not_divide_by_zero(self):
        heights = np.full((10, 10), 4000.0, dtype=np.float32)
        out, _report = apply_height_window(heights, 0, 3177, MODE_SQUEEZE)
        self.assertTrue(np.all(np.isfinite(out)))
        self.assertLessEqual(float(out.max()), 3177.0)


class DefaultWindowTest(unittest.TestCase):

    def test_alps_top_is_capped_by_default(self):
        self.assertEqual(default_window(0, 4200, MODE_CAP), (0.0, 3177.0))

    def test_deep_pits_are_cut_by_default(self):
        self.assertEqual(default_window(-500, 2000, MODE_CUT), (-100.0, 2000.0))

    def test_terrain_that_fits_gives_its_own_range(self):
        for mode in MODES:
            self.assertEqual(default_window(5, 400, mode), (5.0, 400.0))

    def test_width_decides_where_cap_and_cut_place_the_window(self):
        self.assertEqual(default_window(0, 4200, MODE_CAP, width=2000), (0.0, 2000.0))
        self.assertEqual(default_window(0, 4200, MODE_CUT, width=2000), (1177.0, 3177.0))

    def test_squeeze_always_uses_the_whole_range(self):
        self.assertEqual(default_window(0, 4200, MODE_SQUEEZE, width=500), (0.0, 3177.0))

    def test_window_never_wider_than_the_editor_allows(self):
        for mode in MODES:
            low, high = default_window(-2000, 9000, mode, width=99999)
            self.assertGreaterEqual(low, GAME_MIN_M)
            self.assertLessEqual(high, GAME_MAX_M)
            self.assertLessEqual(high - low, GAME_MAX_SPAN_M)

    def test_terrain_completely_outside_gets_a_valid_window(self):
        low, high = default_window(5000, 6000, MODE_CAP)
        self.assertLess(low, high)
        self.assertLessEqual(high, GAME_MAX_M)

    def test_slider_range(self):
        # ueber den ganzen Editor-Bereich, unabhaengig vom Gelaende
        self.assertEqual(window_slider_range(2000), (-100.0, 1177.0))
        # nichts zu schieben, wenn das Fenster die ganze Editor-Spanne fuellt (oder mehr)
        self.assertEqual(window_slider_range(GAME_MAX_SPAN_M), (-100.0, -100.0))
        self.assertEqual(window_slider_range(5000), (-100.0, -100.0))

    def test_slider_moves_a_window_that_already_fits(self):
        # Gelaende 503..2961 m (Bern/Alpen-Beispiel): Fenster = Gelaende, trotzdem verschiebbar
        low, high = window_slider_range(2961 - 503)
        self.assertLess(low, 503)
        self.assertGreater(high, 503)
        # ganz nach oben geschoben schneidet das Fenster den tiefen Teil ab
        out, report = apply_height_window(_ramp(503, 2961), high, high + (2961 - 503), MODE_CUT)
        self.assertGreater(report.raised_fraction, 0.05)
        # ganz nach unten geschoben kappt es die Gipfel
        out, report = apply_height_window(_ramp(503, 2961), low, low + (2961 - 503), MODE_CAP)
        self.assertGreater(report.lowered_fraction, 0.0)


class WarningAndTextTest(unittest.TestCase):

    def test_limit_warning(self):
        self.assertIsNone(limit_warning(-20, 3177))
        self.assertIsNone(limit_warning(0, 936))
        self.assertIn("3177", limit_warning(0, 4200))
        self.assertIsNone(limit_warning(-100, 500))
        self.assertIn("-100", limit_warning(-150, 500))

    def test_describe_untouched_terrain(self):
        _out, report = apply_height_window(_ramp(0, 500), 0, 3177, MODE_CAP)
        self.assertIn("Nichts wird planiert", describe_report(report))

    def test_describe_squeeze(self):
        _out, report = apply_height_window(_ramp(0, 4200), 0, 3177, MODE_SQUEEZE, anchor=0)
        text = describe_report(report)
        self.assertIn("Gestaucht", text)
        self.assertIn("76 %", text)


class SharedNormalizationTest(unittest.TestCase):

    def test_normalize_heights(self):
        norm = normalize_heights(np.array([-50.0, 0.0, 50.0, 100.0, 500.0]), 0, 100)
        np.testing.assert_allclose(norm, [0, 0, 0.5, 1, 1])

    def test_export_and_preview_use_the_same_function(self):
        exporter = (ROOT / "src" / "heightmap" / "heightmap_exporter.py").read_text(encoding="utf-8")
        preview = (ROOT / "src" / "heightmap" / "water_level.py").read_text(encoding="utf-8")
        for source in (exporter, preview):
            self.assertIn("from src.heightmap.height_clipping import", source)
            self.assertIn("normalize_heights(", source)

    def test_exported_png_matches_normalize_heights(self):
        from PIL import Image

        from src.heightmap.heightmap_exporter import export_heightmap_png

        heights = _ramp(GAME_MIN_M, 3500, rows=30, cols=20)
        clipped, _report = apply_height_window(heights, GAME_MIN_M, GAME_MAX_M, MODE_CAP)

        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "h.png"
            export_heightmap_png(clipped, path, GAME_MIN_M, GAME_MAX_M)
            image = np.array(Image.open(path))

        expected = (normalize_heights(clipped, GAME_MIN_M, GAME_MAX_M) * 65535).astype(np.uint16)
        np.testing.assert_array_equal(image, expected)
        self.assertEqual(int(image.max()), 65535)
        self.assertEqual(int(image.min()), 0)


class PreviewHighlightTest(unittest.TestCase):

    def test_preview_marks_top_red_and_bottom_cyan(self):
        from src.heightmap.water_level import render_preview

        heights = np.full((80, 80), 100.0, dtype=np.float32)
        original = heights.copy()
        original[60:, :] = 400.0   # oben gekappt (im Ergebnis 100)
        original[50:55, :] = -50.0  # unten abgeschnitten (im Ergebnis 100)

        image = render_preview(
            heights,
            water_level_m=-1000.0,
            range_min_m=0.0,
            range_max_m=200.0,
            original_heightmap=original,
        )
        rgb = np.array(image)

        red = rgb[70, 10]
        cyan = rgb[52, 10]
        plain = rgb[45, 10]

        self.assertGreater(int(red[0]), int(red[1]) + 60)
        self.assertGreater(int(cyan[1]), int(cyan[0]) + 60)
        self.assertGreater(int(cyan[2]), int(cyan[0]) + 60)
        self.assertLess(abs(int(plain[0]) - int(plain[2])), 5)

    def test_preview_without_original_is_unchanged(self):
        from src.heightmap.water_level import render_preview

        heights = _ramp(0, 100, rows=60, cols=60)
        a = np.array(render_preview(heights, 10.0, 0.0, 100.0))
        b = np.array(render_preview(heights, 10.0, 0.0, 100.0, original_heightmap=None))
        np.testing.assert_array_equal(a, b)


class DialogWiringTest(unittest.TestCase):

    def setUp(self):
        self.dialog = (ROOT / "src" / "gui" / "heightmap_dialog.py").read_text(encoding="utf-8")

    def test_dialog_uses_the_shared_functions(self):
        self.assertIn("from src.heightmap.height_clipping import", self.dialog)
        self.assertIn("apply_height_window(", self.dialog)
        self.assertIn("describe_report(", self.dialog)
        self.assertIn("limit_warning(", self.dialog)
        self.assertIn("original_heightmap=", self.dialog)

    def test_export_writes_the_same_array_as_the_preview(self):
        # Beides geht ueber _effective_heightmap()
        self.assertIn("export_heightmap_png(\n                self._effective_heightmap(),", self.dialog)
        self.assertIn("array = self._effective_heightmap()", self.dialog)

    def test_checkbox_is_documented_as_height_window(self):
        self.assertIn('"Höhenfenster begrenzen', self.dialog)

    def test_docs_mention_the_feature(self):
        guide = (ROOT / "src" / "gui" / "heightmap_guide.py").read_text(encoding="utf-8")
        overview = (ROOT / "src" / "gui" / "feature_overview_dialog.py").read_text(encoding="utf-8")
        for text in (guide, overview):
            self.assertIn("Höhenfenster", text)
            self.assertIn("3177", text)
        self.assertIn("Oben kappen", guide)
        self.assertIn("Unten abschneiden", guide)
        self.assertIn("Stauchen", guide)


if __name__ == "__main__":
    unittest.main()
