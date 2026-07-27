from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
)

from src.map.layer import Layer
from src.gui.layer_row import LayerRowWidget


class LayerPanel(QWidget):
    """
    Panel zur Verwaltung der Kartenlayer.
    """

    def __init__(self, controller):

        super().__init__()

        self.controller = controller

        layout = QVBoxLayout(self)

        # ---------------------------------------------------------
        # Titel
        # ---------------------------------------------------------

        title = QLabel("Layer")

        title.setAlignment(Qt.AlignCenter)

        layout.addWidget(title)

        # ---------------------------------------------------------
        # Layer
        # ---------------------------------------------------------

        self.rows = []

        for layer in Layer:
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