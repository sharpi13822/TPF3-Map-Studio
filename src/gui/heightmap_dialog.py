import io
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
    QLabel,
    QPushButton,
    QFileDialog,
    QMessageBox,
    QCheckBox,
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from src.heightmap.heightmap_exporter import (
    build_heightmap_array,
    build_heightmap_array_preview,
    export_heightmap_png,
)
from src.heightmap.water_level import suggest_water_level, render_preview
from src.heightmap.water_terrain_blend import build_water_mask, blend_terrain_to_water

DEFAULT_CACHE_DIR = Path.home() / ".tpf2_map_studio" / "dem_cache"
DEFAULT_TRANSITION_M = 30.0


class HeightmapDialog(QDialog):
    """
    Laedt automatisch die Copernicus-Hoehendaten fuer die aktuelle
    (ggf. gedrehte) Selection, zeigt eine Vorschau mit Wasserflaeche wie
    im TPF2-Importfenster, und exportiert die fertige 16-Bit-PNG.
    """

    def __init__(self, parent, selection, project=None, osm=None):
        super().__init__(parent)

        self.selection = selection
        self.project = project
        self.osm = osm
        self.heightmap_array = None
        self.suggestion = None
        self._water_mask = None

        self.setWindowTitle("Heightmap")
        self.setMinimumWidth(420)

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # Download
        # -------------------------------------------------

        self.status_label = QLabel(
            "Noch nicht geladen."
        )
        layout.addWidget(self.status_label)

        self.quick_preview_button = QPushButton(
            "Schnellvorschau (niedrige Auflösung, vor dem echten Download)"
        )
        self.quick_preview_button.clicked.connect(
            self._quick_preview
        )
        layout.addWidget(self.quick_preview_button)

        self.download_button = QPushButton(
            "Höhendaten herunterladen"
        )
        self.download_button.clicked.connect(
            self._download
        )
        layout.addWidget(self.download_button)

        # -------------------------------------------------
        # Vorschau
        # -------------------------------------------------

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(300)
        layout.addWidget(self.preview_label)

        # -------------------------------------------------
        # Höhenbereich / Wasserhöhe
        # -------------------------------------------------

        form = QFormLayout()
        layout.addLayout(form)

        self.range_label = QLabel("–")
        form.addRow("Höhenbereich:", self.range_label)

        self.exclude_outliers_checkbox = QCheckBox(
            "Ausreißer aus Höhenbereich ausschließen (mehr Präzision "
            "fürs eigentliche Gelände)"
        )
        self.exclude_outliers_checkbox.setVisible(False)
        self.exclude_outliers_checkbox.toggled.connect(
            self._on_exclude_outliers_toggled
        )
        layout.addWidget(self.exclude_outliers_checkbox)

        self.water_level_input = QDoubleSpinBox()
        self.water_level_input.setRange(-500.0, 9000.0)
        self.water_level_input.setDecimals(0)
        self.water_level_input.setSuffix(" m")
        self.water_level_input.setEnabled(False)
        self.water_level_input.valueChanged.connect(
            self._update_preview
        )
        form.addRow("Wasserhöhe:", self.water_level_input)

        self.note_label = QLabel("")
        self.note_label.setWordWrap(True)
        layout.addWidget(self.note_label)

        # -------------------------------------------------
        # Terrain ans Wasserniveau anpassen (Idee eines
        # Community-Mitglieds: TPF2/TPF3 kennen kein Wassergefaelle,
        # ohne Anpassung fallen Fluesse/Seen bei echten Hoehendaten
        # sonst oft "trocken").
        # -------------------------------------------------

        self.water_blend_checkbox = QCheckBox(
            "Terrain sanft ans Wasserniveau anpassen (verhindert "
            "trockenfallende Flüsse/Seen, weicht dafür geringfügig von "
            "den echten Höhendaten ab; sehr kleine Einzelgewässer, "
            "z.B. Toteislöcher in einem Filz/Moor, werden dabei "
            "automatisch ausgenommen, um Krater-Artefakte zu vermeiden)"
        )
        self.water_blend_checkbox.setEnabled(False)
        self.water_blend_checkbox.toggled.connect(
            self._on_water_blend_toggled
        )
        layout.addWidget(self.water_blend_checkbox)

        transition_row = QHBoxLayout()
        transition_row.addWidget(QLabel("Übergangsbreite:"))
        self.transition_input = QDoubleSpinBox()
        self.transition_input.setRange(4.0, 500.0)
        self.transition_input.setDecimals(0)
        self.transition_input.setSuffix(" m")
        self.transition_input.setValue(DEFAULT_TRANSITION_M)
        self.transition_input.setEnabled(False)
        self.transition_input.valueChanged.connect(
            self._update_preview
        )
        transition_row.addWidget(self.transition_input)
        layout.addLayout(transition_row)

        self.water_blend_note_label = QLabel("")
        self.water_blend_note_label.setWordWrap(True)
        layout.addWidget(self.water_blend_note_label)

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        button_row = QHBoxLayout()
        layout.addLayout(button_row)

        self.export_button = QPushButton(
            "Exportieren..."
        )
        self.export_button.setEnabled(False)
        self.export_button.clicked.connect(
            self._export
        )
        button_row.addWidget(self.export_button)

        close_button = QPushButton("Schließen")
        close_button.clicked.connect(self.reject)
        button_row.addWidget(close_button)

    # ---------------------------------------------------------
    # Download
    # ---------------------------------------------------------

    def _download(self):

        self.status_label.setText(
            "Lade Höhendaten... (kann je nach Kartengröße etwas dauern)"
        )
        self.download_button.setEnabled(False)
        # Sorgt dafuer, dass der Text vor dem (blockierenden) Download
        # tatsaechlich schon sichtbar ist.
        self.repaint()

        try:
            self.heightmap_array = build_heightmap_array(
                self.selection,
                DEFAULT_CACHE_DIR,
            )
        except Exception as exc:
            self.status_label.setText(
                f"Fehlgeschlagen: {exc}"
            )
            self.download_button.setEnabled(True)
            return

        self.suggestion = suggest_water_level(
            self.heightmap_array
        )

        self._water_mask = None  # neuer Download -> alte Maske verwerfen

        has_water_data = (
            self.osm is not None
            and (self.osm.node_count > 0 or self.osm.way_count > 0)
        )

        self.water_blend_checkbox.setEnabled(has_water_data)
        self.water_blend_checkbox.setChecked(False)

        if not has_water_data:
            self.water_blend_note_label.setText(
                "Keine OSM-Daten geladen - für die Terrain-Anpassung "
                "werden die Wasserflächen aus 'OSM laden' benötigt."
            )
        else:
            self.water_blend_note_label.setText("")

        if self.suggestion.outlier_count > 0:

            self.exclude_outliers_checkbox.setText(
                f"Ausreißer aus Höhenbereich ausschließen "
                f"({self.suggestion.outlier_count} Pixel, "
                f"{self.suggestion.outlier_fraction * 100:.2f}% der Fläche "
                f"erkannt)"
            )
            self.exclude_outliers_checkbox.setVisible(True)
            self.exclude_outliers_checkbox.setChecked(False)

        else:

            self.exclude_outliers_checkbox.setVisible(False)
            self.exclude_outliers_checkbox.setChecked(False)

        self._update_range_label()

        self.water_level_input.setEnabled(True)
        self.water_level_input.blockSignals(True)
        self.water_level_input.setValue(
            self.suggestion.suggested_m
        )
        self.water_level_input.blockSignals(False)

        self.note_label.setText(
            self.suggestion.note
        )

        self.status_label.setText(
            f"Geladen: {self.heightmap_array.shape[1]} x "
            f"{self.heightmap_array.shape[0]} Pixel"
        )

        self.export_button.setEnabled(True)
        self.download_button.setEnabled(True)

        self._update_preview()

    # ---------------------------------------------------------
    # Schnellvorschau (vor dem eigentlichen Download)
    # ---------------------------------------------------------

    def _quick_preview(self):
        """
        Laedt dieselben Copernicus-Kacheln wie der echte Download, tastet
        das Band aber nur grob ab (siehe build_heightmap_array_preview) -
        damit laesst sich sofort pruefen, ob Mittelpunkt/Drehung/Form
        stimmen, ohne auf die volle Aufloesung zu warten. Die Kacheln
        landen dabei im Cache, der anschliessende echte Download laedt
        dann nichts mehr neu herunter.

        Beeinflusst bewusst NICHT self.heightmap_array/self.suggestion -
        die Schnellvorschau ersetzt nicht den fuer den Export noetigen
        vollaufloesenden Download.
        """

        self.status_label.setText(
            "Lade Schnellvorschau..."
        )
        self.quick_preview_button.setEnabled(False)
        self.download_button.setEnabled(False)
        self.repaint()

        try:
            preview_array = build_heightmap_array_preview(
                self.selection,
                DEFAULT_CACHE_DIR,
            )
        except Exception as exc:
            self.status_label.setText(
                f"Schnellvorschau fehlgeschlagen: {exc}"
            )
            self.quick_preview_button.setEnabled(True)
            self.download_button.setEnabled(True)
            return

        quick_suggestion = suggest_water_level(preview_array)

        image = render_preview(
            preview_array,
            water_level_m=quick_suggestion.suggested_m,
            range_min_m=quick_suggestion.range_min_m,
            range_max_m=quick_suggestion.range_max_m,
        )

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())

        self.preview_label.setPixmap(
            pixmap.scaledToHeight(400, Qt.SmoothTransformation)
        )

        self.status_label.setText(
            f"Schnellvorschau ({preview_array.shape[1]} x "
            f"{preview_array.shape[0]} Pixel, niedrige Auflösung - "
            f"noch nicht exportierbar). Sieht das plausibel aus? Dann "
            f"jetzt 'Höhendaten herunterladen' für die volle Auflösung."
        )

        self.quick_preview_button.setEnabled(True)
        self.download_button.setEnabled(True)

    # ---------------------------------------------------------
    # Höhenbereich (mit/ohne Ausreißer)
    # ---------------------------------------------------------

    def _effective_range(self) -> tuple[float, float]:
        """
        Der tatsaechlich fuer Vorschau/Export verwendete Hoehenbereich -
        voller Bereich (Standard, nichts geht verloren) oder die engere,
        ausreisserbereinigte Spanne, falls der Nutzer das explizit
        angehakt hat.
        """

        if (
            self.suggestion is not None
            and self.exclude_outliers_checkbox.isChecked()
        ):
            return (
                self.suggestion.robust_range_min_m,
                self.suggestion.robust_range_max_m,
            )

        return self.suggestion.range_min_m, self.suggestion.range_max_m

    def _update_range_label(self):

        range_min, range_max = self._effective_range()

        self.range_label.setText(
            f"{range_min:.0f} – {range_max:.0f} m"
        )

    def _on_exclude_outliers_toggled(self):

        self._update_range_label()
        self._update_preview()

    # ---------------------------------------------------------
    # Terrain-Wasser-Anpassung
    # ---------------------------------------------------------

    def _on_water_blend_toggled(self, checked: bool):

        self.transition_input.setEnabled(checked)

        if checked:

            try:
                self._get_water_mask()
            except Exception as exc:
                QMessageBox.critical(
                    self,
                    "Wassermaske fehlgeschlagen",
                    str(exc),
                )
                self.water_blend_checkbox.setChecked(False)
                return

            if self._water_mask is not None and not self._water_mask.any():

                self.water_blend_note_label.setText(
                    "In diesem Kartenausschnitt wurden keine "
                    "Wasserflächen/-wege gefunden - die Anpassung hat "
                    "hier keine Wirkung."
                )

            else:

                self.water_blend_note_label.setText("")

        self._update_preview()

    def _get_water_mask(self):
        """
        Baut die Wassermaske einmalig und cacht sie (teure Berechnung
        bei grossen Kartenbaendern) - wird bei jedem neuen Download
        verworfen (siehe _download()).
        """

        if self._water_mask is None:

            h_px, w_px = self.heightmap_array.shape

            self._water_mask = build_water_mask(
                self.osm,
                self.selection,
                w_px,
                h_px,
            )

        return self._water_mask

    def _effective_heightmap(self):
        """
        Liefert das Hoehenraster, das fuer Vorschau/Export tatsaechlich
        verwendet wird - unveraendert (Standard) oder mit sanft ans
        Wasserniveau angepasstem Terrain, falls angehakt.
        """

        if not self.water_blend_checkbox.isChecked():
            return self.heightmap_array

        water_mask = self._get_water_mask()

        return blend_terrain_to_water(
            self.heightmap_array,
            water_mask,
            water_level_m=self.water_level_input.value(),
            transition_m=self.transition_input.value(),
            pixel_size_m=self.selection.width_m / (self.heightmap_array.shape[1] - 1),
        )

    # ---------------------------------------------------------
    # Vorschau
    # ---------------------------------------------------------

    def _update_preview(self):

        if self.heightmap_array is None or self.suggestion is None:
            return

        range_min, range_max = self._effective_range()

        image = render_preview(
            self._effective_heightmap(),
            water_level_m=self.water_level_input.value(),
            range_min_m=range_min,
            range_max_m=range_max,
        )

        buffer = io.BytesIO()
        image.save(buffer, format="PNG")

        pixmap = QPixmap()
        pixmap.loadFromData(buffer.getvalue())

        self.preview_label.setPixmap(
            pixmap.scaledToHeight(
                400,
                Qt.SmoothTransformation
            )
        )

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    def _export(self):

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Heightmap exportieren",
            "heightmap.png",
            "PNG-Bilder (*.png)"
        )

        if not filename:
            return

        range_min, range_max = self._effective_range()

        try:
            export_heightmap_png(
                self._effective_heightmap(),
                Path(filename),
                range_min_m=range_min,
                range_max_m=range_max,
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Export fehlgeschlagen",
                str(exc)
            )
            return

        if self.project is not None:
            self.project.mark_heightmap_exported(filename)

        outlier_warning = ""

        if self.exclude_outliers_checkbox.isChecked():

            outlier_warning = (
                f"\n\nHinweis: Die {self.suggestion.outlier_count} als "
                f"Ausreißer erkannten Pixel liegen außerhalb dieses "
                f"Bereichs und wurden dadurch auf den Rand geklemmt "
                f"(0 bzw. 65535) - deren echte Höhe geht im Export verloren."
            )

        water_blend_note = ""

        if self.water_blend_checkbox.isChecked():

            water_blend_note = (
                f"\n\nDas Terrain wurde um Gewässer herum (Übergang "
                f"{self.transition_input.value():.0f} m) sanft ans "
                f"Wasserniveau angepasst - weicht dort geringfügig von "
                f"den echten Höhendaten ab."
            )

        QMessageBox.information(
            self,
            "Export abgeschlossen",
            f"Heightmap gespeichert unter:\n{filename}\n\n"
            f"Höhenbereich für den TPF2-Import: "
            f"{range_min:.0f} – "
            f"{range_max:.0f} m\n"
            f"Wasserhöhe: {self.water_level_input.value():.0f} m"
            f"{outlier_warning}"
            f"{water_blend_note}"
        )