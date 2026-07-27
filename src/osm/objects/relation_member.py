from dataclasses import dataclass


@dataclass(slots=True)
class RelationMember:
    """
    Mitglied einer OSM-Relation.
    """

    type: str
    ref: int
    role: str