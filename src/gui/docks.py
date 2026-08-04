from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QWidget,
    QFormLayout,
    QLabel,
    QLineEdit,
    QPushButton,
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

    parent.delete_marker_button = QPushButton(
        "Marker löschen"
    )

    parent.delete_marker_button.clicked.connect(
        parent._delete_marker
    )

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

    layout.addRow(
       parent.delete_marker_button
    ) 

    dock.setWidget(form)

    return dock