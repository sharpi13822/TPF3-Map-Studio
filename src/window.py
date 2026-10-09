import json
import traceback
from pathlib import Path

from PySide6.QtCore import Qt, QThread, QSize, QTimer, Signal
from PySide6.QtGui import QAction, QActionGroup, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStatusBar,
    QListWidgetItem,
    QMenu,
    QInputDialog,
    QToolBar,
    QVBoxLayout,
    QWidget,

)

from src.features import VACUUMTUBE_IMPORTER
from src.i18n import get_language, save_language, tr
from src.core.project.project import Project
from src.map.layer import Layer
from src.undo.undo_stack import UndoStack
from src.heightmap.station_markers import station_marker_data
from src.heightmap.station_export import collect_stations
from src.gui.actions import AppActions
from src.gui.icon_set import icon, icon_name_for
from src.gui.theme import apply_theme
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


LAYER_HELP_HTML = """
<p><b>So funktioniert das Layer-Panel</b></p>

<p><b>Haken:</b> blendet die Ebene auf der Karte ein oder aus.
Beim Start sind alle Ebenen aus. Erst <i>Werkzeuge &rarr; OSM
laden</i>, dann die gewünschten Haken setzen. Die Ebene
<i>Bahnhöfe</i> schaltet das Studio nach dem Laden selbst ein.</p>

<p><b>Schloss:</b> sperrt die Ebene. Ihre Objekte lassen sich in der
Karte dann nicht mehr anklicken oder bearbeiten, so greifst du nicht
versehentlich daneben.</p>

<p><b>Balken:</b> stellt die Deckkraft der Ebene ein. Nach links
ziehen macht sie durchsichtiger, ganz rechts ist sie voll
sichtbar. So siehst du Ebenen, die darunter liegen.</p>

<p><b>Pfeile:</b> verschieben die Ebene in der Stapelreihenfolge
auf der Karte. Pfeil hoch legt sie vor die anderen Ebenen, Pfeil
runter dahinter. Praktisch, wenn zum Beispiel Wald die Straßen
verdeckt.</p>

<p><b>Rechtsklick</b> auf eine Zeile: Ebene anzeigen, ausblenden,
sperren, entsperren oder die Deckkraft zurücksetzen.</p>

<p><b>Tipp:</b> Ein Klick auf ein Objekt auf der Karte zeigt seine
Eckpunkte. Die Punkte lassen sich ziehen. Ein Klick ins Leere oder
die Esc-Taste beendet das.</p>
"""


# Sprachauswahl im Menue: (Kuerzel, Anzeigename). Die Namen werden nie
# uebersetzt, jede Sprache steht in ihrer eigenen Schreibweise.
LANGUAGE_CHOICES = (
    ("de", "Deutsch"),
    ("en", "English"),
)


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

    # Pfad der aktuell geoeffneten oder zuletzt gespeicherten Projektdatei
    # (None = noch nicht gespeichert). "Speichern" schreibt dorthin.
    _project_file = None

    def __init__(self):
        super().__init__()

        # Farben und Stil fuer das ganze Studio (src/gui/theme.py); die Symbole folgen, sobald das Fenster steht.
        apply_theme(QApplication.instance())
        QTimer.singleShot(0, self._apply_action_icons)

        self.resize(1600, 900)

        self._osm_worker = None

        self.layer_panel = None

        # ---------------------------------------------------------
        # Aktionen
        # ---------------------------------------------------------

        self.actions = AppActions(self)

        self._setup_tool_actions()

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

        # Alle Datenebenen starten ausgeblendet. Muss vor dem Anlegen der
        # Docks passieren, damit die Haken im Layer-Dock leer starten.
        layer_manager = self.map_widget.controller.layer_manager

        for layer in layer_manager.layers:
            layer_manager.set_visible(layer, False)

        self._hook_layer_controls()

        self._build_docks()
        self._build_menu()
        self._build_toolbar()

        # ---------------------------------------------------------
        # Statusleiste
        # ---------------------------------------------------------

        status = QStatusBar()

        self.tool_status = QLabel(tr("Werkzeug: Marker"))

        self.measure_status = QLabel("")

        status.showMessage(
            tr("Bereit")
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

        self.actions.new_project.triggered.connect(
            self._new_project
        )

        self.actions.save_project_as.triggered.connect(
            self._save_project_as
        )

        self.actions.close_project.triggered.connect(
            self._close_project
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
                tr("Fehler"),
                tr("Die Karte konnte nicht geladen werden.")
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

        # Startansicht: Deutschland, ohne vorgesetzten Marker.
        controller.api.center_and_zoom(51.1657, 10.4515, 6)

        # Startzustand der Ebenen (ausgeblendet) an die Karte melden.
        self._sync_layers_to_map()

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
        """
        Speichert in die aktuelle Projektdatei. Gibt es noch keine,
        fragt der Dialog wie bei "Speichern unter..." nach dem Namen.
        """

        if self._project_file:

            self._save_project_to(self._project_file)

            return

        self._save_project_as()

    def _save_project_as(self):
        """
        Fragt immer nach dem Dateinamen.
        """

        filename, _ = QFileDialog.getSaveFileName(

            self,

            tr("Projekt speichern unter"),

            self._project_file or "",

            "TPF3-Map-Studio (*.tpf2ms)"

        )

        if not filename:
            return

        self._save_project_to(filename)

    def _save_project_to(self, filename: str):

        try:

            self.map_widget.controller.save_project(
                filename
            )

        except Exception as e:

            QMessageBox.critical(

                self,

                tr("Fehler"),

                tr("Projekt konnte nicht gespeichert werden.\n\n{error}").format(error=e)

            )

            return

        self._project_file = filename

        self.statusBar().showMessage(
            tr("Projekt gespeichert.")
        )

        self._update_window_title()

    # ---------------------------------------------------------
    # Projekt laden
    # ---------------------------------------------------------

    def _open_project(self):

        filename, _ = QFileDialog.getOpenFileName(

            self,

            tr("Projekt öffnen"),

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

                tr("Fehler"),

                tr("Projekt konnte nicht geladen werden.\n\n{error}").format(error=e)

            )

            return

        # Layer-Dock und Karte auf den geladenen Ebenenzustand bringen.
        if self.layer_panel is not None:
            self.layer_panel.sync_from_state()

        self._sync_layers_to_map()

        self._project_file = filename

        self.statusBar().showMessage(
            tr("Projekt geladen.")
        )

        self._update_window_title()

    # ---------------------------------------------------------
    # Neues Projekt / Projekt schliessen
    # ---------------------------------------------------------

    def _confirm_discard_changes(self) -> bool:
        """
        Fragt bei ungespeicherten Aenderungen nach. True = weitermachen.
        """

        project = self.map_widget.controller.project

        if not project.dirty:
            return True

        result = QMessageBox.question(

            self,

            tr("Projekt speichern"),

            tr("Das Projekt wurde geändert.\n\n"
            "Vorher speichern?"),

            QMessageBox.Yes
            | QMessageBox.No
            | QMessageBox.Cancel,

            QMessageBox.Yes

        )

        if result == QMessageBox.Cancel:
            return False

        if result == QMessageBox.Yes:

            self._save_project()

            if project.dirty:
                return False

        return True

    def _new_project(self):
        """
        Beginnt ein neues, leeres Projekt (fragt vorher nach dem Speichern).
        """

        if self._osm_worker is not None and self._osm_worker.isRunning():

            QMessageBox.information(
                self,
                tr("OSM-Download läuft"),
                tr("Bitte warten, bis der OSM-Download fertig ist.")
            )

            return

        if not self._confirm_discard_changes():
            return

        self._reset_project()

        self.statusBar().showMessage(
            tr("Neues Projekt.")
        )

    def _close_project(self):
        """
        Schliesst das aktuelle Projekt. Das Studio hat nur ein Fenster,
        danach ist ein leeres Projekt geoeffnet (wie bei "Neu").
        """

        self._new_project()

    def _reset_project(self):
        """
        Setzt Projekt, Karte, Ebenen und Rueckgaengig-Liste auf einen
        leeren Zustand zurueck.
        """

        controller = self.map_widget.controller

        controller.project = Project()

        controller.selected_marker = None

        controller._next_marker_id = 1

        controller.undo_stack = UndoStack()

        controller.undo_stack.stack_changed.connect(
            self._update_undo_actions
        )

        controller.set_tool(Tool.MARKER)

        self.actions.marker_tool.setChecked(True)

        # Ebenen wieder wie beim Start: ausgeblendet, entsperrt, voll sichtbar.
        for layer in Layer:

            controller.layer_manager.set_visible(layer, False)
            controller.layer_manager.set_locked(layer, False)
            controller.layer_manager.set_opacity(layer, 1.0)

        # Alles von der Karte nehmen (OSM-Ebenen, eigene Objekte, Marker,
        # Rechteck, Messlinie, Bahnhoefe).
        self._run_js(
            "["
            "'clearMarkers','clearPolylines','clearRectangle','clearMeasureLine',"
            "'clearStations','clearRoads','clearRailways','clearBuildings',"
            "'clearWater','clearWaterways','clearParks','clearLanduse',"
            "'clearVegetation'"
            "].forEach(name => { try { window.MapApi[name](); } "
            "catch (error) { console.warn(name, error); } });"
        )

        if self.layer_panel is not None:
            self.layer_panel.sync_from_state()

        self._sync_layers_to_map()

        self.refresh_project_list()

        self._update_undo_actions()

        self._project_file = None

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
            tr("Projekteigenschaften"),
            tr("Projektname:"),
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
            tr("Projektname geändert: {name}").format(name=name)
        )

    # ---------------------------------------------------------
    # Menü
    # ---------------------------------------------------------

    def _build_menu(self):

        menu = self.menuBar()

        # ---------------------------------------------------------
        # Datei
        # ---------------------------------------------------------

        file_menu = menu.addMenu(tr("Datei"))

        file_menu.addAction(
            self.actions.new_project
        )

        file_menu.addAction(
            self.actions.open_project
        )

        self.dashboard_action = QAction(
            tr("Projekt-Dashboard..."),
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

        file_menu.addAction(
            self.actions.save_project_as
        )

        file_menu.addAction(
            self.actions.close_project
        )

        file_menu.addSeparator()

        self.project_properties_action = QAction(
            tr("Projekteigenschaften..."),
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

        edit_menu = menu.addMenu(tr("Bearbeiten"))

        self.undo_action = QAction(
            tr("Rückgängig"),
            self
        )

        self.undo_action.setShortcut(
            QKeySequence.Undo
        )

        self.undo_action.triggered.connect(
            self.map_widget.controller.undo
        )

        self.redo_action = QAction(
            tr("Wiederholen"),
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

        view_menu = menu.addMenu(tr("Ansicht"))

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

        tools_menu = menu.addMenu(tr("Werkzeuge"))

        tools_menu.addAction(
            self.actions.marker_tool
        )

        tools_menu.addAction(
            self.actions.selection_tool
        )

        self.osm_action = tools_menu.addAction(
            tr("OSM laden")
        )

        overpass_config_action = tools_menu.addAction(
            tr("Overpass-Abfrage...")
        )

        overpass_config_action.triggered.connect(
            self._open_overpass_dialog
        )

        if VACUUMTUBE_IMPORTER:
            export_osm_action = tools_menu.addAction(
                tr("OSM als .osm exportieren...")
            )

            export_osm_action.triggered.connect(
                self._export_osm_xml
            )

        if VACUUMTUBE_IMPORTER:
            converter_command_action = tools_menu.addAction(
                tr("Converter-Befehl anzeigen...")
            )

            converter_command_action.triggered.connect(
                self._open_converter_command
            )

        if VACUUMTUBE_IMPORTER:
            short_segment_action = tools_menu.addAction(
                tr("Kurze Verbindungssegmente...")
            )

            short_segment_action.triggered.connect(
                self._open_short_segment_dialog
            )

        self.osm_action.triggered.connect(
            self._download_osm
        )

        rectangle_action = tools_menu.addAction(
            tr("Rechteck-Tool")
        )

        rectangle_action.triggered.connect(
            self._open_rectangle_tool
        )

        tools_menu.addAction(
            self.actions.measure_tool
        )

        heightmap_action = tools_menu.addAction(
            tr("Heightmap herunterladen")
        )

        heightmap_action.triggered.connect(
            self._open_heightmap_tool
        )

        if VACUUMTUBE_IMPORTER:
            mod_checker_action = tools_menu.addAction(
                tr("Mod-Checker...")
            )

            mod_checker_action.triggered.connect(
                self._open_mod_checker
            )

        preflight_action = tools_menu.addAction(
            tr("Vorab-Prüfung...")
        )

        preflight_action.triggered.connect(
            self._open_preflight_check
        )

        # ---------------------------------------------------------
        # Hilfe
        # ---------------------------------------------------------

        help_menu = menu.addMenu(tr("Hilfe"))

        # Die Import-Anleitung beschreibt den Importer von VacuumTube (src/features.py).
        if VACUUMTUBE_IMPORTER:
            import_guide_action = help_menu.addAction(
                tr("Import-Anleitung...")
            )

            import_guide_action.triggered.connect(
                self._open_import_guide
            )

        feature_overview_action = help_menu.addAction(
            tr("Funktionsübersicht...")
        )

        feature_overview_action.triggered.connect(
            self._open_feature_overview
        )

        # ---------------------------------------------------------
        # Sprache / Language
        # ---------------------------------------------------------

        # Der Menuename bleibt in beiden Sprachen gleich, damit man ihn
        # auch dann findet, wenn man die aktuelle Sprache nicht versteht.
        language_menu = menu.addMenu("Sprache / Language")

        self._language_group = QActionGroup(self)

        self._language_group.setExclusive(True)

        for code, name in LANGUAGE_CHOICES:

            language_action = QAction(name, self)

            language_action.setCheckable(True)

            language_action.setChecked(code == get_language())

            language_action.setData(code)

            self._language_group.addAction(language_action)

            language_menu.addAction(language_action)

        self._language_group.triggered.connect(
            self._language_chosen
        )

    # ---------------------------------------------------------
    # Sprache
    # ---------------------------------------------------------

    def _language_chosen(self, action):
        """
        Speichert die gewaehlte Sprache. Sie gilt ab dem naechsten Start;
        die Hinweise stehen bewusst in beiden Sprachen.
        """

        code = action.data()

        saved = save_language(code)

        if not saved:

            QMessageBox.warning(
                self,
                "Sprache / Language",
                "Die Sprachwahl konnte nicht gespeichert werden.\n\n"
                "The language setting could not be saved."
            )

            return

        if code == get_language():
            return

        QMessageBox.information(
            self,
            "Sprache / Language",
            "Die Sprache wird nach einem Neustart des Studios "
            "umgestellt.\n\n"
            "The language will change after you restart the Studio."
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
                tr("Keine Auswahl"),
                tr("Bitte zuerst mit dem Rechteck-Tool einen "
                "Kartenausschnitt festlegen.")
            )

            return

        self.osm_action.setEnabled(False)

        filter_text = (
            tr("gedrehtes Polygon (poly-Filter)")
            if selection.is_rotated
            else tr("ungedrehte Box")
        )

        self.statusBar().showMessage(
            tr(
                "OSM-Daten werden geladen... "
                "Drehung {deg:.2f}°, {filter}"
            ).format(deg=selection.rotation_deg, filter=filter_text)
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

        selection = controller.project.selection

        rotation_text = (
            tr(", Drehung {deg:.2f}°").format(deg=selection.rotation_deg)
            if selection is not None
            else ""
        )

        self.statusBar().showMessage(
            tr(
                "OSM geladen: {nodes} Nodes, {ways} Ways, "
                "{relations} Relations{rotation}"
            ).format(
                nodes=osm.node_count,
                ways=osm.way_count,
                relations=osm.relation_count,
                rotation=rotation_text,
            )
        )

        self._update_window_title()

        self._auto_show_stations(osm)

    def _auto_show_stations(self, osm):
        """
        Sammelt nach dem OSM-Laden die Bahnhoefe und zeigt sie auf der Karte
        (Ebene "Bahnhoefe"). Ein Fehler hier darf das Laden nie stoeren.
        """

        try:

            selection = self.map_widget.controller.project.selection

            if selection is None:
                return

            data = collect_stations(osm, selection)

            if not data["stations"]:
                return

            self.show_stations_on_map(data, announce=False)

            self.statusBar().showMessage(
                tr("{message}, {count} Bahnhöfe").format(
                    message=self.statusBar().currentMessage(),
                    count=len(data['stations']),
                )
            )

        except Exception as error:  # noqa: BLE001

            print(f"Bahnhöfe konnten nicht gesammelt werden: {error}")

    def _on_osm_failed(self, message: str):

        self.statusBar().showMessage(
            tr("OSM-Download fehlgeschlagen: {message}").format(message=message)
            if message else
            tr("OSM-Download fehlgeschlagen.")
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
                tr("Keine OSM-Daten"),
                tr("Es sind keine OSM-Daten geladen. Zuerst 'OSM laden' "
                "ausführen (Werkzeuge-Menü).")
            )

            return

        filename, _ = QFileDialog.getSaveFileName(
            self,
            tr("OSM-Datei exportieren"),
            "map.osm",
            tr("OSM-Dateien (*.osm)")
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
                tr("Export fehlgeschlagen"),
                str(exc)
            )

            return

        self.statusBar().showMessage(
            tr("OSM-Datei exportiert: {filename}").format(filename=filename)
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
            tr(
                "Kartenband gesetzt: {width:.3f} x {height:.3f} km, "
                "Drehung {deg:.2f}°"
            ).format(
                width=values['width_m'] / 1000,
                height=values['height_m'] / 1000,
                deg=values['rotation_deg'],
            )
        )

    # ---------------------------------------------------------
    # Koordinaten-Messwerkzeug
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # Layer-Dock: Deckkraft und Reihenfolge an die Karte melden
    # ---------------------------------------------------------

    @staticmethod
    def _js_layer_name(layer) -> str:
        """Name der Ebene in map.js (ROADS -> 'roads')."""

        return layer.name.lower()

    def _run_js(self, code: str):

        self.map_widget.page().runJavaScript(code)

    def show_stations_on_map(self, data, announce=True):
        """
        Zeigt die Bahnhoefe aus dem Bahnhofsexport als Marker mit Namen auf
        der Karte (Ebene "Bahnhoefe") und schaltet die Ebene sichtbar.
        """

        items = station_marker_data(data)

        self._run_js(
            f"window.MapApi.showStations({json.dumps(items)});"
        )

        controller = self.map_widget.controller

        controller.set_layer_visible(Layer.STATIONS, True)

        controller.layer_state_changed.emit()

        if announce:

            self.statusBar().showMessage(
                tr("{count} Bahnhöfe auf der Karte (Ebene Bahnhöfe)").format(
                    count=len(items)
                )
            )

    def _send_layer_opacity(self, layer):

        opacity = self.map_widget.controller.layer_manager.opacity(layer)

        self._run_js(
            f"window.MapApi.setLayerOpacity("
            f"{json.dumps(self._js_layer_name(layer))}, {opacity});"
        )

    def _send_layer_locked(self, layer):

        locked = self.map_widget.controller.layer_manager.is_locked(layer)

        self._run_js(
            f"window.MapApi.setLayerLocked("
            f"{json.dumps(self._js_layer_name(layer))}, "
            f"{json.dumps(bool(locked))});"
        )

    def _sync_layers_to_map(self):
        """
        Schickt Sichtbarkeit, Deckkraft und Reihenfolge aller Ebenen aus
        dem LayerManager an die Karte (beim Start und nach dem Laden
        eines Projekts).
        """

        controller = self.map_widget.controller

        manager = controller.layer_manager

        for layer in manager.layers:

            controller.api.set_layer_visible(
                layer,
                manager.is_visible(layer),
            )

            self._send_layer_opacity(layer)

            self._send_layer_locked(layer)

        self._send_layer_order()

    def _send_layer_order(self):

        names = [
            self._js_layer_name(layer)
            for layer in self.map_widget.controller.layer_manager.layers
        ]

        self._run_js(
            f"window.MapApi.setLayerOrder({json.dumps(names)});"
        )

    def _hook_layer_controls(self):
        """
        Der Controller aendert bei Deckkraft und Reihenfolge nur seinen
        eigenen Zustand. Diese Huelle meldet die Aenderung zusaetzlich
        an die Karte. Muss vor dem Anlegen der Docks laufen, damit deren
        Regler die umhuellten Methoden bekommen.
        """

        controller = self.map_widget.controller

        set_opacity = controller.set_layer_opacity
        move_up = controller.move_layer_up
        move_down = controller.move_layer_down
        set_locked = controller.set_layer_locked

        def set_layer_locked(layer, locked):
            set_locked(layer, locked)
            self._send_layer_locked(layer)

        def set_layer_opacity(layer, opacity):
            set_opacity(layer, opacity)
            self._send_layer_opacity(layer)

        def move_layer_up(layer):
            move_up(layer)
            self._send_layer_order()

        def move_layer_down(layer):
            move_down(layer)
            self._send_layer_order()

        controller.set_layer_locked = set_layer_locked
        controller.set_layer_opacity = set_layer_opacity
        controller.move_layer_up = move_layer_up
        controller.move_layer_down = move_layer_down

    def _setup_tool_actions(self):
        """
        Marker-, Auswahl- und Messwerkzeug bilden eine Gruppe: immer genau
        eines ist aktiv (Haken in Werkzeugleiste und Menue synchron).
        Menue und Werkzeugleiste teilen sich dieselben Aktionen.
        """

        self.tool_group = QActionGroup(self)
        self.tool_group.setExclusive(True)

        self.tool_group.addAction(self.actions.marker_tool)
        self.tool_group.addAction(self.actions.selection_tool)
        self.tool_group.addAction(self.actions.measure_tool)

        self.actions.marker_tool.setChecked(True)

        self.actions.marker_tool.triggered.connect(
            lambda: self._set_tool(Tool.MARKER)
        )

        self.actions.selection_tool.triggered.connect(
            lambda: self._set_tool(Tool.SELECTION)
        )

    def _apply_action_icons(self):
        """Setzt die Symbole aus src/gui/icons an Menues und Werkzeugleiste. Ein Fehler hier stoert den Start nicht."""

        try:
            for attribute, name in (
                ("marker_tool", "marker"),
                ("selection_tool", "auswahl"),
                ("measure_tool", "messen"),
            ):
                action = getattr(self.actions, attribute, None)

                if action is not None:
                    action.setIcon(icon(name, checkable=True))

            for action in self.findChildren(QAction):
                name = icon_name_for(action.text(), action.toolTip())

                if name:
                    action.setIcon(icon(name, checkable=action.isCheckable()))

            for toolbar in self.findChildren(QToolBar):
                toolbar.setIconSize(QSize(22, 22))

        except Exception as error:  # noqa: BLE001
            print(f"Symbole konnten nicht gesetzt werden: {error}")

    def _set_tool(self, tool):

        self.map_widget.controller.set_tool(tool)

        names = {
            Tool.MARKER: tr("Marker"),
            Tool.SELECTION: tr("Auswahl"),
            Tool.MEASURE: tr("Koordinaten-Messwerkzeug"),
        }

        self.tool_status.setText(
            tr("Werkzeug: {name}").format(
                name=names.get(tool, tool.value)
            )
        )

    def _toggle_measure_tool(self):

        self.map_widget.controller.set_tool(
            Tool.MEASURE
        )

        self.tool_status.setText(
            tr("Werkzeug: Koordinaten-Messwerkzeug")
        )

        self.measure_status.setText(
            tr("Messung: ersten Punkt anklicken")
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
                tr("Keine Auswahl"),
                tr("Bitte zuerst mit dem Rechteck-Tool einen "
                "Kartenausschnitt festlegen.")
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

        self._add_layer_help()

    def _add_layer_help(self):
        """
        Haengt unter die Ebenenliste im Layer-Dock einen Hilfetext, der
        Haken, Balken und Pfeile erklaert. Das bestehende Dock-Widget
        bleibt unveraendert und wird nur in einen Container gesetzt.
        """

        original = self.layer_dock.widget()

        if original is None:
            return

        self.layer_panel = original

        self.map_widget.controller.layer_state_changed.connect(
            self.layer_panel.sync_from_state
        )

        container = QWidget()

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)

        # Erst den Container einsetzen (das alte Widget wird dabei
        # ausgeblendet), dann das alte Widget hineinsetzen.
        self.layer_dock.setWidget(container)

        layout.addWidget(original)
        original.show()

        help_label = QLabel(tr(LAYER_HELP_HTML))
        help_label.setTextFormat(Qt.RichText)
        help_label.setWordWrap(True)
        help_label.setMargin(8)
        help_label.setAlignment(Qt.AlignTop | Qt.AlignLeft)

        layout.addWidget(help_label)
        layout.addStretch(1)

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
            tr("Marker: {id} | {lat:.6f}, {lon:.6f}").format(
                id=marker.id,
                lat=marker.lat,
                lon=marker.lon,
            )
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
            icon("mitte"),
            tr("Auf Marker zentrieren")
        )

        rename_action = menu.addAction(
            icon("zeichnen"),
            tr("Umbenennen")
        )

        delete_action = menu.addAction(
            icon("loeschen"),
            tr("Löschen")
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

                tr("Projekt speichern"),

                tr("Das Projekt wurde geändert.\n\n"
                "Vor dem Beenden speichern?"),

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
