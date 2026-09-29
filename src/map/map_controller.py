from enum import Enum
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from src.core.project.project import Project
from src.core.project_serializer import ProjectSerializer

from src.osm.overpass_client import OverpassClient
from src.osm.overpass_query_builder import OverpassQueryConfig
from src.osm.objects.osm_data import OSMData

from src.map.layer_manager import LayerManager

from src.map.objects.marker import Marker
from src.map.objects.selection import Selection

from src.map.renderer.renderer_factory import RendererFactory
from src.osm.geometry.geometry_builder import GeometryBuilder

from src.undo.undo_stack import UndoStack
from src.undo.marker_commands import AddMarkerCommand
from src.undo.move_marker_command import MoveMarkerCommand
from src.geometry.polyline import Polyline
from src.export.osm_exporter import OSMExporter
from src.tpf2.tpf2_exporter import TPF2Exporter
from src.tpf2.tpf2_lua_writer import TPF2LuaWriter


class Tool(Enum):
    MARKER = "marker"
    POLYLINE = "polyline"
    SELECTION = "selection"
    MEASURE = "measure"


def _haversine_m(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
) -> float:
    """
    Distanz zwischen zwei lat/lon-Punkten in Metern (Haversine-Formel).
    Fuer die hier relevanten Entfernungen (Kartenband-Groessenordnung,
    bis zu einigen zehn/hundert km) ist das genau genug - siehe auch
    den Kommentar zu _R_EARTH in Selection.corners_latlon().
    """

    import math

    r = 6371008.8

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )

    return 2 * r * math.asin(math.sqrt(a))


def _format_distance(distance_m: float) -> str:

    if distance_m >= 1000:
        return f"{distance_m / 1000:.3f} km ({distance_m:.0f} m)"

    return f"{distance_m:.1f} m"


class MapController(QObject):
    """
    Zentrale Steuerung aller Kartenfunktionen.
    """

    marker_selected = Signal(str)
    marker_updated = Signal(str)
    markers_changed = Signal()
    measurement_changed = Signal(str)

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

        # Overpass-Abfrage-Baukasten: welche Kategorien beim naechsten
        # OSM-Download abgefragt werden (siehe Werkzeuge > Overpass-Abfrage).
        self.overpass_config = OverpassQueryConfig()

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

        # Start-Punkt des Koordinaten-Messwerkzeugs (erster Klick),
        # nach Analogie zu _selection_start beim Rechteck-Werkzeug.
        self._measure_start = None

        # Temporäre Punkte für das Polyline-Werkzeug
        self._polyline_points = []

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
        self._measure_start = None

        print(
            f"Werkzeug gewechselt zu: {tool.value}"
        )

    @property
    def tool(self):
        return self._tool

    # ---------------------------------------------------------
    # Overpass-Abfrage-Konfiguration
    # ---------------------------------------------------------

    def set_overpass_config(self, config: OverpassQueryConfig):
        """
        Legt fest, welche Kategorien der naechste OSM-Download abfragt
        (siehe Werkzeuge > Overpass-Abfrage).
        """

        self.overpass_config = config
    

    # ---------------------------------------------------------
    # Layer
    # ---------------------------------------------------------

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

    def _new_polyline_id(self) -> str:

        index = 1

        while any(
           p.id == f"l{index}"
           for p in self.project.polylines
        ):
            index += 1

        return f"l{index}"

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

        if self._tool == Tool.POLYLINE:

            self._polyline_points.append(
                [lat, lon]
            )

            print(
                f"Polyline-Punkt: "
                f"{lat:.6f}, {lon:.6f}"
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

            return

        if self._tool == Tool.MEASURE:

            if self._measure_start is None:

                self._measure_start = (lat, lon)

                self.api.clear_measure_line()

                self.measurement_changed.emit(
                    f"Messung: Startpunkt {lat:.6f}, {lon:.6f} "
                    f"(zweiten Punkt anklicken)"
                )

                return

            lat1, lon1 = self._measure_start

            self._measure_start = None

            distance_m = _haversine_m(lat1, lon1, lat, lon)

            distance_text = _format_distance(distance_m)

            self.api.draw_measure_line(
                lat1,
                lon1,
                lat,
                lon,
                distance_text,
            )

            self.measurement_changed.emit(
                f"Messung: {distance_text}"
            )

            print(
                f"Distanz gemessen: {distance_text} "
                f"({lat1:.6f}, {lon1:.6f} -> {lat:.6f}, {lon:.6f})"
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

        self.markers_changed.emit()

        return marker.id


    def add_polyline(
        self,
        points: list,
        text: str = "",
        polyline_id: str | None = None
    ) -> str:
        """
        Fügt eine Polyline hinzu.
        """

        polyline = Polyline(
            id=polyline_id or self._new_polyline_id(),
            text=text,
            points=points
        )

        self.project.add_polyline(
            polyline
        )

        print(
            ">>> POLYLINE HINZUGEFÜGT:",
            id(self.project),
            len(self.project.polylines)
        )

        self.api.add_polyline(
            polyline.id,
            polyline.points,
            polyline.text
        )

        self.project.mark_dirty()

        return polyline.id

    def update_polyline(
        self,
        polyline_id: str,
        points: list
    ):

        for polyline in self.project.polylines:

            if polyline.id != polyline_id:
                continue

            polyline.points = points

            self.project.mark_dirty()

            print(
                f"Polyline aktualisiert: {polyline_id}"
            )

            return

        print(
            f"Polyline nicht gefunden: {polyline_id}"
        )

    def update_polyline_properties(
        self,
        polyline_id: str,
        properties: dict
    ):
        """
        Aktualisiert Eigenschaften einer vorhandenen Polyline.
        """

        print(
            f"Polyline Eigenschaften aktualisieren: {polyline_id}"
        )

        for polyline in self.project.polylines:

            if polyline.id != polyline_id:
                continue

            if "name" in properties:
                polyline.text = properties["name"]

            self.project.mark_dirty()

            print(
                f"Polyline Eigenschaften gespeichert: "
                f"{polyline_id}"
            )

            return

        print(
            f"Polyline nicht gefunden: "
            f"{polyline_id}"
        )

    def update_polyline_geometry(
        self,
        polyline_id: str,
        points: list
    ):
        """
        Aktualisiert die Geometrie einer vorhandenen Polyline.
        """

        for polyline in self.project.polylines:

            if polyline.id != polyline_id:
                continue

            polyline.points = points

            self.project.mark_dirty()

            print(
                f"Polyline aktualisiert: {polyline_id}"
            )

            return

        print(
            f"Polyline nicht gefunden: "
            f"{polyline_id}"
        )

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

            self.markers_changed.emit()

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

            self.markers_changed.emit()

            return

    def move_marker(
        self,
        marker_id: str,
        lat: float,
        lon: float
    ):
        """
        Verschiebt einen Marker.
        """

        for marker in self.project.markers:

            if marker.id != marker_id:
                continue

            marker.lat = lat
            marker.lon = lon

            self.project.mark_dirty()

            self.api.update_marker(
                marker.id,
                marker.lat,
                marker.lon,
                marker.text
            )

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

    def marker_moved(
            self,
            marker_id: str,
            lat: float,
            lon: float
    ):
        marker = next(
            (
                m
                for m in self.project.markers
                if m.id == marker_id
            ),
            None
            
        )

        if marker is None:
            return

        self.undo_stack.push(
            MoveMarkerCommand(
                self,
                marker.id,
                marker.lat,
                marker.lon,
                lat,
                lon
            )
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

    def fetch_osm(
        self,
        selection: Selection,
        overpass_config: OverpassQueryConfig,
    ) -> OSMData:
        """
        Laedt und verarbeitet OSM-Daten fuer die uebergebene Auswahl.

        Laeuft im Hintergrund-Thread (siehe MainWindow._download_osm):
        darf daher weder das Projekt veraendern noch die Karte bzw.
        andere Qt-Objekte anfassen - das passiert erst in apply_osm()
        im GUI-Thread. Fehler werden als Exception weitergereicht.
        """

        print(
            "Starte OSM-Download..."
        )

        osm = self.overpass.download(
            selection,
            overpass_config,
        )

        GeometryBuilder(osm).build()

        # ---------------------------------------------------------
        # Export-Test
        # ---------------------------------------------------------

        exporter = OSMExporter()

        export_data = exporter.export(osm)

        # --------------------------------------------------
        # TPF2 Export
        # --------------------------------------------------

        tpf2_exporter = TPF2Exporter.from_export_data(
            export_data

        )

        tpf2_data = tpf2_exporter.export(
            export_data
        )

        # --------------------------------------------------
        # TPF2 Lua / Construction Export
        # --------------------------------------------------

        output_path = (
            Path.home()
            / "Documents"
            / "TPF3-Map-Studio"
            / "exports"
            / "osm_map_1"
        )

        tpf2_writer = TPF2LuaWriter(
            name="OSM Map",
            description=(
                "OpenStreetMap export "
                "for Transport Fever 2"
            ),
        )

        tpf2_writer.write(
            tpf2_data,
            output_path,
        )

        print(
            f"TPF2-Mod: {output_path}"
        )

        print("Export:")
        print(f"  Roads      : {len(export_data.roads)}")
        print(f"  Railways   : {len(export_data.railways)}")
        print(f"  Buildings  : {len(export_data.buildings)}")
        print(f"  Water      : {len(export_data.water)}")
        print(f"  Waterways  : {len(export_data.waterways)}")
        print(f"  Parks      : {len(export_data.parks)}")
        print(f"  Landuse    : {len(export_data.landuse)}")
        print(f"  Vegetation : {len(export_data.vegetation)}")

        print(
            f"TPF2 Roads     : "
            f"{len(tpf2_data.get('roads', []))}"
        )

        print(
            f"TPF2 Railways  : "
            f"{len(tpf2_data.get('railways', []))}"
        )

        print(
            f"TPF2 Export    : {output_path}"
        )

        return osm

    def apply_osm(
        self,
        osm: OSMData,
    ):
        """
        Uebernimmt die von fetch_osm() geladenen Daten ins Projekt und
        zeichnet die Karte neu. Nur im GUI-Thread aufrufen.
        """

        self.project.set_osm_data(osm)

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

    def set_rotated_selection(
        self,
        center_lat: float,
        center_lon: float,
        width_m: float,
        height_m: float,
        rotation_deg: float,
        margin_m: float = 500.0,
    ):
        """
        Erstellt ein gedrehtes Kartenband (Rechteck-Tool) als aktuelle
        Auswahl - Gegenstueck zu selection_changed() fuer den Fall, dass
        Mittelpunkt/Groesse/Drehwinkel direkt eingegeben werden, statt
        zwei Punkte auf der Karte anzuklicken.

        margin_m: Sicherheitsrand fuer die gespeicherte Bounding Box
        (wichtig fuer nachgelagerte OSM-/Hoehendaten-Downloads, siehe
        Selection.from_center()).
        """

        selection = Selection.from_center(
            center_lat=center_lat,
            center_lon=center_lon,
            width_m=width_m,
            height_m=height_m,
            rotation_deg=rotation_deg,
            margin_m=margin_m,
        )

        self.project.set_selection(
            selection
        )

        self.project.mark_dirty()

        print("Gedrehtes Kartenband:")

        print(
            f"  Mittelpunkt: {center_lat:.6f}, {center_lon:.6f}"
        )

        print(
            f"  Groesse: {width_m:.0f} x {height_m:.0f} m, "
            f"Drehung: {rotation_deg:.2f} Grad"
        )

        self.api.clear_rectangle()

        self.api.enable_rectangle_editing(
            center_lat,
            center_lon,
            width_m,
            height_m,
            rotation_deg,
        )

        return selection

    def rectangle_changed(
        self,
        center_lat: float,
        center_lon: float,
        width_m: float,
        height_m: float,
        rotation_deg: float,
    ):
        """
        Aktualisiert die Selection, nachdem das Rechteck-Tool per Maus
        verschoben oder gedreht wurde. Zeichnet NICHT neu - die Karte
        zeigt das Ergebnis bereits live (gleiches Prinzip wie bei
        marker_moved()), hier wird nur der Projektzustand nachgezogen.
        """

        # Fester Sicherheitsrand statt Rueckrechnung aus der alten Bbox:
        # deren Groesse haengt nichtlinear von Breite, Hoehe UND Drehwinkel
        # zusammen ab, ein einfacher Rueckschluss daraus waere bei
        # schraegen Winkeln ungenau. 500 m ist derselbe Standardwert wie
        # im Rechteck-Tool-Dialog.
        margin_m = 500.0

        selection = Selection.from_center(
            center_lat=center_lat,
            center_lon=center_lon,
            width_m=width_m,
            height_m=height_m,
            rotation_deg=rotation_deg,
            margin_m=margin_m,
        )

        self.project.set_selection(
            selection
        )

        self.project.mark_dirty()

        print(
            f"Kartenband verschoben/gedreht: "
            f"Mittelpunkt {center_lat:.6f}, {center_lon:.6f}, "
            f"Drehung {rotation_deg:.2f}°"
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

        print(
            ">>> SPEICHERN:",
            id(self.project),
            len(self.project.polylines)
        )

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

        # ---------------------------------------------------------
        # OSM-Geometrien nach dem Laden neu aufbauen
        # ---------------------------------------------------------

        if self.project.osm.way_count > 0:

            GeometryBuilder(
                self.project.osm
            ).build()

        print(
            ">>> GELADENE POLYLINES:",
            len(self.project.polylines)
        )

        # -------------------------------------------------
        # Layer neu zeichnen
        # -------------------------------------------------

        self.redraw_layers()

        # -------------------------------------------------
        # Gespeicherte Polylines neu zeichnen
        # -------------------------------------------------

        for polyline in self.project.polylines:
            self.api.add_polyline(
                polyline.id,
                polyline.points,
                polyline.text
            )

        # -----------------------------------------------------
        # Gespeicherte Polygone wieder zeichnen
        # -----------------------------------------------------

        for polygon in self.project.polygons:

            self.api.add_polygon(
                polygon.get("id", ""),
                polygon.get("points", []),
                polygon.get("text", ""),
                polygon.get("properties", {})
            )

        # -------------------------------------------------
        # Marker neu zeichnen
        # -------------------------------------------------

        self.redraw_markers()

        # -------------------------------------------------
        # Auswahl wiederherstellen
        # -------------------------------------------------

        if self.project.selection is not None:

            selection = self.project.selection

            if selection.is_rotated:

                center_lat, center_lon = selection.center

                self.api.enable_rectangle_editing(
                    center_lat,
                    center_lon,
                    selection.width_m,
                    selection.height_m,
                    selection.rotation_deg,
                )

            else:

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