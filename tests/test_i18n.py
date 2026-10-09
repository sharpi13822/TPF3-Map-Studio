"""Tests fuer das Uebersetzungssystem (Deutsch / English).

Der deutsche Originaltext ist der Schluessel: tr("Speichern unter...").
Diese Tests sorgen dafuer, dass
- jeder Text im Programm einen englischen Eintrag hat,
- kein englischer Eintrag uebrig bleibt, wenn der deutsche Text geaendert wurde,
- Platzhalter wie {name} in beiden Sprachen gleich sind,
- die Sprachwahl (Erkennung, Speichern, Start) wie geplant funktioniert.
"""

import ast
import os
import string
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from src import i18n
from src.i18n_en import CATALOG

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

# Texte, die auf Englisch bewusst genauso heissen wie auf Deutsch.
SAME_IN_BOTH = {
    "ID:",
    "Name:",
    "Marker",
    "Parks",
    "Vegetation",
    "Heightmap",
    "JSON (*.json)",
    "PNG (*.png)",
    "Lua (*.lua)",
    "Mod",
    "Status",
    "Marker: {id} | {lat:.6f}, {lon:.6f}",
}

# Texte, die nicht als tr("...") im Quelltext stehen, sondern zur Laufzeit
# uebersetzt werden (Layer.label ruft tr(self.value) auf).
DYNAMIC_FILES = {"map/layer.py"}


def _module_constants(tree):
    result = {}
    for node in tree.body:
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            result[node.targets[0].id] = node.value.value
    return result


def collect_keys():
    """Alle Texte aus tr("...") bzw. tr(KONSTANTE) im Ordner src.

    Gibt (Schluessel -> Dateien, Liste nicht aufloesbarer Aufrufe) zurueck.
    """
    keys = {}
    unresolved = []
    for path in sorted(SRC.rglob("*.py")):
        relative = path.relative_to(SRC).as_posix()
        if relative in ("i18n.py", "i18n_en.py"):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        constants = _module_constants(tree)
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "tr"
            ):
                continue
            if len(node.args) != 1 or node.keywords:
                unresolved.append(f"{relative}:{node.lineno}")
                continue
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                keys.setdefault(arg.value, []).append(relative)
            elif isinstance(arg, ast.Name) and arg.id in constants:
                keys.setdefault(constants[arg.id], []).append(relative)
            elif relative not in DYNAMIC_FILES:
                unresolved.append(f"{relative}:{node.lineno}")
    return keys, unresolved


def placeholders(text):
    """Menge der (Feldname, Formatangabe) eines Formattexts."""
    return {
        (field, spec)
        for _literal, field, spec, _conversion in string.Formatter().parse(text)
        if field is not None
    }


class LanguageRestoringTest(unittest.TestCase):
    """Stellt die Sprache nach jedem Test wieder auf Deutsch."""

    def setUp(self):
        i18n.set_language("de")

    def tearDown(self):
        i18n.set_language("de")


class TranslateTest(LanguageRestoringTest):

    def test_german_returns_the_text_unchanged(self):
        self.assertEqual(i18n.tr("Speichern unter..."), "Speichern unter...")

    def test_english_uses_the_catalog(self):
        i18n.set_language("en")
        self.assertEqual(i18n.tr("Speichern unter..."), "Save as...")

    def test_unknown_text_falls_back_to_german(self):
        i18n.set_language("en")
        self.assertEqual(i18n.tr("Dieser Text steht in keinem Katalog"), "Dieser Text steht in keinem Katalog")

    def test_unknown_language_falls_back_to_german(self):
        self.assertEqual(i18n.set_language("fr"), "de")
        self.assertEqual(i18n.get_language(), "de")
        self.assertEqual(i18n.set_language(None), "de")

    def test_placeholders_survive_the_translation(self):
        i18n.set_language("en")
        text = i18n.tr("Projektname geändert: {name}").format(name="Rheintal")
        self.assertEqual(text, "Project name changed: Rheintal")

    def test_translate_to_does_not_change_the_active_language(self):
        self.assertEqual(i18n.translate_to("Datei", "en"), "File")
        self.assertEqual(i18n.get_language(), "de")

    def test_default_language_is_german(self):
        self.assertEqual(i18n.DEFAULT_LANGUAGE, "de")
        self.assertEqual(i18n.SUPPORTED_LANGUAGES, ("de", "en"))


class SystemLanguageTest(unittest.TestCase):

    def test_german_locales(self):
        for name in ("de-DE", "de_AT", "de-CH", "de", "German_Germany.1252", "DE_de"):
            self.assertEqual(i18n.language_from_locale(name), "de", name)

    def test_other_locales_become_english(self):
        for name in ("en-US", "en_GB.UTF-8", "fr-FR", "pl-PL", "ja-JP", "nl-NL"):
            self.assertEqual(i18n.language_from_locale(name), "en", name)

    def test_unknown_locale_stays_german(self):
        for name in ("", None, "C", "POSIX", "  "):
            self.assertEqual(i18n.language_from_locale(name), "de", repr(name))

    def test_detect_uses_the_system_locale_name(self):
        with mock.patch.object(i18n, "system_locale_name", return_value="en-US"):
            self.assertEqual(i18n.detect_system_language(), "en")
        with mock.patch.object(i18n, "system_locale_name", return_value="de-DE"):
            self.assertEqual(i18n.detect_system_language(), "de")


class SavedLanguageTest(LanguageRestoringTest):

    def setUp(self):
        super().setUp()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "TPF3-Map-Studio" / "settings.ini"

    def test_nothing_saved_by_default(self):
        self.assertIsNone(i18n.load_saved_language(self.path))

    def test_save_and_load_roundtrip(self):
        self.assertTrue(i18n.save_language("en", self.path))
        self.assertEqual(i18n.load_saved_language(self.path), "en")
        self.assertTrue(i18n.save_language("de", self.path))
        self.assertEqual(i18n.load_saved_language(self.path), "de")

    def test_unknown_language_is_not_saved(self):
        self.assertFalse(i18n.save_language("fr", self.path))
        self.assertFalse(self.path.exists())

    def test_broken_file_is_ignored(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("das ist keine ini-datei\n[[[", encoding="utf-8")
        self.assertIsNone(i18n.load_saved_language(self.path))

    def test_invalid_value_in_file_is_ignored(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("[general]\nlanguage = klingonisch\n", encoding="utf-8")
        self.assertIsNone(i18n.load_saved_language(self.path))

    def test_saving_keeps_other_settings(self):
        self.path.parent.mkdir(parents=True)
        self.path.write_text("[general]\nanderes = 1\n", encoding="utf-8")
        i18n.save_language("en", self.path)
        text = self.path.read_text(encoding="utf-8")
        self.assertIn("anderes = 1", text)
        self.assertIn("language = en", text)

    def test_settings_path_uses_appdata(self):
        with mock.patch.dict(os.environ, {"APPDATA": self._tmp.name}):
            self.assertEqual(
                i18n.settings_path(),
                Path(self._tmp.name) / "TPF3-Map-Studio" / "settings.ini",
            )


class InitLanguageTest(LanguageRestoringTest):

    def setUp(self):
        super().setUp()
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.path = Path(self._tmp.name) / "settings.ini"

    def test_first_start_takes_the_system_language(self):
        self.assertEqual(i18n.init_language(self.path, detect=lambda: "en"), "en")
        self.assertEqual(i18n.get_language(), "en")

    def test_first_start_does_not_write_a_file(self):
        i18n.init_language(self.path, detect=lambda: "en")
        self.assertFalse(self.path.exists())

    def test_saved_choice_beats_the_system_language(self):
        i18n.save_language("de", self.path)
        self.assertEqual(i18n.init_language(self.path, detect=lambda: "en"), "de")
        i18n.save_language("en", self.path)
        self.assertEqual(i18n.init_language(self.path, detect=lambda: "de"), "en")

    def test_failing_detection_falls_back_to_german(self):
        def broken():
            raise OSError("kein Gebietsschema")

        self.assertEqual(i18n.init_language(self.path, detect=broken), "de")


class CatalogTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.keys, cls.unresolved = collect_keys()

    def test_all_calls_can_be_checked(self):
        self.assertEqual(self.unresolved, [], "tr() nur mit einem festen Text oder einer Konstante aufrufen")

    def test_every_text_has_an_english_entry(self):
        missing = sorted(key for key in self.keys if key not in CATALOG)
        self.assertEqual(missing, [], "fehlt in src/i18n_en.py")

    def test_no_stale_english_entries(self):
        from src.map.layer import Layer

        known = set(self.keys) | {layer.value for layer in Layer}
        stale = sorted(key for key in CATALOG if key not in known)
        self.assertEqual(stale, [], "steht in src/i18n_en.py, aber nirgends mehr im Programm")

    def test_layer_names_are_translated(self):
        from src.map.layer import Layer

        for layer in Layer:
            self.assertIn(layer.value, CATALOG, layer.name)

    def test_layer_label_follows_the_language(self):
        from src.map.layer import Layer

        try:
            i18n.set_language("en")
            self.assertEqual(Layer.ROADS.label, "Roads")
            self.assertEqual(Layer.ROADS.value, "Straßen")
            i18n.set_language("de")
            self.assertEqual(Layer.ROADS.label, "Straßen")
        finally:
            i18n.set_language("de")

    def test_placeholders_match_in_both_languages(self):
        for german, english in CATALOG.items():
            self.assertEqual(placeholders(german), placeholders(english), german)

    def test_english_entries_are_real_translations(self):
        for german, english in CATALOG.items():
            self.assertTrue(english.strip(), german)
            if german not in SAME_IN_BOTH:
                self.assertNotEqual(german, english, f"nicht uebersetzt: {german}")

    def test_english_entries_contain_no_german_letters(self):
        for german, english in CATALOG.items():
            for letter in "äöüÄÖÜß":
                self.assertNotIn(letter, english, german)

    def test_newlines_and_ellipsis_match(self):
        for german, english in CATALOG.items():
            if "<" not in german:  # HTML-Hilfetexte werden frei umbrochen
                self.assertEqual(german.count("\n"), english.count("\n"), german)
            self.assertEqual(german.endswith("..."), english.endswith("..."), german)
            self.assertEqual(german.endswith(":"), english.endswith(":"), german)


class FormatCallsTest(unittest.TestCase):
    """tr("... {name} ...").format(name=...) braucht genau die Felder des Textes."""

    def test_format_arguments_match_the_placeholders(self):
        checked = 0
        for path in sorted(SRC.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Attribute)
                    and node.func.attr == "format"
                    and isinstance(node.func.value, ast.Call)
                    and isinstance(node.func.value.func, ast.Name)
                    and node.func.value.func.id == "tr"
                ):
                    continue
                argument = node.func.value.args[0]
                where = f"{path.name}:{node.lineno}"
                self.assertIsInstance(argument, ast.Constant, where)
                self.assertEqual(node.args, [], where)
                given = {keyword.arg for keyword in node.keywords}
                needed = {field for field, _spec in placeholders(argument.value)}
                self.assertEqual(given, needed, where)
                checked += 1
        self.assertGreaterEqual(checked, 10)

    def test_no_f_string_inside_tr(self):
        # Ein f-String im tr()-Aufruf waere als Schluessel nie im Katalog zu finden.
        for path in sorted(SRC.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "tr"
                    and node.args
                ):
                    self.assertNotIsInstance(node.args[0], ast.JoinedStr, f"{path.name}:{node.lineno}")


class LanguageMenuWiringTest(unittest.TestCase):
    """Das Sprachmenue ist eingebaut und die Sprache steht vor dem Fenster fest."""

    def setUp(self):
        self.window = (SRC / "window.py").read_text(encoding="utf-8")
        self.main = (SRC / "main.py").read_text(encoding="utf-8")

    def test_menu_offers_german_and_english(self):
        self.assertIn('menu.addMenu("Sprache / Language")', self.window)
        self.assertIn('("de", "Deutsch")', self.window)
        self.assertIn('("en", "English")', self.window)

    def test_menu_name_is_not_translated(self):
        self.assertNotIn('tr("Sprache / Language")', self.window)

    def test_choice_is_saved_and_needs_a_restart(self):
        body = self.window[self.window.index("def _language_chosen"):]
        body = body[: body.index("# Toolbar")]
        self.assertIn("save_language(code)", body)
        self.assertIn("Neustart", body)
        self.assertIn("restart", body)

    def test_language_is_set_before_the_window_is_imported(self):
        self.assertLess(
            self.main.index("init_language()"),
            self.main.index("from src.window import MainWindow"),
        )

    def test_settings_are_not_read_in_the_module_import(self):
        # Tests und Importe duerfen keine Datei lesen: nur init_language() tut das.
        core = (SRC / "i18n.py").read_text(encoding="utf-8")
        self.assertNotIn("\ninit_language()", core)


if __name__ == "__main__":
    unittest.main()
