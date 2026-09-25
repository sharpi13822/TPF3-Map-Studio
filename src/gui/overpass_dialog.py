from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGroupBox,
    QCheckBox,
    QLabel,
    QComboBox,
    QPushButton,
    QLineEdit,
    QMessageBox,
    QPlainTextEdit,
    QDialogButtonBox,
)

from src.osm.overpass_query_builder import (
    OverpassQueryConfig,
    build_query,
    load_templates,
    save_template,
    delete_template,
)


CATEGORY_LABELS = (
    ("railways", "Gleistypen"),
    ("include_tram", "  davon Straßenbahn (Tram) einschließen"),
    ("highways", "Straßentypen"),
    ("buildings", "Gebäude"),
    ("parks", "Parks / Gärten"),
    ("landuse", "Flächennutzung"),
    ("vegetation", "Vegetation (Wald, Baumreihen)"),
    ("water", "Gewässer"),
    ("places", "Orte (Städte, Dörfer)"),
)


class OverpassQueryDialog(QDialog):
    """
    Overpass-Abfrage-Baukasten: statt die Overpass-QL-Abfrage von Hand zu
    tippen (Fehlerquelle: verlorene Klammern), werden hier einzelne
    Kategorien per Checkbox an-/ausgeschaltet und die Abfrage automatisch
    zusammengebaut - inklusive Vorschau und wiederverwendbaren Vorlagen.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.setWindowTitle("Overpass-Abfrage")
        self.setMinimumSize(560, 620)

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # Vorlagen
        # -------------------------------------------------

        templates_group = QGroupBox("Vorlage")
        templates_layout = QHBoxLayout(templates_group)

        self.template_combo = QComboBox()
        self.template_combo.addItem("(keine)")
        templates_layout.addWidget(self.template_combo)

        load_button = QPushButton("Laden")
        load_button.clicked.connect(self._load_selected_template)
        templates_layout.addWidget(load_button)

        self.template_name_input = QLineEdit()
        self.template_name_input.setPlaceholderText("Name für neue Vorlage")
        templates_layout.addWidget(self.template_name_input)

        save_button = QPushButton("Als Vorlage speichern")
        save_button.clicked.connect(self._save_as_template)
        templates_layout.addWidget(save_button)

        delete_button = QPushButton("Löschen")
        delete_button.clicked.connect(self._delete_selected_template)
        templates_layout.addWidget(delete_button)

        layout.addWidget(templates_group)

        # -------------------------------------------------
        # Kategorien
        # -------------------------------------------------

        categories_group = QGroupBox("Kategorien")
        categories_layout = QVBoxLayout(categories_group)

        self.checkboxes: dict[str, QCheckBox] = {}

        for key, label in CATEGORY_LABELS:

            checkbox = QCheckBox(label)

            self.checkboxes[key] = checkbox

            categories_layout.addWidget(checkbox)

        self.checkboxes["railways"].toggled.connect(
            self._update_tram_enabled
        )

        layout.addWidget(categories_group)

        # -------------------------------------------------
        # Vorschau
        # -------------------------------------------------

        layout.addWidget(QLabel("Vorschau der resultierenden Abfrage:"))

        self.preview = QPlainTextEdit()
        self.preview.setReadOnly(True)
        self.preview.setStyleSheet(
            "font-family: Consolas, monospace;"
        )
        layout.addWidget(self.preview)

        for checkbox in self.checkboxes.values():
            checkbox.toggled.connect(self._update_preview)

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._apply_and_close)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self._apply_config(self.controller.overpass_config)
        self._refresh_template_list()
        self._update_preview()

    # ---------------------------------------------------------
    # Konfiguration <-> Checkboxen
    # ---------------------------------------------------------

    def _apply_config(self, config: OverpassQueryConfig):

        for key, checkbox in self.checkboxes.items():
            checkbox.setChecked(getattr(config, key))

        self._update_tram_enabled()

    def _current_config(self) -> OverpassQueryConfig:

        values = {
            key: checkbox.isChecked()
            for key, checkbox in self.checkboxes.items()
        }

        return OverpassQueryConfig(**values)

    def _update_tram_enabled(self):

        # Der Tram-Unterpunkt ergibt nur Sinn, solange Gleise ueberhaupt
        # abgefragt werden.
        self.checkboxes["include_tram"].setEnabled(
            self.checkboxes["railways"].isChecked()
        )

    # ---------------------------------------------------------
    # Vorschau
    # ---------------------------------------------------------

    def _update_preview(self):

        # Fuer die Vorschau reicht ein Platzhalter-Bbox - der tatsaechliche
        # Kartenausschnitt wird erst beim echten Download eingesetzt.
        from src.map.objects.selection import Selection

        placeholder = Selection(
            min_lat=0.0, min_lon=0.0, max_lat=0.0, max_lon=0.0
        )

        query = build_query(placeholder, self._current_config())

        self.preview.setPlainText(query.strip())

    # ---------------------------------------------------------
    # Vorlagen
    # ---------------------------------------------------------

    def _refresh_template_list(self):

        self.template_combo.clear()
        self.template_combo.addItem("(keine)")

        for name in sorted(load_templates()):
            self.template_combo.addItem(name)

    def _load_selected_template(self):

        name = self.template_combo.currentText()

        if name == "(keine)":
            return

        templates = load_templates()

        config = templates.get(name)

        if config is None:
            return

        self._apply_config(config)
        self._update_preview()

    def _save_as_template(self):

        name = self.template_name_input.text().strip()

        if not name:

            QMessageBox.warning(
                self,
                "Kein Name",
                "Bitte einen Namen für die Vorlage eingeben.",
            )

            return

        save_template(name, self._current_config())

        self.template_name_input.clear()

        self._refresh_template_list()

        index = self.template_combo.findText(name)

        if index >= 0:
            self.template_combo.setCurrentIndex(index)

    def _delete_selected_template(self):

        name = self.template_combo.currentText()

        if name == "(keine)":
            return

        delete_template(name)

        self._refresh_template_list()

    # ---------------------------------------------------------
    # Übernehmen
    # ---------------------------------------------------------

    def _apply_and_close(self):

        self.controller.set_overpass_config(
            self._current_config()
        )

        self.accept()
