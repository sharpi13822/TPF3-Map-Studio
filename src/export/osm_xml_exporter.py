"""
Export der aktuell geladenen OSM-Daten als Standard-OSM-XML-Datei.

Gleiches Format wie ein direkter Overpass-API-Export (out xml statt
out json) oder eine .osm-Datei von openstreetmap.org - fuer externe
Werkzeuge, die eine .osm-Datei als Eingabe erwarten.

Bewusst mit der Python-Standardbibliothek (xml.etree.ElementTree)
statt manueller String-Zusammensetzung, damit Tag-Werte mit
Sonderzeichen (&, <, >, Anfuehrungszeichen) automatisch korrekt
escaped werden.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from src.osm.objects.osm_data import OSMData


def export_osm_xml(
    osm: OSMData,
    output_path: Path,
    bounds: tuple[float, float, float, float] | None = None,
) -> None:
    """
    Schreibt eine Standard-OSM-XML-Datei (Version 0.6) mit allen
    aktuell geladenen Nodes, Ways und Relations.

    bounds: (min_lat, min_lon, max_lat, max_lon), falls angegeben.
    WICHTIG: Manche externen Werkzeuge (z.B. der OSM-TPF-Converter des
    OSM-TPF2-Importers) lesen die Kartengrenzen ausschliesslich aus
    diesem <bounds>-Element und pruefen zusaetzlich, dass die Datei mit
    einem <note>-Element beginnt - exakt wie es echte Overpass-API-
    ([out:xml])- bzw. openstreetmap.org-Exporte tun. Diese Elemente
    werden deshalb hier bewusst nachgebildet, auch wenn sie fuer die
    eigentlichen Kartendaten irrelevant sind.
    """

    root = ET.Element(
        "osm",
        version="0.6",
        generator="TPF2 Map Studio",
    )

    # Reihenfolge wie bei einem echten Overpass-API-XML-Export
    # (note -> meta -> bounds -> nodes -> ways -> relations), damit
    # Werkzeuge, die dieses Format strikt erwarten, die Datei akzeptieren.

    note_el = ET.SubElement(root, "note")
    note_el.text = (
        "The data included in this document is from "
        "www.openstreetmap.org. The data is made available under "
        "ODbL. (Diese Datei wurde von TPF2 Map Studio erzeugt.)"
    )

    ET.SubElement(root, "meta", osm_base="")

    if bounds is not None:

        min_lat, min_lon, max_lat, max_lon = bounds

        ET.SubElement(
            root,
            "bounds",
            minlat=f"{min_lat:.7f}",
            minlon=f"{min_lon:.7f}",
            maxlat=f"{max_lat:.7f}",
            maxlon=f"{max_lon:.7f}",
        )

    # Reihenfolge Nodes -> Ways -> Relations entspricht der OSM-Konvention
    # (Referenzen zeigen immer auf bereits weiter oben definierte Objekte).

    # Standard-OSM-XML-0.6-Attribute (siehe wiki.openstreetmap.org/wiki/OSM_XML),
    # die in einer echten OSM-API-/Overpass-Datei immer vorhanden sind, hier
    # aber inhaltlich bedeutungslos sind (kein echter Bearbeitungsverlauf) -
    # manche Parser (z.B. osmread) lesen sie trotzdem stur mit, deshalb
    # Platzhalterwerte statt sie wegzulassen:
    _COMMON_ATTRS = {
        "version": "1",
        "timestamp": "2024-01-01T00:00:00Z",
        "changeset": "1",
        "uid": "1",
        "user": "tpf2_map_studio",
        "visible": "true",
    }

    for node in osm.nodes.values():

        node_el = ET.SubElement(
            root,
            "node",
            id=str(node.id),
            lat=f"{node.lat:.7f}",
            lon=f"{node.lon:.7f}",
            **_COMMON_ATTRS,
        )

        for key, value in node.tags.items():
            ET.SubElement(node_el, "tag", k=key, v=str(value))

    for way in osm.ways.values():

        way_el = ET.SubElement(
            root, "way", id=str(way.id), **_COMMON_ATTRS,
        )

        for node_id in way.nodes:
            ET.SubElement(way_el, "nd", ref=str(node_id))

        for key, value in way.tags.items():
            ET.SubElement(way_el, "tag", k=key, v=str(value))

    for relation in osm.relations.values():

        relation_el = ET.SubElement(
            root, "relation", id=str(relation.id), **_COMMON_ATTRS,
        )

        for member in relation.members:

            ET.SubElement(
                relation_el,
                "member",
                type=member.type,
                ref=str(member.ref),
                role=member.role,
            )

        for key, value in relation.tags.items():
            ET.SubElement(relation_el, "tag", k=key, v=str(value))

    tree = ET.ElementTree(root)

    # Python 3.9+: formatiert die Ausgabe lesbar (Einrueckung), rein
    # kosmetisch - an der Gueltigkeit der Datei aendert das nichts.
    ET.indent(tree, space="  ")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    tree.write(
        output_path,
        encoding="UTF-8",
        xml_declaration=True,
    )
