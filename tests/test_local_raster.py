import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from PIL import Image, TiffImagePlugin

from src.heightmap import local_raster_dem as lr
from src.heightmap.crs import get_crs


def plane(x, y):
    return 100.0 + 0.01 * (x - 650000.0) + 0.02 * (y - 6860000.0)


def write_geotiff(path, arr, left, top, cell, epsg, point=False, nodata=None):
    ifd = TiffImagePlugin.ImageFileDirectory_v2()
    ifd[33550] = (cell, cell, 0.0)
    ifd.tagtype[33550] = 12
    ifd[33922] = (0.0, 0.0, 0.0, float(left), float(top), 0.0)
    ifd.tagtype[33922] = 12
    geo = 2 if epsg == 4326 else 1
    keys = [1, 1, 0, 3, 1024, 0, 1, geo, 1025, 0, 1, 2 if point else 1]
    keys += [2048 if epsg == 4326 else 3072, 0, 1, int(epsg)]
    ifd[34735] = tuple(keys)
    ifd.tagtype[34735] = 3
    if nodata is not None:
        ifd[42113] = str(nodata)
        ifd.tagtype[42113] = 2
    Image.fromarray(np.asarray(arr, dtype=np.float32), mode="F").save(path, format="TIFF", tiffinfo=ifd)


def plane_grid(left, top, cell, cols, rows):
    xs = left + (np.arange(cols) + 0.5) * cell
    ys = top - (np.arange(rows) + 0.5) * cell
    xx, yy = np.meshgrid(xs, ys)
    return plane(xx, yy)


# Punkte bei Paris (Lambert-93 etwa x 650000, y 6860000)
LATS = np.array([48.8566, 48.8580, 48.8550, 48.8600])
LONS = np.array([2.3522, 2.3540, 2.3500, 2.3560])


class LocalRasterTest(unittest.TestCase):

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.l93 = get_crs(2154)
        x, y = self.l93.latlon_to_xy(LATS, LONS)
        self.x, self.y = x, y
        self.left = float(np.floor(x.min() / 1000) * 1000) - 1000
        self.top = float(np.ceil(y.max() / 1000) * 1000) + 1000

    def tearDown(self):
        self.tmp.cleanup()

    def selection(self, w=2000.0, h=2000.0):
        return SimpleNamespace(center=(float(LATS.mean()), float(LONS.mean())), width_m=w, height_m=h,
                               scale_factor=1.0, rotation_deg=0.0)

    def test_lambert93_geotiff(self):
        cols = rows = 800
        write_geotiff(self.dir / "a.tif", plane_grid(self.left, self.top, 5.0, cols, rows), self.left, self.top, 5.0, 2154)
        m = lr.LocalRasterMosaic.from_folder(self.dir, self.selection())
        self.assertEqual(m.slot_count, 1)
        self.assertEqual(m.epsg_codes, (2154,))
        v = m.sample_grid(LATS, LONS)
        np.testing.assert_allclose(v, plane(self.x, self.y), atol=1e-3)
        self.assertTrue(lr.folder_needs_generic(self.dir))

    def test_two_tiles_and_nodata(self):
        half = 400
        g = plane_grid(self.left, self.top, 5.0, 800, 800)
        write_geotiff(self.dir / "w.tif", g[:, :half], self.left, self.top, 5.0, 2154)
        right = g[:, half:].copy()
        right[0, 0] = -9999.0
        write_geotiff(self.dir / "o.tif", right, self.left + half * 5.0, self.top, 5.0, 2154, nodata=-9999)
        m = lr.LocalRasterMosaic.from_folder(self.dir, self.selection())
        self.assertEqual(m.slot_count, 2)
        np.testing.assert_allclose(m.sample_grid(LATS, LONS), plane(self.x, self.y), atol=1e-3)
        far = m.sample_grid(np.array([40.0]), np.array([10.0]))
        self.assertTrue(np.isnan(far[0]))

    def test_pixel_is_point(self):
        cell = 5.0
        g = plane_grid(self.left, self.top, cell, 800, 800)
        # Pixelmitte als Bezug: Ecke liegt eine halbe Zelle weiter innen
        write_geotiff(self.dir / "p.tif", g, self.left + cell / 2, self.top - cell / 2, cell, 2154, point=True)
        m = lr.LocalRasterMosaic.from_folder(self.dir, self.selection())
        np.testing.assert_allclose(m.sample_grid(LATS, LONS), plane(self.x, self.y), atol=1e-3)

    def test_asc_with_prj_and_downsampling(self):
        utm = get_crs(25831)
        x, y = utm.latlon_to_xy(LATS, LONS)
        left = float(np.floor(x.min() / 1000) * 1000) - 1000
        top = float(np.ceil(y.max() / 1000) * 1000) + 1000
        cols = rows = 4000
        xs = left + (np.arange(cols) + 0.5)
        ys = top - (np.arange(rows) + 0.5)
        xx, yy = np.meshgrid(xs, ys)
        z = 50.0 + 0.003 * (xx - left) - 0.004 * (top - yy)
        path = self.dir / "kachel.asc"
        with open(path, "w") as f:
            f.write(f"ncols {cols}\nnrows {rows}\nxllcorner {left}\nyllcorner {top - rows}\ncellsize 1.0\nNODATA_value -9999\n")
            np.savetxt(f, z, fmt="%.3f")
        (self.dir / "kachel.prj").write_text('PROJCS["ETRS89 / UTM zone 31N"]')
        m = lr.LocalRasterMosaic.from_folder(self.dir, self.selection())
        self.assertEqual(m.epsg_codes, (25831,))
        self.assertAlmostEqual(m.rasters[0].cell_x, 2.0)
        expect = 50.0 + 0.003 * (x - left) - 0.004 * (top - y)
        np.testing.assert_allclose(m.sample_grid(LATS, LONS), expect, atol=1e-3)

    def test_selection_skips_far_files_and_epsg_txt(self):
        g = plane_grid(self.left, self.top, 5.0, 800, 800)
        write_geotiff(self.dir / "nah.tif", g, self.left, self.top, 5.0, 2154)
        write_geotiff(self.dir / "fern.tif", g, self.left + 200000, self.top, 5.0, 2154)
        m = lr.LocalRasterMosaic.from_folder(self.dir, self.selection())
        self.assertEqual((m.slot_count, m.skipped_files), (1, 1))

    def test_unknown_crs_message(self):
        g = plane_grid(self.left, self.top, 5.0, 10, 10)
        path = self.dir / "x.asc"
        with open(path, "w") as f:
            f.write(f"ncols 10\nnrows 10\nxllcorner {self.left}\nyllcorner {self.top - 50}\ncellsize 5\n")
            np.savetxt(f, g, fmt="%.2f")
        with self.assertRaises(lr.LocalRasterError) as ctx:
            lr.LocalRasterMosaic.from_folder(self.dir)
        self.assertIn("epsg.txt", str(ctx.exception))
        (self.dir / "epsg.txt").write_text("2154\n")
        m = lr.LocalRasterMosaic.from_folder(self.dir)
        self.assertEqual(m.epsg_codes, (2154,))

    def test_dgm1_folder_stays_on_old_path(self):
        write_geotiff(self.dir / "dgm.tif", np.zeros((10, 10)), 600000.0, 5600000.0, 1.0, 25832)
        self.assertFalse(lr.folder_needs_generic(self.dir))
        self.assertFalse(lr.folder_needs_generic(self.dir / "leer"))

    def test_folder_epsg_known(self):
        g = plane_grid(self.left, self.top, 5.0, 10, 10)
        path = self.dir / "x.asc"
        with open(path, "w") as f:
            f.write(f"ncols 10\nnrows 10\nxllcorner {self.left}\nyllcorner {self.top - 50}\ncellsize 5\n")
            np.savetxt(f, g, fmt="%.2f")
        self.assertFalse(lr.folder_epsg_known(self.dir))
        path.rename(self.dir / "RGEALTI_0650_6860_MNT_LAMB93.asc")
        self.assertTrue(lr.folder_epsg_known(self.dir))

    def test_geographic_tiff(self):
        cell = 0.0001
        left, top = 2.34, 48.87
        lon = left + (np.arange(400) + 0.5) * cell
        lat = top - (np.arange(400) + 0.5) * cell
        lo, la = np.meshgrid(lon, lat)
        write_geotiff(self.dir / "geo.tif", 10 + 100 * (lo - 2.34) + 50 * (la - 48.84), left, top, cell, 4326)
        m = lr.LocalRasterMosaic.from_folder(self.dir, self.selection())
        np.testing.assert_allclose(m.sample_grid(LATS, LONS), 10 + 100 * (LONS - 2.34) + 50 * (LATS - 48.84), atol=1e-3)


if __name__ == "__main__":
    unittest.main()
