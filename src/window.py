import traceback
from pathlib import Path

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QListWidgetItem,
    QMenu,
    QInputDialog

)

from src.gui.actions import AppActions
from src.gui.toolbar import MainToolbar
from src.gui.rectangle_dialog import RectangleToolDialog
from src.gui.heightmap_dialog import HeightmapDialog
from src.gui.mod_checker_dialog import ModCheckerDialog
from src.gui.overpass_dialog import OverpassQueryDialog
from src.export.osm_xml_exporter import export_osm_xml
from src.gui.short_segment_dialog import ShortSegmentDialog
from src.gui.converter_command_dialog import ConverterCommandDialog
from src.gui.import_guide_dialog import ImportGuideDialog
from src.gui.feature_overview_dialog import FeatureOverviewDialog
from src.gui.preflight_dialog import PreflightCheckDialog
from src.gui.dashboard_dialog import ProjectDashboardDialog
from src.gui.docks import (
    create_project_dock,
    create_properties_dock,
)
from src.gui.layer_dock import create_layer_dock

from src.core.server import LocalServer

from src.map.map_widget import MapWidget
from src.map.map_controller import Tool
from src.undo.rename_marker_command import RenameMarkerCommand
from src.undo.delete_marker_command import DeleteMarkerCommand


class _OsmWorker(QThread):
    """
    Fuehrt MapController.fetch_osm() im Hintergrund aus.

    Darf keine Qt-Objekte (Karte, Widgets) anfassen: das Ergebnis
    geht per Signal zurueck in den GUI-Thread, wo apply_osm() laeuft.
    """

    loaded = Signal(object)   # OSMData
    failed = Signal(str)

    def __init__(self, controller, selection, config, parent=None):
        super().__init__(parent)

        self._controller = controller
        self._selection = selection
        self._config = config

    def run(self):

        print(">>> _OsmWorker.run() gestartet")

        try:

            osm = self._controller.fetch_osm(
                self._selection,
                self._config,
            )

        except Exception as exc:

            traceback.print_exc()

            self.failed.emit(str(exc))

            return

        print(">>> _OsmWorker.run() fertig, sende Ergebnis")

        self.loaded.emit(osm)


class MainWindow(QMainWindow):
    """
    Hauptfenster von TPF3-Map-Studio.
    """

    def __init__(self):
        super().__init__()

        self.resize(1600, 900)

        self._osm_worker = None

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

        self.map_widget = MapWidget(
            base_url=self.server.url
        )

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

        self.tool_status = QLabel("Werkzeug: Marker")

        self.measure_status = QLabel("")

        status.showMessage(
            "Bereit"
        )

        status.addPermanentWidget(
            self.tool_status
        )

        status.addPermanentWidget(
            self.measure_status
        )

        self.setStatusBar(status)

        # ---------------------------------------------------------
        # Projektaktionen
        # ---------------------------------------------------------

        self.actions.save_project.triggered.connect(
            self._save_project
        )

        self.actions.open_project.triggered.connect(
            self._open_project
        )

        self.actions.rectangle_tool.triggered.connect(
            self._open_rectangle_tool
        )

        self.actions.measure_tool.triggered.connect(
            self._toggle_measure_tool
        )

        self.map_widget.controller.measurement_changed.connect(
            self.measure_status.setText
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

        controller.markers_changed.connect(
            self.refresh_project_list
        )

        self.project_list.itemClicked.connect(
            self._project_item_clicked
        )

        self.project_list.itemDoubleClicked.connect(
            self._project_item_double_clicked
        )

        self.project_list.setContextMenuPolicy(
            Qt.CustomContextMenu
        )

        self.project_list.customContextMenuRequested.connect(
            self._project_context_menu
        )

        self.project_list.itemChanged.connect(
            self._project_item_renamed
        )

        controller.show_start_position()

        self.refresh_project_list()

        controller.undo_stack.stack_changed.connect(
            self._update_undo_actions
        )

        self._update_undo_actions()

        self._update_window_title()

    # ---------------------------------------------------------
    # Fenstertitel
    # ---------------------------------------------------------

    def _update_window_title(self):
        """
        Aktualisiert den Fenstertitel.
        """

        project = self.map_widget.controller.project

        title = f"TPF3-Map-Studio - {project.name}"

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

            "TPF3-Map-Studio (*.tpf2ms)"

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

            "TPF3-Map-Studio (*.tpf2ms)"

        )

        if not filename:
            return

        self._load_project_file(filename)

    def _load_project_file(self, filename: str):
        """
        Laedt eine .tpf2ms-Datei in das aktuelle Fenster. Gemeinsam
        genutzt von _open_project() (Datei-Dialog) und dem
        Projekt-Dashboard (Datei bereits bekannt, kein Dialog noetig).
        """

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
    # Projekt-Dashboard
    # ---------------------------------------------------------

    def _open_dashboard(self):
        """
        Oeffnet die Uebersicht aller gespeicherten .tpf2ms-Projekte in
        einem gewaehlten Ordner.
        """

        dialog = ProjectDashboardDialog(self, self)
        dialog.exec()

    # ---------------------------------------------------------
    # Projekteigenschaften
    # ---------------------------------------------------------

    def _edit_project_properties(self):
        """
        Erlaubt das Setzen/Aendern des Projektnamens (z.B. "Rheintal",
        "Nürnberg-Korridor").
        """

        project = self.map_widget.controller.project

        name, ok = QInputDialog.getText(
            self,
            "Projekteigenschaften",
            "Projektname:",
            text=project.name
        )

        if not ok:
            return

        name = name.strip()

        if not name or name == project.name:
            return

        project.name = name

        project.mark_dirty()

        self._update_window_title()

        self.statusBar().showMessage(
            f"Projektname geändert: {name}"
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

        self.dashboard_action = QAction(
            "Projekt-Dashboard...",
            self
        )

        self.dashboard_action.triggered.connect(
            self._open_dashboard
        )

        file_menu.addAction(
            self.dashboard_action
        )

        file_menu.addAction(
            self.actions.save_project
        )

        file_menu.addSeparator()

        self.project_properties_action = QAction(
            "Projekteigenschaften...",
            self
        )

        self.project_properties_action.triggered.connect(
            self._edit_project_properties
        )

        file_menu.addAction(
            self.project_properties_action
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

        marker_action = tools_menu.addAction(
            "Marker"
        )

        selection_action = tools_menu.addAction(
            "Auswahl"
        )

        self.osm_action = tools_menu.addAction(
            "OSM laden"
        )

        overpass_config_action = tools_menu.addAction(
            "Overpass-Abfrage..."
        )

        overpass_config_action.triggered.connect(
            self._open_overpass_dialog
        )

        export_osm_action = tools_menu.addAction(
            "OSM als .osm exportieren..."
        )

        export_osm_action.triggered.connect(
            self._export_osm_xml
        )

        converter_command_action = tools_menu.addAction(
            "Converter-Befehl anzeigen..."
        )

        converter_command_action.triggered.connect(
            self._open_converter_command
        )

        short_segment_action = tools_menu.addAction(
            "Kurze Verbindungssegmente..."
        )

        short_segment_action.triggered.connect(
            self._open_short_segment_dialog
        )

        marker_action.triggered.connect(

            lambda: (
                self.map_widget.controller.set_tool(
                    Tool.MARKER
                ),
                self.tool_status.setText(
                    "Werkzeug: Marker"
                )
            )

        )

        selection_action.triggered.connect(

            lambda: (
                self.map_widget.controller.set_tool(
                    Tool.SELECTION
                ),
                self.tool_status.setText(
                    "Werkzeug: Auswahl"
                )
            )

        )

        self.osm_action.triggered.connect(
            self._download_osm
        )

        rectangle_action = tools_menu.addAction(
            "Rechteck-Tool"
        )

        rectangle_action.triggered.connect(
            self._open_rectangle_tool
        )

        tools_menu.addAction(
            self.actions.measure_tool
        )

        heightmap_action = tools_menu.addAction(
            "Heightmap herunterladen"
        )

        heightmap_action.triggered.connect(
            self._open_heightmap_tool
        )

        mod_checker_action = tools_menu.addAction(
            "Mod-Checker..."
        )

        mod_checker_action.triggered.connect(
            self._open_mod_checker
        )

        preflight_action = tools_menu.addAction(
            "Vorab-Prüfung..."
        )

        preflight_action.triggered.connect(
            self._open_preflight_check
        )

        # ---------------------------------------------------------
        # Hilfe
        # ---------------------------------------------------------

        help_menu = menu.addMenu("Hilfe")

        import_guide_action = help_menu.addAction(
            "Import-Anleitung..."
        )

        import_guide_action.triggered.connect(
            self._open_import_guide
        )

        feature_overview_action = help_menu.addAction(
            "Funktionsübersicht..."
        )

        feature_overview_action.triggered.connect(
            self._open_feature_overview
        )

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
        """
        Startet den OSM-Download in einem Hintergrund-Thread. Das
        Ergebnis wird per Signal im GUI-Thread uebernommen
        (_on_osm_loaded -> controller.apply_osm()).
        """

        print(">>> _download_osm aufgerufen")

        if self._osm_worker is not None and self._osm_worker.isRunning():
            return

        controller = self.map_widget.controller

        selection = controller.project.selection

        if selection is None:

            QMessageBox.warning(
                self,
                "Keine Auswahl",
                "Bitte zuerst mit dem Rechteck-Tool einen "
                "Kartenausschnitt festlegen."
            )

            return

        self.osm_action.setEnabled(False)

        filter_text = (
            "gedrehtes Polygon (poly-Filter)"
            if selection.is_rotated
            else "ungedrehte Box"
        )

        self.statusBar().showMessage(
            f"OSM-Daten werden geladen... "
            f"Drehung {selection.rotation_deg:.2f}°, {filter_text}"
        )

        # Als Attribut speichern, sonst raeumt Python den Thread weg.
        self._osm_worker = _OsmWorker(
            controller,
            selection,
            controller.overpass_config,
            self,
        )

        self._osm_worker.loaded.connect(
            self._on_osm_loaded
        )

        self._osm_worker.failed.connect(
            self._on_osm_failed
        )

        self._osm_worker.finished.connect(
            self._on_osm_worker_finished
        )

        self._osm_worker.start()

    def _on_osm_loaded(self, osm):
        """
        Laeuft im GUI-Thread: Daten ins Projekt uebernehmen und die
        Karte neu zeichnen.
        """

        print(">>> _on_osm_loaded (GUI-Thread)")

        controller = self.map_widget.controller

        controller.apply_osm(osm)

        # Sichtbarkeit aller Layer erneut an die Karte senden. Bisher
        # erschienen die Daten erst, nachdem man die Haken im Layer-Dock
        # aus- und wieder eingeschaltet hat - das macht genau dieser
        # Aufruf jetzt automatisch.
        for layer in controller.layer_manager.layers:
            controller.api.set_layer_visible(
                layer,
                controller.layer_manager.is_visible(layer),
            )

        selection = controller.project.selection

        rotation_text = (
            f", Drehung {selection.rotation_deg:.2f}°"
            if selection is not None
            else ""
        )

        self.statusBar().showMessage(
            f"OSM geladen: "
            f"{osm.node_count} Nodes, "
            f"{osm.way_count} Ways, "
            f"{osm.relation_count} Relations"
            f"{rotation_text}"
        )

        self._update_window_title()

    def _on_osm_failed(self, message: str):

        self.statusBar().showMessage(
            f"OSM-Download fehlgeschlagen: {message}"
            if message else
            "OSM-Download fehlgeschlagen."
        )

    def _on_osm_worker_finished(self):

        self.osm_action.setEnabled(True)

    # ---------------------------------------------------------
    # Overpass-Abfrage-Baukasten
    # ---------------------------------------------------------

    def _open_overpass_dialog(self):
        """
        Oeffnet den Overpass-Abfrage-Baukasten: legt fest, welche
        Kategorien der naechste 'OSM laden'-Aufruf abfragt.
        """

        dialog = OverpassQueryDialog(
            self,
            self.map_widget.controller,
        )

        dialog.exec()

    # ---------------------------------------------------------
    # OSM-XML-Export
    # ---------------------------------------------------------

    def _export_osm_xml(self):
        """
        Exportiert die aktuell geladenen OSM-Daten als Standard-OSM-XML-
        Datei (.osm).
        """

        osm = self.map_widget.controller.project.osm

        if osm.node_count == 0 and osm.way_count == 0:

            QMessageBox.warning(
                self,
                "Keine OSM-Daten",
                "Es sind keine OSM-Daten geladen. Zuerst 'OSM laden' "
                "ausführen (Werkzeuge-Menü)."
            )

            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "OSM-Datei exportieren",
            "map.osm",
            "OSM-Dateien (*.osm)"
        )

        if not filename:
            return

        selection = self.map_widget.controller.project.selection

        bounds = None

        if selection is not None:

            bounds = (
                selection.min_lat,
                selection.min_lon,
                selection.max_lat,
                selection.max_lon,
            )

        try:
            export_osm_xml(
                osm,
                Path(filename),
                bounds=bounds,
            )
        except Exception as exc:

            QMessageBox.critical(
                self,
                "Export fehlgeschlagen",
                str(exc)
            )

            return

        self.statusBar().showMessage(
            f"OSM-Datei exportiert: {filename}"
        )

    # ---------------------------------------------------------
    # Converter-Befehl
    # ---------------------------------------------------------

    def _open_converter_command(self):
        """
        Oeffnet den Dialog, der den fertigen Aufrufbefehl fuer den
        externen OSM-TPF-Converter (main.exe) zusammensetzt.
        """

        dialog = ConverterCommandDialog(
            self,
            self.map_widget.controller,
        )

        dialog.exec()

    # ---------------------------------------------------------
    # Kurze Verbindungssegmente
    # ---------------------------------------------------------

    def _open_short_segment_dialog(self):
        """
        Oeffnet die Analyse/Vereinfachung fuer sehr kurze _link-Segmente.
        """

        dialog = ShortSegmentDialog(
            self,
            self.map_widget.controller,
        )

        dialog.exec()

    # ---------------------------------------------------------
    # Import-Anleitung
    # ---------------------------------------------------------

    def _open_import_guide(self):

        dialog = ImportGuideDialog(self)

        dialog.exec()

    # ---------------------------------------------------------
    # Funktionsübersicht
    # ---------------------------------------------------------

    def _open_feature_overview(self):

        dialog = FeatureOverviewDialog(self)

        dialog.exec()

    # ---------------------------------------------------------
    # Rechteck-Tool
    # ---------------------------------------------------------

    def _rectangle_center_from_marker(self, has_selection: bool):
        """
        Liefert (lat, lon) eines Markers als Vorbelegung fuer das
        Rechteck-Tool, oder None.

        - Ist ein Marker ausgewaehlt, gilt seine Position immer.
        - Sonst, wenn es noch keine Auswahl gibt, der zuletzt
          gesetzte Marker.
        - Sonst None (bestehende Auswahl bleibt unveraendert).
        """

        controller = self.map_widget.controller

        markers = controller.project.markers

        if not markers:
            return None

        selected_id = controller.selected_marker

        if selected_id:

            for marker in markers:

                if marker.id == selected_id:
                    return (marker.lat, marker.lon)

        if not has_selection:

            last = markers[-1]

            return (last.lat, last.lon)

        return None

    def _open_rectangle_tool(self):
        """
        Oeffnet den Dialog fuer das Rechteck-Tool und legt bei OK das
        eingegebene (ggf. gedrehte) Kartenband als aktuelle Auswahl an.
        Der Mittelpunkt wird aus einem Marker vorbelegt (siehe
        _rectangle_center_from_marker()).
        """

        selection = self.map_widget.controller.project.selection

        dialog = RectangleToolDialog(
            self,
            initial_center=self._rectangle_center_from_marker(
                selection is not None
            ),
            initial_selection=selection,
        )

        if dialog.exec() != RectangleToolDialog.Accepted:
            return

        values = dialog.values()

        self.map_widget.controller.set_rotated_selection(
            **values
        )

        self.statusBar().showMessage(
            f"Kartenband gesetzt: "
            f"{values['width_m']/1000:.3f} x {values['height_m']/1000:.3f} km, "
            f"Drehung {values['rotation_deg']:.2f}°"
        )

    # ---------------------------------------------------------
    # Koordinaten-Messwerkzeug
    # ---------------------------------------------------------

    def _toggle_measure_tool(self):

        self.map_widget.controller.set_tool(
            Tool.MEASURE
        )

        self.tool_status.setText(
            "Werkzeug: Koordinaten-Messwerkzeug"
        )

        self.measure_status.setText(
            "Messung: ersten Punkt anklicken"
        )

    # ---------------------------------------------------------
    # Heightmap
    # ---------------------------------------------------------

    def _open_heightmap_tool(self):
        """
        Oeffnet den Heightmap-Dialog fuer die aktuelle Selection.
        """

        selection = self.map_widget.controller.project.selection

        if selection is None:
            QMessageBox.warning(
                self,
                "Keine Auswahl",
                "Bitte zuerst mit dem Rechteck-Tool einen "
                "Kartenausschnitt festlegen."
            )
            return

        dialog = HeightmapDialog(
            self,
            selection,
            self.map_widget.controller.project,
            osm=self.map_widget.controller.project.osm,
        )
        dialog.exec()

    # ---------------------------------------------------------
    # Mod-Checker
    # ---------------------------------------------------------

    def _open_mod_checker(self):

        dialog = ModCheckerDialog(self)
        dialog.exec()

    # ---------------------------------------------------------
    # Vorab-Prüfung
    # ---------------------------------------------------------

    def _open_preflight_check(self):

        dialog = PreflightCheckDialog(
            self,
            self.map_widget.controller,
        )

        dialog.exec()

    # ---------------------------------------------------------
    # Docks
    # ---------------------------------------------------------

    def _build_docks(self):

        self.project_dock = create_project_dock(self)
        self.layer_dock = create_layer_dock(self)
        self.properties_dock = create_properties_dock(self)

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            self.project_dock
        )

        self.addDockWidget(
            Qt.LeftDockWidgetArea,
            self.layer_dock
        )

        self.addDockWidget(
            Qt.RightDockWidgetArea,
            self.properties_dock
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

    def _undo(self):

        self.map_widget.controller.undo()

    def _redo(self):

        self.map_widget.controller.redo()

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

        print(f"Marker ausgewählt: {marker_id}")

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

        self.prop_id.setText(
            marker.id
        )

        self.prop_name.setText(
            marker.text
        )

        self.prop_lat.setText(
            f"{marker.lat:.6f}"
        )

        self.prop_lon.setText(
            f"{marker.lon:.6f}"
        )

        for i in range(self.project_list.count()):

            item = self.project_list.item(i)

            if item.data(Qt.UserRole) == marker.id:

                self.project_list.setCurrentItem(item)

                break

    def refresh_project_list(self):

        self.project_list.clear()

        controller = self.map_widget.controller

        for marker in controller.project.markers:

            item = QListWidgetItem(
                marker.text or marker.id
            )

            item.setFlags(
                item.flags() | Qt.ItemIsEditable
            )

            item.setData(
                Qt.UserRole,
                marker.id
            )

            self.project_list.addItem(
                item
            )

    def _project_item_clicked(
            self,
            item
    ):

        marker_id = item.data(
            Qt.UserRole
        )

        self.map_widget.controller.marker_clicked(
            marker_id
        )

    def _project_item_double_clicked(
            self,
            item
    ):

        marker_id = item.data(
            Qt.UserRole
        )

        controller = self.map_widget.controller

        marker = next(
            (
                m
                for m in controller.project.markers
                if m.id == marker_id
            ),
            None
        )

        if marker is None:
            return

        controller.api.center(
            marker.lat,
            marker.lon
        )

        controller.marker_clicked(
            marker.id
        )

    def _project_context_menu(
            self,
            pos
    ):

        item = self.project_list.itemAt(pos)

        if item is None:
            return

        menu = QMenu(self)

        center_action = menu.addAction(
            "📍 Auf Marker zentrieren"
        )

        rename_action = menu.addAction(
            "✏️ Umbenennen"
        )

        delete_action = menu.addAction(
            "🗑️ Löschen"
        )

        action = menu.exec(
            self.project_list.mapToGlobal(pos)
        )

        if action == center_action:

            self._project_item_double_clicked(
                item
            )

        elif action == rename_action:

            self.project_list.editItem(
                item
            )

        elif action == delete_action:

            marker_id = item.data(
                Qt.UserRole
            )

            self.prop_id.setText(
                marker_id
            )

            self._delete_marker()

    def _project_item_renamed(
            self,
            item
    ):

        marker_id = item.data(
            Qt.UserRole
        )

        controller = self.map_widget.controller

        marker = next(
            (
                m
                for m in controller.project.markers
                if m.id == marker_id
            ),
            None
        )

        if marker is None:
            return

        if marker.text == item.text():
            return

        controller.undo_stack.push(
            RenameMarkerCommand(
                controller,
                marker.id,
                marker.text,
                item.text()
            )
        )

    def _marker_name_changed(self):

        controller = self.map_widget.controller

        marker = next(
            (
               m
               for m in controller.project.markers
               if m.id == self.prop_id.text()
            ),
            None
        )

        if marker is None:
            return

        controller.undo_stack.push(
            RenameMarkerCommand(
                controller,
                marker.id,
                marker.text,
                self.prop_name.text()
            )
        )

    def _delete_marker(self):

        controller = self.map_widget.controller

        marker = next(
            (

                m
                for m in controller.project.markers
                if m.id == self.prop_id.text()
            ),
            None
        )

        if marker is None:
            return

        controller.undo_stack.push(
            DeleteMarkerCommand(
                controller,
                marker
            )
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

        # Laufenden OSM-Download nicht mitten im Thread abschiessen
        if self._osm_worker is not None and self._osm_worker.isRunning():
            self._osm_worker.wait(5000)

        try:
            self.server.stop()
        except Exception:
            pass

        event.accept()
