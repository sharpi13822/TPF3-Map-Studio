from dataclasses import dataclass, field

from src.map.objects.marker import Marker
from src.map.objects.selection import Selection
from src.osm.objects.osm_data import OSMData



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

    markers: list[Marker] = field(default_factory=list)

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