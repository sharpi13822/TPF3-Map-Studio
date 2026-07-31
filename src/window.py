from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QMessageBox,
    QStatusBar,
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

        self.resize(1600, 900)

        # ---------------------------------------------------------
        # Aktionen
        # ---------------------------------------------------------

        self.actions = AppActions(self)

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

        self.setStatusBar(status)

        # ---------------------------------------------------------
        # Undo / Redo Shortcuts
        # ---------------------------------------------------------

        QShortcut(
            QKeySequence.Undo,
            self
        ).activated.connect(
            self.map_widget.controller.undo
        )

        QShortcut(
            QKeySequence.Redo,
            self
        ).activated.connect(
            self.map_widget.controller.redo
        )

        # ---------------------------------------------------------
        # Projektaktionen
        # ---------------------------------------------------------

        self.actions.save_project.triggered.connect(
            self._save_project
        )

        self.actions.open_project.triggered.connect(
            self._open_project
        )

        # ---------------------------------------------------------
        # Fenstertitel
        # ---------------------------------------------------------

        self._update_window_title()

            # ---------------------------------------------------------
    # Karte geladen
    # ---------------------------------------------------------

    def _on_map_loaded(
        self,
        ok: bool
    ):

        if not ok:

            QMessageBox.critical(
                self,
                "Fehler",
                "Die Karte konnte nicht geladen werden."
            )

            return

        print("Karte geladen")

        controller = self.map_widget.controller

        controller.marker_selected.connect(
            self._marker_selected
        )

        controller.show_start_position()

        controller.undo_stack.stack_changed.connect(
            self._update_undo_actions
        )

        self._update_undo_actions()

        controller.marker_selected.connect(
        self._marker_selected
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

        title = f"TPF2 Map Studio - {project.name}"

        if project.dirty:
            title += " *"

        self.setWindowTitle(title)

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

                f"Projekt konnte nicht gespeichert werden.\n\n{e}"

            )

            return

        self.statusBar().showMessage(
            "Projekt gespeichert."
        )

        self._update_window_title()

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

                f"Projekt konnte nicht geladen werden.\n\n{e}"

            )

            return

        self.statusBar().showMessage(
            "Projekt geladen."
        )

        self._update_window_title()

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

        self.undo_action = QAction(
            "Rückgängig",
            self
        )

        self.undo_action.setShortcut(
            QKeySequence.Undo
        )

        self.undo_action.triggered.connect(
            self.map_widget.controller.undo
        )

        self.redo_action = QAction(
            "Wiederholen",
            self
        )

        self.redo_action.setShortcut(
            QKeySequence.Redo
        )

        self.redo_action.triggered.connect(
            self.map_widget.controller.redo
        )

        edit_menu.addAction(
            self.undo_action
        )

        edit_menu.addAction(
            self.redo_action
        )

        self.actions.undo.triggered.connect(
            self._undo
        )

        self.actions.redo.triggered.connect(
            self._redo
        )

        self.actions.undo.setEnabled(False)
        self.actions.redo.setEnabled(False)

        # ---------------------------------------------------------
        # Ansicht
        # ---------------------------------------------------------

        view_menu = menu.addMenu("Ansicht")

        view_menu.addAction(
            "Projekt"
        )

        view_menu.addAction(
            "Layer"
        )

        view_menu.addAction(
            "Eigenschaften"
        )

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
    # Docks
    # ---------------------------------------------------------

    def _build_docks(self):

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            create_project_dock(self)
        )

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            create_layer_dock(self)
        )

        self.addDockWidget(
            Qt.RightDockWidgetArea,
            create_properties_dock(self)
        )

    # ---------------------------------------------------------
    # Undo / Redo
    # ---------------------------------------------------------

    def _update_undo_actions(self):

        controller = self.map_widget.controller

        self.undo_action.setEnabled(
            controller.can_undo
        )

        self.redo_action.setEnabled(
            controller.can_redo
        )


         # ---------------------------------------------------------
    # Marker ausgewählt
    # ---------------------------------------------------------

    def _marker_selected(
        self,
        marker_id: str
    ):
        """
        Aktualisiert die Statusleiste nach Auswahl eines Markers.
        """

        project = self.map_widget.controller.project

        marker = next(
            (
                m
                for m in project.markers
                if m.id == marker_id
            ),
            None
        )

        if marker is None:
            return

        self.statusBar().showMessage(
            f"Marker: {marker.id} | "
            f"{marker.lat:.6f}, "
            f"{marker.lon:.6f}"
        )   

    # ---------------------------------------------------------
    # Fenster schließen
    # ---------------------------------------------------------

    def closeEvent(
        self,
        event
    ):
        """
        Vor dem Beenden nachfragen, falls Änderungen
        noch nicht gespeichert wurden.
        """

        project = self.map_widget.controller.project

        if project.dirty:

            result = QMessageBox.question(

                self,

                "Projekt speichern",

                "Das Projekt wurde geändert.\n\n"
                "Vor dem Beenden speichern?",

                QMessageBox.Yes
                | QMessageBox.No
                | QMessageBox.Cancel,

                QMessageBox.Yes

            )

            if result == QMessageBox.Cancel:

                event.ignore()
                return

            if result == QMessageBox.Yes:

                self._save_project()

                if project.dirty:
                    event.ignore()
                    return

        try:
            self.server.stop()
        except Exception:
            pass

        event.accept()