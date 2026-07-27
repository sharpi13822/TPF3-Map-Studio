from src.osm.geometry.ring_assembler import RingAssembler
from src.osm.geometry.polygon_matcher import PolygonMatcher


class PolygonBuilder:
    """
    Erstellt Polygongeometrien aus OSM-Ways und Multipolygon-Relationen.

    Rückgabe:

        Way:
            [
                [
                    outer_ring
                ]
            ]

        Relation:
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
        self.assembler = RingAssembler()
        self.matcher = PolygonMatcher()

    # ------------------------------------------------------------------
    # Öffentlich
    # ------------------------------------------------------------------

    def build(self, obj):

        if hasattr(obj, "nodes"):
            return self._build_way(obj)

        if hasattr(obj, "members"):
            return self._build_relation(obj)

        return None

    # ------------------------------------------------------------------
    # Polygon-Way
    # ------------------------------------------------------------------

    def _build_way(self, way):

        ring = self._way_to_ring(
            way,
            close=True,
        )

        if ring is None:
            return None

        if len(ring) < 4:
            return None

        if ring[0] != ring[-1]:
            return None

        return [[ring]]

    # ------------------------------------------------------------------
    # Multipolygon
    # ------------------------------------------------------------------

    def _build_relation(self, relation):

        if relation.tags.get("type") != "multipolygon":
            return None

        outer_segments = []
        inner_segments = []

        for member in relation.members:

            if member.type != "way":
                continue

            way = self.osm.ways.get(member.ref)

            if way is None:
                continue

            segment = self._way_to_ring(
                way,
                close=False,
            )

            if segment is None:
                continue

            #
            # Leere Rolle gilt als outer.
            #
            if member.role in ("", "outer"):

                outer_segments.append(segment)

            elif member.role == "inner":

                inner_segments.append(segment)

        outers = self.assembler.assemble(
            outer_segments
        )

        if not outers:
            return None

        inners = self.assembler.assemble(
            inner_segments
        )

        return self.matcher.assign(
            outers,
            inners,
        )

    # ------------------------------------------------------------------
    # Way -> Koordinatenring
    # ------------------------------------------------------------------

    def _way_to_ring(
        self,
        way,
        close=True,
    ):

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

        if (
            close
            and len(coordinates) >= 3
            and coordinates[0] != coordinates[-1]
        ):
            coordinates.append(
                coordinates[0]
            )

        return coordinates