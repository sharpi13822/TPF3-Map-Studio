from PySide6.QtWidgets import QToolBar
from PySide6.QtCore import Qt


class MainToolbar(QToolBar):

    def __init__(self, actions):
        super().__init__("Werkzeuge")

        self.setToolButtonStyle(
            Qt.ToolButtonTextBesideIcon
        )

        self.addAction(actions.new_project)
        self.addAction(actions.open_project)
        self.addAction(actions.save_project)

        self.addSeparator()

        self.addAction(actions.marker_tool)
        self.addAction(actions.selection_tool)