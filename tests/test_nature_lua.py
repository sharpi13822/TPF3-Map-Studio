import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from src.heightmap import nature_lua

PLAN = {
    "summary": {},
    "features": [
        {"kind": "vineyard", "osm_id": 11, "row_direction_deg": 12.5,
         "points": [[0, 0], [20, 0], [20, 100], [0, 100]]},
        {"kind": "field", "osm_id": 12, "row_direction_deg": 90.0,
         "points": [[0, 200], [50, 200], [50, 240.04]]},
        {"kind": "wall", "osm_id": 13, "points": [[0, 0], [-10.25, 0]]},
        {"kind": "hedge", "osm_id": 14, "points": [[0, 0], [5, 5]]},
        {"kind": "orchard", "osm_id": 15, "points": [[0, 0], [5, 0], [5, 5]]},
        {"kind": "vineyard", "osm_id": 16, "points": [[0, 0], [1, 1]]},
    ],
}


class NatureLuaTest(unittest.TestCase):

    def test_counts_and_content(self):
        text, counts = nature_lua.plan_to_lua(PLAN)
        self.assertEqual(counts, {"vineyard": 1, "field": 1, "wall": 1})
        self.assertIn('{ k = "vineyard", id = 11, r = 12.5, p = { 0.0,0.0,20.0,0.0,20.0,100.0,0.0,100.0 } }', text)
        self.assertIn('{ k = "field", id = 12, r = 90.0, p = { 0.0,200.0,50.0,200.0,50.0,240.0 } }', text)
        self.assertIn('{ k = "wall", id = 13, p = { 0.0,0.0,-10.2,0.0 } }', text)
        self.assertNotIn("hedge", text)
        self.assertNotIn("orchard", text)

    def test_empty_plan(self):
        text, counts = nature_lua.plan_to_lua({"features": []})
        self.assertEqual(sum(counts.values()), 0)
        self.assertIn("flaechen = {", text)

    def test_write_and_cli(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = Path(tmp) / "plan.json"
            plan.write_text(json.dumps(PLAN), encoding="utf-8")
            out = Path(tmp) / "mod" / "naturdata.lua"
            self.assertEqual(nature_lua.main([str(plan), str(out)]), 0)
            self.assertTrue(out.read_text(encoding="utf-8").startswith("-- Natur-Daten"))
            self.assertEqual(nature_lua.main([]), 2)

    @unittest.skipUnless(shutil.which("texlua") or shutil.which("lua"), "kein Lua-Interpreter")
    def test_lua_syntax(self):
        lua = shutil.which("texlua") or shutil.which("lua")
        text, _ = nature_lua.plan_to_lua(PLAN)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "d.lua"
            path.write_text(text + "", encoding="utf-8")
            check = Path(tmp) / "c.lua"
            check.write_text(f'local d = dofile([[{path}]]) assert(#d.flaechen == 2 and #d.linien == 1) print("ok")', encoding="utf-8")
            result = subprocess.run([lua, str(check)], capture_output=True, text=True)
            self.assertIn("ok", result.stdout, result.stderr)


if __name__ == "__main__":
    unittest.main()
