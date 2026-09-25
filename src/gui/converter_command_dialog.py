import json
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QPlainTextEdit,
    QFileDialog,
    QDialogButtonBox,
    QApplication,
)

from src.osm.converter_command import build_converter_command


SETTINGS_PATH = Path.home() / ".tpf2_map_studio" / "converter_command_settings.json"

EXE_OPTIONS = (
    ("main.exe", "main.exe (vorkompiliert, aus den Releases)"),
    (r"venv\Scripts\python main.py", "main.py über venv (Python-Installation nötig)"),
)


class ConverterCommandDialog(QDialog):
    """
    Setzt den Aufrufbefehl fuer den externen OSM-TPF-Converter
    (main.exe ODER main.py ueber venv) aus der aktuellen Selection
    zusammen - erspart das manuelle Zusammensuchen/Abtippen von
    Kartengroesse und Bounds-Koordinaten.
    """

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.setWindowTitle("Converter-Befehl")
        self.setMinimumSize(640, 300)

        layout = QVBoxLayout(self)

        self.warning_label = QLabel("")
        self.warning_label.setWordWrap(True)
        self.warning_label.setStyleSheet(
            "color: #f39c12; font-weight: bold;"
        )
        layout.addWidget(self.warning_label)

        # -------------------------------------------------
        # main.exe oder main.py
        # -------------------------------------------------

        exe_row = QHBoxLayout()

        exe_row.addWidget(QLabel("Ausführen über:"))

        self.exe_combo = QComboBox()

        for value, label in EXE_OPTIONS:
            self.exe_combo.addItem(label, userData=value)

        self.exe_combo.currentIndexChanged.connect(self._on_exe_changed)
        exe_row.addWidget(self.exe_combo)

        layout.addLayout(exe_row)

        # -------------------------------------------------
        # Pfad zur .osm-Datei (Arg 1)
        # -------------------------------------------------

        osm_row = QHBoxLayout()

        osm_row.addWidget(QLabel(".osm-Datei (Arg 1):"))

        self.osm_path_input = QLineEdit()
        self.osm_path_input.setPlaceholderText(
            "z.B. map.osm (mit 'OSM als .osm exportieren...' erzeugt)"
        )
        self.osm_path_input.textChanged.connect(self._update_command)
        osm_row.addWidget(self.osm_path_input)

        browse_button = QPushButton("Durchsuchen...")
        browse_button.clicked.connect(self._browse_osm_file)
        osm_row.addWidget(browse_button)

        layout.addLayout(osm_row)

        # -------------------------------------------------
        # Ergebnis
        # -------------------------------------------------

        self.command_label = QLabel("")
        layout.addWidget(self.command_label)

        self.command_output = QPlainTextEdit()
        self.command_output.setReadOnly(True)
        self.command_output.setMaximumHeight(80)
        self.command_output.setStyleSheet(
            "font-family: Consolas, monospace;"
        )
        layout.addWidget(self.command_output)

        copy_button = QPushButton("In Zwischenablage kopieren")
        copy_button.clicked.connect(self._copy_to_clipboard)
        layout.addWidget(copy_button)

        # -------------------------------------------------
        # Schließen
        # -------------------------------------------------

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

        self._load_settings()
        self._update_command()

    def _browse_osm_file(self):

        filename, _ = QFileDialog.getOpenFileName(
            self,
            ".osm-Datei wählen",
            "",
            "OSM-Dateien (*.osm)"
        )

        if filename:
            self.osm_path_input.setText(filename)

    def _on_exe_changed(self):

        self._save_settings()
        self._update_command()

    def _load_settings(self):

        if not SETTINGS_PATH.is_file():
            return

        try:
            data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return

        saved_exe = data.get("exe_name")

        for index in range(self.exe_combo.count()):

            if self.exe_combo.itemData(index) == saved_exe:
                self.exe_combo.setCurrentIndex(index)
                break

    def _save_settings(self):

        try:
            SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

            SETTINGS_PATH.write_text(
                json.dumps(
                    {"exe_name": self.exe_combo.currentData()},
                    indent=2,
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
        except OSError:
            pass

    def _update_command(self):

        exe_name = self.exe_combo.currentData()

        self.command_label.setText(
            f"Fertiger Befehl ({exe_name} im Converter-Ordner ausführen):"
        )

        selection = self.controller.project.selection

        if selection is None:

            self.command_output.setPlainText("")

            self.warning_label.setText(
                "Kein Kartenausschnitt gesetzt (Rechteck-Tool verwenden)."
            )

            return

        osm_path = self.osm_path_input.text().strip() or "map.osm"

        # Nur der Dateiname wird als Arg1 verwendet (der Converter wird
        # im selben Ordner wie die .osm-Datei ausgefuehrt, siehe Tutorial).
        osm_filename = Path(osm_path).name

        result = build_converter_command(
            selection,
            osm_filename,
            exe_name=exe_name,
        )

        self.command_output.setPlainText(result.command)

        if result.is_rotated:

            self.warning_label.setText(
                "Achtung: Diese Auswahl ist gedreht - der Converter kennt "
                "keine Drehung und erwartet eine einfache, achsenparallele "
                "Bounding Box. Die hier berechnete Box ist die umschließende "
                "Box des gedrehten Bands und passt NICHT exakt zu dessen "
                "tatsächlicher Form."
            )

        else:

            self.warning_label.setText("")

    def _copy_to_clipboard(self):

        QApplication.clipboard().setText(
            self.command_output.toPlainText()
        )
