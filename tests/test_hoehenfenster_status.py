import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATEIEN = (
    "RELEASE_NOTES_v0.1.0.md",
    "docs/ANLEITUNG_HEIGHTMAP.md",
    "docs/ANLEITUNG_HEIGHTMAP.en.md",
    "docs/SPIELWISSEN.md",
    "docs/SPIELWISSEN.en.md",
    "src/gui/heightmap_guide.py",
)

VERALTET = re.compile(
    r"(h\u00f6henfenster|height window)[^.]{0,80}(noch nicht gepr\u00fcft|not been tested)",
    re.IGNORECASE,
)


def _text(rel):
    return (ROOT / rel).read_text(encoding="utf-8")


class HoehenfensterStatusTest(unittest.TestCase):

    def test_keine_veraltete_aussage_ungetestet(self):
        for rel in DATEIEN:
            self.assertIsNone(VERALTET.search(_text(rel)), rel)

    def test_spielwissen_nennt_hoehenfenster_als_getestet(self):
        self.assertIn(
            "Das H\u00f6henfenster selbst ist im Spiel getestet und funktioniert.",
            _text("docs/SPIELWISSEN.md"),
        )
        self.assertIn(
            "The height window itself has been tested in the game and works.",
            _text("docs/SPIELWISSEN.en.md"),
        )


if __name__ == "__main__":
    unittest.main()
