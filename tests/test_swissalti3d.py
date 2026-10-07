"""swissALTI3D als Hoehenquelle: Umrechnung, Kachelwahl, STAC-Abfrage, Zwischenspeicher, Mosaik, Export."""

import io
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image, TiffImagePlugin

from src.heightmap.dgm1_dem import Dgm1Cancelled, Dgm1Error, Dgm1Mosaic, read_raster_info
from src.heightmap.heightmap_exporter import (
    SOURCE_SWISSALTI3D,
    build_heightmap_array_ex,
)
from src.heightmap.lv95 import LV95_ZONE, SWISS_BOUNDS, latlon_to_lv95, lv95_to_latlon
from src.heightmap import swissalti3d_dem as swiss
from src.tpf2.tpf2_geometry import TPF2Geometry

ROOT = Path(__file__).resolve().parent.parent

E0, N0 = 2655000, 1189000  # Kachel "2655-1189": Suedwest-Ecke in LV95


def _height(east, north):
    return 500.0 + (east - E0) * 0.01 + (north - N0) * 0.02


def tile_bytes(e_ul=E0, n_ul=N0 + 1000, px=2.0, size=500):
    cols = np.arange(size)
    rows = np.arange(size)
    ee, nn = np.meshgrid(e_ul + (cols + 0.5) * px, n_ul - (rows + 0.5) * px)
    arr = _height(ee, nn).astype(np.float32)

    ifd = TiffImagePlugin.ImageFileDirectory_v2()
    ifd[33550] = (px, px, 0.0)
    ifd[33922] = (0.0, 0.0, 0.0, float(e_ul), float(n_ul), 0.0)
    ifd[34735] = (1, 1, 0, 3, 1024, 0, 1, 1, 1025, 0, 1, 1, 3072, 0, 1, 2056)
    ifd[42113] = "-9999"

    buffer = io.BytesIO()
    Image.fromarray(arr, mode="F").save(buffer, format="TIFF", tiffinfo=ifd, compression="tiff_deflate")
    return buffer.getvalue()


class _Selection:
    """Minimale Auswahl mit denselben Eigenschaften wie Selection."""

    def __init__(self, east, north, width_m, height_m, rotation_deg=0.0):
        lat, lon = lv95_to_latlon(east, north)
        self.center = (float(lat), float(lon))
        self.width_m = width_m
        self.height_m = height_m
        self.rotation_deg = rotation_deg

    def corners_latlon(self):
        geo = TPF2Geometry(self.center[0], self.center[1], self.rotation_deg)
        hx, hy = self.width_m / 2, self.height_m / 2
        return [geo.inverse(x, y) for x, y in ((-hx, -hy), (hx, -hy), (hx, hy), (-hx, hy))]


def stac_item(year, ie, inn):
    folder = f"https://data.geo.admin.ch/ch.swisstopo.swissalti3d/swissalti3d_{year}_{ie}-{inn}/"
    stem = f"swissalti3d_{year}_{ie}-{inn}"
    return {
        "id": stem,
        "assets": {
            f"{stem}_0.5_2056_5728.tif": {"href": folder + f"{stem}_0.5_2056_5728.tif", "eo:gsd": 0.5},
            f"{stem}_0.5_2056_5728.xyz.zip": {"href": folder + f"{stem}_0.5_2056_5728.xyz.zip", "eo:gsd": 0.5},
            f"{stem}_2_2056_5728.tif": {"href": folder + f"{stem}_2_2056_5728.tif", "eo:gsd": 2.0},
            f"{stem}_2_2056_5728.xyz.zip": {"href": folder + f"{stem}_2_2056_5728.xyz.zip", "eo:gsd": 2.0},
        },
    }


class _Response:
    def __init__(self, status=200, body=None, content=b""):
        self.status_code = status
        self._body = body
        self.content = content

    def json(self):
        return self._body


class _Session:
    """Ersatz fuer requests.Session: STAC-Antworten und Kacheln aus dem Speicher."""

    def __init__(self, items=(), pages=None):
        self.items = list(items)
        self.pages = pages
        self.calls = []

    def get(self, url, params=None, timeout=None):
        self.calls.append((url, params))

        if url.startswith(swiss.STAC_ITEMS_URL):
            if self.pages is not None:
                return _Response(200, self.pages[len(self.calls) - 1])
            return _Response(200, {"features": self.items, "links": []})

        if url.endswith("_2_2056_5728.tif"):
            return _Response(200, content=tile_bytes())

        return _Response(404)


class LV95Test(unittest.TestCase):

    def test_bern_reference_point(self):
        east, north = latlon_to_lv95(46.951082877, 7.438632495)
        self.assertAlmostEqual(float(east), 2600000.0, delta=0.5)
        self.assertAlmostEqual(float(north), 1200000.0, delta=0.5)

    def test_round_trip_is_exact(self):
        lat, lon = np.meshgrid(np.linspace(45.8, 47.8, 25), np.linspace(6.0, 10.4, 40))
        east, north = latlon_to_lv95(lat, lon)
        lat2, lon2 = lv95_to_latlon(east, north)
        self.assertLess(float(np.max(np.abs(lat2 - lat))), 1e-8)
        self.assertLess(float(np.max(np.abs(lon2 - lon))), 1e-8)

    def test_directions(self):
        e1, n1 = latlon_to_lv95(47.0, 8.0)
        e2, n2 = latlon_to_lv95(47.0, 8.1)
        e3, n3 = latlon_to_lv95(47.1, 8.0)
        self.assertGreater(float(e2), float(e1))
        self.assertGreater(float(n3), float(n1))

    def test_bounds_cover_country(self):
        lat_min, lat_max, lon_min, lon_max = SWISS_BOUNDS
        for lat, lon in ((46.95, 7.44), (47.38, 8.54), (46.2, 6.14), (46.85, 9.53), (47.17, 9.5)):
            self.assertTrue(lat_min <= lat <= lat_max and lon_min <= lon <= lon_max)


class TileSelectionTest(unittest.TestCase):

    def test_small_selection_needs_one_tile(self):
        selection = _Selection(E0 + 500, N0 + 500, 400, 400)
        self.assertEqual(swiss.required_swiss_tiles(selection), [(LV95_ZONE, 2655, 1189)])

    def test_rotated_band_needs_only_touched_tiles(self):
        selection = _Selection(E0 + 500, N0 + 500, 2000, 12000, rotation_deg=30.0)
        tiles = swiss.required_swiss_tiles(selection)
        self.assertGreater(len(tiles), 20)
        self.assertLess(len(tiles), 12 * 14)  # weniger als die ganze Bounding-Box
        self.assertTrue(all(zone == LV95_ZONE for zone, _e, _n in tiles))

    def test_blocks_cover_tiles(self):
        tiles = [(LV95_ZONE, 2655, 1189), (LV95_ZONE, 2678, 1189)]
        blocks = swiss.tile_blocks(tiles)
        self.assertEqual(len(blocks), 2)
        for lon_min, lat_min, lon_max, lat_max in blocks:
            self.assertLess(lon_min, lon_max)
            self.assertLess(lat_min, lat_max)
            self.assertTrue(45.5 < lat_min < 48 and 5.5 < lon_min < 10.8)


class StacTest(unittest.TestCase):

    def test_parse_item_prefers_two_meter_tif(self):
        year, ie, inn, href, resolution = swiss.parse_item(stac_item(2022, 2655, 1189))
        self.assertEqual((year, ie, inn, resolution), (2022, 2655, 1189, 2.0))
        self.assertTrue(href.endswith("swissalti3d_2022_2655-1189_2_2056_5728.tif"))

    def test_parse_item_falls_back_to_half_meter(self):
        item = stac_item(2019, 2600, 1200)
        for key in [k for k in item["assets"] if "_2_2056_" in k]:
            del item["assets"][key]
        parsed = swiss.parse_item(item)
        self.assertEqual(parsed[4], 0.5)
        self.assertTrue(parsed[3].endswith("_0.5_2056_5728.tif"))

    def test_parse_item_ignores_other_entries(self):
        self.assertIsNone(swiss.parse_item({"id": "swissalti3d_irgendwas", "assets": {}}))
        self.assertIsNone(swiss.parse_item({"id": "swissalti3d_2022_2655-1189", "assets": {"a.xyz.zip": {"href": "x"}}}))

    def test_latest_year_wins(self):
        result = swiss.pick_latest([stac_item(2019, 2655, 1189), stac_item(2022, 2655, 1189), stac_item(2020, 2656, 1189)])
        self.assertEqual(result[(2655, 1189)][0], 2022)
        self.assertEqual(result[(2656, 1189)][0], 2020)

    def test_pagination_is_followed(self):
        pages = [
            {"features": [stac_item(2022, 2655, 1189)], "links": [{"rel": "next", "href": swiss.STAC_ITEMS_URL + "?cursor=2"}]},
            {"features": [stac_item(2022, 2656, 1189)], "links": []},
        ]
        session = _Session(pages=pages)
        items = swiss.query_items(session, (8.0, 47.0, 8.1, 47.1))
        self.assertEqual(len(items), 2)
        self.assertEqual(len(session.calls), 2)
        first_params = session.calls[0][1]
        self.assertEqual(first_params["limit"], 100)
        self.assertEqual(first_params["bbox"].count(","), 3)
        self.assertIsNone(session.calls[1][1])


class FetchTest(unittest.TestCase):

    def test_fetch_and_cache(self):
        selection = _Selection(E0 + 500, N0 + 500, 400, 400)
        session = _Session(items=[stac_item(2022, 2655, 1189)])

        with tempfile.TemporaryDirectory() as folder:
            cache = Path(folder)
            progress = []

            summary = swiss.fetch_tiles_for_selection(
                selection, cache, progress=lambda d, t, text: progress.append((d, t, text)),
                session=session, sleep=lambda _s: None,
            )

            self.assertEqual((summary.total, summary.fetched, summary.no_data, summary.already_cached), (1, 1, 0, 0))
            self.assertTrue((cache / "2056_2655_1189__swisstopo.tif").exists())
            meta = (cache / "2056_2655_1189__swisstopo.json").read_text(encoding="utf-8")
            self.assertIn("swisstopo", meta)
            self.assertIn("swissALTI3D", meta)
            self.assertEqual(progress[-1][2], "Fertig")

            # zweiter Lauf: alles im Zwischenspeicher, kein Netzwerk
            session2 = _Session(items=[])
            summary2 = swiss.fetch_tiles_for_selection(selection, cache, session=session2, sleep=lambda _s: None)
            self.assertEqual(summary2.already_cached, 1)
            self.assertEqual(session2.calls, [])

    def test_missing_tile_is_remembered(self):
        selection = _Selection(E0 + 500, N0 + 500, 400, 400)

        with tempfile.TemporaryDirectory() as folder:
            cache = Path(folder)
            summary = swiss.fetch_tiles_for_selection(
                selection, cache, session=_Session(items=[]), sleep=lambda _s: None
            )
            self.assertEqual((summary.fetched, summary.no_data), (0, 1))
            self.assertTrue((cache / "2056_2655_1189.none").exists())

            session2 = _Session(items=[])
            swiss.fetch_tiles_for_selection(selection, cache, session=session2, sleep=lambda _s: None)
            self.assertEqual(session2.calls, [])

    def test_cancel(self):
        selection = _Selection(E0 + 500, N0 + 500, 400, 400)

        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(Dgm1Cancelled):
                swiss.fetch_tiles_for_selection(
                    selection, Path(folder), cancelled=lambda: True,
                    session=_Session(items=[stac_item(2022, 2655, 1189)]), sleep=lambda _s: None,
                )

    def test_tiny_answer_is_an_error(self):
        selection = _Selection(E0 + 500, N0 + 500, 400, 400)

        class Tiny(_Session):
            def get(self, url, params=None, timeout=None):
                if url.endswith(".tif"):
                    return _Response(200, content=b"x")
                return super().get(url, params, timeout)

        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(Dgm1Error):
                swiss.fetch_tiles_for_selection(
                    selection, Path(folder), session=Tiny(items=[stac_item(2022, 2655, 1189)]), sleep=lambda _s: None
                )


class MosaicAndExportTest(unittest.TestCase):

    def _cache_with_tile(self, folder):
        cache = Path(folder)
        swiss.store_tile(cache, 2655, 1189, tile_bytes(), 2022, "https://example/tile.tif")
        return cache

    def test_reader_understands_swiss_tile(self):
        with tempfile.TemporaryDirectory() as folder:
            cache = self._cache_with_tile(folder)
            info = read_raster_info(cache / "2056_2655_1189__swisstopo.tif")
            self.assertEqual(info.zone, LV95_ZONE)
            self.assertEqual((info.e_ul, info.n_ul, info.px), (float(E0), float(N0 + 1000), 2.0))

    def test_mosaic_heights_match_the_source(self):
        selection = _Selection(E0 + 500, N0 + 500, 400, 400)

        with tempfile.TemporaryDirectory() as folder:
            cache = self._cache_with_tile(folder)
            mosaic = Dgm1Mosaic.from_cache(selection, cache, 4.0, tiles=swiss.required_swiss_tiles(selection))
            self.assertEqual(mosaic.slot_count, 1)
            self.assertEqual(mosaic.missing_slots, 0)
            self.assertIn(swiss.ATTRIBUTION, mosaic.attributions)

            east = np.array([E0 + 300.0, E0 + 500.0, E0 + 700.0])
            north = np.array([N0 + 400.0, N0 + 500.0, N0 + 650.0])
            lat, lon = lv95_to_latlon(east, north)
            values = mosaic.sample_grid(lat, lon)

            self.assertTrue(np.allclose(values, _height(east, north), atol=0.5), values)

    def test_export_with_swiss_source(self):
        selection = _Selection(E0 + 500, N0 + 500, 400, 400)

        with tempfile.TemporaryDirectory() as folder:
            cache = self._cache_with_tile(folder)
            array, info = build_heightmap_array_ex(
                selection, Path(folder) / "dem", SOURCE_SWISSALTI3D, swiss_cache_dir=cache
            )

        self.assertEqual(array.shape, (101, 101))
        self.assertEqual(info.source, SOURCE_SWISSALTI3D)
        self.assertEqual(info.missing_tiles, 0)
        self.assertIn(swiss.ATTRIBUTION, info.attributions)
        self.assertTrue(500.0 < float(array.min()) < float(array.max()) < 540.0)

    def test_export_without_tiles_explains_the_problem(self):
        selection = _Selection(E0 + 500, N0 + 500, 400, 400)

        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(Dgm1Error) as ctx:
                build_heightmap_array_ex(selection, Path(folder), SOURCE_SWISSALTI3D, swiss_cache_dir=Path(folder))

        self.assertIn("swissALTI3D", str(ctx.exception))

    def test_german_utm_path_is_unchanged(self):
        from src.heightmap.dgm1_dem import required_dgm1_tiles

        selection = type("S", (), {})()
        selection.center = (51.34, 12.37)
        geo = TPF2Geometry(51.34, 12.37, 0.0)
        corners = [geo.inverse(x, y) for x, y in ((-200, -200), (200, -200), (200, 200), (-200, 200))]
        selection.corners_latlon = lambda: corners

        tiles = required_dgm1_tiles(selection)
        self.assertTrue(tiles)
        self.assertTrue(all(zone == 33 for zone, _e, _n in tiles))


class DialogWiringTest(unittest.TestCase):

    def test_dialog_offers_swiss_source(self):
        source = (ROOT / "src" / "gui" / "heightmap_dialog.py").read_text(encoding="utf-8")
        for needle in ("SOURCE_SWISSALTI3D", "SwissFetchJob", "SWISS_BOUNDS", "DEFAULT_SWISS_CACHE_DIR",
                       "swissALTI3D Schweiz (2 m, über data.geo.admin.ch)", "swiss_cache_dir=DEFAULT_SWISS_CACHE_DIR"):
            self.assertIn(needle, source, needle)
        # Import, Liste der Quellen im Dialog und Voreinstellung "wie DGM1"
        self.assertIn("    SOURCE_SWISSALTI3D,\n    build_heightmap_array,", source)
        self.assertIn("            SOURCE_SWISSALTI3D,\n        )[self.source_combo.currentIndex()]", source)
        self.assertIn("dgm1 = source in (SOURCE_DGM1_DE, SOURCE_DGM1_FOLDER, SOURCE_SWISSALTI3D)", source)

    def test_attribution_names_the_owner(self):
        self.assertIn("swisstopo", swiss.ATTRIBUTION)
        self.assertIn("Bundesamt für Landestopografie", swiss.ATTRIBUTION)


if __name__ == "__main__":
    unittest.main()
