import json

from src.map.layer import Layer


class LeafletAPI:

    def __init__(self, web_view):
        self.web_view = web_view

    # ---------------------------------------------------------
    # Intern
    # ---------------------------------------------------------

    def _call(self, function: str, *args):

        # Ellipsis früh erkennen
        for index, arg in enumerate(args):
            if arg is Ellipsis:
                raise ValueError(
                    f"Argument {index} für '{function}' ist Ellipsis (...)."
                )

        try:
            arguments = ", ".join(
                json.dumps(arg)
                for arg in args
            )
        except TypeError:
            print("\n===== JSON ERROR =====")
            print("Function:", function)

            for i, arg in enumerate(args):
                print(f"arg[{i}] = {repr(arg)}")
                print("type     =", type(arg))

            raise

        script = f"window.MapApi.{function}({arguments});"

        if function == "addBatch":
            print("JS >", function, "- Batch gesendet")
        else:
            print("JS >", script)

        self.web_view.page().runJavaScript(script)

    # ---------------------------------------------------------
    # Kamera
    # ---------------------------------------------------------

    def center(self, lat, lon):
        self._call("center", lat, lon)

    def zoom(self, zoom):
        self._call("zoom", zoom)

    def center_and_zoom(self, lat, lon, zoom):
        self._call(
            "centerAndZoom",
            lat,
            lon,
            zoom,
        )

    # ---------------------------------------------------------
    # Marker
    # ---------------------------------------------------------

    def add_marker(self, marker_id, lat, lon, text=""):
        self._call(
            "addMarker",
            marker_id,
            lat,
            lon,
            text,
        )

    def update_marker(self, marker_id, lat, lon, text=""):
        self._call(
            "updateMarker",
            marker_id,
            lat,
            lon,
            text,
        )

    def remove_marker(self, marker_id):
        self._call(
            "removeMarker",
            marker_id,
        )

    def clear_markers(self):
        self._call("clearMarkers")

    def add_polyline(
        self,
        polyline_id,
        points,
        text=""
    ):
        self._call(
            "addPolyline",
            polyline_id,
            points,
            text,
        )

    def add_polygon(
        self,
        polygon_id,
        points,
        text="",
        properties=None
    ):
        self._call(
            "addPolygon",
            polygon_id,
            points,
            text,
            properties or {}
        )

    def remove_polyline(
            self,
            polyline_id
    ):
        self._call(
            "removePolyline",
            polyline_id,
        )

    def clear_polylines(self):
        self._call(
            "clearPolylines"
        )
        
    # ---------------------------------------------------------
    # Rechteck
    # ---------------------------------------------------------

    def draw_rectangle(
        self,
        min_lat,
        min_lon,
        max_lat,
        max_lon,
    ):
        self._call(
            "drawRectangle",
            min_lat,
            min_lon,
            max_lat,
            max_lon,
        )

    def draw_rotated_rectangle(
        self,
        corners,
    ):
        """Zeichnet ein gedrehtes Kartenband als 4-Punkt-Polygon.

        corners: Liste von (lat, lon)-Paaren, wie sie
        Selection.corners_latlon() liefert.
        """
        self._call(
            "drawRotatedRectangle",
            [[lat, lon] for lat, lon in corners],
        )

    def enable_rectangle_editing(
        self,
        center_lat,
        center_lon,
        width_m,
        height_m,
        rotation_deg,
    ):
        """Zeichnet ein gedrehtes Kartenband UND macht es per Maus
        verschieb- und drehbar (zwei Griffe: Mittelpunkt, Drehwinkel).
        Ersetzt eine vorher vorhandene Auswahl.
        """
        self._call(
            "enableRectangleEditing",
            center_lat,
            center_lon,
            width_m,
            height_m,
            rotation_deg,
        )

    def clear_rectangle(self):
        self._call("clearRectangle")

    # ---------------------------------------------------------
    # Koordinaten-Messwerkzeug
    # ---------------------------------------------------------

    def draw_measure_line(
        self,
        lat1,
        lon1,
        lat2,
        lon2,
        text="",
    ):
        self._call(
            "drawMeasureLine",
            lat1,
            lon1,
            lat2,
            lon2,
            text,
        )

    def clear_measure_line(self):
        self._call("clearMeasureLine")

    # ---------------------------------------------------------
    # Layer
    # ---------------------------------------------------------

    def clear(self, layer: Layer):
        self._call(
            "clear",
            layer.name.lower(),
        )


    def draw_batch(
        self,
        layer: Layer,
        objects: list,
    ):
        self._call(
            "drawBatch",
            layer.name.lower(),
            objects,
        )
 
    def update_batch(
        self,
        layer: Layer,
        objects: list,
    ):
        self._call(
            "updateBatch",
            layer.name.lower(),
            objects,
        )

    def remove(
        self,
        layer: Layer,
        object_ids: list[int],
    ):
        print(
            f"JS > removeObjects - "
            f"layer={layer.name.lower()} "
            f"count={len(object_ids)}"
        )
        
        self._call(
            "removeObjects",
            layer.name.lower(),
            object_ids,
        )

    def add_batch(
        self,
        layer: Layer,
        objects: list,
    ):
        self._call(
            "addBatch",
            layer.name.lower(),
            objects,
        ) 
    def set_layer_visible(self, layer: Layer, visible: bool):
        self._call(
            "setLayerVisible",
            layer.name.lower(),
            visible,
        )