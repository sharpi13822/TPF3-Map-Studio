from PySide6.QtWidgets import QToolBar
from PySide6.QtCore import Qt
from PySide6.QtCore import QSize
from PySide6.QtCore import Qt, QSize
from src.i18n import tr


class MainToolbar(QToolBar):

    def __init__(self, actions):
        super().__init__(tr("Werkzeuge"))
        self.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self.setIconSize(QSize(24, 24))
        self.setMovable(False)

       # self.setToolButtonStyle(
       #     Qt.ToolButtonTextBesideIcon
       # )

        self.addAction(actions.new_project)
        self.addAction(actions.open_project)
        self.addAction(actions.save_project)

        self.addSeparator()

        self.addAction(actions.undo)
        self.addAction(actions.redo)

        self.addSeparator()

        self.addAction(actions.marker_tool)
        self.addAction(actions.selection_tool)
        self.addAction(actions.rectangle_tool)
        self.addAction(actions.measure_tool)