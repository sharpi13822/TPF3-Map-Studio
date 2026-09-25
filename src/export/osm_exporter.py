from src.export.export_data import ExportData
from src.export.export_item import ExportItem


class OSMExporter:
    """
    Überführt vorhandene OSM-Daten in eine einheitliche Exportstruktur.
    """

    def export(
        self,
        osm,
    ) -> ExportData:

        data = ExportData()

        self._export_roads(
            osm,
            data,
        )

        self._export_railways(
            osm,
            data,
        )

        self._export_buildings(
            osm,
            data,
        )

        self._export_water(
            osm,
            data,
        )

        self._export_waterways(
            osm,
            data,
        )

        self._export_parks(
            osm,
            data,
        )

        self._export_landuse(
            osm,
            data,
        )

        self._export_vegetation(
            osm,
            data,
        )

        return data

    # ---------------------------------------------------------
    # Roads
    # ---------------------------------------------------------

    def _export_roads(
        self,
        osm,
        data,
    ):

        for obj in osm.highways():

            item = self._create_item(
                osm,
                obj,
                "polyline",
            )

            if item is not None:
                data.roads.append(
                    item
                )

    # ---------------------------------------------------------
    # Railways
    # ---------------------------------------------------------

    def _export_railways(
        self,
        osm,
        data,
    ):

        for obj in osm.railways():

            item = self._create_item(
                osm,
                obj,
                "polyline",
            )

            if item is not None:
                data.railways.append(
                    item
                )

    # ---------------------------------------------------------
    # Buildings
    # ---------------------------------------------------------

    def _export_buildings(
        self,
        osm,
        data,
    ):

        for obj in osm.buildings():

            item = self._create_item(
                osm,
                obj,
                "polygon",
            )

            if item is not None:
                data.buildings.append(
                    item
                )

    # ---------------------------------------------------------
    # Water
    # ---------------------------------------------------------

    def _export_water(
        self,
        osm,
        data,
    ):

        for obj in osm.water():

            item = self._create_item(
                osm,
                obj,
                "polygon",
            )

            if item is not None:
                data.water.append(
                    item
                )

    # ---------------------------------------------------------
    # Waterways
    # ---------------------------------------------------------

    def _export_waterways(
        self,
        osm,
        data,
    ):

        for obj in osm.waterways():

            item = self._create_item(
                osm,
                obj,
                "polyline",
            )

            if item is not None:
                data.waterways.append(
                    item
                )

    # ---------------------------------------------------------
    # Parks
    # ---------------------------------------------------------

    def _export_parks(
        self,
        osm,
        data,
    ):

        for obj in osm.parks():

            item = self._create_item(
                osm,
                obj,
                "polygon",
            )

            if item is not None:
                data.parks.append(
                    item
                )

    # ---------------------------------------------------------
    # Landuse
    # ---------------------------------------------------------

    def _export_landuse(
        self,
        osm,
        data,
    ):

        for obj in osm.landuse():

            item = self._create_item(
                osm,
                obj,
                "polygon",
            )

            if item is not None:
                data.landuse.append(
                    item
                )

    # ---------------------------------------------------------
    # Vegetation
    # ---------------------------------------------------------

    def _export_vegetation(
        self,
        osm,
        data,
    ):

        for obj in osm.vegetation():

            item = self._create_item(
                osm,
                obj,
                "polygon",
            )

            if item is not None:
                data.vegetation.append(
                    item
                )

    # ---------------------------------------------------------
    # Hilfsmethode
    # ---------------------------------------------------------

    def _create_item(
        self,
        osm,
        obj,
        geometry_type,
    ):

        geometry = osm.get_geometry(
            obj.id
        )

        if geometry is None:
            return None

        return ExportItem(
            id=obj.id,
            type=geometry_type,
            geometry=geometry,
            properties=dict(
                getattr(
                    obj,
                    "tags",
                    {},
                )
            ),
        )