"""Zentrales Uebersetzungssystem (Deutsch / English).

Prinzip: Der deutsche Originaltext ist der Schluessel.

    tr("Speichern unter...")

Deutsch gibt den Text unveraendert zurueck. Fuer English steht die
Uebersetzung in ``src/i18n_en.py`` (Woerterbuch Deutsch -> English). Fehlt
dort ein Eintrag, wird der deutsche Text angezeigt - das Programm
funktioniert also auch mit einer unvollstaendigen Uebersetzung.

Texte mit Platzhaltern werden so geschrieben:

    tr("Projektname geaendert: {name}").format(name=name)

Die Sprache wird einmal beim Start festgelegt (``init_language()`` in
``main.py``, BEVOR ``src.window`` importiert wird). Ein Wechsel im Menue
wird gespeichert und wirkt nach einem Neustart. Dieses Modul kennt kein Qt
und liest/schreibt nur eine kleine Ini-Datei, damit es ohne Programmfenster
testbar ist.
"""

import configparser
import json
import locale
import os
import sys
from pathlib import Path

SUPPORTED_LANGUAGES = ("de", "en")
DEFAULT_LANGUAGE = "de"

# Ordner und Datei fuer die gespeicherte Sprachwahl (unter %APPDATA%).
SETTINGS_DIR_NAME = "TPF3-Map-Studio"
SETTINGS_FILE_NAME = "settings.ini"

_language = DEFAULT_LANGUAGE
_catalogs = {}


def get_language():
    """Aktive Sprache: "de" oder "en"."""
    return _language


def set_language(language):
    """Setzt die aktive Sprache. Unbekannte Werte fallen auf Deutsch zurueck."""
    global _language
    _language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE
    return _language


def _catalog(language):
    """Woerterbuch der Sprache (Deutsch ist die Quelle und hat keines)."""
    if language == DEFAULT_LANGUAGE:
        return {}
    if language not in _catalogs:
        if language == "en":
            from src.i18n_en import CATALOG as catalog
        else:
            catalog = {}
        _catalogs[language] = catalog
    return _catalogs[language]


def web_dictionary(language=None):
    """Woerterbuch der Kartenoberflaeche (Deutsch -> Sprache). Bei Deutsch leer."""
    language = language or _language
    if language == DEFAULT_LANGUAGE:
        return {}
    if language == "en":
        from src.i18n_web_en import WEB_CATALOG
        return dict(WEB_CATALOG)
    return {}


def web_script(language=None):
    """JavaScript fuer die Karte: window.TPF_LANG und window.TPF_I18N."""
    language = language or _language
    return (
        "window.TPF_LANG = " + json.dumps(language) + ";\n"
        "window.TPF_I18N = "
        + json.dumps(web_dictionary(language), ensure_ascii=False)
        + ";\n"
    )


def tr(text):
    """Uebersetzt einen deutschen Originaltext in die aktive Sprache."""
    if _language == DEFAULT_LANGUAGE:
        return text
    return _catalog(_language).get(text, text)


def translate_to(text, language):
    """Wie tr(), aber fuer eine bestimmte Sprache (fuer Tests und Menuetexte)."""
    if language == DEFAULT_LANGUAGE:
        return text
    return _catalog(language).get(text, text)


# ---------------------------------------------------------------------
# Sprache des Systems
# ---------------------------------------------------------------------

def _windows_locale_name():
    """Anzeigesprache bzw. Gebietsschema von Windows, z.B. "de-DE"."""
    import ctypes

    buffer = ctypes.create_unicode_buffer(85)
    if ctypes.windll.kernel32.GetUserDefaultLocaleName(buffer, len(buffer)):
        return buffer.value
    return ""


def system_locale_name():
    """Name des Gebietsschemas, z.B. "de-DE" oder "en_US". Leer, wenn unbekannt."""
    try:
        if sys.platform == "win32":
            name = _windows_locale_name()
            if name:
                return name
    except Exception:  # noqa: BLE001 - die Erkennung darf den Start nie stoeren
        pass
    for key in ("LC_ALL", "LC_MESSAGES", "LANG"):
        value = os.environ.get(key, "")
        if value:
            return value
    try:
        return locale.getlocale()[0] or ""
    except Exception:  # noqa: BLE001
        return ""


def language_from_locale(name):
    """"de-DE", "de_AT", "German_Germany" -> "de"; andere Sprachen -> "en".

    Ist das Gebietsschema unbekannt (leer, "C", "POSIX"), bleibt es bei
    Deutsch, damit sich fuer bisherige Nutzer nichts aendert.
    """
    lowered = (name or "").strip().lower()
    if lowered in ("", "c", "posix"):
        return DEFAULT_LANGUAGE
    if lowered.startswith("de") or lowered.startswith("german"):
        return "de"
    return "en"


def detect_system_language():
    """Deutsch, wenn Windows (oder das System) deutsch ist, sonst English."""
    return language_from_locale(system_locale_name())


# ---------------------------------------------------------------------
# Gespeicherte Wahl
# ---------------------------------------------------------------------

def settings_path():
    """Pfad der Einstellungsdatei: %APPDATA%\\TPF3-Map-Studio\\settings.ini."""
    base = os.environ.get("APPDATA")
    root = Path(base) if base else Path.home() / ".config"
    return root / SETTINGS_DIR_NAME / SETTINGS_FILE_NAME


def load_saved_language(path=None):
    """Gespeicherte Sprache oder None (keine Datei, kein Eintrag, ungueltig)."""
    path = Path(path) if path is not None else settings_path()
    parser = configparser.ConfigParser()
    try:
        parser.read(path, encoding="utf-8")
        value = parser.get("general", "language", fallback="").strip().lower()
    except (OSError, configparser.Error):
        return None
    return value if value in SUPPORTED_LANGUAGES else None


def save_language(language, path=None):
    """Speichert die Sprachwahl. Gibt True zurueck, wenn es geklappt hat."""
    if language not in SUPPORTED_LANGUAGES:
        return False
    path = Path(path) if path is not None else settings_path()
    parser = configparser.ConfigParser()
    try:
        parser.read(path, encoding="utf-8")
    except (OSError, configparser.Error):
        parser = configparser.ConfigParser()
    if not parser.has_section("general"):
        parser.add_section("general")
    parser.set("general", "language", language)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            parser.write(handle)
    except OSError:
        return False
    return True


def init_language(path=None, detect=None):
    """Legt die Sprache beim Programmstart fest.

    Reihenfolge: gespeicherte Wahl, sonst Sprache des Systems. Beim ersten
    Start wird nichts gespeichert - gespeichert wird erst, wenn die Person im
    Menue selbst eine Sprache waehlt.
    """
    saved = load_saved_language(path)
    if saved is not None:
        return set_language(saved)
    detect = detect or detect_system_language
    try:
        return set_language(detect())
    except Exception:  # noqa: BLE001
        return set_language(DEFAULT_LANGUAGE)
