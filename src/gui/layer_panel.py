from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)

from src.gui.layer_row import LayerRowWidget


class LayerPanel(QWidget):
    """
    Panel zur Verwaltung der Kartenlayer.
    """

    def __init__(self, controller):

        super().__init__()

        self.controller = controller

        layout = QVBoxLayout(self)

        self._layout = layout

        # ---------------------------------------------------------
        # Titel
        # ---------------------------------------------------------

        title = QLabel("Layer")

        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)

        # ---------------------------------------------------------
        # Layer (in der Reihenfolge des LayerManagers)
        # ---------------------------------------------------------

        self.rows = []

        for layer in controller.layer_manager.layers:
            self._add_layer(
                layout,
                layer.label,
                layer,
            )

        layout.addStretch()

    # ---------------------------------------------------------
    # Layer hinzufügen
    # ---------------------------------------------------------

    def _add_layer(
        self,
        layout,
        text,
        layer
    ):

        row = LayerRowWidget(
            self.controller,
            layer,
            text
        )

        layout.addWidget(
            row
        )

        self.rows.append(
            row
        )

    # ---------------------------------------------------------
    # Reihenfolge neu anzeigen
    # ---------------------------------------------------------

    def refresh_order(self):
        """
        Ordnet die Zeilen nach der aktuellen Reihenfolge des
        LayerManagers neu an (nach einem Klick auf die Pfeile).
        Index 0 im Layout ist der Titel, danach folgen die Zeilen.
        """

        by_layer = {
            row.layer: row
            for row in self.rows
        }

        self.rows = [
            by_layer[layer]
            for layer in self.controller.layer_manager.layers
            if layer in by_layer
        ]

        for row in self.rows:
            self._layout.removeWidget(row)

        for index, row in enumerate(self.rows):
            self._layout.insertWidget(1 + index, row)

    # ---------------------------------------------------------
    # Komplett aus dem LayerManager neu uebernehmen
    # ---------------------------------------------------------

    def sync_from_state(self):
        """
        Uebernimmt Haken, Schloss, Balken und Reihenfolge aus dem
        LayerManager (z.B. nach dem Laden eines Projekts).
        """

        for row in self.rows:
            row.sync_from_state()

        self.refresh_order()
