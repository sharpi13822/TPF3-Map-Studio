import re
import unittest
from pathlib import Path

from src.http_identity import USER_AGENT

ROOT = Path(__file__).resolve().parent.parent


class HttpIdentityTest(unittest.TestCase):

    def test_user_agent_identifiziert_programm(self):
        self.assertIn("TPF3-Map-Studio/", USER_AGENT)
        self.assertIn("https://github.com/sharpi13822/TPF3-Map-Studio", USER_AGENT)

    def test_user_agent_ohne_email(self):
        self.assertIsNone(re.search(r"\S+@\S+", USER_AGENT))

    def test_overpass_und_dgm1_nutzen_gemeinsame_kennung(self):
        for rel in ("src/osm/overpass_client.py", "src/heightmap/dgm1_dem.py"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertIn("from src.http_identity import USER_AGENT", text, rel)
            self.assertIn('"User-Agent": USER_AGENT', text, rel)

    def test_swissalti3d_kennung_mit_url_ohne_email(self):
        text = (ROOT / "src/heightmap/swissalti3d_dem.py").read_text(encoding="utf-8")
        m = re.search(r'USER_AGENT\s*=\s*"([^"]+)"', text)
        self.assertIsNotNone(m)
        self.assertIn("github.com/sharpi13822/TPF3-Map-Studio", m.group(1))
        self.assertIsNone(re.search(r"\S+@\S+", m.group(1)))


if __name__ == "__main__":
    unittest.main()
