import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _relative_targets(text):
    targets = re.findall(r'\]\(([^)\s]+)\)', text) + re.findall(r'src="([^"]+)"', text)
    for target in targets:
        if re.match(r'^(https?:|mailto:|#|\.\./)', target):
            continue
        yield target.split('#')[0]


class ReadmeTest(unittest.TestCase):

    def setUp(self):
        self.readme = (ROOT / "README.md").read_text(encoding="utf-8")

    def test_relative_links_exist(self):
        for target in _relative_targets(self.readme):
            self.assertTrue((ROOT / target).exists(), f"fehlt: {target}")

    def test_notices_links_exist(self):
        text = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        for target in _relative_targets(text):
            self.assertTrue((ROOT / target).exists(), f"fehlt: {target}")

    def test_no_stale_claims(self):
        for stale in ("Mod-Checker gegen", "Eingebaute Anleitung", "python src/main.py", "Transport Fever 2 vorzubereiten"):
            self.assertNotIn(stale, self.readme)

    def test_required_sections(self):
        for heading in ("## Fragen, Probleme und Kontakt", "## Unterstützung", "## Lizenz", "## Funktionen"):
            self.assertIn(heading, self.readme)

    def test_contact_and_donate_links(self):
        self.assertIn("https://github.com/sharpi13822/TPF3-Map-Studio/issues", self.readme)
        self.assertIn("https://github.com/sharpi13822/TPF3-Map-Studio/discussions", self.readme)
        self.assertIn("https://paypal.me/PEttelt", self.readme)

    def test_requirements_are_named_in_notices(self):
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8").lower()
        req = (ROOT / "requirements.txt").read_text(encoding="utf-8")
        for line in req.splitlines():
            name = re.split(r"[=<>!~ ]", line.strip(), maxsplit=1)[0].lower()
            if name:
                self.assertIn(name, notices, f"nicht in THIRD_PARTY_NOTICES.md: {name}")

    def test_relief_source_is_named(self):
        notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
        self.assertIn("github.com/tilezen/joerd/blob/master/docs/attribution.md", notices)
        self.assertIn("elevation-tiles-prod", notices)


if __name__ == "__main__":
    unittest.main()
