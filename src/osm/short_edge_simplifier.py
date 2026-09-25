"""
Erkennung und sichere Vereinfachung sehr kurzer Wegsegmente, insbesondere
bei "_link"-Typen (Autobahn-/Straßen-Ab-/Auffahrten).

Hintergrund: Eine Analyse eines echten SimpleProposalSeq-Laufs zeigte,
dass fehlgeschlagene secondary_link-Kanten im Median ~6.9m lang waren,
erfolgreiche dagegen ~23.1m - fehlgeschlagene Kanten sind also im Schnitt
etwa dreimal kürzer. Ob das Kürzen dieser Segmente die TPF2-Bauversuche
tatsächlich zuverlässiger macht, ist eine Hypothese (siehe die reale
Korrelation), keine bewiesene Ursache - deshalb liefert dieses Modul erst
einmal einen Bericht (nichts wird automatisch verändert) und erst auf
Wunsch eine vereinfachte Kopie zum Export.

WICHTIG zur Sicherheit: Nur Knoten werden entfernt, die garantiert KEINE
echte Kreuzung sind - also Knoten, die
  (a) nicht der erste/letzte Knoten ihres Weges sind (Wegenden sind
      typischerweise Verbindungsstellen zu anderen Wegen), UND
  (b) von keinem anderen Weg referenziert werden (sonst läge dort eine
      Kreuzung mit einer anderen Straße).
Solche Knoten sind reine "Formpunkte" innerhalb eines einzelnen Weges -
sie zu entfernen ändert nur die Detailgeometrie dieses einen Weges, nie
die Topologie (welche Straßen sich wo treffen). Kreuzungsknoten werden
NIE entfernt, auch nicht, wenn die anliegenden Segmente kurz sind.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from src.osm.objects.osm_data import OSMData
from src.osm.objects.way import Way


DEFAULT_THRESHOLD_M = 10.0

DEFAULT_LINK_TYPES = frozenset({
    "motorway_link",
    "trunk_link",
    "primary_link",
    "secondary_link",
    "tertiary_link",
})


@dataclass
class ShortSegment:
    way_id: int
    highway_type: str
    node0: int
    node1: int
    length_m: float


@dataclass
class SimplificationReport:
    short_segments: list[ShortSegment] = field(default_factory=list)
    removable_nodes: set[int] = field(default_factory=set)
    affected_way_ids: set[int] = field(default_factory=set)


def _distance_m(osm: OSMData, n0: int, n1: int) -> float | None:
    """
    Grobe, aber fuer die hier relevanten kurzen Distanzen (wenige zehn
    Meter) voellig ausreichend genaue Meter-Naeherung zwischen zwei
    Knoten (aequirektangulaere Projektion).
    """

    node0 = osm.nodes.get(n0)
    node1 = osm.nodes.get(n1)

    if node0 is None or node1 is None:
        return None

    center_lat = (node0.lat + node1.lat) / 2

    dx = (node1.lon - node0.lon) * 111_320 * math.cos(math.radians(center_lat))
    dy = (node1.lat - node0.lat) * 111_320

    return math.hypot(dx, dy)


def _node_way_counts(osm: OSMData) -> dict[int, int]:
    """Zaehlt, in wie vielen verschiedenen Wegen jeder Knoten vorkommt."""

    counts: dict[int, int] = {}

    for way in osm.ways.values():
        for node_id in set(way.nodes):
            counts[node_id] = counts.get(node_id, 0) + 1

    return counts


def analyze_short_segments(
    osm: OSMData,
    link_types: frozenset[str] = DEFAULT_LINK_TYPES,
    threshold_m: float = DEFAULT_THRESHOLD_M,
) -> SimplificationReport:
    """
    Findet alle zu kurzen Segmente bei den angegebenen highway-Typen UND
    die Knoten, die sich sicher entfernen liessen, um sie zu vereinfachen.
    Veraendert nichts - reine Analyse.
    """

    report = SimplificationReport()

    way_counts = _node_way_counts(osm)

    for way in osm.ways.values():

        highway = way.tags.get("highway")

        if highway not in link_types:
            continue

        nodes = way.nodes

        # -------------------------------------------------
        # Kurze Segmente erfassen (rein informativ)
        # -------------------------------------------------

        for i in range(len(nodes) - 1):

            length = _distance_m(osm, nodes[i], nodes[i + 1])

            if length is not None and length < threshold_m:

                report.short_segments.append(ShortSegment(
                    way_id=way.id,
                    highway_type=highway,
                    node0=nodes[i],
                    node1=nodes[i + 1],
                    length_m=length,
                ))
                report.affected_way_ids.add(way.id)

        # -------------------------------------------------
        # Sicher entfernbare Formpunkt-Knoten ermitteln
        # -------------------------------------------------

        if len(nodes) < 3:
            continue  # nichts zu vereinfachen (nur ein Segment)

        for i in range(1, len(nodes) - 1):  # nie erster/letzter Knoten

            node_id = nodes[i]

            if way_counts.get(node_id, 0) != 1:
                continue  # gehoert zu >1 Weg -> echte Kreuzung, nie anfassen

            prev_len = _distance_m(osm, nodes[i - 1], node_id)
            next_len = _distance_m(osm, node_id, nodes[i + 1])

            if prev_len is None or next_len is None:
                continue

            if prev_len < threshold_m or next_len < threshold_m:
                report.removable_nodes.add(node_id)

    return report


def simplify_short_segments(
    osm: OSMData,
    node_ids_to_remove: set[int],
) -> OSMData:
    """
    Liefert eine NEUE OSMData-Kopie, in der die angegebenen Knoten aus
    allen Wegen entfernt sind. Das Original-Objekt (das im Studio
    geladene Projekt) wird NICHT veraendert - das ist bewusst so, damit
    ein Fehlversuch nichts an den echten Projektdaten kaputt macht.
    """

    new_osm = OSMData()

    for node_id, node in osm.nodes.items():

        if node_id not in node_ids_to_remove:
            new_osm.add_node(node)

    for way in osm.ways.values():

        new_nodes = [n for n in way.nodes if n not in node_ids_to_remove]

        if len(new_nodes) < 2:
            # Sollte durch die Sicherheitsbedingungen in
            # analyze_short_segments() nie vorkommen (Wegenden werden
            # nie entfernt) - als zusaetzliche Absicherung trotzdem:
            # im Zweifel den Weg unveraendert lassen statt ihn kaputt
            # zu machen.
            new_nodes = way.nodes

        new_osm.add_way(Way(
            id=way.id,
            nodes=new_nodes,
            tags=dict(way.tags),
        ))

    for relation in osm.relations.values():
        new_osm.add_relation(relation)

    return new_osm
