from PySide6.QtGui import QAction

from .icons import icon


class AppActions:

    def __init__(self, parent):

        # Datei
        self.new_project = QAction("Neu", parent)
        self.new_project.setToolTip("Neues Projekt")
        self.new_project.setIcon(
            icon("new")
        )
        self.open_project = QAction("Öffnen", parent)
        self.open_project.setToolTip("Projekt öffnen")
        self.open_project.setIcon(
           icon("open")
        )
        self.save_project = QAction("Speichern", parent)
        self.save_project.setToolTip("Projekt speichern")
        self.save_project.setIcon(
            icon("save")
                
        )
        self.save_project_as = QAction("Speichern unter...",parent)
        self.close_project = QAction("Projekt schließen", parent)

        # Bearbeiten
        self.undo = QAction("Rückgängig", parent)
        self.undo.setIcon(icon("undo"))
        self.undo.setEnabled(False)
        self.redo = QAction("Wiederholen", parent)
        self.redo.setIcon(icon("redo"))
        self.redo.setEnabled(False)

        # Werkzeuge
        self.marker_tool = QAction("Marker", parent)
        self.marker_tool.setIcon(
            icon("marker")
        )
        self.marker_tool.setCheckable(True)
        self.marker_tool.setToolTip("Marker setzen")
        self.selection_tool = QAction("Auswahl", parent)
        self.selection_tool.setIcon(
            icon("select")
        )
        self.selection_tool.setCheckable(True)
        self.selection_tool.setToolTip("Bereich auswählen")

        self.rectangle_tool = QAction("Rechteck-Tool", parent)
        self.rectangle_tool.setIcon(
            icon("rectangle_tool")
        )
        self.rectangle_tool.setToolTip(
            "Gedrehtes Kartenband anlegen (Mittelpunkt, Größe, Drehwinkel)"
        )

        self.measure_tool = QAction("Koordinaten-Messwerkzeug", parent)
        self.measure_tool.setIcon(
            icon("measure")
        )
        self.measure_tool.setCheckable(True)
        self.measure_tool.setToolTip(
            "Zwei Punkte anklicken, um lat/lon und Distanz anzuzeigen"
        )

        self.exit = QAction("Beenden", parent)
        self.exit.triggered.connect(parent.close)

        # Test
        self.test_marker = QAction("Testmarker", parent)