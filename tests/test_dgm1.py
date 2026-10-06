"""Tests fuer die DGM1-Hoehenquelle (utm.py, dgm1_dem.py, Quellenwahl im Exporter).

Alles mit kuenstlichen GeoTIFF-Kacheln und einem nachgebauten Webdienst, ohne Netzwerk.
"""

import base64
import io
import json
import math
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
from PIL import Image, TiffImagePlugin

from src.heightmap import dgm1_dem as dd
from src.heightmap import heightmap_exporter as he
from src.heightmap import utm
from src.tpf2.tpf2_geometry import TPF2Geometry


class FakeSelection:
    """Kartenband wie Selection (center, rotation_deg, width_m, height_m, corners_latlon)."""

    def __init__(self, lat, lon, width_m, height_m, rotation_deg=0.0):
        self.center = (lat, lon)
        self.width_m = width_m
        self.height_m = height_m
        self.rotation_deg = rotation_deg

    def corners_latlon(self):
        g = TPF2Geometry(self.center[0], self.center[1], self.rotation_deg)
        hx, hy = self.width_m / 2, self.height_m / 2
        out = []
        for x, y in ((-hx, hy), (hx, hy), (hx, -hy), (-hx, -hy)):
            e = g.right_vector[0] * x + g.up_vector[0] * y
            n = g.right_vector[1] * x + g.up_vector[1] * y
            out.append((
                self.center[0] + n / g.METERS_PER_DEGREE_LAT,
                self.center[1] + e / g.longitude_scale,
            ))
        return out


def write_geotiff(path, array, e_ul, n_ul, px=1.0, epsg=25832, point=False,
                  nodata=None, compression=None):
    """Schreibt ein float32-GeoTIFF mit den Tags, die read_raster_info erwartet."""

    ifd = TiffImagePlugin.ImageFileDirectory_v2()
    ifd[33550] = (px, px, 0.0)
    ifd.tagtype[33550] = 12
    off = px / 2.0 if point else 0.0
    ifd[33922] = (0.0, 0.0, 0.0, e_ul + off, n_ul - off, 0.0)
    ifd.tagtype[33922] = 12
    ifd[34735] = (1, 1, 0, 2, 1025, 0, 1, 2 if point else 1, 3072, 0, 1, epsg)
    ifd.tagtype[34735] = 3
    if nodata is not None:
        ifd[42113] = str(nodata)
        ifd.tagtype[42113] = 2
    im = Image.fromarray(np.asarray(array, dtype=np.float32), mode="F")
    kwargs = {"tiffinfo": ifd}
    if compression:
        kwargs["compression"] = compression
    im.save(path, **kwargs)


def plane(e0, n_top, size_px, px=1.0, base=100.0, se=0.01, sn=0.02):
    """Hoehe = base + se*(E-500000) + sn*(N-5500000), an den Pixelmitten."""

    cols = (np.arange(size_px) + 0.5) * px
    rows = (np.arange(size_px) + 0.5) * px
    e = e0 + cols[None, :]
    n = n_top - rows[:, None]
    return (base + se * (e - 500000.0) + sn * (n - 5500000.0)).astype(np.float32)


def plane_at(e, n, base=100.0, se=0.01, sn=0.02):
    return base + se * (e - 500000.0) + sn * (n - 5500000.0)


class UtmTests(unittest.TestCase):

    def test_known_value_and_roundtrip(self):
        e, n = utm.latlon_to_utm(50.0, 9.0, 32)
        self.assertAlmostEqual(float(e), 500000.0, places=3)
        self.assertAlmostEqual(float(n), 5538630.70, delta=0.02)

        for lat, lon, zone in ((50.35, 7.59, 32), (52.5, 13.4, 33), (47.5, 6.2, 32)):
            e, n = utm.latlon_to_utm(lat, lon, zone)
            la, lo = utm.utm_to_latlon(e, n, zone)
            self.assertAlmostEqual(float(la), lat, places=9)
            self.assertAlmostEqual(float(lo), lon, places=9)

    def test_zone_for_lon(self):
        self.assertEqual(utm.zone_for_lon(7.6), 32)
        self.assertEqual(utm.zone_for_lon(11.99), 32)
        self.assertEqual(utm.zone_for_lon(13.4), 33)


class RequiredTilesTests(unittest.TestCase):

    def test_small_selection(self):
        sel = FakeSelection(50.35, 7.59, 3000, 2000)
        tiles = dd.required_dgm1_tiles(sel)
        zones = {t[0] for t in tiles}
        self.assertEqual(zones, {32})
        self.assertGreaterEqual(len(tiles), 6)
        self.assertLessEqual(len(tiles), 20)

    def test_rotated_band_needs_far_fewer_tiles_than_bounding_box(self):
        sel = FakeSelection(50.2, 7.7, 10752, 53760, rotation_deg=45.0)
        tiles = dd.required_dgm1_tiles(sel)
        es = [t[1] for t in tiles]
        ns = [t[2] for t in tiles]
        bbox = (max(es) - min(es) + 1) * (max(ns) - min(ns) + 1)
        self.assertLess(len(tiles), bbox * 0.5)
        # ungefaehr Flaeche in km2 plus Rand
        self.assertGreater(len(tiles), 570)
        self.assertLess(len(tiles), 800)

    def test_every_pixel_centre_lies_in_a_required_tile(self):
        sel = FakeSelection(50.2, 7.7, 6000, 14000, rotation_deg=30.0)
        wanted = set(dd.required_dgm1_tiles(sel))
        g = TPF2Geometry(50.2, 7.7, 30.0)
        for x in np.linspace(-3000, 3000, 25):
            for y in np.linspace(-7000, 7000, 57):
                e = g.right_vector[0] * x + g.up_vector[0] * y
                n = g.right_vector[1] * x + g.up_vector[1] * y
                lat = 50.2 + n / g.METERS_PER_DEGREE_LAT
                lon = 7.7 + e / g.longitude_scale
                ue, un = utm.latlon_to_utm(lat, lon, 32)
                self.assertIn((32, int(ue // 1000), int(un // 1000)), wanted)


class GeoTiffTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_reads_georeference_zone_and_nodata(self):
        arr = plane(497000, 5671000, 1000)
        arr[0, 0] = -9999
        p = self.dir / "t.tif"
        write_geotiff(p, arr, 497000, 5671000, nodata=-9999)
        info = dd.read_raster_info(p)
        self.assertEqual((info.zone, info.e_ul, info.n_ul, info.px), (32, 497000.0, 5671000.0, 1.0))
        a = dd.read_raster_array(info)
        self.assertTrue(np.isnan(a[0, 0]))
        self.assertFalse(np.isnan(a[5, 5]))

    def test_zone_33_and_pixel_is_point(self):
        p = self.dir / "t.tif"
        write_geotiff(p, plane(400000, 5800000, 1000), 400000, 5800000, epsg=25833, point=True)
        info = dd.read_raster_info(p)
        self.assertEqual(info.zone, 33)
        self.assertAlmostEqual(info.e_ul, 400000.0)
        self.assertAlmostEqual(info.n_ul, 5800000.0)

    def test_transformation_matrix_instead_of_tiepoint(self):
        p = self.dir / "m.tif"
        ifd = TiffImagePlugin.ImageFileDirectory_v2()
        ifd[34264] = (1.0, 0, 0, 497000.0, 0, -1.0, 0, 5671000.0, 0, 0, 0, 0, 0, 0, 0, 1.0)
        ifd.tagtype[34264] = 12
        ifd[34735] = (1, 1, 0, 1, 3072, 0, 1, 25832)
        ifd.tagtype[34735] = 3
        Image.fromarray(plane(497000, 5671000, 1000), mode="F").save(p, tiffinfo=ifd)
        info = dd.read_raster_info(p)
        self.assertEqual((info.zone, info.e_ul, info.n_ul, info.px), (32, 497000.0, 5671000.0, 1.0))

    def test_file_without_georeference_is_rejected_with_clear_error(self):
        p = self.dir / "plain.tif"
        Image.fromarray(plane(497000, 5671000, 100), mode="F").save(p)
        with self.assertRaises(dd.Dgm1Error) as ctx:
            dd.read_raster_info(p)
        self.assertIn("Georeferenzierung", str(ctx.exception))

    def test_compressed_float_tiles_are_readable(self):
        for comp in ("tiff_deflate", "tiff_lzw"):
            p = self.dir / f"{comp}.tif"
            arr = plane(497000, 5671000, 1000)
            write_geotiff(p, arr, 497000, 5671000, compression=comp)
            got = dd.read_raster_array(dd.read_raster_info(p))
            np.testing.assert_allclose(got, arr, atol=1e-4)

    def test_two_km_tile_becomes_four_slots(self):
        p = self.dir / "big.tif"
        write_geotiff(p, plane(496000, 5672000, 2000), 496000, 5672000)
        slots = dd.slots_from_raster(dd.read_raster_info(p), 4.0)
        self.assertEqual(len(slots), 4)
        self.assertEqual({(s.ie, s.inn) for s in slots}, {(496, 5671), (497, 5671), (496, 5670), (497, 5670)})
        self.assertEqual(slots[0].cells.shape, (250, 250))

    def test_misaligned_tile_is_rejected(self):
        p = self.dir / "bad.tif"
        write_geotiff(p, plane(496500, 5671500, 1000), 496500, 5671500)
        with self.assertRaises(dd.Dgm1Error):
            dd.slots_from_raster(dd.read_raster_info(p), 4.0)

    def test_tile_with_extra_edge_pixel_is_cropped(self):
        p = self.dir / "t1001.tif"
        write_geotiff(p, plane(497000, 5671000, 1001), 497000, 5671000)
        slots = dd.slots_from_raster(dd.read_raster_info(p), 4.0)
        self.assertEqual(len(slots), 1)
        self.assertEqual(slots[0].cells.shape, (250, 250))


class MosaicTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def _write_block(self, e_km, n_km_top, n_cols, n_rows):
        for r in range(n_rows):
            for c in range(n_cols):
                e0 = (e_km + c) * 1000
                n_top = (n_km_top - r) * 1000
                write_geotiff(self.dir / f"k_{e_km + c}_{n_km_top - r}.tif",
                              plane(e0, n_top, 1000), e0, n_top)

    def test_samples_plane_exactly_including_tile_seams(self):
        self._write_block(497, 5672, 3, 3)  # Kacheln 497..499 / 5670..5672
        sel = FakeSelection(50.3, 7.7, 1200, 1200)  # Mitte liegt ungefaehr bei E=397000? -> unten gepruft
        # Auswahl direkt ueber UTM-Punkt in der Blockmitte legen
        lat, lon = utm.utm_to_latlon(498500.0, 5671500.0, 32)
        sel = FakeSelection(float(lat), float(lon), 1500, 1500)
        mosaic = dd.Dgm1Mosaic.from_folder(sel, self.dir, 4.0)
        self.assertGreaterEqual(mosaic.slot_count, 4)

        rng = np.random.default_rng(1)
        es = np.concatenate([rng.uniform(498000, 499000, 400), np.full(50, 498000.0) + rng.uniform(-3, 3, 50)])
        ns = np.concatenate([rng.uniform(5671000, 5672000, 400), rng.uniform(5671000, 5672000, 50)])
        la, lo = utm.utm_to_latlon(es, ns, 32)
        got = mosaic.sample_grid(la, lo)
        self.assertFalse(np.isnan(got).any())
        np.testing.assert_allclose(got, plane_at(es, ns), atol=0.05)

    def test_missing_tiles_give_nan(self):
        self._write_block(497, 5672, 1, 1)
        lat, lon = utm.utm_to_latlon(497500.0, 5671500.0, 32)
        sel = FakeSelection(float(lat), float(lon), 800, 800)
        mosaic = dd.Dgm1Mosaic.from_folder(sel, self.dir, 4.0)
        la, lo = utm.utm_to_latlon(np.array([497500.0, 450000.0]), np.array([5671500.0, 5671500.0]), 32)
        got = mosaic.sample_grid(la, lo)
        self.assertFalse(np.isnan(got[0]))
        self.assertTrue(np.isnan(got[1]))

    def test_state_border_parts_are_merged(self):
        # Zwei Teile derselben Kachel: links gueltig, rechts NaN und umgekehrt
        a = plane(497000, 5671000, 1000); a[:, 500:] = np.nan
        b = plane(497000, 5671000, 1000); b[:, :500] = np.nan
        write_geotiff(self.dir / "32_497_5670__DE-A.tif", a, 497000, 5671000)
        write_geotiff(self.dir / "32_497_5670__DE-B.tif", b, 497000, 5671000)
        lat, lon = utm.utm_to_latlon(497500.0, 5670500.0, 32)
        sel = FakeSelection(float(lat), float(lon), 600, 600)
        mosaic = dd.Dgm1Mosaic.from_cache(sel, self.dir, 4.0)
        es = np.array([497100.0, 497900.0]); ns = np.array([5670500.0, 5670500.0])
        la, lo = utm.utm_to_latlon(es, ns, 32)
        got = mosaic.sample_grid(la, lo)
        self.assertFalse(np.isnan(got).any())
        np.testing.assert_allclose(got, plane_at(es, ns), atol=0.05)


def fake_response(zone, ie, inn, origin="DE-RP", error=False, status=200):
    resp = mock.Mock()
    resp.status_code = status
    resp.headers = {}
    if error:
        resp.json.return_value = {"Attributes": {"IsError": True, "Error": {"Title": "Kein Datensatz"}}}
        return resp
    buf = io.BytesIO()
    tmp = Path(tempfile.mkdtemp()) / "x.tif"
    write_geotiff(tmp, plane(ie * 1000, inn * 1000 + 1000, 1000), ie * 1000, inn * 1000 + 1000)
    raw = tmp.read_bytes()
    resp.json.return_value = {
        "Type": "RawTIFResponse",
        "Attributes": {
            "IsError": False,
            "RawTIFs": [{
                "Data": base64.b64encode(raw).decode(), "DataFormat": "GeoTIFF",
                "Actuality": "2024-03-15", "Origin": origin,
                "Attribution": "(c) GeoBasis-DE / LVermGeoRP, dl-de/by-2-0",
                "TileIndex": f"{zone}_{ie}_{inn}",
            }],
        },
    }
    return resp


class FetchTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_fetch_slot_stores_tile_and_attribution_and_uses_cache(self):
        session = mock.Mock()
        session.post.side_effect = lambda url, json=None, **kw: fake_response(32, 497, 5670)
        self.assertEqual(dd.fetch_slot(32, 497, 5670, self.dir, session=session), 1)
        self.assertEqual(session.post.call_count, 1)
        body = session.post.call_args.kwargs["json"]
        self.assertEqual(body["Type"], "RawTIFRequest")
        self.assertEqual(body["Attributes"], {"Zone": 32, "Easting": 497500.0, "Northing": 5670500.0})
        files = dd.cached_files_for_slot(self.dir, 32, 497, 5670)
        self.assertEqual(len(files), 1)
        meta = json.loads(files[0].with_suffix(".json").read_text(encoding="utf-8"))
        self.assertIn("LVermGeoRP", meta["Attribution"])
        # zweiter Aufruf: kein Netzwerk
        self.assertEqual(dd.fetch_slot(32, 497, 5670, self.dir, session=session), 0)
        self.assertEqual(session.post.call_count, 1)

    def test_error_response_is_remembered_as_no_data(self):
        session = mock.Mock()
        session.post.side_effect = lambda url, json=None, **kw: fake_response(32, 1, 2, error=True)
        self.assertEqual(dd.fetch_slot(32, 100, 200, self.dir, session=session), 0)
        self.assertTrue(dd.slot_is_cached(self.dir, 32, 100, 200))
        dd.fetch_slot(32, 100, 200, self.dir, session=session)
        self.assertEqual(session.post.call_count, 1)

    def test_rate_limit_is_retried(self):
        calls = []

        def post(url, json=None, **kw):
            calls.append(1)
            if len(calls) == 1:
                r = mock.Mock(); r.status_code = 429; r.headers = {"Retry-After": "1"}
                return r
            return fake_response(32, 497, 5670)

        session = mock.Mock(); session.post.side_effect = post
        with mock.patch.object(dd.time, "sleep") as sleep:
            self.assertEqual(dd.fetch_slot(32, 497, 5670, self.dir, session=session), 1)
        self.assertEqual(len(calls), 2)
        self.assertTrue(sleep.called)

    def test_gives_up_after_repeated_server_errors(self):
        session = mock.Mock()
        r = mock.Mock(); r.status_code = 503; r.headers = {}
        session.post.return_value = r
        with mock.patch.object(dd.time, "sleep"):
            with self.assertRaises(dd.Dgm1Error):
                dd.fetch_slot(32, 497, 5670, self.dir, session=session, max_retries=2)

    def test_fetch_for_selection_throttles_and_reports_progress(self):
        lat, lon = utm.utm_to_latlon(497500.0, 5670500.0, 32)
        sel = FakeSelection(float(lat), float(lon), 1500, 1500)
        session = mock.Mock()
        session.post.side_effect = lambda url, json=None, **kw: fake_response(
            json["Attributes"]["Zone"], int(json["Attributes"]["Easting"] // 1000),
            int(json["Attributes"]["Northing"] // 1000))
        waits, progress = [], []
        summary = dd.fetch_tiles_for_selection(
            sel, self.dir, progress=lambda d, t, x: progress.append((d, t)),
            session=session, sleep=waits.append)
        self.assertEqual(summary.fetched, summary.total)
        self.assertEqual(session.post.call_count, summary.total)
        self.assertEqual(len(waits), summary.total - 1)
        self.assertEqual(progress[-1][0], progress[-1][1])
        # zweiter Lauf holt nichts mehr
        again = dd.fetch_tiles_for_selection(sel, self.dir, session=session, sleep=waits.append)
        self.assertEqual(again.fetched, 0)
        self.assertEqual(again.already_cached, summary.total)

    def test_cancel(self):
        sel = FakeSelection(50.3, 7.7, 5000, 5000)
        with self.assertRaises(dd.Dgm1Cancelled):
            dd.fetch_tiles_for_selection(sel, self.dir, cancelled=lambda: True, session=mock.Mock())

    def test_job_runs_in_background_and_reports_errors(self):
        sel = FakeSelection(50.3, 7.7, 1000, 1000)
        with mock.patch.object(dd, "fetch_tiles_for_selection", side_effect=dd.Dgm1Error("kaputt")):
            job = dd.Dgm1FetchJob(sel, self.dir)
            job.start(); job.join(5)
        self.assertTrue(job.finished)
        self.assertEqual(job.error, "kaputt")


class ExporterSourceTests(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        lat, lon = utm.utm_to_latlon(498000.0, 5671000.0, 32)
        self.sel = FakeSelection(float(lat), float(lon), 1600, 1200)

    def tearDown(self):
        self.tmp.cleanup()

    def _fill_cache(self, skip=()):
        for zone, ie, inn in dd.required_dgm1_tiles(self.sel):
            if (ie, inn) in skip:
                continue
            write_geotiff(self.dir / f"{zone}_{ie}_{inn}__DE-RP.tif",
                          plane(ie * 1000, inn * 1000 + 1000, 1000), ie * 1000, inn * 1000 + 1000)
            (self.dir / f"{zone}_{ie}_{inn}__DE-RP.json").write_text(
                json.dumps({"Attribution": "(c) GeoBasis-DE / LVermGeoRP"}), encoding="utf-8")

    def test_default_source_is_unchanged_copernicus(self):
        class FakeMosaic:
            def sample_grid(self, lat, lon):
                return np.full(lat.shape, 123.0, dtype=np.float32)
        with mock.patch.object(he, "download_tiles_for_selection", return_value=[]), \
             mock.patch.object(he.DemMosaic, "from_paths", return_value=FakeMosaic()):
            out = he.build_heightmap_array(self.sel, self.dir)
            arr, info = he.build_heightmap_array_ex(self.sel, self.dir)
        self.assertTrue((out == 123.0).all())
        self.assertEqual(info.source, he.SOURCE_COPERNICUS)
        self.assertEqual(info.fallback_fraction, 0.0)

    def test_dgm1_values_attribution_and_no_fallback_when_complete(self):
        self._fill_cache()
        with mock.patch.object(he, "download_tiles_for_selection", side_effect=AssertionError("kein Copernicus noetig")):
            arr, info = he.build_heightmap_array_ex(
                self.sel, self.dir / "dem", he.SOURCE_DGM1_DE, dgm1_cache_dir=self.dir)
        self.assertEqual(arr.shape, he.pixel_size_for_selection(self.sel)[::-1])
        self.assertEqual(info.fallback_fraction, 0.0)
        self.assertEqual(info.missing_tiles, 0)
        self.assertEqual(info.attributions, ["(c) GeoBasis-DE / LVermGeoRP"])
        # Mittelpunkt: Pixel in der Mitte entspricht der Ebene am Kartenmittelpunkt
        mid = arr[arr.shape[0] // 2, arr.shape[1] // 2]
        self.assertAlmostEqual(float(mid), plane_at(498000.0, 5671000.0), delta=0.3)

    def test_missing_tile_is_filled_from_copernicus(self):
        skip = {(498, 5671)}  # Kachel mit dem Kartenmittelpunkt (E=498000, N=5671000)
        self._fill_cache(skip=skip)

        class FakeMosaic:
            def sample_grid(self, lat, lon):
                return np.full(lat.shape, -7.0, dtype=np.float32)

        with mock.patch.object(he, "download_tiles_for_selection", return_value=[]), \
             mock.patch.object(he.DemMosaic, "from_paths", return_value=FakeMosaic()):
            arr, info = he.build_heightmap_array_ex(
                self.sel, self.dir / "dem", he.SOURCE_DGM1_DE, dgm1_cache_dir=self.dir)
        self.assertGreaterEqual(info.missing_tiles, 1)
        self.assertGreater(info.fallback_fraction, 0.0)
        self.assertLess(info.fallback_fraction, 1.0)
        self.assertFalse(np.isnan(arr).any())
        self.assertTrue((arr == -7.0).any())

    def test_dgm1_without_any_tile_raises_clear_error(self):
        with self.assertRaises(dd.Dgm1Error):
            he.build_heightmap_array_ex(self.sel, self.dir / "dem", he.SOURCE_DGM1_DE,
                                        dgm1_cache_dir=self.dir / "leer")

    def test_folder_source(self):
        folder = self.dir / "eigene"
        folder.mkdir()
        for zone, ie, inn in dd.required_dgm1_tiles(self.sel):
            write_geotiff(folder / f"dgm1_{ie}_{inn}.tif",
                          plane(ie * 1000, inn * 1000 + 1000, 1000), ie * 1000, inn * 1000 + 1000)
        arr, info = he.build_heightmap_array_ex(
            self.sel, self.dir / "dem", he.SOURCE_DGM1_FOLDER, dgm1_folder=folder)
        self.assertEqual(info.fallback_fraction, 0.0)
        self.assertEqual(info.source, he.SOURCE_DGM1_FOLDER)

    def test_unknown_source(self):
        with self.assertRaises(ValueError):
            he.build_heightmap_array_ex(self.sel, self.dir, "quatsch")


if __name__ == "__main__":
    unittest.main()
