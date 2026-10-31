"""
Dialog "Biome-Maske aus OSM": erzeugt aus der geladenen OSM-Landnutzung eine
8-Bit-Graustufen-Maske fuer den Biome-Tab im TPF3-Karteneditor.

Die Voreinstellung (welche OSM-Flaeche zu welchem Biom gehoert) ist ein
Vorschlag und im Spiel noch nicht geprueft.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt, QTimer, Signal
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
    QFrame,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
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
from src.heightmap.nature_plan_export import save_plan_for_mask
from src.heightmap.tpf3_paths import find_tpf3_heightmaps_folder
from src.file_names import ascii_safe_path
from src.i18n import tr

# Anzeige -> Meter pro Pixel
_RESOLUTIONS = (
    (tr("16 m pro Pixel (klein, schnell)"), 16.0),
    (tr("8 m pro Pixel (Standard)"), 8.0),
    (tr("4 m pro Pixel (wie die Heightmap)"), 4.0),
)

_PREVIEW_HEIGHT = 480


class BiomeMaskDialog(QDialog):

    # Wird nach jeder berechneten Vorschau gesendet (Biom-Raster, uint8), damit
    # der Heightmap-Dialog die Biome in der 3D-Vorschau zeigen kann.
    preview_ready = Signal(object)

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
        # Kurzbeschreibung der Maske der letzten Vorschau und, nach einem
        # erfolgreichen Export, der exportierten Maske (fuer die Beschreibung
        # zum Teilen im Heightmap-Dialog)
        self._index_summary = ""
        self.exported_summary = None

        self.setWindowTitle(tr("Biome-Maske aus OSM"))

        # Die Einstellungen liegen in einem Scrollbereich, damit der Dialog
        # auch auf kleinen Bildschirmen bedienbar bleibt. Statuszeile und
        # Knoepfe stehen darunter und bleiben immer sichtbar.
        outer = QVBoxLayout(self)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        content = QWidget()
        scroll.setWidget(content)
        outer.addWidget(scroll, 1)

        layout = QVBoxLayout(content)

        self.setMinimumWidth(560)
        self.resize(640, 780)

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

        self.thin_band_input = QDoubleSpinBox()
        self.thin_band_input.setRange(0.0, 300.0)
        self.thin_band_input.setDecimals(0)
        self.thin_band_input.setSuffix(" m")
        self.thin_band_input.setValue(40.0)
        self.thin_band_input.setToolTip(
            tr("Auf dieser Strecke unter der Baumgrenze werden die "
               "Baumgruppen nach oben hin allmählich weniger, statt an einer "
               "harten Linie zu enden. 0 = harte Linie.")
        )
        form.addRow(tr("Weicher Übergang (m darunter):"), self.thin_band_input)

        self.thin_biome_box = QComboBox()
        self.thin_biome_box.addItem(BIOME_NAMES[0], 0)
        self.thin_biome_box.addItem(BIOME_NAMES[2], 2)
        form.addRow(tr("Ersatzbiom:"), self.thin_biome_box)

        self.preview_label = QLabel(tr("Noch keine Vorschau."))
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        outer.addWidget(self.status_label)

        self.nature_checkbox = QCheckBox(
            tr("Natur-Details-Plan (Weinberge, Obstwiesen, Mauern, Hecken) mitspeichern")
        )
        self.nature_checkbox.setChecked(True)
        self.nature_checkbox.setToolTip(
            tr("Speichert zusätzlich die Liste für den Natur-Details-Mod als CSV und JSON. "
               "Mauern und Hecken gibt es nur, wenn beim OSM-Laden 'Natur-Details' angehakt war.")
        )
        outer.addWidget(self.nature_checkbox)

        row = QHBoxLayout()
        outer.addLayout(row)

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

        # Nach der ersten Vorschau rechnet jede Aenderung die Vorschau (und damit
        # die 3D-Ansicht im Heightmap-Dialog) kurz darauf von selbst neu.
        self._auto_timer = QTimer(self)
        self._auto_timer.setSingleShot(True)
        self._auto_timer.setInterval(600)
        self._auto_timer.timeout.connect(self._auto_preview)

        for box in self.category_boxes.values():
            box.currentIndexChanged.connect(self._schedule_preview)

        self.resolution_box.currentIndexChanged.connect(self._schedule_preview)
        self.thin_checkbox.toggled.connect(self._schedule_preview)
        self.thin_limit_input.valueChanged.connect(self._schedule_preview)
        self.thin_band_input.valueChanged.connect(self._schedule_preview)
        self.thin_biome_box.currentIndexChanged.connect(self._schedule_preview)

    def _schedule_preview(self, *_args):
        """Aenderung nach einer ersten Vorschau: kurz warten, dann neu rechnen."""

        if self._index is not None:
            self._auto_timer.start()

    def _auto_preview(self):

        if all(value is None for value in self._assignment().values()):
            return

        self._make_preview()

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
                band_m=self.thin_band_input.value(),
                pixel_m=meters_per_pixel,
            )

        self._index = index
        self._index_summary = self._summary()
        self.preview_ready.emit(index)

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

    def _summary(self) -> str:
        """Zuordnung und Baumgrenze, wie sie gerade eingestellt sind."""

        assignment = self._assignment()
        parts = []

        for key, label, _rules in CATEGORIES:
            value = assignment.get(key)
            if value is not None:
                parts.append(f"{label} → {BIOME_NAMES[value]}")

        text = "; ".join(parts)

        if self.thin_checkbox.isChecked() and self._heights is not None:
            text += "; " + tr(
                "Bäume ab {limit:.0f} m über Wasser ausgedünnt"
            ).format(limit=self.thin_limit_input.value())

        return text

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

        path, renamed = ascii_safe_path(path)

        try:
            save_biome_png(path, self._index)
        except OSError as error:
            QMessageBox.warning(
                self,
                tr("Biome-Maske"),
                tr("Die Datei konnte nicht gespeichert werden:\n{error}").format(error=error),
            )
            return

        self.exported_summary = self._index_summary

        plan_text = ""

        if self.nature_checkbox.isChecked():
            try:
                plan = save_plan_for_mask(
                    self.osm,
                    self.selection,
                    path,
                    game_folder=self._default_folder(),
                )
            except Exception as error:  # noqa: BLE001 - Maske ist schon gespeichert
                plan_text = "\n\n" + tr("Der Natur-Details-Plan konnte nicht gespeichert werden: {error}").format(error=error)
            else:
                if plan is None:
                    plan_text = "\n\n" + tr("Natur-Details-Plan: keine Weinberge, Obstwiesen, Mauern oder Hecken gefunden.")
                else:
                    plan_text = "\n\n" + tr("Natur-Details-Plan: {csv} und {json}\nOrdner: {folder}").format(
                        csv=plan[0].name, json=plan[1].name, folder=plan[0].parent
                    )

        QMessageBox.information(
            self,
            tr("Biome-Maske"),
            tr("Gespeichert:\n{path}\n\nIm Spiel: Karteneditor → Heightmap importieren → Reiter Biome → bei \"Biome\" diese Datei wählen, Berge und Flüsse leer lassen → Anwenden.").format(path=path)
            + plan_text
            + (
                tr("\n\nDer Dateiname wurde ohne Umlaute und Sonderzeichen "
                   "gespeichert, weil sie im Spiel Probleme machen k\u00f6nnen.")
                if renamed
                else ""
            ),
        )
