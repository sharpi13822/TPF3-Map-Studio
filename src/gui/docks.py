from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget,
    QListWidget,
    QTextEdit,
)


def create_project_dock(parent):

    dock = QDockWidget("Projekt", parent)
    dock.setAllowedAreas(Qt.LeftDockWidgetArea)
    dock.setWidget(QListWidget())

    return dock


def create_properties_dock(parent):

    dock = QDockWidget("Eigenschaften", parent)
    dock.setAllowedAreas(Qt.RightDockWidgetArea)
    dock.setWidget(QTextEdit())

    return dock