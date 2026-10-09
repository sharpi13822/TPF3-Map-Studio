import json
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTreeWidget,
    QTreeWidgetItem,
    QFileDialog,
    QDialogButtonBox,
)
from PySide6.QtCore import Qt

from src.core.project_summary import scan_projects_folder
from src.i18n import tr


SETTINGS_PATH = Path.home() / ".tpf2_map_studio" / "dashboard_settings.json"


class ProjectDashboardDialog(QDialog):
    """
    Uebersicht aller gespeicherten .tpf2ms-Projekte in einem gewaehlten
    Ordner, mit Status pro Projekt (Auswahl, OSM-Daten, Heightmap).

    Zeigt bewusst KEINEN Status zu fehlgeschlagenen Kanten - das
    haengt an der stdout.txt-Diagnose, die noch nicht gebaut ist.
    """

    def __init__(self, parent, window):
        super().__init__(parent)

        # 'window' ist das MainWindow - fuer das direkte Oeffnen eines
        # ausgewaehlten Projekts ueber dessen _load_project_file().
        self.window = window

        self.setWindowTitle(tr("Projekt-Dashboard"))
        self.setMinimumSize(820, 480)

        layout = QVBoxLayout(self)

        # -------------------------------------------------
        # Ordner
        # -------------------------------------------------

        folder_row = QHBoxLayout()

        folder_row.addWidget(QLabel(tr("Projekte-Ordner:")))

        self.folder_input = QLineEdit()
        folder_row.addWidget(self.folder_input)

        browse_button = QPushButton(tr("Durchsuchen..."))
        browse_button.clicked.connect(self._browse_folder)
        folder_row.addWidget(browse_button)

        refresh_button = QPushButton(tr("Aktualisieren"))
        refresh_button.clicked.connect(self._refresh)
        folder_row.addWidget(refresh_button)

        layout.addLayout(folder_row)

        # -------------------------------------------------
        # Liste
        # -------------------------------------------------

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels([
            tr("Projekt"), tr("Auswahl"), tr("OSM-Daten"), tr("Heightmap"), tr("Geändert"), tr("Datei"),
        ])
        self.tree.setColumnWidth(0, 160)
        self.tree.setColumnWidth(1, 200)
        self.tree.setColumnWidth(2, 110)
        self.tree.setColumnWidth(3, 130)
        self.tree.setColumnWidth(4, 140)
        self.tree.itemDoubleClicked.connect(self._open_selected)
        layout.addWidget(self.tree)

        # -------------------------------------------------
        # Buttons
        # -------------------------------------------------

        button_row = QHBoxLayout()

        open_button = QPushButton(tr("Ausgewähltes Projekt öffnen"))
        open_button.clicked.connect(self._open_selected)
        button_row.addWidget(open_button)

        button_row.addStretch()

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        button_row.addWidget(buttons)

        layout.addLayout(button_row)

        self._load_settings()
        self._refresh()

    # ---------------------------------------------------------
    # Ordner wählen / merken
    # ---------------------------------------------------------

    def _browse_folder(self):

        start_dir = self.folder_input.text() or str(Path.home())

        chosen = QFileDialog.getExistingDirectory(
            self,
            tr("Projekte-Ordner wählen"),
            start_dir,
        )

        if chosen:
            self.folder_input.setText(chosen)
            self._save_settings()
            self._refresh()

    def _load_settings(self):

        if not SETTINGS_PATH.is_file():
            return

        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        self.folder_input.setText(data.get("projects_folder", ""))

    def _save_settings(self):

        try:
            SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

            SETTINGS_PATH.write_text(
                json.dumps(
                    {"projects_folder": self.folder_input.text()},
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except OSError:
            pass

    # ---------------------------------------------------------
    # Liste befüllen
    # ---------------------------------------------------------

    def _refresh(self):

        self._save_settings()

        self.tree.clear()

        folder_text = self.folder_input.text().strip()

        if not folder_text:
            return

        folder = Path(folder_text)

        summaries = scan_projects_folder(folder)

        for summary in summaries:

            if summary.error:

                item = QTreeWidgetItem([
                    summary.name,
                    tr("Datei fehlerhaft: {error}").format(error=summary.error),
                    "", "", "",
                    str(summary.file_path),
                ])

                self.tree.addTopLevelItem(item)

                continue

            osm_text = (
                tr("{way_count} Wege").format(way_count=summary.way_count)
                if summary.has_osm
                else tr("keine OSM-Daten")
            )

            heightmap_text = (
                tr("exportiert ({item})").format(item=summary.heightmap_exported_at[:10])
                if summary.heightmap_exported
                else tr("fehlt noch")
            )

            item = QTreeWidgetItem([
                summary.name,
                summary.selection_text,
                osm_text,
                heightmap_text,
                summary.file_modified_at[:16].replace("T", " "),
                str(summary.file_path),
            ])

            item.setData(0, Qt.UserRole, str(summary.file_path))

            self.tree.addTopLevelItem(item)

    # ---------------------------------------------------------
    # Öffnen
    # ---------------------------------------------------------

    def _open_selected(self):

        item = self.tree.currentItem()

        if item is None:
            return

        file_path = item.data(0, Qt.UserRole)

        if not file_path:
            return

        self.window._load_project_file(file_path)

        self.accept()
