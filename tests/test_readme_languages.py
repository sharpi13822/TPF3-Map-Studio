"""Prueft, dass die deutschen und englischen Dokumente zusammenpassen."""

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _read(name):
    return (ROOT / name).read_text(encoding="utf-8")


def _headings(text, level):
    return re.findall(rf"^{'#' * level} (.+)$", text, flags=re.M)


def _links(text):
    found = set(re.findall(r"\]\((https?://[^)\s]+)\)", text))
    found |= set(re.findall(r'(?:href|src)="(https?://[^"]+)"', text))
    return sorted(found)


class LanguageSwitchTest(unittest.TestCase):

    def test_files_exist_and_link_each_other(self):
        for de, en in (("README.md", "README.en.md"), ("THIRD_PARTY_NOTICES.md", "THIRD_PARTY_NOTICES.en.md")):
            self.assertTrue((ROOT / en).exists(), en)
            self.assertIn(f"[English]({en})", _read(de))
            self.assertIn(f"[Deutsch]({de})", _read(en))

    def test_license_is_mentioned_in_both(self):
        self.assertIn("MIT", _read("README.md"))
        self.assertIn("MIT", _read("README.en.md"))
        self.assertIn("MIT License", _read("LICENSE"))


class SameStructureTest(unittest.TestCase):

    def test_readme_has_same_sections(self):
        for level in (2, 3):
            self.assertEqual(len(_headings(_read("README.md"), level)), len(_headings(_read("README.en.md"), level)), f"Ebene {level}")

    def test_notices_have_same_sections(self):
        for level in (2, 3):
            self.assertEqual(
                len(_headings(_read("THIRD_PARTY_NOTICES.md"), level)),
                len(_headings(_read("THIRD_PARTY_NOTICES.en.md"), level)),
                f"Ebene {level}",
            )

    def test_same_external_links(self):
        for de, en in (("README.md", "README.en.md"), ("THIRD_PARTY_NOTICES.md", "THIRD_PARTY_NOTICES.en.md")):
            self.assertEqual(_links(_read(de)), _links(_read(en)), en)

    def test_same_commands_in_code_blocks(self):
        blocks_de = re.findall(r"```\n(.*?)```", _read("README.md"), flags=re.S)
        blocks_en = re.findall(r"```\n(.*?)```", _read("README.en.md"), flags=re.S)
        self.assertEqual(blocks_de, blocks_en)

    def test_english_anchors_resolve(self):
        text = _read("README.en.md")
        anchors = set()
        for heading in re.findall(r"^#{2,3} (.+)$", text, flags=re.M):
            slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
            anchors.add(slug)
        for target in re.findall(r"\]\(#([^)]+)\)", text):
            self.assertIn(target, anchors, target)

    def test_german_anchors_resolve(self):
        text = _read("README.md")
        anchors = set()
        for heading in re.findall(r"^#{2,3} (.+)$", text, flags=re.M):
            anchors.add(re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-"))
        for target in re.findall(r"\]\(#([^)]+)\)", text):
            self.assertIn(target, anchors, target)


class ObligationsInEnglishTest(unittest.TestCase):

    def test_swiss_attribution_stays_in_english(self):
        readme = _read("README.en.md")
        notices = _read("THIRD_PARTY_NOTICES.en.md")
        self.assertIn("swissALTI3D", readme)
        self.assertIn("Bundesamt für Landestopografie swisstopo", readme)
        self.assertIn("Attribution is mandatory", notices)
        self.assertIn("https://www.swisstopo.admin.ch/en/terms-of-use-free-geodata-and-geoservices", notices)

    def test_other_obligations_stay_in_english(self):
        notices = _read("THIRD_PARTY_NOTICES.en.md")
        for needle in ("ODbL", "dl-de/by-2-0", "Copernicus", "LGPL", "Tile Usage Policy", "Terrain Tiles"):
            self.assertIn(needle, notices, needle)

    def test_no_forbidden_words(self):
        for name in ("README.en.md", "THIRD_PARTY_NOTICES.en.md"):
            text = _read(name).lower()
            for word in ("esri", "satellite", "arcgisonline"):
                self.assertNotIn(word, text, name)

    def test_release_notes_have_both_languages(self):
        notes = _read("RELEASE_NOTES_v0.1.0.md")
        self.assertIn("## English", notes)
        self.assertIn("## Deutsch", notes)


class PrivacyTest(unittest.TestCase):

    def test_no_private_data_in_public_documents(self):
        names = ("README.md", "README.en.md", "THIRD_PARTY_NOTICES.md", "THIRD_PARTY_NOTICES.en.md", "RELEASE_NOTES_v0.1.0.md", "RELEASE_NOTES_v0.1.1.md", "RELEASE_NOTES_v0.3.0.md", "LICENSE")
        for name in names:
            text = _read(name).lower()
            self.assertNotIn("@gmail", text, name)
            self.assertNotIn("steamcommunity.com/id", text, name)
            self.assertNotIn("backup.git", text, name)


class GameKnowledgeTest(unittest.TestCase):

    def test_both_languages_exist_and_match(self):
        de = _read("docs/SPIELWISSEN.md")
        en = _read("docs/SPIELWISSEN.en.md")
        self.assertIn("[English](SPIELWISSEN.en.md)", de)
        self.assertIn("[Deutsch](SPIELWISSEN.md)", en)
        self.assertEqual(len(_headings(de, 2)), len(_headings(en, 2)))

    def test_key_measurements_are_in_both(self):
        for name in ("docs/SPIELWISSEN.md", "docs/SPIELWISSEN.en.md"):
            text = _read(name)
            for needle in ("3177", "26, 77, 128, 179, 230", "3493540", "325", "375"):
                self.assertIn(needle, text, f"{name}: {needle}")

    def test_no_private_data(self):
        for name in ("docs/SPIELWISSEN.md", "docs/SPIELWISSEN.en.md"):
            text = _read(name).lower()
            self.assertNotIn("@gmail", text, name)
            self.assertNotIn("steamcommunity.com/id", text, name)
            self.assertNotIn("pettelt", text, name)


class HeightmapGuideTest(unittest.TestCase):

    DE = "docs/ANLEITUNG_HEIGHTMAP.md"
    EN = "docs/ANLEITUNG_HEIGHTMAP.en.md"

    def test_both_languages_link_each_other(self):
        self.assertIn("[English](ANLEITUNG_HEIGHTMAP.en.md)", _read(self.DE))
        self.assertIn("[Deutsch](ANLEITUNG_HEIGHTMAP.md)", _read(self.EN))

    def test_same_structure(self):
        de, en = _read(self.DE), _read(self.EN)
        for level in (2, 3):
            self.assertEqual(len(_headings(de, level)), len(_headings(en, level)), f"Ebene {level}")
        steps_de = re.findall(r"(?m)^(\d+)\. ", de)
        steps_en = re.findall(r"(?m)^(\d+)\. ", en)
        self.assertEqual(steps_de, steps_en)
        self.assertEqual(steps_de[:25], [str(n) for n in range(1, 26)])

    def test_key_facts_in_both(self):
        for name in (self.DE, self.EN):
            text = _read(name)
            for needle in ("3177", "swissALTI3D", "swisstopo", "dl-de/by-2-0", "hoehen_schneegrenze_test.png", "400 m"):
                self.assertIn(needle, text, f"{name}: {needle}")

    def test_step_references_match_the_steps(self):
        for name, marker in ((self.DE, "Höhenfenster begrenzen"), (self.EN, "Höhenfenster begrenzen")):
            text = _read(name)
            line = [l for l in text.splitlines() if l.startswith("15. ")][0]
            self.assertIn(marker, line, name)
            self.assertIn("(Schritt 15)" if name == self.DE else "(step 15)", text, name)

    def test_no_private_data(self):
        for name in (self.DE, self.EN):
            text = _read(name).lower()
            self.assertNotIn("@gmail", text, name)
            self.assertNotIn("steamcommunity.com/id", text, name)


if __name__ == "__main__":
    unittest.main()
