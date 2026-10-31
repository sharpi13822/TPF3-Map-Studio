import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src.heightmap import nature_plan_export as npe


class PlanFolderTest(unittest.TestCase):

    def test_neben_der_maske(self):
        self.assertEqual(
            npe.plan_folder_for(Path("C:/x/maske.png"), Path("C:/spiel/biomes")),
            Path("C:/x"),
        )

    def test_nicht_im_spielordner(self):
        with tempfile.TemporaryDirectory() as tmp:
            game = Path(tmp)
            folder = npe.plan_folder_for(game / "biome_osm.png", game)
            self.assertNotEqual(folder.resolve(), game.resolve())

    def test_ohne_spielordner(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertEqual(npe.plan_folder_for(Path(tmp) / "m.png"), Path(tmp))


class SavePlanTest(unittest.TestCase):

    def test_nichts_gefunden(self):
        with mock.patch.object(npe, "collect_features", return_value=[]):
            self.assertIsNone(npe.save_plan_for_mask(None, None, "x/m.png"))

    def test_schreibt_csv_und_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            mask = Path(tmp) / "karte.png"
            with mock.patch.object(npe, "collect_features", return_value=[object()]), \
                    mock.patch.object(npe, "write_csv") as csv_w, \
                    mock.patch.object(npe, "write_json") as json_w:
                result = npe.save_plan_for_mask(None, None, mask)
            self.assertEqual(result[0].name, "karte_natur_details_plan.csv")
            self.assertEqual(result[1].name, "karte_natur_details_plan.json")
            csv_w.assert_called_once()
            json_w.assert_called_once()


if __name__ == "__main__":
    unittest.main()
