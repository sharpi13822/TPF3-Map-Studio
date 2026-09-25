import json
from typing import TYPE_CHECKING
from src.map.objects.marker import Marker
from src.map.objects.selection import Selection
from src.geometry.polyline import Polyline
from src.osm.objects.osm_data import OSMData

if TYPE_CHECKING:
    from src.core.project.project import Project
    from src.map.objects.marker import Marker
    from src.map.objects.selection import Selection


class ProjectSerializer:
    """
    Speichert und lädt Projekte im JSON-Format.
    """

    VERSION = 2

    # ---------------------------------------------------------
    # Speichern
    # ---------------------------------------------------------

    @staticmethod
    def save(
        project: "Project",
        filename: str,
        layer_manager=None
    ):
        """
        Speichert ein Projekt.
        """

        data = {

            "version": ProjectSerializer.VERSION,

            "project": {

                "name": project.name,
                "author": project.author,
                "description": project.description,
                "created": project.created,
                "modified": project.modified,
                "heightmap_export_path": project.heightmap_export_path,
                "heightmap_exported_at": project.heightmap_exported_at

            },

            "layers": (
                layer_manager.to_dict()
                if layer_manager is not None
                else {}
            ),

            "osm": project.osm.to_dict(),

            "markers": [
                {
                    "id": marker.id,
                    "lat": marker.lat,
                    "lon": marker.lon,
                    "text": marker.text
                }
                for marker in project.markers
            ],

            "polylines": [
                {
                    "id": polyline.id,
                    "text": polyline.text,
                    "points": polyline.points,
                    "properties": polyline.properties
                }
                for polyline in project.polylines
            ],

            "polygons": [
                {

                    "id": polygon.get("id", ""),
                    "text": polygon.get("text", ""),
                    "points": polygon.get("points", []),
                    "properties": polygon.get("properties", {})
                }
                for polygon in project.polygons
            ],

            "selection": (
                {
                    "min_lat": project.selection.min_lat,
                    "min_lon": project.selection.min_lon,
                    "max_lat": project.selection.max_lat,
                    "max_lon": project.selection.max_lon,
                    "rotation_deg": project.selection.rotation_deg,
                    "width_m": project.selection.width_m,
                    "height_m": project.selection.height_m,
                    "center_lat": project.selection.center_lat,
                    "center_lon": project.selection.center_lon
                }
                if project.selection
                else None
            )

        }

        with open(
            filename,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                data,
                f,
                indent=4,
                ensure_ascii=False
            )

    # ---------------------------------------------------------
    # Laden
    # ---------------------------------------------------------

    @staticmethod
    def load(
        filename: str,
        project: "Project",
        layer_manager=None
    ):
        """
        Lädt ein Projekt.
        """

        with open(
            filename,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        # -----------------------------------------------------
        # Versionsprüfung
        # -----------------------------------------------------

        version = data.get("version")

        if version != ProjectSerializer.VERSION:

            raise ValueError(
                f"Nicht unterstützte Projektversion: {version}"
            )    

        # -----------------------------------------------------
        # Projektinformationen
        # -----------------------------------------------------

        project_data = data.get(
            "project",
            {}
        )

        project.name = project_data.get(
            "name",
            project.name
        )

        project.author = project_data.get(
            "author",
            project.author
        )

        project.description = project_data.get(
            "description",
            project.description
        )

        project.created = project_data.get(
            "created",
            project.created
        )

        project.modified = project_data.get(
            "modified",
            project.modified
        )

        project.heightmap_export_path = project_data.get(
            "heightmap_export_path",
            ""
        )

        project.heightmap_exported_at = project_data.get(
            "heightmap_exported_at",
            ""
        )

        # -----------------------------------------------------
        # Layer
        # -----------------------------------------------------

        if layer_manager is not None:

            layer_manager.from_dict(
                data.get(
                    "layers",
                    {}
                )
            )

        # -----------------------------------------------------
        # OSM
        # -----------------------------------------------------

        osm_data = data.get(
            "osm"
        )

        if osm_data:

            project.set_osm_data(
                OSMData.from_dict(
                    osm_data
                )
            )

        else:

            project.clear_osm_data()

        # -----------------------------------------------------
        # Marker
        # -----------------------------------------------------

        project.clear_markers()

        for marker_data in data.get(
            "markers",
            []
        ):

            marker = Marker(

                id=marker_data.get(
                    "id",
                    ""
                ),

                lat=marker_data.get(
                    "lat",
                    0.0
                ),

                lon=marker_data.get(
                    "lon",
                    0.0
                ),

                text=marker_data.get(
                    "text",
                    ""
                )

            )

            project.add_marker(
                marker
            )

        # -----------------------------------------------------
        # Polylines
        # -----------------------------------------------------

        project.clear_polylines()

        for polyline_data in data.get(
            "polylines",
            []
        ):

            polyline = Polyline(

                id=polyline_data.get(
                    "id",
                    ""
                ),

                text=polyline_data.get(
                    "text",
                    ""
                ),

                points=polyline_data.get(
                   "points",
                    []
                ),

                properties=polyline_data.get(
                    "properties",
                    {}
                )
            )

            project.add_polyline(
                polyline
            )

        # -----------------------------------------------------
        # Polygone
        # -----------------------------------------------------

        project.clear_polygons()

        for polygon_data in data.get(
            "polygons",
            []
        ):

            polygon = {

                "id": polygon_data.get(
                    "id",
                    ""
                ),

                "text": polygon_data.get(
                    "text",
                    ""
                ),

                "points": polygon_data.get(
                    "points",
                    []
                ),

                "properties": polygon_data.get(
                    "properties",
                    {}
                )

            }

            project.add_polygon(
                polygon
            )

        # -----------------------------------------------------
        # Auswahl
        # -----------------------------------------------------

        selection_data = data.get(
            "selection"
        )

        if selection_data is None:

            project.clear_selection()

        else:

            selection = Selection(

                min_lat=selection_data.get(
                    "min_lat",
                    0.0
                ),

                min_lon=selection_data.get(
                    "min_lon",
                    0.0
                ),

                max_lat=selection_data.get(
                    "max_lat",
                    0.0
                ),

                max_lon=selection_data.get(
                    "max_lon",
                    0.0
                ),

                # Neu (Rechteck-Tool): fehlen diese Felder in einer
                # alten Projektdatei, ergibt .get() automatisch die
                # abwaertskompatiblen Defaults (unrotierte Bbox).
                rotation_deg=selection_data.get(
                    "rotation_deg",
                    0.0
                ),

                width_m=selection_data.get(
                    "width_m"
                ),

                height_m=selection_data.get(
                    "height_m"
                ),

                center_lat=selection_data.get(
                    "center_lat"
                ),

                center_lon=selection_data.get(
                    "center_lon"
                )

            )

            project.set_selection(
                selection
            )