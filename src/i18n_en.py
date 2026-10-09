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
}
