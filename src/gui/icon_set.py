"""
Symbole des Studios (PNG in src/gui/icons) und ihre Zuordnung zu Menue- und Werkzeugleisten-Eintraegen.

Jedes Symbol gibt es in vier Farben: name.png (Akzent-Blau), name_hell.png (Standard in Leisten und Menues),
name_weiss.png (aktiver Knopf auf Blau) und name_grau.png (deaktiviert).
"""

from __future__ import annotations

from pathlib import Path

ICON_DIR = Path(__file__).resolve().parent / "icons"

VARIANTS = ("", "_hell", "_weiss", "_grau")

# (Stichwort im Text oder Tooltip, Symbolname). Die erste passende Zeile gilt, also steht Genaueres oben.
ACTION_ICONS = (
    ("neues projekt", "neu"),
    ("dashboard", "dashboard"),
    ("eigenschaften", "eigenschaften"),
    ("funktionsübersicht", "funktionsuebersicht"),
    ("import-anleitung", "anleitung"),
    ("json export", "json_export"),
    ("json import", "json_import"),
    ("öffnen", "oeffnen"),
    ("projekt schließen", "schliessen"),
    ("speichern", "speichern"),
    ("beenden", "beenden"),
    ("rückgängig", "rueckgaengig"),
    ("wiederholen", "wiederholen"),
    ("rechteck", "rechteck"),
    ("marker", "marker"),
    ("auswahl", "auswahl"),
    ("mess", "messen"),
    ("zeichn", "zeichnen"),
    ("osm laden", "osm_laden"),
    ("overpass", "overpass"),
    ("heightmap", "heightmap"),
    ("vorab", "vorab_pruefung"),
)


def icon_path(name: str, variant: str = "_hell") -> Path:
    return ICON_DIR / f"{name}{variant}.png"


def icon_name_for(text: str, tooltip: str = "") -> str | None:
    """Passenden Symbolnamen zu einem Aktionstext finden, sonst None."""

    haystack = f"{text} {tooltip}".replace("&", "").lower()

    for keyword, name in ACTION_ICONS:
        if keyword in haystack:
            return name

    return None


def icon(name: str, checkable: bool = False):
    """
    QIcon fuer ein Symbol: hell im Normalzustand, grau wenn deaktiviert. Bei umschaltbaren Knoepfen
    wird im eingeschalteten Zustand die weisse Variante gezeigt (der Knopf ist dann blau gefuellt).
    """

    from PySide6.QtCore import QSize
    from PySide6.QtGui import QIcon

    result = QIcon()
    size = QSize()

    result.addFile(str(icon_path(name, "_hell")), size, QIcon.Mode.Normal, QIcon.State.Off)
    result.addFile(str(icon_path(name, "_grau")), size, QIcon.Mode.Disabled, QIcon.State.Off)

    if checkable:
        result.addFile(str(icon_path(name, "_weiss")), size, QIcon.Mode.Normal, QIcon.State.On)
        result.addFile(str(icon_path(name, "_weiss")), size, QIcon.Mode.Active, QIcon.State.On)

    return result
