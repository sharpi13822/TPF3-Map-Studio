"""Der TPF2-Export beim OSM-Download haengt am Schalter VACUUMTUBE_IMPORTER."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTROLLER = ROOT / "src" / "map" / "map_controller.py"
FEATURES = ROOT / "src" / "features.py"


def _fetch_osm_body():
    text = CONTROLLER.read_text(encoding="utf-8").replace("\r\n", "\n")
    return text[text.index("    def fetch_osm("):text.index("    def apply_osm(")]


class ExportGateTest(unittest.TestCase):

    def test_switch_is_off_in_release(self):
        self.assertRegex(
            FEATURES.read_text(encoding="utf-8"),
            r"(?m)^VACUUMTUBE_IMPORTER = False\s*$",
        )

    def test_controller_imports_the_switch(self):
        text = CONTROLLER.read_text(encoding="utf-8")
        self.assertIn("from src.features import VACUUMTUBE_IMPORTER", text)

    def test_every_tpf2_write_is_inside_the_gate(self):
        body = _fetch_osm_body()
        gate = body.index("        if VACUUMTUBE_IMPORTER:\n")
        before = body[:gate]
        after = body[gate:]
        for needle in ("OSMExporter()", "TPF2Exporter", "TPF2LuaWriter(", "osm_map_1", "tpf2_writer.write("):
            self.assertNotIn(needle, before, needle)
            self.assertIn(needle, after, needle)

    def test_download_still_builds_geometry_and_returns_data(self):
        body = _fetch_osm_body()
        self.assertIn("GeometryBuilder(osm).build()", body)
        self.assertTrue(re.search(r"\n        return osm\s*$", body.rstrip() + "\n"))
        self.assertLess(body.index("GeometryBuilder(osm).build()"), body.index("if VACUUMTUBE_IMPORTER:"))


if __name__ == "__main__":
    unittest.main()
