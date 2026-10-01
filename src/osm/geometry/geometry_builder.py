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

    def rebuild_for_nodes(self, node_ids):
        """
        Baut nur die Geometrien neu auf, die von den angegebenen Nodes
        abhaengen (Ways und Relationen, die diese Ways verwenden).
        Gibt die IDs der neu aufgebauten Objekte zurueck.
        """

        node_ids = set(node_ids)

        ways = {
            way.id
            for way in self.osm.ways.values()
            if node_ids.intersection(way.nodes)
        }

        return self.rebuild_for_ways(ways)

    def rebuild_for_ways(self, way_ids):
        """
        Baut die Geometrie der angegebenen Ways und der Relationen, die
        sie verwenden, neu auf. Gibt die IDs der neu aufgebauten Objekte
        zurueck.
        """

        ways = set(way_ids)

        rebuilt = set()

        for way_id in ways:

            geometry = self._build_way(self.osm.ways[way_id])

            if geometry is not None:

                self.osm.set_geometry(way_id, geometry)

                rebuilt.add(way_id)

        for relation in self.osm.relations.values():

            if not any(
                member.type == "way" and member.ref in ways
                for member in relation.members
            ):
                continue

            geometry = self.polygons.build(relation)

            if geometry is not None:

                self.osm.set_geometry(relation.id, geometry)

                rebuilt.add(relation.id)

        return rebuilt

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