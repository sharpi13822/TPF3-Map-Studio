from dataclasses import dataclass, field

from src.osm.objects.node import Node
from src.osm.objects.way import Way
from src.osm.objects.relation import Relation
from src.osm.objects.relation_member import RelationMember

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
    # Serialisieren
    # ---------------------------------------------------------

    def to_dict(self):

        return {

            "nodes": [

                {
                    "id": node.id,
                    "lat": node.lat,
                    "lon": node.lon,
                    "tags": node.tags
                }

                for node in self.nodes.values()

            ],

            "ways": [

                {
                    "id": way.id,
                    "nodes": way.nodes,
                    "tags": way.tags
                }

                for way in self.ways.values()

            ],

            "relations": [

                {
                    "id": relation.id,

                    "members": [

                        {
                            "type": member.type,
                            "ref": member.ref,
                            "role": member.role
                        }

                        for member in relation.members

                    ],

                    "tags": relation.tags

                }

                for relation in self.relations.values()

            ]

        }

    @classmethod
    def from_dict(
        cls,
        data
    ):

        osm = cls()

        # -----------------------------------------------------
        # Nodes
        # -----------------------------------------------------

        for node_data in data.get(
            "nodes",
            []
        ):

            node = Node(

                id=node_data.get(
                    "id",
                    0
                ),

                lat=node_data.get(
                    "lat",
                    0.0
                ),

                lon=node_data.get(
                    "lon",
                    0.0
                ),

                tags=node_data.get(
                    "tags",
                    {}
                )

            )

            osm.add_node(
                node
            )

        # -----------------------------------------------------
        # Ways
        # -----------------------------------------------------

        for way_data in data.get(
            "ways",
            []
        ):

            way = Way(

                id=way_data.get(
                    "id",
                    0
                ),

                nodes=way_data.get(
                    "nodes",
                    []
                ),

                tags=way_data.get(
                    "tags",
                    {}
                )

            )

            osm.add_way(
                way
            )

        # -----------------------------------------------------
        # Relations
        # -----------------------------------------------------

        for relation_data in data.get(
            "relations",
            []
        ):

            members = []

            for member_data in relation_data.get(
                "members",
                []
            ):

                member = RelationMember(

                    type=member_data.get(
                        "type",
                        ""
                    ),

                    ref=member_data.get(
                        "ref",
                        0
                    ),

                    role=member_data.get(
                        "role",
                        ""
                    )

                )

                members.append(
                    member
                )

            relation = Relation(

                id=relation_data.get(
                    "id",
                    0
                ),

                members=members,

                tags=relation_data.get(
                    "tags",
                    {}
                )

            )

            osm.add_relation(
                relation
            )

        return osm

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

    def places(self):
        return OSMFilter.places(self)

    # ---------------------------------------------------------

    def clear(self):

        self.nodes.clear()

        self.ways.clear()

        self.relations.clear()

        self.geometry_cache.clear()