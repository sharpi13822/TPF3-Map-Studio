"""
Anleitung fuer den Heightmap-Dialog: von der leeren Karte bis zur importierten
Heightmap in TPF3. Wird im Dialog ueber den Knopf "Anleitung" oder F1 geoeffnet.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)

GUIDE_HTML = """
<h2>Heightmap vom Studio nach Transport Fever 3</h2>
<p>Schritt für Schritt von der leeren Karte bis zur importierten Heightmap.
Was noch nicht im Spiel getestet ist, steht jeweils dabei.</p>

<h3>Teil A: Im Studio</h3>

<h4>Ausschnitt festlegen</h4>
<ol>
<li>Im Panel auf der Karte unter <b>Kartenquelle</b> am besten <b>Karte + Relief</b>
wählen, damit man Täler und Hänge sieht. Zum gewünschten Gebiet zoomen. Optional mit dem
<b>Marker</b>-Werkzeug einen Marker in die Mitte setzen (er liefert den Mittelpunkt).</li>
<li><b>Werkzeuge → Rechteck-Tool</b>: Mittelpunkt prüfen, <b>Kartengröße</b> und
<b>Format</b> genau wie im Spiel wählen, <b>Drehwinkel</b> einstellen, bis das Band zu deinem
Fluss oder deiner Strecke passt. OK. Das blaue Band lässt sich mit dem blauen Punkt
verschieben und mit dem orangen drehen.</li>
</ol>

<h4>OSM-Daten laden</h4>
<ol start="3">
<li><b>Werkzeuge → OSM laden</b> und warten. Große Gebiete brauchen einige Minuten.
Ohne OSM-Daten funktionieren die Optionen „Wasser nur dort, wo OpenStreetMap Wasser hat“
und „Trassen und Siedlungen einebnen“ nicht.</li>
</ol>

<h4>Höhendaten holen (in diesem Dialog)</h4>
<ol start="4">
<li>Optional <b>Schnellvorschau</b> (grob, sofort da, nicht exportierbar).</li>
<li>Oben unter <b>Höhenquelle</b> wählen: <b>Copernicus</b> (weltweit, 30 m, schnell) oder für
Karten in Deutschland <b>DGM1 Deutschland</b> (1-m-Geländemodell der Bundesländer, genauer an
Hängen und Böschungen). Dann <b>Höhendaten herunterladen</b> und warten, bis oben „Geladen: …
Pixel“ steht. Beim ersten Mal lädt das Studio die Kacheln, danach geht es schneller.
<br>Bei DGM1 kommen die Kacheln über den Webdienst hoehendaten.de, höchstens etwa 20 Kacheln
pro Minute: eine große Karte braucht etwa eine halbe Stunde. Das Fenster zeigt den Fortschritt
und lässt sich abbrechen, bereits geladene Kacheln werden beim nächsten Mal übersprungen. Wer
die Kacheln selbst bei einem Landesportal heruntergeladen hat, wählt <b>DGM1 aus eigenen
GeoTIFF-Kacheln</b> und den Ordner (die Kacheln müssen auf dem 1-km-Raster liegen). Wo DGM1-Daten
fehlen, ergänzt das Studio aus Copernicus. Die Schnellvorschau nutzt immer Copernicus.
<i>DGM1 ist am Rhein (Bingen bis Koblenz, Größenwahnsinnig 1:5) im Spiel getestet.</i>
<br>Für Karten in der <b>Schweiz</b> oder in Liechtenstein gibt es <b>swissALTI3D Schweiz</b>
(Geländemodell von swisstopo mit 2 m Auflösung). Die Auswahl erscheint nur, wenn der Kartenmittelpunkt
dort liegt. Die Kacheln kommen von data.geo.admin.ch, ein Fenster zeigt den Fortschritt und lässt
sich abbrechen, geladene Kacheln liegen im Zwischenspeicher. Wo Daten fehlen, ergänzt das Studio aus
Copernicus. Die Voreinstellung „Empfohlen“ behandelt swissALTI3D wie DGM1.
<i>swissALTI3D ist im Spiel noch nicht getestet.</i></li>
</ol>

<h4>Einstellungen</h4>
<p><b>Schnellstart:</b> Oben im Dialog unter <b>Voreinstellung</b> <i>„Empfohlen“</i> wählen
(Glätten, Einebnen, Wasser nach OSM mit den Standardwerten) oder <i>„Original“</i> (alle
Optionen aus, echte Höhen). Die Voreinstellung springt auf <i>„Eigene Einstellungen“</i>, sobald
du etwas von Hand änderst. Optionen, die OSM-Daten brauchen, bleiben ohne geladene OSM-Daten
aus. Die folgenden Schritte erklären die einzelnen Optionen.</p>
<p>Empfohlene Reihenfolge. Jede Änderung aktualisiert die Vorschau und die Zahlen
unten im Dialog.</p>
<ol start="6">
<li><b>Wasserhöhe</b> prüfen. Tipp: etwas höher als der tiefste Teil des Flusses, aber nicht
so hoch, dass der Fluss an der höchsten Stelle mehr als 10 bis 15 m über dem Pegel liegt.
Bei Flüssen mit Gefälle (zum Beispiel Rhein) ist das ein Kompromiss. Der Knopf
<b>„Wasserhöhe aus den OSM-Gewässern vorschlagen“</b> setzt sie in die Mitte zwischen
tiefstem und höchstem Punkt des Hauptflusses und passt die Grenze „Nur Gewässer bis“
an (braucht OSM-Daten).</li>
<li><b>Gelände glätten</b> anhaken, Standard 15 m. Entfernt die Treppenstufen an den Hängen
(das Höhenmodell hat nur 30 m pro Pixel, das Spiel 4 m). Bei DGM1 ist Glätten meist nicht
nötig, das Modell ist schon genau, die Voreinstellung „Empfohlen“ lässt es dort aus.</li>
<li><b>Trassen und Siedlungen einebnen</b> anhaken, Standard 60 m (bei „Empfohlen“ mit DGM1: 10 m). Bahnstrecken, größere
Straßen und Gebäude werden abgeflacht, damit im Spiel weniger Rampen nötig sind. Braucht
OSM-Daten. <i>Ob es beim Bauen spürbar hilft, ist noch nicht im Spiel geprüft.</i></li>
<li><b>Wasser nur dort, wo OpenStreetMap Wasser hat</b> anhaken (empfohlen). Verhindert
überflutete Auen und Tümpel. Standardwerte: Böschung 60 m (bei „Empfohlen“ mit DGM1: 10 m; breiter = flacheres Ufer), Tiefe
am Ufer 2 m, Tiefe in der Mitte 8 m (Fahrrinne), Ufer über Wasser 2 m, nur Gewässer bis
15 m über Wasserspiegel (höher gelegene Bäche und Bergseen bleiben unverändert). Die Option
„Terrain sanft ans Wasserniveau anpassen“ schaltet sich dabei ab, beide zusammen gehen
nicht.</li>
<li><b>Höhen stauchen</b> gegen weiße und graue Flächen auf den Höhen. Das Spiel färbt nach der
Höhe über dem Wasser (Fels ab etwa 325-350 m, Schnee ab etwa 375-425 m). Die höchste Stelle landet auf
diesem Anteil, der untere Teil des Geländes bleibt unverändert. Beim Rhein hat 45 % funktioniert.
Standard 100 % = unverändert.</li>
<li><b>Gefälle ausgleichen</b> für lange Flüsse mit starkem Gefälle (zum Beispiel der Rhein von
Koblenz bis Bingen, rund 18 m). Es legt Flüsse und Seen auf eine gemeinsame Ebene und verschiebt
dabei alle Höhen: Die Zahlen für das Spiel ändern sich stark, die absoluten Höhen über NN stimmen
danach nicht mehr. Standard: Stärke 100 %, Glättung 400 m, Bezug: Gewässer bis 30 m über dem
Wasserspiegel. Im Test am Rhein (Bingen bis Koblenz, DGM1, Größenwahnsinnig 1:5, Wasserhöhe 70 m)
waren im Spiel beide Enden des Flusses gefüllt.</li>
</ol>

<h4>Kontrolle und Export</h4>
<ol start="12">
<li>In der Vorschau prüfen: Der Fluss sollte ein durchgehendes Band im Tal sein, keine
geraden Streifen oder Keile, keine Tümpel außer denen aus OSM.</li>
<li><b>Unten im Dialog den Text lesen</b> und abschreiben oder fotografieren:
<i>„Im TPF3-Import eintragen: Mindesthöhe …, Maximalhöhe …, Wasserhöhe …“</i> und
<i>„Kartengröße und -format im Spiel: …“</i>. Das sind die <b>echten Höhen</b> (positive
Werte über NN). Diese Zahlen gelten immer für genau die aktuellen Einstellungen. Mit dem Haken
<b>„Werte auf Wasserhöhe 0 beziehen“</b> schaltest du auf die Variante um, die das TPF3-Wiki
für Biome und Materialien empfiehlt (Mindesthöhe kann dabei negativ werden). Mit echten
Höhen liegt alles entsprechend höher im Spiel, weiße Flächen auf den Höhen können dadurch
zunehmen.</li>
<li><b>Exportieren…</b> Der Dialog schlägt den heightmaps-Ordner von TPF3 vor. Gib der Datei
einen <b>eindeutigen Namen</b>, zum Beispiel <tt>rhein_osmwasser.png</tt>.</li>
</ol>

<h3>Teil B: In TPF3</h3>
<ol start="15">
<li>Den Karteneditor öffnen. Bei den Einstellungen unter <b>Welt</b> dieselbe
<b>Kartengröße</b> und dasselbe <b>Kartenformat</b> wählen wie im Studio-Text. Nur dann
passt das Seitenverhältnis, das Spiel streckt jedes Bild auf die Kartengröße. Fehlt eine
Größe (zum Beispiel Gigantomanisch), steht laut Wiki in der <tt>settings.lua</tt> der Schalter
<tt>experimentalMapFeatures</tt>.</li>
<li>Den Dialog <b>Heightmap importieren</b> öffnen (Reiter <b>Heightmap</b>).</li>
<li>In der Liste die exportierte Datei anklicken. Steht sie nicht drin: Dialog schließen und
neu öffnen und prüfen, ob die Datei im Ordner <tt>heightmaps</tt> liegt.</li>
<li>Werte eintragen: <b>Mindesthöhe</b>, <b>Maximalhöhe</b> und <b>Wasserhöhe</b> genau wie im
Studio-Text, <b>Assets behalten: Nein</b>.</li>
<li>Die Vorschau rechts ansehen: Stimmt die Form? Steht nur der Fluss unter Wasser (blau)?</li>
<li><b>Import</b> klicken.</li>
</ol>

<h4>Optional: Bäume (Reiter Biome)</h4>
<ol start="21">
<li>Die Biome-Maske bestimmt die Baumverteilung. Das Studio kann sie aus der OSM-Landnutzung
erzeugen: im Heightmap-Dialog <b>Biome-Maske aus OSM…</b> (braucht geladene OSM-Daten). Die Datei
muss im Ordner <tt>biomes</tt> liegen, damit der Biome-Reiter sie findet. Eine einheitliche Maske
reicht zum Test
(Graustufe 77 = Biom 1, 128 = Biom 2, 179 = Biom 3, jeweils eine Datei im Ordner
<tt>biomes</tt>). Bei <b>Biome</b> die Datei wählen, <b>Berge</b> und <b>Flüsse</b> leer
lassen, <b>Anwenden</b>. Im Test erzeugt die Flüsse-Maske keinen Fluss, und die Berge-Maske
entfernt keine weißen Flächen.</li>
</ol>

<h4>Optional: Städte und Industrien</h4>
<ol start="22">
<li>Im Heightmap-Dialog <b>Städte aus OSM…</b> und <b>Industrien aus OSM…</b> (brauchen geladene
OSM-Daten). Sie erzeugen Dateien für den Ordner <tt>towns_industries</tt>, die der Editor von
TPF3 importieren kann. Bei den Städten stellst du die Größe per Faktor und die Auswahl je Ort ein.
Bei den Industrien werden Hang, Wasser und Kartenrand geprüft.</li>
</ol>

<h4>Optional: Bahnhöfe als Nachschlagewerk</h4>
<ol start="23">
<li><b>Bahnhöfe aus OSM…</b> speichert <tt>bahnhoefe.json</tt> (alles) und <tt>bahnhoefe.csv</tt>
(eine Zeile je Bahnhof) mit Bahnsteigen, Haltepositionen und Status. Die Koordinaten sind Meter ab
Kartenmitte. Im Spiel wird dadurch nichts gebaut und der Editor importiert die Dateien nicht. Sie
helfen beim eigenen Bauen. Nach <b>OSM laden</b> zeigt die Karte die Bahnhöfe auch als Marker.</li>
</ol>

<h3>Teil C: Wenn etwas nicht stimmt</h3>
<table border="1" cellspacing="0" cellpadding="5">
<tr><th align="left">Problem</th><th align="left">Ursache und Lösung</th></tr>
<tr><td>Der Fluss ist ein riesiger See</td><td>Das Spiel kennt nur einen Wasserspiegel
und flutet die Aue. <b>Wasser nur dort, wo OpenStreetMap Wasser hat</b> anhaken.</td></tr>
<tr><td>Der Fluss fällt stellenweise trocken</td><td>Wasserhöhe im Studio etwas erhöhen, die
Zahlen für das Spiel neu ablesen.</td></tr>
<tr><td>Der Fluss bleibt im oberen Teil trocken (starkes Gefälle, zum Beispiel Koblenz–Bingen
mit rund 18 m)</td><td>Zuerst <b>Gefälle ausgleichen</b> anhaken (Schritt 11), das hat am Rhein geholfen. Alternativ
bei „Wasser nur dort, wo OpenStreetMap Wasser hat“ die Grenze
<b>„Nur Gewässer bis … m über Wasserspiegel“</b> auf 25 bis 30 m erhöhen. Zusätzlich die
Wasserhöhe in die Mitte zwischen tiefstem und höchstem Flussabschnitt legen (dort etwa
68 m), dann werden beide Enden um etwa gleich viel korrigiert. <i>Im Spiel noch nicht
geprüft.</i></td></tr>
<tr><td>Steile Wand am Ufer</td><td>Böschung von 60 auf 100 m erhöhen. Bei Schluchten
(Mittelrhein) ist ein Teil natürlich.</td></tr>
<tr><td>Treppenstufen an den Hängen</td><td><b>Gelände glätten</b>, 15 m, bei Bedarf
30 m.</td></tr>
<tr><td>Weiße Flächen auf den Höhen</td><td>Schneegrenze im Spiel. Schneegrenzen-Test
machen, dann <b>Höhen stauchen</b>.</td></tr>
<tr><td>Graue Felsstreifen an Hängen</td><td>Ab einer Neigung färbt das Spiel Fels. Hänge mit
der Böschung oder dem Stauchen abmildern.</td></tr>
<tr><td>Das Gelände ist im Spiel verzerrt</td><td>Kartengröße oder -format im Spiel passt nicht
zum Studio-Text.</td></tr>
<tr><td>Falsche Höhen im Spiel</td><td>Die Zahlen unten im Dialog benutzen, nicht alte Werte.
Sie ändern sich mit jeder Option.</td></tr>
<tr><td>Meldung „Keine Gewässer“</td><td>Zuerst <b>Werkzeuge → OSM laden</b> für denselben
Ausschnitt.</td></tr>
<tr><td>Im Spiel „Map preview exception … No such file“</td><td>Die Datei wurde gelöscht
oder umbenannt. Dialog neu öffnen und die Datei neu wählen.</td></tr>
</table>

<h4>Schneegrenzen-Test (einmalig)</h4>
<ol>
<li>Die Testdatei <tt>hoehen_schneegrenze_test.png</tt> (zwölf Terrassen von 25 m bis 575 m in
50-m-Stufen, unten am niedrigsten) nach <tt>heightmaps</tt> kopieren.</li>
<li>Im Spiel die Kartengröße mit Format 1:5 wählen und mit <b>Mindesthöhe 0, Maximalhöhe 600,
Wasserhöhe 0</b> importieren (diese Werte gelten nur für die Testdatei).</li>
<li>Von unten zählen, ab der wievielten Terrasse Weiß beginnt. Höhe = 25 + 50 × (Nummer − 1).</li>
</ol>

<h3>Quellen bei veröffentlichten Karten</h3>
<ul>
<li>Höhen: Copernicus DEM GLO-30, © DLR e.V. 2010–2014 und © Airbus Defence and Space
GmbH 2014–2018, bereitgestellt im Rahmen von COPERNICUS durch die Europäische Union und
ESA.</li>
<li>Höhen bei Quelle DGM1: © GeoBasis-DE / Landesvermessung des jeweiligen Bundeslandes
(zum Beispiel © GeoBasis-DE / LVermGeoRP), Datenlizenz Deutschland – Namensnennung –
Version 2.0 beziehungsweise CC BY 4.0, je nach Land. Der genaue Vermerk steht nach dem Laden
im Heightmap-Dialog unter der Höhenquelle. Bereitgestellt über hoehendaten.de.</li>
<li>Höhen bei Quelle swissALTI3D: © swisstopo (Bundesamt für Landestopografie swisstopo),
swissALTI3D. Die Quellenangabe ist nach den Nutzungsbedingungen von swisstopo Pflicht.</li>
<li>Karten- und Gewässerdaten: © OpenStreetMap-Mitwirkende.</li>
<li>Relief-Hintergrund im Studio: AWS Terrain Tiles (Mapzen/Tilezen).</li>
</ul>
"""


class HeightmapGuideDialog(QDialog):
    """Scrollbare Anleitung zum Heightmap-Export."""

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setWindowTitle("Anleitung: Heightmap für TPF3")

        self.resize(760, 680)

        layout = QVBoxLayout(self)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(False)
        browser.setHtml(GUIDE_HTML)

        layout.addWidget(browser, 1)

        row = QHBoxLayout()
        row.addStretch(1)

        close_button = QPushButton("Schließen")
        close_button.clicked.connect(self.accept)
        row.addWidget(close_button)

        layout.addLayout(row)
