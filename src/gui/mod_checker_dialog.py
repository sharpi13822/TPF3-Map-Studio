import json
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QCheckBox,
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QFileDialog,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt

from src.mods.mod_checker import run_check
from src.i18n import tr


SETTINGS_PATH = Path.home() / ".tpf2_map_studio" / "mod_checker_settings.json"

DEFAULT_WORKSHOP_PATH = (
    r"C:\Program Files (x86)\Steam\steamapps\workshop\content\1066780"
)
DEFAULT_LOCAL_PATH = str(
    Path.home() / "Documents" / "Transport Fever 2" / "mod"
)

TOGGLES = (
    ("bruecken", tr("Brücken nutzen")),
    ("signale", tr("Signale nutzen")),
    ("wald_import", tr("Wald-Import nutzen")),
    ("objekte", tr("Straßenobjekte nutzen")),
    ("paver", tr("Paver / Bodentexturen nutzen")),
    ("elektrifizierte_gleise", tr("Elektrifizierte Gleise im Gebiet")),
)

STATUS_LABELS = {
    "found_workshop": tr("✅ gefunden (Workshop)"),
    "found_local": tr("✅ gefunden (lokal)"),
    "missing": tr("❌ fehlt"),
    "manual": tr("❓ nicht automatisch prüfbar"),
    "skipped": tr("➖ übersprungen (Funktion nicht genutzt)"),
}


class ModCheckerDialog(QDialog):
    """
    Gleicht installierte Mods (Steam-Workshop-Ordner + lokaler mod-Ordner)
    gegen die offizielle Mod-Liste des OSM-TPF2-Importers ab (siehe
    https://github.com/Vacuum-Tube/OSM-TPF2-Importer/blob/main/doc/Mods.md).

    Prueft NUR, ob ein Mod installiert ist - nicht, ob er im aktuell
    geladenen Spielstand auch aktiviert ist (das steht im binaeren
    Savegame, nicht in einer lesbaren Konfigurationsdatei).
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle(tr("Mod-Checker"))
        self.setMinimumSize(720, 560)

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # Pfade
        # -------------------------------------------------

        paths_group = QGroupBox(tr("Pfade"))
        paths_form = QFormLayout(paths_group)

        self.workshop_input = QLineEdit()
        self.local_input = QLineEdit()
        self.importer_input = QLineEdit()
        self.importer_input.setPlaceholderText(
            tr("Ordnername unter .../mod/, z.B. osm_tpf2_importer")
        )

        paths_form.addRow(
            tr("Steam-Workshop-Ordner:"),
            self._path_row(self.workshop_input),
        )

        paths_form.addRow(
            tr("Lokaler mod-Ordner:"),
            self._path_row(self.local_input),
        )

        paths_form.addRow(
            tr("OSM-Importer-Ordnername:"),
            self.importer_input,
        )

        layout.addWidget(paths_group)

        # -------------------------------------------------
        # Optionen
        # -------------------------------------------------

        options_group = QGroupBox(
            tr("Genutzte Importer-Funktionen "
            "(bestimmt, welche Mod-Kategorien geprüft werden)")
        )
        options_layout = QHBoxLayout(options_group)

        self.toggle_checkboxes: dict[str, QCheckBox] = {}

        for key, label in TOGGLES:

            checkbox = QCheckBox(label)
            checkbox.setChecked(True)

            self.toggle_checkboxes[key] = checkbox

            options_layout.addWidget(checkbox)

        layout.addWidget(options_group)

        # -------------------------------------------------
        # Prüfen-Button
        # -------------------------------------------------

        check_button = QPushButton(tr("Prüfen"))
        check_button.clicked.connect(self._run_check)
        layout.addWidget(check_button)

        # -------------------------------------------------
        # Warnungen (Crash-Mods, Duplikat)
        # -------------------------------------------------

        self.warning_label = QLabel("")
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet(
            "color: #c0392b; font-weight: bold;"
        )
        layout.addWidget(self.warning_label)

        # -------------------------------------------------
        # Ergebnisliste
        # -------------------------------------------------

        self.result_tree = QTreeWidget()
        self.result_tree.setHeaderLabels([tr("Mod"), tr("Status"), tr("Hinweis")])
        self.result_tree.setColumnWidth(0, 340)
        self.result_tree.setColumnWidth(1, 170)
        layout.addWidget(self.result_tree)

        # -------------------------------------------------
        # Schließen
        # -------------------------------------------------

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

        self._load_settings()

    # ---------------------------------------------------------
    # Hilfsfunktionen UI
    # ---------------------------------------------------------

    def _path_row(self, line_edit: QLineEdit):

        container = QHBoxLayout()

        container.addWidget(line_edit)

        browse_button = QPushButton(tr("Durchsuchen..."))

        browse_button.clicked.connect(
            lambda: self._browse_for(line_edit)
        )

        container.addWidget(browse_button)

        from PySide6.QtWidgets import QWidget

        widget = QWidget()
        widget.setLayout(container)

        return widget

    def _browse_for(self, line_edit: QLineEdit):

        start_dir = line_edit.text() or str(Path.home())

        chosen = QFileDialog.getExistingDirectory(
            self,
            tr("Ordner wählen"),
            start_dir,
        )

        if chosen:
            line_edit.setText(chosen)

    # ---------------------------------------------------------
    # Einstellungen laden/speichern
    # ---------------------------------------------------------

    def _load_settings(self):

        data = {}

        if SETTINGS_PATH.is_file():

            try:
                data = json.loads(
                    SETTINGS_PATH.read_text(encoding="utf-8")
                )
            except (OSError, json.JSONDecodeError):
                data = {}

        self.workshop_input.setText(
            data.get("workshop_path", DEFAULT_WORKSHOP_PATH)
        )

        self.local_input.setText(
            data.get("local_path", DEFAULT_LOCAL_PATH)
        )

        self.importer_input.setText(
            data.get("importer_folder_name", "")
        )

        toggle_states = data.get("toggles", {})

        for key, checkbox in self.toggle_checkboxes.items():
            checkbox.setChecked(
                toggle_states.get(key, True)
            )

    def _save_settings(self):

        data = {
            "workshop_path": self.workshop_input.text(),
            "local_path": self.local_input.text(),
            "importer_folder_name": self.importer_input.text(),
            "toggles": {
                key: checkbox.isChecked()
                for key, checkbox in self.toggle_checkboxes.items()
            },
        }

        try:
            SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

            SETTINGS_PATH.write_text(
                json.dumps(data, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError:
            pass

    # ---------------------------------------------------------
    # Prüfung ausführen
    # ---------------------------------------------------------

    def _run_check(self):

        self._save_settings()

        workshop_path = Path(self.workshop_input.text())
        local_path = Path(self.local_input.text())
        importer_name = self.importer_input.text().strip()

        enabled_toggles = {
            key
            for key, checkbox in self.toggle_checkboxes.items()
            if checkbox.isChecked()
        }

        report = run_check(
            workshop_path=workshop_path,
            local_path=local_path,
            importer_folder_name=importer_name,
            enabled_toggles=enabled_toggles,
        )

        self._display_report(report, workshop_path, local_path)

    def _display_report(self, report, workshop_path, local_path):

        self.result_tree.clear()

        warnings = []

        if not report.workshop_path_ok:
            warnings.append(
                tr("Workshop-Ordner nicht gefunden: {workshop_path}").format(workshop_path=workshop_path)
            )

        if not report.local_path_ok:
            warnings.append(
                tr("Lokaler mod-Ordner nicht gefunden: {local_path}").format(local_path=local_path)
            )

        for description, path in report.crash_mods_found:
            warnings.append(
                tr("⚠ Bekannter Problem-Mod gefunden: {description} ({path})").format(description=description, path=path)
            )

        if report.importer_duplicate:

            locations = ", ".join(
                str(path) for path in report.importer_locations
            )

            warnings.append(
                tr("⚠ OSM-TPF2-Importer scheint mehrfach installiert zu sein: {locations}").format(locations=locations)
            )

        self.warning_label.setText("\n".join(warnings))

        # -------------------------------------------------
        # Ergebnisse nach Kategorie gruppieren
        # -------------------------------------------------

        categories: dict[str, QTreeWidgetItem] = {}

        for result in report.results:

            category = result.mod.category

            if category not in categories:

                category_item = QTreeWidgetItem([category, "", ""])

                font = category_item.font(0)
                font.setBold(True)
                category_item.setFont(0, font)

                self.result_tree.addTopLevelItem(category_item)

                categories[category] = category_item

            status_text = STATUS_LABELS.get(result.status, result.status)

            note_parts = []

            if result.mod.note:
                note_parts.append(result.mod.note)

            if result.found_display_name:
                note_parts.append(tr("gefunden als: {found_display_name}").format(found_display_name=result.found_display_name))

            item = QTreeWidgetItem([
                result.mod.name,
                status_text,
                " – ".join(note_parts),
            ])

            categories[category].addChild(item)

        self.result_tree.expandAll()
