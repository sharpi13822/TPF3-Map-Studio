# Biome, Städte und Industrien

Alle vier Funktionen stehen unten im Heightmap-Dialog und brauchen **geladene OSM-Daten** (siehe [OSM-Daten laden](help:osm-daten)).

## Biome-Maske aus OSM

Die Biome-Maske bestimmt im Spiel die Baumverteilung. *Biome-Maske aus OSM…* erzeugt sie aus der geladenen OSM-Landnutzung. Die Datei muss im Ordner `biomes` von TPF3 liegen, damit der Biome-Reiter sie findet.

Das Biome-Fenster blockiert den Heightmap-Dialog nicht: Du kannst es offen lassen und die Vorschau dahinter ansehen. Nach der ersten *Vorschau* rechnet sich die Vorschau bei jeder Änderung der Zuordnung nach einem kurzen Moment von selbst neu, und die 3D-Ansicht zeigt die Biome auf dem Gelände.

Im Spiel: Karteneditor → *Heightmap importieren* → Reiter **Biome** → bei **Biome** die Maske wählen, **Berge** und **Flüsse** leer lassen → **Anwenden**.

Die Graustufen der Maske sind 77 = Biom 1, 128 = Biom 2, 179 = Biom 3. Fels und Schnee färbt das Spiel selbst nach Höhe und Steilheit.

## Städte aus OSM

Erzeugt aus den geladenen OSM-Orten eine Städte-Datei für den Ordner `towns_industries`, die der TPF3-Editor importieren kann. Die Größe stellst du per Faktor ein, die Auswahl triffst du je Ort.

## Industrien aus OSM

Erzeugt aus OSM-Objekten (Höfe, Steinbrüche, Sägewerke, …) eine Industrien-Datei für `towns_industries`. Dabei prüft das Studio Hang, Wasser und Kartenrand, damit nichts auf einem Steilhang oder im Wasser landet.

## Bahnhofsplan zum Nachbauen

Das Spiel kann keine Bahnhöfe importieren. *Bahnhofsplan zum Nachbauen…* liest Bahnhöfe, Haltepunkte, Bahnsteige, Bahnhofsgebäude und Haltepositionen aus den OSM-Daten und speichert `bahnhoefe.json` (alles) und `bahnhoefe.csv` (eine Zeile je Bahnhof). Die Koordinaten sind Meter ab Kartenmitte. Im Spiel wird nichts gebaut, die Dateien dienen als Nachschlagewerk.

## Bauvorlage als Bild

*Bauvorlage als Bild…* zeichnet alle Straßen (nach Klasse eingefärbt: Autobahn violett, Bundesstraße rot, Landes- und Kreisstraßen orange bis gelb, Ortsstraßen grau, Wege braun), die Gleise schwarz-weiß geblockt im Trackmap-Stil (Tunnel grau) und die Bahnsteige als graue Flächen in ein Bild in der Größe der Karte. Es liegt auf demselben Raster wie die Heightmap und wird als `.tga` und `.png` gespeichert. Ohne geladene Höhendaten rechnet das Studio mit 4 m je Pixel. Die Vorlage dient zum 1:1-Nachbauen, im Spiel wird nichts gebaut. Braucht geladene OSM-Daten mit Straßen und Eisenbahn.

## Beschreibung zum Teilen

*Beschreibung zum Teilen…* erzeugt einen Text zum Veröffentlichen deiner Karte (Markdown, Steam-BBCode oder Klartext): Kartengröße, Höhenbereich, Höhenquelle mit Quellenangabe und Lizenz, Änderungen an den Höhendaten. Er lässt sich vor dem Kopieren bearbeiten und ersetzt nicht die Lizenzbedingungen der Quellen, siehe [Quellen und Lizenzen](help:quellen-und-lizenzen). Braucht geladene Höhendaten.
