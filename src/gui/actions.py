from PySide6.QtGui import QAction

from src.i18n import tr

from .icons import icon


class AppActions:

    def __init__(self, parent):

        # Datei
        self.new_project = QAction(tr("Neu"), parent)
        self.new_project.setToolTip(tr("Neues Projekt"))
        self.new_project.setIcon(
            icon("new")
        )
        self.open_project = QAction(tr("Öffnen"), parent)
        self.open_project.setToolTip(tr("Projekt öffnen"))
        self.open_project.setIcon(
           icon("open")
        )
        self.save_project = QAction(tr("Speichern"), parent)
        self.save_project.setToolTip(tr("Projekt speichern"))
        self.save_project.setIcon(
            icon("save")
                
        )
        self.save_project_as = QAction(tr("Speichern unter..."), parent)
        self.save_project_as.setToolTip(tr("Projekt unter neuem Namen speichern"))
        self.close_project = QAction(tr("Projekt schließen"), parent)
        self.close_project.setToolTip(tr("Aktuelles Projekt schließen und mit einem leeren Projekt weiterarbeiten"))

        # Bearbeiten
        self.undo = QAction(tr("Rückgängig"), parent)
        self.undo.setIcon(icon("undo"))
        self.undo.setEnabled(False)
        self.redo = QAction(tr("Wiederholen"), parent)
        self.redo.setIcon(icon("redo"))
        self.redo.setEnabled(False)

        # Werkzeuge
        self.marker_tool = QAction(tr("Marker"), parent)
        self.marker_tool.setIcon(
            icon("marker")
        )
        self.marker_tool.setCheckable(True)
        self.marker_tool.setToolTip(tr("Marker setzen"))
        self.selection_tool = QAction(tr("Auswahl"), parent)
        self.selection_tool.setIcon(
            icon("select")
        )
        self.selection_tool.setCheckable(True)
        self.selection_tool.setToolTip(tr("Bereich auswählen"))

        self.rectangle_tool = QAction(tr("Rechteck-Tool"), parent)
        self.rectangle_tool.setIcon(
            icon("rectangle_tool")
        )
        self.rectangle_tool.setToolTip(
            tr("Gedrehtes Kartenband anlegen (Mittelpunkt, Größe, Drehwinkel)")
        )

        self.measure_tool = QAction(tr("Koordinaten-Messwerkzeug"), parent)
        self.measure_tool.setIcon(
            icon("measure")
        )
        self.measure_tool.setCheckable(True)
        self.measure_tool.setToolTip(
            tr("Zwei Punkte anklicken, um lat/lon und Distanz anzuzeigen")
        )

        self.exit = QAction(tr("Beenden"), parent)
        self.exit.triggered.connect(parent.close)
