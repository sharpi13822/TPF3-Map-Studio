from PySide6.QtGui import QAction


class AppActions:

    def __init__(self, parent):

        # Datei
        self.new_project = QAction("Neu", parent)
        self.open_project = QAction("Öffnen", parent)
        self.save_project = QAction("Speichern", parent)
        self.save_project_as = QAction("Speichern unter...",parent)
        self.close_project = QAction("Projekt schließen", parent)

        # Bearbeiten
        self.undo = QAction("Rückgängig", parent)
        self.redo = QAction("Wiederholen", parent)

        # Werkzeuge
        self.marker_tool = QAction("Marker", parent)
        self.marker_tool.setCheckable(True)

        self.selection_tool = QAction("Auswahl", parent)
        self.selection_tool.setCheckable(True)

        self.exit = QAction("Beenden", parent)
        self.exit.triggered.connect(parent.close)

        # Test
        self.test_marker = QAction("Testmarker", parent)