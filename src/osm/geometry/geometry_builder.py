from src.osm.geometry.polygon_builder import PolygonBuilder


class GeometryBuilder:
    """
    Erzeugt alle darstellbaren Geometrien des OSM-Modells.

    Linien:
        [
            (lat, lon),
            ...
        ]

    Polygone:
        [
            [
                outer,
                inner1,
                inner2,
            ],
            ...
        ]
    """

    def __init__(self, osm):

        self.osm = osm
        self.polygons = PolygonBuilder(osm)

    # ------------------------------------------------------------------
    # Öffentlich
    # ------------------------------------------------------------------

    def build(self):

        self.osm.clear_geometry()

        self._build_ways()
        self._build_relations()

    # ------------------------------------------------------------------
    # Ways
    # ------------------------------------------------------------------

    def _build_ways(self):

        for way in self.osm.ways.values():

            geometry = self._build_way(way)

            if geometry is None:
                continue

            self.osm.set_geometry(
                way.id,
                geometry,
            )

    # ------------------------------------------------------------------
    # Relationen
    # ------------------------------------------------------------------

    def _build_relations(self):

        for relation in self.osm.relations.values():

            geometry = self.polygons.build(
                relation
            )

            if geometry is None:
                continue

            self.osm.set_geometry(
                relation.id,
                geometry,
            )

    # ------------------------------------------------------------------
    # Einzelner Way
    # ------------------------------------------------------------------

    def _build_way(self, way):

        coordinates = []

        for node_id in way.nodes:

            node = self.osm.nodes.get(node_id)

            if node is None:
                continue

            point = (
                node.lat,
                node.lon,
            )

            #
            # Doppelte aufeinanderfolgende Punkte vermeiden.
            #
            if coordinates and coordinates[-1] == point:
                continue

            coordinates.append(point)

        if len(coordinates) < 2:
            return None

        #
        # Geschlossener Way → PolygonBuilder
        #
        if (
            len(coordinates) >= 4
            and coordinates[0] == coordinates[-1]
        ):
            return self.polygons.build(way)

        #
        # Offener Way → Polyline
        #
        return coordinates