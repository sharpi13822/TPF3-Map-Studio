# Heightmap vom TPF3-Map-Studio nach Transport Fever 3

[Deutsch](ANLEITUNG_HEIGHTMAP.md) | [English](ANLEITUNG_HEIGHTMAP.en.md)

Diese Anleitung führt Schritt für Schritt von der leeren Karte bis zur fertig importierten Heightmap im Spiel.
Was noch nicht im Spiel getestet ist, steht jeweils dabei.

---

## Teil A: Im Studio

### 1. Ausschnitt festlegen
1. Studio starten. Im Panel auf der Karte unter **Kartenquelle** am besten **Karte + Relief** wählen. Damit sieht man Täler und Hänge.
2. Zum gewünschten Gebiet zoomen. Mit dem **Marker**-Werkzeug einen Marker in die Mitte setzen (optional, der Marker liefert später den Mittelpunkt).
3. **Werkzeuge → Rechteck-Tool** öffnen:
   - **Mittelpunkt** prüfen (kommt vom Marker),
   - **Kartengröße** wählen, genau wie im Spiel (Winzig bis Gigantomanisch, Format 1:1 bis 1:5),
   - **Drehwinkel** einstellen, bis das Band zu deinem Fluss oder deiner Strecke passt,
   - **OK**. Das blaue Band zeigt, was später geladen wird. Mit dem blauen Punkt lässt es sich verschieben, mit dem orangen drehen.

### 2. OSM-Daten laden
4. **Werkzeuge → OSM laden** und warten. Große Gebiete brauchen einige Minuten, die Statusleiste zeigt den Stand.
5. Die Ebenen im **Layer-Dock links** einschalten, um das Ergebnis zu prüfen (beim Start sind alle aus).

Ohne OSM-Daten funktionieren die Optionen "Wasser nur dort, wo OpenStreetMap Wasser hat" und "Trassen und Siedlungen einebnen" nicht.

### 3. Höhendaten holen
6. **Werkzeuge → Heightmap herunterladen** öffnen.
7. Oben im Dialog die **Höhenquelle** wählen:
   - **Copernicus** (weltweit, 30 m, mit Baumkronen) ist der Standard und überall verfügbar.
   - **DGM1 Deutschland** (1 m) lädt Kacheln über hoehendaten.de, etwa 20 Kacheln pro Minute. Große Karten brauchen eine halbe Stunde.
   - **DGM1 aus eigenen GeoTIFF-Kacheln** (Ordner), wenn du die Kacheln selbst bei einem Landesportal geladen hast.
   - **swissALTI3D** (Schweiz und Liechtenstein, 2 m) von swisstopo, nur bei Karten dort wählbar. Die Quellenangabe ist Pflicht (siehe unten).

   Optional: **Schnellvorschau** (grobes Bild aus Copernicus, sofort da, nicht exportierbar).
8. **Höhendaten herunterladen** und warten. Beim ersten Mal lädt das Studio die Kacheln und legt sie im Cache ab. Danach geht es schneller. Fehlen bei einer Quelle Daten, ergänzt das Studio sie aus Copernicus. Oben steht am Ende "Geladen: … Pixel".

### 4. Einstellungen im Dialog
**Schnellstart:** Oben im Dialog unter **Voreinstellung** "Empfohlen" wählen (Glätten, Einebnen, Wasser nach OSM mit den Standardwerten) oder "Original" (alle Optionen aus, echte Höhen). Beim DGM1 (1 m) sind die Standardwerte für Glätten und Einebnen kleiner (10 m), weil das Modell schon genau ist. Die Voreinstellung springt auf "Eigene Einstellungen", sobald du etwas von Hand änderst. Optionen, die OSM-Daten brauchen, bleiben ohne geladene OSM-Daten aus.

Empfohlene Reihenfolge. Jede Änderung aktualisiert die Vorschau. Die Zahlen unten im Dialog ändern sich mit.

9. **Wasserhöhe** prüfen. Das Studio schlägt einen Wert vor. Tipp: etwas höher als der tiefste Teil des Flusses, aber nicht so hoch, dass der Fluss an der höchsten Stelle mehr als 10 bis 15 m über dem Pegel liegt. Bei Flusstälern mit Gefälle (zum Beispiel Rhein) ist das ein Kompromiss. Der Knopf **"Wasserhöhe aus den OSM-Gewässern vorschlagen"** setzt sie in die Mitte zwischen tiefstem und höchstem Punkt des Hauptflusses und passt die Grenze "Nur Gewässer bis" an (braucht OSM-Daten).
10. **Gelände glätten** anhaken, Standard 15 m. Das entfernt die Treppenstufen an den Hängen (das Höhenmodell hat nur 30 m pro Pixel, das Spiel 4 m).
11. **Trassen und Siedlungen einebnen** anhaken, Standard 60 m. Bahnstrecken, größere Straßen und Gebäude werden abgeflacht, damit im Spiel weniger Rampen nötig sind. Braucht OSM-Daten. (Ob es beim Bauen spürbar hilft, ist noch nicht im Spiel geprüft.)
12. **Wasser nur dort, wo OpenStreetMap Wasser hat** anhaken (empfohlen). Damit verhindert das Studio überflutete Auen und Tümpel. Standardwerte:
    - Böschung 60 m (breiter = flacheres Ufer),
    - Tiefe am Ufer 2 m, Tiefe in der Mitte 8 m (Fahrrinne),
    - Ufer über Wasser 2 m,
    - Nur Gewässer bis 15 m über Wasserspiegel (höher gelegene Bäche und Bergseen bleiben unverändert).

    Die Option **"Terrain sanft ans Wasserniveau anpassen"** schaltet sich dabei ab, beide zusammen gehen nicht.
13. **Höhen stauchen** gegen weiße und graue Flächen auf den Höhen. Das Spiel färbt nach der Höhe über dem Wasser: Fels ab etwa 325-350 m, Schnee ab etwa 375-425 m. Die höchste Stelle landet auf dem eingestellten Anteil ihrer Höhe über dem Wasser; der untere Teil des Geländes bleibt unverändert. Beim Rhein (574 m über Wasser) hat **45 %** funktioniert. Der Dialog warnt, wenn die höchste Stelle mehr als 270 m über dem Wasser liegt. Standard 100 % = unverändert.
14. **Gefälle ausgleichen** nur bei Bedarf und mit Vorsicht: Es verschiebt alle Höhen. Standard: Stärke 100 %, Glättung 400 m, Bezug: Gewässer bis 30 m über dem Wasserspiegel. Die Zahlen für das Spiel ändern sich dabei stark, also immer die neuen benutzen.
15. **Höhenfenster begrenzen** (Haken). Der Karteneditor von TPF3 nimmt beim Import nur Höhen von **−20 bis 3177 m** (im Spiel getestet). Liegt dein Gelände ausserhalb, etwa in den Alpen, legst du hier ein Fenster darüber. Es wirkt zum Schluss, nach Glätten und Stauchen. Die Werte sind Eintragswerte, also die Zahlen, die du im Spiel einträgst (mit dem Haken "Werte auf Wasserhöhe 0 beziehen" relativ zum Wasser).
    - **Modus:** *Oben kappen* setzt Gipfel flach auf die Obergrenze, *Unten abschneiden* setzt Tiefen flach auf die Untergrenze, *Stauchen* drückt das ganze Gelände ins Fenster, ohne es zu strecken. Das Wasserniveau bleibt dabei erhalten.
    - **Fenster einstellen:** mit den beiden Feldern (unten und oben) und dem **Schieberegler**, der über den ganzen Bereich des Editors geht. Passt das Gelände schon ganz hinein, schiebst du das Fenster mit dem Regler und siehst sofort, was wegfällt.
    - **Vorschau:** Rot ist tiefer gesetzt (gekappt oder gestaucht), Cyan ist höher gesetzt (abgeschnitten). Eine Zeile nennt, wie viel Prozent der Fläche planiert werden.
    - Solange das Fenster an ist, wird die Option für Ausreißer ignoriert.

### 5. Kontrolle und Export
16. In der Vorschau prüfen: Der Fluss sollte ein durchgehendes Band im Tal sein, keine geraden Streifen oder Keile, keine Tümpel außer denen aus OSM.
17. **Unten im Dialog den Text lesen** und abschreiben oder fotografieren:
    > Im TPF3-Import eintragen: Mindesthöhe …, Maximalhöhe …, Wasserhöhe …
    > Kartengröße und -format im Spiel: …

    Das sind die **echten Höhen** (positive Werte über NN). Sie gelten immer für genau die aktuellen Einstellungen. Mit dem Haken **"Werte auf Wasserhöhe 0 beziehen"** wechselst du auf die Variante, die das TPF3-Wiki für Biome und Materialien empfiehlt (die Mindesthöhe kann dann negativ werden). Mit echten Höhen liegt alles entsprechend höher im Spiel, weiße Flächen auf den Höhen können dadurch zunehmen.
18. **Exportieren…** Der Dialog schlägt den heightmaps-Ordner von TPF3 vor (bei Steam zum Beispiel `…\userdata\<Nummer>\3493540\local\heightmaps`). **Gib der Datei einen eindeutigen Namen**, zum Beispiel `rhein_osmwasser.png`.

---

## Teil B: In TPF3

19. Den Karteneditor öffnen. Bei den Einstellungen unter **Welt** dieselbe **Kartengröße** und dasselbe **Kartenformat** wählen wie im Studio-Text. Nur dann passt das Seitenverhältnis. Das Spiel streckt jedes Bild auf die Kartengröße.
    Fehlt eine Größe (zum Beispiel Gigantomanisch), steht laut Wiki in der `settings.lua` im Userdata-Ordner der Schalter `experimentalMapFeatures`.
20. Den Dialog **Heightmap importieren** öffnen (Reiter **Heightmap**).
21. In der Liste die exportierte Datei anklicken. Steht sie nicht drin: Dialog schließen und neu öffnen, und prüfen, ob die Datei wirklich im Ordner `heightmaps` liegt.
22. Die Werte aus Schritt 17 eintragen:
    - **Mindesthöhe**, **Maximalhöhe** und **Wasserhöhe** genau wie im Studio-Text,
    - **Assets behalten: Nein**.
23. Die Vorschau rechts ansehen: Stimmt die Form? Steht nur der Fluss unter Wasser (blau)?
24. **Import** klicken.

### Optional: Bäume und Materialien (Reiter Biome)
25. Die Biome-Maske bestimmt die Baumverteilung. Eine einheitliche Maske reicht zum Test (Graustufe 77 = Biom 1, 128 = Biom 2, 179 = Biom 3, jeweils eine Datei im Ordner `biomes`). Bei **Biome** die Datei wählen, **Berge** und **Flüsse** leer lassen, **Anwenden**.
    Die Flüsse-Maske erzeugt im Test keinen Fluss, die Berge-Maske entfernt keine weißen Flächen.

---

## Teil C: Wenn etwas nicht stimmt

| Problem | Ursache und Lösung |
|---|---|
| Der Fluss ist ein riesiger See | Das Spiel kennt nur einen Wasserspiegel und flutet die Aue. **"Wasser nur dort, wo OpenStreetMap Wasser hat"** anhaken. |
| Der Fluss fällt stellenweise trocken | Wasserhöhe im Studio etwas erhöhen. Die Werte für das Spiel neu ablesen. |
| Der Fluss bleibt im oberen Teil trocken (starkes Gefälle, z. B. Koblenz–Bingen rund 18 m) | Bei "Wasser nur dort, wo OpenStreetMap Wasser hat" die Grenze **"Nur Gewässer bis … m über Wasserspiegel"** auf 25 bis 30 m erhöhen. Zusätzlich die Wasserhöhe in die Mitte zwischen tiefstem und höchstem Flussabschnitt legen (dort etwa 68 m). Im Spiel noch nicht geprüft. |
| Steile Wand am Ufer | Böschung von 60 auf 100 m erhöhen. Bei Schluchten (Mittelrhein) ist ein Teil natürlich. |
| Treppenstufen an den Hängen | **Gelände glätten**, 15 m, bei Bedarf 30 m. |
| Gerade Streifen oder Keile im Wasser | War ein Fehler beim Zusammensetzen der OSM-Uferstücke. Mit der aktuellen Version behoben. |
| Warnung "Der Karteneditor nimmt nur Höhen von -20 bis 3177 m" | Dein Bereich liegt ausserhalb dessen, was der Editor annimmt. **Höhenfenster begrenzen** anhaken (Schritt 15) oder **Höhen stauchen**. |
| Im Höhenfenster ändert sich nichts | Das Gelände liegt ganz im Fenster. Mit dem Schieberegler oder engeren Feldern das Fenster verkleinern oder verschieben. |
| Weiße Flächen auf den Höhen | Schneegrenze im Spiel. Den Terrassen-Test machen und **Höhen stauchen**. |
| Graue Felsstreifen an steilen Hängen | Ab einer Neigung färbt das Spiel Fels. Hänge mit der Böschung oder dem Stauchen abmildern. |
| Das Gelände ist im Spiel verzerrt | Kartengröße oder Kartenformat im Spiel passt nicht zum Studio-Text. |
| Falsche Höhen im Spiel | Die Zahlen unten im Studio-Dialog benutzen, nicht alte Werte. Sie ändern sich mit jeder Option. |
| Meldung "Keine Gewässer" | Zuerst **Werkzeuge → OSM laden** für denselben Ausschnitt. |
| Fehlermeldung "Map preview exception … No such file" im Spiel | Die Datei wurde gelöscht oder umbenannt. Dialog neu öffnen und die Datei neu wählen. |

### Schneegrenzen-Test (einmalig)
Die Testdatei `hoehen_schneegrenze_test.png` hat zwölf Terrassen von 25 m bis 575 m in 50-m-Stufen, unten am niedrigsten.
1. Datei nach `heightmaps` kopieren.
2. Im Spiel dieselbe Kartengröße (Format 1:5) wie in der Anleitung oben wählen.
3. Importieren mit **Mindesthöhe 0, Maximalhöhe 600, Wasserhöhe 0**.
4. Von unten zählen, ab der wievielten Terrasse Weiß beginnt. Höhe = 25 + 50 × (Nummer − 1).

---

## Quellen, die du bei veröffentlichten Karten nennen solltest
Nenne die Quelle der Höhendaten, die du benutzt hast. Der Heightmap-Dialog zeigt die genaue Angabe an.
- Höhen weltweit (Copernicus): Copernicus DEM GLO-30, © DLR e.V. 2010–2014 und © Airbus Defence and Space GmbH 2014–2018, bereitgestellt im Rahmen von COPERNICUS durch die Europäische Union und ESA.
- Höhen Deutschland (DGM1): je nach Bundesland Datenlizenz Deutschland, Namensnennung, Version 2.0 (dl-de/by-2-0), zum Beispiel "© GeoBasis-DE / LVermGeoRP (2025), dl-de/by-2-0" für Rheinland-Pfalz.
- Höhen Schweiz und Liechtenstein (swissALTI3D): © swisstopo (Bundesamt für Landestopografie swisstopo). **Die Quellenangabe ist Pflicht.**
- Karten- und Gewässerdaten: © OpenStreetMap-Mitwirkende.
- Relief-Hintergrund im Studio (nur Anzeige): AWS Terrain Tiles (Mapzen/Tilezen).
