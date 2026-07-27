from PySide6.QtWidgets import QToolBar


class MainToolbar(QToolBar):

    def __init__(self, actions):
        super().__init__("Werkzeuge")

        self.addAction(actions.new_project)
        self.addAction(actions.open_project)
        self.addAction(actions.save_project)