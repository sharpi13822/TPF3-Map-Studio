"""
Filter fuer den PyInstaller-Build (wird von build.spec benutzt).

Entfernt Dateien, die das Studio nicht braucht, damit das Paket kleiner wird:
andere Sprachen von QtWebEngine und Qt, die Entwicklerwerkzeuge des Browsers,
die QML-Module (das Studio nutzt nur Widgets) und die AVIF-Erweiterung von Pillow.

Die DLLs von Qt (auch Quick, Qml, Pdf) bleiben, weil QtWebEngine daran haengen kann.
"""

from __future__ import annotations

import re

BEHALTENE_WEBENGINE_SPRACHEN = frozenset({"de.pak", "en-US.pak", "en-GB.pak"})
BEHALTENE_QT_SPRACHEN = frozenset({"de", "en"})

# Falls die Karte im fertigen Programm Probleme macht: auf False setzen.
QML_ENTFERNEN = True

_QM = re.compile(r"^(?P<basis>.+?)_(?P<sprache>[a-z]{2,3})(?:_[A-Za-z]+)?\.qm$")
_QML = re.compile(r"(^|/)PySide6/(Qt/)?qml/")


def soll_behalten(ziel: str) -> bool:
    """True, wenn die Datei (Zielpfad im Paket) mitgepackt werden soll."""

    pfad = ziel.replace("\\", "/")
    name = pfad.rsplit("/", 1)[-1]

    if "qtwebengine_locales/" in pfad:
        return name in BEHALTENE_WEBENGINE_SPRACHEN

    if name == "qtwebengine_devtools_resources.pak":
        return False

    if pfad.endswith(".qm") and "/translations/" in pfad:
        treffer = _QM.match(name)
        return treffer is None or treffer.group("sprache") in BEHALTENE_QT_SPRACHEN

    if QML_ENTFERNEN and _QML.search(pfad):
        return False

    if name.startswith("_avif") and "PIL/" in pfad:
        return False

    return True