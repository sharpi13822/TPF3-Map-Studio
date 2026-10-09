import tempfile
import unittest
from pathlib import Path

from src.qt_translation import find_translation_files


class FindTranslationFilesTest(unittest.TestCase):

    def test_findet_die_datei_der_gewaehlten_sprache(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "qtbase_de.qm").write_bytes(b"x")
            (Path(tmp) / "qtbase_en.qm").write_bytes(b"x")

            de = find_translation_files("de", [tmp])
            en = find_translation_files("en", [tmp])

        self.assertEqual([p.name for p in de], ["qtbase_de.qm"])
        self.assertEqual([p.name for p in en], ["qtbase_en.qm"])

    def test_fehlende_datei_ist_kein_fehler(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(find_translation_files("en", [tmp]), [])

    def test_sucht_in_mehreren_ordnern(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            (Path(b) / "qtbase_de.qm").write_bytes(b"x")
            found = find_translation_files("de", [a, b])

        self.assertEqual(len(found), 1)

    def test_main_installiert_qt_uebersetzungen(self):
        source = (Path(__file__).resolve().parent.parent / "src" / "main.py").read_text(encoding="utf-8")
        self.assertIn("install_qt_translations(app, get_language())", source)


if __name__ == "__main__":
    unittest.main()
