from PySide6.QtWidgets import QDockWidget

from src.gui.layer_panel import LayerPanel


def create_layer_dock(window):

    dock = QDockWidget("Layer", window)

    dock.setObjectName("LayerDock")

    dock.setWidget(
        LayerPanel(
            window.map_widget.controller
        )
    )

    return dock