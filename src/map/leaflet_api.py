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

    def clear_rectangle(self):
        self._call("clearRectangle")

    # ---------------------------------------------------------
    # Layer
    # ---------------------------------------------------------

    def clear(self, layer: Layer):
        self._call(layer.clear_method)

    def draw(
        self,
        layer: Layer,
        object_id,
        geometry,
        style=None,
    ):

        if geometry is None:
            return

        options = {}

        if style is not None:
            options = style.to_dict()

        self._call(
            layer.draw_method,
            object_id,
            geometry,
            options,
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