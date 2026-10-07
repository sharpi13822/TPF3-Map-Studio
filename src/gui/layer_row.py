from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QCheckBox,
    QPushButton,
    QSlider,
    QMenu,
)

from src.gui.icon_set import icon, icon_path


# Layer-Name -> Symbol aus src/gui/icons
ICON_NAMES = {
    "Straßen": "strassen",
    "Bahn": "bahn",
    "Gebäude": "gebaeude",
    "Wasser": "wasser",
    "Gewässer": "wasser",
    "Flüsse": "fluesse",
    "Parks": "parks",
    "Landnutzung": "landnutzung",
    "Vegetation": "vegetation",
    "Bahnhöfe": "bahnhoefe",
}

ICON_SIZE = 18


class LayerRowWidget(QWidget):
    """
    Eine einzelne Zeile im LayerPanel.

    Der Anfangszustand von Haken, Schloss und Balken wird aus dem
    LayerManager gelesen, damit die Zeile immer zum tatsaechlichen
    Zustand passt (z.B. Ebenen beim Start ausgeblendet).
    """

    def __init__(
        self,
        controller,
        layer,
        text
    ):
        super().__init__()

        self.controller = controller
        self.layer = layer

        manager = controller.layer_manager

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

        self.visible.setChecked(
            manager.is_visible(layer)
        )

        self.visible.toggled.connect(
            self._visibility_changed
        )

        # ---------------------------------------------------------
        # Sperren
        # ---------------------------------------------------------

        locked = manager.is_locked(layer)

        self.lock = QPushButton()

        self.lock.setCheckable(True)

        self.lock.setChecked(locked)

        self.lock.setFixedWidth(34)

        self.lock.setIconSize(QSize(16, 16))

        self.lock.setToolTip("Ebene sperren: keine Auswahl und Bearbeitung in der Karte")

        self._update_lock_icon(locked)

        self.lock.toggled.connect(
            self._lock_changed
        )

        # ---------------------------------------------------------
        # Name
        # ---------------------------------------------------------

        self.icon_label = QLabel()

        self.icon_label.setFixedSize(ICON_SIZE + 2, ICON_SIZE + 2)

        icon_name = ICON_NAMES.get(text)

        if icon_name:
            pixmap = QPixmap(str(icon_path(icon_name, "_hell")))
            self.icon_label.setPixmap(
                pixmap.scaled(
                    ICON_SIZE,
                    ICON_SIZE,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

        self.label = QLabel(text)

        self.label.setMinimumWidth(120)

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
            int(round(manager.opacity(layer) * 100))
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

        self.up_button = QPushButton()

        self.up_button.setIcon(icon("pfeil_hoch"))

        self.up_button.setIconSize(QSize(14, 14))

        self.up_button.setToolTip("Ebene nach oben (vor die anderen)")

        self.up_button.setFixedWidth(28)

        self.up_button.clicked.connect(
            self._move_up
        )

        self.down_button = QPushButton()

        self.down_button.setIcon(icon("pfeil_runter"))

        self.down_button.setIconSize(QSize(14, 14))

        self.down_button.setToolTip("Ebene nach unten (hinter die anderen)")

        self.down_button.setFixedWidth(28)

        self.down_button.clicked.connect(
            self._move_down
        )

        # ---------------------------------------------------------
        # Layout füllen
        # ---------------------------------------------------------

        layout.addWidget(self.visible)
        layout.addWidget(self.lock)
        layout.addWidget(self.icon_label)
        layout.addWidget(self.label)
        layout.addStretch()
        layout.addWidget(self.slider)
        layout.addWidget(self.up_button)
        layout.addWidget(self.down_button)

    def _update_lock_icon(self, locked):
        """Zeigt das geschlossene oder offene Schloss."""

        self.lock.setIcon(
            icon("schloss_zu" if locked else "schloss_offen")
        )

    # ---------------------------------------------------------
    # Zustand aus dem LayerManager uebernehmen
    # ---------------------------------------------------------

    def sync_from_state(self):
        """
        Setzt Haken, Schloss und Balken auf den Zustand des
        LayerManagers (z.B. nach dem Laden eines Projekts). Die Signale
        sind dabei gesperrt, es wird also nichts erneut ausgeloest.
        """

        manager = self.controller.layer_manager

        locked = manager.is_locked(self.layer)

        widgets = (self.visible, self.lock, self.slider)

        for widget in widgets:
            widget.blockSignals(True)

        self.visible.setChecked(manager.is_visible(self.layer))

        self.lock.setChecked(locked)

        self._update_lock_icon(locked)

        self.slider.setValue(
            int(round(manager.opacity(self.layer) * 100))
        )

        for widget in widgets:
            widget.blockSignals(False)

    # ---------------------------------------------------------
    # Sichtbarkeit
    # ---------------------------------------------------------

    def _visibility_changed(self, checked):

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

        self._update_lock_icon(checked)

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

        self._refresh_panel()

    def _move_down(self):

        self.controller.move_layer_down(
            self.layer
        )

        self._refresh_panel()

    def _refresh_panel(self):
        """
        Sortiert die Zeilen im Panel nach der neuen Reihenfolge des
        LayerManagers neu.
        """

        panel = self.parentWidget()

        if panel is not None and hasattr(panel, "refresh_order"):
            panel.refresh_order()

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
