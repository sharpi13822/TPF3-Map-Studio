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
    QApplication,
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
from src.heightmap.water_slope_compensation import (
    compensate_water_slope,
    DEFAULT_SMOOTHING_M,
)

DEFAULT_CACHE_DIR = Path.home() / ".tpf2_map_studio" / "dem_cache"
DEFAULT_TRANSITION_M = 30.0

# Als Bezug fuer den Gefaelle-Ausgleich zaehlen Seen/Wasserflaechen sowie
# diese Wasserwege - Baeche und Graeben bewusst nicht: sie liegen oft weit
# ueber dem Talfluss und wuerden ihre Umgebung sonst unnatuerlich absenken.
REFERENCE_WATERWAY_TYPES = frozenset({"river", "canal"})


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
        self._reference_mask = None
        self._processed_key = None
        self._processed_array = None
        self._processed_suggestion = None

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
        # Gefaelle ausgleichen (Idee eines Community-Mitglieds: die
        # Karte "vertikal gerade richten", statt nur die Hoehe ue. NN
        # zu uebernehmen - siehe water_slope_compensation.py).
        # -------------------------------------------------

        self.slope_checkbox = QCheckBox(
            "Gefälle ausgleichen (legt Flüsse und Seen auf eine "
            "gemeinsame Ebene und zieht das Gelände relativ dazu mit; "
            "das Relief über dem jeweiligen Wasserspiegel bleibt "
            "erhalten, die absoluten Höhen ü. NN stimmen danach aber "
            "nicht mehr)"
        )
        self.slope_checkbox.setEnabled(False)
        self.slope_checkbox.toggled.connect(
            self._on_slope_toggled
        )
        layout.addWidget(self.slope_checkbox)

        slope_row = QHBoxLayout()

        slope_row.addWidget(QLabel("Stärke:"))
        self.slope_strength_input = QDoubleSpinBox()
        self.slope_strength_input.setRange(0.0, 100.0)
        self.slope_strength_input.setDecimals(0)
        self.slope_strength_input.setSuffix(" %")
        self.slope_strength_input.setValue(100.0)
        self.slope_strength_input.setEnabled(False)
        # Erst nach Enter/Fokuswechsel neu rechnen, nicht bei jeder Ziffer.
        self.slope_strength_input.setKeyboardTracking(False)
        self.slope_strength_input.valueChanged.connect(
            self._update_preview
        )
        slope_row.addWidget(self.slope_strength_input)

        slope_row.addWidget(QLabel("Glättung:"))
        self.slope_smoothing_input = QDoubleSpinBox()
        self.slope_smoothing_input.setRange(50.0, 5000.0)
        self.slope_smoothing_input.setDecimals(0)
        self.slope_smoothing_input.setSuffix(" m")
        self.slope_smoothing_input.setValue(DEFAULT_SMOOTHING_M)
        self.slope_smoothing_input.setEnabled(False)
        self.slope_smoothing_input.setKeyboardTracking(False)
        self.slope_smoothing_input.valueChanged.connect(
            self._update_preview
        )
        slope_row.addWidget(self.slope_smoothing_input)

        layout.addLayout(slope_row)

        self.slope_note_label = QLabel("")
        self.slope_note_label.setWordWrap(True)
        layout.addWidget(self.slope_note_label)

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
        self._reference_mask = None
        self._reset_processed_cache()

        has_water_data = (
            self.osm is not None
            and (self.osm.node_count > 0 or self.osm.way_count > 0)
        )

        self.water_blend_checkbox.setEnabled(has_water_data)
        self.water_blend_checkbox.setChecked(False)

        self.slope_checkbox.blockSignals(True)
        self.slope_checkbox.setChecked(False)
        self.slope_checkbox.blockSignals(False)
        self.slope_checkbox.setEnabled(has_water_data)
        self.slope_strength_input.setEnabled(False)
        self.slope_smoothing_input.setEnabled(False)

        if not has_water_data:
            self.water_blend_note_label.setText(
                "Keine OSM-Daten geladen - für die Terrain-Anpassung "
                "werden die Wasserflächen aus 'OSM laden' benötigt."
            )
            self.slope_note_label.setText(
                "Keine OSM-Daten geladen - der Gefälle-Ausgleich "
                "braucht die Gewässer aus 'OSM laden'."
            )
        else:
            self.water_blend_note_label.setText("")
            self.slope_note_label.setText("")

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

        # Bei aktivem Gefaelle-Ausgleich verschieben sich die Hoehen
        # (Gelaende wird relativ zum Wasser abgesenkt/angehoben) - der
        # Bereich muss dann aus dem tatsaechlich exportierten Raster
        # stammen, sonst wuerde beim Export abgeschnitten.
        suggestion = self._active_suggestion()

        if (
            suggestion is not None
            and self.exclude_outliers_checkbox.isChecked()
        ):
            return (
                suggestion.robust_range_min_m,
                suggestion.robust_range_max_m,
            )

        return suggestion.range_min_m, suggestion.range_max_m

    def _update_range_label(self):

        range_min, range_max = self._effective_range()

        self.range_label.setText(
            f"{range_min:.0f} – {range_max:.0f} m"
        )

    def _on_exclude_outliers_toggled(self):

        self._update_range_label()
        self._update_preview()

    # ---------------------------------------------------------
    # Gefälle ausgleichen
    # ---------------------------------------------------------

    def _on_slope_toggled(self, checked: bool):

        self.slope_strength_input.setEnabled(checked)
        self.slope_smoothing_input.setEnabled(checked)

        if not checked:

            self.slope_note_label.setText("")
            self._update_preview()
            return

        try:
            reference_mask = self._get_reference_mask()
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Wassermaske fehlgeschlagen",
                str(exc),
            )
            self.slope_checkbox.setChecked(False)
            return

        if not reference_mask.any():

            self.slope_note_label.setText(
                "In diesem Kartenausschnitt wurden keine Seen oder "
                "größeren Flüsse als Bezug gefunden - der "
                "Gefälle-Ausgleich hat hier keine Wirkung."
            )

        else:

            self.slope_note_label.setText(
                "Als Bezug dienen Seen und Wasserflächen sowie Flüsse "
                "und Kanäle; Bäche und Gräben zählen dafür nicht."
            )

        self._update_preview()

    def _get_reference_mask(self):
        """
        Wassermaske nur aus Bezugsgewaessern (Seen/Wasserflaechen, Fluesse,
        Kanaele) - gecacht, bei neuem Download verworfen.
        """

        if self._reference_mask is None:

            QApplication.setOverrideCursor(Qt.WaitCursor)

            try:

                h_px, w_px = self.heightmap_array.shape

                self._reference_mask = build_water_mask(
                    self.osm,
                    self.selection,
                    w_px,
                    h_px,
                    waterway_types=REFERENCE_WATERWAY_TYPES,
                )

            finally:
                QApplication.restoreOverrideCursor()

        return self._reference_mask

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

    def _pixel_size_m(self) -> float:

        return self.selection.width_m / (self.heightmap_array.shape[1] - 1)

    def _processing_key(self):
        """
        Alle Einstellungen, die das verarbeitete Raster beeinflussen -
        aendert sich nichts davon, wird das bereits berechnete Ergebnis
        wiederverwendet (Vorschau UND Export rechnen sonst jeweils neu).
        """

        return (
            self.slope_checkbox.isChecked(),
            self.slope_strength_input.value(),
            self.slope_smoothing_input.value(),
            self.water_blend_checkbox.isChecked(),
            self.transition_input.value(),
            self.water_level_input.value(),
        )

    def _reset_processed_cache(self):

        self._processed_key = None
        self._processed_array = None
        self._processed_suggestion = None

    def _effective_heightmap(self):
        """
        Liefert das Hoehenraster, das fuer Vorschau/Export tatsaechlich
        verwendet wird. Reihenfolge, wenn angehakt:

        1. Gefaelle ausgleichen (Gewaesser auf eine gemeinsame Ebene,
           Gelaende relativ dazu mit)
        2. Terrain sanft ans Wasserniveau anpassen (Ufer glaetten, raeumt
           kleine Restunterschiede aus Schritt 1 auf)

        Ohne Haekchen: das unveraenderte Original.
        """

        slope_on = self.slope_checkbox.isChecked()
        blend_on = self.water_blend_checkbox.isChecked()

        if not slope_on and not blend_on:
            return self.heightmap_array

        key = self._processing_key()

        if key == self._processed_key and self._processed_array is not None:
            return self._processed_array

        QApplication.setOverrideCursor(Qt.WaitCursor)

        try:

            array = self.heightmap_array
            water_level = self.water_level_input.value()
            pixel_size = self._pixel_size_m()

            if slope_on:

                array = compensate_water_slope(
                    array,
                    self._get_reference_mask(),
                    water_level_m=water_level,
                    pixel_size_m=pixel_size,
                    strength=self.slope_strength_input.value() / 100.0,
                    smoothing_m=self.slope_smoothing_input.value(),
                )

            if blend_on:

                array = blend_terrain_to_water(
                    array,
                    self._get_water_mask(),
                    water_level_m=water_level,
                    transition_m=self.transition_input.value(),
                    pixel_size_m=pixel_size,
                )

        finally:
            QApplication.restoreOverrideCursor()

        self._processed_array = array
        self._processed_key = key
        self._processed_suggestion = None

        return array

    def _active_suggestion(self):
        """
        Die Hoehenbereichs-/Ausreisser-Angaben passend zum tatsaechlich
        verwendeten Raster: das Original beim Normalfall, bei aktivem
        Gefaelle-Ausgleich eine frische Analyse des angepassten Rasters.
        """

        if not self.slope_checkbox.isChecked():
            return self.suggestion

        array = self._effective_heightmap()

        if self._processed_suggestion is None:
            self._processed_suggestion = suggest_water_level(array)

        return self._processed_suggestion

    def _sync_outlier_checkbox(self, suggestion):
        """
        Haelt Text/Sichtbarkeit der Ausreisser-Checkbox passend zum
        gerade verwendeten Raster (blockSignals, damit das Umstellen
        keine weitere Neuberechnung ausloest).
        """

        checkbox = self.exclude_outliers_checkbox

        checkbox.blockSignals(True)

        if suggestion.outlier_count > 0:

            checkbox.setText(
                f"Ausreißer aus Höhenbereich ausschließen "
                f"({suggestion.outlier_count} Pixel, "
                f"{suggestion.outlier_fraction * 100:.2f}% der Fläche "
                f"erkannt)"
            )
            checkbox.setVisible(True)

        else:

            checkbox.setVisible(False)
            checkbox.setChecked(False)

        checkbox.blockSignals(False)

    # ---------------------------------------------------------
    # Vorschau
    # ---------------------------------------------------------

    def _update_preview(self):

        if self.heightmap_array is None or self.suggestion is None:
            return

        array = self._effective_heightmap()

        self._sync_outlier_checkbox(self._active_suggestion())

        range_min, range_max = self._effective_range()

        self.range_label.setText(
            f"{range_min:.0f} – {range_max:.0f} m"
        )

        image = render_preview(
            array,
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
                f"\n\nHinweis: Die {self._active_suggestion().outlier_count} als "
                f"Ausreißer erkannten Pixel liegen außerhalb dieses "
                f"Bereichs und wurden dadurch auf den Rand geklemmt "
                f"(0 bzw. 65535) - deren echte Höhe geht im Export verloren."
            )

        slope_note = ""

        if self.slope_checkbox.isChecked():

            slope_note = (
                f"\n\nGefälle-Ausgleich aktiv (Stärke "
                f"{self.slope_strength_input.value():.0f} %, Glättung "
                f"{self.slope_smoothing_input.value():.0f} m): Flüsse und "
                f"Seen wurden auf eine gemeinsame Ebene gelegt, das "
                f"Gelände relativ dazu angepasst - die absoluten Höhen "
                f"ü. NN stimmen dadurch nicht mehr."
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
            f"{slope_note}"
            f"{water_blend_note}"
        )