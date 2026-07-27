import json
from typing import TYPE_CHECKING
from src.map.objects.marker import Marker
from src.map.objects.selection import Selection

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
                "modified": project.modified

            },

            "layers": (
                layer_manager.to_dict()
                if layer_manager is not None
                else {}
            ),

            "markers": [
                {
                    "id": marker.id,
                    "lat": marker.lat,
                    "lon": marker.lon,
                    "text": marker.text
                }
                for marker in project.markers
            ],

            "selection": (
                {
                    "min_lat": project.selection.min_lat,
                    "min_lon": project.selection.min_lon,
                    "max_lat": project.selection.max_lat,
                    "max_lon": project.selection.max_lon
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
                )

            )

            project.set_selection(
                selection
            )
