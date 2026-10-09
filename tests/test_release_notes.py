import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class ReleaseNotesTest(unittest.TestCase):

    def setUp(self):
        self.text = (ROOT / "RELEASE_NOTES_v0.1.0.md").read_text(encoding="utf-8")

    def test_keine_platzhalter_mehr(self):
        self.assertNotIn("<paste from", self.text)
        self.assertNotIn("<aus der", self.text)

    def test_pruefsumme_in_beiden_sprachen_gleich(self):
        hashes = re.findall(r"`([0-9a-f]{64})`", self.text)
        self.assertEqual(len(hashes), 2)
        self.assertEqual(hashes[0], hashes[1])


class ReleaseNotes011Test(unittest.TestCase):

    def setUp(self):
        self.text = (ROOT / "RELEASE_NOTES_v0.1.1.md").read_text(encoding="utf-8")

    def test_beide_sprachen_und_version(self):
        self.assertIn("## English", self.text)
        self.assertIn("## Deutsch", self.text)
        self.assertIn("TPF3-Map-Studio-v0.1.1-win64.zip", self.text)

    def test_pruefsumme_noch_nicht_oder_in_beiden_sprachen_gleich(self):
        hashes = re.findall(r"`([0-9a-f]{64})`", self.text)
        self.assertIn(len(hashes), (0, 2))
        if hashes:
            self.assertEqual(hashes[0], hashes[1])

    def test_keine_privaten_daten(self):
        lower = self.text.lower()
        self.assertNotIn("@gmail", lower)
        self.assertNotIn("steamcommunity.com/id", lower)


if __name__ == "__main__":
    unittest.main()
