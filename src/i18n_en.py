"""Englische Uebersetzung (Schluessel = deutscher Originaltext).

Neue Texte im Programm: ``tr("Deutscher Text")`` schreiben und hier den
englischen Eintrag ergaenzen. ``tests/test_i18n.py`` meldet fehlende
Eintraege und Platzhalter ({name}), die in beiden Sprachen nicht
uebereinstimmen. Schreibweise: britisches Englisch wie in README.en.md.
"""

CATALOG = {
    'Berechne Gelände...':
        'Calculating terrain...',
    'Berechnung abgebrochen.':
        'Calculation cancelled.',
    'Berechnung abgebrochen. Ändere eine Einstellung, um sie erneut zu starten.':
        'Calculation cancelled. Change a setting to start it again.',
    'Gelände berechnen':
        'Calculating terrain',
    'Höhen stauchen':
        'Compressing heights',
    'Höhenraster berechnen':
        'Calculating height grid',
    'Noch etwa {time}':
        'About {time} left',
    'Schreibe PNG-Datei...':
        'Writing PNG file...',
    'Terrain ans Wasser anpassen':
        'Adjusting terrain to water',
    'Wasser nach OSM einsetzen':
        'Applying water from OSM',
    'Wird abgebrochen... (der aktuelle Schritt wird noch beendet)':
        'Cancelling... (the current step is still being finished)',
    'Die Overpass-Server antworten seit längerer Zeit nicht. Bereits geladene Kacheln sind gespeichert. Starte den Download später erneut (am besten nachts oder morgens), dann werden nur die fehlenden Kacheln geladen.':
        'The Overpass servers have not been responding for a while. Tiles already downloaded are saved. Start the download again later (ideally at night or in the morning); only the missing tiles will be loaded.',
    '{count} von {total} Kacheln konnten nicht geladen werden. Die übrigen Kacheln sind gespeichert. Starte den Download später erneut, dann werden nur die fehlenden Kacheln geladen.':
        '{count} of {total} tiles could not be loaded. The other tiles are saved. Start the download again later; only the missing tiles will be loaded.',
    'Mausrad: zoomen. Mit gedrückter Maustaste ziehen: verschieben. Doppelklick: ganze Karte.':
        'Mouse wheel: zoom. Drag with the mouse button held: pan. Double-click: show the whole map.',
    'Eigene TPF2-Heightmap (PNG)':
        'Own TPF2 heightmap (PNG)',
    'TPF2-Heightmap':
        'TPF2 heightmap',
    'TPF2-Heightmap (PNG) wählen':
        'Choose TPF2 heightmap (PNG)',
    'Höhe in Metern für Schwarz (Min):':
        'Height in metres for black (min):',
    'Höhe in Metern für Weiß (Max):':
        'Height in metres for white (max):',
    'Max muss über Min liegen.':
        'Max must be above min.',
    'Die PNG ({w} x {h} Pixel) passt nicht zum Rechteck ({bw} x {bh} Pixel).':
        'The PNG ({w} x {h} pixels) does not match the rectangle ({bw} x {bh} pixels).',
    'Keine TPF2-Heightmap angegeben.':
        'No TPF2 heightmap specified.',
    'Aktuelles Projekt schließen und mit einem leeren Projekt weiterarbeiten':
        'Close the current project and continue with an empty project',
    'Auswahl':
        'Select',
    'Beenden':
        'Exit',
    'Bereich auswählen':
        'Select area',
    'Sehr viele Objekte: Die Karte zeigt je Ebene nur die wichtigsten (bei Fluessen und Strassen die groessten zuerst): {text}. Export und Berechnung nutzen weiterhin alle Daten. Fuer die volle Anzeige ein kleineres Rechteck waehlen.':
        'Very many objects: the map shows only the most important ones per layer (largest rivers and roads first): {text}. Export and calculations still use all data. Choose a smaller rectangle to show everything.',
    'Deckkraft der Ebene in Prozent': 'Layer opacity in percent',
    'Anleitung anzeigen': 'Show guide',
    'Anleitung ausblenden': 'Hide guide',
    'Verlauf ein- oder ausklappen': 'Expand or collapse the history',
    'Seitenleiste': 'Sidebar',
    'Seitenleiste (Projekt und Layer) ein- oder ausklappen (Strg+B)': 'Collapse or expand the sidebar (project and layers) (Ctrl+B)',
    'Seitenleiste einklappen': 'Collapse sidebar',
    'Seitenleiste ausklappen': 'Expand sidebar',
    'Eigenschaften-Leiste': 'Properties bar',
    'Eigenschaften-Panel ein- oder ausklappen (Strg+Umschalt+B)': 'Collapse or expand the properties panel (Ctrl+Shift+B)',
    'Eigenschaften einklappen': 'Collapse properties',
    'Eigenschaften ausklappen': 'Expand properties',
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
    'OSM-Laden abbrechen': 'Cancel OSM download',
    'OSM-Download wird abgebrochen...': 'Cancelling OSM download...',
    'OSM-Download abgebrochen. Die bisherigen Daten bleiben unverändert.': 'OSM download cancelled. The existing data is unchanged.',
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
    # Anleitung im rechten Dock (src/gui/docks.py: GUIDE_HTML)
    """
<h3>So arbeitest du mit dem Studio</h3>

<p><b>1. Bereich festlegen</b><br>
Zuerst sagst du dem Studio, welches Stück Land du brauchst.
Setze mit dem <i>Marker</i>-Werkzeug einen Marker in die Mitte des
gewünschten Gebiets. Öffne dann <i>Werkzeuge &rarr; Rechteck-Tool</i>
und wähle Kartengröße und Drehwinkel. Ein ausgewählter Marker
liefert den Mittelpunkt. Das blaue Rechteck zeigt, was später
geladen wird. Mit den beiden Punkten daran kannst du es
verschieben (blau) und drehen (orange).</p>

<p><b>2. Daten laden</b><br>
<i>Werkzeuge &rarr; OSM laden</i> holt Straßen, Gebäude, Gewässer und
mehr aus OpenStreetMap. Bei großen Gebieten kann das einige Minuten
dauern, die Statusleiste zeigt den Fortschritt. Was geladen wird,
stellst du unter <i>Werkzeuge &rarr; Overpass-Abfrage</i> ein.</p>

<p><b>3. Ebenen ein- und ausblenden</b><br>
Im Panel <i>Layer</i> auf der Karte bestimmst du mit den Haken,
was du siehst. Fahre mit der Maus über einen Eintrag, dann erscheint
eine kurze Erklärung.</p>
<ul>
<li><b>Straßen:</b> alle Straßen und Wege.</li>
<li><b>Bahn:</b> Bahnstrecken.</li>
<li><b>Gebäude:</b> alle Gebäudeumrisse.</li>
<li><b>Wasser:</b> Seen, Teiche und breite Flüsse als Fläche.</li>
<li><b>Flüsse:</b> Bäche und Flüsse als Linie.</li>
<li><b>Parks:</b> Parks und Gärten.</li>
<li><b>Landnutzung:</b> Felder, Wiesen, Obst- und Weinanbau,
Gärtnereien.</li>
<li><b>Vegetation:</b> Wälder und Baumreihen.</li>
<li><b>Bahnhöfe:</b> Bahnhöfe und Haltepunkte mit Namen, aus den
geladenen OSM-Daten. Die Namen erscheinen beim Hineinzoomen.</li>
</ul>
<p>Bei großen Gebieten kann die Karte langsam werden, wenn alles
gleichzeitig sichtbar ist. Dann blendest du einzelne Ebenen aus.</p>

<p><b>4. Hintergrundkarte wählen</b><br>
Unter <i>Kartenquelle</i> wechselst du zwischen der normalen
Straßenkarte (<i>OpenStreetMap</i>) und <i>Karte + Relief</i>. Das
Relief legt ein Schattenrelief darüber: Täler, Hänge und Bergkämme
werden sichtbar, das hilft beim Wählen des Ausschnitts. Die
<i>Eisenbahnkarte</i> legt Gleise und Bahnhöfe darüber, praktisch zum
Prüfen von Strecken. Das <i>Maß-Gitter</i>
hilft beim Abschätzen von Abständen und Größen.</p>

<p><b>5. Eigenes zeichnen</b><br>
Mit <i>Zeichnen</i> legst du eigene Objekte an:</p>
<ul>
<li>Zuerst auf <i>Straße</i>, <i>Fluss</i> oder <i>Gebäude</i> klicken.
Der Knopf bestimmt, was du zeichnest.</li>
<li>Dann die Punkte nacheinander auf der Karte anklicken. Eine rote
Linie zeigt den Verlauf.</li>
<li>Mit <i>Fertig</i> (oder einem Doppelklick) wird das Objekt
übernommen. Eine Straße und ein Fluss brauchen mindestens 2 Punkte,
ein Gebäude mindestens 3. Ein Gebäude schließt sich von selbst.</li>
<li>Nach <i>Fertig</i> ist das Zeichnen beendet. Für das nächste Objekt
wieder zuerst den Knopf (<i>Straße</i>, <i>Fluss</i> oder
<i>Gebäude</i>) anklicken.</li>
<li>Das Objekt liegt in der passenden Ebene (Straßen, Flüsse oder
Gebäude). Ist deren Haken im Layer-Panel aus, siehst du es nicht.</li>
<li>Ein Klick auf das Objekt zeigt seine Eckpunkte. Die Punkte lassen
sich ziehen.</li>
</ul>
<p><i>JSON Export</i> und <i>JSON Import</i> speichern und laden die
Objekte der Karte als Datei.</p>

<p><b>6. Werkzeuge</b><br>
In der Leiste oben wählst du, was ein Klick auf die Karte tut:
Marker setzen, zwei Ecken für eine Auswahl festlegen oder mit dem
Messwerkzeug Koordinaten und Entfernungen anzeigen.</p>

<p><b>7. Speichern und weiterverarbeiten</b><br>
Speichere dein Projekt mit <i>Datei &rarr; Speichern</i>. Für
Transport Fever 3 gibt es unter <i>Werkzeuge</i> die Heightmap. Im
Heightmap-Dialog erzeugst du Höhenmodell, Biome, Städte, Industrien
und eine Liste der Bahnhöfe. Die Schritte dazu stehen in der
Anleitung des Heightmap-Dialogs (F1).</p>
""":
        """
<h3>How to work with the Studio</h3>

<p><b>1. Define the area</b><br>
First you tell the Studio which piece of land you need.
Use the <i>Marker</i> tool to place a marker in the middle of the
area you want. Then open <i>Tools &rarr; Rectangle tool</i>
and choose the map size and rotation angle. A selected marker
provides the centre. The blue rectangle shows what will be loaded
later. With the two points on it you can move it (blue) and
rotate it (orange).</p>

<p><b>2. Load data</b><br>
<i>Tools &rarr; Load OSM</i> fetches roads, buildings, water and
more from OpenStreetMap. For large areas this can take several
minutes; the status bar shows the progress. What gets loaded is
set under <i>Tools &rarr; Overpass query</i>.</p>

<p><b>3. Show and hide layers</b><br>
In the <i>Layers</i> panel on the map you decide with the tick boxes
what you see. Hover the mouse over an entry and a short explanation
appears.</p>
<ul>
<li><b>Roads:</b> all roads and paths.</li>
<li><b>Railways:</b> railway lines.</li>
<li><b>Buildings:</b> all building outlines.</li>
<li><b>Water:</b> lakes, ponds and wide rivers as areas.</li>
<li><b>Rivers:</b> streams and rivers as lines.</li>
<li><b>Parks:</b> parks and gardens.</li>
<li><b>Land use:</b> fields, meadows, orchards and vineyards,
nurseries.</li>
<li><b>Vegetation:</b> forests and rows of trees.</li>
<li><b>Stations:</b> stations and stops with names, taken from the
loaded OSM data. The names appear when you zoom in.</li>
</ul>
<p>For large areas the map can become slow if everything is visible
at the same time. In that case hide individual layers.</p>

<p><b>4. Choose the background map</b><br>
Under <i>Map source</i> you switch between the normal road map
(<i>OpenStreetMap</i>) and <i>Map + relief</i>. The relief adds
a hillshade on top: valleys, slopes and ridges become visible,
which helps when choosing the area. The <i>Railway map</i> overlays
tracks and stations, handy for checking lines. The
<i>Measuring grid</i> helps to estimate distances and sizes.</p>

<p><b>5. Draw your own objects</b><br>
With <i>Draw</i> you create your own objects:</p>
<ul>
<li>First click <i>Road</i>, <i>River</i> or <i>Building</i>.
The button determines what you draw.</li>
<li>Then click the points one after another on the map. A red
line shows the course.</li>
<li>With <i>Done</i> (or a double click) the object is accepted.
A road and a river need at least 2 points, a building at least 3.
A building closes by itself.</li>
<li>After <i>Done</i> drawing is finished. For the next object,
first click the button (<i>Road</i>, <i>River</i> or
<i>Building</i>) again.</li>
<li>The object ends up in the matching layer (Roads, Rivers or
Buildings). If its tick box in the layer panel is off, you will
not see it.</li>
<li>Clicking the object shows its vertices. The points can be
dragged.</li>
</ul>
<p><i>JSON Export</i> and <i>JSON Import</i> save and load the
objects on the map as a file.</p>

<p><b>6. Tools</b><br>
In the bar at the top you choose what a click on the map does:
place a marker, set two corners for a selection, or show
coordinates and distances with the measuring tool.</p>

<p><b>7. Save and process further</b><br>
Save your project with <i>File &rarr; Save</i>. For
Transport Fever 3 there is the heightmap under <i>Tools</i>. In the
heightmap dialog you create the elevation model, biomes, towns,
industries and a list of stations. The steps are described in the
guide of the heightmap dialog (F1).</p>
""",
    'Heightmap':
        'Heightmap',
    'Noch nicht geladen.':
        'Not loaded yet.',
    'Copernicus: weltweit, aber nur 30 m fein und mit Baumkronen. DGM1 Deutschland: 1-m-Geländemodell der Bundesländer, die Kacheln werden über den Webdienst hoehendaten.de geladen (etwa 20 Kacheln pro Minute, danach liegen sie im Zwischenspeicher). Eigene Kacheln: GeoTIFF-Dateien (1-km-Raster), die du selbst bei einem Landesportal heruntergeladen hast. swissALTI3D Schweiz: Geländemodell von swisstopo für die Schweiz und Liechtenstein (2 m), die Kacheln werden von data.geo.admin.ch geladen und liegen danach im Zwischenspeicher. Nur bei Karten in der Schweiz wählbar.':
        'Copernicus: worldwide, but only 30 m resolution and including tree canopy. DGM1 Germany: 1 m terrain model of the German federal states; the tiles are loaded through the web service hoehendaten.de (about 20 tiles per minute, afterwards they are kept in the cache). Own tiles: GeoTIFF files (1 km grid) that you downloaded yourself from a state portal. swissALTI3D Switzerland: terrain model from swisstopo for Switzerland and Liechtenstein (2 m); the tiles are loaded from data.geo.admin.ch and kept in the cache afterwards. Only selectable for maps in Switzerland.',
    'Schnellvorschau (niedrige Auflösung, vor dem echten Download)':
        'Quick preview (low resolution, before the real download)',
    'Die Schnellvorschau nutzt immer Copernicus (schnell, weltweit), auch wenn unten eine DGM1-Quelle gewählt ist.':
        'The quick preview always uses Copernicus (fast, worldwide), even if a DGM1 source is selected below.',
    'Höhendaten herunterladen':
        'Download elevation data',
    'Original: alle Optionen aus, die echten Höhen. Empfohlen: hängt von der Höhenquelle ab. Copernicus: Gelände glätten, Trassen und Siedlungen einebnen und Wasser nur dort, wo OpenStreetMap Wasser hat, mit den Standardwerten. DGM1 und swissALTI3D: Glätten aus (das Modell ist schon genau), Einebnen 10 m, Wasser nach OSM mit Böschung 10 m. Optionen, die OSM-Daten brauchen, bleiben ohne geladene OSM-Daten aus.':
        'Original: all options off, the real elevations. Recommended: depends on the elevation source. Copernicus: smooth terrain, flatten routes and settlements and water only where OpenStreetMap has water, with the default values. DGM1 and swissALTI3D: smoothing off (the model is already accurate), flattening 10 m, water from OSM with a 10 m bank slope. Options that need OSM data stay off while no OSM data is loaded.',
    'Höhenbereich:':
        'Elevation range:',
    'Ausreißer aus Höhenbereich ausschließen (mehr Präzision fürs eigentliche Gelände)':
        'Exclude outliers from the elevation range (more precision for the actual terrain)',
    'Wasserhöhe:':
        'Water level:',
    'Wasserhöhe aus den OSM-Gewässern vorschlagen':
        'Suggest water level from the OSM waters',
    'Liest die Höhen des Hauptflusses (aus OpenStreetMap) und setzt die Wasserhöhe in die Mitte zwischen tiefstem und höchstem Punkt. So wird der Fluss an beiden Enden um etwa gleich viel korrigiert. Braucht geladene OSM-Daten.':
        'Reads the elevations of the main river (from OpenStreetMap) and sets the water level halfway between its lowest and highest point. This way the river is corrected by about the same amount at both ends. Needs loaded OSM data.',
    'Gelände glätten':
        'Smooth terrain',
    'Gelände':
        'Terrain',
    'Trassen und Siedlungen':
        'Routes and settlements',
    'Wasser und Ufer':
        'Water and shores',
    'Höhenfenster (Experte)':
        'Height window (expert)',
    'Gegen Treppenstufen und Kristallflächen an Hängen: das Höhenmodell hat nur etwa 30 m pro Pixel, das Spiel 4 m.':
        'Against stair steps and crystal-like facets on slopes: the elevation model has only about 30 m per pixel, the game 4 m.',
    'Breite der Glättung. 15 m entfernt die gröbsten Stufen, 30 m glättet stärker, flacht aber Gipfel und Kämme leicht ab.':
        'Width of the smoothing. 15 m removes the coarsest steps, 30 m smooths more strongly but slightly flattens peaks and ridges.',
    'Staucht alle Höhen über dem Wasserspiegel auf diesen Anteil. 100 % = unverändert. Hilft, wenn Hochflächen im Spiel über die Schneegrenze ragen (weiße Flächen). Die Hänge werden dabei flacher.':
        'Compresses all elevations above the water level to this proportion. 100 % = unchanged. Helps when plateaus rise above the snow line in the game (white areas). The slopes become flatter as a result.',
    'Trassen und Siedlungen einebnen':
        'Flatten routes and settlements',
    'Bahnstrecken, größere Straßen und Gebäude aus OpenStreetMap: das Gelände dort wird abgeflacht, damit im Spiel weniger Rampen nötig sind. Braucht geladene OSM-Daten.':
        'Railway lines, major roads and buildings from OpenStreetMap: the terrain there is flattened so that fewer ramps are needed in the game. Needs loaded OSM data.',
    'Je größer, desto ebener wird das Gelände entlang der Trassen und in den Ortschaften. Einschnitte und Dämme verschwinden.':
        'The larger the value, the flatter the terrain along the routes and in the settlements. Cuttings and embankments disappear.',
    'Seen, die höher als der Wasserspiegel liegen (zum Beispiel der Schliersee neben dem Tegernsee), werden auf den Wasserspiegel gesenkt. Das Gelände drumherum geht sanft mit und läuft über den eingestellten Auslauf aus, so entsteht keine Steilküste um den See. Braucht geladene OSM-Daten.':
        'Lakes that lie higher than the water level (for example Schliersee next to Tegernsee) are lowered to the water level. The surrounding terrain follows gently and fades out over the set falloff, so no steep cliff forms around the lake. Needs loaded OSM data.',
    'Gelände sanft mitsenken': 'Lower terrain gently around lakes',
    'Auslauf:': 'Falloff:',
    'Seen, die höher als der Wasserspiegel liegen (z. B. Schliersee neben dem Tegernsee), werden auf den Wasserspiegel abgesenkt. Das Gelände drumherum wird mitgesenkt und läuft mit dem eingestellten Auslauf sanft aus - so entsteht keine Steilküste um den See.':
        'Lakes that lie higher than the water level (e.g. Schliersee next to Tegernsee) are lowered to the water level. The surrounding terrain is lowered with them and fades out smoothly over the set falloff, so no steep cliff forms around the lake.',
    'Entfernung vom Ufer, in der die Absenkung auf null ausläuft. Größer = sanfter, aber mehr Umgebung wird verändert.':
        'Distance from the shore over which the lowering fades to zero. Larger = gentler, but more of the surroundings is changed.',
    'Gefälle ausgleichen':
        'Equalise river gradient',
    'Legt Flüsse und Seen auf eine gemeinsame Ebene und zieht das Gelände relativ dazu mit. Das Relief über dem jeweiligen Wasserspiegel bleibt erhalten, die absoluten Höhen ü. NN stimmen danach aber nicht mehr.':
        'Puts rivers and lakes on a common level and pulls the terrain along relative to it. The relief above the respective water level is preserved, but the absolute elevations above sea level are no longer correct afterwards.',
    ' m über Wasserspiegel':
        ' m above water level',
    'Nur Gewässer, die höchstens so hoch über dem Wasserspiegel liegen, dienen als Bezug. Höher gelegene Nebenflüsse und Bergseen werden ignoriert, sonst würde ihr Tal überflutet.':
        'Only waters that lie at most this high above the water level serve as a reference. Tributaries and mountain lakes at higher elevations are ignored, otherwise their valley would be flooded.',
    'Wasser nur dort, wo OpenStreetMap Wasser hat (empfohlen)':
        'Water only where OpenStreetMap has water (recommended)',
    'Gewässer bekommen ein festes Bett, alles andere Land liegt knapp über dem Wasserspiegel: keine überfluteten Auen und Tümpel. Ersetzt die sanfte Anpassung unten.':
        'Waters get a fixed bed, all other land lies just above the water level: no flooded floodplains and ponds. Replaces the gentle adjustment below.',
    'Böschung:':
        'Bank slope:',
    'Breite der Böschung zwischen Flussbett und Land. Breiter = flacheres Ufer, aber auch etwas breiteres Wasser.':
        'Width of the slope between riverbed and land. Wider = flatter bank, but also slightly wider water.',
    'Tiefe am Ufer:':
        'Depth at the bank:',
    'Tiefe des Flussbetts direkt am Ufer. Zur Mitte hin wird es tiefer (Fahrrinne), das ergibt einen natürlichen Querschnitt.':
        'Depth of the riverbed right at the bank. It gets deeper towards the middle (channel), which gives a natural cross-section.',
    'Tiefe in der Mitte:':
        'Depth in the middle:',
    'Tiefe des Flussbetts unter dem Wasserspiegel.':
        'Depth of the riverbed below the water level.',
    'Ufer über Wasser:':
        'Bank above water:',
    'So hoch liegt Land am Ufer mindestens über dem Wasserspiegel. Alles darunter wird angehoben und kann nicht überflutet werden.':
        'Land at the bank lies at least this high above the water level. Everything below is raised and cannot be flooded.',
    'Nur Gewässer bis':
        'Only waters up to',
    'Gewässer, die von Natur aus höher liegen (Bäche in den Bergen, Bergseen), bleiben unverändert.':
        'Waters that naturally lie higher (mountain streams, mountain lakes) remain unchanged.',
    'Terrain sanft ans Wasserniveau anpassen':
        'Gently adjust terrain to the water level',
    'Verhindert trockenfallende Flüsse und Seen, weicht dafür geringfügig von den echten Höhendaten ab. Sehr kleine Einzelgewässer werden ausgenommen, um Krater zu vermeiden. Das Gelände unterhalb des Wasserspiegels wird zusätzlich weichgezeichnet.':
        'Prevents rivers and lakes from running dry, at the cost of deviating slightly from the real elevation data. Very small individual waters are excluded to avoid craters. The terrain below the water level is additionally softened.',
    'Gewässer, die von Natur aus höher liegen (Bäche in den Bergen, Bergseen), bleiben unverändert und werden nicht zu Schluchten.':
        'Waters that naturally lie higher (mountain streams, mountain lakes) remain unchanged and do not turn into gorges.',
    'Der Karteneditor von TPF3 nimmt nur Höhen in diesem Bereich an. Liegt das Gelände (zum Beispiel in den Alpen) darüber oder darunter, wird es hier in ein Fenster gelegt. Die Vorschau färbt betroffene Stellen ein: rot = tiefer gesetzt (oben gekappt oder gestaucht), hellblau = höher gesetzt (unten abgeschnitten). Das Fenster gilt in Eintragswerten, also mit dem Haken unten bezogen auf die Wasserhöhe.':
        'The TPF3 map editor only accepts elevations within this range. If the terrain (for example in the Alps) lies above or below it, it is placed into a window here. The preview colours affected areas: red = lowered (clipped at the top or compressed), light blue = raised (cut off at the bottom). The window applies to entry values, so with the checkbox below it is relative to the water level.',
    'Oben kappen: Alles über dem Fenster wird flach auf die Obergrenze gesetzt, das Fenster liegt zunächst an der tiefsten Stelle. Unten abschneiden: Alles unter dem Fenster wird flach auf die Untergrenze gesetzt, das Fenster liegt zunächst an der höchsten Stelle. Stauchen: das ganze Gelände wird ins Fenster gedrückt, die Wasserhöhe bleibt dabei erhalten. Die Fensterbreite bestimmen die Felder darunter, der Schieberegler verschiebt das Fenster.':
        'Clip top: everything above the window is set flat to the upper limit; the window initially sits at the lowest point. Cut off bottom: everything below the window is set flat to the lower limit; the window initially sits at the highest point. Compress: the whole terrain is squeezed into the window, and the water level is preserved. The fields below set the window width, the slider moves the window.',
    'Werte auf Wasserhöhe 0 beziehen':
        'Relate values to water level 0',
    'Empfehlung des TPF3-Wikis für Biome und Materialien. Die Mindesthöhe kann dabei negativ werden.':
        'Recommendation of the TPF3 wiki for biomes and materials. The minimum height can become negative this way.',
    'Anleitung (F1)':
        'Guide (F1)',
    'Exportieren...':
        'Export...',
    'Biome-Maske aus OSM...':
        'Biome mask from OSM...',
    'Erzeugt aus der geladenen OSM-Landnutzung eine Maske für den Biome-Tab im Karteneditor. Braucht geladene OSM-Daten.':
        'Creates a mask for the Biomes tab in the map editor from the loaded OSM land use. Needs loaded OSM data.',
    'Städte aus OSM...':
        'Towns from OSM...',
    'Erzeugt aus den geladenen OSM-Orten eine Städte-Datei für den Ordner towns_industries. Braucht geladene OSM-Daten.':
        'Creates a towns file for the towns_industries folder from the loaded OSM places. Needs loaded OSM data.',
    'Industrien aus OSM...':
        'Industries from OSM...',
    'Erzeugt aus geladenen OSM-Objekten (Höfe, Steinbrüche, Sägewerke, ...) eine Industrien-Datei für den Ordner towns_industries. Braucht geladene OSM-Daten.':
        'Creates an industries file for the towns_industries folder from loaded OSM objects (farms, quarries, sawmills, ...). Needs loaded OSM data.',
    'Bahnhofsplan zum Nachbauen...':
        'Station plan for rebuilding...',
    'Bauplan zum Nachbauen echter Bahnhöfe: Das Spiel kann keine Bahnhöfe importieren. Liest Bahnhöfe, Haltepunkte, Bahnsteige, Bahnhofsgebäude und Haltepositionen aus den geladenen OSM-Daten und speichert sie als .json (alles) und .csv (eine Zeile je Bahnhof). Braucht geladene OSM-Daten.':
        'Blueprint for rebuilding real stations: the game cannot import stations. Reads stations, halts, platforms, station buildings and stop positions from the loaded OSM data and saves them as .json (everything) and .csv (one row per station). Needs loaded OSM data.',
    'Straßen und Gleise...':
        'Roads and tracks...',
    'Erzeugt aus den geladenen OSM-Wegen einen Mod, der im Spiel Straßen, Gleise, Brücken und Tunnel baut. Braucht geladene OSM-Daten.':
        'Creates a mod from the loaded OSM ways that builds roads, tracks, bridges and tunnels in the game. Needs loaded OSM data.',
    'Schließen':
        'Close',
    'Lade Höhendaten... (kann je nach Kartengröße etwas dauern)':
        'Loading elevation data... (may take a while depending on the map size)',
    'Lade Schnellvorschau...':
        'Loading quick preview...',
    '\nAchtung: Die Wasserhöhe liegt außerhalb des Fensters, die Flüsse wären im Spiel trocken oder die ganze Karte läge unter Wasser.':
        '\nWarning: The water level lies outside the window; the rivers would be dry in the game or the whole map would be under water.',
    'Heightmap exportieren':
        'Export heightmap',
    'PNG-Bilder (*.png)':
        'PNG images (*.png)',
    'Export abgeschlossen':
        'Export complete',
    'Höhenquelle:':
        'Elevation source:',
    'Copernicus (weltweit, 30 m)':
        'Copernicus (worldwide, 30 m)',
    'DGM1 Deutschland (1 m, über hoehendaten.de)':
        'DGM1 Germany (1 m, via hoehendaten.de)',
    'DGM1 aus eigenen GeoTIFF-Kacheln (Ordner)':
        'DGM1 from own GeoTIFF tiles (folder)',
    'swissALTI3D Schweiz (2 m, über data.geo.admin.ch)':
        'swissALTI3D Switzerland (2 m, via data.geo.admin.ch)',
    'Voreinstellung:':
        'Preset:',
    'Eigene Einstellungen':
        'Custom settings',
    'Original (1:1, unverändert)':
        'Original (1:1, unchanged)',
    'Empfohlen (Glätten, Einebnen, Wasser nach OSM)':
        'Recommended (smoothing, flattening, water from OSM)',
    'Glättung:':
        'Smoothing:',
    'Höhen stauchen auf:':
        'Compress elevations to:',
    'Stärke:':
        'Strength:',
    'Bezug: Gewässer bis':
        'Reference: waters up to',
    'Übergangsbreite:':
        'Transition width:',
    'Werte außerhalb:':
        'Values outside:',
    'Oben kappen (Gipfel planieren)':
        'Clip top (level off peaks)',
    'Unten abschneiden (Tiefen planieren)':
        'Cut off bottom (level off depths)',
    'Stauchen (alles ins Fenster drücken)':
        'Compress (squeeze everything into the window)',
    'Fenster von:':
        'Window from:',
    'bis:':
        'to:',
    'Fenster verschieben:':
        'Move window:',
    'Biome-Maske':
        'Biome mask',
    'Keine OSM-Daten geladen. Zuerst Werkzeuge → OSM laden ausführen und die Ebenen Landnutzung/Vegetation laden.':
        'No OSM data loaded. First run Tools → Load OSM and load the Land use/Vegetation layers.',
    'Städte aus OSM':
        'Towns from OSM',
    'Keine OSM-Daten geladen. Zuerst Werkzeuge → OSM laden ausführen.':
        'No OSM data loaded. First run Tools → Load OSM.',
    'Bahnhofsplan zum Nachbauen':
        'Station plan for rebuilding',
    'Keine OSM-Daten geladen. Zuerst Werkzeuge → OSM laden ausführen und die Ebene Eisenbahn laden.':
        'No OSM data loaded. First run Tools → Load OSM and load the Railways layer.',
    'Straßen und Gleise':
        'Roads and tracks',
    'Keine OSM-Daten geladen. Zuerst Werkzeuge → OSM laden ausführen und die Ebenen Straßen und Eisenbahn laden.':
        'No OSM data loaded. First run Tools → Load OSM and load the Roads and Railways layers.',
    'Industrien aus OSM':
        'Industries from OSM',
    'Berechne Höhenraster...':
        'Calculating elevation grid...',
    'Achtung: Ein größerer Teil der Fläche stammt aus Copernicus. An den Nahtstellen kann es kleine Höhenstufen geben.':
        'Warning: A larger part of the area comes from Copernicus. There may be small height steps at the seams.',
    "Keine OSM-Daten geladen - für die Terrain-Anpassung werden die Wasserflächen aus 'OSM laden' benötigt.":
        "No OSM data loaded - the terrain adjustment needs the water areas from 'Load OSM'.",
    "Keine OSM-Daten geladen - der Gefälle-Ausgleich braucht die Gewässer aus 'OSM laden'.":
        "No OSM data loaded - the gradient equalisation needs the waters from 'Load OSM'.",
    'In diesem Kartenausschnitt wurden keine Seen oder größeren Flüsse als Bezug gefunden - der Gefälle-Ausgleich hat hier keine Wirkung.':
        'No lakes or larger rivers were found as a reference in this map area - the gradient equalisation has no effect here.',
    'Als Bezug dienen Seen und Wasserflächen sowie Flüsse und Kanäle bis zur eingestellten Höhe über dem Wasserspiegel; Bäche, Gräben und höher gelegene Gewässer zählen dafür nicht.':
        'Lakes and water areas as well as rivers and canals up to the set height above the water level serve as a reference; streams, ditches and waters at higher elevations do not count.',
    'Keine Gewässer':
        'No waters',
    'In diesem Kartenausschnitt wurden keine Wasserflächen oder -wege gefunden. Zuerst OSM-Daten laden (Werkzeuge → OSM laden).':
        'No water areas or waterways were found in this map area. Load OSM data first (Tools → Load OSM).',
    'Hauptfluss liegt zwischen {low:.0f} und {high:.0f} m. Wasserhöhe auf {middle:.0f} m gesetzt (Mitte). Die Wasseroberfläche wird am oberen Ende um bis zu {lowered:.0f} m abgesenkt und am unteren um bis zu {raised:.0f} m angehoben.':
        'The main river lies between {low:.0f} and {high:.0f} m. Water level set to {middle:.0f} m (middle). The water surface is lowered by up to {lowered:.0f} m at the upper end and raised by up to {raised:.0f} m at the lower end.',
    ' oder ':
        ' or ',
    'Höhenfenster begrenzen (Editor nimmt nur {low:.0f} bis {high:.0f} m)':
        'Limit elevation window (editor only accepts {low:.0f} to {high:.0f} m)',
    ' ({name}, {percent:.1f} % der Fläche aus Copernicus ergänzt)':
        ' ({name}, {percent:.1f} % of the area supplemented from Copernicus)',
    'Quelle: © swisstopo (Bundesamt für Landestopografie swisstopo), swissALTI3D':
        'Source: © swisstopo (Federal Office of Topography swisstopo), swissALTI3D',
    'Quelle: DGM1 der Landesvermessung (Quellenvermerk des Landes beachten)':
        'Source: DGM1 of the state survey (observe the state’s attribution notice)',
    "Schnellvorschau ({width} x {height} Pixel, niedrige Auflösung - noch nicht exportierbar). Sieht das plausibel aus? Dann jetzt 'Höhendaten herunterladen' für die volle Auflösung.":
        "Quick preview ({width} x {height} pixels, low resolution - not exportable yet). Does it look plausible? Then click 'Download elevation data' now for the full resolution.",
    'Wassermaske fehlgeschlagen':
        'Water mask failed',
    ' Die Grenze „Nur Gewässer bis“ wurde auf {value} m erhöht.':
        ' The limit “Only waters up to” was raised to {value} m.',
    'In diesem Kartenausschnitt wurden keine Wasserflächen oder -wege gefunden - die Einstellung hat keine Wirkung. Zuerst OSM-Daten laden (Werkzeuge → OSM laden).':
        'No water areas or waterways were found in this map area - the setting has no effect. Load OSM data first (Tools → Load OSM).',
    'In diesem Kartenausschnitt wurden keine Wasserflächen/-wege gefunden - die Anpassung hat hier keine Wirkung.':
        'No water areas/waterways were found in this map area - the adjustment has no effect here.',
    '\n\nHinweis: Die {count} als Ausreißer erkannten Pixel liegen außerhalb dieses Bereichs und wurden dadurch auf den Rand geklemmt (0 bzw. 65535) - deren echte Höhe geht im Export verloren.':
        '\n\nNote: The {count} pixels detected as outliers lie outside this range and were therefore clamped to the edge (0 or 65535) - their real height is lost in the export.',
    '\n\nGefälle-Ausgleich aktiv (Stärke {strength:.0f} %, Glättung {smoothing:.0f} m): Flüsse und Seen wurden auf eine gemeinsame Ebene gelegt, das Gelände relativ dazu angepasst - die absoluten Höhen ü. NN stimmen dadurch nicht mehr.':
        '\n\nGradient equalisation active (strength {strength:.0f} %, smoothing {smoothing:.0f} m): rivers and lakes were put on a common level and the terrain adjusted relative to it - the absolute elevations above sea level are therefore no longer correct.',
    '\n\nTrassen und Siedlungen eingeebnet ({sigma:.0f} m).':
        '\n\nRoutes and settlements flattened ({sigma:.0f} m).',
    '\n\nHöhen über dem Wasserspiegel auf {percent:.0f} % gestaucht.':
        '\n\nElevations above the water level compressed to {percent:.0f} %.',
    '\n\nGelände geglättet ({sigma:.0f} m).':
        '\n\nTerrain smoothed ({sigma:.0f} m).',
    '\n\nWasser nur dort, wo OpenStreetMap Wasser hat: Flussbett {edge:.0f} m (Ufer) bis {depth:.0f} m (Mitte) unter dem Wasserspiegel, Land mindestens {bank:.1f} m darüber, Böschung {transition:.0f} m.':
        '\n\nWater only where OpenStreetMap has water: riverbed {edge:.0f} m (bank) to {depth:.0f} m (middle) below the water level, land at least {bank:.1f} m above it, bank slope {transition:.0f} m.',
    '\n\nDas Terrain wurde um Gewässer herum (Übergang {transition:.0f} m) sanft ans Wasserniveau angepasst - weicht dort geringfügig von den echten Höhendaten ab.':
        '\n\nThe terrain around waters (transition {transition:.0f} m) was gently adjusted to the water level - it deviates slightly from the real elevation data there.',
    '\n\nHöhenfenster {low:.0f} bis {high:.0f} m: {report}':
        '\n\nElevation window {low:.0f} to {high:.0f} m: {report}',
    'Abgebrochen.':
        'Cancelled.',
    'swissALTI3D-Kacheln laden':
        'Load swissALTI3D tiles',
    'Die Kacheln kommen von data.geo.admin.ch (swisstopo). Bereits geladene Kacheln werden übersprungen. Du kannst jederzeit abbrechen und später weitermachen.':
        'The tiles come from data.geo.admin.ch (swisstopo). Tiles that have already been loaded are skipped. You can cancel at any time and continue later.',
    'Quelle: {sources}':
        'Source: {sources}',
    '{count} Kacheln ohne {source}-Daten im Ausschnitt (dort Copernicus).':
        '{count} tiles without {source} data in the area (Copernicus there).',
    'Ausreißer aus Höhenbereich ausschließen ({count} Pixel, {percent:.2f}% der Fläche erkannt)':
        'Exclude outliers from the elevation range ({count} pixels, {percent:.2f}% of the area detected)',
    'Im TPF3-Import eintragen: Mindesthöhe {low:.0f}, Maximalhöhe {high:.0f}, Wasserhöhe {water:.0f}':
        'Enter in the TPF3 import: minimum height {low:.0f}, maximum height {high:.0f}, water level {water:.0f}',
    'Kartengröße und -format im Spiel: {size}':
        'Map size and format in the game: {size}',
    'Heightmap gespeichert unter:\n{filename}\n\n':
        'Heightmap saved to:\n{filename}\n\n',
    'Schnellvorschau fehlgeschlagen: {error}':
        'Quick preview failed: {error}',
    '\n\nKeine Wege gefunden. Sind Straßen und Gleise geladen (Werkzeuge → OSM laden) und die Haken oben gesetzt?':
        '\n\nNo ways found. Are roads and tracks loaded (Tools → Load OSM) and are the checkboxes above ticked?',
    '  davon Straßenbahn (Tram) einschließen':
        '  including tram',
    '(keine)':
        '(none)',
    ', {population} Einwohner':
        ', {population} inhabitants',
    '.osm-Datei (Arg 1):':
        '.osm file (arg 1):',
    '.osm-Datei wählen':
        'Choose .osm file',
    '16 m pro Pixel (klein, schnell)':
        '16 m per pixel (small, fast)',
    '4 m pro Pixel (wie die Heightmap)':
        '4 m per pixel (like the heightmap)',
    '8 m pro Pixel (Standard)':
        '8 m per pixel (default)',
    'Abbrechen':
        'Cancel',
    'Abstand zu Wasser:':
        'Distance to water:',
    'Abstand zum Kartenrand:':
        'Distance to map edge:',
    'Achtung: Diese Auswahl ist gedreht - der Converter kennt keine Drehung und erwartet eine einfache, achsenparallele Bounding Box. Die hier berechnete Box ist die umschließende Box des gedrehten Bands und passt NICHT exakt zu dessen tatsächlicher Form.':
        'Warning: This selection is rotated - the converter does not know about rotation and expects a simple, axis-aligned bounding box. The box calculated here is the enclosing box of the rotated band and does NOT exactly match its actual shape.',
    'Aktualisieren':
        'Refresh',
    'Alle Arten an':
        'All types on',
    'Alle Arten aus':
        'All types off',
    'Alle auswählen':
        'Select all',
    'Als Vorlage speichern':
        'Save as template',
    'Analysieren':
        'Analyse',
    'Auf längeren Kanten werden Knoten eingefügt (auf der Linie). Zwischen zwei Knoten verläuft die Höhe im Spiel geradlinig; bei Kanten von mehreren hundert Metern schweben die Gleise über dem Hang oder stecken im Einschnitt. 80 m passt zur Gleisterrasse der Heightmap. 0 = aus.':
        'Nodes are inserted on longer edges (on the line). Between two nodes the height runs in a straight line in the game; on edges of several hundred metres the tracks float above the slope or sit inside the cutting. 80 m matches the track terrace of the heightmap. 0 = off.',
    'Auflösung:':
        'Resolution:',
    'Ausführen über:':
        'Run via:',
    'Ausgewähltes Projekt öffnen':
        'Open selected project',
    'Ausschnitt Kantenlänge (0 = alles):':
        'Section edge length (0 = everything):',
    'Ausschnitt Mitte x (Ost):':
        'Section centre x (east):',
    'Ausschnitt Mitte y (Nord):':
        'Section centre y (north):',
    'Autobahn (motorway)':
        'Motorway (motorway)',
    'Autobahn-Ab-/Auffahrten':
        'Motorway slip roads',
    'Autobahn-Auffahrten (motorway_link)':
        'Motorway slip roads (motorway_link)',
    'Bahnhöfe konnten nicht auf der Karte angezeigt werden: {error}':
        'Stations could not be shown on the map: {error}',
    'Bahnhöfe speichern':
        'Save stations',
    'Bahnhöfe speichern...':
        'Save stations...',
    'Berechne Maske ...':
        'Calculating mask ...',
    'Biome-Maske aus OSM':
        'Biome mask from OSM',
    'Biome-Maske speichern':
        'Save biome mask',
    'Bitte einen Namen für die Vorlage eingeben.':
        'Please enter a name for the template.',
    'Breche ab...':
        'Cancelling...',
    'Brücken bauen (bridge=*)':
        'Build bridges (bridge=*)',
    'Brücken nutzen':
        'Use bridges',
    'Brücken, die kürzer sind, werden als gewöhnliche Straße oder gewöhnliches Gleis gebaut. Im Spiel scheiterten alle Gleisbrücken zwischen 4 und 20 m Länge.':
        'Bridges shorter than this are built as ordinary road or track. In the game, all track bridges between 4 and 20 m in length failed.',
    'Bundesstraße (primary)':
        'Primary road (primary)',
    'Bundesstraßen-Auffahrten (primary_link)':
        'Primary road slip roads (primary_link)',
    'Bundesstraßen-Verbindungen':
        'Primary road connections',
    'Converter-Befehl':
        'Converter command',
    'DGM1-Kacheln laden':
        'Load DGM1 tiles',
    'Das Netz konnte nicht berechnet werden:\n{error}':
        'The network could not be calculated:\n{error}',
    'Datei fehlerhaft: {error}':
        'File is faulty: {error}',
    'Der Dienst hoehendaten.de erlaubt etwa 20 Kacheln pro Minute. Bereits geladene Kacheln werden übersprungen. Du kannst jederzeit abbrechen und später weitermachen.':
        'The hoehendaten.de service allows about 20 tiles per minute. Tiles that have already been loaded are skipped. You can cancel at any time and continue later.',
    'Der Mod konnte nicht geschrieben werden:\n{error}':
        'The mod could not be written:\n{error}',
    'Die Bahnhöfe konnten nicht gelesen werden:\n{error}':
        'The stations could not be read:\n{error}',
    'Die Datei konnte nicht gespeichert werden:\n{error}':
        'The file could not be saved:\n{error}',
    'Die Dateien konnten nicht geschrieben werden:\n{error}':
        'The files could not be written:\n{error}',
    'Die Maske konnte nicht berechnet werden:\n{error}':
        'The mask could not be calculated:\n{error}',
    'Doppelt gezeichnete Gleise entfernen (im Spiel ungetestet)':
        'Remove doubled tracks (untested in the game)',
    'Drehwinkel:':
        'Rotation angle:',
    'Durchsuchen...':
        'Browse...',
    'Einbahnstraßen mit schmaler Einbahn-Vorlage bauen (empfohlen)':
        'Build one-way roads with the narrow one-way template (recommended)',
    'Einmündungen und Wegenden, die näher beieinander liegen, werden zu einem Knoten. Die Straßen im Spiel sind 14 bis 30 m breit, dichter liegende Einmündungen lassen sich dort nicht bauen. 0 = aus. Im Spiel noch nicht getestet.':
        'Junctions and way ends that lie closer together are merged into one node. Roads in the game are 14 to 30 m wide; junctions closer together cannot be built there. 0 = off. Not tested in the game yet.',
    'Einmündungen zusammenlegen bis:':
        'Merge junctions up to:',
    'Einstellungen geändert. Bitte „Netz berechnen“ erneut ausführen.':
        'Settings changed. Please run “Calculate network” again.',
    'Eisenbahn (rail)':
        'Railway (rail)',
    'Elektrifizierte Gleise im Gebiet':
        'Electrified tracks in the area',
    'Ergebnis':
        'Result',
    'Erzeugt aus den geladenen OSM-Objekten eine Industrien-Datei für den Ordner towns_industries. Der Nullpunkt ist die Kartenmitte. Im Spiel beim Import "Städte behalten: Ja" wählen, die Datei enthält keine Städte. Die Zuordnung ist ein Vorschlag, ob das Spiel jede Position annimmt, ist ungeprüft.':
        'Creates an industries file for the towns_industries folder from the loaded OSM objects. The origin is the map centre. When importing in the game, choose "Keep towns: Yes", the file contains no towns. The assignment is a suggestion; whether the game accepts every position has not been tested.',
    'Erzeugt aus den geladenen OSM-Orten eine Städte-Datei für den Ordner towns_industries. Der Nullpunkt ist die Kartenmitte. Die Anfangsgröße der Stadt im Spiel wird aus der OSM-Einwohnerzahl abgeleitet: Faktor = Maßstab × Wurzel(Einwohner). Faktor 1 sind im Spiel etwa 100 Einwohner. Große Städte starten größer, kleine Dörfer kleiner. Industrien werden noch nicht erzeugt.':
        'Creates a towns file for the towns_industries folder from the loaded OSM places. The origin is the map centre. The initial size of the town in the game is derived from the OSM population: factor = scale × square root(population). A factor of 1 is about 100 inhabitants in the game. Large cities start larger, small villages smaller. Industries are not created yet.',
    'Erzeugt aus den geladenen OSM-Wegen einen Mod für Transport Fever 3. Der Mod baut im Spiel Straßen, Gleise, Brücken und Tunnel auf die geladene Heightmap. Die Höhen der Strecken plant der Mod selbst (aus dem Gelände, mit Steigungsgrenze). Nullpunkt ist die Kartenmitte, wie bei den Städten.':
        'Creates a mod for Transport Fever 3 from the loaded OSM ways. In the game, the mod builds roads, tracks, bridges and tunnels onto the loaded heightmap. The mod plans the heights of the routes itself (from the terrain, with a gradient limit). The origin is the map centre, as with the towns.',
    'Erzeugt aus der geladenen OSM-Landnutzung eine Maske für den Biome-Tab im Karteneditor. Wähle für jede Art von Fläche das Biom. Alles andere, auch Wasser, bekommt Biom 0. Die Voreinstellung ist ein Vorschlag nach dem Aussehen der Biome und im Spiel noch nicht geprüft.':
        'Creates a mask for the Biomes tab in the map editor from the loaded OSM land use. Choose the biome for each type of area. Everything else, including water, gets biome 0. The preset is a suggestion based on the look of the biomes and has not been checked in the game yet.',
    'Es ist keine Fläche einem Biom zugeordnet.':
        'No area is assigned to a biome.',
    'Es sind keine OSM-Daten geladen.':
        'No OSM data is loaded.',
    "Es sind keine OSM-Daten geladen. Zuerst 'OSM laden' ausführen.":
        "No OSM data is loaded. Run 'Load OSM' first.",
    'Faktor 1 sind etwa 100 Einwohner. Getestet: 0,2 gibt etwa 19 Einwohner. Werte darunter sind ungeprüft.':
        'A factor of 1 is about 100 inhabitants. Tested: 0.2 gives about 19 inhabitants. Values below that are untested.',
    'Faktor 30 ergab im Test 2892 Einwohner, Faktor 100 nur 4476. Höher als 30 ist ungetestet.':
        'In testing, a factor of 30 gave 2892 inhabitants, a factor of 100 only 4476. Anything higher than 30 is untested.',
    'Faktor = Maßstab × Wurzel(Einwohner). Bei 0,03 bekommt Koblenz (110 000) etwa Faktor 10, ein Dorf mit 300 etwa 0,5.':
        'Factor = scale × square root(population). At 0.03, Koblenz (110,000) gets a factor of about 10, a village of 300 about 0.5.',
    'Fertiger Befehl ({exe_name} im Converter-Ordner ausführen):':
        'Finished command (run {exe_name} in the converter folder):',
    'Flächennutzung':
        'Land use',
    'Formpunkte, die die Linie um weniger als diesen Wert verändern, entfallen. Kreuzungen und Wegenden bleiben immer. Weniger Punkte bedeuten ein kleineres Netz im Spiel.':
        'Shape points that change the line by less than this value are dropped. Junctions and way ends are always kept. Fewer points mean a smaller network in the game.',
    'Formpunkte, die näher als dieser Wert am Nachbarn liegen, entfallen. Sehr kurze Kanten sind in TPF2 oft gescheitert.':
        'Shape points that are closer to their neighbour than this value are dropped. Very short edges often failed in TPF2.',
    'Forst ab Größe:':
        'Forest from size:',
    'Genutzte Importer-Funktionen (bestimmt, welche Mod-Kategorien geprüft werden)':
        'Importer features used (determines which mod categories are checked)',
    'Gespeichert ({count} Industrien):\n{path}\n\nIm Spiel: Karteneditor → Reiter Städte/Industrien → Import → diese Datei wählen, "Städte behalten" auf Ja, "Industrien behalten" auf Nein → Import.':
        'Saved ({count} industries):\n{path}\n\nIn the game: Map editor → Towns/Industries tab → Import → choose this file, "Keep towns" set to Yes, "Keep industries" set to No → Import.',
    'Gespeichert ({count} Städte):\n{path}\n\nIm Spiel: Karteneditor → Reiter Städte/Industrien → Import → diese Datei wählen → Import.':
        'Saved ({count} towns):\n{path}\n\nIn the game: Map editor → Towns/Industries tab → Import → choose this file → Import.',
    'Gespeichert:\n{path}\n\nIm Spiel: Karteneditor → Heightmap importieren → Reiter Biome → bei "Biome" diese Datei wählen, Berge und Flüsse leer lassen → Anwenden.':
        'Saved:\n{path}\n\nIn the game: Map editor → Import heightmap → Biomes tab → choose this file under "Biomes", leave Mountains and Rivers empty → Apply.',
    'Gewässer':
        'Waters',
    'Geändert':
        'Modified',
    'Gleichartige Industrien müssen mindestens so weit auseinander liegen.':
        'Industries of the same type must be at least this far apart.',
    'Gleise':
        'Tracks',
    'Gleise, die fast deckungsgleich auf einem anderen Gleis liegen (z. B. Servicegleis auf der Hauptstrecke), entfallen.':
        'Tracks that lie almost exactly on top of another track (e.g. a service track on the main line) are dropped.',
    'Gleistypen':
        'Track types',
    'Gruben: höchster Höhenunterschied:':
        'Pits: maximum height difference:',
    'Größe aus der OSM-Einwohnerzahl ableiten':
        'Derive size from the OSM population',
    'Größter Faktor:':
        'Largest factor:',
    'Größter Knotenabstand:':
        'Largest node spacing:',
    'Hinweis':
        'Note',
    'Hinweis: Es sind keine Höhendaten geladen. Hang- und Wasserprüfung sind aus. Zuerst im Heightmap-Dialog die Höhendaten herunterladen.':
        'Note: No elevation data is loaded. The slope and water checks are off. First download the elevation data in the heightmap dialog.',
    'Höchstens je Art:':
        'Maximum per type:',
    'Höchstens so viele Industrien je Art, die größten zuerst.':
        'At most this many industries per type, the largest first.',
    'Höchster Höhenunterschied (150 m):':
        'Maximum height difference (150 m):',
    'Höchster Höhenunterschied im Umkreis von 150 m. Industrien auf steileren Hängen werden aussortiert. 0 = nicht prüfen.':
        'Maximum height difference within a radius of 150 m. Industries on steeper slopes are sorted out. 0 = do not check.',
    'In Zwischenablage kopieren':
        'Copy to clipboard',
    'In den geladenen OSM-Daten wurden keine Bahnhöfe oder Haltepunkte gefunden.\n\nMöglicherweise lädt die OSM-Abfrage des Studios Bahnhofsdaten nicht mit. Dann müsste die Abfrage um railway=station/halt/platform und building=train_station erweitert werden.':
        "No stations or halts were found in the loaded OSM data.\n\nThe Studio's OSM query may not load station data. In that case the query would have to be extended by railway=station/halt/platform and building=train_station.",
    'In den geladenen OSM-Daten wurden keine Bahnhöfe oder Haltepunkte gefunden.\n\nZuerst Werkzeuge → OSM laden ausführen und die Ebene Eisenbahn laden. Bleibt es leer, lädt die OSM-Abfrage Bahnhofsdaten (railway=station/halt/platform, building=train_station) möglicherweise nicht mit.':
        'No stations or halts were found in the loaded OSM data.\n\nFirst run Tools → Load OSM and load the Railways layer. If it stays empty, the OSM query may not load station data (railway=station/halt/platform, building=train_station).',
    'Industrie-Objekte (Sägewerk, Ziegelei, ...)':
        'Industry objects (sawmill, brickworks, ...)',
    'Natur-Details (Hecken, Mauern)':
        'Nature details (hedges, walls)',
    'Industrien speichern':
        'Save industries',
    'JSON (*.json)':
        'JSON (*.json)',
    'Kartengröße:':
        'Map size:',
    'Kategorien':
        'Categories',
    'Kein Kartenausschnitt gesetzt (Rechteck-Tool verwenden).':
        'No map section set (use the rectangle tool).',
    'Kein Name':
        'No name',
    'Keine Kategorie ausgewählt':
        'No category selected',
    'Keine Orte gefunden. Entweder enthalten die geladenen OSM-Daten keine Ortsknoten (die Overpass-Abfrage muss place=city/town/village mitladen) oder der Filter ist zu streng.':
        'No places found. Either the loaded OSM data contains no place nodes (the Overpass query must also load place=city/town/village) or the filter is too strict.',
    'Keine auswählen':
        'Select none',
    'Keine passenden Objekte gefunden. Entweder fehlen sie in den geladenen OSM-Daten (im Overpass-Baukasten den Haken "Industrie-Objekte" und für Steinbrüche "Siedlung, Heide, Moor, Fels" setzen, dann neu laden) oder die Filter sind zu streng.':
        'No matching objects found. Either they are missing from the loaded OSM data (in the Overpass builder tick "Industry objects" and, for quarries, "Settlement, heath, bog, rock", then reload) or the filters are too strict.',
    'Keine sicher entfernbaren Formpunkte gefunden.':
        'No shape points found that can be removed safely.',
    'Kleinster Faktor:':
        'Smallest factor:',
    'Kleinster Punktabstand:':
        'Smallest point spacing:',
    'Kreisstraße (tertiary)':
        'Tertiary road (tertiary)',
    'Kreisstraßen-Auffahrten (tertiary_link)':
        'Tertiary road slip roads (tertiary_link)',
    'Kreisstraßen-Verbindungen':
        'Tertiary road connections',
    'Kurze Verbindungssegmente':
        'Short connecting segments',
    'Kürzeste Brücke:':
        'Shortest bridge:',
    'Laden':
        'Load',
    'Landesstraße (secondary)':
        'Secondary road (secondary)',
    'Landesstraßen-Auffahrten (secondary_link)':
        'Secondary road slip roads (secondary_link)',
    'Landstraßen-Verbindungen':
        'Secondary road connections',
    'Liest Bahnhöfe, Haltepunkte, Bahnsteige, Bahnhofsgebäude und Haltepositionen aus den geladenen OSM-Daten und speichert sie als .json (alles) und .csv (eine Zeile je Bahnhof). Es wird nichts im Spiel gebaut.':
        'Reads stations, halts, platforms, station buildings and stop positions from the loaded OSM data and saves them as .json (everything) and .csv (one row per station). Nothing is built in the game.',
    'Lokaler mod-Ordner nicht gefunden: {local_path}':
        'Local mod folder not found: {local_path}',
    'Lokaler mod-Ordner:':
        'Local mod folder:',
    'Lua (*.lua)':
        'Lua (*.lua)',
    'Länge':
        'Length',
    'Maske {w_px} x {h_px} Pixel. ':
        'Mask {w_px} x {h_px} pixels. ',
    'Maßstab:':
        'Scale:',
    'Mindestabstand Straße–Gleis:':
        'Minimum distance road–track:',
    'Mindestabstand je Art:':
        'Minimum distance per type:',
    'Mindestabstand zu Gewässern. 0 = nicht prüfen.':
        'Minimum distance to waters. 0 = do not check.',
    'Mindestabstand zum Kartenrand. Felder und Hecken einer Industrie ragen sonst über den Rand hinaus.':
        'Minimum distance to the map edge. Otherwise the fields and hedges of an industry would extend beyond the edge.',
    'Mindestabstand zwischen Straße und Gleis (Mittellinie zu Mittellinie). Die Straße ist 14 m breit, das Gleis mit Masten rund 7 m. Standard 9 m: Die Ränder berühren sich nicht, die Straße bleibt nah an ihrer OSM-Lage, aber es bleibt kein freier Streifen dazwischen (dort geht im Spiel weder Gelände anheben noch Pflanzen setzen). 14 m lassen rund 3,5 m frei, verschieben die Straße aber bis zu 5 m von ihrer Lage. Übergänge und kreuzende Straßen bleiben. 0 = aus.':
        'Minimum distance between road and track (centre line to centre line). The road is 14 m wide, the track with masts about 7 m. Default 9 m: the edges do not touch and the road stays close to its OSM position, but no free strip remains in between (where in the game neither raising terrain nor placing plants is possible). 14 m leaves about 3.5 m free but moves the road up to 5 m from its position. Crossings and crossing roads are kept. 0 = off.',
    'Mindestens Einwohner:':
        'Minimum inhabitants:',
    'Mindestens einen Straßentyp auswählen.':
        'Select at least one road type.',
    'Mittelpunkt Breite (lat):':
        'Centre latitude (lat):',
    'Mittelpunkt Länge (lon):':
        'Centre longitude (lon):',
    'Mod':
        'Mod',
    'Mod geschrieben:\n{root}\n\nIm Spiel:\n1. Mod „Map Studio Import“ im Mod-Menü aktivieren und das Spiel neu starten.\n2. Karte mit der Heightmap laden, warten bis „Map is ready“ in der Konsole steht, Spielstand speichern, Pause ausschalten.\n3. In der Konsole eingeben:\n{START_COMMAND}\n4. Warten bis „Import fertig“ in der Konsole steht.':
        'Mod written:\n{root}\n\nIn the game:\n1. Activate the mod “Map Studio Import” in the mod menu and restart the game.\n2. Load the map with the heightmap, wait until “Map is ready” appears in the console, save the game, switch off pause.\n3. Enter in the console:\n{START_COMMAND}\n4. Wait until “Import fertig” appears in the console (the mod prints this text in German).',
    'Mod schreiben...':
        'Write mod...',
    'Mod-Checker':
        'Mod checker',
    'Name für neue Vorlage':
        'Name for new template',
    'Nebenstraße (unclassified)':
        'Minor road (unclassified)',
    'Netz berechnen':
        'Calculate network',
    'Nichts zu vereinfachen':
        'Nothing to simplify',
    'Nimmt die Haken bei Wohnstraße, Verkehrsberuhigt, Nebenstraße und Zufahrten heraus. Für einen ersten Test sinnvoll: weniger Wege, weniger Überschneidungen.':
        'Unticks the boxes for residential, living street, minor road and service roads. Useful for a first test: fewer ways, fewer overlaps.',
    'Noch keine Vorschau.':
        'No preview yet.',
    'Noch nicht analysiert':
        'Not analysed yet',
    'Noch nicht analysiert.':
        'Not analysed yet.',
    'Noch nicht berechnet. „Netz berechnen“ zeigt, wie viele Wege und Knoten entstehen.':
        'Not calculated yet. “Calculate network” shows how many ways and nodes will be created.',
    'Nur Hauptstrecken (ohne Wohn- und Nebenstraßen)':
        'Main routes only (without residential and minor roads)',
    'Nur Wege in diesem Quadrat (Mitte in Metern ab Kartenmitte). 0 = ganze Karte. Für große Karten: erst einen Ausschnitt von 6000 bis 8000 m testen.':
        'Only ways inside this square (centre in metres from the map centre). 0 = whole map. For large maps: first test a section of 6000 to 8000 m.',
    'OSM-Daten':
        'OSM data',
    'OSM-Importer-Ordnername:':
        'OSM importer folder name:',
    'Ordner wählen':
        'Choose folder',
    'Ordner „mods“ von Transport Fever 3 wählen':
        'Choose the “mods” folder of Transport Fever 3',
    'Ordnername unter .../mod/, z.B. osm_tpf2_importer':
        'Folder name under .../mod/, e.g. osm_tpf2_importer',
    'Orte (Städte, Dörfer)':
        'Places (cities, villages)',
    'Overpass-Abfrage':
        'Overpass query',
    'PNG (*.png)':
        'PNG (*.png)',
    'Parallele Richtungsfahrbahnen (je ein OSM-Weg mit oneway=yes) würden sich sonst als zwei zweispurige Straßen überlagern. Autobahnen bleiben unverändert (es gibt keine Einbahn-Vorlage dafür).':
        'Otherwise parallel carriageways (one OSM way each with oneway=yes) would overlap as two two-lane roads. Motorways remain unchanged (there is no one-way template for them).',
    'Parks / Gärten':
        'Parks / gardens',
    'Paver / Bodentexturen nutzen':
        'Use pavers / ground textures',
    'Pfade':
        'Paths',
    'Projekt-Dashboard':
        'Project dashboard',
    'Projekte-Ordner wählen':
        'Choose projects folder',
    'Projekte-Ordner:':
        'Projects folder:',
    'Prüfen':
        'Check',
    'Prüfpunkt':
        'Check item',
    'Prüft, ob sehr kurze Segmente bei Ab-/Auffahrten-Straßentypen vorkommen. Eine Analyse eines echten Baulaufs zeigte: fehlgeschlagene secondary_link-Kanten waren im Median ~6,9 m lang, erfolgreiche ~23,1 m - das ist eine beobachtete Korrelation, kein bewiesener Grund. Die Vereinfachung entfernt ausschließlich Formpunkte, die garantiert zu keiner echten Kreuzung gehören - Kreuzungen bleiben immer unangetastet.':
        'Checks whether very short segments occur in slip-road types. An analysis of a real build run showed: failed secondary_link edges had a median length of ~6.9 m, successful ones ~23.1 m - this is an observed correlation, not a proven cause. The simplification only removes shape points that are guaranteed not to belong to a real junction - junctions are always left untouched.',
    'Prüfung der aktuell geladenen OSM-Daten, bevor du Heightmap, Städte, Industrien und weitere Dateien erzeugst:':
        'Check of the currently loaded OSM data before you create the heightmap, towns, industries and other files:',
    'Richtungsfahrbahnen zusammenfassen (im Spiel ungetestet)':
        'Merge carriageways (untested in the game)',
    'S-Bahn (light_rail)':
        'Light rail (light_rail)',
    'Schnellstraße (trunk)':
        'Trunk road (trunk)',
    'Schnellstraßen-Ab-/Auffahrten':
        'Trunk road slip roads',
    'Schnellstraßen-Auffahrten (trunk_link)':
        'Trunk road slip roads (trunk_link)',
    'Schwellenwert:':
        'Threshold:',
    'Sicherheitsrand (für Downloads):':
        'Safety margin (for downloads):',
    'Siedlung, Heide, Moor, Fels (für Biome)':
        'Settlement, heath, bog, rock (for biomes)',
    'Signale nutzen':
        'Use signals',
    'Starte...':
        'Starting...',
    'Status':
        'Status',
    'Steam-Workshop-Ordner:':
        'Steam Workshop folder:',
    'Straßen und Gleise für das Spiel':
        'Roads and tracks for the game',
    'Straßenbahn (tram) – im Spiel noch ungetestet':
        'Tram (tram) – not yet tested in the game',
    'Straßenobjekte nutzen':
        'Use road objects',
    'Straßentypen':
        'Road types',
    'Städte speichern':
        'Save towns',
    'Tunnel bauen (tunnel=yes)':
        'Build tunnels (tunnel=yes)',
    'Typ':
        'Type',
    'Vegetation (Wald, Baumreihen)':
        'Vegetation (forest, tree rows)',
    'Vereinfachen bis:':
        'Simplify up to:',
    'Vereinfacht als .osm exportieren...':
        'Export simplified as .osm...',
    'Vereinfachte OSM-Datei exportieren':
        'Export simplified OSM file',
    'Vereinfachte OSM-Datei gespeichert unter:\n{filename}\n\n{count} Formpunkte entfernt (nur nicht-Kreuzungs-Knoten). Das ursprüngliche Projekt im Studio ist unverändert.':
        'Simplified OSM file saved to:\n{filename}\n\n{count} shape points removed (non-junction nodes only). The original project in the Studio is unchanged.',
    'Verkehrsberuhigt (living_street)':
        'Living street (living_street)',
    'Vorab-Prüfung':
        'Pre-check',
    'Vorlage':
        'Template',
    'Vorschau':
        'Preview',
    'Vorschau der resultierenden Abfrage:':
        'Preview of the resulting query:',
    'Wald-Import nutzen':
        'Use forest import',
    'Weg-ID':
        'Way ID',
    'Wege werden so weit vor dem Kartenrand abgeschnitten.':
        'Ways are cut off this far before the map edge.',
    'Wie "Höchster Höhenunterschied", aber für Gruben und Minen (Stein, Lehm, Sand, Kohle, Eisenerz). Sie liegen in OSM meist am Hang, das Spiel schneidet sie als große Grube hinein. 0 = nicht prüfen.':
        'Like "Maximum height difference", but for pits and mines (stone, clay, sand, coal, iron ore). In OSM they mostly lie on a slope, and the game cuts them in as a large pit. 0 = do not check.',
    'Wohnstraße (residential)':
        'Residential road (residential)',
    'Workshop-Ordner nicht gefunden: {workshop_path}':
        'Workshop folder not found: {workshop_path}',
    "Zuerst auf 'Analysieren' klicken.":
        "First click 'Analyse'.",
    'Zufahrten und Wirtschaftswege (service)':
        'Service and farm tracks (service)',
    'Zwei parallele Einbahn-Wege gegenläufiger Richtung werden zu einem zweispurigen Weg in der Mitte. Autobahnen bleiben unverändert.':
        'Two parallel one-way ways in opposite directions become one two-lane way in the middle. Motorways remain unchanged.',
    'exportiert ({item})':
        'exported ({item})',
    'fehlt noch':
        'still missing',
    'gefunden als: {found_display_name}':
        'found as: {found_display_name}',
    'keine OSM-Daten':
        'no OSM data',
    'main.exe (vorkompiliert, aus den Releases)':
        'main.exe (precompiled, from the releases)',
    'main.py über venv (Python-Installation nötig)':
        'main.py via venv (Python installation required)',
    'nicht verwenden':
        'do not use',
    "z.B. map.osm (mit 'OSM als .osm exportieren...' erzeugt)":
        "e.g. map.osm (created with 'Export OSM as .osm...')",
    '{count} Objekte gefunden, {chosen} ausgewählt. Nur die angehakten werden exportiert.':
        '{count} objects found, {chosen} selected. Only the ticked ones are exported.',
    '{count} Orte gefunden, {chosen} ausgewählt. Nur die angehakten Orte werden exportiert.':
        '{count} places found, {chosen} selected. Only the ticked places are exported.',
    '{count} kurze Segmente in {count2} Wegen gefunden. {count3} Formpunkte könnten sicher entfernt werden (keine Kreuzungen darunter).':
        '{count} short segments found in {count2} ways. {count3} shape points could be removed safely (no junctions among them).',
    '{name} ({kind}{population})  Faktor {factor:g}  x {x:.0f} m, y {y:.0f} m':
        '{name} ({kind}{population})  factor {factor:g}  x {x:.0f} m, y {y:.0f} m',
    '{station_summary}\n\nGespeichert:\n{json_path}\n{csv_path}':
        '{station_summary}\n\nSaved:\n{json_path}\n{csv_path}',
    '{summary}\n\nGespeichert:\n{json_path}\n{csv_path}':
        '{summary}\n\nSaved:\n{json_path}\n{csv_path}',
    '{text}  (höchstens noch etwa {remaining_min:.0f} Min.)':
        '{text}  (at most about {remaining_min:.0f} min. left)',
    '{way_count} Wege':
        '{way_count} ways',
    '⚠ Bekannter Problem-Mod gefunden: {description} ({path})':
        '⚠ Known problem mod found: {description} ({path})',
    '⚠ OSM-TPF2-Importer scheint mehrfach installiert zu sein: {locations}':
        '⚠ OSM-TPF2-Importer seems to be installed more than once: {locations}',
    '✅ gefunden (Workshop)':
        '✅ found (Workshop)',
    '✅ gefunden (lokal)':
        '✅ found (local)',
    '❌ fehlt':
        '❌ missing',
    '❓ nicht automatisch prüfbar':
        '❓ cannot be checked automatically',
    '➖ übersprungen (Funktion nicht genutzt)':
        '➖ skipped (feature not used)',
    'Anleitung: Heightmap für TPF3':
        'Guide: Heightmap for TPF3',
    '\n<h2>Heightmap vom Studio nach Transport Fever 3</h2>\n<p>Schritt für Schritt von der leeren Karte bis zur importierten Heightmap.\nWas noch nicht im Spiel getestet ist, steht jeweils dabei.</p>\n\n<h3>Teil A: Im Studio</h3>\n\n<h4>Ausschnitt festlegen</h4>\n<ol>\n<li>Im Panel auf der Karte unter <b>Kartenquelle</b> am besten <b>Karte + Relief</b>\nwählen, damit man Täler und Hänge sieht. Zum gewünschten Gebiet zoomen. Optional mit dem\n<b>Marker</b>-Werkzeug einen Marker in die Mitte setzen (er liefert den Mittelpunkt).</li>\n<li><b>Werkzeuge → Rechteck-Tool</b>: Mittelpunkt prüfen, <b>Kartengröße</b> und\n<b>Format</b> genau wie im Spiel wählen, <b>Drehwinkel</b> einstellen, bis das Band zu deinem\nFluss oder deiner Strecke passt. OK. Das blaue Band lässt sich mit dem blauen Punkt\nverschieben und mit dem orangen drehen.</li>\n</ol>\n\n<h4>OSM-Daten laden</h4>\n<ol start="3">\n<li><b>Werkzeuge → OSM laden</b> und warten. Große Gebiete brauchen einige Minuten.\nOhne OSM-Daten funktionieren die Optionen „Wasser nur dort, wo OpenStreetMap Wasser hat“\nund „Trassen und Siedlungen einebnen“ nicht.</li>\n</ol>\n\n<h4>Höhendaten holen (in diesem Dialog)</h4>\n<ol start="4">\n<li>Optional <b>Schnellvorschau</b> (grob, sofort da, nicht exportierbar).</li>\n<li>Oben unter <b>Höhenquelle</b> wählen: <b>Copernicus</b> (weltweit, 30 m, schnell) oder für\nKarten in Deutschland <b>DGM1 Deutschland</b> (1-m-Geländemodell der Bundesländer, genauer an\nHängen und Böschungen). Dann <b>Höhendaten herunterladen</b> und warten, bis oben „Geladen: …\nPixel“ steht. Beim ersten Mal lädt das Studio die Kacheln, danach geht es schneller.\n<br>Bei DGM1 kommen die Kacheln über den Webdienst hoehendaten.de, höchstens etwa 20 Kacheln\npro Minute: eine große Karte braucht etwa eine halbe Stunde. Das Fenster zeigt den Fortschritt\nund lässt sich abbrechen, bereits geladene Kacheln werden beim nächsten Mal übersprungen. Wer\ndie Kacheln selbst bei einem Landesportal heruntergeladen hat, wählt <b>DGM1 aus eigenen\nGeoTIFF-Kacheln</b> und den Ordner (die Kacheln müssen auf dem 1-km-Raster liegen). Wo DGM1-Daten\nfehlen, ergänzt das Studio aus Copernicus. Die Schnellvorschau nutzt immer Copernicus.\n<i>DGM1 ist am Rhein (Bingen bis Koblenz, Größenwahnsinnig 1:5) im Spiel getestet.</i>\n<br>Für Karten in der <b>Schweiz</b> oder in Liechtenstein gibt es <b>swissALTI3D Schweiz</b>\n(Geländemodell von swisstopo mit 2 m Auflösung). Die Auswahl erscheint nur, wenn der Kartenmittelpunkt\ndort liegt. Die Kacheln kommen von data.geo.admin.ch, ein Fenster zeigt den Fortschritt und lässt\nsich abbrechen, geladene Kacheln liegen im Zwischenspeicher. Wo Daten fehlen, ergänzt das Studio aus\nCopernicus. Die Voreinstellung „Empfohlen“ behandelt swissALTI3D wie DGM1.\n<i>swissALTI3D ist bei Bern im Spiel getestet.</i>\n<br>Für Karten in den <b>Niederlanden</b> gibt es <b>AHN Niederlande</b>\n(Geländemodell mit 2 m Auflösung). Die Auswahl erscheint nur, wenn der Kartenmittelpunkt dort liegt.\nDie Kacheln kommen von PDOK, ein Fenster zeigt den Fortschritt und lässt sich abbrechen, geladene\nKacheln liegen im Zwischenspeicher. Auf Wasserflächen hat das AHN keine Werte, dort ergänzt das\nStudio aus Copernicus. Die Voreinstellung „Empfohlen“ behandelt AHN wie DGM1.\n<i>AHN ist bei Amsterdam im Spiel getestet.</i></li>\n</ol>\n\n<h4>Einstellungen</h4>\n<p><b>Schnellstart:</b> Oben im Dialog unter <b>Voreinstellung</b> <i>„Empfohlen“</i> wählen\n(Glätten, Einebnen, Wasser nach OSM mit den Standardwerten) oder <i>„Original“</i> (alle\nOptionen aus, echte Höhen). Die Voreinstellung springt auf <i>„Eigene Einstellungen“</i>, sobald\ndu etwas von Hand änderst. Optionen, die OSM-Daten brauchen, bleiben ohne geladene OSM-Daten\naus. Die folgenden Schritte erklären die einzelnen Optionen.</p>\n<p>Empfohlene Reihenfolge. Jede Änderung aktualisiert die Vorschau und die Zahlen\nunten im Dialog.</p>\n<ol start="6">\n<li><b>Wasserhöhe</b> prüfen. Tipp: etwas höher als der tiefste Teil des Flusses, aber nicht\nso hoch, dass der Fluss an der höchsten Stelle mehr als 10 bis 15 m über dem Pegel liegt.\nBei Flüssen mit Gefälle (zum Beispiel Rhein) ist das ein Kompromiss. Der Knopf\n<b>„Wasserhöhe aus den OSM-Gewässern vorschlagen“</b> setzt sie in die Mitte zwischen\ntiefstem und höchstem Punkt des Hauptflusses und passt die Grenze „Nur Gewässer bis“\nan (braucht OSM-Daten).</li>\n<li><b>Gelände glätten</b> anhaken, Standard 15 m. Entfernt die Treppenstufen an den Hängen\n(das Höhenmodell hat nur 30 m pro Pixel, das Spiel 4 m). Bei DGM1 ist Glätten meist nicht\nnötig, das Modell ist schon genau, die Voreinstellung „Empfohlen“ lässt es dort aus.</li>\n<li><b>Trassen und Siedlungen einebnen</b> anhaken, Standard 60 m (bei „Empfohlen“ mit DGM1: 10 m). Bahnstrecken, größere\nStraßen und Gebäude werden abgeflacht, damit im Spiel weniger Rampen nötig sind. Braucht\nOSM-Daten. <i>Im Spiel getestet, funktioniert.</i></li>\n<li><b>Wasser nur dort, wo OpenStreetMap Wasser hat</b> anhaken (empfohlen). Verhindert\nüberflutete Auen und Tümpel. Standardwerte: Böschung 60 m (bei „Empfohlen“ mit DGM1: 10 m; breiter = flacheres Ufer), Tiefe\nam Ufer 2 m, Tiefe in der Mitte 8 m (Fahrrinne), Ufer über Wasser 2 m, nur Gewässer bis\n15 m über Wasserspiegel (höher gelegene Bäche und Bergseen bleiben unverändert). Die Option\n„Terrain sanft ans Wasserniveau anpassen“ schaltet sich dabei ab, beide zusammen gehen\nnicht.</li>\n<li><b>Höhen stauchen</b> gegen weiße und graue Flächen auf den Höhen. Das Spiel färbt nach der Höhe der\nimportierten Werte (Fels ab etwa 325-350 m, Schnee ab etwa 375-425 m). Mit dem Haken „Werte auf Wasserhöhe\n0 beziehen“ (Schritt 13) ist das die Höhe über dem Wasser, ohne ihn zählt die Höhe über Meer. Die höchste\nStelle landet auf dem eingestellten Anteil, der untere Teil des Geländes bleibt unverändert. Beim Rhein hat\n45 % funktioniert, bei Bern etwa 75 % (mit dem Haken). Standard 100 % = unverändert. Der Dialog zeigt unten\neinen Hinweis, wenn das Gelände zu hoch liegt.</li>\n<li><b>Gefälle ausgleichen</b> für lange Flüsse mit starkem Gefälle (zum Beispiel der Rhein von\nKoblenz bis Bingen, rund 18 m). Es legt Flüsse und Seen auf eine gemeinsame Ebene und verschiebt\ndabei alle Höhen: Die Zahlen für das Spiel ändern sich stark, die absoluten Höhen über NN stimmen\ndanach nicht mehr. Standard: Stärke 100 %, Glättung 400 m, Bezug: Gewässer bis 30 m über dem\nWasserspiegel. Im Test am Rhein (Bingen bis Koblenz, DGM1, Größenwahnsinnig 1:5, Wasserhöhe 70 m)\nwaren im Spiel beide Enden des Flusses gefüllt.</li>\n</ol>\n\n<h4>Höhenfenster (Grenzen des Karteneditors)</h4>\n<p>Der Karteneditor von TPF3 nimmt beim Import nur Höhen von <b>−100 bis 3177 m</b> an (im Spiel\ngetestet). Liegt das Gelände darüber oder darunter, zum Beispiel in den Alpen, zeigt der Dialog unten\neinen Hinweis. Dann den Haken <b>Höhenfenster begrenzen</b> setzen. Das Fenster gilt in den Werten, die\ndu im Editor einträgst: Mit dem Haken „Werte auf Wasserhöhe 0 beziehen“ ist es relativ zur Wasserhöhe.\nVoreingestellt ist der Bereich des Geländes innerhalb der Editor-Grenzen. Mit den Feldern <b>Fenster\nvon … bis</b> wird es enger, der <b>Schieberegler</b> verschiebt es über den ganzen Bereich des Editors: nach oben werden tiefe\nStellen abgeschnitten, nach unten die Gipfel gekappt (gerechnet wird beim Loslassen).\nFür alles außerhalb des Fensters gibt es drei Modi:</p>\n<ul>\n<li><b>Oben kappen</b>: Alles über dem Fenster wird flach auf die Obergrenze gesetzt, die Gipfel werden\nplaniert. Das Fenster liegt zunächst an der tiefsten Stelle.</li>\n<li><b>Unten abschneiden</b>: Alles unter dem Fenster wird flach auf die Untergrenze gesetzt, tiefe\nStellen werden planiert. Das Fenster liegt zunächst an der höchsten Stelle.</li>\n<li><b>Stauchen</b>: Das ganze Gelände wird ins Fenster gedrückt, über und unter der Wasserhöhe\ngetrennt. Die Wasserhöhe bleibt dabei erhalten, ein Gelände, das schon passt, wird nicht gestreckt.</li>\n</ul>\n<p>Die Vorschau färbt die betroffenen Stellen ein: <b>rot</b> = tiefer gesetzt (oben gekappt oder\ngestaucht), <b>hellblau</b> = höher gesetzt (unten abgeschnitten). Darunter steht zum Beispiel\n„4,2 % der Fläche werden planiert“, gerechnet auf der ganzen Karte. Vorschau, Zahlen unten und\nexportierte Datei benutzen dasselbe Raster. Liegt die Wasserhöhe außerhalb des Fensters, warnt der\nDialog.</p>\n\n<h4>Kontrolle und Export</h4>\n<ol start="12">\n<li>In der Vorschau prüfen: Der Fluss sollte ein durchgehendes Band im Tal sein, keine\ngeraden Streifen oder Keile, keine Tümpel außer denen aus OSM.</li>\n<li><b>Unten im Dialog den Text lesen</b> und abschreiben oder fotografieren:\n<i>„Im TPF3-Import eintragen: Mindesthöhe …, Maximalhöhe …, Wasserhöhe …“</i> und\n<i>„Kartengröße und -format im Spiel: …“</i>. Das sind die <b>echten Höhen</b> (positive\nWerte über NN). Diese Zahlen gelten immer für genau die aktuellen Einstellungen. Mit dem Haken\n<b>„Werte auf Wasserhöhe 0 beziehen“</b> schaltest du auf die Variante um, die das TPF3-Wiki\nfür Biome und Materialien empfiehlt (Mindesthöhe kann dabei negativ werden). Mit echten\nHöhen liegt alles entsprechend höher im Spiel, weiße Flächen auf den Höhen können dadurch\nzunehmen.</li>\n<li><b>Exportieren…</b> Der Dialog schlägt den heightmaps-Ordner von TPF3 vor. Gib der Datei\neinen <b>eindeutigen Namen</b>, zum Beispiel <tt>rhein_osmwasser.png</tt>.</li>\n</ol>\n\n<h3>Teil B: In TPF3</h3>\n<ol start="15">\n<li>Den Karteneditor öffnen. Bei den Einstellungen unter <b>Welt</b> dieselbe\n<b>Kartengröße</b> und dasselbe <b>Kartenformat</b> wählen wie im Studio-Text. Nur dann\npasst das Seitenverhältnis, das Spiel streckt jedes Bild auf die Kartengröße. Fehlt eine\nGröße (zum Beispiel Gigantomanisch), steht laut Wiki in der <tt>settings.lua</tt> der Schalter\n<tt>experimentalMapFeatures</tt>.</li>\n<li>Den Dialog <b>Heightmap importieren</b> öffnen (Reiter <b>Heightmap</b>).</li>\n<li>In der Liste die exportierte Datei anklicken. Steht sie nicht drin: Dialog schließen und\nneu öffnen und prüfen, ob die Datei im Ordner <tt>heightmaps</tt> liegt.</li>\n<li>Werte eintragen: <b>Mindesthöhe</b>, <b>Maximalhöhe</b> und <b>Wasserhöhe</b> genau wie im\nStudio-Text, <b>Assets behalten: Nein</b>.</li>\n<li>Die Vorschau rechts ansehen: Stimmt die Form? Steht nur der Fluss unter Wasser (blau)?</li>\n<li><b>Import</b> klicken.</li>\n</ol>\n\n<h4>Optional: Bäume (Reiter Biome)</h4>\n<ol start="21">\n<li>Die Biome-Maske bestimmt die Baumverteilung. Das Studio kann sie aus der OSM-Landnutzung\nerzeugen: im Heightmap-Dialog <b>Biome-Maske aus OSM…</b> (braucht geladene OSM-Daten). Die Datei\nmuss im Ordner <tt>biomes</tt> liegen, damit der Biome-Reiter sie findet. Eine einheitliche Maske\nreicht zum Test\n(Graustufe 77 = Biom 1, 128 = Biom 2, 179 = Biom 3, fertige Testmasken <tt>biome_einheitlich_1.png</tt> bis\n<tt>_3.png</tt> liegen im Projektordner unter <tt>docs\\testbilder</tt>, jeweils eine Datei im Ordner\n<tt>biomes</tt>). Bei <b>Biome</b> die Datei wählen, <b>Berge</b> und <b>Flüsse</b> leer\nlassen, <b>Anwenden</b>. Im Test erzeugt die Flüsse-Maske keinen Fluss, und die Berge-Maske\nentfernt keine weißen Flächen.</li>\n</ol>\n\n<h4>Optional: Städte und Industrien</h4>\n<ol start="22">\n<li>Im Heightmap-Dialog <b>Städte aus OSM…</b> und <b>Industrien aus OSM…</b> (brauchen geladene\nOSM-Daten). Sie erzeugen Dateien für den Ordner <tt>towns_industries</tt>, die der Editor von\nTPF3 importieren kann. Bei den Städten stellst du die Größe per Faktor und die Auswahl je Ort ein.\nBei den Industrien werden Hang, Wasser und Kartenrand geprüft.</li>\n</ol>\n\n<h4>Optional: Bahnhofsplan zum Nachbauen</h4>\n<ol start="23">\n<li><b>Bahnhofsplan zum Nachbauen…</b> ist ein Bauplan zum Nachbauen echter Bahnhöfe, denn das Spiel kann keine Bahnhöfe importieren. Die Funktion speichert <tt>bahnhoefe.json</tt> (alles) und <tt>bahnhoefe.csv</tt>\n(eine Zeile je Bahnhof) mit Bahnsteigen, Haltepositionen und Status. Die Koordinaten sind Meter ab\nKartenmitte. Im Spiel wird dadurch nichts gebaut und der Editor importiert die Dateien nicht. Sie\nhelfen beim eigenen Bauen. Nach <b>OSM laden</b> zeigt die Karte die Bahnhöfe auch als Marker.</li>\n</ol>\n\n<h3>Teil C: Wenn etwas nicht stimmt</h3>\n<table border="1" cellspacing="0" cellpadding="5">\n<tr><th align="left">Problem</th><th align="left">Ursache und Lösung</th></tr>\n<tr><td>Der Fluss ist ein riesiger See</td><td>Das Spiel kennt nur einen Wasserspiegel\nund flutet die Aue. <b>Wasser nur dort, wo OpenStreetMap Wasser hat</b> anhaken.</td></tr>\n<tr><td>Der Fluss fällt stellenweise trocken</td><td>Wasserhöhe im Studio etwas erhöhen, die\nZahlen für das Spiel neu ablesen.</td></tr>\n<tr><td>Der Fluss bleibt im oberen Teil trocken (starkes Gefälle, zum Beispiel Koblenz–Bingen\nmit rund 18 m)</td><td>Zuerst <b>Gefälle ausgleichen</b> anhaken (Schritt 11), das hat am Rhein geholfen. Alternativ\nbei „Wasser nur dort, wo OpenStreetMap Wasser hat“ die Grenze\n<b>„Nur Gewässer bis … m über Wasserspiegel“</b> auf 25 bis 30 m erhöhen. Zusätzlich die\nWasserhöhe in die Mitte zwischen tiefstem und höchstem Flussabschnitt legen (dort etwa\n68 m), dann werden beide Enden um etwa gleich viel korrigiert. <i>Im Spiel\ngeprüft.</i></td></tr>\n<tr><td>Steile Wand am Ufer</td><td>Böschung von 60 auf 100 m erhöhen. Bei Schluchten\n(Mittelrhein) ist ein Teil natürlich.</td></tr>\n<tr><td>Treppenstufen an den Hängen</td><td><b>Gelände glätten</b>, 15 m, bei Bedarf\n30 m.</td></tr>\n<tr><td>Das ganze Gelände ist weiß oder grau (zum Beispiel in der Schweiz, im Mittelland oder in den\nAlpen)</td><td>Das Gelände liegt ganz über der Schneegrenze des Spiels, weil die Höhen über Meer eingetragen\nwerden (Bern: 488 bis 936 m). Haken <b>„Werte auf Wasserhöhe 0 beziehen“</b> setzen, <b>Höhen stauchen</b>\n(bei Bern etwa 75 %), neue Zahlen unten ablesen, neu exportieren und mit den neuen Zahlen importieren.</td></tr>\n<tr><td>Der Editor nimmt die Höhen nicht an, oder das Gelände ragt über 3177 m (Alpen)</td><td>Der Editor nimmt nur −100 bis 3177 m. <b>Höhenfenster begrenzen</b> anhaken, Modus wählen (Oben kappen, Unten abschneiden oder Stauchen), neue Zahlen unten ablesen. Die Zeile unter dem Fenster zeigt, wie viel Fläche planiert wird.</td></tr>\n<tr><td>Weiße Flächen auf den Höhen</td><td>Schneegrenze im Spiel. Schneegrenzen-Test\nmachen, dann <b>Höhen stauchen</b>.</td></tr>\n<tr><td>Graue Felsstreifen an Hängen</td><td>Ab einer Neigung färbt das Spiel Fels. Hänge mit\nder Böschung oder dem Stauchen abmildern.</td></tr>\n<tr><td>Das Gelände ist im Spiel verzerrt</td><td>Kartengröße oder -format im Spiel passt nicht\nzum Studio-Text.</td></tr>\n<tr><td>Falsche Höhen im Spiel</td><td>Die Zahlen unten im Dialog benutzen, nicht alte Werte.\nSie ändern sich mit jeder Option.</td></tr>\n<tr><td>Meldung „Keine Gewässer“</td><td>Zuerst <b>Werkzeuge → OSM laden</b> für denselben\nAusschnitt.</td></tr>\n<tr><td>Im Spiel „Map preview exception … No such file“</td><td>Die Datei wurde gelöscht\noder umbenannt. Dialog neu öffnen und die Datei neu wählen.</td></tr>\n</table>\n\n<h4>Schneegrenzen-Test (einmalig)</h4>\n<ol>\n<li>Die Testdatei <tt>hoehen_schneegrenze_test.png</tt> (im Projektordner unter <tt>docs\\testbilder</tt>, zwölf Terrassen von 25 m bis 575 m in\n50-m-Stufen, unten am niedrigsten) nach <tt>heightmaps</tt> kopieren.</li>\n<li>Im Spiel die Kartengröße mit Format 1:5 wählen und mit <b>Mindesthöhe 0, Maximalhöhe 600,\nWasserhöhe 0</b> importieren (diese Werte gelten nur für die Testdatei).</li>\n<li>Von unten zählen, ab der wievielten Terrasse Weiß beginnt. Höhe = 25 + 50 × (Nummer − 1).</li>\n</ol>\n\n<h3>Quellen bei veröffentlichten Karten</h3>\n<p>Der Knopf <b>Beschreibung zum Teilen…</b> im Heightmap-Dialog erzeugt einen fertigen\nText mit diesen Angaben (Markdown, Steam-BBCode oder Klartext). Er ersetzt nicht die\nLizenzbedingungen der Quellen, bitte die Bedingungen der jeweiligen Quelle selbst prüfen.</p>\n<ul>\n<li>Höhen bei Quelle Copernicus: produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014 and\n© Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and\nESA; all rights reserved. Die Lizenz verlangt dazu den Satz „The organisations in charge of the\nCopernicus programme by law or by delegation do not incur any liability for any use of the\nCopernicus WorldDEM-30“ (eine Übersetzung ist erlaubt). Der Vermerk gilt für veränderte Daten,\nund das Studio verändert sie immer (zugeschnitten, neu abgetastet). Er gilt auch, wenn Copernicus\nnur Lücken im DGM1, in swissALTI3D oder im AHN ergänzt.</li>\n<li>Höhen bei Quelle DGM1: © GeoBasis-DE / Landesvermessung des jeweiligen Bundeslandes\n(zum Beispiel © GeoBasis-DE / LVermGeoRP), Datenlizenz Deutschland – Namensnennung –\nVersion 2.0 (dl-de/by-2-0, www.govdata.de/dl-de/by-2-0) beziehungsweise CC BY 4.0, je nach Land.\nDer genaue Vermerk steht nach dem Laden im Heightmap-Dialog unter der Höhenquelle. Die Lizenz\ndl-de/by-2-0 verlangt zusätzlich den Hinweis, dass die Daten geändert wurden. Bereitgestellt über\nhoehendaten.de.</li>\n<li>Höhen bei Quelle swissALTI3D: © swisstopo (Bundesamt für Landestopografie swisstopo),\nswissALTI3D. Die Quellenangabe ist nach den Nutzungsbedingungen von swisstopo Pflicht.</li>\n<li>Höhen bei Quelle AHN: © Rijkswaterstaat / AHN (Actueel Hoogtebestand Nederland), Lizenz CC0 1.0.\nEine Quellenangabe ist nicht verlangt, das Studio führt sie trotzdem mit.</li>\n<li>Karten- und Gewässerdaten: © OpenStreetMap-Mitwirkende, Lizenz ODbL\n(www.openstreetmap.org/copyright).</li>\n<li>Relief-Hintergrund im Studio: AWS Terrain Tiles (Mapzen/Tilezen).</li>\n</ul>\n':
        '\n<h2>Heightmap from the Studio to Transport Fever 3</h2>\n<p>Step by step from the empty map to the imported heightmap.\nAnything not yet tested in the game is marked as such.</p>\n\n<h3>Part A: In the Studio</h3>\n\n<h4>Define the section</h4>\n<ol>\n<li>In the panel on the map, choose <b>Map source</b> &rarr; ideally <b>Map + relief</b>\nso that you can see valleys and slopes. Zoom to the area you want. Optionally place a marker in the middle\nwith the <b>Marker</b> tool (it provides the centre point).</li>\n<li><b>Tools &rarr; Rectangle tool</b>: check the centre point, choose <b>Map size</b> and\n<b>Format</b> exactly as in the game, and adjust the <b>Rotation angle</b> until the band fits your\nriver or route. OK. The blue band can be moved with the blue dot\nand rotated with the orange one.</li>\n</ol>\n\n<h4>Load OSM data</h4>\n<ol start="3">\n<li><b>Tools &rarr; Load OSM</b> and wait. Large areas take a few minutes.\nWithout OSM data the options &ldquo;Water only where OpenStreetMap has water&rdquo;\nand &ldquo;Flatten routes and settlements&rdquo; do not work.</li>\n</ol>\n\n<h4>Get elevation data (in this dialog)</h4>\n<ol start="4">\n<li>Optionally <b>Quick preview</b> (coarse, available immediately, not exportable).</li>\n<li>At the top, choose the <b>Elevation source</b>: <b>Copernicus</b> (worldwide, 30 m, fast) or, for\nmaps in Germany, <b>DGM1 Germany</b> (1 m terrain model of the federal states, more accurate on\nslopes and embankments). Then <b>Download elevation data</b> and wait until &ldquo;Loaded: &hellip;\npixels&rdquo; appears at the top. The first time, the Studio downloads the tiles; afterwards it is faster.\n<br>With DGM1 the tiles come through the web service hoehendaten.de, at most about 20 tiles\nper minute: a large map takes about half an hour. The window shows the progress\nand can be cancelled; tiles that have already been loaded are skipped next time. If you\ndownloaded the tiles yourself from a state portal, choose <b>DGM1 from own\nGeoTIFF tiles</b> and the folder (the tiles must lie on the 1 km grid). Where DGM1 data\nis missing, the Studio fills in from Copernicus. The quick preview always uses Copernicus.\n<i>DGM1 has been tested in the game on the Rhine (Bingen to Koblenz, Gr&ouml;&szlig;enwahnsinnig 1:5).</i>\n<br>For maps in <b>Switzerland</b> or Liechtenstein there is <b>swissALTI3D Switzerland</b>\n(terrain model from swisstopo with 2 m resolution). The option only appears if the map centre\nlies there. The tiles come from data.geo.admin.ch; a window shows the progress and can be\ncancelled, and loaded tiles are kept in the cache. Where data is missing, the Studio fills in from\nCopernicus. The &ldquo;Recommended&rdquo; preset treats swissALTI3D like DGM1.\n<i>swissALTI3D has been tested in the game near Bern.</i>\n<br>For maps in the <b>Netherlands</b> there is <b>AHN Netherlands</b>\n(terrain model with 2 m resolution). The option only appears if the map centre lies there.\nThe tiles come from PDOK; a window shows the progress and can be cancelled, and loaded tiles\nare kept in the cache. The AHN has no values on water, there the Studio fills in from\nCopernicus. The &ldquo;Recommended&rdquo; preset treats AHN like DGM1.\n<i>AHN has been tested in the game near Amsterdam.</i></li>\n</ol>\n\n<h4>Settings</h4>\n<p><b>Quick start:</b> At the top of the dialog, under <b>Preset</b>, choose <i>&ldquo;Recommended&rdquo;</i>\n(smoothing, flattening, water from OSM with the default values) or <i>&ldquo;Original&rdquo;</i> (all\noptions off, real elevations). The preset jumps to <i>&ldquo;Custom settings&rdquo;</i> as soon as\nyou change anything by hand. Options that need OSM data stay off while no OSM data is loaded.\nThe following steps explain the individual options.</p>\n<p>Recommended order. Every change updates the preview and the numbers\nat the bottom of the dialog.</p>\n<ol start="6">\n<li>Check the <b>Water level</b>. Tip: slightly higher than the lowest part of the river, but not\nso high that the river at its highest point lies more than 10 to 15 m above the level.\nFor rivers with a gradient (for example the Rhine) this is a compromise. The button\n<b>&ldquo;Suggest water level from the OSM waters&rdquo;</b> sets it halfway between the\nlowest and highest point of the main river and adjusts the limit &ldquo;Only waters up to&rdquo;\n(needs OSM data).</li>\n<li>Tick <b>Smooth terrain</b>, default 15 m. Removes the stair steps on the slopes\n(the elevation model has only 30 m per pixel, the game 4 m). With DGM1, smoothing is usually not\nneeded because the model is already accurate; the &ldquo;Recommended&rdquo; preset leaves it off there.</li>\n<li>Tick <b>Flatten routes and settlements</b>, default 60 m (with &ldquo;Recommended&rdquo; and DGM1: 10 m). Railway lines, major\nroads and buildings are flattened so that fewer ramps are needed in the game. Needs\nOSM data. <i>Tested in the game, it works.</i></li>\n<li>Tick <b>Water only where OpenStreetMap has water</b> (recommended). Prevents\nflooded floodplains and ponds. Default values: bank slope 60 m (with &ldquo;Recommended&rdquo; and DGM1: 10 m; wider = flatter bank), depth\nat the bank 2 m, depth in the middle 8 m (channel), bank above water 2 m, only waters up to\n15 m above the water level (streams and mountain lakes at higher elevations remain unchanged). The option\n&ldquo;Gently adjust terrain to the water level&rdquo; switches off automatically; the two cannot be used\ntogether.</li>\n<li><b>Compress elevations</b> against white and grey areas on the heights. The game colours by the height of the\nimported values (rock from about 325-350 m, snow from about 375-425 m). With the checkbox &ldquo;Relate values to water level\n0&rdquo; (step 13) this is the height above the water; without it, the height above sea level counts. The highest\npoint ends up at the set proportion, the lower part of the terrain stays unchanged. On the Rhine,\n45 % worked, near Bern about 75 % (with the checkbox). Default 100 % = unchanged. The dialog shows a note\nat the bottom if the terrain lies too high.</li>\n<li><b>Equalise river gradient</b> for long rivers with a steep gradient (for example the Rhine from\nKoblenz to Bingen, about 18 m). It puts rivers and lakes on a common level and shifts\nall elevations in the process: the numbers for the game change a lot, and the absolute elevations above sea level\nare no longer correct afterwards. Default: strength 100 %, smoothing 400 m, reference: waters up to 30 m above the\nwater level. In the test on the Rhine (Bingen to Koblenz, DGM1, Gr&ouml;&szlig;enwahnsinnig 1:5, water level 70 m),\nboth ends of the river were filled in the game.</li>\n</ol>\n\n<h4>Elevation window (limits of the map editor)</h4>\n<p>The TPF3 map editor only accepts elevations from <b>&minus;100 to 3177 m</b> on import (tested in the game). If the terrain lies above or below that, for example in the Alps, the dialog shows\na note at the bottom. Then tick <b>Limit elevation window</b>. The window applies to the values you\nenter in the editor: with the checkbox &ldquo;Relate values to water level 0&rdquo; it is relative to the water level.\nBy default it is the range of the terrain within the editor limits. With the fields <b>Window\nfrom &hellip; to</b> it becomes narrower, and the <b>slider</b> moves it across the whole range of the editor: moving it up cuts off low\nareas, moving it down clips the peaks (the calculation runs when you release it).\nThere are three modes for everything outside the window:</p>\n<ul>\n<li><b>Clip top</b>: Everything above the window is set flat to the upper limit, so the peaks are\nlevelled off. The window initially sits at the lowest point.</li>\n<li><b>Cut off bottom</b>: Everything below the window is set flat to the lower limit, so low\nareas are levelled off. The window initially sits at the highest point.</li>\n<li><b>Compress</b>: The whole terrain is squeezed into the window, above and below the water level\nseparately. The water level is preserved, and terrain that already fits is not stretched.</li>\n</ul>\n<p>The preview colours the affected areas: <b>red</b> = lowered (clipped at the top or\ncompressed), <b>light blue</b> = raised (cut off at the bottom). Below it you see, for example,\n&ldquo;4.2 % of the area is levelled&rdquo;, calculated on the whole map. The preview, the numbers at the bottom and the\nexported file use the same grid. If the water level lies outside the window, the\ndialog warns you.</p>\n\n<h4>Check and export</h4>\n<ol start="12">\n<li>Check the preview: the river should be a continuous band in the valley, with no\nstraight strips or wedges and no ponds other than those from OSM.</li>\n<li><b>Read the text at the bottom of the dialog</b> and write it down or photograph it:\n<i>&ldquo;Enter in the TPF3 import: minimum height &hellip;, maximum height &hellip;, water level &hellip;&rdquo;</i> and\n<i>&ldquo;Map size and format in the game: &hellip;&rdquo;</i>. These are the <b>real elevations</b> (positive\nvalues above sea level). These numbers always apply to exactly the current settings. With the checkbox\n<b>&ldquo;Relate values to water level 0&rdquo;</b> you switch to the variant that the TPF3 wiki\nrecommends for biomes and materials (the minimum height can become negative). With real\nelevations everything lies correspondingly higher in the game, so white areas on the heights may\nincrease.</li>\n<li><b>Export&hellip;</b> The dialog suggests the TPF3 heightmaps folder. Give the file\na <b>unique name</b>, for example <tt>rhein_osmwasser.png</tt>.</li>\n</ol>\n\n<h3>Part B: In TPF3</h3>\n<ol start="15">\n<li>Open the map editor. In the settings under <b>World</b>, choose the same\n<b>Map size</b> and the same <b>Map format</b> as in the Studio text. Only then\ndoes the aspect ratio fit; the game stretches every image to the map size. If a\nsize is missing (for example Gigantomanisch), the wiki says the switch\n<tt>experimentalMapFeatures</tt> must be set in <tt>settings.lua</tt>.</li>\n<li>Open the <b>Import heightmap</b> dialog (<b>Heightmap</b> tab).</li>\n<li>Click the exported file in the list. If it is not there: close and\nreopen the dialog and check that the file is in the <tt>heightmaps</tt> folder.</li>\n<li>Enter the values: <b>Minimum height</b>, <b>Maximum height</b> and <b>Water level</b> exactly as in the\nStudio text, <b>Keep assets: No</b>.</li>\n<li>Look at the preview on the right: is the shape right? Is only the river under water (blue)?</li>\n<li>Click <b>Import</b>.</li>\n</ol>\n\n<h4>Optional: Trees (Biomes tab)</h4>\n<ol start="21">\n<li>The biome mask determines the tree distribution. The Studio can create it from the OSM land use:\nin the heightmap dialog use <b>Biome mask from OSM&hellip;</b> (needs loaded OSM data). The file\nmust be in the <tt>biomes</tt> folder so that the Biomes tab finds it. A uniform mask\nis enough for a test\n(grey value 77 = biome 1, 128 = biome 2, 179 = biome 3; ready-made test masks <tt>biome_einheitlich_1.png</tt> to\n<tt>_3.png</tt> are in the project folder under <tt>docs\\\\testbilder</tt>, one file at a time in the folder\n<tt>biomes</tt>). Under <b>Biomes</b> choose the file, leave <b>Mountains</b> and <b>Rivers</b> empty,\n<b>Apply</b>. In the test, the Rivers mask does not create a river, and the Mountains mask\ndoes not remove white areas.</li>\n</ol>\n\n<h4>Optional: Towns and industries</h4>\n<ol start="22">\n<li>In the heightmap dialog use <b>Towns from OSM&hellip;</b> and <b>Industries from OSM&hellip;</b> (they need loaded\nOSM data). They create files for the <tt>towns_industries</tt> folder that the TPF3\neditor can import. For the towns you set the size by factor and the selection per place.\nFor the industries, slope, water and map edge are checked.</li>\n</ol>\n\n<h4>Optional: Station plan for rebuilding</h4>\n<ol start="23">\n<li><b>Station plan for rebuilding&hellip;</b> is a blueprint for rebuilding real stations, because the game cannot import stations. It saves <tt>bahnhoefe.json</tt> (everything) and <tt>bahnhoefe.csv</tt>\n(one row per station) with platforms, stop positions and status. The coordinates are metres from the\nmap centre. Nothing is built in the game by this, and the editor does not import the files. They\nhelp with your own building. After <b>Load OSM</b> the map also shows the stations as markers.</li>\n</ol>\n\n<h3>Part C: When something is wrong</h3>\n<table border="1" cellspacing="0" cellpadding="5">\n<tr><th align="left">Problem</th><th align="left">Cause and solution</th></tr>\n<tr><td>The river is a huge lake</td><td>The game knows only one water level\nand floods the floodplain. Tick <b>Water only where OpenStreetMap has water</b>.</td></tr>\n<tr><td>The river runs dry in places</td><td>Raise the water level in the Studio slightly and read the\nnumbers for the game again.</td></tr>\n<tr><td>The river stays dry in the upper part (steep gradient, for example Koblenz&ndash;Bingen\nwith about 18 m)</td><td>First tick <b>Equalise river gradient</b> (step 11); that helped on the Rhine. Alternatively, under\n&ldquo;Water only where OpenStreetMap has water&rdquo; raise the limit\n<b>&ldquo;Only waters up to &hellip; m above water level&rdquo;</b> to 25 to 30 m. Also\nput the water level halfway between the lowest and highest river section (about\n68 m there), so that both ends are corrected by about the same amount. <i>Checked\nin the game.</i></td></tr>\n<tr><td>Steep wall at the bank</td><td>Increase the bank slope from 60 to 100 m. In gorges\n(Middle Rhine) part of it is natural.</td></tr>\n<tr><td>Stair steps on the slopes</td><td><b>Smooth terrain</b>, 15 m, 30 m if\nneeded.</td></tr>\n<tr><td>The whole terrain is white or grey (for example in Switzerland, the Mittelland or the\nAlps)</td><td>The terrain lies entirely above the game\'s snow line, because the elevations above sea level\nare entered (Bern: 488 to 936 m). Tick <b>&ldquo;Relate values to water level 0&rdquo;</b>, set <b>Compress elevations</b>\n(about 75 % for Bern), read the new numbers at the bottom, export again and import with the new numbers.</td></tr>\n<tr><td>The editor does not accept the elevations, or the terrain exceeds 3177 m (Alps)</td><td>The editor only accepts &minus;100 to 3177 m. Tick <b>Limit elevation window</b>, choose a mode (Clip top, Cut off bottom or Compress), and read the new numbers at the bottom. The line below the window shows how much area is levelled.</td></tr>\n<tr><td>White areas on the heights</td><td>Snow line in the game. Do the snow line test,\nthen <b>Compress elevations</b>.</td></tr>\n<tr><td>Grey rock stripes on slopes</td><td>From a certain slope the game colours rock. Soften slopes with\nthe bank slope or with compression.</td></tr>\n<tr><td>The terrain is distorted in the game</td><td>The map size or format in the game does not match\nthe Studio text.</td></tr>\n<tr><td>Wrong elevations in the game</td><td>Use the numbers at the bottom of the dialog, not old values.\nThey change with every option.</td></tr>\n<tr><td>Message &ldquo;No waters&rdquo;</td><td>First <b>Tools &rarr; Load OSM</b> for the same\nsection.</td></tr>\n<tr><td>In the game &ldquo;Map preview exception &hellip; No such file&rdquo;</td><td>The file was deleted\nor renamed. Reopen the dialog and choose the file again.</td></tr>\n</table>\n\n<h4>Snow line test (one-off)</h4>\n<ol>\n<li>Copy the test file <tt>hoehen_schneegrenze_test.png</tt> (in the project folder under <tt>docs\\\\testbilder</tt>, twelve terraces from 25 m to 575 m in\n50 m steps, lowest at the bottom) to <tt>heightmaps</tt>.</li>\n<li>In the game choose the map size with format 1:5 and import with <b>Minimum height 0, Maximum height 600,\nWater level 0</b> (these values only apply to the test file).</li>\n<li>Count from the bottom to see at which terrace white begins. Height = 25 + 50 × (number − 1).</li>\n</ol>\n\n<h3>Sources for published maps</h3>\n<p>The <b>Description for sharing&hellip;</b> button in the heightmap dialog creates a ready-made\ntext with this information (Markdown, Steam BBCode or plain text). It does not replace the\nlicence terms of the sources, please check the terms of each source yourself.</p>\n<ul>\n<li>Elevations from the Copernicus source: produced using Copernicus WorldDEM-30 © DLR e.V. 2010-2014\nand © Airbus Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European Union and\nESA; all rights reserved. The licence also requires the sentence &ldquo;The organisations in charge of\nthe Copernicus programme by law or by delegation do not incur any liability for any use of the\nCopernicus WorldDEM-30&rdquo; (a translation is allowed). The notice applies to modified data, and\nthe Studio always modifies it (cropped, resampled). It also applies if Copernicus only fills gaps in\nDGM1, swissALTI3D or AHN.</li>\n<li>Elevations from the DGM1 source: © GeoBasis-DE / state survey of the respective federal state\n(for example © GeoBasis-DE / LVermGeoRP), Data licence Germany – Attribution –\nVersion 2.0 (dl-de/by-2-0, www.govdata.de/dl-de/by-2-0) or CC BY 4.0, depending on the state.\nThe exact notice is shown after loading in the heightmap dialog under the elevation source. The\nlicence dl-de/by-2-0 additionally requires a note that the data has been changed. Provided via\nhoehendaten.de.</li>\n<li>Elevations from the swissALTI3D source: © swisstopo (Federal Office of Topography swisstopo),\nswissALTI3D. Attribution is mandatory under the swisstopo terms of use.</li>\n<li>Elevations from the AHN source: © Rijkswaterstaat / AHN (Actueel Hoogtebestand Nederland), licence CC0 1.0.\nAttribution is not required, but the Studio includes it anyway.</li>\n<li>Map and water data: © OpenStreetMap contributors, licence ODbL\n(www.openstreetmap.org/copyright).</li>\n<li>Relief background in the Studio: AWS Terrain Tiles (Mapzen/Tilezen).</li>\n</ul>\n',
    'Alle Schritte müssen in dieser Reihenfolge ausgeführt werden. Die Karte muss vorher komplett leer sein (keine Straßen/Gleise/Vegetation, nur Terrain). Am besten zuerst mit einem kleinen Testausschnitt üben.':
        'All steps must be carried out in this order. The map must be completely empty beforehand (no roads/tracks/vegetation, terrain only). It is best to practise with a small test section first.',
    'Allgemeine Hinweise':
        'General notes',
    'Autobahnen bauen':
        'Build motorways',
    'Bei fehlendem Mod-Typ abbrechen (empfohlen zum Testen)':
        'Abort if a mod type is missing (recommended for testing)',
    'Brücken bauen':
        'Build bridges',
    'Flughafen-Straßen (braucht Airport-Roads-Mod)':
        'Airport roads (needs the Airport Roads mod)',
    'Fuß-/Radwege bauen':
        'Build footpaths/cycle paths',
    'Gleise bauen':
        'Build tracks',
    'Im Script Thread (Workaround ohne CommonAPI2, in UG Console: m.scriptevent.ScriptEvent("areas.buildAreas")). Braucht Forester-Mod (Version 1.4 Interface!) und Paver-Mod. Kann eine Weile dauern.':
        'In the Script Thread (workaround without CommonAPI2, in the UG Console: m.scriptevent.ScriptEvent("areas.buildAreas")). Needs the Forester mod (version 1.4 interface!) and the Paver mod. May take a while.',
    'Import-Anleitung (OSM-TPF2-Importer)':
        'Import guide (OSM-TPF2-Importer)',
    "In der UG Console zuerst die Optionen-Tabelle einfügen, DANACH den Aufruf. Dauer grob schätzbar: Anzahl Edges / 5 Sekunden (siehe Converter-Log), bei großen Karten mehrere Stunden. Bekannter Fallstrick ('Already called, reload osm_importer before use again'): Workaround ist, beides in einer Zeile auszuführen: asdf=1; ":
        "In the UG Console, first paste the options table, THEN the call. The duration can be roughly estimated: number of edges / 5 seconds (see the converter log), several hours for large maps. Known pitfall ('Already called, reload osm_importer before use again'): the workaround is to run both in one line: asdf=1; ",
    "In der UG Console, Zeile für Zeile. Bekannter Absturz ('proposalData.errorState.Empty()'): tritt auf, wenn eine Stadt zu nah an Wasser liegt - betroffene Stadt dann aus osmdata.lua entfernen.":
        "In the UG Console, line by line. Known crash ('proposalData.errorState.Empty()'): occurs when a town is too close to water - remove the affected town from osmdata.lua.",
    'In der UG Console. Muss NACH Schritt 3 kommen, da er Höhen verändert. Baut Einzelbäume, Brunnen, Poller, Litfaßsäulen.':
        'In the UG Console. Must come AFTER step 3, because it changes heights. Builds single trees, fountains, bollards, advertising columns.',
    'Knoten außerhalb der Kartengrenzen überspringen':
        'Skip nodes outside the map boundaries',
    'Kopieren':
        'Copy',
    'Normale Straßentypen bauen':
        'Build normal road types',
    'Optionen-Tabelle + Aufruf kopieren':
        'Copy options table + call',
    'Schritt 0: Initialisierung':
        'Step 0: Initialisation',
    'Schritt 1: Stadtnamen':
        'Step 1: Town names',
    'Schritt 2: Flächen (Wälder/Oberflächen)':
        'Step 2: Areas (forests/surfaces)',
    'Schritt 3: Straßen/Gleise (der lange Schritt)':
        'Step 3: Roads/tracks (the long step)',
    'Schritt 4: Objekte':
        'Step 4: Objects',
    'Signale bauen (nur deutsche Signale)':
        'Build signals (German signals only)',
    'Spiel pausieren. In UG Console UND Script Thread eingeben (Workaround für Script Thread ohne CommonAPI2: m.scriptevent.ScriptEvent("require-osm_importer.main")):':
        'Pause the game. Enter in the UG Console AND the Script Thread (workaround for the Script Thread without CommonAPI2: m.scriptevent.ScriptEvent("require-osm_importer.main")):',
    'Straßen bauen (inkl. Fußwege/Bäche)':
        'Build roads (incl. footpaths/streams)',
    'Straßenbahn als eigene Gleise (statt auf Straßen)':
        'Tram as separate tracks (instead of on roads)',
    'Tunnel bauen (Ergebnis oft unbefriedigend)':
        'Build tunnels (result often unsatisfactory)',
    'U-Bahn-/Stadtbahn-Gleise (subway/light_rail)':
        'Subway/light rail tracks (subway/light_rail)',
    'Wasserstraßen für Bäche/kleine Flüsse':
        'Waterways for streams/small rivers',
    "• Alle 4 Schritte sollten in derselben Sitzung direkt hintereinander laufen, nicht über mehrere Tage verteilt.\n• Bei Änderungen an osmdata.lua oder den Skripten: m.reload() nötig (Spielstand neu laden reicht nicht).\n• Schritt 3 lässt sich nicht zweimal ohne Reload ausführen.\n• Nach Schritt 3: im Log nach 'WARNING' und 'ERROR' suchen (stdout.txt), auch wenn der Prozess nicht abgebrochen ist.\n• Alle Schritte auf einer bereits bebauten Fläche können zu Problemen führen - die Karte muss vorher leer sein.":
        "• All 4 steps should run directly one after another in the same session, not spread over several days.\n• After changes to osmdata.lua or the scripts: m.reload() is required (reloading the savegame is not enough).\n• Step 3 cannot be run twice without a reload.\n• After step 3: search the log for 'WARNING' and 'ERROR' (stdout.txt), even if the process was not aborted.\n• Running any step on an area that is already built up can cause problems - the map must be empty beforehand.",
    'Datei-Menü':
        'File menu',
    'Bearbeiten-Menü':
        'Edit menu',
    'Ansicht-Menü':
        'View menu',
    'Werkzeuge-Menü':
        'Tools menu',
    'Heightmap-Dialog':
        'Heightmap dialog',
    'Karte und Ebenen':
        'Map and layers',
    'Hilfe-Menü':
        'Help menu',
    'Neu und Projekt schließen':
        'New and Close project',
    'Beide beginnen ein neues, leeres Projekt: Marker, Rechteck, OSM-Daten, eigene Objekte und die Rückgängig-Liste werden geleert, die Ebenen sind wieder ausgeblendet. Bei ungespeicherten Änderungen fragt das Studio vorher nach dem Speichern. Läuft gerade ein OSM-Download, geht es erst danach.':
        'Both start a new, empty project: markers, rectangle, OSM data, your own objects and the undo list are cleared, and the layers are hidden again. If there are unsaved changes, the Studio asks whether to save first. If an OSM download is running, this is only possible afterwards.',
    'Lädt ein gespeichertes Projekt (.tpf2ms) mit Projektname, Rechteck-Tool-Auswahl (inkl. Drehung), geladenen Layern und Heightmap-Export-Status. Beim erneuten Öffnen des Rechteck-Tools werden Mittelpunkt, Größe und Drehwinkel automatisch aus dem geladenen Projekt vorbelegt.':
        'Loads a saved project (.tpf2ms) with project name, rectangle tool selection (incl. rotation), loaded layers and heightmap export status. When you open the rectangle tool again, the centre point, size and rotation angle are pre-filled automatically from the loaded project.',
    'Speichern und Speichern unter...':
        'Save and Save as...',
    "Speichern schreibt in die Datei, die du zuletzt geöffnet oder gespeichert hast. Gibt es noch keine, fragt es nach dem Namen. 'Speichern unter...' fragt immer nach dem Namen. Beim Beenden fragt das Studio bei ungespeicherten Änderungen nach.":
        "Save writes to the file you opened or saved last. If there is none yet, it asks for a name. 'Save as...' always asks for a name. When you exit, the Studio asks if there are unsaved changes.",
    'Übersicht aller gespeicherten .tpf2ms-Projekte in einem gewählten Ordner (der Ordner wird gemerkt): Auswahl, ob OSM-Daten geladen sind, ob bereits eine Heightmap exportiert wurde, letztes Änderungsdatum. Doppelklick öffnet das Projekt direkt.':
        'Overview of all saved .tpf2ms projects in a chosen folder (the folder is remembered): selection, whether OSM data is loaded, whether a heightmap has already been exported, last modified date. Double-clicking opens the project directly.',
    "Projektname setzen/ändern (z.B. 'Rheintal', 'Nürnberg-Korridor'). Wird mit gespeichert und erscheint im Fenstertitel sowie im Projekt-Dashboard.":
        "Set/change the project name (e.g. 'Rhine Valley', 'Nuremberg corridor'). It is saved with the project and appears in the window title and in the project dashboard.",
    'Schließt das Studio.':
        'Closes the Studio.',
    'Rückgängig / Wiederholen':
        'Undo / Redo',
    'Macht Änderungen an Markern rückgängig oder stellt sie wieder her, zum Beispiel Umbenennen und Löschen.':
        'Undoes or restores changes to markers, for example renaming and deleting.',
    'Docks ein- und ausblenden':
        'Show and hide docks',
    'Blendet die Bereiche Projekt, Layer und Eigenschaften ein oder aus.':
        'Shows or hides the Project, Layers and Properties areas.',
    'Marker und Auswahl':
        'Marker and Select',
    'Marker setzen: ein Klick auf die Karte setzt einen Marker, der den Mittelpunkt für das Rechteck-Tool liefert. Auswahl: einen Bereich auf der Karte auswählen (zwei Ecken).':
        'Marker: a click on the map places a marker that provides the centre point for the rectangle tool. Select: select an area on the map (two corners).',
    'Zwei Punkte auf der Karte anklicken: erster Klick zeigt lat/lon, zweiter Klick zeigt zusätzlich die Distanz (als Linie auf der Karte und in der Statusleiste).':
        'Click two points on the map: the first click shows lat/lon, the second click additionally shows the distance (as a line on the map and in the status bar).',
    'Legt ein gedrehtes Kartenband an (Mittelpunkt, Größe, Drehwinkel). Im Dialog stellst du Breite und Länge des Mittelpunkts, die Kartengröße im Format des Spiels (der Dialog zeigt Kilometer und Pixel), den Drehwinkel und den Sicherheitsrand für Downloads ein (Standard 500 m, ein zusätzlicher Rand um das Rechteck). Das Rechteck lässt sich auf der Karte verschieben (blauer Punkt) und drehen (oranger Punkt). Beim erneuten Öffnen füllt es sich mit den Werten der aktuellen Projekt-Auswahl vor.':
        "Creates a rotated map band (centre point, size, rotation angle). In the dialog you set the latitude and longitude of the centre point, the map size in the game's format (the dialog shows kilometres and pixels), the rotation angle and the safety margin for downloads (default 500 m, an additional margin around the rectangle). The rectangle can be moved on the map (blue dot) and rotated (orange dot). When you open it again, it is pre-filled with the values of the current project selection.",
    'Lädt die Daten für den gewählten Ausschnitt über die Overpass-API von OpenStreetMap. Die Statusleiste zeigt den Fortschritt. Danach erscheinen die Bahnhöfe automatisch auf der Karte, die übrigen Ebenen schaltest du im Layer-Dock ein.':
        'Loads the data for the chosen section through the OpenStreetMap Overpass API. The status bar shows the progress. Afterwards the stations appear on the map automatically; you switch on the other layers in the Layers dock.',
    'Stellt per Checkboxen ein, was aus OpenStreetMap geladen wird: Gleistypen (Straßenbahn ein/aus), Straßentypen, Gebäude, Parks und Gärten, Flächennutzung, Vegetation, Gewässer, Orte, Siedlung/Heide/Moor/Fels (für die Biome) und Industrie-Objekte. Bahnhöfe und Haltepunkte werden immer mitgeladen. Zeigt eine Live-Vorschau der resultierenden Abfrage und erlaubt wiederverwendbare Vorlagen. Nach einer Änderung muss OSM neu geladen werden.':
        'Uses checkboxes to set what is loaded from OpenStreetMap: track types (tram on/off), road types, buildings, parks and gardens, land use, vegetation, waters, places, settlement/heath/bog/rock (for the biomes) and industry objects. Stations and halts are always loaded as well. Shows a live preview of the resulting query and allows reusable templates. After a change, OSM has to be loaded again.',
    'Setzt den fertigen Aufrufbefehl für main.exe bzw. main.py (über venv) automatisch aus der aktuellen Auswahl zusammen (Kartengröße + Bounds-Koordinaten als Arg 3/4) - mit Kopieren-Button. Warnt, wenn die Auswahl gedreht ist (der Converter kennt keine Drehung).':
        'Automatically assembles the finished call command for main.exe or main.py (via venv) from the current selection (map size + bounds coordinates as arg 3/4) - with a copy button. Warns if the selection is rotated (the converter does not know about rotation).',
    "Ampel-Checks für die geladenen OSM-Daten, bevor du weiterarbeitest: strukturelle Plausibilität (z.B. Knoten/Wege-Verhältnis), 0-Treffer trotz aktivierter Kategorie, besondere Prüfung für 'Orte' (0 Städte bei aktivierter Kategorie = Fehler). Dichte-Kennzahlen (Straßen/Gebäude/Orte pro km²) werden nur angezeigt, nicht bewertet.":
        "Traffic-light checks for the loaded OSM data before you continue: structural plausibility (e.g. node/way ratio), zero hits despite an enabled category, a special check for 'Places' (0 towns with the category enabled = error). Density figures (roads/buildings/places per km²) are only displayed, not rated.",
    'Öffnet den Heightmap-Dialog (siehe nächste Gruppe): Höhendaten laden, Gelände und Wasser einstellen, die Heightmap exportieren und Biome, Städte, Industrien und den Bahnhofsplan zum Nachbauen erzeugen.':
        'Opens the heightmap dialog (see next group): load elevation data, adjust terrain and water, export the heightmap and create biomes, towns, industries and the station plan for rebuilding.',
    'Höhenquelle':
        'Elevation source',
    'Copernicus: weltweit, aber nur 30 m fein und mit Baumkronen. DGM1 Deutschland: 1-m-Geländemodell der Bundesländer, die Kacheln werden über hoehendaten.de geladen (etwa 20 Kacheln pro Minute, danach liegen sie im Zwischenspeicher), die Quellenangabe zeigt der Dialog an. Eigene Kacheln: GeoTIFF-Dateien (1-km-Raster), die du selbst bei einem Landesportal heruntergeladen hast. swissALTI3D Schweiz: Geländemodell von swisstopo für die Schweiz und Liechtenstein (2 m), die Kacheln kommen von data.geo.admin.ch. Die Auswahl erscheint nur bei Karten dort. AHN Niederlande: Geländemodell der Niederlande (2 m), die Kacheln kommen von PDOK. Auch hier erscheint die Auswahl nur bei Karten dort. Wo DGM1-, swissALTI3D- oder AHN-Daten fehlen, ergänzt das Studio aus Copernicus.':
        'Copernicus: worldwide, but only 30 m resolution and including tree canopy. DGM1 Germany: 1 m terrain model of the federal states; the tiles are loaded through hoehendaten.de (about 20 tiles per minute, afterwards they are kept in the cache), and the dialog shows the source attribution. Own tiles: GeoTIFF files (1 km grid) that you downloaded yourself from a state portal. swissALTI3D Switzerland: terrain model from swisstopo for Switzerland and Liechtenstein (2 m); the tiles come from data.geo.admin.ch. The option only appears for maps there. AHN Netherlands: terrain model of the Netherlands (2 m); the tiles come from PDOK. Here too, the option only appears for maps there. Where DGM1, swissALTI3D or AHN data is missing, the Studio fills in from Copernicus.',
    'Schnellvorschau':
        'Quick preview',
    "Zeigt vor dem echten Download eine Vorschau in niedriger Auflösung. Sie nutzt immer Copernicus, auch wenn unten eine DGM1-Quelle gewählt ist. Danach lädt 'Höhendaten herunterladen' die volle Auflösung.":
        "Shows a low-resolution preview before the real download. It always uses Copernicus, even if a DGM1 source is selected below. Afterwards 'Download elevation data' loads the full resolution.",
    'Voreinstellung':
        'Preset',
    'Original: alle Optionen aus, die echten Höhen. Empfohlen: hängt von der Höhenquelle ab (bei Copernicus Glätten, Einebnen und Wasser nach OSM, bei DGM1 und swissALTI3D ohne Glätten, Einebnen 10 m und Wasser nach OSM mit Böschung 10 m). Optionen, die OSM-Daten brauchen, bleiben ohne geladene OSM-Daten aus. Eigene Einstellungen entstehen, sobald du etwas änderst.':
        'Original: all options off, the real elevations. Recommended: depends on the elevation source (with Copernicus smoothing, flattening and water from OSM; with DGM1 and swissALTI3D without smoothing, flattening 10 m and water from OSM with a 10 m bank slope). Options that need OSM data stay off while no OSM data is loaded. Custom settings are created as soon as you change something.',
    'Wasserhöhe':
        'Water level',
    "Das Spiel kennt nur eine Wasserhöhe. Der Dialog schlägt einen Wert aus der Fläche vor und erkennt Ausreißer wie Bergbau-Restlöcher. Dann lässt sich der Höhenbereich ohne sie darstellen ('Ausreißer ausschließen', standardmäßig aus). 'Wasserhöhe aus den OSM-Gewässern vorschlagen' liest die Höhen des Hauptflusses und setzt den Wert in die Mitte zwischen tiefstem und höchstem Punkt.":
        "The game knows only one water level. The dialog suggests a value from the area and detects outliers such as mining pits. The elevation range can then be shown without them ('Exclude outliers', off by default). 'Suggest water level from the OSM waters' reads the elevations of the main river and sets the value halfway between its lowest and highest point.",
    'Felsgrenze:':
        'Rock limit:',
    'Schneegrenze:':
        'Snow limit:',
    'Höhenzonen in der Vorschau zeigen (grün, Fels, Schnee)':
        'Show elevation zones in the preview (green, rock, snow)',
    'Maximum {max_m:.0f} m über Wasser. Anteile: grün {green:.1f} %, Fels {rock:.1f} %, Schnee {snow:.1f} %':
        'Maximum {max_m:.0f} m above water. Shares: green {green:.1f} %, rock {rock:.1f} %, snow {snow:.1f} %',
    'Echter Fels hängt zusätzlich an der Neigung. Das Overlay zeigt nur die Höhenzonen. Die Grenzen (Meter über dem Wasserspiegel) sind Schätzwerte und gelten nur für die Vorschau, nicht für den Export.':
        'Real rock also depends on the slope. The overlay shows only the elevation zones. The limits (metres above the water level) are estimates and apply to the preview only, not to the export.',
    'Höhenzonen in der Vorschau':
        'Elevation zones in the preview',
    "Zeigt in der Vorschau grün, Fels und Schnee nach der Höhe über dem Wasserspiegel. Felsgrenze und Schneegrenze stellst du mit Feld oder Schieber ein (Schätzwerte, nur für die Vorschau, nicht für den Export). Darunter stehen das Maximum und die Flächenanteile. Der Schieber unter 'Höhen stauchen auf' rechnet beim Loslassen neu. Echter Fels hängt im Spiel zusätzlich an der Neigung.":
        "Shows green, rock and snow in the preview according to the height above the water level. You set the rock limit and snow limit with the field or the slider (estimates, for the preview only, not for the export). Below it are the maximum and the area shares. The slider under 'Compress elevations to:' recalculates when you release it. In the game, real rock also depends on the slope.",
    'Bäume in der Höhe ausdünnen':
        'Thin out trees at altitude',
    'Ersetzt Biom 1 (Wiese mit Baumgruppen) ab der Grenze durch ein Biom ohne Bäume. Die Höhe kommt aus dem Heightmap-Dialog (mit allen Einstellungen). Ob die übrigen Biome Bäume haben, ist im Spiel nicht geprüft.':
        'Replaces biome 1 (meadow with groups of trees) above the limit with a biome without trees. The height comes from the heightmap dialog (with all its settings). Whether the other biomes have trees has not been checked in the game.',
    'Baumgrenze (m über Wasser):':
        'Tree limit (m above water):',
    'Ersatzbiom:':
        'Replacement biome:',
    'Weicher Übergang (m darunter):':
        'Soft transition (m below):',
    'Auf dieser Strecke unter der Baumgrenze werden die Baumgruppen nach oben hin allmählich weniger, statt an einer harten Linie zu enden. 0 = harte Linie.':
        'Over this distance below the tree limit the tree groups thin out gradually towards the top instead of ending at a hard line. 0 = hard line.',
    'Stauchfaktor (1 = Originalmaßstab, unter 1 = gedehnt):': 'Compression factor (1 = original scale, below 1 = stretched):',
    'Faktor unter 1: Das reale Gebiet ist kleiner als die Spielkarte, die Höhen werden entsprechend angehoben.': 'Factor below 1: the real area is smaller than the game map, heights are raised accordingly.',
    'Höhen-Faktor:': 'Height factor:',
    'Reale Fläche: {w:.1f} x {h:.1f} km, Höhen x{f:.3f}': 'Real area: {w:.1f} x {h:.1f} km, heights x{f:.3f}',
    'Wie oft die Kartengröße in das reale Gebiet passt. Beispiel: 14,3 km Spielkarte mit Faktor 5 ergibt 71,7 km reales Gebiet. Netz, Städte und Gelände werden entsprechend verkleinert.': 'How many times the map size fits into the real area. Example: a 14.3 km game map with factor 5 covers 71.7 km of real terrain. Network, towns and terrain are shrunk accordingly.',
    'Vorbelegt mit 1 / Stauchfaktor, damit die Berge im Verhältnis bleiben. Kleiner = flacher, 1 = reale Höhen.': 'Preset to 1 / compression factor so mountains keep their proportions. Smaller = flatter, 1 = real heights.',
    'Gebäude, Parks, Flächennutzung und Vegetation abschalten': 'Switch off buildings, parks, land use and vegetation',
    'Gestauchte Karte: Faktor {f:.1f}, reale Fläche {a:.0f} km². Gebäude, Parks, Flächennutzung und Vegetation erzeugen hier sehr große Datenmengen; für Gelände, Orte, Gleise und Straßen genügen die übrigen Kategorien.': 'Compressed map: factor {f:.1f}, real area {a:.0f} km². Buildings, parks, land use and vegetation produce very large amounts of data here; the other categories are enough for terrain, places, tracks and roads.',
    'Nur für sehr große Gebiete verwenden, z. B. 80 x 80 km auf eine Spielkarte. Bei normalen Karten bitte auf 1 lassen, sonst wird das Gebiet verkleinert.': 'Only use this for very large areas, e.g. 80 x 80 km on one game map. For normal maps please leave it at 1, otherwise the area is shrunk.',
    'Die Karte wird gestaucht: {w:.1f} x {h:.1f} km reales Gebiet werden auf {gw:.1f} x {gh:.1f} km Spielkarte verkleinert. Das ist nur für sehr große Gebiete gedacht (z. B. 80 x 80 km). Für eine normale Karte den Stauchfaktor auf 1 setzen. Trotzdem stauchen?': 'The map will be compressed: {w:.1f} x {h:.1f} km of real terrain will be shrunk onto a {gw:.1f} x {gh:.1f} km game map. This is only meant for very large areas (e.g. 80 x 80 km). For a normal map set the compression factor to 1. Compress anyway?',
    'Karte stauchen?': 'Compress map?',
    'Beispielwert Fisch/Maschinen (bisher)': 'Example value fish/machines (previous)',
    'Weglassen (Spiel entscheidet)': 'Omit (game decides)',
    'Leer (keine festen Forderungen)': 'Empty (no fixed demands)',
    'Zufall (pro Stadt)': 'Random (per town)',
    'Projekt-Datei öffnen...': 'Open project file...',
    'Eine einzelne .tpf2ms-Datei direkt wählen, egal in welchem Ordner.': 'Pick a single .tpf2ms file directly, in any folder.',
    'Projekte (*.tpf2ms)': 'Projects (*.tpf2ms)',
    'Seed (0 = zufällig):': 'Seed (0 = random):',
    'Nur für den Modus Zufall: gleicher Seed ergibt bei gleicher Stadtliste dieselben Warenforderungen. 0 = bei jedem Export anders.': 'Random mode only: the same seed gives the same cargo demands for the same town list. 0 = different on every export.',
    'Warenforderung:': 'Cargo demand:',
    'Welche Waren die Städte nachfragen. Zufall: je Stadt 1 Ware je Zeile (Gewerbe/Industrie), zusammen 2, aus den Waren, die von Beginn an freigeschaltet sind. Beispiel, Weglassen und Leer sind nicht geprüft: ausprobieren und beim Import auf Fehler achten.': 'Which goods the towns demand. Random: 1 good per row (commercial/industrial), 2 per town, from the goods unlocked from the start. Example, Omit and Empty are not checked: try them and watch for errors on import.',
    'Auch später freigeschaltete Waren': 'Also goods unlocked later',
    'Nimmt books, plastic, tires und cement dazu. Im Spiel erst nach der Freischaltung wirksam, vorher nur eine Warnung im Log.': 'Adds books, plastic, tires and cement. Only effective in the game once unlocked, before that only a log warning.',
    '\n\nDer Dateiname wurde ohne Umlaute und Sonderzeichen gespeichert, weil sie im Spiel Probleme machen können.': '\n\nThe file name was saved without umlauts and special characters because they can cause problems in the game.',
    'Gelände glätten und Höhen stauchen':
        'Smooth terrain and compress elevations',
    'Glätten gegen Treppenstufen und Kristallflächen an Hängen (das Copernicus-Modell hat nur etwa 30 m pro Pixel). Höhen stauchen drückt alle Höhen über dem Wasserspiegel auf einen Anteil, falls Hochflächen im Spiel über die Schneegrenze ragen (weiße Flächen). Die Hänge werden dabei flacher.':
        'Smoothing works against stair steps and crystal-like facets on slopes (the Copernicus model has only about 30 m per pixel). Compressing elevations squeezes all elevations above the water level to a proportion, in case plateaus rise above the snow line in the game (white areas). The slopes become flatter as a result.',
    'Höhenfenster begrenzen':
        'Limit elevation window',
    "Der Karteneditor von TPF3 nimmt nur Höhen von -100 bis 3177 m an. Mit dem Haken legst du das Gelände in ein Fenster (Felder 'Fenster von ... bis', ein Schieberegler verschiebt es). Für Werte außerhalb gibt es drei Modi: Oben kappen (Gipfel werden flach gesetzt), Unten abschneiden (Tiefen werden flach gesetzt) und Stauchen (alles wird ins Fenster gedrückt, die Wasserhöhe bleibt). Die Vorschau färbt betroffene Stellen ein (rot: tiefer gesetzt, hellblau: höher gesetzt) und zeigt, wie viel Fläche planiert wird. Vorschau, Zahlen und Export benutzen dasselbe Raster. Ohne Haken warnt der Dialog, wenn die Höhen außerhalb der Editor-Grenzen liegen.":
        "The TPF3 map editor only accepts elevations from -100 to 3177 m. With the checkbox you place the terrain in a window (fields 'Window from ... to', a slider moves it). There are three modes for values outside it: Clip top (peaks are set flat), Cut off bottom (depths are set flat) and Compress (everything is squeezed into the window, the water level is preserved). The preview colours affected areas (red: lowered, light blue: raised) and shows how much area is levelled. The preview, the numbers and the export use the same grid. Without the checkbox, the dialog warns if the elevations lie outside the editor limits.",
    'Legt Flüsse und Seen auf eine gemeinsame Ebene und zieht das Gelände relativ dazu mit. Das Relief über dem jeweiligen Wasserspiegel bleibt erhalten, die absoluten Höhen über NN stimmen danach aber nicht mehr. Gewässer, die deutlich höher liegen (Bergseen, Nebenflüsse), dienen nicht als Bezug.':
        'Puts rivers and lakes on a common level and pulls the terrain along relative to it. The relief above the respective water level is preserved, but the absolute elevations above sea level are no longer correct afterwards. Waters that lie considerably higher (mountain lakes, tributaries) do not serve as a reference.',
    'Gewässer bekommen ein festes Bett mit Böschung und Tiefe, alles andere Land liegt knapp über dem Wasserspiegel: keine überfluteten Auen und Tümpel. Ersetzt die sanfte Anpassung darunter.':
        'Waters get a fixed bed with a bank slope and depth, all other land lies just above the water level: no flooded floodplains and ponds. Replaces the gentle adjustment below.',
    'Bahnstrecken, größere Straßen und Gebäude aus OSM: das Gelände dort wird abgeflacht, damit im Spiel weniger Rampen nötig sind. Braucht geladene OSM-Daten. Die Glättung bestimmt, wie eben es wird.':
        'Railway lines, major roads and buildings from OSM: the terrain there is flattened so that fewer ramps are needed in the game. Needs loaded OSM data. The smoothing determines how flat it becomes.',
    'Wasser nur dort, wo OpenStreetMap Wasser hat':
        'Water only where OpenStreetMap has water',
    'Im TPF3-Import eintragen':
        'Enter in the TPF3 import',
    'Zeigt unten im Dialog Mindesthöhe, Maximalhöhe, Wasserhöhe und das Kartenformat, die beim Import der Heightmap im Editor von Transport Fever 3 eingetragen werden.':
        'Shows at the bottom of the dialog the minimum height, maximum height, water level and the map format that are entered when importing the heightmap in the Transport Fever 3 editor.',
    'Speichert die fertige Heightmap als 16-Bit-PNG und schlägt dafür den heightmaps-Ordner von TPF3 vor. Die Anleitung im Dialog öffnet mit F1.':
        'Saves the finished heightmap as a 16-bit PNG and suggests the TPF3 heightmaps folder for it. The guide in the dialog opens with F1.',
    'Erzeugt aus den geladenen OSM-Orten eine Städte-Datei für den Ordner towns_industries. Die Größe lässt sich per Faktor anpassen, die Auswahl erfolgt je Ort.':
        'Creates a towns file for the towns_industries folder from the loaded OSM places. The size can be adjusted by a factor, and the selection is made per place.',
    'Erzeugt aus geladenen OSM-Objekten (Höfe, Steinbrüche, Sägewerke, ...) eine Industrien-Datei für den Ordner towns_industries. Dabei werden Hang, Wasser und Kartenrand geprüft.':
        'Creates an industries file for the towns_industries folder from loaded OSM objects (farms, quarries, sawmills, ...). Slope, water and map edge are checked in the process.',
    'Bauplan zum Nachbauen echter Bahnhöfe: Das Spiel kann keine Bahnhöfe importieren. Liest Bahnhöfe, Haltepunkte, Bahnsteige, Bahnhofsgebäude und Haltepositionen aus den geladenen OSM-Daten (aufgegebene, im Bau befindliche und Betriebsbahnhöfe sind gekennzeichnet) und speichert sie als bahnhoefe.json (alles) und bahnhoefe.csv (eine Zeile je Bahnhof) mit Koordinaten in Metern ab Kartenmitte. Im Spiel wird nichts gebaut, die Dateien dienen als Nachschlagewerk. Aneinanderstoßende Bahnsteig-Wege gelten als ein Bahnsteig, bei Bahnsteigflächen zählt die Länge statt des Umfangs.':
        'Blueprint for rebuilding real stations: the game cannot import stations. Reads stations, halts, platforms, station buildings and stop positions from the loaded OSM data (abandoned, under-construction and service stations are marked) and saves them as bahnhoefe.json (everything) and bahnhoefe.csv (one row per station) with coordinates in metres from the map centre. Nothing is built in the game; the files serve as a reference. Adjoining platform ways count as one platform, and for platform areas the length counts instead of the perimeter.',
    'Kartenquelle':
        'Map source',
    "Wechselt zwischen der normalen Straßenkarte (OpenStreetMap) und 'Karte + Relief' mit einem im Browser berechneten Schattenrelief, das Täler, Hänge und Bergkämme zeigt. Die Eisenbahnkarte (OpenRailwayMap) legt Gleise, Bahnhöfe und Signale darüber, das Maß-Gitter hilft beim Abschätzen von Abständen und Größen.":
        "Switches between the standard road map (OpenStreetMap) and 'Map + relief' with a hillshade calculated in the browser that shows valleys, slopes and ridges. The railway map (OpenRailwayMap) overlays tracks, stations and signals, and the measuring grid helps to estimate distances and sizes.",
    'Layer-Dock':
        'Layers dock',
    'Je Ebene: Haken (ein- und ausblenden), Schloss (sperrt Auswahl und Bearbeitung in der Karte), Balken (Deckkraft) und Pfeile (Reihenfolge). Rechtsklick auf eine Zeile: anzeigen, ausblenden, sperren, entsperren oder die Deckkraft zurücksetzen.':
        'For each layer: checkbox (show and hide), lock (blocks selection and editing in the map), bar (opacity) and arrows (order). Right-click on a row: show, hide, lock, unlock or reset the opacity.',
    'Ebene Bahnhöfe':
        'Stations layer',
    "Nach 'OSM laden' erscheinen die Bahnhöfe als Kreise mit Namen auf der Karte. Blau ist ein Bahnhof, grün ein Haltepunkt, rot aufgegeben, orange im Bau, lila ein Betriebsbahnhof und grau ein zweifelhafter Eintrag (zum Beispiel Bergbahn). Die Namen erscheinen ab einer bestimmten Zoomstufe. Im Layer-Dock lässt sich die Ebene ein- und ausschalten.":
        "After 'Load OSM' the stations appear as circles with names on the map. Blue is a station, green a halt, red abandoned, orange under construction, purple a service station and grey a doubtful entry (for example a mountain railway). The names appear from a certain zoom level. The layer can be switched on and off in the Layers dock.",
    'Zeichnen und JSON':
        'Draw and JSON',
    "Eigene Straßen, Flüsse und Gebäude zeichnen: Knopf wählen, Punkte auf der Karte anklicken, dann 'Fertig'. 'JSON Export' speichert die Objekte der Karte als Datei, 'JSON Import' lädt sie wieder. 'Alle' und 'Keine' schalten alle Ebenen im Panel ein oder aus.":
        "Draw your own roads, rivers and buildings: choose a button, click points on the map, then 'Done'. 'JSON Export' saves the objects on the map as a file, 'JSON Import' loads them again. 'All' and 'None' switch all layers in the panel on or off.",
    'Marker-Liste (Dock Projekt)':
        'Marker list (Project dock)',
    'Rechtsklick auf einen Marker: auf den Marker zentrieren, umbenennen oder löschen. Doppelklick zentriert die Karte auf den Marker.':
        'Right-click on a marker: centre on the marker, rename or delete. Double-clicking centres the map on the marker.',
    'Funktionsübersicht (dieses Fenster)':
        'Feature overview (this window)',
    'Diese Liste der Funktionen des Studios, gruppiert nach Menü und Dialog.':
        "This list of the Studio's functions, grouped by menu and dialog.",
    'Funktionsübersicht':
        'Feature overview',
    'Übersicht der Funktionen des Studios, gruppiert nach dem Menü oder Dialog, in dem sie zu finden sind.':
        "Overview of the Studio's functions, grouped by the menu or dialog in which they can be found.",
    '\n\nHinweis: {outlier_count} Pixel ({value:.2f}% der Fläche) liegen deutlich außerhalb des üblichen Höhenbereichs der restlichen Fläche (z.B. einzelne Bergbau-Restlöcher oder Rand-Artefakte) - Höhenbereich {range_min:.0f}–{range_max:.0f} m. Ohne diese Ausreißer läge er bei {robust_range_min:.0f}–{robust_range_max:.0f} m, was mehr 16-Bit-Präzision für das eigentliche Gelände übrig lässt. Der Export nutzt weiterhin den vollen Bereich (nichts geht verloren), außer du wählst im Dialog explizit die engere Spanne.':
        '\n\nNote: {outlier_count} pixels ({value:.2f}% of the area) lie clearly outside the usual elevation range of the rest of the area (e.g. individual mining pits or edge artefacts) - elevation range {range_min:.0f}–{range_max:.0f} m. Without these outliers it would be {robust_range_min:.0f}–{robust_range_max:.0f} m, which leaves more 16-bit precision for the actual terrain. The export still uses the full range (nothing is lost), unless you explicitly choose the narrower range in the dialog.',
    '  {bridges_short} sehr kurze Bruecken werden als gewoehnliche Kante gebaut':
        '  {bridges_short} very short bridges are built as an ordinary edge',
    '  {junctions_merged} Einmuendungen zusammengelegt, {ways_dropped_merge} Kurzstuecke entfallen':
        '  {junctions_merged} junctions merged, {ways_dropped_merge} short pieces dropped',
    '  {merged_pairs} Richtungsfahrbahnen zusammengefasst':
        '  {merged_pairs} carriageways merged',
    '  {nodes_added} Knoten auf langen Kanten eingefügt':
        '  {nodes_added} nodes inserted on long edges',
    '  {oneway} Einbahnstrassen mit schmaler Einbahn-Vorlage':
        '  {oneway} one-way roads with the narrow one-way template',
    '  {roads_moved} Straßenknoten vom Gleis weggerückt (Mindestabstand)':
        '  {roads_moved} road nodes moved away from the track (minimum distance)',
    '  {tracks_removed} Doppelgleise entfernt':
        '  {tracks_removed} doubled tracks removed',
    '  {tracks_spaced} Gleisknoten auf gleichmäßigen Gleisabstand gerückt':
        '  {tracks_spaced} track nodes moved to an even track spacing',
    '  {tracks_unified} Gleiswege auf die Vorlage ihres Gleisnetzes angeglichen':
        '  {tracks_unified} track ways aligned to the template of their track network',
    "'Adjust Small Streets town new' deaktivieren.":
        "Disable 'Adjust Small Streets town new'.",
    "'No superelevation at speed restricted tracks' deaktivieren.":
        "Disable 'No superelevation at speed restricted tracks'.",
    "'Orte' war aktiviert, aber 0 Städte/Dörfer gefunden. Für ein bewohntes Gebiet ungewöhnlich - Download prüfen, bevor der grosse Lauf gestartet wird.":
        "'Places' was enabled, but 0 towns/villages were found. Unusual for an inhabited area - check the download before starting the big run.",
    "'Orte' war in der Overpass-Abfrage nicht aktiviert - unter Werkzeuge > Overpass-Abfrage einschalten, falls die Städteanzahl geprüft werden soll.":
        "'Places' was not enabled in the Overpass query - enable it under Tools > Overpass query if the number of towns is to be checked.",
    "'{label}' war in der Overpass-Abfrage aktiviert, aber es wurden 0 gefunden.":
        "'{label}' was enabled in the Overpass query, but 0 were found.",
    '0 Wege geladen - die Overpass-Antwort war vermutlich leer oder der Download ist fehlgeschlagen.':
        '0 ways loaded - the Overpass response was probably empty or the download failed.',
    'Achtung: Das ganze Gelände liegt über etwa {HIGH_TERRAIN_M:.0f} m. Im Spiel wird es dadurch komplett weiß (Schnee) oder grau (Fels). Den Haken „Werte auf Wasserhöhe 0 beziehen“ setzen und bei Bedarf „Höhen stauchen“ verwenden.':
        'Warning: The whole terrain lies above about {HIGH_TERRAIN_M:.0f} m. In the game it will therefore be completely white (snow) or grey (rock). Tick “Relate values to water level 0” and use “Compress elevations” if needed.',
    'Achtung: Der Karteneditor nimmt nur Höhen von {GAME_MIN_M:.0f} bis {GAME_MAX_M:.0f} m. Dein Bereich ({entered_min:.0f} bis {entered_max:.0f} m) liegt außerhalb. „Höhenfenster begrenzen“ anhaken oder „Höhen stauchen“ verwenden.':
        'Warning: The map editor only accepts elevations from {GAME_MIN_M:.0f} to {GAME_MAX_M:.0f} m. Your range ({entered_min:.0f} to {entered_max:.0f} m) lies outside it. Tick “Limit elevation window” or use “Compress elevations”.',
    'Ausgewähltes Gebiet: ca. {area_km2:.2f} km².':
        'Selected area: approx. {area_km2:.2f} km².',
    'Basis + Erweiterungen 1-3 vom selben Autor (sebbe_hv69signale_*).':
        'Base + extensions 1-3 by the same author (sebbe_hv69signale_*).',
    'Bekannter Absturzverursacher (nicht Teil der Importer-Anforderungen).':
        'Known cause of crashes (not part of the importer requirements).',
    'Brauerei':
        'Brewery',
    'Bruecken: {bridges}, Tunnel: {tunnels}':
        'Bridges: {bridges}, tunnels: {tunnels}',
    'Brückentypen':
        'Bridge types',
    'Chemiewerk':
        'Chemical plant',
    'Eisenerzmine (resource=iron_ore)':
        'Iron ore mine (resource=iron_ore)',
    'Empfohlen vor dem Import':
        'Recommended before the import',
    'Empfohlen, kein Pflicht-Mod.':
        'Recommended, not a mandatory mod.',
    'Fahrzeugfabrik':
        'Vehicle factory',
    'Fläche':
        'Area',
    'Forester / Bäume':
        'Forester / trees',
    'Forst (große Waldflächen)':
        'Forestry (large forest areas)',
    'Gebäudedichte':
        'Building density',
    'Gestaucht: Höhen über dem Bezugspunkt auf {value:.0f} %, darunter auf {value2:.0f} % ({percent} % der Fläche verändert).':
        'Compressed: elevations above the reference point to {value:.0f} %, below it to {value2:.0f} % ({percent} % of the area changed).',
    'GitHub-Mod, kein Workshop-Eintrag.':
        'GitHub mod, no Workshop entry.',
    'Glashütte':
        'Glassworks',
    'Hinweis: Die höchsten Stellen liegen bei etwa {top:.0f} m. Ab etwa {SNOW_LINE_M:.0f} m färbt das Spiel weiß. „Höhen stauchen“ verringert das.':
        'Note: The highest points are at about {top:.0f} m. From about {SNOW_LINE_M:.0f} m the game colours the terrain white. “Compress elevations” reduces this.',
    'Hoehendaten decken den Kartenausschnitt nicht vollstaendig ab (evtl. fehlt eine Randkachel).':
        'The elevation data does not completely cover the map section (an edge tile may be missing).',
    'Höhenbereich: {range_min_m:.0f} – {range_max_m:.0f} m':
        'Elevation range: {range_min_m:.0f} – {range_max_m:.0f} m',
    'Im Ordner {folder} liegen keine GeoTIFF-Dateien (.tif).':
        'There are no GeoTIFF files (.tif) in the folder {folder}.',
    'Kachel {ie}-{inn}: Antwort von swisstopo ist zu klein, vermutlich fehlerhaft.':
        'Tile {ie}-{inn}: the response from swisstopo is too small, probably faulty.',
    'Kachel {slot_prefix} konnte nicht geladen werden ({error}).':
        'Tile {slot_prefix} could not be loaded ({error}).',
    'Kachel {slot_prefix}: Daten nicht lesbar.':
        'Tile {slot_prefix}: data not readable.',
    'Kachel {tile_id} existiert nicht bei Copernicus DEM (vermutlich reines Wassergebiet ohne Landkachel: {url})':
        'Tile {tile_id} does not exist at Copernicus DEM (probably a pure water area without a land tile: {url})',
    'Kachel {value} von {count}':
        'Tile {value} of {count}',
    'Kartenausschnitt':
        'Map section',
    'Keine DGM1-Kacheln fuer diesen Ausschnitt gefunden. Liegt der Ausschnitt ausserhalb Deutschlands, bitte Copernicus waehlen.':
        'No DGM1 tiles found for this section. If the section lies outside Germany, please choose Copernicus.',
    'Keine Liniengeometrien für TPF2 vorhanden.':
        'No line geometries available for TPF2.',
    "Keine OSM-Daten geladen. Zuerst 'OSM laden' ausführen.":
        "No OSM data loaded. First run 'Load OSM'.",
    'Keine swissALTI3D-Kacheln fuer diesen Ausschnitt gefunden. Liegt der Ausschnitt ausserhalb der Schweiz und Liechtensteins, bitte Copernicus waehlen.':
        'No swissALTI3D tiles found for this section. If the section lies outside Switzerland and Liechtenstein, please choose Copernicus.',
    'Keiner der Overpass-Server war erreichbar.':
        'None of the Overpass servers could be reached.',
    'Knoten/Wege-Verhältnis':
        'Node/way ratio',
    'Knoten: {count} (vor der Vereinfachung {nodes_before} Punkte)':
        'Nodes: {count} (before simplification {nodes_before} points)',
    'Kohlemine (resource=coal)':
        'Coal mine (resource=coal)',
    'Konservenfabrik / Lebensmittel':
        'Cannery / food',
    'Lehmgrube (quarry + resource=clay)':
        'Clay pit (quarry + resource=clay)',
    'Maschinenfabrik':
        'Machine factory',
    'Messung: Startpunkt {lat:.6f}, {lon:.6f} (zweiten Punkt anklicken)':
        'Measurement: start point {lat:.6f}, {lon:.6f} (click the second point)',
    'Messung: {distance_text}':
        'Measurement: {distance_text}',
    'Möbelfabrik':
        'Furniture factory',
    'Nicht unterstützte Projektversion: {version}':
        'Unsupported project version: {version}',
    'Nichts wird gestaucht: Das Gelände passt schon ins Fenster.':
        'Nothing is compressed: the terrain already fits into the window.',
    'Nichts wird planiert: Das Gelände liegt ganz im Fenster. Mit dem Schieberegler oder engeren Feldern lässt sich das ändern.':
        'Nothing is levelled: the terrain lies entirely inside the window. You can change this with the slider or narrower fields.',
    'Nur bis Importer-Version 1.3 benoetigt.':
        'Only needed up to importer version 1.3.',
    'Nur noetig, falls das Gebiet elektrifizierte Bahnstrecken enthaelt.':
        'Only needed if the area contains electrified railway lines.',
    'Nur ueber transportfever.net erhaeltlich, kein fester Ordnername bekannt.':
        'Only available via transportfever.net, no fixed folder name known.',
    'Nur {ratio:.2f} Knoten pro Weg im Schnitt ({node_count} Knoten, {way_count} Wege). Ein Weg braucht mindestens 2 Knoten - der Download wirkt unvollständig.':
        'Only {ratio:.2f} nodes per way on average ({node_count} nodes, {way_count} ways). A way needs at least 2 nodes - the download looks incomplete.',
    'Objekte':
        'Objects',
    'Orte':
        'Places',
    'Ortsdichte':
        'Place density',
    'Paver / Bodentexturen':
        'Paver / ground textures',
    'Raffinerie':
        'Refinery',
    'Sandgrube (quarry + sand/gravel)':
        'Sand pit (quarry + sand/gravel)',
    'Signale':
        'Signals',
    'Stahlwerk':
        'Steelworks',
    'Steinbruch (landuse=quarry)':
        'Quarry (landuse=quarry)',
    'Straßendichte':
        'Road density',
    'Suche Kacheln bei swisstopo ({value} von {count})':
        'Searching for tiles at swisstopo ({value} of {count})',
    'Sägewerk':
        'Sawmill',
    'Textilfabrik':
        'Textile factory',
    'Unlesbare Antwort von hoehendaten.de: {exc}':
        'Unreadable response from hoehendaten.de: {exc}',
    'Unlesbare Antwort von swisstopo: {exc}':
        'Unreadable response from swisstopo: {exc}',
    'Viehzucht (building=cowshed/stable/sty)':
        'Livestock farm (building=cowshed/stable/sty)',
    'Vorschlag basiert auf dem {SUGGESTION_PERCENTILE}. Perzentil der Fläche (ohne die äußersten {EDGE_MARGIN_PX} Pixel Rand), das erfahrungsgemäß dem natürlichen Flussniveau entspricht. Bleiben nach dem Import Flüsse trocken, einen höheren Wert probieren; steht zu viel Fläche unter Wasser, einen niedrigeren.':
        'Suggestion is based on the {SUGGESTION_PERCENTILE}th percentile of the area (without the outermost {EDGE_MARGIN_PX} pixels of edge), which experience shows corresponds to the natural river level. If rivers stay dry after the import, try a higher value; if too much area is under water, a lower one.',
    'Wasserhöhe: {water_level_m:.0f} m':
        'Water level: {water_level_m:.0f} m',
    'Water 4 (4.2/4.3/4.4) und Street 4 mit blauem Wasser aktivieren.':
        'Enable Water 4 (4.2/4.3/4.4) and Street 4 with blue water.',
    'Wege':
        'Ways',
    'Wege: {ways_used} von {ways_osm} OSM-Wegen':
        'Ways: {ways_used} of {ways_osm} OSM ways',
    'Werkzeugfabrik':
        'Tool factory',
    'Wird auch fuer Bruecken-Typen verwendet.':
        'Also used for bridge types.',
    'Wird fuer die Signalplatzierung vorausgesetzt.':
        'Required for signal placement.',
    'Ziegelei':
        'Brickworks',
    'Zwingend genau diese Version (Interface-Variante) verwenden.':
        'Use exactly this version (interface variant).',
    'swisstopo nicht erreichbar ({error}).':
        'swisstopo not reachable ({error}).',
    'PDOK antwortet mit HTTP {status}.':
        'PDOK responded with HTTP {status}.',
    'PDOK nicht erreichbar ({error}).':
        'PDOK not reachable ({error}).',
    'PDOK meldet einen Fehler fuer Kachel {ie}-{inn}: {detail}':
        'PDOK reported an error for tile {ie}-{inn}: {detail}',
    'Kachel {ie}-{inn}: Antwort von PDOK ist kein GeoTIFF.':
        'Tile {ie}-{inn}: the response from PDOK is not a GeoTIFF.',
    'Kachel {ie}-{inn}: Antwort von PDOK nicht lesbar ({exc}).':
        'Tile {ie}-{inn}: the response from PDOK is not readable ({exc}).',
    'Kachel {ie}-{inn}: Antwort von PDOK ist kein Hoehenraster.':
        'Tile {ie}-{inn}: the response from PDOK is not an elevation raster.',
    'AHN Niederlande (2 m, über PDOK)':
        'AHN Netherlands (2 m, via PDOK)',
    'AHN Niederlande: Höhenmodell der Niederlande (2 m Auflösung, ohne Gebäude und Bewuchs). Die Kacheln werden von PDOK geladen und liegen danach im Zwischenspeicher. Nur bei Karten in den Niederlanden wählbar.':
        'AHN Netherlands: elevation model of the Netherlands (2 m resolution, without buildings and vegetation). The tiles are downloaded from PDOK and then kept in the cache. Only available for maps in the Netherlands.',
    'AHN-Kacheln laden':
        'Download AHN tiles',
    'Die Kacheln kommen von PDOK (Rijkswaterstaat, AHN). Bereits geladene Kacheln werden übersprungen. Du kannst jederzeit abbrechen und später weitermachen.':
        'The tiles come from PDOK (Rijkswaterstaat, AHN). Tiles that are already downloaded are skipped. You can cancel at any time and continue later.',
    'Keine AHN-Kacheln fuer diesen Ausschnitt gefunden. Liegt der Ausschnitt ausserhalb der Niederlande, bitte Copernicus waehlen.':
        'No AHN tiles found for this area. If the area is outside the Netherlands, please choose Copernicus.',
    'AHN Niederlande (2 m)':
        'AHN Netherlands (2 m)',
    'CC0 1.0 (frei nutzbar)':
        'CC0 1.0 (free to use)',
    'unbekannter Fehler':
        'unknown error',
    '{count} Orte gefunden.':
        '{count} places found.',
    '{count}× {label} gefunden.':
        '{count}× {label} found.',
    '{name}: Hoehenwerte nicht lesbar ({exc}). Die Datei bleibt zur Pruefung im Ordner liegen.':
        '{name}: elevation values not readable ({exc}). The file stays in the folder for inspection.',
    '{name}: Kachel liegt nicht auf dem 1-km-Raster (Ecke {e_ul:.1f} / {n_ul:.1f}). Solche Dateien werden nicht unterstuetzt.':
        '{name}: tile does not lie on the 1 km grid (corner {e_ul:.1f} / {n_ul:.1f}). Such files are not supported.',
    '{name}: Pixelgroesse {px} m passt nicht in eine 1-km-Kachel.':
        '{name}: pixel size {px} m does not fit into a 1 km tile.',
    '{name}: keine Georeferenzierung im GeoTIFF gefunden.':
        '{name}: no georeferencing found in the GeoTIFF.',
    '{name}: keine lesbare GeoTIFF-Datei ({exc}).':
        '{name}: not a readable GeoTIFF file ({exc}).',
    '{percent} % der Fläche werden planiert (oben gekappt: {percent2} %, unten abgeschnitten: {percent3} %).':
        '{percent} % of the area is levelled (clipped at the top: {percent2} %, cut off at the bottom: {percent3} %).',
    '{ratio:.2f} Knoten pro Weg im Schnitt - unauffällig.':
        '{ratio:.2f} nodes per way on average - nothing unusual.',
    '{value:.1f} Gebäude pro km² (nur zur eigenen Einschätzung).':
        '{value:.1f} buildings per km² (for your own assessment only).',
    '{value:.1f} Straßen-Segmente pro km² (nur zur eigenen Einschätzung, kein automatisches Urteil).':
        '{value:.1f} road segments per km² (for your own assessment only, no automatic verdict).',
    '{value:.2f} Orte pro 100 km² (nur zur eigenen Einschätzung).':
        '{value:.2f} places per 100 km² (for your own assessment only).',
    '{way_count} Wege geladen.':
        '{way_count} ways loaded.',
    'Ölplattform (offshore_platform)':
        'Oil platform (offshore_platform)',
    'Ölquelle (man_made=petroleum_well)':
        'Oil well (man_made=petroleum_well)',
    'Biom 0 - helle Wiese':
        'Biome 0 - light meadow',
    'Biom 1 - Wiese mit Baumgruppen':
        'Biome 1 - meadow with groups of trees',
    'Biom 2 - dunkle Wiese':
        'Biome 2 - dark meadow',
    'Biom 3 - trockene Steppe':
        'Biome 3 - dry steppe',
    'Biom 4 - gruen-braun gemischt':
        'Biome 4 - mixed green-brown',
    'Im TPF3-Import eintragen (auf Wasserhöhe 0 bezogen): Mindesthöhe {low:.0f}, Maximalhöhe {high:.0f}, Wasserhöhe 0':
        'Enter in the TPF3 import (relative to water level 0): minimum height {low:.0f}, maximum height {high:.0f}, water level 0',
    'Kein Ordner mit DGM1-Kacheln angegeben.':
        'No folder with DGM1 tiles specified.',
    'hoehendaten.de antwortet mit HTTP {status} fuer Kachel {slot_prefix}.':
        'hoehendaten.de responds with HTTP {status} for tile {slot_prefix}.',
    'keine':
        'none',
    'swisstopo antwortet mit HTTP {status} ({url}).':
        'swisstopo responds with HTTP {status} ({url}).',
    '{count} Bahnhöfe/Haltepunkte ({parts}), {platforms} Bahnsteige, {buildings} Gebäude, {stops} Haltepositionen; {loose} Objekte ohne Bahnhof in {radius_m:.0f} m.':
        '{count} stations/halts ({parts}), {platforms} platforms, {buildings} buildings, {stops} stop positions; {loose} objects without a station within {radius_m:.0f} m.',
    '3D-Vorschau anzeigen':
        'Show 3D preview',
    '3D-Vorschau fehlgeschlagen: {error}':
        '3D preview failed: {error}',
    '3D-Vorschau':
        '3D preview',
    "Zeigt rechts neben der 2D-Vorschau das Gelände als 3D-Block mit Erdwänden und Boden. Das Wasser füllt den Block wie ein Aquarium bis zur Wasserhöhe. Ist der Haken für die Höhenzonen gesetzt, färbt die Ansicht grün, Fels und Schnee nach denselben Grenzen wie die Zonen, ohne Haken ist das Gelände grau. Mit der linken Maustaste drehen, mit dem Mausrad zoomen, der Regler unten überhöht das Gelände (1× bis 5×). Die Ansicht gilt nur für die Vorschau, nicht für den Export, und lässt sich mit dem Haken '3D-Vorschau anzeigen' ausschalten.":
        "Shows the terrain as a 3D block with earth walls and a base next to the 2D preview. The water fills the block up to the water level, like an aquarium. If the height zones checkbox is ticked, the view colours green, rock and snow using the same limits as the zones; without it the terrain is grey. Drag with the left mouse button to rotate, use the mouse wheel to zoom, and the slider at the bottom exaggerates the relief (1x to 5x). The view is for the preview only, not for the export, and can be switched off with the 'Show 3D preview' checkbox.",
    'Speichern unter':
        'Save as',
    'JSON (*.json);;Alle Dateien (*)':
        'JSON (*.json);;All files (*)',
    'Karteninformationen':
        'Map information',
    'Kartengröße':
        'Map size',
    '{w:.1f} x {h:.1f} km ({wp} x {hp} Pixel)':
        '{w:.1f} x {h:.1f} km ({wp} x {hp} pixels)',
    'Reales Gebiet':
        'Real area',
    '{w:.1f} x {h:.1f} km (Stauchfaktor {f:g}, Höhenfaktor {hs:.3f})':
        '{w:.1f} x {h:.1f} km (compression factor {f:g}, height factor {hs:.3f})',
    'Höhenbereich im Import':
        'Elevation range in the import',
    '{low:.0f} bis {high:.0f} m, Wasserhöhe {water:.0f} m':
        '{low:.0f} to {high:.0f} m, water level {water:.0f} m',
    'Höhen über Wasser gestaucht auf':
        'Elevations above water compressed to',
    'Biome':
        'Biomes',
    'DGM1 Deutschland (1 m)':
        'DGM1 Germany (1 m)',
    'swissALTI3D Schweiz (2 m)':
        'swissALTI3D Switzerland (2 m)',
    '{percent:.1f} % der Fläche aus Copernicus ergänzt':
        '{percent:.1f} % of the area supplemented from Copernicus',
    'Quellenangabe':
        'Attribution',
    'Lizenz':
        'Licence',
    'DGM1 der Landesvermessung (Quellenvermerk des Landes beachten)':
        'DGM1 of the state survey (observe the state’s attribution notice)',
    'OGD swisstopo (Quellenangabe ist Pflicht)':
        'OGD swisstopo (attribution is mandatory)',
    'Karten- und Gewässerdaten':
        'Map and water data',
    '© OpenStreetMap-Mitwirkende (ODbL)':
        '© OpenStreetMap contributors (ODbL)',
    'Änderungen an den Höhendaten':
        'Changes to the elevation data',
    'zugeschnitten und auf 4 m je Pixel neu abgetastet':
        'cropped and resampled to 4 m per pixel',
    'TPF3-Wiki':
        'TPF3 wiki',
    'Erzeugt mit':
        'Created with',
    'Kartenformat im Spiel':
        'Map format in the game',
    'Winzig':
        'Tiny',
    'Klein':
        'Small',
    'Mittel':
        'Medium',
    'Gross':
        'Large',
    'Sehr gross':
        'Very large',
    'Riesig':
        'Huge',
    'Grössenwahnsinnig':
        'Megalomaniac',
    'Gigantomanisch':
        'Gigantomaniac',
    'Die Größenstufe {size} ist im Spiel nur mit experimentalMapFeatures = true in der settings.lua verfügbar. Für experimentelle Größen sind laut TPF3-Wiki mindestens 16 GB RAM nötig.':
        'The size class {size} is only available in the game with experimentalMapFeatures = true in settings.lua. According to the TPF3 wiki, experimental sizes need at least 16 GB of RAM.',
    'Gelände geglättet ({sigma:.0f} m)':
        'Terrain smoothed ({sigma:.0f} m)',
    'Trassen und Siedlungen eingeebnet ({sigma:.0f} m)':
        'Routes and settlements flattened ({sigma:.0f} m)',
    'Gefälle ausgeglichen (Stärke {strength:.0f} %, Glättung {smoothing:.0f} m), die absoluten Höhen ü. NN stimmen nicht mehr':
        'Gradient equalised (strength {strength:.0f} %, smoothing {smoothing:.0f} m), the absolute elevations above sea level are no longer correct',
    'Wasser nur dort, wo OpenStreetMap Wasser hat (Flussbett {edge:g} bis {depth:g} m tief, Böschung {transition:.0f} m)':
        'Water only where OpenStreetMap has water (riverbed {edge:g} to {depth:g} m deep, bank slope {transition:.0f} m)',
    'Terrain um Gewässer sanft ans Wasserniveau angepasst (Übergang {transition:.0f} m)':
        'Terrain around waters gently adjusted to the water level (transition {transition:.0f} m)',
    'Höhenfenster begrenzt ({mode})':
        'Elevation window limited ({mode})',
    'Beschreibung zum Teilen':
        'Description for sharing',
    'Beschreibung zum Teilen...':
        'Description for sharing...',
    'Erzeugt einen Text zum Veröffentlichen der Karte: Kartengröße, Höhenbereich, Höhenquelle mit Quellenangabe und Lizenz, Änderungen an den Höhendaten. Braucht geladene Höhendaten.':
        'Creates a text for publishing the map: map size, elevation range, elevation source with attribution and licence, changes to the elevation data. Needs loaded elevation data.',
    'Ausgabeformat:':
        'Output format:',
    'Klartext':
        'Plain text',
    'OpenStreetMap-Hinweis aufnehmen':
        'Include OpenStreetMap notice',
    'Der Text ersetzt nicht die Lizenzbedingungen der Quellen, bitte die Bedingungen der jeweiligen Quelle selbst prüfen. Beim Wechsel von Format oder Haken wird der Text neu erzeugt, eigene Änderungen gehen dabei verloren.':
        'The text does not replace the licence terms of the sources, please check the terms of each source yourself. When you change the format or the checkbox, the text is generated again and your own changes are lost.',
    'Kopiert.':
        'Copied.',
    'Erzeugt einen Text zum Veröffentlichen der Karte (Markdown, Steam-BBCode oder Klartext) mit Kartengröße und -format, Höhenbereich, Höhenquelle samt Quellenangabe und Lizenz, den Änderungen an den Höhendaten und bei den experimentellen Größenstufen einem Hinweis auf experimentalMapFeatures. Der Text lässt sich vor dem Kopieren bearbeiten. Er ersetzt nicht die Lizenzbedingungen der Quellen. Braucht geladene Höhendaten.':
        'Creates a text for publishing the map (Markdown, Steam BBCode or plain text) with map size and format, elevation range, elevation source with attribution and licence, the changes to the elevation data and, for the experimental size classes, a note about experimentalMapFeatures. The text can be edited before copying. It does not replace the licence terms of the sources. Needs loaded elevation data.',
    'Haftungsausschluss':
        'Disclaimer',
    'Daten verändert':
        'Data modified',
    'Lizenz (je nach Bundesland)':
        'Licence (depending on the state)',
    'Datenlizenz Deutschland – Namensnennung – Version 2.0 (dl-de/by-2-0)':
        'Data licence Germany – Attribution – Version 2.0 (dl-de/by-2-0)',
    'Creative Commons Namensnennung 4.0 International (CC BY 4.0)':
        'Creative Commons Attribution 4.0 International (CC BY 4.0)',
    'Datenstand der Höhendaten':
        'Date of the elevation data',
    'Bäume ab {limit:.0f} m über Wasser ausgedünnt':
        'Trees thinned out above {limit:.0f} m above water',
    '(auf Wasserhöhe 0 bezogen)':
        '(relative to water level 0)',
    'Sprache des Textes:':
        'Language of the text:',
    'Datenstand der OSM-Daten':
        'Date of the OSM data',
    'Das Gebiet im Kartenrezept fehlt (selection).':
        'The area is missing from the map recipe (selection).',
    'Das Gebiet im Kartenrezept ist ungültig (Minimum nicht kleiner als Maximum).':
        'The area in the map recipe is invalid (minimum is not smaller than maximum).',
    'Das Gebiet im Kartenrezept ist unvollständig (Breite, Höhe und Mittelpunkt gehören zusammen).':
        'The area in the map recipe is incomplete (width, height and center belong together).',
    'Das Kartenrezept konnte nicht angewendet werden: {error}':
        'The map recipe could not be applied: {error}',
    'Das ist kein Kartenrezept des TPF3-Map-Studios.':
        'This is not a TPF3 Map Studio map recipe.',
    'Die Datei ist kein lesbares Kartenrezept (kein gültiges JSON).':
        'The file is not a readable map recipe (not valid JSON).',
    'Die Datei ist zu groß für ein Kartenrezept.':
        'The file is too large for a map recipe.',
    'Die Datei konnte nicht gelesen werden: {error}':
        'The file could not be read: {error}',
    'Es sind noch keine Export-Einstellungen gespeichert (Heightmap-Dialog öffnen, Höhendaten laden und den Dialog schließen).\n\nTrotzdem nur das Gebiet exportieren?':
        'No export settings have been saved yet (open the heightmap dialog, load the elevation data and close the dialog).\n\nExport only the area anyway?',
    'Gebiet und Export-Einstellungen als kleine Datei zum Teilen speichern':
        'Save the area and export settings as a small file for sharing',
    'Gebiet und Export-Einstellungen aus einer Rezeptdatei laden (ersetzt das aktuelle Projekt)':
        'Load the area and export settings from a recipe file (replaces the current project)',
    "Im Kartenrezept fehlt der Wert '{key}'.":
        "The map recipe is missing the value '{key}'.",
    "Im Kartenrezept ist der Wert '{key}' ungültig.":
        "The value '{key}' in the map recipe is invalid.",
    'Kartenrezept (*.tpf3recipe)':
        'Map recipe (*.tpf3recipe)',
    'Kartenrezept exportieren':
        'Export map recipe',
    'Kartenrezept exportieren...':
        'Export map recipe...',
    'Kartenrezept gespeichert.':
        'Map recipe saved.',
    'Kartenrezept importieren':
        'Import map recipe',
    'Kartenrezept importieren...':
        'Import map recipe...',
    'Kartenrezept importiert.':
        'Map recipe imported.',
    'Kartenrezept konnte nicht gespeichert werden.\n\n{error}':
        'The map recipe could not be saved.\n\n{error}',
    'Nicht unterstützte Rezeptversion: {version}':
        'Unsupported recipe version: {version}',
    'Fehlerbericht erstellen...':
        'Create bug report...',
    'Log sowie Versions- und Systemangaben als ZIP für eine Fehlermeldung speichern (Namen und Pfade werden entfernt)':
        'Save the log plus version and system information as a ZIP for a bug report (names and paths are removed)',
    'Log-Ordner öffnen':
        'Open log folder',
    'Fehlerbericht speichern':
        'Save bug report',
    'ZIP-Datei (*.zip)':
        'ZIP file (*.zip)',
    'Fehlerbericht konnte nicht erstellt werden.\n\n{error}':
        'The bug report could not be created.\n\n{error}',
    'Fehlerbericht gespeichert':
        'Bug report saved',
    'Der Fehlerbericht wurde gespeichert:\n\n{path}\n\nBenutzername, Windows-Pfade, Steam-ID und E-Mail-Adressen wurden entfernt. Das Log kann Koordinaten des bearbeiteten Gebiets enthalten. Bitte die Datei an die Fehlermeldung (GitHub-Issue oder Forenbeitrag) anhängen.':
        'The bug report was saved:\n\n{path}\n\nUser name, Windows paths, Steam ID and e-mail addresses have been removed. The log may contain coordinates of the area you worked on. Please attach the file to your bug report (GitHub issue or forum post).',
    'Fehlerbericht gespeichert.':
        'Bug report saved.',
    'Log-Ordner konnte nicht geöffnet werden:\n{path}':
        'The log folder could not be opened:\n{path}',
    'Nach Updates suchen...':
        'Check for updates...',
    'Beim Start automatisch nach Updates suchen':
        'Check for updates automatically at startup',
    'Fragt beim Start einmal bei GitHub nach der neuesten Version (dabei sieht GitHub die IP-Adresse und die Versionsnummer des Studios). Standardmäßig aus.':
        'Asks GitHub once at startup for the latest version (GitHub sees the IP address and the version number of the Studio). Off by default.',
    'Suche nach Updates...':
        'Checking for updates...',
    'Keine neuere Version':
        'No newer version',
    'Es ist die neueste Version installiert ({version}).':
        'You have the latest version installed ({version}).',
    'Update-Prüfung fehlgeschlagen':
        'Update check failed',
    'Die Update-Prüfung ist fehlgeschlagen.\n\n{error}':
        'The update check failed.\n\n{error}',
    'Update verfügbar':
        'Update available',
    'Es gibt eine neuere Version des TPF3-Map-Studios.\n\nInstalliert: {current}\nNeueste: {latest}':
        'A newer version of TPF3 Map Studio is available.\n\nInstalled: {current}\nLatest: {latest}',
    'Download-Seite öffnen':
        'Open download page',
    'Diese Version überspringen':
        'Skip this version',
    'Später':
        'Later',
    'Download-Seite konnte nicht geöffnet werden:\n{url}':
        'The download page could not be opened:\n{url}',
    'Es wurde noch keine Version veröffentlicht.':
        'No version has been published yet.',
    'GitHub hat die Anfrage abgelehnt (Rate-Limit). Bitte später erneut versuchen.':
        'GitHub rejected the request (rate limit). Please try again later.',
    'GitHub hat mit Fehler {code} geantwortet.':
        'GitHub answered with error {code}.',
    'Unerwartete Antwort von GitHub.':
        'Unexpected response from GitHub.',
    'GitHub ist nicht erreichbar ({error}).':
        'GitHub could not be reached ({error}).',
    'Die Versionsnummer der neuesten Version ist nicht lesbar: {tag}':
        'The version number of the latest release is not readable: {tag}',
    'OpenStreetMap-Kacheln (Overpass)':
    'OpenStreetMap tiles (Overpass)',
    'Cache verwalten...':
        'Manage cache...',
    'Heruntergeladene Höhendaten ansehen und Speicherplatz freigeben':
        'View downloaded elevation data and free up disk space',
    'Cache verwalten':
        'Manage cache',
    'Heruntergeladene Daten (Höhenmodelle und OpenStreetMap-Kacheln) werden zwischengespeichert, damit sie nicht erneut geladen werden müssen. Leeren schafft Platz; die Daten werden bei Bedarf neu heruntergeladen (bei DGM1 und großen OSM-Gebieten kann das dauern). Projekte, Einstellungen und Logs bleiben unberührt.':
        'Downloaded data (elevation models and OpenStreetMap tiles) is cached so that it does not have to be downloaded again. Clearing frees disk space; the data is downloaded again when needed (this can take a while for DGM1 and large OSM areas). Projects, settings and logs are not affected.',
    '{files} Dateien, {size}':
        '{files} files, {size}',
    'leer':
        'empty',
    'Gesamt: {size}':
        'Total: {size}',
    'Leeren...':
        'Clear...',
    'Ordner öffnen':
        'Open folder',
    'Cache leeren':
        'Clear cache',
    'Den Cache "{name}" leeren?\n\n{size} ({files} Dateien) werden gelöscht. Die Daten werden bei Bedarf erneut heruntergeladen.':
        'Clear the cache "{name}"?\n\n{size} ({files} files) will be deleted. The data is downloaded again when needed.',
    'Cache geleert':
        'Cache cleared',
    '{count} Dateien gelöscht, {size} freigegeben.':
        '{count} files deleted, {size} freed.',
    '{count} Dateien konnten nicht gelöscht werden (vermutlich in Benutzung). Bitte das Studio neu starten und es erneut versuchen.':
        '{count} files could not be deleted (probably in use). Please restart the Studio and try again.',
    'Der Ordner konnte nicht geöffnet werden:\n{path}':
        'The folder could not be opened:\n{path}',
    'Unbekannter Cache: {name}':
        'Unknown cache: {name}',
    'Der Cache-Ordner ist eine Verknüpfung oder liegt außerhalb des Studio-Verzeichnisses und wird nicht geändert: {path}':
        'The cache folder is a link or lies outside the Studio folder and is left unchanged: {path}',
    'Copernicus-Kacheln laden':
        'Loading Copernicus tiles',
    'Die Kacheln (im Schnitt etwa 35 MB) kommen vom öffentlichen Copernicus-DEM-Bucket bei AWS. Bereits geladene Kacheln werden übersprungen. Du kannst jederzeit abbrechen und später weitermachen.':
        'The tiles (about 35 MB on average) come from the public Copernicus DEM bucket on AWS. Tiles that are already downloaded are skipped. You can cancel at any time and continue later.',
    'Kachel {index} von {count}: {tile}':
        'Tile {index} of {count}: {tile}',
    'Kachel {index} von {count}: {tile} ({done_mb:.0f} von {total_mb:.0f} MB)':
        'Tile {index} of {count}: {tile} ({done_mb:.0f} of {total_mb:.0f} MB)',
    'Kachel {index} von {count}: {tile} ({done_mb:.0f} MB)':
        'Tile {index} of {count}: {tile} ({done_mb:.0f} MB)',
    '{count} Kacheln geladen.':
        '{count} tiles downloaded.',
    'Download fehlgeschlagen: {error}':
        'Download failed: {error}',
    'Bahnhofsplan (Station Plan), Einebnung des Geländes unter Gleisen, Studio-Ansicht':
        'Station plan, terrain levelling under tracks, Studio view',
    'Nur die Auswahl, ob Straßenbahngleise mitgeladen werden':
        'Only controls whether tram tracks are loaded',
    'Einebnung des Geländes unter Straßen, Studio-Ansicht und eigene Ebenen':
        'Terrain levelling under roads, Studio view and own layers',
    'Einebnung unter Gebäuden, Bahnhofsgebäude im Bahnhofsplan, Studio-Ansicht':
        'Levelling under buildings, station buildings in the station plan, Studio view',
    'Biome-Maske (Gras/Park), Studio-Ansicht':
        'Biome mask (grass/park), Studio view',
    'Biome-Maske (Acker, Wiese, Wein ...), Bauernhöfe bei den Industrien, Studio-Ansicht':
        'Biome mask (fields, meadow, vineyard ...), farms among the industries, Studio view',
    'Biome-Maske (Wald), Forstwirtschaft bei den Industrien, Studio-Ansicht':
        'Biome mask (forest), forestry among the industries, Studio view',
    'Studio-Ansicht und eigene Ebenen, nicht direkt im TPF3-Editor':
        'Studio view and own layers, not directly in the TPF3 editor',
    'Ortsdatei (Städte und Dörfer) für den TPF3-Editor':
        'Towns file (cities and villages) for the TPF3 editor',
    'Biome-Maske (Siedlung, Heide, Moor, Fels), Steinbrüche bei den Industrien':
        'Biome mask (settlement, heath, bog, rock), quarries among the industries',
    'Industrien (Sägewerk, Ziegelei, ...) für den TPF3-Editor':
        'Industries (sawmill, brickworks, ...) for the TPF3 editor',
    'Studio-Ansicht und eigene Ebenen (Natur-Details), nicht direkt im TPF3-Editor':
        'Studio view and own layers (nature details), not directly in the TPF3 editor',
    'Nur Höhenkarte, Biome-Maske, Orte, Industrien und Bahnhofsplan gehen in den TPF3-Editor. Alle anderen Daten dienen der Ansicht im Studio, eigenen Ebenen und Ableitungen. Fahre mit der Maus über eine Kategorie, um zu sehen, wofür sie gebraucht wird.':
        'Only heightmap, biome mask, towns, industries and station plan go to the TPF3 editor. All other data is used for the Studio view, own layers and derivations. Hover over a category to see what it is used for.',
    'ASC-Dateien umwandeln':
        'Convert ASC files',
    'Im Ordner liegen {count} ASC-Dateien, aber keine GeoTIFF. Das Studio fasst sie zu einer GeoTIFF zusammen (4 m Pixelgröße, Ausschnitt an ganzen Kilometern). In welchem Koordinatensystem liegen die Daten? Das steht beim Anbieter oder in der .prj-Datei neben den ASC-Dateien.':
        'The folder contains {count} ASC files but no GeoTIFF. The Studio merges them into one GeoTIFF (4 m pixel size, section aligned to whole kilometres). Which coordinate system are the data in? The provider states it, or look in the .prj file next to the ASC files.',
    'ASC-Dateien werden umgewandelt ...':
        'Converting ASC files ...',
    '{name} ({done} von {total})':
        '{name} ({done} of {total})',
    'Fertig. Die zusammengefasste Datei liegt als {name} im Ordner. Deine ASC-Dateien wurden nicht verändert.':
        'Done. The merged file is in the folder as {name}. Your ASC files were not changed.',
    '{name}: kein gültiger ASC-Kopf (es fehlt {key}).':
        '{name}: not a valid ASC header ({key} is missing).',
    '{name}: {found} Werte gefunden, erwartet {expected}.':
        '{name}: {found} values found, {expected} expected.',
    'Die Pixelgröße muss in 1000 m aufgehen (1, 2, 4, 5, 10 ...).':
        'The pixel size must divide 1000 m evenly (1, 2, 4, 5, 10 ...).',
    'Im Ordner {folder} liegen keine ASC-Dateien.':
        'There are no ASC files in the folder {folder}.',
    '{name}: Zellgröße {cell} m passt nicht zur Pixelgröße {px} m.':
        '{name}: cell size {cell} m does not fit the pixel size {px} m.',
    'Ordner mit DGM1-Kacheln (GeoTIFF oder ASC) wählen':
        'Choose folder with DGM1 tiles (GeoTIFF or ASC)',
    'Spur {lane}: Kachel {tile}, nächster Versuch in {seconds} s': 'Worker {lane}: tile {tile}, next attempt in {seconds} s',
    'Spur {lane}: Kachel {tile} lädt': 'Worker {lane}: downloading tile {tile}',
    'Spur {lane}: bereit': 'Worker {lane}: ready',
    'OSM: {done} von {total} Kacheln fertig': 'OSM: {done} of {total} tiles ready',
    'Spur {lane} · Kachel {tile} · Versuch {attempt}': 'Worker {lane} · Tile {tile} · Attempt {attempt}',
    '{server}: wartet auf einen freien Anfrageplatz': '{server}: waiting for a free request slot',
    '{server}: Anfrage läuft': '{server}: request in progress',
    '{server}: Fehler — {error}': '{server}: Error — {error}',
    'Serverwechsel: {server} → {next_server}': 'Switching servers: {server} → {next_server}',
    'Alle Server versucht; neuer Durchgang in {seconds} s': 'All servers tried; next round in {seconds} s',
    '{server}: erfolgreich, Kachel gespeichert': '{server}: successful, tile saved',
    'Überlastungsbremse: höchstens eine Serveranfrage gleichzeitig': 'Overload protection: at most one server request at a time',
    'OSM-Download: Server und Verlauf': 'OSM download: servers and history',
    'OSM-Download wird vorbereitet…': 'Preparing OSM download…',
    'Geometrien werden aufgebaut…': 'Building geometries…',
    'Karte wird gezeichnet…': 'Drawing the map…',
    'Karte fertig.': 'Map ready.',
    'Spur {lane}: Download beendet.': 'Worker {lane}: download ended.',
    'Alle OSM-Kacheln geladen.': 'All OSM tiles downloaded.',
    'Download abgebrochen.': 'Download cancelled.',
    'Server überlastet (HTTP 429)': 'Server overloaded (HTTP 429)',
    'Interner Serverfehler (HTTP 500)': 'Internal server error (HTTP 500)',
    'Fehler am Server-Gateway (HTTP 502)': 'Server gateway error (HTTP 502)',
    'Server nicht verfügbar (HTTP 503)': 'Server unavailable (HTTP 503)',
    'Zeitüberschreitung am Server (HTTP 504)': 'Server timeout (HTTP 504)',
    'Zeitüberschreitung bei der Verbindung': 'Connection timed out',
    'Verbindung fehlgeschlagen': 'Connection failed',
    'Beim Start: {cached} vollständig im Cache · {partial} teilweise vorhanden · {new} neu zu laden': 'At start: {cached} fully cached · {partial} partly cached · {new} to download in full',
    'Noch zu ergänzen: {partial} · Noch vollständig zu laden: {new}': 'Still to complete: {partial} · Still to download in full: {new}',
    'Spur {lane}: nicht benötigt – keine weitere Kachel offen': 'Worker {lane}: not needed – no further tile pending',
    'Die Haken bestimmen, welche Merkmale zusätzlich geladen werden. Bereits gespeicherte Details bleiben erhalten, auch wenn ihr Haken aus ist.': 'The checkboxes determine which additional categories to download. Previously cached details are retained even when their checkbox is off.',
    'Berechne ...': 'Calculating ...',
    'Biome nach Höhe (Anteil der Landhöhe):': 'Biomes by height (share of land height):',
    'Biome-Maske speichern...': 'Save biome mask...',
    'Bitte einen anderen Dateinamen wählen – die TPF2-Datei wird nicht überschrieben.': 'Please choose a different file name – the TPF2 file will not be overwritten.',
    'Das Bild enthält Werte außerhalb von 16 Bit.': 'The image contains values outside 16 bit.',
    'Das Bild hat nur 8 Bit und wurde auf 16 Bit gestreckt; Höhenstufen können sichtbar sein.': 'The image only has 8 bit and was stretched to 16 bit; height steps may be visible.',
    'Das Bild ist kein Graustufenbild. Erwartet wird eine 16-Bit-Graustufen-PNG wie aus dem TPF2-Ordner heightmaps.': 'The image is not a greyscale image. A 16-bit greyscale PNG as found in the TPF2 heightmaps folder is expected.',
    'Das Bild ist zu klein oder hat mehrere Farbkanäle.': 'The image is too small or has several colour channels.',
    'Das Bild liegt quer zu dieser Kartengröße.': 'The image is rotated relative to this map size.',
    'Die Berechnung ist fehlgeschlagen:\n{error}': 'The calculation failed:\n{error}',
    'Die Datei konnte nicht als Bild gelesen werden.': 'The file could not be read as an image.',
    'Die Datei wurde nicht gefunden.': 'The file was not found.',
    'Die Heightmap konnte nicht geladen werden.': 'The heightmap could not be loaded.',
    'Die Maximalhöhe muss größer als die Mindesthöhe sein.': 'The maximum height must be greater than the minimum height.',
    'Die PNG enthält keine Meter. Stelle die Wasserhöhe so ein, dass in der Vorschau Seen und Flüsse gefüllt sind, aber kein Land absäuft. Gleiche Höhe wie Mindesthöhe = kein Wasser.': 'The PNG contains no metres. Set the water level so that lakes and rivers are filled in the preview but no land is flooded. Same value as the minimum height = no water.',
    'Die Wasserhöhe muss zwischen Mindest- und Maximalhöhe liegen.': 'The water level must lie between the minimum and maximum height.',
    'Die untere Biom-Grenze muss kleiner als die obere sein.': 'The lower biome limit must be smaller than the upper one.',
    'Entfernt kleine Pfützen, hebt flaches Land knapp über dem Wasser an und vertieft flaches Wasser, damit klare Ufer entstehen. Gelände weiter weg vom Wasser bleibt unverändert.': 'Removes small puddles, raises flat land just above the water and deepens shallow water so that clear shores are formed. Terrain further away from the water stays unchanged.',
    'Gespeichert:\n{path}\n\nIm Spiel: Karteneditor → Heightmap importieren → diese Datei wählen und eintragen:\nMindesthöhe {low:g}, Maximalhöhe {high:g}, Wasserhöhe {water:g}': 'Saved:\n{path}\n\nIn the game: map editor → Import heightmap → choose this file and enter:\nminimum height {low:g}, maximum height {high:g}, water level {water:g}',
    'Grenze Mitte/oben:': 'Limit middle/top:',
    'Grenze unten/Mitte:': 'Limit bottom/middle:',
    'Heightmap speichern': 'Save heightmap',
    'Heightmap speichern...': 'Save heightmap...',
    'Heightmap wählen...': 'Choose heightmap...',
    'Höhen müssen zwischen -100 und 3177 m liegen (Grenzen des TPF3-Imports).': 'Heights must lie between -100 and 3177 m (limits of the TPF3 import).',
    'Kartengröße: {labels}.': 'Map size: {labels}.',
    'Keine bekannte TPF3-Kartengröße – der Karteneditor nimmt die Datei eventuell nicht an.': 'Not a known TPF3 map size – the map editor may not accept the file.',
    'Land mindestens über Wasser:': 'Land at least above water:',
    'Maximalhöhe:': 'Maximum height:',
    'Mindesthöhe:': 'Minimum height:',
    'Mitte:': 'Middle:',
    'Noch keine Heightmap gewählt.': 'No heightmap chosen yet.',
    'Oben:': 'Top:',
    'Pfützen entfernen bis:': 'Remove puddles up to:',
    'TPF2-Heightmap wählen': 'Choose TPF2 heightmap',
    'TPF2-Karte übernehmen': 'Take over TPF2 map',
    'TPF2-Karte übernehmen...': 'Take over TPF2 map...',
    'Ufer bereinigen': 'Clean up shores',
    'Ufer bereinigt: {puddles} Pfützen entfernt, {raised} Pixel angehoben, {lowered} Pixel vertieft.': 'Shores cleaned up: {puddles} puddles removed, {raised} pixels raised, {lowered} pixels deepened.',
    'Unten:': 'Bottom:',
    'Unter Wasser:': 'Under water:',
    'Vorschau:': 'Preview:',
    'Höhe + Biome': 'Height + biomes',
    'Deckkraft der Biome:': 'Biome opacity:',
    'Wie stark die Biom-Farben das Relief überdecken (nur bei Vorschau "Höhe + Biome").': 'How strongly the biome colors cover the relief (only for the "Height + biomes" preview).',
    'Wasser (blau)': 'Water (blue)',
    'Wasser mindestens tief:': 'Water at least deep:',
    'Wasser: {share:.2f} % der Karte.': 'Water: {share:.2f} % of the map.',
    '{w} x {h} Pixel = {wkm:.2f} x {hkm:.2f} km.': '{w} x {h} pixels = {wkm:.2f} x {hkm:.2f} km.',
    'Übernimmt die Heightmap einer TPF2-Karte nach TPF3: Höhen und Wasserhöhe festlegen, Ufer bereinigen und eine Biome-Maske aus der Höhe erzeugen. Gedacht für fiktive Karten, bei denen alles Wasser auf einer Höhe liegt. Fels und Schnee färbt das Spiel selbst.': 'Takes over the heightmap of a TPF2 map into TPF3: set heights and water level, clean up shores and create a biome mask from the height. Intended for fictional maps where all water lies at one level. The game colours rock and snow itself.',
    'Kein Wasser eingestellt (Wasserhöhe = Mindesthöhe).': 'No water set (water level = minimum height).',
    'Es ist kein Wasser eingestellt: Die Wasserhöhe steht auf der Mindesthöhe. Dann werden keine Ufer bereinigt. Wird im Spiel trotzdem eine höhere Wasserhöhe eingetragen, entstehen Pfützen und Löcher.\n\nTrotzdem speichern?': 'No water is set: the water level equals the minimum height. Shores are then not cleaned up. If a higher water level is entered in the game anyway, puddles and holes will appear.\n\nSave anyway?',
    "BEV-Kachel ist beschädigt (falsche Größe nach dem Entpacken).": "BEV tile is damaged (wrong size after unpacking).",
    "Netzwerkfehler: {exc}": "Network error: {exc}",
    "Dienstfehler HTTP {status}": "Service error HTTP {status}",
    "BEV antwortet mit HTTP {status} (erwartet 206, Teilabruf) für {url}.": "BEV answered with HTTP {status} (expected 206, partial download) for {url}.",
    "unvollständige Antwort": "incomplete response",
    "unbekannter Fehler": "unknown error",
    "BEV nicht erreichbar ({error}).": "BEV not reachable ({error}).",
    "Die BEV-Datei ist kein BigTIFF, das Studio kann sie nicht lesen.": "The BEV file is not a BigTIFF; the Studio cannot read it.",
    "Die BEV-Datei hat keine Ebene {level}.": "The BEV file has no level {level}.",
    "Die BEV-Datei nutzt eine unbekannte Kompression.": "The BEV file uses an unknown compression.",
    "Keine BEV-Kacheln fuer diesen Ausschnitt gefunden. Liegt der Ausschnitt ausserhalb Oesterreichs, bitte Copernicus waehlen.": "No BEV tiles found for this area. If the area is outside Austria, please choose Copernicus.",
    "BEV Österreich (1 m, über data.bev.gv.at)": "BEV Austria (1 m, via data.bev.gv.at)",
    "BEV Österreich: Höhenmodell des Bundesamts für Eich- und Vermessungswesen (1 m, ohne Gebäude und Bewuchs). Geladen werden nur die Ausschnitte, die dein Rechteck braucht, nicht die ganzen Dateien von rund 8 GB. Nur bei Karten in Österreich wählbar. Quellenangabe: BEV, CC BY 4.0.": "BEV Austria: terrain model of the Federal Office of Metrology and Surveying (1 m, without buildings and vegetation). Only the parts your rectangle needs are downloaded, not the whole files of about 8 GB. Selectable only for maps in Austria. Source: BEV, CC BY 4.0.",
    "BEV-Kacheln laden": "Load BEV tiles",
    "Die Kacheln kommen vom BEV (data.bev.gv.at). Geladen werden nur die Ausschnitte, die dein Rechteck braucht (rund 0,6 MB je Kachel). Bereits geladene Kacheln werden übersprungen. Du kannst jederzeit abbrechen und später weitermachen.": "The tiles come from the BEV (data.bev.gv.at). Only the parts your rectangle needs are downloaded (about 0.6 MB per tile). Tiles already downloaded are skipped. You can cancel at any time and continue later.",
    "Die Kacheln kommen von data.public.lu (Administration du cadastre et de la topographie, Lidar 2024). Geladen werden nur die Ausschnitte, die dein Rechteck braucht (etwa 0,3 MB je Quadratkilometer). Bereits geladene Kacheln werden übersprungen. Du kannst jederzeit abbrechen und später weitermachen.": "The tiles come from data.public.lu (Administration du cadastre et de la topographie, Lidar 2024). Only the parts your rectangle needs are downloaded (about 0.3 MB per square kilometre). Tiles already downloaded are skipped. You can cancel at any time and continue later.",
    "Die Luxemburg-Datei hat keine Ebene {level}.": "The Luxembourg file has no level {level}.",
    "Die Luxemburg-Datei ist kein BigTIFF, das Studio kann sie nicht lesen.": "The Luxembourg file is not a BigTIFF; the Studio cannot read it.",
    "Die Luxemburg-Datei nutzt eine unbekannte Kompression.": "The Luxembourg file uses an unknown compression.",
    "Die Luxemburg-Datei nutzt einen unbekannten Predictor.": "The Luxembourg file uses an unknown predictor.",
    "Eine Luxemburg-Kachel ist beschädigt (falsche Größe nach dem Entpacken).": "A Luxembourg tile is damaged (wrong size after unpacking).",
    "Keine Luxemburg-Kacheln fuer diesen Ausschnitt gefunden. Liegt der Ausschnitt ausserhalb Luxemburgs, bitte Copernicus waehlen.": "No Luxembourg tiles found for this area. If the area is outside Luxembourg, please choose Copernicus.",
    "Luxemburg (data.public.lu) antwortet mit HTTP {status} (erwartet 206, Teilabruf).": "Luxembourg (data.public.lu) answered with HTTP {status} (expected 206, partial download).",
    "Luxemburg (data.public.lu) nicht erreichbar ({error}).": "Luxembourg (data.public.lu) not reachable ({error}).",
    "Luxemburg MNT 2024 (0,5 m, über data.public.lu)": "Luxembourg MNT 2024 (0.5 m, via data.public.lu)",
    "Luxemburg MNT 2024 (4 m aus 0,5 m)": "Luxembourg MNT 2024 (4 m from 0.5 m)",
    "Luxemburg MNT 2024: Geländemodell der Administration du cadastre et de la topographie aus der Befliegung 2024 (0,5 m, ohne Gebäude und Bewuchs). Die Datei hat rund 40 GB, geladen werden nur die Ausschnitte, die dein Rechteck braucht (bei 4 m pro Pixel etwa 0,3 MB je Quadratkilometer). Nur bei Karten in Luxemburg wählbar. CC0 1.0.": "Luxembourg MNT 2024: terrain model of the Administration du cadastre et de la topographie from the 2024 survey (0.5 m, without buildings and vegetation). The file is about 40 GB; only the parts your rectangle needs are downloaded (at 4 m per pixel about 0.3 MB per square kilometre). Selectable only for maps in Luxembourg. CC0 1.0.",
    "Luxemburg-Kacheln laden": "Load Luxembourg tiles",
}


CATALOG.update({'Anleitungen': 'Guides', 'Anleitungen...': 'Guides...', 'Suchen...': 'Search...'})


CATALOG.update({
    "1 Pixel der Höhenkarte = 4 m im Spiel = {real:.0f} m echtes Gelände. Flüsse und Kanäle werden immer {river:.0f} m breit gezeichnet (nicht mitgestaucht); Bäche und Gräben werden nicht als Wasser gezeichnet. {ex_real:.0f} m echte Höhe werden zu {ex_game:.0f} m.":
        "1 pixel of the height map = 4 m in the game = {real:.0f} m of real terrain. Rivers and canals are always drawn {river:.0f} m wide (not compressed with the map); streams and ditches are not drawn as water. {ex_real:.0f} m of real height become {ex_game:.0f} m.",
    "Wasser-Check: {share:.0f} % der Gewässerfläche liegt höher als {rise:.0f} m über dem Wasserspiegel und bleibt unverändert (dort entsteht kein Wasser). Die übrigen Gewässer werden im Mittel um {mean:.0f} m abgesenkt, höchstens um etwa {p95:.0f} m.":
        "Water check: {share:.0f} % of the water area lies more than {rise:.0f} m above the water level and stays unchanged (no water will appear there). The remaining waters are lowered by {mean:.0f} m on average, by about {p95:.0f} m at most.",
    "Über die Hälfte liegt zu hoch: Die Grenze „Nur Gewässer bis“ erhöhen oder den Wasserspiegel prüfen.":
        "More than half lies too high: raise the \"Only waters up to\" limit or check the water level.",
})

CATALOG.update({
    "Flussbreite:": "River width:",
    " Pixel": " pixels",
    "= {m:.0f} m im Spiel": "= {m:.0f} m in game",
    "Breite, mit der Flüsse und Kanäle aus OpenStreetMap gezeichnet werden (1 Pixel = 4 m im Spiel). Sie wird nicht mit dem Stauchfaktor kleiner. Breiter = besser befahrbar für Schiffe, aber auch breiteres Wasser.":
        "Width used to draw rivers and canals from OpenStreetMap (1 pixel = 4 m in game). It does not shrink with the compression factor. Wider = easier for ships, but also wider water.",
})

CATALOG.update({
    "Steigung in der Vorschau zeigen (gelb ab 4 %, orange ab 10 %, rot ab 24 %)":
        "Show slope in the preview (yellow from 4 %, orange from 10 %, red from 24 %)",
    "Zeigt, wie steil das Gelände im Spiel ist. Rot (ab etwa 24 %) wird im Spiel ungefähr zum Gebirge. Nur Vorschau, kein Export.":
        "Shows how steep the terrain is in the game. Red (from about 24 %) roughly becomes mountains in the game. Preview only, not exported.",
    "Steigung: unter 4 % {flat:.1f} %, 4–10 % {mild:.1f} %, 10–24 % {medium:.1f} %, über 24 % {steep:.1f} % (Maximum {max:.0f} %)":
        "Slope: under 4 % {flat:.1f} %, 4–10 % {mild:.1f} %, 10–24 % {medium:.1f} %, over 24 % {steep:.1f} % (maximum {max:.0f} %)",
})

CATALOG.update({
    "Steigung in der Vorschau":
        "Slope in the preview",
    "Färbt die Vorschau nach der Steilheit des Geländes im Spiel: gelb ab 4 %, orange ab 10 %, rot ab 24 %. Rot wird im Spiel ungefähr zum Gebirge. Darunter stehen die Flächenanteile. Nur Vorschau, nicht für den Export.":
        "Colours the preview by how steep the terrain is in the game: yellow from 4 %, orange from 10 %, red from 24 %. Red roughly becomes mountains in the game. The area shares are shown below. Preview only, not for export.",
})

CATALOG.update({
    "Natur-Details-Plan...": "Nature details plan...",
    "Natur-Details-Plan": "Nature details plan",
    "Natur-Details-Plan speichern": "Save nature details plan",
    "Liest Weinberge, Obstwiesen, Mauern und Hecken aus den geladenen OSM-Daten und speichert sie als .csv und .json mit Lage in Metern ab Kartenmitte, als Vorlage zum Nachbauen mit dem Zaunbaukasten. Mauern und Hecken werden nur geladen, wenn beim OSM-Laden 'Natur-Details' angehakt ist. Im Spiel wird nichts gebaut.":
        "Reads vineyards, orchards, walls and hedges from the loaded OSM data and saves them as .csv and .json with positions in metres from the map centre, as a template for rebuilding with the fence builder. Walls and hedges are only loaded if 'Natur-Details' is ticked when loading OSM. Nothing is built in the game.",
    "Keine Weinberge, Obstwiesen, Mauern oder Hecken gefunden. Mauern und Hecken gibt es nur, wenn beim OSM-Laden 'Natur-Details' angehakt war.":
        "No vineyards, orchards, walls or hedges found. Walls and hedges only exist if 'Natur-Details' was ticked when loading OSM.",
    "Gespeichert: {csv} und {json}\n\nWeinberge: {v} ({vha:.1f} ha), Obstwiesen: {o} ({oha:.1f} ha)\nMauern: {w} ({wl:.0f} m), Hecken: {h} ({hl:.0f} m)":
        "Saved: {csv} and {json}\n\nVineyards: {v} ({vha:.1f} ha), orchards: {o} ({oha:.1f} ha)\nWalls: {w} ({wl:.0f} m), hedges: {h} ({hl:.0f} m)",
    "Liest Weinberge, Obstwiesen, Mauern und Hecken aus den geladenen OSM-Daten und speichert sie als .csv und .json mit Lage in Metern ab Kartenmitte (Flächen mit Reihenrichtung und geschätzter Reihenzahl, Mauern und Hecken mit Länge). Mauern und Hecken gibt es nur, wenn beim OSM-Laden 'Natur-Details' angehakt war. Im Spiel wird nichts gebaut, die Dateien sind eine Vorlage zum Nachbauen mit dem Zaunbaukasten.":
        "Reads vineyards, orchards, walls and hedges from the loaded OSM data and saves them as .csv and .json with positions in metres from the map centre (areas with row direction and estimated row count, walls and hedges with length). Walls and hedges only exist if 'Natur-Details' was ticked when loading OSM. Nothing is built in the game; the files are a template for rebuilding with the fence builder.",
})

CATALOG.update({
    "Mindestfläche für Weinberge und Obstwiesen (m²). Kleinere Flächen (Reste, Zeichenfehler) werden weggelassen:":
        "Minimum area for vineyards and orchards (m²). Smaller areas (leftovers, drawing errors) are left out:",
})

CATALOG.update({
    "Berg-, See- und Sumpf-Masken...": "Mountain, lake and swamp masks...",
    "Berg-, See- und Sumpf-Masken": "Mountain, lake and swamp masks",
    "Zuerst Höhendaten laden.": "Load elevation data first.",
    "Masken speichern (Name ohne Endung wird ergänzt)": "Save masks (name without extension, suffixes are added)",
    "Schlägt aus der Höhenkarte Masken für Berge, Seen und Sümpfe vor und speichert sie als drei PNG-Dateien für den Biome-Tab. Das ist eine Annäherung zum Nachmalen, besonders Seen und Sümpfe treffen die Masken des Spiels nur grob.":
        "Suggests masks for mountains, lakes and swamps from the height map and saves them as three PNG files for the biome tab. This is an approximation to paint over; lakes and swamps in particular only roughly match the game's masks.",
    "Gespeichert: {a}, {b}, {c}\n\nAnteil an der Karte: Berge {m:.1f} %, Seen {l:.1f} %, Sümpfe {s:.1f} %\n\nDas sind Vorschläge zum Nachmalen. Seen und Sümpfe treffen die Masken des Spiels nur grob.":
        "Saved: {a}, {b}, {c}\n\nShare of the map: mountains {m:.1f} %, lakes {l:.1f} %, swamps {s:.1f} %\n\nThese are suggestions to paint over. Lakes and swamps only roughly match the game's masks.",
    "Schlägt aus der Höhenkarte Masken für Berge, Seen und Sümpfe vor und speichert sie als drei PNG-Dateien (0/255) für den Biome-Tab. Berge: die höchsten etwa 35 % der geglätteten Höhe. Seen: flaches Wasser kurz unter dem Wasserspiegel. Sümpfe: flaches Land direkt am Wasserspiegel. Die Regeln sind an Testkarten abgestimmt und eine Annäherung zum Nachmalen, besonders Seen und Sümpfe treffen die Masken des Spiels nur grob.":
        "Suggests masks for mountains, lakes and swamps from the height map and saves them as three PNG files (0/255) for the biome tab. Mountains: the highest ~35 % of the smoothed height. Lakes: shallow water just below the water level. Swamps: flat land right at the water level. The rules are tuned on test maps and are an approximation to paint over; lakes and swamps in particular only roughly match the game's masks.",
})

CATALOG.update({
    'Schnell- und Bundesstra\xdfen breit bauen (4 Spuren, im Spiel ungetestet)':
        'Build trunk and primary roads wide (4 lanes, untested in game)',
    'Der Mod baut diese Stra\xdfen zuerst schmal und weitet sie danach mit dem Konsolenbefehl \u201eaufweiten\u201c auf (sonst st\xfcrzt das Spiel an Kreuzungen ab).':
        'The mod first builds these roads narrow and then widens them with the console command \u201caufweiten\u201d (otherwise the game crashes at junctions).',
    '\n\nDanach (breite Stra\xdfen), wenn \u201eImport fertig\u201c steht:\n{cmd}':
        '\n\nAfterwards (wide roads), once \u201cImport fertig\u201d appears:\n{cmd}',
})
