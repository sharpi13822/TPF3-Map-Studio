import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "tools" / "make_release.ps1"


class ReleaseScriptTest(unittest.TestCase):

    def setUp(self):
        self.text = SCRIPT.read_text(encoding="utf-8")

    def test_script_exists_and_takes_version(self):
        self.assertIn("param(", self.text)
        self.assertIn('[string]$Version = "0.3.0"', self.text)

    def test_build_steps(self):
        for needle in ("-m PyInstaller build.spec --noconfirm", "$LASTEXITCODE", "dist\\TPF3-Map-Studio",
                       "TPF3-Map-Studio.exe", "strassen_hell.png", "Compress-Archive", "Get-FileHash",
                       "-win64.zip", ".sha256.txt"):
            self.assertIn(needle, self.text, needle)

    def test_files_next_to_exe(self):
        for needle in ("START-HIER.txt", "LICENSE", "THIRD_PARTY_NOTICES.md", "Copy-Item"):
            self.assertIn(needle, self.text, needle)

    def test_start_here_file(self):
        start = (ROOT / "tools" / "START-HIER.txt").read_text(encoding="utf-8-sig")
        for needle in ("KOMPLETT entpacken", "TPF3-Map-Studio.exe", "_internal", "Trotzdem ausfuehren",
                       "swissALTI3D", "issues", "discussions", "LICENSE"):
            self.assertIn(needle, start, needle)

    def test_stops_on_errors(self):
        self.assertIn('$ErrorActionPreference = "Stop"', self.text)
        self.assertGreaterEqual(self.text.count("throw "), 4)

    def test_script_is_ascii_safe(self):
        # Windows PowerShell 5 liest Skripte ohne BOM als ANSI: keine Umlaute im Skript
        self.text.encode("ascii")

    def test_readme_names_the_script(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("tools\\make_release.ps1", readme)
        self.assertIn("Höhenquellen im Überblick", readme)
        self.assertIn("swissALTI3D", readme)

    def test_release_zip_is_not_tracked(self):
        gitignore = ROOT / ".gitignore"
        if gitignore.exists():
            text = gitignore.read_text(encoding="utf-8")
            self.assertTrue("*.zip" in text or "TPF3-Map-Studio-v" in text, ".gitignore sollte die Release-ZIP ausschliessen")


if __name__ == "__main__":
    unittest.main()
