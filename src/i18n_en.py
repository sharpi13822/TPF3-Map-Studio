"""Englische Uebersetzung (Schluessel = deutscher Originaltext).

Neue Texte im Programm: ``tr("Deutscher Text")`` schreiben und hier den
englischen Eintrag ergaenzen. ``tests/test_i18n.py`` meldet fehlende
Eintraege und Platzhalter ({name}), die in beiden Sprachen nicht
uebereinstimmen. Schreibweise: britisches Englisch wie in README.en.md.
"""

CATALOG = {
    'Aktuelles Projekt schließen und mit einem leeren Projekt weiterarbeiten':
        'Close the current project and continue with an empty project',
    'Auswahl':
        'Select',
    'Beenden':
        'Exit',
    'Bereich auswählen':
        'Select area',
    'Gedrehtes Kartenband anlegen (Mittelpunkt, Größe, Drehwinkel)':
        'Create a rotated map area (centre, size, rotation angle)',
    'Koordinaten-Messwerkzeug':
        'Coordinate measuring tool',
    'Marker':
        'Marker',
    'Marker setzen':
        'Place marker',
    'Neu':
        'New',
    'Neues Projekt':
        'New project',
    'Projekt schließen':
        'Close project',
    'Projekt speichern':
        'Save project',
    'Projekt unter neuem Namen speichern':
        'Save project under a new name',
    'Projekt öffnen':
        'Open project',
    'Rechteck-Tool':
        'Rectangle tool',
    'Rückgängig':
        'Undo',
    'Speichern':
        'Save',
    'Speichern unter...':
        'Save as...',
    'Wiederholen':
        'Redo',
    'Zwei Punkte anklicken, um lat/lon und Distanz anzuzeigen':
        'Click two points to show lat/lon and distance',
    'Öffnen':
        'Open',
    'Breite:':
        'Latitude:',
    'Eigenschaften':
        'Properties',
    'ID:':
        'ID:',
    'Länge:':
        'Longitude:',
    'Marker löschen':
        'Delete marker',
    'Name:':
        'Name:',
    'Projekt':
        'Project',
    'Layer':
        'Layers',
    'Deckkraft zurücksetzen':
        'Reset opacity',
    'Ebene nach oben (vor die anderen)':
        'Move layer up (in front of the others)',
    'Ebene nach unten (hinter die anderen)':
        'Move layer down (behind the others)',
    'Ebene sperren: keine Auswahl und Bearbeitung in der Karte':
        'Lock layer: no selection or editing on the map',
    'Layer anzeigen':
        'Show layer',
    'Layer ausblenden':
        'Hide layer',
    'Layer entsperren':
        'Unlock layer',
    'Layer sperren':
        'Lock layer',
    'Werkzeuge':
        'Tools',
    'Straßen':
        'Roads',
    'Bahn':
        'Railways',
    'Gebäude':
        'Buildings',
    'Wasser':
        'Water',
    'Flüsse':
        'Rivers',
    'Parks':
        'Parks',
    'Landnutzung':
        'Land use',
    'Vegetation':
        'Vegetation',
    'Bahnhöfe':
        'Stations',
    ', Drehung {deg:.2f}°':
        ', rotation {deg:.2f}°',
    'Ansicht':
        'View',
    'Auf Marker zentrieren':
        'Centre on marker',
    'Bearbeiten':
        'Edit',
    'Bereit':
        'Ready',
    'Bitte warten, bis der OSM-Download fertig ist.':
        'Please wait until the OSM download has finished.',
    'Bitte zuerst mit dem Rechteck-Tool einen Kartenausschnitt festlegen.':
        'Please define a map area with the rectangle tool first.',
    'Converter-Befehl anzeigen...':
        'Show converter command...',
    'Das Projekt wurde geändert.\n\nVor dem Beenden speichern?':
        'The project has been changed.\n\nSave before exiting?',
    'Das Projekt wurde geändert.\n\nVorher speichern?':
        'The project has been changed.\n\nSave first?',
    'Datei':
        'File',
    'Die Karte konnte nicht geladen werden.':
        'The map could not be loaded.',
    "Es sind keine OSM-Daten geladen. Zuerst 'OSM laden' ausführen (Werkzeuge-Menü).":
        "No OSM data is loaded. Run 'Load OSM' first (Tools menu).",
    'Export fehlgeschlagen':
        'Export failed',
    'Fehler':
        'Error',
    'Funktionsübersicht...':
        'Feature overview...',
    'Heightmap herunterladen':
        'Download heightmap',
    'Hilfe':
        'Help',
    'Import-Anleitung...':
        'Import guide...',
    'Kartenband gesetzt: {width:.3f} x {height:.3f} km, Drehung {deg:.2f}°':
        'Map area set: {width:.3f} x {height:.3f} km, rotation {deg:.2f}°',
    'Keine Auswahl':
        'No selection',
    'Keine OSM-Daten':
        'No OSM data',
    'Kurze Verbindungssegmente...':
        'Short connection segments...',
    'Löschen':
        'Delete',
    'Marker: {id} | {lat:.6f}, {lon:.6f}':
        'Marker: {id} | {lat:.6f}, {lon:.6f}',
    'Messung: ersten Punkt anklicken':
        'Measurement: click the first point',
    'Mod-Checker...':
        'Mod checker...',
    'Neues Projekt.':
        'New project.',
    'OSM als .osm exportieren...':
        'Export OSM as .osm...',
    'OSM geladen: {nodes} Nodes, {ways} Ways, {relations} Relations{rotation}':
        'OSM loaded: {nodes} nodes, {ways} ways, {relations} relations{rotation}',
    'OSM laden':
        'Load OSM',
    'OSM-Datei exportieren':
        'Export OSM file',
    'OSM-Datei exportiert: {filename}':
        'OSM file exported: {filename}',
    'OSM-Dateien (*.osm)':
        'OSM files (*.osm)',
    'OSM-Daten werden geladen... Drehung {deg:.2f}°, {filter}':
        'Loading OSM data... rotation {deg:.2f}°, {filter}',
    'OSM-Download fehlgeschlagen.':
        'OSM download failed.',
    'OSM-Download fehlgeschlagen: {message}':
        'OSM download failed: {message}',
    'OSM-Download läuft':
        'OSM download in progress',
    'Overpass-Abfrage...':
        'Overpass query...',
    'Projekt geladen.':
        'Project loaded.',
    'Projekt gespeichert.':
        'Project saved.',
    'Projekt konnte nicht geladen werden.\n\n{error}':
        'The project could not be loaded.\n\n{error}',
    'Projekt konnte nicht gespeichert werden.\n\n{error}':
        'The project could not be saved.\n\n{error}',
    'Projekt speichern unter':
        'Save project as',
    'Projekt-Dashboard...':
        'Project dashboard...',
    'Projekteigenschaften':
        'Project properties',
    'Projekteigenschaften...':
        'Project properties...',
    'Projektname geändert: {name}':
        'Project name changed: {name}',
    'Projektname:':
        'Project name:',
    'Umbenennen':
        'Rename',
    'Vorab-Prüfung...':
        'Pre-check...',
    'Werkzeug: Koordinaten-Messwerkzeug':
        'Tool: Coordinate measuring tool',
    'Werkzeug: Marker':
        'Tool: Marker',
    'Werkzeug: {name}':
        'Tool: {name}',
    'gedrehtes Polygon (poly-Filter)':
        'rotated polygon (poly filter)',
    'ungedrehte Box':
        'unrotated box',
    '{count} Bahnhöfe auf der Karte (Ebene Bahnhöfe)':
        '{count} stations on the map (Stations layer)',
    '{message}, {count} Bahnhöfe':
        '{message}, {count} stations',
    # Hilfetext des Layer-Panels (window.py: LAYER_HELP_HTML)
    """
<p><b>So funktioniert das Layer-Panel</b></p>

<p><b>Haken:</b> blendet die Ebene auf der Karte ein oder aus.
Beim Start sind alle Ebenen aus. Erst <i>Werkzeuge &rarr; OSM
laden</i>, dann die gewünschten Haken setzen. Die Ebene
<i>Bahnhöfe</i> schaltet das Studio nach dem Laden selbst ein.</p>

<p><b>Schloss:</b> sperrt die Ebene. Ihre Objekte lassen sich in der
Karte dann nicht mehr anklicken oder bearbeiten, so greifst du nicht
versehentlich daneben.</p>

<p><b>Balken:</b> stellt die Deckkraft der Ebene ein. Nach links
ziehen macht sie durchsichtiger, ganz rechts ist sie voll
sichtbar. So siehst du Ebenen, die darunter liegen.</p>

<p><b>Pfeile:</b> verschieben die Ebene in der Stapelreihenfolge
auf der Karte. Pfeil hoch legt sie vor die anderen Ebenen, Pfeil
runter dahinter. Praktisch, wenn zum Beispiel Wald die Straßen
verdeckt.</p>

<p><b>Rechtsklick</b> auf eine Zeile: Ebene anzeigen, ausblenden,
sperren, entsperren oder die Deckkraft zurücksetzen.</p>

<p><b>Tipp:</b> Ein Klick auf ein Objekt auf der Karte zeigt seine
Eckpunkte. Die Punkte lassen sich ziehen. Ein Klick ins Leere oder
die Esc-Taste beendet das.</p>
""":
        """
<p><b>How the layer panel works</b></p>

<p><b>Tick box:</b> shows or hides the layer on the map.
All layers are off at the start. First use <i>Tools &rarr; Load
OSM</i>, then tick the layers you want. The <i>Stations</i> layer
is switched on by the Studio itself after loading.</p>

<p><b>Lock:</b> locks the layer. Its objects can then no longer be
clicked or edited on the map, so you don't touch them by
accident.</p>

<p><b>Slider:</b> sets the opacity of the layer. Dragging it left
makes the layer more transparent, all the way to the right it is
fully visible. This lets you see layers that lie underneath.</p>

<p><b>Arrows:</b> move the layer in the stacking order on the map.
The up arrow puts it in front of the other layers, the down arrow
behind them. Handy if, for example, forest covers the roads.</p>

<p><b>Right-click</b> on a row: show, hide, lock or unlock the
layer, or reset its opacity.</p>

<p><b>Tip:</b> Clicking an object on the map shows its vertices.
The points can be dragged. Clicking on empty space or pressing the
Esc key ends this.</p>
""",
}
