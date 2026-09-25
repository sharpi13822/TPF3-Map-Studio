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
from src.core.background_task import run_in_background

DEFAULT_CACHE_DIR = Path.home() / ".tpf2_map_studio" / "dem_cache"


class HeightmapDialog(QDialog):
    """
    Laedt automatisch die Copernicus-Hoehendaten fuer die aktuelle
    (ggf. gedrehte) Selection, zeigt eine Vorschau mit Wasserflaeche wie
    im TPF2-Importfenster, und exportiert die fertige 16-Bit-PNG.
    """

    def __init__(self, parent, selection, project=None):
        super().__init__(parent)

        self.selection = selection
        self.project = project
        self.heightmap_array = None
        self.suggestion = None

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
        self._set_busy(True)

        selection = self.selection

        def work():
            # Laeuft im Hintergrund-Thread: nur Netzwerk und numpy,
            # keine Widgets anfassen.
            array = build_heightmap_array(
                selection,
                DEFAULT_CACHE_DIR,
            )
            return array, suggest_water_level(array)

        run_in_background(
            work,
            on_success=self._on_download_finished,
            on_error=self._on_download_failed,
            name="heightmap-download",
        )

    def _on_download_failed(self, exc):

        self.status_label.setText(
            f"Fehlgeschlagen: {exc}"
        )
        self._set_busy(False)

    def _on_download_finished(self, result):

        self.heightmap_array, self.suggestion = result

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

        self._set_busy(False)
        self.export_button.setEnabled(True)

        self._update_preview()

    def _set_busy(self, busy: bool):
        """
        Sperrt die Download-Knoepfe, solange ein Hintergrund-Download
        laeuft (sonst koennten zwei gleichzeitig dieselben Kacheln in
        den Cache schreiben).
        """

        self.download_button.setEnabled(not busy)
        self.quick_preview_button.setEnabled(not busy)

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
        self._set_busy(True)

        selection = self.selection

        def work():
            # Laeuft im Hintergrund-Thread: liefert fertige PNG-Bytes,
            # das QPixmap wird erst im GUI-Thread daraus erzeugt.
            preview_array = build_heightmap_array_preview(
                selection,
                DEFAULT_CACHE_DIR,
            )

            quick_suggestion = suggest_water_level(preview_array)

            image = render_preview(
                preview_array,
                water_level_m=quick_suggestion.suggested_m,
                range_min_m=quick_suggestion.range_min_m,
                range_max_m=quick_suggestion.range_max_m,
            )

            buffer = io.BytesIO()
            image.save(buffer, format="PNG")

            return preview_array.shape, buffer.getvalue()

        run_in_background(
            work,
            on_success=self._on_quick_preview_finished,
            on_error=self._on_quick_preview_failed,
            name="heightmap-preview",
        )

    def _on_quick_preview_failed(self, exc):

        self.status_label.setText(
            f"Schnellvorschau fehlgeschlagen: {exc}"
        )
        self._set_busy(False)

    def _on_quick_preview_finished(self, result):

        shape, png_bytes = result

        pixmap = QPixmap()
        pixmap.loadFromData(png_bytes)

        self.preview_label.setPixmap(
            pixmap.scaledToHeight(400, Qt.SmoothTransformation)
        )

        self.status_label.setText(
            f"Schnellvorschau ({shape[1]} x "
            f"{shape[0]} Pixel, niedrige Auflösung - "
            f"noch nicht exportierbar). Sieht das plausibel aus? Dann "
            f"jetzt 'Höhendaten herunterladen' für die volle Auflösung."
        )

        self._set_busy(False)

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
    # Vorschau
    # ---------------------------------------------------------

    def _update_preview(self):

        if self.heightmap_array is None or self.suggestion is None:
            return

        range_min, range_max = self._effective_range()

        image = render_preview(
            self.heightmap_array,
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
                self.heightmap_array,
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

        QMessageBox.information(
            self,
            "Export abgeschlossen",
            f"Heightmap gespeichert unter:\n{filename}\n\n"
            f"Höhenbereich für den TPF2-Import: "
            f"{range_min:.0f} – "
            f"{range_max:.0f} m\n"
            f"Wasserhöhe: {self.water_level_input.value():.0f} m"
            f"{outlier_warning}"
        )