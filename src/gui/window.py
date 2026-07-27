from PySide6.QtCore import Qt
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

        self.actions.open_project.triggered.connect(
            self._open_project
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

        self._build_menu()
        self._build_toolbar()
        self._build_docks()

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

        self._update_window_title()

        controller.undo_stack.stack_changed.connect(
            self._update_undo_actions
        )

    # ---------------------------------------------------------
    # Undo / Redo
    # ---------------------------------------------------------

    def _update_undo_actions(self):

        controller = self.map_widget.controller

        if hasattr(self, "undo_action"):

            self.undo_action.setEnabled(
                controller.can_undo
            )

        if hasattr(self, "redo_action"):

            self.redo_action.setEnabled(
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

        file_menu.addSeparator()

        file_menu.addAction(
            self.actions.exit
        )

        # ---------------------------------------------------------
        # Bearbeiten
        # ---------------------------------------------------------

        edit_menu = menu.addMenu("Bearbeiten")

        if hasattr(self, "undo_action"):
            edit_menu.addAction(
                self.undo_action
            )

        if hasattr(self, "redo_action"):
            edit_menu.addAction(
                self.redo_action
            )

        # ---------------------------------------------------------
        # Ansicht
        # ---------------------------------------------------------

        menu.addMenu("Ansicht")

        # ---------------------------------------------------------
        # Werkzeuge
        # ---------------------------------------------------------

        tools_menu = menu.addMenu("Werkzeuge")

        marker_action = tools_menu.addAction(
            "Marker"
        )

        selection_action = tools_menu.addAction(
            "Auswahl"
        )

        osm_action = tools_menu.addAction(
            "OSM laden"
        )

        marker_action.triggered.connect(
            lambda: self.map_widget.controller.set_tool(
                Tool.MARKER
            )
        )

        selection_action.triggered.connect(
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
        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            create_project_dock(self)
        )

        # Layer
        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            create_layer_dock(self)
        )

        # Eigenschaften
        self.addDockWidget(
            Qt.RightDockWidgetArea,
            create_properties_dock(self)
        )

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