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
    QPushButton,
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
from src.gui.cache_dialog import CacheDialog
from src.gui.osm_download_status import (
    COLOR_ERROR,
    COLOR_WARN,
    OsmDownloadStatus,
    format_download_event,
)
from src.core.update_check import (
    decide_action,
    default_settings_path,
    load_settings,
    save_settings,
)
from src.gui.update_worker import UpdateBridge, start_update_check
from src.http_identity import APP_VERSION, USER_AGENT
from src.core.recipe import (
    RECIPE_SUFFIX,
    RecipeError,
    build_recipe,
    project_file_from_recipe,
    read_recipe,
    safe_file_stem,
    write_recipe,
)
from src.gui.mod_checker_dialog import ModCheckerDialog
from src.gui.overpass_dialog import OverpassQueryDialog
from src.osm.overpass_client import OverpassCancelled  # noqa: F401
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
    cancelled = Signal()
    progress = Signal(int, int)
    retry_status = Signal(int, int, int)
    lane_status = Signal(int, int, str, int, int)
    download_status = Signal(object)
    cache_status = Signal(object)
    phase = Signal(str)

    def __init__(self, controller, selection, config, parent=None):
        super().__init__(parent)

        self._cancelled = False

        client = getattr(controller, "overpass", None)

        if client is not None and hasattr(client, "reset_cancel"):
            client.reset_cancel()

        self._controller = controller
        self._selection = selection
        self._config = config

        if client is not None and hasattr(client, "on_progress"):
            client.on_progress = lambda n, total: self.progress.emit(n, total)
        if client is not None and hasattr(client, "on_retry"):
            client.on_retry = lambda tile, attempt, seconds: self.retry_status.emit(tile, attempt, seconds)
        if client is not None and hasattr(client, "on_lane"):
            client.on_lane = lambda lane, tile, state, attempt, seconds: self.lane_status.emit(lane, tile, state, attempt, seconds)

        if client is not None and hasattr(client, "on_status"):
            client.on_status = self.download_status.emit
        if client is not None and hasattr(client, "on_cache_status"):
            client.on_cache_status = self.cache_status.emit

        if hasattr(controller, "on_phase"):
            controller.on_phase = self.phase.emit

    def cancel(self):
        """Bricht den Download ab (vom GUI-Thread aufgerufen)."""

        self._cancelled = True

        client = getattr(self._controller, "overpass", None)

        if client is not None and hasattr(client, "cancel"):
            client.cancel()

    def run(self):

        print(">>> _OsmWorker.run() gestartet")

        try:

            osm = self._controller.fetch_osm(
                self._selection,
                self._config,
            )

        except Exception as exc:

            if self._cancelled or isinstance(exc, OverpassCancelled):

                self.cancelled.emit()

                return

            traceback.print_exc()

            self.failed.emit(str(exc))

            return

        if self._cancelled:

            self.cancelled.emit()

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
        self._build_sidebar_toggle()
        self._build_properties_toggle()

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

        self.osm_cancel_button = QPushButton(tr("OSM-Laden abbrechen"))

        self.osm_cancel_button.setVisible(False)

        self.osm_cancel_button.clicked.connect(
            self._cancel_osm
        )

        status.addPermanentWidget(
            self.osm_cancel_button
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

        self.map_widget.controller.layers_limited.connect(
            self._on_layers_limited
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

    def _on_layers_limited(self, text):
        self.statusBar().showMessage(
            tr("Sehr viele Objekte: Die Karte zeigt je Ebene nur die wichtigsten (bei Fluessen und Strassen die groessten zuerst): {text}. Export und Berechnung nutzen weiterhin alle Daten. Fuer die volle Anzeige ein kleineres Rechteck waehlen.").format(text=text),
            20000,
        )

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

    # ---------------------------------------------------------
    # Kartenrezept (Gebiet + Export-Einstellungen als kleine Datei)
    # ---------------------------------------------------------

    def _export_recipe(self):

        project = self.map_widget.controller.project

        if project.selection is None:
            QMessageBox.warning(
                self,
                tr("Keine Auswahl"),
                tr("Bitte zuerst mit dem Rechteck-Tool einen "
                "Kartenausschnitt festlegen.")
            )
            return

        if not project.export_settings:
            answer = QMessageBox.question(
                self,
                tr("Kartenrezept exportieren"),
                tr("Es sind noch keine Export-Einstellungen gespeichert "
                "(Heightmap-Dialog \u00f6ffnen, H\u00f6hendaten laden und den "
                "Dialog schlie\u00dfen).\n\nTrotzdem nur das Gebiet exportieren?"),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if answer != QMessageBox.Yes:
                return

        default_name = safe_file_stem(project.name) + RECIPE_SUFFIX

        filename, _ = QFileDialog.getSaveFileName(
            self,
            tr("Kartenrezept exportieren"),
            default_name,
            tr("Kartenrezept (*.tpf3recipe)")
        )

        if not filename:
            return

        if not filename.lower().endswith(RECIPE_SUFFIX):
            filename += RECIPE_SUFFIX

        try:
            data = build_recipe(
                project.name,
                project.description,
                project.selection,
                project.export_settings,
            )
            write_recipe(filename, data)
        except Exception as exc:
            QMessageBox.critical(
                self,
                tr("Fehler"),
                tr("Kartenrezept konnte nicht gespeichert werden.\n\n{error}").format(error=exc)
            )
            return

        self.statusBar().showMessage(
            tr("Kartenrezept gespeichert.")
        )

    def _import_recipe(self):

        if self._osm_worker is not None and self._osm_worker.isRunning():
            QMessageBox.information(
                self,
                tr("OSM-Download l\u00e4uft"),
                tr("Bitte warten, bis der OSM-Download fertig ist.")
            )
            return

        filename, _ = QFileDialog.getOpenFileName(
            self,
            tr("Kartenrezept importieren"),
            "",
            tr("Kartenrezept (*.tpf3recipe)")
        )

        if not filename:
            return

        try:
            recipe = read_recipe(filename)
        except RecipeError as exc:
            QMessageBox.critical(self, tr("Fehler"), str(exc))
            return

        # Das Rezept ersetzt das aktuelle Projekt (auch OSM-Daten und Marker).
        if not self._confirm_discard_changes():
            return

        import os
        import tempfile

        with tempfile.TemporaryDirectory() as folder:

            path = os.path.join(folder, "kartenrezept.tpf2ms")

            try:
                project_file_from_recipe(recipe, path)
            except RecipeError as exc:
                QMessageBox.critical(self, tr("Fehler"), str(exc))
                return

            self._load_project_file(path)

        # Kein Dateibezug: "Speichern" fragt nach einem Namen und
        # ueberschreibt kein altes Projekt.
        self._project_file = None

        self.map_widget.controller.project.mark_dirty()

        self._update_window_title()

        self.statusBar().showMessage(
            tr("Kartenrezept importiert.")
        )

    # ---------------------------------------------------------
    # Fehlerbericht und Log-Ordner (Hilfe-Menue)
    # ---------------------------------------------------------

    def _create_bug_report(self):

        import logging
        from pathlib import Path

        from PySide6.QtCore import QStandardPaths

        from src.core.bug_report import create_report, default_report_name
        from src.http_identity import APP_VERSION
        from src.i18n import get_language
        from src.logging_config import LOG_FILE

        # Erst alles in die Logdatei schreiben lassen, dann einpacken.
        for handler in logging.getLogger().handlers:
            try:
                handler.flush()
            except Exception:
                pass

        try:
            import PySide6
            pyside_version = PySide6.__version__
        except Exception:
            pyside_version = "?"

        documents = QStandardPaths.writableLocation(
            QStandardPaths.DocumentsLocation
        )

        name = default_report_name()

        default_path = str(Path(documents) / name) if documents else name

        filename, _ = QFileDialog.getSaveFileName(
            self,
            tr("Fehlerbericht speichern"),
            default_path,
            tr("ZIP-Datei (*.zip)")
        )

        if not filename:
            return

        if not filename.lower().endswith(".zip"):
            filename += ".zip"

        project = self.map_widget.controller.project

        extras = {
            "has_selection": project.has_selection,
            "osm_nodes": project.node_count,
            "osm_ways": project.way_count,
        }

        try:
            create_report(
                filename,
                LOG_FILE,
                APP_VERSION,
                get_language(),
                pyside_version=pyside_version,
                extras=extras,
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                tr("Fehler"),
                tr("Fehlerbericht konnte nicht erstellt werden.\n\n{error}").format(error=exc)
            )
            return

        QMessageBox.information(
            self,
            tr("Fehlerbericht gespeichert"),
            tr("Der Fehlerbericht wurde gespeichert:\n\n{path}\n\n"
            "Benutzername, Windows-Pfade, Steam-ID und E-Mail-Adressen "
            "wurden entfernt. Das Log kann Koordinaten des bearbeiteten "
            "Gebiets enthalten. Bitte die Datei an die Fehlermeldung "
            "(GitHub-Issue oder Forenbeitrag) anh\u00e4ngen.").format(path=filename)
        )

        self.statusBar().showMessage(
            tr("Fehlerbericht gespeichert.")
        )

    def _open_log_folder(self):

        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        from src.logging_config import LOG_DIR

        try:
            LOG_DIR.mkdir(parents=True, exist_ok=True)
        except OSError:
            pass

        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(LOG_DIR))):
            QMessageBox.warning(
                self,
                tr("Fehler"),
                tr("Log-Ordner konnte nicht ge\u00f6ffnet werden:\n{path}").format(path=LOG_DIR)
            )

    # ---------------------------------------------------------
    # Update-Hinweis (Hilfe-Menue)
    # ---------------------------------------------------------

    def _check_for_updates_manual(self, *_):

        self._check_for_updates(manual=True)

    def _startup_update_check(self):

        settings = getattr(self, "_update_settings", None) or {}

        if settings.get("auto_check"):
            self._check_for_updates(manual=False)

    def _check_for_updates(self, manual: bool):

        if getattr(self, "_update_running", False):
            return

        self._update_running = True
        self._update_manual = manual

        # Die Signale kommen aus einem Hintergrund-Thread. Verbunden wird
        # mit Methoden dieses Fensters (nicht mit Lambdas), damit Qt sie
        # sicher im GUI-Thread ausfuehrt.
        bridge = UpdateBridge(self)
        bridge.result.connect(self._on_update_result)
        bridge.failed.connect(self._on_update_failed)
        self._update_bridge = bridge

        if manual:
            self.statusBar().showMessage(
                tr("Suche nach Updates...")
            )

        start_update_check(bridge, USER_AGENT)

    def _on_update_result(self, info):

        manual = getattr(self, "_update_manual", False)

        self._update_running = False

        self.statusBar().clearMessage()

        settings = getattr(self, "_update_settings", None) or {}

        action = decide_action(
            APP_VERSION,
            info.version,
            settings.get("skipped_version", ""),
            manual,
        )

        if action == "update":
            self._show_update_dialog(info)

        elif manual:
            QMessageBox.information(
                self,
                tr("Keine neuere Version"),
                tr("Es ist die neueste Version installiert ({version}).").format(version=APP_VERSION)
            )

    def _on_update_failed(self, message):

        manual = getattr(self, "_update_manual", False)

        self._update_running = False

        self.statusBar().clearMessage()

        if manual:
            QMessageBox.warning(
                self,
                tr("Update-Pr\u00fcfung fehlgeschlagen"),
                tr("Die Update-Pr\u00fcfung ist fehlgeschlagen.\n\n{error}").format(error=message)
            )
        else:
            print("Update-Pruefung fehlgeschlagen:", message)

    def _show_update_dialog(self, info):

        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices

        box = QMessageBox(self)

        box.setIcon(QMessageBox.Information)

        box.setWindowTitle(tr("Update verf\u00fcgbar"))

        box.setText(
            tr("Es gibt eine neuere Version des TPF3-Map-Studios.\n\n"
            "Installiert: {current}\nNeueste: {latest}").format(
                current=APP_VERSION,
                latest=info.version,
            )
        )

        open_button = box.addButton(
            tr("Download-Seite \u00f6ffnen"), QMessageBox.AcceptRole
        )

        skip_button = box.addButton(
            tr("Diese Version \u00fcberspringen"), QMessageBox.DestructiveRole
        )

        box.addButton(tr("Sp\u00e4ter"), QMessageBox.RejectRole)

        box.setDefaultButton(open_button)

        box.exec()

        clicked = box.clickedButton()

        if clicked is open_button:

            if not QDesktopServices.openUrl(QUrl(info.url)):
                QMessageBox.warning(
                    self,
                    tr("Fehler"),
                    tr("Download-Seite konnte nicht ge\u00f6ffnet werden:\n{url}").format(url=info.url)
                )

        elif clicked is skip_button:

            self._update_settings["skipped_version"] = info.version

            self._save_update_settings()

    def _auto_update_toggled(self, checked):

        self._update_settings["auto_check"] = bool(checked)

        self._save_update_settings()

    def _save_update_settings(self):

        try:
            save_settings(default_settings_path(), self._update_settings)
        except OSError as exc:
            print("Update-Einstellungen nicht gespeichert:", exc)

    # ---------------------------------------------------------
    # Cache verwalten (Hilfe-Menue)
    # ---------------------------------------------------------

    def _open_tpf2_import(self, *_):
        """Werkzeuge -> TPF2-Karte übernehmen (Szenario A, v0.6.0)."""
        from src.gui.tpf2_import_dialog import Tpf2ImportDialog

        Tpf2ImportDialog(self).exec()

    def _open_cache_dialog(self, *_):

        dialog = CacheDialog(self)

        dialog.exec()

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

        self.recipe_export_action = QAction(
            tr("Kartenrezept exportieren..."),
            self
        )

        self.recipe_export_action.setToolTip(
            tr("Gebiet und Export-Einstellungen als kleine Datei zum Teilen speichern")
        )

        self.recipe_export_action.triggered.connect(
            self._export_recipe
        )

        file_menu.addAction(
            self.recipe_export_action
        )

        self.recipe_import_action = QAction(
            tr("Kartenrezept importieren..."),
            self
        )

        self.recipe_import_action.setToolTip(
            tr("Gebiet und Export-Einstellungen aus einer Rezeptdatei laden "
            "(ersetzt das aktuelle Projekt)")
        )

        self.recipe_import_action.triggered.connect(
            self._import_recipe
        )

        file_menu.addAction(
            self.recipe_import_action
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
        self.view_menu = view_menu

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

        self.osm_cancel_action = tools_menu.addAction(
            tr("OSM-Laden abbrechen")
        )

        self.osm_cancel_action.setEnabled(False)

        self.osm_cancel_action.triggered.connect(
            self._cancel_osm
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

        tpf2_import_action = tools_menu.addAction(
            tr("TPF2-Karte übernehmen...")
        )

        tpf2_import_action.triggered.connect(
            self._open_tpf2_import
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

        help_center_action = help_menu.addAction(tr("Anleitungen..."))

        help_center_action.triggered.connect(self._open_help_center)

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

        help_menu.addSeparator()

        bug_report_action = help_menu.addAction(
            tr("Fehlerbericht erstellen...")
        )

        bug_report_action.setToolTip(
            tr("Log sowie Versions- und Systemangaben als ZIP f\u00fcr eine "
            "Fehlermeldung speichern (Namen und Pfade werden entfernt)")
        )

        bug_report_action.triggered.connect(
            self._create_bug_report
        )

        log_folder_action = help_menu.addAction(
            tr("Log-Ordner \u00f6ffnen")
        )

        log_folder_action.triggered.connect(
            self._open_log_folder
        )

        cache_action = help_menu.addAction(
            tr("Cache verwalten...")
        )

        cache_action.setToolTip(
            tr("Heruntergeladene H\u00f6hendaten ansehen und Speicherplatz freigeben")
        )

        cache_action.triggered.connect(
            self._open_cache_dialog
        )

        help_menu.addSeparator()

        update_check_action = help_menu.addAction(
            tr("Nach Updates suchen...")
        )

        update_check_action.triggered.connect(
            self._check_for_updates_manual
        )

        self._update_settings = load_settings(default_settings_path())

        auto_update_action = help_menu.addAction(
            tr("Beim Start automatisch nach Updates suchen")
        )

        auto_update_action.setCheckable(True)

        auto_update_action.setChecked(
            self._update_settings["auto_check"]
        )

        auto_update_action.setToolTip(
            tr("Fragt beim Start einmal bei GitHub nach der neuesten Version "
            "(dabei sieht GitHub die IP-Adresse und die Versionsnummer des "
            "Studios). Standardm\u00e4\u00dfig aus.")
        )

        auto_update_action.toggled.connect(
            self._auto_update_toggled
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

    def _build_sidebar_toggle(self):
        """
        Schmale Leiste am linken Rand mit einem Pfeil: klappt Projekt- und
        Layer-Dock nach links weg und wieder heraus. Die Karte bekommt
        dann die ganze Breite.
        """

        self._sidebar_docks = (self.project_dock, self.layer_dock)
        self._sidebar_was_open = []

        bar = QToolBar(tr("Seitenleiste"), self)
        bar.setObjectName("SidebarToggleBar")
        bar.setMovable(False)
        bar.setFloatable(False)
        bar.setAllowedAreas(Qt.LeftToolBarArea)
        bar.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.sidebar_action = QAction(self)
        self.sidebar_action.setCheckable(True)
        self.sidebar_action.setChecked(True)
        self.sidebar_action.setShortcut(QKeySequence("Ctrl+B"))
        self.sidebar_action.setToolTip(
            tr("Seitenleiste (Projekt und Layer) ein- oder ausklappen (Strg+B)")
        )
        self.sidebar_action.toggled.connect(self._set_sidebar_open)

        bar.addAction(self.sidebar_action)

        button = bar.widgetForAction(self.sidebar_action)
        button.setArrowType(Qt.LeftArrow)

        self._sidebar_button = button

        self.addToolBar(Qt.LeftToolBarArea, bar)

        self.view_menu.addSeparator()
        self.view_menu.addAction(self.sidebar_action)

    def _build_properties_toggle(self):
        """
        Schmale Leiste am rechten Rand: klappt das Eigenschaften-Dock nach
        rechts weg und wieder heraus (Strg+Umschalt+B).
        """

        self._properties_was_open = False

        bar = QToolBar(tr("Eigenschaften-Leiste"), self)
        bar.setObjectName("PropertiesToggleBar")
        bar.setMovable(False)
        bar.setFloatable(False)
        bar.setAllowedAreas(Qt.RightToolBarArea)
        bar.setToolButtonStyle(Qt.ToolButtonIconOnly)

        self.properties_action = QAction(self)
        self.properties_action.setCheckable(True)
        self.properties_action.setChecked(True)
        self.properties_action.setShortcut(QKeySequence("Ctrl+Shift+B"))
        self.properties_action.setToolTip(
            tr("Eigenschaften-Panel ein- oder ausklappen (Strg+Umschalt+B)")
        )
        self.properties_action.toggled.connect(self._set_properties_open)

        bar.addAction(self.properties_action)

        button = bar.widgetForAction(self.properties_action)
        button.setArrowType(Qt.RightArrow)

        self._properties_button = button

        self.addToolBar(Qt.RightToolBarArea, bar)

        self.view_menu.addAction(self.properties_action)

    def _set_properties_open(self, open_):
        """Zeigt oder versteckt das rechte Eigenschaften-Dock."""

        if open_:
            if self._properties_was_open:
                self.properties_dock.show()
            self._properties_was_open = False
        else:
            self._properties_was_open = self.properties_dock.isVisible()
            self.properties_dock.hide()

        self._properties_button.setArrowType(
            Qt.RightArrow if open_ else Qt.LeftArrow
        )

        self.properties_action.setText(
            tr("Eigenschaften einklappen") if open_ else tr("Eigenschaften ausklappen")
        )

    def _set_sidebar_open(self, open_):
        """Zeigt oder versteckt die linken Docks und merkt sich, welche offen waren."""

        if open_:
            for dock in self._sidebar_was_open:
                dock.show()
            self._sidebar_was_open = []
        else:
            self._sidebar_was_open = [
                dock for dock in self._sidebar_docks if dock.isVisible()
            ]
            for dock in self._sidebar_docks:
                dock.hide()

        self._sidebar_button.setArrowType(
            Qt.LeftArrow if open_ else Qt.RightArrow
        )

        self.sidebar_action.setText(
            tr("Seitenleiste einklappen") if open_ else tr("Seitenleiste ausklappen")
        )

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

        self._set_osm_running(True)

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

        self._osm_worker.cancelled.connect(
            self._on_osm_cancelled
        )

        self._osm_completed = 0
        self._osm_total = 0
        self._osm_lanes = {}
        self._osm_events = {}
        if not hasattr(self, "_osm_download_panel"):
            self._osm_download_panel = OsmDownloadStatus(self)
            self.addDockWidget(Qt.BottomDockWidgetArea, self._osm_download_panel)
            self.view_menu.addAction(self._osm_download_panel.toggleViewAction())
        self._osm_download_panel.start()
        self._osm_worker.download_status.connect(self._on_osm_download_status)
        self._osm_worker.cache_status.connect(self._on_osm_cache_status)
        self._osm_worker.lane_status.connect(self._on_osm_lane)
        self._osm_worker.phase.connect(self._on_osm_phase)

        self._osm_worker.progress.connect(
            self._on_osm_progress
        )

        self._osm_worker.finished.connect(
            self._on_osm_worker_finished
        )

        self._osm_worker.start()

    def _on_osm_loaded(self, osm):
        if hasattr(self, "_osm_download_panel"):
            self._osm_download_panel.finish(tr("Alle OSM-Kacheln geladen."))

        """
        Laeuft im GUI-Thread: Daten ins Projekt uebernehmen und die
        Karte neu zeichnen.
        """

        print(">>> _on_osm_loaded (GUI-Thread)")

        controller = self.map_widget.controller

        self._on_osm_phase(tr("Karte wird gezeichnet…"))
        QApplication.processEvents()

        controller.apply_osm(osm)

        if hasattr(self, "_osm_download_panel"):
            self._osm_download_panel.finish(tr("Karte fertig."))

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

    def _on_osm_phase(self, text: str):
        if hasattr(self, "_osm_download_panel"):
            self._osm_download_panel.set_phase(text)
        self.statusBar().showMessage(text)

    def _on_osm_progress(self, number: int, total: int):
        self._osm_completed = number
        self._osm_total = total
        if hasattr(self, "_osm_download_panel"):
            self._osm_download_panel.set_progress(number, total)
        self._show_osm_lanes()

    def _on_osm_lane(self, lane, tile, state, attempt, seconds):
        self._osm_lanes[lane] = (tile, state, seconds)
        self._show_osm_lanes()

    def _on_osm_cache_status(self, status):
        self._osm_download_panel.set_cache_status(status)

    def _on_osm_download_status(self, event):
        self._osm_events[event["lane"]] = event
        self._osm_download_panel.update_event(event)
        self._show_osm_lanes()

    def _show_osm_lanes(self):
        parts = []
        for lane, (tile, state, seconds) in sorted(self._osm_lanes.items()):
            event = getattr(self, "_osm_events", {}).get(lane)
            if event is not None:
                parts.append(format_download_event(event))
            elif state == "waiting":
                parts.append(tr("Spur {lane}: Kachel {tile}, nächster Versuch in {seconds} s").format(lane=lane, tile=tile, seconds=seconds))
            elif state == "loading":
                parts.append(tr("Spur {lane}: Kachel {tile} lädt").format(lane=lane, tile=tile))
            else:
                parts.append(tr("Spur {lane}: bereit").format(lane=lane))
        progress = tr("OSM: {done} von {total} Kacheln fertig").format(done=self._osm_completed, total=self._osm_total)
        self.statusBar().showMessage(progress + (" | " + " | ".join(parts) if parts else ""))

    def _on_osm_failed(self, message: str):
        if hasattr(self, "_osm_download_panel"):
            self._osm_download_panel.finish(tr("Download fehlgeschlagen: {error}").format(error=message), COLOR_ERROR)


        self.statusBar().showMessage(
            tr("OSM-Download fehlgeschlagen: {message}").format(message=message)
            if message else
            tr("OSM-Download fehlgeschlagen.")
        )

    def _set_osm_running(self, running: bool):
        """Schaltet Menue und Abbruch-Knopf je nach laufendem Download."""

        self.osm_action.setEnabled(not running)

        self.osm_cancel_action.setEnabled(running)

        self.osm_cancel_button.setEnabled(True)

        self.osm_cancel_button.setVisible(running)

    def _cancel_osm(self):

        worker = self._osm_worker

        if worker is None or not worker.isRunning():
            return

        worker.cancel()

        self.osm_cancel_action.setEnabled(False)

        self.osm_cancel_button.setEnabled(False)

        self.statusBar().showMessage(
            tr("OSM-Download wird abgebrochen...")
        )

    def _on_osm_cancelled(self):
        if hasattr(self, "_osm_download_panel"):
            self._osm_download_panel.finish(tr("Download abgebrochen."), COLOR_WARN)


        self.statusBar().showMessage(
            tr("OSM-Download abgebrochen. Die bisherigen Daten bleiben unver\u00e4ndert.")
        )

    def _on_osm_worker_finished(self):

        self._set_osm_running(False)

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

    def _open_help_center(self):
        from src.gui.help_center_dialog import HelpCenterDialog

        HelpCenterDialog(self).exec()

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
            base_url=self.server.url,
        )
        project = self.map_widget.controller.project
        dialog.apply_settings(project.export_settings)
        dialog.exec()
        project.set_export_settings(dialog.collect_settings())

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
            self._osm_worker.cancel()
            self._osm_worker.wait(5000)

        try:
            self.server.stop()
        except Exception:
            pass

        event.accept()
