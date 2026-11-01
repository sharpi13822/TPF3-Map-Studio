import math
import unittest

import numpy as np

from src.heightmap import crs, utm


class CrsTest(unittest.TestCase):

    def test_utm_matches_utm_module(self):
        for zone, lat, lon in ((32, 50.4, 10.7), (30, 40.4, -3.7), (33, 37.5, 14.0)):
            x, y = crs.get_crs(25800 + zone).latlon_to_xy(lat, lon)
            ex, ey = utm.latlon_to_utm(lat, lon, zone)
            self.assertAlmostEqual(float(x), float(ex), places=6)
            self.assertAlmostEqual(float(y), float(ey), places=6)

    def test_lcc_epsg_guidance_example(self):
        # EPSG Guidance Note 7-2, Lambert 2SP, NAD27 / Texas South Central (Clarke 1866)
        ft = 0.3048006096012192
        f = 1 / 294.97870
        c = crs.Crs(0, "Texas", "lcc", lat1=28 + 23 / 60, lat2=30 + 17 / 60, lat0=27 + 50 / 60,
                    lon0=-99.0, fe=2000000 * ft, fn=0.0, a=6378206.4, e=math.sqrt(f * (2 - f)))
        x, y = c.latlon_to_xy(28.5, -96.0)
        self.assertAlmostEqual(float(x) / ft, 2963503.91, places=1)
        self.assertAlmostEqual(float(y) / ft, 254759.80, places=1)

    def test_false_origins(self):
        for epsg, lat, lon, fx, fy in (
            (2154, 46.5, 3.0, 700000.0, 6600000.0),
            (2157, 53.5, -8.0, 600000.0, 750000.0),
            (3812, 50.797815, 4.359215833333333, 649328.0, 665262.0),
        ):
            x, y = crs.get_crs(epsg).latlon_to_xy(lat, lon)
            self.assertAlmostEqual(float(x), fx, places=3)
            self.assertAlmostEqual(float(y), fy, places=3)

    def test_vectorized_and_geographic(self):
        x, y = crs.get_crs(4326).latlon_to_xy(np.array([48.0, 49.0]), np.array([2.0, 3.0]))
        self.assertEqual(list(x), [2.0, 3.0])
        self.assertEqual(list(y), [48.0, 49.0])

    def test_unknown(self):
        with self.assertRaises(crs.UnknownCrsError):
            crs.get_crs(27700)

    def test_epsg_from_text(self):
        cases = {
            'PROJCS["RGF93_Lambert_93",GEOGCS["GCS_RGF_1993"]]': 2154,
            'PROJCS["ETRS89 / UTM zone 30N",AUTHORITY["EPSG","25830"]]': 25830,
            "RGEALTI_FXX_0650_6860_MNT_LAMB93_IGN69.asc": 2154,
            'PROJCS["WGS_1984_UTM_Zone_33N"]': 32633,
            'PROJCS["RDN2008 / UTM zone 33N (N-E)"]': 6708,
            'GEOGCS["GCS_WGS_1984"]': 4326,
            "irgendwas": None,
        }
        for text, code in cases.items():
            self.assertEqual(crs.epsg_from_text(text), code, text)


if __name__ == "__main__":
    unittest.main()
