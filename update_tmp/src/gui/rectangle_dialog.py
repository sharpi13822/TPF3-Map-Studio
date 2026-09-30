from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QFormLayout,
    QDoubleSpinBox,
    QComboBox,
    QDialogButtonBox,
    QLabel,
)

from src.gui.map_size_presets import ALL_MAP_SIZES, get_by_label


class RectangleToolDialog(QDialog):
    """
    Dialog fuer das Rechteck-Tool: Mittelpunkt, TPF2-Kartengroesse und
    Drehwinkel eingeben, um ein (ggf. gedrehtes) Kartenband auf der
    Karte zu platzieren - wie bei "Real Terrain", nur direkt im Studio.
    """

    def __init__(self, parent=None, initial_center=None, initial_selection=None):
        super().__init__(parent)

        self.setWindowTitle("Rechteck-Tool")

        layout = QVBoxLayout(self)
        form = QFormLayout()
        layout.addLayout(form)

        # -------------------------------------------------
        # Vorbelegung aus einer vorhandenen (z.B. geladenen) Auswahl:
        # initial_selection hat Vorrang vor dem aelteren initial_center,
        # da es zusaetzlich Groesse und Drehwinkel mitbringt. Nur ein
        # gedrehtes Band (width_m/height_m gesetzt) liefert sinnvolle
        # Werte fuer Groesse/Drehung - eine einfache, unrotierte Bbox
        # (z.B. aus einer alten Projektdatei) liefert nur den Mittelpunkt.
        # -------------------------------------------------

        prefill_center = initial_center
        prefill_size = None
        prefill_rotation = None

        if initial_selection is not None:
            prefill_center = initial_selection.center

            if initial_selection.width_m and initial_selection.height_m:
                prefill_size = (
                    initial_selection.width_m,
                    initial_selection.height_m,
                )
                prefill_rotation = initial_selection.rotation_deg

        # Ein explizit uebergebener Mittelpunkt (z.B. die Position eines
        # Markers) hat Vorrang vor dem Mittelpunkt der Auswahl. Groesse
        # und Drehwinkel der Auswahl bleiben dabei erhalten.
        if initial_center is not None:
            prefill_center = initial_center

        # -------------------------------------------------
        # Mittelpunkt
        # -------------------------------------------------

        self.center_lat_input = QDoubleSpinBox()
        self.center_lat_input.setRange(-90.0, 90.0)
        self.center_lat_input.setDecimals(6)
        self.center_lat_input.setSingleStep(0.001)

        self.center_lon_input = QDoubleSpinBox()
        self.center_lon_input.setRange(-180.0, 180.0)
        self.center_lon_input.setDecimals(6)
        self.center_lon_input.setSingleStep(0.001)

        if prefill_center is not None:
            lat, lon = prefill_center
            self.center_lat_input.setValue(lat)
            self.center_lon_input.setValue(lon)

        form.addRow("Mittelpunkt Breite (lat):", self.center_lat_input)
        form.addRow("Mittelpunkt Länge (lon):", self.center_lon_input)

        # -------------------------------------------------
        # Kartengröße
        # -------------------------------------------------

        self.size_combo = QComboBox()
        for size in ALL_MAP_SIZES:
            self.size_combo.addItem(size.label)

        if prefill_size is not None:
            # Naehestes Preset zur gespeicherten Groesse waehlen (Rundung
            # beim Speichern/Laden oder minimale Abweichungen sollen die
            # Zuordnung nicht verhindern).
            width_m, height_m = prefill_size
            best = min(
                ALL_MAP_SIZES,
                key=lambda s: abs(s.width_m - width_m) + abs(s.height_m - height_m),
            )
            match_index = self.size_combo.findText(best.label)
            if match_index >= 0:
                self.size_combo.setCurrentIndex(match_index)
        else:
            # Sinnvoller Standard fuer lange, gedrehte Baender, wenn
            # keine vorhandene Auswahl zum Vorbelegen da ist:
            default_size = get_by_label("Größenwahnsinnig 1:5")
            default_index = (
                self.size_combo.findText(default_size.label)
                if default_size is not None
                else -1
            )
            if default_index >= 0:
                self.size_combo.setCurrentIndex(default_index)

        self.size_combo.currentTextChanged.connect(self._update_size_label)

        form.addRow("Kartengröße:", self.size_combo)

        self.size_label = QLabel()
        form.addRow("", self.size_label)
        self._update_size_label(self.size_combo.currentText())

        # -------------------------------------------------
        # Drehwinkel
        # -------------------------------------------------

        self.rotation_input = QDoubleSpinBox()
        self.rotation_input.setRange(0.0, 359.99)
        self.rotation_input.setDecimals(2)
        self.rotation_input.setSingleStep(0.5)
        self.rotation_input.setSuffix(" °")

        if prefill_rotation is not None:
            self.rotation_input.setValue(prefill_rotation)

        form.addRow("Drehwinkel:", self.rotation_input)

        # -------------------------------------------------
        # Sicherheitsrand (fuer nachgelagerte Downloads)
        # -------------------------------------------------

        self.margin_input = QDoubleSpinBox()
        self.margin_input.setRange(0.0, 10_000.0)
        self.margin_input.setDecimals(0)
        self.margin_input.setSingleStep(100.0)
        self.margin_input.setValue(500.0)
        self.margin_input.setSuffix(" m")

        form.addRow("Sicherheitsrand (für Downloads):", self.margin_input)

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _update_size_label(self, label: str):
        size = get_by_label(label)
        if size is not None:
            self.size_label.setText(
                f"{size.width_m/1000:.3f} x {size.height_m/1000:.3f} km "
                f"({size.width_px}x{size.height_px} px)"
            )
        else:
            self.size_label.setText("")

    def values(self) -> dict:
        """Gibt die eingegebenen Werte zurueck, passend zu
        MapController.set_rotated_selection(**dialog.values())."""

        size = get_by_label(self.size_combo.currentText())

        return {
            "center_lat": self.center_lat_input.value(),
            "center_lon": self.center_lon_input.value(),
            "width_m": size.width_m,
            "height_m": size.height_m,
            "rotation_deg": self.rotation_input.value(),
            "margin_m": self.margin_input.value(),
        }