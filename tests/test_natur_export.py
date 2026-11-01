import json
import unittest
from types import SimpleNamespace

from src.heightmap import nature_lua


class NaturExportTest(unittest.TestCase):

    def test_row_every_in_lua(self):
        text, _ = nature_lua.plan_to_lua({"features": []}, row_every=3)
        self.assertIn("reihe_jede = 3,", text)
        text, _ = nature_lua.plan_to_lua({"features": []}, row_every=0)
        self.assertIn("reihe_jede = 1,", text)

    def test_empty_default(self):
        self.assertIn("flaechen = {", nature_lua.EMPTY_NATURDATA_LUA)
        self.assertIn("reihe_jede = 1,", nature_lua.EMPTY_NATURDATA_LUA)

    def test_features_to_lua(self):
        features = [
            SimpleNamespace(kind="vineyard", osm_id=7, row_direction_deg=45.0,
                            points=[(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]),
            SimpleNamespace(kind="wall", osm_id=8, row_direction_deg=None,
                            points=[(0.0, 0.0), (5.0, 0.0)]),
            SimpleNamespace(kind="orchard", osm_id=9, row_direction_deg=0.0,
                            points=[(0.0, 0.0), (5.0, 0.0), (5.0, 5.0)]),
        ]
        text, counts = nature_lua.features_to_lua(features, row_every=2)
        self.assertEqual(counts, {"vineyard": 1, "field": 0, "wall": 1})
        self.assertIn('k = "vineyard", id = 7, r = 45.0', text)
        self.assertIn('k = "wall", id = 8', text)
        self.assertIn("reihe_jede = 2,", text)

    def test_content_json(self):
        original = json.dumps({"archives": None, "files": ["mapstudio.gs.lua", "osmdata.lua", "hud.lua"]})
        neu = json.loads(nature_lua.add_to_content_json(original))
        self.assertEqual(neu["files"], ["mapstudio.gs.lua", "osmdata.lua", "naturdata.lua", "hud.lua"])
        self.assertIsNone(neu["archives"])
        nochmal = json.loads(nature_lua.add_to_content_json(json.dumps(neu)))
        self.assertEqual(nochmal["files"].count("naturdata.lua"), 1)
        ohne = json.loads(nature_lua.add_to_content_json(json.dumps({"files": ["a.lua"]})))
        self.assertEqual(ohne["files"], ["a.lua", "naturdata.lua"])


if __name__ == "__main__":
    unittest.main()
