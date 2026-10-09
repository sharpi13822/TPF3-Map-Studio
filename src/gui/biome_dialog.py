"""
Dialog "Biome-Maske aus OSM": erzeugt aus der geladenen OSM-Landnutzung eine
8-Bit-Graustufen-Maske fuer den Biome-Tab im TPF3-Karteneditor.

Die Voreinstellung (welche OSM-Flaeche zu welchem Biom gehoert) ist ein
Vorschlag und im Spiel noch nicht geprueft.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from src.heightmap.biome_mask import (
    BIOME_NAMES,
    CATEGORIES,
    DEFAULT_ASSIGNMENT,
    build_biome_index,
    index_to_preview_rgb,
    mask_size_for_selection,
    save_biome_png,
    thin_forest_by_height,
)
from src.heightmap.tpf3_paths import find_tpf3_heightmaps_folder
from src.i18n import tr

# Anzeige -> Meter pro Pixel
_RESOLUTIONS = (
    (tr("16 m pro Pixel (klein, schnell)"), 16.0),
    (tr("8 m pro Pixel (Standard)"), 8.0),
    (tr("4 m pro Pixel (wie die Heightmap)"), 4.0),
)

_PREVIEW_HEIGHT = 480


class BiomeMaskDialog(QDialog):

    def __init__(
        self,
        parent,
        selection,
        osm,
        heights=None,
        water_level_m=0.0,
        default_limit_m=340.0,
    ):
        super().__init__(parent)

        self.selection = selection
        self.osm = osm
        self._heights = heights
        self._water_level_m = float(water_level_m)
        self._index: np.ndarray | None = None

        self.setWindowTitle(tr("Biome-Maske aus OSM"))

        layout = QVBoxLayout(self)

        info = QLabel(
            tr("Erzeugt aus der geladenen OSM-Landnutzung eine Maske für den "
            "Biome-Tab im Karteneditor. Wähle für jede Art von Fläche das "
            "Biom. Alles andere, auch Wasser, bekommt Biom 0. Die "
            "Voreinstellung ist ein Vorschlag nach dem Aussehen der Biome "
            "und im Spiel noch nicht geprüft.")
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        form = QFormLayout()
        layout.addLayout(form)

        self.category_boxes: dict[str, QComboBox] = {}

        for key, label, _rules in CATEGORIES:

            box = QComboBox()
            box.addItem(tr("nicht verwenden"), None)

            for number, name in enumerate(BIOME_NAMES):
                box.addItem(name, number)

            default = DEFAULT_ASSIGNMENT.get(key)

            box.setCurrentIndex(0 if default is None else default + 1)

            self.category_boxes[key] = box

            form.addRow(label + ":", box)

        self.resolution_box = QComboBox()

        for text, value in _RESOLUTIONS:
            self.resolution_box.addItem(text, value)

        self.resolution_box.setCurrentIndex(1)

        form.addRow(tr("Auflösung:"), self.resolution_box)

        self.thin_checkbox = QCheckBox(tr("Bäume in der Höhe ausdünnen"))
        self.thin_checkbox.setToolTip(
            tr("Ersetzt Biom 1 (Wiese mit Baumgruppen) ab der Grenze durch "
               "ein Biom ohne Bäume. Die Höhe kommt aus dem Heightmap-Dialog "
               "(mit allen Einstellungen). Ob die übrigen Biome Bäume "
               "haben, ist im Spiel nicht geprüft.")
        )
        self.thin_checkbox.setEnabled(self._heights is not None)
        form.addRow(self.thin_checkbox)

        self.thin_limit_input = QDoubleSpinBox()
        self.thin_limit_input.setRange(0.0, 1000.0)
        self.thin_limit_input.setDecimals(0)
        self.thin_limit_input.setSuffix(" m")
        self.thin_limit_input.setValue(float(default_limit_m))
        form.addRow(tr("Baumgrenze (m über Wasser):"), self.thin_limit_input)

        self.thin_biome_box = QComboBox()
        self.thin_biome_box.addItem(BIOME_NAMES[0], 0)
        self.thin_biome_box.addItem(BIOME_NAMES[2], 2)
        form.addRow(tr("Ersatzbiom:"), self.thin_biome_box)

        self.preview_label = QLabel(tr("Noch keine Vorschau."))
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        row = QHBoxLayout()
        layout.addLayout(row)

        self.preview_button = QPushButton(tr("Vorschau"))
        self.preview_button.clicked.connect(self._make_preview)
        row.addWidget(self.preview_button)

        self.export_button = QPushButton(tr("Exportieren..."))
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(self._export)
        row.addWidget(self.export_button)

        close_button = QPushButton(tr("Schließen"))
        close_button.clicked.connect(self.reject)
        row.addWidget(close_button)

    # ---------------------------------------------------------

    def _assignment(self) -> dict[str, int | None]:

        return {
            key: box.currentData()
            for key, box in self.category_boxes.items()
        }

    def _make_preview(self):

        assignment = self._assignment()

        if all(value is None for value in assignment.values()):
            QMessageBox.information(
                self,
                tr("Biome-Maske"),
                tr("Es ist keine Fläche einem Biom zugeordnet."),
            )
            return

        meters_per_pixel = float(self.resolution_box.currentData())

        w_px, h_px = mask_size_for_selection(
            self.selection, meters_per_pixel
        )

        self.status_label.setText(tr("Berechne Maske ..."))
        self.repaint()

        try:
            index = build_biome_index(
                self.osm, self.selection, w_px, h_px, assignment
            )
        except Exception as error:
            self.status_label.setText("")
            QMessageBox.warning(
                self,
                tr("Biome-Maske"),
                tr("Die Maske konnte nicht berechnet werden:\n{error}").format(error=error),
            )
            return

        if self.thin_checkbox.isChecked() and self._heights is not None:
            index = thin_forest_by_height(
                index,
                self._heights,
                self._water_level_m,
                self.thin_limit_input.value(),
                int(self.thin_biome_box.currentData()),
            )

        self._index = index

        rgb = np.ascontiguousarray(index_to_preview_rgb(index))

        image = QImage(
            rgb.data,
            rgb.shape[1],
            rgb.shape[0],
            rgb.shape[1] * 3,
            QImage.Format_RGB888,
        ).copy()

        self.preview_label.setPixmap(
            QPixmap.fromImage(image).scaledToHeight(
                _PREVIEW_HEIGHT, Qt.SmoothTransformation
            )
        )

        counts = np.bincount(index.ravel(), minlength=len(BIOME_NAMES))
        total = max(1, int(counts.sum()))

        parts = [
            f"{BIOME_NAMES[i].split(' - ')[0]}: {100 * counts[i] / total:.0f} %"
            for i in range(len(BIOME_NAMES))
            if counts[i] > 0
        ]

        self.status_label.setText(
            tr("Maske {w_px} x {h_px} Pixel. ").format(w_px=w_px, h_px=h_px) + ", ".join(parts)
        )

        self.export_button.setEnabled(True)

    def _default_folder(self) -> Path:

        heightmaps = find_tpf3_heightmaps_folder()

        if heightmaps is not None:
            biomes = heightmaps.parent / "biomes"
            return biomes if biomes.is_dir() else heightmaps

        return Path.home()

    def _export(self):

        if self._index is None:
            return

        path, _ = QFileDialog.getSaveFileName(
            self,
            tr("Biome-Maske speichern"),
            str(self._default_folder() / "biome_osm.png"),
            tr("PNG (*.png)"),
        )

        if not path:
            return

        try:
            save_biome_png(path, self._index)
        except OSError as error:
            QMessageBox.warning(
                self,
                tr("Biome-Maske"),
                tr("Die Datei konnte nicht gespeichert werden:\n{error}").format(error=error),
            )
            return

        QMessageBox.information(
            self,
            tr("Biome-Maske"),
            tr("Gespeichert:\n{path}\n\nIm Spiel: Karteneditor → Heightmap importieren → Reiter Biome → bei \"Biome\" diese Datei wählen, Berge und Flüsse leer lassen → Anwenden.").format(path=path),
        )
