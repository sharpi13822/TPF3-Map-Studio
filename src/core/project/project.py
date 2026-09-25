from dataclasses import dataclass, field

from src.map.objects.marker import Marker
from src.map.objects.selection import Selection
from src.osm.objects.osm_data import OSMData
from src.geometry.polyline import Polyline



@dataclass
class Project:
    """
    Enthält sämtliche Projektdaten.
    """

    name: str = "Neues Projekt"

    # ---------------------------------------------------------
    # Projektinformationen
    # ---------------------------------------------------------

    author: str = ""

    description: str = ""

    created: str = ""

    modified: str = ""

    # ---------------------------------------------------------
    # Projektinformationen
    # ---------------------------------------------------------

    author: str = ""

    description: str = ""

    created: str = ""

    modified: str = ""

    # ---------------------------------------------------------
    # Projektstatus
    # ---------------------------------------------------------

    dirty: bool = False

    # ---------------------------------------------------------
    # Heightmap-Export-Status
    # ---------------------------------------------------------

    heightmap_export_path: str = ""
    heightmap_exported_at: str = ""

    # ---------------------------------------------------------
    # Kartenobjekte
    # ---------------------------------------------------------

    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    def mark_dirty(self):
        """
        Projekt wurde verändert.
        """

        self.dirty = True

    def mark_clean(self):
        """
        Projekt wurde gespeichert.
        """

        self.dirty = False

    def mark_heightmap_exported(self, path: str):
        """
        Vermerkt, dass fuer dieses Projekt erfolgreich eine Heightmap
        exportiert wurde (siehe HeightmapDialog._export()). Wird u.a.
        vom Projekt-Dashboard ausgewertet, um "Heightmap fehlt noch"
        von "Heightmap exportiert" zu unterscheiden.
        """

        from datetime import datetime

        self.heightmap_export_path = path
        self.heightmap_exported_at = datetime.now().isoformat(
            timespec="seconds"
        )

        self.mark_dirty()

    markers: list[Marker] = field(default_factory=list)

    polylines: list[Polyline] = field(default_factory=list)

    polygons: list[dict] = field(default_factory=list)

    selection: Selection | None = None

    # ---------------------------------------------------------
    # OpenStreetMap
    # ---------------------------------------------------------

    osm: OSMData = field(default_factory=OSMData)

    # ---------------------------------------------------------
    # Marker
    # ---------------------------------------------------------

    def add_marker(
        self,
        marker: Marker
    ):
        """
        Marker hinzufügen.
        """

        self.markers.append(marker)

    def remove_marker(
        self,
        marker_id: str
    ) -> bool:
        """
        Marker anhand der ID entfernen.
        """

        for marker in self.markers:

            if marker.id == marker_id:

                self.markers.remove(marker)

                return True

        return False

    def clear_markers(self):
        """
        Alle Marker entfernen.
        """

        self.markers.clear()


    # ---------------------------------------------------------
    # Polylines
    # ---------------------------------------------------------

    def add_polyline(
        self,
        polyline: Polyline
    ):
        """
        Linie hinzufügen.
        """

        self.polylines.append(
            polyline
        )


    def remove_polyline(
        self,
        polyline_id: str
    ) -> bool:
        """
        Linie anhand der ID entfernen.
        """

        for polyline in self.polylines:

            if polyline.id == polyline_id:

                self.polylines.remove(
                    polyline
                )

                return True

        return False


    def clear_polylines(self):
        """
        Alle Linien entfernen.
        """

        self.polylines.clear()

    # ---------------------------------------------------------
    # Polygone
    # ---------------------------------------------------------

    def add_polygon(
        self,
        polygon: dict
    ):
        """
        Polygon hinzufügen.
        """

        self.polygons.append(
            polygon
        )


    def remove_polygon(
        self,
        polygon_id: str
    ) -> bool:
        """
        Polygon anhand der ID entfernen.
        """

        for polygon in self.polygons:

            if polygon.get("id") == polygon_id:

                self.polygons.remove(
                    polygon
                )

                return True

        return False

    def clear_polygons(self):
            """
            Alle Polygone entfernen.
            """

            self.polygons.clear()   

    # ---------------------------------------------------------
    # Auswahl
    # ---------------------------------------------------------

    def set_selection(
        self,
        selection: Selection
    ):
        """
        Rechteckauswahl setzen.
        """

        self.selection = selection

    def clear_selection(self):
        """
        Rechteckauswahl löschen.
        """

        self.selection = None

    # ---------------------------------------------------------
    # OpenStreetMap
    # ---------------------------------------------------------

    def set_osm_data(
        self,
        osm: OSMData
    ):
        """
        OSM-Daten übernehmen.
        """

        self.osm = osm

    def clear_osm_data(self):
        """
        Alle OSM-Daten entfernen.
        """

        self.osm.clear()

    # ---------------------------------------------------------
    # Informationen
    # ---------------------------------------------------------

    @property
    def marker_count(self) -> int:
        return len(self.markers)

    @property
    def polyline_count(self) -> int:
        return len(self.polylines)

    @property
    def has_selection(self) -> bool:
        return self.selection is not None

    @property
    def node_count(self) -> int:
        return self.osm.node_count

    @property
    def way_count(self) -> int:
        return self.osm.way_count

    @property
    def relation_count(self) -> int:
        return self.osm.relation_count