import tempfile
import unittest
from pathlib import Path

from src.heightmap import dgm1_dem as d
from src.map.objects.selection import Selection


class Resp:
    status_code = 400
    headers = {}

    def json(self):
        return {"Attributes": {"Error": {"Detail": "kein Gebiet"}}}


class Session:
    def __init__(self):
        self.zones = []

    def post(self, url, json=None, headers=None, timeout=None):
        self.zones.append(json["Attributes"]["Zone"])
        return Resp()


class Ok:
    status_code = 200
    headers = {}

    def json(self):
        return {"Attributes": {"RawTIFs": [{"Origin": "RP", "Data": "AAAA"}]}}


class MixedSession:
    """Lehnt Kacheln westlich von ie_grenze ab (HTTP 400), liefert die anderen."""

    def __init__(self, ie_grenze):
        self.ie_grenze = ie_grenze
        self.zones = []

    def post(self, url, json=None, headers=None, timeout=None):
        attrs = json["Attributes"]
        self.zones.append(attrs["Zone"])
        ie = int(attrs["Easting"]) // 1000
        return Resp() if ie < self.ie_grenze else Ok()


class ZoneFallbackTest(unittest.TestCase):
    def setUp(self):
        self.sel = Selection.from_center(48.0, 12.3, 2000.0, 2000.0)

    def test_default_zone_is_33_east_of_12(self):
        self.assertEqual({t[0] for t in d.required_dgm1_tiles(self.sel)}, {33})

    def test_zone_override(self):
        self.assertEqual({t[0] for t in d.required_dgm1_tiles(self.sel, zone=32)}, {32})

    def test_rejected_zone_is_retried_in_other_zone(self):
        session = Session()
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(d.Dgm1TileRejected) as ctx:
                d.fetch_tiles_for_selection(
                    self.sel, Path(tmp), min_interval_s=0, session=session, sleep=lambda s: None
                )
        # erst Zone 33 (Standard), dann 32, zuletzt nochmal 33 ohne Wechsel
        self.assertEqual(session.zones[0], 33)
        self.assertIn(32, session.zones)
        self.assertEqual(session.zones[-1], 33)
        self.assertIn("kein Gebiet", str(ctx.exception))

    def test_kacheln_jenseits_der_grenze_gelten_als_ohne_daten(self):
        # Rechteck an der Mosel: westliche Kacheln (Luxemburg) lehnt der Dienst ab
        sel = Selection.from_center(49.6, 6.45, 3000.0, 2000.0)
        tiles = d.required_dgm1_tiles(sel)
        grenze = sorted({t[1] for t in tiles})[1]
        session = MixedSession(grenze)
        with tempfile.TemporaryDirectory() as tmp:
            summary = d.fetch_tiles_for_selection(
                sel, Path(tmp), min_interval_s=0, session=session, sleep=lambda s: None
            )
            none_files = list(Path(tmp).glob("*.none"))
        self.assertGreater(summary.fetched, 0)
        self.assertGreater(summary.no_data, 0)
        self.assertEqual(summary.no_data, len(none_files))
        self.assertEqual(set(session.zones), {32})

    def test_cache_zone_is_found(self):
        alt = d.required_dgm1_tiles(self.sel, zone=32)
        with tempfile.TemporaryDirectory() as tmp:
            zone, ie, inn = alt[0]
            (Path(tmp) / (d._slot_prefix(zone, ie, inn) + ".none")).write_bytes(b"x")
            tiles = d._tiles_in_cached_zone(self.sel, Path(tmp))
        self.assertEqual({t[0] for t in tiles}, {32})


if __name__ == "__main__":
    unittest.main()
