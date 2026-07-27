from src.osm.objects.node import Node
from src.osm.objects.way import Way
from src.osm.objects.relation import Relation
from src.osm.objects.osm_data import OSMData
from src.osm.objects.relation_member import RelationMember

class OSMParser:
    """
    Wandelt Overpass-JSON in OSMData um.
    """

    def parse(
        self,
        data: dict
    ) -> OSMData:

        osm = OSMData()

        for element in data.get("elements", []):

            element_type = element.get("type")

            # -----------------------------------------
            # Node
            # -----------------------------------------

            if element_type == "node":

                node = Node(
                    id=element["id"],
                    lat=element["lat"],
                    lon=element["lon"],
                    tags=element.get("tags", {})
                )

                osm.add_node(node)

            # -----------------------------------------
            # Way
            # -----------------------------------------

            elif element_type == "way":

                way = Way(
                    id=element["id"],
                    nodes=element.get("nodes", []),
                    tags=element.get("tags", {})
                )

                osm.add_way(way)

            # -----------------------------------------
            # Relation
            # -----------------------------------------

            elif element_type == "relation":

                members = []

                for member in element.get("members", []):

                    members.append(
                        RelationMember(
                            type=member["type"],
                            ref=member["ref"],
                            role=member.get("role", "")
                        )
                    )

                relation = Relation(
                    id=element["id"],
                    members=members,
                    tags=element.get("tags", {})
                )

                osm.add_relation(relation)

        print("OSM Parser:")
        print(f"  Nodes     : {osm.node_count}")
        print(f"  Ways      : {osm.way_count}")
        print(f"  Relations : {osm.relation_count}")

        return osm