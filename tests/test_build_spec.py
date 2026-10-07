import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class BuildSpecTest(unittest.TestCase):

    def setUp(self):
        self.spec = (ROOT / "build.spec").read_text(encoding="utf-8")

    def test_datas_pairs_point_to_existing_folders(self):
        block = re.search(r"datas = \[(.*?)\n\]", self.spec, flags=re.S).group(1)
        pairs = re.findall(r'\("([^"]+)",\s*"([^"]+)"\)', block)
        self.assertGreaterEqual(len(pairs), 3)
        for source, target in pairs:
            self.assertEqual(source, target, "Ziel muss dem Quellbaum entsprechen (Path(__file__)-relative Pfade)")
            self.assertTrue((ROOT / source).exists(), source)

    def test_gui_icons_are_bundled(self):
        self.assertIn('("src/gui/icons", "src/gui/icons")', self.spec)
        self.assertIn('("src/map/web", "src/map/web")', self.spec)


if __name__ == "__main__":
    unittest.main()
