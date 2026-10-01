from PySide6.QtCore import QObject, Slot

from src.geometry.polyline import Polyline


class Bridge(QObject):
    """
    Bridge zwischen JavaScript und Python.
    """

    def __init__(self, controller):
        super().__init__()

        self.controller = controller

    # ---------------------------------------------------------
    # Kartenklick
    # ---------------------------------------------------------

    @Slot(float, float)
    def mapClicked(
        self,
        lat: float,
        lon: float
    ):
        print(
            f"Klick: {lat:.6f}, {lon:.6f}"
        )

        self.controller.map_clicked(
            lat,
            lon
        )

    # ---------------------------------------------------------
    # Polyline hinzufügen
    # ---------------------------------------------------------

    @Slot(str, list, str)
    def addPolyline(
        self,
        polyline_id: str,
        points,
        text: str = ""
    ):
        print(
            f"Polyline hinzufügen: {polyline_id}"
        )

        polyline = Polyline(
            id=polyline_id,
            points=points,
            text=text
        )

        self.controller.project.add_polyline(
            polyline
        )

        self.controller.project.mark_dirty()

        print(
            ">>> POLYLINE IM PROJEKT:",
            len(
                self.controller.project.polylines
            )
        )

    # ---------------------------------------------------------
    # Ebene sichtbar schalten (Zeichnen)
    # ---------------------------------------------------------

    @Slot(str)
    def ensureLayerVisible(
        self,
        layer_name: str
    ):
        self.controller.ensure_layer_visible(
            layer_name
        )

    # ---------------------------------------------------------
    # Marker angeklickt
    # ---------------------------------------------------------

    @Slot(str)
    def markerClicked(
        self,
        marker_id: str
    ):
        print(
            f"Marker geklickt: {marker_id}"
        )

        self.controller.marker_clicked(
            marker_id
        )

    # ---------------------------------------------------------
    # Marker verschoben
    # ---------------------------------------------------------

    @Slot(str, float, float)
    def markerMoved(
        self,
        marker_id: str,
        lat: float,
        lon: float
    ):
        self.controller.marker_moved(
            marker_id,
            lat,
            lon
        )

    # ---------------------------------------------------------
    # Polyline verschoben
    # ---------------------------------------------------------

    @Slot(str, list)
    def polylineMoved(
        self,
        polyline_id: str,
        points
    ):
        print(
            f"Polyline verschoben: {polyline_id}"
        )

        self.controller.update_polyline(
            polyline_id,
            points
        )

    # ---------------------------------------------------------
    # OSM-Punkt verschoben
    # ---------------------------------------------------------

    @Slot(float, float, float, float)
    def osmVertexMoved(
        self,
        from_lat: float,
        from_lon: float,
        to_lat: float,
        to_lon: float
    ):
        self.controller.move_osm_vertices(
            from_lat,
            from_lon,
            to_lat,
            to_lon
        )

    # ---------------------------------------------------------
    # Polyline Eigenschaften geändert
    # ---------------------------------------------------------

    @Slot(str, dict)
    def polylinePropertiesChanged(
        self,
        polyline_id: str,
        properties: dict
    ):
        print(
            f"Polyline Eigenschaften geändert: {polyline_id}"
        )

        self.controller.update_polyline_properties(
            polyline_id,
            properties
        )

    # ---------------------------------------------------------
    # Rechteck (temporär)
    # ---------------------------------------------------------

    @Slot(float, float, float, float)
    def selectionChanged(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ):
        self.controller.selection_changed(
            lat1,
            lon1,
            lat2,
            lon2
        )

    # ---------------------------------------------------------
    # Rechteck-Tool: verschoben / gedreht
    # ---------------------------------------------------------

    @Slot(float, float, float, float, float)
    def rectangleChanged(
        self,
        center_lat: float,
        center_lon: float,
        width_m: float,
        height_m: float,
        rotation_deg: float
    ):
        self.controller.rectangle_changed(
            center_lat,
            center_lon,
            width_m,
            height_m,
            rotation_deg
        )