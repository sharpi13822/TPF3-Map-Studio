"""Tests fuer das Kombinieren mehrerer Hoehenquellen (src/heightmap/source_combine.py)."""

import unittest
from types import SimpleNamespace
from unittest import mock

import numpy as np

from src.core.export_settings import sanitize_export_settings
from src.heightmap import heightmap_exporter as hx
from src.heightmap.heightmap_exporter import (
    SOURCE_COPERNICUS,
    SOURCE_DGM1_DE,
    SOURCE_LUX,
    SOURCE_TPF2_PNG,
    HeightmapBuildInfo,
)
from src.heightmap.source_combine import (
    build_heightmap_array_multi,
    combine_layers,
    combined_summary,
    source_shares,
    touches,
)


def _links_rechts(shape=(40, 100), grenze=50, links=100.0, rechts=100.0):
    """Zwei Quellen: A hat nur die linke, B nur die rechte Haelfte (mit Ueberlappung)."""
    a = np.full(shape, np.nan)
    b = np.full(shape, np.nan)
    a[:, :grenze + 10] = links
    b[:, grenze - 10:] = rechts
    return a, b


class CombineLayersTests(unittest.TestCase):

    def test_eine_quelle_bleibt_unveraendert(self):
        a = np.arange(12, dtype=float).reshape(3, 4)
        out, used, offsets = combine_layers([a])
        np.testing.assert_allclose(out, a)
        self.assertTrue((used == 0).all())
        self.assertEqual(offsets, [0.0])

    def test_oberste_quelle_hat_vorrang(self):
        a = np.full((10, 10), 5.0)
        b = np.full((10, 10), 7.0)
        out, used, _ = combine_layers([a, b], blend_m=0, max_offset_m=0)
        np.testing.assert_allclose(out, 5.0)
        self.assertTrue((used == 0).all())

    def test_luecke_wird_aus_naechster_quelle_gefuellt(self):
        a = np.full((10, 10), 5.0)
        a[:, 6:] = np.nan
        b = np.full((10, 10), 5.0)
        out, used, _ = combine_layers([a, b], blend_m=0)
        self.assertFalse(np.isnan(out).any())
        self.assertTrue((used[:, 6:] == 1).all())
        self.assertTrue((used[:, :6] == 0).all())

    def test_hoehenversatz_wird_ausgeglichen(self):
        # B liegt 1,5 m hoeher (anderes Bezugssystem): nach dem Kombinieren keine Stufe
        a, b = _links_rechts(links=200.0, rechts=201.5)
        out, _, offsets = combine_layers([a, b], pixel_m=4.0, blend_m=0)
        np.testing.assert_allclose(out, 200.0, atol=1e-4)
        self.assertAlmostEqual(offsets[0], 0.0)
        self.assertAlmostEqual(offsets[1], -1.5, places=4)

    def test_zu_grosser_versatz_wird_nicht_verschoben(self):
        a, b = _links_rechts(links=200.0, rechts=300.0)
        _, _, offsets = combine_layers([a, b], blend_m=0, max_offset_m=30.0)
        self.assertEqual(offsets[1], 0.0)

    def test_weiche_naht_ohne_spruenge(self):
        # A = 100 m, B = 110 m, Hoehenausgleich aus: an der Naht ein sanfter Uebergang
        shape = (20, 200)
        a = np.full(shape, np.nan)
        a[:, :120] = 100.0
        b = np.full(shape, 110.0)
        out, _, _ = combine_layers([a, b], pixel_m=4.0, blend_m=200.0, max_offset_m=0.0)
        row = out[5].astype(float)
        self.assertAlmostEqual(row[10], 100.0, places=4)    # weit innen: Quelle A
        self.assertAlmostEqual(row[150], 110.0, places=4)   # ausserhalb A: Quelle B
        self.assertTrue(100.0 < row[110] < 110.0)           # in der Naht dazwischen
        steps = np.diff(row)
        self.assertTrue((steps >= -1e-5).all())             # stetig ansteigend
        self.assertLess(steps.max(), 0.5)                   # keine Stufe (10 m auf 50 Pixel)

    def test_drei_quellen_reihenfolge(self):
        a = np.full((10, 30), np.nan)
        b = np.full((10, 30), np.nan)
        c = np.full((10, 30), 0.0)
        a[:, :10] = 0.0
        b[:, 5:20] = 0.0
        _, used, _ = combine_layers([a, b, c], blend_m=0)
        self.assertTrue((used[:, :10] == 0).all())
        self.assertTrue((used[:, 10:20] == 1).all())
        self.assertTrue((used[:, 20:] == 2).all())

    def test_ohne_daten_bleibt_nan(self):
        a = np.full((4, 4), np.nan)
        b = np.full((4, 4), np.nan)
        b[0, 0] = 1.0
        out, used, _ = combine_layers([a, b])
        self.assertTrue(np.isnan(out[1, 1]))
        self.assertEqual(int(used[1, 1]), -1)

    def test_unterschiedliche_groessen(self):
        with self.assertRaises(ValueError):
            combine_layers([np.zeros((2, 2)), np.zeros((3, 3))])

    def test_anteile(self):
        used = np.array([[0, 0, 1, -1]], dtype=np.int8)
        self.assertEqual(source_shares(used, 2), [0.5, 0.25])


class TouchesTests(unittest.TestCase):

    def test_beruehrt_und_daneben(self):
        ecken = [(49.6, 6.3), (49.6, 6.6), (49.8, 6.6), (49.8, 6.3)]
        lux = (49.44, 50.19, 5.73, 6.53)
        self.assertTrue(touches(ecken, lux))
        self.assertTrue(touches(ecken, None))
        weit_weg = [(52.0, 13.0), (52.0, 13.5), (52.5, 13.5), (52.5, 13.0)]
        self.assertFalse(touches(weit_weg, lux))


class ExportSettingsTests(unittest.TestCase):

    def test_quellenliste_wird_bereinigt(self):
        raw = {"combine_sources": ["lux_mnt", "", 5, "lux_mnt", "copernicus", "x"], "combine_blend": 5000}
        cleaned = sanitize_export_settings(raw)
        self.assertEqual(cleaned["combine_sources"], ["lux_mnt", "copernicus"])
        self.assertEqual(cleaned["combine_blend"], 1000.0)

    def test_falsche_typen(self):
        cleaned = sanitize_export_settings({"combine_sources": "lux_mnt", "combine_blend": True})
        self.assertNotIn("combine_sources", cleaned)
        self.assertNotIn("combine_blend", cleaned)


class MultiBuildTests(unittest.TestCase):

    def setUp(self):
        self.selection = SimpleNamespace(scale_factor=1.0, height_scale=1.0)
        self.calls = []

    def _fake_ex(self, layers):
        def fake(selection, cache_dir, source, control=None, raw=False, **kwargs):
            self.calls.append(source)
            arr = layers[source]
            info = HeightmapBuildInfo(source=source, attributions=[f"Quelle {source}"])
            if source == SOURCE_COPERNICUS:
                info.sea_mask = np.zeros(arr.shape, dtype=bool)
            return np.array(arr, dtype=np.float32), info
        return fake

    def _run(self, sources, layers, **kw):
        with mock.patch.object(hx, "build_heightmap_array_ex", self._fake_ex(layers)), \
                mock.patch.object(hx, "_apply_height_scale", lambda a, s: a):
            return build_heightmap_array_multi(self.selection, None, sources, **kw)

    def test_copernicus_ergaenzt_restliche_luecken(self):
        dgm = np.full((10, 10), 50.0)
        dgm[:, 7:] = np.nan
        lux = np.full((10, 10), np.nan)
        lux[:, 4:9] = 50.0
        cop = np.full((10, 10), 50.0)
        out, info = self._run(
            [SOURCE_DGM1_DE, SOURCE_LUX],
            {SOURCE_DGM1_DE: dgm, SOURCE_LUX: lux, SOURCE_COPERNICUS: cop},
            blend_m=0,
        )
        self.assertFalse(np.isnan(out).any())
        self.assertEqual(info.combined, [SOURCE_DGM1_DE, SOURCE_LUX, SOURCE_COPERNICUS])
        self.assertAlmostEqual(sum(info.shares), 1.0)
        self.assertAlmostEqual(info.fallback_fraction, 0.1)
        self.assertEqual(info.source, SOURCE_DGM1_DE)
        self.assertIn("Quelle lux_mnt", info.attributions)

    def test_ohne_luecken_kein_copernicus(self):
        dgm = np.full((5, 5), 1.0)
        lux = np.full((5, 5), 1.0)
        _, info = self._run(
            [SOURCE_DGM1_DE, SOURCE_LUX],
            {SOURCE_DGM1_DE: dgm, SOURCE_LUX: lux},
        )
        self.assertNotIn(SOURCE_COPERNICUS, self.calls)
        self.assertEqual(info.fallback_fraction, 0.0)

    def test_doppelte_quellen_werden_ignoriert(self):
        dgm = np.full((5, 5), 1.0)
        self._run([SOURCE_DGM1_DE, SOURCE_DGM1_DE], {SOURCE_DGM1_DE: dgm})
        self.assertEqual(self.calls, [SOURCE_DGM1_DE])

    def test_tpf2_png_und_zu_viele(self):
        with self.assertRaises(ValueError):
            self._run([SOURCE_DGM1_DE, SOURCE_TPF2_PNG], {})
        with self.assertRaises(ValueError):
            self._run(["a", "b", "c", "d"], {})

    def test_zusammenfassung(self):
        info = HeightmapBuildInfo(combined=[SOURCE_DGM1_DE, SOURCE_LUX], shares=[0.625, 0.375])
        with mock.patch("src.i18n.get_language", return_value="de"):
            self.assertEqual(combined_summary(info), "DGM1 62,5 %, MNT Luxemburg 37,5 %")


class RawModeTests(unittest.TestCase):

    def test_raw_ohne_kacheln_gibt_nan_statt_fehler(self):
        selection = SimpleNamespace(width_m=40.0, height_m=40.0)
        leer = SimpleNamespace(slot_count=0)
        with mock.patch.object(hx, "pixel_size_for_selection", return_value=(10, 10)), \
                mock.patch.object(hx.LuxMosaic, "from_cache", return_value=leer):
            out, info = hx.build_heightmap_array_ex(
                selection, None, SOURCE_LUX, lux_cache_dir="x", raw=True
            )
        self.assertTrue(np.isnan(out).all())
        self.assertEqual(info.fallback_fraction, 1.0)


if __name__ == "__main__":
    unittest.main()


class ShareDescriptionTests(unittest.TestCase):

    def test_kombinierte_quellen_mit_lizenzen(self):
        from src import share_description as sd

        selection = SimpleNamespace(
            width_m=4000.0, height_m=4000.0, is_scaled=False,
            scale_factor=1.0, height_scale=1.0,
        )
        info = HeightmapBuildInfo(
            source=SOURCE_DGM1_DE,
            attributions=["GeoBasis-DE / LVermGeoRP", sd.LUX_ATTRIBUTION],
            combined=[SOURCE_DGM1_DE, SOURCE_LUX],
            shares=[0.6, 0.4],
        )
        with mock.patch.object(sd, "pixel_size_for_selection", return_value=(1000, 1000)), \
                mock.patch.object(sd, "find_by_pixels", return_value=[]):
            rows = sd.collect_rows(
                selection, info, range_min_m=0, range_max_m=500, water_level_m=60,
                osm_used=False,
            )
        werte = {}
        for label, value, _url in rows:
            werte.setdefault(label, []).append(value)
        quelle = [v for k, vs in werte.items() for v in vs if "60" in v and "MNT Luxemburg" in v]
        self.assertTrue(quelle, rows)
        angaben = " ".join(v for k, vs in werte.items() for v in vs)
        self.assertIn(sd.LUX_ATTRIBUTION, angaben)
        self.assertIn("GeoBasis-DE / LVermGeoRP", angaben)
        # DGM1-Zeile ohne die Luxemburger Angabe doppelt
        dgm_zeilen = [v for vs in werte.values() for v in vs if "GeoBasis-DE" in v]
        self.assertTrue(all(sd.LUX_ATTRIBUTION not in v for v in dgm_zeilen))


class BevShareTests(unittest.TestCase):

    def test_bev_mit_name_und_lizenz(self):
        from src import share_description as sd
        from src.heightmap.heightmap_exporter import SOURCE_BEV_AT

        selection = SimpleNamespace(
            width_m=4000.0, height_m=4000.0, is_scaled=False,
            scale_factor=1.0, height_scale=1.0,
        )
        info = HeightmapBuildInfo(source=SOURCE_BEV_AT, attributions=[sd.BEV_ATTRIBUTION])
        with mock.patch.object(sd, "pixel_size_for_selection", return_value=(1000, 1000)), \
                mock.patch.object(sd, "find_by_pixels", return_value=[]), \
                mock.patch.object(sd, "_lang", "de"):
            rows = sd.collect_rows(
                selection, info, range_min_m=0, range_max_m=500, water_level_m=60,
                osm_used=False,
            )
        werte = {label: value for label, value, _url in rows}
        self.assertEqual(werte["Höhenquelle"], "BEV Österreich (1 m)")
        alle = " ".join(v for _l, v, _u in rows)
        self.assertIn(sd.BEV_ATTRIBUTION, alle)
        self.assertIn("CC BY 4.0", alle)
        self.assertNotIn("Copernicus DEM", alle)


class PriorityOrderTests(unittest.TestCase):

    def test_copernicus_immer_zuletzt(self):
        from src.heightmap.source_combine import priority_order
        self.assertEqual(
            priority_order([SOURCE_COPERNICUS, SOURCE_DGM1_DE, SOURCE_LUX, SOURCE_DGM1_DE]),
            [SOURCE_DGM1_DE, SOURCE_LUX, SOURCE_COPERNICUS],
        )


class MinShareTests(unittest.TestCase):

    def test_winzige_anteile_werden_nicht_genannt(self):
        info = HeightmapBuildInfo(
            combined=[SOURCE_DGM1_DE, SOURCE_LUX, SOURCE_COPERNICUS],
            shares=[0.812, 0.18799, 0.00001],
        )
        with mock.patch("src.i18n.get_language", return_value="de"):
            text = combined_summary(info)
        self.assertIn("MNT Luxemburg", text)
        self.assertNotIn("Copernicus", text)
