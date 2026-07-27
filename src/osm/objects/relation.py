from dataclasses import dataclass, field

from src.osm.objects.relation_member import RelationMember


@dataclass(slots=True)
class Relation:
    """
    OpenStreetMap-Relation.
    """

    id: int

    members: list[RelationMember] = field(default_factory=list)

    tags: dict[str, str] = field(default_factory=dict)