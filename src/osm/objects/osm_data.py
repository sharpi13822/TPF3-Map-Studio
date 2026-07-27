from dataclasses import dataclass, field

from src.osm.objects.node import Node
from src.osm.objects.way import Way
from src.osm.objects.relation import Relation

from src.osm.osm_filter import OSMFilter


@dataclass(slots=True)
class OSMData:
    """
    Enthält sämtliche OSM-Daten eines Downloads.
    """

    nodes: dict[int, Node] = field(default_factory=dict)

    ways: dict[int, Way] = field(default_factory=dict)

    relations: dict[int, Relation] = field(default_factory=dict)

    #
    # Geometry Cache
    #
    geometry_cache: dict[int, object] = field(
        default_factory=dict
    )

    # ---------------------------------------------------------
    # Hinzufügen
    # ---------------------------------------------------------

    def add_node(self, node: Node):

        self.nodes[node.id] = node

    def add_way(self, way: Way):

        self.ways[way.id] = way

    def add_relation(self, relation: Relation):

        self.relations[relation.id] = relation

    # ---------------------------------------------------------
    # Geometry Cache
    # ---------------------------------------------------------

    def get_geometry(self, object_id):

        return self.geometry_cache.get(object_id)

    def set_geometry(
        self,
        object_id,
        geometry,
    ):

        self.geometry_cache[object_id] = geometry

    def clear_geometry(self):

        self.geometry_cache.clear()

    # ---------------------------------------------------------
    # Statistiken
    # ---------------------------------------------------------

    @property
    def node_count(self):

        return len(self.nodes)

    @property
    def way_count(self):

        return len(self.ways)

    @property
    def relation_count(self):

        return len(self.relations)

    # ---------------------------------------------------------
    # Filter
    # ---------------------------------------------------------

    def highways(self):
        return OSMFilter.highways(self)

    def buildings(self):
        return OSMFilter.buildings(self)

    def railways(self):
        return OSMFilter.railways(self)

    def parks(self):
        return OSMFilter.parks(self)

    def landuse(self):
        return OSMFilter.landuse(self)

    def vegetation(self):
        return OSMFilter.vegetation(self)

    def water(self):
        return OSMFilter.water(self)

    def waterways(self):
        return OSMFilter.waterways(self)

    # ---------------------------------------------------------

    def clear(self):

        self.nodes.clear()

        self.ways.clear()

        self.relations.clear()

        self.geometry_cache.clear()