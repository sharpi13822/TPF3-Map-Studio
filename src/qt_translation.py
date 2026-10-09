"""
Uebersetzungen von Qt selbst (Standardknoepfe wie OK, Abbrechen, Ja, Nein,
Speichern in Qt-eigenen Dialogen).

Qt waehlt diese Texte nach der Systemsprache. Das Studio hat aber eine eigene
Sprachwahl, deshalb wird hier die passende Qt-Uebersetzung (qtbase_de.qm bzw.
qtbase_en.qm) passend zur gewaehlten Sprache geladen. Windows-eigene
Dateidialoge richten sich weiter nach der Windows-Sprache.
"""

from __future__ import annotations

import sys
from pathlib import Path

QT_BASES = ("qtbase",)


def translation_directories() -> list[Path]:
    """Ordner, in denen die .qm-Dateien von Qt liegen koennten."""

    directories: list[Path] = []

    try:
        from PySide6.QtCore import QLibraryInfo

        directories.append(
            Path(QLibraryInfo.path(QLibraryInfo.LibraryPath.TranslationsPath))
        )
    except Exception:
        pass

    try:
        import PySide6

        directories.append(Path(PySide6.__file__).parent / "Qt" / "translations")
    except Exception:
        pass

    # Eingefrorenes Programm (PyInstaller)
    base = getattr(sys, "_MEIPASS", None)
    if base:
        directories.append(Path(base) / "PySide6" / "Qt" / "translations")

    return directories


def find_translation_files(language: str, directories=None) -> list[Path]:
    """Vorhandene Qt-Uebersetzungsdateien fuer die Sprache ("de" / "en")."""

    if directories is None:
        directories = translation_directories()

    found: list[Path] = []

    for base in QT_BASES:
        for directory in directories:
            candidate = Path(directory) / f"{base}_{language}.qm"
            if candidate.is_file():
                found.append(candidate)
                break

    return found


def install_qt_translations(app, language: str, directories=None) -> list:
    """Setzt die Qt-Sprache und laedt die Uebersetzungen. Gibt die Translator zurueck."""

    from PySide6.QtCore import QLocale, QTranslator

    QLocale.setDefault(QLocale(language))

    translators = []

    for path in find_translation_files(language, directories):
        translator = QTranslator(app)
        if translator.load(str(path)):
            app.installTranslator(translator)
            translators.append(translator)

    return translators
