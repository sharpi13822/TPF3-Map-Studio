"""Tests fuer src/heightmap/build_template.py (Bauvorlage als Bild)."""

import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from src.heightmap import build_template as bt
from src.osm.objects.way import Way
from tests.test_network_export import SELECTION, make_osm, node

W = H = 5000      # 10 km Karte -> 2 m je Pixel


def build_osm():
    nodes = [
        node(1, -4000, 0), node(2, 4000, 0),          # Autobahn West-Ost durch die Mitte
        node(3, 0, -4000), node(4, 0, 4000),          # Gleis Sued-Nord
        node(5, 2000, 2000), node(6, 2100, 2000), node(7, 2100, 2050), node(8, 2000, 2050),  # Bahnsteig
        node(9, -3000, -3000), node(10, -2000, -3000),  # Wohnstrasse
    ]
    ways = [
        Way(100, [1, 2], {"highway": "motorway"}),
        Way(101, [3, 4], {"railway": "rail"}),
        Way(102, [5, 6, 7, 8, 5], {"railway": "platform"}),
        Way(103, [9, 10], {"highway": "residential"}),
        Way(104, [1, 4], {"waterway": "river"}),      # kein Verkehrsweg
    ]
    return make_osm(nodes, ways)


def px(img, x_m, y_m):
    col = int((x_m + 5000) / 2 - 0.5)
    row = int((5000 - y_m) / 2 - 0.5)
    return img.getpixel((col, row))


class BuildTemplateTests(unittest.TestCase):
    def setUp(self):
        self.img = bt.render_build_template(build_osm(), SELECTION, W, H)

    def test_groesse_wie_die_karte(self):
        self.assertEqual(self.img.size, (W, H))
        self.assertEqual(self.img.mode, "RGB")

    def test_autobahn_in_ihrer_farbe(self):
        self.assertEqual(px(self.img, -2500, 0), dict((n, c) for n, c, _ in bt.ROAD_STYLES)["motorway"])

    def test_wohnstrasse_in_ihrer_farbe(self):
        self.assertEqual(px(self.img, -2500, -3000), dict((n, c) for n, c, _ in bt.ROAD_STYLES)["residential"])

    def test_gleis_schwarz_weiss_geblockt(self):
        a = np.array(self.img)
        col = 2499
        mitte = [tuple(a[r, col]) for r in range(600, 1500)]
        self.assertIn((0, 0, 0), mitte)
        self.assertIn((255, 255, 255), mitte)
        rand = [tuple(a[r, col - 1]) for r in range(600, 1500)]
        self.assertTrue(all(p == (0, 0, 0) for p in rand))

    def test_bahnsteig_grau(self):
        self.assertEqual(px(self.img, 2050, 2025), bt.PLATFORM_COLOR)

    def test_fluss_wird_nicht_gezeichnet(self):
        self.assertEqual(px(self.img, -2000, 2000), bt.BACKGROUND)

    def test_gleis_ueber_der_strasse(self):
        self.assertIn(px(self.img, 0, 0), ((0, 0, 0), (255, 255, 255)))

    def test_ohne_bahnsteige(self):
        img = bt.render_build_template(build_osm(), SELECTION, W, H, platforms=False)
        self.assertEqual(px(img, 2050, 2025), bt.BACKGROUND)

    def test_bloecke_wechseln_ab(self):
        pieces = bt._dashes([(0, 0), (100, 0)], 10)
        self.assertEqual(len(pieces), 5)
        self.assertAlmostEqual(pieces[0][0][0], 10.0)
        self.assertAlmostEqual(pieces[0][-1][0], 20.0)

    def test_bloecke_ueber_knicke(self):
        pieces = bt._dashes([(0, 0), (15, 0), (15, 15)], 10)
        self.assertEqual(len(pieces), 1)
        self.assertEqual(pieces[0][0], (10.0, 0.0))
        self.assertEqual(pieces[0][-1], (15.0, 5.0))

    def test_gleis_auch_bei_grobem_raster_geblockt(self):
        a = np.array(bt.render_build_template(build_osm(), SELECTION, 2500, 2500))
        col = 1249
        mitte = [tuple(a[r, col]) for r in range(300, 800)]
        self.assertIn((0, 0, 0), mitte)
        self.assertIn((255, 255, 255), mitte)

    def test_speichern_tga_und_png(self):
        with tempfile.TemporaryDirectory() as d:
            paths = bt.save_build_template(self.img, Path(d) / "vorlage.tga")
            self.assertEqual([p.suffix for p in paths], [".tga", ".png"])
            for p in paths:
                self.assertEqual(Image.open(p).size, (W, H))


if __name__ == "__main__":
    unittest.main()
