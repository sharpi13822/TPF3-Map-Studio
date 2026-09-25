from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QDialogButtonBox,
    QLabel,
)

from src.osm.preflight_check import run_preflight_check, STATUS_ICONS


STATUS_COLORS = {
    "ok": "#2ecc71",
    "warning": "#f39c12",
    "error": "#e74c3c",
    "info": "#7f8c8d",
}


class PreflightCheckDialog(QDialog):
    """
    Zeigt die Vorab-Pruefung fuer das aktuell geladene OSM-Projekt an -
    strukturelle Ampel-Checks plus informative Dichte-Kennzahlen (siehe
    src/osm/preflight_check.py fuer die Begruendung dieser Trennung).
    """

    def __init__(self, parent, controller):
        super().__init__(parent)

        self.controller = controller

        self.setWindowTitle("Vorab-Prüfung")
        self.setMinimumSize(620, 480)

        layout = QVBoxLayout(self)

        layout.addWidget(
            QLabel(
                "Prüfung des aktuell geladenen OSM-Kartenausschnitts, "
                "bevor der grosse Import-Lauf gestartet wird:"
            )
        )

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["", "Prüfpunkt", "Ergebnis"])
        self.tree.setColumnWidth(0, 28)
        self.tree.setColumnWidth(1, 160)
        layout.addWidget(self.tree)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        buttons.rejected.connect(self.reject)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

        self._run_and_display()

    def _run_and_display(self):

        self.tree.clear()

        project = self.controller.project

        results = run_preflight_check(
            project,
            self.controller.overpass_config,
        )

        for result in results:

            item = QTreeWidgetItem([
                STATUS_ICONS.get(result.status, ""),
                result.label,
                result.message,
            ])

            color = STATUS_COLORS.get(result.status)

            if color:
                item.setForeground(1, self._brush(color))
                item.setForeground(2, self._brush(color))

            self.tree.addTopLevelItem(item)

        self.tree.resizeColumnToContents(1)

    @staticmethod
    def _brush(hex_color: str):

        from PySide6.QtGui import QBrush, QColor

        return QBrush(QColor(hex_color))
