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
    'Bahnhöfe aus OSM...':
        'Stations from OSM...',
    'Liest Bahnhöfe, Haltepunkte, Bahnsteige, Bahnhofsgebäude und Haltepositionen aus den geladenen OSM-Daten und speichert sie als .json (alles) und .csv (eine Zeile je Bahnhof). Braucht geladene OSM-Daten.':
        'Reads stations, halts, platforms, station buildings and stop positions from the loaded OSM data and saves them as .json (everything) and .csv (one row per station). Needs loaded OSM data.',
    'Straßen und Gleise...':
        'Roads and tracks...',
    'Erzeugt aus den geladenen OSM-Wegen einen Mod, der im Spiel Straßen, Gleise, Brücken und Tunnel baut. Braucht geladene OSM-Daten.':
        'Creates a mod from the loaded OSM ways that builds roads, tracks, bridges and tunnels in the game. Needs loaded OSM data.',
    'Schließen':
        'Close',
    'Ordner mit DGM1-GeoTIFF-Kacheln wählen':
        'Choose folder with DGM1 GeoTIFF tiles',
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
    'Bahnhöfe aus OSM':
        'Stations from OSM',
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
}
