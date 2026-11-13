"""
Bauvorlage als Bild speichern (Knopf "Bauvorlage als Bild..." im Heightmap-Dialog).

Die eigentliche Arbeit macht src/heightmap/build_template.py; hier steht nur die
Bedienung (Dateiauswahl, Wartecursor und Meldungen).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from src.heightmap.build_template import render_build_template, save_build_template
from src.i18n import tr

TITLE = tr("Bauvorlage als Bild")
DEFAULT_METERS_PER_PIXEL = 4.0


def template_size(selection, heightmap_array=None) -> tuple[int, int]:
    """Breite/Hoehe in Pixeln: wie die geladene Heightmap, sonst 4 m je Pixel."""

    if heightmap_array is not None and getattr(heightmap_array, "ndim", 0) == 2:
        h, w = heightmap_array.shape
        return int(w), int(h)

    w = max(2, int(round(selection.width_m / DEFAULT_METERS_PER_PIXEL)))
    h = max(2, int(round(selection.height_m / DEFAULT_METERS_PER_PIXEL)))
    return w, h


def save_build_template_dialog(parent, selection, osm, heightmap_array=None) -> bool:
    """Fragt den Speicherort ab und schreibt die Vorlage als .tga und .png."""

    chosen, _filter = QFileDialog.getSaveFileName(
        parent,
        TITLE,
        str(Path.home() / "bauvorlage.tga"),
        tr("TGA-Bild (*.tga)"),
    )

    if not chosen:
        return False

    w_px, h_px = template_size(selection, heightmap_array)

    QApplication.setOverrideCursor(Qt.WaitCursor)

    try:
        image = render_build_template(osm, selection, w_px, h_px)
        paths = save_build_template(image, chosen)
    except (OSError, ValueError, MemoryError) as error:
        QApplication.restoreOverrideCursor()
        QMessageBox.warning(parent, TITLE, tr("Die Bauvorlage konnte nicht gespeichert werden:\n{error}").format(error=error))
        return False

    QApplication.restoreOverrideCursor()

    QMessageBox.information(
        parent,
        TITLE,
        tr("Bauvorlage gespeichert ({w} × {h} Pixel, gleiches Raster wie die Heightmap):\n{files}\n\n"
        "Straßen nach Klasse eingefärbt, Gleise schwarz-weiß geblockt, Bahnsteige grau. "
        "Im Spiel wird nichts gebaut.").format(
            w=w_px, h=h_px, files="\n".join(str(p) for p in paths)
        ),
    )
    return True
