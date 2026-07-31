from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QWidget,
    QFormLayout,
    QLabel,
    QLineEdit,
    QListWidget,
)


def create_project_dock(parent):

    dock = QDockWidget("Projekt", parent)
    dock.setAllowedAreas(Qt.LeftDockWidgetArea)
    dock.setWidget(QListWidget())

    return dock


def create_properties_dock(parent):

    dock = QDockWidget("Eigenschaften", parent)
    dock.setAllowedAreas(Qt.RightDockWidgetArea)

    form = QWidget()

    layout = QFormLayout(form)

    parent.prop_id = QLabel()

    parent.prop_name = QLineEdit()
    parent.prop_name.editingFinished.connect(
        parent._marker_name_changed
    )

    parent.prop_lat = QLabel()

    parent.prop_lon = QLabel()

    layout.addRow(
        "ID:",
        parent.prop_id
    )

    layout.addRow(
        "Name:",
        parent.prop_name
    )

    layout.addRow(
        "Breite:",
        parent.prop_lat
    )

    layout.addRow(
        "Länge:",
        parent.prop_lon
    )

    dock.setWidget(form)

    return dock