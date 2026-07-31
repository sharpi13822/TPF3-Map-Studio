from PySide6.QtCore import Qt
from PySide6.QtGui import QActionGroup

from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QFileDialog,
    QMessageBox
)

from src.gui.actions import AppActions
from src.gui.toolbar import MainToolbar
from src.gui.docks import (
    create_project_dock,
    create_properties_dock,
)
from src.gui.layer_dock import create_layer_dock

from src.core.server import LocalServer

from src.map.map_widget import MapWidget
from src.map.map_controller import Tool


class MainWindow(QMainWindow):
    """
    Hauptfenster von TPF2 Map Studio.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("TPF2 Map Studio")
        self.resize(1600, 900)

        # ---------------------------------------------------------
        # Aktionen
        # ---------------------------------------------------------

        self.actions = AppActions(self)

        self.actions.save_project.triggered.connect(
            self._save_project
        )

        self.actions.save_project_as.triggered.connect(
            self._save_project_as
        )

        self.actions.open_project.triggered.connect(
            self._open_project
        )

        self.actions.close_project.triggered.connect(
            self._close_project
        )

        self.actions.new_project.triggered.connect(
            self._new_project
        )

        # ---------------------------------------------------------
        # HTTP-Server
        # ---------------------------------------------------------

        self.server = LocalServer()
        self.server.start()

        # ---------------------------------------------------------
        # Kartenansicht
        # ---------------------------------------------------------

        self.map_widget = MapWidget()

        self.setCentralWidget(
            self.map_widget
        )

        self.map_widget.map_loaded.connect(
            self._on_map_loaded
        )

        # ---------------------------------------------------------
        # Oberfläche
        # ---------------------------------------------------------

        self._build_docks()
        self._build_menu()
        self._build_toolbar()

        # ---------------------------------------------------------
        # Statusleiste
        # ---------------------------------------------------------

        status = QStatusBar()

        status.showMessage(
            "Bereit"
        )

        self.setStatusBar(
            status
        )

            # ---------------------------------------------------------
    # Karte geladen
    # ---------------------------------------------------------

    def _on_map_loaded(
        self,
        ok: bool
    ):

        if not ok:

            print(
                "Fehler beim Laden der Karte"
            )

            return

        print(
            "Karte geladen"
        )

        controller = self.map_widget.controller

        controller.show_start_position()

        controller.set_tool( Tool.MARKER)

        self._update_window_title()

        controller.undo_stack.stack_changed.connect(
            self._update_undo_actions
        )

    # ---------------------------------------------------------
    # Undo / Redo
    # ---------------------------------------------------------

    def _update_undo_actions(self):

        controller = self.map_widget.controller

        self.actions.undo.setEnabled(
            controller.can_undo
        )

        self.actions.redo.setEnabled(
            controller.can_redo
        )

    # ---------------------------------------------------------
    # OSM herunterladen
    # ---------------------------------------------------------

    def _download_osm(self):

        self.statusBar().showMessage(
            "OSM-Daten werden geladen..."
        )

        ok = self.map_widget.controller.download_osm()

        if ok:

            project = self.map_widget.controller.project

            self.statusBar().showMessage(

                f"OSM geladen: "

                f"{project.node_count} Nodes, "

                f"{project.way_count} Ways, "

                f"{project.relation_count} Relations"

            )

        else:

            self.statusBar().showMessage(
                "OSM-Download fehlgeschlagen."
            )

    # ---------------------------------------------------------
    # Projekt speichern
    # ---------------------------------------------------------

    def _save_project(self):

        filename, _ = QFileDialog.getSaveFileName(

            self,

            "Projekt speichern",

            "",

            "TPF2 Map Studio (*.tpf2ms)"

        )

        if not filename:
            return

        try:
            self.map_widget.controller.save_project(
                filename
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Projekt konnte nicht gespeichert werden: {e}"
            )

            self._update_window_title()

            return
        
        self.statusBar().showMessage(
            "Projekt gespeichert."
        )

    # ---------------------------------------------------------
    # Projekt speichern unter
    # ---------------------------------------------------------

    def _save_project_as(self):

        self._save_project()

    # ---------------------------------------------------------
    # Projekt laden
    # ---------------------------------------------------------

    def _open_project(self):

        filename, _ = QFileDialog.getOpenFileName(

            self,

            "Projekt öffnen",

            "",

            "TPF2 Map Studio (*.tpf2ms)"

        )

        if not filename:
            return

        try:

            self.map_widget.controller.load_project(
                filename
            )

        except Exception as e:
            QMessageBox.critical(
                self,
                "Fehler",
                f"Projekt konnte nicht geladen werden: {e}"
            )
            return
        

        self.statusBar().showMessage(
            "Projekt geladen."
        )

        self._update_window_title()

    # ---------------------------------------------------------
    # Fenstertitel
    # ---------------------------------------------------------

    def _update_window_title(self):
        """
        Aktualisiert den Fenstertitel.
        """

        project = self.map_widget.controller.project

        self.setWindowTitle(
            f"TPF2 Map Studio - {project.name}"
        )   

    # ---------------------------------------------------------
    # Menü
    # ---------------------------------------------------------

    def _build_menu(self):

        menu = self.menuBar()

        # ---------------------------------------------------------
        # Datei
        # ---------------------------------------------------------

        file_menu = menu.addMenu("Datei")

        file_menu.addAction(
            self.actions.new_project
        )

        file_menu.addAction(
            self.actions.open_project
        )

        file_menu.addAction(
            self.actions.save_project
        )

        file_menu.addAction(
            self.actions.save_project_as
        )

        file_menu.addAction(
            self.actions.close_project
        )

        file_menu.addSeparator()

        file_menu.addAction(
            self.actions.exit
        )

        # ---------------------------------------------------------
        # Bearbeiten
        # ---------------------------------------------------------

        edit_menu = menu.addMenu("Bearbeiten")

        edit_menu.addAction(
            self.actions.undo
        )

        edit_menu.addAction(
            self.actions.redo
        )

        # ---------------------------------------------------------
        # Ansicht
        # ---------------------------------------------------------

        view_menu = menu.addMenu("Ansicht")

        view_menu.addAction(
            self.project_dock.toggleViewAction()
        )

        view_menu.addAction(
            self.layer_dock.toggleViewAction()
        )

        view_menu.addAction(
            self.properties_dock.toggleViewAction()
        )

        # ---------------------------------------------------------
        # Werkzeuge
        # ---------------------------------------------------------

        tools_menu = menu.addMenu("Werkzeuge")

        tool_group = QActionGroup(self)

        tool_group.setExclusive(True)

        tool_group.addAction( self.actions.marker_tool)

        tool_group.addAction(self.actions.selection_tool)

        self.actions.marker_tool.setChecked(True)

        tools_menu.addAction(
            self.actions.marker_tool
        )

        tools_menu.addAction(
            self.actions.selection_tool
        )

        osm_action = tools_menu.addAction(
            "OSM laden"
        )

        self.actions.marker_tool.triggered.connect(
            lambda: self.map_widget.controller.set_tool(
                Tool.MARKER
            )
        )

        self.actions.selection_tool.triggered.connect(
            lambda: self.map_widget.controller.set_tool(
                Tool.SELECTION
            )
        )

        osm_action.triggered.connect(
            self._download_osm
        )

        # ---------------------------------------------------------
        # Hilfe
        # ---------------------------------------------------------

        menu.addMenu("Hilfe")

    # ---------------------------------------------------------
    # Toolbar
    # ---------------------------------------------------------

    def _build_toolbar(self):

        self.addToolBar(
            MainToolbar(
                self.actions
            )
        )

    # ---------------------------------------------------------
    # Docks
    # ---------------------------------------------------------

    def _build_docks(self):
        """
        Erstellt alle Dockfenster.
        """

        # Projekt

        self.project_dock = create_project_dock(self)

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            self.project_dock
        )

        # Layer

        self.layer_dock = create_layer_dock(self)

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            self.layer_dock
        )

        # Eigenschaften

        self.properties_dock = create_properties_dock(self)

        self.addDockWidget(
            Qt.RightDockWidgetArea,
           self.properties_dock
        )

    # ---------------------------------------------------------
    # Rückgängig
    # ---------------------------------------------------------

    def _undo(self):

        self.map_widget.controller.undo()

    # ---------------------------------------------------------
    # Wiederholen
    # ---------------------------------------------------------

    def _redo(self):

        self.map_widget.controller.redo()


    # ---------------------------------------------------------
    # Projekt zurücksetzen
    # ---------------------------------------------------------

    def _reset_project(self):

        controller = self.map_widget.controller

        controller.clear_markers()

        controller.api.clear_rectangle()

        project = controller.project

        project.name = "Neues Projekt"

        self._update_window_title()

    # ---------------------------------------------------------
    # Neues Projekt
    # ---------------------------------------------------------

    def _new_project(self):

        self._reset_project()

        self.show_status("Neues Projekt erstellt.")
 
    # ---------------------------------------------------------
    # Projekt schließen
    # ---------------------------------------------------------

    def _close_project(self):

        self._reset_project()

        self.show_status( "Projekt geschlossen.")


    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    def show_status(
        self,
        text: str
    ):
        """
        Text in der Statusleiste anzeigen.
        """

        self.statusBar().showMessage(text)

    # ---------------------------------------------------------
    # Fenster schließen
    # ---------------------------------------------------------

    def closeEvent(
        self,
        event
    ):
        """
        Anwendung schließen.
        """

        try:
            self.server.stop()
        except Exception:
            pass

        super().closeEvent(event)