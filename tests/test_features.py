import py_compile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class FeaturesTest(unittest.TestCase):
    def test_importer_hidden(self):
        from src.features import VACUUMTUBE_IMPORTER
        self.assertIs(VACUUMTUBE_IMPORTER, False)

    def test_window_compiles(self):
        py_compile.compile(str(ROOT / "src" / "window.py"), doraise=True)

    def test_window_guards_menu_entries(self):
        text = (ROOT / "src" / "window.py").read_text(encoding="utf-8")
        self.assertIn("from src.features import VACUUMTUBE_IMPORTER", text)
        self.assertEqual(text.count("if VACUUMTUBE_IMPORTER:"), 3)


if __name__ == "__main__":
    unittest.main()
