import re
import unittest
from pathlib import Path

from src.http_identity import USER_AGENT

ROOT = Path(__file__).resolve().parent.parent

MODULE_PFADE = (
    "src/osm/overpass_client.py",
    "src/heightmap/dgm1_dem.py",
    "src/heightmap/swissalti3d_dem.py",
)


class HttpIdentityTest(unittest.TestCase):

    def test_user_agent_identifiziert_programm(self):
        self.assertIn("TPF3-Map-Studio/", USER_AGENT)
        self.assertIn("https://github.com/sharpi13822/TPF3-Map-Studio", USER_AGENT)

    def test_user_agent_ohne_email(self):
        self.assertIsNone(re.search(r"\S+@\S+", USER_AGENT))

    def test_alle_module_nutzen_gemeinsame_kennung(self):
        for rel in MODULE_PFADE:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("from src.http_identity import USER_AGENT", text, rel)
            self.assertIn('"User-Agent": USER_AGENT', text, rel)

    def test_keine_eigene_user_agent_konstante(self):
        for rel in MODULE_PFADE:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIsNone(
                re.search(r'^USER_AGENT\s*=', text, re.MULTILINE), rel
            )

    def test_swissalti3d_nutzt_dieselbe_konstante(self):
        from src.heightmap import swissalti3d_dem as swiss
        self.assertIs(swiss.USER_AGENT, USER_AGENT)


if __name__ == "__main__":
    unittest.main()
