from PySide6.QtGui import QAction


class AppActions:

    def __init__(self, parent):

        # Datei
        self.new_project = QAction("Neu", parent)
        self.open_project = QAction("Öffnen", parent)
        self.save_project = QAction("Speichern", parent)

        self.exit = QAction("Beenden", parent)
        self.exit.triggered.connect(parent.close)

        # Test
        self.test_marker = QAction("Testmarker", parent)