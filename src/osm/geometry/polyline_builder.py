class PolylineBuilder:
    """
    Erzeugt Polylinien aus OSM-Ways.
    """

    def __init__(self, osm):
        self.osm = osm

    # ---------------------------------------------------------

    def build(self, way):

        coordinates = []

        for node_id in way.nodes:

            node = self.osm.nodes.get(node_id)

            if node is None:
                continue

            coordinates.append(
                (
                    node.lat,
                    node.lon,
                )
            )

        return coordinates