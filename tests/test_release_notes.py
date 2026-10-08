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


if __name__ == "__main__":
    unittest.main()
