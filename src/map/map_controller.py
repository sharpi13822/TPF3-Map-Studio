from enum import Enum

from PySide6.QtCore import QObject, Signal

from src.core.project.project import Project
from src.core.project_serializer import ProjectSerializer

from src.osm.overpass_client import OverpassClient

from src.map.layer_manager import LayerManager

from src.map.objects.marker import Marker
from src.map.objects.selection import Selection

from src.map.renderer.renderer_factory import RendererFactory
from src.osm.geometry.geometry_builder import GeometryBuilder

from src.undo.undo_stack import UndoStack
from src.undo.marker_commands import AddMarkerCommand


class Tool(Enum):
    MARKER = "marker"
    SELECTION = "selection"


class MapController(QObject):
    """
    Zentrale Steuerung aller Kartenfunktionen.
    """

    marker_selected = Signal(str)
    marker_updated = Signal(str)

    def __init__(self, api):
        super().__init__()

        self.api = api

        # ---------------------------------------------------------
        # Projekt
        # ---------------------------------------------------------

        self.project = Project()

        # ---------------------------------------------------------
        # OSM
        # ---------------------------------------------------------

        self.overpass = OverpassClient()

        # ---------------------------------------------------------
        # Layer
        # ---------------------------------------------------------

        self.layer_manager = LayerManager()

        # ---------------------------------------------------------
        # Undo / Redo
        # ---------------------------------------------------------

        self.undo_stack = UndoStack()

        # ---------------------------------------------------------
        # Renderer
        # ---------------------------------------------------------

        self.renderers = RendererFactory.create(
            self.api,
            self.layer_manager,
        )


        # ---------------------------------------------------------
        # Renderer-Lookup
        # ---------------------------------------------------------

        self.renderer_lookup = {

            renderer.layer: renderer

            for renderer in self.renderers

        }

        # ---------------------------------------------------------
        # Werkzeug
        # ---------------------------------------------------------

        self._tool = Tool.MARKER

        # ---------------------------------------------------------
        # Marker
        # ---------------------------------------------------------

        self._next_marker_id = 1

        self.selected_marker = None

        # ---------------------------------------------------------
        # Rechteckauswahl
        # ---------------------------------------------------------

        self._selection_start = None

    # ---------------------------------------------------------
    # Werkzeug
    # ---------------------------------------------------------

    def set_tool(
        self,
        tool: Tool
    ):
        """
        Aktives Werkzeug wechseln.
        """

        self._tool = tool

        self._selection_start = None

        print(
            f"Werkzeug gewechselt zu: {tool.value}"
        )

    @property
    def tool(self):
        return self._tool
    

    # ---------------------------------------------------------
    # Layer
    # ---------------------------------------------------------

    def set_layer_visible(self, layer, visible):
     self.layer_manager.set_visible(layer, visible)

     self.redraw_layers()


    def set_layer_locked(self, layer, locked):
     self.layer_manager.set_locked(layer, locked)

     self.redraw_layers() 

    # ---------------------------------------------------------
    # Layer neu zeichnen
    # ---------------------------------------------------------

    def redraw_layers(self):

        print(">>> redraw_layers()")

        osm = self.project.osm

        for renderer in self.renderers:
            renderer.draw(osm)

    # ---------------------------------------------------------
    # Intern
    # ---------------------------------------------------------

    def _new_marker_id(self) -> str:
        """
        Erzeugt eine neue Marker-ID.
        """

        marker_id = f"m{self._next_marker_id}"

        self._next_marker_id += 1

        return marker_id

    # ---------------------------------------------------------
    # Startposition
    # ---------------------------------------------------------

    def show_start_position(self):
        """
        Zentriert die Karte auf München.
        """

        self.api.center_and_zoom(
            48.1372,
            11.5756,
            12
        )

        self.add_marker(
            48.1372,
            11.5756,
            "München"
        )

    # ---------------------------------------------------------
    # Kartenklick
    # ---------------------------------------------------------

    def map_clicked(
        self,
        lat: float,
        lon: float
    ):
        """
        Verarbeitung eines Kartenklicks.
        """

        if self._tool == Tool.MARKER:

            self.execute_command(

                AddMarkerCommand(
                    self,
                    lat,
                    lon,
                    f"{lat:.6f}, {lon:.6f}"
                )

            )

            return

        if self._tool == Tool.SELECTION:

            if self._selection_start is None:

                self._selection_start = (
                    lat,
                    lon
                )

                print(
                    f"Auswahl gestartet: "
                    f"{lat:.6f}, {lon:.6f}"
                )

                return

            lat1, lon1 = self._selection_start

            self._selection_start = None

            self.selection_changed(
                lat1,
                lon1,
                lat,
                lon
            )

    # ---------------------------------------------------------
    # Marker
    # ---------------------------------------------------------

    def add_marker(
        self,
        lat: float,
        lon: float,
        text: str = "",
        marker_id: str | None = None
    ) -> str:
        """
        Fügt einen Marker hinzu.
        """

        marker = Marker(
            id=marker_id or self._new_marker_id(),
            lat=lat,
            lon=lon,
            text=text
        )

        self.project.add_marker(
            marker
        )

        self.project.mark_dirty()

        self.api.add_marker(
            marker.id,
            marker.lat,
            marker.lon,
            marker.text
        )

        return marker.id

    def remove_marker(
        self,
        marker_id: str
    ):
        """
        Entfernt einen Marker.
        """

        for marker in self.project.markers:

            if marker.id != marker_id:
                continue

            self.api.remove_marker(
                marker.id
            )

            self.project.remove_marker(
                marker.id
            )

            self.project.mark_dirty()

            return

    def rename_marker(
            self,
            marker_id: str,
            text: str
        ):

        """
        Ändert den Text eines Markers.
        """

        for marker in self.project.markers:

            if marker.id != marker_id:
                continue

            marker.text = text

            self.project.mark_dirty()

            self.redraw_markers()

            self.marker_updated.emit(
                marker.id
            )

            return

    def clear_markers(self):
        """
        Entfernt alle Marker.
        """

        self.api.clear_markers()

        self.project.clear_markers()

        self.project.mark_dirty()

        print(
            "Alle Marker entfernt."
        )

    def marker_clicked(
        self,
        marker_id: str
    ):
        """
        Marker wurde angeklickt.
        """

        self.selected_marker = marker_id

        print(
            f"Marker ausgewählt: {marker_id}"
        )

       # self.api.select_marker(
       #     marker_id
       # )

        self.marker_selected.emit(
           marker_id
        )

    def redraw_markers(self):
        """
        Zeichnet alle Marker neu.
        """

        self.api.clear_markers()

        for marker in self.project.markers:

            self.api.add_marker(
                marker.id,
                marker.lat,
                marker.lon,
                marker.text
            )

    # ---------------------------------------------------------
    # OpenStreetMap
    # ---------------------------------------------------------

    def download_osm(self) -> bool:
        """
        Lädt OSM-Daten für die aktuelle Auswahl.
        """

        if self.project.selection is None:

            print(
                "Keine Auswahl vorhanden."
            )

            return False

        print(
            "Starte OSM-Download..."
        )

        try:

            osm = self.overpass.download(
                self.project.selection
            )

            GeometryBuilder(osm).build()

            self.project.set_osm_data(osm)

            print("\n===== LANDUSE =====")

            for way in osm.ways.values():

                if "landuse" not in way.tags:
                    continue

                node = osm.nodes.get(way.nodes[0])

                print(
                    way.id,
                    way.tags,
                    node.lat,
                    node.lon
                )

            # ---------------------------------------------------------
            # Debug: Erste Wald-Relation anzeigen
            # ---------------------------------------------------------

            print("===== RELATIONEN =====")

            for relation in osm.relations.values():
                print(
                    relation.id,
                    relation.tags
                )

            print("======================")

            self.redraw_layers()

            print(
                "Download beendet."
            )

            print(
                f"Nodes     : {osm.node_count}"
            )

            print(
                f"Ways      : {osm.way_count}"
            )

            print(
                f"Relations : {osm.relation_count}"
            )

            return True

        except Exception as exc:
            import traceback
            traceback.print_exc()
            
            "OSM-Download fehlgeschlagen:"
        

            print(exc)

            return False    
        
            # ---------------------------------------------------------
    # Rechteckauswahl
    # ---------------------------------------------------------

    def selection_changed(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ):
        """
        Erstellt bzw. aktualisiert die aktuelle Rechteckauswahl.
        """

        selection = Selection(
            min_lat=min(lat1, lat2),
            min_lon=min(lon1, lon2),
            max_lat=max(lat1, lat2),
            max_lon=max(lon1, lon2)
        )

        self.project.set_selection(
            selection
        )

        self.project.mark_dirty()

        print("Bounding Box:")

        print(
            f"  Min: {selection.min_lat:.6f}, "
            f"{selection.min_lon:.6f}"
        )

        print(
            f"  Max: {selection.max_lat:.6f}, "
            f"{selection.max_lon:.6f}"
        )

        self.api.clear_rectangle()

        self.api.draw_rectangle(
            selection.min_lat,
            selection.min_lon,
            selection.max_lat,
            selection.max_lon
        )

    
    # ---------------------------------------------------------
    # Projekt speichern / laden
    # ---------------------------------------------------------

    def save_project(
        self,
        filename: str
    ):
        """
        Speichert das aktuelle Projekt.
        """

        ProjectSerializer.save(
            self.project,
            filename,
            self.layer_manager
        )

        self.project.mark_clean()

    def load_project(
        self,
        filename: str
    ):
        """
        Lädt ein Projekt.
        """

        ProjectSerializer.load(
            filename,
            self.project,
            self.layer_manager
        )

        # -------------------------------------------------
        # Layer neu zeichnen
        # -------------------------------------------------

        self.redraw_layers()

        # -------------------------------------------------
        # Marker neu zeichnen
        # -------------------------------------------------

        self.redraw_markers()

        # -------------------------------------------------
        # Auswahl wiederherstellen
        # -------------------------------------------------

        if self.project.selection is not None:

            selection = self.project.selection

            self.api.draw_rectangle(
                selection.min_lat,
                selection.min_lon,
                selection.max_lat,
                selection.max_lon
            )

        else:

            self.api.clear_rectangle()

        # -------------------------------------------------
        # Auswahl zurücksetzen
        # -------------------------------------------------

        self.selected_marker = None

        # -------------------------------------------------
        # Projekt ist jetzt sauber
        # -------------------------------------------------

        self.project.mark_clean()

            # ---------------------------------------------------------
    # Undo / Redo
    # ---------------------------------------------------------

    def execute_command(
        self,
        command
    ):
        """
        Führt einen Command aus und legt ihn auf den Undo-Stack.
        """

        self.undo_stack.push(
            command
        )

    def undo(self):
        """
        Macht die letzte Aktion rückgängig.
        """

        self.undo_stack.undo()

    def redo(self):
        """
        Stellt die letzte rückgängig gemachte Aktion wieder her.
        """

        self.undo_stack.redo()

    @property
    def can_undo(self):
        return self.undo_stack.can_undo

    @property
    def can_redo(self):
        return self.undo_stack.can_redo

    def set_layer_opacity(self, layer, opacity):
        self.layer_manager.set_opacity(layer, opacity)
        self.redraw_layers()


    def move_layer_up(self, layer):
        self.layer_manager.move_up(layer)
        self.redraw_layers()


    def move_layer_down(self, layer):
        self.layer_manager.move_down(layer)
        self.redraw_layers()

    # ---------------------------------------------------------
    # Informationen
    # ---------------------------------------------------------

    @property
    def selection(self):
        """
        Aktuelle Rechteckauswahl.
        """

        return self.project.selection

    @property
    def markers(self):
        """
        Alle Marker des Projekts.
        """

        return self.project.markers

    @property
    def osm(self):
        """
        Geladene OSM-Daten.
        """

        return self.project.osm

    @property
    def marker_count(self):
        """
        Anzahl der Marker.
        """

        return self.project.marker_count

    @property
    def marker_ids(self):
        """
        Liste aller Marker-IDs.
        """

        return [
            marker.id
            for marker in self.project.markers
        ]

    # ---------------------------------------------------------
    # Marker aktualisieren
    # ---------------------------------------------------------

    def update_marker(
        self,
        marker: Marker
    ):
        """
        Marker wurde geändert.
        """

        self.project.mark_dirty()

        self.marker_updated.emit(
            marker.id
        )
    def set_layer_visible(self, layer, visible):

        self.layer_manager.set_visible(layer, visible)

        self.api.set_layer_visible(layer, visible) 