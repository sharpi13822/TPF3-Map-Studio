from PySide6.QtWidgets import QDockWidget

from src.gui.layer_panel import LayerPanel
from src.i18n import tr


def create_layer_dock(window):

    dock = QDockWidget(tr("Layer"), window)

    dock.setObjectName("LayerDock")

    dock.setWidget(
        LayerPanel(
            window.map_widget.controller
        )
    )

    return dock