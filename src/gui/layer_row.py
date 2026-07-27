from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QPushButton,
    QSlider,
    QMenu,
)


ICON_MAP = {
    "Straßen":      "🛣️",
    "Bahn":         "🚆",
    "Gebäude":      "🏘️",
    "Gewässer":     "💦",
    "Flüsse":       "🏞️",
    "Parks":        "🌳",
    "Landnutzung":  "🌾",
    "Vegetation":   "🌲",
}


class LayerRowWidget(QWidget):
    """
    Eine einzelne Zeile im LayerPanel.
    """

    def __init__(self, controller, layer, text):
        super().__init__()

        print("LayerRowWidget erstellt:", layer)

        self.controller = controller
        self.layer = layer

    def __init__(
        self,
        controller,
        layer,
        text
    ):
        super().__init__()

        self.controller = controller
        self.layer = layer

        # ---------------------------------------------------------
        # Layout
        # ---------------------------------------------------------

        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(4)

        # ---------------------------------------------------------
        # Kontextmenü
        # ---------------------------------------------------------

        self.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.customContextMenuRequested.connect(
            self._show_menu
        )

        # ---------------------------------------------------------
        # Sichtbarkeit
        # ---------------------------------------------------------

        self.visible = QCheckBox()

        self.visible.setChecked(True)

        self.visible.toggled.connect(
            self._visibility_changed
        )

        # ---------------------------------------------------------
        # Sperren
        # ---------------------------------------------------------

        self.lock = QPushButton("🔓")

        self.lock.setCheckable(True)

        self.lock.setFixedWidth(34)

        self.lock.toggled.connect(
            self._lock_changed
        )

        # ---------------------------------------------------------
        # Name
        # ---------------------------------------------------------

        icon = ICON_MAP.get(
            text,
            "📄"
        )

        self.label = QLabel(
            f"{icon} {text}"
        )

        self.label.setMinimumWidth(140)

        # ---------------------------------------------------------
        # Opacity
        # ---------------------------------------------------------

        self.slider = QSlider(
            Qt.Horizontal
        )

        self.slider.setRange(
            0,
            100
        )

        self.slider.setValue(
            100
        )

        self.slider.setFixedWidth(
            90
        )

        self.slider.valueChanged.connect(
            self._opacity_changed
        )

        # ---------------------------------------------------------
        # Reihenfolge
        # ---------------------------------------------------------

        self.up_button = QPushButton("⬆")

        self.up_button.setFixedWidth(28)

        self.up_button.clicked.connect(
            self._move_up
        )

        self.down_button = QPushButton("⬇")

        self.down_button.setFixedWidth(28)

        self.down_button.clicked.connect(
            self._move_down
        )

        # ---------------------------------------------------------
        # Layout füllen
        # ---------------------------------------------------------

        layout.addWidget(self.visible)
        layout.addWidget(self.lock)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.slider)
        layout.addWidget(self.up_button)
        layout.addWidget(self.down_button)

    # ---------------------------------------------------------
    # Sichtbarkeit
    # ---------------------------------------------------------

    def _visibility_changed(self, checked):
        print(f"GUI  layer={self.layer.name}  checked={checked}")
        self.controller.set_layer_visible(self.layer, checked)

    # ---------------------------------------------------------
    # Sperren
    # ---------------------------------------------------------

    def _lock_changed(
        self,
        checked
    ):

        self.controller.set_layer_locked(
            self.layer,
            checked
        )

        self.lock.setText(
            "🔒" if checked else "🔓"
        )

    # ---------------------------------------------------------
    # Opacity
    # ---------------------------------------------------------

    def _opacity_changed(
        self,
        value
    ):

        self.controller.set_layer_opacity(
            self.layer,
            value / 100.0
        )

    # ---------------------------------------------------------
    # Reihenfolge
    # ---------------------------------------------------------

    def _move_up(self):

        self.controller.move_layer_up(
            self.layer
        )

    def _move_down(self):

        self.controller.move_layer_down(
            self.layer
        )

    # ---------------------------------------------------------
    # Kontextmenü
    # ---------------------------------------------------------

    def _show_menu(
        self,
        pos
    ):

        menu = QMenu(self)

        show_action = menu.addAction(
            "Layer anzeigen"
        )

        hide_action = menu.addAction(
            "Layer ausblenden"
        )

        menu.addSeparator()

        lock_action = menu.addAction(
            "Layer sperren"
        )

        unlock_action = menu.addAction(
            "Layer entsperren"
        )

        menu.addSeparator()

        reset_action = menu.addAction(
            "Deckkraft zurücksetzen"
        )

        action = menu.exec(
            self.mapToGlobal(pos)
        )

        if action == show_action:
            self.visible.setChecked(True)

        elif action == hide_action:
            self.visible.setChecked(False)

        elif action == lock_action:
            self.lock.setChecked(True)

        elif action == unlock_action:
            self.lock.setChecked(False)

        elif action == reset_action:
            self.slider.setValue(100)