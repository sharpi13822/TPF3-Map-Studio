"""Englische Uebersetzung der Kartenoberflaeche (src/map/web).

Schluessel = deutscher Originaltext, wie in src/i18n_en.py. Der Server
liefert dieses Woerterbuch als i18n_data.js an die Karte (siehe
src/core/server.py und src/map/web/js/i18n.js). Ein Schluessel in
runden Klammern wie "Gebäude (Zeichenknopf)" ist ein eigener Name
(data-i18n in index.html) fuer einen Text, der an anderer Stelle anders
uebersetzt wird.
"""

WEB_CATALOG = {
    'Layer':
        'Layers',
    'Alle Ebenen im Panel einschalten':
        'Switch on all layers in the panel',
    'Alle':
        'All',
    'Alle Ebenen im Panel ausschalten':
        'Switch off all layers in the panel',
    'Keine':
        'None',
    'Speichert die Objekte der Karte als JSON-Datei':
        'Saves the objects on the map as a JSON file',
    'JSON Export':
        'JSON Export',
    'Lädt eine gespeicherte JSON-Datei auf die Karte':
        'Loads a saved JSON file onto the map',
    'JSON Import':
        'JSON Import',
    'Zeichnen':
        'Draw',
    'Eigene Straße zeichnen: Punkte auf der Karte anklicken, dann Fertig':
        'Draw your own road: click points on the map, then Done',
    'Straße':
        'Road',
    'Eigenen Fluss zeichnen: Punkte auf der Karte anklicken, dann Fertig':
        'Draw your own river: click points on the map, then Done',
    'Fluss':
        'River',
    'Eigenes Gebäude zeichnen: Punkte auf der Karte anklicken, dann Fertig':
        'Draw your own building: click points on the map, then Done',
    'Gebäude (Zeichenknopf)':
        'Building',
    'Zeichnen beenden und das Objekt übernehmen':
        'Finish drawing and accept the object',
    'Fertig':
        'Done',
    'Kartenquelle':
        'Map source',
    'Normale Straßenkarte als Hintergrund':
        'Standard road map as background',
    'OpenStreetMap':
        'OpenStreetMap',
    'Straßenkarte mit Schattenrelief':
        'Road map with hillshade',
    'Karte + Relief':
        'Map + relief',
    'Legt die OpenRailwayMap über die Karte: Gleise, Bahnhöfe und Signale':
        'Overlays the OpenRailwayMap on the map: tracks, stations and signals',
    'Eisenbahnkarte (ORM)':
        'Railway map (ORM)',
    'Blendet ein Gitter über die Karte ein, mit dem sich Abstände und Größen abschätzen lassen':
        'Shows a grid over the map for estimating distances and sizes',
    'Maß-Gitter':
        'Measuring grid',
    'Objekt Information':
        'Object information',
    'Kein Objekt ausgewählt':
        'No object selected',
    'Bearbeiten':
        'Edit',
    'Löschen':
        'Delete',
    'Keine Eigenschaften':
        'No properties',
    'Layer:':
        'Layer:',
    'Typ:':
        'Type:',
    'Punkte:':
        'Points:',
    'Eigenschaften:':
        'Properties:',
    'Eigenschaften bearbeiten':
        'Edit properties',
    'Speichern':
        'Save',
    'Objekt wirklich löschen?':
        'Really delete this object?',
    'Linie':
        'Line',
    'Polygon':
        'Polygon',
    'Multipolygon':
        'Multipolygon',
    'Rechteck':
        'Rectangle',
    'Kreis':
        'Circle',
    'Straßen':
        'Roads',
    'Bahnstrecken':
        'Railway lines',
    'Gebäude':
        'Buildings',
    'Gewässer':
        'Water bodies',
    'Flüsse':
        'Rivers',
    'Parks':
        'Parks',
    'Landnutzung':
        'Land use',
    'Vegetation':
        'Vegetation',
    'Auswahl':
        'Selection',
    'Name':
        'Name',
    'Typ':
        'Type',
    'Referenz':
        'Reference',
    'Höchstgeschwindigkeit':
        'Maximum speed',
    'Einbahnstraße':
        'One-way street',
    'Brücke':
        'Bridge',
    'Tunnel':
        'Tunnel',
    'Oberfläche':
        'Surface',
    'Fahrstreifen':
        'Lanes',
    "Ebene '{layer}' ist gesperrt":
        "Layer '{layer}' is locked",
    'Eckpunkte: {count}':
        'Vertices: {count}',
    ' (nicht bearbeitbar, Geometrie: {geometry})':
        ' (not editable, geometry: {geometry})',
    ' (von {total} Punkten liegen {outside} außerhalb des Bildes)':
        ' (of {total} points, {outside} are outside the view)',
    'Ausgewählt: {layer} {id} ({type}), {detail}':
        'Selected: {layer} {id} ({type}), {detail}',
    'Fehler bei der Auswahl: {message}':
        'Selection error: {message}',
    'Neues Objekt':
        'New object',
    'Rückgängig/Wiederholen gibt es nur für eigene Objekte, nicht für OSM-Objekte.':
        'Undo/redo is only available for your own objects, not for OSM objects.',
    'Relief: AWS Terrain Tiles (Mapzen/Tilezen; Quellen u.a. SRTM, Copernicus, siehe github.com/tilezen/joerd)':
        'Relief: AWS Terrain Tiles (Mapzen/Tilezen; sources include SRTM, Copernicus, see github.com/tilezen/joerd)',
    'Relief konnte nicht berechnet werden: {message}':
        'Relief could not be calculated: {message}',
    '© OpenStreetMap-Mitwirkende':
        '© OpenStreetMap contributors',
    'Daten © OpenStreetMap-Mitwirkende, Stil: CC-BY-SA 2.0 ':
        'Data © OpenStreetMap contributors, style: CC-BY-SA 2.0 ',
}
