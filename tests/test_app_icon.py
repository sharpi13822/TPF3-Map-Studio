import re
import unittest
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ICO = ROOT / "src" / "icons" / "app.ico"
SPEC = ROOT / "build.spec"
ERWARTET = {16, 24, 32, 48, 64, 128, 256}


class AppIconTest(unittest.TestCase):

    def test_ico_vorhanden(self):
        self.assertTrue(ICO.is_file(), "src/icons/app.ico fehlt (python tools/make_icon.py)")

    def test_ico_enthaelt_alle_groessen(self):
        with Image.open(ICO) as im:
            groessen = {w for (w, h) in im.info.get("sizes", set())}
        self.assertTrue(ERWARTET <= groessen, groessen)

    def test_build_spec_nutzt_icon(self):
        text = SPEC.read_text(encoding="utf-8")
        self.assertIsNotNone(
            re.search(r'icon\s*=\s*["\']src/icons/app\.ico["\']', text),
            "build.spec: icon=\"src/icons/app.ico\" fehlt im EXE(...)",
        )


if __name__ == "__main__":
    unittest.main()